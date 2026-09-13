#!/usr/bin/env python3
"""Tests for `rqa.protocol`'s shared types (`CONTRACTS.md` §2) — T30 and shape checks.

No pytest: every `test_*` function here takes no arguments, per `tests/run_all.py`.
"""

from __future__ import annotations

import dataclasses
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from rqa.protocol import (  # noqa: E402
    MECHANICAL_GROUP,
    SUBSTANTIVE_GROUP,
    Category,
    EvidenceState,
    Finding,
    HarnessIdentity,
    InjectionAttempt,
    Invalid,
    Location,
    Obligation,
    Remedy,
    Valid,
    Verdict,
)


# -- T30: the two groups are the exact disjoint union of set(Category) --------
def test_category_groups_are_disjoint() -> None:
    assert MECHANICAL_GROUP.isdisjoint(SUBSTANTIVE_GROUP)


def test_category_groups_union_to_every_category() -> None:
    assert MECHANICAL_GROUP | SUBSTANTIVE_GROUP == set(Category)


def test_category_groups_are_frozensets_of_category() -> None:
    assert isinstance(MECHANICAL_GROUP, frozenset)
    assert isinstance(SUBSTANTIVE_GROUP, frozenset)
    assert all(isinstance(member, Category) for member in MECHANICAL_GROUP | SUBSTANTIVE_GROUP)


def test_mechanical_group_members() -> None:
    assert MECHANICAL_GROUP == {Category.MECHANICAL, Category.PROCEDURAL, Category.CREATION_TIME}


def test_substantive_group_members() -> None:
    assert SUBSTANTIVE_GROUP == {
        Category.CORRECTNESS,
        Category.SECURITY,
        Category.ARCHITECTURAL,
        Category.EVIDENCE,
    }


# -- Evidence states: exactly the seven named values ---------------------------
def test_evidence_state_has_exactly_seven_values() -> None:
    assert {member.value for member in EvidenceState} == {
        "verified",
        "not_verified",
        "unavailable",
        "contradictory",
        "failed",
        "incomplete",
        "unknown",
    }


def test_category_has_exactly_seven_values() -> None:
    assert {member.value for member in Category} == {
        "mechanical",
        "procedural",
        "creation_time",
        "correctness",
        "security",
        "architectural",
        "evidence",
    }


# -- Every dataclass is frozen --------------------------------------------------
def test_location_is_frozen() -> None:
    location = Location(path="a.py", line=1)
    try:
        location.path = "b.py"  # type: ignore[misc]
    except dataclasses.FrozenInstanceError:
        pass
    else:
        raise AssertionError("Location must be frozen")


def test_finding_is_frozen_and_shaped() -> None:
    location = Location(path="a.py", line=None)
    remedy = Remedy(tool="black", paths=("a.py",), check="lint")
    finding = Finding(
        id="f1",
        categories=frozenset({Category.MECHANICAL}),
        extra_tags=frozenset({"performance"}),
        location=location,
        evidence="observed X",
        severity="minor",
        remedy=remedy,
        behaviour_changing=False,
        source_attempt="attempt-1",
    )
    assert finding.categories == {Category.MECHANICAL}
    assert finding.extra_tags == {"performance"}
    assert finding.remedy is remedy
    try:
        finding.evidence = "changed"  # type: ignore[misc]
    except dataclasses.FrozenInstanceError:
        pass
    else:
        raise AssertionError("Finding must be frozen")


def test_finding_categories_and_extra_tags_are_never_merged() -> None:
    finding = Finding(
        id="f2",
        categories=frozenset({Category.SECURITY}),
        extra_tags=frozenset({"performance", "flaky"}),
        location=Location(path="b.py", line=3),
        evidence="e",
        severity="major",
        remedy=None,
        behaviour_changing=None,
        source_attempt="attempt-2",
    )
    assert finding.categories.isdisjoint(finding.extra_tags)
    assert "performance" not in finding.categories
    assert Category.SECURITY not in finding.extra_tags


def test_remedy_paths_is_a_tuple_of_exact_files() -> None:
    remedy = Remedy(tool="ruff", paths=("src/a.py", "src/b.py"), check="ruff-check")
    assert remedy.paths == ("src/a.py", "src/b.py")
    assert isinstance(remedy.paths, tuple)


def test_injection_attempt_is_frozen() -> None:
    attempt = InjectionAttempt(field="body", span_hash="a" * 64, reason="attempted override")
    try:
        attempt.reason = "x"  # type: ignore[misc]
    except dataclasses.FrozenInstanceError:
        pass
    else:
        raise AssertionError("InjectionAttempt must be frozen")


def test_harness_identity_fields() -> None:
    identity = HarnessIdentity(harness="claude-code", model="opus", provider="anthropic")
    assert (identity.harness, identity.model, identity.provider) == (
        "claude-code",
        "opus",
        "anthropic",
    )


def test_verdict_shape() -> None:
    identity = HarnessIdentity(harness="h", model="m", provider="p")
    verdict = Verdict(
        obligations={"ob1": EvidenceState.VERIFIED},
        findings=(),
        injection_attempts=(),
        identity=identity,
        protocol_version="1",
    )
    assert verdict.obligations == {"ob1": EvidenceState.VERIFIED}
    assert verdict.findings == ()
    assert verdict.injection_attempts == ()
    assert verdict.protocol_version == "1"


def test_valid_wraps_a_verdict() -> None:
    identity = HarnessIdentity(harness="h", model="m", provider="p")
    verdict = Verdict(
        obligations={}, findings=(), injection_attempts=(), identity=identity, protocol_version="1"
    )
    valid = Valid(verdict=verdict)
    assert valid.verdict is verdict


def test_invalid_wraps_a_reasons_tuple() -> None:
    invalid = Invalid(reasons=("empty_payload",))
    assert invalid.reasons == ("empty_payload",)
    assert isinstance(invalid.reasons, tuple)


def test_obligation_shape() -> None:
    obligation = Obligation(
        id="ob1",
        paths=("src/**/*.py",),
        required_for=frozenset({"high"}),
        evidence="tests pass",
    )
    assert obligation.paths == ("src/**/*.py",)
    assert obligation.required_for == {"high"}

