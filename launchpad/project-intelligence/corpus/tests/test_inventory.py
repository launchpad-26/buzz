"""Unit tests for the deterministic Buzz source inventory -- issue #624.

Run:  python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"

Every test builds its own throwaway fixture tree under a `tempfile.TemporaryDirectory`
and points `--root`/`run_inventory` at it, mirroring `test_validate.py`'s rule of never
depending on the real repository tree for content assertions -- a category's
discovery is only exercised through the shape it is documented to recognise, not
through whatever this repository happens to contain today, which would make a test
pass or fail for reasons unrelated to the code under test.

ONE test is deliberately outside that rule:
`RealRepoDiscoveryTest.test_real_repo_produces_rust_crate_and_event_kind_items`
runs against the actual repository root and asserts it finds at least one rust_crate
and one event_kind item. It exists to catch a discovery regression against real
committed content no fixture stands in for, and will legitimately fail if
crates/buzz-core/src/kind.rs or the workspace Cargo.toml are ever restructured --
at which point it is reporting that, not a bug in this test.
"""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

# inventory.py lives in a directory (project-intelligence/corpus/) that isn't a
# package (no __init__.py, matching this repo's existing project-intelligence/
# convention), so it's loaded by path rather than imported by dotted name --
# the same pattern test_validate.py uses for validate.py.
_INVENTORY_PATH = Path(__file__).resolve().parent.parent / "inventory.py"
_spec = importlib.util.spec_from_file_location("corpus_inventory", _INVENTORY_PATH)
inventory = importlib.util.module_from_spec(_spec)
sys.modules["corpus_inventory"] = inventory
_spec.loader.exec_module(inventory)

REPO_ROOT = Path(
    __import__("subprocess")
    .run(["git", "rev-parse", "--show-toplevel"], cwd=Path(__file__).resolve().parent, capture_output=True, text=True)
    .stdout.strip()
)


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


class RustCrateDiscoveryTest(unittest.TestCase):
    def test_finds_workspace_members_by_declared_package_name(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(
                root / "Cargo.toml",
                '[workspace]\nmembers = [\n    "crates/buzz-relay",\n    "crates/buzz-core",\n]\n',
            )
            _write(root / "crates" / "buzz-relay" / "Cargo.toml", '[package]\nname = "buzz-relay"\n')
            _write(root / "crates" / "buzz-core" / "Cargo.toml", '[package]\nname = "buzz-core"\n')

            items = inventory.discover_rust_crates(root)

        keys = {item.source_key for item in items}
        self.assertEqual(keys, {"rust_crate:buzz-relay", "rust_crate:buzz-core"})
        self.assertTrue(all(item.category == "rust_crate" for item in items))

    def test_falls_back_to_the_manifest_path_when_no_member_cargo_toml_exists(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(root / "Cargo.toml", '[workspace]\nmembers = [\n    "crates/ghost-crate",\n]\n')

            items = inventory.discover_rust_crates(root)

        self.assertEqual([item.source_key for item in items], ["rust_crate:crates/ghost-crate"])

    def test_missing_cargo_toml_returns_no_items_not_an_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(inventory.discover_rust_crates(Path(tmp)), [])


class EventKindDiscoveryTest(unittest.TestCase):
    def test_finds_kind_constants_with_line_numbers(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(
                root / "crates" / "buzz-core" / "src" / "kind.rs",
                "// header\npub const KIND_TEXT_NOTE: u32 = 1;\npub const KIND_REACTION: u32 = 7;\n",
            )

            items = inventory.discover_event_kinds(root)

        self.assertEqual(len(items), 2)
        by_symbol = {item.symbol: item for item in items}
        self.assertEqual(by_symbol["KIND_TEXT_NOTE"].path, "crates/buzz-core/src/kind.rs:2")
        self.assertEqual(by_symbol["KIND_REACTION"].path, "crates/buzz-core/src/kind.rs:3")
        self.assertEqual(by_symbol["KIND_TEXT_NOTE"].source_key, "event_kind:KIND_TEXT_NOTE")

    def test_ignores_non_kind_constants(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(
                root / "crates" / "buzz-core" / "src" / "kind.rs",
                'pub const AUTHOR_ONLY_KINDS: &[u32] = &[KIND_TEXT_NOTE];\n',
            )

            self.assertEqual(inventory.discover_event_kinds(root), [])


class ClientFeatureDiscoveryTest(unittest.TestCase):
    def test_desktop_features_are_one_item_per_top_level_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "desktop" / "src" / "features" / "chat").mkdir(parents=True)
            (root / "desktop" / "src" / "features" / "settings").mkdir(parents=True)
            _write(root / "desktop" / "src" / "features" / "README.md", "not a feature dir")

            items = inventory.discover_desktop_features(root)

        keys = {item.source_key for item in items}
        self.assertEqual(keys, {"desktop_feature:chat", "desktop_feature:settings"})

    def test_mobile_and_web_features_use_their_own_category(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "mobile" / "lib" / "features" / "home").mkdir(parents=True)
            (root / "web" / "src" / "features" / "search").mkdir(parents=True)

            mobile_items = inventory.discover_mobile_features(root)
            web_items = inventory.discover_web_features(root)

        self.assertEqual([i.source_key for i in mobile_items], ["mobile_feature:home"])
        self.assertEqual([i.source_key for i in web_items], ["web_feature:search"])


class MigrationDiscoveryTest(unittest.TestCase):
    def test_finds_one_item_per_sql_file_keyed_by_stem(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(root / "migrations" / "0001_initial_schema.sql", "-- migration\n")
            _write(root / "migrations" / "0002_moderation.sql", "-- migration\n")
            _write(root / "migrations" / "README.md", "not a migration")

            items = inventory.discover_migrations(root)

        self.assertEqual(
            {item.source_key for item in items},
            {"migration:0001_initial_schema", "migration:0002_moderation"},
        )


class RelayRouteDiscoveryTest(unittest.TestCase):
    def test_finds_route_registrations_across_multiple_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(
                root / "crates" / "buzz-relay" / "src" / "router.rs",
                '.route("/health", get(health_handler))\n.route("/events", post(submit_event))\n',
            )
            _write(
                root / "crates" / "buzz-relay" / "src" / "api" / "media.rs",
                '.route("/upload", put(upload_blob))\n',
            )

            items = inventory.discover_relay_routes(root)

        symbols = {item.symbol for item in items}
        self.assertEqual(symbols, {"/health", "/events", "/upload"})
        self.assertTrue(all(item.category == "relay_route" for item in items))


class ConfigurationDiscoveryTest(unittest.TestCase):
    def test_finds_env_example_keys(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(root / ".env.example", "# comment, not a key\nBUZZ_RELAY_URL=ws://localhost:3000\nBUZZ_AUTH_TAG=\n")

            items = inventory.discover_configuration(root)

        self.assertEqual(
            {item.symbol for item in items},
            {"BUZZ_RELAY_URL", "BUZZ_AUTH_TAG"},
        )


class DocumentationDiscoveryTest(unittest.TestCase):
    def test_finds_root_and_nested_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(root / "ARCHITECTURE.md", "# arch\n")
            _write(root / "docs" / "nips" / "nip-01.md", "# nip\n")
            _write(root / "docs" / "formal" / "model.py", "# not markdown\n")

            items = inventory.discover_existing_docs(root)

        keys = {item.source_key for item in items}
        self.assertEqual(keys, {"existing_doc:ARCHITECTURE.md", "existing_doc:docs/nips/nip-01.md"})


class FormalModelDiscoveryTest(unittest.TestCase):
    def test_finds_python_models_under_docs_formal(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(root / "docs" / "formal" / "nip-pl" / "delivery.py", "# model\n")
            _write(root / "docs" / "formal" / "STATEFUL_GATEWAY.md", "# not python\n")

            items = inventory.discover_formal_models(root)

        self.assertEqual([item.source_key for item in items], ["formal_model:nip-pl/delivery"])


class UnrecognizedAreaTest(unittest.TestCase):
    def test_unknown_top_level_directory_is_reported_not_dropped(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "crates").mkdir()
            (root / "some-new-surface").mkdir()

            areas = inventory.discover_unrecognized_areas(root)

        self.assertEqual(areas, ["some-new-surface"])

    def test_known_and_ignored_directories_are_never_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name in ["crates", "desktop", "mobile", "web", "migrations", "docs", "examples"]:
                (root / name).mkdir()
            for name in [".git", "target", "node_modules", "launchpad", "__worktrees"]:
                (root / name).mkdir()

            self.assertEqual(inventory.discover_unrecognized_areas(root), [])

    def test_files_at_the_top_level_are_never_treated_as_areas(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(root / "README.md", "not a directory")

            self.assertEqual(inventory.discover_unrecognized_areas(root), [])


class DeterminismTest(unittest.TestCase):
    def test_rerun_against_unchanged_tree_is_byte_identical(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(root / "Cargo.toml", '[workspace]\nmembers = [\n    "crates/buzz-core",\n]\n')
            _write(root / "crates" / "buzz-core" / "Cargo.toml", '[package]\nname = "buzz-core"\n')
            _write(root / "crates" / "buzz-core" / "src" / "kind.rs", "pub const KIND_TEXT_NOTE: u32 = 1;\n")
            _write(root / "migrations" / "0001_initial_schema.sql", "-- migration\n")
            (root / "extra-surface").mkdir()

            first = inventory.run_inventory(root).to_json()
            second = inventory.run_inventory(root).to_json()

        self.assertEqual(first, second)
        # Sanity check the JSON is well-formed and carries both channels.
        payload = json.loads(first)
        self.assertIn("items", payload)
        self.assertIn("unrecognized_areas", payload)
        self.assertEqual(payload["unrecognized_areas"], ["extra-surface"])

    def test_output_is_sorted_regardless_of_filesystem_iteration_order(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(root / "migrations" / "0002_second.sql", "-- migration\n")
            _write(root / "migrations" / "0001_first.sql", "-- migration\n")

            report = inventory.run_inventory(root)

        keys = [item.source_key for item in report.items]
        self.assertEqual(keys, sorted(keys))


class RealRepoDiscoveryTest(unittest.TestCase):
    """The one test that reads the real repository -- see module docstring."""

    def test_real_repo_produces_rust_crate_and_event_kind_items(self) -> None:
        report = inventory.run_inventory(REPO_ROOT)
        categories = {item.category for item in report.items}
        self.assertIn("rust_crate", categories)
        self.assertIn("event_kind", categories)
        self.assertIn("migration", categories)


if __name__ == "__main__":
    unittest.main()
