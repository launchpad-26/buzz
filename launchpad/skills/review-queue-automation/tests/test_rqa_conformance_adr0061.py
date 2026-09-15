#!/usr/bin/env python3
"""Task #2216 — ADR-0061's executable half: a decision transitions ONLY on a visible
matching same-head review, and refuses when none is visible (AC13, AC14).

ADR-0061, verbatim: "A human decision on an *authority requirement* escalation does
not re-enter the verdict step. ... The human acts on GitHub; P-02 verifies the
submitted review is visible at the same head and transitions the job directly to
`approved` or `changes_requested` (flow step 12b)."

Every test here drives the REAL `rqa.lifecycle.resume()` against a REAL, persisted
escalation raised through the REAL `rqa.escalation.raise_()` and a REAL
`SqliteEscalationStore`, exactly as `tests/test_rqa_escalation_ac13_resume.py`
wires the completing round trip. What varies is the world 12b verifies against —
the set of reviews E-23 reports — because that set is the whole of what ADR-0061
lets a decision rest on.

These tests assert contract-permanent properties only. They do not assert that the
composed system can reach step 10a (it cannot today — #2274 and F-2 deny REVIEW
before any judgement exists); the recorded runbook (`TESTING.md` Part 2 §11.1)
carries that evidence and its attribution.
"""

from __future__ import annotations

import pathlib
import sys
from datetime import datetime, timezone

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from lifecycle_cascade_bench import (  # noqa: E402
    SNAP_HASH,
    FakeGithub,
    bench,
    make_decision,
    make_facts,
    make_review,
    make_deps,
    stored_status,
    transitions,
)

import rqa.escalation as escalation  # noqa: E402
from rqa.contracts import (  # noqa: E402
    EscalationCause,
    EscalationSubject,
    EscalationSubjectKind,
    JobStatus,
)
from rqa.escalation.store import SqliteEscalationStore  # noqa: E402
from rqa.lifecycle import resume  # noqa: E402
from rqa.lifecycle.errors import LifecycleError, StaleDecisionError  # noqa: E402

#: `raise_()` stamps `raised_at` with the real wall clock; a fixed far-future
#: `submitted_at` keeps "submitted after the escalation was raised" true forever
#: rather than only until the bench's NOW constant ages out.
_FAR_FUTURE = datetime(2100, 1, 1, tzinfo=timezone.utc)

_WRONG_HEAD = "f" * 40


def _escalated_job(reviews: tuple) -> tuple:
    """A job resting ESCALATED on a real authority-requirement escalation, plus deps
    whose E-23 reports exactly `reviews`."""
    connection, record, job = bench(status=JobStatus.ESCALATED, snapshot_hash=SNAP_HASH)
    record.append(job.id, "transition", {
        "from_state": None, "to_state": "queued", "reason": "arrival", "repo": job.repo,
        "number": job.number, "head_sha": job.head_sha, "base_sha": job.base_sha,
        "predecessor_job": None,
    })
    connection.commit()
    store = SqliteEscalationStore(connection)
    raised = escalation.raise_(
        job=job,
        cause=EscalationCause.AUTHORITY_REQUIREMENT,
        subject=EscalationSubject(EscalationSubjectKind.AUTHORITY, "merge"),
        question="RQA holds no verdict authority here; a human must record the outcome",
        context={},
        record=record,
        store=store,
    )
    connection.commit()
    deps = make_deps(
        connection,
        record,
        github=FakeGithub(facts=make_facts(job=job, reviews=reviews)),
        # Deliberately absent: 12b never re-enters planning or judgement (ADR-0061).
        policy=None, authority=None, judgement=None, harness=None, supply=None,
        remediation=None, reuse=None,
    )
    return connection, job, store, raised, deps


def _assert_refused_and_untouched(connection, job, exc: Exception | None) -> None:
    """The refusal shape ADR-0061 requires: a StaleDecisionError, no transition, the
    job still resting where the human found it."""
    assert isinstance(exc, StaleDecisionError), exc
    assert stored_status(connection, job.id) == "escalated"
    assert transitions(connection, job.id) == ["queued", "escalated"] or transitions(
        connection, job.id
    ) == ["queued"], transitions(connection, job.id)


def _resume(job, deps, *, outcome: str = "approved") -> Exception | None:
    try:
        resume(job_id=job.id, decision=make_decision(outcome=outcome), deps=deps)
    except (StaleDecisionError, LifecycleError) as exc:
        return exc
    return None


def test_adr0061_no_visible_matching_review_refuses_and_transitions_nothing() -> None:
    """AC13/DoD: "`rqa decide` ... refuses when none is visible." Zero submitted
    reviews match the decision; 12b refuses and the job does not move."""
    connection, job, store, raised, deps = _escalated_job(reviews=())
    exc = _resume(job, deps)
    _assert_refused_and_untouched(connection, job, exc)
    assert "0 submitted reviews match" in str(exc)


def test_adr0061_a_review_at_a_different_head_is_not_a_matching_review() -> None:
    """"visible at the same head" is part of the match, not decoration: an approving
    review by the right actor after the escalation, but at another head, refuses."""
    connection, job, store, raised, deps = _escalated_job(
        reviews=(make_review(head_sha=_WRONG_HEAD, submitted_at=_FAR_FUTURE),)
    )
    exc = _resume(job, deps)
    _assert_refused_and_untouched(connection, job, exc)


def test_adr0061_two_matching_reviews_are_not_exactly_one_and_refuse() -> None:
    """12b requires exactly one same-head, post-escalation review; an ambiguous pair
    is a refusal, never a coin toss."""
    connection, job, store, raised, deps = _escalated_job(
        reviews=(
            make_review(review_id="review-1", submitted_at=_FAR_FUTURE),
            make_review(review_id="review-2", submitted_at=_FAR_FUTURE),
        )
    )
    exc = _resume(job, deps)
    _assert_refused_and_untouched(connection, job, exc)
    assert "2 submitted reviews match" in str(exc)


def test_adr0061_an_authority_requirement_decision_must_carry_the_humans_outcome() -> None:
    """ADR-0061 makes the human's GitHub outcome the authoritative one; a decision
    that names no outcome cannot transition an authority-requirement escalation."""
    connection, job, store, raised, deps = _escalated_job(
        reviews=(make_review(submitted_at=_FAR_FUTURE),)
    )
    exc = _resume(job, deps, outcome=None)
    assert isinstance(exc, LifecycleError), exc
    assert stored_status(connection, job.id) == "escalated"


def test_adr0061_exactly_one_matching_same_head_review_transitions_directly() -> None:
    """The positive clause: one matching review moves `escalated` directly to the
    human's outcome — no planned/reviewing/judged transition, because a decision on an
    authority-requirement escalation never re-enters the verdict step (ADR-0061)."""
    connection, job, store, raised, deps = _escalated_job(
        reviews=(make_review(outcome="changes_requested", submitted_at=_FAR_FUTURE),)
    )
    result = resume(
        job_id=job.id, decision=make_decision(outcome="changes_requested"), deps=deps
    )
    assert result is JobStatus.CHANGES_REQUESTED
    assert stored_status(connection, job.id) == "changes_requested"
    assert transitions(connection, job.id) == ["queued", "changes_requested"]
