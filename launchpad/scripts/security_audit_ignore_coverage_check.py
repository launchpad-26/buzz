"""Ignore-coverage check for #68: the patterns that must never stop being
ignored, asserted directly against the files that carry them — not inferred
from `git check-ignore`, which would also report false if the file simply
doesn't exist.

Two files, because that is where the coverage actually lives today:

  .gitignore                          repo-wide: env files, identity keys,
                                       key/cert material.
  launchpad/deploy/archived/.gitignore  the deploy-secrets folder's own patterns
                                       (env, keys, the generated `seed/` /
                                       `seed.sample/` cloud-init output).

The second path moved once already — from `launchpad/deploy/.gitignore` to
`launchpad/deploy/archived/.gitignore` when the deploy method was archived,
after #68 was filed against the old path. Asserted against where the file
actually is today, not where the issue text says it was. If it moves again,
this check goes INDETERMINATE (missing file), not silently passes on nothing
— see `_read_lines`.

Coverage is checked as **literal line presence** — the exact pattern string
must appear as its own line in the file. This is deliberately stricter than
asking gitignore's own matcher whether a sample path would be ignored: a
functionally-equivalent but differently-spelled pattern (`*.env` vs `.env`)
would pass a matcher-based check while silently changing what's actually
covered, and this check exists to catch that kind of drift, not paper over it.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List

from security_audit_core import CheckResult, Status

NAME = "ignore-coverage"

#: repo-relative gitignore path -> patterns that MUST be present, one per line.
REQUIRED_COVERAGE: Dict[str, List[str]] = {
    ".gitignore": [
        ".env",
        ".env.local",
        ".env.*.local",
        "identity.key",
        "**/identity.key",
        "*.pem",
        "*.key",
        "id_rsa",
        "id_ed25519",
    ],
    "launchpad/deploy/archived/.gitignore": [
        "seed/",
        "seed.sample/",
    ],
}


def _read_lines(path: Path) -> List[str] | None:
    try:
        return path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return None


def run(repo_root: Path) -> CheckResult:
    missing: List[str] = []
    unreadable: List[str] = []

    for rel_path, patterns in REQUIRED_COVERAGE.items():
        lines = _read_lines(repo_root / rel_path)
        if lines is None:
            unreadable.append(rel_path)
            continue
        line_set = set(lines)
        for pattern in patterns:
            if pattern not in line_set:
                missing.append(f"{rel_path}: {pattern!r}")

    if unreadable:
        return CheckResult(
            NAME,
            Status.INDETERMINATE,
            "could not read " + ", ".join(unreadable) + " — coverage cannot be asserted "
            "against a file this check cannot find; this is not the same as the patterns "
            "being absent from an existing file",
        )
    if missing:
        return CheckResult(
            NAME,
            Status.FAIL,
            f"{len(missing)} required ignore pattern(s) missing: " + "; ".join(missing),
        )
    return CheckResult(
        NAME,
        Status.PASS,
        f"all {sum(len(p) for p in REQUIRED_COVERAGE.values())} required patterns present "
        f"across {len(REQUIRED_COVERAGE)} file(s)",
    )
