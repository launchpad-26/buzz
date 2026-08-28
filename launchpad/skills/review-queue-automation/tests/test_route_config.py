#!/usr/bin/env python3
"""Tests that routing and panel execution share ONE candidate configuration.

Regression guard for a dead-config bug: `routing.py` read `models.{claude,codex,
openrouter,economical}`, the shipped example declared a top-level `routes`
section, and `panel.py` executed from `models.{primary,secondary}`. Three schemes,
two never read — so `resolve_route` reported "no model available" on a config with
six fully specified models.
"""

from __future__ import annotations

import json
import pathlib
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scripts"))

from common import State  # noqa: E402
from routing import _routes_from_config, resolve_route  # noqa: E402

SKILL_ROOT = pathlib.Path(__file__).resolve().parent.parent
EXAMPLE = SKILL_ROOT / "config.example.json"


def _example() -> dict:
    return json.loads(EXAMPLE.read_text(encoding="utf-8"))


def _canonical_cfg() -> dict:
    return {
        "models": {
            "primary": [
                {"runner": "claude", "selector": "opus", "provider_family": "anthropic",
                 "capability": "frontier", "efforts": ["high"]},
                {"runner": "omp", "selector": "openrouter/z-ai/glm-5.3-flash",
                 "provider_family": "z-ai-openrouter", "capability": "frontier",
                 "efforts": ["high"]},
            ],
            "secondary": [
                {"runner": "codex", "selector": "gpt-5.6-sol", "provider_family": "openai",
                 "capability": "frontier", "efforts": ["high"]},
                {"runner": "omp", "selector": "openrouter/cheap/model",
                 "provider_family": "cheap-openrouter", "capability": "economy",
                 "efforts": ["medium"]},
            ],
        }
    }


# -- the shipped example must actually be routable -----------------------
def test_example_config_has_no_dead_routes_section() -> None:
    assert "routes" not in _example(), (
        "a top-level `routes` section is read by nothing and misleads operators"
    )


def test_example_config_resolves_to_a_real_model() -> None:
    """The regression: this previously returned 'human' with 6 models configured."""
    run = resolve_route(_example(), "review")
    assert run.final != "human", "the shipped example must resolve to a real model"
    assert run.resolved, "a resolution must record the route it chose"


def test_example_config_populates_every_expected_rung() -> None:
    rungs = _routes_from_config(_example())
    assert len(rungs["claude"]) >= 1
    assert len(rungs["codex"]) >= 1
    assert len(rungs["openrouter"]) >= 1


# -- rungs derive from the pools panel actually executes ----------------
def test_rungs_derive_from_canonical_pools() -> None:
    rungs = _routes_from_config(_canonical_cfg())
    assert [e["selector"] for e in rungs["claude"]] == ["opus"]
    assert [e["selector"] for e in rungs["codex"]] == ["gpt-5.6-sol"]
    assert [e["selector"] for e in rungs["openrouter"]] == ["openrouter/z-ai/glm-5.3-flash"]
    # an explicitly economy-capability candidate is a last-resort rung
    assert [e["selector"] for e in rungs["economical"]] == ["openrouter/cheap/model"]


def test_subscription_first_order_from_canonical_pools() -> None:
    run = resolve_route(_canonical_cfg(), "review")
    assert run.final == "opus"
    assert run.resolved[0].provider == "anthropic"
    assert run.resolved[0].fallback_position == 0


def test_unknown_runner_is_not_routed() -> None:
    cfg = {"models": {"primary": [
        {"runner": "telepathy", "selector": "x", "provider_family": "f"}
    ]}}
    rungs = _routes_from_config(cfg)
    assert all(not entries for entries in rungs.values())
    assert resolve_route(cfg, "review").final == "human"


def test_explicit_rungs_still_win_when_present() -> None:
    """An operator may pin an exact ladder; that must override derivation."""
    cfg = {
        "models": {
            "claude": [{"model": "pinned-claude", "provider": "anthropic"}],
            "primary": [{"runner": "omp", "selector": "derived", "provider_family": "x"}],
        }
    }
    rungs = _routes_from_config(cfg)
    assert [e["model"] for e in rungs["claude"]] == ["pinned-claude"]
    assert rungs["openrouter"] == [], "derivation must not run when a ladder is pinned"


def test_cooldown_advances_to_the_next_rung() -> None:
    """Subscription-first is rung-ordered: claude -> codex -> openrouter."""
    state = State({"state_dir": tempfile.mkdtemp()})
    try:
        state.db.execute(
            "INSERT INTO providers(key,unavailable_until,last_error,updated_at) "
            "VALUES(?,?,?,?)",
            ("anthropic:opus", "2999-01-01T00:00:00Z", "quota", "2026-01-01T00:00:00Z"),
        )
        state.db.commit()
        run = resolve_route(_canonical_cfg(), "review", state=state)
        assert run.final == "gpt-5.6-sol", run.final
        assert run.resolved[0].provider == "openai"
    finally:
        state.close()


def test_both_subscriptions_cooled_falls_to_openrouter() -> None:
    state = State({"state_dir": tempfile.mkdtemp()})
    try:
        for key in ("anthropic:opus", "openai:gpt-5.6-sol"):
            state.db.execute(
                "INSERT INTO providers(key,unavailable_until,last_error,updated_at) "
                "VALUES(?,?,?,?)",
                (key, "2999-01-01T00:00:00Z", "quota", "2026-01-01T00:00:00Z"),
            )
        state.db.commit()
        run = resolve_route(_canonical_cfg(), "review", state=state)
        assert run.final == "openrouter/z-ai/glm-5.3-flash", run.final
    finally:
        state.close()


def test_all_unavailable_escalates_to_human() -> None:
    state = State({"state_dir": tempfile.mkdtemp()})
    try:
        for key in ("anthropic:opus", "z-ai-openrouter:openrouter/z-ai/glm-5.3-flash",
                    "openai:gpt-5.6-sol", "cheap-openrouter:openrouter/cheap/model"):
            state.db.execute(
                "INSERT INTO providers(key,unavailable_until,last_error,updated_at) "
                "VALUES(?,?,?,?)",
                (key, "2999-01-01T00:00:00Z", "quota", "2026-01-01T00:00:00Z"),
            )
        state.db.commit()
        run = resolve_route(_canonical_cfg(), "review", state=state)
        assert run.final == "human"
    finally:
        state.close()


def test_provider_family_is_used_as_the_cooldown_identity() -> None:
    """Canonical pools carry `provider_family`, not `provider`."""
    run = resolve_route(_canonical_cfg(), "review")
    assert run.resolved[0].provider == "anthropic"


# -- selection metadata surfaces errors instead of hiding them ---------
def test_selection_context_records_errors_rather_than_swallowing() -> None:
    import panel
    from assurance import Profile

    class Boom:
        def as_dict(self):
            raise RuntimeError("profile exploded")

    name, log = panel._selection_context({}, "o/r", 1, "incoming_review", Boom())
    assert name == "direct_analysis"  # safe default preserved
    assert "selection_error" in log, "a selection failure must be recorded, not hidden"
    assert "RuntimeError" in log["selection_error"]


def test_selection_context_succeeds_on_a_real_config() -> None:
    import panel
    from assurance import Profile

    name, log = panel._selection_context(
        _canonical_cfg(), "o/r", 1, "incoming_review", Profile()
    )
    assert name
    assert "selection_error" not in log
    assert log["resolved_model"]["final"] == "opus"
