"""The snapshot store — `code/P-03-policy.md` §5, `container.md` §5's `snapshots` row.

The `snapshots` SQLite table plus `snapshots/<hash>.json` under the state directory,
atomic activation, and last-known-good retention (U-QUEUE-09, U-QUEUE-10). This is
the only module in RQA that writes them.

`SnapshotStore` is declared **here**, not in `rqa/edges.py`: `CONTRACTS.md` §9 names
it in E-03's signature and `rqa.edges` keeps it an empty Protocol whose docstring
says its shape is P-03's to state. This is that statement.

**Last-known-good retention.** No snapshot file or row is ever deleted, updated in
place, or superseded by activating a different hash. A job pinned to an older hash
keeps reading it, unaffected by every activation after it, for the life of the state
directory. Retention is *not* a fallback: an invalid config is a `ValidationFailure`,
never a quiet re-serve of an earlier snapshot (`code/P-03-policy.md` §7).

**Archive before pointer.** The archive file is written, flushed and fsynced into
place before the row that references it exists. An interruption between the two
leaves a complete, correctly-hashed archive and no row, and the next activation of
the same config re-runs a no-op rewrite of identical bytes and completes the insert
(§8 T13). The reverse order would leave a row pointing at nothing.
"""

from __future__ import annotations

import hashlib
import json
import os
import sqlite3
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Protocol

from rqa.contracts import Snapshot
from rqa.policy.snapshot import (
    canonical_bytes,
    snapshot_from_unverified_config,
    snapshot_from_verified_archive,
)
from rqa.policy.types import SnapshotStoreCorrupted
from rqa.protocol import protocol_hash

__all__ = ["StoredSnapshot", "SnapshotStore", "SqliteSnapshotStore", "ARCHIVE_DIR_NAME"]

#: Relative to the state directory, per `container.md` §5's `snapshots` row.
ARCHIVE_DIR_NAME = "snapshots"
_DB_FILENAME = "state.db"

_SCHEMA = """
CREATE TABLE IF NOT EXISTS snapshots (
  hash            TEXT PRIMARY KEY,
  repo            TEXT NOT NULL,
  policy_version  TEXT NOT NULL,
  protocol_hash   TEXT NOT NULL,
  activated_at    TEXT NOT NULL,
  path            TEXT NOT NULL
)
"""


@dataclass(frozen=True)
class StoredSnapshot:
    snapshot: Snapshot  # repo is a placeholder ("") here; snapshot_for() rebuilds it with
    #                     the caller's own repo before returning
    activated_at: datetime


class SnapshotStore(Protocol):
    def get(self, hash: str) -> StoredSnapshot | None: ...
    def activate(self, hash: str, raw: Mapping[str, Any], at: datetime) -> StoredSnapshot: ...


class SqliteSnapshotStore:
    """`SnapshotStore` over a state directory: `state.db` plus `snapshots/<hash>.json`.

    The digest is content-addressed and carries no repository, so two repositories
    with byte-identical configurations share one archive and one row — which is
    exactly what makes "reproduce what this job ran under" a property of the hash
    alone.

    The `snapshots.repo` column is written as `""`. §5 fixes `activate(hash, raw, at)`
    with no repository argument and documents the column as "informational, not a
    key", so the store genuinely never learns a repo; `snapshot_for` puts the
    caller's own `repo` on the `Snapshot` it returns. Nothing reads the column.
    """

    def __init__(self, state_dir: str | os.PathLike[str]):
        self.state_dir = Path(state_dir)
        self.archive_dir = self.state_dir / ARCHIVE_DIR_NAME
        self.db_path = self.state_dir / _DB_FILENAME

    # -- read ------------------------------------------------------------------

    def get(self, hash: str) -> StoredSnapshot | None:
        """The stored snapshot for `hash`, or `None` when no row exists.

        Recomputes SHA-256 over the archived file's own bytes and raises
        `SnapshotStoreCorrupted` on a mismatch: bytes that cannot be trusted are not
        a policy answer, they are a data-integrity fault.
        """
        row = self._row(hash)
        if row is None:
            return None
        policy_version, protocol, activated_at, relative_path = row
        archive = self.state_dir / relative_path
        try:
            body = archive.read_bytes()
        except OSError as exc:
            raise SnapshotStoreCorrupted(
                f"snapshot {hash} has a row but its archive {archive} is unreadable: {exc}"
            ) from exc
        if hashlib.sha256(body).hexdigest() != hash:
            raise SnapshotStoreCorrupted(
                f"archived snapshot {archive} no longer hashes to its own name {hash}"
            )
        try:
            raw = json.loads(body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise SnapshotStoreCorrupted(
                f"archived snapshot {archive} is not the JSON it was written as: {exc}"
            ) from exc
        # Entitled to the relaxed rebuild: the bytes just re-hashed to their own name.
        snapshot = snapshot_from_verified_archive(
            raw=raw, digest=hash, repo="", protocol=protocol
        )
        if snapshot.policy.version != policy_version:
            raise SnapshotStoreCorrupted(
                f"snapshot {hash} row records policy_version {policy_version!r} but its archive "
                f"carries {snapshot.policy.version!r}"
            )
        return StoredSnapshot(snapshot=snapshot, activated_at=datetime.fromisoformat(activated_at))

    # -- write -----------------------------------------------------------------

    def activate(
        self, hash: str, raw: Mapping[str, Any], at: datetime
    ) -> StoredSnapshot:
        """Archive `raw` under `hash` and insert its row, atomically and idempotently.

        A `hash` already archived — by this repository or, since the hash carries no
        repo, by any other with byte-identical content — is returned unchanged and
        nothing is written twice.

        **This method validates `raw` itself, in full, before it writes anything** —
        `MECHANICAL_TOOL_SET` membership included — and raises `PolicyError` rather
        than archiving a config it will not vouch for. It does not rely on its caller
        having validated, even though `snapshot_for` always has by §3 step 3: §4
        checks the same membership on three sides of a remediation decision because no
        single check may be trusted alone, and a store is not exempt from that.
        Unlike `get`, there is no hash-verified read-back here to stand in as proof.
        """
        existing = self.get(hash)
        if existing is not None:
            return existing

        body = canonical_bytes(raw)
        if hashlib.sha256(body).hexdigest() != hash:
            raise SnapshotStoreCorrupted(
                f"refusing to archive config under {hash}: its canonical bytes hash to "
                f"{hashlib.sha256(body).hexdigest()}"
            )
        # The write path: `raw` is caller-supplied with no hash-verified read-back
        # behind it, so the full validator runs — `MECHANICAL_TOOL_SET` membership
        # included — and it runs *before* anything is written, so a config this store
        # will not vouch for is never archived under a hash that then serves it
        # forever. `get`'s relaxed rebuild is a different function on purpose; the two
        # entry points take no flag, so neither call site can drift into the other's.
        snapshot = snapshot_from_unverified_config(
            raw=raw, digest=hash, repo="", protocol=protocol_hash()
        )
        self._archive(hash, body)
        self._insert_row(
            hash=hash,
            policy_version=snapshot.policy.version,
            protocol=snapshot.protocol_hash,
            at=at,
        )
        return StoredSnapshot(snapshot=snapshot, activated_at=at)

    # -- mechanics -------------------------------------------------------------

    def _archive(self, hash: str, body: bytes) -> None:
        """U-RESILIENCE-14's mechanism: same-directory temp file, flush, fsync, then
        an atomic rename onto `snapshots/<hash>.json`. A reader therefore sees either
        no file or the whole file, never a truncated one."""
        self.archive_dir.mkdir(parents=True, exist_ok=True)
        target = self.archive_dir / f"{hash}.json"
        temporary = self.archive_dir / f"{hash}.json.tmp"
        try:
            with open(temporary, "wb") as handle:
                handle.write(body)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary, target)
        except OSError:
            temporary.unlink(missing_ok=True)
            raise
        directory = os.open(self.archive_dir, os.O_RDONLY)
        try:
            os.fsync(directory)
        except OSError:
            # Some filesystems refuse to fsync a directory. The rename is already
            # atomic; only its durability across a power loss is weaker here, and
            # a lost rename is re-done by the next activation of the same config.
            pass
        finally:
            os.close(directory)

    def _insert_row(self, *, hash: str, policy_version: str, protocol: str, at: datetime) -> None:
        """The pointer, inserted only once the archive exists complete-or-not-at-all.

        `OR IGNORE` because the row is content-addressed: a concurrent activation of
        byte-identical bytes writes the identical row, so losing the race is not an
        error. Nothing here ever updates an existing row — that is what makes a pin
        readable for the life of the state directory.
        """
        connection = self._connect()
        try:
            with connection:
                connection.execute(
                    "INSERT OR IGNORE INTO snapshots "
                    "(hash, repo, policy_version, protocol_hash, activated_at, path) "
                    "VALUES (?, ?, ?, ?, ?, ?)",
                    (
                        hash,
                        "",
                        policy_version,
                        protocol,
                        at.isoformat(),
                        f"{ARCHIVE_DIR_NAME}/{hash}.json",
                    ),
                )
        finally:
            connection.close()

    def _row(self, hash: str) -> tuple[str, str, str, str] | None:
        connection = self._connect()
        try:
            cursor = connection.execute(
                "SELECT policy_version, protocol_hash, activated_at, path "
                "FROM snapshots WHERE hash = ?",
                (hash,),
            )
            row = cursor.fetchone()
        finally:
            connection.close()
        return tuple(row) if row is not None else None

    def _connect(self) -> sqlite3.Connection:
        self.state_dir.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(self.db_path)
        connection.execute(_SCHEMA)
        connection.commit()
        return connection
