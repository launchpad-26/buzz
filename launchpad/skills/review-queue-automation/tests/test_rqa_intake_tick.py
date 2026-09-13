#!/usr/bin/env python3
"""P-01 tick orchestration tests: isolation, lock, E-02 wiring, and propagation."""

from __future__ import annotations

import contextlib
import importlib
import inspect
import pathlib
import sqlite3
import sys
import tempfile
from dataclasses import fields
from datetime import datetime, timezone

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

import rqa.intake as intake  # noqa: E402
from rqa.contracts import (  # noqa: E402
    Activity,
    AppendFailed,
    Blocking,
    Budget,
    External,
    GithubUnavailable,
    Grant,
    Job,
    JobStatus,
    LeaseTaken,
    Mechanical,
    Policy,
    PrFacts,
    RemediationPolicy,
    Snapshot,
)
from rqa.intake.lock import acquire  # noqa: E402
from rqa.intake.store import SqliteJobStore, ensure_schema  # noqa: E402
from rqa.intake.types import AdmissionRefusal, IntakeError, JobFailure  # noqa: E402
from rqa.protocol import protocol_hash  # noqa: E402
from rqa.record.writer import SQLiteRecordWriter  # noqa: E402

tick_module = importlib.import_module("rqa.intake.tick")
NOW = datetime(2026, 9, 13, 14, 0, tzinfo=timezone.utc)


class ConnectionSpy:
    def __init__(self) -> None:
        self.commits = 0
        self.rollbacks = 0

    def commit(self):
        self.commits += 1

    def rollback(self):
        self.rollbacks += 1


class FakeJobStore:
    def __init__(self, *, batch=(), followup=()) -> None:
        self.created = []
        self.current = {}
        self.batch = list(batch)
        self.followup = list(followup)
        self.select_calls = []
        self.followup_calls = 0

    def create(self, job):
        self.created.append(job)
        self.current[(job.repo, job.number)] = job

    def current_for_pr(self, repo, number):
        return self.current.get((repo, number))

    def select_batch(self, limit):
        self.select_calls.append(limit)
        return list(self.batch[:limit])

    def pending_followup(self):
        self.followup_calls += 1
        return list(self.followup)


class FakePrFactsStore:
    def __init__(self) -> None:
        self.rows = []

    def upsert(self, row):
        self.rows.append(row)


class FakeLeaseStore:
    def __init__(self) -> None:
        self.put_rows = []
        self.deleted = []

    def put(self, row):
        self.put_rows.append(row)

    def delete(self, repo, number):
        self.deleted.append((repo, number))


class FakeGithub:
    def __init__(self, inventories=None) -> None:
        self.inventories = inventories or {}
        self.inventory_calls = []
        self.claim_calls = []
        self.release_calls = []

    def inventory(self, *, repo):
        self.inventory_calls.append(repo)
        result = self.inventories[repo]
        if isinstance(result, BaseException):
            raise result
        return result

    def claim_lease(self, *, job, grant, record):
        self.claim_calls.append((job, grant, record))
        raise AssertionError("the test did not authorise a lease claim")

    def release_lease(self, *, job, grant, record):
        self.release_calls.append((job, grant, record))
        raise AssertionError("P-01 must not issue an unauthorised release")


class NoKeyStore:
    def read(self, name):
        return None


class NeverTouch:
    def __getattribute__(self, name):
        raise AssertionError(f"lock-contention path touched dependency attribute {name}")


@contextlib.contextmanager
def patched(name, value):
    original = getattr(tick_module, name)
    setattr(tick_module, name, value)
    try:
        yield
    finally:
        setattr(tick_module, name, original)


def make_facts(repo: str, *, number: int = 1, head: str = "a") -> PrFacts:
    return PrFacts(
        repo=repo,
        number=number,
        head_sha=head * 40,
        base_sha="b" * 40,
        merge_base_sha="b" * 40,
        head_repo=f"{repo}-head",
        head_ref=f"feature-{number}",
        head_protected=False,
        author="author-data",
        labels=frozenset({"label-data"}),
        title="title-data",
        body="body-data",
    )


def make_job(job_id: str, number: int) -> Job:
    return Job(
        id=job_id,
        repo="org/repo",
        number=number,
        head_sha=str(number) * 40,
        base_sha="b" * 40,
        head_repo="org/repo",
        head_ref=f"feature-{number}",
        predecessor_job=None,
        predecessor_head_sha=None,
        snapshot_hash=None,
        status=JobStatus.QUEUED,
    )


def call_tick(
    *,
    repos=(),
    github=None,
    jobs=None,
    pr_facts=None,
    leases=None,
    connection=None,
    state_dir,
    log=None,
):
    return tick_module.tick(
        repos=repos,
        github=github if github is not None else FakeGithub(),
        policy=object(),
        authority=object(),
        supply=object(),
        harness=object(),
        judgement=object(),
        remediation=object(),
        escalation=object(),
        reuse=object(),
        jobs=jobs if jobs is not None else FakeJobStore(),
        pr_facts=pr_facts if pr_facts is not None else FakePrFactsStore(),
        leases=leases if leases is not None else FakeLeaseStore(),
        record=object(),
        connection=connection if connection is not None else ConnectionSpy(),
        state_dir=state_dir,
        runner=object(),
        batch_size=20,
        clock=lambda: NOW,
        log=log if log is not None else (lambda message: None),
    )


def test_completed_package_exports_exact_fourteen_name_surface() -> None:
    assert intake.__all__ == [
        "tick",
        "TickResult",
        "AdmissionRefusal",
        "JobFailure",
        "job_id",
        "stable_hash",
        "GithubAdapter",
        "Lease",
        "JobStore",
        "PrFactsStore",
        "LeaseStore",
        "PrFactsRow",
        "LeaseRow",
        "IntakeError",
    ]


def test_tick_has_the_exact_twenty_keyword_only_parameters_and_defaults() -> None:
    parameters = list(inspect.signature(tick_module.tick).parameters.values())
    assert [parameter.name for parameter in parameters] == [
        "repos", "github", "policy", "authority", "supply", "harness",
        "judgement", "remediation", "escalation", "reuse", "jobs", "pr_facts",
        "leases", "record", "connection", "state_dir", "runner", "batch_size",
        "clock", "log",
    ]
    assert all(parameter.kind is inspect.Parameter.KEYWORD_ONLY for parameter in parameters)
    assert parameters[-3].default == 20
    assert parameters[-2].default is tick_module.utcnow
    assert parameters[-1].default is tick_module.tick_log


def test_t1_refusal_skips_inventory_and_every_downstream_repo_action() -> None:
    refusal = AdmissionRefusal("org/refused", "invalid policy", "rqa onboard org/refused")
    github = FakeGithub()
    jobs = FakeJobStore()
    seen = []

    def refuse(repo, *, store, record):
        seen.append((repo, store, record))
        return refusal

    with tempfile.TemporaryDirectory() as directory, patched("_check_admission", refuse):
        result = call_tick(
            repos=("org/refused",),
            github=github,
            jobs=jobs,
            state_dir=pathlib.Path(directory),
        )

    assert len(seen) == 1 and seen[0][0] == "org/refused"
    assert result.repos_refused == (refusal,)
    assert result.repos_admitted == ()
    assert result.jobs_created == ()
    assert github.inventory_calls == []
    assert jobs.created == []


def test_t2_refused_first_repository_does_not_block_the_second() -> None:
    first = "one/refused"
    second = "two/admitted"
    refusal = AdmissionRefusal(first, "invalid policy", f"rqa onboard {first}")
    github = FakeGithub({second: (make_facts(second),)})
    jobs = FakeJobStore()

    def admission(repo, *, store, record):
        return refusal if repo == first else None

    with tempfile.TemporaryDirectory() as directory, patched("_check_admission", admission):
        result = call_tick(
            repos=(first, second),
            github=github,
            jobs=jobs,
            state_dir=pathlib.Path(directory),
        )

    assert result.repos_refused == (refusal,)
    assert result.repos_admitted == (second,)
    assert github.inventory_calls == [second]
    assert len(jobs.created) == 1
    assert result.jobs_created == (jobs.created[0].id,)


def test_t3_real_lock_contention_returns_before_any_dependency_or_table_access() -> None:
    with tempfile.TemporaryDirectory() as directory:
        state_dir = pathlib.Path(directory)
        holder = acquire(state_dir)
        try:
            result = tick_module.tick(
                repos=("org/repo",),
                github=NeverTouch(),
                policy=NeverTouch(),
                authority=NeverTouch(),
                supply=NeverTouch(),
                harness=NeverTouch(),
                judgement=NeverTouch(),
                remediation=NeverTouch(),
                escalation=NeverTouch(),
                reuse=NeverTouch(),
                jobs=NeverTouch(),
                pr_facts=NeverTouch(),
                leases=NeverTouch(),
                record=NeverTouch(),
                connection=NeverTouch(),
                state_dir=state_dir,
                runner=NeverTouch(),
            )
        finally:
            holder.close()

    assert result.outcome == "sweep_already_running"
    assert result.repos_admitted == ()
    assert result.jobs_created == ()
    assert result.jobs_dispatched == ()


def test_t4_unavailable_first_inventory_does_not_block_the_second() -> None:
    first = "one/unavailable"
    second = "two/available"
    unavailable = GithubUnavailable(op="inventory", reason="unreachable", retriable=True)
    github = FakeGithub({first: unavailable, second: (make_facts(second),)})
    jobs = FakeJobStore()

    with tempfile.TemporaryDirectory() as directory, patched(
        "_check_admission", lambda repo, *, store, record: None
    ):
        result = call_tick(
            repos=(first, second),
            github=github,
            jobs=jobs,
            state_dir=pathlib.Path(directory),
        )

    assert result.repos_admitted == (first, second)
    assert github.inventory_calls == [first, second]
    assert len(jobs.created) == 1
    assert result.jobs_created == (jobs.created[0].id,)


def test_raised_repository_failure_rolls_back_and_still_sweeps_the_next_repo() -> None:
    first = "one/broken"
    second = "two/healthy"
    github = FakeGithub({first: RuntimeError("inventory failed"), second: (make_facts(second),)})
    jobs = FakeJobStore()
    connection = ConnectionSpy()
    logs = []

    with tempfile.TemporaryDirectory() as directory, patched(
        "_check_admission", lambda repo, *, store, record: None
    ):
        result = call_tick(
            repos=(first, second),
            github=github,
            jobs=jobs,
            connection=connection,
            state_dir=pathlib.Path(directory),
            log=logs.append,
        )

    assert github.inventory_calls == [first, second]
    assert result.jobs_created == (jobs.created[0].id,)
    assert connection.rollbacks == 1
    assert logs == ["repo sweep failed: one/broken: RuntimeError('inventory failed')"]


def test_repository_wrapper_propagates_appendfailed_without_sweeping_the_next_repo() -> None:
    github = FakeGithub()

    def append_failed(repo, *, store, record):
        raise AppendFailed("record unavailable")

    with tempfile.TemporaryDirectory() as directory, patched("_check_admission", append_failed):
        try:
            call_tick(
                repos=("one/repo", "two/repo"),
                github=github,
                state_dir=pathlib.Path(directory),
            )
        except AppendFailed:
            pass
        else:  # pragma: no cover - failure report
            raise AssertionError("repository isolation swallowed AppendFailed")

    assert github.inventory_calls == []


def test_repository_wrapper_propagates_intakeerror_without_sweeping_the_next_repo() -> None:
    github = FakeGithub()

    def intake_error(repo, *, store, record):
        raise IntakeError("invalid intake wiring")

    with tempfile.TemporaryDirectory() as directory, patched("_check_admission", intake_error):
        try:
            call_tick(
                repos=("one/repo", "two/repo"),
                github=github,
                state_dir=pathlib.Path(directory),
            )
        except IntakeError:
            pass
        else:  # pragma: no cover - failure report
            raise AssertionError("repository isolation swallowed IntakeError")

    assert github.inventory_calls == []


def test_t16_tick_constructs_all_fifteen_lifecycle_dependencies_once() -> None:
    job = make_job("job-1", 1)
    jobs = FakeJobStore(batch=(job,))
    github = FakeGithub()
    leases = FakeLeaseStore()
    connection = ConnectionSpy()
    calls = []

    def fake_admit(*, job, deps):
        calls.append((job, deps))
        return JobStatus.QUEUED

    with tempfile.TemporaryDirectory() as directory, patched("admit", fake_admit):
        state_dir = pathlib.Path(directory)
        result = call_tick(
            github=github,
            jobs=jobs,
            leases=leases,
            connection=connection,
            state_dir=state_dir,
        )

    assert len(calls) == 1 and calls[0][0] is job
    deps = calls[0][1]
    assert [field.name for field in fields(deps)] == [
        "policy", "authority", "supply", "harness", "judgement", "remediation",
        "escalation", "github", "reuse", "record", "connection", "state_dir",
        "runner", "claim_lease", "release_lease",
    ]
    assert deps.github is github
    assert deps.connection is connection
    assert deps.state_dir == state_dir
    assert deps.claim_lease.__self__.leases is leases
    assert deps.release_lease.__self__ is deps.claim_lease.__self__
    assert result.jobs_dispatched == (job.id,)
    assert connection.commits == 1


def test_t17_first_admit_failure_is_contained_and_second_dispatches_once() -> None:
    first = make_job("job-1", 1)
    second = make_job("job-2", 2)
    jobs = FakeJobStore(batch=(first, second))
    github = FakeGithub()
    connection = ConnectionSpy()
    calls = []
    logs = []

    def fake_admit(*, job, deps):
        calls.append(job.id)
        if job is first:
            try:
                raise RuntimeError("context-only-marker")
            except RuntimeError:
                raise ValueError("safe dispatch failure")
        return JobStatus.QUEUED

    with tempfile.TemporaryDirectory() as directory, patched("admit", fake_admit):
        result = call_tick(
            github=github,
            jobs=jobs,
            connection=connection,
            state_dir=pathlib.Path(directory),
            log=logs.append,
        )

    assert calls == [first.id, second.id]
    assert result.jobs_failed == (JobFailure(first.id, "ValueError('safe dispatch failure')"),)
    assert result.jobs_dispatched == (second.id,)
    assert connection.commits == 2
    assert github.claim_calls == []
    assert github.release_calls == []
    assert "context-only-marker" not in repr(result)
    assert all("context-only-marker" not in message for message in logs)


def test_job_wrapper_propagates_appendfailed_and_does_not_dispatch_later_jobs() -> None:
    first = make_job("job-1", 1)
    second = make_job("job-2", 2)
    jobs = FakeJobStore(batch=(first, second))
    calls = []

    def fake_admit(*, job, deps):
        calls.append(job.id)
        raise AppendFailed("record unavailable")

    with tempfile.TemporaryDirectory() as directory, patched("admit", fake_admit):
        try:
            call_tick(jobs=jobs, state_dir=pathlib.Path(directory))
        except AppendFailed:
            pass
        else:  # pragma: no cover - failure report
            raise AssertionError("per-job isolation swallowed AppendFailed")

    assert calls == [first.id]


def test_job_wrapper_propagates_intakeerror_and_does_not_dispatch_later_jobs() -> None:
    first = make_job("job-1", 1)
    second = make_job("job-2", 2)
    jobs = FakeJobStore(batch=(first, second))
    calls = []

    def fake_admit(*, job, deps):
        calls.append(job.id)
        raise IntakeError("invalid intake wiring")

    with tempfile.TemporaryDirectory() as directory, patched("admit", fake_admit):
        try:
            call_tick(jobs=jobs, state_dir=pathlib.Path(directory))
        except IntakeError:
            pass
        else:  # pragma: no cover - failure report
            raise AssertionError("per-job isolation swallowed IntakeError")

    assert calls == [first.id]


def make_snapshot(*, repo: str) -> Snapshot:
    return Snapshot(
        hash="snap-1",
        repo=repo,
        protocol_hash=protocol_hash(),
        authority={activity: activity is Activity.REVIEW for activity in Activity},
        routes=(),
        external=External(allowed=False, deny_label="no-external"),
        policy=Policy(
            version="policy-1",
            obligations=(),
            blocking=Blocking(categories=frozenset(), severities=frozenset(), corroboration=1),
            mechanical=Mechanical(categories=frozenset(), tools=frozenset()),
            assurance={"standard": 1},
            remediation=RemediationPolicy(allow_forks=False),
        ),
        budget=Budget(per_pr_tokens=None, per_repo_daily_tokens=None, per_model_daily_tokens=None),
    )


class FakePolicyClient:
    """`store` rides the client the way `deps.supply` carries its stores — the
    convention `rqa/lifecycle/steps.py` uses (`deps.policy.snapshot_for(..., store=
    deps.policy.store, ...)`); this Protocol's own declared shape names only the
    method, but the real cascade also reads this attribute directly off whatever
    object `tick()` was handed as `policy=`."""

    def __init__(self, snapshot: Snapshot) -> None:
        self.snapshot = snapshot
        self.store = object()
        self.calls = []

    def snapshot_for(self, *, repo, job, store, record):
        self.calls.append((repo, job, store, record))
        return self.snapshot


class FakeAuthorityClient:
    """`github`/`store` ride the client the same way (`deps.authority.github`,
    `deps.authority.store` in `rqa/lifecycle/steps.py`)."""

    def __init__(self, grant: Grant) -> None:
        self.grant_value = grant
        self.github = object()
        self.store = object()
        self.calls = []

    def grant(self, *, repo, activity, snapshot, job_id, categories, record, github, store):
        self.calls.append((repo, activity, snapshot, job_id, categories, record, github, store))
        return self.grant_value


class LeaseTakenGithub:
    """A minimal E-01 stand-in: `claim_lease` reports an already-claimed PR, and
    `release_lease`/`inventory` are never expected to be reached from this test."""

    def __init__(self) -> None:
        self.claim_calls = []

    def claim_lease(self, *, job, grant, record):
        self.claim_calls.append((job, grant, record))
        return LeaseTaken(login="already-claimed")

    def release_lease(self, *, job, grant, record):
        raise AssertionError("a job resting at QUEUED via LeaseTaken never releases")

    def inventory(self, *, repo):
        raise AssertionError("this test sweeps no repositories")


def test_real_lifecycle_admit_reaches_a_resting_status_through_tick() -> None:
    """Real E-02 integration: tick -> LifecycleDeps -> the real `rqa.lifecycle.admit` ->
    transition/record, with policy/authority collaborators real enough for the P-02 §3.2
    step-3 cascade to reach a resting status wherever that cascade is present.

    This assertion is wave-invariant by construction, not by luck. `#2200`'s cascade
    **is present on this branch and is genuinely exercised here**: `admit`'s real step 3
    calls `deps.policy.snapshot_for(...)` and `deps.authority.grant(...)` against the
    fakes below, drives the E-01 `claim_lease` callback, and — per §3.2 step 1's own
    documented branch, "`claim_lease` returning `LeaseTaken` returns the unchanged
    `QUEUED` job" — rests there. It was designed to also hold true were `rqa/lifecycle`
    only arrival-only (as this branch's base briefly was, mid-review — see
    `## Disclosures`): the arrival-only path and the completed cascade's `LeaseTaken`
    rest converge on the identical `QUEUED`/dispatched outcome, so this test does not
    merely happen to pass against whichever `rqa.lifecycle` state is checked out; it was
    never going to assert only what was "true this afternoon" (see `## Disclosures`).
    """
    connection = sqlite3.connect(":memory:")
    ensure_schema(connection)
    jobs = SqliteJobStore(connection, clock=lambda: NOW)
    job = make_job("job-1", 1)
    jobs.create(job)
    connection.commit()
    record = SQLiteRecordWriter(connection, clock=lambda: NOW, keystore=NoKeyStore())
    snapshot = make_snapshot(repo=job.repo)
    policy = FakePolicyClient(snapshot)
    authority = FakeAuthorityClient(
        Grant(
            activity=Activity.REVIEW,
            repo=job.repo,
            job_id=job.id,
            snapshot_hash=snapshot.hash,
            capability_proof_id=1,
            categories=None,
            entry_seq=1,
        )
    )
    github = LeaseTakenGithub()
    leases = FakeLeaseStore()

    with tempfile.TemporaryDirectory() as directory:
        result = tick_module.tick(
            repos=(),
            github=github,
            policy=policy,
            authority=authority,
            supply=object(),
            harness=object(),
            judgement=object(),
            remediation=object(),
            escalation=object(),
            reuse=object(),
            jobs=jobs,
            pr_facts=FakePrFactsStore(),
            leases=leases,
            record=record,
            connection=connection,
            state_dir=pathlib.Path(directory),
            runner=object(),
            clock=lambda: NOW,
            log=lambda message: None,
        )

    assert result.jobs_dispatched == (job.id,)
    assert result.jobs_failed == ()
    assert connection.execute(
        "SELECT COUNT(*) FROM record_entries WHERE job = ? AND kind = 'transition'",
        (job.id,),
    ).fetchone()[0] == 1
    assert connection.execute("SELECT status FROM jobs WHERE id = ?", (job.id,)).fetchone()[0] == "queued"
    # Neither an arrival-only `admit` nor the completed cascade's `LeaseTaken` rest
    # ever writes a local lease row — both hypothetical states agree on this, though
    # only the latter is what this branch's landed #2200 cascade actually exercises.
    assert leases.put_rows == []


def test_a_neighbour_collaborator_blowing_up_lands_only_its_own_job_in_jobs_failed() -> None:
    """P-01 §3 step 5's isolation guarantee, asserted deliberately rather than by
    accident: one job's collaborator failure never takes down the sweep, and it names
    that job in `jobs_failed` rather than either raising out of `tick()` or silently
    disappearing.

    `rqa.lifecycle.admit`'s real cascade **is present on this branch** (#2200 landed;
    see the success-path test above, which genuinely drives it) and calls
    `deps.policy.snapshot_for(...)` as its actual first step-3 call. This test
    substitutes a minimal stand-in for `admit` anyway, deliberately: the point here is
    `tick()`'s **own** per-job isolation wrapper, decoupled from whatever internal call
    order Lifecycle's cascade happens to take before it reaches that call — not a claim
    that the cascade is missing or unreachable. The substitute performs exactly P-02
    §3.2 step 3's first documented call —
    `deps.policy.snapshot_for(repo=job.repo, job=job, store=None, record=deps.record)`
    — against the genuinely bare `object()` `policy` collaborator `tick()` constructs
    `LifecycleDeps` with, for the first job only. That call raises a real, unforced
    `AttributeError` (`object` has no `snapshot_for`), driven through `tick()`'s own
    real per-job isolation wrapper — the exact shape that surfaced once this branch was
    rebased onto #2200's real cascade (`assert () == ('job-1',)` in the four-way
    composite run). Only the `admit` call itself is substituted;
    `LifecycleDeps` construction, the `Lease` wrapper, and the per-job `try/except`
    are all real `tick()` code. The second job's own substitute call succeeds
    trivially — it is the control proving `tick()`'s own wrapper still processes the
    next job after containing the first's failure; it is not a claim about how the
    real, landed cascade would treat a second job sharing the same bare
    collaborator.
    """
    first = make_job("job-1", 1)
    second = make_job("job-2", 2)
    jobs = FakeJobStore(batch=(first, second))
    connection = ConnectionSpy()

    def admit_driving_the_real_step_three_policy_call(*, job, deps):
        if job is first:
            deps.policy.snapshot_for(repo=job.repo, job=job, store=None, record=deps.record)
            return JobStatus.QUEUED  # pragma: no cover - unreachable: the call above raises
        return JobStatus.QUEUED

    with tempfile.TemporaryDirectory() as directory, patched(
        "admit", admit_driving_the_real_step_three_policy_call
    ):
        result = call_tick(
            jobs=jobs,
            connection=connection,
            state_dir=pathlib.Path(directory),
        )

    assert result.outcome == "swept"
    assert result.jobs_dispatched == (second.id,)
    assert len(result.jobs_failed) == 1
    failure = result.jobs_failed[0]
    assert failure.job_id == first.id
    assert failure.error == "AttributeError(\"'object' object has no attribute 'snapshot_for'\")"
    assert connection.commits == 2
