#!/usr/bin/env python3
"""Tests for provider-diverse fallback recipes.

Three properties, each of which was broken before:

1. Subscription routes lead. Candidate order came from config file order, so an
   OpenRouter entry listed first was billed while a paid Claude/Codex
   subscription sat available. `model_route` was declared on all 12 strategies
   and consumed by nothing.
2. A PROVIDER-scoped failure (auth/quota/transport) retires that provider's whole
   family for the run. Previously a family that had just failed was retried with
   a sibling model, costing another full timeout for a correlated outcome.
3. A MODEL-scoped failure (invalid verdict JSON) must NOT retire the family. This
   is the limit on rule 2: sibling models may well emit valid output, and
   dropping the family would needlessly shrink capacity.

Ordering must never lower assurance: a recipe reorders qualified candidates only.
"""

from __future__ import annotations

import json
import pathlib
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scripts"))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import panel  # noqa: E402
from assurance import Profile  # noqa: E402
from common import State  # noqa: E402
from fallback import (  # noqa: E402
    DEFAULT_RECIPE,
    RECIPES,
    order_candidates,
    recipe_for,
    tier_of,
)
from test_regression import REPO, _reviewers, _seed  # noqa: E402

VALID_VERDICT = {
    "signal": "SUPPORTED", "recommendation": "clean", "summary": "s",
    "findings": [], "good": ["x"], "missing_evidence": [],
}


def _entry(selector: str, family: str, *, runner: str = "x", capability: str = "frontier") -> dict:
    return {"runner": runner, "selector": selector, "provider_family": family,
            "capability": capability}


def _cfg(primary: list[dict], secondary: list[dict] | None = None) -> dict:
    return {
        "login": "me", "state_dir": tempfile.mkdtemp(),
        "repos": {REPO: {"path": "/tmp/none"}},
        "assurance": {"large_diff_lines": 700},
        "models": {"cooldown_seconds": 5, "timeout_seconds": 30,
                   "primary": list(primary), "secondary": list(secondary or [])},
    }


def _run(config: dict, number: int, *, fail: set[str] | None = None,
         independence: str = "single") -> dict:
    state = State(config)
    try:
        job = _seed(state, number)
        with _reviewers(fail=fail or set()):
            return panel.run_panel(config, state, REPO, number, "incoming_review",
                                   job, Profile(independence=independence))
    finally:
        state.close()


# ---- tier classification ---------------------------------------------------
def test_tier_is_derived_from_runner_and_economy_is_last_resort() -> None:
    assert tier_of(_entry("opus", "anthropic", runner="claude")) == "claude"
    assert tier_of(_entry("sol", "openai", runner="codex")) == "codex"
    assert tier_of(_entry("or/x", "zai", runner="omp")) == "openrouter"
    # An explicitly economical OpenRouter candidate is a final tier, not a peer
    # of the provider-diverse fallbacks.
    assert tier_of(_entry("or/y", "qwen", runner="omp", capability="economy")) == "economical"


def test_unknown_runner_sorts_last_rather_than_raising() -> None:
    ordered = order_candidates([
        _entry("mystery", "who", runner="not-a-runner"),
        _entry("opus", "anthropic", runner="claude"),
    ])
    assert [entry["selector"] for entry in ordered][0] == "opus"


# ---- recipe selection ------------------------------------------------------
def test_recipe_comes_from_the_strategy_declaration() -> None:
    # direct_analysis declares model_route "preferred"; debate declares "fallback".
    assert recipe_for("direct_analysis").name == "preferred"
    assert recipe_for("debate").name == "fallback"
    assert recipe_for("independent_parallel").name == "diverse"
    assert recipe_for("uncertainty_calibration").name == "economical"


def test_unknown_or_missing_strategy_defaults_to_subscription_first() -> None:
    assert recipe_for(None) is DEFAULT_RECIPE
    assert recipe_for("no-such-strategy") is DEFAULT_RECIPE
    assert DEFAULT_RECIPE.tiers[0] == "claude"


def test_preferred_and_diverse_lead_with_subscriptions() -> None:
    for name in ("preferred", "diverse"):
        assert RECIPES[name].tiers[:2] == ("claude", "codex"), name


def test_second_opinion_recipe_leads_with_a_diverse_tier() -> None:
    """A `fallback` strategy runs after a first view; repeating the same
    subscription route would add cost without adding independence."""
    assert RECIPES["fallback"].tiers[0] == "openrouter"


# ---- ordering --------------------------------------------------------------
def test_ordering_is_stable_within_a_tier_and_adds_or_drops_nothing() -> None:
    entries = [
        _entry("or-first", "zai", runner="omp"),
        _entry("or-second", "qwen", runner="omp"),
        _entry("sol", "openai", runner="codex"),
        _entry("opus", "anthropic", runner="claude"),
    ]
    ordered = order_candidates(entries, RECIPES["preferred"])
    assert [entry["selector"] for entry in ordered] == [
        "opus", "sol", "or-first", "or-second",
    ]
    assert len(ordered) == len(entries)
    assert {id(entry) for entry in ordered} == {id(entry) for entry in entries}


def test_subscription_route_runs_even_when_openrouter_is_configured_first() -> None:
    config = _cfg([
        _entry("openrouter/z-ai/glm", "zai", runner="omp"),
        _entry("opus", "anthropic", runner="claude"),
    ])
    result = _run(config, 601)
    assert result["selected_candidates"] == ["claude:opus"]
    assert result["recipe"] == "preferred"


def test_ordering_never_lowers_the_required_capability() -> None:
    """Reordering must not smuggle in a candidate below the capability floor."""
    config = _cfg([_entry("cheap", "zai", runner="omp", capability="workhorse")])
    state = State(config)
    try:
        job = _seed(state, 602)
        with _reviewers():
            result = panel.run_panel(
                config, state, REPO, 602, "incoming_review", job,
                Profile(capability="frontier", independence="single"),
            )
        assert result["selected_candidates"] == []
        assert result["complete"] is False
    finally:
        state.close()


# ---- failure scope ---------------------------------------------------------
def test_provider_failure_retires_the_whole_family_for_the_run() -> None:
    config = _cfg([
        _entry("opus", "anthropic"),
        _entry("sonnet", "anthropic"),
        _entry("glm", "zai"),
    ])
    result = _run(config, 603, fail={"opus"})
    assert result["failed_families"] == ["anthropic"]
    assert "x:sonnet" not in result["attempted_candidates"], (
        "a sibling of a failed provider must not be attempted"
    )
    assert "x:sonnet" in result["skip"]
    assert result["selected_candidates"] == ["x:glm"]


def test_invalid_verdict_retires_only_that_model_not_its_family() -> None:
    config = _cfg([
        _entry("opus", "anthropic"),
        _entry("sonnet", "anthropic"),
        _entry("glm", "zai"),
    ])
    state = State(config)
    try:
        job = _seed(state, 604)
        original = panel._run_reviewer

        def emit(entry, prompt, out_path, effort, repo_path, timeout):
            if entry["selector"] == "opus":
                out_path.write_text("not json at all")  # model-scoped failure
            else:
                out_path.write_text(json.dumps(VALID_VERDICT))

        panel._run_reviewer = emit
        try:
            result = panel.run_panel(config, state, REPO, 604, "incoming_review",
                                     job, Profile(independence="single"))
        finally:
            panel._run_reviewer = original

        assert result["failed_families"] == []
        assert "x:sonnet" in result["attempted_candidates"]
        assert result["selected_candidates"] == ["x:sonnet"]
    finally:
        state.close()


def test_repeated_provider_failures_do_not_exhaust_other_families() -> None:
    """Every candidate of one broken provider is skipped, and a healthy family
    in a later lane still fills its slot."""
    config = _cfg(
        [_entry("opus", "anthropic"), _entry("sonnet", "anthropic")],
        [_entry("sol", "openai")],
    )
    result = _run(config, 605, fail={"opus", "sonnet"})
    assert result["failed_families"] == ["anthropic"]
    assert result["attempted_candidates"] == ["x:opus", "x:sol"]
    assert result["selected_candidates"] == ["x:sol"]
    assert result["complete"] is True


def test_cross_lane_fallback_verdict_is_not_wasted() -> None:
    """Regression: slots were indexed by LANE, not by fill order.

    When every candidate in the first lane failed and a later lane succeeded, the
    verdict was written to review-B.txt while `_parse_signals` read only the first
    `required` slot files. The panel spent real model tokens, held a valid verdict
    on disk, and still reported `degraded` — so a healthy fallback provider could
    never complete a single-slot panel.
    """
    config = _cfg([_entry("opus", "anthropic")], [_entry("sol", "openai")])
    state = State(config)
    try:
        job = _seed(state, 607)
        with _reviewers(fail={"opus"}):
            result = panel.run_panel(config, state, REPO, 607, "incoming_review",
                                     job, Profile(independence="single"))
        artifacts = state.job_dir(job)
        assert result["selected_candidates"] == ["x:sol"]
        assert (artifacts / "review-A.txt").is_file(), "the fill must occupy slot A"
        assert not (artifacts / "review-B.txt").is_file()
        assert result["signals"] == ["SUPPORTED"]
        assert result["complete"] is True
        assert result["outcome"] == "complete"
    finally:
        state.close()


def test_two_slot_panel_still_fills_both_slots_from_distinct_families() -> None:
    """The fill-order fix must not collapse a two-slot panel into one slot."""
    config = _cfg(
        [_entry("opus", "anthropic"), _entry("glm", "zai")],
        [_entry("sol", "openai")],
    )
    state = State(config)
    try:
        job = _seed(state, 608)
        with _reviewers():
            result = panel.run_panel(config, state, REPO, 608, "incoming_review",
                                     job, Profile(independence="challenger"))
        artifacts = state.job_dir(job)
        assert (artifacts / "review-A.txt").is_file()
        assert (artifacts / "review-B.txt").is_file()
        assert len(result["signals"]) == 2
        assert result["complete"] is True
        families = {entry.split(":")[0] for entry in result["selected_candidates"]}
        assert len(result["selected_candidates"]) == 2 and families
    finally:
        state.close()


def test_attempt_record_names_the_recipe_and_retired_families() -> None:
    """The audit record must explain why a candidate was never tried."""
    config = _cfg([_entry("opus", "anthropic"), _entry("sonnet", "anthropic"),
                   _entry("glm", "zai")])
    result = _run(config, 606, fail={"opus"})
    assert result["strategy"]
    assert result["recipe"] in RECIPES
    assert result["failed_families"] == ["anthropic"]
