#!/usr/bin/env python3
"""Read-merge-write goose's config.yaml to enable the `developer` extension.

STEP 4 of issue #239 (the Route 3 projector): goose's write/shell capability
is a config-FILE toggle, not an env var --
`desktop/src-tauri/src/managed_agents/config_bridge/goose.rs` only ever
*reads* `extensions.developer` out of this file, and nothing in this
repository writes it. This module builds read-merge-write from scratch: read
the existing file if present (empty mapping otherwise), preserve every
existing key untouched, set `extensions.developer = {type: builtin, enabled:
true}`, and write atomically (temp file + rename in the same directory) so a
crash mid-write cannot leave a half-written config an operator's next
`goose` invocation trips over. Running it twice against the same file is a
no-op, not an append-again.

Uses ruamel.yaml's round-trip mode (not PyYAML) specifically so an operator's
comments and quoting style survive a merge -- a plain load+dump strips both
on every write, confirmed to lose a hand-written "# managed by ansible"
comment and turn a quoted host string unquoted. Requires the
`python3-ruamel.yaml` apt package (or `pip install ruamel.yaml`) --
PERSONA_PACK_SPEC.md's tooling notes should mention this once STEP 5 wires
this module into the projector CLI.

Known limitation: no file locking across the read-modify-write window, so a
goose process rewriting its own config.yaml at the same moment this script
runs could lose one side's update. Each individual write stays atomic
(temp file + rename), so this is a lost-update race, not corruption -- the
plan's own atomicity requirement is about surviving a crash mid-write, not
about concurrent writers, and this module does not attempt the latter.

Does not wire into project-pack.py (STEP 5) -- this is the goose-config half
only.

Usage:
    python3 launchpad/agents/goose_config.py --enable-developer
"""

from __future__ import annotations

import argparse
import os
import stat
import sys
import tempfile
from pathlib import Path

from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap


class GooseConfigError(RuntimeError):
    """goose's config.yaml could not be read or merged -- always fails
    loudly, never silently discards or guesses at data the caller would
    act on."""


def _yaml() -> YAML:
    y = YAML()
    y.preserve_quotes = True
    return y


def goose_config_path(env: dict | None = None) -> Path:
    """Mirrors goose.rs's `goose_config_path()` exactly, including its
    edge case: `std::env::var("GOOSE_PATH_ROOT")` returns `Ok("")` for a
    set-but-empty variable, so Rust does NOT treat empty as unset -- an
    explicitly set (even empty) GOOSE_PATH_ROOT wins here too, rather than
    silently falling back to a different path than the one goose itself
    would resolve."""
    env = env if env is not None else os.environ
    if "GOOSE_PATH_ROOT" in env:
        return Path(env["GOOSE_PATH_ROOT"]) / "config" / "config.yaml"
    return Path.home() / ".config" / "goose" / "config.yaml"


def read_config(path: Path) -> CommentedMap:
    """The parsed mapping at `path`, or an empty mapping if the file does
    not exist or is empty. Raises GooseConfigError on invalid YAML or a
    non-mapping top-level value, rather than crashing with a raw
    exception or silently discarding the file's contents."""
    if not path.exists():
        return CommentedMap()
    try:
        with path.open("r", encoding="utf-8") as f:
            loaded = _yaml().load(f)
    except Exception as exc:
        raise GooseConfigError(f"{path} is not valid YAML: {exc}") from exc
    if loaded is None:
        return CommentedMap()
    if not isinstance(loaded, dict):
        raise GooseConfigError(
            f"{path}'s top-level YAML value is a {type(loaded).__name__}, "
            "not a mapping -- refusing to merge into it"
        )
    return loaded


def merge_developer_extension(config: dict) -> dict:
    """Returns a NEW mapping with `extensions.developer` enabled. Every
    other top-level key, and every other extension, is preserved untouched
    (comments and quoting included, when `config` came from `read_config`).
    Idempotent: merging an already-merged mapping returns an equal
    mapping -- `developer`'s existing position in `extensions` is kept
    rather than moved to the end, so a second write matches the first
    byte-for-byte.

    Raises GooseConfigError if an existing `extensions` key is present but
    is not itself a mapping."""
    merged = config.copy() if isinstance(config, CommentedMap) else CommentedMap(config)
    raw_extensions = merged.get("extensions")
    if raw_extensions is None:
        extensions = CommentedMap()
    elif isinstance(raw_extensions, dict):
        extensions = (
            raw_extensions.copy()
            if isinstance(raw_extensions, CommentedMap)
            else CommentedMap(raw_extensions)
        )
    else:
        raise GooseConfigError(
            f"'extensions' is a {type(raw_extensions).__name__}, not a "
            "mapping -- refusing to merge into it"
        )
    extensions["developer"] = {"type": "builtin", "enabled": True}
    merged["extensions"] = extensions
    return merged


def write_config_atomic(path: Path, config: dict) -> None:
    """Writes `config` to `path` via a temp file in the same directory,
    then an atomic rename over the original -- a crash mid-write leaves
    either the old file or the new one, never a half-written one.

    If `path` is a symlink, writes through it (onto the resolved real
    target) rather than replacing the symlink itself -- otherwise a
    dotfile-managed config (Stow, chezmoi, a manual symlink into a synced
    repo) silently loses its symlink on the first run.

    If `path` already exists, the new file keeps its permission mode
    (`tempfile.mkstemp` otherwise always creates at 0600, which would
    silently narrow an existing 0644 file's permissions on every write)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    real_path = path.resolve() if path.is_symlink() else path
    real_path.parent.mkdir(parents=True, exist_ok=True)

    existing_mode = real_path.stat().st_mode if real_path.exists() else None

    fd, tmp_name = tempfile.mkstemp(
        dir=str(real_path.parent), prefix=f".{real_path.name}.", suffix=".tmp"
    )
    try:
        if existing_mode is not None:
            os.chmod(fd, stat.S_IMODE(existing_mode))
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            _yaml().dump(config, f)
        os.replace(tmp_name, real_path)
    except Exception:
        try:
            os.unlink(tmp_name)
        except OSError:
            pass
        raise


def enable_developer_extension(
    path: Path | None = None, env: dict | None = None
) -> Path:
    """Read-merge-write entry point: enables goose's `developer` extension
    at `path` (default: `goose_config_path(env)`). Returns the path
    written."""
    target = path if path is not None else goose_config_path(env)
    current = read_config(target)
    merged = merge_developer_extension(current)
    write_config_atomic(target, merged)
    return target


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--enable-developer",
        action="store_true",
        help="enable goose's developer (shell/write) extension in config.yaml",
    )
    parser.add_argument(
        "--path",
        type=Path,
        default=None,
        help=(
            "override goose's config.yaml path (default: GOOSE_PATH_ROOT or "
            "~/.config/goose/config.yaml)"
        ),
    )
    args = parser.parse_args(argv)

    if not args.enable_developer:
        parser.error("nothing to do -- pass --enable-developer")

    try:
        target = enable_developer_extension(path=args.path)
    except GooseConfigError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(f"enabled developer extension in {target}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
