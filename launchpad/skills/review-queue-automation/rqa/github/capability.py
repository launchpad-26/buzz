"""E-16 `probe` — `code/P-09-github-adapter.md` §3.4; ADR-0062.

Read-only, and needs no grant: it performs no write to establish a write
capability (§8 T9). The caller — P-08, the only consumer — supplies the
credential explicitly, because it wants to attest the exact value it already
read via its own E-22, not trust that this file resolved the identical one
(§4's one declared exception).

**The vocabulary is P-09's.** P-08 consumes it; this file owns how GitHub
expresses it (`code/P-08-authority-gate.md` §4). The strings are the ones
P-08's `REQUIRED_CAPABILITY` table checks a `Grant` against: `pulls:read`,
`contents:read`, `checks:read`, `issues:write`, `pulls:write`,
`contents:write`.

**Proven versus attested (RQA-NFR-024 floor, RQA-NFR-030 ceiling).** Read
capabilities are *proven*: this probe exercised authenticated reads on the
exact repository with the supplied credential. Write capabilities are only
ever *attested_not_proven*: GitHub's `permissions` block reports them, but the
probe never writes to prove one (ADR-E's recorded residual — the
`attestation` record P-08 writes is where that split lands).
"""

from __future__ import annotations

from collections.abc import Mapping

from rqa.contracts import CapabilityReading, GithubUnavailable
from rqa.github import transport as transport_module

__all__ = ["probe"]

#: Proven by this probe's own authenticated reads when the credential has at
#: least read (`pull`) permission on the repository.
_READ_CAPABILITIES = frozenset({"pulls:read", "contents:read", "checks:read"})
#: Reported by GitHub for push-or-higher; never exercised here.
_PUSH_CAPABILITIES = frozenset({"pulls:write", "contents:write", "issues:write"})
#: Triage can manage assignees without contents access.
_TRIAGE_CAPABILITIES = frozenset({"issues:write"})


def probe(*, adapter, repo: str, credential: str) -> CapabilityReading | GithubUnavailable:
    """§3.4, branch by branch: unreadable/unauthenticated user endpoint →
    `unauthenticated`; unreadable repository via transport or rate limit → the
    matching retriable value; 403/404 → the empty capability reading;
    otherwise the derived reading."""
    try:
        user = adapter.transport.rest_json("/user", operation="probe", credential=credential)
    except transport_module.Unavailable:
        return GithubUnavailable(op="probe", reason="unauthenticated", retriable=False)
    login = user.get("login") if isinstance(user, Mapping) else None
    if not isinstance(login, str) or not login:
        return GithubUnavailable(op="probe", reason="unauthenticated", retriable=False)

    try:
        meta = adapter.transport.rest_json(
            f"/repos/{repo}", operation="probe", credential=credential
        )
    except transport_module.Unavailable as failure:
        if failure.status in (403, 404, 410):
            # Not reachable with this credential: the empty capability
            # reading, so every activity is denied CAPABILITY_MISSING (P-08).
            return CapabilityReading(
                capabilities=frozenset(), attested_not_proven=frozenset(), login=login
            )
        return GithubUnavailable(op="probe", reason=failure.reason, retriable=failure.retriable)

    permissions = meta.get("permissions") if isinstance(meta, Mapping) else None
    permissions = permissions if isinstance(permissions, Mapping) else {}

    proven: set[str] = set()
    attested: set[str] = set()
    if permissions.get("pull"):
        proven |= _READ_CAPABILITIES
    if permissions.get("triage"):
        attested |= _TRIAGE_CAPABILITIES
    if permissions.get("push") or permissions.get("maintain") or permissions.get("admin"):
        attested |= _PUSH_CAPABILITIES
    return CapabilityReading(
        capabilities=frozenset(proven),
        attested_not_proven=frozenset(attested),
        login=login,
    )
