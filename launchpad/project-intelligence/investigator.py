"""Investigator -- issue #208, STEP 1.

The tool surface from launchpad/Research/project-intelligence-layer-design.md
(§ Reasoning Rules, "Investigation tool surface"): search_text, search_symbols,
find_references, read_file, list_directory, inspect_git_history, git_blame,
inspect_dependency, run_command, run_test, inspect_logs, query_build_system.

Calling convention (the design doc's decision logic, documented here rather than
enforced by any code -- the caller that applies it is #211's KnowledgeAgent,
which does not exist yet):
  1. Check confidence first (ProjectMemory/ProjectGraph, if already queried).
  2. Verify important claims even when confident -- call a tool anyway.
  3. Investigate when not confident: search broadly, narrow, read, follow
     relationships, inspect history where intent/evolution matters.
  4. Construct the explanation only after 1-3, labeling non-FACT claims.

Every tool in TOOL_REGISTRY is READ_ONLY except run_command and run_test,
which are EXECUTE -- calling either must surface that flag to the caller
before the subprocess actually runs, not silently (see run_tool()).
"""

from __future__ import annotations

from pathlib import Path
from typing import Callable, Literal

SideEffect = Literal["READ_ONLY", "EXECUTE"]

REPO_ROOT = Path(__file__).resolve().parents[2]


def read_file(path: str, start_line: int | None = None, end_line: int | None = None) -> str:
    """Read a file, or a line range of one, relative to the repo root."""
    text = (REPO_ROOT / path).read_text()
    if start_line is None and end_line is None:
        return text
    lines = text.splitlines()
    return "\n".join(lines[(start_line or 1) - 1 : end_line])


def list_directory(path: str = ".") -> list[str]:
    """List immediate entries of a directory, relative to the repo root."""
    return sorted(p.name + ("/" if p.is_dir() else "") for p in (REPO_ROOT / path).iterdir())


def inspect_logs(path: str, tail_lines: int | None = None) -> str:
    """Read a log file. A log is just a file; no separate mechanism from
    read_file, but named distinctly per the design doc's tool table."""
    text = (REPO_ROOT / path).read_text()
    if tail_lines is None:
        return text
    return "\n".join(text.splitlines()[-tail_lines:])


TOOL_REGISTRY: dict[str, tuple[Callable, SideEffect]] = {
    "read_file": (read_file, "READ_ONLY"),
    "list_directory": (list_directory, "READ_ONLY"),
    "inspect_logs": (inspect_logs, "READ_ONLY"),
}
