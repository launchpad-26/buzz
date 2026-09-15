#!/usr/bin/env python3
"""`raise_()` and `pending()` — `code/P-11-escalation.md` §3, §8 rows T1-T4, T19.

No pytest: every `test_*` function takes no arguments, per `tests/run_all.py`.
"""

from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from test_rqa_escalation_fixtures import (  # noqa: E402
    ALL_CAUSES,
    FakeRecord,
    FakeStore,
    NOW,
    SUBJECT,
    make_job,
)

from rqa.contracts import (  # noqa: E402
    AppendFailed,
    EscalationCause,
    EscalationSubject,
    EscalationSubjectKind,
)
from rqa.escalation import EscalationError, pending, raise_  # noqa: E402


def _expect(kind, callable_, *args, **kwargs):
    try:
        callable_(*args, **kwargs)
    except kind as exc:
        return exc
    raise AssertionError(f"{kind.__name__} was not raised")


# -- T1 --------------------------------------------------------------------------


def test_t1_raise_once_per_cause_records_five_entries_and_pending_lists_five() -> None:
    job = make_job()
    record = FakeRecord()
    store = FakeStore()

    raised = []
    for cause in ALL_CAUSES:
        escalation = raise_(
            job=job,
            cause=cause,
            subject=SUBJECT,
            question=f"a specific question about {cause.value}",
            context={"obligation": cause.value},
            record=record,
            store=store,
        )
        raised.append(escalation)

    assert len(ALL_CAUSES) == 5, "RQA-FR-026: the whole vocabulary is five causes"
    entries = record.of_kind("escalation")
    assert len(entries) == 5
    assert [entry["cause"] for entry in entries] == [cause.value for cause in ALL_CAUSES]

    listed = pending(store=store)
    assert len(listed) == 5
    assert {escalation.cause for escalation in listed} == set(ALL_CAUSES)
    for escalation, expected in zip(raised, listed, strict=True):
        assert escalation == expected


# -- T2 --------------------------------------------------------------------------


def test_t2_a_cause_outside_the_five_raises_and_writes_nothing() -> None:
    job = make_job()
    record = FakeRecord()
    store = FakeStore()

    exc = _expect(
        EscalationError,
        raise_,
        job=job,
        cause="other",  # a raw string coerced past the enum
        subject=SUBJECT,
        question="a specific question",
        context={},
        record=record,
        store=store,
    )
    assert "other" in str(exc)
    assert record.appended == []
    assert store.rows == {}


# -- F-T2: a raw string equal to a canonical value is coerced, not crashed on -------


def test_f_t2_a_raw_string_equal_to_a_canonical_value_is_coerced_and_processed() -> None:
    """The membership gate (`_VALID_CAUSES`) tolerates a raw string equal to a
    canonical `EscalationCause` value exactly like the real member — its own comment
    says so — so the rest of the function must too: this must succeed, not crash with
    `AttributeError: 'str' object has no attribute 'value'` on `cause.value` below."""
    job = make_job()
    record = FakeRecord()
    store = FakeStore()

    escalation = raise_(
        job=job,
        cause="evidence_gap",  # a raw string, not EscalationCause.EVIDENCE_GAP
        subject=SUBJECT,
        question="a specific question",
        context={},
        record=record,
        store=store,
    )
    assert escalation.cause is EscalationCause.EVIDENCE_GAP
    [entry] = record.of_kind("escalation")
    assert entry["cause"] == "evidence_gap"
    assert store.get(escalation.id).cause is EscalationCause.EVIDENCE_GAP


# -- T3 --------------------------------------------------------------------------


def test_t3_a_blank_question_raises_and_writes_nothing() -> None:
    job = make_job()
    for question in ("", "   ", "\t\n"):
        record = FakeRecord()
        store = FakeStore()
        _expect(
            EscalationError,
            raise_,
            job=job,
            cause=EscalationCause.EVIDENCE_GAP,
            subject=SUBJECT,
            question=question,
            context={},
            record=record,
            store=store,
        )
        assert record.appended == []
        assert store.rows == {}


def test_t3a_an_invalid_or_blank_subject_raises_and_writes_nothing() -> None:
    job = make_job()
    invalid_subjects = (
        None,
        EscalationSubject("other", "OBL-1"),
        EscalationSubject(EscalationSubjectKind.OBLIGATION, "  "),
    )
    for subject in invalid_subjects:
        record = FakeRecord()
        store = FakeStore()
        _expect(
            EscalationError,
            raise_,
            job=job,
            cause=EscalationCause.EVIDENCE_GAP,
            subject=subject,
            question="needs attention",
            context={},
            record=record,
            store=store,
        )
        assert record.appended == []
        assert store.rows == {}


def test_a_generic_question_still_names_the_specific_subject_structurally() -> None:
    record = FakeRecord()
    store = FakeStore()
    result = raise_(
        job=make_job(),
        cause=EscalationCause.EVIDENCE_GAP,
        subject=SUBJECT,
        question="needs attention",
        context={},
        record=record,
        store=store,
    )
    assert result.subject == SUBJECT
    [entry] = record.of_kind("escalation")
    assert entry["subject"] == {"kind": "obligation", "identifier": "OBL-1"}


# -- T4 --------------------------------------------------------------------------


def test_t4_a_failed_append_propagates_and_writes_no_index_row() -> None:
    job = make_job()
    record = FakeRecord(fail=True)
    store = FakeStore()

    _expect(
        AppendFailed,
        raise_,
        job=job,
        cause=EscalationCause.UNRESOLVED_DECISION,
        subject=SUBJECT,
        question="a specific question",
        context={},
        record=record,
        store=store,
    )
    assert store.rows == {}, "no index row without a record entry behind it"


# -- T19 -------------------------------------------------------------------------


def test_t19_pending_with_no_open_escalations_is_empty() -> None:
    assert pending(store=FakeStore()) == ()


# -- RQA-FR-026: no sixth value, no free text -------------------------------------


def test_the_vocabulary_is_closed_with_no_other_or_free_text_member() -> None:
    values = {cause.value for cause in EscalationCause}
    assert values == {
        "unresolved_decision",
        "conflicting_judgement",
        "evidence_gap",
        "required_information",
        "authority_requirement",
    }
    assert "other" not in values


def test_returned_escalations_are_ordered_oldest_first() -> None:
    """Tests forwarding; production ordering is covered in test_rqa_escalation_store.py."""
    from datetime import timedelta

    job = make_job()
    record = FakeRecord()
    store = FakeStore()
    later = NOW + timedelta(minutes=5)
    earlier = NOW - timedelta(minutes=5)

    # Insert out of chronological order directly against the store so ordering is
    # provably `pending()`'s own doing, not incidental insertion order.
    for question, raised_at in (("second", later), ("first", earlier)):
        store.insert(
            job_id=job.id,
            entry_seq=1,
            cause=EscalationCause.EVIDENCE_GAP,
            subject=SUBJECT,
            question=question,
            context={},
            head_sha=job.head_sha,
            snapshot_hash=job.snapshot_hash,
            raised_at=raised_at,
        )

    listed = pending(store=store)
    assert [escalation.question for escalation in listed] == ["first", "second"]
