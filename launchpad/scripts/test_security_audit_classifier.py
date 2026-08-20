#!/usr/bin/env python3
"""Controls for the fork-added/inherited classifier.

Uses a synthetic upstream tree rather than a real network fetch, so these tests
are fast and offline — the real `fetch_upstream_paths` path is exercised live by
the audit workflow itself, not by this suite. The three paths named in #66's
definition of done are asserted explicitly, not just covered incidentally.

FetchUpstreamPathsTest mocks subprocess.run to force each way `fetch_upstream_paths`
can fail, so a future edit narrowing its `except` clause fails this suite instead
of only showing up as a silent misclassification the next time the network drops.
"""

import subprocess
import unittest
from pathlib import Path
from unittest.mock import patch

from security_audit_classifier import classify, fetch_upstream_paths

# A stand-in for block/buzz's real tree: enough to classify the three paths
# #66 requires, without depending on the network.
_SYNTHETIC_UPSTREAM_PATHS = {
    ".github/workflows/ci.yml",
    "Cargo.toml",
    "src/main.rs",
}


class ClassifyTest(unittest.TestCase):
    def test_fork_only_directory_is_fork_added(self):
        self.assertEqual(
            classify("launchpad/deploy/README.md", _SYNTHETIC_UPSTREAM_PATHS),
            "fork-added",
        )

    def test_file_present_upstream_is_inherited(self):
        self.assertEqual(
            classify(".github/workflows/ci.yml", _SYNTHETIC_UPSTREAM_PATHS),
            "inherited",
        )

    def test_new_fork_only_workflow_is_fork_added(self):
        self.assertEqual(
            classify(".github/workflows/launchpad-security-audit.yml", _SYNTHETIC_UPSTREAM_PATHS),
            "fork-added",
        )

    def test_unreachable_upstream_is_indeterminate_not_a_guess(self):
        for path in (
            "launchpad/deploy/README.md",
            ".github/workflows/ci.yml",
            ".github/workflows/launchpad-security-audit.yml",
        ):
            self.assertEqual(classify(path, None), "indeterminate")

    def test_windows_style_separators_are_normalized(self):
        self.assertEqual(
            classify(".github\\workflows\\ci.yml", _SYNTHETIC_UPSTREAM_PATHS),
            "inherited",
        )

    def test_dot_slash_prefixed_path_is_normalized(self):
        self.assertEqual(
            classify("./.github/workflows/ci.yml", _SYNTHETIC_UPSTREAM_PATHS),
            "inherited",
        )

    def test_absolute_path_is_indeterminate_not_a_guess(self):
        self.assertEqual(
            classify(
                "/home/serina/Launchpad/buzz/.github/workflows/ci.yml",
                _SYNTHETIC_UPSTREAM_PATHS,
            ),
            "indeterminate",
        )

    def test_absolute_path_to_a_fork_only_file_is_still_indeterminate(self):
        # A caller bug that computes absolute paths should never resolve to a
        # guess in either direction, not just for genuinely-inherited files.
        self.assertEqual(
            classify("/home/serina/Launchpad/buzz/launchpad/deploy/README.md", _SYNTHETIC_UPSTREAM_PATHS),
            "indeterminate",
        )


class FetchUpstreamPathsTest(unittest.TestCase):
    def test_returns_none_on_called_process_error(self):
        with patch(
            "security_audit_classifier.subprocess.run",
            side_effect=subprocess.CalledProcessError(1, "git"),
        ):
            self.assertIsNone(fetch_upstream_paths(Path(".")))

    def test_returns_none_on_timeout(self):
        with patch(
            "security_audit_classifier.subprocess.run",
            side_effect=subprocess.TimeoutExpired("git", 30),
        ):
            self.assertIsNone(fetch_upstream_paths(Path(".")))

    def test_returns_none_on_os_error(self):
        # git itself missing from PATH, e.g. — no CalledProcessError, since the
        # process never started.
        with patch("security_audit_classifier.subprocess.run", side_effect=OSError("no git")):
            self.assertIsNone(fetch_upstream_paths(Path(".")))

    def test_parses_nul_separated_output_on_success(self):
        fetch_result = subprocess.CompletedProcess(args=["git", "fetch"], returncode=0)
        # A trailing NUL after the last entry, as git ls-tree -z actually emits —
        # the split must not produce a spurious empty-string path from it.
        ls_tree_result = subprocess.CompletedProcess(
            args=["git", "ls-tree"],
            returncode=0,
            stdout="Cargo.toml\x00.github/workflows/ci.yml\x00",
        )
        with patch(
            "security_audit_classifier.subprocess.run",
            side_effect=[fetch_result, ls_tree_result],
        ):
            paths = fetch_upstream_paths(Path("."))
        self.assertEqual(paths, {"Cargo.toml", ".github/workflows/ci.yml"})


if __name__ == "__main__":
    unittest.main()
