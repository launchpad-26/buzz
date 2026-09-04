"""Unit tests for corpus completeness and source-coverage accounting -- issue #634.

Run:  python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"

Every test builds its own throwaway fixture tree under `tempfile.TemporaryDirectory`
and points `build_coverage`/the CLI at it -- test_inventory.py's rule of never
depending on the real repository tree for content assertions. The fixture root
carries both a miniature Buzz source surface (a workspace crate, event kinds, a
migration, `.env.example` keys) and its own corpus root under
`launchpad/docs/corpus/`, so both sides of the accounting are fully controlled.

The node schema is the ONE real-repo input every test shares: validate.load_nodes
always validates against the committed launchpad/docs/corpus/schema/node.schema.json,
which is exactly the reuse issue #634 asks for (validate.py's discovery and
front-matter parsing contract, not a private reimplementation).
"""

from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

# coverage.py lives in a directory (project-intelligence/corpus/) that isn't a
# package, so it's loaded by path -- the same pattern every sibling test uses.
_COVERAGE_PATH = Path(__file__).resolve().parent.parent / "coverage.py"
_spec = importlib.util.spec_from_file_location("corpus_coverage", _COVERAGE_PATH)
coverage = importlib.util.module_from_spec(_spec)
sys.modules["corpus_coverage"] = coverage
_spec.loader.exec_module(coverage)

manifest = sys.modules["corpus_manifest"]


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


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
        '  - statement: "Fixture statement for coverage tests."\n'
        "    entry_class: FACT\n"
        "    evidence:\n"
        f"{cites}\n"
        "---\n\n"
        f"# {node_id}\n"
    )


def _plan_entry(path: str, start_points: list[str]) -> dict:
    return {
        "path": path,
        "filename": path.rsplit("/", 1)[-1],
        "issue_title": f"task: document {path}",
        "parent_feature": "#621",
        "priority": "P2",
        "start_date": None,
        "target_date": None,
        "effort": "S",
        "blockers": [],
        "template": "concept",
        "purpose": "fixture",
        "audiences": ["agent"],
        "source_start_points": start_points,
    }


def _fixture_root(tmp: str, *, nodes: dict[str, list[str]] | None = None, mystery_dir: bool = False) -> Path:
    """A miniature repo: one crate, two event kinds, one migration, two config keys.

    `nodes` maps node id -> citation list; each becomes one corpus node under the
    fixture's own launchpad/docs/corpus/ root ('launchpad' is in inventory.py's
    deliberately-ignored top-level set, so the corpus never pollutes the inventory).
    """
    root = Path(tmp)
    _write(root / "Cargo.toml", '[workspace]\nmembers = [\n    "crates/demo",\n]\n')
    _write(root / "crates" / "demo" / "Cargo.toml", '[package]\nname = "demo"\n')
    _write(
        root / "crates" / "buzz-core" / "src" / "kind.rs",
        "pub const KIND_ONE: u32 = 1;\npub const KIND_TWO: u32 = 2;\n",
    )
    _write(root / "migrations" / "0001_init.sql", "CREATE TABLE demo ();\n")
    _write(root / ".env.example", "KEY_A=1\nKEY_B=2\n")
    corpus = root / "launchpad" / "docs" / "corpus"
    corpus.mkdir(parents=True, exist_ok=True)
    for node_id, citations in (nodes or {}).items():
        _write(corpus / f"{node_id}.md", _node_text(node_id, citations))
    if mystery_dir:
        (root / "mystery").mkdir()
    return root


def _corpus_root(root: Path) -> Path:
    return root / "launchpad" / "docs" / "corpus"


def _rows_by_key(report) -> dict:
    return {row.source_key: row for row in report.rows}


class DocumentedByNodeCitationTest(unittest.TestCase):
    def test_citation_beneath_a_crate_documents_the_crate_and_links_the_node(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _fixture_root(tmp, nodes={"doc-demo-crate": ["crates/demo/src/lib.rs"]})
            report = coverage.build_coverage(root, _corpus_root(root))
            row = _rows_by_key(report)["rust_crate:demo"]
            self.assertEqual(row.disposition, coverage.DOCUMENTED)
            self.assertEqual(row.nodes, ("doc-demo-crate",))
            self.assertEqual(row.aliases, ())

    def test_line_scoped_citation_documents_only_the_kind_on_that_line(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _fixture_root(tmp, nodes={"doc-kind-one": ["crates/buzz-core/src/kind.rs:1"]})
            report = coverage.build_coverage(root, _corpus_root(root))
            rows = _rows_by_key(report)
            self.assertEqual(rows["event_kind:KIND_ONE"].disposition, coverage.DOCUMENTED)
            self.assertEqual(rows["event_kind:KIND_ONE"].nodes, ("doc-kind-one",))
            self.assertEqual(rows["event_kind:KIND_TWO"].disposition, coverage.GAP)

    def test_whole_file_citation_documents_every_item_in_that_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _fixture_root(tmp, nodes={"doc-config": [".env.example"]})
            report = coverage.build_coverage(root, _corpus_root(root))
            rows = _rows_by_key(report)
            self.assertEqual(rows["config:KEY_A"].disposition, coverage.DOCUMENTED)
            self.assertEqual(rows["config:KEY_B"].disposition, coverage.DOCUMENTED)

    def test_unopenable_citation_forms_never_document_anything(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _fixture_root(
                tmp,
                nodes={
                    "doc-unopenable": [
                        "commit 0052f5a7820ca4ca261efa233feb8bb53858ade6",
                        "https://github.com/block/buzz/blob/0052f5a7820ca4ca261efa233feb8bb53858ade6/crates/demo/src/lib.rs",
                        "helper(arg='crates/demo') -> no callers",
                    ]
                },
            )
            report = coverage.build_coverage(root, _corpus_root(root))
            self.assertEqual(_rows_by_key(report)["rust_crate:demo"].disposition, coverage.GAP)


class DocumentedByManifestTest(unittest.TestCase):
    def test_exact_source_key_start_point_links_the_task_alias(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _fixture_root(tmp)
            rows = manifest.build_manifest(
                [_plan_entry("capabilities/demo.md", ["migration:0001_init"])]
            ).rows
            report = coverage.build_coverage(root, _corpus_root(root), manifest_rows=rows)
            row = _rows_by_key(report)["migration:0001_init"]
            self.assertEqual(row.disposition, coverage.DOCUMENTED)
            self.assertEqual(row.aliases, ("capabilities/demo.md",))
            self.assertEqual(row.nodes, ())

    def test_path_start_point_covers_by_containment_in_both_directions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _fixture_root(tmp)
            rows = manifest.build_manifest(
                [
                    # A file beneath the crate-shaped item covers the crate...
                    _plan_entry("capabilities/relay.md", ["crates/demo/src/main.rs"]),
                    # ...and a directory enclosing file-shaped items covers them.
                    _plan_entry("capabilities/schema.md", ["migrations"]),
                ]
            ).rows
            report = coverage.build_coverage(root, _corpus_root(root), manifest_rows=rows)
            by_key = _rows_by_key(report)
            self.assertEqual(by_key["rust_crate:demo"].aliases, ("capabilities/relay.md",))
            self.assertEqual(by_key["migration:0001_init"].aliases, ("capabilities/schema.md",))


class RegistryDispositionTest(unittest.TestCase):
    def _registry(self, tmp_root: Path, entries: list[dict]) -> list:
        path = tmp_root / "dispositions.json"
        _write(path, json.dumps({"dispositions": entries}))
        return coverage.load_registry(path)

    def test_each_registry_disposition_is_assigned_and_carries_its_audit_trail(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _fixture_root(tmp)
            registry = self._registry(
                root,
                [
                    {
                        "source_key": "event_kind:KIND_ONE",
                        "disposition": "represented-elsewhere",
                        "reason": "described inside the demo crate node",
                        "accounted_by": ["doc-demo-crate"],
                    },
                    {
                        "source_key": "config:KEY_A",
                        "disposition": "generated-only",
                        "reason": "emitted by tooling, no authored surface",
                    },
                    {
                        "source_key": "config:KEY_B",
                        "disposition": "explicitly-excluded",
                        "reason": "out of corpus scope per #621",
                    },
                ],
            )
            report = coverage.build_coverage(root, _corpus_root(root), registry=registry)
            by_key = _rows_by_key(report)
            row = by_key["event_kind:KIND_ONE"]
            self.assertEqual(row.disposition, coverage.REPRESENTED_ELSEWHERE)
            self.assertEqual(row.aliases, ("doc-demo-crate",))
            self.assertEqual(by_key["config:KEY_A"].disposition, coverage.GENERATED_ONLY)
            self.assertEqual(by_key["config:KEY_B"].disposition, coverage.EXPLICITLY_EXCLUDED)
            self.assertIn("out of corpus scope", by_key["config:KEY_B"].detail)

    def test_documented_beats_a_registry_entry_and_flags_it_as_redundant(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _fixture_root(tmp, nodes={"doc-demo-crate": ["crates/demo/src/lib.rs"]})
            registry = self._registry(
                root,
                [
                    {
                        "source_key": "rust_crate:demo",
                        "disposition": "explicitly-excluded",
                        "reason": "stale exclusion",
                    }
                ],
            )
            report = coverage.build_coverage(root, _corpus_root(root), registry=registry)
            self.assertEqual(_rows_by_key(report)["rust_crate:demo"].disposition, coverage.DOCUMENTED)
            self.assertTrue(any("redundant or stale" in f for f in report.findings))

    def test_stale_registry_key_is_a_hard_input_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _fixture_root(tmp)
            registry = self._registry(
                root,
                [
                    {
                        "source_key": "rust_crate:no-such-crate",
                        "disposition": "explicitly-excluded",
                        "reason": "typo",
                    }
                ],
            )
            with self.assertRaises(coverage.CoverageInputError):
                coverage.build_coverage(root, _corpus_root(root), registry=registry)


class NoNotExaminedStateTest(unittest.TestCase):
    """Issue #634: no 'not examined' state can satisfy completeness -- in two halves:
    the registry cannot even represent one, and an unaccounted item is a GAP that
    always fails completeness."""

    def _load(self, tmp_root: Path, entries: list[dict]):
        path = tmp_root / "dispositions.json"
        _write(path, json.dumps({"dispositions": entries}))
        return coverage.load_registry(path)

    def test_not_examined_and_unknown_and_documented_are_all_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for disposition in ("not-examined", "unknown", "not examined", "documented", "GAP"):
                with self.assertRaises(coverage.CoverageInputError, msg=disposition):
                    self._load(
                        root,
                        [
                            {
                                "source_key": "config:KEY_A",
                                "disposition": disposition,
                                "reason": "should never load",
                            }
                        ],
                    )

    def test_registry_without_reason_or_without_accounted_by_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with self.assertRaises(coverage.CoverageInputError):
                self._load(
                    root,
                    [{"source_key": "config:KEY_A", "disposition": "explicitly-excluded", "reason": "  "}],
                )
            with self.assertRaises(coverage.CoverageInputError):
                self._load(
                    root,
                    [
                        {
                            "source_key": "config:KEY_A",
                            "disposition": "represented-elsewhere",
                            "reason": "represented somewhere it never names",
                        }
                    ],
                )

    def test_duplicate_registry_source_key_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            entry = {
                "source_key": "config:KEY_A",
                "disposition": "explicitly-excluded",
                "reason": "once",
            }
            with self.assertRaises(coverage.CoverageInputError):
                self._load(root, [entry, dict(entry)])

    def test_an_unaccounted_item_is_a_gap_and_the_report_is_incomplete(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _fixture_root(tmp)
            report = coverage.build_coverage(root, _corpus_root(root))
            row = _rows_by_key(report)["rust_crate:demo"]
            self.assertEqual(row.disposition, coverage.GAP)
            self.assertEqual(row.nodes, ())
            self.assertEqual(row.aliases, ())
            self.assertFalse(report.complete)
            self.assertIn(row, report.gaps)


class GapVisibilityTest(unittest.TestCase):
    def test_unrecognized_source_area_is_a_visible_gap(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _fixture_root(tmp, mystery_dir=True)
            report = coverage.build_coverage(root, _corpus_root(root))
            row = _rows_by_key(report)["unrecognized_area:mystery"]
            self.assertEqual(row.disposition, coverage.GAP)
            self.assertFalse(report.complete)

    def test_fully_accounted_fixture_is_complete(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _fixture_root(
                tmp,
                nodes={
                    "doc-everything": [
                        "crates/demo/src/lib.rs",
                        "crates/buzz-core/src/kind.rs",
                        "migrations/0001_init.sql",
                        ".env.example",
                    ]
                },
            )
            report = coverage.build_coverage(root, _corpus_root(root))
            self.assertTrue(report.complete)
            self.assertEqual(report.gaps, [])
            self.assertTrue(all(r.disposition == coverage.DOCUMENTED for r in report.rows))

    def test_unloadable_node_contributes_no_coverage_and_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _fixture_root(tmp)
            _write(
                _corpus_root(root) / "broken.md",
                "no frontmatter here at all\n",
            )
            report = coverage.build_coverage(root, _corpus_root(root))
            self.assertEqual(_rows_by_key(report)["rust_crate:demo"].disposition, coverage.GAP)
            self.assertTrue(any("skipped" in f for f in report.findings))


class ExcludedOutputPathsTest(unittest.TestCase):
    """Issue #2059: a generated document's own evidence citation must not be

    able to certify an in-scope item as documented -- the same self-feeding
    indexes.py's own canonical-input contract already excludes registered
    output paths to prevent.
    """

    def test_without_exclusion_a_generated_looking_node_still_documents(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _fixture_root(
                tmp, nodes={"generated-demo-index": ["crates/demo/src/lib.rs"]}
            )
            report = coverage.build_coverage(root, _corpus_root(root))
            row = _rows_by_key(report)["rust_crate:demo"]
            self.assertEqual(row.disposition, coverage.DOCUMENTED)
            self.assertEqual(row.nodes, ("generated-demo-index",))

    def test_excluded_output_path_no_longer_documents_its_own_citation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _fixture_root(
                tmp, nodes={"generated-demo-index": ["crates/demo/src/lib.rs"]}
            )
            report = coverage.build_coverage(
                root,
                _corpus_root(root),
                excluded_output_paths={"generated-demo-index.md"},
            )
            row = _rows_by_key(report)["rust_crate:demo"]
            self.assertEqual(row.disposition, coverage.GAP)

    def test_exclusion_does_not_affect_a_non_excluded_node_citing_the_same_item(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _fixture_root(
                tmp,
                nodes={
                    "generated-demo-index": ["crates/demo/src/lib.rs"],
                    "hand-authored-demo": ["crates/demo/src/lib.rs"],
                },
            )
            report = coverage.build_coverage(
                root,
                _corpus_root(root),
                excluded_output_paths={"generated-demo-index.md"},
            )
            row = _rows_by_key(report)["rust_crate:demo"]
            self.assertEqual(row.disposition, coverage.DOCUMENTED)
            self.assertEqual(row.nodes, ("hand-authored-demo",))

    def test_empty_exclusion_set_behaves_identically_to_omitting_it(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _fixture_root(
                tmp, nodes={"generated-demo-index": ["crates/demo/src/lib.rs"]}
            )
            without = coverage.build_coverage(root, _corpus_root(root))
            with_empty = coverage.build_coverage(
                root, _corpus_root(root), excluded_output_paths=frozenset()
            )
            self.assertEqual(
                _rows_by_key(without)["rust_crate:demo"].disposition,
                _rows_by_key(with_empty)["rust_crate:demo"].disposition,
            )


class CliContractTest(unittest.TestCase):
    def _run_main(self, argv: list[str]) -> tuple[int, str, str]:
        stdout, stderr = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            code = coverage.main(argv)
        return code, stdout.getvalue(), stderr.getvalue()

    def test_gaps_are_advisory_by_default_and_fatal_under_strict(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _fixture_root(tmp)
            code, out, err = self._run_main(["--root", str(root)])
            self.assertEqual(code, 0)
            self.assertIn("INCOMPLETE", err)
            self.assertIn("\tGAP\t", out)
            strict_code, _out, _err = self._run_main(["--root", str(root), "--strict"])
            self.assertEqual(strict_code, 1)

    def test_complete_fixture_exits_zero_even_under_strict(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _fixture_root(
                tmp,
                nodes={
                    "doc-everything": [
                        "crates/demo/src/lib.rs",
                        "crates/buzz-core/src/kind.rs",
                        "migrations/0001_init.sql",
                        ".env.example",
                    ]
                },
            )
            code, out, err = self._run_main(["--root", str(root), "--strict"])
            self.assertEqual(code, 0)
            self.assertIn("COMPLETE", err)
            self.assertNotIn("\tGAP\t", out)

    def test_malformed_registry_is_exit_2(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _fixture_root(tmp)
            bad = root / "bad.json"
            _write(bad, json.dumps({"dispositions": [{"source_key": "x", "disposition": "not-examined", "reason": "r"}]}))
            code, _out, err = self._run_main(["--root", str(root), "--dispositions", str(bad)])
            self.assertEqual(code, 2)
            self.assertIn("ERROR", err)

    def test_missing_corpus_root_is_exit_2(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _fixture_root(tmp)
            code, _out, err = self._run_main(
                ["--root", str(root), "--corpus-root", str(root / "no" / "such" / "dir")]
            )
            self.assertEqual(code, 2)
            self.assertIn("corpus root does not exist", err)

    def test_manifest_failing_626_validation_is_exit_2(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _fixture_root(tmp)
            bad = root / "manifest.json"
            _write(bad, json.dumps({"rows": [{"path": "only-a-path.md"}]}))
            code, _out, err = self._run_main(["--root", str(root), "--manifest", str(bad)])
            self.assertEqual(code, 2)
            self.assertIn("ERROR", err)

    def test_markdown_format_renders_a_table(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _fixture_root(tmp)
            code, out, _err = self._run_main(["--root", str(root), "--format", "markdown"])
            self.assertEqual(code, 0)
            self.assertTrue(out.startswith("| category | source_key | disposition |"))


class DeterminismTest(unittest.TestCase):
    def test_two_cli_runs_over_the_same_tree_are_byte_identical(self) -> None:
        """The full subprocess CLI, not main() in-process, so argv handling,
        module loading and stdout encoding are all inside what is compared."""
        with tempfile.TemporaryDirectory() as tmp:
            root = _fixture_root(
                tmp,
                nodes={"doc-demo-crate": ["crates/demo/src/lib.rs"]},
                mystery_dir=True,
            )
            manifest_path = root / "manifest.json"
            _write(
                manifest_path,
                json.dumps({"rows": [_plan_entry("capabilities/demo.md", ["migration:0001_init"])]}),
            )
            runs = [
                subprocess.run(
                    [
                        sys.executable,
                        str(_COVERAGE_PATH),
                        "--root",
                        str(root),
                        "--manifest",
                        str(manifest_path),
                    ],
                    capture_output=True,
                    check=True,
                )
                for _ in range(2)
            ]
            self.assertEqual(runs[0].stdout, runs[1].stdout)
            self.assertEqual(runs[0].stderr, runs[1].stderr)
            self.assertGreater(len(runs[0].stdout), 0)


if __name__ == "__main__":
    unittest.main()
