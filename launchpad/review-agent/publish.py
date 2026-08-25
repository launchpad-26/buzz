"""Post or update the single COMMENT review this agent owns on a pull request.

Identification is by marker AND by author, and neither alone is sufficient: the
marker says "this is our kind of review", the author says "this one is ours". The
marker alone is attacker-writable -- any GitHub user with read access can submit a
COMMENT review on a public pull request and choose its body, marker included -- so
matching on the marker without the author check lets an outside party pick which
review object this agent tries to update, which turns into a denial of publication
the moment the PUT is refused for a review this token does not own.

A submitted COMMENT review cannot be deleted (measured live, #119 STEP 1: DELETE on
a submitted review returns 422), so once two of the agent's own markers exist on one
pull request neither can be retired. ``find_existing`` therefore always resolves to
the NEWEST review under the configured login, never the oldest, so the body a human
reads at the bottom of the timeline is always current.
"""

from __future__ import annotations

import json
import subprocess

#: First line of every body this agent posts. Passed into ``publish_render.render_body``
#: rather than imported there, so that module never imports this one -- see STEP 7's
#: ``main`` for why the other direction of that edge is normal and this one is not.
MARKER = "<!-- launchpad-review-agent:v1 -->"


def _list_reviews(argv: list[str]) -> list[dict]:
    """Real transport for ``find_existing``. Raises on any failure -- see below."""
    result = subprocess.run(argv, capture_output=True, text=True, check=True)
    return json.loads(result.stdout)


def _submit(argv: list[str]) -> tuple[int, dict]:
    """Real transport for ``post_or_update``'s POST/PUT calls.

    Runs with ``-i`` so the HTTP status is readable regardless of whether ``gh``
    exits zero -- a 4xx/5xx still prints its status line and JSON body to stdout,
    ``gh`` writes only its own one-line summary to stderr, which this deliberately
    does not capture. Combining the two streams is what corrupted an earlier
    fixture capture during STEP 1 with trailing non-JSON text; that failure is why
    this reads stdout alone.
    """
    result = subprocess.run(argv + ["-i"], capture_output=True, text=True)
    lines = result.stdout.splitlines()
    blank = next(i for i, line in enumerate(lines) if line.strip() == "")
    status = int(lines[0].split()[1])
    body_text = "\n".join(lines[blank + 1 :])
    body = json.loads(body_text) if body_text.strip() else {}
    return status, body


def find_existing(
    pr: int,
    repo: str,
    login: str,
    list_reviews=_list_reviews,
) -> tuple[int | None, int]:
    """(the id of the newest review under ``login`` that carries MARKER, the count
    of marked reviews under any OTHER author).

    An unresolved identity aborts rather than degrading to matching on the marker
    alone -- an empty or missing ``login`` raises.

    Paginates via ``--paginate`` and reads the whole listing; a partial listing
    (pagination failing part way) is indistinguishable from an empty one at the
    call site, so a failure here raises rather than returning ``(None, 0)``.
    """
    if not login:
        raise ValueError("find_existing requires a non-empty login")
    argv = ["gh", "api", f"repos/{repo}/pulls/{pr}/reviews", "--paginate"]
    reviews = list_reviews(argv)
    marked = [r for r in reviews if (r.get("body") or "").startswith(MARKER)]
    own = [r for r in marked if r.get("user", {}).get("login") == login]
    foreign_count = len(marked) - len(own)
    if not own:
        return None, foreign_count
    newest = max(own, key=lambda r: r["submitted_at"])
    return newest["id"], foreign_count


def _put(repo: str, pr: int, review_id: int, body: str, submit) -> tuple[int, str, str]:
    argv = [
        "gh",
        "api",
        f"repos/{repo}/pulls/{pr}/reviews/{review_id}",
        "-X",
        "PUT",
        "-f",
        f"body={body}",
    ]
    status, response = submit(argv)
    if not (200 <= status < 300):
        raise RuntimeError(f"PUT on review {review_id} failed with status {status}")
    return review_id, "updated", response["user"]["login"]


def _refuse(foreign_count: int, login: str) -> None:
    raise RuntimeError(
        f"refusing to post: {foreign_count} marked review(s) exist under an author "
        f"other than {login!r}, and none under {login!r} -- resolve manually before "
        f"publishing rather than risk a silent duplicate"
    )


def post_or_update(
    pr: int,
    repo: str,
    body: str,
    login: str,
    list_reviews=_list_reviews,
    submit=_submit,
) -> tuple[int, str, str]:
    """PUT when a review of ours already exists, POST otherwise.

    A nonzero foreign count refuses to post rather than creating a second review --
    see the module docstring. A failed PUT is a hard failure and never falls back to
    POST: that fallback would create the very duplicate this function exists to
    prevent, on exactly the run where something is already wrong.

    ``find_existing`` is called a second time immediately before the POST: two
    pushes seconds apart produce two workflow runs, and a check performed at the
    start of a run is stale by the time the run posts. The foreign-count refusal
    applies to this second call too.
    """
    existing_id, foreign_count = find_existing(pr, repo, login, list_reviews=list_reviews)
    if existing_id is not None:
        return _put(repo, pr, existing_id, body, submit)
    if foreign_count:
        _refuse(foreign_count, login)

    existing_id, foreign_count = find_existing(pr, repo, login, list_reviews=list_reviews)
    if existing_id is not None:
        return _put(repo, pr, existing_id, body, submit)
    if foreign_count:
        _refuse(foreign_count, login)

    argv = [
        "gh",
        "api",
        f"repos/{repo}/pulls/{pr}/reviews",
        "-X",
        "POST",
        "-f",
        f"body={body}",
        "-f",
        "event=COMMENT",
    ]
    status, response = submit(argv)
    if not (200 <= status < 300):
        raise RuntimeError(f"POST failed with status {status}")
    return response["id"], "created", response["user"]["login"]
