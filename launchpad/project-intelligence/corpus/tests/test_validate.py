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
import tempfile
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

    def test_valid_fixture_actually_discovers_its_nodes(self) -> None:
        # errors == [] alone can't distinguish "genuinely clean" from "discovery
        # silently found nothing" -- assert the positive too. Four nodes as of
        # this test: node-a, node-b (auth citation), node-c (url citation), node-d
        # (.env.example citation). generated/index.json is not .md and doesn't count.
        nodes = validate.load_nodes(VALID_DIR)
        self.assertEqual(len(nodes), 4)


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

    def test_env_example_is_not_prohibited(self) -> None:
        # .env.example is this repo's own real, tracked, non-secret config
        # template (AGENTS.md: `cp .env.example .env`). An independent
        # review-code pass found the .env.* blocklist rejected it -- the same
        # class of over-broad match already caught once for buzz-auth, recurring
        # here until that pass found it. node-d-env-example-citation.md in the
        # valid fixtures cites exactly this path.
        self.assertFalse(validate._is_prohibited_citation(".env.example"))

    def test_env_local_is_still_prohibited(self) -> None:
        # The exemption is for conventional non-secret suffixes only -- a real
        # .env.local (or bare .env) must still be rejected.
        self.assertTrue(validate._is_prohibited_citation(".env.local"))
        self.assertTrue(validate._is_prohibited_citation(".env"))


class MalformedEntryDoesNotCrashTest(unittest.TestCase):
    """A non-dict item in `evidence` or `relationships` must never crash the
    validator -- it must be reported (via node.error from schema validation,
    since node.schema.json already requires object-typed entries) rather than
    raising an unhandled AttributeError, per the DoD's "names the failing node,"
    which a stack trace does not. An independent review-code pass found this by
    constructing exactly this input against the shipped code."""

    def test_non_dict_evidence_item_does_not_crash(self) -> None:
        node = validate.LoadedNode(
            path=Path("synthetic"),
            data={"evidence": ["just a bare string, not an object"]},
            error="already reported by schema validation",
        )
        errors = validate.find_citation_problems([node], validate.repo_root())
        self.assertEqual(errors, [])

    def test_non_dict_relationship_item_does_not_crash(self) -> None:
        node = validate.LoadedNode(
            path=Path("synthetic"),
            data={"relationships": ["just a bare string, not an object"]},
            error="already reported by schema validation",
        )
        errors = validate.find_unresolved_relationship_targets([node])
        self.assertEqual(errors, [])


class AbsolutePathCitationTest(unittest.TestCase):
    """An absolute-path citation must be rejected explicitly, not silently
    "validated" against the host filesystem -- pathlib's `/` operator discards
    the left operand when the right is absolute, so `repo_root / "/etc/passwd"`
    would otherwise evaluate to `/etc/passwd` itself. An independent review-code
    pass found this by citing a path that genuinely exists on the host."""

    def test_absolute_path_citation_rejected(self) -> None:
        node = validate.LoadedNode(
            path=Path("synthetic"),
            id="abs-path-check",
            data={
                "evidence": [
                    {"statement": "x", "entry_class": "FACT", "evidence": ["/etc/passwd"]}
                ]
            },
        )
        errors = validate.find_citation_problems([node], validate.repo_root())
        self.assertEqual(len(errors), 1)
        self.assertIn("abs-path-check", errors[0])
        self.assertIn("repo-relative", errors[0])


class UrlCitationTest(unittest.TestCase):
    """URL citations are accepted as-is, checked BEFORE the credential blocklist
    -- an independent review-code pass found the blocklist ran first, silently
    rejecting public URLs whose path merely resembled a credential filename."""

    def test_url_accepted_even_when_path_looks_credential_like(self) -> None:
        node = validate.LoadedNode(
            path=Path("synthetic"),
            id="url-check",
            data={
                "evidence": [
                    {
                        "statement": "x",
                        "entry_class": "FACT",
                        "evidence": [
                            "https://example.com/posts/id_rsa-security-best-practices"
                        ],
                    }
                ]
            },
        )
        errors = validate.find_citation_problems([node], validate.repo_root())
        self.assertEqual(errors, [])


class OwnershipViolationTest(unittest.TestCase):
    def test_stray_non_md_file_rejected_and_named(self) -> None:
        errors = validate.validate_corpus(INVALID_DIR / "misplaced-generated")
        self.assertEqual(len(errors), 1)
        self.assertIn("index.json", errors[0])

    def test_non_md_file_under_generated_is_exempt(self) -> None:
        # Only the reject-outside-generated/ direction was tested before -- this
        # proves the exemption itself has a passing-case fixture, not just that
        # the whole valid/ directory happens to pass for unrelated reasons.
        errors = validate.find_ownership_violations(VALID_DIR)
        self.assertEqual(errors, [])


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
            # errors == [] alone can't distinguish "genuinely empty" from
            # "discovery broke" -- assert zero nodes were found, not merely zero
            # errors, since both would look identical from errors alone.
            self.assertEqual(validate.load_nodes(empty_dir), [])
        finally:
            empty_dir.rmdir()


class SchemaDirExclusionTest(unittest.TestCase):
    """schema/ is #622's own infrastructure, never scanned as corpus content.

    Proven against a purpose-built fixture tree containing BOTH a schema/ file
    and a real sibling, not merely against today's real launchpad/docs/corpus/
    root -- that root currently has zero non-schema content, so a test asserting
    only "no file under schema/ leaked" against it would pass vacuously even if
    exclusion were broadened to reject everything. An independent review-tests
    pass found this.
    """

    def test_sibling_discovered_schema_dir_excluded(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "schema").mkdir()
            real_sibling = root / "real-sibling.md"
            inside_schema = root / "schema" / "inside-schema.md"
            real_sibling.write_text("not real frontmatter, only proving discovery\n")
            inside_schema.write_text("not real frontmatter, only proving exclusion\n")

            files = validate.discover_markdown_files(root)

            self.assertIn(real_sibling, files)
            self.assertNotIn(inside_schema, files)

    def test_real_corpus_root_currently_has_no_content_outside_schema(self) -> None:
        # A documentation-style sanity check on today's real state, not the
        # primary proof of exclusion (see test_sibling_discovered_schema_dir_
        # excluded above, which is the one that can actually fail on regression).
        root = validate.repo_root() / validate.DEFAULT_ROOT
        files = validate.discover_markdown_files(root)
        self.assertEqual(files, [])


if __name__ == "__main__":
    unittest.main()
