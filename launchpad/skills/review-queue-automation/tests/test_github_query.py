#!/usr/bin/env python3
"""`InventoryReader`'s own guards, at the transport boundary.

Closes the coverage gap #1974 found reviewing #1964. `github_query.py` has three
fail-closed mechanisms and `tests/test_queue.py` reached only two of them
through the reconciler:

  - nested-connection page cap        — covered there
  - `changedFiles` mismatch           — covered there
  - OUTER pull-request-walk page cap  — untested until now
  - allowlist rejection in `query()`  — untested until now

Both untested paths were correct as written; the risk was a future edit
quietly breaking a guard nothing watched. These tests drive the real
`InventoryReader` and substitute only its injected `http_post`, the one
function that would otherwise reach the network.
"""

from __future__ import annotations

import json
import pathlib
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scripts"))

import github_query  # noqa: E402
from common import State  # noqa: E402


def _reader(transport, **kwargs) -> github_query.InventoryReader:
    state = State({"state_dir": tempfile.mkdtemp()})
    return github_query.InventoryReader(
        {"github": {"timeout_seconds": 5}}, state, http_post=transport, token="fake-token", **kwargs
    )


def _pr_node(number: int) -> dict:
    """The minimum shape `_packet` accepts, with every connection complete."""
    empty = {"pageInfo": {"hasNextPage": False, "endCursor": None}, "nodes": []}
    return {
        "id": f"NODE-{number}",
        "number": number,
        "title": f"PR {number}",
        "url": f"https://github.com/o/r/pull/{number}",
        "isDraft": False,
        "updatedAt": "2026-08-31T00:00:00Z",
        "additions": 1,
        "deletions": 0,
        "changedFiles": 0,
        "reviewDecision": "",
        "baseRefName": "main",
        "headRefName": "feat",
        "headRefOid": f"head{number}",
        "author": {"login": "someone"},
        "assignees": dict(empty),
        "reviewRequests": dict(empty),
        "reviews": dict(empty),
        "files": dict(empty),
        "commits": {"nodes": []},
    }


# -- the outer pull-request walk ---------------------------------------------

def test_exceeding_the_outer_page_cap_raises_rather_than_truncating() -> None:
    """A queue larger than the walk can complete must not come back partial.

    The failure mode this prevents: reconciling on a subset of open pull
    requests reads exactly like reconciling on all of them.
    """
    pages = {"count": 0}

    def always_more(token, payload, *, timeout=60):
        pages["count"] += 1
        # Every page claims another after it, so the walk can never finish.
        return 200, {"data": {
            "repository": {"pullRequests": {
                "pageInfo": {"hasNextPage": True, "endCursor": f"CUR-{pages['count']}"},
                "nodes": [_pr_node(pages["count"])],
            }},
            "rateLimit": {"cost": 1, "remaining": 4999},
        }}

    reader = _reader(always_more)
    try:
        reader.queue_inventory("o/r")
        raise AssertionError("an unfinishable walk must raise, never return a partial queue")
    except github_query.InventoryError as exc:
        assert "refusing to reconcile an incomplete queue" in str(exc)
        assert str(github_query._PR_PAGE_CAP * github_query._PR_PAGE_SIZE) in str(exc)
    # Exactly `_PR_PAGE_CAP` requests, not one more: the guard raises BEFORE
    # spending a request whose result it would discard.
    assert pages["count"] == github_query._PR_PAGE_CAP, pages


def test_a_walk_that_fits_inside_the_cap_completes() -> None:
    """The control for the test above: the cap must not reject a legitimate walk."""
    pages = {"count": 0}
    total = github_query._PR_PAGE_CAP - 1

    def finite(token, payload, *, timeout=60):
        pages["count"] += 1
        more = pages["count"] < total
        return 200, {"data": {
            "repository": {"pullRequests": {
                "pageInfo": {"hasNextPage": more, "endCursor": f"CUR-{pages['count']}"},
                "nodes": [_pr_node(pages["count"])],
            }},
            "rateLimit": {"cost": 1, "remaining": 4999},
        }}

    packets = _reader(finite).queue_inventory("o/r")
    assert len(packets) == total
    assert pages["count"] == total


def test_a_repository_the_token_cannot_see_raises() -> None:
    def invisible(token, payload, *, timeout=60):
        return 200, {"data": {"repository": None, "rateLimit": {"cost": 1, "remaining": 4999}}}

    try:
        _reader(invisible).queue_inventory("o/r")
        raise AssertionError("an invisible repository must raise")
    except github_query.InventoryError as exc:
        assert "not visible to this token" in str(exc)


# -- the allowlist -----------------------------------------------------------

def test_an_operation_outside_the_allowlist_is_rejected() -> None:
    """Only the named queries may be sent, and the check runs before the network."""
    calls = []

    def recording(token, payload, *, timeout=60):
        calls.append(payload)
        return 200, {"data": {}}

    reader = _reader(recording)
    for operation in ("delete_everything", "queue_inventory_v2", "", "QUEUE_INVENTORY"):
        try:
            reader.query(operation, {})
            raise AssertionError(f"{operation!r} must be rejected")
        except github_query.InventoryError as exc:
            assert "unsupported read operation" in str(exc)
    assert calls == [], "a rejected operation must not reach the transport"


def test_a_mutation_shaped_document_is_rejected_even_if_allowlisted() -> None:
    """Defence in depth: the name being allowlisted is not enough.

    If an edit ever puts a mutation into `QUERIES` — by mistake or otherwise —
    the vocabulary check refuses it. Simulated by adding one, because no such
    document exists in the module and a test that cannot construct the condition
    cannot prove the guard fires.
    """
    calls = []

    def recording(token, payload, *, timeout=60):
        calls.append(payload)
        return 200, {"data": {}}

    reader = _reader(recording)
    original = dict(github_query.QUERIES)
    try:
        github_query.QUERIES["smuggled"] = "mutation Smuggled { addComment { id } }"
        try:
            reader.query("smuggled", {})
            raise AssertionError("a mutation document must be rejected")
        except github_query.InventoryError as exc:
            assert "contains 'mutation'" in str(exc)

        github_query.QUERIES["streamed"] = "subscription Streamed { events { id } }"
        try:
            reader.query("streamed", {})
            raise AssertionError("a subscription document must be rejected")
        except github_query.InventoryError as exc:
            assert "contains 'subscription'" in str(exc)
    finally:
        github_query.QUERIES.clear()
        github_query.QUERIES.update(original)
    assert calls == [], "a rejected document must not reach the transport"


def test_every_shipped_query_passes_its_own_vocabulary_check() -> None:
    """The guard must not be so broad it rejects the module's own documents."""
    reader = _reader(lambda token, payload, *, timeout=60: (200, {"data": {}}))
    for operation in github_query.QUERIES:
        # No exception is the assertion; a rejected shipped query would raise.
        reader.query(operation, {"owner": "o", "name": "r", "number": 1, "cursor": None})


def test_graphql_errors_are_reported_not_swallowed() -> None:
    def erroring(token, payload, *, timeout=60):
        return 200, {"errors": [{"message": "RATE_LIMITED"}]}

    try:
        _reader(erroring).query("queue_inventory", {"owner": "o", "name": "r", "cursor": None})
        raise AssertionError("GraphQL errors must raise")
    except github_query.InventoryError as exc:
        assert "queue_inventory" in str(exc)
        assert "RATE_LIMITED" in str(exc)


if __name__ == "__main__":
    failures = 0
    passed = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                passed += 1
            except Exception as exc:
                failures += 1
                import traceback
                traceback.print_exc()
                print(f"FAIL {name}: {exc}")
    print(f"{passed} passed, {failures} failed")
    sys.exit(1 if failures else 0)
