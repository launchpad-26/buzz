#!/usr/bin/env python3
"""`rqa.judgement.judge` — `code/P-07-judgement.md` §8 rows T1-T7c.

Obligation-universe resolution, cutoff-bounded validation, carry-over
materialisation, captured-check attribution, and the `bound_reached`
escalation. Findings/corroboration/synthetic-finding rows (T8-T14), append
propagation and malformed-input rows (T15-T16) live in
`test_rqa_judgement_findings.py` and `test_rqa_judgement_record.py`.
"""

from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import test_rqa_judgement_fixtures as fx  # noqa: E402
from rqa.contracts import AttemptFailure, CheckConclusion, CheckRun, EvidenceState  # noqa: E402
from rqa.judgement import render  # noqa: E402
from rqa.judgement.judge import JudgementError, judge  # noqa: E402


# -- T1 ---------------------------------------------------------------------


def test_t1_identical_complete_inputs_twice_are_byte_identical() -> None:
    def _run():
        job = fx.make_job()
        facts = fx.make_facts()
        plan = fx.make_plan(obligations=("O1",))
        snapshot = fx.make_snapshot()
        carry = fx.make_carry()
        attempt = fx.make_attempt(outcome=fx.make_verdict(obligations={"O1": EvidenceState.VERIFIED}))
        panel = fx.make_panel(attempts=(attempt,))
        record = fx.FakeRecord()
        result = judge(
            job=job, plan=plan, panel=panel, carry=carry, facts=facts,
            snapshot=snapshot, decision=None, record=record,
        )
        return result, record

    j1, record1 = _run()
    j2, record2 = _run()
    assert j1 == j2
    assert render(j1) == render(j2)
    assert record1.of_kind("judgement") == record2.of_kind("judgement")


# -- T2 ---------------------------------------------------------------------


def test_t2_a_policy_obligation_omitted_by_the_plan_is_absent_from_the_judgement() -> None:
    policy_obligations = (fx.make_obligation(obligation_id="O1"), fx.make_obligation(obligation_id="OX"))
    snapshot = fx.make_snapshot(policy=fx.make_policy(obligations=policy_obligations, assurance={"standard": 1}))
    plan = fx.make_plan(obligations=("O1",))
    attempt = fx.make_attempt(outcome=fx.make_verdict(obligations={"O1": EvidenceState.VERIFIED}))
    panel = fx.make_panel(attempts=(attempt,))
    result = judge(
        job=fx.make_job(), plan=plan, panel=panel, carry=fx.make_carry(), facts=fx.make_facts(),
        snapshot=snapshot, decision=None, record=fx.FakeRecord(),
    )
    assert "OX" not in result.obligations
    assert set(result.obligations) == {"O1"}
    assert result.assurance.required == 1
    assert result.assurance.achieved == 1


# -- T3 -----------------------------------------------------------------------


def test_t3_an_attempt_ending_after_the_cutoff_raises_and_appends_nothing() -> None:
    late_attestation = fx.make_attestation(ended_at=fx.AFTER_CUTOFF)
    attempt = fx.make_attempt(attestation=late_attestation)
    panel = fx.make_panel(attempts=(attempt,), evidence_cutoff=fx.CUTOFF)
    record = fx.FakeRecord()
    try:
        judge(
            job=fx.make_job(), plan=fx.make_plan(), panel=panel, carry=fx.make_carry(),
            facts=fx.make_facts(), snapshot=fx.make_snapshot(), decision=None, record=record,
        )
    except JudgementError:
        pass
    else:
        raise AssertionError("a late attempt must raise JudgementError")
    assert record.entries == []


def test_p07_002_a_late_attemptfailure_raises_and_appends_nothing() -> None:
    """Round-2 regression test for P07-002: the cutoff check in `_validate`
    must run for every attempt regardless of outcome type, so a late
    `AttemptFailure` — not just a late `Verdict` (T3, above) — is the exact
    case the reordering bug let through undetected."""
    late_attestation = fx.make_attestation(ended_at=fx.AFTER_CUTOFF)
    attempt = fx.make_attempt(
        attestation=late_attestation, outcome=AttemptFailure(kind="TRANSIENT", detail="timeout")
    )
    panel = fx.make_panel(attempts=(attempt,), evidence_cutoff=fx.CUTOFF)
    record = fx.FakeRecord()
    try:
        judge(
            job=fx.make_job(), plan=fx.make_plan(), panel=panel, carry=fx.make_carry(),
            facts=fx.make_facts(), snapshot=fx.make_snapshot(), decision=None, record=record,
        )
    except JudgementError:
        pass
    else:
        raise AssertionError("a late AttemptFailure must raise JudgementError")
    assert record.entries == []


# -- T4 -----------------------------------------------------------------------


def test_t4_empty_panel_with_complete_carried_evidence_approves_and_records_the_cutoff() -> None:
    carry = fx.make_carry(reused=(fx.make_carried(obligation_id="O1"),))
    plan = fx.make_plan(obligations=())
    panel = fx.make_panel(attempts=(), evidence_cutoff=fx.CUTOFF)
    facts = fx.make_facts(fetched_at=fx.CUTOFF)
    record = fx.FakeRecord()
    result = judge(
        job=fx.make_job(), plan=plan, panel=panel, carry=carry, facts=facts,
        snapshot=fx.make_snapshot(policy=fx.make_policy(assurance={"standard": 1})),
        decision=None, record=record,
    )
    assert result.disposition == "approve"
    assert result.obligations == {"O1": EvidenceState.VERIFIED}
    assert result.reused_from == "job-0"
    payload = record.of_kind("judgement")[0]
    assert payload["cutoff"] == fx.CUTOFF.isoformat()

# -- #2236 interim (see judge.py's docstring at the `reused_from` assignment) --


def test_2236_reused_from_is_a_bare_job_id_while_the_source_sequence_survives_per_obligation() -> None:
    """Pins the accepted interim `CONTRACTS.md` §6 leaves until #2236 lands:
    `Judgement.reused_from` names only the predecessor job, never a
    `(job, seq)` pair, while each carried item's own `source_judgement_seq`
    is not lost — it survives into the `judgement` record's
    `carried_provenance`, keyed by obligation id.
    """
    carried = fx.make_carried(obligation_id="O1", source_job="job-0", source_judgement_seq=7)
    carry = fx.make_carry(reused=(carried,))
    record = fx.FakeRecord()
    result = judge(
        job=fx.make_job(), plan=fx.make_plan(obligations=()), panel=fx.make_panel(attempts=()),
        carry=carry, facts=fx.make_facts(), snapshot=fx.make_snapshot(), decision=None, record=record,
    )
    assert result.reused_from == "job-0"
    assert not isinstance(result.reused_from, tuple)
    payload = record.of_kind("judgement")[0]
    assert payload["reused_from"] == "job-0"
    assert payload["carried_provenance"]["O1"]["source_judgement_seq"] == 7
    assert payload["carried_provenance"]["O1"]["source_job"] == "job-0"


# -- T5 -----------------------------------------------------------------------


def test_t5_a_required_obligation_with_no_positive_evidence_is_unknown_and_not_approved() -> None:
    plan = fx.make_plan(obligations=("O1",))
    panel = fx.make_panel(attempts=())  # nobody reported on O1 at all
    result = judge(
        job=fx.make_job(), plan=plan, panel=panel, carry=fx.make_carry(), facts=fx.make_facts(),
        snapshot=fx.make_snapshot(), decision=None, record=fx.FakeRecord(),
    )
    assert result.obligations["O1"] is EvidenceState.UNKNOWN
    assert result.disposition != "approve"


# -- T6 -----------------------------------------------------------------------


def test_t6_evidence_depending_only_on_a_pending_check_is_incomplete_and_not_attributed() -> None:
    pending_check = CheckRun(
        name="ci/pending", conclusion=CheckConclusion.PENDING, sha=fx.HEAD_SHA, observed_at=fx.BEFORE_CUTOFF
    )
    facts = fx.make_facts(checks=(pending_check,))
    attempt = fx.make_attempt(outcome=fx.make_verdict(obligations={"O1": EvidenceState.INCOMPLETE}))
    panel = fx.make_panel(attempts=(attempt,))
    result = judge(
        job=fx.make_job(), plan=fx.make_plan(obligations=("O1",)), panel=panel, carry=fx.make_carry(),
        facts=facts, snapshot=fx.make_snapshot(), decision=None, record=fx.FakeRecord(),
    )
    assert result.obligations["O1"] is EvidenceState.INCOMPLETE
    assert "ci/pending" not in result.attribution
    assert result.corroborated == frozenset()
    assert result.blocking == frozenset()


# -- T7 -----------------------------------------------------------------------


def test_t7_a_check_failing_at_head_and_base_is_inherited_and_a_pending_check_is_ignored() -> None:
    head_checks = (
        CheckRun(name="ci/x", conclusion=CheckConclusion.FAILURE, sha=fx.HEAD_SHA, observed_at=fx.BEFORE_CUTOFF),
        CheckRun(name="ci/y", conclusion=CheckConclusion.PENDING, sha=fx.HEAD_SHA, observed_at=fx.BEFORE_CUTOFF),
    )
    base_checks = (
        CheckRun(name="ci/x", conclusion=CheckConclusion.FAILURE, sha=fx.BASE_SHA, observed_at=fx.BEFORE_CUTOFF),
    )
    facts = fx.make_facts(checks=head_checks, base_checks=base_checks)
    result = judge(
        job=fx.make_job(), plan=fx.make_plan(obligations=("O1",)),
        panel=fx.make_panel(attempts=(fx.make_attempt(),)), carry=fx.make_carry(),
        facts=facts, snapshot=fx.make_snapshot(), decision=None, record=fx.FakeRecord(),
    )
    assert result.attribution == {"ci/x": "inherited"}
    assert "ci/y" not in result.attribution


def test_t7_an_inherited_failing_check_cannot_corroborate_a_single_family_finding() -> None:
    head_checks = (
        CheckRun(name="ci/x", conclusion=CheckConclusion.FAILURE, sha=fx.HEAD_SHA, observed_at=fx.BEFORE_CUTOFF),
    )
    base_checks = (
        CheckRun(name="ci/x", conclusion=CheckConclusion.FAILURE, sha=fx.BASE_SHA, observed_at=fx.BEFORE_CUTOFF),
    )
    facts = fx.make_facts(checks=head_checks, base_checks=base_checks)
    finding = fx.make_finding(finding_id="F1", evidence="failure caused by ci/x", source_attempt="att-1")
    attempt = fx.make_attempt(
        attempt_id="att-1",
        outcome=fx.make_verdict(obligations={"O1": EvidenceState.VERIFIED}, findings=(finding,)),
    )
    result = judge(
        job=fx.make_job(), plan=fx.make_plan(obligations=("O1",)), panel=fx.make_panel(attempts=(attempt,)),
        carry=fx.make_carry(), facts=facts, snapshot=fx.make_snapshot(), decision=None, record=fx.FakeRecord(),
    )
    assert "F1" not in result.corroborated


# -- T7b ----------------------------------------------------------------------


def test_t7b_a_failing_check_completed_after_the_cutoff_is_excluded_entirely() -> None:
    late_check = CheckRun(
        name="ci/late", conclusion=CheckConclusion.FAILURE, sha=fx.HEAD_SHA, observed_at=fx.AFTER_CUTOFF
    )
    facts = fx.make_facts(checks=(late_check,))
    finding = fx.make_finding(finding_id="F1", evidence="ci/late failed", source_attempt="att-1")
    attempt = fx.make_attempt(
        attempt_id="att-1",
        outcome=fx.make_verdict(obligations={"O1": EvidenceState.VERIFIED}, findings=(finding,)),
    )
    result = judge(
        job=fx.make_job(), plan=fx.make_plan(obligations=("O1",)), panel=fx.make_panel(attempts=(attempt,)),
        carry=fx.make_carry(), facts=facts, snapshot=fx.make_snapshot(), decision=None, record=fx.FakeRecord(),
    )
    assert result.attribution == {}
    assert "F1" not in result.corroborated
    assert "F1" not in result.blocking


# -- T7c ------------------------------------------------------------------------


def test_t7c_bound_reached_escalates_an_otherwise_approvable_judgement() -> None:
    plan = fx.make_plan(obligations=("O1",))
    attempt = fx.make_attempt(outcome=fx.make_verdict(obligations={"O1": EvidenceState.VERIFIED}))
    panel = fx.make_panel(attempts=(attempt,), bound_reached=True)
    result = judge(
        job=fx.make_job(), plan=plan, panel=panel, carry=fx.make_carry(), facts=fx.make_facts(),
        snapshot=fx.make_snapshot(policy=fx.make_policy(assurance={"standard": 1})),
        decision=None, record=fx.FakeRecord(),
    )
    assert result.obligations["O1"] is EvidenceState.VERIFIED
    assert result.assurance.achieved >= result.assurance.required
    assert result.blocking == frozenset()
    assert result.disposition == "escalate"
    from rqa.contracts import EscalationCause

    assert any(cause is EscalationCause.EVIDENCE_GAP for cause, _ in result.escalation_causes)


def test_approve_is_unreachable_when_bound_reached_is_true() -> None:
    """The same fixture as above, phrased as RQA-FR-039's own negative claim."""
    attempt = fx.make_attempt(outcome=fx.make_verdict(obligations={"O1": EvidenceState.VERIFIED}))
    panel = fx.make_panel(attempts=(attempt,), bound_reached=True)
    result = judge(
        job=fx.make_job(), plan=fx.make_plan(obligations=("O1",)), panel=panel, carry=fx.make_carry(),
        facts=fx.make_facts(), snapshot=fx.make_snapshot(policy=fx.make_policy(assurance={"standard": 1})),
        decision=None, record=fx.FakeRecord(),
    )
    assert result.disposition != "approve"


# -- decision override (not a numbered §8 row; see HANDOFF "Decisions") -------


def test_a_matching_decision_overrides_only_its_own_obligation() -> None:
    plan = fx.make_plan(obligations=("O1", "O2"))
    panel = fx.make_panel(attempts=())  # no reviewer evidence at all
    decision = fx.make_decision(substantiates="O1", outcome="approved")
    result = judge(
        job=fx.make_job(), plan=plan, panel=panel, carry=fx.make_carry(), facts=fx.make_facts(),
        snapshot=fx.make_snapshot(policy=fx.make_policy(assurance={"standard": 1})),
        decision=decision, record=fx.FakeRecord(),
    )
    assert result.obligations["O1"] is EvidenceState.VERIFIED
    assert result.obligations["O2"] is EvidenceState.UNKNOWN


def test_a_changes_requested_decision_fails_its_own_obligation() -> None:
    plan = fx.make_plan(obligations=("O1",))
    decision = fx.make_decision(substantiates="O1", outcome="changes_requested")
    result = judge(
        job=fx.make_job(), plan=plan, panel=fx.make_panel(attempts=()), carry=fx.make_carry(),
        facts=fx.make_facts(), snapshot=fx.make_snapshot(), decision=decision, record=fx.FakeRecord(),
    )
    assert result.obligations["O1"] is EvidenceState.FAILED


def test_independent_verified_evidence_overrides_a_lone_incomplete_report() -> None:
    """§3 step 4's exception: "unless independent evidence verifies the obligation"."""
    incomplete_attempt = fx.make_attempt(
        attempt_id="att-1", route=fx.make_route(family="fam-a"),
        outcome=fx.make_verdict(obligations={"O1": EvidenceState.INCOMPLETE}),
    )
    verified_attempt = fx.make_attempt(
        attempt_id="att-2", route=fx.make_route(family="fam-b"),
        outcome=fx.make_verdict(obligations={"O1": EvidenceState.VERIFIED}),
    )
    panel = fx.make_panel(attempts=(incomplete_attempt, verified_attempt))
    result = judge(
        job=fx.make_job(), plan=fx.make_plan(obligations=("O1",)), panel=panel, carry=fx.make_carry(),
        facts=fx.make_facts(), snapshot=fx.make_snapshot(), decision=None, record=fx.FakeRecord(),
    )
    assert result.obligations["O1"] is EvidenceState.VERIFIED


def test_a_failed_report_is_never_outvoted_by_an_optimistic_verified_report() -> None:
    verified_attempt = fx.make_attempt(
        attempt_id="att-1", route=fx.make_route(family="fam-a"),
        outcome=fx.make_verdict(obligations={"O1": EvidenceState.VERIFIED}),
    )
    failed_attempt = fx.make_attempt(
        attempt_id="att-2", route=fx.make_route(family="fam-b"),
        outcome=fx.make_verdict(obligations={"O1": EvidenceState.FAILED}),
    )
    panel = fx.make_panel(attempts=(verified_attempt, failed_attempt))
    result = judge(
        job=fx.make_job(), plan=fx.make_plan(obligations=("O1",)), panel=panel, carry=fx.make_carry(),
        facts=fx.make_facts(), snapshot=fx.make_snapshot(), decision=None, record=fx.FakeRecord(),
    )
    assert result.obligations["O1"] is EvidenceState.FAILED
