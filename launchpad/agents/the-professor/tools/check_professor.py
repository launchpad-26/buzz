#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Test harness for professor.py -- Phase 1 (§9) of
launchpad/Research/the-professor-skill-suite-redesign.md.

Matches check_server.py's own rigor, ported from MCP-over-stdio to plain
subprocess calls (professor.py has no MCP dependency at all -- that is the
whole point of this redesign, §1a/§4):

  - resolve-pin's output is cross-checked against `git ls-remote` independently
    (not a recorded value), same as check_server.py's own resolve_pin check.
  - path-exists-at is exercised for both the true and false case against a
    real pinned commit (resolved via resolve-pin, not hardcoded).
  - check-page and screen-content are each run against every fixture in
    tools/contract/fixtures/ (steps 3 and 5 of this plan), asserting the
    SPECIFIC expected verdict per fixture -- not just "some finding exists".
  - At least one call is made from a working directory outside this fork's
    checkout with $PROFESSOR_PACK_ROOT set to an arbitrary path, proving pack-
    root resolution actually works away from this fork -- Phase 1's own
    review gate (§9) requires this explicitly.
  - A separate run with $PROFESSOR_PACK_ROOT deliberately unset asserts the
    exact required error text from step 1, for all four subcommands.

Exit code 0 and "ALL CHECKS PASSED" on success; non-zero and a message naming
the specific failing check otherwise -- never a bare non-zero exit, matching
this plan's own step 7 done-when.
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

TOOLS_DIR = Path(__file__).parent
PROFESSOR_PY = TOOLS_DIR / "professor.py"
FIXTURES_DIR = TOOLS_DIR / "contract" / "fixtures"
REPO_ROOT = TOOLS_DIR.parents[3]  # tools/ -> the-professor/ -> agents/ -> launchpad/ -> repo root

# A real, valid Professor pack root -- this worktree's own the-professor/
# directory, which genuinely contains tools/contract/{page-contract,
# sensitive-patterns}.md (step 4 of the 2026-09-06 fix round: check_page and
# screen_content now confirm pack_root points at a real pack installation, so
# check-page/screen-content calls below can no longer use an arbitrary /tmp
# pack_root the way resolve-pin/path-exists-at calls still can -- pack_root
# is irrelevant to those two subcommands).
PACK_ROOT = TOOLS_DIR.parent

EXTERNAL_REPO = "block/buzz"
EXTERNAL_REF = "main"
EXTERNAL_EXISTING_PATH = "Cargo.toml"
EXTERNAL_MISSING_PATH = "THIS_FILE_DOES_NOT_EXIST_9f8e7d6c.md"

# The local-citation commit every check-page fixture below pins to (a real
# commit in this checkout's own history, per localcmd.py's shallow-clone-
# safety comment around line 114: a shallow clone can legitimately be
# missing a commit that is entirely real upstream). Fixed rather than
# re-derived from HEAD, matching every other fixture in this file.
FIXTURE_PINNED_COMMIT = "c552723895f5bfbf399db7e3135a22026597e70a"


def _commit_present_in_local_history(target: str, commit: str) -> bool:
    """Whether `commit` resolves in `target`'s local git history -- the same
    `git cat-file -e <commit>^{commit}` check `_local_citation_exists`
    (localcmd.py) makes, reused here so the harness asks the identical
    question rather than a second, possibly-diverging one (step 5 of the
    2026-09-06 fix round).
    """
    result = subprocess.run(
        ["git", "-C", target, "cat-file", "-e", f"{commit}^{{commit}}"],
        capture_output=True,
        text=True,
        timeout=15,
    )
    return result.returncode == 0


def check_fixture_commit_shallow_clone_safety() -> tuple[str | None, bool]:
    """`check_check_page_fixtures` below skips (rather than fails) any
    fixture assertion that depends on `FIXTURE_PINNED_COMMIT` when that
    commit is not present in this checkout's local history -- a shallow
    clone (`git clone --depth 1`, or GitHub Actions' default checkout depth)
    can legitimately be missing a commit that is entirely real upstream, and
    must never be misreported as "this fixture's expected rule is wrong"
    (step 5 of the 2026-09-06 fix round).

    Returns `(error_or_None, shallow_clone)`. A prior round's version of this
    function returned a hard failure whenever `FIXTURE_PINNED_COMMIT` was
    absent -- a mandatory check running immediately before
    `check_check_page_fixtures` in `main()`'s own sequence, so that hard
    failure pre-empted `check_check_page_fixtures`'s own, already-correct
    skip logic before it ever had a chance to run: a genuinely shallow clone
    still failed the whole harness instead of skipping cleanly (step 7 of the
    2026-09-06 fix round). Fixed here by separating the two distinct
    conditions this function was conflating: `shallow_clone=True` (with no
    error) is the ordinary, expected shallow-clone case -- the caller reports
    a clean, named skip for it, not a failure. Only a genuinely broken
    detection mechanism -- a fabricated, guaranteed-absent commit incorrectly
    reported as present, checked unconditionally, regardless of whether the
    real pinned commit happens to be present -- still returns a hard error.
    """
    fabricated_commit = "f" * 40
    if _commit_present_in_local_history(str(REPO_ROOT), fabricated_commit):
        return (
            f"a fabricated, guaranteed-absent commit {fabricated_commit!r} was "
            "reported as present -- the shallow-clone-safety detection itself "
            "is broken",
            False,
        )

    if not _commit_present_in_local_history(str(REPO_ROOT), FIXTURE_PINNED_COMMIT):
        return None, True

    return None, False


CHECK_PAGE_EXPECTED_RULES = {
    "compliant-local.md": [],
    "compliant-external.md": [],
    "compliant-fenced-code.md": [],
    "compliant-tilde-fenced-code.md": [],
    "compliant-nested-fence-length.md": [],
    "compliant-fenced-fake-claim-and-citation.md": [],
    "compliant-long-shortsha.md": [],
    "compliant-range-at-end.md": [],
    "broken-nonexistent-citation.md": ["citation-not-found"],
    "broken-missing-citation.md": ["missing-citation"],
    "broken-unparseable-citation.md": ["missing-citation"],
    "broken-preamble-uncited-claim.md": ["missing-citation"],
    "broken-setext-only-heading.md": ["missing-citation"],
    "broken-no-headings-at-all.md": ["missing-citation"],
    "broken-out-of-bounds-range.md": ["out-of-bounds-range"],
    "broken-end-line-explicit-zero.md": ["out-of-bounds-range"],
    "broken-external-out-of-bounds-range.md": ["out-of-bounds-range"],
    "external-citation-range-not-evaluated.md": ["citation-range-not-evaluated"],
    "broken-no-provenance-marker.md": ["missing-provenance-marker"],
    "broken-mismatched-marker.md": ["mismatched-provenance-marker"],
    "broken-marker-partial-garbage.md": ["malformed-provenance-marker"],
    "broken-marker-total-garbage.md": ["malformed-provenance-marker"],
    "broken-mixed-claim.md": ["mixed-claim"],
    "broken-frontmatter.md": ["frontmatter"],
    "broken-frontmatter-unparseable-yaml.md": ["frontmatter"],
    "broken-frontmatter-non-mapping.md": ["frontmatter"],
    "broken-frontmatter-missing-field.md": ["frontmatter"],
}

# _parse_frontmatter has four distinct failure branches, all sharing the
# "frontmatter" rule label above -- this maps each dedicated fixture to a
# substring unique to the branch it targets, so the suite can assert on
# *which* branch actually fired, not just that some "frontmatter" finding did.
FRONTMATTER_BRANCH_EXPECTED_MESSAGE_SUBSTRING = {
    "broken-frontmatter.md": "no frontmatter block found",
    "broken-frontmatter-unparseable-yaml.md": "not valid YAML",
    "broken-frontmatter-non-mapping.md": "did not parse to a mapping",
    "broken-frontmatter-missing-field.md": "missing required field(s)",
}

SCREEN_CONTENT_EXPECTED = {
    "clean.md": {"disposition_by_category": {}},
    "block-api-key.md": {"disposition_by_category": {"api-key-token": "block"}},
    "block-high-entropy-token.md": {"disposition_by_category": {"api-key-token": "block"}},
    "block-high-entropy-token-underscore-boundary.md": {
        "disposition_by_category": {"api-key-token": "block"}
    },
    "block-private-key.md": {"disposition_by_category": {"private-key": "block"}},
    "block-connection-string.md": {"disposition_by_category": {"connection-string": "block"}},
    "block-password-literal.md": {"disposition_by_category": {"connection-string": "block"}},
    "block-webhook-url.md": {"disposition_by_category": {"webhook-url-token": "block"}},
    "block-webhook-url-token-param.md": {
        "disposition_by_category": {"webhook-url-token": "block", "api-key-token": "block"}
    },
    "redact-email.md": {"disposition_by_category": {"email-address": "redact"}},
    "redact-email-non-author-frontmatter-field.md": {
        "disposition_by_category": {"email-address": "redact"}
    },
    "clean-email-in-author-field.md": {"disposition_by_category": {}},
    "redact-internal-host.md": {
        "disposition_by_category": {"internal-hostname-private-ip": "redact"}
    },
    "redact-physical-address.md": {"disposition_by_category": {"physical-address": "redact"}},
    # Interim `redact`, not `not-evaluated` -- issue #2110. See the comment on
    # the roster-names finding in localcmd.py's screen_content: a disposition
    # SKILL.md §2 defines no consumer action for is a fail-open, so an
    # undecided candidate takes the ruleset's own Redact disposition until
    # Phase 1b (#2131) can tell attribution from access-control data.
    "dispatch-roster-names.md": {"disposition_by_category": {"roster-names": "redact"}},
    "dispatch-roster-names-two-pairs.md": {
        "disposition_by_category": {"roster-names": "redact"}
    },
    "clean-unrelated-roster-and-names.md": {"disposition_by_category": {}},
}

# The exact, complete message professor.py's pack-root guard emits -- not a
# substring match on the env var's name. A bare uncaught KeyError traceback
# (`KeyError: 'PROFESSOR_PACK_ROOT'`) would also satisfy a substring check on
# the variable name alone, which can't distinguish the designed fail-loud
# message from the exact "generic crash three steps later" anti-pattern this
# plan's step 1 explicitly forbade.
REQUIRED_UNSET_ERROR_TEXT = (
    "professor.py: $PROFESSOR_PACK_ROOT is not set. Every subcommand "
    "requires it to be set -- set $PROFESSOR_PACK_ROOT to this pack's root "
    "directory (the directory containing this `tools/` folder) before "
    "calling professor.py."
)

SUBCOMMAND_ARGS_FOR_UNSET_CHECK = {
    "resolve-pin": ["resolve-pin", "x/y", "main"],
    "path-exists-at": ["path-exists-at", "x/y", "a" * 40, "z"],
    "check-page": ["check-page", "x.md", "--target", "/tmp"],
    "screen-content": ["screen-content", "x.md"],
}


def _run_professor(
    args: list[str],
    *,
    pack_root: str | None,
    cwd: str | None = None,
    path_prepend: str | None = None,
    path_override: str | None = None,
):
    env = dict(os.environ)
    if pack_root is None:
        env["PROFESSOR_PACK_ROOT"] = ""
    else:
        env["PROFESSOR_PACK_ROOT"] = pack_root
    if path_override is not None:
        # Replaces PATH outright rather than prepending, so `gh`/`git` genuinely
        # cannot be found -- the missing-binary case issue #2112 is about.
        env["PATH"] = path_override
    elif path_prepend is not None:
        env["PATH"] = path_prepend + os.pathsep + env.get("PATH", "")
    return subprocess.run(
        [str(PROFESSOR_PY), *args],
        capture_output=True,
        text=True,
        env=env,
        cwd=cwd,
        timeout=60,
    )


def check_pack_root_unset_fails_loud() -> str | None:
    for name, args in SUBCOMMAND_ARGS_FOR_UNSET_CHECK.items():
        result = _run_professor(args, pack_root=None)
        if result.returncode == 0:
            return f"{name}: expected non-zero exit with $PROFESSOR_PACK_ROOT unset, got 0"
        if result.stderr.strip() != REQUIRED_UNSET_ERROR_TEXT:
            return (
                f"{name}: error message did not match the exact required text "
                f"{REQUIRED_UNSET_ERROR_TEXT!r}: got {result.stderr!r}"
            )
    return None


def check_pack_root_resolution_outside_checkout() -> str | None:
    """At least one call from a cwd outside this fork's checkout, with
    $PROFESSOR_PACK_ROOT set to an arbitrary path -- Phase 1's own review gate
    requires this explicitly, not just "works from inside block/buzz".
    """
    with tempfile.TemporaryDirectory() as outside_cwd:
        result = _run_professor(
            ["resolve-pin", EXTERNAL_REPO, EXTERNAL_REF],
            pack_root="/tmp/an-arbitrary-pack-root-that-need-not-exist",
            cwd=outside_cwd,
        )
        if result.returncode != 0:
            return f"resolve-pin from outside checkout failed: {result.stderr}"
        try:
            report = json.loads(result.stdout)
        except json.JSONDecodeError:
            return f"resolve-pin from outside checkout did not return valid JSON: {result.stdout!r}"
        sha = report.get("commit", "")
        if len(sha) != 40 or any(c not in "0123456789abcdef" for c in sha):
            return f"resolve-pin from outside checkout did not return a 40-char SHA: {sha!r}"
        return None


def check_pack_root_spec_validation() -> str | None:
    """`check-page`/`screen-content` must genuinely confirm `pack_root` points
    at a real Professor pack installation -- reading
    `<pack_root>/tools/contract/{page-contract,sensitive-patterns}.md` at the
    start of the call -- rather than accepting any non-empty string (step 4
    of the 2026-09-06 fix round). A `pack_root` missing the relevant spec
    file must fail with a specific, clear error naming the missing file,
    distinct from the "unset" error `check_pack_root_unset_fails_loud`
    covers; a real, valid pack root (this worktree's own the-professor/)
    must keep working exactly as before.
    """
    with tempfile.TemporaryDirectory() as bad_pack_root:
        check_page_result = _run_professor(
            ["check-page", str(FIXTURES_DIR / "clean.md"), "--target", str(REPO_ROOT)],
            pack_root=bad_pack_root,
        )
        if check_page_result.returncode == 0:
            return f"check-page with pack_root missing page-contract.md ({bad_pack_root}): expected non-zero exit, got 0"
        if REQUIRED_UNSET_ERROR_TEXT in check_page_result.stderr:
            return (
                "check-page with pack_root missing page-contract.md: got the "
                "$PROFESSOR_PACK_ROOT-unset error text instead of a distinct "
                f"missing-spec-file error: {check_page_result.stderr!r}"
            )
        if "page-contract.md" not in check_page_result.stderr:
            return (
                "check-page with pack_root missing page-contract.md: expected "
                f"an error naming the missing file, got {check_page_result.stderr!r}"
            )

        screen_content_result = _run_professor(
            ["screen-content", str(FIXTURES_DIR / "clean.md")],
            pack_root=bad_pack_root,
        )
        if screen_content_result.returncode == 0:
            return f"screen-content with pack_root missing sensitive-patterns.md ({bad_pack_root}): expected non-zero exit, got 0"
        if REQUIRED_UNSET_ERROR_TEXT in screen_content_result.stderr:
            return (
                "screen-content with pack_root missing sensitive-patterns.md: got "
                "the $PROFESSOR_PACK_ROOT-unset error text instead of a distinct "
                f"missing-spec-file error: {screen_content_result.stderr!r}"
            )
        if "sensitive-patterns.md" not in screen_content_result.stderr:
            return (
                "screen-content with pack_root missing sensitive-patterns.md: "
                f"expected an error naming the missing file, got {screen_content_result.stderr!r}"
            )

    valid_check_page = _run_professor(
        ["check-page", str(FIXTURES_DIR / "clean.md"), "--target", str(REPO_ROOT)],
        pack_root=str(PACK_ROOT),
    )
    if valid_check_page.returncode != 0:
        return f"check-page with a real, valid pack_root failed unexpectedly: {valid_check_page.stderr}"

    valid_screen_content = _run_professor(
        ["screen-content", str(FIXTURES_DIR / "clean.md")], pack_root=str(PACK_ROOT)
    )
    if valid_screen_content.returncode != 0:
        return f"screen-content with a real, valid pack_root failed unexpectedly: {valid_screen_content.stderr}"

    return None


def check_resolve_pin_matches_git_ls_remote() -> tuple[str | None, str | None]:
    """Returns (error_or_None, resolved_sha_or_None)."""
    result = _run_professor(
        ["resolve-pin", EXTERNAL_REPO, EXTERNAL_REF], pack_root="/tmp"
    )
    if result.returncode != 0:
        return f"resolve-pin failed: {result.stderr}", None
    try:
        report = json.loads(result.stdout)
    except json.JSONDecodeError:
        return f"resolve-pin did not print valid JSON: {result.stdout!r}", None
    for field in ("commit", "commit_author", "commit_at", "pr"):
        if field not in report:
            return f"resolve-pin's JSON is missing required field {field!r}: {report!r}", None
    sha = report["commit"]
    if len(sha) != 40 or any(c not in "0123456789abcdef" for c in sha):
        return f"resolve-pin did not return a 40-char hex SHA: {sha!r}", None

    ls_remote = subprocess.run(
        ["git", "ls-remote", f"https://github.com/{EXTERNAL_REPO}", EXTERNAL_REF],
        capture_output=True,
        text=True,
        timeout=30,
    )
    if ls_remote.returncode != 0:
        return f"git ls-remote failed: {ls_remote.stderr}", None
    remote_sha = ls_remote.stdout.split()[0] if ls_remote.stdout.split() else ""
    if sha != remote_sha:
        return (
            f"resolve-pin's SHA {sha!r} does not match git ls-remote's {remote_sha!r}",
            None,
        )
    return None, sha


# A real block/buzz commit whose message subject carries a trailing "(#NNNN)"
# (a normal squash-merge commit) -- confirms `pr` is the correct integer, not
# just present. Fixed rather than always re-reading `main`'s current HEAD, so
# this assertion doesn't silently start failing the day `main`'s tip happens
# to be a non-squash-merge commit.
PR_PRESENT_COMMIT = "b0466ac465336cb773fbf7355ec05f7d61f4a3aa"  # "...(#6456)"
PR_PRESENT_EXPECTED_PR = 6456

# block/buzz's own root commit ("Initial commit") -- predates the repo having
# any pull requests at all, so its message can never carry a trailing
# "(#NNNN)". Confirms `pr` is JSON `null`, not merely absent or guessed.
PR_ABSENT_COMMIT = "916f096fe9a12d493d156eb45719c5fd01d14287"


def check_resolve_pin_pr_field() -> str | None:
    """`pr` must be the correct integer when the cited commit's message
    subject carries a trailing "(#NNNN)", and JSON `null` -- never inferred
    by a separate network call -- when it does not.
    """
    present_result = _run_professor(
        ["resolve-pin", EXTERNAL_REPO, PR_PRESENT_COMMIT], pack_root="/tmp"
    )
    if present_result.returncode != 0:
        return f"resolve-pin({PR_PRESENT_COMMIT}) failed: {present_result.stderr}"
    try:
        present_report = json.loads(present_result.stdout)
    except json.JSONDecodeError:
        return f"resolve-pin({PR_PRESENT_COMMIT}) did not print valid JSON: {present_result.stdout!r}"
    if present_report.get("pr") != PR_PRESENT_EXPECTED_PR:
        return (
            f"resolve-pin({PR_PRESENT_COMMIT}): expected pr={PR_PRESENT_EXPECTED_PR}, "
            f"got {present_report.get('pr')!r}"
        )

    absent_result = _run_professor(
        ["resolve-pin", EXTERNAL_REPO, PR_ABSENT_COMMIT], pack_root="/tmp"
    )
    if absent_result.returncode != 0:
        return f"resolve-pin({PR_ABSENT_COMMIT}) failed: {absent_result.stderr}"
    try:
        absent_report = json.loads(absent_result.stdout)
    except json.JSONDecodeError:
        return f"resolve-pin({PR_ABSENT_COMMIT}) did not print valid JSON: {absent_result.stdout!r}"
    if absent_report.get("pr") is not None:
        return (
            f"resolve-pin({PR_ABSENT_COMMIT}): expected pr=null, got "
            f"{absent_report.get('pr')!r}"
        )
    return None


def check_path_exists_at_true_and_false(sha: str) -> str | None:
    true_result = _run_professor(
        ["path-exists-at", EXTERNAL_REPO, sha, EXTERNAL_EXISTING_PATH],
        pack_root="/tmp",
    )
    if true_result.returncode != 0 or true_result.stdout.strip() != "true":
        return f"path-exists-at(real path) did not return true: {true_result.stdout!r} {true_result.stderr!r}"

    false_result = _run_professor(
        ["path-exists-at", EXTERNAL_REPO, sha, EXTERNAL_MISSING_PATH],
        pack_root="/tmp",
    )
    if false_result.returncode != 0 or false_result.stdout.strip() != "false":
        return f"path-exists-at(fabricated path) did not return false: {false_result.stdout!r} {false_result.stderr!r}"

    return None


def check_uppercase_sha_is_accepted(sha: str) -> str | None:
    """An uppercase-hex commit SHA must resolve identically to its lowercase
    form (issue #2105), not be rejected as malformed.

    Both answers are asserted, not just the `true` one: a validation bug that
    accepted uppercase but then passed the un-normalized value through could
    still produce a wrong `false`, which would look like a citation defect
    rather than a tool defect.
    """
    upper = sha.upper()
    if upper == sha:
        return f"test setup error: {sha!r} has no uppercase form to test with"

    true_result = _run_professor(
        ["path-exists-at", EXTERNAL_REPO, upper, EXTERNAL_EXISTING_PATH],
        pack_root="/tmp",
    )
    if true_result.returncode != 0 or true_result.stdout.strip() != "true":
        return (
            "path-exists-at(uppercase SHA, real path) did not return true: "
            f"{true_result.stdout!r} {true_result.stderr!r}"
        )

    false_result = _run_professor(
        ["path-exists-at", EXTERNAL_REPO, upper, EXTERNAL_MISSING_PATH],
        pack_root="/tmp",
    )
    if false_result.returncode != 0 or false_result.stdout.strip() != "false":
        return (
            "path-exists-at(uppercase SHA, fabricated path) did not return false: "
            f"{false_result.stdout!r} {false_result.stderr!r}"
        )

    return None


def check_missing_binary_is_structured_not_traceback() -> str | None:
    """A missing `gh` or `git` binary must produce a structured error naming the
    binary, never a raw `FileNotFoundError` traceback (issue #2112).

    Both halves of the tool layer are exercised, because they shell out to
    different binaries through the same helper: `path-exists-at` needs `gh`,
    and `check-page` on a local citation needs `git`. Asserting the absence of
    "Traceback" is the point of the check -- an exit code alone cannot
    distinguish a handled error from an unhandled crash, since both are
    non-zero.
    """
    # PATH cannot simply be emptied: professor.py's shebang is
    # `#!/usr/bin/env -S uv run --script`, so wiping PATH kills `uv` before
    # Python starts and the run fails for the wrong reason. Instead PATH is
    # narrowed to a directory holding nothing but a symlink to `uv` -- the
    # interpreter resolves, `gh` and `git` genuinely do not.
    uv_path = shutil.which("uv")
    if uv_path is None:
        return "test setup error: `uv` not on PATH, cannot construct a gh/git-free PATH"

    with tempfile.TemporaryDirectory() as empty_bin:
        os.symlink(uv_path, os.path.join(empty_bin, "uv"))
        if shutil.which("gh", path=empty_bin) or shutil.which("git", path=empty_bin):
            return "test setup error: gh/git still resolvable on the narrowed PATH"

        gh_result = _run_professor(
            [
                "path-exists-at",
                EXTERNAL_REPO,
                "0" * 40,
                EXTERNAL_EXISTING_PATH,
            ],
            pack_root="/tmp",
            path_override=empty_bin,
        )
        if gh_result.returncode == 0:
            return "path-exists-at with no `gh` on PATH unexpectedly succeeded"
        if "Traceback" in gh_result.stderr:
            return (
                "path-exists-at with no `gh` on PATH produced a raw traceback: "
                f"{gh_result.stderr!r}"
            )
        if "not installed or not on PATH" not in gh_result.stderr:
            return (
                "path-exists-at with no `gh` on PATH did not name the missing "
                f"binary: {gh_result.stderr!r}"
            )

        page_result = _run_professor(
            [
                "check-page",
                str(FIXTURES_DIR / "compliant-local.md"),
                "--target",
                str(REPO_ROOT),
            ],
            pack_root=str(PACK_ROOT),
            path_override=empty_bin,
        )
        if "Traceback" in page_result.stderr:
            return (
                "check-page with no `git` on PATH produced a raw traceback: "
                f"{page_result.stderr!r}"
            )

    return None


def check_citation_check_error_on_api_failure() -> str | None:
    """A rate-limited/auth-failed `gh api` response must produce a distinct
    `citation-check-error` finding, never the same `citation-not-found` outcome
    a genuine 404 produces -- step 1 of the 2026-09-05 fix round guards
    against exactly this regression: an error collapsed into "doesn't exist".
    """
    with tempfile.TemporaryDirectory() as decoy_dir:
        decoy_path = Path(decoy_dir)
        gh_script = decoy_path / "gh"
        gh_script.write_text(
            "#!/bin/sh\n"
            'echo \'{"status": "403", "message": "API rate limit exceeded for user"}\'\n'
            "exit 1\n"
        )
        gh_script.chmod(gh_script.stat().st_mode | 0o111)

        fixture_path = FIXTURES_DIR / "compliant-external.md"
        result = _run_professor(
            ["check-page", str(fixture_path), "--target", str(REPO_ROOT)],
            pack_root=str(PACK_ROOT),
            path_prepend=str(decoy_path),
        )
        if result.returncode != 0:
            return f"check-page(compliant-external.md, decoy 403 gh) failed: {result.stderr}"
        try:
            report = json.loads(result.stdout)
        except json.JSONDecodeError:
            return (
                "check-page(compliant-external.md, decoy 403 gh) did not print "
                f"valid JSON: {result.stdout!r}"
            )
        rules = [f["rule"] for f in report.get("findings", [])]
        if "citation-not-found" in rules:
            return (
                "check-page(compliant-external.md, decoy 403 gh): a rate-limit-"
                f"shaped API failure was misreported as citation-not-found: {rules!r}"
            )
        raw_citation = "block/buzz:Cargo.toml@f038cbbb0d4092a72ffd93f17916f84d2b39bb43"
        for finding in report.get("findings", []):
            if finding.get("rule") == "citation-check-error" and raw_citation in finding.get(
                "message", ""
            ):
                return (
                    "check-page(compliant-external.md, decoy 403 gh): "
                    "citation-check-error message quotes the raw citation "
                    f"string verbatim: {finding['message']!r}"
                )
        if "citation-check-error" not in rules:
            return (
                "check-page(compliant-external.md, decoy 403 gh): expected a "
                f"citation-check-error finding naming the API failure, got {rules!r}"
            )
    return None


def check_local_citation_error_shapes() -> str | None:
    """Three distinct "could not verify" shapes for a *local* citation must
    never collapse into `citation-not-found` -- step 4 of the 2026-09-05 fix
    round, the local-side counterpart to `check_citation_check_error_on_api_
    failure` above (which already covers the network side). Uses
    `local-citation-error-shapes.md`, checked only against deliberately
    broken `--target` directories, never against this pack's own real repo.
    `broken-nonexistent-citation.md` (checked elsewhere, via
    `check_check_page_fixtures`) confirms a genuine confirmed-absent local
    citation still produces `citation-not-found` unaffected by this change.
    """
    fixture_path = FIXTURES_DIR / "local-citation-error-shapes.md"

    def _rules_for(target_dir: str):
        result = _run_professor(
            ["check-page", str(fixture_path), "--target", target_dir], pack_root=str(PACK_ROOT)
        )
        if result.returncode != 0:
            return None, f"check-page against --target {target_dir!r} failed: {result.stderr}"
        try:
            report = json.loads(result.stdout)
        except json.JSONDecodeError:
            return (
                None,
                f"check-page against --target {target_dir!r} did not print valid "
                f"JSON: {result.stdout!r}",
            )
        return [f["rule"] for f in report.get("findings", [])], None

    # Case 1: --target points at a path that doesn't exist at all.
    nonexistent_target = f"/tmp/professor-check-nonexistent-target-{os.getpid()}"
    rules, error = _rules_for(nonexistent_target)
    if error:
        return error
    if rules != ["citation-check-error"]:
        return (
            "--target pointing at a nonexistent path: expected "
            f"['citation-check-error'], got {rules!r}"
        )

    # Case 2: --target is an empty, non-git directory.
    with tempfile.TemporaryDirectory() as nongit_dir:
        rules, error = _rules_for(nongit_dir)
        if error:
            return error
        if rules != ["citation-check-error"]:
            return (
                "--target an empty non-git directory: expected "
                f"['citation-check-error'], got {rules!r}"
            )

    # Case 3: --target is a real, empty git repo with no matching history --
    # the commit the fixture cites was never committed there at all.
    with tempfile.TemporaryDirectory() as emptygit_dir:
        init_result = subprocess.run(
            ["git", "init", "-q", emptygit_dir], capture_output=True, text=True, timeout=15
        )
        if init_result.returncode != 0:
            return f"could not git init a scratch repo for the empty-git-repo case: {init_result.stderr}"
        rules, error = _rules_for(emptygit_dir)
        if error:
            return error
        if rules != ["citation-check-error"]:
            return (
                "--target an empty git repo with no matching history: expected "
                f"['citation-check-error'], got {rules!r}"
            )

    return None


def check_invalid_utf8_produces_structured_error() -> str | None:
    """Invalid UTF-8 input used to raise an uncaught UnicodeDecodeError
    traceback instead of a structured tool error, inconsistent with this
    module's own convention elsewhere (e.g. "check-page: no such file:
    ...") -- step 11 of the 2026-09-05 fix round. `invalid-utf8.md` is a
    real fixture containing a raw 0xFF byte, deliberately not registered in
    CHECK_PAGE_EXPECTED_RULES/SCREEN_CONTENT_EXPECTED above: it can never
    produce a findings JSON body at all, only a structured error and a
    non-zero exit.
    """
    fixture_path = FIXTURES_DIR / "invalid-utf8.md"

    check_page_result = _run_professor(
        ["check-page", str(fixture_path), "--target", str(REPO_ROOT)], pack_root=str(PACK_ROOT)
    )
    if check_page_result.returncode == 0:
        return "check-page(invalid-utf8.md): expected non-zero exit, got 0"
    if "Traceback" in check_page_result.stderr:
        return (
            "check-page(invalid-utf8.md): got a raw traceback instead of a "
            f"structured error: {check_page_result.stderr!r}"
        )
    if "not valid UTF-8" not in check_page_result.stderr:
        return (
            "check-page(invalid-utf8.md): expected a structured 'not valid "
            f"UTF-8' error, got {check_page_result.stderr!r}"
        )

    screen_content_result = _run_professor(
        ["screen-content", str(fixture_path)], pack_root=str(PACK_ROOT)
    )
    if screen_content_result.returncode == 0:
        return "screen-content(invalid-utf8.md): expected non-zero exit, got 0"
    if "Traceback" in screen_content_result.stderr:
        return (
            "screen-content(invalid-utf8.md): got a raw traceback instead of a "
            f"structured error: {screen_content_result.stderr!r}"
        )
    if "not valid UTF-8" not in screen_content_result.stderr:
        return (
            "screen-content(invalid-utf8.md): expected a structured 'not valid "
            f"UTF-8' error, got {screen_content_result.stderr!r}"
        )

    return None


def check_screen_content_accepts_target_flag() -> str | None:
    """`professor.py`'s `screen-content` subparser never defined `--target`,
    but `skills/screen-sensitive/SKILL.md` documents invoking it as
    `professor.py screen-content <scratch-file> --target <target-root>` --
    confirmed failing with "error: unrecognized arguments: --target /tmp"
    before this fix (bonus item found during adjudication, treated as High:
    the mandatory screening gate couldn't be invoked as documented at all).
    Only checks that the documented shape now parses against a target with
    no override present; `check_screen_content_target_ruleset_override`
    below covers the override-detection behaviour itself (step 3 of the
    2026-09-06 fix round).
    """
    with tempfile.TemporaryDirectory() as target_dir:
        result = _run_professor(
            ["screen-content", str(FIXTURES_DIR / "clean.md"), "--target", target_dir],
            pack_root=str(PACK_ROOT),
        )
        if result.returncode != 0:
            return (
                "screen-content <file> --target <dir> failed to parse/run: "
                f"exit {result.returncode}, stderr {result.stderr!r}"
            )
    return None


def check_screen_content_target_ruleset_override() -> str | None:
    """`skills/screen-sensitive/SKILL.md` promises a two-step ruleset
    resolution order: `<target>/.professor/sensitive-patterns.md` if it
    exists, else the bundled default. `screen_content` can't actually
    interpret a target's override content (its categories are hardcoded
    Python), so it must report an explicit `target-ruleset-override`
    (`block`) finding instead of silently screening against the bundled
    default -- step 3 of the 2026-09-06 fix round, changed from
    `not_evaluated` to `block` (fail closed) in step 2 of the 2026-09-06
    round: `not_evaluated` had no defined consumer action, and the
    nearest-sounding outcome in the invoking skill's own procedure was
    "pass", which meant an overridden target's draft was effectively
    screened not at all. A target with NO override (or no `--target` at
    all) must still produce the normal bundled-default result, unchanged.
    """
    with tempfile.TemporaryDirectory() as override_target:
        (Path(override_target) / ".professor").mkdir()
        (Path(override_target) / ".professor" / "sensitive-patterns.md").write_text(
            "# a target-specific override\n"
        )
        result = _run_professor(
            ["screen-content", str(FIXTURES_DIR / "clean.md"), "--target", override_target],
            pack_root=str(PACK_ROOT),
        )
        if result.returncode != 0:
            return f"screen-content(clean.md, override present) failed: {result.stderr}"
        try:
            report = json.loads(result.stdout)
        except json.JSONDecodeError:
            return f"screen-content(clean.md, override present) did not print valid JSON: {result.stdout!r}"
        findings = report.get("findings", [])
        if [f["category"] for f in findings] != ["target-ruleset-override"]:
            return (
                "screen-content(clean.md, override present): expected exactly one "
                f"'target-ruleset-override' finding, got {findings!r}"
            )
        if findings[0]["disposition"] != "block":
            return (
                "screen-content(clean.md, override present): expected disposition "
                f"'block', got {findings[0]['disposition']!r}"
            )

    with tempfile.TemporaryDirectory() as no_override_target:
        result = _run_professor(
            ["screen-content", str(FIXTURES_DIR / "clean.md"), "--target", no_override_target],
            pack_root=str(PACK_ROOT),
        )
        if result.returncode != 0:
            return f"screen-content(clean.md, no override) failed: {result.stderr}"
        try:
            report = json.loads(result.stdout)
        except json.JSONDecodeError:
            return f"screen-content(clean.md, no override) did not print valid JSON: {result.stdout!r}"
        if report.get("findings", []) != []:
            return (
                "screen-content(clean.md, no override): expected the normal "
                f"bundled-default (empty) result, got {report.get('findings')!r}"
            )
    return None


def check_local_citation_never_calls_gh() -> str | None:
    """`compliant-local.md`'s citation is entirely local (no `repo:` prefix) --
    `gh` must never be invoked for it. `compliant-external.md`'s citation
    names a genuinely external repo -- `gh` MUST be invoked for it. Both sides
    matter: a check that only asserted one side couldn't tell "always calls
    gh" and "never calls gh" apart from the correct, conditional behaviour
    this plan's own step 4 required (§4's local/external split).
    """
    real_gh = shutil.which("gh")
    if real_gh is None:
        return "no real `gh` found on PATH to build the passthrough decoy from"

    with tempfile.TemporaryDirectory() as decoy_dir:
        decoy_path = Path(decoy_dir)
        log_path = decoy_path / "gh-invocations.log"
        gh_script = decoy_path / "gh"
        gh_script.write_text(
            "#!/bin/sh\n"
            f'echo "invoked: $@" >> "{log_path}"\n'
            f'exec "{real_gh}" "$@"\n'
        )
        gh_script.chmod(gh_script.stat().st_mode | 0o111)

        local_fixture = FIXTURES_DIR / "compliant-local.md"
        local_result = _run_professor(
            ["check-page", str(local_fixture), "--target", str(REPO_ROOT)],
            pack_root=str(PACK_ROOT),
            path_prepend=str(decoy_path),
        )
        if local_result.returncode != 0:
            return (
                "check-page(compliant-local.md) with decoy gh on PATH failed: "
                f"{local_result.stderr}"
            )
        if log_path.exists():
            return (
                "check-page(compliant-local.md): gh was invoked for a purely "
                f"local citation -- log contents: {log_path.read_text()!r}"
            )

        external_fixture = FIXTURES_DIR / "compliant-external.md"
        external_result = _run_professor(
            ["check-page", str(external_fixture), "--target", str(REPO_ROOT)],
            pack_root=str(PACK_ROOT),
            path_prepend=str(decoy_path),
        )
        if external_result.returncode != 0:
            return (
                "check-page(compliant-external.md) with decoy gh on PATH failed: "
                f"{external_result.stderr}"
            )
        if not log_path.exists():
            return (
                "check-page(compliant-external.md): gh was never invoked for a "
                "genuinely external citation"
            )
    return None


# Fixtures whose citations name a repo other than `--target`, so `check-page`
# resolves them through `netcmd` and really does reach the GitHub API. They are
# excluded from `--offline` (issue #2111): with outbound HTTP blocked they
# report `citation-check-error` instead of their expected rules, which is the
# tool behaving correctly and the *check* being misclassified.
#
# Derived by hand and asserted below rather than detected at runtime -- a
# regex over fixture text would silently drop a fixture from the offline run
# the moment someone wrote a citation it did not anticipate.
EXTERNAL_CITATION_FIXTURES = {
    "compliant-external.md",
    "external-citation-range-not-evaluated.md",
    "broken-external-out-of-bounds-range.md",
}


def check_check_page_fixtures(offline: bool = False) -> str | None:
    # A shallow clone can be missing FIXTURE_PINNED_COMMIT even though it is
    # entirely real upstream -- any fixture citing it would then fail with
    # citation-check-error instead of its expected rule, misattributing a
    # missing-history problem to a code defect (step 5 of the 2026-09-06 fix
    # round). Checked once, upfront, rather than per-fixture inside the loop.
    pinned_commit_present = _commit_present_in_local_history(
        str(REPO_ROOT), FIXTURE_PINNED_COMMIT
    )
    unknown_external = EXTERNAL_CITATION_FIXTURES - set(CHECK_PAGE_EXPECTED_RULES)
    if unknown_external:
        return (
            "EXTERNAL_CITATION_FIXTURES names fixture(s) that are not in "
            f"CHECK_PAGE_EXPECTED_RULES: {sorted(unknown_external)!r} -- the "
            "offline exclusion list has drifted from the fixture set."
        )

    skipped = []
    skipped_external = []
    for fixture_name, expected_rules in CHECK_PAGE_EXPECTED_RULES.items():
        fixture_path = FIXTURES_DIR / fixture_name
        if offline and fixture_name in EXTERNAL_CITATION_FIXTURES:
            skipped_external.append(fixture_name)
            continue
        if not pinned_commit_present and FIXTURE_PINNED_COMMIT in fixture_path.read_text():
            skipped.append(fixture_name)
            continue
        result = _run_professor(
            ["check-page", str(fixture_path), "--target", str(REPO_ROOT)], pack_root=str(PACK_ROOT)
        )
        if result.returncode != 0:
            return f"check-page({fixture_name}) failed: {result.stderr}"
        try:
            report = json.loads(result.stdout)
        except json.JSONDecodeError:
            return f"check-page({fixture_name}) did not print valid JSON: {result.stdout!r}"
        actual_rules = [f["rule"] for f in report.get("findings", [])]
        if actual_rules != expected_rules:
            return (
                f"check-page({fixture_name}): expected rules {expected_rules!r}, "
                f"got {actual_rules!r}"
            )
    if skipped:
        print(
            f"skipped: fixture commit {FIXTURE_PINNED_COMMIT} not present in this "
            f"shallow clone -- {len(skipped)} fixture(s) skipped: {sorted(skipped)!r}"
        )
    if skipped_external:
        print(
            "skipped: --offline -- external-citation fixture(s) not run "
            f"(they reach the GitHub API): {sorted(skipped_external)!r}"
        )
    return None


def check_frontmatter_branches_are_distinct() -> str | None:
    """All four of `_parse_frontmatter`'s failure branches share the
    "frontmatter" rule label -- this asserts each dedicated fixture's actual
    message names the specific branch it targets, so the four don't collapse
    into one untested label.
    """
    for fixture_name, expected_substring in FRONTMATTER_BRANCH_EXPECTED_MESSAGE_SUBSTRING.items():
        fixture_path = FIXTURES_DIR / fixture_name
        result = _run_professor(
            ["check-page", str(fixture_path), "--target", str(REPO_ROOT)], pack_root=str(PACK_ROOT)
        )
        if result.returncode != 0:
            return f"check-page({fixture_name}) failed: {result.stderr}"
        try:
            report = json.loads(result.stdout)
        except json.JSONDecodeError:
            return f"check-page({fixture_name}) did not print valid JSON: {result.stdout!r}"
        findings = report.get("findings", [])
        if len(findings) != 1:
            return f"check-page({fixture_name}): expected exactly one finding, got {findings!r}"
        message = findings[0].get("message", "")
        if expected_substring not in message:
            return (
                f"check-page({fixture_name}): expected message to contain "
                f"{expected_substring!r}, got {message!r}"
            )
    return None


def check_screen_content_fixtures() -> str | None:
    for fixture_name, expectation in SCREEN_CONTENT_EXPECTED.items():
        fixture_path = FIXTURES_DIR / fixture_name
        result = _run_professor(["screen-content", str(fixture_path)], pack_root=str(PACK_ROOT))
        if result.returncode != 0:
            return f"screen-content({fixture_name}) failed: {result.stderr}"
        try:
            report = json.loads(result.stdout)
        except json.JSONDecodeError:
            return f"screen-content({fixture_name}) did not print valid JSON: {result.stdout!r}"

        findings = report.get("findings", [])
        expected_by_category = expectation["disposition_by_category"]

        # Exact-set comparison, matching check-page's own rigor: not just
        # "the expected categories are present" but "no unexpected/extra
        # category showed up either".
        actual_categories = {f["category"] for f in findings}
        expected_categories = set(expected_by_category.keys())
        if actual_categories != expected_categories:
            return (
                f"screen-content({fixture_name}): expected categories "
                f"{expected_categories!r}, got {actual_categories!r}"
            )

        # `match` must be `null` for EVERY finding, regardless of disposition
        # (step 4 of the 2026-09-06 fix round) -- an earlier round suppressed
        # it only for `block`, on the theory that only `block` findings
        # needed it, but a second independent review found the ordinary
        # `redact` case still printed the exact matched text. This sweeps
        # every fixture's every finding, not just one hand-picked case, since
        # `_screen_finding` is the single call site every category goes
        # through and a regression there would affect all of them at once.
        for finding in findings:
            if finding.get("match") is not None:
                return (
                    f"screen-content({fixture_name}): finding {finding!r} "
                    "leaked its matched span via a non-null 'match' field -- "
                    "every finding must report location and category only, "
                    "never the flagged content itself"
                )

        if not expected_by_category:
            continue

        for category, disposition in expected_by_category.items():
            matches = [f for f in findings if f["category"] == category]
            if not matches:
                return f"screen-content({fixture_name}): no {category!r} finding, got {findings!r}"
            for finding in matches:
                if finding["disposition"] != disposition:
                    return (
                        f"screen-content({fixture_name}): {category!r} finding had "
                        f"disposition {finding['disposition']!r}, expected {disposition!r}"
                    )
                if disposition == "redact" and finding["replacement"] != f"[REDACTED: {category}]":
                    return (
                        f"screen-content({fixture_name}): {category!r} finding's "
                        f"replacement was {finding['replacement']!r}, expected "
                        f"'[REDACTED: {category}]'"
                    )
    return None


def check_roster_names_multiple_candidates() -> str | None:
    """`_roster_names_matches` (renamed from the singular
    `_roster_names_first_match`, step 6 of the 2026-09-06 fix round) must
    enumerate every candidate name-list span co-occurring with a roster-
    context phrase, not just the first one found -- `dispatch-roster-
    names-two-pairs.md` has two separate roster-shaped name pairs in two
    different sentences (sections), each in its own window, far enough
    apart that neither pair's roster-context phrase falls within the other
    pair's window. `check_screen_content_fixtures`'s own category-set
    comparison can't distinguish "one roster-names finding" from "two" (a
    Python `set` collapses duplicates), so this is a dedicated count+location
    assertion, not folded into that generic sweep.
    """
    fixture_path = FIXTURES_DIR / "dispatch-roster-names-two-pairs.md"
    result = _run_professor(["screen-content", str(fixture_path)], pack_root=str(PACK_ROOT))
    if result.returncode != 0:
        return f"screen-content(dispatch-roster-names-two-pairs.md) failed: {result.stderr}"
    try:
        report = json.loads(result.stdout)
    except json.JSONDecodeError:
        return (
            "screen-content(dispatch-roster-names-two-pairs.md) did not print "
            f"valid JSON: {result.stdout!r}"
        )
    findings = report.get("findings", [])
    if len(findings) != 2:
        return (
            "screen-content(dispatch-roster-names-two-pairs.md): expected exactly "
            f"2 roster-names findings, got {len(findings)}: {findings!r}"
        )
    lines = [f["location"]["line"] for f in findings]
    if lines != [11, 16]:
        return (
            "screen-content(dispatch-roster-names-two-pairs.md): expected findings "
            f"at lines [11, 16] (verified against the fixture file with grep -n), "
            f"got {lines!r}"
        )
    return None


def check_roster_names_three_names_one_context() -> str | None:
    """`dispatch-roster-names.md` (the pre-existing fixture, three names --
    Alex Example, Jamie Example, Morgan Example -- in a single roster
    context) is only ever swept by `check_screen_content_fixtures`'s general
    category comparison, which collapses any number of `roster-names`
    findings down to the single category `roster-names` in a Python `set` --
    it cannot tell "one finding" from "three". `_roster_names_matches`
    enumerates one finding per candidate NAME, not one per roster context
    (step 10 of the 2026-09-06 fix round, closing the same gap
    `check_roster_names_multiple_candidates` above already closed for
    `dispatch-roster-names-two-pairs.md`, just left unchecked for this
    older, three-names-in-one-context fixture until now).
    """
    fixture_path = FIXTURES_DIR / "dispatch-roster-names.md"
    result = _run_professor(["screen-content", str(fixture_path)], pack_root=str(PACK_ROOT))
    if result.returncode != 0:
        return f"screen-content(dispatch-roster-names.md) failed: {result.stderr}"
    try:
        report = json.loads(result.stdout)
    except json.JSONDecodeError:
        return f"screen-content(dispatch-roster-names.md) did not print valid JSON: {result.stdout!r}"
    findings = report.get("findings", [])
    if len(findings) != 3:
        return (
            "screen-content(dispatch-roster-names.md): expected exactly 3 "
            f"roster-names findings (one per name), got {len(findings)}: {findings!r}"
        )
    return None


def check_password_literal_three_shapes() -> str | None:
    """`block-password-literal.md` exercises PASSWORD_LITERAL_RE for real
    (step 2 of the 2026-09-06 fix round) -- until now, zero fixtures touched
    this regex at all; `block-connection-string.md` only ever exercised
    CONNECTION_STRING_RE. Three distinct shapes on three distinct lines: a
    plain unquoted literal (`password: hunter2`), a JSON-quoted value
    (`{"password": "hunter2"}`), and an underscore-separated keyword
    (`DB_PASSWORD=hunter2`, step 1's own fix). `check_screen_content_fixtures`'s
    category-set comparison can't distinguish "this regex fired once" from
    "it fired on all three shapes" (a `set` collapses the category either
    way), so this is a dedicated count+location assertion, same reasoning as
    `check_roster_names_multiple_candidates` above. In particular, reverting
    step 1's underscore-boundary fix alone still leaves the first two shapes
    matching (both already sit next to a non-word character), so a bare
    category check would not catch that regression -- only the count would.
    """
    fixture_path = FIXTURES_DIR / "block-password-literal.md"
    result = _run_professor(["screen-content", str(fixture_path)], pack_root=str(PACK_ROOT))
    if result.returncode != 0:
        return f"screen-content(block-password-literal.md) failed: {result.stderr}"
    try:
        report = json.loads(result.stdout)
    except json.JSONDecodeError:
        return f"screen-content(block-password-literal.md) did not print valid JSON: {result.stdout!r}"
    findings = report.get("findings", [])
    if len(findings) != 3:
        return (
            "screen-content(block-password-literal.md): expected exactly 3 "
            f"connection-string findings (one per shape), got {len(findings)}: "
            f"{findings!r}"
        )
    if any(f["category"] != "connection-string" for f in findings):
        return (
            "screen-content(block-password-literal.md): expected every finding's "
            f"category to be 'connection-string', got {[f['category'] for f in findings]!r}"
        )
    lines = [f["location"]["line"] for f in findings]
    if lines != [11, 12, 13]:
        return (
            "screen-content(block-password-literal.md): expected findings at "
            f"lines [11, 12, 13] (verified against the fixture file with grep -n), "
            f"got {lines!r}"
        )
    return None


# For each fixture, the exact substrings its check-page findings' messages
# must never contain: the flagged sentence's own raw prose (minus its inline
# tag), and/or the raw citation string as literally typed in the fixture's
# `(behaviour: ...)` tag (step 5 of the 2026-09-06 fix round). This is a
# regression check on the prior round's own "never quote flagged content"
# fix (406b87c10/ddbcdc2e2) -- it does not re-derive the forbidden text from
# the fixture file at runtime, since the point is to assert the LITERAL
# strings the adjudication named, not whatever the fixture happens to say
# today.
MESSAGE_LEAK_FORBIDDEN_SUBSTRINGS = {
    # missing-citation (the "(behaviour: none)" branch)
    "broken-missing-citation.md": [
        "resolve_pin` always retries a rate-limited call up to three times before giving up",
    ],
    # missing-citation (the unparseable-citation branch specifically)
    "broken-unparseable-citation.md": [
        "resolve_pin` always retries a rate-limited call up to three times before giving up",
        "this is not a citation at all",
    ],
    # mixed-claim
    "broken-mixed-claim.md": [
        "This retry logic should really be replaced with exponential backoff",
        "launchpad/agents/the-professor/tools/server.py@c552723895f5bfbf399db7e3135a22026597e70a#L144-L201",
    ],
    # citation-not-found
    "broken-nonexistent-citation.md": [
        "launchpad/agents/the-professor/tools/this-file-does-not-exist.py@c552723895f5bfbf399db7e3135a22026597e70a",
    ],
    # out-of-bounds-range (local)
    "broken-out-of-bounds-range.md": [
        "launchpad/agents/the-professor/tools/server.py@c552723895f5bfbf399db7e3135a22026597e70a#L520-L522",
    ],
    # citation-range-not-evaluated (external)
    "external-citation-range-not-evaluated.md": [
        "block/buzz:Cargo.toml@f038cbbb0d4092a72ffd93f17916f84d2b39bb43#L1-L5",
    ],
}


def check_page_messages_never_leak_raw_content() -> str | None:
    """check-page's messages must never contain the flagged sentence's raw
    text or the raw citation string, across every fixture that exercises one
    of these message-construction paths: missing-citation, mixed-claim,
    citation-not-found, out-of-bounds-range, and citation-range-not-
    evaluated (this function), plus citation-check-error (asserted inside
    `check_citation_check_error_on_api_failure`, which already runs
    compliant-external.md through a decoy `gh` and has the report in hand).
    `broken-unparseable-citation.md` is a new fixture (step 5 of the
    2026-09-06 fix round): no existing fixture exercised
    `_parse_citation_string` returning `None` for a citation that is present
    but doesn't parse, as opposed to `(behaviour: none)`'s "no citation at
    all" branch -- both share the "missing-citation" rule label but are two
    distinct call sites in `_check_section`.
    """
    for fixture_name, forbidden_substrings in MESSAGE_LEAK_FORBIDDEN_SUBSTRINGS.items():
        fixture_path = FIXTURES_DIR / fixture_name
        result = _run_professor(
            ["check-page", str(fixture_path), "--target", str(REPO_ROOT)], pack_root=str(PACK_ROOT)
        )
        if result.returncode != 0:
            return f"check-page({fixture_name}) failed: {result.stderr}"
        try:
            report = json.loads(result.stdout)
        except json.JSONDecodeError:
            return f"check-page({fixture_name}) did not print valid JSON: {result.stdout!r}"
        findings = report.get("findings", [])
        if not findings:
            return f"check-page({fixture_name}): expected at least one finding, got none"
        all_messages = " ".join(f.get("message", "") for f in findings)
        for forbidden in forbidden_substrings:
            if forbidden in all_messages:
                return (
                    f"check-page({fixture_name}): a message leaked forbidden raw "
                    f"content {forbidden!r} -- findings: {findings!r}"
                )
    return None


def _run_network_free_checks(offline: bool) -> int:
    """Every check that reaches no network and needs no `gh` credentials.

    These are the checks CI can run (issue #2111). "Network-free" here means no
    call leaves the machine: several of them still exercise the `gh` code path,
    but through a decoy `gh` placed on PATH (`check_citation_check_error_on_api_failure`,
    `check_local_citation_never_calls_gh`) or with no `gh` at all
    (`check_missing_binary_is_structured_not_traceback`). Local `git` against
    this checkout is likewise not network.

    The shallow-clone check is deliberately in this half: it reads only this
    checkout's own local history.
    """
    error, shallow_clone = check_fixture_commit_shallow_clone_safety()
    if error:
        print(f"FAIL [fixture commit shallow-clone safety]: {error}")
        return 1
    if shallow_clone:
        print(
            "skip: fixture commit shallow-clone safety -- "
            f"{FIXTURE_PINNED_COMMIT} not present in this checkout's local "
            "history (a genuinely shallow clone); dependent check-page "
            "fixtures are skipped below rather than failed"
        )
    else:
        print(
            "ok: fixture commit shallow-clone safety (present here; fabricated "
            "SHA correctly absent)"
        )

    checks: list[tuple[str, object]] = [
        ("pack-root unset fails loud (all four subcommands)", check_pack_root_unset_fails_loud),
        ("pack-root spec validation (check-page/screen-content)", check_pack_root_spec_validation),
        (
            "a missing gh/git binary is a structured error, never a raw traceback",
            check_missing_binary_is_structured_not_traceback,
        ),
        (
            "citation-check-error on API failure (not collapsed into citation-not-found)",
            check_citation_check_error_on_api_failure,
        ),
        (
            "local-citation error shapes (nonexistent --target, non-git --target, "
            "empty git repo all citation-check-error, never citation-not-found)",
            check_local_citation_error_shapes,
        ),
        (
            "local-vs-network boundary (compliant-local.md never calls gh, "
            "compliant-external.md does)",
            check_local_citation_never_calls_gh,
        ),
        (
            "invalid UTF-8 produces a structured error, never a raw traceback "
            "(check-page and screen-content)",
            check_invalid_utf8_produces_structured_error,
        ),
        (
            "screen-content accepts --target, matching SKILL.md's documented "
            "invocation shape",
            check_screen_content_accepts_target_flag,
        ),
        (
            "screen-content reports an explicit target-ruleset-override, never "
            "silently bundled-default",
            check_screen_content_target_ruleset_override,
        ),
        (
            "check-page fixtures ("
            f"{len(CHECK_PAGE_EXPECTED_RULES) - (len(EXTERNAL_CITATION_FIXTURES) if offline else 0)}"
            " fixtures)",
            lambda: check_check_page_fixtures(offline=offline),
        ),
        (
            "frontmatter branches distinct "
            f"({len(FRONTMATTER_BRANCH_EXPECTED_MESSAGE_SUBSTRING)} branches)",
            check_frontmatter_branches_are_distinct,
        ),
        (
            f"screen-content fixtures ({len(SCREEN_CONTENT_EXPECTED)} fixtures)",
            check_screen_content_fixtures,
        ),
        (
            "roster-names enumerates every candidate, not just the first "
            "(2 distinct findings)",
            check_roster_names_multiple_candidates,
        ),
        (
            "dispatch-roster-names.md's three names each produce their own finding "
            "(3 distinct findings)",
            check_roster_names_three_names_one_context,
        ),
        (
            "PASSWORD_LITERAL_RE fires on all three shapes (unquoted, JSON-quoted, "
            "underscore-separated)",
            check_password_literal_three_shapes,
        ),
        (
            "check-page messages never leak the flagged sentence's raw text or the "
            "raw citation string (missing-citation, unparseable-citation, "
            "mixed-claim, citation-not-found, out-of-bounds-range, "
            "citation-range-not-evaluated)",
            check_page_messages_never_leak_raw_content,
        ),
    ]

    for name, check in checks:
        error = check()
        if error:
            print(f"FAIL [{name}]: {error}")
            return 1
        print(f"ok: {name}")

    return 0


def _run_network_checks() -> int:
    """The checks that make real GitHub API calls and need `gh` authenticated.

    Kept out of `_run_network_free_checks` and skippable with `--offline`
    (issue #2111): CI has neither the credentials nor a reason to spend a rate
    limit on them, but they are the only checks that prove `resolve-pin` and
    `path-exists-at` actually work against GitHub, so they must still be run
    by hand or on a schedule -- never dropped.

    Written as a straight-line block rather than folded into the declarative
    list above because the SHA `resolve-pin` returns is threaded into three
    later checks; there is real state here, and hiding it in a registry would
    obscure that.
    """
    error = check_pack_root_resolution_outside_checkout()
    if error:
        print(f"FAIL [pack-root resolution from outside checkout]: {error}")
        return 1
    print("ok: pack-root resolution from outside checkout")

    error, sha = check_resolve_pin_matches_git_ls_remote()
    if error:
        print(f"FAIL [resolve-pin matches git ls-remote]: {error}")
        return 1
    print(f"ok: resolve-pin matches git ls-remote ({sha})")

    error = check_resolve_pin_pr_field()
    if error:
        print(f"FAIL [resolve-pin pr field]: {error}")
        return 1
    print("ok: resolve-pin's pr field (correct integer when present, null when absent)")

    error = check_path_exists_at_true_and_false(sha)
    if error:
        print(f"FAIL [path-exists-at true/false]: {error}")
        return 1
    print("ok: path-exists-at true/false")

    error = check_uppercase_sha_is_accepted(sha)
    if error:
        print(f"FAIL [uppercase SHA accepted]: {error}")
        return 1
    print("ok: an uppercase-hex SHA resolves identically to its lowercase form")

    return 0


def main() -> int:
    args = sys.argv[1:]
    offline = "--offline" in args
    unknown = [a for a in args if a != "--offline"]
    if unknown:
        print(
            f"check_professor.py: unrecognized argument(s) {unknown!r}. "
            "The only accepted flag is --offline (skip the GitHub-API checks).",
            file=sys.stderr,
        )
        return 2

    if _run_network_free_checks(offline) != 0:
        return 1

    if offline:
        # Named individually rather than counted, so a check silently moving out
        # of the network half cannot pass unnoticed as a smaller number.
        print(
            "skip: --offline -- not run: pack-root resolution from outside "
            "checkout, resolve-pin matches git ls-remote, resolve-pin's pr "
            "field, path-exists-at true/false, uppercase SHA accepted. These "
            "need an authenticated `gh` and reach the GitHub API; run "
            "check_professor.py with no flags to include them."
        )
        print("ALL NETWORK-FREE CHECKS PASSED")
        return 0

    if _run_network_checks() != 0:
        return 1

    print("ALL CHECKS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
