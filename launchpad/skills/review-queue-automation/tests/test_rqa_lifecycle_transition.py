#!/usr/bin/env python3
"""`transition()`, `safe_stop()` and `admit()`'s containment boundary —
`code/P-02-lifecycle.md` §3.1, §5, §6 and §8 rows T1, T2, T3, T4 and T5's
containment half.

No pytest: every `test_*` function here takes no arguments, per `tests/run_all.py`.

Every test drives a **real** `sqlite3` connection and P-12's **real** `SQLiteRecordWriter`
over it. That is the point: §5's claim is that `UPDATE jobs` and `record.append` share one
connection's implicit transaction, so a failure in either leaves neither durable. A fake
writer cannot demonstrate that — it would prove only that this file's own fake behaves as
this file's own fake was written to. The two places a fake *is* used are the two failures
a real writer cannot be asked to produce on demand: an append that fails, and a read that
fails. Nothing here touches a network, a keychain or a credential: the injected key store
returns `None`, which is `P-12-record.md` §3.1's explicitly unkeyed append.
"""

from __future__ import annotations

import pathlib
import sqlite3
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from rqa.contracts import AppendFailed, Job, JobStatus  # noqa: E402
from rqa.lifecycle import (  # noqa: E402
    IllegalTransitionError,
    LifecycleError,
    UnknownJobError,
    admit,
    transition,
)
from rqa.lifecycle.deps import LifecycleDeps  # noqa: E402
from rqa.lifecycle.transition import safe_stop  # noqa: E402
from rqa.record.writer import SQLiteRecordWriter  # noqa: E402

#: `code/P-01-intake.md` §5's `jobs` DDL, shown there and in P-02 §5 for reference. P-02
#: owns no DDL; this is the table P-01 will create, reproduced so these tests can run
#: before `rqa/intake` exists.
JOBS_DDL = """
CREATE TABLE jobs (
  id              TEXT PRIMARY KEY,
  repo            TEXT NOT NULL,
  number          INTEGER NOT NULL,
  head_sha        TEXT NOT NULL,
  base_sha        TEXT NOT NULL,
  head_repo       TEXT NOT NULL,
  head_ref        TEXT NOT NULL,
  predecessor_job TEXT REFERENCES jobs(id),
  predecessor_head_sha TEXT,
  snapshot_hash   TEXT,
  status          TEXT NOT NULL,
  created_at      TEXT NOT NULL,
  UNIQUE (repo, number, head_sha)
);
"""

HEAD = "a" * 40
BASE = "b" * 40


class NoKeyStore:
    """ADR-0063's absent-key path: a successful, explicitly unkeyed append. No OS
    keychain is consulted and no key material exists in this process."""

    def read(self, name: str) -> bytes | None:
        return None


class FlakyWriter:
    """A `RecordWriter` that fails a chosen append and otherwise delegates to the real
    one — the one failure a real writer cannot be asked for on demand."""

    def __init__(self, inner, *, fail_on=(1,)):
        self.inner = inner
        self.fail_on = set(fail_on)
        self.calls = 0

    def append(self, job_id, kind, payload):
        self.calls += 1
        if self.calls in self.fail_on:
            raise AppendFailed(f"the record could not be appended (call {self.calls})")
        return self.inner.append(job_id, kind, payload)


class AlwaysFailingWriter:
    def __init__(self) -> None:
        self.calls = 0

    def append(self, job_id, kind, payload):
        self.calls += 1
        raise AppendFailed("the record could not be appended")


class ExplodingWriter:
    """A writer whose failure is *not* a persistence failure — §8 T5's shape: it must
    propagate, never be misclassified as a stop."""

    def append(self, job_id, kind, payload):
        raise LifecycleError("a neighbour's own named error")


class FailingReadConnection(sqlite3.Connection):
    """A connection whose `record_entries` read fails, the way a corrupt page or a
    revoked file handle fails it. Everything else works, so the containment path can be
    driven to a real, committed safe stop."""

    fail_pattern = "SELECT payload FROM record_entries"

    def execute(self, sql, parameters=()):  # type: ignore[override]
        if self.fail_pattern in sql:
            raise sqlite3.OperationalError("disk I/O error")
        return super().execute(sql, parameters)


def make_job(
    *,
    status: JobStatus = JobStatus.QUEUED,
    job_id: str = "job-1",
    snapshot_hash: str | None = None,
    number: int = 7,
) -> Job:
    return Job(
        id=job_id,
        repo="owner/name",
        number=number,
        head_sha=HEAD,
        base_sha=BASE,
        head_repo="owner/name",
        head_ref="feature",
        predecessor_job=None,
        predecessor_head_sha=None,
        snapshot_hash=snapshot_hash,
        status=status,
    )


def new_db(path: str = ":memory:", *, factory=sqlite3.Connection) -> sqlite3.Connection:
    connection = sqlite3.connect(path, factory=factory)
    connection.executescript(JOBS_DDL)
    return connection


def insert_job(connection: sqlite3.Connection, job: Job) -> None:
    connection.execute(
        "INSERT INTO jobs (id, repo, number, head_sha, base_sha, head_repo, head_ref, "
        "predecessor_job, predecessor_head_sha, snapshot_hash, status, created_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            job.id,
            job.repo,
            job.number,
            job.head_sha,
            job.base_sha,
            job.head_repo,
            job.head_ref,
            job.predecessor_job,
            job.predecessor_head_sha,
            job.snapshot_hash,
            job.status.value,
            "2026-09-13T00:00:00.000000+00:00",
        ),
    )
    connection.commit()


def bench(
    *, status: JobStatus = JobStatus.QUEUED, snapshot_hash: str | None = None, path: str = ":memory:",
    factory=sqlite3.Connection,
) -> tuple[sqlite3.Connection, SQLiteRecordWriter, Job]:
    connection = new_db(path, factory=factory)
    job = make_job(status=status, snapshot_hash=snapshot_hash)
    insert_job(connection, job)
    return connection, SQLiteRecordWriter(connection, keystore=NoKeyStore()), job


def stored_status(connection: sqlite3.Connection, job_id: str = "job-1") -> str:
    return connection.execute("SELECT status FROM jobs WHERE id = ?", (job_id,)).fetchone()[0]


def stored_pin(connection: sqlite3.Connection, job_id: str = "job-1") -> str | None:
    return connection.execute(
        "SELECT snapshot_hash FROM jobs WHERE id = ?", (job_id,)
    ).fetchone()[0]


def entries(connection: sqlite3.Connection, job_id: str = "job-1") -> list[tuple]:
    return [
        tuple(row)
        for row in connection.execute(
            "SELECT seq, kind, payload FROM record_entries WHERE job = ? ORDER BY seq",
            (job_id,),
        ).fetchall()
    ]


def lifecycle_deps(connection, record, **overrides) -> LifecycleDeps:
    """P-02's bundle with only the fields this half reaches. The nine neighbour clients
    are `None` on purpose: the kernel must not call one, and a `None` would raise
    loudly if it did."""
    values = {
        "policy": None,
        "authority": None,
        "supply": None,
        "harness": None,
        "judgement": None,
        "remediation": None,
        "escalation": None,
        "github": None,
        "reuse": None,
        "record": record,
        "connection": connection,
        "state_dir": pathlib.Path("/nonexistent"),
        "runner": None,
        "claim_lease": None,
        "release_lease": None,
    }
    values.update(overrides)
    return LifecycleDeps(**values)


# -- T1: the closed table --------------------------------------------------------


def test_a_transition_outside_the_table_changes_nothing() -> None:
    """§8 T1: "raises `IllegalTransitionError`; neither `jobs.status` nor `record_entries`
    changes". Checked before the transaction opens, so it is not a rolled-back write — it
    is no write."""
    for status, target in (
        (JobStatus.QUEUED, JobStatus.JUDGED),
        (JobStatus.MERGED, JobStatus.APPROVED),
        (JobStatus.CHANGES_REQUESTED, JobStatus.APPROVED),
        (JobStatus.SUPERSEDED, JobStatus.CLAIMED),
        (JobStatus.QUEUED, JobStatus.STOPPED),
        (JobStatus.JUDGED, JobStatus.APPROVED),
    ):
        connection, record, job = bench(status=status)
        try:
            transition(job, target, reason="r", connection=connection, record=record)
        except IllegalTransitionError:
            pass
        else:  # pragma: no cover - the raise below is the failure report
            raise AssertionError(f"{status.value} -> {target.value} was accepted")
        assert stored_status(connection) == status.value
        assert entries(connection) == []


def test_the_illegal_transition_message_names_the_legal_targets() -> None:
    connection, record, job = bench(status=JobStatus.QUEUED)
    try:
        transition(job, JobStatus.MERGED, reason="r", connection=connection, record=record)
    except IllegalTransitionError as exc:
        message = str(exc)
    else:  # pragma: no cover - the raise below is the failure report
        raise AssertionError("queued -> merged was accepted")
    assert "queued" in message and "merged" in message
    assert "claimed" in message and "escalated" in message and "superseded" in message


def test_a_status_outside_the_thirteen_is_named_not_a_key_error() -> None:
    connection, record, job = bench()
    broken = Job(**{**job.__dict__, "status": "nearly_approved"})
    try:
        transition(broken, JobStatus.CLAIMED, reason="r", connection=connection, record=record)
    except LifecycleError as exc:
        assert "nearly_approved" in str(exc)
    else:  # pragma: no cover - the raise below is the failure report
        raise AssertionError("an unknown stored status was accepted")
    assert entries(connection) == []


# -- T2: one transaction ---------------------------------------------------------


def test_a_legal_transition_commits_the_status_and_its_entry_together() -> None:
    """§8 T2. Durability is read back on a *second* connection to a file database: an
    uncommitted write is invisible there, so this proves the commit rather than the
    in-connection view of it."""
    with tempfile.TemporaryDirectory() as directory:
        path = str(pathlib.Path(directory) / "state.db")
        connection, record, job = bench(status=JobStatus.CLAIMED, path=path)
        moved = transition(
            job, JobStatus.PLANNED, reason="plan and carry-over recorded",
            connection=connection, record=record,
        )
        assert moved.status is JobStatus.PLANNED
        assert moved.id == job.id and moved.head_sha == job.head_sha

        observer = sqlite3.connect(path)
        assert stored_status(observer) == "planned"
        rows = entries(observer)
        assert len(rows) == 1
        assert rows[0][1] == "transition"
        observer.close()


def test_the_entry_payload_is_section_sixs_eight_fields() -> None:
    """§6: `P-12-record.md` §6 publishes this exact shape, so `resolve_job` and `explain`
    can reconstruct identity and supersession chains from `record_entries` alone."""
    import json

    connection, record, job = bench(status=JobStatus.CLAIMED)
    transition(
        job, JobStatus.PLANNED, reason="plan and carry-over recorded",
        connection=connection, record=record,
    )
    payload = json.loads(entries(connection)[0][2])
    assert payload == {
        "from_state": "claimed",
        "to_state": "planned",
        "reason": "plan and carry-over recorded",
        "repo": "owner/name",
        "number": 7,
        "head_sha": HEAD,
        "base_sha": BASE,
        "predecessor_job": None,
    }


def test_the_arrival_transition_records_no_from_state() -> None:
    """§6: "every call to `transition()`, including the arrival case (`from_state:
    None`)". The arrival edge is the one not in §2's table — a job that has just arrived
    has no previous state to leave."""
    import json

    connection, record, job = bench(status=JobStatus.QUEUED)
    arrived = transition(
        job, JobStatus.QUEUED, reason="admitted", connection=connection, record=record,
        arrival=True,
    )
    assert arrived.status is JobStatus.QUEUED
    payload = json.loads(entries(connection)[0][2])
    assert payload["from_state"] is None and payload["to_state"] == "queued"


def test_the_arrival_case_cannot_be_used_to_bypass_the_table() -> None:
    """`arrival=True` is accepted for `queued → queued` only. Anything else would be a
    free edge into any state, which is exactly what the closed table forbids."""
    connection, record, job = bench(status=JobStatus.JUDGED)
    for from_status, target in (
        (JobStatus.JUDGED, JobStatus.QUEUED),
        (JobStatus.QUEUED, JobStatus.APPROVED),
    ):
        candidate = Job(**{**job.__dict__, "status": from_status})
        try:
            transition(
                candidate, target, reason="r", connection=connection, record=record, arrival=True
            )
        except IllegalTransitionError:
            pass
        else:  # pragma: no cover - the raise below is the failure report
            raise AssertionError(f"arrival {from_status.value} -> {target.value} was accepted")
    assert entries(connection) == []


def test_a_status_write_that_matches_no_row_is_named_not_silent() -> None:
    """A `jobs` row that is not there makes the `UPDATE` a no-op, and a silent no-op here
    is a job the record says moved and the table says did not."""
    connection = new_db()
    record = SQLiteRecordWriter(connection, keystore=NoKeyStore())
    try:
        transition(
            make_job(status=JobStatus.CLAIMED), JobStatus.PLANNED, reason="r",
            connection=connection, record=record,
        )
    except UnknownJobError:
        pass
    else:  # pragma: no cover - the raise below is the failure report
        raise AssertionError("a transition for an absent job was accepted")
    assert entries(connection) == []


# -- T3: a failure in either half leaves neither durable -------------------------


def test_a_failing_append_rolls_the_status_back() -> None:
    """§8 T3, first half: "a failing append leaves `jobs.status` at its old value"."""
    connection, real, job = bench(status=JobStatus.CLAIMED)
    record = FlakyWriter(real, fail_on=(1,))
    try:
        transition(job, JobStatus.PLANNED, reason="r", connection=connection, record=record)
    except AppendFailed:
        pass
    else:  # pragma: no cover - the raise below is the failure report
        raise AssertionError("a failed append was not a failed transition")
    assert stored_status(connection) == "claimed"
    assert entries(connection) == []


def test_a_failing_status_write_leaves_no_entry() -> None:
    """§8 T3, second half: "a failing update leaves no `transition` entry". The `UPDATE`
    is refused by the database itself, inside the transaction the append would join."""
    connection, record, job = bench(status=JobStatus.CLAIMED)
    connection.executescript(
        "CREATE TRIGGER forbid_status_write BEFORE UPDATE ON jobs "
        "BEGIN SELECT RAISE(ABORT, 'refused'); END;"
    )
    try:
        transition(job, JobStatus.PLANNED, reason="r", connection=connection, record=record)
    except sqlite3.Error:
        pass
    else:  # pragma: no cover - the raise below is the failure report
        raise AssertionError("a refused update was not a failed transition")
    assert stored_status(connection) == "claimed"
    assert entries(connection) == []


def test_the_rolled_back_transition_is_followed_by_exactly_one_stop() -> None:
    """§8 T3, together: "the original transition is rolled back and exactly one `STOPPED`
    transition is committed"."""
    import json

    connection, real, job = bench(status=JobStatus.CLAIMED)
    record = FlakyWriter(real, fail_on=(1,))
    try:
        transition(job, JobStatus.PLANNED, reason="r", connection=connection, record=record)
    except AppendFailed:
        stopped = safe_stop(
            job, reason="persistence failure contained (AppendFailed)",
            connection=connection, record=record,
        )
    assert stopped.status is JobStatus.STOPPED
    assert stored_status(connection) == "stopped"
    rows = entries(connection)
    assert len(rows) == 1
    payload = json.loads(rows[0][2])
    assert payload["from_state"] == "claimed" and payload["to_state"] == "stopped"


# -- T4: the fallback's own failure ----------------------------------------------


def test_a_failing_fallback_stop_propagates_and_keeps_the_last_good_state() -> None:
    """§8 T4: "`AppendFailed` propagates and the last-good state remains durable". There
    is no second fallback: two failed persistence attempts is a machine that cannot record
    what it is doing, and continuing would be the silent continue this part prevents."""
    connection, _real, job = bench(status=JobStatus.CLAIMED)
    record = AlwaysFailingWriter()
    try:
        safe_stop(job, reason="contained", connection=connection, record=record)
    except AppendFailed:
        pass
    else:  # pragma: no cover - the raise below is the failure report
        raise AssertionError("the fallback stop's own failure was swallowed")
    assert stored_status(connection) == "claimed"
    assert entries(connection) == []


# -- §5: the write-once snapshot pin ---------------------------------------------


def test_the_first_pin_is_written_in_the_transition_that_follows_it() -> None:
    """§5: "writes … `jobs.snapshot_hash` exactly once — immediately after a successful
    first E-03 pin, in the same transaction as that transition"."""
    connection, record, job = bench(status=JobStatus.QUEUED)
    moved = transition(
        job, JobStatus.CLAIMED, reason="review authority granted; lease claimed",
        connection=connection, record=record, snapshot_hash="sha256:pinned",
    )
    assert stored_pin(connection) == "sha256:pinned"
    assert stored_status(connection) == "claimed"
    assert moved.snapshot_hash == "sha256:pinned"


def test_a_pinned_job_keeps_its_hash_when_a_later_transition_offers_another() -> None:
    """RQA-NFR-010 and U-QUEUE-10: the pin is write-once per job, so a configuration edit
    between a stop and its retry cannot change what a review was judged against."""
    connection, record, job = bench(status=JobStatus.STOPPED, snapshot_hash="sha256:original")
    moved = transition(
        job, JobStatus.CLAIMED, reason="retry", connection=connection, record=record,
        snapshot_hash="sha256:edited-config",
    )
    assert stored_pin(connection) == "sha256:original"
    assert moved.snapshot_hash == "sha256:original"
    assert stored_status(connection) == "claimed"


def test_the_pin_rolls_back_with_its_transition() -> None:
    """The pin is in the transition's transaction, not beside it: a failed append leaves
    the job unpinned as well as unmoved."""
    connection, real, job = bench(status=JobStatus.QUEUED)
    record = FlakyWriter(real, fail_on=(1,))
    try:
        transition(
            job, JobStatus.CLAIMED, reason="r", connection=connection, record=record,
            snapshot_hash="sha256:pinned",
        )
    except AppendFailed:
        pass
    else:  # pragma: no cover - the raise below is the failure report
        raise AssertionError("a failed append left a pinned job")
    assert stored_pin(connection) is None
    assert stored_status(connection) == "queued"


def test_a_transition_without_a_pin_never_touches_the_column() -> None:
    connection, record, job = bench(status=JobStatus.CLAIMED, snapshot_hash="sha256:original")
    transition(job, JobStatus.PLANNED, reason="r", connection=connection, record=record)
    assert stored_pin(connection) == "sha256:original"
    connection2, record2, job2 = bench(status=JobStatus.CLAIMED)
    transition(job2, JobStatus.PLANNED, reason="r", connection=connection2, record=record2)
    assert stored_pin(connection2) is None


# -- §3.1: admit's arrival and its containment boundary --------------------------


def test_admit_writes_the_arrival_transition_once() -> None:
    """§3.1: "writes the arrival `queued` transition when necessary". Necessary means the
    job has no `transition` entry yet, which is the only durable evidence of arrival."""
    connection, record, job = bench(status=JobStatus.QUEUED)
    deps = lifecycle_deps(connection, record)
    assert admit(job=job, deps=deps) is JobStatus.QUEUED
    assert len(entries(connection)) == 1
    assert admit(job=job, deps=deps) is JobStatus.QUEUED
    assert len(entries(connection)) == 1


def test_admit_reports_the_status_the_job_rests_at() -> None:
    """A re-admitted job that already has its arrival entry returns the durable status it
    is at, not the one it arrived with."""
    connection, record, job = bench(status=JobStatus.QUEUED)
    deps = lifecycle_deps(connection, record)
    admit(job=job, deps=deps)
    escalated = transition(
        job, JobStatus.ESCALATED, reason="authority requirement", connection=connection,
        record=record,
    )
    assert admit(job=escalated, deps=deps) is JobStatus.ESCALATED
    assert len(entries(connection)) == 2


def test_admit_refuses_a_mid_lifecycle_job_with_no_recorded_arrival() -> None:
    """A job at `judged` with no `transition` entry is a record that cannot explain the
    state the table claims — a named error, never a silently written second arrival."""
    connection, record, job = bench(status=JobStatus.JUDGED)
    try:
        admit(job=job, deps=lifecycle_deps(connection, record))
    except LifecycleError as exc:
        assert "queued" in str(exc)
    else:  # pragma: no cover - the raise below is the failure report
        raise AssertionError("a mid-lifecycle job with no arrival entry was admitted")
    assert entries(connection) == []


def test_a_contained_persistence_failure_becomes_one_safe_stop() -> None:
    """§3.1: "an `AppendFailed`, `sqlite3.Error`, or `OSError` causes one `STOPPED`
    transition and return". The failure here is a real `sqlite3.Error` from the
    `record_entries` read, and the stop is committed through the real writer."""
    import json

    connection, record, job = bench(status=JobStatus.CLAIMED, factory=FailingReadConnection)
    claimed = transition(
        job, JobStatus.PLANNED, reason="planned", connection=connection, record=record,
    )
    before = len(entries(connection))
    assert admit(job=claimed, deps=lifecycle_deps(connection, record)) is JobStatus.STOPPED
    assert stored_status(connection) == "stopped"
    rows = entries(connection)
    assert len(rows) == before + 1
    payload = json.loads(rows[-1][2])
    assert payload["from_state"] == "planned" and payload["to_state"] == "stopped"
    assert payload["reason"] == "persistence failure contained (OperationalError)"


def test_containment_stops_from_the_durable_state_not_the_handed_one() -> None:
    """The job P-01 hands in can be stale by the time the cascade fails, so the stop is
    made from the row as the committed table holds it."""
    connection, record, job = bench(status=JobStatus.CLAIMED, factory=FailingReadConnection)
    transition(job, JobStatus.PLANNED, reason="planned", connection=connection, record=record)
    import json

    assert admit(job=job, deps=lifecycle_deps(connection, record)) is JobStatus.STOPPED
    payload = json.loads(entries(connection)[-1][2])
    assert payload["from_state"] == "planned", "the stale in-memory `claimed` was used"


def test_a_failure_the_closed_table_cannot_stop_from_propagates() -> None:
    """§2's table has no `queued → stopped` edge, so a contained failure at `queued` has
    no safe stop to make. The rollback has already left the last-good state intact and the
    failure goes to P-01, which re-offers the job on a later tick. Inventing an edge would
    break the table; returning the unchanged status would swallow the failure."""
    connection, record, job = bench(status=JobStatus.QUEUED, factory=FailingReadConnection)
    try:
        admit(job=job, deps=lifecycle_deps(connection, record))
    except sqlite3.OperationalError:
        pass
    else:  # pragma: no cover - the raise below is the failure report
        raise AssertionError("a failure with no licensed stop was swallowed")
    assert stored_status(connection) == "queued"
    assert entries(connection) == []


def test_a_named_neighbour_error_propagates_and_is_not_a_stop() -> None:
    """§8 T5: "it propagates; P-02 does not misclassify it as `STOPPED`". Only the three
    persistence types §3.1 names are contained."""
    connection, _real, job = bench(status=JobStatus.QUEUED)
    try:
        admit(job=job, deps=lifecycle_deps(connection, ExplodingWriter()))
    except LifecycleError as exc:
        assert "neighbour" in str(exc)
    else:  # pragma: no cover - the raise below is the failure report
        raise AssertionError("a neighbour's named error was contained")
    assert stored_status(connection) == "queued"


def test_a_contained_failure_for_a_vanished_job_is_named() -> None:
    """No `jobs` row means no safe stop is possible; the branch is named rather than
    falling through to a status nobody wrote."""
    connection, record, job = bench(status=JobStatus.CLAIMED, factory=FailingReadConnection)
    connection.execute("DELETE FROM jobs WHERE id = ?", (job.id,))
    connection.commit()
    try:
        admit(job=job, deps=lifecycle_deps(connection, record))
    except UnknownJobError as exc:
        assert "OperationalError" in str(exc)
    else:  # pragma: no cover - the raise below is the failure report
        raise AssertionError("a contained failure for a vanished job returned a status")


def test_the_fallback_stops_own_append_failure_propagates_through_admit() -> None:
    """§8 T4 through the boundary that uses it: the durable state is the one committed
    before the failure, and nothing reports a stop that was never written."""
    connection, real, job = bench(status=JobStatus.CLAIMED, factory=FailingReadConnection)
    transition(job, JobStatus.PLANNED, reason="planned", connection=connection, record=real)
    before = entries(connection)
    record = FlakyWriter(real, fail_on=(1,))
    try:
        admit(job=job, deps=lifecycle_deps(connection, record))
    except AppendFailed:
        pass
    else:  # pragma: no cover - the raise below is the failure report
        raise AssertionError("the fallback stop's failure was swallowed")
    assert stored_status(connection) == "planned"
    assert entries(connection) == before
