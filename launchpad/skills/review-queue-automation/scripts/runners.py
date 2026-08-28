"""Reviewer runner adapters for review-queue-automation.

One adapter per supported CLI transport. Each adapter builds a demonstrably
read-only, non-interactive, session-free invocation for a single reviewer slot.

Supported runners and the flag that enforces read-only:

    omp     --no-tools               disables every built-in tool
    claude  --permission-mode plan   plan mode cannot apply edits
    codex   --sandbox read-only      model-run shell commands cannot write

Design rules:
- Read-only is enforced by a flag, not by prompt instruction. Each adapter records
  the exact flags it relies on in `read_only_proof` so an audit can verify the
  claim against the recorded attempt artifact.
- Effort honesty: only some CLIs can enforce a reasoning-effort level. An adapter
  reports `effort_enforced=False` rather than letting a route claim an assurance
  axis its transport cannot actually apply. Callers must record that, so a route
  never inherits credit for effort it did not enforce.
- An unknown runner is a configuration error for the operator, never a candidate
  failure that silently falls through to the next model.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

#: Reasoning-effort levels used by the assurance profiles.
PROFILE_EFFORTS = ("low", "medium", "high", "xhigh")


class UnknownRunnerError(ValueError):
    """Raised when a configured entry names a runner with no adapter."""


class EffortUnsupportedError(ValueError):
    """Raised when a runner cannot enforce the requested effort level."""


@dataclass(frozen=True)
class Invocation:
    """A built reviewer command plus the provenance needed to audit it."""

    cmd: tuple[str, ...]
    runner: str
    selector: str
    effort: str
    effort_enforced: bool
    read_only_proof: tuple[str, ...]

    def as_meta(self) -> dict[str, Any]:
        return {
            "runner": self.runner,
            "selector": self.selector,
            "effort": self.effort,
            "effort_enforced": self.effort_enforced,
            "read_only_proof": list(self.read_only_proof),
        }


@dataclass(frozen=True)
class RunnerAdapter:
    name: str
    read_only_proof: tuple[str, ...]
    #: Efforts this transport can actually enforce. Empty == cannot enforce any.
    enforceable_efforts: tuple[str, ...]
    build: Callable[[dict[str, Any], str, str, str], tuple[str, ...]] = field(repr=False)


def _omp_cmd(entry: dict[str, Any], prompt: str, effort: str, repo_path: str) -> tuple[str, ...]:
    """Read-only omp invocation.

    `--no-tools` is the strictest supported profile (a tool allowlist would permit
    more surface, not less). The session is ephemeral and the target repository is
    passed explicitly rather than inherited from the caller's cwd.
    """
    return (
        "omp",
        "-p",
        "--no-session",
        f"--cwd={repo_path}",
        "--no-tools",
        "--model",
        entry["selector"],
        "--thinking",
        effort,
        prompt,
    )


def _claude_cmd(entry: dict[str, Any], prompt: str, effort: str, repo_path: str) -> tuple[str, ...]:
    """Read-only native Claude invocation.

    `--permission-mode plan` cannot apply edits. Write-capable tools are also
    denied explicitly so the read-only claim does not rest on plan mode alone.
    Claude exposes no reasoning-effort flag, so effort is never reported enforced.
    """
    return (
        "claude",
        "-p",
        "--permission-mode",
        "plan",
        "--disallowed-tools",
        "Edit",
        "Write",
        "NotebookEdit",
        "--add-dir",
        repo_path,
        "--model",
        entry["selector"],
        prompt,
    )


def _codex_cmd(entry: dict[str, Any], prompt: str, effort: str, repo_path: str) -> tuple[str, ...]:
    """Read-only native Codex invocation.

    `--sandbox read-only` prevents model-generated commands from writing.
    `--skip-git-repo-check` keeps the call usable from a worktree or bare path.
    """
    return (
        "codex",
        "exec",
        "--sandbox",
        "read-only",
        "--skip-git-repo-check",
        "-C",
        repo_path,
        "-m",
        entry["selector"],
        "-c",
        f'model_reasoning_effort="{effort}"',
        prompt,
    )


ADAPTERS: dict[str, RunnerAdapter] = {
    "omp": RunnerAdapter(
        name="omp",
        read_only_proof=("--no-tools", "--no-session"),
        enforceable_efforts=PROFILE_EFFORTS,
        build=_omp_cmd,
    ),
    "claude": RunnerAdapter(
        name="claude",
        read_only_proof=("--permission-mode plan", "--disallowed-tools Edit Write NotebookEdit"),
        enforceable_efforts=(),  # no reasoning-effort flag on this CLI
        build=_claude_cmd,
    ),
    "codex": RunnerAdapter(
        name="codex",
        read_only_proof=("--sandbox read-only",),
        enforceable_efforts=("low", "medium", "high", "xhigh"),
        build=_codex_cmd,
    ),
}


def supported_runners() -> list[str]:
    return sorted(ADAPTERS)


def adapter_for(runner: str | None) -> RunnerAdapter:
    """Return the adapter for `runner`, or raise UnknownRunnerError."""
    found = ADAPTERS.get((runner or "").strip())
    if found is None:
        raise UnknownRunnerError(
            f"unknown runner: {runner or '<unset>'} (supported: {', '.join(supported_runners())})"
        )
    return found


def build_invocation(
    entry: dict[str, Any],
    prompt: str,
    effort: str,
    repo_path: str,
    *,
    require_effort_enforced: bool = False,
) -> Invocation:
    """Build the read-only reviewer invocation for one candidate entry.

    `require_effort_enforced=True` refuses a transport that cannot apply the
    requested effort, instead of quietly running at an unknown effort and letting
    the route claim the assurance axis anyway.
    """
    adapter = adapter_for(entry.get("runner"))
    selector = (entry.get("selector") or "").strip()
    if not selector:
        raise UnknownRunnerError(f"runner {adapter.name} entry is missing a selector")

    enforced = effort in adapter.enforceable_efforts
    if require_effort_enforced and not enforced:
        raise EffortUnsupportedError(
            f"runner {adapter.name} cannot enforce effort {effort!r} "
            f"(enforceable: {', '.join(adapter.enforceable_efforts) or 'none'})"
        )

    cmd = adapter.build(entry, prompt, effort, repo_path)
    return Invocation(
        cmd=tuple(cmd),
        runner=adapter.name,
        selector=selector,
        effort=effort,
        effort_enforced=enforced,
        read_only_proof=adapter.read_only_proof,
    )
