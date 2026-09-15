#!/usr/bin/env python3
"""`rqa/cli/render.py` — the untrusted-text neutralisation every subcommand's
output passes through before it reaches a terminal.

Every shape below is a real `rqa` type (`rqa.contracts.Escalation`,
`rqa.lifecycle.NotFound`), never a dataclass defined in this file: a
dataclass declared directly in an ad-hoc `spec_from_file_location`-loaded
test module (`tests/run_all.py`'s loader, which never registers the module
in `sys.modules`) crashes CPython 3.14's `dataclasses._is_type` — it looks
its own module up in `sys.modules` to resolve a postponed (`from __future__
import annotations`) field annotation and finds nothing there. A type
imported from the real package is already registered under its real module
name, so it never hits that lookup.
"""

from __future__ import annotations

import pathlib
import sys
from datetime import datetime, timezone
from types import MappingProxyType

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from rqa.cli.render import sanitize_text, to_jsonable  # noqa: E402
from rqa.contracts import Escalation, EscalationCause  # noqa: E402
from rqa.lifecycle import NotFound  # noqa: E402


def test_sanitize_escapes_every_control_character_and_common_escape_families() -> None:
    hostile = (
        "Fix typo\r\n\x1b[2K\x1b[ADISPOSITION: approved (all checks passed)"
        "\x00\x07\x7f\x9f"
    )
    cleaned = sanitize_text(hostile)
    assert "\r" not in cleaned
    assert "\n" not in cleaned
    assert "\x1b" not in cleaned
    assert "\x00" not in cleaned
    assert "\x07" not in cleaned
    assert "\x7f" not in cleaned
    assert "\x9f" not in cleaned
    assert "\\u000d\\u000a\\u001b" in cleaned
    assert sanitize_text("\u202e\u2028") == "\\u202e\\u2028"
    assert sanitize_text(cleaned) == cleaned
    assert "Fix typo" in cleaned
    assert "DISPOSITION: approved (all checks passed)" in cleaned


def test_sanitize_is_a_no_op_on_ordinary_text() -> None:
    ordinary = "changes_requested: missing test coverage for the new branch"
    assert sanitize_text(ordinary) == ordinary


def test_to_jsonable_walks_dataclasses_mappings_and_sequences() -> None:
    escalation = Escalation(
        id=1,
        job_id="job\x1b-1",
        cause=EscalationCause.EVIDENCE_GAP,
        question="Fix typo\r\n\x1b[2K\x1b[ADISPOSITION: approved",
        context=MappingProxyType({"pr_title\x00": "ALL\x07CLEAR"}),
        head_sha="deadbeef",
        snapshot_hash="snaphash",
        entry_seq=1,
        raised_at=datetime(2026, 9, 14, tzinfo=timezone.utc),
    )
    result = to_jsonable(escalation)
    assert result["job_id"] == "job\\u001b-1"
    assert result["cause"] == "evidence_gap"
    assert result["question"] == "Fix typo\\u000d\\u000a\\u001b[2K\\u001b[ADISPOSITION: approved"
    assert result["context"] == {"pr_title\\u0000": "ALL\\u0007CLEAR"}
    assert result["id"] == 1


def test_to_jsonable_renders_a_dataclass_with_no_untrusted_fields_untouched() -> None:
    assert to_jsonable(NotFound(repo="acme/widget", number=7)) == {
        "repo": "acme/widget",
        "number": 7,
    }


def test_to_jsonable_renders_enum_members_as_their_value() -> None:
    assert to_jsonable(EscalationCause.EVIDENCE_GAP) == "evidence_gap"


def test_to_jsonable_leaves_clean_primitives_untouched() -> None:
    assert to_jsonable(42) == 42
    assert to_jsonable(True) is True
    assert to_jsonable(None) is None
    assert to_jsonable(3.5) == 3.5
