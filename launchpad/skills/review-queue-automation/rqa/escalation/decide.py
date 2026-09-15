"""`decide()` — the E-17 CLI entry point — `code/P-11-escalation.md` §3 — and the
`JobReader`/`LifecycleResume` Protocols this part depends on (§4).

`decide()` is `rqa/edges.py`'s open `def decide(**kwargs): ...` E-17 surface, made
concrete: this is that part's lane to implement, and its first four parameters are
positional-or-keyword exactly as `code/P-11-escalation.md` §3 states; the rest are
keyword-only.

**Deterministic, fail-closed refusal.** Steps 7-8 compare the escalation's own recorded
`head_sha`/`snapshot_hash` — captured before the human ever saw the question — against
`jobs`'s current values through the injected read-only `JobReader`. Either mismatch is a
value (`EscalationRefused`), decided once, before anything is written: never a local
substitute for the human's answer, never a second chance to reinterpret it later.

**`AppendFailed` always propagates** (§3 step 11): the escalation stays open, `store.close`
and `lifecycle.resume` are never reached, and a decision that was not durably recorded
never resumes anything.
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from typing import Literal, Protocol

from rqa.contracts import (
    Decision,
    EscalationCause,
    EscalationRefusalReason,
    EscalationRefused,
    Job,
    JobStatus,
    RecordWriter,
)

from rqa.escalation.escalate import EscalationError, utcnow
from rqa.escalation.store import EscalationStore

__all__ = ["EscalationRefused", "EscalationRefusalReason", "JobReader", "LifecycleResume", "decide"]

_REASON = EscalationRefusalReason
_OUTCOMES = ("approved", "changes_requested")

# Persist visible escapes for terminal controls, separators and bidi directives.
_TEXT_ESCAPES = {n: f"\\u{n:04x}" for n in (
    *range(32), *range(127, 160), 0x061c, 0x200e, 0x200f,
    *range(0x2028, 0x202f), *range(0x2066, 0x206a),
)}


class JobReader(Protocol):
    """`decide.py` — P-01 supplies this read-only P-01 jobs view at wiring time (§4):
    read-only access to `jobs.head_sha`/`jobs.snapshot_hash` through the shared `Job`
    value, never a second copy of job state."""

    def current(self, job_id: str) -> Job | None: ...


class LifecycleDeps(Protocol):
    """P-02's dependency bundle (`code/P-02-lifecycle.md` §2), opaque here: `decide()`
    only forwards it to `lifecycle.resume`, it never reads a field from it. A local
    stand-in for typing, mirroring `rqa.edges.LifecycleDeps`'s own docstring-only
    placeholder — P-11 never imports P-02's real implementation (§1)."""


class LifecycleResume(Protocol):
    """P-02 supplies this E-11 reverse edge at wiring time (§4): `resume`, called with
    the validated escalation's job id, the decision, and the caller-provided
    `LifecycleDeps`; its `JobStatus` return is never inspected."""

    def resume(self, *, job_id: str, decision: Decision, deps: LifecycleDeps) -> JobStatus: ...


def decide(
    escalation_id: int,
    actor: str,
    basis: str,
    outcome: Literal["approved", "changes_requested"] | None = None,
    *,
    store: EscalationStore,
    record: RecordWriter,
    jobs: JobReader,
    lifecycle: LifecycleResume,
    deps: LifecycleDeps,
    clock: Callable[[], datetime] = utcnow,
) -> Decision | EscalationRefused:
    """§3 E-17 `decide`, in order. Every branch returns or raises."""
    if actor.strip() == "":
        raise EscalationError("a decision must name the human actor who made it")
    if basis.strip() == "":
        raise EscalationError("a decision must name its basis")
    if outcome is not None and outcome not in _OUTCOMES:
        raise EscalationError(f"{outcome!r} is not 'approved', 'changes_requested', or None")

    escalation = store.get(escalation_id)
    if escalation is None:
        return EscalationRefused(_REASON.NOT_FOUND, detail=f"no escalation {escalation_id}")
    if escalation.status != "open":
        return EscalationRefused(
            _REASON.ALREADY_CLOSED, detail=f"escalation {escalation_id} is already closed"
        )
    if outcome is None and escalation.cause is EscalationCause.AUTHORITY_REQUIREMENT:
        del escalation
        raise EscalationError("an authority-requirement decision must include --outcome")
    if outcome is not None and escalation.cause is not EscalationCause.AUTHORITY_REQUIREMENT:
        # F-T1: `escalation` carries `.context`/`.question`, both potentially
        # PR-derived; extract only the safe value this message needs, then unbind the
        # whole row before raising — `del` before `raise`, not after, since control
        # never returns to this frame — so neither is reachable from this frame once
        # the exception is introspected.
        offending_cause = escalation.cause.value
        del escalation
        raise EscalationError(
            "an outcome may only be recorded against "
            f"{EscalationCause.AUTHORITY_REQUIREMENT.value!r}, not {offending_cause!r}"
        )

    current = jobs.current(escalation.job_id)
    if current is None or current.head_sha != escalation.head_sha:
        return EscalationRefused(
            _REASON.HEAD_MOVED,
            detail=f"job head is now {current.head_sha if current is not None else '<gone>'}",
        )
    if current.snapshot_hash != escalation.snapshot_hash:
        return EscalationRefused(
            _REASON.SNAPSHOT_MOVED, detail=f"job snapshot is now {current.snapshot_hash!r}"
        )

    substantiates = (
        None
        if escalation.cause is EscalationCause.AUTHORITY_REQUIREMENT
        else escalation.context.get("obligation")
    )
    decision = Decision(
        actor=actor.strip().translate(_TEXT_ESCAPES), basis=basis.strip().translate(_TEXT_ESCAPES), substantiates=substantiates, outcome=outcome
    )

    # F-T1: `record.append`, `store.close` and `lifecycle.resume` below can each raise
    # (`AppendFailed`, a `sqlite3.Error`, `LifecycleError`), and none of the three needs
    # `escalation` itself — only its `job_id` and `cause.value`. Extract those into
    # plain locals and unbind `escalation` (carrying `.context`/`.question`, both
    # potentially PR-derived) before any of the three calls, not merely before a direct
    # `raise`: a `del` guards only the statement it precedes, and `escalation` would
    # otherwise stay live in this frame across the whole sequence. Mirrors
    # `rqa/authority/capability.py`'s `probe_capability`, which extracts what the
    # downstream call needs and drops the sensitive binding around it — here the
    # binding can be dropped before the sequence starts, since none of the three calls
    # takes `escalation` as an argument the way `probe()` takes the credential.
    job_id = escalation.job_id
    cause_value = escalation.cause.value
    del escalation

    entry = record.append(
        job_id,
        kind="decision",
        payload={
            "escalation_id": escalation_id,
            "cause": cause_value,
            "actor": decision.actor,
            "basis": decision.basis,
            "substantiates": decision.substantiates,
            "outcome": decision.outcome,
        },
    )

    store.close(escalation_id, decision_entry_seq=entry.seq, closed_at=clock())
    lifecycle.resume(job_id=job_id, decision=decision, deps=deps)
    return decision
