"""Tests for the dependency-graph builder (index_defs/dependency_graph.py) -- #896.

Follows test_index_code_to_doc_map.py's conventions: indexes.py is loaded by
path under the name "corpus_indexes", and every generation happens into a
throwaway corpus built in a temp directory, so the real launchpad/docs/corpus/
cannot change what these tests assert. Fixture nodes declare relationships[]
directly -- no filesystem/citation resolution is involved, unlike
code-to-doc-map -- so every fixture is fully self-contained.
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
OUTPUT_REL = "generated/dependency-graph.md"

_NODE_TEMPLATE = """---
id: {node_id}
type: architecture
status: active
origin: launchpad
audiences:
  - agent
evidence:
  - statement: "Fixture node for test_index_dependency_graph.py."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/indexes.py"
{relationships}---

# {node_id}

Fixture node for test_index_dependency_graph.py.
"""


def _write_node(corpus_root: Path, node_id: str, rels: list[tuple[str, str]]) -> None:
    if rels:
        block = "relationships:\n" + "\n".join(
            f"  - type: {rel_type}\n    target: {target}" for rel_type, target in rels
        ) + "\n"
    else:
        block = ""
    (corpus_root / f"{node_id}.md").write_text(
        _NODE_TEMPLATE.format(node_id=node_id, relationships=block)
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
            "dependency-graph",
        ]
    )
    if code != 0:
        raise AssertionError(f"generation failed: {err}")
    return (corpus_root / OUTPUT_REL).read_text()


class DependencyGraphSpecTest(unittest.TestCase):
    def _spec(self):
        by_name = {s.name: s for s in indexes.discover_builders(DEFS_DIR)}
        self.assertIn("dependency-graph", by_name)
        return by_name["dependency-graph"]

    def test_builder_discovered_with_declared_identity(self) -> None:
        spec = self._spec()
        self.assertEqual(spec.output_path, OUTPUT_REL)
        self.assertEqual(spec.node_id, "generated-dependency-graph")
        self.assertEqual(spec.node_type, "governance")
        self.assertEqual(
            spec.relationships, ({"type": "references", "target": "corpus-agents"},)
        )


class DependencyGraphGenerationTest(unittest.TestCase):
    def test_two_runs_are_byte_identical(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_node(root, "fixture-source", [("depends-on", "fixture-target")])
            _write_node(root, "fixture-target", [])
            first = _generate(root)
            second = _generate(root)
        self.assertEqual(first, second)

    def test_forward_edge_row_rendered(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_node(root, "fixture-source", [("depends-on", "fixture-target")])
            _write_node(root, "fixture-target", [])
            text = _generate(root)
        self.assertIn(
            "| fixture-source | depends-on | fixture-target |", text
        )

    def test_multiple_edge_types_from_one_source_all_render(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_node(
                root,
                "fixture-source",
                [("depends-on", "fixture-target"), ("references", "fixture-target")],
            )
            _write_node(root, "fixture-target", [])
            text = _generate(root)
        self.assertIn("| fixture-source | depends-on | fixture-target |", text)
        self.assertIn("| fixture-source | references | fixture-target |", text)

    def test_depends_on_edge_produces_depended_on_by_inverse_row(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_node(root, "fixture-source", [("depends-on", "fixture-target")])
            _write_node(root, "fixture-target", [])
            text = _generate(root)
        inverse_section = text.split("#### `depended-on-by`")[1].split("####")[0]
        self.assertIn("| fixture-target | fixture-source |", inverse_section)

    def test_references_edge_produces_no_referenced_by_inverse_heading(self) -> None:
        # references's inverse (referenced-by) is schema-marked authored, not
        # generated, so the framework never computes it -- no such heading is
        # ever rendered, though the exclusion is named in prose elsewhere.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_node(root, "fixture-source", [("references", "fixture-target")])
            _write_node(root, "fixture-target", [])
            text = _generate(root)
        self.assertNotIn("#### `referenced-by`", text)
        inverse_section = text.split(
            "### Derived inverse edges (generated, not authored)"
        )[1].split("### Broken edges")[0]
        self.assertNotIn("fixture-target | fixture-source", inverse_section)

    def test_broken_edge_reported_never_crashes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_node(
                root, "fixture-source", [("depends-on", "fixture-nonexistent")]
            )
            text = _generate(root)
        broken_section = text.split("### Broken edges")[1].split("### Orphaned")[0]
        self.assertIn(
            "| fixture-source | depends-on | fixture-nonexistent |", broken_section
        )

    def test_broken_edges_empty_message_when_none(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_node(root, "fixture-source", [("depends-on", "fixture-target")])
            _write_node(root, "fixture-target", [])
            text = _generate(root)
        broken_section = text.split("### Broken edges")[1].split("### Orphaned")[0]
        self.assertIn("None at this revision", broken_section)

    def test_orphaned_node_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_node(root, "fixture-source", [("depends-on", "fixture-target")])
            _write_node(root, "fixture-target", [])
            _write_node(root, "fixture-lonely", [])
            text = _generate(root)
        orphan_section = text.split("### Orphaned nodes")[1].split("## Relationships")[0]
        self.assertIn("fixture-lonely", orphan_section)
        self.assertNotIn("fixture-source", orphan_section)
        self.assertNotIn("fixture-target", orphan_section)

    def test_orphaned_nodes_empty_message_when_none(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_node(root, "fixture-source", [("depends-on", "fixture-target")])
            _write_node(root, "fixture-target", [])
            text = _generate(root)
        orphan_section = text.split("### Orphaned nodes")[1].split("## Relationships")[0]
        self.assertIn("None at this revision", orphan_section)

    def test_front_matter_carries_node_id_and_type(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_node(root, "fixture-source", [("depends-on", "fixture-target")])
            _write_node(root, "fixture-target", [])
            text = _generate(root)
        front = text.split("---")[1]
        self.assertIn('id: "generated-dependency-graph"', front)
        self.assertIn('type: "governance"', front)
        self.assertIn("do not edit by hand", text)


if __name__ == "__main__":
    unittest.main()
