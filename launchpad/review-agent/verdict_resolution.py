"""Resolve one PR's comment set to zero-or-one authoritative ```verdict block.

Implements launchpad-26/buzz#287 STEPs 5 and 7. The rule itself is
Option B, recorded in ADJUDICATION.md's "PR comment verdict blocks:
refusing more than one (#287)" section: no supersedes marker; the parser
deterministically takes the last complete, closed, well-formed block by
comment order, and refuses anything that does not reduce to exactly one
candidate that way.

``resolve`` (STEP 5) takes `pr_comments.fetch_and_locate`'s per-surface
output and applies six branches, IN ORDER -- order is load-bearing, since
more than one branch can match the same input and the first match must
win:

  1. any surface's comment fetch itself was unreadable  -> "unreadable"
  2. two or more blocks within the SAME comment          -> "refused"
  3. any other malformed case (a malformed row anywhere,
     or an unclosed block, in any comment)               -> "refused"
  4. zero well-formed blocks anywhere                     -> "none_found"
  5. exactly one closed, well-formed block                -> "accepted"
  6. two or more closed, well-formed blocks, each in a
     DIFFERENT comment                                    -> "accepted",
     picking the block with the highest ``(created_at, comment_id)`` pair
     -- comment_id (monotonically increasing on GitHub) is the deciding
     tie-break, since created_at is only second-resolution.

``resolve_verdict`` (STEP 7) is the one importable entry point that chains
`pr_comments.fetch_and_locate` and `resolve` for a live PR number -- see
its own docstring for the consumer contract.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from pr_comments import CommentFetch, TaggedBlock, fetch_and_locate
from verdict_blocks import MalformedRow, ParsedRow, parse_rows

DEFAULT_REPO = "launchpad-26/buzz"

#: The four outcomes `resolve` can reach. Never any other string.
OUTCOMES = ("unreadable", "refused", "none_found", "accepted")


@dataclass(frozen=True)
class BlockLocation:
    """Where one verdict block was found -- comment id, surface, and its
    position within that comment (0-indexed), per STEP 5's naming requirement."""

    comment_id: int
    surface: str
    position: int
    created_at: str = ""


@dataclass
class ResolvedBlock:
    """The accepted block's own parsed content, alongside where it came from."""

    location: BlockLocation
    rows: list[ParsedRow]


@dataclass
class Resolution:
    outcome: str  # one of OUTCOMES
    reason: str = ""
    accepted: ResolvedBlock | None = None
    superseded: list[BlockLocation] = field(default_factory=list)
    refused_locations: list[BlockLocation] = field(default_factory=list)


def _location(tb: TaggedBlock) -> BlockLocation:
    return BlockLocation(tb.comment_id, tb.surface, tb.position, tb.created_at)


def _evaluate(tb: TaggedBlock) -> tuple[bool, list[ParsedRow]]:
    """(well_formed, parsed_rows). well_formed requires closed AND every row parses."""
    if not tb.block.closed:
        return False, []
    rows = parse_rows(tb.block.raw_rows)
    if any(isinstance(r, MalformedRow) for r in rows):
        return False, []
    return True, [r for r in rows if isinstance(r, ParsedRow)]


def resolve(results: dict[str, CommentFetch]) -> Resolution:
    """Apply the six branches above to one PR's fetched-and-located comment set."""
    # Branch 1: the comment fetch itself was unreadable on any surface. Distinct
    # from "none found" -- CONTAINMENT.md's "absence of evidence is never
    # reported as evidence" -- so an unreadable fetch must never render the
    # same as a clean zero-block PR.
    unreadable_surfaces = [s for s, cf in results.items() if not cf.readable]
    if unreadable_surfaces:
        detail = "; ".join(
            f"{s}: {results[s].state} ({results[s].reason})" for s in unreadable_surfaces
        )
        return Resolution(
            outcome="unreadable",
            reason=f"comment fetch unreadable on surface(s): {detail}",
        )

    all_blocks: list[TaggedBlock] = []
    for cf in results.values():
        all_blocks.extend(cf.blocks)

    # Branch 2: two or more blocks within the SAME comment. Checked before the
    # accept-last branch below, since a same-comment pair that is also
    # individually well-formed would otherwise match both -- two fences posted
    # in one write can't be a temporal amendment of each other, so Option B's
    # ordering rule never applies to this shape.
    by_comment: dict[tuple[str, int], list[TaggedBlock]] = {}
    for tb in all_blocks:
        by_comment.setdefault((tb.surface, tb.comment_id), []).append(tb)
    same_comment_groups = [group for group in by_comment.values() if len(group) > 1]
    if same_comment_groups:
        locs = [_location(tb) for group in same_comment_groups for tb in group]
        return Resolution(
            outcome="refused",
            reason="two or more ```verdict blocks were posted within the same comment",
            refused_locations=locs,
        )

    # Branch 3: any other malformed case (a malformed row anywhere, or an
    # unclosed block, in any comment) -- names every block's comment id,
    # surface, and position, not only the offending one.
    evaluations = [(tb, *_evaluate(tb)) for tb in all_blocks]
    if any(not well_formed for _, well_formed, _ in evaluations):
        return Resolution(
            outcome="refused",
            reason="a malformed row or an unclosed block was found in the comment set",
            refused_locations=[_location(tb) for tb in all_blocks],
        )

    # Branch 4: zero blocks found anywhere -- a distinguishable "none found",
    # not an error.
    if not evaluations:
        return Resolution(outcome="none_found", reason="no ```verdict block in any comment")

    # Branches 5 and 6: every remaining block is closed, well-formed, and (by
    # branch 2 above) the only block in its own comment -- so ordering by
    # (created_at, comment_id) always resolves to a single winner, whether
    # there is one block or several across different comments.
    ordered = sorted(evaluations, key=lambda e: (e[0].created_at, e[0].comment_id))
    winner_tb, _, winner_rows = ordered[-1]
    superseded = [_location(tb) for tb, _, _ in ordered[:-1]]
    return Resolution(
        outcome="accepted",
        accepted=ResolvedBlock(location=_location(winner_tb), rows=winner_rows),
        superseded=superseded,
    )


def resolve_verdict(pr: int, repo: str = DEFAULT_REPO) -> Resolution:
    """The one entry point a future consumer calls: fetch PR ``pr``'s full
    comment set, live, and resolve it to zero-or-one authoritative verdict
    block per the Option-B rule this module's docstring states.

    **Consumer contract.** Two candidate future callers exist and neither
    calls this today, per the #287 issue's own "fixing this now is cheap:
    there is no consumer yet to migrate": #119's banner path (composes and
    publishes its own review; does not currently read PR comments at all)
    and #426's pre-review packet. Whichever wires this in owns checking
    ``Resolution.outcome`` -- "unreadable" and "refused" both mean no
    verdict may be treated as authoritative, "none_found" means no
    adjudication has been posted yet, and only "accepted" carries a real
    ``Resolution.accepted.rows`` list to act on.

    Return shape stability (smoke-level, not behavioural) is asserted by
    `check_resolve_verdict_contract.py`.
    """
    results = fetch_and_locate(pr, repo)
    return resolve(results)
