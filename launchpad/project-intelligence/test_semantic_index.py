"""Controls for semantic_index.py -- issue #210.

Run:  python3 -m unittest test_semantic_index    (from launchpad/project-intelligence/)
  or: python3 test_semantic_index.py
"""

from __future__ import annotations

import unittest

from semantic_index import ConceptEntry, SemanticIndex


class ConceptEntryStoreTest(unittest.TestCase):
    def test_add_and_get_round_trip_all_three_fields(self) -> None:
        index = SemanticIndex()
        entry = ConceptEntry(scope="is_shared_gated_kind", embedding=(("kind", 0.5), ("gated", 0.5)), summary="a gloss")
        index.add(entry)

        retrieved = index.get("is_shared_gated_kind")
        self.assertEqual(retrieved.scope, entry.scope)
        self.assertEqual(retrieved.embedding, entry.embedding)
        self.assertEqual(retrieved.summary, entry.summary)

    def test_get_returns_none_for_an_unknown_scope(self) -> None:
        index = SemanticIndex()
        self.assertIsNone(index.get("no-such-scope"))

    def test_add_rejects_a_duplicate_scope(self) -> None:
        index = SemanticIndex()
        index.add(ConceptEntry(scope="s1", embedding=(), summary="a"))
        with self.assertRaises(ValueError):
            index.add(ConceptEntry(scope="s1", embedding=(), summary="b"))


if __name__ == "__main__":
    unittest.main()
