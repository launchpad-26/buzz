#!/usr/bin/env python3
"""Tests for bounded markdown-fence normalisation in verdict parsing.

Several models reliably wrap an otherwise-correct verdict in a ```json fence.
Stripping a fence that wraps the WHOLE payload is a formatting normalisation.
It must NOT become a licence to dig JSON out of prose: the anti-prose rule
(a signal token only counts as a real parsed JSON field) stays enforced.
"""

from __future__ import annotations

import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scripts"))

from verdict import (  # noqa: E402
    signal_from_verdict,
    strip_code_fence,
    validate_verdict,
)

CLEAN = {
    "signal": "SUPPORTED",
    "recommendation": "clean",
    "summary": "Comment typo only; no defects.",
    "findings": [],
    "good": ["Isolated to comment text"],
    "missing_evidence": [],
}


def _body() -> str:
    return json.dumps(CLEAN)


# -- accepted: fence wraps the entire payload ---------------------------
def test_bare_json_is_unchanged() -> None:
    assert strip_code_fence(_body()) == _body()


def test_json_tagged_fence_is_stripped() -> None:
    wrapped = f"```json\n{_body()}\n```"
    assert json.loads(strip_code_fence(wrapped)) == CLEAN


def test_untagged_fence_is_stripped() -> None:
    wrapped = f"```\n{_body()}\n```"
    assert json.loads(strip_code_fence(wrapped)) == CLEAN


def test_fence_with_surrounding_whitespace_is_stripped() -> None:
    wrapped = f"\n\n  ```json\n{_body()}\n```  \n\n"
    assert json.loads(strip_code_fence(wrapped)) == CLEAN


def test_fenced_verdict_validates_and_yields_signal() -> None:
    wrapped = f"```json\n{_body()}\n```"
    ok, issues = validate_verdict(wrapped)
    assert ok, issues
    assert signal_from_verdict(wrapped) == "SUPPORTED"


def test_real_anthropic_shape_is_accepted() -> None:
    """The exact shape observed from Anthropic: pretty-printed inside a fence."""
    wrapped = "```json\n" + json.dumps(CLEAN, indent=2) + "\n```"
    ok, issues = validate_verdict(wrapped)
    assert ok, issues
    assert signal_from_verdict(wrapped) == "SUPPORTED"


# -- rejected: anything outside the fence ------------------------------
def test_prose_before_fence_is_not_stripped() -> None:
    text = f"Here is my review:\n```json\n{_body()}\n```"
    # Strip is a no-op, so the payload stays unparseable and the signal is refused.
    assert strip_code_fence(text) != _body()
    assert signal_from_verdict(text) == ""
    ok, _ = validate_verdict(text)
    assert not ok


def test_prose_after_fence_is_not_stripped() -> None:
    text = f"```json\n{_body()}\n```\nHope that helps!"
    assert signal_from_verdict(text) == ""
    ok, _ = validate_verdict(text)
    assert not ok


def test_signal_token_in_prose_still_refused() -> None:
    """The core anti-prose rule must survive this change."""
    for text in (
        "The signal is SUPPORTED and the patch is clean.",
        "```\nsignal: SUPPORTED\n```",
        f"SUPPORTED\n```json\n{_body()}\n```",
    ):
        assert signal_from_verdict(text) == "", text


def test_two_fences_are_not_merged() -> None:
    text = f"```json\n{_body()}\n```\n```json\n{_body()}\n```"
    assert signal_from_verdict(text) == ""


def test_unclosed_fence_is_refused() -> None:
    assert signal_from_verdict(f"```json\n{_body()}") == ""


def test_empty_and_none_are_safe() -> None:
    assert strip_code_fence("") == ""
    assert strip_code_fence(None) == ""  # type: ignore[arg-type]
    assert signal_from_verdict("") == ""


def test_fence_cannot_rescue_an_invalid_verdict() -> None:
    """Normalising the wrapper must not soften schema validation."""
    bad = dict(CLEAN)
    bad["signal"] = "SUPPORTED"
    bad["findings"] = [{"severity": "high", "title": "t", "location": "a.py:1",
                        "evidence": "e", "primary_source": "s"}]
    wrapped = "```json\n" + json.dumps(bad) + "\n```"
    ok, issues = validate_verdict(wrapped)
    assert not ok, "SUPPORTED with findings is contradictory and must stay rejected"
    assert issues
