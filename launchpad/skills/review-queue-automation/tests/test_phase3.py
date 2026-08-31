#!/usr/bin/env python3
"""Phase 3 tests: named reasoning strategies and subscription-first model routing.

Deterministic; no GitHub, no real models, no network.
"""

from __future__ import annotations

import pathlib
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scripts"))

from common import State  # noqa: E402
from routing import ResolvedRoute, resolve_route  # noqa: E402
from strategies import (  # noqa: E402
    STRATEGIES,
    STRATEGY_BY_NAME,
    available_strategies,
    select_strategy,
)


def test_twelve_strategies_registered() -> None:
    names = available_strategies()
    assert len(names) == 12
    required = {
        "direct_analysis", "decomposition", "checklist", "hypothesis_testing",
        "adversarial", "debate", "independent_parallel", "specialist_panel",
        "sequential_refinement", "critique_revision", "evidence_synthesis",
        "uncertainty_calibration",
    }
    assert required <= set(names)


def test_each_strategy_has_required_fields() -> None:
    for s in STRATEGIES:
        assert s.roles
        assert s.aggregation in {"single", "consensus", "majority", "unanimous",
                                 "panel_adjudicated", "sequenced", "checklist_score",
                                 "hypothesis_register", "calibrated"}
        assert s.output_schema and s.disagreement_handling and s.model_route
        assert s.budget_tokens > 0
        assert s.timeout_seconds > 0


def test_selection_is_deterministic() -> None:
    sig = {"risk": "high", "complexity": 5, "required_independence": "challenger",
           "prior_disagreement": False}
    a, reason_a = select_strategy(sig)
    b, reason_b = select_strategy(sig)
    assert a.name == b.name and reason_a == reason_b


def test_specialist_and_disagreement_signals() -> None:
    # specialist need => specialist panel over direct
    s1, r1 = select_strategy({"specialist_need": True})
    assert s1.name == "specialist_panel"
    # prior disagreement => debate/independent
    s2, r2 = select_strategy({"prior_disagreement": True})
    assert s2.name in {"debate", "independent_parallel", "adversarial"}


def test_unknown_strategy_candidate_falls_back() -> None:
    s, _ = select_strategy({}, candidates=["nope", "checklist"])
    assert s.name == "checklist"
    s2, _ = select_strategy({"risk": "high"}, candidates=["nope"])
    assert s2.name == "direct_analysis"  # safest default


# ---- routing -----------------------------------------------------------
def _routing_cfg() -> dict:
    return {
        "models": {
            "claude": [{"model": "claude-sonnet-4", "provider": "anthropic"}],
            "codex": [{"model": "gpt-5.6-sol", "provider": "openai"}],
            "openrouter": [{"model": "deepseek-v4-flash", "provider": "openrouter"}],
            "economical": [{"model": "economy-1", "provider": "economical"}],
        }
    }


def test_subscription_first_order() -> None:
    run = resolve_route(_routing_cfg(), "review")
    assert run.final == "claude-sonnet-4"
    assert run.resolved[0].provider == "anthropic"
    assert run.resolved[0].fallback_position == 0
    assert run.requested_alias == "review"


def test_fallback_when_first_unavailable() -> None:
    state = State({"state_dir": tempfile.mkdtemp()})
    try:
        state.db.execute(
            "INSERT INTO providers(key,unavailable_until,last_error,updated_at) VALUES(?,?,?,?)",
            ("anthropic:claude-sonnet-4", "2999-01-01T00:00:00+00:00", "cooldown", "2026-01-01T00:00:00+00:00"),
        )
        state.db.commit()
        run = resolve_route(_routing_cfg(), "review", state=state)
        assert run.final == "gpt-5.6-sol", run.final
        assert run.resolved[0].provider == "openai"
        assert run.resolved[0].fallback_position == 1
    finally:
        state.close()


def test_exhaustion_yields_human_fallback() -> None:
    state = State({"state_dir": tempfile.mkdtemp()})
    try:
        for pair in (("anthropic","claude-sonnet-4"),("openai","gpt-5.6-sol"),
                     ("openrouter","deepseek-v4-flash"),("economical","economy-1")):
            state.db.execute(
                "INSERT INTO providers(key,unavailable_until,last_error,updated_at) VALUES(?,?,?,?) "
                "ON CONFLICT(key) DO UPDATE SET unavailable_until=excluded.unavailable_until",
                (f"{pair[0]}:{pair[1]}", "2999-01-01T00:00:00+00:00", "down", "2026-01-01T00:00:00+00:00"),
            )
        state.db.commit()
        run = resolve_route(_routing_cfg(), "review", state=state)
        assert run.final == "human"
        assert not run.attempted  # no model was available to attempt
    finally:
        state.close()


def test_no_fallback_loop_same_provider() -> None:
    # all openrouter entries share one provider; only one may be selected, never dup
    cfg = {"models": {"openrouter": [
        {"model": "m1", "provider": "openrouter"},
        {"model": "m2", "provider": "openrouter"},
    ]}}
    run = resolve_route(cfg, "x")
    assert run.final == "m1"
    assert len(run.attempted) == 1  # no duplicate same-provider selection


def test_resolved_route_log_schema() -> None:
    run = resolve_route(_routing_cfg(), "review")
    d = run.as_dict()
    assert d["requested_alias"] == "review"
    assert d["resolved"][0]["provider"] == "anthropic"
    assert "final" in d and "attempted" in d


def test_provider_hint_prefers_that_rung() -> None:
    run = resolve_route(_routing_cfg(), "x", provider_hint="openrouter")
    assert run.resolved[0].provider == "openrouter"


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