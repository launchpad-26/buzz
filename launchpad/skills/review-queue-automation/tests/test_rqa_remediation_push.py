#!/usr/bin/env python3
"""`rqa.remediation.push` and `rqa.remediation.worktree` — the two E-20 primitives, on
their own: `code/P-10-remediation.md` §3 steps 5, 6 and 13, and §4's `push_head`.

The end-to-end rows are in `test_rqa_remediation_remediate.py`; these are the unit-level
guards for the two functions an attacker-influenced value reaches first — a branch name and
a path inside the checkout.

No pytest: every `test_*` function here takes no arguments, per `tests/run_all.py`. Nothing
here runs git; the runner is a fake and every path lives in a temporary directory.
"""

from __future__ import annotations

import pathlib
import subprocess
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import test_rqa_remediation_fixtures as fx  # noqa: E402
from rqa.remediation.push import https_remote, push_head  # noqa: E402
from rqa.remediation.worktree import checkout_head, resolve_target  # noqa: E402

WORKTREE = pathlib.Path("/tmp/rqa-not-touched")


# -- the remote -----------------------------------------------------------------


def test_only_an_owner_name_pair_becomes_a_remote() -> None:
    assert https_remote(repo="acme/widgets") == "https://github.com/acme/widgets.git"
    for repo in (
        "acme/widgets --force",
        "-x/y",
        "acme/widgets:extra",
        "https://evil.example/acme/widgets",
        "acme/widgets/extra",
        "acme",
        "../../etc/passwd",
        "",
        "a/b\nc",
        None,
    ):
        assert https_remote(repo=repo) is None, repo


# -- the ref gate ---------------------------------------------------------------


def test_a_refused_ref_never_reaches_git_at_all() -> None:
    for head_ref in ("", "rqa/job", "rqa", "--force", "-f", "a b", "a..b", "x:y", "+x", "@{-1}",
                     "back\\slash", "with\nnewline", "/leading", ".hidden", "a//b", "x" * 400):
        runner = fx.FakeRunner()
        result = push_head(runner=runner, worktree=WORKTREE, head_repo=fx.REPO, head_ref=head_ref)
        assert result.returncode != 0, head_ref
        assert runner.calls == [], head_ref


def test_a_refused_remote_never_reaches_git_at_all() -> None:
    runner = fx.FakeRunner()
    result = push_head(runner=runner, worktree=WORKTREE, head_repo="not-a-repo", head_ref="main")
    assert result.returncode != 0
    assert runner.calls == []


def test_git_check_ref_format_runs_before_the_push_and_can_veto_it() -> None:
    runner = fx.FakeRunner(returncodes={"check-ref-format": 1})
    result = push_head(runner=runner, worktree=WORKTREE, head_repo=fx.REPO, head_ref="odd~ref")
    assert result.returncode != 0
    assert runner.ran("git", "push") == []

    runner = fx.FakeRunner(returncodes={"check-ref-format": 1})
    result = push_head(runner=runner, worktree=WORKTREE, head_repo=fx.REPO, head_ref="fine")
    assert result.returncode != 0
    assert runner.argvs == [("git", "check-ref-format", "--branch", "fine")]


def test_the_accepted_push_is_one_remote_one_refspec_and_no_option() -> None:
    runner = fx.FakeRunner()
    result = push_head(
        runner=runner, worktree=WORKTREE, head_repo=fx.FORK, head_ref="feature/tidy"
    )
    assert result.returncode == 0
    assert runner.argvs == [
        ("git", "check-ref-format", "--branch", "feature/tidy"),
        ("git", "push", f"https://github.com/{fx.FORK}.git", "HEAD:refs/heads/feature/tidy"),
    ]
    push = runner.argvs[-1]
    assert len(push) == 4, push
    assert not any(token.startswith("-") for token in push[2:]), push


# -- the checkout ---------------------------------------------------------------


def test_a_fetch_that_answered_with_another_commit_is_refused() -> None:
    with tempfile.TemporaryDirectory() as directory:
        worktree = pathlib.Path(directory) / "wt"
        runner = fx.FakeRunner(fetched_sha="d" * 40)
        assert checkout_head(runner=runner, worktree=worktree, job=fx.make_job()) is False
        assert runner.ran("git", "checkout") == []


def test_the_checkout_never_falls_back_to_the_head_ref() -> None:
    with tempfile.TemporaryDirectory() as directory:
        worktree = pathlib.Path(directory) / "wt"
        runner = fx.FakeRunner()
        assert checkout_head(runner=runner, worktree=worktree, job=fx.make_job()) is True
        tokens = runner.flat()
        assert fx.HEAD_REF not in tokens
        assert tokens.count(fx.HEAD_SHA) == 1


def test_a_missing_git_binary_is_a_refusal_not_an_exception() -> None:
    with tempfile.TemporaryDirectory() as directory:
        worktree = pathlib.Path(directory) / "wt"
        runner = fx.FakeRunner(missing=frozenset({"git"}))
        assert checkout_head(runner=runner, worktree=worktree, job=fx.make_job()) is False


# -- target confinement ----------------------------------------------------------


def test_resolve_target_accepts_only_a_regular_file_at_exactly_that_path() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = pathlib.Path(directory) / "wt"
        (root / "src").mkdir(parents=True)
        (root / "src" / "widget.py").write_bytes(fx.PY_BEFORE)
        assert resolve_target(worktree=root, path="src/widget.py") == (
            root.resolve() / "src" / "widget.py"
        )


def test_resolve_target_refuses_every_way_out_of_the_worktree() -> None:
    with tempfile.TemporaryDirectory() as directory:
        base = pathlib.Path(directory)
        root = base / "wt"
        (root / "src").mkdir(parents=True)
        outside = base / "outside.py"
        outside.write_bytes(fx.PY_BEFORE)
        (root / "src" / "link.py").symlink_to(outside)
        (root / "src" / "inside.py").write_bytes(fx.PY_BEFORE)
        (root / "src" / "loop.py").symlink_to(root / "src" / "loop.py")
        (root / "src" / "adir.py").mkdir()
        elsewhere = base / "elsewhere"
        elsewhere.mkdir()
        (elsewhere / "widget.py").write_bytes(fx.PY_BEFORE)
        (root / "linked").symlink_to(elsewhere, target_is_directory=True)
        # A symlink whose target is *inside* the root is still refused: the resolved path
        # is not the literal one, so the diff and the fingerprint would disagree.
        (root / "src" / "alias.py").symlink_to(root / "src" / "inside.py")

        for path in (
            "src/link.py",
            "src/loop.py",
            "src/adir.py",
            "linked/widget.py",
            "src/alias.py",
            "src/missing.py",
            "../outside.py",
            "src",
        ):
            assert resolve_target(worktree=root, path=path) is None, path


# -- Round 2: G2194-P10-M1 at this module's own two call sites -------------------

SECRET = "ghp_0123456789abcdefghijklmnopqrstuvwx"


class _RaisingRunner(fx.FakeRunner):
    """Raises a timeout carrying the child's own output at one chosen call."""

    def __init__(self, *, raise_at: int, **kwargs) -> None:
        super().__init__(**kwargs)
        self.raise_at = raise_at
        self.index = -1

    def run(self, *, cwd, argv, timeout):
        self.index += 1
        if self.index == self.raise_at:
            raise subprocess.TimeoutExpired(
                cmd=argv, timeout=timeout, output=SECRET.encode(), stderr=SECRET.encode()
            )
        return super().run(cwd=cwd, argv=argv, timeout=timeout)


def test_push_head_turns_a_runner_exception_into_a_non_zero_result_at_either_site() -> None:
    """Neither `git check-ref-format` nor `git push` may raise out of this module: the
    exception carries the child's stderr, and nothing above is entitled to see it."""
    for raise_at, expected_calls in ((0, 1), (1, 2)):
        runner = _RaisingRunner(raise_at=raise_at)
        result = push_head(
            runner=runner, worktree=WORKTREE, head_repo=fx.REPO, head_ref="feature/tidy"
        )
        assert result.returncode != 0, raise_at
        assert SECRET not in result.stderr.decode("utf-8"), raise_at
        assert len(runner.calls) == expected_calls - 1, raise_at


def test_push_head_never_pushes_after_a_failed_ref_check_process() -> None:
    runner = _RaisingRunner(raise_at=0)
    result = push_head(runner=runner, worktree=WORKTREE, head_repo=fx.REPO, head_ref="main")
    assert result.returncode != 0
    assert runner.ran("git", "push") == []
