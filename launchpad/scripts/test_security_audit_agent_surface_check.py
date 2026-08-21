#!/usr/bin/env python3
"""Controls for the #68 agent-surface secret-scan check.

Builds a real temp directory with a real .gitleaks.toml (copied from the
actual repo config, not reinvented) and real files under real
AGENT_SURFACE_DIRS/AGENT_CONFIG_FILE_GLOBS shapes, then runs the real
gitleaks binary against it -- same discipline as #67's own controls: this
suite proves the check's branching, not gitleaks' matching (that is proven
directly against fixtures in the PR body / commit history).
"""

from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path

from security_audit_core import Status
from security_audit_agent_surface_check import run

_REAL_GITLEAKS_TOML = Path(__file__).resolve().parents[2] / ".gitleaks.toml"


def _skip_if_no_gitleaks_config() -> bool:
    return not _REAL_GITLEAKS_TOML.is_file()


@unittest.skipIf(_skip_if_no_gitleaks_config(), "requires the real .gitleaks.toml from the repo root")
class AgentSurfaceSecretScanTest(unittest.TestCase):
    def _prep(self, root: Path) -> None:
        shutil.copy(_REAL_GITLEAKS_TOML, root / ".gitleaks.toml")

    def test_clean_agent_surface_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._prep(root)
            claude_dir = root / ".claude" / "skills" / "example"
            claude_dir.mkdir(parents=True)
            (claude_dir / "SKILL.md").write_text("# Example skill\nNo secrets here.\n", encoding="utf-8")
            result = run(root)
        self.assertEqual(result.status, Status.PASS)

    def test_credential_in_dot_claude_fails(self):
        # Fixture: a real (synthetic) BUZZ_PRIVATE_KEY value dropped into a
        # .claude/ config file -- exactly the "local testing leftover"
        # scenario this check exists for.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._prep(root)
            claude_dir = root / ".claude"
            claude_dir.mkdir()
            (claude_dir / "settings.local.json").write_text(
                '{"env": {"BUZZ_PRIVATE_KEY": '
                '"2222222222222222222222222222222222222222222222222222222222222222"}}\n',
                encoding="utf-8",
            )
            result = run(root)
        self.assertEqual(result.status, Status.FAIL)
        self.assertIn("settings.local.json", result.detail)
        self.assertNotIn("2222222222222222222222222222222222222222222222222222222222222222", result.detail)

    def test_credential_in_mcp_json_anywhere_in_repo_fails(self):
        # AGENT_CONFIG_FILE_GLOBS matches by filename shape, not directory --
        # proves a .mcp.json outside any .{tool}/ directory is still in scope.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._prep(root)
            pack_dir = root / "launchpad" / "agents" / "example-pack"
            pack_dir.mkdir(parents=True)
            (pack_dir / ".mcp.json").write_text(
                '{"mcpServers": {"x": {"env": {"TOKEN": '
                '"ghp_fx9Kj2mNpQr7VbXzYcWdEeFfGgHhIiJjKkLl00"}}}}\n',
                encoding="utf-8",
            )
            result = run(root)
        self.assertEqual(result.status, Status.FAIL)
        self.assertIn(".mcp.json", result.detail)

    def test_missing_gitleaks_config_is_indeterminate(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)  # no .gitleaks.toml written
            (root / ".claude").mkdir()
            result = run(root)
        self.assertEqual(result.status, Status.INDETERMINATE)

    def test_no_surface_files_at_all_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._prep(root)
            result = run(root)
        self.assertEqual(result.status, Status.PASS)
        self.assertIn("0 agent-surface file", result.detail)


if __name__ == "__main__":
    unittest.main()
