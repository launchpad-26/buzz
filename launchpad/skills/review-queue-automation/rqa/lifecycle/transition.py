"""`transition()` — the one function in RQA that changes a job's state.

`code/P-02-lifecycle.md` §1, §5, §6 and §8 T1-T4. Three properties are the whole point of
this module, and each has a test that fails when the guard is reverted:

1. **The table is closed.** A `to` outside `TRANSITIONS[job.status]` raises
   `IllegalTransitionError` and changes *neither* `jobs.status` *nor* `record_entries`
   (T1). The check happens before the transaction opens, so an illegal transition is not
   a rolled-back write — it is no write.
2. **The status write and its `transition` entry are one transaction.** `_commit` is the
   only place in this part that commits (§5). `UPDATE` and `INSERT` share one
   connection's implicit transaction: a failing append leaves `jobs.status` at its old
   value and a failing update leaves no entry (T2, T3). "A failed append is a failed
   transition" (`components.md` §4) is a mechanism here, not a slogan.
3. **A contained failure is a *safe stop*, never a silent continue.** `safe_stop` is the
   `AppendFailed → STOPPED` fallback §1 names. Its own failure propagates and the
   last-good state stays durable (T4). A swallowed append is a correctness defect: it
   would let a review complete authoritatively on a knowingly incomplete record.

**The two columns.** `jobs.status = ?` on every transition, and `jobs.snapshot_hash = ?`
exactly once — immediately after a successful first E-03 pin, in the same transaction as
that transition (§5; `P-03-policy.md` §3 E-03 step 9: "the caller, not `rqa.policy`,
writes `job.snapshot_hash`"). The pin is write-once per job (`container.md` §5,
U-QUEUE-10, RQA-NFR-010): a job whose `snapshot_hash` is already set keeps it, so a later
configuration edit cannot retroactively change what a completed review was judged
against. That is enforced twice — the statement is only issued when the job is unpinned,
and the statement itself carries `AND snapshot_hash IS NULL`.

**Raising inside `except`.** Every raise here either chains a persistence exception
(`sqlite3.Error`, `OSError`, `AppendFailed` — none of which carries a client or a
credential) or chains nothing at all. No message interpolates a `deps` bundle, a client
or a payload: states, ids, kinds and exception type names only (`errors.py`).
"""

from __future__ import annotations

import sqlite3
from dataclasses import replace

from rqa.contracts import Job, JobStatus, RecordWriter
from rqa.lifecycle.errors import IllegalTransitionError, UnknownJobError
from rqa.lifecycle.states import TRANSITIONS, as_status

__all__ = ["transition", "safe_stop"]


def transition(
    job: Job,
    to: JobStatus,
    *,
    reason: str,
    connection: sqlite3.Connection,
    record: RecordWriter,
    snapshot_hash: str | None = None,
    arrival: bool = False,
) -> Job:
    """Move `job` to `to`, atomically with the `transition` entry that records it.

    `job` and `to` are positional (§8 T1's `transition(job, to, ...)`); everything else is
    keyword-only.

    `reason` is the operator-facing account written into the entry and read back by
    `status()` (§3.4 step 3). `connection` and `record` are the caller's — the *same*
    connection the writer was built over, which is what makes one transaction possible.

    `snapshot_hash` is E-03's pin, offered on the transition that follows a successful
    first pin. It is written only if this job has none; a pinned job keeps its hash.

    `arrival=True` is §3.1's arrival case: the job's first `transition` entry, written
    with `from_state: None` (§6). It is the one edge not in §2's table, because a job
    that has just arrived has no previous state to leave; it is accepted only for
    `QUEUED → QUEUED`, so it can never be used to bypass the table for anything else.

    Returns the job as it now is — the same frozen `Job` with its new status, and its
    pinned hash if this call pinned it — so the caller threads forward the state it just
    committed rather than the state it had.
    """
    current = as_status(job.status, what="job.status")
    target = as_status(to, what="to")

    if arrival:
        if current is not JobStatus.QUEUED or target is not JobStatus.QUEUED:
            raise IllegalTransitionError(
                "the arrival transition is queued -> queued only; "
                f"got {current.value} -> {target.value} for job {job.id!r}"
            )
        from_state: str | None = None
    else:
        if target not in TRANSITIONS[current]:
            raise IllegalTransitionError(
                f"{current.value} -> {target.value} is not in the closed transition "
                f"table for job {job.id!r}; {current.value} allows "
                f"{sorted(status.value for status in TRANSITIONS[current])}"
            )
        from_state = current.value

    pin = snapshot_hash if job.snapshot_hash is None else None
    _commit(job, target, from_state, reason, connection=connection, record=record, snapshot_hash=pin)
    if pin is None:
        return replace(job, status=target)
    return replace(job, status=target, snapshot_hash=pin)


def safe_stop(
    job: Job,
    *,
    reason: str,
    connection: sqlite3.Connection,
    record: RecordWriter,
) -> Job:
    """The `AppendFailed → safe-stop` fallback (§1, §3.1): one `STOPPED` transition.

    Called from `admit`'s containment boundary after a persistence failure has already
    been rolled back, so the state it stops from is the durable last-good one. It is an
    ordinary `transition()` — same table check, same one transaction — which is why "the
    fallback attempt is itself inside the same `with connection:` discipline" (§9,
    RQA-NFR-010) holds, and why a failure *here* propagates rather than being contained
    again (T4). There is no second fallback: two failed persistence attempts is a
    machine that cannot record what it is doing, and continuing would be the silent
    continue this part exists to prevent.
    """
    return transition(job, JobStatus.STOPPED, reason=reason, connection=connection, record=record)


def _commit(
    job: Job,
    to: JobStatus,
    from_state: str | None,
    reason: str,
    *,
    connection: sqlite3.Connection,
    record: RecordWriter,
    snapshot_hash: str | None = None,
) -> None:
    """§5's transaction boundary, verbatim, plus §5's write-once `snapshot_hash` pin.

    `with connection:` BEGINs on the first statement, COMMITs on a clean exit and ROLLBACKs
    and re-raises on any exception — stdlib `sqlite3`'s own transaction semantics, nothing
    this part adds. `record.append` never commits or rolls back itself (`P-12-record.md`
    §3.1); this is the only place in this part that does.

    `snapshot_hash` is `None` on every transition but the first pin, and the statement is
    then not issued at all: §5's "writes `jobs.status` … and `jobs.snapshot_hash` exactly
    once" is two statements on exactly one transition per job and one on every other.
    """
    with connection:
        # The one write: jobs.status = the new state; on the first pin only,
        # jobs.snapshot_hash = that pin, in this same transaction (§5).
        cursor = connection.execute(
            "UPDATE jobs SET status = ? WHERE id = ?",
            (to.value, job.id),
        )
        if cursor.rowcount != 1:
            # A status write that matched no row is a silent no-op, and a silent no-op
            # here is a job the record says moved and the table says did not.
            raise UnknownJobError(
                f"no jobs row for {job.id!r}: the {to.value} transition matched "
                f"{cursor.rowcount} rows"
            )
        if snapshot_hash is not None:
            connection.execute(
                "UPDATE jobs SET snapshot_hash = ? WHERE id = ? AND snapshot_hash IS NULL",
                (snapshot_hash, job.id),
            )
        record.append(
            job.id,
            "transition",
            {
                "from_state": from_state,
                "to_state": to.value,
                "reason": reason,
                "repo": job.repo,
                "number": job.number,
                "head_sha": job.head_sha,
                "base_sha": job.base_sha,
                "predecessor_job": job.predecessor_job,
            },
        )

