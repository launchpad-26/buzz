#!/usr/bin/env python3
"""Flow steps 3-13 through `admit()` — `code/P-02-lifecycle.md` §3.2; §8 rows T6-T12,
T17, T18; AC03/AC10/AC14; and the G-2199-P02/M3 credential-reachability probes.

No pytest: every `test_*` function takes no arguments, per `tests/run_all.py`.

Real collaborators wherever one can be steered into the branch (this batch's point):
every test drives the real `transition()` kernel and P-12's real `SQLiteRecordWriter`;
the judgement tests drive the real `rqa.judgement.judge`; the carry-over test drives the
real `rqa.reuse.carry_over` through the real `SQLiteRecordReader` that
`read_prior_record` constructs. Fakes remain for GitHub (network), the harness panel
(processes and models), P-05 supply (steered refusals), P-10 (git), and P-11 (Batch 5,
not landed). The E-12 fakes assert the grant discipline on every call, so §5 guard 2 is
checked at every callsite in this file, not once.
"""

from __future__ import annotations

import pathlib
import sqlite3
import sys
import traceback

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from lifecycle_cascade_bench import (  # noqa: E402
    DDL,
    HEAD,
    NOW,
    REPO,
    SNAP_HASH,
    FakeAuthority,
    FakeGithub,
    FakeHarness,
    FakeJudgement,
    FakeLease,
    FakePolicy,
    FakeReuse,
    FakeRemediation,
    FakeSupply,
    RealJudgement,
    RealReuse,
    RUN_FORBIDDEN,
    bench,
    entry_kinds,
    happy_deps,
    insert_job,
    latest_payload,
    make_deny,
    make_deps,
    make_facts,
    make_finding,
    make_grant,
    make_job,
    make_judgement,
    make_panel,
    make_plan,
    make_snapshot,
    make_validation_failure,
    stored_pin,
    stored_status,
    transitions,
)

from rqa.contracts import (  # noqa: E402
    Activity,
    AppendFailed,
    BundleFailure,
    CarriedEvidence,
    CarryOver,
    Category,
    DenyReason,
    EscalationCause,
    EvidenceState,
    GithubUnavailable,
    JobStatus,
    LeaseTaken,
    Remedy,
    Stale,
)
from rqa.lifecycle import admit  # noqa: E402
from rqa.lifecycle.admit import _durable  # noqa: E402
from rqa.lifecycle.errors import LifecycleError, UnknownJobError  # noqa: E402
from rqa.lifecycle.status import _reason  # noqa: E402
from rqa.lifecycle.steps import NO_CONFORMING_TRANSITION  # noqa: E402
from rqa.remediation import MECHANICAL_TOOL_SET  # noqa: E402


# -- the finished package (wave rule: the post-sibling set, exactly) -------------


def test_the_finished_package_exports_exactly_the_fourteen_names() -> None:
    """§1's re-export list. This lane completes the package, so the set is asserted
    exactly — never a subset or superset."""
    import rqa.lifecycle

    assert set(rqa.lifecycle.__all__) == {
        "admit", "resume", "status", "transition", "JobStatus", "TRANSITIONS",
        "Disposition", "DISPOSITION", "StatusReport", "NotFound", "StaleDecisionError",
        "LifecycleError", "IllegalTransitionError", "UnknownJobError",
    }
    assert len(rqa.lifecycle.__all__) == 14


def test_the_finished_package_has_exactly_the_nine_modules() -> None:
    """§1's module list, scoped to `rqa/lifecycle/*.py` only — blind to `rqa/intake`
    and every other package landing in parallel."""
    lifecycle = pathlib.Path(__file__).resolve().parent.parent / "rqa" / "lifecycle"
    assert {path.stem for path in lifecycle.glob("*.py")} == {
        "__init__", "states", "errors", "deps", "transition", "rest", "steps",
        "admit", "resume", "status",
    }


# -- T6: review authority denied --------------------------------------------------


def test_t6_a_review_deny_escalates_without_claiming() -> None:
    connection, record, job = bench()
    lease = FakeLease()
    deps = make_deps(
        connection, record,
        policy=FakePolicy(make_snapshot()),
        authority=FakeAuthority({Activity.REVIEW: [make_deny(Activity.REVIEW, reason=DenyReason.CAPABILITY_MISSING)]}),
        claim_lease=lease.claim,
        release_lease=lease.release,
    )
    assert admit(job=job, deps=deps) is JobStatus.ESCALATED
    assert stored_status(connection) == "escalated"
    assert lease.claim_calls == []  # no E-01 claim
    raised = deps.escalation.raised
    assert len(raised) == 1
    assert raised[0]["cause"] is EscalationCause.AUTHORITY_REQUIREMENT
    assert transitions(connection) == ["queued", "escalated"]


def test_the_deny_escalation_is_raised_against_the_pinned_snapshot() -> None:
    """`P-11-escalation.md` §2: the job `raise_` reads is already pinned, and the
    escalated transition writes the pin in its own transaction."""
    connection, record, job = bench()
    deps = make_deps(
        connection, record,
        policy=FakePolicy(make_snapshot()),
        authority=FakeAuthority({Activity.REVIEW: [make_deny(Activity.REVIEW)]}),
    )
    admit(job=job, deps=deps)
    assert stored_pin(connection) == SNAP_HASH
    assert deps.escalation.raised[0]["job"].snapshot_hash == SNAP_HASH


def test_a_validation_failure_escalates_the_authority_requirement() -> None:
    connection, record, job = bench()
    deps = make_deps(connection, record, policy=FakePolicy(make_validation_failure()))
    assert admit(job=job, deps=deps) is JobStatus.ESCALATED
    assert deps.escalation.raised[0]["cause"] is EscalationCause.AUTHORITY_REQUIREMENT
    assert stored_pin(connection) is None  # no snapshot existed to pin


def test_a_taken_lease_rests_the_job_queued_unchanged() -> None:
    connection, record, job = bench()
    lease = FakeLease(claim=LeaseTaken(login="someone-else"))
    deps = make_deps(
        connection, record,
        policy=FakePolicy(make_snapshot()),
        authority=FakeAuthority(),
        claim_lease=lease.claim,
        release_lease=lease.release,
    )
    assert admit(job=job, deps=deps) is JobStatus.QUEUED
    assert transitions(connection) == ["queued"]  # arrival only


def test_an_unavailable_claim_rests_queued_because_no_stop_edge_is_licensed() -> None:
    """§3.2 step 1 says STOPPED, but §2's closed table has no queued → stopped edge —
    the same table-wins resolution the landed containment applies to §3.1. The job
    rests queued and is re-offered on a later tick."""
    connection, record, job = bench()
    lease = FakeLease(claim=GithubUnavailable(op="claim_lease", reason="incomplete", retriable=True))
    deps = make_deps(
        connection, record,
        policy=FakePolicy(make_snapshot()),
        authority=FakeAuthority(),
        claim_lease=lease.claim,
        release_lease=lease.release,
    )
    assert admit(job=job, deps=deps) is JobStatus.QUEUED
    assert stored_status(connection) == "queued"
    assert transitions(connection) == ["queued"]


# -- T7 and the happy path ---------------------------------------------------------


def test_t7_one_admission_drives_queued_to_approved_with_exactly_one_run() -> None:
    """The full §3.2 cascade against the real kernel, real record writer and the real
    P-07 judge; the panel comes from a fake harness whose one `run` answer is a
    complete two-family panel. Merge is denied, so `approved` is the rest (AC14's
    granted-verdict half: RQA itself submitted APPROVED)."""
    connection, record, job = bench()
    harness = FakeHarness(plan=make_plan(), run_result=make_panel())
    deps, lease = happy_deps(connection, record, job, harness=harness)
    assert admit(job=job, deps=deps) is JobStatus.APPROVED
    assert transitions(connection) == [
        "queued", "claimed", "planned", "reviewing", "judged", "submitting", "approved",
    ]
    assert len(harness.run_calls) == 1  # exactly one E-07 run per review
    assert deps.supply.route_calls == []  # P-02 never drives an attempt (T7)
    assert deps.supply.reserve_calls == []
    assert deps.supply.consumed_calls == []
    assert stored_pin(connection) == SNAP_HASH
    assert len(deps.github.submit_calls) == 1
    state, body, grant = deps.github.submit_calls[0]
    assert state == "APPROVE" and grant.activity is Activity.APPROVE
    assert body == latest_payload(connection, "judgement")["rendered_body"]


def test_every_transition_payload_carries_exactly_the_eight_section_six_fields() -> None:
    """§6's shape is the first real input `rqa explain` reconstruction has ever had;
    every payload this cascade writes is the published eight-field one."""
    import json

    connection, record, job = bench()
    deps, _ = happy_deps(connection, record, job)
    admit(job=job, deps=deps)
    rows = connection.execute(
        "SELECT payload FROM record_entries WHERE job = ? AND kind = 'transition' ORDER BY seq",
        (job.id,),
    ).fetchall()
    assert len(rows) >= 7
    for (payload,) in rows:
        assert set(json.loads(payload)) == {
            "from_state", "to_state", "reason", "repo", "number", "head_sha",
            "base_sha", "predecessor_job",
        }


def test_the_record_this_cascade_writes_reconstructs_through_real_explain() -> None:
    """A record written by this code is one `rqa.record.explain` can reconstruct —
    P-12's landed reader consuming P-02's first real transition stream."""
    from rqa.record import Explanation, explain

    connection, record, job = bench()
    deps, _ = happy_deps(connection, record, job)
    admit(job=job, deps=deps)
    explanation = explain(connection, REPO, 7)
    assert isinstance(explanation, Explanation)
    assert explanation.disposition == "review-complete"


def test_the_supply_port_closures_forward_the_verbatim_e06_e15_arguments() -> None:
    """§3.2's three closures, character for character: the fake harness exercises the
    port it was handed and the fake supply records exactly what arrived."""
    supply = FakeSupply()

    class PortExercisingHarness(FakeHarness):
        def run(self, *, job, plan, facts, snapshot, supply, state_dir, record):
            from rqa.contracts import RouteCursor

            cursor = RouteCursor(excluded_families=frozenset(), excluded_routes=frozenset())
            supply.route("ob-1", cursor)
            supply.reserve(plan, "route-sentinel")
            supply.consumed("attempt-sentinel", 5, "reservation-sentinel")
            return make_panel()

    connection, record, job = bench()
    deps, _ = happy_deps(
        connection, record, job,
        harness=PortExercisingHarness(plan=make_plan()),
        supply=supply,
    )
    admit(job=job, deps=deps)
    (route_kwargs,) = supply.route_calls
    assert set(route_kwargs) == {"job", "obligation", "snapshot", "facts", "cursor", "prober", "breakers"}
    assert route_kwargs["prober"] is supply.prober and route_kwargs["breakers"] is supply.breakers
    assert route_kwargs["obligation"] == "ob-1"
    (reserve_kwargs,) = supply.reserve_calls
    assert set(reserve_kwargs) == {"job", "plan", "route", "snapshot", "spend"}
    assert reserve_kwargs["spend"] is supply.spend
    (consumed_kwargs,) = supply.consumed_calls
    assert set(consumed_kwargs) == {"job", "attempt", "reading", "reservation", "record", "spend", "breakers"}
    assert consumed_kwargs["reading"] == 5


def test_a_predecessor_admission_drives_the_real_carry_over() -> None:
    """Real E-05: `carry_over` runs against the real `SQLiteRecordReader` that
    `read_prior_record` builds. The predecessor has no record, so P-13 regenerates
    everything with its untrusted-predecessor reason — a real classified answer, not a
    stubbed one."""
    connection, record, job_zero = bench()  # job-1 row; add the successor by hand
    successor = make_job(job_id="job-2", predecessor_job="job-1", head_sha="e" * 40, number=7)
    insert_job(connection, successor)
    reuse = RealReuse()
    deps, _ = happy_deps(connection, record, successor, reuse=reuse,
                         facts=make_facts(job=successor))
    assert admit(job=successor, deps=deps) is JobStatus.APPROVED
    assert len(reuse.calls) == 1
    payload = latest_payload(connection, "carry_over", job_id="job-2")
    assert payload["regenerated"] == ["ob-1"]
    assert payload["reasons"] == {"ob-1": "untrusted_predecessor"}
    assert payload["source_job"] == "job-1"


# -- T8: no failure subtype reaches APPROVED --------------------------------------


def test_t8_bundle_failure_and_every_incomplete_reason_stop() -> None:
    for run_result, expected_reason in (
        (BundleFailure(reason="missing diff"), "bundle incomplete"),
        (make_panel(complete=False, incomplete_reason="exhausted"), "panel incomplete (exhausted)"),
        (make_panel(complete=False, incomplete_reason="budget"), "panel incomplete (budget)"),
        (make_panel(complete=False, incomplete_reason="bundle"), "panel incomplete (bundle)"),
    ):
        connection, record, job = bench()
        deps, _ = happy_deps(
            connection, record, job, harness=FakeHarness(plan=make_plan(), run_result=run_result)
        )
        assert admit(job=job, deps=deps) is JobStatus.STOPPED
        assert stored_status(connection) == "stopped"
        assert latest_payload(connection, "transition")["reason"] == expected_reason
        assert "approved" not in transitions(connection)


def test_t8_a_contradictory_or_unknown_panel_pair_raises() -> None:
    for run_result in (
        make_panel(complete=True, incomplete_reason="budget"),
        make_panel(complete=False, incomplete_reason=None),
        make_panel(complete=False, incomplete_reason="weather"),
    ):
        connection, record, job = bench()
        deps, _ = happy_deps(
            connection, record, job, harness=FakeHarness(plan=make_plan(), run_result=run_result)
        )
        try:
            admit(job=job, deps=deps)
        except LifecycleError:
            pass
        else:
            raise AssertionError(f"panel pair {run_result.complete}/{run_result.incomplete_reason!r} fell through")
        assert stored_status(connection) != "approved"


# -- T9: the carry-only path (AC03, AC10) -----------------------------------------


def test_t9_empty_regenerated_calls_no_harness_and_the_absent_attestation_proves_it() -> None:
    """`carry.regenerated == ()` → zero run calls, judged from carried evidence by the
    REAL P-07 judge, and no `attestation` entry on the job — AC03/AC10's proof."""
    connection, record, job_zero = bench()
    successor = make_job(job_id="job-2", predecessor_job="job-1", head_sha="e" * 40)
    insert_job(connection, successor)
    carried = CarryOver(
        reused=(CarriedEvidence(
            obligation_id="ob-1", state=EvidenceState.VERIFIED, source_job="job-1",
            source_judgement_seq=3, source_attestations=("att-1",),
        ),),
        regenerated=(),
        reasons={},
        source_job="job-1",
    )
    judgement_client = RealJudgement()
    deps, _ = happy_deps(
        connection, record, successor,
        facts=make_facts(job=successor),
        reuse=FakeReuse(carried),
        harness=FakeHarness(plan=make_plan(obligations=()), run_result=RUN_FORBIDDEN),
        judgement=judgement_client,
    )
    assert admit(job=successor, deps=deps) is JobStatus.APPROVED
    kinds = entry_kinds(connection, job_id="job-2")
    assert "attestation" not in kinds  # AC03/AC10: the absence is the proof
    assert "panel" not in kinds  # no run happened, so P-06 never recorded one
    (call,) = judgement_client.calls
    assert call["panel"].attempts == ()
    assert call["panel"].complete is True and call["panel"].bound_reached is False
    # E-09 received the empty complete panel cut off at fact-capture time (T9).
    assert call["panel"].evidence_cutoff == NOW
    judgement_payload = latest_payload(connection, "judgement", job_id="job-2")
    assert judgement_payload["reused_from"] == "job-1"
    assert judgement_payload["disposition"] == "approve"


def test_t9_the_judged_transition_happens_only_after_judge_returns() -> None:
    """T9/T10's ordering: the `judgement` entry sequence precedes the judged
    transition's — the real writer's monotone seq is the witness."""
    import json

    connection, record, job = bench()
    deps, _ = happy_deps(connection, record, job)
    admit(job=job, deps=deps)
    rows = connection.execute(
        "SELECT seq, kind, payload FROM record_entries WHERE job = ? ORDER BY seq", (job.id,)
    ).fetchall()
    judgement_seq = next(seq for seq, kind, _ in rows if kind == "judgement")
    judged_seq = next(
        seq for seq, kind, payload in rows
        if kind == "transition" and json.loads(payload)["to_state"] == "judged"
    )
    assert judgement_seq < judged_seq


# -- T10: a fresh panel's cutoff --------------------------------------------------


def test_t10_the_real_judge_receives_the_panels_post_attempt_cutoff() -> None:
    from datetime import timedelta

    cutoff = NOW + timedelta(minutes=5)
    connection, record, job = bench()
    judgement_client = RealJudgement()
    deps, _ = happy_deps(
        connection, record, job,
        harness=FakeHarness(plan=make_plan(), run_result=make_panel(evidence_cutoff=cutoff)),
        judgement=judgement_client,
    )
    assert admit(job=job, deps=deps) is JobStatus.APPROVED
    (call,) = judgement_client.calls
    assert call["panel"].evidence_cutoff == cutoff
    assert latest_payload(connection, "judgement")["cutoff"] == cutoff.isoformat()


# -- T11: remediation (AC09's dispatch side) ---------------------------------------


def _remediation_judgement():
    """A remediate judgement whose finding carries a real registry `check_id` — this
    lane is the first real producer of `Remedy`-bearing dispositions, so the check
    name comes from `rqa.remediation`'s registry, never invented (#2242/#2243)."""
    spec = MECHANICAL_TOOL_SET["ruff-format"]
    finding = make_finding(
        finding_id="finding-1",
        categories=frozenset({Category.MECHANICAL}),
        remedy=Remedy(tool="ruff-format", paths=("src/x.py",), check=spec.check_id),
    )
    return make_judgement(
        disposition="remediate", findings=(finding,), remediation_candidates=("finding-1",)
    ), finding


def test_t11_a_granted_remediation_receives_the_exact_e10_arguments() -> None:
    judgement, finding = _remediation_judgement()
    connection, record, job = bench()
    remediation = FakeRemediation()
    deps, _ = happy_deps(
        connection, record, job,
        judgement=FakeJudgement(judgement),
        remediation=remediation,
    )
    assert admit(job=job, deps=deps) is JobStatus.REMEDIATING
    assert transitions(connection) == ["queued", "claimed", "planned", "reviewing", "judged", "remediating"]
    (call,) = remediation.calls
    assert call["finding"] is finding or call["finding"].id == "finding-1"
    assert call["grant"].activity is Activity.REMEDIATE
    assert call["facts"] is deps.github._facts  # the one E-23 capture, by identity
    assert call["snapshot"].hash == SNAP_HASH
    assert call["runner"] is deps.runner and call["state_dir"] == deps.state_dir
    granted = [c for c in deps.authority.calls if c[0] is Activity.REMEDIATE]
    assert granted and granted[0][2] == finding.categories  # the complete category set


def test_t11_a_remediation_refusal_reaches_only_escalated() -> None:
    from rqa.contracts import RemediationRefused, RemediationRefusalReason

    judgement, _ = _remediation_judgement()
    connection, record, job = bench()
    deps, _ = happy_deps(
        connection, record, job,
        judgement=FakeJudgement(judgement),
        remediation=FakeRemediation(
            RemediationRefused(
                reason=RemediationRefusalReason.REMEDY_MISSING, detail="x", entry_seq=9
            )
        ),
    )
    assert admit(job=job, deps=deps) is JobStatus.ESCALATED
    assert deps.escalation.raised[-1]["cause"] is EscalationCause.EVIDENCE_GAP
    assert "approved" not in transitions(connection)
    assert "submitting" not in transitions(connection)


def test_a_remediation_deny_escalates_the_authority_requirement() -> None:
    judgement, _ = _remediation_judgement()
    connection, record, job = bench()
    deps, _ = happy_deps(
        connection, record, job,
        judgement=FakeJudgement(judgement),
        authority=FakeAuthority({Activity.REMEDIATE: [make_deny(Activity.REMEDIATE)]}),
    )
    assert admit(job=job, deps=deps) is JobStatus.ESCALATED
    assert deps.escalation.raised[-1]["cause"] is EscalationCause.AUTHORITY_REQUIREMENT
    assert "remediating" not in transitions(connection)


def test_an_escalate_judgement_raises_every_named_cause() -> None:
    judgement = make_judgement(
        disposition="escalate",
        escalation_causes=(
            (EscalationCause.EVIDENCE_GAP, "obligation ob-1 evidence is unknown"),
            (EscalationCause.CONFLICTING_JUDGEMENT, "reviewers disagree on ob-1"),
        ),
        obligations={"ob-1": EvidenceState.UNKNOWN},
    )
    connection, record, job = bench()
    deps, _ = happy_deps(connection, record, job, judgement=FakeJudgement(judgement))
    assert admit(job=job, deps=deps) is JobStatus.ESCALATED
    causes = [raise_["cause"] for raise_ in deps.escalation.raised]
    assert causes == [EscalationCause.EVIDENCE_GAP, EscalationCause.CONFLICTING_JUDGEMENT]


# -- T12 and AC14: verdict authority, submission, merge ----------------------------


def test_t12_a_verdict_deny_takes_the_authority_requirement_path() -> None:
    """AC14's denied half: no verdict activity granted → comment (granted) with the
    judgement's own rendering, an authority-requirement escalation, and §9's verbatim
    transition reason. Review-complete is not reached."""
    connection, record, job = bench()
    deps, _ = happy_deps(
        connection, record, job,
        authority=FakeAuthority({
            Activity.APPROVE: [make_deny(Activity.APPROVE)],
            Activity.MERGE: [make_deny(Activity.MERGE)],
        }),
    )
    assert admit(job=job, deps=deps) is JobStatus.ESCALATED
    assert deps.github.submit_calls == []
    (comment_body, comment_grant) = deps.github.comment_calls[0]
    assert comment_body == latest_payload(connection, "judgement")["rendered_body"]
    assert comment_grant.activity is Activity.COMMENT
    assert deps.escalation.raised[-1]["cause"] is EscalationCause.AUTHORITY_REQUIREMENT
    assert latest_payload(connection, "transition")["reason"] == NO_CONFORMING_TRANSITION
    assert stored_status(connection) == "escalated"
    assert "approved" not in transitions(connection)


def test_a_denied_comment_still_escalates_without_posting() -> None:
    connection, record, job = bench()
    deps, _ = happy_deps(
        connection, record, job,
        authority=FakeAuthority({
            Activity.APPROVE: [make_deny(Activity.APPROVE)],
            Activity.COMMENT: [make_deny(Activity.COMMENT)],
        }),
    )
    assert admit(job=job, deps=deps) is JobStatus.ESCALATED
    assert deps.github.comment_calls == []
    assert latest_payload(connection, "transition")["reason"] == NO_CONFORMING_TRANSITION


def test_t12_a_stale_submission_escalates_an_evidence_gap() -> None:
    connection, record, job = bench()
    deps, _ = happy_deps(
        connection, record, job,
        github=FakeGithub(
            facts=make_facts(job=make_job()),
            submit=Stale(reason="head_changed", observed_head_sha="f" * 40),
        ),
    )
    assert admit(job=job, deps=deps) is JobStatus.ESCALATED
    assert deps.escalation.raised[-1]["cause"] is EscalationCause.EVIDENCE_GAP
    assert "approved" not in transitions(connection)


def test_t12_an_unavailable_submission_stops() -> None:
    connection, record, job = bench()
    deps, _ = happy_deps(
        connection, record, job,
        github=FakeGithub(
            facts=make_facts(job=make_job()),
            submit=GithubUnavailable(op="submit_review", reason="incomplete", retriable=True),
        ),
    )
    assert admit(job=job, deps=deps) is JobStatus.STOPPED
    assert "approved" not in transitions(connection)


def test_t12_a_granted_merge_reaches_merged_under_its_own_grant() -> None:
    connection, record, job = bench()
    deps, _ = happy_deps(
        connection, record, job,
        authority=FakeAuthority(),  # everything granted, including MERGE
    )
    assert admit(job=job, deps=deps) is JobStatus.MERGED
    (merge_grant,) = deps.github.merge_calls
    assert merge_grant.activity is Activity.MERGE
    assert transitions(connection)[-1] == "merged"


def test_a_stale_or_unavailable_merge_rests_at_approved() -> None:
    for merge_result in (
        Stale(reason="head_changed", observed_head_sha="f" * 40),
        GithubUnavailable(op="merge", reason="incomplete", retriable=True),
    ):
        connection, record, job = bench()
        deps, _ = happy_deps(
            connection, record, job,
            authority=FakeAuthority(),
            github=FakeGithub(facts=make_facts(job=make_job()), merge=merge_result),
        )
        assert admit(job=job, deps=deps) is JobStatus.APPROVED
        assert stored_status(connection) == "approved"


# -- T17: one E-23 capture, threaded by identity -----------------------------------


def test_t17_facts_are_captured_once_and_threaded_by_identity() -> None:
    judgement, _ = _remediation_judgement()
    connection, record, job = bench()
    reuse = FakeReuse(CarryOver(reused=(), regenerated=(), reasons={}, source_job=None))
    judgement_client = FakeJudgement(judgement)
    remediation = FakeRemediation()
    harness = FakeHarness(plan=make_plan(), run_result=make_panel())
    deps, _ = happy_deps(
        connection, record, job,
        harness=harness, judgement=judgement_client, remediation=remediation,
    )
    admit(job=job, deps=deps)
    assert len(deps.github.facts_calls) == 1  # E-23 exactly once (T17)
    facts = harness.plan_calls[0][1]
    assert harness.run_calls[0][2] is facts
    assert judgement_client.calls[0]["facts"] is facts
    assert remediation.calls[0]["facts"] is facts


# -- T18: a crash-recovered judged job consumes the recorded judgement -------------


def _recorded_judgement_payload(*, disposition: str = "approve") -> dict:
    return {
        "snapshot_hash": SNAP_HASH,
        "protocol_hash": "sha256:protocol-1",
        "cutoff": NOW.isoformat(),
        "facts_fetched_at": NOW.isoformat(),
        "obligations": {"ob-1": "verified"},
        "reused_from": None,
        "carried_provenance": {},
        "contributing_attempts": ["attempt-alpha"],
        "decision": None,
        "findings": [],
        "corroborated": [],
        "blocking": [],
        "attribution": {},
        "assurance": {"required": 2, "achieved": 2},
        "remediation_candidates": [],
        "escalation_causes": [],
        "disposition": disposition,
        "rendered_body": "the recorded rendering",
    }


def test_t18_a_recovered_judged_job_never_calls_judge_again() -> None:
    connection, record, job = bench(status=JobStatus.JUDGED, snapshot_hash=SNAP_HASH)
    record.append(job.id, "transition", {
        "from_state": None, "to_state": "queued", "reason": "arrival", "repo": REPO,
        "number": 7, "head_sha": HEAD, "base_sha": "b" * 40, "predecessor_job": None,
    })
    record.append(job.id, "judgement", _recorded_judgement_payload())
    connection.commit()
    deps, _ = happy_deps(
        connection, record, job,
        judgement=FakeJudgement(FakeJudgement.JUDGE_FORBIDDEN),
        harness=FakeHarness(plan=make_plan(), run_result=RUN_FORBIDDEN),
    )
    assert admit(job=job, deps=deps) is JobStatus.APPROVED
    (state, body, grant) = deps.github.submit_calls[0]
    assert state == "APPROVE" and body == "the recorded rendering"


# -- a crash-recovered SUBMITTING job re-establishes verdict authority (G-2200 delta) --


def _submitting_bench():
    """A job resting at SUBMITTING with its recorded judgement, re-offered to `admit`
    with a fresh `Cascade` — so `ctx.verdict_grant` is empty and `submit()`'s
    crash-recovery re-grant branch (steps.py's isinstance re-check) is the only thing
    standing between the submission and E-12. This is the same crash-recovery shape
    QUEUED (D-B4-3), PLANNED/REVIEWING (`_require_context`) and JUDGED (T18) already
    have; SUBMITTING sits on the AC14/ADR-0061 verdict-authority boundary."""
    connection, record, job = bench(status=JobStatus.SUBMITTING, snapshot_hash=SNAP_HASH)
    record.append(job.id, "transition", {
        "from_state": None, "to_state": "queued", "reason": "arrival", "repo": REPO,
        "number": 7, "head_sha": HEAD, "base_sha": "b" * 40, "predecessor_job": None,
    })
    record.append(job.id, "judgement", _recorded_judgement_payload())
    connection.commit()
    return connection, record, job


def test_a_recovered_submitting_job_re_establishes_its_grant_before_submitting() -> None:
    """(b) A freshly re-established `Grant` for the exact verdict activity is threaded
    into `submit_review` — never a stale or absent one. Disabling the re-grant branch
    alone hands E-12 `None` and fails here."""
    connection, record, job = _submitting_bench()
    deps, _ = happy_deps(
        connection, record, job,
        judgement=FakeJudgement(FakeJudgement.JUDGE_FORBIDDEN),
        harness=FakeHarness(plan=make_plan(), run_result=RUN_FORBIDDEN),
    )
    assert admit(job=job, deps=deps) is JobStatus.APPROVED
    asked = [call[0] for call in deps.authority.calls]
    assert Activity.APPROVE in asked  # verdict authority was re-established, not assumed
    (state, body, grant) = deps.github.submit_calls[0]
    assert state == "APPROVE" and grant.activity is Activity.APPROVE
    assert grant.job_id == job.id  # the fresh E-04 answer, threaded by the branch
    assert transitions(connection) == ["queued", "approved"]


def test_a_recovered_submitting_job_denied_its_regrant_escalates_without_submitting() -> None:
    """(a) A `Deny` on the re-grant takes the authority-requirement path — §9's
    verbatim RQA-NFR-007 reason, an AUTHORITY_REQUIREMENT escalation, and no
    `submit_review` call — instead of proceeding on authority the cascade no longer
    holds."""
    connection, record, job = _submitting_bench()
    deps, _ = happy_deps(
        connection, record, job,
        judgement=FakeJudgement(FakeJudgement.JUDGE_FORBIDDEN),
        harness=FakeHarness(plan=make_plan(), run_result=RUN_FORBIDDEN),
        authority=FakeAuthority({Activity.APPROVE: [make_deny(Activity.APPROVE)]}),
    )
    assert admit(job=job, deps=deps) is JobStatus.ESCALATED
    assert deps.github.submit_calls == []
    assert deps.escalation.raised[-1]["cause"] is EscalationCause.AUTHORITY_REQUIREMENT
    assert latest_payload(connection, "transition")["reason"] == NO_CONFORMING_TRANSITION
    (comment_body, comment_grant) = deps.github.comment_calls[0]
    assert comment_body == "the recorded rendering"  # the judgement's own rendering
    assert transitions(connection) == ["queued", "escalated"]


def test_a_recovered_reviewing_job_reuses_its_recorded_complete_panel() -> None:
    """§3.3's reconstruction at flow step 13's re-entry: a complete recorded `panel`
    is not paid for twice."""
    connection, record, job = bench(status=JobStatus.REVIEWING, snapshot_hash=SNAP_HASH)
    record.append(job.id, "transition", {
        "from_state": None, "to_state": "queued", "reason": "arrival", "repo": REPO,
        "number": 7, "head_sha": HEAD, "base_sha": "b" * 40, "predecessor_job": None,
    })
    import dataclasses

    record.append(job.id, "plan", dataclasses.asdict(make_plan()))
    record.append(job.id, "panel", {
        "attempts": ["attempt-alpha"], "complete": True, "incomplete_reason": None,
        "evidence_cutoff": NOW.isoformat(), "bound_reached": False,
    })
    connection.commit()
    judgement_client = FakeJudgement(make_judgement(disposition="approve"))
    deps, _ = happy_deps(
        connection, record, job,
        judgement=judgement_client,
        harness=FakeHarness(plan=make_plan(), run_result=RUN_FORBIDDEN),
    )
    assert admit(job=job, deps=deps) is JobStatus.APPROVED
    assert judgement_client.calls[0]["panel"].evidence_cutoff == NOW


# -- G-2199-P02 / M3: the credential-reachability probes ---------------------------


SECRET = "ghp_probe-credential-that-must-never-chain"


def test_probe_the_durable_read_raise_chains_no_credential_bearing_cause() -> None:
    """The gate's own probe, now structural: a credential-bearing exception injected
    as `cause` into `_durable`'s vanished-row raise is reachable from neither
    `__cause__` nor `__context__` nor a rendered traceback. Before the `from None`
    hardening this fails at the `__cause__` assertion."""
    connection = sqlite3.connect(":memory:")
    connection.executescript(DDL)  # tables exist; the row does not
    cause = AppendFailed(f"POST failed; Authorization: token {SECRET}")
    raised: UnknownJobError | None = None
    try:
        _durable(job=make_job(), connection=connection, cause=cause)
    except UnknownJobError as exc:
        raised = exc
    assert raised is not None
    assert raised.__cause__ is None
    assert raised.__context__ is None
    assert raised.__suppress_context__ is True
    rendering = "".join(traceback.format_exception(raised))
    assert SECRET not in rendering
    assert SECRET not in str(raised)


def test_probe_the_status_reason_raise_chains_no_credential_bearing_cause() -> None:
    """The second G-2199 branch: an undecodable stored payload carrying a credential
    is not reachable from `_reason`'s raise through `__cause__` or a rendered
    traceback. (`JSONDecodeError.doc` carries the whole document; before the
    `from None` hardening it rode `__cause__` out of this function. The implicit
    `__context__` set by raising inside an `except` block survives `from None` by
    Python's own semantics and is display-suppressed — recorded as a disclosed
    residual, not silently ignored.)"""
    payload = '{"reason": "x", "leaked": "' + SECRET + '"'  # invalid JSON, secret inside
    raised: LifecycleError | None = None
    try:
        _reason(payload, job_id="job-1")
    except LifecycleError as exc:
        raised = exc
    assert raised is not None
    assert raised.__cause__ is None
    assert raised.__suppress_context__ is True
    rendering = "".join(traceback.format_exception(raised))
    assert SECRET not in rendering
    assert SECRET not in str(raised)
