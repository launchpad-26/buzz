#!/usr/bin/env python3
"""Fake human-approval queue tests: two pending requests while another job
proceeds, resume revalidation, expiry/stale rejection, decline terminal,
idempotency, and supersede on head/policy change. No GitHub, no models.
"""

from __future__ import annotations

import datetime as dt
import json
import pathlib
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scripts"))

from approval import (  # noqa: E402
    RequestQueueError,
    decide,
    enqueue,
    find_approved,
    get,
    is_eligible,
    is_expired,
    list_pending,
    policy_hash,
    supersede_for_head,
    supersede_for_policy,
)
from common import State, job_id  # noqa: E402


def fresh_state() -> State:
    return State({"state_dir": tempfile.mkdtemp()})


def policy() -> dict:
    return {
        "approval": {"effective_risk_max": 24},
        "risk": {"bands": {"low": 24, "medium": 99, "high": 100}},
        "human_queue": {"expiry_minutes": 1440},
    }


def add_job(state: State, *, repo: str = "o/r", number: int = 1, head: str = "h1", status: str = "detected") -> str:
    jid = job_id(repo, number, head, "incoming_review")
    now = dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")
    state.db.execute(
        "INSERT INTO jobs(id,repo,number,head_sha,lane,status,artifact_dir,created_at,updated_at) "
        "VALUES(?,?,?,?,?,?,?,?,?)",
        (jid, repo, number, head, "incoming_review", status, str(state.job_dir(jid)), now, now),
    )
    state.db.commit()
    return jid


def _human_pending_job(state: State, number: int, head: str) -> str:
    jid = add_job(state, number=number, head=head, status="human_approval_pending")
    return jid


def enqueue_for(state: State, jid: str, repo: str, number: int, head: str, pol=None) -> dict:
    return enqueue(
        state, repo=repo, number=number, head_sha=head, policy=pol or policy(),
        summary="s", assurance={}, reviewers=["m"], risk_score=5, risk_band="low",
        protected=[], failed_gates=[], ci={}, findings=[], recommendation="approve",
        rationale="r", action="approve", job_id=jid,
    )


def _dispatch_cfg() -> dict:
    return {
        "version": 1,
        "login": "tucktuck101",
        "state_dir": tempfile.mkdtemp(),
        "repository": {"slug": "o/r", "root": "/tmp", "base": "launchpad"},
        "logging": {"directory": tempfile.mkdtemp(), "format": "otel-jsonl"},
        "models": {"primary": [], "secondary": []},
        "assurance": {"large_diff_lines": 700},
        "dispatch": {"incoming_canary_approved": True, "author_canary_approved": True},
        "approval": {"mode": "human_escalation", "approval_enabled": False, "live_canary_approved": False},
        "risk": {"bands": {"low": 24, "medium": 99, "high": 100}, "protected_triggers": []},
        "human_queue": {"expiry_minutes": 1440},
        "github": {"read_only": True, "api_version": "2022-11-28"},
    }


def _fake_panel_missing(calls: list):
    def run(cfg, state, repo, number, lane, job_id, profile, logger=None):
        calls.append(job_id)
        return {"profile": profile, "required_reviewers": 2, "completed_reviewers": ["a"],
                "complete": True, "signals": ["MISSING_EVIDENCE"], "outcome": "complete"}
    return run


def _status(state: State, jid: str) -> str | None:
    row = state.db.execute("SELECT status FROM jobs WHERE id=?", (jid,)).fetchone()
    return row["status"] if row else None


def test_two_pending_requests_while_another_job_proceeds() -> None:
    """Two pending human requests (job A, job B) coexist; an unrelated detected
    job still dispatches and is never blocked by them."""
    import dispatcher

    state = fresh_state()
    try:
        jid_a = _human_pending_job(state, number=1, head="h1")
        jid_b = _human_pending_job(state, number=2, head="h2")
        enqueue_for(state, jid_a, "o/r", 1, "h1")
        enqueue_for(state, jid_b, "o/r", 2, "h2")
        assert {p["number"] for p in list_pending(state)} == {1, 2}

        # an unrelated detected job still dispatches (MISSING_EVIDENCE -> human_required)
        jid_c = add_job(state, number=3, head="h3")
        calls: list = []
        saved_panel = dispatcher.run_panel
        saved_gather = dispatcher.collect_evidence
        saved_decide = dispatcher.decide_assurance
        dispatcher.run_panel = _fake_panel_missing(calls)

        from assurance import Profile

        def _min(cfg, state, repo, number, lane):
            return Profile("workhorse", "medium", "challenger")

        dispatcher.decide_assurance = _min

        def boom_gather(cfg, state, repo, number, lane, job_id):
            raise RuntimeError("no gather available")

        dispatcher.collect_evidence = boom_gather
        try:
            result = dispatcher.run_job(
                _dispatch_cfg(),
                {"job_id": jid_c, "repo": "o/r", "number": 3, "lane": "incoming_review"},
                state=state,
                claim_lease=False,  # offline test: no GitHub assignee mutation
            )
        finally:
            dispatcher.run_panel = saved_panel
            dispatcher.collect_evidence = saved_gather
            dispatcher.decide_assurance = saved_decide
        # A and B remain pending through C's dispatch
        assert {p["number"] for p in list_pending(state)} == {1, 2}
        assert result["status"] == "human_required", result
    finally:
        state.close()


def test_resume_revalidation() -> None:
    """Resume transitions the job once the decision revalidates against the head."""
    state = fresh_state()
    try:
        jid = _human_pending_job(state, number=5, head="h5")
        req = enqueue_for(state, jid, "o/r", 5, "h5")
        dec = decide(state, req["request_id"], "approve", actor="human")
        assert dec["decision"] == "approve"
        assert _status_pending_req(state, 5) == ["decided"]  # request decided
        # job still awaiting approval until resume
        assert _status(state, jid) == "human_approval_pending"
        from human_cli import _cmd_resume

        # `execute=False` stops before the mutation so this test stays offline;
        # the head is supplied explicitly instead of being read from GitHub.
        res = _cmd_resume(state, jid, policy(), current_head_sha="h5", execute=False)
        assert res["status"] == "approval_revalidation", res
        assert res["head_source"] == "caller"
        assert _status(state, jid) == "approval_revalidation"
    finally:
        state.close()


def test_resume_refuses_when_the_live_head_cannot_be_read() -> None:
    """An unreadable live head is a refusal, never a pass."""
    state = fresh_state()
    try:
        jid = _human_pending_job(state, number=15, head="h15")
        req = enqueue_for(state, jid, "o/r", 15, "h15")
        decide(state, req["request_id"], "approve", actor="human")
        from human_cli import _cmd_resume

        res = _cmd_resume(state, jid, policy())  # no head, no GitHub reachable
        assert "error" in res
        assert "refusing to resume" in res["error"]
        assert _status(state, jid) == "human_approval_pending", "must not transition"
    finally:
        state.close()


def test_resume_recorded_head_escape_hatch_is_explicit_and_reported() -> None:
    state = fresh_state()
    try:
        jid = _human_pending_job(state, number=16, head="h16")
        req = enqueue_for(state, jid, "o/r", 16, "h16")
        decide(state, req["request_id"], "approve", actor="human")
        from human_cli import _cmd_resume

        res = _cmd_resume(state, jid, policy(), allow_recorded_head=True, execute=False)
        assert res["status"] == "approval_revalidation"
        assert "unverified" in res["head_source"], res
    finally:
        state.close()


def _status_pending_req(state: State, number: int) -> list[str]:
    rows = state.db.execute(
        "SELECT state FROM human_requests WHERE repo='o/r' AND number=? AND state!='pending'",
        (number,),
    ).fetchall()
    return [r["state"] for r in rows]


def test_expired_approval_cannot_resume() -> None:
    from human_cli import _cmd_resume

    state = fresh_state()
    try:
        jid = _human_pending_job(state, number=6, head="h6")
        req = enqueue_for(state, jid, "o/r", 6, "h6")
        decide(state, req["request_id"], "approve", actor="human")
        state.db.execute("UPDATE human_requests SET expires_at=? WHERE request_id=?",
                         (dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z"),
                          req["request_id"]))
        state.db.commit()
        assert is_expired(get(state, req["request_id"])) is True
        assert find_approved(state, jid, "o/r", 6, "h6", policy()) is None

        res = _cmd_resume(state, jid, policy(), current_head_sha="h6")
        assert "error" in res, res
        assert "no usable approved" in res["error"]
        assert _status(state, jid) == "human_approval_pending", "must not transition"
    finally:
        state.close()


def test_stale_sha_cannot_resume() -> None:
    """A decision made for an older head must never approve a newer revision."""
    from human_cli import _cmd_resume

    state = fresh_state()
    try:
        jid = _human_pending_job(state, number=7, head="h7")
        req = enqueue_for(state, jid, "o/r", 7, "h7")
        decide(state, req["request_id"], "approve", actor="human")
        # the PR's head changed since the approval
        assert find_approved(state, jid, "o/r", 7, "h8", policy()) is None

        res = _cmd_resume(state, jid, policy(), current_head_sha="h8")
        assert "error" in res, res
        assert "advanced since review" in res["error"]
        assert res["reviewed_head"] == "h7"
        assert res["current_head"] == "h8"
        assert _status(state, jid) == "human_approval_pending", "must not transition"
    finally:
        state.close()


def test_decline_is_terminal() -> None:
    state = fresh_state()
    try:
        jid = _human_pending_job(state, number=8, head="h8")
        req = enqueue_for(state, jid, "o/r", 8, "h8")
        dec = decide(state, req["request_id"], "decline", actor="human")
        assert dec["decision"] == "decline"
        assert dec.get("job_declined") is True
        assert _status(state, jid) == "completed_human_declined"
        try:
            decide(state, req["request_id"], "approve", actor="x")
            raise AssertionError("a decided request must not change again")
        except RequestQueueError:
            pass
    finally:
        state.close()


def test_idempotent_enqueue() -> None:
    state = fresh_state()
    try:
        jid = _human_pending_job(state, number=9, head="h9")
        a = enqueue_for(state, jid, "o/r", 9, "h9")
        b = enqueue_for(state, jid, "o/r", 9, "h9")
        assert a["request_id"] == b["request_id"]
        assert len([r for r in list_pending(state) if r["number"] == 9]) == 1
    finally:
        state.close()


def test_superseded_on_changed_head_and_policy() -> None:
    state = fresh_state()
    try:
        jid = _human_pending_job(state, number=10, head="h10")
        enqueue_for(state, jid, "o/r", 10, "h10")
        assert supersede_for_head(state, "o/r", 10, "h11") == 1
        assert list_pending(state) == []
        # a policy change supersedes a re-enqueued request on a fresh job
        jid2 = _human_pending_job(state, number=10, head="h10b")
        enqueue_for(state, jid2, "o/r", 10, "h10b", pol=policy())
        changed = {**policy(), "risk": {"bands": {"low": 1, "medium": 99, "high": 100}}}
        assert supersede_for_policy(state, "o/r", 10, changed) == 1
        assert list_pending(state) == []
    finally:
        state.close()


def test_is_eligible_and_policy_hash_bound() -> None:
    state = fresh_state()
    try:
        jid = _human_pending_job(state, number=11, head="h11")
        req = enqueue_for(state, jid, "o/r", 11, "h11")
        ph = policy_hash(policy())
        assert req["policy_hash"] == ph and len(ph) == 64
        assert is_eligible(req, "o/r", 11, "h11", policy()) is False
        r2 = decide(state, req["request_id"], "approve", actor="human")
        assert is_eligible(r2, "o/r", 11, "h11", policy()) is True
        changed = {**policy(), "risk": {"bands": {"low": 2, "medium": 99, "high": 100}}}
        assert is_eligible(r2, "o/r", 11, "h11", changed) is False
    finally:
        state.close()


if __name__ == "__main__":
    failures = 0
    passed = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                passed += 1
            except Exception as exc:
                failures += 1
                import traceback
                print(f"FAIL {name}: {exc}")
                traceback.print_exc()
    print(f"{passed} passed, {failures} failed")
    sys.exit(1 if failures else 0)