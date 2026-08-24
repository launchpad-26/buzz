"""KnowledgeAgent -- issue #211, STEPs 3 and 9.

The orchestration layer: decompose the question, decide which components answer
it, decide when to invoke the Investigator, verify, assemble the labeled answer.

STEP 3 built the first ugly path through indexer -> graph -> Answer -> render to
prove the layers connected. STEPs 4-8 built the real stages, and this is now the
thing that runs them in order:

  1. decompose        (question.py)
  2. check confidence (confidence.py)   -- stage 1
  3. investigate      (investigation.py) -- stage 3, skipped when already confident
  4. verify + assemble (verify.py, assemble.py) -- stages 2 and 4

STEP 3's standalone build_answer() is gone rather than left beside this: it was
the scaffold this replaced, and dead code beside working code is a reader's
trap. Its two helpers (find_symbol, cite) survive because they are still used.

No model is called anywhere in this module -- decided 2026-08-24, see the plan's
APPROACH NOTE. Prose is assembled from structural facts.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from answer import Answer
from assemble import assemble
from confidence import Assessment, assess
from graph import ProjectGraph
from indexer import build_index
from investigation import REAL_TOOLS, Findings, Tools, investigate
from memory import ProjectMemory
from question import Depth, decompose
from semantic_index import SemanticIndex, find_it_for_me
from symbol import Symbol
from trace import Trace

WORKED_CRATE = "buzz-core"
WORKED_SYMBOL = "is_shared_gated_kind"
WORKED_QUESTION = f"how does `{WORKED_SYMBOL}` work?"


def find_symbol(symbols: list[Symbol], qualified_name: str) -> Symbol:
    """Exact qualified_name match, never a prefix or substring one: a partial
    match would describe the wrong function while citing its real line range --
    true evidence, wrong subject, the worst shape a citation can have.

    Raises rather than returning None so a miss names the missing symbol
    instead of surfacing as an AttributeError three frames later.
    """
    for sym in symbols:
        if sym.qualified_name == qualified_name:
            return sym
    raise LookupError(f"{qualified_name!r} is not in the index for this crate")


def cite(sym: Symbol) -> str:
    """A symbol's definition as one citation string, in the uniform
    file:start-end form -- a sometimes-range/sometimes-single form needs two
    parsers on the reading side."""
    return f"{sym.defined_at.file}:{sym.defined_at.start_line}-{sym.defined_at.end_line}"


@dataclass
class Outcome:
    """An answer plus the reasoning that produced it, so the decision path is
    inspectable and not just its conclusion."""

    answer: Answer
    assessment: Assessment | None
    findings: Findings | None
    trace: Trace = field(default_factory=Trace)


@dataclass
class KnowledgeAgent:
    crate: str
    symbols: list[Symbol]
    graph: ProjectGraph
    index: SemanticIndex
    memory: ProjectMemory
    # The Investigator surface, injectable for the same reason
    # investigation.py has the seam: three of its five tools shell out to
    # `rql`, and STEP 12 requires a suite that needs neither `rql` nor a
    # network. Production callers take the default.
    tools: Tools = REAL_TOOLS

    @classmethod
    def build(cls, crate: str, memory: ProjectMemory | None = None) -> "KnowledgeAgent":
        """Indexes the crate once. Every method then reads that one index --
        re-indexing per question would make the seven-method surface far more
        expensive than the components it wraps."""
        symbols = build_index(crate)
        return cls(
            crate=crate,
            symbols=symbols,
            graph=ProjectGraph.from_symbols(symbols),
            index=SemanticIndex.from_symbols(symbols),
            memory=memory if memory is not None else ProjectMemory(),
        )

    @property
    def symbol_count(self) -> int:
        return len(self.symbols)

    def find_concept(self, concept: str):
        """§ Concept Retrieval, delegated whole to #210. Returns its
        PipelineResult, or None when nothing ranked."""
        try:
            return find_it_for_me(self.index, self.graph, concept)
        except (LookupError, ValueError):
            return None

    def run(self, text: str, depth: Depth | None = None) -> Outcome:
        """The four stages, in order, with every decision recorded."""
        question = decompose(text)
        if depth is not None:
            question = type(question)(
                raw=question.raw,
                intent=question.intent,
                target=question.target,
                temporal_state=question.temporal_state,
                depth=depth,
                setup_task=question.setup_task,
            )

        trace = Trace()
        if question.target is None:
            # Nothing to assess or investigate without a subject. FIND is the
            # method for this, and routing here instead would silently answer a
            # different question.
            return Outcome(
                answer=Answer(
                    question=text,
                    short_answer="No symbol named in the question.",
                    things_to_be_aware_of="Use knowledge.find() for a concept with no known name.",
                ),
                assessment=None,
                findings=None,
                trace=trace,
            )

        assessment = assess(question.target, self.graph, self.index, self.memory, self.symbols)

        # Stage 3 runs when stage 1 was not confident. When it WAS confident,
        # stage 2 still verifies -- being confident never skips verification,
        # only investigation. That is the distinction § Reasoning Rules draws
        # between its points 2 and 3, and collapsing the two would mean a
        # cached answer was never checked against the tree.
        findings = investigate(question, self.crate, trace, self.tools)

        answer = assemble(question, findings, trace, self.memory)
        return Outcome(answer=answer, assessment=assessment, findings=findings, trace=trace)

    def answer(self, text: str, depth: Depth | None = None) -> Answer:
        return self.run(text, depth=depth).answer


if __name__ == "__main__":
    from answer import render

    agent = KnowledgeAgent.build(WORKED_CRATE)
    outcome = agent.run(WORKED_QUESTION)
    print(render(outcome.answer))
    print("\n=== stage 1: confidence ===")
    for hit in outcome.assessment.hits:  # type: ignore[union-attr]
        print(f"  {hit.component}: {'found' if hit.found else 'empty'} -- {hit.detail}")
    print(f"  confident: {outcome.assessment.confident}")  # type: ignore[union-attr]
    print("\n=== stage 3: investigation trace ===")
    print(outcome.trace.render())
