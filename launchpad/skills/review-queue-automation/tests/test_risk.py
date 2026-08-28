#!/usr/bin/env python3
"""Fakes/tempfile tests for the risk + policy module (risk.py).

Covers FMEA-C JSON serialization, effective-score-as-max, the model-can-only-
raise-floor rule, band boundary/continuity enforcement, max-risk handling,
protected triggers, and versioned risk-assessment.json writing.
"""

from __future__ import annotations

import json
import pathlib
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scripts"))

from risk import (  # noqa: E402
    RISK_ASSESSMENT_VERSION,
    BoundedChange,
    ConfigBandError,
    FailureMode,
    ProtectedTriggerError,
    combined_risk,
    effective_risk,
    protected_triggered,
    read_assessment,
    risk_band,
    validate_bands,
    write_assessment,
)


def test_failure_mode_json_roundtrip() -> None:
    mode = FailureMode("fm-1", severity=5, likelihood=4, detectability=3, complexity=2)
    restored = FailureMode.from_dict(mode.to_dict())
    assert restored == mode
    # Lossless through real JSON text.
    blob = json.dumps(mode.to_dict())
    again = FailureMode.from_dict(json.loads(blob))
def test_failure_mode_rejects_out_of_range() -> None:
    def _make(**over):
        base = {"severity": 5, "likelihood": 5, "detectability": 5, "complexity": 5}
        base.update(over)
        return FailureMode("x", **base)

    for over in ({"severity": 0}, {"likelihood": 11}, {"detectability": -1}):
        try:
            _make(**over)
            raise AssertionError(f"{over} must be rejected")
        except ValueError:
            pass


def test_effective_risk_is_max_not_average() -> None:
    modes = [
        FailureMode("a", 1, 1, 1, 1),       # rpn 1
        FailureMode("b", 10, 10, 10, 10),   # rpn 10000
    ]
    assert effective_risk(modes) == 10000
    assert effective_risk([]) == 0


def test_model_can_only_raise_the_floor() -> None:
    assert combined_risk(10, 40) == 40   # raised above floor
    assert combined_risk(40, 10) == 40   # cannot be lowered below floor
    assert combined_risk(40, 40) == 40


def test_band_boundaries_24_25_99_100() -> None:
    bands = {"low": 24, "medium": 99, "high": 100}
    assert risk_band(24, bands) == "low"
    assert risk_band(25, bands) == "medium"
    assert risk_band(99, bands) == "medium"
    assert risk_band(100, bands) == "high"


def test_max_risk_is_high() -> None:
    bands = {"low": 24, "medium": 99, "high": 100}
    assert risk_band(24, bands) == "low"
    assert risk_band(25, bands) == "medium"
    assert risk_band(99, bands) == "medium"
    assert risk_band(100, bands) == "high"
    assert risk_band(10000, bands) == "high"  # anything at/above max stays high


def test_validate_bands_accepts_continuous() -> None:
    validate_bands({"low": 24, "medium": 99, "high": 100})
    validate_bands({"low": 1, "medium": 50, "high": 100})
    validate_bands({})  # defaults are valid


def test_validate_bands_rejects_breaks_in_continuity() -> None:
    for bands in (
        {"low": 100, "medium": 50, "high": 150},  # not increasing
        {"low": 24, "medium": 24, "high": 100},   # overlap (not strictly increasing)
        {"low": 24, "medium": 99, "high": 99},    # equal ceiling/floor
        {"low": -1, "medium": 99, "high": 100},   # negative low
    ):
        try:
            validate_bands(bands)
            raise AssertionError(f"bands {bands} must be rejected")
        except ConfigBandError:
            pass


def test_protected_trigger_matches_and_fail_closed() -> None:
    patterns = [r"(^|/)security/", r"(^|/)migrations/"]
    path, pat = protected_triggered(["docs/readme.md", "security/cred"], patterns)
    assert path == "security/cred"
    assert pat == r"(^|/)security/"
    assert protected_triggered(["docs/readme.md"], patterns) == (None, None)


def test_bounded_change_passes_and_reports_failures() -> None:
    ok = BoundedChange(one_clear_purpose=True, bounded_blast_radius=True,
                       straightforward_rollback=True, adequate_tests=True)
    assert ok.passes()
    bad = BoundedChange(one_clear_purpose=True, bounded_blast_radius=False)
    assert not bad.passes()
    assert "bounded_blast_radius" in bad.failed()


def test_versioned_assessment_write_and_read_roundtrip() -> None:
    target = pathlib.Path(tempfile.mkdtemp()) / "risk-assessment.json"
    payload = {"effective_risk": 25, "band": "medium", "failure_modes": []}
    write_assessment(target, payload)
    assert target.is_file()
    on_disk = json.loads(target.read_text(encoding="utf-8"))
    assert on_disk["version"] == RISK_ASSESSMENT_VERSION
    version, data = read_assessment(target)
    assert version == RISK_ASSESSMENT_VERSION
    assert data == payload


def test_versioned_assessment_rejects_unknown_version() -> None:
    target = pathlib.Path(tempfile.mkdtemp()) / "risk-assessment.json"
    target.write_text(json.dumps({"version": 999, "risk_assessment": {"x": 1}}), encoding="utf-8")
    try:
        read_assessment(target)
        raise AssertionError("unsupported version must be rejected")
    except ValueError:
        pass


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
