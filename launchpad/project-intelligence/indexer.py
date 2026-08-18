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

from symbol import DefinedAt, GitOwnership, Symbol

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


def run_rql_query(sql: str) -> list[dict]:
    result = subprocess.run(
        ["rql", "query", sql, "--json"],
        capture_output=True,
        text=True,
        check=True,
        cwd=REPO_ROOT,
    )
    return json.loads(result.stdout)


def _best_effort_calls(file_rel: str, start_line: int, end_line: int, own_name: str) -> tuple[str, ...]:
    """Scan the symbol's own source lines for call-like identifiers.

    Best-effort by design (#206's plan, LEFT OUT): no type resolution, no
    distinguishing a real call from a macro or a tuple-struct constructor.
    Precision belongs to #207 (ProjectGraph), which builds real edges once
    symbols exist to link.
    """
    path = REPO_ROOT / file_rel
    try:
        lines = path.read_text().splitlines()
    except OSError:
        return ()
    body = "\n".join(lines[start_line - 1 : end_line])
    found = []
    seen = set()
    for match in _CALL_SITE.finditer(body):
        name = match.group(1)
        if name == own_name or name in _NOT_A_CALL or name in seen:
            continue
        seen.add(name)
        found.append(name)
    return tuple(found)


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
        calls = _best_effort_calls(file_rel, row["start_line"], row["end_line"], row["name"])
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
                git_ownership=GitOwnership(),
            )
        )
    return symbols


def with_called_by(symbols: list[Symbol]) -> list[Symbol]:
    """STEP 3: materialize called_by[] as a real inverse index, once, over the
    already-indexed set -- not recomputed per query.

    Matches each symbol's calls[] entries against the indexed set's own `name`
    (the short, unqualified identifier calls[] holds), same best-effort scope as
    step 2: a name match, not type-resolved call-graph precision.
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

    return [
        replace(sym, called_by=tuple(dict.fromkeys(called_by[sym.qualified_name])))
        for sym in symbols
    ]


def _print_symbol(sym: Symbol) -> None:
    print(f"Symbol: {sym.qualified_name}")
    print(f"Defined: {sym.defined_at.file}:{sym.defined_at.start_line}-{sym.defined_at.end_line} "
          f"({sym.defined_at.temporal_state})")
    print(f"Signature: {sym.signature}")
    print(f"Calls: {', '.join(sym.calls) if sym.calls else '(none found)'}")
    print(f"Called by: {', '.join(sym.called_by) if sym.called_by else '(not yet populated -- STEP 3)'}")
    print(f"Tests: {', '.join(sym.tests) if sym.tests else '(not yet populated -- STEP 5)'}")


if __name__ == "__main__":
    crate = sys.argv[1] if len(sys.argv) > 1 else "buzz-core"
    symbols = with_called_by(index_crate(crate))
    print(f"Indexed {len(symbols)} symbols from crates/{crate}\n")
    for sym in symbols:
        if sym.qualified_name == "is_shared_gated_kind":
            _print_symbol(sym)
            break
    else:
        print("(worked-example symbol 'is_shared_gated_kind' not found in this crate)")
        if symbols:
            _print_symbol(symbols[0])
