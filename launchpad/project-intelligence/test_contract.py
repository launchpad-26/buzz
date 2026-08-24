"""Controls that CONTRACT.md still describes this code -- issue #553.

A contract is a document making claims about an implementation, which is exactly
the shape of claim this layer refuses to accept unverified. Five review rounds on
#211 found eighteen defects, and the single most repeated class was **prose
asserting behaviour the code did not have** -- a docstring claiming a gate that
did not exist, a module header denying one that did, a caveat overstating its own
coverage, an interface paragraph describing routing nothing performed.

CONTRACT.md is a whole document of that kind. So its factual claims are asserted
here rather than trusted: constants, signatures, enum members, schema fields and
the no-`sources`-field guarantee. Drift fails the suite instead of misleading a
reader.

What this CANNOT check is whether the prose is *right* -- whether § 7's
reconciliation is honest, or whether § 6 describes error modes a caller actually
hits. Those need a reviewer. This only holds the mechanical claims.

Hermetic: reads CONTRACT.md and introspects the modules. No `rql`, no network.

Run:  python3 -m unittest test_contract
  or: python3 test_contract.py
"""

from __future__ import annotations

import pathlib
import typing
import unittest
from dataclasses import fields

import answer
import investigation
import knowledge
import memory
import question

CONTRACT = pathlib.Path(__file__).with_name("CONTRACT.md")


class ContractExistsTest(unittest.TestCase):
    def test_the_contract_is_present_and_not_a_stub(self) -> None:
        self.assertTrue(CONTRACT.exists(), "CONTRACT.md is missing")
        self.assertGreater(len(CONTRACT.read_text()), 2000, "CONTRACT.md looks like a stub")


class ContractFactsTest(unittest.TestCase):
    """Every number and name the contract quotes must match the code."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.doc = CONTRACT.read_text()

    def test_quoted_constants_match_the_code(self) -> None:
        for literal, actual in (
            ("1e-9", knowledge.MINIMUM_CANDIDATE_SCORE),
            ("DEPENDENCY_HOPS` (2)", knowledge.DEPENDENCY_HOPS),
            ("IMPACT_DIRECT_HOPS` = 1", knowledge.IMPACT_DIRECT_HOPS),
            ("HISTORY_LINE_WINDOW` (10)", investigation.HISTORY_LINE_WINDOW),
        ):
            with self.subTest(literal=literal):
                self.assertIn(literal, self.doc)
        self.assertEqual(knowledge.MINIMUM_CANDIDATE_SCORE, 1e-9)
        self.assertEqual(knowledge.DEPENDENCY_HOPS, 2)
        self.assertEqual(knowledge.IMPACT_DIRECT_HOPS, 1)
        self.assertEqual(knowledge.IMPACT_SECONDARY_HOPS, 2)
        self.assertEqual(investigation.HISTORY_LINE_WINDOW, 10)

    def test_every_method_in_the_interface_is_documented(self) -> None:
        for name in knowledge.all_methods():
            with self.subTest(method=name):
                self.assertIn(f"`{name}(agent", self.doc, f"{name}() has no signature in the contract")

    def test_the_documented_method_count_is_the_real_one(self) -> None:
        """The contract says "the seven methods". An eighth added without
        updating it would make that sentence false."""
        self.assertEqual(len(knowledge.all_methods()), 7)
        self.assertIn("seven methods", self.doc)

    def test_ask_is_documented_as_the_eighth_entry_point(self) -> None:
        self.assertTrue(callable(knowledge.ask))
        self.assertIn("`ask(agent, text: str) -> Answer`", self.doc)

    def test_every_intent_appears_in_the_routing_table(self) -> None:
        for intent in typing.get_args(question.Intent):
            with self.subTest(intent=intent):
                self.assertIn(f"`{intent}`", self.doc)

    def test_every_setup_task_is_listed(self) -> None:
        for task in question.SETUP_TASKS:
            with self.subTest(task=task):
                self.assertIn(task, self.doc)

    def test_every_setup_source_is_listed(self) -> None:
        for source in knowledge.SETUP_SOURCES:
            with self.subTest(source=source):
                self.assertIn(source, self.doc)

    def test_every_provenance_class_is_documented(self) -> None:
        for entry_class in typing.get_args(memory.EntryClass):
            with self.subTest(entry_class=entry_class):
                self.assertIn(entry_class, self.doc)

    def test_every_temporal_state_is_documented(self) -> None:
        for state in typing.get_args(memory.TemporalState):
            with self.subTest(state=state):
                self.assertIn(state, self.doc)

    def test_every_answer_and_claim_field_is_documented(self) -> None:
        for cls in (answer.Answer, answer.Claim):
            for field in fields(cls):
                with self.subTest(cls=cls.__name__, field=field.name):
                    self.assertIn(field.name, self.doc)

    def test_every_rendered_section_is_documented(self) -> None:
        for section in answer.SECTION_ORDER:
            with self.subTest(section=section):
                self.assertIn(section, self.doc)


class ContractGuaranteesTest(unittest.TestCase):
    """Claims the contract makes about behaviour, not just about names."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.doc = CONTRACT.read_text()

    def test_answer_really_has_no_sources_field(self) -> None:
        """The contract states this as a guarantee a consumer may rely on: the
        Sources section is generated from claims, so it cannot disagree with
        them. If a `sources` field were ever added, that guarantee breaks and
        the contract becomes false."""
        self.assertIn("no `sources` field", self.doc)
        self.assertNotIn("sources", {f.name for f in fields(answer.Answer)})

    def test_the_progression_length_the_contract_claims_is_the_real_one(self) -> None:
        """§7 item 6 says the real trace has six calls, not the design doc's
        five, and that hiding the sixth would be the same lie as a trace
        omitting it. So the number is asserted."""
        self.assertEqual(len(investigation.PROGRESSION), 6)
        self.assertIn("The real trace has six", self.doc)

    def test_a_fact_cannot_be_constructed_without_evidence(self) -> None:
        """§1's table promises a consumer that a FACT always has evidence."""
        with self.assertRaises(ValueError):
            answer.Claim(statement="x", entry_class="FACT", evidence=())

    def test_an_inference_cannot_be_constructed_without_confidence(self) -> None:
        with self.assertRaises(ValueError):
            answer.Claim(statement="x", entry_class="INFERENCE", evidence=("e",))

    def test_team_knowledge_cannot_be_constructed_without_an_author(self) -> None:
        with self.assertRaises(ValueError):
            answer.Claim(statement="x", entry_class="TEAM_KNOWLEDGE")

    def test_team_knowledge_needs_no_evidence(self) -> None:
        """The other half of the same promise -- it is the class that exists for
        uncorroborated statements, so requiring evidence would defeat it."""
        claim = answer.Claim(
            statement="we are dropping this pattern",
            entry_class="TEAM_KNOWLEDGE",
            provided_by="serina",
        )
        self.assertEqual(claim.evidence, ())


class ContractOpenQuestionsTest(unittest.TestCase):
    """The contract's value depends on its unresolved items staying visible."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.doc = CONTRACT.read_text()

    def test_the_known_divergences_are_named_with_their_issues(self) -> None:
        """§7 exists so a consumer is not surprised by a gap. Each open
        divergence must name the issue tracking it, or the section becomes a
        list of excuses rather than a work queue."""
        for issue in ("#571", "#572", "#570", "#569", "#270"):
            with self.subTest(issue=issue):
                self.assertIn(issue, self.doc)

    def test_the_ci_gap_is_disclosed(self) -> None:
        """The contract specifies code whose 307 tests are gated by nothing.
        A reader must not have to discover that elsewhere."""
        self.assertIn("runs in CI", self.doc)
        self.assertIn("#270", self.doc)

    def test_the_unratified_status_is_stated(self) -> None:
        self.assertIn("not ratified", self.doc)


if __name__ == "__main__":
    unittest.main()
