#!/usr/bin/env python3
"""Controls for the #67 secret-material check.

Mocks subprocess.run throughout — no real gitleaks invocation, no network.
.gitleaks.toml's rules themselves are proven against real fixtures with the
real gitleaks binary separately (see the PR body / commit history for that
evidence); this suite is about the check script's own branching and error
handling, which is what a future edit is most likely to quietly break.
"""

import json
import subprocess
import unittest
from pathlib import Path
from unittest.mock import patch

from security_audit_core import Status
from security_audit_secrets_check import run, _run_gitleaks, _scan_full_history, _scan_pr_diff


def _completed(returncode, stdout="[]", stderr=""):
    return subprocess.CompletedProcess(args=["gitleaks"], returncode=returncode, stdout=stdout, stderr=stderr)


_FINDING = {"File": "a.env", "StartLine": 3, "RuleID": "buzz-s3-minio-key", "Secret": "should-never-appear"}


class RunGitleaksTest(unittest.TestCase):
    def test_missing_config_is_indeterminate_without_running_gitleaks(self):
        with patch("security_audit_secrets_check.subprocess.run") as mock_run:
            findings, error = _run_gitleaks(Path("/nonexistent-repo-root"), None, 10)
        mock_run.assert_not_called()
        self.assertIsNone(findings)
        self.assertIn(".gitleaks.toml", error)

    def test_clean_run_returns_empty_findings(self):
        with patch("security_audit_secrets_check.Path.is_file", return_value=True), patch(
            "security_audit_secrets_check.subprocess.run", return_value=_completed(0, "[]")
        ):
            findings, error = _run_gitleaks(Path("."), None, 10)
        self.assertEqual(findings, [])
        self.assertIsNone(error)

    def test_leaks_found_exit_code_one_is_still_success(self):
        # gitleaks exits 1 when it finds something — that is the normal
        # "it worked and found leaks" outcome, not an engine failure.
        with patch("security_audit_secrets_check.Path.is_file", return_value=True), patch(
            "security_audit_secrets_check.subprocess.run",
            return_value=_completed(1, json.dumps([_FINDING])),
        ):
            findings, error = _run_gitleaks(Path("."), None, 10)
        self.assertIsNone(error)
        self.assertEqual(len(findings), 1)

    def test_unexpected_exit_code_is_indeterminate(self):
        with patch("security_audit_secrets_check.Path.is_file", return_value=True), patch(
            "security_audit_secrets_check.subprocess.run", return_value=_completed(2, "", "config error")
        ):
            findings, error = _run_gitleaks(Path("."), None, 10)
        self.assertIsNone(findings)
        self.assertIn("config error", error)

    def test_binary_missing_is_indeterminate(self):
        with patch("security_audit_secrets_check.Path.is_file", return_value=True), patch(
            "security_audit_secrets_check.subprocess.run", side_effect=FileNotFoundError()
        ):
            findings, error = _run_gitleaks(Path("."), None, 10)
        self.assertIsNone(findings)
        self.assertIn("not installed", error)

    def test_timeout_is_indeterminate(self):
        with patch("security_audit_secrets_check.Path.is_file", return_value=True), patch(
            "security_audit_secrets_check.subprocess.run",
            side_effect=subprocess.TimeoutExpired("gitleaks", 10),
        ):
            findings, error = _run_gitleaks(Path("."), None, 10)
        self.assertIsNone(findings)
        self.assertIn("10s", error)

    def test_malformed_json_is_indeterminate(self):
        with patch("security_audit_secrets_check.Path.is_file", return_value=True), patch(
            "security_audit_secrets_check.subprocess.run", return_value=_completed(0, "not json")
        ):
            findings, error = _run_gitleaks(Path("."), None, 10)
        self.assertIsNone(findings)
        self.assertIn("could not parse", error)


class ScanFullHistoryTest(unittest.TestCase):
    def test_clean_history_passes(self):
        with patch("security_audit_secrets_check._run_gitleaks", return_value=([], None)):
            result = _scan_full_history(Path("."))
        self.assertEqual(result.status, Status.PASS)

    def test_findings_warn_not_fail(self):
        # The scheduled/full-history path REPORTS, per #67's definition of
        # done — it must never turn a pre-existing finding into a build
        # failure, which is what distinguishes it from the PR path.
        with patch("security_audit_secrets_check._run_gitleaks", return_value=([_FINDING], None)):
            result = _scan_full_history(Path("."))
        self.assertEqual(result.status, Status.WARN)
        self.assertNotIn("should-never-appear", result.detail)

    def test_engine_error_is_indeterminate(self):
        with patch("security_audit_secrets_check._run_gitleaks", return_value=(None, "boom")):
            result = _scan_full_history(Path("."))
        self.assertEqual(result.status, Status.INDETERMINATE)


class ScanPrDiffTest(unittest.TestCase):
    def test_missing_base_ref_is_indeterminate(self):
        with patch.dict("os.environ", {}, clear=True):
            result = _scan_pr_diff(Path("."))
        self.assertEqual(result.status, Status.INDETERMINATE)
        self.assertIn("GITHUB_BASE_REF", result.detail)

    def test_fetch_failure_is_indeterminate(self):
        with patch.dict("os.environ", {"GITHUB_BASE_REF": "launchpad"}), patch(
            "security_audit_secrets_check.subprocess.run",
            side_effect=subprocess.CalledProcessError(1, "git"),
        ):
            result = _scan_pr_diff(Path("."))
        self.assertEqual(result.status, Status.INDETERMINATE)
        self.assertIn("launchpad", result.detail)

    def test_clean_diff_passes(self):
        with patch.dict("os.environ", {"GITHUB_BASE_REF": "launchpad"}), patch(
            "security_audit_secrets_check.subprocess.run", return_value=_completed(0)
        ), patch("security_audit_secrets_check._run_gitleaks", return_value=([], None)):
            result = _scan_pr_diff(Path("."))
        self.assertEqual(result.status, Status.PASS)

    def test_finding_in_diff_fails_the_run(self):
        with patch.dict("os.environ", {"GITHUB_BASE_REF": "launchpad"}), patch(
            "security_audit_secrets_check.subprocess.run", return_value=_completed(0)
        ), patch("security_audit_secrets_check._run_gitleaks", return_value=([_FINDING], None)):
            result = _scan_pr_diff(Path("."))
        self.assertEqual(result.status, Status.FAIL)
        self.assertNotIn("should-never-appear", result.detail)
        self.assertIn("a.env:3", result.detail)


class RunDispatchTest(unittest.TestCase):
    def test_pull_request_event_uses_diff_scan(self):
        with patch.dict("os.environ", {"GITHUB_EVENT_NAME": "pull_request"}), patch(
            "security_audit_secrets_check._scan_pr_diff"
        ) as mock_diff, patch("security_audit_secrets_check._scan_full_history") as mock_full:
            run(Path("."))
        mock_diff.assert_called_once()
        mock_full.assert_not_called()

    def test_other_events_use_full_history_scan(self):
        for event in ("schedule", "workflow_dispatch", ""):
            with patch.dict("os.environ", {"GITHUB_EVENT_NAME": event}), patch(
                "security_audit_secrets_check._scan_pr_diff"
            ) as mock_diff, patch("security_audit_secrets_check._scan_full_history") as mock_full:
                run(Path("."))
            mock_diff.assert_not_called()
            mock_full.assert_called_once()


if __name__ == "__main__":
    unittest.main()
