"""Builder for launchpad/docs/corpus/decisions/INDEX.md -- issue #845.

Generates the decisions index: where the canonical corpus depends on decision
records. Two deterministic, front-matter-grounded rules select content:

1. A canonical node is listed iff any of its front-matter ``evidence[].evidence``
   citation strings has a path part (before any ``#`` fragment) that begins with
   ``launchpad/decisions/`` and ends with ``.md``. Rows are grouped by the cited
   decision-record path, so the table answers "which nodes rely on this record".
2. Canonical nodes whose corpus-root-relative path begins with ``decisions/``
   (the corpus's own decision-reference nodes) are listed separately -- honestly
   empty while none exist.

The raw ADR files under ``launchpad/decisions/`` are NOT inputs: they are
repository decision records, not corpus nodes, so validate.py's discovery
contract never loads them and this builder never reads them. This index maps
citations *to* them; it does not summarize or restate them.

node_type justification: node.schema.json's type enum has no ``decision`` or
``index`` member. ``governance`` is the closest true fit -- decision records
carry authorized/normative intent, and the precedent nodes on this subject
(``standards/decision-references.md``, ``templates/decision-reference.md``,
``templates/generated-index.md``, the corpus README) all carry
``type: governance``.
"""

_DECISIONS_PATH_PREFIX = "launchpad/decisions/"


def _decision_records_cited(node) -> set:
    """The set of launchpad/decisions/*.md paths this node's front-matter
    evidence citations name. Fragments (``#...``) are stripped before matching
    so cited spans group under their record's path."""
    records = set()
    for entry in node.data.get("evidence") or []:
        if not isinstance(entry, dict):
            continue
        for citation in entry.get("evidence") or []:
            if not isinstance(citation, str):
                continue
            path = citation.split("#", 1)[0]
            if path.startswith(_DECISIONS_PATH_PREFIX) and path.endswith(".md"):
                records.add(path)
    return records


def _generate(ctx):
    by_record: dict = {}
    for node in ctx.valid_nodes:
        if not isinstance(node.id, str):
            continue
        for record in _decision_records_cited(node):
            by_record.setdefault(record, set()).add(node.id)

    citing_ids = sorted({i for ids in by_record.values() for i in ids})

    parts = [
        "## Decision records cited by canonical nodes",
        "",
        f"{len(by_record)} decision-record path(s) under `launchpad/decisions/` are "
        f"cited by the front-matter evidence of {len(citing_ids)} canonical corpus "
        "node(s). Rows are sorted by decision-record path; citing node ids are "
        "sorted lexicographically.",
        "",
    ]
    if by_record:
        parts.append("| Decision record | Cited by (node ids) |")
        parts.append("|---|---|")
        for record, ids in sorted(by_record.items()):
            cited_by = ", ".join(f"`{node_id}`" for node_id in sorted(ids))
            parts.append(f"| `{record}` | {cited_by} |")
    else:
        parts.append(
            "None -- no canonical node's front-matter evidence cites a "
            "`launchpad/decisions/` path at this input digest."
        )

    decision_nodes = sorted(
        (n for n in ctx.valid_nodes if ctx.rel_path(n).startswith("decisions/")),
        key=lambda n: ctx.rel_path(n),
    )
    parts += [
        "",
        "## Canonical corpus nodes under `decisions/`",
        "",
    ]
    if decision_nodes:
        parts.append("| Id | Path |")
        parts.append("|---|---|")
        for node in decision_nodes:
            parts.append(f"| `{node.id}` | `{ctx.rel_path(node)}` |")
    else:
        parts.append(
            "None -- no canonical corpus node lives under the `decisions/` path "
            "prefix at this input digest. This listing is deliberately rendered "
            "empty rather than omitted, so its absence is a stated fact, not "
            "silence."
        )

    return {
        "sections": "\n".join(parts),
        "includes": (
            "canonical nodes whose front-matter `evidence[].evidence` citation "
            "strings have a path part (before any `#` fragment) beginning "
            "`launchpad/decisions/` and ending `.md`, grouped by the cited "
            "decision-record path",
            "canonical corpus nodes whose corpus-root-relative path begins "
            "`decisions/`, listed even when zero exist",
        ),
        "excludes": (
            "The ADR files under `launchpad/decisions/` themselves: they are "
            "repository decision records, not corpus nodes, so they sit outside "
            "`validate.py`'s discovery contract and are not inputs to this "
            "generator -- this index maps citations to them, it never reads them",
            "Decision records mentioned only in body prose: front-matter evidence "
            "citations are the schema-structured, deterministically extractable "
            "signal, so prose mentions do not create rows",
        ),
        "ordering": (
            "decision-record table rows sorted by record path with citing node "
            "ids sorted lexicographically; the `decisions/` node listing sorted "
            "by corpus-root-relative path"
        ),
        "not_covered": (
            "The content, status, or outcome of any decision record -- "
            "`launchpad/decisions/` owns that, and unresolved decisions stay "
            "unresolved there, not here",
        ),
        "unverified": (
            "Whether each cited `launchpad/decisions/` path resolves to an "
            "existing file: this builder matches citation strings only; "
            "`validate.py`'s citation checking owns path existence",
        ),
    }


SPEC = {
    "name": "decisions-index",
    "output_path": "decisions/INDEX.md",
    "node_id": "decisions-index",
    "title": "Decisions index: generated index",
    "node_type": "governance",
    "audiences": ("agent", "developer", "reviewer"),
    "subject": (
        "decision-record citations in canonical front-matter evidence, and "
        "canonical nodes under decisions/"
    ),
    "generate": _generate,
    "relationships": (
        {"type": "implements", "target": "corpus-template-generated-index"},
        {"type": "references", "target": "corpus-agents"},
        {"type": "references", "target": "corpus-standard-decision-references"},
    ),
}
