#!/usr/bin/env python3
"""P-01 E-01 lease callback tests over the real local leases table."""

from __future__ import annotations

import pathlib
import sqlite3
import sys
from datetime import datetime, timezone

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from rqa.contracts import (  # noqa: E402
    Activity,
    GithubUnavailable,
    Grant,
    Job,
    JobStatus,
    LeaseTaken,
    Mutation,
)
from rqa.intake.lease import Lease  # noqa: E402
from rqa.intake.store import SqliteLeaseStore, ensure_schema  # noqa: E402
from rqa.intake.types import LeaseRow  # noqa: E402

NOW = datetime(2026, 9, 13, 13, 0, tzinfo=timezone.utc)


class Record:
    pass


class FakeGithub:
    def __init__(self, *, claim_result=None, release_result=None, events=None) -> None:
        self.claim_result = claim_result
        self.release_result = release_result
        self.events = events if events is not None else []
        self.claim_calls = []
        self.release_calls = []

    def claim_lease(self, *, job, grant, record):
        self.events.append("claim")
        self.claim_calls.append((job, grant, record))
        return self.claim_result

    def release_lease(self, *, job, grant, record):
        self.events.append("release")
        self.release_calls.append((job, grant, record))
        return self.release_result


def make_job() -> Job:
    return Job(
        id="job-1",
        repo="org/repo",
        number=31,
        head_sha="a" * 40,
        base_sha="b" * 40,
        head_repo="alice/fork",
        head_ref="feature",
        predecessor_job=None,
        predecessor_head_sha=None,
        snapshot_hash="c" * 64,
        status=JobStatus.CLAIMED,
    )


def review_grant(job: Job) -> Grant:
    return Grant(
        activity=Activity.REVIEW,
        repo=job.repo,
        job_id=job.id,
        snapshot_hash=job.snapshot_hash or "",
        capability_proof_id=1,
        categories=None,
        entry_seq=2,
    )


def bench(github: FakeGithub):
    connection = sqlite3.connect(":memory:")
    ensure_schema(connection)
    store = SqliteLeaseStore(connection)
    return connection, store, Lease(leases=store, github=github, clock=lambda: NOW)


def test_t10_claim_reaches_github_only_after_a_review_grant_is_reported() -> None:
    events = []
    result = LeaseTaken(login="another-reviewer")
    github = FakeGithub(claim_result=result, events=events)
    _connection, _store, lease = bench(github)
    job = make_job()

    events.append("review-grant")
    returned = lease.claim_lease(job=job, grant=review_grant(job), record=Record())

    assert events == ["review-grant", "claim"]
    assert returned is result


def test_t11_mutation_claim_writes_the_real_local_lease_row() -> None:
    result = Mutation(id="mutation-1", kind="assignee_add", accepted=True)
    github = FakeGithub(claim_result=result)
    _connection, store, lease = bench(github)
    job = make_job()
    grant = review_grant(job)
    record = Record()

    returned = lease.claim_lease(job=job, grant=grant, record=record)

    assert returned is result
    assert github.claim_calls == [(job, grant, record)]
    assert store.current(job.repo, job.number) == LeaseRow(
        job_id=job.id,
        repo=job.repo,
        number=job.number,
        claimed_at=NOW,
    )


def test_t12_denied_or_unavailable_claim_writes_no_local_row() -> None:
    for result in (
        LeaseTaken(login="another-reviewer"),
        GithubUnavailable(op="claim_lease", reason="unreachable", retriable=True),
    ):
        github = FakeGithub(claim_result=result)
        _connection, store, lease = bench(github)
        job = make_job()

        returned = lease.claim_lease(
            job=job,
            grant=review_grant(job),
            record=Record(),
        )

        assert returned is result
        assert store.current(job.repo, job.number) is None


def test_t13_mutation_release_deletes_the_real_local_lease_row() -> None:
    result = Mutation(id="mutation-2", kind="assignee_remove", accepted=True)
    github = FakeGithub(release_result=result)
    _connection, store, lease = bench(github)
    job = make_job()
    store.put(LeaseRow(job.id, job.repo, job.number, NOW))
    grant = review_grant(job)
    record = Record()

    returned = lease.release_lease(job=job, grant=grant, record=record)

    assert returned is result
    assert github.release_calls == [(job, grant, record)]
    assert store.current(job.repo, job.number) is None


def test_t14_unavailable_release_retains_the_real_local_lease_row() -> None:
    result = GithubUnavailable(op="release_lease", reason="rate_limited", retriable=True)
    github = FakeGithub(release_result=result)
    _connection, store, lease = bench(github)
    job = make_job()
    row = LeaseRow(job.id, job.repo, job.number, NOW)
    store.put(row)

    returned = lease.release_lease(
        job=job,
        grant=review_grant(job),
        record=Record(),
    )

    assert returned is result
    assert store.current(job.repo, job.number) == row


def test_t15_all_lease_adapter_arguments_use_contract_keyword_names() -> None:
    claim = LeaseTaken(login="another-reviewer")
    release = GithubUnavailable(op="release_lease", reason="unreachable", retriable=True)
    github = FakeGithub(claim_result=claim, release_result=release)
    _connection, _store, lease = bench(github)
    job = make_job()
    grant = review_grant(job)
    record = Record()

    assert lease.claim_lease(job=job, grant=grant, record=record) is claim
    assert lease.release_lease(job=job, grant=grant, record=record) is release
    assert github.claim_calls == [(job, grant, record)]
    assert github.release_calls == [(job, grant, record)]
