"""Builder: generated/coverage.md -- issue #892 (parent PRD #621).

A generated METRIC REPORT, not a flat node listing: it renders
`coverage.py`'s (issue #634) completeness accounting -- every in-scope source
inventory item with the single positive disposition assigned to it, or a
visible ``GAP``. GAP rows are rendered, never hidden, and the report claims
completeness only when `CoverageReport.complete` is true (zero GAP rows).

``node_type`` choice: ``governance``, following the glossary/index/
decisions-index precedent -- the subject is the corpus's own completeness
accounting, a concern of the corpus about itself, and node.schema.json's type
enum has no metric/report value; no product-surface type fits a meta-report.

Relationships: only ``references -> corpus-agents``. ``implements ->
corpus-template-generated-index`` is deliberately NOT declared: that
template's own boundary table names ``coverage.md`` as a metric report that
"states a metric, not a listing of nodes", i.e. not index-shaped, so claiming
to implement it would contradict the template's own scope. The framework
still renders this document in that template's body skeleton, which is
shape-compatible; the boundary is about what the document *is*.

Repo-root derivation: `build_coverage(root, corpus_root)` needs the
repository root (the inventory side), while the framework hands builders only
``ctx.corpus_root``. When the corpus root ends with ``launchpad/docs/corpus``
(the real layout, and test_coverage.py's fixture layout) the root is three
levels up; otherwise the corpus root itself doubles as the inventory root, so
a bare fixture corpus stays hermetic instead of silently scanning the real
repository.

Determinism note: nothing rendered here may depend on whether the generated
file itself already exists on disk. `build_coverage` runs validate.py's full
node walk (which sees generated outputs once written), so this builder never
renders counts from that node set -- every number below derives from the
source inventory rows, which the corpus's own files can never be
(``launchpad`` is in inventory.py's deliberately-ignored top-level set).
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_COVERAGE_PATH = Path(__file__).resolve().parent.parent / "coverage.py"

# The sibling-load pattern coverage.py itself uses: cached under
# "corpus_coverage" so this builder, coverage.py's own sibling loads, and the
# test suite all share one module object.
_coverage = sys.modules.get("corpus_coverage")
if _coverage is None:
    _spec = importlib.util.spec_from_file_location("corpus_coverage", _COVERAGE_PATH)
    _coverage = importlib.util.module_from_spec(_spec)
    sys.modules["corpus_coverage"] = _coverage
    _spec.loader.exec_module(_coverage)

_CORPUS_SUFFIX = ("launchpad", "docs", "corpus")

# Fixed rendering order: the four positive dispositions #634 defines, then the
# one visible failure state. Zero counts render too, so the vocabulary (and
# the absence of any "not examined" state) is always on the page.
_DISPOSITION_ORDER = (
    _coverage.DOCUMENTED,
    _coverage.REPRESENTED_ELSEWHERE,
    _coverage.GENERATED_ONLY,
    _coverage.EXPLICITLY_EXCLUDED,
    _coverage.GAP,
)


def _repo_root_for(corpus_root: Path) -> Path:
    resolved = corpus_root.resolve()
    if resolved.parts[-3:] == _CORPUS_SUFFIX:
        return resolved.parents[2]
    return resolved


def _cell(text: str) -> str:
    return text.replace("|", "\\|")


def _generate(ctx):
    root = _repo_root_for(ctx.corpus_root)
    report = _coverage.build_coverage(root, ctx.corpus_root.resolve())

    counts = {d: 0 for d in _DISPOSITION_ORDER}
    for row in report.rows:
        counts[row.disposition] = counts.get(row.disposition, 0) + 1
    total = len(report.rows)
    gaps = len(report.gaps)

    lines = [
        "## Coverage report",
        "",
    ]
    if report.complete:
        lines.append(
            f"**COMPLETE**: all {total} in-scope source items are positively "
            "dispositioned at this revision."
        )
    else:
        lines.append(
            f"**INCOMPLETE**: {gaps} of {total} in-scope source items are "
            "`GAP` rows at this revision, each visible in the accounting "
            "table below."
        )
    lines += [
        "",
        "`GAP` dispositions are visible, not hidden: a gap is rendered as a "
        "row like any other disposition, and this report never claims "
        "completeness while `coverage.py` itself reports gaps -- "
        "`CoverageReport.complete` is true exactly when there are zero `GAP` "
        "rows, and that is the only completeness test used here.",
        "",
        "### Disposition summary",
        "",
        "| Disposition | Items |",
        "|---|---|",
    ]
    for disposition in _DISPOSITION_ORDER:
        lines.append(f"| {disposition} | {counts[disposition]} |")
    lines += [
        "",
        "### Accounting",
        "",
        "One row per in-scope source item; `nodes` are the canonical corpus "
        "node ids whose citations cover the item, `aliases` are covering "
        "manifest task aliases or registry `accounted_by` entries.",
        "",
        "| Category | Source key | Path | Disposition | Nodes | Aliases | Detail |",
        "|---|---|---|---|---|---|---|",
    ]
    for row in report.rows:
        lines.append(
            "| "
            + " | ".join(
                (
                    _cell(row.category),
                    f"`{_cell(row.source_key)}`",
                    f"`{_cell(row.path)}`",
                    _cell(row.disposition),
                    _cell(", ".join(row.nodes)),
                    _cell(", ".join(row.aliases)),
                    _cell(row.detail),
                )
            )
            + " |"
        )
    lines += [
        "",
        "### Advisory findings",
        "",
    ]
    if report.findings:
        for finding in report.findings:
            lines.append(f"- {_cell(finding)}")
    else:
        lines.append("- None at this revision.")

    return {
        "sections": "\n".join(lines),
        "includes": [
            "every in-scope source item `inventory.py` (issue #624) discovers "
            "-- Rust workspace crates, event kinds, relay routes, migrations, "
            "desktop/mobile/web features, integration test suites, formal "
            "models, existing docs, and `.env.example` configuration keys -- "
            "one accounting row each, plus one unconditional `GAP` row per "
            "top-level directory the inventory neither discovers nor "
            "deliberately ignores",
            "the single disposition `coverage.py` (issue #634) assigns each "
            "item: `documented` earned by a canonical node's file/position "
            "citation, a registry-recorded positive disposition, or a visible "
            "`GAP` when nothing accounts for the item. At this revision no "
            "#626 manifest JSON and no dispositions registry exist in the "
            "tree, so neither optional input is passed and `documented` is "
            "the only earnable positive disposition",
        ],
        "excludes": [
            "source areas `inventory.py` deliberately ignores (VCS/tool "
            "internals, build artifacts, and the `launchpad/` cohort tree) -- "
            "not Buzz product surface, so never rows here",
            "any hidden or summarized-away state: there is no \"not "
            "examined\" disposition at all, and a `GAP` row is never dropped "
            "or converted to look accounted for",
        ],
        "ordering": (
            "accounting rows stable-sorted by (category, source_key) -- "
            "coverage.py's own output order; node links and aliases sorted "
            "within each row; findings sorted; no timestamps"
        ),
        "not_covered": [
            "Whether `coverage.py --strict` becomes a hard CI or validate "
            "gate -- that is #621's CI wiring decision, not this report's.",
            "Fixing any gap: a `GAP` row's remedy is a future documentation "
            "task, a human-recorded registry disposition, or teaching "
            "`inventory.py` about a new area -- never an edit to this "
            "generated file.",
        ],
        "unverified": [
            "The repository source tree outside the corpus (crates/, "
            "migrations/, desktop/, ...) is an additional input to this "
            "report that the input digest above does not cover -- the digest "
            "hashes canonical corpus nodes only, so unchanged corpus nodes "
            "with changed product source can yield different report content "
            "under the same digest.",
            "`build_coverage` discovers nodes via `validate.py`'s full walk, "
            "which includes generated views present on disk (the framework's "
            "canonical-input set excludes them); any coverage a generated "
            "view's citations earned would appear in the rows like any other "
            "node id.",
        ],
    }


def _extra_evidence(ctx):
    return [
        {
            "statement": (
                "The accounting rows were produced by coverage.py's "
                "build_coverage() (issue #634) over inventory.py's source "
                "inventory (issue #624) and validate.py's node discovery, "
                "with no manifest and no dispositions registry passed; "
                "completeness is claimed only when the report has zero GAP "
                "rows."
            ),
            "entry_class": "FACT",
            "evidence": [
                "launchpad/project-intelligence/corpus/coverage.py",
                "launchpad/project-intelligence/corpus/inventory.py",
            ],
        }
    ]


SPEC = {
    "name": "coverage",
    "output_path": "generated/coverage.md",
    "node_id": "generated-coverage",
    "title": "Coverage: generated corpus coverage report",
    "node_type": "governance",
    "audiences": ["agent", "developer", "reviewer"],
    "subject": (
        "the completeness accounting of every in-scope Buzz source item "
        "against the canonical corpus"
    ),
    "generate": _generate,
    "extra_evidence": _extra_evidence,
    "relationships": ({"type": "references", "target": "corpus-agents"},),
}
