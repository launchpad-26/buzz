#!/usr/bin/env python3
"""§2's closed transition table and six-disposition mapping — `code/P-02-lifecycle.md` §2,
§7 and §8 T20's totality half.

No pytest: every `test_*` function here takes no arguments, per `tests/run_all.py`.

The table is asserted **literally**, row by row, against §2's text rather than by a
property that several different tables would satisfy. That is deliberate: §2 is a
verbatim contract, and "the same review reaches the same disposition the same way"
(RQA-BR-001) is a claim about *this* table. A test that only checked shape would pass on
a table with an extra edge from `judged` to `approved` — exactly the kind of edit this
part exists to make impossible.
"""

from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from rqa.contracts import JobStatus  # noqa: E402
from rqa.lifecycle import DISPOSITION, TRANSITIONS, Disposition, LifecycleError  # noqa: E402
from rqa.lifecycle.states import as_status  # noqa: E402

S = JobStatus

#: §2, verbatim.
EXPECTED_TRANSITIONS = {
    S.QUEUED: {S.CLAIMED, S.ESCALATED, S.SUPERSEDED},
    S.CLAIMED: {S.PLANNED, S.ESCALATED, S.STOPPED, S.SUPERSEDED},
    S.PLANNED: {S.REVIEWING, S.JUDGED, S.ESCALATED, S.STOPPED},
    S.REVIEWING: {S.JUDGED, S.ESCALATED, S.STOPPED},
    S.JUDGED: {S.REMEDIATING, S.ESCALATED, S.SUBMITTING, S.STOPPED},
    S.REMEDIATING: {S.SUPERSEDED, S.ESCALATED, S.STOPPED},
    S.ESCALATED: {S.JUDGED, S.APPROVED, S.CHANGES_REQUESTED, S.STOPPED, S.SUPERSEDED},
    S.SUBMITTING: {S.CHANGES_REQUESTED, S.APPROVED, S.ESCALATED, S.STOPPED},
    S.CHANGES_REQUESTED: {S.SUPERSEDED},
    S.APPROVED: {S.MERGED, S.SUPERSEDED},
    S.MERGED: set(),
    S.STOPPED: {S.CLAIMED, S.SUPERSEDED},
    S.SUPERSEDED: set(),
}

#: §2, verbatim. No `SUPERSEDED` row: §3.4 step 4 proves `status()` cannot observe one.
EXPECTED_DISPOSITION = {
    S.QUEUED: Disposition.BEING_REVIEWED,
    S.CLAIMED: Disposition.BEING_REVIEWED,
    S.PLANNED: Disposition.BEING_REVIEWED,
    S.REVIEWING: Disposition.BEING_REVIEWED,
    S.JUDGED: Disposition.BEING_REVIEWED,
    S.SUBMITTING: Disposition.BEING_REVIEWED,
    S.REMEDIATING: Disposition.AWAITING_REMEDIATION,
    S.ESCALATED: Disposition.AWAITING_HUMAN_JUDGEMENT,
    S.CHANGES_REQUESTED: Disposition.BLOCKED,
    S.APPROVED: Disposition.REVIEW_COMPLETE,
    S.MERGED: Disposition.REVIEW_COMPLETE,
    S.STOPPED: Disposition.UNABLE_TO_PROGRESS,
}

#: RQA-FR-016's six answers, as `flow-review-lifecycle.md` and `architecture.md` word them.
FR016 = {
    "being reviewed",
    "blocked",
    "awaiting remediation",
    "awaiting human judgement",
    "review-complete",
    "unable to progress",
}


# -- the table -----------------------------------------------------------------


def test_the_transition_table_is_section_twos_verbatim() -> None:
    assert {status: set(targets) for status, targets in TRANSITIONS.items()} == (
        EXPECTED_TRANSITIONS
    )


def test_the_table_is_total_over_every_job_status() -> None:
    """A status with no row would make `TRANSITIONS[job.status]` a `KeyError` — an
    unnamed branch in the one function that decides whether a change of state is legal."""
    assert set(TRANSITIONS) == set(JobStatus)
    assert len(set(JobStatus)) == 13


def test_the_table_is_closed_over_the_status_set() -> None:
    """§2: "a transition not in it does not happen". Every target is itself a status with
    a row, so no edge leaves the machine."""
    for status, targets in TRANSITIONS.items():
        for target in targets:
            assert isinstance(target, JobStatus), (status, target)
            assert target in TRANSITIONS, (status, target)


def test_no_status_transitions_to_itself() -> None:
    """A self-edge would let `transition()` append a second entry for a state the job is
    already in, and `status()` would report a reason for a change that never happened."""
    for status, targets in TRANSITIONS.items():
        assert status not in targets, status


def test_merged_and_superseded_are_terminal() -> None:
    assert TRANSITIONS[S.MERGED] == frozenset()
    assert TRANSITIONS[S.SUPERSEDED] == frozenset()


def test_a_stopped_job_can_only_restart_or_be_superseded() -> None:
    """§7: "`stopped`'s only legal forward edge is to `claimed`, so a retry always
    restarts from plan-and-carry-over, never from mid-cascade"."""
    assert TRANSITIONS[S.STOPPED] == frozenset({S.CLAIMED, S.SUPERSEDED})


def test_approved_is_reachable_only_from_escalated_or_submitting() -> None:
    """§9, RQA-FR-028: `submitting`'s forward edges are the only automated path to a
    verdict, and 12b (`escalated`) is the only human one. A refusal, a denial or an
    unavailability reaching `approved` would need a third."""
    sources = {status for status, targets in TRANSITIONS.items() if S.APPROVED in targets}
    assert sources == {S.ESCALATED, S.SUBMITTING}


def test_the_table_cannot_be_edited_at_runtime() -> None:
    """A closed table a caller can mutate is closed by convention only, and one
    assignment would disable the guard that keeps a refusal off the approved path for
    every job in the process."""
    for mapping in (TRANSITIONS, DISPOSITION):
        try:
            mapping[S.MERGED] = frozenset({S.APPROVED})
        except TypeError:
            pass
        else:  # pragma: no cover - the raise below is the failure report
            raise AssertionError(f"{mapping} accepted an assignment")


# -- the dispositions ----------------------------------------------------------


def test_the_disposition_map_is_section_twos_verbatim() -> None:
    assert dict(DISPOSITION) == EXPECTED_DISPOSITION


def test_the_six_dispositions_are_fr016s_six_answers() -> None:
    assert {member.value for member in Disposition} == FR016


def test_disposition_is_total_over_every_status_status_can_return() -> None:
    """§8 T20 and RQA-FR-016's fit criterion: "not merely one of the six legal values" —
    there is no status this part can reach that `DISPOSITION` does not cover. `SUPERSEDED`
    is the one exclusion, and §3.4 step 4 proves `status()` cannot observe it."""
    assert set(DISPOSITION) == set(JobStatus) - {S.SUPERSEDED}
    assert all(isinstance(value, Disposition) for value in DISPOSITION.values())


def test_every_disposition_is_reachable_from_a_queued_job() -> None:
    """RQA-FR-016 asks for six answers; a mapping whose value is unreachable would be a
    seventh state of the system, not an answer. Walked over the table, from arrival."""
    seen = {S.QUEUED}
    frontier = [S.QUEUED]
    while frontier:
        for target in TRANSITIONS[frontier.pop()]:
            if target not in seen:
                seen.add(target)
                frontier.append(target)
    reachable = {DISPOSITION[status] for status in seen if status in DISPOSITION}
    assert reachable == set(Disposition)


# -- the value guard both of them depend on ------------------------------------


def test_as_status_names_a_value_that_is_not_a_status() -> None:
    """`jobs.status` is a TEXT column, so a row can carry anything. A raw `KeyError` from
    the table lookup would be an unnamed branch in the legality check."""
    assert as_status("queued") is S.QUEUED
    assert as_status(S.MERGED) is S.MERGED
    try:
        as_status("approved_by_me", what="jobs.status")
    except LifecycleError as exc:
        assert "jobs.status" in str(exc) and "approved_by_me" in str(exc)
    else:  # pragma: no cover - the raise below is the failure report
        raise AssertionError("an unknown status string was accepted")
