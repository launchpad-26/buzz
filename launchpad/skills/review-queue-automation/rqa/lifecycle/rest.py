"""The shared "entering a resting status" check — `code/P-02-lifecycle.md` §1, §3.2.

Every rest-capable status runs this before the cascade returns it (§3.2: "Before a
rest-capable state is returned, the existing successor/lease recovery check runs").
Two recoveries, in order:

1. **Supersession.** A successor job — one whose `predecessor_job` names this job —
   means a newer head owns this pull request. Where §2's closed table licenses it,
   the resting job transitions to `SUPERSEDED`; where it does not (`merged` and
   `superseded` are terminal), the successor is simply not this job's concern and
   nothing is minted to say otherwise.
2. **Orphaned lease.** A `leases` row for a resting job is a claim nothing will act
   on. It is released **only under a fresh review `Grant`** (§8 T19): a `Deny`
   leaves the lease visible rather than widening authority to tidy up. The grant is
   asked against the pinned snapshot, never a replacement one (§3.2) — an unpinned
   job offers `snapshot=None` and P-08's `NO_SNAPSHOT` deny leaves the lease alone.

**The `leases` column is `job_id`.** P-02 §5's `SELECT 1 FROM leases WHERE job = ?`
snippet is labelled "shown for reference, not redefinition" and does not match the
authoritative DDL: `P-01-intake.md` §5 owns the table and specifies
`job_id TEXT PRIMARY KEY, repo, number, claimed_at`, which is what `rqa/intake`
lands. This module reads the real column.

Nothing here swallows a failure: a persistence error raised by the successor
transition or the lease read propagates to the caller's containment boundary
(`admit`/`resume`), exactly like any other cascade failure.
"""

from __future__ import annotations

from rqa.contracts import (
    Activity,
    Deny,
    GithubUnavailable,
    Grant,
    Job,
    JobStatus,
    Mutation,
    Snapshot,
)
from rqa.lifecycle.deps import LifecycleDeps
from rqa.lifecycle.errors import LifecycleError
from rqa.lifecycle.states import TRANSITIONS, as_status
from rqa.lifecycle.transition import transition

__all__ = ["enter_rest"]


def enter_rest(job: Job, *, snapshot: Snapshot | None, deps: LifecycleDeps) -> Job:
    """§3.2's rest check: supersession, then orphaned-lease release. Returns the job
    as it finally rests — possibly `SUPERSEDED`, never anything else new."""
    state = as_status(job.status, what="jobs.status")

    # 1. Supersession by a successor job (§5's indexed `WHERE predecessor_job = ?`).
    successor = deps.connection.execute(
        "SELECT id FROM jobs WHERE predecessor_job = ?",
        (job.id,),
    ).fetchone()
    if successor is not None and JobStatus.SUPERSEDED in TRANSITIONS[state]:
        job = transition(
            job,
            JobStatus.SUPERSEDED,
            reason=f"superseded by successor job {successor[0]}",
            connection=deps.connection,
            record=deps.record,
        )

    # 2. Orphaned lease, released only under a fresh review Grant (§8 T19). The table
    #    is P-01's DDL: a database in which intake has never created it is a database
    #    in which no lease was ever claimed, so its absence is the same answer as an
    #    absent row — checked via the catalog, never by swallowing an error.
    table = deps.connection.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'leases'"
    ).fetchone()
    if table is None:
        return job
    leased = deps.connection.execute(
        "SELECT 1 FROM leases WHERE job_id = ?",
        (job.id,),
    ).fetchone()
    if leased is None:
        return job

    if snapshot is None and job.snapshot_hash is not None:
        # §3.2: the recovery uses the pinned snapshot, never a replacement one. E-03's
        # pinned branch answers from the archive with no live read; a job with no pin
        # offers None and P-08's NO_SNAPSHOT deny leaves the lease alone.
        pinned = deps.policy.snapshot_for(
            repo=job.repo, job=job, store=deps.policy.store, record=deps.record
        )
        if not isinstance(pinned, Snapshot):
            raise LifecycleError(
                f"E-03 answered a pinned read for job {job.id!r} with {type(pinned).__name__}"
            )
        snapshot = pinned

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
        # T19: a Deny leaves the lease visible. Releasing without authority would be
        # the exact widening the gate exists to prevent.
        return job
    if not isinstance(answer, Grant):
        raise LifecycleError(
            f"authority answered a review grant request with {type(answer).__name__}"
        )
    released = deps.release_lease(job=job, grant=answer, record=deps.record)
    if not isinstance(released, (Mutation, GithubUnavailable)):
        raise LifecycleError(
            f"release_lease returned {type(released).__name__}, which is not an E-01 result"
        )
    # A Mutation released it; a GithubUnavailable leaves it for a later rest entry.
    # Either way the resting status is unchanged.
    return job
