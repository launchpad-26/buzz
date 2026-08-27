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
from common import State
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

    ph = payload.get("head")
    payload_head = ph.get("sha", "") if isinstance(ph, dict) else ""
    resolved_head = head_sha or payload_head or context.get("head", "")

    try:
        complexity = int(payload.get("complexity", 0) or 0)
    except (TypeError, ValueError):
        complexity = 0

    return PRFacts(
        draft=draft,
        author_login=author,
        head_sha=resolved_head,
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


def _run_job_inner(
    local_cfg: dict[str, Any],
    job: dict[str, Any],
    head_sha: str,
    logger: JobLogger | None,
    state: State,
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
    res = eval_approval(
        state, local_cfg, repo=repo, number=number, head_sha=head_sha,
        pr=pr_facts, verdicts=verdicts, profile=final_profile.as_dict(),
        reviewers=[v.get("model", "") for v in verdicts],
        assessments={}, login=local_cfg.get("login", ""),
    )
    _log(logger, "info", body=f"approval evaluation -> {res.disposition}", phase="approval",
         outcome=res.disposition,
         attributes={"risk.score": res.risk_score, "risk.band": res.risk_band_name,
                     "approval.failed_gates": res.failed_gates})

    if res.disposition == "live":
        _transition_guarded(state, job_id, "approval_revalidation", logger=logger,
                            phase="approval", reason=res.reason or res.disposition)
        return _execute_live_approval(
            local_cfg, job, head_sha, logger, state,
            decision=res, decision_steps=steps, final_profile=final_profile,
            verdicts=verdicts, panel_decision=decision,
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


def run_job(local_cfg: dict[str, Any], job: dict[str, Any], *, state: State) -> dict[str, Any]:
    repo = job["repo"]
    number = job["number"]
    lane = job["lane"]
    job_id = job["job_id"]

    row = state.db.execute("SELECT head_sha FROM jobs WHERE id=?", (job_id,)).fetchone()
    if not row:
        return {"job": job_id, "status": "error", "reason": f"job not found: {job_id}"}
    head_sha = row["head_sha"]

    logger = _make_logger(local_cfg, job_id, repo, number, lane)

    if not canary_allowed(local_cfg, state, lane):
        return {"job": job_id, "status": "gated", "reason": f"{lane} canary not approved"}

    # Supersede stale human requests for this PR whose head or policy no longer match.
    supersede_for_head(state, repo, number, head_sha)
    supersede_for_policy(state, repo, number, local_cfg)

    try:
        return _run_job_inner(local_cfg, job, head_sha, logger, state)
    except SafeStopSignal as exc:
        return _arrive_safe_stop(state, job, logger, reason=str(exc))
    except JobBlockingError as exc:
        return {"job": job_id, "repo": repo, "number": number,
                "status": "error", "decision": "JOB_BLOCKING", "reason": str(exc)}


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
            )
            json.dump(result, sys.stdout, indent=2, sort_keys=True)
        sys.stdout.write("\n")
    finally:
        state.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())