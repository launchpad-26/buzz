"""Builder: generated/decision-index.md -- issue #895 (parent PRD #621).

A generated **stats/coverage view** over the ADR-numbered decision records under
``launchpad/decisions/`` -- how many exist, their status breakdown, and which of
them currently have zero canonical-node citations. This is deliberately NOT a
second copy of what ``decisions/INDEX.md`` already does.

Distinction from ``decisions/INDEX.md`` (node id ``decisions-index``, issue #845,
merged, builder ``index_defs/decisions_index.py``): that document lists, per
*cited* decision record, the full set of citing canonical node ids -- "which
nodes cite this record." This document instead counts and buckets every record
that exists on disk -- "how many records exist, what state are they in, and
which ones nothing cites yet" -- the same relationship the batch dispatch for
this task named between issue #891's ``generated-corpus-index`` (a stats view)
and issue #638's ``corpus-index.md`` INDEX (a full listing). The two documents
answer different questions and neither restates the other's content; each
states the distinction in its own body text (required section, below) so a
reader lands on the right one.

Two deterministic signals, both read directly from ``launchpad/decisions/``
rather than from any canonical corpus node:

1. **Status.** Every file matching ``ADR-####-*.md`` under
   ``launchpad/decisions/`` (``README.md`` is not ADR-numbered and is excluded)
   carries a free-text YAML ``status:`` front-matter field. This builder reads
   that field line directly (no full YAML parse -- the field is always a bare
   scalar on its own line at this revision) and buckets it: any value starting
   case-insensitively with ``Superseded`` groups under the single bucket
   ``Superseded``; every other raw value is its own bucket, verbatim, so an
   unanticipated future status renders honestly instead of being silently
   miscategorized into one of today's three observed buckets (``Accepted``,
   ``Proposed``, ``Superseded by ADR-####``).
2. **Citation coverage.** A decision record is "cited" iff some canonical
   node's front-matter ``evidence[].evidence`` citation string has a path part
   (before any ``#`` fragment) equal to ``launchpad/decisions/<that file's
   name>`` -- the identical matching rule ``decisions_index.py`` uses,
   recomputed here (builders are isolated modules; this one does not import a
   sibling) rather than restated as prose. Records with zero matches populate
   the coverage-gap table.

**Digest-uncovered input, disclosed rather than hidden.** ``launchpad/decisions/``
is not a canonical corpus input: ``GenerationContext`` never loads it (per
``decisions_index.py``'s own docstring) and ``ctx.input_digest`` does not cover
it. This builder reads it directly anyway, for the reason ``index_defs/
coverage.py`` (issue #892) already established as a precedent for a
digest-uncovered read: the alternative (folding decision-record bookkeeping
into a hand-authored node, or refusing to count records the corpus does not
canonically model) is worse than disclosing the gap. Following that precedent
exactly: an ``extra_evidence`` FACT entry names the read, and an ``unverified``
bullet in the rendered body states that an unchanged corpus digest can still
carry a changed decision-record count or status mix.

``node_type`` choice: ``governance``, following ``decisions_index.py``'s own
identical reasoning -- node.schema.json's type enum has no ``decision`` or
``index`` member, and this document's subject (the corpus's own decision-record
bookkeeping) is a governance concern, not a product surface.

Contract: module-level ``SPEC`` per indexes.py's IndexSpec; the framework
renders all front matter and the templates/generated-index.md body skeleton.
This module supplies only the subject-specific listing and the
inclusion/exclusion bullets.
"""

from __future__ import annotations

import re
from pathlib import Path

_DECISIONS_DIRNAME = "decisions"
_ADR_FILENAME_RE = re.compile(r"^ADR-\d{4}-.+\.md$")
_CORPUS_SUFFIX = ("launchpad", "docs", "corpus")
_DECISIONS_PATH_PREFIX = "launchpad/decisions/"


def _repo_root_for(corpus_root: Path) -> Path:
    """Repo root the decisions/ directory hangs off of. Mirrors coverage.py's
    (#892) own derivation exactly: when the corpus root is the real
    ``launchpad/docs/corpus`` layout (or a test fixture built the same way),
    the repo root is three levels up; otherwise the corpus root doubles as the
    repo root, so a bare fixture corpus stays hermetic."""
    resolved = corpus_root.resolve()
    if resolved.parts[-3:] == _CORPUS_SUFFIX:
        return resolved.parents[2]
    return resolved


def _adr_status(path: Path) -> str | None:
    """Read only the ``status:`` front-matter line, never the record's body or
    decision content. Returns None if no such line is found (never raises --
    an ADR file this builder cannot parse is a data question, not a crash)."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return None
    in_frontmatter = False
    for i, line in enumerate(text.splitlines()):
        if i == 0:
            if line.strip() != "---":
                return None
            in_frontmatter = True
            continue
        if not in_frontmatter:
            break
        if line.strip() == "---":
            break
        if line.startswith("status:"):
            return line[len("status:") :].strip()
    return None


def _status_bucket(raw: str | None) -> str:
    if not raw:
        return "(no status field)"
    if raw.lower().startswith("superseded"):
        return "Superseded"
    return raw


def _adr_records(repo_root: Path) -> list[tuple[str, str]]:
    """Sorted (repo-root-relative posix path, status bucket) for every
    ADR-numbered record under launchpad/decisions/. Never reads README.md or
    any other non-ADR-numbered file in that directory."""
    decisions_dir = repo_root / "launchpad" / _DECISIONS_DIRNAME
    if not decisions_dir.is_dir():
        return []
    records = []
    for path in sorted(decisions_dir.iterdir(), key=lambda p: p.name):
        if not path.is_file() or not _ADR_FILENAME_RE.match(path.name):
            continue
        rel_path = f"{_DECISIONS_PATH_PREFIX}{path.name}"
        records.append((rel_path, _status_bucket(_adr_status(path))))
    return sorted(records, key=lambda r: r[0])


def _cited_decision_paths(ctx) -> set[str]:
    """The set of launchpad/decisions/*.md paths cited by any canonical node's
    front-matter evidence -- the identical rule decisions_index.py (#845)
    uses, recomputed here rather than imported (builders are isolated
    modules)."""
    cited: set[str] = set()
    for node in ctx.valid_nodes:
        for entry in node.data.get("evidence") or []:
            if not isinstance(entry, dict):
                continue
            for citation in entry.get("evidence") or []:
                if not isinstance(citation, str):
                    continue
                path = citation.split("#", 1)[0]
                if path.startswith(_DECISIONS_PATH_PREFIX) and path.endswith(".md"):
                    cited.add(path)
    return cited


def _cell(text: str) -> str:
    return text.replace("|", "\\|")


def _generate(ctx):
    repo_root = _repo_root_for(ctx.corpus_root)
    records = _adr_records(repo_root)
    cited = _cited_decision_paths(ctx)

    total = len(records)
    cited_count = sum(1 for path, _ in records if path in cited)
    gap_count = total - cited_count

    bucket_counts: dict[str, int] = {}
    for _, bucket in records:
        bucket_counts[bucket] = bucket_counts.get(bucket, 0) + 1

    parts = [
        "## Distinction from `decisions/INDEX.md`",
        "",
        "This document is a **stats/coverage view**: how many ADR-numbered decision "
        "records exist under `launchpad/decisions/`, their status breakdown, and "
        "which currently have zero canonical-node citations. It is a different "
        "document from `decisions/INDEX.md` (node id `decisions-index`, issue #845), "
        "which lists, per *cited* decision record, the full set of citing canonical "
        "node ids. **Read `decisions/INDEX.md` to find which canonical nodes cite a "
        "given record; read this document for the count, status mix, and citation "
        "coverage gaps across all records.** Neither document restates the other's "
        "content.",
        "",
        "## Decision records by status",
        "",
        f"**{total} ADR-numbered decision record(s)** found under "
        "`launchpad/decisions/` at generation time.",
        "",
    ]
    if bucket_counts:
        parts.append("| Status bucket | Count |")
        parts.append("|---|---|")
        for bucket in sorted(bucket_counts):
            parts.append(f"| {_cell(bucket)} | {bucket_counts[bucket]} |")
    else:
        parts.append(
            "None -- no file under `launchpad/decisions/` matches the "
            "`ADR-####-*.md` filename pattern at this revision."
        )

    parts += [
        "",
        "## Citation coverage",
        "",
        f"{cited_count} of {total} decision record(s) are cited by at least one "
        "canonical corpus node's front-matter `evidence[].evidence` citation "
        f"strings; {gap_count} are cited by zero canonical nodes.",
        "",
        "## Coverage gaps: zero-citation decision records",
        "",
    ]
    gaps = [(path, bucket) for path, bucket in records if path not in cited]
    if gaps:
        parts.append(
            f"{len(gaps)} decision record(s) are not cited by any canonical "
            "node's front-matter evidence at this revision, sorted by path:"
        )
        parts.append("")
        parts.append("| Path | Status bucket |")
        parts.append("|---|---|")
        for path, bucket in gaps:
            parts.append(f"| `{path}` | {_cell(bucket)} |")
    else:
        parts.append(
            "None -- every ADR-numbered decision record under "
            "`launchpad/decisions/` is cited by at least one canonical node's "
            "front-matter evidence at this revision."
        )

    return {
        "sections": "\n".join(parts),
        "includes": (
            "every file directly under `launchpad/decisions/` whose name matches "
            "`ADR-####-*.md`, one entry in the status table and, when uncited, one "
            "row in the coverage-gap table",
            "a decision record's `status:` front-matter field, read as a bare "
            "scalar line and bucketed (any value starting case-insensitively with "
            "`Superseded` groups under one `Superseded` bucket; every other raw "
            "value is its own bucket, verbatim)",
            "citation coverage per record, using the same path-prefix-and-`.md`-"
            "suffix match against canonical front-matter evidence citations that "
            "`decisions_index.py` (issue #845) uses",
        ),
        "excludes": (
            "`launchpad/decisions/README.md`: not ADR-numbered, so it never "
            "matches the `ADR-####-*.md` filename pattern",
            "the content of any decision record -- only its filename and "
            "`status:` front-matter field are read; the decision text itself is "
            "never inspected or restated here",
            "which specific canonical node(s) cite a given record -- "
            "`decisions/INDEX.md` owns that per-record listing; this document "
            "carries counts only",
        ),
        "ordering": (
            "the status table is sorted by bucket label; the coverage-gap table "
            "is sorted by decision-record path"
        ),
        "not_covered": (
            "Which specific canonical node(s) cite a given decision record -- "
            "`decisions/INDEX.md` owns that per-record listing, not this "
            "document.",
            "The content, outcome, or rationale of any decision record -- "
            "`launchpad/decisions/` owns that.",
        ),
        "unverified": (
            "`ctx.input_digest` covers canonical corpus inputs only. "
            "`launchpad/decisions/` is read directly by this builder and is not "
            "part of that digest, so an unchanged corpus digest with an added, "
            "removed, or re-statused ADR record can change this report's "
            "content without moving the digest -- the identical disclosure "
            "`index_defs/coverage.py` (issue #892) makes for its own "
            "digest-uncovered repository read.",
            "Whether `status:` is a schema-enforced field on any decision "
            "record: `launchpad/decisions/` is not schema-validated corpus "
            "content, so a record with a missing or malformed `status:` line "
            "renders as the `(no status field)` bucket rather than failing.",
        ),
    }


def _extra_evidence(ctx):
    return [
        {
            "statement": (
                "The status breakdown and citation-coverage counts were "
                "produced by reading every launchpad/decisions/ADR-####-*.md "
                "filename and its status: front-matter field directly from "
                "disk (README.md excluded, not ADR-numbered), and by matching "
                "each canonical corpus node's front-matter "
                "evidence[].evidence citation strings (path part before any "
                "# fragment) against those filenames using the same rule "
                "decisions_index.py (issue #845) uses."
            ),
            "entry_class": "FACT",
            "evidence": [
                "launchpad/decisions/ADR-0001-handbook-repository-location-and-publication-target.md",
                "launchpad/project-intelligence/corpus/index_defs/decisions_index.py",
            ],
        }
    ]


SPEC = {
    "name": "decision-index",
    "output_path": "generated/decision-index.md",
    "node_id": "generated-decision-index",
    "title": "Decision index: generated decision-record stats and coverage",
    "node_type": "governance",
    "audiences": ("agent", "developer", "reviewer"),
    "subject": (
        "the status breakdown and citation-coverage bookkeeping of "
        "launchpad/decisions/ ADR records -- a stats/coverage view distinct "
        "from decisions/INDEX.md's per-record citing-node listing"
    ),
    "generate": _generate,
    "extra_evidence": _extra_evidence,
    "relationships": (
        {"type": "implements", "target": "corpus-template-generated-index"},
        {"type": "references", "target": "corpus-agents"},
    ),
}
