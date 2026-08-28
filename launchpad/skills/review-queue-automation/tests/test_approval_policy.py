#!/usr/bin/env python3
"""Fakes/tempfile tests for the approval evaluation policy (approval_evaluate.py)
and the guarded approval action (approval_action.py).

Covers the live gate (every-gate pass), every individual negative gate, protected
triggers suppressing live approval, the 24/25 risk threshold, and decision
validation by SQLite id / expiry / revalidation.
"""

from __future__ import annotations

import datetime as dt
import json
import pathlib
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scripts"))

from approval_evaluate import (  # noqa: E402
    ApprovalEvidence,
    PRFacts,
    compute_gates,
    evaluate,
    policy_hash_of,
)
from common import State  # noqa: E402


def fresh_state() -> State:
    return State({"state_dir": tempfile.mkdtemp()})


def _cfg(**over) -> dict:
    cfg = {
        "version": 1,
        "login": "me",
        "state_dir": tempfile.mkdtemp(),
        "repository": {"slug": "o/r", "root": "/tmp", "base": "launchpad"},
        "logging": {"directory": "/tmp/l", "format": "otel-jsonl"},
        "models": {"primary": [], "secondary": []},
        "assurance": {"large_diff_lines": 700},
        "dispatch": {},
        "approval": {
            "mode": "live", "approval_enabled": True, "live_canary_approved": True,
            "effective_risk_max": 24, "complexity_max": 2, "file_limit": 50, "line_limit": 1000,
        },
        "risk": {
            "bands": {"low": 24, "medium": 99, "high": 100},
            "protected_triggers": [r"(^|/)security/", r"(^|/)migrations/"],
        },
        "github": {"read_only": True, "api_version": "2022-11-28"},
        # `authority.approve` is conjunctive with `approval.mode`; a fixture that
        # means "live approval is configured" must grant both.
        "authority": {"approve": "live", "request_changes": "disabled"},
    }
    cfg.update(over)
    return cfg


def _pr(**over) -> PRFacts:
    base = dict(
        draft=False, author_login="other", head_sha="H", files=["docs/a.md"],
        additions=5, checks_ok=True, adjudication_complete=True,
        complexity=0, evidence_fresh=True,
    )
    base.update(over)
    return PRFacts(**base)


def _verdict(model, family, **over) -> dict:
    v = {"signal": "SUPPORTED", "recommendation": "clean", "findings": [],
         "_schema_ok": True, "model": model, "provider_family": family}
    v.update(over)
    return v


def _full_evidence(**over) -> ApprovalEvidence:
    # Slot counts default to None so they are DERIVED from the actual verdicts;
    # each test overrides them only when a slot-mismatch case needs a specific
    # conclusion. External-evidence gates are positive by default.
    base = dict(
        required_reviewers=None, completed_reviewers=None,
        bounded_change=True, audit_writable=True, assurance_met=True,
        revalidation_ok=True, rate_limit_ok=True,
    )
    base.update(over)
    return ApprovalEvidence(**base)


def _live_args(state, **mut):
    args = dict(
        state=state, cfg=_cfg(), repo="o/r", number=1, head_sha="H",
        pr=_pr(), verdicts=[_verdict("m1", "f1"), _verdict("m2", "f2")],
        profile={"independence": "challenger"},
        reviewers=["m1", "m2"], assessments={}, login="me",
        evidence=_full_evidence(),
    )
    args.update(mut)
    return args


def test_live_requires_every_gate_and_persists_decision() -> None:
    state = fresh_state()
    try:
        res = evaluate(**_live_args(state))
        assert res.disposition == "live", res.failed_gates
        assert res.decision_id
        row = state.db.execute("SELECT 1 FROM approval_decisions WHERE id=?", (res.decision_id,)).fetchone()
        assert row is not None
    finally:
        state.close()


def _assert_not_live(state, **mut) -> None:
    res = evaluate(**_live_args(state, **mut))
    assert res.disposition != "live", res.failed_gates


def test_every_negative_gate_blocks_live() -> None:
    state = fresh_state()
    try:
        # ... gates driven by PR facts / caller values ...
        _assert_not_live(state, pr=_pr(draft=True))                              # pr_open_not_draft
        _assert_not_live(state, pr=_pr(author_login="me"))                       # author_not_identity
        _assert_not_live(state, pr=_pr(evidence_fresh=False))                    # evidence_fresh
        _assert_not_live(state, pr=_pr(checks_ok=False))                         # checks_complete_ok
        _assert_not_live(state, pr=_pr(adjudication_complete=False))             # adjudication_complete
        _assert_not_live(state, pr=_pr(additions=99999))                         # limits_pass
        _assert_not_live(state, pr=_pr(complexity=5))                            # complexity_le
        _assert_not_live(state, pr=_pr(head_sha="OTHER"))                        # head_matches
        # ... gates driven by verdicts / reviewers ...
        _assert_not_live(state, verdicts=[_verdict("m1", "f1")])                 # distinct_reviewers
        _assert_not_live(state, reviewers=["m1", "m2"], verdicts=[
            _verdict("m1", "f1"), _verdict("m2", "f2"), _verdict("m3", "f3")])   # required slots mismatch
        _assert_not_live(state, verdicts=[
            _verdict("m1", "f1", signal="MISSING_EVIDENCE"), _verdict("m2", "f2")])  # unanimous_clean
        _assert_not_live(state, verdicts=[
            _verdict("m1", "f1", _schema_ok=False), _verdict("m2", "f2")])       # valid_verdicts
        # ... external evidence gates ...
        _assert_not_live(state, evidence=_full_evidence(bounded_change=False))   # bounded_change
        _assert_not_live(state, evidence=_full_evidence(audit_writable=False))   # audit_writable
        _assert_not_live(state, evidence=_full_evidence(assurance_met=False))    # assurance_met
        _assert_not_live(state, evidence=_full_evidence(revalidation_ok=False))  # revalidation_ok
        _assert_not_live(state, evidence=_full_evidence(rate_limit_ok=False))    # rate_limit_ok
        _assert_not_live(state, evidence=_full_evidence(completed_reviewers=1))  # exact slots
        # ... approval_enabled / canary ...
        _assert_not_live(state, cfg=_cfg(approval={"mode": "live", "approval_enabled": False,
                                                   "live_canary_approved": True, "effective_risk_max": 24,
                                                   "complexity_max": 2}))
        _assert_not_live(state, cfg=_cfg(approval={"mode": "live", "approval_enabled": True,
                                                   "live_canary_approved": False, "effective_risk_max": 24,
                                                   "complexity_max": 2}))
    finally:
        state.close()


def test_protected_trigger_always_blocks_live() -> None:
    state = fresh_state()
    try:
        res = evaluate(**_live_args(state, pr=_pr(files=["security/cred"])))
        assert res.disposition == "human_escalation"
        assert res.protected
        # no decision record is ever persisted for a protected PR
        assert state.db.execute("SELECT 1 FROM approval_decisions").fetchone() is None
    finally:
        state.close()


def test_risk_threshold_24_vs_25() -> None:
    state = fresh_state()
    try:
        # effective risk 24 (== max) is allowed.
        res24 = evaluate(**_live_args(state, assessments={"model_observed_effective": 24}))
        assert res24.disposition == "live"
        # risk 25 exceeds the 24 ceiling -> blocked.
        res25 = evaluate(**_live_args(state, assessments={"model_observed_effective": 25}))
        assert res25.disposition != "live"
        assert "effective_risk_le" in res25.failed_gates
        # a model can only raise, never lower, below the deterministic floor.
        res_floor = evaluate(**_live_args(state, assessments={"model_observed_effective": 0}))
        assert res_floor.risk_score in (0, 24)  # model 0 cannot go below deterministic 0
    finally:
        state.close()


def test_policy_hash_covers_full_config() -> None:
    # A change in an unrelated config key still changes the full-config hash, so
    # any config edit invalidates a previously persisted decision.
    a = policy_hash_of(_cfg())
    b = policy_hash_of(_cfg(logging={"directory": "/different", "format": "otel-jsonl"}))
    assert a != b
    assert len(a) == 24


def _future() -> str:
    ts = dt.datetime.now(dt.timezone.utc) + dt.timedelta(minutes=60)
    return ts.isoformat().replace("+00:00", "Z")


def test_load_eligible_decision_and_revalidation_in_approval_action() -> None:
    import approval_action

    state = fresh_state()
    try:
        state.db.execute(
            "INSERT INTO approval_decisions(id,repo,number,head_sha,policy_hash,status,mode,risk_score,created_at,expires_at) "
            "VALUES(?,?,?,?,?,?,?,?,?,?)",
            ("dd1", "o/r", 1, "H", "PH", "eligible", "live", 5, "2026-01-01T00:00:00Z", _future()),
        )
        state.db.commit()
        row = approval_action.load_eligible_decision(state, "dd1")
        assert row and row["repo"] == "o/r"
        assert approval_action.load_eligible_decision(state, "nope") is None

        # Protected trigger in the revalidated file set -> revalidation fails closed.
        cfg = _cfg()
        revalidate = approval_action.build_revalidation(
            cfg, current_head_sha="H", login="me",
            rest_provider=lambda: {"head": {"sha": "H"}, "draft": False,
                                   "user": {"login": "other"}, "files": ["security/x"]},
        )
        checks = revalidate()
        assert checks["no_protected_trigger"] is False
        assert checks["head_matches"] is True

        # Clean file set passes all pre-mutation checks.
        revalidate_ok = approval_action.build_revalidation(
            cfg, current_head_sha="H", login="me",
            rest_provider=lambda: {"head": {"sha": "H"}, "draft": False,
                                   "user": {"login": "other"}, "files": ["docs/a.md"]},
        )
        ok = revalidate_ok()
        assert all(ok.values()), ok
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
