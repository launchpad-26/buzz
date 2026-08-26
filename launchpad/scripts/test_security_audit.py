#!/usr/bin/env python3
"""Controls for the harness itself: report contract, exit code, broken-check handling."""

import unittest
from pathlib import Path
from unittest.mock import patch

import security_audit_core
from security_audit_core import CheckResult, Status, exit_code, format_report, run_all
from security_audit_selftest_check import run as harness_self_test


class FormatReportTest(unittest.TestCase):
    def test_all_four_statuses_present_and_labelled(self):
        results = [
            CheckResult("a", Status.PASS),
            CheckResult("b", Status.FAIL),
            CheckResult("c", Status.WARN),
            CheckResult("d", Status.INDETERMINATE),
        ]
        report = format_report(results)
        for marker in ("PASS", "FAIL", "WARN", "INDETERMINATE"):
            self.assertIn(marker, report)

    def test_indeterminate_never_renders_as_pass(self):
        report = format_report(
            [CheckResult("only-check", Status.INDETERMINATE, "network unreachable")]
        )
        line = next(l for l in report.splitlines() if "only-check" in l)
        self.assertIn("INDETERMINATE", line)
        self.assertNotIn("[PASS", line)

    def test_detail_is_included_when_present(self):
        report = format_report([CheckResult("x", Status.WARN, "worth a look")])
        self.assertIn("worth a look", report)

    def test_summary_counts(self):
        results = [
            CheckResult("a", Status.PASS),
            CheckResult("b", Status.PASS),
            CheckResult("c", Status.FAIL),
            CheckResult("d", Status.INDETERMINATE),
        ]
        report = format_report(results)
        self.assertIn("2 pass, 1 fail, 0 warn, 1 indeterminate", report)


class ExitCodeTest(unittest.TestCase):
    def test_zero_with_no_failures(self):
        results = [
            CheckResult("a", Status.PASS),
            CheckResult("b", Status.WARN),
            CheckResult("c", Status.INDETERMINATE),
        ]
        self.assertEqual(exit_code(results), 0)

    def test_nonzero_when_any_check_fails(self):
        results = [CheckResult("a", Status.PASS), CheckResult("b", Status.FAIL)]
        self.assertEqual(exit_code(results), 1)

    def test_zero_on_empty_results(self):
        self.assertEqual(exit_code([]), 0)


class RunAllTest(unittest.TestCase):
    def test_a_raising_check_is_recorded_as_fail_not_dropped(self):
        def broken(repo_root):
            raise ValueError("boom")

        results = run_all(Path("."), [broken])
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].status, Status.FAIL)
        self.assertIn("boom", results[0].detail)

    def test_a_raising_check_does_not_stop_the_others(self):
        def broken(repo_root):
            raise ValueError("boom")

        def fine(repo_root):
            return CheckResult("fine", Status.PASS)

        results = run_all(Path("."), [broken, fine])
        statuses = {r.name: r.status for r in results}
        self.assertEqual(statuses["fine"], Status.PASS)
        self.assertTrue(any(r.status == Status.FAIL for r in results))


class SelfTestCheckTest(unittest.TestCase):
    def test_self_test_check_passes_against_the_real_harness(self):
        result = harness_self_test(Path("."))
        self.assertEqual(result.status, Status.PASS, result.detail)

    def test_self_test_fails_when_indeterminate_collides_with_pass(self):
        # Proves the self-test can actually fail, not just pass by construction:
        # without this, a self-test rewritten to unconditionally `return
        # CheckResult(NAME, Status.PASS, "ok")` would pass every test in this
        # file. Patching the real _MARKERS dict forces format_report itself to
        # render two statuses identically, so this exercises the self-test's
        # actual detection path, not a mock standing in for it.
        with patch.dict(security_audit_core._MARKERS, {Status.INDETERMINATE: "PASS"}):
            result = harness_self_test(Path("."))
        self.assertEqual(result.status, Status.FAIL)
        self.assertIn("indeterminate", result.detail)

    def test_self_test_fails_when_two_non_pass_statuses_collide(self):
        # The pairwise check (not just each-status-vs-pass) is what this test
        # exercises: FAIL and WARN colliding never touches PASS at all, so a
        # self-test that only compared against pass would miss it.
        with patch.dict(security_audit_core._MARKERS, {Status.WARN: "FAIL"}):
            result = harness_self_test(Path("."))
        self.assertEqual(result.status, Status.FAIL)
        self.assertIn("fail", result.detail)
        self.assertIn("warn", result.detail)


if __name__ == "__main__":
    unittest.main()
