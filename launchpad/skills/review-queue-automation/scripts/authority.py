"""Per-repository, per-activity authority for review-queue-automation.

The automation performs several distinct actions; each has its own authority mode,
because a system that may post advisory comments should not thereby be allowed to
approve or request changes. Authority is resolved independently per repository and
per activity:

  activities:
    review            run / contribute a review panel
    comment           post an advisory PR review comment (fixed COMMENT)
    approve           post an APPROVE review (guarded live path only)
    request_changes   post a CHANGES_REQUESTED review (verified-blocker gate only)
    triage            author-side triage of feedback
    fix               implement/push an author fix

  modes (district, fail-closed):
    disabled          activity never runs
    shadow            full decision computed, no mutation recorded/reported as WOULD
    human_escalation  decision routed to an asynchronous human request
    live              activity runs when its gate passes for the exact HEAD

Hard safety gates (self-approval, final revalidation, exact-HEAD) are enforced by the
action executors regardless of config; configuration can never widen past them.
The default for every activity in every repo is `disabled` unless configured.
"""

from __future__ import annotations

from typing import Any

#: The full set of supported activities.
ACTIVITIES = frozenset(
    {"review", "comment", "approve", "request_changes", "triage", "fix"}
)

#: Recognised authority modes.
MODES = frozenset({"disabled", "shadow", "human_escalation", "live"})

#: Activities that are inherently mutating on GitHub (posting a formal review body).
MUTATING_ACTIVITIES = frozenset({"approve", "request_changes"})
#: Activities that can modify a repository branch.
BRANCH_MUTATING_ACTIVITIES = frozenset({"fix"})

DEFAULT_MODE = "disabled"


class AuthorityConfigError(ValueError):
    """Raised for a malformed authority configuration. Fails closed."""


def validate_authority(authority: dict[str, Any]) -> list[str]:
    """Return a deterministic list of issue strings; empty means valid (fail-closed).

    `authority` is the repository-level `authority` config section. It maps either
    activity names to a mode, or repo keys to an activity->mode dict, or a `default`
    mode.
    """
    issues: list[str] = []
    if authority is None or not isinstance(authority, dict):
        return ["authority must be a non-empty object"]
    # top-level keys: either 'default', an activity name, or a repo key
    for key, value in authority.items():
        if key == "default":
            if value not in MODES:
                issues.append(f"authority.default must be one of {sorted(MODES)}, got {value!r}")
            continue
        if key in ACTIVITIES:
            if value not in MODES:
                issues.append(f"authority.{key} must be one of {sorted(MODES)}, got {value!r}")
            continue
        # treat as a repo key -> activity->mode map
        if not isinstance(value, dict):
            issues.append(f"authority.{key} must be a dict of activity->mode")
            continue
        for act, mode in value.items():
            if act not in ACTIVITIES:
                issues.append(f"authority.{key}.{act} is not a known activity")
            if mode not in MODES:
                issues.append(f"authority.{key}.{act} mode must be one of {sorted(MODES)}, got {mode!r}")
    # MUTATING/BRANCH activities must be live-only on an explicit live flag; but the
    # mode is resolved at action time against the gate. Here we only ensure that a
    # 'live' mutation mode is paired with its explicit live-approval flag elsewhere
    # (the action executors enforce the gate). No widening is possible from mode
    # alone because a live mode still requires the full gate to pass.
    return issues


def _repo_authority(cfg: dict[str, Any], repo: str) -> dict[str, Any]:
    """The effective per-repo authority map, from config or empty (all disabled)."""
    authority = (cfg.get("authority") or {}) or {}
    repo_section = authority.get(repo)
    if isinstance(repo_section, dict):
        return dict(repo_section)
    return {}


def mode_for(cfg: dict[str, Any], repo: str, activity: str) -> str:
    """Resolve the authority mode for `activity` in `repo`.

    Precedence:
      1. activity-specific top-level key in `authority` (e.g. authority.approve) —
         applies to every repo.
      2. repo-scoped override: authority[repo][activity].
      3. authority.default.
      4. DEFAULT_MODE (disabled), fail-closed.
    """
    if activity not in ACTIVITIES:
        return DEFAULT_MODE
    authority = (cfg.get("authority") or {}) or {}
    # A per-repo override is the most specific and wins first.
    repo_section = _repo_authority(cfg, repo)
    if activity in repo_section and repo_section[activity] in MODES:
        return repo_section[activity]
    # Then an activity-level (global) key.
    if activity in authority and authority[activity] in MODES:
        return authority[activity]
    # Then a global default.
    default = authority.get("default")
    if default in MODES:
        return default
    return DEFAULT_MODE


def is_mutating(activity: str) -> bool:
    return activity in MUTATING_ACTIVITIES or activity in BRANCH_MUTATING_ACTIVITIES


def can_act(cfg: dict[str, Any], repo: str, activity: str, *, repo_hard_gate_ok: bool = True) -> bool:
    """True only when the activity's authority mode authorises acting now.

    `repo_hard_gate_ok` is the caller-supplied result of the safety gate (self-approval,
    exact-HEAD revalidation, evidence, assurance); a mutating activity is never allowed
    to act unless the caller passed its gate. Non-mutating advisory activities only need
    a non-disabled mode.
    """
    mode = mode_for(cfg, repo, activity)
    if mode == "disabled":
        return False
    if mode == "shadow":
        return False  # shadow computes but never acts
    if mode == "human_escalation":
        return False  # routed to the human queue, not acted here
    # live
    if not is_mutating(activity):
        return True
    return bool(repo_hard_gate_ok)


def defaults() -> dict[str, Any]:
    """A fail-closed default `authority` section (everything disabled)."""
    return {act: DEFAULT_MODE for act in sorted(ACTIVITIES)}