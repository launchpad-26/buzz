"""GitHub-verified, Grant-gated review lease callbacks — P-01 §4 E-01."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime

from rqa.contracts import Grant, Job, Mutation
from rqa.github import GithubAdapter, GithubUnavailable, LeaseTaken
from rqa.intake.store import LeaseStore
from rqa.intake.types import LeaseRow
from rqa.record import RecordWriter

__all__ = ["Lease"]


@dataclass
class Lease:
    """Maintain local lease state only after GitHub reports a verified mutation."""

    leases: LeaseStore
    github: GithubAdapter
    clock: Callable[[], datetime]

    def claim_lease(
        self, *, job: Job, grant: Grant, record: RecordWriter
    ) -> Mutation | LeaseTaken | GithubUnavailable:
        result = self.github.claim_lease(job=job, grant=grant, record=record)
        if isinstance(result, Mutation):
            self.leases.put(
                LeaseRow(
                    job_id=job.id,
                    repo=job.repo,
                    number=job.number,
                    claimed_at=self.clock(),
                )
            )
        return result

    def release_lease(
        self, *, job: Job, grant: Grant, record: RecordWriter
    ) -> Mutation | GithubUnavailable:
        result = self.github.release_lease(job=job, grant=grant, record=record)
        if isinstance(result, Mutation):
            self.leases.delete(job.repo, job.number)
        return result
