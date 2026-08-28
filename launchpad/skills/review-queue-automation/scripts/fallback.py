"""Provider-diverse fallback recipes for review-queue-automation.

Every strategy declares a `model_route` (see `strategies.py`). This module turns
that declaration into an ordered ladder of first / second / final candidate
tiers, so the order candidates are tried is a property of the review strategy
rather than of whatever order an operator happened to type into config.

Two rules this module exists to enforce:

1. **Subscription routes lead.** Claude and Codex subscriptions are already paid
   for, so a metered OpenRouter call is never made while an equally qualified
   subscription route is available.
2. **Ordering never lowers assurance.** A recipe only REORDERS the candidates a
   caller already deemed qualified. It cannot introduce a candidate, relax a
   capability floor, or substitute a cheaper tier for a required one — an empty
   tier stays empty and the panel degrades instead.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

#: Which ladder tier a candidate belongs to, derived from its runner.
_RUNNER_TIER = {"claude": "claude", "codex": "codex", "omp": "openrouter"}

#: Tiers in their canonical subscription-first order.
TIERS = ("claude", "codex", "openrouter", "economical")


@dataclass(frozen=True)
class Recipe:
    """An ordered candidate ladder: `tiers[0]` is first choice, `tiers[-1]` final."""

    name: str
    tiers: tuple[str, ...]

    def position(self, tier: str) -> int:
        """Rank of `tier`; unknown tiers sort last rather than raising."""
        try:
            return self.tiers.index(tier)
        except ValueError:
            return len(self.tiers)


#: `preferred` and `diverse` both lead with subscriptions. They differ in the
#: independence the panel requires of them, which the panel enforces separately
#: by refusing to fill two slots from one provider family.
#:
#: `fallback` belongs to strategies that run as a SECOND opinion (e.g. debate).
#: Leading those with the subscription route that already produced the first view
#: would add cost without adding independence, so the diverse tier leads instead.
#:
#: `economical` is cost-led by definition.
RECIPES: dict[str, Recipe] = {
    "preferred": Recipe("preferred", ("claude", "codex", "openrouter", "economical")),
    "diverse": Recipe("diverse", ("claude", "codex", "openrouter", "economical")),
    "fallback": Recipe("fallback", ("openrouter", "claude", "codex", "economical")),
    "economical": Recipe("economical", ("economical", "openrouter", "codex", "claude")),
}

DEFAULT_RECIPE = RECIPES["preferred"]


def tier_of(entry: dict[str, Any]) -> str:
    """Classify one candidate into a ladder tier.

    An OpenRouter candidate explicitly marked `economy` capability is a
    last-resort tier, not a peer of the provider-diverse fallbacks.
    """
    tier = _RUNNER_TIER.get((entry.get("runner") or "").strip(), "openrouter")
    if tier == "openrouter" and (entry.get("capability") or "") == "economy":
        return "economical"
    return tier


def recipe_for(strategy_name: str | None) -> Recipe:
    """Return the recipe a strategy declares, defaulting to subscription-first."""
    if not strategy_name:
        return DEFAULT_RECIPE
    from strategies import STRATEGY_BY_NAME

    strategy = STRATEGY_BY_NAME.get(strategy_name)
    if strategy is None:
        return DEFAULT_RECIPE
    return RECIPES.get(strategy.model_route, DEFAULT_RECIPE)


def order_candidates(
    entries: list[dict[str, Any]], recipe: Recipe | None = None
) -> list[dict[str, Any]]:
    """Order candidates by the recipe's ladder, preserving operator order per tier.

    The sort is stable, so two candidates in the same tier keep the relative order
    the operator configured. No candidate is added or removed.
    """
    active = recipe or DEFAULT_RECIPE
    return sorted(entries, key=lambda entry: active.position(tier_of(entry)))
