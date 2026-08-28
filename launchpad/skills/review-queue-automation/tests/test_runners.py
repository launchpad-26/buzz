#!/usr/bin/env python3
"""Unit tests for runners.py — reviewer runner adapters.

Asserts that every supported transport builds a demonstrably read-only,
non-interactive invocation, that the selector and effort land in the command,
that effort is only ever reported enforced when the CLI can actually apply it,
and that an unknown runner is a configuration error rather than a silent
fallthrough. No subprocess is executed here.
"""

from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scripts"))

from runners import (  # noqa: E402
    ADAPTERS,
    EffortUnsupportedError,
    UnknownRunnerError,
    adapter_for,
    build_invocation,
    supported_runners,
)

REPO = "/tmp/repo"
PROMPT = "review this"


def _entry(runner: str, selector: str = "m1") -> dict:
    return {"runner": runner, "selector": selector, "provider_family": "f", "capability": "frontier"}


# -- registry ------------------------------------------------------------
def test_supported_runners_are_the_three_transports() -> None:
    assert supported_runners() == ["claude", "codex", "omp"]


def test_unknown_runner_raises_not_falls_through() -> None:
    for bad in ("", None, "gpt", "openrouter"):
        try:
            adapter_for(bad)
        except UnknownRunnerError as exc:
            assert "unknown runner" in str(exc)
            continue
        raise AssertionError(f"unknown runner must raise: {bad!r}")


def test_missing_selector_is_a_configuration_error() -> None:
    try:
        build_invocation({"runner": "omp", "selector": "  "}, PROMPT, "high", REPO)
    except UnknownRunnerError as exc:
        assert "selector" in str(exc)
    else:
        raise AssertionError("an entry without a selector must be rejected")


# -- read-only enforcement ----------------------------------------------
def test_every_adapter_declares_read_only_proof() -> None:
    for name, adapter in ADAPTERS.items():
        assert adapter.read_only_proof, f"{name} must declare how it enforces read-only"


def test_omp_invocation_is_read_only_and_ephemeral() -> None:
    inv = build_invocation(_entry("omp", "openrouter/z-ai/glm-5.3-flash"), PROMPT, "high", REPO)
    cmd = list(inv.cmd)
    assert cmd[0] == "omp"
    assert "--no-tools" in cmd          # disables all built-in tools
    assert "--no-session" in cmd        # nothing persisted
    assert "-p" in cmd                  # non-interactive
    assert f"--cwd={REPO}" in cmd       # explicit target, not inherited cwd
    assert "openrouter/z-ai/glm-5.3-flash" in cmd
    assert cmd[-1] == PROMPT
    # effort is passed through the thinking flag
    assert cmd[cmd.index("--thinking") + 1] == "high"


def test_claude_invocation_uses_plan_mode_and_denies_write_tools() -> None:
    inv = build_invocation(_entry("claude", "opus"), PROMPT, "high", REPO)
    cmd = list(inv.cmd)
    assert cmd[0] == "claude"
    assert "-p" in cmd
    assert cmd[cmd.index("--permission-mode") + 1] == "plan"
    # read-only must not rest on plan mode alone
    for tool in ("Edit", "Write", "NotebookEdit"):
        assert tool in cmd
    assert cmd[cmd.index("--add-dir") + 1] == REPO
    assert cmd[cmd.index("--model") + 1] == "opus"
    assert cmd[-1] == PROMPT


def test_codex_invocation_uses_read_only_sandbox() -> None:
    inv = build_invocation(_entry("codex", "gpt-5.6-sol"), PROMPT, "high", REPO)
    cmd = list(inv.cmd)
    assert cmd[:2] == ["codex", "exec"]
    assert cmd[cmd.index("--sandbox") + 1] == "read-only"
    assert cmd[cmd.index("-C") + 1] == REPO
    assert cmd[cmd.index("-m") + 1] == "gpt-5.6-sol"
    assert 'model_reasoning_effort="high"' in cmd
    assert cmd[-1] == PROMPT


def test_no_adapter_enables_a_bypass_flag() -> None:
    """No transport may be invoked with an approval/sandbox bypass."""
    forbidden = (
        "--auto-approve",
        "--dangerously-bypass-approvals-and-sandbox",
        "bypassPermissions",
        "danger-full-access",
        "workspace-write",
        "--approve-for-me",
    )
    for runner in supported_runners():
        cmd = " ".join(build_invocation(_entry(runner), PROMPT, "high", REPO).cmd)
        for flag in forbidden:
            assert flag not in cmd, f"{runner} must never pass {flag}"


# -- effort honesty ------------------------------------------------------
def test_omp_and_codex_enforce_effort() -> None:
    for runner in ("omp", "codex"):
        inv = build_invocation(_entry(runner), PROMPT, "xhigh", REPO)
        assert inv.effort_enforced is True, f"{runner} can enforce effort"


def test_claude_never_claims_enforced_effort() -> None:
    """Claude exposes no reasoning-effort flag, so the route must not claim one."""
    for effort in ("low", "medium", "high", "xhigh"):
        inv = build_invocation(_entry("claude"), PROMPT, effort, REPO)
        assert inv.effort_enforced is False
        assert inv.effort == effort  # still recorded as requested


def test_require_effort_enforced_refuses_unenforceable_transport() -> None:
    try:
        build_invocation(_entry("claude"), PROMPT, "xhigh", REPO, require_effort_enforced=True)
    except EffortUnsupportedError as exc:
        assert "cannot enforce effort" in str(exc)
    else:
        raise AssertionError("a route requiring enforced effort must refuse this transport")


def test_require_effort_enforced_allows_capable_transport() -> None:
    inv = build_invocation(_entry("omp"), PROMPT, "high", REPO, require_effort_enforced=True)
    assert inv.effort_enforced is True


# -- provenance ----------------------------------------------------------
def test_invocation_meta_is_auditable() -> None:
    inv = build_invocation(_entry("omp", "anthropic/claude-opus-5"), PROMPT, "medium", REPO)
    meta = inv.as_meta()
    assert meta["runner"] == "omp"
    assert meta["selector"] == "anthropic/claude-opus-5"
    assert meta["effort"] == "medium"
    assert meta["effort_enforced"] is True
    assert "--no-tools" in meta["read_only_proof"]
    # meta must not carry the prompt (it can contain enveloped evidence)
    assert PROMPT not in str(meta)


def test_prompt_is_always_the_final_argument() -> None:
    """Keeps the evidence payload out of flag position for every transport."""
    for runner in supported_runners():
        inv = build_invocation(_entry(runner), PROMPT, "medium", REPO)
        assert inv.cmd[-1] == PROMPT
