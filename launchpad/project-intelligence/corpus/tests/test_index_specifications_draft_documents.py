"""Tests for the specifications-draft-documents builder
(index_defs/specifications_draft_documents.py) -- issue #1303.

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
OUTPUT_REL = "specifications/draft-documents.md"

_NODE_TEMPLATE = """---
id: {node_id}
type: {node_type}
status: {status}
origin: launchpad
audiences:
  - agent
evidence:
  - statement: "This node is a fixture used only by the specifications-draft-documents builder's tests."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/indexes.py"
---

# {node_id}

Fixture node for test_index_specifications_draft_documents.py.
"""


def _write_node(
    corpus_root: Path, rel_path: str, node_id: str, node_type: str, status: str
) -> None:
    path = corpus_root / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        _NODE_TEMPLATE.format(node_id=node_id, node_type=node_type, status=status)
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
            "specifications-draft-documents",
        ]
    )
    if code != 0:
        raise AssertionError(f"generation failed: {err}")
    return (corpus_root / OUTPUT_REL).read_text()


class SpecificationsDraftDocumentsSpecTest(unittest.TestCase):
    def _spec(self):
        by_name = {s.name: s for s in indexes.discover_builders(DEFS_DIR)}
        self.assertIn("specifications-draft-documents", by_name)
        return by_name["specifications-draft-documents"]

    def test_builder_discovered_with_declared_identity(self) -> None:
        spec = self._spec()
        self.assertEqual(spec.output_path, OUTPUT_REL)
        self.assertEqual(spec.node_id, "specifications-draft-documents")
        self.assertEqual(spec.node_type, "governance")


class SpecificationsDraftDocumentsGenerationTest(unittest.TestCase):
    def test_two_runs_are_byte_identical(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_node(
                root,
                "specifications/fixture-draft-spec.md",
                "fixture-draft-spec",
                "interfaces-events",
                "draft",
            )
            first = _generate(root)
            # Regenerate against the same canonical inputs (the output file is
            # excluded from them, so writing it did not change the digest).
            second = _generate(root)
        self.assertEqual(first, second)

    def test_inclusion_requires_both_path_prefix_and_draft_status(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            # Qualifies: in-prefix AND draft.
            _write_node(
                root,
                "specifications/fixture-draft-spec.md",
                "fixture-draft-spec",
                "interfaces-events",
                "draft",
            )
            # In-prefix but not draft -- must be excluded.
            _write_node(
                root,
                "specifications/fixture-active-spec.md",
                "fixture-active-spec",
                "interfaces-events",
                "active",
            )
            # Draft but outside the prefix -- must be excluded.
            _write_node(
                root,
                "architecture/fixture-draft-arch.md",
                "fixture-draft-arch",
                "architecture",
                "draft",
            )
            text = _generate(root)
        self.assertIn("| `fixture-draft-spec` |", text)
        self.assertNotIn("| `fixture-active-spec` |", text)
        self.assertNotIn("| `fixture-draft-arch` |", text)
        self.assertNotIn("No canonical corpus node currently has", text)

    def test_empty_match_renders_honest_empty_listing_with_template_pointer(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_node(
                root,
                "specifications/fixture-active-spec.md",
                "fixture-active-spec",
                "interfaces-events",
                "active",
            )
            _write_node(
                root,
                "architecture/fixture-draft-arch.md",
                "fixture-draft-arch",
                "architecture",
                "draft",
            )
            text = _generate(root)
        self.assertIn("No canonical corpus node currently has", text)
        self.assertIn("specifications/", text)
        self.assertIn("corpus-template-specification", text)
        self.assertNotIn("| `fixture-active-spec` |", text)
        self.assertNotIn("| `fixture-draft-arch` |", text)

    def test_front_matter_carries_node_id_and_type(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_node(
                root,
                "specifications/fixture-draft-spec.md",
                "fixture-draft-spec",
                "interfaces-events",
                "draft",
            )
            text = _generate(root)
        front = text.split("---")[1]
        self.assertIn('id: "specifications-draft-documents"', front)
        self.assertIn('type: "governance"', front)
        self.assertIn("do not edit by hand", text)


if __name__ == "__main__":
    unittest.main()
