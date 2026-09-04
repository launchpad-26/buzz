"""Focused tests for the orphaned-docs builder -- issue #902.

Follows test_index_dependency_graph.py's fixture-node pattern (front-matter
`relationships[]` written directly, no filesystem/citation resolution needed
for the orphan/connected distinction) and test_index_coverage.py's
fixture-repo-root pattern (a temp root whose corpus lives under
`<root>/launchpad/docs/corpus/`, so this builder's repo-root derivation for
`coverage.py` resolves the fixture, never the real repository). Every
behavioral test builds its own throwaway fixture tree; two read-only smoke
tests touch the real committed document.
"""

from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

_INDEXES_PATH = Path(__file__).resolve().parent.parent / "indexes.py"
indexes = sys.modules.get("corpus_indexes")
if indexes is None:
    _spec = importlib.util.spec_from_file_location("corpus_indexes", _INDEXES_PATH)
    indexes = importlib.util.module_from_spec(_spec)
    sys.modules["corpus_indexes"] = indexes
    _spec.loader.exec_module(indexes)

BUILDER_NAME = "orphaned-docs"
OUTPUT_REL = "generated/orphaned-docs.md"
NODE_ID = "generated-orphaned-docs"
REAL_CORPUS = indexes.validate.repo_root() / indexes.validate.DEFAULT_ROOT


def _write(root: Path, rel: str, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _node_text(
    node_id: str,
    node_type: str,
    citations: list[str],
    relationships: list[tuple[str, str]] | None = None,
) -> str:
    # One evidence ENTRY per citation -- `len(node.data["evidence"])` (what
    # orphaned_docs.py's median/thinness computation actually counts) is the
    # number of entries in the list, not the number of citation strings
    # nested inside a single entry's own `evidence: [...]` array.
    entries = "\n".join(
        f'  - statement: "Fixture node for test_index_orphaned_docs.py."\n'
        f"    entry_class: FACT\n"
        f"    evidence:\n"
        f'      - "{citation}"'
        for citation in citations
    )
    rel_block = ""
    if relationships:
        rel_block = "relationships:\n" + "\n".join(
            f"  - type: {rel_type}\n    target: {target}"
            for rel_type, target in relationships
        ) + "\n"
    return (
        "---\n"
        f"id: {node_id}\n"
        f"type: {node_type}\n"
        "status: active\n"
        "origin: launchpad\n"
        "audiences:\n"
        "  - agent\n"
        "evidence:\n"
        f"{entries}\n"
        f"{rel_block}"
        "---\n\n"
        f"# {node_id}\n"
    )


def _spec_for_builder():
    specs = indexes.discover_builders()
    by_name = {s.name: s for s in specs}
    return by_name.get(BUILDER_NAME), specs


def _render_fixture(corpus_root: Path) -> str:
    spec, specs = _spec_for_builder()
    ctx = indexes.build_context(corpus_root, specs)
    return indexes.render_document(spec, ctx)


class DiscoveryTest(unittest.TestCase):
    def test_builder_discovered_with_expected_identity(self) -> None:
        spec, _ = _spec_for_builder()
        self.assertIsNotNone(spec, "orphaned-docs builder not discovered")
        self.assertEqual(spec.output_path, OUTPUT_REL)
        self.assertEqual(spec.node_id, NODE_ID)
        self.assertEqual(spec.node_type, "governance")
        self.assertEqual(
            spec.relationships, ({"type": "references", "target": "corpus-agents"},)
        )
        # Not index-shaped -- the template itself names this document an
        # audit report, so it must not declare implements toward the
        # generated-index template.
        self.assertNotIn(
            {"type": "implements", "target": "corpus-template-generated-index"},
            list(spec.relationships),
        )


class FixtureCorpusTest(unittest.TestCase):
    """A fixture repo with:
    - fixture-connected -> fixture-target (a real edge, both NOT orphans)
    - audit/fixture-orphan-covered: orphan, cites migrations/0001_init.sql
      (earns coverage), 3 evidence entries
    - audit/fixture-orphan-uncovered: orphan, cites nothing in the fixture
      inventory (doubly disconnected), 3 evidence entries
    - audit/fixture-orphan-thin: orphan, cites migrations/0001_init.sql
      (earns coverage too), but only 1 evidence entry -- below the
      corpus-wide median of the other four nodes' 3-entry count.
    """

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        root = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)
        self.root = root
        self.corpus = root / "launchpad" / "docs" / "corpus"

        _write(root, "migrations/0001_init.sql", "CREATE TABLE demo ();\n")

        _write(
            root,
            "launchpad/docs/corpus/fixture-connected.md",
            _node_text(
                "fixture-connected",
                "architecture",
                [
                    "launchpad/project-intelligence/corpus/indexes.py",
                    "launchpad/project-intelligence/corpus/indexes.py",
                    "launchpad/project-intelligence/corpus/indexes.py",
                ],
                relationships=[("references", "fixture-target")],
            ),
        )
        _write(
            root,
            "launchpad/docs/corpus/fixture-target.md",
            _node_text(
                "fixture-target",
                "architecture",
                [
                    "launchpad/project-intelligence/corpus/indexes.py",
                    "launchpad/project-intelligence/corpus/indexes.py",
                    "launchpad/project-intelligence/corpus/indexes.py",
                ],
            ),
        )
        _write(
            root,
            "launchpad/docs/corpus/audit/fixture-orphan-covered.md",
            _node_text(
                "fixture-orphan-covered",
                "governance",
                [
                    "migrations/0001_init.sql",
                    "launchpad/project-intelligence/corpus/indexes.py",
                    "launchpad/project-intelligence/corpus/indexes.py",
                ],
            ),
        )
        _write(
            root,
            "launchpad/docs/corpus/audit/fixture-orphan-uncovered.md",
            _node_text(
                "fixture-orphan-uncovered",
                "governance",
                [
                    "launchpad/project-intelligence/corpus/indexes.py",
                    "launchpad/project-intelligence/corpus/indexes.py",
                    "launchpad/project-intelligence/corpus/indexes.py",
                ],
            ),
        )
        _write(
            root,
            "launchpad/docs/corpus/audit/fixture-orphan-thin.md",
            _node_text(
                "fixture-orphan-thin",
                "governance",
                ["migrations/0001_init.sql"],
            ),
        )

    def test_connected_nodes_excluded_orphans_listed(self) -> None:
        text = _render_fixture(self.corpus)
        orphan_section = text.split("### Orphaned nodes", 1)[1].split(
            "### Concentration"
        )[0]
        self.assertNotIn("fixture-connected", orphan_section)
        self.assertNotIn("| fixture-target |", orphan_section)
        self.assertIn("fixture-orphan-covered", orphan_section)
        self.assertIn("fixture-orphan-uncovered", orphan_section)
        self.assertIn("fixture-orphan-thin", orphan_section)

    def test_concentration_grouped_by_directory_and_type(self) -> None:
        text = _render_fixture(self.corpus)
        concentration = text.split("### Concentration", 1)[1].split(
            "### Coverage cross-reference"
        )[0]
        self.assertIn("| `audit` | 3 |", concentration)
        self.assertIn("| governance | 3 |", concentration)

    def test_coverage_cross_reference_splits_earning_and_disconnected(self) -> None:
        text = _render_fixture(self.corpus)
        cross_ref = text.split("### Coverage cross-reference", 1)[1].split(
            "### Evidence thinness"
        )[0]
        earning_section = cross_ref.split("#### Earns coverage despite no corpus edge", 1)[
            1
        ].split("#### Doubly disconnected")[0]
        disconnected_section = cross_ref.split("#### Doubly disconnected", 1)[1]

        self.assertIn("fixture-orphan-covered", earning_section)
        self.assertIn("fixture-orphan-thin", earning_section)
        self.assertNotIn("fixture-orphan-uncovered", earning_section)

        self.assertIn("fixture-orphan-uncovered", disconnected_section)
        self.assertNotIn("fixture-orphan-covered", disconnected_section)
        self.assertNotIn("fixture-orphan-thin", disconnected_section)

        self.assertIn("**2 of 3** orphaned node(s) earn at least one coverage row", text)
        self.assertIn("**1** earn none (doubly disconnected)", text)

    def test_evidence_thinness_flags_below_median_only(self) -> None:
        text = _render_fixture(self.corpus)
        thinness = text.split("### Evidence thinness", 1)[1].split("## Relationships")[0]
        self.assertIn("median evidence entry count at this revision: **3**", thinness)
        self.assertIn("fixture-orphan-thin", thinness)
        self.assertNotIn("fixture-orphan-covered", thinness)
        self.assertNotIn("fixture-orphan-uncovered", thinness)

    def test_distinction_from_dependency_graph_stated_in_body(self) -> None:
        text = _render_fixture(self.corpus)
        self.assertIn(
            "## Distinction from `generated/dependency-graph.md`", text
        )
        self.assertIn("generated-dependency-graph", text)
        self.assertIn("does not repeat that list for its own sake", text)

    def test_output_stable_across_two_renders(self) -> None:
        self.assertEqual(_render_fixture(self.corpus), _render_fixture(self.corpus))

    def test_front_matter_carries_node_id_and_type(self) -> None:
        text = _render_fixture(self.corpus)
        self.assertTrue(text.startswith(f'---\nid: "{NODE_ID}"\ntype: "governance"\n'))
        self.assertIn("do not edit by hand", text)


class EmptyCorpusTest(unittest.TestCase):
    def test_no_orphans_renders_honest_empty_state(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            corpus = root / "launchpad" / "docs" / "corpus"
            _write(
                root,
                "launchpad/docs/corpus/fixture-connected.md",
                _node_text(
                    "fixture-connected",
                    "architecture",
                    ["launchpad/project-intelligence/corpus/indexes.py"],
                    relationships=[("references", "fixture-target")],
                ),
            )
            _write(
                root,
                "launchpad/docs/corpus/fixture-target.md",
                _node_text(
                    "fixture-target",
                    "architecture",
                    ["launchpad/project-intelligence/corpus/indexes.py"],
                ),
            )
            text = _render_fixture(corpus)
        orphan_section = text.split("### Orphaned nodes", 1)[1].split(
            "### Concentration"
        )[0]
        self.assertIn("None at this revision", orphan_section)
        cross_ref = text.split("### Coverage cross-reference", 1)[1].split(
            "### Evidence thinness"
        )[0]
        self.assertIn(
            "**0 of 0** orphaned node(s) earn at least one coverage row", text
        )
        self.assertIn(
            "None at this revision -- no orphaned node earns a coverage row.",
            cross_ref,
        )
        self.assertIn(
            "None at this revision -- every orphaned node earns at least "
            "one coverage row.",
            cross_ref,
        )
        thinness = text.split("### Evidence thinness", 1)[1].split("## Relationships")[0]
        self.assertIn(
            "None at this revision -- no orphaned node's evidence entry "
            "count falls below the corpus-wide median.",
            thinness,
        )


class RealCorpusSmokeTest(unittest.TestCase):
    """Read-only checks against the committed generated document."""

    def test_committed_document_identity_and_marker(self) -> None:
        target = REAL_CORPUS / OUTPUT_REL
        self.assertTrue(target.is_file(), f"{OUTPUT_REL} missing on disk")
        text = target.read_text(encoding="utf-8")
        front_matter = text.split("---\n")[1]
        self.assertIn(f'id: "{NODE_ID}"', front_matter)
        self.assertIn('type: "governance"', front_matter)
        self.assertIn("**Generated -- do not edit by hand.**", text)
        self.assertIn("## Distinction from `generated/dependency-graph.md`", text)
        self.assertIn("### Concentration", text)
        self.assertIn("### Coverage cross-reference", text)
        self.assertIn("### Evidence thinness", text)


if __name__ == "__main__":
    unittest.main()
