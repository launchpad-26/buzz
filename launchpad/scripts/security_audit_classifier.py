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
from typing import Optional, Set

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
