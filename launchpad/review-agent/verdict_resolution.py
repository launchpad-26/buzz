"""Resolve one PR's comment set to zero-or-one authoritative ```verdict block.

Implements launchpad-26/buzz#287 STEPs 5 and 7. The rule itself is
Option B, recorded in ADJUDICATION.md's "PR comment verdict blocks:
refusing more than one (#287)" section: no supersedes marker; the parser
deterministically takes the last complete, closed, well-formed block by
comment order, and refuses anything that does not reduce to exactly one
candidate that way.

``resolve`` (STEP 5) takes `pr_comments.fetch_and_locate`'s per-surface
output and applies SEVEN branches, IN ORDER -- order is load-bearing, since
more than one branch can match the same input and the first match must
win:

  1. any surface's comment fetch itself was unreadable  -> "unreadable"
  2. two or more blocks within the SAME comment          -> "refused"
  3. any other malformed case (a malformed row anywhere,
     or an unclosed block, in any comment)               -> "refused"
  4. a well-formed, closed block found on the "review"
     (inline code-comment) surface                       -> "refused" --
     never silently accepted, never silently folded into the ordering below,
     and never silently dropped as if it did not exist. Both #261 and #264
     (the only real production evidence Option B rests on) only ever used
     the issue-comment surface; see ADJUDICATION.md's #287 section for the
     scope decision this codifies -- only the issue-comment surface can
     supply an authoritative block.
  5. zero well-formed blocks anywhere                     -> "none_found"
  6. exactly one closed, well-formed block                -> "accepted"
  7. two or more closed, well-formed blocks, each in a
     DIFFERENT comment                                    -> "accepted",
     picking the block with the highest ``(created_at, comment_id)`` pair
     -- comment_id (monotonically increasing on GitHub) is the deciding
     tie-break, since created_at is only second-resolution. By branch 4,
     every block reaching here is already known to be on the issue surface.

``resolve_verdict`` (STEP 7) is the one importable entry point that chains
`pr_comments.fetch_and_locate` and `resolve` for a live PR number -- see
its own docstring for the consumer contract.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from pr_comments import CommentFetch, DEFAULT_REPO, TaggedBlock, fetch_and_locate
from verdict_blocks import MalformedRow, ParsedRow, parse_rows

#: The four outcomes `resolve` can reach. Never any other string.
OUTCOMES = ("unreadable", "refused", "none_found", "accepted")


@dataclass(frozen=True)
class BlockLocation:
    """Where one verdict block was found, and -- for a refusal -- why it
    counts against the set.

    ``comment_id``/``surface``/``position`` (0-indexed within that comment)
    satisfy STEP 5's naming requirement. ``start_line``/``end_line`` (from
    `verdict_blocks.LocatedBlock`, 1-indexed, ``end_line`` is ``None`` for an
    unclosed fence) point at the actual fence within the comment body, not
    only the comment as a whole. ``reason`` carries `verdict_blocks.
    parse_rows`'s own specific per-row reason string(s) when this location is
    part of a malformed refusal (branch 3) -- "" everywhere else -- so a
    refusal names the specific row and specific problem, never a single fixed
    sentence standing in for every possible cause.
    """

    comment_id: int
    surface: str
    position: int
    start_line: int
    end_line: int | None
    created_at: str = ""
    reason: str = ""


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


def _location(tb: TaggedBlock, reason: str = "") -> BlockLocation:
    return BlockLocation(
        comment_id=tb.comment_id,
        surface=tb.surface,
        position=tb.position,
        start_line=tb.block.start_line,
        end_line=tb.block.end_line,
        created_at=tb.created_at,
        reason=reason,
    )


def _evaluate(tb: TaggedBlock) -> tuple[bool, list[ParsedRow], list[MalformedRow]]:
    """(well_formed, parsed_rows, malformed_rows). well_formed requires closed
    AND every row parses. ``malformed_rows`` carries `verdict_blocks.
    parse_rows`'s own real ``MalformedRow`` objects -- never discarded --
    so branch 3 below can report their actual ``.reason`` strings. An
    unclosed block has no trustworthy row text to parse (nothing between an
    unterminated fence and EOF is a real row set), so it gets one synthetic
    ``MalformedRow`` naming exactly that, rather than an empty malformed list
    that would make it indistinguishable from "nothing wrong here yet".
    """
    if not tb.block.closed:
        return False, [], [MalformedRow(reason="block is never closed -- its fence has no matching closer")]
    rows = parse_rows(tb.block.raw_rows)
    malformed = [r for r in rows if isinstance(r, MalformedRow)]
    if malformed:
        return False, [], malformed
    return True, [r for r in rows if isinstance(r, ParsedRow)], []


def resolve(results: dict[str, CommentFetch]) -> Resolution:
    """Apply the seven branches above to one PR's fetched-and-located comment set."""
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
    # surface, and position, not only the offending one, and carries each
    # malformed block's own specific reason string(s) (empty for a
    # well-formed block named only because it shares the refused set).
    evaluations = [(tb, *_evaluate(tb)) for tb in all_blocks]
    if any(not well_formed for _, well_formed, _, _ in evaluations):
        refused = [
            _location(tb, reason="; ".join(m.reason for m in malformed))
            for tb, _well_formed, _rows, malformed in evaluations
        ]
        return Resolution(
            outcome="refused",
            reason="a malformed row or an unclosed block was found in the comment set",
            refused_locations=refused,
        )

    # Branch 4: a well-formed, closed block on the "review" (inline
    # code-comment) surface. Refused outright -- never silently accepted,
    # never silently merged into branch 7's cross-comment ordering (where a
    # later-created_at inline annotation could otherwise silently outrank a
    # real, complete issue-comment block), and never silently dropped as if
    # it were not there (that would make it indistinguishable from branch 5's
    # "none found"). See ADJUDICATION.md's #287 section.
    review_well_formed = [
        tb for tb, well_formed, _rows, _malformed in evaluations
        if well_formed and tb.surface == "review"
    ]
    if review_well_formed:
        return Resolution(
            outcome="refused",
            reason=(
                "a well-formed ```verdict block was found on the review "
                "(inline code-comment) surface; only the issue-comment "
                "surface can supply an authoritative block"
            ),
            refused_locations=[_location(tb) for tb in review_well_formed],
        )

    # Branch 5: zero blocks found anywhere -- a distinguishable "none found",
    # not an error.
    if not evaluations:
        return Resolution(outcome="none_found", reason="no ```verdict block in any comment")

    # Branches 6 and 7: every remaining block is closed, well-formed, on the
    # issue-comment surface (by branch 4), and (by branch 2) the only block
    # in its own comment -- so ordering by (created_at, comment_id) always
    # resolves to a single winner, whether there is one block or several
    # across different comments.
    ordered = sorted(evaluations, key=lambda e: (e[0].created_at, e[0].comment_id))
    winner_tb, _winner_well_formed, winner_rows, _winner_malformed = ordered[-1]
    superseded = [_location(tb) for tb, _wf, _rows, _mf in ordered[:-1]]
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
