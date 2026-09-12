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

**This file is landed in two waves, and it currently carries the routing half.** The
routing and liveness-probing half (§3.1 `route()`, §4's E-24 probe, §5's breaker store)
re-exports `route`, `Route`, `RouteCursor` and `RouteUnavailable` below. The budget and
spend half (§3.2 `reserve()`, §3.3 `consumed()`) appends `reserve`, `consumed`,
`Reservation`, `Refusal` and `Spend` when `budget.py` and `spend.py` land; naming them here
before those modules exist would make the package unimportable. `tests/
test_rqa_supply_surface.py` asserts the surface is exactly one of the two legitimate
states, so neither wave can leave it in a partial one.

`Route`, `RouteCursor` and `RouteUnavailable` are `CONTRACTS.md` §5 types imported from
`rqa.contracts`, which is their one definition; re-exporting them here lets a consumer of a
routing answer import the whole answer from one module. An import is not a declaration:
this file defines nothing.
"""

from __future__ import annotations

from rqa.contracts import Route, RouteCursor, RouteUnavailable
from rqa.supply.ladder import route

__all__ = ["route", "Route", "RouteCursor", "RouteUnavailable"]
