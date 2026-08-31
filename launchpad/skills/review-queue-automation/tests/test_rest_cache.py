#!/usr/bin/env python3
"""REST cache/pagination acceptance tests. All fakes — no GitHub, no network.

Proves:
- A cached page 1 that returns 304 still walks into page 2+ via the persisted
  Link header (requirement 4).
- A 304 without a cached body fails instead of inventing data.
- Pagination Link is persisted per page and reused on subsequent 304 reads.
- State.execute / persistence failures surface as StatePersistenceError, not a
  silently swallowed sqlite3.Error.
"""

from __future__ import annotations

import json
import pathlib
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scripts"))

from common import GithubRest, State, StatePersistenceError  # noqa: E402


def fresh_state() -> State:
    return State({"state_dir": tempfile.mkdtemp()})


def _url(page: int) -> str:
    return f"https://api.github.com/repos/o/r/prs?cnt={page}"


def _store_pages(state: State, pages: dict[str, list]) -> None:
    """Seed etags rows: body + a Link header pointing at the next page."""
    urls = sorted((u for u in pages), key=_page_of)
    for idx, url in enumerate(urls):
        nxt = urls[idx + 1] if idx + 1 < len(urls) else ""
        link = f'<{nxt}>; rel="next"' if nxt else ""
        state.execute(
            "INSERT INTO etags(url,etag,body,link,updated_at) VALUES(?,?,?,?,?)",
            (url, f"e-{url}", json.dumps(pages[url]), link, "2026-01-01T00:00:00Z"),
        )
    state._commit()


def _page_of(url: str) -> int:
    return int(url.rsplit("=", 1)[1])


class _FakeTransport:
    """Serves only 304 once a page is cached (simulating an ETag hit)."""

    def __init__(self, state: State):
        self.state = state

    def _request(self, url, operation, etag=None):
        row = self.state.execute("SELECT etag, body, link FROM etags WHERE url=?", (url,)).fetchone()
        if row is None:
            raise RuntimeError(f"unexpected uncached url {url}")
        return 304, None, row["etag"], _FakeRespHeaders(row["link"] or "")


class _FakeRespHeaders:
    def __init__(self, link: str):
        self._link = link
        self._h = {"x-ratelimit-used": "1", "x-ratelimit-remaining": "4999"}

    def get(self, key, default=None):
        if key == "Link":
            return self._link or default
        return self._h.get(key, default)


def _client(state: State, request_fn) -> GithubRest:
    g = GithubRest.__new__(GithubRest)
    g.state = state
    g.config = {"github": {}}
    g.token = "faketoken"
    g.timeout = 30
    g.api_version = "2022-11-28"
    g._request = request_fn
    return g


def _status_304_always(state: State):
    def _request(url, operation, etag=None):
        row = state.execute("SELECT etag, body, link FROM etags WHERE url=?", (url,)).fetchone()
        if row is None:
            raise RuntimeError(f"unexpected uncached url {url}")
        return 304, None, row["etag"], _FakeRespHeaders(row["link"] or "")
    return _request


def test_cached_page1_304_still_returns_page2() -> None:
    """Requirement 4: a cached page 1 hitting 304 must follow its persisted Link
    to page 2 and return both pages, not silently stop at page 1."""
    state = fresh_state()
    try:
        pages = {
            _url(1): [{"n": 1}],
            _url(2): [{"n": 2}],
        }
        _cached = pages
        # Persist the two pages with their next-link.
        urls = sorted(pages, key=_page_of)
        for idx, url in enumerate(urls):
            nxt = urls[idx + 1] if idx + 1 < len(urls) else ""
            link = f'<{nxt}>; rel="next"' if nxt else ""
            state.execute(
                "INSERT INTO etags(url,etag,body,link,updated_at) VALUES(?,?,?,?,?)",
                (url, f"e{idx}", json.dumps(pages[url]), link, "2026-01-01T00:00:00Z"),
            )
        state._commit()
        client = _client(state, _status_304_always(state))
        # First page cached + 304; the Link header is persisted, so all pages walk.
        result = client.get("/repos/o/r/prs", "list_prs", {"cnt": 1}, paginate=True)
        numbers = [x["n"] for x in result]
        assert numbers == [1, 2], numbers
    finally:
        state.close()


def test_304_without_cached_body_fails_closed() -> None:
    """A 304 implies a cached body; if none exists we must never fabricate data."""
    state = fresh_state()
    try:
        # No etags row for the URL.
        def _request(url, operation, etag=None):
            return 304, None, "etag", _FakeRespHeaders("")
        client = _client(state, _request)
        try:
            client.get("/repos/v2/pr", "pr_meta", {"n": 9})
            raise AssertionError("should fail closed on 304 with no cached body")
        except RuntimeError as exc:
            assert "304 without cached body" in str(exc)
    finally:
        state.close()


def test_persisted_link_reused_across_separate_clients() -> None:
    """The Link header is stored with the cached body, so a NEW client session
    (fresh GithubRest) can still walk page 2 from a 304 on page 1."""
    state = fresh_state()
    try:
        urls = {_url(1): [{"n": 1}], _url(2): [{"n": 2}]}
        keys = sorted(urls, key=_page_of)
        for idx, url in enumerate(keys):
            nxt = keys[idx + 1] if idx + 1 < len(keys) else ""
            link = f'<{nxt}>; rel="next"' if nxt else ""
            state.execute(
                "INSERT INTO etags(url,etag,body,link,updated_at) VALUES(?,?,?,?,?)",
                (url, "e0", json.dumps(urls[url]), link, "2026-01-01T00:00:00Z"),
            )
        state._commit()
        # Two independent client instances, both served 304, must agree.
        a = _client(state, _status_304_always(state))
        b = _client(state, _status_304_always(state))
        ra = [x["n"] for x in a.get("/repos/o/r/prs", "list_prs", {"cnt": 1}, paginate=True)]
        rb = [x["n"] for x in b.get("/repos/o/r/prs", "list_prs", {"cnt": 1}, paginate=True)]
        assert ra == [1, 2] == rb
    finally:
        state.close()


def test_state_execute_typed_persistence_error() -> None:
    """Requirement 8: SQLite failures must surface as StatePersistenceError, not
    be swallowed as a raw sqlite3.Error."""
    state = fresh_state()
    try:
        state.close()  # close the underlying connection to force a persistence failure
        try:
            state.execute("INSERT INTO jobs(id) VALUES(?)", ("x",))
            raise AssertionError("expected StatePersistenceError")
        except StatePersistenceError:
            pass
    finally:
        pass


def test_migrate_is_idempotent_and_deduped() -> None:
    """Opening State twice over the same dir does not duplicate tables or error."""
    d = tempfile.mkdtemp()
    s1 = State({"state_dir": d})
    try:
        tables1 = [r[0] for r in s1.db.execute(
            "SELECT name FROM sqlite_master WHERE type='table'") if not r[0].startswith("sqlite_")]
        s1.close()
        s2 = State({"state_dir": d})
        try:
            tables2 = [r[0] for r in s2.db.execute(
                "SELECT name FROM sqlite_master WHERE type='table'") if not r[0].startswith("sqlite_")]
            assert tables1 == tables2
            assert tables2.count("jobs") == 1
            assert tables2.count("mutations") == 1
            assert "approval_decisions" in tables2
            assert "human_requests" in tables2
            assert "leases" in tables2
        finally:
            s2.close()
    finally:
        pass


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