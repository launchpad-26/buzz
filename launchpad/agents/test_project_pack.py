#!/usr/bin/env python3
"""Controls for project-pack.py's pure projection logic.

Deliberately does not exercise inspect_pack()/find_buzz_binary() against a
real `buzz` binary -- that is covered by manually running the projector
against launchpad/agents/the-professor (see #239 STEP 2's PR). These tests
drive project_env_vars()/apply_operator_precedence()/render_env_file()
directly against already-parsed JSON shapes, so they run anywhere without a
cargo build.

Run:  python3 -m unittest discover -s launchpad/agents -p "test_*.py"
"""

from __future__ import annotations

import importlib.util
import os
import tempfile
import unittest
from pathlib import Path

# project-pack.py has a hyphen (matching the CLI invocation
# `python3 launchpad/agents/project-pack.py ...` the plan and README use), so
# it cannot be `import`ed as a normal module -- load it by file path instead.
_SPEC = importlib.util.spec_from_file_location(
    "project_pack", Path(__file__).resolve().parent / "project-pack.py"
)
m = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(m)


def persona(**overrides):
    base = {
        "name": "bot",
        "runtime": None,
        "runtime_env_vars": [
            ["GOOSE_PROVIDER", "anthropic"],
            ["GOOSE_MODEL", "claude-sonnet-5"],
            ["GOOSE_TEMPERATURE", "0.4"],
        ],
        "mcp_servers": [],
    }
    base.update(overrides)
    return base


class ProjectEnvVarsTests(unittest.TestCase):
    def test_passes_through_runtime_env_vars_verbatim(self):
        pairs = m.project_env_vars(persona(), Path("/pack"))
        as_dict = dict(pairs)
        self.assertEqual(as_dict["GOOSE_PROVIDER"], "anthropic")
        self.assertEqual(as_dict["GOOSE_MODEL"], "claude-sonnet-5")
        self.assertEqual(as_dict["GOOSE_TEMPERATURE"], "0.4")

    def test_agent_command_defaults_to_goose_when_runtime_unset(self):
        pairs = m.project_env_vars(persona(runtime=None), Path("/pack"))
        self.assertIn(("BUZZ_ACP_AGENT_COMMAND", "goose"), pairs)
        self.assertIn(("BUZZ_ACP_AGENT_ARGS", "acp"), pairs)

    def test_agent_command_follows_explicit_runtime(self):
        pairs = m.project_env_vars(persona(runtime="claude"), Path("/pack"))
        self.assertIn(("BUZZ_ACP_AGENT_COMMAND", "claude"), pairs)

    def test_no_mcp_server_emits_no_mcp_command(self):
        pairs = m.project_env_vars(persona(mcp_servers=[]), Path("/pack"))
        keys = [k for k, _ in pairs]
        self.assertNotIn("BUZZ_ACP_MCP_COMMAND", keys)

    def test_single_mcp_server_relative_command_resolved_against_pack_dir(self):
        p = persona(
            mcp_servers=[
                {"name": "professor-tools", "command": "tools/server.py", "args": [], "env": []}
            ]
        )
        pairs = m.project_env_vars(p, Path("/pack/dir"))
        as_dict = dict(pairs)
        self.assertEqual(as_dict["BUZZ_ACP_MCP_COMMAND"], "/pack/dir/tools/server.py")

    def test_single_mcp_server_absolute_command_left_untouched(self):
        p = persona(
            mcp_servers=[
                {"name": "t", "command": "/usr/bin/tools-server", "args": [], "env": []}
            ]
        )
        pairs = m.project_env_vars(p, Path("/pack/dir"))
        as_dict = dict(pairs)
        self.assertEqual(as_dict["BUZZ_ACP_MCP_COMMAND"], "/usr/bin/tools-server")

    # Distinctive server names, not "a"/"b" -- a single letter is a substring
    # of half the words in these messages, so asserting on it would pass
    # whether or not the name was ever interpolated.
    TWO_SERVERS = [
        {"name": "alpha-tools", "command": "alpha.py", "args": [], "env": []},
        {"name": "beta-tools", "command": "beta.py", "args": [], "env": []},
    ]
    SERVER_WITH_ARGS = [
        {"name": "alpha-tools", "command": "npx", "args": ["-y", "server"], "env": []}
    ]

    def test_two_mcp_servers_fails_loudly_rather_than_dropping_one(self):
        with self.assertRaises(m.ProjectionError) as caught:
            m.project_env_vars(
                persona(mcp_servers=self.TWO_SERVERS), Path("/pack/dir")
            )
        # A refusal an operator cannot act on is barely better than a silent
        # drop, so the message must name every server it declined to project.
        message = str(caught.exception)
        self.assertIn("alpha-tools", message)
        self.assertIn("beta-tools", message)

    def test_mcp_server_with_args_fails_loudly_rather_than_dropping_them(self):
        with self.assertRaises(m.ProjectionError) as caught:
            m.project_env_vars(
                persona(mcp_servers=self.SERVER_WITH_ARGS), Path("/pack/dir")
            )
        message = str(caught.exception)
        self.assertIn("alpha-tools", message)
        self.assertIn("bot", message)
        # The args are the whole reason for the refusal -- an operator who
        # cannot see which ones would be dropped cannot judge the trade-off.
        self.assertIn("-y", message)

    def test_refusal_messages_do_not_stack_repr_quoting_into_a_possessive(self):
        """`persona {name!r}'s server ...` renders as "'bot''s" -- repr()'s
        closing quote butted against the possessive apostrophe. Neither test
        above can see it, because both assert on names and args rather than on
        the punctuation between them."""
        for mcp_servers in (self.TWO_SERVERS, self.SERVER_WITH_ARGS):
            with self.subTest(servers=len(mcp_servers)):
                with self.assertRaises(m.ProjectionError) as caught:
                    m.project_env_vars(
                        persona(mcp_servers=mcp_servers), Path("/pack/dir")
                    )
                self.assertNotIn("''", str(caught.exception))


class FindBuzzBinaryTests(unittest.TestCase):
    # These rely on `buzz` genuinely not being on the real PATH in this
    # environment -- find_buzz_binary's `env` param only governs
    # BUZZ_CLI_BIN, since shutil.which() always reads the real process PATH.
    def test_buzz_cli_bin_override_used_when_it_exists(self):
        with tempfile.TemporaryDirectory() as d:
            override = Path(d) / "buzz"
            override.write_text("#!/bin/sh\n")
            found = m.find_buzz_binary(Path(d), {"BUZZ_CLI_BIN": str(override)})
            self.assertEqual(found, override)

    def test_buzz_cli_bin_override_missing_raises(self):
        with self.assertRaises(m.ProjectionError):
            m.find_buzz_binary(Path("/nonexistent"), {"BUZZ_CLI_BIN": "/no/such/buzz"})

    def test_prefers_more_recently_built_of_release_and_debug(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            release = root / "target" / "release" / "buzz"
            debug = root / "target" / "debug" / "buzz"
            release.parent.mkdir(parents=True)
            debug.parent.mkdir(parents=True)
            release.write_text("old")
            os.utime(release, (1000, 1000))
            debug.write_text("new")
            os.utime(debug, (2000, 2000))
            found = m.find_buzz_binary(root, {})
            self.assertEqual(found, debug)

    def test_no_candidate_anywhere_raises(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(m.ProjectionError):
                m.find_buzz_binary(Path(d), {})


class SelectPersonaTests(unittest.TestCase):
    def test_found_by_name(self):
        pack = {"personas": [persona(name="pip"), persona(name="lep")]}
        self.assertEqual(m.select_persona(pack, "lep")["name"], "lep")

    def test_not_found_lists_available_names(self):
        pack = {"personas": [persona(name="pip"), persona(name="lep")]}
        with self.assertRaises(m.ProjectionError) as ctx:
            m.select_persona(pack, "ghost")
        self.assertIn("pip", str(ctx.exception))
        self.assertIn("lep", str(ctx.exception))


class OperatorPrecedenceTests(unittest.TestCase):
    def test_var_not_in_environ_is_kept(self):
        kept, skipped = m.apply_operator_precedence(
            [("GOOSE_MODEL", "claude-sonnet-5")], {}
        )
        self.assertEqual(kept, [("GOOSE_MODEL", "claude-sonnet-5")])
        self.assertEqual(skipped, [])

    def test_var_already_in_environ_is_skipped_not_overwritten(self):
        kept, skipped = m.apply_operator_precedence(
            [("GOOSE_MODEL", "claude-sonnet-5")], {"GOOSE_MODEL": "operator-chosen-model"}
        )
        self.assertEqual(kept, [])
        self.assertEqual(
            skipped, [("GOOSE_MODEL", "claude-sonnet-5", "operator-chosen-model")]
        )

    def test_mixed_pairs_split_correctly(self):
        kept, skipped = m.apply_operator_precedence(
            [("A", "1"), ("B", "2")], {"B": "operator-b"}
        )
        self.assertEqual(kept, [("A", "1")])
        self.assertEqual(skipped, [("B", "2", "operator-b")])


class RenderEnvFileTests(unittest.TestCase):
    def test_kept_vars_rendered_as_export(self):
        out = m.render_env_file([("A", "1")], [])
        self.assertIn("export A=1", out)

    def test_skipped_vars_rendered_as_comment_not_export(self):
        out = m.render_env_file([], [("GOOSE_MODEL", "pack-value", "operator-value")])
        self.assertNotIn("export GOOSE_MODEL", out)
        self.assertIn("skipped GOOSE_MODEL", out)
        self.assertIn("operator-value", out)
        self.assertIn("pack-value", out)

    def test_values_needing_shell_quoting_are_quoted(self):
        out = m.render_env_file([("A", "has space")], [])
        self.assertIn("export A='has space'", out)


if __name__ == "__main__":
    unittest.main()
