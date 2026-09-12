"""The `capabilities` table — `code/P-08-authority-gate.md` §5, `container.md` §5's
`capabilities` row.

`CapabilityStore` is declared **here**, not in `rqa/edges.py`: `CONTRACTS.md` §9 names
it in E-04's signature and `rqa.edges` keeps it an empty Protocol whose docstring says
its shape is P-08's to state. This is that statement, and it is the same arrangement
`rqa/policy/store.py` makes for `SnapshotStore`.

**Written only by P-08.** P-02 reads it — read-only, through `current()` — so an
escalation can carry the proof that refused the activity. Nothing else in RQA touches
these rows.

**One proof per `(repo, job_id)`, and it never commits.** The row is written on the
caller's own connection and left uncommitted, so the proof, the `attestation` entry that
describes it and the `grant` entry that used it become durable together or not at all —
the same discipline `rqa/record/writer.py` keeps for E-13. A re-probe of the same
`(repo, job_id)` replaces the row in place (§5's "UNIQUE violation → replace") rather
than accumulating a second answer for one job: the per-job proof is one fact, and two
rows would leave a reader to guess which one the grant used.

**No credential column, and no credential anywhere.** §5's seven columns are the whole
table; the token that produced the reading is not one of them and is never written here
(RQA-NFR-025).
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from typing import Protocol

from rqa.authority.capability import CapabilityProof

__all__ = ["CapabilityStore", "SqliteCapabilityStore", "ensure_schema"]

_SCHEMA = """
CREATE TABLE IF NOT EXISTS capabilities (
  id            INTEGER PRIMARY KEY,
  repo          TEXT NOT NULL,
  job_id        TEXT NOT NULL,
  capabilities  TEXT NOT NULL,
  attested      TEXT NOT NULL,
  login         TEXT NOT NULL,
  probed_at     TEXT NOT NULL,
  UNIQUE (repo, job_id)
);
"""


class CapabilityStore(Protocol):
    def current(self, repo: str, job_id: str) -> CapabilityProof | None: ...
    def put(self, proof: CapabilityProof) -> int: ...  # returns id; UNIQUE violation → replace


def ensure_schema(*, connection: sqlite3.Connection) -> None:
    """§5's DDL, idempotent. Run from the constructor so no DDL runs inside the
    transaction a `put` joins."""
    connection.execute(_SCHEMA)


def _stamp(moment: datetime) -> str:
    """ISO-8601 UTC. A naive reading is taken as UTC rather than as local time: a
    timestamp that means something different on each machine is not a proof anyone can
    reproduce."""
    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=timezone.utc)
    return moment.astimezone(timezone.utc).isoformat()


class SqliteCapabilityStore:
    """`CapabilityStore` over one caller-owned `sqlite3.Connection`.

    `connection` is a constructor-only dependency; it is not a §5 method parameter.
    """

    def __init__(self, connection: sqlite3.Connection):
        self.connection = connection
        ensure_schema(connection=connection)

    def current(self, repo: str, job_id: str) -> CapabilityProof | None:
        row = self.connection.execute(
            "SELECT id, capabilities, attested, login, probed_at FROM capabilities "
            "WHERE repo = ? AND job_id = ?",
            (repo, job_id),
        ).fetchone()
        if row is None:
            return None
        identifier, capabilities, attested, login, probed_at = row
        return CapabilityProof(
            id=identifier,
            repo=repo,
            job_id=job_id,
            capabilities=frozenset(json.loads(capabilities)),
            login=login,
            probed_at=datetime.fromisoformat(probed_at),
            attested_not_proven=frozenset(json.loads(attested)),
        )

    def put(self, proof: CapabilityProof) -> int:
        """Insert or replace this job's proof for this repository and return its id.

        The sets are stored sorted so two identical readings produce identical bytes —
        a row a reader can compare, and a `json.loads` a reader can round-trip.
        """
        self.connection.execute(
            "INSERT INTO capabilities (repo, job_id, capabilities, attested, login, probed_at) "
            "VALUES (?, ?, ?, ?, ?, ?) "
            "ON CONFLICT (repo, job_id) DO UPDATE SET "
            "capabilities = excluded.capabilities, attested = excluded.attested, "
            "login = excluded.login, probed_at = excluded.probed_at",
            (
                proof.repo,
                proof.job_id,
                json.dumps(sorted(proof.capabilities)),
                json.dumps(sorted(proof.attested_not_proven)),
                proof.login,
                _stamp(proof.probed_at),
            ),
        )
        row = self.connection.execute(
            "SELECT id FROM capabilities WHERE repo = ? AND job_id = ?",
            (proof.repo, proof.job_id),
        ).fetchone()
        return int(row[0])
