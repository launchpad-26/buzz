"""The all-due anchor cadence provider.

This module deliberately has no timer, persistent cadence state, or GitHub client.
The operating system starts RQA at a fixed interval; each invocation asks the job
store for every head newer than its latest successful anchor plus every pending
publication, then passes each job id to the injected single-job provider.  A future
``rqa anchor --all`` command can therefore construct its normal composition once and
pass ``lambda job_id: anchor_job_for(composition, job_id)`` without duplicating the
pinned-snapshot, managed-repository, grant, or retry rules.

The interval is a bound, not a promise of continuous attestation.  A record entry
written just after one OS-timer invocation remains externally unattested until the
next invocation *and* until any publication outage has cleared.  That timer interval
plus outage is the unattested window.  A failed publication is retained locally as a
pending anchor, so the next invocation retries it; no append triggers this provider.

Expected availability failures are represented by the injected single-job provider's
per-job outcome.  This loop keeps processing those outcomes independently rather than
turning one unavailable destination into a failed sweep.  Programming and persistence
errors remain visible to the caller rather than being misreported as availability.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Protocol

from rqa.contracts import Job

__all__ = [
    "AnchorDueJobs",
    "AnchorJobOutcome",
    "AnchorSweep",
    "AnchorSweepItem",
    "sweep_due_anchors",
]


class AnchorDueJobs(Protocol):
    """The read-only job-store view the cadence provider needs."""

    def anchor_due(self) -> list[Job]: ...


class AnchorJobOutcome(Protocol):
    """The common observed fields of the existing single-job anchor results."""

    job_id: str
    anchored_seq: int | None
    published: int
    pending: int


@dataclass(frozen=True)
class AnchorSweepItem:
    """One selected job and the existing composition's observed outcome for it."""

    job_id: str
    outcome: AnchorJobOutcome


@dataclass(frozen=True)
class AnchorSweep:
    """All observed per-job outcomes from one all-due cadence invocation."""

    outcomes: tuple[AnchorSweepItem, ...]


def sweep_due_anchors(
    *, jobs: AnchorDueJobs, anchor: Callable[[str], AnchorJobOutcome]
) -> AnchorSweep:
    """Run the injected single-job anchor provider once for each due job.

    ``anchor`` owns authority, snapshot, and publication handling.  In particular,
    normal unavailability returns an outcome with a pending publication rather than
    raising, so a later job is never skipped merely because an earlier destination
    is unavailable.
    """
    return AnchorSweep(
        outcomes=tuple(
            AnchorSweepItem(job_id=job.id, outcome=anchor(job.id))
            for job in jobs.anchor_due()
        )
    )
