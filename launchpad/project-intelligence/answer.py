"""Claim and Answer -- issue #211, STEP 1.

The answer format from launchpad/Research/project-intelligence-layer-design.md
(§ Data Model, item 7): six named sections, and every claim in the answer
carrying its provenance class rather than its label being a tone of voice.

Provenance vocabulary is memory.py's, not a second one. A Claim validates by
constructing a throwaway MemoryEntry and letting #209's own __post_init__ raise
-- so the rules ("confidence for INFERENCE only", "provided_by for
TEAM_KNOWLEDGE only", "evidence for FACT and INFERENCE") live in exactly one
place. Copying those thirty lines here would let an answer accept a shape the
memory store rejects, which is precisely the conflation the design doc's
"provenance classes are never conflated" constraint forbids.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from memory import EntryClass, MemoryEntry, TemporalState

# The design doc's § Data Model item 7 section list, in the order it gives them.
# `## Sources` is derived from claims rather than authored, so it is not a
# content field -- see Answer.
SECTION_ORDER = (
    "Short answer",
    "How it works",
    "Relevant flow",
    "Important files",
    "Things to be aware of",
    "Sources",
)


@dataclass(frozen=True)
class Claim:
    """One assertion in an answer, with the provenance class it was earned at.

    Deliberately not a MemoryEntry: a claim is transient output, has no id, and
    is never superseded -- it is rebuilt from evidence on the next question.
    It borrows MemoryEntry's *validation* without borrowing its identity.
    """

    statement: str
    entry_class: EntryClass
    evidence: tuple[str, ...] = ()
    confidence: float | None = None
    provided_by: str | None = None
    temporal_state: TemporalState = "WORKING"

    def __post_init__(self) -> None:
        if not isinstance(self.statement, str) or not self.statement.strip():
            raise ValueError(f"statement must be a non-empty string, got {self.statement!r}")

        # Delegate every provenance rule to #209. The id is a placeholder --
        # this entry is discarded, only its validation is wanted.
        probe = MemoryEntry(
            id="claim-validation-probe",
            entry_class=self.entry_class,
            statement=self.statement,
            evidence=self.evidence,
            confidence=self.confidence,
            provided_by=self.provided_by,
            temporal_state=self.temporal_state,
        )
        # MemoryEntry normalizes evidence to a tuple; carry that normalization
        # across so a Claim built from a list is genuinely immutable too.
        object.__setattr__(self, "evidence", probe.evidence)


@dataclass(frozen=True)
class Answer:
    """A rendered-ready answer: five authored sections plus its claims.

    `Sources` is not a field. It is generated from `claims` at render time --
    an authored sources section could disagree with the claims it is meant to
    account for, and a provenance layer whose sources list is hand-maintained
    is a provenance layer that can lie.
    """

    question: str
    short_answer: str = ""
    how_it_works: str = ""
    relevant_flow: str = ""
    important_files: tuple[str, ...] = ()
    things_to_be_aware_of: str = ""
    claims: tuple[Claim, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not isinstance(self.question, str) or not self.question.strip():
            raise ValueError(f"question must be a non-empty string, got {self.question!r}")
        if isinstance(self.important_files, str) or not isinstance(self.important_files, (list, tuple)):
            raise ValueError(f"important_files must be a list or tuple, got {self.important_files!r}")
        if any(not isinstance(c, Claim) for c in self.claims):
            raise ValueError("every item in claims must be a Claim")
        object.__setattr__(self, "important_files", tuple(self.important_files))
        object.__setattr__(self, "claims", tuple(self.claims))

    def claims_of_class(self, entry_class: EntryClass) -> tuple[Claim, ...]:
        return tuple(c for c in self.claims if c.entry_class == entry_class)
