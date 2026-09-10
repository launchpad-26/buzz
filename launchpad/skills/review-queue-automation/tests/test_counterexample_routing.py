#!/usr/bin/env python3
"""Counterexample tests for route selection, route identity, and provider independence.

Three failures are being defended against, and each test asserts a refusal rather
than a success:

1. inventing a route — no configured candidate must resolve to `human`, never to
   an implicit "latest" model;
2. re-using an identity a route no longer has — a changed model, effort, prompt
   or policy must produce a different fingerprint and return to shadow;
3. claiming independence that does not exist — two reviewers behind one provider
   are one opinion, and the approval gate must say so.

Sibling ownership: none of `routing.py`, `model_registry.py` or
`approval_evaluate.py` is sibling-owned, but `test_route_config.py` and
`test_model_registry.py` are pre-existing files this lane did not write, so the
counterexamples live here.
"""

from __future__ import annotations

import datetime as dt
import pathlib
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import model_registry as registry  # noqa: E402
import routing as routingmod  # noqa: E402
from approval_evaluate import ApprovalEvidence, PRFacts, compute_gates  # noqa: E402
from common import State, utcnow  # noqa: E402

_CLAUDE = {"runner": "claude", "selector": "claude-opus-4-5", "provider_family": "anthropic",
           "capability": "frontier", "efforts": ["high"]}
_CODEX = {"runner": "codex", "selector": "gpt-5.6-sol", "provider_family": "openai",
          "capability": "frontier", "efforts": ["high"]}
_OMP = {"runner": "omp", "selector": "some/diverse-model", "provider_family": "meta",
        "capability": "workhorse", "efforts": ["medium"]}
_ECONOMY = {"runner": "omp", "selector": "some/cheap-model", "provider_family": "meta",
            "capability": "economy", "efforts": ["low"]}


def _cfg(**models) -> dict:
    return {"repository": {"slug": "o/r"}, "policy": {"version": "p1"}, "models": models}


def _state() -> State:
    return State({"state_dir": tempfile.mkdtemp()})


def _cooldown(state: State, key: str, *, minutes: int = 60) -> None:
    until = (dt.datetime.now(dt.timezone.utc) + dt.timedelta(minutes=minutes)) \
        .replace(microsecond=0).isoformat().replace("+00:00", "Z")
    state.db.execute(
        "INSERT INTO providers(key,unavailable_until,last_error,updated_at) VALUES(?,?,?,?)",
        (key, until, "probe failed", utcnow()),
    )
    state.db.commit()


# --------------------------------------------------------------------------
# 1. route selection
# --------------------------------------------------------------------------


def test_the_control_a_configured_route_resolves() -> None:
    """Without the control, a resolver that always escalated to `human` would pass
    every counterexample below and never review anything."""
    run = routingmod.resolve_route(_cfg(primary=[_CLAUDE]), "CLAUDE_STRONG", effort="high")
    assert run.final == "claude-opus-4-5"
    assert run.resolved and run.resolved[0].provider == "anthropic"


def test_an_empty_configuration_escalates_instead_of_inventing_a_model() -> None:
    for cfg in ({}, _cfg(), _cfg(primary=[], secondary=[]), {"models": None},
                {"models": {"primary": None}}):
        run = routingmod.resolve_route(cfg, "CLAUDE_STRONG")
        assert run.final == "human", cfg
        assert run.resolved == [], cfg


def test_a_candidate_with_no_model_identity_is_skipped_not_routed_blank() -> None:
    """A pool entry with no selector would otherwise resolve to the empty model —
    a route that looks resolved and cannot run."""
    blank = {"runner": "omp", "provider_family": "meta", "capability": "workhorse"}
    run = routingmod.resolve_route(_cfg(primary=[blank]), "ANY")
    assert run.final == "human"
    assert run.resolved == []


def test_a_candidate_whose_runner_has_no_adapter_never_enters_the_ladder() -> None:
    """An unrecognised runner is a configuration error, not a rung. Routing to it
    would defer the failure to dispatch time on a real PR."""
    for runner in ("", "gemini", "OMP", "codex-cli", None):
        entry = {**_OMP, "runner": runner}
        run = routingmod.resolve_route(_cfg(primary=[entry]), "ANY")
        assert run.final == "human", runner
        assert run.resolved == [], runner


def test_the_ladder_is_subscription_first_and_not_reordered_by_pool_position() -> None:
    """Listing the OpenRouter fallback first must not promote it above the
    configured subscriptions; the ladder, not the file order, decides."""
    run = routingmod.resolve_route(_cfg(primary=[_OMP, _CODEX, _CLAUDE]), "ANY")
    assert run.final == "claude-opus-4-5"
    assert run.resolved[0].fallback_position == 0


def test_an_economy_candidate_is_a_last_resort_not_a_peer_fallback() -> None:
    """`economical` is below `openrouter`. If an economy entry were treated as a
    provider-diverse fallback it would be selected ahead of a stronger one."""
    routes = routingmod._routes_from_config(_cfg(primary=[_ECONOMY, _OMP]))
    assert routes["economical"] == [_ECONOMY]
    assert routes["openrouter"] == [_OMP]
    run = routingmod.resolve_route(_cfg(primary=[_ECONOMY, _OMP]), "ANY")
    assert run.final == "some/diverse-model"


def test_a_route_on_cooldown_is_not_selected() -> None:
    state = _state()
    _cooldown(state, "anthropic:claude-opus-4-5")
    run = routingmod.resolve_route(_cfg(primary=[_CLAUDE, _CODEX]), "ANY", state=state)
    assert run.final == "gpt-5.6-sol"
    assert "claude-opus-4-5" not in run.attempted
    state.close()


def test_every_route_on_cooldown_escalates_rather_than_ignoring_the_cooldown() -> None:
    """The cooldown exists because the transport failed. Falling back to a route
    that is known-broken would loop the failure onto every queued PR."""
    state = _state()
    for key in ("anthropic:claude-opus-4-5", "openai:gpt-5.6-sol", "meta:some/diverse-model"):
        _cooldown(state, key)
    run = routingmod.resolve_route(_cfg(primary=[_CLAUDE, _CODEX, _OMP]), "ANY", state=state)
    assert run.final == "human"
    assert run.resolved == []
    state.close()


def test_an_expired_cooldown_does_not_permanently_retire_a_route() -> None:
    """Guards the guard: if `is_route_available` were simply False for any recorded
    row, the cooldown tests above would pass while the ladder was dead."""
    state = _state()
    past = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=2)) \
        .replace(microsecond=0).isoformat().replace("+00:00", "Z")
    state.db.execute(
        "INSERT INTO providers(key,unavailable_until,last_error,updated_at) VALUES(?,?,?,?)",
        ("anthropic:claude-opus-4-5", past, "old failure", utcnow()),
    )
    state.db.commit()
    run = routingmod.resolve_route(_cfg(primary=[_CLAUDE]), "ANY", state=state)
    assert run.final == "claude-opus-4-5"
    state.close()


def test_a_provider_hint_cannot_conjure_a_rung_that_is_not_configured() -> None:
    run = routingmod.resolve_route(_cfg(primary=[_CODEX]), "ANY", provider_hint="claude")
    assert run.final == "gpt-5.6-sol"
    run = routingmod.resolve_route(_cfg(), "ANY", provider_hint="claude")
    assert run.final == "human"


# --------------------------------------------------------------------------
# 2. route identity
# --------------------------------------------------------------------------


def test_a_qualified_route_without_a_complete_identity_is_refused() -> None:
    """A route with no selector, runner or provider cannot be audited later, so it
    must not be constructible at all."""
    complete = {"runner": "codex", "provider": "openai", "selector": "gpt-5.6-sol"}
    assert registry.qualified_route(complete, effort="high", policy_version="p1")["fingerprint"]
    for missing in ("runner", "provider", "selector"):
        entry = {k: v for k, v in complete.items() if k != missing}
        try:
            registry.qualified_route(entry, effort="high", policy_version="p1")
        except ValueError as exc:
            assert missing in str(exc) or "requires" in str(exc)
        else:  # pragma: no cover
            raise AssertionError(f"a route missing {missing} must be refused")
        entry = {**complete, missing: "   "}
        try:
            registry.qualified_route(entry, effort="high", policy_version="p1")
        except ValueError:
            pass
        else:  # pragma: no cover
            raise AssertionError(f"a route with a blank {missing} must be refused")


def test_every_identity_field_changes_the_route_fingerprint() -> None:
    """A fingerprint that ignored any of these would let a changed route reuse an
    earlier qualification — the whole point of pinning route identity."""
    base = {"runner": "codex", "provider": "openai", "selector": "gpt-5.6-sol",
            "execution_mode": "read_only", "tools": [], "prompt_version": "v1"}
    reference = registry.qualified_route(base, effort="high", policy_version="p1")["fingerprint"]
    variants = [
        ({**base, "selector": "gpt-5.6-terra"}, "high", "p1"),
        ({**base, "model_version": "2026-02-01"}, "high", "p1"),
        ({**base, "execution_mode": "write"}, "high", "p1"),
        ({**base, "tools": ["bash"]}, "high", "p1"),
        ({**base, "prompt_version": "v2"}, "high", "p1"),
        ({**base, "runner": "omp"}, "high", "p1"),
        ({**base, "provider": "openrouter"}, "high", "p1"),
        (base, "low", "p1"),
        (base, "high", "p2"),
    ]
    for entry, effort, policy in variants:
        other = registry.qualified_route(entry, effort=effort, policy_version=policy)["fingerprint"]
        assert other != reference, (entry, effort, policy)
    # Identical input is stable, so the inequalities above are meaningful.
    assert registry.qualified_route(dict(base), effort="high",
                                    policy_version="p1")["fingerprint"] == reference


def test_an_unknown_alias_is_never_resolved_to_a_default_model() -> None:
    for bogus in ("CLAUDE_LATEST", "gpt-5", "", "best", "CODEX"):
        try:
            registry.resolve(bogus)
        except ValueError as exc:
            assert "unknown model alias" in str(exc)
        else:  # pragma: no cover
            raise AssertionError(f"alias {bogus!r} must not resolve")
    assert registry.resolve("codex_strong").selector == "gpt-5.6-sol"


def test_changed_route_material_returns_to_shadow_instead_of_staying_qualified() -> None:
    state = _state()
    cfg = _cfg(primary=[_CODEX])
    first = registry.observe_runtime_routes(state, cfg, scope="o/r")
    assert first["status"] == "observed"
    qualified = registry.mark_runtime_qualified(state, cfg, scope="o/r")
    assert qualified["shadow_locked"] is False

    swapped = _cfg(primary=[{**_CODEX, "selector": "gpt-5.6-terra"}])
    observed = registry.observe_runtime_routes(state, swapped, scope="o/r")
    assert observed["shadow_locked"] is True
    assert observed["status"] == "shadow_locked"
    assert observed["fingerprint"] != qualified["fingerprint"]
    # ...and it stays locked until qualification explicitly replaces it.
    assert registry.observe_runtime_routes(state, swapped, scope="o/r")["shadow_locked"] is True
    state.close()


def test_a_prompt_or_policy_edit_alone_is_enough_to_return_to_shadow() -> None:
    """Model identity is not the only runtime input. A silently-edited prompt or
    policy would change reviewer behaviour under an unchanged qualification."""
    state = _state()
    cfg = _cfg(primary=[_CODEX])
    registry.observe_runtime_routes(state, cfg, scope="o/r")
    registry.mark_runtime_qualified(state, cfg, scope="o/r")
    for edited in (
        {**cfg, "models": {**cfg["models"], "prompt_version": "v9"}},
        {**cfg, "policy": {"version": "p2"}},
        _cfg(primary=[{**_CODEX, "efforts": ["low"]}]),
    ):
        state.db.execute("UPDATE route_qualifications SET status='qualified' WHERE scope='o/r'")
        state.db.commit()
        assert registry.observe_runtime_routes(state, edited, scope="o/r")["shadow_locked"] is True
    state.close()


# --------------------------------------------------------------------------
# 3. provider independence at the approval gate
# --------------------------------------------------------------------------


def _verdict(model: str, family: str) -> dict:
    return {"model": model, "provider_family": family, "signal": "SUPPORTED",
            "recommendation": "clean", "findings": [], "_schema_ok": True}


def _gates(verdicts: list[dict]):
    cfg = {"repository": {"slug": "o/r"}, "approval": {"mode": "disabled"}, "risk": {}}
    pr = PRFacts(draft=False, author_login="someone-else", head_sha="c" * 40)
    return compute_gates(
        cfg, pr, verdicts, [v["model"] for v in verdicts], 0, "low", "bot",
        head_sha="c" * 40, profile={"independence": "challenger"},
        evidence=ApprovalEvidence(),
    )


def test_the_control_two_genuinely_distinct_reviewers_are_distinct() -> None:
    gates = _gates([_verdict("claude-opus-4-5", "anthropic"), _verdict("gpt-5.6-sol", "openai")])
    assert gates.distinct_reviewers is True


def test_two_models_behind_one_provider_are_not_distinct_reviewers() -> None:
    gates = _gates([_verdict("claude-opus-4-5", "anthropic"),
                    _verdict("claude-sonnet-4-5", "anthropic")])
    assert gates.distinct_reviewers is False
    assert gates.passed() is False


def test_the_same_model_twice_is_not_two_reviewers() -> None:
    gates = _gates([_verdict("gpt-5.6-sol", "openai"), _verdict("gpt-5.6-sol", "openai")])
    assert gates.distinct_reviewers is False


def test_one_reviewer_is_never_distinct_reviewers() -> None:
    assert _gates([_verdict("gpt-5.6-sol", "openai")]).distinct_reviewers is False
    assert _gates([]).distinct_reviewers is False


def test_unattributed_reviewers_are_not_distinct_reviewers() -> None:
    """Two verdicts with no provider family recorded could be the same model run
    twice. Absent attribution is not evidence of independence — and "no family"
    must not itself count as a family, which would make one attributed reviewer
    plus one unattributed reviewer look like two providers."""
    assert _gates([_verdict("m1", ""), _verdict("m2", "")]).distinct_reviewers is False
    mixed = _gates([_verdict("claude-opus-4-5", "anthropic"), _verdict("m2", "")])
    assert mixed.distinct_reviewers is False
    assert mixed.passed() is False


def test_a_verdict_that_failed_schema_validation_never_counts_as_a_valid_verdict() -> None:
    bad = {**_verdict("gpt-5.6-sol", "openai"), "_schema_ok": False}
    gates = _gates([_verdict("claude-opus-4-5", "anthropic"), bad])
    assert gates.valid_verdicts is False
    assert gates.passed() is False
