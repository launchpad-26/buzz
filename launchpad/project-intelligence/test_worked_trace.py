"""Controls for worked_trace.py's citation audit -- issue #211.

The trace itself is a live run against real buzz-core data, evidenced in the PR
body (it needs `rql`). The audit is testable here because it only reads files.

Run:  python3 -m unittest test_worked_trace
  or: python3 test_worked_trace.py
"""

from __future__ import annotations

import unittest

from answer import Answer, Claim
from worked_trace import audit_citations

REAL_FILE = "crates/buzz-core/src/kind.rs"
REAL_LINE = 219
REAL_SIGNATURE = "pub fn is_shared_gated_kind(kind: u32) -> bool"


class AuditTest(unittest.TestCase):
    def test_a_supported_citation_passes(self) -> None:
        answer = Answer(
            question="q?",
            claims=(
                Claim(
                    statement=f"is_shared_gated_kind is defined as {REAL_SIGNATURE}",
                    entry_class="FACT",
                    evidence=(f"{REAL_FILE}:{REAL_LINE}-{REAL_LINE + 2}",),
                ),
            ),
        )
        checks, unparsed = audit_citations(answer)
        self.assertEqual(unparsed, [])
        self.assertEqual(len(checks), 1)
        self.assertTrue(checks[0].supported)

    def test_a_citation_that_resolves_but_names_the_wrong_subject_fails(self) -> None:
        """STEP 3's defect as a permanent control at the audit level: the range
        is real and readable, and simply does not contain the subject."""
        answer = Answer(
            question="q?",
            claims=(
                Claim(
                    statement="shared_gated_kinds_membership asserts the exclusions",
                    entry_class="FACT",
                    evidence=(f"{REAL_FILE}:{REAL_LINE}-{REAL_LINE + 2}",),
                ),
            ),
        )
        checks, _ = audit_citations(answer)
        self.assertFalse(checks[0].supported)
        self.assertIn("none of", checks[0].note)

    def test_an_unreadable_path_fails_rather_than_being_skipped(self) -> None:
        answer = Answer(
            question="q?",
            claims=(
                Claim(
                    statement="some_symbol_name does a thing",
                    entry_class="FACT",
                    evidence=("no/such/file.rs:1-2",),
                ),
            ),
        )
        checks, unparsed = audit_citations(answer)
        self.assertEqual(unparsed, [])
        self.assertFalse(checks[0].supported)
        self.assertIn("unreadable", checks[0].note)

    def test_a_non_file_citation_is_reported_unparsed_not_counted_as_verified(self) -> None:
        """A checker that silently skips what it does not understand reports a
        clean audit over nothing."""
        answer = Answer(
            question="q?",
            claims=(
                Claim(
                    statement="two callers exist",
                    entry_class="FACT",
                    evidence=("tested_by edge a -> b (Symbol.tests[])",),
                ),
            ),
        )
        checks, unparsed = audit_citations(answer)
        self.assertEqual(checks, [])
        self.assertEqual(len(unparsed), 1)

    def test_a_single_line_citation_is_parsed_as_well_as_a_range(self) -> None:
        answer = Answer(
            question="q?",
            claims=(
                Claim(
                    statement="is_shared_gated_kind is the gate",
                    entry_class="FACT",
                    evidence=(f"{REAL_FILE}:{REAL_LINE}",),
                ),
            ),
        )
        checks, unparsed = audit_citations(answer)
        self.assertEqual(unparsed, [])
        self.assertTrue(checks[0].supported)

    def test_a_prose_only_claim_is_not_failed_for_having_no_identifier(self) -> None:
        """"is a decision point rather than a transformation" will never appear
        in source. Demanding it would fail every honest inference."""
        answer = Answer(
            question="q?",
            claims=(
                Claim(
                    statement="this is a decision point rather than a change",
                    entry_class="INFERENCE",
                    evidence=(f"{REAL_FILE}:{REAL_LINE}",),
                    confidence=0.7,
                ),
            ),
        )
        checks, _ = audit_citations(answer)
        self.assertTrue(checks[0].supported)
        self.assertIn("no identifier to check", checks[0].note)


if __name__ == "__main__":
    unittest.main()
