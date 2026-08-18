#!/usr/bin/env python3
"""Controls for the fork-added/inherited classifier.

Uses a synthetic upstream tree rather than a real network fetch, so these tests
are fast and offline — the real `fetch_upstream_paths` path is exercised live by
the audit workflow itself, not by this suite. The three paths named in #66's
definition of done are asserted explicitly, not just covered incidentally.
"""

import unittest

from security_audit_classifier import classify

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


if __name__ == "__main__":
    unittest.main()
