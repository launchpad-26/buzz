#!/usr/bin/env python3
"""First-run onboarding / safe update for review-queue-automation.

Local-only: never calls GitHub, never invokes models, never claims a lease, never
approves a canary, never mutates a PR.

- Never silently overwrites an existing config: `init` refuses if one exists;
  a safe `update` path backs up atomically before writing, then verifies and
  restores the previous config on validation failure.
- Rejects empty repository slug, empty login, and unusable model pools before
  reporting runtime-ready.
- Creates the configured `pr review logs` directory and git-ignores repo-local
  config + logs, verifying both remain untracked.
- Prints real, existing next commands.
"""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import sys
from typing import Any

from config import (
    DEFAULT_LOG_DIR_NAME,
    RQA_CONFIG_DIR,
    check_writable,
    ensure_ignored,
    is_git_repo,
    is_ignored,
    is_tracked,
    load_repo_config,
    onboarding_defaults,
    repo_config_path,
    validate_config,
)


def _atomic_write(target: pathlib.Path, content: str) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = target.with_suffix(".tmp")
    tmp.write_text(content, encoding="utf-8")
    tmp.replace(target)


def _backup(config_path: pathlib.Path) -> pathlib.Path | None:
    if not config_path.is_file():
        return None
    backup = config_path.with_suffix(".bak.json")
    backup.write_text(config_path.read_text(encoding="utf-8"), encoding="utf-8")
    return backup


def _restore(backup: pathlib.Path | None, config_path: pathlib.Path) -> None:
    """Atomically put the backed-up config back; best-effort if none existed."""
    if backup is None or not backup.is_file():
        return
    _atomic_write(config_path, backup.read_text(encoding="utf-8"))
    try:
        backup.unlink()
    except OSError:
        pass


def _usable_login() -> str:
    for var in ("GITHUB_LOGIN", "RQA_LOGIN"):
        value = os.environ.get(var, "").strip()
        if value:
            return value
    # Local derivation only — no GitHub API.
    return ""


def _check_runtime_ready(config: dict[str, Any]) -> tuple[bool, list[str]]:
    problems: list[str] = []
    if not (config.get("login") or "").strip():
        problems.append("login is empty; a nonempty login is required before runtime-ready")
    slug = (config.get("repository", {}) or {}).get("slug", "")
    if not slug:
        problems.append("repository.slug is empty; a usable slug is required")
    primary = config.get("models", {}).get("primary") or []
    secondary = config.get("models", {}).get("secondary") or []
    if not primary and not secondary:
        problems.append("no usable model pools configured; at least one candidate is required")
    return not problems, problems


def init_onboard(
    repo_root, *, slug: str, base: str, preflight: str | None, login: str
) -> tuple[str | None, dict[str, Any]]:
    """Create a repo-local config. Refuses to overwrite any existing config."""
    root = pathlib.Path(repo_root).resolve()
    if not root.is_dir():
        return f"not a directory: {root}", {}
    if not is_git_repo(root):
        return f"not a git work tree: {root}", {}
    cfg_path = repo_config_path(root)
    if cfg_path.is_file():
        return "config already exists; refusing to overwrite (use `update`)", {}

    if not slug:
        return "a nonempty --slug OWNER/REPO is required", {}

    config = onboarding_defaults(root)
    config["repository"]["slug"] = slug
    config["repository"]["base"] = base or config["repository"]["base"]
    config["repository"]["root"] = str(root)
    config["repository"]["preflight"] = preflight or ""
    config["login"] = login or _usable_login()
    log_dir = pathlib.Path(config["logging"]["directory"])

    ensure_ignored(root, RQA_CONFIG_DIR + "/")
    ensure_ignored(root, DEFAULT_LOG_DIR_NAME)
    if not check_writable(log_dir):
        return f"cannot create logging directory: {log_dir}", {}
    log_dir.mkdir(parents=True, exist_ok=True)

    _atomic_write(cfg_path, json.dumps(config, indent=2) + "\n")

    issues = validate_config(config, root)
    ready, readiness = _check_runtime_ready(config)
    if issues:
        return "onboarding produced an invalid config: " + "; ".join(issues), {}

    summary = {
        "root": str(root),
        "config_path": str(cfg_path),
        "log_dir": config["logging"]["directory"],
        "ignored_config_dir": is_ignored(root, RQA_CONFIG_DIR + "/"),
        "ignored_log_dir": is_ignored(root, DEFAULT_LOG_DIR_NAME),
        "config_tracked": is_tracked(root, RQA_CONFIG_DIR),
        "runtime_ready": ready,
        "readiness_issues": readiness,
    }
    return None, summary


def update_config(
    repo_root, *, slug: str, base: str, preflight: str | None, login: str
) -> tuple[str | None, dict[str, Any]]:
    """Safely update an existing config with an atomic backup. Refuses if none exists."""
    root = pathlib.Path(repo_root).resolve()
    cfg_path = repo_config_path(root)
    if not cfg_path.is_file():
        return "no config to update; run `init` first", {}

    backup = _backup(cfg_path)

    # Start from existing (preserve prior values), apply provided overrides.
    try:
        config = json.loads(cfg_path.read_text(encoding="utf-8"))
    except Exception:
        config = onboarding_defaults(root)
    if not slug:
        _restore(backup, cfg_path)
        return "a nonempty --slug OWNER/REPO is required", {}
    repo = config.setdefault("repository", {})
    # Root must always equal the target repository being updated.
    if repo.get("root") and str(pathlib.Path(repo["root"]).resolve()) != str(root):
        _restore(backup, cfg_path)
        return f"config repository.root {repo['root']} does not match target repo {root}", {}
    repo["slug"] = slug
    repo["root"] = str(root)
    if base:
        repo["base"] = base
    if preflight is not None:
        repo["preflight"] = preflight
    if login:
        config["login"] = login

    log_dir = pathlib.Path(config.get("logging", {}).get("directory") or (root / DEFAULT_LOG_DIR_NAME))
    ensure_ignored(root, RQA_CONFIG_DIR + "/")
    ensure_ignored(root, DEFAULT_LOG_DIR_NAME)
    if not check_writable(log_dir):
        _restore(backup, cfg_path)
        return f"cannot use logging directory: {log_dir}", {}
    log_dir.mkdir(parents=True, exist_ok=True)

    _atomic_write(cfg_path, json.dumps(config, indent=2) + "\n")

    issues = validate_config(config, root)
    if issues:
        # Roll back the atomic write: never leave a half-valid config live.
        _restore(backup, cfg_path)
        return "update produced an invalid config; previous config restored: " + "; ".join(issues), {}
    ready, readiness = _check_runtime_ready(config)
    return None, {
        "updated": True,
        "backup": str(backup) if backup else None,
        "config_path": str(cfg_path),
        "runtime_ready": ready,
        "readiness_issues": readiness,
        "issues": issues,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Review-queue-automation onboarding")
    sub = parser.add_subparsers(dest="command", required=True)
    init = sub.add_parser("init")
    init.add_argument("repo_root")
    init.add_argument("--slug", default="")
    init.add_argument("--base", default="launchpad")
    init.add_argument("--preflight", default="")
    init.add_argument("--login", default="")
    upd = sub.add_parser("update")
    upd.add_argument("repo_root")
    upd.add_argument("--slug", default="")
    upd.add_argument("--base", default="")
    upd.add_argument("--preflight", default="")
    upd.add_argument("--login", default="")
    check = sub.add_parser("check")
    check.add_argument("repo_root")
    args = parser.parse_args(argv)

    if args.command == "check":
        loaded, path, issues = load_repo_config(args.repo_root)
        if loaded is not None and not issues:
            print(json.dumps({"valid": True, "config": str(path)}, indent=2))
            return 0
        print(json.dumps({"valid": False, "config": str(path), "issues": issues}, indent=2))
        return 1

    if args.command == "init":
        err, summary = init_onboard(args.repo_root, slug=args.slug, base=args.base, preflight=args.preflight or None, login=args.login)
    else:
        err, summary = update_config(args.repo_root, slug=args.slug, base=args.base, preflight=args.preflight or None, login=args.login)
    if err:
        print(json.dumps({"ok": False, "error": err}, indent=2))
        return 1
    print(json.dumps({"ok": True, **summary}, indent=2))
    # Print only real, existing next commands.
    dispatcher = str(pathlib.Path(__file__).resolve().parent / "dispatcher.py")
    exists = pathlib.Path(dispatcher).is_file()
    print("Next safe command: " + (f"python3 {dispatcher} --repo-root {args.repo_root} sweep" if exists else "review-queue-automation onboarding check"))
    return 0


if __name__ == "__main__":
    sys.exit(main())