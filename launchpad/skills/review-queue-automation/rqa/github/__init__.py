"""`rqa.github` — P-09, `architecture/code/P-09-github-adapter.md`.

Every byte RQA sends to or reads from GitHub crosses this one adapter and no
other; every write it performs carries proof, passed in by the caller, that an
activity was already granted, and is idempotent by a deterministic id.

No other module in RQA imports from `rqa.github` except through this file
(§1). The public surface is exactly §1's re-export list and nothing more: the
§4 shared imports (`Activity`, `Grant`, `Job`, `RecordWriter`, `Entry`) plus
`GithubAdapter`, `CheckConclusion`, `FAILING`, `UNSETTLED`, `PASSING`,
`MutationKind`, `Stale`, `LeaseTaken`, `GithubUnavailable`,
`CapabilityReading` and `AdapterError`. The store Protocols (`EtagStore`,
`ApiCallStore`, `MutationStore`, `MutationRow`) deliberately stay
`rqa.github.store` names, the same way `rqa.policy` keeps `SnapshotStore` a
`rqa.policy.store` name. The shared boundary vocabulary is imported from
`rqa.contracts` (`CONTRACTS.md` §§1, 4, 7, 8 are its one definition) and
re-exported here so a consumer of the adapter can import the whole answer
from one module. An import is not a declaration: this file defines nothing.
"""

from __future__ import annotations

from rqa.contracts import (
    FAILING,
    PASSING,
    UNSETTLED,
    Activity,
    CapabilityReading,
    CheckConclusion,
    Entry,
    GithubUnavailable,
    Grant,
    Job,
    LeaseTaken,
    RecordWriter,
    Stale,
)
from rqa.github.types import AdapterError, GithubAdapter, MutationKind

__all__ = [
    "Activity",
    "AdapterError",
    "CapabilityReading",
    "CheckConclusion",
    "Entry",
    "FAILING",
    "GithubAdapter",
    "GithubUnavailable",
    "Grant",
    "Job",
    "LeaseTaken",
    "MutationKind",
    "PASSING",
    "RecordWriter",
    "Stale",
    "UNSETTLED",
]
