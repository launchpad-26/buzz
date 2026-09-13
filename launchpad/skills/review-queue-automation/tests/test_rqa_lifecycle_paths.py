#!/usr/bin/env python3
"""§8 T13: exhaustive state-path search with every refusal, unavailability and denial
at its boundary — no path reaches `APPROVED`, and every branch rests safely.

No pytest: every `test_*` function takes no arguments, per `tests/run_all.py`.

The search enumerates the complete decision tree of one admission: at every neighbour
boundary a scripted client offers *every* answer the seam allows — grant and deny,
mutation and unavailability, complete and incomplete panels, all four judgement
dispositions, pushed and refused remediations, stale and unavailable writes. Each leaf
is one fully-played admission against the real transition kernel and the real record
writer; the tree is discovered, not hand-listed, so a new branch in the cascade fails
this test instead of silently escaping it.

The property (§5 guard 1): a path that consumed any adversarial answer *before* the
approved transition never ends `approved` or `merged`. The only adversarial answers a
review-complete job may have seen are the merge-boundary ones — a merge deny, a stale
merge, an unavailable merge — because `approved` was already durable when they arrived
and §2 licenses no edge that could take it back. Every E-12 fake asserts the grant
discipline on every call, so §5 guard 2 rides every leaf too.
"""

from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from lifecycle_cascade_bench import (  # noqa: E402
    FakeEscalation,
    bench,
    make_deny,
    make_deps,
    make_facts,
    make_finding,
    make_grant,
    make_judgement,
    make_panel,
    make_plan,
    make_snapshot,
    make_validation_failure,
    stored_status,
)

from rqa.contracts import (  # noqa: E402
    Activity,
    BundleFailure,
    CarryOver,
    Category,
    EscalationCause,
    EvidenceState,
    GithubUnavailable,
    Grant,
    JobStatus,
    LeaseTaken,
    Mutation,
    RemediationPushed,
    RemediationRefused,
    RemediationRefusalReason,
    Remedy,
    Stale,
)
from rqa.lifecycle import admit  # noqa: E402

#: Answers that are a refusal, an unavailability or a denial. `lease_taken` is a benign
#: contention outcome; the four judgement dispositions are decisions, not failures.
ADVERSARIAL = frozenset({
    "validation_failure", "deny", "unavailable", "stale", "bundle_failure",
    "incomplete_exhausted", "incomplete_budget", "refused",
})

#: The only boundaries whose adversarial answers arrive after `approved` is durable.
MERGE_POINTS = frozenset({"merge_grant", "merge"})

REST = frozenset({
    JobStatus.QUEUED, JobStatus.REMEDIATING, JobStatus.ESCALATED,
    JobStatus.CHANGES_REQUESTED, JobStatus.APPROVED, JobStatus.MERGED,
    JobStatus.STOPPED, JobStatus.SUPERSEDED,
})


class NeedChoice(Exception):
    def __init__(self, point: str, count: int):
        super().__init__(point)
        self.point = point
        self.count = count


class Script:
    """Replays a fixed choice prefix; the first un-scripted decision point reports how
    many options it has, and the search extends the prefix once per option."""

    def __init__(self, choices):
        self.choices = list(choices)
        self.index = 0
        self.trace = []

    def choose(self, point: str, options):
        if self.index == len(self.choices):
            raise NeedChoice(point, len(options))
        label, factory = options[self.choices[self.index]]
        self.index += 1
        self.trace.append((point, label))
        return factory()


def _judgements():
    finding = make_finding(
        finding_id="finding-1",
        categories=frozenset({Category.MECHANICAL}),
        remedy=Remedy(tool="ruff-format", paths=("src/x.py",), check="ruff-format-check"),
    )
    return (
        ("judge_approve", lambda: make_judgement(disposition="approve")),
        ("judge_request_changes", lambda: make_judgement(disposition="request_changes")),
        ("judge_remediate", lambda: make_judgement(
            disposition="remediate", findings=(finding,), remediation_candidates=("finding-1",)
        )),
        ("judge_escalate", lambda: make_judgement(
            disposition="escalate",
            escalation_causes=((EscalationCause.EVIDENCE_GAP, "ob-1 evidence is unknown"),),
            obligations={"ob-1": EvidenceState.UNKNOWN},
        )),
    )


def _run_one(choices):
    """Play one scripted admission to its leaf. Raises `NeedChoice` at the first
    boundary the prefix does not cover."""
    connection, record, job = bench()
    script = Script(choices)
    facts = make_facts(job=job)
    snapshot = make_snapshot()

    class Policy:
        store = object()

        def snapshot_for(self, *, repo, job, store, record):
            if job is not None and job.snapshot_hash is not None:
                return snapshot  # the pinned read is not a decision point
            return script.choose("policy", (
                ("snapshot", lambda: snapshot),
                ("validation_failure", make_validation_failure),
            ))

    class Authority:
        github = object()
        store = object()

        def grant(self, *, repo, activity, snapshot, job_id, categories, record, github, store):
            point = {
                Activity.REVIEW: "review_grant",
                Activity.REMEDIATE: "remediation_grant",
                Activity.APPROVE: "verdict_grant",
                Activity.REQUEST_CHANGES: "verdict_grant",
                Activity.COMMENT: "comment_grant",
                Activity.MERGE: "merge_grant",
            }[activity]
            return script.choose(point, (
                ("grant", lambda: make_grant(activity, categories=categories)),
                ("deny", lambda: make_deny(activity)),
            ))

    class Github:
        def facts(self, *, job, record):
            return script.choose("facts", (
                ("facts", lambda: facts),
                ("unavailable", lambda: GithubUnavailable(op="facts", reason="incomplete", retriable=True)),
            ))

        def submit_review(self, *, job, state, body, grant, record):
            assert isinstance(grant, Grant) and grant.activity in (
                Activity.APPROVE, Activity.REQUEST_CHANGES
            ), "submit without a verdict Grant"
            return script.choose("submit", (
                ("mutation", lambda: Mutation(id="m-s", kind="submit_review", accepted=True)),
                ("stale", lambda: Stale(reason="head_changed", observed_head_sha="f" * 40)),
                ("unavailable", lambda: GithubUnavailable(op="submit_review", reason="incomplete", retriable=True)),
            ))

        def comment(self, *, job, body, grant, record):
            assert isinstance(grant, Grant) and grant.activity is Activity.COMMENT
            return Mutation(id="m-c", kind="comment", accepted=True)

        def merge(self, *, job, grant, record):
            assert isinstance(grant, Grant) and grant.activity is Activity.MERGE, (
                "merge without a MERGE Grant"
            )
            return script.choose("merge", (
                ("mutation", lambda: Mutation(id="m-m", kind="merge", accepted=True)),
                ("stale", lambda: Stale(reason="head_changed", observed_head_sha="f" * 40)),
                ("unavailable", lambda: GithubUnavailable(op="merge", reason="incomplete", retriable=True)),
            ))

    class Harness:
        def plan(self, *, job, facts, snapshot, carry, record):
            return make_plan()

        def run(self, *, job, plan, facts, snapshot, supply, state_dir, record):
            return script.choose("run", (
                ("panel", lambda: make_panel()),
                ("incomplete_exhausted", lambda: make_panel(complete=False, incomplete_reason="exhausted")),
                ("incomplete_budget", lambda: make_panel(complete=False, incomplete_reason="budget")),
                ("bundle_failure", lambda: BundleFailure(reason="assembly failed")),
            ))

    class Judgement:
        def judge(self, *, job, plan, panel, carry, facts, snapshot, decision, record):
            return script.choose("judge", _judgements())

    class Reuse:
        def carry_over(self, *, job, prior, facts, snapshot, record):
            return CarryOver(reused=(), regenerated=(), reasons={}, source_job=None)

    class Remediation:
        def remediate(self, *, job, finding, grant, facts, snapshot, state_dir, runner, record):
            assert isinstance(grant, Grant) and grant.activity is Activity.REMEDIATE
            return script.choose("remediate", (
                ("pushed", lambda: RemediationPushed(new_head_sha="d" * 40, tool_id="ruff-format", entry_seq=9)),
                ("refused", lambda: RemediationRefused(
                    reason=RemediationRefusalReason.REMEDY_MISSING, detail="x", entry_seq=9
                )),
            ))

    def claim_lease(*, job, grant, record):
        assert isinstance(grant, Grant) and grant.activity is Activity.REVIEW
        return script.choose("claim", (
            ("mutation", lambda: Mutation(id="m-l", kind="claim_lease", accepted=True)),
            ("lease_taken", lambda: LeaseTaken(login="someone-else")),
            ("unavailable", lambda: GithubUnavailable(op="claim_lease", reason="incomplete", retriable=True)),
        ))

    def release_lease(*, job, grant, record):
        assert isinstance(grant, Grant) and grant.activity is Activity.REVIEW
        return Mutation(id="m-r", kind="release_lease", accepted=True)

    deps = make_deps(
        connection, record,
        policy=Policy(), authority=Authority(), github=Github(), harness=Harness(),
        judgement=Judgement(), reuse=Reuse(), remediation=Remediation(),
        escalation=FakeEscalation(),
        claim_lease=claim_lease, release_lease=release_lease,
    )
    final = admit(job=job, deps=deps)
    return final, script.trace, connection


def test_t13_no_adversarial_answer_before_approval_ever_reaches_review_complete() -> None:
    pending = [[]]
    leaves = 0
    seen_finals = set()
    while pending:
        prefix = pending.pop()
        try:
            final, trace, connection = _run_one(prefix)
        except NeedChoice as need:
            pending.extend(prefix + [option] for option in range(need.count))
            continue
        leaves += 1
        seen_finals.add(final)

        # Every leaf rests in a legal resting status, durably.
        assert final in REST, (final, trace)
        assert stored_status(connection) in {status.value for status in REST}, trace
        assert stored_status(connection) == final.value, trace

        # §5 guard 1 / T13: any refusal, unavailability or denial consumed before the
        # approval boundary keeps review-complete unreachable.
        pre_approval_adversarial = [
            (point, label)
            for point, label in trace
            if label in ADVERSARIAL and point not in MERGE_POINTS
        ]
        if pre_approval_adversarial:
            assert final not in (JobStatus.APPROVED, JobStatus.MERGED), (
                f"an adversarial path reached {final.value}: {trace}"
            )

    # The search must actually have explored the tree: every disposition, every
    # failure family, and both review-complete states are reachable somewhere.
    assert leaves >= 25, leaves
    assert JobStatus.APPROVED in seen_finals and JobStatus.MERGED in seen_finals
    assert JobStatus.STOPPED in seen_finals and JobStatus.ESCALATED in seen_finals
    assert JobStatus.REMEDIATING in seen_finals and JobStatus.CHANGES_REQUESTED in seen_finals
    assert JobStatus.QUEUED in seen_finals


def test_t13_the_all_clean_path_is_the_only_shape_that_reaches_review_complete() -> None:
    """The converse witness: replaying the discovered tree, every leaf that ended
    review-complete consumed only clean answers (plus, at most, merge-boundary
    failures after approval was already durable)."""
    pending = [[]]
    complete_traces = []
    while pending:
        prefix = pending.pop()
        try:
            final, trace, _ = _run_one(prefix)
        except NeedChoice as need:
            pending.extend(prefix + [option] for option in range(need.count))
            continue
        if final in (JobStatus.APPROVED, JobStatus.MERGED):
            complete_traces.append(trace)
    assert complete_traces, "the clean path must exist"
    for trace in complete_traces:
        for point, label in trace:
            if label in ADVERSARIAL:
                assert point in MERGE_POINTS, trace
