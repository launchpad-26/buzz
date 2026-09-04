#!/usr/bin/env python3
"""Deterministic validator for the RQA requirements specification (C-T shape).

Compares the current candidate files against the frozen baseline commit (be77edee5, the
last commit before the C-T restructuring) and checks every invariant this restructuring
promised to preserve. Stdlib only. Run from anywhere; paths are relative to this file.

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
FROZEN_COMMIT = "be77edee5"
FROZEN_SPEC_PATH = "launchpad/skills/review-queue-automation/requirements/requirements-specification.md"
FROZEN_QA_PATH = "launchpad/skills/review-queue-automation/requirements/requirements-quality-assessment.md"

CHAR_ORDER = [
    "Necessary", "Appropriate", "Unambiguous", "Complete", "Singular",
    "Feasible", "Verifiable", "Correct", "Conforming",
]

# --------------------------------------------------------------------------- #
# allowlist — fields explicitly permitted to differ from the FROZEN_COMMIT
# baseline for this delta (the 2026-09-04 amendment to #2006). Every entry
# names a one-line reason. After this delta is committed, re-point
# FROZEN_COMMIT at the new baseline and delete this allowlist.
# --------------------------------------------------------------------------- #

ALLOWLIST_REQUIREMENT_FIELDS: dict[tuple[str, str], str] = {
    ("RQA-FR-017", "adr"): "ADR-A resolved by the 2026-09-04 amendment; pointer removed",
    ("RQA-FR-018", "adr"): "ADR-A resolved by the 2026-09-04 amendment; pointer removed",
    ("RQA-NFR-019", "adr"): "ADR-A resolved by the 2026-09-04 amendment; pointer removed",
    ("RQA-NFR-020", "adr"): "ADR-A resolved by the 2026-09-04 amendment; pointer removed",
    ("RQA-NFR-021", "adr"): "ADR-A resolved by the 2026-09-04 amendment; pointer removed",
    ("RQA-FR-030", "adr"): "ADR-C resolved by the 2026-09-04 amendment; pointer removed",
    ("RQA-NFR-022", "adr"): "ADR-C resolved by the 2026-09-04 amendment; pointer removed",
    ("RQA-NFR-028", "adr"): "ADR-C resolved by the 2026-09-04 amendment; pointer removed",
    ("RQA-NFR-028", "fit"): "trust-boundary bound added, grounded in amended CL-058's own new sentence",
    ("RQA-NFR-024", "adr"): "ADR-B resolved by the 2026-09-04 amendment; pointer removed",
    ("RQA-NFR-030", "adr"): "ADR-B resolved by the 2026-09-04 amendment; pointer removed",
}

ALLOWLIST_CLAUSE_QUOTES: dict[str, str] = {
    "CL-036": "AC09 amended 2026-09-04: grants direct push authority for mechanical (non-behavioural) findings",
    "CL-057": "Security bullet 3 amended 2026-09-04: restates the AC09 grant from the remediation-authority side",
    "CL-058": "Security bullet 4 amended 2026-09-04: provenance written by RQA; trust-boundary bound added",
    "CL-060": "Security bullet 6 amended 2026-09-04: credential scope now follows configured authority",
}

ALLOWLIST_QA_VERDICTS: dict[tuple[str, str], str] = {
    ("RQA-NFR-024", "Unambiguous"): "activity-conditioned floor now stated directly by amended CL-060",
    ("RQA-NFR-024", "Feasible"): "ADR-B's external premise resolved by amended CL-060",
    ("RQA-NFR-024", "Correct"): "activity-conditioning now source-confirmed, not interpretive",
    ("RQA-NFR-030", "Unambiguous"): "activity-relative ceiling now stated directly by amended CL-060",
    ("RQA-NFR-030", "Feasible"): "ADR-B's external premise resolved by amended CL-060",
    ("RQA-NFR-030", "Correct"): "activity-conditioning now source-confirmed, not interpretive",
}

ALLOWLIST_NEW_REQUIREMENTS: dict[str, str] = {
    "RQA-NFR-031": ("appended in round 9: the 2026-09-04 amendment states a behavioural-ceiling obligation "
                     "(a finding whose remedy would change the system's behaviour is never classified as "
                     "mechanical) that no existing row carried; derived jointly from CL-036 and CL-057, "
                     "contributing 2 new requirement\u2192clause edges"),
}

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


CHUNK_START = re.compile(r"\*\*(CL-\d{3})\*\*")
LINK_RE = re.compile(r"\(([^)]*\[extract\]\(([^)]*)\))\)")
QUOTE_ONLY_RE = re.compile(r"[\u201c\"](.+?)[\u201d\"]", re.DOTALL)


def parse_derives_cell(cell: str) -> list[tuple[str, str, str, str]]:
    """Return ordered [(clause_id, section_label, link_target, quote), ...].

    Tolerant of narrative text between the clause id and its quote (representation
    detail only) — extracts exactly the clause id, its first extract-linked
    parenthetical, and the first quoted string that follows.
    """
    starts = list(CHUNK_START.finditer(cell))
    out = []
    for i, m in enumerate(starts):
        cid = m.group(1)
        chunk_end = starts[i + 1].start() if i + 1 < len(starts) else len(cell)
        chunk = cell[m.end():chunk_end]
        lm = LINK_RE.search(chunk)
        if not lm:
            continue
        section_text = lm.group(1)
        link_target = lm.group(2)
        section_label = re.sub(r",?\s*\[extract\]\([^)]*\)", "", section_text).strip().strip(",").strip()
        qm = QUOTE_ONLY_RE.search(chunk[lm.end():])
        quote = qm.group(1) if qm else None
        out.append((cid, section_label, link_target, quote))
    return out


def normalize_adr(cell: str) -> str:
    """Collapse an ADR cell (either representation) to a bare token for comparison."""
    cell = cell.strip()
    if cell in ("\u2014", "-", ""):
        return "\u2014"
    if "#2064" in cell:
        return "#2064"
    m = re.search(r"ADR-[ABC]", cell)
    if m:
        return m.group(0)
    return cell


# --------------------------------------------------------------------------- #
# frozen baseline: parse the monolithic table-shaped spec + QA
# --------------------------------------------------------------------------- #

def parse_frozen_spec(text: str) -> dict:
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
    if len(clauses) != 65:
        fail(f"[frozen] expected 65 clauses, found {len(clauses)}")

    req_header = ("| ID | Requirement | EARS pattern | Priority | Status | Source | "
                  "Fit criterion | Derives from (clause + verbatim source text) | ADR |")
    req_starts = [i for i, l in enumerate(lines) if l == req_header]
    if len(req_starts) != 3:
        fail(f"[frozen] expected 3 requirement tables, found {len(req_starts)}")

    records = {}
    for start in req_starts:
        for row in parse_table_rows(lines, start):
            rid, stmt, ears, pri, status, source, fit, derives_cell, adr = row
            records[rid] = {
                "id": rid, "statement": stmt, "ears": ears, "priority": pri,
                "status": status, "fit": fit,
                "clauses": parse_derives_cell(derives_cell),
                "adr": normalize_adr(adr),
            }
    return {"clauses": clauses, "requirements": records}


def parse_frozen_qa(text: str) -> dict:
    lines = text.split("\n")
    header = "| ID | Characteristic | Verdict | Basis (where not obvious) |"
    starts = [i for i, l in enumerate(lines) if l == header]
    if len(starts) != 3:
        fail(f"[frozen-qa] expected 3 QA tables, found {len(starts)}")
    by_id: dict[str, dict[str, str]] = defaultdict(dict)
    for start in starts:
        for rid, char, verdict, _basis in parse_table_rows(lines, start):
            by_id[rid][char] = verdict
    return by_id


# --------------------------------------------------------------------------- #
# candidate: parse the C-T block-shaped spec + QA
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
            "adr": normalize_adr(adr),
        }
    # heading-regex exactness/uniqueness
    heading_lines = [l for l in text.split("\n") if l.startswith("### ")]
    exact = re.compile(r"^### RQA-(BR|FR|NFR)-[0-9]{3}$")
    bad_headings = [l for l in heading_lines if not exact.match(l)]
    if bad_headings:
        fail(f"[candidate] {len(bad_headings)} '### ' heading(s) do not match the exact ID regex: {bad_headings[:5]}")
    ids_from_headings = [l[len('### '):] for l in heading_lines if exact.match(l)]
    if len(ids_from_headings) != len(set(ids_from_headings)):
        dupes = [x for x in set(ids_from_headings) if ids_from_headings.count(x) > 1]
        fail(f"[candidate] duplicate requirement heading(s): {dupes}")
    return {"requirements": records, "heading_ids": ids_from_headings}


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


def parse_candidate_qa(text: str) -> dict:
    by_id: dict[str, dict[str, str]] = defaultdict(dict)
    blocks = re.split(r"^### (RQA-(?:BR|FR|NFR)-\d{3})$", text, flags=re.MULTILINE)
    # blocks[0] is preamble; then alternating id, body
    for i in range(1, len(blocks), 2):
        rid = blocks[i]
        body = blocks[i + 1]
        for char, verdict in re.findall(r"\| (\w+) \| (Pass|Caveat) \|", body):
            if char in CHAR_ORDER:
                by_id[rid][char] = verdict
    return by_id


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
            # pure in-page anchor — must match a heading slug in this same file
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
    frozen = parse_frozen_spec(frozen_spec_text)
    frozen_qa = parse_frozen_qa(frozen_qa_text)

    candidate_spec_text = (HERE / "requirements-specification.md").read_text(encoding="utf-8")
    candidate_qa_text = (HERE / "requirements-quality-assessment.md").read_text(encoding="utf-8")
    candidate_clause_text = (HERE / "clause-inventory.md").read_text(encoding="utf-8")
    candidate_split_text = (HERE / "singular-splits.md").read_text(encoding="utf-8")

    candidate = parse_candidate_spec(candidate_spec_text)
    candidate_clauses = parse_candidate_clause_inventory(candidate_clause_text)
    candidate_qa = parse_candidate_qa(candidate_qa_text)
    candidate_split_clause_ids = parse_candidate_singular_splits(candidate_split_text)

    # ---- 1. per-ID field-level byte equality against the frozen baseline (allowlisted fields excepted) ---- #
    frozen_ids = set(frozen["requirements"])
    candidate_ids = set(candidate["requirements"])
    unexplained_missing = frozen_ids - candidate_ids
    unexplained_extra = (candidate_ids - frozen_ids) - set(ALLOWLIST_NEW_REQUIREMENTS)
    if unexplained_missing or unexplained_extra:
        fail(f"[equality] ID set differs beyond the new-requirements allowlist. Missing from candidate: "
             f"{sorted(unexplained_missing)}; unexplained extra in candidate: {sorted(unexplained_extra)}")
    applied_new_requirements: set[str] = (candidate_ids - frozen_ids) & set(ALLOWLIST_NEW_REQUIREMENTS)

    applied_field_allowlist: set[tuple[str, str]] = set()
    applied_quote_allowlist: set[str] = set()

    for rid in sorted(frozen_ids & candidate_ids):
        f_rec = frozen["requirements"][rid]
        c_rec = candidate["requirements"][rid]
        for field in ("statement", "ears", "priority", "status", "fit", "adr"):
            if f_rec[field] != c_rec[field]:
                if (rid, field) in ALLOWLIST_REQUIREMENT_FIELDS:
                    applied_field_allowlist.add((rid, field))
                    continue
                fail(f"[equality] {rid}.{field} differs.\n  frozen:    {f_rec[field]!r}\n  candidate: {c_rec[field]!r}")
        f_clause_ids = [c[0] for c in f_rec["clauses"]]
        c_clause_ids = [c[0] for c in c_rec["clauses"]]
        if f_clause_ids != c_clause_ids:
            fail(f"[equality] {rid} ordered source-clause IDs differ: frozen={f_clause_ids} candidate={c_clause_ids}")
        for (f_cid, f_sec, _f_link, f_quote), (c_cid, c_sec, _c_link, c_quote) in zip(f_rec["clauses"], c_rec["clauses"]):
            if f_quote is None or c_quote is None or f_quote.strip() != c_quote.strip():
                if f_cid in ALLOWLIST_CLAUSE_QUOTES:
                    applied_quote_allowlist.add(f_cid)
                else:
                    fail(f"[equality] {rid} verbatim quote for {f_cid} differs")
            if f_sec.strip() != c_sec.strip():
                fail(f"[equality] {rid} section label for {f_cid} differs: frozen={f_sec!r} candidate={c_sec!r}")

    # ---- 2. 84 unique blocks (83 frozen + 1 new: RQA-NFR-031, round 9) ---- #
    if len(candidate["heading_ids"]) != 84:
        fail(f"[counts] expected 84 requirement headings, found {len(candidate['heading_ids'])}")

    # ---- 3. 65 exactly-once clause dispositions ---- #
    if len(candidate_clauses) != 65:
        fail(f"[counts] expected 65 clauses in clause-inventory.md, found {len(candidate_clauses)}")
    for cid, c in candidate_clauses.items():
        if c["disposition"] not in ("Derived", "Derived \u2014 traceability rule", "Scope exclusion", "Context \u2014 no obligation"):
            fail(f"[dispositions] {cid} has an unrecognised disposition: {c['disposition']!r}")

    # cross-check candidate clause verbatim text against frozen (content must not have moved, except
    # the amendment-allowlisted clauses)
    for cid, f_c in frozen["clauses"].items():
        c_c = candidate_clauses.get(cid)
        if c_c is None:
            fail(f"[equality] clause {cid} missing from candidate clause-inventory.md")
            continue
        if f_c["verbatim"].strip() != c_c["verbatim"].strip():
            if cid in ALLOWLIST_CLAUSE_QUOTES:
                applied_quote_allowlist.add(cid)
            else:
                fail(f"[equality] clause {cid} verbatim text differs between frozen and candidate")
        if f_c["disposition"].strip() != c_c["disposition"].strip():
            fail(f"[equality] clause {cid} disposition differs: frozen={f_c['disposition']!r} candidate={c_c['disposition']!r}")

    # ---- 4. 93 requirement->clause edges (91 frozen + 2 new: RQA-NFR-031 cites CL-036 and CL-057) ---- #
    candidate_edges = sum(len(r["clauses"]) for r in candidate["requirements"].values())
    frozen_edges = sum(len(r["clauses"]) for r in frozen["requirements"].values())
    new_req_edges = sum(len(candidate["requirements"][rid]["clauses"]) for rid in applied_new_requirements)
    if candidate_edges != frozen_edges + new_req_edges:
        fail(f"[counts] requirement->clause edge count differs: frozen={frozen_edges} + new={new_req_edges} "
             f"!= candidate={candidate_edges}")
    if candidate_edges != 93:
        fail(f"[counts] expected 93 requirement->clause edges, found {candidate_edges}")

    # ---- 5. 26 splits (count of derived clauses cited by >1 requirement's clause list, INCLUDING
    #          joint-citation edges — matches how requirements-specification.md counts them) ---- #
    clause_to_reqs = defaultdict(list)
    for rid, rec in candidate["requirements"].items():
        for cid, *_ in rec["clauses"]:
            clause_to_reqs[cid].append(rid)
    n_splits = sum(1 for reqs in clause_to_reqs.values() if len(reqs) > 1)
    if n_splits != 26:
        fail(f"[counts] expected 26 split clauses, found {n_splits}")
    # cross-check against singular-splits.md's own row list
    split_rows_set = set(candidate_split_clause_ids)
    computed_split_set = {cid for cid, reqs in clause_to_reqs.items() if len(reqs) > 1}
    if split_rows_set != computed_split_set:
        fail(f"[counts] singular-splits.md rows {sorted(split_rows_set)} != computed split set {sorted(computed_split_set)}")

    # ---- 6. 756 QA judgements, 9 per ID (747 frozen + 9 new: RQA-NFR-031) ---- #
    total_qa = sum(len(v) for v in candidate_qa.values())
    if total_qa != 756:
        fail(f"[counts] expected 756 QA judgements, found {total_qa}")
    for rid in candidate_ids:
        chars = candidate_qa.get(rid, {})
        if set(chars) != set(CHAR_ORDER):
            fail(f"[qa] {rid} does not carry exactly the nine characteristics: {sorted(chars)}")
    # candidate QA verdicts must match frozen QA verdicts (substance preserved; restructuring is heading-only),
    # except the amendment-allowlisted verdict promotions
    applied_qa_allowlist: set[tuple[str, str]] = set()
    for rid in sorted(frozen_ids & candidate_ids):
        for char in CHAR_ORDER:
            f_v = frozen_qa.get(rid, {}).get(char)
            c_v = candidate_qa.get(rid, {}).get(char)
            if f_v != c_v:
                if (rid, char) in ALLOWLIST_QA_VERDICTS:
                    applied_qa_allowlist.add((rid, char))
                else:
                    fail(f"[qa-equality] {rid}.{char} verdict differs: frozen={f_v} candidate={c_v}")

    # ---- 7. class-index completeness: every ID in requirements-specification.md's class indexes ---- #
    for label, prefix in (("Business requirements", "BR"), ("Functional requirements", "FR"), ("Non-functional requirements", "NFR")):
        header_match = re.search(rf"\*\*{re.escape(label)} \((\d+)\):\*\*", candidate_spec_text)
        if not header_match:
            fail(f"[class-index] could not find class index header for {label!r}")
            continue
        count = int(header_match.group(1))
        # the index table runs from the header to the blank line before the next bold header/section
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

    # ---- 8. note-cell equality (candidate clause-inventory.md) ---- #
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
    bad_backrefs = [cid for reqs in clause_to_reqs.values() for cid in [None] if False]  # placeholder, real check below
    for rid, rec in candidate["requirements"].items():
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

    # ---- stale-allowlist detection: every declared entry must have actually been needed ---- #
    for key in ALLOWLIST_REQUIREMENT_FIELDS:
        if key not in applied_field_allowlist:
            fail(f"[allowlist] stale entry ALLOWLIST_REQUIREMENT_FIELDS{key} — fields are identical; remove it")
    for cid in ALLOWLIST_CLAUSE_QUOTES:
        if cid not in applied_quote_allowlist:
            fail(f"[allowlist] stale entry ALLOWLIST_CLAUSE_QUOTES[{cid!r}] — quote is identical; remove it")
    for key in ALLOWLIST_QA_VERDICTS:
        if key not in applied_qa_allowlist:
            fail(f"[allowlist] stale entry ALLOWLIST_QA_VERDICTS{key} — verdict is identical; remove it")
    for rid in ALLOWLIST_NEW_REQUIREMENTS:
        if rid not in applied_new_requirements:
            fail(f"[allowlist] stale entry ALLOWLIST_NEW_REQUIREMENTS[{rid!r}] — ID already exists in the frozen baseline; remove it")

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
    print(f"- {len(applied_new_requirements)} new requirement(s) since the frozen baseline: {sorted(applied_new_requirements)}")
    print(f"- {total_qa} QA judgements (9 per requirement)")
    print(f"- every candidate field byte-matches commit {FROZEN_COMMIT}'s statement/fit/EARS/priority/status/ADR/source-clause/quote,")
    print("  EXCEPT the allowlisted fields below (this is delta mode \u2014 re-point FROZEN_COMMIT after commit and delete the allowlist)")
    print("- both traceability directions hold; note-cell equality holds; every relative link resolves")
    print()
    print(f"ALLOWLIST ({len(ALLOWLIST_REQUIREMENT_FIELDS) + len(ALLOWLIST_CLAUSE_QUOTES) + len(ALLOWLIST_QA_VERDICTS) + len(ALLOWLIST_NEW_REQUIREMENTS)} entries, all applied, none stale):")
    print(f"  requirement fields ({len(ALLOWLIST_REQUIREMENT_FIELDS)}):")
    for (rid, field), reason in sorted(ALLOWLIST_REQUIREMENT_FIELDS.items()):
        print(f"    - {rid}.{field}: {reason}")
    print(f"  clause quotes ({len(ALLOWLIST_CLAUSE_QUOTES)}):")
    for cid, reason in sorted(ALLOWLIST_CLAUSE_QUOTES.items()):
        print(f"    - {cid}: {reason}")
    print(f"  QA verdicts ({len(ALLOWLIST_QA_VERDICTS)}):")
    for (rid, char), reason in sorted(ALLOWLIST_QA_VERDICTS.items()):
        print(f"    - {rid}.{char}: {reason}")
    print(f"  new requirements ({len(ALLOWLIST_NEW_REQUIREMENTS)}):")
    for rid, reason in sorted(ALLOWLIST_NEW_REQUIREMENTS.items()):
        print(f"    - {rid}: {reason}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
