#!/usr/bin/env python3
"""Calibration tests for scripts/shadow.py. No network, no GitHub, no real models.

Covers: independently sourced outcome labels (never evaluator/merged-derived),
future-evidence exclusion, merged-alone -> unknown, train/calibration split,
false-auto-approval metrics against independent outcomes, zero decision/mutation
persistence, a real risk-threshold sensitivity sweep, explicit fail-closed
approval evidence (the backtest grades against the live gate set, not a more
permissive one), int/str key normalisation at the JSON boundary, and the fitted
train-split threshold.
"""

from __future__ import annotations

import pathlib
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scripts"))

from common import State  # noqa: E402
from risk import FailureMode  # noqa: E402
import shadow  # noqa: E402

CUTOFF = "2026-01-15T00:00:00Z"


def _cfg(**over) -> dict:
    cfg = {
        "version": 1,
        "login": "op",
        "state_dir": tempfile.mkdtemp(),
        "repository": {"slug": "o/r", "root": "/tmp", "base": "launchpad", "preflight": ""},
        "logging": {"directory": "/tmp/log", "format": "otel-jsonl"},
        "models": {"primary": [], "secondary": []},
        "assurance": {"large_diff_lines": 700},
        "dispatch": {"incoming_canary_approved": True, "author_canary_approved": True},
        "approval": {
            "mode": "disabled", "approval_enabled": False, "live_canary_approved": False,
            "effective_risk_max": 24, "complexity_max": 2, "file_limit": 50, "line_limit": 1000,
        },
        "risk": {
            "bands": {"low": 24, "medium": 99, "high": 100},
            "protected_triggers": [r"(^|/)security/", r"(^|/)migrations/"],
        },
        "github": {"read_only": True, "api_version": "2022-11-28"},
    }
    cfg.update(over)
    return cfg


def _sample(
    number: int,
    merged_at: str,
    outcome: str = "unknown",
    evidence: str = "",
    cutoff: str = CUTOFF,
    checks_at: str | None = CUTOFF,
    adjudication_at: str | None = CUTOFF,
    evidence_at: str | None = CUTOFF,
    head_frozen_at: str | None = CUTOFF,
) -> shadow.HistoricalSample:
    return shadow.HistoricalSample(
        repo="launchpad-26/buzz",
        number=number,
        head_sha=f"head-{number}",
        merged_at=merged_at,
        outcome=outcome,
        evidence_source=evidence,
        cutoff=cutoff,
        checks_ok_at=checks_at,
        adjudication_at=adjudication_at,
        evidence_at=evidence_at,
        head_frozen_at=head_frozen_at,
        files=["docs/a.md"],
        additions=5,
        pr_facts={"author_login": "someone", "complexity": 0},
    )


_CLEAN_A = {"signal": "SUPPORTED", "recommendation": "clean", "findings": [],
            "good": ["docs"], "missing_evidence": [], "model": "claude",
            "provider_family": "anthropic", "_schema_ok": True}
_CLEAN_B = {"signal": "SUPPORTED", "recommendation": "clean", "findings": [],
            "good": ["docs"], "missing_evidence": [], "model": "gpt",
            "provider_family": "openai", "_schema_ok": True}


def _verdicts(numbers: list[int]) -> dict[int, list[dict]]:
    return {n: [_CLEAN_A, _CLEAN_B] for n in numbers}


def _assurance(numbers: list[int]) -> dict[int, dict]:
    """`assurance_met` is not reconstructible from GitHub history; the operator
    supplies it per sample in the assessments file. Without it the gate fails
    closed, which several tests below assert directly."""
    return {n: {"assurance_met": True} for n in numbers}


def _sample_dict(number: int, merged_at: str = "2026-01-01T00:00:00Z", outcome: str = "unknown", source: str = "src", cutoff: str = CUTOFF) -> dict:
    return {
        "repo": "launchpad-26/buzz", "number": number, "head_sha": f"head-{number}",
        "merged_at": merged_at, "outcome": outcome, "evidence_source": source,
        "cutoff": cutoff,
        "cutoff": CUTOFF, "checks_ok_at": CUTOFF, "adjudication_at": CUTOFF,
        "evidence_at": CUTOFF, "head_frozen_at": CUTOFF,
        "files": ["docs/a.md"], "additions": 5,
        "pr_facts": {"author_login": "someone", "complexity": 0},
    }


def _state() -> State:
    return State({"state_dir": tempfile.mkdtemp()})


def _run(
    entries: list[shadow.HistoricalSample],
    *,
    train_ratio: float = 0.75,
    assessments: dict | None = None,
    over: dict | None = None,
):
    cfg = _cfg(**(over or {}))
    st = _state()
    numbers = [e.number for e in entries]
    if assessments is None:
        assessments = _assurance(numbers)
    report = shadow.backtest(
        entries, cfg,
        verdicts=_verdicts(numbers),
        assessments=assessments,
        login="op", train_ratio=train_ratio, state=st,
    )
    return report, cfg, st


# ---- 1. outcome labels independent of the evaluator ----

def test_false_auto_surfaces_when_independent_outcome_is_adverse() -> None:
    # 8 samples, 0.75 split -> train 6, calibrate 2 (samples 7, 8).
    entries = [_sample(n, f"2026-01-{n:02d}T00:00:00Z", outcome="clean", evidence=f"src{n}")
               for n in range(1, 8)]
    entries.append(_sample(8, "2026-01-08T00:00:00Z", outcome="adverse", evidence="incident-tracker#8"))
    report, _, _ = _run(entries, train_ratio=0.75)
    assert report["train_count"] == 6
    assert report["calibrate_count"] == 2
    # evaluator blesses both calibration samples, but the adverse outcome is distinct
    assert report["approval_candidate_count"] == 2
    assert report["false_auto_approval_candidates"] == [8]
    assert report["false_auto_approval_count"] == 1
    r8 = next(r for r in report["samples"] if r["number"] == 8)
    assert r8["outcome"] == "adverse"
    assert r8["evidence_source"] == "incident-tracker#8"
    assert r8["would_auto_approve"] is True


def test_label_never_derived_from_merged() -> None:
    # merged PR, no outcome / no evidence source -> unknown, never clean
    s = _sample(10, "2026-01-10T00:00:00Z")
    assert s.outcome_label() == "unknown"


def test_label_validation_is_strict() -> None:
    assert _sample(11, "2026-01-11T00:00:00Z", outcome="APPROVAL").outcome_label() == "unknown"


# ---- 2. future evidence excluded; nothing hardcoded true ----

def test_future_evidence_never_consumed() -> None:
    s = _sample(21, "2026-01-05T00:00:00Z", outcome="clean", evidence="src",
                checks_at="2026-02-01T00:00:00Z",   # AFTER cutoff and AFTER merged
                adjudication_at="2026-01-01T00:00:00Z",
                evidence_at="2026-01-01T00:00:00Z")
    pr = s.before_merge_facts()
    assert pr.checks_ok is False
    assert pr.adjudication_complete is True
    assert pr.evidence_fresh is True


def test_no_evidence_and_no_cutoff_is_fail_closed() -> None:
    s = _sample(22, "2026-01-05T00:00:00Z", cutoff="")
    pr = s.before_merge_facts()
    assert pr.checks_ok is False
    assert pr.adjudication_complete is False
    assert pr.evidence_fresh is False


def test_future_only_evidence_blocks_approval() -> None:
    # all evidence after merged-> will not be approved
    entries = [_sample(n, f"2026-01-{n:02d}T00:00:00Z", outcome="clean", evidence="src",
                       checks_at="2026-03-01T00:00:00Z") for n in (31, 32, 33)]
    report, _, _ = _run(entries, train_ratio=0.0)
    # calibrate = all three; no evidence fresh -> fail-closed everywhere, no candidates
    assert report["approval_candidate_count"] == 0


# ---- 3. train / calibration split ----

def test_train_calibration_split_is_time_ordered() -> None:
    entries = [_sample(n, f"2026-01-{n:02d}T00:00:00Z", outcome="clean", evidence="src")
               for n in range(1, 11)]
    report, _, _ = _run(entries, train_ratio=0.7)
    assert report["train_count"] == 7
    assert report["calibrate_count"] == 3
    # calibrate = the most recent 3, in their original time order
    assert [r["number"] for r in report["samples"]] == [8, 9, 10]


# ---- 4. threshold sensitivity ----

def test_threshold_sweep_is_sensitive_to_real_risk() -> None:
    low = _sample(60, "2026-01-01T00:00:00Z", outcome="clean", evidence="a")
    med = _sample(61, "2026-01-02T00:00:00Z", outcome="clean", evidence="b")
    hi = _sample(62, "2026-01-03T00:00:00Z", outcome="adverse", evidence="c")
    entries = [low, med, hi]
    # adverse one carries a high FMEA-C failure mode -> risk well above the 24 ceiling
    assessments = {
        60: {"assurance_met": True},
        61: {"assurance_met": True, "failure_modes": [FailureMode("m", 3, 3, 3, 2)]},   # rpn 54 > 24
        62: {"assurance_met": True, "failure_modes": [FailureMode("m", 7, 7, 7, 7)]},   # rpn 2401
    }
    cfg = _cfg()
    st = _state()
    report = shadow.backtest(entries, cfg, verdicts=_verdicts([low.number, med.number, hi.number]),
                             assessments=assessments, login="op", train_ratio=0.0, state=st)
    sens = report["threshold_sensitivity"]
    assert sens["current"] == 24
    # at the current (24) ceiling only the low-risk clean sample clears -> 0 false
    point_at_24 = next(p for p in sens["sweep"] if p["threshold"] == 24)
    assert point_at_24["approval_candidates"] == 1
    assert point_at_24["false_auto"] == 0
    # at a high-enough ceiling the adverse, high-risk sample creeps in -> 1 false
    lowpoint = min(sens["sweep"], key=lambda p: p["threshold"])
    highpoint = max(sens["sweep"], key=lambda p: p["threshold"])
    assert lowpoint["false_auto"] == 0
    assert highpoint["false_auto"] == 1
    # monotone: more headroom never reduces approval candidates
    prev = -1
    for p in sens["sweep"]:
        assert p["approval_candidates"] >= prev
        prev = p["approval_candidates"]


# ---- 5. no persistence, no mutation ----

def test_backtest_forces_shadow_and_writes_no_decision() -> None:
    entries = [_sample(41, "2026-01-01T00:00:00Z", outcome="clean", evidence="a"),
               _sample(42, "2026-01-02T00:00:00Z", outcome="adverse", evidence="b")]
    report, cfg, st = _run(entries, train_ratio=0.0)
    assert report["total"] == 2
    assert cfg["approval"]["mode"] == "disabled"  # on-disk config untouched
    # no approval decision row, even after running the backtest on a live-capable config
    live = _cfg(approval={"mode": "live", "approval_enabled": True, "live_canary_approved": True})
    report2, _, st2 = _run(entries, train_ratio=0.0, over=live)
    assert st2.db.execute("SELECT 1 FROM approval_decisions").fetchone() is None
    assert report2["false_auto_approval_count"] >= 0


def test_shadow_cfg_forced_in_memory_only() -> None:
    cfg = _cfg(approval={"mode": "live", "approval_enabled": True, "live_canary_approved": True})
    forced = shadow.shadow_cfg(cfg)
    assert forced["approval"]["mode"] == "shadow"
    assert cfg["approval"]["mode"] == "live"  # original untouched


def test_current_shadow_no_mutation_no_decision() -> None:
    cfg = _cfg()
    st = _state()
    entry = _sample_dict(50, outcome="clean", source="a")
    r = shadow.current_shadow(cfg, entry, verdicts={50: [_CLEAN_A, _CLEAN_B]},
                              assessments=_assurance([50]), login="op", state=st)
    assert r["would_auto_approve"] is True
    assert r["decision_id"] is None
    assert st.db.execute("SELECT 1 FROM approval_decisions").fetchone() is None


# ---- 6. explicit approval evidence: the backtest grades the LIVE gate set ----
#
# Regression guard for B5. `shadow.evaluate_before_merge` used to call
# `approval_evaluate.evaluate` with no `evidence=` argument, which takes the
# legacy default-open branch in `compute_gates` and silently sets FIVE gates to
# True. The backtest therefore graded every sample against a strictly more
# permissive gate set than `dispatcher.py`, and reported would-approve for
# samples the live path would have escalated.

def _gates_for(sample: shadow.HistoricalSample, cfg: dict, assessment: dict,
               *, audit_writable: bool = True):
    from approval_evaluate import compute_gates

    evidence = shadow.historical_evidence(
        sample, cfg, assessment, audit_writable=audit_writable
    )
    return compute_gates(
        cfg, sample.before_merge_facts(), [_CLEAN_A, _CLEAN_B],
        ["claude", "gpt"], 0, "low", "op",
        head_sha=sample.head_sha,
        profile={"independence": "challenger"},
        evidence=evidence,
    )


def test_legacy_no_evidence_call_defaults_five_gates_open() -> None:
    """The behaviour shadow.py must never re-enter. If this ever stops being
    true, `historical_evidence` is no longer load-bearing and can be revisited."""
    from approval_evaluate import compute_gates

    s = _sample(70, "2026-01-01T00:00:00Z", outcome="clean", evidence="src")
    open_gates = compute_gates(
        _cfg(), s.before_merge_facts(), [_CLEAN_A, _CLEAN_B], ["claude", "gpt"],
        0, "low", "op", head_sha=s.head_sha, profile={"independence": "challenger"},
    )
    for gate in shadow.EVIDENCE_GATES:
        assert getattr(open_gates, gate) is True, gate


def test_each_evidence_gate_fails_closed_without_proof() -> None:
    cfg = _cfg()
    # additions=0 -> bounded_change unprovable; no assurance_met in assessments;
    # no head_frozen_at -> revalidation unprovable; audit probe failed;
    # a configured REST floor -> rate limit unreconstructible.
    cfg_with_floor = _cfg(poll={"rest_remaining_floor": 200})
    bare = shadow.HistoricalSample(
        repo="o/r", number=71, head_sha="head-71", merged_at="2026-01-01T00:00:00Z",
        outcome="clean", evidence_source="src", cutoff=CUTOFF,
        checks_ok_at=CUTOFF, adjudication_at=CUTOFF, evidence_at=CUTOFF,
        head_frozen_at=None, files=["docs/a.md"], additions=0,
        pr_facts={"author_login": "someone", "complexity": 0},
    )
    gates = _gates_for(bare, cfg_with_floor, {}, audit_writable=False)
    failed = {k for k, v in gates.failed().items() if v}
    for gate in shadow.EVIDENCE_GATES:
        assert gate in failed, f"{gate} must fail closed without evidence"
    # ...and each one flips on when, and only when, its proof is present.
    proven = _sample(71, "2026-01-01T00:00:00Z", outcome="clean", evidence="src")
    ok = _gates_for(proven, cfg, {"assurance_met": True}, audit_writable=True)
    for gate in shadow.EVIDENCE_GATES:
        assert getattr(ok, gate) is True, gate


def test_backtest_gate_set_is_identical_to_the_live_path() -> None:
    """Same inputs, same gates. The dispatcher builds an ApprovalEvidence from
    live state; shadow builds one from the historical record. Given equal
    evidence VALUES the two must produce byte-identical gate dicts — shadow must
    not be evaluating a different or smaller gate set."""
    from approval_evaluate import ApprovalEvidence, compute_gates

    cfg = _cfg()
    s = _sample(72, "2026-01-01T00:00:00Z", outcome="clean", evidence="src")
    shadow_ev = shadow.historical_evidence(s, cfg, {"assurance_met": True}, audit_writable=True)
    # The shape dispatcher._approval_evidence returns.
    live_ev = ApprovalEvidence(
        bounded_change=True, audit_writable=True, assurance_met=True,
        revalidation_ok=True, rate_limit_ok=True,
    )
    kwargs = dict(
        head_sha=s.head_sha, profile={"independence": "challenger"},
    )
    a = compute_gates(cfg, s.before_merge_facts(), [_CLEAN_A, _CLEAN_B],
                      ["claude", "gpt"], 0, "low", "op", evidence=shadow_ev, **kwargs)
    b = compute_gates(cfg, s.before_merge_facts(), [_CLEAN_A, _CLEAN_B],
                      ["claude", "gpt"], 0, "low", "op", evidence=live_ev, **kwargs)
    assert a.failed() == b.failed()
    assert set(a.all_gates()) == set(b.all_gates())
    assert set(a.all_gates()) >= set(shadow.EVIDENCE_GATES)


def test_missing_assurance_evidence_blocks_the_whole_run() -> None:
    entries = [_sample(n, f"2026-01-{n:02d}T00:00:00Z", outcome="clean", evidence="src")
               for n in (81, 82, 83)]
    report, _, _ = _run(entries, train_ratio=0.0, assessments={})
    assert report["approval_candidate_count"] == 0
    assert report["universally_failed_gates"] == ["assurance_met"]
    assert any("assurance_met" in w for w in report["warnings"])


def test_configured_rest_floor_is_not_reconstructible_and_fails_closed() -> None:
    entries = [_sample(n, f"2026-01-{n:02d}T00:00:00Z", outcome="clean", evidence="src")
               for n in (84, 85)]
    report, _, _ = _run(entries, train_ratio=0.0, over={"poll": {"rest_remaining_floor": 200}})
    assert report["approval_candidate_count"] == 0
    assert "rate_limit_ok" in report["universally_failed_gates"]


def test_daily_approval_cap_is_replayed_as_a_counterfactual() -> None:
    # Two same-day samples, cap of 1: the second one hits the replayed cap.
    entries = [_sample(86, "2026-01-14T01:00:00Z", outcome="clean", evidence="src",
                       cutoff="2026-01-14T01:00:00Z", checks_at="2026-01-14T00:00:00Z",
                       adjudication_at="2026-01-14T00:00:00Z",
                       evidence_at="2026-01-14T00:00:00Z",
                       head_frozen_at="2026-01-14T00:00:00Z"),
               _sample(87, "2026-01-14T02:00:00Z", outcome="clean", evidence="src",
                       cutoff="2026-01-14T02:00:00Z", checks_at="2026-01-14T00:00:00Z",
                       adjudication_at="2026-01-14T00:00:00Z",
                       evidence_at="2026-01-14T00:00:00Z",
                       head_frozen_at="2026-01-14T00:00:00Z")]
    over = {"approval": dict(_cfg()["approval"], daily_limit=1)}
    report, _, _ = _run(entries, train_ratio=0.0, over=over)
    assert report["approval_candidate_count"] == 1
    blocked = next(r for r in report["samples"] if r["number"] == 87)
    assert "rate_limit_ok" in blocked["failed_gates"]


# ---- 7. int/str key normalisation at the JSON boundary ----

def test_string_keys_are_normalised_to_int() -> None:
    entries = [_sample(n, f"2026-01-{n:02d}T00:00:00Z", outcome="clean", evidence="src")
               for n in (91, 92)]
    cfg = _cfg()
    report = shadow.backtest(
        entries, cfg,
        verdicts={"91": [_CLEAN_A, _CLEAN_B], "92": [_CLEAN_A, _CLEAN_B]},
        assessments={"91": {"assurance_met": True}, "92": {"assurance_met": True}},
        login="op", train_ratio=0.0, state=_state(),
    )
    assert report["samples_with_verdicts"] == 2
    assert report["approval_candidate_count"] == 2


def test_non_integer_key_is_rejected_not_dropped() -> None:
    try:
        shadow._normalize_number_map({"not-a-number": []}, label="verdicts")
    except ValueError as exc:
        assert "non-integer key" in str(exc)
    else:
        raise AssertionError("a non-integer key must raise, not be silently dropped")


def test_warning_distinguishes_unmatched_from_unsupplied() -> None:
    entries = [_sample(n, f"2026-01-{n:02d}T00:00:00Z", outcome="clean", evidence="src")
               for n in (93, 94)]
    cfg = _cfg()
    # verdicts supplied, but for PR numbers that are not in the sample set
    report = shadow.backtest(
        entries, cfg, verdicts={"999": [_CLEAN_A, _CLEAN_B]},
        assessments={}, login="op", train_ratio=0.0, state=_state(),
    )
    assert report["samples_with_verdicts"] == 0
    assert any("NONE matched" in w for w in report["warnings"])
    assert not any("no reviewer verdicts supplied" in w for w in report["warnings"])
    # and the genuinely-empty case still says so
    empty = shadow.backtest(
        entries, cfg, verdicts={}, assessments={}, login="op",
        train_ratio=0.0, state=_state(),
    )
    assert any("no reviewer verdicts supplied" in w for w in empty["warnings"])


# ---- 8. the train split fits a parameter ----

def test_train_split_fits_a_threshold_and_scores_it_held_out() -> None:
    # train half contains an adverse sample that clears every gate at risk 16 —
    # a would-approve the gate set got WRONG — so the learned ceiling drops
    # below it. This is the whole point of fitting on train: the mistake is
    # priced in before the calibration half is scored.
    entries = [_sample(n, f"2026-01-{n:02d}T00:00:00Z",
                       outcome="adverse" if n == 2 else "clean", evidence="src")
               for n in (1, 2, 3, 4)]
    assessments = {n: {"assurance_met": True} for n in (1, 2, 3, 4)}
    assessments[2] = {"assurance_met": True, "failure_modes": [FailureMode("m", 2, 2, 2, 2)]}  # rpn 16
    report, _, _ = _run(entries, train_ratio=0.5, assessments=assessments)
    learned = report["learned_threshold"]
    assert learned["fitted_on"] == 2
    assert learned["changed"] is True
    assert learned["effective_risk_max"] == 15
    assert learned["held_out"]["threshold"] == 15
    assert learned["configured"]["threshold"] == 24


def test_fit_never_raises_the_configured_ceiling() -> None:
    entries = [_sample(n, f"2026-01-{n:02d}T00:00:00Z", outcome="clean", evidence="src")
               for n in (1, 2, 3, 4)]
    report, _, _ = _run(entries, train_ratio=0.5)
    learned = report["learned_threshold"]
    assert learned["changed"] is False
    assert learned["effective_risk_max"] == 24


def test_train_results_are_reported_not_discarded() -> None:
    entries = [_sample(n, f"2026-01-{n:02d}T00:00:00Z", outcome="clean", evidence="src")
               for n in (1, 2, 3, 4)]
    report, _, _ = _run(entries, train_ratio=0.5)
    assert len(report["train_samples"]) == 2
    assert [r["number"] for r in report["train_samples"]] == [1, 2]


if __name__ == "__main__":
    failures = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"PASS {name}")
            except Exception as exc:  # noqa: BLE001
                failures += 1
                print(f"FAIL {name}: {exc}")
    sys.exit(1 if failures else 0)