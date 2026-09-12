"""`rqa.supply` — P-05, `architecture/code/P-05-reviewer-supply.md`.

Decides *which configured route may run next, and how much of a configured budget may be
spent before it does* — walking only the ladder the operator configured, respecting every
axis inclusively, and telling a measured cost apart from an estimate — never from anything
else.

No other module in RQA imports from `rqa.supply` except through this file. The public
surface is exactly §1's re-export list: `route`, `reserve`, `consumed`, `Route`,
`RouteCursor`, `Reservation`, `Refusal`, `RouteUnavailable`, `Spend`. `BreakerStore`,
`SpendStore`, `BreakerState`, `SupplyError`, the alias registry and the probe adapter stay
submodule names, the way `rqa.policy` keeps `SnapshotStore` out of its package surface even
though E-03's signature mentions the Protocol.

**This file landed in two waves, and the surface is now complete.** The routing and
liveness-probing half (§3.1 `route()`, §4's E-24 probe, §5's breaker store) re-exports
`route`, `Route`, `RouteCursor` and `RouteUnavailable`. The budget and spend half
(§3.2 `reserve()`, §3.3 `consumed()`) appends `reserve`, `consumed`, `Reservation`,
`Refusal` and `Spend` from `budget.py` and `spend.py`, bringing `__all__` to §1's full
nine-name list. `tests/test_rqa_supply_surface.py` asserts the surface is exactly one
of the two legitimate states, so neither wave can leave it in a partial one.

`Route`, `RouteCursor`, `Reservation`, `Refusal`, `RouteUnavailable` and `Spend` are
`CONTRACTS.md` §5 types imported from
`rqa.contracts`, which is their one definition; re-exporting them here lets a consumer of a
routing answer import the whole answer from one module. An import is not a declaration:
this file defines nothing.
"""

from __future__ import annotations

from rqa.contracts import Refusal, Reservation, Route, RouteCursor, RouteUnavailable, Spend
from rqa.supply.budget import reserve
from rqa.supply.ladder import route
from rqa.supply.spend import consumed

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
]
