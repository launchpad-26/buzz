"""`rqa.cli` — E-17's command surface and E-21's `rqa tick` entry point.

`main(argv)` is the whole public surface: parse, build real collaborators,
call exactly one provider, render, exit. See `rqa/cli/main.py`.
"""

from __future__ import annotations

from rqa.cli.main import main

__all__ = ["main"]
