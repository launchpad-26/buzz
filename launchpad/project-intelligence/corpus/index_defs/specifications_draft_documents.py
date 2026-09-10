"""Builder for launchpad/docs/corpus/specifications/draft-documents.md -- issue
#1303.

Inclusion rule (deterministic, path- and status-grounded): a canonical node is
listed if and only if BOTH:

1. its corpus-root-relative path (`ctx.rel_path(node)`) begins with the
   literal prefix `specifications/` -- the same path-membership axis
   `index_defs/specifications_index.py` (#1302) already uses for this
   subtree, chosen here for family consistency rather than re-deriving a
   second, competing notion of "in the specifications subtree"; and
2. its front-matter `status` field is the literal string `"draft"` --
   `node.schema.json`'s `status` enum is exactly `["draft", "active",
   "deprecated", "retired", "flagged"]` (verified directly against the
   schema file), so this is a plain equality check against one enum member,
   never a prose judgement about a document's maturity.

This task's own brief poses a second candidate axis -- every node declaring
`{"type": "implements", "target": "corpus-template-specification"}` -- as an
alternative or addition to the path-prefix rule. Both axes are checked
directly against this worktree's corpus tree rather than assumed: grepping
every relationship block under `launchpad/docs/corpus` finds zero nodes of
any kind declaring an `implements` edge to `corpus-template-specification`,
and `specifications/` on disk contains only `specifications/INDEX.md`, which
is `index_defs/specifications_index.py`'s own registered output path and is
therefore excluded from every builder's canonical inputs by the framework
(`canonical_input_paths`/`build_context` in indexes.py) -- it can never
appear in `ctx.valid_nodes` regardless of which axis is chosen. The two axes
therefore agree today: both match zero canonical nodes. Given that agreement,
this builder follows #1302's own path-prefix choice rather than the
relationship-based alternative, for the same reason #1302 gives implicitly by
being the established precedent for this subtree -- path membership is what
every sibling in this five-task family (#1302-#1306) is built against, and
introducing a second, relationship-based inclusion axis for one sibling alone
would fragment the family's inclusion model without any observed case where
the two axes actually diverge. If a future specification document is ever
authored that satisfies one axis but not the other, that divergence is new
information this builder does not have today and does not anticipate; #1303's
own OPEN note in its plan says so explicitly.

At the time this builder was written, the rule matches zero canonical nodes
(verified: no path under the corpus root begins `specifications/` other than
the registered-output `INDEX.md`, and even if it were counted, its own
generated status is always the framework-hardcoded `"draft"` literal, not an
authored claim about a hand-written specification's maturity -- moot here
since it is excluded from canonical inputs regardless). This is a sibling of
#1302 (specifications/INDEX.md), #1304 (implemented-documents.md), #1305
(normative-documents.md) and #1306 (superseded-documents.md), with no
ordering dependency between them. The builder renders that emptiness
honestly, per the Feature #621 brief and standards/generated-content.md,
rather than widening the rule to look fuller -- mirroring the same zero-match
handling `index_defs/api_index.py` (#886), `index_defs/concept_index.py`
(#889) and `index_defs/specifications_index.py` (#1302) already use on this
base. Because the listing is honestly empty today, the empty-state message
also names `launchpad/docs/corpus/templates/specification.md` (id
`corpus-template-specification`) so a reader learns what a draft
specification node is expected to look like instead of finding a bare
"nothing here".

node_type justification: node.schema.json's type enum has no `specification`
or `index` member. `governance` is the closest true fit for this
corpus-about-corpus meta-document -- the same reasoning
`index_defs/specifications_index.py` (#1302) and `index_defs/decisions_index.py`
(#845) apply to their own per-subtree indexes, and the precedent nodes for
corpus-about-corpus documents (corpus README, standards,
`templates/generated-index.md`, `templates/specification.md` itself) all
carry `type: governance`.
"""

_SPECIFICATIONS_PATH_PREFIX = "specifications/"
_DRAFT_STATUS = "draft"


def _is_member(ctx, node) -> bool:
    return ctx.rel_path(node).startswith(
        _SPECIFICATIONS_PATH_PREFIX
    ) and node.data.get("status") == _DRAFT_STATUS


def _generate(ctx):
    members = sorted(
        (n for n in ctx.valid_nodes if _is_member(ctx, n)),
        key=lambda n: ctx.rel_path(n),
    )

    lines = [
        "## Draft specification nodes under `specifications/`",
        "",
    ]
    if members:
        lines += ["| Id | Path | Status | Audiences |", "|---|---|---|---|"]
        for node in members:
            audiences = ", ".join(node.data.get("audiences") or [])
            lines.append(
                f"| `{node.id}` | `{ctx.rel_path(node)}` | "
                f"{node.data.get('status', '')} | {audiences} |"
            )
    else:
        lines += [
            "No canonical corpus node currently has both a corpus-root-relative",
            "path beginning `specifications/` and a front-matter `status` of",
            "literally `draft`. This listing is empty because the corpus holds no",
            "draft specification documents yet -- an empty fact, not an omission.",
            "It populates automatically as specification documents are authored",
            "under that prefix with `status: draft` (see the sibling task family",
            "#1302-#1306).",
            "",
            "A node placed under `specifications/` is expected to follow",
            "`launchpad/docs/corpus/templates/specification.md`",
            "(`corpus-template-specification`): the normative definition of one",
            "protocol, algorithm, or wire/data format, with a purpose and boundary",
            "statement, motivation, definitions, a BCP 14 normative-language",
            "declaration when it uses MUST/SHOULD/MAY, the normative body itself,",
            "versioning and compatibility, a required Security Considerations",
            "section, relationships, and scope and omissions. Its front-matter",
            "`status` starts `draft` (per `node.schema.json`'s status enum) until",
            "a reviewer advances it.",
        ]

    return {
        "sections": "\n".join(lines),
        "includes": [
            "every canonical corpus node whose corpus-root-relative path "
            "(as `validate.py`'s discovery contract resolves it) begins with the "
            "literal prefix `specifications/` AND whose front-matter `status` "
            "field is literally `draft` -- both a path check and an exact status "
            "equality check, never a front-matter `type` check or a prose "
            "judgement about maturity"
        ],
        "excludes": [
            "nodes under `specifications/` whose `status` is `active`, "
            "`deprecated`, `retired`, or `flagged` -- only literal `draft` "
            "qualifies",
            "nodes with `status: draft` that live outside the `specifications/` "
            "path prefix -- path membership is required in addition to status",
            "the template `corpus-template-specification` itself "
            "(`templates/specification.md`), which prescribes the shape of a "
            "future specification node but is not itself a member of the "
            "`specifications/` prefix",
            "every registered generated output path, including this "
            "document's own sibling `specifications/INDEX.md`, so no generated "
            "view feeds itself or is mistaken for an authored draft",
        ],
        "ordering": (
            "listing rows sorted lexicographically by corpus-root-relative path"
        ),
        "not_covered": [
            "The content, normative body, or maturity progression of any "
            "specification -- each specification node under `specifications/` "
            "owns that itself, once one exists.",
            "Non-`draft` specification lifecycle states such as `active` or "
            "`deprecated` -- those are the sibling tasks' concern (#1304-#1306), "
            "not this document's.",
        ],
    }


def _extra_evidence(ctx):
    count = sum(1 for n in ctx.valid_nodes if _is_member(ctx, n))
    return [
        {
            "statement": (
                f"At input digest sha256:{ctx.input_digest}, exactly {count} "
                "canonical node(s) have both a corpus-root-relative path "
                "beginning `specifications/` and a front-matter `status` of "
                "literally `draft`; the listing contains exactly those nodes "
                "and no others."
            ),
            "entry_class": "FACT",
            "evidence": ["launchpad/project-intelligence/corpus/validate.py"],
        },
        {
            "statement": (
                "node.schema.json's `status` property enum is exactly "
                '["draft", "active", "deprecated", "retired", "flagged"]; this '
                "builder's status filter compares against the literal string "
                "\"draft\", one member of that enum."
            ),
            "entry_class": "FACT",
            "evidence": ["launchpad/docs/corpus/schema/node.schema.json"],
        },
    ]


SPEC = {
    "name": "specifications-draft-documents",
    "output_path": "specifications/draft-documents.md",
    "node_id": "specifications-draft-documents",
    "title": (
        "Draft specification documents: generated listing of draft-status "
        "specification nodes"
    ),
    "node_type": "governance",
    "audiences": ("agent", "developer", "reviewer"),
    "subject": (
        "canonical corpus nodes under the specifications/ path prefix whose "
        "front-matter status is literally draft"
    ),
    "generate": _generate,
    "extra_evidence": _extra_evidence,
    "relationships": (
        {"type": "references", "target": "corpus-agents"},
        {"type": "implements", "target": "corpus-template-generated-index"},
        {"type": "references", "target": "corpus-template-specification"},
    ),
}
