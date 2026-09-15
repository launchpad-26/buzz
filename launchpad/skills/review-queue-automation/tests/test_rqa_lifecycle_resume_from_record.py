#!/usr/bin/env python3
"""D-B5-2: the REAL `rqa.escalation.decide()` driving the REAL `rqa.lifecycle.resume()`
over one real `SqliteEscalationStore` and one real record — for all five
`EscalationCause` values, so both resume branches are covered.

No pytest: every `test_*` function takes no arguments, per `tests/run_all.py`.

**Why this file exists.** `code/P-11-escalation.md` §3 fixes `decide()`'s order: step 12
`store.close(...)`, then step 13 `lifecycle.resume(...)`. §5 fixes `pending()` to
`status = 'open'` rows only. So any `resume` that re-derives "the escalation this
decision answers" from `pending()` finds nothing by the time it is called, and every
successful `decide()` raises instead of completing. That is exactly what
`rqa/lifecycle/resume.py` did until this file's fix: it is unobservable through
`tests/lifecycle_cascade_bench.py`'s `FakeEscalation`, whose `pending()` returns a
tuple the test constructed and which no `close()` affects, and only becomes visible when
one real `EscalationStore` sits on both sides of the same call.

**Import boundary.** `code/P-02-lifecycle.md` §1 forbids `rqa.lifecycle` from importing
`rqa.escalation` and `code/P-11-escalation.md` §1 forbids the reverse. A test may import
both: this is the wiring, and a test file is the only place the wiring may exist.

**What `resume` reads instead.** P-02 §7 permits `record_entries` and explicitly forbids
"the content of `human_requests` rows" — and `pending()` is a `human_requests` read
rendered as `Escalation` values. The `escalation` record entry P-11 appends at `raise_`
step 4 (§6) carries the four fields `resume` needs, and is inside P-02's permitted read
set. `test_resume_never_consults_pending` pins that direction so a future edit cannot
quietly restore the forbidden read.
"""

from __future__ import annotations

import dataclasses
import pathlib
import sys
from datetime import datetime, timezone

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from lifecycle_cascade_bench import (  # noqa: E402
    NOW,
    SNAP_HASH,
    FakeAuthority,
    FakeGithub,
    FakeLease,
    FakePolicy,
    RealJudgement,
    bench,
    make_deny,
    make_deps,
    make_facts,
    make_plan,
    make_review,
    make_snapshot,
    stored_status,
    transitions,
)

import rqa.escalation as escalation  # noqa: E402
from rqa.contracts import (  # noqa: E402
    Activity,
    Decision,
    EscalationCause,
    EscalationSubject,
    EscalationSubjectKind,
    JobStatus,
)
from rqa.escalation.store import SqliteEscalationStore  # noqa: E402
from rqa.lifecycle import resume  # noqa: E402

#: `raise_()` stamps `raised_at`, and the record writer stamps the entry's `at`, from the
#: real wall clock — neither takes an injectable clock (`code/P-11-escalation.md` §3).
#: `make_review`'s default `submitted_at` is relative to the bench's fixed historical
#: `NOW`, which any real clock outruns, so 12b's post-escalation bound would refuse it
#: for a date-dependent reason that is not the property under test. A fixed far-future
#: submission sidesteps that without weakening the bound itself, which
#: `tests/test_rqa_lifecycle_resume.py` exercises directly with a pinned clock.
_FAR_FUTURE = datetime(2100, 1, 1, tzinfo=timezone.utc)


class RealEscalationClient:
    """P-02's `EscalationClient` Protocol (`rqa/lifecycle/deps.py`), satisfied with
    P-11's actual `raise_`/`pending` over a real `SqliteEscalationStore`. `pending` stays
    on the client because `rqa/edges.py` declares E-11 as `raise_` *and* `pending`: the
    Protocol mirrors the edge, not P-02's current call sites."""

    def __init__(self, store: SqliteEscalationStore) -> None:
        self.store = store
        self.pending_calls = 0

    def raise_(self, *, job, cause, subject, question, context, record, store):
        return escalation.raise_(
            job=job, cause=cause, subject=subject, question=question, context=context,
            record=record, store=store
        )

    def pending(self, *, store):
        self.pending_calls += 1
        return escalation.pending(store=store)


class RealLifecycle:
    """`LifecycleResume` — `resume` is a free function; this is the smallest adapter
    that gives `decide()`'s `lifecycle.resume(...)` call something to resolve against."""

    def resume(self, *, job_id, decision, deps):
        return resume(job_id=job_id, decision=decision, deps=deps)


class FakeJobs:
    """`JobReader` — P-01's read-only `jobs` view, faked exactly as P-11's own tests
    fake it; `decide()`'s steps 7-8 freshness check is not what this file proves."""

    def __init__(self, job) -> None:
        self.job = job

    def current(self, job_id):
        return self.job


def _escalated(cause: EscalationCause):
    """An escalated job with one real, open `human_requests` row and the matching real
    `escalation` record entry — both written by P-11's own `raise_()`.

    A 12a cause also gets the recorded `plan` and complete `panel` §3.3's reconstruction
    reads; 12b reconstructs nothing.
    """
    connection, record, job = bench(status=JobStatus.ESCALATED, snapshot_hash=SNAP_HASH)
    record.append(job.id, "transition", {
        "from_state": None, "to_state": "queued", "reason": "arrival", "repo": job.repo,
        "number": job.number, "head_sha": job.head_sha, "base_sha": job.base_sha,
        "predecessor_job": None,
    })
    if cause is not EscalationCause.AUTHORITY_REQUIREMENT:
        record.append(job.id, "plan", dataclasses.asdict(make_plan()))
        record.append(job.id, "panel", {
            "attempts": [], "complete": True, "incomplete_reason": None,
            "evidence_cutoff": NOW.isoformat(), "bound_reached": False,
        })
    connection.commit()

    store = SqliteEscalationStore(connection)
    raised = escalation.raise_(
        job=job,
        cause=cause,
        subject=EscalationSubject(
            EscalationSubjectKind.AUTHORITY
            if cause is EscalationCause.AUTHORITY_REQUIREMENT
            else EscalationSubjectKind.OBLIGATION,
            "merge" if cause is EscalationCause.AUTHORITY_REQUIREMENT else "ob-1",
        ),
        question="a specific question only a human can answer",
        # 12a: `decide()` reads `context['obligation']` into `Decision.substantiates`,
        # which is what lets the real judge settle the gap this escalation names.
        context={} if cause is EscalationCause.AUTHORITY_REQUIREMENT else {"obligation": "ob-1"},
        record=record,
        store=store,
    )
    connection.commit()
    return connection, record, job, store, raised


def _deps(connection, record, job, escalation_client, *, reviews=()):
    lease = FakeLease()
    return make_deps(
        connection,
        record,
        policy=FakePolicy(make_snapshot()),
        authority=FakeAuthority({Activity.MERGE: [make_deny(Activity.MERGE)]}),
        judgement=RealJudgement(),
        github=FakeGithub(facts=make_facts(job=job, reviews=reviews)),
        escalation=escalation_client,
        claim_lease=lease.claim,
        release_lease=lease.release,
    )


def _round_trip(cause: EscalationCause, *, escalation_client=None):
    """One real `decide()` answering one real escalation of `cause`."""
    connection, record, job, store, raised = _escalated(cause)
    client = escalation_client(store) if escalation_client is not None else RealEscalationClient(store)
    authority = cause is EscalationCause.AUTHORITY_REQUIREMENT
    deps = _deps(
        connection, record, job, client,
        reviews=(
            (make_review(outcome="changes_requested", submitted_at=_FAR_FUTURE),)
            if authority
            else ()
        ),
    )
    result = escalation.decide(
        raised.id,
        "human-reviewer",
        "reviewed on GitHub",
        "changes_requested" if authority else None,
        store=store,
        record=record,
        jobs=FakeJobs(job),
        lifecycle=RealLifecycle(),
        deps=deps,
    )
    return connection, job, client, result


#: The one resting state each branch reaches through a *real* `decide()`, and the exact
#: transition sequence behind it.
#:
#: 12b (`authority_requirement`) admits the human's own recorded GitHub outcome and
#: transitions straight to it — no re-judgement, so no `judged` row.
#:
#: 12a is bounded by `decide()`'s own step 3: an outcome may only be recorded against
#: `authority_requirement` (`code/P-11-escalation.md` §3), so a 12a `Decision` always
#: carries `outcome=None`, and `rqa/judgement/evidence.py`'s
#: `resolve_obligation_state` only lets a decision settle an obligation when its outcome
#: is not `None`. A 12a decision therefore substantiates without deciding, the real judge
#: re-judges the reconstructed panel on its evidence alone, that evidence is still
#: unknown, and it escalates again — the `judged` row proves 12a's re-entry ran, and
#: `escalated` is the only state this reconstruction can rest at. That is P-07/P-11
#: semantics, not this defect: what this file proves is that `resume` *completes* its
#: branch instead of raising before either branch is chosen.
_RESTING = {
    EscalationCause.AUTHORITY_REQUIREMENT: (
        "changes_requested", ["queued", "changes_requested"],
    ),
}
_TWELVE_A_RESTING = ("escalated", ["queued", "judged", "escalated"])


def _expected(cause: EscalationCause):
    return _RESTING.get(cause, _TWELVE_A_RESTING)


def test_a_real_decide_completes_for_every_escalation_cause() -> None:
    """The defect's direct proof. `decide()` closes the `human_requests` row at step 12
    and resumes at step 13; `resume` must still recover the escalation it is answering.
    All five causes, so both branches: `authority_requirement` takes 12b, the other four
    take 12a.

    Each cause asserts exactly one resting status and the exact transition sequence
    behind it — not merely "did not raise" — so a fix that resumed into the wrong branch
    would still fail here."""
    seen = set()
    for cause in EscalationCause:
        connection, job, _, result = _round_trip(cause)
        seen.add(cause)
        assert isinstance(result, Decision), (
            f"{cause.value}: decide() returned {type(result).__name__}, not a Decision"
        )
        status, sequence = _expected(cause)
        assert stored_status(connection, job.id) == status, cause.value
        assert transitions(connection, job.id) == sequence, cause.value
    assert seen == set(EscalationCause), "every cause in the closed vocabulary was driven"


def test_a_real_decide_closes_the_escalation_it_answered() -> None:
    """Step 12's `close` and step 13's resume act on the same durable state: the answered
    row is closed once the round trip completes, so nothing invites a second answer to a
    question already answered. Asserted on that row by id rather than on the whole queue,
    because a 12a re-judgement legitimately opens a *new* escalation of its own."""
    for cause in EscalationCause:
        _, _, client, _ = _round_trip(cause)
        answered = client.store.get(1)
        assert answered is not None and answered.status == "closed", cause.value


def test_resume_never_consults_pending() -> None:
    """`code/P-02-lifecycle.md` §7: this part "does not read ... the content of
    `human_requests` rows". `pending()` is precisely that read, rendered as `Escalation`
    values, so `resume` recovering its escalation through it was a §7 violation as well
    as an ordering bug. An `EscalationClient` whose `pending` refuses to answer proves
    the read is gone rather than merely unnecessary — while `raise_` on the same client
    keeps working, because 12a's re-escalation still needs it."""

    class PendingRefuses(RealEscalationClient):
        def pending(self, *, store):
            raise AssertionError(
                "resume() read human_requests through pending(); P-02 §7 forbids it"
            )

    for cause in EscalationCause:
        connection, job, _, result = _round_trip(cause, escalation_client=PendingRefuses)
        assert isinstance(result, Decision)
        status, _ = _expected(cause)
        assert stored_status(connection, job.id) == status, cause.value


def test_second_real_decision_resumes_the_latest_escalation():
    """A resolved evidence question leads to an authority question, then an outcome.

    Only the judgement/remote facts are controlled. Both escalation entries,
    decisions, resume calls and transitions use production code and real SQLite.
    Selecting the oldest escalation takes 12a again and fails the final state check.
    """
    from lifecycle_cascade_bench import FakeJudgement, make_judgement
    connection, record, job, store, first = _escalated(EscalationCause.EVIDENCE_GAP)
    client = RealEscalationClient(store)
    deps = _deps(connection, record, job, client, reviews=(
        make_review(outcome="changes_requested", submitted_at=_FAR_FUTURE),
    ))
    deps = dataclasses.replace(deps,
        judgement=FakeJudgement(make_judgement()),
        authority=FakeAuthority({
            Activity.APPROVE: [make_deny(Activity.APPROVE)],
            Activity.COMMENT: [make_deny(Activity.COMMENT)],
        }),
    )
    try:
        escalation.decide(first.id, "human-reviewer", "supplied the missing evidence",
            store=store, record=record, jobs=FakeJobs(job), lifecycle=RealLifecycle(), deps=deps)
        connection.commit()
        second, = escalation.pending(store=store)
        assert second.id != first.id and second.cause is EscalationCause.AUTHORITY_REQUIREMENT
        assert store.get(first.id).status == "closed"
        escalation.decide(second.id, "human-reviewer", "reviewed on GitHub", "changes_requested",
            store=store, record=record, jobs=FakeJobs(job), lifecycle=RealLifecycle(), deps=deps)
        connection.commit()
        assert store.get(second.id).status == "closed"
        assert escalation.pending(store=store) == ()
        assert stored_status(connection, job.id) == "changes_requested"
        assert connection.execute("SELECT count(*) FROM record_entries WHERE kind='escalation'").fetchone()[0] == 2
        assert connection.execute("SELECT count(*) FROM record_entries WHERE kind='decision'").fetchone()[0] == 2
    finally:
        connection.close()
