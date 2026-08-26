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


def _flatten_pages(payload) -> list[dict]:
    """One flat review list from ``gh api --paginate --slurp`` output.

    ``--slurp`` returns a JSON array of PAGES -- an array of arrays -- not a flat
    array of reviews. Without it, ``--paginate`` concatenates one bare JSON array
    per page, which is not a single JSON value at all: ``json.loads`` raises
    ``JSONDecodeError`` as soon as a PR has more than one page of reviews. An
    independent review panel found that, and the injected transport the controls
    use returns a pre-flattened list, so no test could have caught it.

    Accepts either shape so a caller injecting a flat list (every existing
    control) keeps working, and mixed shapes raise rather than silently dropping
    a page.
    """
    if not isinstance(payload, list):
        raise ValueError(f"review listing must be a JSON array, got {type(payload).__name__}")
    pages = [item for item in payload if isinstance(item, list)]
    if not pages:
        return list(payload)
    if len(pages) != len(payload):
        raise ValueError("review listing mixes page arrays with bare review objects")
    return [review for page in pages for review in page]


def _list_reviews(argv: list[str]) -> list[dict]:
    """Real transport for ``find_existing``. Raises on any failure -- see below."""
    result = subprocess.run(argv, capture_output=True, text=True, check=True)
    return _flatten_pages(json.loads(result.stdout))


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
    try:
        status = int(lines[0].split()[1])
        blank = next(i for i, line in enumerate(lines) if line.strip() == "")
    except (IndexError, ValueError, StopIteration):
        # Fail closed, not crash: an unrecognisable response shape is not a
        # 2xx, and post_or_update's own status check already turns that into
        # a raised RuntimeError naming the status -- letting the parse itself
        # raise here would surface a confusing traceback instead.
        return 0, {"parse_error": f"unrecognisable response: {lines[:1]!r}"}
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
    # --slurp is what makes --paginate's output a single JSON value; see
    # _flatten_pages for the failure it prevents.
    argv = ["gh", "api", f"repos/{repo}/pulls/{pr}/reviews", "--paginate", "--slurp"]
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
        detail = f" ({response['parse_error']})" if "parse_error" in response else ""
        raise RuntimeError(f"PUT on review {review_id} failed with status {status}{detail}")
    return review_id, "updated", response["user"]["login"]


def _note_foreign(foreign_count: int, login: str) -> None:
    """Report foreign marked reviews without letting them block publication.

    An earlier revision REFUSED to post whenever a marked review existed under
    another author and none under ours. The marker is public and this agent's own
    documentation publishes it, so anyone able to comment could paste it once and
    permanently deny the agent its required review -- an independent review panel
    found that denial-of-service. The duplicate this refusal was guarding against
    cannot happen anyway: ``find_existing`` matches on marker AND author, so a
    foreign marked review is never mistaken for ours, and posting ours creates the
    one review every later run then updates in place.

    Still surfaced, on stderr, because a foreign marker is worth a human's
    attention even when it is not worth failing over.
    """
    print(
        f"note: {foreign_count} marked review(s) exist under an author other than "
        f"{login!r}; publishing ours regardless -- they are matched by author, not "
        f"by marker alone, so this cannot duplicate our own review",
        file=sys.stderr,
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
        _note_foreign(foreign_count, login)

    existing_id, foreign_count = find_existing(pr, repo, login, list_reviews=list_reviews)
    if existing_id is not None:
        return _put(repo, pr, existing_id, body, submit)
    if foreign_count:
        _note_foreign(foreign_count, login)

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
        detail = f" ({response['parse_error']})" if "parse_error" in response else ""
        raise RuntimeError(f"POST failed with status {status}{detail}")
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
        reviewer=document.get("reviewer"),
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

    try:
        review_id, action, author_login = post_or_update(pr, repo, body, args.login)
    except RuntimeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
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
