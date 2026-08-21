#!/usr/bin/env python3
"""Controls for the #68 ignore-coverage check.

Builds real temp-directory fixtures with real files on disk and points
`run()` at them — no mocking, since this check's whole job is reading real
file content, and a mock of `Path.read_text` would just be re-asserting the
implementation rather than proving the behaviour.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from security_audit_core import Status
from security_audit_ignore_coverage_check import REQUIRED_COVERAGE, run


def _write_full_coverage(root: Path) -> None:
    """A repo_root with every required pattern present, correctly placed."""
    for rel_path, patterns in REQUIRED_COVERAGE.items():
        full_path = root / rel_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text("\n".join(patterns) + "\n", encoding="utf-8")


class IgnoreCoverageTest(unittest.TestCase):
    def test_full_coverage_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_full_coverage(root)
            result = run(root)
        self.assertEqual(result.status, Status.PASS)

    def test_missing_pattern_in_root_gitignore_fails(self):
        # Fixture: every pattern present except one deliberately dropped from
        # .gitignore -- proves the check actually reads content, not just
        # file existence.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_full_coverage(root)
            patterns = [p for p in REQUIRED_COVERAGE[".gitignore"] if p != "*.pem"]
            (root / ".gitignore").write_text("\n".join(patterns) + "\n", encoding="utf-8")
            result = run(root)
        self.assertEqual(result.status, Status.FAIL)
        self.assertIn("*.pem", result.detail)

    def test_missing_pattern_in_archived_gitignore_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_full_coverage(root)
            deploy_gitignore = root / "launchpad/deploy/archived/.gitignore"
            deploy_gitignore.write_text("seed/\n", encoding="utf-8")  # seed.sample/ dropped
            result = run(root)
        self.assertEqual(result.status, Status.FAIL)
        self.assertIn("seed.sample/", result.detail)

    def test_differently_spelled_equivalent_pattern_still_fails(self):
        # A matcher-based check would treat "*.env" as equivalent coverage
        # for ".env" -- this check must not, since the whole point is
        # catching a silent respelling, not just "is something similar there".
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_full_coverage(root)
            patterns = ["*.env" if p == ".env" else p for p in REQUIRED_COVERAGE[".gitignore"]]
            (root / ".gitignore").write_text("\n".join(patterns) + "\n", encoding="utf-8")
            result = run(root)
        self.assertEqual(result.status, Status.FAIL)

    def test_missing_file_is_indeterminate_not_pass(self):
        # An absent gitignore file must never read as "nothing to fail on".
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = run(root)
        self.assertEqual(result.status, Status.INDETERMINATE)


if __name__ == "__main__":
    unittest.main()
