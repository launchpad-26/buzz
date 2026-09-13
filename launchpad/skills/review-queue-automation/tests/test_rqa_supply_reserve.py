#!/usr/bin/env python3
"""`rqa.supply.budget.reserve` — `code/P-05-reviewer-supply.md` §3.2 and §8 rows T13-T17,
T24 and T27.

No pytest: every `test_*` function here takes no arguments, per `tests/run_all.py`.

T27 is the composite proof for this batch: its Given is this half's (`reserve()`
returning `Refusal(downgrade="fallback")`) and its Then is the sibling half's landed
`route()`, called for real with the advanced cursor. Nothing here reaches a network, a
live model or a credential — the prober is a fake and every store is a fake or an
in-memory SQLite database.
"""

from __future__ import annotations

import inspect
import pathlib
import sqlite3
import sys
from datetime import datetime, timedelta, timezone

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from rqa import edges  # noqa: E402
from rqa.contracts import (  # noqa: E402
    Blocking,
    Budget,
    External,
    Mechanical,
    Plan,
    Policy,
    Refusal,
    RemediationPolicy,
    Reservation,
    RouteCursor,
    RouteUnavailable,
    Snapshot,
)
from rqa.supply import reserve, route  # noqa: E402
from rqa.supply.breakers import SupplyError  # noqa: E402
from rqa.supply.budget import ROLLING_WINDOW, TOKENS_PER_PARTICIPANT, new_reservation_id  # noqa: E402
from rqa.supply.spend import SqliteSpendStore  # noqa: E402

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from test_rqa_supply_route import (  # noqa: E402
    DENY_LABEL,
    FALLBACK,
    PRIMARY,
    REPO,
    FakeProber,
    make_facts,
    make_job,
)

PARTICIPANTS = 3
#: The reservation §3.2 step 1 computes for the plan below.
TOKENS = PARTICIPANTS * TOKENS_PER_PARTICIPANT


# -- fakes ----------------------------------------------------------------------


class FakeSpend:
    """`SpendStore`. Answers each counter from a fixed total and logs every query and
    append, so a test can assert which axes were consulted, in what order, with what
    window — and that `reserve()` never wrote anything."""

    def __init__(self, *, pr: int = 0, repo: int = 0, model: int = 0):
        self.pr = pr
        self.repo = repo
        self.model = model
        self.queries: list[tuple[str, tuple[object, ...]]] = []
        self.appended: list[dict] = []

    def pr_total(self, repo: str, number: int) -> int:
        self.queries.append(("pr_total", (repo, number)))
        return self.pr

    def repo_total_since(self, repo: str, since: datetime) -> int:
        self.queries.append(("repo_total_since", (repo, since)))
        return self.repo

    def model_total_since(self, model: str, since: datetime) -> int:
        self.queries.append(("model_total_since", (model, since)))
        return self.model

    def append(self, *, job_id: str, repo: str, number: int, model: str, tokens: int,
               measured: bool, source: str, recorded_at: datetime) -> None:
        self.appended.append({"job_id": job_id, "repo": repo, "number": number,
                              "model": model, "tokens": tokens, "measured": measured,
                              "source": source, "recorded_at": recorded_at})


# -- builders -------------------------------------------------------------------


def make_plan(participants: int = PARTICIPANTS) -> Plan:
    return Plan(obligations=("correctness",), omitted={}, strategy="panel",
                participants=participants, risk_class="standard", head_sha="a" * 40,
                snapshot_hash="c" * 64, protocol_hash="d" * 64, policy_version="1")


def make_snapshot(*routes, budget: Budget) -> Snapshot:
    return Snapshot(
        hash="c" * 64,
        repo=REPO,
        protocol_hash="d" * 64,
        authority={},
        routes=tuple(routes),
        external=External(allowed=True, deny_label=DENY_LABEL),
        policy=Policy(
            version="1",
            obligations=(),
            blocking=Blocking(categories=frozenset(), severities=frozenset(), corroboration=1),
            mechanical=Mechanical(categories=frozenset(), tools=frozenset()),
            assurance={},
            remediation=RemediationPolicy(allow_forks=False),
        ),
        budget=budget,
    )


def ask(*, budget: Budget, spend: FakeSpend | SqliteSpendStore | None = None,
        participants: int = PARTICIPANTS):
    return reserve(job=make_job(), plan=make_plan(participants), route=PRIMARY,
                   snapshot=make_snapshot(PRIMARY, budget=budget),
                   spend=spend if spend is not None else FakeSpend())


# -- the seam ---------------------------------------------------------------------


def test_reserve_matches_the_contracts_md_edge_signature_exactly() -> None:
    assert inspect.signature(reserve) == inspect.signature(edges.reserve)


def test_the_budget_constants_are_the_ones_section_three_two_states() -> None:
    assert TOKENS_PER_PARTICIPANT == 150_000
    assert ROLLING_WINDOW == timedelta(hours=24)


def test_reserve_is_handed_no_record_writer() -> None:
    """§6: no record kind exists for "a reservation was granted or refused", and E-06's
    signature gives `reserve()` no writer to call — on any path, including refusals."""
    assert "record" not in inspect.signature(reserve).parameters


# -- §8 T13-T15: every bound is inclusive, so equality refuses ---------------------


def test_t13_the_pr_axis_refuses_at_exact_equality_with_downgrade_incomplete() -> None:
    spend = FakeSpend(pr=7)
    answer = ask(budget=Budget(per_pr_tokens=7 + TOKENS, per_repo_daily_tokens=None,
                               per_model_daily_tokens=None), spend=spend)
    assert answer == Refusal(downgrade="incomplete", axis="per_pr_tokens")


def test_t14_the_repo_axis_refuses_at_exact_equality_with_downgrade_incomplete() -> None:
    spend = FakeSpend(repo=11)
    answer = ask(budget=Budget(per_pr_tokens=None, per_repo_daily_tokens=11 + TOKENS,
                               per_model_daily_tokens=None), spend=spend)
    assert answer == Refusal(downgrade="incomplete", axis="per_repo_daily_tokens")


def test_t15_the_model_axis_refuses_at_exact_equality_with_downgrade_fallback() -> None:
    """Only the model axis has a per-route escape, so only it tells P-06 to advance the
    cursor past `route.family` (§3.2 step 5, AC12)."""
    spend = FakeSpend(model=13)
    answer = ask(budget=Budget(per_pr_tokens=None, per_repo_daily_tokens=None,
                               per_model_daily_tokens=13 + TOKENS), spend=spend)
    assert answer == Refusal(downgrade="fallback", axis="per_model_daily_tokens")


def test_an_exceeded_bound_refuses_like_a_reached_one() -> None:
    answer = ask(budget=Budget(per_pr_tokens=TOKENS - 1, per_repo_daily_tokens=None,
                               per_model_daily_tokens=None))
    assert answer == Refusal(downgrade="incomplete", axis="per_pr_tokens")


def test_the_model_axis_is_queried_for_the_supplied_routes_model() -> None:
    spend = FakeSpend()
    ask(budget=Budget(per_pr_tokens=None, per_repo_daily_tokens=None,
                      per_model_daily_tokens=10**9), spend=spend)
    assert spend.queries == [("model_total_since", (PRIMARY.model, spend.queries[0][1][1]))]


# -- §8 T16: headroom grants ------------------------------------------------------


def test_t16_one_token_of_headroom_on_every_axis_grants_the_full_reservation() -> None:
    spend = FakeSpend(pr=5, repo=5, model=5)
    answer = ask(budget=Budget(per_pr_tokens=5 + TOKENS + 1, per_repo_daily_tokens=5 + TOKENS + 1,
                               per_model_daily_tokens=5 + TOKENS + 1), spend=spend)
    assert isinstance(answer, Reservation)
    assert answer.tokens == PARTICIPANTS * TOKENS_PER_PARTICIPANT


def test_the_reservation_id_is_a_fresh_non_empty_string_every_time() -> None:
    budget = Budget(per_pr_tokens=None, per_repo_daily_tokens=None, per_model_daily_tokens=None)
    first, second = ask(budget=budget), ask(budget=budget)
    assert isinstance(first.id, str) and first.id
    assert first.id != second.id
    assert new_reservation_id() != new_reservation_id()


def test_the_reservation_scales_with_the_plans_participants_and_nothing_else() -> None:
    budget = Budget(per_pr_tokens=None, per_repo_daily_tokens=None, per_model_daily_tokens=None)
    assert ask(budget=budget, participants=1).tokens == TOKENS_PER_PARTICIPANT
    assert ask(budget=budget, participants=5).tokens == 5 * TOKENS_PER_PARTICIPANT


# -- §8 T17: a reservation is never a spend ---------------------------------------


def test_t17_a_grant_writes_nothing_to_the_spend_store() -> None:
    spend = FakeSpend()
    answer = ask(budget=Budget(per_pr_tokens=None, per_repo_daily_tokens=None,
                               per_model_daily_tokens=None), spend=spend)
    assert isinstance(answer, Reservation)
    assert spend.appended == []


def test_t17_a_refusal_writes_nothing_to_the_spend_store_either() -> None:
    spend = FakeSpend()
    ask(budget=Budget(per_pr_tokens=1, per_repo_daily_tokens=1, per_model_daily_tokens=1),
        spend=spend)
    assert spend.appended == []


def test_t17_a_reservation_leaves_no_residue_the_next_reserve_call_sees() -> None:
    """§7: nothing is persisted between `reserve()` and the first `consumed()`; every
    axis is checked against tokens already *spent*, never against outstanding
    reservations — so a second call with the same store gets the same answer."""
    store = SqliteSpendStore(connection=sqlite3.connect(":memory:"))
    budget = Budget(per_pr_tokens=TOKENS + 1, per_repo_daily_tokens=None,
                    per_model_daily_tokens=None)
    first = ask(budget=budget, spend=store)
    second = ask(budget=budget, spend=store)
    assert isinstance(first, Reservation) and isinstance(second, Reservation)
    assert store.pr_total(REPO, 7) == 0


# -- §8 T24: a None bound is never checked ----------------------------------------


def test_t24_a_none_model_bound_is_never_queried_while_the_other_axes_still_refuse() -> None:
    spend = FakeSpend(pr=10**12, repo=10**12, model=10**12)
    answer = ask(budget=Budget(per_pr_tokens=1, per_repo_daily_tokens=1,
                               per_model_daily_tokens=None), spend=spend)
    assert answer == Refusal(downgrade="incomplete", axis="per_pr_tokens")
    assert all(name != "model_total_since" for name, _ in spend.queries)


def test_t24_an_all_none_budget_grants_without_a_single_counter_query() -> None:
    spend = FakeSpend(pr=10**12, repo=10**12, model=10**12)
    answer = ask(budget=Budget(per_pr_tokens=None, per_repo_daily_tokens=None,
                               per_model_daily_tokens=None), spend=spend)
    assert isinstance(answer, Reservation)
    assert spend.queries == []


# -- §3.2's order and window -------------------------------------------------------


def test_the_axes_are_checked_in_section_three_twos_order_and_stop_at_the_first_refusal() -> None:
    spend = FakeSpend(pr=10**12, repo=10**12, model=10**12)
    answer = ask(budget=Budget(per_pr_tokens=1, per_repo_daily_tokens=1,
                               per_model_daily_tokens=1), spend=spend)
    assert answer.axis == "per_pr_tokens"
    assert [name for name, _ in spend.queries] == ["pr_total"]


def test_the_repo_axis_is_checked_before_the_model_axis() -> None:
    spend = FakeSpend(repo=10**12, model=10**12)
    answer = ask(budget=Budget(per_pr_tokens=None, per_repo_daily_tokens=1,
                               per_model_daily_tokens=1), spend=spend)
    assert answer.axis == "per_repo_daily_tokens"
    assert [name for name, _ in spend.queries] == ["repo_total_since"]


def test_both_daily_axes_share_one_rolling_24_hour_window() -> None:
    """§3.2 step 2: `window_start = utcnow() - ROLLING_WINDOW`, computed once and used
    by both daily axes — a rolling window, not a UTC calendar-day boundary."""
    spend = FakeSpend()
    before = datetime.now(timezone.utc)
    ask(budget=Budget(per_pr_tokens=None, per_repo_daily_tokens=10**9,
                      per_model_daily_tokens=10**9), spend=spend)
    after = datetime.now(timezone.utc)
    sinces = [arguments[1] for name, arguments in spend.queries if name.endswith("_since")]
    assert len(sinces) == 2
    assert sinces[0] == sinces[1]
    assert before - ROLLING_WINDOW <= sinces[0] <= after - ROLLING_WINDOW


# -- storage faults are `SupplyError`, never a budget decision ---------------------


def test_a_failing_counter_query_raises_supply_error_not_a_refusal() -> None:
    connection = sqlite3.connect(":memory:")
    store = SqliteSpendStore(connection=connection)
    connection.close()
    try:
        ask(budget=Budget(per_pr_tokens=10**9, per_repo_daily_tokens=None,
                          per_model_daily_tokens=None), spend=store)
    except SupplyError:
        return
    raise AssertionError("a storage fault must raise SupplyError, never return a value")


def test_a_budget_refusal_is_a_value_and_never_raises() -> None:
    """RQA-FR-039/AC11: a reached bound is a `Refusal` value at every configured axis;
    nothing in this part converts it into an exception or a success."""
    for budget in (
        Budget(per_pr_tokens=1, per_repo_daily_tokens=None, per_model_daily_tokens=None),
        Budget(per_pr_tokens=None, per_repo_daily_tokens=1, per_model_daily_tokens=None),
        Budget(per_pr_tokens=None, per_repo_daily_tokens=None, per_model_daily_tokens=1),
    ):
        answer = ask(budget=budget)
        assert isinstance(answer, Refusal)


# -- §8 T27: the composite proof — this half's refusal drives the sibling's route() --


def test_t27_a_fallback_refusal_advances_the_cursor_to_a_different_family_route() -> None:
    """The Given is this half's: `reserve()` refuses the model axis with
    `downgrade="fallback"`. The Then is the sibling's landed `route()`: with the refused
    route's family excluded — exactly the advance P-06 makes — the next result is a
    route from a different family."""
    snapshot = make_snapshot(
        PRIMARY, FALLBACK,
        budget=Budget(per_pr_tokens=None, per_repo_daily_tokens=None,
                      per_model_daily_tokens=TOKENS),  # equality: PRIMARY's model refuses
    )
    refusal = reserve(job=make_job(), plan=make_plan(), route=PRIMARY, snapshot=snapshot,
                      spend=FakeSpend())
    assert refusal == Refusal(downgrade="fallback", axis="per_model_daily_tokens")
    # P-06's advance (CONTRACTS.md §10): the refused route's family joins the exclusions.
    cursor = RouteCursor(excluded_families=frozenset({PRIMARY.family}),
                         excluded_routes=frozenset())
    answer = route(job=make_job(), obligation="correctness", snapshot=snapshot,
                   facts=make_facts(), cursor=cursor, prober=FakeProber(),
                   breakers=_FreshBreakers())
    selected, _ = answer
    assert selected == FALLBACK
    assert selected.family != PRIMARY.family


def test_t27_with_no_distinct_family_configured_the_advance_exhausts_to_unavailable() -> None:
    snapshot = make_snapshot(
        PRIMARY,
        budget=Budget(per_pr_tokens=None, per_repo_daily_tokens=None,
                      per_model_daily_tokens=TOKENS),
    )
    refusal = reserve(job=make_job(), plan=make_plan(), route=PRIMARY, snapshot=snapshot,
                      spend=FakeSpend())
    assert refusal == Refusal(downgrade="fallback", axis="per_model_daily_tokens")
    cursor = RouteCursor(excluded_families=frozenset({PRIMARY.family}),
                         excluded_routes=frozenset())
    answer = route(job=make_job(), obligation="correctness", snapshot=snapshot,
                   facts=make_facts(), cursor=cursor, prober=FakeProber(),
                   breakers=_FreshBreakers())
    assert answer == RouteUnavailable(no_fallback=True, tried=())


def _FreshBreakers():
    """A real, empty `SqliteBreakerStore` — T27 exercises the landed sibling code end to
    end, so its breaker store is the landed implementation, not a fake."""
    from rqa.supply.breakers import SqliteBreakerStore

    return SqliteBreakerStore(connection=sqlite3.connect(":memory:"))
