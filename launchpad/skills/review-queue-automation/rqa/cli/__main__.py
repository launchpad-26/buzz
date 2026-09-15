"""`python3 -m rqa.cli <command> ...` — the `rqa` command surface, until a
packaged console-script entry point exists (`CUTOVER.md`, #2212)."""

from __future__ import annotations

import sys

from rqa.cli.main import main

if __name__ == "__main__":
    sys.exit(main())
