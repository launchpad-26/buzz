"""Named reasoning strategies for review-queue-automation.

Each strategy is a data record describing how participants are composed and how
their outputs are aggregated, so selection and degradation are deterministic and
testable. The strategy is chosen from review signals (risk, complexity, required
independence, presence of a prior disagreement), and the selection reason is
recorded.

Strategies never count failed/timed-out/invalid participants as agreement; the
aggregator drops any participant whose output is missing or invalid.
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
    parallel: bool  # True => participants run concurrently
    min_participants: int
    required_inputs: tuple[str, ...]
    output_schema: str  # e.g. "reviewer-verdict"
    aggregation: str
    disagreement_handling: str
    degraded_form: str
    assurance_contribution: float  # 0..1 towards achieved assurance
    budget_tokens: int  # soft token budget
    timeout_seconds: int
    model_route: str  # e.g. "preferred", "fallback", "diverse", "economical"


# The full registry of the 12 named strategies from the spec.
STRATEGIES: tuple[Strategy, ...] = (
    Strategy("direct_analysis", ("reviewer",), False, 1, ("evidence.txt",), "reviewer-verdict",
             "single", "single_verdict", "single_verdict", 0.35, 200000, 1800, "preferred"),
    Strategy("decomposition", ("reviewer", "focus"), False, 2, ("evidence.txt", "files"), "reviewer-verdict",
             "consensus", "adjudicate_split", "single_partial", 0.5, 300000, 2400, "preferred"),
    Strategy("checklist", ("reviewer",), False, 1, ("evidence.txt", "rubric"), "reviewer-verdict",
             "checklist_score", "flag_unknown", "single_verdict", 0.45, 200000, 1800, "preferred"),
    Strategy("hypothesis_testing", ("reviewer",), False, 1, ("evidence.txt", "files", "tests"), "reviewer-verdict",
             "hypothesis_register", "escalate", "single_uncertain", 0.4, 250000, 2400, "preferred"),
    Strategy("adversarial", ("reviewer", "adversary"), False, 2, ("evidence.txt",), "reviewer-verdict",
             "majority", "adjudicate_split", "single_verdict", 0.55, 300000, 2400, "diverse"),
    Strategy("debate", ("proponent", "opponent"), True, 2, ("evidence.txt",), "reviewer-verdict",
             "panel_adjudicated", "adjudicate_split", "single_proponent", 0.6, 350000, 3000, "fallback"),
    Strategy("independent_parallel", ("reviewer_a", "reviewer_b"), True, 2, ("evidence.txt",), "reviewer-verdict",
             "unanimous", "adjudicate_split", "single_reviewer", 0.7, 400000, 3000, "diverse"),
    Strategy("specialist_panel", ("reviewer", "security", "integration"), True, 2, ("evidence.txt", "files", "checks"), "reviewer-verdict",
             "panel_adjudicated", "adjudicate_split", "security_only", 0.8, 500000, 3600, "preferred"),
    Strategy("sequential_refinement", ("reviewer", "refiner"), False, 2, ("evidence.txt",), "reviewer-verdict",
             "sequenced", "hold_pending", "single_verdict", 0.65, 350000, 3000, "preferred"),
    Strategy("critique_revision", ("author_review", "critic"), False, 2, ("evidence.txt",), "reviewer-verdict",
             "sequenced", "adjudicate_split", "single_verdict", 0.6, 350000, 3000, "preferred"),
    Strategy("evidence_synthesis", ("reviewer", "synthesizer"), False, 2, ("evidence.txt", "linked_issue"), "reviewer-verdict",
             "consensus", "flag_unknown", "single_verdict", 0.6, 300000, 2400, "preferred"),
    Strategy("uncertainty_calibration", ("reviewer",), False, 1, ("evidence.txt",), "reviewer-verdict",
             "calibrated", "flag_unknown", "single_uncertain", 0.4, 200000, 1800, "economical"),
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