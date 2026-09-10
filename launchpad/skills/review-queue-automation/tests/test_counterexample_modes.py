#!/usr/bin/env python3
"""Counterexample tests for strategy activation and execution modes.

The property under test is one sentence: a participant that did not really
produce an independent, schema-valid verdict must never be counted as agreement.
Everything below is a way of not producing one — absent, invalid, timed out, or
from the same provider family as a slot already counted — and the assertion is
always that the aggregate is NOT `success`.

Strategy activation is the other half: a strategy that declares two independent
participants must not be executed by a mode that is satisfied by one. So the
strategy->mode mapping is asserted to be total, and the modes are asserted to
keep their minimums.

Sibling ownership: `strategies.py` belongs to the runtime lane. These
counterexamples live in a new file rather than in `test_strategy_metadata.py`
or `test_modes.py`.
"""

from __future__ import annotations

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import modes as modesmod  # noqa: E402
import strategies as stratmod  # noqa: E402
from modes import (  # noqa: E402
    DEBATE_ADJUDICATE,
    DEGRADED,
    DUAL_KEY,
    EXECUTOR_VERIFIER,
    GENERATOR_VERIFIER,
    HUMAN,
    INDEPENDENT_REVIEW,
    RETRYABLE,
    SINGLE,
    SUCCESS,
    ModeError,
    Participant,
    aggregate,
)


def _p(role: str, model: str, family: str, **over) -> Participant:
    kwargs = {"valid": True, "signal": "SUPPORTED", "timed_out": False}
    kwargs.update(over)
    return Participant(role=role, model=model, provider_family=family, **kwargs)


#: Two genuinely independent, valid, agreeing reviewers.
def _independent_pair() -> list[Participant]:
    return [_p("reviewer_a", "claude-opus-4-5", "anthropic"),
            _p("reviewer_b", "gpt-5.6-sol", "openai")]


# --------------------------------------------------------------------------
# 1. controls
# --------------------------------------------------------------------------


def test_the_control_a_real_independent_panel_succeeds() -> None:
    """Without this, an aggregator that returned HUMAN for everything would pass
    every counterexample below and review nothing."""
    result = aggregate(INDEPENDENT_REVIEW, _independent_pair())
    assert result.status == SUCCESS, result.reason
    assert len(result.counted) == 2
    assert result.discounted == ()


def test_the_control_each_multi_participant_mode_can_be_satisfied() -> None:
    cases = {
        SINGLE: [_p("reviewer", "m1", "anthropic")],
        INDEPENDENT_REVIEW: _independent_pair(),
        GENERATOR_VERIFIER: [_p("generator", "m1", "anthropic"), _p("verifier", "m2", "openai")],
        EXECUTOR_VERIFIER: [_p("executor", "m1", "anthropic"), _p("verifier", "m2", "openai")],
        DUAL_KEY: [_p("key_a", "m1", "anthropic"), _p("key_b", "m2", "openai")],
        DEBATE_ADJUDICATE: [_p("proponent", "m1", "anthropic"), _p("opponent", "m2", "openai"),
                            _p("adjudicator", "m3", "google")],
    }
    for mode, participants in cases.items():
        assert aggregate(mode, participants).status == SUCCESS, mode


# --------------------------------------------------------------------------
# 2. a participant that did not produce a verdict is not agreement
# --------------------------------------------------------------------------


def test_a_missing_participant_is_never_agreement() -> None:
    for mode in (INDEPENDENT_REVIEW, GENERATOR_VERIFIER, EXECUTOR_VERIFIER, DUAL_KEY):
        spec = modesmod.spec_for(mode)
        one = [_p(spec.roles[0], "claude-opus-4-5", "anthropic")]
        result = aggregate(mode, one)
        assert result.status != SUCCESS, (mode, result.reason)
        assert len(result.counted) < spec.min_counted
    # Debate without its third seat is likewise not a satisfied panel.
    partial = [_p("proponent", "m1", "anthropic"), _p("opponent", "m2", "openai")]
    assert aggregate(DEBATE_ADJUDICATE, partial).status != SUCCESS


def test_an_invalid_verdict_is_discounted_not_counted() -> None:
    """`valid` comes from schema validation, never from the model's own claim. An
    unparseable reviewer that still "voted" would be a fabricated second opinion."""
    for mode in (SINGLE, INDEPENDENT_REVIEW, DUAL_KEY):
        participants = [
            _p("reviewer_a", "claude-opus-4-5", "anthropic", valid=False, signal="SUPPORTED"),
            _p("reviewer_b", "gpt-5.6-sol", "openai", valid=False, signal="SUPPORTED"),
        ]
        result = aggregate(mode, participants)
        assert result.status != SUCCESS, mode
        assert result.counted == (), mode
        assert all("no schema-valid verdict" == why for _label, why in result.discounted), mode
    # One valid + one invalid is still not an independent pair.
    mixed = [_p("reviewer_a", "claude-opus-4-5", "anthropic"),
             _p("reviewer_b", "gpt-5.6-sol", "openai", valid=False)]
    assert aggregate(INDEPENDENT_REVIEW, mixed).status != SUCCESS


def test_a_timed_out_participant_is_discounted_even_when_it_left_a_signal() -> None:
    """A partial response that arrived after the deadline is not a review. A
    timed-out slot carrying `signal="SUPPORTED"` is the exact shape of an
    accidental rubber stamp."""
    participants = [
        _p("reviewer_a", "claude-opus-4-5", "anthropic"),
        _p("reviewer_b", "gpt-5.6-sol", "openai", timed_out=True, signal="SUPPORTED"),
    ]
    result = aggregate(INDEPENDENT_REVIEW, participants)
    assert result.status != SUCCESS
    assert ("gpt-5.6-sol", "timed out") in result.discounted
    assert "gpt-5.6-sol" not in result.counted


def test_a_timed_out_participant_is_discounted_before_its_validity_is_consulted() -> None:
    """Order matters: a slot marked both valid and timed out must not slip through
    on the validity branch."""
    result = aggregate(SINGLE, [_p("reviewer", "m1", "anthropic", timed_out=True, valid=True)])
    assert result.status == RETRYABLE
    assert result.counted == ()
    assert result.discounted == (("m1", "timed out"),)


def test_no_participant_at_all_is_retryable_never_success() -> None:
    for mode in sorted(modesmod.MODES):
        result = aggregate(mode, [])
        assert result.status != SUCCESS, mode
        assert result.counted == (), mode


# --------------------------------------------------------------------------
# 3. provider independence
# --------------------------------------------------------------------------


def test_two_reviewers_from_the_same_provider_family_are_not_two_reviewers() -> None:
    """Two models behind one provider share weights, outages and blind spots. The
    second is a duplicate opinion, and counting it would manufacture independence
    the panel does not have."""
    same_family = [_p("reviewer_a", "claude-opus-4-5", "anthropic"),
                   _p("reviewer_b", "claude-sonnet-4-5", "anthropic")]
    for mode in (INDEPENDENT_REVIEW, GENERATOR_VERIFIER, EXECUTOR_VERIFIER, DUAL_KEY,
                 DEBATE_ADJUDICATE):
        result = aggregate(mode, same_family)
        assert result.status != SUCCESS, mode
        assert any("same provider family" in why for _l, why in result.discounted), (
            mode, result.discounted
        )


def test_the_same_family_rule_still_applies_to_the_third_seat() -> None:
    trio = [_p("proponent", "m1", "anthropic"), _p("opponent", "m2", "openai"),
            _p("adjudicator", "m3", "openai")]
    result = aggregate(DEBATE_ADJUDICATE, trio)
    assert result.status != SUCCESS
    assert ("m3", "same provider family as m2 (openai)") in result.discounted


def test_a_mode_that_requires_independence_says_so_in_its_spec() -> None:
    """Guards the guard: if `require_distinct_families` were false everywhere, the
    duplicate-family tests above would be asserting nothing."""
    for mode in (INDEPENDENT_REVIEW, GENERATOR_VERIFIER, EXECUTOR_VERIFIER, DUAL_KEY,
                 DEBATE_ADJUDICATE):
        assert modesmod.spec_for(mode).require_distinct_families, mode


def test_two_unattributed_participants_are_never_called_independent() -> None:
    """A participant with no recorded provider family is unattributable.

    `aggregate` cannot discount what it cannot see: with an empty family there is
    nothing to compare, so both slots are counted. The approval path is the
    backstop that makes that safe — `_distinct_identities` counts only NON-EMPTY
    families, so two unattributed reviewers can never satisfy
    `distinct_reviewers`. Assert the backstop, because that is the guard that
    actually stands between an unattributed pair and an approval."""
    from approval_evaluate import _distinct_identities

    unlabelled = [_p("reviewer_a", "m1", ""), _p("reviewer_b", "m2", "")]
    result = aggregate(modesmod.for_profile("challenger", 2), unlabelled)
    assert not any("same provider family" in why for _l, why in result.discounted)

    _models, families, _completed = _distinct_identities(
        [{"model": "m1", "provider_family": ""}, {"model": "m2", "provider_family": ""}], []
    )
    assert len(families) < 2, families
    # ...and a genuinely attributed pair does reach two, so this is not vacuous.
    _models, families, _completed = _distinct_identities(
        [{"model": "m1", "provider_family": "anthropic"},
         {"model": "m2", "provider_family": "openai"}], []
    )
    assert len(families) == 2


# --------------------------------------------------------------------------
# 4. verifier / unanimity
# --------------------------------------------------------------------------


def test_a_generation_without_its_verifier_is_a_human_matter() -> None:
    """The whole point of generator/verifier is independent confirmation. A
    missing verifier means the verification step did not happen — that is not
    partial credit."""
    for mode, producer in ((GENERATOR_VERIFIER, "generator"), (EXECUTOR_VERIFIER, "executor")):
        two_producers = [_p(producer, "m1", "anthropic"), _p(producer, "m2", "openai")]
        result = aggregate(mode, two_producers)
        assert result.status == HUMAN, (mode, result.status)
        assert "verifier produced no valid verdict" in result.reason


def test_a_verifier_that_timed_out_counts_as_no_verifier() -> None:
    participants = [_p("generator", "m1", "anthropic"),
                    _p("verifier", "m2", "openai", timed_out=True)]
    result = aggregate(GENERATOR_VERIFIER, participants)
    assert result.status == HUMAN
    assert "verifier produced no valid verdict" in result.reason


def test_a_debate_without_its_adjudicator_degrades_and_never_succeeds() -> None:
    trio = [_p("proponent", "m1", "anthropic"), _p("opponent", "m2", "openai"),
            _p("adjudicator", "m3", "google", valid=False)]
    result = aggregate(DEBATE_ADJUDICATE, trio)
    assert result.status == DEGRADED
    assert "adjudicator produced no valid verdict" in result.reason


def test_disagreement_in_a_unanimous_mode_is_escalated_not_averaged() -> None:
    for mode in (INDEPENDENT_REVIEW, DUAL_KEY, GENERATOR_VERIFIER):
        spec = modesmod.spec_for(mode)
        participants = [
            _p(spec.roles[0], "m1", "anthropic", signal="SUPPORTED"),
            _p(spec.roles[1], "m2", "openai", signal="REFUTED"),
        ]
        result = aggregate(mode, participants)
        assert result.status == HUMAN, (mode, result.status)
        assert "disagree" in result.reason or "no valid verdict" in result.reason


def test_dual_key_gives_no_partial_credit() -> None:
    """`allow_degraded` is False for dual key on purpose: one key turning is not
    half an authorization."""
    assert modesmod.spec_for(DUAL_KEY).allow_degraded is False
    result = aggregate(DUAL_KEY, [_p("key_a", "m1", "anthropic")])
    assert result.status == HUMAN
    assert result.status != DEGRADED


# --------------------------------------------------------------------------
# 5. strategy activation
# --------------------------------------------------------------------------


def test_an_unknown_execution_mode_is_rejected_not_defaulted() -> None:
    for bogus in ("", "panel", "SINGLE", "independent-review", "consensus"):
        try:
            modesmod.spec_for(bogus)
        except ModeError as exc:
            assert bogus in str(exc) or "unknown execution mode" in str(exc)
        else:  # pragma: no cover
            raise AssertionError(f"spec_for({bogus!r}) must raise")


def test_every_registered_strategy_maps_to_an_explicit_execution_mode() -> None:
    """`_AGGREGATION_MODE` falls back to SINGLE for an unmapped aggregation. A
    `consensus` strategy silently executed as a one-reviewer panel would drop an
    independence requirement without a trace, so the mapping must be total."""
    aggregations = {s.aggregation for s in stratmod.STRATEGIES}
    unmapped = aggregations - set(modesmod._AGGREGATION_MODE)
    assert unmapped == set(), f"aggregations with no execution mode: {sorted(unmapped)}"
    assert aggregations <= stratmod.VALID_AGGREGATIONS


def test_a_multi_participant_strategy_never_executes_as_a_single_reviewer() -> None:
    for strategy in stratmod.STRATEGIES:
        spec = modesmod.mode_for(strategy.name)
        if len(strategy.roles) >= 2:
            assert spec.min_counted >= 2, (strategy.name, spec.name)
            assert spec.require_distinct_families, (strategy.name, spec.name)


def test_an_unknown_strategy_name_does_not_activate_a_multi_seat_mode() -> None:
    """An unrecognised name must fall back to the *narrowest* mode, never to one
    whose completion the panel cannot actually verify."""
    for bogus in ("", None, "consensus", "independent-parallel", "IndependentParallel"):
        spec = modesmod.mode_for(bogus)
        assert spec.name == SINGLE, bogus


def test_a_profile_demanding_independence_never_yields_a_single_seat_mode() -> None:
    for independence in ("challenger", "panel", "unknown-value"):
        for required in (2, 3, 5):
            spec = modesmod.for_profile(independence, required)
            assert spec.name == INDEPENDENT_REVIEW, (independence, required)
            assert spec.min_counted >= max(2, required), (independence, required)
            assert spec.require_distinct_families
    # ...and the single-seat case is genuinely reachable, so the above is not
    # vacuously true.
    assert modesmod.for_profile("single", 1).name == SINGLE


def test_a_profile_mode_is_not_satisfied_by_fewer_participants_than_it_requires() -> None:
    spec = modesmod.for_profile("panel", 3)
    two = [_p("reviewer_a", "m1", "anthropic"), _p("reviewer_b", "m2", "openai")]
    result = aggregate(spec, two)
    assert result.status != SUCCESS
    assert "2/3" in result.reason


def test_candidate_restriction_is_honoured_when_selecting_a_strategy() -> None:
    """A caller that narrows the candidate set (e.g. by budget) must not have a
    wider strategy selected behind its back."""
    signals = {"specialist_need": True, "required_independence": "panel", "risk": "high"}
    chosen, reason = stratmod.select_strategy(signals)
    assert chosen.name == "specialist_panel" and reason == "specialist_need"
    narrowed, reason = stratmod.select_strategy(signals, candidates=["direct_analysis"])
    assert narrowed.name == "direct_analysis"
    assert reason == "specialist_need"  # the reason is still the real signal


def test_selection_is_deterministic_for_identical_signals() -> None:
    """A non-deterministic selector would make every other property here
    unreproducible."""
    signals = {"risk": "high", "complexity": 4, "required_independence": "challenger",
               "prior_disagreement": True, "specialist_need": False}
    first = stratmod.select_strategy(dict(signals))
    for _ in range(5):
        assert stratmod.select_strategy(dict(signals)) == first
