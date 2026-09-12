#!/usr/bin/env python3
"""`rqa.judgement`'s own public surface — `code/P-07-judgement.md` §1.

Wave-invariant (see the lane prompt): this asserts only `rqa.judgement`'s own
`__all__` and its own module set. It never asserts a pinned set of packages or
modules under `rqa/` as a whole, never asserts that a sibling's module or
symbol is absent, and never asserts a total test/package count — `rqa.reuse`
(P-13) lands in the same wave and none of that is this package's concern.
"""

from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

import rqa.judgement as judgement  # noqa: E402
from rqa.contracts import Assurance, Judgement  # noqa: E402

_PACKAGE_DIR = pathlib.Path(judgement.__file__).resolve().parent


def test_the_re_exported_surface_is_exactly_the_five_1_names() -> None:
    assert judgement.__all__ == ["judge", "render", "Judgement", "Assurance", "JudgementError"]
    for name in judgement.__all__:
        assert hasattr(judgement, name), f"{name!r} is in __all__ but not an attribute"


def test_judgement_and_assurance_are_the_rqa_contracts_types_not_redefinitions() -> None:
    assert judgement.Judgement is Judgement
    assert judgement.Assurance is Assurance


def test_the_own_module_set_is_exactly_the_six_1_files() -> None:
    own_modules = {path.name for path in _PACKAGE_DIR.glob("*.py")}
    assert own_modules == {
        "__init__.py",
        "judge.py",
        "evidence.py",
        "findings.py",
        "checks.py",
        "render.py",
    }


def test_judgementerror_is_this_packages_own_exception() -> None:
    assert judgement.JudgementError.__module__ == "rqa.judgement.judge"
    assert issubclass(judgement.JudgementError, Exception)
