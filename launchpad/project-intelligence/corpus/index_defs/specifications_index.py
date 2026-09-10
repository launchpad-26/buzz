"""Builder for launchpad/docs/corpus/specifications/INDEX.md -- issue #1302.

Inclusion rule (deterministic, path-grounded): a canonical node is listed if
and only if its corpus-root-relative path (`ctx.rel_path(node)`) begins with
the literal prefix `specifications/`. Membership is decided by path alone,
never by front-matter `type`, prose judgement, or title matching -- a
`specification` node's own `type` deliberately varies by subject
(`templates/specification.md` names `interfaces-events`, `architecture`, or
`implementation` as plausible picks depending on what is being specified), so
`type` cannot be the selector the way it is for `index_defs/api_index.py`'s
`interfaces-events`-only rule.

At the time this builder was written, `launchpad/docs/corpus/specifications/`
does not exist as a directory on the merge base and the rule matches zero
canonical nodes (verified: no path under the corpus root begins
`specifications/`). This is the first of a five-task family (#1302-#1306)
covering that subtree; #1303 (draft-documents.md), #1304
(implemented-documents.md), #1305 (normative-documents.md) and #1306
(superseded-documents.md) are siblings with no ordering dependency on this
task, per the batch's own rule. The builder renders that emptiness honestly,
per the Feature #621 brief and standards/generated-content.md, rather than
widening the rule to look fuller -- and, because the framework's canonical
inputs come from `validate.py`'s node walk (not a directory listing), the
`specifications/` directory need not exist on disk for this builder to run:
`generate(ctx)` never touches the filesystem directly, only `ctx.valid_nodes`.
This mirrors the same zero-match handling `index_defs/api_index.py` (#886) and
`index_defs/concept_index.py` (#889) already use on this base.

Because the listing is honestly empty today, the empty-state message also
names `launchpad/docs/corpus/templates/specification.md` (id
`corpus-template-specification`) so a reader learns what a `specifications/`
node is expected to look like instead of finding a bare "nothing here".

node_type justification: node.schema.json's type enum has no `specification`
or `index` member. `governance` is the closest true fit for this
corpus-about-corpus meta-document -- the same reasoning
`index_defs/decisions_index.py` (#845) applies to its own per-subtree index,
and the precedent nodes for corpus-about-corpus documents (corpus README,
standards, `templates/generated-index.md`, `templates/specification.md`
itself) all carry `type: governance`.
"""

_SPECIFICATIONS_PATH_PREFIX = "specifications/"


def _generate(ctx):
    members = sorted(
        (
            n
            for n in ctx.valid_nodes
            if ctx.rel_path(n).startswith(_SPECIFICATIONS_PATH_PREFIX)
        ),
        key=lambda n: ctx.rel_path(n),
    )

    lines = ["## Canonical corpus nodes under `specifications/`", ""]
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
            "No canonical corpus node currently has a corpus-root-relative path",
            "beginning `specifications/`. This listing is empty because the corpus",
            "holds no specification documents yet -- an empty fact, not an",
            "omission. It populates automatically as specification documents are",
            "authored under that prefix (see the sibling task family #1302-#1306).",
            "",
            "A node placed under `specifications/` is expected to follow",
            "`launchpad/docs/corpus/templates/specification.md`",
            "(`corpus-template-specification`): the normative definition of one",
            "protocol, algorithm, or wire/data format, with a purpose and boundary",
            "statement, motivation, definitions, a BCP 14 normative-language",
            "declaration when it uses MUST/SHOULD/MAY, the normative body itself,",
            "versioning and compatibility, a required Security Considerations",
            "section, relationships, and scope and omissions.",
        ]

    return {
        "sections": "\n".join(lines),
        "includes": [
            "every canonical corpus node whose corpus-root-relative path "
            "(as `validate.py`'s discovery contract resolves it) begins with the "
            "literal prefix `specifications/` -- a path check, never a "
            "front-matter `type` check, because a `specification` node's own "
            "`type` deliberately varies by subject"
        ],
        "excludes": [
            "nodes of any front-matter `type`, including `interfaces-events`, "
            "`architecture`, or `implementation` nodes that live outside the "
            "`specifications/` path prefix -- path membership decides inclusion "
            "here, not type",
            "the template `corpus-template-specification` itself "
            "(`templates/specification.md`), which prescribes the shape of a "
            "future specification node but is not itself a member of the "
            "`specifications/` prefix",
        ],
        "ordering": (
            "listing rows sorted lexicographically by corpus-root-relative path"
        ),
        "not_covered": [
            "The content, normative body, or maturity of any specification -- "
            "each specification node under `specifications/` owns that itself, "
            "once one exists."
        ],
    }


def _extra_evidence(ctx):
    count = sum(
        1
        for n in ctx.valid_nodes
        if ctx.rel_path(n).startswith(_SPECIFICATIONS_PATH_PREFIX)
    )
    return [
        {
            "statement": (
                f"At input digest sha256:{ctx.input_digest}, exactly {count} "
                "canonical node(s) have a corpus-root-relative path beginning "
                "`specifications/`; the listing contains exactly those nodes "
                "and no others."
            ),
            "entry_class": "FACT",
            "evidence": ["launchpad/project-intelligence/corpus/validate.py"],
        }
    ]


SPEC = {
    "name": "specifications-index",
    "output_path": "specifications/INDEX.md",
    "node_id": "specifications-index",
    "title": "Specifications index: generated listing of specification nodes",
    "node_type": "governance",
    "audiences": ("agent", "developer", "reviewer"),
    "subject": (
        "canonical corpus nodes whose path lives under the specifications/ "
        "prefix"
    ),
    "generate": _generate,
    "extra_evidence": _extra_evidence,
    "relationships": (
        {"type": "references", "target": "corpus-agents"},
        {"type": "implements", "target": "corpus-template-generated-index"},
        {"type": "references", "target": "corpus-template-specification"},
    ),
}
