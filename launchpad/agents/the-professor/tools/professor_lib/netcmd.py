"""`resolve-pin` / `path-exists-at` -- the network-backed half of professor.py's
tool layer (redesign doc §4's `netcmd` subgraph: "external citations only").

Step 1 stub: reachable without crashing, not yet implemented. Step 2 replaces this
with a real port of `server.py`'s `resolve_pin`/`path_exists_at`.
"""

import sys


def resolve_pin(repo: str, ref: str) -> int:
    print("resolve-pin: not yet implemented (step 2)", file=sys.stderr)
    return 1


def path_exists_at(repo: str, commit: str, path: str) -> int:
    print("path-exists-at: not yet implemented (step 2)", file=sys.stderr)
    return 1
