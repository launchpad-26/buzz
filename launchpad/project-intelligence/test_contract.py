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
reconciliation is honest. That needs a reviewer.

§ 6's error modes WERE in that category and are not any more. A Codex review of
#577 found the table promising `ValueError` for an empty target while all five
methods returned an `Answer`, and § 5 promising a caveat per `INFERENCE` claim
while `find()` returned one with the field empty. Both were reachable from the
hermetic fixture agent in `test_knowledge`, so both are now asserted below
rather than left to the next reviewer's diligence. `ContractBehaviourTest` is
the lesson: a promise about what a call *does* is checkable by making the call,
and a substring search for the sentence that makes the promise is not.

Hermetic: reads CONTRACT.md and introspects the modules. No `rql`, no network.

Run:  python3 -m unittest test_contract
  or: python3 test_contract.py
"""

from __future__ import annotations

import pathlib
import re
import typing
import unittest
from dataclasses import fields

import answer
import confidence
import investigation
import knowledge
import memory
import question
import trace
from answer import Answer

# The hermetic fixture agent -- fixture Symbols, never build(), so no `rql`.
from test_knowledge import TARGET, _agent

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
        ):
            with self.subTest(literal=literal):
                self.assertIn(literal, self.doc)
        self.assertEqual(knowledge.MINIMUM_CANDIDATE_SCORE, 1e-9)
        self.assertEqual(knowledge.DEPENDENCY_HOPS, 2)
        self.assertEqual(knowledge.IMPACT_DIRECT_HOPS, 1)
        self.assertEqual(knowledge.IMPACT_SECONDARY_HOPS, 2)
        self.assertFalse(
            hasattr(investigation, "HISTORY_LINE_WINDOW"),
            "HISTORY_LINE_WINDOW was #569's workaround; it should stay removed now #569 is fixed",
        )

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


class ContractBehaviourTest(unittest.TestCase):
    """Promises about what a CALL does, asserted by making the call.

    Every test here corresponds to a sentence a Codex review of #577 found to be
    false. A substring check for that sentence passed while the sentence was
    wrong, which is the whole reason this class exists.
    """

    @classmethod
    def setUpClass(cls) -> None:
        cls.doc = CONTRACT.read_text()

    # -- § 6: the error table --------------------------------------------------

    def test_six_of_the_seven_do_not_raise_on_an_empty_target(self) -> None:
        """§ 6 promised `ValueError` for an empty target from all seven. Six of
        them wrap the argument before a validator sees it -- `explain("")`
        interpolates it into a non-empty question, `dependencies("")` never calls
        `confidence.assess` at all -- but `find` does not, and raises (below). A
        consumer's `except ValueError` around one of these six is dead code.
        """
        agent = _agent()
        for name in ("explain", "dependencies", "impact", "setup", "conventions", "history"):
            with self.subTest(method=name):
                result = getattr(knowledge, name)(agent, "")
                self.assertIsInstance(
                    result, Answer, f"knowledge.{name}('') should return an Answer, not raise"
                )

    def test_find_and_ask_raise_on_an_empty_target(self) -> None:
        """`find` is the one method of the seven with no bounded input to wrap an
        empty argument into, so the empty query reaches `Answer.__post_init__`
        unguarded. `ask` -- an eighth function, not one of the seven -- calls
        `question.decompose` on the raw argument before it routes anywhere, so it
        raises the same way `find` does, through a different mechanism.
        """
        agent = _agent()
        with self.assertRaises(ValueError):
            knowledge.find(agent, "")
        with self.assertRaises(ValueError):
            knowledge.ask(agent, "")

    def test_the_contract_no_longer_promises_that_exception(self) -> None:
        """The other half: the document must not re-acquire the false promise."""
        self.assertIn(
            "Six of the seven methods do not raise on an empty target", self.doc
        )
        self.assertNotIn("None of the seven methods raise on an empty target", self.doc)

    def test_the_functions_that_do_raise_still_raise(self) -> None:
        """§ 6's rows are true of these three called directly, which is why the
        table was narrowed rather than deleted."""
        agent = _agent()
        with self.assertRaises(ValueError):
            question.decompose("")
        with self.assertRaises(ValueError):
            confidence.assess("", agent.graph, agent.index, agent.memory)
        with self.assertRaises(ValueError):
            answer.Answer(question="")

        # investigate() raises on a question carrying no target -- which is what
        # a nameless question decomposes to, and is find()'s case instead.
        nameless = question.decompose("how does sharing work around here?")
        self.assertIsNone(nameless.target, "fixture question unexpectedly resolved a target")
        with self.assertRaises(ValueError):
            investigation.investigate(nameless, agent.crate, trace.Trace())

    # -- § 5: the caveat promise ----------------------------------------------

    def test_an_inference_claim_does_not_guarantee_a_caveat(self) -> None:
        """§ 5 said `things_to_be_aware_of` "is generated from the `INFERENCE`
        claims", so a consumer could read an empty field as "no inference here".
        `find()` disproves it. Asserted so that a future change which DOES
        populate it consistently fails here and forces § 5 to be corrected --
        the drift is caught in either direction.
        """
        result = knowledge.find(_agent(), "whether a kind is gated for sharing")
        self.assertTrue(
            result.claims_of_class("INFERENCE"), "expected find() to return an INFERENCE claim"
        )
        self.assertEqual(
            result.things_to_be_aware_of,
            "",
            "find() now emits a caveat -- § 5's narrowed wording must be revisited",
        )

    def test_ask_loses_the_base_state_when_it_routes(self) -> None:
        """§ 5's BASE row is honest for the explain pipeline and not for `ask()`,
        which classifies BASE then dispatches to `impact()` and drops it. Tracked
        as #588; asserted so the row cannot silently become true-but-undocumented.

        Asserts the premise first: if the cue words ever stop classifying this
        text as BASE, `assertNotIn` below would pass vacuously (nothing to lose
        if nothing was ever classified). Fail here, not silently there.
        """
        text = f"what happens at head if I change `{TARGET}`?"
        self.assertEqual(
            question.decompose(text).temporal_state,
            "BASE",
            "fixture question no longer classifies BASE -- this test would pass vacuously below",
        )
        result = knowledge.ask(_agent(), text)
        self.assertNotIn("BASE", result.things_to_be_aware_of)
        self.assertIn("#588", self.doc)

    # -- § 3: the shape count -------------------------------------------------

    def test_the_citation_shape_count_matches_the_table(self) -> None:
        """§ 3 said "all four shapes" above a five-row table, and "three of five"
        two lines below that. Nothing caught it, because no test counted. This
        counts, so the number and the table cannot drift apart again.
        """
        words = {"three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8}
        section = self.doc.split("## 3. Citation forms", 1)[1].split("\n---", 1)[0]

        rows = [
            line
            for line in section.splitlines()
            if line.startswith("|") and not line.startswith("| Shape") and "---" not in line
        ]

        match = re.search(r"must handle all\s+(\w+)\s+shapes", section)
        self.assertIsNotNone(match, "§ 3 no longer states how many shapes there are")
        stated = words.get(match.group(1))
        self.assertIsNotNone(stated, f"unrecognised number word {match.group(1)!r} in § 3")
        self.assertEqual(
            stated, len(rows), f"§ 3 says {match.group(1)} shapes; the table lists {len(rows)}"
        )

    def test_the_openability_prose_matches_the_table(self) -> None:
        """The same section's "mis-handle three of six" is a second, independent
        count of the same table -- it drifted too, so it is asserted too.

        Checks both numbers the sentence states: the numerator (unopenable rows)
        AND the denominator (total rows) -- asserting only the numerator lets
        "three of one hundred" pass, which does not pin the sentence to the
        table it claims to describe.
        """
        words = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6}
        section = self.doc.split("## 3. Citation forms", 1)[1].split("\n---", 1)[0]

        rows = [
            line
            for line in section.splitlines()
            if line.startswith("|") and not line.startswith("| Shape") and "---" not in line
        ]
        not_openable = [line for line in rows if line.rstrip().endswith("| no |")]

        match = re.search(r"mis-handle\s+(\w+)\s+of\s+(\w+)", section)
        self.assertIsNotNone(match, "§ 3 no longer states how many citations are unopenable")
        self.assertEqual(
            words.get(match.group(1)), len(not_openable), "numerator does not match unopenable rows"
        )
        self.assertEqual(
            words.get(match.group(2)), len(rows), "denominator does not match the table's total rows"
        )


if __name__ == "__main__":
    unittest.main()
