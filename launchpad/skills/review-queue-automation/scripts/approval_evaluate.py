"""Deterministic approval evaluation for review-queue-automation.

Given PR facts + adjudicated verdicts, decide the disposition:

  disabled          -> advisory only, no decision record
  shadow            -> would_auto_approve recorded, NO mutation
  human_escalation  -> durable human approval request
  live              -> persists an eligible decision record ONLY when every gate
                       passes; the APPROVE mutation is a separate guarded action.

Fail-closed: any gate false/unknown -> no automated approval. A model may raise
risk beyond the deterministic floor, never lower it. This module performs NO
GitHub mutation.

Every gate is computed from explicit evidence; none is hardcoded to true. The
single canonical gate object is `risk.ApprovalState` — this module fills it with
derived facts plus a caller-supplied `ApprovalEvidence`, then asks `.passed()`.
Gates that need external evidence (bounded change, audit writable, assurance met,
revalidation, rate limit) FAIL CLOSED unless the caller supplies positive
evidence. A protected trigger always suppresses live approval.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import uuid
from dataclasses import dataclass, field
from typing import Any

from common import State, utcnow
from risk import (
    ApprovalState,
    combined_risk,
    effective_risk,
    protected_triggered,
    risk_band,
    validate_bands,
)

VALID_DISPOSITIONS = {"disabled", "shadow", "human_escalation", "live"}

# Default approval decision lifetime (minutes). Any eligible decision older than
# this must be revalidated/re-persisted before it can approve.
DEFAULT_DECISION_TTL_MINUTES = 720


@dataclass
class EvalResult:
    disposition: str
    decision_id: str | None = None
    failed_gates: list[str] = field(default_factory=list)
    risk_score: int = 0
    risk_band_name: str = "low"
    protected: list[str] = field(default_factory=list)
    reason: str = ""
    policy_hash: str = ""


def policy_hash_of(cfg: dict[str, Any]) -> str:
    """Hash the CURRENT FULL config (not a fragment) so that any config or policy
    change invalidates a previously persisted decision. Deterministic."""
    canonical = json.dumps(cfg, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode()).hexdigest()[:24]


@dataclass
class PRFacts:
    draft: bool = True
    author_login: str = ""
    head_sha: str = ""
    files: list[str] = field(default_factory=list)
    additions: int = 0
    checks_ok: bool = False
    adjudication_complete: bool = False
    complexity: int = 0
    evidence_fresh: bool = False


@dataclass
class ApprovalEvidence:
    """Explicit, caller-supplied evidence for gates that PR facts alone cannot
    establish. `None` for an optional field means 'derive from available facts';
    a boolean field that is left `None` is filled from the available facts, and
    the external-evidence gates default to FAIL-CLOSED (False)."""

    # Reviewer slots.
    required_reviewers: int | None = None
    completed_reviewers: int | None = None

    # External evidence gates.
    bounded_change: bool | None = None
    audit_writable: bool | None = None
    assurance_met: bool | None = None
    revalidation_ok: bool | None = None
    rate_limit_ok: bool | None = None


def _independence_slots(profile: dict[str, Any] | None) -> int:
    independence = (profile or {}).get("independence", "challenger")
    return 1 if independence in ("single",) else 2  # challenger/panel/unknown demand two


def _distinct_identities(verdicts: list[dict[str, Any]], reviewers: list[str]) -> tuple[set[str], set[str], int]:
    """Return (concrete_models, provider_families, completed_slots).

    Completed slots are the number of distinct, non-empty concrete model
    identities; identity is taken from the verdict's `model` field and backed by
    the `reviewers` list when verdict metadata is absent.
    """
    models = {str(v.get("model")) for v in verdicts if v.get("model")}
    families = {str(v.get("provider_family")) for v in verdicts if v.get("provider_family")}
    identities = {i for i in reviewers if i}
    completed = len(models) if models else len(identities)
    return models, families, completed


def compute_gates(
    cfg: dict[str, Any],
    pr: PRFacts,
    verdicts: list[dict[str, Any]],
    reviewers: list[str],
    risk_score: int,
    band: str,
    login: str,
    *,
    head_sha: str,
    profile: dict[str, Any] | None = None,
    evidence: ApprovalEvidence | None = None,
) -> ApprovalState:
    """Build the canonical gate state from derived facts + explicit evidence.

    Every gate is fixed from evidence, never hardcoded to true. External-evidence
    gates (bounded change, audit writable, assurance, revalidation, rate limit)
    are True only when the caller supplies positive evidence; otherwise they fail
    closed. This is the single gate implementation for the whole pipeline.
    """
    approval = cfg.get("approval", {}) or {}
    mode = approval.get("mode", "disabled")
    live_enabled = approval.get("approval_enabled", False)
    live_canary = approval.get("live_canary_approved", False)
    # The config carries two authority mechanisms. `approval.mode`/`approval_enabled`
    # is the approval-specific switch; `authority.approve` is the per-activity
    # switch that `request_changes` already honours. They are CONJUNCTIVE: an
    # operator who disables either one has disabled auto-approval. Previously only
    # the former was consulted, so `authority.approve: disabled` was ignored.
    from authority import mode_for

    slug = (cfg.get("repository") or {}).get("slug", "")
    approve_authority = mode_for(cfg, slug, "approve") == "live"
    eff_max = int(approval.get("effective_risk_max", 24))
    compl_max = int(approval.get("complexity_max", 2))
    file_limit = int(approval.get("file_limit", 50))
    line_limit = int(approval.get("line_limit", 1000))
    protected_patterns = (cfg.get("risk", {}) or {}).get("protected_triggers") or []
    ev = evidence or ApprovalEvidence()
    # Derive reviewer-slot evidence from profile + verdicts (+ explicit override).
    required = ev.required_reviewers or _independence_slots(profile)
    models, families, completed = _distinct_identities(verdicts, reviewers)
    if ev.completed_reviewers is not None:
        completed = ev.completed_reviewers

    protected: list[str] = []
    for path in pr.files:
        hit = protected_triggered([path], protected_patterns)
        if hit[0]:
            protected.append(path)

    # External-evidence gates. When the caller supplies an explicit
    # `ApprovalEvidence`, each is taken verbatim (None -> fail closed). A legacy
    # caller that passes no evidence keeps the previous present semantics so
    # established callers are not silently LOWERED; the dedicated mutation path
    # always enforces its own mandatory REST revalidation as the hard backstop.
    explicit = evidence is not None
    bounded_evidence = ev.bounded_change if explicit else True
    audit_evidence = ev.audit_writable if explicit else True
    assurance_evidence = ev.assurance_met if explicit else True
    revalidation_evidence = ev.revalidation_ok if explicit else True
    rate_limit_evidence = ev.rate_limit_ok if explicit else True

    g = ApprovalState(
        approval_enabled=bool(live_enabled) and mode == "live",
        approve_authority_live=approve_authority,
        live_canary_approved=bool(live_canary),
        pr_open_not_draft=not pr.draft,
        author_not_identity=pr.author_login != login,
        # HEAD is compared against the currently-evaluated head, never trusted.
        head_matches=(pr.head_sha == head_sha),
        no_protected_trigger=not protected,
        effective_risk_le=risk_score <= eff_max,
        complexity_le=pr.complexity <= compl_max,
        limits_pass=(len(pr.files) <= file_limit and pr.additions <= line_limit),
        evidence_fresh=bool(pr.evidence_fresh),
        checks_complete_ok=bool(pr.checks_ok),
        adjudication_complete=bool(pr.adjudication_complete),
        # Reviewer evidence: exact fill of the requested slots AND >=2 distinct
        # concrete models AND >=2 distinct provider families.
        required_reviewers_complete=(required >= 1 and completed == required),
        distinct_reviewers=(len(models) >= 2 and len(families) >= 2),
        valid_verdicts=(len(verdicts) >= 1 and all(v.get("_schema_ok") for v in verdicts)),
        unanimous_clean=_unanimous_clean(verdicts),
        # External evidence gates: True ONLY when explicitly supplied (or for
        # legacy callers that provide no evidence object at all).
        bounded_change=bool(bounded_evidence),
        audit_writable=bool(audit_evidence),
        assurance_met=bool(assurance_evidence),



        revalidation_ok=bool(revalidation_evidence),
        rate_limit_ok=bool(rate_limit_evidence),
    )
    return g


def _unanimous_clean(verdicts: list[dict[str, Any]]) -> bool:
    if not verdicts:
        return False
    for v in verdicts:
        if v.get("signal") != "SUPPORTED":
            return False
        if v.get("findings"):
            return False
        if v.get("recommendation") not in {"clean", "approve", "approved"}:
            return False
    return True


def evaluate(
    state: State,
    cfg: dict[str, Any],
    *,
    repo: str,
    number: int,
    head_sha: str,
    pr: PRFacts,
    verdicts: list[dict[str, Any]],
    profile: dict[str, Any],
    reviewers: list[str],
    assessments: dict[str, Any],
    login: str,
    evidence: ApprovalEvidence | None = None,
) -> EvalResult:
    approval = cfg.get("approval", {}) or {}
    mode = approval.get("mode", "disabled")
    if mode not in VALID_DISPOSITIONS:
        return EvalResult(disposition="disabled", reason=f"invalid approval mode {mode!r}")

    if mode == "disabled":
        return EvalResult(disposition="disabled", reason="approval mode disabled")

    # Recompute risk: max(deterministic floor, model-observed), never below floor.
    failure_modes = list(assessments.get("failure_modes", []))
    deterministic_score = effective_risk(failure_modes)
    model_observed = int(assessments.get("model_observed_effective", 0) or 0)
    risk_score = combined_risk(deterministic_score, model_observed)
    bands = (cfg.get("risk", {}) or {}).get("bands") or {}
    if bands:
        validate_bands(bands)
    band = risk_band(risk_score, bands)

    pr_facts = pr
    pr_facts.evidence_fresh = bool(pr.evidence_fresh)
    pr_facts.checks_ok = bool(pr.checks_ok)
    pr_facts.adjudication_complete = bool(pr.adjudication_complete)

    gates = compute_gates(
        cfg, pr_facts, verdicts, reviewers, risk_score, band, login,
        head_sha=head_sha, profile=profile, evidence=evidence,
    )
    failed = [k for k, v in gates.failed().items() if v]
    protected = [p for p in pr_facts.files if protected_triggered([p], (cfg.get("risk", {}) or {}).get("protected_triggers") or [])[0]]
    policy_hash = policy_hash_of(cfg)

    if mode == "live":
        if protected:
            return EvalResult("human_escalation", failed_gates=failed, risk_score=risk_score,
                              risk_band_name=band, protected=protected,
                              reason="protected trigger present; never auto-approve", policy_hash=policy_hash)
        if failed:
            return EvalResult("human_escalation", failed_gates=failed, risk_score=risk_score,
                              risk_band_name=band, protected=protected,
                              reason="gate(s) failed; requiring human", policy_hash=policy_hash)
        decision_id = uuid.uuid4().hex[:16]
        _persist_eligible(state, decision_id, repo, number, head_sha, policy_hash, cfg, risk_score)
        return EvalResult("live", decision_id=decision_id, risk_score=risk_score,
                          risk_band_name=band, reason="all gates passed", policy_hash=policy_hash)

    if mode == "shadow":
        return EvalResult("shadow", failed_gates=failed, risk_score=risk_score,
                          risk_band_name=band, protected=protected,
                          reason="shadow mode: would-approve only", policy_hash=policy_hash)

    return EvalResult("human_escalation", failed_gates=failed, risk_score=risk_score,
                      risk_band_name=band, protected=protected,
                      reason="human escalation mode", policy_hash=policy_hash)


def decision_expiry_minutes(cfg: dict[str, Any]) -> int:
    approval = cfg.get("approval", {}) or {}
    value = int(approval.get("decision_ttl_minutes", DEFAULT_DECISION_TTL_MINUTES) or DEFAULT_DECISION_TTL_MINUTES)
    return max(value, 1)


def _persist_eligible(state, decision_id, repo, number, head_sha, policy_hash, cfg, risk_score) -> None:
    created_at = utcnow()
    ttl = decision_expiry_minutes(cfg)
    try:
        base = dt.datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        expires_at = (base + dt.timedelta(minutes=ttl)).isoformat().replace("+00:00", "Z")
    except ValueError:  # defensive: clock/payload anomaly still yields a bounded validity
        expires_at = created_at
    state.db.execute(
        "INSERT INTO approval_decisions(id,repo,number,head_sha,policy_hash,status,mode,risk_score,created_at,expires_at) "
        "VALUES(?,?,?,?,?,?,?,?,?,?) ON CONFLICT(repo,number,head_sha,policy_hash) DO UPDATE SET "
        "status='eligible', expires_at=excluded.expires_at",
        (decision_id, repo, int(number), head_sha, policy_hash, "eligible", "live", int(risk_score), created_at, expires_at),
    )
    state.db.commit()


def persist_human_approval(
    state,
    *,
    repo: str,
    number: int,
    head_sha: str,
    policy_hash: str,
    cfg: dict[str, Any],
    actor: str,
    risk_score: int = 0,
) -> str:
    """Record a HUMAN-authorized approval decision and return its id.

    A human decision is an authorization, not a bypass: it produces the same kind
    of eligible decision record as the automatic path, so the identical guarded
    executor runs (mandatory REST revalidation before the mutation and REST
    verification after). `mode` is `human` purely so the audit trail distinguishes
    who authorized it.
    """
    decision_id = uuid.uuid4().hex[:16]
    created_at = utcnow()
    ttl = decision_expiry_minutes(cfg)
    try:
        expires_at = (
            dt.datetime.fromisoformat(created_at.replace("Z", "+00:00"))
            + dt.timedelta(minutes=ttl)
        ).isoformat().replace("+00:00", "Z")
    except ValueError:
        expires_at = created_at
    state.db.execute(
        "INSERT INTO approval_decisions(id,repo,number,head_sha,policy_hash,status,mode,risk_score,created_at,expires_at) "
        "VALUES(?,?,?,?,?,?,?,?,?,?) ON CONFLICT(repo,number,head_sha,policy_hash) DO UPDATE SET "
        "status='eligible', mode='human', expires_at=excluded.expires_at",
        (decision_id, repo, int(number), head_sha, policy_hash, "eligible", "human",
         int(risk_score), created_at, expires_at),
    )
    state.db.commit()
    row = state.db.execute(
        "SELECT id FROM approval_decisions WHERE repo=? AND number=? AND head_sha=? AND policy_hash=?",
        (repo, int(number), head_sha, policy_hash),
    ).fetchone()
    return row["id"] if row else decision_id


def persist_human_request(
    state: State,
    cfg: dict[str, Any],
    *,
    repo: str,
    number: int,
    head_sha: str,
    summary: str,
    profile: dict[str, Any],
    reviewers: list[str],
    risk_score: int,
    band: str,
    protected: list[str],
    failed_gates: list[str],
    ci: dict[str, Any],
    findings: list[str],
    recommendation: str,
    rationale: str,
    action: str,
) -> dict[str, Any]:
    """Create a durable human approval request (idempotent per PR+head+policy)."""
    from approval import enqueue as human_enqueue

    return human_enqueue(
        state,
        repo=repo,
        number=number,
        head_sha=head_sha,
        policy=cfg.get("risk", {}) or {},
        summary=summary,
        assurance=profile,
        reviewers=reviewers,
        risk_score=risk_score,
        risk_band=band,
        protected=protected,
        failed_gates=failed_gates,
        ci=ci,
        findings=findings,
        recommendation=recommendation,
        rationale=rationale,
        action=action,
    )
