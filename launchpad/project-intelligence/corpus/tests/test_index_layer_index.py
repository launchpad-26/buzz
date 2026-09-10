"""Focused tests for the layer-index builder -- issue #900.

Follows test_index_configuration_index.py's conventions: indexes.py is
loaded by path under the name "corpus_indexes"; behavioral assertions run
against a fixture corpus built in a temp directory, so the real
launchpad/docs/corpus/ cannot change what they assert. Two read-only smoke
tests touch the real tree: one that the builder is discovered from the
shipped index_defs/, one that the committed generated document carries the
expected identity, marker and sub-layer headings.
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

BUILDER_NAME = "layer-index"
OUTPUT_REL = "generated/layer-index.md"
NODE_ID = "generated-layer-index"
REAL_CORPUS = indexes.validate.repo_root() / indexes.validate.DEFAULT_ROOT

_FIXTURE_EVIDENCE = (
    "evidence:\n"
    '  - statement: "Fixture node for test_index_layer_index.py."\n'
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
        self.assertIsNotNone(spec, "layer-index not discovered")
        self.assertEqual(spec.output_path, OUTPUT_REL)
        self.assertEqual(spec.node_id, NODE_ID)
        self.assertEqual(spec.node_type, "layers")


class InclusionRuleTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)
        # Included: two sub-layers, alphabetically out of order on disk to
        # prove the grouping sorts rather than preserving discovery order.
        _write(
            self.root,
            "layers/observability/fixture-metrics.md",
            _node("fixture-obs-metrics", "layers"),
        )
        _write(
            self.root,
            "layers/compute/fixture-runtime.md",
            _node("fixture-compute-runtime", "layers"),
        )
        _write(
            self.root,
            "layers/compute/fixture-liveness.md",
            _node("fixture-compute-liveness", "layers"),
        )
        # Included: a direct child of layers/ with no sub-layer directory.
        _write(
            self.root, "layers/fixture-root.md", _node("fixture-layers-root", "layers")
        )
        # Excluded, surfaced as divergence: type: layers outside layers/.
        _write(
            self.root,
            "generated/fixture-other-index.md",
            _node("fixture-other-index", "layers"),
        )
        # Excluded entirely: different type, outside layers/.
        _write(
            self.root,
            "arch/fixture-unrelated.md",
            _node("fixture-unrelated", "architecture"),
        )
        # Invalid: missing required front-matter fields -> node.error set.
        _write(
            self.root,
            "layers/compute/fixture-broken.md",
            "---\nid: fixture-broken\n---\n\n# broken\n",
        )

    def test_path_prefix_is_the_rule_grouped_by_sublayer(self) -> None:
        text = _render_fixture(self.root)
        listing = text.split("## Layer index", 1)[1]
        index_section = listing.split("### Nodes elsewhere with `type: layers`", 1)[0]
        self.assertIn("4 canonical corpus node(s)", index_section)
        self.assertIn("across 3 sub-layer(s)", index_section)

        # Sub-layer headings appear in alphabetical order.
        compute_pos = index_section.index("### compute")
        observability_pos = index_section.index("### observability")
        root_pos = index_section.index("### (root)")
        self.assertLess(compute_pos, observability_pos)
        self.assertLess(observability_pos, root_pos)

        compute_section = index_section[compute_pos:observability_pos]
        # Rows within a sub-layer sorted by path, not fixture-write order.
        liveness_pos = compute_section.index("fixture-compute-liveness")
        runtime_pos = compute_section.index("fixture-compute-runtime")
        self.assertLess(liveness_pos, runtime_pos)

        self.assertIn("fixture-obs-metrics", index_section)
        self.assertIn("fixture-layers-root", index_section)
        self.assertNotIn("fixture-unrelated", text)
        self.assertNotIn("fixture-broken", text)

    def test_type_layers_outside_prefix_surfaced_not_listed(self) -> None:
        text = _render_fixture(self.root)
        index_section, divergence = text.split(
            "### Nodes elsewhere with `type: layers`", 1
        )
        self.assertNotIn("fixture-other-index", index_section)
        self.assertIn("fixture-other-index", divergence)
        self.assertIn("`generated/fixture-other-index.md`", divergence)

    def test_output_stable_across_two_renders(self) -> None:
        self.assertEqual(_render_fixture(self.root), _render_fixture(self.root))


class EmptyRuleTest(unittest.TestCase):
    def test_zero_matches_renders_honest_empty_listing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(root, "arch/fixture-only.md", _node("fixture-only", "architecture"))
            text = _render_fixture(root)
            self.assertIn("0 canonical corpus node(s)", text)
            self.assertIn("across 0 sub-layer(s)", text)
            self.assertIn("- None at this revision.", text)


class RealCorpusSmokeTest(unittest.TestCase):
    """Read-only checks against the committed generated document."""

    def test_committed_document_identity_marker_and_sublayers(self) -> None:
        target = REAL_CORPUS / OUTPUT_REL
        self.assertTrue(target.is_file(), f"{OUTPUT_REL} missing on disk")
        text = target.read_text(encoding="utf-8")
        front_matter = text.split("---\n")[1]
        self.assertIn(f'id: "{NODE_ID}"', front_matter)
        self.assertIn('type: "layers"', front_matter)
        self.assertIn("**Generated -- do not edit by hand.**", text)
        for sublayer in ("compute", "configuration", "lifecycle", "observability"):
            self.assertIn(f"### {sublayer}", text)


if __name__ == "__main__":
    unittest.main()
