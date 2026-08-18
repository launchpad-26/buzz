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
which are EXECUTE -- calling either prints the EXECUTE flag before the
subprocess runs and carries it on the returned CommandResult, not silently
(see run_command/run_test).
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


def _rql_read_json(uri_with_modifier: str) -> dict:
    result = subprocess.run(
        ["rql", "read", uri_with_modifier, "--json"], capture_output=True, text=True, check=True, cwd=REPO_ROOT
    )
    return json.loads(result.stdout)


@dataclass(frozen=True)
class CommitSummary:
    hash: str
    date: str
    author: str
    message: str


def inspect_git_history(file: str, start_line: int, end_line: int) -> list[CommitSummary]:
    """Commits touching a file range -- a thin wrapper over RepoQL's `=> history`
    modifier, the same primitive #206 already proved (enrich_git_ownership())."""
    data = _rql_read_json(f"file:///{file}#line={start_line},{end_line} => history")
    return [
        CommitSummary(hash=c["hash"], date=c["date"], author=c["author"], message=c["message"])
        for c in data.get("commits", [])
    ]


@dataclass(frozen=True)
class BlameLine:
    line: int
    content: str
    hash: str
    author: str
    date: str


def git_blame(file: str, start_line: int, end_line: int) -> list[BlameLine]:
    """Line-level authorship -- a thin wrapper over RepoQL's `=> blame` modifier,
    the same primitive #206 already proved."""
    data = _rql_read_json(f"file:///{file}#line={start_line},{end_line} => blame")
    return [
        BlameLine(line=ln["lineNumber"], content=ln["content"], hash=ln["hash"], author=ln["author"], date=ln["date"])
        for ln in data.get("lines", [])
    ]


@dataclass(frozen=True)
class Dependency:
    name: str
    declared: dict  # the crate's own manifest entry, e.g. {"workspace": True}
    resolved: dict  # the actual version/source, following workspace inheritance if present


def inspect_dependency(crate: str, name: str) -> Dependency | None:
    """A named dependency's declared version/source, resolved through
    Cargo's `workspace = true` inheritance -- most of this workspace's
    crates declare deps this way (crates/buzz-core/Cargo.toml), so returning
    the bare `{"workspace": true}` without resolving it would not actually
    answer the question "what version does this crate depend on".
    """
    import tomllib

    crate_manifest = tomllib.loads((REPO_ROOT / "crates" / crate / "Cargo.toml").read_text())
    declared = crate_manifest.get("dependencies", {}).get(name)
    if declared is None:
        return None

    resolved = declared
    if isinstance(declared, dict) and declared.get("workspace") is True:
        root_manifest = tomllib.loads((REPO_ROOT / "Cargo.toml").read_text())
        resolved = root_manifest.get("workspace", {}).get("dependencies", {}).get(name, declared)

    return Dependency(name=name, declared=declared, resolved=resolved)


@dataclass(frozen=True)
class BuildTarget:
    name: str
    kind: list[str]  # e.g. ["lib"], ["bin"], ["test"]
    src_path: str


@dataclass(frozen=True)
class BuildInfo:
    crate: str
    version: str
    edition: str
    targets: list[BuildTarget]


def query_build_system(crate: str) -> BuildInfo:
    """What the build system would do for a crate, without doing it.

    `cargo metadata --no-deps` resolves and prints the manifest graph -- it
    does not invoke rustc, so it produces no build artifacts under target/
    (verified: a directory snapshot of target/ before and after this call is
    identical, see the commit message). --no-deps limits the resolved graph
    to this workspace's own packages, not third-party dependency metadata.
    """
    result = subprocess.run(
        [
            "cargo",
            "metadata",
            "--no-deps",
            "--format-version",
            "1",
            "--manifest-path",
            str(REPO_ROOT / "crates" / crate / "Cargo.toml"),
        ],
        capture_output=True,
        text=True,
        check=True,
        cwd=REPO_ROOT,
    )
    data = json.loads(result.stdout)
    pkg = next(p for p in data["packages"] if p["name"] == crate)
    targets = [
        BuildTarget(name=t["name"], kind=t["kind"], src_path=t["src_path"].removeprefix(str(REPO_ROOT) + "/"))
        for t in pkg["targets"]
    ]
    return BuildInfo(crate=pkg["name"], version=pkg["version"], edition=pkg["edition"], targets=targets)


@dataclass(frozen=True)
class CommandResult:
    side_effect: SideEffect  # always "EXECUTE" -- carried on the result itself,
    # not just printed, so a caller inspecting the return value (not stdout)
    # still cannot miss that a subprocess actually ran.
    command: str
    returncode: int
    stdout: str
    stderr: str


def run_command(command: list[str]) -> CommandResult:
    """Run an arbitrary command. EXECUTE -- has real side effects, unlike
    every other tool in this registry. The EXECUTE flag is surfaced (printed)
    before the subprocess runs, and again on the returned result, per #208's
    own Definition of done: the caller must see EXECUTE before consequences,
    not buried after them or only inferred from a registry lookup.
    """
    print(f"[EXECUTE] run_command: {' '.join(command)}")
    result = subprocess.run(command, capture_output=True, text=True, cwd=REPO_ROOT)
    return CommandResult(
        side_effect="EXECUTE",
        command=" ".join(command),
        returncode=result.returncode,
        stdout=result.stdout,
        stderr=result.stderr,
    )


def run_test(crate: str, test_name: str | None = None) -> CommandResult:
    """Run a crate's test suite, or one named test within it, via
    `cargo test`. EXECUTE -- same surfacing contract as run_command."""
    cmd = ["cargo", "test", "-p", crate]
    if test_name:
        cmd.append(test_name)
    print(f"[EXECUTE] run_test: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=REPO_ROOT)
    return CommandResult(
        side_effect="EXECUTE",
        command=" ".join(cmd),
        returncode=result.returncode,
        stdout=result.stdout,
        stderr=result.stderr,
    )


TOOL_REGISTRY: dict[str, tuple[Callable, SideEffect]] = {
    "read_file": (read_file, "READ_ONLY"),
    "list_directory": (list_directory, "READ_ONLY"),
    "inspect_logs": (inspect_logs, "READ_ONLY"),
    "search_text": (search_text, "READ_ONLY"),
    "search_symbols": (search_symbols, "READ_ONLY"),
    "find_references": (find_references, "READ_ONLY"),
    "inspect_git_history": (inspect_git_history, "READ_ONLY"),
    "git_blame": (git_blame, "READ_ONLY"),
    "inspect_dependency": (inspect_dependency, "READ_ONLY"),
    "query_build_system": (query_build_system, "READ_ONLY"),
    "run_command": (run_command, "EXECUTE"),
    "run_test": (run_test, "EXECUTE"),
}


def _demo_invocations() -> dict[str, Callable[[], object]]:
    """One real, working call per registered tool -- the CLI trace below prints
    each one's actual result, not a stub. Worked examples reuse #206/#207's
    own known-good symbol (is_shared_gated_kind) and dependency (nostr) so
    the trace is cross-checkable against those tasks' own verification."""
    return {
        "read_file": lambda: read_file("launchpad/project-intelligence/investigator.py", 1, 1),
        "list_directory": lambda: list_directory("launchpad/project-intelligence"),
        "inspect_logs": lambda: inspect_logs("launchpad/project-intelligence/investigator.py", tail_lines=1),
        "search_text": lambda: search_text("TOOL_REGISTRY", glob="*.py")[:1],
        "search_symbols": lambda: search_symbols("is_shared_gated_kind", crate="buzz-core"),
        "find_references": lambda: find_references("is_shared_gated_kind", crate="buzz-core"),
        "inspect_git_history": lambda: inspect_git_history("crates/buzz-core/src/kind.rs", 219, 221)[:1],
        "git_blame": lambda: git_blame("crates/buzz-core/src/kind.rs", 219, 221)[:1],
        "inspect_dependency": lambda: inspect_dependency("buzz-core", "nostr"),
        "query_build_system": lambda: query_build_system("buzz-core"),
        "run_command": lambda: run_command(["echo", "investigator-cli-demo"]),
        "run_test": lambda: run_test("buzz-core", "kind::tests::"),
    }


if __name__ == "__main__":
    print("Investigator tool surface -- every tool, its side-effect marker, one real result\n")
    demos = _demo_invocations()
    for name, (_, effect) in TOOL_REGISTRY.items():
        result = demos[name]()
        line = f"[{effect}] {name} -> {result!r}"
        print(line if len(line) <= 220 else line[:217] + "...")
