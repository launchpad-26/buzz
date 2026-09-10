"""Builder: specifications/superseded-documents.md -- issue #1306 (parent PRD
#621, family #1302-#1306).

Inclusion rule (deterministic, schema-grounded, generated-inverse-edge based):
a canonical node under `specifications/` qualifies as "superseded" precisely
when it carries one or more incoming `superseded-by` edges -- i.e.
`ctx.inverse_edges['superseded-by']` holds a non-empty source list for that
node's id. `relationships.schema.json` marks the forward type `supersedes`'s
inverse as `superseded-by`, `inverse: generated`, so the framework itself
computes this once in `indexes.py`'s `build_context` (the same field #896's
`dependency_graph.py` already renders corpus-wide in its own "Derived inverse
edges" section). This builder reuses `ctx.inverse_edges['superseded-by']`
directly and never recomputes the derivation independently -- it is the
narrower, `specifications/`-scoped reading of that one signal, not a second
computation of it.

Scope: candidates are narrowed to the `specifications/` path prefix, following
#1302's own precedent (`specifications_index.py`) for selecting the
specifications subtree by path rather than front-matter `type` -- a
`specification` node's own `type` deliberately varies by subject
(`interfaces-events`, `architecture`, or `implementation`), so `type` cannot be
the selector here either.

`status: deprecated`/`retired` is a DIFFERENT signal and is never conflated
with "superseded" here. A specification can be superseded (some other node's
`supersedes` edge targets it) without ever being marked
`status: deprecated`/`retired`, and a node can carry `status: deprecated` or
`retired` for reasons unrelated to being formally superseded by another corpus
node (retirement can be a standalone editorial decision). Both directions of
mismatch between the two signals are therefore surfaced in an always-rendered
divergence subsection below, transparently, rather than one signal silently
overriding the other or being picked as the "real" one -- mirroring #890's and
#900's precedent (`configuration_index.py`, `layer_index.py`) of naming a
signal disagreement in a generated subsection instead of resolving it
silently.

At the time this builder was written, `specifications/` contains only
`specifications/INDEX.md` (#1302's own generated output, itself excluded from
canonical inputs before any builder runs) -- there is no other canonical node
under the prefix yet. Corpus-wide, zero nodes declare a `supersedes`
relationship and zero nodes carry `status: deprecated` or `status: retired`
(verified directly against the real front matter, not the template's
placeholder text). Both the main listing and the divergence subsection are
therefore honestly empty at this revision; this builder renders that
emptiness rather than widening either rule to look fuller. It activates
automatically the moment a `specifications/` node declares a `supersedes`
edge, or carries `status: deprecated`/`retired`, with no further generator
change required.

node_type justification: as with #1302's own `specifications-index.md`,
node.schema.json's type enum has no `specification` or `index` value; this is
a corpus-about-corpus meta-document (a derived view of the specifications
subtree, not a subject-domain document itself), so `governance` is the closest
true fit -- the same reasoning `specifications_index.py` (#1302) and
`dependency_graph.py` (#896) already apply to their own generated views.
"""

from __future__ import annotations

_PATH_PREFIX = "specifications/"
_INVERSE_TYPE = "superseded-by"
_FLAGGED_STATUSES = ("deprecated", "retired")


def _in_scope(ctx):
    return sorted(
        (n for n in ctx.valid_nodes if ctx.rel_path(n).startswith(_PATH_PREFIX)),
        key=ctx.rel_path,
    )


def _superseded_by(ctx):
    return ctx.inverse_edges.get(_INVERSE_TYPE, {})


def _generate(ctx):
    scoped = _in_scope(ctx)
    by_target = _superseded_by(ctx)

    superseded = sorted(
        (n for n in scoped if by_target.get(n.id)), key=ctx.rel_path
    )
    status_only = sorted(
        (
            n
            for n in scoped
            if n.data.get("status") in _FLAGGED_STATUSES and not by_target.get(n.id)
        ),
        key=ctx.rel_path,
    )
    edge_only = sorted(
        (n for n in superseded if n.data.get("status") not in _FLAGGED_STATUSES),
        key=ctx.rel_path,
    )

    lines = ["## Superseded specifications", ""]
    lines.append(
        "A `specifications/` node is listed here precisely when it carries one "
        "or more incoming `superseded-by` edges -- the framework's own "
        "generated inverse of another node's `supersedes` relationship "
        "(`ctx.inverse_edges['superseded-by']`), reused directly and never "
        "recomputed by this builder."
    )
    lines.append("")
    if superseded:
        lines += ["| Id | Path | Status | Superseded by |", "|---|---|---|---|"]
        for node in superseded:
            sources = ", ".join(by_target.get(node.id, ()))
            status = node.data.get("status", "")
            lines.append(
                f"| `{node.id}` | `{ctx.rel_path(node)}` | {status} | {sources} |"
            )
    else:
        lines += [
            "No canonical node under `specifications/` currently carries an "
            "incoming `superseded-by` edge. This listing is empty because "
            "`specifications/` holds no non-generated canonical node yet "
            "(`specifications/INDEX.md`, #1302's own generated output, is "
            "excluded from canonical inputs before this builder runs) -- an "
            "empty fact, not an omission. It populates automatically once a "
            "specification node under the prefix declares a `supersedes` "
            "edge targeting another specification node.",
        ]
    lines.append("")
    lines.append(
        "### Signal divergence: `superseded-by` vs. `status: deprecated`/`retired`"
    )
    lines.append("")
    lines.append(
        "These are two different signals and are never conflated: a node can "
        "be superseded without being marked deprecated/retired, or carry "
        "`status: deprecated`/`retired` without any incoming `supersedes` "
        "edge. Both directions of mismatch are surfaced here rather than one "
        "signal silently overriding the other."
    )
    lines.append("")
    lines.append(
        f"**`status` is deprecated/retired, no `{_INVERSE_TYPE}` edge exists:**"
    )
    lines.append("")
    if status_only:
        lines += ["| Id | Path | Status |", "|---|---|---|"]
        for node in status_only:
            lines.append(
                f"| `{node.id}` | `{ctx.rel_path(node)}` | "
                f"{node.data.get('status', '')} |"
            )
    else:
        lines.append("None at this revision.")
    lines.append("")
    lines.append(
        f"**`{_INVERSE_TYPE}` edge exists, `status` is not deprecated/retired:**"
    )
    lines.append("")
    if edge_only:
        lines += [
            "| Id | Path | Status | Superseded by |",
            "|---|---|---|---|",
        ]
        for node in edge_only:
            sources = ", ".join(by_target.get(node.id, ()))
            lines.append(
                f"| `{node.id}` | `{ctx.rel_path(node)}` | "
                f"{node.data.get('status', '')} | {sources} |"
            )
    else:
        lines.append("None at this revision.")

    return {
        "sections": "\n".join(lines),
        "includes": [
            "every valid canonical corpus node whose corpus-root-relative "
            "path begins with the literal prefix `specifications/` AND has "
            "one or more incoming `superseded-by` edges, i.e. "
            "`ctx.inverse_edges['superseded-by']` carries a non-empty source "
            "list for that node's id -- reusing the framework's own "
            "generated inverse-edge derivation (#896's `build_context`), "
            "never recomputed independently",
        ],
        "excludes": [
            "nodes selected by `status: deprecated`/`retired` alone -- that "
            "is a different, non-conflated signal; a node in that state with "
            "no incoming `superseded-by` edge is surfaced only in the "
            "divergence subsection, not the main listing",
            "nodes outside the `specifications/` path prefix, even if they "
            "carry an incoming `superseded-by` edge -- this document is "
            "scoped to the specifications subtree; "
            "`generated/dependency-graph.md` (#896) already renders every "
            "`superseded-by` edge corpus-wide",
            "the other three generated-inverse relationship types "
            "(`depended-on-by`, `implemented-by`, `has-part`) and the "
            "authored `referenced-by` inverse -- only `superseded-by` is "
            "this document's subject",
        ],
        "ordering": (
            "the main listing and both divergence subsections are each "
            "sorted lexicographically by corpus-root-relative path"
        ),
        "not_covered": [
            "Whether a `supersedes` relationship or a "
            "`deprecated`/`retired` status is itself correct or current -- "
            "this document only reports the two signals as the corpus "
            "currently declares them.",
        ],
    }


def _extra_evidence(ctx):
    scoped = _in_scope(ctx)
    by_target = _superseded_by(ctx)
    superseded_count = sum(1 for n in scoped if by_target.get(n.id))
    flagged_count = sum(
        1 for n in scoped if n.data.get("status") in _FLAGGED_STATUSES
    )
    return [
        {
            "statement": (
                f"At input digest sha256:{ctx.input_digest}, {len(scoped)} "
                "canonical node(s) have a corpus-root-relative path "
                f"beginning `specifications/`, of which {superseded_count} "
                "carry one or more incoming `superseded-by` edges "
                "(ctx.inverse_edges['superseded-by']) and "
                f"{flagged_count} carry `status: deprecated` or "
                "`status: retired`; the listing and divergence subsections "
                "contain exactly those nodes and no others."
            ),
            "entry_class": "FACT",
            "evidence": ["launchpad/project-intelligence/corpus/indexes.py"],
        }
    ]


SPEC = {
    "name": "superseded-documents",
    "output_path": "specifications/superseded-documents.md",
    "node_id": "specifications-superseded-documents",
    "title": "Superseded specifications: generated listing",
    "node_type": "governance",
    "audiences": ("agent", "developer", "reviewer"),
    "subject": (
        "canonical corpus nodes under the specifications/ prefix that carry "
        "one or more incoming superseded-by edges"
    ),
    "generate": _generate,
    "extra_evidence": _extra_evidence,
    "relationships": (
        {"type": "references", "target": "corpus-agents"},
        {"type": "implements", "target": "corpus-template-generated-index"},
        {"type": "references", "target": "corpus-template-specification"},
    ),
}
