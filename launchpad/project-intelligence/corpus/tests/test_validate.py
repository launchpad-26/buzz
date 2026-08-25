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
        errors = validate.validate_corpus(INVALID_DIR / "bad-schema")
        self.assertEqual(len(errors), 1)
        self.assertIn("validator-fixture-bad-schema", errors[0])


class DuplicateIdTest(unittest.TestCase):
    def test_duplicate_id_rejected_and_named(self) -> None:
        errors = validate.validate_corpus(INVALID_DIR / "duplicate-id")
        self.assertEqual(len(errors), 1)
        self.assertIn("validator-fixture-duplicate", errors[0])
        self.assertIn("duplicate id", errors[0])


class UnresolvedRelationshipTargetTest(unittest.TestCase):
    def test_unresolved_target_rejected_and_named(self) -> None:
        errors = validate.validate_corpus(INVALID_DIR / "unresolved-target")
        self.assertEqual(len(errors), 1)
        self.assertIn("validator-fixture-unresolved-target", errors[0])
        self.assertIn("no-such-node-anywhere", errors[0])


class MissingCitationTest(unittest.TestCase):
    def test_missing_citation_rejected_and_named(self) -> None:
        errors = validate.validate_corpus(INVALID_DIR / "missing-citation")
        self.assertEqual(len(errors), 1)
        self.assertIn("validator-fixture-missing-citation", errors[0])
        # The offending path itself is not required to be absent from this
        # particular error class's message -- unlike prohibited-citation below,
        # a missing-file path is not private content. Only assert the node is named.


class ProhibitedCitationTest(unittest.TestCase):
    def test_prohibited_citation_rejected_without_leaking_the_value(self) -> None:
        errors = validate.validate_corpus(INVALID_DIR / "prohibited-citation")
        self.assertEqual(len(errors), 1)
        self.assertIn("validator-fixture-prohibited-citation", errors[0])
        # The DoD's "without leaking private source content", taken literally: the
        # rejected value itself must never appear in the error output.
        self.assertNotIn("id_rsa", errors[0])

    def test_ordinary_auth_path_is_not_prohibited(self) -> None:
        # crates/buzz-auth is a real, ordinary, non-secret crate this repo ships.
        # An earlier draft of this plan's credential blocklist (*auth* as a bare
        # substring) would have rejected it; serina:review-plan caught this before
        # any code was written. node-b-auth-citation.md in the valid fixtures cites
        # exactly this path -- this test asserts it passes, not merely that the
        # whole valid directory happens to pass for unrelated reasons.
        self.assertFalse(validate._is_prohibited_citation("crates/buzz-auth/src/lib.rs"))


class OwnershipViolationTest(unittest.TestCase):
    def test_stray_non_md_file_rejected_and_named(self) -> None:
        errors = validate.validate_corpus(INVALID_DIR / "misplaced-generated")
        self.assertEqual(len(errors), 1)
        self.assertIn("index.json", errors[0])


class MissingInputTest(unittest.TestCase):
    """A nonexistent root is a missing input (fail closed). An existing root with
    zero nodes is a true, honest state -- launchpad/docs/corpus/ today, before
    #636/#639 land content -- and must pass, not fail. These are deliberately
    different outcomes; see this plan's own OPEN section for why."""

    def test_nonexistent_root_raises_corpus_root_missing(self) -> None:
        missing_path = FIXTURES_DIR / "does-not-exist-anywhere"
        self.assertFalse(missing_path.exists())
        with self.assertRaises(validate.CorpusRootMissing):
            validate.validate_corpus(missing_path)

    def test_main_reports_failure_for_nonexistent_root(self) -> None:
        missing_path = FIXTURES_DIR / "does-not-exist-anywhere"
        exit_code = validate.main(["--root", str(missing_path)])
        self.assertEqual(exit_code, 1)

    def test_existing_but_empty_root_passes_cleanly(self) -> None:
        empty_dir = FIXTURES_DIR / "empty-on-purpose"
        empty_dir.mkdir(exist_ok=True)
        try:
            self.assertEqual(validate.validate_corpus(empty_dir), [])
        finally:
            empty_dir.rmdir()


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
