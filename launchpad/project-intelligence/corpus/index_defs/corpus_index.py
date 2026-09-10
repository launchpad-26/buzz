"""Builder for the corpus summary index -- issue #891 (parent PRD #621).

Generates ``launchpad/docs/corpus/generated/corpus-index.md``: an aggregate
STATS view of the corpus -- counts of canonical nodes by front-matter type,
status and audience, and by top-level directory. It deliberately emits no
per-node rows at all: the full id/type/path listing already exists as
``INDEX.md`` (node id ``corpus-index``, builder ``index_defs/index.py``,
issue #638), and a second per-node listing would be a near-duplicate. This
node's id is ``generated-corpus-index`` and the distinction between the two
documents is stated in the rendered body itself, so a reader is never left
guessing which one to consult.

Node type is ``governance``: node.schema.json's type enum has no ``index``
value, and ``governance`` is the documented precedent for corpus-infrastructure
nodes (README.md, the ``standards/`` family, ``templates/generated-index.md``
and the root index builder all carry it and state that reasoning).

Every count is derived mechanically from front-matter fields
(``type``/``status``/``audiences``) or from the corpus-root-relative path --
never from prose judgement. Ordering is deterministic: type, status and
audience rows sort by category value; directory rows put the corpus root
first, then top-level directory names in sorted order (the same group order
the root index uses). Discovered files that fail to parse or validate are
counted -- honestly, as a number -- but cannot contribute to the front-matter
tables, and that is said inline.
"""

from collections import Counter

_ROOT_LABEL = "(corpus root)"


def _count_table(header: str, counts: dict) -> list[str]:
    lines = [f"| {header} | Count |", "|---|---|"]
    lines += [f"| {key} | {counts[key]} |" for key in counts]
    return lines


def _generate(ctx):
    valid = ctx.valid_nodes
    invalid = [n for n in ctx.nodes if n.error is not None]

    by_type = dict(sorted(Counter(n.data.get("type", "?") for n in valid).items()))
    by_status = dict(
        sorted(Counter(n.data.get("status", "?") for n in valid).items())
    )
    by_audience = dict(
        sorted(
            Counter(
                a for n in valid for a in (n.data.get("audiences") or [])
            ).items()
        )
    )
    dir_counts = Counter(
        parts[0] + "/" if len(parts) > 1 else _ROOT_LABEL
        for parts in (ctx.rel_path(n).split("/") for n in valid)
    )
    by_dir = {
        key: dir_counts[key]
        for key in (
            [k for k in [_ROOT_LABEL] if k in dir_counts]
            + sorted(k for k in dir_counts if k != _ROOT_LABEL)
        )
    }

    lines = [
        "## Corpus summary",
        "",
        "**Which index to consult:** this document is the *aggregate summary* "
        "view of the corpus -- counts only, no individual nodes. For the full "
        "per-node listing (every node's id, type and path, grouped by "
        "directory), consult `INDEX.md` (node id `corpus-index`). This "
        "document (node id `generated-corpus-index`) intentionally names no "
        "individual node, so the two generated views never duplicate each "
        "other.",
        "",
        f"{len(valid)} valid canonical node(s); {len(invalid)} discovered "
        "file(s) failed to parse or validate (counted here, listed per-path "
        "by `INDEX.md`). Invalid files cannot contribute to the front-matter "
        "tables below.",
        "",
        "### Nodes by type",
        "",
        *_count_table("Type", by_type),
        "",
        "### Nodes by status",
        "",
        *_count_table("Status", by_status),
        "",
        "### Nodes by audience",
        "",
        "A node declares one or more audiences, so this column sums to more "
        "than the node count -- each node is counted once per declared "
        "audience:",
        "",
        *_count_table("Audience", by_audience),
        "",
        "### Nodes by top-level directory",
        "",
        *_count_table("Directory", by_dir),
    ]
    return {
        "sections": "\n".join(lines),
        "includes": [
            "every valid canonical corpus node, counted exactly once in the "
            "type, status and directory tables, and once per declared "
            "audience in the audience table -- counts derive only from "
            "front-matter fields and corpus-root-relative paths, never from "
            "prose",
            "discovered files that fail to parse or validate, as an honest "
            "count (their front matter is unreadable, so they cannot join "
            "the tables)",
        ],
        "excludes": [
            "per-node rows of any kind -- ids, titles and paths are "
            "`INDEX.md`'s job (node `corpus-index`); this summary "
            "deliberately names no individual node",
            "graph-shape statistics (edge, orphan and broken-edge counts) -- "
            "outside this summary's front-matter and path aggregates",
        ],
        "ordering": (
            "type, status and audience rows sort by category value; directory "
            "rows put the corpus root first, then top-level directory names "
            "in sorted order"
        ),
        "not_covered": [
            "the per-node listing itself -- `INDEX.md` (node `corpus-index`) "
            "owns that.",
            "why any count is what it is -- the canonical nodes themselves "
            "own their type, status and audience declarations.",
        ],
    }


def _extra_evidence(ctx):
    valid = ctx.valid_nodes
    invalid_count = sum(1 for n in ctx.nodes if n.error is not None)
    n_types = len({n.data.get("type") for n in valid})
    n_statuses = len({n.data.get("status") for n in valid})
    return [
        {
            "statement": (
                f"At input digest sha256:{ctx.input_digest}, the corpus holds "
                f"{len(valid)} valid canonical node(s) across {n_types} "
                f"distinct type(s) and {n_statuses} distinct status value(s); "
                f"{invalid_count} discovered file(s) failed to parse or "
                "validate. All counts derive from front-matter fields and "
                "paths only."
            ),
            "entry_class": "FACT",
            "evidence": ["launchpad/docs/corpus/schema/node.schema.json"],
        },
        {
            "statement": (
                "The full per-node listing lives in INDEX.md (node id "
                "corpus-index); this summary intentionally lists no "
                "individual node, so the two generated views do not "
                "duplicate each other."
            ),
            "entry_class": "FACT",
            "evidence": [
                "launchpad/project-intelligence/corpus/index_defs/index.py"
            ],
        },
    ]


SPEC = {
    "name": "corpus-index",
    "output_path": "generated/corpus-index.md",
    "node_id": "generated-corpus-index",
    "title": "Corpus summary: generated index",
    "node_type": "governance",
    "audiences": ["agent", "developer", "reviewer"],
    "subject": (
        "aggregate counts of canonical corpus nodes by type, status, audience "
        "and top-level directory"
    ),
    "generate": _generate,
    "extra_evidence": _extra_evidence,
    "relationships": (
        {"type": "references", "target": "corpus-agents"},
        {"type": "implements", "target": "corpus-template-generated-index"},
    ),
}
