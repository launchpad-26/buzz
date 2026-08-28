"""Unified entry-point config resolution for review-queue-automation.

Every CLI runtime entry point should call `resolve` (or `resolve_or_onboarding`)
so they all consume the single authoritative repo-local config and fail toward
`onboarding_required` when it is missing/invalid.
"""

from __future__ import annotations

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
    """Return (config|None, path). On failure print onboarding_required and return None,None."""
    resolved = resolve(repo_root)
    if resolved is None:
        print(
            {
                "status": "onboarding_required",
                "reason": "repo-local config missing or invalid",
                "onboarding": f"python3 {project_root() / 'scripts' / 'onboarding.py'} init {repo_root}",
            },
            file=sys.stdout,
        )
        return None, None
    config, path, _issues = resolved
    return config, path


def make_state(config: dict[str, Any]) -> State:
    return State({"state_dir": config.get("state_dir", "~/.config/review-queue-automation")})