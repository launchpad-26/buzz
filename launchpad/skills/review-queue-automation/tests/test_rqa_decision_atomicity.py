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


# -- The github stores must not commit a connection they do not own ---------------
#
# The savepoint in `rqa/lifecycle/transition.py` closed the path where a nested
# *transition* committed the caller's transaction. It did not close the class.
# `rqa/cli/composition.py` hands one connection to every collaborator, and each of
# the three stores in `rqa/github/store.py` ends its write with an unconditional
# `self._connection.commit()`. `resume()`'s first action is a live GitHub read
# (`rqa/lifecycle/resume.py`), so that read commits the decision `decide()` left
# provisional on purpose. A later validation failure then has nothing to roll back:
# the escalation is durably closed, the job is stuck at `escalated`, and the retry
# is refused ALREADY_CLOSED, so the corrected decision can never be applied.
#
# Every other decide()/resume() test substitutes a fake github that never reaches a
# store, which is why the suite was green and blind to this. These two drive the
# real `Transport` over the real `Sqlite*Store`s, wired the way the composition root
# wires them, with only the network send stubbed.

import sqlite3
import tempfile

from rqa.cli.composition import build_composition
from rqa.github import ensure_schema as github_ensure_schema
from rqa.github.store import MutationRow, SqliteApiCallStore, SqliteEtagStore, SqliteMutationStore
from rqa.github.transport import Response, Transport


def _stub_send(request):
    """One completed exchange carrying an ETag, so both read-path stores write."""
    del request
    return Response(status=200, headers={"ETag": '"abc"', "X-RateLimit-Remaining": "42"}, body="{}")


class GithubReadingThroughRealStores:
    """A `facts()` that performs a real `Transport` exchange over real stores before
    answering — exactly what the true `GithubAdapter.facts()` does to the connection,
    without assembling every GraphQL fixture the full read needs."""

    def __init__(self, inner, transport):
        self.inner = inner
        self.transport = transport

    def facts(self, *, job, record):
        self.transport._exchange(
            _request(), kind="rest", operation="facts"
        )
        self.transport._get_one(
            "https://api.github.com/probe",
            operation="facts",
            accept="application/vnd.github+json",
            credential="not-a-token",
        )
        return self.inner.facts(job=job, record=record)


def _request():
    from rqa.github.transport import Request

    return Request(method="GET", url="https://api.github.com/probe", headers={}, body=None)


def test_a_real_github_read_inside_decide_does_not_commit_the_decision():
    """Blocker: `decide()` -> `resume()` -> a real GitHub read must leave the
    caller's transaction open and its decision undoable.

    Without the commit discipline at the composition root, `connection.in_transaction`
    is already False by the time the caller gets control back, the rollback below is a
    no-op, and the decision plus the escalation close survive it.
    """
    connection, record, job, store, raised = fx._escalated_job_with_a_real_open_row()
    try:
        github_ensure_schema(connection)
        connection.commit()
        transport = Transport(
            etags=SqliteEtagStore(_caller_owned(connection)),
            api_calls=SqliteApiCallStore(_caller_owned(connection)),
            send=_stub_send,
            resolve_credential=lambda: "not-a-token",
        )
        client = fx.RealEscalationClient(store)
        deps = fx._deps_for_12b(connection, record, job=job, escalation_client=client)
        deps = _with_github(deps, GithubReadingThroughRealStores(deps.github, transport))

        decide(
            raised.id, "human-reviewer", "reviewed on GitHub", "changes_requested",
            store=store, record=record, jobs=fx.FakeJobs(job),
            lifecycle=fx.RealLifecycle(), deps=deps,
        )

        assert connection.in_transaction, (
            "a github read inside resume() ended the caller's transaction; the "
            "decision is now durable and the CLI's rollback cannot undo it"
        )
        connection.rollback()
        assert connection.execute(
            "SELECT count(*) FROM record_entries WHERE kind='decision'"
        ).fetchone()[0] == 0
        assert store.get(raised.id).status == "open"
        assert fx.stored_status(connection, job.id) == "escalated"
    finally:
        connection.close()


def _caller_owned(connection):
    from rqa.cli.composition import _CallerOwnedConnection

    return _CallerOwnedConnection(connection)


def _with_github(deps, github):
    from dataclasses import replace

    return replace(deps, github=github)


def test_the_composition_root_wires_the_github_stores_so_they_cannot_commit():
    """The general guard behind the test above: whatever `build_composition` hands the
    three `rqa/github/store.py` stores, a write through any of them must not end a
    transaction the caller owns, and must be undone by the caller's rollback.

    This is asserted against the real `build_composition` wiring rather than against a
    hand-built `Transport`, so it fails if a future store is added to the composition
    root over the raw connection.
    """
    import pathlib

    state_dir = pathlib.Path(tempfile.mkdtemp())
    # ADR-0066 is keyless: the composition must not accept or consult a
    # credential-store collaborator merely to build the transaction boundary.
    comp = build_composition(state_dir)
    connection = comp.connection
    try:
        connection.execute("CREATE TABLE probe(x)")
        connection.commit()
        connection.execute("INSERT INTO probe VALUES(1)")
        assert connection.in_transaction

        comp.github.transport.etags.put("cache-key", '"etag"', "{}", None)
        comp.github.transport.api_calls.record("rest", "facts", 200, {})
        comp.github.mutations.put(
            MutationRow("mid", "job-1", "comment", "pending", None, "t", "t")
        )

        assert connection.in_transaction, (
            "a github store committed the composition's connection; every caller that "
            "leaves work provisional on it loses the ability to roll that work back"
        )
        connection.rollback()
        assert connection.execute("SELECT count(*) FROM probe").fetchone()[0] == 0
        assert connection.execute("SELECT count(*) FROM etags").fetchone()[0] == 0
        assert connection.execute("SELECT count(*) FROM api_calls").fetchone()[0] == 0
        assert connection.execute("SELECT count(*) FROM mutations").fetchone()[0] == 0
    finally:
        connection.close()


def test_the_caller_owned_view_refuses_to_roll_back_its_owners_transaction():
    """`commit()` is inert, but `rollback()` fails loud: a collaborator discarding the
    owner's transaction is the same defect in the other direction, and silence there
    would hide it."""
    from rqa.cli.composition import _CallerOwnedConnection

    connection = sqlite3.connect(":memory:")
    try:
        view = _CallerOwnedConnection(connection)
        view.execute("CREATE TABLE t(x)")
        assert view.commit() is None
        try:
            view.rollback()
        except RuntimeError:
            pass
        else:
            raise AssertionError("rollback through the caller-owned view must raise")
    finally:
        connection.close()
