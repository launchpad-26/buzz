"""GitHub authentication and capability probing for review-queue-automation.

Authority is asserted from PROVEN capability, never assumed. The probe establishes
what the locally authenticated identity can actually do using read-only calls, and
downgrades the runtime mode when a capability is missing.

Rules:
- Auth comes from the local `gh` login (or GITHUB_TOKEN/GH_TOKEN). The token is
  never written to config, state, evidence, or logs; only its presence and the
  resolved login are recorded.
- Capability is derived from the repository's `permissions` object for the
  authenticated user, so probing costs reads and mutates nothing.
- A capability that cannot be proven is reported UNKNOWN and treated as absent.
  Read access without write access downgrades to recommendation-only rather than
  failing, so the queue keeps producing drafts and human requests.
- Nothing here raises `SystemExit`: a missing token degrades the run, it does not
  kill the process mid-sweep.
"""

from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass, field
from typing import Any

#: Runtime modes, most capable first.
FULL = "full"                        # can post reviews and mutate PR metadata
RECOMMENDATION_ONLY = "recommendation_only"  # reads fine, actions go to the human queue
UNUSABLE = "unusable"                # cannot even read; nothing safe to do

TOKEN_ENV_VARS = ("GITHUB_TOKEN", "GH_TOKEN")


@dataclass
class TokenSource:
    present: bool
    source: str = ""
    reason: str = ""

    def as_dict(self) -> dict[str, Any]:
        # Deliberately no token value, not even truncated.
        return {"present": self.present, "source": self.source, "reason": self.reason}


@dataclass
class Capabilities:
    """What the authenticated identity is PROVEN able to do on one repository."""

    login: str = ""
    repo_readable: bool = False
    pulls_readable: bool = False
    can_submit_review: bool = False
    can_create_issue: bool = False
    can_add_labels: bool = False
    permissions: dict[str, bool] = field(default_factory=dict)
    unknown: tuple[str, ...] = ()
    reasons: list[str] = field(default_factory=list)

    @property
    def mode(self) -> str:
        if not (self.repo_readable and self.pulls_readable):
            return UNUSABLE
        if self.can_submit_review:
            return FULL
        return RECOMMENDATION_ONLY

    def as_dict(self) -> dict[str, Any]:
        return {
            "login": self.login,
            "mode": self.mode,
            "repo_readable": self.repo_readable,
            "pulls_readable": self.pulls_readable,
            "can_submit_review": self.can_submit_review,
            "can_create_issue": self.can_create_issue,
            "can_add_labels": self.can_add_labels,
            "permissions": dict(self.permissions),
            "unknown": list(self.unknown),
            "reasons": list(self.reasons),
        }


def resolve_token_source(*, _runner=subprocess.run) -> TokenSource:
    """Establish that an auth token exists, WITHOUT returning or recording it."""
    for name in TOKEN_ENV_VARS:
        if os.environ.get(name, "").strip():
            return TokenSource(present=True, source=f"env:{name}")
    try:
        result = _runner(
            ["gh", "auth", "token"], capture_output=True, timeout=15,
            stdin=subprocess.DEVNULL,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError) as exc:
        return TokenSource(present=False, reason=f"gh auth token unavailable: {exc}")
    if result.returncode != 0:
        stderr = (result.stderr or b"").decode("utf-8", errors="replace").strip()
        return TokenSource(present=False, reason=f"gh auth token failed: {stderr[:200]}")
    if not (result.stdout or b"").strip():
        return TokenSource(present=False, reason="gh auth token returned empty output")
    return TokenSource(present=True, source="gh")


def capabilities_from_permissions(
    login: str,
    permissions: dict[str, Any] | None,
    *,
    has_issues: bool = True,
) -> Capabilities:
    """Derive capability from a repository `permissions` object.

    GitHub reports `{admin, maintain, push, triage, pull}` for the authenticated
    user. Submitting a review needs read access; label management needs triage or
    push. Anything the payload does not state is UNKNOWN and therefore absent.
    """
    caps = Capabilities(login=login)
    if not isinstance(permissions, dict) or not permissions:
        caps.unknown = ("permissions",)
        caps.reasons.append("repository payload carried no permissions object")
        return caps

    flags = {k: bool(v) for k, v in permissions.items() if isinstance(v, bool)}
    caps.permissions = flags

    pull = flags.get("pull", False)
    triage = flags.get("triage", False)
    push = flags.get("push", False)
    admin = flags.get("admin", False)

    caps.repo_readable = pull or triage or push or admin
    caps.pulls_readable = caps.repo_readable
    # A review submission requires read access to the repository.
    caps.can_submit_review = caps.repo_readable
    caps.can_create_issue = caps.repo_readable and bool(has_issues)
    caps.can_add_labels = triage or push or admin

    if not caps.repo_readable:
        caps.reasons.append("authenticated identity has no read permission")
    if not caps.can_add_labels:
        caps.reasons.append("no triage/push permission: label changes go to a human")
    if not caps.can_create_issue:
        caps.reasons.append("issues unavailable: findings cannot be filed as issues")
    return caps


def probe(
    config: dict[str, Any],
    state,
    repo: str,
    *,
    _reader=None,
    _runner=subprocess.run,
) -> dict[str, Any]:
    """Probe auth + capability for `repo`. Read-only; never raises."""
    token = resolve_token_source(_runner=_runner)
    report: dict[str, Any] = {"repo": repo, "token": token.as_dict()}

    if not token.present:
        caps = Capabilities()
        caps.reasons.append(token.reason or "no auth token available")
        caps.unknown = ("permissions",)
        report["capabilities"] = caps.as_dict()
        report["mode"] = UNUSABLE
        return report

    reader = _reader
    if reader is None:
        from github_rest import RestReader

        reader = RestReader(config, state)

    login = ""
    try:
        login = (reader.viewer() or {}).get("login", "")
    except Exception as exc:
        report["viewer_error"] = str(exc)[:200]

    try:
        meta = reader.repo_meta(repo) or {}
    except Exception as exc:
        caps = Capabilities(login=login)
        caps.reasons.append(f"repository unreadable: {str(exc)[:200]}")
        caps.unknown = ("permissions",)
        report["capabilities"] = caps.as_dict()
        report["mode"] = UNUSABLE
        return report

    caps = capabilities_from_permissions(
        login or (meta.get("owner") or {}).get("login", ""),
        meta.get("permissions"),
        has_issues=bool(meta.get("has_issues", True)),
    )
    report["capabilities"] = caps.as_dict()
    report["mode"] = caps.mode
    return report


def downgrade_config_for_mode(config: dict[str, Any], mode: str) -> dict[str, Any]:
    """Return a copy of `config` with authority reduced to fit a proven mode.

    Capability can only ever REDUCE configured authority; it never grants any. A
    repo where writes cannot be proven runs advisory-only with actions routed to
    the human queue.
    """
    import copy

    reduced = copy.deepcopy(config)
    if mode == FULL:
        return reduced

    authority = dict(reduced.get("authority") or {})
    for activity in ("approve", "request_changes", "comment", "fix"):
        if authority.get(activity) == "live":
            authority[activity] = "human_escalation"
    reduced["authority"] = authority

    approval = dict(reduced.get("approval") or {})
    if approval.get("mode") == "live":
        approval["mode"] = "human_escalation"
    approval["approval_enabled"] = False
    reduced["approval"] = approval
    return reduced
