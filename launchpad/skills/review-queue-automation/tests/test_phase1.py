#!/usr/bin/env python3
"""Phase 1 tests: per-activity authority, policy-as-data, and assurance compute.

Pure deterministic fakes / no external effects.
"""

from __future__ import annotations

import json
import pathlib
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scripts"))

from authority import (  # noqa: E402
    ACTIVITIES,
    MODES,
    AuthorityConfigError,
    can_act,
    mode_for,
    validate_authority,
)
from policy import (  # noqa: E402
    PolicyStore,
    PolicyValidationError,
    canonicalize,
    content_hash,
    validate_policy,
)
from risk import compute_assurance  # noqa: E402

# -- authority -----------------------------------------------------------
def test_authority_defaults_fail_closed() -> None:
    from authority import defaults

    d = defaults()
    assert {a: "disabled" for a in ACTIVITIES} == d
    # no config => every activity disabled
    assert mode_for({}, "o/r", "approve") == "disabled"
    assert can_act({}, "o/r", "approve") is False


def test_authority_per_activity_and_per_repo() -> None:
    cfg = {"authority": {"approve": "live", "comment": "live",
                         "o/r": {"approve": "disabled", "request_changes": "human_escalation"}}}
    # activity-level applies everywhere
    assert mode_for(cfg, "a/b", "approve") == "live"
    # repo override wins
    assert mode_for(cfg, "o/r", "approve") == "disabled"
    assert mode_for(cfg, "o/r", "request_changes") == "human_escalation"
    # default elsewhere
    assert mode_for(cfg, "o/r", "triage") == "disabled"


def test_authority_mutating_requires_hard_gate() -> None:
    cfg = {"authority": {"approve": "live"}}
    # live mode but hard gate not passed => cannot act
    assert can_act(cfg, "o/r", "approve", repo_hard_gate_ok=False) is False
    assert can_act(cfg, "o/r", "approve", repo_hard_gate_ok=True) is True
    # shadow / human_escalation never act
    assert can_act({"authority": {"approve": "shadow"}}, "o/r", "approve") is False
    assert can_act({"authority": {"approve": "human_escalation"}}, "o/r", "approve") is False


def test_authority_validation_rejects_unknown_mode() -> None:
    issues = validate_authority({"approve": "nonsense"})
    assert issues, "unknown mode must be rejected"


def test_authority_factory_helpers_importable() -> None:
    # These are intentionally exercised for import/contract stability.
    assert "approve" in ACTIVITIES
    assert "live" in MODES


# -- policy as data ------------------------------------------------------
def _good_policy() -> dict:
    return {
        "version": "v1",
        "authority": {"approve": "disabled"},
        "approval": {"effective_risk_max": 24, "complexity_max": 2,
                     "file_limit": 50, "line_limit": 1000, "approval_rate_max": 0.5},
        "risk": {"bands": {"low": 24, "medium": 99, "high": 100}, "protected_triggers": []},
        "human_queue": {"expiry_minutes": 1440},
    }


def test_policy_validates_and_pins_hash() -> None:
    vp = canonicalize(_good_policy())
    assert vp.version == "v1"
    assert len(vp.hash) == 64
    # same content => same hash
    assert content_hash(_good_policy()) == vp.hash


def test_policy_rejects_malformed() -> None:
    p = _good_policy()
    p["risk"]["bands"] = {"low": 100, "medium": 50, "high": 40}  # discontinuous
    assert validate_policy(p)
    try:
        canonicalize(p)
        raise AssertionError("must reject discontinuous bands")
    except PolicyValidationError:
        pass


def test_policy_store_atomic_reload_and_lkg() -> None:
    store = PolicyStore(tempfile.mkdtemp())
    # no active yet
    assert store.active()[0] is None
    vp = store.reload(_good_policy())
    assert store.active()[0].hash == vp.hash
    # malformed candidate -> last-known-good retained
    bad = _good_policy()
    bad["approval"]["effective_risk_max"] = "nonsense"
    try:
        store.reload(bad)
        raise AssertionError("must reject malformed candidate")
    except PolicyValidationError:
        pass
    # LKG still active
    active, err = store.active()
    assert active is not None and active.hash == vp.hash, err


def test_policy_reload_with_rollback_retains_lkg() -> None:
    store = PolicyStore(tempfile.mkdtemp())
    vp = store.reload(_good_policy())
    bad = _good_policy()
    bad.pop("approval")  # missing required key
    try:
        store.reload_with_rollback(bad)
        raise AssertionError("malformed reload must not apply")
    except Exception:
        pass
    active, _ = store.active()
    assert active is not None and active.hash == vp.hash


# -- assurance compute ---------------------------------------------------
def test_missing_evidence_lowers_assurance() -> None:
    full = compute_assurance(required_rpn=20, evidence_completeness=1.0, fresh=True,
                             achieved_slots=2, required_slots=2)
    partial = compute_assurance(required_rpn=20, evidence_completeness=0.5, fresh=True,
                                achieved_slots=2, required_slots=2)
    assert full.achieved_assurance > partial.achieved_assurance
    assert partial.evidence_completeness == 0.5
    # missing evidence (incomplete) blocks approval at low completeness
    assert full.can_approve and not partial.can_approve


def test_high_rpn_raises_required_assurance() -> None:
    low = compute_assurance(required_rpn=20, evidence_completeness=1.0, fresh=True,
                            achieved_slots=2, required_slots=2)
    high = compute_assurance(required_rpn=200, evidence_completeness=1.0, fresh=True,
                             achieved_slots=2, required_slots=2)
    assert high.required_assurance == "high"
    assert low.required_assurance == "low"


def test_severe_failure_mode_not_averaged_away() -> None:
    # max RPN of 10*10*10*10=10000 drives the bar up even if other modes are small
    rpn = 10000
    ev = compute_assurance(required_rpn=rpn, evidence_completeness=1.0, fresh=True,
                           achieved_slots=2, required_slots=2)
    assert ev.required_assurance == "high"


def test_disagreement_adds_uncertainty() -> None:
    a = compute_assurance(required_rpn=20, evidence_completeness=1.0, fresh=True,
                          achieved_slots=2, required_slots=2, disagreement=True)
    b = compute_assurance(required_rpn=20, evidence_completeness=1.0, fresh=True,
                          achieved_slots=2, required_slots=2, disagreement=False)
    assert a.residual_uncertainty > b.residual_uncertainty


def test_assurance_fields_are_deterministic_and_serializable() -> None:
    ev = compute_assurance(required_rpn=25, evidence_completeness=0.9, fresh=False,
                           achieved_slots=2, required_slots=3, unknown=True)
    d = ev.as_dict()
    serialized = json.dumps(d, sort_keys=True)
    assert json.loads(serialized) == d


def test_assurance_blockers_gate_approval() -> None:
    ev = compute_assurance(required_rpn=20, evidence_completeness=1.0, fresh=True,
                           achieved_slots=2, required_slots=2,
                           blockers=("protected trigger",))
    assert not ev.can_approve
    assert ev.can_request_changes is True or ev.blockers


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