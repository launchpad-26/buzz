"""Tests for the doc-to-code-map builder (index_defs/doc_to_code_map.py) -- #897.

Follows test_index_code_to_doc_map.py's conventions (#888): indexes.py is
loaded by path under the name "corpus_indexes", and every generation happens
into a throwaway corpus built in a temp directory, so the real
launchpad/docs/corpus/ cannot change what these tests assert. This document is
the INVERSE of generated/code-to-doc-map.md -- same (code path, node id)
pairs, regrouped by node id -- so the fixture shapes mirror that sibling test
file's exactly, checking the same inclusion/exclusion rules from the other
side of the pair.
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
OUTPUT_REL = "generated/doc-to-code-map.md"

# A file that exists in this repository, cited by fixtures below.
REAL_PATH = "launchpad/project-intelligence/corpus/indexes.py"

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

Fixture node for test_index_doc_to_code_map.py.
"""


def _write_node(corpus_root: Path, node_id: str, citations: list[str]) -> None:
    entries = []
    for citation in citations:
        entries.append(
            '  - statement: "Fixture claim for the doc-to-code-map tests."\n'
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
            "doc-to-code-map",
        ]
    )
    if code != 0:
        raise AssertionError(f"generation failed: {err}")
    return (corpus_root / OUTPUT_REL).read_text()


class DocToCodeMapSpecTest(unittest.TestCase):
    def _spec(self):
        by_name = {s.name: s for s in indexes.discover_builders(DEFS_DIR)}
        self.assertIn("doc-to-code-map", by_name)
        return by_name["doc-to-code-map"]

    def test_builder_discovered_with_declared_identity(self) -> None:
        spec = self._spec()
        self.assertEqual(spec.output_path, OUTPUT_REL)
        self.assertEqual(spec.node_id, "generated-doc-to-code-map")
        self.assertEqual(spec.node_type, "governance")

    def test_no_implements_edge_toward_index_template(self) -> None:
        # This document is a mapping, not an index -- templates/generated-
        # index.md's own boundary table names doc-to-code-map.md explicitly
        # as such, so it must not declare `implements` toward that template,
        # matching code_to_doc_map.py's own precedent.
        spec = self._spec()
        targets = {rel["target"] for rel in spec.relationships}
        self.assertNotIn("corpus-template-generated-index", targets)
        self.assertEqual(
            spec.relationships, ({"type": "references", "target": "corpus-agents"},)
        )


class DocToCodeMapGenerationTest(unittest.TestCase):
    def test_two_runs_are_byte_identical(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_node(root, "fixture-code-node", [REAL_PATH])
            first = _generate(root)
            second = _generate(root)
        self.assertEqual(first, second)

    def test_resolving_code_citation_becomes_one_pair_row(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_node(root, "fixture-code-node", [REAL_PATH])
            text = _generate(root)
        # Node-first column order: the inverse of code-to-doc-map.md's row.
        self.assertIn(f"| fixture-code-node | `{REAL_PATH}` |", text)

    def test_line_suffixed_citations_collapse_into_one_row(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_node(
                root,
                "fixture-code-node",
                [REAL_PATH, f"{REAL_PATH}:12", f"{REAL_PATH}:12-34"],
            )
            text = _generate(root)
        row = f"| fixture-code-node | `{REAL_PATH}` |"
        self.assertEqual(text.count(row), 1)
        # The suffix is stripped, never listed verbatim.
        self.assertNotIn(f"{REAL_PATH}:12", text)

    def test_non_code_citation_shapes_are_all_excluded(self) -> None:
        excluded = [
            # corpus-internal path (a real file, still excluded by prefix)
            "launchpad/docs/corpus/AGENTS.md",
            # decision-record path (excluded by prefix, existence irrelevant)
            "launchpad/decisions/0001-record-architecture-decisions.md",
            # bare URL
            "https://example.com/some/doc",
            # commit-only ref (whitespace-shaped)
            "commit a44cf52fc740ebebbdd671427480d14f0bce0115",
            # tool-result string
            "grep_recursive('index') -> no generator found",
            # path-shaped but resolves to no real file
            "crates/definitely-not-a-real-crate/src/lib.rs",
        ]
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_node(root, "fixture-noise-node", excluded)
            _write_node(root, "fixture-code-node", [REAL_PATH])
            text = _generate(root)
        mapping = text.split("## Doc-to-code mapping")[1]
        self.assertIn(f"| fixture-code-node | `{REAL_PATH}` |", mapping)
        self.assertNotIn("fixture-noise-node", mapping)
        for citation in excluded:
            self.assertNotIn(f"`{citation}`", mapping)

    def test_multiple_nodes_citing_one_path_each_get_a_row(self) -> None:
        # Node-grouped view: two nodes citing the same file both appear,
        # sorted by node id first.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_node(root, "fixture-node-a", [REAL_PATH])
            _write_node(root, "fixture-node-b", [REAL_PATH])
            text = _generate(root)
        mapping = text.split("## Doc-to-code mapping")[1]
        self.assertIn(f"| fixture-node-a | `{REAL_PATH}` |", mapping)
        self.assertIn(f"| fixture-node-b | `{REAL_PATH}` |", mapping)
        # node id first, so fixture-node-a's row precedes fixture-node-b's.
        self.assertLess(
            mapping.index("fixture-node-a"), mapping.index("fixture-node-b")
        )

    def test_empty_map_renders_honest_empty_message(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_node(root, "fixture-noise-node", ["https://example.com/x"])
            text = _generate(root)
        self.assertIn("This mapping is empty", text)
        self.assertNotIn("| Corpus node id |", text)

    def test_front_matter_carries_node_id_and_type(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_node(root, "fixture-code-node", [REAL_PATH])
            text = _generate(root)
        front = text.split("---")[1]
        self.assertIn('id: "generated-doc-to-code-map"', front)
        self.assertIn('type: "governance"', front)
        self.assertIn("do not edit by hand", text)

    def test_inverse_relationship_to_code_to_doc_map_is_named(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_node(root, "fixture-code-node", [REAL_PATH])
            text = _generate(root)
        self.assertIn("generated/code-to-doc-map.md", text)
        self.assertIn("INVERSE", text)


if __name__ == "__main__":
    unittest.main()
