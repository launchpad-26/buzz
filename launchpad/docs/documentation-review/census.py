#!/usr/bin/env python3
"""Deterministic census over the launchpad/ subtree.

WHY THIS FILE EXISTS. The first run of this audit reported its census figures --
citation counts, link counts, credential-pattern matches -- from throwaway shell
pipelines that were never committed. Two independent reviewers then tried to
reproduce them and could not: both landed on 18,791 repository-path citations of
20,850 strings where the report claimed 18,715 of 20,680, and neither could
reproduce the "745 relative links" denominator by ANY reasonable method (they got
1,515 raw, 895 deduplicated, 1,273 excluding fragments).

A number nobody can reproduce is not a measurement, it is an assertion wearing a
measurement's clothes -- and the audit that published those numbers is the same
document that criticises `coverage.md` for a disposition earned by a rule it does
not state. That is the defect this file closes.

The rules below are therefore written down rather than implied, because the
denominator IS the claim. Change a rule and you change the number; so the rule
travels with the number.

Run:  python3 census.py            (from this directory, or anywhere in the repo)
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from collections import Counter

# ---------------------------------------------------------------------------
# Scope
# ---------------------------------------------------------------------------
# The audited subtree. Everything outside it belongs to upstream `block/buzz`
# and is explicitly out of scope for this audit.
SUBTREE = "launchpad"

# The corpus, excluding its JSON Schema directory. `schema/` holds the schema
# itself rather than nodes described by it, so counting it as corpus content
# would inflate the node population with its own definition.
CORPUS = "launchpad/docs/corpus"
CORPUS_EXCLUDE = "/schema/"

# ---------------------------------------------------------------------------
# Citation forms — IMPORTED, never reimplemented
# ---------------------------------------------------------------------------
# `launchpad/project-intelligence/corpus/validate.py` already decides what
# counts as a repository-path citation. This module imports that decision
# instead of restating it.
#
# THE REASON IS MEASURED, NOT STYLISTIC. When the audit's figures were
# challenged, three parties independently reimplemented the classifier and got
# three different answers over the same 748 files:
#
#     original audit   18,715 repo-path of 20,680 strings
#     two reviewers    18,791 of 20,850   (agreeing with each other)
#     a first draft of this file          18,399 of 20,801
#
# None was lying; each drew the category boundary somewhere slightly different.
# A definition restated is a definition forked, and a forked definition makes
# the number unfalsifiable -- every party can "reproduce" their own. So the
# validator is the single authority, and if its rules are wrong they are wrong
# in exactly one place.
RE_URL = re.compile(r"^(https?|mailto):")

_VALIDATE = None


def _validator():
    """Import the repository's own citation classifier, lazily."""
    global _VALIDATE
    if _VALIDATE is None:
        root = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, check=True,
        ).stdout.strip()
        sys.path.insert(0, os.path.join(root, "launchpad/project-intelligence/corpus"))
        import validate as _v  # type: ignore
        _VALIDATE = _v
    return _VALIDATE


def tracked_files(rev: str, pathspec: str) -> list[str]:
    out = subprocess.run(
        ["git", "ls-tree", "-r", "--name-only", rev, "--", pathspec],
        capture_output=True, text=True, check=True,
    ).stdout.split("\n")
    return [f for f in out if f]


def blob(rev: str, path: str) -> str:
    """Read a blob as text. Binary files decode to '' rather than crashing.

    The first run of this script died on a PNG with UnicodeDecodeError, which
    would have aborted the census partway and reported nothing -- a census that
    fails closed on one binary file is worse than one that skips it, provided
    it says so. Binary files carry no citations or Markdown links by
    definition, so skipping them changes no number here.
    """
    out = subprocess.run(
        ["git", "show", f"{rev}:{path}"], capture_output=True,
    ).stdout
    try:
        return out.decode("utf-8")
    except UnicodeDecodeError:
        return ""


def classify(cite: str) -> str:
    """Delegate to the validator; collapse its verdict to a census bucket."""
    v = _validator()
    c = cite.strip().strip("\"'")
    if not c:
        return "empty"
    if RE_URL.match(c):
        return "url"
    if v._COMMIT_CITATION_RE.match(c) or v._FULL_SHA_RE.match(c):
        return "commit"
    if v._GRAPH_EDGE_RE.match(c) or v._TOOL_RESULT_RE.match(c):
        return "graph_edge_or_tool_result"
    # A repository-path citation is one the validator can resolve to a path:
    # either `path:LINE[-END]` or a bare path. Markdown-link citations carry
    # their target inside the parentheses.
    m = v._MARKDOWN_LINK_RE.match(c)
    if m:
        c = m.group("target")
        if RE_URL.match(c):
            return "url"
    if v._FILE_POSITION_RE.match(c):
        return "repo_path"
    if "/" in c and " " not in c:
        return "repo_path"
    return "other"


def census_citations(rev: str) -> tuple[Counter, int, int]:
    """Every string in an `evidence:` list of every corpus node."""
    files = [
        f for f in tracked_files(rev, CORPUS)
        if f.endswith(".md") and CORPUS_EXCLUDE not in f
    ]
    kinds: Counter = Counter()
    for f in files:
        text = blob(rev, f)
        # Evidence citations are YAML list items nested under `evidence:`.
        # Matching the bullet directly is deliberate: a full YAML parse would
        # fail closed on any malformed node and silently shrink the denominator.
        in_evidence = False
        for line in text.split("\n"):
            if re.match(r"^\s*evidence:\s*$", line):
                in_evidence = True
                continue
            if in_evidence:
                m = re.match(r'^\s+-\s+"?([^"\n]+)"?\s*$', line)
                if m:
                    kinds[classify(m.group(1))] += 1
                    continue
                if line.strip() and not line.startswith((" ", "\t")):
                    in_evidence = False
    return kinds, len(files), sum(kinds.values())


# ---------------------------------------------------------------------------
# Relative links
# ---------------------------------------------------------------------------
RE_LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)")


def census_links(rev: str) -> dict:
    """Relative Markdown links under the subtree.

    THE RULE, stated because it sets the denominator:
      * source: every tracked `.md` file under `launchpad/`
      * counted: `[text](target)` where target is NOT http(s)/mailto and NOT
        anchor-only (`#frag`)
      * a target's `#fragment` is stripped before resolution; anchors are not
        verified (nothing here resolves heading anchors)
      * EVERY OCCURRENCE counts, not unique (file, target) pairs -- a broken
        link is broken once per place a reader can hit it
    """
    files = [f for f in tracked_files(rev, SUBTREE) if f.endswith(".md")]
    total = broken = 0
    broken_list: list[str] = []
    for f in files:
        for target in RE_LINK.findall(blob(rev, f)):
            if RE_URL.match(target) or target.startswith("#"):
                continue
            total += 1
            resolved = os.path.normpath(
                os.path.join(os.path.dirname(f), target.split("#")[0])
            )
            if not os.path.exists(resolved):
                broken += 1
                broken_list.append(f"{f} -> {target}")
    return {
        "files": len(files),
        "total": total,
        "broken": broken,
        "broken_list": broken_list,
    }


# ---------------------------------------------------------------------------
# Credential patterns
# ---------------------------------------------------------------------------
# Counts and filenames ONLY. A matched value is NEVER printed: reproducing a
# suspected credential into a transcript is the harm the check exists to find.
SECRET_PATTERNS = {
    "aws_access_key": r"AKIA[0-9A-Z]{16}",
    "github_token": r"gh[pousr]_[A-Za-z0-9]{36,}",
    "slack_token": r"xox[baprs]-[A-Za-z0-9-]{10,}",
    "google_api_key": r"AIza[0-9A-Za-z_\-]{35}",
    "pem_private_key": r"-----BEGIN [A-Z ]*PRIVATE KEY-----",
}


def census_secrets(rev: str) -> dict[tuple[int, str], int]:
    """Count credential-pattern matches. Returns COUNTS ONLY.

    The return type is deliberate. An earlier version returned
    `(path, pattern_name, count)` tuples, and CodeQL flagged printing them as
    "clear-text logging of sensitive information" (high). Reading the flag
    closely, it was right about the shape even though the printed values were
    safe: the tuple left a function that had the file's text in scope, so every
    field carried that provenance, and a later edit could have widened the tuple
    to include a match without any reviewer noticing the type had changed
    meaning.

    Now nothing leaves this function but an INDEX into the caller's own file
    list, a pattern NAME the caller already holds, and an integer. The caller
    prints strings it supplied itself. That is not a workaround for the
    analyser; it is the property the analyser was asking for, and the reason a
    scanner reviewing a scanner was worth listening to.
    """
    files = tracked_files(rev, SUBTREE)
    counts: dict[tuple[int, str], int] = {}
    for i, f in enumerate(files):
        text = blob(rev, f)
        if not text:
            continue
        for name, pat in SECRET_PATTERNS.items():
            n = len(re.findall(pat, text))
            if n:
                counts[(i, name)] = n
    return counts


# ---------------------------------------------------------------------------
# Node status
# ---------------------------------------------------------------------------
RE_STATUS = re.compile(r'^status:\s*"?([a-z]+)"?\s*$', re.M)


def census_status(rev: str) -> dict:
    files = [
        f for f in tracked_files(rev, CORPUS)
        if f.endswith(".md") and CORPUS_EXCLUDE not in f
    ]
    all_counts: Counter = Counter()
    canon_counts: Counter = Counter()
    for f in files:
        m = RE_STATUS.search(blob(rev, f))
        if not m:
            continue
        all_counts[m.group(1)] += 1
        if "/generated/" not in f:
            canon_counts[m.group(1)] += 1
    return {"all": all_counts, "canonical": canon_counts, "files": len(files)}


def pct(n: int, d: int) -> str:
    return f"{100 * n / d:.2f}%" if d else "n/a"


def main() -> int:
    rev = sys.argv[1] if len(sys.argv) > 1 else "HEAD"
    root = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True, text=True, check=True,
    ).stdout.strip()
    os.chdir(root)

    sha = subprocess.run(
        ["git", "rev-parse", rev], capture_output=True, text=True, check=True
    ).stdout.strip()
    print(f"Census of {SUBTREE}/ at {sha}\n")

    kinds, nfiles, ntotal = census_citations(rev)
    print("Citations (corpus evidence ledgers)")
    print(f"  files scanned                {nfiles}")
    print(f"  citation strings, total      {ntotal}")
    print(f"  repository-path citations    {kinds['repo_path']}")
    for k in sorted(kinds):
        if k != "repo_path":
            print(f"    {k:<26} {kinds[k]}")

    links = census_links(rev)
    print("\nRelative links (every occurrence, not unique pairs)")
    print(f"  markdown files scanned       {links['files']}")
    print(f"  relative links               {links['total']}")
    print(f"  resolve                      {links['total'] - links['broken']}")
    print(f"  broken                       {links['broken']}")
    for b in links["broken_list"]:
        print(f"    BROKEN  {b}")

    counts = census_secrets(rev)
    print("\nCredential patterns (counts only; values never printed)")
    if not counts:
        print("  0 matches")
    # Every string printed here is one MAIN already held: a path from
    # `git ls-tree`, and a key of this module's own SECRET_PATTERNS literal.
    # Nothing that passed through the file's text reaches stdout.
    paths = tracked_files(rev, SUBTREE)
    for (idx, name), n in sorted(counts.items()):
        print(f"  {paths[idx]}: {int(n)} match(es) of {name} [value NOT reproduced]")

    st = census_status(rev)
    a, c = st["all"], st["canonical"]
    at, ct = sum(a.values()), sum(c.values())
    print("\nNode status")
    print(f"  all corpus files ({at:>3})        draft {a['draft']} ({pct(a['draft'], at)}), active {a['active']}")
    print(f"  canonical only   ({ct:>3})        draft {c['draft']} ({pct(c['draft'], ct)}), active {c['active']}")
    print("\n  The two populations give different percentages. Any figure quoted")
    print("  from here must say which one it uses.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
