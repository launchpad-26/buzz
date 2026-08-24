"""Controls for knowledge_agent.py -- issue #211.

Hermetic: the pure helpers on constructed Symbol fixtures, plus KnowledgeAgent
.run() driven through the Tools seam with call-counting stand-ins. build_answer's
live path (build(), which indexes via `rql`) is verified live and evidenced in
the PR body -- the same boundary test_indexer.py's own docstring draws.

Run:  python3 -m unittest test_knowledge_agent
  or: python3 test_knowledge_agent.py
"""

from __future__ import annotations

import unittest
from dataclasses import dataclass

from graph import ProjectGraph
from investigation import Tools
from knowledge_agent import KnowledgeAgent, cite, find_symbol
from memory import MemoryEntry, ProjectMemory
from semantic_index import SemanticIndex
from symbol import DefinedAt, Symbol

FILE = "crates/buzz-core/src/kind.rs"
TARGET = "is_shared_gated_kind"
SIGNATURE = f"pub fn {TARGET}(kind: u32) -> bool"
FILE_TEXT = "\n".join(["// header"] * 5 + [SIGNATURE, "}"] + ["mod tests {", f"  {TARGET}(1);", "}"])


def _symbol(qualified_name: str, start: int = 219, end: int = 221, calls: tuple[str, ...] = ()) -> Symbol:
    """Field values copied from the real buzz-core symbol this task's live demo
    uses, so the fixture and the demo cannot describe different things."""
    return Symbol(
        symbol_id=f"{FILE}::{qualified_name}",
        kind="function",
        qualified_name=qualified_name,
        defined_at=DefinedAt(
            file=FILE,
            start_line=start,
            end_line=end,
            temporal_state="WORKING",
        ),
        signature=f"pub fn {qualified_name}(kind: u32) -> bool",
        calls=calls,
    )


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


class _CountingTools:
    """Records how many times each tool was called, so a test can assert on
    whether a STAGE ran rather than on what it returned."""

    def __init__(self, refs: list | None = None) -> None:
        self.counts: dict[str, int] = {}
        self.refs = refs if refs is not None else []

    def _bump(self, name: str) -> None:
        self.counts[name] = self.counts.get(name, 0) + 1

    def as_tools(self) -> Tools:
        def search_symbols(name, crate):
            self._bump("search_symbols")
            return [_Match(TARGET, "function", FILE, SIGNATURE)]

        def read_file(path, *a, **k):
            self._bump("read_file")
            return FILE_TEXT

        def find_references(qn, crate):
            self._bump("find_references")
            return list(self.refs)

        def search_text(pattern, **k):
            self._bump("search_text")
            return []

        def inspect_git_history(f, s, e):
            self._bump("inspect_git_history")
            return []

        return Tools(
            search_symbols=search_symbols,
            read_file=read_file,
            find_references=find_references,
            search_text=search_text,
            inspect_git_history=inspect_git_history,
        )


def _agent(tools: Tools, memory: ProjectMemory | None = None) -> KnowledgeAgent:
    symbols = [_symbol(TARGET, calls=("contains",))]
    return KnowledgeAgent(
        crate="buzz-core",
        symbols=symbols,
        graph=ProjectGraph.from_symbols(symbols),
        index=SemanticIndex.from_symbols(symbols),
        memory=memory if memory is not None else ProjectMemory(),
        tools=tools,
    )


def _unconfident_agent(tools: Tools) -> KnowledgeAgent:
    """An agent whose three components know nothing about the target: no graph
    node, no concept entry, no memory. Built from a DIFFERENT symbol so the
    target is genuinely absent from all three."""
    symbols = [_symbol("something_else")]
    return KnowledgeAgent(
        crate="buzz-core",
        symbols=symbols,
        graph=ProjectGraph.from_symbols(symbols),
        index=SemanticIndex.from_symbols(symbols),
        memory=ProjectMemory(),
        tools=tools,
    )


class ConfidenceGateTest(unittest.TestCase):
    """The gate two independent reviewers found missing on 2026-08-24.

    run() computed assess() and then investigated unconditionally, while the
    module docstring claimed stage 3 was "skipped when already confident". No
    test covered it in either direction, so the wiring could be inverted
    silently. These assert on CALL COUNTS, not on returned values, because the
    question is whether a stage ran at all.
    """

    def test_confident_skips_the_corroboration_stages(self) -> None:
        counting = _CountingTools()
        agent = _agent(counting.as_tools())
        outcome = agent.run(f"how does `{TARGET}` work?")
        self.assertTrue(outcome.assessment.confident)
        self.assertEqual(counting.counts.get("find_references", 0), 0)
        self.assertEqual(counting.counts.get("search_text", 0), 0)

    def test_not_confident_runs_the_corroboration_stages(self) -> None:
        counting = _CountingTools()
        agent = _unconfident_agent(counting.as_tools())
        outcome = agent.run(f"how does `{TARGET}` work?")
        self.assertFalse(outcome.assessment.confident)
        self.assertEqual(counting.counts.get("find_references", 0), 1)

    def test_locate_and_read_run_even_when_confident(self) -> None:
        """Never skipped: nothing in the graph, index or memory supplies a
        citable file:line, so skipping them yields an answer with no citation."""
        counting = _CountingTools()
        agent = _agent(counting.as_tools())
        agent.run(f"how does `{TARGET}` work?")
        self.assertEqual(counting.counts.get("search_symbols", 0), 1)
        self.assertGreaterEqual(counting.counts.get("read_file", 0), 1)

    def test_history_is_not_gated_by_confidence(self) -> None:
        """History is the CONTENT of a historical question, not corroboration of
        a present-tense one. Gating it would make knowledge.history() return no
        commits for any target stage 1 felt confident about."""
        counting = _CountingTools()
        agent = _agent(counting.as_tools())
        outcome = agent.run(f"how did `{TARGET}` evolve?")
        self.assertTrue(outcome.assessment.confident)
        self.assertEqual(counting.counts.get("inspect_git_history", 0), 1)

    def test_a_skipped_lookup_never_reports_an_absence_it_did_not_establish(self) -> None:
        """`not corroborated` no longer means "searched and found nothing" -- it
        can mean "never searched". Neither the caveats nor an "appears unused"
        claim may assert an absence nobody looked for."""
        counting = _CountingTools()
        agent = _agent(counting.as_tools())
        answer = agent.run(f"how does `{TARGET}` work?").answer
        self.assertNotIn("No caller and no test-side mention", answer.things_to_be_aware_of)
        self.assertEqual(
            [c for c in answer.claims_of_class("INFERENCE") if "appears unused" in c.statement], []
        )

    def test_an_unconfident_search_that_finds_nothing_does_report_the_absence(self) -> None:
        """The mirror of the test above -- without it, a version that never
        reported an absence at all would pass."""
        counting = _CountingTools()
        agent = _unconfident_agent(counting.as_tools())
        answer = agent.run(f"how does `{TARGET}` work?").answer
        self.assertIn("No caller and no test-side mention", answer.things_to_be_aware_of)

    def test_a_memory_fact_alone_is_enough_to_skip_corroboration(self) -> None:
        counting = _CountingTools()
        memory = ProjectMemory()
        memory.add(
            MemoryEntry(
                id="m1",
                entry_class="FACT",
                statement=f"{TARGET} gates shared kinds",
                evidence=(f"{FILE}:219-221",),
            )
        )
        agent = _unconfident_agent(counting.as_tools())
        agent.memory = memory
        outcome = agent.run(f"how does `{TARGET}` work?")
        self.assertTrue(outcome.assessment.confident)
        self.assertEqual(counting.counts.get("find_references", 0), 0)


class RunShapeTest(unittest.TestCase):
    def test_a_nameless_question_returns_an_answer_without_investigating(self) -> None:
        counting = _CountingTools()
        agent = _agent(counting.as_tools())
        outcome = agent.run("where is the code that checks kind gating?")
        self.assertEqual(counting.counts, {})
        self.assertIsNone(outcome.assessment)
        self.assertIn("No symbol named", outcome.answer.short_answer)

    def test_an_explicit_depth_overrides_the_classified_one(self) -> None:
        counting = _CountingTools()
        agent = _agent(counting.as_tools())
        # RATIONALE reaches the history stage on its own, with the question
        # phrased in the present tense so temporal_state stays WORKING -- this
        # isolates the depth half of investigate()'s `or`.
        agent.run(f"how does `{TARGET}` work?", depth="RATIONALE")
        self.assertEqual(counting.counts.get("inspect_git_history", 0), 1)


class FindSymbolTest(unittest.TestCase):
    def test_returns_the_exact_qualified_name_match(self) -> None:
        wanted = _symbol(TARGET)
        symbols = [_symbol("is_unshared_gated_event"), wanted]
        self.assertIs(find_symbol(symbols, TARGET), wanted)

    def test_a_miss_raises_rather_than_returning_none(self) -> None:
        """A None here would flow into the caller as an AttributeError three
        frames later, naming a field instead of the missing symbol."""
        with self.assertRaises(LookupError) as caught:
            find_symbol([_symbol(TARGET)], "no_such_symbol")
        self.assertIn("no_such_symbol", str(caught.exception))

    def test_matching_is_not_a_prefix_or_substring_match(self) -> None:
        """`is_shared_gated_kind` must not satisfy a lookup for
        `is_shared_gated_kind_v2`, or an answer would describe the wrong
        function while citing its real line range -- true evidence, wrong
        subject, which is the worst shape a citation can have."""
        with self.assertRaises(LookupError):
            find_symbol([_symbol(TARGET)], f"{TARGET}_v2")

    def test_an_empty_index_raises(self) -> None:
        with self.assertRaises(LookupError):
            find_symbol([], TARGET)


class CiteTest(unittest.TestCase):
    def test_renders_file_colon_start_dash_end(self) -> None:
        self.assertEqual(cite(_symbol(TARGET)), f"{FILE}:219-221")

    def test_a_single_line_symbol_still_renders_a_range(self) -> None:
        """Uniform shape matters: the done-when opens these by parsing them, and
        a sometimes-range/sometimes-single form needs two parsers."""
        self.assertEqual(cite(_symbol("one_liner", start=42, end=42)), f"{FILE}:42-42")


if __name__ == "__main__":
    unittest.main()
