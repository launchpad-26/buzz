"""Change-set to impacted-documentation-node mapping -- issue #635.

Given a repository revision range, reports which `launchpad/docs/corpus/`
nodes a changed path's evidence citations name -- directly, by citing the
path itself, and transitively, by a `depends-on`/`part-of`/`supersedes`
relationship edge to a directly-impacted node.

Mapping runs entirely through the front-matter `evidence` ledger's
file-naming citations, the only node-to-source link the schema has
(`launchpad/docs/corpus/AGENTS.md`: the evidence array "is also the node's
provenance ledger -- there is no separate provenance field"). There is no
node-to-file edge type in `relationships.schema.json` to use instead.

Node discovery and citation normalization are NOT re-implemented here: this
module imports `discover_nodes`, `iter_citations` and `normalize_file_citation`
from `stale.py` (issue #556), which already made the same walk for staleness
detection and exposes them as a public, stable-signature surface for exactly
this reuse.

Relationship-type propagation is a human decision (2026-09-03, Serina, not
re-litigated here): `depends-on`, `part-of` and `supersedes` propagate impact
across the corpus graph; `references` and `implements` do not. See
`_PROPAGATION_DIRECTION` for the direction each propagating type flows, taken
from `relationships.schema.json`'s own `relationshipMeta` directionality text.

Propagation is transitive (multi-hop), not a single hop from the directly
impacted node: a neighbour of a newly-propagated neighbour is admitted too,
because the same "genuine dependency" justification that admits a direct
neighbour recurses -- see `propagate_impact`'s own docstring for the detail.

`changed_paths` diffs `base`/`head` with git's literal two-dot form
(tree-to-tree), not the merge-base-relative three-dot form. This is a
deliberate, already-made decision -- see `changed_paths`'s docstring.

What this module does NOT establish:

- That a node cites a changed file is not evidence the node's CLAIMS
  changed -- only that a human should re-check them. This is the same
  distinction `stale.py` draws for its own verdicts ("movement, not
  meaning"); this module inherits it rather than restating a different rule.
- It does not detect staleness itself (`stale.py`, issue #556) -- that
  module decides whether a cited file actually moved since a node's recorded
  revision; this module only asks whether a file the caller says changed is
  cited at all.
- It does not regenerate, re-check, or file anything against the nodes it
  names (issues #559 and #631) -- it is a pure mapping step those two build
  on, not a maintenance action of its own.

Run:  python3 launchpad/project-intelligence/corpus/impact.py --base <rev>
      --head <rev> [--root PATH] [--out PATH]
  or: python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

# stale.py lives in this same directory and isn't a package (no __init__.py --
# this repo's existing project-intelligence/ convention), so it's loaded by
# path, the same way stale.py itself loads validate.py. Loading stale.py
# (rather than validate.py directly) is deliberate: stale.py's own module
# docstring and #635's plan both name it as the shared surface to import,
# and `stale.validate` gives this module validate.py's loader/schema/label
# helpers too, without a second by-path load of the same file.
_CORPUS_DIR = Path(__file__).resolve().parent
_stale_spec = importlib.util.spec_from_file_location("corpus_stale", _CORPUS_DIR / "stale.py")
stale = importlib.util.module_from_spec(_stale_spec)
sys.modules.setdefault("corpus_stale", stale)
_stale_spec.loader.exec_module(stale)

validate = stale.validate

DEFAULT_ROOT = validate.DEFAULT_ROOT


# ---------------------------------------------------------------------------
# STEP 1 -- citation-to-node index
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class CitationRef:
    """One node's citation of one path -- the "reason/evidence path" DoD
    bullet 4 asks for: which node, which evidence entry, and what it claims."""

    node_id: object
    entry_index: int
    statement: str | None


def build_citation_index(nodes: list["validate.LoadedNode"]) -> dict[str, list[CitationRef]]:
    """Map every normalized file-naming citation to the node(s) citing it.

    Walks every evidence entry via `stale.iter_citations` and normalizes each
    citation via `stale.normalize_file_citation` -- both public, stable-
    signature functions #556 built for exactly this reuse. Citations that
    name no file (commit, graph-edge, tool-result, URL) normalize to `None`
    and are dropped explicitly here rather than being allowed to fall through
    to some accidental default.
    """
    index: dict[str, list[CitationRef]] = {}
    for node in nodes:
        statements: dict[int, str | None] = {}
        for entry_index, entry in enumerate(node.data.get("evidence") or [], start=1):
            if isinstance(entry, dict):
                statements[entry_index] = entry.get("statement")

        for entry_index, _citation_index, citation in stale.iter_citations(node):
            path = stale.normalize_file_citation(citation)
            if path is None:
                continue
            index.setdefault(path, []).append(
                CitationRef(node.id, entry_index, statements.get(entry_index))
            )
    return index


# ---------------------------------------------------------------------------
# STEP 2 -- change-set reader
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ChangedPath:
    """One path git reports as changed. `status` is git's own `--name-status`
    letter (A/M/D/R...). For a rename, `path` is the NEW name and `old_path`
    is the pre-rename name -- both are real paths a citation could still
    name, so both are checked against the citation index."""

    status: str
    path: str
    old_path: str | None = None


def changed_paths(base: str, head: str, repo_dir: Path) -> list[ChangedPath]:
    """Every path that differs between `base` and `head`.

    Explicit `-c core.quotepath=false` and `--find-renames` rather than
    inherited config: `diff.renames` and `core.quotepath` are user-settable,
    and would otherwise make the same range produce different output on
    different machines -- the determinism this module's DoD bullet 6 asks
    for has to hold across machines, not just across repeated runs on one.

    Deliberately literal two-dot `git diff <base> <head>` (tree-to-tree),
    NOT the merge-base-relative three-dot `<base>...<head>` form the
    repository's own pre-push lanes use elsewhere. This is a decision, made
    once here, not an oversight: this module is a general-purpose diffing
    tool that takes exact refs from its caller (a human at the CLI, or a
    future automated caller such as issue #631's skill), and two-dot is the
    unsurprising, literal reading of "diff base against head" for that
    contract. A caller that wants merge-base-relative (three-dot) semantics
    instead -- e.g. "everything head has done since it diverged from base"
    -- can compute `git merge-base <base> <head>` itself and pass the
    result as `base`; this module does not do that resolution on the
    caller's behalf.
    """
    result = subprocess.run(
        [
            "git",
            "-c",
            "core.quotepath=false",
            "diff",
            "--name-status",
            "--find-renames",
            base,
            head,
        ],
        cwd=repo_dir,
        capture_output=True,
        text=True,
        check=True,
    )
    changes: list[ChangedPath] = []
    for line in result.stdout.splitlines():
        if not line:
            continue
        fields = line.split("\t")
        status = fields[0][0]
        if status == "R":
            # `R<similarity>\t<old>\t<new>` -- the similarity digits are not a
            # status this module distinguishes on, only the letter is.
            changes.append(ChangedPath(status="R", path=fields[2], old_path=fields[1]))
        else:
            changes.append(ChangedPath(status=status, path=fields[1]))
    return changes


# ---------------------------------------------------------------------------
# STEP 4 -- relationship-type propagation
# ---------------------------------------------------------------------------

# A node's `relationships` entry is always `{type, target}` recorded on the
# SOURCE node (the node whose own front matter carries it), naming an edge to
# TARGET. relationships.schema.json's relationshipMeta gives each type's
# directionality in prose; this maps that prose to which way IMPACT flows
# along the declared edge:
#
#   "forward"  -- impact flows source -> target (the source's own change
#                 bears on the target)
#   "backward" -- impact flows target -> source (the source's claims depend
#                 on the target, so the target's change bears on the source)
#   "both"     -- either side's change bears on the other
#
# depends-on: "source requires target to be true/current for source's own
#   claims to hold" -- the SOURCE depends on the TARGET, so when the target
#   changes, the source is the one whose claims are now in question:
#   backward.
# part-of: "source is a constituent section/child of target" -- containment.
#   A changed CHILD (the source) bears on the PARENT's (target's) summary,
#   the same direction of consequence depends-on has, just phrased the other
#   way round: forward.
# supersedes: "source replaces target; target becomes historical" -- a
#   change bearing on either side is relevant to the other, since the
#   active node's claim of superseding the other can itself go stale: both.
# references / implements: DO NOT propagate (human decision, 2026-09-03,
#   not re-litigated) -- absent from this map entirely, rather than mapped
#   to a no-op direction, so a typo'd relationship type fails closed by
#   never matching any entry instead of silently matching one.
_PROPAGATION_DIRECTION = {
    "depends-on": "backward",
    "part-of": "forward",
    "supersedes": "both",
}


def _propagation_edges(nodes: list["validate.LoadedNode"]) -> list[tuple[object, object, str]]:
    """Every `(from_id, to_id, relationship_type)` edge along which impact
    propagates -- "from_id impacted implies to_id impacted" -- derived from
    each node's own declared `relationships` per `_PROPAGATION_DIRECTION`.
    """
    edges: list[tuple[object, object, str]] = []
    for node in nodes:
        for relationship in node.data.get("relationships") or []:
            if not isinstance(relationship, dict):
                continue
            rel_type = relationship.get("type")
            target = relationship.get("target")
            direction = _PROPAGATION_DIRECTION.get(rel_type)
            if direction is None or target is None:
                continue
            if direction == "forward":
                edges.append((node.id, target, rel_type))
            elif direction == "backward":
                edges.append((target, node.id, rel_type))
            else:  # "both"
                edges.append((node.id, target, rel_type))
                edges.append((target, node.id, rel_type))
    return edges


def propagate_impact(
    directly_impacted: Iterable[object], nodes: list["validate.LoadedNode"]
) -> list["ImpactedNode"]:
    """Breadth-first, transitive expansion from `directly_impacted` along
    propagating relationship edges only.

    Transitive rather than a single hop: the same "genuine dependency" rule
    that admits a direct neighbour applies just as well to a neighbour of a
    newly-admitted neighbour, so expansion continues to a fixpoint rather
    than stopping after one step.
    """
    forward: dict[object, list[tuple[object, str]]] = {}
    for from_id, to_id, rel_type in _propagation_edges(nodes):
        forward.setdefault(from_id, []).append((to_id, rel_type))

    known_ids = {node.id for node in nodes}
    seen = set(directly_impacted)
    # `seen` is a `set`, and Python randomizes `str` hash order per process
    # (PYTHONHASHSEED unset by default) -- `list(seen)` would give a
    # different frontier order on every separate `python3 impact.py`
    # invocation, even against byte-identical input. That is not just
    # internal bookkeeping: when two frontier members both have an edge to
    # the same not-yet-seen neighbour, whichever is processed first is the
    # one named in that neighbour's `reason` string (e.g. "propagated via
    # 'part-of' relationship with a" vs "...with b"), so an unordered
    # frontier makes the reported `reason` -- and therefore the JSON output
    # -- nondeterministic across processes. Sorting by `str(id)` here is
    # what makes two separate invocations against the same input produce
    # byte-identical output (DoD bullet 6). Every downstream frontier
    # (`next_frontier` below) is already deterministic once this one is:
    # it is built by iterating this sorted frontier in order, then each
    # node's own edge list in its declared (list, not set) order.
    frontier = sorted(seen, key=str)
    propagated: list[ImpactedNode] = []
    while frontier:
        next_frontier: list[object] = []
        for current in frontier:
            for neighbour_id, rel_type in forward.get(current, []):
                if neighbour_id not in known_ids or neighbour_id in seen:
                    continue
                seen.add(neighbour_id)
                propagated.append(
                    ImpactedNode(
                        node_id=neighbour_id,
                        reason=f"propagated via '{rel_type}' relationship with {current}",
                    )
                )
                next_frontier.append(neighbour_id)
        frontier = next_frontier
    return propagated


# ---------------------------------------------------------------------------
# STEP 3 / 5 / 7 -- report shape
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ImpactedNode:
    """One node impacted by the change set, directly or by propagation.

    `changed_path`/`evidence_entry_index`/`statement` are set for a direct
    citation match; `reason` alone carries the explanation for a propagated
    neighbour, which cites no changed path of its own.
    """

    node_id: object
    reason: str
    changed_path: str | None = None
    evidence_entry_index: int | None = None
    statement: str | None = None


@dataclass
class CoverageGaps:
    """Changed paths that matched no citation at all (DoD: coverage gaps).

    `paths` never contains a credential-shaped path -- see
    `build_coverage_gaps` -- `redacted_count` says one was withheld without
    ever naming it.
    """

    paths: list[str] = field(default_factory=list)
    redacted_count: int = 0
    by_area: dict[str, int] = field(default_factory=dict)


@dataclass(frozen=True)
class UnreadableNode:
    """One node `validate.load_nodes` could not schema-validate. `label` is
    `validate._label`'s safe-to-print form -- the node's own id when it is a
    plain kebab-case string, otherwise its file path."""

    label: str
    error: str


@dataclass
class ImpactReport:
    impacted_nodes: list[ImpactedNode] = field(default_factory=list)
    coverage_gaps: CoverageGaps = field(default_factory=CoverageGaps)
    unreadable_nodes: list[UnreadableNode] = field(default_factory=list)

    def to_json(self) -> str:
        payload = {
            "impacted_nodes": [
                {
                    "node_id": row.node_id,
                    "reason": row.reason,
                    "changed_path": row.changed_path,
                    "evidence_entry_index": row.evidence_entry_index,
                    "statement": row.statement,
                }
                for row in sorted(
                    self.impacted_nodes,
                    key=lambda r: (str(r.node_id), r.reason, r.changed_path or ""),
                )
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


def build_coverage_gaps(changed_path_names: Iterable[str], covered_paths: set[str]) -> CoverageGaps:
    """Every changed path that matched no citation, grouped by top-level area.

    A credential-shaped path (reusing `validate._is_prohibited_citation`,
    rather than a second blocklist -- see `evidence.py`'s own comment about
    this exact duplication) is counted in `redacted_count` and excluded from
    both `paths` and `by_area`, so no channel of the report ever echoes it.
    """
    gaps = CoverageGaps()
    for path in sorted(set(changed_path_names)):
        if path in covered_paths:
            continue
        if validate._is_prohibited_citation(path):
            gaps.redacted_count += 1
            continue
        gaps.paths.append(path)
        area = path.split("/", 1)[0] if "/" in path else "(root)"
        gaps.by_area[area] = gaps.by_area.get(area, 0) + 1
    return gaps


def compute_impact(root: Path, base: str, head: str, repo_dir: Path) -> ImpactReport:
    """Run the full mapping: discover nodes, index citations, diff the range,
    match directly, propagate, and report coverage gaps and unreadable nodes.
    """
    all_nodes = validate.load_nodes(root)
    valid_nodes = [node for node in all_nodes if node.error is None]
    unreadable_nodes = [
        UnreadableNode(label=validate._label(node.id, node.path), error=node.error)
        for node in all_nodes
        if node.error is not None
    ]

    citation_index = build_citation_index(valid_nodes)
    changes = changed_paths(base, head, repo_dir)

    direct: list[ImpactedNode] = []
    directly_impacted_ids: set[object] = set()
    covered_paths: set[str] = set()
    for change in changes:
        candidate_paths = [change.path] if change.old_path is None else [change.path, change.old_path]
        for path in candidate_paths:
            refs = citation_index.get(path)
            if not refs:
                continue
            covered_paths.add(change.path)
            for ref in refs:
                directly_impacted_ids.add(ref.node_id)
                direct.append(
                    ImpactedNode(
                        node_id=ref.node_id,
                        reason=f"cites {path}",
                        changed_path=path,
                        evidence_entry_index=ref.entry_index,
                        statement=ref.statement,
                    )
                )

    propagated = propagate_impact(directly_impacted_ids, valid_nodes)
    gaps = build_coverage_gaps((change.path for change in changes), covered_paths)

    return ImpactReport(
        impacted_nodes=direct + propagated,
        coverage_gaps=gaps,
        unreadable_nodes=unreadable_nodes,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", required=True, help="revision to diff from")
    parser.add_argument("--head", required=True, help="revision to diff to")
    parser.add_argument("--root", type=Path, default=None, help=f"corpus root (default: {DEFAULT_ROOT})")
    parser.add_argument("--out", type=Path, default=None, help="write JSON here instead of stdout")
    args = parser.parse_args(argv)

    repo_dir = validate.repo_root()
    root = args.root if args.root else repo_dir / DEFAULT_ROOT

    output = compute_impact(root, args.base, args.head, repo_dir).to_json()

    if args.out:
        args.out.write_text(output)
    else:
        sys.stdout.write(output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
