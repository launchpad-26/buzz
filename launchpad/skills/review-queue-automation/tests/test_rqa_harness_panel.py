#!/usr/bin/env python3
"""P-06 §3.2 — the panel loop. §8 rows T4, T4b, T5-T13 and T17.

T4   successful first route and valid verdict -> one reservation, invocation and
     consumption; complete panel whose cutoff is after the attempt; matching `panel` entry
T4b  a per-model bound refuses the first reservation with `Refusal(fallback)` and the
     configured fallback returns a valid verdict -> complete, `bound_reached is True`,
     and the `panel` entry records it (RQA-FR-039)
T5   candidate-terminal -> route excluded before the next selection
T6   provider-terminal -> family excluded before the next selection
T7   transient then success on the same route -> two distinct reservations, two
     invocations, two consumptions, no new route selection between them
T8   the retry's fresh reservation refuses fallback -> no second invocation, family
     excluded, selection advances
T9   two transient invocations for one route -> no third invocation, route excluded
T10  `Refusal(incomplete|escalate)` -> incomplete panel with the cutoff after the last
     attempt, if any
T11  `RouteUnavailable` before completion -> incomplete exhausted panel and entry
T12  finite routes and terminal outcomes -> termination
T13  usage sidecar and separately none -> consumption follows each invocation with the
     corresponding reservation
T17  append fails for bundle, attestation or panel -> `AppendFailed` propagates

Every invocation here is a local Python script standing in for a harness. Nothing in
this file opens a socket, reads a credential or calls a model.
"""

from __future__ import annotations

import ast
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import test_rqa_harness_fixtures as fx  # noqa: E402
from rqa.contracts import AppendFailed, BundleFailure, PanelResult, Refusal, Route  # noqa: E402
from rqa.harness import run  # noqa: E402
from rqa.harness.errors import EmptyPlanError, HarnessError  # noqa: E402
from rqa.protocol import Verdict  # noqa: E402


def _route(directory: pathlib.Path, *, name: str, behaviours: tuple[str, ...], family: str):
    script = fx.harness_script(directory=directory, behaviours=behaviours, name=name)
    return fx.make_route(script=script, family=family), script


def _run(
    *,
    state_dir: pathlib.Path,
    supply: fx.FakeSupply,
    record: fx.FakeRecord | None = None,
    participants: int = 1,
    obligations: tuple[str, ...] = ("O1",),
):
    writer = record if record is not None else fx.FakeRecord()
    result = run(
        job=fx.make_job(),
        plan=fx.make_plan(obligations=obligations, participants=participants),
        facts=fx.make_facts(),
        snapshot=fx.make_snapshot(),
        supply=supply,
        state_dir=state_dir,
        record=writer,
    )
    return result, writer


# -- T4 -------------------------------------------------------------------------


def test_t4_one_reservation_one_invocation_one_consumption_and_a_complete_panel() -> None:
    with fx.workspace() as raw:
        directory = pathlib.Path(raw)
        route, script = _route(directory, name="h1", behaviours=("valid",), family="fam-a")
        supply = fx.FakeSupply((route,))
        result, record = _run(state_dir=directory / "state", supply=supply)

        assert isinstance(result, PanelResult)
        assert result.complete is True
        assert result.incomplete_reason is None
        assert result.bound_reached is False
        assert len(supply.reserve_calls) == 1
        assert len(fx.script_calls(script=script)) == 1
        assert len(supply.consumed_calls) == 1
        assert len(result.attempts) == 1
        assert isinstance(result.attempts[0].outcome, Verdict)


def test_t4_the_cutoff_is_captured_after_the_final_attempt() -> None:
    with fx.workspace() as raw:
        directory = pathlib.Path(raw)
        route, _ = _route(directory, name="h1", behaviours=("valid",), family="fam-a")
        supply = fx.FakeSupply((route,))
        result, _ = _run(state_dir=directory / "state", supply=supply)
        assert isinstance(result, PanelResult)
        assert result.evidence_cutoff >= result.attempts[-1].attestation.ended_at


def test_t4_the_panel_entry_matches_the_returned_result() -> None:
    with fx.workspace() as raw:
        directory = pathlib.Path(raw)
        route, _ = _route(directory, name="h1", behaviours=("valid",), family="fam-a")
        result, record = _run(state_dir=directory / "state", supply=fx.FakeSupply((route,)))
        assert isinstance(result, PanelResult)
        entries = record.of_kind("panel")
        assert len(entries) == 1
        entry = entries[0]
        assert entry["attempts"] == [attempt.id for attempt in result.attempts]
        assert entry["complete"] is result.complete
        assert entry["incomplete_reason"] == result.incomplete_reason
        assert entry["evidence_cutoff"] == result.evidence_cutoff.isoformat()
        assert entry["bound_reached"] is result.bound_reached


def test_t4_the_bundle_entry_is_appended_once_before_any_attempt() -> None:
    with fx.workspace() as raw:
        directory = pathlib.Path(raw)
        route, _ = _route(directory, name="h1", behaviours=("valid",), family="fam-a")
        _, record = _run(state_dir=directory / "state", supply=fx.FakeSupply((route,)))
        assert record.kinds() == ["bundle", "attestation", "panel"]
        assert record.of_kind("bundle")[0]["status"] == "ready"


def test_t4_the_attestation_is_rqas_measurement_and_the_model_claim_is_marked_separate() -> None:
    """§6, RQA-NFR-022, U-VERDICT-11: the attested route fields come from the `Route` RQA
    selected; the harness's own identity is recorded under its own key and never merged."""
    with fx.workspace() as raw:
        directory = pathlib.Path(raw)
        route, _ = _route(directory, name="h1", behaviours=("valid",), family="fam-a")
        _, record = _run(state_dir=directory / "state", supply=fx.FakeSupply((route,)))
        payload = record.of_kind("attestation")[0]
        attested = payload["attested"]
        assert attested["harness"] == route.harness == "fake"
        assert attested["provider"] == route.provider
        assert attested["family"] == route.family
        assert attested["exit_code"] == 0
        assert payload["self_reported"]["harness"] == "self-reported-harness"
        assert payload["self_reported"]["provider"] == "self-reported-provider"
        # The two halves share no value: nothing the model wrote reached an attested field.
        assert attested["harness"] != payload["self_reported"]["harness"]
        assert attested["model"] != payload["self_reported"]["model"]


def test_t4_the_effort_recorded_is_the_one_the_transport_enforces() -> None:
    """U-DISPATCH-25's effort honesty, carried into the field that matters."""
    with fx.workspace() as raw:
        directory = pathlib.Path(raw)
        route, _ = _route(directory, name="h1", behaviours=("valid",), family="fam-a")
        _, record = _run(state_dir=directory / "state", supply=fx.FakeSupply((route,)))
        attested = record.of_kind("attestation")[0]["attested"]
        # single_pass requests "medium"; the fake transport enforces only "high".
        assert attested["effort_requested"] == "medium"
        assert attested["effort"] == "unenforced"
        assert attested["effort_enforced"] is False
        assert attested["read_only_proof"] == ["--fake-read-only"]


def test_the_run_writes_only_the_two_trees_section_five_permits() -> None:
    with fx.workspace() as raw:
        directory = pathlib.Path(raw)
        state_dir = directory / "state"
        route, _ = _route(directory, name="h1", behaviours=("valid",), family="fam-a")
        _run(state_dir=state_dir, supply=fx.FakeSupply((route,)))
        job_dir = state_dir / "jobs" / "job-1"
        assert sorted(entry.name for entry in job_dir.iterdir()) == ["bundle", "harness"]
        assert sorted(entry.name for entry in (job_dir / "harness").iterdir()) == ["01"]
        assert sorted(entry.name for entry in state_dir.iterdir()) == ["jobs"]


def test_the_slot_holds_the_verdict_the_streams_and_rqas_own_attestation() -> None:
    with fx.workspace() as raw:
        directory = pathlib.Path(raw)
        state_dir = directory / "state"
        route, _ = _route(directory, name="h1", behaviours=("usage:99",), family="fam-a")
        _run(state_dir=state_dir, supply=fx.FakeSupply((route,)))
        slot = state_dir / "jobs" / "job-1" / "harness" / "01"
        for name in ("verdict.json", "usage.json", "stdout.log", "stderr.log", "attestation.json"):
            assert (slot / name).is_file(), name


# -- T5 -------------------------------------------------------------------------


def test_t5_a_candidate_terminal_outcome_excludes_the_route_before_the_next_selection() -> None:
    with fx.workspace() as raw:
        directory = pathlib.Path(raw)
        first, _ = _route(directory, name="h1", behaviours=("invalid",), family="fam-a")
        second, _ = _route(directory, name="h2", behaviours=("valid",), family="fam-b")
        supply = fx.FakeSupply((first, second))
        result, _ = _run(state_dir=directory / "state", supply=supply)
        assert isinstance(result, PanelResult) and result.complete is True
        assert len(supply.route_calls) == 2
        assert supply.route_calls[1][1].excluded_routes == frozenset({first})
        assert supply.route_calls[1][1].excluded_families == frozenset()
        assert result.attempts[0].outcome.kind == "CANDIDATE_TERMINAL"


def test_a_zero_exit_without_a_verdict_is_candidate_terminal_not_an_empty_success() -> None:
    with fx.workspace() as raw:
        directory = pathlib.Path(raw)
        route, _ = _route(directory, name="h1", behaviours=("noverdict",), family="fam-a")
        result, _ = _run(state_dir=directory / "state", supply=fx.FakeSupply((route,)))
        assert isinstance(result, PanelResult)
        assert result.complete is False
        assert result.attempts[0].outcome.kind == "CANDIDATE_TERMINAL"
        assert result.attempts[0].outcome.detail == "no_verdict"


def test_an_invalid_verdicts_reasons_stay_on_disk_and_out_of_the_record() -> None:
    with fx.workspace() as raw:
        directory = pathlib.Path(raw)
        state_dir = directory / "state"
        route, _ = _route(directory, name="h1", behaviours=("invalid",), family="fam-a")
        _, record = _run(state_dir=state_dir, supply=fx.FakeSupply((route,)))
        payload = record.of_kind("attestation")[0]
        assert payload["detail"].startswith("invalid_verdict:")
        assert (state_dir / "jobs" / "job-1" / "harness" / "01" / "validation.json").is_file()
        assert "not json" not in payload["detail"]


# -- T6 -------------------------------------------------------------------------


def test_t6_a_provider_terminal_outcome_excludes_the_family_before_the_next_selection() -> None:
    with fx.workspace() as raw:
        directory = pathlib.Path(raw)
        first, _ = _route(directory, name="h1", behaviours=("exit2",), family="fam-a")
        sibling, sibling_script = _route(directory, name="h2", behaviours=("valid",), family="fam-a")
        other, _ = _route(directory, name="h3", behaviours=("valid",), family="fam-b")
        supply = fx.FakeSupply((first, sibling, other))
        result, _ = _run(state_dir=directory / "state", supply=supply)
        assert isinstance(result, PanelResult) and result.complete is True
        assert supply.route_calls[1][1].excluded_families == frozenset({"fam-a"})
        # The sibling in the excluded family was never invoked.
        assert fx.script_calls(script=sibling_script) == []
        assert result.attempts[0].outcome.kind == "PROVIDER_TERMINAL"


# -- T7 -------------------------------------------------------------------------


def test_t7_a_transient_then_success_uses_two_distinct_reservations_on_one_route() -> None:
    with fx.workspace() as raw:
        directory = pathlib.Path(raw)
        route, script = _route(directory, name="h1", behaviours=("exit7", "valid"), family="fam-a")
        supply = fx.FakeSupply((route,))
        result, _ = _run(state_dir=directory / "state", supply=supply)

        assert isinstance(result, PanelResult) and result.complete is True
        assert len(fx.script_calls(script=script)) == 2
        assert len(supply.reserve_calls) == 2
        assert len(supply.consumed_calls) == 2
        reservation_ids = [call[2].id for call in supply.consumed_calls]
        assert len(set(reservation_ids)) == 2, "a reservation is consumed by exactly one invocation"
        # No new route selection between the two invocations (§3.2 step 6).
        assert len(supply.route_calls) == 1
        assert supply.reserve_calls == [route, route]


# -- T8 -------------------------------------------------------------------------


def test_t8_a_retry_reservation_refused_fallback_makes_no_second_invocation() -> None:
    with fx.workspace() as raw:
        directory = pathlib.Path(raw)
        first, first_script = _route(directory, name="h1", behaviours=("exit7", "valid"), family="fam-a")
        second, _ = _route(directory, name="h2", behaviours=("valid",), family="fam-b")
        supply = fx.FakeSupply(
            (first, second),
            reserve_answers=[None, Refusal(downgrade="fallback", axis="per_model_daily_tokens")],
        )
        result, record = _run(state_dir=directory / "state", supply=supply)

        assert isinstance(result, PanelResult) and result.complete is True
        assert len(fx.script_calls(script=first_script)) == 1, "no second invocation"
        assert supply.route_calls[1][1].excluded_families == frozenset({"fam-a"})
        assert result.bound_reached is True
        assert record.of_kind("panel")[0]["bound_reached"] is True


# -- T9 -------------------------------------------------------------------------


def test_t9_two_transients_on_one_route_make_no_third_invocation() -> None:
    with fx.workspace() as raw:
        directory = pathlib.Path(raw)
        route, script = _route(
            directory, name="h1", behaviours=("exit7", "exit7", "valid"), family="fam-a"
        )
        supply = fx.FakeSupply((route,))
        result, _ = _run(state_dir=directory / "state", supply=supply)

        assert isinstance(result, PanelResult)
        assert len(fx.script_calls(script=script)) == 2, "no third invocation"
        assert result.complete is False
        assert result.incomplete_reason == "exhausted"
        assert supply.route_calls[1][1].excluded_routes == frozenset({route})


# -- T10 ------------------------------------------------------------------------


def test_t10_a_first_reservation_refused_incomplete_returns_a_budget_panel() -> None:
    with fx.workspace() as raw:
        directory = pathlib.Path(raw)
        route, script = _route(directory, name="h1", behaviours=("valid",), family="fam-a")
        supply = fx.FakeSupply(
            (route,), reserve_answers=[Refusal(downgrade="incomplete", axis="per_pr_tokens")]
        )
        result, record = _run(state_dir=directory / "state", supply=supply)
        assert isinstance(result, PanelResult)
        assert result.complete is False
        assert result.incomplete_reason == "budget"
        assert result.attempts == ()
        assert result.bound_reached is True
        assert fx.script_calls(script=script) == []
        assert record.of_kind("panel")[0]["incomplete_reason"] == "budget"


def test_t10_an_escalate_refusal_after_one_attempt_keeps_the_cutoff_after_it() -> None:
    with fx.workspace() as raw:
        directory = pathlib.Path(raw)
        first, _ = _route(directory, name="h1", behaviours=("valid",), family="fam-a")
        second, _ = _route(directory, name="h2", behaviours=("valid",), family="fam-b")
        supply = fx.FakeSupply(
            (first, second),
            reserve_answers=[None, Refusal(downgrade="escalate", axis="per_repo_daily_tokens")],
        )
        result, _ = _run(state_dir=directory / "state", supply=supply, participants=2)
        assert isinstance(result, PanelResult)
        assert result.complete is False
        assert result.incomplete_reason == "budget"
        assert len(result.attempts) == 1
        assert result.evidence_cutoff >= result.attempts[-1].attestation.ended_at
        assert result.bound_reached is True


# -- T11 ------------------------------------------------------------------------


def test_t11_route_unavailable_before_completion_is_an_exhausted_panel() -> None:
    with fx.workspace() as raw:
        directory = pathlib.Path(raw)
        supply = fx.FakeSupply(())
        result, record = _run(state_dir=directory / "state", supply=supply)
        assert isinstance(result, PanelResult)
        assert result.complete is False
        assert result.incomplete_reason == "exhausted"
        assert result.attempts == ()
        entry = record.of_kind("panel")[0]
        assert entry["complete"] is False
        assert entry["incomplete_reason"] == "exhausted"
        assert entry["attempts"] == []


# -- T12 ------------------------------------------------------------------------


def test_t12_the_loop_terminates_within_finite_routes_plus_one_retry_each() -> None:
    with fx.workspace() as raw:
        directory = pathlib.Path(raw)
        routes = []
        scripts = []
        for index, family in enumerate(("fam-a", "fam-b", "fam-c")):
            route, script = _route(
                directory, name=f"h{index}", behaviours=("exit7",), family=family
            )
            routes.append(route)
            scripts.append(script)
        supply = fx.FakeSupply(tuple(routes))
        result, _ = _run(state_dir=directory / "state", supply=supply)

        assert isinstance(result, PanelResult)
        assert result.incomplete_reason == "exhausted"
        # Exactly two invocations per route: the attempt and the one permitted retry.
        assert [len(fx.script_calls(script=script)) for script in scripts] == [2, 2, 2]
        assert len(result.attempts) == 6
        assert len(supply.route_calls) == 4


def test_a_supply_port_that_ignores_the_cursor_is_a_programming_error_not_a_loop() -> None:
    """The finiteness argument rests on the cursor being honoured, so a port that hands
    back an excluded route stops the job instead of spinning against it."""

    class IgnoresCursor(fx.FakeSupply):
        def route(self, obligation, cursor):
            self.route_calls.append((obligation, cursor))
            return self.ladder[0], cursor

    with fx.workspace() as raw:
        directory = pathlib.Path(raw)
        route, _ = _route(directory, name="h1", behaviours=("invalid",), family="fam-a")
        supply = IgnoresCursor((route,))
        try:
            _run(state_dir=directory / "state", supply=supply)
        except HarnessError:
            return
        raise AssertionError("an excluded route returned again must raise HarnessError")


# -- independence: which participants count (U-POLICY-09, U-VERDICT-08, U-VERDICT-11) --


def test_two_valid_verdicts_from_one_provider_family_do_not_meet_an_independence_of_two() -> None:
    """U-POLICY-09, kept: participants are discounted *before* counting, so "two responses
    from one provider family satisfy an independence requirement they did not meet" cannot
    happen. U-VERDICT-12's predicate is never upgraded afterwards."""
    with fx.workspace() as raw:
        directory = pathlib.Path(raw)
        first, _ = _route(directory, name="h1", behaviours=("valid",), family="fam-a")
        second, _ = _route(directory, name="h2", behaviours=("valid",), family="fam-a")
        supply = fx.FakeSupply((first, second))
        result, _ = _run(state_dir=directory / "state", supply=supply, participants=2)

        assert isinstance(result, PanelResult)
        assert len(result.attempts) == 2
        assert all(isinstance(attempt.outcome, Verdict) for attempt in result.attempts)
        assert result.complete is False
        assert result.incomplete_reason == "exhausted"


def test_independence_is_counted_from_the_attested_route_not_the_models_self_report() -> None:
    """U-VERDICT-11, kept: "reading the family from the JSON the model produced lets a
    model assert an independence it does not have". Both harnesses here report the
    *identical* identity; the panel completes because RQA's own routes are two families."""
    with fx.workspace() as raw:
        directory = pathlib.Path(raw)
        first, _ = _route(directory, name="h1", behaviours=("valid",), family="fam-a")
        second, _ = _route(directory, name="h2", behaviours=("valid",), family="fam-b")
        result, record = _run(
            state_dir=directory / "state", supply=fx.FakeSupply((first, second)), participants=2
        )
        assert isinstance(result, PanelResult) and result.complete is True
        reported = {entry["self_reported"]["provider"] for entry in record.of_kind("attestation")}
        attested = {entry["attested"]["family"] for entry in record.of_kind("attestation")}
        assert reported == {"self-reported-provider"}, "one self-reported identity"
        assert attested == {"fam-a", "fam-b"}, "two attested families"


def test_a_failed_attempt_never_counts_toward_the_required_participants() -> None:
    with fx.workspace() as raw:
        directory = pathlib.Path(raw)
        failed, _ = _route(directory, name="h1", behaviours=("invalid",), family="fam-a")
        good, _ = _route(directory, name="h2", behaviours=("valid",), family="fam-b")
        result, _ = _run(
            state_dir=directory / "state", supply=fx.FakeSupply((failed, good)), participants=2
        )
        assert isinstance(result, PanelResult)
        assert len(result.attempts) == 2
        assert result.complete is False, "one valid verdict does not fill two participants"


# -- T13 ------------------------------------------------------------------------


def test_t13_consumption_follows_each_invocation_with_its_own_reservation() -> None:
    with fx.workspace() as raw:
        directory = pathlib.Path(raw)
        measured, _ = _route(directory, name="h1", behaviours=("usage:4242",), family="fam-a")
        unmeasured, _ = _route(directory, name="h2", behaviours=("valid",), family="fam-b")
        supply = fx.FakeSupply((measured, unmeasured))
        result, _ = _run(state_dir=directory / "state", supply=supply, participants=2)

        assert isinstance(result, PanelResult) and result.complete is True
        assert [call[1] for call in supply.consumed_calls] == [4242, None]
        assert [call[0].id for call in supply.consumed_calls] == [a.id for a in result.attempts]
        # Each consumption carries the reservation that preceded its own invocation.
        assert len({call[2].id for call in supply.consumed_calls}) == 2


def test_t13_a_failed_attempt_is_still_reported_as_consumed() -> None:
    """§3.2 step 4: `consumed` is called "for every outcome, including timeout or launch
    failure"."""
    with fx.workspace() as raw:
        directory = pathlib.Path(raw)
        route, _ = _route(directory, name="h1", behaviours=("exit2",), family="fam-a")
        supply = fx.FakeSupply((route,))
        result, _ = _run(state_dir=directory / "state", supply=supply)
        assert isinstance(result, PanelResult)
        assert len(supply.consumed_calls) == 1
        assert supply.consumed_calls[0][1] is None


def test_a_missing_harness_script_is_terminal_and_still_reported_as_consumed() -> None:
    """A route pointing at a script that is not there: the interpreter exits non-zero, so
    §3.3's table classifies it, and `consumed` is still called for the attempt."""
    with fx.workspace() as raw:
        directory = pathlib.Path(raw)
        absent = fx.make_route(script=directory / "nope.py", family="fam-a")
        supply = fx.FakeSupply((absent,))
        result, _ = _run(state_dir=directory / "state", supply=supply)
        assert isinstance(result, PanelResult)
        assert result.complete is False
        assert len(supply.consumed_calls) == 1
        # CPython exits 2 when it cannot open the script, so §3.3's table classifies this
        # `PROVIDER_TERMINAL`. The property under test is that a failed attempt is still
        # an `AttemptFailure` from the table and is still reported as consumed.
        assert result.attempts[0].outcome.kind in {"TRANSIENT", "PROVIDER_TERMINAL", "CANDIDATE_TERMINAL"}


# -- T4b ------------------------------------------------------------------------


def test_t4b_a_fallback_refusal_latches_bound_reached_through_a_complete_panel() -> None:
    with fx.workspace() as raw:
        directory = pathlib.Path(raw)
        bounded, bounded_script = _route(directory, name="h1", behaviours=("valid",), family="fam-a")
        fallback, _ = _route(directory, name="h2", behaviours=("valid",), family="fam-b")
        supply = fx.FakeSupply(
            (bounded, fallback),
            reserve_answers=[Refusal(downgrade="fallback", axis="per_model_daily_tokens")],
        )
        result, record = _run(state_dir=directory / "state", supply=supply)

        assert isinstance(result, PanelResult)
        assert result.complete is True
        assert result.bound_reached is True
        assert record.of_kind("panel")[0]["bound_reached"] is True
        # The bounded route was never invoked, and its whole family was excluded.
        assert fx.script_calls(script=bounded_script) == []
        assert supply.route_calls[1][1].excluded_families == frozenset({"fam-a"})


def test_bound_reached_is_false_when_no_reservation_was_ever_refused() -> None:
    with fx.workspace() as raw:
        directory = pathlib.Path(raw)
        route, _ = _route(directory, name="h1", behaviours=("valid",), family="fam-a")
        result, _ = _run(state_dir=directory / "state", supply=fx.FakeSupply((route,)))
        assert isinstance(result, PanelResult)
        assert result.bound_reached is False


# -- T17 ------------------------------------------------------------------------


def _expect_append_failed(kind: str) -> None:
    with fx.workspace() as raw:
        directory = pathlib.Path(raw)
        route, _ = _route(directory, name="h1", behaviours=("valid",), family="fam-a")
        record = fx.FakeRecord(fail_kind=kind)
        try:
            _run(state_dir=directory / "state", supply=fx.FakeSupply((route,)), record=record)
        except AppendFailed:
            return
        raise AssertionError(f"AppendFailed for {kind} did not propagate out of run()")


def test_t17_append_failure_for_the_bundle_entry_propagates() -> None:
    _expect_append_failed("bundle")


def test_t17_append_failure_for_the_attestation_entry_propagates() -> None:
    _expect_append_failed("attestation")


def test_t17_append_failure_for_the_panel_entry_propagates() -> None:
    _expect_append_failed("panel")


def test_t17_no_module_in_the_package_can_catch_append_failed() -> None:
    """Structural, from the AST rather than a text search — these modules discuss
    `AppendFailed` by name in their docstrings precisely because they never catch it.

    Two ways it could be caught: by name, or by an over-broad handler. Neither exists.
    """
    harness = pathlib.Path(__file__).resolve().parent.parent / "rqa" / "harness"
    for module in sorted(harness.glob("*.py")):
        tree = ast.parse(module.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if not isinstance(node, ast.ExceptHandler):
                continue
            caught = node.type
            names: list[str] = []
            if caught is None:
                raise AssertionError(f"{module.name} has a bare except")
            targets = caught.elts if isinstance(caught, ast.Tuple) else [caught]
            for target in targets:
                names.append(ast.unparse(target))
            for name in names:
                assert name not in {"AppendFailed", "Exception", "BaseException"}, (
                    f"{module.name} catches {name}"
                )


# -- named programming errors ---------------------------------------------------


def test_running_with_no_planned_obligation_raises_empty_plan_error() -> None:
    with fx.workspace() as raw:
        directory = pathlib.Path(raw)
        try:
            run(
                job=fx.make_job(),
                plan=fx.make_plan(obligations=()),
                facts=fx.make_facts(),
                snapshot=fx.make_snapshot(),
                supply=fx.FakeSupply(()),
                state_dir=directory,
                record=fx.FakeRecord(),
            )
        except EmptyPlanError:
            return
        raise AssertionError("an empty plan must not produce an invented evidence outcome")


def test_a_route_with_no_adapter_and_no_command_is_a_harness_error() -> None:
    with fx.workspace() as raw:
        directory = pathlib.Path(raw)
        unknown = Route(
            harness="never-registered", model="m", provider="p", family="fam-a", external=False
        )
        try:
            _run(state_dir=directory / "state", supply=fx.FakeSupply((unknown,)))
        except HarnessError:
            return
        raise AssertionError("an unroutable harness must stop the job")


def test_a_reserve_answer_that_is_neither_a_reservation_nor_a_refusal_is_a_harness_error() -> None:
    with fx.workspace() as raw:
        directory = pathlib.Path(raw)
        route, _ = _route(directory, name="h1", behaviours=("valid",), family="fam-a")
        supply = fx.FakeSupply((route,), reserve_answers=["not a reservation"])
        try:
            _run(state_dir=directory / "state", supply=supply)
        except HarnessError:
            return
        raise AssertionError("a nonsense reserve answer must raise rather than be acted on")


# -- T16's run-level half -------------------------------------------------------


def test_t16_a_bundle_failure_creates_no_attempt_and_returns_the_shared_value() -> None:
    with fx.workspace() as raw:
        directory = pathlib.Path(raw)
        state_dir = directory / "state"
        state_dir.mkdir()
        (state_dir / "jobs").write_text("not a directory", encoding="utf-8")
        route, script = _route(directory, name="h1", behaviours=("valid",), family="fam-a")
        supply = fx.FakeSupply((route,))
        result, record = _run(state_dir=state_dir, supply=supply)

        assert isinstance(result, BundleFailure)
        assert record.kinds() == ["bundle"]
        assert record.of_kind("bundle")[0]["status"] == "incomplete"
        assert supply.route_calls == []
        assert fx.script_calls(script=script) == []


def test_a_stale_harness_slot_is_cleared_before_a_new_attempt() -> None:
    """U-VERDICT-12 / U-DOCS-09 / U-DOCS-41: an earlier run's output can never satisfy a
    later attempt."""
    with fx.workspace() as raw:
        directory = pathlib.Path(raw)
        state_dir = directory / "state"
        slot = state_dir / "jobs" / "job-1" / "harness" / "01"
        slot.mkdir(parents=True)
        (slot / "verdict.json").write_text("stale", encoding="utf-8")
        (slot / "leftover.txt").write_text("stale", encoding="utf-8")
        route, _ = _route(directory, name="h1", behaviours=("noverdict",), family="fam-a")
        result, _ = _run(state_dir=state_dir, supply=fx.FakeSupply((route,)))
        assert isinstance(result, PanelResult)
        assert not (slot / "leftover.txt").exists()
        assert result.attempts[0].outcome.kind == "CANDIDATE_TERMINAL"
