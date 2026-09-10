"""Deterministic regeneration reporting -- issue #559, parent Feature #534,
parent PRD #602.

Given a repository revision range, joins `impact.py` (#635) and `stale.py`
(#556) -- neither re-implemented here -- to report, for every node
`impact.py` names as impacted:

- per evidence-entry route-2 eligibility (`standards/provenance.md` MUST 3's
  second route) against that node's own recorded revision, and
- a node-level revision disposition: `may-move` only when EVERY claim in the
  node's FULL ledger (not only the claims this change's diff touched) is
  route-2 clean, else `must-not-move (MUST 4)`.

This is the deterministic half of "regeneration" only. The tool can never
establish MUST 3 route 1 (a human re-reading a source and confirming a claim
still holds) -- so it never claims to. `may-move` is a conservative,
mechanically-checkable finding, not a verdict that a node's content is
correct.

This module does NOT:

- re-anchor a drifted citation's line range. Locating where a cited range
  moved to is not deterministic in general, and guessing would silently
  produce a citation pointing at the wrong code -- worse than the drift it
  fixed. `corpus-maintain` (a human or agent under that skill) does this by
  opening the file, per #559's own STEP 5.
- rewrite a statement whose meaning changed. That is authoring
  (`corpus-author`, a different skill under a different issue), and #559's
  Out of scope refuses it.
- create a node for a coverage gap. Reported, never filled --
  `corpus-maintain`'s own rule.
- open a pull request. The Feature #534 PR is opened by the documented
  AGENTS.md section 6 flow; wiring `gh pr create` into a corpus tool would
  collide with the pr-gate hook, DCO, and ADR-0054's one-Feature-one-PR rule.

`--apply` performs the one write this tool can honestly make: rewriting a
`may-move` node's own recorded-revision entry (the entry
`stale.extract_recorded_revision` resolved the node's recorded SHA from) to
the new head. It is a TARGETED TEXTUAL SUBSTITUTION of that entry's own two
lines -- its `statement` line and its `commit <sha>` citation line -- located
by entry POSITION, never by searching the file for the SHA's text. The old
SHA is commonly cited again elsewhere in the same node as an unrelated,
genuinely historical citation (measured: 88 of 226 real corpus nodes,
including one of #559's own two demonstration nodes, whose entry citing the
same SHA as a `tool_result` is a true "as of commit X" claim that must NOT
change). A global string/regex replace of the old SHA would silently corrupt
that unrelated citation into a false claim, and nothing in `validate.py`
would catch it. Every other byte of the file is left untouched, and the
node's `id` is never touched (MUST 5) -- this is a line-scoped textual edit,
never a YAML round-trip, which would reformat the whole ledger and make the
diff unreviewable.

Before any write, `--apply` refuses if the current branch is this
repository's default branch (`launchpad`). Nothing on GitHub enforces this --
`gh api repos/launchpad-26/buzz/rulesets` / `.../rules/branches/launchpad`
both return `[]` and `.../branches/launchpad/protection` returns `404` (all
re-verified for #559) -- so the refusal has to be this tool's own.

Run:  python3 launchpad/project-intelligence/corpus/regenerate.py --base <rev>
      --head <rev> [--root PATH] [--repo-dir PATH] [--out PATH]
      [--format json|text] [--apply]
  or: python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

# impact.py lives in this same directory and isn't a package (no
# __init__.py -- this repo's existing project-intelligence/ convention), so
# it's loaded by path, the same way impact.py itself loads stale.py, and
# stale.py loads validate.py. Loading impact.py (rather than stale.py
# directly) gives this module impact.compute_impact for the impacted set,
# plus impact.stale and impact.validate transitively -- one by-path load
# reaches all three sibling modules without a second load of any of them.
_CORPUS_DIR = Path(__file__).resolve().parent
_impact_spec = importlib.util.spec_from_file_location("corpus_impact", _CORPUS_DIR / "impact.py")
impact = importlib.util.module_from_spec(_impact_spec)
sys.modules.setdefault("corpus_impact", impact)
_impact_spec.loader.exec_module(impact)

stale = impact.stale
validate = impact.validate

DEFAULT_ROOT = validate.DEFAULT_ROOT
DEFAULT_BRANCH = "launchpad"


def _run_git(args: list[str], repo_dir: Path) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=repo_dir, capture_output=True, text=True)


def current_branch(repo_dir: Path) -> str:
    return _run_git(["rev-parse", "--abbrev-ref", "HEAD"], repo_dir).stdout.strip()


def resolve_full_sha(ref: str, repo_dir: Path) -> str | None:
    """The full 40-character commit SHA `ref` names, or `None` if `ref`
    cannot be resolved to a commit in this repository.

    Needed because `--head` (like `stale.py`'s `--head`) accepts any git ref
    -- `HEAD`, a branch name, a short SHA -- but a recorded-revision entry
    must always name a full 40-character SHA, never a symbolic ref that will
    mean something different tomorrow.
    """
    result = _run_git(["rev-parse", "--verify", f"{ref}^{{commit}}"], repo_dir)
    if result.returncode != 0:
        return None
    return result.stdout.strip()


# ---------------------------------------------------------------------------
# Route-2 classification -- MUST 3's second route, per claim (evidence entry)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ClaimRoute2:
    """One evidence entry's route-2 classification against a node's own
    recorded revision.

    `status` is one of:
      - "clean"  -- every citation on this claim is file-naming, and none of
        them changed between the recorded revision and head.
      - "dirty"  -- every citation is file-naming, but at least one changed
        (or could not be confirmed unchanged -- see `classify_claim`).
      - "closed" -- at least one citation on this claim is not file-naming
        (a commit reference, a graph edge, a tool result, or either URL
        form), so route 2 cannot run for this claim at all.
    """

    entry_index: int
    status: str
    reason: str


def classify_claim(
    entry_index: int,
    citations: list[str],
    recorded_sha: str,
    head: str,
    repo_dir: Path,
) -> ClaimRoute2:
    """Classify one evidence entry's route-2 eligibility.

    Two passes, deliberately in this order: first every citation is checked
    for SHAPE (file-naming or not) -- a single non-file citation closes route
    2 for the whole claim regardless of what the other citations say. Only
    when every citation is file-naming does the second pass ask whether any
    of them changed.

    Reuses `stale.normalize_file_citation` (position suffix stripped before
    the path reaches git -- the ":127 matches nothing and exits 0" trap),
    `stale.path_exists_at_revision` (an empty diff for a path that never
    existed at the recorded revision is indistinguishable from "unchanged";
    treated as NOT clean, conservatively, rather than trusted as clean) and
    `stale.diff_touched` -- none re-implemented here.
    """
    if not citations:
        return ClaimRoute2(entry_index, "clean", "no citations to check")

    normalized_paths: list[str] = []
    for citation in citations:
        normalized = stale.normalize_file_citation(citation)
        if normalized is None:
            return ClaimRoute2(
                entry_index,
                "closed",
                "at least one citation is non-file (commit reference, graph "
                "edge, tool result, or URL) -- route 2 cannot run for this claim",
            )
        normalized_paths.append(normalized)

    dirty_reasons: list[str] = []
    for path in normalized_paths:
        if not stale.path_exists_at_revision(recorded_sha, path, repo_dir):
            dirty_reasons.append(
                f"{path} does not resolve at the recorded revision -- an "
                "empty diff would be indistinguishable from unchanged"
            )
            continue
        if stale.diff_touched(recorded_sha, head, path, repo_dir):
            dirty_reasons.append(f"{path} changed between the recorded revision and head")

    if dirty_reasons:
        return ClaimRoute2(entry_index, "dirty", "; ".join(dirty_reasons))

    return ClaimRoute2(entry_index, "clean", "unchanged between the recorded revision and head")


# ---------------------------------------------------------------------------
# Recorded-revision entry location -- for --apply's line-scoped rewrite only.
# Never used to derive the SHA itself; `stale.extract_recorded_revision`
# already does that. This only answers "which entry, by position".
# ---------------------------------------------------------------------------


def locate_recorded_revision_entry(node: "validate.LoadedNode", sha: str) -> int:
    """The 1-based evidence-entry index of the entry `sha` was resolved from.

    Mirrors `stale.extract_recorded_revision`'s two rungs -- reusing its own
    module-level regexes (`stale._RECORDED_REVISION_STATEMENT_RE`,
    `stale._COMMIT_CITATION_RE`), never a second copy of the pattern -- but
    returns a POSITION instead of a SHA, which `extract_recorded_revision`'s
    public signature does not expose and `--apply`'s line-scoped rewrite
    needs. Raises `ValueError`, never guesses, if the position cannot be
    pinned to exactly one entry: this is the exact scoping boundary the
    corruption risk (a SHA cited again elsewhere in the same node) depends
    on being unambiguous.
    """
    entries = node.data.get("evidence") or []

    rung1 = [
        index
        for index, entry in enumerate(entries, start=1)
        if isinstance(entry, dict)
        and isinstance(entry.get("statement"), str)
        and (match := stale._RECORDED_REVISION_STATEMENT_RE.search(entry["statement"]))
        and match.group(1).lower() == sha.lower()
    ]
    if len(rung1) == 1:
        return rung1[0]

    rung2: list[int] = []
    for index, entry in enumerate(entries, start=1):
        if not isinstance(entry, dict):
            continue
        for citation in entry.get("evidence") or []:
            if not isinstance(citation, str):
                continue
            match = stale._COMMIT_CITATION_RE.match(citation.strip())
            if match and len(match.group(1)) == 40 and match.group(1).lower() == sha.lower():
                rung2.append(index)
                break
    if len(rung2) == 1:
        return rung2[0]

    raise ValueError(
        f"cannot pin a single recorded-revision entry position for {node.id} "
        f"(sha {sha}): {len(rung1)} statement match(es), {len(rung2)} commit-"
        "citation entry match(es) -- refusing to guess"
    )


def _end_of_evidence_item(lines: list[str], after_index: int) -> int:
    """The line index one past the current top-level evidence-list item,
    starting the search at `after_index`: either the next unindented
    front-matter key (e.g. `relationships:`), the closing `---` delimiter,
    or end of file -- whichever comes first.
    """
    for index in range(after_index, len(lines)):
        line = lines[index]
        stripped = line.rstrip("\n")
        if stripped == "---":
            return index
        if line and not line[0].isspace() and ":" in line:
            return index
    return len(lines)


def apply_revision_move(path: Path, entry_index: int, old_sha: str, new_sha: str) -> None:
    """Rewrite ONLY the recorded-revision entry's statement line and its
    `commit <sha>` citation line, in place, byte-identical everywhere else.

    Entry boundaries are found by position -- every real corpus node's
    evidence list starts each item with `  - statement:` at 2-space
    indentation (this repository's consistent authoring convention, the same
    one `write_node` in this package's own test fixtures reproduces) -- never
    by searching the file for `old_sha`'s text. This is what keeps an
    unrelated citation of the same SHA elsewhere in the node (measured: 88 of
    226 real nodes) untouched.
    """
    text = path.read_text()
    lines = text.splitlines(keepends=True)

    starts = [index for index, line in enumerate(lines) if line.startswith("  - statement:")]
    if entry_index > len(starts) or entry_index < 1:
        raise ValueError(f"evidence entry {entry_index} not found in {path}")
    start = starts[entry_index - 1]
    end = starts[entry_index] if entry_index < len(starts) else _end_of_evidence_item(lines, start + 1)

    statement_index = start
    if old_sha not in lines[statement_index]:
        raise ValueError(
            f"recorded-revision entry {entry_index} in {path} does not carry "
            f"{old_sha} on its statement line -- refusing to guess which line to rewrite"
        )

    citation_pattern = re.compile(
        r'^(\s*-\s*")commit\s+' + re.escape(old_sha) + r'("\s*)$', re.IGNORECASE
    )
    citation_index = None
    for index in range(start, end):
        if citation_pattern.match(lines[index]):
            citation_index = index
            break
    if citation_index is None:
        raise ValueError(
            f"recorded-revision entry {entry_index} in {path} has no `commit "
            f"{old_sha}` citation line -- refusing to guess which line to rewrite"
        )

    lines[statement_index] = lines[statement_index].replace(old_sha, new_sha)
    lines[citation_index] = lines[citation_index].replace(old_sha, new_sha)
    path.write_text("".join(lines))


# ---------------------------------------------------------------------------
# Report shape
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Triggering:
    changed_path: str | None
    evidence_entry_index: int | None


@dataclass
class NodeReport:
    node_id: object
    recorded_revision: str | None
    disposition: str  # "may-move" | "must-not-move (MUST 4)"
    triggering: list[Triggering] = field(default_factory=list)
    claims: list[ClaimRoute2] = field(default_factory=list)
    blocking: list[int] = field(default_factory=list)
    applied: bool = False
    new_revision: str | None = None


@dataclass
class RegenerateReport:
    nodes: list[NodeReport] = field(default_factory=list)
    coverage_gaps: "impact.CoverageGaps" = field(default_factory=impact.CoverageGaps)
    unreadable_nodes: list["impact.UnreadableNode"] = field(default_factory=list)

    def to_json(self) -> str:
        payload = {
            "nodes": [
                {
                    "node_id": node.node_id,
                    "recorded_revision": node.recorded_revision,
                    "disposition": node.disposition,
                    "applied": node.applied,
                    "new_revision": node.new_revision,
                    "triggering": [
                        {
                            "changed_path": row.changed_path,
                            "evidence_entry_index": row.evidence_entry_index,
                        }
                        for row in node.triggering
                    ],
                    "claims": [
                        {
                            "evidence_entry_index": claim.entry_index,
                            "status": claim.status,
                            "reason": claim.reason,
                        }
                        for claim in sorted(node.claims, key=lambda c: c.entry_index)
                    ],
                    "blocking": sorted(node.blocking),
                }
                for node in sorted(self.nodes, key=lambda n: str(n.node_id))
            ],
            "coverage_gaps": {
                "paths": sorted(self.coverage_gaps.paths),
                "redacted_count": self.coverage_gaps.redacted_count,
                "by_area": dict(sorted(self.coverage_gaps.by_area.items())),
            },
            "unreadable_nodes": [
                {"label": u.label, "error": u.error}
                for u in sorted(self.unreadable_nodes, key=lambda u: u.label)
            ],
        }
        return json.dumps(payload, indent=2, sort_keys=True) + "\n"

    def to_text(self) -> str:
        lines: list[str] = []
        for node in sorted(self.nodes, key=lambda n: str(n.node_id)):
            if node.applied:
                revision = f"moved to {node.new_revision} (MUST 3 route 2)"
            elif node.disposition == "may-move":
                revision = "eligible to move (MUST 3 route 2 clear on every claim) -- not moved, re-run with --apply"
            else:
                blockers = ", ".join(str(index) for index in sorted(node.blocking)) or "none named"
                revision = f"unmoved (MUST 4) -- blocking claim(s): {blockers}"

            triggers = node.triggering or [Triggering(None, None)]
            for trigger in triggers:
                path_label = trigger.changed_path or "(propagated, no direct changed path)"
                entry_label = (
                    f"evidence entry {trigger.evidence_entry_index}"
                    if trigger.evidence_entry_index is not None
                    else "(no direct evidence entry)"
                )
                lines.append(f"{node.node_id}  {path_label}  {entry_label}  revision: {revision}")

        lines.append("")
        lines.append(
            f"COVERAGE GAPS  {len(self.coverage_gaps.paths)} path(s), "
            f"{self.coverage_gaps.redacted_count} redacted"
        )
        for area, count in sorted(self.coverage_gaps.by_area.items()):
            lines.append(f"  {area}: {count}")

        if self.unreadable_nodes:
            lines.append("")
            lines.append(f"UNREADABLE NODES  {len(self.unreadable_nodes)}")
            for node in sorted(self.unreadable_nodes, key=lambda u: u.label):
                lines.append(f"  {node.label}: {node.error}")

        return "\n".join(lines) + "\n"


def evaluate_node(
    node: "validate.LoadedNode",
    head: str,
    repo_dir: Path,
    triggering: list[Triggering],
) -> NodeReport:
    """One impacted node's full disposition: every non-recorded-revision
    claim in its ledger classified via route 2, and the node-level
    `may-move` / `must-not-move (MUST 4)` disposition that follows.

    The recorded-revision entry itself is excluded from claim classification
    (located by `locate_recorded_revision_entry`) -- the same exclusion
    `stale.evaluate_citation` already makes for its own findings ("AGENTS.md
    states it does not count against the check"). Once the recorded revision
    is resolved via `stale.extract_recorded_revision`, that resolution --
    never a second, independent derivation -- is what this function trusts.

    Before any per-claim diff, one node-level gate runs first -- reusing
    `stale.commit_exists`, not a second copy of that check. Skipping it would
    reopen the exact trap AGENTS.md documents for this checkout: `git diff`
    against a SHA this repository never fetched (a shallow clone, or CI's
    depth-1 checkout) exits non-zero, but `classify_claim`'s `diff_touched`
    call reads only stdout, so a failed diff and a genuinely empty
    (unchanged) diff would be indistinguishable without this gate -- every
    claim would misread as "clean" and the node would wrongly report
    `may-move`. `commit_exists` failing means "cannot establish", which
    resolves to MUST 4, the same conservative default `stale.py` uses for the
    identical failure.

    Deliberately NOT gated on `stale.is_ancestor`, unlike `stale.py`'s own
    node-level gate 2. That gate exists there to protect `git log
    sha..head` (`last_touch_revision`), the merge-base-relative RANGE form
    that genuinely does go quietly empty for a non-ancestor `sha` (ADR-0004's
    documented trap). `classify_claim` never calls that form -- `diff_touched`
    and `path_exists_at_revision` both take `sha` and `head` as two
    POSITIONAL revisions (`git diff sha head -- path`, `git cat-file -e
    sha:path`), a literal two-tree comparison that is well-defined and
    ancestry-agnostic; git does not special-case it for divergent history.
    Measured directly against this repository (#559's own demonstration
    range): `338b4d0cf2` is NOT an ancestor of `2d4b887f3c` (parallel PR
    branches later reconciled through a merge neither commit is itself), yet
    `git diff 338b4d0cf2 2d4b887f3c -- desktop/.../SettingsPanels.tsx`
    correctly reports the file changed -- confirmed independently by
    STEP 1's own grep-based line inspection. Adding an `is_ancestor` gate
    here would silently discard that correct, verifiable result and replace
    it with an uninformative node-level refusal, which is what an earlier
    revision of this function did before this was caught.
    """
    recorded = stale.extract_recorded_revision(node)
    if recorded.sha is None:
        return NodeReport(
            node_id=node.id,
            recorded_revision=None,
            disposition="must-not-move (MUST 4)",
            triggering=triggering,
            claims=[],
            blocking=[],
        )

    if not stale.commit_exists(recorded.sha, repo_dir):
        return NodeReport(
            node_id=node.id,
            recorded_revision=recorded.sha,
            disposition="must-not-move (MUST 4)",
            triggering=triggering,
            claims=[],
            blocking=[],
        )

    try:
        exclude_index = locate_recorded_revision_entry(node, recorded.sha)
    except ValueError:
        exclude_index = None

    claims: list[ClaimRoute2] = []
    for entry_index, entry in enumerate(node.data.get("evidence") or [], start=1):
        if entry_index == exclude_index:
            continue
        if not isinstance(entry, dict):
            continue
        citations = [c for c in (entry.get("evidence") or []) if isinstance(c, str)]
        claims.append(classify_claim(entry_index, citations, recorded.sha, head, repo_dir))

    blocking = [claim.entry_index for claim in claims if claim.status != "clean"]
    disposition = "may-move" if not blocking else "must-not-move (MUST 4)"

    return NodeReport(
        node_id=node.id,
        recorded_revision=recorded.sha,
        disposition=disposition,
        triggering=triggering,
        claims=claims,
        blocking=blocking,
    )


def build_report(root: Path, base: str, head: str, repo_dir: Path) -> RegenerateReport:
    """Run the full chain: `impact.compute_impact` for the impacted set, then
    this module's own route-2 classification and disposition for every node
    it names."""
    impact_report = impact.compute_impact(root, base, head, repo_dir)
    all_nodes = {node.id: node for node in stale.discover_nodes(root)}

    triggering_by_node: dict[object, list[Triggering]] = {}
    for row in sorted(
        impact_report.impacted_nodes,
        key=lambda r: (str(r.node_id), r.reason, r.changed_path or ""),
    ):
        triggering_by_node.setdefault(row.node_id, []).append(
            Triggering(row.changed_path, row.evidence_entry_index)
        )

    nodes: list[NodeReport] = []
    for node_id in sorted(triggering_by_node, key=str):
        node = all_nodes.get(node_id)
        if node is None:
            # Named as impacted, but not resolvable via a fresh discover_nodes
            # walk of `root` -- schema-invalid or removed since impact.py's
            # own load. Defensive: today's call sites feed `impact_report`
            # and `all_nodes` from the same `root` in the same run, so this
            # branch is currently unreachable in practice. It is NOT reported
            # as an unreadable node -- nothing here appends to
            # `report.unreadable_nodes`, which only ever carries what
            # impact.py's own separate load already produced -- it is a
            # silent drop if this branch is ever actually reached.
            continue
        nodes.append(evaluate_node(node, head, repo_dir, triggering_by_node[node_id]))

    return RegenerateReport(
        nodes=nodes,
        coverage_gaps=impact_report.coverage_gaps,
        unreadable_nodes=impact_report.unreadable_nodes,
    )


def apply_report(report: RegenerateReport, root: Path, head: str, repo_dir: Path) -> None:
    """Move every `may-move` node's recorded revision to `head`, in place.

    Mutates `report` in place (`applied`, `new_revision`) so a caller's
    subsequent render reflects what actually happened, not merely what was
    eligible.
    """
    new_sha = resolve_full_sha(head, repo_dir)
    if new_sha is None:
        raise ValueError(f"cannot resolve {head!r} to a commit in this repository")

    all_nodes = {node.id: node for node in stale.discover_nodes(root)}
    for node_report in report.nodes:
        if node_report.disposition != "may-move":
            continue
        node = all_nodes[node_report.node_id]
        entry_index = locate_recorded_revision_entry(node, node_report.recorded_revision)
        apply_revision_move(node.path, entry_index, node_report.recorded_revision, new_sha)
        node_report.applied = True
        node_report.new_revision = new_sha


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--base", required=True, help="revision to diff from")
    parser.add_argument("--head", required=True, help="revision to diff to")
    parser.add_argument("--root", type=Path, default=None, help=f"corpus root (default: {DEFAULT_ROOT})")
    parser.add_argument("--repo-dir", type=Path, default=None, help="repository root (default: resolved via git)")
    parser.add_argument("--out", type=Path, default=None, help="write the report here instead of stdout")
    parser.add_argument("--format", choices=["json", "text"], default="json", help="report format (default: json)")
    parser.add_argument(
        "--apply",
        action="store_true",
        help="rewrite every may-move node's recorded-revision entry to --head (refuses on the default branch)",
    )
    args = parser.parse_args(argv)

    repo_dir = args.repo_dir if args.repo_dir else validate.repo_root()
    root = args.root if args.root else repo_dir / DEFAULT_ROOT

    if not root.exists():
        sys.stderr.write(f"corpus root does not exist: {root}\n")
        return 1

    if args.apply:
        branch = current_branch(repo_dir)
        if branch == DEFAULT_BRANCH:
            sys.stderr.write(
                f"--apply refused: current branch is {DEFAULT_BRANCH!r}, this "
                "repository's default branch. Nothing on GitHub enforces this "
                "for launchpad-26/buzz -- the refusal is this tool's own. Run "
                "from a branch cut from launchpad instead.\n"
            )
            return 1

    if resolve_full_sha(args.base, repo_dir) is None:
        sys.stderr.write(f"--base does not resolve to a commit: {args.base}\n")
        return 1
    if resolve_full_sha(args.head, repo_dir) is None:
        sys.stderr.write(f"--head does not resolve to a commit: {args.head}\n")
        return 1

    report = build_report(root, args.base, args.head, repo_dir)

    if args.apply:
        try:
            apply_report(report, root, args.head, repo_dir)
        except ValueError as error:
            sys.stderr.write(f"--apply failed: {error}\n")
            return 1

    output = report.to_text() if args.format == "text" else report.to_json()

    if args.out:
        args.out.write_text(output)
    else:
        sys.stdout.write(output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
