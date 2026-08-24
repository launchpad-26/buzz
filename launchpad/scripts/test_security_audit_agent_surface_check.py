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


def _skip_if_gitleaks_unavailable() -> bool:
    # Checks the config file AND the binary. Two of this repo's three CI
    # workflows (`scripts`, `adr-boundary`) run `unittest discover` over this
    # whole directory without installing gitleaks -- only the `audit`
    # workflow does. Before this fix, those two jobs found the config file
    # (present regardless), ran the real subprocess call, and got
    # Status.INDETERMINATE back where the assertions expected PASS/FAIL --
    # a confusing failure with nothing wrong in the check's own logic.
    # Skipping cleanly when the actual dependency this suite needs isn't
    # present is the same shape as the existing config-file check, just
    # covering the other missing piece.
    return not _REAL_GITLEAKS_TOML.is_file() or shutil.which("gitleaks") is None


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


@unittest.skipIf(_skip_if_gitleaks_unavailable(), "requires the real .gitleaks.toml and the gitleaks binary on PATH")
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

    def test_no_surface_files_at_all_is_indeterminate_not_pass(self):
        """Nothing to scan is not a clean scan.

        This test previously asserted PASS with "0 agent-surface file" in the
        detail, which codified the fail-open behaviour rather than catching it:
        a sparse checkout or a refactor that moved the agent-config directories
        produced a green control that had scanned zero bytes, indistinguishable
        in the summary from a real clean scan. `exit_code()` only fails on FAIL,
        so the audit passed. Inverted deliberately — if this ever asserts PASS
        again, the control has stopped asserting anything.
        """
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._prep(root)
            result = run(root)
        self.assertEqual(result.status, Status.INDETERMINATE)
        self.assertIn("asserts", result.detail)
        self.assertNotIn("no credential-shaped strings found", result.detail)


if __name__ == "__main__":
    unittest.main()
