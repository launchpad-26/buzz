"""Durable, SQLite-backed human approval queue for review-queue-automation.

Keyed by `repo + PR number + head SHA + full-config policy hash` and tied to a
`job_id`. A changed SHA or policy hash supersedes a pending request; multiple
unrelated requests may be pending at once. Decisions are made via deterministic
CLI commands (no interactive stdin).

Idempotency: enqueueing the same (repo, number, head, policy, job) reuses the
existing request_id; it never duplicates.

The `job_id` column is added lazily here (idempotent ALTER) so the feature works
even before common.py's canonical migration is updated; the canonical schema
change is requested in WORKMUX_RESULT.md.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import uuid
from typing import Any

from common import State, utcnow

# 64-hex (full) policy hash, not a 24-hex truncation.
POLICY_HASH_LENGTH = 64


def policy_hash(policy: dict[str, Any]) -> str:
    """Deterministic full-config/policy hash (unsliced SHA-256).

    Pass the *full* normalized config to bind a request to the whole runtime
    policy (approval thresholds, risk bands, assurance, human_queue), so a
    change anywhere in the policy supersedes the request.
    """
    canonical = json.dumps(policy, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode()).hexdigest()


class RequestQueueError(Exception):
    pass


def _expiry(created_at: str, minutes: int) -> str:
    try:
        base = dt.datetime.fromisoformat(created_at.replace("Z", "+00:00"))
    except ValueError:
        base = dt.datetime.now(dt.timezone.utc)
    return (
        (base + dt.timedelta(minutes=minutes)).isoformat().replace("+00:00", "Z")
    )


_HUMAN_COLUMNS = (
    "job_id", "request_id", "repo", "number", "head_sha", "policy_hash", "state",
    "created_at", "expires_at", "summary", "assurance", "reviewers", "risk_score",
    "risk_band", "protected", "failed_gates", "ci", "findings", "recommendation",
    "rationale", "action", "decision", "decision_actor", "decided_at",
)


def _ensure_job_id_column(state: State) -> bool:
    """Idempotently add the `job_id` column when the segment migration has not.

    common.py owns the canonical schema; until it is updated this runtime ALTER
    keeps the queue functional. Returns True when the column is present afterward.
    """
    cols = {r["name"] for r in state.db.execute("PRAGMA table_info(human_requests)")}
    if "job_id" in cols:
        return True
    try:
        state.db.execute("ALTER TABLE human_requests ADD COLUMN job_id TEXT")
        state.db.commit()
    except Exception:
        state.db.rollback()
        try:
            state.db.commit()
        except Exception:
            pass
        return False
    return True


def enqueue(
    state: State,
    *,
    repo: str,
    number: int,
    head_sha: str,
    policy: dict[str, Any],
    summary: str,
    assurance: dict[str, Any],
    reviewers: list[str],
    risk_score: float,
    risk_band: str,
    protected: list[str],
    failed_gates: list[str],
    ci: dict[str, Any],
    findings: list[str],
    recommendation: str,
    rationale: str,
    action: str,
    job_id: str = "",
    expiry_minutes: int = 1440,
) -> dict[str, Any]:
    _ensure_job_id_column(state)
    policy_hash_value = policy_hash(policy)
    # Enqueue stores job_id as "" when absent, so the dedupe must compare against
    # "" (SQL `= NULL` never matches, which would let the same natural key insert
    # twice and collide on the UNIQUE index).
    stored_job_id = job_id or ""
    existing = state.db.execute(
        "SELECT * FROM human_requests WHERE repo=? AND number=? AND head_sha=? AND policy_hash=? AND job_id=?",
        (repo, number, head_sha, policy_hash_value, stored_job_id),
    ).fetchone()
    if existing:
        return dict(existing)

    request_id = uuid.uuid4().hex[:16]
    created_at = utcnow()
    values = {
        "job_id": job_id or "",
        "request_id": request_id,
        "repo": repo,
        "number": int(number),
        "head_sha": head_sha,
        "policy_hash": policy_hash_value,
        "state": "pending",
        "created_at": created_at,
        "expires_at": _expiry(created_at, expiry_minutes),
        "summary": (summary or "")[:400],
        "assurance": json.dumps(assurance or {}),
        "reviewers": json.dumps(reviewers or []),
        "risk_score": float(risk_score),
        "risk_band": risk_band,
        "protected": json.dumps(protected or []),
        "failed_gates": json.dumps(failed_gates or []),
        "ci": json.dumps(ci or {}),
        "findings": json.dumps(findings or []),
        "recommendation": recommendation,
        "rationale": (rationale or "")[:800],
        "action": action,
        "decision": "none",
        "decision_actor": "",
        "decided_at": "",
    }
    cols = list(_HUMAN_COLUMNS)
    placeholders = ",".join("?" for _ in cols)
    state.db.execute(
        f"INSERT INTO human_requests({','.join(cols)}) VALUES({placeholders})",
        tuple(values[c] for c in cols),
    )
    state.db.commit()
    return values


def list_pending(state: State) -> list[dict[str, Any]]:
    _ensure_job_id_column(state)
    rows = state.db.execute(
        "SELECT * FROM human_requests WHERE state='pending' ORDER BY created_at ASC"
    ).fetchall()
    return [dict(r) for r in rows]


def get(state: State, request_id: str) -> dict[str, Any] | None:
    row = state.db.execute(
        "SELECT * FROM human_requests WHERE request_id=?", (request_id,)
    ).fetchone()
    return dict(row) if row else None


def is_expired(row: dict[str, Any]) -> bool:
    if not row.get("expires_at"):
        return False
    try:
        expiry = dt.datetime.fromisoformat(row["expires_at"].replace("Z", "+00:00"))
    except ValueError:
        return True
    return dt.datetime.now(dt.timezone.utc) > expiry


def validate_decision_against(row: dict[str, Any], repo: str, number: int, head_sha: str, policy: dict[str, Any]) -> None:
    """Fail closed if an approval decision no longer matches current state."""
    if row.get("head_sha") != head_sha:
        raise RequestQueueError("decision's head SHA is stale")
    if row.get("policy_hash") != policy_hash(policy):
        raise RequestQueueError("decision's policy hash is stale")
    if isinstance(row.get("number"), (int, float)) and row["number"] != int(number):
        raise RequestQueueError("decision's PR number mismatch")


def is_eligible(row: dict[str, Any], repo, number, head_sha, policy) -> bool:
    """An approval is usable only if pending+approved and not expired/stale."""
    try:
        validate_decision_against(row, repo, number, head_sha, policy)
    except RequestQueueError:
        return False
    if row.get("decision") != "approve":
        return False
    return not is_expired(row)


def find_approved(
    state: State,
    job_id: str,
    repo: str,
    number: int,
    head_sha: str,
    policy: dict[str, Any],
) -> dict[str, Any] | None:
    """Return the usable human `approve` decision bound to `job_id`, or None."""
    _ensure_job_id_column(state)
    ph = policy_hash(policy)
    rows = state.db.execute(
        "SELECT * FROM human_requests WHERE job_id=? AND repo=? AND number=?",
        (job_id, repo, int(number)),
    ).fetchall()
    for row in rows:
        r = dict(row)
        if r.get("decision") != "approve":
            continue
        try:
            validate_decision_against(r, repo, number, head_sha, policy)
        except RequestQueueError:
            continue
        if is_expired(r):
            continue
        return r
    return None


def decide(
    state: State,
    request_id: str,
    decision: str,
    actor: str,
    reason: str = "",
) -> dict[str, Any]:
    """Record a human decision: approve | decline | request_changes.

    Does not mutate a PR itself. Approval is resumed through final revalidation.

    `approve` leaves the job `human_approval_pending` until `resume` moves it to
    `approval_revalidation`. `decline`/`request_changes` are terminal: the bound
    job (if any and still pending approval) moves to `completed_human_declined`.
    """
    row = get(state, request_id)
    if row is None:
        raise RequestQueueError(f"unknown human request {request_id}")
    if row["state"] != "pending":
        raise RequestQueueError(f"human request {request_id} is not pending")
    if is_expired(row):
        raise RequestQueueError(f"human request {request_id} expired")
    norm = decision.lower()
    if norm not in {"approve", "decline", "request_changes"}:
        raise RequestQueueError(f"invalid decision: {decision}")
    now = utcnow()
    state.db.execute(
        "UPDATE human_requests SET state='decided', decision=?, decision_actor=?, decided_at=?, rationale=? "
        "WHERE request_id=?",
        (norm, actor, now, reason, request_id),
    )
    state.db.commit()
    updated = get(state, request_id)

    if norm in {"decline", "request_changes"}:
        job_declined = _decline_job(state, updated)
        updated = dict(updated)
        updated["job_declined"] = job_declined
    return updated


def _decline_job(state: State, request: dict[str, Any]) -> bool:
    """Move a bound job that is still awaiting human approval to a terminal decline."""
    job_id = request.get("job_id") or ""
    if not job_id:
        return False
    row = state.db.execute("SELECT status FROM jobs WHERE id=?", (job_id,)).fetchone()
    if not row or row["status"] != "human_approval_pending":
        return False
    try:
        state.db.execute(
            "UPDATE jobs SET status='completed_human_declined', reason=?, updated_at=? WHERE id=?",
            (request.get("decision_actor") or "human", utcnow(), job_id),
        )
        state.db.commit()
        return True
    except Exception:
        return False


def remove(state: State, request_id: str) -> None:
    state.db.execute("DELETE FROM human_requests WHERE request_id=?", (request_id,))
    state.db.commit()


def set_execution_state(state: State, request_id: str, exec_state: str) -> None:
    """Move a decided request through its execution states.

    exec_state is one of: execution_pending | executed | execution_failed |
    cancelled | withdrawn. This is recorded separately from the human decision so
    an action is never marked successful before GitHub confirms it (the caller
    confirms via REST and only then calls this with 'executed').
    """
    valid = {"execution_pending", "executed", "execution_failed", "cancelled", "withdrawn"}
    if exec_state not in valid:
        raise RequestQueueError(f"invalid execution state {exec_state}")
    state.db.execute(
        "UPDATE human_requests SET state=? WHERE request_id=?",
        (exec_state, request_id),
    )
    state.db.commit()


def supersede_for_head(state: State, repo: str, number: int, current_head: str) -> int:
    """Supersede pending requests for (repo, PR) bound to a different head."""
    _ensure_job_id_column(state)
    rows = state.db.execute(
        "SELECT request_id, head_sha FROM human_requests WHERE repo=? AND number=? AND state='pending'",
        (repo, number),
    ).fetchall()
    count = 0
    for row in rows:
        if row["head_sha"] != current_head:
            state.db.execute(
                "UPDATE human_requests SET state='superseded' WHERE request_id=?",
                (row["request_id"],),
            )
            count += 1
    state.db.commit()
    return count


def supersede_for_policy(state: State, repo: str, number: int, policy: dict[str, Any]) -> int:
    """Supersede pending requests for (repo, PR) whose policy hash no longer matches."""
    _ensure_job_id_column(state)
    current = policy_hash(policy)
    rows = state.db.execute(
        "SELECT request_id, policy_hash FROM human_requests WHERE repo=? AND number=? AND state='pending'",
        (repo, number),
    ).fetchall()
    count = 0
    for row in rows:
        if row["policy_hash"] != current:
            state.db.execute(
                "UPDATE human_requests SET state='superseded' WHERE request_id=?",
                (row["request_id"],),
            )
            count += 1
    state.db.commit()
    return count