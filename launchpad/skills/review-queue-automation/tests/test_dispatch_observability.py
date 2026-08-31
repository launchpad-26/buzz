#!/usr/bin/env python3
"""Orchestrator trace tests (T26).

`JobLogger` was constructed by the dispatcher and never called on: a job left no
orchestrator-emitted trace at all, only whatever `common.State.transition`
happened to log. These tests read the JSONL back with
`logging_otel.read_events` and assert that one faked end-to-end dispatch
explains every state change and every external action.

They are written to FAIL if any required event is dropped, so removing an
emission is a test failure rather than a silent hole in the audit trail.
"""

from __future__ import annotations

import collections
import datetime as dt
import json
import pathlib
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scripts"))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import dispatcher  # noqa: E402
from common import State, job_id as make_job_id  # noqa: E402
from config import policy_defaults  # noqa: E402
from logging_otel import JOB_EVENTS, REQUIRED_JOB_EVENTS, read_events  # noqa: E402
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


def _traced_config(mode: str = "live") -> tuple[dict, str]:
    """A config whose logging directory is a fresh temp dir, with a real policy."""
    log_dir = tempfile.mkdtemp()
    cfg = _config(mode)
    cfg["state_dir"] = tempfile.mkdtemp()
    cfg["logging"] = {"directory": log_dir, "format": "otel-jsonl"}
    cfg["policy"] = policy_defaults(cfg)
    return cfg, log_dir


def _events(log_dir: str, job: str) -> list[dict]:
    return read_events(pathlib.Path(log_dir) / "jobs" / job / "events.jsonl")


def _ledger_panel(state: State, job: str, repo: str, number: int, head: str) -> None:
    """Write the ledger rows the REAL panel writes, so the planner/route events
    have the same material to read back that production gives them."""
    from ledger import record

    record(state, job_id=job, repo=repo, number=number, head_sha=head,
           kind="strategy", entry_key="review_plan",
           payload={"name": "review_plan", "activities": ["verify_evidence"],
                    "focus": ["docs/a.md"], "is_rereview": False})
    record(state, job_id=job, repo=repo, number=number, head_sha=head,
           kind="route", entry_key="claude:opus",
           payload={"slot": "review-A.txt", "provider_family": "anthropic",
                    "capability": "frontier", "effort_enforced": True,
                    "qualified_route": {"effort_enforced": True}})


def _dispatch_traced(number: int = 700, mode: str = "live") -> tuple[dict, list[dict], State]:
    cfg, log_dir = _traced_config(mode)
    state = State({"state_dir": cfg["state_dir"]})
    jid = seed_job(state, number=number, head=f"h{number}")
    seed_evidence(state, jid)
    seed_verdicts(state, jid, [_clean_verdict("opus", "anthropic"),
                               _clean_verdict("gpt", "openai")])
    _ledger_panel(state, jid, "o/r", number, f"h{number}")

    saved = patch_dispatcher(run_panel=fake_panel("SUPPORTED"))
    previous = patch_approval(fake_approve(True, "approved"))
    try:
        result = dispatcher.run_job(
            cfg, {"job_id": jid, "repo": "o/r", "number": number, "lane": "incoming_review"},
            state=state,
        )
    finally:
        restore_approval(previous)
        restore_dispatcher(saved)
    return result, _events(log_dir, jid), state


# -- the required event set -------------------------------------------------
def test_end_to_end_dispatch_emits_every_required_event() -> None:
    result, events, state = _dispatch_traced(700)
    try:
        assert result["status"] == "completed_auto_approved", result
        emitted = {event["event_name"] for event in events}
        missing = sorted(REQUIRED_JOB_EVENTS - emitted)
        assert not missing, f"orchestrator dropped required events: {missing}"
        # the approval branch must also record the external action it performed
        assert "mutation" in emitted
        assert "lease_acquired" in emitted and "lease_released" in emitted
    finally:
        state.close()


def test_a_dropped_event_fails_the_trace_check() -> None:
    """The guard itself must be able to fail: removing one event is detected."""
    _result, events, state = _dispatch_traced(701)
    try:
        emitted = {event["event_name"] for event in events}
        assert REQUIRED_JOB_EVENTS <= emitted
        for dropped in sorted(REQUIRED_JOB_EVENTS):
            reduced = emitted - {dropped}
            assert not REQUIRED_JOB_EVENTS <= reduced, (
                f"the check would still pass without {dropped}; it proves nothing"
            )
    finally:
        state.close()


def test_every_emitted_event_name_is_registered() -> None:
    """No free-form event names: a trace consumer keys off the registry."""
    _result, events, state = _dispatch_traced(702)
    try:
        known = set(JOB_EVENTS) | {"info", "warning", "error", "review_automation",
                                   "panel_attempt"}
        unknown = {e["event_name"] for e in events} - known
        assert not unknown, f"unregistered event names emitted: {sorted(unknown)}"
    finally:
        state.close()


# -- the trace actually explains the job ------------------------------------
def test_trace_explains_decision_route_and_plan() -> None:
    _result, events, state = _dispatch_traced(703)
    try:
        by_name = collections.defaultdict(list)
        for event in events:
            by_name[event["event_name"]].append(event)

        decision = by_name["decision"][-1]["attributes"]
        assert decision["decision.disposition"] == "live"

        planner = by_name["planner"][0]["attributes"]
        assert planner["planner.activities"] == ["verify_evidence"], planner

        route = by_name["route_selection"][0]["attributes"]
        assert route["route.key"] == "claude:opus"
        assert route["route.provider_family"] == "anthropic"

        verify = [e["attributes"] for e in by_name["verify"]]
        assert any(v["verify.ok"] for v in verify), verify

        mutation = by_name["mutation"][-1]["attributes"]
        assert mutation["mutation.operation"] == "approve_review"
        assert mutation["mutation.verified"] is True
    finally:
        state.close()


def test_cost_and_latency_attributes_are_present_and_bounded() -> None:
    """Bounded cost/token/latency numbers must survive into the trace.

    They previously did not: `_is_sensitive_key` matches "token" as a substring,
    so a legitimate token COUNT was written as "<redacted>".
    """
    _result, events, state = _dispatch_traced(704)
    try:
        budget_event = [e for e in events if e["event_name"] == "budget"][0]
        attrs = budget_event["attributes"]
        assert isinstance(attrs["cost.tokens_reserved"], int)
        assert 0 < attrs["cost.tokens_reserved"] <= 1_000_000_000
        assert attrs["cost.tokens_reserved"] != "<redacted>"
        assert isinstance(attrs["budget.headroom.per_pr"], int)

        strategy = [e for e in events if e["event_name"] == "strategy"][0]["attributes"]
        assert isinstance(strategy["latency.ms"], int) and strategy["latency.ms"] >= 0
        assert isinstance(strategy["cost.tokens"], int)
    finally:
        state.close()


def test_rereview_is_emitted_only_when_a_prior_revision_exists() -> None:
    cfg, log_dir = _traced_config()
    state = State({"state_dir": cfg["state_dir"]})
    try:
        jid = seed_job(state, number=705, head="h705")
        seed_evidence(state, jid)
        seed_verdicts(state, jid, [_clean_verdict("opus", "anthropic"),
                                   _clean_verdict("gpt", "openai")])
        now = dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")
        older = make_job_id("o/r", 705, "old705", "incoming_review")
        state.db.execute(
            "INSERT INTO jobs(id,repo,number,head_sha,lane,status,artifact_dir,created_at,updated_at)"
            " VALUES(?,?,?,?,?,?,?,?,?)",
            (older, "o/r", 705, "old705", "incoming_review", "superseded",
             str(state.job_dir(older)), now, now),
        )
        state.db.commit()

        saved = patch_dispatcher(run_panel=fake_panel("SUPPORTED"))
        previous = patch_approval(fake_approve(True, "approved"))
        try:
            dispatcher.run_job(
                cfg, {"job_id": jid, "repo": "o/r", "number": 705, "lane": "incoming_review"},
                state=state,
            )
        finally:
            restore_approval(previous)
            restore_dispatcher(saved)

        rereview = [e for e in _events(log_dir, jid) if e["event_name"] == "rereview"]
        assert len(rereview) == 1
        assert rereview[0]["attributes"]["review.prior_revisions"] == 1
    finally:
        state.close()


# -- redaction survives the new emissions -----------------------------------
def test_no_credential_material_reaches_the_trace() -> None:
    """Redaction must hold across every event the orchestrator now emits."""
    cfg, log_dir = _traced_config()
    state = State({"state_dir": cfg["state_dir"]})
    jid = seed_job(state, number=706, head="h706")
    seed_evidence(state, jid)
    seed_verdicts(state, jid, [_clean_verdict("opus", "anthropic"),
                               _clean_verdict("gpt", "openai")])
    jwt = "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxIn0.c2lnbmF0dXJlSGVyZQ"
    token = "ghp_" + "A" * 36

    def hostile_panel(cfg_, state_, repo, number, lane, job, profile, logger=None):
        # A panel result carrying credential-shaped material, as a compromised or
        # merely careless runner could produce.
        return {
            "profile": profile, "required_reviewers": 2,
            "completed_reviewers": [token, jwt], "complete": True,
            "signals": ["SUPPORTED", "SUPPORTED"], "outcome": "complete",
            "strategy": f"direct_analysis authorization: Bearer {token}",
            "recipe": "preferred", "roles": ["reviewer", "adversary"],
            "budget_tokens": 1000, "disagreement": False,
            "disagreement_handling": "",
        }

    saved = patch_dispatcher(run_panel=hostile_panel)
    previous = patch_approval(fake_approve(True, "approved"))
    try:
        dispatcher.run_job(
            cfg, {"job_id": jid, "repo": "o/r", "number": 706, "lane": "incoming_review"},
            state=state,
        )
    finally:
        restore_approval(previous)
        restore_dispatcher(saved)
        state.close()

    blob = json.dumps(_events(log_dir, jid))
    assert token not in blob, "a token-shaped value reached the trace"
    assert jwt not in blob, "a JWT-shaped value reached the trace"
    assert "<redacted" in blob
