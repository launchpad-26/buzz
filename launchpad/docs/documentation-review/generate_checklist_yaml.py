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

Every item in the YAML comes from a block in the Markdown, and the script exits
non-zero rather than silently skipping a block it cannot parse.

That is not the same as parity, and this file used to claim it was. Regenerating
reproduces whatever the parser does, including its mistakes -- a byte-for-byte
match after a re-run proves determinism, not correctness. An independent
cross-model review found the parser truncating three requirements at nested
emphasis while the ID counts matched perfectly. Parity is therefore asserted by
test_documentation_review.py, which compares field *content* against the
Markdown, and not by this script.
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

# Two parser defects have lived on this one line, in opposite directions, and
# the fix for each created the other. Both were found by cross-model review, not
# by this suite.
#
#   Non-greedy (.+?)  stopped at the FIRST '**', truncating every requirement
#                     containing nested emphasis. START-006, OPS-006 and
#                     AGENT-001 silently lost "names", "restore" and "not".
#   Greedy (.+)       ran to the LAST '**', so a *bolded trailing tag* was
#                     swallowed INTO the requirement -- and because the tag was
#                     then inside the requirement rather than in its own group,
#                     `corpus_gap` silently went false.
#
# Neither is fixable by choosing a different quantifier: a line regex cannot tell
# a delimiter from emphasis. So the TAIL is anchored instead. After the closing
# '**' only whitespace and one backticked tag may appear before end of line --
# which is the documented convention anyway. A bolded tag now MATCHES NOTHING,
# the item falls out of this pattern entirely, and ITEM_COUNT_RE (deliberately
# independent) turns that into a loud failure. Guessing is what caused both bugs;
# refusing to guess is the fix.
# So the heading is no longer matched by a regex at all. This pattern only finds
# the line and hands the rest of it to split_heading(), which scans for the
# delimiter that actually closes the opening '**' by tracking nesting depth --
# the one thing a regex cannot do here.
ITEM_RE = r"^\*\*([A-Z]+-\d{3}) \u00b7 (.*)\n((?:\u2014.*\n)+)"
ITEM_COUNT_RE = r"^\*\*[A-Z]+-\d{3} \u00b7 "
EMPHASIS_RE = r"\*\*|__"
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


def split_heading(pid: str, rest: str) -> tuple:
    """Split `requirement** optional-tag` at the delimiter that really closes.

    `rest` is everything after "**ID · ". The opening '**' is already open, so
    depth starts at 1; each subsequent '**' toggles it. The requirement ends at
    the marker that brings depth back to 0. Everything after that is the tag.

        text with **bold** inside** `tag`   ->  depth 1,2,1,0  -> closes at the
                                                third marker, tag = `tag`
        text** **Corpus gap**              ->  depth 1,0       -> closes at the
                                                FIRST marker, tag = **Corpus gap**

    The second case is the one both previous parsers got wrong in opposite ways:
    non-greedy truncated the first case, greedy swallowed the tag in the second.
    Depth tracking gets both right, and a tag that still contains '**' after the
    split is a format the convention does not allow -- so it is refused here
    rather than silently absorbed.
    """
    depth, i = 1, 0
    while i < len(rest):
        if rest.startswith("**", i):
            before = rest[i - 1] if i else " "
            after = rest[i + 2] if i + 2 < len(rest) else " "
            # CommonMark flanking, reduced to what this format needs: a marker
            # preceded by non-space closes; one followed by non-space opens.
            if not before.isspace():
                depth -= 1
            elif not after.isspace():
                depth += 1
            if depth == 0:
                requirement, tag = rest[:i], rest[i + 2 :].strip()
                if "**" in tag or "__" in tag:
                    sys.exit(
                        f"{pid}: the text after the requirement contains bold "
                        f"({tag!r}). A trailing tag must be plain or backticked "
                        "-- bold there is indistinguishable from the "
                        "requirement's own closing delimiter."
                    )
                return requirement, tag
            i += 2
            continue
        i += 1
    sys.exit(f"{pid}: heading has no closing '**':\n  **{pid} · {rest}")


# Values that legitimately mean "no dependencies". Anything else that fails to
# parse is an error, not an empty list.
NO_DEPS = {"", "-", "—", "none", "n/a", "na"}


def parse_dependencies(pid: str, deps: str) -> list:
    """Parse the dependency list, refusing anything it cannot read.

    This used to be a comprehension with `if re.match(...)` as its filter, which
    silently DROPPED any token that did not match -- backtick-formatted, an
    unexpected separator, a typo'd id. A dropped edge leaves no trace: the YAML
    is well-formed, the count is right, and the dependency graph is quietly
    wrong. An independent review demonstrated the loss by backticking one id.

    A filter and a validator look identical and mean opposite things. This is
    the validator.
    """
    out = []
    for raw in deps.split(","):
        token = raw.strip().strip("`").strip()
        if token.lower() in NO_DEPS:
            continue
        if not re.fullmatch(r"[A-Z]+-\d{3}", token):
            sys.exit(
                f"{pid}: cannot parse dependency {token!r} (from {deps!r}). "
                "Dependencies must be bare ids like READER-001, comma separated."
            )
        out.append(token)
    return out


def parse(text: str) -> list:
    items, seen = [], set()
    for pid, heading_rest, body in re.findall(ITEM_RE, text, re.M):
        if pid in seen:
            sys.exit(f"duplicate id: {pid}")
        seen.add(pid)

        requirement, tag = split_heading(pid, heading_rest)

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
                # Emphasis markers are presentation, not content. The YAML holds
                # the plain sentence; test_documentation_review.py compares the
                # two after the same normalisation.
                "requirement": re.sub(EMPHASIS_RE, "", requirement).strip(),
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
                "dependencies": parse_dependencies(pid, deps),
                "failure_risk": field(body, "Failure risk"),
                "corpus_gap": ("Corpus gap" in tag)
                or ("Corpus gap" in field(body, "Source")),
            }
        )
    return items


def parse_result_states(text: str) -> list[str]:
    """Read the result-state vocabulary from the Markdown's own declaration.

    NEVER hardcode this list. It WAS hardcoded until 2026-09-14, and the literal
    omitted `NOT_EVALUATED` and `UNABLE_TO_ASSESS` -- the two states the
    checklist's own non-negotiable rules 2 and 4 make mandatory. An agent
    enforcing the emitted enum would have been obliged to reject this framework's
    own audit report, whose central claim is that 79 items were *not evaluated*
    and that this is not the same as passing them.

    Nothing could detect the contradiction, because the per-item generation
    guarantee did not extend to the header: the Markdown declared no enum, so the
    generated file had nothing to disagree with. A generated artefact is only as
    trustworthy as the part of it that is actually generated.
    """
    block = re.search(r"^### Result states\s*$(.*?)^---\s*$", text, re.M | re.S)
    if not block:
        raise SystemExit(
            f"generate_checklist_yaml: no '### Result states' section in {SRC.name}. "
            "The vocabulary is declared there and read from there; it is "
            "deliberately not hardcoded here."
        )
    states = re.findall(r"^- `([A-Z_]+)`", block.group(1), re.M)
    missing = {"NOT_EVALUATED", "UNABLE_TO_ASSESS"} - set(states)
    if missing:
        raise SystemExit(
            f"generate_checklist_yaml: '### Result states' omits {sorted(missing)}, "
            "which non-negotiable rules 2 and 4 require. Refusing to emit a "
            "contract that forbids a state the rules mandate."
        )
    return states


def render(items: list, states: list[str]) -> str:
    out = [HEADER]
    out.append('checklist_version: "1.1"')
    out.append('baseline_revision: "78e789369e3392f187e8c63753262669108fda81"')
    out.append("generated_from:")
    out.append('  - path: "launchpad/Research/documentation-corpus-review/"')
    out.append("    files_reviewed: 41")
    out.append("    files_unreadable: 0")
    out.append("rules:")
    out.extend("  - " + quote(r) for r in RULES)
    out.append("result_states: [" + ", ".join(s.lower() for s in states) + "]")
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
    text = SRC.read_text(encoding="utf-8")
    items = parse(text)
    if not items:
        sys.exit("parsed zero items - the Markdown item format has probably changed")

    # Independent count, not derived from ITEM_RE. A block the item pattern
    # cannot parse is dropped silently by re.findall; this is what makes that
    # loud. It has caught a real regression once, when 21 tagged items vanished.
    declared = len(re.findall(ITEM_COUNT_RE, text, re.M))
    if declared != len(items):
        parsed_ids = {i["id"] for i in items}
        all_ids = set(re.findall(r"^\*\*([A-Z]+-\d{3}) · ", text, re.M))
        sys.exit(
            f"{declared} item headings in the Markdown but {len(items)} parsed. "
            f"Unparsed: {sorted(all_ids - parsed_ids)}"
        )

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

    OUT.write_text(render(items, parse_result_states(text)), encoding="utf-8")
    by_cat = collections.Counter(i["category"] for i in items)
    print(f"wrote {OUT.name}: {len(items)} items")
    print(f"  categories: {dict(by_cat)}")
    print(f"  corpus-gap items: {sum(1 for i in items if i['corpus_gap'])}")


if __name__ == "__main__":
    main()
