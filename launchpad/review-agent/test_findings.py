#!/usr/bin/env python3
"""Controls for findings.py -- issue #117 STEP 2's output contract in code.

Three prior fix rounds against this module (673f04091, 44175da78, 8bd3d2116,
and this round's follow-up) were verified with throwaway scripts that were
deleted before each commit. A final-branch review flagged that as a real gap:
nobody after the fact could reproduce what "verified" meant, and one review
pass itself could not confirm the claims without re-deriving the fixtures from
scratch. This file is the fix -- a permanent, committed witness for every case
verified across all four rounds, runnable by anyone, not just quoted in a PR
description.

STEP 9 (#117) still owns the eventual multi-file control suite this repository
will run in CI (alongside #120's own `check_stepN.py` controls, which this file
does not touch or duplicate). This file is scoped to `findings.py` alone, and
is deliberately not wired into `run_controls.py`'s CONTROLS list or `make test`
-- that list is #120's own containment-control suite (see its module docstring:
"every containment control"), and a `findings.py` regression showing up inside
it would land as a second, unrelated-looking entry next to the pre-existing
`check_step6.py` corpus failure, muddying the "one known failure" story that
failure already has. `python3 -m unittest test_findings` (or `python3
test_findings.py`) run directly is a real, path-invoked suite in its own right.

Run:  python3 -m unittest test_findings    (from launchpad/review-agent/)
  or: python3 test_findings.py
"""

from __future__ import annotations

import unittest

import contain
import findings
import review

NONCE = "deadbeefcafef00d"


def make_states(omit: str | None = None):
    states = {ep: "ok" for ep in contain.ENTRY_POINTS}
    if omit is not None:
        del states[omit]
    return states


def make_finding(**overrides):
    """A well-formed finding dict, with a correctly recomputed finding_id.

    Passing ``finding_id`` explicitly in ``overrides`` skips the recompute, for
    tests that need a deliberately wrong one.
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


def make_document(reports=None, nonce=NONCE, states=None, containment_findings=None):
    reports = reports if reports is not None else [make_report(findings_list=[make_finding()])]
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


class SharedSeverityTests(unittest.TestCase):
    def test_severity_order_is_the_same_object_as_reviews(self):
        self.assertIs(findings.SEVERITY_ORDER, review.SEVERITY_ORDER)


class WellFormedDocumentTests(unittest.TestCase):
    def test_well_formed_document_validates_clean(self):
        self.assertEqual(findings.validate(make_document()), [])

    def test_three_simultaneous_defects_all_surface(self):
        doc = make_document()
        doc["nonce"] = ""
        doc["reports"][0]["dimension"] = "containment"
        doc["containment"]["states"] = make_states(omit=contain.ENTRY_POINTS[0])
        violations = findings.validate(doc)
        self.assertGreaterEqual(len(violations), 3, violations)


class AnchorValidationTests(unittest.TestCase):
    def test_anchor_pr_with_non_null_file_is_rejected(self):
        doc = make_document(
            reports=[make_report(findings_list=[make_finding(anchor="pr", file="x.rs", line=None)])]
        )
        violations = findings.validate(doc)
        self.assertTrue(any("anchor 'pr'" in v and "file" in v for v in violations), violations)

    def test_anchor_line_with_null_line_is_rejected(self):
        doc = make_document(
            reports=[make_report(findings_list=[make_finding(anchor="line", file="x.rs", line=None)])]
        )
        violations = findings.validate(doc)
        self.assertTrue(any("anchor 'line'" in v and "line" in v for v in violations), violations)

    def test_anchor_file_with_non_null_line_is_rejected(self):
        doc = make_document(
            reports=[make_report(findings_list=[make_finding(anchor="file", file="x.rs", line=7)])]
        )
        violations = findings.validate(doc)
        self.assertTrue(any("anchor 'file'" in v and "line" in v for v in violations), violations)


class SeverityValidationTests(unittest.TestCase):
    def test_severity_not_in_the_ladder_is_rejected(self):
        doc = make_document(
            reports=[make_report(findings_list=[make_finding(severity="Critical")])]
        )
        violations = findings.validate(doc)
        self.assertTrue(any("SEVERITY_ORDER" in v for v in violations), violations)

    def test_unhashable_severity_is_rejected_not_crashed(self):
        doc = make_document(reports=[make_report(findings_list=[make_finding(severity={})])])
        violations = findings.validate(doc)  # must not raise TypeError
        self.assertTrue(
            any("severity must be a string" in v and "dict" in v for v in violations), violations
        )

    def test_unhashable_severity_list_is_rejected_not_crashed(self):
        doc = make_document(reports=[make_report(findings_list=[make_finding(severity=[1, 2])])])
        violations = findings.validate(doc)  # must not raise TypeError
        self.assertTrue(
            any("severity must be a string" in v and "list" in v for v in violations), violations
        )


class EntryPointEvidenceTests(unittest.TestCase):
    def test_entry_point_set_with_no_evidence_is_rejected(self):
        doc = make_document(
            reports=[
                make_report(
                    findings_list=[
                        make_finding(anchor="pr", file=None, line=None, entry_point="pr_body", evidence=None)
                    ]
                )
            ]
        )
        violations = findings.validate(doc)
        self.assertTrue(
            any("evidence" in v and "entry_point is set" in v for v in violations), violations
        )

    def test_evidence_set_with_no_entry_point_is_rejected(self):
        doc = make_document(
            reports=[
                make_report(
                    findings_list=[
                        make_finding(anchor="pr", file=None, line=None, entry_point=None, evidence="excerpt")
                    ]
                )
            ]
        )
        violations = findings.validate(doc)
        self.assertTrue(any("evidence must be null" in v for v in violations), violations)

    def test_unhashable_entry_point_dict_is_rejected_not_crashed(self):
        doc = make_document(
            reports=[
                make_report(
                    findings_list=[
                        make_finding(anchor="pr", file=None, line=None, entry_point={}, evidence="x")
                    ]
                )
            ]
        )
        violations = findings.validate(doc)  # must not raise TypeError
        self.assertTrue(
            any("entry_point must be a string or null" in v and "dict" in v for v in violations),
            violations,
        )

    def test_unhashable_entry_point_list_is_rejected_not_crashed(self):
        doc = make_document(
            reports=[
                make_report(
                    findings_list=[
                        make_finding(anchor="pr", file=None, line=None, entry_point=[1, 2], evidence="x")
                    ]
                )
            ]
        )
        violations = findings.validate(doc)  # must not raise TypeError
        self.assertTrue(
            any("entry_point must be a string or null" in v and "list" in v for v in violations),
            violations,
        )


class DimensionAndFindingIdTests(unittest.TestCase):
    def test_finding_missing_dimension_is_rejected(self):
        finding = make_finding()
        del finding["dimension"]
        doc = make_document(reports=[make_report(findings_list=[finding])])
        violations = findings.validate(doc)
        self.assertTrue(any("dimension must be a non-empty string" in v for v in violations), violations)

    def test_finding_empty_dimension_is_rejected(self):
        doc = make_document(reports=[make_report(findings_list=[make_finding(dimension="")])])
        violations = findings.validate(doc)
        self.assertTrue(any("dimension must be a non-empty string" in v for v in violations), violations)

    def test_finding_missing_finding_id_is_rejected(self):
        finding = make_finding()
        del finding["finding_id"]
        doc = make_document(reports=[make_report(findings_list=[finding])])
        violations = findings.validate(doc)
        self.assertTrue(any("finding_id must be a non-empty string" in v for v in violations), violations)

    def test_finding_id_not_matching_its_own_fields_is_rejected(self):
        doc = make_document(
            reports=[make_report(findings_list=[make_finding(finding_id="not-the-real-hash")])]
        )
        violations = findings.validate(doc)
        self.assertTrue(
            any("does not match the id recomputed" in v for v in violations), violations
        )

    def test_finding_id_recomputed_correctly_matches_and_produces_no_violation(self):
        # make_finding() itself calls findings.finding_id(...) for its default --
        # this proves that recompute is exercised on the well-formed path too,
        # not only on the deliberately-wrong-id path above.
        doc = make_document()
        self.assertEqual(findings.validate(doc), [])


class ContainmentBlockTests(unittest.TestCase):
    def test_six_of_seven_states_is_rejected(self):
        doc = make_document(states=make_states(omit=contain.ENTRY_POINTS[0]))
        violations = findings.validate(doc)
        self.assertTrue(any("containment.states" in v for v in violations), violations)

    def test_non_dict_containment_is_rejected_not_crashed(self):
        doc = make_document()
        doc["containment"] = ["not", "a", "dict"]
        violations = findings.validate(doc)  # must not raise
        self.assertTrue(any("document.containment: expected an object" in v for v in violations), violations)

    def test_non_dict_containment_finding_entry_is_rejected_not_crashed(self):
        doc = make_document(containment_findings=["not an object"])
        violations = findings.validate(doc)  # must not raise
        self.assertTrue(
            any("document.containment.findings[0]: expected an object" in v for v in violations),
            violations,
        )

    def test_containment_finding_kind_outside_the_three_values_is_rejected(self):
        doc = make_document(
            containment_findings=[
                {"kind": "not_a_real_kind", "entry_point": "pr_body", "evidence": "x", "severity": "Blocker"}
            ]
        )
        violations = findings.validate(doc)
        self.assertTrue(any("kind" in v and "not_a_real_kind" in v for v in violations), violations)

    def test_unhashable_containment_finding_kind_is_rejected_not_crashed(self):
        doc = make_document(
            containment_findings=[{"kind": {}, "entry_point": "pr_body", "evidence": "x", "severity": "Blocker"}]
        )
        violations = findings.validate(doc)  # must not raise TypeError
        self.assertTrue(
            any("kind must be a string" in v and "dict" in v for v in violations), violations
        )


class ReportEnvelopeTests(unittest.TestCase):
    def test_dimension_slug_containment_is_rejected(self):
        doc = make_document(reports=[make_report(dimension="containment", findings_list=[])])
        violations = findings.validate(doc)
        self.assertTrue(any("reserved slug 'containment'" in v for v in violations), violations)

    def test_report_missing_dimension_is_rejected(self):
        doc = make_document(reports=[make_report(findings_list=[])])
        del doc["reports"][0]["dimension"]
        violations = findings.validate(doc)
        self.assertTrue(any("missing required key 'dimension'" in v for v in violations), violations)

    def test_report_missing_envelope_fields_is_rejected(self):
        doc = make_document(reports=[make_report(findings_list=[])])
        for key in ("schema_version", "pr", "merge_base_sha", "head_sha"):
            del doc["reports"][0][key]
        violations = findings.validate(doc)
        for key in ("schema_version", "pr", "merge_base_sha", "head_sha"):
            self.assertTrue(any(f"missing required key '{key}'" in v for v in violations), (key, violations))

    def test_findings_null_is_rejected_not_crashed(self):
        doc = make_document(reports=[make_report(findings_list=[])])
        doc["reports"][0]["findings"] = None
        violations = findings.validate(doc)  # must not raise TypeError
        self.assertTrue(any("findings must be an array" in v for v in violations), violations)

    def test_outcome_invalid_enum_value_is_rejected(self):
        doc = make_document(
            reports=[make_report(status="complete", outcome="banana", findings_list=[])]
        )
        violations = findings.validate(doc)
        self.assertTrue(
            any("outcome must be 'clean' or 'findings'" in v and "'banana'" in v for v in violations),
            violations,
        )

    def test_outcome_clean_with_findings_present_is_rejected(self):
        doc = make_document(
            reports=[make_report(status="complete", outcome="clean", findings_list=[make_finding()])]
        )
        violations = findings.validate(doc)
        self.assertTrue(
            any("outcome 'clean' requires an empty findings array" in v for v in violations), violations
        )

    def test_outcome_findings_with_no_findings_is_rejected(self):
        doc = make_document(
            reports=[make_report(status="complete", outcome="findings", findings_list=[])]
        )
        violations = findings.validate(doc)
        self.assertTrue(
            any("outcome 'findings' requires a non-empty findings array" in v for v in violations),
            violations,
        )

    def test_finding_entry_that_is_not_an_object_is_rejected_not_crashed(self):
        doc = make_document(reports=[make_report(findings_list=["not a finding object"])])
        violations = findings.validate(doc)  # must not raise
        self.assertTrue(any("finding[0]: expected an object" in v for v in violations), violations)


class MergedDocumentTests(unittest.TestCase):
    def test_no_top_level_nonce_is_rejected(self):
        doc = make_document()
        del doc["nonce"]
        doc["reports"][0]["completion_marker"] = f"BUZZ-DIMENSION-COMPLETE:secrets-and-access:{NONCE}"
        violations = findings.validate(doc)
        self.assertTrue(any("missing or empty top-level 'nonce'" in v for v in violations), violations)

    def test_document_missing_required_keys_is_rejected(self):
        doc = make_document()
        for key in ("pr", "merge_base_sha", "head_sha", "reports"):
            del doc[key]
        violations = findings.validate(doc)
        for key in ("pr", "merge_base_sha", "head_sha", "reports"):
            self.assertTrue(any(f"document: missing required key '{key}'" in v for v in violations), (key, violations))

    def test_empty_reports_array_is_rejected(self):
        doc = make_document(reports=[])
        violations = findings.validate(doc)
        self.assertTrue(any("document.reports: must not be empty" in v for v in violations), violations)

    def test_non_list_reports_is_rejected_not_crashed(self):
        doc = make_document()
        doc["reports"] = {"not": "a list"}
        violations = findings.validate(doc)  # must not raise
        self.assertTrue(any("document.reports: expected an array" in v for v in violations), violations)

    def test_one_bad_report_is_named_and_its_clean_sibling_stays_silent(self):
        good_report = make_report(dimension="secrets-and-access", nonce=NONCE, findings_list=[])
        bad_report = make_report(dimension="ux-and-docs", nonce="WRONG-NONCE-VALUE", findings_list=[])
        # A second, independent defect planted on the SAME bad report -- proves
        # both violations were reached, not that the loop stopped after the first
        # and the sibling was simply never validated.
        del bad_report["pr"]
        doc = make_document(reports=[good_report, bad_report], nonce=NONCE)
        violations = findings.validate(doc)
        bad_hits = [v for v in violations if "ux-and-docs" in v]
        good_hits = [v for v in violations if "secrets-and-access" in v]
        self.assertTrue(any("completion_marker nonce does not match" in v for v in bad_hits), violations)
        self.assertTrue(any("missing required key 'pr'" in v for v in bad_hits), violations)
        self.assertEqual(good_hits, [], "sibling report must produce zero violations of its own")


if __name__ == "__main__":
    unittest.main(verbosity=2)
