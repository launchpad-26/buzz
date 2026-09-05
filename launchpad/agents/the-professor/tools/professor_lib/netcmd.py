"""`resolve-pin` / `path-exists-at` -- the network-backed half of professor.py's
tool layer (redesign doc §4's `netcmd` subgraph: "external citations only").

Thin ports of `server.py`'s `resolve_pin`/`path_exists_at` -- same validation
(40-hex-char SHA check, `_RATE_LIMIT_OR_AUTH_STATUSES` handling, `path`'s `?`/`&`
rejection, `commit` shape check), same `gh api` calls -- minus the `@mcp.tool()`
decorator and the `mcp` import (redesign doc §9, Phase 1: "resolve-pin and
path-exists-at are thin ports of the current server.py functions minus the
@mcp.tool() decorators and the mcp import").

This is always the network-backed, GitHub-API path (§4 places both in the
`netcmd` half of the tool-call diagram, for citing sources genuinely external to
whatever repo is being documented) -- `check-page`'s citation-existence check
(step 4) must NOT reuse this for a citation to its own `--target`'s tree; only a
citation to a genuinely different, external repo goes through here.
"""

import json
import re
import subprocess
import sys

_RATE_LIMIT_OR_AUTH_STATUSES = {"401", "403", "429"}

# GitHub's default squash-merge format appends "(#NNNN)" to the end of the
# commit subject (message's first line) -- the same rule `draft-page`/
# `update-page`'s SKILL.md apply to `git log`'s `%s` for a target-repo's own
# commit, applied here to the API response's `.commit.message` field instead
# (redesign doc, "output schema changes"). Only ever read from this one
# `gh api` response already being made -- never a second network call.
TRAILING_PR_RE = re.compile(r"\(#(\d+)\)\s*$")


def _run_gh_api(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["gh", "api", *args],
        capture_output=True,
        text=True,
        timeout=30,
    )


def _parse_error_status(result: subprocess.CompletedProcess) -> tuple[str | None, str]:
    """Read a failed `gh api` call's JSON error body, if any, for its `status` and
    `message` fields -- same trap `server.py`'s tools guard against: an
    unauthenticated or rate-limited response is an ordinary-looking JSON body that
    can be mistaken for a genuine bad ref/repo/path if it's allowed to fall through
    undetected.
    """
    status = None
    message = result.stderr.strip() or result.stdout.strip()
    try:
        error_body = json.loads(result.stdout)
        status = error_body.get("status")
        message = error_body.get("message", message)
    except json.JSONDecodeError:
        pass
    return status, message


def resolve_pin(repo: str, ref: str) -> int:
    """Resolve `ref` (branch, tag, or SHA) on `repo` to its full 40-character
    commit SHA, plus the author, date, and originating PR (if any) -- all
    read from the one `gh api repos/{repo}/commits/{ref}` call already being
    made, never a second round-trip. Prints a JSON object to stdout on
    success: `{"commit": "<sha>", "commit_author": "<name> <<email>>",
    "commit_at": "<ISO 8601>", "pr": <int|null>}` (redesign doc's "output
    schema changes" -- Phase 1 replaces the old bare-SHA-string output with
    this structured shape, since `draft-page`/`update-page`'s SKILL.md both
    already destructure these four fields from this call).
    """
    result = _run_gh_api([f"repos/{repo}/commits/{ref}"])

    if result.returncode != 0:
        status, message = _parse_error_status(result)
        if status in _RATE_LIMIT_OR_AUTH_STATUSES:
            print(
                f"resolve-pin({repo!r}, {ref!r}): GitHub API returned HTTP "
                f"{status} ({message}). This looks like a rate limit or an "
                "authentication problem, not a bad repo/ref -- check "
                "`gh auth status` and GitHub's current rate limit before "
                "treating this as a real defect.",
                file=sys.stderr,
            )
        else:
            print(
                f"resolve-pin({repo!r}, {ref!r}) failed "
                f"(HTTP {status or 'unknown'}): {message}",
                file=sys.stderr,
            )
        return 1

    try:
        commit_data = json.loads(result.stdout)
    except json.JSONDecodeError:
        print(
            f"resolve-pin({repo!r}, {ref!r}): gh api reported success but "
            f"did not return valid JSON: {result.stdout!r}. Refusing to "
            "print it -- this can happen when a rate-limited or partial "
            "response slips past error detection.",
            file=sys.stderr,
        )
        return 1

    sha = commit_data.get("sha", "")
    if not isinstance(sha, str) or len(sha) != 40 or any(
        c not in "0123456789abcdef" for c in sha
    ):
        print(
            f"resolve-pin({repo!r}, {ref!r}): gh api reported success but "
            f"`.sha` was {sha!r}, which is not a 40-character hex SHA. "
            "Refusing to print it -- this can happen when a rate-limited or "
            "partial response slips past error detection.",
            file=sys.stderr,
        )
        return 1

    commit = commit_data.get("commit") or {}
    author = commit.get("author") or {}
    author_name = author.get("name", "")
    author_email = author.get("email", "")
    commit_author = f"{author_name} <{author_email}>"
    commit_at = author.get("date")
    message = commit.get("message") or ""
    subject = message.splitlines()[0] if message else ""
    pr_match = TRAILING_PR_RE.search(subject)
    pr = int(pr_match.group(1)) if pr_match else None

    print(
        json.dumps(
            {
                "commit": sha,
                "commit_author": commit_author,
                "commit_at": commit_at,
                "pr": pr,
            }
        )
    )
    return 0


def path_exists_at(repo: str, commit: str, path: str) -> int:
    """Return (via exit code and stdout) whether `path` exists in `repo` at
    `commit`. Prints `true` or `false` to stdout on success.
    """
    if len(commit) != 40 or any(c not in "0123456789abcdef" for c in commit):
        print(
            f"path-exists-at({repo!r}, {commit!r}, {path!r}): `commit` is not "
            "a 40-character hex SHA. This tool checks existence at a pinned "
            "commit, not a branch or tag -- resolve it with resolve-pin "
            "first.",
            file=sys.stderr,
        )
        return 1
    if "?" in path or "&" in path:
        print(
            f"path-exists-at({repo!r}, {commit!r}, {path!r}): `path` contains "
            "'?' or '&', which cannot appear in a real repository path. "
            "Refusing rather than risk it being interpreted as part of the "
            "request's query string.",
            file=sys.stderr,
        )
        return 1

    result = subprocess.run(
        [
            "gh",
            "api",
            f"repos/{repo}/contents/{path}",
            "--method",
            "GET",
            "-f",
            f"ref={commit}",
        ],
        capture_output=True,
        text=True,
        timeout=30,
    )

    if result.returncode == 0:
        print("true")
        return 0

    status, message = _parse_error_status(result)

    if status == "404":
        print("false")
        return 0

    if status in _RATE_LIMIT_OR_AUTH_STATUSES:
        print(
            f"path-exists-at({repo!r}, {commit!r}, {path!r}): GitHub API "
            f"returned HTTP {status} ({message}). This looks like a rate "
            "limit or an authentication problem, not a real answer about "
            "whether the path exists -- check `gh auth status` and GitHub's "
            "current rate limit before treating this as 'path does not "
            "exist'.",
            file=sys.stderr,
        )
        return 1

    print(
        f"path-exists-at({repo!r}, {commit!r}, {path!r}) failed "
        f"(HTTP {status or 'unknown'}): {message}",
        file=sys.stderr,
    )
    return 1


def path_exists_at_bool(repo: str, commit: str, path: str) -> tuple[bool | None, str | None]:
    """In-process variant returning a real `bool` (or `None` on error) plus an
    explanatory message when the result is `None`, for step 4's `check-page` to
    call directly when a citation names a genuinely external repo -- never a
    self-subprocess call to `professor.py` itself.

    `None` means "could not verify" (rate limit, auth problem, or some other
    API failure) -- a caller must not collapse this into the same outcome as a
    confirmed `False` (a genuine 404). This mirrors `path_exists_at`'s own
    rate-limit/auth distinction above, just returned as data instead of
    printed to stderr, since this in-process variant has no stderr of its own
    for a caller to inspect.
    """
    if len(commit) != 40 or any(c not in "0123456789abcdef" for c in commit):
        return None, (
            f"path-exists-at-bool({repo!r}, {commit!r}, {path!r}): `commit` is "
            "not a 40-character hex SHA."
        )
    if "?" in path or "&" in path:
        return None, (
            f"path-exists-at-bool({repo!r}, {commit!r}, {path!r}): `path` "
            "contains '?' or '&', which cannot appear in a real repository path."
        )

    result = subprocess.run(
        [
            "gh",
            "api",
            f"repos/{repo}/contents/{path}",
            "--method",
            "GET",
            "-f",
            f"ref={commit}",
        ],
        capture_output=True,
        text=True,
        timeout=30,
    )

    if result.returncode == 0:
        return True, None

    status, message = _parse_error_status(result)
    if status == "404":
        return False, None

    if status in _RATE_LIMIT_OR_AUTH_STATUSES:
        return None, (
            f"path-exists-at-bool({repo!r}, {commit!r}, {path!r}): GitHub API "
            f"returned HTTP {status} ({message}). This looks like a rate limit "
            "or an authentication problem, not a real answer about whether the "
            "path exists -- check `gh auth status` and GitHub's current rate "
            "limit before treating this as a confirmed citation defect."
        )

    return None, (
        f"path-exists-at-bool({repo!r}, {commit!r}, {path!r}) failed "
        f"(HTTP {status or 'unknown'}): {message}"
    )
