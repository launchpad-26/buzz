#!/usr/bin/env python3
"""Controls for run_adjudication.py -- issue #118 STEP 3's CLI.

Exercises every behaviour named in STEP 3's own done-when list in
launchpad/plans/2026-08-13-issue-118-adjudication.md: byte-identical
pass-through of ``pr``/``merge_base_sha``/``head_sha``/``containment``,
anchor ``pr`` adjudicated without raising, all three containment kinds
passed through with no verdict field added, malformed JSON and an
already-illegal input ``severity`` both refused before a single finding is
adjudicated (the injected judge's own call count proves the refusal happens
first), and no ``gh`` subprocess or HTTP client invoked during a stub run.

Deliberately NOT exercised here (later steps' territory, per the plan):
the nonce three-way disagreement diagnosis and the ``stages`` manifest
(STEP 4), the escalate-only guard and downgrade recording for a judge that
actually re-rates severity (STEP 6), and dedupe (STEP 7). Every fixture
below either omits a re-rating entirely or only ever asserts that this
stage's own severity pass-through (``severity == reported_severity``,
always) holds.

This file is scoped to `run_adjudication.py` alone and is deliberately not
wired into `run_controls.py`'s CONTROLS list -- that is STEP 10's control
suite over the full adjudication surface, not this module in isolation.

Run:  python3 -m unittest test_run_adjudication    (from launchpad/review-agent/)
  or: python3 test_run_adjudication.py
"""

from __future__ import annotations

import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import contain
import findings
import run_adjudication
import verdicts

HERE = Path(__file__).parent
SCRIPT = HERE / "run_adjudication.py"

NONCE = "deadbeefcafef00d"


def make_states(omit: str | None = None) -> dict:
    states = {ep: "ok" for ep in contain.ENTRY_POINTS}
    if omit is not None:
        del states[omit]
    return states


def make_raw_finding(**overrides) -> dict:
    """A well-formed #117 finding dict -- BEFORE adjudication. None of
    ADJUDICATION.md's six added fields are present, matching what #117
    actually emits.
    """
    base = dict(
        dimension="secrets-and-access",
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
    if "finding_id" not in overrides:
        base["finding_id"] = findings.finding_id(
            base["dimension"],
            base["anchor"],
            base["file"],
            base["line"],
            base["entry_point"],
            base["defect"],
            base["evidence"],
        )
    return base


def make_report(dimension="secrets-and-access", nonce=NONCE, findings_list=None, **overrides) -> dict:
    findings_list = findings_list if findings_list is not None else []
    report = dict(
        schema_version=1,
        dimension=dimension,
        pr=42,
        merge_base_sha="a" * 40,
        head_sha="b" * 40,
        status="complete",
        outcome="findings" if findings_list else "clean",
        error=None,
        findings=findings_list,
        findings_count=len(findings_list),
    )
    report.update(overrides)
    report["completion_marker"] = f"BUZZ-DIMENSION-COMPLETE:{dimension}:{nonce}"
    return report


def make_document(reports=None, nonce=NONCE, states=None, containment_findings=None) -> dict:
    reports = reports if reports is not None else [make_report(findings_list=[make_raw_finding()])]
    return dict(
        pr=42,
        merge_base_sha="a" * 40,
        head_sha="b" * 40,
        reports=reports,
        containment=dict(
            findings=containment_findings if containment_findings is not None else [],
            states=states if states is not None else make_states(),
        ),
        nonce=nonce,
    )


def make_containment_finding(kind: str, entry_point="pr_body", evidence="BUZZ-UNTRUSTED forged") -> dict:
    return {"kind": kind, "entry_point": entry_point, "evidence": evidence, "severity": "Blocker"}


class CountingJudge:
    """A judge that records how many times it was called, so a test can
    assert it was never invoked -- the mechanism STEP 3's done-when uses to
    prove the input-validation refusal happens BEFORE any judge runs, not
    merely that the output happens to look refused.
    """

    def __init__(self, verdict="REFUTED", evidence="counting judge: forced verdict"):
        self.calls: list[dict] = []
        self._verdict = verdict
        self._evidence = evidence

    def __call__(self, finding: dict, document: dict) -> dict:
        self.calls.append(finding)
        return {"verdict": self._verdict, "verdict_evidence": self._evidence}

    @property
    def call_count(self) -> int:
        return len(self.calls)


class ByteIdenticalPassThroughTests(unittest.TestCase):
    def test_pr_merge_base_head_and_containment_survive_untouched(self):
        containment_findings = [make_containment_finding("delimiter_forge")]
        input_doc = make_document(containment_findings=containment_findings)
        output_doc = run_adjudication.adjudicate(input_doc, run_adjudication.stub_judge)

        for key in ("pr", "merge_base_sha", "head_sha", "containment"):
            self.assertEqual(
                json.dumps(output_doc[key], sort_keys=True),
                json.dumps(input_doc[key], sort_keys=True),
                f"{key} was not byte-identical",
            )

    def test_output_validates_against_both_contracts(self):
        input_doc = make_document()
        output_doc = run_adjudication.adjudicate(input_doc, run_adjudication.stub_judge)
        self.assertEqual(verdicts.validate(input_doc, output_doc), [])
        self.assertEqual(findings.validate(output_doc), [])


class AnchorPrTests(unittest.TestCase):
    def test_pr_anchored_finding_adjudicates_without_raising(self):
        finding = make_raw_finding(anchor="pr", file=None, line=None)
        input_doc = make_document(reports=[make_report(findings_list=[finding])])

        output_doc = run_adjudication.adjudicate(input_doc, run_adjudication.stub_judge)

        adjudicated = output_doc["reports"][0]["findings"][0]
        self.assertTrue(adjudicated["verdict_evidence"])
        self.assertIn(adjudicated["verdict"], verdicts.VERDICTS)


class ContainmentPassThroughTests(unittest.TestCase):
    def test_all_three_containment_kinds_emitted_unchanged(self):
        kinds = ["delimiter_forge", "delimiter_lookalike", "injection_attempt"]
        containment_findings = [make_containment_finding(k) for k in kinds]
        input_doc = make_document(containment_findings=containment_findings)

        output_doc = run_adjudication.adjudicate(input_doc, run_adjudication.stub_judge)

        self.assertEqual(output_doc["containment"]["findings"], containment_findings)
        for cf in output_doc["containment"]["findings"]:
            self.assertEqual(cf["severity"], "Blocker")
            self.assertNotIn("verdict", cf)
            self.assertNotIn("verdict_evidence", cf)


class MalformedJsonTests(unittest.TestCase):
    def _run_main_with_stdin(self, stdin_text: str) -> tuple[int, str, str]:
        stdout, stderr = io.StringIO(), io.StringIO()
        with mock.patch.object(sys, "stdin", io.StringIO(stdin_text)), \
             contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            exit_code = run_adjudication.main([])
        return exit_code, stdout.getvalue(), stderr.getvalue()

    def test_malformed_json_exits_nonzero_and_prints_no_document(self):
        exit_code, stdout, stderr = self._run_main_with_stdin("{not valid json")
        self.assertNotEqual(exit_code, 0)
        self.assertEqual(stdout, "")
        self.assertTrue(stderr)

    def test_valid_json_non_object_exits_nonzero_and_prints_no_document(self):
        # `[]`, a bare string, and a bare number are all VALID JSON but not
        # objects -- json.loads succeeds on each, so this is not caught by
        # the JSONDecodeError branch above. Refused cleanly before reaching
        # findings.validate, which assumes a dict.
        for stdin_text in ("[]", '"just a string"', "42"):
            with self.subTest(stdin_text=stdin_text):
                exit_code, stdout, stderr = self._run_main_with_stdin(stdin_text)
                self.assertNotEqual(exit_code, 0)
                self.assertEqual(stdout, "")
                self.assertTrue(stderr)


class IllegalInputSeverityTests(unittest.TestCase):
    """A fixture whose one finding arrives with an out-of-ladder `severity` --
    #117's own field name; `reported_severity` does not exist until this
    stage produces it. This must be refused wholesale, before any judge runs.
    """

    def _illegal_document(self) -> dict:
        finding = make_raw_finding(severity="Info")
        return make_document(reports=[make_report(findings_list=[finding])])

    def test_adjudicate_raises_before_calling_the_judge(self):
        judge = CountingJudge(verdict="REFUTED")
        input_doc = self._illegal_document()

        with self.assertRaises(run_adjudication.InputValidationError):
            run_adjudication.adjudicate(input_doc, judge)

        self.assertEqual(judge.call_count, 0, judge.calls)

    def test_main_exits_nonzero_and_prints_no_document(self):
        input_doc = self._illegal_document()
        stdout, stderr = io.StringIO(), io.StringIO()
        with mock.patch.object(sys, "stdin", io.StringIO(json.dumps(input_doc))), \
             contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            exit_code = run_adjudication.main([])
        self.assertNotEqual(exit_code, 0)
        self.assertEqual(stdout.getvalue(), "")
        self.assertTrue(stderr.getvalue())


class NoNetworkOrSubprocessTests(unittest.TestCase):
    """A stub run must invoke neither a `gh` subprocess nor any HTTP client --
    this module never fetches PR surfaces itself (CONTAINMENT.md's
    "never re-read raw PR text"). Patched to raise on any call, so a
    regression that reaches for either fails this test rather than passing
    silently because nothing was actually asserted about call counts.
    """

    def test_stub_run_makes_no_subprocess_or_http_call(self):
        input_doc = make_document()

        def _boom(*args, **kwargs):
            raise AssertionError("run_adjudication must not invoke subprocess/HTTP during a stub run")

        with mock.patch("subprocess.run", side_effect=_boom), \
             mock.patch("subprocess.Popen", side_effect=_boom), \
             mock.patch("urllib.request.urlopen", side_effect=_boom), \
             mock.patch("http.client.HTTPConnection.request", side_effect=_boom), \
             mock.patch("http.client.HTTPSConnection.request", side_effect=_boom):
            output_doc = run_adjudication.adjudicate(input_doc, run_adjudication.stub_judge)

        self.assertEqual(verdicts.validate(input_doc, output_doc), [])


class ReplayJudgeTests(unittest.TestCase):
    """--replay's own code path, proven real (STEP 9's actual recordings do
    not exist yet -- this is a hand-built stand-in, not an end-to-end
    exercise of STEP 9's eventual format).
    """

    def test_replay_uses_the_recorded_verdict_when_present(self):
        finding = make_raw_finding()
        with tempfile.TemporaryDirectory() as tmp:
            recording_path = Path(tmp) / "recorded.json"
            recording_path.write_text(
                json.dumps(
                    {
                        finding["finding_id"]: {
                            "verdict": "CONFIRMED",
                            "verdict_evidence": "replay: read the file at head_sha, credential present.",
                        }
                    }
                )
            )
            judge = run_adjudication.make_replay_judge(Path(tmp))
            result = judge(finding, {})

        self.assertEqual(result["verdict"], "CONFIRMED")
        self.assertTrue(result["verdict_evidence"])

    def test_replay_fails_closed_to_unproven_when_no_recording_matches(self):
        finding = make_raw_finding()
        with tempfile.TemporaryDirectory() as tmp:
            judge = run_adjudication.make_replay_judge(Path(tmp))
            result = judge(finding, {})

        self.assertEqual(result["verdict"], "UNPROVEN")
        self.assertIn(finding["finding_id"], result["verdict_evidence"])

    def test_replay_dir_that_does_not_exist_fails_closed_rather_than_raising(self):
        judge = run_adjudication.make_replay_judge(Path("/nonexistent/replay/dir"))
        finding = make_raw_finding()
        result = judge(finding, {})
        self.assertEqual(result["verdict"], "UNPROVEN")


class JudgeFailsClosedTests(unittest.TestCase):
    def test_judge_exception_fails_closed_to_unproven(self):
        def _raising_judge(finding, document):
            raise RuntimeError("boom")

        input_doc = make_document()
        output_doc = run_adjudication.adjudicate(input_doc, _raising_judge)
        adjudicated = output_doc["reports"][0]["findings"][0]
        self.assertEqual(adjudicated["verdict"], "UNPROVEN")
        self.assertTrue(adjudicated["verdict_evidence"])

    def test_judge_returning_illegal_verdict_fails_closed_to_unproven(self):
        def _bad_judge(finding, document):
            return {"verdict": "APPROVED", "verdict_evidence": "looks fine"}

        input_doc = make_document()
        output_doc = run_adjudication.adjudicate(input_doc, _bad_judge)
        adjudicated = output_doc["reports"][0]["findings"][0]
        self.assertEqual(adjudicated["verdict"], "UNPROVEN")

    def test_judge_returning_empty_evidence_fails_closed_to_unproven(self):
        def _empty_evidence_judge(finding, document):
            return {"verdict": "CONFIRMED", "verdict_evidence": ""}

        input_doc = make_document()
        output_doc = run_adjudication.adjudicate(input_doc, _empty_evidence_judge)
        adjudicated = output_doc["reports"][0]["findings"][0]
        self.assertEqual(adjudicated["verdict"], "UNPROVEN")

    def test_judge_returning_whitespace_evidence_fails_closed_to_unproven(self):
        """A truthiness test is not the "unusable output" check this function
        promises: ``not "   "`` is False. ADJUDICATION.md's reason for
        requiring evidence is that "an UNPROVEN with no reason is
        indistinguishable from a stage that skipped the finding", and
        whitespace IS no reason -- so a CONFIRMED Blocker could be published
        with a blank justification and still validate clean.
        """
        for blank in ("   ", "\n", "\t", "   \n  ", "\xa0"):
            with self.subTest(evidence=blank):
                def _blank_evidence_judge(finding, document, _b=blank):
                    return {"verdict": "CONFIRMED", "verdict_evidence": _b}

                input_doc = make_document()
                output_doc = run_adjudication.adjudicate(input_doc, _blank_evidence_judge)
                adjudicated = output_doc["reports"][0]["findings"][0]
                self.assertEqual(adjudicated["verdict"], "UNPROVEN")
                self.assertTrue(adjudicated["verdict_evidence"].strip())

    def test_judge_returning_non_string_evidence_fails_closed_to_unproven(self):
        """The sibling half: the guard had no type check, so any truthy value
        passed. ``verdict_evidence: 42`` is not something a reader can act on.
        """
        for wrong_type in (42, True, 0.5, ["x"], {"a": 1}):
            with self.subTest(evidence=wrong_type):
                def _wrong_type_judge(finding, document, _w=wrong_type):
                    return {"verdict": "CONFIRMED", "verdict_evidence": _w}

                input_doc = make_document()
                output_doc = run_adjudication.adjudicate(input_doc, _wrong_type_judge)
                adjudicated = output_doc["reports"][0]["findings"][0]
                self.assertEqual(adjudicated["verdict"], "UNPROVEN")
                self.assertIsInstance(adjudicated["verdict_evidence"], str)

    def test_blank_evidence_output_still_satisfies_the_verdict_contract(self):
        """The half that makes this load-bearing: before the fix, the blank
        evidence reached the published document AND `verdicts.validate`
        returned zero violations, because the contract check used the same
        truthiness idiom. Both ends must now agree.
        """
        def _blank_evidence_judge(finding, document):
            return {"verdict": "CONFIRMED", "verdict_evidence": "   \n  "}

        input_doc = make_document()
        output_doc = run_adjudication.adjudicate(input_doc, _blank_evidence_judge)
        self.assertEqual(verdicts.validate(input_doc, output_doc), [])
        self.assertEqual(output_doc["reports"][0]["findings"][0]["verdict"], "UNPROVEN")


class ReplayBlankEvidenceTests(unittest.TestCase):
    """`--replay` forwards a recording's contents unfiltered, so the blank
    shape was reachable from an ordinary command line -- not only from an
    injected judge. This drives the guard through the shipped flag.
    """

    @staticmethod
    def _replay_run(finding, evidence):
        """Drive `adjudicate` through a real replay recording.

        The recording format is a mapping ``finding_id -> {verdict, ...}``,
        NOT a flat record -- get that wrong and the lookup misses, the judge
        fails closed with "no recorded judge output", and a test asserting
        UNPROVEN passes for entirely the wrong reason.
        """
        with tempfile.TemporaryDirectory() as tmp:
            recording = {
                finding["finding_id"]: {"verdict": "CONFIRMED", "verdict_evidence": evidence}
            }
            (Path(tmp) / "rec.json").write_text(json.dumps(recording), encoding="utf-8")
            judge = run_adjudication.make_replay_judge(Path(tmp))
            input_doc = make_document(reports=[make_report(findings_list=[finding])])
            output_doc = run_adjudication.adjudicate(input_doc, judge)
        return input_doc, output_doc

    def test_a_matching_recording_is_actually_used(self):
        """The control this class needs to be worth anything: prove the lookup
        HITS, so a later UNPROVEN is the blank-evidence guard firing and not a
        recording that was never found.
        """
        finding = make_raw_finding()
        input_doc, output_doc = self._replay_run(finding, "the credential is present at that line")
        adjudicated = output_doc["reports"][0]["findings"][0]
        self.assertEqual(adjudicated["verdict"], "CONFIRMED")
        self.assertNotIn("no recorded judge output", adjudicated["verdict_evidence"])
        self.assertEqual(verdicts.validate(input_doc, output_doc), [])

    def test_replay_recording_with_whitespace_evidence_fails_closed(self):
        finding = make_raw_finding()
        input_doc, output_doc = self._replay_run(finding, "   \n  ")
        adjudicated = output_doc["reports"][0]["findings"][0]
        self.assertEqual(adjudicated["verdict"], "UNPROVEN")
        self.assertTrue(adjudicated["verdict_evidence"].strip())
        # Specifically the guard, not a missed lookup.
        self.assertIn("unusable output", adjudicated["verdict_evidence"])
        self.assertNotIn("no recorded judge output", adjudicated["verdict_evidence"])
        self.assertEqual(verdicts.validate(input_doc, output_doc), [])


class NotesDeferralTests(unittest.TestCase):
    """`adjudication.notes` is hardcoded empty at this step and the judge
    protocol does not honour a `notes` key. That is deliberate, but it was
    undocumented -- and `adjudicator.md` (#265) normatively tells a judge to
    record new observations there. These tests pin the CURRENT behaviour so
    the deferral is asserted rather than assumed, and so whichever way #118
    resolves it, a test changes with the decision.
    """

    def test_a_judge_supplied_notes_key_is_not_carried(self):
        def _noting_judge(finding, document):
            return {
                "verdict": "CONFIRMED",
                "verdict_evidence": "the credential is present at that line",
                "notes": ["a genuinely new defect noticed while adjudicating"],
            }

        input_doc = make_document()
        output_doc = run_adjudication.adjudicate(input_doc, _noting_judge)
        # Documented deferral, not an accident: see this module's docstring.
        self.assertEqual(output_doc["adjudication"]["notes"], [])
        self.assertEqual(verdicts.validate(input_doc, output_doc), [])

    def test_the_deferral_is_stated_in_the_module_docstring(self):
        """The finding was that nothing said so. If the sentence goes, this
        test goes red rather than the gap reopening silently.
        """
        self.assertIn("notes", run_adjudication.__doc__)
        self.assertRegex(run_adjudication.__doc__, r"notes.*(defer|STEP 6/7|left empty)")


class NoRerateInThisStepTests(unittest.TestCase):
    """This step performs no re-rating at all (STEP 6's job): every finding's
    `severity` equals its `reported_severity`, even when the injected judge
    returns a verdict -- the judge protocol here carries no severity field.
    """

    def test_severity_always_equals_reported_severity(self):
        finding = make_raw_finding(severity="Blocker")
        input_doc = make_document(reports=[make_report(findings_list=[finding])])

        output_doc = run_adjudication.adjudicate(input_doc, run_adjudication.stub_judge)

        adjudicated = output_doc["reports"][0]["findings"][0]
        self.assertEqual(adjudicated["reported_severity"], "Blocker")
        self.assertEqual(adjudicated["severity"], "Blocker")
        self.assertIsNone(adjudicated["severity_reason"])
        self.assertIsNone(adjudicated["duplicate_of"])


class SubprocessInvocationTests(unittest.TestCase):
    """The literal CLI form STEP 3's done-when names:
    `python3 run_adjudication.py < fixture.json`.
    """

    def test_real_process_stub_run_exits_zero_and_prints_a_valid_document(self):
        input_doc = make_document()
        proc = subprocess.run(
            [sys.executable, str(SCRIPT)],
            input=json.dumps(input_doc),
            capture_output=True,
            text=True,
            cwd=str(HERE),
            timeout=30,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        output_doc = json.loads(proc.stdout)
        self.assertEqual(verdicts.validate(input_doc, output_doc), [])
        self.assertEqual(findings.validate(output_doc), [])

    def test_real_process_malformed_json_exits_nonzero_no_stdout(self):
        proc = subprocess.run(
            [sys.executable, str(SCRIPT)],
            input="{not json",
            capture_output=True,
            text=True,
            cwd=str(HERE),
            timeout=30,
        )
        self.assertNotEqual(proc.returncode, 0)
        self.assertEqual(proc.stdout, "")

    def test_real_process_illegal_severity_exits_nonzero_no_stdout(self):
        finding = make_raw_finding(severity="Info")
        input_doc = make_document(reports=[make_report(findings_list=[finding])])
        proc = subprocess.run(
            [sys.executable, str(SCRIPT)],
            input=json.dumps(input_doc),
            capture_output=True,
            text=True,
            cwd=str(HERE),
            timeout=30,
        )
        self.assertNotEqual(proc.returncode, 0)
        self.assertEqual(proc.stdout, "")


if __name__ == "__main__":
    unittest.main()
