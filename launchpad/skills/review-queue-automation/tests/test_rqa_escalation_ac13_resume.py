#!/usr/bin/env python3
"""AC13 clause 3, end to end: the REAL `rqa.lifecycle.resume()` wired to a REAL
`rqa.escalation` store — `code/P-11-escalation.md`'s AC13, and the lane prompt's
"AC13 clause 3" instruction.

No pytest: every `test_*` function takes no arguments, per `tests/run_all.py`.

**Import boundary.** P-11 §1 forbids `rqa.escalation` from importing P-02's
implementation, and P-02 §1 forbids `rqa.lifecycle` from importing `rqa.escalation`.
This file imports both — it is the wiring test the lane prompt asks for, and it is the
one place that wiring is allowed to exist: never inside either package's own source.

**What this file proves.** D-B5-2 used to live here as a pinned red: `resume()` derived
"the open escalation this decision answers" from `deps.escalation.pending(store=...)`,
which only ever returns `status = 'open'` rows (`code/P-11-escalation.md` §5), while
`decide()`'s own step order — §3 steps 11-13 — closes the row (`store.close`, step 12)
*before* calling `lifecycle.resume` (step 13). Both steps run against the identical
`EscalationStore`/`sqlite3.Connection` in production (P-01 wires one `human_requests`
table per state directory), so every successful `decide()` raised `LifecycleError`
instead of completing, for every cause.

That is fixed on P-02's side: `resume` now recovers the escalation from the
`escalation` record entry P-11 appends at `raise_` step 4 (§6) — a read
`code/P-02-lifecycle.md` §7 already permits, unlike the `human_requests` content read
`pending()` performs — so `decide()`'s step order is no longer observable to it.
`test_the_real_round_trip_through_decide_completes` is the former red, flipped: same
setup, now asserting the round trip succeeds. `rqa/lifecycle/resume.py` keeps the
step-order guarantee honest from the other side, and
`tests/test_rqa_lifecycle_resume_from_record.py` covers all five causes and both
branches.

`test_the_real_resume_resumes_at_the_recorded_step_without_restarting_the_review` proves
the rest of AC13 clause 3: called directly, the REAL `rqa.lifecycle.resume()` transitions
the job directly from `ESCALATED` to its recorded resting status — no re-entry into
planning or judgement — using this package's real store and its real `raise_()`, not a
fake.
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


# -- AC13 clause 3, direct --------------------------------------------------------


def test_the_real_resume_resumes_at_the_recorded_step_without_restarting_the_review() -> None:
    """`rqa.lifecycle.resume()`, called directly against a real, genuinely-persisted
    escalation, transitions `ESCALATED -> CHANGES_REQUESTED` directly. `transitions()`
    shows only the original `queued` arrival and the direct resume outcome: no
    `planned`/`reviewing`/`judged` entry exists, so nothing re-entered planning or
    judgement — the review was resumed, not restarted.

    The `human_requests` row is still open here only because `decide()` has not run;
    `resume` itself no longer cares either way, which is the whole of the D-B5-2 fix."""
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
        "resume() left the operator's queue exactly as it found it: closing the row is "
        "decide()'s step 12, never resume's"
    )


# -- The former red: the real round trip through decide(), now completing ---------


def test_the_real_round_trip_through_decide_completes() -> None:
    """The D-B5-2 regression guard, flipped. `decide()` follows
    `code/P-11-escalation.md` §3 literally — step 12 (`store.close`) before step 13
    (`lifecycle.resume`) — so by the time the REAL `rqa.lifecycle.resume()` runs, the
    `human_requests` row it is answering is already closed and `pending()` no longer
    lists it. `resume` reads the `escalation` record entry instead (§6), which step 12
    does not touch, so the round trip completes: a `Decision` is returned and the job
    rests at the outcome the human recorded.

    This test was written red on purpose by the lane that landed P-11, to pin the defect
    until a fix on one side or the other arrived. It is now green, and it fails again the
    moment `resume` goes back to deriving its escalation from an ordering-sensitive
    source."""
    connection, record, job, store, raised = _escalated_job_with_a_real_open_row()
    real_client = RealEscalationClient(store)
    deps = _deps_for_12b(connection, record, job=job, escalation_client=real_client)

    result = escalation.decide(
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

    assert isinstance(result, Decision)
    assert result.outcome == "changes_requested"
    assert stored_status(connection, job.id) == "changes_requested"
    assert transitions(connection, job.id) == ["queued", "changes_requested"]
    closed = store.get(raised.id)
    assert closed is not None and closed.status == "closed"
    assert escalation.pending(store=store) == ()
