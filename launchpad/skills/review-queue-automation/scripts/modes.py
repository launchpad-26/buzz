"""Strategy execution modes: how participants compose into one panel result.

A strategy says WHICH questions to ask (`planner.py`) and how participants are
composed (`strategies.py`). This module owns the one remaining question: given
what the participants actually produced, did the panel happen?

The answer is deliberately narrow. This module decides **whether a valid,
sufficiently independent panel occurred** — `success` / `degraded` / `retryable` /
`human`. It never decides what the findings mean; `assurance.classify` owns that
from the signals. Keeping the two apart avoids a second competing decision path.

The rule that motivates the module: **a participant that did not produce a valid
verdict, or that duplicates a provider family already counted, is not agreement.**
Counting slot files cannot see either condition.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

# ---- statuses ---------------------------------------------------------------
SUCCESS = "success"
DEGRADED = "degraded"
RETRYABLE = "retryable"
HUMAN = "human"

#: A missing verifier means the verification step did not happen. For modes whose
#: entire purpose is independent confirmation that is a human matter, not a
#: partial credit.
_MISSING_VERIFIER_HUMAN = "human"
_MISSING_VERIFIER_DEGRADED = "degraded"


@dataclass(frozen=True)
class Participant:
    """One reviewer slot's real outcome, as recorded by the machinery.

    `provider_family` and `valid` come from trusted sidecar metadata and schema
    validation respectively — never from model-controlled verdict content.
    """

    role: str
    model: str
    provider_family: str = ""
    valid: bool = False
    signal: str = ""
    timed_out: bool = False


@dataclass(frozen=True)
class ModeResult:
    mode: str
    status: str
    reason: str
    counted: tuple[str, ...] = ()
    discounted: tuple[tuple[str, str], ...] = ()
    signals: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, Any]:
        return {
            "mode": self.mode,
            "status": self.status,
            "reason": self.reason,
            "counted": list(self.counted),
            "discounted": [list(item) for item in self.discounted],
            "signals": list(self.signals),
        }


@dataclass(frozen=True)
class ModeSpec:
    name: str
    min_counted: int
    require_distinct_families: bool
    require_unanimous: bool
    allow_degraded: bool
    verifier_role: str = ""
    on_missing_verifier: str = _MISSING_VERIFIER_HUMAN
    roles: tuple[str, ...] = field(default_factory=tuple)


SINGLE = "single"
INDEPENDENT_REVIEW = "independent_review"
GENERATOR_VERIFIER = "generator_verifier"
EXECUTOR_VERIFIER = "executor_verifier"
DEBATE_ADJUDICATE = "debate_adjudicate"
DUAL_KEY = "dual_key"

MODES: dict[str, ModeSpec] = {
    # One reviewer. Either it produced a valid verdict or nothing ran.
    SINGLE: ModeSpec(SINGLE, 1, False, False, False, roles=("reviewer",)),
    # Two independent reviewers; contradiction is a human matter.
    INDEPENDENT_REVIEW: ModeSpec(
        INDEPENDENT_REVIEW, 2, True, True, True, roles=("reviewer_a", "reviewer_b")
    ),
    # A generator's output is only reviewed once an independent verifier confirms
    # it. An unverified generation is never a pass.
    GENERATOR_VERIFIER: ModeSpec(
        GENERATOR_VERIFIER, 2, True, True, False,
        verifier_role="verifier", roles=("generator", "verifier"),
    ),
    EXECUTOR_VERIFIER: ModeSpec(
        EXECUTOR_VERIFIER, 2, True, True, False,
        verifier_role="verifier", roles=("executor", "verifier"),
    ),
    # Two opposed views plus an adjudicator. Without the adjudicator two views
    # still exist, so this degrades rather than escalating.
    DEBATE_ADJUDICATE: ModeSpec(
        DEBATE_ADJUDICATE, 3, True, False, True,
        verifier_role="adjudicator", on_missing_verifier=_MISSING_VERIFIER_DEGRADED,
        roles=("proponent", "opponent", "adjudicator"),
    ),
    # Both keys must turn. There is deliberately no partial credit.
    DUAL_KEY: ModeSpec(DUAL_KEY, 2, True, True, False, roles=("key_a", "key_b")),
}

#: How a strategy's declared aggregation maps onto an execution mode.
_AGGREGATION_MODE = {
    "single": SINGLE,
    "checklist_score": SINGLE,
    "hypothesis_register": SINGLE,
    "calibrated": SINGLE,
    "consensus": INDEPENDENT_REVIEW,
    "majority": INDEPENDENT_REVIEW,
    "unanimous": DUAL_KEY,
    "panel_adjudicated": DEBATE_ADJUDICATE,
    "sequenced": GENERATOR_VERIFIER,
}


class ModeError(ValueError):
    pass


def mode_for(strategy_name: str | None) -> ModeSpec:
    """Resolve the execution mode a strategy implies. Unknown -> single."""
    if not strategy_name:
        return MODES[SINGLE]
    from strategies import STRATEGY_BY_NAME

    strategy = STRATEGY_BY_NAME.get(strategy_name)
    if strategy is None:
        return MODES[SINGLE]
    return MODES[_AGGREGATION_MODE.get(strategy.aggregation, SINGLE)]


def spec_for(mode: str) -> ModeSpec:
    try:
        return MODES[mode]
    except KeyError as exc:
        raise ModeError(f"unknown execution mode {mode!r}; known: {', '.join(sorted(MODES))}") from exc


def for_profile(independence: str, required: int) -> ModeSpec:
    """The mode the CURRENT panel can actually execute, from its assurance profile.

    `panel.py` fills two reviewer slots, so it can execute `single` and
    `independent_review`. The remaining modes (generator/executor verifier,
    debate+adjudicate, dual key) are defined and tested here but require
    role-aware, multi-participant execution the panel does not yet perform — see
    the backlog. Deriving the spec from the profile rather than from the
    strategy's aggregation keeps completeness aligned with what ran.

    Agreement is deliberately NOT folded in: `require_unanimous` stays false so a
    disagreeing panel is still a panel that HAPPENED. `assurance.classify` owns
    what the disagreement means, and folding it in here would turn a material
    disagreement into a degraded draft instead of a human escalation.
    """
    if independence == "single" or required <= 1:
        return ModeSpec(SINGLE, 1, False, False, False, roles=("reviewer",))
    return ModeSpec(
        INDEPENDENT_REVIEW,
        max(2, int(required)),
        True,   # distinct provider families
        False,  # agreement is assurance's decision, not participation
        True,
        roles=("reviewer_a", "reviewer_b"),
    )


def aggregate(mode: str | ModeSpec, participants: list[Participant]) -> ModeResult:
    """Decide deterministically whether this mode's panel occurred.

    Discounting happens before any counting: an invalid, timed-out, or
    family-duplicate participant contributes nothing, and the reason is recorded
    so a reader can see why a slot did not count.
    """
    spec = mode if isinstance(mode, ModeSpec) else spec_for(mode)

    counted: list[Participant] = []
    discounted: list[tuple[str, str]] = []
    families: dict[str, str] = {}

    for participant in participants:
        label = participant.model or participant.role
        if participant.timed_out:
            discounted.append((label, "timed out"))
            continue
        if not participant.valid:
            discounted.append((label, "no schema-valid verdict"))
            continue
        family = participant.provider_family
        if spec.require_distinct_families and family and family in families:
            discounted.append(
                (label, f"same provider family as {families[family]} ({family})")
            )
            continue
        if family:
            families.setdefault(family, label)
        counted.append(participant)

    signals = tuple(participant.signal for participant in counted if participant.signal)
    counted_labels = tuple(p.model or p.role for p in counted)
    base = {
        "mode": spec.name,
        "counted": counted_labels,
        "discounted": tuple(discounted),
        "signals": signals,
    }

    # A required verifier that never produced a valid verdict means the
    # verification step did not happen.
    if spec.verifier_role and not any(p.role == spec.verifier_role for p in counted):
        status = (
            DEGRADED if spec.on_missing_verifier == _MISSING_VERIFIER_DEGRADED else HUMAN
        )
        return ModeResult(
            status=status,
            reason=f"{spec.verifier_role} produced no valid verdict",
            **base,
        )

    if not counted:
        return ModeResult(
            status=RETRYABLE,
            reason="no participant produced a valid verdict",
            **base,
        )

    if len(counted) < spec.min_counted:
        if spec.allow_degraded:
            return ModeResult(
                status=DEGRADED,
                reason=f"{len(counted)}/{spec.min_counted} independent participants",
                **base,
            )
        return ModeResult(
            status=HUMAN,
            reason=(
                f"{spec.name} requires {spec.min_counted} independent participants, "
                f"got {len(counted)}"
            ),
            **base,
        )

    if spec.require_unanimous and len(set(signals)) > 1:
        return ModeResult(
            status=HUMAN,
            reason="participants disagree: " + ", ".join(sorted(set(signals))),
            **base,
        )

    return ModeResult(status=SUCCESS, reason=f"{spec.name} satisfied", **base)
