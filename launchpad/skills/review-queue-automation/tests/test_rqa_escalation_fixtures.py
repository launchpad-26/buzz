#!/usr/bin/env python3
"""Fakes and builders shared by the `rqa.escalation` (P-11) tests.

Not a test module: `run_all.py` globs `test_*.py` and pytest collects the same, but a
module with no zero-argument `test_*` function simply contributes none — the same
pattern `tests/test_rqa_remediation_fixtures.py` and `tests/test_rqa_harness_fixtures.py`
use. Self-contained: no dependency on another part's test fixtures, so this package's
tests never break because a sibling's fixtures changed shape.

`code/P-11-escalation.md` §8's preamble: "Each is a unit test with fakes for
`RecordWriter`, `EscalationStore`, `JobReader`, `LifecycleResume`, and P-02's
`LifecycleDeps`." `FakeStore` here is an in-memory `EscalationStore`; SQL-level
correctness of the real `SqliteEscalationStore` gets its own file
(`test_rqa_escalation_store.py`) so these tests stay about entry-point behaviour, not
persistence mechanics.
"""

from __future__ import annotations

import pathlib
import sys
from dataclasses import replace
from datetime import datetime, timezone

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from rqa.contracts import (  # noqa: E402
    AppendFailed,
    Entry,
    EscalationCause,
    Job,
    JobStatus,
)
from rqa.escalation.store import EscalationRow  # noqa: E402

HEAD = "a" * 40
BASE = "b" * 40
REPO = "owner/name"
SNAP_HASH = "sha256:snapshot-1"
NOW = datetime(2026, 9, 13, 12, 0, 0, tzinfo=timezone.utc)


def make_job(
    *,
    job_id: str = "job-1",
    head_sha: str = HEAD,
    snapshot_hash: str | None = SNAP_HASH,
    status: JobStatus = JobStatus.ESCALATED,
) -> Job:
    return Job(
        id=job_id,
        repo=REPO,
        number=7,
        head_sha=head_sha,
        base_sha=BASE,
        head_repo=REPO,
        head_ref="feature",
        predecessor_job=None,
        predecessor_head_sha=None,
        snapshot_hash=snapshot_hash,
        status=status,
    )


class FakeRecord:
    """`RecordWriter`. Keeps every append; can fail the terminal one (T4, T17)."""

    def __init__(self, *, fail: bool = False) -> None:
        self.appended: list[tuple[str, str, dict]] = []
        self.fail = fail

    def append(self, job_id: str, kind: str, payload) -> Entry:
        if self.fail:
            raise AppendFailed("the record is unwritable")
        self.appended.append((job_id, kind, dict(payload)))
        return Entry(seq=len(self.appended), hash="h" * 64)

    def of_kind(self, kind: str) -> list[dict]:
        return [payload for _, entry_kind, payload in self.appended if entry_kind == kind]


class FakeStore:
    """An in-memory `EscalationStore`: §5's four methods, no SQL."""

    def __init__(self) -> None:
        self.rows: dict[int, EscalationRow] = {}
        self._next_id = 1
        self.insert_calls: list[int] = []
        self.close_calls: list[int] = []

    def insert(
        self, *, job_id, entry_seq, cause, question, context, head_sha, snapshot_hash, raised_at
    ) -> int:
        row_id = self._next_id
        self._next_id += 1
        self.rows[row_id] = EscalationRow(
            id=row_id,
            job_id=job_id,
            entry_seq=entry_seq,
            cause=cause,
            question=question,
            context=dict(context),
            head_sha=head_sha,
            snapshot_hash=snapshot_hash,
            raised_at=raised_at,
            status="open",
            closed_at=None,
            decision_entry_seq=None,
        )
        self.insert_calls.append(row_id)
        return row_id

    def get(self, escalation_id: int) -> EscalationRow | None:
        return self.rows.get(escalation_id)

    def pending(self) -> tuple[EscalationRow, ...]:
        open_rows = [row for row in self.rows.values() if row.status == "open"]
        return tuple(sorted(open_rows, key=lambda row: (row.raised_at, row.id)))

    def close(self, escalation_id: int, *, decision_entry_seq: int, closed_at) -> None:
        self.rows[escalation_id] = replace(
            self.rows[escalation_id],
            status="closed",
            closed_at=closed_at,
            decision_entry_seq=decision_entry_seq,
        )
        self.close_calls.append(escalation_id)


class FakeJobs:
    """`JobReader`. `job=None` simulates a job that no longer exists ('<gone>')."""

    def __init__(self, job: Job | None) -> None:
        self.job = job
        self.calls: list[str] = []

    def current(self, job_id: str) -> Job | None:
        self.calls.append(job_id)
        return self.job


class FakeLifecycle:
    """`LifecycleResume`. Records every call; its `JobStatus` answer is never inspected
    by `decide()` (§3's guarantee), so a scripted value is enough."""

    def __init__(self, *, status: JobStatus = JobStatus.JUDGED) -> None:
        self.status = status
        self.calls: list[dict] = []

    def resume(self, *, job_id, decision, deps):
        self.calls.append({"job_id": job_id, "decision": decision, "deps": deps})
        return self.status


#: A stand-in for P-02's `LifecycleDeps`: opaque, never read by `decide()` — only
#: forwarded to `lifecycle.resume`. A bare sentinel proves that forwarding never
#: unpacks it.
SENTINEL_DEPS = object()

ALL_CAUSES = tuple(EscalationCause)
