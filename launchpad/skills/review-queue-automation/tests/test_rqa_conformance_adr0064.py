#!/usr/bin/env python3
"""Task #2216 — ADR-0064's executable half: the push is exact and never forced, a
changed semantic fingerprint refuses with its named reason, and the refusal reaches
a named human (AC09, RQA-NFR-031/033).

ADR-0064 §7, verbatim: "The push is exact and non-forced, to the validated
pull-request head repository and ref only." §4: "A parser-derived semantic
fingerprint is identical before and after. A parse error, an unsupported construct,
or a changed fingerprint refuses the remediation."

The push and fingerprint tests drive the REAL `push_head` and the REAL fourteen-step
`remediate()` over the shared P-10 fixtures; the reaches-a-named-human test drives
the REAL lifecycle step 9. No test performs a GitHub write — the runner is the
declared E-26 seam, and the run boundary (TESTING.md §4) forbids a live push, which
is one of three independent reasons the composed demonstration is recorded as not
reachable in `TESTING.md` Part 2 §11.4.
"""

from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import lifecycle_cascade_bench as lifecycle_bench  # noqa: E402
import test_rqa_remediation_fixtures as fixtures  # noqa: E402
import rqa.escalation as escalation  # noqa: E402

from rqa.contracts import (  # noqa: E402
    Activity,
    EscalationCause,
    JobStatus,
    RemediationRefusalReason,
    RemediationRefused,
)
from rqa.escalation.store import SqliteEscalationStore  # noqa: E402
from rqa.lifecycle.steps import Cascade, step9  # noqa: E402
from rqa.remediation import remediate  # noqa: E402
from rqa.remediation.push import push_head  # noqa: E402


class _RecordingRunner:
    """E-26, recording argv and answering success — push_head's whole world."""

    def __init__(self) -> None:
        self.argvs: list[tuple[str, ...]] = []

    def run(self, *, cwd, argv, timeout):
        self.argvs.append(tuple(argv))
        from rqa.contracts import ProcessResult

        return ProcessResult(returncode=0, stdout=b"", stderr=b"")


class _RealEscalation:
    """P-02's E-11 protocol backed by P-11's real SQLite store."""

    def __init__(self, connection) -> None:
        self.store = SqliteEscalationStore(connection)

    def raise_(self, *, job, cause, subject, question, context, record, store):
        return escalation.raise_(
            job=job,
            cause=cause,
            subject=subject,
            question=question,
            context=context,
            record=record,
            store=store,
        )

    def pending(self, *, store):
        return escalation.pending(store=store)


def test_adr0064_the_push_argv_is_exact_and_carries_no_force() -> None:
    """§7: one remote, one refspec, no option after `push`. `--force`,
    `--force-with-lease` and a `+`-prefixed refspec are not merely absent — no
    argv element can carry them."""
    runner = _RecordingRunner()
    result = push_head(
        runner=runner,
        worktree=pathlib.Path("/tmp"),
        head_repo="acme/widgets",
        head_ref="feature/tidy",
    )
    assert result.returncode == 0
    assert runner.argvs == [
        ("git", "check-ref-format", "--branch", "feature/tidy"),
        ("git", "push", "https://github.com/acme/widgets.git", "HEAD:refs/heads/feature/tidy"),
    ]
    push_argv = runner.argvs[-1]
    assert not any(token.startswith("-") for token in push_argv[2:]), push_argv
    assert not any(token.startswith("+") for token in push_argv), push_argv
    assert len(push_argv) == 4, "git, push, one remote, one refspec — nothing else"


def test_adr0064_a_hostile_head_ref_is_refused_before_git_is_asked_anything() -> None:
    """A PR author controls the head branch name; a ref that could become an option
    or a second refspec never reaches an argv at all."""
    for hostile in ("-delete-everything", "a:b", "one two", "evil+ref", "x?y"):
        runner = _RecordingRunner()
        result = push_head(
            runner=runner,
            worktree=pathlib.Path("/tmp"),
            head_repo="acme/widgets",
            head_ref=hostile,
        )
        assert result.returncode == 128, hostile
        assert runner.argvs == [], f"{hostile!r} must be refused locally, before git"


def test_adr0064_a_changed_semantic_fingerprint_refuses_with_its_named_reason() -> None:
    """§4: the formatter output changed a literal, so the parser-derived fingerprint
    moved; the candidate is refused BEHAVIOUR_CHANGED — the oracle decides, never a
    formatter label — and nothing is pushed."""
    runner = fixtures.FakeRunner(on_fix=fixtures.writes(fixtures.PY_ADVERSARIAL))
    arguments = fixtures.call(runner=runner)
    with fixtures.sandbox() as state_dir:
        outcome = remediate(state_dir=state_dir, **arguments)
    assert isinstance(outcome, RemediationRefused), outcome
    assert outcome.reason is RemediationRefusalReason.BEHAVIOUR_CHANGED
    assert fixtures.TARGET in outcome.detail
    assert runner.ran("git", "push") == [], "a refused remedy never pushes"
    actions = arguments["record"].of_kind("action")
    assert [a["decision"] for a in actions] == ["refused"]
    assert actions[0]["reason"] == "behaviour_changed"


def test_adr0064_a_behaviour_neutral_fix_still_pushes_to_the_head_only() -> None:
    """The positive twin, over the same fixtures: byte-different, AST-identical
    output survives every gate, and the one push argv is the §7 shape."""
    runner = fixtures.FakeRunner(on_fix=fixtures.writes(fixtures.PY_AFTER))
    arguments = fixtures.call(runner=runner)
    with fixtures.sandbox() as state_dir:
        outcome = remediate(state_dir=state_dir, **arguments)
    assert not isinstance(outcome, RemediationRefused), outcome
    pushes = runner.ran("git", "push")
    assert len(pushes) == 1
    remote, refspec = pushes[0][2], pushes[0][3]
    assert remote == f"https://github.com/{fixtures.REPO}.git"
    assert refspec == f"HEAD:refs/heads/{fixtures.HEAD_REF}"
    assert "--force" not in runner.flat()


def test_adr0064_a_refused_candidate_reaches_a_named_human() -> None:
    """AC09/DoD: the refusal is not a log line — the REAL step 9 turns it into a
    durable escalation naming the reason, and the job rests awaiting human
    judgement."""
    connection, record, job = lifecycle_bench.bench(status=JobStatus.JUDGED)
    finding = lifecycle_bench.make_finding()
    judgement = lifecycle_bench.make_judgement(
        disposition="remediate",
        findings=(finding,),
        remediation_candidates=(finding.id,),
    )
    escalation_client = _RealEscalation(connection)
    deps = lifecycle_bench.make_deps(
        connection,
        record,
        authority=lifecycle_bench.FakeAuthority(),
        remediation=lifecycle_bench.FakeRemediation(
            result=RemediationRefused(
                reason=RemediationRefusalReason.BEHAVIOUR_CHANGED,
                detail="src/x.py is not provably behavior-equivalent",
                entry_seq=1,
            )
        ),
        escalation=escalation_client,
    )
    ctx = Cascade(
        deps=deps,
        facts=lifecycle_bench.make_facts(job=job),
        snapshot=lifecycle_bench.make_snapshot(),
        judgement=judgement,
    )

    moved, _ = step9(job, ctx)

    assert lifecycle_bench.stored_status(connection, job.id) == "escalated"
    raised = lifecycle_bench.latest_payload(connection, "escalation")
    assert raised["cause"] == EscalationCause.EVIDENCE_GAP.value
    assert "behaviour_changed" in raised["question"]
    grant_activities = [activity for activity, _, _ in deps.authority.calls]
    assert grant_activities == [Activity.REMEDIATE], (
        "the remedy ran under a REMEDIATE grant and nothing else was asked for"
    )
