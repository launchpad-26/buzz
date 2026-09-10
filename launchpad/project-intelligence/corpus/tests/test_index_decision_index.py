"""Focused tests for the decision-index builder -- issue #895.

Follows test_index_coverage.py's fixture shape (a miniature repo root whose
corpus lives under ``<root>/launchpad/docs/corpus/``, so the builder's
repo-root derivation resolves the fixture root rather than the real
repository) and test_index_decisions_index.py's citation-fixture conventions.
Every behavioral test builds its own throwaway ``launchpad/decisions/`` tree,
so the real ``launchpad/decisions/`` cannot change what they assert. Two
read-only smoke tests touch the real tree.
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

BUILDER_NAME = "decision-index"
OUTPUT_REL = "generated/decision-index.md"
NODE_ID = "generated-decision-index"
REAL_CORPUS = indexes.validate.repo_root() / indexes.validate.DEFAULT_ROOT


def _write(root: Path, rel: str, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _adr_text(status_line: str | None) -> str:
    front = "---\n"
    if status_line is not None:
        front += f"status: {status_line}\ndate: 2026-01-01\n"
    front += "---\n\n# Fixture ADR\n\n## Decision\n\nFixture content.\n"
    return front


def _node_text(node_id: str, citations: list[str]) -> str:
    cites = "\n".join(f'      - "{c}"' for c in citations)
    return (
        "---\n"
        f"id: {node_id}\n"
        "type: governance\n"
        "status: active\n"
        "origin: launchpad\n"
        "audiences:\n"
        "  - agent\n"
        "evidence:\n"
        '  - statement: "Fixture node for test_index_decision_index.py."\n'
        "    entry_class: FACT\n"
        "    evidence:\n"
        f"{cites}\n"
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
        self.assertIsNotNone(spec, "decision-index builder not discovered")
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


class StatusAndCoverageTest(unittest.TestCase):
    """A fixture repo with four ADR records (Accepted, Proposed, a Superseded
    variant, and one with no status: line) plus a non-ADR README.md, and one
    canonical node citing exactly one of the four records."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        root = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)
        self.corpus = root / "launchpad" / "docs" / "corpus"

        _write(
            root,
            "launchpad/decisions/ADR-0001-fixture-accepted.md",
            _adr_text("Accepted"),
        )
        _write(
            root,
            "launchpad/decisions/ADR-0002-fixture-proposed.md",
            _adr_text("Proposed"),
        )
        _write(
            root,
            "launchpad/decisions/ADR-0003-fixture-superseded.md",
            _adr_text("Superseded by ADR-0001"),
        )
        _write(
            root,
            "launchpad/decisions/ADR-0004-fixture-no-status.md",
            _adr_text(None),
        )
        # Not ADR-numbered -- must never appear in any table or count.
        _write(root, "launchpad/decisions/README.md", "# Decisions\n\nstatus: bogus\n")

        # Cites ADR-0001 with a fragment that must be stripped for matching.
        _write(
            root,
            "launchpad/docs/corpus/standards/citing.md",
            _node_text(
                "fixture-citing",
                ["launchpad/decisions/ADR-0001-fixture-accepted.md#L3"],
            ),
        )

    def test_status_buckets_counted_and_labelled(self) -> None:
        text = _render_fixture(self.corpus)
        summary = text.split("## Decision records by status", 1)[1].split(
            "## Citation coverage"
        )[0]
        self.assertIn("**4 ADR-numbered decision record(s)**", summary)
        self.assertIn("| Accepted | 1 |", summary)
        self.assertIn("| Proposed | 1 |", summary)
        self.assertIn("| Superseded | 1 |", summary)
        self.assertIn("| (no status field) | 1 |", summary)
        # README.md's bogus "status:" line must never surface as a bucket.
        self.assertNotIn("bogus", text)

    def test_citation_coverage_counts(self) -> None:
        text = _render_fixture(self.corpus)
        self.assertIn(
            "1 of 4 decision record(s) are cited by at least one canonical "
            "corpus node's front-matter",
            text,
        )
        self.assertIn("3 are cited by zero canonical nodes", text)

    def test_cited_record_excluded_from_gap_table_uncited_included(self) -> None:
        text = _render_fixture(self.corpus)
        gap_section = text.split(
            "## Coverage gaps: zero-citation decision records", 1
        )[1].split("## Relationships")[0]
        self.assertNotIn("ADR-0001-fixture-accepted.md", gap_section)
        self.assertIn(
            "| `launchpad/decisions/ADR-0002-fixture-proposed.md` | Proposed |",
            gap_section,
        )
        self.assertIn(
            "| `launchpad/decisions/ADR-0003-fixture-superseded.md` | Superseded |",
            gap_section,
        )
        self.assertIn(
            "| `launchpad/decisions/ADR-0004-fixture-no-status.md` | "
            "(no status field) |",
            gap_section,
        )

    def test_readme_never_counted(self) -> None:
        text = _render_fixture(self.corpus)
        # 4 ADR records total, not 5 -- README.md is not ADR-numbered.
        # "README.md" legitimately appears in this builder's own prose (the
        # exclusion bullet and the evidence-ledger statement); it must never
        # appear as a table row, and its bogus "status:" value must never
        # surface as a bucket.
        self.assertIn("**4 ADR-numbered decision record(s)**", text)
        self.assertNotIn("| README.md |", text)
        self.assertNotIn("`launchpad/decisions/README.md` |", text)
        self.assertIn(
            "`launchpad/decisions/README.md`: not ADR-numbered", text
        )

    def test_distinction_from_decisions_index_stated_in_body(self) -> None:
        text = _render_fixture(self.corpus)
        self.assertIn("## Distinction from `decisions/INDEX.md`", text)
        self.assertIn("stats/coverage view", text)
        self.assertIn("decisions-index", text)

    def test_output_stable_across_two_renders(self) -> None:
        self.assertEqual(_render_fixture(self.corpus), _render_fixture(self.corpus))


class EmptyDecisionsTreeTest(unittest.TestCase):
    def test_no_decisions_directory_renders_honest_empty_state(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            corpus = root / "launchpad" / "docs" / "corpus"
            corpus.mkdir(parents=True)
            text = _render_fixture(corpus)
        self.assertIn("**0 ADR-numbered decision record(s)**", text)
        self.assertIn(
            "None -- no file under `launchpad/decisions/` matches the "
            "`ADR-####-*.md` filename pattern",
            text,
        )
        self.assertIn(
            "None -- every ADR-numbered decision record under "
            "`launchpad/decisions/` is cited by at least one canonical node's "
            "front-matter evidence at this revision.",
            text,
        )


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
        self.assertIn("## Distinction from `decisions/INDEX.md`", text)


if __name__ == "__main__":
    unittest.main()
