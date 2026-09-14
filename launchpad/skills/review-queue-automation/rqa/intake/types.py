"""P-01's own result values and local cache rows — `code/P-01-intake.md` §2.

`Job` and `JobStatus` are the shared types defined only in `CONTRACTS.md` §1
and imported from `rqa.contracts`, never redefined. Everything declared here
is genuinely P-01's own: the `tick()` result shape, the admission-refusal and
per-job-failure values it reports, its one programming-error exception, and
the two local rows (`PrFactsRow`, `LeaseRow`) that never cross a part
boundary.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Literal

__all__ = [
    "TickResult",
    "AdmissionRefusal",
    "JobFailure",
    "IntakeError",
    "PrFactsRow",
    "LeaseRow",
]


@dataclass(frozen=True)
class AdmissionRefusal:
    repo: str
    reason: str  # every ValidationError in the ValidationFailure, joined
    onboarding_command: str  # f"rqa onboard {repo}"


@dataclass(frozen=True)
class JobFailure:
    job_id: str
    error: str  # repr(exc); logged, never appended to the record — §6


@dataclass(frozen=True)
class TickResult:
    outcome: Literal["swept", "sweep_already_running"]
    repos_admitted: tuple[str, ...]
    repos_refused: tuple[AdmissionRefusal, ...]
    jobs_created: tuple[str, ...]  # job ids created this tick
    jobs_dispatched: tuple[str, ...]  # job ids handed to lifecycle.admit this tick
    jobs_failed: tuple[JobFailure, ...]  # admit() raised; U-DISPATCH-22
    revisited_resting_jobs: tuple[str, ...]  # job ids added to the batch only so
    # Lifecycle can revisit a resting job (§3 step 4)


class IntakeError(Exception):
    """Programming error: this part was called wrongly, or one of its own
    invariants is broken. Never raised for an admission refusal, a lock
    contention, a lease denial, or an inventory `GithubUnavailable` — those
    are values. Not caught by Lifecycle's containment boundary."""


@dataclass(frozen=True)
class PrFactsRow:
    """A local cache of exactly the inventory facts P-01 needs: the shared
    `PrFacts` fields used for job identity, supersession and the PR-head
    destination, plus `last_seen_at` for this part's own freshness
    bookkeeping. Not a replacement definition of shared `PrFacts`."""

    repo: str
    number: int
    head_sha: str  # sole source of the observed head (U-QUEUE-14)
    base_sha: str
    head_repo: str  # copied from shared PrFacts for the actual PR head
    head_ref: str
    author: str
    labels: tuple[str, ...]
    last_seen_at: datetime  # refreshed on every inventory pass that lists this PR


@dataclass(frozen=True)
class LeaseRow:
    job_id: str
    repo: str
    number: int
    claimed_at: datetime
