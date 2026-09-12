#!/usr/bin/env python3
"""P-01 batch assembly tests: bounded FIFO plus capacity-free resting follow-up."""

from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from rqa.contracts import Job, JobStatus  # noqa: E402
from rqa.intake.batch import _select_batch  # noqa: E402
from rqa.intake.types import IntakeError  # noqa: E402


def make_job(job_id: str, status: JobStatus) -> Job:
    return Job(
        id=job_id,
        repo="org/repo",
        number=int(job_id.rsplit("-", 1)[-1]),
        head_sha=job_id,
        base_sha="base",
        head_repo="org/repo",
        head_ref="feature",
        predecessor_job=None,
        predecessor_head_sha=None,
        snapshot_hash=None,
        status=status,
    )


class BatchStore:
    def __init__(self, resumable, followup=()) -> None:
        self.resumable = list(resumable)
        self.followup = list(followup)
        self.limits = []
        self.followup_calls = 0

    def select_batch(self, limit):
        self.limits.append(limit)
        return self.resumable[:limit]

    def pending_followup(self):
        self.followup_calls += 1
        return list(self.followup)


def test_t8_resumable_selection_forwards_the_cap_and_preserves_fifo_order() -> None:
    fifo = [make_job(f"job-{number}", JobStatus.QUEUED) for number in range(1, 5)]
    store = BatchStore(fifo)

    batch, revisited = _select_batch(jobs=store, limit=2)

    assert [job.id for job in batch] == ["job-1", "job-2"]
    assert revisited == ()
    assert store.limits == [2]
    assert store.followup_calls == 1


def test_t9_resting_followup_is_appended_once_without_consuming_capacity() -> None:
    resumable = [make_job("job-1", JobStatus.QUEUED), make_job("job-2", JobStatus.STOPPED)]
    resting = make_job("job-3", JobStatus.ESCALATED)
    duplicate_id = make_job("job-1", JobStatus.APPROVED)
    store = BatchStore(resumable, (resting, resting, duplicate_id))

    batch, revisited = _select_batch(jobs=store, limit=2)

    assert [job.id for job in batch] == ["job-1", "job-2", "job-3"]
    assert revisited == ("job-3",)


def test_store_partition_violation_is_an_intake_programming_error() -> None:
    bad_resumable = BatchStore((make_job("job-1", JobStatus.MERGED),))
    try:
        _select_batch(jobs=bad_resumable, limit=1)
    except IntakeError:
        pass
    else:  # pragma: no cover - failure report
        raise AssertionError("a non-resumable JobStore result entered the batch")

    bad_followup = BatchStore((), (make_job("job-2", JobStatus.QUEUED),))
    try:
        _select_batch(jobs=bad_followup, limit=1)
    except IntakeError:
        pass
    else:  # pragma: no cover - failure report
        raise AssertionError("a non-resting follow-up entered the batch")
