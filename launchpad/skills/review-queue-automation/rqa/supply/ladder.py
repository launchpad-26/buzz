"""`route()` — E-06, `code/P-05-reviewer-supply.md` §3.1: candidate filtering, the
subscription-first sort, and the ladder walk that probes through E-24.

**What this answers.** *Which configured route may run next for this obligation, given
what the cursor has already excluded?* — and nothing else. The ladder is the operator's:
every route returned comes out of `snapshot.routes`, in the order they configured it,
with subscriptions first. Nothing here invents, substitutes or repairs a route
(`RQA-FR-024`, `RQA-NFR-009`).

**Every branch returns a value.** Exhaustion — an empty ladder, every candidate filtered,
every candidate cooling down or breaker-open, every probe failed — is one terminal branch
returning `RouteUnavailable(no_fallback=True, tried=...)`. It is a value, never an
exception and never a substitute route, which is what makes a reached bound "a clear, safe,
recoverable non-success state" rather than a false green (`RQA-FR-038`, AC12).

**The returned cursor always excludes the returned route.** So a caller that feeds it back
is guaranteed a different route or `RouteUnavailable`, and the excluded set grows
monotonically: the ladder is finite and the panel loop above it therefore terminates.

**Labels are data.** `may_send_external` is computed once from
`snapshot.external.allowed` and one set-membership test against `facts.pr.labels`. A label
is compared by value and never parsed — a PR cannot talk to the router by writing one
(`RQA-NFR-027`, `RQA-NFR-029`, and the PRD's "PR content is untrusted data, never
instructions").

**Nothing is recorded here** (§6). No record kind exists for "a route was resolved", so
`route()` takes no `RecordWriter` and this module imports none.

`job` and `obligation` are part of E-06's fixed signature and are deliberately unread: the
configured ladder is snapshot-wide, and P-06 calls `route()` once per obligation so that
each obligation walks its own cursor. Narrowing the ladder by obligation would be a policy
decision, and policy lives in the snapshot.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from rqa.contracts import Facts, Job, Route, RouteCursor, RouteUnavailable, Snapshot
from rqa.supply.aliases import alias_of, subscription_of
from rqa.supply.breakers import BreakerStore, utcnow
from rqa.supply.probe import PROBE_COOLDOWN, PROBE_TIMEOUT_SECONDS

if TYPE_CHECKING:  # annotation-only; E-24's Protocol is never needed at runtime
    from rqa.contracts import HarnessProber

__all__ = ["eligible", "route", "route_key", "subscription_first"]


def route_key(candidate: Route) -> str:
    """§3.1 step 5a's `providers` key: `f"{harness}:{provider}:{model}"`.

    Exact-route, not per-family: a cooldown earned by one model's transport failure must
    not retire a sibling model behind the same provider, which is the family breaker's job
    and is scoped differently on purpose (§5).
    """
    return f"{candidate.harness}:{candidate.provider}:{candidate.model}"


def _still_future(moment: datetime | None) -> bool:
    """Is `moment` a live deadline? A missing or already-passed one is not.

    A naive reading is taken as UTC rather than compared against an aware `utcnow()`,
    which would raise. §7's rule — an unparseable or missing deadline is treated as
    expired — is the same decision one step earlier, in the store.
    """
    if moment is None:
        return False
    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=timezone.utc)
    return moment > utcnow()


def eligible(*, snapshot: Snapshot, facts: Facts, cursor: RouteCursor) -> tuple[Route, ...]:
    """§3.1 steps 1-2: the configured candidates this call may consider, in configured order.

    A candidate is kept only if **all** hold: it is not an external route while external
    sending is forbidden; its family is not excluded by the cursor; it is not itself
    excluded by the cursor; and **either** its `(harness, model)` pair is in the alias
    registry **or** it carries a non-empty `command`.

    That last disjunct is `RQA-FR-030`/AC15: a conforming harness RQA ships no alias for
    participates because the operator configured its argv, not because RQA's source was
    edited. Eligibility here is not admission to invocation — `P-06` §3.2 step 2 runs the
    conformance pair against that argv before any PR content reaches it.

    A candidate failing every test is dropped **silently**: never probed, never returned,
    and never replaced by a nearby known route (`RQA-FR-024`, `RQA-NFR-009`).
    """
    # Step 1, computed once. `facts.pr.labels` is read as data and compared for membership
    # only; it is never parsed for instructions (RQA-NFR-027, RQA-NFR-029).
    may_send_external = snapshot.external.allowed and snapshot.external.deny_label not in facts.pr.labels
    return tuple(
        candidate
        for candidate in snapshot.routes
        if not (candidate.external and not may_send_external)
        and candidate.family not in cursor.excluded_families
        and candidate not in cursor.excluded_routes
        and (alias_of(candidate) is not None or bool(candidate.command))
    )


def subscription_first(candidates: tuple[Route, ...]) -> tuple[Route, ...]:
    """§3.1 step 3: a **stable** sort on the registry entry's `subscription` flag, `True`
    before `False`, preserving each tier's configured relative order.

    Subscription-first and never past the configured ladder (U-RESILIENCE-03's salvaged
    ordering mechanism, U-POLICY-14): a metered call is not made while an equally
    configured subscription seat is untried, and no candidate is added, removed or
    re-derived by the ordering.
    """
    return tuple(sorted(candidates, key=lambda candidate: not subscription_of(candidate)))


def route(*, job: Job, obligation: str, snapshot: Snapshot, facts: Facts, cursor: RouteCursor,
          prober: HarnessProber, breakers: BreakerStore) -> tuple[Route, RouteCursor] | RouteUnavailable:
    """E-06, verbatim from `CONTRACTS.md` §9. §3.1's six steps, in order.

    Returns `(route, next_cursor)` for the first configured candidate whose E-24 probe
    succeeds, or `RouteUnavailable(no_fallback=True, tried=...)` when the ladder exhausts.
    `tried` is the probe order and holds exactly the candidates that were probed — a
    candidate skipped at step 5a or 5b is absent from it, because it was never asked.
    """
    del job, obligation  # E-06's signature; see the module docstring.
    tried: list[Route] = []
    for candidate in subscription_first(eligible(snapshot=snapshot, facts=facts, cursor=cursor)):
        # 5a. Still cooling down from a recent probe failure.
        if _still_future(breakers.cooldown(route_key(candidate))):
            continue
        # 5b. This family's breaker is open. An expired deadline is not open: the store
        #     half-opens it on read and writes nothing doing so (§5, U-DISPATCH-05).
        state = breakers.breaker(candidate.family)
        if state.status == "open" and _still_future(state.open_until):
            continue
        # 5c. Only now does the candidate count as tried.
        tried.append(candidate)
        # 5d. E-24. `route()` never inspects why a probe failed.
        if prober.probe(candidate, timeout=PROBE_TIMEOUT_SECONDS):
            breakers.set_cooldown(route_key(candidate), until=None, error="")
            return candidate, RouteCursor(
                excluded_families=cursor.excluded_families,
                excluded_routes=cursor.excluded_routes | frozenset({candidate}),
            )
        breakers.set_cooldown(
            route_key(candidate), until=utcnow() + PROBE_COOLDOWN, error="probe failed"
        )
    # 6. The one terminal branch for every exhaustion shape.
    return RouteUnavailable(no_fallback=True, tried=tuple(tried))
