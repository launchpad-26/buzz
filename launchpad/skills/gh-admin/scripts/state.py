"""SQLite-backed durable state store for the gh-admin suite (issue #1846).

This is the suite's **own copy** of the review-queue-automation State pattern
(`launchpad/skills/review-queue-automation/scripts/common.py`'s `State`
class): WAL journal mode, `foreign_keys=ON`, a 30-second busy timeout, an
exclusive advisory lock for one-runner-at-a-time commands, and additive
column migrations. It is a copy, not an import: that class's `leases` table
carries `FOREIGN KEY (job_id) REFERENCES jobs(id)`, and this suite has no
`jobs` table, so importing it here would create a dangling foreign key on
first write. This module also points at its own database file
(`gh-admin-state.sqlite3`, never `state.sqlite3`) — both suites define
tables named `leases` with different shapes, and `CREATE TABLE IF NOT
EXISTS` lets whichever suite opens the file first silently win if the two
were ever pointed at the same path.

One deliberate deviation from the copied pattern: the review-queue
original uses `fcntl.flock` unconditionally, which does not exist on
Windows (`ModuleNotFoundError: No module named 'fcntl'`) -- confirmed in
this development environment. `_ExclusiveLock` below dispatches to
`fcntl.flock` on POSIX and `msvcrt.locking` on Windows, so the suite (and
its tests) can actually run on both platforms this repo is developed on.
"""

from __future__ import annotations

import contextlib
import datetime
import json
import os
import pathlib
import sqlite3
from dataclasses import dataclass
from typing import Any, Iterator

try:
    import fcntl  # POSIX

    _PLATFORM_LOCK = "fcntl"
except ImportError:  # Windows
    import msvcrt

    _PLATFORM_LOCK = "msvcrt"


class StatePersistenceError(RuntimeError):
    """Raised when the gh-admin state store cannot be opened or written."""


def utcnow() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def _lock_file(handle) -> bool:
    """Try to take a non-blocking exclusive lock on `handle`. True on success."""
    if _PLATFORM_LOCK == "fcntl":
        try:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            return True
        except BlockingIOError:
            return False
    # msvcrt locks a byte range starting at the file's current position.
    # Lock exactly one byte at offset 0 -- the byte's content is unused,
    # only its lock state matters.
    handle.seek(0)
    try:
        msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
        return True
    except OSError:
        return False


def _unlock_file(handle) -> None:
    if _PLATFORM_LOCK == "fcntl":
        fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
        return
    handle.seek(0)
    try:
        msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
    except OSError:
        # Already unlocked (e.g. handle never successfully locked) -- not
        # an error for release semantics.
        pass


@dataclass
class RuntimeLock:
    """An exclusive, non-blocking process lock for one state directory.

    Mirrors review-queue-automation's `RuntimeLock`. The descriptor stays
    open for the lock's lifetime; on POSIX the kernel releases `flock`
    locks automatically if this process crashes. On Windows, `msvcrt`
    locks are released when the file handle closes, which happens on
    process exit including most crashes -- not a byte-for-byte guarantee
    on every abnormal termination, but the same "don't rely on graceful
    shutdown" property the POSIX path has.
    """

    path: pathlib.Path
    _handle: Any

    def release(self) -> None:
        if self._handle is None:
            return
        try:
            _unlock_file(self._handle)
        finally:
            self._handle.close()
            self._handle = None


# The expected column set per table, checked *after* `_migrate()` runs, not
# before. Table *names* alone are not enough: `CREATE TABLE IF NOT EXISTS`
# is a silent no-op against a pre-existing table of the same name but a
# different shape (e.g. this path accidentally pointed at a database
# already carrying review-queue-automation's own `leases` table, which
# collides on name but has different columns and a `job_id` foreign key
# this suite must never carry). A names-only check would still pass in
# exactly that case, since every *other* table gets created fresh — this
# is why each table's column set is captured, not just its existence.
EXPECTED_COLUMNS: dict[str, frozenset[str]] = {
    "page_cache": frozenset({"url", "etag", "weak_etag", "body", "next_link", "fetched_at"}),
    "scan_manifest": frozenset(
        {
            "repo",
            "number",
            "project_item_id",
            "board_status",
            "native_state",
            "state_reason",
            "scanned_at",
        }
    ),
    "rate_ledger": frozenset({"id", "dimension", "units", "recorded_at"}),
    "inflight": frozenset({"id", "dimension", "units", "reserved_at", "released_at"}),
    "retry_queue": frozenset(
        {
            "id",
            "operation",
            "payload",
            "attempts",
            "last_error",
            "next_attempt_at",
            "created_at",
        }
    ),
    "resource_state": frozenset(
        {"resource_type", "resource_key", "computed_state", "computed_at"}
    ),
    "item_ids": frozenset({"repo", "number", "database_id", "resolved_at"}),
    "incidents": frozenset(
        {"id", "kind", "repo", "number", "detail", "detected_at", "acknowledged_at"}
    ),
    "leases": frozenset({"scope", "holder", "claimed_at", "expires_at"}),
    "sessions": frozenset({"id", "started_at", "ended_at", "dead_letters", "summary"}),
}

EXPECTED_TABLES = frozenset(EXPECTED_COLUMNS)


class State:
    """SQLite-backed durable state for the gh-admin suite.

    Tables: `page_cache` (REST/GraphQL response cache, keyed by URL, both
    strong and weak ETag validators), `scan_manifest` (last-scanned board
    projection per repo+number), `rate_ledger` (append-only debit log per
    rate dimension, survives a crash after the debit reached "sent"),
    `inflight` (reservations taken before dispatch, released after),
    `retry_queue` (deferred retryable operations), `resource_state`
    (cached computed state per resource, e.g. the readiness ladder),
    `item_ids` ((repo, number) -> immutable database id cache),
    `incidents` (dead letters and other conditions a session must
    acknowledge), `leases` (exclusive claims, e.g. one Feature claimed by
    one orchestrator run -- no `job_id` foreign key, unlike the
    review-queue original, because this suite has no `jobs` table),
    `sessions` (one row per preflight run).
    """

    def __init__(self, state_dir: str | os.PathLike):
        self.root = pathlib.Path(state_dir).expanduser().resolve()
        self.root.mkdir(parents=True, exist_ok=True)
        self.db_path = self.root / "gh-admin-state.sqlite3"
        try:
            self.db = sqlite3.connect(self.db_path, timeout=30)
            self.db.row_factory = sqlite3.Row
            self.db.execute("PRAGMA journal_mode=WAL")
            self.db.execute("PRAGMA foreign_keys=ON")
            self._migrate()
            self._assert_fingerprint()
        except StatePersistenceError:
            # _assert_fingerprint() raises this directly (not a
            # sqlite3.Error/OSError) when the on-disk schema doesn't match
            # this suite's expected shape. Close before propagating -- same
            # leak the clause below closes, but this exception is already
            # the right type and must not be wrapped a second time.
            self._close_after_init_failure()
            raise
        except (sqlite3.Error, OSError) as exc:
            self._close_after_init_failure()
            raise StatePersistenceError(
                f"gh-admin state persistence did not open cleanly at {self.db_path}: {exc}"
            ) from exc

    def _close_after_init_failure(self) -> None:
        """Close `self.db` when __init__ fails after opening it.

        `self.db` is only assigned once `sqlite3.connect()` above has
        succeeded -- if connect() itself is what raised, the attribute was
        never set, so this is a no-op rather than an AttributeError. A
        secondary error from close() itself is suppressed so it can't mask
        the original failure being propagated.
        """
        db = getattr(self, "db", None)
        if db is None:
            return
        try:
            db.close()
        except sqlite3.Error:
            pass

    def try_runtime_lock(self, command: str) -> RuntimeLock | None:
        """Acquire the state-dir command lock, or return None when another run owns it."""
        path = self.root / "runtime.lock"
        try:
            handle = path.open("a+", encoding="utf-8")
        except OSError as exc:
            raise StatePersistenceError(f"runtime lock unavailable at {path}: {exc}") from exc

        if not _lock_file(handle):
            handle.close()
            return None

        handle.seek(0)
        handle.truncate()
        handle.write(
            json.dumps({"command": command, "pid": os.getpid(), "started_at": utcnow()}) + "\n"
        )
        handle.flush()
        os.fsync(handle.fileno())
        return RuntimeLock(path, handle)

    def execute(self, sql: str, params: tuple = ()) -> Any:
        try:
            return self.db.execute(sql, params)
        except sqlite3.Error as exc:
            raise StatePersistenceError(f"gh-admin state persistence failed: {exc}") from exc

    def commit(self) -> None:
        try:
            self.db.commit()
        except sqlite3.Error as exc:
            raise StatePersistenceError(f"gh-admin state commit failed: {exc}") from exc

    def close(self) -> None:
        self.db.close()

    @contextlib.contextmanager
    def transaction(self) -> Iterator["State"]:
        """Commit on clean exit, roll back on exception."""
        try:
            yield self
            self.commit()
        except Exception:
            self.db.rollback()
            raise

    def _migrate(self) -> None:
        self.db.executescript(
            """
            CREATE TABLE IF NOT EXISTS page_cache (
              url TEXT PRIMARY KEY,
              etag TEXT,
              weak_etag TEXT,
              body TEXT NOT NULL,
              next_link TEXT,
              fetched_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS scan_manifest (
              repo TEXT NOT NULL,
              number INTEGER NOT NULL,
              project_item_id TEXT,
              board_status TEXT,
              native_state TEXT,
              state_reason TEXT,
              scanned_at TEXT NOT NULL,
              PRIMARY KEY (repo, number)
            );

            CREATE TABLE IF NOT EXISTS rate_ledger (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              dimension TEXT NOT NULL,
              units INTEGER NOT NULL,
              recorded_at TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS rate_ledger_by_dimension
              ON rate_ledger (dimension, recorded_at);

            CREATE TABLE IF NOT EXISTS inflight (
              id TEXT PRIMARY KEY,
              dimension TEXT NOT NULL,
              units INTEGER NOT NULL,
              reserved_at TEXT NOT NULL,
              released_at TEXT
            );

            CREATE TABLE IF NOT EXISTS retry_queue (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              operation TEXT NOT NULL,
              payload TEXT NOT NULL,
              attempts INTEGER NOT NULL DEFAULT 0,
              last_error TEXT,
              next_attempt_at TEXT NOT NULL,
              created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS resource_state (
              resource_type TEXT NOT NULL,
              resource_key TEXT NOT NULL,
              computed_state TEXT NOT NULL,
              computed_at TEXT NOT NULL,
              PRIMARY KEY (resource_type, resource_key)
            );

            CREATE TABLE IF NOT EXISTS item_ids (
              repo TEXT NOT NULL,
              number INTEGER NOT NULL,
              database_id INTEGER NOT NULL,
              resolved_at TEXT NOT NULL,
              PRIMARY KEY (repo, number)
            );

            CREATE TABLE IF NOT EXISTS incidents (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              kind TEXT NOT NULL,
              repo TEXT,
              number INTEGER,
              detail TEXT NOT NULL,
              detected_at TEXT NOT NULL,
              acknowledged_at TEXT
            );

            CREATE TABLE IF NOT EXISTS leases (
              scope TEXT PRIMARY KEY,
              holder TEXT NOT NULL,
              claimed_at TEXT NOT NULL,
              expires_at TEXT
            );

            CREATE TABLE IF NOT EXISTS sessions (
              id TEXT PRIMARY KEY,
              started_at TEXT NOT NULL,
              ended_at TEXT,
              dead_letters INTEGER NOT NULL DEFAULT 0,
              summary TEXT
            );
            """
        )
        # Additive column migrations for databases created by an earlier
        # version. `CREATE TABLE IF NOT EXISTS` above cannot add a column to
        # an existing table, so each new column a later sibling task needs
        # is applied idempotently here via `_add_column_if_missing`, mirroring
        # review-queue-automation's `common.py` (`self._add_column_if_missing(
        # "jobs", "snapshot_hash", "TEXT")`). No column needs adding yet, so
        # there is no call site here today -- this is the path existing for
        # the next sibling task under Feature #1845 that does need one.
        self.commit()

    def _add_column_if_missing(self, table: str, column: str, decl: str) -> bool:
        """Add `column` to `table` when absent. Returns True when it was added."""
        existing = {row["name"] for row in self.db.execute(f"PRAGMA table_info({table})")}
        if column in existing:
            return False
        self.db.execute(f"ALTER TABLE {table} ADD COLUMN {column} {decl}")
        return True

    def _assert_fingerprint(self) -> None:
        rows = self.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        ).fetchall()
        actual_tables = {row["name"] for row in rows}
        missing = EXPECTED_TABLES - actual_tables
        if missing:
            raise StatePersistenceError(
                f"gh-admin state store at {self.db_path} is missing expected tables "
                f"{sorted(missing)} after migration. CREATE TABLE IF NOT EXISTS did not "
                "create them, which most likely means this path already held a "
                "differently-shaped database (e.g. review-queue-automation's own "
                "state.sqlite3) rather than a gh-admin one."
            )

        # Table presence alone doesn't catch a same-named, differently-shaped
        # pre-existing table (CREATE TABLE IF NOT EXISTS leaves it untouched) --
        # check every expected table's actual column set matches, not just
        # that a table with that name exists.
        shape_mismatches: list[str] = []
        for table, expected_columns in EXPECTED_COLUMNS.items():
            info_rows = self.execute(f"PRAGMA table_info({table})").fetchall()
            actual_columns = {row["name"] for row in info_rows}
            if actual_columns != expected_columns:
                shape_mismatches.append(
                    f"{table}: expected columns {sorted(expected_columns)}, "
                    f"found {sorted(actual_columns)}"
                )
        if shape_mismatches:
            raise StatePersistenceError(
                f"gh-admin state store at {self.db_path} has tables that exist but "
                "don't match this suite's expected shape (a same-named table from a "
                "different schema was already at this path, and CREATE TABLE IF NOT "
                "EXISTS left it untouched): " + "; ".join(shape_mismatches)
            )

        # Belt-and-braces: this suite's `leases` must never carry a foreign
        # key, unlike review-queue-automation's job_id-referencing original
        # (the exact hazard the objective names). The column-shape check
        # above would already catch review-queue's literal `leases` shape,
        # but this asserts the invariant directly regardless of column names.
        fk_rows = self.execute("PRAGMA foreign_key_list(leases)").fetchall()
        if fk_rows:
            raise StatePersistenceError(
                f"gh-admin state store at {self.db_path}: leases table must have no "
                f"foreign keys, found: {[dict(r) for r in fk_rows]}"
            )
