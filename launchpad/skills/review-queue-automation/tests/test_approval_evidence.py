#!/usr/bin/env python3
"""Tests that the external-evidence approval gates are actually enforced.

`compute_gates` keeps a backward-compatible fallback in which `bounded_change`,
`audit_writable`, `assurance_met`, `revalidation_ok` and `rate_limit_ok` default
to True when no evidence object is supplied. The dispatcher used to supply none,
so all five auto-passed in the LIVE path — `assurance_met` in particular meant
achieved assurance was never checked before approving.

The dispatcher must therefore always supply real values, each failing closed.
"""

from __future__ import annotations

import json
import pathlib
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scripts"))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import dispatcher  # noqa: E402
from common import State, utcnow  # noqa: E402
from test_dispatch_flow import (  # noqa: E402
    _clean_verdict,
    _config,
    fake_approve,
    fake_panel,
    patch_approval,
    patch_dispatcher,
    restore_approval,
    restore_dispatcher,
    seed_evidence,
    seed_job,
    seed_verdicts,
)


def _dispatch(
    *, number: int, additions: int = 2, daily_limit: int | None = None,
    prior_approvals: int = 0, rest_floor: int = 0, rest_remaining: int | None = None,
) -> dict:
    state = State({"state_dir": tempfile.mkdtemp()})
    saved = patch_dispatcher(run_panel=fake_panel("SUPPORTED"))
    previous = patch_approval(fake_approve(True, "approved"))
    try:
        cfg = _config("live")
        if daily_limit is not None:
            cfg["approval"]["daily_limit"] = daily_limit
        if rest_floor:
            cfg["poll"] = {"rest_remaining_floor": rest_floor}

        jid = seed_job(state, number=number, head=f"h{number}")
        seed_evidence(state, jid)
        seed_verdicts(state, jid, [_clean_verdict("opus", "anthropic"),
                                   _clean_verdict("ds", "openrouter")])

        row = state.db.execute(
            "SELECT payload FROM prs WHERE repo='o/r' AND number=?", (number,)
        ).fetchone()
        payload = json.loads(row["payload"])
        payload["additions"] = additions
        payload["deletions"] = 0
        state.db.execute("UPDATE prs SET payload=? WHERE repo='o/r' AND number=?",
                         (json.dumps(payload), number))

        now = utcnow()
        for i in range(prior_approvals):
            state.db.execute(
                "INSERT INTO mutations(client_mutation_id,operation,status,response,"
                "created_at,updated_at) VALUES(?,?,?,?,?,?)",
                (f"prior-{i}", "approve_review", "verified", "{}", now, now),
            )
        if rest_remaining is not None:
            state.db.execute(
                "INSERT INTO api_calls(called_at,transport,operation,status,remaining) "
                "VALUES(?,?,?,?,?)",
                (now, "rest", "pr_meta", 200, rest_remaining),
            )
        state.db.commit()

        return dispatcher.run_job(
            cfg, {"job_id": jid, "repo": "o/r", "number": number, "lane": "incoming_review"},
            state=state,
        )
    finally:
        restore_approval(previous)
        restore_dispatcher(saved)
        state.close()


# -- baseline ------------------------------------------------------------
def test_a_qualifying_pr_still_approves() -> None:
    """The gates must be enforceable without blocking legitimate approvals."""
    result = _dispatch(number=601)
    assert result["approval_disposition"] == "live"
    assert result["status"] == "completed_auto_approved"


# -- bounded change ------------------------------------------------------
def test_oversized_diff_blocks_approval() -> None:
    result = _dispatch(number=602, additions=5000)
    assert result["approval_disposition"] == "human_escalation"
    assert result["status"] == "human_approval_pending"


def test_diff_at_the_threshold_is_still_bounded() -> None:
    # default large_diff_lines in the fixture config is 700
    result = _dispatch(number=608, additions=700)
    assert result["approval_disposition"] == "live"


# -- rate limits ---------------------------------------------------------
def test_daily_cap_reached_blocks_approval() -> None:
    result = _dispatch(number=603, daily_limit=2, prior_approvals=2)
    assert result["approval_disposition"] == "human_escalation"


def test_daily_cap_with_headroom_allows_approval() -> None:
    result = _dispatch(number=604, daily_limit=5, prior_approvals=2)
    assert result["approval_disposition"] == "live"


def test_unknown_rest_remaining_fails_closed_against_a_floor() -> None:
    """An unknown rate-limit budget is not a pass."""
    result = _dispatch(number=605, rest_floor=200)
    assert result["approval_disposition"] == "human_escalation"


def test_rest_remaining_below_floor_blocks_approval() -> None:
    result = _dispatch(number=606, rest_floor=200, rest_remaining=50)
    assert result["approval_disposition"] == "human_escalation"


def test_rest_remaining_above_floor_allows_approval() -> None:
    result = _dispatch(number=607, rest_floor=200, rest_remaining=900)
    assert result["approval_disposition"] == "live"


# -- the evidence object itself -----------------------------------------
def test_dispatcher_supplies_every_external_gate() -> None:
    """No external-evidence gate may be left to the permissive fallback."""
    state = State({"state_dir": tempfile.mkdtemp()})
    try:
        jid = seed_job(state, number=610, head="h610")
        seed_evidence(state, jid)
        verdicts = [_clean_verdict("opus", "anthropic"), _clean_verdict("ds", "openrouter")]
        evidence = dispatcher._approval_evidence(
            _config("live"), state,
            {"job_id": jid, "repo": "o/r", "number": 610}, "h610",
            verdicts=verdicts, required_slots=2,
        )
        for field in ("bounded_change", "audit_writable", "assurance_met",
                      "revalidation_ok", "rate_limit_ok"):
            assert getattr(evidence, field) is not None, (
                f"{field} must be supplied explicitly, never left to the fallback"
            )
        assert evidence.required_reviewers == 2
        assert evidence.completed_reviewers == 2
    finally:
        state.close()


def test_stale_observed_head_fails_the_precheck() -> None:
    state = State({"state_dir": tempfile.mkdtemp()})
    try:
        jid = seed_job(state, number=611, head="h611")
        seed_evidence(state, jid)
        row = state.db.execute(
            "SELECT payload FROM prs WHERE repo='o/r' AND number=611"
        ).fetchone()
        payload = json.loads(row["payload"])
        payload["head"] = {"sha": "MOVED"}
        state.db.execute("UPDATE prs SET payload=? WHERE repo='o/r' AND number=611",
                         (json.dumps(payload),))
        state.db.commit()

        evidence = dispatcher._approval_evidence(
            _config("live"), state,
            {"job_id": jid, "repo": "o/r", "number": 611}, "h611",
            verdicts=[], required_slots=2,
        )
        assert evidence.revalidation_ok is False
    finally:
        state.close()


def test_missing_pr_payload_is_not_a_bounded_change() -> None:
    """With no observed diff we cannot assert the change is small."""
    state = State({"state_dir": tempfile.mkdtemp()})
    try:
        jid = seed_job(state, number=612, head="h612")
        seed_evidence(state, jid)
        state.db.execute("DELETE FROM prs WHERE repo='o/r' AND number=612")
        state.db.commit()

        evidence = dispatcher._approval_evidence(
            _config("live"), state,
            {"job_id": jid, "repo": "o/r", "number": 612}, "h612",
            verdicts=[], required_slots=2,
        )
        assert evidence.bounded_change is False
        assert evidence.revalidation_ok is False
    finally:
        state.close()
