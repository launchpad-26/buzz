"""ProjectIndexer adapter over RepoQL -- issue #206, STEP 2.

Maps RepoQL's own `Functions` view (already-parsed structural data: qualified names,
signatures, declaring types, line ranges) into this design's `Symbol` record, rather
than writing a second parser. `calls[]` is a best-effort scan of the symbol's own
source lines for call-like identifiers -- precision is explicitly out of scope for
this task (see #206's plan, LEFT OUT); `called_by[]`, `git_ownership`, `tests[]`,
`config_dependencies[]`, and `documentation_links[]` are later steps in the same plan.

Requires the `rql` CLI on PATH (RepoQL's own host must already be indexing this repo).

Run:  python3 indexer.py <crate-name>   (from launchpad/project-intelligence/)
  e.g. python3 indexer.py buzz-core
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from dataclasses import replace
from pathlib import Path

from symbol import CommitSummary, DefinedAt, GitOwnership, Symbol

REPO_ROOT = Path(__file__).resolve().parents[2]

# Rust keywords and control-flow words that precede `(` but are not calls.
_NOT_A_CALL = frozenset(
    {
        "if", "while", "for", "match", "return", "let", "fn", "loop", "else",
        "assert", "assert_eq", "assert_ne", "debug_assert", "unreachable",
        "Some", "None", "Ok", "Err",
    }
)
_CALL_SITE = re.compile(r"\b([a-zA-Z_][a-zA-Z0-9_]*)\s*\(")
_ENV_VAR_READ = re.compile(r'env::var(?:_os)?\s*\(\s*"([A-Za-z_][A-Za-z0-9_]*)"')


def run_rql_query(sql: str) -> list[dict]:
    result = subprocess.run(
        ["rql", "query", sql, "--json"],
        capture_output=True,
        text=True,
        check=True,
        cwd=REPO_ROOT,
    )
    return json.loads(result.stdout)


def _read_body(file_rel: str, start_line: int, end_line: int) -> str:
    path = REPO_ROOT / file_rel
    try:
        lines = path.read_text().splitlines()
    except OSError:
        return ""
    return "\n".join(lines[start_line - 1 : end_line])


def _best_effort_calls(body: str, own_name: str) -> tuple[str, ...]:
    """Scan the symbol's own source lines for call-like identifiers.

    Best-effort by design (#206's plan, LEFT OUT): no type resolution, no
    distinguishing a real call from a macro or a tuple-struct constructor.
    Precision belongs to #207 (ProjectGraph), which builds real edges once
    symbols exist to link.
    """
    found = []
    seen = set()
    for match in _CALL_SITE.finditer(body):
        name = match.group(1)
        if name == own_name or name in _NOT_A_CALL or name in seen:
            continue
        seen.add(name)
        found.append(name)
    return tuple(found)


def _best_effort_config_deps(body: str) -> tuple[str, ...]:
    """STEP 6: scan the symbol's own source lines for env-var reads.

    Best-effort: only the literal-string-argument form of `env::var`/
    `env::var_os` is recognised (`env::var("SOME_VAR")`); a variable name
    built dynamically would not be caught. Config keys read some other way
    (a config struct field, a CLI flag) are out of this task's scope too.
    """
    seen = dict.fromkeys(m.group(1) for m in _ENV_VAR_READ.finditer(body))
    return tuple(seen)


def index_crate(crate_name: str) -> list[Symbol]:
    """Query RepoQL's Functions view for one crate and map rows into Symbols."""
    rows = run_rql_query(
        "SELECT uri, file, name, qualified_name, function_kind, declaring_type, "
        "signature, start_line, end_line FROM Functions "
        f"WHERE file LIKE '%crates/{crate_name}/%'"
    )

    symbols = []
    for row in rows:
        file_rel = row["file"].removeprefix("file:///")
        kind = "method" if row.get("declaring_type") else "function"
        body = _read_body(file_rel, row["start_line"], row["end_line"])
        calls = _best_effort_calls(body, row["name"])
        config_deps = _best_effort_config_deps(body)
        symbols.append(
            Symbol(
                symbol_id=row["uri"],
                kind=kind,
                qualified_name=row["qualified_name"],
                defined_at=DefinedAt(
                    file=file_rel,
                    start_line=row["start_line"],
                    end_line=row["end_line"],
                    temporal_state="WORKING",
                ),
                signature=row["signature"],
                calls=calls,
                config_dependencies=config_deps,
                git_ownership=GitOwnership(),
            )
        )
    return symbols


def with_called_by(symbols: list[Symbol]) -> list[Symbol]:
    """STEP 3: materialize called_by[] as a real inverse index, once, over the
    already-indexed set -- not recomputed per query.

    Also resolves each symbol's own calls[] from the bare short names STEP 2
    could only scan for, to the same qualified-name representation called_by[]
    uses -- both fields are symbol references (design doc, Data Model item 1)
    and one holding short names while the other held qualified names was an
    internal inconsistency, caught in review. A call to something not in the
    indexed set (a std-lib method, another crate) has no qualified name to
    resolve to and keeps its bare short name, marked as such by the absence of
    "::" -- there is nothing more precise to offer without indexing that
    target too.

    Same best-effort scope as step 2: a name match, not type-resolved
    call-graph precision. A short name shared by more than one indexed symbol
    resolves to ALL of them, which can attach a caller to the wrong target --
    an accepted limitation of this task's scope (see the plan's LEFT OUT);
    real precision is #207's (ProjectGraph) job once symbols exist to link.
    """
    by_name: dict[str, list[str]] = {}
    for sym in symbols:
        by_name.setdefault(sym.qualified_name.rsplit("::", 1)[-1], []).append(sym.qualified_name)

    called_by: dict[str, list[str]] = {sym.qualified_name: [] for sym in symbols}
    for sym in symbols:
        for called_name in sym.calls:
            for target_qname in by_name.get(called_name, ()):
                if target_qname != sym.qualified_name:
                    called_by[target_qname].append(sym.qualified_name)

    def resolve_calls(calls: tuple[str, ...], own_qname: str) -> tuple[str, ...]:
        resolved = []
        for name in calls:
            targets = [t for t in by_name.get(name, ()) if t != own_qname]
            resolved.extend(targets or [name])
        return tuple(dict.fromkeys(resolved))

    return [
        replace(
            sym,
            calls=resolve_calls(sym.calls, sym.qualified_name),
            called_by=tuple(dict.fromkeys(called_by[sym.qualified_name])),
        )
        for sym in symbols
    ]


_TEST_LIKE = re.compile(r"(^|::)tests?::|^test_|_test$")


def with_tests(symbols: list[Symbol]) -> list[Symbol]:
    """STEP 5: derive tests[] as the subset of each symbol's called_by[] whose
    qualified_name looks like a test (Rust's own `tests::` module convention,
    or a test_/_test name), rather than a second, separate search pass --
    the calling relationship already found in STEP 3 is the same evidence.
    """
    return [
        replace(sym, tests=tuple(caller for caller in sym.called_by if _TEST_LIKE.search(caller)))
        for sym in symbols
    ]


_DOC_GLOBS = ("*.md", "launchpad/**/*.md")


def _repo_markdown_files() -> list[Path]:
    files: list[Path] = []
    for pattern in _DOC_GLOBS:
        files.extend(REPO_ROOT.glob(pattern))
    return files


def with_documentation_links(symbols: list[Symbol]) -> list[Symbol]:
    """STEP 7: attach markdown docs that mention each symbol's qualified name
    OR its source file (either is real evidence the doc discusses it).

    Best-effort: a name/path match, not a semantic check that the doc is
    actually ABOUT this symbol -- a name shared with an unrelated concept, or
    a file mentioned for an unrelated reason, would false-positive. Scoped to
    this repo's root-level and launchpad/ markdown, not every markdown file
    in the tree. Does not attach a `#section` fragment -- doing that requires
    parsing each doc's heading structure to know which section a match falls
    under, a bigger lift than this task's own done-when asked for (a symbol
    documented "somewhere" showing that doc's *path*); left for whoever needs
    section-level granularity next.
    """
    doc_files = _repo_markdown_files()
    doc_texts = [(f, f.read_text(errors="ignore")) for f in doc_files]

    result = []
    for sym in symbols:
        short_name = sym.qualified_name.rsplit("::", 1)[-1]
        name_pattern = re.compile(r"\b" + re.escape(short_name) + r"\b")
        file_pattern = re.compile(re.escape(sym.defined_at.file))
        links = tuple(
            str(f.relative_to(REPO_ROOT))
            for f, text in doc_texts
            if name_pattern.search(text) or file_pattern.search(text)
        )
        result.append(replace(sym, documentation_links=links))
    return result


def _rql_read_json(uri_with_modifier: str) -> dict:
    result = subprocess.run(
        ["rql", "read", uri_with_modifier, "--json"],
        capture_output=True,
        text=True,
        check=True,
        cwd=REPO_ROOT,
    )
    return json.loads(result.stdout)


def enrich_git_ownership(sym: Symbol) -> Symbol:
    """STEP 4: populate git_ownership via RepoQL's history/blame, for one symbol.

    Not run eagerly over a whole crate in this task -- each call shells out to
    `rql read` and costs roughly a second; batching/parallelizing that for
    hundreds of symbols is a real performance concern this task's scope
    (prove the schema and pipeline once) deliberately leaves for later.
    """
    base_uri = sym.symbol_id.split("#", 1)[0] + "#symbol=" + sym.qualified_name

    history = _rql_read_json(f"{base_uri} => history")
    commits = tuple(
        CommitSummary(hash=c["hash"], date=c["date"], author=c["author"], message=c["message"])
        for c in history.get("commits", [])
    )

    blame = _rql_read_json(f"{base_uri} => blame")
    author_line_counts: dict[str, int] = {}
    for line in blame.get("lines", ()):
        author_line_counts[line["author"]] = author_line_counts.get(line["author"], 0) + 1
    primary_authors = tuple(
        author for author, _ in sorted(author_line_counts.items(), key=lambda kv: -kv[1])
    )

    return replace(sym, git_ownership=GitOwnership(primary_authors=primary_authors, history=commits))


def build_index(crate_name: str) -> list[Symbol]:
    """The full pipeline, steps 2-3 and 5-7 -- everything except git_ownership
    (STEP 4). Every returned Symbol has an EMPTY GitOwnership by default; call
    enrich_git_ownership() per symbol to populate it. This is deliberate, not
    partial: #206's own Definition of done requires git_ownership verified
    "for at least one symbol" (a chosen worked example), not eagerly for a
    whole crate -- each rql read call costs roughly a second, and batching
    that for hundreds of symbols is a real performance concern this task's
    scope leaves for later. A caller of this function alone gets no ownership
    data; that is the contract, not a bug.
    """
    symbols = index_crate(crate_name)
    symbols = with_called_by(symbols)
    symbols = with_tests(symbols)
    symbols = with_documentation_links(symbols)
    return symbols


def _print_symbol(sym: Symbol) -> None:
    """STEP 8: one full Symbol record, matching the design doc's
    PaymentService.processPayment worked-example shape -- every field
    populated or explicitly empty, never silently omitted."""
    print(f"Symbol ID: {sym.symbol_id}")
    print(f"Kind: {sym.kind}")
    print(f"Symbol: {sym.qualified_name}")
    print(f"Defined: {sym.defined_at.file}:{sym.defined_at.start_line}-{sym.defined_at.end_line} "
          f"({sym.defined_at.temporal_state})")
    print(f"Signature: {sym.signature}")
    print(f"Calls: {', '.join(sym.calls) if sym.calls else '(none found)'}")
    print(f"Called by: {', '.join(sym.called_by) if sym.called_by else '(none found)'}")
    print(f"Tests: {', '.join(sym.tests) if sym.tests else '(none found)'}")
    print(f"Config dependencies: {', '.join(sym.config_dependencies) if sym.config_dependencies else '(none found)'}")
    print(f"Documentation: {', '.join(sym.documentation_links) if sym.documentation_links else '(none found)'}")
    if sym.git_ownership.history:
        print(f"Primary authors: {', '.join(sym.git_ownership.primary_authors)}")
        print("Git history:")
        for c in sym.git_ownership.history:
            print(f"  {c.hash[:7]} {c.date[:10]} {c.author} | {c.message}")
    else:
        print("Git ownership: (none found)")


if __name__ == "__main__":
    crate = sys.argv[1] if len(sys.argv) > 1 else "buzz-core"
    symbols = build_index(crate)
    print(f"Indexed {len(symbols)} symbols from crates/{crate}\n")
    for sym in symbols:
        if sym.qualified_name == "is_shared_gated_kind":
            _print_symbol(enrich_git_ownership(sym))
            break
    else:
        print("(worked-example symbol 'is_shared_gated_kind' not found in this crate)")
        if symbols:
            _print_symbol(symbols[0])
