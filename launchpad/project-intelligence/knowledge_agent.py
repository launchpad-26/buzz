"""KnowledgeAgent -- issue #211, STEP 3.

The first real answer, end to end: index a real crate, resolve one real symbol,
traverse the real graph, and render the design doc's six-section format from
what was actually found.

Deliberately narrow at this step -- one hardcoded question, no question
decomposition, no confidence check, no investigation loop. Those are STEPs 4-8.
What this step buys is a working path through every layer (indexer -> graph ->
Answer -> render) before any of the reasoning is built on top of it, so the
reasoning has something real to improve rather than parts to assemble.

No model is called here or anywhere in this module -- decided 2026-08-24, see
the plan's APPROACH NOTE. Prose is assembled from structural facts.
"""

from __future__ import annotations

from answer import Answer, Claim
from graph import ProjectGraph, reachable
from indexer import build_index
from symbol import Symbol

WORKED_CRATE = "buzz-core"
WORKED_SYMBOL = "is_shared_gated_kind"
WORKED_QUESTION = f"how does {WORKED_SYMBOL} work?"


def find_symbol(symbols: list[Symbol], qualified_name: str) -> Symbol:
    """Exact qualified_name match. Raises rather than returning None: at this
    step the symbol is hardcoded, so a miss is a broken assumption about the
    index, not a runtime case to degrade for."""
    for sym in symbols:
        if sym.qualified_name == qualified_name:
            return sym
    raise LookupError(f"{qualified_name!r} is not in the index for this crate")


def cite(sym: Symbol) -> str:
    """A symbol's definition as one citation string, in the file:start-end form
    the done-when checks by opening."""
    return f"{sym.defined_at.file}:{sym.defined_at.start_line}-{sym.defined_at.end_line}"


def build_answer(crate: str, qualified_name: str, question: str) -> Answer:
    symbols = build_index(crate)
    graph = ProjectGraph.from_symbols(symbols)
    sym = find_symbol(symbols, qualified_name)

    callees = [e.target for e in graph.edges_from(qualified_name, ("calls",))]
    callers = [e.target for e in graph.edges_from(qualified_name, ("called_by",))]
    tests = [e.target for e in graph.edges_from(qualified_name, ("tested_by",))]
    downstream = reachable(graph, qualified_name, ("calls",), max_hops=2)

    claims = [
        Claim(
            statement=f"{qualified_name} is defined as {sym.signature}",
            entry_class="FACT",
            evidence=(cite(sym),),
            temporal_state=sym.defined_at.temporal_state,
        )
    ]

    # An inference the return type supports but nothing states: a bool-returning
    # function is a decision point, not a transformation. The signature is the
    # whole evidence, and the confidence carries the rest.
    #
    # An earlier version also cited "no doc or test states the intent". Running
    # the done-when disproved it -- kind.rs:1079-1081 is a comment inside this
    # symbol's own test explaining exactly why one kind is excluded. Asserting
    # an absence nobody had looked for is the failure this layer exists to
    # prevent, so the claim now rests only on what was actually read.
    if sym.signature.rstrip().endswith("bool"):
        claims.append(
            Claim(
                statement=f"{qualified_name} is a decision point rather than a transformation",
                entry_class="INFERENCE",
                evidence=(f"returns bool -- {cite(sym)}",),
                confidence=0.7,
            )
        )

    if tests:
        # Cites the graph edge, NOT the symbol's own file:line. An earlier
        # version cited cite(sym) here, which pointed a claim about tests at
        # the definition's line range -- a citation that resolves but does not
        # say what the claim says. The test in this repo's case actually lives
        # ~850 lines away, so the mis-citation was invisible to any check that
        # only asked whether the path existed.
        claims.append(
            Claim(
                statement=f"{len(tests)} test(s) reference it: {', '.join(sorted(tests))}",
                entry_class="FACT",
                evidence=tuple(f"tested_by edge {qualified_name} -> {t} (Symbol.tests[])" for t in sorted(tests)),
            )
        )
    else:
        # Absence is a finding, and it is an observed one -- the index carries
        # no tested_by edge -- so it is a FACT about the index, phrased as such
        # rather than as a claim that no test exists anywhere.
        claims.append(
            Claim(
                statement="the index carries no test reference for it",
                entry_class="FACT",
                evidence=(f"no tested_by edge from {qualified_name} in the ProjectGraph",),
            )
        )

    flow = ""
    if downstream:
        deepest = max(downstream, key=lambda r: r.hop)
        flow = f"{' -> '.join(deepest.path)}  ({deepest.hop} hop(s))"

    return Answer(
        question=question,
        short_answer=(
            f"A {sym.kind} in {sym.defined_at.file}"
            + (f", called by {', '.join(sorted(callers))}" if callers else ", with no callers in this crate")
            + "."
        ),
        how_it_works=(
            f"{qualified_name} calls {', '.join(sorted(callees))}."
            if callees
            else f"{qualified_name} calls nothing else -- it decides from its arguments alone."
        ),
        relevant_flow=flow,
        important_files=(sym.defined_at.file,),
        things_to_be_aware_of=(
            f"Reached in {len(downstream)} node(s) within 2 call hops."
            if downstream
            else "Nothing downstream within 2 call hops, so a change here is contained to its callers."
        ),
        claims=tuple(claims),
    )


if __name__ == "__main__":
    from answer import render

    print(render(build_answer(WORKED_CRATE, WORKED_SYMBOL, WORKED_QUESTION)))
