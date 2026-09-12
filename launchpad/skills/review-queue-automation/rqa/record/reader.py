"""`SQLiteRecordReader` — `code/P-12-record.md` §2 and §5's read protocol — plus
`resolve_job`, §3.3's (repo, number) → job lookup.

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

**`resolve_job`** answers "which job is the current head for this (repo, number)?"
without ever reading P-01's `jobs` table (`container.md` §5 does not list P-12 as a
reader of it, §6): every job is self-describing from its own `transition` entries
alone (§6). It never guesses — zero or more than one head candidate is
`AmbiguousHead`, never a silent pick of the first or the latest.
"""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass

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
    rows_of_kind_across_jobs,
)
from rqa.record.verify import verify

__all__ = ["SQLiteRecordReader", "resolve_job", "ResolvedJob", "NoRecord", "AmbiguousHead"]


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


@dataclass(frozen=True)
class ResolvedJob:
    """`resolve_job` found exactly one unambiguous current head (§3.3)."""

    job_id: str


@dataclass(frozen=True)
class NoRecord:
    """No job's `transition` entries name this (repo, number)."""


@dataclass(frozen=True)
class AmbiguousHead:
    """More than one job matches (repo, number) and none names the other as its
    predecessor — `resolve_job` never guesses which is current."""

    candidates: tuple[str, ...]


def resolve_job(
    connection: sqlite3.Connection, repo: str, number: int
) -> ResolvedJob | NoRecord | AmbiguousHead:
    """§3.3: the (repo, number) → job lookup every `explain(repo, number)` call starts
    from, without ever reading P-01's `jobs` table.

    Reads every `transition` row across every job (§5's read protocol), keeps only
    those whose payload's `repo`/`number` match, and groups the survivors by `job`.
    Zero matching jobs is `NoRecord`. Among the matching jobs, a job is a head
    candidate unless some *other* matching job's `transition` payload names it as
    that job's own `predecessor_job` — a job can carry several `transition` rows
    over its life, so every one of them is checked, not just the first. Exactly one
    head candidate is `ResolvedJob`; zero or more than one is `AmbiguousHead`, naming
    every candidate rather than picking one.

    A row whose `payload` does not parse as the closed transition shape (missing
    `repo`/`number`, or a `payload` that is not a JSON object) is skipped rather than
    raising: `resolve_job` reconstructs from what the record actually holds, and a
    corrupt or foreign row is evidence for nothing here.
    """
    payloads_by_job: dict[str, list[dict]] = {}
    for entry in rows_of_kind_across_jobs(connection=connection, kind="transition"):
        try:
            payload = json.loads(entry.payload)
        except ValueError:
            continue
        if not isinstance(payload, dict):
            continue
        if payload.get("repo") != repo or payload.get("number") != number:
            continue
        payloads_by_job.setdefault(entry.job, []).append(payload)

    if not payloads_by_job:
        return NoRecord()

    named_as_predecessor: set[str] = set()
    for payloads in payloads_by_job.values():
        for payload in payloads:
            predecessor = payload.get("predecessor_job")
            if isinstance(predecessor, str):
                named_as_predecessor.add(predecessor)

    heads = sorted(job for job in payloads_by_job if job not in named_as_predecessor)
    if len(heads) == 1:
        return ResolvedJob(job_id=heads[0])
    return AmbiguousHead(candidates=tuple(heads if heads else sorted(payloads_by_job)))
