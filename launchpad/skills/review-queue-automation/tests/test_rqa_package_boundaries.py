#!/usr/bin/env python3
"""Shared enforcement of every part contract's package-front-door rule."""

from __future__ import annotations

import ast
import pathlib


RQA = pathlib.Path(__file__).resolve().parent.parent / "rqa"
PARTS = frozenset(
    path.name for path in RQA.iterdir() if path.is_dir() and (path / "__init__.py").is_file()
)

# These exceptions are explicit in their owning part contracts. P-04 makes its one
# path matcher a qualified submodule import for P-06 and P-13, while P-01 retains
# ownership of the deterministic identity primitive P-09 uses for mutation ids.
ALLOWED = frozenset(
    {
        ("harness/risk.py", "rqa.protocol.paths"),
        ("github/writes.py", "rqa.intake.identity"),
        ("reuse/obligations.py", "rqa.protocol.paths"),
    }
)


def test_cross_part_imports_use_package_front_doors() -> None:
    found: set[tuple[str, str]] = set()
    offenders: list[tuple[str, int, str]] = []

    for path in sorted(RQA.rglob("*.py")):
        relative = path.relative_to(RQA)
        owner = relative.parts[0]
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            modules: list[str] = []
            if isinstance(node, ast.ImportFrom) and node.module:
                modules.append(node.module)
            elif isinstance(node, ast.Import):
                modules.extend(alias.name for alias in node.names)

            for module in modules:
                segments = module.split(".")
                if len(segments) < 3 or segments[0] != "rqa":
                    continue
                target = segments[1]
                if target not in PARTS or target == owner:
                    continue
                key = (str(relative), module)
                if key in ALLOWED:
                    found.add(key)
                else:
                    offenders.append((str(relative), node.lineno, module))

    assert offenders == [], offenders
    assert found == ALLOWED, f"documented package-boundary exceptions drifted: {found ^ ALLOWED}"
