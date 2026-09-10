"""Focused tests for the capability-index builder -- issue #887.

Follows test_indexes.py's conventions: indexes.py is loaded by path under the
name "corpus_indexes"; behavioral assertions run against a fixture corpus
built in a temp directory, so the real launchpad/docs/corpus/ cannot change
what they assert. Two read-only smoke tests touch the real tree: one that the
builder is discovered from the shipped index_defs/, one that the committed
generated document carries the expected identity and marker.
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

BUILDER_NAME = "capability-index"
OUTPUT_REL = "generated/capability-index.md"
NODE_ID = "generated-capability-index"
REAL_CORPUS = indexes.validate.repo_root() / indexes.validate.DEFAULT_ROOT

_FIXTURE_EVIDENCE = (
    "evidence:\n"
    '  - statement: "Fixture node for test_index_capability_index.py."\n'
    "    entry_class: FACT\n"
    "    evidence:\n"
    '      - "launchpad/project-intelligence/corpus/indexes.py"\n'
)


def _node(node_id: str, node_type: str) -> str:
    return (
        "---\n"
        f"id: {node_id}\n"
        f"type: {node_type}\n"
        "status: draft\n"
        "origin: launchpad\n"
        "audiences:\n"
        "  - agent\n"
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
        self.assertIsNotNone(spec, "capability-index not discovered")
        self.assertEqual(spec.output_path, OUTPUT_REL)
        self.assertEqual(spec.node_id, NODE_ID)
        self.assertEqual(spec.node_type, "capabilities")


class InclusionRuleTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)
        # Included: capabilities-typed, under and outside capabilities/.
        _write(
            self.root,
            "capabilities/channels/fixture-cap.md",
            _node("fixture-cap-channels", "capabilities"),
        )
        _write(
            self.root,
            "other/fixture-stray.md",
            _node("fixture-cap-stray", "capabilities"),
        )
        # Divergent: under capabilities/ but a different type.
        _write(
            self.root,
            "capabilities/communities/fixture-prov.md",
            _node("fixture-prov", "architecture"),
        )
        # Invalid: missing required front-matter fields -> node.error set.
        _write(
            self.root,
            "capabilities/channels/fixture-broken.md",
            "---\nid: fixture-broken\n---\n\n# broken\n",
        )

    def test_type_field_is_the_rule_not_the_path(self) -> None:
        text = _render_fixture(self.root)
        listing = text.split("## Capability index", 1)[1]
        index_table = listing.split("### Nodes under `capabilities/`", 1)[0]
        divergence = listing.split("### Nodes under `capabilities/`", 1)[1]
        self.assertIn("| fixture-cap-channels |", index_table)
        self.assertIn("| fixture-cap-stray |", index_table)
        self.assertIn("2 canonical corpus node(s)", index_table)
        # The architecture-typed node under capabilities/ is excluded from the
        # index and surfaced in the divergence table instead.
        self.assertNotIn("| fixture-prov |", index_table)
        self.assertIn("`capabilities/communities/fixture-prov.md` | architecture", divergence)
        # The invalid node appears nowhere.
        self.assertNotIn("fixture-broken", text)

    def test_stray_capabilities_node_gets_parent_dir_area(self) -> None:
        text = _render_fixture(self.root)
        self.assertIn("| other | fixture-cap-stray | `other/fixture-stray.md` |", text)

    def test_output_stable_across_two_renders(self) -> None:
        self.assertEqual(_render_fixture(self.root), _render_fixture(self.root))


class EmptyRuleTest(unittest.TestCase):
    def test_zero_matches_renders_honest_empty_listing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(root, "arch/fixture-only.md", _node("fixture-only", "architecture"))
            text = _render_fixture(root)
            self.assertIn("0 canonical corpus node(s)", text)
            self.assertIn("- None at this revision.", text)


class RealCorpusSmokeTest(unittest.TestCase):
    """Read-only checks against the committed generated document."""

    def test_committed_document_identity_and_marker(self) -> None:
        target = REAL_CORPUS / OUTPUT_REL
        self.assertTrue(target.is_file(), f"{OUTPUT_REL} missing on disk")
        text = target.read_text(encoding="utf-8")
        front_matter = text.split("---\n")[1]
        self.assertIn(f'id: "{NODE_ID}"', front_matter)
        self.assertIn('type: "capabilities"', front_matter)
        self.assertIn("**Generated -- do not edit by hand.**", text)


if __name__ == "__main__":
    unittest.main()
