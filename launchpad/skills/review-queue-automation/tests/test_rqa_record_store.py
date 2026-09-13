#!/usr/bin/env python3
"""The record store — `code/P-12-record.md` §5 and §8's closing property.

No pytest: every `test_*` function here takes no arguments, per `tests/run_all.py`.

These tests drive the real primitives against a real SQLite connection, because the
properties under test are the ones a fake cannot have: the §5 DDL's own CHECK
constraints, the `(job, seq)` uniqueness the chain depends on, and the ordered reads
`append`, `verify` and every reader are defined in terms of.
"""

from __future__ import annotations

import json
import pathlib
import sqlite3
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from rqa.record.hashing import LEGACY_PREV_HASH  # noqa: E402
from rqa.record.store import (  # noqa: E402
    StoredEntry,
    ensure_schema,
    entries_for_job,
    entries_of_kind,
    head_entry,
    head_row,
    insert_entry,
    is_legacy,
    latest_of_kind,
    record_row,
    rows_of_kind_across_jobs,
    upsert_head,
)


def connected() -> sqlite3.Connection:
    connection = sqlite3.connect(":memory:")
    ensure_schema(connection=connection)
    return connection


def entry(
    *,
    job: str = "job-1",
    seq: int = 1,
    kind: str = "transition",
    payload: dict | None = None,
    prev_hash: str | None = None,
    hash: str | None = None,
    hmac: str | None = None,
    keyed: bool = False,
    at: str = "2026-09-12T08:30:15.123456+00:00",
) -> StoredEntry:
    return StoredEntry(
        job=job,
        seq=seq,
        kind=kind,
        at=at,
        payload=json.dumps(payload if payload is not None else {"to_state": "queued"}),
        prev_hash=prev_hash,
        hash=hash or f"{seq:064d}",
        hmac=hmac,
        keyed=keyed,
    )


def test_ensuring_the_schema_twice_is_a_no_op() -> None:
    connection = connected()
    ensure_schema(connection=connection)
    tables = {
        row[0]
        for row in connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table'"
        ).fetchall()
    }
    assert {"record_entries", "record_heads"} <= tables
    indexes = {
        row[0]
        for row in connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'index'"
        ).fetchall()
    }
    assert {"record_entries_by_job", "record_entries_by_kind"} <= indexes


def test_the_keyed_bit_and_the_hmac_cannot_disagree() -> None:
    """§5's CHECK: `hmac` is NULL exactly when `keyed = 0`. A row claiming to be keyed
    with no HMAC, or unkeyed with one, is not storable — which is what lets `verify`
    read the pair as one fact."""
    connection = connected()
    for broken in (
        entry(keyed=True, hmac=None),
        entry(keyed=False, hmac="a" * 64),
    ):
        raised = False
        try:
            insert_entry(connection=connection, entry=broken)
        except sqlite3.IntegrityError:
            raised = True
        assert raised


def test_a_sequence_cannot_be_written_twice_for_one_job() -> None:
    """§5's `UNIQUE (job, seq)`: two rows at one sequence would make "the entry at
    seq n" ambiguous, and the chain is defined by sequence."""
    connection = connected()
    insert_entry(connection=connection, entry=entry(seq=1))
    raised = False
    try:
        insert_entry(connection=connection, entry=entry(seq=1, kind="plan"))
    except sqlite3.IntegrityError:
        raised = True
    assert raised
    insert_entry(connection=connection, entry=entry(job="job-2", seq=1))


def test_reads_are_ordered_by_sequence_and_scoped_to_their_job() -> None:
    connection = connected()
    for seq, kind in ((3, "plan"), (1, "transition"), (2, "transition")):
        insert_entry(connection=connection, entry=entry(seq=seq, kind=kind))
    insert_entry(connection=connection, entry=entry(job="job-2", seq=1, kind="plan"))

    assert [row.seq for row in entries_for_job(connection=connection, job="job-1")] == [1, 2, 3]
    assert [
        row.seq for row in entries_of_kind(connection=connection, job="job-1", kind="transition")
    ] == [1, 2]
    latest = latest_of_kind(connection=connection, job="job-1", kind="transition")
    assert latest is not None and latest.seq == 2
    assert latest_of_kind(connection=connection, job="job-1", kind="grant") is None


def test_the_head_read_ignores_migrated_rows() -> None:
    """§3.1 step 3 reads the highest-`seq` *non-legacy* row."""
    connection = connected()
    insert_entry(connection=connection, entry=entry(seq=1))
    insert_entry(
        connection=connection,
        entry=entry(seq=2, kind="legacy", prev_hash=LEGACY_PREV_HASH),
    )
    head = head_entry(connection=connection, job="job-1")
    assert head is not None and head.seq == 1
    assert head_entry(connection=connection, job="no-such-job") is None


def test_a_migrated_row_is_the_one_carrying_the_legacy_parent_not_a_kind() -> None:
    """§6: `approval_decisions` and `cost_ledger` migrate into `decision` and `spend`,
    so kind cannot tell a migrated row from a live one."""
    migrated = entry(seq=1, kind="decision", prev_hash=LEGACY_PREV_HASH)
    live = entry(seq=2, kind="decision", prev_hash="a" * 64)
    assert is_legacy(entry=migrated) is True
    assert is_legacy(entry=live) is False
    assert is_legacy(entry=entry(seq=3, prev_hash=None)) is False


def test_the_migration_primitive_writes_a_historical_row_through_this_module() -> None:
    """§6: migrated rows carry a historical `at` and the fixed `"legacy"` parent rather
    than the live clock and a followed chain, so the one-time migration writes through
    these primitives rather than through `RecordWriter`. It still travels through the
    single insert path §8's closing property names."""
    connection = connected()
    insert_entry(
        connection=connection,
        entry=entry(
            job="legacy:approval_decisions:17",
            seq=1,
            kind="decision",
            at="2025-03-04T05:06:07.000000+00:00",
            payload={"actor": "unknown", "basis": "migrated from approval_decisions"},
            prev_hash=LEGACY_PREV_HASH,
        ),
    )
    rows = entries_for_job(connection=connection, job="legacy:approval_decisions:17")
    assert len(rows) == 1
    assert rows[0].prev_hash == "legacy"
    assert record_row(entry=rows[0]).at.year == 2025


def test_the_cross_job_scan_returns_one_kind_everywhere_in_job_then_sequence_order() -> None:
    """§5's read protocol: `resolve_job` scans `transition` rows across the table,
    because `container.md` §5 does not make P-12 a reader of P-01's `jobs` table."""
    connection = connected()
    insert_entry(connection=connection, entry=entry(job="job-b", seq=2))
    insert_entry(connection=connection, entry=entry(job="job-b", seq=1))
    insert_entry(connection=connection, entry=entry(job="job-a", seq=1))
    insert_entry(connection=connection, entry=entry(job="job-a", seq=2, kind="plan"))

    scanned = rows_of_kind_across_jobs(connection=connection, kind="transition")
    assert [(row.job, row.seq) for row in scanned] == [("job-a", 1), ("job-b", 1), ("job-b", 2)]
    assert rows_of_kind_across_jobs(connection=connection, kind="escalation") == ()


def test_the_head_pointer_is_upserted_not_appended() -> None:
    """§3.1 step 7: one head row per job, carrying the same keyed state as the entry
    it names."""
    connection = connected()
    upsert_head(connection=connection, job="job-1", seq=1, hash="a" * 64, hmac="b" * 64, keyed=True)
    upsert_head(connection=connection, job="job-1", seq=2, hash="c" * 64, hmac=None, keyed=False)
    assert connection.execute("SELECT COUNT(*) FROM record_heads").fetchone()[0] == 1
    assert head_row(connection=connection, job="job-1") == (2, "c" * 64, None, False)
    assert head_row(connection=connection, job="job-2") is None


def test_a_stored_row_converts_to_the_shared_record_row_type() -> None:
    connection = connected()
    insert_entry(
        connection=connection, entry=entry(seq=1, kind="plan", payload={"obligations": ["o1"]})
    )
    row = record_row(entry=entries_for_job(connection=connection, job="job-1")[0])
    assert (row.seq, row.kind) == (1, "plan")
    assert row.payload == {"obligations": ["o1"]}
    assert row.at.isoformat(timespec="microseconds") == "2026-09-12T08:30:15.123456+00:00"
