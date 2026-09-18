#!/usr/bin/env python3
"""All-due anchor cadence: selection delegates to the existing job composition.

The fake publisher is the only GitHub-facing collaborator.  It makes one job's
destination unavailable without a network, then proves that the other job, retries,
and no-op runs remain independent.
"""

from __future__ import annotations

import contextlib
import importlib
import pathlib
import sqlite3
import sys
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from rqa.anchor_cadence import sweep_due_anchors  # noqa: E402
from rqa.cli.composition import anchor_job_for  # noqa: E402
from rqa.contracts import (  # noqa: E402
    Activity,
    Blocking,
    Budget,
    External,
    Grant,
    Job,
    JobStatus,
    Mechanical,
    Policy,
    RemediationPolicy,
    Snapshot,
)
from rqa.intake import SqliteJobStore, ensure_schema  # noqa: E402
from rqa.policy.store import StoredSnapshot  # noqa: E402
from rqa.record import PublishFailed, SQLiteRecordWriter, verify  # noqa: E402
from rqa.record.store import anchors_for_job, entries_for_job  # noqa: E402

composition_module = importlib.import_module("rqa.cli.composition")

_CLOCK = datetime(2026, 9, 18, tzinfo=timezone.utc)
_HASH = "a" * 64


def _snapshot() -> Snapshot:
    return Snapshot(
        hash=_HASH,
        repo="",
        protocol_hash="b" * 64,
        authority={activity: activity is Activity.COMMENT for activity in Activity},
        routes=(),
        external=External(allowed=False, deny_label=""),
        policy=Policy(
            version="test",
            obligations=(),
            blocking=Blocking(categories=frozenset(), severities=frozenset(), corroboration=1),
            mechanical=Mechanical(categories=frozenset(), tools=frozenset()),
            assurance={},
            remediation=RemediationPolicy(allow_forks=False),
        ),
        budget=Budget(per_pr_tokens=None, per_repo_daily_tokens=None, per_model_daily_tokens=None),
    )


class _Snapshots:
    def __init__(self, stored: StoredSnapshot | None):
        self.stored = stored

    def get(self, hash_: str) -> StoredSnapshot | None:
        assert hash_ == _HASH
        return self.stored


class _Gate:
    def __init__(self, repos: tuple[str, ...]):
        self.repos = frozenset(repos)


class _Authority:
    github = object()
    store = object()

    def __init__(self, *, record: SQLiteRecordWriter, repos: tuple[str, ...]):
        self.gate = _Gate(repos)
        self.record = record
        self.calls: list[str] = []

    def grant(self, **kwargs):
        self.calls.append(kwargs["job_id"])
        entry = self.record.append(
            kwargs["job_id"],
            "grant",
            {
                "activity": Activity.COMMENT.value,
                "snapshot_hash": kwargs["snapshot"].hash,
                "categories": None,
                "capability_proof_id": 1,
                "decision": "granted",
            },
        )
        return Grant(
            activity=Activity.COMMENT,
            repo=kwargs["repo"],
            job_id=kwargs["job_id"],
            snapshot_hash=kwargs["snapshot"].hash,
            capability_proof_id=1,
            categories=None,
            entry_seq=entry.seq,
        )


class _Publisher:
    unavailable: set[str] = set()
    calls: list[str] = []

    def __init__(self, *, adapter, job: Job, grant: Grant | None):
        self.job = job
        self.grant = grant

    def publish(self, *, anchor):
        type(self).calls.append(self.job.id)
        if self.job.id in type(self).unavailable:
            raise PublishFailed("test destination unavailable")
        assert self.grant is not None
        return f"fake:{self.job.repo}#{self.job.number}:{anchor.seq}"


class _Comp:
    def __init__(self, *, managed: tuple[str, ...], snapshot: StoredSnapshot | None):
        self.connection = sqlite3.connect(":memory:")
        ensure_schema(self.connection)
        self.clock = lambda: _CLOCK
        self.jobs = SqliteJobStore(self.connection, clock=self._next_created_at())
        self.record = SQLiteRecordWriter(self.connection, clock=self.clock)
        self.snapshot_store = _Snapshots(snapshot)
        self.authority = _Authority(record=self.record, repos=managed)
        self.github = object()

    @staticmethod
    def _next_created_at():
        moments = iter(_CLOCK + timedelta(seconds=index) for index in range(100))
        return lambda: next(moments)

    def add_job(self, *, job_id: str, repo: str, number: int) -> Job:
        job = Job(
            id=job_id,
            repo=repo,
            number=number,
            head_sha=f"head-{job_id}",
            base_sha="base",
            head_repo=repo,
            head_ref="feature",
            predecessor_job=None,
            predecessor_head_sha=None,
            snapshot_hash=_HASH,
            status=JobStatus.QUEUED,
        )
        self.jobs.create(job)
        self.record.append(job.id, "transition", {"to_state": "queued"})
        return job


@contextlib.contextmanager
def _publisher(*, unavailable: set[str] | None = None):
    _Publisher.calls = []
    _Publisher.unavailable = set() if unavailable is None else unavailable
    with patch.object(composition_module, "GithubAnchorPublisher", _Publisher):
        yield _Publisher


def _stored_snapshot() -> StoredSnapshot:
    return StoredSnapshot(snapshot=_snapshot(), activated_at=_CLOCK)


def _record_count(comp: _Comp, job_id: str) -> int:
    return len(entries_for_job(connection=comp.connection, job=job_id))


def _sweep(comp: _Comp):
    return sweep_due_anchors(
        jobs=comp.jobs,
        anchor=lambda job_id: anchor_job_for(comp, job_id),
    )


def test_all_due_sweep_is_independent_retries_pending_and_is_a_true_no_op_when_unchanged() -> None:
    comp = _Comp(
        managed=("acme/available", "acme/unavailable"),
        snapshot=_stored_snapshot(),
    )
    available = comp.add_job(job_id="available", repo="acme/available", number=1)
    unavailable = comp.add_job(job_id="unavailable", repo="acme/unavailable", number=2)

    with _publisher(unavailable={unavailable.id}) as publisher:
        first = _sweep(comp)
        outcomes = {item.job_id: item.outcome for item in first.outcomes}
        assert set(outcomes) == {available.id, unavailable.id}
        assert outcomes[available.id].published == 1
        assert outcomes[unavailable.id].pending == 1
        assert publisher.calls == [available.id, unavailable.id]

        # The unavailable destination did not prevent the other job from being
        # anchored.  Its local row detects a removed tail offline, but the external
        # claim remains unattested until the timer's next invocation and recovery.
        assert verify(comp.connection, unavailable.id).anchor_published is False
        counts_after_first = {
            job.id: _record_count(comp, job.id) for job in (available, unavailable)
        }

        publisher.unavailable = set()
        retry = _sweep(comp)
        assert [item.job_id for item in retry.outcomes] == [unavailable.id]
        assert retry.outcomes[0].outcome.published == 1
        assert {
            job.id: _record_count(comp, job.id) for job in (available, unavailable)
        } == counts_after_first, "retry must reuse its recorded grant without record growth"

        no_op = _sweep(comp)
        assert no_op.outcomes == ()
        assert {
            job.id: _record_count(comp, job.id) for job in (available, unavailable)
        } == counts_after_first

        # Appends never trigger anchoring.  They only make the next OS-timer sweep
        # select the newer head, which bounds the externally unattested window.
        comp.record.append(available.id, "transition", {"to_state": "later"})
        assert len(anchors_for_job(connection=comp.connection, job=available.id)) == 1
        newer_head = _sweep(comp)
        assert [item.job_id for item in newer_head.outcomes] == [available.id]
        assert len(anchors_for_job(connection=comp.connection, job=available.id)) == 2


def test_all_due_sweep_reports_unmanaged_and_missing_snapshot_jobs_without_record_growth() -> None:
    comp = _Comp(managed=("acme/managed",), snapshot=None)
    unmanaged = comp.add_job(job_id="unmanaged", repo="acme/unmanaged", number=1)
    missing_snapshot = comp.add_job(job_id="missing", repo="acme/managed", number=2)
    before = {job.id: _record_count(comp, job.id) for job in (unmanaged, missing_snapshot)}

    with _publisher() as publisher:
        sweep = _sweep(comp)

    outcomes = {item.job_id: item.outcome for item in sweep.outcomes}
    assert outcomes[unmanaged.id].detail == "not published: repo_not_managed"
    assert "snapshot is missing" in outcomes[missing_snapshot.id].detail
    assert publisher.calls == []
    assert {job.id: _record_count(comp, job.id) for job in (unmanaged, missing_snapshot)} == before
    assert anchors_for_job(connection=comp.connection, job=unmanaged.id) == ()
    assert anchors_for_job(connection=comp.connection, job=missing_snapshot.id) == ()
