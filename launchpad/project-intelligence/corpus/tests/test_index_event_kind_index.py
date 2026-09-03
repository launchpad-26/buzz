"""Tests for the event-kind-index builder (index_defs/event_kind_index.py) --
#899.

Follows test_index_crate_index.py's conventions: indexes.py is loaded by path
under the name "corpus_indexes", and every generation happens into a
throwaway corpus built in a temp directory, so the real
launchpad/docs/corpus/ cannot change what these tests assert. Kind discovery,
however, is deliberately NOT a fixture concern: the builder enumerates
`pub const KIND_*` declarations from the real repository's
crates/buzz-core/src/kind.rs (validate.repo_root()) regardless of --root, the
same way index_defs/crate_index.py resolves crates/ against the real repo.
So these tests exercise the real kind.rs file for enumeration, and a
throwaway corpus root only for the canonical-node side of the cross-reference.
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
OUTPUT_REL = "generated/event-kind-index.md"

# A real constant declared in the real repository's kind.rs, cited by
# fixtures below. Verified directly against the working tree (not assumed):
# `pub const KIND_USER_STATUS: u32 = 30315;` is on line 70; the preceding
# constant, KIND_LONG_FORM, is on line 66 -- both used to test that a
# line-range must actually contain the target constant's own line.
REAL_KIND_NAME = "KIND_USER_STATUS"
REAL_KIND_VALUE = "30315"
REAL_KIND_LINE = 70
REAL_KIND_RS_PATH = "crates/buzz-core/src/kind.rs"

_NODE_TEMPLATE = """---
id: {node_id}
type: architecture
status: active
origin: launchpad
audiences:
  - agent
evidence:
{evidence}
---

# {node_id}

Fixture node for test_index_event_kind_index.py.
"""


def _write_node(corpus_root: Path, node_id: str, citations: list[str]) -> None:
    entries = []
    for citation in citations:
        entries.append(
            '  - statement: "Fixture claim for the event-kind-index tests."\n'
            "    entry_class: FACT\n"
            "    evidence:\n"
            f'      - "{citation}"'
        )
    (corpus_root / f"{node_id}.md").write_text(
        _NODE_TEMPLATE.format(node_id=node_id, evidence="\n".join(entries))
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
            "event-kind-index",
        ]
    )
    if code != 0:
        raise AssertionError(f"generation failed: {err}")
    return (corpus_root / OUTPUT_REL).read_text()


def _row_for(text: str, kind_name: str) -> str:
    return next(
        line for line in text.splitlines() if line.startswith(f"| `{kind_name}` |")
    )


class EventKindIndexSpecTest(unittest.TestCase):
    def _spec(self):
        by_name = {s.name: s for s in indexes.discover_builders(DEFS_DIR)}
        self.assertIn("event-kind-index", by_name)
        return by_name["event-kind-index"]

    def test_builder_discovered_with_declared_identity(self) -> None:
        spec = self._spec()
        self.assertEqual(spec.output_path, OUTPUT_REL)
        self.assertEqual(spec.node_id, "generated-event-kind-index")
        self.assertEqual(spec.node_type, "governance")


class EventKindIndexGenerationTest(unittest.TestCase):
    def test_two_runs_are_byte_identical(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_node(root, "fixture-kind-node", [f"{REAL_KIND_RS_PATH}:67-70"])
            first = _generate(root)
            second = _generate(root)
        self.assertEqual(first, second)

    def test_real_kind_appears_even_with_zero_fixture_nodes(self) -> None:
        # Kind enumeration walks the real repository's kind.rs file
        # independently of the (empty) fixture corpus, so a known kind shows
        # up with an honest "no documenting node" marker.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            text = _generate(root)
        row = _row_for(text, REAL_KIND_NAME)
        self.assertIn(f"| {REAL_KIND_VALUE} |", row)
        self.assertIn(f"{REAL_KIND_RS_PATH}:{REAL_KIND_LINE}", row)
        self.assertIn("none documented yet", row)

    def test_line_suffixed_citation_containing_declaration_line_attributes(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_node(root, "fixture-kind-node", [f"{REAL_KIND_RS_PATH}:67-70"])
            text = _generate(root)
        row = _row_for(text, REAL_KIND_NAME)
        self.assertIn("fixture-kind-node", row)
        self.assertNotIn("none documented yet", row)

    def test_bare_file_citation_attributes_to_no_kind(self) -> None:
        # A citation with no line-suffix cites kind.rs generally, not any
        # one kind -- it must not be force-attributed to every row.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_node(root, "fixture-bare-node", [REAL_KIND_RS_PATH])
            text = _generate(root)
        self.assertNotIn("fixture-bare-node", text)

    def test_line_suffix_missing_the_declaration_line_does_not_attribute(
        self,
    ) -> None:
        # Line 66 is KIND_LONG_FORM's declaration line, not
        # KIND_USER_STATUS's (line 70) -- a citation of :66 alone must not
        # attribute to KIND_USER_STATUS.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_node(root, "fixture-wrong-line-node", [f"{REAL_KIND_RS_PATH}:66"])
            text = _generate(root)
        row = _row_for(text, REAL_KIND_NAME)
        self.assertNotIn("fixture-wrong-line-node", row)

    def test_non_kind_rs_citation_shapes_do_not_attribute_documentation(
        self,
    ) -> None:
        excluded = [
            # resolves to a real file, but not kind.rs
            "launchpad/docs/corpus/AGENTS.md:1-5",
            # bare URL
            "https://example.com/some/doc",
            # commit-only ref (whitespace-shaped)
            "commit a44cf52fc740ebebbdd671427480d14f0bce0115",
            # tool-result string
            "grep_recursive('kind') -> no generator found",
            # path-shaped but resolves to no real file
            "crates/definitely-not-a-real-crate/src/kind.rs:70",
        ]
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_node(root, "fixture-noise-node", excluded)
            text = _generate(root)
        self.assertNotIn("fixture-noise-node", text)

    def test_front_matter_carries_node_id_and_type(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            text = _generate(root)
        front = text.split("---")[1]
        self.assertIn('id: "generated-event-kind-index"', front)
        self.assertIn('type: "governance"', front)
        self.assertIn("do not edit by hand", text)


if __name__ == "__main__":
    unittest.main()
