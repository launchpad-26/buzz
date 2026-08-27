#!/usr/bin/env python3
"""Review-queue dispatcher: drive the assurance loop for one job.

- Requires a valid, git-ignored repo-local config; else it refuses dispatch and
  directs the operator to onboarding (no GitHub/model activity).
- Loads persisted PR/job/evidence facts (head, draft, author, files, sizes,
  checks, evidence timestamps) from SQLite and the job artifact dir; it never
  fabricates them.
- Moves jobs along a validated state table (states.py) and logs every transition
  and assurance attempt to the configured otel-jsonl directory.
- A partial first-review panel -> `degraded_draft` (retains verdicts, no
  mutation, no re-run without new evidence). A complete panel ->
  `adjudication` -> `approval_evaluation`.
- MISSING_EVIDENCE performs exactly ONE bounded deterministic evidence gather;
  if none is available it escalates. It never re-runs the identical panel.
- Human approval requests carry the job id and a full-config/policy hash; a
  changed head or policy supersedes them.
- A state-persistence or audit-logging failure safe-stops the affected job;
  unrelated jobs continue (the sweeper is non-blocking).
- `run_job` reports the ACTUAL final state it reached, not a placeholder.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import sys
from typing import Any

from assurance import Profile, drive
from authority import mode_for
from common import State, expand_path
from config import load_repo_config
from errors import EvidenceIncompleteError, JobBlockingError
from evidence import collect as collect_evidence
from logging_otel import JobLogger
from approval_evaluate import PRFacts, evaluate as eval_approval
from approval import enqueue as enqueue_human, supersede_for_head, supersede_for_policy
from verdict import parse_verdict_or_none, validate_verdict

# panel.py is the assurance/panel owner. The dispatcher loads it lazily so the
# module stays importable and so tests can patch run_panel/decide_assurance
# before any panel code is touched. Real dispatch calls the real functions.
run_panel = None
decide_assurance = None


def _ensure_panel() -> None:
    global run_panel, decide_assurance
    if run_panel is not None and decide_assurance is not None:
        return
    from panel import decide_assurance as _da, run_panel as _rp  # noqa: E402
    run_panel = _rp
    decide_assurance = _da


class PartialPanel(Exception):
    """A reviewer slot produced no fresh verdict after its fallback chain ran."""

    def __init__(self, result: dict[str, Any]):
        super().__init__(
            f"partial panel: {len(result['completed_reviewers'])}/{result['required_reviewers']}"
        )
        self.result = result


class SafeStopSignal(Exception):
    """Recoverable state-persistence or audit-logging failure; stop the job safely."""


# Degradation ladder: high authority on the left, low on the right. `degrade()`
# moves a job down EXACTLY one reachable rung and never upward; evidence, risk,
# assurance and reviewer authority are never reduced by a downgrade step.
#     live -> shadow -> human pending -> advisory -> degraded evidence -> safe stop
_DEGRADE_RANK = {
    "approval_revalidation": 6,   # live
    "would_auto_approve": 5,      # shadow marker
    "human_approval_pending": 4,  # human pending
    "advisory_action": 3,         # advisory
    "degraded_draft": 2,          # degraded evidence
    "degraded": 2,                # degraded evidence
    "safe_stop": 1,
    # `superseded` and the completed_* states are terminal sinks and are NOT
    # ranked, so `degrade` refuses and raises JobBlockingError for them.
}


def _make_logger(local_cfg: dict[str, Any], job_id: str, repo: str, number: int, lane: str) -> JobLogger | None:
    logging_cfg = local_cfg.get("logging", {})
    log_root = logging_cfg.get("directory")
    if not log_root:
        return None
    return JobLogger(
        log_root,
        job_id,
        repo=repo,
        number=number,
        lane=lane,
        max_stderr=int(logging_cfg.get("max_stderr_bytes", 8192)),
    )


def _transition_guarded(
    state: State,
    job_id: str,
    target: str,
    *,
    logger=None,
    reason: str | None = None,
    phase: str = "state",
) -> str:
    """Transition, converting any non-degradable persistence failure into SafeStop.

    An illegal / nonexistent transition still raises JobBlockingError (fail
    loudly). A DB write failure or log write failure safe-stops the job.
    """
    try:
        state.transition(job_id, target, logger=logger, phase=phase, reason=reason)
    except JobBlockingError:
        raise
    except Exception as exc:
        raise SafeStopSignal(f"state {phase} transition/persistence failure: {exc}") from exc
    return target


def _log(logger, level: str, *, body: str, phase: str, outcome: str = "", attributes: dict[str, Any] | None = None) -> None:
    if logger is None:
        return
    try:
        getattr(logger, level)(body=body, phase=phase, outcome=outcome, attributes=attributes)
    except Exception as exc:
        raise SafeStopSignal(f"audit logging failure: {exc}") from exc


def _arrive_safe_stop(state: State, job: dict[str, Any], logger, reason: str) -> dict[str, Any]:
    """Best-effort transition to safe_stop; swallow failures so the caller still results."""
    job_id = job["job_id"]
    try:
        state.transition(job_id, "safe_stop", logger=logger, phase="dispatch", reason=reason)
    except Exception:
        pass
    return {
        "job": job_id, "repo": job.get("repo", ""), "number": job.get("number"),
        "status": "safe_stop", "decision": "SAFE_STOP", "reason": reason,
    }



def _ledger_record(state: State, job: dict[str, Any], head_sha: str, kind: str,
                   payload: dict[str, Any], *, entry_key: str = "",
                   snapshot_meta: dict[str, Any] | None = None) -> None:
    """Append a ledger entry. Never raises: the ledger explains decisions, so a
    ledger problem must not change one. Failures surface in the JSONL log."""
    try:
        from ledger import record

        meta = snapshot_meta or {}
        record(
            state, job_id=job["job_id"], repo=job["repo"], number=job["number"],
            head_sha=head_sha, kind=kind, payload=payload, entry_key=entry_key,
            snapshot_hash=meta.get("snapshot_hash", "") or "",
            policy_version=meta.get("policy_version", "") or "",
        )
    except Exception:
        pass


def _pr_payload(state: State, repo: str, number: int) -> dict[str, Any]:
    row = state.db.execute(
        "SELECT payload FROM prs WHERE repo=? AND number=?", (repo, number)
    ).fetchone()
    if not row:
        return {}
    try:
        payload = json.loads(row["payload"])
        return payload if isinstance(payload, dict) else {}
    except Exception:
        return {}


def _evidence_meta(state: State, job_id: str) -> dict[str, Any]:
    path = state.job_dir(job_id) / "evidence.json"
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _evidence_fresh(local_cfg: dict[str, Any], collected_at: str) -> bool:
    """Fresh only when job evidence.json has a timestamp within the bound."""
    if not collected_at:
        return False
    try:
        ts = dt.datetime.fromisoformat(collected_at.replace("Z", "+00:00"))
    except ValueError:
        return False
    max_age = int((local_cfg.get("approval") or {}).get("evidence_max_age_seconds", 3600))
    return (dt.datetime.now(dt.timezone.utc) - ts).total_seconds() <= max_age


def _load_pr_facts(state: State, job: dict[str, Any], head_sha: str, local_cfg: dict[str, Any]) -> PRFacts:
    """Build PR facts from PERSISTED prs payload + evidence.json (never hardcoded)."""
    repo = job["repo"]
    number = job["number"]
    job_id = job["job_id"]
    payload = _pr_payload(state, repo, number)
    evidence = _evidence_meta(state, job_id)
    context = evidence.get("context") or {}

    raw_files = payload.get("files") or []
    files: list[str] = []
    for f in raw_files:
        if isinstance(f, dict):
            files.append(str(f.get("filename", "")))
        elif isinstance(f, str):
            files.append(f)

    try:
        additions = int(payload.get("additions", 0) or 0)
    except (TypeError, ValueError):
        additions = 0

    user = payload.get("user")
    author = user.get("login", "") if isinstance(user, dict) else ""
    if not author:
        author = context.get("author", "")

    draft = bool(payload.get("draft"))
    if not draft and "draft" in context:
        draft = bool(context.get("draft"))

    checks = evidence.get("checks") or []
    checks_ok = bool(checks) and all(
        isinstance(c, dict) and c.get("conclusion") == "SUCCESS" for c in checks
    )

    # PRFacts.head_sha must be the OBSERVED current head, so the `head_matches`
    # gate can actually compare it against the head that was reviewed. Falling
    # back to the job's own head_sha here would make that gate tautological (it
    # would compare the reviewed head with itself and could never fail). An
    # unknown observed head stays empty, which fails the gate closed.
    ph = payload.get("head")
    payload_head = ph.get("sha", "") if isinstance(ph, dict) else ""
    observed_head = payload_head or context.get("head", "")

    try:
        complexity = int(payload.get("complexity", 0) or 0)
    except (TypeError, ValueError):
        complexity = 0

    return PRFacts(
        draft=draft,
        author_login=author,
        head_sha=observed_head,
        files=files,
        additions=additions,
        checks_ok=checks_ok,
        adjudication_complete=True,
        complexity=complexity,
        evidence_fresh=_evidence_fresh(local_cfg, evidence.get("collected_at", "")),
    )


def _collected_verdicts(state: State, job_id: str) -> list[dict[str, Any]]:
    """Consume schema-valid verdict objects; invalid slots are omitted (never forged)."""
    artifact_dir = state.job_dir(job_id)
    out: list[dict[str, Any]] = []
    for f in ("review-A.txt", "review-B.txt"):
        p = artifact_dir / f
        if not p.is_file():
            continue
        try:
            text = p.read_text(encoding="utf-8")
        except OSError:
            continue
        parsed = parse_verdict_or_none(text)
        if not isinstance(parsed, dict):
            continue
        ok, _ = validate_verdict(text)
        parsed["_schema_ok"] = bool(ok)
        out.append(parsed)
    return out


def _evidence_missing(
    state: State,
    local_cfg: dict[str, Any],
    job: dict[str, Any],
    logger,
    message: str,
) -> dict[str, Any]:
    """MISSING_EVIDENCE: one bounded deterministic gather if available, else escalate."""
    job_id = job["job_id"]
    try:
        collect_evidence(local_cfg, state, job["repo"], job["number"], job["lane"], job_id)
    except Exception as gather_exc:
        reason = f"evidence missing and no bounded gather available: {gather_exc}"
        _transition_guarded(state, job_id, "human_required", logger=logger,
                            phase="assurance", reason=reason)
        return {"job": job_id, "repo": job.get("repo"), "number": job.get("number"),
                "status": "human_required", "decision": "EVIDENCE_INCOMPLETE", "reason": reason}
    reason = (
        "evidence missing; one bounded deterministic gather completed; "
        "no identical panel re-run"
    )
    _transition_guarded(state, job_id, "degraded_draft", logger=logger,
                        phase="assurance", reason=reason)
    return {"job": job_id, "repo": job.get("repo"), "number": job.get("number"),
            "status": "degraded_draft", "decision": "EVIDENCE_INCOMPLETE", "reason": reason}


def notify_human(local_cfg: dict[str, Any], request: dict[str, Any]) -> dict[str, Any]:
    """Deliver a queued human request over the configured transport.

    A failure here must NOT remove or decline the request: the item stays in the
    pending queue so it is never lost to a transient notification problem. Every
    caller therefore wraps this and preserves the row on exception.

    Returns the delivery record from `notify.deliver`.
    """
    from notify import deliver

    return deliver(local_cfg, request)


def _deliver_notification(
    local_cfg: dict[str, Any], request: dict[str, Any], logger
) -> str:
    """Deliver a queued request and describe the outcome truthfully.

    Never raises: the durable queue row is the record of work, so a delivery
    problem must not fail the job. The returned string distinguishes an actual
    delivery from "queued but nothing was sent", so a missing transport cannot
    look like a successful notification.
    """
    try:
        record = notify_human(local_cfg, request)
    except Exception as exc:  # delivery only; the request stays pending
        _log(logger, "warning", body="notification failure; request preserved",
             phase="approval", outcome="notification_failed")
        return f"notification failure (request preserved): {exc}"
    if isinstance(record, dict) and not record.get("delivered", False):
        detail = record.get("detail", "no transport configured")
        _log(logger, "warning", body=f"human request queued but not delivered: {detail}",
             phase="approval", outcome="not_delivered")
        return f"not delivered ({detail})"
    transport = record.get("transport", "unknown") if isinstance(record, dict) else "unknown"
    return f"delivered via {transport}"


def degrade(
    state: State,
    job_id: str,
    *,
    reason: str,
    logger=None,
    phase: str = "degradation",
) -> str:
    """Move a job EXACTLY one reachable rung down the degradation ladder.

    Never raises evidence/risk/assurance/authority. `reason` is preserved verbatim
    as the transition reason (exact downward reason). Already-at-the-floor returns
    the current state unchanged.
    """
    from states import TRANSITIONS

    current = state.current_status(job_id)
    if current is None:
        raise JobBlockingError(f"cannot degrade nonexistent job {job_id}")
    if current not in _DEGRADE_RANK:
        raise JobBlockingError(f"cannot degrade unranked status {current}")
    rank = _DEGRADE_RANK[current]
    if rank <= _DEGRADE_RANK["safe_stop"]:
        return current
    allowed = TRANSITIONS.get(current, frozenset())
    lower = [(t, _DEGRADE_RANK[t]) for t in allowed if t in _DEGRADE_RANK and _DEGRADE_RANK[t] < rank]
    if not lower:
        if "safe_stop" in allowed:
            target = "safe_stop"
        else:
            raise JobBlockingError(f"no lower step from {current}")
    else:
        target = max(lower, key=lambda item: item[1])[0]
    _transition_guarded(state, job_id, target, logger=logger,
                        reason=f"degraded: {reason}", phase=phase)
    return target


def _cached_pr_node_id(state: State, repo: str, number: int) -> str:
    """Read the PR node id cached by queue.py. Empty string when absent."""
    payload = _pr_payload(state, repo, number)
    node = payload.get("node_id")
    return str(node) if node else ""


def _recent_approval_count(state: State, hours: int = 24) -> int:
    """Verified approval mutations inside the trailing window."""
    since = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=hours)) \
        .isoformat().replace("+00:00", "Z")
    row = state.db.execute(
        "SELECT COUNT(*) AS c FROM mutations WHERE operation='approve_review' "
        "AND status='verified' AND updated_at>=?",
        (since,),
    ).fetchone()
    return int(row["c"]) if row else 0


def _rest_remaining(state: State) -> int | None:
    """Most recent recorded REST rate-limit remaining, or None if unknown."""
    row = state.db.execute(
        "SELECT remaining FROM api_calls WHERE remaining IS NOT NULL "
        "ORDER BY id DESC LIMIT 1"
    ).fetchone()
    return int(row["remaining"]) if row and row["remaining"] is not None else None


def _approval_evidence(
    local_cfg: dict[str, Any],
    state: State,
    job: dict[str, Any],
    head_sha: str,
    *,
    verdicts: list[dict[str, Any]],
    required_slots: int,
) -> Any:
    """Compute the external-evidence gates from ACTUAL state.

    `compute_gates` keeps a backward-compatible fallback in which these gates
    default to True when no evidence object is supplied. That fallback must never
    apply to the live path: the dispatcher therefore always supplies real values,
    and each one fails closed when it cannot be established.
    """
    from approval_evaluate import ApprovalEvidence

    approval = local_cfg.get("approval") or {}
    assurance_cfg = local_cfg.get("assurance") or {}

    # Achieved assurance, computed from the evidence and reviewer completion that
    # this job actually obtained.
    assurance = _job_assurance(
        local_cfg, state, job["job_id"],
        required_slots=required_slots,
        achieved_slots=len(verdicts),
        blockers=(),
    )

    # Bounded change: the diff must be inside the configured large-diff threshold.
    payload = _pr_payload(state, job["repo"], job["number"])
    try:
        additions = int(payload.get("additions", 0) or 0)
        deletions = int(payload.get("deletions", 0) or 0)
    except (TypeError, ValueError):
        additions = deletions = 0
    large = int(assurance_cfg.get("large_diff_lines", 700) or 700)
    bounded_change = bool(payload) and (additions + deletions) <= large

    # Audit writable: the job directory must accept the audit artefacts.
    try:
        probe = state.job_dir(job["job_id"]) / ".audit-probe"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink()
        audit_writable = True
    except OSError:
        audit_writable = False

    # Rate limits: the daily approval cap and the REST remaining floor. An unknown
    # REST remaining is not a pass.
    daily_limit = approval.get("daily_limit")
    within_daily = True
    if isinstance(daily_limit, int) and daily_limit >= 0:
        within_daily = _recent_approval_count(state) < daily_limit
    floor = int((local_cfg.get("poll") or {}).get("rest_remaining_floor", 0) or 0)
    remaining = _rest_remaining(state)
    within_rest = True if floor <= 0 else (remaining is not None and remaining >= floor)
    rate_limit_ok = within_daily and within_rest

    # A cheap pre-check only. The AUTHORITATIVE revalidation is the mandatory live
    # REST read inside `approval_action.execute_approval`, immediately before the
    # mutation; this gate exists so an already-known-stale head is rejected earlier.
    observed = (payload.get("head") or {}).get("sha", "") if isinstance(payload.get("head"), dict) else ""
    revalidation_ok = bool(observed) and observed == head_sha

    return ApprovalEvidence(
        required_reviewers=required_slots,
        completed_reviewers=len(verdicts),
        bounded_change=bounded_change,
        audit_writable=audit_writable,
        assurance_met=assurance.assurance_met,
        revalidation_ok=revalidation_ok,
        rate_limit_ok=rate_limit_ok,
    )


def _execute_live_approval(
    local_cfg: dict[str, Any],
    job: dict[str, Any],
    head_sha: str,
    logger: JobLogger | None,
    state: State,
    *,
    decision: Any,
    decision_steps: list[Any],
    final_profile: Any,
    verdicts: list[dict[str, Any]],
    panel_decision: str,
    snapshot_meta: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Run the guarded APPROVE mutation for an eligible live decision.

    The job stays in `approval_revalidation` for the duration of the call, because
    `approval_action.approve` performs the mandatory REST revalidation itself and
    `approval_action` is not a legal predecessor of the human queue. On success the
    job advances `approval_action -> completed_auto_approved`. Every failure mode
    lands on a distinct, legal state:

      denied / stale  -> durable human request + `human_approval_pending`
      uncertain       -> `safe_stop` (the mutation may have landed; never retry blind)
      no decision / transport failure / missing node id -> `safe_stop`

    The mutation is idempotency-keyed inside `execute_approval`, so a crash during
    the call is safe to re-enter: revalidation re-runs and the mutation is not
    duplicated.
    """
    from approval_action import (
        APPROVED,
        DENIED,
        STALE,
        UNCERTAIN,
        approve,
    )

    repo = job["repo"]
    number = job["number"]
    job_id = job["job_id"]

    def _result(status_note: str, extra: dict[str, Any] | None = None) -> dict[str, Any]:
        out = {
            "job": job_id, "repo": repo, "number": number,
            "decision": panel_decision,
            "status": state.current_status(job_id),
            "approval_disposition": decision.disposition,
            "approval_outcome": status_note,
            "final_profile": final_profile.as_dict(),
            "steps": [{"profile": s.profile.as_dict(), "decision": s.decision}
                      for s in decision_steps],
        }
        out.update(extra or {})
        return out

    pr_node_id = _cached_pr_node_id(state, repo, number)
    if not pr_node_id:
        reason = f"no cached PR node_id for {repo}#{number}; run queue.py before approval"
        _log(logger, "error", body=reason, phase="approval", outcome="safe_stop")
        _transition_guarded(state, job_id, "safe_stop", logger=logger,
                            phase="approval", reason=reason)
        return _result("missing_node_id", {"reason": reason})

    ok, outcome, message = approve(
        state,
        decision_id=decision.decision_id,
        repo=repo,
        number=number,
        head_sha=head_sha,
        policy_hash=decision.policy_hash,
        pr_node_id=pr_node_id,
        login=local_cfg.get("login", ""),
        config=local_cfg,
    )
    _log(logger, "info" if ok else "warning",
         body=f"approval mutation -> {outcome}", phase="approval", outcome=outcome,
         attributes={"approval.decision_id": decision.decision_id,
                     "approval.outcome": outcome})

    _ledger_record(state, job, head_sha, "action", {
        "operation": "approve_review",
        "outcome": outcome,
        "verified": bool(ok and outcome == APPROVED),
        "decision_id": decision.decision_id,
        "message": message,
    }, entry_key="approve", snapshot_meta=snapshot_meta)
    if ok and outcome == APPROVED:
        _transition_guarded(state, job_id, "approval_action", logger=logger,
                            phase="approval", reason="approve mutation verified")
        _transition_guarded(state, job_id, "completed_auto_approved", logger=logger,
                            phase="approval", reason="auto-approved on reviewed head")
        return _result(outcome, {"decision_id": decision.decision_id})

    if outcome in (DENIED, STALE):
        expiry = int((local_cfg.get("human_queue") or {}).get("expiry_minutes", 1440))
        request = enqueue_human(
            state, repo=repo, number=number, head_sha=head_sha,
            policy=local_cfg, job_id=job_id,
            summary=f"{repo}#{number} approval blocked at revalidation",
            assurance=final_profile.as_dict(),
            reviewers=[v.get("model", "") for v in verdicts],
            risk_score=decision.risk_score, risk_band=decision.risk_band_name,
            protected=decision.protected, failed_gates=decision.failed_gates,
            ci={}, findings=[],
            recommendation="require human approval",
            rationale=f"{outcome}: {message}"[:800],
            action="approve", expiry_minutes=expiry,
        )
        notification = _deliver_notification(local_cfg, request, logger)
        _transition_guarded(state, job_id, "human_approval_pending", logger=logger,
                            phase="approval", reason=f"{outcome}: {message}"[:200])
        return _result(outcome, {"reason": message,
                                 "request_id": request.get("request_id"),
                                 "notification": notification})

    # UNCERTAIN and every remaining failure: stop safely, never retry blind.
    reason = f"{outcome}: {message}"
    severity = "error" if outcome == UNCERTAIN else "warning"
    _log(logger, severity, body=f"approval halted ({outcome})", phase="approval",
         outcome="safe_stop")
    _transition_guarded(state, job_id, "safe_stop", logger=logger,
                        phase="approval", reason=reason[:200])
    return _result(outcome, {"reason": message})


def _rc_execute(state: State, variables: dict[str, Any], job: str, **kwargs) -> dict[str, Any]:
    """Seam over the CHANGES_REQUESTED mutation so tests can intercept it."""
    from github_mutate import execute_request_changes

    return execute_request_changes(state, variables, job, **kwargs)


def _rc_transport(local_cfg: dict[str, Any], state: State, repo: str, number: int):
    """Return (revalidate, rest_probe) bound to the REST allowlist.

    `execute_request_changes` only verifies when a probe, login and head are all
    supplied, so the caller must always provide them; otherwise the mutation would
    be posted unverified.
    """
    from github_rest import RestReader

    reader = RestReader(local_cfg or {}, state)

    def revalidate_factory(head_sha: str):
        def revalidate() -> bool:
            # Fail closed on ANY transport problem. A revalidation that cannot be
            # performed is not a pass, and it must not raise out of the gate: one
            # PR's REST hiccup may never abort the whole sweep.
            try:
                meta = reader.pr_meta(repo, number) or {}
            except Exception:
                return False
            if not meta:
                return False
            if (meta.get("head", {}) or {}).get("sha") != head_sha:
                return False
            return bool(meta.get("draft")) is False

        return revalidate

    return revalidate_factory, (lambda: reader.pr_reviews(repo, number))


def _job_assurance(
    local_cfg: dict[str, Any],
    state: State,
    job_id: str,
    *,
    required_slots: int,
    achieved_slots: int,
    blockers: tuple[str, ...],
    disagreement: bool = False,
):
    """Compute achieved assurance from facts actually gathered for this job."""
    from risk import compute_assurance

    evidence = _evidence_meta(state, job_id)
    present = [
        bool(evidence.get("checks") is not None),
        bool(evidence.get("context")),
        bool(evidence.get("pr") or evidence.get("files") is not None),
    ]
    completeness = sum(1 for p in present if p) / len(present)
    return compute_assurance(
        required_rpn=0,
        bands=(local_cfg.get("risk") or {}).get("bands"),
        evidence_completeness=completeness,
        achieved_slots=achieved_slots,
        required_slots=max(1, required_slots),
        fresh=_evidence_fresh(local_cfg, evidence.get("collected_at", "")),
        disagreement=disagreement,
        blockers=blockers,
    )


def _execute_request_changes(
    local_cfg: dict[str, Any],
    job: dict[str, Any],
    head_sha: str,
    logger: JobLogger | None,
    state: State,
    *,
    final_profile: Any,
    verdicts: list[dict[str, Any]],
    steps: list[Any],
    snapshot_meta: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Handle a panel that unanimously located defects.

    A model asserting a defect is never sufficient to block a PR. The finding must
    be corroborated (two distinct provider families, or one family citing a check
    that actually failed), the `request_changes` authority must be live, and the
    deterministic gate must pass with a fresh revalidation. Anything short of that
    escalates to a human with the findings attached.
    """
    from action_gate import request_changes_gate
    from findings import blocking_summary, corroborate

    repo = job["repo"]
    number = job["number"]
    job_id = job["job_id"]

    def _result(outcome: str, extra: dict[str, Any] | None = None) -> dict[str, Any]:
        out = {
            "job": job_id, "repo": repo, "number": number,
            "decision": "REQUEST_CHANGES",
            "status": state.current_status(job_id),
            "request_changes_outcome": outcome,
            "final_profile": final_profile.as_dict(),
            "steps": [{"profile": s.profile.as_dict(), "decision": s.decision} for s in steps],
        }
        out.update(extra or {})
        # Single exit point, so every terminal outcome of this path lands in the
        # ledger and the timeline is never missing its conclusion.
        _ledger_record(state, job, head_sha, "decision", {
            "disposition": outcome,
            "panel_decision": "REQUEST_CHANGES",
            "status": out["status"],
            "reason": out.get("reason", ""),
            "failed_gates": out.get("failed_gates", []),
            "profile": final_profile.as_dict(),
        }, entry_key="request_changes_outcome", snapshot_meta=snapshot_meta)
        return out

    _transition_guarded(state, job_id, "adjudication", logger=logger,
                        phase="adjudication", reason="panel located defects")

    evidence = _evidence_meta(state, job_id)
    blocking_severities = tuple(
        (local_cfg.get("findings") or {}).get("blocking_severities") or ("blocker",)
    )
    results = corroborate(verdicts, checks=evidence.get("checks") or [],
                          blocking_severities=blocking_severities)
    summary = blocking_summary(results)
    verified = [r for r in results if r.verified]

    _log(logger, "info", body="finding corroboration complete", phase="adjudication",
         outcome="corroborated" if verified else "uncorroborated",
         attributes={"findings.verified": summary["verified_count"],
                     "findings.unverified": summary["unverified_count"]})
    for item in results:
        entry = item.as_dict()
        _ledger_record(state, job, head_sha, "finding", entry,
                       entry_key=f"{entry.get('severity')}:{entry.get('location')}",
                       snapshot_meta=snapshot_meta)

    # Uncorroborated defects are a human question, never an authoritative action.
    if not verified:
        reason = (f"{summary['unverified_count']} uncorroborated finding(s); "
                  "no independent corroboration or reproducing check failure")
        _transition_guarded(state, job_id, "human_required", logger=logger,
                            phase="adjudication", reason=reason[:200])
        return _result("uncorroborated", {"reason": reason, "findings": summary})

    mode = mode_for(local_cfg, repo, "request_changes")
    if mode != "live":
        reason = f"request_changes authority is {mode}; verified defects need a human"
        _transition_guarded(state, job_id, "human_required", logger=logger,
                            phase="adjudication", reason=reason[:200])
        return _result("authority_not_live", {"reason": reason, "findings": summary})

    _transition_guarded(state, job_id, "approval_evaluation", logger=logger,
                        phase="decision", reason="evaluating request-changes gate")

    revalidate_factory, rest_probe = _rc_transport(local_cfg, state, repo, number)
    assurance = _job_assurance(
        local_cfg, state, job_id,
        required_slots=len(verdicts) or 1,
        achieved_slots=len(verdicts),
        blockers=tuple(f"blocker:{r.finding.location}" for r in verified),
    )
    _ledger_record(state, job, head_sha, "assurance", assurance.as_dict(),
                   entry_key="request_changes_assurance", snapshot_meta=snapshot_meta)
    payload = _pr_payload(state, repo, number)
    gate = request_changes_gate(
        cfg=local_cfg, repo=repo, head_sha=head_sha,
        pr={"draft": bool(payload.get("draft")),
            "head": (payload.get("head") or {}).get("sha", head_sha)},
        verified_blocker=True,
        blocker_evidence_sufficient=True,
        assurance=assurance,
        revalidate=revalidate_factory(head_sha),
    )
    if not gate.allowed:
        expiry = int((local_cfg.get("human_queue") or {}).get("expiry_minutes", 1440))
        request = enqueue_human(
            state, repo=repo, number=number, head_sha=head_sha,
            policy=local_cfg, job_id=job_id,
            summary=f"{repo}#{number} has verified defects but the gate denied action",
            assurance=final_profile.as_dict(),
            reviewers=[v.get("model", "") for v in verdicts],
            risk_score=0, risk_band=assurance.required_assurance,
            protected=[], failed_gates=gate.failed,
            ci={}, findings=[r.as_dict() for r in verified],
            recommendation="request changes",
            rationale=gate.reason[:800], action="request_changes",
            expiry_minutes=expiry,
        )
        notification = _deliver_notification(local_cfg, request, logger)
        _transition_guarded(state, job_id, "human_approval_pending", logger=logger,
                            phase="decision", reason=gate.reason[:200])
        return _result("gate_denied", {"reason": gate.reason, "failed_gates": gate.failed,
                                       "findings": summary,
                                       "request_id": request.get("request_id"),
                                       "notification": notification})

    pr_node_id = _cached_pr_node_id(state, repo, number)
    if not pr_node_id:
        reason = f"no cached PR node_id for {repo}#{number}; run queue.py first"
        _transition_guarded(state, job_id, "safe_stop", logger=logger,
                            phase="decision", reason=reason)
        return _result("missing_node_id", {"reason": reason, "findings": summary})

    body = _render_request_changes_body(repo, number, head_sha, verified)
    try:
        _rc_execute(
            state, {"pullRequestId": pr_node_id, "body": body}, job_id,
            rest_probe=rest_probe, login=local_cfg.get("login", ""), head_sha=head_sha,
        )
    except Exception as exc:
        reason = f"request-changes mutation failed: {exc}"
        _log(logger, "error", body="request-changes halted", phase="decision",
             outcome="safe_stop")
        _transition_guarded(state, job_id, "safe_stop", logger=logger,
                            phase="decision", reason=reason[:200])
        return _result("mutation_failed", {"reason": str(exc), "findings": summary})

    _ledger_record(state, job, head_sha, "action", {
        "operation": "request_changes_review",
        "outcome": "changes_requested",
        "verified": True,
        "verified_findings": summary["verified_count"],
    }, entry_key="request_changes", snapshot_meta=snapshot_meta)
    _transition_guarded(state, job_id, "changes_requested", logger=logger,
                        phase="decision", reason="verified defects; changes requested")
    return _result("changes_requested", {"findings": summary})


def _render_request_changes_body(
    repo: str, number: int, head_sha: str, verified: list[Any]
) -> str:
    """Body for the CHANGES_REQUESTED review: only corroborated findings."""
    lines = [
        f"Automated review of {repo}#{number} at `{head_sha}` found "
        f"{len(verified)} corroborated blocking finding(s).",
        "",
    ]
    for item in verified:
        finding = item.finding
        basis = ("independently reported by two provider families"
                 if item.basis == "two_provider_families"
                 else f"corroborated by failing check `{item.citation}`")
        lines.extend([
            f"- **{finding.severity}** `{finding.location}` — {finding.title}",
            f"  - evidence: {finding.evidence}",
            f"  - primary source: {finding.primary_source}",
            f"  - basis: {basis}",
        ])
    lines.extend([
        "",
        "Findings without independent corroboration are not listed here; they are "
        "escalated to a human reviewer instead.",
    ])
    return "\n".join(lines)


def _run_job_inner(
    local_cfg: dict[str, Any],
    job: dict[str, Any],
    head_sha: str,
    logger: JobLogger | None,
    state: State,
    snapshot_meta: dict[str, Any] | None = None,
) -> dict[str, Any]:
    repo = job["repo"]
    number = job["number"]
    lane = job["lane"]
    job_id = job["job_id"]
    _ensure_panel()

    def assess(profile: Profile) -> list[str]:
        result = run_panel(local_cfg, state, repo, number, lane, job_id, profile, logger=logger)
        if not result["complete"]:
            raise PartialPanel(result)
        # A complete panel that calls for more evidence must NOT re-run the identical
        # model loop; it escalates so the dispatcher can do one bounded re-gather.
        if any(sig == "MISSING_EVIDENCE" for sig in result["signals"]):
            raise EvidenceIncompleteError("panel verdict missing evidence; bounded gather, no re-run")
        return result["signals"]

    try:
        _transition_guarded(state, job_id, "assurance", logger=logger,
                            phase="dispatch", reason="panel start")
        minimum = decide_assurance(local_cfg, state, repo, number, lane)
        final_profile, decision, steps = drive(minimum, assess, max_steps=6)
    except PartialPanel as exc:
        reason = f"partial panel: {exc.result['completed_reviewers']}/{exc.result['required_reviewers']}; no mutation"
        _transition_guarded(state, job_id, "degraded_draft", logger=logger,
                            phase="assurance", reason=reason)
        return {
            "job": job_id, "repo": repo, "number": number,
            "decision": "PARTIAL_PANEL", "status": "degraded_draft", "reason": reason,
            "completed_reviewers": exc.result["completed_reviewers"],
            "required_reviewers": exc.result["required_reviewers"],
            "final_profile": exc.result["profile"], "steps": [],
        }
    except JobBlockingError as exc:
        _transition_guarded(state, job_id, "human_required", logger=logger,
                            phase="assurance", reason=str(exc))
        return {"job": job_id, "status": "human_required", "reason": str(exc),
                "decision": "JOB_BLOCKING"}
    except EvidenceIncompleteError as exc:
        return _evidence_missing(state, local_cfg, job, logger, message=str(exc))

    if decision == "REQUEST_CHANGES":
        return _execute_request_changes(
            local_cfg, job, head_sha, logger, state,
            final_profile=final_profile,
            verdicts=_collected_verdicts(state, job_id),
            steps=steps,
            snapshot_meta=snapshot_meta,
        )

    if decision != "SUCCESS":
        _transition_guarded(state, job_id, "human_required", logger=logger,
                            phase="assurance", reason=decision)
        return {"job": job_id, "repo": repo, "number": number,
                "decision": decision, "status": "human_required",
                "final_profile": final_profile.as_dict(),
                "steps": [{"profile": s.profile.as_dict(), "decision": s.decision} for s in steps]}
    _transition_guarded(state, job_id, "adjudication", logger=logger,
                        phase="assurance", reason="panel complete")
    _transition_guarded(state, job_id, "approval_evaluation", logger=logger,
                        phase="approval", reason="evaluating approval")
    verdicts = _collected_verdicts(state, job_id)
    pr_facts = _load_pr_facts(state, job, head_sha, local_cfg)
    required_slots = 1 if final_profile.independence == "single" else 2
    res = eval_approval(
        state, local_cfg, repo=repo, number=number, head_sha=head_sha,
        pr=pr_facts, verdicts=verdicts, profile=final_profile.as_dict(),
        reviewers=[v.get("model", "") for v in verdicts],
        assessments={}, login=local_cfg.get("login", ""),
        evidence=_approval_evidence(
            local_cfg, state, job, head_sha,
            verdicts=verdicts, required_slots=required_slots,
        ),
    )
    _log(logger, "info", body=f"approval evaluation -> {res.disposition}", phase="approval",
         outcome=res.disposition,
         attributes={"risk.score": res.risk_score, "risk.band": res.risk_band_name,
                     "approval.failed_gates": res.failed_gates})
    _ledger_record(state, job, head_sha, "decision", {
        "disposition": res.disposition,
        "failed_gates": res.failed_gates,
        "risk_score": res.risk_score,
        "risk_band": res.risk_band_name,
        "protected": res.protected,
        "reason": res.reason,
        "panel_decision": decision,
        "profile": final_profile.as_dict(),
    }, entry_key="approval_evaluation", snapshot_meta=snapshot_meta)

    if res.disposition == "live":
        _transition_guarded(state, job_id, "approval_revalidation", logger=logger,
                            phase="approval", reason=res.reason or res.disposition)
        return _execute_live_approval(
            local_cfg, job, head_sha, logger, state,
            decision=res, decision_steps=steps, final_profile=final_profile,
            verdicts=verdicts, panel_decision=decision,
            snapshot_meta=snapshot_meta,
        )
    elif res.disposition == "shadow":
        _transition_guarded(state, job_id, "advisory_action", logger=logger,
                            phase="approval",
                            reason="shadow mode: would-approve recorded, no mutation")
    elif res.disposition == "human_escalation":
        expiry = int((local_cfg.get("human_queue") or {}).get("expiry_minutes", 1440))
        request = enqueue_human(
            state, repo=repo, number=number, head_sha=head_sha,
            policy=local_cfg,  # full config => full policy hash bound to the request
            job_id=job_id,
            summary=f"{repo}#{number} needs human approval",
            assurance=final_profile.as_dict(),
            reviewers=[v.get("model", "") for v in verdicts],
            risk_score=res.risk_score, risk_band=res.risk_band_name,
            protected=res.protected, failed_gates=res.failed_gates,
            ci={}, findings=[], recommendation="require human approval",
            rationale=res.reason or "human escalation", action="approve",
            expiry_minutes=expiry,
        )
        # Notification failure must NOT drop the request from the pending queue.
        notification = _deliver_notification(local_cfg, request, logger)
        _transition_guarded(state, job_id, "human_approval_pending", logger=logger,
                            phase="approval", reason="queued for human approval")
        return {
            "job": job_id, "repo": repo, "number": number,
            "decision": decision, "status": state.current_status(job_id),
            "approval_disposition": res.disposition,
            "request_id": request.get("request_id"),
            "policy_hash": request.get("policy_hash"),
            "notification": notification,
            "final_profile": final_profile.as_dict(),
            "steps": [{"profile": s.profile.as_dict(), "decision": s.decision} for s in steps],
        }
    else:  # disabled -> advisory only
        _transition_guarded(state, job_id, "advisory_action", logger=logger,
                            phase="approval",
                            reason="approval mode disabled; advisory only")

    return {
        "job": job_id, "repo": repo, "number": number,
        "decision": decision, "status": state.current_status(job_id),
        "approval_disposition": res.disposition,
        "final_profile": final_profile.as_dict(),
        "steps": [{"profile": s.profile.as_dict(), "decision": s.decision} for s in steps],
    }


def resolve_snapshot(
    local_cfg: dict[str, Any], state: State, job_id: str
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Return (effective_config, snapshot_meta) for this job.

    A job runs under the snapshot it STARTED with. On first dispatch the active
    snapshot is recorded against the job; on resume the pinned snapshot is
    reloaded and used, so editing the config mid-flight cannot retroactively
    change an in-flight job's authority, thresholds, or model routes.

    When no policy is configured the snapshot cannot be built; the caller's config
    is used unchanged and the reason is reported rather than failing the job, so
    snapshotting is additive for repos that have not adopted policy-as-data.
    """
    from snapshot import SnapshotError, SnapshotStore, build_snapshot

    try:
        store = SnapshotStore(expand_path(local_cfg.get("state_dir") or "."))
    except OSError as exc:
        return local_cfg, {"pinned": False, "reason": f"snapshot store unavailable: {exc}"}

    row = state.db.execute(
        "SELECT snapshot_hash FROM jobs WHERE id=?", (job_id,)
    ).fetchone()
    pinned_hash = (row["snapshot_hash"] if row else None) or ""

    if pinned_hash:
        pinned = store.get(pinned_hash)
        if pinned is not None:
            return pinned.config, {
                "pinned": True, "resumed": True, **pinned.as_meta(),
            }
        # The archive is gone; refuse to silently upgrade the job to a newer
        # snapshot and say so instead.
        return local_cfg, {
            "pinned": False,
            "reason": f"pinned snapshot {pinned_hash[:12]} is no longer archived",
        }

    from policy import validate_policy

    try:
        snap = build_snapshot(local_cfg, validate_policy=validate_policy)
    except SnapshotError as exc:
        return local_cfg, {"pinned": False, "reason": str(exc)}

    active = store.active()
    if active is None or active.hash != snap.hash:
        store.activate(snap)
    state.execute("UPDATE jobs SET snapshot_hash=? WHERE id=?", (snap.hash, job_id))
    state.db.commit()
    return snap.config, {"pinned": True, "resumed": False, **snap.as_meta()}


def run_job(
    local_cfg: dict[str, Any],
    job: dict[str, Any],
    *,
    state: State,
    capability_mode: str | None = None,
) -> dict[str, Any]:
    """Drive one job to a terminal state.

    `capability_mode` is the proven GitHub capability for this repo (see
    `github_auth.probe`). It can only ever REDUCE the authority the snapshot
    authorises, never grant it, and is re-applied on every run because capability
    is current state rather than something the snapshot pins.
    """
    repo = job["repo"]
    number = job["number"]
    lane = job["lane"]
    job_id = job["job_id"]

    row = state.db.execute("SELECT head_sha FROM jobs WHERE id=?", (job_id,)).fetchone()
    if not row:
        return {"job": job_id, "status": "error", "reason": f"job not found: {job_id}"}
    head_sha = row["head_sha"]

    # Everything below runs under the job's pinned snapshot, not the caller's
    # possibly-newer config.
    local_cfg, snapshot_meta = resolve_snapshot(local_cfg, state, job_id)

    capability_note = ""
    if capability_mode:
        from github_auth import FULL, downgrade_config_for_mode

        if capability_mode != FULL:
            local_cfg = downgrade_config_for_mode(local_cfg, capability_mode)
            capability_note = f"authority clamped to proven capability: {capability_mode}"

    logger = _make_logger(local_cfg, job_id, repo, number, lane)
    if snapshot_meta.get("pinned"):
        _log(logger, "info", body="running under pinned runtime snapshot",
             phase="dispatch", outcome="pinned",
             attributes={"snapshot.hash": snapshot_meta.get("snapshot_hash"),
                         "config.version": snapshot_meta.get("config_version"),
                         "policy.version": snapshot_meta.get("policy_version"),
                         "snapshot.resumed": snapshot_meta.get("resumed")})
    if capability_note:
        _log(logger, "warning", body=capability_note, phase="dispatch",
             outcome="capability_clamped",
             attributes={"github.capability_mode": capability_mode})

    if not canary_allowed(local_cfg, state, lane):
        return {"job": job_id, "status": "gated", "reason": f"{lane} canary not approved",
                "snapshot": snapshot_meta}

    # Supersede stale human requests for this PR whose head or policy no longer match.
    supersede_for_head(state, repo, number, head_sha)
    supersede_for_policy(state, repo, number, local_cfg)

    try:
        result = _run_job_inner(local_cfg, job, head_sha, logger, state, snapshot_meta)
    except SafeStopSignal as exc:
        result = _arrive_safe_stop(state, job, logger, reason=str(exc))
    except JobBlockingError as exc:
        result = {"job": job_id, "repo": repo, "number": number,
                  "status": "error", "decision": "JOB_BLOCKING", "reason": str(exc)}
    result["snapshot"] = snapshot_meta
    return result


def canary_allowed(local_cfg: dict[str, Any], state: State, lane: str) -> bool:
    """Canary approval is authoritative in the SQLite `canaries` table; when no
    row exists it falls back to the repo-local config key, which is
    `incoming_canary_approved` / `author_canary_approved` (not `{lane}_...`)."""
    row = state.db.execute("SELECT status FROM canaries WHERE lane=?", (lane,)).fetchone()
    if row is not None:
        return row["status"] == "approved"
    key = "incoming_canary_approved" if lane == "incoming_review" else "author_canary_approved"
    return bool((local_cfg.get("dispatch") or {}).get(key, False))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Review-queue dispatch / onboarding gate")
    parser.add_argument("--config", default=None)
    parser.add_argument("--repo-root", required=True)
    parser.add_argument("--no-capability-probe", action="store_true",
                        help="skip the GitHub capability probe (offline/testing)")
    sub = parser.add_subparsers(dest="command", required=True)

    sw = sub.add_parser("sweep")
    sw.add_argument("--lane", default="incoming_review")
    sw.add_argument("--limit", type=int, default=2)

    one = sub.add_parser("dispatch-one")
    one.add_argument("--number", required=True, type=int)
    one.add_argument("--job", required=True)
    one.add_argument("--lane", required=True)
    args = parser.parse_args(argv)

    cfg, cfg_path, issues = load_repo_config(args.repo_root)
    if cfg is None:
        print(
            json.dumps(
                {
                    "status": "onboarding_required",
                    "reason": "; ".join(issues),
                    "config": str(cfg_path),
                    "onboarding": f"python3 scripts/onboarding.py init {args.repo_root}",
                },
                indent=2,
            )
        )
        return 1

    state_dir = cfg.get("state_dir")
    state = State({"state_dir": state_dir or "~/.config/review-queue-automation"})

    # Probe capability ONCE per invocation, not per job: it costs two reads and
    # applies to the whole repository. A repo we cannot write to still produces
    # drafts and human requests rather than failing.
    capability_mode = None
    slug = (cfg.get("repository") or {}).get("slug", "")
    if slug and not args.no_capability_probe:
        from github_auth import UNUSABLE, probe as probe_capability

        try:
            capability = probe_capability(cfg, state, slug)
            capability_mode = capability.get("mode")
        except Exception as exc:  # probing must never abort a sweep
            capability_mode = None
            capability = {"error": str(exc)[:200]}
        if capability_mode == UNUSABLE:
            print(json.dumps({
                "status": "capability_unusable",
                "reason": "the authenticated identity cannot read this repository",
                "capability": capability,
            }, indent=2, sort_keys=True))
            state.close()
            return 1

    try:
        if args.command == "sweep":
            rows = state.db.execute(
                "SELECT id AS job_id, repo, number, lane FROM jobs "
                "WHERE lane=? AND status='detected' ORDER BY created_at LIMIT ?",
                (args.lane, args.limit),
            ).fetchall()
            results = []
            for row in rows:
                try:
                    result = run_job(
                        cfg,
                        {"job_id": row["job_id"], "repo": row["repo"], "number": row["number"], "lane": row["lane"]},
                        state=state,
                        capability_mode=capability_mode,
                    )
                except Exception as exc:
                    result = {"job": row["job_id"], "status": "error", "reason": str(exc)[:500]}
                results.append(result)
            json.dump(results, sys.stdout, indent=2, sort_keys=True)
        else:
            row = state.db.execute(
                "SELECT repo, number, lane FROM jobs WHERE id=?", (args.job,)
            ).fetchone()
            if row is None:
                raise SystemExit(f"job not found: {args.job}")
            result = run_job(
                cfg,
                {"job_id": args.job, "repo": row["repo"], "number": row["number"], "lane": row["lane"]},
                state=state,
                capability_mode=capability_mode,
            )
            json.dump(result, sys.stdout, indent=2, sort_keys=True)
        sys.stdout.write("\n")
    finally:
        state.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())