"""#287 STEP 5 control: the Option-B resolution rule.

Needs network for the #261/#264 live assertions; the remaining cases are
synthetic and construct `pr_comments.CommentFetch`/`TaggedBlock` directly so
they do not depend on the live API at all.
"""

from __future__ import annotations

import sys

from pr_comments import CommentFetch, TaggedBlock
from pr_comments import fetch_and_locate as live_fetch_and_locate
from verdict_blocks import LocatedBlock
from verdict_resolution import resolve

FAILURES: list[str] = []


def check(label: str, condition: bool, detail: str = "") -> None:
    if condition:
        print(f"PASS  {label}")
    else:
        FAILURES.append(label)
        print(f"FAIL  {label}  {detail}")


def test_pr_261_live() -> None:
    results = live_fetch_and_locate(261, "launchpad-26/buzz")
    resolution = resolve(results)
    check("PR #261 resolves to accepted", resolution.outcome == "accepted", resolution.reason)
    if resolution.accepted:
        check(
            "PR #261 accepts comment 5364261676's block",
            resolution.accepted.location.comment_id == 5364261676,
            f"got {resolution.accepted.location}",
        )
        check(
            "PR #261 reports comment 5364185647 as superseded",
            any(loc.comment_id == 5364185647 for loc in resolution.superseded),
            f"got {resolution.superseded}",
        )


def test_pr_264_live() -> None:
    results = live_fetch_and_locate(264, "launchpad-26/buzz")
    resolution = resolve(results)
    check("PR #264 resolves to accepted", resolution.outcome == "accepted", resolution.reason)
    if resolution.accepted:
        check(
            "PR #264 accepts comment 5364504768's block (the Blocker promotion)",
            resolution.accepted.location.comment_id == 5364504768,
            f"got {resolution.accepted.location}",
        )
        check(
            "PR #264 reports comment 5364221899 as superseded",
            any(loc.comment_id == 5364221899 for loc in resolution.superseded),
            f"got {resolution.superseded}",
        )


def _well_formed_block(text: str) -> LocatedBlock:
    return LocatedBlock(start_line=1, end_line=3, closed=True, raw_rows=text)


def _malformed_block() -> LocatedBlock:
    return LocatedBlock(start_line=1, end_line=3, closed=True, raw_rows="not enough fields")


ROW = "CONFIRMED\tHigh\tfoo.py:1\tsomething"


def test_two_well_formed_blocks_same_comment_refused() -> None:
    tb1 = TaggedBlock(_well_formed_block(ROW), comment_id=1, surface="issue", created_at="t1", position=0)
    tb2 = TaggedBlock(_well_formed_block(ROW), comment_id=1, surface="issue", created_at="t1", position=1)
    results = {"issue": CommentFetch(state="ok", blocks=[tb1, tb2]), "review": CommentFetch(state="ok")}
    resolution = resolve(results)
    check(
        "two well-formed closed blocks in ONE comment -> refused, not accepted",
        resolution.outcome == "refused",
        f"got {resolution.outcome} / {resolution.reason}",
    )
    check(
        "refusal names both positions",
        {loc.position for loc in resolution.refused_locations} == {0, 1},
        f"got {resolution.refused_locations}",
    )


def test_malformed_in_second_of_two_different_comments_refused() -> None:
    tb1 = TaggedBlock(_well_formed_block(ROW), comment_id=1, surface="issue", created_at="t1", position=0)
    tb2 = TaggedBlock(_malformed_block(), comment_id=2, surface="issue", created_at="t2", position=0)
    results = {"issue": CommentFetch(state="ok", blocks=[tb1, tb2]), "review": CommentFetch(state="ok")}
    resolution = resolve(results)
    check(
        "malformed row in second of two different-comment blocks -> refused",
        resolution.outcome == "refused",
        f"got {resolution.outcome} / {resolution.reason}",
    )
    check(
        "refusal names both locations",
        {loc.comment_id for loc in resolution.refused_locations} == {1, 2},
        f"got {resolution.refused_locations}",
    )


def test_unreadable_fetch_refused_distinct_from_none_found() -> None:
    results = {
        "issue": CommentFetch(state="absent", reason="gh timed out"),
        "review": CommentFetch(state="ok"),
    }
    resolution = resolve(results)
    check(
        "an unreadable comment fetch resolves to 'unreadable', not 'none_found'",
        resolution.outcome == "unreadable",
        f"got {resolution.outcome}",
    )


def main() -> int:
    test_pr_261_live()
    test_pr_264_live()
    test_two_well_formed_blocks_same_comment_refused()
    test_malformed_in_second_of_two_different_comments_refused()
    test_unreadable_fetch_refused_distinct_from_none_found()

    if FAILURES:
        print(f"\n{len(FAILURES)} failed: {FAILURES}")
        return 1
    print("\nall STEP 5 control shapes passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
