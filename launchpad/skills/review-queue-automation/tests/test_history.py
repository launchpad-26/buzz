#!/usr/bin/env python3
"""Tests for history.py — closed-PR ingestion for shadow calibration.

The critical property is that the outcome label is INDEPENDENT of the evaluator
being calibrated, and conservative: absence of objection is never treated as
approval. Also guards the hindsight rule — no evidence timestamp after the
cutoff may be counted.
"""

from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scripts"))

from history import (  # noqa: E402
    ADVERSE,
    CLEAN,
    CONTESTED,
    UNKNOWN,
    _reverted_numbers,
    _timestamps,
    build_entry,
    checks_ok_timestamp,
    classify_outcome,
)

MERGED = "2026-08-01T12:00:00Z"


def _pr(**over) -> dict:
    pr = {
        "number": 10,
        "title": "fix: a thing",
        "head": {"sha": "abc123"},
        "user": {"login": "alice"},
        "created_at": "2026-07-30T09:00:00Z",
        "updated_at": "2026-08-01T12:00:05Z",  # AFTER merge, as GitHub does
        "merged_at": MERGED,
        "closed_at": MERGED,
        "additions": 12,
    }
    pr.update(over)
    return pr


def _review(state, login="bob", at="2026-07-31T10:00:00Z") -> dict:
    return {"state": state, "user": {"login": login}, "submitted_at": at}


# -- outcome independence ------------------------------------------------
def test_changes_requested_is_contested() -> None:
    outcome, source = classify_outcome(_pr(), [_review("CHANGES_REQUESTED")], reverted=set())
    assert outcome == CONTESTED
    assert "requested changes" in source


def test_approved_and_merged_is_clean() -> None:
    outcome, source = classify_outcome(_pr(), [_review("APPROVED")], reverted=set())
    assert outcome == CLEAN
    assert "approval" in source


def test_merged_with_no_review_is_unknown_not_clean() -> None:
    """Absence of objection is not approval; calling it clean would inflate accuracy."""
    outcome, source = classify_outcome(_pr(), [], reverted=set())
    assert outcome == UNKNOWN
    assert "no human review" in source


def test_commented_and_merged_is_clean() -> None:
    outcome, _ = classify_outcome(_pr(), [_review("COMMENTED")], reverted=set())
    assert outcome == CLEAN


def test_reverted_pr_is_adverse_even_if_approved() -> None:
    outcome, source = classify_outcome(
        _pr(number=10), [_review("APPROVED")], reverted={10}
    )
    assert outcome == ADVERSE
    assert "revert" in source


def test_closed_unmerged_after_review_is_adverse() -> None:
    pr = _pr(merged_at=None, closed_at="2026-08-01T12:00:00Z")
    outcome, _ = classify_outcome(pr, [_review("COMMENTED")], reverted=set())
    assert outcome == ADVERSE


def test_closed_unmerged_without_review_is_unknown() -> None:
    pr = _pr(merged_at=None, closed_at="2026-08-01T12:00:00Z")
    outcome, _ = classify_outcome(pr, [], reverted=set())
    assert outcome == UNKNOWN


def test_the_automations_own_reviews_do_not_count_as_human() -> None:
    """Otherwise the evaluator would be grading its own homework."""
    outcome, _ = classify_outcome(
        _pr(), [_review("APPROVED", login="rqa-bot")], reverted=set(),
        self_login="rqa-bot",
    )
    assert outcome == UNKNOWN


def test_changes_requested_by_the_automation_is_not_contested() -> None:
    outcome, _ = classify_outcome(
        _pr(), [_review("CHANGES_REQUESTED", login="rqa-bot")], reverted=set(),
        self_login="rqa-bot",
    )
    assert outcome == UNKNOWN


# -- revert detection ----------------------------------------------------
def test_revert_titles_are_detected() -> None:
    closed = [
        {"number": 20, "title": 'Revert "fix: a thing" (#10)'},
        {"number": 21, "title": "revert #11 and #12"},
        {"number": 22, "title": "feat: unrelated (#13)"},
    ]
    assert _reverted_numbers(closed) == {10, 11, 12}


def test_non_revert_titles_naming_numbers_are_ignored() -> None:
    assert _reverted_numbers([{"number": 1, "title": "fix: follow up to #99"}]) == set()


# -- hindsight rule ------------------------------------------------------
def test_post_cutoff_updated_at_is_never_used_as_evidence() -> None:
    """Merging bumps updated_at; using it would make every sample look fresh."""
    stamps = _timestamps(_pr(), [])
    assert stamps["cutoff"] == MERGED
    assert stamps["evidence_at"] is not None
    assert stamps["evidence_at"] <= MERGED
    assert stamps["evidence_at"] != "2026-08-01T12:00:05Z"


def test_evidence_at_takes_the_latest_provable_pre_cutoff_signal() -> None:
    stamps = _timestamps(
        _pr(), [_review("APPROVED", at="2026-07-31T23:00:00Z")],
        checks_ok_at="2026-07-31T22:00:00Z",
    )
    assert stamps["evidence_at"] == "2026-07-31T23:00:00Z"


def test_future_review_is_not_counted() -> None:
    stamps = _timestamps(_pr(), [_review("APPROVED", at="2026-09-01T00:00:00Z")])
    assert stamps["adjudication_at"] is None
    # falls back to creation, which does predate the cutoff
    assert stamps["evidence_at"] == "2026-07-30T09:00:00Z"


def test_no_cutoff_means_no_evidence() -> None:
    stamps = _timestamps(_pr(merged_at=None, closed_at=None), [_review("APPROVED")])
    assert stamps["cutoff"] == ""
    assert stamps["evidence_at"] is None
    assert stamps["adjudication_at"] is None


# -- check evidence ------------------------------------------------------
def test_all_successful_checks_yield_latest_completion() -> None:
    checks = [
        {"status": "completed", "conclusion": "SUCCESS", "completed_at": "2026-07-31T10:00:00Z"},
        {"status": "completed", "conclusion": "SUCCESS", "completed_at": "2026-07-31T11:00:00Z"},
    ]
    assert checks_ok_timestamp(checks) == "2026-07-31T11:00:00Z"


def test_any_failure_makes_checks_fail_closed() -> None:
    checks = [
        {"status": "completed", "conclusion": "SUCCESS", "completed_at": "2026-07-31T10:00:00Z"},
        {"status": "completed", "conclusion": "FAILURE", "completed_at": "2026-07-31T11:00:00Z"},
    ]
    assert checks_ok_timestamp(checks) is None


def test_incomplete_check_fails_closed() -> None:
    assert checks_ok_timestamp([{"status": "in_progress", "conclusion": None}]) is None


def test_missing_completion_time_fails_closed() -> None:
    assert checks_ok_timestamp(
        [{"status": "completed", "conclusion": "SUCCESS", "completed_at": ""}]
    ) is None


def test_no_checks_is_not_green() -> None:
    assert checks_ok_timestamp([]) is None


def test_neutral_and_skipped_count_as_not_failing() -> None:
    checks = [
        {"status": "completed", "conclusion": "NEUTRAL", "completed_at": "2026-07-31T10:00:00Z"},
        {"status": "completed", "conclusion": "SKIPPED", "completed_at": "2026-07-31T09:00:00Z"},
    ]
    assert checks_ok_timestamp(checks) == "2026-07-31T10:00:00Z"


# -- entry shape ---------------------------------------------------------
def test_entry_is_shadow_build_sample_compatible() -> None:
    from shadow import build_sample

    entry = build_entry(
        "o/r", _pr(), [_review("APPROVED")], ["src/a.py"],
        reverted=set(), checks_ok_at="2026-07-31T11:00:00Z",
    )
    sample = build_sample(entry)
    assert sample.repo == "o/r"
    assert sample.number == 10
    assert sample.head_sha == "abc123"
    assert sample.outcome_label() == CLEAN
    assert sample.cutoff == MERGED

    facts = sample.before_merge_facts()
    assert facts.checks_ok is True
    assert facts.adjudication_complete is True
    assert facts.evidence_fresh is True
    assert facts.files == ["src/a.py"]
    assert facts.author_login == "alice"


def test_entry_without_check_evidence_stays_fail_closed() -> None:
    from shadow import build_sample

    entry = build_entry("o/r", _pr(), [_review("APPROVED")], [], reverted=set())
    facts = build_sample(entry).before_merge_facts()
    assert facts.checks_ok is False, "absent check evidence must not read as green"
