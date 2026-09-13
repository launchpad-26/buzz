"""E-10 orchestration — `code/P-10-remediation.md` §3's fourteen ordered steps.

Remediation authority is the largest new exposure in RQA: it is the one place the system
writes to a human's branch. The ordering below is the security argument, not a style, and
every step is a thing a reviewer can point at:

* **Separately gated (step 1).** The `REMEDIATE` grant is *verified* here, never assumed and
  never implied by another activity. A mismatch on activity, repository, job, pinned
  snapshot or the finding's complete category set raises `RemediationError` before any
  record is written and before any directory exists. A `Deny` — or anything else that is
  not a `Grant` — is indistinguishable from no grant at all.
* **Bounded (steps 2-4).** Only a registered tool, with its registered check, over exact
  validated paths, on a head the pinned policy allows RQA to touch. All four refuse
  *before* a worktree exists.
* **Isolated (step 5 onward).** Everything happens under `state_dir/worktrees/<job.id>/`,
  removed in a `finally` on every exit path — so cleanup precedes even a propagating
  `AppendFailed`.
* **Proven neutral (steps 6, 9, 11).** The pre-fix fingerprints are captured before any
  formatter runs, and the post-fix bytes must reproduce them. An unavailable fingerprint is
  a refusal, never an optimistic pass.
* **Never elevated (step 13).** The only `git push` argv in RQA is `push.push_head`'s, and
  it cannot construct a force, a second refspec or another ref.

No credential, token or key is read, held, logged or recorded here, and no subprocess
output is copied into a `detail` or into the record: a refusal names what failed and its
exit status, never the bytes a tool printed.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

from rqa.contracts import (
    Activity,
    Facts,
    Finding,
    Grant,
    Job,
    ProcessRunner,
    RecordWriter,
    RemediationPushed,
    RemediationRefused,
    RemediationRefusalReason,
    Snapshot,
)

from rqa.remediation import worktree as worktree_mod
from rqa.remediation.push import push_head
from rqa.remediation.tools import (
    MECHANICAL_TOOL_SET,
    RemediationError,
    ToolSpec,
    build_argv,
    check_passed,
    semantic_fingerprint,
    validate_remedy_paths,
)

__all__ = ["TOOL_TIMEOUT_SECONDS", "remediate"]

_REASON = RemediationRefusalReason

TOOL_TIMEOUT_SECONDS = 300.0

#: A file a formatter is allowed to be pointed at. Larger than this and no fingerprint is
#: produced, so the remediation refuses rather than loading an unbounded amount of an
#: attacker-influenced branch into memory.
_MAX_FILE_BYTES = 4 * 1024 * 1024

#: Kept out of the commit message, which is built from a fixed template plus this.
_SAFE_ID = frozenset("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-")

_COMMIT_NAME = "RQA Remediation"
_COMMIT_EMAIL = "rqa@users.noreply.github.com"


def _safe(identifier: str, *, limit: int = 64) -> str:
    """An id reduced to what may appear in a commit message or a record payload."""
    kept = "".join(character for character in str(identifier) if character in _SAFE_ID)
    return kept[:limit] or "unnamed"


# --------------------------------------------------------------------------
# Step 1 — the grant gate. Raises; never refuses politely.
# --------------------------------------------------------------------------


def _require_verified_grant(
    *, job: Job, finding: Finding, grant: Grant, facts: Facts, snapshot: Snapshot
) -> None:
    """§3 step 1, before any record or worktree action.

    Every clause is an equality against something the caller pinned: the grant must be for
    *this* activity, repository, job, snapshot and the finding's *complete* category set —
    set equality, never a subset test, so a grant for `{MECHANICAL}` cannot authorise a
    finding that is also `{PROCEDURAL}`. The facts must describe the same PR head as the
    job, so the bytes that were classified are the bytes about to be rewritten.
    """
    if not isinstance(grant, Grant):
        raise RemediationError(
            "remediate requires a verified Grant; a Deny or a missing grant is not one"
        )
    if grant.activity is not Activity.REMEDIATE:
        raise RemediationError(
            f"grant authorises {grant.activity!r}, not {Activity.REMEDIATE!r}"
        )
    if grant.repo != job.repo:
        raise RemediationError(f"grant is for repo {grant.repo!r}, job is {job.repo!r}")
    if grant.job_id != job.id:
        raise RemediationError(f"grant is for job {grant.job_id!r}, job is {job.id!r}")
    if grant.snapshot_hash != snapshot.hash:
        raise RemediationError(
            f"grant pins snapshot {grant.snapshot_hash!r}, snapshot is {snapshot.hash!r}"
        )
    if grant.categories != finding.categories:
        raise RemediationError(
            "grant categories do not equal the finding's complete category set"
        )

    pr = facts.pr
    for name, from_facts, from_job in (
        ("repo", pr.repo, job.repo),
        ("number", pr.number, job.number),
        ("head_sha", pr.head_sha, job.head_sha),
        ("base_sha", pr.base_sha, job.base_sha),
        ("head_repo", pr.head_repo, job.head_repo),
        ("head_ref", pr.head_ref, job.head_ref),
    ):
        if from_facts != from_job:
            raise RemediationError(
                f"facts.pr.{name}={from_facts!r} does not match job.{name}={from_job!r}"
            )


# --------------------------------------------------------------------------
# Process execution. Every `runner.run(...)` in this module goes through one of
# the four helpers below, and each of them returns a plain value.
#
# Two properties they exist to hold (G2194-P10-M1):
#
# * **Every** failure mode is a value, not an exception. A missing binary, a
#   timeout, a runner that raises anything at all — each becomes a status or a
#   `None`, and the caller turns that into a named `RemediationRefused`. The
#   original exception object is neither retained nor re-raised, so nothing a
#   child process printed can travel out of this module inside
#   `TimeoutExpired.stderr`, a `__context__` chain, or an exception's traceback.
# * A `ProcessResult` never escapes the helper's own frame. `remediate` binds
#   integers, booleans and validated strings, never a child's stdout/stderr, so
#   a later propagating `AppendFailed` cannot reach process bytes through this
#   module's frame locals either.
# --------------------------------------------------------------------------


def _status(
    *, runner: ProcessRunner, cwd: Path, argv: tuple[str, ...], timeout: float
) -> int | None:
    """The exit status of one process, or `None` if it could not be run at all.

    `None` rather than a reserved integer (G2194-P10-NEW2): on POSIX a process killed by
    signal N reports `-N`, so *every* integer including `-1` is a legal status a process
    that genuinely ran can report. A sentinel inside the integer channel would classify a
    `SIGHUP`-killed formatter as "could not be run" when §3 step 7 requires `TOOL_FAILED`.
    """
    try:
        return runner.run(cwd=cwd, argv=argv, timeout=timeout).returncode
    except Exception:  # noqa: BLE001 - a process failure is a status here, never a raise
        return None


def _check_status(
    *, runner: ProcessRunner, cwd: Path, spec: ToolSpec, argv: tuple[str, ...], timeout: float
) -> bool | None:
    """Did the registered check report a clean tree? `None` if it could not be run."""
    try:
        result = runner.run(cwd=cwd, argv=argv, timeout=timeout)
    except Exception:  # noqa: BLE001 - see this section's comment
        return None
    return check_passed(spec=spec, result=result)


def _resolved_head(*, runner: ProcessRunner, cwd: Path, timeout: float) -> str | None:
    """`git rev-parse HEAD` as a validated object name, or `None`.

    The only thing that leaves this frame is a string of hex digits; the raw stdout does
    not.
    """
    try:
        result = runner.run(cwd=cwd, argv=("git", "rev-parse", "HEAD"), timeout=timeout)
    except Exception:  # noqa: BLE001 - see this section's comment
        return None
    if result.returncode != 0 or not isinstance(result.stdout, bytes):
        return None
    resolved = result.stdout.decode("utf-8", "replace").strip()
    if not resolved or any(character not in "0123456789abcdef" for character in resolved):
        return None
    return resolved


def _push_status(
    *, runner: ProcessRunner, worktree: Path, head_repo: str, head_ref: str
) -> int | None:
    """`push_head`'s exit status, or `None` if it could not be run at all.

    `None` for the same reason `_status` uses it: no integer is reserved, because any
    integer is a status a real process can report. The `ProcessResult` is confined to this
    frame either way.
    """
    try:
        return push_head(
            runner=runner, worktree=worktree, head_repo=head_repo, head_ref=head_ref
        ).returncode
    except Exception:  # noqa: BLE001 - see this section's comment
        return None


# --------------------------------------------------------------------------
# Step 8 — the exact changed set. No pattern matching exists here.
# --------------------------------------------------------------------------


def _changed_paths(*, runner: ProcessRunner, worktree: Path) -> frozenset[str] | None:
    """`git diff --name-only -z`, as an exact set. `None` for failure or malformed output.

    NUL-delimited output is the only form read, so a path containing a newline or a quote
    cannot split a record into two, and a truncated or non-UTF-8 answer is a refusal rather
    than a guess. The decoded names are the only thing that leaves this frame.
    """
    try:
        result = runner.run(
            cwd=worktree,
            argv=("git", "diff", "--name-only", "-z"),
            timeout=worktree_mod.GIT_TIMEOUT_SECONDS,
        )
    except Exception:  # noqa: BLE001 - see the process-execution section above
        return None
    if result.returncode != 0:
        return None
    raw = result.stdout
    if not isinstance(raw, bytes):
        return None
    if raw == b"":
        return frozenset()
    if not raw.endswith(b"\x00"):
        return None
    names: set[str] = set()
    for chunk in raw.split(b"\x00")[:-1]:
        if chunk == b"":
            return None
        try:
            names.add(chunk.decode("utf-8", "strict"))
        except UnicodeDecodeError:
            return None
    return frozenset(names)


# --------------------------------------------------------------------------
# Steps 6, 9 and 11 — fingerprints over bytes actually on disk.
# --------------------------------------------------------------------------


def _read_target(*, worktree: Path, path: str) -> bytes | None:
    target = worktree_mod.resolve_target(worktree=worktree, path=path)
    if target is None:
        return None
    try:
        if target.stat().st_size > _MAX_FILE_BYTES:
            return None
        return target.read_bytes()
    except OSError:
        return None


def _fingerprint(*, spec: ToolSpec, worktree: Path, path: str) -> bytes | None:
    content = _read_target(worktree=worktree, path=path)
    if content is None:
        return None
    return semantic_fingerprint(oracle=spec.equivalence_id, path=path, content=content)


def _content_digests(*, worktree: Path, paths: tuple[str, ...]) -> dict[str, bytes | None]:
    """Exact bytes of every target, digested — the tree state a fixpoint is compared to."""
    digests: dict[str, bytes | None] = {}
    for path in paths:
        content = _read_target(worktree=worktree, path=path)
        digests[path] = None if content is None else hashlib.sha256(content).digest()
    return digests


# --------------------------------------------------------------------------
# E-10.
# --------------------------------------------------------------------------


def remediate(*, job: Job, finding: Finding, grant: Grant, facts: Facts, snapshot: Snapshot,
              state_dir: Path, runner: ProcessRunner, record: RecordWriter) -> RemediationPushed | RemediationRefused:
    """Apply one exact mechanical remedy to one PR head branch, or refuse and say why.

    Returns `RemediationPushed` only after the fix was applied in an isolated checkout of
    the pinned head, the actual diff was proven in scope and behavior-equivalent, the
    registered check passed, the fix was a fixpoint, and one commit was pushed to the PR's
    own branch without force. Every other outcome is a `RemediationRefused` naming one of
    `CONTRACTS.md` §6's fifteen reasons. Exactly one `action` entry is written per value
    outcome, and `AppendFailed` propagates.
    """
    # -- step 1 ------------------------------------------------------------
    _require_verified_grant(job=job, finding=finding, grant=grant, facts=facts, snapshot=snapshot)

    remedy = finding.remedy
    tool_id = remedy.tool if remedy is not None else None

    def refuse(reason: RemediationRefusalReason, detail: str) -> RemediationRefused:
        """One refusal: one `action` entry, then the value (§6)."""
        payload: dict[str, object] = {"finding_id": finding.id}
        if tool_id is not None:
            payload["tool_id"] = tool_id
        payload["decision"] = "refused"
        payload["reason"] = reason.value
        payload["detail"] = detail
        entry = record.append(job.id, "action", payload)
        return RemediationRefused(reason=reason, detail=detail, entry_seq=entry.seq)

    def pushed(*, spec: ToolSpec, new_head_sha: str) -> RemediationPushed:
        entry = record.append(
            job.id,
            "action",
            {
                "finding_id": finding.id,
                "tool_id": spec.id,
                "decision": "pushed",
                "detail": f"{spec.id} applied to {len(remedy.paths)} file(s) and pushed",
                "new_head_sha": new_head_sha,
            },
        )
        return RemediationPushed(new_head_sha=new_head_sha, tool_id=spec.id, entry_seq=entry.seq)

    # -- step 2 ------------------------------------------------------------
    if remedy is None:
        return refuse(_REASON.REMEDY_MISSING, "the finding carries no remedy")
    spec = MECHANICAL_TOOL_SET.get(remedy.tool)
    if spec is None:
        return refuse(
            _REASON.TOOL_NOT_IN_SET, f"{_safe(remedy.tool)!r} is not in MECHANICAL_TOOL_SET"
        )
    if remedy.check != spec.check_id:
        return refuse(
            _REASON.CHECK_NOT_IN_SET,
            f"{_safe(remedy.check)!r} is not {spec.id}'s registered check {spec.check_id!r}",
        )

    # -- step 3 ------------------------------------------------------------
    if job.head_repo != job.repo and snapshot.policy.remediation.allow_forks is False:
        return refuse(
            _REASON.FORK_NOT_ALLOWED,
            f"head lives in a fork and the pinned policy {snapshot.hash} disallows forks",
        )
    if facts.pr.head_protected:
        return refuse(_REASON.HEAD_PROTECTED, "the PR head branch is protected")

    # -- step 4 ------------------------------------------------------------
    if not validate_remedy_paths(remedy=remedy, facts=facts, finding=finding):
        return refuse(
            _REASON.INVALID_PATH,
            "the remedy does not name exact, unique, captured files this tool formats, "
            "including the finding's own location",
        )

    # -- step 5 ------------------------------------------------------------
    root = worktree_mod.path_for(state_dir=state_dir, job_id=job.id)
    try:
        # A crashed predecessor is removed, never reused: whatever is there was left by a
        # run that did not finish, and nothing in it has been proven.
        worktree_mod.remove(path=root)
        if not worktree_mod.checkout_head(runner=runner, worktree=root, job=job):
            return refuse(
                _REASON.NO_HEAD,
                f"could not check out {job.head_sha[:12]} from {_safe(job.head_repo, limit=128)}",
            )

        # -- step 6 --------------------------------------------------------
        before: dict[str, bytes] = {}
        for path in remedy.paths:
            fingerprint = _fingerprint(spec=spec, worktree=root, path=path)
            if fingerprint is None:
                return refuse(
                    _REASON.INVALID_PATH,
                    f"{path!r} is not a fingerprintable regular file inside the worktree",
                )
            before[path] = fingerprint

        fix_argv = build_argv(prefix=spec.fix_argv, paths=remedy.paths)
        check_argv = build_argv(prefix=spec.check_argv, paths=remedy.paths)

        # -- step 7 --------------------------------------------------------
        status = _status(runner=runner, cwd=root, argv=fix_argv, timeout=TOOL_TIMEOUT_SECONDS)
        if status is None:
            return refuse(_REASON.TOOL_UNAVAILABLE, f"{spec.id} could not be run")
        if status != 0:
            return refuse(_REASON.TOOL_FAILED, f"{spec.id} exited {status}")

        # -- step 8 --------------------------------------------------------
        permitted = frozenset(remedy.paths)
        changed = _changed_paths(runner=runner, worktree=root)
        if changed is None:
            return refuse(_REASON.SCOPE_EXCEEDED, "the changed-file set could not be read")
        if not changed <= permitted:
            outside = len(changed - permitted)
            # The foreign names are dropped here rather than merely left unreported: a
            # refusal appends to the record, and an append can raise (G2194-P10-M1).
            changed = None
            return refuse(
                _REASON.SCOPE_EXCEEDED,
                f"{outside} file(s) outside the remedy's exact paths changed",
            )

        # -- step 9 --------------------------------------------------------
        for path in sorted(changed):
            after = _fingerprint(spec=spec, worktree=root, path=path)
            if after is None or after != before[path]:
                return refuse(
                    _REASON.BEHAVIOUR_CHANGED,
                    f"{path!r} is not provably behavior-equivalent after {spec.id}",
                )

        # -- step 10 -------------------------------------------------------
        passed = _check_status(
            runner=runner, cwd=root, spec=spec, argv=check_argv, timeout=TOOL_TIMEOUT_SECONDS
        )
        if passed is None:
            return refuse(_REASON.TOOL_UNAVAILABLE, f"{spec.check_id} could not be run")
        if not passed:
            return refuse(
                _REASON.CHECK_STILL_FAILING, f"{spec.check_id} still fails after {spec.id}"
            )

        # -- step 11 -------------------------------------------------------
        settled = _content_digests(worktree=root, paths=remedy.paths)
        status = _status(runner=runner, cwd=root, argv=fix_argv, timeout=TOOL_TIMEOUT_SECONDS)
        if status is None:
            return refuse(_REASON.TOOL_UNAVAILABLE, f"{spec.id} could not be run")
        if status != 0:
            return refuse(_REASON.TOOL_FAILED, f"{spec.id} exited {status}")
        if _content_digests(worktree=root, paths=remedy.paths) != settled:
            # Scope and equivalence are re-checked over the second run's changes before the
            # weaker refusal is reported: a second run that escaped scope or altered
            # behavior is that, not merely a non-fixpoint.
            second = _changed_paths(runner=runner, worktree=root)
            if second is None or not second <= permitted:
                second = None
                return refuse(
                    _REASON.SCOPE_EXCEEDED, "the second fix changed files outside the remedy"
                )
            for path in sorted(second):
                after = _fingerprint(spec=spec, worktree=root, path=path)
                if after is None or after != before[path]:
                    return refuse(
                        _REASON.BEHAVIOUR_CHANGED,
                        f"{path!r} is not provably behavior-equivalent after {spec.id}",
                    )
            return refuse(_REASON.NOT_FIXPOINT, f"{spec.id} is not a fixpoint on these files")

        # -- the final verification, over the bytes about to be committed ----
        #
        # Unconditional, and compared against step 6's pre-fix fingerprints rather than
        # against any digest taken later (G2194-P10-F4). Step 9 fingerprints the tree the
        # *first* fix produced, and `settled` is taken after the check has already run, so
        # a check step that altered tracked bytes followed by a no-op second fix would
        # otherwise reach `git add` with bytes nothing ever compared to `before`. What
        # `CONTRACTS.md` §11 requires proven equivalent is the committed pair, so the last
        # word belongs here rather than to any earlier pass.
        final = _changed_paths(runner=runner, worktree=root)
        if final is None:
            return refuse(_REASON.SCOPE_EXCEEDED, "the changed-file set could not be read")
        if not final <= permitted:
            outside = len(final - permitted)
            final = None
            return refuse(
                _REASON.SCOPE_EXCEEDED,
                f"{outside} file(s) outside the remedy's exact paths changed",
            )
        for path in sorted(final):
            after = _fingerprint(spec=spec, worktree=root, path=path)
            if after is None or after != before[path]:
                return refuse(
                    _REASON.BEHAVIOUR_CHANGED,
                    f"{path!r} is not provably behavior-equivalent in the tree to be committed",
                )

        # -- step 12 -------------------------------------------------------
        message = (
            f"style({spec.id}): apply mechanical remedy for finding {_safe(finding.id)}\n"
            f"\nApplied by RQA under a verified remediate grant; proven behavior-equivalent "
            f"by {spec.equivalence_id}.\n"
        )
        commit_argv = (
            ("git", "add", "--") + remedy.paths,
            (
                "git",
                "-c",
                f"user.name={_COMMIT_NAME}",
                "-c",
                f"user.email={_COMMIT_EMAIL}",
                "commit",
                "-m",
                message,
            ),
        )
        for argv in commit_argv:
            status = _status(
                runner=runner, cwd=root, argv=argv, timeout=worktree_mod.GIT_TIMEOUT_SECONDS
            )
            if status is None or status != 0:
                return refuse(
                    _REASON.COMMIT_FAILED, f"{argv[0]} {argv[1]} could not be completed"
                )

        # The new HEAD is resolved here, with the commit that produced it, so that a
        # failure to resolve it is `COMMIT_FAILED` rather than an unnamed branch after a
        # push has already happened. Step 14 reports this value.
        new_head_sha = _resolved_head(
            runner=runner, cwd=root, timeout=worktree_mod.GIT_TIMEOUT_SECONDS
        )
        if new_head_sha is None:
            return refuse(_REASON.COMMIT_FAILED, "the new commit could not be resolved")

        # -- step 13 -------------------------------------------------------
        status = _push_status(
            runner=runner, worktree=root, head_repo=job.head_repo, head_ref=job.head_ref
        )
        if status is None or status != 0:
            return refuse(_REASON.PUSH_REJECTED, "git push did not complete")

        # -- step 14 -------------------------------------------------------
        return pushed(spec=spec, new_head_sha=new_head_sha)
    finally:
        # Unconditional, and before a propagating `AppendFailed` (§3, T16).
        worktree_mod.remove(path=root)

