"""Decision logic stage 1 -- issue #211, STEP 5.

"Check confidence first": query ProjectGraph, SemanticIndex and ProjectMemory
for what is already known about a target, and report which components answered
and which were empty.

The reporting is the point. A component that found nothing must be named as
empty rather than omitted, because an omitted component reads as "not
consulted" and a caller cannot tell the difference between "memory has no
opinion" and "memory was never asked". § Reasoning Rules puts this first for a
reason: everything downstream decides whether to investigate based on it.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from graph import ProjectGraph
from memory import ProjectMemory
from semantic_index import SemanticIndex
from symbol import Symbol

MEMORY_CLASSES = ("FACT", "INFERENCE", "TEAM_KNOWLEDGE")


@dataclass(frozen=True)
class ComponentHit:
    component: str
    found: bool
    detail: str


@dataclass(frozen=True)
class Assessment:
    target: str
    hits: tuple[ComponentHit, ...]

    @property
    def knows_of_target(self) -> bool:
        """Some component has heard of the target. Reporting only -- NOT the
        gate. Existence is not an answer."""
        return any(h.found for h in self.hits)

    @property
    def confident(self) -> bool:
        """True only when a PRIOR ANSWER is stored -- i.e. ProjectMemory has an
        entry about the target. Derived, never stored.

        This was `any(h.found for h in self.hits)` until 2026-08-24, and that
        was wrong in a way only measurement exposed. SemanticIndex.from_symbols
        adds one ConceptEntry per symbol_id BY CONSTRUCTION, so a semantic hit
        is guaranteed for every symbol in the crate. Once the caller started
        using this value as control flow, the consequence was measured:

            distinct qualified_names in buzz-core: 439
            not confident:                           0

        Zero of 439. The corroboration stages became unreachable in production,
        and knowledge.explain() silently dropped a FACT claim carrying eight
        real file:line citations plus its whole `Relevant flow` section.

        The design doc settles what the predicate should be. Step 1 is "Query
        ProjectGraph / SemanticIndex / ProjectMemory for an existing ANSWER",
        and its own worked example is explicit: `search_symbols("UserRepository")`
        FINDS the symbol and the doc still records "no existing ProjectMemory
        entry -- confidence: none yet." Existence in an index is not an answer;
        a stored claim is.

        Consequence worth stating plainly: ProjectMemory does not persist
        between runs (#209), so on a fresh process this is False for every
        target and the full investigation always runs. That is the safe
        direction, and the gate is real and tested rather than decorative -- it
        fires the moment a stored answer exists, which is what #209 will make
        durable.
        """
        return any(h.found for h in self.hits if h.component == "ProjectMemory")

    @property
    def sources(self) -> tuple[str, ...]:
        return tuple(h.component for h in self.hits if h.found)

    @property
    def empty(self) -> tuple[str, ...]:
        return tuple(h.component for h in self.hits if not h.found)


def _graph_hit(graph: ProjectGraph, target: str) -> ComponentHit:
    edges = graph.edges_from(target)
    return ComponentHit(
        component="ProjectGraph",
        found=bool(edges),
        detail=(
            f"{len(edges)} outgoing edge(s): {', '.join(sorted({e.edge_type for e in edges}))}"
            if edges
            else "no outgoing edges -- the target is not a node this graph knows"
        ),
    )


def _semantic_hit(index: SemanticIndex, target: str, symbols: Sequence[Symbol]) -> ComponentHit:
    """Looks up by symbol_id, resolved from the qualified_name via the Symbol
    list -- NOT by qualified_name directly.

    #210 keys symbol-level ConceptEntry scopes on symbol_id on purpose: one
    qualified_name can cover several symbols in a real crate, so it is not a
    unique key. An earlier version here called index.get(qualified_name) and so
    reported "SemanticIndex: empty" for symbols the index definitely held --
    a false negative that made stage 1 under-report its own confidence. Found
    by running the live agent, not by reading.
    """
    ids = [s.symbol_id for s in symbols if s.qualified_name == target]
    hits = [i for i in ids if index.get(i) is not None]
    return ComponentHit(
        component="SemanticIndex",
        found=bool(hits),
        detail=(
            f"{len(hits)} concept entry/entries for symbol_id(s) of {target!r}"
            if hits
            else (
                f"no concept entry for any symbol_id of {target!r}"
                if ids
                else f"no symbol in the index has qualified_name {target!r}"
            )
        ),
    )


def _memory_hit(memory: ProjectMemory, target: str) -> ComponentHit:
    """Substring match on the statement, because #209's store offers no
    query-by-subject -- query_by_class is its only query. Crude on purpose and
    stated here rather than hidden: a target whose name appears inside a longer
    identifier will match, and a stored entry about the same subject phrased
    without the identifier will not. Narrowing this needs an indexed subject
    field on MemoryEntry, which is #209's to add, not this task's to bolt on.
    """
    # `superseded_by is None` is the control-flow half of a filter this branch
    # already applied to both CONSUMERS -- assemble._team_knowledge and
    # knowledge.conventions -- each with its own regression test. This site was
    # missed, and it is the one that matters most: a retracted entry made stage 1
    # confident, which SKIPPED find_references and search_text, so withdrawn
    # knowledge silently changed the investigation while staying invisible in the
    # answer. Found by the review panel, which called out the asymmetry directly.
    #
    # Fixing the same class in two places and not looking for the third is the
    # mistake, not the missing line.
    matched = [
        entry
        for entry_class in MEMORY_CLASSES
        for entry in memory.query_by_class(entry_class)
        if entry.superseded_by is None and target in entry.statement
    ]
    classes = sorted({e.entry_class for e in matched})
    return ComponentHit(
        component="ProjectMemory",
        found=bool(matched),
        detail=(
            f"{len(matched)} entry/entries mentioning {target!r} ({', '.join(classes)})"
            if matched
            else f"no stored entry mentions {target!r}"
        ),
    )


def assess(
    target: str,
    graph: ProjectGraph,
    index: SemanticIndex,
    memory: ProjectMemory,
    symbols: Sequence[Symbol] = (),
) -> Assessment:
    """All three components are always consulted, in a fixed order, so the
    report is the same shape whether anything was found or not."""
    if not isinstance(target, str) or not target.strip():
        raise ValueError(f"target must be a non-empty string, got {target!r}")
    return Assessment(
        target=target,
        hits=(
            _graph_hit(graph, target),
            _semantic_hit(index, target, symbols),
            _memory_hit(memory, target),
        ),
    )
