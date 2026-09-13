"""`consumed()` and the `spend` store — E-15, `code/P-05-reviewer-supply.md` §3.3, §5
and §6: measured cost told apart from an estimate, written down before anything local
is updated.

**Step 1 is the entire measured/estimated decision** (RQA-FR-021, U-DISPATCH-13):
`measured = reading is not None`. An exposed actual reading always wins; the
reservation's token ceiling stands in only when none was exposed, and is then always
marked estimated — never conflated with a measurement. The test is `is not None`,
never truthiness: a reading of `0` is a real measurement of zero, not a missing one.
This is the provenance AC11 turns on — the legacy estate charged the strategy's
*declared* budget as though it were a cost, and no adapter parsed actual usage.

**The durable record comes first.** §3.3 step 2 appends the `spend` entry before any
local bookkeeping, and `AppendFailed` propagates uncaught: no local counter is updated
and no breaker is touched for an attempt whose cost the durable record does not hold
(E-13's contract). The `spend` kind is the only record entry P-05 writes, and this
module is the only place in `rqa/` that writes it for a review (§6; the one ruled
exception is P-12's one-time legacy migration in `rqa/record/migrate.py`).

**The store is a flat, append-only projection** — one row per `consumed()` call,
mirroring the record entry it is written alongside. It exists so the three budget axes
can be summed locally without re-scanning the hash-chained record on every `reserve()`
call. Written only by P-05, read only by P-05 (container.md §5: readers `-`).

**`SpendStore` is declared here**, not in `rqa/edges.py`: `CONTRACTS.md` §9 names it
in E-06's and E-15's signatures and keeps it an empty Protocol whose docstring says its
shape is P-05's to state. This is that statement — the same arrangement
`rqa/supply/breakers.py` makes for `BreakerStore` and `rqa/authority/store.py` for
`CapabilityStore`.

A reservation is never written as a spend (§7): nothing here records "a reservation
was granted or refused", and `reserve()` (`budget.py`) has no writer to call. Only
what was actually consumed — measured or estimated — is recorded.
"""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Protocol

from rqa.contracts import AttemptFailure, Spend
from rqa.supply.breakers import SupplyError, utcnow

if TYPE_CHECKING:  # annotation-only; resolved by type checkers, never at import
    from rqa.contracts import Attempt, Job, RecordWriter, Reservation
    from rqa.supply.breakers import BreakerStore

__all__ = ["SpendStore", "SqliteSpendStore", "consumed", "ensure_schema"]


class SpendStore(Protocol):
    def pr_total(self, repo: str, number: int) -> int: ...
    def repo_total_since(self, repo: str, since: datetime) -> int: ...
    def model_total_since(self, model: str, since: datetime) -> int: ...
    def append(self, *, job_id: str, repo: str, number: int, model: str, tokens: int,
               measured: bool, source: str, recorded_at: datetime) -> None: ...


#: §5's DDL, verbatim: the flat projection and the three indexes that serve the three
#: budget axes (`per_pr_tokens`, `per_repo_daily_tokens`, `per_model_daily_tokens`).
_SCHEMA = """
CREATE TABLE IF NOT EXISTS spend (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  job_id      TEXT NOT NULL,
  repo        TEXT NOT NULL,
  number      INTEGER NOT NULL,
  model       TEXT NOT NULL,
  tokens      INTEGER NOT NULL,
  measured    INTEGER NOT NULL,
  source      TEXT NOT NULL,
  recorded_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS spend_by_pr        ON spend(repo, number);
CREATE INDEX IF NOT EXISTS spend_by_repo_time ON spend(repo, recorded_at);
CREATE INDEX IF NOT EXISTS spend_by_model_time ON spend(model, recorded_at);
"""


def ensure_schema(*, connection: sqlite3.Connection) -> None:
    """§5's DDL, idempotent, mirroring `rqa/supply/breakers.py`'s arrangement."""
    connection.executescript(_SCHEMA)


def _stamp(moment: datetime) -> str:
    """ISO-8601 UTC with microseconds — one uniform width, so the `recorded_at` string
    comparison the two `*_total_since` queries make is exactly the chronological one.
    A naive reading is taken as UTC rather than as local time, so a row written on a
    machine in another zone is not silently moved."""
    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=timezone.utc)
    return moment.astimezone(timezone.utc).isoformat(timespec="microseconds")


class SqliteSpendStore:
    """`SpendStore` over one caller-owned `sqlite3.Connection`.

    Writes commit, deliberately — the same reasoning as `SqliteBreakerStore`: each
    scheduled tick is a separate process, and a spend held only in memory would let
    the next `reserve()` re-grant tokens the previous job already burned.

    Every storage fault is `SupplyError` (§2): a store that cannot answer a counter
    query is a programming or storage fault, never a budget decision, and never a
    `Refusal`. The message names the operation and its scope — never a value the
    store was handed (RQA-NFR-025).
    """

    def __init__(self, *, connection: sqlite3.Connection) -> None:
        self._connection = connection
        ensure_schema(connection=connection)

    def pr_total(self, repo: str, number: int) -> int:
        return self._sum(
            "SELECT COALESCE(SUM(tokens),0) FROM spend WHERE repo=? AND number=?",
            (repo, number),
            what=f"pr total for {repo!r}#{number}",
        )

    def repo_total_since(self, repo: str, since: datetime) -> int:
        return self._sum(
            "SELECT COALESCE(SUM(tokens),0) FROM spend WHERE repo=? AND recorded_at>=?",
            (repo, _stamp(since)),
            what=f"repo total for {repo!r}",
        )

    def model_total_since(self, model: str, since: datetime) -> int:
        return self._sum(
            "SELECT COALESCE(SUM(tokens),0) FROM spend WHERE model=? AND recorded_at>=?",
            (model, _stamp(since)),
            what=f"model total for {model!r}",
        )

    def append(self, *, job_id: str, repo: str, number: int, model: str, tokens: int,
               measured: bool, source: str, recorded_at: datetime) -> None:
        try:
            self._connection.execute(
                "INSERT INTO spend(job_id,repo,number,model,tokens,measured,source,recorded_at) "
                "VALUES(?,?,?,?,?,?,?,?)",
                (job_id, repo, number, model, tokens, int(measured), source, _stamp(recorded_at)),
            )
            self._connection.commit()
        except sqlite3.Error as exc:
            raise SupplyError(f"spend store could not append the row for job {job_id!r}") from exc

    def _sum(self, sql: str, parameters: tuple[object, ...], *, what: str) -> int:
        try:
            row = self._connection.execute(sql, parameters).fetchone()
        except sqlite3.Error as exc:
            raise SupplyError(f"spend store could not read the {what}") from exc
        return int(row[0] or 0)


def consumed(*, job: Job, attempt: Attempt, reading: int | None, reservation: Reservation,
             record: RecordWriter, spend: SpendStore, breakers: BreakerStore) -> Spend:
    """E-15, verbatim from `CONTRACTS.md` §9. §3.3's five steps, in order.

    Every branch returns or (step 2 only) raises; that raise — `AppendFailed` — is the
    one exception this contract names as always propagating. Nothing after a failed
    append runs: no local counter, no breaker call, for an attempt whose cost the
    durable record does not hold.
    """
    # 1. The whole measured/estimated decision (RQA-FR-021, U-DISPATCH-13). The test
    #    is `is not None`, never truthiness: `reading=0` is a measurement of zero.
    measured = reading is not None
    tokens = reading if reading is not None else reservation.tokens
    source = "harness" if measured else "reservation"
    # 2. The authoritative append, first, with exactly §6's nine payload keys.
    #    `AppendFailed` propagates uncaught.
    record.append(job.id, kind="spend", payload={
        "tokens": tokens,
        "measured": measured,
        "source": source,
        "model": attempt.route.model,
        "provider": attempt.route.provider,
        "repo": job.repo,
        "number": job.number,
        "attempt_id": attempt.id,
        "reservation_id": reservation.id,
    })
    # 3. The local projection, only after the authoritative append succeeded.
    spend.append(job_id=job.id, repo=job.repo, number=job.number,
                 model=attempt.route.model, tokens=tokens, measured=measured,
                 source=source, recorded_at=utcnow())
    # 4. The family breaker, from the outcome's three-way classification. The `Verdict`
    #    case is inspected only to distinguish succeeded from failed — never opened
    #    further (§7) — and the third branch is a real branch: neither a TRANSIENT nor
    #    a CANDIDATE_TERMINAL failure reflects on the *provider's* health, so neither
    #    touches the breaker at all.
    outcome = attempt.outcome
    if isinstance(outcome, AttemptFailure):
        if outcome.kind == "PROVIDER_TERMINAL":
            breakers.record_failure(attempt.route.family, outcome.detail)
    else:
        breakers.record_success(attempt.route.family)
    # 5.
    return Spend(tokens=tokens, measured=measured, source=source)
