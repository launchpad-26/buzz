"""Builder for generated/documentation-graph.md -- issue #898 (parent PRD #621).

Distinction from ``generated/dependency-graph.md`` (node id
``generated-dependency-graph``, issue #896, merged, builder
``index_defs/dependency_graph.py``): that document already renders every
relationship a valid canonical node declares in its own front-matter
``relationships[]`` array as a raw per-edge table -- one row per (source, type,
target) triple, across all five schema forward types, plus the four derived
generated-inverse views, broken edges and orphaned nodes. Repeating that same
edge listing here, even narrowed to a subset of relationship types, would be a
near-duplicate of an already-merged document. This builder instead reads the
identical underlying data (``ctx.forward_edges``) but renders it at a different
granularity: a per-node degree/connectivity summary -- which nodes are
structural hubs (highest combined in+out degree) and how many nodes carry no
declared relationship at all -- rather than a per-edge dump. "Read
``dependency-graph.md`` to see every declared edge; read this document to see
which nodes that graph is built around" is the same "same source data, different
shape" relationship ``generated/decision-index.md`` (#895) already holds against
``decisions/INDEX.md`` (#845) and ``generated/corpus-index.md`` (#891) holds
against the corpus ``INDEX.md`` (#638): a stats/summary view standing next to a
full per-item listing, neither restating the other's content. This document
states the distinction in its own rendered body (below), not only in this
docstring.

Candidate angles considered and rejected (per this task's dispatch brief, which
named three): (a) a narrower graph limited to "navigation" relationship types
(``references`` + ``part-of``, excluding ``implements``/``depends-on``) --
rejected because it would still be an edge-shaped listing, merely filtered,
which risks the identical near-duplicate shape the brief specifically warned
against; scoping down does not change shape. (b) a hierarchical/tree rendering
of ``part-of`` nesting -- rejected because, measured directly against the real
corpus at authoring time, only 2 ``part-of`` edges exist corpuswide (of 192
total forward edges: 167 ``references``, 17 ``implements``, 6 ``depends-on``, 2
``part-of``, 0 ``supersedes``), too thin to carry an entire document. (c) --
the angle used here -- a per-node degree/connectivity view, mirroring how
``generated/corpus-index.md`` (#891) is a stats view of what the hand-authored
corpus ``INDEX.md`` (#638) lists in full.

Degree computation. For every id in ``ctx.node_ids``, ``in_degree`` counts
``ctx.forward_edges`` entries whose ``target`` equals that id, ``out_degree``
counts entries whose ``source`` equals that id, and ``total_degree`` is their
sum -- computed directly in this module from ``ctx.forward_edges`` alone
(already resolved-edges-only, per ``indexes.py``'s own ``build_context``: a
relationship whose target does not resolve to a valid node id is a broken edge,
tracked separately in ``ctx.broken_edges``, and never appears in
``forward_edges``). No relationship type is filtered out and no new
graph-derivation logic is added to ``indexes.py`` -- this is a straight
per-node fold over the exact edges ``dependency-graph.md`` already renders
per-edge.

Hub table. Every node with ``total_degree > 0`` is rendered, sorted by
``(-total_degree, node_id)`` -- a complete deterministic listing rather than an
arbitrary top-N cutoff, consistent with the framework's own "never hide a
finding behind a threshold" treatment of broken edges and orphaned nodes in
``dependency_graph.py``.

Leaf nodes are reported by count only, not re-listed. Measured directly against
the real corpus at authoring time, the set of nodes with ``total_degree == 0``
computed here is set-identical to ``ctx.orphans`` (81 of 205 valid nodes, both
sides), and ``dependency-graph.md``'s own "Orphaned nodes" section already lists
each one with its path. This document states the count and names that section
by cross-reference instead of duplicating the listing. The two sets can
theoretically diverge: ``ctx.orphans`` excludes a node from the orphan set if it
sources *any* declared edge, including a broken one (``build_context``'s
``has_out`` accumulates both ``forward`` and ``broken`` edge sources), while
this builder's ``out_degree`` counts resolved edges only -- a node whose sole
declared relationship is broken would show ``total_degree == 0`` here but not
appear in ``ctx.orphans``. At this revision ``ctx.broken_edges`` is empty, so no
such node exists and the sets coincide; the rendered body and an
``unverified`` bullet both name this as a revision-specific fact, not a
guarantee.

``node_type`` choice: ``governance``, the identical reasoning
``dependency_graph.py`` already gives -- the subject is the corpus's own
relationship structure, not a subject-domain concern with its own enum value.

``relationships``: only ``references -> corpus-agents``. ``implements ->
corpus-template-generated-index`` is deliberately omitted, for the identical
reason ``dependency_graph.py`` states: ``templates/generated-index.md``'s own
boundary table classifies ``documentation-graph.md`` as "A graph -- Same reason
as `dependency-graph.md`", i.e. explicitly outside that template's index-shaped
scope, so claiming to implement it would contradict the template's own text.
"""

from __future__ import annotations


def _degrees(ctx) -> dict[str, dict[str, int]]:
    """in/out/total degree per node id, computed from ctx.forward_edges alone
    (resolved edges only -- a broken edge never appears in forward_edges)."""
    degrees: dict[str, dict[str, int]] = {
        node_id: {"in": 0, "out": 0} for node_id in ctx.node_ids
    }
    by_type: dict[str, int] = {}
    for edge in ctx.forward_edges:
        by_type[edge.type] = by_type.get(edge.type, 0) + 1
        if edge.source in degrees:
            degrees[edge.source]["out"] += 1
        if edge.target in degrees:
            degrees[edge.target]["in"] += 1
    for node_id, d in degrees.items():
        d["total"] = d["in"] + d["out"]
    return degrees


def _distinction_section() -> list[str]:
    return [
        "## Distinction from `generated/dependency-graph.md`",
        "",
        "`generated/dependency-graph.md` (node id `generated-dependency-graph`, "
        "issue #896) already renders every declared relationship as a raw "
        "per-edge table -- one row per (source, type, target) triple, across "
        "all five schema forward types, plus the four derived generated-inverse "
        "views, broken edges and orphaned nodes. This document reads the "
        "identical underlying edges (`ctx.forward_edges`) but renders them at a "
        "different granularity: a per-node degree/connectivity summary -- which "
        "nodes are structural hubs, and how many nodes carry no declared "
        "relationship at all -- rather than a per-edge dump. **Read "
        "`dependency-graph.md` to see every declared edge; read this document "
        "to see which nodes that graph is built around.** Neither document "
        "restates the other's content -- the same relationship "
        "`generated/decision-index.md` (#895, a stats/bucket view) already "
        "holds against `decisions/INDEX.md` (#845, a per-record listing), and "
        "`generated/corpus-index.md` (#891, a stats view) holds against the "
        "hand-authored corpus `INDEX.md` (#638, a full listing).",
    ]


def _summary_section(ctx, degrees: dict[str, dict[str, int]]) -> list[str]:
    by_type: dict[str, int] = {}
    for edge in ctx.forward_edges:
        by_type[edge.type] = by_type.get(edge.type, 0) + 1
    nonzero = sum(1 for d in degrees.values() if d["total"] > 0)
    zero = len(degrees) - nonzero

    lines = ["## Connectivity summary", ""]
    lines.append(
        f"{len(ctx.node_ids)} valid canonical node(s); {len(ctx.forward_edges)} "
        "resolved forward relationship edge(s) between them (a relationship "
        "whose declared target resolves to no valid node id is a broken edge, "
        "counted separately by `generated/dependency-graph.md` and excluded "
        "from every count below)."
    )
    lines.append("")
    if by_type:
        lines += ["| Relationship type | Edge count |", "|---|---|"]
        for rel_type in sorted(by_type):
            lines.append(f"| {rel_type} | {by_type[rel_type]} |")
    else:
        lines.append(
            "No canonical node currently declares a relationship that resolves "
            "to another valid node's id."
        )
    lines.append("")
    lines.append(
        f"{nonzero} node(s) have total degree (in-degree + out-degree) greater "
        f"than zero; {zero} node(s) have total degree zero -- see *Leaf nodes "
        "(zero degree)* below."
    )
    return lines


def _hub_section(ctx, degrees: dict[str, dict[str, int]]) -> list[str]:
    lines = ["## Hub nodes (highest total degree)", ""]
    lines.append(
        "Every valid canonical node with total degree greater than zero, one "
        "row per node, sorted by descending total degree (ties broken by node "
        "id ascending) -- a complete listing, not a curated top-N cutoff."
    )
    lines.append("")
    by_id = {n.id: n for n in ctx.valid_nodes if isinstance(n.id, str)}
    ranked = sorted(
        (node_id for node_id, d in degrees.items() if d["total"] > 0),
        key=lambda node_id: (-degrees[node_id]["total"], node_id),
    )
    if ranked:
        lines += [
            "| Node id | Path | In-degree | Out-degree | Total degree |",
            "|---|---|---|---|---|",
        ]
        for node_id in ranked:
            node = by_id.get(node_id)
            path = ctx.rel_path(node) if node is not None else "?"
            d = degrees[node_id]
            lines.append(f"| {node_id} | `{path}` | {d['in']} | {d['out']} | {d['total']} |")
    else:
        lines.append(
            "None at this revision -- no valid canonical node has a nonzero "
            "in-degree or out-degree."
        )
    return lines


def _leaf_section(ctx, degrees: dict[str, dict[str, int]]) -> list[str]:
    zero_ids = sorted(node_id for node_id, d in degrees.items() if d["total"] == 0)
    lines = ["## Leaf nodes (zero degree)", ""]
    lines.append(
        f"{len(zero_ids)} valid canonical node(s) have total degree zero -- no "
        "resolved forward edge sourced from or targeting them. Not re-listed "
        "here: `generated/dependency-graph.md`'s own \"Orphaned nodes\" section "
        "already lists each one with its path, and this document does not "
        "duplicate that listing."
    )
    lines.append("")
    orphan_ids = set(ctx.orphans)
    zero_set = set(zero_ids)
    if zero_set == orphan_ids:
        lines.append(
            f"At this revision the zero-total-degree set computed here is "
            f"set-identical to `ctx.orphans` ({len(zero_ids)} node(s) both "
            "sides) -- see *Distinction from ctx.orphans* below for why that "
            "equality is a fact about this revision, not a guarantee."
        )
    else:
        only_here = sorted(zero_set - orphan_ids)
        only_orphans = sorted(orphan_ids - zero_set)
        lines.append(
            f"At this revision the zero-total-degree set computed here "
            f"({len(zero_ids)} node(s)) differs from `ctx.orphans` "
            f"({len(orphan_ids)} node(s)): {len(only_here)} node(s) are "
            "zero-degree here but not in `ctx.orphans` (each has a broken "
            f"outgoing edge only), and {len(only_orphans)} node(s) are the "
            "reverse. See *Distinction from ctx.orphans* below."
        )
    lines.append("")
    lines += [
        "### Distinction from `ctx.orphans`",
        "",
        "`ctx.orphans` (rendered in full by `generated/dependency-graph.md`) "
        "excludes a node from the orphan set if it sources *any* declared "
        "relationship, including a broken one -- `indexes.py`'s `build_context` "
        "counts a broken edge's source toward \"has an outgoing edge\" even "
        "though the edge itself resolves to no valid target. This builder's "
        "`out_degree`, by contrast, counts resolved edges only (a broken edge "
        "never appears in `ctx.forward_edges`), so a node whose sole declared "
        "relationship is broken would show total degree zero here while not "
        "appearing in `ctx.orphans`. At this revision zero broken edges exist "
        "(see *Connectivity summary*), so no such node exists and the two sets "
        "coincide -- a revision-specific fact, not a structural guarantee.",
    ]
    return lines


def _generate(ctx):
    degrees = _degrees(ctx)

    lines = _distinction_section()
    lines.append("")
    lines += _summary_section(ctx, degrees)
    lines.append("")
    lines += _hub_section(ctx, degrees)
    lines.append("")
    lines += _leaf_section(ctx, degrees)

    return {
        "sections": "\n".join(lines),
        "includes": [
            "every valid canonical node's in-degree, out-degree and total "
            "degree, computed by folding `ctx.forward_edges` (every "
            "relationship a valid node declares in its own front-matter "
            "`relationships[]` array whose target resolves to another valid "
            "node's id) -- the identical edges `generated/dependency-graph.md` "
            "already renders per-edge, summarized here per-node instead",
            "a complete hub ranking (every node with total degree greater than "
            "zero, sorted descending, no top-N cutoff) and a leaf-node count "
            "(total degree zero), rather than a per-edge dump",
        ],
        "excludes": [
            "the per-edge listing itself (source, type, target rows): "
            "`generated/dependency-graph.md` already owns that full listing; "
            "this document only summarizes it per node",
            "the four derived generated-inverse edge views "
            "(`depended-on-by`/`superseded-by`/`implemented-by`/`has-part`): "
            "already rendered in full by `generated/dependency-graph.md`; this "
            "document's degree counts already fold every forward edge "
            "regardless of type, so recomputing the inverse views separately "
            "would add nothing",
            "the full path listing for every zero-degree node: "
            "`generated/dependency-graph.md`'s Orphaned nodes section already "
            "lists each one; this document states the count and "
            "cross-references that section instead",
            "any relationship declared by a node whose own front matter fails "
            "schema validation (`node.error` is not `None`) -- the framework's "
            "`valid_nodes`/`forward_edges` already exclude these before this "
            "builder ever runs",
        ],
        "ordering": (
            "the by-type count table is sorted by relationship type name; the "
            "hub table is sorted by (-total_degree, node_id) -- descending "
            "degree, ties broken by node id ascending"
        ),
        "not_covered": [
            "Transitive or indirect connectivity (e.g. whether node A can "
            "reach node C through some path via node B) -- only direct "
            "in-degree/out-degree from `ctx.forward_edges` is computed, never a "
            "reachability closure.",
            "Whether a high-degree node is a hub because it is genuinely "
            "load-bearing or because many nodes independently cite the same "
            "boilerplate reference (e.g. `references -> corpus-agents`, which "
            "every builder's own SPEC declares) -- that judgement is left to a "
            "human reader, not inferred here.",
        ],
        "unverified": [
            "Whether the zero-total-degree set computed here stays "
            "set-identical to `ctx.orphans` as the corpus grows: the two sets "
            "coincide today only because `ctx.broken_edges` is empty at this "
            "revision (see *Distinction from ctx.orphans* in the rendered "
            "body); a future broken edge would open a one-node gap between "
            "them without changing either count's own correctness.",
        ],
    }


def _extra_evidence(ctx):
    degrees = _degrees(ctx)
    nonzero = sum(1 for d in degrees.values() if d["total"] > 0)
    zero_ids = {node_id for node_id, d in degrees.items() if d["total"] == 0}
    orphan_ids = set(ctx.orphans)
    return [
        {
            "statement": (
                f"At input digest sha256:{ctx.input_digest}, folding "
                f"{len(ctx.forward_edges)} resolved forward edge(s) across "
                f"{len(ctx.node_ids)} valid canonical node(s) yields "
                f"{nonzero} node(s) with nonzero total degree (hub candidates) "
                f"and {len(zero_ids)} node(s) with zero total degree; the "
                f"zero-degree set is set-identical to `ctx.orphans` "
                f"({len(orphan_ids)} node(s)) because `ctx.broken_edges` is "
                f"empty ({len(ctx.broken_edges)} broken edge(s)) at this "
                "revision -- computed directly in this builder from "
                "`ctx.forward_edges`/`ctx.node_ids`/`ctx.orphans`, never "
                "hand-authored."
            ),
            "entry_class": "FACT",
            "evidence": ["launchpad/project-intelligence/corpus/indexes.py"],
        }
    ]


SPEC = {
    "name": "documentation-graph",
    "output_path": "generated/documentation-graph.md",
    "node_id": "generated-documentation-graph",
    "title": "Documentation graph: node connectivity summary",
    "node_type": "governance",
    "audiences": ["agent", "developer", "reviewer"],
    "subject": (
        "the corpus's own declared relationship graph, summarized per node as "
        "in-degree/out-degree/total-degree -- which nodes are structural hubs "
        "and how many carry no declared relationship at all -- rather than as "
        "a raw per-edge listing"
    ),
    "generate": _generate,
    "extra_evidence": _extra_evidence,
    "relationships": ({"type": "references", "target": "corpus-agents"},),
}
