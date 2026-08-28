"""Deterministic action gates for review-queue-automation.

Approval and request-changes are separate, independently-authorized actions.

Approval ELIGIBILITY is NOT decided here: it lives in
`approval_evaluate.compute_gates`, which owns the canonical `ApprovalState` gate
set and is the path the dispatcher actually runs. A second approval gate used to
live in this module; it had no callers, so it could drift from the live path
while still looking authoritative. It was removed rather than left as a trap.

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
