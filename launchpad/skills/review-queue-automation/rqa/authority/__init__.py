"""`rqa.authority` — P-08, `architecture/code/P-08-authority-gate.md`.

Answers *may RQA perform this activity on this repository, for this job, right now?* —
from the pinned snapshot and a proven capability, never from anything else — and records
the answer. No activity is granted without both a validated pinned snapshot and a
per-job capability proof for that repository; an unreadable policy yields no snapshot and
therefore no grant (RQA-NFR-018, RQA-NFR-025).

No other module in RQA imports from `rqa.authority` except through this file, and the
public surface is §1's re-export list plus the one concrete store a composition root
must construct: `grant`, `Activity`, `Grant`, `Deny`, `GateError`,
`SqliteCapabilityStore`. `Gate`, `CapabilityProof`, `CapabilityStore`, `GithubProbe`
and `CredentialGithubUnavailable` stay submodule names.

**Why the store is surface.** P-08 never constructs its own store — `grant()` takes it
as a parameter — so something outside this package always must, and the operator CLI's
composition root (#2211) is the first module in RQA whose job is exactly that.
Withholding `SqliteCapabilityStore` while forbidding a reach past `__init__` left no
conforming way to build it: the clause was unfalsifiable only until a composition root
existed. Publishing the store keeps the import a front-door one and satisfies §1's
sentence as written.

`Activity`, `Grant` and `Deny` are `CONTRACTS.md` §1/§8 types imported from
`rqa.contracts`, which is their one definition; re-exporting them here lets a consumer of
an authority answer import the whole answer from one module. An import is not a
declaration: this file defines nothing.
"""

from __future__ import annotations

from rqa.authority.gate import Gate, GateError, grant
from rqa.authority.store import SqliteCapabilityStore
from rqa.contracts import Activity, Deny, Grant

__all__ = ["grant", "Activity", "Grant", "Deny", "GateError", "SqliteCapabilityStore", "Gate"]
