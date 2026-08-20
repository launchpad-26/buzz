#!/usr/bin/env python3
"""Controls for run_dimensions.py -- issue #117 STEP 3's concurrent runner.

Scope: this module alone. It does not exercise ``contain.py``/``fetch.py``
themselves (those have their own controls -- ``check_step3.py`` and friends,
issue #120's suite) and it is not wired into ``run_controls.py`` (that list is
#120's own containment-control suite; wiring this file into it, or into
``check_dimensions.py``, is STEP 9's job later, not this task's).

STEP 4's three dimension prompt files do not exist yet, so every test here
either injects an explicit ``dimensions`` list into ``build_document`` (the
core, testable entry point) or points ``list_dimensions`` at a temporary
directory -- never at the real, currently-empty ``dimensions/``.

Run:  python3 -m unittest test_run_dimensions    (from launchpad/review-agent/)
  or: python3 test_run_dimensions.py
"""

from __future__ import annotations

import contextlib
import io
import itertools
import json
import tempfile
import threading
import time
import unittest
from pathlib import Path
from unittest import mock

import contain
import fetch
import findings
import run_dimensions

HERE = Path(__file__).parent
PAYLOAD_PATH = str(HERE / "fixtures" / "captured-pr.json")

PR = 42
MERGE_BASE_SHA = "a" * 40
HEAD_SHA = "b" * 40
DIMENSIONS = ["dim-alpha", "dim-beta", "dim-gamma"]


def clean_reviewer(document: str) -> dict:
    return {"outcome": "clean", "findings": []}


def indexed_reviewer(behaviors):
    """A reviewer whose behavior depends on call ORDER, not on which dimension it
    was invoked for. ``behaviors`` is a list of zero-argument callables; a lock
    around a shared counter assigns each concurrent call a unique index, so
    exactly one call gets each behavior regardless of which worker thread wins
    the race to run first.
    """
    counter = itertools.count()
    lock = threading.Lock()

    def reviewer(document: str):
        with lock:
            index = next(counter)
        return behaviors[index]()

    return reviewer


def make_finding(**overrides) -> dict:
    """A well-formed ten-field finding dict, mirroring test_findings.py's helper."""
    base = dict(
        dimension="dim-alpha",
        severity="High",
        anchor="line",
        file="crates/buzz-relay/src/lib.rs",
        line=42,
        defect="hardcoded credential",
        failure="credential leaks to logs",
        entry_point=None,
        evidence=None,
    )
    base.update(overrides)
    base["finding_id"] = findings.finding_id(
        base["dimension"], base["anchor"], base["file"], base["line"],
        base["entry_point"], base["defect"], base["evidence"],
    )
    return base


def load_fixture_surfaces() -> dict:
    return fetch.from_payload(PAYLOAD_PATH)


def fake_completed_process(stdout_bytes: bytes, returncode: int = 0, stderr_bytes: bytes = b""):
    """A stand-in for ``subprocess.CompletedProcess`` -- only the three attributes
    ``run_dimensions.py`` reads (``returncode``, ``stdout``, ``stderr``).
    """
    proc = mock.Mock()
    proc.returncode = returncode
    proc.stdout = stdout_bytes
    proc.stderr = stderr_bytes
    return proc


def build_gh_include_output(status_line: str, headers: dict, body: str) -> bytes:
    """The byte shape ``gh api ... --include`` produces: a status line, headers,
    a blank line, then the body -- what ``_http_probe`` parses.
    """
    header_lines = "\r\n".join(f"{key}: {value}" for key, value in headers.items())
    text = f"{status_line}\r\n{header_lines}\r\n\r\n{body}"
    return text.encode("utf-8")


class BuildDocumentShapeTests(unittest.TestCase):
    """--payload-style runs (surfaces built offline) against the core function."""

    def setUp(self):
        self.surfaces = load_fixture_surfaces()
        self.nonce = contain.make_nonce(seed="step3-tests")

    def test_clean_stub_produces_one_report_per_dimension_and_validates(self):
        doc = run_dimensions.build_document(
            PR, MERGE_BASE_SHA, HEAD_SHA, self.surfaces, DIMENSIONS, self.nonce,
            reviewer=clean_reviewer, timeout=5.0,
        )
        self.assertEqual(len(doc["reports"]), len(DIMENSIONS))
        self.assertTrue(all(r["status"] == "complete" for r in doc["reports"]))
        self.assertTrue(all(r["outcome"] == "clean" for r in doc["reports"]))
        self.assertEqual(findings.validate(doc), [])

    def test_default_reviewer_is_the_clean_stub(self):
        doc = run_dimensions.build_document(
            PR, MERGE_BASE_SHA, HEAD_SHA, self.surfaces, DIMENSIONS, self.nonce,
            timeout=5.0,
        )
        self.assertEqual(findings.validate(doc), [])
        for report in doc["reports"]:
            self.assertEqual(report["status"], "complete")
            self.assertEqual(report["outcome"], "clean")
            self.assertEqual(report["findings"], [])

    def test_merged_document_has_exactly_the_contract_keys(self):
        doc = run_dimensions.build_document(
            PR, MERGE_BASE_SHA, HEAD_SHA, self.surfaces, DIMENSIONS, self.nonce,
            reviewer=clean_reviewer, timeout=5.0,
        )
        self.assertEqual(
            set(doc.keys()),
            {"pr", "merge_base_sha", "head_sha", "reports", "containment", "nonce"},
        )
        self.assertEqual(doc["pr"], PR)
        self.assertEqual(doc["merge_base_sha"], MERGE_BASE_SHA)
        self.assertEqual(doc["head_sha"], HEAD_SHA)

    def test_nonce_matches_every_reports_completion_marker(self):
        doc = run_dimensions.build_document(
            PR, MERGE_BASE_SHA, HEAD_SHA, self.surfaces, DIMENSIONS, self.nonce,
            reviewer=clean_reviewer, timeout=5.0,
        )
        # Read the nonce back out of the document itself, not the `self.nonce`
        # variable already held -- proves the field round-trips through the
        # produced JSON rather than merely matching what was passed in.
        round_tripped = json.loads(json.dumps(doc))
        document_nonce = round_tripped["nonce"]
        for report in round_tripped["reports"]:
            marker = report["completion_marker"]
            _, _marker_dimension, marker_nonce = marker.split(":", 2)
            self.assertEqual(marker_nonce, document_nonce)

    def test_containment_findings_and_states_match_contain_render_verbatim(self):
        expected_document, expected_findings, _all_readable, expected_states = contain.render(
            self.surfaces, self.nonce
        )
        doc = run_dimensions.build_document(
            PR, MERGE_BASE_SHA, HEAD_SHA, self.surfaces, DIMENSIONS, self.nonce,
            reviewer=clean_reviewer, timeout=5.0,
        )
        self.assertEqual(
            doc["containment"]["findings"],
            [f.as_dict() for f in expected_findings],
        )
        self.assertEqual(doc["containment"]["states"], expected_states)
        self.assertEqual(set(doc["containment"]["states"].keys()), set(contain.ENTRY_POINTS))

    def test_degrade_pr_diff_oversized_reflected_in_states_and_still_valid(self):
        surfaces = fetch.degrade(self.surfaces, "pr_diff=oversized")
        doc = run_dimensions.build_document(
            PR, MERGE_BASE_SHA, HEAD_SHA, surfaces, DIMENSIONS, self.nonce,
            reviewer=clean_reviewer, timeout=5.0,
        )
        self.assertEqual(doc["containment"]["states"]["pr_diff"], "oversized")
        self.assertEqual(findings.validate(doc), [])


class ReviewerFailureTests(unittest.TestCase):
    def setUp(self):
        self.surfaces = load_fixture_surfaces()
        self.nonce = contain.make_nonce(seed="step3-failure-tests")

    def test_one_reviewer_raising_fails_only_that_dimension(self):
        def ok():
            return {"outcome": "clean", "findings": []}

        def boom():
            raise RuntimeError("boom")

        reviewer = indexed_reviewer([ok, boom, ok])
        doc = run_dimensions.build_document(
            PR, MERGE_BASE_SHA, HEAD_SHA, self.surfaces, DIMENSIONS, self.nonce,
            reviewer=reviewer, timeout=5.0,
        )
        statuses = [r["status"] for r in doc["reports"]]
        self.assertEqual(statuses.count("failed"), 1)
        self.assertEqual(statuses.count("complete"), 2)
        failed = next(r for r in doc["reports"] if r["status"] == "failed")
        self.assertIn("boom", failed["error"]["reason"])
        self.assertIsNone(failed["outcome"])
        self.assertEqual(failed["findings"], [])
        self.assertEqual(failed["findings_count"], 0)
        # Even a failed report keeps a valid, last-key completion marker.
        self.assertEqual(list(failed.keys())[-1], "completion_marker")
        self.assertEqual(findings.validate(doc), [])

    def test_one_reviewer_timing_out_fails_only_that_dimension_and_does_not_hang(self):
        def ok():
            return {"outcome": "clean", "findings": []}

        def slow():
            time.sleep(2.0)
            return {"outcome": "clean", "findings": []}

        reviewer = indexed_reviewer([ok, slow, ok])
        start = time.monotonic()
        doc = run_dimensions.build_document(
            PR, MERGE_BASE_SHA, HEAD_SHA, self.surfaces, DIMENSIONS, self.nonce,
            reviewer=reviewer, timeout=0.1,
        )
        elapsed = time.monotonic() - start
        self.assertLess(elapsed, 1.0, "run should not block on the slow reviewer")
        statuses = [r["status"] for r in doc["reports"]]
        self.assertEqual(statuses.count("failed"), 1)
        self.assertEqual(statuses.count("complete"), 2)
        failed = next(r for r in doc["reports"] if r["status"] == "failed")
        self.assertIn("timed out", failed["error"]["reason"])

    def test_reviewer_output_failing_validate_produces_failed_report(self):
        def bad_outcome_findings_mismatch():
            # outcome "clean" with a non-empty findings array: a structural
            # violation findings.validate() catches (§ the report envelope).
            return {"outcome": "clean", "findings": [make_finding()]}

        reviewer = lambda document: bad_outcome_findings_mismatch()  # noqa: E731
        doc = run_dimensions.build_document(
            PR, MERGE_BASE_SHA, HEAD_SHA, self.surfaces, DIMENSIONS, self.nonce,
            reviewer=reviewer, timeout=5.0,
        )
        self.assertTrue(all(r["status"] == "failed" for r in doc["reports"]))
        for report in doc["reports"]:
            self.assertIn("validate", report["error"]["reason"])
        self.assertEqual(findings.validate(doc), [])

    def test_exit_code_is_nonzero_when_any_dimension_failed(self):
        def ok():
            return {"outcome": "clean", "findings": []}

        def boom():
            raise RuntimeError("boom")

        reviewer = indexed_reviewer([ok, boom, ok])
        doc = run_dimensions.build_document(
            PR, MERGE_BASE_SHA, HEAD_SHA, self.surfaces, DIMENSIONS, self.nonce,
            reviewer=reviewer, timeout=5.0,
        )
        all_complete = all(r["status"] == "complete" for r in doc["reports"])
        self.assertFalse(all_complete)


class ConcurrencyTests(unittest.TestCase):
    def test_three_reviewers_run_concurrently_not_serially(self):
        def reviewer(document: str) -> dict:
            time.sleep(0.2)
            return {"outcome": "clean", "findings": []}

        surfaces = load_fixture_surfaces()
        nonce = contain.make_nonce(seed="step3-concurrency")
        start = time.monotonic()
        doc = run_dimensions.build_document(
            PR, MERGE_BASE_SHA, HEAD_SHA, surfaces, DIMENSIONS, nonce,
            reviewer=reviewer, timeout=5.0,
        )
        elapsed = time.monotonic() - start
        # Closer to one sleep (0.2s) than to three serial sleeps (0.6s).
        self.assertLess(elapsed, 0.45)
        self.assertTrue(all(r["status"] == "complete" for r in doc["reports"]))


class PayloadModeNetworkFreeTests(unittest.TestCase):
    def _with_fake_dimensions_dir(self):
        """A temp dimensions/ with 3 stub .py files, standing in for STEP 4's real
        ones -- so a full CLI run today exercises the actual production code path
        (list_dimensions() -> build_document()) instead of the real, still-empty
        dimensions/, which legitimately produces zero reports and is out of scope
        for this test (that degenerate today-only state is covered by
        ListModeTests instead).
        """
        tmp = tempfile.TemporaryDirectory()
        directory = Path(tmp.name)
        for slug in ("dim-one", "dim-two", "dim-three"):
            (directory / f"{slug}.py").write_text("# stub dimension\n")
        self.addCleanup(tmp.cleanup)
        return mock.patch.object(run_dimensions, "DIMENSIONS_DIR", directory)

    def test_payload_mode_never_invokes_gh_or_subprocess(self):
        with self._with_fake_dimensions_dir(), \
             mock.patch("fetch.subprocess.run") as fetch_run, \
             mock.patch("run_dimensions.subprocess.run") as runner_run:
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                exit_code = run_dimensions.main(["--payload", PAYLOAD_PATH, "--seed", "cli-test"])
            fetch_run.assert_not_called()
            runner_run.assert_not_called()
        self.assertEqual(exit_code, run_dimensions.EXIT_OK)
        doc = json.loads(buf.getvalue())
        self.assertEqual(len(doc["reports"]), 3)
        self.assertEqual(findings.validate(doc), [])

    def test_payload_mode_pr_number_optional_defaults_to_zero(self):
        with self._with_fake_dimensions_dir():
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                exit_code = run_dimensions.main(["--payload", PAYLOAD_PATH, "--seed", "cli-default-pr"])
        self.assertEqual(exit_code, run_dimensions.EXIT_OK)
        doc = json.loads(buf.getvalue())
        self.assertEqual(doc["pr"], 0)

    def test_pr_and_payload_are_mutually_exclusive(self):
        # The positional `pr` and `--payload` form a mutually exclusive pair, the
        # same shape as contain.py's own --pr/--payload group -- so a payload run
        # cannot also carry an explicit pr number on the command line; it always
        # gets the default (0) or whatever the payload file itself states.
        buf = io.StringIO()
        with self.assertRaises(SystemExit), contextlib.redirect_stderr(buf):
            run_dimensions.main(["7", "--payload", PAYLOAD_PATH])

    def test_pr_required_unless_payload_given(self):
        buf = io.StringIO()
        with self.assertRaises(SystemExit), contextlib.redirect_stderr(buf):
            run_dimensions.main([])


class ListModeTests(unittest.TestCase):
    def test_list_dimensions_on_missing_directory_is_empty(self):
        with tempfile.TemporaryDirectory() as tmp:
            missing = Path(tmp) / "does-not-exist"
            self.assertEqual(run_dimensions.list_dimensions(missing), [])

    def test_list_dimensions_reads_py_files_sorted_and_ignores_others(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            (directory / "zeta.py").write_text("# stub\n")
            (directory / "alpha.py").write_text("# stub\n")
            (directory / ".gitkeep").write_text("placeholder\n")
            (directory / "notes.md").write_text("not a dimension\n")
            self.assertEqual(run_dimensions.list_dimensions(directory), ["alpha", "zeta"])

    def test_list_mode_cli_prints_sorted_slugs(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            (directory / "zeta.py").write_text("# stub\n")
            (directory / "alpha.py").write_text("# stub\n")
            with mock.patch.object(run_dimensions, "DIMENSIONS_DIR", directory):
                buf = io.StringIO()
                with contextlib.redirect_stdout(buf):
                    exit_code = run_dimensions.main(["--list"])
        self.assertEqual(exit_code, run_dimensions.EXIT_OK)
        self.assertEqual(buf.getvalue().splitlines(), ["alpha", "zeta"])

    def test_list_mode_against_the_real_dimensions_dir_prints_the_three_slugs(self):
        # STEP 4 (#117) populated the real dimensions/ directory with three files.
        # This asserts the real, on-disk state rather than a fixture, so a dimension
        # file added, removed, or renamed outside this test would be caught here too.
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            exit_code = run_dimensions.main(["--list"])
        self.assertEqual(exit_code, run_dimensions.EXIT_OK)
        self.assertEqual(
            buf.getvalue().splitlines(),
            ["claim-vs-evidence", "correctness-and-failure-modes", "secrets-and-access"],
        )


class CredentialProbeClassificationTests(unittest.TestCase):
    """Pure-function controls: no gh call, no network -- see module docstring."""

    def test_user_probe_200_is_live(self):
        outcome, _ = run_dimensions.classify_user_probe(200, "")
        self.assertEqual(outcome, "live")

    def test_user_probe_installation_token_403_is_live(self):
        outcome, reason = run_dimensions.classify_user_probe(
            403, "Resource not accessible by integration"
        )
        self.assertEqual(outcome, "live")
        self.assertTrue(reason)  # distinct from the plain-200 case's empty reason

    def test_user_probe_other_403_is_infrastructure(self):
        outcome, reason = run_dimensions.classify_user_probe(403, "Some other reason")
        self.assertEqual(outcome, "infrastructure")
        self.assertIn("403", reason)

    def test_user_probe_401_is_infrastructure(self):
        outcome, reason = run_dimensions.classify_user_probe(401, "Bad credentials")
        self.assertEqual(outcome, "infrastructure")

    def test_user_probe_network_error_is_infrastructure(self):
        outcome, reason = run_dimensions.classify_user_probe(None, "gh timed out after 30s")
        self.assertEqual(outcome, "infrastructure")

    def test_pr_probe_200_is_live(self):
        outcome, _ = run_dimensions.classify_pr_probe(200, "")
        self.assertEqual(outcome, "live")

    def test_pr_probe_404_is_no_such_pr(self):
        outcome, _ = run_dimensions.classify_pr_probe(404, "Not Found")
        self.assertEqual(outcome, "no_such_pr")

    def test_pr_probe_403_rate_limited_is_infrastructure(self):
        outcome, reason = run_dimensions.classify_pr_probe(403, "rate limited", rate_limit_remaining=0)
        self.assertEqual(outcome, "infrastructure")
        self.assertIn("rate", reason.lower())

    def test_pr_probe_403_not_rate_limited_is_blocked(self):
        outcome, reason = run_dimensions.classify_pr_probe(403, "Forbidden", rate_limit_remaining=42)
        self.assertEqual(outcome, "blocked")

    def test_pr_probe_403_with_absent_rate_limit_header_is_blocked(self):
        # rate_limit_remaining=None is the real, common case: the header is
        # genuinely absent from the response rather than present and non-zero.
        # Only a confirmed 0 counts as rate-limited; None must not be treated
        # as though it meant the same thing.
        outcome, _ = run_dimensions.classify_pr_probe(403, "Forbidden", rate_limit_remaining=None)
        self.assertEqual(outcome, "blocked")

    def test_pr_probe_401_is_infrastructure(self):
        outcome, _ = run_dimensions.classify_pr_probe(401, "Bad credentials")
        self.assertEqual(outcome, "infrastructure")

    def test_pr_probe_network_error_is_infrastructure(self):
        outcome, _ = run_dimensions.classify_pr_probe(None, "gh timed out after 30s")
        self.assertEqual(outcome, "infrastructure")

    def test_no_such_pr_reason_never_collides_with_an_infrastructure_reason(self):
        no_such_pr_outcome, no_such_pr_reason = run_dimensions.classify_pr_probe(404, "Not Found")
        infra_outcomes_and_reasons = [
            run_dimensions.classify_pr_probe(401, "Bad credentials"),
            run_dimensions.classify_pr_probe(403, "rate limited", rate_limit_remaining=0),
            run_dimensions.classify_pr_probe(None, "network error"),
        ]
        self.assertEqual(no_such_pr_outcome, "no_such_pr")
        for outcome, reason in infra_outcomes_and_reasons:
            self.assertEqual(outcome, "infrastructure")
            self.assertNotEqual(reason, no_such_pr_reason)

    def test_blocked_outcome_is_distinct_from_infrastructure_and_no_such_pr(self):
        blocked_outcome, _ = run_dimensions.classify_pr_probe(403, "Forbidden", rate_limit_remaining=5)
        self.assertNotIn(blocked_outcome, ("infrastructure", "no_such_pr", "live"))


class NoDimensionsTests(unittest.TestCase):
    """Fix for the Blocker finding: zero dimensions must never read as exit 0.

    ``all(status == "complete" for report in [])`` is vacuously True in Python,
    so without an explicit check, a run with no dimension files would print an
    empty-``reports`` document and exit 0 -- exactly the document
    ``findings.validate()`` itself rejects.
    """

    def test_build_document_with_empty_dimensions_list_produces_no_reports(self):
        surfaces = load_fixture_surfaces()
        nonce = contain.make_nonce(seed="step3-empty-dims")
        doc = run_dimensions.build_document(
            PR, MERGE_BASE_SHA, HEAD_SHA, surfaces, [], nonce, timeout=1.0
        )
        self.assertEqual(doc["reports"], [])
        self.assertIn(
            "document.reports: must not be empty — a run produces at least one report",
            findings.validate(doc),
        )

    def test_main_exits_no_dimensions_when_dimensions_dir_is_empty(self):
        with tempfile.TemporaryDirectory() as tmp:
            empty_dir = Path(tmp)  # no *.py files at all
            with mock.patch.object(run_dimensions, "DIMENSIONS_DIR", empty_dir), \
                 mock.patch("fetch.subprocess.run") as fetch_run, \
                 mock.patch("run_dimensions.subprocess.run") as runner_run:
                buf_out, buf_err = io.StringIO(), io.StringIO()
                with contextlib.redirect_stdout(buf_out), contextlib.redirect_stderr(buf_err):
                    exit_code = run_dimensions.main(
                        ["--payload", PAYLOAD_PATH, "--seed", "no-dims"]
                    )
            fetch_run.assert_not_called()
            runner_run.assert_not_called()
        self.assertEqual(exit_code, run_dimensions.EXIT_NO_DIMENSIONS)
        self.assertNotEqual(exit_code, run_dimensions.EXIT_OK)
        self.assertEqual(buf_out.getvalue(), "")  # no document printed at all
        self.assertIn("NO DIMENSIONS", buf_err.getvalue())


class HungReviewerDaemonThreadTests(unittest.TestCase):
    """Fix for the High finding: a reviewer that never returns (not merely a
    slow-but-finite call) must not block the process from exiting.
    """

    def test_hung_reviewer_does_not_block_collection_and_its_thread_is_daemon(self):
        block_forever = threading.Event()  # deliberately never set

        def hung_reviewer(document: str) -> dict:
            block_forever.wait()  # simulates a genuinely stalled model call
            return {"outcome": "clean", "findings": []}  # pragma: no cover

        surfaces = load_fixture_surfaces()
        nonce = contain.make_nonce(seed="step3-hung-thread")
        threads_before = set(threading.enumerate())

        start = time.monotonic()
        doc = run_dimensions.build_document(
            PR, MERGE_BASE_SHA, HEAD_SHA, surfaces, ["only-dim"], nonce,
            reviewer=hung_reviewer, timeout=0.1,
        )
        elapsed = time.monotonic() - start

        self.assertLess(elapsed, 1.0, "collection must not wait for a reviewer that never returns")
        self.assertEqual(doc["reports"][0]["status"], "failed")
        self.assertIn("timed out", doc["reports"][0]["error"]["reason"])

        new_threads = set(threading.enumerate()) - threads_before
        self.assertTrue(new_threads, "expected the hung reviewer's thread to still be alive")
        for thread in new_threads:
            self.assertTrue(
                thread.daemon,
                f"{thread} must be a daemon thread -- a non-daemon thread stuck "
                "here would be joined by concurrent.futures.thread's atexit hook "
                "(if it were a ThreadPoolExecutor worker) or by Python's normal "
                "thread-join-at-exit behavior, blocking the whole process from "
                "exiting even after every dimension has already been reported.",
            )


class LiveModeExitCodeWiringTests(unittest.TestCase):
    """The live (non-``--payload``) branch's exit-code wiring, with
    ``probe_credential_and_pr`` mocked -- no network, no ``gh`` call.
    """

    def _run_live(self, probe_return):
        with mock.patch(
            "run_dimensions.probe_credential_and_pr", return_value=probe_return
        ), mock.patch("run_dimensions.subprocess.run") as runner_run, mock.patch(
            "fetch.subprocess.run"
        ) as fetch_run:
            buf_out, buf_err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(buf_out), contextlib.redirect_stderr(buf_err):
                exit_code = run_dimensions.main(["123"])
        return exit_code, buf_out.getvalue(), buf_err.getvalue(), runner_run, fetch_run

    def test_no_such_pr_outcome_exits_with_no_such_pr_code(self):
        exit_code, out, err, runner_run, fetch_run = self._run_live(
            ("no_such_pr", "pull request not found", None)
        )
        self.assertEqual(exit_code, run_dimensions.EXIT_NO_SUCH_PR)
        self.assertEqual(out, "")
        self.assertIn("NO SUCH PR", err)
        runner_run.assert_not_called()
        fetch_run.assert_not_called()

    def test_blocked_outcome_exits_with_blocked_code(self):
        exit_code, out, err, runner_run, fetch_run = self._run_live(
            ("blocked", "credential blocked from this pull request", None)
        )
        self.assertEqual(exit_code, run_dimensions.EXIT_BLOCKED)
        self.assertEqual(out, "")
        self.assertIn("BLOCKED", err)
        runner_run.assert_not_called()
        fetch_run.assert_not_called()

    def test_infrastructure_outcome_exits_with_infrastructure_code(self):
        exit_code, out, err, runner_run, fetch_run = self._run_live(
            ("infrastructure", "bad credentials", None)
        )
        self.assertEqual(exit_code, run_dimensions.EXIT_INFRASTRUCTURE)
        self.assertEqual(out, "")
        self.assertIn("INFRASTRUCTURE", err)
        runner_run.assert_not_called()
        fetch_run.assert_not_called()

    def test_live_outcome_proceeds_and_reuses_the_probes_pr_json(self):
        """Also covers the Medium finding: the PR JSON is fetched once, not
        twice -- ``resolve_commit_pair`` must be called with the ``pr_json``
        ``probe_credential_and_pr`` already returned, never re-fetching it.
        """
        pr_json = {
            "base": {"ref": "launchpad", "sha": "c" * 40},
            "head": {"ref": "feature-x", "sha": HEAD_SHA},
        }
        with tempfile.TemporaryDirectory() as tmp:
            fake_dims = Path(tmp)
            for slug in ("dim-one", "dim-two"):
                (fake_dims / f"{slug}.py").write_text("# stub\n")

            with mock.patch(
                "run_dimensions.probe_credential_and_pr", return_value=("live", "", pr_json)
            ) as probe, mock.patch(
                "run_dimensions.resolve_commit_pair", return_value=(MERGE_BASE_SHA, HEAD_SHA)
            ) as resolve, mock.patch(
                "fetch.fetch_all", return_value=load_fixture_surfaces()
            ) as fetch_all, mock.patch.object(
                run_dimensions, "DIMENSIONS_DIR", fake_dims
            ):
                buf = io.StringIO()
                with contextlib.redirect_stdout(buf):
                    exit_code = run_dimensions.main(["123", "--seed", "live-happy-path"])

        self.assertEqual(exit_code, run_dimensions.EXIT_OK)
        probe.assert_called_once_with(fetch.DEFAULT_REPO, 123)
        resolve.assert_called_once_with(fetch.DEFAULT_REPO, 123, pr_json=pr_json)
        fetch_all.assert_called_once_with(123, fetch.DEFAULT_REPO)
        doc = json.loads(buf.getvalue())
        self.assertEqual(doc["merge_base_sha"], MERGE_BASE_SHA)
        self.assertEqual(doc["head_sha"], HEAD_SHA)
        self.assertEqual(findings.validate(doc), [])


class HttpProbePlumbingTests(unittest.TestCase):
    """``_http_probe``/``_gh_api_json``/``resolve_commit_pair``, all with
    ``subprocess.run`` mocked to return captured-shape ``gh api --include``
    output -- no network, no real ``gh`` call.
    """

    def test_http_probe_parses_200_with_no_message(self):
        output = build_gh_include_output(
            "HTTP/2.0 200 OK", {"content-type": "application/json"}, '{"login":"agent"}'
        )
        with mock.patch(
            "run_dimensions.subprocess.run", return_value=fake_completed_process(output)
        ):
            status, message, rate_limit_remaining, body = run_dimensions._http_probe("user")
        self.assertEqual(status, 200)
        self.assertEqual(message, "")
        self.assertIsNone(rate_limit_remaining)
        self.assertIn("agent", body)

    def test_http_probe_parses_403_with_rate_limit_header(self):
        output = build_gh_include_output(
            "HTTP/2.0 403 Forbidden",
            {"x-ratelimit-remaining": "0", "content-type": "application/json"},
            '{"message": "API rate limit exceeded"}',
        )
        with mock.patch(
            "run_dimensions.subprocess.run", return_value=fake_completed_process(output)
        ):
            status, message, rate_limit_remaining, _body = run_dimensions._http_probe(
                "repos/launchpad-26/buzz/pulls/1"
            )
        self.assertEqual(status, 403)
        self.assertEqual(message, "API rate limit exceeded")
        self.assertEqual(rate_limit_remaining, 0)

    def test_http_probe_parses_404(self):
        output = build_gh_include_output(
            "HTTP/2.0 404 Not Found", {"content-type": "application/json"}, '{"message": "Not Found"}'
        )
        with mock.patch(
            "run_dimensions.subprocess.run", return_value=fake_completed_process(output)
        ):
            status, message, rate_limit_remaining, _body = run_dimensions._http_probe(
                "repos/launchpad-26/buzz/pulls/999999"
            )
        self.assertEqual(status, 404)
        self.assertEqual(message, "Not Found")
        self.assertIsNone(rate_limit_remaining)

    def test_http_probe_gh_not_installed_is_none_status(self):
        with mock.patch("run_dimensions.subprocess.run", side_effect=FileNotFoundError()):
            status, message, rate_limit_remaining, body = run_dimensions._http_probe("user")
        self.assertIsNone(status)
        self.assertIn("not installed", message)
        self.assertIsNone(rate_limit_remaining)
        self.assertEqual(body, "")

    def test_gh_api_json_success(self):
        proc = fake_completed_process(b'{"number": 42}')
        with mock.patch("run_dimensions.subprocess.run", return_value=proc):
            result = run_dimensions._gh_api_json("repos/x/y/pulls/42")
        self.assertEqual(result, {"number": 42})

    def test_gh_api_json_failure_raises_runtime_error(self):
        proc = fake_completed_process(b"", returncode=1, stderr_bytes=b"HTTP 404: Not Found")
        with mock.patch("run_dimensions.subprocess.run", return_value=proc):
            with self.assertRaises(RuntimeError):
                run_dimensions._gh_api_json("repos/x/y/pulls/999")

    def test_resolve_commit_pair_compares_against_head_sha_not_head_ref(self):
        pr_json_bytes = json.dumps(
            {
                "base": {"ref": "launchpad", "sha": "c" * 40},
                "head": {"ref": "some-branch-name-that-only-exists-on-a-fork", "sha": "d" * 40},
            }
        ).encode("utf-8")
        compare_json_bytes = json.dumps({"merge_base_commit": {"sha": "e" * 40}}).encode("utf-8")

        pull_proc = fake_completed_process(pr_json_bytes)
        compare_proc = fake_completed_process(compare_json_bytes)

        with mock.patch(
            "run_dimensions.subprocess.run", side_effect=[pull_proc, compare_proc]
        ) as run_mock:
            merge_base_sha, head_sha = run_dimensions.resolve_commit_pair("owner/repo", 7)

        self.assertEqual(head_sha, "d" * 40)
        self.assertEqual(merge_base_sha, "e" * 40)
        # The compare call must use the head SHA, never the head branch name --
        # an unqualified branch name resolves against the BASE repo and either
        # 404s or silently misresolves for a fork-based PR.
        compare_call_argv = run_mock.call_args_list[1].args[0]  # ["gh", "api", path]
        compare_path = compare_call_argv[2]
        self.assertIn("d" * 40, compare_path)
        self.assertNotIn("some-branch-name-that-only-exists-on-a-fork", compare_path)

    def test_resolve_commit_pair_reuses_a_supplied_pr_json_without_refetching(self):
        pr_json = {
            "base": {"ref": "launchpad", "sha": "c" * 40},
            "head": {"ref": "some-branch-name", "sha": "d" * 40},
        }
        compare_proc = fake_completed_process(
            json.dumps({"merge_base_commit": {"sha": "e" * 40}}).encode("utf-8")
        )
        with mock.patch(
            "run_dimensions.subprocess.run", return_value=compare_proc
        ) as run_mock:
            merge_base_sha, head_sha = run_dimensions.resolve_commit_pair(
                "owner/repo", 7, pr_json=pr_json
            )
        self.assertEqual(head_sha, "d" * 40)
        self.assertEqual(merge_base_sha, "e" * 40)
        # Only ONE subprocess call -- the compare call -- since pr_json was
        # already supplied and this function did not need to re-fetch it.
        self.assertEqual(run_mock.call_count, 1)


class PayloadCommitPairRoundTripTests(unittest.TestCase):
    """The ``--payload`` branch of ``merge_base_sha``/``head_sha`` resolution:
    when the payload file itself carries those keys, they round-trip into the
    printed document rather than falling back to the dummy SHA.
    """

    def test_payload_with_its_own_commit_pair_keys_round_trips_into_document(self):
        with tempfile.TemporaryDirectory() as tmp:
            payload = json.loads(Path(PAYLOAD_PATH).read_text(encoding="utf-8"))
            payload["merge_base_sha"] = "f" * 40
            payload["head_sha"] = "1" * 40
            payload_path = Path(tmp) / "payload-with-shas.json"
            payload_path.write_text(json.dumps(payload), encoding="utf-8")

            fake_dims = Path(tmp) / "dims"
            fake_dims.mkdir()
            (fake_dims / "dim-one.py").write_text("# stub\n")

            with mock.patch.object(run_dimensions, "DIMENSIONS_DIR", fake_dims):
                buf = io.StringIO()
                with contextlib.redirect_stdout(buf):
                    exit_code = run_dimensions.main(
                        ["--payload", str(payload_path), "--seed", "payload-shas"]
                    )

        self.assertEqual(exit_code, run_dimensions.EXIT_OK)
        doc = json.loads(buf.getvalue())
        self.assertEqual(doc["merge_base_sha"], "f" * 40)
        self.assertEqual(doc["head_sha"], "1" * 40)

    def test_payload_without_commit_pair_keys_falls_back_to_dummy_sha(self):
        with tempfile.TemporaryDirectory() as tmp:
            fake_dims = Path(tmp) / "dims"
            fake_dims.mkdir()
            (fake_dims / "dim-one.py").write_text("# stub\n")

            with mock.patch.object(run_dimensions, "DIMENSIONS_DIR", fake_dims):
                buf = io.StringIO()
                with contextlib.redirect_stdout(buf):
                    exit_code = run_dimensions.main(
                        ["--payload", PAYLOAD_PATH, "--seed", "payload-no-shas"]
                    )

        self.assertEqual(exit_code, run_dimensions.EXIT_OK)
        doc = json.loads(buf.getvalue())
        self.assertEqual(doc["merge_base_sha"], "0" * 40)
        self.assertEqual(doc["head_sha"], "0" * 40)


if __name__ == "__main__":
    unittest.main()
