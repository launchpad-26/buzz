#!/usr/bin/env python3
"""The `human_requests` table — `code/P-11-escalation.md` §5.

No pytest: every `test_*` function takes no arguments, per `tests/run_all.py`.
"""

from __future__ import annotations

import pathlib
import sqlite3
import sys
from datetime import datetime, timezone

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from rqa.contracts import EscalationCause, EscalationSubject, EscalationSubjectKind  # noqa: E402
from rqa.escalation.store import SqliteEscalationStore, ensure_schema  # noqa: E402

JOB = "job-1"
RAISED_AT = datetime(2026, 9, 12, 8, 30, 15, tzinfo=timezone.utc)
CLOSED_AT = datetime(2026, 9, 12, 9, 0, 0, tzinfo=timezone.utc)
SUBJECT = EscalationSubject(EscalationSubjectKind.OBLIGATION, "OBL-1")


def connected() -> sqlite3.Connection:
    return sqlite3.connect(":memory:")


def test_the_schema_is_section_fives_fourteen_columns_and_nothing_else() -> None:
    connection = connected()
    ensure_schema(connection=connection)
    columns = [row[1] for row in connection.execute("PRAGMA table_info(human_requests)")]
    assert columns == [
        "id", "job_id", "entry_seq", "cause", "subject_kind", "subject_id",
        "question", "context", "head_sha",
        "snapshot_hash", "raised_at", "status", "closed_at", "decision_entry_seq",
    ]


def test_no_column_is_a_decision_actor_rationale_or_transport_column() -> None:
    """§5: those migrate onto the `decision` record entry; the transport columns have
    no successor at all (U-AUTHORITY-12, bin)."""
    connection = connected()
    ensure_schema(connection=connection)
    columns = {row[1] for row in connection.execute("PRAGMA table_info(human_requests)")}
    for forbidden in ("decision_actor", "rationale", "transport", "delivered_at"):
        assert forbidden not in columns, columns


def test_ensuring_the_schema_twice_is_a_no_op() -> None:
    connection = connected()
    ensure_schema(connection=connection)
    ensure_schema(connection=connection)
    assert connection.execute("SELECT count(*) FROM human_requests").fetchone()[0] == 0


def test_a_row_round_trips_field_for_field() -> None:
    store = SqliteEscalationStore(connected())
    row_id = store.insert(
        job_id=JOB,
        entry_seq=3,
        cause=EscalationCause.EVIDENCE_GAP,
        subject=SUBJECT,
        question="which obligation is unmet?",
        context={"obligation": "OBL-1"},
        head_sha="a" * 40,
        snapshot_hash="sha256:snap-1",
        raised_at=RAISED_AT,
    )
    row = store.get(row_id)
    assert row.id == row_id
    assert row.job_id == JOB
    assert row.entry_seq == 3
    assert row.cause is EscalationCause.EVIDENCE_GAP
    assert row.subject == SUBJECT
    assert row.question == "which obligation is unmet?"
    assert dict(row.context) == {"obligation": "OBL-1"}
    assert row.head_sha == "a" * 40
    assert row.snapshot_hash == "sha256:snap-1"
    assert row.raised_at == RAISED_AT
    assert row.status == "open"
    assert row.closed_at is None
    assert row.decision_entry_seq is None


def test_e_b5_1_a_null_snapshot_hash_inserts_and_round_trips_as_none() -> None:
    """`CONTRACTS.md` §1: `Job.snapshot_hash: str | None` — a job escalated before P-03
    ever returned a real `Snapshot` (P-02's `ValidationFailure` branch of step 3) has no
    snapshot to pin. `snapshot_hash` is nullable here for exactly that job; `part
    P-11-escalation.md` §2/§5's non-nullable narrowing was the defect (ruling E-B5-1),
    not this column."""
    store = SqliteEscalationStore(connected())
    row_id = store.insert(
        job_id=JOB, entry_seq=1, cause=EscalationCause.AUTHORITY_REQUIREMENT, subject=SUBJECT,
        question="policy failed to validate; may a human proceed?", context={},
        head_sha="a" * 40, snapshot_hash=None, raised_at=RAISED_AT,
    )
    row = store.get(row_id)
    assert row.snapshot_hash is None
    [pending_row] = store.pending()
    assert pending_row.snapshot_hash is None


def test_an_absent_id_is_none_not_an_empty_row() -> None:
    store = SqliteEscalationStore(connected())
    assert store.get(999) is None


def test_pending_lists_only_open_rows_oldest_first() -> None:
    from datetime import timedelta

    store = SqliteEscalationStore(connected())
    later = store.insert(
        job_id=JOB, entry_seq=1, cause=EscalationCause.EVIDENCE_GAP, subject=SUBJECT, question="second",
        context={}, head_sha="a" * 40, snapshot_hash="s", raised_at=RAISED_AT + timedelta(hours=1),
    )
    earlier = store.insert(
        job_id=JOB, entry_seq=2, cause=EscalationCause.EVIDENCE_GAP, subject=SUBJECT, question="first",
        context={}, head_sha="a" * 40, snapshot_hash="s", raised_at=RAISED_AT,
    )
    already_closed = store.insert(
        job_id=JOB, entry_seq=3, cause=EscalationCause.EVIDENCE_GAP, subject=SUBJECT, question="closed one",
        context={}, head_sha="a" * 40, snapshot_hash="s", raised_at=RAISED_AT - timedelta(hours=1),
    )
    store.close(already_closed, decision_entry_seq=9, closed_at=CLOSED_AT)

    pending = store.pending()
    assert [row.id for row in pending] == [earlier, later]


def test_close_sets_status_closed_at_and_decision_entry_seq() -> None:
    store = SqliteEscalationStore(connected())
    row_id = store.insert(
        job_id=JOB, entry_seq=1, cause=EscalationCause.AUTHORITY_REQUIREMENT, subject=SUBJECT, question="q",
        context={}, head_sha="a" * 40, snapshot_hash="s", raised_at=RAISED_AT,
    )
    store.close(row_id, decision_entry_seq=42, closed_at=CLOSED_AT)
    row = store.get(row_id)
    assert row.status == "closed"
    assert row.closed_at == CLOSED_AT
    assert row.decision_entry_seq == 42
    assert row not in store.pending()


def test_the_unique_constraint_is_job_id_and_entry_seq() -> None:
    store = SqliteEscalationStore(connected())
    store.insert(
        job_id=JOB, entry_seq=1, cause=EscalationCause.EVIDENCE_GAP, subject=SUBJECT, question="q",
        context={}, head_sha="a" * 40, snapshot_hash="s", raised_at=RAISED_AT,
    )
    try:
        store.insert(
            job_id=JOB, entry_seq=1, cause=EscalationCause.EVIDENCE_GAP, subject=SUBJECT, question="q2",
            context={}, head_sha="a" * 40, snapshot_hash="s", raised_at=RAISED_AT,
        )
    except sqlite3.IntegrityError:
        pass
    else:
        raise AssertionError("a duplicate (job_id, entry_seq) must violate the UNIQUE constraint")


def test_a_naive_timestamp_is_read_back_as_utc() -> None:
    store = SqliteEscalationStore(connected())
    naive = datetime(2026, 9, 12, 8, 30, 15)  # no tzinfo
    row_id = store.insert(
        job_id=JOB, entry_seq=1, cause=EscalationCause.EVIDENCE_GAP, subject=SUBJECT, question="q",
        context={}, head_sha="a" * 40, snapshot_hash="s", raised_at=naive,
    )
    read = store.get(row_id)
    assert read.raised_at == naive.replace(tzinfo=timezone.utc)


def test_the_context_mapping_round_trips_through_json() -> None:
    store = SqliteEscalationStore(connected())
    row_id = store.insert(
        job_id=JOB, entry_seq=1, cause=EscalationCause.REQUIRED_INFORMATION, subject=SUBJECT, question="q",
        context={"obligation": "OBL-2", "note": "needs a second reviewer"},
        head_sha="a" * 40, snapshot_hash="s", raised_at=RAISED_AT,
    )
    row = store.get(row_id)
    assert dict(row.context) == {"obligation": "OBL-2", "note": "needs a second reviewer"}


def test_the_store_never_commits_so_the_row_lands_with_its_record_entry() -> None:
    """Mirrors `test_rqa_authority_store.py`'s equivalent: the row and the `escalation`
    record entry it indexes are written on the caller's own connection and must commit
    or roll back together, never independently."""
    path = pathlib.Path("/tmp/rqa-escalation-store-commit-test.db")
    path.unlink(missing_ok=True)
    try:
        connection = sqlite3.connect(str(path))
        store = SqliteEscalationStore(connection)
        store.insert(
            job_id=JOB, entry_seq=1, cause=EscalationCause.EVIDENCE_GAP, subject=SUBJECT, question="q",
            context={}, head_sha="a" * 40, snapshot_hash="s", raised_at=RAISED_AT,
        )
        connection.close()

        reopened = sqlite3.connect(str(path))
        ensure_schema(connection=reopened)
        assert reopened.execute("SELECT count(*) FROM human_requests").fetchone()[0] == 0
    finally:
        path.unlink(missing_ok=True)


def test_the_protocol_methods_are_section_fives_four() -> None:
    import inspect

    from rqa.escalation.store import EscalationStore

    assert list(inspect.signature(EscalationStore.insert).parameters)[0] == "self"
    assert list(inspect.signature(EscalationStore.get).parameters) == ["self", "escalation_id"]
    assert list(inspect.signature(EscalationStore.pending).parameters) == ["self"]
    assert list(inspect.signature(EscalationStore.close).parameters) == [
        "self", "escalation_id", "decision_entry_seq", "closed_at",
    ]
