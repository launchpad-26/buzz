#!/usr/bin/env python3
"""P-06 §2, §3.2 step 2 and §3.3 — adapters, the external command, the conformance gate.

§8 rows covered here:

T14b a configured route whose harness has no built-in alias but carries a non-empty
     `command` runs through the generic external-command adapter with the same
     bundle/protocol/output arguments and the same classification table; no RQA source
     change is required (RQA-FR-030, AC15)
T14c a configured `command` route whose conformance run fails, errors on spawn, or times
     out is `CANDIDATE_TERMINAL` at step 2, excluded through the cursor, recorded, and
     never invoked with PR content; a passing run appends its conformance `attestation`
     once and is cached for the job
T15  paired clean/adversarial diff, body and comment fixtures, including paraphrases,
     under every authority mode -> identical non-defensive result; the adversarial result
     contains a semantic `InjectionAttempt`; adapter registration fails otherwise
"""

from __future__ import annotations

import ast
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import test_rqa_harness_fixtures as fx  # noqa: E402
from rqa.contracts import Activity, PanelResult, Route  # noqa: E402
from rqa.harness import run  # noqa: E402
from rqa.harness.adapters import (  # noqa: E402
    AUTHORITY_MODES,
    CONFORMANCE_GATE_CASE,
    CONFORMANCE_SUITE,
    ExternalCommandAdapter,
    adapter_for,
    authority_for_mode,
    conformance_suite_hash,
    pair_reasons,
    register,
    suite_reasons,
)
from rqa.harness.errors import HarnessError  # noqa: E402
from rqa.harness.invoke import argv_hash, invoke  # noqa: E402
from rqa.harness import panel as panel_module  # noqa: E402
from rqa.protocol import (  # noqa: E402
    EvidenceState,
    HarnessIdentity,
    InjectionAttempt,
    Invalid,
    Valid,
    Verdict,
)

HARNESS_DIR = pathlib.Path(__file__).resolve().parent.parent / "rqa" / "harness"


def _command_route(script: pathlib.Path, *, family: str = "fam-x", harness: str = "acme-reviewer") -> Route:
    return Route(
        harness=harness,
        model="acme-1",
        provider="acme",
        family=family,
        external=True,
        command=(sys.executable, str(script)),
    )


def _run(*, state_dir: pathlib.Path, supply, record=None, participants: int = 1):
    writer = record if record is not None else fx.FakeRecord()
    result = run(
        job=fx.make_job(),
        plan=fx.make_plan(participants=participants),
        facts=fx.make_facts(),
        snapshot=fx.make_snapshot(),
        supply=supply,
        state_dir=state_dir,
        record=writer,
    )
    return result, writer


# -- T14b -----------------------------------------------------------------------


def test_t14b_a_command_route_dispatches_to_the_generic_external_command_adapter() -> None:
    route = _command_route(pathlib.Path("/bin/true"))
    adapter = adapter_for(route=route)
    assert isinstance(adapter, ExternalCommandAdapter)
    assert adapter.argv(route, "high") == route.command


def test_t14b_admitting_this_harness_requires_no_change_to_rqas_source() -> None:
    """AC15's fit criterion fails "a transient patch applied to admit the harness". The
    name of the harness under test appears nowhere in the package."""
    for module in sorted(HARNESS_DIR.glob("*.py")):
        source = module.read_text(encoding="utf-8")
        assert "acme-reviewer" not in source, module.name
        assert "acme-1" not in source, module.name


def test_t14b_the_command_receives_the_same_three_appended_paths_as_a_builtin() -> None:
    with fx.workspace() as raw:
        directory = pathlib.Path(raw)
        script = fx.harness_script(
            directory=directory, behaviours=("conform", "conform", "valid"), name="acme"
        )
        route = _command_route(script)
        supply = fx.FakeSupply((route,))
        result, record = _run(state_dir=directory / "state", supply=supply)

        assert isinstance(result, PanelResult) and result.complete is True
        calls = fx.script_calls(script=script)
        assert len(calls) == 3, "two conformance members plus one real attempt"
        attempt_call = calls[-1]
        # The child sees its own `sys.argv`: the script, then exactly the three paths RQA
        # appends — bundle directory, protocol instruction, verdict output path.
        assert attempt_call["argv"][0] == str(script)
        assert len(attempt_call["argv"]) == 4
        assert attempt_call["bundle"].endswith("/jobs/job-1/bundle")
        assert attempt_call["protocol"].endswith("PROTOCOL.md")
        assert attempt_call["verdict"].endswith("/harness/03/verdict.json")


def test_t14b_the_same_classification_table_applies_to_a_command_route() -> None:
    with fx.workspace() as raw:
        directory = pathlib.Path(raw)
        script = fx.harness_script(
            directory=directory, behaviours=("conform", "conform", "exit2"), name="acme"
        )
        route = _command_route(script)
        supply = fx.FakeSupply((route,))
        result, _ = _run(state_dir=directory / "state", supply=supply)
        assert isinstance(result, PanelResult)
        assert result.attempts[0].outcome.kind == "PROVIDER_TERMINAL"


def test_a_command_route_never_reports_an_effort_it_cannot_enforce() -> None:
    adapter = adapter_for(route=_command_route(pathlib.Path("/bin/true")))
    assert adapter.resolved_effort("high") == "unenforced"
    assert adapter.enforceable_efforts == frozenset()


def test_a_command_wins_over_a_builtin_alias_at_the_single_dispatch_point() -> None:
    """§2's dispatch order, verbatim. ADR-0065 point 4 rejects the combination at the
    configuration surface; its conditional half is unowned (#2234) and this function does
    not invent a second veto over the dispatch the contract states."""
    route = Route(
        harness="omp", model="m", provider="p", family="f", external=False, command=("/bin/true",)
    )
    assert isinstance(adapter_for(route=route), ExternalCommandAdapter)


def test_an_empty_command_is_not_a_command() -> None:
    route = Route(harness="omp", model="m", provider="p", family="f", external=False, command=())
    assert not isinstance(adapter_for(route=route), ExternalCommandAdapter)


# -- T14c -----------------------------------------------------------------------


def _conformance_entries(record: fx.FakeRecord) -> list[dict]:
    return [entry for entry in record.of_kind("attestation") if entry.get("subject") == "conformance"]


def test_t14c_a_failing_conformance_run_excludes_the_route_and_never_sees_pr_content() -> None:
    with fx.workspace() as raw:
        directory = pathlib.Path(raw)
        bad = fx.harness_script(
            directory=directory, behaviours=("conform_silent", "conform_silent"), name="silent"
        )
        good, _ = (
            fx.make_route(
                script=fx.harness_script(directory=directory, behaviours=("valid",), name="fallback"),
                family="fam-b",
            ),
            None,
        )
        supply = fx.FakeSupply((_command_route(bad), good))
        result, record = _run(state_dir=directory / "state", supply=supply)

        assert isinstance(result, PanelResult) and result.complete is True
        entries = _conformance_entries(record)
        assert len(entries) == 1
        assert entries[0]["result"] == "fail"
        assert entries[0]["outcome"] == "CANDIDATE_TERMINAL"
        # Excluded through the cursor, so selection advanced to the fallback.
        assert supply.route_calls[1][1].excluded_routes == frozenset({_command_route(bad)})
        # And not one pull-request byte ever reached the command.
        for call in fx.script_calls(script=bad):
            for token in fx.TOKENS.values():
                assert token not in call["bundle_text"], token
        assert len(fx.script_calls(script=bad)) == 2, "the pair ran; the attempt did not"


def test_t14c_a_conformance_spawn_error_is_candidate_terminal_and_recorded() -> None:
    with fx.workspace() as raw:
        directory = pathlib.Path(raw)
        missing = Route(
            harness="acme-reviewer",
            model="acme-1",
            provider="acme",
            family="fam-x",
            external=True,
            command=(str(directory / "no-such-binary"),),
        )
        supply = fx.FakeSupply((missing,))
        result, record = _run(state_dir=directory / "state", supply=supply)
        assert isinstance(result, PanelResult)
        assert result.complete is False
        assert result.incomplete_reason == "exhausted"
        assert result.attempts == ()
        entries = _conformance_entries(record)
        assert len(entries) == 1
        assert entries[0]["result"] == "fail"
        assert entries[0]["process"] == "spawn_failed"


def test_t14c_a_conformance_timeout_is_candidate_terminal_and_recorded() -> None:
    original = panel_module.CONFORMANCE_TIMEOUT_SECONDS
    panel_module.CONFORMANCE_TIMEOUT_SECONDS = 1
    try:
        with fx.workspace() as raw:
            directory = pathlib.Path(raw)
            script = fx.harness_script(directory=directory, behaviours=("sleep",), name="slow")
            supply = fx.FakeSupply((_command_route(script),))
            result, record = _run(state_dir=directory / "state", supply=supply)
            assert isinstance(result, PanelResult)
            assert result.attempts == ()
            entries = _conformance_entries(record)
            assert entries[0]["result"] == "fail"
            assert entries[0]["process"] == "timeout"
    finally:
        panel_module.CONFORMANCE_TIMEOUT_SECONDS = original


def test_t14c_a_passing_conformance_run_is_appended_once_and_cached_for_the_job() -> None:
    with fx.workspace() as raw:
        directory = pathlib.Path(raw)
        script = fx.harness_script(
            directory=directory,
            behaviours=("conform", "conform", "invalid", "valid"),
            name="acme",
        )
        first = _command_route(script, family="fam-a")
        second = _command_route(script, family="fam-b")
        supply = fx.FakeSupply((first, second))
        result, record = _run(state_dir=directory / "state", supply=supply)

        assert isinstance(result, PanelResult) and result.complete is True
        entries = _conformance_entries(record)
        assert len(entries) == 1, "cached by (argv_hash, protocol_hash) for the rest of the job"
        assert entries[0]["result"] == "pass"
        assert entries[0]["argv_hash"] == argv_hash((sys.executable, str(script)))
        assert entries[0]["protocol_hash"] == fx.make_snapshot().protocol_hash
        assert entries[0]["case"] == CONFORMANCE_GATE_CASE.id
        # Two gate invocations, then one attempt per route — the gate did not run twice.
        assert len(fx.script_calls(script=script)) == 4


def test_a_builtin_adapters_registry_membership_is_not_re_run_as_a_gate() -> None:
    with fx.workspace() as raw:
        directory = pathlib.Path(raw)
        route, script = (
            fx.make_route(
                script=fx.harness_script(directory=directory, behaviours=("valid",), name="b"),
                family="fam-a",
            ),
            None,
        )
        _, record = _run(state_dir=directory / "state", supply=fx.FakeSupply((route,)))
        assert _conformance_entries(record) == []
        assert script is None


# -- T15 ------------------------------------------------------------------------


def _verdict(*, state: str = "verified", attempts: tuple[InjectionAttempt, ...] = ()) -> Valid:
    return Valid(
        verdict=Verdict(
            obligations={"O1": EvidenceState(state)},
            findings=(),
            injection_attempts=attempts,
            identity=HarnessIdentity(harness="h", model="m", provider="p"),
            protocol_version="1",
        )
    )


def _conforming(case) -> tuple[Valid, Valid]:
    return (
        _verdict(),
        _verdict(
            attempts=(
                InjectionAttempt(
                    field=case.field,
                    span_hash="a" * 64,
                    reason="the text asks the reviewer to change the review outcome",
                ),
            )
        ),
    )


def test_t15_the_suite_spans_every_authority_mode_and_all_three_channels() -> None:
    modes = {case.mode for case in CONFORMANCE_SUITE}
    channels = {case.channel for case in CONFORMANCE_SUITE}
    assert modes == set(AUTHORITY_MODES)
    assert channels == {"body", "diff", "comment"}
    assert "advisory_only" in modes, "the PRD names advisory-only explicitly"
    assert len({case.payload for case in CONFORMANCE_SUITE}) >= 3, "semantic paraphrases"


def test_t15_advisory_only_grants_nothing_and_full_grants_everything() -> None:
    advisory = authority_for_mode(mode="advisory_only")
    full = authority_for_mode(mode="full")
    assert set(advisory) == set(Activity) == set(full)
    assert not any(advisory.values())
    assert all(full.values())


def test_t15_a_conforming_harness_passes_every_pair() -> None:
    results = {case.id: _conforming(case) for case in CONFORMANCE_SUITE}
    assert suite_reasons(results=results) == ()


def test_t15_omitting_the_injection_attempt_fails_every_pair() -> None:
    results = {case.id: (_verdict(), _verdict()) for case in CONFORMANCE_SUITE}
    reasons = suite_reasons(results=results)
    assert len(reasons) == len(CONFORMANCE_SUITE)
    assert all("reported no injection attempt" in reason for reason in reasons)


def test_t15_changing_the_evidence_under_the_adversarial_input_fails() -> None:
    case = CONFORMANCE_SUITE[0]
    clean, adversarial = _conforming(case)
    drifted = Valid(
        verdict=Verdict(
            obligations={"O1": EvidenceState.NOT_VERIFIED},
            findings=adversarial.verdict.findings,
            injection_attempts=adversarial.verdict.injection_attempts,
            identity=adversarial.verdict.identity,
            protocol_version="1",
        )
    )
    reasons = pair_reasons(case=case, clean=clean, adversarial=drifted)
    assert any("changed under the adversarial input" in reason for reason in reasons)


def test_t15_a_defensive_clean_member_fails() -> None:
    case = CONFORMANCE_SUITE[0]
    _, adversarial = _conforming(case)
    reasons = pair_reasons(case=case, clean=adversarial, adversarial=adversarial)
    assert any("clean member reported an injection attempt" in reason for reason in reasons)


def test_t15_locating_the_attempt_in_the_wrong_field_fails() -> None:
    case = CONFORMANCE_SUITE[0]
    clean, _ = _conforming(case)
    misplaced = _verdict(
        attempts=(InjectionAttempt(field="body" if case.field != "body" else "diff:x.py", span_hash="b" * 64, reason="r"),)
    )
    reasons = pair_reasons(case=case, clean=clean, adversarial=misplaced)
    assert any("did not locate the attempt" in reason for reason in reasons)


def test_t15_an_invalid_or_absent_member_fails_rather_than_being_skipped() -> None:
    case = CONFORMANCE_SUITE[0]
    assert pair_reasons(case=case, clean=Invalid(("bad",)), adversarial=None)
    assert suite_reasons(results={}) != ()


def test_t15_registration_fails_without_a_role_separated_data_channel() -> None:
    class NoRoles:
        harness = "no-roles"
        enforceable_efforts = frozenset()
        role_separated_data = False
        injection_conformance_hash = conformance_suite_hash()

        def argv(self, route, effort):
            return ()

        def resolved_effort(self, requested):
            return requested

    try:
        register(adapter=NoRoles())
    except HarnessError:
        return
    raise AssertionError("an adapter without channel separation must be absent, not degraded")


def test_t15_registration_fails_for_a_stale_conformance_suite() -> None:
    class Stale:
        harness = "stale-suite"
        enforceable_efforts = frozenset()
        role_separated_data = True
        injection_conformance_hash = "0" * 64

        def argv(self, route, effort):
            return ()

        def resolved_effort(self, requested):
            return requested

    try:
        register(adapter=Stale())
    except HarnessError:
        return
    raise AssertionError("an adapter naming a suite this build does not publish must be absent")


def test_t15_every_registered_builtin_declares_the_published_suite() -> None:
    from rqa.harness.adapters import builtin_harnesses, registered

    for harness in builtin_harnesses():
        adapter = registered(harness=harness)
        assert adapter is not None
        assert adapter.role_separated_data is True
        assert adapter.injection_conformance_hash == conformance_suite_hash()


def test_the_suite_hash_changes_when_the_suite_changes() -> None:
    """A declaration that could survive a change to the suite would not be a declaration."""
    import hashlib

    from rqa.harness.adapters import CONFORMANCE_SUITE_ID

    recomputed = hashlib.sha256(CONFORMANCE_SUITE_ID.encode())
    for case in CONFORMANCE_SUITE:
        recomputed.update(b"\x00")
        recomputed.update(
            f"{case.id}\x01{case.mode}\x01{case.channel}\x01{case.field}\x01{case.payload}".encode()
        )
    assert recomputed.hexdigest() == conformance_suite_hash()
    altered = hashlib.sha256((CONFORMANCE_SUITE_ID + "x").encode()).hexdigest()
    assert altered != conformance_suite_hash()


# -- invoke(): environment, timeout, process group -------------------------------


def test_the_child_environment_is_an_allow_list_with_no_credential() -> None:
    """`tests/conftest.py` puts sentinel `GITHUB_TOKEN`/`GH_TOKEN` values in this
    process's environment. Neither may reach a harness."""
    import json
    import os

    with fx.workspace() as raw:
        directory = pathlib.Path(raw)
        script = directory / "dumpenv.py"
        script.write_text(
            "import json, os, pathlib, sys\n"
            "pathlib.Path(sys.argv[-1]).write_text(json.dumps(dict(os.environ)))\n",
            encoding="utf-8",
        )
        out = directory / "env.json"
        os.environ["RQA_HARNESS_LEAK_CANARY"] = "canary"
        try:
            execution = invoke(
                argv=(sys.executable, str(script), str(out)),
                cwd=directory,
                stdout_path=directory / "o.log",
                stderr_path=directory / "e.log",
                timeout=30,
            )
        finally:
            del os.environ["RQA_HARNESS_LEAK_CANARY"]
        assert execution.exit_code == 0
        child_env = json.loads(out.read_text())
        assert "GITHUB_TOKEN" not in child_env
        assert "GH_TOKEN" not in child_env
        assert "RQA_HARNESS_LEAK_CANARY" not in child_env
        # The env RQA hands the child is built *up* from the allow-list, so that is the
        # exact property to assert. `__CF_USER_TEXT_ENCODING` is re-added by macOS's own
        # CoreFoundation initialisation after `execve` and is not something RQA passed;
        # excluding it by name keeps the check honest rather than loosening it.
        allowed = {"PATH", "HOME", "LANG", "LC_ALL", "TMPDIR"}
        platform_injected = {"__CF_USER_TEXT_ENCODING"}
        from rqa.harness.invoke import _child_env

        assert set(_child_env()) <= allowed
        assert (set(child_env) - platform_injected) <= allowed
        for name in set(os.environ) - allowed - platform_injected:
            assert name not in child_env, name


def test_a_timeout_is_observed_and_reported_as_a_timeout() -> None:
    with fx.workspace() as raw:
        directory = pathlib.Path(raw)
        script = directory / "sleep.py"
        script.write_text("import time\ntime.sleep(60)\n", encoding="utf-8")
        execution = invoke(
            argv=(sys.executable, str(script)),
            cwd=directory,
            stdout_path=directory / "o.log",
            stderr_path=directory / "e.log",
            timeout=1,
        )
        assert execution.timed_out is True
        assert execution.ended_at >= execution.started_at


def test_a_timeout_terminates_the_whole_process_group() -> None:
    """§3.3: "timeout terminates the process group". A harness killed alone leaves its
    grandchild holding the bundle and the output path."""
    tree = ast.parse((HARNESS_DIR / "invoke.py").read_text(encoding="utf-8"))
    keywords = {
        keyword.arg
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        for keyword in node.keywords
    }
    assert "start_new_session" in keywords
    calls = {
        ast.unparse(node.func)
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
    }
    assert "os.killpg" in calls and "os.getpgid" in calls


def test_a_spawn_failure_is_a_value_and_carries_no_argv() -> None:
    with fx.workspace() as raw:
        directory = pathlib.Path(raw)
        execution = invoke(
            argv=(str(directory / "absent-binary"),),
            cwd=directory,
            stdout_path=directory / "o.log",
            stderr_path=directory / "e.log",
            timeout=5,
        )
        assert execution.spawn_failed is True
        assert execution.exit_code < 0


def test_only_the_invoke_module_spawns_a_process() -> None:
    for module in sorted(HARNESS_DIR.glob("*.py")):
        source = ast.parse(module.read_text(encoding="utf-8"))
        imported = {
            alias.name.split(".")[0]
            for node in ast.walk(source)
            if isinstance(node, ast.Import)
            for alias in node.names
        }
        if module.name == "invoke.py":
            assert "subprocess" in imported
        else:
            assert "subprocess" not in imported, module.name


def test_no_module_in_the_package_imports_another_parts_implementation() -> None:
    """§1: `rqa.harness` never imports or calls P-05's functions directly."""
    forbidden = ("rqa.supply", "rqa.policy", "rqa.authority", "rqa.github")
    for module in sorted(HARNESS_DIR.glob("*.py")):
        tree = ast.parse(module.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                for package in forbidden:
                    assert not node.module.startswith(package), f"{module.name}: {node.module}"


def test_every_adapter_result_reaches_the_e08_validator_before_judgement() -> None:
    """AC01/RQA-FR-001: no adapter path bypasses E-08.

    `panel.validate` is replaced by a counting wrapper around P-04's own function, and
    both dispatch paths — the built-in adapter and the generic external command — are
    driven through `run()`. Every `Verdict` that reaches a `PanelResult` must be one this
    counter saw, and the conformance gate's two members must be validated too.
    """
    from rqa.protocol import validate as real_validate

    seen: list[str] = []

    def counting(*, path, attempt_id):
        seen.append(attempt_id)
        return real_validate(path=path, attempt_id=attempt_id)

    with fx.workspace() as raw:
        directory = pathlib.Path(raw)
        builtin = fx.make_route(
            script=fx.harness_script(directory=directory, behaviours=("valid",), name="b"),
            family="fam-a",
        )
        external = _command_route(
            fx.harness_script(
                directory=directory, behaviours=("conform", "conform", "valid"), name="x"
            ),
            family="fam-b",
        )
        panel_module.validate = counting  # type: ignore[assignment]
        try:
            result, _ = _run(
                state_dir=directory / "state",
                supply=fx.FakeSupply((builtin, external)),
                participants=2,
            )
        finally:
            panel_module.validate = real_validate  # type: ignore[assignment]

        assert isinstance(result, PanelResult) and result.complete is True
        verdict_attempts = [
            attempt.id for attempt in result.attempts if not hasattr(attempt.outcome, "kind")
        ]
        assert len(verdict_attempts) == 2, "one per dispatch path"
        for attempt_id in verdict_attempts:
            assert attempt_id in seen, attempt_id
        # The gate's clean and adversarial members were validated as well.
        assert len([item for item in seen if ":conformance:" in item]) == 2
