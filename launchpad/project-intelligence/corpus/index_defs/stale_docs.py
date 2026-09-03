"""Builder for generated/stale-docs.md -- issue #904 (parent PRD #621).

This document is an AUDIT REPORT, not an index: `templates/generated-index.md`
names `stale-docs.md` explicitly ("An audit report" / "Same reason as
`orphaned-docs.md`"), the same non-index-shaped-sibling boundary
`index_defs/orphaned_docs.py` (#902), `index_defs/dependency_graph.py` (#896),
`index_defs/coverage.py` (#892) and `index_defs/decision_index.py` (#895)
already establish for their own subjects.

**Subject.** Every node's `evidence` array is also its provenance ledger --
there is no separate provenance field (AGENTS.md, "Evidence, citations, and
what validation proves"). The revision a node was written against is recorded
there as a `commit <sha>`-shaped citation attached to a FACT such as "This node
was authored and checked against repository revision <sha>" (`corpus-agents`'
own first evidence entry is the worked example). This builder audits whether
that recorded revision still looks current, using exactly the deterministic
procedure AGENTS.md's own "Checking whether cited files moved" section already
documents and requires a corpus author to run by hand:

    git diff --name-only <recorded-sha> -- <the normalized file paths in the
    ledger>

That same section states the procedure's two hard limits, both honoured here
rather than re-derived by guesswork:

1. **Normalize first.** A file citation may carry a position (`path:1077` or
   `path:219-221`); those are not valid pathspecs. `coverage.py`'s
   `_node_file_citations(node)` (#892, merged) already strips the position and
   returns the bare path, so this builder reuses it verbatim instead of
   re-implementing the same normalization a second, possibly divergent way.
2. **Only three of CONTRACT.md's six citation shapes name an openable file at
   all** -- bare path, file line, file range. Graph edge, tool result, commit
   and both URL forms the validator additionally recognises do not, and are
   therefore untouched by any `git diff`. `_node_file_citations` already
   excludes exactly those non-file shapes (it mirrors
   `validate._classify_citation`'s own routing order), so this builder never
   passes a non-file citation to git.

AGENTS.md is explicit that the result "is a narrowing step, not a
certification: only re-verifying a claim against its source establishes that
the claim still holds." This builder does not overclaim past that: a node
whose cited files changed since its recorded revision is reported as
*possibly* stale, never as definitely wrong, and a node whose cited files did
not change is reported as carrying *no signal of staleness from this check*,
never as definitely current.

**Two sections, kept deliberately separate because they carry different
epistemic weight (per this task's own dispatch brief: do not fabricate
confidence in a staleness signal that cannot actually be verified
deterministically):**

1. **No revision-pinning FACT** (primary). Structurally deterministic, no git
   invocation needed at all: every valid node whose evidence ledger carries
   zero `commit <sha>`-shaped citations anywhere. A companion **Ambiguous
   revision** table lists nodes citing more than one *distinct* commit sha --
   nothing in this builder picks a winner among them; a node either has
   exactly one recorded revision to check against, or it does not, or it is
   ambiguous which one is authoritative.
2. **Commit-freshness comparison** (secondary, explicitly labeled
   best-effort). For the remaining nodes -- exactly one distinct recorded
   sha -- the builder shells out. Because this worktree's own repository is a
   shallow clone (`git rev-parse --is-shallow-repository` -> true, measured at
   this revision) a recorded sha can be real and correct yet simply
   unreachable from a shallow checkout; `git cat-file -e <sha>` is run FIRST,
   scoped to the repository root, and any sha that does not resolve locally
   lands in a "cannot verify locally" bucket -- never folded into "stale".
   Only a sha that resolves locally is ever passed to `git diff --name-only`.
   Every subprocess invocation is wrapped so a missing `git` binary, or a
   directory that is not inside any git repository at all (true of every
   from-scratch test fixture that does not `git init`), degrades this whole
   section to a stated limitation rather than crashing generation.

`_repo_root_for` (three levels up from a real `launchpad/docs/corpus` layout,
else the corpus root doubles as the repo root for a hermetic fixture) is
copied verbatim from `index_defs/orphaned_docs.py`'s own derivation, itself
copied from `index_defs/coverage.py`, for the identical reason: run git
against the real repository when rendering for real, and against a
self-contained fixture repository in tests.

**Digest-uncovered input, disclosed rather than hidden.** The commit-freshness
comparison reads live git history -- `git cat-file` / `git diff` against
`HEAD` and the working tree -- which `ctx.input_digest` (a hash over canonical
corpus Markdown only) does not cover, the identical disclosure
`index_defs/coverage.py` (#892), `index_defs/orphaned_docs.py` (#902) and
`index_defs/decision_index.py` (#895) already make for their own
digest-uncovered reads. An `extra_evidence` FACT entry names the read; an
`unverified` bullet in the rendered body states that an unchanged corpus
digest can still carry a different commit-freshness comparison if the
repository's git history moves.

`node_type` choice: `governance`, following `orphaned_docs.py`/
`dependency_graph.py`/`coverage.py`/`decision_index.py`'s identical reasoning
-- the subject is the corpus's own currency, a governance concern about the
corpus itself, not a product-surface type.

`relationships`: only `references -> corpus-agents`. `implements ->
corpus-template-generated-index` is deliberately NOT declared, mirroring
`orphaned_docs.py` -- the template's own boundary table names this document an
audit report, not an index, so claiming to implement the index template would
contradict its own text.
"""

from __future__ import annotations

import importlib.util
import re
import subprocess
import sys
from pathlib import Path

_COVERAGE_PATH = Path(__file__).resolve().parent.parent / "coverage.py"

# The sibling-load pattern index_defs/coverage.py and index_defs/orphaned_docs.py
# both use: cached under "corpus_coverage" so this builder, coverage.py's own
# sibling loads, and the test suite all share one module object -- and, through
# it, one shared `validate` module (coverage.py loads validate.py the same way).
_coverage = sys.modules.get("corpus_coverage")
if _coverage is None:
    _spec = importlib.util.spec_from_file_location("corpus_coverage", _COVERAGE_PATH)
    _coverage = importlib.util.module_from_spec(_spec)
    sys.modules["corpus_coverage"] = _coverage
    _spec.loader.exec_module(_coverage)

_validate = _coverage.validate

_CORPUS_SUFFIX = ("launchpad", "docs", "corpus")
_SHA_RE = re.compile(r"^commit\s+([0-9a-fA-F]{7,40})\b")
_GIT_TIMEOUT_SECONDS = 30


def _repo_root_for(corpus_root: Path) -> Path:
    """Repo root the git commands run against. Copied verbatim from
    index_defs/orphaned_docs.py's own derivation (itself copied from
    index_defs/coverage.py): three levels up from the real
    launchpad/docs/corpus layout, else the corpus root doubles as the repo
    root so a bare fixture corpus stays hermetic."""
    resolved = corpus_root.resolve()
    if resolved.parts[-3:] == _CORPUS_SUFFIX:
        return resolved.parents[2]
    return resolved


def _commit_shas(node) -> set[str]:
    """Every distinct sha named by a `commit <sha>`-shaped citation anywhere in
    one node's evidence ledger, matched by validate.py's own classifier shape
    (`_COMMIT_CITATION_RE`) so this builder cannot silently disagree with what
    the validator itself would call a commit reference."""
    shas: set[str] = set()
    for entry in node.data.get("evidence") or []:
        if not isinstance(entry, dict):
            continue
        for citation in entry.get("evidence") or []:
            if not isinstance(citation, str):
                continue
            text = citation.strip()
            if _validate._COMMIT_CITATION_RE.match(text):
                match = _SHA_RE.match(text)
                if match:
                    shas.add(match.group(1))
    return shas


def _run_git(args: list[str], repo_root: Path) -> tuple[bool, str]:
    """Run one git subprocess scoped to repo_root. Returns (ok, stdout).
    Any failure -- non-git-repo working directory, missing sha, missing `git`
    binary, or a timeout -- is folded into `ok=False` rather than raised, so a
    single bad or unreachable commit degrades this builder's secondary section
    gracefully instead of crashing generation."""
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=repo_root,
            capture_output=True,
            text=True,
            timeout=_GIT_TIMEOUT_SECONDS,
        )
    except (OSError, subprocess.TimeoutExpired):
        return False, ""
    return result.returncode == 0, result.stdout


def _sha_resolves_locally(sha: str, repo_root: Path) -> bool:
    ok, _ = _run_git(["cat-file", "-e", sha], repo_root)
    return ok


def _changed_paths_since(sha: str, paths: list[str], repo_root: Path) -> tuple[bool, list[str]]:
    """(command_ok, sorted changed paths) for `git diff --name-only <sha> --
    <paths>`, scoped to repo_root. command_ok is False only when the git
    invocation itself failed (not when it ran and found zero changes)."""
    ok, stdout = _run_git(["diff", "--name-only", sha, "--", *paths], repo_root)
    if not ok:
        return False, []
    changed = sorted({line.strip() for line in stdout.splitlines() if line.strip()})
    return True, changed


def _cell(text: str) -> str:
    return text.replace("|", "\\|")


class _Classified:
    """One valid node's classification, computed once and reused by both
    `_generate` and `_extra_evidence` for the same `ctx` (the per-process cache
    below keys on `id(ctx)`, the identical pattern `orphaned_docs.py` uses for
    its own expensive `coverage.build_coverage()` call)."""

    __slots__ = (
        "node_id",
        "path",
        "bucket",
        "sha",
        "distinct_shas",
        "changed_paths",
        "checked_paths",
    )

    def __init__(self, node_id, path, bucket, sha=None, distinct_shas=None, changed_paths=None, checked_paths=None):
        self.node_id = node_id
        self.path = path
        self.bucket = bucket
        self.sha = sha
        self.distinct_shas = distinct_shas or ()
        self.changed_paths = changed_paths or ()
        self.checked_paths = checked_paths or ()


_CLASSIFICATION_CACHE: dict[int, list[_Classified]] = {}


def _classify_all(ctx) -> list[_Classified]:
    cached = _CLASSIFICATION_CACHE.get(id(ctx))
    if cached is not None:
        return cached

    repo_root = _repo_root_for(ctx.corpus_root)
    results: list[_Classified] = []
    for node in ctx.valid_nodes:
        if not isinstance(node.id, str):
            continue
        path = ctx.rel_path(node)
        shas = _commit_shas(node)

        if not shas:
            results.append(_Classified(node.id, path, "no_revision"))
            continue
        if len(shas) > 1:
            results.append(
                _Classified(
                    node.id, path, "ambiguous_revision", distinct_shas=tuple(sorted(shas))
                )
            )
            continue

        sha = next(iter(shas))
        if not _sha_resolves_locally(sha, repo_root):
            results.append(_Classified(node.id, path, "unresolvable", sha=sha))
            continue

        citations = _coverage._node_file_citations(node)
        checked_paths = sorted({p for p, _s, _e in citations if p})
        if not checked_paths:
            results.append(_Classified(node.id, path, "no_file_citations", sha=sha))
            continue

        command_ok, changed = _changed_paths_since(sha, checked_paths, repo_root)
        if not command_ok:
            results.append(_Classified(node.id, path, "unresolvable", sha=sha))
        elif changed:
            results.append(
                _Classified(
                    node.id,
                    path,
                    "possibly_stale",
                    sha=sha,
                    changed_paths=tuple(changed),
                    checked_paths=tuple(checked_paths),
                )
            )
        else:
            results.append(
                _Classified(
                    node.id, path, "fresh", sha=sha, checked_paths=tuple(checked_paths)
                )
            )

    results.sort(key=lambda c: c.node_id)
    _CLASSIFICATION_CACHE[id(ctx)] = results
    return results


def _no_revision_section(classified: list[_Classified]) -> list[str]:
    lines = ["### No revision-pinning FACT", ""]
    lines.append(
        "Every valid canonical node whose `evidence` ledger carries zero "
        "`commit <sha>`-shaped citations (matched by `validate.py`'s own "
        "`_COMMIT_CITATION_RE`). Structurally deterministic -- no git "
        "invocation is needed to compute this section, only the node's own "
        "front matter. This is a structural risk, not proof that the node's "
        "content is actually stale: it means no revision was recorded to "
        "check freshness against in the first place."
    )
    lines.append("")
    rows = [c for c in classified if c.bucket == "no_revision"]
    if rows:
        lines += ["| Node id | Path |", "|---|---|"]
        for c in rows:
            lines.append(f"| {c.node_id} | `{_cell(c.path)}` |")
    else:
        lines.append(
            "None at this revision -- every valid canonical node carries at "
            "least one commit citation."
        )
    return lines


def _ambiguous_revision_section(classified: list[_Classified]) -> list[str]:
    lines = ["### Ambiguous revision", ""]
    lines.append(
        "Valid canonical nodes citing more than one *distinct* `commit "
        "<sha>` value across their evidence ledger. Nothing in this builder "
        "picks a winner among them -- reported so a human can decide which "
        "recorded revision (if either) is authoritative, never resolved "
        "automatically."
    )
    lines.append("")
    rows = [c for c in classified if c.bucket == "ambiguous_revision"]
    if rows:
        lines += ["| Node id | Path | Distinct commit shas |", "|---|---|---|"]
        for c in rows:
            shas = ", ".join(f"`{s}`" for s in c.distinct_shas)
            lines.append(f"| {c.node_id} | `{_cell(c.path)}` | {shas} |")
    else:
        lines.append(
            "None at this revision -- no valid canonical node cites more "
            "than one distinct commit."
        )
    return lines


def _bucket_table(
    classified: list[_Classified], bucket: str, heading: str, columns: list[str], row_fn
) -> list[str]:
    lines = [f"#### {heading}", ""]
    rows = [c for c in classified if c.bucket == bucket]
    if rows:
        lines.append("| " + " | ".join(columns) + " |")
        lines.append("|" + "|".join("---" for _ in columns) + "|")
        for c in rows:
            lines.append(row_fn(c))
    else:
        lines.append(f"None at this revision in this bucket.")
    lines.append("")
    return lines


def _freshness_section(classified: list[_Classified]) -> list[str]:
    checked = [
        c
        for c in classified
        if c.bucket in ("unresolvable", "no_file_citations", "possibly_stale", "fresh")
    ]
    possibly_stale = [c for c in checked if c.bucket == "possibly_stale"]
    fresh = [c for c in checked if c.bucket == "fresh"]
    unresolvable = [c for c in checked if c.bucket == "unresolvable"]
    no_files = [c for c in checked if c.bucket == "no_file_citations"]

    lines = ["### Commit-freshness comparison (best-effort)", ""]
    lines.append(
        "**This section is a narrowing step, not a certification** -- the "
        "identical framing AGENTS.md's own \"Checking whether cited files "
        "moved\" section states for the procedure this builder automates: "
        "`git diff --name-only <recorded-sha> -- <normalized file paths>`. A "
        "node landing in \"possibly stale\" below has at least one cited "
        "file that changed since its recorded revision -- that does not by "
        "itself establish the node's claim is now wrong, only that the "
        "underlying file moved. A node landing in \"no signal of staleness\" "
        "has had none of its cited files change -- that does not establish "
        "the claim still holds, only that this narrow check found nothing."
    )
    lines.append("")
    lines.append(
        f"Of {len(classified)} valid canonical node(s): "
        f"**{len(possibly_stale)}** possibly stale, **{len(fresh)}** with no "
        f"signal of staleness, **{len(unresolvable)}** whose recorded "
        f"revision could not be verified locally, **{len(no_files)}** with "
        "no other file citation to compare against."
    )
    lines.append("")

    def _possibly_stale_row(c: _Classified) -> str:
        changed = ", ".join(f"`{_cell(p)}`" for p in c.changed_paths)
        return f"| {c.node_id} | `{_cell(c.path)}` | `{c.sha}` | {changed} |"

    lines += _bucket_table(
        classified,
        "possibly_stale",
        "Possibly stale -- at least one cited file changed since the recorded revision",
        ["Node id", "Path", "Recorded commit", "Changed cited path(s)"],
        _possibly_stale_row,
    )

    def _fresh_row(c: _Classified) -> str:
        return (
            f"| {c.node_id} | `{_cell(c.path)}` | `{c.sha}` | "
            f"{len(c.checked_paths)} |"
        )

    lines += _bucket_table(
        classified,
        "fresh",
        "No signal of staleness -- none of the cited files changed since the recorded revision",
        ["Node id", "Path", "Recorded commit", "Cited paths checked"],
        _fresh_row,
    )

    def _unresolvable_row(c: _Classified) -> str:
        return f"| {c.node_id} | `{_cell(c.path)}` | `{c.sha}` |"

    lines += _bucket_table(
        classified,
        "unresolvable",
        "Cannot verify locally -- the recorded commit does not resolve in this checkout",
        ["Node id", "Path", "Recorded commit"],
        _unresolvable_row,
    )
    lines.append(
        "A recorded commit failing to resolve locally is not evidence of "
        "staleness by itself -- this worktree's repository is a shallow "
        "clone, so an older, entirely valid revision can be genuinely "
        "unreachable from it, or the `git` binary/working tree can be "
        "unavailable to this generator run. Either way, this builder never "
        "folds an unresolvable commit into \"possibly stale\"."
    )
    lines.append("")

    def _no_files_row(c: _Classified) -> str:
        return f"| {c.node_id} | `{_cell(c.path)}` | `{c.sha}` |"

    lines += _bucket_table(
        classified,
        "no_file_citations",
        "No other file citation to compare -- nothing for git to check besides the revision itself",
        ["Node id", "Path", "Recorded commit"],
        _no_files_row,
    )
    return lines


def _generate(ctx):
    classified = _classify_all(ctx)

    lines: list[str] = []
    lines.append("## Stale-docs audit")
    lines.append("")
    lines += _no_revision_section(classified)
    lines.append("")
    lines += _ambiguous_revision_section(classified)
    lines.append("")
    lines += _freshness_section(classified)

    no_revision_count = sum(1 for c in classified if c.bucket == "no_revision")
    ambiguous_count = sum(1 for c in classified if c.bucket == "ambiguous_revision")

    return {
        "sections": "\n".join(lines),
        "includes": [
            "every valid canonical node with zero `commit <sha>`-shaped "
            "evidence citations (`validate._COMMIT_CITATION_RE`), in the "
            "'No revision-pinning FACT' table",
            "every valid canonical node citing more than one distinct "
            "commit sha, in the 'Ambiguous revision' table",
            "for every remaining node (exactly one distinct recorded "
            "commit), the result of `git cat-file -e <sha>` scoped to the "
            "repository root, then -- only if that resolves locally -- "
            "`git diff --name-only <sha> -- <cited paths>` over the node's "
            "other openable file citations, reused verbatim from "
            "`coverage.py`'s `_node_file_citations`",
        ],
        "excludes": [
            "graph-edge, tool-result, commit and URL citations from the "
            "freshness comparison -- only bare path, file line and file "
            "range citations name an openable file, per CONTRACT.md's six "
            "shapes and AGENTS.md's own stated limits",
            "any claim that a 'possibly stale' node's FACT is now actually "
            "false, or that a 'no signal of staleness' node's FACT still "
            "holds -- both would overclaim past what a `git diff` "
            "establishes, which AGENTS.md itself calls 'a narrowing step, "
            "not a certification'",
            "picking a single authoritative sha for a node citing more than "
            "one -- reported as ambiguous instead",
        ],
        "ordering": (
            "every table is sorted by node id; the 'Distinct commit shas' "
            "and 'Changed cited path(s)' cells are each sorted lists"
        ),
        "not_covered": [
            "Fixing any individual missing, ambiguous or possibly-stale "
            "revision -- a future authoring task, never an edit to this "
            "generated file.",
            "Re-verifying whether a flagged node's claims still hold against "
            "their sources -- only a human reading the source establishes "
            "that, per AGENTS.md's own 'Three things a passing run does not "
            "mean'.",
        ],
        "unverified": [
            "`ctx.input_digest` covers canonical corpus inputs only. The "
            "commit-freshness comparison reads live git history (`git "
            "cat-file`, `git diff` against the working tree) via subprocess "
            "calls scoped to the repository root, which that digest does "
            "not cover -- an unchanged corpus digest can still carry a "
            "different commit-freshness comparison if the repository's git "
            "history moves, the identical disclosure `index_defs/"
            "coverage.py` (#892), `index_defs/orphaned_docs.py` (#902) and "
            "`index_defs/decision_index.py` (#895) already make for their "
            "own digest-uncovered reads.",
            f"This worktree's repository is a shallow clone; "
            f"{no_revision_count} node(s) recorded no revision at all and "
            f"{ambiguous_count} recorded more than one distinct revision -- "
            "neither condition is checked further by the freshness "
            "comparison, and the 'cannot verify locally' bucket can grow on "
            "a shallower or more recent clone even with no corpus content "
            "change at all.",
        ],
    }


def _extra_evidence(ctx):
    # generate(ctx) always runs before extra_evidence(ctx) (render_document
    # builds the body first), so the classification is already cached under
    # this ctx's identity -- no second, expensive subprocess sweep.
    classified = _classify_all(ctx)
    no_revision = sum(1 for c in classified if c.bucket == "no_revision")
    ambiguous = sum(1 for c in classified if c.bucket == "ambiguous_revision")
    possibly_stale = sum(1 for c in classified if c.bucket == "possibly_stale")
    fresh = sum(1 for c in classified if c.bucket == "fresh")
    unresolvable = sum(1 for c in classified if c.bucket == "unresolvable")
    no_files = sum(1 for c in classified if c.bucket == "no_file_citations")
    return [
        {
            "statement": (
                f"At input digest sha256:{ctx.input_digest}, of "
                f"{len(classified)} valid canonical node(s): {no_revision} "
                f"carry no commit-shaped evidence citation, {ambiguous} "
                "carry more than one distinct commit sha, and of the "
                f"remainder {possibly_stale} have at least one cited file "
                f"changed since their recorded revision (`git diff "
                f"--name-only <sha> -- <cited paths>`), {fresh} have none "
                f"changed, {unresolvable} record a commit that does not "
                f"resolve locally in this (shallow) checkout via `git "
                f"cat-file -e`, and {no_files} record a revision but cite "
                "no other openable file to compare against."
            ),
            "entry_class": "FACT",
            "evidence": [
                "launchpad/project-intelligence/corpus/indexes.py",
                "launchpad/project-intelligence/corpus/validate.py",
                "launchpad/project-intelligence/corpus/coverage.py",
            ],
        },
        {
            "statement": (
                "AGENTS.md's 'Checking whether cited files moved' section "
                "states the exact procedure this builder automates (`git "
                "diff --name-only <recorded-sha> -- <normalized file "
                "paths>`) and calls its result 'a narrowing step, not a "
                "certification.'"
            ),
            "entry_class": "FACT",
            "evidence": ["launchpad/docs/corpus/AGENTS.md"],
        },
    ]


SPEC = {
    "name": "stale-docs",
    "output_path": "generated/stale-docs.md",
    "node_id": "generated-stale-docs",
    "title": "Stale docs: generated revision-currency audit report",
    "node_type": "governance",
    "audiences": ("agent", "developer", "reviewer"),
    "subject": (
        "an audit of the corpus's own recorded revisions -- which valid "
        "canonical nodes carry no (or an ambiguous) commit-shaped "
        "provenance citation, and, for the rest, a best-effort git-based "
        "comparison of whether the files each node cites elsewhere in its "
        "own evidence have changed since that recorded revision"
    ),
    "generate": _generate,
    "extra_evidence": _extra_evidence,
    "relationships": ({"type": "references", "target": "corpus-agents"},),
}
