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

import json
import subprocess
from dataclasses import dataclass
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


@dataclass(frozen=True)
class TextMatch:
    file: str
    line: int
    text: str


def search_text(pattern: str, regex: bool = False, glob: str = "*") -> list[TextMatch]:
    """Literal or regex text search across the repo. Uses plain `grep`, not
    RepoQL -- this is the one tool with no structural need for the index, and
    avoiding the dependency here means one less tool affected if the RepoQL
    host is unavailable.
    """
    cmd = ["grep", "-rn", "--include", glob]
    if not regex:
        cmd.append("-F")
    cmd += [pattern, "."]
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=REPO_ROOT)
    matches = []
    for line in result.stdout.splitlines():
        # grep -n output: "./path/to/file:LINE:text"
        path, lineno, text = line.split(":", 2)
        matches.append(TextMatch(file=path.removeprefix("./"), line=int(lineno), text=text))
    return matches


@dataclass(frozen=True)
class SymbolMatch:
    qualified_name: str
    kind: str
    file: str
    signature: str


def search_symbols(name: str, crate: str | None = None) -> list[SymbolMatch]:
    """Find symbols by name via RepoQL's Functions view -- structured data
    (kind, declaring type, signature) a text search alone cannot give.
    """
    where = f"name = '{name}'"
    if crate:
        where += f" AND file LIKE '%crates/{crate}/%'"
    sql = f"SELECT qualified_name, function_kind, declaring_type, file, signature FROM Functions WHERE {where}"
    result = subprocess.run(["rql", "query", sql, "--json"], capture_output=True, text=True, check=True, cwd=REPO_ROOT)
    rows = json.loads(result.stdout)
    return [
        SymbolMatch(
            qualified_name=r["qualified_name"],
            kind="method" if r.get("declaring_type") else "function",
            file=r["file"].removeprefix("file:///"),
            signature=r["signature"],
        )
        for r in rows
    ]


@dataclass(frozen=True)
class Reference:
    caller_qualified_name: str
    file: str
    line: int


def find_references(qualified_name: str, crate: str) -> list[Reference]:
    """Real callers of a symbol, not just text matches on its name --
    #208's own Definition of done draws this distinction explicitly.

    A plain text search on the short name alone would match comments, doc
    mentions, and unrelated identifiers sharing the name. This instead:
    1. Enumerates every OTHER function in the crate via search_symbols
       (structured data, not text).
    2. Reads each candidate's own source range (read_file) and checks for a
       real call-site pattern -- the short name immediately followed by `(`
       -- not just the name appearing anywhere in the file.
    This is the same distinction #206's with_called_by() drew (a resolved
    call-site match, not a bare grep), reimplemented here since #208 has no
    dependency on #206's branch-local code.
    """
    short_name = qualified_name.rsplit("::", 1)[-1]
    call_pattern = f"{short_name}("

    sql = (
        "SELECT qualified_name, file, start_line, end_line FROM Functions "
        f"WHERE file LIKE '%crates/{crate}/%' AND qualified_name != '{qualified_name}'"
    )
    result = subprocess.run(["rql", "query", sql, "--json"], capture_output=True, text=True, check=True, cwd=REPO_ROOT)
    candidates = json.loads(result.stdout)

    references = []
    for c in candidates:
        file_rel = c["file"].removeprefix("file:///")
        body = read_file(file_rel, c["start_line"], c["end_line"])
        line_offset = body.find(call_pattern)
        if line_offset == -1:
            continue
        line_number = c["start_line"] + body[:line_offset].count("\n")
        references.append(Reference(caller_qualified_name=c["qualified_name"], file=file_rel, line=line_number))
    return references


TOOL_REGISTRY: dict[str, tuple[Callable, SideEffect]] = {
    "read_file": (read_file, "READ_ONLY"),
    "list_directory": (list_directory, "READ_ONLY"),
    "inspect_logs": (inspect_logs, "READ_ONLY"),
    "search_text": (search_text, "READ_ONLY"),
    "search_symbols": (search_symbols, "READ_ONLY"),
    "find_references": (find_references, "READ_ONLY"),
}
