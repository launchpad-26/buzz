"""`append` — E-13, `code/P-12-record.md` §3.1.

Every other part except P-04 reaches the record through this one method, and every
one of them calls it on a `RecordWriter` built over the *same* `sqlite3.Connection`
the caller's own state-changing statement runs on, before that transaction commits.
`append` never commits and never rolls back: that is what makes the entry and the
change it records one atomic fact. `components.md` §4, P-02: "Every transition is
committed in one transaction with its `transition` entry in the record (E-13); a
failed append is a failed transition."

**`AppendFailed` propagates, always.** Nothing in this package catches it (§7), so a
caller that cannot write its provenance cannot quietly complete: it sees the failure
and rolls back. That is exactly the failure conversion U-DISPATCH-20 records as the
estate's defect — `except Exception: pass` around the ledger write, so a review could
complete authoritatively with a knowingly incomplete record — and the responsibility
carried here with that shape corrected (U-RESILIENCE-06's rework).

**An absent key is not a failure.** §3.1 step 5: the key store returning `None` makes
a successful, explicitly unkeyed append — `keyed=0`, `hmac=NULL` — which opens an
`unverifiable: no key` segment for `verify` to report honestly (ADR-0063). Only a key
store that could not be *asked* is `AppendFailed`. No key is ever generated to fill
the gap.
"""

from __future__ import annotations

import sqlite3
from collections.abc import Callable, Mapping
from datetime import datetime, timezone

from rqa.contracts import AppendFailed, Entry, EntryKind, KeyStore
from rqa.record.hashing import (
    GENESIS_PREV_HASH,
    canonical_json,
    compute_hash,
    compute_hmac,
)
from rqa.record.keychain import KEY_NAME, KeyStoreExplanationUnavailable, OSKeyStore
from rqa.record.kinds import require_kind
from rqa.record.store import StoredEntry, ensure_schema, head_entry, insert_entry, upsert_head

__all__ = ["SQLiteRecordWriter", "utcnow"]


def utcnow() -> datetime:
    """The default wall clock: an aware UTC timestamp."""
    return datetime.now(timezone.utc)


def _stamp(moment: datetime) -> str:
    """§3.1 step 4: UTC ISO-8601 with microseconds.

    A naive reading is taken as UTC rather than as local time. The alternative — a
    timestamp that means something different depending on which machine wrote it —
    is not a property a record can carry.
    """
    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=timezone.utc)
    return moment.astimezone(timezone.utc).isoformat(timespec="microseconds")


class SQLiteRecordWriter:
    """P-12's `RecordWriter` over one caller-owned connection.

    `connection`, `clock` and `keystore` are constructor-only dependencies; they are
    not E-13 parameters (§3.1). The schema is ensured here, once, so no DDL runs
    inside the transaction `append` joins.
    """

    def __init__(
        self,
        connection: sqlite3.Connection,
        *,
        clock: Callable[[], datetime] = utcnow,
        keystore: KeyStore = OSKeyStore(),
    ):
        self._connection = connection
        self._clock = clock
        self._keystore = keystore
        ensure_schema(connection=connection)

    def append(self, job_id: str, kind: EntryKind, payload: Mapping) -> Entry:
        """E-13, verbatim from `CONTRACTS.md` §7. §3.1's eight steps, in order.

        Deterministic for identical hashed inputs, re-reads its head on every call,
        and never inspects payload semantics beyond steps 1 and 2 — which kind means
        what is the calling part's contract, not this one's (§7).
        """
        # 1. The closed set, before anything is read or written.
        kind = require_kind(kind=kind)

        # 2. JSON-safety, before anything is written. `PayloadNotSerializable`
        #    propagates: an unrenderable payload is the caller's defect (§2).
        payload_text = canonical_json(payload=payload)

        # 3. The head this entry chains onto — re-read every call, never cached.
        try:
            previous = head_entry(connection=self._connection, job=job_id)
        except (sqlite3.Error, OSError) as exc:
            raise AppendFailed(
                f"could not read the record head for job {job_id!r} (kind {kind!r}): {exc}"
            ) from exc
        if previous is None:
            seq = 1
            prev_hash = GENESIS_PREV_HASH
        else:
            seq = previous.seq + 1
            prev_hash = previous.hash

        # 4. Time and identity.
        at = _stamp(self._clock())
        entry_hash = compute_hash(
            job=job_id, seq=seq, kind=kind, at=at, payload=payload, prev_hash=prev_hash
        )

        # 5. The operator's key: present, absent, or unaskable — three outcomes,
        #    two of them successful appends and only the third a failure.
        try:
            key = self._keystore.read(KEY_NAME)
        except (KeyStoreExplanationUnavailable, OSError) as exc:
            raise AppendFailed(
                f"the key store could not be read while appending {kind!r} for job "
                f"{job_id!r}: {exc}"
            ) from exc
        if key is None:
            keyed = False
            entry_hmac: str | None = None
        else:
            keyed = True
            entry_hmac = compute_hmac(key=key, job=job_id, seq=seq, hash=entry_hash)
        del key

        entry = StoredEntry(
            job=job_id,
            seq=seq,
            kind=kind,
            at=at,
            payload=payload_text,
            prev_hash=prev_hash,
            hash=entry_hash,
            hmac=entry_hmac,
            keyed=keyed,
        )

        # 6. The row. No commit is issued.
        try:
            insert_entry(connection=self._connection, entry=entry)
        except (sqlite3.Error, OSError) as exc:
            raise AppendFailed(
                f"could not write the {kind!r} entry at seq {seq} for job {job_id!r}: {exc}"
            ) from exc

        # 7. The head pointer, on the same connection and in the same transaction.
        try:
            upsert_head(
                connection=self._connection,
                job=job_id,
                seq=seq,
                hash=entry_hash,
                hmac=entry_hmac,
                keyed=keyed,
            )
        except (sqlite3.Error, OSError) as exc:
            raise AppendFailed(
                f"could not update the record head for job {job_id!r} at seq {seq}: {exc}"
            ) from exc

        # 8.
        return Entry(seq=seq, hash=entry_hash)
