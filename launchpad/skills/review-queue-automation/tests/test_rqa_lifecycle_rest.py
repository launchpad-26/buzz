#!/usr/bin/env python3
"""The resting-status recovery check — `rqa/lifecycle/rest.py`, `code/P-02-lifecycle.md`
§3.2's "existing successor/lease recovery check" and §8 T19.

No pytest: every `test_*` function takes no arguments, per `tests/run_all.py`.

Every test drives the real `transition()` kernel and P-12's real writer through
`admit()`, so the check runs where production runs it: on entering a resting status.
"""

from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from lifecycle_cascade_bench import (  # noqa: E402
    SNAP_HASH,
    FakeAuthority,
    FakeLease,
    FakePolicy,
    bench,
    insert_job,
    insert_lease,
    lease_present,
    make_deny,
    make_deps,
    make_job,
    make_snapshot,
    stored_status,
    transitions,
)

from rqa.contracts import Activity, DenyReason, GithubUnavailable, JobStatus  # noqa: E402
from rqa.lifecycle import admit  # noqa: E402


def _arrival_entry(record, job) -> None:
    record.append(job.id, "transition", {
        "from_state": None, "to_state": "queued", "reason": "arrival", "repo": job.repo,
        "number": job.number, "head_sha": job.head_sha, "base_sha": job.base_sha,
        "predecessor_job": job.predecessor_job,
    })


def _resting_bench(*, status=JobStatus.STOPPED, snapshot_hash=SNAP_HASH):
    """A job already resting at `status`, with its arrival entry recorded, re-offered
    to `admit` — flow step 13's crash-recovery shape."""
    connection, record, job = bench(status=status, snapshot_hash=snapshot_hash)
    _arrival_entry(record, job)
    connection.commit()
    return connection, record, job


# -- supersession ------------------------------------------------------------------


def test_a_resting_job_with_a_successor_is_superseded() -> None:
    connection, record, job = _resting_bench()
    insert_job(connection, make_job(job_id="job-2", predecessor_job="job-1", head_sha="e" * 40))
    deps = make_deps(connection, record, policy=FakePolicy(make_snapshot()), authority=FakeAuthority())
    assert admit(job=job, deps=deps) is JobStatus.SUPERSEDED
    assert stored_status(connection) == "superseded"
    assert transitions(connection)[-1] == "superseded"


def test_a_resting_job_without_a_successor_keeps_its_status() -> None:
    connection, record, job = _resting_bench()
    deps = make_deps(connection, record, policy=FakePolicy(make_snapshot()), authority=FakeAuthority())
    assert admit(job=job, deps=deps) is JobStatus.STOPPED
    assert transitions(connection) == ["queued"]  # nothing new was minted


def test_a_terminal_state_never_mints_an_unlicensed_superseded_edge() -> None:
    """`merged` is terminal in §2's closed table; a successor cannot move it."""
    connection, record, job = _resting_bench(status=JobStatus.MERGED)
    insert_job(connection, make_job(job_id="job-2", predecessor_job="job-1", head_sha="e" * 40))
    deps = make_deps(connection, record, policy=FakePolicy(make_snapshot()), authority=FakeAuthority())
    assert admit(job=job, deps=deps) is JobStatus.MERGED
    assert stored_status(connection) == "merged"


# -- T19: the orphaned lease -------------------------------------------------------


def test_t19_an_orphaned_lease_is_released_only_under_a_fresh_review_grant() -> None:
    connection, record, job = _resting_bench()
    insert_lease(connection, job)
    lease = FakeLease()
    authority = FakeAuthority()  # grants REVIEW
    deps = make_deps(
        connection, record,
        policy=FakePolicy(make_snapshot()),
        authority=authority,
        claim_lease=lease.claim,
        release_lease=lease.release,
    )
    assert admit(job=job, deps=deps) is JobStatus.STOPPED
    assert len(lease.release_calls) == 1
    assert lease.release_calls[0].activity is Activity.REVIEW
    granted = [call for call in authority.calls if call[0] is Activity.REVIEW]
    assert granted, "the release must have asked for a fresh review grant"


def test_t19_a_deny_leaves_the_lease_visible() -> None:
    connection, record, job = _resting_bench()
    insert_lease(connection, job)
    lease = FakeLease()
    deps = make_deps(
        connection, record,
        policy=FakePolicy(make_snapshot()),
        authority=FakeAuthority({Activity.REVIEW: [make_deny(Activity.REVIEW, reason=DenyReason.CAPABILITY_MISSING)]}),
        claim_lease=lease.claim,
        release_lease=lease.release,
    )
    assert admit(job=job, deps=deps) is JobStatus.STOPPED
    assert lease.release_calls == []
    assert lease_present(connection)


def test_the_release_grant_is_asked_against_the_pinned_snapshot() -> None:
    """§3.2: "That recovery uses the pinned snapshot, never a replacement snapshot" —
    the E-03 pinned read supplies it for a directly-resting job."""
    connection, record, job = _resting_bench()
    insert_lease(connection, job)
    lease = FakeLease()
    authority = FakeAuthority()
    policy = FakePolicy(make_snapshot())
    deps = make_deps(
        connection, record, policy=policy, authority=authority,
        claim_lease=lease.claim, release_lease=lease.release,
    )
    admit(job=job, deps=deps)
    review_calls = [call for call in authority.calls if call[0] is Activity.REVIEW]
    assert review_calls[0][1] is policy.result  # the pinned snapshot, not None
    assert policy.calls, "the pinned snapshot came from E-03's pinned read"


def test_an_unpinned_resting_job_offers_no_snapshot_and_keeps_its_lease() -> None:
    """No pin → `snapshot=None` → P-08 denies NO_SNAPSHOT → the lease stays. Authority
    is never widened to tidy up."""
    connection, record, job = _resting_bench(status=JobStatus.STOPPED, snapshot_hash=None)
    insert_lease(connection, job)
    lease = FakeLease()
    authority = FakeAuthority({Activity.REVIEW: [make_deny(Activity.REVIEW, reason=DenyReason.NO_SNAPSHOT)]})
    deps = make_deps(
        connection, record, policy=FakePolicy(make_snapshot()), authority=authority,
        claim_lease=lease.claim, release_lease=lease.release,
    )
    admit(job=job, deps=deps)
    review_calls = [call for call in authority.calls if call[0] is Activity.REVIEW]
    assert review_calls[0][1] is None
    assert lease_present(connection)


def test_an_unavailable_release_keeps_resting_with_the_lease_in_place() -> None:
    connection, record, job = _resting_bench()
    insert_lease(connection, job)

    class UnavailableRelease(FakeLease):
        def release(self, *, job, grant, record):
            super().release(job=job, grant=grant, record=record)
            return GithubUnavailable(op="release_lease", reason="incomplete", retriable=True)

    lease = UnavailableRelease()
    deps = make_deps(
        connection, record,
        policy=FakePolicy(make_snapshot()),
        authority=FakeAuthority(),
        claim_lease=lease.claim,
        release_lease=lease.release,
    )
    assert admit(job=job, deps=deps) is JobStatus.STOPPED
    assert lease_present(connection)  # this part never deletes the row; P-01 owns it


def test_a_database_with_no_leases_table_is_a_database_with_no_lease() -> None:
    """`leases` is P-01's DDL; its absence can only mean no lease was ever claimed.
    The catalog check answers it — no error is swallowed to get there."""
    import sqlite3

    from lifecycle_cascade_bench import NoKeyStore
    from rqa.record.writer import SQLiteRecordWriter

    connection = sqlite3.connect(":memory:")
    connection.executescript(
        "CREATE TABLE jobs (id TEXT PRIMARY KEY, repo TEXT, number INTEGER, head_sha TEXT,"
        " base_sha TEXT, head_repo TEXT, head_ref TEXT, predecessor_job TEXT,"
        " predecessor_head_sha TEXT, snapshot_hash TEXT, status TEXT NOT NULL,"
        " created_at TEXT)"
    )
    job = make_job(status=JobStatus.STOPPED, snapshot_hash=SNAP_HASH)
    connection.execute(
        "INSERT INTO jobs VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (job.id, job.repo, job.number, job.head_sha, job.base_sha, job.head_repo,
         job.head_ref, None, None, job.snapshot_hash, "stopped", "t"),
    )
    connection.commit()
    record = SQLiteRecordWriter(connection, keystore=NoKeyStore())
    _arrival_entry(record, job)
    connection.commit()
    deps = make_deps(connection, record, policy=FakePolicy(make_snapshot()), authority=FakeAuthority())
    assert admit(job=job, deps=deps) is JobStatus.STOPPED


def test_a_superseded_job_still_releases_its_orphaned_lease() -> None:
    """Supersession first, then the lease check — a dead job's claim is exactly the
    orphan the recovery exists for."""
    connection, record, job = _resting_bench()
    insert_job(connection, make_job(job_id="job-2", predecessor_job="job-1", head_sha="e" * 40))
    insert_lease(connection, job)
    lease = FakeLease()
    deps = make_deps(
        connection, record,
        policy=FakePolicy(make_snapshot()),
        authority=FakeAuthority(),
        claim_lease=lease.claim,
        release_lease=lease.release,
    )
    assert admit(job=job, deps=deps) is JobStatus.SUPERSEDED
    assert len(lease.release_calls) == 1
