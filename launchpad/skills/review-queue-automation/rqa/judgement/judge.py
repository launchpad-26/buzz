"""E-09 algorithm and disposition selection — `code/P-07-judgement.md` §3.

`judge()` turns the selected plan, carried evidence, validated panel verdicts,
pinned policy, and canonical captured facts into one deterministic current-job
`Judgement`, in the eleven ordered steps §3 states. It reads neither clock,
filesystem, configuration, environment, network, nor a neighbour; every input
it needs arrives as a keyword argument. It writes nothing persistent of its
own (§5) beyond the one `judgement` record entry §6 names.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Literal

from rqa.contracts import (
    AttemptFailure,
    CarryOver,
    Decision,
    EscalationCause,
    EvidenceState,
    Facts,
    Finding,
    Job,
    Judgement,
    PanelResult,
    Plan,
    RecordWriter,
    Snapshot,
    Verdict,
)
from rqa.protocol import paths

from rqa.judgement import checks as checks_mod
from rqa.judgement import evidence as evidence_mod
from rqa.judgement import findings as findings_mod
from rqa.judgement.render import render

__all__ = ["judge", "JudgementError"]


class JudgementError(Exception):
    """Programming error or internally inconsistent supposedly validated input."""


def _validate(
    *,
    job: Job,
    plan: Plan,
    panel: PanelResult,
    carry: CarryOver,
    facts: Facts,
    decision: Decision | None,
) -> None:
    """§3 step 1. Every violation raises `JudgementError`; nothing is appended."""
    if facts.pr.repo != job.repo or facts.pr.number != job.number or facts.pr.head_sha != job.head_sha:
        raise JudgementError(
            f"facts do not identify job {job.id}: "
            f"facts.pr=({facts.pr.repo!r}, {facts.pr.number!r}, {facts.pr.head_sha!r}) "
            f"job=({job.repo!r}, {job.number!r}, {job.head_sha!r})"
        )
    if not isinstance(facts.checks, tuple) or not isinstance(facts.base_checks, tuple):
        raise JudgementError("facts.checks and facts.base_checks must both be present")
    if facts.fetched_at is None:
        raise JudgementError("facts.fetched_at is missing")
    if panel.evidence_cutoff is None:
        raise JudgementError("panel.evidence_cutoff is missing")
    if panel.complete is not True:
        raise JudgementError(f"panel is not complete: {panel.incomplete_reason!r}")
    if panel.incomplete_reason is not None:
        raise JudgementError(
            f"panel is complete but carries incomplete_reason={panel.incomplete_reason!r}"
        )

    plan_ids = list(plan.obligations)
    if len(set(plan_ids)) != len(plan_ids):
        raise JudgementError("plan.obligations contains a duplicate id")
    carried_ids = [carried.obligation_id for carried in carry.reused]
    if len(set(carried_ids)) != len(carried_ids):
        raise JudgementError("carry.reused contains a duplicate obligation id")
    if set(plan_ids) & set(carried_ids):
        raise JudgementError("plan.obligations and carry.reused are not disjoint")

    for attempt in panel.attempts:
        if attempt.attestation.ended_at > panel.evidence_cutoff:
            raise JudgementError(
                f"attempt {attempt.id!r} ended at {attempt.attestation.ended_at!r}, "
                f"after panel.evidence_cutoff {panel.evidence_cutoff!r}"
            )
        if not isinstance(attempt.outcome, Verdict) and not isinstance(attempt.outcome, AttemptFailure):
            raise JudgementError(
                f"attempt {attempt.id!r} outcome is neither Verdict nor AttemptFailure"
            )

    if decision is not None and decision.substantiates is not None:
        universe = set(plan_ids) | set(carried_ids)
        if decision.substantiates not in universe:
            raise JudgementError(
                f"decision.substantiates {decision.substantiates!r} is outside the obligation universe"
            )


def _obligation_definitions(snapshot: Snapshot) -> dict[str, object]:
    return {obligation.id: obligation for obligation in snapshot.policy.obligations}


def _reused_from(carry: CarryOver) -> str | None:
    """§3 step 3: `carry.source_job` when at least one carried item exists,
    otherwise `None`.

    **Interim, not the pinned reference §3.3 of P-12-record.md describes — see
    #2236.** `reused_from` is a bare job id (`CONTRACTS.md` §6:
    `Judgement.reused_from: str | None`), never a `(job, seq)` pair: there is
    nowhere on `Judgement` to carry the source sequence that
    `CarriedEvidence.source_judgement_seq` names per obligation. Each carried
    item's own sequence still survives into `carried_provenance` (built beside
    this call), so the information is not lost — only `reused_from` itself
    cannot address a specific predecessor judgement row. #2236 tracks the
    `CONTRACTS.md` §6 change (a `(job, seq)` reused_from) plus the
    `judge()`/`carry_over()` obligations that would populate it; this
    accepted-interim shape does not change until that lands, and
    `rqa.record.explain._walk_reuse_chain` documents the same seam from its
    own reading side.
    """
    return carry.source_job if carry.reused else None


def _has_evidence_bearing_changed_path(
    *, obligation_ids: Iterable[str], snapshot: Snapshot, changed_paths: frozenset[str]
) -> bool:
    """Whether any changed path falls within the path scope of an obligation in
    `obligation_ids` (§3 step 8's "evidence-bearing changed path"). Uses
    `rqa.protocol.paths.matches` exclusively — the only matcher P-07 may use.
    """
    definitions = _obligation_definitions(snapshot)
    for obligation_id in obligation_ids:
        obligation = definitions.get(obligation_id)
        if obligation is None:
            continue
        for pattern in obligation.paths:
            for path in changed_paths:
                if paths.matches(path, pattern):
                    return True
    return False


def _finding_payload(finding: Finding) -> dict[str, object]:
    return {
        "id": finding.id,
        "categories": sorted(category.value for category in finding.categories),
        "extra_tags": sorted(finding.extra_tags),
        "location": {"path": finding.location.path, "line": finding.location.line},
        "evidence": finding.evidence,
        "severity": finding.severity,
        "remedy": (
            None
            if finding.remedy is None
            else {
                "tool": finding.remedy.tool,
                "paths": list(finding.remedy.paths),
                "check": finding.remedy.check,
            }
        ),
        "behaviour_changing": finding.behaviour_changing,
        "source_attempt": finding.source_attempt,
    }


def judge(
    *,
    job: Job,
    plan: Plan,
    panel: PanelResult,
    carry: CarryOver,
    facts: Facts,
    snapshot: Snapshot,
    decision: Decision | None,
    record: RecordWriter,
) -> Judgement:
    # ---- step 1: programming invariants ---------------------------------
    _validate(job=job, plan=plan, panel=panel, carry=carry, facts=facts, decision=decision)

    # ---- step 2: obligation universe -------------------------------------
    universe_order: list[str] = list(plan.obligations) + [
        carried.obligation_id for carried in carry.reused
    ]
    carried_ids = frozenset(carried.obligation_id for carried in carry.reused)

    obligations: dict[str, EvidenceState] = {}
    carried_provenance: dict[str, dict[str, object]] = {}

    # ---- step 3: carried evidence ------------------------------------------
    for carried in carry.reused:
        obligations[carried.obligation_id] = EvidenceState.VERIFIED
        carried_provenance[carried.obligation_id] = {
            "source_job": carried.source_job,
            "source_judgement_seq": carried.source_judgement_seq,
            "source_attestations": list(carried.source_attestations),
        }
    reused_from = _reused_from(carry)

    # ---- step 4: non-carried obligation states -----------------------------
    for obligation_id in plan.obligations:
        obligations[obligation_id] = evidence_mod.resolve_obligation_state(
            obligation_id, attempts=panel.attempts, decision=decision
        )

    # ---- step 5: captured-check attribution --------------------------------
    attribution = checks_mod.attribute(
        head_checks=facts.checks, base_checks=facts.base_checks, cutoff=panel.evidence_cutoff
    )
    pr_failing_checks = [name for name, kind in attribution.items() if kind == "pr"]

    # ---- step 6: findings, fingerprinted and corroborated ------------------
    attempt_family_by_id = {attempt.id: attempt.route.family for attempt in panel.attempts}

    all_findings: list[Finding] = []
    groups: dict[findings_mod.Fingerprint, list[Finding]] = {}
    for attempt in panel.attempts:
        if not isinstance(attempt.outcome, Verdict):
            continue
        for finding in attempt.outcome.findings:
            if findings_mod.is_malformed(finding):
                raise JudgementError(f"finding {finding.id!r} is malformed")
            all_findings.append(finding)
            groups.setdefault(findings_mod.fingerprint(finding), []).append(finding)

    corroborated_ids: set[str] = set()
    blocking_ids: set[str] = set()
    remediation_eligible_ids: set[str] = set()
    captured_paths = frozenset(facts.files)

    for group in groups.values():
        families = findings_mod.corroborating_families(
            group, attempt_family_by_id=attempt_family_by_id
        )
        check_citation: str | None = None
        if len(families) < 2:
            for finding in group:
                check_citation = findings_mod.cited_pr_failing_check(
                    finding.evidence, pr_failing_checks=pr_failing_checks
                )
                if check_citation is not None:
                    break
        is_corroborated = len(families) >= 2 or check_citation is not None
        if not is_corroborated:
            continue
        for finding in group:
            corroborated_ids.add(finding.id)
            # ---- step 7: policy blocking and remediation candidacy ---------
            if findings_mod.is_blocking_by_policy(
                finding, blocking_categories=snapshot.policy.blocking.categories
            ):
                blocking_ids.add(finding.id)
            if findings_mod.is_remediation_candidate(
                finding,
                mechanical_categories=snapshot.policy.mechanical.categories,
                mechanical_tools=snapshot.policy.mechanical.tools,
                captured_paths=captured_paths,
            ):
                remediation_eligible_ids.add(finding.id)

    # §3's preamble: "preserves supplied stable order to break ties" —
    # `remediation_candidates` is emitted in `all_findings`' own retained
    # order, never in fingerprint-group insertion order (which reorders
    # findings whose fingerprints interleave).
    remediation_candidates: list[str] = [
        finding.id for finding in all_findings if finding.id in remediation_eligible_ids
    ]

    # ---- step 8: synthetic injection / envelope / suspicious-clean --------
    for attempt in panel.attempts:
        if not isinstance(attempt.outcome, Verdict):
            continue
        for injection in attempt.outcome.injection_attempts:
            synthetic = findings_mod.build_injection_finding(
                attempt_id=attempt.id, injection=injection
            )
            all_findings.append(synthetic)
            corroborated_ids.add(synthetic.id)
            blocking_ids.add(synthetic.id)

    envelope_fields: dict[str, str] = {
        "pr:title": facts.pr.title,
        "pr:body": facts.pr.body,
        "diff": facts.diff,
    }
    for file_path, content in facts.files.items():
        envelope_fields[f"file:{file_path}"] = content.decode("utf-8", errors="replace")
    for field, label, nonce, opens, closes in findings_mod.scan_envelope_breaks(envelope_fields):
        synthetic = findings_mod.build_envelope_finding(
            field=field, label=label, nonce=nonce, opens=opens, closes=closes
        )
        all_findings.append(synthetic)
        corroborated_ids.add(synthetic.id)
        blocking_ids.add(synthetic.id)

    if panel.attempts:
        non_carried_universe = [oid for oid in universe_order if oid not in carried_ids]
        # E-B3b-1 (ruled 2026-09-13, "per obligation, fail-closed"):
        # `CONTRACTS.md` §12.4's subject is "a touched obligation ... requiring
        # a second family" — scoped per obligation, not per panel. A family
        # that never reported a given obligation is not a second family for
        # it, so an ordinary `Plan.participants` split across disjoint
        # obligations can never silence this guard on the one that was
        # actually touched.
        suspicious = False
        for obligation_id in non_carried_universe:
            if not _has_evidence_bearing_changed_path(
                obligation_ids=(obligation_id,), snapshot=snapshot, changed_paths=facts.changed_paths
            ):
                continue
            families_for_obligation = {
                attempt.route.family
                for attempt in panel.attempts
                if isinstance(attempt.outcome, Verdict)
                and not attempt.outcome.findings
                and attempt.outcome.obligations.get(obligation_id) is EvidenceState.VERIFIED
            }
            if len(families_for_obligation) < 2:
                suspicious = True
                break
        if suspicious:
            synthetic = findings_mod.build_suspicious_clean_finding(job_id=job.id)
            all_findings.append(synthetic)
            corroborated_ids.add(synthetic.id)
            blocking_ids.add(synthetic.id)

    # ---- step 9: assurance and escalation causes ---------------------------
    if plan.risk_class not in snapshot.policy.assurance:
        raise JudgementError(f"plan.risk_class {plan.risk_class!r} has no configured assurance value")
    required = snapshot.policy.assurance[plan.risk_class]
    assurance = evidence_mod.compute_assurance(states=obligations, required=required)

    causes: list[tuple[EscalationCause, str]] = []
    seen_causes: set[EscalationCause] = set()

    def add_cause(cause: EscalationCause, detail: str) -> None:
        if cause not in seen_causes:
            seen_causes.add(cause)
            causes.append((cause, detail))

    for obligation_id in universe_order:
        state = obligations[obligation_id]
        if state is EvidenceState.CONTRADICTORY:
            add_cause(
                EscalationCause.CONFLICTING_JUDGEMENT,
                f"obligation {obligation_id} reported contradictory evidence",
            )
        elif state in (EvidenceState.UNAVAILABLE, EvidenceState.INCOMPLETE):
            add_cause(
                EscalationCause.REQUIRED_INFORMATION,
                f"obligation {obligation_id} evidence is {state.value}",
            )
        elif state is EvidenceState.FAILED:
            add_cause(
                EscalationCause.UNRESOLVED_DECISION,
                f"obligation {obligation_id} evidence failed",
            )
        elif state in (EvidenceState.UNKNOWN, EvidenceState.NOT_VERIFIED):
            add_cause(
                EscalationCause.EVIDENCE_GAP,
                f"obligation {obligation_id} evidence is {state.value}",
            )

    for finding in all_findings:
        if finding.behaviour_changing is not False:
            add_cause(
                EscalationCause.UNRESOLVED_DECISION,
                f"finding {finding.id} is behaviour-changing",
            )

    if assurance.achieved < assurance.required:
        add_cause(
            EscalationCause.EVIDENCE_GAP,
            f"assurance {assurance.achieved}/{assurance.required} below required",
        )

    if panel.bound_reached:
        add_cause(EscalationCause.EVIDENCE_GAP, "panel reservation bound was reached")

    # ---- step 10: disposition ----------------------------------------------
    disposition: Literal["approve", "request_changes", "remediate", "escalate"]
    if blocking_ids:
        disposition = "request_changes"
    elif causes:
        disposition = "escalate"
    elif remediation_candidates:
        disposition = "remediate"
    else:
        disposition = "approve"

    # ---- step 11: construct, append, return --------------------------------
    judgement = Judgement(
        obligations=dict(obligations),
        findings=tuple(all_findings),
        corroborated=frozenset(corroborated_ids),
        blocking=frozenset(blocking_ids),
        attribution=dict(attribution),
        assurance=assurance,
        remediation_candidates=tuple(remediation_candidates),
        escalation_causes=tuple(causes),
        disposition=disposition,
        reused_from=reused_from,
    )
    rendered_body = render(judgement)

    payload: dict[str, object] = {
        "snapshot_hash": snapshot.hash,
        "protocol_hash": snapshot.protocol_hash,
        "cutoff": panel.evidence_cutoff.isoformat(),
        "facts_fetched_at": facts.fetched_at.isoformat(),
        "obligations": {oid: state.value for oid, state in judgement.obligations.items()},
        "reused_from": judgement.reused_from,
        "carried_provenance": carried_provenance,
        "contributing_attempts": [
            attempt.id for attempt in panel.attempts if isinstance(attempt.outcome, Verdict)
        ],
        "decision": (
            None
            if decision is None
            else {
                "actor": decision.actor,
                "basis": decision.basis,
                "substantiates": decision.substantiates,
                "outcome": decision.outcome,
            }
        ),
        "findings": [_finding_payload(finding) for finding in judgement.findings],
        "corroborated": sorted(judgement.corroborated),
        "blocking": sorted(judgement.blocking),
        "attribution": dict(judgement.attribution),
        "assurance": {"required": assurance.required, "achieved": assurance.achieved},
        "remediation_candidates": list(judgement.remediation_candidates),
        "escalation_causes": [
            {"cause": cause.value, "detail": detail} for cause, detail in judgement.escalation_causes
        ],
        "disposition": judgement.disposition,
        "rendered_body": rendered_body,
    }
    record.append(job.id, "judgement", payload)
    return judgement
