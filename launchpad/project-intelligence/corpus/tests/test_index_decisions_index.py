"""Unit tests for the decisions-index builder (decisions/INDEX.md) -- issue #845.

Run:  python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"

Every test builds its corpus in a temp directory (same rule test_indexes.py
states), so the real launchpad/docs/corpus/ cannot change what they assert.
Discovery tests read the shipped index_defs/ package, which IS this builder's
contract surface; they select the decisions-index SPEC by name so sibling
builders landing in the same package cannot break them.
"""

from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

_INDEXES_PATH = Path(__file__).resolve().parent.parent / "indexes.py"
_spec = importlib.util.spec_from_file_location("corpus_indexes", _INDEXES_PATH)
indexes = importlib.util.module_from_spec(_spec)
sys.modules["corpus_indexes"] = indexes
_spec.loader.exec_module(indexes)

_NODE_TEMPLATE = """---
id: {node_id}
type: governance
status: active
origin: launchpad
audiences:
  - agent
evidence:
  - statement: "Fixture node for the decisions-index builder's own tests."
    entry_class: FACT
    evidence:
      - {citation}
---

# {node_id}

Fixture content.
"""


def _write_node(corpus_root: Path, rel_path: str, node_id: str, citation: str) -> None:
    target = corpus_root / rel_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        _NODE_TEMPLATE.format(node_id=node_id, citation=f'"{citation}"'),
        encoding="utf-8",
    )


def _decisions_spec() -> "indexes.IndexSpec":
    matches = [s for s in indexes.discover_builders() if s.name == "decisions-index"]
    if len(matches) != 1:
        raise AssertionError(
            f"expected exactly one shipped 'decisions-index' builder, found "
            f"{len(matches)}"
        )
    return matches[0]


def _render(corpus_root: Path) -> str:
    spec = _decisions_spec()
    ctx = indexes.build_context(corpus_root, [spec])
    return indexes.render_document(spec, ctx)


class DiscoveryTest(unittest.TestCase):
    def test_shipped_builder_declares_its_identity(self) -> None:
        spec = _decisions_spec()
        self.assertEqual(spec.output_path, "decisions/INDEX.md")
        self.assertEqual(spec.node_id, "decisions-index")
        self.assertEqual(spec.node_type, "governance")
        self.assertIn(
            {"type": "implements", "target": "corpus-template-generated-index"},
            list(spec.relationships),
        )


class InclusionRuleTest(unittest.TestCase):
    def _fixture_corpus(self, tmp: str) -> Path:
        root = Path(tmp) / "corpus"
        root.mkdir()
        # Cites a decision record, with a fragment that must be stripped.
        _write_node(
            root,
            "standards/citing.md",
            "fixture-citing",
            "launchpad/decisions/ADR-9999-fixture.md#L5",
        )
        # Cites nothing under launchpad/decisions/ -- must not be listed.
        _write_node(
            root,
            "standards/non-citing.md",
            "fixture-non-citing",
            "launchpad/other/ADR-0001-elsewhere.md",
        )
        # Cites a decisions/ path that is not .md -- must not be listed.
        _write_node(
            root,
            "standards/non-md.md",
            "fixture-non-md",
            "launchpad/decisions/notes.txt",
        )
        # Lives under the corpus's own decisions/ prefix -- second listing.
        _write_node(
            root,
            "decisions/some-reference.md",
            "fixture-decision-reference",
            "launchpad/project-intelligence/corpus/indexes.py",
        )
        return root

    def test_citing_node_is_listed_under_its_record_without_fragment(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            text = _render(self._fixture_corpus(tmp))
        self.assertIn(
            "| `launchpad/decisions/ADR-9999-fixture.md` | `fixture-citing` |", text
        )
        self.assertNotIn("ADR-9999-fixture.md#L5", text)

    def test_non_matching_citations_create_no_rows(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            text = _render(self._fixture_corpus(tmp))
        records_section = text.split("## Decision records cited by canonical nodes")[1]
        records_section = records_section.split("## Canonical corpus nodes")[0]
        self.assertNotIn("fixture-non-citing", records_section)
        self.assertNotIn("fixture-non-md", records_section)
        self.assertNotIn("notes.txt", records_section)

    def test_corpus_decisions_subtree_node_is_listed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            text = _render(self._fixture_corpus(tmp))
        self.assertIn(
            "| `fixture-decision-reference` | `decisions/some-reference.md` |", text
        )

    def test_empty_matches_render_honest_empty_sections(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "corpus"
            root.mkdir()
            _write_node(
                root,
                "standards/non-citing.md",
                "fixture-non-citing",
                "launchpad/other/ADR-0001-elsewhere.md",
            )
            text = _render(root)
        self.assertIn("0 decision-record path(s)", text)
        self.assertIn(
            "None -- no canonical node's front-matter evidence cites a", text
        )
        self.assertIn(
            "None -- no canonical corpus node lives under the `decisions/` path",
            text,
        )


class DeterminismAndFrontMatterTest(unittest.TestCase):
    def test_two_renders_are_byte_identical(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "corpus"
            root.mkdir()
            _write_node(
                root,
                "standards/citing.md",
                "fixture-citing",
                "launchpad/decisions/ADR-9999-fixture.md",
            )
            first = _render(root)
            second = _render(root)
        self.assertEqual(first.encode(), second.encode())

    def test_front_matter_carries_node_id_and_type(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "corpus"
            root.mkdir()
            _write_node(
                root,
                "standards/citing.md",
                "fixture-citing",
                "launchpad/decisions/ADR-9999-fixture.md",
            )
            text = _render(root)
        self.assertTrue(
            text.startswith('---\nid: "decisions-index"\ntype: "governance"\n')
        )


if __name__ == "__main__":
    unittest.main()
