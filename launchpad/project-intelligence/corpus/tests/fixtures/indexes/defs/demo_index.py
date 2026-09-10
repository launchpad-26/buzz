"""Fixture builder for test_indexes.py -- NOT a real corpus builder.

Deliberately a plain dict SPEC with no framework imports, proving a builder
module can depend on nothing but the documented contract."""


def _generate(ctx):
    rows = [
        f"| {node.id} | `{ctx.rel_path(node)}` |"
        for node in sorted(ctx.valid_nodes, key=lambda n: str(n.id))
    ]
    listing = "\n".join(
        ["## Demo listing", "", "| Id | Path |", "|---|---|", *rows]
    )
    return {
        "sections": listing,
        "includes": [
            "every canonical corpus node the validator's discovery contract finds"
        ],
        "excludes": ["nothing subject-specific"],
        "ordering": "listing rows sorted by node id",
    }


SPEC = {
    "name": "demo-index",
    "output_path": "generated/demo-index.md",
    "node_id": "fixture-generated-demo-index",
    "title": "Demo index: generated index",
    "node_type": "governance",
    "audiences": ["agent"],
    "subject": "the fixture corpus nodes",
    "generate": _generate,
}
