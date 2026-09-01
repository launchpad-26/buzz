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
import time
from typing import Any

from assurance import Profile, drive
from authority import mode_for
from cadence import decide as cadence_decide, due as cadence_due, read as cadence_read, schedule_after, write as cadence_write
from checks import all_passing as all_checks_passing
from common import State, expand_path, utcnow
from config import load_repo_config
from errors import EvidenceIncompleteError, JobBlockingError
from evidence import collect as collect_evidence
from logging_otel import JOB_EVENTS, JobLogger, metric_attributes
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


def _reconcile_queue(local_cfg: dict[str, Any], state: State, repo: str) -> dict[str, Any]:
    """Refresh queue facts immediately before selecting a scheduled sweep's jobs."""
    from queue import reconcile

    return reconcile(local_cfg, state, repo)


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


def _log(
    logger,
    level: str,
    *,
    body: str,
    phase: str,
    outcome: str = "",
    attributes: dict[str, Any] | None = None,
    event: str = "",
) -> None:
    """Emit one orchestrator event. A logging failure safe-stops the job.

    `event` is one of `logging_otel.JOB_EVENTS`; it is what a trace consumer keys
    off, so it is validated here rather than being a free-form string that can
    silently drift out of the registry.
    """
    if logger is None:
        return
    if event and event not in JOB_EVENTS:
        raise SafeStopSignal(f"unknown job event name: {event!r}")
    try:
        kwargs: dict[str, Any] = {
            "body": body, "phase": phase, "outcome": outcome, "attributes": attributes
        }
        if event:
            kwargs["event_name"] = event
        getattr(logger, level)(**kwargs)
    except SafeStopSignal:
        raise
    except Exception as exc:
        raise SafeStopSignal(f"audit logging failure: {exc}") from exc


def _now_ms() -> int:
    return int(time.monotonic() * 1000)


def _elapsed_ms(started_ms: int) -> int:
    return max(0, _now_ms() - started_ms)


def _arrive_safe_stop(state: State, job: dict[str, Any], logger, reason: str) -> dict[str, Any]:
    """Best-effort transition to safe_stop; swallow failures so the caller still results."""
    job_id = job["job_id"]
    try:
        state.transition(job_id, "safe_stop", logger=logger, phase="dispatch", reason=reason)
    except Exception:
        pass
    # The safe-stop event is best-effort by construction: the job is already
    # stopping because something failed, so a second failure here must not
    # replace the outcome with an exception.
    try:
        _log(logger, "error", body="job stopped safely", phase="dispatch",
             outcome="safe_stop", event="safe_stop",
             attributes={"job.reason": reason[:200]})
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

    # One shared vocabulary, in `checks.py`. This line previously compared
    # `conclusion` to the literal `"SUCCESS"`, which is the GraphQL enum spelling,
    # against evidence gathered over REST, which is lower-case — so `checks_ok`
    # was never true and the `checks_complete_ok` gate could never pass. It also
    # required `SUCCESS` from every check, which no pull request in this
    # repository satisfies: the changed-paths fan-out skips whole job families,
    # and `SKIPPED` is a green outcome. Still fails closed on an empty list and
    # on any pending check.
    checks = evidence.get("checks") or []
    checks_ok = all_checks_passing(checks)

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
        _log(logger, "warning", body="evidence gather unavailable", phase="evidence",
             outcome="human_required", event="evidence",
             attributes={"evidence.gathered": False, "evidence.reason": reason[:200]})
        _log(logger, "warning", body="escalated for missing evidence", phase="evidence",
             outcome="human_required", event="decision",
             attributes={"decision.disposition": "EVIDENCE_INCOMPLETE"})
        return {"job": job_id, "repo": job.get("repo"), "number": job.get("number"),
                "status": "human_required", "decision": "EVIDENCE_INCOMPLETE", "reason": reason}
    reason = (
        "evidence missing; one bounded deterministic gather completed; "
        "no identical panel re-run"
    )
    _transition_guarded(state, job_id, "degraded_draft", logger=logger,
                        phase="assurance", reason=reason)
    _log(logger, "info", body="one bounded evidence gather completed", phase="evidence",
         outcome="gathered", event="evidence", attributes={"evidence.gathered": True})
    _log(logger, "warning", body="degraded draft after evidence gather", phase="evidence",
         outcome="degraded_draft", event="decision",
         attributes={"decision.disposition": "EVIDENCE_INCOMPLETE"})
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
    # `approve` performs the mandatory live REST revalidation itself, so its
    # outcome IS the verification result for the reviewed head.
    _emit_verify_event(logger, subject=f"{repo}#{number} head before approve",
                       ok=bool(ok and outcome == APPROVED), detail=f"{outcome}: {message}")
    _emit_mutation_event(logger, operation="approve_review", outcome=outcome,
                         verified=bool(ok and outcome == APPROVED), detail=message)
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
        _emit_human_queue_event(logger, request, action="approve",
                                reason=f"{outcome}: {message}")
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



def _post_advisory_review(
    local_cfg: dict[str, Any],
    state: State,
    job: dict[str, Any],
    head_sha: str,
    logger,
    *,
    disposition: str,
    failed_gates: list[str] | None = None,
    verdicts: list[dict[str, Any]] | None = None,
    snapshot_meta: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Publish the advisory review for this job. Never raises.

    Advisory output is the default product of the pipeline, so the corroboration
    split, achieved assurance and executed routes are all reported. Posting is
    idempotent per job, so a re-dispatch of the same revision does not duplicate.
    """
    from advisory import build_body, post_advisory
    from findings import blocking_summary, corroborate
    from ledger import entries

    repo, number, job_id = job["repo"], job["number"], job["job_id"]
    verdicts = verdicts if verdicts is not None else _collected_verdicts(state, job_id)
    evidence = _evidence_meta(state, job_id)

    blocking_severities = tuple(
        (local_cfg.get("findings") or {}).get("blocking_severities") or ("blocker",)
    )
    results = corroborate(verdicts, checks=evidence.get("checks") or [],
                          blocking_severities=blocking_severities)
    summary = blocking_summary(results)

    # Routes and activities come from the ledger, so the comment describes what
    # actually ran rather than what was configured.
    routes: list[dict[str, Any]] = []
    activities: list[str] = []
    try:
        for item in entries(state, job_id):
            if item["kind"] == "route":
                routes.append(item["payload"])
            elif item["kind"] == "strategy":
                activities = list(item["payload"].get("activities") or []) or activities
    except Exception:
        pass

    assurance = _job_assurance(
        local_cfg, state, job_id,
        required_slots=max(1, len(verdicts)),
        achieved_slots=len(verdicts),
        blockers=tuple(f"blocker:{r.finding.location}" for r in results if r.verified),
    ).as_dict()

    body = build_body(
        repo=repo, number=number, head_sha=head_sha, disposition=disposition,
        verified=summary["verified"], unverified=summary["unverified"],
        routes=routes, assurance=assurance, activities=activities,
        failed_gates=failed_gates or [],
        snapshot_hash=(snapshot_meta or {}).get("snapshot_hash", "") or "",
    )
    record = post_advisory(
        state, local_cfg=local_cfg, repo=repo, number=number, job_id=job_id,
        pr_node_id=_cached_pr_node_id(state, repo, number), body=body,
        login=local_cfg.get("login", ""), head_sha=head_sha,
    )
    _emit_mutation_event(logger, operation="add_comment_review",
                         outcome="posted" if record.get("posted") else "withheld",
                         verified=bool(record.get("posted")),
                         detail=str(record.get("reason", "")))
    _log(logger, "info" if record.get("posted") else "warning",
         body=("advisory review posted" if record.get("posted")
               else f"advisory review not posted: {record.get('reason', '')}"),
         phase="advisory",
         outcome="posted" if record.get("posted") else "withheld")
    _ledger_record(state, job, head_sha, "action", {
        "operation": "add_comment_review",
        "outcome": "posted" if record.get("posted") else "withheld",
        "verified": bool(record.get("posted")),
        "reason": record.get("reason", ""),
        "verified_findings": summary["verified_count"],
        "unverified_findings": summary["unverified_count"],
    }, entry_key="advisory", snapshot_meta=snapshot_meta)
    record["findings"] = summary
    return record


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
        _log(logger, "warning", body="uncorroborated findings escalated",
             phase="adjudication", outcome="human_required", event="decision",
             attributes={"decision.disposition": "uncorroborated",
                         "decision.reason": reason[:200]})
        return _result("uncorroborated", {"reason": reason, "findings": summary})

    mode = mode_for(local_cfg, repo, "request_changes")
    if mode != "live":
        reason = f"request_changes authority is {mode}; verified defects need a human"
        _transition_guarded(state, job_id, "human_required", logger=logger,
                            phase="adjudication", reason=reason[:200])
        _log(logger, "warning", body=reason, phase="adjudication",
             outcome="human_required", event="decision",
             attributes={"decision.disposition": "authority_not_live",
                         "authority.request_changes": mode})
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
    _emit_verify_event(logger, subject=f"{repo}#{number} head before request-changes",
                       ok=bool(gate.allowed), detail=gate.reason)
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
        _emit_human_queue_event(logger, request, action="request_changes",
                                reason=gate.reason)
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
        _emit_mutation_event(logger, operation="request_changes_review",
                             outcome="failed", verified=False, detail=str(exc))
        _log(logger, "error", body="request-changes halted", phase="decision",
             outcome="safe_stop")
        _transition_guarded(state, job_id, "safe_stop", logger=logger,
                            phase="decision", reason=reason[:200])
        return _result("mutation_failed", {"reason": str(exc), "findings": summary})

    _emit_mutation_event(logger, operation="request_changes_review",
                         outcome="changes_requested", verified=True,
                         detail=f"{summary['verified_count']} corroborated finding(s)")
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


def _emit_evidence_event(state: State, job: dict[str, Any], local_cfg, logger) -> dict[str, Any]:
    """Report the evidence bundle this job will actually reason over.

    Only bounded facts are logged — counts, freshness and the collection
    timestamp — never the evidence content itself, which is nonce-enveloped PR
    material and must not reach the log.
    """
    evidence = _evidence_meta(state, job["job_id"])
    checks = evidence.get("checks") or []
    fresh = _evidence_fresh(local_cfg, evidence.get("collected_at", ""))
    _log(logger, "info" if evidence else "warning",
         body="evidence bundle loaded" if evidence else "no evidence bundle on disk",
         phase="evidence", outcome="fresh" if fresh else "stale", event="evidence",
         attributes={
             "evidence.present": bool(evidence),
             "evidence.fresh": fresh,
             "evidence.collected_at": evidence.get("collected_at", ""),
             "evidence.checks": len(checks) if isinstance(checks, list) else 0,
             "evidence.has_context": bool(evidence.get("context")),
         })
    return evidence


def _emit_rereview_event(state: State, job: dict[str, Any], head_sha: str, logger) -> bool:
    """Emit `rereview` when this head supersedes a previously reviewed revision."""
    row = state.db.execute(
        "SELECT COUNT(*) AS c FROM jobs WHERE repo=? AND number=? AND head_sha<>?",
        (job["repo"], job["number"], head_sha),
    ).fetchone()
    prior = int(row["c"]) if row else 0
    if not prior:
        return False
    _log(logger, "info", body=f"re-review: {prior} prior revision(s) of this PR",
         phase="evidence", outcome="rereview", event="rereview",
         attributes={"review.prior_revisions": prior, "github.head.sha": head_sha})
    return True


def _budget_scope(job: dict[str, Any]) -> str:
    return str(job.get("repo") or "default")


def _reserve_budget(
    local_cfg: dict[str, Any], state: State, job: dict[str, Any], logger, profile
) -> Any:
    """Reserve this job's model spend BEFORE the panel runs.

    The reservation is the strategy's declared `budget_tokens`, so the cost of the
    work is bounded by a number the strategy itself publishes rather than
    discovered after the fact. A refusal is returned, never raised: the caller
    downgrades to a draft or a human, which is the whole point of checking here.
    """
    import budget
    from strategies import strategy_for_profile

    strategy, reason = strategy_for_profile(profile)
    decision = budget.reserve(
        state, local_cfg,
        job_id=job["job_id"], repo=job["repo"], number=job["number"],
        tokens=int(strategy.budget_tokens), scope=_budget_scope(job),
        rest_remaining=_rest_remaining(state),
    )
    _log(logger, "info" if decision.allowed else "warning",
         body=("budget reserved before spend" if decision.allowed
               else f"budget refused before spend: {decision.reason}"),
         phase="assurance", outcome="reserved" if decision.allowed else "refused",
         event="budget",
         attributes={
             "budget.limit": decision.limit,
             "budget.downgrade": decision.downgrade,
             "budget.breaker": decision.breaker,
             "budget.reason": decision.reason,
             "reasoning.strategy": strategy.name,
             "reasoning.strategy_reason": reason,
             # `_is_sensitive_key` matches "token" anywhere in a key, so the
             # `_tokens` suffix is dropped: these are headroom COUNTS and must
             # not be redacted out of the trace.
             **{f"budget.headroom.{k.removesuffix('_tokens')}": v
                for k, v in decision.headroom.items()},
             **metric_attributes(
                 tokens_reserved=decision.reserved_tokens,
                 attempts=budget.attempts_for_job(state, job["job_id"]),
             ),
         })
    return strategy, decision


def _emit_panel_trace(
    state: State, job: dict[str, Any], logger, panel_result: dict[str, Any],
    *, latency_ms: int, tokens: int
) -> None:
    """Emit `strategy`, `planner` and `route_selection` for the panel that ran.

    Planner and route facts are read back from the LEDGER rather than re-derived,
    so the trace describes what was actually recorded for this job instead of what
    the orchestrator would have expected.
    """
    from ledger import entries

    _log(logger, "info",
         body=f"strategy {panel_result.get('strategy', '')} -> {panel_result.get('outcome', '')}",
         phase="assurance", outcome=str(panel_result.get("outcome", "")),
         event="strategy",
         attributes={
             "reasoning.strategy": panel_result.get("strategy", ""),
             "reasoning.recipe": panel_result.get("recipe", ""),
             "reasoning.roles": panel_result.get("roles", []),
             "reasoning.disagreement": bool(panel_result.get("disagreement", False)),
             "reasoning.disagreement_handling": panel_result.get("disagreement_handling", ""),
             "review.required": panel_result.get("required_reviewers", 0),
             "review.completed": len(panel_result.get("completed_reviewers", []) or []),
             **metric_attributes(latency_ms=latency_ms, tokens=tokens),
         })

    try:
        recorded = entries(state, job["job_id"])
    except Exception:
        recorded = []

    for item in recorded:
        if item["kind"] == "strategy" and item.get("entry_key") == "review_plan":
            payload = item["payload"] or {}
            _log(logger, "info", body="deterministic review plan resolved",
                 phase="assurance", outcome="planned", event="planner",
                 attributes={
                     "planner.activities": payload.get("activities", []),
                     "planner.focus": payload.get("focus", []),
                     "planner.rereview": payload.get("is_rereview", False),
                 })
            break
    else:
        _log(logger, "warning", body="no review plan was recorded for this job",
             phase="assurance", outcome="unplanned", event="planner")

    routes = [item for item in recorded if item["kind"] == "route"]
    for item in routes[:_MAX_LOGGED_ROUTES]:
        payload = item["payload"] or {}
        qualified = payload.get("qualified_route") or {}
        _log(logger, "info", body=f"route executed: {item.get('entry_key', '')}",
             phase="assurance", outcome="executed", event="route_selection",
             attributes={
                 "route.key": item.get("entry_key", ""),
                 "route.slot": payload.get("slot", ""),
                 "route.provider_family": payload.get("provider_family", ""),
                 "route.capability": payload.get("capability", ""),
                 "route.effort_enforced": payload.get("effort_enforced",
                                                      qualified.get("effort_enforced")),
                 "route.qualified": bool(qualified),
             })
    if not routes:
        _log(logger, "warning", body="no model route was recorded for this job",
             phase="assurance", outcome="unrouted", event="route_selection")


def _emit_human_queue_event(logger, request: dict[str, Any], *, action: str, reason: str) -> None:
    _log(logger, "info", body=f"human request enqueued for {action}",
         phase="approval", outcome="queued", event="human_queue",
         attributes={"human.request_id": request.get("request_id", ""),
                     "human.action": action,
                     "human.policy_hash": request.get("policy_hash", ""),
                     "human.reason": reason[:200]})


def _emit_verify_event(logger, *, subject: str, ok: bool, detail: str = "") -> None:
    _log(logger, "info" if ok else "warning",
         body=f"revalidation of {subject}: {'ok' if ok else 'failed'}",
         phase="approval", outcome="verified" if ok else "unverified", event="verify",
         attributes={"verify.subject": subject, "verify.ok": bool(ok),
                     "verify.detail": detail[:200]})


def _emit_mutation_event(logger, *, operation: str, outcome: str, verified: bool,
                         detail: str = "") -> None:
    _log(logger, "info" if verified else "warning",
         body=f"external action {operation} -> {outcome}",
         phase="mutation", outcome=outcome, event="mutation",
         attributes={"mutation.operation": operation, "mutation.outcome": outcome,
                     "mutation.verified": bool(verified),
                     "mutation.detail": detail[:200]})


#: Route events are one per executed slot; the cap keeps a pathological fallback
#: chain from flooding the trace.
_MAX_LOGGED_ROUTES = 4


def _budget_refused(
    state: State, job: dict[str, Any], head_sha: str, logger, reservation,
    *, snapshot_meta: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Apply the downgrade a refused reservation demands, BEFORE any spend.

    `draft` keeps the job producing a non-authoritative artefact; `human` hands it
    to a person. Neither can spend a model call, which is the guarantee: a budget
    is reached and then respected, never exceeded and then noticed.
    """
    from budget import HUMAN

    job_id = job["job_id"]
    target = "human_required" if reservation.downgrade == HUMAN else "degraded_draft"
    reason = f"budget refused ({reservation.limit}): {reservation.reason}"
    _transition_guarded(state, job_id, target, logger=logger,
                        phase="assurance", reason=reason[:200])
    _log(logger, "warning", body="downgraded before spend", phase="assurance",
         outcome=target, event="decision",
         attributes={"decision.disposition": "BUDGET_REFUSED",
                     "decision.downgrade": reservation.downgrade,
                     "budget.limit": reservation.limit,
                     "decision.reason": reservation.reason[:200]})
    _ledger_record(state, job, head_sha, "decision", {
        "disposition": "budget_refused",
        "downgrade": reservation.downgrade,
        "limit": reservation.limit,
        "reason": reservation.reason,
        "status": target,
    }, entry_key="budget_refused", snapshot_meta=snapshot_meta)
    return {
        "job": job_id, "repo": job["repo"], "number": job["number"],
        "status": target, "decision": "BUDGET_REFUSED",
        "reason": reason, "budget": reservation.as_dict(),
    }


def _run_job_inner(
    local_cfg: dict[str, Any],
    job: dict[str, Any],
    head_sha: str,
    logger: JobLogger | None,
    state: State,
    snapshot_meta: dict[str, Any] | None = None,
) -> dict[str, Any]:
    import budget

    repo = job["repo"]
    number = job["number"]
    lane = job["lane"]
    job_id = job["job_id"]
    _ensure_panel()

    _emit_evidence_event(state, job, local_cfg, logger)
    _emit_rereview_event(state, job, head_sha, logger)

    #: The last panel result seen, so the trace can describe what actually ran
    #: even when `drive` escalated out of the loop.
    panel_trace: dict[str, Any] = {"result": None, "latency_ms": 0, "tokens": 0}
    reserved_tokens = 0

    def assess(profile: Profile) -> list[str]:
        started = _now_ms()
        try:
            result = run_panel(local_cfg, state, repo, number, lane, job_id, profile, logger=logger)
        except Exception:
            # A panel that could not run at all is a failure against the breaker:
            # a provider outage must eventually stop costing full timeouts.
            budget.record_failure(state, local_cfg, _budget_scope(job), "panel raised")
            raise
        latency = _elapsed_ms(started)
        # Spend is recorded with the reservation as an upper bound (runners do not
        # report token counts), so the NEXT reservation is stricter, never looser.
        spend = int(result.get("budget_tokens") or reserved_tokens or 0)
        budget.record_spend(
            state, job_id=job_id, repo=repo, number=number, tokens=spend,
            model=",".join(str(m) for m in (result.get("completed_reviewers") or []))[:120],
            latency_ms=latency,
        )
        if result.get("complete"):
            budget.record_success(state, _budget_scope(job))
        else:
            budget.record_failure(
                state, local_cfg, _budget_scope(job),
                f"panel {result.get('outcome', 'incomplete')}",
            )
        panel_trace.update({"result": result, "latency_ms": latency, "tokens": spend})
        if not result["complete"]:
            raise PartialPanel(result)
        # A complete panel that calls for more evidence must NOT re-run the identical
        # model loop; it escalates so the dispatcher can do one bounded re-gather.
        if any(sig == "MISSING_EVIDENCE" for sig in result["signals"]):
            raise EvidenceIncompleteError("panel verdict missing evidence; bounded gather, no re-run")
        return result["signals"]

    def _trace_panel() -> None:
        if panel_trace["result"] is not None:
            _emit_panel_trace(state, job, logger, panel_trace["result"],
                              latency_ms=int(panel_trace["latency_ms"]),
                              tokens=int(panel_trace["tokens"]))

    try:
        _transition_guarded(state, job_id, "assurance", logger=logger,
                            phase="dispatch", reason="panel start")
        minimum = decide_assurance(local_cfg, state, repo, number, lane)

        # The pre-spend gate. Nothing above this line costs a model call, so a
        # refusal here downgrades BEFORE any budget can be exceeded rather than
        # discovering the overspend afterwards.
        _strategy, reservation = _reserve_budget(local_cfg, state, job, logger, minimum)
        reserved_tokens = reservation.reserved_tokens
        if not reservation.allowed:
            return _budget_refused(state, job, head_sha, logger, reservation,
                                   snapshot_meta=snapshot_meta)

        final_profile, decision, steps = drive(minimum, assess, max_steps=6)
        _trace_panel()
    except PartialPanel as exc:
        _trace_panel()
        reason = f"partial panel: {exc.result['completed_reviewers']}/{exc.result['required_reviewers']}; no mutation"
        _transition_guarded(state, job_id, "degraded_draft", logger=logger,
                            phase="assurance", reason=reason)
        _log(logger, "warning", body="partial panel; degraded draft", phase="assurance",
             outcome="degraded_draft", event="decision",
             attributes={"decision.disposition": "PARTIAL_PANEL",
                         "decision.reason": reason[:200]})
        return {
            "job": job_id, "repo": repo, "number": number,
            "decision": "PARTIAL_PANEL", "status": "degraded_draft", "reason": reason,
            "completed_reviewers": exc.result["completed_reviewers"],
            "required_reviewers": exc.result["required_reviewers"],
            "final_profile": exc.result["profile"], "steps": [],
        }
    except JobBlockingError as exc:
        _trace_panel()
        _transition_guarded(state, job_id, "human_required", logger=logger,
                            phase="assurance", reason=str(exc))
        _log(logger, "error", body="job blocked", phase="assurance",
             outcome="human_required", event="decision",
             attributes={"decision.disposition": "JOB_BLOCKING",
                         "decision.reason": str(exc)[:200]})
        return {"job": job_id, "status": "human_required", "reason": str(exc),
                "decision": "JOB_BLOCKING"}
    except EvidenceIncompleteError as exc:
        _trace_panel()
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
        _log(logger, "warning", body=f"panel decision {decision}", phase="assurance",
             outcome="human_required", event="decision",
             attributes={"decision.disposition": decision})
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
         outcome=res.disposition, event="decision",
         attributes={"risk.score": res.risk_score, "risk.band": res.risk_band_name,
                     "decision.disposition": res.disposition,
                     "decision.reason": (res.reason or "")[:200],
                     "approval.failed_gates": res.failed_gates,
                     **metric_attributes(
                         tokens=int(panel_trace["tokens"]),
                         latency_ms=int(panel_trace["latency_ms"]),
                     )})
    # The head the panel reviewed is compared with the head currently observed.
    # `_load_pr_facts` deliberately keeps the observed head separate so this is a
    # real comparison rather than a value checked against itself.
    _emit_verify_event(logger, subject="reviewed head",
                       ok=bool(pr_facts.head_sha) and pr_facts.head_sha == head_sha,
                       detail=f"observed={pr_facts.head_sha or '<unknown>'} reviewed={head_sha}")
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
        advisory = _post_advisory_review(
            local_cfg, state, job, head_sha, logger,
            disposition=res.disposition, failed_gates=res.failed_gates,
            verdicts=verdicts, snapshot_meta=snapshot_meta,
        )
        _transition_guarded(state, job_id, "completed_advisory", logger=logger,
                            phase="advisory", reason="advisory review published")
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
        _emit_human_queue_event(logger, request, action="approve",
                                reason=res.reason or "human escalation")
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
        advisory = _post_advisory_review(
            local_cfg, state, job, head_sha, logger,
            disposition=res.disposition, failed_gates=res.failed_gates,
            verdicts=verdicts, snapshot_meta=snapshot_meta,
        )
        _transition_guarded(state, job_id, "completed_advisory", logger=logger,
                            phase="advisory", reason="advisory review published")

    return {
        "job": job_id, "repo": repo, "number": number,
        "decision": decision, "status": state.current_status(job_id),
        "approval_disposition": res.disposition,
        "advisory": advisory,
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
        # The archive is gone; refuse to silently upgrade this in-flight job.
        return local_cfg, {
            "pinned": False,
            "reason": f"pinned snapshot {pinned_hash[:12]} is no longer archived",
        }
    from policy import validate_policy

    try:
        # Model slug, prompt, tools, effort, and execution-mode changes must
        # re-enter shadow. Running jobs returned above retain their old pin.
        from model_registry import observe_runtime_routes

        route_meta = observe_runtime_routes(
            state,
            local_cfg,
            scope=str((local_cfg.get("repository") or {}).get("slug") or "default"),
        )
        effective_cfg = local_cfg
        if route_meta["shadow_locked"]:
            effective_cfg = json.loads(json.dumps(local_cfg))
            effective_cfg.setdefault("approval", {})["mode"] = "shadow"
            effective_cfg["approval"]["approval_enabled"] = False
            effective_cfg["approval"]["live_canary_approved"] = False
            effective_cfg.setdefault("authority", {})["approve"] = "shadow"
        snap = build_snapshot(effective_cfg, validate_policy=validate_policy)
    except (SnapshotError, ValueError) as exc:
        return local_cfg, {"pinned": False, "reason": str(exc)}

    active = store.active()
    if active is None or active.hash != snap.hash:
        store.activate(snap)
    state.execute("UPDATE jobs SET snapshot_hash=? WHERE id=?", (snap.hash, job_id))
    state.db.commit()
    return snap.config, {
        "pinned": True,
        "resumed": False,
        **snap.as_meta(),
        "route_qualification": route_meta,
    }



#: Seams over the lease so tests can intercept the GitHub assignee mutations.
def _lease_claim(local_cfg, state, repo, number, job, login):
    from lease import claim

    return claim(local_cfg, state, repo, number, job, login)


def _lease_release(local_cfg, state, repo, number, job, login):
    from lease import release

    return release(local_cfg, state, repo, number, job, login)


def _local_lease_holder(state: State, repo: str, number: int) -> str:
    row = state.db.execute(
        "SELECT job_id FROM leases WHERE repo=? AND number=?", (repo, number)
    ).fetchone()
    return row["job_id"] if row else ""



def run_job(
    local_cfg: dict[str, Any],
    job: dict[str, Any],
    *,
    state: State,
    capability_mode: str | None = None,
    claim_lease: bool = True,
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
    started_ms = _now_ms()

    if not canary_allowed(local_cfg, state, lane):
        try:
            _log(logger, "warning", body=f"{lane} canary not approved",
                 phase="dispatch", outcome="gated", event="preflight",
                 attributes={"preflight.canary_approved": False})
        except SafeStopSignal as exc:
            return _arrive_safe_stop(state, job, None, reason=str(exc))
        return {"job": job_id, "status": "gated", "reason": f"{lane} canary not approved",
                "snapshot": snapshot_meta}

    # Supersede stale human requests for this PR whose head or policy no longer match.
    supersede_for_head(state, repo, number, head_sha)
    supersede_for_policy(state, repo, number, local_cfg)

    # Claim the review lease BEFORE any model spend. A PR already claimed by
    # someone else is not ours to review: concurrent sweeps must not duplicate work
    # or post duplicate advisory comments.
    #
    # The claim runs INSIDE the guarded block so that an audit-logging failure here
    # safe-stops the job like any other, rather than escaping run_job.
    login = local_cfg.get("login", "")
    lease_held = False
    try:
        _emit_preflight(local_cfg, state, job, head_sha, logger,
                        snapshot_meta=snapshot_meta,
                        capability_mode=capability_mode,
                        capability_note=capability_note,
                        started_ms=started_ms)
        if claim_lease and login:
            held_by = _local_lease_holder(state, repo, number)
            if held_by and held_by != job_id:
                return {"job": job_id, "repo": repo, "number": number,
                        "status": "gated",
                        "reason": f"lease already held by job {held_by}",
                        "snapshot": snapshot_meta}
            try:
                lease_held = bool(
                    _lease_claim(local_cfg, state, repo, number, job_id, login)
                )
            except Exception as exc:
                _log(logger, "warning", body=f"lease claim failed: {exc}",
                     phase="dispatch", outcome="lease_unavailable")
                return {"job": job_id, "repo": repo, "number": number,
                        "status": "gated",
                        "reason": f"could not claim the review lease: {exc}",
                        "snapshot": snapshot_meta}
            if not lease_held:
                return {"job": job_id, "repo": repo, "number": number,
                        "status": "gated",
                        "reason": "the PR is claimed by another reviewer",
                        "snapshot": snapshot_meta}
            _log(logger, "info", body="review lease claimed", phase="dispatch",
                 outcome="lease_claimed", event="lease_acquired",
                 attributes={"lease.login": login,
                             **metric_attributes(latency_ms=_elapsed_ms(started_ms))})

        result = _run_job_inner(local_cfg, job, head_sha, logger, state, snapshot_meta)
    except SafeStopSignal as exc:
        result = _arrive_safe_stop(state, job, logger, reason=str(exc))
    except JobBlockingError as exc:
        result = {"job": job_id, "repo": repo, "number": number,
                  "status": "error", "decision": "JOB_BLOCKING", "reason": str(exc)}
    finally:
        # Release on EVERY exit path, including an unexpected exception. A retained
        # lease blocks the queue indefinitely. This block cannot raise: a failure
        # here must never replace the review outcome.
        if lease_held:
            release_error = ""
            try:
                _lease_release(local_cfg, state, repo, number, job_id, login)
            except Exception as exc:
                release_error = str(exc)
            try:
                if release_error:
                    _log(logger, "error",
                         body=f"lease release failed: {release_error}",
                         phase="dispatch", outcome="lease_release_failed",
                         event="lease_released")
                else:
                    _log(logger, "info", body="review lease released",
                         phase="dispatch", outcome="lease_released",
                         event="lease_released",
                         attributes=metric_attributes(latency_ms=_elapsed_ms(started_ms)))
            except Exception:
                pass

    result["snapshot"] = snapshot_meta
    return result


def _emit_preflight(
    local_cfg: dict[str, Any], state: State, job: dict[str, Any], head_sha: str, logger,
    *, snapshot_meta: dict[str, Any], capability_mode: str | None,
    capability_note: str, started_ms: int,
) -> None:
    """Emit `queueing` and `preflight` for a job that passed its entry checks.

    Called from inside `run_job`'s guarded block so that an audit-logging failure
    safe-stops this job like any other rather than escaping `run_job`.
    """
    _log(logger, "info", body=f"job queued for dispatch: {job['repo']}#{job['number']}",
         phase="dispatch", outcome="queued", event="queueing",
         attributes={"job.lane": job["lane"], "github.head.sha": head_sha,
                     "job.status": state.current_status(job["job_id"]) or ""})
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
    _log(logger, "info", body="preflight checks passed", phase="dispatch",
         outcome="ready", event="preflight",
         attributes={
             "preflight.canary_approved": True,
             "preflight.snapshot_pinned": bool(snapshot_meta.get("pinned")),
             "preflight.snapshot_reason": snapshot_meta.get("reason", ""),
             "policy.version": snapshot_meta.get("policy_version", ""),
             "github.capability_mode": capability_mode or "unprobed",
             **metric_attributes(latency_ms=_elapsed_ms(started_ms)),
         })


def canary_allowed(local_cfg: dict[str, Any], state: State, lane: str) -> bool:
    """Canary approval is authoritative in the SQLite `canaries` table; when no
    row exists it falls back to the repo-local config key, which is
    `incoming_canary_approved` / `author_canary_approved` (not `{lane}_...`)."""
    row = state.db.execute("SELECT status FROM canaries WHERE lane=?", (lane,)).fetchone()
    if row is not None:
        return row["status"] == "approved"
    key = "incoming_canary_approved" if lane == "incoming_review" else "author_canary_approved"
    return bool((local_cfg.get("dispatch") or {}).get(key, False))


def recover_interrupted(
    local_cfg: dict[str, Any],
    state: State,
) -> list[dict[str, Any]]:
    """Release leases stranded by a crashed worker without re-running its decision.

    Recovery is an explicit operator command. It only touches leases recorded in
    this state directory, REST-verifies each release through the normal lease
    helper, and safe-stops a non-terminal job rather than guessing which evidence
    or model output a terminated process had reached.
    """
    from states import can_transition

    login = str(local_cfg.get("login") or "").strip()
    rows = state.db.execute(
        "SELECT l.repo, l.number, l.job_id, j.status FROM leases l "
        "JOIN jobs j ON j.id=l.job_id ORDER BY l.claimed_at, l.repo, l.number"
    ).fetchall()
    recovered: list[dict[str, Any]] = []
    for row in rows:
        item = {"job": row["job_id"], "repo": row["repo"], "number": row["number"]}
        if not login:
            recovered.append({**item, "released": False, "reason": "configured login is empty"})
            continue
        try:
            _lease_release(local_cfg, state, row["repo"], row["number"], row["job_id"], login)
        except Exception as exc:
            recovered.append({**item, "released": False, "reason": str(exc)[:500]})
            continue
        if can_transition(row["status"], "safe_stop"):
            state.transition(
                row["job_id"],
                "safe_stop",
                reason="interrupted worker recovered; review lease released",
            )
        recovered.append({**item, "released": True, "status": state.current_status(row["job_id"])})

    # A worker can be killed after it transitioned a job but before (or without)
    # claiming a lease — the mid-panel window, and every dispatch that runs with
    # `claim_lease=False`. Such a job has no lease row, so the loop above never
    # sees it, and it would sit in a non-terminal state forever waiting for a
    # process that is gone. `recover` holds the state directory's exclusive
    # runtime lock, so nothing is in flight and safe-stopping these is sound:
    # that is what makes recovery possible with no manual DB surgery.
    leased = {row["job_id"] for row in rows}
    placeholders = ",".join("?" for _ in ACTIVE_WORKER_STATUSES)
    stranded = state.db.execute(
        f"SELECT id, status FROM jobs WHERE status IN ({placeholders}) ORDER BY updated_at, id",
        ACTIVE_WORKER_STATUSES,
    ).fetchall()
    for row in stranded:
        if row["id"] in leased or not can_transition(row["status"], "safe_stop"):
            continue
        state.transition(row["id"], "safe_stop",
                         reason="interrupted worker recovered; no lease was held")
        recovered.append({"job": row["id"], "released": False,
                          "reason": "no lease was held", "status": "safe_stop"})
    return recovered


#: Statuses that can only be occupied while a worker is ACTIVELY driving the job.
#: `recover` safe-stops these when no process holds the state directory. States
#: that are legitimately waiting on somebody else — `detected` (queued),
#: `human_approval_pending`, `human_required`, `degraded_draft`, `held`,
#: `retryable` — are deliberately NOT here: they are not stranded, and stopping
#: them would silently discard pending human work.
ACTIVE_WORKER_STATUSES = (
    "preflight", "evidence", "assurance", "adjudication",
    "approval_evaluation", "approval_revalidation", "approval_action",
    "advisory_action",
)

#: Statuses from which no further work is possible. Only these are eligible for
#: artifact retention: a job that could still be resumed keeps its artifacts.
TERMINAL_STATUSES = (
    "completed_auto_approved", "completed_human_declined", "completed_advisory",
    "completed", "superseded", "safe_stop", "closed", "merged",
)

#: Default retention window. Artifacts are model output and evidence copies; the
#: audit trail that explains a decision lives in SQLite and is never purged.
DEFAULT_RETENTION_DAYS = 30


def _retention_days(local_cfg: dict[str, Any]) -> int:
    section = (local_cfg.get("retention") or {})
    try:
        days = int(section.get("artifact_days", DEFAULT_RETENTION_DAYS))
    except (TypeError, ValueError):
        days = DEFAULT_RETENTION_DAYS
    return max(0, days)


def _artifact_manifest(directory: pathlib.Path) -> list[dict[str, Any]]:
    """Describe every file under `directory` by name, size and content hash.

    This is what makes a purge auditable: after the bytes are gone the ledger
    still states exactly which artifacts existed and what they hashed to, so a
    later reader can tell whether the artifact they are missing was deleted by
    retention or never written.
    """
    import hashlib

    manifest: list[dict[str, Any]] = []
    if not directory.is_dir():
        return manifest
    for path in sorted(directory.rglob("*")):
        if not path.is_file():
            continue
        try:
            data = path.read_bytes()
        except OSError as exc:
            manifest.append({"path": path.name, "error": str(exc)[:120]})
            continue
        manifest.append({
            "path": path.relative_to(directory).as_posix(),
            "bytes": len(data),
            "sha256": hashlib.sha256(data).hexdigest(),
        })
    return manifest


def _purge_tree(directory: pathlib.Path) -> int:
    """Delete every file under `directory`, then the directory. Returns file count."""
    import shutil

    if not directory.is_dir():
        return 0
    count = sum(1 for path in directory.rglob("*") if path.is_file())
    shutil.rmtree(directory, ignore_errors=True)
    return count


def retention_sweep(
    local_cfg: dict[str, Any], state: State, *, days: int | None = None,
    apply: bool = False,
) -> dict[str, Any]:
    """Purge artifacts for terminal jobs older than the retention window.

    Dry-run by default: `apply=False` reports exactly what WOULD be deleted and
    touches nothing, because a retention command that deletes on first invocation
    is a command operators run once by accident.

    What survives a purge, always:
      - the `jobs` row (identity, head, lane, final status, timestamps)
      - every `ledger_entries` row (the decision trail)
      - `mutations`, `approval_decisions`, `human_requests` (what was done, and
        on whose authority)
      - a `retention_manifest` ledger entry naming and hashing every artifact
        that was removed

    Only the artifact BYTES go: model output, evidence copies, JSONL logs.
    """
    window = _retention_days(local_cfg) if days is None else max(0, int(days))
    cutoff = (
        dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=window)
    ).isoformat().replace("+00:00", "Z")
    placeholders = ",".join("?" for _ in TERMINAL_STATUSES)
    rows = state.db.execute(
        f"SELECT id, repo, number, head_sha, status, updated_at FROM jobs "
        f"WHERE status IN ({placeholders}) AND updated_at < ? ORDER BY updated_at, id",
        (*TERMINAL_STATUSES, cutoff),
    ).fetchall()

    log_root = pathlib.Path((local_cfg.get("logging") or {}).get("directory") or "")
    purged: list[dict[str, Any]] = []
    for row in rows:
        job_id = row["id"]
        artifact_dir = state.root / "jobs" / job_id
        log_dir = (log_root / "jobs" / job_id) if str(log_root) else pathlib.Path("")
        manifest = _artifact_manifest(artifact_dir)
        log_manifest = _artifact_manifest(log_dir) if str(log_root) else []
        entry = {
            "job": job_id, "repo": row["repo"], "number": row["number"],
            "status": row["status"], "updated_at": row["updated_at"],
            "artifact_files": len(manifest), "log_files": len(log_manifest),
            "applied": bool(apply),
        }
        if apply:
            # Record the manifest BEFORE deleting. A crash between the two leaves
            # a manifest for artifacts that still exist (harmless); the reverse
            # would leave deleted artifacts with no audit record at all.
            _ledger_record(
                state,
                {"job_id": job_id, "repo": row["repo"], "number": row["number"]},
                row["head_sha"], "evidence",
                {"operation": "retention_purge", "retention_days": window,
                 "artifacts": manifest, "logs": log_manifest},
                entry_key="retention_manifest",
            )
            entry["artifact_files"] = _purge_tree(artifact_dir)
            if str(log_root):
                entry["log_files"] = _purge_tree(log_dir)
        purged.append(entry)

    return {
        "retention_days": window,
        "cutoff": cutoff,
        "applied": bool(apply),
        "eligible_jobs": len(purged),
        "jobs": purged,
    }


def reset_cooldowns(state: State, *, scope: str = "") -> dict[str, Any]:
    """Clear provider cooldowns and circuit breakers so work can resume.

    An operator command, never automatic: a cooldown exists because something
    failed, and clearing it on a timer would just re-spend against the same
    broken provider.
    """
    from budget import reset_breakers

    if scope:
        cursor = state.execute("DELETE FROM providers WHERE key=?", (scope,))
    else:
        cursor = state.execute("DELETE FROM providers", ())
    providers = int(cursor.rowcount or 0)
    state.db.commit()
    breakers = reset_breakers(state, scope)
    return {"scope": scope or "*", "providers_cleared": providers,
            "breakers_cleared": breakers}


def backup_state(state: State, destination: str | None = None) -> dict[str, Any]:
    """Take a consistent backup of the state database and its snapshot archive.

    `sqlite3.Connection.backup` is used rather than a file copy, so the backup is
    consistent even while WAL writes are in flight.
    """
    import shutil
    import sqlite3

    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    target = pathlib.Path(destination) if destination else (state.root / "backups" / stamp)
    target.mkdir(parents=True, exist_ok=True)
    db_path = target / "state.sqlite3"
    with sqlite3.connect(db_path) as handle:
        state.db.backup(handle)
    snapshots = state.root / "snapshots"
    copied = 0
    if snapshots.is_dir():
        shutil.copytree(snapshots, target / "snapshots", dirs_exist_ok=True)
        copied = sum(1 for path in (target / "snapshots").rglob("*") if path.is_file())
    return {"destination": str(target), "database": str(db_path),
            "snapshot_files": copied, "created_at": stamp}


def runtime_health(local_cfg: dict[str, Any], state: State) -> dict[str, Any]:
    """Local, side-effect-free health. No network, no mutation, no model calls.

    Reports the things that actually stop this harness: a corrupt database, an
    unwritable state or log directory, an open circuit breaker, a stranded lease,
    and how much of the cost budget the last day consumed.
    """
    import budget

    checks: dict[str, Any] = {}
    try:
        row = state.db.execute("PRAGMA integrity_check").fetchone()
        checks["database"] = str(row[0]) if row else "unknown"
    except Exception as exc:
        checks["database"] = f"error: {exc}"[:200]

    def _writable(path: pathlib.Path) -> bool:
        try:
            probe = path / ".health-probe"
            probe.write_text("ok", encoding="utf-8")
            probe.unlink()
            return True
        except OSError:
            return False

    checks["state_dir_writable"] = _writable(state.root)
    log_dir = (local_cfg.get("logging") or {}).get("directory") or ""
    checks["log_dir_writable"] = _writable(pathlib.Path(log_dir)) if log_dir else False

    breakers = [
        budget.breaker_state(state, row["scope"])
        for row in state.db.execute("SELECT scope FROM circuit_breakers ORDER BY scope")
    ]
    open_breakers = [b for b in breakers if b["status"] != budget.CLOSED]

    cooldowns = state.db.execute(
        "SELECT COUNT(*) AS c FROM providers WHERE unavailable_until IS NOT NULL"
    ).fetchone()
    oldest = state.db.execute(
        "SELECT id, status, updated_at FROM jobs WHERE status NOT IN "
        f"({','.join('?' for _ in TERMINAL_STATUSES)}) ORDER BY updated_at LIMIT 1",
        TERMINAL_STATUSES,
    ).fetchone()

    slug = str((local_cfg.get("repository") or {}).get("slug") or "")
    healthy = (
        checks["database"] == "ok"
        and checks["state_dir_writable"]
        and not open_breakers
    )
    return {
        "status": "healthy" if healthy else "degraded",
        "checks": checks,
        "runtime": runtime_status(state),
        "breakers": breakers,
        "open_breakers": [b["scope"] for b in open_breakers],
        "provider_cooldowns": int(cooldowns["c"]) if cooldowns else 0,
        "oldest_unfinished_job": (
            {"job": oldest["id"], "status": oldest["status"], "updated_at": oldest["updated_at"]}
            if oldest else None
        ),
        "budget": {
            "limits": budget.limits(local_cfg),
            "repo_tokens_24h": budget.spent_for_repo(state, slug) if slug else 0,
        },
        "retention_days": _retention_days(local_cfg),
    }


def runtime_status(state: State) -> dict[str, Any]:
    """Return local, side-effect-free managed-harness health for one state dir."""
    rows = state.db.execute(
        "SELECT status, COUNT(*) AS count FROM jobs GROUP BY status ORDER BY status"
    ).fetchall()
    leases = state.db.execute("SELECT COUNT(*) AS count FROM leases").fetchone()["count"]
    return {
        "status": "ready",
        "state_dir": str(state.root),
        "jobs": {row["status"]: row["count"] for row in rows},
        "leases": leases,
        "worker_concurrency": 1,
    }


def _managed_sweep(
    cfg: dict[str, Any],
    state: State,
    slug: str,
    *,
    lane: str,
    limit: int,
    capability_mode: Any,
) -> dict[str, Any]:
    """Reconcile the queue, then run up to `limit` detected jobs of one lane.

    Intentionally serial per state directory. `limit` controls batch size, not
    parallelism, and order is a stable FIFO even when two jobs were detected in
    the same second.

    `pending` is the number of jobs still `detected` in this lane AFTER the batch
    ran — the cadence reads it to decide whether the next sweep should be at the
    active interval or one step further into backoff.
    """
    queue_result = _reconcile_queue(cfg, state, slug)
    rows = state.db.execute(
        "SELECT id AS job_id, repo, number, lane FROM jobs "
        "WHERE lane=? AND status='detected' ORDER BY created_at, id LIMIT ?",
        (lane, limit),
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
    pending = state.db.execute(
        "SELECT COUNT(*) AS n FROM jobs WHERE lane=? AND status='detected'", (lane,)
    ).fetchone()["n"]
    return {"queue": queue_result, "results": results, "pending": int(pending)}


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

    # The scheduler's entry point. A timer runs this at the SHORTEST interval the
    # cadence can choose; `tick` decides whether this is actually the moment to
    # sweep, so backoff lives in persisted state rather than in the timer.
    tick = sub.add_parser(
        "tick",
        help="sweep only if the persisted cadence says it is due, then reschedule",
    )
    tick.add_argument("--lane", default="incoming_review")
    tick.add_argument("--limit", type=int, default=2)
    tick.add_argument("--force", action="store_true",
                      help="sweep regardless of the schedule; still reschedules afterwards")
    tick.add_argument("--dry-run", action="store_true",
                      help="report the decision and exit without sweeping or rescheduling")

    one = sub.add_parser("dispatch-one")
    one.add_argument("--number", required=True, type=int)
    one.add_argument("--job", required=True)
    one.add_argument("--lane", required=True)

    sub.add_parser(
        "recover",
        help="release verified leases left by an interrupted worker; never re-runs a decision",
    )

    sub.add_parser("status", help="show local state-dir health without network activity")
    sub.add_parser("health", help="local health check: database, disks, breakers, budget")

    ret = sub.add_parser(
        "retention",
        help="purge artifacts for terminal jobs past the retention window "
             "(dry-run unless --apply); the audit trail is never purged",
    )
    ret.add_argument("--days", type=int, default=None,
                     help="override retention.artifact_days for this run")
    ret.add_argument("--apply", action="store_true",
                     help="actually delete; without it nothing is removed")

    cooldown = sub.add_parser(
        "cooldown-reset", help="clear provider cooldowns and circuit breakers")
    cooldown.add_argument("--scope", default="",
                          help="a single provider key or breaker scope; default all")

    backup = sub.add_parser("backup", help="consistent backup of state.sqlite3 + snapshots")
    backup.add_argument("--dest", default=None, help="destination directory")

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
    runtime_lock = state.try_runtime_lock(args.command)
    if runtime_lock is None:
        print(json.dumps({
            "status": "sweep_already_running",
            "reason": "another command owns this state directory",
        }, indent=2, sort_keys=True))
        state.close()
        return 0


    # Local, side-effect-free commands: no capability probe, no network.
    _LOCAL_COMMANDS = {
        "status": lambda: runtime_status(state),
        "health": lambda: runtime_health(cfg, state),
        "retention": lambda: retention_sweep(
            cfg, state, days=getattr(args, "days", None), apply=getattr(args, "apply", False)),
        "cooldown-reset": lambda: reset_cooldowns(state, scope=getattr(args, "scope", "")),
        "backup": lambda: backup_state(state, getattr(args, "dest", None)),
    }
    if args.command in _LOCAL_COMMANDS:
        try:
            json.dump(_LOCAL_COMMANDS[args.command](), sys.stdout, indent=2, sort_keys=True)
            sys.stdout.write("\n")
        finally:
            runtime_lock.release()
            state.close()
        return 0
    try:
        # Probe capability ONCE per invocation, not per job: it costs two reads and
        # applies to the whole repository. A repo we cannot write to still produces
        # drafts and human requests rather than failing.
        capability_mode = None
        slug = (cfg.get("repository") or {}).get("slug", "")
        if slug and not args.no_capability_probe and args.command != "recover":
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
                return 1

        if args.command == "recover":
            json.dump(recover_interrupted(cfg, state), sys.stdout, indent=2, sort_keys=True)
        elif args.command == "sweep":
            if not slug:
                raise SystemExit("repository.slug is required for a managed sweep")
            json.dump(
                _managed_sweep(
                    cfg, state, slug,
                    lane=args.lane, limit=args.limit, capability_mode=capability_mode,
                ),
                sys.stdout,
                indent=2,
                sort_keys=True,
            )
        elif args.command == "tick":
            if not slug:
                raise SystemExit("repository.slug is required for a scheduled tick")
            scope = f"{slug}:{args.lane}"
            stored = cadence_read(state, scope)
            is_due = args.force or cadence_due(stored.get("next_run_at"))
            if not is_due:
                # The common case. A timer fires at the shortest interval and most
                # of those firings are meant to do nothing.
                json.dump({
                    "status": "not_due",
                    "scope": scope,
                    "next_run_at": stored.get("next_run_at"),
                    "idle_streak": stored.get("idle_streak", 0),
                    "last_reason": stored.get("last_reason"),
                }, sys.stdout, indent=2, sort_keys=True)
            elif args.dry_run:
                json.dump({
                    "status": "due",
                    "scope": scope,
                    "dry_run": True,
                    "next_run_at": stored.get("next_run_at"),
                    "idle_streak": stored.get("idle_streak", 0),
                }, sys.stdout, indent=2, sort_keys=True)
            else:
                swept = _managed_sweep(
                    cfg, state, slug,
                    lane=args.lane, limit=args.limit, capability_mode=capability_mode,
                )
                decision = cadence_decide(
                    cfg.get("poll"),
                    queue_count=int(swept.get("pending") or 0) + len(swept.get("results") or []),
                    remaining=_rest_remaining(state),
                    idle_streak=int(stored.get("idle_streak") or 0),
                )
                ran_at = utcnow()
                next_run_at = schedule_after(decision.delay_seconds, ran_at)
                cadence_write(
                    state, scope,
                    idle_streak=decision.idle_streak,
                    next_run_at=next_run_at,
                    last_run_at=ran_at,
                    reason=decision.reason,
                )
                json.dump({
                    "status": "swept",
                    "scope": scope,
                    "cadence": {**decision.as_dict(), "next_run_at": next_run_at},
                    **swept,
                }, sys.stdout, indent=2, sort_keys=True)
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
        runtime_lock.release()
        state.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())