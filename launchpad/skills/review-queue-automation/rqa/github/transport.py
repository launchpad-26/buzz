"""E-18 — the ONLY module in RQA that imports an HTTP client (`urllib.request`,
stdlib). `code/P-09-github-adapter.md` §1, §4, §5.

Owns this adapter's private credential resolution (`_credential()`, a
subprocess call to `gh auth token` — structurally identical to but independent
of P-08's E-22 read [ADR-E assumed, ADR-0062]), the ETag cache, paginated REST
GET, GraphQL POST, and rate-limit recording from response headers.

**Credential hygiene (§4, §7, U-DOCS-24).** The credential on every call is
resolved fresh, held in a local variable for the lifetime of one HTTP call, and
discarded. It is never stored on `Transport`, never written to `etags`,
`api_calls` or `mutations`, never logged, and never put into an exception's
`str()`. `probe()` (§3.4) is the one declared exception where the caller (P-08)
supplies the credential explicitly.

**Fail closed, refuse rather than truncate (U-AUTHORITY-10, U-AUTHORITY-11,
U-RESILIENCE-12).** A page-cap overrun is a refusal, never a silent truncation;
a 304 without a cached body is a defect, not an empty page; every REST GET is
ETag-cached with its Link header so a 304 does not lose pagination
(U-DOCS-50's kept behaviour); and one `api_calls` row is written after every
call, REST or GraphQL, successful or not, from response headers alone
(RQA-FR-021).

Availability failures raise `Unavailable`, a private control-flow signal the
§3 entry points catch and convert to the shared `GithubUnavailable` value; it
never crosses this package's boundary. A non-transport exception (for example
`testing.raising_socket()`'s guard) propagates untouched, so a suite that
regresses into a live call fails deterministically (§8 T10).
"""

from __future__ import annotations

import json
import subprocess
import urllib.error
import urllib.request
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field

from rqa.github.store import ApiCallStore, EtagStore

__all__ = [
    "ACCEPT_DIFF",
    "ACCEPT_JSON",
    "API_ROOT",
    "API_VERSION",
    "GRAPHQL_URL",
    "Request",
    "Response",
    "Transport",
    "Unavailable",
]

API_ROOT = "https://api.github.com"
GRAPHQL_URL = "https://api.github.com/graphql"
#: `X-GitHub-Api-Version`, pinned to a fixed value this file owns (§4).
API_VERSION = "2022-11-28"
ACCEPT_JSON = "application/vnd.github+json"
#: For the one diff-text read in §3.5.
ACCEPT_DIFF = "application/vnd.github.v3.diff"
_USER_AGENT = "review-queue-automation"
_TIMEOUT_SECONDS = 30
#: `\u0001` — the §5 `cache_key` separator for a non-default representation.
_CACHE_KEY_SEPARATOR = "\u0001"


class Unavailable(Exception):
    """Private transport-availability signal. Carries the fields the §3 entry
    points need to build a `GithubUnavailable` value; never neighbour-facing.
    `detail` never contains a credential or a request header."""

    def __init__(
        self,
        *,
        reason: str,
        retriable: bool,
        status: int | None = None,
        errors: tuple[Mapping, ...] = (),
        detail: str = "",
    ) -> None:
        super().__init__(detail or reason)
        self.reason = reason
        self.retriable = retriable
        self.status = status
        self.errors = errors
        self.detail = detail


@dataclass(frozen=True)
class Request:
    """One HTTP exchange as the injectable sender sees it."""

    method: str
    url: str
    headers: Mapping[str, str]
    body: bytes | None


@dataclass(frozen=True)
class Response:
    status: int
    headers: Mapping[str, str]
    body: str


def _credential() -> str:
    """This adapter's private, per-call credential resolution [ADR-E assumed]:
    a subprocess call to `gh auth token`. The return value is held by the one
    caller for the lifetime of one HTTP call and discarded — never stored,
    logged, or persisted (§4, ADR-0062 #4)."""
    try:
        completed = subprocess.run(
            ("gh", "auth", "token"),
            capture_output=True,
            text=True,
            check=False,
            timeout=_TIMEOUT_SECONDS,
        )
    except (OSError, subprocess.SubprocessError) as error:
        raise Unavailable(
            reason="unauthenticated",
            retriable=False,
            detail="gh auth token could not be run",
        ) from error
    token = completed.stdout.strip()
    if completed.returncode != 0 or not token:
        raise Unavailable(
            reason="unauthenticated",
            retriable=False,
            detail="gh auth token returned no credential",
        )
    return token


def _urllib_send(request: Request) -> Response:
    """The default sender: one real HTTPS exchange. An HTTP error status is a
    `Response`, not an exception; a connection-level failure raises `OSError`
    (converted to `Unavailable(reason="unreachable")` by the caller)."""
    prepared = urllib.request.Request(
        request.url,
        data=request.body,
        headers=dict(request.headers),
        method=request.method,
    )
    try:
        with urllib.request.urlopen(prepared, timeout=_TIMEOUT_SECONDS) as response:
            return Response(
                status=response.status,
                headers=dict(response.headers.items()),
                body=response.read().decode("utf-8", errors="replace"),
            )
    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")
        return Response(status=error.code, headers=dict(error.headers.items()), body=body)


def _next_link(link_header: str | None) -> str | None:
    """The `rel="next"` URL out of a Link header, or None."""
    for entry in (link_header or "").split(","):
        if 'rel="next"' in entry:
            start = entry.find("<")
            end = entry.find(">")
            if 0 <= start < end:
                return entry[start + 1 : end]
    return None


def _rate_limited(response: Response) -> bool:
    remaining = _header_value(response.headers, "X-RateLimit-Remaining")
    return response.status == 429 or (response.status == 403 and remaining == "0")


def _header_value(headers: Mapping[str, str], name: str) -> str | None:
    for key, value in headers.items():
        if key.lower() == name.lower():
            return value
    return None


def _status_unavailable(response: Response, *, operation: str) -> Unavailable:
    """Map a non-success HTTP status to the availability vocabulary. The body
    is deliberately not echoed into `detail`."""
    if response.status == 401:
        return Unavailable(reason="unauthenticated", retriable=False, status=401)
    if _rate_limited(response):
        return Unavailable(reason="rate_limited", retriable=True, status=response.status)
    if response.status in (403, 404, 410):
        return Unavailable(reason="not_found", retriable=False, status=response.status)
    return Unavailable(
        reason="unreachable",
        retriable=True,
        status=response.status,
        detail=f"{operation}: HTTP {response.status}",
    )


@dataclass(frozen=True)
class Transport:
    """The adapter's one seam to GitHub. `send` and `resolve_credential` are
    injectable so every test runs against fixture responses and a non-token
    credential — no live connection, ever (§8's preamble, T10)."""

    etags: EtagStore
    api_calls: ApiCallStore
    send: Callable[[Request], Response] = _urllib_send
    resolve_credential: Callable[[], str] = field(default=_credential)

    # -- private ---------------------------------------------------------------

    def _headers(self, *, accept: str, credential: str | None, etag: str | None) -> dict[str, str]:
        token = credential if credential is not None else self.resolve_credential()
        headers = {
            "Accept": accept,
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": API_VERSION,
            "User-Agent": _USER_AGENT,
        }
        if etag:
            headers["If-None-Match"] = etag
        return headers

    def _exchange(self, request: Request, *, kind: str, operation: str) -> Response:
        """One send, with its mandatory `api_calls` row (§5): written after
        every completed exchange, successful or not, from response headers
        alone. A connection-level failure produced no response and therefore
        no headers to record."""
        try:
            response = self.send(request)
        except (OSError, TimeoutError) as error:
            raise Unavailable(
                reason="unreachable",
                retriable=True,
                detail=f"{operation}: connection failed",
            ) from error
        self.api_calls.record(kind, operation, response.status, response.headers)
        return response

    def _get_one(
        self, url: str, *, operation: str, accept: str, credential: str | None
    ) -> tuple[str, str | None]:
        """One ETag-cached REST GET: `(body_text, link_header)`. Read the cache
        before every GET; write it after every fresh (non-304) `ETag` (§5)."""
        cache_key = url if accept == ACCEPT_JSON else f"{url}{_CACHE_KEY_SEPARATOR}{accept}"
        cached = self.etags.get(cache_key)
        request = Request(
            method="GET",
            url=url,
            headers=self._headers(
                accept=accept,
                credential=credential,
                etag=cached[0] if cached else None,
            ),
            body=None,
        )
        response = self._exchange(request, kind="rest", operation=operation)
        if response.status == 304:
            if cached is None:
                raise Unavailable(
                    reason="malformed",
                    retriable=False,
                    status=304,
                    detail=f"{operation}: 304 without a cached body",
                )
            return cached[1], cached[2]
        if response.status != 200:
            raise _status_unavailable(response, operation=operation)
        etag = _header_value(response.headers, "ETag")
        link = _header_value(response.headers, "Link")
        if etag:
            self.etags.put(cache_key, etag, response.body, link)
        return response.body, link

    # -- REST ------------------------------------------------------------------

    def rest_json(self, path: str, *, operation: str, credential: str | None = None) -> object:
        """One REST GET, parsed. `path` is `/`-rooted or a full pagination URL."""
        url = path if path.startswith("https://") else f"{API_ROOT}{path}"
        body, _ = self._get_one(url, operation=operation, accept=ACCEPT_JSON, credential=credential)
        try:
            return json.loads(body)
        except ValueError as error:
            raise Unavailable(
                reason="malformed",
                retriable=False,
                detail=f"{operation}: response is not JSON",
            ) from error

    def rest_text(
        self, path: str, *, operation: str, accept: str, credential: str | None = None
    ) -> str:
        """One REST GET returned verbatim — the §3.5 diff-text read."""
        url = path if path.startswith("https://") else f"{API_ROOT}{path}"
        body, _ = self._get_one(url, operation=operation, accept=accept, credential=credential)
        return body

    def rest_paginated(
        self,
        path: str,
        *,
        operation: str,
        page_cap: int,
        item_key: str | None = None,
        credential: str | None = None,
    ) -> list:
        """Walk `rel="next"` Link pagination, refusing past `page_cap` pages
        rather than returning a partial result (U-AUTHORITY-10). `item_key`
        collects list items out of object-shaped pages (`check_runs`)."""
        url = path if path.startswith("https://") else f"{API_ROOT}{path}"
        items: list = []
        for _ in range(page_cap):
            body, link = self._get_one(
                url, operation=operation, accept=ACCEPT_JSON, credential=credential
            )
            try:
                payload = json.loads(body)
            except ValueError as error:
                raise Unavailable(
                    reason="malformed",
                    retriable=False,
                    detail=f"{operation}: response is not JSON",
                ) from error
            if item_key is not None:
                payload = payload.get(item_key) if isinstance(payload, Mapping) else None
            if not isinstance(payload, list):
                raise Unavailable(
                    reason="malformed",
                    retriable=False,
                    detail=f"{operation}: paginated response is not a list",
                )
            items.extend(payload)
            next_url = _next_link(link)
            if next_url is None:
                return items
            url = next_url
        raise Unavailable(
            reason="page_cap_exceeded",
            retriable=False,
            detail=f"{operation}: more than {page_cap} pages",
        )

    # -- GraphQL -----------------------------------------------------------------

    def _post_graphql(
        self, document: str, variables: Mapping, *, operation: str, credential: str | None
    ) -> Mapping:
        body = json.dumps({"query": document, "variables": dict(variables)}).encode("utf-8")
        request = Request(
            method="POST",
            url=GRAPHQL_URL,
            headers=self._headers(accept=ACCEPT_JSON, credential=credential, etag=None),
            body=body,
        )
        response = self._exchange(request, kind="graphql", operation=operation)
        if response.status != 200:
            raise _status_unavailable(response, operation=operation)
        try:
            payload = json.loads(response.body)
        except ValueError as error:
            raise Unavailable(
                reason="malformed",
                retriable=False,
                detail=f"{operation}: response is not JSON",
            ) from error
        errors = payload.get("errors") or []
        if errors:
            raise Unavailable(
                reason="graphql_error",
                retriable=False,
                errors=tuple(errors),
                detail=f"{operation}: GraphQL reported {len(errors)} error(s)",
            )
        data = payload.get("data")
        if not isinstance(data, Mapping):
            raise Unavailable(
                reason="malformed",
                retriable=False,
                detail=f"{operation}: GraphQL response has no data object",
            )
        return data

    def graphql(
        self, document: str, variables: Mapping, *, operation: str, credential: str | None = None
    ) -> Mapping:
        """One GraphQL read. Refuses a mutation document: writes go through
        `mutate` so a read-only caller provably cannot write (§8 T9)."""
        if document.lstrip().startswith("mutation"):
            raise ValueError("graphql() is read-only; use mutate() for a mutation")
        return self._post_graphql(document, variables, operation=operation, credential=credential)

    def mutate(
        self, document: str, variables: Mapping, *, operation: str, credential: str | None = None
    ) -> Mapping:
        """One GraphQL mutation — the adapter's only write path to GitHub."""
        if not document.lstrip().startswith("mutation"):
            raise ValueError("mutate() sends mutations only")
        return self._post_graphql(document, variables, operation=operation, credential=credential)

