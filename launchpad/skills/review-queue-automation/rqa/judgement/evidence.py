"""Cutoff-bounded obligation-state and assurance calculation —
`code/P-07-judgement.md` §3 steps 4 and 9.

Every `Attempt` reaching this module has already been proven, at step 1, to
have ended at or before `panel.evidence_cutoff` — that is the "cutoff-bounded"
half of this module's name. The other half, reconciling possibly-disagreeing
attempts into one `EvidenceState` per obligation, is `reduce_states`.

This module never raises `JudgementError`; it has no dependency on `judge.py`.
"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence

from rqa.contracts import Assurance, Attempt, Decision, EvidenceState, Verdict

__all__ = ["reduce_states", "resolve_obligation_state", "compute_assurance"]

#: §3 step 4, verbatim, after the qualifying-`VERIFIED` check: "CONTRADICTORY,
#: FAILED, UNAVAILABLE, INCOMPLETE, NOT_VERIFIED, then UNKNOWN."
_FALLBACK_ORDER: tuple[EvidenceState, ...] = (
    EvidenceState.CONTRADICTORY,
    EvidenceState.FAILED,
    EvidenceState.UNAVAILABLE,
    EvidenceState.INCOMPLETE,
    EvidenceState.NOT_VERIFIED,
)


def reduce_states(states: Sequence[EvidenceState]) -> EvidenceState:
    """Reconcile every attempt's reported state for one obligation into one
    (§3 step 4).

    `VERIFIED` is "qualifying positive evidence" only when it is present and
    not contradicted by a `CONTRADICTORY` or outright `FAILED` report from a
    different attempt — that is what lets one attempt's `INCOMPLETE` (for
    example, evidence that depended on a still-pending check) be overridden by
    another attempt's independent `VERIFIED`, while a genuine `CONTRADICTORY`
    or `FAILED` report is never silently outvoted by an optimistic one.
    Nobody reporting on this obligation at all is `UNKNOWN`.
    """
    present = set(states)
    if not present:
        return EvidenceState.UNKNOWN
    if (
        EvidenceState.VERIFIED in present
        and EvidenceState.CONTRADICTORY not in present
        and EvidenceState.FAILED not in present
    ):
        return EvidenceState.VERIFIED
    for state in _FALLBACK_ORDER:
        if state in present:
            return state
    return EvidenceState.UNKNOWN


def resolve_obligation_state(
    obligation_id: str,
    *,
    attempts: tuple[Attempt, ...],
    decision: Decision | None,
) -> EvidenceState:
    """A non-carried obligation's state (§3 step 4): a matching non-empty
    decision overrides outright and only its own `substantiates` obligation;
    otherwise the reconciled verdict states decide.
    """
    if (
        decision is not None
        and decision.substantiates == obligation_id
        and decision.outcome is not None
    ):
        return EvidenceState.VERIFIED if decision.outcome == "approved" else EvidenceState.FAILED
    states = [
        attempt.outcome.obligations[obligation_id]
        for attempt in attempts
        if isinstance(attempt.outcome, Verdict) and obligation_id in attempt.outcome.obligations
    ]
    return reduce_states(states)


def compute_assurance(*, states: Mapping[str, EvidenceState], required: int) -> Assurance:
    """§3 step 9: `achieved = floor(required * verified / total)` over the
    universe only; an empty universe yields `(0, 0)`."""
    total = len(states)
    if total == 0:
        return Assurance(required=0, achieved=0)
    verified = sum(1 for state in states.values() if state is EvidenceState.VERIFIED)
    return Assurance(required=required, achieved=math.floor(required * verified / total))
