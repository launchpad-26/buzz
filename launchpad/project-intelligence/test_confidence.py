"""Controls for confidence.py -- issue #211.

Hermetic: constructed Symbols, a real ProjectGraph/SemanticIndex built from
them, and a real in-memory ProjectMemory. No `rql`, no repo reads.

Run:  python3 -m unittest test_confidence
  or: python3 test_confidence.py
"""

from __future__ import annotations

import unittest

from confidence import assess
from graph import ProjectGraph
from memory import MemoryEntry, ProjectMemory
from semantic_index import SemanticIndex
from symbol import DefinedAt, Symbol

TARGET = "is_shared_gated_kind"
ABSENT = "no_such_symbol_anywhere"


def _symbol(qualified_name: str, calls: tuple[str, ...] = ()) -> Symbol:
    return Symbol(
        symbol_id=f"crates/buzz-core/src/kind.rs::{qualified_name}",
        kind="function",
        qualified_name=qualified_name,
        defined_at=DefinedAt(
            file="crates/buzz-core/src/kind.rs",
            start_line=219,
            end_line=221,
            temporal_state="WORKING",
        ),
        signature=f"pub fn {qualified_name}(kind: u32) -> bool",
        calls=calls,
    )


class AssessTest(unittest.TestCase):
    def setUp(self) -> None:
        self.symbols = [_symbol(TARGET, calls=("contains",))]
        self.graph = ProjectGraph.from_symbols(self.symbols)
        self.index = SemanticIndex.from_symbols(self.symbols)
        self.memory = ProjectMemory()

    def test_graph_and_memory_hits_report_confident_and_name_both(self) -> None:
        """STEP 5's first done-when."""
        self.memory.add(
            MemoryEntry(
                id="m1",
                entry_class="FACT",
                statement=f"{TARGET} gates shared kinds",
                evidence=("crates/buzz-core/src/kind.rs:219-221",),
            )
        )
        result = assess(TARGET, self.graph, self.index, self.memory)
        self.assertTrue(result.confident)
        self.assertIn("ProjectGraph", result.sources)
        self.assertIn("ProjectMemory", result.sources)

    def test_an_unknown_target_reports_no_confidence_and_names_all_three_empty(self) -> None:
        """STEP 5's second done-when."""
        result = assess(ABSENT, self.graph, self.index, self.memory)
        self.assertFalse(result.confident)
        self.assertEqual(result.sources, ())
        self.assertEqual(
            set(result.empty), {"ProjectGraph", "SemanticIndex", "ProjectMemory"}
        )

    def test_all_three_components_are_always_reported(self) -> None:
        """An omitted component reads as "not consulted". A caller must be able
        to tell "memory had no opinion" from "memory was never asked"."""
        for target in (TARGET, ABSENT):
            with self.subTest(target=target):
                result = assess(target, self.graph, self.index, self.memory)
                self.assertEqual(
                    [h.component for h in result.hits],
                    ["ProjectGraph", "SemanticIndex", "ProjectMemory"],
                )

    def test_confidence_is_never_reported_from_an_empty_component(self) -> None:
        """The rule the whole stage exists to hold: sources and empty partition
        the hits exactly, with no component in both and none in neither."""
        result = assess(TARGET, self.graph, self.index, self.memory)
        self.assertEqual(set(result.sources) & set(result.empty), set())
        self.assertEqual(
            set(result.sources) | set(result.empty),
            {h.component for h in result.hits},
        )

    def test_empty_memory_is_reported_empty_not_absent(self) -> None:
        result = assess(TARGET, self.graph, self.index, self.memory)
        self.assertIn("ProjectMemory", result.empty)
        memory_hit = next(h for h in result.hits if h.component == "ProjectMemory")
        self.assertIn("no stored entry mentions", memory_hit.detail)

    def test_team_knowledge_alone_is_enough_to_be_confident(self) -> None:
        """TEAM_KNOWLEDGE carries no evidence by design, so a stage that only
        counted evidence-bearing classes would silently discard the one class
        that exists for uncorroborated statements."""
        memory = ProjectMemory()
        memory.add(
            MemoryEntry(
                id="m2",
                entry_class="TEAM_KNOWLEDGE",
                statement=f"we are not adding kinds near {ABSENT} this milestone",
                provided_by="serina",
            )
        )
        result = assess(ABSENT, ProjectGraph.from_symbols([]), SemanticIndex.from_symbols([]), memory)
        self.assertTrue(result.confident)
        self.assertEqual(result.sources, ("ProjectMemory",))

    def test_a_real_indexed_symbol_with_empty_memory_is_not_confident(self) -> None:
        """The assertion whose absence let a High-severity regression ship.

        SemanticIndex.from_symbols adds an entry per symbol_id BY CONSTRUCTION,
        so a semantic hit is guaranteed for every symbol in the crate. When
        `confident` meant "any component found something", it was measured True
        for 439 of 439 buzz-core symbols -- making the corroboration stages
        unreachable in production once it became control flow.

        The design doc's own worked example is the authority: search_symbols
        FINDS UserRepository and the doc still records "confidence: none yet",
        because no ProjectMemory entry exists. Existence is not an answer.
        """
        result = assess(TARGET, self.graph, self.index, self.memory, self.symbols)
        self.assertTrue(result.knows_of_target, "the symbol should be known to the index")
        self.assertIn("ProjectGraph", result.sources)
        self.assertIn("SemanticIndex", result.sources)
        self.assertFalse(result.confident, "index presence is not a stored answer")

    def test_only_a_project_memory_hit_makes_it_confident(self) -> None:
        self.memory.add(
            MemoryEntry(
                id="m9",
                entry_class="FACT",
                statement=f"{TARGET} gates shared kinds",
                evidence=("crates/buzz-core/src/kind.rs:219-221",),
            )
        )
        self.assertTrue(assess(TARGET, self.graph, self.index, self.memory, self.symbols).confident)

    def test_knows_of_target_and_confident_are_different_questions(self) -> None:
        """Kept as separate properties on purpose: collapsing them is what
        caused the regression, so the distinction is asserted, not just named."""
        result = assess(TARGET, self.graph, self.index, self.memory, self.symbols)
        self.assertNotEqual(result.knows_of_target, result.confident)

    def test_semantic_index_is_found_via_symbol_id_not_qualified_name(self) -> None:
        """#210 keys symbol-level scopes on symbol_id on purpose -- one
        qualified_name can cover several symbols. An earlier version looked up
        the qualified_name directly and reported "SemanticIndex: empty" for
        symbols the index definitely held, making stage 1 under-report its own
        confidence. Found by running the live agent."""
        result = assess(TARGET, self.graph, self.index, self.memory, self.symbols)
        self.assertIn("SemanticIndex", result.sources)

    def test_omitting_the_symbol_list_reports_semantic_index_honestly(self) -> None:
        """Without the Symbol list there is no way to resolve qualified_name to
        symbol_id, and the detail must say that rather than imply the index was
        consulted and came back empty."""
        result = assess(TARGET, self.graph, self.index, self.memory)
        hit = next(h for h in result.hits if h.component == "SemanticIndex")
        self.assertFalse(hit.found)
        self.assertIn("no symbol in the index has qualified_name", hit.detail)

    def test_an_empty_target_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            assess("  ", self.graph, self.index, self.memory)


if __name__ == "__main__":
    unittest.main()
