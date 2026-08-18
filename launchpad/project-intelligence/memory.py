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

import uuid
from dataclasses import dataclass, replace
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

    def _supersede(self, old: MemoryEntry, new: MemoryEntry) -> None:
        """Store the new entry, and mark the old one superseded by it.

        MemoryEntry is frozen -- "setting" superseded_by means storing a
        REPLACEMENT instance with that one field changed via
        dataclasses.replace(), never mutating the original in place. This is
        the mechanism the reconciliation rule depends on: the old entry's
        statement, evidence, and every other field stay byte-for-byte what
        they were -- get(old.id) never returns something silently rewritten.
        """
        self.add(new)
        self._entries[old.id] = replace(old, superseded_by=new.id)

    def record_code_contradiction(self, entry_id: str, new_statement: str, new_evidence: tuple[str, ...]) -> MemoryEntry | None:
        """Live repository evidence contradicts a stored entry.

        For FACT/INFERENCE: create a new FACT entry from the new evidence and
        flag the old entry stale via superseded_by -- never delete or
        silently overwrite the old statement; the repository wins, but the
        old claim's own record stays intact for anyone auditing why the
        agent used to believe it. Returns the new entry.

        TEAM_KNOWLEDGE exception: a code-only observation -- even one that
        directly contradicts the statement, e.g. no corroborating annotation
        anywhere in the source -- never supersedes a TEAM_KNOWLEDGE entry.
        "OrderRepository.legacyExport is being migrated off" can remain true
        while the code that runs it is untouched; only a person's later,
        explicit statement can retire it (record_team_statement). Returns
        None here and leaves the entry exactly as stored.
        """
        old = self._entries.get(entry_id)
        if old is None:
            raise KeyError(entry_id)

        if old.entry_class == "TEAM_KNOWLEDGE":
            return None

        new_entry = MemoryEntry(
            id=str(uuid.uuid4()),
            entry_class="FACT",
            statement=new_statement,
            evidence=tuple(new_evidence),
            temporal_state=old.temporal_state,
        )
        self._supersede(old, new_entry)
        return new_entry

    def record_team_statement(self, entry_id: str, new_statement: str, provided_by: str) -> MemoryEntry:
        """An explicit new statement from a person -- the one thing that CAN
        supersede a TEAM_KNOWLEDGE entry, since it carries the same kind of
        provenance the original entry did (a person said so), not a code
        observation. Applies to any entry class: a person's later word is at
        least as strong evidence as what STEP 3 accepts from code alone.
        """
        old = self._entries.get(entry_id)
        if old is None:
            raise KeyError(entry_id)

        new_entry = MemoryEntry(
            id=str(uuid.uuid4()),
            entry_class="TEAM_KNOWLEDGE",
            statement=new_statement,
            provided_by=provided_by,
            temporal_state=old.temporal_state,
        )
        self._supersede(old, new_entry)
        return new_entry


def _print_entry(label: str, entry: MemoryEntry | None) -> None:
    if entry is None:
        print(f"  {label}: None")
        return
    print(f"  {label}: [{entry.entry_class}] {entry.statement!r} (superseded_by={entry.superseded_by})")


if __name__ == "__main__":
    print("ProjectMemory -- the design doc's legacyExport worked example, end to end\n")
    store = ProjectMemory()
    store.add(
        MemoryEntry(
            id="legacy-export-warning",
            entry_class="TEAM_KNOWLEDGE",
            statement="OrderRepository.legacyExport is being migrated off; do not add new callers.",
            provided_by="developer, migration issue #482",
        )
    )
    print("1. Added TEAM_KNOWLEDGE entry:")
    _print_entry("legacy-export-warning", store.get("legacy-export-warning"))

    no_op = store.record_code_contradiction(
        "legacy-export-warning",
        "no deprecation marker found on legacyExport in the current source",
        ("grep: no match for 'deprecated' near legacyExport",),
    )
    print(f"\n2. record_code_contradiction() against it -> {no_op!r} (no-op: code alone cannot supersede TEAM_KNOWLEDGE)")
    _print_entry("legacy-export-warning (unchanged)", store.get("legacy-export-warning"))

    retirement = store.record_team_statement(
        "legacy-export-warning", "migration #482 complete, legacyExport removed", "developer, migration issue #482"
    )
    print("\n3. record_team_statement() retires it:")
    _print_entry("legacy-export-warning (now superseded)", store.get("legacy-export-warning"))
    _print_entry("new entry", retirement)

    print("\nProjectMemory -- a separate FACT reconciliation example\n")
    store.add(
        MemoryEntry(
            id="kind-gating-fact",
            entry_class="FACT",
            statement="is_shared_gated_kind gates only KIND_PERSONA",
            evidence=("crates/buzz-core/src/kind.rs:219",),
        )
    )
    print("1. Added FACT entry:")
    _print_entry("kind-gating-fact", store.get("kind-gating-fact"))

    superseding = store.record_code_contradiction(
        "kind-gating-fact",
        "is_shared_gated_kind gates KIND_PERSONA and KIND_TEAM_CATALOG",
        ("crates/buzz-core/src/kind.rs:219-221",),
    )
    print("\n2. record_code_contradiction() supersedes it (repository wins):")
    _print_entry("kind-gating-fact (now superseded)", store.get("kind-gating-fact"))
    _print_entry("new entry", superseding)
