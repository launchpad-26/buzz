"""`rqa.intake` — P-01, `architecture/code/P-01-intake.md`.

Finds the work and holds the queue: gates every configured repository on a
valid, resolvable snapshot before touching it, holds the machine's exclusive
sweep lock, reads GitHub's PR inventory, creates at most one job per revision,
detects a head change and hands Lifecycle the superseded predecessor's id,
provides the GitHub-verified review-lease mechanism a `Grant` authorises
Lifecycle to drive, and hands a bounded, fairly-ordered batch of jobs to
Lifecycle — never deciding what a job means, only that it exists and whose
turn it is.

No other module in RQA imports from `rqa.intake` except through this file,
with one documented exception: `rqa.github` imports `rqa.intake.identity`
directly for `stable_hash` (§1). The public surface is exactly §1's
re-export list: `tick`, `TickResult`, `AdmissionRefusal`, `JobFailure`,
`job_id`, `stable_hash`, `GithubAdapter`, `Lease`, `JobStore`, `PrFactsStore`,
`LeaseStore`, `PrFactsRow`, `LeaseRow`, `IntakeError`. This lane (`P-01`'s
queue-primitives-and-store half, §§1-2 and §5) implements eleven of those
fourteen: `tick`, `Lease` and `GithubAdapter` are the sibling lane's
(`admission.py`, `inventory.py`, `lease.py`, `batch.py`, `tick.py`) — the
sibling appends them here once its half lands; `GithubAdapter` is re-exported
from the already-landed `rqa.github`, never redefined. An import is not a
declaration: this file defines nothing.
"""

from __future__ import annotations

from rqa.github import GithubAdapter
from rqa.intake.identity import job_id, stable_hash
from rqa.intake.lease import Lease
from rqa.intake.store import JobStore, LeaseStore, PrFactsStore
from rqa.intake.types import (
    AdmissionRefusal,
    IntakeError,
    JobFailure,
    LeaseRow,
    PrFactsRow,
    TickResult,
)
from rqa.intake.tick import tick

__all__ = [
    "tick",
    "TickResult",
    "AdmissionRefusal",
    "JobFailure",
    "job_id",
    "stable_hash",
    "GithubAdapter",
    "Lease",
    "JobStore",
    "PrFactsStore",
    "LeaseStore",
    "PrFactsRow",
    "LeaseRow",
    "IntakeError",
]
