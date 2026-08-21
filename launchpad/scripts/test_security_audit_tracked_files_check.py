#!/usr/bin/env python3
"""Controls for the #68 tracked-sensitive-files check.

Builds real git repositories in temp directories and commits real files —
the check shells out to `git ls-tree`, and a mock of subprocess.run would
just restate the fixture data rather than proving the check reads a real
tree correctly.
"""

from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from security_audit_core import Status
from security_audit_tracked_files_check import run


def _init_repo_with_files(root: Path, files: dict[str, str]) -> None:
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.name", "test"], cwd=root, check=True)
    for rel_path, content in files.items():
        full_path = root / rel_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content, encoding="utf-8")
    subprocess.run(["git", "add", "-A"], cwd=root, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "test fixture"], cwd=root, check=True)


class TrackedSensitiveFilesTest(unittest.TestCase):
    def test_clean_repo_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _init_repo_with_files(root, {"README.md": "hello\n", "src/main.py": "print(1)\n"})
            result = run(root)
        self.assertEqual(result.status, Status.PASS)

    def test_tracked_dotenv_file_fails(self):
        # Fixture: a real .env file, actually committed, proving the check
        # catches a file that predates whatever .gitignore says today.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _init_repo_with_files(root, {".env": "SOME_TOKEN=fake-value-for-test\n"})
            result = run(root)
        self.assertEqual(result.status, Status.FAIL)
        self.assertIn(".env", result.detail)

    def test_tracked_pem_file_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _init_repo_with_files(root, {"deploy/host.pem": "-----BEGIN FAKE-----\n"})
            result = run(root)
        self.assertEqual(result.status, Status.FAIL)
        self.assertIn("host.pem", result.detail)

    def test_tracked_id_rsa_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _init_repo_with_files(root, {"ops/id_rsa": "fake key material\n"})
            result = run(root)
        self.assertEqual(result.status, Status.FAIL)

    def test_env_example_is_exempt(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _init_repo_with_files(root, {".env.example": "SOME_TOKEN=CHANGE_ME\n"})
            result = run(root)
        self.assertEqual(result.status, Status.PASS)

    def test_seed_directory_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _init_repo_with_files(root, {"deploy/seed/cloud-init.yaml": "ssh_authorized_keys: []\n"})
            result = run(root)
        self.assertEqual(result.status, Status.FAIL)

    def test_git_failure_is_indeterminate(self):
        with tempfile.TemporaryDirectory() as tmp:
            # Not a git repo at all -- `git ls-tree` must fail cleanly.
            result = run(Path(tmp))
        self.assertEqual(result.status, Status.INDETERMINATE)


class NewlyHiddenTrackedFileTest(unittest.TestCase):
    """PR-mode only: a real two-commit history against a real 'origin' remote
    (a second bare repo, not a mock) -- proves the diff-against-base-ref path
    actually reads real git history, not a mocked stand-in for it.
    """

    def test_new_ignore_pattern_covering_a_tracked_file_warns(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "work"
            bare = Path(tmp) / "origin.git"
            root.mkdir()
            subprocess.run(["git", "init", "-q", "--bare", str(bare)], check=True)

            # Base commit: a real tracked file, an empty .gitignore. Neither
            # is sensitive on its own -- the WARN is about the *combination*
            # introduced in the next commit.
            _init_repo_with_files(root, {"deploy/legacy-notes.txt": "notes\n", ".gitignore": "\n"})
            subprocess.run(["git", "remote", "add", "origin", str(bare)], cwd=root, check=True)
            subprocess.run(["git", "branch", "-M", "launchpad"], cwd=root, check=True)
            subprocess.run(["git", "push", "-q", "origin", "launchpad"], cwd=root, check=True)

            # PR commit: adds an ignore pattern that newly covers the
            # already-tracked file above. The file is not removed -- exactly
            # the accidental-cover-up shape this half of the check exists for.
            (root / ".gitignore").write_text("deploy/legacy-notes.txt\n", encoding="utf-8")
            subprocess.run(["git", "add", "-A"], cwd=root, check=True)
            subprocess.run(["git", "commit", "-q", "-m", "add ignore pattern"], cwd=root, check=True)

            with mock.patch.dict("os.environ", {"GITHUB_BASE_REF": "launchpad"}):
                result = run(root)

        self.assertEqual(result.status, Status.WARN)
        self.assertIn("legacy-notes.txt", result.detail)

    def test_not_in_pr_mode_is_unaffected(self):
        # No GITHUB_BASE_REF at all -- the newly-hidden check must be a no-op,
        # not an error, outside PR mode. Only that one variable is removed
        # (not the whole environment) so `git` itself still resolves via PATH.
        import os

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _init_repo_with_files(root, {"README.md": "hello\n"})
            env = dict(os.environ)
            env.pop("GITHUB_BASE_REF", None)
            with mock.patch.dict("os.environ", env, clear=True):
                result = run(root)
        self.assertEqual(result.status, Status.PASS)


if __name__ == "__main__":
    unittest.main()
