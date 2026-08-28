#!/usr/bin/env python3
"""Error classification + validated state transition tests."""

from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scripts"))

from errors import (  # noqa: E402
    CANDIDATE_TERMINAL,
    JOB_BLOCKING,
    TRANSIENT,
    classify_error,
)
from states import (  # noqa: E402
    ALL_STATES,
    TRANSITIONS,
    assert_transition,
    can_transition,
    transition_entries,
)


def test_transient_classification() -> None:
    for msg in ("connection reset by peer", "timed out", "502 Bad Gateway", "network unreachable"):
        assert classify_error(msg) == TRANSIENT, msg


def test_candidate_terminal_classification() -> None:
    for msg in ("insufficient_quota", "rate limit exceeded", "401 unauthorized", "model not found", "Invalid schema: signal"):
        assert classify_error(msg) == CANDIDATE_TERMINAL, msg


def test_job_blocking_classification() -> None:
    for msg in ("evidence.txt missing; run evidence", "invalid config: missing keys", "unknown runner: bogus", "invalid state transition: held -> action"):
        assert classify_error(msg) == JOB_BLOCKING, msg


def test_unknown_classifies_terminal() -> None:
    assert classify_error("weird random failure") == CANDIDATE_TERMINAL


def test_all_expected_states_present() -> None:
    expected = {
        "detected", "preflight", "evidence", "assurance", "adjudication",
        "approval_evaluation", "would_auto_approve", "approval_revalidation",
        "approval_action", "human_approval_pending", "advisory_action",
        "completed_auto_approved", "completed_human_declined", "completed_advisory",
        "ready_for_review", "changes_requested", "requested_changes_fixed",
        "author_triage", "closed", "merged",
        "degraded_draft", "degraded", "safe_stop", "retryable", "held",
        "human_required", "action", "completed", "superseded",
    }
    assert ALL_STATES == expected


def test_legal_transitions_flow() -> None:
    assert can_transition("detected", "evidence")
    assert can_transition("evidence", "assurance")
    assert can_transition("assurance", "adjudication")
    assert can_transition("assurance", "degraded_draft")
    assert can_transition("adjudication", "action")
    assert can_transition("action", "completed")


def test_illegal_transitions_rejected() -> None:
    assert not can_transition("detected", "completed")
    assert not can_transition("detected", "adjudication")
    assert not can_transition("human_required", "action")
    assert not can_transition("completed", "action")
    assert not can_transition("superseded", "detected")


def test_assert_transition_raises_on_illegal() -> None:
    from errors import JobBlockingError

    try:
        assert_transition("detected", "completed")
        raise AssertionError("expected JobBlockingError")
    except JobBlockingError:
        pass


def test_transition_entries_enumeration() -> None:
    entries = transition_entries()
    assert entries
    for source, target in entries:
        assert source in TRANSITIONS
        assert target in TRANSITIONS[source]


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
                print(f"FAIL {name}: {exc}")
    print(f"{passed} passed, {failures} failed")
    sys.exit(1 if failures else 0)