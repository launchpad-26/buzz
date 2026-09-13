"""`rqa.authority` — P-08, `architecture/code/P-08-authority-gate.md`.

Answers *may RQA perform this activity on this repository, for this job, right now?* —
from the pinned snapshot and a proven capability, never from anything else — and records
the answer. No activity is granted without both a validated pinned snapshot and a
per-job capability proof for that repository; an unreadable policy yields no snapshot and
therefore no grant (RQA-NFR-018, RQA-NFR-025).

No other module in RQA imports from `rqa.authority` except through this file, and the
public surface is exactly §1's re-export list: `grant`, `Activity`, `Grant`, `Deny`,
`GateError`. `Gate`, `CapabilityProof`, `CapabilityStore`, `GithubProbe`,
`SqliteCapabilityStore` and `CredentialGithubUnavailable` stay submodule names —
deliberately, the way `rqa.policy` keeps `SnapshotStore` out of its package surface even
though E-03's signature mentions the Protocol.

`Activity`, `Grant` and `Deny` are `CONTRACTS.md` §1/§8 types imported from
`rqa.contracts`, which is their one definition; re-exporting them here lets a consumer of
an authority answer import the whole answer from one module. An import is not a
declaration: this file defines nothing.
"""

from __future__ import annotations

from rqa.authority.gate import GateError, grant
from rqa.contracts import Activity, Deny, Grant

__all__ = ["grant", "Activity", "Grant", "Deny", "GateError"]
