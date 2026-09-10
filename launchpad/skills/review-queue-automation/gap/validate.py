#!/usr/bin/env python3
"""Deterministic rerun procedure for the RQA gap analysis (issue #2070).

Re-derives the estate manifest and the frozen requirements set at the pinned
revision and checks four invariants against the current corpus under `gap/`:

  1. Manifest re-inventory: the tracked-file list and its stated `Count:` are
     re-derived from `git ls-tree` at the manifest's own recorded revision;
     every `assessed` file must map, through `clusters.md` and an
     `evidence/<cluster>.md` unit's `Files:` line, to a unit that has an entry
     in `dispositions/<cluster>.md`; every `excluded` file must carry a
     non-empty reason.
  2. Requirements re-inventory: every `### RQA-...` heading of the frozen
     `requirements-specification.md` has exactly one row across
     `register/{br,fr,nfr}.md`, and no register row keys an ID that is not a
     requirement.
  3. Staleness: for every register row, and for every `path:line` citation
     inside the evidence files, the last commit that touched the cited path
     (on the current branch) must be an ancestor of the commit the row (or,
     for evidence files, the manifest) records as its evaluation revision. A
     citation is checked only when the cited path is one of the manifest's own
     135 tracked files -- the only paths a "the tree at revision X" claim can
     be made about. That gate quietly excludes two kinds of citation that are
     not code drift: a bare module-name shorthand that drops its directory
     prefix (`config.py:42` instead of `scripts/config.py:42`, which resolves
     to nothing) and a citation into `gap/` itself (this analysis's own
     output, which necessarily postdates every implementation revision and
     would otherwise "fail" unconditionally).
  4. Open escalations: every `PENDING-HUMAN:<id>` marker actually in use
     anywhere under `gap/`.

Stdlib only. Run from anywhere; paths are relative to this file.

    python3 validate.py

Collects every failure rather than stopping at the first, and prints counts
on a clean run so a pass is informative, not just silent. Exits non-zero if
either checks 1-3 raise a structural failure or check 4 finds an open marker.

Check 4 fails when and only when a real `PENDING-HUMAN:<id>` marker exists
somewhere under `gap/`, and it then lists every occurrence with its
`file:line`. Its output is printed under a heading separate from checks 1-3 so
a reader can tell "a person still owes an answer" from "the analysis is
structurally broken" at a glance — which is why the check is shaped this way
and why a red run must be read for *which* check failed. Observed on the corpus
as of 2026-09-08: check 4 passes and this file exits 0, the maintainer having
ruled on all six escalations that were open (`gap/gap-analysis.md` §8). That is
a dated observation about the corpus, not the check's expected outcome; a later
revision that raises a new escalation will fail check 4 again, correctly.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent  # .../gap
REPO_ROOT = HERE.parents[3]  # .../buzz
SKILL_REL = "launchpad/skills/review-queue-automation"
SKILL = REPO_ROOT / SKILL_REL

CLUSTERS = ["queue", "dispatch", "policy", "verdict", "authority", "resilience", "docs"]
REGISTER_CLASSES = ["br", "fr", "nfr"]

structural_failures: list[str] = []

# Check 3's disclosure list: citations check_register_staleness/check_evidence_staleness
# could not resolve to a manifest-tracked path (bare module-name shorthand missing its
# directory prefix), and therefore did not check for staleness at all. Populated by
# those two functions, printed under check 3's own heading in main() -- distinct from
# structural_failures because an unresolved citation is NOT a failure (see the NOT
# APPLICABLE wording at the print site): it is a disclosed gap in what was verified.
excluded_register_citations: list[tuple[str, str, str, str]] = []  # (cls, rid, path, line)
excluded_evidence_citations: list[tuple[str, str, str]] = []  # (cluster, path, line)


def fail(msg: str) -> None:
    structural_failures.append(msg)


# --------------------------------------------------------------------------- #
# git access
# --------------------------------------------------------------------------- #

def _git(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=REPO_ROOT, capture_output=True, text=True)


def git_ls_tree(revision: str, rel_path: str) -> list[str]:
    """Files tracked under `rel_path` at `revision`, relative to `rel_path` itself."""
    r = _git(["ls-tree", "-r", "--name-only", revision, "--", rel_path])
    if r.returncode != 0:
        raise RuntimeError(f"git ls-tree {revision} -- {rel_path} failed: {r.stderr.strip()}")
    prefix = rel_path.rstrip("/") + "/"
    return [line[len(prefix):] for line in r.stdout.splitlines() if line]


_commit_cache: dict[str, str | None] = {}


def resolve_commit(revision: str) -> str | None:
    if revision not in _commit_cache:
        r = _git(["rev-parse", f"{revision}^{{commit}}"])
        _commit_cache[revision] = r.stdout.strip() if r.returncode == 0 else None
    return _commit_cache[revision]


_last_touch_cache: dict[str, str | None] = {}


def last_touch_commit(rel_path: str) -> str | None:
    """The most recent commit on the current branch touching `rel_path`, or None
    if the path has no history here (not tracked, or the directory prefix the
    citation used does not resolve to a real file)."""
    if rel_path not in _last_touch_cache:
        r = _git(["log", "-1", "--format=%H", "--", rel_path])
        out = r.stdout.strip()
        _last_touch_cache[rel_path] = out if r.returncode == 0 and out else None
    return _last_touch_cache[rel_path]


def is_ancestor(older: str, newer: str) -> bool:
    return _git(["merge-base", "--is-ancestor", older, newer]).returncode == 0


_blob_cache: dict[tuple[str, str], str | None] = {}


def blob_at(revision: str, rel_path: str) -> str | None:
    """The blob hash of `rel_path` as of `revision`, or None if absent there."""
    key = (revision, rel_path)
    if key not in _blob_cache:
        r = _git(["rev-parse", f"{revision}:{rel_path}"])
        out = r.stdout.strip()
        _blob_cache[key] = out if r.returncode == 0 and out else None
    return _blob_cache[key]


def content_unchanged_since(revision: str, rel_path: str) -> bool:
    """True when `rel_path`'s bytes at HEAD are identical to its bytes at
    `revision`.

    Staleness is a question about whether the lines a citation names have
    MOVED, which is a property of content, not of history. A commit that
    touches a file without changing it -- a revert restoring the pinned bytes,
    a merge bringing the same content in by another route, a mode change --
    makes `last_touch_commit` postdate the pin while every cited line still
    points exactly where it did. Comparing blob hashes is strictly more
    accurate than comparing commits: identical blobs prove no line moved, and
    any real edit changes the blob, so this narrows nothing that matters. It is
    an accuracy fix, not a relaxation -- do not extend it to "close enough"
    comparisons such as line counts or timestamps.
    """
    head = blob_at("HEAD", rel_path)
    return head is not None and head == blob_at(revision, rel_path)


# --------------------------------------------------------------------------- #
# shared pipe-table parsing (matches ../requirements/validate.py's house style)
# --------------------------------------------------------------------------- #

def parse_pipe_row(line: str) -> list[str]:
    assert line.startswith("|") and line.endswith("|"), line
    return [c.strip() for c in line[1:-1].split("|")]


def parse_table_rows(lines: list[str], header_idx: int) -> list[list[str]]:
    rows = []
    i = header_idx + 2
    while i < len(lines) and lines[i].startswith("|"):
        rows.append(parse_pipe_row(lines[i]))
        i += 1
    return rows


def find_table_rows(text: str, header_prefix: str, ncols: int, label: str) -> list[list[str]]:
    lines = text.split("\n")
    idx = next((i for i, l in enumerate(lines) if l.startswith(header_prefix)), None)
    if idx is None:
        fail(f"[{label}] table header {header_prefix!r} not found")
        return []
    rows = parse_table_rows(lines, idx)
    bad = [r for r in rows if len(r) != ncols]
    if bad:
        fail(f"[{label}] {len(bad)} row(s) do not have {ncols} columns (a stray '|' in a cell?)")
    return [r for r in rows if len(r) == ncols]


# --------------------------------------------------------------------------- #
# citation extraction
# --------------------------------------------------------------------------- #

# A formal citation per methodology.md §3 rule 1 is `path:line`, the path relative
# to launchpad/skills/review-queue-automation/. Every file in this estate carries
# one of these five extensions, so a path is recognised by its extension, not by
# a fixed directory list (gap/ itself, and requirements/, are legitimate citation
# targets alongside scripts/, tests/, schemas/ and references/).
PATH_LINE_RE = re.compile(
    r"(?P<path>(?:[A-Za-z0-9_.-]+/)*[A-Za-z0-9_.-]+\.(?:py|md|json|sh|example)):(?P<line>\d+(?:-\d+)?)"
)

UNIT_HEADING_RE = re.compile(r"^### (U-([A-Z]+)-\d{2}) \u2014 ", re.MULTILINE)
FILES_LINE_RE = re.compile(r"^Files:\s*(.+)$", re.MULTILINE)


def cited_paths(text: str) -> set[str]:
    return {m.group("path") for m in PATH_LINE_RE.finditer(text)}


def cited_path_line_pairs(text: str) -> list[tuple[str, str]]:
    """Every `path:line` citation in `text`, in order, without deduplicating --
    the raw occurrence count is what check 3's disclosure states, since a row
    citing the same bare shorthand twice is two undischarged citations, not one."""
    return [(m.group("path"), m.group("line")) for m in PATH_LINE_RE.finditer(text)]


def parse_evidence_units(text: str) -> dict[str, list[str]]:
    """unit id -> the file list from its own `Files:` line."""
    units: dict[str, list[str]] = {}
    current: str | None = None
    for line in text.split("\n"):
        hm = UNIT_HEADING_RE.match(line)
        if hm:
            current = hm.group(1)
            continue
        if current is not None:
            fm = FILES_LINE_RE.match(line)
            if fm:
                units[current] = [p.strip() for p in fm.group(1).split(",")]
                current = None
    return units


def parse_unit_ids(text: str) -> set[str]:
    return {m.group(1) for m in UNIT_HEADING_RE.finditer(text)}


# --------------------------------------------------------------------------- #
# check 1 -- manifest re-inventory
# --------------------------------------------------------------------------- #

def check_manifest() -> dict:
    text = (SKILL / "gap/manifest.md").read_text(encoding="utf-8")

    rev_m = re.search(r"^Revision:\s*(\S+)\s*$", text, re.MULTILINE)
    if not rev_m:
        fail("[manifest] no 'Revision:' line found")
        # Every return path has this same five-key shape (matching the normal
        # return at the bottom of this function): main() reads all five keys
        # unconditionally, so a malformed manifest must still produce a
        # complete, if empty, result -- an accumulated failure plus a full
        # printed report -- rather than a bare KeyError deep inside main().
        return {"revision": None, "rows": [], "assessed": {}, "excluded": {}, "tracked_files": set()}
    revision = rev_m.group(1)

    count_m = re.search(r"^Count:\s*(\d+)\s*$", text, re.MULTILINE)
    stated_count = int(count_m.group(1)) if count_m else None
    if count_m is None:
        fail("[manifest] no 'Count:' line found")

    rows = find_table_rows(text, "| path | scope | reason |", 3, "manifest")

    paths = [r[0] for r in rows]
    path_set = set(paths)
    if len(paths) != len(path_set):
        dupes = sorted({p for p in path_set if paths.count(p) > 1})
        fail(f"[manifest] path(s) listed more than once: {dupes}")

    revision_commit = resolve_commit(revision)
    if revision_commit is None:
        fail(f"[manifest] recorded revision {revision!r} does not resolve to a commit")
        actual_files: set[str] = set()
    else:
        actual_files = set(git_ls_tree(revision_commit, SKILL_REL))

    missing_from_manifest = actual_files - path_set
    extra_in_manifest = path_set - actual_files
    if missing_from_manifest or extra_in_manifest:
        fail(
            f"[manifest] does not match `git ls-tree {revision} -- {SKILL_REL}`: "
            f"tracked but unlisted={sorted(missing_from_manifest)}; "
            f"listed but not tracked at that revision={sorted(extra_in_manifest)}"
        )

    if stated_count is not None and stated_count != len(rows):
        fail(f"[manifest] stated Count: {stated_count} but the table has {len(rows)} row(s)")

    assessed: dict[str, str] = {}
    excluded: dict[str, str] = {}
    for path, scope, reason in rows:
        if scope == "assessed":
            assessed[path] = reason
        elif scope == "excluded":
            excluded[path] = reason
        else:
            fail(f"[manifest] {path} has an unrecognised scope {scope!r} (expected assessed/excluded)")

    for path, reason in excluded.items():
        if not reason or reason == "-":
            fail(f"[manifest] excluded file {path!r} carries no reason")

    tracked_files = path_set | actual_files
    return {
        "revision": revision,
        "rows": rows,
        "assessed": assessed,
        "excluded": excluded,
        "tracked_files": tracked_files,
    }


def check_cluster_mapping(assessed: dict[str, str]) -> tuple[dict[str, set[str]], dict[str, set[tuple[str, str]]]]:
    clusters_text = (SKILL / "gap/clusters.md").read_text(encoding="utf-8")
    cluster_rows = find_table_rows(clusters_text, "| path | cluster |", 2, "clusters")
    cluster_of: dict[str, str] = {}
    for path, cluster in cluster_rows:
        if path in cluster_of:
            fail(f"[clusters] {path!r} is assigned to more than one cluster")
        cluster_of[path] = cluster

    file_to_units: dict[str, set[tuple[str, str]]] = {}
    disposition_ids: dict[str, set[str]] = {}
    for cluster in CLUSTERS:
        ev_text = (SKILL / f"gap/evidence/{cluster}.md").read_text(encoding="utf-8")
        for unit_id, files in parse_evidence_units(ev_text).items():
            for f in files:
                file_to_units.setdefault(f, set()).add((cluster, unit_id))
        di_text = (SKILL / f"gap/dispositions/{cluster}.md").read_text(encoding="utf-8")
        disposition_ids[cluster] = parse_unit_ids(di_text)

    for path in sorted(assessed):
        cluster = cluster_of.get(path)
        if cluster is None:
            fail(f"[coverage] assessed file {path!r} is not assigned to any cluster in clusters.md")
            continue
        if cluster not in CLUSTERS:
            fail(f"[coverage] {path!r} is assigned to unrecognised cluster {cluster!r}")
            continue
        units_naming_it = {u for (c, u) in file_to_units.get(path, set()) if c == cluster}
        if not units_naming_it:
            fail(f"[coverage] assessed file {path!r} (cluster {cluster}) is named by no unit's "
                 f"'Files:' line in evidence/{cluster}.md")
            continue
        if not (units_naming_it & disposition_ids[cluster]):
            fail(f"[coverage] assessed file {path!r} (cluster {cluster}) is named only by unit(s) "
                 f"{sorted(units_naming_it)}, none of which has an entry in dispositions/{cluster}.md")

    return disposition_ids, file_to_units


# --------------------------------------------------------------------------- #
# check 2 -- requirements re-inventory
# --------------------------------------------------------------------------- #

REQ_HEADING_RE = re.compile(r"^### (RQA-(?:BR|FR|NFR)-\d{3})$", re.MULTILINE)


def check_requirements() -> tuple[set[str], dict[str, list[list[str]]]]:
    spec_text = (SKILL / "requirements/requirements-specification.md").read_text(encoding="utf-8")
    ids = REQ_HEADING_RE.findall(spec_text)
    dupes = sorted({x for x in set(ids) if ids.count(x) > 1})
    if dupes:
        fail(f"[requirements] duplicate '### RQA-...' heading(s) in the frozen specification: {dupes}")
    spec_ids = set(ids)

    register_rows: dict[str, list[list[str]]] = {}
    seen: dict[str, list[str]] = {}
    for cls in REGISTER_CLASSES:
        text = (SKILL / f"gap/register/{cls}.md").read_text(encoding="utf-8")
        rows = find_table_rows(
            text, "| id | gap degree | root cause | evidence | depends on | revision | notes |", 7,
            f"register/{cls}",
        )
        register_rows[cls] = rows
        for row in rows:
            seen.setdefault(row[0], []).append(cls)

    register_ids = set(seen)
    missing = sorted(spec_ids - register_ids)
    if missing:
        fail(f"[requirements] requirement(s) with no register row: {missing}")
    extra = sorted(register_ids - spec_ids)
    if extra:
        fail(f"[requirements] register row(s) key an ID that is not a frozen requirement: {extra}")
    multi = {rid: classes for rid, classes in seen.items() if len(classes) > 1}
    if multi:
        fail(f"[requirements] requirement ID(s) with more than one register row: {multi}")

    return spec_ids, register_rows


# --------------------------------------------------------------------------- #
# check 3 -- staleness
# --------------------------------------------------------------------------- #

def check_register_staleness(register_rows: dict[str, list[list[str]]], tracked_files: set[str]) -> None:
    for cls, rows in register_rows.items():
        for row in rows:
            rid, _degree, _cause, evidence, _depends, revision, notes = row
            row_commit = resolve_commit(revision)
            if row_commit is None:
                fail(f"[staleness] {rid} (register/{cls}.md): recorded revision {revision!r} "
                     f"does not resolve to a commit")
                continue
            raw_citations = cited_path_line_pairs(evidence) + cited_path_line_pairs(notes)
            resolvable: set[str] = set()
            for path, line in raw_citations:
                if path.startswith("gap/"):
                    # DELIBERATELY NOT CHECKED: a citation into gap/ itself. Every file
                    # under gap/ (this analysis's own output, e.g. RQA-FR-035's citation
                    # of gap/manifest.md:52) is necessarily committed after every row's
                    # recorded revision -- the analysis is written after the code it
                    # analyses -- so treating it as a staleness subject would fail that
                    # row PERMANENTLY on every future run, not occasionally. This is a
                    # one-instance, examined exclusion (all three of the maintainer's
                    # agent, and both review seats, confirmed it sound), not a loophole
                    # to widen: do not remove this branch to "catch more" citations.
                    continue
                if path in tracked_files:
                    resolvable.add(path)
                else:
                    # Bare module-name shorthand missing its directory prefix (e.g.
                    # `config.py:42` instead of `scripts/config.py:42`): check 3 cannot
                    # tell which tracked file it means, so it does not resolve it by
                    # guessing and does not check it. Disclosed, not silently dropped --
                    # see the NOT APPLICABLE report in main().
                    excluded_register_citations.append((cls, rid, path, line))
            for path in sorted(resolvable):
                rel = f"{SKILL_REL}/{path}"
                touch = last_touch_commit(rel)
                if touch is None:
                    continue
                if not is_ancestor(touch, row_commit) and not content_unchanged_since(row_commit, rel):
                    fail(
                        f"[staleness] {rid} (register/{cls}.md) cites {path}, last touched by "
                        f"{touch[:9]} which postdates the row's recorded revision {revision} ({row_commit[:9]})"
                    )


def check_evidence_staleness(manifest_revision: str | None, tracked_files: set[str]) -> None:
    if manifest_revision is None:
        return
    manifest_commit = resolve_commit(manifest_revision)
    if manifest_commit is None:
        return  # already reported by check_manifest
    for cluster in CLUSTERS:
        text = (SKILL / f"gap/evidence/{cluster}.md").read_text(encoding="utf-8")
        raw_citations = cited_path_line_pairs(text)
        resolvable: set[str] = set()
        for path, line in raw_citations:
            if path.startswith("gap/"):
                continue  # see the DELIBERATELY NOT CHECKED note in check_register_staleness
            if path in tracked_files:
                resolvable.add(path)
            else:
                excluded_evidence_citations.append((cluster, path, line))
        for path in sorted(resolvable):
            rel = f"{SKILL_REL}/{path}"
            touch = last_touch_commit(rel)
            if touch is None:
                continue
            if not is_ancestor(touch, manifest_commit) and not content_unchanged_since(manifest_commit, rel):
                fail(
                    f"[staleness] evidence/{cluster}.md cites {path}, last touched by {touch[:9]} "
                    f"which postdates the manifest revision {manifest_revision} ({manifest_commit[:9]})"
                )



# --------------------------------------------------------------------------- #
# check 4 -- open PENDING-HUMAN escalations
# --------------------------------------------------------------------------- #

# The marker grammar is three-way (gap/methodology.md §1, §4, §9):
#   PENDING-HUMAN:<real-id>   -- an escalation in use. The only form that fails.
#   PENDING-HUMAN:<short-id>  -- the definitional placeholder (literal angle
#                                 brackets), lives in gap/methodology.md, never a marker.
#   PENDING-HUMAN (no colon)  -- prose describing the mechanism, never a marker.
# A settled escalation's resolution prose names it by bare id (e.g. `RC-DECIDE`),
# never by quoting the marker string, so a real `PENDING-HUMAN:<id>` occurrence
# always means the escalation is still open.
MARKER_RE = re.compile(r"PENDING-HUMAN:(\S*)")
MARKER_ID_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]*")


def find_open_escalations() -> list[tuple[str, int, str]]:
    hits: list[tuple[str, int, str]] = []
    # Scanned as gap/**/*.md ONLY, never gap/**/*.py. This file's own source
    # necessarily contains the literal string "PENDING-HUMAN:" -- in this
    # comment, in MARKER_RE's pattern, in the docstring above -- so a scan that
    # widened to include gap/validate.py would report itself as an open
    # escalation on every run. Do not "fix" a narrow-looking glob by widening it.
    for path in sorted((SKILL / "gap").glob("**/*.md")):
        text = path.read_text(encoding="utf-8")
        rel = str(path.relative_to(SKILL))
        for m in MARKER_RE.finditer(text):
            token = m.group(1)
            if token.startswith("<"):
                continue  # `PENDING-HUMAN:<short-id>` -- the definitional placeholder
            id_m = MARKER_ID_RE.match(token)
            if not id_m:
                continue
            line_no = text.count("\n", 0, m.start()) + 1
            hits.append((rel, line_no, id_m.group(0)))
    return hits


# --------------------------------------------------------------------------- #
# main
# --------------------------------------------------------------------------- #

def main() -> int:
    manifest = check_manifest()
    disposition_ids, file_to_units = check_cluster_mapping(manifest["assessed"])
    spec_ids, register_rows = check_requirements()
    check_register_staleness(register_rows, manifest["tracked_files"])
    check_evidence_staleness(manifest["revision"], manifest["tracked_files"])
    escalations = find_open_escalations()

    total_units = sum(len(ids) for ids in disposition_ids.values())
    degree_counts: dict[str, int] = {}
    for rows in register_rows.values():
        for row in rows:
            degree_counts[row[1]] = degree_counts.get(row[1], 0) + 1

    print("=== estate re-inventory ===")
    print(f"- {len(manifest['rows'])} tracked file(s): {len(manifest['assessed'])} assessed, "
          f"{len(manifest['excluded'])} excluded")
    print(f"- {total_units} disposition unit(s) across {len(CLUSTERS)} clusters: "
          + ", ".join(f"{c}={len(disposition_ids.get(c, ()))}" for c in CLUSTERS))
    print(f"- {len(spec_ids)} frozen requirement(s): "
          + ", ".join(f"{cls}={len(register_rows.get(cls, ()))}" for cls in REGISTER_CLASSES))
    if degree_counts:
        print(f"- gap degrees: " + ", ".join(f"{k}={v}" for k, v in sorted(degree_counts.items())))

    print()
    print("=== checks 1-3: structural invariants ===")
    if structural_failures:
        print(f"FAIL \u2014 {len(structural_failures)} issue(s):\n")
        for f in structural_failures:
            print(f"- {f}")
    else:
        print("PASS \u2014 manifest, cluster/unit/disposition coverage, requirement-register "
              "completeness and evidence-revision staleness all check out.")

    n_reg_excluded = len(excluded_register_citations)
    n_ev_excluded = len(excluded_evidence_citations)
    n_excluded = n_reg_excluded + n_ev_excluded
    print()
    print("--- check 3: citations outside staleness scope ---")
    if n_excluded:
        reg_by_cls = ", ".join(
            f"{cls}={sum(1 for c, *_ in excluded_register_citations if c == cls)}" for cls in REGISTER_CLASSES
        )
        ev_by_cluster = ", ".join(
            f"{c}={sum(1 for cl, *_ in excluded_evidence_citations if cl == c)}" for c in CLUSTERS
        )
        print(
            f"NOT APPLICABLE to {n_excluded} citation(s) -- register: {n_reg_excluded} ({reg_by_cls}), "
            f"evidence: {n_ev_excluded} ({ev_by_cluster}). This is not a clean bill for them: each cites "
            f"a bare module-name shorthand missing its directory prefix (e.g. `config.py:42` instead of "
            f"`scripts/config.py:42`), which does not resolve to a manifest-tracked path, so check 3 "
            f"verified none of them for staleness."
        )
        for cls, rid, path, line in sorted(excluded_register_citations):
            print(f"  - {rid} (register/{cls}.md) cites {path}:{line}")
        for cluster, path, line in sorted(excluded_evidence_citations):
            print(f"  - evidence/{cluster}.md cites {path}:{line}")
    else:
        print("PASS \u2014 every citation check 3 found resolved to a manifest-tracked path.")

    print()
    print("=== check 4: open PENDING-HUMAN escalations ===")
    if escalations:
        distinct_ids = {marker_id for _rel, _line_no, marker_id in escalations}
        print(
            f"FAIL \u2014 {len(distinct_ids)} open escalation(s) awaiting a maintainer ruling, "
            f"across {len(escalations)} marker occurrence(s):\n"
        )
        for rel, line_no, marker_id in escalations:
            print(f"- {rel}:{line_no} PENDING-HUMAN:{marker_id}")
    else:
        print("PASS \u2014 no open PENDING-HUMAN markers.")

    return 1 if (structural_failures or escalations) else 0


if __name__ == "__main__":
    sys.exit(main())
