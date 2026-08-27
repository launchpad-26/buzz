#!/usr/bin/env python3
"""Tests for immutable alias resolution and model-route shadow locking."""

from __future__ import annotations

import pathlib
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scripts"))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import dispatcher  # noqa: E402
from common import State  # noqa: E402
from model_registry import qualified_route, resolve, route_material_fingerprint  # noqa: E402
from routing import resolve_route  # noqa: E402
from route_probe import OK, TRANSPORT_FAILED, persist_probe_result  # noqa: E402
from test_dispatch_flow import _config, seed_evidence, seed_job  # noqa: E402


def _policy() -> dict:
    return {
        "version": "v1", "authority": {"approve": "disabled"},
        "approval": {"effective_risk_max": 24, "complexity_max": 2, "file_limit": 50,
                     "line_limit": 1000, "approval_rate_max": 0.5},
        "risk": {"bands": {"low": 24, "medium": 99, "high": 100}},
        "human_queue": {"expiry_minutes": 1440},
    }

def _entry(
    selector: str = "gpt-5.6-sol",
    *,
    tools: list[str] | None = None,
    prompt_version: str = "review-v1",
) -> dict:
    return {
        "alias": "CODEX_STRONG", "runner": "codex", "selector": selector,
        "model_version": selector, "provider_family": "openai", "capability": "frontier",
        "efforts": ["high"], "execution_mode": "read_only", "tools": tools or [],
        "prompt_version": prompt_version,
    }


def _cfg(state_dir: str, entry: dict) -> dict:
    cfg = _config("live")
    cfg["state_dir"] = state_dir
    cfg["policy"] = _policy()
    cfg["models"] = {"prompt_version": "review-v1", "primary": [entry], "secondary": []}
    return cfg


def _job(state: State, number: int) -> str:
    jid = seed_job(state, number=number, head=f"h{number}")
    seed_evidence(state, jid)
    return jid


def test_registry_resolves_normalized_native_alias() -> None:
    route = resolve("cod.exe_strong")
    assert route.name == "CODEX_STRONG"
    assert route.runner == "codex"
    assert route.selector == "gpt-5.6-sol"


def test_qualified_route_contains_all_execution_identity_inputs() -> None:
    route = qualified_route(_entry(tools=["read_file@1"]), effort="high", policy_version="v1")
    assert route["alias"] == "CODEX_STRONG"
    assert route["model_version"] == "gpt-5.6-sol"
    assert route["execution_mode"] == "read_only"
    assert route["tools"] == ["read_file@1"]
    assert route["prompt_version"] == "review-v1"
    assert route["policy_version"] == "v1"
    assert len(route["fingerprint"]) == 64


def test_router_records_the_exact_qualified_route_it_selected() -> None:
    config = {"policy": _policy(), "models": {"prompt_version": "review-v1", "primary": [_entry()], "secondary": []}}
    resolved = resolve_route(config, "review", effort="high").resolved[0].qualified
    assert resolved["model"] == "gpt-5.6-sol"
    assert resolved["effort"] == "high"
    assert resolved["prompt_version"] == "review-v1"
    assert resolved["policy_version"] == "v1"


def test_model_slug_prompt_or_tools_change_alters_route_fingerprint() -> None:
    base = {"policy": _policy(), "models": {"prompt_version": "review-v1", "primary": [_entry()], "secondary": []}}
    slug = {"policy": _policy(), "models": {"prompt_version": "review-v1", "primary": [_entry("gpt-5.7-sol")], "secondary": []}}
    prompt = {"policy": _policy(), "models": {"prompt_version": "review-v2", "primary": [_entry(prompt_version="review-v2")], "secondary": []}}
    tools = {"policy": _policy(), "models": {"prompt_version": "review-v1", "primary": [_entry(tools=["read_file@2"])], "secondary": []}}
    fingerprints = {route_material_fingerprint(x) for x in (base, slug, prompt, tools)}
    assert len(fingerprints) == 4


def test_changed_route_material_forces_new_job_to_shadow() -> None:
    state_dir = tempfile.mkdtemp()
    state = State({"state_dir": state_dir})
    try:
        first = _job(state, 801)
        cfg = _cfg(state_dir, _entry())
        initial, initial_meta = dispatcher.resolve_snapshot(cfg, state, first)
        assert initial_meta["route_qualification"]["status"] == "observed"
        assert initial["approval"]["mode"] == "live"

        second = _job(state, 802)
        changed, changed_meta = dispatcher.resolve_snapshot(_cfg(state_dir, _entry("gpt-5.7-sol")), state, second)
        assert changed_meta["route_qualification"]["status"] == "shadow_locked"
        assert changed["approval"]["mode"] == "shadow"
        assert changed["authority"]["approve"] == "shadow"

        # Re-entering the old job must retain its original live snapshot.
        resumed, resumed_meta = dispatcher.resolve_snapshot(_cfg(state_dir, _entry("gpt-5.7-sol")), state, first)
        assert resumed_meta["resumed"] is True
        assert resumed["approval"]["mode"] == "live"
    finally:
        state.close()


def test_probe_persists_provider_health_and_qualifies_current_routes() -> None:
    from model_registry import mark_runtime_qualified, observe_runtime_routes

    state_dir = tempfile.mkdtemp()
    state = State({"state_dir": state_dir})
    try:
        cfg = _cfg(state_dir, _entry())
        persist_probe_result(state, cfg, _entry(), {"status": OK})
        row = state.db.execute("SELECT unavailable_until,last_error FROM providers").fetchone()
        assert row["unavailable_until"] is None and row["last_error"] is None
        qualified = mark_runtime_qualified(state, cfg, scope="o/r")
        assert qualified["status"] == "qualified"
        assert observe_runtime_routes(state, cfg, scope="o/r")["shadow_locked"] is False

        persist_probe_result(state, cfg, _entry(), {"status": TRANSPORT_FAILED, "detail": "quota exhausted"})
        row = state.db.execute("SELECT unavailable_until,last_error FROM providers").fetchone()
        assert row["unavailable_until"] is not None
        assert row["last_error"] == "quota exhausted"
    finally:
        state.close()
