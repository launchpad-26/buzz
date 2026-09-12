"""`carry_over()` — P-13's E-05 revision-reuse entry point."""

from __future__ import annotations

from collections.abc import Mapping

from rqa.contracts import (
    CarriedEvidence,
    CarryOver,
    EvidenceState,
    Facts,
    Job,
    Obligation,
    RecordReader,
    RecordRow,
    RecordUntrusted,
    RecordWriter,
    Snapshot,
    VerifiedRecordPrefix,
)
from rqa.reuse.obligations import (
    Reason,
    ReuseError,
    _carried_evidence,
    _prior_states,
    _reason,
)
from rqa.reuse.pin import prior_pin


def _complete_regeneration(
    *, obligations: tuple[Obligation, ...], reason: Reason, source_job: str | None
) -> CarryOver:
    """A total result in which every current obligation regenerates for one reason."""
    return CarryOver(
        reused=(),
        regenerated=tuple(obligation.id for obligation in obligations),
        reasons={obligation.id: reason.value for obligation in obligations},
        source_job=source_job,
    )


def _classify(
    *,
    obligations: tuple[Obligation, ...],
    facts: Facts,
    source_job: str,
    judgement_row: RecordRow,
    prior_states: Mapping[str, EvidenceState],
) -> CarryOver:
    """Classify every current obligation exactly once, preserving snapshot order."""
    reused: list[CarriedEvidence] = []
    regenerated: list[str] = []
    reasons: dict[str, str] = {}

    for obligation in obligations:
        reason = _reason(
            obligation=obligation,
            prior_states=prior_states,
            revision_changed_paths=facts.revision_changed_paths,
        )
        reasons[obligation.id] = reason.value
        if reason is Reason.UNCHANGED_VERIFIED:
            reused.append(
                _carried_evidence(
                    obligation=obligation,
                    source_job=source_job,
                    judgement_row=judgement_row,
                )
            )
        else:
            regenerated.append(obligation.id)

    return CarryOver(
        reused=tuple(reused),
        regenerated=tuple(regenerated),
        reasons=reasons,
        source_job=source_job,
    )


def _payload(*, carry: CarryOver, snapshot: Snapshot) -> dict[str, object]:
    """Serialize the complete §6 `carry_over` entry without leaking shared value types."""
    reused = [
        {
            "obligation_id": evidence.obligation_id,
            "state": evidence.state.value,
            "source_job": evidence.source_job,
            "source_judgement_seq": evidence.source_judgement_seq,
            "source_attestations": list(evidence.source_attestations),
        }
        for evidence in carry.reused
    ]
    return {
        "source_job": carry.source_job,
        "reused": reused,
        "regenerated": list(carry.regenerated),
        "reasons": dict(carry.reasons),
        "protocol_hash": snapshot.protocol_hash,
        "policy_version": snapshot.policy.version,
    }


def _append_and_return(
    *, carry: CarryOver, job: Job, snapshot: Snapshot, record: RecordWriter
) -> CarryOver:
    """Make the decision durable before returning it; `AppendFailed` propagates."""
    record.append(job.id, "carry_over", _payload(carry=carry, snapshot=snapshot))
    return carry


def carry_over(
    *, job: Job, prior: RecordReader, facts: Facts, snapshot: Snapshot, record: RecordWriter
) -> CarryOver:
    """E-05, verbatim from `CONTRACTS.md` §9; classify and record P-13 §3 in order."""
    if job.repo != snapshot.repo:
        raise ReuseError(
            f"job repository {job.repo!r} does not match snapshot repository {snapshot.repo!r}"
        )

    obligations = snapshot.policy.obligations
    source_job = job.predecessor_job
    if source_job is None:
        carry = _complete_regeneration(
            obligations=obligations,
            reason=Reason.NO_PREDECESSOR,
            source_job=None,
        )
        return _append_and_return(carry=carry, job=job, snapshot=snapshot, record=record)

    prefix = prior.trusted_prefix(source_job)
    if isinstance(prefix, RecordUntrusted):
        carry = _complete_regeneration(
            obligations=obligations,
            reason=Reason.UNTRUSTED_PREDECESSOR,
            source_job=source_job,
        )
        return _append_and_return(carry=carry, job=job, snapshot=snapshot, record=record)
    if not isinstance(prefix, VerifiedRecordPrefix) or prefix.job_id != source_job:
        raise ReuseError("record reader returned a malformed predecessor prefix")

    judgement_row = prefix.latest("judgement")
    pin = prior_pin(prefix=prefix)

    if judgement_row is None:
        carry = _complete_regeneration(
            obligations=obligations,
            reason=Reason.NO_PRIOR_JUDGEMENT,
            source_job=source_job,
        )
    else:
        # Every present judgement is decoded even when the plan pin moved: §3 names a
        # malformed judgement as an error, not a reason to regenerate.
        prior_states = _prior_states(judgement_row=judgement_row)
        if pin is None or pin != (snapshot.protocol_hash, snapshot.policy.version):
            carry = _complete_regeneration(
                obligations=obligations,
                reason=Reason.PIN_CHANGED,
                source_job=source_job,
            )
        else:
            carry = _classify(
                obligations=obligations,
                facts=facts,
                source_job=source_job,
                judgement_row=judgement_row,
                prior_states=prior_states,
            )

    return _append_and_return(carry=carry, job=job, snapshot=snapshot, record=record)
