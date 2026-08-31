"""Cost, retry and rate-limit controls for review-queue-automation.

Before this module existed the only spend control in the whole skill was
`approval.daily_limit` (a cap on APPROVE mutations, not on model spend) and a
per-state-directory concurrency of one. There was no budget, no retry ceiling
and no circuit breaker, so a provider outage or one expensive PR could burn an
unbounded number of full-timeout model invocations.

The rule this module enforces is **reserve before you spend**:

1. `reserve()` is called by the orchestrator BEFORE the panel runs. It projects
   `already spent for this scope + the strategy's declared budget_tokens` against
   every configured limit. If the projection would breach a limit, the reservation
   is refused and the caller downgrades to a draft or to a human. The spend never
   happens, so a budget can be reached but not exceeded.
2. `record_spend()` is called AFTER the panel, with the reservation as an
   upper-bound estimate of what that attempt cost. Runners do not report token
   counts, so the declared budget is used; it over-counts rather than
   under-counts, which makes the next reservation stricter, never looser.

The circuit breaker is scoped (per repo, per provider family). Consecutive
failures open it; while open, `reserve()` refuses pre-spend. A breaker that has
been open longer than its cooldown half-opens: one attempt is permitted, and its
outcome either closes the breaker or re-opens it for another cooldown.

Everything here is local SQLite state in the job's own state directory. No
network, no clock other than the wall clock, and every read fails closed: an
unknown value is treated as "cannot prove we are within budget".
"""

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field
from typing import Any

from common import utcnow

#: Reservation kinds recorded in `cost_ledger`.
RESERVATION = "reservation"
SPEND = "spend"

#: Downgrade targets, in descending authority. `reserve()` never returns a
#: downgrade that would RAISE authority.
DRAFT = "draft"
HUMAN = "human"

CLOSED = "closed"
OPEN = "open"
HALF_OPEN = "half_open"

#: Defaults are deliberately generous but finite: the point is that an unbounded
#: run is impossible, not that a specific number is correct for every repo.
DEFAULTS: dict[str, Any] = {
    "per_pr_tokens": 2_000_000,
    "per_repo_daily_tokens": 40_000_000,
    "per_model_daily_tokens": 20_000_000,
    "max_attempts_per_job": 6,
    "max_concurrent_jobs": 1,
    # Deliberately 0 (disabled) by default rather than inheriting
    # `poll.rest_remaining_floor`. The approval gate ALREADY fails closed on that
    # floor immediately before a mutation, which is the more precise place to
    # enforce it; a pre-spend copy would pre-empt that gate and turn a
    # human_escalation into a plain refusal. An operator who wants spend itself
    # gated on REST headroom sets this key explicitly.
    "rest_remaining_floor": 0,
    "circuit_breaker": {"failure_threshold": 3, "cooldown_seconds": 900},
}

#: Job statuses that occupy a concurrency slot (a job that may still spend).
IN_FLIGHT_STATUSES = (
    "preflight", "evidence", "assurance", "adjudication",
    "approval_evaluation", "approval_revalidation", "approval_action",
)


class BudgetError(ValueError):
    """Raised when a budget section is structurally unusable."""


@dataclass(frozen=True)
class BudgetDecision:
    """The pre-spend verdict. `allowed=False` means nothing may be spent."""

    allowed: bool
    reserved_tokens: int
    reason: str = ""
    downgrade: str = ""
    limit: str = ""
    headroom: dict[str, int] = field(default_factory=dict)
    breaker: str = CLOSED

    def as_dict(self) -> dict[str, Any]:
        return {
            "allowed": self.allowed,
            "reserved_tokens": self.reserved_tokens,
            "reason": self.reason,
            "downgrade": self.downgrade,
            "limit": self.limit,
            "headroom": dict(self.headroom),
            "breaker": self.breaker,
        }


def limits(config: dict[str, Any]) -> dict[str, Any]:
    """Resolve the effective budget limits, filling defaults for absent keys.

    A limit of 0 (or a negative number) means "unlimited" for that axis, which is
    how an operator opts a single axis out without disabling the others.
    """
    section = dict((config or {}).get("budget") or {})
    resolved: dict[str, Any] = dict(DEFAULTS)
    breaker = dict(DEFAULTS["circuit_breaker"])
    breaker.update(dict(section.get("circuit_breaker") or {}))
    resolved.update({k: v for k, v in section.items() if k != "circuit_breaker"})
    resolved["circuit_breaker"] = breaker
    for key in ("per_pr_tokens", "per_repo_daily_tokens", "per_model_daily_tokens",
                "max_attempts_per_job", "max_concurrent_jobs", "rest_remaining_floor"):
        value = resolved.get(key, 0)
        if isinstance(value, bool) or not isinstance(value, int):
            raise BudgetError(f"budget.{key} must be an integer, got {value!r}")
    return resolved


def validate_budget(config: dict[str, Any]) -> list[str]:
    """Deterministic issues list for a `budget` section. Empty == valid."""
    section = (config or {}).get("budget")
    if section is None:
        return []
    if not isinstance(section, dict):
        return ["budget must be an object"]
    issues: list[str] = []
    for key in ("per_pr_tokens", "per_repo_daily_tokens", "per_model_daily_tokens",
                "max_attempts_per_job", "max_concurrent_jobs", "rest_remaining_floor"):
        if key not in section:
            continue
        value = section[key]
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            issues.append(f"budget.{key} must be a non-negative integer")
    breaker = section.get("circuit_breaker")
    if breaker is not None:
        if not isinstance(breaker, dict):
            issues.append("budget.circuit_breaker must be an object")
        else:
            for key in ("failure_threshold", "cooldown_seconds"):
                if key not in breaker:
                    continue
                value = breaker[key]
                if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
                    issues.append(f"budget.circuit_breaker.{key} must be a positive integer")
    return issues


# ---- accounting -------------------------------------------------------------
def _since(hours: int = 24) -> str:
    return (
        dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=hours)
    ).isoformat().replace("+00:00", "Z")


def _sum(state, sql: str, params: tuple) -> int:
    row = state.db.execute(sql, params).fetchone()
    return int(row["total"] or 0) if row else 0


def spent_for_pr(state, repo: str, number: int) -> int:
    return _sum(
        state,
        "SELECT SUM(tokens) AS total FROM cost_ledger "
        "WHERE kind=? AND repo=? AND number=?",
        (SPEND, repo, number),
    )


def spent_for_repo(state, repo: str, *, hours: int = 24) -> int:
    return _sum(
        state,
        "SELECT SUM(tokens) AS total FROM cost_ledger "
        "WHERE kind=? AND repo=? AND recorded_at>=?",
        (SPEND, repo, _since(hours)),
    )


def spent_for_model(state, model: str, *, hours: int = 24) -> int:
    return _sum(
        state,
        "SELECT SUM(tokens) AS total FROM cost_ledger "
        "WHERE kind=? AND model=? AND recorded_at>=?",
        (SPEND, model, _since(hours)),
    )


def attempts_for_job(state, job_id: str) -> int:
    row = state.db.execute(
        "SELECT COUNT(*) AS c FROM cost_ledger WHERE kind=? AND job_id=?",
        (RESERVATION, job_id),
    ).fetchone()
    return int(row["c"]) if row else 0


def in_flight_jobs(state, *, exclude_job: str = "") -> int:
    placeholders = ",".join("?" for _ in IN_FLIGHT_STATUSES)
    params: list[Any] = list(IN_FLIGHT_STATUSES)
    sql = f"SELECT COUNT(*) AS c FROM jobs WHERE status IN ({placeholders})"
    if exclude_job:
        sql += " AND id<>?"
        params.append(exclude_job)
    row = state.db.execute(sql, tuple(params)).fetchone()
    return int(row["c"]) if row else 0


def record_reservation(state, *, job_id: str, repo: str, number: int, tokens: int,
                       model: str = "", provider_family: str = "") -> None:
    _insert(state, RESERVATION, job_id, repo, number, model, provider_family, tokens, 0)


def record_spend(state, *, job_id: str, repo: str, number: int, tokens: int,
                 model: str = "", provider_family: str = "", latency_ms: int = 0) -> None:
    """Record what an attempt actually cost (upper bound; see the module docstring)."""
    _insert(state, SPEND, job_id, repo, number, model, provider_family, tokens, latency_ms)


def _insert(state, kind: str, job_id: str, repo: str, number: int, model: str,
            provider_family: str, tokens: int, latency_ms: int) -> None:
    state.execute(
        "INSERT INTO cost_ledger(recorded_at,job_id,repo,number,model,provider_family,"
        "kind,tokens,latency_ms) VALUES(?,?,?,?,?,?,?,?,?)",
        (utcnow(), job_id, repo, int(number), model or "", provider_family or "",
         kind, max(0, int(tokens)), max(0, int(latency_ms))),
    )
    state.db.commit()


def usage(state, repo: str, number: int, *, job_id: str = "") -> dict[str, int]:
    """Bounded, log-safe usage counters for one job/PR/repo."""
    return {
        "pr_tokens": spent_for_pr(state, repo, number),
        "repo_tokens_24h": spent_for_repo(state, repo),
        "job_attempts": attempts_for_job(state, job_id) if job_id else 0,
        "jobs_in_flight": in_flight_jobs(state),
    }


# ---- circuit breaker --------------------------------------------------------
def _breaker_row(state, scope: str):
    return state.db.execute(
        "SELECT scope,failures,status,open_until,last_error FROM circuit_breakers WHERE scope=?",
        (scope,),
    ).fetchone()


def breaker_state(state, scope: str) -> dict[str, Any]:
    """Current breaker status for `scope`, half-opening an expired open breaker."""
    row = _breaker_row(state, scope)
    if row is None:
        return {"scope": scope, "status": CLOSED, "failures": 0, "open_until": ""}
    status = row["status"] or CLOSED
    open_until = row["open_until"] or ""
    if status == OPEN and open_until and _expired(open_until):
        status = HALF_OPEN
    return {
        "scope": scope,
        "status": status,
        "failures": int(row["failures"] or 0),
        "open_until": open_until,
        "last_error": (row["last_error"] or "")[:200],
    }


def _expired(timestamp: str) -> bool:
    try:
        when = dt.datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    except ValueError:
        # An unparseable timestamp must not pin the breaker open forever.
        return True
    return dt.datetime.now(dt.timezone.utc) >= when


def record_failure(state, config: dict[str, Any], scope: str, error: str = "") -> dict[str, Any]:
    """Count one failure against `scope`, opening the breaker at the threshold."""
    resolved = limits(config)["circuit_breaker"]
    threshold = int(resolved["failure_threshold"])
    cooldown = int(resolved["cooldown_seconds"])
    row = _breaker_row(state, scope)
    failures = (int(row["failures"] or 0) if row else 0) + 1
    status = CLOSED
    open_until = ""
    if failures >= threshold:
        status = OPEN
        open_until = (
            dt.datetime.now(dt.timezone.utc) + dt.timedelta(seconds=cooldown)
        ).isoformat().replace("+00:00", "Z")
    state.execute(
        "INSERT INTO circuit_breakers(scope,failures,status,open_until,last_error,updated_at) "
        "VALUES(?,?,?,?,?,?) ON CONFLICT(scope) DO UPDATE SET failures=excluded.failures,"
        "status=excluded.status,open_until=excluded.open_until,last_error=excluded.last_error,"
        "updated_at=excluded.updated_at",
        (scope, failures, status, open_until, (error or "")[:300], utcnow()),
    )
    state.db.commit()
    return {"scope": scope, "status": status, "failures": failures, "open_until": open_until}


def record_success(state, scope: str) -> dict[str, Any]:
    """A success closes the breaker and clears its failure count."""
    state.execute(
        "INSERT INTO circuit_breakers(scope,failures,status,open_until,last_error,updated_at) "
        "VALUES(?,0,?,'','',?) ON CONFLICT(scope) DO UPDATE SET failures=0,"
        "status=excluded.status,open_until='',last_error='',updated_at=excluded.updated_at",
        (scope, CLOSED, utcnow()),
    )
    state.db.commit()
    return {"scope": scope, "status": CLOSED, "failures": 0, "open_until": ""}


def reset_breakers(state, scope: str = "") -> int:
    """Operator cooldown reset. Returns how many breakers were cleared."""
    if scope:
        cursor = state.execute("DELETE FROM circuit_breakers WHERE scope=?", (scope,))
    else:
        cursor = state.execute("DELETE FROM circuit_breakers", ())
    state.db.commit()
    return int(cursor.rowcount or 0)


# ---- the pre-spend gate -----------------------------------------------------
def reserve(
    state,
    config: dict[str, Any],
    *,
    job_id: str,
    repo: str,
    number: int,
    tokens: int,
    scope: str = "",
    rest_remaining: int | None = None,
) -> BudgetDecision:
    """Decide, BEFORE any spend, whether this attempt may run.

    Refusal carries the downgrade the caller must apply: `draft` when the work can
    still produce a non-authoritative artefact, `human` when the situation needs a
    person (a hard rate-limit floor, or an open circuit breaker).

    A successful reservation is RECORDED, so the retry ceiling counts attempts
    that were permitted rather than attempts that happened to complete.
    """
    resolved = limits(config)
    breaker_scope = scope or repo
    tokens = max(0, int(tokens))

    breaker = breaker_state(state, breaker_scope)
    if breaker["status"] == OPEN:
        return BudgetDecision(
            allowed=False, reserved_tokens=0, limit="circuit_breaker",
            downgrade=HUMAN, breaker=OPEN,
            reason=(f"circuit breaker open for {breaker_scope} after "
                    f"{breaker['failures']} consecutive failures; open until "
                    f"{breaker['open_until']}"),
        )

    floor = int(resolved["rest_remaining_floor"])
    if floor > 0:
        if rest_remaining is None:
            return BudgetDecision(
                allowed=False, reserved_tokens=0, limit="rest_remaining_floor",
                downgrade=HUMAN, breaker=breaker["status"],
                reason=("REST rate-limit remaining is unknown and a floor of "
                        f"{floor} is configured; an unprovable floor is not a pass"),
            )
        if int(rest_remaining) < floor:
            return BudgetDecision(
                allowed=False, reserved_tokens=0, limit="rest_remaining_floor",
                downgrade=HUMAN, breaker=breaker["status"],
                reason=f"REST remaining {rest_remaining} is below the floor of {floor}",
            )

    max_attempts = int(resolved["max_attempts_per_job"])
    attempts = attempts_for_job(state, job_id)
    if max_attempts > 0 and attempts >= max_attempts:
        return BudgetDecision(
            allowed=False, reserved_tokens=0, limit="max_attempts_per_job",
            downgrade=HUMAN, breaker=breaker["status"],
            reason=f"retry ceiling reached: {attempts}/{max_attempts} attempts for this job",
        )

    max_concurrent = int(resolved["max_concurrent_jobs"])
    concurrent = in_flight_jobs(state, exclude_job=job_id)
    if max_concurrent > 0 and concurrent >= max_concurrent:
        return BudgetDecision(
            allowed=False, reserved_tokens=0, limit="max_concurrent_jobs",
            downgrade=DRAFT, breaker=breaker["status"],
            reason=(f"{concurrent} job(s) already in flight; the concurrency cap is "
                    f"{max_concurrent}"),
        )

    checks = (
        ("per_pr_tokens", spent_for_pr(state, repo, number),
         f"PR {repo}#{number}"),
        ("per_repo_daily_tokens", spent_for_repo(state, repo),
         f"repo {repo} in the last 24h"),
    )
    headroom: dict[str, int] = {}
    for key, already, subject in checks:
        cap = int(resolved[key])
        if cap <= 0:
            continue
        headroom[key] = max(0, cap - already)
        if already + tokens > cap:
            return BudgetDecision(
                allowed=False, reserved_tokens=0, limit=key, downgrade=DRAFT,
                breaker=breaker["status"], headroom=headroom,
                reason=(f"reserving {tokens} tokens for {subject} would take spend to "
                        f"{already + tokens}, past the {key} budget of {cap}"),
            )

    record_reservation(state, job_id=job_id, repo=repo, number=number, tokens=tokens)
    return BudgetDecision(
        allowed=True, reserved_tokens=tokens, breaker=breaker["status"],
        headroom=headroom, reason="within budget",
    )
