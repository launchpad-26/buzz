"""The closed fourteen-kind set and this part's programming errors —
`code/P-12-record.md` §1, §2 and §6.

`EntryKind` and `ENTRY_KINDS` have exactly one definition, `CONTRACTS.md` §7, landed
in `rqa/contracts.py`. This module imports and re-exports them; it declares neither,
because two sources for a closed set is how a closed set stops being closed.

**Where this part's three errors live.** §1 fixes eleven modules and none of them is
an `errors` module, so the two raise sites carry their own error: the kind gate is
here with the set it gates against, and `PayloadNotSerializable` is in `hashing.py`
beside `canonical_json`, the only function that can raise it. `RecordProgrammingError`
is declared here as the shared base both subclasses extend.

These are programming errors, never recorded outcomes: a caller that names a kind
outside the closed set, or hands over a value `canonical_json` cannot render, has a
defect in itself. §2: "Never caught by Lifecycle's containment boundary (P-02)".
"""

from __future__ import annotations

from rqa.contracts import ENTRY_KINDS, EntryKind

__all__ = [
    "ENTRY_KINDS",
    "EntryKind",
    "PayloadNotSerializable",
    "RecordProgrammingError",
    "UnknownEntryKind",
    "require_kind",
]


class RecordProgrammingError(Exception):
    """Base class for this part's own programming errors — never a policy, availability
    or tamper finding. Never caught by Lifecycle's containment boundary (P-02); a caller
    passing an unknown kind or an unserializable payload is a defect in the caller, not a
    recorded outcome."""


class UnknownEntryKind(RecordProgrammingError):
    """`kind` is not one of the fourteen values in ENTRY_KINDS."""


def require_kind(*, kind: object) -> EntryKind:
    """`kind` itself when it is one of the fourteen; otherwise `UnknownEntryKind`.

    §3.1 step 1: this runs before anything is read or written, so a rejected kind
    leaves the record byte-identical. The membership test is on the value, so a
    `str` subclass that happens to carry a member's text — an enum from another
    part, say — is rejected here rather than stored as a kind nobody can reproduce.
    """
    if type(kind) is not str or kind not in ENTRY_KINDS:
        raise UnknownEntryKind(
            f"{kind!r} is not one of the fourteen entry kinds: {sorted(ENTRY_KINDS)}"
        )
    return kind
