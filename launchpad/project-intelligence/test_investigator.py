"""Controls for investigator.py -- issue #208.

Run:  python3 -m unittest test_investigator    (from launchpad/project-intelligence/)
  or: python3 test_investigator.py
"""

from __future__ import annotations

import subprocess
import time
import unittest

import investigator


class ToolRegistrySideEffectTest(unittest.TestCase):
    # STEP 8: every one of the twelve tools now exists, so the strong claim
    # can finally be made -- exactly {run_command, run_test} are EXECUTE, and
    # nothing else. Superseded weaker version (kept true throughout STEP 1-7:
    # "no tool other than those two is ever EXECUTE") is now implied by this.
    def test_exactly_run_command_and_run_test_are_execute(self) -> None:
        execute_tools = {name for name, (_, effect) in investigator.TOOL_REGISTRY.items() if effect == "EXECUTE"}
        self.assertEqual(execute_tools, {"run_command", "run_test"})

    def test_all_twelve_tools_from_the_design_doc_are_registered(self) -> None:
        self.assertEqual(
            set(investigator.TOOL_REGISTRY.keys()),
            {
                "read_file",
                "list_directory",
                "inspect_logs",
                "search_text",
                "search_symbols",
                "find_references",
                "inspect_git_history",
                "git_blame",
                "inspect_dependency",
                "query_build_system",
                "run_command",
                "run_test",
            },
        )


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


class PathContainmentTest(unittest.TestCase):
    # Codex review finding (P1): `REPO_ROOT / path` alone does not stop an
    # absolute or ".."-laden path from escaping the repo -- pathlib's `/`
    # discards REPO_ROOT entirely when `path` is itself absolute.
    def test_read_file_rejects_an_absolute_path_outside_the_repo(self) -> None:
        with self.assertRaises(ValueError):
            investigator.read_file("/etc/hostname")

    def test_read_file_rejects_dotdot_traversal_outside_the_repo(self) -> None:
        with self.assertRaises(ValueError):
            investigator.read_file("../../../../../../../etc/hostname")

    def test_list_directory_rejects_an_absolute_path_outside_the_repo(self) -> None:
        with self.assertRaises(ValueError):
            investigator.list_directory("/etc")

    def test_inspect_logs_rejects_an_absolute_path_outside_the_repo(self) -> None:
        with self.assertRaises(ValueError):
            investigator.inspect_logs("/etc/hostname")

    def test_a_path_that_stays_inside_the_repo_still_works(self) -> None:
        # The containment check must not be so strict it breaks ordinary use.
        content = investigator.read_file("launchpad/project-intelligence/../project-intelligence/investigator.py")
        self.assertIn("TOOL_REGISTRY", content)

    def test_inspect_dependency_rejects_a_crate_that_escapes_the_repo(self) -> None:
        # review-code finding (PR #217, must-fix #3): this built its manifest
        # path directly from REPO_ROOT / "crates" / crate / ..., bypassing
        # _resolve_within_repo entirely -- the exact P1 class the second
        # commit on this PR fixed everywhere else.
        with self.assertRaises(ValueError):
            investigator.inspect_dependency("../../../../../../../etc", "passwd")

    def test_query_build_system_rejects_a_crate_that_escapes_the_repo(self) -> None:
        with self.assertRaises(ValueError):
            investigator.query_build_system("../../../../../../../etc")


class SearchTextTest(unittest.TestCase):
    def test_finds_a_real_known_string(self) -> None:
        matches = investigator.search_text("TOOL_REGISTRY", glob="*.py")
        files = {m.file for m in matches}
        self.assertIn("launchpad/project-intelligence/investigator.py", files)

    def test_pattern_starting_with_a_dash_is_treated_as_search_text_not_a_flag(self) -> None:
        # Codex review finding (P2): without a "--" terminator, grep reads a
        # leading "-" as another option instead of the search pattern.
        matches = investigator.search_text("--include", glob="*.py")
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

    def test_default_glob_does_not_crash_walking_git_and_target(self) -> None:
        # review-code finding (PR #217, must-fix #1): the default glob="*"
        # walked .git/ (and target/, if present) and crashed on the first
        # binary match -- "Binary file X matches" has no ":" separators, so
        # `line.split(":", 2)` raised ValueError. Reproduces the real
        # trigger: no glob narrowing at all, from the repo root, which
        # .git/ guarantees contains binary pack data.
        matches = investigator.search_text("TOOL_REGISTRY")
        files = {m.file for m in matches}
        self.assertIn("launchpad/project-intelligence/investigator.py", files)
        self.assertTrue(all(not f.startswith(".git/") and not f.startswith("target/") for f in files))

    def test_no_matches_returns_empty_not_an_error(self) -> None:
        # grep exits 1 (not 0) when nothing matches -- a normal result, not
        # the "real grep failure" case returncode-checking now guards
        # against, and must not raise. Built by concatenation so this test's
        # own source line is not itself a match for the pattern it searches.
        needle = "no_such_string_exists" + "_anywhere_zzy987"
        self.assertEqual(investigator.search_text(needle), [])


class InjectionRejectionTest(unittest.TestCase):
    # review-code finding (PR #217, must-fix #2): search_symbols/
    # find_references f-string caller input into an rql SQL WHERE clause,
    # and inspect_git_history/git_blame f-string it into an rql URI.
    # Validation runs before any subprocess call, so these are hermetic --
    # no live `rql` binary needed to prove the rejection happens.
    def test_search_symbols_rejects_a_name_with_a_sql_quote(self) -> None:
        with self.assertRaises(ValueError):
            investigator.search_symbols("x' OR '1'='1")

    def test_search_symbols_rejects_a_crate_with_a_sql_quote(self) -> None:
        with self.assertRaises(ValueError):
            investigator.search_symbols("is_shared_gated_kind", crate="buzz-core' --")

    def test_find_references_rejects_a_qualified_name_with_a_sql_quote(self) -> None:
        with self.assertRaises(ValueError):
            investigator.find_references("x' OR '1'='1", crate="buzz-core")

    def test_find_references_rejects_a_crate_with_a_sql_quote(self) -> None:
        with self.assertRaises(ValueError):
            investigator.find_references("is_shared_gated_kind", crate="buzz-core' --")

    def test_inspect_git_history_rejects_a_file_with_a_uri_modifier_injection(self) -> None:
        with self.assertRaises(ValueError):
            investigator.inspect_git_history("f.rs#symbol=x => write:evil", 1, 2)

    def test_git_blame_rejects_a_file_with_a_uri_fragment_injection(self) -> None:
        with self.assertRaises(ValueError):
            investigator.git_blame("f.rs#line=1,2 => blame; DROP", 1, 2)

    def test_inspect_git_history_accepts_an_ordinary_repo_relative_path(self) -> None:
        # The validation must not be so strict it rejects real, ordinary
        # paths -- confirmed by construction (no exception), not by calling
        # through to a live rql (see the module docstring's reasoning).
        investigator._validate_repo_relative_path("crates/buzz-core/src/kind.rs", "file")


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

    def test_merges_crate_local_feature_additions_into_the_workspace_entry(self) -> None:
        # Codex review finding (P2): crates/buzz-agent/Cargo.toml adds
        # features (e.g. "io-std") to tokio's workspace-inherited entry --
        # replacing wholesale with the root entry silently drops them.
        dep = investigator.inspect_dependency("buzz-agent", "tokio")
        self.assertIsNotNone(dep)
        self.assertIn("features", dep.declared)  # the crate-local addition is present in `declared`
        self.assertIn("io-std", dep.declared["features"])
        # The merged `resolved` view must carry both the crate-local addition
        # AND the workspace's own base features -- neither side silently
        # lost. Cross-checked directly against Cargo.toml:45's real entry
        # (rt-multi-thread, macros, net, time, sync, io-util, signal, process).
        self.assertIn("io-std", dep.resolved["features"])
        for base_feature in ("rt-multi-thread", "macros", "net", "time", "sync", "io-util", "signal", "process"):
            self.assertIn(base_feature, dep.resolved["features"])


class RunCommandAndRunTestTest(unittest.TestCase):
    def test_run_command_surfaces_execute_flag_before_output(self) -> None:
        with self.subTest("printed"):
            proc = subprocess.run(
                [
                    "python3",
                    "-c",
                    "import investigator; r = investigator.run_command(['echo', 'hi']); print('AFTER:', r.stdout.strip())",
                ],
                capture_output=True,
                text=True,
                cwd=investigator.REPO_ROOT / "launchpad" / "project-intelligence",
            )
            lines = proc.stdout.splitlines()
            self.assertTrue(lines[0].startswith("[EXECUTE] run_command:"))
            self.assertEqual(lines[1], "AFTER: hi")

        with self.subTest("on the returned result"):
            result = investigator.run_command(["echo", "hi"])
            self.assertEqual(result.side_effect, "EXECUTE")
            self.assertEqual(result.returncode, 0)
            self.assertEqual(result.stdout.strip(), "hi")

    def test_run_test_surfaces_execute_flag_and_runs_a_real_fast_test(self) -> None:
        result = investigator.run_test("buzz-core", "kind::tests::")
        self.assertEqual(result.side_effect, "EXECUTE")
        self.assertIn("test result:", result.stdout)

    def test_execute_notice_is_visible_before_the_subprocess_finishes_not_only_after(self) -> None:
        # Codex review finding (P1): the earlier test only checked final
        # ordering in fully-captured stdout, which print's block-buffering
        # (the normal mode whenever stdout is piped, as an agent harness
        # would) can still satisfy by coincidence even if the line only
        # becomes visible after the subprocess has already completed. This
        # proves the notice is actually flushed and readable *during* a
        # command that is still running, using a wall-clock margin.
        proc = subprocess.Popen(
            ["python3", "-c", "import investigator; investigator.run_command(['sleep', '2'])"],
            cwd=investigator.REPO_ROOT / "launchpad" / "project-intelligence",
            stdout=subprocess.PIPE,
            text=True,
        )
        started = time.monotonic()
        try:
            line = proc.stdout.readline()
            elapsed = time.monotonic() - started
        finally:
            proc.wait(timeout=10)
            proc.stdout.close()
        self.assertTrue(line.startswith("[EXECUTE] run_command:"), line)
        self.assertLess(elapsed, 1.0, "EXECUTE notice should be flushed well before the 2s sleep finishes")


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
