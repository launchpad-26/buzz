"""Controls for graph.py -- issue #207.

Run:  python3 -m unittest test_graph    (from launchpad/project-intelligence/)
  or: python3 test_graph.py
"""

from __future__ import annotations

import unittest
from dataclasses import replace

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
        expected = [
            ("a", "b", "calls", "Symbol.calls[]"),
            ("b", "a", "called_by", "Symbol.called_by[]"),
            ("t", "a", "tested_by", "Symbol.tests[]"),
            ("a", "OTEL_SERVICE_NAME", "configured_by", "Symbol.config_dependencies[]"),
        ]
        self.assertEqual([(e.source, e.target, e.edge_type, e.evidence) for e in edges], expected)


def _sym(qualified_name: str, calls: tuple[str, ...] = (), called_by: tuple[str, ...] = ()) -> Symbol:
    return Symbol(
        symbol_id=f"file:///f.rs#symbol={qualified_name}",
        kind="function",
        qualified_name=qualified_name,
        defined_at=DefinedAt("f.rs", 1, 2, "WORKING"),
        signature=f"fn {qualified_name}()",
        calls=calls,
        called_by=called_by,
    )


class ProjectGraphFromSymbolsTest(unittest.TestCase):
    def test_calls_and_called_by_are_structural_inverses_not_double_counted(self) -> None:
        # Mirrors the real shape: #206 already resolves calls[] to qualified
        # names, and called_by[] is that same fact from the other side.
        # callee.called_by is populated here (not left empty) specifically so
        # an implementation that incorrectly reads BOTH calls[] and
        # called_by[] as independent sources -- doubling this edge from the
        # same underlying fact -- would fail this test. Caught in review: an
        # earlier version of this fixture left called_by empty, which could
        # not have caught that regression.
        caller = _sym("caller", calls=("callee",))
        callee = _sym("callee", called_by=("caller",))
        graph = ProjectGraph.from_symbols([caller, callee])

        self.assertEqual(len(graph.edges_from("caller", ("calls",))), 1)
        self.assertEqual(len(graph.edges_from("callee", ("called_by",))), 1)


class EdgeDirectionTest(unittest.TestCase):
    """Every edge_type's direction must read "source IS edge_type target" --
    e.g. "is_shared_gated_kind IS tested_by tests::foo", not the reverse. A
    first version of tested_by/documented_by got this backwards; caught only
    by reading the printed CLI output, not by any test, which is why this
    test exists now.
    """

    def test_tested_by_reads_symbol_is_tested_by_test(self) -> None:
        target = replace(_sym("is_shared_gated_kind"), tests=("tests::shared_gated_kinds_membership",))
        graph = ProjectGraph.from_symbols([target])

        edges = graph.edges_from("is_shared_gated_kind", ("tested_by",))
        self.assertEqual(len(edges), 1)
        self.assertEqual(edges[0].source, "is_shared_gated_kind")
        self.assertEqual(edges[0].target, "tests::shared_gated_kinds_membership")

    def test_documented_by_reads_symbol_is_documented_by_doc(self) -> None:
        target = replace(_sym("is_private_ip"), documentation_links=("ARCHITECTURE.md",))
        graph = ProjectGraph.from_symbols([target])

        edges = graph.edges_from("is_private_ip", ("documented_by",))
        self.assertEqual(len(edges), 1)
        self.assertEqual(edges[0].source, "is_private_ip")
        self.assertEqual(edges[0].target, "doc:ARCHITECTURE.md")

    def test_configured_by_reads_symbol_is_configured_by_key(self) -> None:
        target = replace(_sym("service_resource"), config_dependencies=("OTEL_SERVICE_NAME",))
        graph = ProjectGraph.from_symbols([target])

        edges = graph.edges_from("service_resource", ("configured_by",))
        self.assertEqual(len(edges), 1)
        self.assertEqual(edges[0].source, "service_resource")
        self.assertEqual(edges[0].target, "config:OTEL_SERVICE_NAME")


class SyntheticNodeNamespacingTest(unittest.TestCase):
    def test_config_key_and_symbol_with_same_name_do_not_collide(self) -> None:
        # A config key and a symbol could plausibly share literal text (e.g. a
        # symbol named the same as an env var it reads). Without namespacing,
        # both become the same graph node and a traversal could wander from
        # the config key straight into the symbol's own outgoing edges.
        symbol_named_like_a_key = _sym("RUST_LOG", calls=("downstream",))
        reader = replace(_sym("reader"), config_dependencies=("RUST_LOG",))
        graph = ProjectGraph.from_symbols([symbol_named_like_a_key, reader])

        # The config-key node is namespaced ("config:RUST_LOG"), so it has no
        # outgoing "calls" edges of its own -- those belong only to the real
        # symbol node ("RUST_LOG").
        self.assertEqual(graph.edges_from("config:RUST_LOG", ("calls",)), [])
        self.assertEqual(len(graph.edges_from("RUST_LOG", ("calls",))), 1)

    def test_unresolved_call_targets_do_not_create_a_false_reachability_hub(self) -> None:
        # Two unrelated symbols that both call the same unresolved external
        # name (e.g. a std-lib/other-crate function #206 couldn't resolve,
        # like "contains") must not become falsely reachable from each other.
        # Before this fix, the bare unresolved name became a shared node, and
        # the inverse "called_by" edge fanned every caller of that name into
        # each other -- reproduced directly: reachable() with ("calls",
        # "called_by") reported one caller reachable from the other.
        symbol_a = _sym("moduleA::check_thing", calls=("contains",))
        symbol_b = _sym("moduleB::totally_unrelated_thing", calls=("contains",))
        graph = ProjectGraph.from_symbols([symbol_a, symbol_b])

        result = reachable(graph, "moduleA::check_thing", ("calls", "called_by"), max_hops=2)
        nodes = [r.node for r in result]

        self.assertIn("extern:contains", nodes)
        self.assertNotIn("moduleB::totally_unrelated_thing", nodes)
        # The synthetic external node is a pure sink -- no "called_by" edges
        # fan back out of it, unlike a real resolved symbol.
        self.assertEqual(graph.edges_from("extern:contains", ("called_by",)), [])


class ReachableRejectsInvalidBoundsTest(unittest.TestCase):
    def test_negative_max_hops_is_rejected(self) -> None:
        graph = ProjectGraph.from_symbols([_sym("a", calls=("b",))])
        with self.assertRaises(ValueError):
            reachable(graph, "a", ("calls",), max_hops=-1)

    def test_zero_max_hops_finds_nothing(self) -> None:
        graph = ProjectGraph.from_symbols([_sym("a", calls=("b",))])
        self.assertEqual(reachable(graph, "a", ("calls",), max_hops=0), [])


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
