"""Controls for semantic_index.py -- issue #210.

Run:  python3 -m unittest test_semantic_index    (from launchpad/project-intelligence/)
  or: python3 test_semantic_index.py
"""

from __future__ import annotations

import unittest

from semantic_index import ConceptEntry, SemanticIndex, cosine_similarity, embed_text, summarize_symbol, tokenize
from symbol import DefinedAt, Symbol

# A real Symbol from buzz-core, constructed by hand from fields already
# cross-checked against the live repo in #206/#207 (crates/buzz-core/src/kind.rs)
# -- not built via indexer.build_index(), which shells out to rql and is
# deliberately kept out of this committed, hermetic suite (same reasoning as
# test_indexer.py/test_graph.py).
_IS_SHARED_GATED_KIND = Symbol(
    symbol_id="crates/buzz-core/src/kind.rs::is_shared_gated_kind",
    kind="function",
    qualified_name="is_shared_gated_kind",
    defined_at=DefinedAt(file="crates/buzz-core/src/kind.rs", start_line=219, end_line=221, temporal_state="WORKING"),
    signature="pub fn is_shared_gated_kind(kind: u32) -> bool",
    calls=("contains",),
    called_by=("is_unshared_gated_event", "tests::shared_gated_kinds_membership"),
    tests=("tests::shared_gated_kinds_membership",),
    documentation_links=("ARCHITECTURE.md",),
)


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


class SummarizeSymbolTest(unittest.TestCase):
    def test_includes_the_qualified_name_and_a_real_test(self) -> None:
        summary = summarize_symbol(_IS_SHARED_GATED_KIND)
        self.assertIn("is_shared_gated_kind", summary)
        self.assertIn("tests::shared_gated_kinds_membership", summary)  # a real entry from tests[]

    def test_includes_signature_and_calls(self) -> None:
        summary = summarize_symbol(_IS_SHARED_GATED_KIND)
        self.assertIn("pub fn is_shared_gated_kind(kind: u32) -> bool", summary)
        self.assertIn("contains", summary)

    def test_omits_empty_fields_rather_than_printing_them_blank(self) -> None:
        bare = Symbol(
            symbol_id="x",
            kind="function",
            qualified_name="bare_fn",
            defined_at=DefinedAt(file="x.rs", start_line=1, end_line=2, temporal_state="WORKING"),
            signature="fn bare_fn()",
        )
        summary = summarize_symbol(bare)
        self.assertNotIn("tested by", summary)
        self.assertNotIn("configured by", summary)
        self.assertNotIn("documented in", summary)
        self.assertNotIn("calls", summary)


class TokenizeTest(unittest.TestCase):
    def test_splits_snake_case_identifiers(self) -> None:
        self.assertEqual(tokenize("is_shared_gated_kind"), ["is", "shared", "gated", "kind"])

    def test_splits_camel_case_identifiers(self) -> None:
        self.assertEqual(tokenize("sendWelcomeEmail"), ["send", "welcome", "email"])

    def test_splits_natural_language_text_too(self) -> None:
        self.assertEqual(tokenize("Where's the code?"), ["where", "s", "the", "code"])


class EmbedAndCosineSimilarityTest(unittest.TestCase):
    # Hand-computed inputs, not real symbols -- proves the math itself is
    # correct independent of any indexing behavior (per #210's plan STEP 3
    # done-when).
    def test_embedding_of_a_vector_against_itself_is_one(self) -> None:
        vec = embed_text("kind gated shared kind")
        self.assertAlmostEqual(cosine_similarity(vec, vec), 1.0, places=9)

    def test_disjoint_vocabularies_have_zero_similarity(self) -> None:
        a = embed_text("apples bananas")
        b = embed_text("rockets moons")
        self.assertEqual(cosine_similarity(a, b), 0.0)

    def test_hand_computed_partial_overlap(self) -> None:
        # "a a b" -> {a: 2/3, b: 1/3}; "a c c" -> {a: 1/3, c: 2/3}
        # numerator = (2/3 * 1/3) = 2/9
        # norm_a = sqrt((2/3)^2 + (1/3)^2) = sqrt(5)/3
        # norm_b = sqrt((1/3)^2 + (2/3)^2) = sqrt(5)/3
        # cosine = (2/9) / (5/9) = 2/5 = 0.4
        a = embed_text("a a b")
        b = embed_text("a c c")
        self.assertAlmostEqual(cosine_similarity(a, b), 0.4, places=9)

    def test_a_zero_vector_has_zero_similarity_not_a_division_error(self) -> None:
        empty = ()
        non_empty = embed_text("kind")
        self.assertEqual(cosine_similarity(empty, non_empty), 0.0)
        self.assertEqual(cosine_similarity(empty, empty), 0.0)


if __name__ == "__main__":
    unittest.main()
