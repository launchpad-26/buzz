"""Builder for launchpad/docs/corpus/GLOSSARY.md -- issue #637 (parent PRD #621).

Emits the corpus glossary: a generated index of every canonical glossary-term
node. The inclusion rule is deterministic and schema-grounded, never prose
judgement: a valid canonical node qualifies if and only if it declares a
forward ``implements`` relationship targeting ``corpus-template-glossary-term``
-- the exact edge templates/glossary-term.md ("Relationships an instance node
should consider") tells a real glossary-term instance to declare. The rule is
read from the framework's generated ``implemented-by`` inverse edges, so it
cannot drift from what relationships.schema.json and validate.py enforce.

If the rule matches zero nodes -- true at the time this builder was written,
since no glossary-term instance exists yet -- the glossary renders an honest
empty listing and says so, rather than widening the rule to look fuller.

``node_type`` is ``governance``: node.schema.json's type enum has no glossary
or index value, and the glossary indexes terms whose subjects may span all
thirteen surfaces, so no single subject type fits. ``governance`` follows the
precedent every corpus meta-document (README.md, standards/*.md, the templates,
and the generated-index template itself) already records for the same choice.
"""

_TEMPLATE_ID = "corpus-template-glossary-term"


def _qualifying(ctx):
    """Sorted (node id, node) pairs for every valid canonical node declaring
    implements -> corpus-template-glossary-term, via the framework's generated
    implemented-by inverse edges."""
    sources = ctx.inverse_edges.get("implemented-by", {}).get(_TEMPLATE_ID, ())
    by_id = {n.id: n for n in ctx.valid_nodes if isinstance(n.id, str)}
    return [(node_id, by_id[node_id]) for node_id in sources if node_id in by_id]


def _generate(ctx):
    entries = _qualifying(ctx)
    lines = ["## Glossary terms", ""]
    if entries:
        lines += ["| Term node id | Path | Type | Status |", "|---|---|---|---|"]
        for node_id, node in entries:
            data = node.data
            lines.append(
                f"| {node_id} | `{ctx.rel_path(node)}` "
                f"| {data.get('type', '')} | {data.get('status', '')} |"
            )
    else:
        lines += [
            "No canonical corpus node currently declares a forward `implements`",
            f"relationship targeting `{_TEMPLATE_ID}`, so the glossary is empty",
            "at this revision. This is the honest state, not a generator gap:",
            "no glossary-term instance has been written yet. The first term node",
            "that declares that edge will appear here on the next regeneration.",
        ]
    return {
        "sections": "\n".join(lines),
        "includes": [
            "every valid canonical corpus node that declares a forward "
            f"`implements` relationship targeting `{_TEMPLATE_ID}` -- the edge "
            "`templates/glossary-term.md` tells a glossary-term instance to "
            "declare; matched via the validator-derived `implemented-by` "
            "inverse edges, never by prose judgement",
        ],
        "excludes": [
            f"`templates/glossary-term.md` itself ({_TEMPLATE_ID}): it is the "
            "template a term implements, not a term",
            "nodes that merely mention, define or discuss a term in prose "
            "without declaring the `implements` edge -- keyword or path "
            "matching would be prose judgement, not a schema-grounded rule",
            "nodes whose front matter fails validation: only valid nodes "
            "contribute edges to the derived graph",
        ],
        "ordering": "listing rows sorted by qualifying node id (ascending)",
        "not_covered": [
            "The meaning of any term -- each glossary-term node owns its own "
            "definition; this document only locates them.",
        ],
        "unverified": [
            "The inclusion rule has never matched a real corpus node: no "
            "glossary-term instance existed when this builder was written, so "
            "the populated-listing shape is exercised only by this builder's "
            "own test fixtures until the first real term node merges.",
        ],
    }


def _extra_evidence(ctx):
    count = len(_qualifying(ctx))
    return [
        {
            "statement": (
                f"At input digest sha256:{ctx.input_digest}, exactly {count} "
                "canonical corpus node(s) declare a forward implements "
                f"relationship targeting {_TEMPLATE_ID}; the glossary lists "
                "exactly those nodes."
            ),
            "entry_class": "FACT",
            "evidence": [
                "launchpad/project-intelligence/corpus/index_defs/glossary.py",
                "launchpad/docs/corpus/templates/glossary-term.md",
            ],
        }
    ]


SPEC = {
    "name": "glossary",
    "output_path": "GLOSSARY.md",
    "node_id": "corpus-glossary",
    "title": "Corpus glossary: generated index",
    "node_type": "governance",
    "audiences": ["agent", "developer", "reviewer"],
    "subject": (
        "the canonical glossary-term nodes (implements -> "
        "corpus-template-glossary-term) in this corpus"
    ),
    "generate": _generate,
    "extra_evidence": _extra_evidence,
    "relationships": (
        {"type": "implements", "target": "corpus-template-generated-index"},
        {"type": "references", "target": _TEMPLATE_ID},
        {"type": "references", "target": "corpus-agents"},
    ),
}
