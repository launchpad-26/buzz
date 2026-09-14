"""Isolated exact-head checkout, target confinement and unconditional cleanup —
`code/P-10-remediation.md` §3 steps 5-6, §4's `fetch_head()` and §5.

The operator's checkout is never the workspace. Every byte a formatter sees lives under
`state_dir/worktrees/<job.id>/`, a directory this module creates for one E-10 call and
`remove` deletes on every exit path — including the path where the record append raises.
Nothing here reads or writes anything outside that directory.

Two untrusted inputs are handled as data, never as instructions:

* `job.head_sha` becomes a fetch argument only after it is proven to be a lowercase hex
  object name, and the fetched result is checked against it. There is **no** fallback to
  `job.head_ref` or to any other ref: a fetch that did not produce exactly the pinned head
  fails, and the caller refuses with `NO_HEAD`.
* `remedy.paths` are re-resolved inside the checkout with `strict=True` before a formatter
  runs. A symlink, a symlinked parent, a directory, a device node, a missing file or
  anything whose resolved location is not the literal path beneath the worktree root is
  refused. Resolution happens *after* checkout precisely because the captured facts prove
  what was true at fetch time, not what is true on disk now.
"""

from __future__ import annotations

import re
import shutil
from pathlib import Path

from rqa.contracts import Job, ProcessRunner

from rqa.remediation.push import https_remote
from rqa.remediation.tools import RemediationError

__all__ = [
    "FETCH_TIMEOUT_SECONDS",
    "GIT_TIMEOUT_SECONDS",
    "WORKTREES_DIRNAME",
    "checkout_head",
    "path_for",
    "remove",
    "resolve_target",
]

#: The one directory name P-10 writes under `state_dir` (§5).
WORKTREES_DIRNAME = "worktrees"

FETCH_TIMEOUT_SECONDS = 900.0
GIT_TIMEOUT_SECONDS = 120.0

_JOB_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
_OBJECT_NAME = re.compile(r"^[0-9a-f]{40}$|^[0-9a-f]{64}$")


def path_for(*, state_dir: Path, job_id: str) -> Path:
    """`state_dir/worktrees/<job.id>/`.

    A job id is RQA-minted (`stable_hash(repo, number, head_sha)`), so an id that is not a
    single safe path segment is a programming error, not a refusal — and it is rejected
    before it can become a path at all.
    """
    if not isinstance(job_id, str) or not _JOB_ID.match(job_id) or job_id in (".", ".."):
        raise RemediationError(f"{job_id!r} is not a usable job id")
    return Path(state_dir) / WORKTREES_DIRNAME / job_id


def remove(*, path: Path) -> None:
    """Delete the worktree, whatever state it is in. Never raises, never follows a symlink.

    Called before creation (a crashed predecessor is removed, never reused) and in the
    `finally` of every exit path after creation.
    """
    try:
        if path.is_symlink() or (path.exists() and not path.is_dir()):
            path.unlink(missing_ok=True)
            return
        shutil.rmtree(path, ignore_errors=True)
    except OSError:
        return


def checkout_head(*, runner: ProcessRunner, worktree: Path, job: Job) -> bool:
    """Fetch exactly `job.head_sha` from `job.head_repo` and check it out detached.

    `fetch_head()` of §4: the remote is built from `job.head_repo`, the only ref-ish
    argument is the pinned object name, and `job.head_ref` is never a fetch fallback. The
    resolved `FETCH_HEAD` must equal the pinned SHA, so a remote that answered with a
    different commit fails instead of being formatted and pushed.
    """
    if not _OBJECT_NAME.match(job.head_sha or ""):
        return False
    remote = https_remote(repo=job.head_repo)
    if remote is None:
        return False
    try:
        worktree.mkdir(parents=True, exist_ok=False)
    except OSError:
        return False

    def git(argv: tuple[str, ...], *, timeout: float = GIT_TIMEOUT_SECONDS):
        """One git process, or `None` if it could not be run.

        Every exception is a `None` here — a missing binary, a timeout carrying the
        child's own output, anything else — and the exception object is neither retained
        nor re-raised, so nothing git printed can leave this module inside an exception
        (G2194-P10-M1). The `ProcessResult` never leaves `checkout_head`'s frame either.
        """
        try:
            return runner.run(cwd=worktree, argv=argv, timeout=timeout)
        except Exception:  # noqa: BLE001 - see the docstring
            return None

    for argv, timeout in (
        (("git", "init", "--quiet"), GIT_TIMEOUT_SECONDS),
        (("git", "fetch", "--no-tags", remote, job.head_sha), FETCH_TIMEOUT_SECONDS),
    ):
        result = git(argv, timeout=timeout)
        if result is None or result.returncode != 0:
            return False

    resolved = git(("git", "rev-parse", "FETCH_HEAD"))
    if resolved is None or resolved.returncode != 0:
        return False
    if not isinstance(resolved.stdout, bytes):
        return False
    try:
        fetched = resolved.stdout.decode("utf-8", "strict").strip()
    except UnicodeDecodeError:
        return False
    if fetched != job.head_sha:
        return False

    checked_out = git(("git", "checkout", "--detach", "FETCH_HEAD"))
    return checked_out is not None and checked_out.returncode == 0


def resolve_target(*, worktree: Path, path: str) -> Path | None:
    """The checked-out file for an already-validated remedy path, or `None`.

    `None` for a missing file, a symlink at any component, a directory, a non-regular
    file, or anything that resolves somewhere other than exactly `<root>/<path>`. The last
    condition is the escape check: the resolved root is compared with the literal join, so
    a symlinked parent — the usual way out of a sandbox — cannot match even when its target
    happens to be inside the root.
    """
    try:
        root = Path(worktree).resolve(strict=True)
        candidate = root / path
        if candidate.is_symlink():
            return None
        resolved = candidate.resolve(strict=True)
    except (OSError, RuntimeError, ValueError):
        return None
    if resolved != root / path:
        return None
    if resolved.is_symlink() or not resolved.is_file():
        return None
    return resolved
