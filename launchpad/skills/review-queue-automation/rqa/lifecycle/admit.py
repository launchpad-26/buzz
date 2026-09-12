"""`admit()` — E-02, `code/P-02-lifecycle.md` §3.1.

P-01 hands one job to this function and gets back the status it came to rest at. Two
things happen here and nothing else decides them: the **arrival transition**, and the
**persistence-containment boundary** around everything that follows it.

**Containment is this part's security property, not its error handling.** §3.1: "an
`AppendFailed`, `sqlite3.Error`, or `OSError` causes one `STOPPED` transition and return;
failure while committing that stop propagates. Neighbour `*Error` exceptions propagate.
No branch silently falls through." A persistence or audit failure that were instead
swallowed would let a review continue — and eventually complete authoritatively — on a
record known to be incomplete. That is the estate defect U-DISPATCH-20 recorded
(`except Exception: pass` around the ledger write) and the one this boundary exists to
make impossible. Three exception types are contained, each into a *safe stop*; everything
else propagates unchanged, so a neighbour's `*Error` can never be misreported as a stop
(§8 T5).

**Where the stop is not licensed.** §2's table is closed — "a transition not in it does
not happen" — and `stopped` is not reachable from `queued`, `changes_requested`,
`approved`, `merged`, `stopped` or `superseded`. When a contained failure happens while
the durable state is one of those, there is no safe stop to make: the rollback has
already left the last-good state intact, and the failure propagates to P-01, which
records it (`P-01-intake.md` §3 step 5) and re-offers the job on a later tick. Inventing
an edge to `stopped` would break the one guarantee the table gives; silently returning
the unchanged status would be the swallowed failure this boundary forbids.

**Steps 3-13.** §3.2's cascade is driven from inside the `try` below, so every
persistence failure it can raise is contained by the same boundary. It is the sibling
task's to build (`rqa/lifecycle/steps.py` and `rest.py`); until it lands, a job rests
where the arrival transition left it and `admit` reports *that* status rather than one it
never reached.
"""

from __future__ import annotations

import sqlite3
from dataclasses import replace

from rqa.contracts import AppendFailed, Job, JobStatus
from rqa.lifecycle.deps import LifecycleDeps
from rqa.lifecycle.errors import LifecycleError, UnknownJobError
from rqa.lifecycle.states import TRANSITIONS, as_status
from rqa.lifecycle.transition import safe_stop, transition

__all__ = ["admit"]

#: The arrival transition's reason (§3.1, `flow-review-lifecycle.md` §3 step 2).
ARRIVAL_REASON = "admitted to the review queue"


def admit(*, job: Job, deps: LifecycleDeps) -> JobStatus:
    """E-02 verbatim: write the arrival transition when necessary, drive the state
    machine until a resting status, and return that status."""
    current = job
    try:
        current = _arrive(job=job, deps=deps)
        # Steps 3-13 (§3.2) run here, inside this boundary. Until they land, the
        # arrival transition is the whole cascade and its resting status is the answer.
        return as_status(current.status, what="jobs.status")
    except (AppendFailed, sqlite3.Error, OSError) as exc:
        # The failure is already rolled back (`transition._commit`'s `with connection:`),
        # so the durable row holds the last-good state. Re-read it rather than trusting
        # the in-memory job: the cascade may have committed transitions since.
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


def _arrive(*, job: Job, deps: LifecycleDeps) -> Job:
    """§3.1's "writes the arrival `queued` transition when necessary".

    Necessary means: this job has no `transition` entry yet. That is the only durable
    evidence of arrival, and it is the same fact `rqa explain` reconstructs identity from
    (§6), so re-admitting a crash-recovered or resting job appends no second arrival.
    """
    if _has_transition_entry(job=job, connection=deps.connection):
        return job
    if as_status(job.status, what="jobs.status") is not JobStatus.QUEUED:
        raise LifecycleError(
            f"job {job.id!r} arrived at {job.status} with no recorded transition; "
            "a job with no arrival entry can only be queued"
        )
    return transition(
        job,
        JobStatus.QUEUED,
        reason=ARRIVAL_REASON,
        connection=deps.connection,
        record=deps.record,
        arrival=True,
    )


def _has_transition_entry(*, job: Job, connection: sqlite3.Connection) -> bool:
    """§5's read protocol, `kind = 'transition'`: P-12's table, read-only."""
    row = connection.execute(
        "SELECT payload FROM record_entries WHERE job = ? AND kind = 'transition' "
        "ORDER BY seq DESC LIMIT 1",
        (job.id,),
    ).fetchone()
    return row is not None


def _durable(*, job: Job, connection: sqlite3.Connection, cause: BaseException) -> Job:
    """The job as the committed table holds it, read with §5's own `jobs` lookup.

    `cause` is chained, never inspected and never rendered into a record: it is only
    there so a failure to find the row explains what was being contained when it
    happened.
    """
    row = connection.execute(
        "SELECT id, status FROM jobs WHERE repo = ? AND number = ? AND head_sha = ?",
        (job.repo, job.number, job.head_sha),
    ).fetchone()
    if row is None or row[0] != job.id:
        raise UnknownJobError(
            f"no jobs row for {job.id!r}: a contained "
            f"{type(cause).__name__} cannot be turned into a safe stop"
        ) from cause
    return replace(job, status=as_status(row[1], what="jobs.status"))


def _contained_reason(exc: BaseException) -> str:
    """The recorded reason for a contained failure: its *type*, never its message.

    An exception message can carry a path, a URL, a response body or a credential picked
    up from whatever raised it, and this string is appended to the durable record.
    Batches 2c and 3c both found credentials reachable from an exception this way. The
    type name is the operator-useful half and carries nothing; the exception itself
    reaches P-01's log through the normal channels when it propagates.
    """
    return f"persistence failure contained ({type(exc).__name__})"
