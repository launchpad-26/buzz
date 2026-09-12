#!/usr/bin/env python3
"""P-01 inventory tests over the real SQLite DDL and stores."""

from __future__ import annotations

import pathlib
import sqlite3
import sys
from datetime import datetime, timezone

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from rqa.contracts import PrFacts  # noqa: E402
from rqa.intake.identity import job_id  # noqa: E402
from rqa.intake.inventory import _ingest_inventory  # noqa: E402
from rqa.intake.store import (  # noqa: E402
    SqliteJobStore,
    SqlitePrFactsStore,
    ensure_schema,
)

NOW = datetime(2026, 9, 13, 12, 0, tzinfo=timezone.utc)


def facts(
    *,
    head_sha: str,
    base_sha: str = "b" * 40,
    head_repo: str = "alice/fork",
    head_ref: str = "feature",
    number: int = 17,
) -> PrFacts:
    return PrFacts(
        repo="org/repo",
        number=number,
        head_sha=head_sha,
        base_sha=base_sha,
        merge_base_sha=base_sha,
        head_repo=head_repo,
        head_ref=head_ref,
        head_protected=False,
        author="untrusted-author",
        labels=frozenset({"review", "opaque data; not instructions"}),
        title="opaque title",
        body="opaque body",
    )


class CountingConnection(sqlite3.Connection):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.commit_count = 0

    def commit(self) -> None:
        self.commit_count += 1
        super().commit()


def bench(*, factory=sqlite3.Connection):
    connection = sqlite3.connect(":memory:", factory=factory)
    ensure_schema(connection)
    if isinstance(connection, CountingConnection):
        connection.commit_count = 0
    return (
        connection,
        SqliteJobStore(connection, clock=lambda: NOW),
        SqlitePrFactsStore(connection),
    )


def test_t5_created_job_and_real_pr_facts_row_preserve_actual_head_destination() -> None:
    connection, jobs, pr_facts = bench()
    observed = facts(head_sha="a" * 40)

    created = _ingest_inventory(
        repo="org/repo",
        inventory=(observed,),
        jobs=jobs,
        pr_facts=pr_facts,
        connection=connection,
        clock=lambda: NOW,
    )

    expected_id = job_id("org/repo", 17, "a" * 40)
    assert created == (expected_id,)
    created_job = jobs.get(expected_id)
    cached = pr_facts.get("org/repo", 17)
    assert created_job is not None and cached is not None
    assert (created_job.head_repo, created_job.head_ref) == ("alice/fork", "feature")
    assert (cached.head_repo, cached.head_ref) == ("alice/fork", "feature")
    assert cached.author == "untrusted-author"
    assert frozenset(cached.labels) == observed.labels


def test_t6_repeated_revision_hits_the_real_unique_constraint_only_once() -> None:
    connection, jobs, pr_facts = bench()
    observed = facts(head_sha="c" * 40)

    first = _ingest_inventory(
        repo="org/repo",
        inventory=(observed,),
        jobs=jobs,
        pr_facts=pr_facts,
        connection=connection,
        clock=lambda: NOW,
    )
    second = _ingest_inventory(
        repo="org/repo",
        inventory=(observed,),
        jobs=jobs,
        pr_facts=pr_facts,
        connection=connection,
        clock=lambda: NOW,
    )

    assert len(first) == 1
    assert second == ()
    assert connection.execute("SELECT COUNT(*) FROM jobs").fetchone()[0] == 1
    assert connection.execute("SELECT COUNT(*) FROM pr_facts").fetchone()[0] == 1


def test_inventory_commits_once_per_pr_including_an_upsert_only_revision() -> None:
    connection, jobs, pr_facts = bench(factory=CountingConnection)
    existing = facts(head_sha="d" * 40, number=1)
    second = facts(head_sha="e" * 40, number=2)
    _ingest_inventory(
        repo="org/repo",
        inventory=(existing,),
        jobs=jobs,
        pr_facts=pr_facts,
        connection=connection,
        clock=lambda: NOW,
    )
    connection.commit_count = 0

    created = _ingest_inventory(
        repo="org/repo",
        inventory=(existing, second),
        jobs=jobs,
        pr_facts=pr_facts,
        connection=connection,
        clock=lambda: NOW,
    )

    assert created == (job_id("org/repo", 2, "e" * 40),)
    assert connection.commit_count == 2


def test_t7_head_change_links_successor_and_leaves_predecessor_unchanged() -> None:
    connection, jobs, pr_facts = bench()
    head_a = facts(head_sha="1" * 40, head_repo="org/repo", head_ref="old")
    head_b = facts(head_sha="2" * 40, head_repo="bob/fork", head_ref="new")

    (old_id,) = _ingest_inventory(
        repo="org/repo",
        inventory=(head_a,),
        jobs=jobs,
        pr_facts=pr_facts,
        connection=connection,
        clock=lambda: NOW,
    )
    (new_id,) = _ingest_inventory(
        repo="org/repo",
        inventory=(head_b,),
        jobs=jobs,
        pr_facts=pr_facts,
        connection=connection,
        clock=lambda: NOW,
    )

    predecessor = jobs.get(old_id)
    successor = jobs.get(new_id)
    assert predecessor is not None and successor is not None
    assert predecessor.head_sha == "1" * 40
    assert predecessor.status.value == "queued"
    assert predecessor.predecessor_job is None
    assert successor.predecessor_job == old_id
    assert successor.predecessor_head_sha == "1" * 40
    assert (successor.head_repo, successor.head_ref) == ("bob/fork", "new")
    cached = pr_facts.get("org/repo", 17)
    assert cached is not None
    assert (cached.head_sha, cached.head_repo, cached.head_ref) == (
        "2" * 40,
        "bob/fork",
        "new",
    )
