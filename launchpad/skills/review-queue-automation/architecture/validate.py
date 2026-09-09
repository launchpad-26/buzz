#!/usr/bin/env python3
"""Consistency check for the #2071 RQA architecture description.

Reads the canonical tables of the four documents and exits non-zero when any of the
issue's mechanically checkable conditions fails:

  1. every requirement in the frozen specification has exactly one accountable part;
  2. every part is accountable for at least one requirement;
  3. every disposition unit in the gap register is placed in or replaced by a part;
  4. every persisted record has exactly one writing part;
  5. the decomposition-blocking ADR list (components.md §9) and the ADR references in
     the four documents agree in both directions;
  6. every part id, edge id and constraint id used anywhere is defined exactly once;
  7. the flow's state table reaches every FR-016 disposition;
  8. every part has a code-level contract under code/ naming the edges it provides, the
     records it writes and the requirements it answers for;
  9. code/CONTRACTS.md exists and carries a signature for every edge.

The tables are canonical; this script never reads a diagram. It reads the frozen
specification and the gap dispositions only to learn the requirement and unit id sets.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
DOCS = ["context.md", "container.md", "components.md", "flow-review-lifecycle.md"]
NARRATIVE = "architecture.md"
CARRIERS = {"ARCH", "TRACKER"}
FR016 = {
    "being reviewed",
    "blocked",
    "awaiting remediation",
    "awaiting human judgement",
    "review-complete",
    "unable to progress",
}
PART_RE = re.compile(r"\bP-\d\d\b")
EDGE_RE = re.compile(r"\bE-\d\d\b")
ADR_RE = re.compile(r"\bADR-[A-Z]\b")

failures: list[str] = []


def fail(msg: str) -> None:
    failures.append(msg)


def table_rows(text: str, header_prefix: str) -> list[list[str]]:
    """Rows of the first markdown table whose header row starts with `| header_prefix |`."""
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if line.startswith(f"| {header_prefix} |"):
            rows = []
            for row in lines[i + 2 :]:
                if not row.startswith("|"):
                    break
                cells = [c.strip() for c in row.strip().strip("|").split(" | ")]
                rows.append(cells)
            return rows
    fail(f"table with header {header_prefix!r} not found")
    return []


def main() -> int:
    texts = {d: (HERE / d).read_text() for d in DOCS}
    if not (HERE / NARRATIVE).exists():
        fail(f"{NARRATIVE} missing: the views have no narrative entry point")
    else:
        narrative = (HERE / NARRATIVE).read_text()
        for d in DOCS + ["adr-drafts/"]:
            if d not in narrative:
                fail(f"{NARRATIVE} does not point at {d}")
    comp = texts["components.md"]

    # Universe of ids from the frozen inputs.
    spec = (SKILL / "requirements" / "requirements-specification.md").read_text()
    req_ids = re.findall(r"^### (RQA-[A-Z]+-\d{3})$", spec, re.M)
    unit_ids = []
    for f in sorted((SKILL / "gap" / "dispositions").glob("*.md")):
        unit_ids += re.findall(r"^### (U-[A-Z]+-\d\d) — ", f.read_text(), re.M)

    # 6a. parts defined exactly once, in §4 headings.
    part_defs = re.findall(r"^### (P-\d\d) — (.+)$", comp, re.M)
    parts = [p for p, _ in part_defs]
    if len(parts) != len(set(parts)):
        fail("duplicate part definition in components.md §4")
    part_set = set(parts)

    # 1. requirement → exactly one accountable part.
    req_rows = table_rows(comp, "requirement | accountable part")
    seen = {}
    for cells in req_rows:
        rid, acc, contrib = cells[0], cells[1], cells[2]
        seen.setdefault(rid, []).append(acc)
        if acc not in part_set and acc not in CARRIERS:
            fail(f"{rid}: accountable {acc!r} is not a defined part or carrier")
        if acc in CARRIERS and rid not in {"RQA-FR-034", "RQA-FR-035"}:
            fail(f"{rid}: carrier {acc} is admitted only for RQA-FR-034 and RQA-FR-035")
        for c in PART_RE.findall(contrib):
            if c not in part_set:
                fail(f"{rid}: contributing {c} is not a defined part")
            if c == acc:
                fail(f"{rid}: accountable part {acc} also listed as contributing")
    for rid in req_ids:
        n = len(seen.get(rid, []))
        if n != 1:
            fail(f"{rid}: {n} accountable rows (expected exactly 1)")
    for rid in seen:
        if rid not in req_ids:
            fail(f"{rid}: row present but not in the frozen specification")

    # 2. every part accountable for ≥ 1 requirement.
    acc_counts = {p: 0 for p in parts}
    for rid, accs in seen.items():
        if accs and accs[0] in acc_counts:
            acc_counts[accs[0]] += 1
    for p, n in acc_counts.items():
        if n == 0:
            fail(f"{p}: accountable for no requirement")

    # 3. every unit placed or replaced.
    unit_rows = table_rows(comp, "unit | recommended")
    placed = {}
    for cells in unit_rows:
        uid, disp, rel, part = cells[0], cells[1], cells[2], cells[3]
        placed.setdefault(uid, []).append((disp, rel, part))
        if part not in part_set:
            fail(f"{uid}: part {part!r} not defined")
        if disp == "bin" and rel != "replaced by":
            fail(f"{uid}: bin unit must be 'replaced by', got {rel!r}")
        if disp != "bin" and rel != "placed in":
            fail(f"{uid}: {disp} unit must be 'placed in', got {rel!r}")
    for uid in unit_ids:
        n = len(placed.get(uid, []))
        if n != 1:
            fail(f"{uid}: {n} placement rows (expected exactly 1)")
    for uid in placed:
        if uid not in unit_ids:
            fail(f"{uid}: row present but not in the gap dispositions")

    # 4. records: exactly one writer, which is a part or 'operator'.
    rec_rows = table_rows(texts["container.md"], "record | form")
    for cells in rec_rows:
        rec, writer = cells[0], cells[2]
        writers = PART_RE.findall(writer)
        if writer == "operator":
            continue
        if len(writers) != 1 or writers[0] not in part_set or writers[0] != writer:
            fail(f"record {rec}: writing part {writer!r} is not exactly one defined part")

    # 5. ADR list ↔ references, both directions.
    adr_rows = table_rows(comp, "ADR | question")
    listed = set()
    for cells in adr_rows:
        m = ADR_RE.search(cells[0])
        if not m:
            fail(f"ADR row without an ADR id: {cells[0]!r}")
            continue
        listed.add(m.group(0))
        if cells[2].strip("*") not in {"blocking", "not blocking"}:
            fail(f"{m.group(0)}: blocking column must be 'blocking' or 'not blocking'")
        if not (HERE / "adr-drafts" / f"{m.group(0)}.md").exists():
            fail(f"{m.group(0)}: no draft under adr-drafts/")
    referenced = set()
    for d, t in texts.items():
        referenced |= set(ADR_RE.findall(t))
    for a in referenced - listed:
        fail(f"{a} referenced in a document but absent from components.md §9")
    for a in listed - referenced:
        fail(f"{a} listed in §9 but referenced nowhere")
    for p in (HERE / "adr-drafts").glob("ADR-*.md"):
        if p.stem not in listed:
            fail(f"adr-drafts/{p.name} exists but is not listed in §9")

    # 6b. every part/edge id used anywhere is defined.
    edge_rows = table_rows(comp, "edge | from")
    edge_set = {cells[0] for cells in edge_rows}
    if len(edge_set) != len(edge_rows):
        fail("duplicate edge id in components.md §6")
    for d, t in texts.items():
        for p in set(PART_RE.findall(t)) - part_set:
            fail(f"{d}: uses undefined part {p}")
        for e in set(EDGE_RE.findall(t)) - edge_set:
            fail(f"{d}: uses undefined edge {e}")
    for cells in edge_rows:
        for p in PART_RE.findall(cells[1] + " " + cells[2]):
            if p not in part_set:
                fail(f"{cells[0]}: endpoint {p} not defined")
    # Every part must appear on at least one edge.
    on_edges = set()
    for cells in edge_rows:
        on_edges |= set(PART_RE.findall(cells[1] + " " + cells[2]))
    on_edges |= set(PART_RE.findall(" ".join(c[1] for c in edge_rows if c[0] == "E-13")))
    # E-13's 'any part' covers the record edge for every part.
    if any(c[0] == "E-13" and c[1].startswith("every part") for c in edge_rows):
        on_edges |= part_set
    for p in part_set - on_edges:
        fail(f"{p}: appears on no edge")

    # 6c. constraints table: every id names a part or ARCH.
    cons_rows = table_rows(texts["context.md"], "id | constraint")
    cons_ids = [c[0] for c in cons_rows]
    for cid in ["C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8", "C9", "PR",
                "NG-4", "NG-5", "NG-6", "NG-7", "NG-8", "SEC-1", "SEC-2", "SEC-3", "SEC-4", "SEC-5", "SEC-6", "SEC-7"]:
        if cid not in cons_ids:
            fail(f"context.md §7: constraint {cid} missing")
    for cells in cons_rows:
        if cells[2] not in part_set and cells[2] != "ARCH":
            fail(f"constraint {cells[0]}: honoured by {cells[2]!r}, not a part or ARCH")

    # 7. flow state table reaches every FR-016 disposition.
    st_rows = table_rows(texts["flow-review-lifecycle.md"], "internal state | FR-016 disposition")
    disps = {cells[1] for cells in st_rows}
    for dsp in FR016 - disps:
        fail(f"flow §4: disposition {dsp!r} unreachable")


    # 8. code-level contracts: one per part, each naming its provided edges, records and requirements.
    code_dir = HERE / "code"
    code_files = {p.name[:4]: p for p in code_dir.glob("P-*.md")} if code_dir.exists() else {}
    edge_provider = {}
    for cells in edge_rows:
        for p in PART_RE.findall(cells[2]):
            edge_provider.setdefault(p, set()).add(cells[0])
    rec_writer = {}
    for cells in rec_rows:
        for p in PART_RE.findall(cells[2]):
            rec_writer.setdefault(p, set()).add(cells[0].strip("`"))
    for p in parts:
        f = code_files.get(p)
        if f is None:
            fail(f"code/: no contract file for {p}")
            continue
        body = f.read_text()
        for e in sorted(edge_provider.get(p, ())):
            if e not in body:
                fail(f"code/{f.name}: provides {e} per components.md §6 but never names it")
        for rec in sorted(rec_writer.get(p, ())):
            if f"`{rec}`" not in body and rec not in body:
                fail(f"code/{f.name}: writes record {rec} per container.md §5 but never names it")
        for rid, accs in seen.items():
            if accs and accs[0] == p and rid not in body:
                fail(f"code/{f.name}: accountable for {rid} but §9 does not name it")
        for heading in ("## 1.", "## 2.", "## 3.", "## 4.", "## 5.", "## 6.", "## 7.", "## 8.", "## 9."):
            if heading not in body:
                fail(f"code/{f.name}: missing section {heading}")
    for k, f in code_files.items():
        if k not in part_set:
            fail(f"code/{f.name}: names a part that does not exist")
    # 9. the seam truth exists and every edge id in §6 has a signature in it
    contracts = code_dir / "CONTRACTS.md"
    if not contracts.exists():
        fail("code/CONTRACTS.md missing: no seam truth")
    else:
        ctext = contracts.read_text()
        for cells in edge_rows:
            if cells[0] not in ctext:
                fail(f"code/CONTRACTS.md: no signature for {cells[0]}")
        for fn in ("def admit(", "def carry_over(", "def route(", "def reserve(", "def plan(", "def run(", "def judge(", "def remediate(", "def raise_(", "def submit_review(", "def facts(", "def grant(", "def snapshot_for(", "def validate(", "def consumed(", "def probe("):
            if fn not in ctext:
                fail(f"code/CONTRACTS.md: missing {fn}")

        # 10. Regression guards for the cross-part invariants corrected during review.
        required_contracts = {
            "evidence_cutoff: datetime": "PanelResult must carry the post-panel cutoff",
            "injection_attempts: tuple[InjectionAttempt, ...]": "Verdict must report injection attempts",
            "categories: frozenset[Category] | None": "authority grants must cover every finding category",
            "snapshot: Snapshot": "remediation must receive the pinned snapshot",
            "ENTRY_KINDS: frozenset[EntryKind]": "record entry kinds must be closed",
            "revision_changed_paths: frozenset[str]": "reuse needs predecessor-to-current paths",
            "observed_at: datetime": "checks need immutable cutoff comparison",
            "reviews: tuple[SubmittedReview, ...]": "human outcomes need visible GitHub review evidence",
            "predecessor_head_sha: str | None": "jobs must pin the revision-compare base",
            "def trusted_prefix(": "record reuse needs authenticated predecessor reads",
        }
        for snippet, reason in required_contracts.items():
            if snippet not in ctext:
                fail(f"code/CONTRACTS.md: {reason} ({snippet!r} missing)")

        shared_classes = set(
            re.findall(r"^class ([A-Za-z_][A-Za-z0-9_]*)[(:]", ctext, re.M)
        )
        for part, path in code_files.items():
            body = path.read_text()
            duplicates = shared_classes & set(
                re.findall(r"^class ([A-Za-z_][A-Za-z0-9_]*)[(:]", body, re.M)
            )
            for name in sorted(duplicates):
                fail(f"code/{path.name}: redefines shared type {name}")

        reuse = code_files["P-13"].read_text()
        if "prior.trusted_prefix(source_job)" not in reuse:
            fail("code/P-13-revision-reuse.md: predecessor reuse bypasses authenticated record prefix")
        if "prior.latest(" in reuse or "prior.entries(" in reuse:
            fail("code/P-13-revision-reuse.md: predecessor reuse performs an unauthenticated row read")
        if "facts.revision_changed_paths" not in reuse:
            fail("code/P-13-revision-reuse.md: invalidation does not use predecessor-to-current paths")
        remediation = code_files["P-10"].read_text()
        for binding in ("grant.job_id == job.id", "grant.snapshot_hash == snapshot.hash",
                        "grant.categories == finding.categories"):
            if binding not in remediation:
                fail(f"code/P-10-remediation.md: missing grant binding {binding}")

        all_architecture = "\n".join(
            [narrative, *texts.values(), ctext]
            + [p.read_text() for p in code_files.values()]
            + [p.read_text() for p in (HERE / "adr-drafts").glob("ADR-*.md")]
        )
        forbidden = {
            "category: Category | None": "singular remediation-category grant",
            "same reservation": "reservation reuse across harness attempts",
            "facts.fetched_at <= panel.evidence_cutoff": "pre-panel fact time used as attempt cutoff",
            "ADRs are not filed": "stale unfiled-ADR narrative",
        }
        for snippet, reason in forbidden.items():
            if snippet in all_architecture:
                fail(f"architecture retains {reason}: {snippet!r}")
        for issue in ("#2157", "#2158", "#2159", "#2160"):
            if issue not in all_architecture:
                fail(f"architecture does not link filed ADR issue {issue}")

    print(f"parts {len(parts)} · requirements {len(req_ids)} · units {len(unit_ids)} · "
          f"records {len(rec_rows)} · edges {len(edge_rows)} · ADRs {len(listed)} · "
          f"constraints {len(cons_rows)} · states {len(st_rows)} · code contracts {len(code_files)}")
    if failures:
        print(f"FAIL — {len(failures)} problem(s):")
        for f in failures:
            print(f"  - {f}")
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
