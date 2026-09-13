"""`rqa.remediation` — `code/CONTRACTS.md` §9 E-10, owned by `code/P-10-remediation.md`.

Given an exact mechanical remedy, a pinned snapshot and a verified `REMEDIATE` grant,
`remediate` validates the target, applies the remedy to exact files in an isolated
worktree, mechanically proves the actual diff behavior-equivalent and in scope, and pushes
one commit to that PR head branch — or refuses, naming one of `CONTRACTS.md` §6's fifteen
reasons. It never force-pushes, never merges, never touches the operator's checkout and
never applies a model-supplied patch.

`MECHANICAL_TOOL_SET` is exported here because it is the registry `rqa.policy` and
`rqa.authority` resolve at call time to decide whether a configured tool id exists at all.
Every other name below is a `rqa.contracts` type re-exported rather than redefined; this
package declares only `ToolSpec` and `RemediationError`, which are P-10's own (§2).
"""

from __future__ import annotations

from rqa.contracts import RemediationPushed, RemediationRefusalReason, RemediationRefused

from rqa.remediation.remediate import remediate
from rqa.remediation.tools import MECHANICAL_TOOL_SET, RemediationError, ToolSpec

__all__ = [
    "remediate",
    "RemediationPushed",
    "RemediationRefused",
    "RemediationRefusalReason",
    "MECHANICAL_TOOL_SET",
    "ToolSpec",
    "RemediationError",
]
