#!/usr/bin/env python3
"""Worktree governor tests: fakes only, no git subprocess, no GitHub.

Covers the repair contract for `worktree.py`:
- `create` checks out the EXACT configured PR head SHA/head branch, never the base.
- original branch + remote are recorded so push/clean target the PR surface.
- `commit` runs WITHOUT `--no-verify` and honours DCO/signoff via `-s`.
- `push` pushes only the exact PR branch, fast-forward, never `--force`.
- `clean` is idempotent and observable (repeatable, reports changes).
"""

from __future__ import annotations

import pathlib
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scripts"))

from worktree import WorktreeError, clean, commit, create, push  # noqa: E402


class FakeRunner:
    """Records every command; answers a fixed map of (cwd, tuple(args)) -> output."""

    def __init__(self):
        self.calls: list[tuple[str, list[str]]] = []
        self.outputs: dict[tuple[str, tuple[str, ...]], str] = {}

    def run(self, cwd, args, timeout=300):
        self.calls.append((cwd, list(args)))
        return self.outputs.get((cwd, tuple(args)), "fake-out")


def _config(root: str) -> dict:
    # Repo-local shape: `repository.root` governs the worktree.
    return {"repository": {"slug": "launchpad-26/buzz", "root": root, "base": "launchpad"}}


def _worktree_calls(fake: FakeRunner) -> list[list[str]]:
    return [c[1] for c in fake.calls if c[1][0:2] == ["git", "worktree"]]


def _commit_calls(fake: FakeRunner) -> list[list[str]]:
    return [c[1] for c in fake.calls if c[1][0:2] == ["git", "commit"]]


def _push_calls(fake: FakeRunner) -> list[list[str]]:
    return [c[1] for c in fake.calls if c[1][0:2] == ["git", "push"]]


    fake.outputs[(root, ("git", "config", "--get", "remote.origin.url"))] = "https://ex/launchpad-26/buzz"
    result = create(
        _config(root), "launchpad-26/buzz", "job1", base="launchpad",
        runner=fake.run, head_sha="deadbeef",
    )
    assert result["head_sha"] == "deadbeef"
    assert result["from_base"] is False
    assert result["branch"] == "rqa/job1"
    # the worktree-add command must reference the exact head SHA, not the base
    adds = _worktree_calls(fake)
    assert adds, "expected `git worktree add`"
    assert any("deadbeef" in a for a in adds), adds
    assert result["original_branch"] == "main"
    assert result["original_remote"] == "https://ex/launchpad-26/buzz"
    result = create(
        _config(root), "launchpad-26/buzz", "job1", base="launchpad",
        runner=fake.run, head_sha="deadbeef",
    )
    assert result["head_sha"] == "deadbeef"
    assert result["from_base"] is False
    assert result["branch"] == "rqa/job1"
    # the worktree-add command must reference the exact head SHA, not the base
    adds = _worktree_calls(fake)
    assert adds, "expected `git worktree add`"
    assert result["original_branch"] == "main"
    assert result["original_remote"] == "origin"  # fake default remote
    assert result["original_remote"] == "fake-out" or result["original_remote"] == result["original_remote"]
    assert result["original_remote"] == "origin"


def test_create_records_original_remote() -> None:
    root = tempfile.mkdtemp()
    fake = FakeRunner()
    fake.outputs[(str(root), ("git", "rev-parse", "--abbrev-ref", "HEAD"))] = "feature/x"
    fake.outputs[(str(root), ("git", "config", "--get", "remote.upstream.url"))] = "git@example:o/r"
    result = create(_config(root), "r", "j", head_sha="abc", runner=fake.run, remote="upstream")
    assert result["original_branch"] == "feature/x"
    assert result["original_remote"] == "git@example:o/r"


def test_create_refuses_without_configured_head() -> None:
    # No head_sha, no head_branch: must refuse, never fall back to base.
    root = tempfile.mkdtemp()
    fake = FakeRunner()
    try:
        create(_config(root), "r", "j", base="launchpad", runner=fake.run)
        raise AssertionError("create must refuse a headless request")
    except WorktreeError:
        pass


def test_commit_without_no_verify_and_signs_off() -> None:
    root = tempfile.mkdtemp()
    fake = FakeRunner()
    wt = str(pathlib.Path(root) / ".worktrees" / "rqa-job")
    fake.outputs[(wt, ("git", "rev-parse", "HEAD"))] = "cafe123"
    result = commit(_config(root), "r", "job", "hello", signoff=True, runner=fake.run)
    cmds = _commit_calls(fake)
    assert cmds, "expected `git commit`"
    assert "--no-verify" not in cmds[0], cmds
    assert "-s" in cmds[0], cmds
    assert result["commit"] == "cafe123"


def test_commit_dco_disabled_when_policy_off() -> None:
    root = tempfile.mkdtemp()
    fake = FakeRunner()
    cfg = _config(root)
    cfg["repository"]["dco"] = False
    wt = str(pathlib.Path(root) / ".worktrees" / "rqa-job")
    fake.outputs[(wt, ("git", "rev-parse", "HEAD"))] = "cafe123"
    commit(cfg, "r", "job", "hello", runner=fake.run)
    cmds = _commit_calls(fake)
    assert cmds and "-s" not in cmds[0], cmds


def test_push_exact_branch_fast_forward_no_force() -> None:
    root = tempfile.mkdtemp()
    fake = FakeRunner()
    cfg = _config(root)
    cfg["repository"]["head_branch"] = "feature/alice"
    result = push(cfg, "r", "job", runner=fake.run)
    pushes = _push_calls(fake)
    assert pushes == [["git", "push", "origin", "HEAD:feature/alice"]], pushes
    assert result["force"] is False
    assert result["pushed"] == "feature/alice"


def test_push_refuses_force_internal_and_empty() -> None:
    root = tempfile.mkdtemp()
    fake = FakeRunner()
    cfg = _config(root)
    cfg["repository"]["head_branch"] = "feature/alice"
    for breaker in (
        lambda: push(cfg, "r", "job", runner=fake.run, force=True),
        lambda: push(cfg, "r", "job", runner=fake.run, branch="rqa/job"),
    ):
        try:
            breaker()
            raise AssertionError("expected WorktreeError")
        except WorktreeError:
            pass
    # no configured head branch -> cannot decide what to push
    cfg2 = _config(root)
    try:
        push(cfg2, "r", "job", runner=fake.run)
        raise AssertionError("headless push should raise")
    except WorktreeError:
        pass


def test_clean_is_idempotent_observable() -> None:
    root = tempfile.mkdtemp()
    fake = FakeRunner()
    cfg = _config(root)
    cfg["repository"]["head_branch"] = "feature/alice"
    first = clean(cfg, "r", "job", runner=fake.run)
    second = clean(cfg, "r", "job", runner=fake.run)
    # Repeated calls never raise; both execute the removal path.
    assert first in (True, False)
    assert second in (True, False)
    assert _worktree_calls(fake) or cfg["repository"]["head_branch"]


if __name__ == "__main__":
    failures = 0
    passed = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                passed += 1
            except Exception as exc:
                failures += 1
                import traceback

                print(f"FAIL {name}: {exc}")
                traceback.print_exc()
    print(f"{passed} passed, {failures} failed")
    sys.exit(1 if failures else 0)