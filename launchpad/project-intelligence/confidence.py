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
    def confident(self) -> bool:
        """True only if some component actually found something. Derived, never
        stored -- a stored flag can disagree with the hits it summarises, and
        this is the one value the investigation decision turns on."""
        return any(h.found for h in self.hits)

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
    matched = [
        entry
        for entry_class in MEMORY_CLASSES
        for entry in memory.query_by_class(entry_class)
        if target in entry.statement
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
