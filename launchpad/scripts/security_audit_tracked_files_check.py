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
from security_audit_classifier import divergence, fetch_upstream_blobs
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
    # No .example (or any other) suffix exemption here, deliberately: every
    # pattern above is end-anchored to its own exact filename shape
    # (.env, .key, .pem, id_rsa, id_ed25519), so a `foo.env.example` never
    # matches those in the first place -- an exemption bought them nothing.
    # It did buy something real to exempt, though: seed/ and seed.sample/
    # match on directory component, not filename, so a tracked
    # seed/authorized_keys.example previously slipped past a suffix
    # exemption despite being exactly the shape #68 documents a real past
    # incident for (a committed SSH public key). Found via review-code
    # against #275; verified no fixture in this suite or #67's own
    # .gitleaks.toml relied on a *.example exemption existing here.
    return any(pattern.search(path) for pattern in _SENSITIVE_PATTERNS)


def _check_newly_hidden_tracked_files(
    repo_root: Path, tracked: List[str]
) -> Optional[List[str]]:
    """PR mode only: lines added to a watched .gitignore in this PR that now
    cover an already-tracked path. Returns human-readable descriptions, an
    empty list if not in PR mode or nothing matches, and `None` if the
    heuristic could not run at all (git fetch or diff failed) — `None` and
    `[]` are deliberately different: a git failure is "could not determine",
    not "nothing newly hidden", the same distinction `_tracked_paths` already
    draws for the primary FAIL-capable scan above.
    """
    import os

    base_ref = os.environ.get("GITHUB_BASE_REF", "")
    if not base_ref:
        return []

    try:
        # No --depth=1: same bug as security_audit_secrets_check.py's PR-diff
        # fetch (fixed on #271 after a real CI run reproduced it) -- a shallow
        # fetch of base_ref grafts a new boundary onto that ref even when the
        # checkout already has full history, breaking FETCH_HEAD..HEAD's
        # ancestry once base_ref has advanced past this branch's merge-base.
        # Here it would silently widen "lines added to the ignore file in
        # this PR" to "the ignore file's entire history", which degrades to
        # WARN rather than a hard FAIL, but is still wrong and worth fixing
        # at the same time.
        subprocess.run(
            ["git", "fetch", "origin", base_ref],
            cwd=repo_root,
            check=True,
            capture_output=True,
            timeout=60,
        )
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError):
        # Could not determine — not the same as "nothing newly hidden". A
        # bare `return []` here previously made a git failure indistinguishable
        # from a clean scan; see the docstring above and `run()`'s handling of
        # `None`.
        return None

    findings: List[str] = []
    diff_failed = False
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
            # Record and keep scanning the other watched gitignore path(s) —
            # a real finding there must not be suppressed by an unrelated
            # file's diff failure. Only surfaced as `None` below if nothing
            # was found despite the failure (see the same distinction above).
            diff_failed = True
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
    if diff_failed and not findings:
        return None
    return findings


def _partition_by_ownership(
    repo_root: Path, hits: List[str]
) -> tuple[List[str], List[str], List[str]]:
    """Split sensitive-shaped hits into (cohort, upstream_identical, unknown).

    WHY OWNERSHIP MATTERS HERE. This is a fork that operates the upstream
    product rather than developing it. Upstream ships APNs test fixtures that
    are genuinely private-key-shaped and genuinely private keys
    (`crates/buzz-push-gateway/tests/fixtures/apns-test-*.pem`, from
    `c432a111c`, an ancestor of `block/buzz@main`, byte-for-byte identical
    here). This check flagged all six on every branch cut after 2026-08-28, so
    `audit` was red on trunk and on every pull request regardless of content
    (launchpad-26/buzz#1965). A deterministic check that fails for everyone
    stops being read.

    The cohort cannot fix those files — it does not own them, and it does not
    move or rename upstream paths. What it can do is be precise about what it is
    accountable for. So this narrows by OWNERSHIP, not by adding an exemption
    list: an allowlist would be a standing hole, and this check deliberately has
    none (see `_matches_sensitive_shape`, where a suffix exemption was removed
    after one let a tracked `seed/authorized_keys.example` through).

    Identity, not origin. A file present upstream but MODIFIED here still fails:
    an inherited filename is exactly where cohort-added key material could hide.
    """
    upstream_blobs = fetch_upstream_blobs(repo_root)
    cohort: List[str] = []
    upstream_identical: List[str] = []
    unknown: List[str] = []
    for path in hits:
        verdict = divergence(path, repo_root, upstream_blobs)
        if verdict == "inherited-identical":
            upstream_identical.append(path)
        elif verdict == "indeterminate":
            unknown.append(path)
        else:  # fork-added or inherited-modified — the cohort is accountable
            cohort.append(path)
    return cohort, upstream_identical, unknown


def run(repo_root: Path) -> CheckResult:
    tracked = _tracked_paths(repo_root)
    if tracked is None:
        return CheckResult(NAME, Status.INDETERMINATE, "could not list tracked files (git ls-tree failed)")

    sensitive_hits = sorted(p for p in tracked if _matches_sensitive_shape(p))
    newly_hidden = _check_newly_hidden_tracked_files(repo_root, tracked)

    cohort_hits: List[str] = []
    upstream_hits: List[str] = []
    unknown_hits: List[str] = []
    if sensitive_hits:
        cohort_hits, upstream_hits, unknown_hits = _partition_by_ownership(
            repo_root, sensitive_hits
        )

    if cohort_hits:
        return CheckResult(
            NAME,
            Status.FAIL,
            f"{len(cohort_hits)} cohort-owned tracked file(s) match a sensitive shape: "
            + "; ".join(cohort_hits[:10])
            + (f", and {len(cohort_hits) - 10} more" if len(cohort_hits) > 10 else ""),
        )
    if unknown_hits:
        # Upstream unreachable: ownership is unknown, so neither failing nor
        # passing is honest. INDETERMINATE is visibly not-green and cannot be
        # mistaken for a clean result.
        return CheckResult(
            NAME,
            Status.INDETERMINATE,
            f"could not establish upstream ownership for {len(unknown_hits)} "
            f"sensitive-shaped tracked file(s): " + "; ".join(unknown_hits[:10]),
        )
    if newly_hidden:
        return CheckResult(
            NAME,
            Status.WARN,
            f"{len(newly_hidden)} newly-added ignore pattern(s) cover already-tracked content: "
            + "; ".join(newly_hidden),
        )
    # The upstream-identical hits are named, not silently dropped. A skip nobody
    # can see is indistinguishable from a check that stopped looking.
    suffix = ""
    if upstream_hits:
        suffix = (
            f"; {len(upstream_hits)} sensitive-shaped file(s) are byte-for-byte "
            f"upstream's and not cohort-owned: " + "; ".join(upstream_hits[:10])
            + (f", and {len(upstream_hits) - 10} more" if len(upstream_hits) > 10 else "")
        )
    return CheckResult(
        NAME,
        Status.PASS,
        f"no cohort-owned tracked file matches a sensitive shape "
        f"({len(tracked)} tracked files checked){suffix}",
    )
