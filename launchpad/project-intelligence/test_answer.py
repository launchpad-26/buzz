"""Controls for answer.py -- issue #211.

Hermetic: constructed Claims and Answers only, no `rql`, no repo reads, no
network. Matches test_indexer.py's stated boundary for this directory.

Run:  python3 -m unittest test_answer    (from launchpad/project-intelligence/)
  or: python3 test_answer.py
"""

from __future__ import annotations

import unittest

from answer import SECTION_ORDER, Answer, Claim


class ClaimProvenanceValidationTest(unittest.TestCase):
    """STEP 1's done-when: the two shapes that must raise, and why."""

    def test_inference_without_confidence_is_rejected(self) -> None:
        with self.assertRaises(ValueError) as caught:
            Claim(
                statement="the cache was added for performance reasons",
                entry_class="INFERENCE",
                evidence=("commit f4e1c9 message",),
                confidence=None,
            )
        self.assertIn("confidence is required for an INFERENCE entry", str(caught.exception))

    def test_fact_without_evidence_is_rejected(self) -> None:
        with self.assertRaises(ValueError) as caught:
            Claim(statement="the cache exists", entry_class="FACT", evidence=())
        self.assertIn("evidence is required for a FACT entry", str(caught.exception))

    def test_team_knowledge_without_provided_by_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            Claim(statement="we are dropping this pattern", entry_class="TEAM_KNOWLEDGE")

    def test_team_knowledge_needs_no_evidence(self) -> None:
        """The one class that exists precisely for uncorroborated statements."""
        claim = Claim(
            statement="we are dropping this pattern next quarter",
            entry_class="TEAM_KNOWLEDGE",
            provided_by="serina",
        )
        self.assertEqual(claim.evidence, ())

    def test_confidence_on_a_fact_is_rejected(self) -> None:
        """A FACT with a confidence score is a hedged fact -- an INFERENCE wearing
        the wrong label, which is the exact conflation this layer forbids."""
        with self.assertRaises(ValueError):
            Claim(
                statement="the cache exists",
                entry_class="FACT",
                evidence=("kind.rs:44",),
                confidence=0.9,
            )

    def test_unknown_entry_class_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            Claim(statement="something", entry_class="PROBABLY", evidence=("x",))

    def test_empty_statement_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            Claim(statement="   ", entry_class="FACT", evidence=("kind.rs:44",))

    def test_evidence_passed_as_a_list_is_normalized_to_a_tuple(self) -> None:
        """Frozen is not immutable if a caller keeps a live list reference."""
        mutable = ["kind.rs:44"]
        claim = Claim(statement="the gate exists", entry_class="FACT", evidence=mutable)
        mutable.append("kind.rs:99")
        self.assertEqual(claim.evidence, ("kind.rs:44",))

    def test_a_bare_string_is_not_exploded_into_characters(self) -> None:
        with self.assertRaises(ValueError):
            Claim(statement="the gate exists", entry_class="FACT", evidence="kind.rs:44")


class AnswerShapeTest(unittest.TestCase):
    def test_section_order_matches_the_design_doc(self) -> None:
        self.assertEqual(
            SECTION_ORDER,
            (
                "Short answer",
                "How it works",
                "Relevant flow",
                "Important files",
                "Things to be aware of",
                "Sources",
            ),
        )

    def test_sources_is_not_an_authored_field(self) -> None:
        """Guards the docstring's claim: sources derive from claims, so no
        caller can author a sources section that disagrees with them."""
        self.assertNotIn("sources", Answer.__dataclass_fields__)

    def test_claims_of_class_partitions_by_provenance(self) -> None:
        fact = Claim(statement="a", entry_class="FACT", evidence=("f:1",))
        inference = Claim(
            statement="b", entry_class="INFERENCE", evidence=("f:2",), confidence=0.6
        )
        answer = Answer(question="q?", claims=(fact, inference))
        self.assertEqual(answer.claims_of_class("FACT"), (fact,))
        self.assertEqual(answer.claims_of_class("INFERENCE"), (inference,))
        self.assertEqual(answer.claims_of_class("TEAM_KNOWLEDGE"), ())

    def test_non_claim_in_claims_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            Answer(question="q?", claims=("just a string",))

    def test_empty_question_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            Answer(question="")

    def test_important_files_as_a_bare_string_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            Answer(question="q?", important_files="kind.rs")


if __name__ == "__main__":
    unittest.main()
