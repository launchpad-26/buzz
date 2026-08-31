#!/usr/bin/env python3
"""Scheduler cadence.

`poll.active_seconds` and `poll.idle_seconds` were in the config schema and read
by nothing — `OPERATORS.md` called them "scheduler cadence hints" while no
scheduler existed, so work was only discovered when someone ran `sweep` by hand.
These controls pin the three rules the bash watcher actually ran against these
repositories, and the timer semantics that replace its sleep loop.
"""

from __future__ import annotations

import pathlib
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scripts"))

import cadence  # noqa: E402
from common import State  # noqa: E402

POLL = {"active_seconds": 300, "idle_seconds": [600, 1200, 1800], "rest_remaining_floor": 200}


def _state() -> State:
    return State({"state_dir": tempfile.mkdtemp()})


# -- the three rules ----------------------------------------------------------

def test_work_pending_uses_the_active_interval_and_resets_the_streak() -> None:
    d = cadence.decide(POLL, queue_count=3, remaining=5000, idle_streak=2)
    assert d.delay_seconds == 300
    assert d.idle_streak == 0
    assert d.reason == cadence.WORK_PENDING


def test_idle_backoff_lengthens_one_step_per_empty_sweep() -> None:
    streak = 0
    seen = []
    for _ in range(5):
        d = cadence.decide(POLL, queue_count=0, remaining=5000, idle_streak=streak)
        streak = d.idle_streak
        seen.append(d.delay_seconds)
        assert d.reason == cadence.IDLE_BACKOFF
    # 600, 1200, 1800, then held at the longest — the watcher's exact ladder.
    assert seen == [600, 1200, 1800, 1800, 1800]


def test_rest_floor_backs_off_to_the_longest_interval() -> None:
    d = cadence.decide(POLL, queue_count=9, remaining=10, idle_streak=1)
    assert d.delay_seconds == 1800
    assert d.reason == cadence.RATE_LIMIT_FLOOR


def test_rate_limited_sweep_does_not_reset_the_streak() -> None:
    """It learned nothing about whether work is waiting, so it claims nothing."""
    d = cadence.decide(POLL, queue_count=0, remaining=10, idle_streak=2)
    assert d.idle_streak == 2


def test_unknown_rest_budget_counts_as_below_the_floor() -> None:
    """Sweeping on unread budget is assuming budget we could not see."""
    d = cadence.decide(POLL, queue_count=5, remaining=None, idle_streak=0)
    assert d.reason == cadence.RATE_LIMIT_FLOOR


def test_unknown_rest_budget_is_fine_when_no_floor_is_configured() -> None:
    poll = {**POLL, "rest_remaining_floor": 0}
    d = cadence.decide(poll, queue_count=5, remaining=None, idle_streak=0)
    assert d.reason == cadence.WORK_PENDING
    assert d.delay_seconds == 300


def test_missing_or_malformed_poll_config_falls_back_to_defaults() -> None:
    for poll in (None, {}, {"active_seconds": "soon", "idle_seconds": "later"}):
        d = cadence.decide(poll, queue_count=1, remaining=None, idle_streak=0)
        assert d.delay_seconds == cadence.DEFAULT_ACTIVE_SECONDS, poll


def test_non_positive_intervals_cannot_busy_loop_the_timer() -> None:
    poll = {"active_seconds": 0, "idle_seconds": [0, -5], "rest_remaining_floor": 0}
    assert cadence.decide(poll, queue_count=1, remaining=1, idle_streak=0).delay_seconds >= 1
    assert cadence.decide(poll, queue_count=0, remaining=1, idle_streak=0).delay_seconds >= 1


# -- timer semantics ----------------------------------------------------------

def test_a_first_run_is_due() -> None:
    assert cadence.due(None) is True
    assert cadence.due("") is True


def test_a_future_schedule_is_not_due_and_a_past_one_is() -> None:
    assert cadence.due("2099-01-01T00:00:00Z", now="2026-08-31T00:00:00Z") is False
    assert cadence.due("2026-01-01T00:00:00Z", now="2026-08-31T00:00:00Z") is True


def test_an_unparseable_schedule_is_due_rather_than_deferred() -> None:
    """Failing towards 'run' — never running is the worse failure for a scheduler."""
    assert cadence.due("soon", now="2026-08-31T00:00:00Z") is True
    assert cadence.due("2026-08-31 00:00:00", now="2026-08-31T00:00:00Z") is True


def test_schedule_after_adds_the_delay_in_utc() -> None:
    assert cadence.schedule_after(300, now="2026-08-31T00:00:00Z") == "2026-08-31T00:05:00Z"
    assert cadence.schedule_after(1800, now="2026-08-31T23:45:00Z") == "2026-09-01T00:15:00Z"


# -- persistence --------------------------------------------------------------

def test_cadence_survives_the_process_that_wrote_it() -> None:
    """The whole reason this is a table and not a variable: the timer exits."""
    state = _state()
    try:
        assert cadence.read(state, "o/r:incoming_review")["idle_streak"] == 0
        cadence.write(
            state, "o/r:incoming_review",
            idle_streak=2, next_run_at="2026-08-31T00:20:00Z",
            last_run_at="2026-08-31T00:00:00Z", reason=cadence.IDLE_BACKOFF,
        )
        stored = cadence.read(state, "o/r:incoming_review")
        assert stored["idle_streak"] == 2
        assert stored["next_run_at"] == "2026-08-31T00:20:00Z"
        assert stored["last_reason"] == cadence.IDLE_BACKOFF
    finally:
        state.close()


def test_scopes_do_not_share_a_schedule() -> None:
    """Two repositories, or two lanes, back off independently."""
    state = _state()
    try:
        cadence.write(
            state, "o/a:incoming_review", idle_streak=3,
            next_run_at="2099-01-01T00:00:00Z", last_run_at="x", reason="idle_backoff",
        )
        assert cadence.read(state, "o/b:incoming_review")["idle_streak"] == 0
        assert cadence.read(state, "o/a:author_triage")["next_run_at"] is None
    finally:
        state.close()


if __name__ == "__main__":
    failures = 0
    passed = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                passed += 1
            except Exception as exc:
                failures += 1
                import traceback
                traceback.print_exc()
                print(f"FAIL {name}: {exc}")
    print(f"{passed} passed, {failures} failed")
    sys.exit(1 if failures else 0)
