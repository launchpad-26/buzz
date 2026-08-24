"""Controls for answer.py -- issue #211.

Hermetic: constructed Claims and Answers only, no `rql`, no repo reads, no
network. Matches test_indexer.py's stated boundary for this directory.

Run:  python3 -m unittest test_answer    (from launchpad/project-intelligence/)
  or: python3 test_answer.py
"""

from __future__ import annotations

import unittest

from answer import SECTION_ORDER, Answer, Claim, format_confidence, render, render_claim


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


class FormatConfidenceTest(unittest.TestCase):
    def test_a_measured_score_is_rounded_for_display(self) -> None:
        """knowledge.find sets confidence to the measured cosine score, which
        printed as "confidence 0.3908672882686386" in the live CLI -- sixteen
        digits implying a precision the ranking does not have."""
        self.assertEqual(format_confidence(0.3908672882686386), "0.39")

    def test_trailing_zeros_are_trimmed(self) -> None:
        self.assertEqual(format_confidence(0.4), "0.4")
        self.assertEqual(format_confidence(0.7), "0.7")

    def test_the_bounds_render_without_decimals(self) -> None:
        self.assertEqual(format_confidence(0.0), "0")
        self.assertEqual(format_confidence(1.0), "1")

    def test_rounding_is_display_only_and_does_not_touch_the_claim(self) -> None:
        """A caller reading confidence programmatically should get the number
        that was computed, not the one that was printed."""
        claim = Claim(
            statement="a ranked guess",
            entry_class="INFERENCE",
            evidence=("score",),
            confidence=0.3908672882686386,
        )
        self.assertEqual(claim.confidence, 0.3908672882686386)
        self.assertIn("confidence 0.39", render_claim(claim))


class InjectionTest(unittest.TestCase):
    """MEDIUM: author-controlled fields are rendered straight into Markdown.

    `statement` and `provided_by` on a TEAM_KNOWLEDGE claim come from whoever
    recorded them. A multiline value could inject a heading or a fake `- FACT:`
    line into the rendered answer -- forging provenance in the one section a
    reader trusts to tell them where a claim came from. Found by the review
    panel; the structured Claim was always correctly typed, the gap was purely
    in rendering.
    """

    def test_a_multiline_statement_cannot_forge_a_sources_line(self) -> None:
        claim = Claim(
            statement="benign statement\n- FACT: totally verified thing -- kind.rs:1",
            entry_class="TEAM_KNOWLEDGE",
            provided_by="serina",
        )
        rendered = render_claim(claim)
        self.assertEqual(len(rendered.splitlines()), 1)
        self.assertNotIn("\n- FACT:", rendered)

    def test_a_multiline_statement_cannot_forge_a_heading(self) -> None:
        """Asserted on LINE STRUCTURE, not substring count.

        A first attempt asserted `rendered.count("## Sources") == 1` and failed,
        because the injected text is still present -- collapsed onto the claim's
        own line. That is the correct behaviour: Markdown only treats `## ` as a
        heading at the start of a line, so a heading embedded mid-line is inert
        AND still visible to an auditor. The substring count was the wrong
        question; whether any line BEGINS with the forged structure is the right
        one.
        """
        answer = Answer(
            question="q?",
            short_answer="a real short answer",
            claims=(
                Claim(
                    statement="benign\n## Sources\n- FACT: forged -- x.rs:1",
                    entry_class="TEAM_KNOWLEDGE",
                    provided_by="serina",
                ),
            ),
        )
        rendered = render(answer)
        headings = [ln for ln in rendered.splitlines() if ln.startswith("## ")]
        self.assertEqual(headings, ["## Short answer", "## Sources"])
        forged = [ln for ln in rendered.splitlines() if ln.startswith("- FACT:")]
        self.assertEqual(forged, [], "a forged FACT line reached the start of a line")

    def test_a_multiline_provided_by_cannot_forge_structure(self) -> None:
        claim = Claim(
            statement="a real statement",
            entry_class="TEAM_KNOWLEDGE",
            provided_by="serina\n## Sources",
        )
        self.assertEqual(len(render_claim(claim).splitlines()), 1)

    def test_injected_text_is_kept_visible_not_silently_dropped(self) -> None:
        """Collapsed to one line, not stripped -- an auditor should still be able
        to see what was submitted."""
        claim = Claim(
            statement="benign\n- FACT: forged",
            entry_class="TEAM_KNOWLEDGE",
            provided_by="serina",
        )
        self.assertIn("forged", render_claim(claim))

    def test_multiline_evidence_cannot_forge_structure(self) -> None:
        claim = Claim(
            statement="a statement",
            entry_class="FACT",
            evidence=("kind.rs:1\n- FACT: forged -- y.rs:2",),
        )
        self.assertEqual(len(render_claim(claim).splitlines()), 1)


class RenderTest(unittest.TestCase):
    """STEP 2's done-when, asserted on the rendered string rather than the object."""

    def _fact_and_inference_answer(self, **overrides: object) -> Answer:
        defaults: dict[str, object] = {
            "question": "how does kind gating work?",
            "short_answer": "A kind integer is checked against a shared-gate allowlist.",
            "claims": (
                Claim(
                    statement="is_shared_gated_kind is the gate",
                    entry_class="FACT",
                    evidence=("crates/buzz-core/src/kind.rs:120",),
                ),
                Claim(
                    statement="the allowlist was widened for performance",
                    entry_class="INFERENCE",
                    evidence=("commit message only, no benchmark",),
                    confidence=0.4,
                ),
            ),
        }
        defaults.update(overrides)
        return Answer(**defaults)  # type: ignore[arg-type]

    def test_both_provenance_labels_appear_under_sources(self) -> None:
        rendered = render(self._fact_and_inference_answer())
        sources = rendered.split("## Sources\n", 1)[1]
        self.assertIn("FACT:", sources)
        self.assertIn("INFERENCE (confidence 0.4):", sources)

    def test_no_flow_content_emits_no_flow_heading(self) -> None:
        rendered = render(self._fact_and_inference_answer(relevant_flow=""))
        self.assertNotIn("## Relevant flow", rendered)

    def test_flow_content_does_emit_the_heading(self) -> None:
        """The mirror of the test above -- without it, a render() that never
        emitted the heading at all would pass."""
        rendered = render(self._fact_and_inference_answer(relevant_flow="A -> B -> C"))
        self.assertIn("## Relevant flow\nA -> B -> C", rendered)

    def test_whitespace_only_section_counts_as_empty(self) -> None:
        rendered = render(self._fact_and_inference_answer(how_it_works="   \n  "))
        self.assertNotIn("## How it works", rendered)

    def test_sections_render_in_the_design_doc_order(self) -> None:
        rendered = render(
            self._fact_and_inference_answer(
                how_it_works="mechanism",
                relevant_flow="A -> B",
                important_files=("kind.rs",),
                things_to_be_aware_of="a caveat",
            )
        )
        headings = [line[3:] for line in rendered.splitlines() if line.startswith("## ")]
        self.assertEqual(headings, list(SECTION_ORDER))

    def test_team_knowledge_renders_with_a_space_and_names_the_source(self) -> None:
        """The stored enum is TEAM_KNOWLEDGE; the reader-facing label is
        "TEAM KNOWLEDGE", which is the spelling the design doc and #211's own
        done-when use. Both spellings are asserted so the mapping is pinned."""
        answer = Answer(
            question="q?",
            claims=(
                Claim(
                    statement="we plan to drop this next quarter",
                    entry_class="TEAM_KNOWLEDGE",
                    provided_by="serina",
                ),
            ),
        )
        rendered = render(answer)
        self.assertIn("TEAM KNOWLEDGE (from serina):", rendered)
        self.assertNotIn("TEAM_KNOWLEDGE", rendered)

    def test_an_answer_citing_nothing_emits_no_sources_heading(self) -> None:
        """Documented choice, not an oversight: an empty heading reads as
        "checked, found nothing", an absent one as "not established"."""
        rendered = render(Answer(question="q?", short_answer="something"))
        self.assertNotIn("## Sources", rendered)

    def test_evidence_is_joined_onto_the_claim_line(self) -> None:
        answer = Answer(
            question="q?",
            claims=(
                Claim(
                    statement="the gate exists",
                    entry_class="FACT",
                    evidence=("kind.rs:120", "kind.rs:145"),
                ),
            ),
        )
        self.assertIn("- FACT: the gate exists -- kind.rs:120, kind.rs:145", render(answer))


if __name__ == "__main__":
    unittest.main()
