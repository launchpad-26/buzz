"""Builder for generated/dependency-graph.md -- issue #896 (parent PRD #621).

This document is a GRAPH (edges between corpus nodes), not a flat listing of
one node type: templates/generated-index.md's own boundary table names
dependency-graph.md explicitly ("Edges between nodes, not a flat listing"), so
this builder reuses the framework's front matter and body skeleton but supplies
graph-shaped ``sections`` content instead of an index-shaped table of nodes --
the same non-index-shaped-sibling pattern code-to-doc-map.py (#888) and
coverage.py (#892) already established.

Source and scope: every relationship a valid canonical node declares in its own
front-matter ``relationships[]`` array, exactly as ``ctx.forward_edges`` already
carries it -- no new graph derivation happens in this module. All five schema
forward types (``depends-on``, ``supersedes``, ``implements``, ``references``,
``part-of``) are graphed, not a narrower "depends-on only" subset: the dispatch
brief for this task says to use ``ctx.forward_edges`` -- unfiltered -- "as your
source", and against the real corpus at authoring time a depends-on-only
document would carry only 6 rows (192 forward edges total, of which 167 are
``references``, 17 ``implements``, 6 ``depends-on``, 2 ``part-of``, 0
``supersedes``), too thin a reading of that instruction to be the intended one.
"Dependency" is read here as the corpus's own declared relationship structure in
general -- every forward type expresses some form of inter-node coupling, from
``depends-on``'s strict "target must stay true/current" directionality down to
``references``'s soft citation -- rather than one schema enum value alone.

Four labeled subsections, each rendered directly from ``ctx`` with no new
derivation logic:

1. **Forward edges (authored)** -- one row per ``ctx.forward_edges`` entry,
   already sorted (source, type, target) by the framework.
2. **Derived inverse edges (generated, not authored)** -- one sub-table per
   ``ctx.inverse_edges`` key (``depended-on-by``, ``has-part``,
   ``implemented-by``, ``superseded-by``, sorted), each row a target and its
   sorted source list. Explicitly labeled generated/derived: these are computed
   by ``indexes.py``'s ``build_context`` from the forward edges above, never
   hand-authored, and ``node.schema.json``'s relationship-type enum has no field
   for any of the four names regardless. ``references``'s own inverse
   (``referenced-by``) is marked ``inverse: authored`` in
   relationships.schema.json, so the framework never computes it and it is not
   rendered here -- noted explicitly in the exclusion list rather than silently
   absent.
3. **Broken edges** -- always rendered, even when empty, from
   ``ctx.broken_edges``. Feature #621's own acceptance criterion states
   "Orphaned nodes, unresolved relationships, broken provenance and stale source
   references are visible" -- an unresolved relationship is exactly a broken
   edge, so this section is never hidden or summarized away.
4. **Orphaned nodes** -- always rendered, even when empty, from ``ctx.orphans``
   (valid nodes with no forward or inverse edge in either direction), the same
   acceptance criterion naming orphaned nodes directly.

node_type choice: ``governance``. The listing's subject is the corpus's own
relationship structure, not a subject-domain concern with its own enum value --
the same corpus-about-corpus-traceability reasoning code-to-doc-map.py and
coverage.py already give for their own ``type: governance`` choice.

relationships: only ``references -> corpus-agents``. ``implements ->
corpus-template-generated-index`` is deliberately omitted, for the identical
reason code-to-doc-map.py and coverage.py already state: the template's own
boundary table classifies this document as a graph outside its index-shaped
scope, so claiming to implement it would contradict the template's own text.
"""

from __future__ import annotations

_INVERSE_LABELS = {
    "depended-on-by": "depends-on",
    "superseded-by": "supersedes",
    "implemented-by": "implements",
    "has-part": "part-of",
}


def _forward_edges_section(ctx) -> list[str]:
    lines = ["### Forward edges (authored)", ""]
    lines.append(
        "One row per relationship a valid canonical node declares in its own "
        "front-matter `relationships[]` array, where the declared `target` "
        "resolves to another valid node's `id`."
    )
    lines.append("")
    if ctx.forward_edges:
        lines += ["| Source | Type | Target |", "|---|---|---|"]
        for edge in ctx.forward_edges:
            lines.append(f"| {edge.source} | {edge.type} | {edge.target} |")
    else:
        lines.append(
            "No canonical node currently declares a relationship that resolves "
            "to another valid node's id. This is an empty fact, not an "
            "omission -- it will populate as nodes with `relationships[]` "
            "merge."
        )
    return lines


def _inverse_edges_section(ctx) -> list[str]:
    lines = ["### Derived inverse edges (generated, not authored)", ""]
    lines.append(
        "Computed by `indexes.py`'s `build_context` from the forward edges "
        "above, for the four relationship types "
        "`launchpad/docs/corpus/schema/relationships.schema.json` marks "
        "`inverse: generated` (`depends-on` -> `depended-on-by`, `supersedes` "
        "-> `superseded-by`, `implements` -> `implemented-by`, `part-of` -> "
        "`has-part`). Never hand-authored -- `node.schema.json`'s "
        "`relationships[].type` enum has no field for any of these four names, "
        "so a node's own front matter cannot declare one regardless. "
        "`references`'s own inverse (`referenced-by`) is marked `inverse: "
        "authored`, not generated, so the framework does not compute it and it "
        "is not rendered here."
    )
    lines.append("")
    for inverse_type in sorted(ctx.inverse_edges):
        forward_type = _INVERSE_LABELS.get(inverse_type, "?")
        by_target = ctx.inverse_edges[inverse_type]
        lines.append(f"#### `{inverse_type}` (derived from `{forward_type}`)")
        lines.append("")
        if by_target:
            lines += ["| Target | Sources (`" + forward_type + "` from) |", "|---|---|"]
            for target in sorted(by_target):
                sources = ", ".join(by_target[target])
                lines.append(f"| {target} | {sources} |")
        else:
            lines.append(
                f"No `{forward_type}` edge currently resolves to a target, so "
                f"there is no `{inverse_type}` row at this revision."
            )
        lines.append("")
    return lines


def _broken_edges_section(ctx) -> list[str]:
    lines = ["### Broken edges", ""]
    lines.append(
        "Relationships whose declared `target` resolves to no valid node id. "
        "Always rendered, never hidden or summarized away -- an unresolved "
        "relationship is exactly the kind of finding this document exists to "
        "surface (Feature #621's own acceptance criterion names \"unresolved "
        "relationships\" and \"broken provenance\" as things that must stay "
        "visible)."
    )
    lines.append("")
    if ctx.broken_edges:
        lines += ["| Source | Type | Declared target (unresolved) |", "|---|---|---|"]
        for edge in ctx.broken_edges:
            lines.append(f"| {edge.source} | {edge.type} | {edge.target} |")
    else:
        lines.append(
            f"None at this revision -- {len(ctx.forward_edges)} declared "
            "relationship(s) checked, every one resolved to a valid node id."
        )
    return lines


def _orphaned_nodes_section(ctx) -> list[str]:
    lines = ["### Orphaned nodes", ""]
    lines.append(
        "Valid canonical nodes with no forward or inverse edge in either "
        "direction -- they declare no relationship of their own, and no other "
        "node's relationship targets them. Always rendered, never hidden -- "
        "Feature #621's own acceptance criterion names orphaned nodes directly "
        "as a finding this document must surface."
    )
    lines.append("")
    if ctx.orphans:
        by_id = {n.id: n for n in ctx.valid_nodes if isinstance(n.id, str)}
        lines += ["| Orphaned node id | Path |", "|---|---|"]
        for node_id in ctx.orphans:
            node = by_id.get(node_id)
            path = ctx.rel_path(node) if node is not None else "?"
            lines.append(f"| {node_id} | `{path}` |")
    else:
        lines.append(
            "None at this revision -- every valid canonical node has at least "
            "one forward or inverse edge."
        )
    return lines


def _generate(ctx):
    lines = ["## Dependency graph", ""]
    lines += _forward_edges_section(ctx)
    lines.append("")
    lines += _inverse_edges_section(ctx)
    lines += _broken_edges_section(ctx)
    lines.append("")
    lines += _orphaned_nodes_section(ctx)

    return {
        "sections": "\n".join(lines),
        "includes": [
            "every relationship declared in a valid canonical node's own "
            "front-matter `relationships[]` array whose `target` resolves to "
            "another valid node's `id` -- one forward-edge row per (source, "
            "type, target) triple, exactly as `ctx.forward_edges` carries it",
            "the four generated-inverse relationship views (`depended-on-by`, "
            "`superseded-by`, `implemented-by`, `has-part`) computed from "
            "those forward edges by the framework itself "
            "(`indexes.py`'s `build_context`), for the relationship types "
            "`relationships.schema.json` marks `inverse: generated`",
            "every relationship whose declared target resolves to no valid "
            "node id, in its own always-visible broken-edges section",
            "every valid canonical node with no forward or inverse edge in "
            "either direction, in its own always-visible orphaned-nodes "
            "section",
        ],
        "excludes": [
            "the `references` relationship type's own inverse "
            "(`referenced-by`): `relationships.schema.json` marks it "
            "`inverse: authored`, not generated, so the framework does not "
            "compute it and this document does not fabricate one",
            "any relationship declared by a node whose own front matter fails "
            "schema validation (`node.error` is not `None`) -- the "
            "framework's `valid_nodes` / `forward_edges` already exclude "
            "these before this builder ever runs",
            "citation-level or prose-level dependencies, such as an evidence "
            "citation naming another file -- only front-matter "
            "`relationships[]` entries are edges in this graph; "
            "`generated/code-to-doc-map.md` covers path citations separately",
        ],
        "ordering": (
            "forward edges sorted by (source, type, target); each inverse-edge "
            "view sorted by target, with its source list sorted; broken edges "
            "sorted by (source, type, target); orphaned nodes sorted by id -- "
            "ctx's own deterministic sort order from indexes.py, unchanged by "
            "this builder"
        ),
        "not_covered": [
            "Whether a broken edge or an orphaned node is a genuine authoring "
            "mistake or an intentional, temporary state (e.g. a sibling node "
            "not yet merged) -- that judgement is left to a human reader, not "
            "inferred here.",
            "Indirect or transitive dependency paths (e.g. A depends-on B "
            "depends-on C implying something about A and C) -- only the "
            "direct edges the corpus declares are rendered, never a "
            "transitive closure.",
            "Narrative or citation-shaped dependencies described in a node's "
            "body text but not captured in its structured `relationships[]` "
            "array.",
        ],
    }


def _extra_evidence(ctx):
    inverse_counts = {k: len(v) for k, v in ctx.inverse_edges.items()}
    return [
        {
            "statement": (
                f"At input digest sha256:{ctx.input_digest}, the canonical "
                f"nodes declare {len(ctx.forward_edges)} forward "
                f"relationship(s) that resolve to a valid node id, "
                f"{len(ctx.broken_edges)} that do not (broken edges), and "
                f"{len(ctx.orphans)} valid node(s) with no edge in either "
                f"direction (orphans); the four derived inverse views have "
                f"{inverse_counts.get('depended-on-by', 0)} depended-on-by, "
                f"{inverse_counts.get('superseded-by', 0)} superseded-by, "
                f"{inverse_counts.get('implemented-by', 0)} implemented-by "
                f"and {inverse_counts.get('has-part', 0)} has-part target(s), "
                "all computed by indexes.py's build_context, never "
                "hand-authored."
            ),
            "entry_class": "FACT",
            "evidence": ["launchpad/project-intelligence/corpus/indexes.py"],
        }
    ]


SPEC = {
    "name": "dependency-graph",
    "output_path": "generated/dependency-graph.md",
    "node_id": "generated-dependency-graph",
    "title": "Dependency graph: generated relationship graph",
    "node_type": "governance",
    "audiences": ["agent", "developer", "reviewer"],
    "subject": (
        "the corpus's own declared relationship graph -- forward edges, their "
        "generated inverses, unresolved (broken) edges, and orphaned nodes"
    ),
    "generate": _generate,
    "extra_evidence": _extra_evidence,
    "relationships": ({"type": "references", "target": "corpus-agents"},),
}
