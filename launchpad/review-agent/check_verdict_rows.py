"""#287 STEP 3 control: the row parser, on synthetic row text.

No network. Every case in STEP 3's `done when` is its own function.
"""

from __future__ import annotations

import sys

from verdict_blocks import MalformedRow, ParsedRow, parse_rows

FAILURES: list[str] = []


def check(label: str, condition: bool, detail: str = "") -> None:
    if condition:
        print(f"PASS  {label}")
    else:
        FAILURES.append(label)
        print(f"FAIL  {label}  {detail}")


def test_well_formed_row() -> None:
    rows = parse_rows("CONFIRMED\tHigh\tfoo.py:12\tsomething is wrong here")
    check("one well-formed row parses to one result", len(rows) == 1, f"got {rows!r}")
    if rows:
        r = rows[0]
        check("result is a ParsedRow, not malformed", isinstance(r, ParsedRow), f"got {r!r}")
        if isinstance(r, ParsedRow):
            check(
                "all four fields parse correctly",
                (r.verdict, r.severity, r.location, r.description)
                == ("CONFIRMED", "High", "foo.py:12", "something is wrong here"),
                f"got {r!r}",
            )


def test_short_row_is_malformed() -> None:
    raw = "CONFIRMED\tHigh\tfoo.py:12"
    rows = parse_rows(raw)
    check("a <4-field row produces one result", len(rows) == 1, f"got {rows!r}")
    if rows:
        r = rows[0]
        check("short row is flagged malformed", isinstance(r, MalformedRow), f"got {r!r}")
        if isinstance(r, MalformedRow):
            check("malformed message carries the row's own text", raw in r.reason, r.reason)


def test_five_field_row_joins_description() -> None:
    raw = "CONFIRMED\tHigh\tfoo.py:12\tfirst half\tsecond half after an inner tab"
    rows = parse_rows(raw)
    check("a 5-field row produces one result", len(rows) == 1, f"got {rows!r}")
    if rows:
        r = rows[0]
        check("5-field row is NOT malformed", isinstance(r, ParsedRow), f"got {r!r}")
        if isinstance(r, ParsedRow):
            check(
                "fields 4-5 are joined with a tab into description",
                r.description == "first half\tsecond half after an inner tab",
                f"got {r.description!r}",
            )


def test_unknown_verdict_is_malformed() -> None:
    raw = "MAYBE\tHigh\tfoo.py:12\tsomething"
    rows = parse_rows(raw)
    check("unknown verdict value flagged malformed", isinstance(rows[0], MalformedRow), f"got {rows!r}")


def test_unknown_severity_is_malformed() -> None:
    raw = "CONFIRMED\tCatastrophic\tfoo.py:12\tsomething"
    rows = parse_rows(raw)
    check("unknown severity value flagged malformed", isinstance(rows[0], MalformedRow), f"got {rows!r}")


def main() -> int:
    test_well_formed_row()
    test_short_row_is_malformed()
    test_five_field_row_joins_description()
    test_unknown_verdict_is_malformed()
    test_unknown_severity_is_malformed()

    if FAILURES:
        print(f"\n{len(FAILURES)} failed: {FAILURES}")
        return 1
    print("\nall STEP 3 control shapes passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
