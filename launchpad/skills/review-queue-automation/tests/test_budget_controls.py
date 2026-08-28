#!/usr/bin/env python3
"""Cost, retry and rate-limit control tests (T28).

The guarantee under test: the system downgrades to a draft or to a human BEFORE
a budget is exceeded, never after. Every refusal case therefore asserts that the
panel was not invoked at all — a downgrade that still spent the money would be
no control.
"""

from __future__ import annotations

import pathlib
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scripts"))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import budget  # noqa: E402
import dispatcher  # noqa: E402
from common import State  # noqa: E402
from config import policy_defaults  # noqa: E402
from test_dispatch_flow import (  # noqa: E402
    _clean_verdict,
    _config,
    fake_panel,
    patch_dispatcher,
    restore_dispatcher,
    seed_evidence,
    seed_job,
    seed_verdicts,
)


def _cfg(**budget_overrides) -> dict:
    cfg = _config("live")
    cfg["state_dir"] = tempfile.mkdtemp()
    cfg["logging"] = {"directory": tempfile.mkdtemp(), "format": "otel-jsonl"}
    cfg["policy"] = policy_defaults(cfg)
    if budget_overrides:
        cfg["budget"] = budget_overrides
    return cfg


def _seeded(state: State, number: int) -> str:
    jid = seed_job(state, number=number, head=f"h{number}")
    seed_evidence(state, jid)
    seed_verdicts(state, jid, [_clean_verdict("opus", "anthropic"),
                               _clean_verdict("gpt", "openai")])
    return jid


def _dispatch(cfg: dict, state: State, jid: str, number: int) -> tuple[dict, list]:
    """Dispatch with a panel that RECORDS every invocation, so a test can prove
    that a refusal spent nothing."""
    calls: list = []
    saved = patch_dispatcher(run_panel=fake_panel("SUPPORTED", calls=calls))
    try:
        result = dispatcher.run_job(
            cfg, {"job_id": jid, "repo": "o/r", "number": number, "lane": "incoming_review"},
            state=state,
        )
    finally:
        restore_dispatcher(saved)
    return result, calls


# -- limits resolution ------------------------------------------------------
def test_limits_are_finite_by_default() -> None:
    resolved = budget.limits({})
    for key in ("per_pr_tokens", "per_repo_daily_tokens", "max_attempts_per_job"):
        assert resolved[key] > 0, f"{key} must be finite by default"


def test_a_zero_limit_disables_only_that_axis() -> None:
    state = State({"state_dir": tempfile.mkdtemp()})
    try:
        cfg = {"budget": {"per_pr_tokens": 0, "per_repo_daily_tokens": 10}}
        budget.record_spend(state, job_id="j", repo="o/r", number=1, tokens=100)
        # per_pr is disabled, but the repo daily cap still bites.
        decision = budget.reserve(state, cfg, job_id="j2", repo="o/r", number=1, tokens=1)
        assert decision.allowed is False
        assert decision.limit == "per_repo_daily_tokens"
    finally:
        state.close()


# -- the pre-spend guarantee ------------------------------------------------
def test_expensive_pr_downgrades_to_draft_before_any_spend() -> None:
    cfg = _cfg(per_pr_tokens=1, max_concurrent_jobs=0)
    state = State({"state_dir": cfg["state_dir"]})
    try:
        jid = _seeded(state, 800)
        result, calls = _dispatch(cfg, state, jid, 800)
        assert result["decision"] == "BUDGET_REFUSED", result
        assert result["status"] == "degraded_draft"
        assert result["budget"]["limit"] == "per_pr_tokens"
        assert calls == [], "the panel ran despite the budget refusal: money was spent"
        # nothing was charged, because nothing ran
        assert budget.spent_for_pr(state, "o/r", 800) == 0
    finally:
        state.close()


def test_open_circuit_breaker_downgrades_to_human_before_any_spend() -> None:
    """A provider outage must stop costing full timeouts."""
    cfg = _cfg(circuit_breaker={"failure_threshold": 2, "cooldown_seconds": 900},
               max_concurrent_jobs=0)
    state = State({"state_dir": cfg["state_dir"]})
    try:
        budget.record_failure(state, cfg, "o/r", "provider down")
        opened = budget.record_failure(state, cfg, "o/r", "provider down")
        assert opened["status"] == budget.OPEN

        jid = _seeded(state, 801)
        result, calls = _dispatch(cfg, state, jid, 801)
        assert result["decision"] == "BUDGET_REFUSED", result
        assert result["status"] == "human_required"
        assert result["budget"]["limit"] == "circuit_breaker"
        assert calls == [], "the panel ran with the breaker open"
    finally:
        state.close()


def test_retry_ceiling_refuses_further_attempts() -> None:
    cfg = _cfg(max_attempts_per_job=2, max_concurrent_jobs=0)
    state = State({"state_dir": cfg["state_dir"]})
    try:
        jid = _seeded(state, 802)
        for _ in range(2):
            budget.record_reservation(state, job_id=jid, repo="o/r", number=802, tokens=1)
        result, calls = _dispatch(cfg, state, jid, 802)
        assert result["budget"]["limit"] == "max_attempts_per_job", result
        assert result["status"] == "human_required"
        assert calls == []
    finally:
        state.close()


def test_concurrency_cap_refuses_a_second_in_flight_job() -> None:
    cfg = _cfg(max_concurrent_jobs=1)
    state = State({"state_dir": cfg["state_dir"]})
    try:
        busy = _seeded(state, 803)
        state.transition(busy, "assurance")
        jid = _seeded(state, 804)
        result, calls = _dispatch(cfg, state, jid, 804)
        assert result["budget"]["limit"] == "max_concurrent_jobs", result
        assert calls == []
    finally:
        state.close()


def test_rest_floor_refuses_when_remaining_is_unknown() -> None:
    """An unprovable rate-limit floor is not a pass."""
    state = State({"state_dir": tempfile.mkdtemp()})
    try:
        cfg = {"budget": {"rest_remaining_floor": 200}}
        decision = budget.reserve(state, cfg, job_id="j", repo="o/r", number=1,
                                  tokens=10, rest_remaining=None)
        assert decision.allowed is False
        assert decision.limit == "rest_remaining_floor"
        assert decision.downgrade == budget.HUMAN

        below = budget.reserve(state, cfg, job_id="j", repo="o/r", number=1,
                               tokens=10, rest_remaining=5)
        assert below.allowed is False
        above = budget.reserve(state, cfg, job_id="j", repo="o/r", number=1,
                               tokens=10, rest_remaining=5000)
        assert above.allowed is True
    finally:
        state.close()


# -- accounting -------------------------------------------------------------
def test_a_successful_dispatch_records_spend_and_closes_the_breaker() -> None:
    cfg = _cfg(max_concurrent_jobs=0)
    state = State({"state_dir": cfg["state_dir"]})
    try:
        jid = _seeded(state, 805)
        result, calls = _dispatch(cfg, state, jid, 805)
        assert len(calls) == 1, result
        assert budget.spent_for_pr(state, "o/r", 805) > 0, "spend was never recorded"
        assert budget.breaker_state(state, "o/r")["status"] == budget.CLOSED
        assert budget.attempts_for_job(state, jid) == 1
    finally:
        state.close()


def test_an_open_breaker_half_opens_after_its_cooldown() -> None:
    state = State({"state_dir": tempfile.mkdtemp()})
    try:
        cfg = {"budget": {"circuit_breaker": {"failure_threshold": 1,
                                              "cooldown_seconds": 900}}}
        budget.record_failure(state, cfg, "o/r", "down")
        assert budget.breaker_state(state, "o/r")["status"] == budget.OPEN
        # Wind the cooldown into the past rather than sleeping.
        state.db.execute(
            "UPDATE circuit_breakers SET open_until=? WHERE scope=?",
            ("2000-01-01T00:00:00Z", "o/r"),
        )
        state.db.commit()
        assert budget.breaker_state(state, "o/r")["status"] == budget.HALF_OPEN
        # half-open permits one attempt
        decision = budget.reserve(state, cfg, job_id="j", repo="o/r", number=1, tokens=1)
        assert decision.allowed is True
        budget.record_success(state, "o/r")
        assert budget.breaker_state(state, "o/r")["status"] == budget.CLOSED
    finally:
        state.close()


def test_reset_clears_breakers() -> None:
    state = State({"state_dir": tempfile.mkdtemp()})
    try:
        budget.record_failure(state, {"budget": {"circuit_breaker":
                                                 {"failure_threshold": 1,
                                                  "cooldown_seconds": 5}}}, "o/r", "x")
        assert budget.reset_breakers(state) == 1
        assert budget.breaker_state(state, "o/r")["status"] == budget.CLOSED
    finally:
        state.close()


# -- config validation ------------------------------------------------------
def test_a_malformed_budget_section_is_an_error_not_a_silent_default() -> None:
    assert budget.validate_budget({}) == []
    assert budget.validate_budget({"budget": {"per_pr_tokens": -5}})
    assert budget.validate_budget({"budget": {"circuit_breaker": {"cooldown_seconds": 0}}})
    assert budget.validate_budget({"budget": "nope"}) == ["budget must be an object"]
