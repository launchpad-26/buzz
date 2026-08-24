#!/usr/bin/env python3
"""Controls for run_adjudication.py -- issue #118 STEP 3 and STEP 4's CLI.

Exercises every behaviour named in STEP 3's own done-when list in
launchpad/plans/2026-08-13-issue-118-adjudication.md: byte-identical
pass-through of ``pr``/``merge_base_sha``/``head_sha``/``containment``,
anchor ``pr`` adjudicated without raising, all three containment kinds
passed through with no verdict field added, malformed JSON and an
already-illegal input ``severity`` both refused before a single finding is
adjudicated (the injected judge's own call count proves the refusal happens
first), and no ``gh`` subprocess or HTTP client invoked during a stub run.

Also exercises STEP 4's own done-when: the nonce check (three refusals --
``"absent provenance"``, ``"mixed document"``, ``"mismatched envelope"`` --
in that fixed order) and the ``stages`` manifest. The three refusals are
proven two ways: directly against ``_verify_nonce`` with hand-built
documents (``NonceVerificationDirectTests`` below), which is the only way to
observe their distinct reasons at all, and end to end through ``main`` with
realistic fixtures (``NonceVerificationEndToEndTests``), where every one of
them is ALSO already caught by #117's own ``findings.validate`` -- which
``adjudicate`` runs first -- with its own, less specific, message. Both are
tested because both are true: the dedicated check is real defence in depth,
per ADJUDICATION.md's own reasoning, and it does not change what ``main``
reports for any fixture that also happens to fail #117's own contract, which
is every reachable fixture today.

Also exercises STEP 6's own done-when: a judge that REFUTEs every finding
(membership/length/`findings_count` unchanged, `total_refutation` true, the
`adjudication` stage status not "complete") and the same judge against zero
findings (`total_refutation` false, status "complete"); a judge returning
the out-of-ladder severity "Info" over a legally in-ladder
`reported_severity` (UNPROVEN at the reported severity, with a reason, and
the document still passes `verdicts.validate`) -- the sibling case, a
finding ARRIVING with an illegal `reported_severity`, stays
`IllegalInputSeverityTests`' job above, not repeated here; a bare
`review.SEVERITY_ORDER[f["severity"]]` subscript over every finding in
every output; and a judge that downgrades a Blocker to Low
(`adjudication.downgrades` names it with from/to/reason). See
`SeverityRerateTests` and `TotalRefutationStatusTests` below.

Also exercises STEP 7's own done-when: given two findings from two
dimensions describing one planted defect (a ``dedupe_judge`` injected to
report them as duplicates of each other), both are present in the output,
both carry a verdict, exactly one carries `duplicate_of` naming the other,
and `duplicate_groups` carries one group naming both; the survivor is the
same across two runs of the same input, asserted by byte-comparing the two
outputs; a finding whose `duplicate_of` names an id absent from the document,
and one naming itself, are each rejected by `verdicts.validate` (that
validator already exists from STEP 2 -- confirmed here, not reimplemented);
and a run that dedupes nothing (the default `stub_dedupe_judge`) emits an
EMPTY `duplicate_groups` array rather than omitting the key. See
`DedupeTests` below.

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
import review
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
    """The stub judge never re-rates: every finding's `severity` equals its
    `reported_severity`, even though `stub_judge` returns a verdict --
    it simply never includes a `severity` key in its return dict, which
    STEP 6's guard (see `SeverityRerateTests` below) treats identically to a
    `severity` equal to `reported_severity`: no re-rating at all.
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


class NonceVerificationDirectTests(unittest.TestCase):
    """Direct, unit-level tests of ``_verify_nonce`` in isolation -- the
    three refusals' distinct reasons and their fixed precedence, without the
    rest of ``adjudicate`` around them. ``NonceVerificationEndToEndTests``
    below proves the same three reasons surface through the real CLI, now
    that ``_verify_nonce`` runs before ``findings.validate`` in
    ``adjudicate`` (see the module docstring's STEP 4 section).
    """

    def test_no_top_level_nonce_is_absent_provenance(self):
        doc = make_document(reports=[make_report(nonce=NONCE)], nonce=NONCE)
        del doc["nonce"]
        with self.assertRaises(run_adjudication.NonceVerificationError) as ctx:
            run_adjudication._verify_nonce(doc)
        self.assertEqual(ctx.exception.reason, "absent provenance")

    def test_report_with_no_parseable_marker_is_absent_provenance(self):
        report = make_report(nonce=NONCE)
        del report["completion_marker"]
        doc = make_document(reports=[report], nonce=NONCE)
        with self.assertRaises(run_adjudication.NonceVerificationError) as ctx:
            run_adjudication._verify_nonce(doc)
        self.assertEqual(ctx.exception.reason, "absent provenance")

    def test_one_unparseable_marker_among_otherwise_agreeing_reports_is_absent_provenance(self):
        # "must equal EVERY report's completion marker" cannot be checked for
        # a report whose marker cannot be read -- one bad report withholds
        # provenance for the whole document, it does not just drop out of
        # the comparison.
        good = make_report(dimension="a", nonce=NONCE)
        unreadable = make_report(dimension="b", nonce=NONCE)
        del unreadable["completion_marker"]
        doc = make_document(reports=[good, unreadable], nonce=NONCE)
        with self.assertRaises(run_adjudication.NonceVerificationError) as ctx:
            run_adjudication._verify_nonce(doc)
        self.assertEqual(ctx.exception.reason, "absent provenance")

    def test_reports_disagreeing_with_each_other_is_mixed_document(self):
        doc = make_document(
            reports=[make_report(dimension="a", nonce="N1"), make_report(dimension="b", nonce="N2")],
            nonce=NONCE,
        )
        with self.assertRaises(run_adjudication.NonceVerificationError) as ctx:
            run_adjudication._verify_nonce(doc)
        self.assertEqual(ctx.exception.reason, "mixed document")

    def test_reports_agreeing_but_not_with_top_level_is_mismatched_envelope(self):
        doc = make_document(
            reports=[make_report(dimension="a", nonce="N1"), make_report(dimension="b", nonce="N1")],
            nonce=NONCE,  # top-level differs from both reports' shared "N1"
        )
        with self.assertRaises(run_adjudication.NonceVerificationError) as ctx:
            run_adjudication._verify_nonce(doc)
        self.assertEqual(ctx.exception.reason, "mismatched envelope")

    def test_mixed_document_wins_over_mismatched_envelope_when_both_apply(self):
        # Every report disagrees with the top-level key AND with each other:
        # satisfies both "mixed document" and "mismatched envelope" at once.
        # ADJUDICATION.md states the mixed document wins.
        doc = make_document(
            reports=[make_report(dimension="a", nonce="N1"), make_report(dimension="b", nonce="N2")],
            nonce="N3",
        )
        with self.assertRaises(run_adjudication.NonceVerificationError) as ctx:
            run_adjudication._verify_nonce(doc)
        self.assertEqual(ctx.exception.reason, "mixed document")

    def test_matching_nonce_is_returned_unchanged_and_never_invented(self):
        doc = make_document(reports=[make_report(nonce=NONCE)], nonce=NONCE)
        self.assertEqual(run_adjudication._verify_nonce(doc), NONCE)


class NonceVerificationEndToEndTests(unittest.TestCase):
    """The same three refusals, through `main` with realistic fixtures --
    proving the DISTINCT reason each one names is actually observable end to
    end, not just from calling `_verify_nonce` directly.

    This is only true because `adjudicate()` runs `_verify_nonce` BEFORE
    #117's own `findings.validate`. `findings.validate` independently rejects
    the same documents, but with one generic per-report message that does not
    distinguish "reports disagree with each other" from "reports agree with
    each other but not the top-level key" -- see the module docstring's STEP 4
    section. Checking the ordering here, not just the exit code, is the whole
    point of this class: a regression that reverts the ordering would still
    pass a test that only asserts `stdout == ""`.
    """

    def _run_main_with_document(self, document: dict) -> tuple[int, str, str]:
        stdout, stderr = io.StringIO(), io.StringIO()
        with mock.patch.object(sys, "stdin", io.StringIO(json.dumps(document))), \
             contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            exit_code = run_adjudication.main([])
        return exit_code, stdout.getvalue(), stderr.getvalue()

    def test_two_reports_with_different_nonces_exits_nonzero_no_document(self):
        doc = make_document(
            reports=[make_report(dimension="a", nonce="N1"), make_report(dimension="b", nonce="N2")],
            nonce=NONCE,
        )
        exit_code, stdout, stderr = self._run_main_with_document(doc)
        self.assertNotEqual(exit_code, 0)
        self.assertEqual(stdout, "")
        self.assertIn("mixed document", stderr, stderr)

    def test_reports_agreeing_but_not_top_level_exits_nonzero_no_document(self):
        doc = make_document(
            reports=[make_report(dimension="a", nonce="N1"), make_report(dimension="b", nonce="N1")],
            nonce=NONCE,
        )
        exit_code, stdout, stderr = self._run_main_with_document(doc)
        self.assertNotEqual(exit_code, 0)
        self.assertEqual(stdout, "")
        self.assertIn("mismatched envelope", stderr, stderr)
        self.assertNotIn("mixed document", stderr, stderr)

    def test_no_top_level_nonce_exits_nonzero_and_invents_nothing(self):
        doc = make_document(reports=[make_report(nonce=NONCE)], nonce=NONCE)
        del doc["nonce"]
        exit_code, stdout, stderr = self._run_main_with_document(doc)
        self.assertNotEqual(exit_code, 0)
        self.assertEqual(stdout, "")  # nothing printed means no nonce was invented
        self.assertIn("absent provenance", stderr, stderr)

    def test_report_with_no_marker_exits_nonzero_and_never_reports_complete(self):
        report = make_report(nonce=NONCE)
        del report["completion_marker"]
        doc = make_document(reports=[report], nonce=NONCE)
        exit_code, stdout, stderr = self._run_main_with_document(doc)
        self.assertNotEqual(exit_code, 0)
        # No document at all is printed, so no stage status is ever emitted --
        # "complete" in particular is never among them.
        self.assertEqual(stdout, "")
        self.assertIn("absent provenance", stderr, stderr)


class MalformedReportsDefersToFindingsValidateTests(unittest.TestCase):
    """A `reports`-shape defect (missing, non-list, empty) is not a nonce
    problem -- `_verify_nonce` would call it "absent provenance", which
    buries `findings.validate`'s more specific, more useful message. These
    three shapes must all defer to that message instead.
    """

    def _run_main_with_document(self, document: dict) -> tuple[int, str, str]:
        stdout, stderr = io.StringIO(), io.StringIO()
        with mock.patch.object(sys, "stdin", io.StringIO(json.dumps(document))), \
             contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            exit_code = run_adjudication.main([])
        return exit_code, stdout.getvalue(), stderr.getvalue()

    def test_missing_reports_key_names_the_missing_key_not_provenance(self):
        doc = make_document(reports=[make_report(nonce=NONCE)], nonce=NONCE)
        del doc["reports"]
        exit_code, stdout, stderr = self._run_main_with_document(doc)
        self.assertNotEqual(exit_code, 0)
        self.assertEqual(stdout, "")
        self.assertIn("missing required key 'reports'", stderr, stderr)
        self.assertNotIn("absent provenance", stderr, stderr)

    def test_empty_reports_array_names_the_empty_array_not_provenance(self):
        doc = make_document(reports=[], nonce=NONCE)
        exit_code, stdout, stderr = self._run_main_with_document(doc)
        self.assertNotEqual(exit_code, 0)
        self.assertEqual(stdout, "")
        self.assertIn("must not be empty", stderr, stderr)
        self.assertNotIn("absent provenance", stderr, stderr)

    def test_non_list_reports_names_the_wrong_type_not_provenance(self):
        doc = make_document(reports=[make_report(nonce=NONCE)], nonce=NONCE)
        doc["reports"] = "not-a-list"
        exit_code, stdout, stderr = self._run_main_with_document(doc)
        self.assertNotEqual(exit_code, 0)
        self.assertEqual(stdout, "")
        self.assertIn("expected an array", stderr, stderr)
        self.assertNotIn("absent provenance", stderr, stderr)


class StagesManifestTests(unittest.TestCase):
    """The top-level `stages` array STEP 4 adds: every entry already on
    input, in order, plus exactly one new `adjudication` entry.
    """

    def test_happy_path_output_nonce_unchanged_and_marker_is_last_key(self):
        reports = [make_report(dimension=d, nonce=NONCE) for d in ("a", "b", "c")]
        input_doc = make_document(reports=reports, nonce=NONCE)

        output_doc = run_adjudication.adjudicate(input_doc, run_adjudication.stub_judge)

        self.assertEqual(output_doc["nonce"], NONCE)
        adjudication = output_doc["adjudication"]
        keys = list(adjudication.keys())
        self.assertEqual(keys[-1], "completion_marker")
        self.assertEqual(adjudication["completion_marker"], f"BUZZ-ADJUDICATION-COMPLETE:{NONCE}")

    def test_output_stages_carries_input_entries_plus_one_new_adjudication_entry(self):
        input_doc = make_document()
        input_doc["stages"] = [{"name": "preflight", "status": "complete", "reason": None}]

        output_doc = run_adjudication.adjudicate(input_doc, run_adjudication.stub_judge)

        self.assertEqual(
            output_doc["stages"],
            [
                {"name": "preflight", "status": "complete", "reason": None},
                {"name": "adjudication", "status": "complete", "reason": None},
            ],
        )

    def test_output_stages_is_just_the_new_entry_when_input_has_none(self):
        input_doc = make_document()
        self.assertNotIn("stages", input_doc)

        output_doc = run_adjudication.adjudicate(input_doc, run_adjudication.stub_judge)

        self.assertEqual(
            output_doc["stages"],
            [{"name": "adjudication", "status": "complete", "reason": None}],
        )

    def test_input_stages_list_is_not_mutated(self):
        input_doc = make_document()
        input_stages = [{"name": "preflight", "status": "complete", "reason": None}]
        input_doc["stages"] = input_stages

        run_adjudication.adjudicate(input_doc, run_adjudication.stub_judge)

        self.assertEqual(input_stages, [{"name": "preflight", "status": "complete", "reason": None}])


class AlreadyAdjudicatedTests(unittest.TestCase):
    """An input already carrying an `adjudication` entry in `stages` is a
    re-run against an already-adjudicated document -- refused outright,
    never silently overwritten.
    """

    def test_adjudicate_raises_and_never_calls_the_judge(self):
        input_doc = make_document()
        input_doc["stages"] = [{"name": "adjudication", "status": "complete", "reason": None}]
        judge = CountingJudge()

        with self.assertRaises(run_adjudication.AlreadyAdjudicatedError):
            run_adjudication.adjudicate(input_doc, judge)

        self.assertEqual(judge.call_count, 0, judge.calls)

    def test_main_exits_nonzero_and_prints_no_document(self):
        input_doc = make_document()
        input_doc["stages"] = [{"name": "adjudication", "status": "complete", "reason": None}]
        stdout, stderr = io.StringIO(), io.StringIO()
        with mock.patch.object(sys, "stdin", io.StringIO(json.dumps(input_doc))), \
             contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            exit_code = run_adjudication.main([])
        self.assertNotEqual(exit_code, 0)
        self.assertEqual(stdout.getvalue(), "")
        self.assertTrue(stderr.getvalue())


class MalformedStagesShapeTests(unittest.TestCase):
    """A `stages` value that is PRESENT but not a list was treated as absent
    at both sites that read it: the re-run guard returned early, and the
    manifest builder substituted `[]`. Two consequences, and the second is
    the one that costs something:

      1. The re-run guard is bypassed -- an `adjudication` entry inside an
         object container adjudicates at exit 0 instead of being refused.
      2. Every prior entry is silently discarded. A `blocked` pre-flight
         (#116's fork-PR-secrets-withheld case) disappears and the document
         publishes as `complete`, because #119 only banners a non-`complete`
         status. That is #118's fifth criterion failing through a shape
         defect no verdict-side check looks at.

    "#117 never emits that shape" is not a defence available to this step:
    the `stages` manifest is explicitly an output #117 does NOT produce, so
    this stage cannot inherit a guarantee from it. Absent stays legal.
    """

    NON_LIST_SHAPES = (
        ({"0": {"name": "adjudication", "status": "complete", "reason": None}}, "object"),
        ("adjudication", "string"),
        (42, "int"),
        (True, "bool"),
    )

    def test_adjudicate_raises_on_every_non_list_stages_shape(self):
        for shape, label in self.NON_LIST_SHAPES:
            with self.subTest(shape=label):
                input_doc = make_document()
                input_doc["stages"] = shape
                judge = CountingJudge()
                with self.assertRaises(run_adjudication.StagesShapeError):
                    run_adjudication.adjudicate(input_doc, judge)
                # Refused before any finding is adjudicated, like every other
                # input-shape refusal in this module.
                self.assertEqual(judge.call_count, 0, judge.calls)

    def test_the_re_run_guard_is_not_bypassed_by_an_object_container(self):
        """The bypass itself: before the fix this adjudicated at exit 0."""
        input_doc = make_document()
        input_doc["stages"] = {"0": {"name": "adjudication", "status": "complete", "reason": None}}
        with self.assertRaises(run_adjudication.StagesShapeError):
            run_adjudication.adjudicate(input_doc, run_adjudication.stub_judge)

    def test_a_blocked_preflight_is_never_silently_discarded(self):
        """The expensive half. A `blocked` pre-flight inside a non-list
        container used to vanish, and the document published `complete`.
        """
        input_doc = make_document()
        input_doc["stages"] = {
            "p": {"name": "preflight", "status": "blocked", "reason": "fork PR, secrets withheld"}
        }
        with self.assertRaises(run_adjudication.StagesShapeError):
            run_adjudication.adjudicate(input_doc, run_adjudication.stub_judge)

    def test_a_stages_entry_that_is_not_an_object_is_refused(self):
        input_doc = make_document()
        input_doc["stages"] = ["preflight"]
        with self.assertRaises(run_adjudication.StagesShapeError):
            run_adjudication.adjudicate(input_doc, run_adjudication.stub_judge)

    def test_a_stages_entry_with_a_non_string_name_is_refused(self):
        """The Low that rides along: a non-string `name` cannot impersonate an
        `adjudication` entry, so the re-run guard is not bypassed this way --
        but an off-shape entry reaching #119 is still not something to pass
        through in silence.
        """
        input_doc = make_document()
        input_doc["stages"] = [{"name": {"nested": "adjudication"}, "status": "complete"}]
        with self.assertRaises(run_adjudication.StagesShapeError):
            run_adjudication.adjudicate(input_doc, run_adjudication.stub_judge)

    def test_absent_stages_is_still_legal(self):
        """The control. #117 emits no `stages` key at all, so absent must stay
        the normal case -- a fix that refused absence would break every real
        document.
        """
        input_doc = make_document()
        self.assertNotIn("stages", input_doc)
        output_doc = run_adjudication.adjudicate(input_doc, run_adjudication.stub_judge)
        self.assertEqual([e["name"] for e in output_doc["stages"]], ["adjudication"])

    def test_explicit_null_stages_is_treated_as_absent(self):
        input_doc = make_document()
        input_doc["stages"] = None
        output_doc = run_adjudication.adjudicate(input_doc, run_adjudication.stub_judge)
        self.assertEqual([e["name"] for e in output_doc["stages"]], ["adjudication"])

    def test_a_well_formed_preflight_entry_still_survives_in_order(self):
        """The other control: the shape this step is meant to carry forward
        must still be carried forward, in order, untouched.
        """
        input_doc = make_document()
        input_doc["stages"] = [
            {"name": "preflight", "status": "blocked", "reason": "fork PR, secrets withheld"}
        ]
        output_doc = run_adjudication.adjudicate(input_doc, run_adjudication.stub_judge)
        self.assertEqual([e["name"] for e in output_doc["stages"]], ["preflight", "adjudication"])
        self.assertEqual(output_doc["stages"][0]["status"], "blocked")

    def test_main_exits_nonzero_and_prints_no_document(self):
        for shape, label in self.NON_LIST_SHAPES:
            with self.subTest(shape=label):
                input_doc = make_document()
                input_doc["stages"] = shape
                stdout, stderr = io.StringIO(), io.StringIO()
                with mock.patch.object(sys, "stdin", io.StringIO(json.dumps(input_doc))), \
                     contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                    exit_code = run_adjudication.main([])
                self.assertNotEqual(exit_code, 0)
                self.assertEqual(stdout.getvalue(), "")
                self.assertTrue(stderr.getvalue())

    def test_real_process_refuses_an_object_container(self):
        """Through the real process, the way the defect was found."""
        input_doc = make_document()
        input_doc["stages"] = {"0": {"name": "adjudication", "status": "complete", "reason": None}}
        proc = subprocess.run(
            [sys.executable, str(SCRIPT)],
            input=json.dumps(input_doc),
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertNotEqual(proc.returncode, 0)
        self.assertEqual(proc.stdout, "")
        self.assertIn("stages", proc.stderr)


class PublishIncompleteRuleTests(unittest.TestCase):
    """#119's own rule -- "any status other than 'complete' is incomplete
    and banners the whole review" -- run here as an assertion against the
    output, since #119's own code does not exist to run against (STEP 4's
    own done-when names this explicitly).
    """

    def test_happy_path_stage_status_is_complete_so_119_would_not_banner_it(self):
        input_doc = make_document()

        output_doc = run_adjudication.adjudicate(input_doc, run_adjudication.stub_judge)

        adjudication_stage = next(
            entry for entry in output_doc["stages"] if entry["name"] == "adjudication"
        )
        # #119's stated rule, applied directly: only "complete" reads as
        # complete: anything else -- any other string -- banners the review.
        self.assertEqual(adjudication_stage["status"], "complete")
        self.assertIsNone(adjudication_stage["reason"])


def _make_judge(verdict="CONFIRMED", **overrides):
    """A judge returning ``verdict`` (default CONFIRMED) plus whatever keys
    ``overrides`` supplies -- used throughout STEP 6's tests to inject a
    judge that re-rates, refuses, or refutes without hand-writing a callable
    per test.
    """

    def _judge(finding: dict, document: dict) -> dict:
        result = {"verdict": verdict, "verdict_evidence": "judge examined it directly"}
        result.update(overrides)
        return result

    return _judge


class JudgeCannotMutateWhatItIsJudgingTests(unittest.TestCase):
    """The escalate-only guard is enforced on what the judge RETURNS, so the
    judge must not be handed the object those checks are about.

    Found by a cross-model (Codex) review on 2026-08-24, after four same-model
    passes over the same code did not raise it. Before the fix, `adjudicate()`
    called the judge with the live output finding and read `reported_severity`
    back out of it AFTERWARDS, so a judge could rewrite the finding in place
    and route around every guard at once: three input `Blocker`s came out
    `Low`, `reported_severity` recorded `Low` (falsifying the record of what
    was reported), `downgrades` stayed empty, and `verdicts.validate` reported
    no violations.

    A judge is injected Python, not model output, so this needs a hostile or
    buggy judge implementation rather than a prompt injection -- but STEP 6's
    premise is that the prohibitions hold in code regardless of what the judge
    does, and a guard the guarded component can step around is not one.
    """

    @staticmethod
    def _mutating_judge(finding: dict, document: dict) -> dict:
        finding["severity"] = "Low"
        finding["finding_id"] = "0" * 16
        finding["defect"] = "rewritten by the judge"
        return {"verdict": "REFUTED", "verdict_evidence": "claimed refutation"}

    def test_in_place_severity_edit_does_not_reach_the_output(self):
        finding = make_raw_finding(severity="Blocker")
        input_doc = make_document(reports=[make_report(findings_list=[finding])])

        output_doc = run_adjudication.adjudicate(input_doc, self._mutating_judge)

        adjudicated = output_doc["reports"][0]["findings"][0]
        self.assertEqual(adjudicated["severity"], "Blocker")
        self.assertEqual(adjudicated["reported_severity"], "Blocker")
        self.assertIsNone(adjudicated["severity_reason"])
        self.assertEqual(output_doc["adjudication"]["downgrades"], [])

    def test_in_place_identity_edits_do_not_reach_the_output(self):
        # finding_id is what the input/output set-equality check is keyed on,
        # so an in-place edit here would defeat that check too.
        finding = make_raw_finding(severity="Blocker")
        original_id = finding["finding_id"]
        original_defect = finding["defect"]
        input_doc = make_document(reports=[make_report(findings_list=[finding])])

        output_doc = run_adjudication.adjudicate(input_doc, self._mutating_judge)

        adjudicated = output_doc["reports"][0]["findings"][0]
        self.assertEqual(adjudicated["finding_id"], original_id)
        self.assertEqual(adjudicated["defect"], original_defect)

    def test_the_verdict_itself_is_still_honoured(self):
        # Guards the guard: copying the finding must not stop a judge doing its
        # actual job. REFUTED is a verdict, not an approval -- refusing to let a
        # judge edit the finding is not refusing its conclusion.
        finding = make_raw_finding(severity="Blocker")
        input_doc = make_document(reports=[make_report(findings_list=[finding])])

        output_doc = run_adjudication.adjudicate(input_doc, self._mutating_judge)

        adjudicated = output_doc["reports"][0]["findings"][0]
        self.assertEqual(adjudicated["verdict"], "REFUTED")
        self.assertEqual(output_doc["adjudication"]["verdict_counts"]["REFUTED"], 1)

    def test_dedupe_judge_cannot_mutate_decided_findings(self):
        # By the time the dedupe judge runs, every finding already carries its
        # final verdict and severity, and nothing re-reads them afterwards.
        finding = make_raw_finding(severity="Blocker")
        input_doc = make_document(reports=[make_report(findings_list=[finding])])

        def mutating_dedupe(adjudicated_findings, document):
            for item in adjudicated_findings:
                item["severity"] = "Info"
                item["verdict"] = "CONFIRMED"
            return []

        output_doc = run_adjudication.adjudicate(
            input_doc, _make_judge(verdict="UNPROVEN"), dedupe_judge=mutating_dedupe
        )

        adjudicated = output_doc["reports"][0]["findings"][0]
        self.assertEqual(adjudicated["severity"], "Blocker")
        self.assertEqual(adjudicated["verdict"], "UNPROVEN")


class UnusableSeverityReasonFailsClosedTests(unittest.TestCase):
    """A judge-supplied `severity_reason` gets the same type discipline as
    `verdict`, `verdict_evidence` and `severity`.

    Also from the cross-model (Codex) pass on 2026-08-24. Forwarded unchecked,
    a non-string reason reached the output verbatim: a judge returning
    `severity_reason={"approved": True}` produced a document carrying a
    forbidden `approved` key in both the finding and its downgrade record.
    `verdicts.validate` does catch that -- 9 violations -- but `main()` never
    calls it, so the CLI printed the document and exited 0.

    This module's own rule for the finding-set integrity check applies: "a
    stage that can print a lossy document and rely on a downstream
    verdicts.validate call to catch it has already lost the document once."
    """

    def _adjudicate_with(self, ret):
        finding = make_raw_finding(severity="Blocker")
        input_doc = make_document(reports=[make_report(findings_list=[finding])])
        output_doc = run_adjudication.adjudicate(input_doc, lambda f, d: dict(ret))
        return input_doc, output_doc, output_doc["reports"][0]["findings"][0]

    def test_non_string_reason_fails_closed_on_the_rerating_too(self):
        _, output_doc, adjudicated = self._adjudicate_with(
            {
                "verdict": "REFUTED",
                "verdict_evidence": "x",
                "severity": "Low",
                "severity_reason": {"approved": True},
            }
        )
        # The re-rating is refused, not applied-with-a-dropped-reason: a
        # severity change with no usable reason is what the contract forbids.
        self.assertEqual(adjudicated["severity"], "Blocker")
        self.assertEqual(adjudicated["reported_severity"], "Blocker")
        self.assertIsNone(adjudicated["severity_reason"])
        self.assertEqual(output_doc["adjudication"]["downgrades"], [])

    def test_no_forbidden_key_survives_into_the_document(self):
        input_doc, output_doc, _ = self._adjudicate_with(
            {
                "verdict": "REFUTED",
                "verdict_evidence": "x",
                "severity": "Low",
                "severity_reason": {"approved": True},
            }
        )
        # The property that actually matters, asserted against the contract
        # checker rather than by inspecting fields one at a time.
        self.assertEqual(verdicts.validate(input_doc, output_doc), [])
        self.assertNotIn("approved", json.dumps(output_doc))

    def test_blank_reason_fails_closed(self):
        # Whitespace-only, the same "blank not empty" distinction
        # _run_judge_safely already makes for verdict_evidence.
        _, _, adjudicated = self._adjudicate_with(
            {
                "verdict": "REFUTED",
                "verdict_evidence": "x",
                "severity": "Low",
                "severity_reason": "   ",
            }
        )
        self.assertEqual(adjudicated["severity"], "Blocker")
        self.assertIsNone(adjudicated["severity_reason"])

    def test_a_legal_rerating_with_a_usable_reason_still_applies(self):
        # Guards the guard: failing closed must not swallow the legitimate case.
        _, _, adjudicated = self._adjudicate_with(
            {
                "verdict": "CONFIRMED",
                "verdict_evidence": "x",
                "severity": "High",
                "severity_reason": "narrower than reported",
            }
        )
        self.assertEqual(adjudicated["severity"], "High")
        self.assertEqual(adjudicated["reported_severity"], "Blocker")
        self.assertEqual(adjudicated["severity_reason"], "narrower than reported")


class SeverityRerateTests(unittest.TestCase):
    """STEP 6's severity re-rating guard: legal re-ratings (both directions),
    illegal ones (refused), and the no-op case, all against `adjudicate()`
    directly.
    """

    def test_no_severity_key_is_unchanged_from_step_3_4(self):
        finding = make_raw_finding(severity="High")
        input_doc = make_document(reports=[make_report(findings_list=[finding])])

        output_doc = run_adjudication.adjudicate(input_doc, _make_judge())

        adjudicated = output_doc["reports"][0]["findings"][0]
        self.assertEqual(adjudicated["severity"], "High")
        self.assertEqual(adjudicated["reported_severity"], "High")
        self.assertIsNone(adjudicated["severity_reason"])
        self.assertEqual(output_doc["adjudication"]["downgrades"], [])

    def test_severity_equal_to_reported_is_treated_as_no_rerating(self):
        finding = make_raw_finding(severity="High")
        input_doc = make_document(reports=[make_report(findings_list=[finding])])

        output_doc = run_adjudication.adjudicate(input_doc, _make_judge(severity="High"))

        adjudicated = output_doc["reports"][0]["findings"][0]
        self.assertEqual(adjudicated["severity"], "High")
        self.assertIsNone(adjudicated["severity_reason"])
        self.assertEqual(output_doc["adjudication"]["downgrades"], [])

    def test_legal_downgrade_blocker_to_low_is_recorded_with_reason(self):
        finding = make_raw_finding(severity="Blocker")
        input_doc = make_document(reports=[make_report(findings_list=[finding])])
        fid = finding["finding_id"]

        output_doc = run_adjudication.adjudicate(
            input_doc,
            _make_judge(severity="Low", severity_reason="on inspection this is cosmetic"),
        )

        adjudicated = output_doc["reports"][0]["findings"][0]
        self.assertEqual(adjudicated["reported_severity"], "Blocker")
        self.assertEqual(adjudicated["severity"], "Low")
        self.assertEqual(adjudicated["severity_reason"], "on inspection this is cosmetic")
        self.assertEqual(
            output_doc["adjudication"]["downgrades"],
            [
                {
                    "finding_id": fid,
                    "from": "Blocker",
                    "to": "Low",
                    "reason": "on inspection this is cosmetic",
                }
            ],
        )
        self.assertEqual(verdicts.validate(input_doc, output_doc), [])

    def test_downgrade_with_no_judge_reason_gets_a_generated_default(self):
        finding = make_raw_finding(severity="Blocker")
        input_doc = make_document(reports=[make_report(findings_list=[finding])])

        output_doc = run_adjudication.adjudicate(input_doc, _make_judge(severity="Low"))

        adjudicated = output_doc["reports"][0]["findings"][0]
        self.assertTrue(adjudicated["severity_reason"])
        self.assertEqual(len(output_doc["adjudication"]["downgrades"]), 1)
        self.assertEqual(output_doc["adjudication"]["downgrades"][0]["reason"], adjudicated["severity_reason"])
        self.assertEqual(verdicts.validate(input_doc, output_doc), [])

    def test_legal_upgrade_is_not_a_downgrade_but_still_needs_a_reason(self):
        finding = make_raw_finding(severity="Low")
        input_doc = make_document(reports=[make_report(findings_list=[finding])])

        output_doc = run_adjudication.adjudicate(
            input_doc, _make_judge(severity="Blocker", severity_reason="worse than reported")
        )

        adjudicated = output_doc["reports"][0]["findings"][0]
        self.assertEqual(adjudicated["reported_severity"], "Low")
        self.assertEqual(adjudicated["severity"], "Blocker")
        self.assertEqual(adjudicated["severity_reason"], "worse than reported")
        self.assertEqual(output_doc["adjudication"]["downgrades"], [])
        self.assertEqual(verdicts.validate(input_doc, output_doc), [])

    def test_illegal_severity_over_legal_reported_severity_is_unproven_at_reported(self):
        # The scenario STEP 6's own done-when names precisely: a judge
        # re-rates a LEGALLY in-ladder reported_severity to an out-of-ladder
        # value. STEP 3's input validation does not catch this -- the input
        # was legal -- only this stage's own re-rating guard does.
        finding = make_raw_finding(severity="Medium")
        input_doc = make_document(reports=[make_report(findings_list=[finding])])

        output_doc = run_adjudication.adjudicate(
            input_doc, _make_judge(verdict="CONFIRMED", severity="Info")
        )

        adjudicated = output_doc["reports"][0]["findings"][0]
        self.assertEqual(adjudicated["verdict"], "UNPROVEN")
        self.assertEqual(adjudicated["reported_severity"], "Medium")
        self.assertEqual(adjudicated["severity"], "Medium")
        self.assertTrue(adjudicated["severity_reason"])
        self.assertIn("Info", adjudicated["severity_reason"])
        self.assertEqual(output_doc["adjudication"]["downgrades"], [])
        self.assertEqual(verdicts.validate(input_doc, output_doc), [])
        # The positive form, used bare on purpose: #119's own `.get(sev, 9)`
        # default would silently mask an out-of-ladder emission here.
        for report in output_doc["reports"]:
            for f in report["findings"]:
                review.SEVERITY_ORDER[f["severity"]]

    def test_illegal_severity_is_never_added_to_downgrades(self):
        finding = make_raw_finding(severity="High")
        input_doc = make_document(reports=[make_report(findings_list=[finding])])

        output_doc = run_adjudication.adjudicate(input_doc, _make_judge(severity="Info"))

        self.assertEqual(output_doc["adjudication"]["downgrades"], [])

    def test_unhashable_severity_fails_closed_instead_of_crashing(self):
        # A judge (or a malformed --replay recording) returning a severity
        # that isn't even a string -- a list or dict -- must fail closed the
        # same as any other unusable output, never raise TypeError from
        # `proposed_severity not in review.SEVERITY_ORDER`'s `in` check.
        finding = make_raw_finding(severity="High")
        input_doc = make_document(reports=[make_report(findings_list=[finding])])

        for bad_severity in (["Blocker"], {"value": "Blocker"}):
            with self.subTest(bad_severity=bad_severity):
                output_doc = run_adjudication.adjudicate(
                    input_doc, _make_judge(severity=bad_severity)
                )
                adjudicated = output_doc["reports"][0]["findings"][0]
                self.assertEqual(adjudicated["severity"], "High")
                self.assertEqual(adjudicated["reported_severity"], "High")
                self.assertEqual(output_doc["adjudication"]["downgrades"], [])
                self.assertEqual(verdicts.validate(input_doc, output_doc), [])

    def test_out_of_ladder_reported_severity_is_refused_even_when_agreed_with(self):
        # STEP 6's own done-when: "a guard watching only re-ratings never sees
        # a finding that ARRIVED at 'Info' and was agreed with, and copies it
        # into `severity` untouched." Asserted against
        # `_apply_severity_rerating` directly, because `main()` cannot reach
        # this shape -- STEP 3's findings.validate refuses an out-of-ladder
        # input severity before any judge runs -- so a document-level fixture
        # would test STEP 3's gate instead of this guard.
        #
        # Both sub-cases produce the same effective severity, which is the
        # point: agreement and silence are the same thing to this branch.
        for proposed in ("Info", None):
            with self.subTest(proposed=proposed):
                downgrades: list[dict] = []
                verdict, severity, reason = run_adjudication._apply_severity_rerating(
                    "fid", "Info", "CONFIRMED", proposed, None, downgrades
                )
                self.assertEqual(verdict, "UNPROVEN")
                # Blocker, not something smaller: this stage may not decide an
                # unrateable finding is a minor one.
                self.assertEqual(severity, "Blocker")
                self.assertIn("Info", reason)
                self.assertTrue(reason)
                # Nothing legally fell -- the value was refused, not compared.
                self.assertEqual(downgrades, [])

    def test_legal_reported_severity_is_untouched_when_agreed_with(self):
        # The control for the guard above: a LEGAL reported severity the judge
        # agrees with (or says nothing about) must still pass through
        # unchanged, with no reason and no verdict override. Without this, the
        # guard above could pass by refusing everything.
        for proposed in ("High", None):
            with self.subTest(proposed=proposed):
                downgrades: list[dict] = []
                verdict, severity, reason = run_adjudication._apply_severity_rerating(
                    "fid", "High", "CONFIRMED", proposed, None, downgrades
                )
                self.assertEqual((verdict, severity, reason), ("CONFIRMED", "High", None))
                self.assertEqual(downgrades, [])


class BareSeverityOrderSubscriptTests(unittest.TestCase):
    """The positive form of the out-of-ladder guard, run over every finding
    in a document containing every re-rating shape at once: a bare
    `review.SEVERITY_ORDER[f["severity"]]` subscript must succeed for all of
    them. Bare on purpose -- #119 defends itself with `.get(severity, 9)`,
    and a control borrowing that default would pass on exactly the output
    this stage must not emit.
    """

    def test_bare_subscript_succeeds_for_every_finding_across_every_rerating_shape(self):
        no_rerate = make_raw_finding(dimension="a", severity="Medium")
        downgraded = make_raw_finding(dimension="b", severity="Blocker")
        upgraded = make_raw_finding(dimension="c", severity="Low")
        refused = make_raw_finding(dimension="d", severity="High")
        report = make_report(
            dimension="mixed",
            findings_list=[no_rerate, downgraded, upgraded, refused],
        )
        input_doc = make_document(reports=[report])

        def judge(finding: dict, document: dict) -> dict:
            by_id = {
                no_rerate["finding_id"]: {},
                downgraded["finding_id"]: {"severity": "Low"},
                upgraded["finding_id"]: {"severity": "Blocker"},
                refused["finding_id"]: {"severity": "Info"},
            }
            extra = by_id[finding["finding_id"]]
            result = {"verdict": "CONFIRMED", "verdict_evidence": "checked"}
            result.update(extra)
            if "severity" in extra and extra["severity"] in review.SEVERITY_ORDER:
                result["severity_reason"] = "re-rated for this test"
            return result

        output_doc = run_adjudication.adjudicate(input_doc, judge)

        for r in output_doc["reports"]:
            for f in r["findings"]:
                review.SEVERITY_ORDER[f["severity"]]  # must not raise

        self.assertEqual(verdicts.validate(input_doc, output_doc), [])
        self.assertEqual(len(output_doc["adjudication"]["downgrades"]), 1)
        self.assertEqual(output_doc["adjudication"]["downgrades"][0]["finding_id"], downgraded["finding_id"])


class TotalRefutationStatusTests(unittest.TestCase):
    """STEP 6's total-refutation status: the `stages` adjudication entry
    reports `"total_refutation"` (never "complete") when every finding is
    REFUTED, and the zero-findings case is never flagged.
    """

    def test_every_finding_refuted_is_flagged_and_stage_status_is_not_complete(self):
        findings_list = [
            make_raw_finding(dimension="a"),
            make_raw_finding(dimension="b"),
        ]
        report = make_report(dimension="mixed", findings_list=findings_list)
        input_doc = make_document(reports=[report])

        output_doc = run_adjudication.adjudicate(input_doc, _make_judge(verdict="REFUTED"))

        self.assertEqual(
            [f["finding_id"] for f in output_doc["reports"][0]["findings"]],
            [f["finding_id"] for f in findings_list],
        )
        self.assertEqual(output_doc["reports"][0]["findings_count"], 2)
        self.assertTrue(output_doc["adjudication"]["total_refutation"])
        adjudication_stage = next(
            entry for entry in output_doc["stages"] if entry["name"] == "adjudication"
        )
        self.assertNotEqual(adjudication_stage["status"], "complete")
        self.assertEqual(adjudication_stage["status"], "total_refutation")
        self.assertTrue(adjudication_stage["reason"])
        self.assertEqual(verdicts.validate(input_doc, output_doc), [])

    def test_zero_findings_is_not_total_refutation_and_stage_is_complete(self):
        report = make_report(dimension="clean", findings_list=[])
        input_doc = make_document(reports=[report])

        output_doc = run_adjudication.adjudicate(input_doc, _make_judge(verdict="REFUTED"))

        self.assertFalse(output_doc["adjudication"]["total_refutation"])
        adjudication_stage = next(
            entry for entry in output_doc["stages"] if entry["name"] == "adjudication"
        )
        self.assertEqual(adjudication_stage["status"], "complete")
        self.assertEqual(verdicts.validate(input_doc, output_doc), [])


class NothingRemovedAssertionTests(unittest.TestCase):
    """STEP 6's "nothing is removed" reassertion inside `adjudicate()`
    itself -- proven here by monkeypatching `_collect_finding_ids` to lie
    about the output set, since the function does not otherwise ever drop or
    invent a finding_id by construction. This is deliberately a whitebox
    test of a belt-and-braces check that has no other way to fail.
    """

    def test_a_finding_id_mismatch_raises_before_returning(self):
        input_doc = make_document()
        real_collect = run_adjudication._collect_finding_ids
        calls = {"n": 0}

        def lying_collect(document: dict) -> set[str]:
            calls["n"] += 1
            ids = real_collect(document)
            # Lie only on the SECOND call (the output-document call) so the
            # input-side call still reflects the truth, matching what a real
            # drop/invent defect would look like.
            if calls["n"] == 2:
                return ids | {"invented-id-not-really-present"}
            return ids

        with mock.patch.object(run_adjudication, "_collect_finding_ids", lying_collect):
            with self.assertRaises(run_adjudication.FindingSetIntegrityError):
                run_adjudication.adjudicate(input_doc, run_adjudication.stub_judge)


def _pairing_dedupe_judge(fid_a: str, fid_b: str):
    """A ``dedupe_judge`` that always reports exactly one group: ``fid_a``
    and ``fid_b`` are the same defect. Used throughout ``DedupeTests`` in
    place of a real cross-finding dedupe mechanism -- STEP 7's own harness
    is what is under test, not any particular mechanism (see
    ``run_adjudication``'s module docstring, STEP 7 section, for why the
    mechanism is a separate, injectable callable at all).
    """

    def _dedupe(adjudicated_findings: list, document: dict) -> list:
        return [[fid_a, fid_b]]

    return _dedupe


class DedupeTests(unittest.TestCase):
    """STEP 7's own done-when, in full: two findings from two dimensions
    describing one planted defect, both emitted with their own verdict and
    exactly one carrying `duplicate_of`; `duplicate_groups` naming both;
    survivor determinism proven by byte-comparing two runs; `verdicts.
    validate` already rejecting a `duplicate_of` naming an absent id or
    itself (STEP 2's validator, confirmed here rather than reimplemented);
    and the empty-not-missing `duplicate_groups` key on a run that dedupes
    nothing.
    """

    def _two_dimension_document(self, severity="High") -> tuple[dict, str, str]:
        """Two findings, two different dimensions, describing one planted
        defect in different words -- different `finding_id`s by
        construction, since `dimension` is one of `finding_id`'s hash
        inputs. Returns ``(input_doc, finding_id_a, finding_id_b)``.
        """
        finding_a = make_raw_finding(
            dimension="secrets-and-access",
            defect="hardcoded credential in connection string",
            severity=severity,
        )
        finding_b = make_raw_finding(
            dimension="access-control",
            defect="database password embedded directly in source",
            severity=severity,
        )
        input_doc = make_document(
            reports=[
                make_report(dimension="secrets-and-access", findings_list=[finding_a]),
                make_report(dimension="access-control", findings_list=[finding_b]),
            ]
        )
        return input_doc, finding_a["finding_id"], finding_b["finding_id"]

    def test_both_findings_present_with_their_own_verdict_and_grouped(self):
        input_doc, fid_a, fid_b = self._two_dimension_document()

        output_doc = run_adjudication.adjudicate(
            input_doc, _make_judge(verdict="CONFIRMED"), dedupe_judge=_pairing_dedupe_judge(fid_a, fid_b)
        )

        all_findings = [f for r in output_doc["reports"] for f in r["findings"]]
        self.assertEqual({f["finding_id"] for f in all_findings}, {fid_a, fid_b})
        for f in all_findings:
            self.assertEqual(f["verdict"], "CONFIRMED")

        # Equal severity and verdict on both sides -- the tiebreaker is the
        # lowest finding_id, per ADJUDICATION.md § Dedupe.
        survivor, duplicate = sorted([fid_a, fid_b])
        by_id = {f["finding_id"]: f for f in all_findings}
        self.assertIsNone(by_id[survivor]["duplicate_of"])
        self.assertEqual(by_id[duplicate]["duplicate_of"], survivor)

        self.assertEqual(
            output_doc["adjudication"]["duplicate_groups"],
            [{"survivor": survivor, "duplicates": [duplicate]}],
        )
        self.assertEqual(output_doc["adjudication"]["findings_out"], 2)
        self.assertEqual(verdicts.validate(input_doc, output_doc), [])
        self.assertEqual(findings.validate(output_doc), [])

    def test_dedupe_judge_sees_the_adjudicated_findings_not_the_raw_ones(self):
        # The dedupe judge is called ONCE, after every finding already has
        # its final verdict/severity -- never once per finding like `Judge`.
        input_doc, fid_a, fid_b = self._two_dimension_document()
        seen: list[list[dict]] = []

        def _recording_dedupe(adjudicated_findings, document):
            seen.append(adjudicated_findings)
            return []

        run_adjudication.adjudicate(
            input_doc, _make_judge(verdict="CONFIRMED"), dedupe_judge=_recording_dedupe
        )

        self.assertEqual(len(seen), 1, "dedupe_judge must be called exactly once")
        (adjudicated_findings,) = seen
        self.assertEqual(len(adjudicated_findings), 2)
        for f in adjudicated_findings:
            self.assertIn("verdict", f)
            self.assertIn("severity", f)

    def test_survivor_prefers_highest_severity(self):
        finding_a = make_raw_finding(dimension="a", defect="one defect", severity="Medium")
        finding_b = make_raw_finding(dimension="b", defect="same defect worded differently", severity="Blocker")
        input_doc = make_document(
            reports=[
                make_report(dimension="a", findings_list=[finding_a]),
                make_report(dimension="b", findings_list=[finding_b]),
            ]
        )
        fid_a, fid_b = finding_a["finding_id"], finding_b["finding_id"]

        output_doc = run_adjudication.adjudicate(
            input_doc, _make_judge(verdict="CONFIRMED"), dedupe_judge=_pairing_dedupe_judge(fid_a, fid_b)
        )

        [group] = output_doc["adjudication"]["duplicate_groups"]
        self.assertEqual(group["survivor"], fid_b, "the Blocker finding must survive over the Medium one")
        self.assertEqual(verdicts.validate(input_doc, output_doc), [])

    def test_survivor_prefers_confirmed_over_unproven_over_refuted(self):
        finding_a = make_raw_finding(dimension="a", defect="one defect", severity="High")
        finding_b = make_raw_finding(dimension="b", defect="same defect worded differently", severity="High")
        input_doc = make_document(
            reports=[
                make_report(dimension="a", findings_list=[finding_a]),
                make_report(dimension="b", findings_list=[finding_b]),
            ]
        )
        fid_a, fid_b = finding_a["finding_id"], finding_b["finding_id"]

        def judge(finding: dict, document: dict) -> dict:
            verdict = "UNPROVEN" if finding["finding_id"] == fid_a else "CONFIRMED"
            return {"verdict": verdict, "verdict_evidence": "checked independently"}

        output_doc = run_adjudication.adjudicate(
            input_doc, judge, dedupe_judge=_pairing_dedupe_judge(fid_a, fid_b)
        )

        [group] = output_doc["adjudication"]["duplicate_groups"]
        self.assertEqual(group["survivor"], fid_b, "CONFIRMED must survive over UNPROVEN at equal severity")
        self.assertEqual(verdicts.validate(input_doc, output_doc), [])

    def test_survivor_is_the_same_across_two_runs_byte_for_byte(self):
        input_doc, fid_a, fid_b = self._two_dimension_document()

        output_1 = run_adjudication.adjudicate(
            input_doc, _make_judge(verdict="CONFIRMED"), dedupe_judge=_pairing_dedupe_judge(fid_a, fid_b)
        )
        output_2 = run_adjudication.adjudicate(
            input_doc, _make_judge(verdict="CONFIRMED"), dedupe_judge=_pairing_dedupe_judge(fid_a, fid_b)
        )

        self.assertEqual(
            json.dumps(output_1, sort_keys=True),
            json.dumps(output_2, sort_keys=True),
            "two runs of the same input must agree on the same survivor, byte for byte",
        )

    def test_dedupe_judge_raising_fails_closed_to_no_duplicates(self):
        input_doc, fid_a, fid_b = self._two_dimension_document()

        def _raising_dedupe(adjudicated_findings, document):
            raise RuntimeError("boom")

        output_doc = run_adjudication.adjudicate(
            input_doc, _make_judge(verdict="CONFIRMED"), dedupe_judge=_raising_dedupe
        )

        self.assertEqual(output_doc["adjudication"]["duplicate_groups"], [])
        for f in [f for r in output_doc["reports"] for f in r["findings"]]:
            self.assertIsNone(f["duplicate_of"])
        self.assertEqual(verdicts.validate(input_doc, output_doc), [])

    def test_dedupe_judge_returning_garbage_is_dropped_not_raised(self):
        input_doc, fid_a, fid_b = self._two_dimension_document()

        def _garbage_dedupe(adjudicated_findings, document):
            return [
                "not-a-list",  # a group that is not a list at all
                [fid_a],  # too few real ids to be a group
                [fid_a, "unknown-finding-id-not-in-document"],  # references an absent id
                123,  # not even a list-shaped entry
            ]

        output_doc = run_adjudication.adjudicate(
            input_doc, _make_judge(verdict="CONFIRMED"), dedupe_judge=_garbage_dedupe
        )

        self.assertEqual(output_doc["adjudication"]["duplicate_groups"], [])
        for f in [f for r in output_doc["reports"] for f in r["findings"]]:
            self.assertIsNone(f["duplicate_of"])
        self.assertEqual(verdicts.validate(input_doc, output_doc), [])

    def test_default_dedupe_judge_finds_no_duplicates_and_key_is_present_not_missing(self):
        input_doc = make_document()

        output_doc = run_adjudication.adjudicate(input_doc, run_adjudication.stub_judge)

        self.assertIn("duplicate_groups", output_doc["adjudication"])
        self.assertEqual(output_doc["adjudication"]["duplicate_groups"], [])
        self.assertEqual(verdicts.validate(input_doc, output_doc), [])

    def test_stub_dedupe_judge_directly_returns_no_groups(self):
        finding = make_raw_finding()
        self.assertEqual(run_adjudication.stub_dedupe_judge([finding], {}), [])

    def test_duplicate_of_naming_an_absent_id_is_rejected_by_validate(self):
        # STEP 2's validator, confirmed here rather than reimplemented.
        finding = make_raw_finding()
        input_doc = make_document(reports=[make_report(findings_list=[finding])])
        output_doc = run_adjudication.adjudicate(input_doc, run_adjudication.stub_judge)

        output_doc["reports"][0]["findings"][0]["duplicate_of"] = "not-a-real-finding-id"

        violations = verdicts.validate(input_doc, output_doc)
        self.assertTrue(
            any("is not a finding_id present in the document" in v for v in violations), violations
        )

    def test_duplicate_of_naming_itself_is_rejected_by_validate(self):
        # STEP 2's validator, confirmed here rather than reimplemented.
        finding = make_raw_finding()
        input_doc = make_document(reports=[make_report(findings_list=[finding])])
        output_doc = run_adjudication.adjudicate(input_doc, run_adjudication.stub_judge)

        fid = output_doc["reports"][0]["findings"][0]["finding_id"]
        output_doc["reports"][0]["findings"][0]["duplicate_of"] = fid

        violations = verdicts.validate(input_doc, output_doc)
        self.assertTrue(any("names itself" in v for v in violations), violations)


if __name__ == "__main__":
    unittest.main()
