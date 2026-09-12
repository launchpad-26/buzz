#!/usr/bin/env python3
"""Append propagation and malformed/invalid-input rows — `code/P-07-judgement.md`
§8 rows T15-T16.
"""

from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import test_rqa_judgement_fixtures as fx  # noqa: E402
from rqa.contracts import AppendFailed, Category, EvidenceState, Location  # noqa: E402
from rqa.judgement.judge import JudgementError, judge  # noqa: E402


# -- T15 ------------------------------------------------------------------------


def test_t15_an_append_failure_propagates() -> None:
    record = fx.FakeRecord(fail_kind="judgement")
    try:
        judge(
            job=fx.make_job(), plan=fx.make_plan(obligations=("O1",)),
            panel=fx.make_panel(attempts=(fx.make_attempt(),)), carry=fx.make_carry(),
            facts=fx.make_facts(), snapshot=fx.make_snapshot(), decision=None, record=record,
        )
    except AppendFailed:
        pass
    else:
        raise AssertionError("AppendFailed must propagate out of judge()")


# -- T16 ------------------------------------------------------------------------


def test_t16_an_incomplete_panel_raises_and_appends_nothing() -> None:
    record = fx.FakeRecord()
    panel = fx.make_panel(complete=False, incomplete_reason="exhausted")
    try:
        judge(
            job=fx.make_job(), plan=fx.make_plan(), panel=panel, carry=fx.make_carry(),
            facts=fx.make_facts(), snapshot=fx.make_snapshot(), decision=None, record=record,
        )
    except JudgementError:
        pass
    else:
        raise AssertionError("an incomplete panel must raise JudgementError")
    assert record.entries == []


def test_t16_a_missing_evidence_cutoff_raises_and_appends_nothing() -> None:
    record = fx.FakeRecord()
    panel = fx.make_panel(evidence_cutoff=None)
    try:
        judge(
            job=fx.make_job(), plan=fx.make_plan(), panel=panel, carry=fx.make_carry(),
            facts=fx.make_facts(), snapshot=fx.make_snapshot(), decision=None, record=record,
        )
    except JudgementError:
        pass
    else:
        raise AssertionError("a missing panel.evidence_cutoff must raise JudgementError")
    assert record.entries == []


def test_t16_a_complete_panel_with_a_contradictory_incomplete_reason_raises() -> None:
    record = fx.FakeRecord()
    panel = fx.make_panel(complete=True, incomplete_reason="exhausted")
    try:
        judge(
            job=fx.make_job(), plan=fx.make_plan(), panel=panel, carry=fx.make_carry(),
            facts=fx.make_facts(), snapshot=fx.make_snapshot(), decision=None, record=record,
        )
    except JudgementError:
        pass
    else:
        raise AssertionError(
            "panel.complete is True with a non-None incomplete_reason must raise JudgementError"
        )
    assert record.entries == []


def test_t16_a_duplicate_id_within_carry_reused_itself_raises() -> None:
    record = fx.FakeRecord()
    carry = fx.make_carry(
        reused=(
            fx.make_carried(obligation_id="O1", source_judgement_seq=3),
            fx.make_carried(obligation_id="O1", source_judgement_seq=4),
        )
    )
    try:
        judge(
            job=fx.make_job(), plan=fx.make_plan(obligations=()), panel=fx.make_panel(attempts=()),
            carry=carry, facts=fx.make_facts(), snapshot=fx.make_snapshot(), decision=None, record=record,
        )
    except JudgementError:
        pass
    else:
        raise AssertionError("a duplicate obligation id within carry.reused must raise JudgementError")
    assert record.entries == []


def test_t16_a_duplicate_id_between_plan_and_carry_raises_and_appends_nothing() -> None:
    record = fx.FakeRecord()
    plan = fx.make_plan(obligations=("O1",))
    carry = fx.make_carry(reused=(fx.make_carried(obligation_id="O1"),))
    try:
        judge(
            job=fx.make_job(), plan=plan, panel=fx.make_panel(attempts=()), carry=carry,
            facts=fx.make_facts(), snapshot=fx.make_snapshot(), decision=None, record=record,
        )
    except JudgementError:
        pass
    else:
        raise AssertionError("plan/carry ids sharing an obligation id must raise JudgementError")
    assert record.entries == []


def test_t16_a_duplicate_id_within_the_plan_itself_raises() -> None:
    record = fx.FakeRecord()
    plan = fx.make_plan(obligations=("O1", "O1"))
    try:
        judge(
            job=fx.make_job(), plan=plan, panel=fx.make_panel(attempts=()), carry=fx.make_carry(),
            facts=fx.make_facts(), snapshot=fx.make_snapshot(), decision=None, record=record,
        )
    except JudgementError:
        pass
    else:
        raise AssertionError("a duplicate id within plan.obligations must raise JudgementError")
    assert record.entries == []


def test_t16_a_malformed_finding_raises_and_appends_nothing() -> None:
    record = fx.FakeRecord()
    malformed = fx.make_finding(
        finding_id="FA", categories=frozenset({Category.CORRECTNESS}),
        location=Location(path="", line=None), source_attempt="att-1",
    )
    attempt = fx.make_attempt(
        attempt_id="att-1",
        outcome=fx.make_verdict(obligations={"O1": EvidenceState.VERIFIED}, findings=(malformed,)),
    )
    try:
        judge(
            job=fx.make_job(), plan=fx.make_plan(obligations=("O1",)),
            panel=fx.make_panel(attempts=(attempt,)), carry=fx.make_carry(),
            facts=fx.make_facts(), snapshot=fx.make_snapshot(), decision=None, record=record,
        )
    except JudgementError:
        pass
    else:
        raise AssertionError("a malformed finding (empty location path) must raise JudgementError")
    assert record.entries == []


def test_t16_a_decision_naming_an_obligation_outside_the_universe_raises() -> None:
    record = fx.FakeRecord()
    decision = fx.make_decision(substantiates="not-in-universe", outcome="approved")
    try:
        judge(
            job=fx.make_job(), plan=fx.make_plan(obligations=("O1",)), panel=fx.make_panel(attempts=()),
            carry=fx.make_carry(), facts=fx.make_facts(), snapshot=fx.make_snapshot(),
            decision=decision, record=record,
        )
    except JudgementError:
        pass
    else:
        raise AssertionError("a decision outside the obligation universe must raise JudgementError")
    assert record.entries == []


def test_facts_that_do_not_identify_the_job_raise() -> None:
    from dataclasses import replace

    record = fx.FakeRecord()
    mismatched_job = replace(fx.make_job(), head_sha="c" * 40)
    try:
        judge(
            job=mismatched_job, plan=fx.make_plan(obligations=("O1",)), panel=fx.make_panel(attempts=()),
            carry=fx.make_carry(), facts=fx.make_facts(), snapshot=fx.make_snapshot(),
            decision=None, record=record,
        )
    except JudgementError:
        pass
    else:
        raise AssertionError("facts identifying a different job must raise JudgementError")
    assert record.entries == []
