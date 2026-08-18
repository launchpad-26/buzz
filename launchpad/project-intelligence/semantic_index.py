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
from collections import Counter
from dataclasses import dataclass

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

    def add(self, entry: ConceptEntry) -> None:
        if entry.scope in self._entries:
            raise ValueError(f"an entry with scope {entry.scope!r} already exists")
        self._entries[entry.scope] = entry

    def get(self, scope: str) -> ConceptEntry | None:
        return self._entries.get(scope)


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
