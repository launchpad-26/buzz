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
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Literal

SideEffect = Literal["READ_ONLY", "EXECUTE"]

REPO_ROOT = Path(__file__).resolve().parents[2]


def _resolve_within_repo(path: str) -> Path:
    """Resolve a caller-supplied path and reject it unless it stays under
    REPO_ROOT. `REPO_ROOT / path` alone does not enforce this: pathlib's `/`
    discards the left side entirely when `path` is itself absolute (e.g.
    "/etc/passwd"), and a relative path containing ".." can walk out via
    resolve() regardless. Every tool taking a repo-relative path routes
    through this, closing off host-file reads a "repo-relative contract"
    alone does not prevent."""
    candidate = (REPO_ROOT / path).resolve()
    if candidate != REPO_ROOT and REPO_ROOT not in candidate.parents:
        raise ValueError(f"path escapes the repository root: {path!r}")
    return candidate


# review-code finding (PR #217, must-fix #2): search_symbols/find_references
# f-string caller-supplied identifiers straight into an `rql query` SQL WHERE
# clause, and inspect_git_history/git_blame f-string a caller-supplied file
# path straight into an `rql read` URI. A value containing "'" breaks or
# redirects the SQL; a value containing "#" or "=>" injects a different
# fragment or modifier into the URI. Reject anything outside a safe charset
# up front rather than attempt to escape it -- the same "reject, don't
# escape" choice The Professor's server.py made for the same class of bug.
_SAFE_IDENTIFIER = re.compile(r"^[A-Za-z0-9_.:\-]+$")


def _validate_identifier(value: str, label: str) -> str:
    if not value or not _SAFE_IDENTIFIER.match(value):
        raise ValueError(
            f"{label} must be a plain identifier (letters, digits, '_', ':', '.', '-'), got {value!r}"
        )
    return value


_SAFE_REPO_RELATIVE_PATH = re.compile(r"^[A-Za-z0-9_./\-]+$")


def _validate_repo_relative_path(value: str, label: str) -> str:
    if not value or not _SAFE_REPO_RELATIVE_PATH.match(value) or ".." in value.split("/"):
        raise ValueError(
            f"{label} must be a plain repo-relative path with no '..' segments, got {value!r}"
        )
    return value


def read_file(path: str, start_line: int | None = None, end_line: int | None = None) -> str:
    """Read a file, or a line range of one, relative to the repo root."""
    text = _resolve_within_repo(path).read_text()
    if start_line is None and end_line is None:
        return text
    lines = text.splitlines()
    return "\n".join(lines[(start_line or 1) - 1 : end_line])


def list_directory(path: str = ".") -> list[str]:
    """List immediate entries of a directory, relative to the repo root."""
    return sorted(p.name + ("/" if p.is_dir() else "") for p in _resolve_within_repo(path).iterdir())


def inspect_logs(path: str, tail_lines: int | None = None) -> str:
    """Read a log file. A log is just a file; no separate mechanism from
    read_file, but named distinctly per the design doc's tool table."""
    text = _resolve_within_repo(path).read_text()
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
    # review-code finding (PR #217, must-fix #1): the default glob "*" walks
    # .git/ and target/, and a binary match under the old command printed
    # "Binary file X matches" -- a line with no ":" separators at all, which
    # `line.split(":", 2)` below raised ValueError on. "-I" tells grep to
    # treat binary files as non-matching instead of reporting them; the two
    # --exclude-dir flags keep the walk out of .git and build artifacts,
    # which are irrelevant to a source-text search and expensive to walk.
    cmd = ["grep", "-rn", "-I", "--exclude-dir=.git", "--exclude-dir=target", "--include", glob]
    if not regex:
        cmd.append("-F")
    # "--" terminates option parsing so a pattern starting with "-" (e.g.
    # "--help") is treated as the search text, not another grep flag.
    cmd += ["--", pattern, "."]
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=REPO_ROOT)
    # grep's exit code is part of its contract, not noise: 0 = matches found,
    # 1 = no matches (a normal, expected outcome, not an error), 2+ = a real
    # error (bad pattern, unreadable file, ...). The old code never checked
    # this, so a real grep failure was silently indistinguishable from "no
    # results" -- the caller would just get an empty list either way.
    if result.returncode not in (0, 1):
        raise RuntimeError(f"search_text: grep exited {result.returncode}: {result.stderr!r}")
    matches = []
    for line in result.stdout.splitlines():
        # grep -n output: "./path/to/file:LINE:text". "-I" above means this
        # should never see a binary-file notice line, but the split is kept
        # defensive (skip, don't crash) for any other unparseable line grep
        # might still emit.
        parts = line.split(":", 2)
        if len(parts) != 3:
            continue
        path, lineno, text = parts
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
    _validate_identifier(name, "name")
    if crate:
        _validate_identifier(crate, "crate")
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
    2. Reads each candidate's own source range (read_file) and checks each
       line for a real call-site pattern: the short name (word-bounded, so
       "shared_gated_kind" cannot match inside "is_shared_gated_kind"),
       optionally followed by whitespace and/or a turbofish (`::<T>`), then
       `(`. Lines that are pure `//` comments are skipped, and every
       matching line in a candidate is reported, not just the first.
    This is the same distinction #206's with_called_by() drew (a resolved
    call-site match, not a bare grep), reimplemented here since #208 has no
    dependency on #206's branch-local code.

    Best-effort, not a Rust parser: does not track block comments (/* */),
    string/byte-string literals, or macro-generated calls -- a call-site
    pattern inside one of those would still be reported as a reference.
    """
    _validate_identifier(qualified_name, "qualified_name")
    _validate_identifier(crate, "crate")
    short_name = qualified_name.rsplit("::", 1)[-1]
    call_pattern = re.compile(rf"\b{re.escape(short_name)}\s*(?:::<[^>]*>)?\s*\(")

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
        for offset, line_text in enumerate(body.splitlines()):
            if line_text.strip().startswith("//"):
                continue
            if call_pattern.search(line_text):
                line_number = c["start_line"] + offset
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


# git log's field separator for inspect_git_history: NUL. Not a printable
# control character (an earlier version used 0x1e/0x1f "unit/record
# separator" bytes on the theory that a commit subject would never contain
# them -- cross-vendor review (Codex, #569) found that wrong: git accepts
# 0x1e/0x1f in a commit message verbatim, confirmed by actually creating one
# (`git commit -F` with those bytes in the message succeeds). NUL is
# different in kind, not just convention: git refuses to create a commit
# whose message contains one at all ("a NUL byte in commit log message not
# allowed"), confirmed the same way. That is what makes it safe here, not a
# guess about what commit authors typically do.
#
# Framing: each record is emitted as %x00 followed by its four NUL-separated
# fields, so splitting the whole output on NUL and dropping the leading empty
# string (from the very first record's own leading NUL) gives a flat list
# that is exactly a multiple of 4 long -- chunk it back into records rather
# than searching for a record boundary. git's own between-entry blank line
# lands on the trailing edge of each record's message field (there is no
# field after it to absorb it), so that field alone is rstripped.
#
# Two different constants because they serve two different sides of the same
# byte: `_GIT_LOG_FORMAT_SEP` is the four-character literal text git's
# `--pretty=format:` syntax recognizes and turns into an actual NUL byte when
# it writes output -- it goes into the subprocess argv, which cannot itself
# contain a raw NUL (`subprocess.run` raises `ValueError: embedded null
# byte`). `_GIT_LOG_OUTPUT_SEP` is the real NUL byte that shows up once git
# has run, used only to split the captured stdout string in Python -- never
# passed to a subprocess as an argument.
_GIT_LOG_FORMAT_SEP = "%x00"
_GIT_LOG_OUTPUT_SEP = "\x00"


def inspect_git_history(file: str, start_line: int, end_line: int) -> list[CommitSummary]:
    """Commits touching a file's line range, via `git log -L start,end:file`
    directly rather than RepoQL's `=> history` modifier.

    issue #569: RepoQL's `#line=N,N => history` fragment returned zero commits
    for a degenerate single-line range (start_line == end_line), even where
    `git log -L N,N:file` names a real one for that exact line -- measured on
    crates/buzz-core/src/kind.rs (0 commits for (850, 850), 4 for (840, 860)),
    independently confirmed twice: once by this issue and once already
    recorded in investigation.py's own HISTORY_LINE_WINDOW comment. Reading
    this function's own source rules out the alternative hypothesis that the
    bug was here -- there was no line-count-dependent branch, just a direct
    `data.get("commits", [])` passthrough. RepoQL's own fragment resolution
    was the only place left in the chain this function could see, though its
    exact internal behavior for `#line=N,N` was not directly observable
    (unreachable for live testing in the environment this fix was built in --
    see the commit message). Rather than guess at that internal semantics,
    this calls `git log -L` directly: the same primitive RepoQL's own history
    modifier is meant to mirror, and the same "avoid depending on RepoQL
    where a git-native tool already answers the question" trade-off
    search_text() above makes for grep -- "one less tool affected if the
    RepoQL host is unavailable" applies here too.

    Raises ValueError for start_line > end_line, and RuntimeError (via a
    non-zero `git log` exit) for a file or line range git itself cannot
    resolve -- an out-of-range line or nonexistent file is a real error, not
    a silent empty result.
    """
    _validate_repo_relative_path(file, "file")
    _resolve_within_repo(file)  # containment check; git now runs directly, not through RepoQL's own sandboxing
    if start_line > end_line:
        raise ValueError(f"start_line ({start_line}) must be <= end_line ({end_line})")
    sep = _GIT_LOG_FORMAT_SEP
    fmt = f"{sep}%H{sep}%aI{sep}%an{sep}%s"
    cmd = ["git", "log", "--no-patch", f"--pretty=format:{fmt}", "-L", f"{start_line},{end_line}:{file}"]
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=REPO_ROOT)
    if result.returncode != 0:
        raise RuntimeError(
            f"inspect_git_history: git log -L failed for {file}:{start_line}-{end_line}: {result.stderr.strip()}"
        )
    fields = result.stdout.split(_GIT_LOG_OUTPUT_SEP)
    if fields and fields[0] == "":
        fields = fields[1:]  # the leading NUL every record (including the first) starts with
    commits = []
    for i in range(0, len(fields), 4):
        commit_hash, date, author, message = fields[i : i + 4]
        # git inserts a blank line between log entries; with nothing after
        # the message field to absorb it, it lands here as a trailing "\n".
        commits.append(CommitSummary(hash=commit_hash, date=date, author=author, message=message.rstrip("\n")))
    return commits


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
    _validate_repo_relative_path(file, "file")
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

    A crate-local entry can add its own keys alongside `workspace = true`
    (e.g. crates/buzz-agent/Cargo.toml adds `features = ["io-std", ...]` to
    tokio's workspace entry) -- Cargo merges these into the workspace
    dependency rather than the crate-local entry replacing it wholesale.
    `features` unions (Cargo's own merge behavior); any other crate-local
    key (`optional`, `default-features`, ...) overrides the workspace value.
    """
    import tomllib

    # review-code finding (PR #217, must-fix #3): this built its path directly
    # from REPO_ROOT / "crates" / crate / ..., bypassing _resolve_within_repo
    # entirely -- crate="../../etc" walked straight out of the repo, the same
    # bug class the second commit on this PR already fixed for
    # read_file/list_directory/inspect_logs. _validate_identifier rejects any
    # "/" or ".." up front; _resolve_within_repo is the second, independent
    # layer, same as every other repo-relative tool here.
    _validate_identifier(crate, "crate")
    crate_manifest = tomllib.loads(_resolve_within_repo(f"crates/{crate}/Cargo.toml").read_text())
    declared = crate_manifest.get("dependencies", {}).get(name)
    if declared is None:
        return None

    resolved = declared
    if isinstance(declared, dict) and declared.get("workspace") is True:
        root_manifest = tomllib.loads((REPO_ROOT / "Cargo.toml").read_text())
        workspace_entry = root_manifest.get("workspace", {}).get("dependencies", {}).get(name, {})
        resolved = dict(workspace_entry)
        local_extra = {k: v for k, v in declared.items() if k != "workspace"}
        local_features = local_extra.pop("features", None)
        if local_features is not None:
            resolved["features"] = sorted(set(resolved.get("features", [])) | set(local_features))
        resolved.update(local_extra)

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

    --locked is required for the same READ_ONLY guarantee: without it, cargo
    metadata will silently rewrite Cargo.lock if it is out of date relative
    to a manifest, even with --no-deps -- a real mutation this registered
    READ_ONLY tool must not perform. With --locked the call fails loudly
    instead of writing, which is the correct behavior for a tool that
    promises not to change the checkout.
    """
    # review-code finding (PR #217, must-fix #3): same path-containment bypass
    # as inspect_dependency above -- crate went straight into a manifest path
    # with no validation and no _resolve_within_repo call.
    _validate_identifier(crate, "crate")
    manifest_path = _resolve_within_repo(f"crates/{crate}/Cargo.toml")
    result = subprocess.run(
        [
            "cargo",
            "metadata",
            "--no-deps",
            "--locked",
            "--format-version",
            "1",
            "--manifest-path",
            str(manifest_path),
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
    # flush=True: stdout is block-buffered (not line-buffered) whenever it is
    # piped rather than a terminal -- the normal case for an agent harness
    # capturing this tool's output. Without an explicit flush, the caller
    # would not see this line until the subprocess below had already
    # finished (or Python exited), which fails "surfaced before execution".
    print(f"[EXECUTE] run_command: {' '.join(command)}", flush=True)
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
    print(f"[EXECUTE] run_test: {' '.join(cmd)}", flush=True)  # same buffering reason as run_command
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
