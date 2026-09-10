"""Tests for the crate-index builder (index_defs/crate_index.py) -- #893.

Follows test_indexes.py's conventions: indexes.py is loaded by path under the
name "corpus_indexes", and every generation happens into a throwaway corpus
built in a temp directory, so the real launchpad/docs/corpus/ cannot change
what these tests assert. Crate discovery, however, is deliberately NOT a
fixture concern: the builder enumerates crates/*/Cargo.toml against the real
repository working tree (validate.repo_root()) regardless of --root, the same
way index_defs/code_to_doc_map.py resolves cited paths against the real repo.
So these tests exercise the real crates/ directory for enumeration, and a
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
OUTPUT_REL = "generated/crate-index.md"

# A real file under a real crate in this repository, cited by fixtures below.
REAL_CRATE_NAME = "buzz-core"
REAL_CRATE_PATH = "crates/buzz-core/src/kind.rs"

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

Fixture node for test_index_crate_index.py.
"""


def _write_node(corpus_root: Path, node_id: str, citations: list[str]) -> None:
    entries = []
    for citation in citations:
        entries.append(
            '  - statement: "Fixture claim for the crate-index tests."\n'
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
            "crate-index",
        ]
    )
    if code != 0:
        raise AssertionError(f"generation failed: {err}")
    return (corpus_root / OUTPUT_REL).read_text()


class CrateIndexSpecTest(unittest.TestCase):
    def _spec(self):
        by_name = {s.name: s for s in indexes.discover_builders(DEFS_DIR)}
        self.assertIn("crate-index", by_name)
        return by_name["crate-index"]

    def test_builder_discovered_with_declared_identity(self) -> None:
        spec = self._spec()
        self.assertEqual(spec.output_path, OUTPUT_REL)
        self.assertEqual(spec.node_id, "generated-crate-index")
        self.assertEqual(spec.node_type, "governance")


class CrateIndexGenerationTest(unittest.TestCase):
    def test_two_runs_are_byte_identical(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_node(root, "fixture-crate-node", [REAL_CRATE_PATH])
            first = _generate(root)
            second = _generate(root)
        self.assertEqual(first, second)

    def test_real_crate_appears_even_with_zero_fixture_nodes(self) -> None:
        # Crate enumeration walks the real repository's crates/ directory
        # independently of the (empty) fixture corpus, so a known crate
        # shows up with an honest "no documenting node" marker.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            text = _generate(root)
        self.assertIn(f"| `{REAL_CRATE_NAME}` | `crates/{REAL_CRATE_NAME}` |", text)
        self.assertIn("none documented yet", text)

    def test_citation_under_crate_attributes_documentation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_node(root, "fixture-crate-node", [REAL_CRATE_PATH])
            text = _generate(root)
        row = next(
            line
            for line in text.splitlines()
            if line.startswith(f"| `{REAL_CRATE_NAME}` |")
        )
        self.assertIn("fixture-crate-node", row)
        self.assertNotIn("none documented yet", row)

    def test_line_suffixed_citations_collapse_to_the_same_crate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_node(
                root,
                "fixture-crate-node",
                [REAL_CRATE_PATH, f"{REAL_CRATE_PATH}:12", f"{REAL_CRATE_PATH}:12-34"],
            )
            text = _generate(root)
        row = next(
            line
            for line in text.splitlines()
            if line.startswith(f"| `{REAL_CRATE_NAME}` |")
        )
        # One citing node listed exactly once, regardless of how many
        # line-suffixed citations of files under its directory exist.
        self.assertEqual(row.count("fixture-crate-node"), 1)

    def test_non_crate_citation_shapes_do_not_attribute_documentation(self) -> None:
        excluded = [
            # resolves to a real file, but outside any crates/<name>/ dir
            "launchpad/docs/corpus/AGENTS.md",
            # bare URL
            "https://example.com/some/doc",
            # commit-only ref (whitespace-shaped)
            "commit a44cf52fc740ebebbdd671427480d14f0bce0115",
            # tool-result string
            "grep_recursive('index') -> no generator found",
            # path-shaped but resolves to no real file
            "crates/definitely-not-a-real-crate/src/lib.rs",
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
        self.assertIn('id: "generated-crate-index"', front)
        self.assertIn('type: "governance"', front)
        self.assertIn("do not edit by hand", text)


if __name__ == "__main__":
    unittest.main()
