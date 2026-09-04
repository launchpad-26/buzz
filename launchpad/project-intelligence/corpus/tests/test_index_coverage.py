"""Focused tests for the coverage builder -- issue #892.

Follows test_index_capability_index.py's conventions (indexes.py loaded by
path as "corpus_indexes"; behavioral assertions against a throwaway fixture
tree) and test_coverage.py's fixture shape: a miniature repo root whose corpus
lives under `<root>/launchpad/docs/corpus/`, so the builder's repo-root
derivation resolves the fixture root and `inventory.py` walks the fixture,
never the real repository. Two read-only smoke tests touch the real tree.
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

BUILDER_NAME = "coverage"
OUTPUT_REL = "generated/coverage.md"
NODE_ID = "generated-coverage"
REAL_CORPUS = indexes.validate.repo_root() / indexes.validate.DEFAULT_ROOT

_VISIBILITY_SENTENCE = "`GAP` dispositions are visible, not hidden"


def _node_text(node_id: str, citations: list[str]) -> str:
    cites = "\n".join(f'      - "{c}"' for c in citations)
    return (
        "---\n"
        f"id: {node_id}\n"
        "type: architecture\n"
        "status: active\n"
        "origin: launchpad\n"
        "audiences:\n"
        "  - agent\n"
        "evidence:\n"
        '  - statement: "Fixture statement for coverage builder tests."\n'
        "    entry_class: FACT\n"
        "    evidence:\n"
        f"{cites}\n"
        "---\n\n"
        f"# {node_id}\n"
    )


def _write(root: Path, rel: str, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


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
        self.assertIsNotNone(spec, "coverage builder not discovered")
        self.assertEqual(spec.output_path, OUTPUT_REL)
        self.assertEqual(spec.node_id, NODE_ID)
        self.assertEqual(spec.node_type, "governance")


class AccountingTest(unittest.TestCase):
    """A fixture repo with one documented item, one gap item, and one
    unrecognized top-level directory: all three dispositions must be visible."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        root = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)
        _write(root, "migrations/0001_init.sql", "CREATE TABLE demo ();\n")
        _write(root, "migrations/0002_extra.sql", "CREATE TABLE more ();\n")
        (root / "mystery").mkdir()
        self.corpus = root / "launchpad" / "docs" / "corpus"
        _write(
            root,
            "launchpad/docs/corpus/fixture-migration-doc.md",
            _node_text("fixture-migration-doc", ["migrations/0001_init.sql"]),
        )

    def test_documented_gap_and_unrecognized_rows_all_visible(self) -> None:
        text = _render_fixture(self.corpus)
        accounting = text.split("### Accounting", 1)[1]
        # The cited migration is documented and links the citing node id.
        self.assertIn(
            "| migration | `migration:0001_init` | `migrations/0001_init.sql` "
            "| documented | fixture-migration-doc |",
            accounting,
        )
        # The uncited migration is a visible GAP row, never dropped.
        self.assertIn(
            "| migration | `migration:0002_extra` | `migrations/0002_extra.sql` "
            "| GAP |",
            accounting,
        )
        # The unrecognized top-level directory is an unconditional GAP row.
        self.assertIn("| unrecognized_area | `unrecognized_area:mystery` |", accounting)
        # The report says INCOMPLETE and never claims completeness with gaps.
        self.assertIn("**INCOMPLETE**: 2 of 3 in-scope source items", text)
        self.assertNotIn("**COMPLETE**:", text)
        self.assertIn(_VISIBILITY_SENTENCE, text)

    def test_disposition_summary_counts(self) -> None:
        text = _render_fixture(self.corpus)
        summary = text.split("### Disposition summary", 1)[1].split("### Accounting")[0]
        self.assertIn("| documented | 1 |", summary)
        self.assertIn("| GAP | 2 |", summary)
        # The registry-only dispositions render as zero rather than vanishing.
        self.assertIn("| represented-elsewhere | 0 |", summary)

    def test_output_stable_across_two_renders(self) -> None:
        self.assertEqual(_render_fixture(self.corpus), _render_fixture(self.corpus))


class CompleteReportTest(unittest.TestCase):
    def test_zero_gaps_claims_complete(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(root, "migrations/0001_init.sql", "CREATE TABLE demo ();\n")
            corpus = root / "launchpad" / "docs" / "corpus"
            _write(
                root,
                "launchpad/docs/corpus/fixture-migration-doc.md",
                _node_text("fixture-migration-doc", ["migrations/0001_init.sql"]),
            )
            text = _render_fixture(corpus)
            self.assertIn(
                "**COMPLETE**: all 1 in-scope source items are positively "
                "dispositioned",
                text,
            )
            self.assertNotIn("| GAP | 1 |", text)


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
        self.assertIn(_VISIBILITY_SENTENCE, text)
        # Whichever completeness verdict the committed report carries, it must
        # carry exactly one of the two, never both and never neither.
        self.assertEqual(
            1, text.count("**COMPLETE**:") + text.count("**INCOMPLETE**:")
        )


if __name__ == "__main__":
    unittest.main()
