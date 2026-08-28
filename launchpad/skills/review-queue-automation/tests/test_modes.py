#!/usr/bin/env python3
"""Tests for strategy execution modes.

The property that motivates the module: a participant that produced no valid
verdict, timed out, or duplicates a provider family already counted is NOT
agreement. Counting slot files can see none of those.

A deliberate boundary is asserted here too: for the mode the panel actually
executes, a DISAGREEING panel is still a panel that happened. Folding agreement
into participation would turn a material disagreement into a degraded draft
instead of the human escalation `assurance.classify` already produces.
"""

from __future__ import annotations

import json
import pathlib
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scripts"))

import panel  # noqa: E402
from modes import (  # noqa: E402
    DEGRADED,
    HUMAN,
    MODES,
    RETRYABLE,
    SUCCESS,
    ModeError,
    Participant,
    aggregate,
    for_profile,
    mode_for,
    spec_for,
)
from strategies import STRATEGIES, VALID_AGGREGATIONS  # noqa: E402


def _p(role: str, model: str, family: str, *, valid: bool = True,
       signal: str = "SUPPORTED", timed_out: bool = False) -> Participant:
    return Participant(role=role, model=model, provider_family=family,
                       valid=valid, signal=signal, timed_out=timed_out)


def _pair(**kwargs) -> list[Participant]:
    second = {"signal": "SUPPORTED", "valid": True, "timed_out": False}
    second.update(kwargs)
    return [_p("reviewer_a", "opus", "anthropic"),
            _p("reviewer_b", "sol", "openai", **second)]


# ---- participation discounting ---------------------------------------------
def test_two_independent_valid_participants_satisfy_the_mode() -> None:
    result = aggregate(for_profile("challenger", 2), _pair())
    assert result.status == SUCCESS
    assert len(result.counted) == 2
    assert result.discounted == ()


def test_second_participant_from_the_same_family_is_not_agreement() -> None:
    participants = [_p("reviewer_a", "opus", "anthropic"),
                    _p("reviewer_b", "sonnet", "anthropic")]
    result = aggregate(for_profile("challenger", 2), participants)
    assert result.status == DEGRADED
    assert len(result.counted) == 1
    assert result.discounted[0][0] == "sonnet"
    assert "same provider family" in result.discounted[0][1]


def test_invalid_verdict_is_not_agreement() -> None:
    result = aggregate(for_profile("challenger", 2), _pair(valid=False))
    assert result.status == DEGRADED
    assert result.discounted == (("sol", "no schema-valid verdict"),)


def test_timed_out_participant_is_not_agreement() -> None:
    result = aggregate(for_profile("challenger", 2), _pair(timed_out=True))
    assert result.status == DEGRADED
    assert result.discounted == (("sol", "timed out"),)


def test_timeout_is_reported_as_timeout_even_though_it_is_also_invalid() -> None:
    """Discount reasons must name the real cause, not the first check that trips."""
    result = aggregate(for_profile("challenger", 2), _pair(valid=False, timed_out=True))
    assert result.discounted == (("sol", "timed out"),)


def test_no_valid_participant_is_retryable_not_degraded() -> None:
    participants = [_p("reviewer_a", "opus", "anthropic", valid=False),
                    _p("reviewer_b", "sol", "openai", valid=False)]
    result = aggregate(for_profile("challenger", 2), participants)
    assert result.status == RETRYABLE
    assert result.counted == ()


# ---- the deliberate participation / agreement boundary ---------------------
def test_disagreement_does_not_break_participation_for_the_executed_mode() -> None:
    result = aggregate(for_profile("challenger", 2), _pair(signal="DEFECTS_FOUND"))
    assert result.status == SUCCESS, (
        "a disagreeing panel still HAPPENED; assurance.classify decides what the "
        "disagreement means, and escalating here would produce a degraded draft "
        "instead of a human escalation"
    )
    assert set(result.signals) == {"SUPPORTED", "DEFECTS_FOUND"}


def test_modes_that_require_unanimity_do_escalate_on_disagreement() -> None:
    participants = [_p("key_a", "opus", "anthropic"),
                    _p("key_b", "sol", "openai", signal="DEFECTS_FOUND")]
    result = aggregate("dual_key", participants)
    assert result.status == HUMAN
    assert "disagree" in result.reason


# ---- required verifier -----------------------------------------------------
def test_generator_without_a_valid_verifier_is_a_human_matter() -> None:
    result = aggregate("generator_verifier", [_p("generator", "opus", "anthropic")])
    assert result.status == HUMAN
    assert result.reason == "verifier produced no valid verdict"


def test_debate_without_an_adjudicator_degrades_because_two_views_exist() -> None:
    participants = [_p("proponent", "opus", "anthropic"),
                    _p("opponent", "sol", "openai")]
    result = aggregate("debate_adjudicate", participants)
    assert result.status == DEGRADED
    assert result.reason == "adjudicator produced no valid verdict"


def test_dual_key_has_no_partial_credit() -> None:
    result = aggregate("dual_key", [_p("key_a", "opus", "anthropic")])
    assert result.status == HUMAN
    assert "requires 2 independent participants" in result.reason


def test_every_declared_mode_reaches_a_named_status() -> None:
    for name, spec in MODES.items():
        full = [_p(role, f"m{idx}", f"family{idx}")
                for idx, role in enumerate(spec.roles)]
        assert aggregate(name, full).status == SUCCESS, name
        assert aggregate(name, []).status in {RETRYABLE, HUMAN, DEGRADED}, name


def test_unknown_mode_is_rejected() -> None:
    try:
        spec_for("telepathy")
    except ModeError as exc:
        assert "unknown execution mode" in str(exc)
    else:
        raise AssertionError("an unknown mode must be rejected")


# ---- mapping ---------------------------------------------------------------
def test_profile_selects_the_mode_the_panel_can_execute() -> None:
    assert for_profile("single", 1).name == "single"
    assert for_profile("challenger", 2).name == "independent_review"
    # required is authoritative over a mislabelled independence string
    assert for_profile("challenger", 1).name == "single"


def test_strategy_aggregation_maps_onto_an_execution_mode() -> None:
    assert mode_for("direct_analysis").name == "single"
    assert mode_for("independent_parallel").name == "dual_key"
    assert mode_for("debate").name == "debate_adjudicate"
    assert mode_for("sequential_refinement").name == "generator_verifier"
    assert mode_for(None).name == "single"
    assert mode_for("no-such-strategy").name == "single"


def test_every_strategy_aggregation_is_valid_and_mapped() -> None:
    """The registry declared VALID_AGGREGATIONS and never enforced it; three rows
    had drifted outside it, so no execution mode knew how to run them."""
    used = {strategy.aggregation for strategy in STRATEGIES}
    assert used <= VALID_AGGREGATIONS
    for strategy in STRATEGIES:
        assert mode_for(strategy.name).name in MODES, strategy.name


# ---- panel integration -----------------------------------------------------
def _write_slot(artifacts: pathlib.Path, slot: str, family: str, *,
                signal: str = "SUPPORTED") -> None:
    (artifacts / slot).write_text(json.dumps({
        "signal": signal, "recommendation": "clean", "summary": "s",
        "findings": [], "good": ["x"], "missing_evidence": [],
    }))
    (artifacts / slot).with_suffix(".meta.json").write_text(json.dumps({
        "slot": slot, "model": f"model-{family}", "provider_family": family,
        "trusted": True,
    }))


def test_panel_reads_provider_family_from_the_trusted_sidecar() -> None:
    artifacts = pathlib.Path(tempfile.mkdtemp())
    _write_slot(artifacts, "review-A.txt", "anthropic")
    _write_slot(artifacts, "review-B.txt", "openai")
    participants = panel._mode_participants(artifacts, 2)
    assert [p.provider_family for p in participants] == ["anthropic", "openai"]
    assert all(p.valid for p in participants)
    assert aggregate(for_profile("challenger", 2), participants).status == SUCCESS


def test_panel_participation_rejects_two_slots_from_one_family() -> None:
    """Independence is verified from machinery-written metadata, so a same-family
    pair cannot satisfy a two-participant panel even if both slots are filled."""
    artifacts = pathlib.Path(tempfile.mkdtemp())
    _write_slot(artifacts, "review-A.txt", "anthropic")
    _write_slot(artifacts, "review-B.txt", "anthropic")
    result = aggregate(for_profile("challenger", 2), panel._mode_participants(artifacts, 2))
    assert result.status == DEGRADED
    assert len(result.counted) == 1


def test_panel_missing_slot_is_an_invalid_participant_with_a_reason() -> None:
    artifacts = pathlib.Path(tempfile.mkdtemp())
    _write_slot(artifacts, "review-A.txt", "anthropic")
    participants = panel._mode_participants(artifacts, 2)
    assert len(participants) == 2
    assert participants[1].valid is False
    result = aggregate(for_profile("challenger", 2), participants)
    assert result.discounted[0][1] == "no schema-valid verdict"


def test_panel_tolerates_an_unreadable_sidecar() -> None:
    """A corrupt sidecar must not crash the panel; the slot simply claims no family."""
    artifacts = pathlib.Path(tempfile.mkdtemp())
    _write_slot(artifacts, "review-A.txt", "anthropic")
    (artifacts / "review-A.meta.json").write_text("{not json")
    participants = panel._mode_participants(artifacts, 1)
    assert participants[0].valid is True
    assert participants[0].provider_family == ""
