#!/usr/bin/env python3
"""The check-conclusion vocabulary. One definition, four consumers.

WHY THIS MODULE EXISTS. Four modules judged check results, each with its own
literal set, and one of them was wrong in two ways at once
(launchpad-26/buzz#1963):

    dispatcher.py:287   c.get("conclusion") == "SUCCESS"
    findings.py:126     _clean(...).upper() in FAILING_CONCLUSIONS
    history.py:189      (...).upper() not in ("SUCCESS", "NEUTRAL", "SKIPPED")
    panel.py:483        (...).upper() not in ("SUCCESS", "NEUTRAL", "SKIPPED", "")

`dispatcher.py` fed the `checks_complete_ok` approval gate, and it neither
upper-cased nor accepted anything but `SUCCESS`:

  1. CASING. Its checks come from `evidence.py` via `RestReader.checks()`, and
     the REST check-runs API returns `conclusion` lower-case (`"success"`).
     `SUCCESS` is the GraphQL `CheckConclusionState` spelling. The comparison was
     written against one transport and fed by the other, so it was never true.
  2. VOCABULARY. Even upper-cased, requiring `SUCCESS` from every check fails on
     any suite containing a skipped job. Every pull request in this repository
     has several: the `Detect Changed Paths` fan-out skips the desktop, mobile
     and relay jobs on a docs- or launchpad-only change. `SKIPPED` is a green
     outcome here, not an absent one.

Both defects fail closed, so nothing was ever wrongly approved — but
`checks_complete_ok` is one of the 22 conjunctive gates in
`risk.ApprovalState.passed()`, and a gate that can never be true makes automated
approval unsatisfiable no matter how it is configured.

TWO DIFFERENT QUESTIONS, KEPT DISTINCT. "Did the suite pass?" and "did a check
genuinely fail?" are not each other's negation, because a check can be pending.
`is_passing` answers the first, `is_failing` the second, and a pending check is
neither. `FAILING` is deliberately narrower than "not passing": it names the
conclusions that corroborate a reviewer's finding, where an unknown or absent
conclusion must not be counted as evidence of breakage.
"""

from __future__ import annotations

from typing import Any

#: Conclusions that mean "this check is not standing in the way".
#: `NEUTRAL` and `SKIPPED` are green outcomes: GitHub reports them for a check
#: that ran and declined to judge, and for one the workflow's own path filters
#: never started.
PASSING = frozenset({"SUCCESS", "NEUTRAL", "SKIPPED"})

#: Conclusions that count as a real failure for finding corroboration.
#: Narrower than "not in PASSING" on purpose — see the module docstring.
FAILING = frozenset({"FAILURE", "TIMED_OUT", "CANCELLED", "ACTION_REQUIRED", "STALE"})


def canonical(value: Any) -> str:
    """The one canonical spelling of a conclusion: stripped and upper-cased.

    Accepts either transport's casing. GraphQL's `CheckConclusionState` is the
    canonical form because it is already an enumeration; REST's lower-case
    strings fold onto it.
    """
    return str(value or "").strip().upper()


#: A commit status reports the same idea as a check run in a different
#: vocabulary. GraphQL's `StatusState` -> `CheckConclusionState`, so consumers
#: compare one set. `PENDING` maps to "" — pending is not a conclusion, and
#: `is_pending` is what answers that question.
_STATUS_TO_CONCLUSION = {
    "SUCCESS": "SUCCESS",
    "FAILURE": "FAILURE",
    "ERROR": "FAILURE",
    "EXPECTED": "SUCCESS",
    "PENDING": "",
}


def conclusion_from_status(state: Any) -> str:
    """The conclusion a commit status implies, in the canonical vocabulary.

    An unrecognised state passes through canonicalised rather than being forced
    into a known value: `is_failing` then treats it as standing in the way, which
    is the safe reading of a state we do not know.
    """
    key = canonical(state)
    return _STATUS_TO_CONCLUSION.get(key, key)


def conclusion_of(check: Any) -> str:
    """The canonical conclusion of one check entry, or "" when absent."""
    if not isinstance(check, dict):
        return ""
    return canonical(check.get("conclusion"))


def is_pending(check: Any) -> bool:
    """True when this check has reached no conclusion yet."""
    return conclusion_of(check) == ""


def is_passing(check: Any) -> bool:
    """True when this check is green. A pending check is NOT passing."""
    return conclusion_of(check) in PASSING


def is_failing(check: Any) -> bool:
    """True when this check is neither green nor pending.

    Broader than `FAILING` by design: an unrecognised conclusion is treated as
    standing in the way rather than waved through, because the safe reading of an
    unknown state is that something is wrong.
    """
    return not is_passing(check) and not is_pending(check)


def all_passing(checks: Any) -> bool:
    """True when there is at least one check and every one of them is green.

    Fails closed twice over: an empty list is not green (no evidence is not
    evidence of success), and a single pending check is not green either.
    """
    if not checks:
        return False
    return all(is_passing(check) for check in checks)


def failing_names(checks: Any, *, name_keys: tuple[str, ...] = ("name", "id")) -> list[str]:
    """Names of checks whose conclusion is a genuine failure, per `FAILING`."""
    names: list[str] = []
    for check in checks or []:
        if not isinstance(check, dict):
            continue
        if conclusion_of(check) not in FAILING:
            continue
        for key in name_keys:
            value = str(check.get(key) or "").strip()
            if value:
                names.append(value)
                break
    return names
