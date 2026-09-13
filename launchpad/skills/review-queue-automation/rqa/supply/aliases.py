"""The closed alias registry — `code/P-05-reviewer-supply.md` §1: every recognised
`(harness, model)` pair and its subscription tier (U-POLICY-11, U-POLICY-14).

**Closed, hand-maintained, and it never guesses.** A pair is recognised or it is not;
there is no normalisation of near-misses, no "latest" alias and no nearest-match. That is
the property `RQA-FR-032` needs: the exact provider path is nameable *before* anything is
sent to it, and an alias that resolved to whatever a provider currently calls "latest"
would be nameable only afterwards. It is also half of `RQA-NFR-009`/`RQA-FR-024`: a
configured pair this table does not know is dropped by `ladder.eligible` unless the
operator declared its `command`, never replaced with a nearby known route.

**Absence from this table is not a veto** (`RQA-FR-030`, AC15). §3.1 step 2 admits a
candidate that is absent here but carries a non-empty `Route.command`: the operator
configured that harness's argv, so it participates without an edit to RQA's source. The
registry's remaining job for such a route is the subscription tier, and an unregistered
pair has none — `subscription_of` reports `False`, so it sorts with the metered tier and
never displaces a configured subscription route. It is never *rejected* for that.

**Content.** The subscription rows are the incumbent's closed alias table
(`scripts/model_registry.py:27-33`), keyed on the `(harness, model)` pair `Route` actually
carries rather than on the alias name the incumbent used. The metered rows are the
documented default fallback ladder (`references/model-fallbacks.md`, U-DOCS-07) with its
exact OpenRouter slugs, deliberately not `latest` aliases. `subscription=True` means the
route runs against a seat RQA already pays for, so the subscription-first sort in
`ladder.py` prefers it over any metered call (U-RESILIENCE-03's salvaged ordering
mechanism, U-POLICY-10).

This module is pure data and two lookups. It probes nothing and invokes nothing.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from rqa.contracts import Route

__all__ = ["ALIASES", "Alias", "alias_of", "subscription_of"]


@dataclass(frozen=True)
class Alias:
    harness: str
    model: str
    subscription: bool  # True: a seat already paid for; False: a metered call


def _entries(*rows: Alias) -> Mapping[tuple[str, str], Alias]:
    return {(row.harness, row.model): row for row in rows}


#: The whole registry. `Route.provider` and `Route.family` stay the operator's declaration
#: — this table answers only "is this pair one RQA ships an adapter for, and is it a
#: subscription seat?", which is what §3.1 steps 2 and 3 ask of it.
ALIASES: Mapping[tuple[str, str], Alias] = _entries(
    # Subscription seats — `scripts/model_registry.py:27-33`, carried unchanged.
    Alias("claude", "claude-sonnet-4-5", True),
    Alias("claude", "claude-opus-4-5", True),
    Alias("claude", "claude-fable-1", True),
    Alias("codex", "gpt-5.6-luna", True),
    Alias("codex", "gpt-5.6-terra", True),
    Alias("codex", "gpt-5.6-sol", True),
    # Metered fallbacks — `references/model-fallbacks.md`, exact slugs.
    Alias("omp", "z-ai/glm-5.3-flash", False),
    Alias("omp", "deepseek/deepseek-v4-flash-0731", False),
    Alias("omp", "qwen/qwen3.8-flash", False),
    Alias("omp", "google/gemini-3.7-flash", False),
)


def alias_of(candidate: Route) -> Alias | None:
    """The registry entry for `candidate`'s `(harness, model)` pair, or `None`.

    `None` is the only "not recognised" answer; nothing here raises, and nothing here
    returns a different pair's entry.
    """
    return ALIASES.get((candidate.harness, candidate.model))


def subscription_of(candidate: Route) -> bool:
    """`candidate`'s subscription tier: `True` only for a registered subscription seat.

    An unregistered pair — one admitted by §3.1 step 2's `command` disjunct — has no tier,
    and `False` places it with the metered candidates in the step-3 sort. That is the
    conservative reading of "subscription-first": an operator-declared command is never
    assumed to be free.
    """
    entry = alias_of(candidate)
    return entry is not None and entry.subscription
