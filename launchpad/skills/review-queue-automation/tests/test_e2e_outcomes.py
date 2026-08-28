#!/usr/bin/env python3
"""End-to-end outcome matrix with every external effect intercepted.

This is the safety net before any live canary. For each terminal outcome it
asserts three things:

  1. the outcome is REACHABLE through the real dispatcher (not a unit stub);
  2. exactly the intended GitHub mutations were attempted, and no others;
  3. the ledger can explain the result, and the review lease was released.

Property (2) is the important one: a pipeline that reaches the right state while
quietly posting the wrong thing is worse than one that fails.
"""

from __future__ import annotations

import json
import pathlib
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scripts"))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import advisory  # noqa: E402
import approval_action  # noqa: E402
import dispatcher  # noqa: E402
from common import State, utcnow  # noqa: E402
from ledger import explain  # noqa: E402
from test_dispatch_flow import (  # noqa: E402
    _clean_verdict,
    _config,
    fake_panel,
    patch_dispatcher,
    restore_dispatcher,
    seed_evidence,
    seed_job,
    seed_verdicts,
)

LIVE_RC = {"request_changes": "live"}


def _defect(model: str, family: str, location: str = "src/a.py:12") -> dict:
    return {
        "signal": "DEFECTS_FOUND", "recommendation": "findings", "summary": "defect",
        "findings": [{"severity": "blocker", "title": "auth bypass",
                      "location": location, "evidence": "expired sessions refresh",
                      "primary_source": "src/a.py"}],
        "good": [], "missing_evidence": [],
        "model": model, "provider_family": family,
    }


class Harness:
    """Drives one job with every GitHub effect recorded rather than performed."""

    def __init__(self):
        self.mutations: list[str] = []
        self.lease_claims: list = []
        self.lease_releases: list = []

    def run(
        self,
        *,
        number: int,
        mode: str = "disabled",
        authority: dict | None = None,
        verdicts: list[dict] | None = None,
        signals="SUPPORTED",
        panel_complete: bool = True,
        approve_result=(True, "approved", "approved"),
        rc_raises: Exception | None = None,
        node_id: str = "PR_node",
        canary: bool = True,
        lease_claimed: bool = True,
    ) -> tuple[dict, str, State]:
        state = State({"state_dir": tempfile.mkdtemp()})

        def rc_execute(state_, variables, job, **kwargs):
            if rc_raises:
                raise rc_raises
            self.mutations.append("request_changes_review")
            return {}

        def fake_advisory(state_, **kwargs):
            self.mutations.append("add_comment_review")
            return {"posted": True, "mode": "live"}

        def fake_approve(state_, **kwargs):
            self.mutations.append("approve_review")
            return approve_result

        saved = patch_dispatcher(
            run_panel=fake_panel(signals, complete=panel_complete),
            _rc_execute=rc_execute,
            _rc_transport=lambda c, s, r, n: ((lambda h: (lambda: True)), (lambda: [])),
            _lease_claim=lambda *a, **k: (self.lease_claims.append(a) or lease_claimed),
            _lease_release=lambda *a, **k: self.lease_releases.append(a),
        )
        original_advisory = advisory.post_advisory
        original_approve = approval_action.approve
        advisory.post_advisory = fake_advisory
        approval_action.approve = fake_approve
        try:
            cfg = _config(mode)
            cfg["authority"] = {"comment": "live", **(authority or {})}
            if not canary:
                cfg["dispatch"] = {"incoming_canary_approved": False,
                                   "author_canary_approved": False}

            jid = seed_job(state, number=number, head=f"h{number}")
            seed_evidence(state, jid)
            seed_verdicts(state, jid, verdicts or [
                _clean_verdict("opus", "anthropic"), _clean_verdict("ds", "openrouter")])

            if not node_id:
                row = state.db.execute(
                    "SELECT payload FROM prs WHERE repo='o/r' AND number=?", (number,)
                ).fetchone()
                payload = json.loads(row["payload"])
                payload.pop("node_id", None)
                state.db.execute("UPDATE prs SET payload=? WHERE repo='o/r' AND number=?",
                                 (json.dumps(payload), number))
                state.db.commit()

            result = dispatcher.run_job(
                cfg,
                {"job_id": jid, "repo": "o/r", "number": number, "lane": "incoming_review"},
                state=state,
            )
            return result, jid, state
        finally:
            advisory.post_advisory = original_advisory
            approval_action.approve = original_approve
            restore_dispatcher(saved)


# -- terminal outcomes ---------------------------------------------------
def test_completed_auto_approved() -> None:
    h = Harness()
    result, jid, state = h.run(number=900, mode="live", authority={"approve": "live"})
    try:
        assert state.current_status(jid) == "completed_auto_approved", result
        assert h.mutations == ["approve_review"], h.mutations
        assert explain(state, jid)["final_action"]["operation"] == "approve_review"
        assert len(h.lease_releases) == 1
    finally:
        state.close()


def test_completed_advisory() -> None:
    h = Harness()
    result, jid, state = h.run(number=901, mode="disabled")
    try:
        assert state.current_status(jid) == "completed_advisory", result
        assert h.mutations == ["add_comment_review"], h.mutations
        assert len(h.lease_releases) == 1
    finally:
        state.close()


def test_shadow_mode_posts_advisory_and_never_approves() -> None:
    h = Harness()
    result, jid, state = h.run(number=902, mode="shadow")
    try:
        assert state.current_status(jid) == "completed_advisory", result
        assert "approve_review" not in h.mutations, "shadow must never approve"
        assert h.mutations == ["add_comment_review"]
    finally:
        state.close()


def test_changes_requested() -> None:
    h = Harness()
    result, jid, state = h.run(
        number=903, mode="live", authority=LIVE_RC, signals=["DEFECTS_FOUND"] * 2,
        verdicts=[_defect("opus", "anthropic"), _defect("ds", "openrouter")],
    )
    try:
        assert state.current_status(jid) == "changes_requested", result
        assert h.mutations == ["request_changes_review"], h.mutations
        assert "approve_review" not in h.mutations
        assert len(h.lease_releases) == 1
    finally:
        state.close()


def test_human_required_for_uncorroborated_defect() -> None:
    h = Harness()
    result, jid, state = h.run(
        number=904, mode="live", authority=LIVE_RC, signals=["DEFECTS_FOUND"],
        verdicts=[_defect("opus", "anthropic")],
    )
    try:
        assert state.current_status(jid) == "human_required", result
        assert h.mutations == [], "an uncorroborated defect must mutate nothing"
        assert len(h.lease_releases) == 1
    finally:
        state.close()


def test_human_approval_pending_in_escalation_mode() -> None:
    h = Harness()
    result, jid, state = h.run(number=905, mode="human_escalation")
    try:
        assert state.current_status(jid) == "human_approval_pending", result
        assert h.mutations == [], "escalation must not act on GitHub"
        row = state.db.execute(
            "SELECT job_id FROM human_requests WHERE state='pending'"
        ).fetchone()
        assert row and row["job_id"] == jid
        assert len(h.lease_releases) == 1
    finally:
        state.close()


def test_safe_stop_on_uncertain_approval() -> None:
    h = Harness()
    result, jid, state = h.run(
        number=906, mode="live", authority={"approve": "live"},
        approve_result=(False, "uncertain", "cannot confirm"),
    )
    try:
        assert state.current_status(jid) == "safe_stop", result
        assert h.mutations == ["approve_review"]
        assert len(h.lease_releases) == 1
    finally:
        state.close()


def test_safe_stop_on_missing_node_id() -> None:
    h = Harness()
    result, jid, state = h.run(
        number=907, mode="live", authority={"approve": "live"}, node_id="",
    )
    try:
        assert state.current_status(jid) == "safe_stop", result
        assert h.mutations == [], "no mutation without a PR node id"
    finally:
        state.close()


def test_safe_stop_on_request_changes_mutation_failure() -> None:
    h = Harness()
    result, jid, state = h.run(
        number=908, mode="live", authority=LIVE_RC, signals=["DEFECTS_FOUND"] * 2,
        verdicts=[_defect("opus", "anthropic"), _defect("ds", "openrouter")],
        rc_raises=RuntimeError("graphql 500"),
    )
    try:
        assert state.current_status(jid) == "safe_stop", result
        assert h.mutations == [], "a failed mutation records no success"
        assert len(h.lease_releases) == 1
    finally:
        state.close()


def test_degraded_draft_on_partial_panel() -> None:
    h = Harness()
    result, jid, state = h.run(number=909, mode="live", authority={"approve": "live"},
                               panel_complete=False)
    try:
        assert state.current_status(jid) == "degraded_draft", result
        assert h.mutations == [], "a partial panel must mutate nothing"
        assert len(h.lease_releases) == 1
    finally:
        state.close()


def test_gated_when_canary_not_approved() -> None:
    h = Harness()
    result, jid, state = h.run(number=910, mode="live", authority={"approve": "live"},
                               canary=False)
    try:
        assert result["status"] == "gated", result
        assert "canary not approved" in result["reason"]
        assert h.mutations == []
        assert h.lease_claims == [], "gating precedes the lease claim"
    finally:
        state.close()


def test_gated_when_lease_is_held_elsewhere() -> None:
    h = Harness()
    result, _jid, state = h.run(number=911, mode="live", authority={"approve": "live"},
                                lease_claimed=False)
    try:
        assert result["status"] == "gated", result
        assert "claimed by another reviewer" in result["reason"]
        assert h.mutations == []
        assert h.lease_releases == [], "we never held it"
    finally:
        state.close()


# -- cross-cutting invariants -------------------------------------------
def test_every_outcome_releases_the_lease_it_took() -> None:
    """A retained lease blocks the queue forever."""
    cases = [
        dict(number=920, mode="live", authority={"approve": "live"}),
        dict(number=921, mode="disabled"),
        dict(number=922, mode="human_escalation"),
        dict(number=923, mode="live", authority={"approve": "live"},
             approve_result=(False, "uncertain", "x")),
        dict(number=924, mode="live", authority={"approve": "live"},
             panel_complete=False),
    ]
    for case in cases:
        h = Harness()
        _result, _jid, state = h.run(**case)
        try:
            assert len(h.lease_claims) == 1, case
            assert len(h.lease_releases) == 1, case
        finally:
            state.close()


def test_no_outcome_approves_without_live_approve_authority() -> None:
    """The conjunctive authority rule holds across every mode."""
    for mode in ("disabled", "shadow", "human_escalation", "live"):
        h = Harness()
        _result, _jid, state = h.run(number=930 + len(mode), mode=mode,
                                     authority={"approve": "disabled"})
        try:
            assert "approve_review" not in h.mutations, mode
        finally:
            state.close()


def test_every_outcome_is_explainable() -> None:
    cases = [
        dict(number=940, mode="live", authority={"approve": "live"}),
        dict(number=941, mode="disabled"),
        dict(number=942, mode="live", authority=LIVE_RC,
             signals=["DEFECTS_FOUND"] * 2,
             verdicts=[_defect("opus", "anthropic"), _defect("ds", "openrouter")]),
    ]
    for case in cases:
        h = Harness()
        _result, jid, state = h.run(**case)
        try:
            report = explain(state, jid)
            assert report["explained"] is True, case
            assert report["final_decision"] is not None, case
        finally:
            state.close()
