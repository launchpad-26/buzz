"""The externally anchored chain head — `code/P-12-record.md` §3.4, [ADR-0066].

ADR-0066 made the review record a hash chain with **no key**. The chain detects an
edit, a reordering, an interrupted write and any alteration by an actor who does not
recompute it. Two things it cannot detect on its own, both stated by that ADR rather
than discovered later:

- a **removed tail** — `verify` walks from the first row and stops where it stops
  trusting, so a chain with its last entries deleted is shorter but perfectly
  consistent and returns `ok=True`;
- a **wholly rebuilt chain** — an actor who rewrites a row and recomputes every hash
  after it produces a chain that verifies clean.

This module closes both, up to the last anchor, by publishing the chain head where the
*reviewed agent* cannot rewrite it and comparing the local record against it. The
forensic case is the one that matters most in practice: an agent that goes wrong does
not forge its log, it crashes — and the entries that matter most are the last ones.

**Why the local row is written first.** `anchor_job` records the anchor locally
*before* attempting to publish, and leaves `destination` NULL when the publish fails.
That local row is what detects a truncated tail with **no network at all**, which is
what keeps `explain` offline (the parent feature is "tamper-evident record *and
offline explanation*"). The published copy is what additionally catches an actor who
deleted the local anchor rows too. The two are deliberately different strengths:

| What happened | Caught offline? |
|---|---|
| A crashed or killed agent truncated the log | Yes — the local anchor survives |
| An actor truncated the log *and* the local anchors | No — needs the published copy |

**This module never appends to the record. That is a rule, not an accident.**
Publishing an anchor must not write a record entry, because the entry would move the
head, which would need a new anchor, which would publish again — for ever. The
concrete trap is `rqa/github/writes.py`: every mutation there routes through
`_dispatch`, which calls `record.append(job, "action", ...)`. An `AnchorPublisher`
must therefore reach GitHub through the transport directly, never through that layer.
`tests/test_rqa_record_anchor.py` asserts the invariant that makes this stick —
append N entries, publish an anchor, and the record still holds exactly N.

Anchoring is also never triggered *by* an append. The caller decides when (on a
schedule, at job end, or on an explicit command), so even if a recorded write were
ever reintroduced the anchor would lag one entry and catch up, rather than chase.

**The bound on the claim.** Anchoring is periodic. The guarantee is "complete as at
the last anchor", never "complete as at the final entry": entries appended after the
most recent anchor are unattested, and truncation inside that window is undetectable.
Narrowing the window is a frequency choice, not a further mechanism.
"""

from __future__ import annotations

import sqlite3
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timezone

from rqa.contracts import (
    Anchor,
    AnchorEvidence,
    AnchorPublisher,
    AnchorRead,
    AnchorReadOutcome,
    AnchorSource,
    PublishFailed,
)
from rqa.record.store import (
    AnchorConflict,
    StoredAnchor,
    StoredAnchorEvidence,
    import_external_anchors,
    head_entry,
    insert_anchor,
    latest_anchor,
    mark_anchor_published,
    pending_anchors,
)

__all__ = [
    "Anchor",
    "AnchorPublisher",
    "AnchorResult",
    "PublishFailed",
    "anchor_job",
    "AnchorConflict",
    "recover_external_anchors",
]


@dataclass(frozen=True)
class AnchorResult:
    """What one `anchor_job` call did. Every field is an observed outcome."""

    job_id: str
    anchored_seq: int | None  # the head anchored this call; None when there was nothing to do
    published: int  # anchors that reached their destination this call, retries included
    pending: int  # anchors still unpublished after this call
    failures: tuple[str, ...]  # one message per failed publish; never carries record content


def recover_external_anchors(
    connection: sqlite3.Connection,
    *,
    source: AnchorSource,
    repo: str,
    number: int,
    job_id: str,
    publisher: str,
) -> AnchorRead:
    """Explicitly recover authenticated external anchor evidence for one job.

    Only ``FOUND`` can write.  Every other source result is returned unchanged and
    writes nothing; in particular, a source-reported conflict is never narrowed by a
    timestamp choice.  The imported rows hold only anchor position, digest and source
    provenance, so recovery adds no ``record_entries``.
    """
    read = source.read(repo=repo, number=number, job_id=job_id, publisher=publisher)
    if read.outcome is not AnchorReadOutcome.FOUND:
        return read

    # The source contract already authenticates this binding.  Re-checking it at the
    # persistence boundary means a malformed or substituted implementation cannot
    # cross the local trust boundary merely by returning FOUND.
    for item in read.evidence:
        if (
            item.anchor.job != job_id
            or item.repo != repo
            or item.number != number
            or item.publisher != publisher
        ):
            raise AnchorConflict("external anchor evidence does not match the recovery request")
    import_external_anchors(connection=connection, job=job_id, evidence=read.evidence)
    return read


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _stamp(moment: datetime) -> str:
    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=timezone.utc)
    return moment.astimezone(timezone.utc).isoformat(timespec="microseconds")


def _publish(
    connection: sqlite3.Connection, publisher: AnchorPublisher, row: StoredAnchor
) -> str | None:
    """Publish one recorded anchor. Returns a failure message, or None on success."""
    try:
        destination = publisher.publish(
            anchor=Anchor(job=row.job, seq=row.seq, hash=row.hash, at=row.at)
        )
    except PublishFailed as exc:
        # `AnchorPublisher`'s contract is that a failed publish raises `PublishFailed`,
        # and this catches exactly that and nothing wider.
        #
        # Nothing broader is caught **here** on purpose. §8's guard forbids
        # `except Exception` anywhere in `rqa/record/`, because that is how
        # U-DISPATCH-20's defect was written — a swallowed failure around a ledger
        # write, letting a review complete authoritatively with a knowingly incomplete
        # record. The guard is right, and this module is not the place to make an
        # exception to it.
        #
        # A publisher that violates its contract by raising something else is
        # contained at the boundary instead, where publishers are built: see
        # `rqa/github/anchor_publisher.py`, which converts anything its transport
        # throws into `PublishFailed` before it can reach this package.
        return f"seq {row.seq}: {exc}"
    if not destination:
        return f"seq {row.seq}: publisher returned no destination"
    mark_anchor_published(
        connection=connection, job=row.job, seq=row.seq, destination=destination
    )
    return None


def anchor_job(
    connection: sqlite3.Connection,
    job_id: str,
    *,
    publisher: AnchorPublisher,
    clock: Callable[[], datetime] = _utcnow,
) -> AnchorResult:
    """Anchor `job_id`'s current chain head, and retry anything still pending.

    Behaviour, in order. Every branch returns.

    1. Retry every pending anchor for this job, oldest first. A failed publish leaves
       the row pending and contributes a message; it never raises.
    2. Read the job's current head. No head → nothing to anchor.
    3. Head already anchored → no new row. Anchoring is idempotent, so a caller may
       run it as often as it likes without growing the table.
    4. Otherwise record the anchor locally, then attempt to publish it.

    **Never raises for a publish outcome, and never appends to the record.** A caller
    that cannot reach its destination still has a local anchor, and an append that
    happens next is unaffected — the whole point is that anchoring cannot fail a
    review.
    """
    result_failures: list[str] = []
    published = 0

    for row in pending_anchors(connection=connection, job=job_id):
        failure = _publish(connection, publisher, row)
        if failure is None:
            published += 1
        else:
            result_failures.append(failure)

    head = head_entry(connection=connection, job=job_id)
    if head is None:
        return AnchorResult(
            job_id=job_id,
            anchored_seq=None,
            published=published,
            pending=len(pending_anchors(connection=connection, job=job_id)),
            failures=tuple(result_failures),
        )

    existing = latest_anchor(connection=connection, job=job_id)
    if existing is not None and existing.seq >= head.seq:
        return AnchorResult(
            job_id=job_id,
            anchored_seq=None,
            published=published,
            pending=len(pending_anchors(connection=connection, job=job_id)),
            failures=tuple(result_failures),
        )

    insert_anchor(
        connection=connection,
        job=job_id,
        seq=head.seq,
        hash=head.hash,
        at=_stamp(clock()),
    )
    fresh = latest_anchor(connection=connection, job=job_id)
    assert fresh is not None  # noqa: S101 - just inserted, in this transaction
    failure = _publish(connection, publisher, fresh)
    if failure is None:
        published += 1
    else:
        result_failures.append(failure)

    return AnchorResult(
        job_id=job_id,
        anchored_seq=head.seq,
        published=published,
        pending=len(pending_anchors(connection=connection, job=job_id)),
        failures=tuple(result_failures),
    )
