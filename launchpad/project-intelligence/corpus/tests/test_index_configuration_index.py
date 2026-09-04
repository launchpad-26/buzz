"""Focused tests for the configuration-index builder -- issue #890.

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

BUILDER_NAME = "configuration-index"
OUTPUT_REL = "generated/configuration-index.md"
NODE_ID = "generated-configuration-index"
TEMPLATE_ID = "corpus-template-configuration"
REAL_CORPUS = indexes.validate.repo_root() / indexes.validate.DEFAULT_ROOT

_FIXTURE_EVIDENCE = (
    "evidence:\n"
    '  - statement: "Fixture node for test_index_configuration_index.py."\n'
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
        self.assertIsNotNone(spec, "configuration-index not discovered")
        self.assertEqual(spec.output_path, OUTPUT_REL)
        self.assertEqual(spec.node_id, NODE_ID)
        self.assertEqual(spec.node_type, "layers")


class InclusionRuleTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)
        # The template node itself, outside the prefix and not an implementer.
        _write(
            self.root,
            "templates/configuration.md",
            _node(TEMPLATE_ID, "governance"),
        )
        # Included: under the prefix, implementing the template.
        _write(
            self.root,
            "layers/configuration/fixture-relay.md",
            _node("fixture-cfg-relay", "layers", implements=TEMPLATE_ID),
        )
        # Included: under the prefix, no relationships (the defaults.md shape).
        _write(
            self.root,
            "layers/configuration/fixture-defaults.md",
            _node("fixture-cfg-defaults", "layers"),
        )
        # Included despite type: under the prefix, non-layers type.
        _write(
            self.root,
            "layers/configuration/fixture-odd.md",
            _node("fixture-cfg-odd", "architecture"),
        )
        # Excluded: layers-typed but under another layers subtree.
        _write(
            self.root,
            "layers/compute/fixture-compute.md",
            _node("fixture-compute", "layers"),
        )
        # Excluded from listing, surfaced separately: outside implementer.
        _write(
            self.root,
            "other/fixture-external.md",
            _node("fixture-cfg-external", "layers", implements=TEMPLATE_ID),
        )
        # Invalid: missing required front-matter fields -> node.error set.
        _write(
            self.root,
            "layers/configuration/fixture-broken.md",
            "---\nid: fixture-broken\n---\n\n# broken\n",
        )

    def test_path_prefix_is_the_rule_not_type_or_relationship(self) -> None:
        text = _render_fixture(self.root)
        listing = text.split("## Configuration index", 1)[1]
        index_table = listing.split("### Listed nodes whose type", 1)[0]
        self.assertIn("3 canonical corpus node(s)", index_table)
        self.assertIn("| fixture-cfg-relay |", index_table)
        self.assertIn("| fixture-cfg-defaults |", index_table)
        # Non-layers type under the prefix is still listed (path is the rule).
        self.assertIn("| fixture-cfg-odd |", index_table)
        # Layers-typed node elsewhere and the outside implementer are not.
        self.assertNotIn("| fixture-compute |", index_table)
        self.assertNotIn("| fixture-cfg-external |", index_table)
        # The invalid node appears nowhere.
        self.assertNotIn("fixture-broken", text)

    def test_template_edge_reported_per_row(self) -> None:
        text = _render_fixture(self.root)
        self.assertIn(
            "| fixture-cfg-relay | `layers/configuration/fixture-relay.md` "
            "| draft | yes |",
            text,
        )
        self.assertIn(
            "| fixture-cfg-defaults | "
            "`layers/configuration/fixture-defaults.md` | draft | no |",
            text,
        )

    def test_divergences_surfaced(self) -> None:
        text = _render_fixture(self.root)
        type_div = text.split("### Listed nodes whose type", 1)[1].split(
            "### `", 1
        )[0]
        outside = text.split("implementers outside", 1)[1]
        self.assertIn(
            "`layers/configuration/fixture-odd.md` | architecture", type_div
        )
        self.assertIn("| fixture-cfg-external | `other/fixture-external.md` |", outside)

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
        self.assertIn('type: "layers"', front_matter)
        self.assertIn("**Generated -- do not edit by hand.**", text)


if __name__ == "__main__":
    unittest.main()
