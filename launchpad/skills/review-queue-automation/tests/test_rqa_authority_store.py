#!/usr/bin/env python3
"""The `capabilities` table — `code/P-08-authority-gate.md` §5.

No pytest: every `test_*` function here takes no arguments, per `tests/run_all.py`.

These tests drive the real store against a real SQLite connection, because the
properties under test are the ones a fake cannot have: §5's own DDL, the
`(repo, job_id)` uniqueness the per-job proof depends on, and the replace-on-conflict
behaviour §5 specifies.
"""

from __future__ import annotations

import pathlib
import sqlite3
import sys
from datetime import datetime, timezone

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from rqa.authority.capability import CapabilityProof  # noqa: E402
from rqa.authority.store import SqliteCapabilityStore, ensure_schema  # noqa: E402

REPO = "launchpad-26/buzz"
JOB = "job-1"
PROBED_AT = datetime(2026, 9, 12, 8, 30, 15, tzinfo=timezone.utc)


def connected() -> sqlite3.Connection:
    return sqlite3.connect(":memory:")


def proof(
    *,
    repo: str = REPO,
    job_id: str = JOB,
    capabilities: frozenset[str] = frozenset({"pulls:write", "contents:read"}),
    login: str = "rqa-operator",
    attested: frozenset[str] = frozenset({"admin:org"}),
    probed_at: datetime = PROBED_AT,
) -> CapabilityProof:
    return CapabilityProof(
        id=0,
        repo=repo,
        job_id=job_id,
        capabilities=capabilities,
        login=login,
        probed_at=probed_at,
        attested_not_proven=attested,
    )


def test_the_schema_is_section_fives_seven_columns_and_nothing_else() -> None:
    connection = connected()
    ensure_schema(connection=connection)
    columns = [
        row[1] for row in connection.execute("PRAGMA table_info(capabilities)").fetchall()
    ]
    assert columns == ["id", "repo", "job_id", "capabilities", "attested", "login", "probed_at"]


def test_no_column_holds_a_credential() -> None:
    """§7: P-08 does not store the token, and §5 gives it no column to live in."""
    connection = connected()
    ensure_schema(connection=connection)
    columns = [
        row[1].lower() for row in connection.execute("PRAGMA table_info(capabilities)").fetchall()
    ]
    for forbidden in ("token", "credential", "secret", "password"):
        assert not any(forbidden in column for column in columns), columns


def test_ensuring_the_schema_twice_is_a_no_op() -> None:
    connection = connected()
    ensure_schema(connection=connection)
    ensure_schema(connection=connection)
    assert connection.execute("SELECT count(*) FROM capabilities").fetchone()[0] == 0


def test_a_stored_proof_round_trips_field_for_field() -> None:
    store = SqliteCapabilityStore(connected())
    identifier = store.put(proof())
    read = store.current(REPO, JOB)
    assert read is not None
    assert read.id == identifier
    assert read.repo == REPO
    assert read.job_id == JOB
    assert read.capabilities == frozenset({"pulls:write", "contents:read"})
    assert read.attested_not_proven == frozenset({"admin:org"})
    assert read.login == "rqa-operator"
    assert read.probed_at == PROBED_AT


def test_an_absent_proof_is_none_not_an_empty_one() -> None:
    store = SqliteCapabilityStore(connected())
    assert store.current(REPO, JOB) is None
    store.put(proof())
    assert store.current(REPO, "job-2") is None
    assert store.current("other/repo", JOB) is None


def test_a_second_put_for_one_job_replaces_the_row_and_keeps_its_id() -> None:
    """§5: "UNIQUE violation → replace". One job has one proof, never two answers a
    reader would have to choose between."""
    store = SqliteCapabilityStore(connected())
    first = store.put(proof(capabilities=frozenset({"pulls:read"})))
    second = store.put(proof(capabilities=frozenset({"pulls:write"}), login="someone-else"))
    assert first == second
    read = store.current(REPO, JOB)
    assert read.capabilities == frozenset({"pulls:write"})
    assert read.login == "someone-else"
    assert store.connection.execute("SELECT count(*) FROM capabilities").fetchone()[0] == 1


def test_two_jobs_on_one_repository_are_two_rows_with_two_ids() -> None:
    store = SqliteCapabilityStore(connected())
    first = store.put(proof(job_id="job-1"))
    second = store.put(proof(job_id="job-2"))
    assert first != second
    assert store.connection.execute("SELECT count(*) FROM capabilities").fetchone()[0] == 2


def test_the_sets_are_stored_sorted_so_one_reading_has_one_representation() -> None:
    store = SqliteCapabilityStore(connected())
    store.put(proof(capabilities=frozenset({"pulls:write", "contents:read", "checks:read"})))
    stored = store.connection.execute("SELECT capabilities FROM capabilities").fetchone()[0]
    assert stored == '["checks:read", "contents:read", "pulls:write"]'


def test_a_naive_timestamp_is_read_back_as_utc() -> None:
    store = SqliteCapabilityStore(connected())
    store.put(proof(probed_at=datetime(2026, 9, 12, 8, 30, 15)))
    read = store.current(REPO, JOB)
    assert read.probed_at == PROBED_AT


def test_the_store_never_commits_so_the_proof_lands_with_its_record_entries() -> None:
    """The proof, the `attestation` that describes it and the `grant` that used it
    become durable together or not at all — the discipline `rqa/record/writer.py` keeps
    for E-13."""
    path = pathlib.Path(__file__).resolve().parent / "_rqa_authority_store_probe.db"
    path.unlink(missing_ok=True)
    try:
        writer = sqlite3.connect(path)
        store = SqliteCapabilityStore(writer)
        store.put(proof())
        writer.rollback()
        assert store.current(REPO, JOB) is None
        writer.close()
    finally:
        path.unlink(missing_ok=True)


def test_the_protocol_methods_are_section_fives_two() -> None:
    import inspect

    from rqa.authority.store import CapabilityStore

    assert sorted(
        name for name in vars(CapabilityStore) if not name.startswith("_")
    ) == ["current", "put"]
    assert list(inspect.signature(CapabilityStore.current).parameters) == ["self", "repo", "job_id"]
    assert list(inspect.signature(CapabilityStore.put).parameters) == ["self", "proof"]
