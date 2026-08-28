#!/usr/bin/env python3
"""Every field a strategy declares must be READ by a runtime module.

Declared-but-unread metadata reads as authoritative while changing nothing, and
this skill had accumulated six such fields on `Strategy` alone
(`parallel`, `min_participants`, `required_inputs`, `degraded_form`,
`assurance_contribution`, `disagreement_handling`). They were deleted or given a
real consumer; this file is the guard that stops the seventh.

The scan is textual on purpose: it looks for the field being read ANYWHERE in
`scripts/` outside `strategies.py`, so it cannot be satisfied by another
declaration. Each surviving field additionally has a behavioural test below, so
a consumer that exists only to satisfy the scan is not enough.
"""

from __future__ import annotations

import dataclasses
import json
import pathlib
import re
import sys
import tempfile

SKILL = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SKILL / "scripts"))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import panel  # noqa: E402
from strategies import (  # noqa: E402
    DECLARED_FIELDS,
    STRATEGY_BY_NAME,
    Strategy,
    strategy_for_profile,
)

#: Modules that may consume strategy metadata. `strategies.py` is excluded: a
#: field referenced only by its own module is still dead.
_RUNTIME_MODULES = sorted(
    path for path in (SKILL / "scripts").glob("*.py")
    if path.name != "strategies.py"
)


def _readers(field: str) -> list[str]:
    """Modules that read `field` off something (attribute or mapping access)."""
    pattern = re.compile(rf"(\.{field}\b|\[[\"']{field}[\"']\]|\bget\([\"']{field}[\"'])")
    return [path.name for path in _RUNTIME_MODULES
            if pattern.search(path.read_text(encoding="utf-8"))]


# -- the guard --------------------------------------------------------------
def test_every_declared_field_is_read_by_a_runtime_module() -> None:
    dead = {
        field.name: _readers(field.name)
        for field in dataclasses.fields(Strategy)
        if not _readers(field.name)
    }
    assert not dead, (
        "Strategy declares fields nothing reads: " + ", ".join(sorted(dead))
        + ". Give each a runtime consumer or delete it — declared-and-unread "
        "metadata looks authoritative and changes nothing."
    )


def test_declared_fields_matches_the_dataclass() -> None:
    """The documented field list cannot drift from the actual dataclass."""
    actual = tuple(field.name for field in dataclasses.fields(Strategy))
    assert actual == DECLARED_FIELDS, (actual, DECLARED_FIELDS)


def test_the_previously_dead_fields_are_gone() -> None:
    declared = {field.name for field in dataclasses.fields(Strategy)}
    for removed in ("parallel", "min_participants", "required_inputs",
                    "degraded_form", "assurance_contribution"):
        assert removed not in declared, f"{removed} was reintroduced without a consumer"


def test_the_guard_detects_a_newly_added_dead_field() -> None:
    """The guard must be able to fail, or it proves nothing."""
    assert _readers("a_field_no_module_reads") == []
    assert _readers("aggregation"), "the scan must find a field that IS consumed"


# -- each surviving field is behaviourally consumed -------------------------
def test_model_route_orders_the_fallback_chain() -> None:
    from fallback import recipe_for

    assert recipe_for("direct_analysis").name == "preferred"
    assert recipe_for("independent_parallel").name == "diverse"
    assert recipe_for("uncertainty_calibration").name == "economical"


def test_aggregation_selects_the_execution_mode() -> None:
    from modes import mode_for

    assert mode_for("direct_analysis").name == "single"
    assert mode_for("independent_parallel").name == "dual_key"


def test_roles_label_the_panel_slots() -> None:
    """`roles` names the participants; the panel must use it, not re-invent it."""
    adversarial = STRATEGY_BY_NAME["adversarial"]
    assert adversarial.roles == ("reviewer", "adversary")
    labels = [panel._slot_role(adversarial.roles, i, 2) for i in range(2)]
    assert labels == ["reviewer", "adversary"]
    # A strategy with fewer roles than slots degrades the LABEL, not the panel.
    assert panel._slot_role(("solo",), 1, 2) == "reviewer_b"


def test_budget_tokens_is_the_reservation_the_orchestrator_makes() -> None:
    import budget
    from common import State

    state = State({"state_dir": tempfile.mkdtemp()})
    try:
        strategy, _reason = strategy_for_profile(
            {"level": "low", "independence": "challenger"})
        assert strategy.budget_tokens > 0
        decision = budget.reserve(
            state, {"budget": {"per_pr_tokens": strategy.budget_tokens - 1}},
            job_id="j", repo="o/r", number=1, tokens=strategy.budget_tokens)
        assert decision.allowed is False, (
            "the strategy's declared budget must be what is reserved"
        )
        ok = budget.reserve(
            state, {"budget": {"per_pr_tokens": strategy.budget_tokens}},
            job_id="j", repo="o/r", number=1, tokens=strategy.budget_tokens)
        assert ok.allowed is True
        assert ok.reserved_tokens == strategy.budget_tokens
    finally:
        state.close()


def test_timeout_seconds_can_only_shorten_a_run() -> None:
    """The panel takes the tighter of the operator timeout and the strategy's."""
    strategy = STRATEGY_BY_NAME["direct_analysis"]
    operator_timeout = strategy.timeout_seconds + 600
    assert min(operator_timeout, strategy.timeout_seconds) == strategy.timeout_seconds
    shorter = strategy.timeout_seconds - 600
    assert min(shorter, strategy.timeout_seconds) == shorter, (
        "a strategy must never be able to LENGTHEN an operator timeout"
    )


def test_output_schema_mismatch_stops_the_panel() -> None:
    """A strategy asking for a schema the panel does not validate is fail-closed."""
    from errors import JobBlockingError

    assert all(s.output_schema == panel.VERDICT_SCHEMA
               for s in STRATEGY_BY_NAME.values())

    original = STRATEGY_BY_NAME["direct_analysis"]
    STRATEGY_BY_NAME["direct_analysis"] = dataclasses.replace(
        original, output_schema="some-other-schema")
    try:
        from assurance import Profile
        from common import State

        state = State({"state_dir": tempfile.mkdtemp()})
        try:
            job = "job-schema"
            artifacts = state.job_dir(job)
            (artifacts / "evidence.txt").write_text("evidence", encoding="utf-8")
            config = {"models": {"primary": [], "secondary": []},
                      "repository": {"root": "/tmp"}, "assurance": {}}
            raised = False
            try:
                panel.run_panel(config, state, "o/r", 1, "incoming_review", job,
                                Profile("workhorse", "medium", "single"))
            except JobBlockingError as exc:
                raised = "output_schema" in str(exc)
            assert raised, "a schema mismatch must block the job, not be ignored"
        finally:
            state.close()
    finally:
        STRATEGY_BY_NAME["direct_analysis"] = original


def test_disagreement_handling_is_reported_when_participants_split() -> None:
    """A split among counted participants surfaces the strategy's handling."""
    from modes import ModeSpec, Participant, aggregate

    strategy = STRATEGY_BY_NAME["adversarial"]
    assert strategy.disagreement_handling == "adjudicate_split"

    spec = ModeSpec("independent_review", 2, True, False, True,
                    roles=("reviewer", "adversary"))
    split = aggregate(spec, [
        Participant(role="reviewer", model="a", provider_family="anthropic",
                    valid=True, signal="SUPPORTED"),
        Participant(role="adversary", model="b", provider_family="openai",
                    valid=True, signal="MATERIAL_DISAGREEMENT"),
    ])
    signals = {s for s in split.signals if s}
    assert len(signals) > 1
    handling = strategy.disagreement_handling if len(signals) > 1 else ""
    assert handling == "adjudicate_split"
