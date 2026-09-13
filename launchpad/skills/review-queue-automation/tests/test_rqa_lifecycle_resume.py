#!/usr/bin/env python3
"""`resume()` — steps 12a/12b, the E-11 reverse edge — `code/P-02-lifecycle.md` §3.3;
§8 rows T14, T15, T16; AC14's human-outcome half (ADR-0061).

No pytest: every `test_*` function takes no arguments, per `tests/run_all.py`.

The 12a re-judgements drive the REAL `rqa.judgement.judge` against the reconstructed
plan/carry/panel, so the cutoff semantics asserted here are P-07's real ones, not a
fake's. P-11 itself is Batch 5 and is faked through the `EscalationClient` Protocol.
"""

from __future__ import annotations

import dataclasses
import pathlib
import sys
from datetime import timedelta

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from lifecycle_cascade_bench import (  # noqa: E402
    HEAD,
    NOW,
    REPO,
    SNAP_HASH,
    FakeAuthority,
    FakeEscalation,
    FakeGithub,
    FakeJudgement,
    FakeLease,
    FakePolicy,
    RealJudgement,
    bench,
    latest_payload,
    make_decision,
    make_deny,
    make_deps,
    make_escalation,
    make_facts,
    make_judgement,
    make_plan,
    make_review,
    make_snapshot,
    stored_status,
    transitions,
)

from rqa.contracts import (  # noqa: E402
    Activity,
    AppendFailed,
    CheckConclusion,
    CheckRun,
    EscalationCause,
    GithubUnavailable,
    JobStatus,
)
from rqa.lifecycle import resume  # noqa: E402
from rqa.lifecycle.errors import (  # noqa: E402
    LifecycleError,
    StaleDecisionError,
    UnknownJobError,
)


def _escalated_bench(*, cause=EscalationCause.AUTHORITY_REQUIREMENT, raised_at=NOW):
    connection, record, job = bench(status=JobStatus.ESCALATED, snapshot_hash=SNAP_HASH)
    record.append(job.id, "transition", {
        "from_state": None, "to_state": "queued", "reason": "arrival", "repo": job.repo,
        "number": job.number, "head_sha": job.head_sha, "base_sha": job.base_sha,
        "predecessor_job": None,
    })
    connection.commit()
    escalation = make_escalation(job=job, cause=cause, raised_at=raised_at)
    return connection, record, job, escalation


def _deps(connection, record, job, escalation, *, facts=None, reviews=(), **overrides):
    """`escalation=None` means no open escalation is pending."""
    lease = FakeLease()
    clients = {
        "policy": FakePolicy(make_snapshot()),
        "authority": FakeAuthority({Activity.MERGE: [make_deny(Activity.MERGE)]}),
        "github": FakeGithub(
            facts=facts if facts is not None else make_facts(job=job, reviews=reviews)
        ),
        "judgement": RealJudgement(),
        "escalation": FakeEscalation(pending=() if escalation is None else (escalation,)),
        "claim_lease": lease.claim,
        "release_lease": lease.release,
    }
    clients.update(overrides)
    return make_deps(connection, record, **clients)


def _expect(kind, callable_, *args, **kwargs):
    try:
        callable_(*args, **kwargs)
    except kind as exc:
        return exc
    raise AssertionError(f"{kind.__name__} was not raised")


# -- loading and precondition errors ------------------------------------------------


def test_an_absent_job_raises_unknown_job_error() -> None:
    connection, record, job, escalation = _escalated_bench()
    deps = _deps(connection, record, job, escalation)
    _expect(UnknownJobError, resume, job_id="job-nope", decision=make_decision(), deps=deps)


def test_a_job_not_at_escalated_raises_lifecycle_error() -> None:
    connection, record, job = bench(status=JobStatus.JUDGED, snapshot_hash=SNAP_HASH)
    deps = _deps(connection, record, job, make_escalation(job=job))
    exc = _expect(LifecycleError, resume, job_id=job.id, decision=make_decision(), deps=deps)
    assert "judged" in str(exc)


def test_an_escalated_job_with_no_open_escalation_raises() -> None:
    connection, record, job, _ = _escalated_bench()
    deps = _deps(connection, record, job, None)
    _expect(LifecycleError, resume, job_id=job.id, decision=make_decision(), deps=deps)


def test_unavailable_facts_stop_the_job_and_leave_the_decision_unapplied() -> None:
    connection, record, job, escalation = _escalated_bench()
    deps = _deps(
        connection, record, job, escalation,
        github=FakeGithub(facts=GithubUnavailable(op="facts", reason="incomplete", retriable=True)),
    )
    assert resume(job_id=job.id, decision=make_decision(), deps=deps) is JobStatus.STOPPED
    assert latest_payload(connection, "transition")["reason"] == "facts unavailable"


# -- T16: staleness is fail-closed, and never a local alternative --------------------


def test_t16_a_moved_head_raises_and_makes_no_transition() -> None:
    """A review matching the *recorded* head is present, so only the freshness guard
    stands between this stale decision and a transition — deleting the guard fails
    this test, not a later check."""
    connection, record, job, escalation = _escalated_bench()
    moved = dataclasses.replace(job, head_sha="f" * 40)
    facts = make_facts(job=moved)
    facts = dataclasses.replace(facts, reviews=(make_review(head_sha=job.head_sha),))
    deps = _deps(connection, record, job, escalation, facts=facts)
    _expect(StaleDecisionError, resume, job_id=job.id, decision=make_decision(), deps=deps)
    assert stored_status(connection) == "escalated"
    assert transitions(connection) == ["queued"]


def test_t16_a_moved_snapshot_raises_and_makes_no_transition() -> None:
    connection, record, job, _ = _escalated_bench()
    stale = make_escalation(job=job, snapshot_hash="sha256:some-older-snapshot")
    deps = _deps(connection, record, job, stale, reviews=(make_review(),))
    _expect(StaleDecisionError, resume, job_id=job.id, decision=make_decision(), deps=deps)
    assert transitions(connection) == ["queued"]


def test_t16_absent_ambiguous_or_mismatched_reviews_raise() -> None:
    for reviews in (
        (),  # absent
        (make_review(review_id="r1"), make_review(review_id="r2")),  # ambiguous
        (make_review(actor="somebody-else"),),  # wrong actor
        (make_review(outcome="changes_requested"),),  # wrong outcome
        (make_review(head_sha="f" * 40),),  # wrong head
        (make_review(submitted_at=NOW - timedelta(hours=1)),),  # before the escalation
    ):
        connection, record, job, escalation = _escalated_bench()
        deps = _deps(connection, record, job, escalation, reviews=reviews)
        _expect(StaleDecisionError, resume, job_id=job.id, decision=make_decision(), deps=deps)
        assert stored_status(connection) == "escalated"
        assert transitions(connection) == ["queued"]


def test_a_12b_decision_without_an_outcome_raises() -> None:
    connection, record, job, escalation = _escalated_bench()
    deps = _deps(connection, record, job, escalation, reviews=(make_review(),))
    _expect(
        LifecycleError, resume,
        job_id=job.id, decision=make_decision(outcome=None), deps=deps,
    )
    assert transitions(connection) == ["queued"]


# -- T15: 12b admits exactly one matching human outcome ------------------------------


def test_t15_one_matching_review_transitions_directly_with_no_verdict_grant() -> None:
    connection, record, job, escalation = _escalated_bench()
    deps = _deps(connection, record, job, escalation, reviews=(make_review(),))
    assert resume(job_id=job.id, decision=make_decision(), deps=deps) is JobStatus.APPROVED
    assert transitions(connection) == ["queued", "approved"]  # escalated → approved, directly
    asked = [call[0] for call in deps.authority.calls]
    assert Activity.APPROVE not in asked and Activity.REQUEST_CHANGES not in asked
    assert deps.github.submit_calls == []  # the human already submitted; RQA never does
    assert Activity.MERGE in asked  # step 11 ran for the approval
    assert latest_payload(connection, "transition")["reason"] == "recorded human outcome: approved"


def test_t15_a_changes_requested_outcome_rests_blocked() -> None:
    connection, record, job, escalation = _escalated_bench()
    deps = _deps(
        connection, record, job, escalation,
        reviews=(make_review(outcome="changes_requested"),),
    )
    decision = make_decision(outcome="changes_requested")
    assert resume(job_id=job.id, decision=decision, deps=deps) is JobStatus.CHANGES_REQUESTED
    assert transitions(connection) == ["queued", "changes_requested"]


def test_a_12b_approval_with_a_granted_merge_reaches_merged() -> None:
    connection, record, job, escalation = _escalated_bench()
    deps = _deps(
        connection, record, job, escalation,
        reviews=(make_review(),),
        authority=FakeAuthority(),  # merge granted
    )
    assert resume(job_id=job.id, decision=make_decision(), deps=deps) is JobStatus.MERGED
    (merge_grant,) = deps.github.merge_calls
    assert merge_grant.activity is Activity.MERGE


# -- T14: 12a re-judges from the reconstruction --------------------------------------


def _twelve_a_bench(*, panel_cutoff=None):
    """An escalated job that went through plan and judgement; optionally a recorded
    fresh-run panel with the given cutoff."""
    connection, record, job, escalation = _escalated_bench(cause=EscalationCause.EVIDENCE_GAP)
    record.append(job.id, "plan", dataclasses.asdict(make_plan()))
    if panel_cutoff is not None:
        record.append(job.id, "panel", {
            "attempts": ["attempt-alpha"], "complete": True, "incomplete_reason": None,
            "evidence_cutoff": panel_cutoff.isoformat(), "bound_reached": False,
        })
    connection.commit()
    return connection, record, job, escalation


def test_t14_the_real_judge_receives_the_recorded_cutoff_and_late_checks_cannot_count() -> None:
    """Same head, newer facts: a PR check observed AFTER the recorded cutoff is not
    attributed by P-07's real cutoff-bounded attribution, so it cannot affect the
    judgement (T14)."""
    cutoff = NOW - timedelta(hours=1)
    connection, record, job, escalation = _twelve_a_bench(panel_cutoff=cutoff)
    late_check = CheckRun(
        name="ci", conclusion=CheckConclusion.FAILURE, sha=HEAD,
        observed_at=NOW + timedelta(hours=2),
    )
    facts = make_facts(job=job, checks=(late_check,), fetched_at=NOW + timedelta(hours=3))
    deps = _deps(connection, record, job, escalation, facts=facts)
    decision = make_decision(substantiates="ob-1")
    assert resume(job_id=job.id, decision=decision, deps=deps) is JobStatus.APPROVED
    payload = latest_payload(connection, "judgement")
    assert payload["cutoff"] == cutoff.isoformat()  # E-09 received the reconstructed panel
    assert payload["attribution"] == {}  # the late check did not attribute (T14)
    assert payload["decision"] == {
        "actor": "human-reviewer", "basis": "reviewed on GitHub",
        "substantiates": "ob-1", "outcome": "approved",
    }
    assert transitions(connection) == ["queued", "judged", "submitting", "approved"]


def test_t14_a_carry_only_resume_uses_the_judgement_cutoff() -> None:
    cutoff = NOW - timedelta(minutes=30)
    connection, record, job, escalation = _twelve_a_bench(panel_cutoff=None)
    record.append(job.id, "judgement", {
        "snapshot_hash": SNAP_HASH, "protocol_hash": "sha256:protocol-1",
        "cutoff": cutoff.isoformat(), "facts_fetched_at": NOW.isoformat(),
        "obligations": {"ob-1": "unknown"}, "reused_from": None, "carried_provenance": {},
        "contributing_attempts": [], "decision": None, "findings": [], "corroborated": [],
        "blocking": [], "attribution": {}, "assurance": {"required": 2, "achieved": 0},
        "remediation_candidates": [], "escalation_causes": [
            {"cause": "evidence_gap", "detail": "obligation ob-1 evidence is unknown"},
        ], "disposition": "escalate", "rendered_body": "recorded rendering",
    })
    connection.commit()
    deps = _deps(connection, record, job, escalation)
    decision = make_decision(substantiates="ob-1")
    assert resume(job_id=job.id, decision=decision, deps=deps) is JobStatus.APPROVED
    payload = latest_payload(connection, "judgement")
    assert payload["cutoff"] == cutoff.isoformat()


def test_a_12a_decision_that_does_not_settle_the_gap_escalates_again() -> None:
    """The decision substantiates nothing, so the real judge re-escalates: the review
    never silently completes on an unanswered gap, and the resume path still only
    reaches `escalated`."""
    connection, record, job, escalation = _twelve_a_bench(panel_cutoff=NOW)
    deps = _deps(connection, record, job, escalation)
    decision = make_decision(substantiates=None, outcome=None)
    assert resume(job_id=job.id, decision=decision, deps=deps) is JobStatus.ESCALATED
    assert transitions(connection) == ["queued", "judged", "escalated"]
    assert deps.escalation.raised, "the fresh causes were raised through E-11"


# -- containment (§3.1, inherited by §3.3) -------------------------------------------


def test_a_persistence_failure_during_resume_becomes_one_safe_stop() -> None:
    class FlakyWriter:
        def __init__(self, inner):
            self.inner = inner
            self.calls = 0

        def append(self, job_id, kind, payload):
            self.calls += 1
            if self.calls == 1:
                raise AppendFailed("the record could not be appended")
            return self.inner.append(job_id, kind, payload)

    connection, real_record, job, escalation = _escalated_bench(cause=EscalationCause.EVIDENCE_GAP)
    connection.execute("DELETE FROM record_entries")  # rebuild: flaky writer appends all
    connection.commit()
    record = FlakyWriter(real_record)
    deps = _deps(
        connection, record, job, escalation,
        judgement=FakeJudgement(make_judgement(disposition="approve")),
    )
    # 12a reconstruction reads durable plan and panel entries; write both with the
    # real writer so only the ESCALATED → JUDGED transition append can fail.
    real_record.append(job.id, "plan", dataclasses.asdict(make_plan()))
    real_record.append(job.id, "panel", {
        "attempts": [], "complete": True, "incomplete_reason": None,
        "evidence_cutoff": NOW.isoformat(), "bound_reached": False,
    })
    connection.commit()
    assert resume(job_id=job.id, decision=make_decision(substantiates="ob-1"), deps=deps) is JobStatus.STOPPED
    assert stored_status(connection) == "stopped"
    assert latest_payload(connection, "transition")["reason"] == (
        "persistence failure contained (AppendFailed)"
    )
