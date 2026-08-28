#!/usr/bin/env python3
"""Deterministic queue reconciler tests. All fakes — no GitHub, no network.

Covers REQUIRED changes 1-3:
- full PR fact enrichment from pr_meta + changed-files (files, summed additions/
  deletions, draft/open/author/branches/node_id, requested reviewers, head SHA,
  checks timestamps);
- latest-substantive-review-per-reviewer triage (dismissed and superseded change
  requests do not queue);
- a new head supersedes every older nonterminal job AND its pending request;
- changed-files read failure fails closed (no empty safe-looking job).
"""

from __future__ import annotations

import json
import pathlib
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scripts"))

import approval  # noqa: E402
from common import State, job_id  # noqa: E402


def fresh_state() -> State:
    return State({"state_dir": tempfile.mkdtemp()})


def _cfg(login: str = "tucktuck101") -> dict:
    return {"login": login}


def _detail(number: int, author: str, head: str) -> dict:
    return {
        "number": number,
        "user": {"login": author},
        "head": {"sha": head, "ref": "feat"},
        "base": {"ref": "main"},
        "node_id": f"NODE-{number}",
        "draft": False,
        "state": "open",
        "updated_at": "2026-08-27T00:00:00Z",
        "assignees": [],
    }


class _FakeRestReader:
    """Deterministic stand-in for github_rest.RestReader."""

    def __init__(self, details: dict, changed: dict, reviews: dict,
                 checks: dict, requested: dict, fail_changed: set[int] | None = None):
        self.details = details
        self.changed = changed
        self.reviews = reviews
        # NOTE: stored under checks_data so it does not shadow the checks() method.
        self.checks_data = checks
        self.requested = requested
        self.fail_changed = fail_changed or set()

    def open_prs(self, repo):
        return [
            {"number": n, "head": {"sha": d["head"]["sha"]},
             "user": {"login": d["user"]["login"]}}
            for n, d in self.details.items()
        ]

    def pr_meta(self, repo, number):
        return self.details[number]

    def changed_files(self, repo, number):
        if number in self.fail_changed:
            raise RuntimeError("changed-files REST returned 500")
        return self.changed[number]

    def checks(self, repo, number):
        return self.checks_data[number]

    def requested_reviewers(self, repo, number):
        return self.requested[number]

    def pr_reviews(self, repo, number):
        return self.reviews[number]

    def review_comments(self, repo, number):
        return []

    def issue_comments(self, repo, number):
        return []

def _reconcile(state, reader, cfg=None):
    import queue as queue_mod
    cfg = cfg or _cfg()
    orig = queue_mod.RestReader
    queue_mod.RestReader = lambda config, state: reader
    try:
        return queue_mod.reconcile(cfg, state, "o/r")
    finally:
        queue_mod.RestReader = orig


def _base_reader(fail_changed=None):
    return _FakeRestReader(
        details={1: _detail(1, "author", "h1")},
        changed={1: [{"filename": "a.txt", "additions": 1, "deletions": 1},
                      {"filename": "b.py", "additions": 3, "deletions": 0}]},
        reviews={1: []},
        checks={1: [{"name": "ci", "completed_at": "2026-08-27T01:00:00Z"}]},
        requested={1: [{"login": "r1"}]},
        fail_changed={1} if fail_changed else None,
    )


def test_full_fact_enrichment() -> None:
    from queue import _checks_timestamps

    state = fresh_state()
    try:
        reader = _base_reader()
        result = _reconcile(state, reader)
        assert result["repo"] == "o/r"
        row = state.execute("SELECT payload FROM prs WHERE repo='o/r' AND number=1").fetchone()
        payload = json.loads(row["payload"])
        # complete file list
        assert payload["files"] == ["a.txt", "b.py"]
        # summed additions/deletions from changed-files
        assert payload["additions"] == 4
        assert payload["deletions"] == 1
        # enrichment from full REST detail
        detail = payload["pr_detail"]
        assert detail["node_id"] == "NODE-1"
        assert detail["draft"] is False
        assert detail["user"]["login"] == "author"
        assert detail["head"]["sha"] == "h1"
        assert detail["base"]["ref"] == "main"
        # requested reviewers + checks timestamps
        assert payload["requested_reviewers"] == [{"login": "r1"}]
        assert payload["checks"] == [{"name": "ci", "completed_at": "2026-08-27T01:00:00Z"}]
        assert _checks_timestamps(payload["checks"]) == "2026-08-27T01:00:00Z"
        # one job created for the unclaimed incoming PR
        jobs = state.execute("SELECT id, lane, status FROM jobs").fetchall()
        assert len(jobs) == 1
        assert jobs[0]["lane"] == "incoming_review"
        assert jobs[0]["status"] == "detected"
    finally:
        state.close()


def test_changed_files_failure_fails_closed() -> None:
    state = fresh_state()
    try:
        reader = _base_reader(fail_changed=True)
        try:
            _reconcile(state, reader)
            raise AssertionError("changed-files failure must raise, never empty files")
        except RuntimeError as exc:
            assert "changed-files" in str(exc)
        # no job persisted on a fail-closed read
        assert state.execute("SELECT 1 FROM jobs").fetchone() is None
    finally:
        state.close()


def test_superseded_change_request_does_not_queue_author_triage() -> None:
    state = fresh_state()
    try:
        # Same reviewer: earlier CHANGES_REQUESTED is superseded by a later APPROVED.
        reader = _FakeRestReader(
            details={1: _detail(1, _cfg()["login"], "h1")},
            changed={1: [{"filename": "a.txt", "additions": 1, "deletions": 0}]},
            reviews={1: [
                {"user": {"login": "reviewer1"}, "state": "CHANGES_REQUESTED"},
                {"user": {"login": "reviewer1"}, "state": "APPROVED"},
            ]},
            checks={1: []}, requested={1: []},
        )
        _reconcile(state, reader)
        # no outstanding change request -> no author-triage job
        assert state.execute("SELECT 1 FROM jobs").fetchone() is None
    finally:
        state.close()


def test_dismissed_change_request_does_not_queue() -> None:
    state = fresh_state()
    try:
        reader = _FakeRestReader(
            details={1: _detail(1, _cfg()["login"], "hx")},
            changed={1: [{"filename": "a.txt", "additions": 1, "deletions": 0}]},
            reviews={1: [{"user": {"login": "bob"}, "state": "DISMISSED"}]},
            checks={1: []}, requested={1: []},
        )
        _reconcile(state, reader)
        assert state.execute("SELECT 1 FROM jobs").fetchone() is None
    finally:
        state.close()


def test_latest_change_request_queues_author_triage() -> None:
    state = fresh_state()
    try:
        reader = _FakeRestReader(
            details={1: _detail(1, _cfg()["login"], "hx")},
            changed={1: [{"filename": "a.txt", "additions": 1, "deletions": 0}]},
            reviews={1: [
                {"user": {"login": "bob"}, "state": "CHANGES_REQUESTED"},
                {"user": {"login": "carol"}, "state": "COMMENTED"},
                {"user": {"login": "carol"}, "state": "CHANGES_REQUESTED"},
            ]},
            checks={1: []}, requested={1: []},
        )
        _reconcile(state, reader)
        rows = state.execute("SELECT lane FROM jobs").fetchall()
        assert [r["lane"] for r in rows] == ["author_triage"]
    finally:
        state.close()


def test_new_head_supersedes_old_job_and_pending_request() -> None:
    state = fresh_state()
    try:
        old = job_id("o/r", 3, "oldhead", "incoming_review")
        state.execute(
            "INSERT INTO jobs(id,repo,number,head_sha,lane,status,artifact_dir,created_at,updated_at) "
            "VALUES(?,?,?,?,?,?,?,?,?)",
            (old, "o/r", 3, "oldhead", "incoming_review", "assurance", "/tmp/j",
             "2026-01-01T00:00:00Z", "2026-01-01T00:00:00Z"),
        )
        approval.enqueue(
            state, repo="o/r", number=3, head_sha="oldhead", policy={},
            summary="s", assurance={}, reviewers=[], risk_score=1, risk_band="low",
            protected=[], failed_gates=[], ci={}, findings=[], recommendation="x",
            rationale="x", action="approve",
        )
        state._commit()

        reader = _FakeRestReader(
            details={3: _detail(3, "author", "newhead")},
            changed={3: [{"filename": "a.txt", "additions": 1, "deletions": 0}]},
            reviews={3: []}, checks={3: []}, requested={3: []},
        )
        _reconcile(state, reader)
        # the old job is superseded, not terminal
        job = state.execute("SELECT status FROM jobs WHERE id=?", (old,)).fetchone()
        assert job["status"] == "superseded"
        # the pending review request for the stale head is superseded too
        reqs = state.execute(
            "SELECT state FROM human_requests WHERE repo='o/r' AND number=3"
        ).fetchall()
        assert reqs and all(r["state"] == "superseded" for r in reqs), [dict(r) for r in reqs]
    finally:
        state.close()


if __name__ == "__main__":
    failures = 0
    passed = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                passed += 1
            except Exception as exc:
                failures += 1
                import traceback
                traceback.print_exc()
                print(f"FAIL {name}: {exc}")
    print(f"{passed} passed, {failures} failed")
    sys.exit(1 if failures else 0)