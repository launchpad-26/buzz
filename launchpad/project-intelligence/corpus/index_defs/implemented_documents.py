"""Builder for launchpad/docs/corpus/specifications/implemented-documents.md --
issue #1304 (parent PRD #621, sibling family #1302-#1306).

Specification population: identical to #1302's `specifications_index.py`. A
canonical node is a candidate specification if and only if its
corpus-root-relative path (`ctx.rel_path(node)`) begins with the literal
prefix `specifications/`. Path, never front-matter `type` or prose judgement
-- a `specification` node's own `type` deliberately varies by subject
(`templates/specification.md` names `interfaces-events`, `architecture`, or
`implementation` as plausible picks), so `type` cannot be the selector here
either. #1303 (draft-documents.md) does not exist on this base to compare
against, so this builder follows #1302's own precedent directly rather than
guessing at a shared convention.

Interpreting "implemented"
---------------------------
`node.schema.json`'s `status` enum is exactly `['draft', 'active',
'deprecated', 'retired', 'flagged']` -- there is no `implemented` literal
anywhere in the schema, so "implemented" cannot be read off a node's own
front matter directly. Two candidate readings were considered:

(a) CHOSEN. "Implemented" means the specification's normative content has
    actually shipped in code, detected via the relationship graph:
    `relationships.schema.json` defines `implements` with directionality
    "source is the concrete realization of target, e.g. a template instance
    of a standard", and marks its inverse `implemented-by` as `generated`.
    `indexes.py`'s `build_context` already computes that inverse into
    `ctx.inverse_edges['implemented-by']` (target id -> sorted source ids)
    from every valid node's forward `relationships[]`. A specification node
    whose id appears as a key in that mapping with a non-empty source tuple
    has, by the schema's own stated directionality, at least one concrete
    realization elsewhere in the corpus declaring `implements` against it --
    which is exactly what "this specification has been implemented" means.
    This reading needs no new graph derivation; it reuses the framework's
    existing generated-inverse computation exactly as
    `index_defs/dependency_graph.py` (#896) already renders it for its own
    "derived inverse edges" section, just filtered to one inverse type and
    scoped to one path prefix.

(b) REJECTED. "Implemented" as a loose synonym for `status: active` (as
    opposed to `draft`). This is weaker and more inferential: nothing in
    `node.schema.json` or `relationships.schema.json` ties the word
    "implemented" to the `active` status value -- `active` only means "not
    draft, not deprecated, not retired, not flagged" as a lifecycle state,
    which says nothing about whether the specification's normative content
    has been realized anywhere in code. A node could be `status: active`
    (accepted as the current normative text) with zero implementations, or
    conceivably still `status: draft` while an early implementation already
    exists elsewhere in the corpus under a different relationship. Because
    (a) is directly grounded in the schema's own stated relationship
    semantics and (b) is not grounded in the schema's status semantics at
    all, (a) is the interpretation this builder implements. (b) is not
    rendered as a fallback or secondary listing -- see the module's
    `excludes` bullet below, which names the rejection explicitly rather
    than leaving it silently absent.

At the time this builder was written, `specifications/` holds no canonical
node at all (verified: the only file under that prefix is
`specifications/INDEX.md`, the sibling `specifications-index` builder's own
output, excluded from canonical inputs as every registered output path is).
The rule therefore matches zero nodes today. This is rendered as an honest
empty listing, per the Feature #621 brief and
`standards/generated-content.md`, rather than widened to look fuller --
mirroring #1302's own handling of the identical zero-match state on this
base.

node_type justification: identical to #1302's own reasoning.
`node.schema.json`'s type enum has no `specification` or `index` member;
`governance` is the closest true fit for this corpus-about-corpus
meta-document, the same choice `specifications_index.py`, `decisions_index.py`
and `dependency_graph.py` already make for their own per-subtree or
per-relationship-type index documents.
"""

_SPECIFICATIONS_PATH_PREFIX = "specifications/"
_IMPLEMENTED_BY = "implemented-by"


def _implemented_specification_nodes(ctx):
    """Valid nodes under specifications/ with a non-empty implemented-by
    inverse edge -- interpretation (a) above. Sorted by corpus-root-relative
    path, the same ordering #1302's specifications-index uses."""
    implemented_by = ctx.inverse_edges.get(_IMPLEMENTED_BY, {})
    return sorted(
        (
            n
            for n in ctx.valid_nodes
            if ctx.rel_path(n).startswith(_SPECIFICATIONS_PATH_PREFIX)
            and implemented_by.get(n.id)
        ),
        key=lambda n: ctx.rel_path(n),
    )


def _generate(ctx):
    implemented_by = ctx.inverse_edges.get(_IMPLEMENTED_BY, {})
    members = _implemented_specification_nodes(ctx)

    lines = [
        '## Interpreting "implemented"',
        "",
        "`node.schema.json`'s `status` enum is exactly `draft`, `active`, `deprecated`,",
        "`retired`, `flagged` -- it has no `implemented` value. This document reads",
        '"implemented" as: **a specification-shaped node (path under `specifications/`)',
        "whose id appears in the generated `implemented-by` inverse-edge view with at",
        "least one source** -- meaning some other canonical node declares a forward",
        "`implements` relationship targeting it. `relationships.schema.json` describes",
        "`implements` directionality as \"source is the concrete realization of target, "
        'e.g. a template instance of a standard,"',
        "so a non-empty `implemented-by` entry is read literally as \"this specification",
        'has a concrete realization elsewhere in the corpus."',
        "",
        "The rejected alternative was reading \"implemented\" as a loose synonym for",
        "`status: active` (as opposed to `draft`). That reading is weaker and purely",
        "inferential: nothing in `node.schema.json` or `relationships.schema.json` ties",
        "the word \"implemented\" to the `active` lifecycle value, which only means",
        '"not draft, not deprecated, not retired, not flagged" and says nothing about',
        "whether the specification's normative content has actually shipped in code.",
        "This document does not use `status` as its implemented signal.",
        "",
        "## Canonical corpus nodes under `specifications/` with a non-empty `implemented-by` edge",
        "",
    ]
    if members:
        lines += [
            "| Id | Path | Status | Implemented by (`implements` source ids) |",
            "|---|---|---|---|",
        ]
        for node in members:
            sources = ", ".join(f"`{s}`" for s in implemented_by.get(node.id, ()))
            lines.append(
                f"| `{node.id}` | `{ctx.rel_path(node)}` | "
                f"{node.data.get('status', '')} | {sources} |"
            )
    else:
        lines += [
            "No canonical corpus node currently has a corpus-root-relative path",
            "beginning `specifications/` with a non-empty `implemented-by` inverse edge.",
            "This listing is empty for two compounding reasons, both facts rather than",
            "omissions: as of this input digest no canonical node's path begins",
            "`specifications/` at all (the sibling `specifications-index` builder, #1302,",
            "renders that same empty state for the full subtree), and even once a",
            "specification node exists, it only appears here once some other canonical",
            "node declares a forward `implements` relationship targeting it.",
            "",
            "A node placed under `specifications/` is expected to follow",
            "`launchpad/docs/corpus/templates/specification.md`",
            "(`corpus-template-specification`): the normative definition of one",
            "protocol, algorithm, or wire/data format. A concrete realization of that",
            "specification elsewhere in the corpus should declare",
            "`relationships: [{type: implements, target: <the specification's id>}]`",
            "in its own front matter for that specification to appear in this listing.",
        ]

    return {
        "sections": "\n".join(lines),
        "includes": [
            "every canonical corpus node whose corpus-root-relative path (as "
            "`validate.py`'s discovery contract resolves it) begins with the literal "
            "prefix `specifications/` -- a path check, never a front-matter `type` "
            "check, matching #1302's `specifications-index` population rule",
            "restricted further to only those specification nodes whose id is a key "
            "with at least one source in `ctx.inverse_edges['implemented-by']` -- the "
            "generated inverse of the `implements` relationship type, computed by "
            "`indexes.py`'s `build_context` from every valid node's forward "
            "`relationships[]`, never hand-authored or re-derived by this builder",
        ],
        "excludes": [
            "any specification-path node with an empty or absent `implemented-by` "
            "entry -- a specification that exists but that nothing in the corpus "
            "yet declares `implements` against is not listed here as "
            '"implemented"',
            "nodes of any front-matter `type` outside the `specifications/` path "
            "prefix, even if some other node declares `implements` targeting them "
            "-- this document is scoped to specification-shaped nodes specifically, "
            "matching #1302's own prefix scoping",
            "the loose-synonym reading of `status: active` as \"implemented\" -- "
            "considered and explicitly rejected; see \"Interpreting "
            '\\"implemented\\"\" above',
            "the template `corpus-template-specification` itself "
            "(`templates/specification.md`), which prescribes the shape of a future "
            "specification node but is not itself a member of the "
            "`specifications/` prefix",
        ],
        "ordering": (
            "listing rows sorted lexicographically by corpus-root-relative path"
        ),
        "not_covered": [
            "The content, normative body, or maturity of any specification, or of "
            "any node that implements one -- each node under `specifications/` and "
            "each implementing node owns that itself.",
            "Partial or in-progress implementations -- the `implements` relationship "
            "is a boolean edge in the schema (a node either declares it or does "
            "not); this document cannot and does not report a completeness "
            "percentage.",
        ],
    }


def _extra_evidence(ctx):
    spec_count = sum(
        1
        for n in ctx.valid_nodes
        if ctx.rel_path(n).startswith(_SPECIFICATIONS_PATH_PREFIX)
    )
    implemented_count = len(_implemented_specification_nodes(ctx))
    return [
        {
            "statement": (
                f"At input digest sha256:{ctx.input_digest}, exactly {spec_count} "
                "canonical node(s) have a corpus-root-relative path beginning "
                f"`specifications/`, of which exactly {implemented_count} have a "
                "non-empty `implemented-by` inverse edge (interpretation (a) of "
                '"implemented", stated in this document\'s own "Interpreting '
                '\\"implemented\\"\" section); the listing contains exactly those '
                "nodes and no others."
            ),
            "entry_class": "FACT",
            "evidence": ["launchpad/project-intelligence/corpus/validate.py"],
        },
        {
            "statement": (
                "relationships.schema.json describes `implements` directionality as "
                '"source is the concrete realization of target, e.g. a template '
                'instance of a standard" and marks its inverse `implemented-by` as '
                "`generated`; `indexes.py`'s `build_context` computes that inverse "
                "from every valid node's forward `relationships[]` and exposes it as "
                "`ctx.inverse_edges['implemented-by']`, which this builder reads "
                "without any new graph derivation of its own."
            ),
            "entry_class": "FACT",
            "evidence": [
                "launchpad/docs/corpus/schema/relationships.schema.json",
                "launchpad/project-intelligence/corpus/indexes.py",
            ],
        },
    ]


SPEC = {
    "name": "implemented-documents",
    "output_path": "specifications/implemented-documents.md",
    "node_id": "specifications-implemented-documents",
    "title": "Implemented documents: generated listing of implemented specifications",
    "node_type": "governance",
    "audiences": ("agent", "developer", "reviewer"),
    "subject": (
        "canonical corpus nodes under the specifications/ prefix that have a "
        "non-empty implemented-by inverse edge -- i.e. specifications with at "
        "least one concrete implementation declared elsewhere in the corpus"
    ),
    "generate": _generate,
    "extra_evidence": _extra_evidence,
    "relationships": (
        {"type": "references", "target": "corpus-agents"},
        {"type": "implements", "target": "corpus-template-generated-index"},
        {"type": "references", "target": "corpus-template-specification"},
    ),
}
