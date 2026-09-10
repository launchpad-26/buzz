#!/usr/bin/env python3
"""Integration tests for the reviewer runner adapters and the onboarding route probe.

No live model is called anywhere in this file, and nothing is mutated. Two
techniques replace a real provider:

* `_fake_bin` writes a real executable named `omp` / `claude` / `codex` into a
  temporary directory and points `PATH` at ONLY that directory, so the probe
  spawns a genuine subprocess whose behaviour the test chose. The real
  CLIs on this machine are unreachable for the duration.
* `_no_bin` points `PATH` at an EMPTY directory, so every adapter binary is
  genuinely absent. That is a constructed absence, not a skip: the tests assert
  the absence is classified and the route is left unqualified. No test in this
  file no-ops when a binary is missing.

Both are deterministic on any machine, whether or not the real CLIs are
installed.
"""

from __future__ import annotations

import contextlib
import io
import json
import os
import pathlib
import shutil
import stat
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import ledger as ledgermod  # noqa: E402
import route_probe  # noqa: E402
import runners  # noqa: E402
from common import State  # noqa: E402
from errors import JobBlockingError  # noqa: E402
from runners import (  # noqa: E402
    ADAPTERS,
    PROFILE_EFFORTS,
    EffortUnsupportedError,
    UnknownRunnerError,
    adapter_for,
    build_invocation,
    supported_runners,
)

_REPO = "/tmp/some-repo"
_PROMPT = "review this patch"

_ENTRIES = {
    "omp": {"runner": "omp", "selector": "some/diverse-model", "provider_family": "meta",
            "capability": "workhorse", "efforts": ["medium"]},
    "claude": {"runner": "claude", "selector": "claude-opus-4-5", "provider_family": "anthropic",
               "capability": "frontier", "efforts": ["high"]},
    "codex": {"runner": "codex", "selector": "gpt-5.6-sol", "provider_family": "openai",
              "capability": "frontier", "efforts": ["high"]},
}


def _pairs(cmd: tuple[str, ...], flag: str) -> list[str]:
    """Every argument that immediately follows `flag`. Adjacency matters: a
    selector that is present but detached from its flag is not passed to the CLI."""
    return [cmd[i + 1] for i, token in enumerate(cmd) if token == flag and i + 1 < len(cmd)]


#: The system directories the tests still need (`sh`, `cat`, `git`). None of the
#: three adapter CLIs installs here, and `_no_bin` asserts that rather than
#: assuming it.
_SYSTEM_PATH = "/usr/bin:/bin:/usr/sbin:/sbin"

_ADAPTER_BINARIES = ("omp", "claude", "codex")


@contextlib.contextmanager
def _path_only(directory: pathlib.Path):
    previous = os.environ.get("PATH", "")
    os.environ["PATH"] = f"{directory}:{_SYSTEM_PATH}"
    try:
        yield
    finally:
        os.environ["PATH"] = previous


@contextlib.contextmanager
def _fake_bin(script_body: str):
    """Install a fake `omp`, `claude` and `codex` ahead of everything on PATH.

    The fakes shadow any real CLI, so no live model can be reached from inside
    this context; the assertion below fails loudly if one is still resolvable.
    """
    directory = pathlib.Path(tempfile.mkdtemp())
    for name in _ADAPTER_BINARIES:
        target = directory / name
        target.write_text(script_body, encoding="utf-8")
        target.chmod(target.stat().st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
    with _path_only(directory):
        for name in _ADAPTER_BINARIES:
            assert shutil.which(name) == str(directory / name), (
                f"{name} did not resolve to the fake; refusing to risk a live call"
            )
        yield directory


@contextlib.contextmanager
def _no_bin():
    """A PATH on which every adapter binary is genuinely absent.

    This is a constructed absence, not a skip. If an adapter is somehow still
    resolvable the test FAILS rather than passing vacuously.
    """
    directory = pathlib.Path(tempfile.mkdtemp())
    with _path_only(directory):
        for name in _ADAPTER_BINARIES:
            assert shutil.which(name) is None, (
                f"{name} is still on PATH; the absence case cannot be exercised"
            )
        yield directory


_GOOD_VERDICT = json.dumps({
    "signal": "SUPPORTED", "recommendation": "clean", "summary": "no defects",
    "findings": [], "good": ["clear naming"], "missing_evidence": [],
})


# --------------------------------------------------------------------------
# 1. command construction: exact alias, exact effort, real read-only flags
# --------------------------------------------------------------------------


def test_every_supported_runner_has_an_adapter_and_no_others_exist() -> None:
    assert supported_runners() == ["claude", "codex", "omp"]
    for name in supported_runners():
        assert adapter_for(name).name == name


def test_the_omp_command_targets_the_exact_alias_and_effort_read_only() -> None:
    invocation = build_invocation(_ENTRIES["omp"], _PROMPT, "xhigh", _REPO)
    cmd = invocation.cmd
    assert cmd[0] == "omp"
    assert _pairs(cmd, "--model") == ["some/diverse-model"]
    assert _pairs(cmd, "--thinking") == ["xhigh"]
    assert "--no-tools" in cmd and "--no-session" in cmd
    assert f"--cwd={_REPO}" in cmd
    assert cmd[-1] == _PROMPT
    assert invocation.effort_enforced is True
    assert invocation.selector == "some/diverse-model"


def test_the_claude_command_is_plan_mode_with_write_tools_denied() -> None:
    invocation = build_invocation(_ENTRIES["claude"], _PROMPT, "high", _REPO)
    cmd = invocation.cmd
    assert cmd[0] == "claude"
    assert _pairs(cmd, "--model") == ["claude-opus-4-5"]
    assert _pairs(cmd, "--permission-mode") == ["plan"]
    assert _pairs(cmd, "--add-dir") == [_REPO]
    denied = cmd[cmd.index("--disallowed-tools") + 1: cmd.index("--add-dir")]
    assert set(denied) == {"Edit", "Write", "NotebookEdit"}
    assert cmd[-1] == _PROMPT
    # This CLI has no reasoning-effort flag, so nothing in the command may claim one.
    assert not any(token.startswith("--thinking") or "reasoning_effort" in token for token in cmd)
    assert invocation.effort_enforced is False


def test_the_codex_command_is_sandboxed_read_only_at_the_requested_effort() -> None:
    invocation = build_invocation(_ENTRIES["codex"], _PROMPT, "high", _REPO)
    cmd = invocation.cmd
    assert cmd[0] == "codex" and cmd[1] == "exec"
    assert _pairs(cmd, "--sandbox") == ["read-only"]
    assert _pairs(cmd, "-m") == ["gpt-5.6-sol"]
    assert _pairs(cmd, "-C") == [_REPO]
    assert _pairs(cmd, "-c") == ['model_reasoning_effort="high"']
    assert "--skip-git-repo-check" in cmd
    assert cmd[-1] == _PROMPT
    assert invocation.effort_enforced is True


def test_each_adapter_targets_the_effort_it_was_given_not_a_default() -> None:
    for effort in PROFILE_EFFORTS:
        omp = build_invocation(_ENTRIES["omp"], _PROMPT, effort, _REPO)
        assert _pairs(omp.cmd, "--thinking") == [effort]
        assert omp.effort == effort
        codex = build_invocation(_ENTRIES["codex"], _PROMPT, effort, _REPO)
        assert _pairs(codex.cmd, "-c") == [f'model_reasoning_effort="{effort}"']
        assert codex.effort == effort


def test_the_prompt_is_one_argument_and_is_never_shell_interpolated() -> None:
    """The command is an argv tuple, so prompt content cannot become shell syntax.
    A prompt full of metacharacters must arrive verbatim as a single element."""
    hostile = 'review "; rm -rf / #\n$(whoami) `id` && echo pwned'
    for runner, entry in _ENTRIES.items():
        cmd = build_invocation(entry, hostile, "medium", _REPO).cmd
        assert isinstance(cmd, tuple)
        assert cmd[-1] == hostile
        assert sum(1 for token in cmd if token == hostile) == 1, runner


def test_the_recorded_read_only_proof_names_flags_the_command_actually_carries() -> None:
    """A proof that cites a flag the command does not pass is a false audit trail."""
    for runner, entry in _ENTRIES.items():
        invocation = build_invocation(entry, _PROMPT, "medium", _REPO)
        assert invocation.read_only_proof
        for proof in invocation.read_only_proof:
            for token in proof.split():
                assert token in invocation.cmd, (runner, proof, token)


# --------------------------------------------------------------------------
# 2. effort honesty
# --------------------------------------------------------------------------


def test_a_transport_that_cannot_enforce_effort_never_reports_it_enforced() -> None:
    assert ADAPTERS["claude"].enforceable_efforts == ()
    for effort in PROFILE_EFFORTS:
        assert build_invocation(_ENTRIES["claude"], _PROMPT, effort, _REPO).effort_enforced is False


def test_requiring_enforced_effort_refuses_a_transport_that_cannot_apply_it() -> None:
    """Running at an unknown effort while the route claims the assurance axis is
    the failure. Refusing the route is the alternative."""
    for effort in PROFILE_EFFORTS:
        try:
            build_invocation(_ENTRIES["claude"], _PROMPT, effort, _REPO,
                             require_effort_enforced=True)
        except EffortUnsupportedError as exc:
            assert "claude" in str(exc) and "none" in str(exc)
        else:  # pragma: no cover
            raise AssertionError(f"claude must not claim enforced effort {effort}")
    # ...and the transports that CAN enforce it are still accepted.
    for runner in ("omp", "codex"):
        for effort in PROFILE_EFFORTS:
            invocation = build_invocation(_ENTRIES[runner], _PROMPT, effort, _REPO,
                                          require_effort_enforced=True)
            assert invocation.effort_enforced is True


def test_an_effort_outside_the_profile_scale_is_not_reported_enforced() -> None:
    for effort in ("ultra", "max", "HIGH", "", "9"):
        for runner in ("omp", "codex", "claude"):
            invocation = build_invocation(_ENTRIES[runner], _PROMPT, effort, _REPO)
            assert invocation.effort_enforced is False, (runner, effort)
            try:
                build_invocation(_ENTRIES[runner], _PROMPT, effort, _REPO,
                                 require_effort_enforced=True)
            except EffortUnsupportedError:
                continue
            raise AssertionError(f"{runner} must not claim enforced effort {effort!r}")


# --------------------------------------------------------------------------
# 3. an unknown runner is rejected at onboarding, not at dispatch
# --------------------------------------------------------------------------


def test_an_unknown_runner_is_refused_when_the_command_is_built() -> None:
    for runner in ("gemini", "OMP", "codex-cli", "", None, "  "):
        try:
            adapter_for(runner)
        except UnknownRunnerError as exc:
            assert "unknown runner" in str(exc)
        else:  # pragma: no cover
            raise AssertionError(f"runner {runner!r} must be refused")
        try:
            build_invocation({"runner": runner, "selector": "m"}, _PROMPT, "medium", _REPO)
        except UnknownRunnerError:
            continue
        raise AssertionError(f"runner {runner!r} must be refused before any spawn")


def test_a_candidate_with_no_selector_is_refused_rather_than_run_blank() -> None:
    for selector in ("", "   ", None):
        try:
            build_invocation({"runner": "codex", "selector": selector}, _PROMPT, "high", _REPO)
        except UnknownRunnerError as exc:
            assert "selector" in str(exc)
        else:  # pragma: no cover
            raise AssertionError(f"selector {selector!r} must be refused")


def test_an_unknown_runner_is_a_config_error_and_never_spawns_a_process() -> None:
    """`probe_route` must classify it before `subprocess.run`. With an empty PATH
    a spawn would surface as `transport_failed`, so `config_error` is proof that
    no process was attempted."""
    with _no_bin():
        result = route_probe.probe_route(
            {"runner": "gemini", "selector": "gemini-3"}, "medium", repo_path=_REPO)
    assert result["status"] == route_probe.CONFIG_ERROR
    assert "unknown runner" in result["detail"]
    assert "elapsed_seconds" not in result


def test_the_panel_treats_an_unknown_runner_as_job_blocking_not_a_candidate_failure() -> None:
    """Dispatch must not silently fall through to the next candidate: a misspelled
    runner is an operator's configuration error and has to reach them.

    Asserted against the live path (`panel._run_reviewer`), not a re-implementation,
    and with an empty PATH so a spawn would be visible as a different failure."""
    import panel

    out = pathlib.Path(tempfile.mkdtemp()) / "verdict.json"
    with _no_bin():
        for runner in ("gemini", "", "OMP"):
            try:
                panel._run_reviewer({"runner": runner, "selector": "m"}, _PROMPT, out,
                                    "medium", _REPO, 5)
            except JobBlockingError as exc:
                assert "unknown runner" in str(exc)
            else:  # pragma: no cover
                raise AssertionError(f"runner {runner!r} must block the job")
            assert not out.exists(), runner
        # An effort the transport cannot enforce is a candidate concern, not a
        # blocking one, so the panel builds the command and only the SPAWN fails.
        try:
            panel._run_reviewer(dict(_ENTRIES["claude"]), _PROMPT, out, "high", _REPO, 5)
        except JobBlockingError:  # pragma: no cover
            raise AssertionError("an absent binary must not be reported as a config error")
        except OSError:
            pass


# --------------------------------------------------------------------------
# 4. the smoke probe: strict verdict parsing against a real subprocess
# --------------------------------------------------------------------------


def _probe(runner: str = "codex", effort: str = "high", timeout: int = 20) -> dict:
    return route_probe.probe_route(_ENTRIES[runner], effort, repo_path=_REPO, timeout=timeout)


def test_the_control_a_conforming_response_qualifies_the_route() -> None:
    """Without this control, a probe that rejected everything would pass every
    counterexample below while qualifying no route at all."""
    with _fake_bin(f"#!/bin/sh\ncat <<'JSON'\n{_GOOD_VERDICT}\nJSON\n"):
        result = _probe()
    assert result["status"] == route_probe.OK, result
    assert result["effort_enforced"] is True
    assert result["read_only_proof"] == ["--sandbox read-only"]


def test_a_response_that_is_not_a_valid_verdict_never_qualifies_the_route() -> None:
    truncated = _GOOD_VERDICT[: len(_GOOD_VERDICT) // 2]
    schema_violating = json.dumps({"signal": "SUPPORTED", "summary": "ok"})
    wrong_enum = json.dumps({**json.loads(_GOOD_VERDICT), "signal": "LGTM"})
    fenced = f"Here you go:\n```json\n{_GOOD_VERDICT}\n```\nHope that helps!"
    for body, why in (
        ("", "empty output"),
        ("   \n", "whitespace only"),
        ("I reviewed it and found no defects.", "prose instead of JSON"),
        (truncated, "truncated JSON"),
        (schema_violating, "missing required fields"),
        (wrong_enum, "signal outside the enum"),
        ("[]", "wrong top-level type"),
        (fenced, "fenced with commentary"),
    ):
        with _fake_bin("#!/bin/sh\ncat <<'OUT'\n" + body + "\nOUT\n"):
            result = _probe()
        assert result["status"] == route_probe.VERDICT_REJECTED, (why, result)
        assert result["detail"], why


def test_a_nonzero_exit_is_a_transport_failure_not_a_rejected_verdict() -> None:
    """The two must not be conflated: one means the CLI broke, the other means the
    model did not comply. Only the second says anything about the model."""
    with _fake_bin(f"#!/bin/sh\necho 'auth expired' >&2\nexit 7\n"):
        result = _probe()
    assert result["status"] == route_probe.TRANSPORT_FAILED
    assert "exit 7" in result["detail"] and "auth expired" in result["detail"]


def test_a_conforming_verdict_on_stderr_does_not_qualify_the_route() -> None:
    """The verdict is read from stdout. A CLI that only logs it must not pass."""
    with _fake_bin(f"#!/bin/sh\ncat >&2 <<'JSON'\n{_GOOD_VERDICT}\nJSON\n"):
        result = _probe()
    assert result["status"] == route_probe.VERDICT_REJECTED


def test_a_route_that_does_not_answer_in_time_is_a_timeout_not_a_pass() -> None:
    with _fake_bin("#!/bin/sh\nsleep 30\n"):
        result = route_probe.probe_route(_ENTRIES["codex"], "high", repo_path=_REPO, timeout=1)
    assert result["status"] == route_probe.TIMEOUT
    assert result["effort_enforced"] is True
    assert "within 1s" in result["detail"]


def test_the_probe_never_raises_whatever_the_transport_does() -> None:
    """A probe that raised would abort onboarding on the first bad route instead of
    reporting which routes are usable."""
    for body in ("#!/bin/sh\nexit 1\n", "#!/bin/sh\nkill -9 $$\n", "not-an-executable-format\n"):
        with _fake_bin(body):
            result = _probe(timeout=10)
        assert result["status"] in (route_probe.TRANSPORT_FAILED, route_probe.VERDICT_REJECTED)


# --------------------------------------------------------------------------
# 5. an absent adapter binary leaves the route unqualified
# --------------------------------------------------------------------------


def test_an_absent_adapter_binary_is_classified_never_ignored() -> None:
    with _no_bin():
        for runner in ("omp", "claude", "codex"):
            result = route_probe.probe_route(_ENTRIES[runner], "high", repo_path=_REPO)
            assert result["status"] == route_probe.TRANSPORT_FAILED, runner
            assert result["detail"], runner


def _configured_repo() -> tuple[pathlib.Path, dict]:
    import subprocess as sp

    import config as cfgmod

    root = pathlib.Path(tempfile.mkdtemp()).resolve()
    sp.run(["git", "init", "-q"], cwd=root, check=True, capture_output=True)
    (root / ".gitignore").write_text(".review-queue-automation/\npr review logs\n",
                                     encoding="utf-8")
    (root / cfgmod.DEFAULT_LOG_DIR_NAME).mkdir(exist_ok=True)
    cfg = cfgmod.onboarding_defaults(root)
    cfg["login"] = "op"
    cfg["repository"]["slug"] = "o/r"
    cfg["state_dir"] = str(root / ".state")
    cfg["models"]["primary"] = [_ENTRIES["codex"]]
    cfg["models"]["secondary"] = [_ENTRIES["claude"]]
    assert cfgmod.validate_config(cfg, root) == []
    path = cfgmod.repo_config_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(cfg), encoding="utf-8")
    return root, cfg


def _run_probe_main(args: list[str]) -> tuple[int, dict]:
    """Run the onboarding probe entry point and return (exit code, report).

    Output is captured rather than printed so the report can be asserted on — the
    exit code alone does not say WHY a repo was rejected.
    """
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        code = route_probe.main(args)
    return code, json.loads(buffer.getvalue())


def test_onboarding_refuses_a_configured_route_that_cannot_run_the_smoke_prompt() -> None:
    """The acceptance criterion: a route whose binary is absent leaves the repo
    unqualified and shadow-locked, and the probe exits nonzero."""
    root, cfg = _configured_repo()
    with _no_bin():
        code, report = _run_probe_main(["--repo-root", str(root), "--json"])
    assert code == 1

    state = State(cfg)
    row = state.db.execute(
        "SELECT status FROM route_qualifications WHERE scope=?", ("o/r",)).fetchone()
    assert row is None, "an unusable route must never be recorded as qualified"
    unavailable = state.db.execute(
        "SELECT key, unavailable_until, last_error FROM providers").fetchall()
    assert unavailable, "a failed probe must record the transport as unavailable"
    for provider in unavailable:
        assert provider["unavailable_until"], provider["key"]
        assert provider["last_error"], provider["key"]
    state.close()


def test_onboarding_refuses_a_repo_whose_configured_runner_has_no_adapter() -> None:
    import config as cfgmod

    root, cfg = _configured_repo()
    cfg["models"]["primary"] = [{**_ENTRIES["codex"], "runner": "gemini"}]
    cfgmod.repo_config_path(root).write_text(json.dumps(cfg), encoding="utf-8")
    with _no_bin():
        code, report = _run_probe_main(["--repo-root", str(root), "--json"])
    assert code == 1
    state = State(cfg)
    assert state.db.execute(
        "SELECT status FROM route_qualifications WHERE scope=?", ("o/r",)).fetchone() is None
    state.close()


def test_onboarding_refuses_a_repo_with_no_configured_routes_at_all() -> None:
    import config as cfgmod

    root, cfg = _configured_repo()
    cfg["models"]["primary"] = []
    cfg["models"]["secondary"] = []
    cfgmod.repo_config_path(root).write_text(json.dumps(cfg), encoding="utf-8")
    with _no_bin():
        code, report = _run_probe_main(["--repo-root", str(root), "--json"])
    assert code == 1
    # The reason has to be legible: "zero routes, all of them usable" is a true
    # statement and a useless one, so the probe must name the real condition.
    assert report["status"] == "no_routes_configured", report
    assert "not runtime-ready" in report["detail"]


def test_onboarding_qualifies_the_repo_only_when_every_route_passes() -> None:
    """The control for the two refusals above, and the counterexample for
    "one good route is enough": a mixed result must stay unqualified.

    Note the asymmetry this pins down: `route_probe.main` PERSISTS a qualification
    only on a clean sweep, and reports `unqualified` without clearing the earlier
    row. The report and the exit code are the rejection; the stale
    `route_qualifications` row is reported as a gap, not asserted as correct."""
    root, cfg = _configured_repo()
    with _fake_bin(f"#!/bin/sh\ncat <<'JSON'\n{_GOOD_VERDICT}\nJSON\n"):
        code, report = _run_probe_main(["--repo-root", str(root), "--json"])
    assert code == 0, report
    assert report["all_usable"] is True and report["usable"] == 2
    assert report["qualification"]["status"] == "qualified"
    state = State(cfg)
    row = state.db.execute(
        "SELECT status FROM route_qualifications WHERE scope=?", ("o/r",)).fetchone()
    assert row is not None and row["status"] == "qualified"
    state.close()

    # Now make exactly one of the two configured routes fail.
    mixed = "#!/bin/sh\ncase \"$0\" in *codex) cat <<'JSON'\n" + _GOOD_VERDICT + \
            "\nJSON\n;; *) exit 3 ;; esac\n"
    with _fake_bin(mixed):
        code, report = _run_probe_main(["--repo-root", str(root), "--json"])
    assert code == 1, report
    assert report["all_usable"] is False
    assert report["usable"] == 1 and report["probed"] == 2
    assert report["qualification"] == {"status": "unqualified", "shadow_locked": True}
    state = State(cfg)
    broken = state.db.execute(
        "SELECT unavailable_until, last_error FROM providers WHERE key=?",
        ("anthropic:claude-opus-4-5",)).fetchone()
    assert broken is not None and broken["unavailable_until"], "the failed route must cool down"
    working = state.db.execute(
        "SELECT unavailable_until FROM providers WHERE key=?",
        ("openai:gpt-5.6-sol",)).fetchone()
    assert working is not None and working["unavailable_until"] is None
    state.close()


# --------------------------------------------------------------------------
# 6. adapter metadata survives into the ledger
# --------------------------------------------------------------------------


def test_adapter_metadata_reaches_the_ledger_intact() -> None:
    """Model, effort, enforcement and read-only proof must be reconstructable from
    the ledger alone; an audit cannot re-run the review to find out."""
    state = State({"state_dir": tempfile.mkdtemp()})
    invocation = build_invocation(_ENTRIES["claude"], _PROMPT, "high", _REPO)
    meta = invocation.as_meta()
    assert meta == {
        "runner": "claude",
        "selector": "claude-opus-4-5",
        "effort": "high",
        "effort_enforced": False,
        "read_only_proof": ["--permission-mode plan",
                            "--disallowed-tools Edit Write NotebookEdit"],
    }

    ledgermod.record(
        state, job_id="job-1", repo="o/r", number=9, head_sha="a" * 40,
        kind=ledgermod.ROUTE, payload=meta, entry_key="reviewer_a",
        snapshot_hash="snap-1", policy_version="p1",
    )
    stored = ledgermod.entries(state, "job-1", kind=ledgermod.ROUTE)
    assert len(stored) == 1
    assert stored[0]["payload"] == meta
    assert stored[0]["snapshot_hash"] == "snap-1"
    assert stored[0]["policy_version"] == "p1"

    report = ledgermod.explain(state, "job-1")
    rendered = ledgermod.render_explanation(report)
    assert "claude:claude-opus-4-5" in rendered
    assert "effort=high" in rendered
    assert "[effort NOT enforced]" in rendered
    state.close()


def test_an_enforced_effort_is_not_annotated_as_unenforced() -> None:
    """Guards the guard: if the annotation were unconditional it would carry no
    information."""
    state = State({"state_dir": tempfile.mkdtemp()})
    meta = build_invocation(_ENTRIES["codex"], _PROMPT, "high", _REPO).as_meta()
    assert meta["effort_enforced"] is True
    ledgermod.record(state, job_id="job-2", repo="o/r", number=9, head_sha="a" * 40,
                     kind=ledgermod.ROUTE, payload=meta)
    rendered = ledgermod.render_explanation(ledgermod.explain(state, "job-2"))
    assert "codex:gpt-5.6-sol" in rendered
    assert "[effort NOT enforced]" not in rendered
    state.close()


def test_a_ledger_entry_without_an_exact_revision_is_refused() -> None:
    """Route metadata attributed to no particular revision would appear to explain
    a decision it may not belong to."""
    state = State({"state_dir": tempfile.mkdtemp()})
    meta = build_invocation(_ENTRIES["codex"], _PROMPT, "high", _REPO).as_meta()
    for missing in ({"job_id": ""}, {"repo": ""}, {"head_sha": ""}):
        kwargs = {"job_id": "job-3", "repo": "o/r", "number": 9, "head_sha": "a" * 40,
                  "kind": ledgermod.ROUTE, "payload": meta}
        kwargs.update(missing)
        try:
            ledgermod.record(state, **kwargs)
        except ledgermod.LedgerError:
            continue
        raise AssertionError(f"a ledger entry missing {missing} must be refused")
    try:
        ledgermod.record(state, job_id="job-3", repo="o/r", number=9, head_sha="a" * 40,
                         kind="invocation", payload=meta)
    except ledgermod.LedgerError as exc:
        assert "unknown ledger kind" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("an unknown ledger kind must be refused")
    state.close()


def test_the_probe_result_carries_the_same_effort_and_proof_the_command_used() -> None:
    """A recorded probe must describe the invocation that actually ran, so the
    ledger and the probe report cannot disagree about a route's guarantees."""
    with _fake_bin(f"#!/bin/sh\ncat <<'JSON'\n{_GOOD_VERDICT}\nJSON\n"):
        for runner in ("omp", "claude", "codex"):
            invocation = build_invocation(_ENTRIES[runner], route_probe.SMOKE_PROMPT,
                                          "high", _REPO)
            result = route_probe.probe_route(_ENTRIES[runner], "high", repo_path=_REPO,
                                             timeout=20)
            assert result["status"] == route_probe.OK, runner
            assert result["effort"] == "high"
            assert result["effort_enforced"] == invocation.effort_enforced, runner
            assert result["read_only_proof"] == list(invocation.read_only_proof), runner
            assert result["route"] == f"{runner}:{_ENTRIES[runner]['selector']}"
