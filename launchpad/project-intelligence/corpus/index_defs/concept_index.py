"""Builder for launchpad/docs/corpus/generated/concept-index.md -- issue #889
(parent PRD #621).

Emits the concept index: a generated index of every canonical concept node. The
inclusion rule is deterministic and schema-grounded, never prose judgement: a
valid canonical node qualifies if and only if it declares a forward
``implements`` relationship targeting ``corpus-template-concept`` -- the id of
``templates/concept.md``. The rule is read from the framework's generated
``implemented-by`` inverse edges, so it cannot drift from what
relationships.schema.json and validate.py enforce.

Honesty note on the rule's grounding: unlike ``templates/glossary-term.md``
(which spells out the edges an instance should declare), ``templates/concept.md``
does not itself prescribe this edge. The rule rests on
relationships.schema.json's ``implements`` directionality -- "source is the
concrete realization of target (e.g. a template instance of a standard)" -- and
on the template-instance convention the corpus's merged builders already apply
(glossary.py matches implements -> corpus-template-glossary-term; every
registered index builder declares implements -> corpus-template-generated-index).

If the rule matches zero nodes -- true at the time this builder was written,
since no concept instance exists yet -- the index renders an honest empty
listing and says so, rather than widening the rule to look fuller.

``node_type`` is ``governance``: node.schema.json's type enum has no concept or
index value, and a concept instance may take any subject type from the enum, so
no single subject type fits the index of them all. ``governance`` follows the
precedent every corpus meta-document (README.md, standards/*.md, the templates,
and the generated-index template itself) already records for the same choice.
"""

_TEMPLATE_ID = "corpus-template-concept"


def _qualifying(ctx):
    """Sorted (node id, node) pairs for every valid canonical node declaring
    implements -> corpus-template-concept, via the framework's generated
    implemented-by inverse edges."""
    sources = ctx.inverse_edges.get("implemented-by", {}).get(_TEMPLATE_ID, ())
    by_id = {n.id: n for n in ctx.valid_nodes if isinstance(n.id, str)}
    return [(node_id, by_id[node_id]) for node_id in sources if node_id in by_id]


def _generate(ctx):
    entries = _qualifying(ctx)
    lines = ["## Concept nodes", ""]
    if entries:
        lines += ["| Concept node id | Path | Type | Status |", "|---|---|---|---|"]
        for node_id, node in entries:
            data = node.data
            lines.append(
                f"| {node_id} | `{ctx.rel_path(node)}` "
                f"| {data.get('type', '')} | {data.get('status', '')} |"
            )
    else:
        lines += [
            "No canonical corpus node currently declares a forward `implements`",
            f"relationship targeting `{_TEMPLATE_ID}`, so the concept index is",
            "empty at this revision. This is the honest state, not a generator",
            "gap: no concept instance has been written yet. The first concept",
            "node that declares that edge will appear here on the next",
            "regeneration.",
        ]
    return {
        "sections": "\n".join(lines),
        "includes": [
            "every valid canonical corpus node that declares a forward "
            f"`implements` relationship targeting `{_TEMPLATE_ID}` -- the id "
            "of `templates/concept.md`; matched via the validator-derived "
            "`implemented-by` inverse edges, never by prose judgement",
        ],
        "excludes": [
            f"`templates/concept.md` itself ({_TEMPLATE_ID}): it is the "
            "template a concept implements, not a concept",
            "nodes that merely explain, discuss or resemble a concept in "
            "prose without declaring the `implements` edge -- keyword, path "
            "or type matching would be prose judgement, not a schema-grounded "
            "rule (node.schema.json's type enum has no `concept` value to "
            "match on)",
            "nodes whose front matter fails validation: only valid nodes "
            "contribute edges to the derived graph",
        ],
        "ordering": "listing rows sorted by qualifying node id (ascending)",
        "not_covered": [
            "The substance of any concept -- each concept node owns its own "
            "explanation; this document only locates them.",
        ],
        "unverified": [
            "The inclusion rule has never matched a real corpus node: no "
            "concept instance existed when this builder was written, so the "
            "populated-listing shape is exercised only by this builder's own "
            "test fixtures until the first real concept node merges.",
            "templates/concept.md does not itself prescribe the `implements` "
            "edge this rule matches on; the rule follows the corpus-wide "
            "template-instance convention (relationships.schema.json's "
            "`implements` directionality) rather than an instruction in the "
            "template's own text.",
        ],
    }


def _extra_evidence(ctx):
    count = len(_qualifying(ctx))
    return [
        {
            "statement": (
                f"At input digest sha256:{ctx.input_digest}, exactly {count} "
                "canonical corpus node(s) declare a forward implements "
                f"relationship targeting {_TEMPLATE_ID}; the concept index "
                "lists exactly those nodes."
            ),
            "entry_class": "FACT",
            "evidence": [
                "launchpad/project-intelligence/corpus/index_defs/concept_index.py",
                "launchpad/docs/corpus/templates/concept.md",
            ],
        }
    ]


SPEC = {
    "name": "concept-index",
    "output_path": "generated/concept-index.md",
    "node_id": "generated-concept-index",
    "title": "Corpus concept index: generated index",
    "node_type": "governance",
    "audiences": ["agent", "developer", "reviewer"],
    "subject": (
        "the canonical concept nodes (implements -> corpus-template-concept) "
        "in this corpus"
    ),
    "generate": _generate,
    "extra_evidence": _extra_evidence,
    "relationships": (
        {"type": "implements", "target": "corpus-template-generated-index"},
        {"type": "references", "target": _TEMPLATE_ID},
        {"type": "references", "target": "corpus-agents"},
    ),
}
