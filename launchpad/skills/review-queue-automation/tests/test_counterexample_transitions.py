#!/usr/bin/env python3
"""Counterexample tests for the job state machine and its persistence.

A counterexample test asserts the guard REJECTS the bad move. `assert_transition`
that never raises, or a `State.transition` that writes first and validates second,
would both pass a happy-path test while letting a job skip revalidation.

Two layers are covered deliberately:

* the pure table (`states.py`) — hardcoded illegal moves and hardcoded
  predecessor sets, so widening `TRANSITIONS` turns a test red rather than
  silently redefining what "legal" means;
* the durable applier (`common.State.transition`) — an illegal move must leave
  the row untouched, emit an error event, and raise.

Sibling ownership: `common.py` is owned by the runtime lane, so its transition
counterexamples live here rather than in `test_state_persistence.py`.
"""

from __future__ import annotations

import pathlib
import sys
import tempfile
from typing import Any

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import states as statesmod  # noqa: E402
from common import State, utcnow  # noqa: E402
from errors import JobBlockingError  # noqa: E402

# --------------------------------------------------------------------------
# 1. the transition table itself
# --------------------------------------------------------------------------

#: Moves that MUST stay illegal. Hardcoded, not derived from `TRANSITIONS`, so a
#: widened table fails here instead of redefining the property it is checked
#: against. Each entry names the safety rule it would break.
ILLEGAL_MOVES: tuple[tuple[str, str, str], ...] = (
    ("detected", "approval_action", "approving straight off detection skips every gate"),
    ("detected", "completed_auto_approved", "a job cannot complete as approved without acting"),
    ("preflight", "approval_evaluation", "evaluation without evidence or assurance"),
    ("evidence", "adjudication", "adjudicating without an assurance step"),
    ("evidence", "approval_evaluation", "evaluation without assurance"),
    ("assurance", "approval_evaluation", "evaluation must be reached via adjudication"),
    ("assurance", "approval_action", "acting without adjudication or evaluation"),
    ("adjudication", "approval_action", "acting without the approval evaluation"),
    ("adjudication", "approval_revalidation", "revalidation without an evaluation result"),
    ("approval_evaluation", "approval_action", "acting without the final revalidation"),
    ("approval_evaluation", "completed_auto_approved", "completing without acting"),
    ("would_auto_approve", "approval_action", "a shadow would-approve must revalidate first"),
    ("would_auto_approve", "completed_auto_approved", "a shadow decision never completes as approved"),
    ("human_approval_pending", "approval_action", "human assent still revalidates before acting"),
    ("human_approval_pending", "completed_auto_approved", "a human-pending job is not an auto-approval"),
    ("advisory_action", "approval_action", "advisory output never escalates itself to approval"),
    ("advisory_action", "approval_evaluation", "advisory is a descent; it does not climb back"),
    ("degraded", "approval_evaluation", "a degraded job never re-enters approval evaluation"),
    ("degraded", "approval_action", "a degraded job never acts"),
    ("degraded_draft", "approval_evaluation", "a degraded draft never enters approval"),
    ("changes_requested", "approval_action", "a blocked PR is not approvable"),
    ("changes_requested", "completed_auto_approved", "a blocked PR is not approvable"),
    ("safe_stop", "approval_revalidation", "safe stop is a sink, not a pause"),
    ("safe_stop", "evidence", "safe stop is a sink, not a pause"),
    ("held", "approval_action", "a held job acts only after a human releases it"),
    ("closed", "evidence", "a closed PR is not re-reviewed in place"),
    ("merged", "approval_action", "a merged PR is never approved afterwards"),
    ("completed_auto_approved", "approval_action", "an approval is never replayed"),
    ("completed_advisory", "approval_evaluation", "a completed job does not restart"),
    ("completed_human_declined", "approval_revalidation", "a decline is not retried into approval"),
    ("superseded", "detected", "superseded is absorbing"),
    ("superseded", "safe_stop", "superseded is absorbing"),
)

#: The ONLY states from which each guarded state may be entered. Hardcoded for
#: the same reason as `ILLEGAL_MOVES`.
EXCLUSIVE_PREDECESSORS: dict[str, frozenset[str]] = {
    "approval_action": frozenset({"approval_revalidation"}),
    "completed_auto_approved": frozenset({"approval_action"}),
    "approval_revalidation": frozenset(
        {"approval_evaluation", "would_auto_approve", "human_approval_pending", "human_required"}
    ),
    "would_auto_approve": frozenset({"approval_evaluation"}),
    "approval_evaluation": frozenset({"adjudication", "action"}),
    "completed_human_declined": frozenset({"human_approval_pending"}),
}


def _predecessors(target: str) -> frozenset[str]:
    return frozenset(
        source for source, targets in statesmod.TRANSITIONS.items() if target in targets
    )


def test_the_control_transitions_are_legal() -> None:
    """Not a counterexample — the control. A table that rejects everything would
    satisfy every test below while running no job at all."""
    for source, target in (
        ("detected", "preflight"),
        ("preflight", "evidence"),
        ("evidence", "assurance"),
        ("assurance", "adjudication"),
        ("adjudication", "approval_evaluation"),
        ("approval_evaluation", "approval_revalidation"),
        ("approval_revalidation", "approval_action"),
        ("approval_action", "completed_auto_approved"),
    ):
        assert statesmod.can_transition(source, target), (source, target)
        statesmod.assert_transition(source, target)


def test_every_hardcoded_illegal_move_is_rejected() -> None:
    for source, target, why in ILLEGAL_MOVES:
        assert source in statesmod.ALL_STATES, source
        assert target in statesmod.ALL_STATES, target
        assert not statesmod.can_transition(source, target), f"{source} -> {target}: {why}"
        try:
            statesmod.assert_transition(source, target)
        except JobBlockingError as exc:
            assert source in str(exc) and target in str(exc)
        else:  # pragma: no cover - the assertion below reports it
            raise AssertionError(f"{source} -> {target} must raise: {why}")


def test_every_undeclared_move_in_the_whole_cross_product_is_rejected() -> None:
    """Exhaustive over states x states. Catches a `can_transition` that answers
    True without consulting the table at all."""
    rejected = 0
    for source in sorted(statesmod.ALL_STATES):
        for target in sorted(statesmod.ALL_STATES):
            if target in statesmod.TRANSITIONS[source]:
                continue
            assert not statesmod.can_transition(source, target), (source, target)
            rejected += 1
    # A table that declared every edge legal would leave nothing to reject.
    assert rejected > len(statesmod.ALL_STATES), rejected


def test_a_state_never_transitions_to_itself() -> None:
    """Re-entering the same state is not progress; it would let a job loop inside
    a phase forever while still passing every per-edge check."""
    for source in sorted(statesmod.ALL_STATES):
        assert source not in statesmod.TRANSITIONS[source], source


def test_guarded_states_have_exactly_their_declared_predecessors() -> None:
    for target, expected in EXCLUSIVE_PREDECESSORS.items():
        assert _predecessors(target) == expected, (
            f"{target} is now reachable from {sorted(_predecessors(target))}, "
            f"expected exactly {sorted(expected)}"
        )


def test_terminal_states_lead_only_to_superseded() -> None:
    for terminal in (
        "completed",
        "completed_auto_approved",
        "completed_advisory",
        "completed_human_declined",
        "safe_stop",
        "closed",
        "merged",
    ):
        assert statesmod.TRANSITIONS[terminal] == frozenset({"superseded"}), terminal
    assert statesmod.TRANSITIONS["superseded"] == frozenset()


def test_an_unknown_state_name_is_never_a_legal_target_or_source() -> None:
    for bogus in ("", "APPROVAL_ACTION", "approved", "approval action", "done", None):
        assert not statesmod.can_transition("approval_revalidation", bogus)  # type: ignore[arg-type]
        assert not statesmod.can_transition(bogus, "safe_stop")  # type: ignore[arg-type]


def test_a_new_job_may_only_start_at_detected() -> None:
    assert statesmod.can_transition(None, "detected")
    for target in sorted(statesmod.ALL_STATES - {"detected"}):
        assert not statesmod.can_transition(None, target), target


# --------------------------------------------------------------------------
# 2. the durable applier
# --------------------------------------------------------------------------


class _RecordingLogger:
    """Captures the events `State.transition` emits, so a test can assert that an
    illegal move produced an ERROR and never a success transition event."""

    def __init__(self) -> None:
        self.errors: list[dict[str, Any]] = []
        self.transitions: list[tuple[str | None, str]] = []

    def error(self, **kwargs: Any) -> None:
        self.errors.append(kwargs)

    def transition(self, prior: str | None, next_: str, **kwargs: Any) -> None:
        self.transitions.append((prior, next_))


def _state() -> State:
    return State({"state_dir": tempfile.mkdtemp()})


_SEEDED = [0]


def _seed_job(state: State, job_id: str, status: str) -> None:
    """One row per call. The `jobs` table is unique on (repo, number, head_sha,
    lane), so each seeded job gets its own PR number."""
    now = utcnow()
    _SEEDED[0] += 1
    state.execute(
        "INSERT INTO jobs(id,repo,number,head_sha,lane,status,artifact_dir,retries,"
        "created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?)",
        (job_id, "o/r", _SEEDED[0], "a" * 40, "incoming", status,
         str(state.job_dir(job_id)), 0, now, now),
    )
    state.db.commit()


def test_a_legal_transition_is_applied_and_logged() -> None:
    """The control for the applier: without it, a `transition` that raised on
    everything would pass every counterexample below."""
    state = _state()
    logger = _RecordingLogger()
    _seed_job(state, "j-ok", "approval_revalidation")
    prior, target = state.transition("j-ok", "approval_action", logger=logger)
    assert (prior, target) == ("approval_revalidation", "approval_action")
    assert state.current_status("j-ok") == "approval_action"
    assert logger.transitions == [("approval_revalidation", "approval_action")]
    assert logger.errors == []
    state.close()


def test_an_illegal_transition_leaves_the_row_untouched_and_errors() -> None:
    state = _state()
    for source, target, why in ILLEGAL_MOVES:
        job_id = f"j-{source}-{target}"
        _seed_job(state, job_id, source)
        logger = _RecordingLogger()
        try:
            state.transition(job_id, target, logger=logger)
        except JobBlockingError:
            pass
        else:  # pragma: no cover
            raise AssertionError(f"{source} -> {target} was applied: {why}")
        assert state.current_status(job_id) == source, (source, target)
        assert logger.transitions == [], (source, target)
        assert len(logger.errors) == 1, (source, target)
        event = logger.errors[0]
        assert event["outcome"] == "transition_rejected"
        assert event["attributes"]["job.prior_status"] == source
        assert event["attributes"]["job.status"] == target
    state.close()


def test_a_transition_on_a_nonexistent_job_writes_nothing_and_emits_no_event() -> None:
    """A missing row must be refused BEFORE any write or event. An applier that
    inserted-or-updated would create a job in an arbitrary state."""
    state = _state()
    logger = _RecordingLogger()
    try:
        state.transition("no-such-job", "detected", logger=logger)
    except JobBlockingError as exc:
        assert "nonexistent" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("a transition on a nonexistent job must raise")
    assert state.current_status("no-such-job") is None
    assert state.db.execute("SELECT COUNT(*) AS n FROM jobs").fetchone()["n"] == 0
    assert logger.transitions == []
    assert logger.errors == []
    state.close()


def test_an_illegal_transition_raises_even_with_no_logger_attached() -> None:
    """The rejection is the guard; the event is only its record. A transition that
    only refused when someone was watching would be no guard at all."""
    state = _state()
    _seed_job(state, "j-silent", "detected")
    try:
        state.transition("j-silent", "approval_action")
    except JobBlockingError:
        pass
    else:  # pragma: no cover
        raise AssertionError("an illegal transition must raise without a logger")
    assert state.current_status("j-silent") == "detected"
    state.close()


def test_a_rejected_transition_does_not_consume_the_reason_of_the_next_one() -> None:
    """A rejected move must not leave a half-applied row: the following legal move
    still records its own reason, not the refused one."""
    state = _state()
    _seed_job(state, "j-seq", "approval_evaluation")
    try:
        state.transition("j-seq", "approval_action", reason="refused")
    except JobBlockingError:
        pass
    row = state.db.execute("SELECT status, reason FROM jobs WHERE id=?", ("j-seq",)).fetchone()
    assert row["status"] == "approval_evaluation"
    assert row["reason"] is None
    state.transition("j-seq", "approval_revalidation", reason="accepted")
    row = state.db.execute("SELECT status, reason FROM jobs WHERE id=?", ("j-seq",)).fetchone()
    assert (row["status"], row["reason"]) == ("approval_revalidation", "accepted")
    state.close()
