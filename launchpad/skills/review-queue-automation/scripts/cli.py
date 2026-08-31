"""Unified entry-point config resolution for review-queue-automation.

Every CLI runtime entry point should call `resolve` (or `resolve_or_onboarding`)
so they all consume the single authoritative repo-local config and fail toward
`onboarding_required` when it is missing/invalid.
"""

from __future__ import annotations

import json
import os
import pathlib
import sys
from typing import Any

from common import State, normalize_config
from config import load_repo_config


def project_root() -> pathlib.Path:
    return pathlib.Path(__file__).resolve().parent.parent


def resolve(repo_root: str) -> tuple[dict[str, Any], pathlib.Path, list[str]] | None:
    """Load + validate repo-local config. Returns (config, path, issues) or None.

    When None, callers should exit with `onboarding_required` (no activity).
    """
    config, path, issues = load_repo_config(repo_root)
    if config is None or issues:
        return None
    return normalize_config(config), path, issues


def resolve_or_onboarding(
    repo_root: str,
) -> tuple[dict[str, Any] | None, pathlib.Path | None]:
    """Return `(config, path)`, or `(None, None)` after printing `onboarding_required`.

    NOTE FOR CALLERS: this ALWAYS returns a 2-tuple, so `if result is None` can
    never be true. Unpack first, then test the config:

        config, _ = resolve_or_onboarding(repo_root)
        if config is None:
            return 1
    """
    resolved = resolve(repo_root)
    if resolved is None:
        print(
            json.dumps(
                {
                    "status": "onboarding_required",
                    "reason": "repo-local config missing or invalid",
                    "onboarding": (
                        f"python3 {project_root() / 'scripts' / 'onboarding.py'} "
                        f"init {repo_root}"
                    ),
                },
                indent=2,
                sort_keys=True,
            ),
            file=sys.stdout,
        )
        return None, None
    config, path, _issues = resolved
    return config, path


def make_state(config: dict[str, Any]) -> State:
    return State({"state_dir": config.get("state_dir", "~/.config/review-queue-automation")})