#!/usr/bin/env python3
"""Tests for the gh-admin state store (issue #1846). No GitHub/network.

Fixture-free, pytest-free -- run directly (`python3 test_state.py`) or
picked up by a future `run_all.py` runner, matching
`review-queue-automation/tests`' own convention (see that suite's
`run_all.py` docstring for the discovery rule this mirrors).
"""

from __future__ import annotations

import pathlib
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scripts"))

from state import EXPECTED_TABLES, State, StatePersistenceError  # noqa: E402


def fresh_state() -> State:
    return State(tempfile.mkdtemp())


def test_migrate_creates_every_expected_table() -> None:
    state = fresh_state()
    try:
        rows = state.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        ).fetchall()
        actual = {row["name"] for row in rows}
        assert EXPECTED_TABLES <= actual, f"missing: {EXPECTED_TABLES - actual}"
    finally:
        state.close()


def test_database_path_is_suite_specific_not_review_queues() -> None:
    state = fresh_state()
    try:
        assert state.db_path.name == "gh-admin-state.sqlite3"
        assert state.db_path.name != "state.sqlite3"
    finally:
        state.close()


def test_leases_table_has_no_dangling_jobs_foreign_key() -> None:
    """The objective's own named hazard: the copied review-queue `leases`
    table carries `FOREIGN KEY (job_id) REFERENCES jobs(id))`, and this
    suite has no `jobs` table. Confirm this suite's own `leases` table
    declares no foreign key at all."""
    state = fresh_state()
    try:
        rows = state.execute("PRAGMA foreign_key_list(leases)").fetchall()
        assert rows == [], f"leases table must have no foreign keys, found: {rows}"
    finally:
        state.close()


def test_named_baseline_first_writer_wins_is_caught_not_silent() -> None:
    """The exact failure mode the objective names: 'both schemas define
    etags/mutations/leases with different shapes and CREATE TABLE IF NOT
    EXISTS lets the first writer silently win.' Reproduce review-queue-
    automation's own `leases` shape directly (`FOREIGN KEY (job_id)
    REFERENCES jobs(id)`, per that suite's `common.py` -- not imported
    here, since it unconditionally imports `fcntl`, unavailable on
    Windows; the shape is copied as data, not executed as code) at the
    exact path gh-admin's State expects, and confirm the fingerprint
    check refuses to treat the result as a valid gh-admin store rather
    than silently accepting whatever tables happen to already exist."""
    import sqlite3

    tmp_dir = pathlib.Path(tempfile.mkdtemp())
    db_path = tmp_dir / "gh-admin-state.sqlite3"
    collider = sqlite3.connect(db_path)
    collider.executescript(
        """
        CREATE TABLE IF NOT EXISTS jobs (id TEXT PRIMARY KEY);
        CREATE TABLE IF NOT EXISTS leases (
          repo TEXT NOT NULL,
          number INTEGER NOT NULL,
          job_id TEXT NOT NULL,
          claimed_at TEXT NOT NULL,
          PRIMARY KEY (repo, number),
          FOREIGN KEY (job_id) REFERENCES jobs(id)
        );
        """
    )
    collider.commit()
    collider.close()

    try:
        State(str(tmp_dir))
        raise AssertionError(
            "expected StatePersistenceError: gh-admin State must refuse a "
            "database shaped like review-queue-automation's, not silently accept it"
        )
    except StatePersistenceError as exc:
        assert "don't match this suite's expected shape" in str(exc)


def test_reopen_is_idempotent() -> None:
    tmp_dir = tempfile.mkdtemp()
    first = State(tmp_dir)
    first.execute(
        "INSERT INTO item_ids(repo,number,database_id,resolved_at) VALUES(?,?,?,?)",
        ("launchpad-26/buzz", 1846, 5279265254, "2026-08-31T00:00:00Z"),
    )
    first.commit()
    first.close()

    second = State(tmp_dir)
    try:
        row = second.execute(
            "SELECT database_id FROM item_ids WHERE repo=? AND number=?",
            ("launchpad-26/buzz", 1846),
        ).fetchone()
        assert row["database_id"] == 5279265254
    finally:
        second.close()


def test_runtime_lock_excludes_a_second_holder_until_released() -> None:
    tmp_dir = tempfile.mkdtemp()
    state = State(tmp_dir)
    try:
        first_lock = state.try_runtime_lock("scan")
        assert first_lock is not None

        second_lock = state.try_runtime_lock("scan")
        assert second_lock is None, "a second concurrent holder must be refused"

        first_lock.release()

        third_lock = state.try_runtime_lock("scan")
        assert third_lock is not None, "the lock must be re-acquirable after release"
        third_lock.release()
    finally:
        state.close()


def test_add_column_if_missing_adds_idempotently_to_on_disk_schema() -> None:
    """Issue #1946: `_migrate()` had no additive-column path -- `CREATE TABLE
    IF NOT EXISTS` cannot add a column to a table that already exists on
    disk. Reproduce that exact scenario: an on-disk `gh-admin-state.sqlite3`
    already carrying the pre-addition schema (created by a first State
    instance and closed, matching how a real prior run left the file), then
    reopen it and add a column the original schema never had. The column
    must appear after the first call and the call must be idempotent -- a
    second call must not raise and must report nothing was added."""
    tmp_dir = tempfile.mkdtemp()

    first = State(tmp_dir)
    first.close()

    second = State(tmp_dir)
    try:
        before = {row["name"] for row in second.execute("PRAGMA table_info(sessions)")}
        assert "example_new_column" not in before

        added = second._add_column_if_missing("sessions", "example_new_column", "TEXT")
        assert added is True
        second.commit()

        after = {row["name"] for row in second.execute("PRAGMA table_info(sessions)")}
        assert "example_new_column" in after

        added_again = second._add_column_if_missing("sessions", "example_new_column", "TEXT")
        assert added_again is False, "a second call must be a no-op, not an error"
    finally:
        second.close()

    # Confirm the column survived on disk, not just in the connection that
    # added it -- via a raw connection, not another State(...), since
    # State's own _assert_fingerprint() rejects any table whose columns
    # don't exactly match EXPECTED_COLUMNS, and this test's added column is
    # deliberately not in that fixed set.
    import sqlite3

    raw = sqlite3.connect(pathlib.Path(tmp_dir) / "gh-admin-state.sqlite3")
    try:
        columns = {row[1] for row in raw.execute("PRAGMA table_info(sessions)")}
        assert "example_new_column" in columns
    finally:
        raw.close()


def test_execute_wraps_sqlite_errors() -> None:
    state = fresh_state()
    try:
        try:
            state.execute("SELECT * FROM no_such_table")
            raise AssertionError("expected StatePersistenceError")
        except StatePersistenceError:
            pass
    finally:
        state.close()


if __name__ == "__main__":
    failures = 0
    passed = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                passed += 1
            except Exception as exc:
                failures += 1
                import traceback

                traceback.print_exc()
                print(f"FAIL {name}: {exc}")
    print(f"{passed} passed, {failures} failed")
    sys.exit(1 if failures else 0)
