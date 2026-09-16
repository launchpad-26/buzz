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

**There is no key (ADR-0066).** §3.1 step 5 once read an operator-held HMAC key from
the platform credential store. ADR-0066 retired it: the review record is a hash chain
with an externally anchored head, and the key defended an actor already outside
#2006's stated trust boundary while costing a per-platform credential integration.

Two consequences worth stating here rather than leaving to be discovered:

- **`append` has no credential-store failure mode.** It cannot fail for a key reason
  on any platform, which is the whole of #2272. Every entry is written `keyed=0`,
  `hmac=NULL`, the branch the store's CHECK on `(keyed, hmac)` already allowed.
- **Historical `keyed=1` rows are left exactly as they are.** Their HMAC column is
  not cleared and the schema is not migrated; `verify` reports them as unattested
  rather than as a break, so a record written before this change stays readable and
  is never presented as tampered with.
"""

from __future__ import annotations

import sqlite3
from collections.abc import Callable, Mapping
from datetime import datetime, timezone

from rqa.contracts import AppendFailed, Entry, EntryKind
from rqa.record.hashing import (
    GENESIS_PREV_HASH,
    canonical_json,
    compute_hash,
)
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

    `connection` and `clock` are constructor-only dependencies; they are not E-13
    parameters (§3.1). The schema is ensured here, once, so no DDL runs inside the
    transaction `append` joins.

    ADR-0066: there is no key. Every entry this writer produces is unkeyed
    (`keyed=0`, `hmac=NULL`), and `append` has no credential-store failure mode on
    any platform.
    """

    def __init__(
        self,
        connection: sqlite3.Connection,
        *,
        clock: Callable[[], datetime] = utcnow,
    ):
        self._connection = connection
        self._clock = clock
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

        # 5. ADR-0066 retired the operator-held key, so this step no longer reads
        #    one and no longer has a failure mode. Every entry is unkeyed, which the
        #    store's CHECK on `(keyed, hmac)` accepts as the `keyed = 0` branch.
        #    Historical `keyed = 1` rows keep their HMAC and stay readable; `verify`
        #    reports them as unattested rather than as a break.
        keyed = False
        entry_hmac: str | None = None

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
