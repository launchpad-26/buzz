"""Bounded FIFO selection plus capacity-free resting follow-up widening — P-01 §3."""

from __future__ import annotations

from rqa.contracts import Job
from rqa.intake.store import (
    DEFAULT_BATCH_SIZE,
    JobStore,
    _RESTING,
    _SWEEP_RESUMABLE,
)
from rqa.intake.types import IntakeError

__all__: list[str] = []


def _select_batch(
    *, jobs: JobStore, limit: int = DEFAULT_BATCH_SIZE
) -> tuple[tuple[Job, ...], tuple[str, ...]]:
    """Return resumable work followed by each qualifying resting job once.

    ``JobStore`` owns both status partitions and FIFO SQL. Importing its private
    sets here keeps this module tied to that one definition rather than forking a
    second copy while it assembles the two store results.
    """
    resumable = jobs.select_batch(limit=limit)
    if any(job.status not in _SWEEP_RESUMABLE for job in resumable):
        raise IntakeError("JobStore.select_batch returned a non-resumable job")

    selected = list(resumable)
    selected_ids = {job.id for job in selected}
    revisited: list[str] = []
    for job in jobs.pending_followup():
        if job.status not in _RESTING:
            raise IntakeError("JobStore.pending_followup returned a non-resting job")
        if job.id in selected_ids:
            continue
        selected.append(job)
        selected_ids.add(job.id)
        revisited.append(job.id)
    return tuple(selected), tuple(revisited)
