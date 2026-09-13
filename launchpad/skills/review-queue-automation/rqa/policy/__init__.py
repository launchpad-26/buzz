"""`rqa.policy` — P-03, `architecture/code/P-03-policy.md`.

Turns a repository's `.rqa/config.json` into the one pinned, content-hashed
`Snapshot` a job runs against for its entire lifetime: read fresh on every call,
validated fail-closed, derived as a copy of what validated (never a wider
fallback), and activated atomically with every previously activated snapshot kept
byte-for-byte intact. Separately, `onboard` writes a starter configuration and
never overwrites an operator's file.

No other module in RQA imports from `rqa.policy` except through this file. The
public surface is exactly `P-03-policy.md` §1's re-export list and nothing more:
`SnapshotStore` and `StoredSnapshot` are deliberately **not** re-exported — they
stay `rqa.policy.store` names even though E-03's signature mentions the Protocol.
The shared snapshot vocabulary — `Snapshot`, `Route`, `External`, `Policy`,
`Blocking`, `Mechanical`, `Budget`, and the validation outcomes — is imported from
`rqa.contracts` (`CONTRACTS.md` §3 is its one definition) and re-exported here so a
consumer of pinned policy can import the whole answer from one module. An import is
not a declaration: this file defines nothing.
"""

from __future__ import annotations

from rqa.contracts import (
    Blocking,
    Budget,
    External,
    Mechanical,
    Policy,
    Route,
    Snapshot,
    ValidationError,
    ValidationErrorCode,
    ValidationFailure,
)
from rqa.policy.onboard import (
    OnboardRefusal,
    OnboardRefusalReason,
    OnboardResult,
    Written,
    onboard,
)
from rqa.policy.snapshot import snapshot_for
from rqa.policy.types import PolicyError, SnapshotStoreCorrupted

__all__ = [
    "Snapshot",
    "Route",
    "External",
    "Policy",
    "Blocking",
    "Mechanical",
    "Budget",
    "snapshot_for",
    "ValidationError",
    "ValidationErrorCode",
    "ValidationFailure",
    "PolicyError",
    "SnapshotStoreCorrupted",
    "onboard",
    "OnboardResult",
    "Written",
    "OnboardRefusal",
    "OnboardRefusalReason",
]
