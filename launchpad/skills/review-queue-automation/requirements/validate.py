#!/usr/bin/env python3
"""Deterministic validator for the RQA requirements specification (C-T shape).

Compares the current candidate files against the frozen baseline commit and checks every
invariant. Strict full byte-identity mode: every requirement field (statement, fit, EARS,
priority, status, ADR), every ordered source-clause ID and verbatim quote, and every QA
verdict must match the frozen baseline exactly. Stdlib only. Run from anywhere; paths are
relative to this file.

    python3 validate.py

Exits non-zero and prints every failure found (does not stop at the first one).
"""
from __future__ import annotations

import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[3]  # .../buzz
# Baseline prior to the round-9b corrections. The orchestrator substitutes the actual
# commit SHA (which will contain the round-9b document corrections) here after commit;
# that commit is in the same C-T block shape and is parsed with the same block parser.
# An explicit BUZZ_FROZEN_COMMIT env override is honoured for one-off proof runs without
# editing the committed placeholder.
FROZEN_COMMIT = __import__("os").environ.get("BUZZ_FROZEN_COMMIT", "R9B-COMMIT")
FROZEN_SPEC_PATH = "launchpad/skills/review-queue-automation/requirements/requirements-specification.md"
FROZEN_QA_PATH = "launchpad/skills/review-queue-automation/requirements/requirements-quality-assessment.md"
FROZEN_CLAUSE_PATH = "launchpad/skills/review-queue-automation/requirements/clause-inventory.md"
FROZEN_SPLIT_PATH = "launchpad/skills/review-queue-automation/requirements/singular-splits.md"

CHAR_ORDER = [
    "Necessary", "Appropriate", "Unambiguous", "Complete", "Singular",
    "Feasible", "Verifiable", "Correct", "Conforming",
]

failures: list[str] = []


def fail(msg: str) -> None:
    failures.append(msg)


# --------------------------------------------------------------------------- #
# git access
# --------------------------------------------------------------------------- #

def git_show(commit: str, path: str) -> str:
    result = subprocess.run(
        ["git", "show", f"{commit}:{path}"],
        cwd=REPO_ROOT, capture_output=True, text=True, check=True,
    )
    return result.stdout


# --------------------------------------------------------------------------- #
# shared table-parsing helpers
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


# --------------------------------------------------------------------------- #
# candidate + frozen baseline: both are C-T block-shaped, so both sides are parsed
# with the same block parser below.
# --------------------------------------------------------------------------- #

BLOCK_RE = re.compile(
    r"^### (RQA-(?:BR|FR|NFR)-\d{3})\n\n(.+?)\n\n\*In plain terms: (.+?)\*\n\n"
    r"`([^`]+)` \u00b7 `([^`]+)` \u00b7 (`[^`]+`) \u00b7 ADR: (.+?)\n\n"
    r"\*\*Source:\*\*\n(.+?)\n\n\*\*Fit criterion:\*\* (.+?)"
    r"(?:\n\n\*\*See also:\*\*.*?)?(?=\n### |\n---|\Z)",
    re.DOTALL | re.MULTILINE,
)
SRC_BULLET_RE = re.compile(
    r"^- \*\*(CL-\d{3})\*\* \(([^)]*), \[extract\]\(([^)]*)\)\): [\u201c\"](.+?)[\u201d\"]$",
    re.MULTILINE,
)


def parse_candidate_spec(text: str) -> dict:
    records = {}
    for m in BLOCK_RE.finditer(text):
        rid, stmt, _gloss, ears, pri, status, adr, src_block, fit = m.groups()
        clause_list = SRC_BULLET_RE.findall(src_block)
        records[rid] = {
            "id": rid, "statement": stmt.strip(), "ears": ears.strip(),
            "priority": pri.strip(), "status": status.strip(), "fit": fit.strip(),
            "clauses": [(cid, sec.strip(), link.strip(), quote.strip())
                        for cid, sec, link, quote in clause_list],
            "adr": adr,
        }
    return records


def parse_candidate_qa(text: str) -> dict:
    by_id: dict[str, dict[str, str]] = defaultdict(dict)
    blocks = re.split(r"^### (RQA-(?:BR|FR|NFR)-\d{3})$", text, flags=re.MULTILINE)
    for i in range(1, len(blocks), 2):
        rid = blocks[i]
        body = blocks[i + 1]
        for char, verdict in re.findall(r"\| (\w+) \| (Pass|Caveat) \|", body):
            if char in CHAR_ORDER:
                by_id[rid][char] = verdict
    return by_id


def parse_candidate_clause_inventory(text: str) -> dict:
    lines = text.split("\n")
    ci_idx = next(i for i, l in enumerate(lines) if l.startswith("| Clause | Section | Verbatim text"))
    clause_rows = parse_table_rows(lines, ci_idx)
    clauses = {}
    for row in clause_rows:
        cid = re.match(r"\*\*(CL-\d{3})\*\*", row[0]).group(1)
        clauses[cid] = {
            "label": row[0], "section_link": row[1], "verbatim": row[2],
            "disposition": row[3], "note": row[4],
        }
    return clauses


def parse_candidate_singular_splits(text: str) -> list[str]:
    lines = text.split("\n")
    header = "| Clause | Source label | Requirements produced | How the split was drawn |"
    idx = next(i for i, l in enumerate(lines) if l == header)
    rows = parse_table_rows(lines, idx)
    return [re.match(r"\*\*(CL-\d{3})\*\*", r[0]).group(1) for r in rows]


def parse_candidate_heading_ids(text: str) -> list[str]:
    exact = re.compile(r"^### RQA-(BR|FR|NFR)-[0-9]{3}$")
    heading_lines = [l for l in text.split("\n") if l.startswith("### ")]
    bad = [l for l in heading_lines if not exact.match(l)]
    if bad:
        fail(f"[candidate] {len(bad)} '### ' heading(s) do not match the exact ID regex: {bad[:5]}")
    ids = [l[len('### '):] for l in heading_lines if exact.match(l)]
    if len(ids) != len(set(ids)):
        dupes = [x for x in set(ids) if ids.count(x) > 1]
        fail(f"[candidate] duplicate requirement heading(s): {dupes}")
    return ids


# --------------------------------------------------------------------------- #
# link resolution
# --------------------------------------------------------------------------- #

LINK_MD_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
HEADING_RE_ANY = re.compile(r"^(#{1,6}) (.+)$", re.MULTILINE)


def github_slug(heading_text: str) -> str:
    s = heading_text.strip().lower()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"\s+", "-", s)
    return s


def heading_slugs(text: str) -> set[str]:
    slugs: set[str] = set()
    seen: dict[str, int] = {}
    for _level, heading_text in HEADING_RE_ANY.findall(text):
        base = github_slug(heading_text)
        n = seen.get(base, 0)
        slugs.add(base if n == 0 else f"{base}-{n}")
        seen[base] = n + 1
    return slugs


_slug_cache: dict[Path, set[str]] = {}


def slugs_for_file(p: Path) -> set[str]:
    p = p.resolve()
    if p not in _slug_cache:
        try:
            _slug_cache[p] = heading_slugs(p.read_text(encoding="utf-8")) if p.suffix == ".md" else set()
        except OSError:
            _slug_cache[p] = set()
    return _slug_cache[p]


def check_links_resolve(path: Path, text: str) -> None:
    own_slugs = heading_slugs(text)
    for m in LINK_MD_RE.finditer(text):
        target = m.group(1)
        if target.startswith(("http://", "https://", "mailto:")):
            continue
        file_part, has_hash, anchor = target.partition("#")
        if not file_part:
            if has_hash and anchor and anchor not in own_slugs:
                fail(f"[links] {path.name}: in-page anchor '#{anchor}' does not match any heading")
            continue
        resolved = (path.parent / file_part).resolve()
        if not resolved.exists():
            fail(f"[links] {path.name}: '{target}' does not resolve (missing {resolved})")
            continue
        if has_hash and anchor:
            target_slugs = slugs_for_file(resolved)
            if target_slugs and anchor not in target_slugs:
                fail(f"[links] {path.name}: '{target}' — anchor '#{anchor}' not found in {resolved.name}")


# --------------------------------------------------------------------------- #
# main
# --------------------------------------------------------------------------- #

def main() -> int:
    frozen_spec_text = git_show(FROZEN_COMMIT, FROZEN_SPEC_PATH)
    frozen_qa_text = git_show(FROZEN_COMMIT, FROZEN_QA_PATH)
    frozen_clause_text = git_show(FROZEN_COMMIT, FROZEN_CLAUSE_PATH)
    frozen_split_text = git_show(FROZEN_COMMIT, FROZEN_SPLIT_PATH)
    frozen = parse_candidate_spec(frozen_spec_text)
    frozen_qa = parse_candidate_qa(frozen_qa_text)
    frozen_clauses = parse_candidate_clause_inventory(frozen_clause_text)
    frozen_split_clause_ids = parse_candidate_singular_splits(frozen_split_text)

    candidate_spec_text = (HERE / "requirements-specification.md").read_text(encoding="utf-8")
    candidate_qa_text = (HERE / "requirements-quality-assessment.md").read_text(encoding="utf-8")
    candidate_clause_text = (HERE / "clause-inventory.md").read_text(encoding="utf-8")
    candidate_split_text = (HERE / "singular-splits.md").read_text(encoding="utf-8")

    candidate = parse_candidate_spec(candidate_spec_text)
    candidate_clauses = parse_candidate_clause_inventory(candidate_clause_text)
    candidate_qa = parse_candidate_qa(candidate_qa_text)
    candidate_split_clause_ids = parse_candidate_singular_splits(candidate_split_text)
    candidate_heading_ids = parse_candidate_heading_ids(candidate_spec_text)

    # ---- 1. per-ID field-level byte equality ---- #
    frozen_ids = set(frozen)
    candidate_ids = set(candidate)
    if frozen_ids != candidate_ids:
        fail(f"[equality] ID set differs. Missing from candidate: {sorted(frozen_ids - candidate_ids)}; "
             f"extra in candidate: {sorted(candidate_ids - frozen_ids)}")

    for rid in sorted(frozen_ids & candidate_ids):
        f_rec = frozen[rid]
        c_rec = candidate[rid]
        for field in ("statement", "ears", "priority", "status", "fit", "adr"):
            if f_rec[field] != c_rec[field]:
                fail(f"[equality] {rid}.{field} differs.\n  frozen:    {f_rec[field]!r}\n  candidate: {c_rec[field]!r}")
        f_clause_ids = [c[0] for c in f_rec["clauses"]]
        c_clause_ids = [c[0] for c in c_rec["clauses"]]
        if f_clause_ids != c_clause_ids:
            fail(f"[equality] {rid} ordered source-clause IDs differ: frozen={f_clause_ids} candidate={c_clause_ids}")
        for (f_cid, f_sec, _f_link, f_quote), (c_cid, c_sec, _c_link, c_quote) in zip(f_rec["clauses"], c_rec["clauses"]):
            if f_quote is None or c_quote is None or f_quote.strip() != c_quote.strip():
                fail(f"[equality] {rid} verbatim quote for {f_cid} differs")
            if f_sec.strip() != c_sec.strip():
                fail(f"[equality] {rid} section label for {f_cid} differs: frozen={f_sec!r} candidate={c_sec!r}")

    # ---- 2. 86 unique blocks ---- #
    if len(candidate_heading_ids) != 86:
        fail(f"[counts] expected 86 requirement headings, found {len(candidate_heading_ids)}")

    # ---- 3. 65 exactly-once clause dispositions ---- #
    if len(candidate_clauses) != 65:
        fail(f"[counts] expected 65 clauses in clause-inventory.md, found {len(candidate_clauses)}")
    for cid, c in candidate_clauses.items():
        if c["disposition"] not in ("Derived", "Derived \u2014 traceability rule", "Scope exclusion", "Context \u2014 no obligation"):
            fail(f"[dispositions] {cid} has an unrecognised disposition: {c['disposition']!r}")

    for cid, f_c in frozen_clauses.items():
        c_c = candidate_clauses.get(cid)
        if c_c is None:
            fail(f"[equality] clause {cid} missing from candidate clause-inventory.md")
            continue
        if f_c["verbatim"].strip() != c_c["verbatim"].strip():
            fail(f"[equality] clause {cid} verbatim text differs between frozen and candidate")
        if f_c["disposition"].strip() != c_c["disposition"].strip():
            fail(f"[equality] clause {cid} disposition differs: frozen={f_c['disposition']!r} candidate={c_c['disposition']!r}")
    if set(frozen_clauses) != set(candidate_clauses):
        fail(f"[equality] clause ID set differs: frozen-only={sorted(set(frozen_clauses)-set(candidate_clauses))} "
             f"candidate-only={sorted(set(candidate_clauses)-set(frozen_clauses))}")
    if set(frozen_split_clause_ids) != set(candidate_split_clause_ids):
        fail(f"[equality] singular-splits.md row set differs: frozen-only="
             f"{sorted(set(frozen_split_clause_ids)-set(candidate_split_clause_ids))} candidate-only="
             f"{sorted(set(candidate_split_clause_ids)-set(frozen_split_clause_ids))}")

    # ---- 4. 95 requirement->clause edges ---- #
    candidate_edges = sum(len(r["clauses"]) for r in candidate.values())
    frozen_edges = sum(len(r["clauses"]) for r in frozen.values())
    if candidate_edges != frozen_edges:
        fail(f"[counts] requirement->clause edge count differs: frozen={frozen_edges} candidate={candidate_edges}")
    if candidate_edges != 95:
        fail(f"[counts] expected 95 requirement->clause edges, found {candidate_edges}")

    # ---- 5. 26 splits ---- #
    clause_to_reqs = defaultdict(list)
    for rid, rec in candidate.items():
        for cid, *_ in rec["clauses"]:
            clause_to_reqs[cid].append(rid)
    n_splits = sum(1 for reqs in clause_to_reqs.values() if len(reqs) > 1)
    if n_splits != 26:
        fail(f"[counts] expected 26 split clauses, found {n_splits}")
    split_rows_set = set(candidate_split_clause_ids)
    computed_split_set = {cid for cid, reqs in clause_to_reqs.items() if len(reqs) > 1}
    if split_rows_set != computed_split_set:
        fail(f"[counts] singular-splits.md rows {sorted(split_rows_set)} != computed split set {sorted(computed_split_set)}")

    # ---- 6. 774 QA judgements, 9 per ID ---- #
    total_qa = sum(len(v) for v in candidate_qa.values())
    if total_qa != 774:
        fail(f"[counts] expected 774 QA judgements, found {total_qa}")
    for rid in candidate_ids:
        chars = candidate_qa.get(rid, {})
        if set(chars) != set(CHAR_ORDER):
            fail(f"[qa] {rid} does not carry exactly the nine characteristics: {sorted(chars)}")
    for rid in sorted(frozen_ids & candidate_ids):
        for char in CHAR_ORDER:
            f_v = frozen_qa.get(rid, {}).get(char)
            c_v = candidate_qa.get(rid, {}).get(char)
            if f_v != c_v:
                fail(f"[qa-equality] {rid}.{char} verdict differs: frozen={f_v} candidate={c_v}")

    # ---- 7. class-index completeness ---- #
    for label, prefix in (("Business requirements", "BR"), ("Functional requirements", "FR"), ("Non-functional requirements", "NFR")):
        header_match = re.search(rf"\*\*{re.escape(label)} \((\d+)\):\*\*", candidate_spec_text)
        if not header_match:
            fail(f"[class-index] could not find class index header for {label!r}")
            continue
        count = int(header_match.group(1))
        block_start = header_match.end()
        next_marker = re.search(r"\n\n(?:\*\*|##)", candidate_spec_text[block_start:])
        block_end = block_start + next_marker.start() if next_marker else len(candidate_spec_text)
        block = candidate_spec_text[block_start:block_end]
        ids_in_class = {rid for rid in candidate_ids if rid.split("-")[1] == prefix}
        if count != len(ids_in_class):
            fail(f"[class-index] {label} declares {count} but {len(ids_in_class)} requirement(s) exist")
        listed_ids = set(re.findall(rf"RQA-{prefix}-\d{{3}}", block))
        if listed_ids != ids_in_class:
            fail(f"[class-index] {label} index lists {sorted(listed_ids ^ ids_in_class)} inconsistently")

    # ---- 8. note-cell equality ---- #
    derived_cids = {cid for cid, c in candidate_clauses.items() if c["disposition"] == "Derived"}
    for cid in derived_cids:
        actual_reqs = clause_to_reqs.get(cid, [])
        note = candidate_clauses[cid]["note"]
        missing = [rid for rid in actual_reqs if rid not in note]
        if missing:
            fail(f"[note-cell] {cid}'s Note cell does not name {missing}")

    # ---- 9. both traceability directions ---- #
    rule_cids = {cid for cid, c in candidate_clauses.items() if c["disposition"] == "Derived \u2014 traceability rule"}
    named_cids = set(clause_to_reqs) | rule_cids
    unreferenced_derived = derived_cids - named_cids
    if unreferenced_derived:
        fail(f"[traceability] derived clause(s) not named by any requirement: {sorted(unreferenced_derived)}")
    for rid, rec in candidate.items():
        for cid, *_ in rec["clauses"]:
            if cid not in candidate_clauses:
                fail(f"[traceability] {rid} references non-existent clause {cid}")
            elif candidate_clauses[cid]["disposition"] not in ("Derived", "Derived \u2014 traceability rule"):
                fail(f"[traceability] {rid} references a {candidate_clauses[cid]['disposition']} clause {cid}, expected Derived")

    # ---- 10. every relative link resolves ---- #
    for name in ("requirements-specification.md", "requirements-quality-assessment.md", "methodology.md",
                 "clause-inventory.md", "singular-splits.md", "set-assessment.md", "traceability.md",
                 "revision-history.md", "adr-drafts/README.md",
                 "adr-drafts/ADR-A-ac09-remediation-code-modification-contradiction.md",
                 "adr-drafts/ADR-B-credential-scope-vs-merge-capability.md",
                 "adr-drafts/ADR-C-external-harness-provenance-authentication.md"):
        p = HERE / name
        if not p.exists():
            fail(f"[files] expected file missing: {name}")
            continue
        check_links_resolve(p, p.read_text(encoding="utf-8"))

    # ---- report ---- #
    if failures:
        print(f"FAIL \u2014 {len(failures)} issue(s):\n")
        for f in failures:
            print(f"- {f}")
        return 1

    print("PASS")
    print(f"- {len(candidate_ids)} requirements: "
          f"{sum(1 for r in candidate_ids if r.startswith('RQA-BR'))} business, "
          f"{sum(1 for r in candidate_ids if r.startswith('RQA-FR'))} functional, "
          f"{sum(1 for r in candidate_ids if r.startswith('RQA-NFR'))} non-functional")
    print(f"- {len(candidate_clauses)} clauses, {candidate_edges} requirement\u2192clause edges, {n_splits} split clauses")
    print(f"- {total_qa} QA judgements (9 per requirement), all verdicts match the frozen baseline")
    print(f"- every candidate field byte-matches commit {FROZEN_COMMIT}'s "
          f"statement/fit/EARS/priority/status/ADR/source-clause/quote")
    print("- both traceability directions hold; note-cell equality holds; every relative link resolves")
    return 0


if __name__ == "__main__":
    sys.exit(main())