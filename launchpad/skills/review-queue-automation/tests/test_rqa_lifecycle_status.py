#!/usr/bin/env python3
"""`status()` — E-17, `code/P-02-lifecycle.md` §3.4 and §8 T20.

No pytest: every `test_*` function here takes no arguments, per `tests/run_all.py`.

T20 is "`status(repo, number)` for every current-head status and an unknown PR |
disposition is total for known statuses and the unknown returns `NotFound`", so the
disposition case below is parametrised over **every** status the function can observe,
driven through the real `transition()` and the real `SQLiteRecordWriter` rather than by
writing `jobs.status` from the test. A test that set the column directly would pass even
if the transition table and the disposition map disagreed about which states exist.
"""

from __future__ import annotations

import json
import pathlib
import sqlite3
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from rqa.contracts import Job, JobStatus  # noqa: E402
from rqa.lifecycle import (  # noqa: E402
    DISPOSITION,
    Disposition,
    LifecycleError,
    NotFound,
    StatusReport,
    status,
)
from rqa.record.writer import SQLiteRecordWriter  # noqa: E402

#: `code/P-01-intake.md` §5's tables, reproduced because P-02 owns no DDL and
#: `rqa/intake` lands separately.
DDL = """
CREATE TABLE jobs (
  id              TEXT PRIMARY KEY,
  repo            TEXT NOT NULL,
  number          INTEGER NOT NULL,
  head_sha        TEXT NOT NULL,
  base_sha        TEXT NOT NULL,
  head_repo       TEXT NOT NULL,
  head_ref        TEXT NOT NULL,
  predecessor_job TEXT REFERENCES jobs(id),
  predecessor_head_sha TEXT,
  snapshot_hash   TEXT,
  status          TEXT NOT NULL,
  created_at      TEXT NOT NULL,
  UNIQUE (repo, number, head_sha)
);
CREATE TABLE pr_facts (
  repo         TEXT NOT NULL,
  number       INTEGER NOT NULL,
  head_sha     TEXT NOT NULL,
  base_sha     TEXT NOT NULL,
  head_repo    TEXT NOT NULL,
  head_ref     TEXT NOT NULL,
  author       TEXT NOT NULL,
  labels       TEXT NOT NULL,
  last_seen_at TEXT NOT NULL,
  PRIMARY KEY (repo, number)
);
"""

REPO = "owner/name"
NUMBER = 7
HEAD = "a" * 40
OLD_HEAD = "c" * 40
BASE = "b" * 40


class NoKeyStore:
    """ADR-0063's absent-key path. No OS keychain, no key material in this process."""

    def read(self, name: str) -> bytes | None:
        return None


def new_db() -> tuple[sqlite3.Connection, SQLiteRecordWriter]:
    connection = sqlite3.connect(":memory:")
    connection.executescript(DDL)
    return connection, SQLiteRecordWriter(connection, keystore=NoKeyStore())


def add_pr_facts(connection: sqlite3.Connection, *, head_sha: str = HEAD) -> None:
    connection.execute(
        "INSERT INTO pr_facts (repo, number, head_sha, base_sha, head_repo, head_ref, "
        "author, labels, last_seen_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (REPO, NUMBER, head_sha, BASE, REPO, "feature", "author", "[]", "2026-09-13T00:00:00Z"),
    )
    connection.commit()


def add_job(
    connection: sqlite3.Connection,
    *,
    job_id: str,
    head_sha: str,
    job_status: JobStatus,
    predecessor_job: str | None = None,
) -> Job:
    connection.execute(
        "INSERT INTO jobs (id, repo, number, head_sha, base_sha, head_repo, head_ref, "
        "predecessor_job, predecessor_head_sha, snapshot_hash, status, created_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            job_id, REPO, NUMBER, head_sha, BASE, REPO, "feature", predecessor_job, None,
            None, job_status.value, "2026-09-13T00:00:00.000000+00:00",
        ),
    )
    connection.commit()
    return Job(
        id=job_id, repo=REPO, number=NUMBER, head_sha=head_sha, base_sha=BASE, head_repo=REPO,
        head_ref="feature", predecessor_job=predecessor_job, predecessor_head_sha=None,
        snapshot_hash=None, status=job_status,
    )


def add_transition_entry(
    record: SQLiteRecordWriter,
    connection: sqlite3.Connection,
    *,
    job_id: str,
    to_state: str,
    reason: str,
) -> None:
    """`append` never commits (`P-12-record.md` §3.1) — the caller's transaction does,
    and here the caller is this fixture."""
    record.append(
        job_id,
        "transition",
        {
            "from_state": None, "to_state": to_state, "reason": reason, "repo": REPO,
            "number": NUMBER, "head_sha": HEAD, "base_sha": BASE, "predecessor_job": None,
        },
    )
    connection.commit()


# -- T20: the unknown PR ---------------------------------------------------------


def test_an_unknown_pull_request_is_not_found() -> None:
    """§3.4 step 1: no `pr_facts` row means RQA has never seen the PR."""
    connection, _record = new_db()
    assert status(REPO, NUMBER, connection=connection) == NotFound(REPO, NUMBER)


def test_a_known_pull_request_with_no_job_for_its_current_head_is_not_found() -> None:
    """§3.4 step 2: the narrow window right after inventory, before admission. A job for
    an *older* head is not an answer about the PR as it is now."""
    connection, _record = new_db()
    add_pr_facts(connection)
    add_job(connection, job_id="old", head_sha=OLD_HEAD, job_status=JobStatus.STOPPED)
    assert status(REPO, NUMBER, connection=connection) == NotFound(REPO, NUMBER)


def test_not_found_carries_the_repo_and_number_that_were_asked_for() -> None:
    connection, _record = new_db()
    answer = status(REPO, NUMBER, connection=connection)
    assert isinstance(answer, NotFound)
    assert answer.repo == REPO and answer.number == NUMBER


# -- T20: every status the function can observe ----------------------------------


def test_every_observable_status_maps_to_its_disposition_and_reason() -> None:
    """§8 T20 and RQA-FR-016: one of the six dispositions, and the reason for it, for
    every status `status()` can return — twelve of the thirteen, since §3.4 step 4 proves
    `SUPERSEDED` is unobservable at the current head."""
    for job_status, disposition in DISPOSITION.items():
        connection, record = new_db()
        add_pr_facts(connection)
        add_job(connection, job_id="job-1", head_sha=HEAD, job_status=job_status)
        add_transition_entry(
            record, connection, job_id="job-1", to_state=job_status.value, reason=f"reached {job_status.value}"
        )
        answer = status(REPO, NUMBER, connection=connection)
        assert isinstance(answer, StatusReport), job_status
        assert answer.job_id == "job-1"
        assert answer.internal_state is job_status
        assert answer.disposition is disposition
        assert answer.disposition in set(Disposition)
        assert answer.reason == f"reached {job_status.value}"
        connection.close()


def test_the_reason_is_the_latest_transitions() -> None:
    """§3.4 step 3 orders by `seq DESC`: `rqa status` answers with the current state's
    reason, never the one that got the job into the state before it."""
    connection, record = new_db()
    add_pr_facts(connection)
    add_job(connection, job_id="job-1", head_sha=HEAD, job_status=JobStatus.STOPPED)
    add_transition_entry(record, connection, job_id="job-1", to_state="claimed", reason="lease claimed")
    add_transition_entry(record, connection, job_id="job-1", to_state="planned", reason="plan recorded")
    add_transition_entry(record, connection, job_id="job-1", to_state="stopped", reason="bundle incomplete")
    answer = status(REPO, NUMBER, connection=connection)
    assert answer.reason == "bundle incomplete"


def test_a_job_with_no_recorded_transition_still_reports_its_disposition() -> None:
    """A `jobs` row can exist with no entry — a rolled-back arrival, or a crash between
    `jobs.create` and E-02. The disposition is still known; only the narrative is missing,
    and saying so is more honest than inventing one."""
    connection, _record = new_db()
    add_pr_facts(connection)
    add_job(connection, job_id="job-1", head_sha=HEAD, job_status=JobStatus.QUEUED)
    answer = status(REPO, NUMBER, connection=connection)
    assert answer.disposition is Disposition.BEING_REVIEWED
    assert answer.reason == "no recorded transition"


def test_only_transition_entries_are_read_for_the_reason() -> None:
    """§3.4 step 3 filters on `kind = 'transition'`: a later `judgement` or `action` entry
    is a neighbour's record, not this part's account of the state."""
    connection, record = new_db()
    add_pr_facts(connection)
    add_job(connection, job_id="job-1", head_sha=HEAD, job_status=JobStatus.JUDGED)
    add_transition_entry(record, connection, job_id="job-1", to_state="judged", reason="judgement recorded")
    record.append("job-1", "judgement", {"disposition": "approve", "reason": "not a transition"})
    connection.commit()
    assert status(REPO, NUMBER, connection=connection).reason == "judgement recorded"


def test_a_superseded_predecessor_does_not_answer_for_the_current_head() -> None:
    """§3.4 step 4: the job lookup is keyed on the PR's *current* head, so a superseded
    job — one a later job's `predecessor_job` points away from — can never be returned.
    That is why `DISPOSITION` needs no `SUPERSEDED` entry."""
    connection, record = new_db()
    add_pr_facts(connection)
    add_job(connection, job_id="old", head_sha=OLD_HEAD, job_status=JobStatus.SUPERSEDED)
    add_job(
        connection, job_id="new", head_sha=HEAD, job_status=JobStatus.REVIEWING,
        predecessor_job="old",
    )
    add_transition_entry(record, connection, job_id="old", to_state="superseded", reason="head moved")
    add_transition_entry(record, connection, job_id="new", to_state="reviewing", reason="panel running")
    answer = status(REPO, NUMBER, connection=connection)
    assert answer.job_id == "new"
    assert answer.internal_state is JobStatus.REVIEWING
    assert answer.reason == "panel running"


# -- T20: determinism and read-only-ness -----------------------------------------


def test_two_calls_with_nothing_changed_return_identical_reports() -> None:
    """§3.4's guarantee: "Two calls with nothing changed in between return
    field-for-field identical results". No clock, no cache, no ambient state."""
    connection, record = new_db()
    add_pr_facts(connection)
    add_job(connection, job_id="job-1", head_sha=HEAD, job_status=JobStatus.ESCALATED)
    add_transition_entry(record, connection, job_id="job-1", to_state="escalated", reason="evidence gap")
    first = status(REPO, NUMBER, connection=connection)
    second = status(REPO, NUMBER, connection=connection)
    assert first == second
    assert (first.job_id, first.internal_state, first.disposition, first.reason) == (
        second.job_id, second.internal_state, second.disposition, second.reason
    )


def test_status_writes_nothing_and_opens_no_transaction() -> None:
    """§3.4: read-only — "never calls `transition`, never touches a neighbour, never
    blocks on a lock". Three ordinary `SELECT`s, outside the write transaction `_commit`
    opens."""
    connection, record = new_db()
    add_pr_facts(connection)
    add_job(connection, job_id="job-1", head_sha=HEAD, job_status=JobStatus.APPROVED)
    add_transition_entry(record, connection, job_id="job-1", to_state="approved", reason="obligations met")
    before = (
        connection.execute("SELECT * FROM jobs").fetchall(),
        connection.execute("SELECT * FROM record_entries").fetchall(),
    )
    status(REPO, NUMBER, connection=connection)
    assert not connection.in_transaction
    assert before == (
        connection.execute("SELECT * FROM jobs").fetchall(),
        connection.execute("SELECT * FROM record_entries").fetchall(),
    )


# -- the stored state contradicting the contract ---------------------------------


def test_a_status_outside_the_thirteen_is_named() -> None:
    connection, _record = new_db()
    add_pr_facts(connection)
    connection.execute(
        "INSERT INTO jobs (id, repo, number, head_sha, base_sha, head_repo, head_ref, "
        "predecessor_job, predecessor_head_sha, snapshot_hash, status, created_at) "
        "VALUES ('job-1', ?, ?, ?, ?, ?, 'feature', NULL, NULL, NULL, 'almost_approved', 'x')",
        (REPO, NUMBER, HEAD, BASE, REPO),
    )
    connection.commit()
    try:
        status(REPO, NUMBER, connection=connection)
    except LifecycleError as exc:
        assert "almost_approved" in str(exc)
    else:  # pragma: no cover - the raise below is the failure report
        raise AssertionError("a corrupt jobs.status was reported as a disposition")


def test_a_superseded_job_at_the_current_head_is_a_named_inconsistency() -> None:
    """`DISPOSITION` has no `SUPERSEDED` entry because §3.4 step 4 proves it unreachable.
    If the stored state contradicts that proof, this says so — a status this function
    cannot map is a corrupted table, not a seventh disposition to invent."""
    connection, _record = new_db()
    add_pr_facts(connection)
    add_job(connection, job_id="job-1", head_sha=HEAD, job_status=JobStatus.SUPERSEDED)
    try:
        status(REPO, NUMBER, connection=connection)
    except LifecycleError as exc:
        assert "superseded" in str(exc)
    else:  # pragma: no cover - the raise below is the failure report
        raise AssertionError("a superseded job at the current head was given a disposition")


def test_a_transition_entry_with_no_reason_is_a_named_inconsistency() -> None:
    """§6 fixes the payload shape this part writes. A `transition` entry without a string
    `reason` was not written by this part, and guessing a narrative for it would make
    `rqa status` answer for a record it cannot read."""
    connection, record = new_db()
    add_pr_facts(connection)
    add_job(connection, job_id="job-1", head_sha=HEAD, job_status=JobStatus.QUEUED)
    record.append("job-1", "transition", {"to_state": "queued"})
    connection.commit()
    try:
        status(REPO, NUMBER, connection=connection)
    except LifecycleError as exc:
        assert "reason" in str(exc)
    else:  # pragma: no cover - the raise below is the failure report
        raise AssertionError("an unreadable transition entry produced a report")


def test_the_report_and_not_found_are_frozen_values() -> None:
    """`CONTRACTS.md`'s convention: every value type is a frozen dataclass, so a caller
    cannot edit an answer it was given and pass it on."""
    from dataclasses import FrozenInstanceError

    report = StatusReport(
        "job-1", internal_state=JobStatus.QUEUED, disposition=Disposition.BEING_REVIEWED,
        reason="admitted",
    )
    for value, field, replacement in (
        (report, "reason", "something else"),
        (NotFound(REPO, NUMBER), "number", 9),
    ):
        try:
            setattr(value, field, replacement)
        except FrozenInstanceError:
            pass
        else:  # pragma: no cover - the raise below is the failure report
            raise AssertionError(f"{type(value).__name__} is not frozen")


def test_the_payload_this_part_writes_is_the_payload_status_reads() -> None:
    """The two halves of §6 meet here: `transition()` writes the entry and `status()`
    reads its `reason` back. Asserted end to end rather than against a hand-built row."""
    from rqa.lifecycle import transition

    connection, record = new_db()
    add_pr_facts(connection)
    job = add_job(connection, job_id="job-1", head_sha=HEAD, job_status=JobStatus.QUEUED)
    transition(
        job, JobStatus.ESCALATED, reason="authority requirement", connection=connection,
        record=record,
    )
    answer = status(REPO, NUMBER, connection=connection)
    assert answer.internal_state is JobStatus.ESCALATED
    assert answer.disposition is Disposition.AWAITING_HUMAN_JUDGEMENT
    assert answer.reason == "authority requirement"
    payload = json.loads(
        connection.execute(
            "SELECT payload FROM record_entries WHERE job = 'job-1' ORDER BY seq DESC LIMIT 1"
        ).fetchone()[0]
    )
    assert payload["from_state"] == "queued" and payload["to_state"] == "escalated"
