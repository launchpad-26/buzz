"""Builder: generated/capability-index.md -- issue #887 (parent PRD #621).

A generated index of every canonical corpus node whose front-matter ``type``
is ``capabilities``. The inclusion rule is the schema field alone -- never the
``capabilities/`` path prefix -- because the two signals measurably diverge at
this revision: ``capabilities/communities/community-provisioning.md`` lives
under the path but carries ``type: architecture``, so a path rule would list a
node the schema says is something else. The divergence is itself surfaced in a
generated subsection each run, so a reader can always see exactly where path
and type disagree instead of wondering whether an absence is a bug.

``node_type`` choice: this index node carries ``type: capabilities`` -- the
subject's own node.schema.json enum value. The README/standards precedent uses
``governance`` for nodes that govern the corpus itself; this document does not
govern anything, it is a derived view *of the capabilities surface*, so the
subject-specific type is the closer fit (the batch dispatch for #886-#906
explicitly allows a subject-specific index to take its subject's own type,
justified here as required).

Contract: module-level ``SPEC`` per indexes.py's IndexSpec; the framework
renders all front matter and the templates/generated-index.md body skeleton.
This module supplies only the subject-specific listing and the
inclusion/exclusion bullets.
"""

from __future__ import annotations

from pathlib import PurePosixPath

_TYPE = "capabilities"
_PATH_PREFIX = "capabilities/"


def _area(rel_path: str) -> str:
    """Deterministic grouping label for a listing row: the path segment under
    ``capabilities/`` (e.g. ``channels``), else the node's parent directory,
    else ``(root)`` -- so a hypothetical capabilities-typed node outside the
    tree still gets a stable, honest label."""
    parts = PurePosixPath(rel_path).parts
    if parts[0] == "capabilities" and len(parts) > 2:
        return parts[1]
    if len(parts) > 1:
        return parts[-2]
    return "(root)"


def _generate(ctx):
    included = sorted(
        (n for n in ctx.valid_nodes if n.data.get("type") == _TYPE),
        key=ctx.rel_path,
    )
    divergent = sorted(
        (
            n
            for n in ctx.valid_nodes
            if ctx.rel_path(n).startswith(_PATH_PREFIX)
            and n.data.get("type") != _TYPE
        ),
        key=ctx.rel_path,
    )

    lines = [
        "## Capability index",
        "",
        f"{len(included)} canonical corpus node(s) carry front-matter "
        f"`type: {_TYPE}` at this revision.",
        "",
        "| Capability area | Id | Path | Status |",
        "|---|---|---|---|",
    ]
    for node in included:
        rel = ctx.rel_path(node)
        status = node.data.get("status", "")
        lines.append(f"| {_area(rel)} | {node.id} | `{rel}` | {status} |")

    lines += [
        "",
        "### Nodes under `capabilities/` with a different type",
        "",
        "Path prefix and front-matter type can disagree; this index follows "
        "the type. The following valid node(s) live under `capabilities/` but "
        "are excluded because their `type` is not `capabilities`:",
        "",
    ]
    if divergent:
        lines += ["| Path | Type |", "|---|---|"]
        for node in divergent:
            lines.append(f"| `{ctx.rel_path(node)}` | {node.data.get('type')} |")
    else:
        lines.append("- None at this revision.")

    return {
        "sections": "\n".join(lines),
        "includes": [
            "every valid canonical corpus node whose front-matter `type` is "
            f"`{_TYPE}` -- the schema field is the whole rule, evaluated by "
            "the generator against the validator's own parsed front matter"
        ],
        "excludes": [
            "nodes selected by path alone: living under `capabilities/` does "
            "not qualify a node -- any valid node there with a different "
            "`type` is listed in the divergence subsection instead of the "
            "index",
            "nodes the validator rejects (a parse or schema error): an "
            "invalid node has no trustworthy `type` to match on",
        ],
        "ordering": (
            "listing rows sorted by corpus-root-relative path (which groups "
            "rows by capability area); the divergence table uses the same sort"
        ),
        "not_covered": [
            "What each capability does -- the listed nodes themselves own "
            "their content; this index only locates them.",
        ],
    }


SPEC = {
    "name": "capability-index",
    "output_path": "generated/capability-index.md",
    "node_id": "generated-capability-index",
    "title": "Capability index: generated index",
    "node_type": _TYPE,
    "audiences": ["agent", "developer", "reviewer"],
    "subject": (
        "every canonical corpus node with front-matter type: capabilities"
    ),
    "generate": _generate,
    "relationships": (
        {"type": "references", "target": "corpus-agents"},
        {"type": "implements", "target": "corpus-template-generated-index"},
    ),
}
