"""Fetch one PR's full comment set, per-comment, and locate every ```verdict block.

Implements launchpad-26/buzz#287 STEP 4. `fetch.py`'s `Surface`/`_joined()`
flattens every comment into one joined string and discards comment id,
author, and creation time entirely -- not reusable here. STEP 5's
resolution rule needs per-comment boundaries, to refuse a same-comment
double-block, and `(created_at, comment_id)` ordering, to pick "the last
one" across different comments -- both erased by `_joined`.

This module borrows `fetch.py`'s pagination incantation (`gh api --paginate
--slurp` against both `issues/{pr}/comments` and `pulls/{pr}/comments`) and
its `UNREADABLE` state model / `CAP_PER_ENTRY_POINT` cap, applied per
surface here rather than to one joined string, so a failed or oversized
fetch is a distinguishable state per surface, never silently "zero
comments".
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field

import fetch
from verdict_blocks import LocatedBlock, locate_verdict_blocks

DEFAULT_REPO = fetch.DEFAULT_REPO

#: The two comment surfaces #287's OPEN section keeps in scope. `fetch.py`
#: already distinguishes them; excluding one silently here would be a
#: narrower guard than the issue asks for (see the plan's OPEN section).
SURFACE_ENDPOINTS = {
    "issue": "issues/{pr}/comments",
    "review": "pulls/{pr}/comments",
}


@dataclass
class TaggedBlock:
    """One located ```verdict block, tagged with where it came from."""

    block: LocatedBlock
    comment_id: int
    surface: str  # "issue" | "review"
    created_at: str
    position: int  # 0-indexed position of this block within its own comment


@dataclass
class CommentFetch:
    """One surface's fetch outcome: readable ("ok") or one of fetch.UNREADABLE."""

    state: str
    reason: str = ""
    blocks: list[TaggedBlock] = field(default_factory=list)

    @property
    def readable(self) -> bool:
        return self.state not in fetch.UNREADABLE


def _fetch_items(endpoint: str) -> tuple[str, list[dict], str]:
    """Returns (state, items, reason). Mirrors `fetch._json_field` + `fetch._classify`,
    applied to a paginated comment list rather than a single JSON field."""
    state, out, reason = fetch._gh(["api", "--paginate", "--slurp", endpoint])
    if state != "ok":
        return state, [], reason
    try:
        pages = json.loads(out)
    except json.JSONDecodeError as exc:
        return "unparseable", [], f"malformed JSON: {exc}"
    try:
        items = [item for page in pages for item in page]
    except TypeError as exc:
        return "unparseable", [], f"unexpected shape: {exc}"
    total_bytes = sum(len((item.get("body") or "").encode("utf-8")) for item in items)
    if total_bytes > fetch.CAP_PER_ENTRY_POINT:
        return (
            "oversized",
            items,
            f"{total_bytes} bytes exceeds the {fetch.CAP_PER_ENTRY_POINT}-byte cap; "
            "refused rather than truncated",
        )
    return "ok", items, ""


def fetch_and_locate(pr: int, repo: str = DEFAULT_REPO) -> dict[str, CommentFetch]:
    """One CommentFetch per surface: "issue" and "review".

    Every ```verdict block in every comment on that surface is located and
    tagged with its source comment's id, surface, created_at, and position
    within that comment -- the shape STEP 5's resolution rule consumes.
    """
    base = f"repos/{repo}"
    result: dict[str, CommentFetch] = {}
    for surface, template in SURFACE_ENDPOINTS.items():
        endpoint = f"{base}/{template.format(pr=pr)}"
        state, items, reason = _fetch_items(endpoint)
        if state != "ok":
            result[surface] = CommentFetch(state=state, reason=reason)
            continue
        tagged: list[TaggedBlock] = []
        for item in items:
            comment_id = item.get("id")
            created_at = item.get("created_at") or ""
            body = item.get("body") or ""
            located = locate_verdict_blocks(body)
            for position, block in enumerate(located):
                tagged.append(TaggedBlock(block, comment_id, surface, created_at, position))
        result[surface] = CommentFetch(state="ok", blocks=tagged)
    return result


def degrade(results: dict[str, CommentFetch], spec: str) -> dict[str, CommentFetch]:
    """Force a surface into a degenerate state, mirroring `fetch.degrade`'s CLI shape:
    ``degrade(results, "issue=absent")``."""
    surface, _, state = spec.partition("=")
    if surface not in SURFACE_ENDPOINTS:
        raise ValueError(f"unknown surface: {surface!r}")
    if state not in fetch.UNREADABLE:
        raise ValueError(f"unknown unreadable state: {state!r}")
    results = dict(results)
    results[surface] = CommentFetch(state=state, reason=f"forced by --degrade {spec}")
    return results


def _main(argv: list[str]) -> int:
    """CLI: ``python3 pr_comments.py <pr> [repo]`` -- prints every tagged block found."""
    if not argv:
        print("usage: pr_comments.py <pr> [repo]", file=__import__("sys").stderr)
        return 2
    pr = int(argv[0])
    repo = argv[1] if len(argv) > 1 else DEFAULT_REPO
    results = fetch_and_locate(pr, repo)
    for surface, cf in results.items():
        if not cf.readable:
            print(f"{surface}: UNREADABLE state={cf.state!r} reason={cf.reason!r}")
            continue
        print(f"{surface}: {len(cf.blocks)} block(s)")
        for tb in cf.blocks:
            print(
                f"  comment={tb.comment_id} created_at={tb.created_at} "
                f"position={tb.position} closed={tb.block.closed}"
            )
    return 0


if __name__ == "__main__":
    import sys

    sys.exit(_main(sys.argv[1:]))
