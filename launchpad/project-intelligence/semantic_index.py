"""SemanticIndex -- issue #210, STEP 1.

ConceptEntry and the concept-retrieval pipeline (concept -> subsystem ->
candidate symbols -> confirmed references) from
launchpad/Research/project-intelligence-layer-design.md (§ Data Model item 3,
§ Reasoning Rules "Concept retrieval"). Ingests #206's Symbol records for
content and calls into #207's ProjectGraph for structural confirmation.
"""

from __future__ import annotations

from dataclasses import dataclass


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
