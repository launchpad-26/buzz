"""Builder for the corpus root index -- issue #638 (parent PRD #621).

Generates ``launchpad/docs/corpus/INDEX.md``: the top-level table of contents of
the corpus. Its inclusion rule is deliberately the widest one the framework can
express -- every canonical node the validator's own discovery contract finds --
because a root index that filtered by type, status or audience would be a
different document (that is what the subject-specific indexes under
``generated/`` are for).

Node type is ``governance``: node.schema.json's type enum has no ``index``
value, and ``governance`` is the documented precedent for corpus-infrastructure
nodes (README.md, the ``standards/`` family and
``templates/generated-index.md`` all carry it and state that reasoning).

Grouping and ordering are purely path-derived, never judgement-derived:
corpus-root-level files form the first group, then each top-level directory in
sorted name order; rows within a group sort by corpus-root-relative path.
Nodes that fail to parse or validate are still listed (by path, in their own
subsection) rather than silently dropped -- the same honesty rule
``validate.py``'s ``find_non_canonical_nodes`` applies to its exclusions.
"""


def _rows(ctx, nodes):
    return [
        f"| `{node.id}` | {node.data.get('type', '?')} | `{ctx.rel_path(node)}` |"
        for node in sorted(nodes, key=ctx.rel_path)
    ]


def _generate(ctx):
    root_label = "Corpus root"
    groups: dict[str, list] = {}
    for node in ctx.valid_nodes:
        parts = ctx.rel_path(node).split("/")
        group = f"`{parts[0]}/`" if len(parts) > 1 else root_label
        groups.setdefault(group, []).append(node)

    ordered_groups = [g for g in [root_label] if g in groups] + sorted(
        g for g in groups if g != root_label
    )

    invalid = [n for n in ctx.nodes if n.error is not None]

    lines = [
        "## Corpus index",
        "",
        f"{len(ctx.valid_nodes)} valid canonical node(s) in {len(ordered_groups)} "
        f"group(s); {len(invalid)} discovered file(s) failed to parse or validate.",
    ]
    for group in ordered_groups:
        nodes = groups[group]
        lines += [
            "",
            f"### {group} ({len(nodes)})",
            "",
            "| Id | Type | Path |",
            "|---|---|---|",
            *_rows(ctx, nodes),
        ]
    if invalid:
        lines += [
            "",
            "### Discovered but not valid",
            "",
            "These files are inside the discovery contract but failed to parse or",
            "validate; they are listed rather than dropped:",
            "",
            *[f"- `{ctx.rel_path(node)}`" for node in sorted(invalid, key=ctx.rel_path)],
        ]
    lines += [
        "",
        "## Registered generated outputs",
        "",
        "Registered builder output paths at generation time. Each is a generated",
        "derived view, excluded from the canonical listing above by construction:",
        "",
        *[f"- `{path}`" for path in ctx.output_paths],
    ]
    return {
        "sections": "\n".join(lines),
        "includes": [
            "every canonical corpus node `validate.py`'s `discover_markdown_files` "
            "contract finds -- no type, status or audience filter narrows the root "
            "index",
            "discovered files that fail to parse or validate, listed by path in "
            "their own subsection rather than silently dropped",
        ],
        "excludes": [
            "nothing subject-specific -- this is the root table of contents, so "
            "the only exclusions are the contract-level ones below",
        ],
        "ordering": (
            "groups: the corpus root first, then top-level directories in sorted "
            "name order; rows within each group sort by corpus-root-relative path"
        ),
        "not_covered": [
            "each subject-specific generated view's own listing -- the registered "
            "outputs named above own those.",
        ],
    }


SPEC = {
    "name": "index",
    "output_path": "INDEX.md",
    "node_id": "corpus-index",
    "title": "Corpus index: generated index",
    "node_type": "governance",
    "audiences": ["agent", "developer", "reviewer"],
    "subject": "every canonical corpus node, grouped by top-level directory",
    "generate": _generate,
    "relationships": [
        {"type": "references", "target": "corpus-agents"},
        {"type": "implements", "target": "corpus-template-generated-index"},
    ],
}
