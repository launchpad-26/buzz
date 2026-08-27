"""Deterministic action gates for review-queue-automation.

Approval and request-changes are separate, independently-authorized actions with
distinct gates:

- `approve_gate`  requires: live `approve` authority; open non-draft PR; exact HEAD;
  successful required checks; satisfied reviewer requirements; no self-approval;
  no verified blocker; no unresolved high-severity finding; sufficient evidence;
  achieved assurance >= required; risk/uncertainty within thresholds; applicable
  policy permission; a non-expired, non-superseded decision; successful final
  revalidation; an unused idempotency key.

- `request_changes_gate` requires: live `request_changes` authority; a VERIFIED
  blocking defect tied to the current code and exact HEAD; sufficient evidence;
  successful final revalidation. Suggestions / uncertain findings are comments or
  human recommendations, never request-changes.

Final revalidation is INJECTED (a callable returning fresh GitHub state), never
hardcoded to success. Every gate is fail-closed: any unknown/false input denies
the action.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

from authority import can_act, mode_for
from risk import AssuranceEvaluation, compute_assurance

# Revalidation outcome: caller supplies a deterministic check; None/False denies.
Revalidation = Callable[[], bool] | None


@dataclass
class Gate:
    allowed: bool = False
    reason: str = ""
    failed: list[str] = field(default_factory=list)

    def deny(self, reason: str, gate: str | None = None) -> None:
        self.allowed = False
        self.reason = reason
        if gate:
            self.failed.append(gate)

    def as_dict(self) -> dict[str, Any]:
        return {"allowed": self.allowed, "reason": self.reason, "failed": self.failed}


def approve_gate(
    *,
    cfg: dict[str, Any],
    repo: str,
    head_sha: str,
    pr: dict[str, Any],
    reviewers_complete: bool,
    no_self_approval: bool,
    blockers: list[str],
    high_findings: list[str],
    assurance: AssuranceEvaluation | None,
    policy_permits: bool,
    decision_usable: bool,
    idempotency_key_unused: bool,
    revalidate: Revalidation,
    approval_authority_ok: Callable[[], bool] | None = None,
) -> Gate:
    """The single gate for an automatic APPROVE action. Fail-closed."""
    g = Gate()
    # authority must be live
    if not can_act(cfg, repo, "approve", repo_hard_gate_ok=True):
        g.deny("approve authority is not live", "authority")
        return g
    if approval_authority_ok is not None and not approval_authority_ok():
        g.deny("approve authority not live", "authority")
        return g
    if pr.get("draft", True):
        g.deny("PR is draft or unknown", "open_non_draft")
    if pr.get("head") and pr["head"] != head_sha:
        g.deny("stale HEAD for approval", "exact_head")
    if not reviewers_complete:
        g.deny("reviewer requirements not met", "reviewers")
    if not no_self_approval:
        g.deny("self-approval prohibited", "no_self_approval")
    if blockers:
        g.deny(f"verified blocker present: {', '.join(blockers[:3])}", "no_blocker")
    if high_findings:
        g.deny("unresolved high-severity finding", "no_high_finding")
    if assurance is None or not assurance.assurance_met:
        g.deny("achieved assurance below required", "assurance")
    if not policy_permits:
        g.deny("policy does not permit approval", "policy_permission")
    if not decision_usable:
        g.deny("decision expired or superseded", "decision_usable")
    if not idempotency_key_unused:
        g.deny("idempotency key already used", "idempotency")
    if revalidate is None or not revalidate():
        g.deny("final revalidation failed or unavailable", "final_revalidation")
    g.allowed = len(g.failed) == 0
    if g.allowed:
        g.reason = "all approval gates pass"
    return g


def request_changes_gate(
    *,
    cfg: dict[str, Any],
    repo: str,
    head_sha: str,
    pr: dict[str, Any],
    verified_blocker: bool,
    blocker_evidence_sufficient: bool,
    assurance: AssuranceEvaluation | None,
    revalidate: Revalidation,
    rc_authority_ok: Callable[[], bool] | None = None,
) -> Gate:
    """The single gate for a CHANGES_REQUESTED action. Fail-closed, distinct from
    approval. A verified blocking defect tied to the current HEAD is required."""
    g = Gate()
    if not can_act(cfg, repo, "request_changes", repo_hard_gate_ok=True):
        g.deny("request_changes authority is not live", "authority")
        return g
    if rc_authority_ok is not None and not rc_authority_ok():
        g.deny("request_changes authority not live", "authority")
        return g
    if pr.get("head") and pr["head"] != head_sha:
        g.deny("stale HEAD for request-changes", "exact_head")
    if not verified_blocker:
        g.deny("no verified blocking defect; suggestions stay comments", "verified_blocker")
    if not blocker_evidence_sufficient:
        g.deny("blocker lacks sufficient evidence", "blocker_evidence")
    if assurance is None or not assurance.assurance_met:
        g.deny("achieved assurance below required for a blocking claim", "assurance")
    if revalidate is None or not revalidate():
        g.deny("final revalidation failed or unavailable", "final_revalidation")
    g.allowed = len(g.failed) == 0
    if g.allowed:
        g.reason = "all request-changes gates pass"
    return g
