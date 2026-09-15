"""Regression coverage for PR #2269: nested transitions must not erase decisions."""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import test_rqa_escalation_ac13_resume as fx
from rqa.contracts import AppendFailed
from rqa.escalation import decide


class FailTransition:
    def __init__(self, inner):
        self.inner = inner

    def append(self, job_id, kind, payload):
        if kind == "transition":
            raise AppendFailed("injected transition persistence failure")
        return self.inner.append(job_id, kind, payload)


def _decide(connection, record, job, store, raised):
    client = fx.RealEscalationClient(store)
    deps = fx._deps_for_12b(connection, record, job=job, escalation_client=client)
    return decide(
        raised.id, "human-reviewer", "reviewed on GitHub", "changes_requested",
        store=store, record=record, jobs=fx.FakeJobs(job),
        lifecycle=fx.RealLifecycle(), deps=deps,
    )


def test_failed_resume_propagates_and_preserves_the_decision_until_caller_rollback():
    connection, record, job, store, raised = fx._escalated_job_with_a_real_open_row()
    try:
        try:
            _decide(connection, FailTransition(record), job, store, raised)
        except AppendFailed:
            pass
        else:
            raise AssertionError("a failed transition must not report decided")
        assert connection.in_transaction
        assert connection.execute("SELECT count(*) FROM record_entries WHERE kind='decision'").fetchone()[0] == 1
        assert store.get(raised.id).status == "closed"
        connection.rollback()
        assert connection.execute("SELECT count(*) FROM record_entries WHERE kind='decision'").fetchone()[0] == 0
        assert store.get(raised.id).status == "open"
        assert fx.stored_status(connection, job.id) == "escalated"
    finally:
        connection.close()


def test_successful_resume_does_not_commit_the_callers_decision_early():
    connection, record, job, store, raised = fx._escalated_job_with_a_real_open_row()
    try:
        _decide(connection, record, job, store, raised)
        assert connection.in_transaction
        assert fx.stored_status(connection, job.id) == "changes_requested"
        connection.rollback()
        assert store.get(raised.id).status == "open"
        assert fx.stored_status(connection, job.id) == "escalated"
        _decide(connection, record, job, store, raised)
        connection.commit()
        assert store.get(raised.id).status == "closed"
        assert fx.stored_status(connection, job.id) == "changes_requested"
    finally:
        connection.close()
