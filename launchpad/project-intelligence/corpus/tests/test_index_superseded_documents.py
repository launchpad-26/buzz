"""Tests for the superseded-documents builder
(index_defs/superseded_documents.py) -- issue #1306.

Follows test_index_specifications_index.py's conventions: indexes.py is
loaded by path under the name "corpus_indexes", and every generation happens
into a throwaway corpus built in a temp directory, so the real
launchpad/docs/corpus/ cannot change what these tests assert.
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
OUTPUT_REL = "specifications/superseded-documents.md"

_NODE_TEMPLATE = """---
id: {node_id}
type: {node_type}
status: {status}
origin: launchpad
audiences:
  - agent
evidence:
  - statement: "This node is a fixture used only by the superseded-documents builder's tests."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/indexes.py"
{relationships}---

# {node_id}

Fixture node for test_index_superseded_documents.py.
"""


def _write_node(
    corpus_root: Path,
    rel_path: str,
    node_id: str,
    node_type: str,
    status: str = "active",
    supersedes_target: str | None = None,
) -> None:
    relationships = ""
    if supersedes_target is not None:
        relationships = (
            "relationships:\n"
            "  - type: supersedes\n"
            f"    target: {supersedes_target}\n"
        )
    path = corpus_root / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        _NODE_TEMPLATE.format(
            node_id=node_id,
            node_type=node_type,
            status=status,
            relationships=relationships,
        )
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
            "superseded-documents",
        ]
    )
    if code != 0:
        raise AssertionError(f"generation failed: {err}")
    return (corpus_root / OUTPUT_REL).read_text()


class SupersededDocumentsSpecTest(unittest.TestCase):
    def _spec(self):
        by_name = {s.name: s for s in indexes.discover_builders(DEFS_DIR)}
        self.assertIn("superseded-documents", by_name)
        return by_name["superseded-documents"]

    def test_builder_discovered_with_declared_identity(self) -> None:
        spec = self._spec()
        self.assertEqual(spec.output_path, OUTPUT_REL)
        self.assertEqual(spec.node_id, "specifications-superseded-documents")
        self.assertEqual(spec.node_type, "governance")


class SupersededDocumentsGenerationTest(unittest.TestCase):
    def test_two_runs_are_byte_identical(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_node(
                root,
                "specifications/fixture-old-spec.md",
                "fixture-old-spec",
                "interfaces-events",
            )
            _write_node(
                root,
                "specifications/fixture-new-spec.md",
                "fixture-new-spec",
                "interfaces-events",
                supersedes_target="fixture-old-spec",
            )
            first = _generate(root)
            second = _generate(root)
        self.assertEqual(first, second)

    def test_superseded_node_listed_with_its_superseding_source(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_node(
                root,
                "specifications/fixture-old-spec.md",
                "fixture-old-spec",
                "interfaces-events",
            )
            _write_node(
                root,
                "specifications/fixture-new-spec.md",
                "fixture-new-spec",
                "interfaces-events",
                supersedes_target="fixture-old-spec",
            )
            text = _generate(root)
        # The superseded node appears in the main listing, naming the source
        # of the incoming `superseded-by` edge.
        self.assertIn("fixture-old-spec", text)
        self.assertIn("fixture-new-spec", text)
        main_section = text.split("## Superseded specifications", 1)[1].split(
            "### Signal divergence", 1
        )[0]
        self.assertIn("| `fixture-old-spec` |", main_section)
        self.assertIn("fixture-new-spec", main_section)
        # The superseding node itself (the source of the edge, not its
        # target) is never listed as superseded.
        self.assertNotIn("| `fixture-new-spec` |", main_section)

    def test_node_outside_specifications_prefix_excluded_even_with_edge(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_node(
                root,
                "architecture/fixture-old-arch.md",
                "fixture-old-arch",
                "architecture",
            )
            _write_node(
                root,
                "architecture/fixture-new-arch.md",
                "fixture-new-arch",
                "architecture",
                supersedes_target="fixture-old-arch",
            )
            text = _generate(root)
        self.assertNotIn("fixture-old-arch", text)
        self.assertNotIn("fixture-new-arch", text)
        self.assertIn(
            "No canonical node under `specifications/` currently carries", text
        )

    def test_deprecated_status_with_no_edge_lands_only_in_divergence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_node(
                root,
                "specifications/fixture-deprecated-spec.md",
                "fixture-deprecated-spec",
                "interfaces-events",
                status="deprecated",
            )
            text = _generate(root)
        main_section = text.split("## Superseded specifications", 1)[1].split(
            "### Signal divergence", 1
        )[0]
        divergence_section = text.split("### Signal divergence", 1)[1]
        self.assertNotIn("fixture-deprecated-spec", main_section)
        self.assertIn("fixture-deprecated-spec", divergence_section)
        self.assertIn(
            "**`status` is deprecated/retired, no `superseded-by` edge exists:**",
            text,
        )

    def test_empty_match_renders_honest_empty_listing_and_divergence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_node(
                root,
                "architecture/fixture-arch-node.md",
                "fixture-arch-node",
                "architecture",
            )
            text = _generate(root)
        self.assertIn(
            "No canonical node under `specifications/` currently carries", text
        )
        self.assertIn("None at this revision.", text)
        self.assertNotIn("fixture-arch-node", text)

    def test_front_matter_carries_node_id_and_type(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_node(
                root,
                "specifications/fixture-old-spec.md",
                "fixture-old-spec",
                "interfaces-events",
            )
            text = _generate(root)
        front = text.split("---")[1]
        self.assertIn('id: "specifications-superseded-documents"', front)
        self.assertIn('type: "governance"', front)
        self.assertIn("do not edit by hand", text)


if __name__ == "__main__":
    unittest.main()
