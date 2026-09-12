"""The breaker store — `code/P-05-reviewer-supply.md` §5, `container.md` §5's `breakers`
row: the `providers` cooldown table and the `circuit_breakers` family breaker
(U-RESILIENCE-02).

Two tables, carried unchanged in shape from the incumbent DDL in `scripts/common.py`,
scoped differently on purpose. `providers` is a short, exact-route cooldown driven by
probe outcomes — one row per `f"{harness}:{provider}:{model}"`. `circuit_breakers` is a
coarser, escalating per-family breaker driven by attempt outcomes. Keying the cooldown on
the exact route and the breaker on the family is what keeps one model's transport failure
from retiring its provider while a provider-scoped outage still retires every model behind
it (U-VERDICT-09's reasoning, carried).

`BreakerStore` is declared **here**, not in `rqa/edges.py`: `CONTRACTS.md` §9 names it in
E-06's and E-15's signatures and `rqa.edges` keeps it an empty Protocol whose docstring
says its shape is P-05's to state. This is that statement, and it is the same arrangement
`rqa/authority/store.py` makes for `CapabilityStore` and `rqa/policy/store.py` makes for
`SnapshotStore`.

`SupplyError` is declared here too, because §2 declares it in this module's code block.
It is not in §1's re-export list, so it stays a submodule name.

**No reset, by design** (§7, U-DISPATCH-05 `bin`). Nothing here clears a cooldown or a
breaker on demand. The only ways a scope becomes usable again are a passing probe
(`set_cooldown(key, until=None, ...)`), a `consumed()` outcome (`record_success`), or the
stored deadline passing. Deadlines are therefore read fresh on every call and never
written back by a read.

**Half-open on read, and never a write on read.** `breaker()` re-reads the row every time
and reports an `open` row whose `open_until` has passed as usable again, without touching
the database: the returned state is `closed` with the failure count preserved, so one more
`record_failure` re-opens it immediately while a `record_success` closes it for good.
`BreakerState.status` is `CONTRACTS.md`-free (§2, P-05-internal) and its `Literal` admits
only `closed` and `open`, so `closed`-with-failures is the half-open state's
representation, not a third status. A missing or unparseable deadline on an `open` row is
treated as expired for the same reason the incumbent did (`scripts/budget.py:270-276`): a
bad timestamp must not pin a provider family out of service forever.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Literal, Protocol

__all__ = [
    "BREAKER_COOLDOWN",
    "FAILURE_THRESHOLD",
    "BreakerState",
    "BreakerStore",
    "SqliteBreakerStore",
    "SupplyError",
    "ensure_schema",
    "utcnow",
]

#: §5, verbatim: consecutive PROVIDER_TERMINAL failures before a family opens.
FAILURE_THRESHOLD: int = 3
#: §5, verbatim: matches the incumbent's default exactly (carried unchanged).
BREAKER_COOLDOWN = timedelta(seconds=900)


class SupplyError(Exception):
    """Programming or storage fault inside P-05 — a SpendStore/BreakerStore read or write
    that itself fails, or an internal invariant violation. Never raised for a policy,
    availability or budget reason; those are shared-contract values. Not caught by
    Lifecycle's containment boundary."""


@dataclass(frozen=True)
class BreakerState:
    scope: str  # a provider family, e.g. "anthropic"
    failures: int
    status: Literal["closed", "open"]
    open_until: datetime | None  # set only while status == "open"


class BreakerStore(Protocol):
    def cooldown(self, route_key: str) -> datetime | None: ...
    def set_cooldown(self, route_key: str, *, until: datetime | None, error: str) -> None: ...
    def breaker(self, scope: str) -> BreakerState: ...  # half-opens an expired "open" row on
    #                                                     # read; never writes on read (U-DISPATCH-05)
    def record_failure(self, scope: str, error: str) -> BreakerState: ...  # opens at FAILURE_THRESHOLD
    def record_success(self, scope: str) -> BreakerState: ...  # failures=0, status=closed


_SCHEMA = """
CREATE TABLE IF NOT EXISTS providers (
  key               TEXT PRIMARY KEY,
  unavailable_until TEXT,
  last_error        TEXT,
  updated_at        TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS circuit_breakers (
  scope       TEXT PRIMARY KEY,
  failures    INTEGER NOT NULL DEFAULT 0,
  status      TEXT NOT NULL DEFAULT 'closed',
  open_until  TEXT,
  last_error  TEXT,
  updated_at  TEXT NOT NULL
);
"""

#: Column widths are bounded so a provider's error text cannot grow a row without limit;
#: the incumbent truncated at the same points (`scripts/budget.py:298`).
_ERROR_LIMIT = 300


def utcnow() -> datetime:
    """The one clock this package reads, mirroring `rqa/record/writer.py`'s."""
    return datetime.now(timezone.utc)


def ensure_schema(*, connection: sqlite3.Connection) -> None:
    """§5's DDL, idempotent, in the shape the incumbent already uses."""
    connection.executescript(_SCHEMA)


def _stamp(moment: datetime) -> str:
    """ISO-8601 UTC. A naive reading is taken as UTC rather than as local time, so a
    deadline written on a machine in another zone is not silently moved."""
    if moment.tzinfo is None:
        return moment.replace(tzinfo=timezone.utc).isoformat()
    return moment.astimezone(timezone.utc).isoformat()


def _parse(value: object) -> datetime | None:
    """A stored deadline, or `None` when it is absent, empty or unparseable.

    §7: "An unparseable or missing deadline on an `open`/cooling-down row is treated as
    expired, never as pinned open forever." `None` is that treatment — every caller reads
    it as "no live deadline".
    """
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        moment = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    except ValueError:
        return None
    return moment if moment.tzinfo is not None else moment.replace(tzinfo=timezone.utc)


class SqliteBreakerStore:
    """`BreakerStore` over one caller-owned `sqlite3.Connection`.

    Writes commit, deliberately. Each scheduled tick is a separate process, so a cooldown
    held only in memory would be discarded between jobs and the dead route re-probed on
    every one — the failure mode U-POLICY-13 records for the in-process alternative.
    """

    def __init__(self, *, connection: sqlite3.Connection) -> None:
        self._connection = connection
        ensure_schema(connection=connection)

    # -- `providers`: the exact-route probe cooldown ---------------------------

    def cooldown(self, route_key: str) -> datetime | None:
        row = self._one(
            "SELECT unavailable_until FROM providers WHERE key=?",
            (route_key,),
            what=f"cooldown for route {route_key!r}",
        )
        return _parse(row[0]) if row is not None else None

    def set_cooldown(self, route_key: str, *, until: datetime | None, error: str) -> None:
        self._write(
            "INSERT INTO providers(key,unavailable_until,last_error,updated_at) "
            "VALUES(?,?,?,?) ON CONFLICT(key) DO UPDATE SET "
            "unavailable_until=excluded.unavailable_until,last_error=excluded.last_error,"
            "updated_at=excluded.updated_at",
            (route_key, _stamp(until) if until is not None else "", error[:_ERROR_LIMIT], _stamp(utcnow())),
            what=f"cooldown for route {route_key!r}",
        )

    # -- `circuit_breakers`: the per-family breaker ----------------------------

    def breaker(self, scope: str) -> BreakerState:
        row = self._one(
            "SELECT failures,status,open_until FROM circuit_breakers WHERE scope=?",
            (scope,),
            what=f"breaker for scope {scope!r}",
        )
        if row is None:
            return BreakerState(scope=scope, failures=0, status="closed", open_until=None)
        failures = int(row[0] or 0)
        open_until = _parse(row[2])
        if row[1] == "open" and open_until is not None and open_until > utcnow():
            return BreakerState(scope=scope, failures=failures, status="open", open_until=open_until)
        # Half-open: an expired, missing or unparseable deadline reads back as usable
        # again, with the failure count intact. No write happens here (§5, U-DISPATCH-05).
        return BreakerState(scope=scope, failures=failures, status="closed", open_until=None)

    def record_failure(self, scope: str, error: str) -> BreakerState:
        current = self._one(
            "SELECT failures FROM circuit_breakers WHERE scope=?",
            (scope,),
            what=f"breaker for scope {scope!r}",
        )
        failures = int(current[0] or 0) + 1 if current is not None else 1
        opened = failures >= FAILURE_THRESHOLD
        state = BreakerState(
            scope=scope,
            failures=failures,
            status="open" if opened else "closed",
            open_until=utcnow() + BREAKER_COOLDOWN if opened else None,
        )
        return self._put(state, error=error)

    def record_success(self, scope: str) -> BreakerState:
        return self._put(
            BreakerState(scope=scope, failures=0, status="closed", open_until=None), error=""
        )

    # -- storage ---------------------------------------------------------------

    def _put(self, state: BreakerState, *, error: str) -> BreakerState:
        self._write(
            "INSERT INTO circuit_breakers(scope,failures,status,open_until,last_error,updated_at) "
            "VALUES(?,?,?,?,?,?) ON CONFLICT(scope) DO UPDATE SET failures=excluded.failures,"
            "status=excluded.status,open_until=excluded.open_until,last_error=excluded.last_error,"
            "updated_at=excluded.updated_at",
            (
                state.scope,
                state.failures,
                state.status,
                _stamp(state.open_until) if state.open_until is not None else "",
                error[:_ERROR_LIMIT],
                _stamp(utcnow()),
            ),
            what=f"breaker for scope {state.scope!r}",
        )
        return state

    def _one(self, sql: str, parameters: tuple[object, ...], *, what: str) -> tuple | None:
        try:
            return self._connection.execute(sql, parameters).fetchone()
        except sqlite3.Error as exc:
            raise SupplyError(f"breaker store could not read the {what}") from exc

    def _write(self, sql: str, parameters: tuple[object, ...], *, what: str) -> None:
        try:
            self._connection.execute(sql, parameters)
            self._connection.commit()
        except sqlite3.Error as exc:
            raise SupplyError(f"breaker store could not write the {what}") from exc
