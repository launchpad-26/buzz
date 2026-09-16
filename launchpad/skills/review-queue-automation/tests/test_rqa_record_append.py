#!/usr/bin/env python3
"""`append` — E-13, `code/P-12-record.md` §3.1 and §8 rows T4, T5, T11, T14, T15,
T16 (its append and verify halves), T21.

No pytest: every `test_*` function here takes no arguments, per `tests/run_all.py`.

Every test drives a real SQLite connection — in memory, or a temp file where a second
connection has to read what the first one did. ADR-0066 removed the credential-store
dependency, so none of these paths reads an OS keychain (§8).
"""

from __future__ import annotations

import pathlib
import sqlite3
import sys
import tempfile
from datetime import datetime, timezone

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

import rqa.record.writer as writer_module  # noqa: E402
from rqa.contracts import ENTRY_KINDS, AppendFailed, Entry  # noqa: E402
from rqa.record import PayloadNotSerializable, UnknownEntryKind, verify  # noqa: E402
from rqa.record.writer import SQLiteRecordWriter  # noqa: E402

def fixed_clock(moment: datetime = datetime(2026, 9, 12, 8, 30, 15, 123456, tzinfo=timezone.utc)):
    return lambda: moment


def memory_writer(**kwargs) -> tuple[sqlite3.Connection, SQLiteRecordWriter, None]:
    """ADR-0066: there is no key store, so the third element is always `None`. It is
    kept so the many `connection, writer, _ = memory_writer()` call sites read the
    same as before."""
    connection = sqlite3.connect(":memory:")
    return connection, SQLiteRecordWriter(connection, **kwargs), None


def rows(connection: sqlite3.Connection, job: str) -> list[tuple]:
    cursor = connection.execute(
        "SELECT seq, kind, at, payload, prev_hash, hash, hmac, keyed FROM record_entries "
        "WHERE job = ? ORDER BY seq",
        (job,),
    )
    return [tuple(row) for row in cursor.fetchall()]


# -- the shape E-13 fixes ------------------------------------------------------


def test_append_is_the_positional_signature_contracts_declares() -> None:
    """`CONTRACTS.md` §7 states `append(self, job_id, kind, payload)` positionally, and
    the keyword-only preamble convention does not override a signature the seam states
    positionally. The implementation matches the Protocol character-for-character."""
    import inspect

    from rqa.contracts import RecordWriter

    declared = inspect.signature(RecordWriter.append)
    implemented = inspect.signature(SQLiteRecordWriter.append)
    assert [p.name for p in implemented.parameters.values()] == [
        p.name for p in declared.parameters.values()
    ]
    assert [p.kind for p in implemented.parameters.values()] == [
        p.kind for p in declared.parameters.values()
    ]


def test_the_writers_dependencies_are_constructor_only() -> None:
    """§3.1: `connection` and `clock` are constructor-only; they are not
    E-13 parameters, so no caller can vary them per call."""
    import inspect

    parameters = inspect.signature(SQLiteRecordWriter.__init__).parameters
    assert list(parameters) == ["self", "connection", "clock"]
    assert parameters["clock"].kind is inspect.Parameter.KEYWORD_ONLY
    assert set(inspect.signature(SQLiteRecordWriter.append).parameters) == {
        "self",
        "job_id",
        "kind",
        "payload",
    }


# -- §3.1 steps 1 and 2: the two programming errors ---------------------------


def test_t14_an_unknown_kind_raises_and_writes_nothing() -> None:
    """T14: `append(job, "not_a_real_kind", {})` raises `UnknownEntryKind`;
    `record_entries` for that job is unchanged (zero new rows)."""
    connection, writer, _keystore = memory_writer()
    writer.append("job-1", "transition", {"to_state": "queued"})
    before = rows(connection, "job-1")

    raised = False
    try:
        writer.append("job-1", "not_a_real_kind", {})
    except UnknownEntryKind:
        raised = True
    assert raised, "an unknown kind must raise UnknownEntryKind"
    assert rows(connection, "job-1") == before
    # Step 1 runs before anything is read or written: the key store is untouched too.


def test_a_string_subclass_carrying_a_members_text_is_not_a_kind() -> None:
    """§1: this package never accepts another part's enum. A `str` subclass whose text
    matches a member would otherwise be stored as a kind nobody can reproduce."""
    from enum import Enum

    class OtherPartsKind(str, Enum):
        TRANSITION = "transition"

    _connection, writer, _keystore = memory_writer()
    raised = False
    try:
        writer.append("job-1", OtherPartsKind.TRANSITION, {})
    except UnknownEntryKind:
        raised = True
    assert raised


def test_t15_a_raw_datetime_payload_raises_and_writes_nothing() -> None:
    """T15: `append(job, "spend", {"at": datetime.now()})` raises
    `PayloadNotSerializable`; zero new rows."""
    connection, writer, _keystore = memory_writer()
    raised = False
    try:
        writer.append("job-1", "spend", {"at": datetime.now(timezone.utc)})
    except PayloadNotSerializable:
        raised = True
    assert raised, "a raw datetime is not JSON-safe data"
    assert rows(connection, "job-1") == []


def test_a_payload_holding_another_parts_dataclass_is_refused() -> None:
    """§2: "no Enum, no dataclass, no other part's type"."""
    from rqa.contracts import Entry as SharedEntry

    connection, writer, _keystore = memory_writer()
    raised = False
    try:
        writer.append("job-1", "plan", {"entry": SharedEntry(seq=1, hash="a" * 64)})
    except PayloadNotSerializable:
        raised = True
    assert raised
    assert rows(connection, "job-1") == []


def test_t21_every_one_of_the_fourteen_kinds_is_accepted_and_a_fifteenth_is_not() -> None:
    """T21: append one minimal JSON-safe payload for each member of `ENTRY_KINDS`; all
    fourteen are accepted; any fifteenth string raises `UnknownEntryKind`."""
    connection, writer, _keystore = memory_writer()
    assert len(ENTRY_KINDS) == 14
    for kind in sorted(ENTRY_KINDS):
        entry = writer.append("job-1", kind, {"minimal": True})
        assert isinstance(entry, Entry)
    stored = rows(connection, "job-1")
    assert [row[1] for row in stored] == sorted(ENTRY_KINDS)
    assert [row[0] for row in stored] == list(range(1, 15))

    raised = False
    try:
        writer.append("job-1", "fifteenth", {})
    except UnknownEntryKind:
        raised = True
    assert raised


# -- §3.1 steps 3 and 4: sequence, chain and time ------------------------------


def test_the_first_entry_is_seq_one_with_a_null_parent_and_each_next_chains() -> None:
    """§3.1 step 3: no head → `seq=1`, `prev_hash` NULL; found → `seq+1` and the
    found row's hash as the parent."""
    connection, writer, _keystore = memory_writer()
    writer.append("job-1", "transition", {"to_state": "queued"})
    writer.append("job-1", "plan", {"obligations": ["o1"]})
    writer.append("job-1", "judgement", {"disposition": "approve"})

    stored = rows(connection, "job-1")
    assert [row[0] for row in stored] == [1, 2, 3]
    assert stored[0][4] is None
    assert stored[1][4] == stored[0][5]
    assert stored[2][4] == stored[1][5]


def test_two_jobs_keep_independent_chains() -> None:
    connection, writer, _keystore = memory_writer()
    writer.append("job-1", "transition", {"to_state": "queued"})
    writer.append("job-2", "transition", {"to_state": "queued"})
    assert rows(connection, "job-2")[0][0] == 1
    assert rows(connection, "job-2")[0][4] is None


def test_the_timestamp_is_utc_iso_8601_with_microseconds() -> None:
    """§3.1 step 4."""
    connection, writer, _keystore = memory_writer(clock=fixed_clock())
    writer.append("job-1", "transition", {"to_state": "queued"})
    assert rows(connection, "job-1")[0][2] == "2026-09-12T08:30:15.123456+00:00"


def test_a_naive_clock_reading_is_taken_as_utc_not_as_local_time() -> None:
    connection, writer, _keystore = memory_writer(
        clock=fixed_clock(datetime(2026, 9, 12, 8, 30, 15, 123456))
    )
    writer.append("job-1", "transition", {"to_state": "queued"})
    assert rows(connection, "job-1")[0][2] == "2026-09-12T08:30:15.123456+00:00"


def test_append_is_deterministic_for_identical_hashed_inputs() -> None:
    """§3.1's guarantee. Two separate databases, the same clock, the same key: the
    same hash, because nothing incidental enters the formula."""
    first = memory_writer(clock=fixed_clock())
    second = memory_writer(clock=fixed_clock())
    payload_a = {"b": 1, "a": [1, 2], "c": {"d": None}}
    payload_b = {"c": {"d": None}, "a": (1, 2), "b": 1}
    assert first[1].append("job-1", "plan", payload_a) == second[1].append(
        "job-1", "plan", payload_b
    )


# -- §3.1 step 5: ADR-0066 retired the operator key ---------------------------


def test_every_append_is_unkeyed_and_no_credential_store_is_consulted() -> None:
    """ADR-0066: step 5 reads no key, so every row is written `keyed=0, hmac=NULL`.

    This is also #2272's resolution in its final form: there is no platform
    credential command left to be absent, so an append cannot fail for a key reason
    on macOS, Linux, Windows, a container, or CI.
    """
    connection, writer, _ = memory_writer()
    entry = writer.append("job-1", "transition", {"to_state": "queued"})
    assert isinstance(entry, Entry)

    stored = rows(connection, "job-1")[0]
    assert stored[6] is None, "hmac must be NULL"
    assert stored[7] == 0, "keyed must be stored as 0, never inferred"

    result = verify(connection, "job-1")
    assert result.ok is True
    assert result.bad_seq is None and result.kind is None


def test_the_writer_takes_no_key_store_and_has_no_credential_failure_mode() -> None:
    """The constructor parameter is gone, not merely defaulted, and `append` no
    longer has a branch that can raise `AppendFailed` for a credential reason."""
    import inspect

    parameters = inspect.signature(SQLiteRecordWriter.__init__).parameters
    assert "keystore" not in parameters
    assert list(parameters) == ["self", "connection", "clock"]

    source = pathlib.Path(
        pathlib.Path(__file__).resolve().parent.parent / "rqa" / "record" / "writer.py"
    ).read_text(encoding="utf-8")
    for forbidden in ("keychain", "KeyStore", "compute_hmac", "security", "secret-tool"):
        assert forbidden not in source, f"{forbidden!r} survives in writer.py"


# -- §3.1 steps 6 and 7: the row, the head, and the caller's transaction -------


def test_t11_three_appends_leave_one_head_row_and_per_row_keyed_state() -> None:
    """T11: three successive appends → `record_heads` holds exactly one latest
    `(seq, hash, hmac=NULL, keyed=0)` row, and every `record_entries` row carries the
    same unkeyed state. Under ADR-0066 that state is uniform rather than per-row."""
    connection, writer, _ = memory_writer()
    writer.append("job-1", "transition", {"to_state": "queued"})
    writer.append("job-1", "plan", {"obligations": ["o1"]})
    writer.append("job-1", "transition", {"to_state": "stopped"})

    heads = connection.execute(
        "SELECT job, seq, hash, hmac, keyed FROM record_heads"
    ).fetchall()
    assert len(heads) == 1, "one head per job, upserted rather than appended"
    job, seq, head_hash, head_hmac, head_keyed = heads[0]
    stored = rows(connection, "job-1")
    assert (job, seq, head_hash, head_hmac, head_keyed) == ("job-1", 3, stored[2][5], None, 0)

    assert [row[7] for row in stored] == [0, 0, 0]
    assert [row[6] is None for row in stored] == [True, True, True]


def test_t4_an_uncommitted_append_disappears_when_the_caller_rolls_back() -> None:
    """T4: a connection with an open transaction: `append` succeeds (uncommitted), then
    the caller's own next statement fails and the caller rolls back → a fresh read of
    `record_entries` for that job returns zero rows.

    This is E-13's whole point: the entry and the state change it records are one
    caller-controlled transaction (`components.md` §4, P-02).
    """
    with tempfile.TemporaryDirectory() as directory:
        path = str(pathlib.Path(directory) / "state.db")
        connection = sqlite3.connect(path)
        connection.execute("CREATE TABLE jobs (id TEXT PRIMARY KEY)")
        writer = SQLiteRecordWriter(connection)

        connection.execute("INSERT INTO jobs (id) VALUES ('job-1')")  # opens the transaction
        entry = writer.append("job-1", "transition", {"to_state": "queued"})
        assert entry.seq == 1
        assert rows(connection, "job-1"), "the row is visible inside the transaction"

        failed = False
        try:
            connection.execute("INSERT INTO jobs (id) VALUES ('job-1')")  # the caller's own failure
        except sqlite3.IntegrityError:
            failed = True
            connection.rollback()
        assert failed

        assert rows(connection, "job-1") == []
        fresh = sqlite3.connect(path)
        try:
            assert rows(fresh, "job-1") == []
            assert fresh.execute("SELECT COUNT(*) FROM record_heads").fetchone()[0] == 0
        finally:
            fresh.close()
        connection.close()


def test_append_never_commits_the_callers_transaction() -> None:
    """§3.1: "`append` never calls `connection.commit()` or `connection.rollback()`
    itself." A writer that committed would make a failed transition authoritative."""
    calls: list[str] = []

    class WatchedConnection(sqlite3.Connection):
        def commit(self):
            calls.append("commit")
            super().commit()

        def rollback(self):
            calls.append("rollback")
            super().rollback()

    connection = sqlite3.connect(":memory:", factory=WatchedConnection)
    writer = SQLiteRecordWriter(connection)
    writer.append("job-1", "transition", {"to_state": "queued"})
    assert calls == []


def test_t5_a_failing_insert_propagates_append_failed_to_the_callers_own_call_site() -> None:
    """T5: `append`'s `INSERT` raises `sqlite3.OperationalError` (monkeypatched) →
    `AppendFailed` is observed propagating out of the call at the test's own call site —
    nothing inside `rqa.record` caught it.

    §7 states that as a prohibition, and U-DISPATCH-20 records the estate defect it
    replaces: `except Exception: pass` around a ledger write let a review complete
    authoritatively with a knowingly incomplete record.
    """
    connection, writer, _keystore = memory_writer()
    original = writer_module.insert_entry

    def exploding_insert(**kwargs):
        raise sqlite3.OperationalError("database is locked")

    writer_module.insert_entry = exploding_insert
    try:
        observed = None
        try:
            writer.append("job-1", "transition", {"to_state": "queued"})
        except AppendFailed as exc:  # the test's own call site
            observed = exc
        assert observed is not None, "AppendFailed must reach the caller"
        assert isinstance(observed.__cause__, sqlite3.OperationalError)
    finally:
        writer_module.insert_entry = original
    assert rows(connection, "job-1") == []


def test_a_failing_head_upsert_is_also_append_failed() -> None:
    """§3.1 step 7: the head write is inside the same caller transaction, so its
    failure is the same all-or-nothing outcome — the caller rolls back both."""
    connection, writer, _keystore = memory_writer()
    original = writer_module.upsert_head

    def exploding_upsert(**kwargs):
        raise sqlite3.OperationalError("disk I/O error")

    writer_module.upsert_head = exploding_upsert
    try:
        raised = False
        try:
            writer.append("job-1", "transition", {"to_state": "queued"})
        except AppendFailed:
            raised = True
        assert raised
    finally:
        writer_module.upsert_head = original


def test_a_failing_head_read_is_append_failed_rather_than_a_new_chain() -> None:
    """A store read that fails must not be mistaken for "this job has no entries yet":
    that would silently restart the chain at seq 1 with a NULL parent."""
    connection, writer, _keystore = memory_writer()
    original = writer_module.head_entry

    def exploding_read(**kwargs):
        raise sqlite3.OperationalError("no such table: record_entries")

    writer_module.head_entry = exploding_read
    try:
        raised = False
        try:
            writer.append("job-1", "transition", {"to_state": "queued"})
        except AppendFailed:
            raised = True
        assert raised
    finally:
        writer_module.head_entry = original
    assert rows(connection, "job-1") == []


def test_a_live_chain_ignores_migrated_rows_when_it_reads_its_head() -> None:
    """§3.1 step 3 reads the highest-`seq` *non-legacy* row, and §6 marks every
    migrated row with `prev_hash="legacy"` — so a migrated segment never becomes the
    parent of a live entry."""
    from rqa.record.hashing import LEGACY_PREV_HASH
    from rqa.record.store import StoredEntry, insert_entry

    connection, writer, _keystore = memory_writer()
    insert_entry(
        connection=connection,
        entry=StoredEntry(
            job="job-1",
            seq=90,
            kind="legacy",
            at="2025-01-01T00:00:00.000000+00:00",
            payload='{"source_table":"ledger_entries"}',
            prev_hash=LEGACY_PREV_HASH,
            hash="f" * 64,
            hmac=None,
            keyed=False,
        ),
    )
    entry = writer.append("job-1", "transition", {"to_state": "queued"})
    assert entry.seq == 1
    assert rows(connection, "job-1")[0][4] is None
