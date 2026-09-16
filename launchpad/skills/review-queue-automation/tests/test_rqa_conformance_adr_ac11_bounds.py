#!/usr/bin/env python3
"""Task #2216 — AC11/RQA-FR-039's executable half: a configured resource bound
reached produces a fallback, an explicitly incomplete review or an escalation, and
the run's disposition is never successful — even when a fallback route returned a
valid verdict.

AC11 names no ADR; the deciding texts are PRD #2006's AC11 and RQA-FR-039 ("never
manufacture a successful outcome"), implemented across P-05 (`reserve`), P-06 (the
panel's latched `bound_reached`) and P-07 (judgement step 9/10).

These tests drive the REAL `reserve()` and the REAL `judge()`; the stop test drives
the REAL lifecycle step 7. The composed system cannot reach any of them today
(#2274 and F-2 deny REVIEW before a plan exists) — `TESTING.md` Part 2 §11.5
records that block; nothing here routes around it.
"""

from __future__ import annotations

import pathlib
import sys
from dataclasses import replace
from datetime import datetime

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from lifecycle_cascade_bench import (  # noqa: E402
    CarryOver,
    FakeHarness,
    FakeJudgement,
    FakeSupply,
    bench,
    make_facts,
    make_panel,
    make_plan,
    make_snapshot,
    make_deps,
    stored_status,
)

from rqa.contracts import (  # noqa: E402
    Budget,
    EscalationCause,
    EscalationSubject,
    EscalationSubjectKind,
    JobStatus,
    Refusal,
    Reservation,
)
from rqa.judgement import judge  # noqa: E402
from rqa.lifecycle.states import DISPOSITION, Disposition, as_status  # noqa: E402
from rqa.lifecycle.steps import Cascade, step7  # noqa: E402
from rqa.supply.budget import TOKENS_PER_PARTICIPANT, reserve  # noqa: E402


class _FakeSpend:
    """The spend counters `reserve()` compares each axis against."""

    def __init__(self, *, pr: int = 0, repo: int = 0, model: int = 0) -> None:
        self._pr, self._repo, self._model = pr, repo, model

    def pr_total(self, repo: str, number: int) -> int:
        return self._pr

    def repo_total_since(self, repo: str, since: datetime) -> int:
        return self._repo

    def model_total_since(self, model: str, since: datetime) -> int:
        return self._model


def _reserve(*, budget: Budget, spend: _FakeSpend):
    from lifecycle_cascade_bench import make_job, make_route

    snapshot = replace(make_snapshot(), budget=budget)
    return reserve(
        job=make_job(),
        plan=make_plan(),
        route=make_route("alpha"),
        snapshot=snapshot,
        spend=spend,
    )


def test_ac11_a_shared_axis_bound_reached_is_an_explicitly_incomplete_review() -> None:
    """The PR axis is shared by every model, so no fallback escapes it: the refusal's
    downgrade is `incomplete` — an explicitly incomplete review, never a success.
    The bound is inclusive: equality refuses."""
    attempt_tokens = make_plan().participants * TOKENS_PER_PARTICIPANT
    outcome = _reserve(
        budget=Budget(per_pr_tokens=attempt_tokens, per_repo_daily_tokens=None,
                      per_model_daily_tokens=None),
        spend=_FakeSpend(pr=0),
    )
    assert isinstance(outcome, Refusal), outcome
    assert outcome.downgrade == "incomplete"
    assert outcome.axis == "per_pr_tokens"


def test_ac11_the_model_axis_bound_produces_a_fallback_instead() -> None:
    """Only the model axis has a per-route escape — a different configured route has
    a separate model cap — so it, and only it, downgrades to `fallback` (AC12)."""
    attempt_tokens = make_plan().participants * TOKENS_PER_PARTICIPANT
    outcome = _reserve(
        budget=Budget(per_pr_tokens=None, per_repo_daily_tokens=None,
                      per_model_daily_tokens=attempt_tokens),
        spend=_FakeSpend(model=0),
    )
    assert isinstance(outcome, Refusal), outcome
    assert outcome.downgrade == "fallback"
    assert outcome.axis == "per_model_daily_tokens"


def test_ac11_a_bound_under_the_attempt_ceiling_reserves() -> None:
    """The detector's other half: one token of headroom above the attempt ceiling
    reserves. If this fails while the equality twin refuses, the gate is not
    measuring the bound."""
    attempt_tokens = make_plan().participants * TOKENS_PER_PARTICIPANT
    outcome = _reserve(
        budget=Budget(per_pr_tokens=attempt_tokens + 1, per_repo_daily_tokens=None,
                      per_model_daily_tokens=None),
        spend=_FakeSpend(pr=0),
    )
    assert isinstance(outcome, Reservation), outcome


def _judged(*, bound_reached: bool):
    connection, record, job = bench()
    return judge(
        job=job,
        plan=make_plan(),
        panel=make_panel(bound_reached=bound_reached),
        carry=CarryOver(reused=(), regenerated=("ob-1",),
                        reasons={"ob-1": "no_predecessor"}, source_job=None),
        facts=make_facts(job=job),
        snapshot=make_snapshot(),
        decision=None,
        record=record,
    )


def test_ac11_a_reached_bound_is_never_a_successful_disposition() -> None:
    """AC11's sharpest clause: the panel completed through a fallback and every
    verdict is valid and verified — and the disposition is STILL not `approve`,
    because `bound_reached` latched. The run escalates with the named cause."""
    judgement = _judged(bound_reached=True)
    assert judgement.disposition != "approve"
    assert judgement.disposition == "escalate"
    assert (
        EscalationCause.EVIDENCE_GAP,
        EscalationSubject(EscalationSubjectKind.ASSURANCE, "panel-budget"),
        "panel reservation bound was reached",
    ) in judgement.escalation_causes


def test_ac11_the_same_panel_without_the_bound_approves() -> None:
    """The mutation twin, in-file: identical evidence, `bound_reached=False`, and the
    disposition is `approve`. Together with the test above this proves the refusal
    turns on the bound and on nothing else."""
    judgement = _judged(bound_reached=False)
    assert judgement.disposition == "approve"


def test_ac11_a_budget_incomplete_panel_stops_and_is_not_review_complete() -> None:
    """When no fallback exists the panel comes back explicitly incomplete
    (`incomplete_reason="budget"`); the REAL step 7 stops the job without ever
    calling judgement, and `stopped` maps to "unable to progress" — an FR-016
    answer that is not review-complete."""
    connection, record, job = bench(status=JobStatus.REVIEWING)
    deps = make_deps(
        connection,
        record,
        harness=FakeHarness(run_result=make_panel(
            attempts=(), complete=False, incomplete_reason="budget", bound_reached=True,
        )),
        supply=FakeSupply(),
        judgement=FakeJudgement(FakeJudgement.JUDGE_FORBIDDEN),
    )
    ctx = Cascade(
        deps=deps,
        facts=make_facts(job=job),
        snapshot=make_snapshot(),
        plan=make_plan(),
        carry=CarryOver(reused=(), regenerated=("ob-1",),
                        reasons={"ob-1": "no_predecessor"}, source_job=None),
    )

    step7(job, ctx)

    assert stored_status(connection, job.id) == "stopped"
    disposition = DISPOSITION[as_status("stopped")]
    assert disposition is Disposition.UNABLE_TO_PROGRESS
    assert disposition is not Disposition.REVIEW_COMPLETE
