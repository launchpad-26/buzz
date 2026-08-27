#!/usr/bin/env python3
"""#287 STEP 6: the issue's five named control shapes, plus STEP 5's sixth.

No network. `PR #261`/`PR #264` are real fixtures, recorded (not re-fetched
live here) under `fixtures/verdict_blocks/` -- see that directory's
PROVENANCE.md and `recordings/FALSIFIABILITY.md` for what is real and how
that claim is checked. Every other shape is synthetic, built directly from
`pr_comments.CommentFetch`/`TaggedBlock` and `verdict_blocks.LocatedBlock`.

Six shapes, six distinct test methods -- not one method asserting all six,
per this plan's own GATES note that `serina:review-tests` checks specifically
for that.

Run:  python3 -m unittest test_verdict_resolution    (from launchpad/review-agent/)
  or: python3 test_verdict_resolution.py
"""

from __future__ import annotations

import json
import os
import unittest

from pr_comments import CommentFetch, TaggedBlock, from_items
from verdict_blocks import LocatedBlock, locate_verdict_blocks
from verdict_resolution import resolve

HERE = os.path.dirname(os.path.abspath(__file__))
RECORDINGS_DIR = os.path.join(HERE, "fixtures", "verdict_blocks", "recordings")

ROW = "CONFIRMED\tHigh\tfoo.py:1\tsomething is wrong"


def _load_recording(pr: int) -> list[dict]:
    with open(os.path.join(RECORDINGS_DIR, f"pr-{pr}-comments.json"), encoding="utf-8") as handle:
        return json.load(handle)


def _empty_fetch() -> CommentFetch:
    return CommentFetch(state="ok", blocks=[])


def _well_formed_located(text: str = ROW) -> LocatedBlock:
    return LocatedBlock(start_line=1, end_line=3, closed=True, info="verdict", raw_rows=text)


class ZeroBlocksTests(unittest.TestCase):
    """Shape 1: no ```verdict block anywhere -- "none found", not an error."""

    def test_zero_blocks_resolves_to_none_found(self) -> None:
        results = {"issue": _empty_fetch(), "review": _empty_fetch()}
        resolution = resolve(results)
        self.assertEqual(resolution.outcome, "none_found")
        self.assertIsNone(resolution.accepted)


class OneBlockTests(unittest.TestCase):
    """Shape 2: exactly one closed, well-formed block -- accepted."""

    def test_one_well_formed_block_is_accepted(self) -> None:
        tb = TaggedBlock(_well_formed_located(), comment_id=1, surface="issue", created_at="t1", position=0)
        results = {"issue": CommentFetch(state="ok", blocks=[tb]), "review": _empty_fetch()}
        resolution = resolve(results)
        self.assertEqual(resolution.outcome, "accepted")
        self.assertIsNotNone(resolution.accepted)
        self.assertEqual(resolution.accepted.location.comment_id, 1)
        self.assertEqual(len(resolution.accepted.rows), 1)
        self.assertEqual(resolution.superseded, [])


class SameCommentDoubleBlockTests(unittest.TestCase):
    """Shape 3: two WELL-FORMED, CLOSED blocks in one comment.

    Deliberately not a malformed pair -- a malformed pair would pass through
    the catch-all malformed branch instead of proving the same-comment
    branch specifically runs and wins ahead of the accept-last branch.
    """

    def test_two_well_formed_blocks_in_one_comment_are_refused(self) -> None:
        tb1 = TaggedBlock(_well_formed_located(), comment_id=1, surface="issue", created_at="t1", position=0)
        tb2 = TaggedBlock(_well_formed_located(), comment_id=1, surface="issue", created_at="t1", position=1)
        results = {"issue": CommentFetch(state="ok", blocks=[tb1, tb2]), "review": _empty_fetch()}
        resolution = resolve(results)
        self.assertEqual(resolution.outcome, "refused")
        self.assertIsNone(resolution.accepted)
        self.assertEqual({loc.position for loc in resolution.refused_locations}, {0, 1})


class DifferentCommentsRealFixtureTests(unittest.TestCase):
    """Shape 4: two blocks across two DIFFERENT comments -- accept the last by
    (created_at, comment_id), report the other superseded. Real fixtures:
    the actual #261 and #264 double-block comment sets."""

    def _resolve_recorded(self, pr: int):
        items = _load_recording(pr)
        return resolve({"issue": from_items(items, "issue"), "review": _empty_fetch()})

    def test_pr_261_accepts_the_later_comment(self) -> None:
        resolution = self._resolve_recorded(261)
        self.assertEqual(resolution.outcome, "accepted")
        self.assertEqual(resolution.accepted.location.comment_id, 5364261676)
        self.assertEqual([loc.comment_id for loc in resolution.superseded], [5364185647])

    def test_pr_264_accepts_the_blocker_promotion(self) -> None:
        resolution = self._resolve_recorded(264)
        self.assertEqual(resolution.outcome, "accepted")
        self.assertEqual(resolution.accepted.location.comment_id, 5364504768)
        self.assertEqual([loc.comment_id for loc in resolution.superseded], [5364221899])
        # The named promotion: row 1's severity moved High -> Blocker.
        row1 = resolution.accepted.rows[0]
        self.assertEqual(row1.severity, "Blocker")


class QuotedAndIndentedLookalikeTests(unittest.TestCase):
    """Shape 5: a fenced block inside a quoted-or-indented context that only
    looks like a real verdict block -- must resolve as if it were not there."""

    def test_blockquoted_fence_is_not_a_block(self) -> None:
        body = (
            "Quoting an earlier reviewer's block:\n\n"
            "> ```verdict\n"
            f"> {ROW}\n"
            "> ```\n\n"
            "My own comment carries no verdict block of its own."
        )
        located = locate_verdict_blocks(body)
        self.assertEqual(located, [])
        cf = from_items([{"id": 1, "created_at": "t1", "body": body}], "issue")
        resolution = resolve({"issue": cf, "review": _empty_fetch()})
        self.assertEqual(resolution.outcome, "none_found")

    def test_indented_fence_is_not_a_block(self) -> None:
        body = f"Prose.\n\n    ```verdict\n    {ROW}\n    ```\n"
        located = locate_verdict_blocks(body)
        self.assertEqual(located, [])
        cf = from_items([{"id": 1, "created_at": "t1", "body": body}], "issue")
        resolution = resolve({"issue": cf, "review": _empty_fetch()})
        self.assertEqual(resolution.outcome, "none_found")


class UnreadableFetchTests(unittest.TestCase):
    """Shape 6: an unreadable/absent comment fetch -- refused as "unreadable",
    never rendered the same as a clean zero-block PR."""

    def test_absent_surface_resolves_to_unreadable(self) -> None:
        results = {
            "issue": CommentFetch(state="absent", reason="gh timed out after 60s"),
            "review": _empty_fetch(),
        }
        resolution = resolve(results)
        self.assertEqual(resolution.outcome, "unreadable")
        self.assertNotEqual(resolution.outcome, "none_found")

    def test_oversized_surface_resolves_to_unreadable(self) -> None:
        results = {
            "issue": _empty_fetch(),
            "review": CommentFetch(state="oversized", reason="over the per-entry-point cap"),
        }
        resolution = resolve(results)
        self.assertEqual(resolution.outcome, "unreadable")


if __name__ == "__main__":
    unittest.main()
