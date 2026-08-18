"""Controls for investigator.py -- issue #208.

Run:  python3 -m unittest test_investigator    (from launchpad/project-intelligence/)
  or: python3 test_investigator.py
"""

from __future__ import annotations

import subprocess
import unittest

import investigator


class ToolRegistrySideEffectTest(unittest.TestCase):
    # Only three tools are registered as of STEP 1 (run_command/run_test are
    # STEP 7's job) -- assert the invariant that holds at every step: no tool
    # other than those two named ones is ever EXECUTE. The stronger claim
    # ("exactly these two ARE registered as EXECUTE") belongs to STEP 8's
    # test, once every tool actually exists.
    def test_no_tool_other_than_run_command_or_run_test_is_execute(self) -> None:
        for name, (_, effect) in investigator.TOOL_REGISTRY.items():
            if name in ("run_command", "run_test"):
                continue
            self.assertEqual(effect, "READ_ONLY", f"{name} should be READ_ONLY")


class ReadFileTest(unittest.TestCase):
    def test_reads_a_real_file_in_full(self) -> None:
        content = investigator.read_file("launchpad/project-intelligence/investigator.py")
        self.assertIn("TOOL_REGISTRY", content)

    def test_reads_a_line_range(self) -> None:
        content = investigator.read_file(
            "crates/buzz-core/src/kind.rs", start_line=219, end_line=221
        )
        self.assertEqual(
            content, "pub fn is_shared_gated_kind(kind: u32) -> bool {\n    SHARED_GATED_KINDS.contains(&kind)\n}"
        )


class ListDirectoryTest(unittest.TestCase):
    def test_lists_real_entries(self) -> None:
        entries = investigator.list_directory("launchpad/project-intelligence")
        self.assertIn("investigator.py", entries)
        self.assertIn("test_investigator.py", entries)


class SearchTextTest(unittest.TestCase):
    def test_finds_a_real_known_string(self) -> None:
        matches = investigator.search_text("TOOL_REGISTRY", glob="*.py")
        files = {m.file for m in matches}
        self.assertIn("launchpad/project-intelligence/investigator.py", files)

    def test_cross_checked_against_plain_grep(self) -> None:
        matches = investigator.search_text("is_shared_gated_kind", glob="*.rs")
        grep_result = subprocess.run(
            ["grep", "-rln", "--include", "*.rs", "is_shared_gated_kind", "."],
            capture_output=True,
            text=True,
            cwd=investigator.REPO_ROOT,
        )
        grep_files = {line.removeprefix("./") for line in grep_result.stdout.splitlines()}
        self.assertEqual({m.file for m in matches}, grep_files)


class InspectDependencyTest(unittest.TestCase):
    def test_resolves_a_real_workspace_inherited_dependency(self) -> None:
        dep = investigator.inspect_dependency("buzz-core", "nostr")
        self.assertIsNotNone(dep)
        self.assertEqual(dep.declared, {"workspace": True})
        # Cross-checked directly against Cargo.toml:70's real entry.
        self.assertEqual(dep.resolved["version"], "0.44")
        self.assertIn("nip44", dep.resolved["features"])

    def test_unknown_dependency_returns_none(self) -> None:
        self.assertIsNone(investigator.inspect_dependency("buzz-core", "no-such-crate-xyz"))


class QueryBuildSystemTest(unittest.TestCase):
    def test_resolves_real_crate_targets_with_no_build_artifacts(self) -> None:
        before = subprocess.run(
            ["find", "target", "-maxdepth", "2"], capture_output=True, text=True, cwd=investigator.REPO_ROOT
        ).stdout
        info = investigator.query_build_system("buzz-core")
        after = subprocess.run(
            ["find", "target", "-maxdepth", "2"], capture_output=True, text=True, cwd=investigator.REPO_ROOT
        ).stdout
        self.assertEqual(before, after, "query_build_system must not produce build artifacts")

        self.assertEqual(info.crate, "buzz-core")
        target_names = {t.name for t in info.targets}
        self.assertIn("buzz_core", target_names)


# search_symbols() shells out to the rql CLI, same as indexer.py's index_crate() --
# not given a test here, same reasoning as test_indexer.py's docstring: verified
# live against the real repo instead (see the commit message), so a RepoQL host
# lock conflict (hit twice already building #206/#207) can never block this
# committed, hermetic suite.


if __name__ == "__main__":
    unittest.main()
