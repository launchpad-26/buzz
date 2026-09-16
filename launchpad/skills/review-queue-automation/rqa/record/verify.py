"""`verify` — chain recomputation, `code/P-12-record.md` §3.2.

`verify` is not a separately named edge; it is the mechanism `explain` calls, exposed
publicly because tests, and an operator who wants to check tamper-evidence without a
full reconstruction, both need it directly (§3).

**What it proves, and what it does not.** It walks the job's non-legacy rows from the
first, recomputing each row's own hash and checking each row's recorded parent. That
detects accidental corruption, an interrupted or partial write, reordering, and any
edit by an actor who does not recompute the chain.

It does **not** detect an actor who rewrites a row *and* recomputes every downstream
hash, and it does **not** detect a removed tail: the walk starts at the first row and
stops at the first row it stops trusting, so a chain with its last rows deleted is
shorter but internally consistent and returns `ok=True`. `bad_seq` is the first seq
verification stopped trusting, never evidence that rows were removed (issue #2220).
Both gaps are ADR-0066's stated position, and both are closed by the externally
anchored chain head (#2300), not by anything in this module.

**The key is gone (ADR-0066).** `verify` once authenticated keyed rows against an
operator-held HMAC key read from the platform credential store, and opened an
`unverifiable: no key` segment for rows it could not authenticate. There is no key
now, so there is nothing to authenticate against and nothing to report as a gap: the
chain is the whole check, and it applies uniformly to every row.

Historical `keyed = 1` rows written before that change keep their stored HMAC. This
module does not read it, does not validate its shape, and never treats its presence
as a break — such a row is checked by its hash and its parent link exactly as any
other row is. A record written under ADR-0063 therefore stays readable and is never
presented as tampered with.

`verify` never mutates either table, never reads the trace, and never raises for an
integrity outcome; only a store read failure raises, as `sqlite3.Error`/`OSError`.
"""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from enum import Enum
from typing import Literal

from rqa.record.hashing import (
    PayloadNotSerializable,
    compute_hash,
)
from rqa.record.store import StoredEntry, entries_for_job, is_legacy, latest_anchor

__all__ = ["BreakKind", "VerifyResult", "verify"]


class BreakKind(str, Enum):
    HASH_MISMATCH = "hash_mismatch"  # a row's stored hash does not match its own recomputed content
    CHAIN_BREAK = "chain_break"  # a row's prev_hash does not match the previous real row's hash
    # Named TAIL_REMOVED, not TRUNCATED: `tests/test_rqa_record_surface.py` scans this
    # package's string literals for destructive SQL, and "TRUNCATED" contains
    # "TRUNCATE". The guard is right; the enum moved rather than the guard.
    TAIL_REMOVED = "tail_removed"  # entries the anchored head proves existed are gone
    ANCHOR_MISMATCH = "anchor_mismatch"  # the row at the anchored seq is not the row anchored


@dataclass(frozen=True)
class VerifyResult:
    job_id: str
    ok: bool
    bad_seq: int | None  # first seq verification stopped trusting; None iff ok
    kind: BreakKind | None  # None iff ok
    checked_through_seq: int  # last real (non-legacy) seq examined before stopping or finishing
    anchored_through_seq: int  # highest seq an anchor attests; 0 when the job has none
    anchor_published: bool  # False when the newest anchor never reached its destination


def _row_hash(entry: StoredEntry, *, payload: object) -> str:
    return compute_hash(
        job=entry.job,
        seq=entry.seq,
        kind=entry.kind,
        at=entry.at,
        payload=payload,  # type: ignore[arg-type]
        prev_hash=entry.prev_hash,
    )


def verify(connection: sqlite3.Connection, job_id: str) -> VerifyResult:
    """§3.2's steps, in order. Every branch returns.

    ADR-0066: the chain is the whole check. There is no key to read, so a row's
    `keyed` bit and its stored `hmac` are not consulted — a historical `keyed = 1`
    row is checked exactly as any other row is, by its own hash and its link to its
    parent, and is never reported as a break for carrying an HMAC nothing can verify.
    """

    rows = entries_for_job(connection=connection, job=job_id)
    anchor = latest_anchor(connection=connection, job=job_id)
    anchored_through = anchor.seq if anchor is not None else 0
    anchor_published = anchor.published if anchor is not None else False
    by_seq = {entry.seq: entry for entry in rows if not is_legacy(entry=entry)}
    checked_through = 0
    parent_hash: str | None = None  # the previous real row's hash; None before the first
    seen_real = False

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
                checked_through_seq=checked_through,
                anchored_through_seq=anchored_through,
                anchor_published=anchor_published,
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
                checked_through_seq=checked_through,
                anchored_through_seq=anchored_through,
                anchor_published=anchor_published,
            )

        parent_hash = entry.hash
        seen_real = True
        checked_through = entry.seq

    # -- step 4: the anchored head (ADR-0066) ---------------------------------
    # The chain is internally consistent at this point. An anchor is independent
    # evidence about what the chain *was*, so it catches the two things internal
    # consistency cannot: rows removed from the tail, and a chain rebuilt wholesale.
    if anchor is not None:
        anchored_row = by_seq.get(anchor.seq)
        if anchored_row is None:
            # The anchor attests a sequence that is no longer in the record. A
            # consistent walk over the rows that remain is exactly what truncation
            # looks like, which is why this check cannot come from the walk itself.
            return VerifyResult(
                job_id=job_id,
                ok=False,
                bad_seq=anchor.seq,
                kind=BreakKind.TAIL_REMOVED,
                checked_through_seq=checked_through,
                anchored_through_seq=anchored_through,
                anchor_published=anchor_published,
            )
        if anchored_row.hash != anchor.hash:
            # The row is present at that sequence but is not the row that was
            # anchored: the chain was recomputed after the fact.
            return VerifyResult(
                job_id=job_id,
                ok=False,
                bad_seq=anchor.seq,
                kind=BreakKind.ANCHOR_MISMATCH,
                checked_through_seq=checked_through,
                anchored_through_seq=anchored_through,
                anchor_published=anchor_published,
            )

    # -- step 5: a complete walk ----------------------------------------------
    return VerifyResult(
        job_id=job_id,
        ok=True,
        bad_seq=None,
        kind=None,
        checked_through_seq=checked_through,
        anchored_through_seq=anchored_through,
        anchor_published=anchor_published,
    )
