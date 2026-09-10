"""Unit tests for the deterministic corpus index/graph generator -- issue #633.

Run:  python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"

Every test points --root (and build_context) at fixtures under this directory,
so the real launchpad/docs/corpus/ cannot change what they assert -- the same
rule test_validate.py states. Generation always happens into a COPY of the
fixture corpus in a temp directory, so no test dirties the committed fixtures.
"""

from __future__ import annotations

import contextlib
import importlib.util
import io
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures" / "indexes"
CLEAN_DIR = FIXTURES_DIR / "clean"
BROKEN_DIR = FIXTURES_DIR / "broken"
DEFS_DIR = FIXTURES_DIR / "defs"

# indexes.py lives in a non-package directory, so it is loaded by path -- the
# same pattern test_validate.py uses for validate.py. Loading it under the name
# "corpus_indexes" is also the name it registers for builder modules to import.
_INDEXES_PATH = Path(__file__).resolve().parent.parent / "indexes.py"
_spec = importlib.util.spec_from_file_location("corpus_indexes", _INDEXES_PATH)
indexes = importlib.util.module_from_spec(_spec)
sys.modules["corpus_indexes"] = indexes
_spec.loader.exec_module(indexes)

validate = indexes.validate

OUTPUT_REL = "generated/demo-index.md"


def _run_main(argv: list[str]) -> tuple[int, str, str]:
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = indexes.main(argv)
    return code, out.getvalue(), err.getvalue()


def _write_builder(directory: Path, module_name: str, **overrides) -> None:
    spec = {
        "name": "some-index",
        "output_path": "generated/some-index.md",
        "node_id": "fixture-generated-some-index",
        "title": "Some index",
        "node_type": "governance",
        "audiences": ["agent"],
        "subject": "some fixture subject",
    }
    spec.update(overrides)
    body = (
        "def _generate(ctx):\n"
        "    return {'sections': '## Listing\\n\\n- none', 'includes': ['everything']}\n"
        f"SPEC = dict({spec!r}, generate=_generate)\n"
    )
    (directory / f"{module_name}.py").write_text(body)


class DiscoveryTest(unittest.TestCase):
    def test_empty_defs_dir_returns_no_builders(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(indexes.discover_builders(Path(tmp)), [])

    def test_missing_defs_dir_returns_no_builders(self) -> None:
        self.assertEqual(
            indexes.discover_builders(Path("/nonexistent/index_defs")), []
        )

    def test_shipped_index_defs_package_discovers_cleanly(self) -> None:
        # The framework itself ships zero builders; each generated document
        # adds its own builder module as its own follow-up issue (#637 added
        # the first). Whatever builders ship, discovery of the real package
        # must succeed -- every SPEC valid, duplicate names/output paths
        # already a hard error inside discover_builders itself.
        specs = indexes.discover_builders()
        for spec in specs:
            self.assertIsInstance(spec, indexes.IndexSpec)

    def test_builders_discovered_in_sorted_module_name_order(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            _write_builder(
                directory, "b_second", name="second", output_path="generated/second.md"
            )
            _write_builder(
                directory, "a_first", name="first", output_path="generated/first.md"
            )
            names = [s.name for s in indexes.discover_builders(directory)]
        self.assertEqual(names, ["first", "second"])

    def test_underscore_modules_and_init_are_skipped(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            (directory / "__init__.py").write_text("")
            (directory / "_helper.py").write_text("raise RuntimeError('never loaded')")
            self.assertEqual(indexes.discover_builders(directory), [])

    def test_duplicate_builder_name_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            _write_builder(directory, "one", name="dupe", output_path="generated/a.md")
            _write_builder(directory, "two", name="dupe", output_path="generated/b.md")
            with self.assertRaisesRegex(indexes.SpecError, "duplicate builder name"):
                indexes.discover_builders(directory)

    def test_duplicate_output_path_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            _write_builder(directory, "one", name="a", output_path="generated/x.md")
            _write_builder(directory, "two", name="b", output_path="generated/x.md")
            with self.assertRaisesRegex(indexes.SpecError, "duplicate output_path"):
                indexes.discover_builders(directory)

    def test_node_type_outside_schema_enum_is_rejected(self) -> None:
        # 'index' is NOT in node.schema.json's type enum -- the closest real
        # value is 'governance', and a builder must pick a real one.
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            _write_builder(directory, "bad_type", node_type="index")
            with self.assertRaisesRegex(indexes.SpecError, "bad_type.*node_type"):
                indexes.discover_builders(directory)

    def test_inverse_relationship_type_in_spec_is_rejected(self) -> None:
        # Inverse edges are derived, never authored -- a SPEC hand-declaring
        # one must fail loudly (relationships.schema.json / MUST 6).
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            _write_builder(
                directory,
                "bad_rel",
                relationships=[{"type": "depended-on-by", "target": "some-node"}],
            )
            with self.assertRaisesRegex(indexes.SpecError, "generated, never authored"):
                indexes.discover_builders(directory)

    def test_output_path_escaping_the_corpus_root_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            _write_builder(directory, "escape", output_path="../outside.md")
            with self.assertRaisesRegex(indexes.SpecError, "inside the corpus root"):
                indexes.discover_builders(directory)


class GraphTest(unittest.TestCase):
    def test_broken_edge_is_reported_not_raised(self) -> None:
        ctx = indexes.build_context(BROKEN_DIR, [])
        self.assertEqual(
            ctx.broken_edges,
            (
                indexes.BrokenEdge(
                    source="fixture-index-broken-a",
                    type="depends-on",
                    target="fixture-index-missing",
                ),
            ),
        )

    def test_broken_target_never_enters_the_inverse_maps(self) -> None:
        ctx = indexes.build_context(BROKEN_DIR, [])
        self.assertNotIn("fixture-index-missing", ctx.inverse_edges["depended-on-by"])

    def test_orphan_is_reported(self) -> None:
        # broken-a has an out-edge (albeit broken), so only the true isolate
        # is an orphan.
        ctx = indexes.build_context(BROKEN_DIR, [])
        self.assertEqual(ctx.orphans, ("fixture-index-orphan",))

    def test_clean_fixture_has_no_orphans_or_broken_edges(self) -> None:
        ctx = indexes.build_context(CLEAN_DIR, [])
        self.assertEqual(ctx.orphans, ())
        self.assertEqual(ctx.broken_edges, ())

    def test_all_four_generated_inverse_types_are_derived(self) -> None:
        ctx = indexes.build_context(CLEAN_DIR, [])
        self.assertEqual(
            ctx.inverse_edges["depended-on-by"],
            {"fixture-index-alpha": ("fixture-index-beta",)},
        )
        self.assertEqual(
            ctx.inverse_edges["superseded-by"],
            {"fixture-index-delta": ("fixture-index-beta",)},
        )
        self.assertEqual(
            ctx.inverse_edges["implemented-by"],
            {"fixture-index-alpha": ("fixture-index-gamma",)},
        )
        self.assertEqual(
            ctx.inverse_edges["has-part"],
            {"fixture-index-beta": ("fixture-index-gamma",)},
        )

    def test_referenced_by_is_never_derived(self) -> None:
        # references -> referenced-by is marked `authored` in
        # relationships.schema.json, so it must not appear as a derived map,
        # even though the clean fixture carries a references edge.
        ctx = indexes.build_context(CLEAN_DIR, [])
        self.assertNotIn("referenced-by", ctx.inverse_edges)
        self.assertIn(
            indexes.Edge(
                source="fixture-index-gamma",
                type="references",
                target="fixture-index-delta",
            ),
            ctx.forward_edges,
        )

    def test_context_ordering_is_deterministic(self) -> None:
        ctx = indexes.build_context(CLEAN_DIR, [])
        self.assertEqual(list(ctx.node_ids), sorted(ctx.node_ids))
        paths = [n.path for n in ctx.nodes]
        self.assertEqual(paths, sorted(paths))
        self.assertEqual(
            list(ctx.forward_edges),
            sorted(ctx.forward_edges, key=lambda e: (e.source, e.type, e.target)),
        )


class GenerationTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name) / "corpus"
        shutil.copytree(CLEAN_DIR, self.root)
        self.output = self.root / OUTPUT_REL

    def _generate(self) -> int:
        code, _out, _err = _run_main(
            ["--all", "--root", str(self.root), "--defs-dir", str(DEFS_DIR)]
        )
        return code

    def _check(self) -> int:
        code, _out, _err = _run_main(
            ["--check", "--root", str(self.root), "--defs-dir", str(DEFS_DIR)]
        )
        return code

    def test_no_change_regeneration_is_byte_identical(self) -> None:
        self.assertEqual(self._generate(), 0)
        first = self.output.read_bytes()
        self.assertEqual(self._generate(), 0)
        self.assertEqual(first, self.output.read_bytes())

    def test_check_passes_after_generate_and_fails_after_tamper(self) -> None:
        self.assertEqual(self._generate(), 0)
        self.assertEqual(self._check(), 0)
        self.output.write_bytes(self.output.read_bytes() + b"tampered\n")
        self.assertEqual(self._check(), 1)

    def test_check_fails_when_the_output_is_missing(self) -> None:
        self.assertEqual(self._check(), 1)

    def test_output_carries_do_not_edit_marker_and_digest(self) -> None:
        self.assertEqual(self._generate(), 0)
        text = self.output.read_text()
        self.assertIn("Generated -- do not edit by hand", text)
        self.assertIn("launchpad/project-intelligence/corpus/indexes.py", text)
        ctx = indexes.build_context(
            self.root, indexes.discover_builders(DEFS_DIR)
        )
        self.assertIn(f"sha256:{ctx.input_digest}", text)
        self.assertEqual(len(ctx.input_digest), 64)

    def test_output_is_lf_only_with_single_trailing_newline(self) -> None:
        self.assertEqual(self._generate(), 0)
        raw = self.output.read_bytes()
        self.assertNotIn(b"\r", raw)
        self.assertTrue(raw.endswith(b"\n"))
        self.assertFalse(raw.endswith(b"\n\n"))

    def test_outputs_are_excluded_from_canonical_inputs(self) -> None:
        specs = indexes.discover_builders(DEFS_DIR)
        digest_before = indexes.build_context(self.root, specs).input_digest
        self.assertEqual(self._generate(), 0)
        after = indexes.build_context(self.root, specs)
        # The output now exists on disk, but neither the input set nor the
        # digest may see it -- a generated view never feeds itself.
        self.assertEqual(after.input_digest, digest_before)
        input_rels = {
            p.relative_to(self.root).as_posix()
            for p in indexes.canonical_input_paths(self.root, specs)
        }
        self.assertNotIn(OUTPUT_REL, input_rels)

    def test_generated_node_passes_the_validator_contract(self) -> None:
        self.assertEqual(self._generate(), 0)
        report = validate.validate_corpus(self.root)
        self.assertEqual(report.errors, [])
        loaded = {
            node.id: node for node in validate.load_nodes(self.root)
        }
        generated = loaded["fixture-generated-demo-index"]
        self.assertIsNone(generated.error)
        self.assertEqual(generated.data["status"], "draft")
        self.assertEqual(generated.data["origin"], "launchpad")

    def test_listing_rows_present_and_sorted(self) -> None:
        self.assertEqual(self._generate(), 0)
        text = self.output.read_text()
        positions = [
            text.index(node_id)
            for node_id in (
                "fixture-index-alpha",
                "fixture-index-beta",
                "fixture-index-delta",
                "fixture-index-gamma",
            )
        ]
        self.assertEqual(positions, sorted(positions))


class CliTest(unittest.TestCase):
    def test_list_names_the_fixture_builder(self) -> None:
        code, out, _err = _run_main(["--list", "--defs-dir", str(DEFS_DIR)])
        self.assertEqual(code, 0)
        self.assertIn("demo-index", out)
        self.assertIn(OUTPUT_REL, out)

    def test_check_with_no_builders_exits_zero(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            code, out, _err = _run_main(
                ["--check", "--root", str(CLEAN_DIR), "--defs-dir", str(tmp)]
            )
        self.assertEqual(code, 0)
        self.assertIn("no builders registered", out)

    def test_unknown_only_name_fails_naming_the_known_builders(self) -> None:
        code, _out, err = _run_main(
            [
                "--only",
                "no-such-builder",
                "--root",
                str(CLEAN_DIR),
                "--defs-dir",
                str(DEFS_DIR),
            ]
        )
        self.assertEqual(code, 1)
        self.assertIn("no-such-builder", err)
        self.assertIn("demo-index", err)

    def test_missing_corpus_root_fails_cleanly(self) -> None:
        code, _out, err = _run_main(
            [
                "--check",
                "--root",
                str(FIXTURES_DIR / "does-not-exist"),
                "--defs-dir",
                str(DEFS_DIR),
            ]
        )
        self.assertEqual(code, 1)
        self.assertIn("corpus root does not exist", err)

    def test_all_and_only_are_mutually_exclusive(self) -> None:
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                indexes.main(["--all", "--only", "demo-index"])

    def test_an_action_flag_is_required(self) -> None:
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                indexes.main([])

    def test_broken_builder_module_fails_with_its_module_name(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            (directory / "exploding.py").write_text("raise RuntimeError('boom')")
            code, _out, err = _run_main(
                ["--list", "--defs-dir", str(directory)]
            )
        self.assertEqual(code, 1)
        self.assertIn("exploding.py", err)


if __name__ == "__main__":
    unittest.main()
