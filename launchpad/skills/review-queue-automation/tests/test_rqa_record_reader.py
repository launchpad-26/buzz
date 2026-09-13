#!/usr/bin/env python3
"""`SQLiteRecordReader` — `code/P-12-record.md` §2 and §5's read protocol.

No pytest: every `test_*` function here takes no arguments, per `tests/run_all.py`.

The distinction these tests exist for: `entries` and `latest` return what is stored and
claim nothing about it, while `trusted_prefix` is the one method that makes a trust
claim. §2: "Operational consumers such as P-13 must use this method rather than treating
`latest()` as authenticated."
"""

from __future__ import annotations

import json
import pathlib
import sqlite3
import sys
from datetime import datetime, timezone

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from rqa.contracts import (  # noqa: E402
    RecordReader,
    RecordRow,
    RecordTrustFailureReason,
    RecordUntrusted,
    VerifiedRecordPrefix,
)
from rqa.record.hashing import LEGACY_PREV_HASH  # noqa: E402
from rqa.record.reader import SQLiteRecordReader  # noqa: E402
from rqa.record.store import StoredEntry, insert_entry  # noqa: E402
from rqa.record.writer import SQLiteRecordWriter  # noqa: E402

KEY = b"a-test-key-that-never-leaves-this-process"


class FakeKeyStore:
    def __init__(self, *, key: bytes | None = KEY):
        self.key = key

    def read(self, name: str) -> bytes | None:
        return self.key


def populated(*, key: bytes | None = KEY):
    keystore = FakeKeyStore(key=key)
    connection = sqlite3.connect(":memory:")
    writer = SQLiteRecordWriter(connection, keystore=keystore)
    writer.append("job-1", "transition", {"to_state": "queued", "repo": "o/r", "number": 7})
    writer.append("job-1", "plan", {"obligations": ["o1"], "policy_version": "1.2.0"})
    writer.append("job-1", "judgement", {"disposition": "approve"})
    writer.append("job-1", "transition", {"to_state": "approved", "repo": "o/r", "number": 7})
    return connection, SQLiteRecordReader(connection, keystore=keystore)


def test_the_reader_implements_the_protocol_signatures_contracts_declares() -> None:
    import inspect

    for name in ("entries", "latest", "trusted_prefix"):
        declared = inspect.signature(getattr(RecordReader, name))
        implemented = inspect.signature(getattr(SQLiteRecordReader, name))
        assert [(p.name, p.kind, p.default) for p in implemented.parameters.values()] == [
            (p.name, p.kind, p.default) for p in declared.parameters.values()
        ], name


def test_entries_returns_every_row_in_sequence_order() -> None:
    _connection, reader = populated()
    rows = reader.entries("job-1")
    assert [row.seq for row in rows] == [1, 2, 3, 4]
    assert [row.kind for row in rows] == ["transition", "plan", "judgement", "transition"]
    assert all(isinstance(row, RecordRow) for row in rows)
    assert rows[1].payload == {"obligations": ["o1"], "policy_version": "1.2.0"}
    assert isinstance(rows[0].at, datetime)
    assert rows[0].at.tzinfo is not None


def test_entries_filters_by_kind_when_one_is_given() -> None:
    _connection, reader = populated()
    assert [row.seq for row in reader.entries("job-1", "transition")] == [1, 4]
    assert reader.entries("job-1", "escalation") == ()
    assert reader.entries("no-such-job") == ()


def test_latest_returns_the_greatest_sequence_of_a_kind_or_none() -> None:
    _connection, reader = populated()
    latest = reader.latest("job-1", "transition")
    assert latest is not None and latest.seq == 4
    assert latest.payload["to_state"] == "approved"
    assert reader.latest("job-1", "escalation") is None
    assert reader.latest("no-such-job", "transition") is None


def test_a_verified_history_returns_a_prefix_whose_latest_searches_only_its_own_rows() -> None:
    """§2: "its `latest(kind)` searches only its immutable `rows`"."""
    _connection, reader = populated()
    prefix = reader.trusted_prefix("job-1")
    assert isinstance(prefix, VerifiedRecordPrefix)
    assert prefix.job_id == "job-1"
    assert [row.seq for row in prefix.rows] == [1, 2, 3, 4]
    assert prefix.checked_through_seq == 4
    assert prefix.latest("judgement").seq == 3
    assert prefix.latest("escalation") is None


def test_no_rows_is_missing() -> None:
    _connection, reader = populated()
    untrusted = reader.trusted_prefix("no-such-job")
    assert isinstance(untrusted, RecordUntrusted)
    assert untrusted.reason is RecordTrustFailureReason.MISSING


def test_a_tampered_row_is_an_integrity_break_naming_where_it_stopped() -> None:
    connection, reader = populated()
    connection.execute(
        "UPDATE record_entries SET payload = ? WHERE job = ? AND seq = ?",
        (json.dumps({"disposition": "merge"}), "job-1", 3),
    )
    untrusted = reader.trusted_prefix("job-1")
    assert isinstance(untrusted, RecordUntrusted)
    assert untrusted.reason is RecordTrustFailureReason.INTEGRITY_BREAK
    assert "3" in untrusted.detail


def test_an_unkeyed_history_is_unverifiable_rather_than_trusted_or_broken() -> None:
    """The ADR-0063 middle ground: the record reads fine, and it is honestly not
    authenticated. `trusted_prefix` refuses to call that verified, and refuses to call
    it tampered."""
    _connection, reader = populated(key=None)
    untrusted = reader.trusted_prefix("job-1")
    assert isinstance(untrusted, RecordUntrusted)
    assert untrusted.reason is RecordTrustFailureReason.UNVERIFIABLE
    assert "no key" in untrusted.detail


def test_a_migrated_row_makes_the_history_legacy_even_when_it_verifies() -> None:
    """§6: a migrated row is "never `verified=True` from `explain`, regardless of how
    well-formed its content is". The same rule holds for the prefix a reader will
    vouch for."""
    connection, reader = populated()
    insert_entry(
        connection=connection,
        entry=StoredEntry(
            job="job-1",
            seq=90,
            kind="decision",
            at="2025-01-01T00:00:00.000000+00:00",
            payload=json.dumps({"actor": "unknown", "basis": "migrated"}),
            prev_hash=LEGACY_PREV_HASH,
            hash="c" * 64,
            hmac=None,
            keyed=False,
        ),
    )
    untrusted = reader.trusted_prefix("job-1")
    assert isinstance(untrusted, RecordUntrusted)
    assert untrusted.reason is RecordTrustFailureReason.LEGACY
    assert "90" in untrusted.detail


def test_a_basic_read_makes_no_trust_claim_about_a_tampered_row() -> None:
    """The reason `trusted_prefix` exists: `latest` still answers here, and answering is
    not vouching. A consumer that needs authentication must ask for it."""
    connection, reader = populated()
    connection.execute(
        "UPDATE record_entries SET payload = ? WHERE job = ? AND seq = ?",
        (json.dumps({"disposition": "merge"}), "job-1", 3),
    )
    latest = reader.latest("job-1", "judgement")
    assert latest is not None and latest.payload == {"disposition": "merge"}
    assert isinstance(reader.trusted_prefix("job-1"), RecordUntrusted)


def test_reading_mutates_nothing() -> None:
    connection, reader = populated()
    before = connection.execute("SELECT * FROM record_entries ORDER BY seq").fetchall()
    reader.entries("job-1")
    reader.latest("job-1", "plan")
    reader.trusted_prefix("job-1")
    assert connection.execute("SELECT * FROM record_entries ORDER BY seq").fetchall() == before


def test_a_row_stored_with_an_unparseable_payload_is_a_corrupt_store_not_an_empty_row() -> None:
    """A reader that smoothed a corrupt payload into `{}` would hand a caller a record
    entry that never existed."""
    connection, reader = populated()
    connection.execute(
        "UPDATE record_entries SET payload = ? WHERE job = ? AND seq = ?",
        ("{not json", "job-1", 2),
    )
    raised = False
    try:
        reader.entries("job-1")
    except ValueError:
        raised = True
    assert raised


def test_the_stored_timestamp_round_trips_to_an_aware_utc_datetime() -> None:
    keystore = FakeKeyStore()
    connection = sqlite3.connect(":memory:")
    moment = datetime(2026, 9, 12, 8, 30, 15, 123456, tzinfo=timezone.utc)
    writer = SQLiteRecordWriter(connection, clock=lambda: moment, keystore=keystore)
    writer.append("job-1", "transition", {"to_state": "queued"})
    reader = SQLiteRecordReader(connection, keystore=keystore)
    assert reader.entries("job-1")[0].at == moment
