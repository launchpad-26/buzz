"""Tests for the code-to-doc-map builder (index_defs/code_to_doc_map.py) -- #888.

Follows test_indexes.py's conventions: indexes.py is loaded by path under the
name "corpus_indexes", and every generation happens into a throwaway corpus
built in a temp directory, so the real launchpad/docs/corpus/ cannot change
what these tests assert. The builder resolves cited paths against the real
repository root (validate.repo_root()), so fixtures cite real repo files to
exercise the kept branch and shaped non-paths to exercise every exclusion.
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
OUTPUT_REL = "generated/code-to-doc-map.md"

# A file that exists in this repository, cited by fixtures below.
REAL_PATH = "launchpad/project-intelligence/corpus/indexes.py"

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

Fixture node for test_index_code_to_doc_map.py.
"""


def _write_node(corpus_root: Path, node_id: str, citations: list[str]) -> None:
    entries = []
    for citation in citations:
        entries.append(
            '  - statement: "Fixture claim for the code-to-doc-map tests."\n'
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
            "code-to-doc-map",
        ]
    )
    if code != 0:
        raise AssertionError(f"generation failed: {err}")
    return (corpus_root / OUTPUT_REL).read_text()


class CodeToDocMapSpecTest(unittest.TestCase):
    def _spec(self):
        by_name = {s.name: s for s in indexes.discover_builders(DEFS_DIR)}
        self.assertIn("code-to-doc-map", by_name)
        return by_name["code-to-doc-map"]

    def test_builder_discovered_with_declared_identity(self) -> None:
        spec = self._spec()
        self.assertEqual(spec.output_path, OUTPUT_REL)
        self.assertEqual(spec.node_id, "generated-code-to-doc-map")
        self.assertEqual(spec.node_type, "governance")


class CodeToDocMapGenerationTest(unittest.TestCase):
    def test_two_runs_are_byte_identical(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_node(root, "fixture-code-node", [REAL_PATH])
            first = _generate(root)
            second = _generate(root)
        self.assertEqual(first, second)

    def test_resolving_code_citation_becomes_one_pair_row(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_node(root, "fixture-code-node", [REAL_PATH])
            text = _generate(root)
        self.assertIn(f"| `{REAL_PATH}` | fixture-code-node |", text)

    def test_line_suffixed_citations_collapse_into_one_row(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_node(
                root,
                "fixture-code-node",
                [REAL_PATH, f"{REAL_PATH}:12", f"{REAL_PATH}:12-34"],
            )
            text = _generate(root)
        row = f"| `{REAL_PATH}` | fixture-code-node |"
        self.assertEqual(text.count(row), 1)
        # The suffix is stripped, never listed verbatim.
        self.assertNotIn(f"{REAL_PATH}:12", text)

    def test_non_code_citation_shapes_are_all_excluded(self) -> None:
        excluded = [
            # corpus-internal path (a real file, still excluded by prefix)
            "launchpad/docs/corpus/AGENTS.md",
            # decision-record path (excluded by prefix, existence irrelevant)
            "launchpad/decisions/0001-record-architecture-decisions.md",
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
            _write_node(root, "fixture-code-node", [REAL_PATH])
            text = _generate(root)
        mapping = text.split("## Code-to-doc mapping")[1]
        self.assertIn(f"| `{REAL_PATH}` | fixture-code-node |", mapping)
        self.assertNotIn("fixture-noise-node", mapping)
        for citation in excluded:
            self.assertNotIn(f"`{citation}`", mapping)

    def test_empty_map_renders_honest_empty_message(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_node(root, "fixture-noise-node", ["https://example.com/x"])
            text = _generate(root)
        self.assertIn("This mapping is empty", text)
        self.assertNotIn("| Code path |", text)

    def test_front_matter_carries_node_id_and_type(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_node(root, "fixture-code-node", [REAL_PATH])
            text = _generate(root)
        front = text.split("---")[1]
        self.assertIn('id: "generated-code-to-doc-map"', front)
        self.assertIn('type: "governance"', front)
        self.assertIn("do not edit by hand", text)


if __name__ == "__main__":
    unittest.main()
