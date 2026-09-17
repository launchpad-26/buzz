"""`rqa.github` — P-09, `architecture/code/P-09-github-adapter.md`.

Every byte RQA sends to or reads from GitHub crosses this one adapter and no
other; every write it performs carries proof, passed in by the caller, that an
activity was already granted, and is idempotent by a deterministic id.

No other module in RQA imports from `rqa.github` except through this file
(§1). The public surface is §1's re-export list — the §4 shared imports
(`Activity`, `Grant`, `Job`, `RecordWriter`, `Entry`) plus `GithubAdapter`,
`CheckConclusion`, `FAILING`, `UNSETTLED`, `PASSING`, `MutationKind`, `Stale`,
`LeaseTaken`, `GithubUnavailable`, `CapabilityReading` and `AdapterError` —
plus the concrete collaborators a composition root must construct:
`SqliteEtagStore`, `SqliteApiCallStore`, `SqliteMutationStore`,
`ensure_schema`, `Transport`, `GithubAnchorPublisher` and `GithubAnchorReader`.

**Why those six are surface.** P-09 never constructs its own stores or its own
transport; `GithubAdapter`'s implementation takes each as a parameter, so
something outside this package always must build them, and the operator CLI's
composition root (#2211) is the first module in RQA whose job is exactly that.
Withholding them while forbidding a reach past `__init__` left no conforming way
to build the adapter: the clause was unfalsifiable only until a composition root
existed. `ensure_schema` is P-09's own — each part publishes its own through its
own package, so `rqa.github.ensure_schema` and `rqa.intake.ensure_schema` are
distinct front doors and no collision arises.

The store *Protocols* (`EtagStore`, `ApiCallStore`, `MutationStore`,
`MutationRow`) deliberately stay `rqa.github.store` names: a caller that only
names the seam has no reason to reach for the package. The shared boundary
vocabulary is imported from `rqa.contracts` (`CONTRACTS.md` §§1, 4, 7, 8 are its
one definition) and re-exported here so a consumer of the adapter can import the
whole answer from one module. An import is not a declaration: this file defines
nothing.
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
from rqa.github.anchor_publisher import GithubAnchorPublisher
from rqa.github.anchor_reader import GithubAnchorReader
from rqa.github.store import (
    SqliteApiCallStore,
    SqliteEtagStore,
    SqliteMutationStore,
    ensure_schema,
)
from rqa.github.transport import Transport
from rqa.github.types import AdapterError, GithubAdapter, MutationKind

__all__ = [
    "Activity",
    "AdapterError",
    "CapabilityReading",
    "CheckConclusion",
    "Entry",
    "FAILING",
    "GithubAdapter",
    "GithubAnchorPublisher",
    "GithubAnchorReader",
    "GithubUnavailable",
    "Grant",
    "Job",
    "LeaseTaken",
    "MutationKind",
    "PASSING",
    "RecordWriter",
    "SqliteApiCallStore",
    "SqliteEtagStore",
    "SqliteMutationStore",
    "Stale",
    "Transport",
    "UNSETTLED",
    "ensure_schema",
]
