"""Per-obligation reuse classification and provenance construction — P-13 §3.5-6."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from enum import Enum

import rqa.protocol.paths
from rqa.contracts import CarriedEvidence, EvidenceState, Obligation, RecordRow


class Reason(str, Enum):
    """The complete P-13 §2 vocabulary for one obligation's reuse decision."""

    PATH_TOUCHED = "path_touched"
    PIN_CHANGED = "pin_changed"
    NOT_VERIFIED = "not_verified"
    NEW_OBLIGATION = "new_obligation"
    NO_PRIOR_JUDGEMENT = "no_prior_judgement"
    NO_PREDECESSOR = "no_predecessor"
    UNTRUSTED_PREDECESSOR = "untrusted_predecessor"
    UNCHANGED_VERIFIED = "unchanged_verified"


class ReuseError(Exception):
    """Programming error or malformed predecessor record: no trustworthy CarryOver can be made."""


def _prior_states(*, judgement_row: RecordRow) -> dict[str, EvidenceState]:
    """Decode the predecessor judgement's closed evidence-state mapping."""
    payload = judgement_row.payload
    if not isinstance(payload, Mapping):
        raise ReuseError("predecessor judgement payload is not a mapping")
    raw_states = payload.get("obligations")
    if not isinstance(raw_states, Mapping):
        raise ReuseError("predecessor judgement obligations is not a mapping")

    states: dict[str, EvidenceState] = {}
    for obligation_id, raw_state in raw_states.items():
        if type(obligation_id) is not str or not obligation_id:
            raise ReuseError("predecessor judgement has an invalid obligation id")
        if type(raw_state) is not str:
            raise ReuseError(
                f"predecessor judgement state for {obligation_id!r} is not a string"
            )
        try:
            states[obligation_id] = EvidenceState(raw_state)
        except ValueError as exc:
            raise ReuseError(
                f"predecessor judgement state for {obligation_id!r} is unknown"
            ) from exc
    return states


def _reason(
    *,
    obligation: Obligation,
    prior_states: Mapping[str, EvidenceState],
    revision_changed_paths: frozenset[str],
) -> Reason:
    """Classify one current obligation in P-13 §3.5's required order."""
    state = prior_states.get(obligation.id)
    if state is None:
        return Reason.NEW_OBLIGATION
    if state is not EvidenceState.VERIFIED:
        return Reason.NOT_VERIFIED
    if any(
        rqa.protocol.paths.matches(path, pattern)
        for path in revision_changed_paths
        for pattern in obligation.paths
    ):
        return Reason.PATH_TOUCHED
    return Reason.UNCHANGED_VERIFIED


def _source_attestations(*, judgement_row: RecordRow, obligation_id: str) -> tuple[str, ...]:
    """Read RQA-authored contributing attempt ids, never self-reported model identity."""
    payload = judgement_row.payload
    if not isinstance(payload, Mapping):
        raise ReuseError("predecessor judgement payload is not a mapping")
    raw_contributions = payload.get("contributing_attempts")
    if not isinstance(raw_contributions, Mapping):
        raise ReuseError("predecessor judgement contributing_attempts is not a mapping")
    raw_attempts = raw_contributions.get(obligation_id)
    if (
        isinstance(raw_attempts, (str, bytes, bytearray))
        or not isinstance(raw_attempts, Sequence)
        or not raw_attempts
    ):
        raise ReuseError(
            f"predecessor judgement contributions for {obligation_id!r} are malformed"
        )
    if any(type(attempt_id) is not str or not attempt_id for attempt_id in raw_attempts):
        raise ReuseError(
            f"predecessor judgement contributions for {obligation_id!r} contain an invalid id"
        )
    return tuple(raw_attempts)


def _carried_evidence(
    *, obligation: Obligation, source_job: str, judgement_row: RecordRow
) -> CarriedEvidence:
    """Build authenticated provenance from the latest trusted judgement (§3.6).

    **Interim, pending #2236.** P-13 §3.6 fixes `source_judgement_seq` to the
    `judgement_row.seq` returned by `VerifiedRecordPrefix.latest("judgement")`, so this
    mints the predecessor's *latest trusted* judgement sequence. The pinned `(job, seq)`
    reference #2236 calls for cannot be carried farther today because
    `Judgement.reused_from` (`CONTRACTS.md` §6) is only a job id. This interim behaviour
    stays aligned with P-12's documented reuse-chain resolution until #2236 lands.
    """
    if type(judgement_row.seq) is not int or judgement_row.seq < 1:
        raise ReuseError("predecessor judgement sequence is malformed")
    attestations = _source_attestations(
        judgement_row=judgement_row, obligation_id=obligation.id
    )
    return CarriedEvidence(
        obligation_id=obligation.id,
        state=EvidenceState.VERIFIED,
        source_job=source_job,
        # Interim (see the docstring and #2236): this is the latest trusted judgement,
        # because no earlier pinned source sequence is readable from the landed seam.
        source_judgement_seq=judgement_row.seq,
        source_attestations=attestations,
    )
