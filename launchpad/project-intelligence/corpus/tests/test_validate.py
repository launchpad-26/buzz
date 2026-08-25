"""Unit tests for the deterministic corpus validator -- issue #623.

Run:  python3 -m unittest launchpad.project_intelligence.corpus.tests.test_validate
  or: python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"

These tests only ever point --root at fixtures under this directory, never at the
real launchpad/docs/corpus/ -- that root's own content (or lack of it) must never
change what this suite asserts.
"""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"
VALID_DIR = FIXTURES_DIR / "valid"
INVALID_DIR = FIXTURES_DIR / "invalid"

# validate.py lives in a directory (project-intelligence/corpus/) that isn't a
# package (no __init__.py, matching this repo's existing project-intelligence/
# convention), so it's loaded by path rather than imported by dotted name.
_VALIDATE_PATH = Path(__file__).resolve().parent.parent / "validate.py"
_spec = importlib.util.spec_from_file_location("corpus_validate", _VALIDATE_PATH)
validate = importlib.util.module_from_spec(_spec)
sys.modules["corpus_validate"] = validate
_spec.loader.exec_module(validate)


class ValidFixtureTest(unittest.TestCase):
    def test_valid_fixture_passes(self) -> None:
        errors = validate.validate_corpus(VALID_DIR)
        self.assertEqual(errors, [])


class SchemaViolationTest(unittest.TestCase):
    def test_bad_schema_fixture_named_and_rejected(self) -> None:
        errors = validate.validate_corpus(INVALID_DIR)
        self.assertEqual(len(errors), 1)
        self.assertIn("validator-fixture-bad-schema", errors[0])


class RealCorpusRootExclusionTest(unittest.TestCase):
    """schema/ is #622's own infrastructure, never scanned as corpus content."""

    def test_real_corpus_root_excludes_schema_dir(self) -> None:
        root = validate.repo_root() / validate.DEFAULT_ROOT
        files = validate.discover_markdown_files(root)
        self.assertTrue(
            all("schema" not in f.relative_to(root).parts[:1] for f in files),
            f"a file under schema/ leaked into discovery: {files}",
        )


if __name__ == "__main__":
    unittest.main()
