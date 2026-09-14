#!/usr/bin/env python3
"""`rqa.supply.aliases` — `code/P-05-reviewer-supply.md` §1's closed alias registry
(U-POLICY-11), and the ladder helpers that read it (§3.1 steps 2 and 3).

No pytest: every `test_*` function here takes no arguments, per `tests/run_all.py`.

The registry is pure data: these tests read it and never invoke or probe anything.
"""

from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from rqa.contracts import Route, RouteCursor  # noqa: E402
from rqa.supply.aliases import ALIASES, Alias, alias_of, subscription_of  # noqa: E402
from rqa.supply.ladder import eligible, route_key, subscription_first  # noqa: E402

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from test_rqa_supply_route import (  # noqa: E402
    DECLARED,
    EMPTY_CURSOR,
    METERED,
    PRIMARY,
    UNKNOWN,
    make_facts,
    make_snapshot,
)


# -- the registry ----------------------------------------------------------------


def test_every_entry_is_keyed_by_its_own_harness_and_model_pair() -> None:
    for key, entry in ALIASES.items():
        assert isinstance(entry, Alias)
        assert key == (entry.harness, entry.model)


def test_the_registry_carries_both_tiers() -> None:
    tiers = {entry.subscription for entry in ALIASES.values()}
    assert tiers == {True, False}


def test_a_registered_subscription_seat_reports_its_tier() -> None:
    assert alias_of(PRIMARY) is not None
    assert subscription_of(PRIMARY) is True


def test_a_registered_metered_route_is_recognised_but_is_not_a_subscription() -> None:
    """Membership admits it at step 2; its tier places it after every subscription seat at
    step 3. The two questions are separate."""
    assert alias_of(METERED) is not None
    assert subscription_of(METERED) is False


def test_an_unregistered_pair_resolves_to_nothing_and_nothing_near_it() -> None:
    """U-POLICY-11, kept: the table is closed and `resolve` never guesses. There is no
    normalisation, no "latest" alias and no nearest match (`RQA-NFR-009`)."""
    assert alias_of(UNKNOWN) is None
    for near_miss in (
        Route(harness="claude", model="claude-sonnet", provider="anthropic", family="anthropic", external=False),
        Route(harness="Claude", model="claude-sonnet-4-5", provider="anthropic", family="anthropic", external=False),
        Route(harness="claude", model="CLAUDE-SONNET-4-5", provider="anthropic", family="anthropic", external=False),
    ):
        assert alias_of(near_miss) is None, near_miss


def test_the_registry_is_not_consulted_for_provider_or_family() -> None:
    """`Route.provider` and `Route.family` stay the operator's declaration: a registered
    pair configured under a different family is still that family's route, because the
    family is what keeps the ladder provider-diverse."""
    relabelled = Route(harness="claude", model="claude-sonnet-4-5", provider="proxy",
                       family="proxy", external=False)
    assert alias_of(relabelled) is not None
    assert relabelled.family == "proxy"


def test_an_unregistered_pair_carrying_a_command_has_no_subscription_tier() -> None:
    """An operator-declared command is never assumed to be a seat RQA already pays for, so
    it sorts with the metered tier — admitted, never promoted."""
    assert alias_of(DECLARED) is None
    assert subscription_of(DECLARED) is False


# -- §3.1 steps 2 and 3, directly -------------------------------------------------


def test_eligible_keeps_the_configured_order() -> None:
    snapshot = make_snapshot(METERED, PRIMARY, DECLARED)
    assert eligible(snapshot=snapshot, facts=make_facts(), cursor=EMPTY_CURSOR) == (
        METERED, PRIMARY, DECLARED
    )


def test_eligible_drops_an_unregistered_pair_with_no_command() -> None:
    snapshot = make_snapshot(UNKNOWN, PRIMARY)
    assert eligible(snapshot=snapshot, facts=make_facts(), cursor=EMPTY_CURSOR) == (PRIMARY,)


def test_eligible_admits_an_unregistered_pair_with_a_command() -> None:
    snapshot = make_snapshot(DECLARED)
    assert eligible(snapshot=snapshot, facts=make_facts(), cursor=EMPTY_CURSOR) == (DECLARED,)


def test_eligible_admits_nothing_the_operator_did_not_configure() -> None:
    snapshot = make_snapshot(PRIMARY)
    assert set(eligible(snapshot=snapshot, facts=make_facts(), cursor=EMPTY_CURSOR)) <= set(
        snapshot.routes
    )


def test_eligible_honours_both_cursor_exclusions_at_once() -> None:
    snapshot = make_snapshot(PRIMARY, METERED, DECLARED)
    cursor = RouteCursor(excluded_families=frozenset({METERED.family}),
                         excluded_routes=frozenset({PRIMARY}))
    assert eligible(snapshot=snapshot, facts=make_facts(), cursor=cursor) == (DECLARED,)


def test_the_subscription_sort_is_stable_and_adds_nothing() -> None:
    candidates = (METERED, DECLARED, PRIMARY)
    sorted_candidates = subscription_first(candidates)
    assert sorted_candidates == (PRIMARY, METERED, DECLARED)
    assert set(sorted_candidates) == set(candidates)


def test_route_key_is_harness_provider_model() -> None:
    assert route_key(PRIMARY) == "claude:anthropic:claude-sonnet-4-5"


def test_route_key_separates_two_models_of_one_provider() -> None:
    """§5's scoping: the cooldown is exact-route, so one model's transport failure never
    retires its sibling behind the same provider."""
    sibling = Route(harness="claude", model="claude-opus-4-5", provider="anthropic",
                    family="anthropic", external=False)
    assert route_key(sibling) != route_key(PRIMARY)
