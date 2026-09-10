"""Builder for generated/api-index.md -- the API/interface surface index (#886).

Inclusion rule (deterministic, schema-grounded): a canonical node is listed if
and only if its front-matter `type` is `interfaces-events` -- node.schema.json's
own enum value for interface/event-surface contracts. Membership is decided by
that field alone, never by prose judgement, path keywords, or title matching.
At the time this builder was written the rule matches zero canonical nodes on
the merge base; the builder renders that emptiness honestly instead of widening
the rule (per the Feature #621 brief and standards/generated-content.md).

node_type choice: `interfaces-events`, the subject's own type. The precedent
(corpus README/standards) uses `governance` for corpus-about-corpus nodes, but
templates/generated-index.md's contract lets a subject-specific index carry its
subject's type; this document IS the corpus's view of the interfaces-events
surface, so a reader filtering by that type finds the index alongside its
members. The type enum is read from node.schema.json by the framework, which
rejects any non-enum value at discovery time.
"""


def _generate(ctx):
    members = sorted(
        (n for n in ctx.valid_nodes if n.data.get("type") == "interfaces-events"),
        key=lambda n: str(n.id),
    )
    lines = ["## API surface listing", ""]
    if members:
        lines += ["| Node id | Path | Status | Audiences |", "|---|---|---|---|"]
        for node in members:
            audiences = ", ".join(node.data.get("audiences") or [])
            lines.append(
                f"| {node.id} | `{ctx.rel_path(node)}` | "
                f"{node.data.get('status', '')} | {audiences} |"
            )
    else:
        lines += [
            "No canonical corpus node currently carries front-matter",
            "`type: interfaces-events`. This listing is empty because the corpus",
            "holds no API-surface nodes yet -- an empty fact, not an omission.",
            "It will populate automatically when interface/event nodes merge.",
        ]
    return {
        "sections": "\n".join(lines),
        "includes": [
            "every canonical corpus node whose front-matter `type` is "
            "`interfaces-events` -- node.schema.json's type-enum value for "
            "interface/event-surface contracts (API endpoints, protocol "
            "messages, event kinds)"
        ],
        "excludes": [
            "nodes of any other type, even when their prose describes protocol "
            "flows or endpoints (e.g. `architecture` flow nodes such as "
            "`architecture-flows-http-event-submission`) -- the front-matter "
            "`type` field decides membership, never content",
            "the governance templates `corpus-template-interface` and "
            "`corpus-template-event-kind`, which prescribe the shape of future "
            "interface/event nodes but are not themselves API-surface nodes",
        ],
        "ordering": "listing rows sorted lexicographically by node id",
        "not_covered": [
            "The runtime API surface itself (HTTP endpoints, NIPs, event "
            "kinds) -- this index lists corpus nodes documenting that surface, "
            "not the surface."
        ],
    }


def _extra_evidence(ctx):
    count = sum(
        1 for n in ctx.valid_nodes if n.data.get("type") == "interfaces-events"
    )
    return [
        {
            "statement": (
                f"At input digest sha256:{ctx.input_digest}, exactly {count} "
                "canonical node(s) carry front-matter type: interfaces-events; "
                "the listing contains exactly those nodes and no others."
            ),
            "entry_class": "FACT",
            "evidence": ["launchpad/docs/corpus/schema/node.schema.json"],
        }
    ]


SPEC = {
    "name": "api-index",
    "output_path": "generated/api-index.md",
    "node_id": "generated-api-index",
    "title": "API index: generated listing of interface and event surface nodes",
    "node_type": "interfaces-events",
    "audiences": ["agent", "developer"],
    "subject": "the canonical corpus nodes typed interfaces-events (the API/interface surface)",
    "generate": _generate,
    "extra_evidence": _extra_evidence,
    "relationships": (
        {"type": "references", "target": "corpus-agents"},
        {"type": "implements", "target": "corpus-template-generated-index"},
    ),
}
