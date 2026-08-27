"""#287 STEP 4 control: fetch + locate against the real, live GitHub API.

Needs network (`gh api` against launchpad-26/buzz). This is the plan's own
`RUNS HERE` step: the first control in this plan that proves something
against real data, not synthetic fixtures.
"""

from __future__ import annotations

import sys

from pr_comments import fetch_and_locate

REPO = "launchpad-26/buzz"

FAILURES: list[str] = []


def check(label: str, condition: bool, detail: str = "") -> None:
    if condition:
        print(f"PASS  {label}")
    else:
        FAILURES.append(label)
        print(f"FAIL  {label}  {detail}")


def _issue_comment_ids(pr: int) -> list[int]:
    results = fetch_and_locate(pr, REPO)
    cf = results["issue"]
    check(f"PR #{pr} issue surface is readable", cf.readable, f"state={cf.state} reason={cf.reason}")
    return sorted(tb.comment_id for tb in cf.blocks)


def test_pr_261() -> None:
    ids = _issue_comment_ids(261)
    check(
        "PR #261: exactly the two known blocks, tagged with the right comment ids",
        ids == sorted([5364185647, 5364261676]),
        f"got {ids}",
    )


def test_pr_264() -> None:
    ids = _issue_comment_ids(264)
    check(
        "PR #264: exactly the two known blocks, tagged with the right comment ids",
        ids == sorted([5364221899, 5364504768]),
        f"got {ids}",
    )


def test_invalid_pr_is_unreadable() -> None:
    results = fetch_and_locate(999999999, REPO)
    cf = results["issue"]
    check(
        "an invalid PR number reports an unreadable state, not zero comments",
        not cf.readable and cf.state == "absent",
        f"got state={cf.state} readable={cf.readable} blocks={cf.blocks}",
    )


def main() -> int:
    test_pr_261()
    test_pr_264()
    test_invalid_pr_is_unreadable()

    if FAILURES:
        print(f"\n{len(FAILURES)} failed: {FAILURES}")
        return 1
    print("\nall STEP 4 live control shapes passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
