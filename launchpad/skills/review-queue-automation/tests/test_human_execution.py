#!/usr/bin/env python3
"""Tests that a delayed human approval is APPLIED, and applied safely.

`resume` previously moved the job to `approval_revalidation` and stopped, so a
human approval never resulted in an approval. It also revalidated against the
job's own recorded head by default, which always matches and made the staleness
check meaningless.

Now: the live head is required (an unreadable head refuses), the decision is
revalidated against it, and the approval runs through the SAME guarded executor
as the automatic path — a human decision authorizes an approval rather than
bypassing its checks.
"""

from __future__ import annotations

import json
import pathlib
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scripts"))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import approval_action  # noqa: E402
import human_cli  # noqa: E402
from approval import decide  # noqa: E402
from common import State, utcnow  # noqa: E402
from test_human_queue import (  # noqa: E402
    _human_pending_job,
    _status,
    enqueue_for,
    policy,
)


def _seed(state: State, number: int, head: str, *, node_id: str = "PR_node") -> str:
    jid = _human_pending_job(state, number=number, head=head)
    now = utcnow()
    state.db.execute(
        "INSERT OR REPLACE INTO prs(repo,number,head_sha,updated_at,payload,open,last_seen) "
        "VALUES(?,?,?,?,?,1,?)",
        ("o/r", number, head, now,
         json.dumps({"head": {"sha": head}, "node_id": node_id,
                     "draft": False, "user": {"login": "alice"}}), now),
    )
    state.db.commit()
    req = enqueue_for(state, jid, "o/r", number, head)
    decide(state, req["request_id"], "approve", actor="jeff")
    return jid


def _with_fake_approve(result, calls):
    def fake(state, **kwargs):
        calls.append(kwargs)
        return result

    previous = approval_action.approve
    approval_action.approve = fake
    return previous


# -- the approval is actually applied ----------------------------------
def test_human_approval_reaches_a_verified_approval() -> None:
    state = State({"state_dir": tempfile.mkdtemp()})
    calls: list = []
    previous = _with_fake_approve((True, "approved", "approved"), calls)
    try:
        jid = _seed(state, 20, "h20")
        result = human_cli._cmd_resume(state, jid, policy(), current_head_sha="h20")

        assert _status(state, jid) == "completed_auto_approved", result
        assert result["approval_outcome"] == "approved"
        assert len(calls) == 1, "the guarded executor must run exactly once"
    finally:
        approval_action.approve = previous
        state.close()


def test_human_decision_uses_the_same_guarded_executor() -> None:
    """The human path must not get a shortcut around REST revalidation."""
    state = State({"state_dir": tempfile.mkdtemp()})
    calls: list = []
    previous = _with_fake_approve((True, "approved", "approved"), calls)
    try:
        jid = _seed(state, 21, "h21")
        human_cli._cmd_resume(state, jid, policy(), current_head_sha="h21")

        passed = calls[0]
        # `config` present => approval_action wires the REAL REST revalidation and
        # post-mutation verification rather than skipping them.
        assert passed.get("config") is not None
        assert passed["head_sha"] == "h21"
        assert passed["pr_node_id"] == "PR_node"
        assert passed["decision_id"]
    finally:
        approval_action.approve = previous
        state.close()


def test_decision_is_recorded_as_human_authorized() -> None:
    state = State({"state_dir": tempfile.mkdtemp()})
    calls: list = []
    previous = _with_fake_approve((True, "approved", "approved"), calls)
    try:
        jid = _seed(state, 22, "h22")
        human_cli._cmd_resume(state, jid, policy(), current_head_sha="h22")

        row = state.db.execute(
            "SELECT mode, status FROM approval_decisions"
        ).fetchone()
        assert row["mode"] == "human", "the audit trail must show who authorized it"
        assert row["status"] == "eligible"
        assert "jeff" in calls[0]["body"], "the review body must name the authorizer"
    finally:
        approval_action.approve = previous
        state.close()


# -- failure modes -----------------------------------------------------
def test_uncertain_mutation_safe_stops() -> None:
    state = State({"state_dir": tempfile.mkdtemp()})
    calls: list = []
    previous = _with_fake_approve((False, "uncertain", "cannot confirm"), calls)
    try:
        jid = _seed(state, 23, "h23")
        result = human_cli._cmd_resume(state, jid, policy(), current_head_sha="h23")
        assert _status(state, jid) == "safe_stop"
        assert result["approval_outcome"] == "uncertain"
    finally:
        approval_action.approve = previous
        state.close()


def test_missing_node_id_safe_stops_before_any_mutation() -> None:
    state = State({"state_dir": tempfile.mkdtemp()})
    calls: list = []
    previous = _with_fake_approve((True, "approved", "approved"), calls)
    try:
        jid = _seed(state, 24, "h24", node_id="")
        result = human_cli._cmd_resume(state, jid, policy(), current_head_sha="h24")
        assert _status(state, jid) == "safe_stop"
        assert result["approval_outcome"] == "missing_node_id"
        assert calls == [], "no mutation without a PR node id"
    finally:
        approval_action.approve = previous
        state.close()


def test_no_execute_stops_before_the_mutation() -> None:
    state = State({"state_dir": tempfile.mkdtemp()})
    calls: list = []
    previous = _with_fake_approve((True, "approved", "approved"), calls)
    try:
        jid = _seed(state, 25, "h25")
        result = human_cli._cmd_resume(
            state, jid, policy(), current_head_sha="h25", execute=False
        )
        assert result["status"] == "approval_revalidation"
        assert _status(state, jid) == "approval_revalidation"
        assert calls == []
    finally:
        approval_action.approve = previous
        state.close()


def test_stale_head_never_reaches_the_executor() -> None:
    state = State({"state_dir": tempfile.mkdtemp()})
    calls: list = []
    previous = _with_fake_approve((True, "approved", "approved"), calls)
    try:
        jid = _seed(state, 26, "h26")
        result = human_cli._cmd_resume(state, jid, policy(), current_head_sha="MOVED")
        assert "error" in result
        assert "advanced since review" in result["error"]
        assert calls == [], "a stale head must be refused before any mutation"
        assert _status(state, jid) == "human_approval_pending"
        assert state.db.execute(
            "SELECT 1 FROM approval_decisions"
        ).fetchone() is None, "no decision record may be created for a stale head"
    finally:
        approval_action.approve = previous
        state.close()


def test_job_not_awaiting_approval_is_refused() -> None:
    state = State({"state_dir": tempfile.mkdtemp()})
    calls: list = []
    previous = _with_fake_approve((True, "approved", "approved"), calls)
    try:
        jid = _seed(state, 27, "h27")
        state.db.execute("UPDATE jobs SET status='safe_stop' WHERE id=?", (jid,))
        state.db.commit()
        result = human_cli._cmd_resume(state, jid, policy(), current_head_sha="h27")
        assert "error" in result
        assert "not awaiting human approval" in result["error"]
        assert calls == []
    finally:
        approval_action.approve = previous
        state.close()


def test_unknown_job_is_refused() -> None:
    state = State({"state_dir": tempfile.mkdtemp()})
    try:
        result = human_cli._cmd_resume(state, "nope", policy(), current_head_sha="h")
        assert "error" in result
        assert "job not found" in result["error"]
    finally:
        state.close()
