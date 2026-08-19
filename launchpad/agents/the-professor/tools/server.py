#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["mcp", "pyyaml"]
# ///
"""The Professor's tool-server — the Facts layer of the three-layer design in
launchpad/Research/the-professor-design.md.

An MCP server (stdio transport) exposing the facts this agent must not
recall from memory. Step 3 of the plan built two tools:

  - read_contract()    the handbook's page contract, fetched live
  - list_categories()  the handbook's live navigation categories

Step 4 adds a third:

  - resolve_pin()      resolves a repo ref to its full 40-char commit SHA

Step 5 adds a fourth:

  - path_exists_at()   does a path exist at a pinned commit? (bool)

Step 6 adds the fifth and last:

  - check_page()       runs the handbook's own provenance gate against a
                        draft page's content

The handbook tools fetch from launchpad-26/handbook at call time and never
bake its text into this file — per the design's own default: "nothing is
quoted from a document that changes... A quoted contract goes stale silently;
a read one cannot" (design doc, section "How the next agent gets built").

check_page() cannot follow the same "fetch one file via `gh api`" pattern the
other four tools use: the gate it must run (`scripts/check_provenance.py`)
imports a local `provenance` package -- several files, not one -- so it needs
a real directory tree on disk, not a single file's content. Design doc open
question 5 answers directly what check_page must do about this: "Does
`check_page` call the gate directly, or reimplement it? Reimplementing would
produce a second parser that drifts from the first -- the exact failure the
gate's own modules are structured to avoid." So check_page keeps a local git
checkout of launchpad-26/handbook and shells out to its real scripts as real
subprocesses, exactly as CI does -- it never re-parses the page contract's
rules in Python.

Runs as `uv run --script`, which is why the dependencies above are declared
inline (PEP 723) rather than via a requirements file or a checked-in venv:
this file is the single bare executable that a later step (Step 7's
buzz-acp wiring) must be able to spawn directly, with no `python3 <path>`
two-token form and no CLI flags. `uv` resolves and caches the dependencies
the first time this shebang line runs.
"""

import base64
import json
import os
import subprocess
import tempfile
from pathlib import Path

import yaml
from mcp.server.mcpserver import MCPServer

HANDBOOK_REPO = "launchpad-26/handbook"
HANDBOOK_CLONE_URL = f"https://github.com/{HANDBOOK_REPO}"
HANDBOOK_DEFAULT_BRANCH = "main"

# Where the local checkout used by check_page() lives, persisted across calls
# (and across server restarts) so every call is not a full re-clone. Under
# the system temp dir, not this repo's working tree -- it is a runtime cache
# of another repository's content, not something to commit here.
HANDBOOK_CLONE_DIR = Path(tempfile.gettempdir()) / "the-professor-handbook-checkout"

# Entries in the live mkdocs.yml `nav:` list that are excluded from
# list_categories(). Judgement call, stated here and in the report:
#
#   - "Home" (index.md) is a landing page, not a topic a reader picks
#     because they have a question about it.
#   - "The page contract" (page-contract.md) is reference material ABOUT
#     the corpus (what every page must carry), not a user-need category
#     the corpus is organized into. mkdocs.yml's own nav comment says the
#     hierarchy is "organised by user need, never by repository layout
#     (PRD Ruling 3)" -- the contract itself isn't a user need, it's the
#     spec the corpus is checked against.
#
# Excluding these two from the live 13-entry nav leaves the eleven entries
# PRD #4 Ruling 3 names. This code does not assert "13" or "11" as counts:
# it reads whatever the live nav contains and subtracts exactly these two
# titles, so it tracks the handbook if entries are ever added or renamed.
EXCLUDED_NAV_TITLES = {"Home", "The page contract"}

mcp = MCPServer(name="the-professor-tools")


def _fetch_handbook_file(path: str) -> str:
    """Fetch a file from launchpad-26/handbook at HEAD, live, via `gh api`.

    Uses the `gh` CLI (already authenticated in this environment) rather
    than a hand-rolled HTTP call with a token pulled from the environment,
    and never caches or bakes the result into source -- every call re-fetches.
    """
    result = subprocess.run(
        ["gh", "api", f"repos/{HANDBOOK_REPO}/contents/{path}", "-q", ".content"],
        capture_output=True,
        text=True,
        check=True,
        timeout=30,
    )
    encoded_content = result.stdout.strip()
    return base64.b64decode(encoded_content).decode("utf-8")


@mcp.tool()
def read_contract() -> str:
    """Return the current text of the handbook's page contract.

    Fetched live from launchpad-26/handbook's docs/page-contract.md at call
    time -- never quoted into a prompt, so it can never go stale relative to
    a cached or hardcoded copy. See design doc section 4, "What the contract
    must be read, never copied."
    """
    return _fetch_handbook_file("docs/page-contract.md")


@mcp.tool()
def list_categories() -> list[str]:
    """Return the handbook's live navigation categories.

    Parses launchpad-26/handbook's mkdocs.yml `nav:` list at call time (never
    hardcoded) and excludes two structural entries that are not "categories"
    in PRD #4 Ruling 3's sense -- see EXCLUDED_NAV_TITLES above for which two
    and why. The remainder are the slots pages are filed into by the
    question they answer.
    """
    raw_yaml = _fetch_handbook_file("mkdocs.yml")
    nav_entries = yaml.safe_load(raw_yaml)["nav"]
    titles = [next(iter(entry.keys())) for entry in nav_entries]
    return [title for title in titles if title not in EXCLUDED_NAV_TITLES]


_RATE_LIMIT_OR_AUTH_STATUSES = {"401", "403", "429"}


@mcp.tool()
def resolve_pin(repo: str, ref: str) -> str:
    """Resolve `ref` (branch, tag, or SHA) on `repo` to its full 40-character commit SHA.

    Calls `GET /repos/{repo}/commits/{ref}` live via `gh api` -- same fetch
    convention as `_fetch_handbook_file` above: `gh` is already authenticated
    in this environment, so this never hand-rolls an HTTP call with a token
    pulled from the environment.

    A prior review round on this plan flagged a real trap: an unauthenticated
    or rate-limited GitHub API response is an ordinary-looking JSON body (a
    "message" and a "status" field) that can be mistaken for a genuine bad
    ref/repo if it's allowed to fall through undetected. This tool reads that
    "status" field before deciding what happened, and raises an error that
    names auth/rate-limiting explicitly rather than letting it look like "no
    such ref". It also refuses to return anything that isn't exactly 40 hex
    characters, so a truncated or malformed response can never masquerade as
    a real SHA.
    """
    result = subprocess.run(
        ["gh", "api", f"repos/{repo}/commits/{ref}", "-q", ".sha"],
        capture_output=True,
        text=True,
        timeout=30,
    )

    if result.returncode != 0:
        status = None
        message = result.stderr.strip() or result.stdout.strip()
        try:
            error_body = json.loads(result.stdout)
            status = error_body.get("status")
            message = error_body.get("message", message)
        except json.JSONDecodeError:
            pass

        if status in _RATE_LIMIT_OR_AUTH_STATUSES:
            raise RuntimeError(
                f"resolve_pin({repo!r}, {ref!r}): GitHub API returned HTTP "
                f"{status} ({message}). This looks like a rate limit or an "
                "authentication problem, not a bad repo/ref -- check "
                "`gh auth status` and GitHub's current rate limit before "
                "treating this as a real defect."
            )
        raise RuntimeError(
            f"resolve_pin({repo!r}, {ref!r}) failed "
            f"(HTTP {status or 'unknown'}): {message}"
        )

    sha = result.stdout.strip()
    if len(sha) != 40 or any(c not in "0123456789abcdef" for c in sha):
        raise RuntimeError(
            f"resolve_pin({repo!r}, {ref!r}): gh api reported success but "
            f"returned {sha!r}, which is not a 40-character hex SHA. Refusing "
            "to return it -- this can happen when a rate-limited or partial "
            "response slips past error detection."
        )
    return sha


@mcp.tool()
def path_exists_at(repo: str, commit: str, path: str) -> bool:
    """Return whether `path` exists in `repo` at `commit`.

    Calls `GET /repos/{repo}/contents/{path}?ref={commit}` live via `gh api`
    -- same fetch convention as `resolve_pin` above. A 404 from GitHub is
    this tool's normal negative answer (`False`), not an error: a missing
    path is an expected result this tool exists to report, so it must not
    raise just because the file isn't there.

    That is deliberately narrower than "any non-zero exit is False". The
    same trap `resolve_pin` guards against applies here: an unauthenticated
    or rate-limited response is also a non-zero exit with a JSON error body,
    and it must not be allowed to look like an ordinary 404 -- that would
    silently misreport a real auth/rate-limit failure as "path does not
    exist". Only a response whose `status` field is literally "404" is
    treated as a real negative; auth/rate-limit statuses and anything else
    raise instead.
    """
    result = subprocess.run(
        ["gh", "api", f"repos/{repo}/contents/{path}?ref={commit}"],
        capture_output=True,
        text=True,
        timeout=30,
    )

    if result.returncode == 0:
        return True

    status = None
    message = result.stderr.strip() or result.stdout.strip()
    try:
        error_body = json.loads(result.stdout)
        status = error_body.get("status")
        message = error_body.get("message", message)
    except json.JSONDecodeError:
        pass

    if status == "404":
        return False

    if status in _RATE_LIMIT_OR_AUTH_STATUSES:
        raise RuntimeError(
            f"path_exists_at({repo!r}, {commit!r}, {path!r}): GitHub API "
            f"returned HTTP {status} ({message}). This looks like a rate "
            "limit or an authentication problem, not a real answer about "
            "whether the path exists -- check `gh auth status` and GitHub's "
            "current rate limit before treating this as 'path does not "
            "exist'."
        )

    raise RuntimeError(
        f"path_exists_at({repo!r}, {commit!r}, {path!r}) failed "
        f"(HTTP {status or 'unknown'}): {message}"
    )


def _refresh_handbook_checkout() -> Path:
    """Ensure a local, up-to-date checkout of launchpad-26/handbook exists on
    disk and return its root path.

    Refreshed on every call rather than cloned once and left to age: this
    file's whole convention (see the other four tools) is that nothing about
    the handbook is ever read from a copy that could have gone stale. A
    `fetch` + hard `reset` against a persistent clone gets the same freshness
    guarantee as re-cloning from scratch, for a fraction of the cost -- so
    there is no "refresh mechanism to build later" TODO here; refreshing IS
    the mechanism, run inline on every check_page() call.

    A prior clone missing its `.git` directory (e.g. the temp dir was cleared
    but partially recreated) is treated as absent and re-cloned from scratch,
    rather than trying to repair a half-present checkout in place.
    """
    if (HANDBOOK_CLONE_DIR / ".git").is_dir():
        fetch = subprocess.run(
            ["git", "fetch", "--depth", "1", "origin", HANDBOOK_DEFAULT_BRANCH],
            cwd=HANDBOOK_CLONE_DIR,
            capture_output=True,
            text=True,
            timeout=60,
        )
        if fetch.returncode != 0:
            raise RuntimeError(
                "check_page: could not refresh the handbook checkout at "
                f"{HANDBOOK_CLONE_DIR} (`git fetch` exit {fetch.returncode}): "
                f"{fetch.stderr.strip()}"
            )
        reset = subprocess.run(
            ["git", "reset", "--hard", f"origin/{HANDBOOK_DEFAULT_BRANCH}"],
            cwd=HANDBOOK_CLONE_DIR,
            capture_output=True,
            text=True,
            timeout=30,
        )
        if reset.returncode != 0:
            raise RuntimeError(
                "check_page: could not fast-forward the handbook checkout at "
                f"{HANDBOOK_CLONE_DIR} (`git reset` exit {reset.returncode}): "
                f"{reset.stderr.strip()}"
            )
    else:
        HANDBOOK_CLONE_DIR.parent.mkdir(parents=True, exist_ok=True)
        clone = subprocess.run(
            ["git", "clone", "--depth", "1", HANDBOOK_CLONE_URL, str(HANDBOOK_CLONE_DIR)],
            capture_output=True,
            text=True,
            timeout=120,
        )
        if clone.returncode != 0:
            raise RuntimeError(
                f"check_page: could not clone {HANDBOOK_CLONE_URL} to "
                f"{HANDBOOK_CLONE_DIR} (exit {clone.returncode}): {clone.stderr.strip()}"
            )
    return HANDBOOK_CLONE_DIR


def _subprocess_env_with_github_token() -> dict[str, str]:
    """The gate scripts (`provenance/github.py`) make their own GitHub API
    calls for pin verification and read `GITHUB_TOKEN`/`GH_TOKEN` from *their*
    process environment to do it -- `gh`'s own stored auth does not become
    that env var for a child process automatically, so it must be exported
    here explicitly.

    Never logs or returns the token itself -- only ever places it directly
    into the env mapping handed to `subprocess.run`.
    """
    result = subprocess.run(
        ["gh", "auth", "token"], capture_output=True, text=True, timeout=15
    )
    if result.returncode != 0:
        raise RuntimeError(
            "check_page: `gh auth token` failed "
            f"(exit {result.returncode}): {result.stderr.strip()}. The gate "
            "scripts need GITHUB_TOKEN/GH_TOKEN for their own pin-verification "
            "calls to the GitHub API -- check `gh auth status`."
        )
    env = dict(os.environ)
    env["GITHUB_TOKEN"] = result.stdout.strip()
    return env


@mcp.tool()
def check_page(draft_content: str) -> dict:
    """Run the handbook's real provenance gate against a draft page's content.

    Writes `draft_content` into an isolated scratch directory containing
    nothing else, then runs `scripts/check_provenance.py <dir> --format json`
    and `scripts/page_index.py <dir> -o /dev/null` from a local checkout of
    launchpad-26/handbook as real subprocesses -- the same two commands the
    handbook's own CI runs -- and returns their combined result.

    This deliberately does not re-parse the page contract's rules in Python.
    Design doc open question 5: reimplementing the gate "would produce a
    second parser that drifts from the first -- the exact failure the gate's
    own modules are structured to avoid." Calling the real scripts is the only
    way this tool's verdict can never disagree with CI's.

    Isolation matters because `check_provenance.py` takes a directory and
    `rglob`s it for every `*.md` file: pointing it at a directory holding any
    other page (or a fixture, or a stray file) would check all of them at
    once and blur which findings belong to this draft. Each call gets its own
    fresh temporary directory, used for nothing else and removed immediately
    after.

    Returns a dict with `findings`, `unchecked`, and `skipped` -- exactly the
    three keys `check_provenance.py --format json` reports, defined in that
    script's own docstring (a finding fails the build; unchecked is reported
    but blocks nothing because CI cannot read the private cohort repos;
    skipped means the page had no valid frontmatter so no rule ran on it at
    all) -- plus a `page_index` key reporting `page_index.py`'s own verdict:
    it independently validates required frontmatter fields and pin shape
    (e.g. a truncated commit SHA) that `check_provenance.py` does not check
    itself, so `page_index`'s errors are additional signal, not a duplicate
    of `findings`.
    """
    handbook_dir = _refresh_handbook_checkout()
    env = _subprocess_env_with_github_token()

    with tempfile.TemporaryDirectory(prefix="the-professor-check-page-") as scratch:
        scratch_dir = Path(scratch)
        (scratch_dir / "draft.md").write_text(draft_content, encoding="utf-8")

        provenance_run = subprocess.run(
            [
                "uv",
                "run",
                "--with",
                "pyyaml",
                "python3",
                str(handbook_dir / "scripts" / "check_provenance.py"),
                str(scratch_dir),
                "--format",
                "json",
            ],
            capture_output=True,
            text=True,
            timeout=60,
            env=env,
        )
        try:
            provenance_data = json.loads(provenance_run.stdout)
        except json.JSONDecodeError as exc:
            raise RuntimeError(
                "check_page: check_provenance.py did not produce parseable "
                f"JSON (exit {provenance_run.returncode}). stdout="
                f"{provenance_run.stdout!r} stderr={provenance_run.stderr!r}"
            ) from exc

        index_run = subprocess.run(
            [
                "uv",
                "run",
                "--with",
                "pyyaml",
                "python3",
                str(handbook_dir / "scripts" / "page_index.py"),
                str(scratch_dir),
                "-o",
                "/dev/null",
            ],
            capture_output=True,
            text=True,
            timeout=60,
            env=env,
        )

    return {
        "findings": provenance_data.get("findings", []),
        "unchecked": provenance_data.get("unchecked", []),
        "skipped": provenance_data.get("skipped", []),
        "page_index": {
            "ok": index_run.returncode == 0,
            "errors": [
                line for line in index_run.stderr.splitlines() if line.strip()
            ],
        },
    }


if __name__ == "__main__":
    mcp.run()  # defaults to stdio transport
