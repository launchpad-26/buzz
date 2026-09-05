"""`check-page` / `screen-content` -- the local-only half of professor.py's tool
layer (redesign doc §4's `localcmd` subgraph: "no network, runs on every write").

Step 1 stub: reachable without crashing, not yet implemented. Step 4 (`check-page`)
and step 6 (`screen-content`) replace this with real implementations against
`tools/contract/page-contract.md` and `tools/contract/sensitive-patterns.md`
respectively.
"""

import sys


def check_page(file_path: str, target: str, pack_root: str) -> int:
    print("check-page: not yet implemented (step 4)", file=sys.stderr)
    return 1


def screen_content(file_path: str, pack_root: str) -> int:
    print("screen-content: not yet implemented (step 6)", file=sys.stderr)
    return 1
