"""SemanticIndex -- issue #210, STEP 1.

ConceptEntry and the concept-retrieval pipeline (concept -> subsystem ->
candidate symbols -> confirmed references) from
launchpad/Research/project-intelligence-layer-design.md (§ Data Model item 3,
§ Reasoning Rules "Concept retrieval"). Ingests #206's Symbol records for
content and calls into #207's ProjectGraph for structural confirmation.
"""

from __future__ import annotations

import math
import re
from collections import Counter, defaultdict
from dataclasses import dataclass

from graph import Edge, ProjectGraph
from symbol import Symbol

_WORD_RE = re.compile(r"[a-zA-Z]+")
_CAMEL_BOUNDARY_RE = re.compile(r"(?<=[a-z0-9])(?=[A-Z])")


def tokenize(text: str) -> list[str]:
    """Splits text into lowercase word tokens, decomposing identifier-style
    boundaries (camelCase and snake_case) so `is_shared_gated_kind` and
    `sendWelcomeEmail` yield the same kind of word tokens a natural-language
    concept query would use: ["is","shared","gated","kind"] /
    ["send","welcome","email"]. This is what lets a vague NL question share
    real vocabulary with an identifier without either side special-casing
    the other.
    """
    words: list[str] = []
    for raw in _WORD_RE.findall(text):
        for part in _CAMEL_BOUNDARY_RE.split(raw):
            if part:
                words.append(part.lower())
    return words


def embed_text(text: str) -> tuple[tuple[str, float], ...]:
    """A bag-of-words frequency vector, stored as a sorted immutable tuple of
    (token, weight) pairs -- not a trained ML embedding model. This is a
    deliberate, documented simplification (see the plan's OPEN section):
    #210's own issue text scopes real embedding-model selection as out of
    scope beyond demonstrating the pipeline once.
    """
    tokens = tokenize(text)
    counts = Counter(tokens)
    total = sum(counts.values()) or 1
    return tuple(sorted((token, count / total) for token, count in counts.items()))


def cosine_similarity(a: tuple[tuple[str, float], ...], b: tuple[tuple[str, float], ...]) -> float:
    """Cosine similarity between two bag-of-words vectors, each given as a
    tuple of (token, weight) pairs. Returns 0.0 for a zero vector on either
    side (rather than dividing by zero) -- an empty embedding has no
    meaningful direction to compare.
    """
    da, db = dict(a), dict(b)
    common = set(da) & set(db)
    numerator = sum(da[token] * db[token] for token in common)
    norm_a = math.sqrt(sum(weight * weight for weight in da.values()))
    norm_b = math.sqrt(sum(weight * weight for weight in db.values()))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return numerator / (norm_a * norm_b)


def embed_symbol(sym: Symbol, identity_weight: float = 2.0) -> tuple[tuple[str, float], ...]:
    """A symbol's embedding, weighting its OWN identity (kind + qualified_name
    + signature) more heavily than incidental mentions of OTHER symbols in
    its relationships (calls/tests/config/docs).

    Without this, a caller's own bag-of-words absorbs its callees' name
    tokens too (since "calls X" contributes X's own identifier tokens), so a
    caller can outrank the callee it calls for a query about the callee's
    own behavior -- found empirically while verifying STEP 5's worked
    example: is_unshared_gated_event (which calls is_shared_gated_kind, and
    also shares the token "gated") initially outranked is_shared_gated_kind
    itself for a concept query about kind gating, once the query's own
    wording also touched a token unique to the caller's name (e.g. "event").
    identity_weight=2.0 was the smallest value that reliably corrected this
    against the real worked example below, checked empirically, not derived
    analytically -- documented here rather than left as an unexplained
    constant.
    """
    identity_vec = dict(embed_text(f"{sym.kind} {sym.qualified_name} {sym.signature}"))

    context_parts = []
    if sym.calls:
        context_parts.append("calls " + ", ".join(sym.calls))
    if sym.tests:
        context_parts.append("tested by " + ", ".join(sym.tests))
    if sym.config_dependencies:
        context_parts.append("configured by " + ", ".join(sym.config_dependencies))
    if sym.documentation_links:
        context_parts.append("documented in " + ", ".join(sym.documentation_links))
    context_vec = dict(embed_text("; ".join(context_parts))) if context_parts else {}

    merged: Counter[str] = Counter()
    for token, weight in identity_vec.items():
        merged[token] += weight * identity_weight
    for token, weight in context_vec.items():
        merged[token] += weight
    return tuple(sorted(merged.items()))


@dataclass(frozen=True)
class ConceptEntry:
    """Matches the design doc's ConceptEntry schema field-for-field.

    `scope` is a symbol_id (qualified_name), a file path, or a doc_section --
    the design doc names all three as valid scope kinds, which is exactly
    how later steps build the pipeline's two ranking levels (per-symbol and
    per-file "subsystem") from the same entry type, rather than inventing a
    second data structure for the coarser level.

    `embedding` is an immutable tuple of (token, weight) pairs, not a dict --
    same reasoning as #209's MemoryEntry.evidence being a tuple: keeps this
    frozen dataclass genuinely hashable/immutable rather than holding a
    mutable reference a caller could edit in place.
    """

    scope: str
    embedding: tuple[tuple[str, float], ...]
    summary: str


class SemanticIndex:
    """An in-process ConceptEntry store, keyed by scope."""

    def __init__(self) -> None:
        self._entries: dict[str, ConceptEntry] = {}
        self._qualified_name_by_symbol_id: dict[str, str] = {}
        self._file_scopes: set[str] = set()
        self._symbol_ids_by_file: dict[str, list[str]] = defaultdict(list)

    def add(self, entry: ConceptEntry) -> None:
        if entry.scope in self._entries:
            raise ValueError(f"an entry with scope {entry.scope!r} already exists")
        self._entries[entry.scope] = entry

    def get(self, scope: str) -> ConceptEntry | None:
        return self._entries.get(scope)

    def qualified_name_for(self, symbol_id: str) -> str | None:
        """The qualified_name a per-symbol ConceptEntry's scope (symbol_id)
        came from -- needed because #207's ProjectGraph addresses nodes by
        qualified_name, not symbol_id (see graph.py's own docstring), so the
        pipeline's confirmation step (STEP 6) must translate between the
        two, not assume they're interchangeable.
        """
        return self._qualified_name_by_symbol_id.get(symbol_id)

    @classmethod
    def from_symbols(cls, symbols: list[Symbol]) -> "SemanticIndex":
        """Builds TWO levels of ConceptEntry from real Symbol records:

        1. One per symbol (scope=symbol_id) -- the "candidate symbols" level
           of the pipeline. symbol_id, not qualified_name: a real crate can
           have multiple symbols sharing one short qualified_name (e.g. a
           method name repeated across different impls/modules) -- found by
           running this against real buzz-core data, not assumed -- so
           qualified_name is not safe as a unique scope key. symbol_id (a
           real RepoQL URI, from #206's index_crate()) is.
        2. One per FILE (scope=file path, aggregating that file's symbols'
           summaries into one combined summary/embedding) -- the "candidate
           subsystem(s)" level. The design doc's own ConceptEntry schema
           names file as a valid scope kind alongside symbol_id, so this is
           the schema's own coarser level, not invented machinery.

        Both are generated once here, at index time, from #206's already-
        extracted structural facts -- never guessed fresh per query. The
        embedding uses embed_symbol() (identity-weighted), not a plain
        embed_text(summary) -- see embed_symbol()'s own docstring for why a
        plain bag-of-words over the summary text mis-ranked STEP 5's own
        worked example.
        """
        index = cls()
        file_symbols: dict[str, list[Symbol]] = defaultdict(list)

        for sym in symbols:
            summary = summarize_symbol(sym)
            index.add(ConceptEntry(scope=sym.symbol_id, embedding=embed_symbol(sym), summary=summary))
            index._qualified_name_by_symbol_id[sym.symbol_id] = sym.qualified_name
            index._symbol_ids_by_file[sym.defined_at.file].append(sym.symbol_id)
            file_symbols[sym.defined_at.file].append(sym)

        for file, syms_in_file in file_symbols.items():
            file_summary = "; ".join(summarize_symbol(s) for s in syms_in_file)
            merged_embedding: Counter[str] = Counter()
            for s in syms_in_file:
                for token, weight in embed_symbol(s):
                    merged_embedding[token] += weight
            index.add(ConceptEntry(scope=file, embedding=tuple(sorted(merged_embedding.items())), summary=file_summary))
            index._file_scopes.add(file)

        return index

    def search(self, concept: str, top_k: int = 3) -> list["SearchResult"]:
        """The retrieval step of Concept Retrieval, as two literal ranking
        stages, not one flat rank: first rank file-level "subsystem" entries
        against the concept, then within the top-scoring file(s) rank the
        symbol-level entries scoped to them. Returns candidate symbols
        (paired with which subsystem they came from and both scores),
        ranked by candidate score -- the retrieval step alone; confirming a
        candidate via #207's ProjectGraph is a separate step (STEP 6).
        """
        query_embedding = embed_text(concept)

        subsystem_scores = [
            (self._entries[file], cosine_similarity(query_embedding, self._entries[file].embedding))
            for file in self._file_scopes
        ]
        subsystem_scores.sort(key=lambda pair: pair[1], reverse=True)
        top_subsystems = subsystem_scores[:top_k]

        results: list[SearchResult] = []
        for subsystem_entry, subsystem_score in top_subsystems:
            candidate_ids = self._symbol_ids_by_file.get(subsystem_entry.scope, [])
            candidate_scores = [
                (self._entries[sid], cosine_similarity(query_embedding, self._entries[sid].embedding))
                for sid in candidate_ids
            ]
            candidate_scores.sort(key=lambda pair: pair[1], reverse=True)
            for candidate_entry, candidate_score in candidate_scores[:top_k]:
                results.append(SearchResult(subsystem_entry, subsystem_score, candidate_entry, candidate_score))

        results.sort(key=lambda r: r.candidate_score, reverse=True)
        return results


@dataclass(frozen=True)
class Confirmation:
    tests: tuple[Edge, ...]
    callers: tuple[Edge, ...]


def confirm_via_graph(graph: ProjectGraph, qualified_name: str) -> Confirmation:
    """The pipeline's final step: real structural confirmation via #207's
    ProjectGraph, not semantic similarity alone. Returns the candidate's
    real tested_by and called_by edges -- empty tuples if none, still
    returned rather than hidden, so a caller can see an unconfirmed
    candidate for what it is instead of a confirmation that silently looks
    the same as a confirmed one.
    """
    return Confirmation(
        tests=tuple(graph.edges_from(qualified_name, ("tested_by",))),
        callers=tuple(graph.edges_from(qualified_name, ("called_by",))),
    )


@dataclass(frozen=True)
class SearchResult:
    subsystem: ConceptEntry
    subsystem_score: float
    candidate: ConceptEntry
    candidate_score: float


def summarize_symbol(sym: Symbol) -> str:
    """A short natural-language gloss of a symbol, generated ONCE from #206's
    already-extracted structural facts -- never guessed fresh per query, per
    the design doc's own stated constraint on ConceptEntry.summary.

    Deliberately a deterministic template, not an LLM call: every other
    module built this session (#206-#209) has no LLM/API dependency, and
    #210's own issue text scopes "embedding model selection" as out of
    scope beyond what demonstrates the pipeline once -- the same reasoning
    extends to summary generation.
    """
    parts = [f"{sym.kind} {sym.qualified_name}", sym.signature]
    if sym.calls:
        parts.append("calls " + ", ".join(sym.calls))
    if sym.tests:
        parts.append("tested by " + ", ".join(sym.tests))
    if sym.config_dependencies:
        parts.append("configured by " + ", ".join(sym.config_dependencies))
    if sym.documentation_links:
        parts.append("documented in " + ", ".join(sym.documentation_links))
    return "; ".join(parts)
