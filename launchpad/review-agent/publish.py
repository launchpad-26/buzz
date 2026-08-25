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

import argparse
import json
import os
import subprocess
import sys

import publish_render

DEFAULT_LOGIN = "github-actions[bot]"

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


def _build_argparser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=None, help="owner/repo, defaults to GITHUB_REPOSITORY")
    parser.add_argument("--as", dest="login", default=DEFAULT_LOGIN, help="the identity posting reviews")
    parser.add_argument("--dry-run", action="store_true", help="print the body, post nothing")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Read the seven-or-eight-key stdin document, render it, post or update.

    The document WRAPS #117's and #118's envelopes verbatim -- ``reports`` and
    ``containment`` mean here exactly what they mean there, per #117's own
    contract, so this never restates or renames a field inside them.
    ``adjudication`` is optional, exactly as ``containment`` was before #117
    settled it: a caller with no adjudication stage omits the key, and
    ``duplicate_groups`` defaults to empty rather than the key being required.
    """
    args = _build_argparser().parse_args(argv)

    if args.login == "":
        print("error: --as requires a non-empty login", file=sys.stderr)
        return 1

    repo = args.repo or os.environ.get("GITHUB_REPOSITORY")
    if not repo:
        print(
            "error: no repository specified -- pass --repo owner/name or set "
            "GITHUB_REPOSITORY",
            file=sys.stderr,
        )
        return 1

    try:
        document = json.loads(sys.stdin.read())
    except json.JSONDecodeError as exc:
        print(f"error: malformed JSON on stdin: {exc}", file=sys.stderr)
        return 1

    adjudication = document.get("adjudication") or {}
    duplicate_groups = adjudication.get("duplicate_groups", ())

    body = publish_render.render_body(
        MARKER,
        document.get("reports"),
        document.get("stages"),
        document.get("containment"),
        document.get("head_sha"),
        document.get("merge_base_sha"),
        duplicate_groups=duplicate_groups,
        nonce=document.get("nonce"),
    )

    if args.dry_run:
        print(body)
        return 0

    pr = document.get("pr")
    if not isinstance(pr, int):
        print(
            f"error: stdin document has no valid integer 'pr' field, got {pr!r}",
            file=sys.stderr,
        )
        return 1

    review_id, action, author_login = post_or_update(pr, repo, body, args.login)
    print(f"{action} review {review_id} as {author_login}")

    # STEP 9's identity control reads this in a LATER step of the same job --
    # the live credential's actual login only exists inside this process, off
    # the POST/PUT response, and $GITHUB_OUTPUT is how a value crosses that
    # step boundary. Absent outside Actions, so this is a no-op locally.
    github_output = os.environ.get("GITHUB_OUTPUT")
    if github_output:
        with open(github_output, "a", encoding="utf-8") as handle:
            handle.write(f"author_login={author_login}\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
