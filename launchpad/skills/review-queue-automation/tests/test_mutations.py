#!/usr/bin/env python3
"""Fakes/tempfile tests for github_mutate.py — mutation authority + lifecycle.

Covers: generic entry point cannot approve, fixed events, forged-decision
rejection (repo/PR/head/policy/status/expiry), SQLite decision-by-id loading,
mandatory REST revalidation before mutation, mandatory REST verification after
mutation, and the pending -> verified|failed|uncertain lifecycle (uncertain never
blindly retried).
"""

from __future__ import annotations

import datetime as dt
import pathlib
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scripts"))

from common import State  # noqa: E402
from errors import DecisionStaleError, MutationUncertainError  # noqa: E402
from github_mutate import (  # noqa: E402
    ApprovalRecordRequiredError,
    PermissionAuthorityError,
    execute_approval,
    fixed_event_of,
    post,
    _APPROVE_QUERY,
    _COMMENT_QUERY,
)


def fresh_state() -> State:
    return State({"state_dir": tempfile.mkdtemp()})


def _future_expiry(minutes: int = 120) -> str:
    ts = dt.datetime.now(dt.timezone.utc) + dt.timedelta(minutes=minutes)
    return ts.isoformat().replace("+00:00", "Z")


def _seed_decision(state: State, *, status="eligible", expires_at=None,
                   repo="o/r", number=1, head_sha="HEAD1", policy_hash="PH1") -> str:
    decision_id = "dc0102030405"
    if expires_at is None:
        expires_at = _future_expiry()
    state.db.execute(
        "INSERT INTO approval_decisions(id,repo,number,head_sha,policy_hash,status,mode,risk_score,created_at,expires_at) "
        "VALUES(?,?,?,?,?,?,?,?,?,?)",
        (decision_id, repo, number, head_sha, policy_hash, status, "live", 5, "2026-01-01T00:00:00Z", expires_at),
    )
    state.db.commit()
    return decision_id


def _ok_post(token, payload, *, timeout=60):
    return 200, {"data": {"addPullRequestReview": {"pullRequestReview": {"id": "R1"}}}}


def _good_revalidate() -> dict:
    return {"head_matches": True, "pr_open_not_draft": True,
            "no_protected_trigger": True, "author_not_identity": True}


def test_generic_post_cannot_approve() -> None:
    state = fresh_state()
    try:
        calls = []

        def fake(token, payload, *, timeout=60):
            calls.append(payload)
            return 200, {"data": {}}

        try:
            post(state, "approve_review", {"pullRequestId": "PR_1"}, "job1", http_post=fake)
            raise AssertionError("generic post must refuse approve_review")
        except ApprovalRecordRequiredError:
            pass
        assert calls == [], "generic approve must never reach the network"
    finally:
        state.close()


def test_fixed_events_are_never_caller_supplied() -> None:
    assert fixed_event_of("add_comment_review") == "COMMENT"
    assert fixed_event_of("approve_review") == "APPROVE"
    assert "event:COMMENT" in _COMMENT_QUERY
    assert "event:APPROVE" in _APPROVE_QUERY


def test_forged_repo_or_pr_rejected() -> None:
    state = fresh_state()
    try:
        decision_id = _seed_decision(state)
        for repo, number in ((("o/other"), 1), (("o/r"), 7)):
            try:
                execute_approval(state, {}, {}, "job1", decision_id=decision_id,
                                 repo=repo, number=number,
                                 current_head_sha="HEAD1", current_policy_hash="PH1")
                raise AssertionError("repo/PR mismatch must be rejected")
            except ApprovalRecordRequiredError:
                pass
    finally:
        state.close()


def test_forged_head_and_policy_rejected() -> None:
    state = fresh_state()
    try:
        decision_id = _seed_decision(state)
        try:
            execute_approval(state, {}, {}, "job1", decision_id=decision_id,
                             repo="o/r", number=1,
                             current_head_sha="FORGED", current_policy_hash="PH1")
            raise AssertionError("stale head must be rejected")
        except DecisionStaleError:
            pass
        try:
            execute_approval(state, {}, {}, "job1", decision_id=decision_id,
                             repo="o/r", number=1,
                             current_head_sha="HEAD1", current_policy_hash="FORGED")
            raise AssertionError("stale policy hash must be rejected")
        except DecisionStaleError:
            pass
    finally:
        state.close()


def test_not_eligible_status_rejected() -> None:
    state = fresh_state()
    try:
        decision_id = _seed_decision(state, status="revoked")
        try:
            execute_approval(state, {}, {}, "job1", decision_id=decision_id,
                             repo="o/r", number=1,
                             current_head_sha="HEAD1", current_policy_hash="PH1")
            raise AssertionError("non-eligible status must be rejected")
        except ApprovalRecordRequiredError:
            pass
    finally:
        state.close()


def test_expired_decision_rejected() -> None:
    state = fresh_state()
    try:
        decision_id = _seed_decision(state, expires_at="2000-01-01T00:00:00Z")
        try:
            execute_approval(state, {}, {}, "job1", decision_id=decision_id,
                             repo="o/r", number=1,
                             current_head_sha="HEAD1", current_policy_hash="PH1")
            raise AssertionError("expired decision must be rejected")
        except DecisionStaleError:
            pass
    finally:
        state.close()


def test_approval_loads_eligible_decision_by_id_from_sqlite() -> None:
    state = fresh_state()
    try:
        decision_id = _seed_decision(state)
        sent = {}

        def fake(token, payload, *, timeout=60):
            sent["payload"] = payload
            return 200, {"data": {"addPullRequestReview": {"pullRequestReview": {"id": "R1"}}}}

        # Caller JSON (`decision` dict) is forged and ignored; the DB row authorizes.
        data = execute_approval(
            state, {"repo": "FORGED", "number": 999}, {"pullRequestId": "PR_1"}, "job1",
            decision_id=decision_id, repo="o/r", number=1,
            current_head_sha="HEAD1", current_policy_hash="PH1",
            http_post=fake,
            rest_before=_good_revalidate,
            rest_after=lambda: "verified",
        )
        assert data["addPullRequestReview"]["pullRequestReview"]["id"] == "R1"
        assert "event:APPROVE" in sent["payload"]
        statuses = [r["status"] for r in state.db.execute(
            "SELECT status FROM mutations WHERE operation='approve_review'").fetchall()]
        assert "verified" in statuses, statuses
    finally:
        state.close()


def test_mandatory_revalidation_before_mutation() -> None:
    state = fresh_state()
    try:
        decision_id = _seed_decision(state)
        sent = []

        def fake(token, payload, *, timeout=60):
            sent.append(payload)
            return 200, {"data": {"addPullRequestReview": {"pullRequestReview": {"id": "R1"}}}}

        # No rest_before -> refused BEFORE any mutation.
        try:
            execute_approval(state, {}, {"pullRequestId": "PR_1"}, "job1",
                             decision_id=decision_id, repo="o/r", number=1,
                             current_head_sha="HEAD1", current_policy_hash="PH1",
                             http_post=fake, rest_after=lambda: "verified")
            raise AssertionError("approval without revalidation must be refused")
        except PermissionAuthorityError:
            pass
        assert sent == [], "no mutation may occur without revalidation"
    finally:
        state.close()


def test_revalidation_failure_blocks_mutation() -> None:
    state = fresh_state()
    try:
        decision_id = _seed_decision(state)
        sent = []

        def fake(token, payload, *, timeout=60):
            sent.append(payload)
            return 200, {"data": {"addPullRequestReview": {"pullRequestReview": {"id": "R1"}}}}

        try:
            execute_approval(state, {}, {"pullRequestId": "PR_1"}, "job1",
                             decision_id=decision_id, repo="o/r", number=1,
                             current_head_sha="HEAD1", current_policy_hash="PH1",
                             http_post=fake, rest_after=lambda: "verified",
                             rest_before=lambda: {"head_matches": False})
            raise AssertionError("failing revalidation must block the mutation")
        except PermissionAuthorityError:
            pass
        assert sent == [], "no mutation on failed revalidation"
    finally:
        state.close()


def _uncertain_kwargs(state, decision_id, sent):
    def fake(token, payload, *, timeout=60):
        sent.append(payload)
        return 200, {"data": {"addPullRequestReview": {"pullRequestReview": {"id": "R1"}}}}

    return dict(state=state, decision={}, variables={"pullRequestId": "PR_1"}, job="jobU",
                decision_id=decision_id, repo="o/r", number=1,
                current_head_sha="HEAD1", current_policy_hash="PH1",
                http_post=fake, rest_before=_good_revalidate,
                rest_after=lambda: "uncertain")


def test_mandatory_verification_uncertain_persists_and_no_retry() -> None:
    state = fresh_state()
    try:
        decision_id = _seed_decision(state)
        sent = []

        args = _uncertain_kwargs(state, decision_id, sent)

        try:
            execute_approval(**args)
            raise AssertionError("uncertain verification must raise MutationUncertain")
        except MutationUncertainError:
            pass
        assert len(sent) == 1, "exactly one mutation on first attempt"
        from github_mutate import LIFECYCLE_STATES
        statuses = [r["status"] for r in state.db.execute(
            "SELECT status FROM mutations WHERE operation='approve_review'").fetchall()]
        assert "uncertain" in statuses

        # Second attempt must NOT blindly re-send, even though it is uncertain.
        try:
            execute_approval(**args)
            raise AssertionError("uncertain must not be blindly retried")
        except MutationUncertainError:
            pass
        assert len(sent) == 1, "uncertain must never blindly re-send"
        assert LIFECYCLE_STATES == ("verified", "failed", "uncertain")
    finally:
        state.close()


def test_verified_lifecycle_persisted_only_after_confirmation() -> None:
    state = fresh_state()
    try:
        decision_id = _seed_decision(state)
        data = execute_approval(
            state, {}, {"pullRequestId": "PR_1"}, "job1",
            decision_id=decision_id, repo="o/r", number=1,
            current_head_sha="HEAD1", current_policy_hash="PH1",
            http_post=_ok_post, rest_before=_good_revalidate,
            rest_after=lambda: "verified",
        )
        assert data.get("addPullRequestReview")
        statuses = [r["status"] for r in state.db.execute(
            "SELECT status FROM mutations WHERE operation='approve_review'").fetchall()]
        assert "verified" in statuses
        assert "pending" not in statuses
    finally:
        state.close()


def test_failed_lifecycle_raises_without_verified() -> None:
    state = fresh_state()
    try:
        decision_id = _seed_decision(state)
        try:
            execute_approval(
                state, {}, {"pullRequestId": "PR_1"}, "job1",
                decision_id=decision_id, repo="o/r", number=1,
                current_head_sha="HEAD1", current_policy_hash="PH1",
                http_post=_ok_post, rest_before=_good_revalidate,
                rest_after=lambda: "failed",
            )
            raise AssertionError("failed verification must raise")
        except RuntimeError:
            pass
        statuses = [r["status"] for r in state.db.execute(
            "SELECT status FROM mutations WHERE operation='approve_review'").fetchall()]
        assert "failed" in statuses
        assert "verified" not in statuses
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
                print(f"FAIL {name}: {exc}")
    print(f"{passed} passed, {failures} failed")
    sys.exit(1 if failures else 0)
