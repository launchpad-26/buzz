"""Tests for the test-index builder (index_defs/test_index.py) -- #905.

Follows test_indexes.py's conventions: indexes.py is loaded by path under the
name "corpus_indexes", and every generation happens into a throwaway corpus
built in a temp directory, so the real launchpad/docs/corpus/ cannot change
what these tests assert. The builder resolves cited paths against the real
repository root (validate.repo_root()), same as code_to_doc_map.py/
crate_index.py, so fixtures cite real repo files to exercise both the
citation classifier and the test-path-matching pattern.
"""

from __future__ import annotations

import contextlib
import importlib.util
import io
import sys
import tempfile
import unittest
from pathlib import Path

_INDEXES_PATH = Path(__file__).resolve().parent.parent / "indexes.py"
_spec = importlib.util.spec_from_file_location("corpus_indexes", _INDEXES_PATH)
indexes = importlib.util.module_from_spec(_spec)
sys.modules["corpus_indexes"] = indexes
_spec.loader.exec_module(indexes)

DEFS_DIR = Path(__file__).resolve().parent.parent / "index_defs"
OUTPUT_REL = "generated/test-index.md"

# Real repository files, cited by fixtures below.
# A real test file: lives directly under a `tests/` directory AND matches
# `test_*` -- exercises both halves of the pattern at once.
REAL_TEST_PATH = "launchpad/project-intelligence/corpus/tests/test_indexes.py"
# A real test file matching only the `*.test.*` filename pattern (no `tests/`
# directory component in its path).
REAL_DOTTED_TEST_PATH = (
    "desktop/src/features/presence/lib/presence.test.mjs"
)
# A real, ordinary (non-test) source file for negative-path coverage.
REAL_NON_TEST_PATH = "launchpad/project-intelligence/corpus/indexes.py"

_NODE_TEMPLATE = """---
id: {node_id}
type: architecture
status: active
origin: launchpad
audiences:
  - agent
evidence:
{evidence}
---

# {node_id}

Fixture node for test_index_test_index.py.
"""


def _write_node(corpus_root: Path, node_id: str, citations: list[str]) -> None:
    entries = []
    for citation in citations:
        entries.append(
            '  - statement: "Fixture claim for the test-index tests."\n'
            "    entry_class: FACT\n"
            "    evidence:\n"
            f'      - "{citation}"'
        )
    (corpus_root / f"{node_id}.md").write_text(
        _NODE_TEMPLATE.format(node_id=node_id, evidence="\n".join(entries))
    )


def _run_main(argv: list[str]) -> tuple[int, str, str]:
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = indexes.main(argv)
    return code, out.getvalue(), err.getvalue()


def _generate(corpus_root: Path) -> str:
    code, _, err = _run_main(
        [
            "--root",
            str(corpus_root),
            "--defs-dir",
            str(DEFS_DIR),
            "--only",
            "test-index",
        ]
    )
    if code != 0:
        raise AssertionError(f"generation failed: {err}")
    return (corpus_root / OUTPUT_REL).read_text()


class TestIndexSpecTest(unittest.TestCase):
    def _spec(self):
        by_name = {s.name: s for s in indexes.discover_builders(DEFS_DIR)}
        self.assertIn("test-index", by_name)
        return by_name["test-index"]

    def test_builder_discovered_with_declared_identity(self) -> None:
        spec = self._spec()
        self.assertEqual(spec.output_path, OUTPUT_REL)
        self.assertEqual(spec.node_id, "generated-test-index")
        self.assertEqual(spec.node_type, "governance")


class TestIndexPathPredicateTest(unittest.TestCase):
    """Direct unit coverage of the path-pattern predicate itself, independent
    of citation resolution -- the pattern is stated in prose in the module
    docstring and the generated document; this locks the executable form to
    that prose."""

    def setUp(self) -> None:
        module_name = "corpus_index_def_test_index"
        module_path = DEFS_DIR / "test_index.py"
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        self.builder = module

    def test_tests_directory_component_matches_regardless_of_filename(self) -> None:
        self.assertTrue(self.builder._is_test_path("crates/buzz-search/tests/fts_integration.rs"))
        self.assertTrue(self.builder._is_test_path("desktop/tests/e2e/channel-mute.spec.ts"))

    def test_filename_patterns_match_without_a_tests_directory(self) -> None:
        self.assertTrue(self.builder._is_test_path("desktop/src/features/presence/lib/presence.test.mjs"))
        self.assertTrue(self.builder._is_test_path("mobile/test/features/profile/user_status_provider_test.dart"))
        self.assertTrue(self.builder._is_test_path("docs/formal/nip-pl/mutation_test.py"))
        self.assertTrue(self.builder._is_test_path("scripts/test_something.py"))

    def test_singular_test_directory_alone_does_not_match(self) -> None:
        # A `test` (singular) directory component with a filename that fails
        # both filename patterns is deliberately NOT a test path -- only the
        # plural `tests` directory name and the three filename patterns
        # count, per the stated rule.
        self.assertFalse(self.builder._is_test_path("mobile/test/fixtures/sample_data.json"))

    def test_ordinary_source_path_does_not_match(self) -> None:
        self.assertFalse(self.builder._is_test_path("crates/buzz-core/src/kind.rs"))
        self.assertFalse(self.builder._is_test_path("crates/buzz-relay/src/authority.rs"))


class TestIndexGenerationTest(unittest.TestCase):
    def test_two_runs_are_byte_identical(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_node(root, "fixture-test-node", [REAL_TEST_PATH])
            first = _generate(root)
            second = _generate(root)
        self.assertEqual(first, second)

    def test_tests_directory_citation_becomes_a_row(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_node(root, "fixture-test-node", [REAL_TEST_PATH])
            text = _generate(root)
        row = next(
            line
            for line in text.splitlines()
            if line.startswith(f"| `{REAL_TEST_PATH}` |")
        )
        self.assertIn("fixture-test-node", row)

    def test_dotted_test_filename_citation_becomes_a_row(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_node(root, "fixture-dotted-node", [REAL_DOTTED_TEST_PATH])
            text = _generate(root)
        row = next(
            line
            for line in text.splitlines()
            if line.startswith(f"| `{REAL_DOTTED_TEST_PATH}` |")
        )
        self.assertIn("fixture-dotted-node", row)

    def test_non_test_source_citation_is_excluded(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_node(root, "fixture-source-node", [REAL_NON_TEST_PATH])
            text = _generate(root)
        mapping = text.split("## Test index")[1]
        self.assertNotIn("fixture-source-node", mapping)
        self.assertNotIn(f"`{REAL_NON_TEST_PATH}`", mapping)

    def test_line_suffixed_citations_collapse_to_one_row(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_node(
                root,
                "fixture-test-node",
                [REAL_TEST_PATH, f"{REAL_TEST_PATH}:12", f"{REAL_TEST_PATH}:12-34"],
            )
            text = _generate(root)
        row = next(
            line
            for line in text.splitlines()
            if line.startswith(f"| `{REAL_TEST_PATH}` |")
        )
        self.assertEqual(row.count("fixture-test-node"), 1)

    def test_multiple_citing_nodes_are_listed_sorted(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_node(root, "fixture-node-b", [REAL_TEST_PATH])
            _write_node(root, "fixture-node-a", [REAL_TEST_PATH])
            text = _generate(root)
        row = next(
            line
            for line in text.splitlines()
            if line.startswith(f"| `{REAL_TEST_PATH}` |")
        )
        self.assertIn("fixture-node-a, fixture-node-b", row)

    def test_non_test_citation_shapes_are_all_excluded(self) -> None:
        excluded = [
            # resolves to a real file, but not test-shaped
            REAL_NON_TEST_PATH,
            # bare URL
            "https://example.com/some/doc",
            # commit-only ref (whitespace-shaped)
            "commit a44cf52fc740ebebbdd671427480d14f0bce0115",
            # tool-result string
            "grep_recursive('index') -> no generator found",
            # path-shaped but resolves to no real file
            "crates/definitely-not-a-real-crate/tests/test_missing.rs",
        ]
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_node(root, "fixture-noise-node", excluded)
            text = _generate(root)
        mapping = text.split("## Test index")[1]
        self.assertNotIn("fixture-noise-node", mapping)

    def test_empty_index_renders_honest_empty_message(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_node(root, "fixture-noise-node", ["https://example.com/x"])
            text = _generate(root)
        self.assertIn("This index is empty", text)
        self.assertNotIn("| Test path |", text)

    def test_front_matter_carries_node_id_and_type(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            text = _generate(root)
        front = text.split("---")[1]
        self.assertIn('id: "generated-test-index"', front)
        self.assertIn('type: "governance"', front)
        self.assertIn("do not edit by hand", text)


if __name__ == "__main__":
    unittest.main()
