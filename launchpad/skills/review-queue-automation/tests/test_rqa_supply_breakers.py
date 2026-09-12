#!/usr/bin/env python3
"""`rqa.supply.breakers` — `code/P-05-reviewer-supply.md` §5's two tables, §7's no-reset
rule, and the half-open-on-read property T10 states parenthetically.

No pytest: every `test_*` function here takes no arguments, per `tests/run_all.py`.

Every test runs against an in-memory SQLite connection. Nothing here reaches a network, a
state directory or a credential.
"""

from __future__ import annotations

import inspect
import pathlib
import sqlite3
import sys
from datetime import datetime, timedelta, timezone

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from rqa.supply.breakers import (  # noqa: E402
    BREAKER_COOLDOWN,
    FAILURE_THRESHOLD,
    BreakerState,
    BreakerStore,
    SqliteBreakerStore,
    SupplyError,
    ensure_schema,
    utcnow,
)

KEY = "claude:anthropic:claude-sonnet-4-5"
SCOPE = "anthropic"


def store() -> SqliteBreakerStore:
    return SqliteBreakerStore(connection=sqlite3.connect(":memory:"))


def rows(subject: SqliteBreakerStore, table: str) -> list[tuple]:
    return list(subject._connection.execute(f"SELECT * FROM {table}").fetchall())


# -- §5's constants and shape ---------------------------------------------------


def test_the_breaker_constants_are_the_ones_section_five_states() -> None:
    assert FAILURE_THRESHOLD == 3
    assert BREAKER_COOLDOWN.total_seconds() == 900


def test_the_concrete_store_satisfies_the_protocol_signatures_verbatim() -> None:
    """§5's five methods, character-for-character — including the positional/keyword form
    each one documents."""
    for name in ("cooldown", "set_cooldown", "breaker", "record_failure", "record_success"):
        expected = inspect.signature(getattr(BreakerStore, name))
        actual = inspect.signature(getattr(SqliteBreakerStore, name))
        assert actual == expected, name


def test_the_protocol_states_section_fives_five_methods_and_no_more() -> None:
    declared = {name for name in vars(BreakerStore) if not name.startswith("_")}
    assert declared == {"cooldown", "set_cooldown", "breaker", "record_failure", "record_success"}


def test_the_two_tables_are_the_ones_section_five_declares() -> None:
    connection = sqlite3.connect(":memory:")
    ensure_schema(connection=connection)
    names = {
        row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")
    }
    assert {"providers", "circuit_breakers"} <= names


def test_the_schema_is_idempotent() -> None:
    connection = sqlite3.connect(":memory:")
    ensure_schema(connection=connection)
    ensure_schema(connection=connection)  # a second application is a no-op, not an error


# -- `providers`: the exact-route probe cooldown --------------------------------


def test_an_unknown_route_has_no_cooldown() -> None:
    assert store().cooldown(KEY) is None


def test_a_set_cooldown_reads_back_as_the_same_instant() -> None:
    subject = store()
    until = utcnow() + timedelta(seconds=300)
    subject.set_cooldown(KEY, until=until, error="probe failed")
    assert subject.cooldown(KEY) == until


def test_a_cleared_cooldown_reads_back_as_none() -> None:
    subject = store()
    subject.set_cooldown(KEY, until=utcnow() + timedelta(seconds=300), error="probe failed")
    subject.set_cooldown(KEY, until=None, error="")
    assert subject.cooldown(KEY) is None


def test_one_route_per_row_so_a_sibling_model_keeps_its_own_cooldown() -> None:
    subject = store()
    subject.set_cooldown(KEY, until=utcnow() + timedelta(seconds=300), error="probe failed")
    assert subject.cooldown("claude:anthropic:claude-opus-4-5") is None


def test_an_unparseable_cooldown_deadline_is_treated_as_expired() -> None:
    """§7: an unparseable deadline never pins a route out of service."""
    subject = store()
    subject._connection.execute(
        "INSERT INTO providers(key,unavailable_until,last_error,updated_at) VALUES(?,?,?,?)",
        (KEY, "not-a-timestamp", "", "2026-09-12T09:00:00+00:00"),
    )
    assert subject.cooldown(KEY) is None


def test_a_legacy_z_suffixed_deadline_is_read_not_discarded() -> None:
    """The incumbent wrote `...Z` (`scripts/budget.py:292`); a carried row still parses."""
    subject = store()
    subject._connection.execute(
        "INSERT INTO providers(key,unavailable_until,last_error,updated_at) VALUES(?,?,?,?)",
        (KEY, "2099-01-01T00:00:00Z", "", "2026-09-12T09:00:00+00:00"),
    )
    assert subject.cooldown(KEY) == datetime(2099, 1, 1, tzinfo=timezone.utc)


def test_a_cooldown_survives_the_connection_that_wrote_it() -> None:
    """Each scheduled tick is a separate process, so an in-memory flag would re-probe a
    dead route on every job (U-POLICY-13's reasoning for persisting)."""
    path = pathlib.Path(__file__).resolve().parent / "_breakers_probe.sqlite3"
    path.unlink(missing_ok=True)
    try:
        until = utcnow() + timedelta(seconds=300)
        SqliteBreakerStore(connection=sqlite3.connect(path)).set_cooldown(
            KEY, until=until, error="probe failed"
        )
        assert SqliteBreakerStore(connection=sqlite3.connect(path)).cooldown(KEY) == until
    finally:
        path.unlink(missing_ok=True)


# -- `circuit_breakers`: the per-family breaker ---------------------------------


def test_an_unknown_scope_is_closed_with_no_failures() -> None:
    assert store().breaker(SCOPE) == BreakerState(
        scope=SCOPE, failures=0, status="closed", open_until=None
    )


def test_failures_below_the_threshold_leave_the_breaker_closed() -> None:
    subject = store()
    for expected in range(1, FAILURE_THRESHOLD):
        state = subject.record_failure(SCOPE, "provider terminal")
        assert state == BreakerState(scope=SCOPE, failures=expected, status="closed", open_until=None)


def test_the_threshold_failure_opens_the_breaker_for_the_cooldown() -> None:
    subject = store()
    before = utcnow()
    for _ in range(FAILURE_THRESHOLD):
        state = subject.record_failure(SCOPE, "provider terminal")
    assert state.status == "open"
    assert state.failures == FAILURE_THRESHOLD
    assert before + BREAKER_COOLDOWN <= state.open_until <= utcnow() + BREAKER_COOLDOWN


def test_an_open_breaker_reads_back_open_while_its_deadline_is_live() -> None:
    subject = store()
    for _ in range(FAILURE_THRESHOLD):
        subject.record_failure(SCOPE, "provider terminal")
    assert subject.breaker(SCOPE).status == "open"


def test_a_success_closes_the_breaker_and_clears_the_count() -> None:
    subject = store()
    for _ in range(FAILURE_THRESHOLD):
        subject.record_failure(SCOPE, "provider terminal")
    assert subject.record_success(SCOPE) == BreakerState(
        scope=SCOPE, failures=0, status="closed", open_until=None
    )
    assert subject.breaker(SCOPE).status == "closed"


def test_failures_are_counted_per_scope_and_never_shared() -> None:
    subject = store()
    for _ in range(FAILURE_THRESHOLD):
        subject.record_failure(SCOPE, "provider terminal")
    assert subject.breaker("openai") == BreakerState(
        scope="openai", failures=0, status="closed", open_until=None
    )


# -- half-open on read, and never a write on read -------------------------------


def seed_open(subject: SqliteBreakerStore, *, open_until: str) -> None:
    subject._connection.execute(
        "INSERT INTO circuit_breakers(scope,failures,status,open_until,last_error,updated_at) "
        "VALUES(?,?,?,?,?,?)",
        (SCOPE, FAILURE_THRESHOLD, "open", open_until, "provider terminal", "2026-09-12T09:00:00+00:00"),
    )


def test_an_expired_open_row_half_opens_on_read() -> None:
    subject = store()
    seed_open(subject, open_until=(utcnow() - timedelta(minutes=1)).isoformat())
    state = subject.breaker(SCOPE)
    assert state.status == "closed"
    assert state.open_until is None
    assert state.failures == FAILURE_THRESHOLD  # the count survives the half-open


def test_the_half_open_read_writes_nothing() -> None:
    """§5, U-DISPATCH-05: `breaker()` never writes on read. The row is byte-identical
    afterwards, so nothing a later reader sees was decided by this read."""
    subject = store()
    seed_open(subject, open_until=(utcnow() - timedelta(minutes=1)).isoformat())
    before = rows(subject, "circuit_breakers")
    subject.breaker(SCOPE)
    subject.breaker(SCOPE)
    assert rows(subject, "circuit_breakers") == before


def test_a_half_open_breaker_re_opens_on_the_very_next_failure() -> None:
    subject = store()
    seed_open(subject, open_until=(utcnow() - timedelta(minutes=1)).isoformat())
    state = subject.record_failure(SCOPE, "provider terminal")
    assert state.status == "open"
    assert state.failures == FAILURE_THRESHOLD + 1


def test_an_unparseable_open_until_is_treated_as_expired() -> None:
    """§7: a bad timestamp must not pin a provider family out of service forever."""
    subject = store()
    seed_open(subject, open_until="not-a-timestamp")
    assert subject.breaker(SCOPE).status == "closed"


def test_a_missing_open_until_on_an_open_row_is_treated_as_expired() -> None:
    subject = store()
    seed_open(subject, open_until="")
    assert subject.breaker(SCOPE).status == "closed"


# -- §7: there is no reset --------------------------------------------------------


def test_the_store_offers_no_manual_reset_of_either_table() -> None:
    """§7, U-DISPATCH-05 (`bin`): the responsibility goes away. The only ways back are a
    passing probe, a `consumed()` outcome, or the stored deadline passing."""
    surface = {name for name in dir(SqliteBreakerStore) if not name.startswith("_")}
    assert surface == {"cooldown", "set_cooldown", "breaker", "record_failure", "record_success"}
    for forbidden in ("reset", "clear", "unlock", "reopen", "purge"):
        assert not any(forbidden in name for name in surface), forbidden


def test_no_row_is_ever_deleted_from_either_table() -> None:
    source = (pathlib.Path(__file__).resolve().parent.parent / "rqa/supply/breakers.py").read_text(
        encoding="utf-8"
    )
    assert "DELETE" not in source.upper().replace("DELETED", "")


# -- storage faults are `SupplyError`, never a routing value ----------------------


def test_a_failed_read_raises_supply_error() -> None:
    subject = store()
    subject._connection.close()
    try:
        subject.breaker(SCOPE)
    except SupplyError:
        return
    raise AssertionError("a storage fault must raise SupplyError")


def test_a_failed_write_raises_supply_error() -> None:
    subject = store()
    subject._connection.close()
    try:
        subject.set_cooldown(KEY, until=None, error="")
    except SupplyError:
        return
    raise AssertionError("a storage fault must raise SupplyError")


def test_a_supply_error_names_the_scope_and_carries_nothing_else() -> None:
    """`RQA-NFR-025`: an error message is a place a secret can end up. This one holds the
    scope and the operation, and no value it was handed."""
    subject = store()
    subject._connection.close()
    try:
        subject.set_cooldown(KEY, until=None, error="ghp_" + "a" * 36)
    except SupplyError as exc:
        assert KEY in str(exc)
        assert "ghp_" not in str(exc)
        assert "ghp_" not in str(exc.__cause__)
        return
    raise AssertionError("a storage fault must raise SupplyError")
