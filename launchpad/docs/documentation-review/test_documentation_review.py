#!/usr/bin/env python3
"""Validate this framework against its own rules.

IN PLAIN TERMS
    What this is   The test suite for these documents. It checks that the
                   checklist and its machine-readable twin agree, that every
                   item is complete, and that the docs obey the two
                   reader-first rules they impose on everyone else.
    Who it is for  Anyone changing anything in this directory, and CI.
    What to do     Run it from this directory:
                       python3 test_documentation_review.py
                   Exit 0 means every check passed. Exit 1 lists the failures.
    Know this      A framework that does not pass its own READER-001 and
                   READER-002 has no standing to require them of anyone else.

HOW IT WORKS

    03-master-checklist.md ----+
    checklist.yaml ------------+---> parity, completeness, dependency checks
    *.md ----------------------+---> reader-first, fences, links

Each check prints PASS or FAIL with a count. Nothing is skipped silently; a
check that cannot run is reported as a failure, never as a pass.
"""

import pathlib
import re
import sys

try:
    import yaml
except ImportError:
    sys.exit("PyYAML is required: pip install pyyaml")

HERE = pathlib.Path(__file__).resolve().parent
CHECKLIST_MD = HERE / "03-master-checklist.md"
CHECKLIST_YAML = HERE / "checklist.yaml"

REQUIRED_FIELDS = (
    "id",
    "category",
    "requirement",
    "audience",
    "applicability",
    "applies_when",
    "priority_default",
    "rationale",
    "evidence_required",
    "suggested_locations",
    "source_references",
    "audit_method",
    "automation_potential",
    "failure_risk",
)

failures: list[str] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    print(f"  {'PASS' if ok else 'FAIL'}  {name}{' — ' + detail if detail else ''}")
    if not ok:
        failures.append(f"{name}: {detail}")


def main() -> int:
    print("Validating the documentation-review framework\n")

    for path in (CHECKLIST_MD, CHECKLIST_YAML):
        if not path.exists():
            check(f"{path.name} exists", False, "missing")
            return finish()

    md_text = CHECKLIST_MD.read_text(encoding="utf-8")
    data = yaml.safe_load(CHECKLIST_YAML.read_text(encoding="utf-8"))
    items = data.get("items") or []

    print("Checklist integrity")
    # DELIBERATELY LOOSER THAN THE GENERATOR'S PATTERN. The generator requires
    # `**ID · text**` followed by an em-dash field block; this requires only a
    # bolded ID at the start of a line. That difference is the whole point.
    #
    # Until 2026-09-14 this scan was `r"^\*\*([A-Z]+-\d{3}) "` — the generator's
    # own shape. A cross-model review then deleted one space (`**READER-002 ·`
    # became `**READER-002·`) and BOTH parsers skipped the item identically: the
    # generator wrote 121 items, `item_count` self-reported 121, the two ID sets
    # matched each other because both were missing the same ID, and the suite
    # exited 0 — while the README claimed it "fails loudly rather than silently
    # dropping an item".
    #
    # A parity test written in the generator's own vocabulary cannot see what
    # that vocabulary cannot express. The check only has force if the two
    # parsers can DISAGREE, so this one is intentionally permissive: anything a
    # reader would recognise as an item heading must survive into the YAML.
    md_ids = set(re.findall(r"^\*\*([A-Z]+-\d{3})\b", md_text, re.M))
    yaml_ids = {i["id"] for i in items}

    check("YAML parses and has items", bool(items), f"{len(items)} items")
    check(
        "declared item_count matches actual",
        data.get("item_count") == len(items),
        f"declared {data.get('item_count')}, actual {len(items)}",
    )
    check(
        "IDs are unique in the YAML",
        len(yaml_ids) == len(items),
        f"{len(items) - len(yaml_ids)} duplicates",
    )
    check(
        "Markdown and YAML contain the same IDs",
        md_ids == yaml_ids,
        f"differ by {sorted(md_ids ^ yaml_ids)}" if md_ids != yaml_ids else "",
    )

    # CONTENT parity, not just ID parity. Matching ID sets says the same items
    # exist on both sides; it says nothing about whether they still say the same
    # thing. The same cross-model review replaced a YAML requirement with
    # contradictory text and the suite passed, because nothing compared the
    # words. An ID-only check licenses exactly the drift generation was adopted
    # to make impossible.
    # GREEDY, and emphasis-stripped, to match what the generator now stores.
    # This pattern was `(.+?)` — non-greedy — so it stopped at the FIRST `**` and
    # reproduced the generator's own truncation on BOTH sides of the comparison.
    # Two parsers sharing a defect agree perfectly and prove nothing: START-006,
    # OPS-006 and AGENT-001 each silently lost the word carrying their meaning
    # ("names", "restore", "not") while this check reported parity.
    md_requirements = {
        pid: re.sub(r"\*\*|__", "", req).strip()
        for pid, req in re.findall(
            r"^\*\*([A-Z]+-\d{3}) · (.+)\*\*", md_text, re.M
        )
    }
    mismatched = [
        i["id"]
        for i in items
        if i["id"] in md_requirements
        and " ".join((i.get("requirement") or "").split())
        != " ".join(md_requirements[i["id"]].split())
    ]
    check(
        "requirement text is identical in Markdown and YAML",
        not mismatched,
        f"{mismatched}" if mismatched else "",
    )

    empty = [
        i["id"] for i in items if any(not i.get(f) for f in REQUIRED_FIELDS)
    ]
    check("every item has all required fields", not empty, f"{empty}" if empty else "")

    dangling = [
        (i["id"], d)
        for i in items
        for d in (i.get("dependencies") or [])
        if d not in yaml_ids
    ]
    check(
        "dependencies resolve to real IDs",
        not dangling,
        f"{dangling}" if dangling else "",
    )

    bad_priority = [
        i["id"] for i in items if i["priority_default"] not in {"P0", "P1", "P2", "P3"}
    ]
    check("priorities are P0-P3", not bad_priority, f"{bad_priority}")

    bad_applic = [
        i["id"]
        for i in items
        if i["applicability"] not in {"required", "conditional", "optional"}
    ]
    check("applicability values are valid", not bad_applic, f"{bad_applic}")

    print("\nReader-first rules, applied to this framework's own documents")
    docs = sorted(p for p in HERE.glob("*.md"))
    check("markdown documents found", bool(docs), f"{len(docs)} files")

    no_summary, no_diagram, no_equiv, unbalanced = [], [], [], []
    for doc in docs:
        text = doc.read_text(encoding="utf-8")
        if "## In plain terms" not in text:
            no_summary.append(doc.name)
        if not re.search(r"^```mermaid", text, re.M):
            no_diagram.append(doc.name)
        if not re.search(r"^\*In words:\*", text, re.M):
            no_equiv.append(doc.name)
        if len(re.findall(r"^```", text, re.M)) % 2:
            unbalanced.append(doc.name)

    check("READER-001 — every doc opens with a plain summary", not no_summary, f"{no_summary}")
    check("READER-002a — every doc has a diagram", not no_diagram, f"{no_diagram}")
    check("READER-002b — every diagram has a text equivalent", not no_equiv, f"{no_equiv}")
    check("code fences are balanced", not unbalanced, f"{unbalanced}")

    print("\nCross-references")
    broken = []
    total = 0
    for doc in docs:
        text = re.sub(r"```.*?```", "", doc.read_text(encoding="utf-8"), flags=re.S)
        # Inline code spans too, not just fenced blocks. A document that QUOTES a
        # link as an example — `![image](url)` — is not carrying that link, and
        # counting it both invents a broken link and inflates the denominator.
        # The independent review made the same point about the audit's own link
        # census: quoted examples are not interchangeable with rendered links.
        text = re.sub(r"`[^`\n]*`", "", text)
        for link in re.findall(r"\]\(([^)\s#]+)", text):
            if link.startswith(("http", "mailto")):
                continue
            total += 1
            if not (HERE / link).exists():
                broken.append(f"{doc.name} -> {link}")
    check("relative links resolve", not broken, f"{broken}" if broken else f"{total} checked")

    generator = HERE / "generate_checklist_yaml.py"
    check(
        "the generator named by checklist.yaml exists",
        generator.exists(),
        "" if generator.exists() else "generate_checklist_yaml.py missing",
    )

    return finish()


def finish() -> int:
    print()
    if failures:
        print(f"FAILED — {len(failures)} check(s) did not pass:")
        for f in failures:
            print(f"  - {f}")
        return 1
    print("All checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
