"""`etags`, `api_calls` and `mutations` — `code/P-09-github-adapter.md` §5.

This module is the only place in RQA that writes any of the three tables. The
read protocol (§5) is narrow and stated there: `etags` is read and written only
inside `transport.py`; `api_calls` is written after **every** call this adapter
makes to GitHub, successful or not, from response headers alone — never from an
estimate (RQA-FR-021, U-RESILIENCE-12); `mutations` is read before every write
for the shared discipline's dedupe check and written after (U-AUTHORITY-09's
retained deterministic-identifier mechanism, RQA-BR-007). P-05 reads `api_calls`
directly as a raw row scan; no P-09 function serves that read.

Nothing here ever sees a credential: rate-limit facts arrive as response
headers, and the `Authorization` header is never part of what a caller passes
in (`transport._credential()`'s return dies inside one HTTP call, §4).

**`mutations.state` vocabulary** (§5): `"pending"` — sent, not yet verified;
`"verified"` — sent and its mandatory post-check confirmed the effect;
`"completed"` — accepted with no separate post-check, or an idempotent no-op;
`"uncertain"` — refused before any send (`Stale`/`LeaseTaken`/read failure) or
failed in transport after dispatch. The shared write discipline treats exactly
`{"completed", "verified"}` as terminal for its dedupe check.
"""

from __future__ import annotations

import json
import sqlite3
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Protocol

__all__ = [
    "SCHEMA",
    "TERMINAL_STATES",
    "ApiCallStore",
    "EtagStore",
    "MutationRow",
    "MutationStore",
    "SqliteApiCallStore",
    "SqliteEtagStore",
    "SqliteMutationStore",
    "ensure_schema",
]

#: §5's DDL, with `IF NOT EXISTS` so the stores can be constructed against a
#: state directory that already has the tables (the `rqa.record.store` pattern).
SCHEMA = (
    """
    CREATE TABLE IF NOT EXISTS etags (
      cache_key   TEXT PRIMARY KEY,
      etag        TEXT NOT NULL,
      body        TEXT NOT NULL,
      link        TEXT,
      updated_at  TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS api_calls (
      id          INTEGER PRIMARY KEY AUTOINCREMENT,
      called_at   TEXT NOT NULL,
      transport   TEXT NOT NULL,
      operation   TEXT NOT NULL,
      status      INTEGER NOT NULL,
      resource    TEXT,
      rate_limit  INTEGER,
      remaining   INTEGER,
      used        INTEGER,
      reset_at    TEXT
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS mutations (
      client_mutation_id TEXT PRIMARY KEY,
      job_id      TEXT NOT NULL,
      kind        TEXT NOT NULL,
      state       TEXT NOT NULL,
      response    TEXT,
      created_at  TEXT NOT NULL,
      updated_at  TEXT NOT NULL
    )
    """,
)

#: The states the shared write discipline (§3 preamble) treats as "already
#: done": a later call with the same `client_mutation_id` returns the prior
#: `Mutation` without an HTTP call or a second `action` entry (§6, T3).
TERMINAL_STATES = frozenset({"completed", "verified"})


def ensure_schema(connection: sqlite3.Connection) -> None:
    """Create the three §5 tables when absent. Idempotent."""
    for statement in SCHEMA:
        connection.execute(statement)
    connection.commit()


# -- §5's Protocols, verbatim --------------------------------------------------


class EtagStore(Protocol):
    def get(self, cache_key: str) -> tuple[str, str, str | None] | None: ...  # (etag, body, link)
    def put(self, cache_key: str, etag: str, body: str, link: str | None) -> None: ...


class ApiCallStore(Protocol):
    def record(self, transport: str, operation: str, status: int, headers: Mapping[str, str]) -> None: ...
    # parses X-RateLimit-* from headers; inserts one row; never raises on a missing header


class MutationStore(Protocol):
    def find(self, client_mutation_id: str) -> "MutationRow | None": ...
    def put(self, row: "MutationRow") -> None: ...   # INSERT ... ON CONFLICT DO UPDATE


@dataclass(frozen=True)
class MutationRow:
    """One `mutations` row, exactly as it sits on disk (§5). Timestamps are the
    stored ISO-8601 UTC text; `response` is GitHub's own payload as JSON text,
    or None where no mutation was ever sent."""

    client_mutation_id: str
    job_id: str
    kind: str
    state: str
    response: str | None
    created_at: str
    updated_at: str


# -- SQLite implementations ------------------------------------------------------


def _utcnow_text() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


class SqliteEtagStore:
    """`etags` over one SQLite connection. Read and written only by
    `transport.py` (§5's read protocol)."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    def get(self, cache_key: str) -> tuple[str, str, str | None] | None:
        row = self._connection.execute(
            "SELECT etag, body, link FROM etags WHERE cache_key = ?", (cache_key,)
        ).fetchone()
        if row is None:
            return None
        return (row[0], row[1], row[2])

    def put(self, cache_key: str, etag: str, body: str, link: str | None) -> None:
        self._connection.execute(
            "INSERT INTO etags(cache_key, etag, body, link, updated_at)"
            " VALUES(?, ?, ?, ?, ?)"
            " ON CONFLICT(cache_key) DO UPDATE SET etag = excluded.etag,"
            " body = excluded.body, link = excluded.link,"
            " updated_at = excluded.updated_at",
            (cache_key, etag, body, link, _utcnow_text()),
        )
        self._connection.commit()


def _header(headers: Mapping[str, str], name: str) -> str | None:
    """Case-insensitive header lookup; None when absent."""
    for key, value in headers.items():
        if key.lower() == name.lower():
            return value
    return None


def _int_or_none(value: str | None) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except ValueError:
        return None


def _reset_iso(value: str | None) -> str | None:
    """`X-RateLimit-Reset` (epoch seconds) as ISO-8601 UTC text; None when the
    header is absent or malformed. Header-derived, never an estimate."""
    epoch = _int_or_none(value)
    if epoch is None:
        return None
    return datetime.fromtimestamp(epoch, tz=timezone.utc).isoformat()


class SqliteApiCallStore:
    """`api_calls` over one SQLite connection: measured consumption per call,
    parsed from `X-RateLimit-*` response headers (RQA-FR-021). A missing header
    is a NULL column, never an estimate and never an exception."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    def record(self, transport: str, operation: str, status: int, headers: Mapping[str, str]) -> None:
        self._connection.execute(
            "INSERT INTO api_calls(called_at, transport, operation, status,"
            " resource, rate_limit, remaining, used, reset_at)"
            " VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                _utcnow_text(),
                transport,
                operation,
                status,
                _header(headers, "X-RateLimit-Resource"),
                _int_or_none(_header(headers, "X-RateLimit-Limit")),
                _int_or_none(_header(headers, "X-RateLimit-Remaining")),
                _int_or_none(_header(headers, "X-RateLimit-Used")),
                _reset_iso(_header(headers, "X-RateLimit-Reset")),
            ),
        )
        self._connection.commit()


class SqliteMutationStore:
    """`mutations` over one SQLite connection: the adapter's only
    de-duplication boundary (§7's residual acknowledged there)."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    def find(self, client_mutation_id: str) -> "MutationRow | None":
        row = self._connection.execute(
            "SELECT client_mutation_id, job_id, kind, state, response,"
            " created_at, updated_at FROM mutations WHERE client_mutation_id = ?",
            (client_mutation_id,),
        ).fetchone()
        if row is None:
            return None
        return MutationRow(
            client_mutation_id=row[0],
            job_id=row[1],
            kind=row[2],
            state=row[3],
            response=row[4],
            created_at=row[5],
            updated_at=row[6],
        )

    def put(self, row: "MutationRow") -> None:
        self._connection.execute(
            "INSERT INTO mutations(client_mutation_id, job_id, kind, state,"
            " response, created_at, updated_at) VALUES(?, ?, ?, ?, ?, ?, ?)"
            " ON CONFLICT(client_mutation_id) DO UPDATE SET"
            " state = excluded.state, response = excluded.response,"
            " updated_at = excluded.updated_at",
            (
                row.client_mutation_id,
                row.job_id,
                row.kind,
                row.state,
                row.response,
                row.created_at,
                row.updated_at,
            ),
        )
        self._connection.commit()


def response_text(payload: object) -> str | None:
    """GitHub's payload as the JSON text the `response` column stores; None
    when no mutation was ever sent (§5's column comment)."""
    if payload is None:
        return None
    return json.dumps(payload, sort_keys=True)
