"""E-21 tick orchestration — P-01 §3's full repository sweep and dispatch."""

from __future__ import annotations

import errno
import sys
from collections.abc import Callable, Sequence
from datetime import datetime, timezone
from pathlib import Path
from sqlite3 import Connection

from rqa.contracts import ProcessRunner
from rqa.github import GithubAdapter, GithubUnavailable
from rqa.intake.admission import _check_admission
from rqa.intake.batch import _select_batch
from rqa.intake.inventory import _ingest_inventory
from rqa.intake.lease import Lease
from rqa.intake.lock import acquire
from rqa.intake.store import DEFAULT_BATCH_SIZE, JobStore, LeaseStore, PrFactsStore
from rqa.intake.types import IntakeError, JobFailure, TickResult
from rqa.lifecycle import LifecycleDeps, admit
from rqa.lifecycle.deps import (
    AuthorityClient,
    EscalationClient,
    HarnessClient,
    JudgementClient,
    PolicyClient,
    RemediationClient,
    ReuseClient,
    SupplyClient,
)
from rqa.record import AppendFailed, RecordWriter

__all__ = ["tick"]


def utcnow() -> datetime:
    """Return an aware UTC timestamp for inventory and lease persistence."""
    return datetime.now(timezone.utc)


def tick_log(message: str) -> None:
    """Write one tick diagnostic to stderr; P-01 appends no record entry."""
    print(message, file=sys.stderr)


def tick(
    *,
    repos: Sequence[str],
    github: GithubAdapter,
    policy: PolicyClient,
    authority: AuthorityClient,
    supply: SupplyClient,
    harness: HarnessClient,
    judgement: JudgementClient,
    remediation: RemediationClient,
    escalation: EscalationClient,
    reuse: ReuseClient,
    jobs: JobStore,
    pr_facts: PrFactsStore,
    leases: LeaseStore,
    record: RecordWriter,
    connection: Connection,
    state_dir: Path,
    runner: ProcessRunner,
    batch_size: int = DEFAULT_BATCH_SIZE,
    clock: Callable[[], datetime] = utcnow,
    log: Callable[[str], None] = tick_log,
) -> TickResult:
    """Sweep every configured repository and dispatch one bounded, fair batch."""
    try:
        lock_handle = acquire(state_dir)
    except (BlockingIOError, OSError) as exc:
        if exc.errno not in {errno.EACCES, errno.EAGAIN}:
            raise
        return TickResult(
            outcome="sweep_already_running",
            repos_admitted=(),
            repos_refused=(),
            jobs_created=(),
            jobs_dispatched=(),
            jobs_failed=(),
            revisited_resting_jobs=(),
        )

    repos_admitted: list[str] = []
    repos_refused = []
    jobs_created: list[str] = []
    jobs_dispatched: list[str] = []
    jobs_failed: list[JobFailure] = []

    try:
        for repo in repos:
            try:
                refusal = _check_admission(repo, store=policy, record=record)
                if refusal is not None:
                    repos_refused.append(refusal)
                    log(f"repo admission refused: {repo}: {refusal.reason}")
                    continue

                repos_admitted.append(repo)
                result = github.inventory(repo=repo)
                if isinstance(result, GithubUnavailable):
                    log(f"repo inventory unavailable: {repo}: {result!r}")
                    continue

                jobs_created.extend(
                    _ingest_inventory(
                        repo=repo,
                        inventory=result,
                        jobs=jobs,
                        pr_facts=pr_facts,
                        connection=connection,
                        clock=clock,
                    )
                )
            except (IntakeError, AppendFailed):
                raise
            except Exception as exc:
                connection.rollback()
                log(f"repo sweep failed: {repo}: {exc!r}")

        batch, revisited_resting_jobs = _select_batch(jobs=jobs, limit=batch_size)
        for job in batch:
            try:
                lease = Lease(leases=leases, github=github, clock=clock)
                deps = LifecycleDeps(
                    policy=policy,
                    authority=authority,
                    supply=supply,
                    harness=harness,
                    judgement=judgement,
                    remediation=remediation,
                    escalation=escalation,
                    github=github,
                    reuse=reuse,
                    record=record,
                    connection=connection,
                    state_dir=state_dir,
                    runner=runner,
                    claim_lease=lease.claim_lease,
                    release_lease=lease.release_lease,
                )
                admit(job=job, deps=deps)
                connection.commit()
                jobs_dispatched.append(job.id)
            except (IntakeError, AppendFailed):
                raise
            except Exception as exc:
                connection.commit()
                error = repr(exc)
                log(f"job dispatch failed: {job.id}: {error}")
                jobs_failed.append(JobFailure(job_id=job.id, error=error))

        return TickResult(
            outcome="swept",
            repos_admitted=tuple(repos_admitted),
            repos_refused=tuple(repos_refused),
            jobs_created=tuple(jobs_created),
            jobs_dispatched=tuple(jobs_dispatched),
            jobs_failed=tuple(jobs_failed),
            revisited_resting_jobs=revisited_resting_jobs,
        )
    finally:
        lock_handle.close()
