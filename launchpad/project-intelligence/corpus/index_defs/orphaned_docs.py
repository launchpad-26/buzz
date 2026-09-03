"""Builder for generated/orphaned-docs.md -- issue #902 (parent PRD #621).

This document is an AUDIT REPORT, not an index: `templates/generated-index.md`
names `orphaned-docs.md` explicitly ("An audit report" / "A filtered exception
list, not a full listing"), the same non-index-shaped-sibling boundary
`index_defs/dependency_graph.py` (#896), `index_defs/coverage.py` (#892) and
`index_defs/decision_index.py` (#895) already establish for their own subjects.

**Orphan detection is reused, never recomputed.** `index_defs/dependency_graph.py`
(#896, merged) already renders an "Orphaned nodes" section straight from
`ctx.orphans` -- valid nodes with no forward or inverse edge in either
direction, computed once by `indexes.py`'s `build_context`. This builder reads
that identical field and derives nothing of its own about what counts as an
orphan: recomputing the definition here, even if it produced the same answer
today, would let the two documents silently diverge the moment either one's
notion of "orphan" drifted -- exactly the kind of drift Feature #621 exists to
catch. `dependency-graph.md` already gives a reader the orphan *list*; this
document's job is the audit value a flat list does not carry: where orphaning
concentrates, whether an orphaned node is still doing useful evidence work
despite having no corpus-graph edge, and whether its own evidence looks thin.
See "Distinction from `generated/dependency-graph.md`" (rendered in the body)
for the reader-facing statement of this boundary.

Three additional, deterministic signals, each computed directly from `ctx`
and (for the second) from `coverage.py`'s own accounting -- no new orphan
detection, no prose judgement:

1. **Concentration.** Every orphan is bucketed by its top-level corpus
   directory (the first path segment under `ctx.corpus_root`, or `(root)` for
   a node directly under the corpus root) and by its own front-matter `type`.
   Both derive from fields `ctx.rel_path` and `node.data` already expose.
2. **Coverage cross-reference.** `coverage.py` (#634, merged) assigns every
   in-scope repository source item a disposition; a `documented` row records
   which canonical node id(s) earned it. This builder loads `coverage.py` the
   same sibling-module pattern `index_defs/coverage.py` (#892) already
   established, runs `build_coverage` once, and collects every node id that
   appears in any row's `nodes` field. An orphaned node whose id appears in
   that set has no corpus-graph edge but still earns product-source coverage
   -- it is not neglected, just relationally disconnected from other corpus
   nodes. An orphaned node absent from that set is doubly disconnected: no
   corpus edge AND no coverage-earning citation, the higher-priority audit
   finding. The repo-root derivation (`corpus_root.parts[-3:] ==
   ("launchpad","docs","corpus")` -> three levels up, else the corpus root
   doubles as the repo root for a hermetic fixture) is copied verbatim from
   `index_defs/coverage.py`'s own derivation, for the identical reason: build
   the report against the real repository when running for real, and against
   a self-contained fixture tree in tests.
3. **Evidence thinness.** For every orphan, its own front-matter `evidence[]`
   entry count is compared against the corpus-wide MEDIAN entry count across
   all of `ctx.valid_nodes` (not just the orphans) -- computed fresh from the
   live node set every run, never a hardcoded number, so the threshold moves
   with the corpus rather than fossilizing. An orphan below that median is
   flagged, not because a low count is inherently wrong, but because it is a
   second, independent axis (distinct from "has no relationship") on which a
   document can look under-supported and worth a human look.

**Digest-uncovered input, disclosed rather than hidden.** `coverage.py`'s
accounting reads the repository source tree outside the corpus root (crates/,
migrations/, desktop/, ...), which `ctx.input_digest` does not cover -- the
identical disclosure `index_defs/coverage.py` (#892) and `index_defs/
decision_index.py` (#895) already make for their own digest-uncovered reads.
An `extra_evidence` FACT entry names the read; an `unverified` bullet in the
rendered body states that an unchanged corpus digest can still carry a
different coverage cross-reference if product source changes.

`node_type` choice: `governance`, following `dependency_graph.py`/
`coverage.py`/`decision_index.py`'s identical reasoning -- the subject is the
corpus's own structural health, a governance concern about the corpus itself,
not a product-surface type.

`relationships`: only `references -> corpus-agents`. `implements ->
corpus-template-generated-index` is deliberately NOT declared, for the reason
the template itself states about this exact document -- its own boundary
table names `orphaned-docs.md` as "An audit report" / "A filtered exception
list, not a full listing," i.e. not index-shaped, so claiming to implement
that template would contradict its own text. The framework still renders this
document in that template's shape-compatible body skeleton; the boundary is
about what the document *is*, the same distinction `dependency-graph.py` and
`coverage.py` already draw for themselves.
"""

from __future__ import annotations

import importlib.util
import statistics
import sys
from pathlib import Path

_COVERAGE_PATH = Path(__file__).resolve().parent.parent / "coverage.py"

# The sibling-load pattern index_defs/coverage.py itself uses: cached under
# "corpus_coverage" so this builder, coverage.py's own sibling loads, and the
# test suite all share one module object.
_coverage = sys.modules.get("corpus_coverage")
if _coverage is None:
    _spec = importlib.util.spec_from_file_location("corpus_coverage", _COVERAGE_PATH)
    _coverage = importlib.util.module_from_spec(_spec)
    sys.modules["corpus_coverage"] = _coverage
    _spec.loader.exec_module(_coverage)

_CORPUS_SUFFIX = ("launchpad", "docs", "corpus")


def _repo_root_for(corpus_root: Path) -> Path:
    """Repo root the coverage accounting hangs off of. Copied verbatim from
    index_defs/coverage.py's own derivation: three levels up from the real
    launchpad/docs/corpus layout, else the corpus root doubles as the repo
    root so a bare fixture corpus stays hermetic."""
    resolved = corpus_root.resolve()
    if resolved.parts[-3:] == _CORPUS_SUFFIX:
        return resolved.parents[2]
    return resolved


def _cell(text: str) -> str:
    return text.replace("|", "\\|")


def _top_dir(rel_path: str) -> str:
    parts = rel_path.split("/")
    return parts[0] if len(parts) > 1 else "(root)"


# build_coverage() walks the entire repository source tree (crates/,
# migrations/, desktop/, mobile/, web/, ...) and is expensive (tens of
# seconds against the real repository). Both `_generate` and `_extra_evidence`
# need the same covering-id set for the same ctx within one render call, so
# this per-process cache -- keyed by ctx object identity, never by anything
# that could be reused across a different ctx -- avoids paying that cost
# twice per document render. It never crosses process boundaries and has no
# effect on the rendered output, which is why `--check`'s in-memory-vs-disk
# diff and the two-run byte-identical test both still hold.
_covering_ids_cache: dict[int, set[str]] = {}


def _covering_node_ids(ctx) -> set[str]:
    """Every canonical node id that earns a `documented` (or any positive,
    node-linked) coverage row somewhere in coverage.py's accounting -- read
    directly from CoverageRow.nodes, never re-derived here."""
    cached = _covering_ids_cache.get(id(ctx))
    if cached is not None:
        return cached
    root = _repo_root_for(ctx.corpus_root)
    report = _coverage.build_coverage(root, ctx.corpus_root.resolve())
    covering: set[str] = set()
    for row in report.rows:
        covering.update(row.nodes)
    _covering_ids_cache[id(ctx)] = covering
    return covering


def _orphan_table_section(ctx, by_id: dict) -> list[str]:
    lines = ["### Orphaned nodes", ""]
    lines.append(
        "Reused verbatim from `ctx.orphans` -- the same field "
        "`generated/dependency-graph.md` (#896) renders its own \"Orphaned "
        "nodes\" section from. This builder computes no orphan detection of "
        "its own: a valid canonical node is orphaned exactly when it has no "
        "forward or inverse relationship edge in either direction, per "
        "`indexes.py`'s `build_context`."
    )
    lines.append("")
    if ctx.orphans:
        lines += ["| Orphaned node id | Path |", "|---|---|"]
        for node_id in ctx.orphans:
            node = by_id.get(node_id)
            path = ctx.rel_path(node) if node is not None else "?"
            lines.append(f"| {node_id} | `{path}` |")
    else:
        lines.append(
            "None at this revision -- every valid canonical node has at "
            "least one forward or inverse edge."
        )
    return lines


def _concentration_section(ctx, by_id: dict) -> list[str]:
    lines = ["### Concentration", ""]
    lines.append(
        "Where orphaning concentrates: each orphan's top-level corpus "
        "directory (first path segment under the corpus root, `(root)` for "
        "a node directly under it) and its own front-matter `type`."
    )
    lines.append("")

    by_dir: dict[str, int] = {}
    by_type: dict[str, int] = {}
    for node_id in ctx.orphans:
        node = by_id.get(node_id)
        if node is None:
            continue
        top = _top_dir(ctx.rel_path(node))
        by_dir[top] = by_dir.get(top, 0) + 1
        node_type = node.data.get("type")
        label = node_type if isinstance(node_type, str) and node_type else "(no type)"
        by_type[label] = by_type.get(label, 0) + 1

    lines.append("#### By top-level directory")
    lines.append("")
    if by_dir:
        lines += ["| Directory | Orphan count |", "|---|---|"]
        for directory in sorted(by_dir):
            lines.append(f"| `{_cell(directory)}` | {by_dir[directory]} |")
    else:
        lines.append("None at this revision -- there are no orphaned nodes.")
    lines.append("")

    lines.append("#### By node type")
    lines.append("")
    if by_type:
        lines += ["| Type | Orphan count |", "|---|---|"]
        for node_type in sorted(by_type):
            lines.append(f"| {_cell(node_type)} | {by_type[node_type]} |")
    else:
        lines.append("None at this revision -- there are no orphaned nodes.")
    return lines


def _coverage_cross_reference_section(ctx, by_id: dict, covering_ids: set[str]) -> list[str]:
    lines = ["### Coverage cross-reference", ""]
    lines.append(
        "Whether an orphaned node's id appears in any row of "
        "`coverage.py`'s (#634) accounting as a node that earns a positive "
        "disposition for some in-scope repository source item. An orphan "
        "that earns coverage has no corpus-graph edge but is still doing "
        "useful evidence work -- it documents real source, it is simply not "
        "linked to another corpus node. An orphan that earns no coverage is "
        "doubly disconnected: no corpus edge and no coverage-earning "
        "citation, the higher-priority finding of the two."
    )
    lines.append("")

    earning = [nid for nid in ctx.orphans if nid in covering_ids]
    not_earning = [nid for nid in ctx.orphans if nid not in covering_ids]

    lines.append(
        f"**{len(earning)} of {len(ctx.orphans)}** orphaned node(s) earn at "
        "least one coverage row; "
        f"**{len(not_earning)}** earn none (doubly disconnected)."
    )
    lines.append("")

    lines.append("#### Earns coverage despite no corpus edge")
    lines.append("")
    if earning:
        lines += ["| Orphaned node id | Path |", "|---|---|"]
        for node_id in earning:
            node = by_id.get(node_id)
            path = ctx.rel_path(node) if node is not None else "?"
            lines.append(f"| {node_id} | `{path}` |")
    else:
        lines.append(
            "None at this revision -- no orphaned node earns a coverage row."
        )
    lines.append("")

    lines.append("#### Doubly disconnected (no corpus edge, no coverage row)")
    lines.append("")
    if not_earning:
        lines += ["| Orphaned node id | Path |", "|---|---|"]
        for node_id in not_earning:
            node = by_id.get(node_id)
            path = ctx.rel_path(node) if node is not None else "?"
            lines.append(f"| {node_id} | `{path}` |")
    else:
        lines.append(
            "None at this revision -- every orphaned node earns at least "
            "one coverage row."
        )
    return lines


def _evidence_thinness_section(ctx, by_id: dict) -> list[str]:
    lines = ["### Evidence thinness", ""]
    lines.append(
        "Orphaned nodes whose own front-matter `evidence[]` entry count "
        "falls below the corpus-wide MEDIAN entry count across all "
        "`ctx.valid_nodes` (recomputed fresh every run from the live node "
        "set, never a hardcoded number). A low count is not inherently "
        "wrong; this is a second, independent axis from \"has no "
        "relationship\" on which a document can look under-supported and "
        "worth a closer look."
    )
    lines.append("")

    all_counts = [len(n.data.get("evidence") or []) for n in ctx.valid_nodes]
    if not all_counts:
        lines.append(
            "None at this revision -- there are no valid canonical nodes to "
            "compute a median from."
        )
        return lines

    median = statistics.median(all_counts)
    lines.append(
        f"Corpus-wide median evidence entry count at this revision: "
        f"**{median}** (over {len(all_counts)} valid node(s))."
    )
    lines.append("")

    thin = [
        nid
        for nid in ctx.orphans
        if by_id.get(nid) is not None
        and len(by_id[nid].data.get("evidence") or []) < median
    ]
    if thin:
        lines += [
            "| Orphaned node id | Path | Evidence entries |",
            "|---|---|---|",
        ]
        for node_id in thin:
            node = by_id[node_id]
            path = ctx.rel_path(node)
            count = len(node.data.get("evidence") or [])
            lines.append(f"| {node_id} | `{path}` | {count} |")
    else:
        lines.append(
            "None at this revision -- no orphaned node's evidence entry "
            "count falls below the corpus-wide median."
        )
    return lines


def _distinction_section() -> list[str]:
    return [
        "## Distinction from `generated/dependency-graph.md`",
        "",
        "This document is a different thing from `generated/dependency-graph.md` "
        "(node id `generated-dependency-graph`, issue #896, merged), which "
        "already renders the full graph -- forward edges, their generated "
        "inverses, broken edges, and its own \"Orphaned nodes\" section built "
        "from the identical `ctx.orphans` field this document reuses. Reading "
        "`dependency-graph.md`'s orphan section gives a reader the flat list: "
        "which nodes have no edge. **This document does not repeat that list "
        "for its own sake** -- it answers three further questions the graph "
        "document does not: where does orphaning concentrate (by directory and "
        "by node type); does an orphaned node still earn coverage for real "
        "repository source despite having no corpus-graph edge, or is it "
        "doubly disconnected; and does an orphaned node's own evidence look "
        "unusually thin. **Read `dependency-graph.md` for the graph and the "
        "orphan list itself; read this document for the audit -- where the "
        "orphans are, whether they are still doing useful work, and which of "
        "them warrant a closer look.** Neither document recomputes the other's "
        "definition of what an orphan is: both read the identical "
        "`ctx.orphans` field, so they cannot silently disagree.",
        "",
    ]


def _generate(ctx):
    by_id = {n.id: n for n in ctx.valid_nodes if isinstance(n.id, str)}
    covering_ids = _covering_node_ids(ctx)

    lines = []
    lines += _distinction_section()
    lines.append("## Orphaned documents audit")
    lines.append("")
    lines += _orphan_table_section(ctx, by_id)
    lines.append("")
    lines += _concentration_section(ctx, by_id)
    lines.append("")
    lines += _coverage_cross_reference_section(ctx, by_id, covering_ids)
    lines.append("")
    lines += _evidence_thinness_section(ctx, by_id)

    return {
        "sections": "\n".join(lines),
        "includes": [
            "every valid canonical node with no forward or inverse "
            "relationship edge in either direction, exactly as `ctx.orphans` "
            "(computed once by `indexes.py`'s `build_context`, shared with "
            "`generated/dependency-graph.md`) carries it -- never recomputed "
            "independently here",
            "each orphan's top-level corpus directory and front-matter "
            "`type`, bucketed into concentration tables",
            "each orphan's presence or absence in `coverage.py`'s (#634) "
            "accounting as a node earning at least one `documented` (or "
            "otherwise node-linked) coverage row, splitting orphans into "
            "\"earns coverage\" and \"doubly disconnected\"",
            "each orphan's own front-matter evidence entry count, flagged "
            "when it falls below the corpus-wide median entry count across "
            "all valid canonical nodes (recomputed fresh every run)",
        ],
        "excludes": [
            "any node that has at least one forward or inverse relationship "
            "edge -- this document is scoped to `ctx.orphans` exclusively, "
            "the identical set `generated/dependency-graph.md` already lists",
            "a second, independent orphan-detection rule -- there is exactly "
            "one definition of \"orphan\" in this corpus (`ctx.orphans`), "
            "shared by every document that renders one",
            "any judgement about whether a given orphan or coverage gap is "
            "a genuine authoring mistake or an intentional, temporary state "
            "-- left to a human reader",
        ],
        "ordering": (
            "the orphaned-nodes table follows ctx.orphans's own sorted-by-id "
            "order; concentration tables are sorted by directory/type label; "
            "the coverage cross-reference tables and the evidence-thinness "
            "table each follow ctx.orphans's order, filtered"
        ),
        "not_covered": [
            "The full relationship graph -- forward edges, generated "
            "inverses, broken edges -- `generated/dependency-graph.md` (#896) "
            "owns that.",
            "Fixing any individual orphan, coverage gap, or thin-evidence "
            "finding -- a future authoring or relationship-linking task, "
            "never an edit to this generated file.",
            "Whether `coverage.py --strict` becomes a CI or validate gate -- "
            "that is #621's CI wiring decision, not this report's.",
        ],
        "unverified": [
            "`ctx.input_digest` covers canonical corpus inputs only. The "
            "coverage cross-reference reads the repository source tree "
            "outside the corpus root (crates/, migrations/, desktop/, ...) "
            "via `coverage.py`, which that digest does not cover -- an "
            "unchanged corpus digest with changed product source can yield a "
            "different coverage cross-reference under the same digest, the "
            "identical disclosure `index_defs/coverage.py` (#892) and "
            "`index_defs/decision_index.py` (#895) already make for their "
            "own digest-uncovered reads.",
        ],
    }


def _extra_evidence(ctx):
    # The framework always calls generate(ctx) before extra_evidence(ctx)
    # (render_document builds the body first, then the front matter), so the
    # covering-id set is already cached under this ctx's identity by the time
    # this runs -- no second, expensive build_coverage() call.
    covering_ids = _covering_node_ids(ctx)
    earning = sum(1 for nid in ctx.orphans if nid in covering_ids)
    not_earning = len(ctx.orphans) - earning
    all_counts = [len(n.data.get("evidence") or []) for n in ctx.valid_nodes]
    median = statistics.median(all_counts) if all_counts else 0
    return [
        {
            "statement": (
                f"At input digest sha256:{ctx.input_digest}, "
                f"{len(ctx.orphans)} of {len(ctx.valid_nodes)} valid "
                "canonical node(s) are orphaned (ctx.orphans, computed by "
                "indexes.py's build_context, the identical field "
                "generated/dependency-graph.md renders its own orphan "
                f"section from); {earning} of those orphans earn at least "
                f"one coverage.py (#634) accounting row and {not_earning} "
                "earn none; the corpus-wide median front-matter evidence "
                f"entry count across all valid nodes is {median}."
            ),
            "entry_class": "FACT",
            "evidence": [
                "launchpad/project-intelligence/corpus/indexes.py",
                "launchpad/project-intelligence/corpus/coverage.py",
            ],
        }
    ]


SPEC = {
    "name": "orphaned-docs",
    "output_path": "generated/orphaned-docs.md",
    "node_id": "generated-orphaned-docs",
    "title": "Orphaned docs: generated orphaned-node audit report",
    "node_type": "governance",
    "audiences": ("agent", "developer", "reviewer"),
    "subject": (
        "an audit of the corpus's own orphaned canonical nodes (ctx.orphans, "
        "reused from generated/dependency-graph.md's identical field) -- "
        "where orphaning concentrates, whether an orphan still earns "
        "coverage.py accounting despite having no corpus-graph edge, and "
        "whether its own evidence looks unusually thin"
    ),
    "generate": _generate,
    "extra_evidence": _extra_evidence,
    "relationships": ({"type": "references", "target": "corpus-agents"},),
}
