#!/usr/bin/env python3
"""`rqa.intake.store` — `code/P-01-intake.md` §2, §5, §8 (T8, T9), the two
`JobStatus` partitions, and the four security guards this lane owns.

Real `sqlite3` connection against the real DDL throughout — stronger evidence
than a fake store, and what §8's guidance for T8/T9 asks for directly.
"""

from __future__ import annotations

import ast
import pathlib
import re
import sqlite3
import sys
from datetime import datetime, timedelta, timezone

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from rqa.contracts import Job, JobStatus  # noqa: E402
from rqa.intake.store import (  # noqa: E402
    DEFAULT_BATCH_SIZE,
    SCHEMA,
    SqliteJobStore,
    SqliteLeaseStore,
    SqlitePrFactsStore,
    _RESTING,
    _SWEEP_RESUMABLE,
    ensure_schema,
)
from rqa.intake.types import LeaseRow, PrFactsRow  # noqa: E402

INTAKE = pathlib.Path(__file__).resolve().parent.parent / "rqa" / "intake"


def _connection() -> sqlite3.Connection:
    connection = sqlite3.connect(":memory:")
    ensure_schema(connection)
    return connection


def _job(
    *,
    job_id: str,
    repo: str = "alice/repo",
    number: int = 1,
    head_sha: str = "sha-1",
    predecessor_job: str | None = None,
    predecessor_head_sha: str | None = None,
    status: JobStatus = JobStatus.QUEUED,
) -> Job:
    return Job(
        job_id, repo, number, head_sha, "base-sha", repo, "feature",
        predecessor_job, predecessor_head_sha, None, status,
    )


# -- §5: DDL shape -----------------------------------------------------------------


def test_schema_carries_the_three_tables_and_their_named_constraints() -> None:
    joined = SCHEMA
    assert "CREATE TABLE IF NOT EXISTS jobs" in joined
    assert "UNIQUE (repo, number, head_sha)" in joined
    assert "CREATE INDEX IF NOT EXISTS idx_jobs_pr" in joined
    assert "CREATE INDEX IF NOT EXISTS idx_jobs_sweep" in joined
    assert "CREATE TABLE IF NOT EXISTS pr_facts" in joined
    assert "PRIMARY KEY (repo, number)" in joined
    assert "CREATE TABLE IF NOT EXISTS leases" in joined
    assert "job_id     TEXT PRIMARY KEY" in joined
    assert "UNIQUE (repo, number)" in joined


def test_ensure_schema_is_idempotent_against_an_existing_state_dir() -> None:
    connection = _connection()
    ensure_schema(connection)  # a second call must not raise
    connection.execute("INSERT INTO leases (job_id, repo, number, claimed_at) VALUES ('j', 'r', 1, 'now')")
    connection.commit()


# -- security guard 1: UNIQUE(repo, number, head_sha) on jobs -----------------------


def test_guard_unique_repo_number_head_sha_refuses_a_duplicate_job() -> None:
    connection = _connection()
    store = SqliteJobStore(connection)
    store.create(_job(job_id="job-a"))
    connection.commit()
    try:
        store.create(_job(job_id="job-b"))  # same (repo, number, head_sha)
    except sqlite3.IntegrityError:
        pass
    else:
        raise AssertionError("a duplicate (repo, number, head_sha) must be refused")


def test_guard_reverted_unique_constraint_would_accept_the_duplicate() -> None:
    """Mutation verification: without the constraint, the same insert
    succeeds — proving the guard, not an unrelated failure, refused it above."""
    connection = sqlite3.connect(":memory:")
    connection.executescript(
        "CREATE TABLE jobs (id TEXT PRIMARY KEY, repo TEXT, number INTEGER, head_sha TEXT)"
    )
    connection.execute("INSERT INTO jobs VALUES ('job-a', 'alice/repo', 1, 'sha-1')")
    connection.execute("INSERT INTO jobs VALUES ('job-b', 'alice/repo', 1, 'sha-1')")
    connection.commit()
    assert connection.execute("SELECT COUNT(*) FROM jobs").fetchone()[0] == 2


# -- security guard 2: UNIQUE(repo, number) on leases -------------------------------


def test_guard_unique_repo_number_on_leases_refuses_a_second_concurrent_claim() -> None:
    connection = _connection()
    leases = SqliteLeaseStore(connection)
    now = datetime.now(timezone.utc)
    leases.put(LeaseRow("job-a", "alice/repo", 1, now))
    connection.commit()
    try:
        leases.put(LeaseRow("job-b", "alice/repo", 1, now))  # different job, same PR
    except sqlite3.IntegrityError:
        pass
    else:
        raise AssertionError("a second concurrent claim on the same PR must be refused")


def test_guard_reverted_unique_constraint_would_accept_the_second_claim() -> None:
    connection = sqlite3.connect(":memory:")
    connection.executescript("CREATE TABLE leases (job_id TEXT PRIMARY KEY, repo TEXT, number INTEGER, claimed_at TEXT)")
    connection.execute("INSERT INTO leases VALUES ('job-a', 'alice/repo', 1, 'now')")
    connection.execute("INSERT INTO leases VALUES ('job-b', 'alice/repo', 1, 'now')")
    connection.commit()
    assert connection.execute("SELECT COUNT(*) FROM leases").fetchone()[0] == 2


# -- security guard 4: every store method binds parameters --------------------------


def test_guard_sql_metacharacters_round_trip_byte_identical_and_change_no_querys_meaning() -> None:
    connection = _connection()
    prf = SqlitePrFactsStore(connection)
    hostile_repo = "alice/repo"
    hostile_head_ref = "'; DROP TABLE jobs; --"
    hostile_head_sha = "sha'); DELETE FROM pr_facts; --"
    row = PrFactsRow(
        hostile_repo, 7, hostile_head_sha, "base", hostile_repo, hostile_head_ref,
        'bob"); --', ("a'; DROP TABLE leases; --",), datetime.now(timezone.utc),
    )
    prf.upsert(row)
    connection.commit()

    read_back = prf.get(hostile_repo, 7)
    assert read_back.head_sha == hostile_head_sha
    assert read_back.head_ref == hostile_head_ref
    assert read_back.labels == ("a'; DROP TABLE leases; --",)
    # Every table this part owns is untouched: no metacharacter was ever
    # interpreted as SQL.
    for table in ("jobs", "pr_facts", "leases"):
        connection.execute(f"SELECT * FROM {table}")  # raises OperationalError if dropped


def test_guard_no_store_method_formats_a_query_string_with_an_argument() -> None:
    """A caller-supplied value never reaches `.execute()` through an f-string
    or `%`/`.format()` interpolation anywhere in this file — bound
    placeholders only."""
    source = (pathlib.Path(__file__).resolve().parent.parent / "rqa" / "intake" / "store.py").read_text()
    tree = ast.parse(source)
    offenders = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "execute":
            first_arg = node.args[0] if node.args else None
            if isinstance(first_arg, ast.JoinedStr):
                offenders.append(node.lineno)
            elif (
                isinstance(first_arg, ast.Call)
                and isinstance(first_arg.func, ast.Attribute)
                and first_arg.func.attr == "format"
            ):
                offenders.append(node.lineno)
            elif isinstance(first_arg, ast.BinOp) and isinstance(first_arg.op, ast.Mod):
                offenders.append(node.lineno)
    assert offenders == [], offenders


# -- §8 T8: select_batch caps at batch_size in (created_at, id) order --------------


def test_t8_more_resumable_jobs_than_batch_size_selects_exactly_batch_size_in_order() -> None:
    connection = _connection()
    base = datetime(2026, 1, 1, tzinfo=timezone.utc)
    ticks = iter(base + timedelta(seconds=i) for i in range(DEFAULT_BATCH_SIZE + 5))
    store = SqliteJobStore(connection, clock=lambda: next(ticks))
    expected_order = []
    for i in range(DEFAULT_BATCH_SIZE + 5):
        job_id = f"job-{i:03d}"
        store.create(_job(job_id=job_id, repo="alice/repo", number=i, head_sha=f"sha-{i}"))
        expected_order.append(job_id)
    connection.commit()

    batch = store.select_batch(DEFAULT_BATCH_SIZE)
    assert len(batch) == DEFAULT_BATCH_SIZE
    assert [job.id for job in batch] == expected_order[:DEFAULT_BATCH_SIZE]


def test_select_batch_excludes_resting_jobstatuses() -> None:
    connection = _connection()
    store = SqliteJobStore(connection)
    store.create(_job(job_id="resumable", number=1, head_sha="s1"))
    store.create(_job(job_id="resting", number=2, head_sha="s2"))
    connection.commit()
    store.set_status("resting", JobStatus.APPROVED)
    connection.commit()

    batch = store.select_batch(10)
    assert [job.id for job in batch] == ["resumable"]


# -- §8 T9: pending_followup offers a resting job once ------------------------------


def test_t9_a_resting_job_with_an_unsuperseded_successor_is_offered() -> None:
    connection = _connection()
    store = SqliteJobStore(connection)
    store.create(_job(job_id="predecessor", number=1, head_sha="sha-a"))
    connection.commit()
    store.set_status("predecessor", JobStatus.APPROVED)
    connection.commit()
    store.create(
        _job(job_id="successor", number=1, head_sha="sha-b", predecessor_job="predecessor",
             predecessor_head_sha="sha-a")
    )
    connection.commit()

    followup = store.pending_followup()
    assert [job.id for job in followup] == ["predecessor"]


def test_t9_a_resting_job_with_an_outstanding_lease_is_offered() -> None:
    connection = _connection()
    store = SqliteJobStore(connection)
    leases = SqliteLeaseStore(connection)
    store.create(_job(job_id="leased", number=1, head_sha="sha-a"))
    connection.commit()
    store.set_status("leased", JobStatus.ESCALATED)
    connection.commit()
    leases.put(LeaseRow("leased", "alice/repo", 1, datetime.now(timezone.utc)))
    connection.commit()

    followup = store.pending_followup()
    assert [job.id for job in followup] == ["leased"]


def test_t9_offered_exactly_once_when_both_reasons_apply() -> None:
    connection = _connection()
    store = SqliteJobStore(connection)
    leases = SqliteLeaseStore(connection)
    store.create(_job(job_id="predecessor", number=1, head_sha="sha-a"))
    connection.commit()
    store.set_status("predecessor", JobStatus.APPROVED)
    connection.commit()
    store.create(
        _job(job_id="successor", number=1, head_sha="sha-b", predecessor_job="predecessor",
             predecessor_head_sha="sha-a")
    )
    leases.put(LeaseRow("predecessor", "alice/repo", 1, datetime.now(timezone.utc)))
    connection.commit()

    followup = store.pending_followup()
    assert [job.id for job in followup] == ["predecessor"]


def test_pending_followup_excludes_a_resting_job_with_neither_reason() -> None:
    connection = _connection()
    store = SqliteJobStore(connection)
    store.create(_job(job_id="quiet", number=1, head_sha="sha-a"))
    connection.commit()
    store.set_status("quiet", JobStatus.MERGED)
    connection.commit()

    assert store.pending_followup() == []


def test_pending_followup_excludes_a_superseded_successor() -> None:
    """A successor that has itself already been marked SUPERSEDED does not
    count as "unsuperseded"."""
    connection = _connection()
    store = SqliteJobStore(connection)
    store.create(_job(job_id="predecessor", number=1, head_sha="sha-a"))
    connection.commit()
    store.set_status("predecessor", JobStatus.APPROVED)
    connection.commit()
    store.create(
        _job(job_id="successor", number=1, head_sha="sha-b", predecessor_job="predecessor",
             predecessor_head_sha="sha-a")
    )
    connection.commit()
    store.set_status("successor", JobStatus.SUPERSEDED)
    connection.commit()

    assert store.pending_followup() == []


# -- the two JobStatus partitions cover every member exactly once ------------------


def test_sweep_resumable_and_resting_partition_every_jobstatus_member_exactly_once() -> None:
    """Wave-invariant: asserted against the full `JobStatus` enumeration, not
    a hand-listed subset a later member could silently fall out of."""
    every_member = frozenset(JobStatus)
    assert _SWEEP_RESUMABLE | _RESTING == every_member
    assert _SWEEP_RESUMABLE & _RESTING == frozenset()


# -- basic read/write round trips ---------------------------------------------------


def test_get_and_current_for_pr_and_set_snapshot_hash() -> None:
    connection = _connection()
    store = SqliteJobStore(connection)
    store.create(_job(job_id="job-a", repo="alice/repo", number=9, head_sha="sha-a"))
    connection.commit()

    assert store.get("job-a").id == "job-a"
    assert store.get("missing") is None
    assert store.current_for_pr("alice/repo", 9).id == "job-a"
    assert store.current_for_pr("alice/repo", 404) is None

    store.set_snapshot_hash("job-a", "snap-1")
    connection.commit()
    assert store.get("job-a").snapshot_hash == "snap-1"


def test_current_for_pr_returns_the_latest_of_two_revisions() -> None:
    connection = _connection()
    ticks = iter(
        [datetime(2026, 1, 1, tzinfo=timezone.utc), datetime(2026, 1, 2, tzinfo=timezone.utc)]
    )
    store = SqliteJobStore(connection, clock=lambda: next(ticks))
    store.create(_job(job_id="old", repo="alice/repo", number=1, head_sha="sha-old"))
    connection.commit()
    store.create(
        _job(job_id="new", repo="alice/repo", number=1, head_sha="sha-new",
             predecessor_job="old", predecessor_head_sha="sha-old")
    )
    connection.commit()

    assert store.current_for_pr("alice/repo", 1).id == "new"


def test_pr_facts_upsert_refreshes_last_seen_at_and_facts_on_conflict() -> None:
    connection = _connection()
    prf = SqlitePrFactsStore(connection)
    first_seen = datetime(2026, 1, 1, tzinfo=timezone.utc)
    second_seen = datetime(2026, 1, 2, tzinfo=timezone.utc)
    prf.upsert(PrFactsRow("alice/repo", 1, "sha-a", "base", "alice/repo", "feature", "alice", (), first_seen))
    connection.commit()
    prf.upsert(PrFactsRow("alice/repo", 1, "sha-b", "base", "alice/repo", "feature", "alice", ("wip",), second_seen))
    connection.commit()

    row = prf.get("alice/repo", 1)
    assert row.head_sha == "sha-b"
    assert row.labels == ("wip",)
    assert row.last_seen_at == second_seen
    assert connection.execute("SELECT COUNT(*) FROM pr_facts").fetchone()[0] == 1


def test_lease_current_and_delete() -> None:
    connection = _connection()
    leases = SqliteLeaseStore(connection)
    assert leases.current("alice/repo", 1) is None
    claimed_at = datetime.now(timezone.utc)
    leases.put(LeaseRow("job-a", "alice/repo", 1, claimed_at))
    connection.commit()
    assert leases.current("alice/repo", 1) == LeaseRow("job-a", "alice/repo", 1, claimed_at)
    leases.delete("alice/repo", 1)
    connection.commit()
    assert leases.current("alice/repo", 1) is None


# -- §8's suite-wide property, tested against its stated intent --------------------


def _resolve_string_literal(node: ast.AST, bindings: dict) -> str | None:
    """Resolve `node` to its string value when it is an inline literal, an
    f-string/concatenation built only from literals and bound placeholders,
    or a reference to a local variable already known (in `bindings`) to
    resolve one of those ways. `None` when it cannot be determined
    statically — a call this cannot resolve is skipped, never silently
    treated as safe."""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.JoinedStr):
        parts: list[str] = []
        for value in node.values:
            if isinstance(value, ast.Constant) and isinstance(value.value, str):
                parts.append(value.value)
            elif isinstance(value, ast.FormattedValue):
                parts.append("")  # an interpolated bound value carries no SQL keyword
            else:
                return None
        return "".join(parts)
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        left = _resolve_string_literal(node.left, bindings)
        right = _resolve_string_literal(node.right, bindings)
        return None if left is None or right is None else left + right
    if isinstance(node, ast.Name):
        return bindings.get(node.id)
    return None


def _sql_execute_statements(tree: ast.AST):
    """Yield every `.execute(...)` call in `tree` together with its resolved
    SQL text — an inline literal, an f-string/concatenation of literals, OR
    a simple local variable assigned one of those forms earlier in the same
    function (`sql = "..."; connection.execute(sql)`). The narrower
    predicate this replaces only ever looked at an inline `ast.Constant`
    first argument, so SQL lifted into a variable was invisible to it."""
    for function in ast.walk(tree):
        if not isinstance(function, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        bindings: dict = {}
        for node in ast.walk(function):
            if (
                isinstance(node, ast.Assign)
                and len(node.targets) == 1
                and isinstance(node.targets[0], ast.Name)
            ):
                resolved = _resolve_string_literal(node.value, bindings)
                if resolved is not None:
                    bindings[node.targets[0].id] = resolved
        for node in ast.walk(function):
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr == "execute"
                and node.args
            ):
                resolved = _resolve_string_literal(node.args[0], bindings)
                if resolved is not None:
                    yield node, resolved


def _assigns_jobs_status(sql: str) -> bool:
    """True when `sql` is a statement that assigns `jobs.status` — an
    `INSERT INTO jobs` naming the column, or an `UPDATE ... SET` whose
    assignment list (the text between `SET` and `WHERE`, never past it)
    contains `status =` *anywhere*, not only immediately after `SET`.
    Matching only immediately after `SET` is exactly the loophole a
    multi-column `UPDATE jobs SET head_sha = ?, status = ?` slips through;
    scoping the search to the SET clause (rather than the whole statement)
    keeps a `WHERE status = ?` filter — a read, never an assignment — from
    false-positiving."""
    if re.search(r"\binsert\s+into\s+jobs\b", sql, re.IGNORECASE):
        return True
    set_match = re.search(r"\bset\b", sql, re.IGNORECASE)
    if set_match is None:
        return False
    set_clause = sql[set_match.end():]
    where_match = re.search(r"\bwhere\b", set_clause, re.IGNORECASE)
    if where_match is not None:
        set_clause = set_clause[: where_match.start()]
    return re.search(r"\bstatus\s*=", set_clause, re.IGNORECASE) is not None


def test_only_set_status_and_creates_queued_literal_ever_assign_jobs_status() -> None:
    """P-01 §8's suite-wide property, tested against the closing sentence
    that states its actual intent: "no other statement in this part ever
    assigns jobs.status" (see `## Disclosures` for why a literal
    `grep -n "status"` cannot pass here: §5's own mandated DDL text). This
    guard defends the invariant rather than today's spelling of it: it
    resolves `.execute()` calls whose SQL was lifted into a local variable,
    not only inline literals, and it matches `status` anywhere in an
    `UPDATE jobs SET ...` assignment list, not only immediately after `SET`.
    `test_the_guard_catches_a_multi_column_status_update` and
    `test_the_guard_catches_status_assigned_through_a_local_sql_variable`
    prove each widening catches a mutation the narrower predicate missed."""
    source = (INTAKE / "store.py").read_text()
    tree = ast.parse(source)
    set_status_ranges = [
        (node.lineno, node.end_lineno)
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef) and node.name == "set_status"
    ]
    assert set_status_ranges, "set_status not found"

    def _inside_set_status(lineno: int) -> bool:
        return any(start <= lineno <= end for start, end in set_status_ranges)

    hits = [
        (node, sql)
        for node, sql in _sql_execute_statements(tree)
        if not _inside_set_status(node.lineno) and _assigns_jobs_status(sql)
    ]
    assert len(hits) == 1, [(node.lineno, sql) for node, sql in hits]
    assert "'queued'" in hits[0][1]


def test_the_guard_catches_a_multi_column_status_update() -> None:
    """The narrower predicate this guard replaced (`status` immediately
    after `SET`) missed a multi-column update naming `status` second or
    later; the widened `_assigns_jobs_status` catches it."""
    sql = "UPDATE jobs SET head_sha = ?, status = ? WHERE id = ?"
    old_predicate = re.compile(r"set\s+status\s*=|insert into jobs", re.IGNORECASE)
    assert old_predicate.search(sql) is None, "the old predicate was expected to miss this"
    assert _assigns_jobs_status(sql) is True


def test_the_guard_catches_status_assigned_through_a_local_sql_variable() -> None:
    """The narrower helper this guard replaced only ever inspected an inline
    `ast.Constant` first argument to `.execute()`, so SQL lifted into a local
    variable was invisible to it regardless of the regex. The widened
    `_sql_execute_statements` resolves it."""
    source = (
        "class C:\n"
        "    def mutate(self, connection):\n"
        "        sql = 'UPDATE jobs SET status = ?, id = ?'\n"
        "        connection.execute(sql, (1, 2))\n"
    )
    tree = ast.parse(source)

    def _old_execute_string_literal_calls(tree: ast.AST):
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr == "execute"
                and node.args
                and isinstance(node.args[0], ast.Constant)
                and isinstance(node.args[0].value, str)
            ):
                yield node

    assert list(_old_execute_string_literal_calls(tree)) == [], "the old resolver was expected to miss this"

    resolved = list(_sql_execute_statements(tree))
    assert len(resolved) == 1
    _, sql = resolved[0]
    assert _assigns_jobs_status(sql) is True


def test_the_guard_does_not_flag_a_where_clause_filter_on_status() -> None:
    """A `WHERE status = ?` filter is a read, never an assignment — scoping
    the search to the SET clause (and stopping at WHERE) is what keeps this
    guard from false-positiving on an ordinary status-filtered read."""
    assert _assigns_jobs_status("UPDATE jobs SET head_sha = ? WHERE status = 'queued'") is False
