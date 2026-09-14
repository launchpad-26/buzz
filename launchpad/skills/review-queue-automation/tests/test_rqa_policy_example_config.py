#!/usr/bin/env python3
"""`config.example.json` — the tracked example must stay runtime-shippable.

`gap/gap-analysis.md` §6.3, U-POLICY-03: the tracked example is asserted to
validate under `rqa.policy.validate`, but until this file existed nothing
checked that — R2-F1 (Task #2214, D-B6-7). Two things this file proves, and
must go on proving after every future edit to the tracked example:

* the file on disk under `<skill-root>/config.example.json` loads and passes
  `rqa.policy.validate.validate()` unmodified — read from its real path, never
  a copy or an inline fixture, so the tracked artefact is the thing under
  test;
* the same validator genuinely rejects a corrupted document, so a future
  regression that silently widens or breaks the schema is caught rather than
  assumed away by a validator that always says yes.

No pytest: every `test_*` function here takes no arguments, per
`tests/run_all.py`'s discovery rule. The suite is also run under the
acceptance venv's real `pytest`, which collects the same functions.
"""

from __future__ import annotations

import copy
import json
import pathlib
import sys

_SKILL_ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_SKILL_ROOT))

from rqa.policy.validate import validate  # noqa: E402
from rqa.policy.types import ValidatedConfig  # noqa: E402
from rqa.contracts import ValidationErrorCode, ValidationFailure  # noqa: E402

#: The tracked example, read from its real repository path — never a copy.
_EXAMPLE_PATH = _SKILL_ROOT / "config.example.json"


def _load_example() -> dict:
    return json.loads(_EXAMPLE_PATH.read_text(encoding="utf-8"))


def test_tracked_example_config_validates() -> None:
    """The file actually tracked in the repository, loaded from its real path
    and pushed through the real validation entry point with no substitution,
    passes. A `ValidationFailure` here means the tracked artefact itself is
    broken, which is exactly what U-POLICY-03 requires never be true."""
    raw = _load_example()
    outcome = validate(raw, repo="example/repo")
    assert isinstance(outcome, ValidatedConfig), (
        f"config.example.json failed to validate: {outcome}"
    )


def test_tracked_example_config_rejects_an_unknown_top_level_key() -> None:
    """The rejection power is permanent, not a one-off observation: take the
    real tracked document, corrupt it in memory only (an unknown top-level
    key — `_keys()`'s `UNKNOWN_KEY` path, `code/P-03-policy.md` §2's closed
    five-key top level), and confirm `validate()` still refuses it. The
    tracked file on disk is never written to by this test."""
    raw = copy.deepcopy(_load_example())
    raw["retention"] = {"window_days": 30}  # a top-level key P-03 does not name

    outcome = validate(raw, repo="example/repo")

    assert isinstance(outcome, ValidationFailure), (
        f"expected rejection of an unknown top-level key, got {outcome}"
    )
    assert any(error.code == ValidationErrorCode.UNKNOWN_KEY for error in outcome.errors), (
        f"expected an UNKNOWN_KEY error, got {[e.code for e in outcome.errors]}"
    )
