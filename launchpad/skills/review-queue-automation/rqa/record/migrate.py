"""One-way legacy migration — `code/P-12-record.md` §6's migration mapping.

Runs once, ever, against the three pre-cutover tables `scripts/common.py` defines:
`ledger_entries`, `approval_decisions`, `cost_ledger`. Every migrated row — of
every target kind — carries `prev_hash="legacy"`, so it is never examined by
`verify` (§3.2 step 2) and never `verified=True` from `explain` (§3.3 step 5),
"regardless of how well-formed its content is" (§6). Nothing here reads those
three tables directly: `LegacySource` is a read-only Protocol so this module (and
its tests) never depend on a real pre-cutover database, and nothing else in
`rqa.record` ever consults it again after the one run that returns
`already_done=True` for all three tables.

**Disposition units this module honours.**

* **U-DOCS-40** (salvage) — "Shadow-backtest read-only guarantee and
  historical-cutoff enforcement coverage". The responsibility moves, and the
  implementation is rewritten rather than ported: `LegacySource` is read-only by
  construction (three narrow iterators, nothing else), and every migrated row's
  `prev_hash="legacy"` sentinel is the historical-cutoff enforcement — it is what
  permanently excludes migrated content from ever counting as live, verified,
  current-state evidence, no matter how the record is later queried.
* **U-QUEUE-13** (bin) — "closed-PR ingestion into independent, fail-closed
  calibration samples" (`scripts/history.py`, `scripts/shadow.py`). The record
  already holds every fact a calibration sample would, once migrated; there is no
  separate ingestion surface here, and none is added — `history.py` is not
  imported, ported, or replaced by an equivalent inside this package.
* **U-VERDICT-21** (bin) — "Shadow CLI entrypoints (backtest and current-shadow)"
  (`scripts/dispatcher.py`, `scripts/shadow.py`). A CLI is out of this lane's
  scope regardless (§9's E-17 prose line reserves the command surface for #2211);
  there is no shadow-backtest mechanism anywhere in `rqa.record` to entrypoint.
* **U-DOCS-18** (bin) — "Retention purge-with-manifest guarantee documentation".
  This module has no delete, purge, vacuum, or compaction statement either — a
  one-way migration is pure insertion — matching store.py's own "Retention: none"
  (U-DISPATCH-06, the sibling lane's).

**Ordering and idempotency (§6).** `ledger_entries`, then `approval_decisions`,
then `cost_ledger` — deterministic, and independently skippable on retry. A
table's migration is considered already done when any `record_entries` row's
payload already names it as `source_table`; every migrated row, regardless of
target `kind`, carries that marker so a partial retry never re-migrates a table
it already finished, even though only `ledger_entries`' target kind (`legacy`) is
otherwise obligated to have one.

**Sequence numbering.** `(job, seq)` is unique (§5), and a migrated row is never
the parent of anything, so it takes a sequence of its own rather than reusing the
one a later live `append` would choose (§3.1 step 3 already ignores every
`prev_hash="legacy"` row when it reads a job's head). Each job's next free `seq`
is read from the store once per migration run and incremented locally as rows are
inserted for it, so multiple legacy rows for the same job — across one or more of
the three source tables — still land on distinct sequences.
"""

from __future__ import annotations

import json
import sqlite3
from collections.abc import Iterator, Mapping
from dataclasses import dataclass
from typing import Any, Protocol

from rqa.record.hashing import LEGACY_PREV_HASH, canonical_json, compute_hash
from rqa.record.store import (
    StoredEntry,
    ensure_schema,
    entries_for_job,
    insert_entry,
    rows_of_kind_across_jobs,
)

__all__ = ["migrate_legacy", "MigrationSummary", "MigrationTableResult", "LegacySource"]


class LegacySource(Protocol):
    """Read-only view of the pre-cutover tables, for the one-time migration. Not an
    ongoing dependency: nothing else in this part ever reads these tables, and this
    Protocol exists only so `migrate_legacy` can be tested against a fixture instead
    of a real pre-cutover database."""

    def ledger_entries(self) -> Iterator[Mapping[str, Any]]: ...
    def approval_decisions(self) -> Iterator[Mapping[str, Any]]: ...
    def cost_ledger(self) -> Iterator[Mapping[str, Any]]: ...


@dataclass(frozen=True)
class MigrationTableResult:
    migrated: int
    already_done: bool


@dataclass(frozen=True)
class MigrationSummary:
    ledger_entries: MigrationTableResult
    approval_decisions: MigrationTableResult
    cost_ledger: MigrationTableResult


class _SeqAllocator:
    """The next free `seq` for a job, read from the store once and incremented
    locally — so several legacy rows for the same job land on distinct sequences
    within one migration run without a store round-trip per row."""

    def __init__(self, connection: sqlite3.Connection):
        self._connection = connection
        self._next: dict[str, int] = {}

    def take(self, job: str) -> int:
        if job not in self._next:
            existing = entries_for_job(connection=self._connection, job=job)
            self._next[job] = max((entry.seq for entry in existing), default=0) + 1
        seq = self._next[job]
        self._next[job] = seq + 1
        return seq


def _already_migrated(*, connection: sqlite3.Connection, kind: str, source_table: str) -> bool:
    for entry in rows_of_kind_across_jobs(connection=connection, kind=kind):
        try:
            payload = json.loads(entry.payload)
        except ValueError:
            continue
        if isinstance(payload, dict) and payload.get("source_table") == source_table:
            return True
    return False


def _insert_migrated(
    *, connection: sqlite3.Connection, job: str, seq: int, kind: str, at: str, payload: Mapping[str, Any]
) -> None:
    entry_hash = compute_hash(job=job, seq=seq, kind=kind, at=at, payload=payload, prev_hash=LEGACY_PREV_HASH)
    insert_entry(
        connection=connection,
        entry=StoredEntry(
            job=job,
            seq=seq,
            kind=kind,
            at=at,
            payload=canonical_json(payload=payload),
            prev_hash=LEGACY_PREV_HASH,
            hash=entry_hash,
            hmac=None,
            keyed=False,
        ),
    )


def _migrate_ledger_entries(
    *, connection: sqlite3.Connection, source: LegacySource, allocator: _SeqAllocator
) -> MigrationTableResult:
    if _already_migrated(connection=connection, kind="legacy", source_table="ledger_entries"):
        return MigrationTableResult(migrated=0, already_done=True)
    count = 0
    for row in source.ledger_entries():
        job = str(row["job_id"])
        payload = {
            "source_table": "ledger_entries",
            "source_pk": int(row["id"]),
            "legacy_kind": row["kind"],
            "entry_key": row.get("entry_key"),
            "fields": dict(row),
        }
        _insert_migrated(
            connection=connection,
            job=job,
            seq=allocator.take(job),
            kind="legacy",
            at=str(row["recorded_at"]),
            payload=payload,
        )
        count += 1
    return MigrationTableResult(migrated=count, already_done=False)


#: §6: `approval_decisions.status` → `Decision.outcome`. The estate has so far
#: only ever written `status="eligible"` (never a decided terminal status), so
#: this mapping is deliberately conservative: an unrecognised or non-terminal
#: status maps to `None` rather than guessing a disposition that was never
#: actually decided.
_APPROVAL_OUTCOME = {
    "approved": "approved",
    "changes_requested": "changes_requested",
    "denied": "changes_requested",
    "rejected": "changes_requested",
}


def _migrate_approval_decisions(
    *, connection: sqlite3.Connection, source: LegacySource, allocator: _SeqAllocator
) -> MigrationTableResult:
    if _already_migrated(connection=connection, kind="decision", source_table="approval_decisions"):
        return MigrationTableResult(migrated=0, already_done=True)
    count = 0
    for row in source.approval_decisions():
        job_id = row.get("job_id")
        # §6: the synthetic key is the fallback for a NULL job_id specifically —
        # an empty string is a valid, non-NULL TEXT value and keeps its own job_id.
        job = str(job_id) if job_id is not None else f"legacy:approval_decisions:{row['id']}"
        status = row.get("status")
        mode = row.get("mode")
        payload = {
            "source_table": "approval_decisions",
            "source_pk": row["id"],
            "actor": "unknown",
            "basis": f"migrated from approval_decisions: status={status}, mode={mode}",
            "substantiates": None,
            "outcome": _APPROVAL_OUTCOME.get(str(status)),
        }
        _insert_migrated(
            connection=connection,
            job=job,
            seq=allocator.take(job),
            kind="decision",
            at=str(row["created_at"]),
            payload=payload,
        )
        count += 1
    return MigrationTableResult(migrated=count, already_done=False)


def _migrate_cost_ledger(
    *, connection: sqlite3.Connection, source: LegacySource, allocator: _SeqAllocator
) -> MigrationTableResult:
    if _already_migrated(connection=connection, kind="spend", source_table="cost_ledger"):
        return MigrationTableResult(migrated=0, already_done=True)
    count = 0
    for row in source.cost_ledger():
        job = str(row["job_id"])
        payload = {
            "source_table": "cost_ledger",
            "source_pk": int(row["id"]),
            "tokens": int(row.get("tokens", 0)),
            "measured": False,
            "source": "migrated",
            "axis": "unknown",
            "route": {"harness": None, "model": row.get("model"), "provider": row.get("provider_family")},
            "attempt_id": None,
        }
        _insert_migrated(
            connection=connection,
            job=job,
            seq=allocator.take(job),
            kind="spend",
            at=str(row["recorded_at"]),
            payload=payload,
        )
        count += 1
    return MigrationTableResult(migrated=count, already_done=False)


def migrate_legacy(*, connection: sqlite3.Connection, source: LegacySource) -> MigrationSummary:
    """Migrate `ledger_entries`, then `approval_decisions`, then `cost_ledger` —
    deterministic order, each independently skippable on retry (§6)."""
    ensure_schema(connection=connection)
    allocator = _SeqAllocator(connection)
    return MigrationSummary(
        ledger_entries=_migrate_ledger_entries(connection=connection, source=source, allocator=allocator),
        approval_decisions=_migrate_approval_decisions(
            connection=connection, source=source, allocator=allocator
        ),
        cost_ledger=_migrate_cost_ledger(connection=connection, source=source, allocator=allocator),
    )
