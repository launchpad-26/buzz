"""Builder for generated/event-kind-index.md -- the event kind index (#899).

Subject: Nostr event kind integers, per this repository's own AGENTS.md ("All
event kind integers are defined in buzz-core/src/kind.rs. New features get new
kind integers -- add them here first, then implement handling in the relay").
This document is a CROSS-REFERENCE (known kind constant -> which canonical
nodes document it), the same shape index_defs/crate_index.py and
index_defs/code_to_doc_map.py already use, not a listing of canonical nodes
filtered by front-matter `type`.

Why a type-enum filter does not work here: templates/event-kind.md's own
Required section 1 states that a real event-kind instance node "would most
plausibly take node.schema.json's ... interfaces-events type" -- but that is
an INFERENCE (confidence 0.6) about a future instance, not a fact about this
base. Verified fresh rather than assumed from that template's now-stale
count: at this revision zero canonical nodes (excluding generated/,
templates/ and schema/) carry `type: interfaces-events`, and zero carry
`relationships: implements -> corpus-template-event-kind`. Both candidate
signals stay genuinely empty; a filter over either would render an empty
index even though real per-kind evidence already exists in the corpus (see
below) -- the honest move per the #621 brief is not to fake population with a
wider, prose-judgement rule, but to change what drives the listing.

Determinism source for "known kinds": a regex walk of
`crates/buzz-core/src/kind.rs` in the working tree at generation time,
matching `pub const KIND_<NAME>: u32 = <value>;` per line and recording each
constant's name, value and 1-based declaration line number. This is NOT any
node's own prose commentary about kind.rs -- it is the same kind of
mechanical, working-tree-inspectable registry read `index_defs/crate_index.py`
takes from `crates/*/Cargo.toml` via `tomllib`, applied to kind.rs's own
`pub const` declarations instead. At this revision kind.rs declares 129 such
constants with no duplicate values (kind.rs's own `no_duplicate_kind_values`
unit test already enforces that invariant on the constants this builder
reads, so this builder does not re-derive it).

Cross-reference rule (deterministic, schema-grounded, mirrors
`index_defs/crate_index.py` and `index_defs/code_to_doc_map.py`'s citation
classifier, extended one level deeper): for each known kind constant, a
valid canonical node "documents" it if and only if one of the node's
front-matter `evidence[].evidence` citations is path-shaped (no whitespace,
parentheses, `->` or `://`), resolves to
`crates/buzz-core/src/kind.rs` in the repository's working tree, AND carries
a `:N` or `:N-M` trailing line-suffix whose range includes that constant's
own declaration line. A bare (no-line-suffix) citation of kind.rs cites the
file generally -- evidence about the registry as a whole, not about any one
kind -- and is therefore excluded from per-kind attribution rather than
force-attributed to every kind or silently dropped without explanation
(named explicitly in "excludes" below). Membership is decided by that
mechanical citation shape and line-range containment alone, never by prose
judgement -- the corpus already holds many such line-suffixed citations today
(e.g. `capabilities/presence/user-status.md` cites
`crates/buzz-core/src/kind.rs:67-70`, a range that contains line 70,
`KIND_USER_STATUS`'s own declaration line), so this listing populates
non-trivially rather than rendering an empty table.

Determinism note (same wrinkle crate_index.py and code_to_doc_map.py
disclose): both the kind.rs constant walk and cited-file/line resolution are
checked against the working tree, which the framework's input digest
(canonical corpus nodes only) does not cover. At a fixed repository revision
the cross-reference is fully deterministic; the generated document discloses
this in its "Expected but not verified" section.

node_type choice: `governance`. This document's rows are kind.rs constants,
not canonical nodes of one front-matter type, so no single subject type-enum
value fits the way `interfaces-events` would fit a real per-kind instance
node; `governance` follows the same reasoning `crate_index.py` and
`code_to_doc_map.py` already give for their own rows being repository
artifacts rather than typed corpus nodes.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from pathlib import PurePosixPath

# indexes.py loads validate.py as "corpus_validate" before any builder module
# is imported, so this lookup always succeeds under the framework and under
# the test suite (both load indexes.py first).
_validate = sys.modules["corpus_validate"]

_LINE_SUFFIX_RE = re.compile(r":(\d+)(?:-(\d+))?$")
_KIND_CONST_RE = re.compile(r"^pub const (KIND_[A-Z0-9_]+): u32 = (\d+);")

_KIND_RS_PATH = "crates/buzz-core/src/kind.rs"

_NONE_YET = "-- none documented yet --"


def _repo_root() -> Path:
    return _validate.repo_root().resolve()


def _discover_kinds(repo_root: Path):
    """Sorted (value, name, declaration line) triples, one per `pub const
    KIND_<NAME>: u32 = <value>;` line found in kind.rs in the working tree.
    Determinism source: a plain regex walk of the file's own lines -- never
    AGENTS.md's or kind.rs's own prose commentary about which kinds exist."""
    path = repo_root / _KIND_RS_PATH
    if not path.is_file():
        return []
    found = []
    for lineno, line in enumerate(path.read_text().splitlines(), start=1):
        match = _KIND_CONST_RE.match(line.strip())
        if not match:
            continue
        name, value = match.group(1), int(match.group(2))
        found.append((value, name, lineno))
    found.sort(key=lambda k: (k[0], k[1]))
    return found


def _cited_kind_line(citation, repo_root: Path):
    """Return the (start, end) 1-based line range a citation's line-suffix
    names, or None if the citation is not a line-suffixed kind.rs citation
    that resolves to a real file. Purely mechanical: the same character-shape
    tests `index_defs/code_to_doc_map.py` and `index_defs/crate_index.py`
    use, plus a line-suffix parse. Never prose judgement."""
    if not isinstance(citation, str) or not citation:
        return None
    if any(ch in citation for ch in " \t\n()") or "->" in citation:
        return None  # tool-result / prose shape (includes "commit <sha>")
    if "://" in citation:
        return None  # URL
    suffix_match = _LINE_SUFFIX_RE.search(citation)
    if suffix_match is None:
        return None  # bare file citation: cites kind.rs generally, not one kind
    stripped = citation[: suffix_match.start()]
    pure = PurePosixPath(stripped)
    if pure.is_absolute() or ".." in pure.parts or not pure.parts:
        return None
    rel = pure.as_posix()
    if rel != _KIND_RS_PATH:
        return None
    if not (repo_root / pure).is_file():
        return None  # does not resolve to a real file in this tree
    start = int(suffix_match.group(1))
    end = int(suffix_match.group(2)) if suffix_match.group(2) else start
    if end < start:
        return None
    return (start, end)


def _documenting_nodes(ctx, kinds, repo_root: Path):
    """{kind name -> sorted node ids} whose evidence citations carry a
    line-suffixed kind.rs citation whose range includes that kind's own
    declaration line."""
    found: dict[str, set[str]] = {name: set() for _, name, _ in kinds}
    for node in ctx.valid_nodes:
        if not isinstance(node.id, str):
            continue
        for entry in node.data.get("evidence") or []:
            if not isinstance(entry, dict):
                continue
            for citation in entry.get("evidence") or []:
                line_range = _cited_kind_line(citation, repo_root)
                if line_range is None:
                    continue
                start, end = line_range
                for _, name, decl_line in kinds:
                    if start <= decl_line <= end:
                        found[name].add(node.id)
    return {name: tuple(sorted(ids)) for name, ids in found.items()}


def _generate(ctx):
    repo_root = _repo_root()
    kinds = _discover_kinds(repo_root)
    documenting = _documenting_nodes(ctx, kinds, repo_root)

    lines = ["## Event kind index", ""]
    if kinds:
        lines += [
            "| Kind name | Value | Declared at | Documented by |",
            "|---|---|---|---|",
        ]
        for value, name, decl_line in kinds:
            node_ids = documenting.get(name, ())
            documented = ", ".join(node_ids) if node_ids else _NONE_YET
            location = f"`{_KIND_RS_PATH}:{decl_line}`"
            lines.append(f"| `{name}` | {value} | {location} | {documented} |")
    else:
        lines += [
            f"No `{_KIND_RS_PATH}` file exists in the repository's working tree",
            "at this revision, so the event kind index is empty -- an honest",
            "empty fact, not an omission.",
        ]

    return {
        "sections": "\n".join(lines),
        "includes": [
            f"one row per `pub const KIND_<NAME>: u32 = <value>;` declaration "
            f"found by a plain regex walk of `{_KIND_RS_PATH}` in the "
            "repository's working tree -- never a hand-copied kind list from "
            "AGENTS.md or from any corpus node's own prose",
            "for each such kind, the sorted list of valid canonical node ids "
            "whose front-matter `evidence[].evidence` citations include a "
            f"path-shaped citation of `{_KIND_RS_PATH}` carrying a `:N` or "
            "`:N-M` trailing line-suffix whose range includes that "
            "constant's own declaration line",
        ],
        "excludes": [
            f"bare (no-line-suffix) citations of `{_KIND_RS_PATH}` -- they "
            "cite the registry file generally, evidence about kind.rs as a "
            "whole rather than about any one kind, so they attribute to no "
            "row rather than being force-attributed to every kind",
            "tool-result and prose-shaped citations (anything containing "
            "whitespace, parentheses or `->`), including bare `commit <sha>` "
            "refs -- a commit is not a code path",
            "bare URLs (any citation containing `://`)",
            "citations that resolve to a real file other than "
            f"`{_KIND_RS_PATH}` -- they document something, but not this "
            "index's subject",
            "absolute paths, paths with `..` components, and path-shaped "
            "citations that do not resolve to a regular file in the "
            "current working tree",
            "a line-suffixed citation whose range does not include any "
            "known constant's declaration line -- it cites a real line in "
            "kind.rs, but not a kind declaration",
        ],
        "ordering": (
            "kind rows sorted numerically by kind value, then "
            "lexicographically by constant name; each kind's documenting-"
            "node list sorted by node id"
        ),
        "not_covered": [
            "Each kind's referenced NIP, tag shape, content semantics or "
            "access-control gating -- that is a real event-kind instance "
            "node's job (templates/event-kind.md), not this index's.",
            "Whether a kind is still live versus superseded by a later "
            "renumbering (kind.rs's own doc comments record some of this "
            "history inconsistently) -- this index lists every declared "
            "constant as found, without classifying liveness.",
            "The reverse view (which kinds a given corpus node documents) "
            "beyond what reading this table backwards provides.",
        ],
        "unverified": [
            "Both the kind.rs constant walk and cited-line resolution are "
            "checked against the working tree at generation time, which the "
            "input digest (canonical corpus nodes only) does not cover; "
            "adding, removing or renumbering a kind constant, or editing "
            "kind.rs so a previously-cited line range now lands on a "
            "different constant, changes this index without changing the "
            "digest.",
        ],
    }


def _extra_evidence(ctx):
    repo_root = _repo_root()
    kinds = _discover_kinds(repo_root)
    documenting = _documenting_nodes(ctx, kinds, repo_root)
    documented_count = sum(1 for ids in documenting.values() if ids)
    return [
        {
            "statement": (
                f"At generation time, a regex walk of {_KIND_RS_PATH} in the "
                f"repository working tree found exactly {len(kinds)} "
                "`pub const KIND_<NAME>: u32 = <value>;` declaration(s); "
                f"{documented_count} of them have at least one valid "
                "canonical node citing a line-suffixed reference to "
                f"{_KIND_RS_PATH} whose range includes that constant's own "
                "declaration line, via the mechanical citation classifier "
                "in this builder module."
            ),
            "entry_class": "FACT",
            "evidence": [
                "launchpad/project-intelligence/corpus/index_defs/event_kind_index.py"
            ],
        }
    ]


SPEC = {
    "name": "event-kind-index",
    "output_path": "generated/event-kind-index.md",
    "node_id": "generated-event-kind-index",
    "title": "Event kind index: generated cross-reference of Nostr event kinds and documenting nodes",
    "node_type": "governance",
    "audiences": ["agent", "developer"],
    "subject": (
        "this repository's Nostr event kind integers (discovered from "
        "crates/buzz-core/src/kind.rs's `pub const KIND_*` declarations), "
        "cross-referenced against the canonical corpus nodes that cite a "
        "specific kind's declaration line as evidence"
    ),
    "generate": _generate,
    "extra_evidence": _extra_evidence,
    "relationships": (
        {"type": "references", "target": "corpus-agents"},
        {"type": "implements", "target": "corpus-template-generated-index"},
    ),
}
