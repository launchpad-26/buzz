"""`rqa.supply` — P-05, `architecture/code/P-05-reviewer-supply.md`.

Decides *which configured route may run next, and how much of a configured budget may be
spent before it does* — walking only the ladder the operator configured, respecting every
axis inclusively, and telling a measured cost apart from an estimate — never from anything
else.

No other module in RQA imports from `rqa.supply` except through this file. The public
surface is §1's re-export list — `route`, `reserve`, `consumed`, `Route`, `RouteCursor`,
`Reservation`, `Refusal`, `RouteUnavailable`, `Spend` — plus the concrete collaborators
a composition root must construct: `BreakerStore`/`SqliteBreakerStore`,
`SpendStore`/`SqliteSpendStore`, and `SubprocessHarnessProber`/`SubprocessProcessRunner`.
`BreakerState`, `SupplyError`, the alias registry and the `HarnessProber` seam stay
submodule names.

**Why those six are surface.** `route()`, `reserve()` and `consumed()` take their
breaker store, spend store and prober as parameters, and nothing inside `rqa/supply/`
ever constructs one, so something outside this package always must — and the operator
CLI's composition root (#2211) is the first module in RQA whose job is exactly that.
Withholding them while forbidding a reach past `__init__` left no conforming way to
build them: the clause was unfalsifiable only until a composition root existed.

**This file landed in two waves, and §1's surface is complete.** The routing and
liveness-probing half (§3.1 `route()`, §4's E-24 probe, §5's breaker store) re-exported
`route`, `Route`, `RouteCursor` and `RouteUnavailable`. The budget and spend half
(§3.2 `reserve()`, §3.3 `consumed()`) appended `reserve`, `consumed`, `Reservation`,
`Refusal` and `Spend` from `budget.py` and `spend.py`, bringing §1's share of `__all__`
to its full nine-name list. `tests/test_rqa_supply_surface.py` asserts the surface is
exactly one of the two legitimate states, so neither wave could leave it in a partial one.

`Route`, `RouteCursor`, `Reservation`, `Refusal`, `RouteUnavailable` and `Spend` are
`CONTRACTS.md` §5 types imported from
`rqa.contracts`, which is their one definition; re-exporting them here lets a consumer of a
routing answer import the whole answer from one module. An import is not a declaration:
this file defines nothing.
"""

from __future__ import annotations

from rqa.contracts import Refusal, Reservation, Route, RouteCursor, RouteUnavailable, Spend
from rqa.supply.breakers import BreakerStore, SqliteBreakerStore
from rqa.supply.budget import reserve
from rqa.supply.ladder import route
from rqa.supply.probe import SubprocessHarnessProber, SubprocessProcessRunner
from rqa.supply.spend import SpendStore, SqliteSpendStore, consumed

__all__ = [
    "route",
    "reserve",
    "consumed",
    "Route",
    "RouteCursor",
    "Reservation",
    "Refusal",
    "RouteUnavailable",
    "Spend",
    "BreakerStore",
    "SqliteBreakerStore",
    "SpendStore",
    "SqliteSpendStore",
    "SubprocessHarnessProber",
    "SubprocessProcessRunner",
]
