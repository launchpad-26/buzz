"""`rqa.protocol` — `code/CONTRACTS.md` §2, owned by `code/P-04-protocol.md`.

The published protocol definition, wire schema, and path matcher (§§1-2). Other
parts import protocol types and pure functions only through this module, except for
the deliberately qualified `rqa.protocol.paths.matches` import P-04 §2 mandates —
`paths` is reachable only as a submodule and is never re-exported by name here.

This module currently re-exports only §§1-2's names. `validate`, `Valid`, `Invalid`
and `ProtocolError` (P-04 §3, the structural/coherence validation entry point) are
owned by a sibling implementation lane building `schema.py`, `contradictions.py` and
`validate.py`, none of which exist in this tree yet — importing them here would make
this package unimportable before that lane merges. That lane appends `validate` and
`ProtocolError` to this file once it lands. `Valid` and `Invalid` are §2's shared
result types and are already re-exported below; they are never redefined.
"""

from __future__ import annotations

from rqa.protocol.envelope import envelope, extract
from rqa.protocol.interaction import PROBE_MARKER
from rqa.protocol.types import (
    MECHANICAL_GROUP,
    SUBSTANTIVE_GROUP,
    Category,
    EvidenceState,
    Finding,
    HarnessIdentity,
    InjectionAttempt,
    Invalid,
    Location,
    Obligation,
    Remedy,
    Valid,
    Verdict,
)
from rqa.protocol.version import PROTOCOL_VERSION, protocol_hash
from rqa.protocol.validate import ProtocolError, validate

__all__ = [
    "Valid",
    "Invalid",
    "Location",
    "Category",
    "MECHANICAL_GROUP",
    "SUBSTANTIVE_GROUP",
    "EvidenceState",
    "Obligation",
    "Remedy",
    "Finding",
    "InjectionAttempt",
    "HarnessIdentity",
    "Verdict",
    "PROTOCOL_VERSION",
    "protocol_hash",
    "PROBE_MARKER",
    "envelope",
    "extract",
    "validate",
    "ProtocolError",
]
