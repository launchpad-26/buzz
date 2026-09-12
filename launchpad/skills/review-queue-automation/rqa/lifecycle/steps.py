"""Flow steps 3-13, one function per step, plus the dispatch table — `code/P-02-lifecycle.md` §3.2.

`admit()` and `resume()` both drive the same loop: `drive()` dispatches on the job's
current status until it reaches a resting one, and every state change goes through the
landed `transition()` kernel against the closed `TRANSITIONS` table. The dispatch is
§3.2's, verbatim: `queued → 3/4`, `claimed → 5`, `planned → 6/7/8`, `reviewing → 8`,
`judged → 9/10`, `submitting → submit`, `approved → 11`; `remediating`, `escalated`,
`changes_requested`, `merged`, `stopped` and `superseded` rest, each through
`rest.enter_rest` (the release half of flow step 13 that is this part's).

**This module decides nothing a neighbour owns.** Every call expression to E-23 `facts`,
E-05 `carry_over`, E-07 `plan`/`run`, E-06/E-15 through the `SupplyPort` closures, E-09
`judge`, E-10 `remediate` and E-12 `comment`/`submit_review`/`merge` is §3.2's,
character for character. A neighbour's answer licenses exactly one transition; what the
answer *means* was the neighbour's decision.

**Facts are data, never instructions.** The one place PR-derived bytes pass through here
is the `Facts` value threaded to the neighbours that consume it. No PR title, body,
label or branch name is ever interpolated into a transition reason, an escalation
question, an escalation context value, or anything else this module writes or raises —
reasons and questions are built from fixed templates plus enum values, job ids and
repository names only. A crafted PR therefore has no lever on which transition is taken.

**Where §3.2 and §2's closed table disagree, the table wins.** §3.2 step 1 says a
`GithubUnavailable` from the lease claim "transitions to STOPPED", but the claim happens
while the job is `queued` and §2 licenses no `queued → stopped` edge. This module rests
the job at `queued` instead — the same resolution the landed `admit` containment applies
to §3.1's unconditional-stop sentence: never mint an unlicensed edge. The job is
re-offered on a later tick, which is what `stopped` would have bought anyway.

**Raising near credentials.** `ctx` holds `deps`, which holds every live client, so it
is a frame local at every raise site in this module. `LifecycleDeps` elides its fields
from its own repr and every message built here names states, ids, kinds and enum values
only, so no raise renders a client (`errors.py`, `deps.py`).
"""

from __future__ import annotations

import json
import sqlite3
from collections.abc import Mapping
from dataclasses import dataclass, replace
from datetime import datetime
from types import MappingProxyType

from rqa.contracts import (
    Activity,
    Assurance,
    BundleFailure,
    CarriedEvidence,
    CarryOver,
    Category,
    Deny,
    Decision,
    EscalationCause,
    EvidenceState,
    Facts,
    Finding,
    GithubUnavailable,
    Grant,
    Job,
    JobStatus,
    Judgement,
    LeaseTaken,
    Location,
    Mutation,
    PanelResult,
    Plan,
    RemediationPushed,
    RemediationRefused,
    RecordReader,
    Remedy,
    RouteCursor,
    Snapshot,
    Stale,
    ValidationFailure,
)
from rqa.lifecycle.deps import LifecycleDeps
from rqa.lifecycle.errors import LifecycleError
from rqa.lifecycle.rest import enter_rest
from rqa.lifecycle.states import as_status
from rqa.lifecycle.transition import transition
from rqa.record.reader import SQLiteRecordReader

__all__ = ["drive", "Cascade", "read_prior_record", "DISPATCH"]

#: §9 RQA-NFR-007: step 10a's transition reason, written verbatim `[ADR-D assumed]`.
NO_CONFORMING_TRANSITION = "no source-conforming next transition was available"

#: The stop reason for an E-23 `GithubUnavailable` (§3.2 step 2).
FACTS_UNAVAILABLE = "facts unavailable"


def read_prior_record(*, job: Job, connection: sqlite3.Connection) -> RecordReader:
    """The predecessor-record reader E-05's call expression names (§3.2 step 3).

    P-12's reader over the caller's own connection — §1's licensed import of
    `rqa.record`'s names. Only its `trusted_prefix` makes a trust claim, and P-13 is
    the one who calls it; this function decides nothing about the prior record.
    """
    del job  # identifies the call site in §3.2's expression; the reader is per-connection
    return SQLiteRecordReader(connection)


@dataclass(frozen=True)
class _Port:
    """The concrete `SupplyPort` P-02 constructs over P-05's functions (§3.2).

    `rqa/edges.py` landed `SupplyPort` as a `typing.Protocol`, which cannot be
    instantiated, while §3.2's sample constructs one; a frozen dataclass whose three
    fields carry §3.2's verbatim closures satisfies the Protocol structurally and is
    the only P-02-local shape involved. P-06 sees exactly the three positional-view
    methods §9's E-07 comment states.
    """

    route: object
    reserve: object
    consumed: object


@dataclass
class Cascade:
    """The per-admission context `(snapshot, facts, carry, plan, panel, judgement)`
    (§3.1), plus the verdict grant step 10 hands to the submit step.

    Deliberately not frozen: it is this module's working state for one cascade, not a
    value exchanged with a neighbour. Every value *in* it is a shared frozen dataclass.
    """

    deps: LifecycleDeps
    snapshot: Snapshot | None = None
    facts: Facts | None = None
    carry: CarryOver | None = None
    plan: Plan | None = None
    panel: PanelResult | None = None
    judgement: Judgement | None = None
    verdict_grant: Grant | None = None


def drive(job: Job, *, deps: LifecycleDeps, cascade: Cascade | None = None) -> Job:
    """§3.2's dispatch loop: run the current status's step until a resting status.

    Returns the job as it rests. Persistence failures propagate to the caller's
    containment boundary (`admit` §3.1, `resume` §3.3); neighbour `*Error` exceptions
    propagate unchanged.
    """
    ctx = cascade if cascade is not None else Cascade(deps=deps)
    while True:
        state = as_status(job.status, what="jobs.status")
        step = DISPATCH.get(state)
        if step is None:
            # remediating, escalated, changes_requested, merged, stopped, superseded.
            return enter_rest(job, snapshot=ctx.snapshot, deps=deps)
        job, resting = step(job, ctx)
        if resting:
            # A step that rests in place: queued after LeaseTaken, approved without a
            # merge. The rest check still runs (§3.2).
            return enter_rest(job, snapshot=ctx.snapshot, deps=deps)


# --------------------------------------------------------------------------
# Steps 3-5 — snapshot, claim, carry-over and plan (§3.2)
# --------------------------------------------------------------------------


def step3(job: Job, ctx: Cascade) -> tuple[Job, bool]:
    """Step 3 (+3a): pin the snapshot, obtain review authority, claim the lease.

    Dispatch row `queued → 3/4`; step 4's one E-23 call runs "at claim", which the
    loop reaches through `claimed → 5` (`step5` fetches facts first).
    """
    deps = ctx.deps
    snapshot = deps.policy.snapshot_for(
        repo=job.repo, job=job, store=deps.policy.store, record=deps.record
    )
    if isinstance(snapshot, ValidationFailure):
        _escalate_authority_requirement(
            job,
            ctx,
            detail="policy validation failed",
        )
        return (
            transition(
                job,
                JobStatus.ESCALATED,
                reason="policy validation failed; authority requirement escalated",
                connection=deps.connection,
                record=deps.record,
            ),
            False,
        )
    if not isinstance(snapshot, Snapshot):
        raise LifecycleError(f"E-03 returned {type(snapshot).__name__}")
    ctx.snapshot = snapshot

    answer = deps.authority.grant(
        repo=job.repo,
        activity=Activity.REVIEW,
        snapshot=snapshot,
        job_id=job.id,
        categories=None,
        record=deps.record,
        github=deps.authority.github,
        store=deps.authority.store,
    )
    if isinstance(answer, Deny):
        # 3a. The escalation is raised against the snapshot the job is being pinned
        # to in this same transaction (`P-11-escalation.md` §2 reads it off the job).
        _escalate_authority_requirement(
            job if job.snapshot_hash is not None else replace(job, snapshot_hash=snapshot.hash),
            ctx,
            detail=f"review denied ({answer.reason.value})",
        )
        return (
            transition(
                job,
                JobStatus.ESCALATED,
                reason=f"review authority denied ({answer.reason.value})",
                connection=deps.connection,
                record=deps.record,
                snapshot_hash=snapshot.hash,
            ),
            False,
        )
    if not isinstance(answer, Grant):
        raise LifecycleError(f"E-04 returned {type(answer).__name__}")

    claimed = deps.claim_lease(job=job, grant=answer, record=deps.record)
    if isinstance(claimed, LeaseTaken):
        # §3.2 step 1: "LeaseTaken returns the unchanged QUEUED job."
        return job, True
    if isinstance(claimed, GithubUnavailable):
        # §3.2 step 1 says STOPPED, but §2's closed table licenses no queued → stopped
        # edge — see the module docstring. The job rests queued and is re-offered.
        return job, True
    if not isinstance(claimed, Mutation) or not claimed.accepted:
        raise LifecycleError(f"E-01 claim returned {type(claimed).__name__}, not accepted")
    return (
        transition(
            job,
            JobStatus.CLAIMED,
            reason="review lease claimed under review grant",
            connection=deps.connection,
            record=deps.record,
            snapshot_hash=snapshot.hash,
        ),
        False,
    )


def step4(job: Job, ctx: Cascade) -> Facts | GithubUnavailable:
    """Step 4: the one E-23 call per admission cascade, verbatim (§3.1)."""
    facts = ctx.deps.github.facts(job=job, record=ctx.deps.record)
    if isinstance(facts, Facts):
        ctx.facts = facts
    return facts


def step5(job: Job, ctx: Cascade) -> tuple[Job, bool]:
    """Step 5: facts at claim, carry-over, plan, then `CLAIMED → PLANNED`."""
    deps = ctx.deps
    if ctx.facts is None:
        got = step4(job, ctx)
        if isinstance(got, GithubUnavailable):
            # §3.2 step 2: a value, never a success state. `claimed → stopped` is licensed.
            return _stop(job, ctx, reason=FACTS_UNAVAILABLE), False
    facts = ctx.facts
    if facts is None:
        raise LifecycleError("E-23 returned neither Facts nor GithubUnavailable")

    snapshot = _ensure_snapshot(job, ctx)
    if isinstance(snapshot, ValidationFailure):
        _escalate_authority_requirement(job, ctx, detail="policy validation failed")
        return (
            transition(
                job,
                JobStatus.ESCALATED,
                reason="policy validation failed; authority requirement escalated",
                connection=deps.connection,
                record=deps.record,
            ),
            False,
        )

    if job.predecessor_job is not None:
        carry = deps.reuse.carry_over(
            job=job, prior=read_prior_record(job=job, connection=deps.connection), facts=facts,
            snapshot=snapshot, record=deps.record,
        )
    else:
        # §3.2 step 3: "Without a predecessor it starts with empty CarryOver."
        carry = CarryOver(reused=(), regenerated=(), reasons={}, source_job=None)

    plan = deps.harness.plan(
        job=job, facts=facts, snapshot=snapshot, carry=carry, record=deps.record,
    )

    if job.predecessor_job is None:
        # §3.2 step 3: the no-predecessor replacement, verbatim fields.
        carry = CarryOver(reused=(), regenerated=plan.obligations,
                          reasons={id: "no_predecessor" for id in plan.obligations},
                          source_job=None)

    ctx.carry = carry
    ctx.plan = plan
    # §3.2 step 4: plan and final carry become durable with this commit, then PLANNED,
    # unconditionally.
    return (
        transition(
            job,
            JobStatus.PLANNED,
            reason="plan and carry-over recorded",
            connection=deps.connection,
            record=deps.record,
            snapshot_hash=snapshot.hash,
        ),
        False,
    )


# --------------------------------------------------------------------------
# Steps 6-8 — one panel call, then judgement (§3.2)
# --------------------------------------------------------------------------


def step6(job: Job, ctx: Cascade) -> tuple[Job, bool]:
    """Step 6 (dispatch row `planned → 6/7/8`): the carry-only branch judges from an
    empty complete panel with zero `run` calls (§3.2 step 4, 5a); a non-empty
    regenerated set transitions `PLANNED → REVIEWING` immediately before the loop
    makes its one `run` call in `step7`."""
    deps = ctx.deps
    outcome = _require_context(job, ctx)
    if outcome is not None:
        return outcome
    carry, facts = ctx.carry, ctx.facts
    if carry is None or facts is None or ctx.plan is None or ctx.snapshot is None:
        raise LifecycleError(f"planned job {job.id!r} has an incomplete cascade context")

    if carry.regenerated == ():
        # 5a. No reservation was requested, so no bound was reached (§3.2 step 4).
        panel = PanelResult(attempts=(), complete=True, incomplete_reason=None,
                            evidence_cutoff=facts.fetched_at, bound_reached=False)
        ctx.panel = panel
        judgement = step8(job, ctx, panel=panel, decision=None)
        ctx.judgement = judgement
        return (
            transition(
                job,
                JobStatus.JUDGED,
                reason="judged from carried evidence",
                connection=deps.connection,
                record=deps.record,
            ),
            False,
        )

    return (
        transition(
            job,
            JobStatus.REVIEWING,
            reason="panel run started",
            connection=deps.connection,
            record=deps.record,
        ),
        False,
    )


def step7(job: Job, ctx: Cascade) -> tuple[Job, bool]:
    """Step 7 (dispatch row `reviewing → 8`): the one `run` call when this cascade has
    not yet made it, then judgement.

    A crash-recovered `reviewing` job whose panel already completed re-reads the
    recorded `panel` entry instead of paying for a second run — §3.3's own
    reconstruction, applied at the state flow-step-13 recovery re-enters. One with no
    recorded panel lost its run to the rollback and makes this cascade's single call.
    """
    deps = ctx.deps
    outcome = _require_context(job, ctx)
    if outcome is not None:
        return outcome
    facts, snapshot, plan, carry = ctx.facts, ctx.snapshot, ctx.plan, ctx.carry
    if facts is None or snapshot is None or plan is None or carry is None:
        raise LifecycleError(f"reviewing job {job.id!r} has an incomplete cascade context")

    panel = ctx.panel
    if panel is None:
        panel = _recorded_panel(job, ctx)
    if panel is None:
        # §3.2's SupplyPort construction and the one E-07 run call, verbatim.
        cursor = RouteCursor(excluded_families=frozenset(), excluded_routes=frozenset())
        supply = _Port(
            route=lambda obligation, cursor: deps.supply.route(
                job=job, obligation=obligation, snapshot=snapshot, facts=facts, cursor=cursor,
                prober=deps.supply.prober, breakers=deps.supply.breakers,
            ),
            reserve=lambda plan, route: deps.supply.reserve(
                job=job, plan=plan, route=route, snapshot=snapshot, spend=deps.supply.spend,
            ),
            consumed=lambda attempt, reading, reservation: deps.supply.consumed(
                job=job, attempt=attempt, reading=reading, reservation=reservation,
                record=deps.record, spend=deps.supply.spend, breakers=deps.supply.breakers,
            ),
        )
        panel_or_failure = deps.harness.run(
            job=job, plan=plan, facts=facts, snapshot=snapshot, supply=supply,
            state_dir=deps.state_dir, record=deps.record,
        )
        if isinstance(panel_or_failure, BundleFailure):
            return _stop(job, ctx, reason="bundle incomplete"), False
        if not isinstance(panel_or_failure, PanelResult):
            raise LifecycleError(f"E-07 run returned {type(panel_or_failure).__name__}")
        panel = panel_or_failure

    if not panel.complete:
        # §3.2's total map: exhausted → STOPPED, budget → STOPPED, bundle → STOPPED.
        if panel.incomplete_reason not in ("exhausted", "budget", "bundle"):
            raise LifecycleError(
                f"incomplete panel carries unknown reason {panel.incomplete_reason!r}"
            )
        return _stop(job, ctx, reason=f"panel incomplete ({panel.incomplete_reason})"), False
    if panel.incomplete_reason is not None:
        raise LifecycleError(
            f"complete panel carries incomplete_reason {panel.incomplete_reason!r}"
        )

    ctx.panel = panel
    judgement = step8(job, ctx, panel=panel, decision=None)
    ctx.judgement = judgement
    return (
        transition(
            job,
            JobStatus.JUDGED,
            reason="judgement recorded",
            connection=deps.connection,
            record=deps.record,
        ),
        False,
    )


def step8(job: Job, ctx: Cascade, *, panel: PanelResult, decision: Decision | None) -> Judgement:
    """Step 8: the E-09 call, verbatim (§3.2). `judge` writes the single `judgement`
    entry; this part never duplicates it."""
    deps = ctx.deps
    result = deps.judgement.judge(
        job=job, plan=ctx.plan, panel=panel, carry=ctx.carry, facts=ctx.facts,
        snapshot=ctx.snapshot, decision=decision, record=deps.record,
    )
    if not isinstance(result, Judgement):
        raise LifecycleError(f"E-09 returned {type(result).__name__}")
    return result


# --------------------------------------------------------------------------
# Steps 9-11 — act, submit, merge (§3.2)
# --------------------------------------------------------------------------


def step9(job: Job, ctx: Cascade) -> tuple[Job, bool]:
    """Step 9 (+10's authority half): act on the judgement. Exactly one branch runs.

    A crash-recovered `judged` job consumes its recorded `judgement` entry and never
    calls E-09 again (§5's read protocol, §8 T18).
    """
    deps = ctx.deps
    judgement = ctx.judgement
    if judgement is None:
        judgement = _recorded_judgement(job, ctx)
        ctx.judgement = judgement

    if judgement.disposition == "remediate":
        return _remediate(job, ctx, judgement)

    if judgement.disposition == "escalate":
        # "escalate raises every named cause then ESCALATED" (§3.2).
        for cause, detail in judgement.escalation_causes:
            _raise_escalation(job, ctx, cause=cause, question=detail, context={"cause": cause.value})
        causes = ", ".join(cause.value for cause, _ in judgement.escalation_causes) or "unnamed"
        return (
            transition(
                job,
                JobStatus.ESCALATED,
                reason=f"escalated: {causes}",
                connection=deps.connection,
                record=deps.record,
            ),
            False,
        )

    if judgement.disposition not in ("approve", "request_changes"):
        raise LifecycleError(f"judgement carries unknown disposition {judgement.disposition!r}")

    # Step 10: verdict authority for the activity the judgement calls for.
    activity = (
        Activity.APPROVE if judgement.disposition == "approve" else Activity.REQUEST_CHANGES
    )
    answer = _grant(job, ctx, activity=activity)
    if isinstance(answer, Deny):
        # 10a: the authority-requirement path — ADR-0061's "RQA is not permitted to
        # act". Comment the rendering where allowed, escalate, and record the
        # verbatim RQA-NFR-007 reason.
        return _authority_requirement_escalation(job, ctx, denied=activity), False
    ctx.verdict_grant = answer
    return (
        transition(
            job,
            JobStatus.SUBMITTING,
            reason="verdict authority granted",
            connection=deps.connection,
            record=deps.record,
        ),
        False,
    )


def submit(job: Job, ctx: Cascade) -> tuple[Job, bool]:
    """Step 10b's submission half (dispatch row `submitting → submit`)."""
    deps = ctx.deps
    judgement = ctx.judgement
    if judgement is None:
        judgement = _recorded_judgement(job, ctx)
        ctx.judgement = judgement
    if judgement.disposition not in ("approve", "request_changes"):
        raise LifecycleError(
            f"submitting job {job.id!r} carries a {judgement.disposition!r} judgement"
        )
    activity = (
        Activity.APPROVE if judgement.disposition == "approve" else Activity.REQUEST_CHANGES
    )
    grant = ctx.verdict_grant
    if not isinstance(grant, Grant) or grant.activity is not activity:
        # A crash-recovered submitting job re-establishes its verdict authority; a
        # submission never rides anything but a `Grant` for this exact activity.
        answer = _grant(job, ctx, activity=activity)
        if isinstance(answer, Deny):
            return _authority_requirement_escalation(job, ctx, denied=activity), False
        grant = answer
        ctx.verdict_grant = grant

    state = "APPROVE" if judgement.disposition == "approve" else "REQUEST_CHANGES"
    body = _rendered_body(job, ctx)
    result = deps.github.submit_review(
        job=job, state=state, body=body, grant=grant, record=deps.record
    )
    if isinstance(result, Mutation):
        if not result.accepted:
            raise LifecycleError("E-12 submit_review returned a non-accepted Mutation")
        target = (
            JobStatus.APPROVED if judgement.disposition == "approve"
            else JobStatus.CHANGES_REQUESTED
        )
        return (
            transition(
                job,
                target,
                reason=f"review submitted: {judgement.disposition}",
                connection=deps.connection,
                record=deps.record,
            ),
            False,
        )
    if isinstance(result, Stale):
        # §3.2: Stale escalates EVIDENCE_GAP.
        _raise_escalation(
            job,
            ctx,
            cause=EscalationCause.EVIDENCE_GAP,
            question="review submission found the head stale; the evidence no longer matches",
            context={"reason": result.reason},
        )
        return (
            transition(
                job,
                JobStatus.ESCALATED,
                reason="submission stale; evidence gap escalated",
                connection=deps.connection,
                record=deps.record,
            ),
            False,
        )
    if isinstance(result, GithubUnavailable):
        return _stop(job, ctx, reason="github unavailable"), False
    raise LifecycleError(f"E-12 submit_review returned {type(result).__name__}")


def step11(job: Job, ctx: Cascade) -> tuple[Job, bool]:
    """Step 11: merge, gated the same way as every other activity (RQA-FR-029).

    A merge that is not configured is P-08's `NOT_ENABLED` deny, so "the record says
    which" (flow step 11) holds without this part reading policy content. `Stale` and
    `GithubUnavailable` rest at `approved`: §2 licenses no other edge from it, the
    review is complete either way, and an idempotent merge is retried on a later rest.
    """
    deps = ctx.deps
    snapshot = _pinned_snapshot(job, ctx)
    answer = deps.authority.grant(
        repo=job.repo,
        activity=Activity.MERGE,
        snapshot=snapshot,
        job_id=job.id,
        categories=None,
        record=deps.record,
        github=deps.authority.github,
        store=deps.authority.store,
    )
    if isinstance(answer, Deny):
        return job, True
    if not isinstance(answer, Grant):
        raise LifecycleError(f"E-04 returned {type(answer).__name__}")
    result = deps.github.merge(job=job, grant=answer, record=deps.record)
    if isinstance(result, Mutation):
        if not result.accepted:
            raise LifecycleError("E-12 merge returned a non-accepted Mutation")
        return (
            transition(
                job,
                JobStatus.MERGED,
                reason="merged under merge grant",
                connection=deps.connection,
                record=deps.record,
            ),
            False,
        )
    if isinstance(result, (Stale, GithubUnavailable)):
        return job, True
    raise LifecycleError(f"E-12 merge returned {type(result).__name__}")


#: §3.2's dispatch table. Steps 12a/12b are `resume.py`'s; the resting statuses —
#: remediating, escalated, changes_requested, merged, stopped, superseded — are
#: deliberately absent and rest through `rest.enter_rest` (flow step 13's release half).
DISPATCH: Mapping[JobStatus, object] = MappingProxyType(
    {
        JobStatus.QUEUED: step3,
        JobStatus.CLAIMED: step5,
        JobStatus.PLANNED: step6,
        JobStatus.REVIEWING: step7,
        JobStatus.JUDGED: step9,
        JobStatus.SUBMITTING: submit,
        JobStatus.APPROVED: step11,
    }
)


# --------------------------------------------------------------------------
# Step 9's remediation branch
# --------------------------------------------------------------------------


def _remediate(job: Job, ctx: Cascade, judgement: Judgement) -> tuple[Job, bool]:
    """9a: first P-07 candidate, a category-scoped grant, then the E-10 call verbatim."""
    deps = ctx.deps
    if not judgement.remediation_candidates:
        raise LifecycleError("a remediate judgement carries no remediation candidate")
    candidate = judgement.remediation_candidates[0]
    finding = next((f for f in judgement.findings if f.id == candidate), None)
    if finding is None:
        raise LifecycleError("the first remediation candidate names no recorded finding")

    facts = _require_facts(job, ctx)
    if facts is None:
        return _stop(job, ctx, reason=FACTS_UNAVAILABLE), False
    snapshot = _pinned_snapshot(job, ctx)

    answer = deps.authority.grant(
        repo=job.repo,
        activity=Activity.REMEDIATE,
        snapshot=snapshot,
        job_id=job.id,
        categories=finding.categories,
        record=deps.record,
        github=deps.authority.github,
        store=deps.authority.store,
    )
    if isinstance(answer, Deny):
        # §3.2: "A remediation Deny similarly escalates with AUTHORITY_REQUIREMENT."
        _escalate_authority_requirement(
            job, ctx, detail=f"remediation denied ({answer.reason.value})"
        )
        return (
            transition(
                job,
                JobStatus.ESCALATED,
                reason=f"remediation authority denied ({answer.reason.value})",
                connection=deps.connection,
                record=deps.record,
            ),
            False,
        )
    if not isinstance(answer, Grant):
        raise LifecycleError(f"E-04 returned {type(answer).__name__}")

    job = transition(
        job,
        JobStatus.REMEDIATING,
        reason="mechanical remediation granted",
        connection=deps.connection,
        record=deps.record,
    )
    push = deps.remediation.remediate(
        job=job, finding=finding, grant=answer, facts=facts, snapshot=snapshot,
        state_dir=deps.state_dir, runner=deps.runner, record=deps.record,
    )
    if isinstance(push, RemediationPushed):
        # §3.2: "RemediationPushed leaves the job REMEDIATING" — the push is observed
        # as a new head on the next tick.
        return job, False
    if isinstance(push, RemediationRefused):
        _raise_escalation(
            job,
            ctx,
            cause=EscalationCause.EVIDENCE_GAP,
            question=f"remediation was refused ({push.reason.value}); a human must judge",
            context={"reason": push.reason.value},
        )
        return (
            transition(
                job,
                JobStatus.ESCALATED,
                reason=f"remediation refused ({push.reason.value}); evidence gap escalated",
                connection=deps.connection,
                record=deps.record,
            ),
            False,
        )
    raise LifecycleError(f"E-10 returned {type(push).__name__}")


# --------------------------------------------------------------------------
# Step 10a — the authority-requirement path (ADR-0061 / AC14)
# --------------------------------------------------------------------------


def _authority_requirement_escalation(job: Job, ctx: Cascade, *, denied: Activity) -> Job:
    """10a: comment the judgement's rendering where allowed, raise the authority
    requirement, then transition with §9's verbatim RQA-NFR-007 reason."""
    deps = ctx.deps
    comment_grant = _grant(job, ctx, activity=Activity.COMMENT)
    if isinstance(comment_grant, Grant):
        body = _rendered_body(job, ctx)
        if body:
            posted = deps.github.comment(
                job=job, body=body, grant=comment_grant, record=deps.record
            )
            if not isinstance(posted, (Mutation, GithubUnavailable)):
                raise LifecycleError(f"E-12 comment returned {type(posted).__name__}")
            # A GithubUnavailable comment is a lost courtesy, never a lost escalation.
    _escalate_authority_requirement(
        job, ctx, detail=f"verdict activity {denied.value} denied"
    )
    return transition(
        job,
        JobStatus.ESCALATED,
        reason=NO_CONFORMING_TRANSITION,
        connection=deps.connection,
        record=deps.record,
    )


# --------------------------------------------------------------------------
# Shared helpers
# --------------------------------------------------------------------------


def _stop(job: Job, ctx: Cascade, *, reason: str) -> Job:
    return transition(
        job,
        JobStatus.STOPPED,
        reason=reason,
        connection=ctx.deps.connection,
        record=ctx.deps.record,
    )


def _grant(job: Job, ctx: Cascade, *, activity: Activity) -> Grant | Deny:
    """One E-04 call against the pinned snapshot, with the injected probe and store."""
    answer = ctx.deps.authority.grant(
        repo=job.repo,
        activity=activity,
        snapshot=_pinned_snapshot(job, ctx),
        job_id=job.id,
        categories=None,
        record=ctx.deps.record,
        github=ctx.deps.authority.github,
        store=ctx.deps.authority.store,
    )
    if not isinstance(answer, (Grant, Deny)):
        raise LifecycleError(f"E-04 returned {type(answer).__name__}")
    return answer


def _raise_escalation(
    job: Job, ctx: Cascade, *, cause: EscalationCause, question: str, context: Mapping
) -> None:
    """One E-11 raise. The store rides the injected client the way `deps.supply`
    carries its prober, breakers and spend (§3.2's closures)."""
    ctx.deps.escalation.raise_(
        job=job,
        cause=cause,
        question=question,
        context=context,
        record=ctx.deps.record,
        store=ctx.deps.escalation.store,
    )


def _escalate_authority_requirement(job: Job, ctx: Cascade, *, detail: str) -> None:
    _raise_escalation(
        job,
        ctx,
        cause=EscalationCause.AUTHORITY_REQUIREMENT,
        question=f"RQA lacks authority on {job.repo}: {detail}",
        context={"repo": job.repo, "detail": detail},
    )


def _require_facts(job: Job, ctx: Cascade) -> Facts | None:
    if ctx.facts is not None:
        return ctx.facts
    got = step4(job, ctx)
    return got if isinstance(got, Facts) else None


def _ensure_snapshot(job: Job, ctx: Cascade) -> Snapshot | ValidationFailure:
    if ctx.snapshot is not None:
        return ctx.snapshot
    snapshot = ctx.deps.policy.snapshot_for(
        repo=job.repo, job=job, store=ctx.deps.policy.store, record=ctx.deps.record
    )
    if isinstance(snapshot, Snapshot):
        ctx.snapshot = snapshot
        return snapshot
    if isinstance(snapshot, ValidationFailure):
        return snapshot
    raise LifecycleError(f"E-03 returned {type(snapshot).__name__}")


def _pinned_snapshot(job: Job, ctx: Cascade) -> Snapshot | None:
    """The pinned snapshot, or None when the job holds no pin. Never a replacement:
    E-03's pinned branch answers from the archive without a live read."""
    if ctx.snapshot is not None:
        return ctx.snapshot
    if job.snapshot_hash is None:
        return None
    snapshot = ctx.deps.policy.snapshot_for(
        repo=job.repo, job=job, store=ctx.deps.policy.store, record=ctx.deps.record
    )
    if not isinstance(snapshot, Snapshot):
        raise LifecycleError(
            f"E-03 answered a pinned read for job {job.id!r} with {type(snapshot).__name__}"
        )
    ctx.snapshot = snapshot
    return snapshot


def _require_context(job: Job, ctx: Cascade) -> tuple[Job, bool] | None:
    """Rebuild the (facts, snapshot, plan, carry) context for a crash-recovered
    `planned`/`reviewing` job; the in-cascade path finds everything already threaded.

    Returns a `(job, resting)` outcome when re-establishing the context itself forces
    a transition (facts unavailable → stopped; validation failure → escalated), or
    `None` when the context is complete and the step may proceed.
    """
    deps = ctx.deps
    if ctx.facts is None:
        got = step4(job, ctx)
        if isinstance(got, GithubUnavailable):
            return _stop(job, ctx, reason=FACTS_UNAVAILABLE), False
    snapshot = _ensure_snapshot(job, ctx)
    if isinstance(snapshot, ValidationFailure):
        _escalate_authority_requirement(job, ctx, detail="policy validation failed")
        return (
            transition(
                job,
                JobStatus.ESCALATED,
                reason="policy validation failed; authority requirement escalated",
                connection=deps.connection,
                record=deps.record,
            ),
            False,
        )
    if ctx.plan is None:
        ctx.plan = _recorded_plan(job, ctx)
    if ctx.carry is None:
        ctx.carry = _recorded_carry(job, ctx)
    return None


# --------------------------------------------------------------------------
# §5's record read-back: reconstruction of recorded neighbour values
# --------------------------------------------------------------------------


def _latest_payload(job: Job, ctx: Cascade, *, kind: str) -> Mapping | None:
    """§5's read protocol, verbatim shape: the latest entry of `kind` for this job."""
    row = ctx.deps.connection.execute(
        "SELECT payload FROM record_entries WHERE job = ? AND kind = ? "
        "ORDER BY seq DESC LIMIT 1",
        (job.id, kind),
    ).fetchone()
    if row is None:
        return None
    try:
        decoded = json.loads(row[0])
    except (TypeError, ValueError):
        raise LifecycleError(
            f"the latest {kind!r} entry for job {job.id!r} is not decodable JSON"
        ) from None
    if not isinstance(decoded, dict):
        raise LifecycleError(f"the latest {kind!r} entry for job {job.id!r} is not an object")
    return decoded


def _recorded_plan(job: Job, ctx: Cascade) -> Plan:
    payload = _latest_payload(job, ctx, kind="plan")
    if payload is None:
        raise LifecycleError(f"job {job.id!r} is past planning but has no plan entry")
    return Plan(
        obligations=tuple(payload["obligations"]),
        omitted=dict(payload["omitted"]),
        strategy=payload["strategy"],
        participants=payload["participants"],
        risk_class=payload["risk_class"],
        head_sha=payload["head_sha"],
        snapshot_hash=payload["snapshot_hash"],
        protocol_hash=payload["protocol_hash"],
        policy_version=payload["policy_version"],
    )


def _recorded_carry(job: Job, ctx: Cascade) -> CarryOver:
    """The recorded `carry_over`, or the no-predecessor reconstruction §3.2 step 3
    makes total from the plan alone (E-05 is only ever called with a predecessor)."""
    payload = _latest_payload(job, ctx, kind="carry_over")
    if payload is None:
        if job.predecessor_job is not None:
            raise LifecycleError(
                f"job {job.id!r} has a predecessor but no carry_over entry"
            )
        plan = ctx.plan if ctx.plan is not None else _recorded_plan(job, ctx)
        return CarryOver(reused=(), regenerated=plan.obligations,
                         reasons={id: "no_predecessor" for id in plan.obligations},
                         source_job=None)
    return CarryOver(
        reused=tuple(
            CarriedEvidence(
                obligation_id=item["obligation_id"],
                state=EvidenceState(item["state"]),
                source_job=item["source_job"],
                source_judgement_seq=item["source_judgement_seq"],
                source_attestations=tuple(item["source_attestations"]),
            )
            for item in payload["reused"]
        ),
        regenerated=tuple(payload["regenerated"]),
        reasons=dict(payload["reasons"]),
        source_job=payload["source_job"],
    )


def _recorded_panel(job: Job, ctx: Cascade) -> PanelResult | None:
    """The recorded `panel` entry as §3.3's reconstruction: the recorded cutoff,
    completeness and bound, with no attempts — verdict content is not in the record."""
    payload = _latest_payload(job, ctx, kind="panel")
    if payload is None:
        return None
    return PanelResult(
        attempts=(),
        complete=payload["complete"],
        incomplete_reason=payload["incomplete_reason"],
        evidence_cutoff=datetime.fromisoformat(payload["evidence_cutoff"]),
        bound_reached=payload["bound_reached"],
    )


def _recorded_judgement(job: Job, ctx: Cascade) -> Judgement:
    """§5: "where a resumed `judged` job needs it without a fresh `judge()` call, the
    recorded `judgement`" — decoded into the shared dataclasses by field name (T18)."""
    payload = _latest_payload(job, ctx, kind="judgement")
    if payload is None:
        raise LifecycleError(f"job {job.id!r} is judged but has no judgement entry")
    return Judgement(
        obligations={key: EvidenceState(value) for key, value in payload["obligations"].items()},
        findings=tuple(_decode_finding(item) for item in payload["findings"]),
        corroborated=frozenset(payload["corroborated"]),
        blocking=frozenset(payload["blocking"]),
        attribution=dict(payload["attribution"]),
        assurance=Assurance(
            required=payload["assurance"]["required"],
            achieved=payload["assurance"]["achieved"],
        ),
        remediation_candidates=tuple(payload["remediation_candidates"]),
        escalation_causes=tuple(
            (EscalationCause(item["cause"]), item["detail"])
            for item in payload["escalation_causes"]
        ),
        disposition=payload["disposition"],
        reused_from=payload["reused_from"],
    )


def _decode_finding(item: Mapping) -> Finding:
    remedy = item["remedy"]
    return Finding(
        id=item["id"],
        categories=frozenset(Category(value) for value in item["categories"]),
        extra_tags=frozenset(item["extra_tags"]),
        location=Location(path=item["location"]["path"], line=item["location"]["line"]),
        evidence=item["evidence"],
        severity=item["severity"],
        remedy=(
            None
            if remedy is None
            else Remedy(tool=remedy["tool"], paths=tuple(remedy["paths"]), check=remedy["check"])
        ),
        behaviour_changing=item["behaviour_changing"],
        source_attempt=item["source_attempt"],
    )


def _rendered_body(job: Job, ctx: Cascade) -> str:
    """The recorded judgement's own rendering (P-07 writes `rendered_body` into its
    entry). This part posts the rendering; it never composes one — deciding how a
    judgement reads is P-07's (§7)."""
    payload = _latest_payload(job, ctx, kind="judgement")
    if payload is None:
        return ""
    body = payload.get("rendered_body")
    return body if isinstance(body, str) else ""
