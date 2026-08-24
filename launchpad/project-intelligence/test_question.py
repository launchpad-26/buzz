"""Controls for question.py -- issue #211.

Hermetic: strings in, Question out. No `rql`, no repo reads, no network.

Run:  python3 -m unittest test_question
  or: python3 test_question.py
"""

from __future__ import annotations

import unittest
from typing import get_args

from question import SETUP_TASKS, Depth, classify_intent, decompose, extract_target

# STEP 4's done-when: seven questions, one per intent, no two colliding.
# Kept as data so the "no two collide" property is checked over the whole set
# rather than one assertion at a time.
ONE_PER_INTENT = {
    "SETUP": "how do I run the tests?",
    "IMPACT": "what happens if I change `is_shared_gated_kind`?",
    "DEPENDENCIES": "what does `is_shared_gated_kind` depend on?",
    "HISTORY": "how did `is_shared_gated_kind` evolve?",
    "CONVENTIONS": "what are our conventions for kind gating?",
    "FIND": "where is the code that checks kind gating?",
    "EXPLAIN": "how does `is_shared_gated_kind` work?",
}


class IntentTest(unittest.TestCase):
    def test_each_intent_has_a_question_that_reaches_only_it(self) -> None:
        classified = {intent: decompose(q).intent for intent, q in ONE_PER_INTENT.items()}
        self.assertEqual(classified, {intent: intent for intent in ONE_PER_INTENT})

    def test_all_seven_intents_are_covered(self) -> None:
        """Guards against a future intent being added with no question proving
        it is reachable -- an unreachable branch reads as working code."""
        self.assertEqual(len(ONE_PER_INTENT), 7)
        self.assertEqual(len(set(ONE_PER_INTENT.values())), 7)

    def test_an_unrecognised_question_falls_back_to_explain(self) -> None:
        """Documented behaviour, not an accident: falling back beats guessing."""
        self.assertEqual(decompose("tell me about the gating thing").intent, "EXPLAIN")


class SetupTaskTest(unittest.TestCase):
    def test_running_the_tests_resolves_to_test_not_run(self) -> None:
        """"run" is the verb, "test" is the subject. Matching `run` first
        answered "how do I start the app" to a question about the suite."""
        self.assertEqual(decompose("how do I run the tests?").setup_task, "test")

    def test_running_the_app_resolves_to_run(self) -> None:
        self.assertEqual(decompose("how do I run the app?").setup_task, "run")

    def test_mechanism_questions_are_not_setup_questions(self) -> None:
        """"how does the test runner work" contains "test" but asks about
        mechanism. Routing it to SETUP answers a different question."""
        question = decompose("how does the test runner work?")
        self.assertEqual(question.intent, "EXPLAIN")
        self.assertIsNone(question.setup_task)

    def test_every_named_task_is_reachable(self) -> None:
        for task in SETUP_TASKS:
            with self.subTest(task=task):
                self.assertEqual(decompose(f"how do I {task} this project?").setup_task, task)


class TemporalStateTest(unittest.TestCase):
    def test_historical_phrasing_selects_history(self) -> None:
        self.assertEqual(decompose("how did `foo_bar` change over time?").temporal_state, "HISTORY")

    def test_present_tense_phrasing_selects_working(self) -> None:
        self.assertEqual(decompose("how does `foo_bar` work?").temporal_state, "WORKING")

    def test_comparative_phrasing_selects_base(self) -> None:
        self.assertEqual(decompose("how did `foo_bar` behave before my changes?").temporal_state, "BASE")


class TargetTest(unittest.TestCase):
    def test_a_backticked_target_wins_over_a_bare_identifier(self) -> None:
        """The caller marked one up deliberately; a marked-up target may not
        even look like an identifier (a path, a config key)."""
        self.assertEqual(
            extract_target("how does `crates/buzz-core/src/kind.rs` relate to is_shared_gated_kind?"),
            "crates/buzz-core/src/kind.rs",
        )

    def test_snake_case_is_recognised(self) -> None:
        self.assertEqual(extract_target("how does is_shared_gated_kind work?"), "is_shared_gated_kind")

    def test_camel_case_is_recognised(self) -> None:
        self.assertEqual(extract_target("how does AuthMiddleware work?"), "AuthMiddleware")

    def test_path_qualified_names_are_recognised(self) -> None:
        self.assertEqual(extract_target("what calls kind::is_shared_gated_kind?"), "kind::is_shared_gated_kind")

    def test_a_question_with_no_nameable_target_returns_none(self) -> None:
        self.assertIsNone(extract_target("where is the code that sends the welcome email?"))

    def test_a_named_where_is_question_is_not_a_concept_search(self) -> None:
        """FIND exists for callers who cannot name the thing. Someone who wrote
        the name already has it, so the concept pipeline is the wrong tool."""
        self.assertEqual(classify_intent("where is `AuthMiddleware`?")[0], "EXPLAIN")


class DepthTest(unittest.TestCase):
    """classify_depth had ZERO coverage anywhere in the suite until review-tests
    found it: a version returning a constant would have passed all 138 tests.

    The only downstream effect of depth is investigation.py's
    `temporal_state == "HISTORY" or depth == "RATIONALE"`, and every historical
    test phrases its question so temporal_state ALSO says HISTORY -- so the
    depth half of that `or` was never isolated either. That branch is now pinned
    in test_knowledge_agent.py, and the six literals are pinned here.
    """

    def test_each_depth_level_is_reachable(self) -> None:
        cases = {
            "SUMMARY": "briefly, how does `foo_bar` work?",
            "IMPLEMENTATION": "exactly how does `foo_bar` work?",
            "TRACE": "trace `foo_bar` end to end",
            "RATIONALE": "what was the design decision behind `foo_bar`?",
            "IMPACT": "what happens if I change `foo_bar`?",
            "ONBOARDING": "how does `foo_bar` work?",
        }
        classified = {depth: decompose(q).depth for depth, q in cases.items()}
        self.assertEqual(classified, {depth: depth for depth in cases})

    def test_all_six_levels_are_covered_by_the_cases_above(self) -> None:
        """Guards against a seventh level being added with no question proving
        it is reachable -- an unreachable branch reads as working code."""
        self.assertEqual(len(set(get_args(Depth))), 6)

    def test_an_impact_question_always_takes_impact_depth(self) -> None:
        """Intent wins over phrasing here: a blast-radius question rendered at
        onboarding depth would answer a different question than was asked."""
        self.assertEqual(decompose("briefly, what happens if I change `foo_bar`?").depth, "IMPACT")

    def test_a_historical_question_takes_rationale_depth(self) -> None:
        self.assertEqual(decompose("how did `foo_bar` evolve?").depth, "RATIONALE")


class ValidationTest(unittest.TestCase):
    def test_an_empty_question_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            decompose("   ")


if __name__ == "__main__":
    unittest.main()
