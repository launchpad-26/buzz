#!/usr/bin/env python3
"""Classify a repository path as fork-added or inherited-from-upstream.

Method: fetch `block/buzz`'s default branch as a shallow, unmerged ref and list
its tree with `git ls-tree`. A path present in that tree is `inherited` —
Launchpad may have modified it, but it did not originate here. A path absent
from that tree is `fork-added`. This is origin classification, not a diff: it
answers "did this path exist upstream at all", not "does it still match
upstream" — #62's later checks that care about drift from upstream are separate
work, not this classifier's job.

`git` over the network is the one thing this can fail at, and it is only ever
called once per audit run (the caller fetches the tree once and classifies many
paths against it) rather than once per path, so an unreachable upstream costs
one timeout, not one per file. When it fails, `fetch_upstream_paths` returns
`None` and `classify` reports `indeterminate` for every path — never `fork-added`
and never `inherited`. Guessing either way is wrong in a specific, asymmetric
sense: calling an inherited file fork-added makes the audit permanently red over
files nobody here wrote, and calling a fork-added file inherited makes the audit
blind to exactly the files #62 exists to watch.
"""

import re
import subprocess
from pathlib import Path, PurePosixPath
from typing import Dict, Optional, Set

#: Matches a Windows drive letter root ("C:/", "d:/") after backslash-to-slash
#: normalization. PurePosixPath.is_absolute() only recognizes a leading "/" --
#: it has no concept of a drive letter, so "C:/Users/x/buzz/foo.py" reads as
#: NOT absolute to it and would otherwise fall through to the plain membership
#: check below, almost certainly returning the wrong-direction "fork-added"
#: guess this function exists to avoid. This repo already treats Windows-style
#: paths as a real input class (the backslash normalization two lines below
#: predates this check), so the absolute-path guard must catch this form too.
_WINDOWS_DRIVE_ROOT = re.compile(r"^[A-Za-z]:/")

UPSTREAM_URL = "https://github.com/block/buzz.git"
UPSTREAM_REF = "main"


def fetch_upstream_paths(repo_root: Path, timeout: int = 30) -> Optional[Set[str]]:
    """The set of file paths in block/buzz's default branch tree, or None if unreachable."""
    try:
        subprocess.run(
            ["git", "fetch", "--depth=1", UPSTREAM_URL, UPSTREAM_REF],
            cwd=repo_root,
            check=True,
            capture_output=True,
            timeout=timeout,
        )
        result = subprocess.run(
            # -z, not the default newline-separated output: git's default quoting
            # (core.quotepath, on by default) C-style-escapes any path containing a
            # non-ASCII or otherwise "unusual" byte, e.g. `"caf\303\251.md"` for
            # `café.md`. classify() compares raw strings against this set, so a
            # quoted path would never match its own unquoted form and would be
            # misclassified fork-added instead of inherited. -z sidesteps quoting
            # entirely rather than disabling it with a config flag, which also
            # covers a filename containing a literal newline that plain
            # newline-splitting would silently corrupt.
            ["git", "ls-tree", "-r", "-z", "--name-only", "FETCH_HEAD"],
            cwd=repo_root,
            check=True,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError):
        return None
    return set(filter(None, result.stdout.split("\0")))


def classify(path: str, upstream_paths: Optional[Set[str]]) -> str:
    """'fork-added', 'inherited', or 'indeterminate' when upstream_paths is None."""
    if upstream_paths is None:
        return "indeterminate"
    normalized = path.replace("\\", "/")
    if normalized.startswith("./"):
        normalized = normalized[2:]
    # git ls-tree's output (what upstream_paths is built from) is always relative.
    # An absolute path can't be safely compared against it without knowing the
    # repo root, and guessing fork-added for it is exactly the wrong-direction
    # guess this module's docstring warns against — indeterminate is honest.
    if PurePosixPath(normalized).is_absolute() or _WINDOWS_DRIVE_ROOT.match(normalized):
        return "indeterminate"
    return "inherited" if normalized in upstream_paths else "fork-added"


def fetch_upstream_blobs(repo_root: Path, timeout: int = 30) -> Optional[Dict[str, str]]:
    """Map every upstream path to its blob OID, or None if upstream is unreachable.

    Same single fetch as `fetch_upstream_paths`, one column wider: `git ls-tree`
    already carries the OID, so identity costs no extra network. Callers that
    only need origin should keep using `fetch_upstream_paths`.

    Origin is not enough for a check that asks "is the cohort accountable for
    this file". A path present upstream may still have been modified here, and a
    modification is exactly where cohort-owned content could hide inside an
    inherited filename. Comparing OIDs answers "is this byte-for-byte upstream's
    file", which is the question that licenses skipping it.
    """
    try:
        subprocess.run(
            ["git", "fetch", "--depth=1", UPSTREAM_URL, UPSTREAM_REF],
            cwd=repo_root,
            check=True,
            capture_output=True,
            timeout=timeout,
        )
        result = subprocess.run(
            # -z for the same quoting reason `fetch_upstream_paths` documents.
            # Default (non---name-only) output is "<mode> <type> <oid>\t<path>".
            ["git", "ls-tree", "-r", "-z", "FETCH_HEAD"],
            cwd=repo_root,
            check=True,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError):
        return None
    blobs: Dict[str, str] = {}
    for entry in filter(None, result.stdout.split("\0")):
        meta, _, path = entry.partition("\t")
        parts = meta.split()
        if not path or len(parts) < 3:
            continue
        blobs[path] = parts[2]
    return blobs


def local_blob(repo_root: Path, path: str, timeout: int = 30) -> Optional[str]:
    """The blob OID of `path` at HEAD, or None when it cannot be resolved."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", f"HEAD:{path}"],
            cwd=repo_root,
            check=True,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError):
        return None
    return result.stdout.strip() or None


def divergence(path: str, repo_root: Path, upstream_blobs: Optional[Dict[str, str]]) -> str:
    """Ownership of one path, as one of four answers.

    - `fork-added`         — absent upstream. The cohort wrote it.
    - `inherited-modified` — present upstream, different content here.
    - `inherited-identical`— present upstream, byte-for-byte identical.
    - `indeterminate`      — upstream unreachable, or the local OID would not
                             resolve. Never guessed in either direction, for the
                             asymmetry this module's docstring sets out.

    Only `inherited-identical` licenses a caller to treat a file as none of the
    cohort's business. The other three are all cohort-accountable or unknown.
    """
    if upstream_blobs is None:
        return "indeterminate"
    normalized = path.replace("\\", "/")
    if normalized.startswith("./"):
        normalized = normalized[2:]
    if PurePosixPath(normalized).is_absolute() or _WINDOWS_DRIVE_ROOT.match(normalized):
        return "indeterminate"
    upstream_oid = upstream_blobs.get(normalized)
    if upstream_oid is None:
        return "fork-added"
    here = local_blob(repo_root, normalized)
    if here is None:
        return "indeterminate"
    return "inherited-identical" if here == upstream_oid else "inherited-modified"
