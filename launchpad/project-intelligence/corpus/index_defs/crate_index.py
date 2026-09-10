"""Builder for generated/crate-index.md -- the repository crate index (#893).

Subject: the repository's Rust crates under `crates/`. This document is a
CROSS-REFERENCE (known crate -> which canonical nodes document it), not a
listing of canonical nodes filtered by front-matter `type`.

Why a type-enum filter does not work here: node.schema.json's type enum
includes `implementation`, the value that would naturally fit crate-level
documentation, but at the time this builder was written zero canonical nodes
carry `type: implementation` (verified against the merge base). A filter over
that value would render an empty index even though real per-crate evidence
already exists in the corpus (see below) -- the honest move per the #621
brief is not to fake population with a wider, prose-judgement rule, but to
change what drives the listing.

Determinism source for "known crates": a sorted directory listing of
`crates/*/Cargo.toml` in the working tree at generation time, read via the
stdlib `tomllib` parser for each crate's `package.name` and optional
`package.description`. This is NOT AGENTS.md's own crates/ table -- that
table is hand-copied prose, not a corpus node, and cannot be an input per the
brief. It is also demonstrably stale: AGENTS.md's table names ~13 crates by
example ("buzz-relay, buzz-core, buzz-db, buzz-auth, etc., ~20 crates") while
the working tree at this revision holds more (confirmed by `ls crates/`).
`crates/*/Cargo.toml` is inspectable, mechanically enumerable, and the same
kind of workspace-manifest signal `Cargo.toml`'s own `[workspace] members`
list would give (a literal `crates/*` glob member), so it is the crate
registry the repository itself actually uses, not a documentation copy of it.

Cross-reference rule (deterministic, schema-grounded, mirrors
`index_defs/code_to_doc_map.py`'s citation classifier): for each known crate
directory `crates/<name>`, a valid canonical node "documents" it if and only
if one of the node's front-matter `evidence[].evidence` citations is
path-shaped (no whitespace, parentheses, `->` or `://`; an optional single
trailing `:N` / `:N-M` line suffix is stripped), resolves to a real file in
the repository's working tree, and that file's path starts with
`crates/<name>/`. Membership is decided by that mechanical citation shape and
directory containment alone, never by prose judgement -- the corpus already
holds many such citations today (e.g.
`capabilities/presence/user-status.md` cites
`crates/buzz-core/src/kind.rs:67-70`), so this listing populates
non-trivially rather than rendering an empty table.

Determinism note (same wrinkle code_to_doc_map.py discloses): both the crate
directory listing and cited-file existence are checked against the working
tree, which the framework's input digest (canonical corpus nodes only) does
not cover. At a fixed repository revision the cross-reference is fully
deterministic; the generated document discloses this in its "Expected but
not verified" section.

node_type choice: `governance`. This document's rows are repository crates,
not canonical nodes of one front-matter type, so no single subject type-enum
value fits the way `interfaces-events` fits api-index.py; `governance`
follows the same reasoning code_to_doc_map.py already gives for its own rows
being repository files rather than typed corpus nodes.
"""

from __future__ import annotations

import re
import sys
import tomllib
from pathlib import Path
from pathlib import PurePosixPath

# indexes.py loads validate.py as "corpus_validate" before any builder module
# is imported, so this lookup always succeeds under the framework and under
# the test suite (both load indexes.py first).
_validate = sys.modules["corpus_validate"]

_LINE_SUFFIX_RE = re.compile(r":\d+(?:-\d+)?$")

_NONE_YET = "-- none documented yet --"
_NO_DESCRIPTION = "-- no `description` in Cargo.toml --"


def _repo_root() -> Path:
    return _validate.repo_root().resolve()


def _discover_crates(repo_root: Path):
    """Sorted (crate name, crates/<dir> path, description) triples, one per
    `crates/*/Cargo.toml` in the working tree. Determinism source: the
    directory listing itself (sorted glob), read via the stdlib `tomllib`
    parser -- never AGENTS.md's hand-authored crates/ table."""
    crates_dir = repo_root / "crates"
    if not crates_dir.is_dir():
        return []
    found = []
    for toml_path in sorted(crates_dir.glob("*/Cargo.toml")):
        try:
            data = tomllib.loads(toml_path.read_text())
        except (OSError, tomllib.TOMLDecodeError):
            continue
        package = data.get("package")
        if not isinstance(package, dict):
            continue
        name = package.get("name")
        if not isinstance(name, str) or not name:
            continue
        description = package.get("description")
        if not isinstance(description, str):
            description = ""
        rel_dir = f"crates/{toml_path.parent.name}"
        found.append((name, rel_dir, description.strip()))
    found.sort(key=lambda c: c[0])
    return found


def _cited_crate_dir(citation, crate_dirs, repo_root: Path):
    """Return the `crates/<dir>` prefix a citation's file resolves under, or
    None. Purely mechanical: the same character-shape tests
    index_defs/code_to_doc_map.py uses, plus a filesystem existence check and
    membership in the known crate-directory set. Never prose judgement."""
    if not isinstance(citation, str) or not citation:
        return None
    if any(ch in citation for ch in " \t\n()") or "->" in citation:
        return None  # tool-result / prose shape (includes "commit <sha>")
    if "://" in citation:
        return None  # URL
    stripped = _LINE_SUFFIX_RE.sub("", citation)
    if ":" in stripped:
        return None  # residual colon: not a plain relative path
    pure = PurePosixPath(stripped)
    if pure.is_absolute() or ".." in pure.parts or not pure.parts:
        return None
    rel = pure.as_posix()
    if not rel.startswith("crates/"):
        return None
    if not (repo_root / pure).is_file():
        return None  # does not resolve to a real file in this tree
    parts = pure.parts
    if len(parts) < 2:
        return None
    rel_dir = "/".join(parts[:2])
    return rel_dir if rel_dir in crate_dirs else None


def _documenting_nodes(ctx, crate_dirs, repo_root: Path):
    """{crates/<dir> -> sorted node ids} whose evidence citations resolve to
    a file under that crate's directory."""
    found: dict[str, set[str]] = {d: set() for d in crate_dirs}
    for node in ctx.valid_nodes:
        if not isinstance(node.id, str):
            continue
        for entry in node.data.get("evidence") or []:
            if not isinstance(entry, dict):
                continue
            for citation in entry.get("evidence") or []:
                rel_dir = _cited_crate_dir(citation, crate_dirs, repo_root)
                if rel_dir is not None:
                    found[rel_dir].add(node.id)
    return {d: tuple(sorted(ids)) for d, ids in found.items()}


def _generate(ctx):
    repo_root = _repo_root()
    crates = _discover_crates(repo_root)
    crate_dirs = {rel_dir for _, rel_dir, _ in crates}
    documenting = _documenting_nodes(ctx, crate_dirs, repo_root)

    lines = ["## Crate index", ""]
    if crates:
        lines += [
            "| Crate | Path | Description | Documented by |",
            "|---|---|---|---|",
        ]
        for name, rel_dir, description in crates:
            node_ids = documenting.get(rel_dir, ())
            documented = ", ".join(node_ids) if node_ids else _NONE_YET
            desc = description or _NO_DESCRIPTION
            lines.append(f"| `{name}` | `{rel_dir}` | {desc} | {documented} |")
    else:
        lines += [
            "No `crates/*/Cargo.toml` file exists in the repository's working",
            "tree at this revision, so the crate index is empty -- an honest",
            "empty fact, not an omission.",
        ]

    return {
        "sections": "\n".join(lines),
        "includes": [
            "one row per `crates/*/Cargo.toml` found by a sorted directory "
            "glob of the repository's working tree, keyed by that "
            "manifest's `package.name` (and `package.description` when "
            "present) -- never AGENTS.md's hand-authored crates/ table, "
            "which is prose, not a corpus node, and cannot be an input",
            "for each such crate, the sorted list of valid canonical node "
            "ids whose front-matter `evidence[].evidence` citations include "
            "a path-shaped citation (no whitespace, parentheses, `->` or "
            "`://`; an optional trailing `:N` / `:N-M` line suffix is "
            "stripped) that resolves to a real file under that crate's "
            "`crates/<name>/` directory",
        ],
        "excludes": [
            "tool-result and prose-shaped citations (anything containing "
            "whitespace, parentheses or `->`), including bare `commit <sha>` "
            "refs -- a commit is not a code path",
            "bare URLs (any citation containing `://`)",
            "citations that resolve to a real file outside any known "
            "`crates/<name>/` directory (e.g. `web/`, `desktop/`, "
            "`launchpad/`) -- they document something, but not a crate",
            "absolute paths, paths with `..` components, and path-shaped "
            "citations that do not resolve to a regular file in the "
            "current working tree",
            "crate directories with a `Cargo.toml` that fails to parse or "
            "carries no `package.name`",
        ],
        "ordering": (
            "crate rows sorted lexicographically by crate (package) name; "
            "each crate's documenting-node list sorted by node id"
        ),
        "not_covered": [
            "Each crate's actual purpose beyond its own Cargo.toml "
            "`description` (when present) -- this index does not read "
            "source code or infer intent.",
            "The workspace dependency graph between crates -- this is a "
            "documentation cross-reference, not a `cargo tree` view.",
            "The reverse view (which crates a given corpus node covers) "
            "beyond what reading this table backwards provides.",
        ],
        "unverified": [
            "Both the known-crate directory listing and cited-file "
            "existence are checked against the working tree at generation "
            "time, which the input digest (canonical corpus nodes only) "
            "does not cover; adding, removing or renaming a crate, or "
            "deleting a cited file, changes this index without changing "
            "the digest.",
        ],
    }


def _extra_evidence(ctx):
    repo_root = _repo_root()
    crates = _discover_crates(repo_root)
    crate_dirs = {rel_dir for _, rel_dir, _ in crates}
    documenting = _documenting_nodes(ctx, crate_dirs, repo_root)
    documented_count = sum(1 for ids in documenting.values() if ids)
    return [
        {
            "statement": (
                f"At generation time, a sorted glob of crates/*/Cargo.toml "
                f"in the repository working tree found exactly {len(crates)} "
                f"crate(s); {documented_count} of them have at least one "
                "valid canonical node citing a file under their directory "
                "as evidence, via the mechanical citation classifier in "
                "this builder module."
            ),
            "entry_class": "FACT",
            "evidence": ["launchpad/project-intelligence/corpus/index_defs/crate_index.py"],
        }
    ]


SPEC = {
    "name": "crate-index",
    "output_path": "generated/crate-index.md",
    "node_id": "generated-crate-index",
    "title": "Crate index: generated cross-reference of repository crates and documenting nodes",
    "node_type": "governance",
    "audiences": ["agent", "developer"],
    "subject": (
        "the repository's Rust crates under crates/ (discovered from "
        "crates/*/Cargo.toml), cross-referenced against the canonical "
        "corpus nodes that cite them as evidence"
    ),
    "generate": _generate,
    "extra_evidence": _extra_evidence,
    "relationships": (
        {"type": "references", "target": "corpus-agents"},
        {"type": "implements", "target": "corpus-template-generated-index"},
    ),
}
