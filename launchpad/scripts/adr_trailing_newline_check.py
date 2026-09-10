#!/usr/bin/env python3
"""Check that every accepted ADR file ends with exactly one trailing newline.

launchpad-26/buzz#1453: all 29 ADRs that predate the batch filed as PRs
#1433-#1446 end with a trailing newline. Those 14 new ADR files did not,
because whatever wrote them (an agent session's file-write tool, not a
committed script -- see #1453's investigation notes) did not add one. The
files themselves are cosmetic to open one at a time, but the reason to guard
it here rather than let it recur is that it makes the last line of every
future record noisy in diffs, on every ADR from now on.

What counts as a failure:

- **No trailing newline at all** -- the classic `\\ No newline at end of
  file` diff marker this issue was filed against.
- **More than one trailing newline** -- equally not "exactly one", and just
  as easy for a generator to produce by accident (e.g. an extra blank line
  appended after already-correct content).

An empty file is skipped rather than failed: there is no line to end, so
"ends with one newline" does not apply to it, and failing an empty file
would be asserting something about content that is not there.

Usage:
    python3 adr_trailing_newline_check.py [repo-root]

Exits 0 when every ADR file passes, 1 otherwise. Failures print one per
line, followed by a `failed: N` summary line -- matching the shape of
adr_boundary_check.py in this same directory.
"""

import sys
from pathlib import Path

DECISIONS_REL = "launchpad/decisions"


def find_violations(decisions_dir: Path) -> list[str]:
    """Return one message per ADR-*.md file that fails the trailing-newline check.

    Only ADR-*.md files are checked -- launchpad/decisions/README.md and any
    other non-ADR file in the directory are outside what #1453 is about, and
    checking them would widen this guard past the issue that asked for it.
    """
    failures = []
    for path in sorted(decisions_dir.glob("ADR-*.md")):
        data = path.read_bytes()
        if not data:
            # Nothing to check: an empty file has no trailing newline to be
            # missing or doubled.
            continue
        rel = path.name
        if not data.endswith(b"\n"):
            failures.append(f"{rel} has no trailing newline")
        elif data.endswith(b"\n\n"):
            failures.append(f"{rel} ends with more than one trailing newline")
    return failures


def main(argv):
    root = Path(argv[1] if len(argv) > 1 else ".").resolve()
    decisions_dir = root / DECISIONS_REL

    if not decisions_dir.is_dir():
        print(f"FAIL missing directory: {decisions_dir}")
        return 1

    failures = find_violations(decisions_dir)

    for f in failures:
        print(f"FAIL {f}")
    print(f"failed: {len(failures)}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
