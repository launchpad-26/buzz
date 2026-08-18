"""ProjectGraph -- issue #207, STEP 1.

Typed, directional edges over #206's Symbol records, per
launchpad/Research/project-intelligence-layer-design.md (Data Model, item 2).

This task implements 4 of the design doc's 8 edge types -- the ones #206's Symbol
schema already produces directly (calls/called_by, tested_by, configured_by,
documented_by). imports, deployed_by, owns, and depends_on need extraction #206
does not currently do and are left out (see #207's plan, OPEN/LEFT OUT).
"""

from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass
from typing import Literal

from symbol import Symbol

EdgeType = Literal[
    "imports",
    "calls",
    "called_by",
    "configured_by",
    "tested_by",
    "documented_by",
    "deployed_by",
    "owns",
    "depends_on",
]


@dataclass(frozen=True)
class Edge:
    source: str  # symbol_id or a synthetic node id (e.g. a config key, a doc path)
    target: str
    edge_type: EdgeType
    evidence: str  # what produced this edge, e.g. "Symbol.calls[]", "Symbol.tests[]"


class ProjectGraph:
    """STEP 2: materializes 4 of the design doc's 8 edge types from a list of
    #206 Symbol records -- the ones already present on each Symbol
    (calls/called_by, tests[], config_dependencies[], documentation_links[]).
    Nodes are addressed by qualified_name (matching #206's own resolved
    representation for calls/called_by); config keys and doc paths are
    synthetic node ids with no corresponding Symbol.
    """

    def __init__(self) -> None:
        self._edges: list[Edge] = []
        self._by_source: dict[str, list[Edge]] = defaultdict(list)

    @classmethod
    def from_symbols(cls, symbols: list[Symbol]) -> "ProjectGraph":
        graph = cls()
        for sym in symbols:
            for target in sym.calls:
                # "called_by" is derived as this edge's own structural inverse, not
                # re-read from Symbol.called_by[] -- that field is itself computed
                # from calls[] in #206 (with_called_by()), so treating both as
                # independent sources would double the edge from the same fact.
                graph._add(Edge(sym.qualified_name, target, "calls", "Symbol.calls[]"))
                graph._add(Edge(target, sym.qualified_name, "called_by", "Symbol.calls[] (inverse)"))
            for test in sym.tests:
                # Edge direction reads "sym IS tested_by test" -- same convention
                # as configured_by below (symbol as source, describing itself),
                # not "test is tested_by sym", which a first version of this
                # method got backwards.
                graph._add(Edge(sym.qualified_name, test, "tested_by", "Symbol.tests[]"))
            for key in sym.config_dependencies:
                graph._add(Edge(sym.qualified_name, key, "configured_by", "Symbol.config_dependencies[]"))
            for doc in sym.documentation_links:
                graph._add(Edge(sym.qualified_name, doc, "documented_by", "Symbol.documentation_links[]"))
        return graph

    def _add(self, edge: Edge) -> None:
        self._edges.append(edge)
        self._by_source[edge.source].append(edge)

    def edges_from(self, node: str, edge_types: tuple[EdgeType, ...] | None = None) -> list[Edge]:
        edges = self._by_source.get(node, [])
        if edge_types is None:
            return list(edges)
        return [e for e in edges if e.edge_type in edge_types]


@dataclass(frozen=True)
class Reachable:
    node: str
    hop: int
    path: tuple[str, ...]  # the node sequence from the start, inclusive of both ends


def reachable(
    graph: ProjectGraph,
    from_node: str,
    edge_types: tuple[EdgeType, ...],
    max_hops: int,
) -> list[Reachable]:
    """STEP 3: BFS over the materialized edges, filtered by edge_types, up to
    max_hops. Returns every node found, nearest first; the start node itself
    is never included (hop 0 would be the trivial, uninteresting case).
    """
    visited = {from_node}
    frontier: deque[tuple[str, int, tuple[str, ...]]] = deque([(from_node, 0, (from_node,))])
    found: list[Reachable] = []

    while frontier:
        node, hop, path = frontier.popleft()
        if hop == max_hops:
            continue
        for edge in graph.edges_from(node, edge_types):
            if edge.target in visited:
                continue
            visited.add(edge.target)
            new_path = path + (edge.target,)
            found.append(Reachable(edge.target, hop + 1, new_path))
            frontier.append((edge.target, hop + 1, new_path))

    return found


def _demo_negative_case(graph: ProjectGraph) -> None:
    """STEP 5: a vague, terminology-free question has no symbol_id to start
    from, so reachable() is not the right tool for it at all -- this graph
    answers "what's connected to X", never "what handles kind gating". That
    question is #210's (SemanticIndex) job, out of scope here.
    """
    vague_description = "the code that checks kind gating"
    result = reachable(graph, vague_description, ("calls",), max_hops=2)
    print(f"Query: reachable(graph, {vague_description!r}, ...)")
    print(f"Result: {result} -- empty, because '{vague_description}' is not a symbol_id")
    print("this graph knows about. Resolving a description to a starting symbol is")
    print("#210's (SemanticIndex) job, not this graph's -- confirming the boundary.")


if __name__ == "__main__":
    import sys as _sys

    from indexer import build_index

    crate = _sys.argv[1] if len(_sys.argv) > 1 else "buzz-core"
    graph = ProjectGraph.from_symbols(build_index(crate))

    print(f"=== STEP 6: every edge for one chosen real symbol ===\n")
    node = "is_shared_gated_kind"
    edges = graph.edges_from(node)
    if not edges:
        print(f"(no edges found from {node!r} in crates/{crate})")
    for e in edges:
        print(f"{e.source} --{e.edge_type}--> {e.target}  ({e.evidence})")

    print(f"\n=== STEP 4: a 2-hop relationship the flat Symbol record alone cannot show ===\n")
    two_hop_start = "tests::is_unshared_gated_event_author_always_allowed"
    result = reachable(graph, two_hop_start, ("calls",), max_hops=2)
    hop2 = [r for r in result if r.node == node]
    print(f"reachable({two_hop_start!r}, max_hops=2) includes {node!r}: {bool(hop2)}")
    if hop2:
        print(f"  path: {' -> '.join(hop2[0].path)}")

    print(f"\n=== STEP 5: the negative case -- vague questions need a starting symbol ===\n")
    _demo_negative_case(graph)
