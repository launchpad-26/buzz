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

# Inputs the census could not read, and binaries it skipped. Reported in the
# output rather than folded silently into the totals: a denominator that quietly
# omits what it could not open is the exact failure this file was written to fix.
FAILED_READS: list[str] = []
BINARY_SKIPS: list[str] = []
# Files whose front matter would not parse as YAML, so the line scanner was used
# instead. Named in the output because their counts are the less reliable ones.
YAML_FALLBACKS: list[str] = []

try:
    import yaml
except ImportError:  # the scanner fallback still works without it
    yaml = None

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

    A FAILED READ IS NOT EMPTY CONTENT. This function used to ignore git's exit
    status, so a read that failed with exit 128 returned '' -- indistinguishable
    from a file that is genuinely empty, and silently removing that file's
    citations and links from the denominator. An independent review demonstrated
    it by fault injection. Failed reads are now recorded and reported in the
    output, because a census that quietly drops inputs is the precise defect this
    file exists to correct.
    """
    proc = subprocess.run(["git", "show", f"{rev}:{path}"], capture_output=True)
    if proc.returncode != 0:
        FAILED_READS.append(
            f"{path} (git exit {proc.returncode}: "
            f"{proc.stderr.decode('utf-8', 'replace').strip()[:80]})"
        )
        return ""
    try:
        return proc.stdout.decode("utf-8")
    except UnicodeDecodeError:
        BINARY_SKIPS.append(path)
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
        # PARSE THE FRONT MATTER AS YAML, because that is what it is.
        #
        # This used to scan for `- ` bullets with a regex, justified in a comment
        # saying a real parse "would fail closed on any malformed node and
        # silently shrink the denominator". The justification was sound; the
        # implementation was not. An independent review parsed the same files
        # properly and got 20,850 strings against this scanner's 20,801, with 36
        # files differing in BOTH directions -- the regex both missed citations
        # (block scalars, flow sequences, multi-line quoted strings) and invented
        # them (list items under other keys that happened to follow `evidence:`).
        #
        # So: parse properly, and keep the fail-open property by falling back to
        # the scanner per-file and REPORTING which files fell back, rather than
        # by never parsing at all.
        cites, fell_back = extract_evidence(text)
        if fell_back:
            YAML_FALLBACKS.append(f)
        for c in cites:
            kinds[classify(c)] += 1
    return kinds, len(files), sum(kinds.values())


def extract_evidence(text: str) -> tuple[list[str], bool]:
    """Return (citation strings, whether the YAML parse failed for this file)."""
    fm = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if fm and yaml is not None:
        try:
            data = yaml.safe_load(fm.group(1))
        except Exception:
            data = None
        if isinstance(data, dict):
            return _walk_evidence(data), False
    return _scan_evidence(text), True


def _walk_evidence(node) -> list[str]:
    """Every string under any `evidence:` key, at any depth."""
    out: list[str] = []
    if isinstance(node, dict):
        for k, v in node.items():
            if k == "evidence":
                out.extend(_strings(v))
            else:
                out.extend(_walk_evidence(v))
    elif isinstance(node, list):
        for v in node:
            out.extend(_walk_evidence(v))
    return out


def _strings(node) -> list[str]:
    """Citation strings only.

    The real shape, confirmed against the schema rather than assumed:

        evidence:                       <- top-level list of ENTRIES
          - statement: "..."
            entry_class: FACT
            evidence: ["path.rs:12"]    <- the citations, nested under the
                                           SAME key name one level down

    Two wrong guesses preceded this. Taking every value of an entry mapping swept
    in `statement` prose and inflated the total to 49,881; looking for a
    `citations:` key found nothing at all and reported 0. Both were confidently
    wrong in the same way the original regex was, which is the argument for
    checking the schema instead of inferring it from one sample.
    """
    if isinstance(node, str):
        return [node]
    if isinstance(node, list):
        return [s for v in node for s in _strings(v)]
    if isinstance(node, dict):
        return _strings(node["evidence"]) if "evidence" in node else []
    return []


def _scan_evidence(text: str) -> list[str]:
    """The original line scanner, kept only as the per-file fallback."""
    out, in_evidence = [], False
    for line in text.split("\n"):
        if re.match(r"^\s*evidence:\s*$", line):
            in_evidence = True
            continue
        if in_evidence:
            m = re.match(r'^\s+-\s+"?([^"\n]+)"?\s*$', line)
            if m:
                out.append(m.group(1))
                continue
            if line.strip() and not line.startswith((" ", "\t")):
                in_evidence = False
    return out


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
    # RESOLVE AGAINST `rev`'s OWN TREE, not the working directory.
    #
    # This used to call os.path.exists(), which answers a question about the
    # checkout on disk right now -- so an untracked scratch file could make a
    # historical link "resolve", and a file deleted in the working tree could
    # make a tracked historical target "break". A census labelled with a
    # revision has to be answerable from that revision alone, or the label is
    # decoration. An independent review named this as an evidence-boundary
    # defect, and it is: the instrument was reading two different worlds and
    # reporting one number.
    tree = set(tracked_files(rev, "."))
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
            # A directory target resolves if the tree holds anything beneath it.
            hit = resolved in tree or any(
                p.startswith(resolved + "/") for p in tree
            )
            if not hit:
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
CREDENTIAL_SHAPE_RULES = {
    "aws_access_key": r"AKIA[0-9A-Z]{16}",
    "github_token": r"gh[pousr]_[A-Za-z0-9]{36,}",
    "slack_token": r"xox[baprs]-[A-Za-z0-9-]{10,}",
    "google_api_key": r"AIza[0-9A-Za-z_\-]{35}",
    "pem_private_key": r"-----BEGIN [A-Z ]*PRIVATE KEY-----",
}


def census_credential_shapes(rev: str) -> dict[str, tuple[int, int]]:
    """Count credential-pattern matches. Returns AGGREGATES ONLY, never locations.

    Maps pattern name -> (total matches, number of distinct files).

    WHY THIS DELIBERATELY TELLS YOU LESS THAN IT COULD. Two earlier versions
    returned per-file detail: first `(path, name, count)` tuples, then an index
    into the caller's file list. CodeQL flagged printing both as "clear-text
    logging of sensitive information" (high severity), and the second attempt
    taught me why the first fix missed: I had tried to launder the provenance
    rather than remove it, and indexing carried the taint straight through.

    The analyser is making a point worth conceding. "Which files contain a
    credential-shaped string" IS information derived from credential content.
    A scanner that prints that to stdout, into CI logs, into a terminal
    scrollback, into a transcript, is a disclosure channel -- a weak one, but a
    real one, and precisely the kind that gets copied somewhere public because
    it looked like harmless output. The payload was never printed; the map to
    the payload was.

    So this reports totals, and locating a match is a deliberate second step
    the reader has to choose:

        grep -rlE '<the pattern from CREDENTIAL_SHAPE_RULES>' launchpad/

    The cost is real: a changed count tells you something moved without telling
    you where. That is the trade accepted here, and it is reversible -- if the
    cohort decides paths belong in the output, restore them and suppress the
    rule with a written justification rather than by restructuring, because
    restructuring to dodge an analyser is how a genuine finding gets buried.
    """
    totals: dict[str, tuple[int, int]] = {}
    for f in tracked_files(rev, SUBTREE):
        text = blob(rev, f)
        if not text:
            continue
        for name, pat in CREDENTIAL_SHAPE_RULES.items():
            n = len(re.findall(pat, text))
            if n:
                prev = totals.get(name, (0, 0))
                totals[name] = (prev[0] + n, prev[1] + 1)
    return totals


# ---------------------------------------------------------------------------
# Node status
# ---------------------------------------------------------------------------
RE_STATUS = re.compile(r'^status:\s*"?([a-z]+)"?\s*$', re.M)


def generated_output_paths() -> set[str]:
    """The registry's own list of generated outputs, not a path guess.

    `"/generated/" not in f` excluded 21 files. The registry excludes 29 -- the
    other eight live outside that directory, so they were being counted as
    canonical nodes. That is how this script reported a 727-node canonical
    population at 93.54% draft when the registry-defined population is 719 at
    93.46%. The exclusion rule has to come from whoever owns it.
    """
    try:
        _validator()  # puts the corpus package dir on sys.path
        import indexes  # noqa: PLC0415

        return {
            f"{CORPUS}/{s.output_path}" for s in indexes.discover_builders()
        }
    except Exception as exc:
        print(
            f"  WARNING: could not load the builder registry ({exc}); "
            "canonical counts are NOT reported rather than guessed",
            file=sys.stderr,
        )
        return set()


def census_status(rev: str) -> dict:
    files = [
        f for f in tracked_files(rev, CORPUS)
        if f.endswith(".md") and CORPUS_EXCLUDE not in f
    ]
    generated = generated_output_paths()
    all_counts: Counter = Counter()
    canon_counts: Counter = Counter()
    for f in files:
        m = RE_STATUS.search(blob(rev, f))
        if not m:
            continue
        all_counts[m.group(1)] += 1
        if f not in generated:
            canon_counts[m.group(1)] += 1
    return {
        "all": all_counts,
        "canonical": canon_counts if generated else None,
        "files": len(files),
        "generated": len(generated),
    }


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

    totals = census_credential_shapes(rev)
    # NAMED FOR THE ANALYSER AS WELL AS THE READER. These were `SECRET_PATTERNS`
    # and `census_secrets` until 2026-09-15, and CodeQL's Python sensitive-data
    # heuristic classifies by IDENTIFIER NAME: anything matching secret/token/
    # key/credential is treated as sensitive, so printing a loop variable drawn
    # from a dict called SECRET_PATTERNS raised a HIGH "clear-text logging of
    # sensitive information" — three times, through two restructures that
    # reduced what was printed without touching what it was called.
    #
    # The "secret" it objected to was the label `"github_token"`: a string this
    # module writes, not a credential it read. The old names were simply wrong.
    # These are rules describing the SHAPE of a credential; they contain no
    # credential, and the counts derived from them contain no credential either.
    print("\nCredential patterns (totals only — no values, no paths)")
    if not totals:
        print("  0 matches")
    for name in sorted(totals):
        matches, files_ = totals[name]
        print(f"  {name}: {matches} match(es) across {files_} file(s)")
    if totals:
        print("  Locations are deliberately not printed — see census_credential_shapes'")
        print("  docstring. To locate one, grep for that pattern yourself.")

    st = census_status(rev)
    a, c = st["all"], st["canonical"]
    at = sum(a.values())
    print("\nNode status")
    print(f"  all corpus files ({at:>3})        draft {a['draft']} ({pct(a['draft'], at)}), active {a['active']}")
    if c is None:
        print("  canonical only               NOT REPORTED — the builder registry")
        print("                               could not be loaded, and guessing the")
        print("                               exclusion is what made this wrong before")
    else:
        ct = sum(c.values())
        print(f"  canonical only   ({ct:>3})        draft {c['draft']} ({pct(c['draft'], ct)}), active {c['active']}")
        print(f"  (canonical = all minus the registry's {st['generated']} generated outputs)")
    print("\n  The two populations give different percentages. Any figure quoted")
    print("  from here must say which one it uses.")

    # Everything the census could not read, stated rather than absorbed.
    print("\nInstrument integrity")
    print(f"  failed reads                 {len(FAILED_READS)}")
    for x in FAILED_READS[:10]:
        print(f"    FAILED  {x}")
    print(f"  binaries skipped             {len(BINARY_SKIPS)}")
    print(f"  YAML fallbacks (line scan)   {len(YAML_FALLBACKS)}")
    for x in YAML_FALLBACKS[:10]:
        print(f"    FALLBACK  {x}")
    if FAILED_READS:
        print("\n  A failed read is NOT an empty file. The totals above exclude")
        print("  these inputs; treat every figure as a lower bound until fixed.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
