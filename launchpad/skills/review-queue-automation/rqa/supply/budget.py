"""`reserve()` — E-06's budget half, `code/P-05-reviewer-supply.md` §3.2: per-axis
inclusive bound checking against the spend store, before the work the bound covers.

**Every bound is inclusive, and a reached bound is a value** (RQA-FR-022, RQA-FR-039,
AC11). Each comparison is `already + tokens >= bound` — equality refuses — and every
refusal is returned as a `Refusal`, never raised and never convertible into a success
by anything in this part. The gate is consulted *before* the work it bounds
(U-DISPATCH-12): the reservation is a fixed, conservative per-attempt ceiling the
panel must not exceed, not a promise it will spend this much.

**The three axes are checked in §3.2's order** — `per_pr_tokens`, then
`per_repo_daily_tokens`, then `per_model_daily_tokens` — and an axis whose configured
bound is `None` is never checked. The `downgrade` differs per axis and is not
interchangeable: only the model axis has a per-route escape (a different configured
route has a separate model cap), so only it returns `downgrade="fallback"`, telling
P-06 to advance the cursor past `route.family` before asking `route()` again (AC12).
The two shared axes return `downgrade="incomplete"`: no model on the ladder has its
own separate PR- or repo-scoped budget, so no fallback route escapes them.

**Both daily axes use one rolling 24-hour window** — `utcnow() - ROLLING_WINDOW`,
computed once — not a UTC calendar-day boundary.

**A reservation is not persisted** (§7). Every axis is checked against tokens already
*spent* (the `spend` store), never against outstanding reservations: a reservation
that is never spent leaves no residue, and nothing survives a crash between
`reserve()` and the first `consumed()` because nothing needs to. `reserve()` writes
nothing — no record entry (no kind exists for "a reservation was granted or refused",
§6) and no store row; E-06 hands it no writer to call.

`reserve()` raises only `SupplyError`, and only if `spend` itself fails to answer a
counter query — a storage fault, never a budget decision. It does not apply the
external-send filter when checking `per_model_daily_tokens`: the route it is handed is
already an eligible one selected by `route()` (§7).
"""

from __future__ import annotations

import uuid
from datetime import timedelta
from typing import TYPE_CHECKING

from rqa.contracts import Refusal, Reservation
from rqa.supply.breakers import utcnow
from rqa.supply.spend import SpendStore

if TYPE_CHECKING:  # annotation-only; resolved by type checkers, never at import
    from rqa.contracts import Job, Plan, Route, Snapshot

__all__ = ["ROLLING_WINDOW", "TOKENS_PER_PARTICIPANT", "new_reservation_id", "reserve"]

#: §3.2, verbatim: generous but finite, per-attempt reservation ceiling.
TOKENS_PER_PARTICIPANT: int = 150_000
#: §3.2, verbatim: both daily axes; not a UTC calendar-day boundary.
ROLLING_WINDOW = timedelta(hours=24)


def new_reservation_id() -> str:
    """A fresh opaque reservation id. Carried by P-06 through `SupplyPort` into `run()`
    and back into `consumed()`, where it correlates the `spend` record entry with the
    reservation it discharges — its only job."""
    return uuid.uuid4().hex


def reserve(*, job: Job, plan: Plan, route: Route, snapshot: Snapshot, spend: SpendStore) -> Reservation | Refusal:
    """E-06, verbatim from `CONTRACTS.md` §9. §3.2's six steps, in order.

    Every branch returns a value. The only raise is the spend store's own
    `SupplyError` on a storage fault, which passes through unwrapped.
    """
    # 1. A fixed, conservative per-attempt ceiling — an upper bound the panel must not
    #    exceed, not a promise it will spend this much (U-DISPATCH-12). Only
    #    `plan.participants` is read from the plan.
    tokens = plan.participants * TOKENS_PER_PARTICIPANT
    # 2. One rolling window for both daily axes.
    window_start = utcnow() - ROLLING_WINDOW
    # 3. The PR axis: shared by every model, so no fallback route escapes it.
    if snapshot.budget.per_pr_tokens is not None:
        already = spend.pr_total(job.repo, job.number)
        if already + tokens >= snapshot.budget.per_pr_tokens:
            return Refusal(downgrade="incomplete", axis="per_pr_tokens")
    # 4. The repo axis: same reasoning — repo-scoped, shared by every model.
    if snapshot.budget.per_repo_daily_tokens is not None:
        already = spend.repo_total_since(job.repo, window_start)
        if already + tokens >= snapshot.budget.per_repo_daily_tokens:
            return Refusal(downgrade="incomplete", axis="per_repo_daily_tokens")
    # 5. The model axis: a different configured route has a separate model cap, so this
    #    one — and only this one — tells P-06 to advance the cursor past `route.family`.
    if snapshot.budget.per_model_daily_tokens is not None:
        already = spend.model_total_since(route.model, window_start)
        if already + tokens >= snapshot.budget.per_model_daily_tokens:
            return Refusal(downgrade="fallback", axis="per_model_daily_tokens")
    # 6. Every checked axis passed; an axis whose bound is `None` was never checked.
    return Reservation(id=new_reservation_id(), tokens=tokens)
