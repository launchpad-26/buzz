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


def write_workflow(root, name, paths, runner="pytest tests"):
    """A minimal but believable workflow: triggered on `paths`, runs a suite."""
    root = pathlib.Path(root)
    directory = root / ".github" / "workflows"
    directory.mkdir(parents=True, exist_ok=True)
    entries = "".join(f"      - '{p}'\n" for p in paths)
    (directory / name).write_text(
        f"on:\n  pull_request:\n    paths:\n{entries}"
        f"jobs:\n  tests:\n    steps:\n      - run: {runner}\n",
        encoding="utf-8",
    )
    return root


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

    def test_empty_run_here_is_rejected(self):
        """A manifest that runs nothing must not report itself consistent.

        Without this the matrix builds with no legs, no suite executes, and the
        pipeline is green -- the same silent-zero shape the floors exist to catch,
        one level up.
        """
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            (root / "wf.yml").write_text("launchpad/skills/alpha", encoding="utf-8")
            problems = m.coverage_problems(
                ["alpha"], {}, {"alpha": "wf.yml"}, repo_root=root
            )
        self.assertTrue(any("run no suite at all" in p for p in problems))

    def test_zero_floor_is_rejected(self):
        problems = m.coverage_problems(["alpha"], {"alpha": 0}, {})
        self.assertTrue(any("positive integer" in p for p in problems))

    def test_non_integer_floor_is_rejected(self):
        problems = m.coverage_problems(["alpha"], {"alpha": "many"}, {})
        self.assertTrue(any("positive integer" in p for p in problems))

    def test_negative_floor_is_rejected(self):
        problems = m.coverage_problems(["alpha"], {"alpha": -1}, {})
        self.assertTrue(any("positive integer" in p for p in problems))

    def test_boolean_floor_is_rejected(self):
        """JSON `true` is an int in Python and would pass as floor 1."""
        problems = m.coverage_problems(["alpha"], {"alpha": True}, {})
        self.assertTrue(any("positive integer" in p for p in problems))

    def test_floor_of_one_is_accepted(self):
        """The boundary itself: 1 passes, 0 does not."""
        self.assertEqual(m.coverage_problems(["alpha"], {"alpha": 1}, {}), [])

    # These isolate the exclusion rules, so they keep one real entry in
    # 'run_here'. An empty one is its own finding (see
    # test_empty_run_here_is_rejected) and would otherwise mask what they assert.
    def test_exclusion_naming_a_missing_workflow_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            problems = m.coverage_problems(
                ["alpha", "kept"],
                {"kept": 1},
                {"alpha": ".github/workflows/gone.yml"},
                repo_root=pathlib.Path(tmp),
            )
        self.assertEqual(len(problems), 1)
        self.assertIn("does not exist", problems[0])

    def test_exclusion_whose_workflow_ignores_the_skill_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = write_workflow(
                tmp, "wf.yml", paths=["launchpad/skills/something-else/**"]
            )
            problems = m.coverage_problems(
                ["alpha", "kept"],
                {"kept": 1},
                {"alpha": ".github/workflows/wf.yml"},
                repo_root=root,
            )
        self.assertEqual(len(problems), 1)
        self.assertIn("no trigger path", problems[0])

    def test_truthful_exclusion_reports_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = write_workflow(tmp, "wf.yml", paths=["launchpad/skills/alpha/**"])
            problems = m.coverage_problems(
                ["alpha", "kept"],
                {"kept": 1},
                {"alpha": ".github/workflows/wf.yml"},
                repo_root=root,
            )
        self.assertEqual(problems, [])


class ExclusionStrictnessTests(unittest.TestCase):
    """A `covered_elsewhere` claim must be believable, not merely stringy.

    The first version searched the named file's whole text for the skill path,
    which a cross-model review defeated with a text file containing one comment.
    """

    def test_a_plain_text_file_is_not_coverage(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            (root / "not-a-workflow.txt").write_text(
                "# launchpad/skills/alpha", encoding="utf-8"
            )
            problems = m.exclusion_problems(
                "alpha", "not-a-workflow.txt", repo_root=root
            )
        self.assertEqual(len(problems), 1)
        self.assertIn("not under .github/workflows/", problems[0])

    def test_a_file_outside_the_workflows_directory_is_not_coverage(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            (root / "elsewhere.yml").write_text(
                "paths:\n  - launchpad/skills/alpha/**\npytest\n", encoding="utf-8"
            )
            problems = m.exclusion_problems("alpha", "elsewhere.yml", repo_root=root)
        self.assertIn("not under .github/workflows/", problems[0])

    def test_a_workflow_mentioning_the_skill_only_in_a_comment_is_not_coverage(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            wf = root / ".github" / "workflows"
            wf.mkdir(parents=True)
            (wf / "wf.yml").write_text(
                "# covers launchpad/skills/alpha one day\n"
                "on:\n  pull_request:\n    paths:\n      - 'other/**'\n"
                "jobs:\n  t:\n    steps:\n      - run: pytest tests\n",
                encoding="utf-8",
            )
            problems = m.exclusion_problems(
                "alpha", ".github/workflows/wf.yml", repo_root=root
            )
        self.assertEqual(len(problems), 1)
        self.assertIn("no trigger path", problems[0])

    def test_a_workflow_triggered_on_the_skill_but_running_no_tests_is_not_coverage(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            wf = root / ".github" / "workflows"
            wf.mkdir(parents=True)
            (wf / "wf.yml").write_text(
                "on:\n  pull_request:\n    paths:\n"
                "      - 'launchpad/skills/alpha/**'\n"
                "jobs:\n  t:\n    steps:\n      - run: echo hello\n",
                encoding="utf-8",
            )
            problems = m.exclusion_problems(
                "alpha", ".github/workflows/wf.yml", repo_root=root
            )
        self.assertEqual(len(problems), 1)
        self.assertIn("no test runner", problems[0])

    def test_paths_ignore_does_not_count_as_a_trigger(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            wf = root / ".github" / "workflows"
            wf.mkdir(parents=True)
            (wf / "wf.yml").write_text(
                "on:\n  pull_request:\n    paths-ignore:\n"
                "      - 'launchpad/skills/alpha/**'\n"
                "jobs:\n  t:\n    steps:\n      - run: pytest tests\n",
                encoding="utf-8",
            )
            problems = m.exclusion_problems(
                "alpha", ".github/workflows/wf.yml", repo_root=root
            )
        self.assertIn("no trigger path", problems[0])

    def test_the_real_rqa_workflow_satisfies_the_claim(self):
        """The one exclusion actually in the committed manifest."""
        self.assertEqual(
            m.exclusion_problems(
                "review-queue-automation", ".github/workflows/launchpad-rqa-tests.yml"
            ),
            [],
        )


class TriggerPathTests(unittest.TestCase):
    def test_collects_entries_under_paths(self):
        text = "on:\n  pull_request:\n    paths:\n      - 'a/**'\n      - \"b/**\"\n"
        self.assertEqual(m.trigger_paths(text), ["a/**", "b/**"])

    def test_ignores_paths_ignore_entries(self):
        text = "on:\n  push:\n    paths-ignore:\n      - 'a/**'\n"
        self.assertEqual(m.trigger_paths(text), [])

    def test_stops_at_the_end_of_the_block(self):
        text = (
            "on:\n  pull_request:\n    paths:\n      - 'a/**'\n"
            "jobs:\n  t:\n    steps:\n      - run: x\n"
        )
        self.assertEqual(m.trigger_paths(text), ["a/**"])

    def test_collects_from_more_than_one_block(self):
        text = (
            "on:\n  pull_request:\n    paths:\n      - 'a/**'\n"
            "  push:\n    paths:\n      - 'b/**'\n"
        )
        self.assertEqual(m.trigger_paths(text), ["a/**", "b/**"])

    def test_comments_inside_a_block_are_skipped_not_collected(self):
        text = "paths:\n  # a note\n  - 'a/**'\n"
        self.assertEqual(m.trigger_paths(text), ["a/**"])


class FloorDropTests(unittest.TestCase):
    """The ratchet. Before this, the only thing stopping a lowered floor was
    the sentence 'do not lower the floor' inside an error message."""

    def test_holding_a_floor_is_fine(self):
        self.assertEqual(m.floor_drop_problems({"a": 9}, {"a": 9}), [])

    def test_raising_a_floor_is_fine(self):
        self.assertEqual(m.floor_drop_problems({"a": 9}, {"a": 20}), [])

    def test_lowering_a_floor_is_rejected(self):
        problems = m.floor_drop_problems({"evidence-reduce": 90}, {"evidence-reduce": 1})
        self.assertEqual(len(problems), 1)
        self.assertIn("drops from 90 to 1", problems[0])

    def test_a_declared_drop_with_a_reason_is_allowed(self):
        problems = m.floor_drop_problems(
            {"a": 9}, {"a": 4}, {"a": "five cases moved to the shared suite"}
        )
        self.assertEqual(problems, [])

    def test_an_empty_reason_does_not_count_as_declared(self):
        problems = m.floor_drop_problems({"a": 9}, {"a": 4}, {"a": ""})
        self.assertEqual(len(problems), 1)
        self.assertIn("drops from 9 to 4", problems[0])

    def test_a_stale_exemption_is_rejected(self):
        """Left behind, it would silently permit the next real drop."""
        problems = m.floor_drop_problems({"a": 9}, {"a": 9}, {"a": "last time"})
        self.assertEqual(len(problems), 1)
        self.assertIn("stale exemption", problems[0])

    def test_a_new_skill_absent_from_the_base_is_not_a_drop(self):
        self.assertEqual(m.floor_drop_problems({}, {"new": 3}), [])

    def test_a_skill_removed_from_run_here_is_not_a_drop(self):
        self.assertEqual(m.floor_drop_problems({"gone": 9}, {}), [])

    def test_committed_manifest_declares_no_floor_drops(self):
        self.assertEqual(m.load_floor_drops(), {})


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

    def test_a_parametrized_node_id_cannot_suppress_a_healthy_count(self):
        """Regression: a healthy suite must not go red because of a test's name.

        pytest renders `parametrize("msg", ["1 error"])` as the literal collection
        line `tests/test_probe.py::test_reports[1 error]` -- verified against
        pytest 8.3.4, spaces intact. Scanning the whole output matched the error
        pattern there and reported a healthy 3-test suite as unreadable.
        """
        output = (
            "tests/test_probe.py::test_reports[1 error]\n"
            "tests/test_probe.py::test_reports[ok]\n"
            "tests/test_probe.py::test_other\n"
            "\n"
            "3 tests collected in 0.01s\n"
        )
        self.assertEqual(m.parse_collected(output), 3)

    def test_a_parametrized_node_id_cannot_forge_a_count(self):
        output = (
            "tests/test_x.py::test_a[25 tests collected]\n"
            "\n"
            "1 test collected in 0.01s\n"
        )
        self.assertEqual(m.parse_collected(output), 1)

    def test_a_parametrized_node_id_cannot_forge_an_empty_suite(self):
        output = (
            "tests/test_x.py::test_a[no tests collected]\n"
            "\n"
            "7 tests collected in 0.01s\n"
        )
        self.assertEqual(m.parse_collected(output), 7)

    def test_real_collection_error_summary_is_still_rejected(self):
        """pytest 8.3.4's actual error summary, which must still fail."""
        output = (
            "ERROR tests/test_broken.py\n"
            "!!!!!!!! Interrupted: 1 error during collection !!!!!!!!\n"
            "3 tests collected, 1 error in 0.07s\n"
        )
        self.assertIsNone(m.parse_collected(output))

    def test_summary_line_ignores_trailing_blank_lines(self):
        self.assertEqual(
            m.summary_line("9 tests collected in 0.1s\n\n\n"),
            "9 tests collected in 0.1s",
        )

    def test_summary_line_of_empty_output_is_empty(self):
        self.assertEqual(m.summary_line(""), "")

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

class CommandTests(unittest.TestCase):
    """Drive the two subcommands the workflow actually invokes.

    An earlier version of this file asserted on a list comprehension written
    inside the test rather than on cmd_matrix's output. It passed with
    cmd_matrix gutted to `print(json.dumps([]))` -- an empty matrix that runs
    no suite at all, which is the exact catastrophe this lane exists to
    prevent. These call the real commands and read their real stdout.
    """

    def _capture(self, argv, run_here, covered_elsewhere=None):
        import contextlib
        import io

        real_load = m.load_manifest
        m.load_manifest = lambda *a, **k: (run_here, covered_elsewhere or {})
        try:
            with contextlib.redirect_stdout(io.StringIO()) as out:
                code = m.main(argv)
            return code, out.getvalue()
        finally:
            m.load_manifest = real_load

    def test_matrix_emits_one_entry_per_run_here_skill(self):
        code, out = self._capture(["matrix"], {"beta": 2, "alpha": 9})
        self.assertEqual(code, 0)
        self.assertEqual(
            json.loads(out),
            [{"skill": "alpha", "floor": 9}, {"skill": "beta", "floor": 2}],
        )

    def test_matrix_is_sorted_so_job_names_are_stable(self):
        _, out = self._capture(["matrix"], {"zulu": 1, "alpha": 1, "mike": 1})
        self.assertEqual(
            [e["skill"] for e in json.loads(out)], ["alpha", "mike", "zulu"]
        )

    def test_matrix_of_a_single_skill_is_still_a_list(self):
        _, out = self._capture(["matrix"], {"only": 3})
        self.assertEqual(json.loads(out), [{"skill": "only", "floor": 3}])

    def test_check_exits_zero_on_the_real_consistent_tree(self):
        run_here, covered = m.load_manifest()
        code, out = self._capture(["check"], run_here, covered)
        self.assertEqual(code, 0)
        self.assertIn("consistent", out)

    def test_check_exits_one_and_names_the_skill_when_undeclared(self):
        code, out = self._capture(["check"], {"analysis-technique": 25})
        self.assertEqual(code, 1)
        self.assertIn("::error::", out)
        self.assertIn("evidence-reduce", out)


class RealManifestTests(unittest.TestCase):
    def test_every_floor_in_the_committed_manifest_is_a_real_int(self):
        """A JSON `true` would otherwise pass as floor 1 -- bool subclasses int."""
        run_here, _ = m.load_manifest()
        self.assertNotEqual(run_here, {})
        for skill, floor in run_here.items():
            with self.subTest(skill=skill):
                self.assertNotIsInstance(floor, bool)
                self.assertIsInstance(floor, int)
                self.assertGreaterEqual(floor, 1)


if __name__ == "__main__":
    unittest.main()
