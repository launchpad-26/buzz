"""`status()` — E-17's `rqa status`, `code/P-02-lifecycle.md` §3.4.

Answers RQA-FR-016: one of the six `Disposition` values and the reason for it, for a pull
request named by `(repo, number)`. `repo` and `number` are **positional** — E-17 is a
command surface, and §3.4 is authoritative for this callable's form (`CONTRACTS.md` §9
states E-17 in prose only).

**Read-only, and cheap.** It never calls `transition`, never touches a neighbour, and
never blocks on a lock: three ordinary `SELECT`s on the three tables §5's read protocol
permits, outside the write transaction `_commit` opens. Two calls with nothing changed in
between return field-for-field identical results (§8 T20) — the report is derived
entirely from stored rows, with no clock, no cache and no ambient state.

**Why `SUPERSEDED` is not in `DISPOSITION`.** Step 2 looks the job up by the PR's
*current* head (step 1's `pr_facts.head_sha`). A superseded job is one a later job's
`predecessor_job` points away from, so its head is by definition not the current head and
step 2 cannot return it. §3.4 step 4 states this; the `LifecycleError` below is what
happens if the stored state contradicts it, because a status this function cannot map is
a corrupted table, not a sixth answer to invent.
"""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass

from rqa.contracts import JobStatus
from rqa.lifecycle.errors import LifecycleError
from rqa.lifecycle.states import DISPOSITION, Disposition

__all__ = ["status", "StatusReport", "NotFound"]

#: §3.4 step 3 reads the latest `transition` entry for its reason. A job row can exist
#: with no entry yet — the arrival transition rolled back, or a crash between P-01's
#: `jobs.create` and E-02 — and that is a real, reportable state rather than an error:
#: the disposition is still known from `jobs.status`, only the narrative is missing.
NO_RECORDED_TRANSITION = "no recorded transition"


@dataclass(frozen=True)
class StatusReport:
    job_id: str
    internal_state: JobStatus
    disposition: Disposition
    reason: str


@dataclass(frozen=True)
class NotFound:
    repo: str
    number: int


def status(repo: str, number: int, *, connection: sqlite3.Connection) -> StatusReport | NotFound:
    """§3.4's four steps, in order."""
    # 1. The PR's current head, from P-01's `pr_facts` (P-02 is a listed reader).
    row = connection.execute(
        "SELECT head_sha FROM pr_facts WHERE repo = ? AND number = ?",
        (repo, number),
    ).fetchone()
    if row is None:
        return NotFound(repo, number)
    head_sha = row[0]

    # 2. The job for that head. No row: the PR is known but no job exists for its
    #    current head yet — the narrow window right after inventory, before admission.
    row = connection.execute(
        "SELECT id, status FROM jobs WHERE repo = ? AND number = ? AND head_sha = ?",
        (repo, number, head_sha),
    ).fetchone()
    if row is None:
        return NotFound(repo, number)
    job_id, stored_status = row[0], row[1]

    # 3. The latest `transition` entry's reason (P-12's table, read-only).
    row = connection.execute(
        "SELECT payload FROM record_entries WHERE job = ? AND kind = 'transition' "
        "ORDER BY seq DESC LIMIT 1",
        (job_id,),
    ).fetchone()
    reason = NO_RECORDED_TRANSITION if row is None else _reason(row[0], job_id=job_id)

    # 4. The report. `JobStatus(...)` and `DISPOSITION[...]` are both total over what
    #    step 2 can return; anything else is a corrupted `jobs.status`, named as such.
    try:
        internal_state = JobStatus(stored_status)
    except ValueError as exc:
        raise LifecycleError(
            f"jobs.status for {job_id!r} is not a JobStatus: {stored_status!r}"
        ) from exc
    if internal_state not in DISPOSITION:
        raise LifecycleError(
            f"job {job_id!r} is at {internal_state.value} for the current head of "
            f"{repo}#{number}; §3.4 step 4 proves that is unreachable, so the stored "
            "state is inconsistent"
        )
    return StatusReport(
        job_id,
        internal_state=internal_state,
        disposition=DISPOSITION[internal_state],
        reason=reason,
    )


def _reason(payload: object, *, job_id: str) -> str:
    """The `reason` field of a `transition` payload (§6), decoded from its JSON text.

    A payload that is not an object, or one without a `reason`, is a record this part
    wrote in a shape it does not write — `LifecycleError`, not a guessed narrative.
    """
    try:
        decoded = json.loads(payload)
    except (TypeError, ValueError) as exc:
        raise LifecycleError(
            f"the latest transition entry for job {job_id!r} is not decodable JSON"
        ) from exc
    if not isinstance(decoded, dict) or not isinstance(decoded.get("reason"), str):
        raise LifecycleError(
            f"the latest transition entry for job {job_id!r} carries no string reason"
        )
    return decoded["reason"]
