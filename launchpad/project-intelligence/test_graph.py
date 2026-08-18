"""Controls for graph.py -- issue #207.

Run:  python3 -m unittest test_graph    (from launchpad/project-intelligence/)
  or: python3 test_graph.py
"""

from __future__ import annotations

import unittest

from graph import Edge, ProjectGraph, reachable
from symbol import DefinedAt, Symbol


class EdgeFieldsTest(unittest.TestCase):
    def test_constructs_at_least_four_distinct_edge_types(self) -> None:
        edges = [
            Edge(source="a", target="b", edge_type="calls", evidence="Symbol.calls[]"),
            Edge(source="b", target="a", edge_type="called_by", evidence="Symbol.called_by[]"),
            Edge(source="t", target="a", edge_type="tested_by", evidence="Symbol.tests[]"),
            Edge(
                source="a",
                target="OTEL_SERVICE_NAME",
                edge_type="configured_by",
                evidence="Symbol.config_dependencies[]",
            ),
        ]
        self.assertEqual({e.edge_type for e in edges}, {"calls", "called_by", "tested_by", "configured_by"})
        self.assertEqual(edges[0].source, "a")
        self.assertEqual(edges[0].target, "b")
        self.assertEqual(edges[0].evidence, "Symbol.calls[]")


def _sym(qualified_name: str, calls: tuple[str, ...] = ()) -> Symbol:
    return Symbol(
        symbol_id=f"file:///f.rs#symbol={qualified_name}",
        kind="function",
        qualified_name=qualified_name,
        defined_at=DefinedAt("f.rs", 1, 2, "WORKING"),
        signature=f"fn {qualified_name}()",
        calls=calls,
    )


class ProjectGraphFromSymbolsTest(unittest.TestCase):
    def test_calls_and_called_by_are_structural_inverses_not_double_counted(self) -> None:
        # Mirrors the real shape: #206 already resolves calls[] to qualified
        # names, and called_by[] is that same fact from the other side --
        # ProjectGraph must not read both and double the edge.
        caller = _sym("caller", calls=("callee",))
        callee = _sym("callee", calls=(), )
        graph = ProjectGraph.from_symbols([caller, callee])

        self.assertEqual(len(graph.edges_from("caller", ("calls",))), 1)
        self.assertEqual(len(graph.edges_from("callee", ("called_by",))), 1)


class ReachableTest(unittest.TestCase):
    """Fixture mirrors the real 2-hop chain verified in the repo (see #207's
    plan): tests::is_unshared_gated_event_author_always_allowed ->
    is_unshared_gated_event -> is_shared_gated_kind. Kept as a hermetic
    fixture rather than a live rql-dependent test, same reasoning as
    test_indexer.py.
    """

    def _real_chain_graph(self) -> ProjectGraph:
        test_fn = _sym("tests::is_unshared_gated_event_author_always_allowed", calls=("is_unshared_gated_event",))
        middle = _sym("is_unshared_gated_event", calls=("is_shared_gated_kind",))
        target = _sym("is_shared_gated_kind", calls=("contains",))
        return ProjectGraph.from_symbols([test_fn, middle, target])

    def test_two_hop_chain_matches_the_verified_real_example(self) -> None:
        graph = self._real_chain_graph()
        result = reachable(
            graph, "tests::is_unshared_gated_event_author_always_allowed", ("calls",), max_hops=2
        )
        by_node = {r.node: r for r in result}

        self.assertIn("is_unshared_gated_event", by_node)
        self.assertEqual(by_node["is_unshared_gated_event"].hop, 1)
        self.assertIn("is_shared_gated_kind", by_node)
        self.assertEqual(by_node["is_shared_gated_kind"].hop, 2)

    def test_max_hops_bounds_the_search(self) -> None:
        graph = self._real_chain_graph()
        result = reachable(
            graph, "tests::is_unshared_gated_event_author_always_allowed", ("calls",), max_hops=1
        )
        self.assertEqual([r.node for r in result], ["is_unshared_gated_event"])

    def test_start_node_itself_is_never_returned(self) -> None:
        graph = self._real_chain_graph()
        result = reachable(
            graph, "tests::is_unshared_gated_event_author_always_allowed", ("calls",), max_hops=2
        )
        self.assertNotIn("tests::is_unshared_gated_event_author_always_allowed", [r.node for r in result])

    def test_unknown_start_node_returns_empty_not_an_error(self) -> None:
        graph = self._real_chain_graph()
        result = reachable(graph, "no_such_symbol", ("calls",), max_hops=2)
        self.assertEqual(result, [])


if __name__ == "__main__":
    unittest.main()
