"""`rqa.protocol` — `code/CONTRACTS.md` §2, owned by `code/P-04-protocol.md`.

The published protocol definition, wire schema, and path matcher (§§1-2). Other
parts import protocol types and pure functions only through this module, except for
the deliberately qualified `rqa.protocol.paths.matches` import P-04 §2 mandates —
`paths` is reachable only as a submodule and is never re-exported by name here.

The package now exposes both halves of the completed P-04 surface: §§1-2's shared
types and protocol artefacts, plus §3's structural/coherence `validate` entry point
and `ProtocolError`. `Valid` and `Invalid` remain the shared result types from
`types.py`; they are re-exported here and never redefined.
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
from rqa.protocol.version import PROTOCOL_VERSION, protocol_hash, schema_path
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
    "schema_path",
    "protocol_hash",
    "PROBE_MARKER",
    "envelope",
    "extract",
    "validate",
    "ProtocolError",
]
