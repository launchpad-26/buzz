"""ProjectMemory -- issue #209, STEP 1.

MemoryEntry and the provenance/reconciliation rules from
launchpad/Research/project-intelligence-layer-design.md (§ Data Model, item 4):
FACT / INFERENCE / TEAM_KNOWLEDGE, stored as a real structural field, never a
free-text note -- and the reconciliation rule: live evidence contradicting a
stored FACT/INFERENCE flags it stale via a new superseding entry, never a
silent overwrite; TEAM_KNOWLEDGE is the one exception -- only an explicit new
statement from a person, never a code-only observation, supersedes it.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

EntryClass = Literal["FACT", "INFERENCE", "TEAM_KNOWLEDGE"]
TemporalState = Literal["BASE", "WORKING", "HISTORY"]

_VALID_CLASSES = {"FACT", "INFERENCE", "TEAM_KNOWLEDGE"}
_VALID_TEMPORAL_STATES = {"BASE", "WORKING", "HISTORY"}


@dataclass(frozen=True)
class MemoryEntry:
    """Matches the design doc's MemoryEntry schema field-for-field.

    Validation enforces the doc's own stated constraints: `confidence` is
    required for INFERENCE only, `provided_by` is required for TEAM_KNOWLEDGE
    only, and `evidence` is required for FACT and INFERENCE (a TEAM_KNOWLEDGE
    entry is "stored verbatim with who said it and when" -- it does not need
    corroborating evidence, that's precisely the case it exists for).
    """

    id: str
    entry_class: EntryClass
    statement: str
    evidence: tuple[str, ...] = ()
    confidence: float | None = None
    provided_by: str | None = None
    temporal_state: TemporalState = "WORKING"
    superseded_by: str | None = None

    def __post_init__(self) -> None:
        if self.entry_class not in _VALID_CLASSES:
            raise ValueError(f"entry_class must be one of {_VALID_CLASSES}, got {self.entry_class!r}")
        if self.temporal_state not in _VALID_TEMPORAL_STATES:
            raise ValueError(f"temporal_state must be one of {_VALID_TEMPORAL_STATES}, got {self.temporal_state!r}")

        if self.entry_class == "INFERENCE":
            if self.confidence is None:
                raise ValueError("confidence is required for an INFERENCE entry")
        elif self.confidence is not None:
            raise ValueError(f"confidence is only valid on INFERENCE entries, not {self.entry_class}")

        if self.entry_class == "TEAM_KNOWLEDGE":
            if self.provided_by is None:
                raise ValueError("provided_by is required for a TEAM_KNOWLEDGE entry")
        elif self.provided_by is not None:
            raise ValueError(f"provided_by is only valid on TEAM_KNOWLEDGE entries, not {self.entry_class}")

        if self.entry_class in ("FACT", "INFERENCE") and not self.evidence:
            raise ValueError(f"evidence is required for a {self.entry_class} entry")


class ProjectMemory:
    """An in-process MemoryEntry store.

    `class` is a real structural field on every stored entry, queryable
    directly (query_by_class) -- never a note embedded in `statement` that a
    caller would have to parse back out.
    """

    def __init__(self) -> None:
        self._entries: dict[str, MemoryEntry] = {}

    def add(self, entry: MemoryEntry) -> None:
        if entry.id in self._entries:
            raise ValueError(f"an entry with id {entry.id!r} already exists")
        self._entries[entry.id] = entry

    def get(self, entry_id: str) -> MemoryEntry | None:
        return self._entries.get(entry_id)

    def query_by_class(self, entry_class: EntryClass) -> list[MemoryEntry]:
        return [e for e in self._entries.values() if e.entry_class == entry_class]
