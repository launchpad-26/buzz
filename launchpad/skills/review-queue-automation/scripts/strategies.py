"""Named reasoning strategies for review-queue-automation.

Each strategy is a data record describing how participants are composed and how
their outputs are aggregated, so selection and degradation are deterministic and
testable. The strategy is chosen from review signals (risk, complexity, required
independence, presence of a prior disagreement), and the selection reason is
recorded.

Strategies never count failed/timed-out/invalid participants as agreement; the
aggregator drops any participant whose output is missing or invalid.

EVERY field declared on `Strategy` has a runtime consumer, and
`tests/test_strategy_metadata.py` fails if one loses it. Declared-but-unread
metadata reads as authoritative while changing nothing, which is worse than no
metadata at all; six such fields had already accumulated here. The current
consumers are:

    name                   selection + attempt log + `fallback.recipe_for`
    roles                  `panel._mode_participants` slot role labels
    aggregation            `modes.mode_for` -> execution mode
    disagreement_handling  `panel.run_panel` when counted signals diverge
    output_schema          `panel.run_panel` schema guard (fail-closed)
    budget_tokens          `budget.reserve` pre-spend reservation
    timeout_seconds        `panel.run_panel` per-strategy runtime ceiling
    model_route            `fallback.recipe_for` -> candidate ordering
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

VALID_AGGREGATIONS = frozenset(
    {
        "single", "consensus", "majority", "unanimous", "panel_adjudicated",
        "sequenced", "checklist_score", "hypothesis_register", "calibrated",
    }
)


@dataclass(frozen=True)
class Strategy:
    name: str
    roles: tuple[str, ...]  # participant roles, e.g. ("reviewer", "challenger")
    output_schema: str  # e.g. "reviewer-verdict"
    aggregation: str
    disagreement_handling: str
    budget_tokens: int  # reservation ceiling, enforced pre-spend by budget.py
    timeout_seconds: int  # per-strategy runtime ceiling; the panel takes the min
    model_route: str  # e.g. "preferred", "fallback", "diverse", "economical"


#: Every declared field must have a runtime consumer (see the module docstring).
#: `tests/test_strategy_metadata.py` asserts this against the real modules, so a
#: newly-added dead field fails CI instead of shipping.
DECLARED_FIELDS: tuple[str, ...] = (
    "name", "roles", "output_schema", "aggregation", "disagreement_handling",
    "budget_tokens", "timeout_seconds", "model_route",
)


# The full registry of the 12 named strategies from the spec.
STRATEGIES: tuple[Strategy, ...] = (
    Strategy("direct_analysis", ("reviewer",), "reviewer-verdict",
             "single", "single_verdict", 200000, 1800, "preferred"),
    Strategy("decomposition", ("reviewer", "focus"), "reviewer-verdict",
             "consensus", "adjudicate_split", 300000, 2400, "preferred"),
    Strategy("checklist", ("reviewer",), "reviewer-verdict",
             "checklist_score", "flag_unknown", 200000, 1800, "preferred"),
    Strategy("hypothesis_testing", ("reviewer",), "reviewer-verdict",
             "hypothesis_register", "escalate", 250000, 2400, "preferred"),
    Strategy("adversarial", ("reviewer", "adversary"), "reviewer-verdict",
             "majority", "adjudicate_split", 300000, 2400, "diverse"),
    Strategy("debate", ("proponent", "opponent"), "reviewer-verdict",
             "panel_adjudicated", "adjudicate_split", 350000, 3000, "fallback"),
    Strategy("independent_parallel", ("reviewer_a", "reviewer_b"), "reviewer-verdict",
             "unanimous", "adjudicate_split", 400000, 3000, "diverse"),
    Strategy("specialist_panel", ("reviewer", "security", "integration"), "reviewer-verdict",
             "panel_adjudicated", "adjudicate_split", 500000, 3600, "preferred"),
    Strategy("sequential_refinement", ("reviewer", "refiner"), "reviewer-verdict",
             "sequenced", "hold_pending", 350000, 3000, "preferred"),
    Strategy("critique_revision", ("author_review", "critic"), "reviewer-verdict",
             "sequenced", "adjudicate_split", 350000, 3000, "preferred"),
    Strategy("evidence_synthesis", ("reviewer", "synthesizer"), "reviewer-verdict",
             "consensus", "flag_unknown", 300000, 2400, "preferred"),
    Strategy("uncertainty_calibration", ("reviewer",), "reviewer-verdict",
             "calibrated", "flag_unknown", 200000, 1800, "economical"),
)

STRATEGY_BY_NAME: dict[str, Strategy] = {s.name: s for s in STRATEGIES}

# `VALID_AGGREGATIONS` was previously declared and never enforced, and three
# registry rows had drifted outside it. Assert at import so a new row cannot
# introduce an aggregation no execution mode knows how to run.
assert {s.aggregation for s in STRATEGIES} <= VALID_AGGREGATIONS, (
    "strategy registry uses aggregations outside VALID_AGGREGATIONS: "
    + ", ".join(sorted({s.aggregation for s in STRATEGIES} - VALID_AGGREGATIONS))
)


class StrategyError(ValueError):
    pass


def available_strategies() -> list[str]:
    return [s.name for s in STRATEGIES]


def signals_for_profile(
    profile: Any,
    *,
    complexity: int = 0,
    prior_disagreement: bool = False,
    specialist_need: bool = False,
) -> dict[str, Any]:
    """Build the selection signals for an assurance profile.

    Shared so the orchestrator (which must reserve the strategy's token budget
    BEFORE any spend) and the panel (which executes it) can never select two
    different strategies for the same job.
    """
    as_dict = profile.as_dict() if hasattr(profile, "as_dict") else dict(profile or {})
    return {
        "risk": as_dict.get("level", "low"),
        "complexity": int(complexity),
        "required_independence": as_dict.get("independence", "single"),
        "prior_disagreement": bool(prior_disagreement),
        "specialist_need": bool(specialist_need),
    }


def strategy_for_profile(profile: Any, **kwargs: Any) -> tuple[Strategy, str]:
    """Deterministic strategy for an assurance profile. Never raises."""
    return select_strategy(signals_for_profile(profile, **kwargs))


def select_strategy(signals: dict[str, Any], candidates: list[str] | None = None) -> tuple[Strategy, str]:
    """Deterministically choose a strategy from review signals.

    Returns (strategy, selection_reason). Signals:
      risk: 'low' | 'medium' | 'high'
      complexity: int
      required_independence: 'single' | 'challenger' | 'panel'
      prior_disagreement: bool
      specialist_need: bool (security/migration/CI surface)
    Unknown/failed participants do not count as agreement regardless of strategy.

    The selection is ordered; the most specific signal wins.
    """
    allowed = set(candidates) if candidates else STRATEGY_BY_NAME.keys()
    risk = signals.get("risk", "low")
    independence = signals.get("required_independence", "single")
    prior_disagreement = bool(signals.get("prior_disagreement", False))
    specialist = bool(signals.get("specialist_need", False))
    complexity = int(signals.get("complexity", 0))

    def pick(names: list[str]) -> Strategy:
        for n in names:
            if n in allowed:
                return STRATEGY_BY_NAME[n]
        return STRATEGY_BY_NAME["direct_analysis"]

    if specialist:
        return pick(["specialist_panel", "independent_parallel", "direct_analysis"]), \
            "specialist_need"
    if prior_disagreement:
        return pick(["debate", "independent_parallel", "adversarial", "direct_analysis"]), \
            "prior_disagreement"
    if independence == "panel":
        return pick(["independent_parallel", "debate", "specialist_panel", "direct_analysis"]), \
            "required_panel"
    if independence == "challenger":
        return pick(["adversarial", "independent_parallel", "critique_revision", "direct_analysis"]), \
            "required_challenger"
    if risk == "high":
        return pick(["uncertainty_calibration", "checklist", "decomposition", "direct_analysis"]), \
            "high_risk"
    if complexity >= 3:
        return pick(["decomposition", "specialist_panel", "evidence_synthesis", "direct_analysis"]), \
            "high_complexity"
    return pick(["direct_analysis", "checklist"]), "default_low"