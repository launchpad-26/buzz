"""Focused tests for the provenance-index builder -- issue #903.

Follows test_index_decision_index.py's and test_index_coverage.py's fixture
shape. Unlike decision_index.py, this builder needs no repo-root derivation
or off-corpus directory: every number it renders comes from
``ctx.valid_nodes[*].data['evidence']``, so a bare fixture corpus (no
``launchpad/decisions/`` tree) is enough. Every behavioral test builds its own
throwaway fixture corpus, so the real corpus cannot change what they assert.
One read-only smoke test touches the real, committed generated document.
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

BUILDER_NAME = "provenance-index"
OUTPUT_REL = "generated/provenance-index.md"
NODE_ID = "generated-provenance-index"
REAL_CORPUS = indexes.validate.repo_root() / indexes.validate.DEFAULT_ROOT


def _write(root: Path, rel: str, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _evidence_yaml(entries: list[dict]) -> str:
    """Render a list of {"statement", "entry_class", ...} dicts as the
    evidence block a node's front matter carries. Every entry is
    schema-valid: FACT/INFERENCE carry `evidence` citations (INFERENCE also
    `confidence`), TEAM_KNOWLEDGE carries `provided_by` -- so every fixture
    node built with this helper passes node.schema.json and lands in
    ctx.valid_nodes, matching the real validator's own gate."""
    lines = ["evidence:"]
    for entry in entries:
        lines.append(f'  - statement: "{entry["statement"]}"')
        lines.append(f'    entry_class: {entry["entry_class"]}')
        if entry["entry_class"] in ("FACT", "INFERENCE"):
            lines.append("    evidence:")
            for citation in entry["evidence"]:
                lines.append(f'      - "{citation}"')
        if entry["entry_class"] == "INFERENCE":
            lines.append(f'    confidence: {entry["confidence"]}')
        if entry["entry_class"] == "TEAM_KNOWLEDGE":
            lines.append(f'    provided_by: "{entry["provided_by"]}"')
    return "\n".join(lines)


def _node_text(node_id: str, entries: list[dict]) -> str:
    return (
        "---\n"
        f"id: {node_id}\n"
        "type: governance\n"
        "status: active\n"
        "origin: launchpad\n"
        "audiences:\n"
        "  - agent\n"
        f"{_evidence_yaml(entries)}\n"
        "---\n\n"
        f"# {node_id}\n"
    )


def _fact(statement: str, evidence: list[str]) -> dict:
    return {"statement": statement, "entry_class": "FACT", "evidence": evidence}


def _inference(statement: str, evidence: list[str], confidence: float) -> dict:
    return {
        "statement": statement,
        "entry_class": "INFERENCE",
        "evidence": evidence,
        "confidence": confidence,
    }


def _team_knowledge(statement: str, provided_by: str) -> dict:
    return {
        "statement": statement,
        "entry_class": "TEAM_KNOWLEDGE",
        "provided_by": provided_by,
    }


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
        self.assertIsNotNone(spec, "provenance-index builder not discovered")
        self.assertEqual(spec.output_path, OUTPUT_REL)
        self.assertEqual(spec.node_id, NODE_ID)
        self.assertEqual(spec.node_type, "governance")
        self.assertIn(
            {"type": "implements", "target": "corpus-template-generated-index"},
            list(spec.relationships),
        )
        self.assertIn(
            {"type": "references", "target": "corpus-agents"},
            list(spec.relationships),
        )


class DistributionTest(unittest.TestCase):
    """A fixture corpus with two nodes: one carrying 2 FACT + 1 INFERENCE + 1
    TEAM_KNOWLEDGE, the other carrying 1 FACT only."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        root = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)
        self.corpus = root / "launchpad" / "docs" / "corpus"

        _write(
            root,
            "launchpad/docs/corpus/fixture-mixed.md",
            _node_text(
                "fixture-mixed",
                [
                    _fact("First fact.", ["launchpad/docs/corpus/AGENTS.md"]),
                    _fact("Second fact.", ["launchpad/docs/corpus/README.md"]),
                    _inference(
                        "An inference.", ["launchpad/docs/corpus/AGENTS.md"], 0.6
                    ),
                    _team_knowledge("Told to us.", "a teammate"),
                ],
            ),
        )
        _write(
            root,
            "launchpad/docs/corpus/fixture-fact-only.md",
            _node_text(
                "fixture-fact-only",
                [_fact("Only fact.", ["launchpad/docs/corpus/AGENTS.md"])],
            ),
        )

    def test_per_node_counts_rendered(self) -> None:
        text = _render_fixture(self.corpus)
        table = text.split("## Per-node evidence distribution", 1)[1].split(
            "## Corpus-wide totals"
        )[0]
        self.assertIn(
            "| fixture-mixed | `fixture-mixed.md` | 2 | 1 | 1 | 4 |", table
        )
        self.assertIn(
            "| fixture-fact-only | `fixture-fact-only.md` | 1 | 0 | 0 | 1 |", table
        )

    def test_per_node_rows_sorted_by_node_id(self) -> None:
        text = _render_fixture(self.corpus)
        table = text.split("## Per-node evidence distribution", 1)[1].split(
            "## Corpus-wide totals"
        )[0]
        self.assertLess(
            table.index("fixture-fact-only"), table.index("fixture-mixed")
        )

    def test_corpus_wide_totals(self) -> None:
        text = _render_fixture(self.corpus)
        totals = text.split("## Corpus-wide totals", 1)[1].split(
            "## Zero-evidence nodes"
        )[0]
        self.assertIn("Across all 2 node(s): **5** total evidence entries.", totals)
        self.assertIn("| FACT | 3 |", totals)
        self.assertIn("| INFERENCE | 1 |", totals)
        self.assertIn("| TEAM_KNOWLEDGE | 1 |", totals)

    def test_zero_evidence_section_states_none_and_why(self) -> None:
        text = _render_fixture(self.corpus)
        section = text.split("## Zero-evidence nodes", 1)[1].split(
            "## Relationships"
        )[0]
        self.assertIn("expected to be empty", section)
        self.assertIn(
            "None -- every schema-valid canonical corpus node at this "
            "revision carries at least one evidence entry",
            section,
        )

    def test_distinction_from_coverage_stated_in_body(self) -> None:
        text = _render_fixture(self.corpus)
        self.assertIn("## Distinction from `coverage.md` and `coverage.py`", text)
        self.assertIn("source-inventory disposition", text)
        self.assertIn("#892", text)
        self.assertIn("#634", text)

    def test_output_stable_across_two_renders(self) -> None:
        self.assertEqual(_render_fixture(self.corpus), _render_fixture(self.corpus))


class EmptyCorpusTest(unittest.TestCase):
    def test_no_nodes_renders_honest_empty_state(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            corpus = root / "launchpad" / "docs" / "corpus"
            corpus.mkdir(parents=True)
            text = _render_fixture(corpus)
        self.assertIn("**0 canonical corpus node(s)**", text)
        self.assertIn(
            "None -- no schema-valid canonical corpus node was discovered "
            "at this revision.",
            text,
        )
        self.assertIn("Across all 0 node(s): **0** total evidence entries.", text)


class FrontMatterTest(unittest.TestCase):
    def test_front_matter_carries_node_id_and_type(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            corpus = root / "launchpad" / "docs" / "corpus"
            corpus.mkdir(parents=True)
            text = _render_fixture(corpus)
        self.assertTrue(
            text.startswith(f'---\nid: "{NODE_ID}"\ntype: "governance"\n')
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
        self.assertIn("## Zero-evidence nodes", text)
        self.assertIn(
            "None -- every schema-valid canonical corpus node at this "
            "revision carries at least one evidence entry",
            text,
        )


if __name__ == "__main__":
    unittest.main()
