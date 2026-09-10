"""Tests for the test-to-doc-map builder (index_defs/test_to_doc_map.py) -- #906.

Follows test_index_doc_to_code_map.py's conventions (#897): indexes.py is
loaded by path under the name "corpus_indexes", and every generation happens
into a throwaway corpus built in a temp directory, so the real
launchpad/docs/corpus/ cannot change what these tests assert. This document
is the TEST-FILTERED SUBSET of generated/code-to-doc-map.md (#888) -- the
same (code path, node id) pairs that document computes, kept only where the
code path is test-shaped -- so these tests check both the base pair
computation (reused, not reimplemented) and this module's own test-path
classifier.
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
OUTPUT_REL = "generated/test-to-doc-map.md"

# A real test-shaped path in this repository (unittest suffix convention).
REAL_TEST_PATH = "launchpad/project-intelligence/corpus/tests/test_validate.py"
# A real path in this repository that is NOT test-shaped.
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

Fixture node for test_index_test_to_doc_map.py.
"""


def _write_node(corpus_root: Path, node_id: str, citations: list[str]) -> None:
    entries = []
    for citation in citations:
        entries.append(
            '  - statement: "Fixture claim for the test-to-doc-map tests."\n'
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
            "test-to-doc-map",
        ]
    )
    if code != 0:
        raise AssertionError(f"generation failed: {err}")
    return (corpus_root / OUTPUT_REL).read_text()


class TestToDocMapSpecTest(unittest.TestCase):
    def _spec(self):
        by_name = {s.name: s for s in indexes.discover_builders(DEFS_DIR)}
        self.assertIn("test-to-doc-map", by_name)
        return by_name["test-to-doc-map"]

    def test_builder_discovered_with_declared_identity(self) -> None:
        spec = self._spec()
        self.assertEqual(spec.output_path, OUTPUT_REL)
        self.assertEqual(spec.node_id, "generated-test-to-doc-map")
        self.assertEqual(spec.node_type, "governance")

    def test_no_implements_edge_toward_index_template(self) -> None:
        # This document is a mapping, not an index -- matching
        # code_to_doc_map.py's and doc_to_code_map.py's own precedent.
        spec = self._spec()
        targets = {rel["target"] for rel in spec.relationships}
        self.assertNotIn("corpus-template-generated-index", targets)
        self.assertEqual(
            spec.relationships, ({"type": "references", "target": "corpus-agents"},)
        )


class TestPathClassifierTest(unittest.TestCase):
    """Direct tests of `_is_test_path`, loaded from the builder module by its
    own fixed path (same pattern the builder itself uses to load
    code_to_doc_map.py)."""

    @classmethod
    def setUpClass(cls) -> None:
        module_path = DEFS_DIR / "test_to_doc_map.py"
        spec = importlib.util.spec_from_file_location(
            "corpus_test_to_doc_map_direct", module_path
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        cls.module = module

    def test_tests_directory_segment_matches(self) -> None:
        self.assertTrue(self.module._is_test_path("crates/foo/tests/bar.rs"))

    def test_singular_test_directory_segment_matches(self) -> None:
        self.assertTrue(self.module._is_test_path("mobile/test/features/x_test.dart"))

    def test_camel_case_test_suffix_directory_matches(self) -> None:
        self.assertTrue(self.module._is_test_path("mobile/ios/RunnerTests/Foo.swift"))
        self.assertTrue(
            self.module._is_test_path("mobile/android/app/src/androidTest/Foo.kt")
        )

    def test_python_test_filename_conventions_match(self) -> None:
        self.assertTrue(self.module._is_test_path("pkg/test_validate.py"))
        self.assertTrue(self.module._is_test_path("pkg/mutation_test.py"))

    def test_js_test_and_spec_filename_conventions_match(self) -> None:
        self.assertTrue(self.module._is_test_path("desktop/src/foo/bar.test.mjs"))
        self.assertTrue(self.module._is_test_path("desktop/tests/e2e/bar.spec.ts"))
        self.assertTrue(self.module._is_test_path("web/src/foo.test.tsx"))

    def test_dart_test_filename_convention_matches(self) -> None:
        self.assertTrue(self.module._is_test_path("mobile/lib/foo/bar_test.dart"))

    def test_latest_directory_segment_is_not_test_shaped(self) -> None:
        # "latest" ends with the substring "test" but is all-lowercase and
        # not equal to "test"/"tests" -- the capital-T rule excludes it.
        self.assertFalse(self.module._is_test_path("releases/latest/notes.md"))

    def test_non_test_path_does_not_match(self) -> None:
        self.assertFalse(self.module._is_test_path(REAL_NON_TEST_PATH))


class TestToDocMapGenerationTest(unittest.TestCase):
    def test_two_runs_are_byte_identical(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_node(root, "fixture-test-node", [REAL_TEST_PATH])
            first = _generate(root)
            second = _generate(root)
        self.assertEqual(first, second)

    def test_test_shaped_citation_becomes_one_pair_row(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_node(root, "fixture-test-node", [REAL_TEST_PATH])
            text = _generate(root)
        self.assertIn(f"| `{REAL_TEST_PATH}` | fixture-test-node |", text)

    def test_non_test_shaped_citation_is_excluded(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_node(root, "fixture-non-test-node", [REAL_NON_TEST_PATH])
            _write_node(root, "fixture-test-node", [REAL_TEST_PATH])
            text = _generate(root)
        mapping = text.split("## Test-to-doc mapping")[1]
        self.assertIn(f"| `{REAL_TEST_PATH}` | fixture-test-node |", mapping)
        self.assertNotIn("fixture-non-test-node", mapping)
        self.assertNotIn(f"`{REAL_NON_TEST_PATH}`", mapping)

    def test_line_suffixed_citations_collapse_into_one_row(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_node(
                root,
                "fixture-test-node",
                [REAL_TEST_PATH, f"{REAL_TEST_PATH}:12", f"{REAL_TEST_PATH}:12-34"],
            )
            text = _generate(root)
        row = f"| `{REAL_TEST_PATH}` | fixture-test-node |"
        self.assertEqual(text.count(row), 1)
        self.assertNotIn(f"{REAL_TEST_PATH}:12", text)

    def test_non_code_citation_shapes_are_all_excluded(self) -> None:
        excluded = [
            "launchpad/docs/corpus/AGENTS.md",
            "launchpad/decisions/0001-record-architecture-decisions.md",
            "https://example.com/some/doc",
            "commit a44cf52fc740ebebbdd671427480d14f0bce0115",
            "grep_recursive('index') -> no generator found",
            "crates/definitely-not-a-real-crate/tests/not_real.rs",
        ]
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_node(root, "fixture-noise-node", excluded)
            _write_node(root, "fixture-test-node", [REAL_TEST_PATH])
            text = _generate(root)
        mapping = text.split("## Test-to-doc mapping")[1]
        self.assertIn(f"| `{REAL_TEST_PATH}` | fixture-test-node |", mapping)
        self.assertNotIn("fixture-noise-node", mapping)
        for citation in excluded:
            self.assertNotIn(f"`{citation}`", mapping)

    def test_empty_map_renders_honest_empty_message(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_node(root, "fixture-non-test-node", [REAL_NON_TEST_PATH])
            text = _generate(root)
        self.assertIn("This mapping is empty", text)
        self.assertNotIn("| Test path |", text)

    def test_front_matter_carries_node_id_and_type(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_node(root, "fixture-test-node", [REAL_TEST_PATH])
            text = _generate(root)
        front = text.split("---")[1]
        self.assertIn('id: "generated-test-to-doc-map"', front)
        self.assertIn('type: "governance"', front)
        self.assertIn("do not edit by hand", text)

    def test_subset_relationship_to_code_to_doc_map_is_named(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_node(root, "fixture-test-node", [REAL_TEST_PATH])
            text = _generate(root)
        self.assertIn("generated/code-to-doc-map.md", text)
        self.assertIn("TEST-FILTERED SUBSET", text)
        self.assertIn("not an independent extraction", text)


if __name__ == "__main__":
    unittest.main()
