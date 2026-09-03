"""Focused tests for the corpus root index builder (index_defs/index.py) -- #638.

Run:  python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"

Unlike test_indexes.py's fixture-rooted framework tests, these deliberately run
against the REAL corpus root and the REAL shipped index_defs/ package -- the
builder's whole job is to index the real corpus -- but strictly read-only:
everything renders in memory, nothing is written to disk.
"""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

_INDEXES_PATH = Path(__file__).resolve().parent.parent / "indexes.py"
_spec = importlib.util.spec_from_file_location("corpus_indexes", _INDEXES_PATH)
indexes = importlib.util.module_from_spec(_spec)
sys.modules["corpus_indexes"] = indexes
_spec.loader.exec_module(indexes)

CORPUS_ROOT = indexes.validate.repo_root() / indexes.validate.DEFAULT_ROOT


def _index_spec():
    specs = [s for s in indexes.discover_builders() if s.name == "index"]
    assert len(specs) == 1, "expected exactly one builder named 'index'"
    return specs[0]


class IndexBuilderTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.all_specs = indexes.discover_builders()
        cls.spec = _index_spec()
        cls.ctx = indexes.build_context(CORPUS_ROOT, cls.all_specs)
        cls.text = indexes.render_document(cls.spec, cls.ctx)

    def test_builder_is_discovered_with_the_contracted_identity(self) -> None:
        self.assertEqual(self.spec.output_path, "INDEX.md")
        self.assertEqual(self.spec.node_id, "corpus-index")
        self.assertEqual(self.spec.node_type, "governance")
        self.assertEqual(
            self.spec.module_path, indexes.DEFAULT_DEFS_DIR / "index.py"
        )

    def test_rendered_front_matter_carries_id_and_type(self) -> None:
        self.assertTrue(
            self.text.startswith(
                '---\nid: "corpus-index"\ntype: "governance"\n'
                'status: "draft"\norigin: "launchpad"\n'
            )
        )

    def test_two_independent_renders_are_byte_identical(self) -> None:
        again_ctx = indexes.build_context(CORPUS_ROOT, self.all_specs)
        again = indexes.render_document(self.spec, again_ctx)
        self.assertEqual(self.text, again)

    def test_every_valid_canonical_node_is_listed(self) -> None:
        # The root index's inclusion rule is total: every valid node's id and
        # corpus-root-relative path appear as a listing row.
        self.assertGreater(len(self.ctx.valid_nodes), 0)
        for node in self.ctx.valid_nodes:
            row_start = f"| `{node.id}` |"
            self.assertIn(row_start, self.text)
            self.assertIn(f"| `{self.ctx.rel_path(node)}` |", self.text)

    def test_no_registered_output_is_listed_as_a_canonical_row(self) -> None:
        # Generated outputs are excluded from the canonical inputs, so none of
        # them (including INDEX.md itself) may appear as a table row.
        for output in self.ctx.output_paths:
            self.assertNotIn(f"| `{output}` |", self.text)
        self.assertNotIn("corpus-index", self.ctx.node_ids)

    def test_groups_are_root_first_then_sorted_directories(self) -> None:
        headings = [
            line for line in self.text.splitlines() if line.startswith("### ")
        ]
        named = [h for h in headings if not h.startswith("### Discovered")]
        self.assertTrue(named[0].startswith("### Corpus root"))
        dir_names = [h.split("`")[1] for h in named[1:]]
        self.assertEqual(dir_names, sorted(dir_names))
        self.assertGreater(len(dir_names), 0)


if __name__ == "__main__":
    unittest.main()
