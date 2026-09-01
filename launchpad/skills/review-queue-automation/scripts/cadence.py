#!/usr/bin/env python3
"""Adaptive sweep cadence. The scheduler's decision, and nowhere else.

WHY THIS MODULE EXISTS. `poll.active_seconds`, `poll.idle_seconds` and
`poll.rest_remaining_floor` have been in the config schema since onboarding was
written, and `OPERATORS.md` calls them "scheduler cadence hints" — but no
scheduler existed, so `active_seconds` and `idle_seconds` were read by nothing.
Work was only ever discovered when an operator ran `sweep` by hand.

The cadence itself is not new thinking: it is the one the bash watcher this
skill replaces ran against these repositories for real, ported unchanged in
shape and made configurable.

  - REST budget below the floor  -> back off to the longest idle interval.
  - Work pending                 -> the active interval, and reset the streak.
  - Nothing pending              -> lengthen the interval one step per empty
                                    sweep, to the longest.

TIMER, NOT DAEMON. `decide` returns a delay and the caller persists
`next_run_at`; a short-lived timer job then checks whether it is due. A
long-running loop would hold the state-directory runtime lock between sweeps —
the invariant `0b8e64732` added is one worker per state directory — and would
need supervision to survive a crash or a laptop sleeping. A timer job holds the
lock only while it works, and a missed interval costs one cycle.

An UNKNOWN REST budget is treated as below the floor when a floor is configured.
The alternative is sweeping on the assumption that budget we could not read is
budget we have.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

from common import State, utcnow

#: Used when `poll` omits them. Same values `config.onboarding_defaults` writes.
DEFAULT_ACTIVE_SECONDS = 300
DEFAULT_IDLE_SECONDS = (600, 1200, 1800)

RATE_LIMIT_FLOOR = "rate_limit_floor"
WORK_PENDING = "work_pending"
IDLE_BACKOFF = "idle_backoff"


@dataclass(frozen=True)
class Decision:
    """How long until the next sweep, and why."""

    delay_seconds: int
    idle_streak: int
    reason: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "delay_seconds": self.delay_seconds,
            "idle_streak": self.idle_streak,
            "reason": self.reason,
        }


def _intervals(poll_cfg: dict[str, Any] | None) -> tuple[int, tuple[int, ...]]:
    poll = poll_cfg or {}
    try:
        active = int(poll.get("active_seconds") or DEFAULT_ACTIVE_SECONDS)
    except (TypeError, ValueError):
        active = DEFAULT_ACTIVE_SECONDS
    raw = poll.get("idle_seconds")
    idle: tuple[int, ...]
    if isinstance(raw, (list, tuple)) and raw:
        try:
            idle = tuple(int(value) for value in raw)
        except (TypeError, ValueError):
            idle = DEFAULT_IDLE_SECONDS
    else:
        idle = DEFAULT_IDLE_SECONDS
    # A non-positive interval would busy-loop the timer.
    active = max(1, active)
    idle = tuple(max(1, value) for value in idle)
    return active, idle


def decide(
    poll_cfg: dict[str, Any] | None,
    *,
    queue_count: int,
    remaining: Optional[int],
    idle_streak: int,
) -> Decision:
    """The next delay, from the same three rules the bash watcher used.

    `queue_count` is actionable work discovered by this sweep, not the size of
    the open-PR queue: a repository with ninety open pull requests and nothing to
    review is idle, and treating it as busy would poll every five minutes
    forever.

    `remaining` is the REST budget, or None when it could not be read.
    """
    active, idle = _intervals(poll_cfg)
    try:
        floor = int((poll_cfg or {}).get("rest_remaining_floor") or 0)
    except (TypeError, ValueError):
        floor = 0

    if floor > 0 and (remaining is None or remaining < floor):
        # Deliberately does NOT reset the streak: a rate-limited sweep discovered
        # nothing about whether work is waiting.
        return Decision(max(idle), idle_streak, RATE_LIMIT_FLOOR)

    if queue_count > 0:
        return Decision(active, 0, WORK_PENDING)

    streak = idle_streak + 1
    step = idle[min(streak, len(idle)) - 1]
    return Decision(step, streak, IDLE_BACKOFF)


# -- persistence --------------------------------------------------------------


def read(state: State, scope: str) -> dict[str, Any]:
    """The stored cadence row for `scope`, or a first-run default."""
    row = state.db.execute(
        "SELECT scope, idle_streak, next_run_at, last_run_at, last_reason "
        "FROM cadence WHERE scope=?",
        (scope,),
    ).fetchone()
    if row is None:
        return {
            "scope": scope,
            "idle_streak": 0,
            "next_run_at": None,
            "last_run_at": None,
            "last_reason": None,
        }
    return dict(row)


def write(
    state: State,
    scope: str,
    *,
    idle_streak: int,
    next_run_at: str,
    last_run_at: str,
    reason: str,
) -> None:
    state.db.execute(
        "INSERT INTO cadence(scope,idle_streak,next_run_at,last_run_at,last_reason,updated_at) "
        "VALUES(?,?,?,?,?,?) "
        "ON CONFLICT(scope) DO UPDATE SET idle_streak=excluded.idle_streak,"
        "next_run_at=excluded.next_run_at,last_run_at=excluded.last_run_at,"
        "last_reason=excluded.last_reason,updated_at=excluded.updated_at",
        (scope, int(idle_streak), next_run_at, last_run_at, reason, utcnow()),
    )
    state.db.commit()


def due(next_run_at: Optional[str], now: Optional[str] = None) -> bool:
    """Whether a sweep is due. A missing or unparseable schedule is due.

    Failing towards "run" is right for a scheduler: the cost of an early sweep is
    one cheap inventory read, and the cost of never running is the whole feature.
    """
    if not next_run_at:
        return True
    current = now or utcnow()
    # Both are UTC ISO-8601 with a trailing Z, so lexical order is chronological.
    # Anything that is not that shape is treated as due rather than parsed
    # loosely into a date that silently defers work.
    if len(next_run_at) != len(current) or not next_run_at.endswith("Z"):
        return True
    return current >= next_run_at


def schedule_after(delay_seconds: int, now: Optional[str] = None) -> str:
    """`now + delay` as a UTC ISO-8601 timestamp with a trailing Z."""
    import datetime as dt

    current = now or utcnow()
    try:
        base = dt.datetime.fromisoformat(current.replace("Z", "+00:00"))
    except ValueError:
        base = dt.datetime.now(dt.timezone.utc)
    return (
        (base + dt.timedelta(seconds=int(delay_seconds)))
        .astimezone(dt.timezone.utc)
        .isoformat()
        .replace("+00:00", "Z")
    )
