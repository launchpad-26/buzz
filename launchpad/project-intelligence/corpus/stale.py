"""Staleness detection for canonical documentation corpus nodes -- issue #556.

Detects when a `launchpad/docs/corpus/` node's recorded-revision evidence has
moved since it was authored or last re-checked: for every node, resolve its
recorded commit SHA, diff the paths its evidence citations name between that
SHA and `HEAD`, and report `stale` / `fresh` / `unestablished` per node --
never a judgement about whether the node's *content* is still correct. ADR-0004
(now superseded by ADR-0050) drew that line -- "detection is mechanical,
triage is judgement" -- and this module keeps it: it reports movement, never
"the node is wrong".

Disposition of DoD bullet 5 ("existing #556 findings are incorporated or
explicitly superseded by the new canonical-corpus model"):

Re-checked 2026-09-03 via `gh issue view 556 --repo launchpad-26/buzz --json
comments,body` (`comments: []`) and `gh api
repos/launchpad-26/buzz/issues/556/timeline --paginate` (latest event: the
2026-09-03 `blocked_by_removed`/`blocking_added` dependency-direction fix
already recorded in the plan; no comment-type event exists at any point in the
timeline). #556 itself carries no findings -- no comments, no linked PR. The
only trace of what it inherited is its 2026-08-24 rename from the
handbook-era title ("extend staleness detection beyond handbook pages to
crate content"), whose mechanism was ADR-0004, "How stale synthesised pages
are detected". Treating ADR-0004's four findings as the referent for DoD
bullet 5 is therefore this module's stated interpretation, not a fact GitHub
records -- flagged as `OPEN` item 1 in the plan for a reviewer to confirm or
correct.

| ADR-0004 finding | Disposition |
|---|---|
| Detection is git-only -- no model, no embeddings | incorporated |
| `git log A..B` (and `git diff A..B`) return empty and exit 0 when `A` is not an ancestor of `B`, so the ancestor check is mandatory and must fail closed | incorporated -- this is DoD bullet 4 |
| Detection is mechanical; triage is judgement -- report movement, never "the node is wrong" | incorporated |
| Output is one GitHub issue per scheduled run, plus a published index | superseded -- this module ships `stale.py` and its tests; filing issues and publishing an index belong to #631/#559 |

What this checker does NOT establish (STEP 8):

- It detects **movement, not meaning** -- a whitespace commit flags a node
  exactly as a rewrite does. ADR-0004's own recorded consequence, carried
  forward unchanged.
- A `fresh` verdict does **not** mean any claim in the node still holds --
  only a human re-reading the source does that (provenance.md MUST 3 route 1).
  `fresh` means only "the file-naming citations this module could check are
  unchanged since the recorded revision", never "the node is correct".
- **It will report almost every node `unestablished` under CI's depth-1
  checkout**, because gate 1 (`git cat-file -e <sha>^{commit}`) fails closed
  on a recorded revision this checkout's shallow history never fetched. It is
  therefore a local/scheduled tool until something fetches history for CI to
  run it against -- read a wall of `unestablished` there as an unfetched
  history, not a corpus-wide defect. See `LEFT OUT` in the plan for why wiring
  this into CI is deliberately not part of this issue.

Run:  python3 launchpad/project-intelligence/corpus/stale.py [--root PATH] [--head REF]
  or: python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"
"""

from __future__ import annotations

import argparse
import importlib.util
import posixpath
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Iterator

# validate.py lives in a directory (project-intelligence/corpus/) that isn't a
# package (no __init__.py -- this repo's existing project-intelligence/
# convention), so it's loaded by path, the same way test_validate.py and
# test_inventory.py already do, rather than by a dotted import. This is a
# deliberate choice over the alternative the plan named -- lifting
# discover_markdown_files/_load_frontmatter to public names in validate.py --
# because #556's own impacted-components list names only stale.py and
# corpus/tests/, and validate.py is unchanged either way; if a future issue
# wants those two names public, that is a one-line change there, not here.
_VALIDATE_PATH = Path(__file__).resolve().parent / "validate.py"
_validate_spec = importlib.util.spec_from_file_location("corpus_validate", _VALIDATE_PATH)
validate = importlib.util.module_from_spec(_validate_spec)
sys.modules.setdefault("corpus_validate", validate)
_validate_spec.loader.exec_module(validate)

DEFAULT_ROOT = validate.DEFAULT_ROOT
DEFAULT_HEAD = "HEAD"

# Rung 1 of the recorded-revision ladder (STEP 2): the fixed provenance
# sentence every node's own `AGENTS.md`-documented convention uses. Matched
# with `.search`, not `.match` -- linking.md's second occurrence embeds the
# same clause mid-sentence ("AGENTS.md's own front matter states this node
# was authored and checked against repository revision <sha>, the same
# revision this node records...").
_RECORDED_REVISION_STATEMENT_RE = re.compile(
    r"authored and checked against repository revision ([0-9a-f]{40})\b"
)

# Rung 2's citation shape, duplicated from validate.py's `_COMMIT_CITATION_RE`
# with a capturing group added -- validate.py's own version has none, because
# it only ever needs to recognise the shape, never extract the SHA from it.
_COMMIT_CITATION_RE = re.compile(r"^commit\s+([0-9a-fA-F]{7,40})\b")


@dataclass(frozen=True)
class RecordedRevision:
    """One node's resolved recorded-revision SHA, or why none could be resolved.

    `(node_id, sha, reason)` -- STEP 2's own done-when names this shape as a
    plain tuple; a frozen dataclass is used instead purely for the
    self-documenting field names, the convention every sibling module in this
    package (`evidence.py`, `manifest.py`) already follows for exactly this
    kind of small immutable result.
    """

    node_id: object
    sha: str | None
    reason: str | None = None


def discover_nodes(root: Path) -> list["validate.LoadedNode"]:
    """Every schema-valid corpus node under `root`.

    Reuses `validate.py`'s own loader and schema validation rather than
    re-walking the tree -- see the module-level comment on why validate.py is
    loaded by path instead of edited. Schema-invalid nodes (`node.error` set)
    are excluded: `validate.py` already reports them as validation errors, and
    an invalid node's `data` is not safe to assume well-shaped for the
    recorded-revision ladder or citation extraction below (the same reasoning
    `validate.py`'s own `find_citation_problems` uses to skip them).

    Public and stable-signature deliberately: issue #635's `impact.py`
    (building next on this same branch) imports this directly rather than
    re-implementing node discovery.
    """
    return [node for node in validate.load_nodes(root) if node.error is None]


def iter_citations(node: "validate.LoadedNode") -> Iterator[tuple[int, int, str]]:
    """Yield `(entry_index, citation_index, citation)` for every string
    citation in `node`'s evidence ledger, 1-indexed the way `validate.py`'s own
    position labels (`"evidence entry 2, citation 1"`) are -- so a caller that
    wants to name a citation by position, not by value, can reuse the same
    coordinates `validate.py` prints.

    Public and stable-signature: #635 needs the same iteration order to build
    its own per-path citation index without re-implementing this walk.
    """
    for entry_index, entry in enumerate(node.data.get("evidence") or [], start=1):
        if not isinstance(entry, dict):
            continue
        for citation_index, citation in enumerate(entry.get("evidence") or [], start=1):
            if isinstance(citation, str):
                yield entry_index, citation_index, citation


def normalize_file_citation(citation: str) -> str | None:
    """Return the repo-relative path a file-shaped citation names, with any
    trailing `:<line>` or `:<start>-<end>` position stripped -- or `None` if
    the citation is not one of CONTRACT.md section 3's three file-naming
    shapes (file range, file line, bare path).

    This is the normalization AGENTS.md's *Checking whether cited files
    moved* warns is mandatory: passing an un-normalized `path:127` straight to
    `git diff` resolves nothing and prints empty output, indistinguishable
    from an unchanged file.

    Public and stable-signature: #635 needs the identical normalized path for
    every file-shaped citation to build its own per-path index, and must
    reach the same conclusion this module does about which citations name a
    file at all.
    """
    text = citation.strip()
    if not text:
        return None

    link = validate._MARKDOWN_LINK_RE.match(text)
    if link:
        text = link.group("target")

    if text.startswith(validate._URL_PREFIXES):
        return None

    if (
        validate._COMMIT_CITATION_RE.match(text)
        or validate._GRAPH_EDGE_RE.match(text)
        or validate._TOOL_RESULT_RE.match(text)
    ):
        return None

    position = validate._FILE_POSITION_RE.match(text)
    if position:
        return position.group("path")

    if any(character.isspace() for character in text):
        return None

    return text


def extract_recorded_revision(node: "validate.LoadedNode") -> RecordedRevision:
    """Resolve one node's recorded-revision SHA via STEP 2's two-rung ladder.

    Rung 1: exactly one evidence ENTRY (not one distinct SHA -- two entries
    citing the identical SHA still fail this rung and fall through) whose
    `statement` matches the recorded-revision sentence.

    Rung 2: otherwise, exactly one distinct `commit <sha>` citation anywhere
    in the ledger -- counting only FULL 40-character SHAs. `_COMMIT_CITATION_RE`
    also matches 7-39 character abbreviations, but an abbreviation and the same
    commit's full SHA are the identical commit under two different strings; if
    both were tallied as distinct they would wrongly trip rung 3's "ambiguous"
    fallthrough for what is actually a single, unambiguous commit. Rung 2 has
    no repository to resolve an abbreviation against (this function takes no
    `repo_dir`), so an abbreviation on its own -- with no full-length citation
    of the same commit elsewhere in the ledger -- is excluded from the tally
    rather than guessed at.

    Rung 3: otherwise, unestablished -- ambiguous or absent, never guessed.
    """
    matching_statement_shas: list[str] = []
    commit_citation_shas: set[str] = set()

    for entry in node.data.get("evidence") or []:
        if not isinstance(entry, dict):
            continue
        statement = entry.get("statement")
        if isinstance(statement, str):
            match = _RECORDED_REVISION_STATEMENT_RE.search(statement)
            if match:
                matching_statement_shas.append(match.group(1).lower())
        for citation in entry.get("evidence") or []:
            if not isinstance(citation, str):
                continue
            commit_match = _COMMIT_CITATION_RE.match(citation.strip())
            if commit_match and len(commit_match.group(1)) == 40:
                commit_citation_shas.add(commit_match.group(1).lower())

    if len(matching_statement_shas) == 1:
        return RecordedRevision(node.id, matching_statement_shas[0])
    if len(commit_citation_shas) == 1:
        return RecordedRevision(node.id, next(iter(commit_citation_shas)))
    return RecordedRevision(
        node.id, None, reason="ambiguous or absent recorded revision"
    )


# ---------------------------------------------------------------------------
# Git primitives (STEP 4's four gates) -- every one takes `repo_dir` explicitly
# rather than assuming `validate.repo_root()`, so the hermetic fixtures STEP 6
# builds (throwaway repos under `tempfile.TemporaryDirectory`) exercise the
# identical code path production uses, never a fixture-only substitute.
# ---------------------------------------------------------------------------


def _run_git(args: list[str], repo_dir: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args], cwd=repo_dir, capture_output=True, text=True
    )


def commit_exists(sha: str, repo_dir: Path) -> bool:
    """Gate 1: is `sha` a commit this repository actually has?

    Not hypothetical: this checkout is shallow, and CI checks out at depth 1.
    `git cat-file -e` fails closed (non-zero exit) for a SHA the repository
    has never heard of, which is exactly "cannot establish", never "does not
    exist".
    """
    return _run_git(["cat-file", "-e", f"{sha}^{{commit}}"], repo_dir).returncode == 0


def is_ancestor(sha: str, head: str, repo_dir: Path) -> bool:
    """Gate 2: is `sha` an ancestor of `head`?

    ADR-0004's fail-closed step: `git diff`/`git log A..B` go quietly empty
    and exit 0 when `A` is not an ancestor of `B`, so skipping this check
    would read "recorded revision on a divergent branch" as "nothing changed".
    """
    return (
        _run_git(["merge-base", "--is-ancestor", sha, head], repo_dir).returncode
        == 0
    )


def path_exists_at_revision(sha: str, path: str, repo_dir: Path) -> bool:
    """Gate 3: did `path` exist AT `sha` -- not in the current working tree.

    Reused twice, deliberately: once here to decide whether a diff's empty
    output means "unchanged" or "never looked at anything", and again by the
    redaction check below to decide whether a citation is safe to echo. Using
    the recorded revision rather than the current tree is what lets a citation
    naming a file that was later deleted or renamed still be named in its
    finding -- see the module docstring's redaction note.
    """
    return _run_git(["cat-file", "-e", f"{sha}:{path}"], repo_dir).returncode == 0


def _lexically_contained_path(path_text: str, repo_dir: Path) -> str | None:
    """Gate 4 (part 1): reject an absolute or repository-escaping path.

    Purely lexical -- `posixpath.normpath`, no filesystem access, no symlink
    resolution -- because a citation this checks may legitimately not exist in
    the CURRENT tree (a deleted or renamed file, the exact case gate 3's
    redaction distinction exists for). `validate.py`'s sibling check
    (`_classify_repo_path`) resolves against the live filesystem because it is
    checking a citation for CURRENT existence; this one is checking a citation
    for historical existence, so it cannot depend on the path being resolvable
    today.
    """
    if PurePosixPath(path_text).is_absolute():
        return None
    normalized = posixpath.normpath(path_text)
    if normalized == ".." or normalized.startswith("../") or normalized == ".":
        return None
    return normalized


def diff_touched(sha: str, head: str, path: str, repo_dir: Path) -> bool:
    """Did `path` change between `sha` and `head`? Non-empty output => yes.

    Only ever called after gate 3 confirms `path` existed at `sha` -- an empty
    result from a nonexistent-at-`sha` pathspec is indistinguishable from an
    empty result from an unchanged file, which is the trap AGENTS.md documents
    and this module's own tests reproduce.
    """
    result = _run_git(["diff", "--name-only", sha, head, "--", path], repo_dir)
    return bool(result.stdout.strip())


def last_touch_revision(sha: str, head: str, path: str, repo_dir: Path) -> str | None:
    """The last commit that touched `path` in `(sha, head]` -- never bare `head`.

    "`HEAD` moved" is not information a reader can act on; "this file last
    moved at *this* commit" is.
    """
    result = _run_git(
        ["log", "-1", "--format=%H", f"{sha}..{head}", "--", path], repo_dir
    )
    out = result.stdout.strip()
    return out or None


def _position_label(entry_index: int, citation_index: int) -> str:
    return f"evidence entry {entry_index}, citation {citation_index}"


@dataclass(frozen=True)
class Finding:
    """One node's stale or unestablished citation -- DoD bullet 2's shape.

    `citation` is the normalized path ONLY when it is safe to echo -- see the
    module docstring's redaction note. Otherwise it is a position label
    (`"evidence entry 2, citation 1"`), naming the offender's location without
    ever printing a value that might be credential-shaped or was never a real
    path at all.
    """

    node_id: object
    status: str  # "stale" | "unestablished"
    citation: str
    reason: str
    recorded_revision: str | None
    current_revision: str | None = None


@dataclass(frozen=True)
class NodeVerdict:
    """One node's overall staleness verdict plus the findings that produced it.

    Precedence (STEP 4): any citation stale -> `stale`; else any citation or
    gate unestablished -> `unestablished`; else `fresh`. There is no code path
    to `fresh` while any input was unknown -- see `evaluate_node`.
    """

    node_id: object
    status: str  # "stale" | "fresh" | "unestablished"
    findings: tuple[Finding, ...] = ()


def evaluate_citation(
    node_id: object,
    recorded_sha: str,
    head: str,
    citation: str,
    entry_index: int,
    citation_index: int,
    repo_dir: Path,
) -> Finding | None:
    """Evaluate one citation. `None` means "fresh, or excluded -- no finding".

    Routes citations by CONTRACT.md section 3's six shapes plus `validate.py`'s
    two URL forms. The node's OWN recorded-revision `commit <sha>` citation is
    excluded entirely (returns `None`, not an `unestablished` finding) --
    AGENTS.md states it "does not count against the check", and reporting it
    would put one unestablished finding on every node forever.
    """
    text = citation.strip()
    if not text:
        # An empty citation is already a validate.py error (reported there);
        # nothing here to check, and nothing new to say about it.
        return None

    link = validate._MARKDOWN_LINK_RE.match(text)
    if link:
        text = link.group("target")

    position_label = _position_label(entry_index, citation_index)

    if text.startswith(validate._URL_PREFIXES):
        # OPEN item 2: pinned same-repo GitHub URLs are, in principle,
        # checkable -- deciding whether a URL names THIS repository (origin,
        # upstream, or both) is left to a human, per the plan. Every URL,
        # pinned or not, is unestablished in this version.
        return Finding(
            node_id,
            "unestablished",
            position_label,
            "is a URL citation, which this version does not verify",
            recorded_sha,
        )

    commit_match = _COMMIT_CITATION_RE.match(text)
    if commit_match:
        cited_sha = commit_match.group(1).lower()
        if recorded_sha.lower().startswith(cited_sha) or cited_sha.startswith(
            recorded_sha.lower()
        ):
            # This citation IS the node's own recorded-revision entry.
            return None
        return Finding(
            node_id,
            "unestablished",
            position_label,
            "is a commit reference, which names no file `git diff` can check",
            recorded_sha,
        )

    if validate._GRAPH_EDGE_RE.match(text) or validate._TOOL_RESULT_RE.match(text):
        return Finding(
            node_id,
            "unestablished",
            position_label,
            "is a graph-edge or tool-result citation, which names no openable file",
            recorded_sha,
        )

    # Everything else is either a file-shaped citation (bare path, or
    # `path:line`/`path:start-end`) or matches none of CONTRACT.md's forms at
    # all -- the same shape-routing decision `normalize_file_citation` already
    # makes (and #635 already relies on), so it is the single call site for
    # that decision rather than a second, inline copy of it.
    path_text = normalize_file_citation(text)
    if path_text is None:
        return Finding(
            node_id,
            "unestablished",
            position_label,
            "matches none of CONTRACT.md's six supported citation forms",
            recorded_sha,
        )

    if validate._is_prohibited_citation(path_text):
        return Finding(
            node_id,
            "unestablished",
            position_label,
            "matches a prohibited credential-like pattern, refused without echoing its value",
            recorded_sha,
        )

    normalized_path = _lexically_contained_path(path_text, repo_dir)
    if normalized_path is None:
        return Finding(
            node_id,
            "unestablished",
            position_label,
            "is absolute or resolves outside the repository, refused without echoing its value",
            recorded_sha,
        )

    if not path_exists_at_revision(recorded_sha, normalized_path, repo_dir):
        return Finding(
            node_id,
            "unestablished",
            position_label,
            "does not resolve to a real file at the recorded revision -- an "
            "empty diff would be indistinguishable from 'unchanged'",
            recorded_sha,
        )

    # Safe to echo from here: the citation passed the prohibited/absolute/
    # escaping checks AND resolved to a real file at the recorded revision --
    # a location this repository's own history already confirms, the same
    # reasoning validate.py's _label() uses to justify printing a node path.
    if diff_touched(recorded_sha, head, normalized_path, repo_dir):
        current = last_touch_revision(recorded_sha, head, normalized_path, repo_dir)
        return Finding(
            node_id,
            "stale",
            normalized_path,
            "file changed between the recorded revision and head",
            recorded_sha,
            current,
        )

    return None  # fresh -- no finding


def evaluate_node(
    node: "validate.LoadedNode",
    recorded: RecordedRevision,
    head: str,
    repo_dir: Path,
) -> NodeVerdict:
    """STEP 4's four gates, in order, then per-citation evaluation.

    Gates 1 and 2 are node-level: they concern the recorded revision itself,
    not any one citation, so they run once, before any citation is diffed, and
    short-circuit the whole node to `unestablished` if either fails. Gates 3
    and 4 are per-citation and live inside `evaluate_citation`.
    """
    if recorded.sha is None:
        return NodeVerdict(
            node.id,
            "unestablished",
            (
                Finding(
                    node.id,
                    "unestablished",
                    "(recorded revision)",
                    recorded.reason or "no recorded revision could be established",
                    None,
                ),
            ),
        )

    if not commit_exists(recorded.sha, repo_dir):
        return NodeVerdict(
            node.id,
            "unestablished",
            (
                Finding(
                    node.id,
                    "unestablished",
                    "(recorded revision)",
                    "recorded revision is absent from this repository -- a "
                    "missing SHA means 'cannot establish', never 'does not exist'",
                    recorded.sha,
                ),
            ),
        )

    if not is_ancestor(recorded.sha, head, repo_dir):
        return NodeVerdict(
            node.id,
            "unestablished",
            (
                Finding(
                    node.id,
                    "unestablished",
                    "(recorded revision)",
                    "recorded revision is not an ancestor of head -- ADR-0004's "
                    "fail-closed step, because the range diff goes quietly empty otherwise",
                    recorded.sha,
                ),
            ),
        )

    findings: list[Finding] = []
    saw_stale = False
    saw_unestablished = False
    for entry_index, citation_index, citation in iter_citations(node):
        outcome = evaluate_citation(
            node.id, recorded.sha, head, citation, entry_index, citation_index, repo_dir
        )
        if outcome is None:
            continue
        findings.append(outcome)
        if outcome.status == "stale":
            saw_stale = True
        elif outcome.status == "unestablished":
            saw_unestablished = True

    if saw_stale:
        status = "stale"
    elif saw_unestablished:
        status = "unestablished"
    else:
        status = "fresh"
    return NodeVerdict(node.id, status, tuple(findings))


@dataclass(frozen=True)
class StaleReport:
    """A full run's verdicts, sorted for deterministic rendering (STEP 8)."""

    verdicts: tuple[NodeVerdict, ...]

    def render(self) -> str:
        lines: list[str] = []
        for verdict in sorted(self.verdicts, key=lambda v: str(v.node_id)):
            for finding in sorted(
                verdict.findings, key=lambda f: (f.status, f.citation, f.reason)
            ):
                current = (
                    f", current {finding.current_revision}"
                    if finding.current_revision
                    else ""
                )
                lines.append(
                    f"{finding.status.upper()}  {verdict.node_id}: "
                    f"{finding.citation} -- {finding.reason} "
                    f"(recorded {finding.recorded_revision}{current})"
                )
        counts = {"stale": 0, "fresh": 0, "unestablished": 0}
        for verdict in self.verdicts:
            counts[verdict.status] += 1
        lines.append(
            f"SUMMARY  {len(self.verdicts)} node(s): {counts['stale']} stale, "
            f"{counts['fresh']} fresh, {counts['unestablished']} unestablished"
        )
        return "\n".join(lines) + "\n"


def run(root: Path, head: str, repo_dir: Path) -> StaleReport:
    """Discover every node under `root` and evaluate its staleness against `head`."""
    verdicts = tuple(
        evaluate_node(node, extract_recorded_revision(node), head, repo_dir)
        for node in discover_nodes(root)
    )
    return StaleReport(verdicts)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root", default=None, help=f"corpus root (default: {DEFAULT_ROOT})"
    )
    parser.add_argument(
        "--head", default=DEFAULT_HEAD, help=f"git ref to diff against (default: {DEFAULT_HEAD})"
    )
    args = parser.parse_args(argv)

    repo_dir = validate.repo_root()
    root = Path(args.root) if args.root else repo_dir / DEFAULT_ROOT

    report = run(root, args.head, repo_dir)
    sys.stdout.write(report.render())
    return 0


if __name__ == "__main__":
    sys.exit(main())
