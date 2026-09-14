#!/usr/bin/env python3
"""Shared bench for the P-02 cascade tests — `tests/test_rqa_lifecycle_{steps,rest,resume,paths}.py`.

Not a test module: `run_all.py` globs `test_*.py` and pytest collects the same, so
nothing here runs on its own. It exists so the four cascade test files drive one set of
fixtures instead of four drifting copies.

Every fixture follows the batch's real-collaborator rule: the record writer is always
P-12's real `SQLiteRecordWriter`, every transition goes through the real kernel, and a
fake stands in only where a real neighbour cannot be steered into the branch under test
(GitHub, the harness process, P-11 which is Batch 5). Fakes for E-12 writes **assert the
grant discipline on every call**: being handed anything but a `Grant` for their own
activity is an immediate test failure, which makes §5 guard 2 checked at every callsite
of every test that uses this bench, not only in the tests written for it.

No key material, no keychain, no network: the key store returns `None` (ADR-0063's
explicitly unkeyed append) and `tests/conftest.py` blocks sockets suite-wide.
"""

from __future__ import annotations

import pathlib
import sys
import sqlite3
import tempfile
from datetime import datetime, timedelta, timezone

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from rqa.contracts import (  # noqa: E402
    Activity,
    Assurance,
    Attempt,
    Attestation,
    Blocking,
    Budget,
    CarriedEvidence,
    CarryOver,
    Category,
    Decision,
    Deny,
    DenyReason,
    Escalation,
    EscalationCause,
    EvidenceState,
    External,
    Facts,
    Finding,
    GithubUnavailable,
    Grant,
    HarnessIdentity,
    Job,
    JobStatus,
    Judgement,
    LeaseTaken,
    Location,
    Mechanical,
    Mutation,
    Obligation,
    PanelResult,
    Plan,
    Policy,
    PrFacts,
    RemediationPolicy,
    RemediationPushed,
    Route,
    Snapshot,
    Stale,
    SubmittedReview,
    ValidationError,
    ValidationErrorCode,
    ValidationFailure,
    Verdict,
)
from rqa.lifecycle.deps import LifecycleDeps  # noqa: E402
from rqa.record.writer import SQLiteRecordWriter  # noqa: E402

HEAD = "a" * 40
BASE = "b" * 40
REPO = "owner/name"
SNAP_HASH = "sha256:snapshot-1"
NOW = datetime(2026, 9, 13, 12, 0, 0, tzinfo=timezone.utc)

#: `code/P-01-intake.md` §5's tables, reproduced because P-02 owns no DDL. `leases`
#: uses the landed `job_id` column (`rqa/intake/store.py`; P-02 §5's `job` snippet is a
#: stale reference — see the lane handoff's Disclosures).
DDL = """
CREATE TABLE jobs (
  id              TEXT PRIMARY KEY,
  repo            TEXT NOT NULL,
  number          INTEGER NOT NULL,
  head_sha        TEXT NOT NULL,
  base_sha        TEXT NOT NULL,
  head_repo       TEXT NOT NULL,
  head_ref        TEXT NOT NULL,
  predecessor_job TEXT REFERENCES jobs(id),
  predecessor_head_sha TEXT,
  snapshot_hash   TEXT,
  status          TEXT NOT NULL,
  created_at      TEXT NOT NULL,
  UNIQUE (repo, number, head_sha)
);
CREATE TABLE pr_facts (
  repo     TEXT NOT NULL,
  number   INTEGER NOT NULL,
  head_sha TEXT NOT NULL,
  PRIMARY KEY (repo, number)
);
CREATE TABLE leases (
  job_id     TEXT PRIMARY KEY,
  repo       TEXT NOT NULL,
  number     INTEGER NOT NULL,
  claimed_at TEXT NOT NULL,
  UNIQUE (repo, number)
);
"""


class NoKeyStore:
    """ADR-0063's absent-key path: unkeyed appends, no OS keychain, no key material."""

    def read(self, name: str) -> bytes | None:
        return None


# --------------------------------------------------------------------------
# Rows and shared values
# --------------------------------------------------------------------------


def make_job(
    *,
    status: JobStatus = JobStatus.QUEUED,
    job_id: str = "job-1",
    snapshot_hash: str | None = None,
    predecessor_job: str | None = None,
    head_sha: str = HEAD,
    number: int = 7,
) -> Job:
    return Job(
        id=job_id,
        repo=REPO,
        number=number,
        head_sha=head_sha,
        base_sha=BASE,
        head_repo=REPO,
        head_ref="feature",
        predecessor_job=predecessor_job,
        predecessor_head_sha=None if predecessor_job is None else "c" * 40,
        snapshot_hash=snapshot_hash,
        status=status,
    )


def insert_job(connection: sqlite3.Connection, job: Job) -> None:
    connection.execute(
        "INSERT INTO jobs (id, repo, number, head_sha, base_sha, head_repo, head_ref, "
        "predecessor_job, predecessor_head_sha, snapshot_hash, status, created_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            job.id, job.repo, job.number, job.head_sha, job.base_sha, job.head_repo,
            job.head_ref, job.predecessor_job, job.predecessor_head_sha,
            job.snapshot_hash, job.status.value, NOW.isoformat(),
        ),
    )
    connection.commit()


def insert_lease(connection: sqlite3.Connection, job: Job) -> None:
    connection.execute(
        "INSERT INTO leases (job_id, repo, number, claimed_at) VALUES (?, ?, ?, ?)",
        (job.id, job.repo, job.number, NOW.isoformat()),
    )
    connection.commit()


def lease_present(connection: sqlite3.Connection, job_id: str = "job-1") -> bool:
    return (
        connection.execute("SELECT 1 FROM leases WHERE job_id = ?", (job_id,)).fetchone()
        is not None
    )


def bench(
    *,
    status: JobStatus = JobStatus.QUEUED,
    snapshot_hash: str | None = None,
    predecessor_job: str | None = None,
) -> tuple[sqlite3.Connection, SQLiteRecordWriter, Job]:
    connection = sqlite3.connect(":memory:")
    connection.executescript(DDL)
    job = make_job(
        status=status, snapshot_hash=snapshot_hash, predecessor_job=predecessor_job
    )
    insert_job(connection, job)
    return connection, SQLiteRecordWriter(connection, keystore=NoKeyStore()), job


def stored_status(connection: sqlite3.Connection, job_id: str = "job-1") -> str:
    return connection.execute(
        "SELECT status FROM jobs WHERE id = ?", (job_id,)
    ).fetchone()[0]


def stored_pin(connection: sqlite3.Connection, job_id: str = "job-1") -> str | None:
    return connection.execute(
        "SELECT snapshot_hash FROM jobs WHERE id = ?", (job_id,)
    ).fetchone()[0]


def transitions(connection: sqlite3.Connection, job_id: str = "job-1") -> list[str]:
    """Every recorded transition's `to_state`, in sequence order."""
    import json

    return [
        json.loads(row[0])["to_state"]
        for row in connection.execute(
            "SELECT payload FROM record_entries WHERE job = ? AND kind = 'transition' "
            "ORDER BY seq",
            (job_id,),
        )
    ]


def entry_kinds(connection: sqlite3.Connection, job_id: str = "job-1") -> list[str]:
    return [
        row[0]
        for row in connection.execute(
            "SELECT kind FROM record_entries WHERE job = ? ORDER BY seq", (job_id,)
        )
    ]


def latest_payload(connection: sqlite3.Connection, kind: str, job_id: str = "job-1") -> dict:
    import json

    row = connection.execute(
        "SELECT payload FROM record_entries WHERE job = ? AND kind = ? ORDER BY seq DESC LIMIT 1",
        (job_id, kind),
    ).fetchone()
    assert row is not None, f"no {kind} entry recorded"
    return json.loads(row[0])


def make_snapshot(*, merge_enabled: bool = False, tools: frozenset[str] | None = None) -> Snapshot:
    return Snapshot(
        hash=SNAP_HASH,
        repo=REPO,
        protocol_hash="sha256:protocol-1",
        authority={
            Activity.REVIEW: True,
            Activity.COMMENT: True,
            Activity.APPROVE: True,
            Activity.REQUEST_CHANGES: True,
            Activity.REMEDIATE: True,
            Activity.MERGE: merge_enabled,
        },
        routes=(),
        external=External(allowed=False, deny_label="external"),
        policy=Policy(
            version="1.0.0",
            obligations=(
                Obligation(
                    id="ob-1",
                    paths=("**",),
                    required_for=frozenset({"standard"}),
                    evidence="behaviour is reviewed",
                ),
            ),
            blocking=Blocking(
                categories=frozenset({Category.SECURITY, Category.CORRECTNESS}),
                severities=frozenset({"high"}),
                corroboration=2,
            ),
            mechanical=Mechanical(
                categories=frozenset({Category.MECHANICAL}),
                tools=tools if tools is not None else frozenset({"ruff-format"}),
            ),
            assurance={"standard": 2},
            remediation=RemediationPolicy(allow_forks=False),
        ),
        budget=Budget(None, None, None),
    )


def make_validation_failure() -> ValidationFailure:
    return ValidationFailure(
        repo=REPO,
        errors=(ValidationError(code=ValidationErrorCode.UNREADABLE, path=".rqa/config.json", detail="x"),),
    )


def make_facts(
    *,
    job: Job,
    reviews: tuple[SubmittedReview, ...] = (),
    checks: tuple = (),
    fetched_at: datetime = NOW,
) -> Facts:
    return Facts(
        pr=PrFacts(
            repo=job.repo,
            number=job.number,
            head_sha=job.head_sha,
            base_sha=job.base_sha,
            merge_base_sha=job.base_sha,
            head_repo=job.head_repo,
            head_ref=job.head_ref,
            head_protected=False,
            author="author-login",
            labels=frozenset(),
            title="a title that must never steer a transition",
            body="a body that must never steer a transition",
        ),
        diff="diff --git a/src/x.py b/src/x.py",
        changed_paths=frozenset({"src/x.py"}),
        revision_changed_paths=frozenset(),
        files={},
        checks=checks,
        base_checks=(),
        reviews=reviews,
        fetched_at=fetched_at,
    )


def make_plan(*, obligations: tuple[str, ...] = ("ob-1",)) -> Plan:
    return Plan(
        obligations=obligations,
        omitted={},
        strategy="panel",
        participants=2,
        risk_class="standard",
        head_sha=HEAD,
        snapshot_hash=SNAP_HASH,
        protocol_hash="sha256:protocol-1",
        policy_version="1.0.0",
    )


def make_route(family: str) -> Route:
    return Route(
        harness="claude-code",
        model=f"model-{family}",
        provider=family,
        family=family,
        external=False,
        command=None,
    )


def make_attempt(
    *,
    family: str,
    obligations: dict | None = None,
    findings: tuple[Finding, ...] = (),
    ended_at: datetime = NOW - timedelta(minutes=1),
    attempt_id: str | None = None,
) -> Attempt:
    verdict = Verdict(
        obligations=obligations if obligations is not None else {"ob-1": EvidenceState.VERIFIED},
        findings=findings,
        injection_attempts=(),
        identity=HarnessIdentity(harness="claude-code", model=f"model-{family}", provider=family),
        protocol_version="1",
    )
    return Attempt(
        id=attempt_id or f"attempt-{family}",
        route=make_route(family),
        outcome=verdict,
        attestation=Attestation(
            harness="claude-code",
            model=f"model-{family}",
            provider=family,
            route=make_route(family),
            effort="medium",
            started_at=ended_at - timedelta(minutes=2),
            ended_at=ended_at,
            exit_code=0,
        ),
    )


def make_panel(
    *,
    attempts: tuple[Attempt, ...] | None = None,
    complete: bool = True,
    incomplete_reason: str | None = None,
    evidence_cutoff: datetime = NOW,
    bound_reached: bool = False,
) -> PanelResult:
    if attempts is None:
        attempts = (make_attempt(family="alpha"), make_attempt(family="beta"))
    return PanelResult(
        attempts=attempts,
        complete=complete,
        incomplete_reason=incomplete_reason,
        evidence_cutoff=evidence_cutoff,
        bound_reached=bound_reached,
    )


def make_finding(
    *,
    finding_id: str = "finding-1",
    categories: frozenset[Category] = frozenset({Category.MECHANICAL}),
    remedy=None,
    behaviour_changing: bool = False,
) -> Finding:
    return Finding(
        id=finding_id,
        categories=categories,
        extra_tags=frozenset(),
        location=Location(path="src/x.py", line=1),
        evidence="src/x.py is not formatted",
        severity="low",
        remedy=remedy,
        behaviour_changing=behaviour_changing,
        source_attempt="attempt-alpha",
    )


def make_judgement(
    *,
    disposition: str = "approve",
    findings: tuple[Finding, ...] = (),
    remediation_candidates: tuple[str, ...] = (),
    escalation_causes: tuple = (),
    obligations: dict | None = None,
) -> Judgement:
    return Judgement(
        obligations=obligations if obligations is not None else {"ob-1": EvidenceState.VERIFIED},
        findings=findings,
        corroborated=frozenset(f.id for f in findings),
        blocking=frozenset(),
        attribution={},
        assurance=Assurance(required=2, achieved=2),
        remediation_candidates=remediation_candidates,
        escalation_causes=escalation_causes,
        disposition=disposition,
        reused_from=None,
    )


def make_grant(activity: Activity, *, categories: frozenset[Category] | None = None) -> Grant:
    return Grant(
        activity=activity,
        repo=REPO,
        job_id="job-1",
        snapshot_hash=SNAP_HASH,
        capability_proof_id=1,
        categories=categories,
        entry_seq=0,
    )


def make_deny(activity: Activity, *, reason: DenyReason = DenyReason.NOT_ENABLED) -> Deny:
    return Deny(
        activity=activity,
        repo=REPO,
        job_id="job-1",
        reason=reason,
        detail="denied by the bench",
        entry_seq=0,
    )


def make_escalation(
    *,
    job: Job,
    cause: EscalationCause = EscalationCause.AUTHORITY_REQUIREMENT,
    raised_at: datetime = NOW,
    head_sha: str | None = None,
    snapshot_hash: str | None = None,
    escalation_id: int = 1,
) -> Escalation:
    return Escalation(
        id=escalation_id,
        job_id=job.id,
        cause=cause,
        question="a specific question",
        context={},
        head_sha=head_sha if head_sha is not None else job.head_sha,
        snapshot_hash=snapshot_hash if snapshot_hash is not None else (job.snapshot_hash or SNAP_HASH),
        entry_seq=1,
        raised_at=raised_at,
    )


def make_decision(
    *,
    actor: str = "human-reviewer",
    outcome: str | None = "approved",
    substantiates: str | None = None,
) -> Decision:
    return Decision(actor=actor, basis="reviewed on GitHub", substantiates=substantiates, outcome=outcome)


def make_review(
    *,
    actor: str = "human-reviewer",
    outcome: str = "approved",
    head_sha: str = HEAD,
    submitted_at: datetime = NOW + timedelta(hours=1),
    review_id: str = "review-1",
) -> SubmittedReview:
    return SubmittedReview(
        id=review_id, actor=actor, outcome=outcome, head_sha=head_sha, submitted_at=submitted_at
    )


# --------------------------------------------------------------------------
# Fake neighbours — used only where a real one cannot be steered into the branch
# --------------------------------------------------------------------------


class FakePolicy:
    """E-03. `store` rides the client the way §3.2's closures ride `deps.supply`."""

    def __init__(self, result):
        self.result = result
        self.store = object()
        self.calls = []

    def snapshot_for(self, *, repo, job, store, record):
        assert store is self.store, "E-03 must receive the client's own store"
        self.calls.append((repo, job))
        return self.result


class FakeAuthority:
    """E-04, scripted per activity; the last scripted answer is sticky."""

    def __init__(self, script: dict | None = None):
        self.script = {activity: list(answers) for activity, answers in (script or {}).items()}
        self.github = object()
        self.store = object()
        self.calls = []

    def grant(self, *, repo, activity, snapshot, job_id, categories, record, github, store):
        assert github is self.github and store is self.store, (
            "E-04 must receive the client's own probe and store"
        )
        self.calls.append((activity, snapshot, categories))
        answers = self.script.get(activity)
        if not answers:
            return make_grant(activity, categories=categories)
        answer = answers.pop(0) if len(answers) > 1 else answers[0]
        return answer


class FakeGithub:
    """E-23 + E-12. Every write asserts §5 guard 2 at its own callsite: a missing
    `Grant`, or one for a different activity, is an immediate failure."""

    def __init__(self, *, facts, submit=None, comment=None, merge=None):
        self._facts = facts
        self._submit = submit
        self._comment = comment
        self._merge = merge
        self.facts_calls = []
        self.submit_calls = []
        self.comment_calls = []
        self.merge_calls = []

    def facts(self, *, job, record):
        self.facts_calls.append(job)
        return self._facts

    def submit_review(self, *, job, state, body, grant, record):
        assert isinstance(grant, Grant), "submit_review called without a Grant"
        assert grant.activity in (Activity.APPROVE, Activity.REQUEST_CHANGES), grant.activity
        assert (state == "APPROVE") == (grant.activity is Activity.APPROVE), (
            "the submit state must match the granted activity"
        )
        self.submit_calls.append((state, body, grant))
        return self._submit if self._submit is not None else Mutation(
            id="m-submit", kind="submit_review", accepted=True
        )

    def comment(self, *, job, body, grant, record):
        assert isinstance(grant, Grant) and grant.activity is Activity.COMMENT, (
            "comment called without a COMMENT Grant"
        )
        self.comment_calls.append((body, grant))
        return self._comment if self._comment is not None else Mutation(
            id="m-comment", kind="comment", accepted=True
        )

    def merge(self, *, job, grant, record):
        assert isinstance(grant, Grant) and grant.activity is Activity.MERGE, (
            "merge called without a MERGE Grant"
        )
        self.merge_calls.append(grant)
        return self._merge if self._merge is not None else Mutation(
            id="m-merge", kind="merge", accepted=True
        )


RUN_FORBIDDEN = object()


class FakeHarness:
    """E-07. `run_result=RUN_FORBIDDEN` makes any run call an immediate failure —
    that is AC03's proof shape."""

    def __init__(self, *, plan=None, run_result=RUN_FORBIDDEN):
        self._plan = plan if plan is not None else make_plan()
        self._run = run_result
        self.plan_calls = []
        self.run_calls = []

    def plan(self, *, job, facts, snapshot, carry, record):
        self.plan_calls.append((job, facts, snapshot, carry))
        return self._plan

    def run(self, *, job, plan, facts, snapshot, supply, state_dir, record):
        if self._run is RUN_FORBIDDEN:
            raise AssertionError("harness.run must not be called on this path")
        self.run_calls.append((job, plan, facts, snapshot, supply, state_dir))
        return self._run


class FakeSupply:
    """E-06/E-15 behind §3.2's `SupplyPort` closures. Records the exact keywords each
    closure forwarded so the verbatim argument contract is assertable."""

    def __init__(self):
        self.prober = object()
        self.breakers = object()
        self.spend = object()
        self.route_calls = []
        self.reserve_calls = []
        self.consumed_calls = []

    def route(self, **kwargs):
        self.route_calls.append(kwargs)
        from rqa.contracts import RouteUnavailable

        return RouteUnavailable(no_fallback=True, tried=())

    def reserve(self, **kwargs):
        self.reserve_calls.append(kwargs)
        from rqa.contracts import Refusal

        return Refusal(downgrade="incomplete", axis="tokens")

    def consumed(self, **kwargs):
        self.consumed_calls.append(kwargs)
        from rqa.contracts import Spend

        return Spend(tokens=1, measured=True, source="reservation")


class FakeJudgement:
    JUDGE_FORBIDDEN = object()

    def __init__(self, result):
        self._result = result
        self.calls = []

    def judge(self, *, job, plan, panel, carry, facts, snapshot, decision, record):
        if self._result is FakeJudgement.JUDGE_FORBIDDEN:
            raise AssertionError("judge must not be called on this path")
        self.calls.append(
            {"job": job, "plan": plan, "panel": panel, "carry": carry, "facts": facts,
             "snapshot": snapshot, "decision": decision}
        )
        return self._result


class RealJudgement:
    """The landed P-07 `judge`, wrapped as P-02's `JudgementClient` and recording the
    panel/facts it received — the real collaborator, not a stub."""

    def __init__(self):
        self.calls = []

    def judge(self, **kwargs):
        from rqa.judgement import judge as real_judge

        self.calls.append(kwargs)
        return real_judge(**kwargs)


class RealReuse:
    """The landed P-13 `carry_over`, as P-02's `ReuseClient`."""

    def __init__(self):
        self.calls = []

    def carry_over(self, **kwargs):
        from rqa.reuse import carry_over as real_carry_over

        self.calls.append(kwargs)
        return real_carry_over(**kwargs)


class FakeReuse:
    def __init__(self, carry: CarryOver):
        self._carry = carry
        self.calls = []

    def carry_over(self, *, job, prior, facts, snapshot, record):
        self.calls.append({"job": job, "prior": prior, "facts": facts, "snapshot": snapshot})
        return self._carry


class FakeRemediation:
    def __init__(self, result=None):
        self._result = result if result is not None else RemediationPushed(
            new_head_sha="d" * 40, tool_id="ruff-format", entry_seq=9
        )
        self.calls = []

    def remediate(self, *, job, finding, grant, facts, snapshot, state_dir, runner, record):
        assert isinstance(grant, Grant) and grant.activity is Activity.REMEDIATE, (
            "remediate called without a REMEDIATE Grant"
        )
        self.calls.append(
            {"job": job, "finding": finding, "grant": grant, "facts": facts,
             "snapshot": snapshot, "state_dir": state_dir, "runner": runner}
        )
        return self._result


class FakeEscalation:
    """E-11 — the one genuinely absent collaborator (P-11 is Batch 5), faked through
    the `EscalationClient` Protocol as the lane contract instructs."""

    def __init__(self, pending: tuple = ()):
        self.store = object()
        self.raised = []
        self._pending = pending

    def raise_(self, *, job, cause, question, context, record, store):
        assert store is self.store, "E-11 must receive the client's own store"
        self.raised.append({"job": job, "cause": cause, "question": question, "context": context})
        return make_escalation(job=job, cause=cause, escalation_id=len(self.raised))

    def pending(self, *, store):
        assert store is self.store
        return self._pending


class FakeLease:
    def __init__(self, claim=None):
        self._claim = claim
        self.claim_calls = []
        self.release_calls = []

    def claim(self, *, job, grant, record):
        assert isinstance(grant, Grant) and grant.activity is Activity.REVIEW, (
            "claim_lease called without a REVIEW Grant"
        )
        self.claim_calls.append(grant)
        return self._claim if self._claim is not None else Mutation(
            id="m-claim", kind="claim_lease", accepted=True
        )

    def release(self, *, job, grant, record):
        assert isinstance(grant, Grant) and grant.activity is Activity.REVIEW, (
            "release_lease called without a REVIEW Grant"
        )
        self.release_calls.append(grant)
        return Mutation(id="m-release", kind="release_lease", accepted=True)


class FakeRunner:
    def run(self, *, cwd, argv, timeout):
        raise AssertionError("the lifecycle must never run a process itself")


def make_deps(connection, record, **clients) -> LifecycleDeps:
    """The §2 bundle. Unnamed neighbours default to `None` so an unexpected call
    raises loudly instead of silently succeeding."""
    values = {
        "policy": None,
        "authority": None,
        "supply": None,
        "harness": None,
        "judgement": None,
        "remediation": None,
        "escalation": FakeEscalation(),
        "github": None,
        "reuse": None,
        "record": record,
        "connection": connection,
        "state_dir": pathlib.Path(tempfile.gettempdir()),
        "runner": FakeRunner(),
        "claim_lease": None,
        "release_lease": None,
    }
    values.update(clients)
    return LifecycleDeps(**values)


def happy_deps(
    connection,
    record,
    job,
    **overrides,
):
    """A full bundle that drives one no-predecessor admission to `approved` (merge
    denied) with the real record writer, real transition kernel and real P-07 judge.
    Every piece is overridable per test."""
    snapshot = overrides.pop("snapshot", make_snapshot())
    facts = overrides.pop("facts", make_facts(job=job))
    lease = overrides.pop("lease", FakeLease())
    clients = {
        "policy": FakePolicy(snapshot),
        "authority": FakeAuthority({Activity.MERGE: [make_deny(Activity.MERGE)]}),
        "harness": FakeHarness(plan=make_plan(), run_result=make_panel()),
        "judgement": RealJudgement(),
        "remediation": FakeRemediation(),
        "github": FakeGithub(facts=facts),
        "reuse": FakeReuse(CarryOver(reused=(), regenerated=(), reasons={}, source_job=None)),
        "supply": FakeSupply(),
        "claim_lease": lease.claim,
        "release_lease": lease.release,
    }
    clients.update(overrides)
    return make_deps(connection, record, **clients), lease
