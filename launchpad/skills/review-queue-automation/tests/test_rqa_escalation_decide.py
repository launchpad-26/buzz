#!/usr/bin/env python3
"""`decide()` — `code/P-11-escalation.md` §3, §8 rows T5-T17.

No pytest: every `test_*` function takes no arguments, per `tests/run_all.py`.

Every test raises through the real `raise_()` first, so `store.get(escalation_id)`
reflects genuinely-inserted state rather than a hand-built row — the same discipline
`test_rqa_escalation_raise.py` uses.
"""

from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from test_rqa_escalation_fixtures import (  # noqa: E402
    SENTINEL_DEPS,
    FakeJobs,
    FakeLifecycle,
    FakeRecord,
    FakeStore,
    SUBJECT,
    make_job,
)

from rqa.contracts import (  # noqa: E402
    AppendFailed,
    Decision,
    EscalationCause,
    EscalationRefusalReason,
    EscalationRefused,
)
from rqa.escalation import EscalationError, decide, raise_  # noqa: E402


def _expect(kind, callable_, *args, **kwargs):
    try:
        callable_(*args, **kwargs)
    except kind as exc:
        return exc
    raise AssertionError(f"{kind.__name__} was not raised")


def _raised(*, cause=EscalationCause.EVIDENCE_GAP, context=None, job=None):
    """A real, open escalation over a fresh `FakeRecord`/`FakeStore`, plus the job it
    was raised against — the shared setup every `decide()` test starts from."""
    job = job if job is not None else make_job()
    record = FakeRecord()
    store = FakeStore()
    escalation = raise_(
        job=job,
        cause=cause,
        subject=SUBJECT,
        question="a specific question",
        context=context if context is not None else {},
        record=record,
        store=store,
    )
    return job, record, store, escalation


def _decide(job, record, store, escalation, *, actor="human-reviewer", basis="reviewed", outcome=None,
            jobs=None, lifecycle=None, deps=SENTINEL_DEPS):
    return decide(
        escalation.id,
        actor,
        basis,
        outcome,
        store=store,
        record=record,
        jobs=jobs if jobs is not None else FakeJobs(job),
        lifecycle=lifecycle if lifecycle is not None else FakeLifecycle(),
        deps=deps,
    )


# -- T5 / T6 -----------------------------------------------------------------------


def test_t5_a_blank_actor_raises_and_calls_neither_close_nor_resume() -> None:
    job, record, store, escalation = _raised()
    lifecycle = FakeLifecycle()
    _expect(EscalationError, _decide, job, record, store, escalation, actor="", lifecycle=lifecycle)
    assert record.of_kind("decision") == []
    assert store.close_calls == []
    assert lifecycle.calls == []


def test_t6_a_blank_basis_raises_the_same_way() -> None:
    job, record, store, escalation = _raised()
    lifecycle = FakeLifecycle()
    _expect(EscalationError, _decide, job, record, store, escalation, basis="   ", lifecycle=lifecycle)
    assert record.of_kind("decision") == []
    assert store.close_calls == []
    assert lifecycle.calls == []


# -- T7 --------------------------------------------------------------------------


def test_t7_an_outcome_on_a_non_authority_cause_raises() -> None:
    job, record, store, escalation = _raised(cause=EscalationCause.EVIDENCE_GAP)
    _expect(EscalationError, _decide, job, record, store, escalation, outcome="approved")
    assert record.of_kind("decision") == []


# -- T8 --------------------------------------------------------------------------


def test_t8_an_authority_requirement_outcome_is_recorded_with_no_substantiation() -> None:
    job, record, store, escalation = _raised(cause=EscalationCause.AUTHORITY_REQUIREMENT)
    result = _decide(job, record, store, escalation, outcome="approved")
    assert result == Decision(
        actor="human-reviewer", basis="reviewed", substantiates=None, outcome="approved"
    )
    assert record.of_kind("decision") == [
        {
            "escalation_id": escalation.id,
            "cause": "authority_requirement",
            "actor": "human-reviewer",
            "basis": "reviewed",
            "substantiates": None,
            "outcome": "approved",
        }
    ]


# -- T9 --------------------------------------------------------------------------


def test_t9_a_required_information_decision_substantiates_its_own_obligation() -> None:
    job, record, store, escalation = _raised(
        cause=EscalationCause.REQUIRED_INFORMATION, context={"obligation": "OBL-3"}
    )
    result = _decide(job, record, store, escalation, outcome=None)
    assert result == Decision(
        actor="human-reviewer", basis="reviewed", substantiates="OBL-3", outcome=None
    )


# -- T10 / T11 ---------------------------------------------------------------------


def test_t10_a_moved_head_refuses_and_makes_no_write() -> None:
    job, record, store, escalation = _raised()
    moved = make_job(job_id=job.id, head_sha="c" * 40, snapshot_hash=job.snapshot_hash)
    lifecycle = FakeLifecycle()
    result = _decide(job, record, store, escalation, jobs=FakeJobs(moved), lifecycle=lifecycle)
    assert result == EscalationRefused(
        EscalationRefusalReason.HEAD_MOVED, detail=f"job head is now {moved.head_sha}"
    )
    assert store.get(escalation.id).status == "open"
    assert record.of_kind("decision") == []
    assert lifecycle.calls == []


def test_t11_a_moved_snapshot_with_a_matching_head_refuses_the_same_way() -> None:
    job, record, store, escalation = _raised()
    moved = make_job(job_id=job.id, head_sha=job.head_sha, snapshot_hash="sha256:snapshot-2")
    lifecycle = FakeLifecycle()
    result = _decide(job, record, store, escalation, jobs=FakeJobs(moved), lifecycle=lifecycle)
    assert result == EscalationRefused(
        EscalationRefusalReason.SNAPSHOT_MOVED, detail="job snapshot is now 'sha256:snapshot-2'"
    )
    assert store.get(escalation.id).status == "open"
    assert record.of_kind("decision") == []
    assert lifecycle.calls == []


# -- E-B5-1: an unpinned job's escalation compares None-to-None, not str-to-None -----


def test_e_b5_1_an_unpinned_escalation_completes_when_the_job_is_still_unpinned() -> None:
    """`CONTRACTS.md` §1: `Job.snapshot_hash: str | None`. A job escalated before P-03
    ever returned a real `Snapshot` (P-02's `ValidationFailure` branch of step 3) has
    `snapshot_hash=None` on both the escalation and the current job — `None != None` is
    `False`, so step 8 does not refuse, and the decision completes normally."""
    unpinned = make_job(snapshot_hash=None)
    job, record, store, escalation = _raised(job=unpinned, cause=EscalationCause.AUTHORITY_REQUIREMENT)
    assert escalation.snapshot_hash is None
    lifecycle = FakeLifecycle()
    result = _decide(
        job, record, store, escalation, outcome="approved",
        jobs=FakeJobs(unpinned), lifecycle=lifecycle,
    )
    assert isinstance(result, Decision)
    assert result.outcome == "approved"
    assert store.get(escalation.id).status == "closed"
    assert len(lifecycle.calls) == 1


def test_e_b5_1_a_job_pinned_after_an_unpinned_escalation_refuses_snapshot_moved() -> None:
    """The converse: an escalation raised while unpinned (`snapshot_hash=None`), then
    the job is pinned to a real snapshot before the human decides — `None != "sha256:
    snapshot-2"` is `True`, so step 8 refuses `SNAPSHOT_MOVED` exactly as it would for
    two different real hashes."""
    unpinned = make_job(snapshot_hash=None)
    job, record, store, escalation = _raised(job=unpinned, cause=EscalationCause.AUTHORITY_REQUIREMENT)
    now_pinned = make_job(job_id=job.id, head_sha=job.head_sha, snapshot_hash="sha256:snapshot-2")
    lifecycle = FakeLifecycle()
    result = _decide(
        job, record, store, escalation, outcome="approved",
        jobs=FakeJobs(now_pinned), lifecycle=lifecycle,
    )
    assert result == EscalationRefused(
        EscalationRefusalReason.SNAPSHOT_MOVED, detail="job snapshot is now 'sha256:snapshot-2'"
    )
    assert store.get(escalation.id).status == "open"
    assert lifecycle.calls == []


def test_a_job_that_no_longer_exists_is_also_head_moved() -> None:
    job, record, store, escalation = _raised()
    result = _decide(job, record, store, escalation, jobs=FakeJobs(None))
    assert result == EscalationRefused(EscalationRefusalReason.HEAD_MOVED, detail="job head is now <gone>")


# -- T12 -------------------------------------------------------------------------


def test_t12_an_unknown_escalation_id_is_not_found() -> None:
    job, record, store, escalation = _raised()
    result = decide(
        escalation.id + 999,
        "human-reviewer",
        "reviewed",
        None,
        store=store,
        record=record,
        jobs=FakeJobs(job),
        lifecycle=FakeLifecycle(),
        deps=SENTINEL_DEPS,
    )
    assert result == EscalationRefused(
        EscalationRefusalReason.NOT_FOUND, detail=f"no escalation {escalation.id + 999}"
    )


# -- T13 -------------------------------------------------------------------------


def test_t13_a_second_decide_on_the_same_escalation_is_already_closed() -> None:
    job, record, store, escalation = _raised()
    first = _decide(job, record, store, escalation)
    assert isinstance(first, Decision)
    second = _decide(job, record, store, escalation, actor="someone-else")
    assert second == EscalationRefused(
        EscalationRefusalReason.ALREADY_CLOSED, detail=f"escalation {escalation.id} is already closed"
    )
    assert len(record.of_kind("decision")) == 1


# -- T14 -------------------------------------------------------------------------


def test_t14_the_decision_entry_carries_all_six_fields_readable_back() -> None:
    job, record, store, escalation = _raised(
        cause=EscalationCause.CONFLICTING_JUDGEMENT, context={"obligation": "OBL-9"}
    )
    _decide(job, record, store, escalation, actor="alice", basis="checked both reviews")
    [payload] = record.of_kind("decision")
    assert payload == {
        "escalation_id": escalation.id,
        "cause": "conflicting_judgement",
        "actor": "alice",
        "basis": "checked both reviews",
        "substantiates": "OBL-9",
        "outcome": None,
    }


# -- T15 -------------------------------------------------------------------------


def test_t15_a_successful_decide_closes_the_row_and_drops_it_from_pending() -> None:
    from rqa.escalation import pending

    job, record, store, escalation = _raised()
    _decide(job, record, store, escalation)
    row = store.get(escalation.id)
    assert row.status == "closed"
    [decision_payload] = record.of_kind("decision")
    assert row.decision_entry_seq == 2  # entry 1 is `escalation`, entry 2 is `decision`
    assert pending(store=store) == ()


# -- T16 -------------------------------------------------------------------------


def test_t16_resume_is_called_exactly_once_with_the_verbatim_keywords_and_its_return_is_ignored() -> None:
    job, record, store, escalation = _raised(cause=EscalationCause.AUTHORITY_REQUIREMENT)
    lifecycle = FakeLifecycle(status=None)  # a deliberately unusable return value
    result = _decide(job, record, store, escalation, outcome="changes_requested", lifecycle=lifecycle)
    assert isinstance(result, Decision)
    assert len(lifecycle.calls) == 1
    call = lifecycle.calls[0]
    assert call["job_id"] == escalation.job_id
    assert call["decision"] == result
    assert call["deps"] is SENTINEL_DEPS


# -- T17 -------------------------------------------------------------------------


def test_t17_a_failed_decision_append_propagates_and_leaves_the_row_open() -> None:
    job, record, store, escalation = _raised()
    lifecycle = FakeLifecycle()
    failing_record = FakeRecord(fail=True)
    _expect(
        AppendFailed,
        _decide,
        job,
        failing_record,
        store,
        escalation,
        lifecycle=lifecycle,
    )
    assert store.get(escalation.id).status == "open"
    assert store.close_calls == []
    assert lifecycle.calls == []
