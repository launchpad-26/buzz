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


def _oid(root: Path, rel_path: str) -> str:
    """The committed blob OID of `rel_path`, for building a fake upstream tree."""
    result = subprocess.run(
        ["git", "rev-parse", f"HEAD:{rel_path}"],
        cwd=root, check=True, capture_output=True, text=True,
    )
    return result.stdout.strip()


class _NoUpstreamMixin:
    """Keep these tests off the network.

    `run()` now asks `security_audit_classifier.fetch_upstream_blobs` who owns a
    sensitive-shaped hit, and that shells out to `git fetch` against block/buzz.
    Unpatched, every case below would clone a real remote to decide something
    the fixture already knows. An empty upstream tree is the honest stand-in for
    "this fixture repo inherited nothing", which is what makes every
    pre-existing expectation here still the right one.
    """

    def setUp(self):
        patcher = mock.patch(
            "security_audit_tracked_files_check.fetch_upstream_blobs",
            return_value={},
        )
        self.fetch_upstream = patcher.start()
        self.addCleanup(patcher.stop)


class TrackedSensitiveFilesTest(_NoUpstreamMixin, unittest.TestCase):
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

    def test_env_example_never_matched_the_env_pattern_in_the_first_place(self):
        # .env.example doesn't end in exactly ".env", so it was never going
        # to match the (^|/)\.env$ pattern -- no exemption needed or wanted.
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

    def test_example_suffixed_file_inside_seed_directory_still_fails(self):
        # Regression for a real gap review-code found on #275: a now-removed
        # *.example suffix exemption short-circuited _matches_sensitive_shape
        # before the seed/ directory-component pattern ever got a chance to
        # match, so a tracked seed/authorized_keys.example reported PASS --
        # exactly the shape #68 documents a real past incident for (a
        # committed SSH public key), just renamed with a trailing .example.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _init_repo_with_files(
                root, {"deploy/archived/seed/authorized_keys.example": "ssh-ed25519 AAAA...\n"}
            )
            result = run(root)
        self.assertEqual(result.status, Status.FAIL)
        self.assertIn("authorized_keys.example", result.detail)

    def test_git_failure_is_indeterminate(self):
        with tempfile.TemporaryDirectory() as tmp:
            # Not a git repo at all -- `git ls-tree` must fail cleanly.
            result = run(Path(tmp))
        self.assertEqual(result.status, Status.INDETERMINATE)


class UpstreamOwnershipTest(unittest.TestCase):
    """Ownership scoping for #1965.

    Upstream ships genuinely private-key-shaped APNs test fixtures. This fork
    operates the upstream product rather than developing it, cannot fix those
    files, and was reporting FAIL on every branch for all six — so `audit` was
    red on trunk and unreadable on every pull request. Scoping by ownership must
    silence exactly that case and nothing else.
    """

    def test_upstream_identical_fixture_does_not_fail_and_is_named(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _init_repo_with_files(
                root, {"crates/gw/tests/fixtures/apns-test-identity.pem": "-----BEGIN PRIVATE KEY-----\n"}
            )
            upstream = {"crates/gw/tests/fixtures/apns-test-identity.pem":
                        _oid(root, "crates/gw/tests/fixtures/apns-test-identity.pem")}
            with mock.patch(
                "security_audit_tracked_files_check.fetch_upstream_blobs",
                return_value=upstream,
            ):
                result = run(root)
        self.assertEqual(result.status, Status.PASS)
        # Named, not silently dropped: a skip nobody can see is a check that stopped looking.
        self.assertIn("apns-test-identity.pem", result.detail)
        self.assertIn("upstream", result.detail)

    def test_a_cohort_added_key_still_fails_alongside_upstream_fixtures(self):
        """The acceptance criterion: narrowing must not blind the check.

        An upstream-identical fixture and a cohort-added key in the same tree —
        the second one must still fail the run.
        """
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _init_repo_with_files(root, {
                "crates/gw/tests/fixtures/apns-test-identity.pem": "-----BEGIN PRIVATE KEY-----\n",
                "launchpad/deploy/relay.pem": "-----BEGIN PRIVATE KEY-----\n",
            })
            upstream = {"crates/gw/tests/fixtures/apns-test-identity.pem":
                        _oid(root, "crates/gw/tests/fixtures/apns-test-identity.pem")}
            with mock.patch(
                "security_audit_tracked_files_check.fetch_upstream_blobs",
                return_value=upstream,
            ):
                result = run(root)
        self.assertEqual(result.status, Status.FAIL)
        self.assertIn("relay.pem", result.detail)
        # The upstream fixture must not be counted against the cohort.
        self.assertNotIn("apns-test-identity.pem", result.detail)

    def test_an_inherited_path_modified_here_still_fails(self):
        """Identity, not origin.

        An inherited filename is exactly where cohort-added key material could
        hide, so presence upstream is not enough — the bytes must match.
        """
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _init_repo_with_files(
                root, {"crates/gw/tests/fixtures/apns-test-identity.pem": "-----BEGIN PRIVATE KEY-----\nours\n"}
            )
            upstream = {"crates/gw/tests/fixtures/apns-test-identity.pem": "0" * 40}
            with mock.patch(
                "security_audit_tracked_files_check.fetch_upstream_blobs",
                return_value=upstream,
            ):
                result = run(root)
        self.assertEqual(result.status, Status.FAIL)
        self.assertIn("apns-test-identity.pem", result.detail)

    def test_unreachable_upstream_is_indeterminate_not_pass(self):
        """Ownership unknown is neither clean nor damning, and must not read as clean."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _init_repo_with_files(root, {"deploy/host.pem": "-----BEGIN PRIVATE KEY-----\n"})
            with mock.patch(
                "security_audit_tracked_files_check.fetch_upstream_blobs",
                return_value=None,
            ):
                result = run(root)
        self.assertEqual(result.status, Status.INDETERMINATE)
        self.assertIn("host.pem", result.detail)


class NewlyHiddenTrackedFileTest(_NoUpstreamMixin, unittest.TestCase):
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
