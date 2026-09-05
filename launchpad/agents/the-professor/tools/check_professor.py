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
    "broken-nonexistent-citation.md": ["citation-not-found"],
    "broken-missing-citation.md": ["missing-citation"],
    "broken-out-of-bounds-range.md": ["out-of-bounds-range"],
    "broken-no-provenance-marker.md": ["missing-provenance-marker"],
    "broken-mismatched-marker.md": ["mismatched-provenance-marker"],
    "broken-mixed-claim.md": ["mixed-claim"],
    "broken-frontmatter.md": ["frontmatter"],
}

SCREEN_CONTENT_EXPECTED = {
    "clean.md": {"disposition_by_category": {}},
    "block-api-key.md": {"disposition_by_category": {"api-key-token": "block"}},
    "block-private-key.md": {"disposition_by_category": {"private-key": "block"}},
    "block-connection-string.md": {"disposition_by_category": {"connection-string": "block"}},
    "block-webhook-url.md": {"disposition_by_category": {"webhook-url-token": "block"}},
    "redact-email.md": {"disposition_by_category": {"email-address": "redact"}},
    "redact-internal-host.md": {
        "disposition_by_category": {"internal-hostname-private-ip": "redact"}
    },
    "redact-physical-address.md": {"disposition_by_category": {"physical-address": "redact"}},
    "dispatch-roster-names.md": {"disposition_by_category": {"roster-names": "not_evaluated"}},
}

REQUIRED_UNSET_ERROR_TEXT = "PROFESSOR_PACK_ROOT"

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
        if REQUIRED_UNSET_ERROR_TEXT not in result.stderr:
            return (
                f"{name}: error message did not name {REQUIRED_UNSET_ERROR_TEXT!r}: "
                f"{result.stderr!r}"
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

        if not expected_by_category:
            if findings:
                return f"screen-content({fixture_name}): expected no findings, got {findings!r}"
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

    error = check_check_page_fixtures()
    if error:
        print(f"FAIL [check-page fixtures]: {error}")
        return 1
    print(f"ok: check-page fixtures ({len(CHECK_PAGE_EXPECTED_RULES)} fixtures)")

    error = check_screen_content_fixtures()
    if error:
        print(f"FAIL [screen-content fixtures]: {error}")
        return 1
    print(f"ok: screen-content fixtures ({len(SCREEN_CONTENT_EXPECTED)} fixtures)")

    print("ALL CHECKS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
