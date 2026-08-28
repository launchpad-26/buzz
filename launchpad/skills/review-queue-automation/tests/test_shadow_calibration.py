#!/usr/bin/env python3
"""Calibration tests for scripts/shadow.py. No network, no GitHub, no real models.

Covers: independently sourced outcome labels (never evaluator/merged-derived),
future-evidence exclusion, merged-alone -> unknown, train/calibration split,
false-auto-approval metrics against independent outcomes, zero decision/mutation
persistence, and a real risk-threshold sensitivity sweep.
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


def _sample_dict(number: int, merged_at: str = "2026-01-01T00:00:00Z", outcome: str = "unknown", source: str = "src", cutoff: str = CUTOFF) -> dict:
    return {
        "repo": "launchpad-26/buzz", "number": number, "head_sha": f"head-{number}",
        "merged_at": merged_at, "outcome": outcome, "evidence_source": source,
        "cutoff": cutoff,
        "cutoff": CUTOFF, "checks_ok_at": CUTOFF, "adjudication_at": CUTOFF,
        "evidence_at": CUTOFF, "files": ["docs/a.md"], "additions": 5,
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
    report = shadow.backtest(
        entries, cfg,
        verdicts=_verdicts([e.number for e in entries]),
        assessments=assessments or {},
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
        61: {"failure_modes": [FailureMode("m", 3, 3, 3, 2)]},   # rpn 54 > 24
        62: {"failure_modes": [FailureMode("m", 7, 7, 7, 7)]},   # rpn 2401
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
                              assessments={}, login="op", state=st)
    assert r["would_auto_approve"] is True
    assert r["decision_id"] is None
    assert st.db.execute("SELECT 1 FROM approval_decisions").fetchone() is None


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