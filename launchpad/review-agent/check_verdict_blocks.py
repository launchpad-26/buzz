"""#287 STEP 2 control: the fenced-block locator, on synthetic comment bodies.

No network. Every case in STEP 2's `done when` is its own function so a failure
names exactly which shape broke, not "the suite failed".
"""

from __future__ import annotations

import sys

from verdict_blocks import locate_verdict_blocks

FAILURES: list[str] = []


def check(label: str, condition: bool, detail: str = "") -> None:
    if condition:
        print(f"PASS  {label}")
    else:
        FAILURES.append(label)
        print(f"FAIL  {label}  {detail}")


def test_zero_blocks() -> None:
    body = "Just a normal comment with no fences at all.\n\nSecond paragraph."
    blocks = locate_verdict_blocks(body)
    check("zero blocks -> empty list", blocks == [], f"got {blocks!r}")


def test_one_closed_block() -> None:
    body = "Some prose.\n\n```verdict\nCONFIRMED\tHigh\tfoo.py:1\tsomething wrong\n```\n\nMore prose."
    blocks = locate_verdict_blocks(body)
    check("one closed block -> one entry", len(blocks) == 1, f"got {len(blocks)}: {blocks!r}")
    if blocks:
        b = blocks[0]
        check("closed block reports closed=True", b.closed is True)
        check("closed block has an end_line", b.end_line is not None)
        check(
            "closed block captures its row text",
            b.raw_rows == "CONFIRMED\tHigh\tfoo.py:1\tsomething wrong",
            f"got {b.raw_rows!r}",
        )


def test_one_unclosed_block() -> None:
    body = "Prose before.\n\n```verdict\nCONFIRMED\tHigh\tfoo.py:1\tsomething wrong\n"
    blocks = locate_verdict_blocks(body)
    check(
        "unclosed block is flagged, not dropped or empty",
        len(blocks) == 1 and blocks[0].closed is False and blocks[0].end_line is None,
        f"got {blocks!r}",
    )
    if blocks:
        check(
            "unclosed block still carries its row text",
            blocks[0].raw_rows == "CONFIRMED\tHigh\tfoo.py:1\tsomething wrong",
            f"got {blocks[0].raw_rows!r}",
        )


def test_blockquoted_fence_not_matched() -> None:
    body = (
        "Quoting an earlier reviewer:\n\n"
        "> ```verdict\n"
        "> CONFIRMED\tHigh\tfoo.py:1\tsomething wrong\n"
        "> ```\n\n"
        "My own take follows in prose only."
    )
    blocks = locate_verdict_blocks(body)
    check(
        "blockquoted ```verdict fence is not matched as top-level",
        blocks == [],
        f"got {blocks!r}",
    )


def test_indented_fence_not_matched() -> None:
    body = "Prose.\n\n    ```verdict\n    CONFIRMED\tHigh\tfoo.py:1\tsomething wrong\n    ```\n"
    blocks = locate_verdict_blocks(body)
    check(
        "4-space-indented ```verdict fence is not matched",
        blocks == [],
        f"got {blocks!r}",
    )


def test_unrelated_fence_not_matched() -> None:
    body = "```python\nprint('not a verdict block')\n```"
    blocks = locate_verdict_blocks(body)
    check("unrelated fenced code is not matched as a verdict block", blocks == [], f"got {blocks!r}")


def main() -> int:
    test_zero_blocks()
    test_one_closed_block()
    test_one_unclosed_block()
    test_blockquoted_fence_not_matched()
    test_indented_fence_not_matched()
    test_unrelated_fence_not_matched()

    if FAILURES:
        print(f"\n{len(FAILURES)} failed: {FAILURES}")
        return 1
    print("\nall STEP 2 control shapes passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
