#!/usr/bin/env python3
"""Generate checklist.yaml from 03-master-checklist.md.

IN PLAIN TERMS
    What this is   The script that turns the human checklist into the machine
                   one. Humans edit the Markdown; this keeps the YAML in step.
    Who it is for  Anyone changing a checklist item.
    What to do     Edit 03-master-checklist.md, then run this from this
                   directory:  python3 generate_checklist_yaml.py
    Know this      Never hand-edit checklist.yaml. This overwrites it.

HOW IT WORKS

    03-master-checklist.md   <-- the source of truth, humans edit here
             |
             |  parse each "**ID - requirement**" block
             |  and its seven em-dash fields
             v
    generate_checklist_yaml.py
             |
             v
    checklist.yaml           <-- generated, do not hand-edit

Parity between the two files is by construction: every item in the YAML came
from a block in the Markdown, and the script fails loudly rather than silently
skipping a block it cannot parse.
"""

import collections
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
SRC = HERE / "03-master-checklist.md"
OUT = HERE / "checklist.yaml"

CATEGORY = {
    "READER": "reader-first",
    "FOUND": "foundations",
    "START": "getting-started",
    "ARCH": "architecture",
    "DEV": "developer-workflows",
    "API": "interfaces-and-contracts",
    "OPS": "operations-security-reliability",
    "GOV": "governance",
    "HUMAN": "human-readable",
    "AGENT": "agent-readable",
}

AUDIENCE = {"Both": ["human", "agent"], "Human": ["human"], "Agent": ["agent"]}
AUTOMATION = {
    "Automated": "automated",
    "Partially automated": "partial",
    "Human review": "human",
}

ITEM_RE = r"^\*\*([A-Z]+-\d{3}) \u00b7 (.+?)\*\*(.*)\n((?:\u2014.*\n)+)"
META_RE = (
    "\u2014\\s*([^/]+)/\\s*([^/]+)/\\s*([^/]+)/"
    "\\s*\\*\\*(P\\d)\\*\\*\\s*/\\s*([^/]+)/\\s*(.*)"
)

RULES = [
    "No aggregate score; an average may not offset a failed gate.",
    "not_applicable and not_evaluated are different results and both need a reason.",
    "A deterministic check proves its own predicate and nothing else.",
    "A tool failure becomes unable_to_assess, never a pass.",
    "Report 'no defect detected against inventory X', never 'complete' or 'correct'.",
]

HEADER = '''# Output 10 - Machine-readable master documentation checklist
#
# ---------------------------------------------------------------------------
# IN PLAIN TERMS
#
#   What this is   The same documentation rules as 03-master-checklist.md, in a
#                  form a program can read. The Markdown file is the one humans
#                  should read; this one is for tooling.
#   Who it is for  Scripts, linters, CI jobs and agents.
#   What to do     Load it, filter by `applicability` and `priority_default`,
#                  and run the `audit_method` for each item you select.
#   Know this      `corpus_gap: true` means the rule is NOT backed by the
#                  research - it is supplementary best practice. Weaker.
#
# HOW IT IS PRODUCED
#
#     03-master-checklist.md        (humans write and edit HERE)
#              |
#              v
#     generate_checklist_yaml.py    (run it from this directory)
#              |
#              v
#     checklist.yaml                (this file - generated, do not hand-edit)
#
#   Editing this file directly will be overwritten. Change the Markdown.
# ---------------------------------------------------------------------------
'''


def field(body: str, name: str) -> str:
    """Pull one em-dash field out of an item block, whitespace-normalised."""
    m = re.search(
        "\u2014\\s+\\*\\*" + name + "\\*\\*\\s+(.*?)(?=\\n\u2014|\\Z)", body, re.S
    )
    return re.sub(r"\s+", " ", m.group(1)).strip() if m else ""


def quote(s: str) -> str:
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def parse(text: str) -> list:
    items, seen = [], set()
    for pid, requirement, tag, body in re.findall(ITEM_RE, text, re.M):
        if pid in seen:
            sys.exit(f"duplicate id: {pid}")
        seen.add(pid)

        meta = body.split("\n")[0]
        m = re.match(META_RE, meta)
        if not m:
            sys.exit(f"could not parse the meta line for {pid}:\n  {meta}")
        _cat, aud, applicability, priority, automation, deps = (
            x.strip() for x in m.groups()
        )

        prefix = pid.split("-")[0]
        if prefix not in CATEGORY:
            sys.exit(f"unknown id prefix {prefix!r} in {pid}; add it to CATEGORY")

        items.append(
            {
                "id": pid,
                "category": CATEGORY[prefix],
                "requirement": requirement.strip(),
                "audience": AUDIENCE[aud],
                "applicability": applicability.lower(),
                "applies_when": field(body, "Applies when"),
                "priority_default": priority,
                "rationale": field(body, "Rationale"),
                "evidence_required": field(body, "Evidence needed"),
                "suggested_locations": field(body, "Location"),
                "source_references": field(body, "Source"),
                "audit_method": field(body, "Audit method"),
                "automation_potential": AUTOMATION[automation],
                "dependencies": [
                    d.strip()
                    for d in deps.split(",")
                    if re.match(r"^[A-Z]+-\d{3}$", d.strip())
                ],
                "failure_risk": field(body, "Failure risk"),
                "corpus_gap": ("Corpus gap" in tag)
                or ("Corpus gap" in field(body, "Source")),
            }
        )
    return items


def render(items: list) -> str:
    out = [HEADER]
    out.append('checklist_version: "1.1"')
    out.append('baseline_revision: "78e789369e3392f187e8c63753262669108fda81"')
    out.append("generated_from:")
    out.append('  - path: "launchpad/Research/documentation-corpus-review/"')
    out.append("    files_reviewed: 41")
    out.append("    files_unreadable: 0")
    out.append("rules:")
    out.extend("  - " + quote(r) for r in RULES)
    out.append(
        "result_states: [pass, partial, fail, incorrect, stale, duplicated, "
        "not_applicable, unknown, human_confirmation_required]"
    )
    out.append(f"item_count: {len(items)}")
    out.append("items:")
    for it in items:
        out.append(f'  - id: "{it["id"]}"')
        out.append(f'    category: "{it["category"]}"')
        out.append(f"    requirement: {quote(it['requirement'])}")
        out.append("    audience:")
        out.extend(f"      - {a}" for a in it["audience"])
        out.append(f'    applicability: "{it["applicability"]}"')
        out.append(f"    applies_when: {quote(it['applies_when'])}")
        out.append(f'    priority_default: "{it["priority_default"]}"')
        out.append(f"    rationale: {quote(it['rationale'])}")
        out.append(f"    evidence_required: {quote(it['evidence_required'])}")
        out.append(f"    suggested_locations: {quote(it['suggested_locations'])}")
        out.append(f"    source_references: {quote(it['source_references'])}")
        out.append(f"    corpus_gap: {str(it['corpus_gap']).lower()}")
        out.append(f"    audit_method: {quote(it['audit_method'])}")
        out.append(f'    automation_potential: "{it["automation_potential"]}"')
        deps = ", ".join(f'"{d}"' for d in it["dependencies"])
        out.append(f"    dependencies: [{deps}]")
        out.append(f"    failure_risk: {quote(it['failure_risk'])}")
    return "\n".join(out) + "\n"


def main() -> None:
    if not SRC.exists():
        sys.exit(f"cannot find {SRC}")
    items = parse(SRC.read_text(encoding="utf-8"))
    if not items:
        sys.exit("parsed zero items - the Markdown item format has probably changed")

    missing = [
        i["id"]
        for i in items
        if not all(
            i[k]
            for k in (
                "requirement",
                "applies_when",
                "rationale",
                "evidence_required",
                "audit_method",
                "failure_risk",
            )
        )
    ]
    if missing:
        sys.exit(f"items with an empty required field: {missing}")

    ids = {i["id"] for i in items}
    dangling = [
        (i["id"], d) for i in items for d in i["dependencies"] if d not in ids
    ]
    if dangling:
        sys.exit(f"dependencies pointing at unknown ids: {dangling}")

    OUT.write_text(render(items), encoding="utf-8")
    by_cat = collections.Counter(i["category"] for i in items)
    print(f"wrote {OUT.name}: {len(items)} items")
    print(f"  categories: {dict(by_cat)}")
    print(f"  corpus-gap items: {sum(1 for i in items if i['corpus_gap'])}")


if __name__ == "__main__":
    main()
