#!/usr/bin/env python3
"""Unit tests for the assurance ladder."""

from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scripts"))

from assurance import (  # noqa: E402
    Profile,
    classify,
    convene_panel,
    drive,
    minimum_profile,
    raised,
)


def test_default_profile() -> None:
    assert minimum_profile("incoming_review").as_dict() == {
        "capability": "workhorse",
        "effort": "medium",
        "independence": "challenger",
    }


def test_sensitive_forces_frontier() -> None:
    assert minimum_profile("incoming_review", sensitive=True, large=False).as_dict() == {
        "capability": "frontier",
        "effort": "high",
        "independence": "challenger",
    }


def test_author_triage_frontier_when_sensitive() -> None:
    assert minimum_profile("author_triage", sensitive=True).capability == "frontier"


def test_raise_effort() -> None:
    assert raised(Profile(), "effort").effort == "high"
    assert raised(Profile(effort="xhigh"), "effort") is None


def test_raise_capability_cap() -> None:
    assert raised(Profile(capability="frontier"), "capability") is None
    assert raised(Profile(capability="workhorse"), "capability").capability == "frontier"


def test_convene_panel_forces_strongest() -> None:
    p = convene_panel(Profile())
    assert p.as_dict() == {"capability": "frontier", "effort": "xhigh", "independence": "panel"}


def test_supported_succeeds() -> None:
    assert classify(Profile(), ["SUPPORTED"]) == "SUCCESS"
    assert classify(Profile(), ["SUPPORTED", "SUPPORTED"]) == "SUCCESS"


def test_missing_evidence_gathers() -> None:
    assert classify(Profile(), ["MISSING_EVIDENCE"]) == "GATHER_EVIDENCE"


def test_insufficient_capability_raises_effort_first() -> None:
    assert classify(Profile(), ["INSUFFICIENT_CAPABILITY"]) == "RAISE_EFFORT"
    assert classify(Profile(effort="xhigh"), ["INSUFFICIENT_CAPABILITY"]) == "RAISE_CAPABILITY"
    assert classify(Profile(capability="frontier", effort="xhigh"), ["INSUFFICIENT_CAPABILITY"]) == "HUMAN"


def test_material_disagreement_convenes_panel_then_human() -> None:
    assert classify(Profile(), ["MATERIAL_DISAGREEMENT"]) == "CONVENE_PANEL"
    assert classify(Profile(independence="panel"), ["MATERIAL_DISAGREEMENT"]) == "HUMAN"


def test_human_reserved() -> None:
    assert classify(Profile(), ["HUMAN_RESERVED"]) == "HUMAN"


def test_empty_signals_gathers() -> None:
    assert classify(Profile(), []) == "GATHER_EVIDENCE"


def test_drive_escalates_effort_then_succeeds() -> None:
    attempts: dict[str, list[str]] = {}

    def assess(p: Profile) -> list[str]:
        key = p.as_dict()["effort"]
        attempts[key] = attempts.get(key, 0) + 1
        return ["INSUFFICIENT_CAPABILITY"] if p.effort == "medium" else ["SUPPORTED"]

    final, decision, steps = drive(minimum_profile("incoming_review"), assess)
    assert decision == "SUCCESS"
    assert final.effort == "high"
    assert [s.decision for s in steps] == ["RAISE_EFFORT", "SUCCESS"]


def test_drive_material_disagreement_convenes_panel() -> None:
    assess = lambda p: (  # noqa: E731
        ["MATERIAL_DISAGREEMENT"] if p.independence != "panel" else ["SUPPORTED"]
    )
    final, decision, steps = drive(Profile(), assess)
    assert decision == "SUCCESS"
    assert final.independence == "panel"
    assert steps[0].decision == "CONVENE_PANEL"


def test_drive_max_steps_hits_human() -> None:
    assess = lambda p: ["INSUFFICIENT_CAPABILITY"]  # noqa: E731
    final, decision, _ = drive(Profile(capability="frontier", effort="xhigh"), assess)
    assert decision == "HUMAN"


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