#!/usr/bin/env python3
"""Re-record #287's real double-block fixtures from the live PRs they came from.

Needs network (`gh api` against launchpad-26/buzz). Writes exactly the two
comments named in ADJUDICATION.md's #287 section for each PR to
``recordings/pr-<n>-comments.json`` -- id, created_at, user.login, and body,
unmodified from what `gh api` returns. No content in either file is
hand-typed; running this script is the only way either file's bytes are
produced. See PROVENANCE.md.

Run:  python3 generate.py    (from this directory, or anywhere -- it locates
                               launchpad/review-agent/ from its own path)
"""

from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REVIEW_AGENT_DIR = os.path.dirname(os.path.dirname(HERE))
if REVIEW_AGENT_DIR not in sys.path:
    sys.path.insert(0, REVIEW_AGENT_DIR)

import fetch  # noqa: E402

REPO = "launchpad-26/buzz"
RECORDINGS_DIR = os.path.join(HERE, "recordings")

#: (PR number, [comment ids to keep]) -- the exact pair named in
#: ADJUDICATION.md's #287 section for each PR.
TARGETS = {
    261: [5364185647, 5364261676],
    264: [5364221899, 5364504768],
}


def _fetch_comments(pr: int) -> list[dict]:
    state, out, reason = fetch._gh(
        ["api", "--paginate", "--slurp", f"repos/{REPO}/issues/{pr}/comments"]
    )
    if state != "ok":
        raise RuntimeError(f"PR #{pr}: fetch failed ({state}): {reason}")
    pages = json.loads(out)
    return [item for page in pages for item in page]


def record(pr: int, wanted_ids: list[int]) -> str:
    items = _fetch_comments(pr)
    by_id = {item["id"]: item for item in items}
    missing = [cid for cid in wanted_ids if cid not in by_id]
    if missing:
        raise RuntimeError(f"PR #{pr}: comment id(s) not found in live fetch: {missing}")
    kept = sorted(
        (
            {
                "id": by_id[cid]["id"],
                "created_at": by_id[cid]["created_at"],
                "user": {"login": by_id[cid]["user"]["login"]},
                "body": by_id[cid]["body"],
            }
            for cid in wanted_ids
        ),
        key=lambda c: c["id"],
    )
    return json.dumps(kept, indent=2) + "\n"


def main() -> int:
    os.makedirs(RECORDINGS_DIR, exist_ok=True)
    for pr, wanted_ids in TARGETS.items():
        text = record(pr, wanted_ids)
        path = os.path.join(RECORDINGS_DIR, f"pr-{pr}-comments.json")
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(text)
        print(f"wrote {os.path.relpath(path, HERE)} ({len(text)} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
