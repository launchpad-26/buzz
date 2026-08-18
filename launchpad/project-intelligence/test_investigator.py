"""Controls for investigator.py -- issue #208.

Run:  python3 -m unittest test_investigator    (from launchpad/project-intelligence/)
  or: python3 test_investigator.py
"""

from __future__ import annotations

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


if __name__ == "__main__":
    unittest.main()
