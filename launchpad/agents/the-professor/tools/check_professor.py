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

EXTERNAL_REPO = "block/buzz"
EXTERNAL_REF = "main"
EXTERNAL_EXISTING_PATH = "Cargo.toml"
EXTERNAL_MISSING_PATH = "THIS_FILE_DOES_NOT_EXIST_9f8e7d6c.md"

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
    "broken-preamble-uncited-claim.md": ["missing-citation"],
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
    "block-private-key.md": {"disposition_by_category": {"private-key": "block"}},
    "block-connection-string.md": {"disposition_by_category": {"connection-string": "block"}},
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
    "dispatch-roster-names.md": {"disposition_by_category": {"roster-names": "not_evaluated"}},
    "clean-unrelated-roster-and-names.md": {"disposition_by_category": {}},
}

# The exact, complete message professor.py's pack-root guard emits -- not a
# substring match on the env var's name. A bare uncaught KeyError traceback
# (`KeyError: 'PROFESSOR_PACK_ROOT'`) would also satisfy a substring check on
# the variable name alone, which can't distinguish the designed fail-loud
# message from the exact "generic crash three steps later" anti-pattern this
# plan's step 1 explicitly forbade.
REQUIRED_UNSET_ERROR_TEXT = (
    "professor.py: $PROFESSOR_PACK_ROOT is not set. This tool needs it to "
    "resolve where this pack's own files (contract specs, etc.) live -- set "
    "$PROFESSOR_PACK_ROOT to this pack's root directory (the directory "
    "containing this `tools/` folder) before calling professor.py."
)

SUBCOMMAND_ARGS_FOR_UNSET_CHECK = {
    "resolve-pin": ["resolve-pin", "--repo", "x/y", "--ref", "main"],
    "path-exists-at": ["path-exists-at", "--repo", "x/y", "--commit", "a" * 40, "--path", "z"],
    "check-page": ["check-page", "x.md", "--target", "/tmp"],
    "screen-content": ["screen-content", "x.md"],
}


def _run_professor(
    args: list[str],
    *,
    pack_root: str | None,
    cwd: str | None = None,
    path_prepend: str | None = None,
):
    env = dict(os.environ)
    if pack_root is None:
        env["PROFESSOR_PACK_ROOT"] = ""
    else:
        env["PROFESSOR_PACK_ROOT"] = pack_root
    if path_prepend is not None:
        env["PATH"] = path_prepend + os.pathsep + env.get("PATH", "")
    return subprocess.run(
        ["python3", str(PROFESSOR_PY), *args],
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
            ["resolve-pin", "--repo", EXTERNAL_REPO, "--ref", EXTERNAL_REF],
            pack_root="/tmp/an-arbitrary-pack-root-that-need-not-exist",
            cwd=outside_cwd,
        )
        if result.returncode != 0:
            return f"resolve-pin from outside checkout failed: {result.stderr}"
        sha = result.stdout.strip()
        if len(sha) != 40 or any(c not in "0123456789abcdef" for c in sha):
            return f"resolve-pin from outside checkout did not return a 40-char SHA: {sha!r}"
        return None


def check_resolve_pin_matches_git_ls_remote() -> tuple[str | None, str | None]:
    """Returns (error_or_None, resolved_sha_or_None)."""
    result = _run_professor(
        ["resolve-pin", "--repo", EXTERNAL_REPO, "--ref", EXTERNAL_REF], pack_root="/tmp"
    )
    if result.returncode != 0:
        return f"resolve-pin failed: {result.stderr}", None
    sha = result.stdout.strip()
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


def check_path_exists_at_true_and_false(sha: str) -> str | None:
    true_result = _run_professor(
        ["path-exists-at", "--repo", EXTERNAL_REPO, "--commit", sha, "--path", EXTERNAL_EXISTING_PATH],
        pack_root="/tmp",
    )
    if true_result.returncode != 0 or true_result.stdout.strip() != "true":
        return f"path-exists-at(real path) did not return true: {true_result.stdout!r} {true_result.stderr!r}"

    false_result = _run_professor(
        ["path-exists-at", "--repo", EXTERNAL_REPO, "--commit", sha, "--path", EXTERNAL_MISSING_PATH],
        pack_root="/tmp",
    )
    if false_result.returncode != 0 or false_result.stdout.strip() != "false":
        return f"path-exists-at(fabricated path) did not return false: {false_result.stdout!r} {false_result.stderr!r}"

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
            pack_root="/tmp",
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
            ["check-page", str(fixture_path), "--target", target_dir], pack_root="/tmp"
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
            pack_root="/tmp",
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
            pack_root="/tmp",
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


def check_check_page_fixtures() -> str | None:
    for fixture_name, expected_rules in CHECK_PAGE_EXPECTED_RULES.items():
        fixture_path = FIXTURES_DIR / fixture_name
        result = _run_professor(
            ["check-page", str(fixture_path), "--target", str(REPO_ROOT)], pack_root="/tmp"
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
            ["check-page", str(fixture_path), "--target", str(REPO_ROOT)], pack_root="/tmp"
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
        result = _run_professor(["screen-content", str(fixture_path)], pack_root="/tmp")
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


def main() -> int:
    checks = [
        ("pack-root unset fails loud (all four subcommands)", check_pack_root_unset_fails_loud),
        (
            "pack-root resolution from outside checkout",
            check_pack_root_resolution_outside_checkout,
        ),
    ]

    for name, check in checks:
        error = check()
        if error:
            print(f"FAIL [{name}]: {error}")
            return 1
        print(f"ok: {name}")

    error, sha = check_resolve_pin_matches_git_ls_remote()
    if error:
        print(f"FAIL [resolve-pin matches git ls-remote]: {error}")
        return 1
    print(f"ok: resolve-pin matches git ls-remote ({sha})")

    error = check_path_exists_at_true_and_false(sha)
    if error:
        print(f"FAIL [path-exists-at true/false]: {error}")
        return 1
    print("ok: path-exists-at true/false")

    error = check_citation_check_error_on_api_failure()
    if error:
        print(f"FAIL [citation-check-error on API failure]: {error}")
        return 1
    print("ok: citation-check-error on API failure (not collapsed into citation-not-found)")

    error = check_local_citation_error_shapes()
    if error:
        print(f"FAIL [local-citation error shapes]: {error}")
        return 1
    print(
        "ok: local-citation error shapes (nonexistent --target, non-git "
        "--target, empty git repo all citation-check-error, never citation-not-found)"
    )

    error = check_local_citation_never_calls_gh()
    if error:
        print(f"FAIL [local-vs-network boundary]: {error}")
        return 1
    print("ok: local-vs-network boundary (compliant-local.md never calls gh, compliant-external.md does)")

    error = check_check_page_fixtures()
    if error:
        print(f"FAIL [check-page fixtures]: {error}")
        return 1
    print(f"ok: check-page fixtures ({len(CHECK_PAGE_EXPECTED_RULES)} fixtures)")

    error = check_frontmatter_branches_are_distinct()
    if error:
        print(f"FAIL [frontmatter branches distinct]: {error}")
        return 1
    print(
        "ok: frontmatter branches distinct "
        f"({len(FRONTMATTER_BRANCH_EXPECTED_MESSAGE_SUBSTRING)} branches)"
    )

    error = check_screen_content_fixtures()
    if error:
        print(f"FAIL [screen-content fixtures]: {error}")
        return 1
    print(f"ok: screen-content fixtures ({len(SCREEN_CONTENT_EXPECTED)} fixtures)")

    print("ALL CHECKS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
