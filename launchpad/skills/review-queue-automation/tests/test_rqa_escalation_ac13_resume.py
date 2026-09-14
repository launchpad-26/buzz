#!/usr/bin/env python3
"""AC13 clause 3, end to end: the REAL `rqa.lifecycle.resume()` wired to a REAL
`rqa.escalation` store — `code/P-11-escalation.md`'s AC13, and the lane prompt's
"AC13 clause 3" instruction.

No pytest: every `test_*` function takes no arguments, per `tests/run_all.py`.

**Import boundary.** P-11 §1 forbids `rqa.escalation` from importing P-02's
implementation, and P-02 §1 forbids `rqa.lifecycle` from importing `rqa.escalation`.
This file imports both — it is the wiring test the lane prompt asks for, and it is the
one place that wiring is allowed to exist: never inside either package's own source.

**What this file actually proves, and what it discloses.** `resume()` re-derives "the
open escalation this decision answers" through `deps.escalation.pending(store=...)`
(`rqa/lifecycle/resume.py`'s `_open_escalation`), which only ever returns rows with
`status = 'open'` (`code/P-11-escalation.md` §5). `decide()`'s own step order — §3 steps
11-13 — closes the row (`store.close`, step 12) *before* calling `lifecycle.resume`
(step 13). Both steps run against the identical `EscalationStore`/`sqlite3.Connection`
in production (P-01 wires one `human_requests` table per state directory), so by the
time `resume()` looks the escalation up, it has already been closed and `pending()` no
longer lists it — `_open_escalation` finds zero matches and raises `LifecycleError`,
for every cause, on every successful `decide()`. `test_the_real_round_trip_through_decide_currently_fails`
proves this is real and reproducible, not a theory; it is disclosed in the handoff as a
cross-part defect between this already-landed `rqa/lifecycle/resume.py` and
`code/P-11-escalation.md` §3's step order, out of scope for this lane to fix (neither
`rqa/lifecycle/**` nor `architecture/**` may be touched here).

`test_the_real_resume_resumes_at_the_recorded_step_without_restarting_the_review` proves
the part of AC13 clause 3 that P-11 alone can prove without that defect in the way:
handed a still-open, genuinely-persisted `SqliteEscalationStore` row (the shape
`resume()` needs to succeed), the REAL `rqa.lifecycle.resume()` transitions the job
directly from `ESCALATED` to its recorded resting status — no re-entry into planning or
judgement — using this package's real store and its real `raise_()`, not a fake.
"""

from __future__ import annotations

import pathlib
import sys
from datetime import datetime, timezone

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from lifecycle_cascade_bench import (  # noqa: E402
    HEAD,
    SNAP_HASH,
    FakeGithub,
    FakeLease,
    bench,
    make_deps,
    make_facts,
    make_review,
    stored_status,
    transitions,
)

import rqa.escalation as escalation  # noqa: E402
from rqa.contracts import Decision, EscalationCause, JobStatus  # noqa: E402
from rqa.escalation.store import SqliteEscalationStore  # noqa: E402
from rqa.lifecycle import resume  # noqa: E402
from rqa.lifecycle.errors import LifecycleError  # noqa: E402


class RealEscalationClient:
    """Wires the REAL `rqa.escalation.raise_`/`pending` to a REAL `SqliteEscalationStore`
    — P-02's `EscalationClient` Protocol (`rqa/lifecycle/deps.py`), satisfied here with
    this part's actual implementation rather than a fake. `.store` is what
    `_open_escalation` reads (`deps.escalation.pending(store=deps.escalation.store)`).
    This adapter lives only in the test: neither package's source may import the other.
    """

    def __init__(self, store: SqliteEscalationStore) -> None:
        self.store = store

    def raise_(self, *, job, cause, question, context, record, store):
        return escalation.raise_(
            job=job, cause=cause, question=question, context=context, record=record, store=store
        )

    def pending(self, *, store):
        return escalation.pending(store=store)


class RealLifecycle:
    """`LifecycleResume` — wraps the real `rqa.lifecycle.resume` free function so
    `decide()`'s `lifecycle.resume(job_id=..., decision=..., deps=...)` call resolves to
    it. `resume` is a plain function, not a bound method; this is the smallest adapter
    that gives it a `.resume` attribute without editing either package's source."""

    def resume(self, *, job_id, decision, deps):
        return resume(job_id=job_id, decision=decision, deps=deps)


class FakeJobs:
    """`JobReader` — P-01's view, faked here; `decide()`'s own freshness check (§3
    steps 7-8) is exercised the same way every other T5-T17 test exercises it."""

    def __init__(self, job) -> None:
        self.job = job

    def current(self, job_id):
        return self.job


def _escalated_job_with_a_real_open_row():
    """A job pinned at `ESCALATED`, `SNAP_HASH`, plus one real, still-open escalation
    raised against it through this package's own `raise_()` and `SqliteEscalationStore`
    — the exact shape `rqa.lifecycle.resume()` needs to find via `pending()`."""
    connection, record, job = bench(status=JobStatus.ESCALATED, snapshot_hash=SNAP_HASH)
    record.append(job.id, "transition", {
        "from_state": None, "to_state": "queued", "reason": "arrival", "repo": job.repo,
        "number": job.number, "head_sha": job.head_sha, "base_sha": job.base_sha,
        "predecessor_job": None,
    })
    connection.commit()

    store = SqliteEscalationStore(connection)
    raised = escalation.raise_(
        job=job,
        cause=EscalationCause.AUTHORITY_REQUIREMENT,
        question="RQA has no MERGE authority for this repository; may a human record the "
        "GitHub-side outcome directly?",
        context={},
        record=record,
        store=store,
    )
    connection.commit()
    return connection, record, job, store, raised


#: `escalation.raise_()` stamps `raised_at` with the real wall clock (§3: no injectable
#: clock on `raise_`, unlike `decide`'s). `make_review`'s own fixture default is a fixed
#: historical constant relative to `lifecycle_cascade_bench.NOW`, which the real
#: `raised_at` outruns as soon as this suite is run after that constant's date — a
#: reproducible, date-dependent flake, not a genuine staleness case. A fixed, far-future
#: `submitted_at` sidesteps it without touching either test's own body.
_FAR_FUTURE = datetime(2100, 1, 1, tzinfo=timezone.utc)


def _deps_for_12b(connection, record, *, job, escalation_client):
    lease = FakeLease()
    return make_deps(
        connection,
        record,
        github=FakeGithub(
            facts=make_facts(
                job=job,
                reviews=(make_review(outcome="changes_requested", submitted_at=_FAR_FUTURE),),
            )
        ),
        escalation=escalation_client,
        # Deliberately `None`/absent: proves 12b never re-enters planning or judgement.
        policy=None,
        authority=None,
        judgement=None,
        harness=None,
        supply=None,
        remediation=None,
        reuse=None,
        claim_lease=lease.claim,
        release_lease=lease.release,
    )


# -- The part of AC13 clause 3 this lane can prove without the disclosed defect ---


def test_the_real_resume_resumes_at_the_recorded_step_without_restarting_the_review() -> None:
    """`rqa.lifecycle.resume()`, called directly against a real, still-open
    `SqliteEscalationStore` row — the still-open state a real `resume()` needs, which
    `decide()`'s actual step-12-before-13 order never leaves behind (D-B5-2; see the
    module docstring), supplied here directly to isolate this half of the proof from
    that defect — transitions `ESCALATED -> CHANGES_REQUESTED` directly. `transitions()`
    shows only the original `queued` arrival and the direct resume outcome: no
    `planned`/`reviewing`/`judged` entry exists, so nothing re-entered planning or
    judgement — the review was resumed, not restarted."""
    connection, record, job, store, raised = _escalated_job_with_a_real_open_row()
    real_client = RealEscalationClient(store)
    deps = _deps_for_12b(connection, record, job=job, escalation_client=real_client)

    decision = Decision(
        actor="human-reviewer", basis="reviewed on GitHub", substantiates=None,
        outcome="changes_requested",
    )
    result = resume(job_id=job.id, decision=decision, deps=deps)

    assert result is JobStatus.CHANGES_REQUESTED
    assert stored_status(connection, job.id) == "changes_requested"
    assert transitions(connection, job.id) == ["queued", "changes_requested"]
    assert real_client.pending(store=store) == (raised,), (
        "resume() read the escalation through this package's real pending(), not a fake"
    )


# -- The disclosed defect: decide()'s own step order breaks the real round trip ---


def test_the_real_round_trip_through_decide_currently_fails() -> None:
    """Regression-guards the disclosed defect: `decide()` follows
    `code/P-11-escalation.md` §3 literally — step 12 (`store.close`) before step 13
    (`lifecycle.resume`) — so by the time the REAL `rqa.lifecycle.resume()` asks
    `pending()` for "the one open escalation this decision answers", P-11 has already
    closed it. `_open_escalation` (`rqa/lifecycle/resume.py`) finds zero matches and
    raises `LifecycleError`. This is a genuine, reproducible cross-part defect between
    the already-landed `rqa/lifecycle/resume.py` and this part's own §3 step order, not
    a bug in this package: `decide()` is implemented character-for-character to §3, and
    neither `rqa/lifecycle/**` nor `architecture/**` may be edited from this lane.
    Disclosed in the handoff; not fixed here."""
    connection, record, job, store, raised = _escalated_job_with_a_real_open_row()
    real_client = RealEscalationClient(store)
    deps = _deps_for_12b(connection, record, job=job, escalation_client=real_client)

    try:
        escalation.decide(
            raised.id,
            "human-reviewer",
            "reviewed on GitHub",
            "changes_requested",
            store=store,
            record=record,
            jobs=FakeJobs(job),
            lifecycle=RealLifecycle(),
            deps=deps,
        )
    except LifecycleError as exc:
        assert "0 open escalations exist" in str(exc)
    else:
        raise AssertionError(
            "the disclosed defect was not reproduced — if `rqa/lifecycle/resume.py` or "
            "`code/P-11-escalation.md` §3's step order changed, update the disclosure "
            "in the lane handoff and this test together"
        )
