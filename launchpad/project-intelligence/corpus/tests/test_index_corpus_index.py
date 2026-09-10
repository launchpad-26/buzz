"""Focused tests for the corpus summary builder (index_defs/corpus_index.py) -- #891.

Run:  python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"

Like test_index_index.py, these run against the REAL corpus root and the REAL
shipped index_defs/ package -- the builder's whole job is to summarize the real
corpus -- but strictly read-only: everything renders in memory, nothing is
written to disk. The distinguishing property under test: this document is the
aggregate stats view (counts only) and must never emit a per-node row, because
INDEX.md (node id ``corpus-index``) already owns the full per-node listing.
"""

from __future__ import annotations

import importlib.util
import re
import sys
import unittest
from collections import Counter
from pathlib import Path

_INDEXES_PATH = Path(__file__).resolve().parent.parent / "indexes.py"
_spec = importlib.util.spec_from_file_location("corpus_indexes", _INDEXES_PATH)
indexes = importlib.util.module_from_spec(_spec)
sys.modules["corpus_indexes"] = indexes
_spec.loader.exec_module(indexes)

CORPUS_ROOT = indexes.validate.repo_root() / indexes.validate.DEFAULT_ROOT


def _summary_spec():
    specs = [s for s in indexes.discover_builders() if s.name == "corpus-index"]
    assert len(specs) == 1, "expected exactly one builder named 'corpus-index'"
    return specs[0]


def _table_counts(text: str, heading: str) -> dict[str, int]:
    """Parse the two-column count table under one `### heading` into a dict."""
    section = text.split(f"### {heading}", 1)[1].split("###", 1)[0]
    rows = re.findall(r"^\| (.+?) \| (\d+) \|$", section, flags=re.MULTILINE)
    counts = {key: int(value) for key, value in rows if key not in ("Type", "Status", "Audience", "Directory")}
    return counts


class CorpusSummaryBuilderTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.all_specs = indexes.discover_builders()
        cls.spec = _summary_spec()
        cls.ctx = indexes.build_context(CORPUS_ROOT, cls.all_specs)
        cls.text = indexes.render_document(cls.spec, cls.ctx)

    def test_builder_is_discovered_with_the_contracted_identity(self) -> None:
        self.assertEqual(self.spec.output_path, "generated/corpus-index.md")
        self.assertEqual(self.spec.node_id, "generated-corpus-index")
        self.assertEqual(self.spec.node_type, "governance")
        self.assertEqual(
            self.spec.module_path, indexes.DEFAULT_DEFS_DIR / "corpus_index.py"
        )

    def test_rendered_front_matter_carries_id_and_type(self) -> None:
        self.assertTrue(
            self.text.startswith(
                '---\nid: "generated-corpus-index"\ntype: "governance"\n'
                'status: "draft"\norigin: "launchpad"\n'
            )
        )

    def test_two_independent_renders_are_byte_identical(self) -> None:
        again_ctx = indexes.build_context(CORPUS_ROOT, self.all_specs)
        again = indexes.render_document(self.spec, again_ctx)
        self.assertEqual(self.text, again)

    def test_type_and_status_counts_match_an_independent_recount(self) -> None:
        expected_types = Counter(
            n.data.get("type", "?") for n in self.ctx.valid_nodes
        )
        expected_status = Counter(
            n.data.get("status", "?") for n in self.ctx.valid_nodes
        )
        self.assertEqual(_table_counts(self.text, "Nodes by type"), dict(expected_types))
        self.assertEqual(
            _table_counts(self.text, "Nodes by status"), dict(expected_status)
        )

    def test_audience_counts_match_and_sum_over_node_count(self) -> None:
        expected = Counter(
            a
            for n in self.ctx.valid_nodes
            for a in (n.data.get("audiences") or [])
        )
        rendered = _table_counts(self.text, "Nodes by audience")
        self.assertEqual(rendered, dict(expected))
        # Audiences are multi-valued, so the column must sum past the node count.
        self.assertGreater(sum(rendered.values()), len(self.ctx.valid_nodes))

    def test_directory_counts_sum_to_the_valid_node_count(self) -> None:
        rendered = _table_counts(self.text, "Nodes by top-level directory")
        self.assertEqual(sum(rendered.values()), len(self.ctx.valid_nodes))
        named = [k for k in rendered if k != "(corpus root)"]
        self.assertEqual(named, sorted(named))

    def test_no_per_node_row_ever_appears(self) -> None:
        # The whole point of this document versus INDEX.md: no valid node's id
        # or corpus-root-relative path is emitted anywhere in the body.
        self.assertGreater(len(self.ctx.valid_nodes), 0)
        body = self.text.split("---", 2)[2]  # skip front matter
        for node in self.ctx.valid_nodes:
            self.assertNotIn(f"`{node.id}`", body)
            self.assertNotIn(f"`{self.ctx.rel_path(node)}`", body)

    def test_distinction_from_the_root_index_is_stated_inline(self) -> None:
        self.assertIn("consult `INDEX.md` (node id `corpus-index`)", self.text)
        self.assertIn("aggregate summary", self.text)


if __name__ == "__main__":
    unittest.main()
