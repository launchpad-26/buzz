"""Tracked-files check for #68.

An ignore pattern only stops a *future* `git add`. A file already committed
before the pattern existed stays tracked regardless of what `.gitignore` says
today — this check is independent of `security_audit_ignore_coverage_check.py`
for exactly that reason: it asks "is anything matching a sensitive shape
actually IN the tree", never "would it be allowed in if added now".

Two things this check does, corresponding to two DoD items:

  1. Scan every tracked file (``git ls-tree -r``) against the sensitive-shape
     patterns and FAIL on any non-exempt match.
  2. In PR mode only (``GITHUB_BASE_REF`` set), diff the two ignore files
     against the PR's base and WARN if a newly-added ignore line would cover
     a path that is already tracked — the shape an accidental cover-up takes
     in a diff: "hide it going forward" without removing what is already
     there. WARN, not FAIL: the pattern addition may be entirely legitimate
     (tightening coverage for new files), it is the *combination* with an
     existing tracked match that is worth a human's attention, and (1) above
     already fails the run if the tracked file itself is sensitive.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path
from typing import List, Optional

from security_audit_core import CheckResult, Status
from security_audit_ignore_coverage_check import REQUIRED_COVERAGE

NAME = "tracked-sensitive-files"

#: Path-shape patterns a tracked file must never match. Kept as compiled
#: regexes (not the gitignore glob syntax REQUIRED_COVERAGE uses) because this
#: check matches real repo-relative paths, not gitignore's own matcher.
_SENSITIVE_PATTERNS = [
    re.compile(r"(^|/)\.env$"),
    re.compile(r"(^|/)\.env\.local$"),
    re.compile(r"(^|/)\.env\.[^/]+\.local$"),
    re.compile(r"(^|/)identity\.key$"),
    re.compile(r"\.pem$"),
    re.compile(r"\.key$"),
    re.compile(r"(^|/)id_rsa$"),
    re.compile(r"(^|/)id_ed25519$"),
    re.compile(r"(^|/)seed/"),
    re.compile(r"(^|/)seed\.sample/"),
]

#: Explicitly safe by naming convention — a template meant to be copied and
#: filled in, never a real value. Verified against every current match of the
#: patterns above before this exemption was added (`.env.example`,
#: `deploy/compose/.env.example`, `mobile/.env.json.example` — all three are
#: template files, confirmed by content, not just by name).
_EXEMPT_SUFFIX = re.compile(r"\.example$")


def _tracked_paths(repo_root: Path) -> Optional[List[str]]:
    try:
        result = subprocess.run(
            ["git", "ls-tree", "-r", "-z", "--name-only", "HEAD"],
            cwd=repo_root,
            check=True,
            capture_output=True,
            timeout=30,
            encoding="utf-8",
            errors="replace",
        )
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError):
        return None
    return [p for p in result.stdout.split("\0") if p]


def _matches_sensitive_shape(path: str) -> bool:
    if _EXEMPT_SUFFIX.search(path):
        return False
    return any(pattern.search(path) for pattern in _SENSITIVE_PATTERNS)


def _check_newly_hidden_tracked_files(repo_root: Path, tracked: List[str]) -> List[str]:
    """PR mode only: lines added to a watched .gitignore in this PR that now
    cover an already-tracked path. Returns human-readable descriptions, empty
    if not in PR mode, the base ref can't be fetched, or nothing matches.
    """
    import os

    base_ref = os.environ.get("GITHUB_BASE_REF", "")
    if not base_ref:
        return []

    try:
        subprocess.run(
            ["git", "fetch", "--depth=1", "origin", base_ref],
            cwd=repo_root,
            check=True,
            capture_output=True,
            timeout=60,
        )
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError):
        return []

    findings: List[str] = []
    for gitignore_path in REQUIRED_COVERAGE:
        diff = subprocess.run(
            ["git", "diff", "--unified=0", f"FETCH_HEAD..HEAD", "--", gitignore_path],
            cwd=repo_root,
            capture_output=True,
            timeout=30,
            encoding="utf-8",
            errors="replace",
        )
        if diff.returncode != 0:
            continue
        added_lines = [
            line[1:].strip()
            for line in diff.stdout.splitlines()
            if line.startswith("+") and not line.startswith("+++")
        ]
        for added_pattern in added_lines:
            if not added_pattern:
                continue
            # Match as a plain substring/glob-lite check against tracked
            # paths — good enough to flag "this new pattern's literal text
            # is a path component that's already tracked", which is the
            # accidental-cover-up shape this half of the check exists for.
            # A full gitignore-matcher reimplementation is not worth it here:
            # a false negative just means (1) above still catches the file
            # if it's genuinely sensitive, and a false positive is a WARN, not
            # a FAIL.
            stripped = added_pattern.rstrip("/")
            for tracked_path in tracked:
                if stripped and (
                    tracked_path == stripped
                    or tracked_path.endswith("/" + stripped)
                    or f"/{stripped}/" in f"/{tracked_path}/"
                ):
                    findings.append(f"{gitignore_path}: new pattern {added_pattern!r} covers tracked {tracked_path!r}")
    return findings


def run(repo_root: Path) -> CheckResult:
    tracked = _tracked_paths(repo_root)
    if tracked is None:
        return CheckResult(NAME, Status.INDETERMINATE, "could not list tracked files (git ls-tree failed)")

    sensitive_hits = sorted(p for p in tracked if _matches_sensitive_shape(p))
    newly_hidden = _check_newly_hidden_tracked_files(repo_root, tracked)

    if sensitive_hits:
        return CheckResult(
            NAME,
            Status.FAIL,
            f"{len(sensitive_hits)} tracked file(s) match a sensitive shape: "
            + "; ".join(sensitive_hits[:10])
            + (f", and {len(sensitive_hits) - 10} more" if len(sensitive_hits) > 10 else ""),
        )
    if newly_hidden:
        return CheckResult(
            NAME,
            Status.WARN,
            f"{len(newly_hidden)} newly-added ignore pattern(s) cover already-tracked content: "
            + "; ".join(newly_hidden),
        )
    return CheckResult(
        NAME,
        Status.PASS,
        f"no tracked file matches a sensitive shape ({len(tracked)} tracked files checked)",
    )
