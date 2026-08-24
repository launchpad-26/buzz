"""Controls for knowledge_agent.py -- issue #211.

Hermetic: the pure helpers only, on constructed Symbol fixtures. build_answer()
shells out to `rql` through indexer.build_index(), so it is verified live and
evidenced in the PR body instead -- the same boundary test_indexer.py's own
docstring draws for this directory.

Run:  python3 -m unittest test_knowledge_agent
  or: python3 test_knowledge_agent.py
"""

from __future__ import annotations

import unittest

from knowledge_agent import cite, find_symbol
from symbol import DefinedAt, Symbol


def _symbol(qualified_name: str, start: int = 219, end: int = 221) -> Symbol:
    """Field values copied from the real buzz-core symbol this task's live demo
    uses, so the fixture and the demo cannot describe different things."""
    return Symbol(
        symbol_id=f"crates/buzz-core/src/kind.rs::{qualified_name}",
        kind="function",
        qualified_name=qualified_name,
        defined_at=DefinedAt(
            file="crates/buzz-core/src/kind.rs",
            start_line=start,
            end_line=end,
            temporal_state="WORKING",
        ),
        signature=f"pub fn {qualified_name}(kind: u32) -> bool",
    )


class FindSymbolTest(unittest.TestCase):
    def test_returns_the_exact_qualified_name_match(self) -> None:
        wanted = _symbol("is_shared_gated_kind")
        symbols = [_symbol("is_unshared_gated_event"), wanted]
        self.assertIs(find_symbol(symbols, "is_shared_gated_kind"), wanted)

    def test_a_miss_raises_rather_than_returning_none(self) -> None:
        """A None here would flow into build_answer as an AttributeError three
        frames later, naming a field instead of the missing symbol."""
        with self.assertRaises(LookupError) as caught:
            find_symbol([_symbol("is_shared_gated_kind")], "no_such_symbol")
        self.assertIn("no_such_symbol", str(caught.exception))

    def test_matching_is_not_a_prefix_or_substring_match(self) -> None:
        """`is_shared_gated_kind` must not satisfy a lookup for
        `is_shared_gated_kind_v2`, or an answer would describe the wrong
        function while citing its real line range -- true evidence, wrong
        subject, which is the worst shape a citation can have."""
        with self.assertRaises(LookupError):
            find_symbol([_symbol("is_shared_gated_kind")], "is_shared_gated_kind_v2")

    def test_an_empty_index_raises(self) -> None:
        with self.assertRaises(LookupError):
            find_symbol([], "is_shared_gated_kind")


class CiteTest(unittest.TestCase):
    def test_renders_file_colon_start_dash_end(self) -> None:
        self.assertEqual(
            cite(_symbol("is_shared_gated_kind")), "crates/buzz-core/src/kind.rs:219-221"
        )

    def test_a_single_line_symbol_still_renders_a_range(self) -> None:
        """Uniform shape matters: the done-when opens these by parsing them, and
        a sometimes-range/sometimes-single form needs two parsers."""
        self.assertEqual(
            cite(_symbol("one_liner", start=42, end=42)),
            "crates/buzz-core/src/kind.rs:42-42",
        )


if __name__ == "__main__":
    unittest.main()
