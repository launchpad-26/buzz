"""Unit tests for the glossary builder (index_defs/glossary.py) -- issue #637.

Run:  python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"

Inclusion-rule behavior is asserted against fixture corpora built in temp
directories, per test_indexes.py's own rule, so real corpus content cannot
change what those tests assert. The committed GLOSSARY.md is touched read-only,
and only for properties the builder's SPEC fixes (id, type, marker) -- never
for digest- or listing-dependent content that shifts whenever any corpus node
changes.
"""

from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

# Same load-by-path pattern as test_indexes.py; reuse the already-loaded module
# when another test file in the same run got there first.
_INDEXES_PATH = Path(__file__).resolve().parent.parent / "indexes.py"
indexes = sys.modules.get("corpus_indexes")
if indexes is None:
    _spec = importlib.util.spec_from_file_location("corpus_indexes", _INDEXES_PATH)
    indexes = importlib.util.module_from_spec(_spec)
    sys.modules["corpus_indexes"] = indexes
    _spec.loader.exec_module(indexes)

REAL_DEFS_DIR = Path(__file__).resolve().parent.parent / "index_defs"
REAL_CORPUS_ROOT = (
    indexes.validate.repo_root() / indexes.validate.DEFAULT_ROOT
)
TEMPLATE_ID = "corpus-template-glossary-term"
EMPTY_SENTENCE = "so the glossary is empty"


def _glossary_spec() -> "indexes.IndexSpec":
    specs = [s for s in indexes.discover_builders(REAL_DEFS_DIR) if s.name == "glossary"]
    assert specs, "glossary builder not discovered"
    return specs[0]


def _write_node(root: Path, rel: str, node_id: str, implements: str | None) -> None:
    lines = [
        "---",
        f"id: {node_id}",
        "type: governance",
        "status: active",
        "origin: launchpad",
        "audiences:",
        "  - agent",
        "evidence:",
        '  - statement: "Fixture node for test_index_glossary.py."',
        "    entry_class: FACT",
        "    evidence:",
        '      - "launchpad/project-intelligence/corpus/indexes.py"',
    ]
    if implements:
        lines += [
            "relationships:",
            "  - type: implements",
            f"    target: {implements}",
        ]
    lines += ["---", "", f"# {node_id}", "", "Fixture body.", ""]
    (root / rel).write_text("\n".join(lines))


class DiscoveryTest(unittest.TestCase):
    def test_glossary_builder_discovered_with_declared_identity(self) -> None:
        spec = _glossary_spec()
        self.assertEqual(spec.output_path, "GLOSSARY.md")
        self.assertEqual(spec.node_id, "corpus-glossary")
        self.assertEqual(spec.node_type, "governance")


class InclusionRuleTest(unittest.TestCase):
    def _render(self, root: Path) -> str:
        spec = _glossary_spec()
        ctx = indexes.build_context(root, [spec])
        return indexes.render_document(spec, ctx)

    def test_node_implementing_the_template_is_listed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_node(root, "glossary-term-template.md", TEMPLATE_ID, None)
            _write_node(root, "term-nip.md", "term-nip", TEMPLATE_ID)
            _write_node(root, "term-relay.md", "term-relay", TEMPLATE_ID)
            _write_node(root, "unrelated.md", "unrelated-node", None)
            text = self._render(root)
        self.assertIn("| term-nip | `term-nip.md`", text)
        self.assertIn("| term-relay | `term-relay.md`", text)
        # Sorted by node id: term-nip before term-relay.
        self.assertLess(text.index("| term-nip |"), text.index("| term-relay |"))
        # Neither the template itself nor a non-implementing node is a row.
        self.assertNotIn(f"| {TEMPLATE_ID} |", text)
        self.assertNotIn("| unrelated-node |", text)
        self.assertNotIn(EMPTY_SENTENCE, text)

    def test_node_implementing_a_different_template_is_not_listed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_node(root, "glossary-term-template.md", TEMPLATE_ID, None)
            _write_node(root, "other-template.md", "other-template", None)
            _write_node(root, "impl-other.md", "impl-other", "other-template")
            text = self._render(root)
        self.assertNotIn("| impl-other |", text)
        self.assertIn(EMPTY_SENTENCE, text)

    def test_empty_match_renders_honest_empty_listing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_node(root, "unrelated.md", "unrelated-node", None)
            text = self._render(root)
        self.assertIn("## Glossary terms", text)
        self.assertIn(EMPTY_SENTENCE, text)
        self.assertIn("exactly 0 canonical corpus node(s)", text)

    def test_output_is_byte_stable_across_two_renders(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_node(root, "glossary-term-template.md", TEMPLATE_ID, None)
            _write_node(root, "term-nip.md", "term-nip", TEMPLATE_ID)
            first = self._render(root)
            second = self._render(root)
        self.assertEqual(first.encode(), second.encode())


class CommittedDocumentTest(unittest.TestCase):
    """Read-only checks on the committed generated file, limited to properties
    the SPEC fixes regardless of corpus content."""

    def test_committed_glossary_front_matter_and_marker(self) -> None:
        text = (REAL_CORPUS_ROOT / "GLOSSARY.md").read_text()
        self.assertIn('id: "corpus-glossary"', text)
        self.assertIn('type: "governance"', text)
        self.assertIn("Generated -- do not edit by hand.", text)


if __name__ == "__main__":
    unittest.main()
