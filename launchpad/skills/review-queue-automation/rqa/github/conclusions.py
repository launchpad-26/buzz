"""The canonical `CheckConclusion` vocabulary and total normalisation functions
(U-VERDICT-06). `code/P-09-github-adapter.md` §1, §2; `CONTRACTS.md` §4.

One canonicalisation and one conclusion vocabulary that every consumer imports
rather than re-declares — the register records that the estate's version of
this module (`scripts/checks.py`) replaced four independently drifted literal
sets. The definitions themselves live only in `rqa.contracts` (§4) and are
imported unchanged here; this module owns turning what GitHub says into that
vocabulary and nothing else.

U-VERDICT-06's recorded rework is honoured by the shape of the whole package:
a bare conclusion is no longer sufficient input to a blocking decision.
`checks()` (E-14) returns the same canonical vocabulary for a head read and a
base read, and `facts()` (E-23) carries both `checks` and `base_checks`, so
the PR-versus-base attribution RQA-FR-014/RQA-FR-036/RQA-BR-009 require can be
derived — by P-07, never here (§7: P-09 supplies the total normalisation and
never the classification).

**Totality (§2, §8 T6).** Every documented or unknown source value maps to
exactly one `CheckConclusion`, never an exception. Unknown GitHub values
normalise to `ACTION_REQUIRED` — fail closed: a conclusion this adapter does
not recognise stands in the way rather than passing silently. Pending never
corroborates, blocks, or inherits (`UNSETTLED`); the estate's fail-closed
reading of "no conclusion yet" is kept.

The one deliberate vocabulary change from the estate: `CANCELLED` moved from
the failing set to `PASSING` — `CONTRACTS.md` §4 fixes
`FAILING = {failure, timed_out, action_required}` and
`PASSING = {success, neutral, skipped, cancelled}`, and the contract is the
single source. A legacy commit status `error` has no member of its own and
takes the unknown mapping, `ACTION_REQUIRED`, which keeps it failing.
"""

from __future__ import annotations

from rqa.contracts import FAILING, PASSING, UNSETTLED, CheckConclusion

__all__ = [
    "FAILING",
    "PASSING",
    "UNSETTLED",
    "CheckConclusion",
    "normalise_conclusion",
    "normalise_status",
]

#: The spellings GitHub documents for a check-run conclusion, canonicalised.
_BY_VALUE = {member.value: member for member in CheckConclusion}

#: GraphQL `StatusState` / REST commit-status `state` → the one vocabulary.
#: `pending` is not a conclusion; it is the unsettled reading. `error` is
#: deliberately unlisted and takes the unknown mapping (ACTION_REQUIRED).
_STATUS_TO_CONCLUSION = {
    "success": CheckConclusion.SUCCESS,
    "failure": CheckConclusion.FAILURE,
    "pending": CheckConclusion.PENDING,
    "expected": CheckConclusion.PENDING,
}


def _canonical(value: object) -> str:
    """The one canonical spelling: stripped and lower-cased; "" when absent."""
    if value is None:
        return ""
    return str(value).strip().lower()


def normalise_conclusion(value: object) -> CheckConclusion:
    """The `CheckConclusion` of one check-run conclusion field. Total: an
    absent conclusion (the run has not completed) is `PENDING`; a documented
    value is itself; anything unknown is `ACTION_REQUIRED` (§2)."""
    key = _canonical(value)
    if key == "":
        return CheckConclusion.PENDING
    return _BY_VALUE.get(key, CheckConclusion.ACTION_REQUIRED)


def normalise_status(state: object) -> CheckConclusion:
    """The `CheckConclusion` a legacy commit status implies. Total: an absent
    state reads as `PENDING` (nothing concluded), a documented state maps per
    `_STATUS_TO_CONCLUSION`, and anything else — including the legacy `error`
    — is `ACTION_REQUIRED` (§2's unknown rule)."""
    key = _canonical(state)
    if key == "":
        return CheckConclusion.PENDING
    return _STATUS_TO_CONCLUSION.get(key, CheckConclusion.ACTION_REQUIRED)
