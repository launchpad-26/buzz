#!/usr/bin/env python3
"""Controls for #118 STEP 8: the four documents under fixtures/adjudication/.

STEP 8's plan text originally said every fixture here would be "synthesised, not
recorded" because #117 did not exist when the plan was written. #117 is now fully
merged (PR #252) and 15 real recorded reviewer outputs live under recordings/, so this
suite checks the corrected reality instead: four of the five behaviours STEP 8 names
are genuinely produced by replaying that real recorded output through the real
run_dimensions.build_document; the fifth (all three containment kinds at once) has no
real recording to replay, so its surfaces are crafted and only the containment output
built from them is real. See fixtures/adjudication/PROVENANCE.md for the full
accounting; this file is the executable half of that claim.

A permanent, committed witness, the same convention test_fixtures.py and
test_recordings.py already established for #117's own STEP 7/STEP 8 fixtures.

Not wired into run_controls.py -- that list is #120's own containment-control suite;
this file is scoped to #118's STEP 8 fixtures alone, the same reasoning
test_fixtures.py's own docstring gives for staying off that list.

Run:  python3 -m unittest test_adjudication_fixtures    (from launchpad/review-agent/)
  or: python3 test_adjudication_fixtures.py
"""

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import unittest

import contain
import findings
import verdicts

HERE = os.path.dirname(os.path.abspath(__file__))
FIXTURES_DIR = os.path.join(HERE, "fixtures", "adjudication")
SCRIPT = os.path.join(HERE, "run_adjudication.py")
PROVENANCE_NOTE = os.path.join(FIXTURES_DIR, "PROVENANCE.md")

# fixtures/adjudication/ is a fixtures directory, not a package (no
# __init__.py, deliberately -- matching fixtures/dimensions/), so generate.py
# is loaded by file path rather than by a dotted import.
_spec = importlib.util.spec_from_file_location(
    "adjudication_fixtures_generate", os.path.join(FIXTURES_DIR, "generate.py")
)
generate = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(generate)

DOCUMENT_FILES = tuple(generate.BUILDERS.keys())

CONTAINMENT_KINDS = frozenset({"delimiter_forge", "delimiter_lookalike", "injection_attempt"})

# The five behaviours STEP 8 names, and the fragment each document's own
# `_fixture.isolates` field must contain. "line-anchored-findings.json" carries
# two fragments because the real replay that produces it genuinely has both
# properties at once -- see PROVENANCE.md for why this is one document, not two.
EXPECTED_BEHAVIOUR_FRAGMENTS = {
    "line-anchored-findings.json": [
        "three reports, one finding per dimension, all anchor 'line'",
        "two dimensions describing ONE defect",
    ],
    "pr-anchored-finding.json": ["pr-anchored finding"],
    "containment-all-kinds.json": ["all three containment kinds"],
    "mixed-report-statuses.json": [
        "one failed report, one clean report, one report with findings"
    ],
}


def _load(filename: str) -> dict:
    with open(os.path.join(FIXTURES_DIR, filename), encoding="utf-8") as handle:
        return json.load(handle)


class FixtureFilesExistTests(unittest.TestCase):
    def test_exactly_four_documents_exist_on_disk(self):
        # containment-crafted-payload.json is generate.py's INPUT (a crafted PR
        # payload, fed through fetch.from_payload), not one of the four merged
        # documents this suite validates against run_adjudication.py -- excluded
        # by name rather than by counting every *.json, so a future generator
        # input file does not silently inflate this count.
        on_disk = sorted(
            f
            for f in os.listdir(FIXTURES_DIR)
            if f.endswith(".json") and f != "containment-crafted-payload.json"
        )
        self.assertEqual(on_disk, sorted(DOCUMENT_FILES))

    def test_every_document_parses_as_json(self):
        for filename in DOCUMENT_FILES:
            with self.subTest(filename=filename):
                self.assertIsInstance(_load(filename), dict)

    def test_provenance_note_exists(self):
        self.assertTrue(os.path.isfile(PROVENANCE_NOTE), PROVENANCE_NOTE)


class HeaderNamesBehaviourAndProvenanceTests(unittest.TestCase):
    def test_every_document_names_which_behaviour_it_isolates(self):
        for filename, fragments in EXPECTED_BEHAVIOUR_FRAGMENTS.items():
            with self.subTest(filename=filename):
                doc = _load(filename)
                self.assertIn("_fixture", doc)
                isolates = doc["_fixture"].get("isolates")
                self.assertIsInstance(isolates, list)
                self.assertTrue(isolates)
                joined = " ".join(isolates)
                for fragment in fragments:
                    self.assertIn(fragment, joined)

    def test_every_document_names_its_provenance(self):
        for filename in DOCUMENT_FILES:
            with self.subTest(filename=filename):
                fixture_meta = _load(filename)["_fixture"]
                self.assertIsInstance(fixture_meta.get("provenance"), str)
                self.assertTrue(fixture_meta["provenance"])
                self.assertIsInstance(fixture_meta.get("real"), bool)

    def test_exactly_one_document_is_not_real(self):
        # containment-all-kinds.json alone -- crafted surfaces run through the
        # real pipeline. Every other document replays a real #117 recording
        # end to end, with no hand-written finding content.
        not_real = [f for f in DOCUMENT_FILES if _load(f)["_fixture"]["real"] is False]
        self.assertEqual(not_real, ["containment-all-kinds.json"])


class FindingsValidateTests(unittest.TestCase):
    def test_every_document_passes_findings_validate_with_zero_violations(self):
        for filename in DOCUMENT_FILES:
            with self.subTest(filename=filename):
                self.assertEqual(findings.validate(_load(filename)), [])


class RunAdjudicationCliTests(unittest.TestCase):
    """The literal CLI form: `python3 run_adjudication.py < fixture.json` --
    the same real-process pattern test_run_adjudication.py's own
    SubprocessInvocationTests uses, run here against every STEP 8 document
    rather than a hand-built minimal one.
    """

    def test_every_document_is_a_valid_input_to_run_adjudication(self):
        for filename in DOCUMENT_FILES:
            with self.subTest(filename=filename):
                input_doc = _load(filename)
                proc = subprocess.run(
                    [sys.executable, SCRIPT],
                    input=json.dumps(input_doc),
                    capture_output=True,
                    text=True,
                    cwd=HERE,
                    timeout=30,
                )
                self.assertEqual(proc.returncode, 0, proc.stderr)
                output_doc = json.loads(proc.stdout)
                self.assertEqual(verdicts.validate(input_doc, output_doc), [])
                self.assertEqual(findings.validate(output_doc), [])


class LineAnchoredFindingsFixtureTests(unittest.TestCase):
    """Behaviour-specific checks for line-anchored-findings.json -- both of
    its named behaviours at once, per its own header.
    """

    def test_three_reports_one_finding_each_all_anchor_line(self):
        doc = _load("line-anchored-findings.json")
        self.assertEqual(len(doc["reports"]), 3)
        for report in doc["reports"]:
            self.assertEqual(report["findings_count"], 1)
            finding = report["findings"][0]
            self.assertEqual(finding["anchor"], "line")
            self.assertEqual(finding["severity"], "Blocker")

    def test_all_three_findings_describe_the_same_defect_at_the_same_location(self):
        doc = _load("line-anchored-findings.json")
        findings_list = [r["findings"][0] for r in doc["reports"]]
        locations = {(f["file"], f["line"]) for f in findings_list}
        defects = {f["defect"] for f in findings_list}
        self.assertEqual(len(locations), 1, f"expected one shared location, got {locations}")
        self.assertEqual(len(defects), 1, f"expected one shared defect text, got {defects}")
        # finding_id differs across the three -- `dimension` is a hash input,
        # per ADJUDICATION.md's own Dedupe section -- so this genuinely
        # exercises adjudicate()'s dedupe path (three distinct ids describing
        # one defect) rather than three identical ids.
        ids = {f["finding_id"] for f in findings_list}
        self.assertEqual(len(ids), 3)


class PrAnchoredFindingFixtureTests(unittest.TestCase):
    def test_claim_vs_evidence_report_carries_a_line_and_a_pr_anchored_finding(self):
        doc = _load("pr-anchored-finding.json")
        [claim_report] = [r for r in doc["reports"] if r["dimension"] == "claim-vs-evidence"]
        anchors = sorted(f["anchor"] for f in claim_report["findings"])
        self.assertEqual(anchors, ["line", "pr"])
        [pr_finding] = [f for f in claim_report["findings"] if f["anchor"] == "pr"]
        self.assertIsNone(pr_finding["file"])
        self.assertIsNone(pr_finding["line"])

    def test_other_two_dimensions_are_clean(self):
        doc = _load("pr-anchored-finding.json")
        for report in doc["reports"]:
            if report["dimension"] != "claim-vs-evidence":
                with self.subTest(dimension=report["dimension"]):
                    self.assertEqual(report["outcome"], "clean")
                    self.assertEqual(report["findings"], [])


class ContainmentAllKindsFixtureTests(unittest.TestCase):
    def test_states_map_has_exactly_seven_keys_matching_entry_points(self):
        doc = _load("containment-all-kinds.json")
        states = doc["containment"]["states"]
        self.assertEqual(set(states.keys()), set(contain.ENTRY_POINTS))
        self.assertEqual(len(states), 7)

    def test_containment_findings_cover_all_three_kinds(self):
        doc = _load("containment-all-kinds.json")
        kinds = {f["kind"] for f in doc["containment"]["findings"]}
        self.assertEqual(kinds, set(CONTAINMENT_KINDS))

    def test_zero_dimension_findings(self):
        doc = _load("containment-all-kinds.json")
        self.assertEqual(len(doc["reports"]), 3)
        for report in doc["reports"]:
            with self.subTest(dimension=report["dimension"]):
                self.assertEqual(report["outcome"], "clean")
                self.assertEqual(report["findings"], [])


class MixedReportStatusesFixtureTests(unittest.TestCase):
    def test_one_failed_one_clean_one_findings(self):
        doc = _load("mixed-report-statuses.json")
        statuses = sorted(r["status"] for r in doc["reports"])
        self.assertEqual(statuses, ["complete", "complete", "failed"])
        outcomes = sorted(r["outcome"] for r in doc["reports"] if r["status"] == "complete")
        self.assertEqual(outcomes, ["clean", "findings"])

    def test_failed_report_carries_a_real_error_reason_not_a_placeholder(self):
        doc = _load("mixed-report-statuses.json")
        [failed] = [r for r in doc["reports"] if r["status"] == "failed"]
        self.assertIsNone(failed["outcome"])
        self.assertIsInstance(failed["error"], dict)
        # The reason string comes from the real exception _collect_report
        # caught, not a hand-written placeholder -- "raised" is
        # run_dimensions._collect_report's own wording for that branch.
        self.assertIn("raised", failed["error"]["reason"])


class RegenerationReproducesCommittedBytesTests(unittest.TestCase):
    """PROVENANCE.md's provenance claims are checkable, not merely asserted,
    only if regenerating actually reproduces the committed bytes. This is
    that check -- run generate.py's own build functions again and compare
    against the file already on disk, with no I/O side effects of its own.
    """

    def test_generate_render_matches_committed_file_byte_for_byte(self):
        for filename in DOCUMENT_FILES:
            with self.subTest(filename=filename):
                rendered = generate.render(filename)
                with open(os.path.join(FIXTURES_DIR, filename), encoding="utf-8") as handle:
                    committed = handle.read()
                self.assertEqual(rendered, committed)


if __name__ == "__main__":
    unittest.main()
