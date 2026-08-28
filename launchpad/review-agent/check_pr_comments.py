"""#287 STEP 4 control: fetch + locate against the real, live GitHub API.

Needs network (`gh api` against launchpad-26/buzz). This is the plan's own
`RUNS HERE` step: the first control in this plan that proves something
against real data, not synthetic fixtures.
"""

from __future__ import annotations

import sys

from pr_comments import degrade, fetch_and_locate

REPO = "launchpad-26/buzz"

FAILURES: list[str] = []


def check(label: str, condition: bool, detail: str = "") -> None:
    if condition:
        print(f"PASS  {label}")
    else:
        FAILURES.append(label)
        print(f"FAIL  {label}  {detail}")


def _check_pr(pr: int, expected_issue_ids: list[int]) -> None:
    """Asserts on BOTH surfaces `fetch_and_locate` returns -- not only "issue".
    Without checking "review" too, this control never actually proves PR
    #261/#264 have EXACTLY the two known blocks: an unnoticed extra block on
    the review-comment surface would sail through silently."""
    results = fetch_and_locate(pr, REPO)

    issue = results["issue"]
    check(f"PR #{pr} issue surface is readable", issue.readable, f"state={issue.state} reason={issue.reason}")
    ids = sorted(tb.comment_id for tb in issue.blocks)
    check(
        f"PR #{pr}: exactly the two known blocks on the issue surface, right comment ids",
        ids == sorted(expected_issue_ids),
        f"got {ids}",
    )

    review = results["review"]
    check(f"PR #{pr} review (inline-comment) surface is readable", review.readable, f"state={review.state} reason={review.reason}")
    check(
        f"PR #{pr} review surface carries zero ```verdict blocks",
        review.blocks == [],
        f"got {review.blocks!r}",
    )


def test_pr_261() -> None:
    _check_pr(261, [5364185647, 5364261676])


def test_pr_264() -> None:
    _check_pr(264, [5364221899, 5364504768])


def test_invalid_pr_is_unreadable() -> None:
    results = fetch_and_locate(999999999, REPO)
    cf = results["issue"]
    check(
        "an invalid PR number reports an unreadable state, not zero comments",
        not cf.readable and cf.state == "absent",
        f"got state={cf.state} readable={cf.readable} blocks={cf.blocks}",
    )


def test_degrade_forces_a_distinguishable_unreadable_state() -> None:
    """`degrade()` (STEP 4's stated alternate way to force "forced-unreadable",
    alongside the invalid-PR-number path above) actually gets called from
    somewhere -- this control, and the CLI's own `--degrade` flag."""
    results = fetch_and_locate(261, REPO)
    degraded = degrade(results, "review=oversized")
    check(
        "degrade() forces the named surface into the requested state",
        degraded["review"].state == "oversized" and not degraded["review"].readable,
        f"got {degraded['review']}",
    )
    check(
        "degrade() leaves the other surface untouched",
        degraded["issue"] is results["issue"],
    )
    check(
        "degrade()'s reason names the forcing spec",
        "--degrade review=oversized" in degraded["review"].reason,
        degraded["review"].reason,
    )


def test_degrade_accepts_fetch_pys_longer_surface_names() -> None:
    """review-final MEDIUM #5: `fetch.py` (same directory, same two GitHub
    endpoints) calls these surfaces `pr_issue_comments`/`pr_review_comments`
    -- the vocabulary `contain.py`/`run_dimensions.py`'s own `--degrade`
    flags already use. Both spellings must reach the identical state, not
    just avoid crashing."""
    results = fetch_and_locate(261, REPO)
    via_alias = degrade(results, "pr_review_comments=absent")
    via_short = degrade(results, "review=absent")
    check(
        "the fetch.py-style alias forces the same state as the short name",
        via_alias["review"].state == via_short["review"].state == "absent",
        f"alias={via_alias['review'].state} short={via_short['review'].state}",
    )


def main() -> int:
    test_pr_261()
    test_pr_264()
    test_invalid_pr_is_unreadable()
    test_degrade_forces_a_distinguishable_unreadable_state()
    test_degrade_accepts_fetch_pys_longer_surface_names()

    if FAILURES:
        print(f"\n{len(FAILURES)} failed: {FAILURES}")
        return 1
    print("\nall STEP 4 live control shapes passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
