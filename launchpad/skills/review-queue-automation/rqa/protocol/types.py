"""P-04-owned shared protocol types — `architecture/code/CONTRACTS.md` §2.

Every type here is defined only in `CONTRACTS.md` §2. This module implements those
exact frozen shapes and does not redefine, rename, reorder or retype any of them;
where a part contract and `CONTRACTS.md` disagree, `CONTRACTS.md` is right. Other
parts import these types only through `rqa.protocol.__init__`.

`Obligation.paths` holds `PathGlob` patterns matched only by
`rqa.protocol.paths.matches` — this module owns shape, never matching.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from enum import Enum


class EvidenceState(str, Enum):
    VERIFIED = "verified"
    NOT_VERIFIED = "not_verified"
    UNAVAILABLE = "unavailable"
    CONTRADICTORY = "contradictory"
    FAILED = "failed"
    INCOMPLETE = "incomplete"
    UNKNOWN = "unknown"


class Category(str, Enum):
    MECHANICAL = "mechanical"
    PROCEDURAL = "procedural"
    CREATION_TIME = "creation_time"
    CORRECTNESS = "correctness"
    SECURITY = "security"
    ARCHITECTURAL = "architectural"
    EVIDENCE = "evidence"


MECHANICAL_GROUP: frozenset[Category] = frozenset(
    {Category.MECHANICAL, Category.PROCEDURAL, Category.CREATION_TIME}
)
SUBSTANTIVE_GROUP: frozenset[Category] = frozenset(
    {Category.CORRECTNESS, Category.SECURITY, Category.ARCHITECTURAL, Category.EVIDENCE}
)


@dataclass(frozen=True)
class Location:
    path: str
    line: int | None


@dataclass(frozen=True)
class Remedy:
    """An exact, scoped remedy. Only findings carrying one can become remediation
    candidates. [ADR-G assumed]"""

    tool: str  # a MECHANICAL_TOOL_SET id
    paths: tuple[str, ...]  # exact normalized repository-relative files; non-empty,
    # unique, no glob metacharacters, absolute path, "." or ".." segment
    check: str  # the check name that must pass after the fix


@dataclass(frozen=True)
class Finding:
    id: str
    categories: frozenset[Category]  # non-empty; MUST contain >=1 from
    # MECHANICAL_GROUP | SUBSTANTIVE_GROUP
    extra_tags: frozenset[str]  # open vocabulary the protocol does not close (e.g. "performance")
    location: Location
    evidence: str  # non-empty
    severity: str
    remedy: Remedy | None
    behaviour_changing: bool | None  # the reviewer's own assertion; P-07 treats None as True
    source_attempt: str


@dataclass(frozen=True)
class InjectionAttempt:
    field: str  # body | comment:<id> | diff:<path>
    span_hash: str  # lowercase SHA-256 of the exact untrusted bytes, never their text
    reason: str  # semantic attempt to alter review/evidence, not phrase matching


@dataclass(frozen=True)
class HarnessIdentity:  # self-reported; recorded, never trusted
    harness: str
    model: str
    provider: str


@dataclass(frozen=True)
class Verdict:
    obligations: Mapping[str, EvidenceState]
    findings: tuple[Finding, ...]
    injection_attempts: tuple[InjectionAttempt, ...]
    identity: HarnessIdentity
    protocol_version: str


@dataclass(frozen=True)
class Valid:
    verdict: Verdict


@dataclass(frozen=True)
class Invalid:
    reasons: tuple[str, ...]


@dataclass(frozen=True)
class Obligation:
    id: str
    paths: tuple[str, ...]  # PathGlob patterns, matched ONLY by rqa.protocol.paths.matches()
    required_for: frozenset[str]  # risk classes
    evidence: str
