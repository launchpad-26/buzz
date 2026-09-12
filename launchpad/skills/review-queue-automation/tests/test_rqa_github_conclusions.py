#!/usr/bin/env python3
"""U-VERDICT-06's canonical vocabulary and total normalisation —
`code/P-09-github-adapter.md` §2, §8 row T6; `CONTRACTS.md` §4.
"""

from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from rqa.contracts import FAILING, PASSING, UNSETTLED, CheckConclusion  # noqa: E402
from rqa.github.conclusions import normalise_conclusion, normalise_status  # noqa: E402

_NAMED_CONCLUSIONS = {
    "success": CheckConclusion.SUCCESS,
    "failure": CheckConclusion.FAILURE,
    "neutral": CheckConclusion.NEUTRAL,
    "cancelled": CheckConclusion.CANCELLED,
    "skipped": CheckConclusion.SKIPPED,
    "timed_out": CheckConclusion.TIMED_OUT,
    "action_required": CheckConclusion.ACTION_REQUIRED,
    "pending": CheckConclusion.PENDING,
}

_LEGACY_STATUSES = {
    "success": CheckConclusion.SUCCESS,
    "failure": CheckConclusion.FAILURE,
    "pending": CheckConclusion.PENDING,
    "expected": CheckConclusion.PENDING,
    # `error` has no member of its own: the unknown rule keeps it failing.
    "error": CheckConclusion.ACTION_REQUIRED,
}


def test_t6_every_named_conclusion_normalises_to_its_member() -> None:
    for value, expected in _NAMED_CONCLUSIONS.items():
        assert normalise_conclusion(value) is expected, value
        assert normalise_conclusion(value.upper()) is expected, value
        assert normalise_conclusion(f"  {value} ") is expected, value


def test_t6_unknown_conclusions_normalise_to_action_required() -> None:
    for value in ("stale", "startup_failure", "mystery", "ERRORED", 42, object()):
        assert normalise_conclusion(value) is CheckConclusion.ACTION_REQUIRED, value


def test_t6_absent_conclusion_is_pending() -> None:
    assert normalise_conclusion(None) is CheckConclusion.PENDING
    assert normalise_conclusion("") is CheckConclusion.PENDING
    assert normalise_conclusion("   ") is CheckConclusion.PENDING


def test_t6_every_legacy_status_normalises_to_exactly_one_member() -> None:
    for value, expected in _LEGACY_STATUSES.items():
        assert normalise_status(value) is expected, value
        assert normalise_status(value.upper()) is expected, value
    assert normalise_status(None) is CheckConclusion.PENDING
    assert normalise_status("weird") is CheckConclusion.ACTION_REQUIRED


def test_t6_normalisation_is_total_never_an_exception() -> None:
    class Odd:
        def __str__(self):
            return "odd"

    for value in (None, "", 0, 1.5, [], {}, Odd(), b"success"):
        assert isinstance(normalise_conclusion(value), CheckConclusion)
        assert isinstance(normalise_status(value), CheckConclusion)


def test_t6_the_three_sets_are_the_contract_sets() -> None:
    assert FAILING == frozenset(
        {CheckConclusion.FAILURE, CheckConclusion.TIMED_OUT, CheckConclusion.ACTION_REQUIRED}
    )
    assert UNSETTLED == frozenset({CheckConclusion.PENDING})
    assert PASSING == frozenset(
        {
            CheckConclusion.SUCCESS,
            CheckConclusion.NEUTRAL,
            CheckConclusion.SKIPPED,
            CheckConclusion.CANCELLED,
        }
    )


def test_t6_the_three_sets_are_disjoint_and_exhaustive() -> None:
    assert FAILING & UNSETTLED == frozenset()
    assert FAILING & PASSING == frozenset()
    assert UNSETTLED & PASSING == frozenset()
    assert FAILING | UNSETTLED | PASSING == frozenset(CheckConclusion)


def test_t6_pending_never_corroborates_or_blocks() -> None:
    assert CheckConclusion.PENDING not in FAILING
    assert CheckConclusion.PENDING not in PASSING
    assert CheckConclusion.PENDING in UNSETTLED


def test_the_vocabulary_is_the_contracts_declaration_not_a_copy() -> None:
    import rqa.contracts as contracts
    import rqa.github as github
    import rqa.github.conclusions as conclusions

    assert conclusions.CheckConclusion is contracts.CheckConclusion
    assert conclusions.FAILING is contracts.FAILING
    assert github.CheckConclusion is contracts.CheckConclusion
    assert github.PASSING is contracts.PASSING
