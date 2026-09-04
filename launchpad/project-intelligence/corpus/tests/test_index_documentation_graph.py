"""Tests for the documentation-graph builder (index_defs/documentation_graph.py)
-- #898.

Follows test_index_dependency_graph.py's conventions: indexes.py is loaded by
path under the name "corpus_indexes", and every generation happens into a
throwaway corpus built in a temp directory, so the real launchpad/docs/corpus/
cannot change what these tests assert. Fixture nodes declare relationships[]
directly -- no filesystem/citation resolution is involved -- so every fixture
is fully self-contained.
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
OUTPUT_REL = "generated/documentation-graph.md"

_NODE_TEMPLATE = """---
id: {node_id}
type: architecture
status: active
origin: launchpad
audiences:
  - agent
evidence:
  - statement: "Fixture node for test_index_documentation_graph.py."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/indexes.py"
{relationships}---

# {node_id}

Fixture node for test_index_documentation_graph.py.
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
            "documentation-graph",
        ]
    )
    if code != 0:
        raise AssertionError(f"generation failed: {err}")
    return (corpus_root / OUTPUT_REL).read_text()


class DocumentationGraphSpecTest(unittest.TestCase):
    def _spec(self):
        by_name = {s.name: s for s in indexes.discover_builders(DEFS_DIR)}
        self.assertIn("documentation-graph", by_name)
        return by_name["documentation-graph"]

    def test_builder_discovered_with_declared_identity(self) -> None:
        spec = self._spec()
        self.assertEqual(spec.output_path, OUTPUT_REL)
        self.assertEqual(spec.node_id, "generated-documentation-graph")
        self.assertEqual(spec.node_type, "governance")
        self.assertEqual(
            spec.relationships, ({"type": "references", "target": "corpus-agents"},)
        )


class DocumentationGraphGenerationTest(unittest.TestCase):
    def test_two_runs_are_byte_identical(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_node(root, "fixture-hub", [])
            _write_node(root, "fixture-source-a", [("references", "fixture-hub")])
            _write_node(root, "fixture-source-b", [("depends-on", "fixture-hub")])
            first = _generate(root)
            second = _generate(root)
        self.assertEqual(first, second)

    def test_hub_ranked_above_lower_degree_node(self) -> None:
        # fixture-hub is targeted by two distinct sources (in-degree 2) while
        # fixture-lone-source declares one outgoing edge to a third node
        # (out-degree 1). The hub table must rank total_degree 2 above
        # total_degree 1, by (-total_degree, node_id).
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_node(root, "fixture-hub", [])
            _write_node(root, "fixture-source-a", [("references", "fixture-hub")])
            _write_node(root, "fixture-source-b", [("depends-on", "fixture-hub")])
            _write_node(root, "fixture-minor-target", [])
            _write_node(
                root, "fixture-lone-source", [("implements", "fixture-minor-target")]
            )
            text = _generate(root)
        hub_section = text.split("## Hub nodes (highest total degree)")[1].split(
            "## Leaf nodes"
        )[0]
        hub_row = "| fixture-hub | `fixture-hub.md` | 2 | 0 | 2 |"
        lone_source_row = "| fixture-lone-source | `fixture-lone-source.md` | 0 | 1 | 1 |"
        self.assertIn(hub_row, hub_section)
        self.assertIn(lone_source_row, hub_section)
        self.assertLess(
            hub_section.index(hub_row), hub_section.index(lone_source_row)
        )

    def test_mixed_edge_types_all_count_toward_degree(self) -> None:
        # references and depends-on both target fixture-hub; degree counts
        # every forward edge regardless of relationship type.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_node(root, "fixture-hub", [])
            _write_node(root, "fixture-source-a", [("references", "fixture-hub")])
            _write_node(root, "fixture-source-b", [("depends-on", "fixture-hub")])
            text = _generate(root)
        self.assertIn("| fixture-hub | `fixture-hub.md` | 2 | 0 | 2 |", text)

    def test_zero_degree_node_counted_not_itemized(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_node(root, "fixture-hub", [])
            _write_node(root, "fixture-source-a", [("references", "fixture-hub")])
            _write_node(root, "fixture-lonely", [])
            text = _generate(root)
        leaf_section = text.split("## Leaf nodes (zero degree)")[1].split(
            "## Relationships"
        )[0]
        self.assertIn("1 valid canonical node(s) have total degree zero", leaf_section)
        # Not itemized: the leaf node's own id/path is not rendered as a row.
        self.assertNotIn("fixture-lonely.md", leaf_section)
        hub_section = text.split("## Hub nodes (highest total degree)")[1].split(
            "## Leaf nodes"
        )[0]
        self.assertNotIn("fixture-lonely", hub_section)

    def test_empty_hub_table_message_when_no_edges(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_node(root, "fixture-isolated", [])
            text = _generate(root)
        hub_section = text.split("## Hub nodes (highest total degree)")[1].split(
            "## Leaf nodes"
        )[0]
        self.assertIn("None at this revision", hub_section)

    def test_distinction_section_names_both_documents(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_node(root, "fixture-hub", [])
            _write_node(root, "fixture-source-a", [("references", "fixture-hub")])
            text = _generate(root)
        distinction = text.split("## Distinction from `generated/dependency-graph.md`")[
            1
        ].split("## Connectivity summary")[0]
        self.assertIn("dependency-graph.md", distinction)
        self.assertIn(
            "renders them at a different granularity", distinction
        )

    def test_front_matter_carries_node_id_and_type(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_node(root, "fixture-hub", [])
            _write_node(root, "fixture-source-a", [("references", "fixture-hub")])
            text = _generate(root)
        front = text.split("---")[1]
        self.assertIn('id: "generated-documentation-graph"', front)
        self.assertIn('type: "governance"', front)
        self.assertIn("do not edit by hand", text)


if __name__ == "__main__":
    unittest.main()
