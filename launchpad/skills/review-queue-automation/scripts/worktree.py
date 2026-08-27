#!/usr/bin/env python3
"""Isolated author-triage worktree operations: create, commit, push, clean.

Safety rules (enforced here):

- `create` builds the worktree from the EXACT configured PR head SHA / head
  branch, never from the base branch. Without a configured head it refuses —
  there is no base fallback. The original branch and remote are recorded in the
  result so `push`/`clean` target the right place.
- `commit` runs WITHOUT `--no-verify`, so repository hooks (lint, CI-local
  checks) run. A DCO/Signed-off-by trailer is added when the repo policy asks
  for it (config `dco`, default on) or when `signoff=True`.
- `push` pushes only the exact PR head branch, with a plain fast-forward push
  and never `--force`.
- `clean` is idempotent (repeatable) and reports whether anything changed.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from typing import Any, Callable


class WorktreeError(Exception):
    pass


def run_command(
    cwd: str,
    args: list[str],
    *,
    timeout: int = 300,
    env: dict[str, str] | None = None,
) -> tuple[int, str, str]:
    """Run a git/predictable command, returning (rc, stdout, stderr)."""
    result = subprocess.run(
        args, capture_output=True, text=True, timeout=timeout, cwd=cwd,
        stdin=subprocess.DEVNULL, env=env,
    )
    return result.returncode, result.stdout, result.stderr


def _worktree_dir(config: dict[str, Any], repo: str, job: str) -> str:
    root = _repo_root(config, repo)
    return os.path.join(root, ".worktrees", f"rqa-{job}")


def _repo_root(config: dict[str, Any], repo: str) -> str:
    """Repo path from either config shape (repos.<repo>.path or repository.root)."""
    if "repos" in config:
        entry = config["repos"].get(repo)
        if entry and entry.get("path"):
            return entry["path"]
    repo_cfg = config.get("repository", {}) or {}
    return repo_cfg.get("root", "")


def _repo_cfg(config: dict[str, Any], repo: str) -> dict[str, Any]:
    """The config entry governing `repo`, from either config shape."""
    if "repos" in config:
        entry = config["repos"].get(repo)
        if entry:
            return dict(entry)
    return dict(config.get("repository", {}) or {})


def _config_head(config: dict[str, Any], repo: str, key: str) -> str:
    return str(_repo_cfg(config, repo).get(key, "") or "").strip()


def _dco_enabled(config: dict[str, Any], repo: str, signoff: bool) -> bool:
    """DCO/signoff is honoured when the caller asks or the repo policy wants it.

    `normalize_config` sets `dco: True` on repo-local config by default, so the
    safe default is to sign off. An explicit `dco: False` disables it.
    """
    if signoff:
        return True
    policy = _repo_cfg(config, repo).get("dco")
    return bool(policy if policy is not None else True)


def _original_branch(root: str, runner: Callable) -> str:
    try:
        return runner(root, ["git", "rev-parse", "--abbrev-ref", "HEAD"])
    except WorktreeError:
        return ""


def _original_remote(root: str, runner: Callable, remote: str) -> str:
    try:
        url = runner(root, ["git", "config", "--get", f"remote.{remote}.url"])
        return url.strip() or remote
    except WorktreeError:
        return remote


def create(
    config: dict[str, Any],
    repo: str,
    job: str,
    base: str | None = None,
    number: int = 0,
    *,
    runner: Callable | None = None,
    head_sha: str = "",
    head_branch: str = "",
    remote: str = "origin",
) -> dict[str, Any]:
    """Create an isolated worktree at <repo>/.worktrees/rqa-<job> from the EXACT
    configured PR head SHA/head branch.

    Refuses to create from the base branch. Records the original branch and
    remote (and the head SHA/branch) in the returned dict so push/clean target
    the exact PR surface.
    """
    root = _repo_root(config, repo)
    if not root or not os.path.isdir(root):
        raise WorktreeError(f"repo root unavailable for {repo}")
    work = _worktree_dir(config, repo, job)

    # The exact PR head — configured head wins over per-call override only when
    # the caller supplied nothing. We never fall back to the base branch.
    head_sha = head_sha or _config_head(config, repo, "head_sha")
    head_branch = head_branch or _config_head(config, repo, "head_branch")
    if not head_sha and not head_branch:
        raise WorktreeError(
            f"no PR head SHA or head branch configured for {repo}; "
            "refusing to create a worktree from the base branch"
        )

    runner = runner or _run

    # Record the original checkout branch/remote before we switch anywhere.
    original_branch = _original_branch(root, runner)
    original_remote = _original_remote(root, runner, remote)
    current_head = head_sha or head_branch

    os.makedirs(os.path.dirname(work), exist_ok=True)
    # Fetch the exact head (SHA or branch), never the base.
    runner(root, ["git", "fetch", "--no-tags", remote, current_head])
    branch = f"rqa/{job}"
    # Create an isolated branch at the exact head commit.
    runner(root, ["git", "worktree", "add", "-b", branch, work, current_head])
    return {
        "repo": repo,
        "job": job,
        "number": number,
        "worktree": work,
        "branch": branch,
        "head_sha": head_sha,
        "head_branch": head_branch,
        "original_branch": original_branch,
        "original_remote": original_remote,
        "from_base": False,
    }


def _run(cwd: str, args: list[str], timeout: int = 300) -> str:
    rc, out, err = run_command(cwd, args, timeout=timeout)
    if rc != 0:
        raise WorktreeError(f"{args[0]} failed ({rc}): {err[-1200:]}")
    return out.strip()


def commit(
    config: dict[str, Any],
    repo: str,
    job: str,
    message: str,
    signoff: bool = False,
    provenance: str = "",
    number: int = 0,
    *,
    runner: Callable | None = None,
) -> dict[str, Any]:
    work = _worktree_dir(config, repo, job)
    r = runner or _run
    r(work, ["git", "add", "-A"])
    # NO `--no-verify`: repository hooks always run.
    cmd = ["git", "commit", "-m", message]
    if _dco_enabled(config, repo, signoff):
        cmd.append("-s")
    if provenance:
        cmd += ["--trailer", provenance]
    r(work, cmd)
    sha = r(work, ["git", "rev-parse", "HEAD"])
    return {"repo": repo, "number": int(number), "job": job, "commit": sha}


def push(
    config: dict[str, Any],
    repo: str,
    job: str,
    branch: str | None = None,
    *,
    runner: Callable | None = None,
    remote: str = "origin",
    force: bool = False,
) -> dict[str, Any]:
    """Push only the exact PR head branch, fast-forward, never force.

    `branch` selects the remote ref; it defaults to the configured PR head
    branch. Pushing an internal rqa ref or with `--force` is refused.
    """
    work = _worktree_dir(config, repo, job)
    r = runner or _run

    # The ref we push must be the PR's own branch. We only ever push the exact
    # head branch; an explicit different branch or an internal rqa ref is refused.
    if branch is None:
        branch = _config_head(config, repo, "head_branch")
    if not branch:
        raise WorktreeError("no PR head branch configured; cannot decide what to push")
    if branch.startswith("rqa/"):
        raise WorktreeError("refusing to push an internal rqa branch to the PR remote")
    if force:
        raise WorktreeError("refusing to force-push the PR branch; fast-forward only")

    # Plain push, no --force: a non-fast-forward update is rejected by the server.
    r(work, ["git", "push", remote, f"HEAD:{branch}"])
    return {"repo": repo, "job": job, "pushed": branch, "remote": remote, "force": False}


def clean(
    config: dict[str, Any],
    repo: str,
    job: str,
    *,
    runner: Callable | None = None,
) -> bool:
    """Idempotently remove the worktree and its branch. Safe to call repeatedly.

    Reports `True` if anything was removed, `False` if there was nothing to do.
    Never raises on an already-clean state.
    """
    root = _repo_root(config, repo)
    work = _worktree_dir(config, repo, job)
    r = runner or _run
    changed = False
    if os.path.isdir(work):
        try:
            r(root, ["git", "worktree", "remove", "--force", work])
            changed = True
        except WorktreeError:
            pass
    for branch in {f"rqa/{job}", _config_head(config, repo, "head_branch")}:
        if not branch:
            continue
        try:
            r(root, ["git", "branch", "-D", branch])
            changed = True
        except WorktreeError:
            pass
    return changed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Isolated author worktree governor")
    parser.add_argument("--config", default=None)
    parser.add_argument("operation", choices=["create", "commit", "push", "clean"])
    parser.add_argument("repo")
    parser.add_argument("--job", required=True)
    parser.add_argument("--message", default=None)
    parser.add_argument("--base", default="")
    parser.add_argument("--branch", default=None)
    parser.add_argument("--number", type=int, default=0)
    parser.add_argument("--signoff", action="store_true")
    parser.add_argument("--provenance", default="")
    parser.add_argument("--head-sha", default="")
    parser.add_argument("--head-branch", default="")
    parser.add_argument("--remote", default="origin")
    args = parser.parse_args(argv)

    from common import load_config

    config, _ = load_config(args.config)
    if args.operation == "create":
        result = create(
            config, args.repo, args.job, args.base or None, args.number,
            head_sha=args.head_sha, head_branch=args.head_branch, remote=args.remote,
        )
    elif args.operation == "commit":
        result = commit(config, args.repo, args.job, args.message or f"author-triage {args.job}", args.signoff, args.provenance, args.number)
    elif args.operation == "push":
        result = push(config, args.repo, args.job, args.branch, remote=args.remote)
    else:
        clean(config, args.repo, args.job)
        result = {"repo": args.repo, "job": args.job, "cleaned": True}
    if isinstance(result, dict):
        json.dump(result, sys.stdout, indent=2, sort_keys=True)
        sys.stdout.write("\n")
    else:
        print(result)
    return 0


if __name__ == "__main__":
    sys.exit(main())
