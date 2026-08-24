"""Controls for worked_answer.py -- issue #211.

Hermetic: a KnowledgeAgent built from fixture Symbols and driven through the
Tools seam. The live run against real buzz-core data is evidenced in the PR body.

Run:  python3 -m unittest test_worked_answer
  or: python3 test_worked_answer.py
"""

from __future__ import annotations

import unittest
from dataclasses import dataclass

from answer import SECTION_ORDER, render
from graph import ProjectGraph
from investigation import Tools
from knowledge_agent import KnowledgeAgent
from memory import ProjectMemory
from semantic_index import SemanticIndex
from symbol import DefinedAt, Symbol
from worked_answer import build, deepest_path, render_flow, section_names

FILE = "crates/buzz-core/src/kind.rs"
GATE = "is_unshared_gated_event"
INNER = "is_shared_gated_kind"
SIGNATURE = f"pub fn {GATE}(event: &nostr::Event, requester_pubkey_bytes: &[u8]) -> bool"
FILE_TEXT = "\n".join(["// header"] * 5 + [SIGNATURE, "}"])


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


def _symbol(name: str, calls: tuple[str, ...] = ()) -> Symbol:
    return Symbol(
        symbol_id=f"{FILE}::{name}",
        kind="function",
        qualified_name=name,
        defined_at=DefinedAt(file=FILE, start_line=232, end_line=250, temporal_state="WORKING"),
        signature=SIGNATURE if name == GATE else f"pub fn {name}(kind: u32) -> bool",
        calls=calls,
    )


def _agent() -> KnowledgeAgent:
    # A real 2-hop chain: GATE -> INNER -> contains (unresolved, so "extern:").
    symbols = [_symbol(GATE, calls=(INNER,)), _symbol(INNER, calls=("contains",))]
    tools = Tools(
        search_symbols=lambda name, crate: [_Match(GATE, "function", FILE, SIGNATURE)],
        read_file=lambda path, *a, **k: FILE_TEXT,
        find_references=lambda qn, crate: [_Ref("tests::gate_allows_author", FILE, 1013)],
        search_text=lambda pattern, **k: [],
        inspect_git_history=lambda f, s, e: [],
    )
    return KnowledgeAgent(
        crate="buzz-core",
        symbols=symbols,
        graph=ProjectGraph.from_symbols(symbols),
        index=SemanticIndex.from_symbols(symbols),
        memory=ProjectMemory(),
        tools=tools,
    )


class DeepestPathTest(unittest.TestCase):
    def test_returns_the_longest_path_not_the_first_neighbour(self) -> None:
        """A one-hop neighbour is a dependency; a flow is what the call actually
        travels through."""
        hit = deepest_path(_agent(), GATE)
        self.assertIsNotNone(hit)
        self.assertEqual(hit.hop, 2)
        self.assertEqual(hit.path, (GATE, INNER, "extern:contains"))

    def test_a_symbol_with_no_outgoing_calls_has_no_flow(self) -> None:
        self.assertIsNone(deepest_path(_agent(), "extern:contains"))

    def test_an_unknown_symbol_has_no_flow_rather_than_raising(self) -> None:
        self.assertIsNone(deepest_path(_agent(), "no_such_symbol"))

    def test_the_path_is_stable_across_runs(self) -> None:
        """An unstable demo cannot be diffed, so ties break on the path."""
        agent = _agent()
        self.assertEqual(deepest_path(agent, GATE), deepest_path(agent, GATE))


class RenderFlowTest(unittest.TestCase):
    def test_the_flow_line_carries_the_hop_count(self) -> None:
        rendered = render_flow(deepest_path(_agent(), GATE))
        self.assertIn(f"{GATE} -> {INNER} -> extern:contains", rendered)
        self.assertIn("(2 hops)", rendered)

    def test_a_single_hop_is_not_pluralised(self) -> None:
        hit = deepest_path(_agent(), INNER)
        self.assertIn("(1 hop)", render_flow(hit))


class BuildTest(unittest.TestCase):
    """STEP 11's done-when."""

    def test_all_six_sections_are_present(self) -> None:
        rendered = render(build(_agent()))
        self.assertEqual(section_names(rendered), list(SECTION_ORDER))

    def test_the_flow_is_a_traversal_not_the_caller_list(self) -> None:
        """explain()'s caller-based flow answers "what reaches this". A
        traversal answers "what does this reach". Both are real; this example
        wants the second."""
        answer = build(_agent())
        self.assertIn("hop", answer.relevant_flow)
        self.assertNotIn("tests::gate_allows_author ->", answer.relevant_flow)

    def test_the_caveats_carry_an_inference_with_stated_evidence(self) -> None:
        answer = build(_agent())
        inferences = answer.claims_of_class("INFERENCE")
        self.assertTrue(inferences)
        for claim in inferences:
            self.assertTrue(claim.evidence)
            self.assertIn(claim.statement, answer.things_to_be_aware_of)

    def test_the_rendered_flow_has_a_claim_backing_it(self) -> None:
        """Every assertion in an answer must appear in its claim ledger. The
        earlier version substituted relevant_flow and added no claim, so this
        artefact -- the one built to DEMONSTRATE that property -- asserted a
        2-hop path nothing in Sources mentioned."""
        answer = build(_agent())
        self.assertTrue(answer.relevant_flow)
        path_claims = [c for c in answer.claims if "call path" in c.statement]
        self.assertEqual(len(path_claims), 1)
        for node in (GATE, INNER):
            self.assertIn(node, path_claims[0].statement)
        self.assertEqual(path_claims[0].entry_class, "FACT")
        self.assertTrue(path_claims[0].evidence)

    def test_every_node_in_the_rendered_flow_appears_in_a_claim(self) -> None:
        """Stronger than checking a claim exists: the claim must cover the path
        that was actually rendered, not some other path."""
        answer = build(_agent())
        rendered_nodes = [n.strip() for n in answer.relevant_flow.split("(")[0].split("->")]
        ledger = " | ".join(c.statement for c in answer.claims)
        for node in rendered_nodes:
            self.assertIn(node, ledger, f"{node!r} is rendered but claimed nowhere")

    def test_a_symbol_with_no_flow_keeps_the_assembled_answer_unchanged(self) -> None:
        """No traversal is not a reason to discard a real answer."""
        agent = _agent()
        answer = build(agent)
        self.assertTrue(answer.claims)


if __name__ == "__main__":
    unittest.main()
