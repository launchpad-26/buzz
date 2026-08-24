#!/usr/bin/env python3
"""Project a resolved persona pack into buzz-acp + goose runtime env vars.

STEP 2 of issue #239 (the Route 3 projector): a GENERIC tool, not specific to
The Professor. It calls `buzz pack inspect --format json <pack-dir>` (added in
STEP 1) and emits a shell-sourceable env file mapping the persona's fully
resolved config onto the env vars buzz-acp and the agent runtime (goose) read
at spawn time -- PERSONA_PACK_SPEC.md Section 10 and buzz-acp's own CLI
env-var names (crates/buzz-acp/src/config.rs: BUZZ_ACP_AGENT_COMMAND,
BUZZ_ACP_AGENT_ARGS, BUZZ_ACP_MCP_COMMAND).

Operator env vars always win (mirrors buzz-acp's own `std::env::var(key)`
check before injecting persona env vars, PERSONA_PACK_SPEC.md's precedence
level 1): a var already set in the calling shell before this script runs is
left untouched -- no `export` line is emitted for it -- rather than being
silently overwritten by a sourced file.

Does NOT touch goose's config.yaml (STEP 4) or wire the two halves together
(STEP 5) -- this is the env-var half only.

Usage:
    python3 launchpad/agents/project-pack.py the-professor
    python3 launchpad/agents/project-pack.py the-professor --out /tmp/env.sh
    source <(python3 launchpad/agents/project-pack.py the-professor)
"""

from __future__ import annotations

import argparse
import json
import os
import shlex
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


class ProjectionError(RuntimeError):
    """A pack/persona could not be projected -- always fails loudly, never
    silently drops or guesses at a value the caller would act on."""


def find_buzz_binary(repo_root: Path, env: dict) -> Path:
    """Locate the `buzz` CLI binary. Checked in order: an explicit
    BUZZ_CLI_BIN override, PATH, then the two conventional cargo build output
    locations. Raises rather than falling back to a guess."""
    override = env.get("BUZZ_CLI_BIN")
    if override:
        path = Path(override)
        if path.is_file():
            return path
        raise ProjectionError(f"BUZZ_CLI_BIN={override!r} does not exist")

    on_path = shutil.which("buzz")
    if on_path:
        return Path(on_path)

    # Prefer whichever of release/debug was built most recently rather than
    # a fixed release-over-debug order: a stale release binary from an
    # earlier session silently shadowing a just-rebuilt debug one is exactly
    # the kind of bug this helper exists to avoid, not reproduce.
    candidates = [
        c
        for c in (
            repo_root / "target" / "release" / "buzz",
            repo_root / "target" / "debug" / "buzz",
        )
        if c.is_file()
    ]
    if candidates:
        return max(candidates, key=lambda c: c.stat().st_mtime)

    raise ProjectionError(
        "could not find the `buzz` CLI binary -- set BUZZ_CLI_BIN, put `buzz` "
        "on PATH, or run `cargo build -p buzz-cli` first"
    )


def inspect_pack(buzz_bin: Path, pack_dir: Path) -> dict:
    """Run `buzz pack inspect --format json <pack_dir>` and parse its output."""
    result = subprocess.run(
        [str(buzz_bin), "pack", "inspect", str(pack_dir), "--format", "json"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise ProjectionError(
            f"`buzz pack inspect --format json {pack_dir}` failed "
            f"(exit {result.returncode}): {result.stderr.strip()}"
        )
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as e:
        raise ProjectionError(
            f"`buzz pack inspect --format json {pack_dir}` did not emit valid "
            f"JSON: {e}"
        ) from e


def select_persona(pack: dict, persona_name: str) -> dict:
    """Find persona_name in the resolved pack, or fail loudly with the names
    that were actually available -- never silently pick "the first one"."""
    personas = pack.get("personas", [])
    for persona in personas:
        if persona.get("name") == persona_name:
            return persona
    available = ", ".join(p.get("name", "?") for p in personas) or "(none)"
    raise ProjectionError(
        f"no persona named {persona_name!r} in this pack. Available: {available}"
    )


def project_env_vars(persona: dict, pack_dir: Path) -> list[tuple[str, str]]:
    """Compute the full set of (key, value) pairs this persona projects to,
    before operator-precedence filtering. Reuses `runtime_env_vars` as
    resolved by buzz-persona's own resolve_pack() (model/provider split,
    temperature, context limit) rather than re-deriving it in Python --
    a second implementation of that precedence/split logic would drift from
    the Rust one the first time either changed."""
    pairs: list[tuple[str, str]] = [(k, v) for k, v in persona.get("runtime_env_vars", [])]

    # BUZZ_ACP_AGENT_COMMAND: which ACP-adapter binary buzz-acp spawns.
    # The persona's own `runtime` field already uses this vocabulary
    # ("goose", "claude", ...); buzz-acp's own default is "goose" when unset,
    # so an absent runtime projects the same value buzz-acp would already
    # assume -- explicit rather than implicit, per the plan's own "no other
    # human step" requirement.
    runtime = persona.get("runtime") or "goose"
    pairs.append(("BUZZ_ACP_AGENT_COMMAND", runtime))
    # "acp" is the fixed subcommand every known adapter binary exposes for
    # ACP mode; nothing in a persona pack varies it today.
    pairs.append(("BUZZ_ACP_AGENT_ARGS", "acp"))

    mcp_servers = persona.get("mcp_servers", [])
    if len(mcp_servers) > 1:
        names = ", ".join(s.get("name", "?") for s in mcp_servers)
        raise ProjectionError(
            f"persona {persona.get('name')!r} declares {len(mcp_servers)} MCP "
            f"servers ({names}), but buzz-acp's BUZZ_ACP_MCP_COMMAND accepts "
            "exactly one (Config.mcp_command is a single String, not a list "
            "-- see crates/buzz-acp/src/lib.rs build_mcp_servers()). Refusing "
            "to silently project only the first and drop the rest."
        )
    if len(mcp_servers) == 1:
        server = mcp_servers[0]
        if server.get("args"):
            raise ProjectionError(
                f"MCP server {server.get('name')!r} for persona "
                f"{persona.get('name')!r} declares args {server['args']!r}, but "
                "BUZZ_ACP_MCP_COMMAND is a bare command string -- buzz-acp's "
                "build_mcp_servers() always spawns it with an empty args list. "
                "Projecting only the command would silently drop the required "
                "arguments."
            )
        command = Path(server["command"])
        if not command.is_absolute():
            # buzz-persona does zero path resolution on `command` (it is kept
            # exactly as authored, pack-relative) and buzz-acp does none
            # either -- it execs Config.mcp_command literally. A relative
            # command therefore only resolves if the caller's cwd happens to
            # be the pack directory, which is not something to assume.
            command = (pack_dir / command).resolve()
        pairs.append(("BUZZ_ACP_MCP_COMMAND", str(command)))

    return pairs


def apply_operator_precedence(
    pairs: list[tuple[str, str]], environ: dict
) -> tuple[list[tuple[str, str]], list[tuple[str, str, str]]]:
    """Split pairs into (kept, skipped). A var already present in `environ`
    is skipped -- the operator's value wins and is left untouched -- with
    enough detail recorded to explain the skip in the emitted file."""
    kept: list[tuple[str, str]] = []
    skipped: list[tuple[str, str, str]] = []
    for key, value in pairs:
        if key in environ:
            skipped.append((key, value, environ[key]))
        else:
            kept.append((key, value))
    return kept, skipped


def render_env_file(
    kept: list[tuple[str, str]], skipped: list[tuple[str, str, str]]
) -> str:
    """Render the sourceable env file. Skipped vars get a comment, not an
    export -- the whole point is that sourcing this file must not clobber
    an operator's already-set value."""
    lines = [
        "# Generated by launchpad/agents/project-pack.py -- do not hand-edit.",
        "# Re-run the projector after changing the pack instead.",
    ]
    for key, value in kept:
        lines.append(f"export {key}={shlex.quote(value)}")
    for key, resolved_value, operator_value in skipped:
        lines.append(
            f"# skipped {key}: operator env already sets it to "
            f"{shlex.quote(operator_value)} (pack would have projected "
            f"{shlex.quote(resolved_value)})"
        )
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("persona", help="Persona name to project (also used as the "
                         "default pack directory name under launchpad/agents/)")
    parser.add_argument(
        "--pack-dir",
        type=Path,
        default=None,
        help="Pack directory (default: launchpad/agents/<persona>)",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Write the env file here instead of stdout",
    )
    args = parser.parse_args(argv)

    pack_dir = args.pack_dir or (REPO_ROOT / "launchpad" / "agents" / args.persona)
    pack_dir = pack_dir.resolve()

    try:
        buzz_bin = find_buzz_binary(REPO_ROOT, os.environ)
        pack = inspect_pack(buzz_bin, pack_dir)
        persona = select_persona(pack, args.persona)
        pairs = project_env_vars(persona, pack_dir)
        kept, skipped = apply_operator_precedence(pairs, os.environ)
        rendered = render_env_file(kept, skipped)
    except ProjectionError as e:
        print(f"project-pack: {e}", file=sys.stderr)
        return 1

    if args.out:
        args.out.write_text(rendered)
    else:
        sys.stdout.write(rendered)
    return 0


if __name__ == "__main__":
    sys.exit(main())
