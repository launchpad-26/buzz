"""Unit tests for the one-node corpus scaffold helper -- issue #632.

Run:  python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"

Every test builds a throwaway fixture root under `tempfile.TemporaryDirectory`,
copying the REAL `node.schema.json` into it (never a hand-copied second
enum list, which would drift silently) and creating a fake template file so
`_known_templates` recognises it. One test also runs the real `validate.py`
against a scaffolded node, to check this module's output is not merely
schema-shaped in isolation but genuinely passes the corpus's own checker.
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

_CORPUS_DIR = Path(__file__).resolve().parent.parent
_REAL_SCHEMA_PATH = _CORPUS_DIR.parent.parent / "docs" / "corpus" / "schema" / "node.schema.json"

_SCAFFOLD_PATH = _CORPUS_DIR / "scaffold.py"
_spec = importlib.util.spec_from_file_location("corpus_scaffold", _SCAFFOLD_PATH)
scaffold = importlib.util.module_from_spec(_spec)
sys.modules["corpus_scaffold"] = scaffold
_spec.loader.exec_module(scaffold)

manifest = scaffold.manifest  # already loaded by scaffold.py itself


def _make_row(**overrides) -> "manifest.ManifestRow":
    base = dict(
        path="launchpad/docs/corpus/capabilities/chat.md",
        filename="chat.md",
        issue_title="task: document capabilities/chat.md",
        parent_feature="#608",
        priority="P2",
        start_date=None,
        target_date=None,
        effort="M",
        blockers=(),
        template="capability",
        purpose="Describe the chat capability's contract.",
        audiences=("agent", "developer"),
        source_start_points=("desktop_feature:chat",),
    )
    base.update(overrides)
    return manifest.ManifestRow(**base)


def _fixture_root(tmp: str) -> Path:
    """A throwaway repo root carrying the REAL schema plus one known template."""
    root = Path(tmp)
    schema_dir = root / "launchpad" / "docs" / "corpus" / "schema"
    schema_dir.mkdir(parents=True)
    (schema_dir / "node.schema.json").write_text(_REAL_SCHEMA_PATH.read_text())
    templates_dir = root / "launchpad" / "docs" / "corpus" / "templates"
    templates_dir.mkdir(parents=True)
    # A real template doc is itself a corpus node (type: governance, per the
    # corpus batch's finding that node.schema.json's type enum has no
    # template/policy value) -- give this fixture one too, so a test running
    # the real validator over it is exercising a realistic tree, not one
    # that fails for a reason unrelated to scaffold.py.
    (templates_dir / "capability.md").write_text(
        "---\n"
        "id: corpus-template-capability\n"
        "type: governance\n"
        "status: active\n"
        "origin: launchpad\n"
        "audiences:\n"
        "  - agent\n"
        "evidence:\n"
        "  - statement: \"Fixture template, not a real corpus document.\"\n"
        "    entry_class: TEAM_KNOWLEDGE\n"
        "    provided_by: \"test_scaffold.py fixture\"\n"
        "---\n\n# Capability template\n"
    )
    return root


class SuccessfulCreateTest(unittest.TestCase):
    def test_creates_the_file_with_schema_valid_front_matter(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _fixture_root(tmp)
            row = _make_row()

            target = scaffold.scaffold_node(
                root, row, node_type="capabilities", origin="launchpad", revision="deadbeef" * 5
            )

            self.assertTrue(target.exists())
            text = target.read_text()
            front_matter_text = text.split("---\n")[1]
            front_matter = yaml.safe_load(front_matter_text)
            self.assertEqual(front_matter["id"], "chat")
            self.assertEqual(front_matter["type"], "capabilities")
            self.assertEqual(front_matter["origin"], "launchpad")
            self.assertEqual(front_matter["status"], "draft")
            self.assertEqual(front_matter["audiences"], ["agent", "developer"])
            self.assertEqual(len(front_matter["evidence"]), 1)
            self.assertEqual(front_matter["evidence"][0]["entry_class"], "FACT")

    def test_scaffolded_node_actually_passes_the_real_validator(self) -> None:
        validate_path = _CORPUS_DIR / "validate.py"
        vspec = importlib.util.spec_from_file_location("corpus_validate_for_scaffold_test", validate_path)
        validate = importlib.util.module_from_spec(vspec)
        sys.modules[vspec.name] = validate
        vspec.loader.exec_module(validate)

        revision = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=validate.repo_root(),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        ).stdout.strip()

        with tempfile.TemporaryDirectory() as tmp:
            root = _fixture_root(tmp)
            row = _make_row()
            scaffold.scaffold_node(root, row, node_type="capabilities", origin="launchpad", revision=revision)
            corpus_root = root / "launchpad" / "docs" / "corpus"
            report = validate.validate_corpus(corpus_root)

            self.assertEqual(report.errors, [])


class ModeTest(unittest.TestCase):
    def test_create_mode_refuses_an_existing_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _fixture_root(tmp)
            row = _make_row()
            scaffold.scaffold_node(root, row, node_type="capabilities", origin="launchpad", revision="a" * 40)

            with self.assertRaises(scaffold.ScaffoldError) as ctx:
                scaffold.scaffold_node(root, row, node_type="capabilities", origin="launchpad", revision="b" * 40)
        self.assertIn("already exists", str(ctx.exception))

    def test_update_mode_requires_the_file_to_already_exist(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _fixture_root(tmp)
            row = _make_row()

            with self.assertRaises(scaffold.ScaffoldError) as ctx:
                scaffold.scaffold_node(
                    root, row, node_type="capabilities", origin="launchpad", revision="a" * 40, mode="update"
                )
        self.assertIn("does not exist", str(ctx.exception))

    def test_update_mode_overwrites_an_existing_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _fixture_root(tmp)
            row = _make_row()
            scaffold.scaffold_node(root, row, node_type="capabilities", origin="launchpad", revision="a" * 40)

            target = scaffold.scaffold_node(
                root, row, node_type="capabilities", origin="launchpad", revision="c" * 40, mode="update"
            )

            self.assertIn("c" * 40, target.read_text())

    def test_unknown_mode_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _fixture_root(tmp)
            row = _make_row()
            with self.assertRaises(scaffold.ScaffoldError):
                scaffold.scaffold_node(root, row, node_type="capabilities", origin="launchpad", revision="a" * 40, mode="delete")


class UnknownTemplateTest(unittest.TestCase):
    def test_a_template_with_no_registered_file_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _fixture_root(tmp)
            row = _make_row(template="does-not-exist-template")

            with self.assertRaises(scaffold.ScaffoldError) as ctx:
                scaffold.scaffold_node(root, row, node_type="capabilities", origin="launchpad", revision="a" * 40)
        self.assertIn("unknown template", str(ctx.exception))

    def test_no_templates_directory_at_all_fails_closed_for_every_template(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            schema_dir = root / "launchpad" / "docs" / "corpus" / "schema"
            schema_dir.mkdir(parents=True)
            (schema_dir / "node.schema.json").write_text(_REAL_SCHEMA_PATH.read_text())
            # Deliberately no templates/ directory -- matches this repo's real state today.
            row = _make_row()

            with self.assertRaises(scaffold.ScaffoldError) as ctx:
                scaffold.scaffold_node(root, row, node_type="capabilities", origin="launchpad", revision="a" * 40)
        self.assertIn("unknown template", str(ctx.exception))


class InvalidSchemaValueTest(unittest.TestCase):
    def test_unknown_type_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _fixture_root(tmp)
            row = _make_row()
            with self.assertRaises(scaffold.ScaffoldError) as ctx:
                scaffold.scaffold_node(root, row, node_type="not-a-real-type", origin="launchpad", revision="a" * 40)
        self.assertIn("unknown type", str(ctx.exception))

    def test_unknown_origin_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _fixture_root(tmp)
            row = _make_row()
            with self.assertRaises(scaffold.ScaffoldError) as ctx:
                scaffold.scaffold_node(root, row, node_type="capabilities", origin="nowhere", revision="a" * 40)
        self.assertIn("unknown origin", str(ctx.exception))

    def test_unknown_status_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _fixture_root(tmp)
            row = _make_row()
            with self.assertRaises(scaffold.ScaffoldError) as ctx:
                scaffold.scaffold_node(
                    root, row, node_type="capabilities", origin="launchpad", revision="a" * 40, status="on-fire"
                )
        self.assertIn("unknown status", str(ctx.exception))

    def test_unknown_audience_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _fixture_root(tmp)
            row = _make_row(audiences=("agent", "goblin"))
            with self.assertRaises(scaffold.ScaffoldError) as ctx:
                scaffold.scaffold_node(root, row, node_type="capabilities", origin="launchpad", revision="a" * 40)
        self.assertIn("unknown audience", str(ctx.exception))

    def test_empty_audiences_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _fixture_root(tmp)
            row = _make_row(audiences=())
            with self.assertRaises(scaffold.ScaffoldError):
                scaffold.scaffold_node(root, row, node_type="capabilities", origin="launchpad", revision="a" * 40)


class PathSafetyTest(unittest.TestCase):
    def test_a_path_outside_the_corpus_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _fixture_root(tmp)
            row = _make_row(path="crates/buzz-relay/src/lib.rs", filename="lib.rs")
            with self.assertRaises(scaffold.ScaffoldError) as ctx:
                scaffold.scaffold_node(root, row, node_type="capabilities", origin="launchpad", revision="a" * 40)
        self.assertIn("not under", str(ctx.exception))

    def test_a_path_under_schema_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _fixture_root(tmp)
            row = _make_row(path="launchpad/docs/corpus/schema/sneaky.md", filename="sneaky.md")
            with self.assertRaises(scaffold.ScaffoldError) as ctx:
                scaffold.scaffold_node(root, row, node_type="capabilities", origin="launchpad", revision="a" * 40)
        self.assertIn("schema/", str(ctx.exception))

    def test_a_filename_that_does_not_derive_a_valid_id_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _fixture_root(tmp)
            row = _make_row(path="launchpad/docs/corpus/capabilities/Chat_Room.md", filename="Chat_Room.md")
            with self.assertRaises(scaffold.ScaffoldError) as ctx:
                scaffold.scaffold_node(root, row, node_type="capabilities", origin="launchpad", revision="a" * 40)
        self.assertIn("valid kebab-case id", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
