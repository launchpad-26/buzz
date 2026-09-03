"""Tests for the normative-documents builder (index_defs/normative_documents.py)
-- issue #1305.

Follows test_index_specifications_index.py's conventions: indexes.py is loaded
by path under the name "corpus_indexes", and every generation happens into a
throwaway corpus built in a temp directory, so the real
launchpad/docs/corpus/ cannot change what these tests assert.

Exercises the three-part inclusion rule directly: (a) path prefix
`specifications/`, (b) front-matter `type` is not `governance`, (c) the raw
file text case-insensitively names RFC 2119, RFC 8174, or BCP 14. Each rule
must independently gate membership -- a fixture that fails exactly one of the
three must be excluded.
"""

from __future__ import annotations

import contextlib
import importlib.util
import io
import sys
import tempfile
import unittest
from pathlib import Path

_INDEXES_PATH = Path(__file__).resolve().parent.parent / "indexes.py"
_spec = importlib.util.spec_from_file_location("corpus_indexes", _INDEXES_PATH)
indexes = importlib.util.module_from_spec(_spec)
sys.modules["corpus_indexes"] = indexes
_spec.loader.exec_module(indexes)

DEFS_DIR = Path(__file__).resolve().parent.parent / "index_defs"
OUTPUT_REL = "specifications/normative-documents.md"

_NODE_TEMPLATE = """---
id: {node_id}
type: {node_type}
status: active
origin: launchpad
audiences:
  - agent
evidence:
  - statement: "This node is a fixture used only by the normative-documents builder's tests."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/indexes.py"
---

# {node_id}

Fixture node for test_index_normative_documents.py.
{extra_body}
"""


def _write_node(
    corpus_root: Path,
    rel_path: str,
    node_id: str,
    node_type: str,
    extra_body: str = "",
) -> None:
    path = corpus_root / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        _NODE_TEMPLATE.format(
            node_id=node_id, node_type=node_type, extra_body=extra_body
        )
    )


def _run_main(argv: list[str]) -> tuple[int, str, str]:
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = indexes.main(argv)
    return code, out.getvalue(), err.getvalue()


def _generate(corpus_root: Path) -> str:
    code, _, err = _run_main(
        [
            "--root",
            str(corpus_root),
            "--defs-dir",
            str(DEFS_DIR),
            "--only",
            "normative-documents",
        ]
    )
    if code != 0:
        raise AssertionError(f"generation failed: {err}")
    return (corpus_root / OUTPUT_REL).read_text()


_RFC_2119_SENTENCE = (
    "This document uses MUST, MUST NOT, SHOULD, SHOULD NOT, MAY, and "
    "RECOMMENDED as defined in RFC 2119."
)
_BCP_14_SENTENCE = (
    'The key words "MUST", "SHOULD", and "MAY" in this document are to be '
    "interpreted as described in BCP 14 [RFC2119] [RFC8174] when, and only "
    "when, they appear in all capitals."
)


class NormativeDocumentsSpecTest(unittest.TestCase):
    def _spec(self):
        by_name = {s.name: s for s in indexes.discover_builders(DEFS_DIR)}
        self.assertIn("normative-documents", by_name)
        return by_name["normative-documents"]

    def test_builder_discovered_with_declared_identity(self) -> None:
        spec = self._spec()
        self.assertEqual(spec.output_path, OUTPUT_REL)
        self.assertEqual(spec.node_id, "specifications-normative-documents")
        self.assertEqual(spec.node_type, "governance")


class NormativeDocumentsGenerationTest(unittest.TestCase):
    def test_two_runs_are_byte_identical(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_node(
                root,
                "specifications/fixture-normative-spec.md",
                "fixture-normative-spec",
                "interfaces-events",
                extra_body=_RFC_2119_SENTENCE,
            )
            first = _generate(root)
            second = _generate(root)
        self.assertEqual(first, second)

    def test_rule_a_excludes_nodes_outside_specifications_prefix(self) -> None:
        """A node with a qualifying type and normative-keyword text, but
        living outside specifications/, must not appear."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_node(
                root,
                "architecture/fixture-outside-prefix.md",
                "fixture-outside-prefix",
                "architecture",
                extra_body=_RFC_2119_SENTENCE,
            )
            text = _generate(root)
        self.assertNotIn("fixture-outside-prefix", text)
        self.assertIn("No canonical corpus node currently qualifies", text)

    def test_rule_b_excludes_governance_typed_nodes_under_the_prefix(self) -> None:
        """A specifications/ node that names RFC 2119 but is type: governance
        (e.g. a meta/index document) must not appear -- rule (b)."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_node(
                root,
                "specifications/fixture-governance-node.md",
                "fixture-governance-node",
                "governance",
                extra_body=_BCP_14_SENTENCE,
            )
            text = _generate(root)
        self.assertNotIn("fixture-governance-node", text)
        self.assertIn("No canonical corpus node currently qualifies", text)

    def test_rule_c_excludes_nodes_with_no_normative_keyword_text(self) -> None:
        """A specifications/ node with a qualifying (non-governance) type but
        no RFC 2119/8174/BCP 14 text anywhere must not appear -- rule (c)."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_node(
                root,
                "specifications/fixture-silent-spec.md",
                "fixture-silent-spec",
                "interfaces-events",
                extra_body="This specification uses MUST and SHOULD freely.",
            )
            text = _generate(root)
        self.assertNotIn("fixture-silent-spec", text)
        self.assertIn("No canonical corpus node currently qualifies", text)

    def test_node_satisfying_all_three_rules_is_included(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_node(
                root,
                "specifications/fixture-normative-spec.md",
                "fixture-normative-spec",
                "interfaces-events",
                extra_body=_RFC_2119_SENTENCE,
            )
            # Distractors: fails rule (a), (b), and (c) respectively.
            _write_node(
                root,
                "architecture/fixture-outside-prefix.md",
                "fixture-outside-prefix",
                "architecture",
                extra_body=_RFC_2119_SENTENCE,
            )
            _write_node(
                root,
                "specifications/fixture-governance-node.md",
                "fixture-governance-node",
                "governance",
                extra_body=_BCP_14_SENTENCE,
            )
            _write_node(
                root,
                "specifications/fixture-silent-spec.md",
                "fixture-silent-spec",
                "interfaces-events",
                extra_body="This specification uses MUST and SHOULD freely.",
            )
            text = _generate(root)
        self.assertIn("| `fixture-normative-spec` |", text)
        self.assertNotIn("fixture-outside-prefix", text)
        self.assertNotIn("fixture-governance-node", text)
        self.assertNotIn("fixture-silent-spec", text)
        self.assertNotIn("No canonical corpus node currently qualifies", text)

    def test_bcp14_keyword_alone_also_qualifies(self) -> None:
        """RFC 8174 / BCP 14 boilerplate (not just RFC 2119) satisfies rule (c)."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_node(
                root,
                "specifications/fixture-bcp14-spec.md",
                "fixture-bcp14-spec",
                "architecture",
                extra_body=_BCP_14_SENTENCE,
            )
            text = _generate(root)
        self.assertIn("| `fixture-bcp14-spec` |", text)

    def test_empty_match_renders_honest_empty_listing_with_interpretation_section(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_node(
                root,
                "architecture/fixture-arch-node.md",
                "fixture-arch-node",
                "architecture",
            )
            text = _generate(root)
        self.assertIn("No canonical corpus node currently qualifies", text)
        self.assertIn('Interpreting "normative"', text)
        self.assertIn("specifications/INDEX.md", text)
        self.assertNotIn("fixture-arch-node", text)

    def test_front_matter_carries_node_id_and_type(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_node(
                root,
                "specifications/fixture-normative-spec.md",
                "fixture-normative-spec",
                "interfaces-events",
                extra_body=_RFC_2119_SENTENCE,
            )
            text = _generate(root)
        front = text.split("---")[1]
        self.assertIn('id: "specifications-normative-documents"', front)
        self.assertIn('type: "governance"', front)
        self.assertIn("do not edit by hand", text)


if __name__ == "__main__":
    unittest.main()
