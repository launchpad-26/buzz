"""Controls for semantic_index.py -- issue #210.

Run:  python3 -m unittest test_semantic_index    (from launchpad/project-intelligence/)
  or: python3 test_semantic_index.py
"""

from __future__ import annotations

import unittest

from semantic_index import (
    ConceptEntry,
    SemanticIndex,
    cosine_similarity,
    embed_symbol,
    embed_text,
    summarize_symbol,
    tokenize,
)
from symbol import DefinedAt, Symbol

# A second real Symbol from the SAME file (crates/buzz-core/src/kind.rs:232-236),
# cross-checked directly against the real source -- used to demonstrate STEP 4's
# per-file aggregation with more than one real symbol from the same file.
_IS_UNSHARED_GATED_EVENT = Symbol(
    symbol_id="crates/buzz-core/src/kind.rs::is_unshared_gated_event",
    kind="function",
    qualified_name="is_unshared_gated_event",
    defined_at=DefinedAt(file="crates/buzz-core/src/kind.rs", start_line=232, end_line=236, temporal_state="WORKING"),
    signature="pub fn is_unshared_gated_event(event: &nostr::Event, requester_pubkey_bytes: &[u8]) -> bool",
    calls=("is_shared_gated_kind",),
)

# A real symbol from a DIFFERENT file with clearly unrelated vocabulary
# (crates/buzz-core/src/invite.rs:34-36, cross-checked via `rql query`) -- used
# to prove the two-stage search discriminates by subsystem, not just symbol.
_ENCODE_V2_CODE = Symbol(
    symbol_id="crates/buzz-core/src/invite.rs::encode_v2_code",
    kind="function",
    qualified_name="encode_v2_code",
    defined_at=DefinedAt(file="crates/buzz-core/src/invite.rs", start_line=34, end_line=36, temporal_state="WORKING"),
    signature="pub fn encode_v2_code(secret: &[u8; V2_SECRET_LEN]) -> String",
)

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


class EmbedSymbolTest(unittest.TestCase):
    def test_identity_tokens_are_weighted_more_than_context_tokens(self) -> None:
        # is_unshared_gated_event's own summary mentions is_shared_gated_kind
        # (via "calls") -- without identity-weighting, a query sharing
        # vocabulary with that mention could make the CALLER outscore the
        # callee itself. Confirmed this was a real risk (not hypothetical)
        # by first observing it with plain embed_text(summary), before
        # embed_symbol() was written -- see the fix commit's message.
        vec = dict(embed_symbol(_IS_UNSHARED_GATED_EVENT))
        # "event" (identity, weight 2.0/total) must outweigh "kind" (context,
        # weight 1.0/total, absorbed from the "calls is_shared_gated_kind" mention).
        self.assertGreater(vec["event"], vec["kind"])


class TwoStageSearchTest(unittest.TestCase):
    def test_ranks_the_correct_subsystem_then_the_correct_candidate_within_it(self) -> None:
        index = SemanticIndex.from_symbols([_IS_SHARED_GATED_KIND, _IS_UNSHARED_GATED_EVENT, _ENCODE_V2_CODE])
        results = index.search("which function decides if a kind is gated for shared visibility")

        self.assertGreater(len(results), 0)
        top = results[0]
        # Stage 1: the correct subsystem (file) won.
        self.assertEqual(top.subsystem.scope, "crates/buzz-core/src/kind.rs")
        # Stage 2: the correct candidate symbol within it won.
        self.assertEqual(top.candidate.scope, _IS_SHARED_GATED_KIND.symbol_id)
        # The unrelated file's symbol never appears as the top result.
        self.assertNotEqual(top.candidate.scope, _ENCODE_V2_CODE.symbol_id)


class FromSymbolsTest(unittest.TestCase):
    def test_builds_one_concept_entry_per_symbol_keyed_by_symbol_id(self) -> None:
        index = SemanticIndex.from_symbols([_IS_SHARED_GATED_KIND, _IS_UNSHARED_GATED_EVENT])
        self.assertIsNotNone(index.get(_IS_SHARED_GATED_KIND.symbol_id))
        self.assertIsNotNone(index.get(_IS_UNSHARED_GATED_EVENT.symbol_id))

    def test_symbol_id_not_qualified_name_avoids_a_real_collision(self) -> None:
        # Two distinct real symbols sharing one qualified_name (a realistic
        # shape found live against buzz-core -- multiple symbols named
        # "build_event" in different modules) must not collide, since
        # qualified_name is not a safe unique key but symbol_id is.
        a = Symbol(
            symbol_id="file:///crates/buzz-core/src/a.rs#symbol=build_event",
            kind="function",
            qualified_name="build_event",
            defined_at=DefinedAt(file="crates/buzz-core/src/a.rs", start_line=1, end_line=2, temporal_state="WORKING"),
            signature="fn build_event() -> Event",
        )
        b = Symbol(
            symbol_id="file:///crates/buzz-core/src/b.rs#symbol=build_event",
            kind="function",
            qualified_name="build_event",
            defined_at=DefinedAt(file="crates/buzz-core/src/b.rs", start_line=1, end_line=2, temporal_state="WORKING"),
            signature="fn build_event() -> Event",
        )
        index = SemanticIndex.from_symbols([a, b])  # must not raise
        self.assertIsNotNone(index.get(a.symbol_id))
        self.assertIsNotNone(index.get(b.symbol_id))

    def test_qualified_name_for_translates_symbol_id_back(self) -> None:
        index = SemanticIndex.from_symbols([_IS_SHARED_GATED_KIND])
        self.assertEqual(index.qualified_name_for(_IS_SHARED_GATED_KIND.symbol_id), "is_shared_gated_kind")

    def test_builds_a_file_level_entry_aggregating_more_than_one_real_symbol(self) -> None:
        index = SemanticIndex.from_symbols([_IS_SHARED_GATED_KIND, _IS_UNSHARED_GATED_EVENT])
        file_entry = index.get("crates/buzz-core/src/kind.rs")
        self.assertIsNotNone(file_entry)
        # Both real symbols' own qualified names appear in the aggregated summary.
        self.assertIn("is_shared_gated_kind", file_entry.summary)
        self.assertIn("is_unshared_gated_event", file_entry.summary)
        # The aggregated embedding is not just one symbol's alone.
        single_symbol_entry = index.get(_IS_SHARED_GATED_KIND.symbol_id)
        self.assertNotEqual(file_entry.embedding, single_symbol_entry.embedding)


if __name__ == "__main__":
    unittest.main()
