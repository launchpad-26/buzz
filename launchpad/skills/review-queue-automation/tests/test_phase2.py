#!/usr/bin/env python3
"""Phase 2 tests: lifecycle transitions, request-changes gate + mutation, and
human-queue execution states. Deterministic fakes only; no GitHub, no models."""

from __future__ import annotations

import json
import pathlib
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scripts"))

from action_gate import approve_gate, request_changes_gate, Gate  # noqa: E402
from approval import RequestQueueError, set_execution_state  # noqa: E402
from common import State, job_id  # noqa: E402
from risk import AssuranceEvaluation, compute_assurance  # noqa: E402


def fresh_state() -> State:
    return State({"state_dir": tempfile.mkdtemp()})


def _cfg(**authority) -> dict:
    return {
        "login": "me",
        "authority": authority or {
            "approve": "live", "request_changes": "live", "comment": "live",
        },
    }


def _assurance_ok(**kw) -> AssuranceEvaluation:
    return compute_assurance(
        required_rpn=20, evidence_completeness=1.0, fresh=True,
        achieved_slots=2, required_slots=2, **kw,
    )


# ---- request-changes gate: separate live authority + verified blocker ---------
def test_approve_and_rc_gates_are_independent() -> None:
    # approve live but request_changes disabled => approve gate path only
    cfg = _cfg(approve="live", request_changes="disabled", comment="live")
    pr = {"draft": False, "head": "H"}
    # request-changes must be denied when its own authority is disabled
    g = request_changes_gate(
        cfg=cfg, repo="o/r", head_sha="H", pr=pr, verified_blocker=True,
        blocker_evidence_sufficient=True, assurance=_assurance_ok(),
        revalidate=lambda: True,
    )
    assert not g.allowed and "authority" in g.failed
    # approve still independent
    g2 = approve_gate(
        cfg=cfg, repo="o/r", head_sha="H", pr=pr, reviewers_complete=True,
        no_self_approval=True, blockers=[], high_findings=[],
        assurance=_assurance_ok(), policy_permits=True, decision_usable=True,
        idempotency_key_unused=True, revalidate=lambda: True,
    )
    assert g2.allowed


def test_rc_rejects_no_verified_blocker() -> None:
    g = request_changes_gate(
        cfg=_cfg(), repo="o/r", head_sha="H", pr={"draft": False, "head": "H"},
        verified_blocker=False, blocker_evidence_sufficient=True,
        assurance=_assurance_ok(), revalidate=lambda: True,
    )
    assert not g.allowed
    assert "verified_blocker" in g.failed


def test_rc_requires_sufficient_blocker_evidence() -> None:
    g = request_changes_gate(
        cfg=_cfg(), repo="o/r", head_sha="H", pr={"draft": False, "head": "H"},
        verified_blocker=True, blocker_evidence_sufficient=False,
        assurance=_assurance_ok(), revalidate=lambda: True,
    )
    assert not g.allowed and "blocker_evidence" in g.failed


def test_rc_rejects_stale_head() -> None:
    g = request_changes_gate(
        cfg=_cfg(), repo="o/r", head_sha="NEWH", pr={"draft": False, "head": "OLDH"},
        verified_blocker=True, blocker_evidence_sufficient=True,
        assurance=_assurance_ok(), revalidate=lambda: True,
    )
    assert not g.allowed and "exact_head" in g.failed


def test_final_revalidation_not_hardcoded() -> None:
    # revalidate returns False => denied (never hardcoded to success)
    g = request_changes_gate(
        cfg=_cfg(), repo="o/r", head_sha="H", pr={"draft": False, "head": "H"},
        verified_blocker=True, blocker_evidence_sufficient=True,
        assurance=_assurance_ok(), revalidate=lambda: False,
    )
    assert not g.allowed and "final_revalidation" in g.failed
    a = approve_gate(
        cfg=_cfg(), repo="o/r", head_sha="H", pr={"draft": False, "head": "H"},
        reviewers_complete=True, no_self_approval=True, blockers=[], high_findings=[],
        assurance=_assurance_ok(), policy_permits=True, decision_usable=True,
        idempotency_key_unused=True, revalidate=None,
    )
    assert not a.allowed and "final_revalidation" in a.failed


def test_rc_allows_verified_blocker() -> None:
    cfg = _cfg(approve="live", request_changes="live", comment="live")
    g = request_changes_gate(
        cfg=cfg, repo="o/r", head_sha="H", pr={"draft": False, "head": "H"},
        verified_blocker=True, blocker_evidence_sufficient=True,
        assurance=_assurance_ok(), revalidate=lambda: True,
    )
    assert g.allowed


# ---- request-changes mutation --------------------------------------------------
def test_request_changes_mutation_event_is_fixed() -> None:
    import github_mutate

    assert github_mutate.fixed_event_of("request_changes_review") == "CHANGES_REQUESTED"
    assert not github_mutate.requires_approval_record("request_changes_review")


def test_request_changes_mutation_fake() -> None:
    import github_mutate

    state = fresh_state()
    try:
        calls = {}

        def fake_post(token, payload, *, timeout=60):
            calls["payload"] = payload
            return 200, {"data": {"addPullRequestReview": {"pullRequestReview": {"id": "R"}}}}

        data = github_mutate.execute_request_changes(
            state, {"pullRequestId": "PR1", "body": "blocking"}, "job",
            http_post=fake_post,
        )
        assert "CHANGES_REQUESTED" in github_mutate._REQUEST_CHANGES_QUERY
        assert calls["payload"]
    finally:
        state.close()


# ---- lifecycle transitions -------------------------------------------------------
def test_lifecycle_transitions_valid() -> None:
    from states import can_transition

    assert can_transition("detected", "ready_for_review")
    assert can_transition("ready_for_review", "assurance")
    assert can_transition("changes_requested", "requested_changes_fixed")
    assert can_transition("requested_changes_fixed", "assurance")
    assert can_transition("author_triage", "changes_requested")
    assert can_transition("detected", "author_triage")
    assert can_transition("detected", "closed")
    assert can_transition("detected", "merged")


def test_invalid_transitions_rejected() -> None:
    from states import can_transition

    # cannot jump from detected straight to approval
    assert not can_transition("detected", "approval_evaluation")
    assert not can_transition("detected", "completed_auto_approved")
    assert not can_transition("merged", "detected")
    assert not can_transition("changes_requested", "approve_gate")


# ---- human-queue execution states -----------------------------------------------
def test_set_execution_state() -> None:
    from approval import enqueue

    state = fresh_state()
    try:
        req = enqueue(state, repo="o/r", number=1, head_sha="H", policy={},
                      summary="s", assurance={}, reviewers=[], risk_score=1,
                      risk_band="low", protected=[], failed_gates=[], ci={},
                      findings=[], recommendation="approve", rationale="r",
                      action="approve", job_id="job1")
        set_execution_state(state, req["request_id"], "execution_pending")
        assert state.db.execute("SELECT state FROM human_requests WHERE request_id=?",
                                (req["request_id"],)).fetchone()[0] == "execution_pending"
        set_execution_state(state, req["request_id"], "executed")
        assert state.db.execute("SELECT state FROM human_requests WHERE request_id=?",
                                (req["request_id"],)).fetchone()[0] == "executed"
    finally:
        state.close()


def test_set_execution_state_rejects_unknown() -> None:
    from approval import enqueue

    state = fresh_state()
    try:
        req = enqueue(state, repo="o/r", number=1, head_sha="H", policy={},
                      summary="s", assurance={}, reviewers=[], risk_score=1,
                      risk_band="low", protected=[], failed_gates=[], ci={},
                      findings=[], recommendation="approve", rationale="r",
                      action="approve", job_id="job1")
        try:
            set_execution_state(state, req["request_id"], "definitely-done")
            raise AssertionError("unknown execution state must be rejected")
        except RequestQueueError:
            pass
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