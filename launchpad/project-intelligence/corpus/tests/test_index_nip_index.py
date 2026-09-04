"""Tests for the nip-index builder (index_defs/nip_index.py) -- #901.

Follows test_indexes.py's and test_index_crate_index.py's conventions:
indexes.py is loaded by path under the name "corpus_indexes", and every
generation happens into a throwaway corpus built in a temp directory, so the
real launchpad/docs/corpus/ cannot change what these tests assert. Unlike
crate_index.py, this builder's determinism source is entirely
ctx.valid_nodes / node.path -- no real-repo working-tree directory (like
crates/) is read -- so every test here is fully fixture-local.
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
OUTPUT_REL = "generated/nip-index.md"

_NODE_TEMPLATE = """---
id: {node_id}
type: architecture
status: active
origin: launchpad
audiences:
  - agent
evidence:
  - statement: "Fixture claim for the nip-index tests.{front_matter_extra}"
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
---

# {node_id}

Fixture node for test_index_nip_index.py.
{body_extra}
"""


def _write_node(
    corpus_root: Path,
    node_id: str,
    front_matter_extra: str = "",
    body_extra: str = "",
) -> None:
    (corpus_root / f"{node_id}.md").write_text(
        _NODE_TEMPLATE.format(
            node_id=node_id,
            front_matter_extra=front_matter_extra,
            body_extra=body_extra,
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
            "nip-index",
        ]
    )
    if code != 0:
        raise AssertionError(f"generation failed: {err}")
    return (corpus_root / OUTPUT_REL).read_text()


class NipIndexSpecTest(unittest.TestCase):
    def _spec(self):
        by_name = {s.name: s for s in indexes.discover_builders(DEFS_DIR)}
        self.assertIn("nip-index", by_name)
        return by_name["nip-index"]

    def test_builder_discovered_with_declared_identity(self) -> None:
        spec = self._spec()
        self.assertEqual(spec.output_path, OUTPUT_REL)
        self.assertEqual(spec.node_id, "generated-nip-index")
        self.assertEqual(spec.node_type, "governance")


class NipIndexGenerationTest(unittest.TestCase):
    def test_two_runs_are_byte_identical(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_node(root, "fixture-nip-node", front_matter_extra=" Mentions NIP-29.")
            first = _generate(root)
            second = _generate(root)
        self.assertEqual(first, second)

    def test_zero_nip_fixture_corpus_renders_honest_empty_table(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_node(root, "fixture-no-nip-node")
            text = _generate(root)
        self.assertIn("NIP index is empty", text)
        self.assertNotIn("| NIP | Mentioning nodes | Node ids |", text)

    def test_front_matter_mention_is_picked_up(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_node(
                root, "fixture-front-matter-node", front_matter_extra=" See NIP-42 auth."
            )
            text = _generate(root)
        row = next(line for line in text.splitlines() if line.startswith("| `NIP-42`"))
        self.assertIn("fixture-front-matter-node", row)

    def test_body_only_mention_is_picked_up(self) -> None:
        # A NIP token that appears ONLY in the body Markdown (not in any
        # front-matter field) must still be found -- this is the behavior
        # that distinguishes this builder from a front-matter-only scan.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_node(
                root,
                "fixture-body-node",
                body_extra="\nThis capability implements NIP-50 search.\n",
            )
            text = _generate(root)
        row = next(line for line in text.splitlines() if line.startswith("| `NIP-50`"))
        self.assertIn("fixture-body-node", row)

    def test_lowercase_unhyphenated_source_identifiers_are_excluded(self) -> None:
        # crates/buzz-auth/src/nip42.rs and nip29_group_id are real lexical
        # collisions in this repository's own corpus -- the case-sensitive,
        # hyphen-requiring regex must not treat them as a NIP-42/NIP-29
        # mention.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_node(
                root,
                "fixture-source-identifier-node",
                body_extra=(
                    "\nSee `crates/buzz-auth/src/nip42.rs` and the "
                    "`nip29_group_id` column.\n"
                ),
            )
            text = _generate(root)
        self.assertIn("NIP index is empty", text)

    def test_two_nodes_citing_the_same_nip_are_both_listed_sorted(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_node(
                root, "fixture-zzz-node", front_matter_extra=" Mentions NIP-17."
            )
            _write_node(
                root, "fixture-aaa-node", front_matter_extra=" Also mentions NIP-17."
            )
            text = _generate(root)
        row = next(line for line in text.splitlines() if line.startswith("| `NIP-17`"))
        self.assertIn("fixture-aaa-node, fixture-zzz-node", row)
        self.assertEqual(row.count("| 2 |"), 1)

    def test_numeric_ordering_places_nip_9_before_nip_10(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_node(
                root, "fixture-ten-node", front_matter_extra=" Mentions NIP-10."
            )
            _write_node(
                root, "fixture-nine-node", front_matter_extra=" Mentions NIP-09."
            )
            text = _generate(root)
        nine_line = next(i for i, l in enumerate(text.splitlines()) if "`NIP-09`" in l)
        ten_line = next(i for i, l in enumerate(text.splitlines()) if "`NIP-10`" in l)
        self.assertLess(nine_line, ten_line)

    def test_front_matter_carries_node_id_and_type(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            text = _generate(root)
        front = text.split("---")[1]
        self.assertIn('id: "generated-nip-index"', front)
        self.assertIn('type: "governance"', front)
        self.assertIn("do not edit by hand", text)


if __name__ == "__main__":
    unittest.main()
