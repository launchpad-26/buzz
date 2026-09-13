#!/usr/bin/env python3
"""`migrate_legacy` — `code/P-12-record.md` §6's migration mapping and §8 row T10.

No pytest: every `test_*` function here takes no arguments, per `tests/run_all.py`.

`FakeLegacySource` is the fixture `LegacySource` names in its own docstring: a
narrow, read-only stand-in for the three pre-cutover tables, so this module never
depends on a real `scripts/common.py`-backed database.
"""

from __future__ import annotations

import json
import pathlib
import sqlite3
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from rqa.record.hashing import LEGACY_PREV_HASH  # noqa: E402
from rqa.record.migrate import MigrationSummary, migrate_legacy  # noqa: E402


class FakeLegacySource:
    """One fixture row per table, matching `scripts/common.py`'s column shapes."""

    def __init__(self, *, ledger=None, approvals=None, costs=None):
        self._ledger = ledger if ledger is not None else []
        self._approvals = approvals if approvals is not None else []
        self._costs = costs if costs is not None else []

    def ledger_entries(self):
        return iter(self._ledger)

    def approval_decisions(self):
        return iter(self._approvals)

    def cost_ledger(self):
        return iter(self._costs)


def stored_rows(connection: sqlite3.Connection, job: str) -> list[tuple]:
    cursor = connection.execute(
        "SELECT job, seq, kind, at, payload, prev_hash, hash, hmac, keyed "
        "FROM record_entries WHERE job = ? ORDER BY seq",
        (job,),
    )
    return [tuple(row) for row in cursor.fetchall()]


def one_of_each() -> FakeLegacySource:
    return FakeLegacySource(
        ledger=[
            {
                "id": 101,
                "job_id": "legacy-job-1",
                "repo": "acme/widgets",
                "number": 7,
                "head_sha": "sha-ledger",
                "recorded_at": "2025-06-01T00:00:00Z",
                "kind": "finding",
                "entry_key": "finding-1",
                "payload": json.dumps({"note": "an old finding"}),
                "snapshot_hash": "old-snap",
                "policy_version": "old-policy",
            }
        ],
        approvals=[
            {
                "id": "appr-1",
                "job_id": "legacy-job-1",
                "repo": "acme/widgets",
                "number": 7,
                "head_sha": "sha-ledger",
                "policy_hash": "old-policy-hash",
                "status": "approved",
                "mode": "live",
                "risk_score": 3,
                "created_at": "2025-06-01T00:01:00Z",
                "expires_at": None,
            }
        ],
        costs=[
            {
                "id": 201,
                "recorded_at": "2025-06-01T00:02:00Z",
                "job_id": "legacy-job-1",
                "repo": "acme/widgets",
                "number": 7,
                "model": "gpt-old",
                "provider_family": "openai",
                "kind": "review",
                "tokens": 4096,
                "latency_ms": 1500,
            }
        ],
    )


# -- T10 -----------------------------------------------------------------------


def test_t10_one_fixture_row_from_each_table_migrates_to_the_documented_kinds() -> None:
    """T10: one fixture row from each of `ledger_entries`, `approval_decisions`,
    `cost_ledger` → `migrate_legacy` produces exactly: `kind="legacy"` with
    `legacy_kind`/`fields` set; `kind="decision"` with `actor="unknown"`;
    `kind="spend"` with `measured=False` — each with `prev_hash="legacy"`."""
    connection = sqlite3.connect(":memory:")
    summary = migrate_legacy(connection=connection, source=one_of_each())

    assert isinstance(summary, MigrationSummary)
    assert (summary.ledger_entries.migrated, summary.ledger_entries.already_done) == (1, False)
    assert (summary.approval_decisions.migrated, summary.approval_decisions.already_done) == (1, False)
    assert (summary.cost_ledger.migrated, summary.cost_ledger.already_done) == (1, False)

    rows = stored_rows(connection, "legacy-job-1")
    assert len(rows) == 3
    for row in rows:
        assert row[5] == LEGACY_PREV_HASH  # prev_hash
        assert row[7] is None  # hmac
        assert row[8] == 0  # keyed

    by_kind = {row[2]: json.loads(row[4]) for row in rows}

    legacy_payload = by_kind["legacy"]
    assert legacy_payload["source_table"] == "ledger_entries"
    assert legacy_payload["legacy_kind"] == "finding"
    assert legacy_payload["fields"]["repo"] == "acme/widgets"
    # "fields" carries the original columns verbatim — the legacy `payload` column
    # was itself already JSON text, so it stays text here rather than being reparsed.
    assert json.loads(legacy_payload["fields"]["payload"]) == {"note": "an old finding"}

    decision_payload = by_kind["decision"]
    assert decision_payload["source_table"] == "approval_decisions"
    assert decision_payload["actor"] == "unknown"
    assert decision_payload["outcome"] == "approved"
    assert "status=approved" in decision_payload["basis"]

    spend_payload = by_kind["spend"]
    assert spend_payload["source_table"] == "cost_ledger"
    assert spend_payload["measured"] is False
    assert spend_payload["tokens"] == 4096
    assert spend_payload["route"] == {"harness": None, "model": "gpt-old", "provider": "openai"}


def test_t10_distinct_sequences_are_assigned_for_the_same_job_key() -> None:
    """All three fixture rows share `job_id="legacy-job-1"`; `(job, seq)` is
    unique, so each migrated row must land on its own sequence."""
    connection = sqlite3.connect(":memory:")
    migrate_legacy(connection=connection, source=one_of_each())
    rows = stored_rows(connection, "legacy-job-1")
    seqs = sorted(row[1] for row in rows)
    assert seqs == [1, 2, 3]


# -- idempotency and per-table skippability -------------------------------------


def test_migration_is_idempotent_on_retry() -> None:
    connection = sqlite3.connect(":memory:")
    first = migrate_legacy(connection=connection, source=one_of_each())
    assert first.ledger_entries.migrated == 1

    second = migrate_legacy(connection=connection, source=one_of_each())
    assert (second.ledger_entries.migrated, second.ledger_entries.already_done) == (0, True)
    assert (second.approval_decisions.migrated, second.approval_decisions.already_done) == (0, True)
    assert (second.cost_ledger.migrated, second.cost_ledger.already_done) == (0, True)

    # No duplicate rows were inserted on the retry.
    assert len(stored_rows(connection, "legacy-job-1")) == 3


def test_each_table_is_independently_skippable() -> None:
    """A table already migrated is skipped even when the other two are not yet
    done — §6: "each table's migration is independently skippable on retry"."""
    connection = sqlite3.connect(":memory:")
    only_ledger = FakeLegacySource(ledger=one_of_each()._ledger)
    first = migrate_legacy(connection=connection, source=only_ledger)
    assert first.ledger_entries.already_done is False
    assert first.approval_decisions.migrated == 0 and first.approval_decisions.already_done is False
    assert first.cost_ledger.migrated == 0 and first.cost_ledger.already_done is False

    second = migrate_legacy(connection=connection, source=one_of_each())
    assert second.ledger_entries.already_done is True
    assert second.approval_decisions.already_done is False and second.approval_decisions.migrated == 1
    assert second.cost_ledger.already_done is False and second.cost_ledger.migrated == 1


def test_migration_with_nothing_to_migrate_is_a_no_op() -> None:
    connection = sqlite3.connect(":memory:")
    summary = migrate_legacy(connection=connection, source=FakeLegacySource())
    assert summary.ledger_entries.migrated == 0 and summary.ledger_entries.already_done is False
    assert connection.execute("SELECT COUNT(*) FROM record_entries").fetchone()[0] == 0


# -- approval_decisions without a job_id ----------------------------------------


def test_an_approval_decision_with_no_job_id_gets_a_synthetic_job_key() -> None:
    """§6: the migrated `job` key is the old `job_id` if not `NULL`, else
    `f"legacy:approval_decisions:{id}"`."""
    connection = sqlite3.connect(":memory:")
    source = FakeLegacySource(
        approvals=[
            {
                "id": "appr-orphan",
                "job_id": None,
                "repo": "acme/widgets",
                "number": 9,
                "head_sha": "sha-orphan",
                "policy_hash": "hash",
                "status": "changes_requested",
                "mode": "live",
                "risk_score": 5,
                "created_at": "2025-06-02T00:00:00Z",
                "expires_at": None,
            }
        ]
    )
    migrate_legacy(connection=connection, source=source)
    rows = stored_rows(connection, "legacy:approval_decisions:appr-orphan")
    assert len(rows) == 1
    payload = json.loads(rows[0][4])
    assert payload["outcome"] == "changes_requested"


def test_an_approval_decision_with_an_empty_string_job_id_keeps_its_own_key() -> None:
    """F4: §6 says "old `job_id` if not `NULL`" — a specific test against SQL `NULL`,
    not general falsiness. An empty string is a valid, non-NULL `TEXT` value and
    must keep its own job id rather than falling into the synthetic-key branch."""
    connection = sqlite3.connect(":memory:")
    source = FakeLegacySource(
        approvals=[
            {
                "id": "appr-empty",
                "job_id": "",
                "repo": "acme/widgets",
                "number": 11,
                "head_sha": "sha-empty",
                "policy_hash": "hash",
                "status": "approved",
                "mode": "live",
                "risk_score": 1,
                "created_at": "2025-06-03T00:00:00Z",
                "expires_at": None,
            }
        ]
    )
    migrate_legacy(connection=connection, source=source)
    # Kept its own (empty-string) job id, not the synthetic fallback key.
    assert stored_rows(connection, "") != []
    assert stored_rows(connection, "legacy:approval_decisions:appr-empty") == []
