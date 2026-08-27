"""Validated, resumable job state machine for review-queue-automation.

The core flow is:

    detected -> preflight -> evidence -> assurance -> adjudication
    adjudication -> approval_evaluation
    approval_evaluation -> would_auto_approve | approval_revalidation |
                           human_approval_pending | advisory_action |
                           changes_requested | degraded | safe_stop | superseded
    would_auto_approve -> approval_revalidation
    approval_revalidation -> approval_action
    approval_action -> completed_auto_approved
    human_approval_pending -> approval_revalidation | completed_human_declined |
                              advisory_action | degraded | safe_stop | superseded
    advisory_action -> completed_advisory | degraded | safe_stop | superseded
    degraded -> safe_stop | advisory_action | human_required | superseded
    safe_stop / completed_* / superseded are terminal sinks.

Degradation ladder (authority descends, evidence/risk/assurance never reduced):

    live (approval) -> human pending -> advisory -> degraded evidence ->
    safe stop

`degraded`, `advisory_action` and `human_approval_pending` may descend to the
next-lower rung (advisory_action / degraded / safe_stop respectively) so a
downgrade always has a deterministic, legal next state. `safe_stop` is a
safety sink reachable from every nonterminal state so a persistence or logging
failure can stop the affected job without inventing a transition.

Legacy action path (adjudication -> action -> completed) is preserved for
existing callers but now coexists with the approval-aware flow.

Every move must go through `assert_transition`; `State.transition` refuses to
move a job that does not exist (raises without emitting a success event).
"""

from __future__ import annotations

from typing import Any

from errors import JobBlockingError

ALL_STATES = frozenset(
    {
        "detected",
        "preflight",
        "evidence",
        "assurance",
        "adjudication",
        "approval_evaluation",
        "would_auto_approve",
        "approval_revalidation",
        "approval_action",
        "human_approval_pending",
        "advisory_action",
        "completed_auto_approved",
        "completed_human_declined",
        "completed_advisory",
        "action",          # preserved legacy sink -> completed
        "completed",       # legacy terminal
        # explicit lifecycle states
        "ready_for_review",
        "changes_requested",
        "requested_changes_fixed",
        "author_triage",
        "closed",
        "merged",
        "degraded_draft",
        "degraded",
        "safe_stop",
        "retryable",
        "held",
        "human_required",
        "superseded",
    }
)

TRANSITIONS: dict[str, frozenset[str]] = {
    "detected": frozenset({"preflight", "evidence", "assurance", "ready_for_review", "author_triage", "closed", "merged", "held", "human_required", "retryable", "superseded", "safe_stop"}),
    "ready_for_review": frozenset({"evidence", "assurance", "author_triage", "closed", "merged", "superseded", "safe_stop"}),
    "changes_requested": frozenset({"requested_changes_fixed", "advisory_action", "author_triage", "closed", "merged", "superseded", "safe_stop"}),
    "requested_changes_fixed": frozenset({"evidence", "assurance", "closed", "merged", "superseded", "safe_stop"}),
    "author_triage": frozenset({"evidence", "assurance", "changes_requested", "advisory_action", "closed", "merged", "superseded", "safe_stop"}),
    "closed": frozenset({"superseded"}),
    "merged": frozenset({"superseded"}),
    "preflight": frozenset({"evidence", "held", "human_required", "superseded", "safe_stop"}),
    "evidence": frozenset({"assurance", "retryable", "held", "human_required", "superseded", "safe_stop"}),
    "assurance": frozenset({"adjudication", "degraded_draft", "retryable", "held", "human_required", "superseded", "safe_stop"}),
    "adjudication": frozenset({"action", "approval_evaluation", "human_required", "held", "retryable", "superseded", "safe_stop"}),
    "approval_evaluation": frozenset(
        {"would_auto_approve", "approval_revalidation", "human_approval_pending",
         "advisory_action", "changes_requested", "degraded", "safe_stop", "superseded"}
    ),
    "would_auto_approve": frozenset({"approval_revalidation", "superseded", "safe_stop"}),
    "approval_revalidation": frozenset(
        {"approval_action", "human_approval_pending", "advisory_action", "degraded", "safe_stop", "superseded"}
    ),
    "approval_action": frozenset({"completed_auto_approved", "changes_requested", "superseded", "safe_stop"}),
    "human_approval_pending": frozenset(
        {"approval_revalidation", "completed_human_declined", "advisory_action", "degraded", "safe_stop", "superseded"}
    ),
    "advisory_action": frozenset({"completed_advisory", "changes_requested", "degraded", "safe_stop", "superseded"}),
    # legacy surfaces
    "action": frozenset({"completed", "held", "human_required", "superseded", "approval_evaluation", "safe_stop"}),
    "degraded_draft": frozenset({"retryable", "held", "human_required", "superseded", "degraded", "safe_stop"}),
    "degraded": frozenset({"advisory_action", "safe_stop", "human_required", "superseded"}),
    "safe_stop": frozenset({"superseded"}),
    "retryable": frozenset({"evidence", "assurance", "held", "human_required", "superseded", "safe_stop"}),
    "held": frozenset({"human_required", "superseded", "safe_stop"}),
    "human_required": frozenset({"superseded", "approval_revalidation", "advisory_action", "safe_stop"}),
    "completed_auto_approved": frozenset({"superseded"}),
    "completed_human_declined": frozenset({"superseded"}),
    "completed_advisory": frozenset({"superseded"}),
    "completed": frozenset({"superseded"}),
    "superseded": frozenset(),
}

assert ALL_STATES == frozenset(TRANSITIONS), "transition table misses a state"


def can_transition(current: str | None, target: str) -> bool:
    if current is None:
        return target == "detected"
    if target not in ALL_STATES or current not in TRANSITIONS:
        return False
    return target in TRANSITIONS[current]


def assert_job_exists(current: str | None) -> None:
    if current is None:
        raise JobBlockingError("state transition on nonexistent job <new> -> <target> rejected")


def assert_transition(from_state: str | None, target: str) -> None:
    if not can_transition(from_state, target):
        allowed = sorted(TRANSITIONS.get(from_state or "detected", [])) or ["<none>"]
        raise JobBlockingError(
            f"invalid state transition: {from_state} -> {target} (allowed: {','.join(allowed)})"
        )


def transition_entries() -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    for source, targets in TRANSITIONS.items():
        for target in sorted(targets):
            out.append((source, target))
    return out


def describe() -> dict[str, Any]:
    return {
        "states": sorted(ALL_STATES),
        "transitions": {k: sorted(v) for k, v in TRANSITIONS.items()},
    }