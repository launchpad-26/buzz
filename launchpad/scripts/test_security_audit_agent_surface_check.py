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


def _assembled(*parts: str) -> str:
    """Join fragments at runtime rather than writing a credential-shaped
    string as one contiguous literal in this file's own source.

    This test file is itself scanned by #67's PR-diff gitleaks check (it is
    ordinary tracked source, not a fixture under the excluded
    `security_audit_fixtures/` path) -- a real `ghp_...`-shaped literal here
    was caught failing a real CI run before this helper existed (see the PR
    body). `+`-joining the fragments across two Python string literals keeps
    the raw source text non-contiguous (a closing quote, `+`, an opening
    quote sit between them) while still producing the intended value at
    runtime for `run()` to actually scan.
    """
    return "".join(parts)


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
            fake_key = _assembled(
                "22222222222222222222222222", "22222222222222222222222222", "222222222222"
            )
            (claude_dir / "settings.local.json").write_text(
                _assembled('{"env": {"BUZZ_PRIVATE_KEY": "', fake_key, '"}}\n'),
                encoding="utf-8",
            )
            result = run(root)
        self.assertEqual(result.status, Status.FAIL)
        self.assertIn("settings.local.json", result.detail)
        self.assertNotIn(fake_key, result.detail)

    def test_credential_in_mcp_json_anywhere_in_repo_fails(self):
        # AGENT_CONFIG_FILE_GLOBS matches by filename shape, not directory --
        # proves a .mcp.json outside any .{tool}/ directory is still in scope.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._prep(root)
            pack_dir = root / "launchpad" / "agents" / "example-pack"
            pack_dir.mkdir(parents=True)
            fake_token = _assembled("gh", "p_", "fx9Kj2mNpQr7VbXzYcWdEeFfGgHhIiJjKkLl00")
            (pack_dir / ".mcp.json").write_text(
                _assembled('{"mcpServers": {"x": {"env": {"TOKEN": "', fake_token, '"}}}}\n'),
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
