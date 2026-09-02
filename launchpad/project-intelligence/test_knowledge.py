"""Controls for knowledge.py -- issue #211.

Hermetic: a KnowledgeAgent constructed from fixture Symbols (never build(),
which indexes via `rql`) and driven through investigation.py's Tools seam.
setup() reads real repo manifests, which is deterministic and needs no index.

Run:  python3 -m unittest test_knowledge
  or: python3 test_knowledge.py
"""

from __future__ import annotations

import re
import unittest
from dataclasses import dataclass

import knowledge
from answer import SECTION_ORDER, Answer, render
from graph import ProjectGraph
from investigation import Tools
from knowledge_agent import KnowledgeAgent
from memory import MemoryEntry, ProjectMemory
from semantic_index import SemanticIndex
from symbol import DefinedAt, Symbol

TARGET = "is_shared_gated_kind"
CALLER = "is_unshared_gated_event"
FILE = "crates/buzz-core/src/kind.rs"
SIGNATURE = f"pub fn {TARGET}(kind: u32) -> bool"
FILE_TEXT = "\n".join(["// header"] * 5 + [SIGNATURE, "}"] + ["mod tests {", f"  {TARGET}(1);", "}"])


@dataclass(frozen=True)
class _Match:
    qualified_name: str
    kind: str
    file: str
    signature: str


@dataclass(frozen=True)
class _Ref:
    caller_qualified_name: str
    file: str
    line: int


def _symbol(name: str, calls: tuple[str, ...] = (), tests: tuple[str, ...] = ()) -> Symbol:
    return Symbol(
        symbol_id=f"{FILE}::{name}",
        kind="function",
        qualified_name=name,
        defined_at=DefinedAt(file=FILE, start_line=219, end_line=221, temporal_state="WORKING"),
        signature=f"pub fn {name}(kind: u32) -> bool",
        calls=calls,
        tests=tests,
    )


def _agent(memory: ProjectMemory | None = None) -> KnowledgeAgent:
    symbols = [_symbol(TARGET, tests=("tests::membership",)), _symbol(CALLER, calls=(TARGET,))]
    tools = Tools(
        search_symbols=lambda name, crate: [_Match(TARGET, "function", FILE, SIGNATURE)],
        read_file=lambda path, *a, **k: FILE_TEXT,
        find_references=lambda qn, crate: [],
        search_text=lambda pattern, **k: [],
        inspect_git_history=lambda f, s, e: [],
    )
    return KnowledgeAgent(
        crate="buzz-core",
        symbols=symbols,
        graph=ProjectGraph.from_symbols(symbols),
        index=SemanticIndex.from_symbols(symbols),
        memory=memory if memory is not None else ProjectMemory(),
        tools=tools,
    )


class SurfaceTest(unittest.TestCase):
    """STEP 9's done-when: all seven called, every claim provenance-labeled."""

    def setUp(self) -> None:
        memory = ProjectMemory()
        memory.add(
            MemoryEntry(
                id="tk1",
                entry_class="TEAM_KNOWLEDGE",
                statement=f"we are not adding kind variants near {TARGET} this milestone",
                provided_by="serina",
            )
        )
        self.agent = _agent(memory)
        self.calls = {
            "find": lambda: knowledge.find(self.agent, "whether a kind is gated for sharing"),
            "explain": lambda: knowledge.explain(self.agent, TARGET),
            "dependencies": lambda: knowledge.dependencies(self.agent, TARGET),
            "impact": lambda: knowledge.impact(self.agent, TARGET),
            "setup": lambda: knowledge.setup(self.agent, "test"),
            "conventions": lambda: knowledge.conventions(self.agent, "kind"),
            "history": lambda: knowledge.history(self.agent, TARGET),
        }

    def test_all_seven_methods_exist_and_are_callable(self) -> None:
        self.assertEqual(set(self.calls), set(knowledge.all_methods()))
        for name in knowledge.all_methods():
            with self.subTest(method=name):
                self.assertTrue(callable(getattr(knowledge, name)))

    def test_every_method_returns_an_answer(self) -> None:
        """One return type is the point: a caller never has to learn a second
        shape to find out whether a field is a fact."""
        for name, call in self.calls.items():
            with self.subTest(method=name):
                self.assertIsInstance(call(), Answer)

    def test_every_claim_from_every_method_carries_a_provenance_class(self) -> None:
        for name, call in self.calls.items():
            result = call()
            with self.subTest(method=name):
                self.assertTrue(result.claims, f"knowledge.{name} returned no claims at all")
                for claim in result.claims:
                    self.assertIn(claim.entry_class, ("FACT", "INFERENCE", "TEAM_KNOWLEDGE"))

    def test_no_method_returns_a_claim_without_evidence_unless_team_knowledge(self) -> None:
        """TEAM_KNOWLEDGE is the only class allowed to stand without evidence,
        and Claim already enforces that -- this asserts no method smuggles an
        unevidenced claim through by mislabeling its class."""
        for name, call in self.calls.items():
            for claim in call().claims:
                with self.subTest(method=name, claim=claim.statement):
                    if claim.entry_class == "TEAM_KNOWLEDGE":
                        self.assertIsNotNone(claim.provided_by)
                    else:
                        self.assertTrue(claim.evidence)


class ExplainDepthTest(unittest.TestCase):
    """#571's done-when: explain(symbol, depth) actually renders differently."""

    def setUp(self) -> None:
        # A dedicated agent, not the shared _agent() helper: TRACE needs a
        # populated Relevant flow section, which needs find_references to
        # return a real caller -- _agent()'s stub always returns []. No
        # ProjectMemory entry here (see RATIONALE's own agent below): assess()
        # treats any ProjectMemory hit as `confident`, which skips the
        # find_references/search_text corroboration stages entirely -- the
        # same defect this repo's confidence.py docstring already documents
        # being found the hard way once. A memory entry here would silently
        # empty out Relevant flow again.
        symbols = [_symbol(TARGET, tests=("tests::membership",)), _symbol(CALLER, calls=(TARGET,))]
        tools = Tools(
            search_symbols=lambda name, crate: [_Match(TARGET, "function", FILE, SIGNATURE)],
            read_file=lambda path, *a, **k: FILE_TEXT,
            find_references=lambda qn, crate: [_Ref(CALLER, FILE, 220)],
            search_text=lambda pattern, **k: [],
            inspect_git_history=lambda f, s, e: [],
        )
        self.agent = KnowledgeAgent(
            crate="buzz-core",
            symbols=symbols,
            graph=ProjectGraph.from_symbols(symbols),
            index=SemanticIndex.from_symbols(symbols),
            memory=ProjectMemory(),
            tools=tools,
        )

    def test_four_depths_share_one_claim_set_and_differ_only_in_rendering(self) -> None:
        """STEP 5: SUMMARY/ONBOARDING/IMPLEMENTATION/TRACE run the identical
        investigation -- only RATIONALE (extra history stage) and IMPACT
        (delegates to impact() entirely) are allowed to differ, and both are
        pre-existing, documented exceptions rather than new ones."""
        answers = {
            depth: knowledge.explain(self.agent, TARGET, depth)
            for depth in ("SUMMARY", "ONBOARDING", "IMPLEMENTATION", "TRACE")
        }
        claim_sets = {depth: a.claims for depth, a in answers.items()}
        first = next(iter(claim_sets.values()))
        for depth, claims in claim_sets.items():
            with self.subTest(depth=depth):
                self.assertEqual(claims, first)
        # And they really are differently rendered, not vacuously equal because
        # nothing renders differently either.
        rendered = {depth: render(a) for depth, a in answers.items()}
        self.assertEqual(len(set(rendered.values())), len(rendered))

    def test_summary_is_one_paragraph_with_no_file_path(self) -> None:
        rendered = render(knowledge.explain(self.agent, TARGET, "SUMMARY"))
        self.assertIsNone(re.search(r"\S+\.\w+:\d+", rendered))
        headings = [ln for ln in rendered.splitlines() if ln.startswith("## ")]
        self.assertEqual(headings, ["## Short answer"])

    def test_onboarding_is_the_only_depth_with_every_section_present(self) -> None:
        rendered = render(knowledge.explain(self.agent, TARGET, "ONBOARDING"))
        headings = [ln[3:] for ln in rendered.splitlines() if ln.startswith("## ")]
        self.assertEqual(headings, list(SECTION_ORDER))

    def test_implementation_has_line_referenced_sources_and_no_relevant_flow(self) -> None:
        rendered = render(knowledge.explain(self.agent, TARGET, "IMPLEMENTATION"))
        headings = [ln[3:] for ln in rendered.splitlines() if ln.startswith("## ")]
        self.assertEqual(headings, ["Short answer", "How it works", "Important files", "Sources"])
        self.assertRegex(rendered, r"\S+\.\w+:\d+")

    def test_trace_has_relevant_flow_and_no_how_it_works(self) -> None:
        rendered = render(knowledge.explain(self.agent, TARGET, "TRACE"))
        headings = [ln[3:] for ln in rendered.splitlines() if ln.startswith("## ")]
        self.assertEqual(headings, ["Short answer", "Relevant flow", "Sources"])

    def test_rationale_excludes_the_generic_fact_and_keeps_team_knowledge(self) -> None:
        # A separate agent, with a TEAM_KNOWLEDGE entry mentioning TARGET --
        # not self.agent, whose whole point is an EMPTY memory (see setUp).
        memory = ProjectMemory()
        memory.add(
            MemoryEntry(
                id="tk-rationale",
                entry_class="TEAM_KNOWLEDGE",
                statement=f"we are not adding kind variants near {TARGET} this milestone",
                provided_by="serina",
            )
        )
        agent = KnowledgeAgent(
            crate="buzz-core",
            symbols=self.agent.symbols,
            graph=self.agent.graph,
            index=self.agent.index,
            memory=memory,
            tools=self.agent.tools,
        )
        rendered = render(knowledge.explain(agent, TARGET, "RATIONALE"))
        self.assertIn("## Sources", rendered)
        self.assertNotIn(f"{TARGET} is defined as", rendered)
        self.assertIn("TEAM KNOWLEDGE", rendered)

    def test_impact_states_direct_and_secondary_separately(self) -> None:
        answer = knowledge.explain(self.agent, TARGET, "IMPACT")
        self.assertRegex(answer.short_answer, r"\d+ direct and \d+ secondary")
        self.assertEqual(answer.depth, "IMPACT")

    def test_target_less_question_still_renders_at_the_requested_depth(self) -> None:
        """Review finding (High): KnowledgeAgent.run()'s target-less early
        return (question.target is None) built its Answer directly, never
        through assemble() -- so it never got STEP 2's depth stamp. A blank
        or unresolvable backticked target (extract_target() returns None for
        one) reaches this path through the public agent.answer() /
        knowledge.explain() surface with no hand-built object needed."""
        answer = self.agent.answer("how does `` work?", depth="SUMMARY")
        self.assertEqual(answer.depth, "SUMMARY")
        rendered = render(answer)
        headings = [ln for ln in rendered.splitlines() if ln.startswith("## ")]
        self.assertEqual(headings, ["## Short answer"])


class AskRoutingTest(unittest.TestCase):
    """HIGH 2: every intent must reach its own method.

    `run()` never branched on intent, so five of seven were dead values:
    "how do I run the tests?" classified SETUP with setup_task="test", discarded
    both, and answered "no symbol named in the question" while setup() existed
    and would have answered. question.py meanwhile claimed "a question and a
    direct call route to identical logic".

    The review panel called this the FOURTH dead-classified-value defect on a
    branch that had fixed that class three times. So this asserts the whole
    routing table rather than one case.
    """

    ROUTES = {
        "SETUP": ("how do I run the tests?", "how do I test this project?"),
        "IMPACT": (f"what happens if I change `{TARGET}`?", "what happens if I change"),
        "DEPENDENCIES": (f"what does `{TARGET}` depend on?", "what does is_shared_gated_kind depend on"),
        "HISTORY": (f"how did `{TARGET}` evolve?", None),
        "CONVENTIONS": ("what are our conventions for kind gating?", "what are our conventions"),
        "FIND": ("where is the code that checks kind gating?", None),
        "EXPLAIN": (f"how does `{TARGET}` work?", None),
    }

    def test_every_intent_routes_to_a_distinct_method(self) -> None:
        """Identified by the `question` field each method stamps on its Answer --
        which differs per method, so two intents reaching the same one shows up."""
        agent = _agent()
        produced = {
            intent: knowledge.ask(agent, question).question
            for intent, (question, _) in self.ROUTES.items()
        }
        # SETUP, DEPENDENCIES, IMPACT and CONVENTIONS each rewrite the question
        # into their own phrasing; the rest pass it through. Either way, no two
        # intents may produce the same answer shape from different questions.
        self.assertEqual(len(produced), 7)
        for intent, (_, expected_fragment) in self.ROUTES.items():
            if expected_fragment is None:
                continue
            with self.subTest(intent=intent):
                self.assertIn(expected_fragment, produced[intent])

    def test_a_setup_question_is_answered_by_setup_not_by_explain(self) -> None:
        """The exact case the panel reproduced."""
        answer = knowledge.ask(SetupTest._real_tools_agent(), "how do I run the tests?")
        self.assertNotIn("No symbol named", answer.short_answer)
        self.assertTrue(
            any("Justfile" in " ".join(c.evidence) for c in answer.claims),
            "a SETUP question did not reach setup()",
        )

    def test_all_seven_intents_are_covered_by_the_routing_table(self) -> None:
        """Guards against an eighth intent being added with no route -- which
        would fall through to explain() silently, which is this defect again."""
        from question import Intent
        from typing import get_args

        self.assertEqual(set(self.ROUTES), set(get_args(Intent)))

    def test_an_intent_needing_a_target_says_so_rather_than_guessing(self) -> None:
        """IMPACT with no nameable symbol must not crash on a None target, and
        must not silently answer a different question."""
        answer = knowledge.ask(_agent(), "what happens if I change the gating thing?")
        self.assertIn("No symbol named", answer.short_answer)
        self.assertIn("IMPACT", answer.things_to_be_aware_of)


class ImpactTest(unittest.TestCase):
    def test_direct_and_secondary_are_separate_claims(self) -> None:
        """Conflating them hides which consequences are certain and which are
        worth double-checking (§ Impact analysis)."""
        result = knowledge.impact(_agent(), TARGET)
        statements = " | ".join(c.statement for c in result.claims)
        self.assertIn("direct dependent", statements)
        self.assertIn("secondary dependent", statements)
        self.assertEqual(len(result.claims), 2)

    def test_a_real_caller_appears_as_a_direct_dependent(self) -> None:
        result = knowledge.impact(_agent(), TARGET)
        direct = next(c for c in result.claims if "direct dependent" in c.statement)
        self.assertIn(CALLER, direct.statement)

    def test_counts_are_pluralised_properly_and_never_print_a_paren_s(self) -> None:
        """The live CLI printed "1 direct(s)", which reads as unfinished output
        in an answer whose whole point is being trustworthy."""
        result = knowledge.dependencies(_agent(), CALLER)
        statements = " | ".join(c.statement for c in result.claims)
        self.assertNotIn("(s)", statements)
        self.assertIn("1 direct dependency", statements)

    def test_the_short_answer_also_avoids_paren_s(self) -> None:
        """The pluralisation fix landed on claims only, and its regression test
        iterated result.claims -- so the defect its own narrative described
        survived one field over, invisibly. Found by the review panel."""
        for call in (knowledge.dependencies, knowledge.impact):
            with self.subTest(method=call.__name__):
                result = call(_agent(), CALLER)
                self.assertNotIn("(s)", result.short_answer)

    def test_a_plural_count_uses_the_plural_word(self) -> None:
        result = knowledge.impact(_agent(), TARGET)
        direct = next(c for c in result.claims if "direct dependent" in c.statement)
        self.assertNotIn("(s)", direct.statement)

    def test_an_empty_slice_is_still_a_fact_scoped_to_the_graph(self) -> None:
        """"The graph holds no dependent" is an observation. "Nothing depends on
        this" is a claim about the world that was never established."""
        result = knowledge.impact(_agent(), "symbol_with_no_edges")
        for claim in result.claims:
            self.assertEqual(claim.entry_class, "FACT")
            # "the INDEXED graph holds no ..." -- the wording is what earns the
            # FACT label here, since nothing was re-read from the tree. Codex
            # pushed on exactly this: a cached traversal asserted as fact.
            self.assertIn("the indexed graph holds no", claim.statement)

    def test_a_graph_only_answer_states_that_it_is_a_snapshot(self) -> None:
        """No live read happens in dependencies()/impact(), so the answer must
        say so rather than let a reader assume the tree was consulted."""
        for call in (knowledge.dependencies, knowledge.impact):
            with self.subTest(method=call.__name__):
                result = call(_agent(), TARGET)
                self.assertIn("indexed at agent build time", result.things_to_be_aware_of)


class ConventionsTest(unittest.TestCase):
    def test_fact_entries_are_excluded(self) -> None:
        """A convention is what the team decided, not what the code happens to
        do. Reading conventions off the code is how an accident becomes a rule."""
        memory = ProjectMemory()
        memory.add(
            MemoryEntry(
                id="f1",
                entry_class="FACT",
                statement=f"{TARGET} returns bool",
                evidence=(f"{FILE}:219-221",),
            )
        )
        result = knowledge.conventions(_agent(memory), TARGET)
        self.assertEqual(result.claims_of_class("FACT")[0].statement.count("returns bool"), 0)

    def test_a_superseded_convention_is_not_surfaced_as_current(self) -> None:
        """conventions() had the same superseded_by gap as assemble, and only
        assemble got a regression test in the first fix round -- Codex flagged
        the asymmetry. Both consumers now have one."""
        memory = ProjectMemory()
        memory.add(
            MemoryEntry(
                id="old",
                entry_class="TEAM_KNOWLEDGE",
                statement=f"{TARGET}: do not use",
                provided_by="alice",
                superseded_by="new",
            )
        )
        memory.add(
            MemoryEntry(
                id="new",
                entry_class="TEAM_KNOWLEDGE",
                statement=f"{TARGET}: approved for use",
                provided_by="bob",
            )
        )
        result = knowledge.conventions(_agent(memory), TARGET)
        team = result.claims_of_class("TEAM_KNOWLEDGE")
        self.assertEqual(len(team), 1)
        self.assertEqual(team[0].provided_by, "bob")

    def test_setup_reads_through_the_injected_seam(self) -> None:
        """The existing setup tests deliberately use REAL tools, so reverting
        setup() to the process-global investigator would go undetected. Codex
        mutation-tested exactly that. This one injects a reader and asserts it
        was the one used."""
        seen: list[str] = []

        def reader(path, *a, **k):
            seen.append(path)
            return "test:\n    echo hi"

        agent = _agent()
        agent.tools = Tools(
            search_symbols=agent.tools.search_symbols,
            read_file=reader,
            find_references=agent.tools.find_references,
            search_text=agent.tools.search_text,
            inspect_git_history=agent.tools.inspect_git_history,
        )
        knowledge.setup(agent, "test")
        self.assertTrue(seen, "setup() did not read through the injected seam")
        self.assertIn("Justfile", seen)

    def test_the_non_persistence_caveat_is_stated_not_implied(self) -> None:
        result = knowledge.conventions(_agent(), None)
        self.assertIn("does not persist", result.things_to_be_aware_of)


class SetupTest(unittest.TestCase):
    """setup() reads through agent.tools now, not the process-global
    investigator -- the seam was split and Codex found it. These tests therefore
    use REAL tools, because reading real manifests is the behaviour under test.
    """

    @staticmethod
    def _real_tools_agent() -> KnowledgeAgent:
        symbols = [_symbol(TARGET, tests=("tests::membership",))]
        return KnowledgeAgent(
            crate="buzz-core",
            symbols=symbols,
            graph=ProjectGraph.from_symbols(symbols),
            index=SemanticIndex.from_symbols(symbols),
            memory=ProjectMemory(),
        )

    def test_a_real_justfile_recipe_is_cited_by_file_and_line(self) -> None:
        result = knowledge.setup(self._real_tools_agent(), "test")
        cited = [c for c in result.claims if "Justfile" in " ".join(c.evidence)]
        self.assertTrue(cited, "no claim cited the real Justfile")
        self.assertRegex(cited[0].evidence[0], r"^Justfile:\d+$")

    def test_an_unknown_task_reports_not_found_rather_than_guessing(self) -> None:
        """A generic recipe is wrong the moment the project's tooling differs
        from the guess, so nothing is invented."""
        result = knowledge.setup(self._real_tools_agent(), "frobnicate")
        self.assertIn("no 'frobnicate' entry point", result.claims[0].statement)


class FindTest(unittest.TestCase):
    def test_a_rejected_candidate_is_never_reported_as_an_empty_index(self) -> None:
        """The cross-model review's finding 1: this path emitted
        `FACT: the SemanticIndex returned no candidate` while find_concept had
        returned is_shared_gated_kind at score 0.0. A FACT that is untrue is the
        worst output this layer can produce, and it was introduced BY the fix
        for the 0.0-score defect. The two no-answer states are now distinct."""
        result = knowledge.find(_agent(), "zzzz nothing like this exists zzzz")
        for claim in result.claims:
            self.assertNotIn("returned no candidate", claim.statement)
        self.assertIn("at or below the floor", result.claims[0].statement)
        self.assertIn("did return a top-ranked symbol", result.things_to_be_aware_of)

    def test_a_genuinely_empty_index_does_report_an_empty_index(self) -> None:
        """The mirror. Without it, a version that never reported an empty index
        would pass the test above."""
        empty = KnowledgeAgent(
            crate="empty",
            symbols=[],
            graph=ProjectGraph.from_symbols([]),
            index=SemanticIndex.from_symbols([]),
            memory=ProjectMemory(),
        )
        result = knowledge.find(empty, "anything")
        self.assertIn("returned no candidate", result.claims[0].statement)

    def test_a_zero_score_concept_resolves_to_nothing_not_to_whatever_ranked_first(self) -> None:
        """Verified against #210, not assumed: the concept below scores 0.0 --
        no shared token with any summary -- and the pipeline STILL returns a
        candidate, with real tested_by and called_by edges attached. Reporting
        that as a find is true evidence about the wrong subject."""
        result = knowledge.find(_agent(), "zzzz nothing like this exists zzzz")
        self.assertIn("No candidate resolved", result.short_answer)
        for claim in result.claims:
            self.assertNotIn("is the implementation", claim.statement)

    def test_an_empty_index_returns_no_candidate_instead_of_crashing(self) -> None:
        """Found by review-code, reproduced before fixing. find_it_for_me returns
        a PipelineResult with EVERY field None -- not None itself -- when
        index.search() is empty, which happens for an index built from zero
        symbols. The first version of the score-floor guard checked only
        `result is not None`, so this raised
        "TypeError: '<=' not supported between instances of 'NoneType' and
        'float'". The guard added to close one fail-open defect had opened a
        crash on the empty case."""
        empty = KnowledgeAgent(
            crate="empty",
            symbols=[],
            graph=ProjectGraph.from_symbols([]),
            index=SemanticIndex.from_symbols([]),
            memory=ProjectMemory(),
        )
        result = knowledge.find(empty, "anything at all")
        self.assertIn("No candidate resolved", result.short_answer)
        self.assertEqual(result.claims[0].entry_class, "FACT")

    def test_a_score_exactly_at_the_floor_resolves_to_nothing(self) -> None:
        """Pins the `<=` boundary itself, which no test covered -- only the 0.0
        case was exercised, and 0.0 would also pass under a `<` comparison."""

        class _AtFloor:
            qualified_name = "whatever"
            candidate_score = knowledge.MINIMUM_CANDIDATE_SCORE
            subsystem_score = 0.5
            subsystem = type("S", (), {"scope": "f.rs"})()
            confirmation = None

        agent = _agent()
        agent.find_concept = lambda concept: _AtFloor()  # type: ignore[method-assign]
        self.assertIn("No candidate resolved", knowledge.find(agent, "x").short_answer)

    def test_a_score_just_above_the_floor_does_resolve(self) -> None:
        """The mirror, without which a guard that rejected everything would
        pass the test above."""

        class _AboveFloor:
            qualified_name = "whatever"
            candidate_score = knowledge.MINIMUM_CANDIDATE_SCORE * 10
            subsystem_score = 0.5
            subsystem = type("S", (), {"scope": "f.rs"})()
            confirmation = None

        agent = _agent()
        agent.find_concept = lambda concept: _AboveFloor()  # type: ignore[method-assign]
        self.assertIn("Most likely whatever", knowledge.find(agent, "x").short_answer)

    def test_the_identification_itself_is_never_a_fact(self) -> None:
        """A similarity rank and being right are different properties. The
        scores are measured (FACT); that the top hit answers the question is
        not."""
        result = knowledge.find(_agent(), "whether a kind is gated for sharing")
        identification = [c for c in result.claims if "is the implementation" in c.statement]
        self.assertEqual(len(identification), 1)
        self.assertEqual(identification[0].entry_class, "INFERENCE")

    def test_the_confidence_on_the_identification_is_the_measured_score(self) -> None:
        """Inventing a separate number would hide the one real measurement
        behind a guess about it."""
        agent = _agent()
        concept = "whether a kind is gated for sharing"
        expected = agent.find_concept(concept).candidate_score
        identification = next(
            c for c in knowledge.find(agent, concept).claims if "is the implementation" in c.statement
        )
        self.assertAlmostEqual(identification.confidence, expected)

    def test_graph_edges_are_not_worded_as_confirming_the_match(self) -> None:
        """Those edges exist no matter what was asked, so the wording must not
        let a reader take them for corroboration of the concept resolution."""
        result = knowledge.find(_agent(), "gated kind sharing check")
        edge_claims = [c for c in result.claims if "real graph edge" in c.statement]
        for claim in edge_claims:
            self.assertIn("not a confirmation of the match", claim.statement)


if __name__ == "__main__":
    unittest.main()
