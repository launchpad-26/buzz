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

Does not wire into project-pack.py (STEP 5) -- this is the goose-config half
only.

Usage:
    python3 launchpad/agents/goose_config.py --enable-developer
"""

from __future__ import annotations

import argparse
import os
import sys
import tempfile
from pathlib import Path

import yaml


def goose_config_path(env: dict | None = None) -> Path:
    """Mirrors goose.rs's `goose_config_path()`: a set, non-empty
    GOOSE_PATH_ROOT wins, else `~/.config/goose/config.yaml`."""
    env = env if env is not None else os.environ
    root = env.get("GOOSE_PATH_ROOT")
    if root:
        return Path(root) / "config" / "config.yaml"
    return Path.home() / ".config" / "goose" / "config.yaml"


def read_config(path: Path) -> dict:
    """The parsed mapping at `path`, or an empty mapping if the file does
    not exist or is empty."""
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        loaded = yaml.safe_load(f)
    return loaded or {}


def merge_developer_extension(config: dict) -> dict:
    """Returns a NEW mapping with `extensions.developer` enabled. Every
    other top-level key, and every other extension, is preserved untouched.
    Idempotent: merging an already-merged mapping returns an equal
    mapping -- `developer`'s existing position in `extensions` is kept
    rather than moved to the end, so a second write matches the first
    byte-for-byte."""
    merged = dict(config)
    extensions = dict(merged.get("extensions") or {})
    extensions["developer"] = {"type": "builtin", "enabled": True}
    merged["extensions"] = extensions
    return merged


def write_config_atomic(path: Path, config: dict) -> None:
    """Writes `config` to `path` via a temp file in the same directory,
    then an atomic rename over the original -- a crash mid-write leaves
    either the old file or the new one, never a half-written one."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(
        dir=str(path.parent), prefix=f".{path.name}.", suffix=".tmp"
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            yaml.safe_dump(config, f, default_flow_style=False, sort_keys=False)
        os.replace(tmp_name, path)
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

    target = enable_developer_extension(path=args.path)
    print(f"enabled developer extension in {target}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
