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

import subprocess
from pathlib import Path
from typing import Optional, Set

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
            ["git", "ls-tree", "-r", "--name-only", "FETCH_HEAD"],
            cwd=repo_root,
            check=True,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError):
        return None
    return set(result.stdout.splitlines())


def classify(path: str, upstream_paths: Optional[Set[str]]) -> str:
    """'fork-added', 'inherited', or 'indeterminate' when upstream_paths is None."""
    if upstream_paths is None:
        return "indeterminate"
    return "inherited" if path.replace("\\", "/") in upstream_paths else "fork-added"
