#!/usr/bin/env python3
"""`rqa.supply.spend` — `code/P-05-reviewer-supply.md` §3.3, §5's `spend` store, §6's one
record entry, and §8 rows T18-T23.

No pytest: every `test_*` function here takes no arguments, per `tests/run_all.py`.

T21's second clause — a prior `open` breaker closes on success — runs against the landed
`SqliteBreakerStore`, so the real close is proven, not just that a method was called.
Nothing here reaches a network, a live model or a credential — every store is a fake or
an in-memory SQLite database, and the `SupplyError` security test asserts a handed
token-shaped value cannot be recovered from the exception's message, `args`, `__cause__`
or `__context__`.
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
    AppendFailed,
    Attempt,
    AttemptFailure,
    Attestation,
    Entry,
    HarnessIdentity,
    Reservation,
    Spend,
    Verdict,
)
from rqa.supply import consumed  # noqa: E402
from rqa.supply.breakers import SqliteBreakerStore, SupplyError, utcnow  # noqa: E402
from rqa.supply.spend import SpendStore, SqliteSpendStore, ensure_schema  # noqa: E402

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from test_rqa_supply_route import PRIMARY, REPO, make_job  # noqa: E402

NOW = datetime(2026, 9, 12, 9, 0, 0, tzinfo=timezone.utc)
RESERVATION = Reservation(id="res-1", tokens=450_000)

#: §6's payload, in full. Exactly these nine keys, nothing else.
PAYLOAD_KEYS = frozenset({"tokens", "measured", "source", "model", "provider", "repo",
                          "number", "attempt_id", "reservation_id"})


# -- fakes ----------------------------------------------------------------------
# Each fake logs into a shared `events` list, so a test can assert §3.3's order:
# the authoritative record first, the local projection second, the breaker last.


class FakeRecord:
    def __init__(self, events: list | None = None):
        self.events = events if events is not None else []
        self.entries: list[tuple[str, str, dict]] = []

    def append(self, job_id, kind, payload):
        self.events.append("record.append")
        self.entries.append((job_id, kind, dict(payload)))
        return Entry(seq=len(self.entries), hash="h" * 64)


class FailingRecord:
    def append(self, job_id, kind, payload):
        raise AppendFailed("the record could not be appended")


class FakeSpendSink:
    def __init__(self, events: list | None = None):
        self.events = events if events is not None else []
        self.appended: list[dict] = []

    def pr_total(self, repo, number):
        return 0

    def repo_total_since(self, repo, since):
        return 0

    def model_total_since(self, model, since):
        return 0

    def append(self, *, job_id, repo, number, model, tokens, measured, source, recorded_at):
        self.events.append("spend.append")
        self.appended.append({"job_id": job_id, "repo": repo, "number": number,
                              "model": model, "tokens": tokens, "measured": measured,
                              "source": source, "recorded_at": recorded_at})


class FakeBreakerSink:
    def __init__(self, events: list | None = None):
        self.events = events if events is not None else []
        self.calls: list[tuple[str, str, str]] = []

    def cooldown(self, route_key):
        return None

    def set_cooldown(self, route_key, *, until, error):
        self.calls.append(("set_cooldown", route_key, error))

    def breaker(self, scope):
        raise AssertionError("consumed() never reads a breaker")

    def record_failure(self, scope, error):
        self.events.append("breakers.record_failure")
        self.calls.append(("record_failure", scope, error))

    def record_success(self, scope):
        self.events.append("breakers.record_success")
        self.calls.append(("record_success", scope, ""))


# -- builders -------------------------------------------------------------------


def make_verdict() -> Verdict:
    return Verdict(obligations={}, findings=(), injection_attempts=(),
                   identity=HarnessIdentity(harness=PRIMARY.harness, model=PRIMARY.model,
                                            provider=PRIMARY.provider),
                   protocol_version="1")


def make_attempt(outcome) -> Attempt:
    return Attempt(id="attempt-1", route=PRIMARY, outcome=outcome,
                   attestation=Attestation(harness=PRIMARY.harness, model=PRIMARY.model,
                                           provider=PRIMARY.provider, route=PRIMARY,
                                           effort="standard", started_at=NOW,
                                           ended_at=NOW + timedelta(minutes=3),
                                           exit_code=0))


def consume(*, reading, outcome=None, record=None, spend=None, breakers=None) -> Spend:
    return consumed(
        job=make_job(),
        attempt=make_attempt(outcome if outcome is not None else make_verdict()),
        reading=reading,
        reservation=RESERVATION,
        record=record if record is not None else FakeRecord(),
        spend=spend if spend is not None else FakeSpendSink(),
        breakers=breakers if breakers is not None else FakeBreakerSink(),
    )


# -- the seam ---------------------------------------------------------------------


def test_consumed_matches_the_contracts_md_edge_signature_exactly() -> None:
    assert inspect.signature(consumed) == inspect.signature(edges.consumed)


def test_the_spend_store_shape_is_stated_in_this_package() -> None:
    """`rqa/edges.py` keeps `SpendStore` an empty Protocol whose shape is P-05's to
    state; `rqa/supply/spend.py` is that statement — §5's four methods, no more."""
    assert SpendStore is not edges.SpendStore
    declared = {name for name in vars(SpendStore) if not name.startswith("_")}
    assert declared == {"pr_total", "repo_total_since", "model_total_since", "append"}


def test_the_concrete_store_satisfies_the_protocol_signatures_verbatim() -> None:
    for name in ("pr_total", "repo_total_since", "model_total_since", "append"):
        expected = inspect.signature(getattr(SpendStore, name))
        actual = inspect.signature(getattr(SqliteSpendStore, name))
        assert actual == expected, name


# -- §8 T18-T19, and reading=0: the measured/estimated decision --------------------


def test_t18_an_exposed_reading_is_measured_from_the_harness_and_wins_over_the_ceiling() -> None:
    spend = FakeSpendSink()
    answer = consume(reading=57_000, spend=spend)
    assert answer == Spend(tokens=57_000, measured=True, source="harness")
    assert spend.appended[0]["tokens"] == 57_000
    assert spend.appended[0]["tokens"] != RESERVATION.tokens


def test_t19_no_reading_charges_the_reservation_ceiling_and_is_marked_estimated() -> None:
    """U-DISPATCH-13/RQA-FR-021: the ceiling stands in only when nothing was exposed,
    and is always marked estimated — never conflated with a measurement."""
    spend = FakeSpendSink()
    answer = consume(reading=None, spend=spend)
    assert answer == Spend(tokens=RESERVATION.tokens, measured=False, source="reservation")
    assert spend.appended[0]["measured"] is False
    assert spend.appended[0]["source"] == "reservation"


def test_a_reading_of_zero_is_a_measurement_of_zero_not_a_missing_reading() -> None:
    """The test is `is not None`, never truthiness (§3.3 step 1)."""
    answer = consume(reading=0)
    assert answer == Spend(tokens=0, measured=True, source="harness")


def test_the_record_and_the_store_row_carry_the_same_provenance() -> None:
    record, spend = FakeRecord(), FakeSpendSink()
    consume(reading=57_000, record=record, spend=spend)
    _, _, payload = record.entries[0]
    row = spend.appended[0]
    assert (payload["tokens"], payload["measured"], payload["source"]) == (
        row["tokens"], row["measured"], row["source"]) == (57_000, True, "harness")


# -- §6: the one record entry ------------------------------------------------------


def test_the_entry_is_kind_spend_for_this_job_with_exactly_the_nine_payload_keys() -> None:
    record = FakeRecord()
    consume(reading=57_000, record=record)
    job_id, kind, payload = record.entries[0]
    assert job_id == make_job().id
    assert kind == "spend"
    assert frozenset(payload) == PAYLOAD_KEYS


def test_the_payload_values_are_the_attempts_and_the_reservations() -> None:
    record = FakeRecord()
    consume(reading=57_000, record=record)
    _, _, payload = record.entries[0]
    assert payload == {
        "tokens": 57_000,
        "measured": True,
        "source": "harness",
        "model": PRIMARY.model,
        "provider": PRIMARY.provider,
        "repo": REPO,
        "number": 7,
        "attempt_id": "attempt-1",
        "reservation_id": RESERVATION.id,
    }


def test_exactly_one_entry_is_written_per_call() -> None:
    record = FakeRecord()
    consume(reading=None, record=record)
    assert len(record.entries) == 1


# -- §3.3's order: record, then projection, then breaker ----------------------------


def test_the_authoritative_append_precedes_the_projection_which_precedes_the_breaker() -> None:
    events: list[str] = []
    consume(reading=57_000, record=FakeRecord(events), spend=FakeSpendSink(events),
            breakers=FakeBreakerSink(events))
    assert events == ["record.append", "spend.append", "breakers.record_success"]


def test_the_projection_row_is_the_jobs_and_the_routes_with_an_aware_utc_stamp() -> None:
    spend = FakeSpendSink()
    consume(reading=None, spend=spend)
    row = spend.appended[0]
    assert (row["job_id"], row["repo"], row["number"], row["model"]) == (
        make_job().id, REPO, 7, PRIMARY.model)
    assert row["recorded_at"].tzinfo is not None
    assert row["recorded_at"].utcoffset() == timedelta(0)


# -- §8 T20-T22: the three-way breaker classification -------------------------------


def test_t20_a_provider_terminal_failure_records_one_failure_for_the_routes_family() -> None:
    breakers = FakeBreakerSink()
    consume(reading=None, outcome=AttemptFailure(kind="PROVIDER_TERMINAL", detail="502"),
            breakers=breakers)
    assert breakers.calls == [("record_failure", PRIMARY.family, "502")]


def test_t21_a_verdict_records_one_success_for_the_routes_family() -> None:
    breakers = FakeBreakerSink()
    consume(reading=57_000, outcome=make_verdict(), breakers=breakers)
    assert breakers.calls == [("record_success", PRIMARY.family, "")]


def test_t21_a_prior_open_breaker_closes_on_a_successful_attempt_in_the_real_store() -> None:
    """The cross-half clause, against the landed `SqliteBreakerStore`: a family opened by
    three PROVIDER_TERMINAL failures reads back `open`, and one successful `consumed()`
    closes it and clears the count — §5's `record_success` semantics, proven end to end."""
    breakers = SqliteBreakerStore(connection=sqlite3.connect(":memory:"))
    for _ in range(3):
        breakers.record_failure(PRIMARY.family, "provider terminal")
    assert breakers.breaker(PRIMARY.family).status == "open"
    consume(reading=57_000, outcome=make_verdict(), breakers=breakers)
    state = breakers.breaker(PRIMARY.family)
    assert state.status == "closed"
    assert state.failures == 0
    assert state.open_until is None


def test_t22_a_transient_failure_makes_no_breaker_call_at_all() -> None:
    breakers = FakeBreakerSink()
    consume(reading=None, outcome=AttemptFailure(kind="TRANSIENT", detail="timeout"),
            breakers=breakers)
    assert breakers.calls == []


def test_t22_a_candidate_terminal_failure_makes_no_breaker_call_either() -> None:
    """Neither reflects on the *provider's* health (§3.3 step 4, §7): the third branch
    is a real branch, not a fall-through into failure or success."""
    breakers = FakeBreakerSink()
    consume(reading=None,
            outcome=AttemptFailure(kind="CANDIDATE_TERMINAL", detail="invalid verdict"),
            breakers=breakers)
    assert breakers.calls == []


def test_a_failed_attempt_still_records_its_spend() -> None:
    """The cost was incurred whatever the outcome; the classification decides only the
    breaker, never whether the spend is written."""
    record, spend = FakeRecord(), FakeSpendSink()
    consume(reading=41_000, outcome=AttemptFailure(kind="TRANSIENT", detail="timeout"),
            record=record, spend=spend)
    assert len(record.entries) == 1
    assert spend.appended[0]["tokens"] == 41_000


# -- §8 T23: AppendFailed propagates and nothing below runs -------------------------


def test_t23_a_failed_append_propagates_and_neither_the_projection_nor_the_breaker_runs() -> None:
    spend, breakers = FakeSpendSink(), FakeBreakerSink()
    try:
        consume(reading=57_000, record=FailingRecord(), spend=spend, breakers=breakers)
    except AppendFailed:
        assert spend.appended == []
        assert breakers.calls == []
        return
    raise AssertionError("AppendFailed must propagate uncaught")


# -- §5: the sqlite projection ------------------------------------------------------


def store() -> SqliteSpendStore:
    return SqliteSpendStore(connection=sqlite3.connect(":memory:"))


def add(subject: SqliteSpendStore, *, repo: str = REPO, number: int = 7,
        model: str = PRIMARY.model, tokens: int = 1000, measured: bool = True,
        source: str = "harness", at: datetime | None = None) -> None:
    subject.append(job_id="job-1", repo=repo, number=number, model=model, tokens=tokens,
                   measured=measured, source=source,
                   recorded_at=at if at is not None else utcnow())


def test_the_schema_declares_the_table_and_its_three_indexes() -> None:
    connection = sqlite3.connect(":memory:")
    ensure_schema(connection=connection)
    tables = {row[0] for row in connection.execute(
        "SELECT name FROM sqlite_master WHERE type='table'")}
    indexes = {row[0] for row in connection.execute(
        "SELECT name FROM sqlite_master WHERE type='index'")}
    assert "spend" in tables
    assert {"spend_by_pr", "spend_by_repo_time", "spend_by_model_time"} <= indexes
    ensure_schema(connection=connection)  # idempotent


def test_the_columns_are_exactly_section_fives() -> None:
    subject = store()
    names = [row[1] for row in subject._connection.execute("PRAGMA table_info(spend)")]
    assert names == ["id", "job_id", "repo", "number", "model", "tokens", "measured",
                     "source", "recorded_at"]


def test_pr_total_sums_only_the_named_pr() -> None:
    subject = store()
    add(subject, tokens=100)
    add(subject, tokens=200)
    add(subject, number=8, tokens=4000)
    add(subject, repo="other/repo", tokens=8000)
    assert subject.pr_total(REPO, 7) == 300
    assert subject.pr_total(REPO, 8) == 4000
    assert subject.pr_total("other/repo", 7) == 8000


def test_repo_total_since_sums_only_rows_inside_the_window() -> None:
    subject = store()
    add(subject, tokens=100, at=NOW - timedelta(hours=25))
    add(subject, tokens=200, at=NOW - timedelta(hours=1))
    add(subject, tokens=400, at=NOW)
    assert subject.repo_total_since(REPO, NOW - timedelta(hours=24)) == 600


def test_model_total_since_sums_only_the_named_model_inside_the_window() -> None:
    subject = store()
    add(subject, tokens=100, at=NOW - timedelta(hours=25))
    add(subject, tokens=200, at=NOW - timedelta(hours=2))
    add(subject, model="other-model", tokens=4000, at=NOW - timedelta(hours=2))
    assert subject.model_total_since(PRIMARY.model, NOW - timedelta(hours=24)) == 200


def test_an_empty_store_answers_zero_on_every_axis() -> None:
    subject = store()
    assert subject.pr_total(REPO, 7) == 0
    assert subject.repo_total_since(REPO, NOW) == 0
    assert subject.model_total_since(PRIMARY.model, NOW) == 0


def test_measured_is_stored_as_zero_or_one() -> None:
    subject = store()
    add(subject, measured=True)
    add(subject, measured=False, source="reservation")
    values = [row[0] for row in subject._connection.execute(
        "SELECT measured FROM spend ORDER BY id")]
    assert values == [1, 0]


def test_a_row_survives_the_connection_that_wrote_it() -> None:
    """Each scheduled tick is a separate process; a spend held only in memory would let
    the next `reserve()` re-grant tokens the previous job already burned."""
    path = pathlib.Path(__file__).resolve().parent / "_spend_probe.sqlite3"
    path.unlink(missing_ok=True)
    try:
        writer = SqliteSpendStore(connection=sqlite3.connect(path))
        add(writer, tokens=1234)
        reader = SqliteSpendStore(connection=sqlite3.connect(path))
        assert reader.pr_total(REPO, 7) == 1234
    finally:
        path.unlink(missing_ok=True)


def test_a_failed_read_raises_supply_error() -> None:
    subject = store()
    subject._connection.close()
    try:
        subject.pr_total(REPO, 7)
    except SupplyError:
        return
    raise AssertionError("a storage fault must raise SupplyError")


def test_a_failed_write_raises_supply_error() -> None:
    subject = store()
    subject._connection.close()
    try:
        add(subject)
    except SupplyError:
        return
    raise AssertionError("a storage fault must raise SupplyError")


def test_a_supply_error_carries_no_value_the_store_was_handed() -> None:
    """RQA-NFR-025, and the Batch 2c lesson: a credential must not be recoverable from
    the exception's message, `args`, `__cause__` or `__context__`."""
    subject = store()
    subject._connection.close()
    secret = "ghp_" + "a" * 36
    try:
        subject.append(job_id="job-1", repo=REPO, number=7, model=secret, tokens=1,
                       measured=True, source=secret, recorded_at=utcnow())
    except SupplyError as exc:
        for view in (str(exc), repr(exc.args), str(exc.__cause__), repr(exc.__context__)):
            assert "ghp_" not in view
        return
    raise AssertionError("a storage fault must raise SupplyError")


# -- the two halves of this lane compose: consumed() feeds reserve() ----------------


def test_a_measured_spend_written_by_consumed_is_what_the_next_reserve_counts() -> None:
    """AC11 end to end within this half: the axes are summed from what was actually
    consumed — measured or estimated — never from a reservation."""
    subject = store()
    consume(reading=57_000, spend=subject)
    assert subject.pr_total(REPO, 7) == 57_000
    assert subject.model_total_since(PRIMARY.model, utcnow() - timedelta(hours=24)) == 57_000
