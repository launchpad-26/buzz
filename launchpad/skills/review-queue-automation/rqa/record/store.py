"""`record_entries` and `record_heads` — `code/P-12-record.md` §5, and §8's closing
property.

This module is the only place in RQA that writes either table. `append` (§3.1) and
the one-way migration (§6) both travel through the primitives here; nothing else,
inside this package or outside it, issues an insert against them. §8 states that as a
property of the whole tree, and `tests/test_rqa_record_surface.py` scans `rqa/` for it.

**Retention: none.** §5 and §7: there is no delete, purge, vacuum or compaction
statement here, and none is to be added. `container.md` §5 records the unbounded
growth of these tables as a deliberate, operator-carried cost.

**Rows in, rows out.** A `StoredEntry` is the row exactly as it sits on disk —
`payload` is the canonical JSON *text*, `keyed` is the explicit bit, `hmac` is NULL
exactly when `keyed` is 0. `verify` needs that literal form, because re-deriving any
of it from something else is how an integrity check stops checking. `record_row`
converts to `CONTRACTS.md` §7's `RecordRow` for readers, which is the only place the
payload becomes a `Mapping` again.
"""

from __future__ import annotations

import json
import sqlite3
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from rqa.contracts import EntryKind, RecordRow
from rqa.record.hashing import LEGACY_PREV_HASH

__all__ = [
    "SCHEMA",
    "StoredEntry",
    "ensure_schema",
    "entries_for_job",
    "entries_of_kind",
    "head_entry",
    "head_row",
    "insert_entry",
    "is_legacy",
    "latest_of_kind",
    "record_row",
    "rows_of_kind_across_jobs",
    "upsert_head",
    "StoredAnchor",
    "insert_anchor",
    "mark_anchor_published",
    "latest_anchor",
    "pending_anchors",
    "anchors_for_job",
]

#: §5's DDL, with `IF NOT EXISTS` so a writer can be constructed against a state
#: directory that already has the tables. The shape, the CHECKs and the indexes are
#: §5's verbatim; the CHECK on `(keyed, hmac)` is what makes "unkeyed" a stored fact
#: rather than an inference from a missing head row (§3.1).
SCHEMA = (
    """
    CREATE TABLE IF NOT EXISTS record_entries (
      job       TEXT NOT NULL,
      seq       INTEGER NOT NULL,
      kind      TEXT NOT NULL,
      at        TEXT NOT NULL,
      payload   JSON NOT NULL,
      prev_hash TEXT,
      hash      TEXT NOT NULL,
      hmac      TEXT,
      keyed     INTEGER NOT NULL CHECK (keyed IN (0, 1)),
      CHECK ((keyed = 1 AND hmac IS NOT NULL) OR (keyed = 0 AND hmac IS NULL)),
      UNIQUE (job, seq)
    )
    """,
    "CREATE INDEX IF NOT EXISTS record_entries_by_job ON record_entries(job, seq)",
    "CREATE INDEX IF NOT EXISTS record_entries_by_kind ON record_entries(kind)",
    """
    CREATE TABLE IF NOT EXISTS record_heads (
      job TEXT PRIMARY KEY, seq INTEGER NOT NULL, hash TEXT NOT NULL,
      hmac TEXT, keyed INTEGER NOT NULL CHECK (keyed IN (0, 1))
    )
    """,
    # ADR-0066's anchored chain head. One row per published (or pending) anchor:
    # `destination` is NULL until the publish succeeds, which is what makes a failed
    # publish a recorded, retryable fact rather than a silently dropped one.
    """
    CREATE TABLE IF NOT EXISTS record_anchors (
      job         TEXT NOT NULL,
      seq         INTEGER NOT NULL,
      hash        TEXT NOT NULL,
      at          TEXT NOT NULL,
      destination TEXT,
      UNIQUE (job, seq)
    )
    """,
    "CREATE INDEX IF NOT EXISTS record_anchors_by_job ON record_anchors(job, seq)",
)

_COLUMNS = "job, seq, kind, at, payload, prev_hash, hash, hmac, keyed"


@dataclass(frozen=True)
class StoredEntry:
    """One `record_entries` row, in its stored form."""

    job: str
    seq: int
    kind: str
    at: str
    payload: str  # canonical JSON text, exactly as hashed
    prev_hash: str | None
    hash: str
    hmac: str | None
    keyed: bool


def ensure_schema(*, connection: sqlite3.Connection) -> None:
    """Create the two tables and their indexes if they are not there yet.

    Idempotent, and deliberately separate from every write path: a writer runs this
    once when it is constructed, before the caller opens the transaction `append`
    joins, so no DDL ever lands in the middle of a caller's transaction.
    """
    for statement in SCHEMA:
        connection.execute(statement)


def insert_entry(*, connection: sqlite3.Connection, entry: StoredEntry) -> None:
    """Write one row. The only such statement in RQA (§8's closing property).

    No commit and no rollback: the caller owns the transaction, which is what makes
    the entry and the state change it describes atomic with each other (§3.1).
    """
    connection.execute(
        f"INSERT INTO record_entries ({_COLUMNS}) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            entry.job,
            entry.seq,
            entry.kind,
            entry.at,
            entry.payload,
            entry.prev_hash,
            entry.hash,
            entry.hmac,
            1 if entry.keyed else 0,
        ),
    )


def upsert_head(
    *,
    connection: sqlite3.Connection,
    job: str,
    seq: int,
    hash: str,
    hmac: str | None,
    keyed: bool,
) -> None:
    """Point `record_heads` at the job's newest entry (§3.1 step 7).

    The head carries the same `keyed`/`hmac` state as the entry it names, but it is
    a convenience, never proof: §5's read protocol requires `verify` to read each
    row's own bits rather than treating this row as evidence about any of them.
    """
    connection.execute(
        "INSERT INTO record_heads (job, seq, hash, hmac, keyed) VALUES (?, ?, ?, ?, ?) "
        "ON CONFLICT(job) DO UPDATE SET seq = excluded.seq, hash = excluded.hash, "
        "hmac = excluded.hmac, keyed = excluded.keyed",
        (job, seq, hash, hmac, 1 if keyed else 0),
    )


def is_legacy(*, entry: StoredEntry) -> bool:
    """§6: a migrated row is the one carrying `prev_hash = "legacy"`.

    Not the `kind`: `approval_decisions` and `cost_ledger` migrate into `decision`
    and `spend`, so kind cannot tell a migrated row from a live one — the sentinel
    parent can, and it is what keeps migrated rows out of `verify`'s walk.
    """
    return entry.prev_hash == LEGACY_PREV_HASH


def _entry(row: tuple) -> StoredEntry:
    job, seq, kind, at, payload, prev_hash, hash, hmac, keyed = row
    return StoredEntry(
        job=job,
        seq=int(seq),
        kind=kind,
        at=at,
        payload=payload,
        prev_hash=prev_hash,
        hash=hash,
        hmac=hmac,
        keyed=bool(keyed),
    )


def head_entry(*, connection: sqlite3.Connection, job: str) -> StoredEntry | None:
    """The highest-`seq` non-legacy row for `job`, or `None` (§3.1 step 3).

    Migrated rows are excluded so a live chain never adopts a `prev_hash = "legacy"`
    row as its parent; a job holding only migrated rows starts its live chain at
    `seq` 1 with a NULL parent, exactly as an empty job does.
    """
    cursor = connection.execute(
        f"SELECT {_COLUMNS} FROM record_entries "
        "WHERE job = ? AND (prev_hash IS NULL OR prev_hash <> ?) "
        "ORDER BY seq DESC LIMIT 1",
        (job, LEGACY_PREV_HASH),
    )
    row = cursor.fetchone()
    return None if row is None else _entry(tuple(row))


def entries_for_job(*, connection: sqlite3.Connection, job: str) -> tuple[StoredEntry, ...]:
    """Every row for `job`, ordered by `seq` — §5's range scan over `(job, seq)`."""
    cursor = connection.execute(
        f"SELECT {_COLUMNS} FROM record_entries WHERE job = ? ORDER BY seq", (job,)
    )
    return tuple(_entry(tuple(row)) for row in cursor.fetchall())


def entries_of_kind(
    *, connection: sqlite3.Connection, job: str, kind: str
) -> tuple[StoredEntry, ...]:
    """Every row of one kind for `job`, ordered by `seq`."""
    cursor = connection.execute(
        f"SELECT {_COLUMNS} FROM record_entries WHERE job = ? AND kind = ? ORDER BY seq",
        (job, kind),
    )
    return tuple(_entry(tuple(row)) for row in cursor.fetchall())


def latest_of_kind(
    *, connection: sqlite3.Connection, job: str, kind: str
) -> StoredEntry | None:
    """The greatest-`seq` row of one kind for `job`, or `None` (§5's read protocol)."""
    cursor = connection.execute(
        f"SELECT {_COLUMNS} FROM record_entries WHERE job = ? AND kind = ? "
        "ORDER BY seq DESC LIMIT 1",
        (job, kind),
    )
    row = cursor.fetchone()
    return None if row is None else _entry(tuple(row))


def rows_of_kind_across_jobs(
    *, connection: sqlite3.Connection, kind: str
) -> tuple[StoredEntry, ...]:
    """Every row of one kind across every job, ordered by `(job, seq)`.

    §5's read protocol names one such scan: `resolve_job` reads `transition` rows to
    find which job a `(repo, number)` belongs to, because `container.md` §5 does not
    make P-12 a reader of P-01's `jobs` table.
    """
    cursor = connection.execute(
        f"SELECT {_COLUMNS} FROM record_entries WHERE kind = ? ORDER BY job, seq", (kind,)
    )
    return tuple(_entry(tuple(row)) for row in cursor.fetchall())


def head_row(*, connection: sqlite3.Connection, job: str) -> tuple[int, str, str | None, bool] | None:
    """`record_heads` for `job` as `(seq, hash, hmac, keyed)`, or `None`."""
    cursor = connection.execute(
        "SELECT seq, hash, hmac, keyed FROM record_heads WHERE job = ?", (job,)
    )
    row = cursor.fetchone()
    if row is None:
        return None
    seq, hash, hmac, keyed = row
    return int(seq), hash, hmac, bool(keyed)


def record_row(*, entry: StoredEntry) -> RecordRow:
    """One stored row as `CONTRACTS.md` §7's `RecordRow`.

    The payload comes back as the plain `Mapping` it was stored as; a row whose
    payload text no longer parses is a corrupt store, and `json.JSONDecodeError`
    (a `ValueError`) propagates rather than being smoothed into an empty payload.
    """
    payload: Mapping[str, Any] = json.loads(entry.payload)
    kind: EntryKind = entry.kind  # type: ignore[assignment]
    return RecordRow(
        seq=entry.seq,
        kind=kind,
        at=datetime.fromisoformat(entry.at),
        payload=payload,
    )


# --------------------------------------------------------------------------
# ADR-0066: the anchored chain head. These rows are evidence *about* the chain,
# never part of it — nothing here is hashed into an entry, and `append` neither
# reads nor writes this table.
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class StoredAnchor:
    """One anchor row. `destination` is None while the publish is still pending."""

    job: str
    seq: int
    hash: str
    at: str
    destination: str | None

    @property
    def published(self) -> bool:
        return self.destination is not None


def _anchor(row: tuple) -> StoredAnchor:
    job, seq, hash_, at, destination = row
    return StoredAnchor(job=job, seq=seq, hash=hash_, at=at, destination=destination)


def insert_anchor(
    *, connection: sqlite3.Connection, job: str, seq: int, hash: str, at: str
) -> None:
    """Record the intent to anchor `(job, seq)` before any publish is attempted.

    Written first, on purpose. The local row is what detects a truncated tail with no
    network at all, so it must survive a publish that never succeeds.
    """
    connection.execute(
        "INSERT OR IGNORE INTO record_anchors (job, seq, hash, at, destination) "
        "VALUES (?, ?, ?, ?, NULL)",
        (job, seq, hash, at),
    )


def mark_anchor_published(
    *, connection: sqlite3.Connection, job: str, seq: int, destination: str
) -> None:
    """Record where the anchor was published. Only called after the publish returned."""
    connection.execute(
        "UPDATE record_anchors SET destination = ? WHERE job = ? AND seq = ?",
        (destination, job, seq),
    )


def latest_anchor(*, connection: sqlite3.Connection, job: str) -> StoredAnchor | None:
    """The highest-`seq` anchor for `job`, published or not."""
    cursor = connection.execute(
        "SELECT job, seq, hash, at, destination FROM record_anchors "
        "WHERE job = ? ORDER BY seq DESC LIMIT 1",
        (job,),
    )
    row = cursor.fetchone()
    return None if row is None else _anchor(tuple(row))


def pending_anchors(*, connection: sqlite3.Connection, job: str) -> tuple[StoredAnchor, ...]:
    """Anchors recorded but never published, oldest first — the retry queue."""
    cursor = connection.execute(
        "SELECT job, seq, hash, at, destination FROM record_anchors "
        "WHERE job = ? AND destination IS NULL ORDER BY seq",
        (job,),
    )
    return tuple(_anchor(tuple(row)) for row in cursor.fetchall())


def anchors_for_job(*, connection: sqlite3.Connection, job: str) -> tuple[StoredAnchor, ...]:
    """Every anchor for `job`, in sequence order."""
    cursor = connection.execute(
        "SELECT job, seq, hash, at, destination FROM record_anchors "
        "WHERE job = ? ORDER BY seq",
        (job,),
    )
    return tuple(_anchor(tuple(row)) for row in cursor.fetchall())
