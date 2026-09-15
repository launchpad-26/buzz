"""The `human_requests` table and the `EscalationStore` protocol —
`code/P-11-escalation.md` §5, `container.md` §5's `human_requests` row.

`EscalationStore` is declared **here**, not in `rqa/edges.py`: `CONTRACTS.md` §9 names
it in E-11's signature and `rqa.edges` keeps it an empty Protocol whose docstring says
its shape is P-11's to state. This is that statement, and it is the same arrangement
`rqa/policy/store.py` makes for `SnapshotStore` and `rqa/authority/store.py` makes for
`CapabilityStore`.

**Written only by P-11.** P-02 reads it, read-only, through the injected `EscalationClient`
Protocol — never a second copy of this table (`container.md` §5: readers of
`human_requests` = P-02).

**No decision, actor, rationale or transport column.** §5: the index answers "what is
open", never "what was decided" — `actor`/`basis`/`substantiates`/`outcome` live on the
`decision` record entry (§6), and the notification-transport columns U-AUTHORITY-12 bins
have no successor here at all.
"""

from __future__ import annotations

import json
import sqlite3
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime, timezone
from types import MappingProxyType
from typing import Literal, Protocol

from rqa.contracts import EscalationCause

__all__ = ["EscalationRow", "EscalationStore", "SqliteEscalationStore", "ensure_schema"]

#: §5's DDL, verbatim, with `IF NOT EXISTS` so a writer can be constructed against a
#: state directory that already has the table (`rqa/authority/store.py`'s convention).
_SCHEMA = """
CREATE TABLE IF NOT EXISTS human_requests (
  id                  INTEGER PRIMARY KEY,
  job_id              TEXT NOT NULL,
  entry_seq           INTEGER NOT NULL,
  cause               TEXT NOT NULL,
  question            TEXT NOT NULL,
  context             TEXT NOT NULL,
  head_sha            TEXT NOT NULL,
  snapshot_hash       TEXT,                  -- NULL: escalated before a snapshot was ever
                                              -- pinned (P-02 step 3's ValidationFailure branch;
                                              -- CONTRACTS.md's own Job.snapshot_hash: str | None)
  raised_at           TEXT NOT NULL,
  status              TEXT NOT NULL DEFAULT 'open',
  closed_at           TEXT,
  decision_entry_seq  INTEGER,
  UNIQUE (job_id, entry_seq)
);
CREATE INDEX IF NOT EXISTS human_requests_status ON human_requests (status);
"""

_COLUMNS = (
    "id, job_id, entry_seq, cause, question, context, head_sha, snapshot_hash, "
    "raised_at, status, closed_at, decision_entry_seq"
)


@dataclass(frozen=True)
class EscalationRow:
    id: int
    job_id: str
    entry_seq: int
    cause: EscalationCause
    question: str
    context: Mapping[str, str]
    head_sha: str
    snapshot_hash: str | None
    raised_at: datetime
    status: Literal["open", "closed"]
    closed_at: datetime | None
    decision_entry_seq: int | None


class EscalationStore(Protocol):
    def insert(
        self,
        *,
        job_id: str,
        entry_seq: int,
        cause: EscalationCause,
        question: str,
        context: Mapping[str, str],
        head_sha: str,
        snapshot_hash: str | None,
        raised_at: datetime,
    ) -> int: ...  # returns the new row's id

    def get(self, escalation_id: int) -> EscalationRow | None: ...

    def pending(self) -> tuple[EscalationRow, ...]: ...  # status = 'open', raised_at ascending

    def close(self, escalation_id: int, *, decision_entry_seq: int, closed_at: datetime) -> None: ...


def ensure_schema(*, connection: sqlite3.Connection) -> None:
    """§5's DDL, idempotent. Run from the constructor so no DDL runs inside the
    transaction an `insert`/`close` joins."""
    connection.executescript(_SCHEMA)


def _stamp(moment: datetime) -> str:
    """ISO-8601 UTC. A naive reading is taken as UTC rather than as local time: a
    timestamp that means something different on each machine is not a durable fact
    anyone can reproduce."""
    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=timezone.utc)
    return moment.astimezone(timezone.utc).isoformat()


def _row(record: tuple) -> EscalationRow:
    (
        identifier, job_id, entry_seq, cause, question, context, head_sha, snapshot_hash,
        raised_at, status, closed_at, decision_entry_seq,
    ) = record
    return EscalationRow(
        id=int(identifier),
        job_id=job_id,
        entry_seq=int(entry_seq),
        cause=EscalationCause(cause),
        question=question,
        context=MappingProxyType(json.loads(context)),
        head_sha=head_sha,
        snapshot_hash=snapshot_hash,
        raised_at=datetime.fromisoformat(raised_at),
        status=status,
        closed_at=None if closed_at is None else datetime.fromisoformat(closed_at),
        decision_entry_seq=None if decision_entry_seq is None else int(decision_entry_seq),
    )


class SqliteEscalationStore:
    """`EscalationStore` over one caller-owned `sqlite3.Connection`.

    `connection` is a constructor-only dependency; it is not a §5 method parameter, so
    an `insert`/`close` joins whatever transaction the caller's own record append and
    job transition are already inside (§5: "written only by P-11").
    """

    def __init__(self, connection: sqlite3.Connection):
        self.connection = connection
        ensure_schema(connection=connection)

    def insert(
        self,
        *,
        job_id: str,
        entry_seq: int,
        cause: EscalationCause,
        question: str,
        context: Mapping[str, str],
        head_sha: str,
        snapshot_hash: str | None,
        raised_at: datetime,
    ) -> int:
        cursor = self.connection.execute(
            "INSERT INTO human_requests "
            "(job_id, entry_seq, cause, question, context, head_sha, snapshot_hash, raised_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                job_id,
                entry_seq,
                cause.value,
                question,
                json.dumps(dict(context), sort_keys=True),
                head_sha,
                snapshot_hash,
                _stamp(raised_at),
            ),
        )
        return int(cursor.lastrowid)

    def get(self, escalation_id: int) -> EscalationRow | None:
        row = self.connection.execute(
            f"SELECT {_COLUMNS} FROM human_requests WHERE id = ?", (escalation_id,)
        ).fetchone()
        return None if row is None else _row(tuple(row))

    def pending(self) -> tuple[EscalationRow, ...]:
        cursor = self.connection.execute(
            f"SELECT {_COLUMNS} FROM human_requests "
            "WHERE status = 'open' ORDER BY raised_at ASC, id ASC"
        )
        return tuple(_row(tuple(row)) for row in cursor.fetchall())

    def close(self, escalation_id: int, *, decision_entry_seq: int, closed_at: datetime) -> None:
        self.connection.execute(
            "UPDATE human_requests SET status = 'closed', closed_at = ?, decision_entry_seq = ? "
            "WHERE id = ?",
            (_stamp(closed_at), decision_entry_seq, escalation_id),
        )
