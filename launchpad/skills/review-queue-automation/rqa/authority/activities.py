"""The closed activity vocabulary and what each activity needs on GitHub —
`code/P-08-authority-gate.md` §2.

`Activity` is `CONTRACTS.md` §1's type, declared once in `rqa/contracts.py` and
re-exported here so a reader of this package finds the vocabulary beside the
requirements it drives. An import is not a declaration; this module defines exactly
one name of its own, `REQUIRED_CAPABILITY`.

**The six are independent.** `REQUIRED_CAPABILITY` is a per-activity table, never a
ladder: two activities sharing a capability requirement (`COMMENT`, `APPROVE` and
`REQUEST_CHANGES` all need `pulls:write`) still need their own `authority` flag in the
pinned snapshot, and `MERGE` is never implied by `APPROVE` — it carries a strictly
larger requirement *and* its own flag (RQA-NFR-017, `§8` T3).

The capability strings are P-09's vocabulary (E-16), not GitHub's. How a permission
level (`admin`/`maintain`/`write`/`triage`/`read`) and a token's scopes become these
strings is `rqa.github`'s to decide (§4); P-08 only consumes them.
"""

from __future__ import annotations

from rqa.contracts import Activity

__all__ = ["Activity", "REQUIRED_CAPABILITY"]

#: What each activity must be able to do on GitHub for a grant to be possible (§2).
#: `REVIEW` covers the assignee lease claim/release and every read — `issues:write` is
#: the assignee write, not a comment; the other five are the GitHub writes they name.
REQUIRED_CAPABILITY: dict[Activity, frozenset[str]] = {
    Activity.REVIEW: frozenset({"pulls:read", "contents:read", "checks:read", "issues:write"}),
    Activity.COMMENT: frozenset({"pulls:write"}),
    Activity.APPROVE: frozenset({"pulls:write"}),
    Activity.REQUEST_CHANGES: frozenset({"pulls:write"}),
    Activity.REMEDIATE: frozenset({"contents:write"}),
    Activity.MERGE: frozenset({"pulls:write", "contents:write"}),
}
