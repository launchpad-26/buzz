"""Captured-check attribution and evidence completeness — `code/P-07-judgement.md`
§3 step 5.

P-07 never fetches checks (E-14 is not one of its dependencies); it only reduces
the checks already frozen in `Facts` by P-02's E-23 capture. "Evidence
completeness" here is the cutoff bound itself: a check observed after
`panel.evidence_cutoff` is not merely stale, it is excluded from every judgement
input, so a still-running check that finishes moments after the panel's last
attempt never silently joins the evidence base a already-recorded judgement was
computed from.

Attribution answers one question per eligible, genuinely failing head check:
did this PR introduce the failure, or did it inherit it from the base? A
`PASSING` or `UNSETTLED` (pending) check gets no attribution entry at all —
`Judgement.attribution` only ever names checks that are actually blocking
candidates, and a pending check "never corroborates, blocks, or inherits"
(`CONTRACTS.md` §4).
"""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from rqa.contracts import FAILING, CheckRun

__all__ = ["eligible", "attribute"]


def eligible(checks: tuple[CheckRun, ...], *, cutoff: datetime) -> tuple[CheckRun, ...]:
    """Checks observed at or before `cutoff`. Later observations are excluded from
    every judgement input (§3 step 5) — no later attestation, and no later check,
    ever counts."""
    return tuple(check for check in checks if check.observed_at <= cutoff)


def attribute(
    *,
    head_checks: tuple[CheckRun, ...],
    base_checks: tuple[CheckRun, ...],
    cutoff: datetime,
) -> dict[str, Literal["pr", "inherited"]]:
    """Attribution for every eligible head check reporting a genuine failure
    (§3 step 5).

    A failing head check is `"inherited"` only when an eligible same-name base
    check is also failing; otherwise it is `"pr"`. `PASSING` and `UNSETTLED`
    head checks get no entry — there is nothing to attribute and nothing that
    may corroborate or block. An inherited failure still gets an entry (it
    "remains visible"); it is the caller's job to never let it corroborate or
    block.
    """
    eligible_head = eligible(head_checks, cutoff=cutoff)
    eligible_base_failing_names = {
        check.name for check in eligible(base_checks, cutoff=cutoff) if check.conclusion in FAILING
    }
    attribution: dict[str, Literal["pr", "inherited"]] = {}
    for check in eligible_head:
        if check.conclusion not in FAILING:
            continue
        attribution[check.name] = (
            "inherited" if check.name in eligible_base_failing_names else "pr"
        )
    return attribution
