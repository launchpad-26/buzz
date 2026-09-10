"""Focused tests for the database-index builder -- issue #894.

Follows test_indexes.py's conventions: indexes.py is loaded by path under the
name "corpus_indexes"; behavioral assertions run against a fixture corpus
built in a temp directory, so the real launchpad/docs/corpus/ cannot change
what they assert. Two read-only smoke tests touch the real tree: one that the
builder is discovered from the shipped index_defs/, one that the committed
generated document carries the expected identity, marker, and today's
genuinely empty primary listing.
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

BUILDER_NAME = "database-index"
OUTPUT_REL = "generated/database-index.md"
NODE_ID = "generated-database-index"
DATASTORE_TEMPLATE_ID = "corpus-template-datastore"
DATA_ENTITY_TEMPLATE_ID = "corpus-template-data-entity"
REAL_CORPUS = indexes.validate.repo_root() / indexes.validate.DEFAULT_ROOT

_FIXTURE_EVIDENCE = (
    "evidence:\n"
    '  - statement: "Fixture node for test_index_database_index.py."\n'
    "    entry_class: FACT\n"
    "    evidence:\n"
    '      - "launchpad/project-intelligence/corpus/indexes.py"\n'
)


def _node(node_id: str, node_type: str, implements: str | None = None) -> str:
    relationships = ""
    if implements is not None:
        relationships = (
            "relationships:\n"
            "  - type: implements\n"
            f"    target: {implements}\n"
        )
    return (
        "---\n"
        f"id: {node_id}\n"
        f"type: {node_type}\n"
        "status: draft\n"
        "origin: launchpad\n"
        "audiences:\n"
        "  - agent\n"
        f"{relationships}"
        f"{_FIXTURE_EVIDENCE}"
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


def _render_fixture(root: Path) -> str:
    spec, specs = _spec_for_builder()
    ctx = indexes.build_context(root, specs)
    return indexes.render_document(spec, ctx)


class DiscoveryTest(unittest.TestCase):
    def test_builder_discovered_with_expected_identity(self) -> None:
        spec, _ = _spec_for_builder()
        self.assertIsNotNone(spec, "database-index not discovered")
        self.assertEqual(spec.output_path, OUTPUT_REL)
        self.assertEqual(spec.node_id, NODE_ID)
        self.assertEqual(spec.node_type, "governance")


class InclusionRuleTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)
        # The two template nodes themselves -- not implementers of anything.
        _write(
            self.root,
            "templates/datastore.md",
            _node(DATASTORE_TEMPLATE_ID, "governance"),
        )
        _write(
            self.root,
            "templates/data-entity.md",
            _node(DATA_ENTITY_TEMPLATE_ID, "governance"),
        )
        # Included: implements the datastore template, type architecture.
        _write(
            self.root,
            "architecture/containers/fixture-postgres.md",
            _node(
                "fixture-postgres",
                "architecture",
                implements=DATASTORE_TEMPLATE_ID,
            ),
        )
        # Included: implements the data-entity template, type implementation,
        # and lives outside architecture/containers/ entirely.
        _write(
            self.root,
            "capabilities/channels/fixture-channel-entity.md",
            _node(
                "fixture-channel-entity",
                "implementation",
                implements=DATA_ENTITY_TEMPLATE_ID,
            ),
        )
        # Excluded from the index, surfaced in the watch list: under the
        # container prefix, declares neither template edge.
        _write(
            self.root,
            "architecture/containers/fixture-redis.md",
            _node("fixture-redis", "architecture"),
        )
        # Excluded entirely: elsewhere, no relevant edge.
        _write(
            self.root,
            "capabilities/channels/fixture-channel.md",
            _node("fixture-channel", "capabilities"),
        )
        # Invalid: missing required front-matter fields -> node.error set.
        _write(
            self.root,
            "architecture/containers/fixture-broken.md",
            "---\nid: fixture-broken\n---\n\n# broken\n",
        )

    def test_implements_edge_is_the_rule_for_both_templates(self) -> None:
        text = _render_fixture(self.root)
        index_section = text.split("## Database index", 1)[1].split(
            "### Architecture containers watch list", 1
        )[0]
        self.assertIn("2 canonical corpus node(s)", index_section)
        self.assertIn(
            f"| fixture-postgres | `architecture/containers/fixture-postgres.md` "
            f"| draft | `{DATASTORE_TEMPLATE_ID}` |",
            index_section,
        )
        self.assertIn(
            "| fixture-channel-entity | "
            "`capabilities/channels/fixture-channel-entity.md` | draft | "
            f"`{DATA_ENTITY_TEMPLATE_ID}` |",
            index_section,
        )
        # Neither non-implementer appears in the primary index.
        self.assertNotIn("| fixture-redis |", index_section)
        self.assertNotIn("| fixture-channel |", index_section)
        # The invalid node appears nowhere.
        self.assertNotIn("fixture-broken", text)

    def test_watchlist_is_unfiltered_container_prefix_not_a_second_rule(self) -> None:
        text = _render_fixture(self.root)
        watchlist = text.split("### Architecture containers watch list", 1)[1]
        # Both the implementer and the non-implementer under the prefix show up.
        self.assertIn(
            f"| fixture-postgres | `architecture/containers/fixture-postgres.md` "
            f"| `{DATASTORE_TEMPLATE_ID}` |",
            watchlist,
        )
        self.assertIn(
            "| fixture-redis | `architecture/containers/fixture-redis.md` | no |",
            watchlist,
        )
        # A node outside the prefix, even an implementer, is not in the watch list.
        self.assertNotIn("fixture-channel-entity", watchlist)

    def test_output_stable_across_two_renders(self) -> None:
        self.assertEqual(_render_fixture(self.root), _render_fixture(self.root))


class EmptyRuleTest(unittest.TestCase):
    def test_zero_matches_renders_honest_empty_listing_and_watchlist(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(root, "other/fixture-only.md", _node("fixture-only", "capabilities"))
            text = _render_fixture(root)
            index_section = text.split("## Database index", 1)[1].split(
                "### Architecture containers watch list", 1
            )[0]
            watchlist = text.split("### Architecture containers watch list", 1)[1]
            self.assertIn("0 canonical corpus node(s)", index_section)
            self.assertIn("No canonical corpus node declares either edge yet", index_section)
            self.assertIn(
                "No valid node exists under `architecture/containers/`", watchlist
            )


class RealCorpusSmokeTest(unittest.TestCase):
    """Read-only checks against the committed generated document."""

    def test_committed_document_identity_marker_and_honest_empty_listing(self) -> None:
        target = REAL_CORPUS / OUTPUT_REL
        self.assertTrue(target.is_file(), f"{OUTPUT_REL} missing on disk")
        text = target.read_text(encoding="utf-8")
        front_matter = text.split("---\n")[1]
        self.assertIn(f'id: "{NODE_ID}"', front_matter)
        self.assertIn('type: "governance"', front_matter)
        self.assertIn("**Generated -- do not edit by hand.**", text)
        index_section = text.split("## Database index", 1)[1].split(
            "### Architecture containers watch list", 1
        )[0]
        # Proves the empty-listing claim against the real corpus rather than
        # assuming it: at this revision no node implements either template.
        self.assertIn("0 canonical corpus node(s)", index_section)


if __name__ == "__main__":
    unittest.main()
