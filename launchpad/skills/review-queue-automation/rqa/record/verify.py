"""`verify` — chain and keyed-segment recomputation, `code/P-12-record.md` §3.2.

`verify` is not a separately named edge; it is the mechanism `explain` calls, exposed
publicly because tests, and an operator who wants to check tamper-evidence without a
full reconstruction, both need it directly (§3).

**What it proves, and what it does not.** It walks the job's non-legacy rows from the
first, recomputing each row's own hash and checking each row's recorded parent, then
authenticates every keyed row it can against the operator's key. An alteration that
is internally consistent — a rewritten row with correctly recomputed downstream
hashes — still fails its HMAC, which is the whole point of the keyed bit (RQA-NFR-028).
What it does **not** do is detect a removed tail: the walk starts at the first row and
stops at the first row it stops trusting, so a chain with its last rows deleted is
shorter but internally consistent and returns `ok=True`. `bad_seq` is the first seq
verification stopped trusting, never evidence that rows were removed (issue #2220).

**No key is not a break.** An unkeyed row, and a keyed row this machine has no key
for, both open an `unverifiable: no key` segment. Neither refuses the record and
neither is reported as tampering: a record nobody can authenticate is honestly
unverifiable, and saying so is what keeps a missing key from stopping a review
(ADR-0063).

`verify` never mutates either table, never reads the trace, and never raises for an
integrity outcome; only a store read failure raises, as `sqlite3.Error`/`OSError`.
"""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from enum import Enum
from typing import Literal

from rqa.contracts import KeyStore
from rqa.record.hashing import (
    PayloadNotSerializable,
    compute_hash,
    compute_hmac,
    hmac_matches,
    is_hex_digest,
)
from rqa.record.keychain import KEY_NAME, KeyStoreExplanationUnavailable, OSKeyStore
from rqa.record.store import StoredEntry, entries_for_job, is_legacy

__all__ = ["BreakKind", "UnverifiableSegment", "VerifyResult", "verify"]


class BreakKind(str, Enum):
    HASH_MISMATCH = "hash_mismatch"  # a row's stored hash does not match its own recomputed content
    CHAIN_BREAK = "chain_break"  # a row's prev_hash does not match the previous real row's hash
    HMAC_MISMATCH = "hmac_mismatch"  # a keyed row does not authenticate under the available key


@dataclass(frozen=True)
class UnverifiableSegment:
    job_id: str
    first_seq: int
    last_seq: int
    reason: Literal["no key"] = "no key"


@dataclass(frozen=True)
class VerifyResult:
    job_id: str
    ok: bool
    bad_seq: int | None  # first seq verification stopped trusting; None iff ok
    kind: BreakKind | None  # None iff ok
    hmac_checked: bool  # True iff at least one keyed row was checked this run
    checked_through_seq: int  # last real (non-legacy) seq examined before stopping or finishing
    unverifiable: tuple[UnverifiableSegment, ...]  # unkeyed or unavailable-key segments; never breaks


class _Segments:
    """Accumulates consecutive unverifiable rows into segments.

    §3.1: "consecutive unkeyed rows form one segment and a later keyed row closes
    it". A keyed run with no available key is the same shape and the same reason, so
    adjacency is what joins rows here, not why each one could not be authenticated —
    an operator reading `unverifiable: no key` over seqs 4-9 does not care which of
    the two produced each row, only that none of them is authenticated.
    """

    def __init__(self, job_id: str):
        self._job_id = job_id
        self._closed: list[UnverifiableSegment] = []
        self._first: int | None = None
        self._last: int | None = None

    def add(self, seq: int) -> None:
        if self._first is None:
            self._first = seq
        self._last = seq

    def close(self) -> None:
        if self._first is not None and self._last is not None:
            self._closed.append(
                UnverifiableSegment(job_id=self._job_id, first_seq=self._first, last_seq=self._last)
            )
        self._first = None
        self._last = None

    def collected(self) -> tuple[UnverifiableSegment, ...]:
        self.close()
        return tuple(self._closed)


def _row_hash(entry: StoredEntry, *, payload: object) -> str:
    return compute_hash(
        job=entry.job,
        seq=entry.seq,
        kind=entry.kind,
        at=entry.at,
        payload=payload,  # type: ignore[arg-type]
        prev_hash=entry.prev_hash,
    )


def verify(
    connection: sqlite3.Connection, job_id: str, *, keystore: KeyStore = OSKeyStore()
) -> VerifyResult:
    """§3.2's four steps, in order. Every branch returns."""

    rows = entries_for_job(connection=connection, job=job_id)
    segments = _Segments(job_id)
    hmac_checked = False
    checked_through = 0
    parent_hash: str | None = None  # the previous real row's hash; None before the first
    seen_real = False
    #: A key read once and reused for the rest of the walk. Only a *successful* read
    #: is cached: §3.2 lets a later keyed row close a segment an earlier unavailable
    #: read opened, so an absent or unaskable key is re-asked rather than remembered.
    key: bytes | None = None

    for entry in rows:
        if is_legacy(entry=entry):
            # §6: a migrated row is never examined here. It is not a break and not an
            # unverifiable segment — it simply carries no chain to check.
            continue

        # -- step 2: parent, then own content ---------------------------------
        expected_parent = parent_hash if seen_real else None
        if entry.prev_hash != expected_parent:
            return VerifyResult(
                job_id=job_id,
                ok=False,
                bad_seq=entry.seq,
                kind=BreakKind.CHAIN_BREAK,
                hmac_checked=hmac_checked,
                checked_through_seq=checked_through,
                unverifiable=segments.collected(),
            )
        try:
            recomputed = _row_hash(entry, payload=json.loads(entry.payload))
        except (ValueError, PayloadNotSerializable):
            # Stored payload text that no longer parses, or no longer parses into
            # JSON-safe data, cannot be rehashed into the stored hash. That is the
            # hash-mismatch finding itself, not an exception for the caller: §3.2
            # never raises for an integrity outcome.
            recomputed = None
        if recomputed != entry.hash:
            return VerifyResult(
                job_id=job_id,
                ok=False,
                bad_seq=entry.seq,
                kind=BreakKind.HASH_MISMATCH,
                hmac_checked=hmac_checked,
                checked_through_seq=checked_through,
                unverifiable=segments.collected(),
            )

        # -- step 3: the keyed bit --------------------------------------------
        if not entry.keyed:
            segments.add(entry.seq)
        elif not is_hex_digest(value=entry.hmac):
            return VerifyResult(
                job_id=job_id,
                ok=False,
                bad_seq=entry.seq,
                kind=BreakKind.HMAC_MISMATCH,
                hmac_checked=hmac_checked,
                checked_through_seq=checked_through,
                unverifiable=segments.collected(),
            )
        else:
            if key is None:
                try:
                    key = keystore.read(KEY_NAME)
                except (KeyStoreExplanationUnavailable, OSError):
                    # "verification remains readable and reports the run
                    # `unverifiable: no key`, rather than refusing the record."
                    key = None
            if key is None:
                segments.add(entry.seq)
            else:
                expected = compute_hmac(key=key, job=entry.job, seq=entry.seq, hash=entry.hash)
                if not hmac_matches(stored=entry.hmac or "", recomputed=expected):
                    return VerifyResult(
                        job_id=job_id,
                        ok=False,
                        bad_seq=entry.seq,
                        kind=BreakKind.HMAC_MISMATCH,
                        hmac_checked=hmac_checked,
                        checked_through_seq=checked_through,
                        unverifiable=segments.collected(),
                    )
                hmac_checked = True
                segments.close()

        parent_hash = entry.hash
        seen_real = True
        checked_through = entry.seq

    # -- step 4: a complete walk ----------------------------------------------
    return VerifyResult(
        job_id=job_id,
        ok=True,
        bad_seq=None,
        kind=None,
        hmac_checked=hmac_checked,
        checked_through_seq=checked_through,
        unverifiable=segments.collected(),
    )
