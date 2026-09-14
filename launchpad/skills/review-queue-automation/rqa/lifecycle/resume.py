"""`resume()` — the E-11 reverse edge, steps 12a/12b — `code/P-02-lifecycle.md` §3.3.

A human answered an escalation and P-11 calls back in. Two paths, split by the open
escalation's cause:

- **12a** (evidence gap, conflicting judgement, unresolved decision, required
  information): the review re-enters at judgement. `plan`, `carry` and the last
  complete panel are reconstructed from the record (§5's read protocol); E-09 receives
  fresh same-head facts, the recorded evidence cutoff, and the decision, then
  `escalated → judged` and the ordinary step-9 dispatch continues (RQA-FR-027).
- **12b** (authority requirement): RQA was not permitted to act, so the human acted on
  GitHub and recorded what they did (ADR-0061). This function admits that outcome only
  when **exactly one** `facts.reviews` row matches `decision.actor`, `decision.outcome`
  and `job.head_sha` and was submitted at or after the escalation was raised — absent,
  ambiguous or mismatched raises `StaleDecisionError` and makes **no** transition. Only
  then `escalated → approved | changes_requested`, directly, with step 11 performed for
  an approval. Step 10 is never re-entered.

**Where the escalation comes from.** The `escalation` record entry P-11 appends at
`raise_` step 4 (`code/P-11-escalation.md` §6), read through §5's read protocol — not
E-11's `pending()`. `decide()`'s own step order closes the `human_requests` row (step
12) *before* calling this function (step 13), so `pending()` no longer lists it by the
time we are running; and `code/P-02-lifecycle.md` §7 forbids this part from reading "the
content of `human_requests` rows" in the first place, while placing `record_entries`
inside its permitted set. One durable source, permitted and ordering-independent.

**Staleness is fail-closed and value-free.** A moved head or a moved snapshot raises
`StaleDecisionError`; this function never substitutes a local alternative value for the
human's decision (§3.3). The comparison is against the pinned job row and the recorded
escalation's own head and snapshot — both captured before the human ever saw the
question.

**Containment.** The drive after a successful check runs under the same boundary as
`admit` (§3.1): an `AppendFailed`, `sqlite3.Error` or `OSError` becomes one licensed
safe stop from the durable state, a failure while committing that stop propagates, and
a neighbour's `*Error` propagates unchanged. The pre-transition checks raise this
part's own errors and are not converted into stops — refusing a decision changes
nothing and needs no recovery.

Like every module here, no PR-derived byte reaches a reason, a question or a raise:
the review rows being matched are data compared field-by-field, never interpolated.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime

from rqa.contracts import (
    AppendFailed,
    Decision,
    EscalationCause,
    Facts,
    GithubUnavailable,
    Job,
    JobStatus,
    PanelResult,
)
from rqa.lifecycle.admit import _contained_reason, _durable
from rqa.lifecycle.deps import LifecycleDeps
from rqa.lifecycle.errors import LifecycleError, StaleDecisionError, UnknownJobError
from rqa.lifecycle.rest import enter_rest
from rqa.lifecycle.states import TRANSITIONS, as_status
from rqa.lifecycle.steps import (
    Cascade,
    _latest_payload,
    _pinned_snapshot,
    _recorded_carry,
    _recorded_panel,
    _recorded_plan,
    drive,
    step8,
)
from rqa.lifecycle.transition import safe_stop, transition

__all__ = ["resume"]

#: The 12b outcome → status mapping. Any other outcome raises `LifecycleError` (§3.3).
_OUTCOME_STATUS = {
    "approved": JobStatus.APPROVED,
    "changes_requested": JobStatus.CHANGES_REQUESTED,
}


@dataclass(frozen=True)
class _RecordedEscalation:
    """The escalation a decision answers, as recovered from the record.

    Exactly the four fields `resume` uses, and deliberately **not** a
    `contracts.Escalation`: that value's `id` is the `human_requests` row id, and §7
    forbids this part from reading that table's content — a synthesised id would be a
    fabricated field, not a recovered one. Module-private, so nothing at the seam moves:
    E-11's `resume(*, job_id, decision, deps) -> JobStatus` is unchanged.

    `raised_at` is the record entry's own `at`. `RecordWriter.append` takes no `at`, so
    the writer stamps it microseconds after P-11 computed its `raised_at = utcnow()`
    (`code/P-11-escalation.md` §3): `at >= raised_at` by construction. 12b's
    "submitted at or after we asked" bound can therefore only become marginally
    stricter, never looser — the fail-closed direction.
    """

    cause: EscalationCause
    raised_at: datetime
    head_sha: str
    snapshot_hash: str | None


def resume(*, job_id: str, decision: Decision, deps: LifecycleDeps) -> JobStatus:
    """E-11 verbatim (`rqa/edges.py`): apply one recorded human decision to one
    escalated job and drive it to its next resting status."""
    job = _load(job_id=job_id, deps=deps)
    if as_status(job.status, what="jobs.status") is not JobStatus.ESCALATED:
        raise LifecycleError(
            f"job {job_id!r} is {job.status.value}, not escalated; there is no open "
            "question for a decision to answer"
        )
    escalation = _recorded_escalation(job=job, deps=deps)

    current = job
    try:
        facts = deps.github.facts(job=job, record=deps.record)
        if isinstance(facts, GithubUnavailable):
            # An availability outcome is a value (§2). Without same-head facts the
            # decision cannot be verified; `escalated → stopped` is the licensed safe
            # rest and the decision is left unapplied for a later, verifiable resume.
            current = transition(
                job,
                JobStatus.STOPPED,
                reason="facts unavailable",
                connection=deps.connection,
                record=deps.record,
            )
            return as_status(
                enter_rest(current, snapshot=None, deps=deps).status, what="jobs.status"
            )
        if not isinstance(facts, Facts):
            raise LifecycleError(f"E-23 returned {type(facts).__name__}")

        _check_freshness(job=job, facts=facts, escalation=escalation)

        if escalation.cause is EscalationCause.AUTHORITY_REQUIREMENT:
            current = _step12b(
                job=job, decision=decision, facts=facts, escalation=escalation, deps=deps
            )
        else:
            current = _step12a(job=job, decision=decision, facts=facts, deps=deps)
        return as_status(current.status, what="jobs.status")
    except (AppendFailed, sqlite3.Error, OSError) as exc:
        # §3.1's containment, unchanged in meaning: re-read the durable row, stop
        # where the table licenses a stop, propagate where it does not.
        durable = _durable(job=current, connection=deps.connection, cause=exc)
        if JobStatus.STOPPED not in TRANSITIONS[as_status(durable.status, what="jobs.status")]:
            raise
        stopped = safe_stop(
            durable,
            reason=_contained_reason(exc),
            connection=deps.connection,
            record=deps.record,
        )
        return as_status(stopped.status, what="jobs.status")


def _step12a(*, job: Job, decision: Decision, facts: Facts, deps: LifecycleDeps) -> Job:
    """12a: reconstruct, re-judge with the decision, `escalated → judged`, continue."""
    ctx = Cascade(deps=deps, facts=facts)
    snapshot = _pinned_snapshot(job, ctx)
    if snapshot is None:
        raise LifecycleError(
            f"job {job.id!r} reached a 12a resume without a pinned snapshot"
        )
    ctx.plan = _recorded_plan(job, ctx)
    ctx.carry = _recorded_carry(job, ctx)

    panel = _recorded_panel(job, ctx)
    if panel is None:
        # Carry-only review: no `panel` entry exists; the cutoff is the recorded
        # judgement's (§3.3). Checks observed after it cannot affect judgement.
        panel = _carry_only_panel(job, ctx)
    elif not panel.complete:
        raise LifecycleError(
            f"job {job.id!r} carries an incomplete recorded panel; an escalated job "
            "can only have rested on a complete one"
        )
    ctx.panel = panel

    ctx.judgement = step8(job, ctx, panel=panel, decision=decision)
    job = transition(
        job,
        JobStatus.JUDGED,
        reason="human decision applied",
        connection=deps.connection,
        record=deps.record,
    )
    return drive(job, deps=deps, cascade=ctx)


def _step12b(
    *,
    job: Job,
    decision: Decision,
    facts: Facts,
    escalation: _RecordedEscalation,
    deps: LifecycleDeps,
) -> Job:
    """12b: admit the human's own GitHub outcome, verified against E-23, then step 11
    for an approval. No verdict grant is requested (§8 T15)."""
    outcome = decision.outcome
    if outcome not in _OUTCOME_STATUS:
        raise LifecycleError(
            "an authority-requirement decision must record the human's outcome as "
            f"approved or changes_requested; got {outcome!r}"
        )
    matches = [
        review
        for review in facts.reviews
        if review.actor == decision.actor
        and review.outcome == outcome
        and review.head_sha == job.head_sha
        and review.submitted_at >= escalation.raised_at
    ]
    if len(matches) != 1:
        raise StaleDecisionError(
            f"{len(matches)} submitted reviews match the recorded decision for job "
            f"{job.id!r}; exactly one same-head, post-escalation review is required"
        )
    job = transition(
        job,
        _OUTCOME_STATUS[outcome],
        reason=f"recorded human outcome: {outcome}",
        connection=deps.connection,
        record=deps.record,
    )
    # Step 11 runs for an approval; changes_requested rests. Both through the loop.
    return drive(job, deps=deps, cascade=Cascade(deps=deps, facts=facts))


def _carry_only_panel(job: Job, ctx: Cascade) -> PanelResult:
    payload = _latest_payload(job, ctx, kind="judgement")
    if payload is None or not isinstance(payload.get("cutoff"), str):
        raise LifecycleError(
            f"job {job.id!r} has neither a panel entry nor a judgement cutoff to "
            "reconstruct one from"
        )
    return PanelResult(
        attempts=(),
        complete=True,
        incomplete_reason=None,
        evidence_cutoff=datetime.fromisoformat(payload["cutoff"]),
        bound_reached=False,
    )


def _check_freshness(*, job: Job, facts: Facts, escalation: _RecordedEscalation) -> None:
    """§3.3: either mismatch — head or pinned snapshot — raises; no transition follows."""
    if facts.pr.head_sha != job.head_sha:
        raise StaleDecisionError(
            f"the pull request head moved after the escalation for job {job.id!r} "
            "was raised; the decision is not applied"
        )
    if escalation.head_sha != job.head_sha:
        raise StaleDecisionError(
            f"the escalation for job {job.id!r} was raised against a different head; "
            "the decision is not applied"
        )
    if escalation.snapshot_hash != job.snapshot_hash:
        raise StaleDecisionError(
            f"the pinned snapshot for job {job.id!r} does not match the one the "
            "escalation was raised against; the decision is not applied"
        )


def _load(*, job_id: str, deps: LifecycleDeps) -> Job:
    """§3.3's permitted `jobs` read; an absent row raises `UnknownJobError`."""
    row = deps.connection.execute(
        "SELECT id, repo, number, head_sha, base_sha, head_repo, head_ref, "
        "predecessor_job, predecessor_head_sha, snapshot_hash, status "
        "FROM jobs WHERE id = ?",
        (job_id,),
    ).fetchone()
    if row is None:
        raise UnknownJobError(f"no jobs row for {job_id!r}; nothing exists to resume")
    return Job(
        id=row[0],
        repo=row[1],
        number=row[2],
        head_sha=row[3],
        base_sha=row[4],
        head_repo=row[5],
        head_ref=row[6],
        predecessor_job=row[7],
        predecessor_head_sha=row[8],
        snapshot_hash=row[9],
        status=as_status(row[10], what="jobs.status"),
    )


def _recorded_escalation(*, job: Job, deps: LifecycleDeps) -> _RecordedEscalation:
    """The escalation this decision answers, from the latest `escalation` record entry.

    §5's read protocol, through `steps._latest_payload` — the one record-read idiom this
    package has — plus the same row's `at`, read in exactly that shape. The two reads
    observe the same row by construction: identical predicate and ordering, on the same
    connection, with no append between them.

    Absence is a `LifecycleError`: an `ESCALATED` job with no `escalation` entry is a
    wiring defect in the caller, not a crash. There is no multiplicity branch to guard
    any more — this reads the *latest* entry, and `decide()`, the only caller, has
    already proved at its steps 5-8 that exactly one open escalation exists for this job
    and has not been answered before (`code/P-11-escalation.md` §3).
    """
    ctx = Cascade(deps=deps)
    payload = _latest_payload(job, ctx, kind="escalation")
    if payload is None:
        raise LifecycleError(
            f"job {job.id!r} is escalated but has no escalation entry; there is nothing "
            "recorded for a decision to answer"
        )
    # F-T1: the payload also carries `question` and `context`, both potentially
    # PR-derived. Take the four fields this part uses and unbind the whole mapping
    # before any raise below, so neither is reachable from this frame's `f_locals` once
    # an exception raised here is introspected.
    cause_value = payload.get("cause")
    head_sha = payload.get("head_sha")
    snapshot_hash = payload.get("snapshot_hash")
    del payload

    if not isinstance(cause_value, str) or not isinstance(head_sha, str):
        raise LifecycleError(
            f"the escalation entry for job {job.id!r} records no cause or no head"
        )
    try:
        cause = EscalationCause(cause_value)
    except ValueError:
        raise LifecycleError(
            f"the escalation entry for job {job.id!r} records {cause_value!r}, which is "
            "not one of the five causes"
        ) from None

    row = deps.connection.execute(
        "SELECT at FROM record_entries WHERE job = ? AND kind = ? ORDER BY seq DESC LIMIT 1",
        (job.id, "escalation"),
    ).fetchone()
    return _RecordedEscalation(
        cause=cause,
        raised_at=datetime.fromisoformat(row[0]),
        head_sha=head_sha,
        snapshot_hash=snapshot_hash if isinstance(snapshot_hash, str) else None,
    )
