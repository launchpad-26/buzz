#!/usr/bin/env python3
"""Controls for verdicts.py -- issue #118 STEP 2's verdict contract in code.

Exercises every behaviour named in STEP 2's own done-when list in
launchpad/plans/2026-08-13-issue-118-adjudication.md, plus the shared-object
guarantee (`verdicts.SEVERITY_ORDER is review.SEVERITY_ORDER`) and the
re-run of #117's own `findings.validate` against the output document.

This file is scoped to `verdicts.py` alone and is deliberately not wired into
`run_controls.py`'s CONTROLS list -- that is STEP 10's control suite, over the
full adjudication surface (`run_adjudication.py` included), not this module in
isolation. `python3 -m unittest test_verdicts` (or `python3 test_verdicts.py`)
run directly is a real, path-invoked suite in its own right.

Run:  python3 -m unittest test_verdicts    (from launchpad/review-agent/)
  or: python3 test_verdicts.py
"""

from __future__ import annotations

import copy
import unittest

import contain
import findings
import review
import verdicts

NONCE = "deadbeefcafef00d"


def make_states(omit: str | None = None):
    states = {ep: "ok" for ep in contain.ENTRY_POINTS}
    if omit is not None:
        del states[omit]
    return states


def make_raw_finding(**overrides):
    """A well-formed #117 finding dict -- BEFORE adjudication. None of the six
    ADJUDICATION.md fields are present, matching what #117 actually emits.
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


def make_finding(**overrides):
    """A well-formed, ALREADY-ADJUDICATED finding dict: #117's ten fields plus
    the six ADJUDICATION.md adds. ``finding_id`` is recomputed from the seven
    hash inputs, which never include ``severity`` or any of the six added
    fields -- so a re-rating never invalidates the id.
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
        verdict="CONFIRMED",
        verdict_evidence="Read the file at head_sha; the credential is present at that line.",
        reported_severity="High",
        severity_reason=None,
        duplicate_of=None,
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


def make_report(dimension="secrets-and-access", nonce=NONCE, findings_list=None, **overrides):
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


def make_document(reports=None, nonce=NONCE, states=None, containment_findings=None, adjudication=None):
    reports = reports if reports is not None else [make_report(findings_list=[make_raw_finding()])]
    doc = dict(
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
    if adjudication is not None:
        doc["adjudication"] = adjudication
    return doc


def make_adjudication(findings_list, nonce=NONCE, **overrides):
    """A well-formed `adjudication` block for exactly ``findings_list``."""
    counts = {"CONFIRMED": 0, "REFUTED": 0, "UNPROVEN": 0}
    for f in findings_list:
        counts[f["verdict"]] = counts.get(f["verdict"], 0) + 1
    block = dict(
        schema_version=1,
        verdict_counts=counts,
        findings_in=len(findings_list),
        findings_out=len(findings_list),
        duplicate_groups=[],
        downgrades=[],
        total_refutation=bool(findings_list) and all(f["verdict"] == "REFUTED" for f in findings_list),
        notes=[],
    )
    block.update(overrides)
    block["completion_marker"] = f"BUZZ-ADJUDICATION-COMPLETE:{nonce}"
    return block


def make_well_formed_pair(nonce=NONCE):
    """A matching (input_document, output_document) pair: one finding, no
    re-rating, no dedupe, nothing refuted -- the baseline every mutation test
    below starts from and breaks in exactly one way.
    """
    raw = make_raw_finding()
    verdicted = make_finding()
    assert raw["finding_id"] == verdicted["finding_id"]

    input_doc = make_document(
        reports=[make_report(findings_list=[raw], nonce=nonce)],
        nonce=nonce,
    )
    output_doc = make_document(
        reports=[make_report(findings_list=[verdicted], nonce=nonce)],
        nonce=nonce,
        adjudication=make_adjudication([verdicted], nonce=nonce),
    )
    return input_doc, output_doc


class SharedSeverityOrderTests(unittest.TestCase):
    def test_severity_order_is_the_same_object_as_review(self):
        self.assertIs(verdicts.SEVERITY_ORDER, review.SEVERITY_ORDER)


class WellFormedPairTests(unittest.TestCase):
    def test_well_formed_pair_validates_clean(self):
        input_doc, output_doc = make_well_formed_pair()
        self.assertEqual(verdicts.validate(input_doc, output_doc), [])

    def test_findings_validate_still_accepts_the_output(self):
        # STEP 2's own requirement: verdicts.validate re-runs findings.validate
        # over the output, but the output document must also pass it stood alone.
        _, output_doc = make_well_formed_pair()
        self.assertEqual(findings.validate(output_doc), [])

    def test_four_independent_violations_surface_at_once(self):
        input_doc, output_doc = make_well_formed_pair()
        # 1: verdict not one of the three legal values.
        output_doc["reports"][0]["findings"][0]["verdict"] = "APPROVED"
        # 2: verdict_evidence empty.
        output_doc["reports"][0]["findings"][0]["verdict_evidence"] = ""
        # 3: reported_severity out of the ladder.
        output_doc["reports"][0]["findings"][0]["reported_severity"] = "Info"
        # 4: a forbidden key present in the document.
        output_doc["adjudication"]["approved"] = None
        violations = verdicts.validate(input_doc, output_doc)
        self.assertGreaterEqual(len(violations), 4, violations)


class FindingIdSetTests(unittest.TestCase):
    """The two cases a mere findings_out == findings_in COUNT comparison
    cannot tell apart from a well-formed document, because both leave that
    equality true.
    """

    def test_dropped_finding_id_is_named(self):
        raw_a = make_raw_finding(defect="defect A")
        raw_b = make_raw_finding(defect="defect B")
        verdicted_a = make_finding(defect="defect A", finding_id=raw_a["finding_id"])

        input_doc = make_document(
            reports=[make_report(findings_list=[raw_a, raw_b])],
        )
        # Output drops raw_b's finding_id entirely, and its own adjudication
        # block is internally self-consistent (findings_out == findings_in == 1)
        # -- a count-only check would see nothing wrong here.
        output_doc = make_document(
            reports=[make_report(findings_list=[verdicted_a])],
            adjudication=make_adjudication([verdicted_a]),
        )
        violations = verdicts.validate(input_doc, output_doc)
        self.assertTrue(
            any(raw_b["finding_id"] in v and "missing from output" in v for v in violations),
            violations,
        )

    def test_invented_finding_id_is_named(self):
        raw_a = make_raw_finding(defect="defect A")
        verdicted_a = make_finding(defect="defect A", finding_id=raw_a["finding_id"])
        invented = make_finding(defect="defect NEVER ON INPUT", finding_id="0" * 16)

        input_doc = make_document(
            reports=[make_report(findings_list=[raw_a])],
        )
        # Output carries an extra finding absent from input, and its own
        # adjudication block is internally self-consistent (findings_out ==
        # findings_in == 2) -- a count-only check would see nothing wrong here
        # either.
        output_doc = make_document(
            reports=[make_report(findings_list=[verdicted_a, invented])],
            adjudication=make_adjudication([verdicted_a, invented]),
        )
        violations = verdicts.validate(input_doc, output_doc)
        self.assertTrue(
            any("0000000000000000" in v and "invented" in v for v in violations),
            violations,
        )


class SeverityLadderTests(unittest.TestCase):
    def test_severity_out_of_ladder_is_rejected(self):
        input_doc, output_doc = make_well_formed_pair()
        output_doc["reports"][0]["findings"][0]["severity"] = "Info"
        violations = verdicts.validate(input_doc, output_doc)
        self.assertTrue(any("severity" in v and "Info" in v for v in violations), violations)

    def test_reported_severity_out_of_ladder_is_rejected(self):
        # The case a guard watching only re-ratings never sees: the finding
        # ARRIVED broken and the judge never touched severity at all.
        input_doc, output_doc = make_well_formed_pair()
        output_doc["reports"][0]["findings"][0]["reported_severity"] = "Info"
        violations = verdicts.validate(input_doc, output_doc)
        self.assertTrue(
            any("reported_severity" in v and "Info" in v for v in violations), violations
        )


class DowngradeTests(unittest.TestCase):
    def test_a_real_fall_with_no_downgrade_entry_is_rejected(self):
        raw = make_raw_finding(severity="Blocker")
        verdicted = make_finding(severity="Low", reported_severity="Blocker", severity_reason="re-rated down")
        input_doc = make_document(reports=[make_report(findings_list=[raw])])
        output_doc = make_document(
            reports=[make_report(findings_list=[verdicted])],
            adjudication=make_adjudication([verdicted]),  # downgrades left empty
        )
        violations = verdicts.validate(input_doc, output_doc)
        self.assertTrue(
            any("severity fell" in v and "not" in v and "recorded" in v for v in violations),
            violations,
        )

    def test_a_downgrade_entry_with_no_real_fall_is_rejected(self):
        input_doc, output_doc = make_well_formed_pair()  # severity == reported_severity, no fall
        fid = output_doc["reports"][0]["findings"][0]["finding_id"]
        output_doc["adjudication"]["downgrades"] = [
            {"finding_id": fid, "from": "High", "to": "High", "reason": "not actually a fall"}
        ]
        violations = verdicts.validate(input_doc, output_doc)
        self.assertTrue(
            any("did not fall" in v or "did not actually fall" in v for v in violations)
            or any("severity did not fall" in v for v in violations),
            violations,
        )


class TotalRefutationTests(unittest.TestCase):
    def test_all_refuted_with_flag_false_is_rejected(self):
        raw = make_raw_finding()
        verdicted = make_finding(verdict="REFUTED", verdict_evidence="checked and found absent")
        input_doc = make_document(reports=[make_report(findings_list=[raw])])
        output_doc = make_document(
            reports=[make_report(findings_list=[verdicted])],
            adjudication=make_adjudication([verdicted], total_refutation=False),
        )
        violations = verdicts.validate(input_doc, output_doc)
        self.assertTrue(any("total_refutation" in v for v in violations), violations)

    def test_mixed_verdicts_with_flag_true_is_rejected(self):
        raw_a = make_raw_finding(defect="A")
        raw_b = make_raw_finding(defect="B")
        confirmed = make_finding(defect="A", finding_id=raw_a["finding_id"], verdict="CONFIRMED")
        refuted = make_finding(
            defect="B",
            finding_id=raw_b["finding_id"],
            verdict="REFUTED",
            verdict_evidence="checked and found absent",
        )
        input_doc = make_document(reports=[make_report(findings_list=[raw_a, raw_b])])
        output_doc = make_document(
            reports=[make_report(findings_list=[confirmed, refuted])],
            adjudication=make_adjudication([confirmed, refuted], total_refutation=True),
        )
        violations = verdicts.validate(input_doc, output_doc)
        self.assertTrue(any("total_refutation" in v for v in violations), violations)


class DedupeTests(unittest.TestCase):
    def test_group_naming_a_finding_whose_duplicate_of_is_null_is_rejected(self):
        raw_a = make_raw_finding(defect="A")
        raw_b = make_raw_finding(defect="B")
        survivor = make_finding(defect="A", finding_id=raw_a["finding_id"])
        # duplicate_of left null (default), but a group claims it as a duplicate.
        not_pointing_back = make_finding(defect="B", finding_id=raw_b["finding_id"], duplicate_of=None)
        input_doc = make_document(reports=[make_report(findings_list=[raw_a, raw_b])])
        adjudication = make_adjudication(
            [survivor, not_pointing_back],
            duplicate_groups=[{"survivor": survivor["finding_id"], "duplicates": [not_pointing_back["finding_id"]]}],
        )
        output_doc = make_document(
            reports=[make_report(findings_list=[survivor, not_pointing_back])],
            adjudication=adjudication,
        )
        violations = verdicts.validate(input_doc, output_doc)
        self.assertTrue(any("does not point back" in v for v in violations), violations)

    def test_finding_pointing_at_a_survivor_listed_in_no_group_is_rejected(self):
        raw_a = make_raw_finding(defect="A")
        raw_b = make_raw_finding(defect="B")
        survivor = make_finding(defect="A", finding_id=raw_a["finding_id"])
        orphaned_duplicate = make_finding(
            defect="B", finding_id=raw_b["finding_id"], duplicate_of=survivor["finding_id"]
        )
        input_doc = make_document(reports=[make_report(findings_list=[raw_a, raw_b])])
        # No duplicate_groups entry at all names this pairing.
        output_doc = make_document(
            reports=[make_report(findings_list=[survivor, orphaned_duplicate])],
            adjudication=make_adjudication([survivor, orphaned_duplicate]),
        )
        violations = verdicts.validate(input_doc, output_doc)
        self.assertTrue(
            any("no" in v and "duplicate_groups" in v and "lists this finding" in v for v in violations),
            violations,
        )


class VerdictEvidenceTests(unittest.TestCase):
    def test_refuted_with_empty_verdict_evidence_is_rejected(self):
        input_doc, output_doc = make_well_formed_pair()
        output_doc["reports"][0]["findings"][0]["verdict"] = "REFUTED"
        output_doc["reports"][0]["findings"][0]["verdict_evidence"] = ""
        violations = verdicts.validate(input_doc, output_doc)
        self.assertTrue(any("verdict_evidence" in v for v in violations), violations)


class FindingsValidateReRunTests(unittest.TestCase):
    def test_output_breaking_findings_own_contract_is_caught(self):
        # A document that leaves this stage still satisfies the contract it
        # arrived under -- here the top-level nonce is emptied, which #117's
        # own findings.validate rejects on its own terms.
        input_doc, output_doc = make_well_formed_pair()
        output_doc["nonce"] = ""
        violations = verdicts.validate(input_doc, output_doc)
        self.assertTrue(any("nonce" in v for v in violations), violations)
        # And findings.validate, run directly, agrees.
        self.assertTrue(any("nonce" in v for v in findings.validate(output_doc)))


class DeepCopyIsolationTests(unittest.TestCase):
    def test_validate_does_not_mutate_either_document(self):
        input_doc, output_doc = make_well_formed_pair()
        input_before = copy.deepcopy(input_doc)
        output_before = copy.deepcopy(output_doc)
        verdicts.validate(input_doc, output_doc)
        self.assertEqual(input_doc, input_before)
        self.assertEqual(output_doc, output_before)


if __name__ == "__main__":
    unittest.main()
