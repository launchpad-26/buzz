#!/usr/bin/env python3
"""Controls for goose_config.py's read-merge-write logic.

STEP 4 of issue #239 (the Route 3 projector): goose's `developer` extension
(write/shell capability) is a config-FILE toggle
(`~/.config/goose/config.yaml`, or `$GOOSE_PATH_ROOT/config/config.yaml`),
and nothing in this repository writes that file today
(`desktop/src-tauri/src/managed_agents/config_bridge/goose.rs` is
read-only). These tests drive the module's pure functions directly, plus one
end-to-end pass against a real temp file for the atomic-write and
idempotency guarantees the plan's own done-when demands.

Run:  python3 -m unittest discover -s launchpad/agents -p "test_*.py"
"""

from __future__ import annotations

import importlib.util
import os
import stat
import tempfile
import unittest
from pathlib import Path

_SPEC = importlib.util.spec_from_file_location(
    "goose_config", Path(__file__).resolve().parent / "goose_config.py"
)
m = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(m)


class GooseConfigPathTests(unittest.TestCase):
    def test_uses_goose_path_root_when_set(self):
        path = m.goose_config_path({"GOOSE_PATH_ROOT": "/custom/root"})
        self.assertEqual(path, Path("/custom/root/config/config.yaml"))

    def test_defaults_to_home_config_goose_when_unset(self):
        path = m.goose_config_path({})
        self.assertEqual(path, Path.home() / ".config" / "goose" / "config.yaml")

    def test_empty_goose_path_root_mirrors_rust_treating_it_as_set(self):
        # Rust's std::env::var("GOOSE_PATH_ROOT") returns Ok("") for a
        # set-but-empty variable, so goose.rs's own resolution does NOT
        # treat empty as unset. This module mirrors that exactly, even
        # though it is arguably a footgun -- diverging would mean this
        # script patches a different file than the one goose itself reads.
        path = m.goose_config_path({"GOOSE_PATH_ROOT": ""})
        self.assertEqual(path, Path("config/config.yaml"))


class ReadConfigTests(unittest.TestCase):
    def test_missing_file_returns_empty_dict(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(m.read_config(Path(d) / "does-not-exist.yaml"), {})

    def test_reads_existing_mapping(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "config.yaml"
            path.write_text("active_provider: anthropic\n", encoding="utf-8")
            self.assertEqual(m.read_config(path), {"active_provider": "anthropic"})

    def test_empty_file_returns_empty_dict(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "config.yaml"
            path.write_text("", encoding="utf-8")
            self.assertEqual(m.read_config(path), {})

    def test_invalid_yaml_raises_goose_config_error(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "config.yaml"
            path.write_text("{{{{not valid", encoding="utf-8")
            with self.assertRaises(m.GooseConfigError):
                m.read_config(path)

    def test_non_mapping_top_level_raises_goose_config_error(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "config.yaml"
            path.write_text("- just\n- a\n- list\n", encoding="utf-8")
            with self.assertRaises(m.GooseConfigError):
                m.read_config(path)

    def test_preserves_comments_on_round_trip(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "config.yaml"
            path.write_text(
                "# managed by ansible -- do not edit by hand\n"
                'active_provider: databricks_v2  # production creds\n',
                encoding="utf-8",
            )
            cfg = m.read_config(path)
            m.write_config_atomic(path, cfg)
            written = path.read_text(encoding="utf-8")
            self.assertIn("# managed by ansible -- do not edit by hand", written)
            self.assertIn("# production creds", written)


# The fixture below is RAW TEXT on purpose, not built by calling this module's
# own writer. An earlier version of these controls built every fixture with
# write_config_atomic(), so both the "before" and the "after" had already been
# through the same serializer -- which is exactly the shape that cannot detect a
# serializer that mangles human-authored YAML. review-code found this twice
# independently. It carries a top-of-file comment, an inline comment on a
# top-level key, a comment nested two levels deep, a deliberately quoted scalar,
# and an inline comment inside `extensions` -- the block this module writes into.
OPERATOR_AUTHORED_CONFIG = """\
# top-of-file: managed by ansible, do not edit by hand
active_provider: databricks_v2   # inline on a top-level key
providers:
  databricks_v2:
    # a comment nested two levels deep
    model: goose-claude-4-6-opus
    host: "https://dbc.example"   # quoted on purpose
extensions:
  my-mcp:
    type: stdio      # inline inside the block this module writes into
    enabled: false
"""


class OperatorAuthoredConfigTests(unittest.TestCase):
    """The guarantee this module exists for, exercised through the REAL entry
    point (`enable_developer_extension`, merge included) against a file a human
    wrote by hand.

    The distinction matters and was a genuine coverage gap: comment
    preservation was previously only asserted across read_config ->
    write_config_atomic, which skips merge_developer_extension entirely. Since
    the merge copies the mapping (`config.copy()` / `CommentedMap(...)`), a copy
    that dropped ruamel's comment attachments would have lost every comment on
    the real path while the old test still passed."""

    def _write_fixture(self, d: str) -> Path:
        path = Path(d) / "config.yaml"
        path.write_text(OPERATOR_AUTHORED_CONFIG, encoding="utf-8")
        return path

    def test_merge_preserves_every_comment_and_quoting_style(self):
        with tempfile.TemporaryDirectory() as d:
            path = self._write_fixture(d)
            m.enable_developer_extension(path=path)
            written = path.read_text(encoding="utf-8")

            for probe in (
                "# top-of-file: managed by ansible, do not edit by hand",
                "# inline on a top-level key",
                "# a comment nested two levels deep",
                "# quoted on purpose",
                "# inline inside the block this module writes into",
            ):
                self.assertIn(probe, written, f"comment lost through merge: {probe}")

            # The quoting style itself, not just the value: PyYAML's dumper
            # re-emits this unquoted, which is how the original Blocker was found.
            self.assertIn('host: "https://dbc.example"', written)

    def test_merge_adds_developer_without_disturbing_existing_extension(self):
        with tempfile.TemporaryDirectory() as d:
            path = self._write_fixture(d)
            m.enable_developer_extension(path=path)
            cfg = m.read_config(path)
            self.assertEqual(
                cfg["extensions"]["my-mcp"], {"type": "stdio", "enabled": False}
            )
            self.assertEqual(
                cfg["extensions"]["developer"], {"type": "builtin", "enabled": True}
            )
            self.assertEqual(cfg["active_provider"], "databricks_v2")

    def test_second_run_on_operator_authored_file_is_byte_for_byte_no_op(self):
        with tempfile.TemporaryDirectory() as d:
            path = self._write_fixture(d)
            m.enable_developer_extension(path=path)
            after_first = path.read_bytes()
            m.enable_developer_extension(path=path)
            self.assertEqual(
                after_first,
                path.read_bytes(),
                "a second run against a human-authored file must be a no-op",
            )

    def test_only_addition_is_the_developer_block(self):
        """BYTE-EXACT: the output is the input with the developer block appended
        and nothing else changed at all.

        An earlier version of this control compared line *membership*
        (`[ln for ln in written.splitlines() if ln in original_lines]`), which
        cross-vendor review correctly called weaker than its own docstring
        claimed: `splitlines()` discards a missing trailing newline, hides a
        CRLF/LF conversion, and would tolerate the three new lines being
        interleaved anywhere among the originals. Comparing the whole string
        closes all three at once and needs no separate ordering argument."""
        with tempfile.TemporaryDirectory() as d:
            path = self._write_fixture(d)
            m.enable_developer_extension(path=path)

            expected = OPERATOR_AUTHORED_CONFIG + (
                "  developer:\n" "    type: builtin\n" "    enabled: true\n"
            )
            self.assertEqual(
                path.read_text(encoding="utf-8"),
                expected,
                "output must be the operator's file byte-for-byte, plus only "
                "the appended developer block",
            )


class MergeDeveloperExtensionTests(unittest.TestCase):
    def test_adds_developer_extension_when_absent(self):
        merged = m.merge_developer_extension({})
        self.assertEqual(
            merged["extensions"]["developer"], {"type": "builtin", "enabled": True}
        )

    def test_preserves_unrelated_top_level_keys(self):
        original = {
            "active_provider": "databricks_v2",
            "providers": {"databricks_v2": {"model": "goose-claude-4-6-opus"}},
        }
        merged = m.merge_developer_extension(original)
        self.assertEqual(merged["active_provider"], "databricks_v2")
        self.assertEqual(
            merged["providers"]["databricks_v2"]["model"], "goose-claude-4-6-opus"
        )

    def test_preserves_other_extensions(self):
        original = {
            "extensions": {"my-mcp": {"type": "stdio", "enabled": False}},
        }
        merged = m.merge_developer_extension(original)
        self.assertEqual(
            merged["extensions"]["my-mcp"], {"type": "stdio", "enabled": False}
        )
        self.assertEqual(
            merged["extensions"]["developer"], {"type": "builtin", "enabled": True}
        )

    def test_does_not_mutate_the_input(self):
        original = {"extensions": {"my-mcp": {"type": "stdio", "enabled": False}}}
        m.merge_developer_extension(original)
        self.assertNotIn("developer", original["extensions"])

    def test_is_idempotent_when_developer_already_enabled(self):
        once = m.merge_developer_extension({})
        twice = m.merge_developer_extension(once)
        self.assertEqual(once, twice)

    def test_overwrites_a_disabled_developer_entry_to_enabled(self):
        original = {"extensions": {"developer": {"type": "builtin", "enabled": False}}}
        merged = m.merge_developer_extension(original)
        self.assertEqual(
            merged["extensions"]["developer"], {"type": "builtin", "enabled": True}
        )

    def test_non_mapping_extensions_key_raises_goose_config_error(self):
        with self.assertRaises(m.GooseConfigError):
            m.merge_developer_extension({"extensions": ["not", "a", "mapping"]})


class WriteConfigAtomicTests(unittest.TestCase):
    def test_creates_parent_directory_and_file(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "nested" / "config.yaml"
            m.write_config_atomic(path, {"a": 1})
            self.assertTrue(path.is_file())
            self.assertEqual(m.read_config(path), {"a": 1})

    def test_leaves_no_temp_files_behind_on_success(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "config.yaml"
            m.write_config_atomic(path, {"a": 1})
            self.assertEqual(os.listdir(d), ["config.yaml"])

    def test_overwrites_existing_file(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "config.yaml"
            path.write_text("stale: true\n", encoding="utf-8")
            m.write_config_atomic(path, {"fresh": True})
            self.assertEqual(m.read_config(path), {"fresh": True})

    def test_preserves_existing_file_permissions(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "config.yaml"
            path.write_text("a: 1\n", encoding="utf-8")
            os.chmod(path, 0o644)
            m.write_config_atomic(path, {"a": 2})
            self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o644)

    def test_writes_through_a_symlink_rather_than_replacing_it(self):
        with tempfile.TemporaryDirectory() as d:
            real_path = Path(d) / "real-config.yaml"
            m.write_config_atomic(real_path, {"stale": True})
            link_path = Path(d) / "config.yaml"
            link_path.symlink_to(real_path)

            m.write_config_atomic(link_path, {"fresh": True})

            self.assertTrue(link_path.is_symlink(), "the symlink must survive the write")
            self.assertEqual(link_path.resolve(), real_path)
            self.assertEqual(m.read_config(real_path), {"fresh": True})


class EnableDeveloperExtensionEndToEndTests(unittest.TestCase):
    """The plan's own done-when for STEP 4: run twice against a fixture
    carrying an unrelated provider block and one other extension -- both
    survive byte-for-byte except the added/updated developer entry, and the
    second run is a no-op (idempotent, not append-again)."""

    def _fixture_path(self, d: str) -> Path:
        path = Path(d) / "config.yaml"
        fixture = {
            "active_provider": "databricks_v2",
            "providers": {
                "databricks_v2": {
                    "model": "goose-claude-4-6-opus",
                    "host": "https://dbc.example",
                }
            },
            "extensions": {"my-mcp": {"type": "stdio", "enabled": False}},
        }
        m.write_config_atomic(path, fixture)
        return path

    def test_creates_file_when_none_exists(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "config.yaml"
            self.assertFalse(path.exists())
            written = m.enable_developer_extension(path=path)
            self.assertEqual(written, path)
            cfg = m.read_config(path)
            self.assertEqual(
                cfg["extensions"]["developer"], {"type": "builtin", "enabled": True}
            )

    def test_preserves_unrelated_provider_block_and_other_extension(self):
        with tempfile.TemporaryDirectory() as d:
            path = self._fixture_path(d)
            m.enable_developer_extension(path=path)
            cfg = m.read_config(path)
            self.assertEqual(cfg["active_provider"], "databricks_v2")
            self.assertEqual(
                cfg["providers"]["databricks_v2"]["model"], "goose-claude-4-6-opus"
            )
            self.assertEqual(
                cfg["extensions"]["my-mcp"], {"type": "stdio", "enabled": False}
            )
            self.assertEqual(
                cfg["extensions"]["developer"], {"type": "builtin", "enabled": True}
            )

    def test_second_run_is_a_byte_for_byte_no_op(self):
        with tempfile.TemporaryDirectory() as d:
            path = self._fixture_path(d)
            m.enable_developer_extension(path=path)
            after_first = path.read_bytes()
            m.enable_developer_extension(path=path)
            after_second = path.read_bytes()
            self.assertEqual(
                after_first,
                after_second,
                "a second run must be a no-op, not append-again",
            )

    def test_defaults_to_goose_config_path_when_no_path_given(self):
        with tempfile.TemporaryDirectory() as d:
            fixture_path = Path(d) / "config" / "config.yaml"
            fixture_path.parent.mkdir(parents=True)
            m.write_config_atomic(fixture_path, {"active_provider": "anthropic"})
            written = m.enable_developer_extension(env={"GOOSE_PATH_ROOT": d})
            self.assertEqual(written, fixture_path)
            cfg = m.read_config(fixture_path)
            self.assertEqual(cfg["active_provider"], "anthropic")
            self.assertEqual(
                cfg["extensions"]["developer"], {"type": "builtin", "enabled": True}
            )


if __name__ == "__main__":
    unittest.main()
