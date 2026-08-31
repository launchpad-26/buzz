"""Unit tests for the corpus packaging script -- issue #552.

Run:  python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"

Almost every test here points `package_corpus`/`generate_corpus_json` at
fixtures under this directory, following test_validate.py's own rule. ONE
test is the documented exception: `DriftGuardTest` compares the real,
committed `launchpad/crates/knowledge/generated/corpus.json` against a fresh
run over the real corpus root, because that is the only way to guard against
drift between the two -- no fixture can stand in for "the committed artifact
matches what regenerating it right now would produce". This mirrors
test_validate.py's own `test_real_corpus_root_discovery_matches_an_independent_walk`
exception for the identical reason.
"""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"
VALID_DIR = FIXTURES_DIR / "valid"
INVALID_DIR = FIXTURES_DIR / "invalid"

# package.py lives in a directory (project-intelligence/corpus/) that isn't a
# package (no __init__.py, matching this repo's existing project-intelligence/
# convention -- see test_validate.py), so it's loaded by path rather than
# imported by dotted name.
_PACKAGE_PATH = Path(__file__).resolve().parent.parent / "package.py"
_spec = importlib.util.spec_from_file_location("corpus_package", _PACKAGE_PATH)
package = importlib.util.module_from_spec(_spec)
sys.modules["corpus_package"] = package
_spec.loader.exec_module(package)


class PackageFixtureTest(unittest.TestCase):
    def test_valid_fixture_packages_every_node(self) -> None:
        # Same five nodes test_validate.py's ValidFixtureTest counts:
        # node-a, node-b, node-c, node-d, node-e.
        packaged = package.package_corpus(VALID_DIR)
        self.assertEqual(len(packaged), 5)

    def test_packaged_nodes_are_sorted_by_id(self) -> None:
        packaged = package.package_corpus(VALID_DIR)
        ids = [entry["id"] for entry in packaged]
        self.assertEqual(ids, sorted(ids))

    def test_packaged_fields_survive_unchanged_from_the_source_node(self) -> None:
        packaged = package.package_corpus(VALID_DIR)
        node = next(entry for entry in packaged if entry["id"] == "validator-fixture-a")
        self.assertEqual(node["type"], "verification")
        self.assertEqual(node["status"], "active")
        self.assertEqual(node["origin"], "launchpad")
        self.assertEqual(node["audiences"], ["agent"])
        self.assertEqual(len(node["evidence"]), 1)
        self.assertTrue(node["body"].startswith("# Validator fixture A"))

    def test_two_runs_over_unchanged_input_are_byte_identical(self) -> None:
        # The determinism the drift guard depends on: same input, same bytes.
        first = package.generate_corpus_json(VALID_DIR)
        second = package.generate_corpus_json(VALID_DIR)
        self.assertEqual(first, second)


class PackageRefusesInvalidNodesTest(unittest.TestCase):
    def test_a_schema_invalid_node_fails_packaging_rather_than_being_dropped(self) -> None:
        # Packaging must fail closed on a bad node, not silently produce a
        # smaller-than-expected artifact that still looks like a clean pass.
        with self.assertRaises(package.PackagingError) as ctx:
            package.package_corpus(INVALID_DIR / "bad-schema")
        self.assertIn("validator-fixture-bad-schema", str(ctx.exception))

    def test_missing_corpus_root_is_reported_not_packaged_as_empty(self) -> None:
        with self.assertRaises(package.validate.CorpusRootMissing):
            package.package_corpus(FIXTURES_DIR / "does-not-exist-anywhere")


class DriftGuardTest(unittest.TestCase):
    """The committed `launchpad/crates/knowledge/generated/corpus.json` must
    be byte-identical to what a fresh run of the packaging script produces
    from the real corpus root right now -- mirrors the
    `corpus_matches_generated_snapshot` pattern
    `crates/buzz-agent/src/model_capabilities.rs` already uses for
    `scripts/normative-corpus.json`. A corpus change that lands without
    rerunning `just knowledge-package` is caught here, not silently shipped
    stale.
    """

    def test_committed_corpus_json_copies_match_a_fresh_packaging_run(self) -> None:
        # Both committed copies (the knowledge crate's and the desktop
        # Settings panel's) come from the same generation run and must stay
        # byte-identical to each other and to a fresh run -- see step 5's
        # DEFAULT_OUTPUTS.
        repo_root = package.validate.repo_root()
        fresh = package.generate_corpus_json(repo_root / package.DEFAULT_CORPUS_ROOT)
        for relative_output in package.DEFAULT_OUTPUTS:
            committed_path = repo_root / relative_output
            committed = committed_path.read_text()
            self.assertEqual(
                committed,
                fresh,
                f"{relative_output} is out of date -- run `just knowledge-package` "
                "and commit the result",
            )


if __name__ == "__main__":
    unittest.main()
