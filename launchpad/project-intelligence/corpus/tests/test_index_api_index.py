"""Tests for the api-index builder (index_defs/api_index.py) -- issue #886.

Follows test_indexes.py's conventions: indexes.py is loaded by path under the
name "corpus_indexes", and every generation happens into a throwaway corpus
built in a temp directory, so the real launchpad/docs/corpus/ cannot change
what these tests assert.
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
OUTPUT_REL = "generated/api-index.md"

_NODE_TEMPLATE = """---
id: {node_id}
type: {node_type}
status: active
origin: launchpad
audiences:
  - agent
evidence:
  - statement: "This node is a fixture used only by the api-index builder's tests."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/indexes.py"
---

# {node_id}

Fixture node for test_index_api_index.py.
"""


def _write_node(corpus_root: Path, node_id: str, node_type: str) -> None:
    (corpus_root / f"{node_id}.md").write_text(
        _NODE_TEMPLATE.format(node_id=node_id, node_type=node_type)
    )


def _run_main(argv: list[str]) -> tuple[int, str, str]:
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = indexes.main(argv)
    return code, out.getvalue(), err.getvalue()


def _generate(corpus_root: Path) -> str:
    code, _, err = _run_main(
        ["--root", str(corpus_root), "--defs-dir", str(DEFS_DIR), "--only", "api-index"]
    )
    if code != 0:
        raise AssertionError(f"generation failed: {err}")
    return (corpus_root / OUTPUT_REL).read_text()


class ApiIndexSpecTest(unittest.TestCase):
    def _spec(self):
        by_name = {s.name: s for s in indexes.discover_builders(DEFS_DIR)}
        self.assertIn("api-index", by_name)
        return by_name["api-index"]

    def test_builder_discovered_with_declared_identity(self) -> None:
        spec = self._spec()
        self.assertEqual(spec.output_path, OUTPUT_REL)
        self.assertEqual(spec.node_id, "generated-api-index")
        self.assertEqual(spec.node_type, "interfaces-events")


class ApiIndexGenerationTest(unittest.TestCase):
    def test_two_runs_are_byte_identical(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_node(root, "fixture-iface-node", "interfaces-events")
            first = _generate(root)
            # Regenerate against the same canonical inputs (the output file is
            # excluded from them, so writing it did not change the digest).
            second = _generate(root)
        self.assertEqual(first, second)

    def test_inclusion_rule_selects_only_interfaces_events_nodes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_node(root, "fixture-iface-node", "interfaces-events")
            _write_node(root, "fixture-arch-node", "architecture")
            text = _generate(root)
        self.assertIn("| fixture-iface-node |", text)
        self.assertNotIn("| fixture-arch-node |", text)
        self.assertNotIn("No canonical corpus node currently carries", text)

    def test_empty_match_renders_honest_empty_listing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_node(root, "fixture-arch-node", "architecture")
            text = _generate(root)
        self.assertIn("No canonical corpus node currently carries", text)
        self.assertIn("`type: interfaces-events`", text)
        self.assertNotIn("| fixture-arch-node |", text)

    def test_front_matter_carries_node_id_and_type(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_node(root, "fixture-iface-node", "interfaces-events")
            text = _generate(root)
        front = text.split("---")[1]
        self.assertIn('id: "generated-api-index"', front)
        self.assertIn('type: "interfaces-events"', front)
        self.assertIn("do not edit by hand", text)


if __name__ == "__main__":
    unittest.main()
