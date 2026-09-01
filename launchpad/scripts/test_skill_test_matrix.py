#!/usr/bin/env python3
"""Controls for skill_test_matrix.py.

Each control is written so it FAILS if the guard it covers stops guarding.
The synthetic cases build their own trees under a temp directory, so nothing
here depends on the current contents of launchpad/skills -- except the two
controls at the end, which deliberately assert against the real tree, because
"the manifest matches reality" is the property this tooling exists to hold.
"""

from __future__ import annotations

import json
import pathlib
import tempfile
import unittest

import skill_test_matrix as m


def make_tree(root, skills_with_tests=(), skills_without_tests=()):
    skills = pathlib.Path(root) / "launchpad" / "skills"
    for name in skills_with_tests:
        (skills / name / "tests").mkdir(parents=True)
    for name in skills_without_tests:
        (skills / name).mkdir(parents=True)
    return skills


class DiscoverSkillsTests(unittest.TestCase):
    def test_finds_only_directories_holding_tests(self):
        with tempfile.TemporaryDirectory() as tmp:
            skills = make_tree(tmp, ["alpha", "beta"], ["gamma"])
            self.assertEqual(m.discover_skills(skills), ["alpha", "beta"])

    def test_missing_skills_directory_is_empty_not_an_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            absent = pathlib.Path(tmp) / "nope"
            self.assertEqual(m.discover_skills(absent), [])

    def test_a_file_named_like_a_skill_is_not_a_skill(self):
        with tempfile.TemporaryDirectory() as tmp:
            skills = make_tree(tmp, ["alpha"])
            (skills / "readme.md").write_text("x", encoding="utf-8")
            self.assertEqual(m.discover_skills(skills), ["alpha"])


class CoverageProblemTests(unittest.TestCase):
    """The guard that closes #2018: an undeclared skill must be reported."""

    def test_consistent_manifest_reports_nothing(self):
        problems = m.coverage_problems(["alpha"], {"alpha": 3}, {})
        self.assertEqual(problems, [])

    def test_undeclared_skill_is_reported(self):
        problems = m.coverage_problems(["alpha", "beta"], {"alpha": 3}, {})
        self.assertEqual(len(problems), 1)
        self.assertIn("beta", problems[0])
        self.assertIn("neither", problems[0])

    def test_skill_declared_in_both_maps_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            workflow = root / "wf.yml"
            workflow.write_text("launchpad/skills/alpha", encoding="utf-8")
            problems = m.coverage_problems(
                ["alpha"], {"alpha": 3}, {"alpha": "wf.yml"}, repo_root=root
            )
        self.assertTrue(any("exactly one" in p for p in problems))

    def test_declared_skill_with_no_suite_on_disk_is_reported(self):
        problems = m.coverage_problems([], {"alpha": 3}, {})
        self.assertEqual(len(problems), 1)
        self.assertIn("no launchpad/skills/alpha/tests", problems[0])

    def test_zero_floor_is_rejected(self):
        problems = m.coverage_problems(["alpha"], {"alpha": 0}, {})
        self.assertTrue(any("positive integer" in p for p in problems))

    def test_non_integer_floor_is_rejected(self):
        problems = m.coverage_problems(["alpha"], {"alpha": "many"}, {})
        self.assertTrue(any("positive integer" in p for p in problems))

    def test_exclusion_naming_a_missing_workflow_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            problems = m.coverage_problems(
                ["alpha"], {}, {"alpha": "gone.yml"}, repo_root=pathlib.Path(tmp)
            )
        self.assertEqual(len(problems), 1)
        self.assertIn("does not exist", problems[0])

    def test_exclusion_whose_workflow_ignores_the_skill_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            (root / "wf.yml").write_text(
                "paths:\n  - launchpad/skills/something-else/**\n", encoding="utf-8"
            )
            problems = m.coverage_problems(
                ["alpha"], {}, {"alpha": "wf.yml"}, repo_root=root
            )
        self.assertEqual(len(problems), 1)
        self.assertIn("never mentions", problems[0])

    def test_truthful_exclusion_reports_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            (root / "wf.yml").write_text(
                "paths:\n  - launchpad/skills/alpha/**\n", encoding="utf-8"
            )
            problems = m.coverage_problems(
                ["alpha"], {}, {"alpha": "wf.yml"}, repo_root=root
            )
        self.assertEqual(problems, [])


class ParseCollectedTests(unittest.TestCase):
    """Counts CASES. A guard satisfiable by a filename is not a guard."""

    def test_reads_the_case_count(self):
        self.assertEqual(m.parse_collected("25 tests collected in 0.03s"), 25)

    def test_reads_the_singular_form(self):
        self.assertEqual(m.parse_collected("1 test collected in 0.01s"), 1)

    def test_zero_collected_is_zero_not_none(self):
        self.assertEqual(m.parse_collected("0 tests collected in 0.01s"), 0)

    def test_last_summary_wins(self):
        output = "3 tests collected in 0.01s\n9 tests collected in 0.02s\n"
        self.assertEqual(m.parse_collected(output), 9)

    def test_no_summary_is_none(self):
        self.assertIsNone(m.parse_collected("something else entirely"))

    def test_pytests_empty_suite_phrasing_is_zero_not_none(self):
        """The output produced by renaming every test_* to check_*.

        Reported as an empty suite rather than as an unreadable summary, so the
        error names the real cause. Verified against pytest 8.3.4's actual
        stdout, not assumed.
        """
        self.assertEqual(m.parse_collected("no tests collected in 0.03s"), 0)

    def test_collection_errors_are_not_a_count(self):
        output = "4 tests collected, 1 error in 0.05s"
        self.assertIsNone(m.parse_collected(output))


class AssertFloorTests(unittest.TestCase):
    def setUp(self):
        self.manifest = {"alpha": 5}

    def _run(self, skill, stdin_text):
        """Drive the real CLI path with a stubbed manifest and stdin.

        stdout is captured rather than left to escape: these controls
        deliberately exercise the failure paths, and their ::error:: lines would
        otherwise be indistinguishable in a CI log from a real failure.
        """
        import contextlib
        import io
        import sys

        real_stdin = sys.stdin
        real_load = m.load_manifest
        m.load_manifest = lambda *a, **k: (self.manifest, {})
        sys.stdin = io.StringIO(stdin_text)
        try:
            with contextlib.redirect_stdout(io.StringIO()) as captured:
                code = m.main(["assert-floor", "--skill", skill])
            self.captured = captured.getvalue()
            return code
        finally:
            sys.stdin = real_stdin
            m.load_manifest = real_load

    def test_meeting_the_floor_passes(self):
        self.assertEqual(self._run("alpha", "5 tests collected in 0.1s"), 0)

    def test_exceeding_the_floor_passes(self):
        self.assertEqual(self._run("alpha", "40 tests collected in 0.1s"), 0)

    def test_falling_below_the_floor_fails(self):
        self.assertEqual(self._run("alpha", "4 tests collected in 0.1s"), 1)

    def test_empty_suite_fails_rather_than_passing_silently(self):
        self.assertEqual(self._run("alpha", "0 tests collected in 0.1s"), 1)
        self.assertIn("collected 0 test case(s)", self.captured)

    def test_renaming_every_test_away_is_reported_as_an_empty_suite(self):
        """pytest's real output for that mutation, not a paraphrase of it."""
        self.assertEqual(self._run("alpha", "no tests collected in 0.03s"), 1)
        self.assertIn("collected 0 test case(s)", self.captured)
        self.assertNotIn("no usable collection summary", self.captured)

    def test_unparseable_output_fails_rather_than_passing(self):
        self.assertEqual(self._run("alpha", "pytest exploded"), 1)

    def test_unknown_skill_fails(self):
        self.assertEqual(self._run("omega", "9 tests collected in 0.1s"), 1)


class RealTreeTests(unittest.TestCase):
    """These assert against the repository as it actually is, on purpose."""

    def test_committed_manifest_matches_the_committed_skills(self):
        run_here, covered_elsewhere = m.load_manifest()
        problems = m.coverage_problems(
            m.discover_skills(), run_here, covered_elsewhere
        )
        self.assertEqual(problems, [], "\n".join(problems))

    def test_manifest_is_valid_json_with_both_maps(self):
        data = json.loads(m.MANIFEST.read_text(encoding="utf-8"))
        self.assertIn("run_here", data)
        self.assertIn("covered_elsewhere", data)

    def test_matrix_covers_every_run_here_entry(self):
        run_here, _ = m.load_manifest()
        entries = [
            {"skill": s, "floor": f} for s, f in sorted(run_here.items())
        ]
        self.assertEqual(len(entries), len(run_here))
        self.assertTrue(all(e["floor"] >= 1 for e in entries))


if __name__ == "__main__":
    unittest.main()
