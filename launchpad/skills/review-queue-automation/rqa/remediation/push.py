"""The validated PR-head refspec builder — `code/P-10-remediation.md` §3 step 13 and §4.

`push_head` is the **only** function in RQA that builds a `git push` argv. That is the
whole of the no-force-push guarantee: there is one construction site, its option list is a
literal with no branch that appends to it, and the refspec it builds is
`HEAD:refs/heads/{head_ref}` and nothing else. `--force`, `--force-with-lease`, `+ref` and
a second refspec are not "not passed" — there is no code path that could construct them.

A PR author controls the head branch's **name**, so `head_ref` is untrusted data. It is
never interpolated anywhere except as a whole argv element, and it must survive both a
local syntax gate and `git check-ref-format --branch` before a push argv exists at all. A
ref that fails either is reported as a non-zero `ProcessResult` without a push happening;
`remediate` turns that into `RemediationRefused(PUSH_REJECTED)`.

No credential appears here. The remote is a plain HTTPS URL; whatever credential helper the
operator has configured supplies authentication out of band, so no token can reach an argv,
a log line or the record.
"""

from __future__ import annotations

import re
from pathlib import Path

from rqa.contracts import ProcessResult, ProcessRunner

__all__ = ["PUSH_TIMEOUT_SECONDS", "https_remote", "push_head", "refused"]

#: Reported when this module refuses to build a push argv at all. Git's own "fatal"
#: status, so a caller that only looks at `returncode` cannot mistake it for success.
_REFUSED_RETURNCODE = 128

PUSH_TIMEOUT_SECONDS = 300.0
_REF_CHECK_TIMEOUT_SECONDS = 30.0

_REPO = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,99}/[A-Za-z0-9][A-Za-z0-9._-]{0,99}$")

#: Characters a branch name may never contain here, over and above what
#: `git check-ref-format --branch` rejects: a leading `-` would be an option, `+` and `:`
#: are refspec syntax, and `@{` is a reflog selector.
_FORBIDDEN_IN_REF = frozenset("\\:+?*[]^~ \t\x00")

_MAX_REF_LENGTH = 255


def refused(*, detail: str) -> ProcessResult:
    """A refusal shaped like a process outcome, so the caller has one branch to read."""
    return ProcessResult(returncode=_REFUSED_RETURNCODE, stdout=b"", stderr=detail.encode("utf-8"))


def https_remote(*, repo: str) -> str | None:
    """The HTTPS remote for `owner/name`, or `None` when that is not what `repo` is.

    Built from a validated `owner/name` only, so nothing an attacker controls can turn the
    remote into an option, another scheme, or another host.
    """
    if not isinstance(repo, str) or not _REPO.match(repo):
        return None
    return f"https://github.com/{repo}.git"


def _ref_syntax_ok(head_ref: object) -> bool:
    """The local gate, run before git is asked anything.

    `rqa/` is refused because an internal RQA ref is never the PR's own branch (§3 step 13);
    the rest keeps the name from being read as an option or as refspec syntax.
    """
    if not isinstance(head_ref, str) or not head_ref or len(head_ref) > _MAX_REF_LENGTH:
        return False
    if any(character < " " or character == "\x7f" for character in head_ref):
        return False
    if _FORBIDDEN_IN_REF & set(head_ref):
        return False
    if head_ref.startswith("-") or head_ref.startswith(".") or head_ref.startswith("/"):
        return False
    if "@{" in head_ref or ".." in head_ref or "//" in head_ref:
        return False
    if head_ref == "rqa" or head_ref.startswith("rqa/"):
        return False
    return True


def push_head(*, runner: ProcessRunner, worktree: Path, head_repo: str, head_ref: str) -> ProcessResult:
    """Push `HEAD` to exactly this PR head branch in exactly this repository.

    Validates `head_ref` first — locally, then with `git check-ref-format --branch` — and
    builds the remote from `head_repo`. The push argv below is the only one in RQA; it has
    no option after `push`, one remote and one refspec, and `--force` cannot be passed or
    constructed. A non-fast-forward update is therefore rejected by the server, which is
    the intended outcome: a head that moved under RQA is not RQA's to overwrite.
    """
    remote = https_remote(repo=head_repo)
    if remote is None:
        return refused(detail=f"{head_repo!r} is not an owner/name repository")
    if not _ref_syntax_ok(head_ref):
        return refused(detail=f"{head_ref!r} is not a pushable PR head branch name")
    try:
        checked = runner.run(
            cwd=worktree,
            argv=("git", "check-ref-format", "--branch", head_ref),
            timeout=_REF_CHECK_TIMEOUT_SECONDS,
        )
    except Exception:  # noqa: BLE001 - see this module's docstring (G2194-P10-M1)
        return refused(detail="git check-ref-format could not be run")
    if checked.returncode != 0:
        return refused(detail=f"git check-ref-format rejected {head_ref!r}")
    try:
        return runner.run(
            cwd=worktree,
            argv=("git", "push", remote, f"HEAD:refs/heads/{head_ref}"),
            timeout=PUSH_TIMEOUT_SECONDS,
        )
    except Exception:  # noqa: BLE001 - see this module's docstring (G2194-P10-M1)
        return refused(detail="git push could not be run")
