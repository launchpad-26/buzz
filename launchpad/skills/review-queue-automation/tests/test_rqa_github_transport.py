#!/usr/bin/env python3
"""The E-18 transport: ETag cache, Link pagination, measured `api_calls`, and
the no-live-network guard — `code/P-09-github-adapter.md` §4, §5, §8 rows T4,
T5, T10; U-DOCS-50, U-RESILIENCE-12, U-AUTHORITY-11, RQA-FR-021.

These tests run the REAL `Transport` against a scripted sender and the REAL
SQLite stores over `:memory:` connections — the cache and recording logic is
the unit under test. Only the HTTP exchange itself is faked.
"""

from __future__ import annotations

import pathlib
import sqlite3
import sys
from datetime import datetime, timezone

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from rqa.contracts import JobStatus  # noqa: E402
from rqa.github import GithubAdapter  # noqa: E402
from rqa.github.store import (  # noqa: E402
    SqliteApiCallStore,
    SqliteEtagStore,
    SqliteMutationStore,
    ensure_schema,
)
from rqa.github.testing import NON_TOKEN_CREDENTIAL, raising_socket  # noqa: E402
from rqa.github.transport import API_ROOT, Request, Response, Transport, Unavailable  # noqa: E402

_RATE_HEADERS = {
    "X-RateLimit-Resource": "core",
    "X-RateLimit-Limit": "5000",
    "X-RateLimit-Remaining": "4993",
    "X-RateLimit-Used": "7",
    "X-RateLimit-Reset": "1765000000",
}

_PAGE_ONE = f"{API_ROOT}/repos/octo/repo/items?per_page=50"
_PAGE_TWO = f"{API_ROOT}/repos/octo/repo/items?per_page=50&page=2"


class ScriptedSender:
    """Responses per URL, consumed in order (the last repeats)."""

    def __init__(self, script: dict):
        self.script = {url: list(responses) for url, responses in script.items()}
        self.requests: list[Request] = []

    def __call__(self, request: Request) -> Response:
        self.requests.append(request)
        queue = self.script[request.url]
        return queue.pop(0) if len(queue) > 1 else queue[0]


def fresh_transport(sender) -> tuple[Transport, sqlite3.Connection]:
    connection = sqlite3.connect(":memory:")
    ensure_schema(connection)
    transport = Transport(
        etags=SqliteEtagStore(connection),
        api_calls=SqliteApiCallStore(connection),
        send=sender,
        resolve_credential=lambda: NON_TOKEN_CREDENTIAL,
    )
    return transport, connection


def two_page_sender() -> ScriptedSender:
    return ScriptedSender(
        {
            _PAGE_ONE: [
                Response(
                    status=200,
                    headers={
                        "ETag": 'W/"etag-one"',
                        "Link": f'<{_PAGE_TWO}>; rel="next"',
                        **_RATE_HEADERS,
                    },
                    body="[1, 2]",
                ),
                Response(status=304, headers=_RATE_HEADERS, body=""),
            ],
            _PAGE_TWO: [
                Response(
                    status=200,
                    headers={"ETag": 'W/"etag-two"', **_RATE_HEADERS},
                    body="[3]",
                ),
                Response(status=304, headers=_RATE_HEADERS, body=""),
            ],
        }
    )


# -- T4 / U-DOCS-50: a 304 serves the cached body AND the cached Link ------------


def test_t4_full_two_page_walk_through_304s_uses_cached_body_and_link() -> None:
    sender = two_page_sender()
    transport, _ = fresh_transport(sender)

    first = transport.rest_paginated(_PAGE_ONE, operation="inventory", page_cap=5)
    assert first == [1, 2, 3]
    assert len(sender.requests) == 2

    second = transport.rest_paginated(_PAGE_ONE, operation="inventory", page_cap=5)
    assert second == [1, 2, 3]
    assert len(sender.requests) == 4
    # The revalidating requests carried the cached ETags...
    assert sender.requests[2].headers.get("If-None-Match") == 'W/"etag-one"'
    assert sender.requests[3].headers.get("If-None-Match") == 'W/"etag-two"'
    # ...and the 304 responses carried no body: the cache supplied it, and the
    # cached Link supplied page two (a 304 does not lose pagination).
    assert sender.requests[3].url == _PAGE_TWO


def test_a_304_without_a_cached_body_is_a_refusal_not_an_empty_page() -> None:
    sender = ScriptedSender({_PAGE_ONE: [Response(status=304, headers={}, body="")]})
    transport, _ = fresh_transport(sender)
    try:
        transport.rest_json(_PAGE_ONE, operation="inventory")
    except Unavailable as failure:
        assert failure.reason == "malformed" and failure.retriable is False
    else:
        raise AssertionError("expected Unavailable for 304 without cache")


def test_a_page_cap_overrun_refuses_rather_than_truncates() -> None:
    sender = two_page_sender()
    transport, _ = fresh_transport(sender)
    try:
        transport.rest_paginated(_PAGE_ONE, operation="inventory", page_cap=1)
    except Unavailable as failure:
        assert failure.reason == "page_cap_exceeded" and failure.retriable is False
    else:
        raise AssertionError("expected Unavailable for page-cap overrun")


# -- T5: api_calls rows are header-derived, never an estimate --------------------


def test_t5_every_call_records_one_header_derived_api_calls_row() -> None:
    sender = two_page_sender()
    graphql_url = "https://api.github.com/graphql"
    sender.script[graphql_url] = [
        Response(
            status=200,
            headers={"X-RateLimit-Resource": "graphql", "X-RateLimit-Limit": "5000",
                     "X-RateLimit-Remaining": "4999", "X-RateLimit-Used": "1",
                     "X-RateLimit-Reset": "1765000000"},
            body='{"data": {"viewer": {"login": "operator"}}}',
        )
    ]
    transport, connection = fresh_transport(sender)

    transport.rest_paginated(_PAGE_ONE, operation="inventory", page_cap=5)
    transport.rest_paginated(_PAGE_ONE, operation="inventory", page_cap=5)  # 304s
    transport.graphql("query{viewer{login}}", {}, operation="probe")

    rows = connection.execute(
        "SELECT transport, operation, status, resource, rate_limit, remaining,"
        " used, reset_at FROM api_calls ORDER BY id"
    ).fetchall()
    assert len(rows) == 5  # two fresh GETs, two 304s, one GraphQL POST
    expected_reset = datetime.fromtimestamp(1765000000, tz=timezone.utc).isoformat()
    for row in rows[:4]:
        assert row[0] == "rest" and row[1] == "inventory"
        assert row[3] == "core" and row[4] == 5000 and row[5] == 4993 and row[6] == 7
        assert row[7] == expected_reset
    assert rows[2][2] == 304 and rows[0][2] == 200
    assert rows[4][0] == "graphql" and rows[4][1] == "probe" and rows[4][3] == "graphql"


def test_t5_missing_rate_headers_record_null_never_an_estimate() -> None:
    url = f"{API_ROOT}/user"
    sender = ScriptedSender({url: [Response(status=200, headers={}, body='{"login": "x"}')]})
    transport, connection = fresh_transport(sender)
    transport.rest_json(url, operation="probe")
    row = connection.execute(
        "SELECT resource, rate_limit, remaining, used, reset_at FROM api_calls"
    ).fetchone()
    assert row == (None, None, None, None, None)


def test_the_credential_is_sent_per_call_and_never_persisted() -> None:
    sender = two_page_sender()
    transport, connection = fresh_transport(sender)
    transport.rest_paginated(_PAGE_ONE, operation="inventory", page_cap=5)
    for request in sender.requests:
        assert request.headers["Authorization"] == f"Bearer {NON_TOKEN_CREDENTIAL}"
    for table in ("etags", "api_calls", "mutations"):
        for row in connection.execute(f"SELECT * FROM {table}").fetchall():
            assert NON_TOKEN_CREDENTIAL not in str(row), table


def test_graphql_errors_surface_as_graphql_error_with_the_errors_attached() -> None:
    graphql_url = "https://api.github.com/graphql"
    sender = ScriptedSender(
        {graphql_url: [Response(status=200, headers={}, body='{"errors": [{"message": "boom"}]}')]}
    )
    transport, _ = fresh_transport(sender)
    try:
        transport.graphql("query{viewer{login}}", {}, operation="facts")
    except Unavailable as failure:
        assert failure.reason == "graphql_error" and failure.retriable is False
        assert failure.errors[0]["message"] == "boom"
    else:
        raise AssertionError("expected Unavailable for GraphQL errors")


def test_rate_limit_and_not_found_statuses_map_to_their_reasons() -> None:
    limited = f"{API_ROOT}/limited"
    missing = f"{API_ROOT}/missing"
    sender = ScriptedSender(
        {
            limited: [Response(status=403, headers={"X-RateLimit-Remaining": "0"}, body="")],
            missing: [Response(status=404, headers={}, body="")],
        }
    )
    transport, _ = fresh_transport(sender)
    try:
        transport.rest_json(limited, operation="checks")
    except Unavailable as failure:
        assert failure.reason == "rate_limited" and failure.retriable is True
    else:
        raise AssertionError("expected rate_limited")
    try:
        transport.rest_json(missing, operation="inventory")
    except Unavailable as failure:
        assert failure.reason == "not_found" and failure.retriable is False
    else:
        raise AssertionError("expected not_found")


# -- T10: NON_TOKEN_CREDENTIAL + raising_socket() --------------------------------


def test_t10_a_read_through_the_real_sender_cannot_complete_a_live_connection() -> None:
    from rqa.contracts import Job

    connection = sqlite3.connect(":memory:")
    ensure_schema(connection)
    transport = Transport(
        etags=SqliteEtagStore(connection),
        api_calls=SqliteApiCallStore(connection),
        # The REAL default sender: no injected fake. The socket guard is what
        # stops this test from authenticating anywhere.
        resolve_credential=lambda: NON_TOKEN_CREDENTIAL,
    )
    adapter = GithubAdapter(
        transport=transport,
        mutations=SqliteMutationStore(connection),
        clock=lambda: datetime.now(timezone.utc),
    )
    job = Job(
        id="job-1", repo="octo/repo", number=7, head_sha="H1", base_sha="B1",
        head_repo="octo/repo", head_ref="feature", predecessor_job=None,
        predecessor_head_sha=None, snapshot_hash=None, status=JobStatus.QUEUED,
    )
    with raising_socket():
        for name, read in (
            ("inventory", lambda: adapter.inventory(repo="octo/repo")),
            ("checks", lambda: adapter.checks(repo="octo/repo", sha="H1")),
            ("facts", lambda: adapter.facts(job=job, record=None)),
        ):
            try:
                read()
            except RuntimeError as error:
                assert "live network connection" in str(error), name
            else:
                raise AssertionError(f"{name}: expected the socket guard to fire")
    # No live connection completed: nothing was recorded from any response.
    assert connection.execute("SELECT COUNT(*) FROM api_calls").fetchone()[0] == 0
    assert connection.execute("SELECT COUNT(*) FROM etags").fetchone()[0] == 0
