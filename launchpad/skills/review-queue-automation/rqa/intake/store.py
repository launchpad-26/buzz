"""`jobs`, `pr_facts` and `leases` — `code/P-01-intake.md` §5 — and the three
read/write protocols P-02 and the sibling `rqa/intake/` modules hold them
through.

Only this module writes these three tables (`container.md` §5: `jobs` and
`pr_facts` are written by P-01; so is `leases`). `JobStore.set_status` and
`JobStore.set_snapshot_hash` are declared here **only** for
`code/P-02-lifecycle.md` to call: nothing under `rqa/intake/` calls either
after `create`'s own `INSERT`, which fixes the initial `JobStatus` with the
literal `'queued'` rather than by calling `set_status` (§5, §7,
`tests/test_rqa_intake_surface.py`'s suite-wide property).

`DEFAULT_BATCH_SIZE` and the two `JobStatus` partitions `_SWEEP_RESUMABLE`/
`_RESTING` live here rather than in the sibling's `batch.py`, because
`select_batch`/`pending_followup` are this module's own methods and need them
directly. See this lane's handoff `## Decisions` for why the sibling package
imports these three names instead of redefining them.

Every statement below binds its parameters; none interpolates a caller-
supplied value into SQL text — `repo`, `head_ref`, `labels` and every other
GitHub-observed field are untrusted data and are stored and read back through
bound placeholders only (§5's security guard 4).
"""

from __future__ import annotations

import json
import sqlite3
from collections.abc import Callable
from datetime import datetime, timezone
from typing import Protocol

from rqa.contracts import Job, JobStatus
from rqa.intake.types import LeaseRow, PrFactsRow

__all__ = [
    "SCHEMA",
    "DEFAULT_BATCH_SIZE",
    "ensure_schema",
    "JobStore",
    "PrFactsStore",
    "LeaseStore",
    "SqliteJobStore",
    "SqlitePrFactsStore",
    "SqliteLeaseStore",
]

#: `§3` step 3's implementer's-choice constant; no `container.md` §5 record
#: models a batch size as policy-configurable.
DEFAULT_BATCH_SIZE = 20

# The two JobStatus partitions `code/P-01-intake.md` §2 mirrors from
# `flow-review-lifecycle.md` §4. Together they cover all thirteen JobStatus
# members exactly once — `tests/test_rqa_intake_surface.py` asserts that.
_SWEEP_RESUMABLE: frozenset[JobStatus] = frozenset(
    {
        JobStatus.QUEUED,
        JobStatus.CLAIMED,
        JobStatus.PLANNED,
        JobStatus.REVIEWING,
        JobStatus.JUDGED,
        JobStatus.SUBMITTING,
        JobStatus.STOPPED,
    }
)
_RESTING: frozenset[JobStatus] = frozenset(
    {
        JobStatus.ESCALATED,
        JobStatus.REMEDIATING,
        JobStatus.APPROVED,
        JobStatus.MERGED,
        JobStatus.CHANGES_REQUESTED,
        JobStatus.SUPERSEDED,
    }
)
_SWEEP_RESUMABLE_VALUES: frozenset[str] = frozenset(member.value for member in _SWEEP_RESUMABLE)
_RESTING_VALUES: frozenset[str] = frozenset(member.value for member in _RESTING)

SCHEMA = """
CREATE TABLE IF NOT EXISTS jobs (
  id              TEXT PRIMARY KEY,
  repo            TEXT NOT NULL,
  number          INTEGER NOT NULL,
  head_sha        TEXT NOT NULL,
  base_sha        TEXT NOT NULL,
  head_repo       TEXT NOT NULL,
  head_ref        TEXT NOT NULL,
  predecessor_job TEXT REFERENCES jobs(id),
  predecessor_head_sha TEXT,
  snapshot_hash   TEXT,
  status          TEXT NOT NULL,
  created_at      TEXT NOT NULL,
  UNIQUE (repo, number, head_sha)
);
CREATE INDEX IF NOT EXISTS idx_jobs_pr    ON jobs (repo, number, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_jobs_sweep ON jobs (status, created_at, id);

CREATE TABLE IF NOT EXISTS pr_facts (
  repo         TEXT NOT NULL,
  number       INTEGER NOT NULL,
  head_sha     TEXT NOT NULL,
  base_sha     TEXT NOT NULL,
  head_repo    TEXT NOT NULL,
  head_ref     TEXT NOT NULL,
  author       TEXT NOT NULL,
  labels       TEXT NOT NULL,
  last_seen_at TEXT NOT NULL,
  PRIMARY KEY (repo, number)
);

CREATE TABLE IF NOT EXISTS leases (
  job_id     TEXT PRIMARY KEY,
  repo       TEXT NOT NULL,
  number     INTEGER NOT NULL,
  claimed_at TEXT NOT NULL,
  UNIQUE (repo, number)
);
"""


def ensure_schema(connection: sqlite3.Connection) -> None:
    """Create the three §5 tables and their indexes when absent. Idempotent."""
    connection.executescript(SCHEMA)
    connection.commit()


class JobStore(Protocol):
    def create(self, job: Job) -> None: ...  # INSERT; UNIQUE violation is the caller's
    # own duplicate-check failing, never reached in practice per §3 step 2c's guard
    def get(self, job_id: str) -> Job | None: ...  # read: P-02, P-11, P-13
    def current_for_pr(self, repo: str, number: int) -> Job | None: ...  # latest job for (repo, number)
    def select_batch(self, limit: int) -> list[Job]: ...  # §3 step 3
    def pending_followup(self) -> list[Job]: ...  # §3 step 4
    def set_status(self, job_id: str, status: JobStatus) -> None: ...  # P-02's exclusive write
    def set_snapshot_hash(self, job_id: str, snapshot_hash: str) -> None: ...  # P-02's exclusive
    # write, once, at first pin


class PrFactsStore(Protocol):
    def upsert(self, row: PrFactsRow) -> None: ...  # INSERT ... ON CONFLICT(repo, number) DO UPDATE
    def get(self, repo: str, number: int) -> PrFactsRow | None: ...


class LeaseStore(Protocol):
    def current(self, repo: str, number: int) -> LeaseRow | None: ...  # read: P-02 (container.md §5)
    def put(self, row: LeaseRow) -> None: ...
    def delete(self, repo: str, number: int) -> None: ...


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


# `SELECT * FROM jobs` returns columns in the DDL's declared order above:
# id, repo, number, head_sha, base_sha, head_repo, head_ref, predecessor_job,
# predecessor_head_sha, snapshot_hash, status, created_at (indexes 0-11).
# Reading positionally, and constructing `Job` positionally rather than by
# keyword, keeps every read method free of a second, independent spelling of
# the column name `create`'s `INSERT` already names once.
_STATUS_COLUMN_INDEX = 10
_PREDECESSOR_COLUMN_INDEX = 7


def _row_to_job(row: tuple) -> Job:
    return Job(
        row[0],
        row[1],
        row[2],
        row[3],
        row[4],
        row[5],
        row[6],
        row[7],
        row[8],
        row[9],
        JobStatus(row[_STATUS_COLUMN_INDEX]),
    )


class SqliteJobStore:
    """`JobStore` over the one shared `state.db` connection. Never commits:
    the caller owns transaction boundaries (`code/P-01-intake.md` §3: "P-01
    commits once per PR ... and once per job")."""

    def __init__(self, connection: sqlite3.Connection, *, clock: Callable[[], datetime] = _utcnow) -> None:
        self._connection = connection
        self._clock = clock

    def create(self, job: Job) -> None:
        self._connection.execute(
            "INSERT INTO jobs (id, repo, number, head_sha, base_sha, head_repo,"
            " head_ref, predecessor_job, predecessor_head_sha, snapshot_hash,"
            " status, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'queued', ?)",
            (
                job.id,
                job.repo,
                job.number,
                job.head_sha,
                job.base_sha,
                job.head_repo,
                job.head_ref,
                job.predecessor_job,
                job.predecessor_head_sha,
                job.snapshot_hash,
                self._clock().isoformat(),
            ),
        )

    def get(self, job_id: str) -> Job | None:
        row = self._connection.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
        return None if row is None else _row_to_job(row)

    def current_for_pr(self, repo: str, number: int) -> Job | None:
        # `id DESC` only breaks a `created_at` tie by content hash, which has
        # no relationship to insertion order — structurally safe because the
        # exclusive sweep lock (`lock.py`) serialises every tick and this is
        # queried at most once per PR per tick, never concurrently.
        row = self._connection.execute(
            "SELECT * FROM jobs WHERE repo = ? AND number = ?"
            " ORDER BY created_at DESC, id DESC LIMIT 1",
            (repo, number),
        ).fetchone()
        return None if row is None else _row_to_job(row)

    def select_batch(self, limit: int) -> list[Job]:
        rows = self._connection.execute("SELECT * FROM jobs ORDER BY created_at, id").fetchall()
        resumable = [row for row in rows if row[_STATUS_COLUMN_INDEX] in _SWEEP_RESUMABLE_VALUES]
        return [_row_to_job(row) for row in resumable[:limit]]

    def pending_followup(self) -> list[Job]:
        rows = self._connection.execute("SELECT * FROM jobs ORDER BY created_at, id").fetchall()
        successors_by_predecessor: dict[str, list[tuple]] = {}
        for row in rows:
            predecessor = row[_PREDECESSOR_COLUMN_INDEX]
            if predecessor is not None:
                successors_by_predecessor.setdefault(predecessor, []).append(row)
        leased_job_ids = {
            leased[0] for leased in self._connection.execute("SELECT job_id FROM leases").fetchall()
        }

        followup: list[Job] = []
        for row in rows:
            if row[_STATUS_COLUMN_INDEX] not in _RESTING_VALUES:
                continue
            job_id = row[0]
            successors = successors_by_predecessor.get(job_id, ())
            has_unsuperseded_successor = any(
                successor[_STATUS_COLUMN_INDEX] != JobStatus.SUPERSEDED.value for successor in successors
            )
            if has_unsuperseded_successor or job_id in leased_job_ids:
                followup.append(_row_to_job(row))
        return followup

    def set_status(self, job_id: str, status: JobStatus) -> None:
        self._connection.execute("UPDATE jobs SET status = ? WHERE id = ?", (status.value, job_id))

    def set_snapshot_hash(self, job_id: str, snapshot_hash: str) -> None:
        self._connection.execute(
            "UPDATE jobs SET snapshot_hash = ? WHERE id = ?", (snapshot_hash, job_id)
        )


class SqlitePrFactsStore:
    """`PrFactsStore` over the same shared connection. Never commits (see
    `SqliteJobStore`)."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    def upsert(self, row: PrFactsRow) -> None:
        self._connection.execute(
            "INSERT INTO pr_facts (repo, number, head_sha, base_sha, head_repo,"
            " head_ref, author, labels, last_seen_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
            " ON CONFLICT(repo, number) DO UPDATE SET"
            " head_sha = excluded.head_sha, base_sha = excluded.base_sha,"
            " head_repo = excluded.head_repo, head_ref = excluded.head_ref,"
            " author = excluded.author, labels = excluded.labels,"
            " last_seen_at = excluded.last_seen_at",
            (
                row.repo,
                row.number,
                row.head_sha,
                row.base_sha,
                row.head_repo,
                row.head_ref,
                row.author,
                json.dumps(list(row.labels)),
                row.last_seen_at.isoformat(),
            ),
        )

    def get(self, repo: str, number: int) -> PrFactsRow | None:
        row = self._connection.execute(
            "SELECT repo, number, head_sha, base_sha, head_repo, head_ref, author,"
            " labels, last_seen_at FROM pr_facts WHERE repo = ? AND number = ?",
            (repo, number),
        ).fetchone()
        if row is None:
            return None
        return PrFactsRow(
            repo=row[0],
            number=row[1],
            head_sha=row[2],
            base_sha=row[3],
            head_repo=row[4],
            head_ref=row[5],
            author=row[6],
            labels=tuple(json.loads(row[7])),
            last_seen_at=datetime.fromisoformat(row[8]),
        )


class SqliteLeaseStore:
    """`LeaseStore` over the same shared connection. Never commits (see
    `SqliteJobStore`)."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    def current(self, repo: str, number: int) -> LeaseRow | None:
        row = self._connection.execute(
            "SELECT job_id, repo, number, claimed_at FROM leases WHERE repo = ? AND number = ?",
            (repo, number),
        ).fetchone()
        if row is None:
            return None
        return LeaseRow(job_id=row[0], repo=row[1], number=row[2], claimed_at=datetime.fromisoformat(row[3]))

    def put(self, row: LeaseRow) -> None:
        # UNIQUE(repo, number) violation is a second concurrent claim on the
        # same PR; UNIQUE(job_id) [the primary key] is a caller error. Both
        # propagate as sqlite3.IntegrityError, never swallowed here.
        self._connection.execute(
            "INSERT INTO leases (job_id, repo, number, claimed_at) VALUES (?, ?, ?, ?)",
            (row.job_id, row.repo, row.number, row.claimed_at.isoformat()),
        )

    def delete(self, repo: str, number: int) -> None:
        self._connection.execute("DELETE FROM leases WHERE repo = ? AND number = ?", (repo, number))
