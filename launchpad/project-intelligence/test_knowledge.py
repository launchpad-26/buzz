"""Controls for knowledge.py -- issue #211.

Hermetic: a KnowledgeAgent constructed from fixture Symbols (never build(),
which indexes via `rql`) and driven through investigation.py's Tools seam.
setup() reads real repo manifests, which is deterministic and needs no index.

Run:  python3 -m unittest test_knowledge
  or: python3 test_knowledge.py
"""

from __future__ import annotations

import unittest
from dataclasses import dataclass

import knowledge
from answer import Answer
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

    def test_an_empty_slice_is_still_a_fact_scoped_to_the_graph(self) -> None:
        """"The graph holds no dependent" is an observation. "Nothing depends on
        this" is a claim about the world that was never established."""
        result = knowledge.impact(_agent(), "symbol_with_no_edges")
        for claim in result.claims:
            self.assertEqual(claim.entry_class, "FACT")
            self.assertIn("the graph holds no", claim.statement)


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

    def test_the_non_persistence_caveat_is_stated_not_implied(self) -> None:
        result = knowledge.conventions(_agent(), None)
        self.assertIn("does not persist", result.things_to_be_aware_of)


class SetupTest(unittest.TestCase):
    def test_a_real_justfile_recipe_is_cited_by_file_and_line(self) -> None:
        result = knowledge.setup(_agent(), "test")
        cited = [c for c in result.claims if "Justfile" in " ".join(c.evidence)]
        self.assertTrue(cited, "no claim cited the real Justfile")
        self.assertRegex(cited[0].evidence[0], r"^Justfile:\d+$")

    def test_an_unknown_task_reports_not_found_rather_than_guessing(self) -> None:
        """A generic recipe is wrong the moment the project's tooling differs
        from the guess, so nothing is invented."""
        result = knowledge.setup(_agent(), "frobnicate")
        self.assertIn("no 'frobnicate' entry point", result.claims[0].statement)


class FindTest(unittest.TestCase):
    def test_an_unresolvable_concept_says_so_about_the_index(self) -> None:
        result = knowledge.find(_agent(), "zzzz nothing like this exists zzzz")
        self.assertIn("statement about this index", result.things_to_be_aware_of)

    def test_a_zero_score_concept_resolves_to_nothing_not_to_whatever_ranked_first(self) -> None:
        """Verified against #210, not assumed: the concept below scores 0.0 --
        no shared token with any summary -- and the pipeline STILL returns a
        candidate, with real tested_by and called_by edges attached. Reporting
        that as a find is true evidence about the wrong subject."""
        result = knowledge.find(_agent(), "zzzz nothing like this exists zzzz")
        self.assertIn("No candidate resolved", result.short_answer)
        for claim in result.claims:
            self.assertNotIn("is the implementation", claim.statement)

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
