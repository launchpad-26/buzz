"""`SQLiteRecordReader` — `code/P-12-record.md` §2 and §5's read protocol.

Ordered, side-effect-free reads over one job's rows, plus the one method that makes a
trust claim.

**`entries` and `latest` make no trust claim at all.** They return what is stored, in
sequence order, including rows a `verify` walk would have stopped at and including
migrated rows. That is deliberate and it is why `trusted_prefix` exists: §2 —
"Operational consumers such as P-13 must use this method rather than treating
`latest()` as authenticated."

`trusted_prefix` runs `verify` with this reader's key store and converts its outcome
into `CONTRACTS.md` §7's vocabulary: no rows is `MISSING`, a chain or HMAC break is
`INTEGRITY_BREAK`, any `unverifiable: no key` segment is `UNVERIFIABLE`, and any
migrated row is `LEGACY`. Only a complete, chain-valid, key-authenticated, non-legacy
history returns a `VerifiedRecordPrefix`, whose `latest(kind)` searches its own
immutable rows and nothing else.
"""

from __future__ import annotations

import sqlite3

from rqa.contracts import (
    EntryKind,
    KeyStore,
    RecordRow,
    RecordTrustFailureReason,
    RecordUntrusted,
    VerifiedRecordPrefix,
)
from rqa.record.keychain import OSKeyStore
from rqa.record.store import (
    entries_for_job,
    entries_of_kind,
    is_legacy,
    latest_of_kind,
    record_row,
)
from rqa.record.verify import verify

__all__ = ["SQLiteRecordReader"]


class SQLiteRecordReader:
    """Immutable record reader. Basic reads make no trust claim."""

    def __init__(self, connection: sqlite3.Connection, *, keystore: KeyStore = OSKeyStore()):
        self._connection = connection
        self._keystore = keystore

    def entries(self, job_id: str, kind: EntryKind | None = None) -> tuple[RecordRow, ...]:
        """Every row for `job_id`, in sequence order; one kind when `kind` is given."""
        stored = (
            entries_for_job(connection=self._connection, job=job_id)
            if kind is None
            else entries_of_kind(connection=self._connection, job=job_id, kind=kind)
        )
        return tuple(record_row(entry=entry) for entry in stored)

    def latest(self, job_id: str, kind: EntryKind) -> RecordRow | None:
        """The greatest-`seq` row of `kind` for `job_id`, or `None`.

        Unauthenticated by construction — see the module docstring.
        """
        entry = latest_of_kind(connection=self._connection, job=job_id, kind=kind)
        return None if entry is None else record_row(entry=entry)

    def trusted_prefix(self, job_id: str) -> VerifiedRecordPrefix | RecordUntrusted:
        """The job's verified history, or the one reason it cannot be trusted (§2)."""
        stored = entries_for_job(connection=self._connection, job=job_id)
        if not stored:
            return RecordUntrusted(
                reason=RecordTrustFailureReason.MISSING,
                detail=f"no record entries for job {job_id!r}",
            )
        result = verify(self._connection, job_id, keystore=self._keystore)
        if not result.ok:
            return RecordUntrusted(
                reason=RecordTrustFailureReason.INTEGRITY_BREAK,
                detail=(
                    f"{result.kind.value if result.kind else 'break'} at seq {result.bad_seq}"
                ),
            )
        if result.unverifiable:
            first = result.unverifiable[0]
            return RecordUntrusted(
                reason=RecordTrustFailureReason.UNVERIFIABLE,
                detail=(
                    f"unverifiable: {first.reason} over seq {first.first_seq}-{first.last_seq}"
                    f" ({len(result.unverifiable)} segment(s))"
                ),
            )
        legacy = [entry.seq for entry in stored if is_legacy(entry=entry)]
        if legacy:
            return RecordUntrusted(
                reason=RecordTrustFailureReason.LEGACY,
                detail=f"migrated rows at seq {legacy} carry no verifiable chain",
            )
        return VerifiedRecordPrefix(
            job_id=job_id,
            rows=tuple(record_row(entry=entry) for entry in stored),
            checked_through_seq=result.checked_through_seq,
        )
