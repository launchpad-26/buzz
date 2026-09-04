"""Builder: generated/layer-index.md -- issue #900 (parent PRD #621).

A generated index of every canonical corpus node under the `layers/` subtree,
grouped by sub-layer (`compute`, `configuration`, `lifecycle`,
`observability`), selected by the corpus-root-relative path prefix
`layers/`.

Why the path prefix is the rule, not front-matter `type` -- both signals were
checked against the real corpus at the base revision, following #890's
precedent of checking rather than assuming:

- Front-matter `type`: node.schema.json's type enum has no per-sub-layer
  value (`compute`, `configuration`, ...), so every node genuinely under
  `layers/` carries the single shared value `type: layers` -- so far this
  matches the path exactly. But `type: layers` is not unique to the
  `layers/` subtree: `generated/configuration-index.md` (#890's own
  generated document) also declares `type: layers`, following the same
  subject-type precedent this builder uses for its own front matter. A
  `type: layers` rule therefore over-includes a generated index that is not
  itself a layer node -- 37 matches corpus-wide against 36 real layer nodes
  at this revision.
- The path prefix `layers/` matches exactly the 36 real layer nodes (10
  compute, 9 configuration, 6 lifecycle, 11 observability) and nothing else.
  It is the accurate signal, generalizing #890's finding (path correct, type
  over-includes) from the configuration subtree to the whole layers tree.

The over-inclusion is structurally prevented regardless of which signal a
builder chooses: `indexes.py`'s `build_context` excludes every registered
builder's `output_path` -- including `generated/configuration-index.md` --
from canonical inputs before any builder runs, so `generated/
configuration-index.md` never reaches this builder's `ctx.valid_nodes` at
all. The divergence is still named here and surfaced in a generated
subsection each run (the #887 capability-index precedent for transparency),
because that framework guard is not obvious to a reader of the rendered
document, and because a future node could reintroduce `type: layers` outside
`layers/` in a way the guard does not cover (any node that is not itself a
registered generated output).

`node_type` choice: this index node carries `type: layers` -- the subject
nodes' own enum value, following the capability-index/configuration-index
precedent that a subject-specific index takes its subject's type
(README/standards use `governance` only for nodes that govern the corpus
itself; this document governs nothing, it is a derived view of the layers
surface).

Contract: module-level `SPEC` per indexes.py's IndexSpec; the framework
renders all front matter and the templates/generated-index.md body skeleton.
This module supplies only the subject-specific listing and the
inclusion/exclusion bullets.
"""

from __future__ import annotations

from pathlib import PurePosixPath

_PATH_PREFIX = "layers/"
_EXPECTED_TYPE = "layers"
_KNOWN_SUBLAYERS = ("compute", "configuration", "lifecycle", "observability")


def _sublayer(rel_path: str) -> str:
    """The grouping label for a listing row: the path segment directly under
    `layers/` (e.g. `compute`), `(root)` for a node directly under `layers/`
    with no further subdirectory, or `(other)` -- never used for nodes this
    builder actually selects today, but kept so a future sub-layer or a
    direct `layers/*.md` child is grouped honestly rather than silently
    dropped or misfiled."""
    parts = PurePosixPath(rel_path).parts
    if parts[0] != "layers":
        return "(other)"
    if len(parts) <= 2:
        return "(root)"
    return parts[1]


def _group_sort_key(group: str) -> tuple:
    """Named sub-layers sort alphabetically first; the `(root)` and `(other)`
    edge-case buckets always sort after them, regardless of their own
    parenthesized spelling (which would otherwise sort before every letter)."""
    if group == "(root)":
        return (1, group)
    if group == "(other)":
        return (2, group)
    return (0, group)


def _generate(ctx):
    included = sorted(
        (n for n in ctx.valid_nodes if ctx.rel_path(n).startswith(_PATH_PREFIX)),
        key=ctx.rel_path,
    )
    groups: dict[str, list] = {}
    for node in included:
        groups.setdefault(_sublayer(ctx.rel_path(node)), []).append(node)

    type_divergent_outside = sorted(
        (
            n
            for n in ctx.valid_nodes
            if not ctx.rel_path(n).startswith(_PATH_PREFIX)
            and n.data.get("type") == _EXPECTED_TYPE
        ),
        key=ctx.rel_path,
    )

    lines = [
        "## Layer index",
        "",
        f"{len(included)} canonical corpus node(s) live under "
        f"`{_PATH_PREFIX}` at this revision, across {len(groups)} sub-layer(s).",
        "",
    ]
    for group in sorted(groups, key=_group_sort_key):
        nodes = groups[group]
        lines.append(f"### {group}")
        lines.append("")
        lines.append(f"{len(nodes)} node(s).")
        lines.append("")
        lines.append("| Id | Path | Status |")
        lines.append("|---|---|---|")
        for node in nodes:
            rel = ctx.rel_path(node)
            status = node.data.get("status", "")
            lines.append(f"| {node.id} | `{rel}` | {status} |")
        lines.append("")

    lines += [
        f"### Nodes elsewhere with `type: {_EXPECTED_TYPE}`",
        "",
        "The path prefix is the inclusion rule, not front-matter `type`, so a "
        f"valid node outside `{_PATH_PREFIX}` that nonetheless declares "
        f"`type: {_EXPECTED_TYPE}` is not listed above; this subsection "
        "surfaces any such divergence instead of leaving it silent:",
        "",
    ]
    if type_divergent_outside:
        lines += ["| Id | Path |", "|---|---|"]
        for node in type_divergent_outside:
            lines.append(f"| {node.id} | `{ctx.rel_path(node)}` |")
    else:
        lines.append("- None at this revision.")

    return {
        "sections": "\n".join(lines),
        "includes": [
            "every valid canonical corpus node whose corpus-root-relative "
            f"path starts with `{_PATH_PREFIX}` -- the path prefix is the "
            "whole rule, because front-matter `type` alone over-includes: "
            f"`type: {_EXPECTED_TYPE}` also matches a generated document "
            "outside the layers tree that shares the subject-type "
            "convention (see the module docstring for the exact node and "
            "count at this revision)"
        ],
        "excludes": [
            "nodes selected by front-matter `type` alone: any valid node "
            f"outside `{_PATH_PREFIX}` with `type: {_EXPECTED_TYPE}` is "
            "surfaced in its own divergence subsection instead of listed",
            "nodes the validator rejects (a parse or schema error): an "
            "invalid node has no trustworthy path-independent identity to "
            "list",
        ],
        "ordering": (
            "sub-layer subsections in alphabetical order by the path "
            f"segment directly under `{_PATH_PREFIX}` (`(root)` and "
            "`(other)` sort after named sub-layers by construction of the "
            "grouping key); rows within each subsection sorted by "
            "corpus-root-relative path; the divergence subsection uses the "
            "same path sort"
        ),
        "not_covered": [
            "What each layer node actually documents -- the listed nodes "
            "themselves own their content; this index only locates them.",
            "A per-sub-layer index distinct from this whole-tree listing -- "
            "`generated/configuration-index.md` (#890) already exists for "
            "the configuration sub-layer; the other three sub-layers have "
            "no dedicated index of their own.",
        ],
    }


SPEC = {
    "name": "layer-index",
    "output_path": "generated/layer-index.md",
    "node_id": "generated-layer-index",
    "title": "Layer index: generated index",
    "node_type": _EXPECTED_TYPE,
    "audiences": ["agent", "developer", "operator", "reviewer"],
    "subject": "every canonical corpus node under layers/, grouped by sub-layer",
    "generate": _generate,
    "relationships": (
        {"type": "references", "target": "corpus-agents"},
        {"type": "implements", "target": "corpus-template-generated-index"},
    ),
}
