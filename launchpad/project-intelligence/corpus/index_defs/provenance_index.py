"""Builder: generated/provenance-index.md -- issue #903 (parent PRD #621).

A generated **stats/coverage view** over every canonical corpus node's own
evidence ledger: per node, its `entry_class` distribution (counts of `FACT`,
`INFERENCE`, `TEAM_KNOWLEDGE`), corpus-wide totals across every node, and a
visible "zero-evidence nodes" section.

**Distinction from #892's ``coverage.md`` and #634's ``coverage.py``.** Those
answer "does some canonical node account for each in-scope *repository source
item*" (a Rust crate, an event kind, a migration, ...) -- a source-inventory
disposition. This document answers a different question entirely: for each
*canonical corpus node that already exists*, what does its own evidence ledger
look like -- how many `FACT` / `INFERENCE` / `TEAM_KNOWLEDGE` entries does it
carry. Neither reads the other's input (this builder never touches
`inventory.py` or `coverage.py`) and neither restates the other's content; the
rendered body states this distinction explicitly (required section, below) so
a reader lands on the right document.

**Why the zero-evidence section is expected to render empty.**
`node.schema.json`'s `evidence` property is `required` with `minItems: 1`
(`launchpad/docs/corpus/schema/node.schema.json`, read directly), and
`validate.py` runs that schema over every discovered node: a node whose front
matter fails it gets `node.error` set and is excluded from `ctx.valid_nodes`
(read directly in `validate.py`, `load_nodes` / the `node.error` checks in
`find_broken_relationships` and the evidence-entry validators). So a node
present in `ctx.valid_nodes` can never carry an empty `evidence` array -- this
section is a standing tripwire, not a hedge: it names the invariant instead of
silently assuming it, and if it ever renders non-empty that is a hard schema
regression, not a normal corpus state.

``node_type`` choice: ``governance``, following ``decision_index.py``'s (#895)
and ``coverage.py``'s (#892) own identical reasoning -- node.schema.json's
type enum has no ``provenance``/``evidence``/``index`` member, and this
document's subject (the corpus's own evidence-ledger bookkeeping) is a
governance concern about the corpus itself, not a product surface.

Contract: module-level ``SPEC`` per indexes.py's IndexSpec; the framework
renders all front matter and the templates/generated-index.md body skeleton.
This module supplies only the subject-specific listing and the
inclusion/exclusion bullets. No ``extra_evidence`` is needed: every number
this builder renders derives from ``ctx.valid_nodes[*].data['evidence']``,
already inside ``ctx.input_digest`` (unlike ``decision_index.py``'s
digest-uncovered ``launchpad/decisions/`` read), and the framework's own two
standard evidence entries (generator + builder module) already cover "how
this table was produced."
"""

from __future__ import annotations

_ENTRY_CLASSES = ("FACT", "INFERENCE", "TEAM_KNOWLEDGE")


def _cell(text: str) -> str:
    return text.replace("|", "\\|")


def _node_counts(node) -> dict[str, int]:
    """entry_class -> count for one node's evidence array. Unknown/malformed
    entries (never expected on a schema-valid node, but never trusted blindly
    either) are simply not counted under any of the three known classes."""
    counts = {cls: 0 for cls in _ENTRY_CLASSES}
    for entry in node.data.get("evidence") or []:
        if not isinstance(entry, dict):
            continue
        cls = entry.get("entry_class")
        if cls in counts:
            counts[cls] += 1
    return counts


def _generate(ctx):
    nodes = sorted(ctx.valid_nodes, key=lambda n: str(n.id))

    per_node = []  # (node, path, counts, total)
    zero_evidence = []  # (node, path)
    totals = {cls: 0 for cls in _ENTRY_CLASSES}
    grand_total = 0

    for node in nodes:
        counts = _node_counts(node)
        total = sum(counts.values())
        path = ctx.rel_path(node)
        per_node.append((node, path, counts, total))
        for cls in _ENTRY_CLASSES:
            totals[cls] += counts[cls]
        grand_total += total
        if not (node.data.get("evidence") or []):
            zero_evidence.append((node, path))

    parts = [
        "## Distinction from `coverage.md` and `coverage.py`",
        "",
        "This document is a **stats/coverage view over evidence citation "
        "classification**: for each canonical corpus node that already "
        "exists, how many `FACT`, `INFERENCE` and `TEAM_KNOWLEDGE` entries "
        "its own evidence ledger carries. It is a different document from "
        "`generated/coverage.md` (issue #892) and `coverage.py` (issue "
        "#634), which answer a different question -- whether each in-scope "
        "*repository source item* (a Rust crate, an event kind, a "
        "migration, ...) is accounted for by some canonical node, a "
        "source-inventory disposition. **Read `coverage.md` to find "
        "whether a repository source item is documented; read this "
        "document for the evidence-class mix a node's own citations "
        "carry.** Neither document reads the other's input and neither "
        "restates the other's content.",
        "",
        "## Per-node evidence distribution",
        "",
        f"**{len(nodes)} canonical corpus node(s)** carry a schema-valid "
        "evidence ledger at generation time.",
        "",
    ]
    if per_node:
        parts.append("| Node id | Path | FACT | INFERENCE | TEAM_KNOWLEDGE | Total |")
        parts.append("|---|---|---|---|---|---|")
        for node, path, counts, total in per_node:
            parts.append(
                "| "
                + " | ".join(
                    (
                        _cell(str(node.id)),
                        f"`{_cell(path)}`",
                        str(counts["FACT"]),
                        str(counts["INFERENCE"]),
                        str(counts["TEAM_KNOWLEDGE"]),
                        str(total),
                    )
                )
                + " |"
            )
    else:
        parts.append(
            "None -- no schema-valid canonical corpus node was discovered "
            "at this revision."
        )

    parts += [
        "",
        "## Corpus-wide totals",
        "",
        f"Across all {len(nodes)} node(s): **{grand_total}** total evidence "
        "entries.",
        "",
        "| Entry class | Count |",
        "|---|---|",
    ]
    for cls in _ENTRY_CLASSES:
        parts.append(f"| {cls} | {totals[cls]} |")

    parts += [
        "",
        "## Zero-evidence nodes",
        "",
        "`node.schema.json`'s `evidence` property is `required` with "
        "`minItems: 1`, and `validate.py` rejects any node whose front "
        "matter fails that schema -- such a node never reaches "
        "`ctx.valid_nodes`. This section is therefore **expected to be "
        "empty**; it states that explicitly rather than silently assuming "
        "it, and its non-emptiness would itself be a hard schema-"
        "enforcement regression, not a normal corpus state.",
        "",
    ]
    if zero_evidence:
        parts.append(
            f"{len(zero_evidence)} node(s) carry an empty or missing "
            "`evidence` array despite passing schema validation -- this is "
            "unexpected and names a validator gap:"
        )
        parts.append("")
        parts.append("| Node id | Path |")
        parts.append("|---|---|")
        for node, path in zero_evidence:
            parts.append(f"| {_cell(str(node.id))} | `{_cell(path)}` |")
    else:
        parts.append(
            "None -- every schema-valid canonical corpus node at this "
            "revision carries at least one evidence entry, as "
            "`node.schema.json`'s `minItems: 1` requires."
        )

    return {
        "sections": "\n".join(parts),
        "includes": (
            "every canonical corpus node in `ctx.valid_nodes` (schema-valid "
            "front matter; a node that failed schema validation is already "
            "excluded here and reported separately by `validate.py` "
            "itself), one row in the per-node table keyed by its own "
            "front-matter `id`",
            "each node's evidence entries, counted per `entry_class` value "
            "(`FACT`, `INFERENCE`, `TEAM_KNOWLEDGE`) exactly as "
            "`node.schema.json`'s `evidenceEntry.entry_class` enum defines "
            "them",
            "a corpus-wide total for each entry class and a grand total, "
            "summed across every listed node",
            "a zero-evidence-nodes section, always rendered (never omitted "
            "when empty), naming the schema invariant that makes an empty "
            "result the expected one",
        ),
        "excludes": (
            "any node excluded from `ctx.valid_nodes` (schema-invalid front "
            "matter): `validate.py`'s own run already reports those as hard "
            "errors; this document counts only nodes that passed",
            "whether an evidence entry's citation actually supports its "
            "statement -- AGENTS.md is explicit that checking is "
            "structural only, so this document counts classification "
            "labels, never citation quality or content",
            "which specific citations a node's evidence entries point to -- "
            "the per-node table counts by class, it does not list "
            "individual citation strings",
        ),
        "ordering": (
            "the per-node table is sorted by node id; entry-class columns "
            "are in the fixed order FACT, INFERENCE, TEAM_KNOWLEDGE "
            "throughout; the zero-evidence table (when non-empty) is "
            "sorted by node id"
        ),
        "not_covered": (
            "Whether a repository source item is documented at all -- "
            "`generated/coverage.md` (issue #892) and `coverage.py` (issue "
            "#634) own that source-inventory disposition, not this "
            "document.",
            "Whether any individual evidence entry's citation supports its "
            "statement -- AGENTS.md's own rule that checking is structural "
            "only applies; this document never audits citation content.",
        ),
        "unverified": (),
    }


SPEC = {
    "name": "provenance-index",
    "output_path": "generated/provenance-index.md",
    "node_id": "generated-provenance-index",
    "title": "Provenance index: generated evidence-class distribution",
    "node_type": "governance",
    "audiences": ("agent", "developer", "reviewer"),
    "subject": (
        "the entry_class distribution (FACT/INFERENCE/TEAM_KNOWLEDGE) of "
        "every canonical corpus node's own evidence ledger, plus "
        "corpus-wide totals and a zero-evidence-nodes tripwire -- distinct "
        "from generated/coverage.md's source-inventory disposition"
    ),
    "generate": _generate,
    "relationships": (
        {"type": "implements", "target": "corpus-template-generated-index"},
        {"type": "references", "target": "corpus-agents"},
    ),
}
