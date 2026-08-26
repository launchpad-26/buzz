#!/usr/bin/env python3
"""Proves `.gitleaks.toml`'s rules actually fire, against real fixtures.

WHY THIS EXISTS SEPARATELY FROM test_security_audit_secrets_check.py

That suite mocks `subprocess.run` throughout and says so in its own docstring:
it tests the check script's branching and error handling. Nothing in it runs
gitleaks, so it stays green if a rule in `.gitleaks.toml` breaks. The PR body
for #67 pasted a manual run proving each category fires — but a manual run is
not a test, and `test_security_audit_secrets_check.py` itself records a
near-miss where a capturing group silently dropped a finding to zero once
`useDefault = true` was added. This closes that: edit a rule so it no longer
matches, and this fails.

THREE OF THE SEVEN CATEGORIES RIDE ON GITLEAKS' OWN DEFAULT RULESET

`.gitleaks.toml` sets `[extend] useDefault = true`, and the SSH-key, registry
token and 64-hex/env-assignment categories are matched by gitleaks' built-in
`private-key`, `github-pat` and `generic-api-key` rules rather than by anything
this repo wrote. #67's own "Not verified" flagged that a gitleaks version bump
could change that behaviour with nothing to catch it. That is why DEFAULT_RULES
is asserted separately below and why its failure message names the version: a
break there points at the pin in `launchpad-security-audit.yml`, not at a rule
in this repo.

THE FIXTURE DIRECTORY IS ALLOWLISTED IN THE REAL CONFIG

`.gitleaks.toml`'s global `[allowlist] paths` excludes the fixtures, so the live
scan does not report on them — correct for the live scan, and fatal for a test
that used the config unmodified: it would scan an excluded directory, find
nothing, and pass. So this builds a copy with that one path entry removed, and
asserts the entry was present before removing it. If the config is restructured
so the line no longer matches verbatim, this fails loudly instead of quietly
scanning nothing.

NO SECRET VALUE IS PRINTED

gitleaks runs with `--redact`, and every assertion message here is built from
rule IDs and fixture filenames only — never from a report's `Secret` or `Match`
field. `test_no_secret_value_survives_redaction` asserts the redaction rather
than assuming it.

SKIPPING

Skipped when gitleaks is not on PATH, so a local `unittest discover` still runs
for someone who has not installed it. That skip is a hole in CI, where gitleaks
IS installed and this must actually execute — so set
`REQUIRE_GITLEAKS_RULESET=1` and the skip becomes a failure. The workflow sets
it. Same reasoning as launchpad-agents-tests.yml's empty-discovery guard: a
check that can be satisfied by absence is not a check.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CONFIG = REPO_ROOT / ".gitleaks.toml"
FIXTURES = REPO_ROOT / "launchpad/scripts/security_audit_fixtures/secrets"

# The one global-allowlist entry that hides the fixtures from the live scan.
# Matched verbatim so a restructured config fails this test rather than
# silently reducing it to a scan of an excluded directory.
FIXTURE_ALLOWLIST_LINE = (
    "    '''launchpad/scripts/security_audit_fixtures/secrets/.*''',\n"
)

# Rules this repo defines in .gitleaks.toml. A miss here is our regex.
OUR_RULES = {
    "nostr-nsec-private-key",
    "buzz-private-key",
    "glibc-crypt-hash",
    "buzz-s3-minio-key",
    "postgres-url-with-password",
}

# Rules gitleaks itself supplies via [extend] useDefault = true. A miss here is
# most likely the pinned gitleaks version changing, not a change in this repo.
DEFAULT_RULES = {
    "private-key",      # ssh_private_key.txt
    "github-pat",       # registry_token.txt
    "generic-api-key",  # env_assignment.env and the 64-hex shapes
}

# Every fixture file must produce at least one finding. Stronger than the rule
# assertions on their own: it catches a fixture nobody matches any more, which
# rule-level assertions can hide when two fixtures share a rule.
EXPECTED_FIXTURE_FILES = {
    "crypt_hashes.txt",
    "env_assignment.env",
    "nostr_keys.txt",
    "postgres_url.txt",
    "registry_token.txt",
    "s3_minio_keys.txt",
    "ssh_private_key.txt",
}


def _gitleaks_version() -> str:
    try:
        out = subprocess.run(
            ["gitleaks", "version"],
            capture_output=True, encoding="utf-8", errors="replace", timeout=30,
        )
        return (out.stdout or out.stderr or "").strip() or "unknown"
    except (OSError, subprocess.SubprocessError):
        return "unknown"


def _skip_or_fail_without_gitleaks() -> None:
    """Skip locally, fail in CI. See the SKIPPING note in the module docstring."""
    if shutil.which("gitleaks"):
        return
    if os.environ.get("REQUIRE_GITLEAKS_RULESET") == "1":
        raise AssertionError(
            "REQUIRE_GITLEAKS_RULESET=1 but gitleaks is not on PATH. This suite is "
            "the only thing that proves .gitleaks.toml's rules still fire; letting "
            "it skip here would pass vacuously. Check the install step in "
            ".github/workflows/launchpad-security-audit.yml."
        )
    raise unittest.SkipTest(
        "gitleaks not on PATH — install it, or set REQUIRE_GITLEAKS_RULESET=1 to "
        "make its absence a failure (CI does)."
    )


class GitleaksRulesetTests(unittest.TestCase):
    """Runs the real binary against the real fixtures with the real ruleset."""

    findings: list[dict] = []

    @classmethod
    def setUpClass(cls) -> None:
        _skip_or_fail_without_gitleaks()

        if not CONFIG.is_file():
            raise AssertionError(f"{CONFIG} not found — cannot scan without the ruleset")
        if not FIXTURES.is_dir():
            raise AssertionError(f"{FIXTURES} not found — nothing to scan")

        source = CONFIG.read_text(encoding="utf-8")
        if FIXTURE_ALLOWLIST_LINE not in source:
            raise AssertionError(
                "The fixture path-allowlist entry was not found verbatim in "
                ".gitleaks.toml. It is what hides the fixtures from the live scan, "
                "and this test must remove it to have anything to scan. The config "
                "has been restructured: update FIXTURE_ALLOWLIST_LINE to match, and "
                "confirm the live scan still excludes the fixtures."
            )

        cls._tmp = tempfile.TemporaryDirectory()
        tmp = Path(cls._tmp.name)
        scan_config = tmp / "gitleaks-fixtures.toml"
        scan_config.write_text(source.replace(FIXTURE_ALLOWLIST_LINE, ""), encoding="utf-8")
        report = tmp / "report.json"

        proc = subprocess.run(
            [
                "gitleaks", "detect",
                "--no-git",
                "--source", str(FIXTURES),
                "--config", str(scan_config),
                "--report-format", "json",
                "--report-path", str(report),
                "--redact",
                "--no-banner",
                # Findings ARE the expected result here, so a non-zero "leaks
                # found" exit is not a failure of this test.
                "--exit-code", "0",
            ],
            capture_output=True, encoding="utf-8", errors="replace", timeout=180,
        )
        if proc.returncode != 0:
            raise AssertionError(
                f"gitleaks exited {proc.returncode} with --exit-code 0, which means it "
                f"could not run rather than that it found nothing. stderr tail: "
                f"{(proc.stderr or '')[-400:]}"
            )
        if not report.is_file():
            raise AssertionError("gitleaks wrote no report file")

        raw = report.read_text(encoding="utf-8").strip()
        cls.findings = json.loads(raw) if raw else []

    @classmethod
    def tearDownClass(cls) -> None:
        tmp = getattr(cls, "_tmp", None)
        if tmp is not None:
            tmp.cleanup()

    def test_the_scan_produced_findings_at_all(self):
        """A zero-finding scan is the failure this whole suite exists to catch."""
        self.assertGreater(
            len(self.findings), 0,
            "gitleaks reported zero findings against the planted fixtures. Either "
            "every rule is broken, or the fixtures are still being allowlisted out "
            "of the scan.",
        )

    def test_every_rule_this_repo_defines_fires(self):
        fired = {f["RuleID"] for f in self.findings}
        missing = sorted(OUR_RULES - fired)
        self.assertFalse(
            missing,
            f"Rules defined in .gitleaks.toml that matched nothing: {missing}. Their "
            f"fixtures are still present, so the regex no longer matches. Rules that "
            f"did fire: {sorted(fired)}",
        )

    def test_every_gitleaks_default_rule_we_rely_on_fires(self):
        """Separate from our own rules: a miss here points at the version pin."""
        fired = {f["RuleID"] for f in self.findings}
        missing = sorted(DEFAULT_RULES - fired)
        self.assertFalse(
            missing,
            f"gitleaks' own default rules that matched nothing: {missing}. "
            f".gitleaks.toml relies on these via [extend] useDefault = true and does "
            f"not define equivalents, so these categories are now unguarded. Most "
            f"likely cause is the pinned gitleaks version changing its default "
            f"ruleset — running version: {_gitleaks_version()}. The pin lives in "
            f".github/workflows/launchpad-security-audit.yml. Rules that did fire: "
            f"{sorted(fired)}",
        )

    def test_every_fixture_file_is_matched_by_something(self):
        """Catches an orphaned fixture that rule-level assertions would hide."""
        matched = {Path(f["File"]).name for f in self.findings}
        unmatched = sorted(EXPECTED_FIXTURE_FILES - matched)
        self.assertFalse(
            unmatched,
            f"Fixture files that produced no finding: {unmatched}. Each exists to "
            f"prove one category is caught; a fixture nobody matches is a category "
            f"nobody guards.",
        )

    def test_the_fixture_set_has_not_grown_unnoticed(self):
        """A new fixture with no assertion is a category nobody proved."""
        on_disk = {p.name for p in FIXTURES.iterdir() if p.is_file()}
        untracked = sorted(on_disk - EXPECTED_FIXTURE_FILES)
        self.assertFalse(
            untracked,
            f"Fixture files present but not named in EXPECTED_FIXTURE_FILES: "
            f"{untracked}. Add them there, and add the rule they are meant to prove "
            f"to OUR_RULES or DEFAULT_RULES, or this suite silently ignores them.",
        )

    def test_no_secret_value_survives_redaction(self):
        """The disclosure guarantee, asserted rather than assumed."""
        leaked = sorted({
            f["RuleID"] for f in self.findings
            if f.get("Secret") and f["Secret"] != "REDACTED"
        })
        self.assertFalse(
            leaked,
            f"gitleaks returned an unredacted Secret field for findings from rules "
            f"{leaked}. --redact is what keeps fixture values out of CI logs and out "
            f"of this suite's own failure output. Do not paste the value here while "
            f"debugging.",
        )


if __name__ == "__main__":
    unittest.main()
