"""Inventory persistence and one-job-per-revision creation — P-01 §3 step 2c."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from datetime import datetime
from sqlite3 import Connection

from rqa.contracts import Job, JobStatus, PrFacts
from rqa.intake.identity import job_id
from rqa.intake.store import JobStore, PrFactsStore
from rqa.intake.types import PrFactsRow

__all__: list[str] = []


def _ingest_inventory(
    *,
    repo: str,
    inventory: Sequence[PrFacts],
    jobs: JobStore,
    pr_facts: PrFactsStore,
    connection: Connection,
    clock: Callable[[], datetime],
) -> tuple[str, ...]:
    """Persist one complete repository inventory and return newly-created job ids.

    Each fact is committed independently after its cache upsert and possible job
    insert. GitHub-owned strings remain opaque values throughout.
    """
    created: list[str] = []
    for facts in inventory:
        pr_facts.upsert(
            PrFactsRow(
                repo=repo,
                number=facts.number,
                head_sha=facts.head_sha,
                base_sha=facts.base_sha,
                head_repo=facts.head_repo,
                head_ref=facts.head_ref,
                author=facts.author,
                labels=tuple(facts.labels),
                last_seen_at=clock(),
            )
        )

        existing = jobs.current_for_pr(repo, facts.number)
        if existing is None or existing.head_sha != facts.head_sha:
            new_job = _new_job(repo=repo, facts=facts, predecessor=existing)
            jobs.create(new_job)
            created.append(new_job.id)

        connection.commit()
    return tuple(created)


def _new_job(*, repo: str, facts: PrFacts, predecessor: Job | None) -> Job:
    return Job(
        id=job_id(repo, facts.number, facts.head_sha),
        repo=repo,
        number=facts.number,
        head_sha=facts.head_sha,
        base_sha=facts.base_sha,
        head_repo=facts.head_repo,
        head_ref=facts.head_ref,
        predecessor_job=None if predecessor is None else predecessor.id,
        predecessor_head_sha=None if predecessor is None else predecessor.head_sha,
        snapshot_hash=None,
        status=JobStatus.QUEUED,
    )
