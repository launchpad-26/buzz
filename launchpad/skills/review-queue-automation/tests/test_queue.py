#!/usr/bin/env python3
"""Deterministic queue reconciler tests. All fakes — no GitHub, no network.

WHY THE FAKE SITS AT THE TRANSPORT BOUNDARY. The previous version of this file
substituted a hand-written `_FakeRestReader` for the real reader. That fake
defined a `changed_files` method the real `RestReader` never had, so
`queue.py`'s call to it was green in the suite and an `AttributeError` in
production (launchpad-26/buzz#1962). A fake that invents its own method surface
tests the fake.

Everything here therefore drives the REAL `github_query.InventoryReader` and
substitutes only its injected `http_post` — the single function that would have
touched the network. A method that does not exist on the real class now fails
these tests, and `test_reader_surface_is_real` asserts that property directly.

Covers:
- full PR fact enrichment from one inventory read (files, additions/deletions,
  draft/open/author/branches/node_id, assignees, requested reviewers, head SHA,
  checks timestamps);
- latest-substantive-review-per-reviewer triage (dismissed and superseded change
  requests do not queue);
- a new head supersedes every older nonterminal job AND its pending request;
- an incomplete file list fails closed (no empty safe-looking job);
- `queue.main()` runs end to end;
- the reader surface `queue.py` depends on actually exists.
"""

from __future__ import annotations

import io
import json
import pathlib
import sys
import tempfile
from contextlib import redirect_stdout

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scripts"))

import approval  # noqa: E402
import github_query  # noqa: E402
from common import State, job_id  # noqa: E402


def fresh_state() -> State:
    return State({"state_dir": tempfile.mkdtemp()})


def _cfg(login: str = "tucktuck101") -> dict:
    return {"login": login, "github": {"timeout_seconds": 5}}


def _pr_node(
    number: int,
    author: str,
    head: str,
    *,
    files: list[dict] | None = None,
    reviews: list[dict] | None = None,
    checks: list[dict] | None = None,
    requested: list[str] | None = None,
    assignees: list[str] | None = None,
    additions: int = 4,
    deletions: int = 1,
    changed_files: int | None = None,
    draft: bool = False,
) -> dict:
    """One `pullRequests.nodes[]` entry, shaped as GitHub's GraphQL API shapes it."""
    files = files if files is not None else [
        {"path": "a.txt", "additions": 1, "deletions": 1},
        {"path": "b.py", "additions": 3, "deletions": 0},
    ]
    checks = checks if checks is not None else [
        {"__typename": "CheckRun", "name": "ci", "status": "COMPLETED",
         "conclusion": "SUCCESS", "startedAt": "2026-08-27T00:30:00Z",
         "completedAt": "2026-08-27T01:00:00Z"},
    ]
    return {
        "id": f"NODE-{number}",
        "number": number,
        "title": f"PR {number}",
        "url": f"https://github.com/o/r/pull/{number}",
        "isDraft": draft,
        "updatedAt": "2026-08-27T00:00:00Z",
        "additions": additions,
        "deletions": deletions,
        "changedFiles": len(files) if changed_files is None else changed_files,
        "reviewDecision": "",
        "baseRefName": "main",
        "headRefName": "feat",
        "headRefOid": head,
        "author": {"login": author},
        "assignees": {"pageInfo": {"hasNextPage": False, "endCursor": None},
                      "nodes": [{"login": a} for a in (assignees or [])]},
        "reviewRequests": {
            "pageInfo": {"hasNextPage": False, "endCursor": None},
            "nodes": [{"requestedReviewer": {"login": r}} for r in (requested or [])],
        },
        "reviews": {"pageInfo": {"hasNextPage": False, "endCursor": None},
                    "nodes": reviews or []},
        "files": {"pageInfo": {"hasNextPage": False, "endCursor": None}, "nodes": files},
        "commits": {"nodes": [{"commit": {"statusCheckRollup": {
            "state": "SUCCESS",
            "contexts": {"pageInfo": {"hasNextPage": False, "endCursor": None},
                         "nodes": checks},
        }}}]},
    }


def _review(login: str, state: str, commit: str = "h1") -> dict:
    return {"id": f"R-{login}-{state}", "state": state,
            "submittedAt": "2026-08-27T00:10:00Z",
            "author": {"login": login}, "commit": {"oid": commit}}


class _FakeTransport:
    """Stands in for `github_query.handle_http_post` only. Records every call."""

    def __init__(self, nodes: list[dict], *, errors: list[dict] | None = None):
        self.nodes = nodes
        self.errors = errors
        self.calls: list[dict] = []

    def __call__(self, token: str, payload: str, *, timeout: int = 60):
        body = json.loads(payload)
        self.calls.append(body)
        if self.errors:
            return 200, {"errors": self.errors}
        return 200, {
            "data": {
                "repository": {
                    "pullRequests": {
                        "pageInfo": {"hasNextPage": False, "endCursor": None},
                        "nodes": self.nodes,
                    }
                },
                "rateLimit": {"cost": 1, "remaining": 4999, "resetAt": "2026-08-27T02:00:00Z"},
            }
        }


def _reconcile(state: State, transport: _FakeTransport, cfg: dict | None = None):
    """Run the real reconciler with the real reader over a fake transport."""
    import queue as queue_mod

    cfg = cfg or _cfg()
    original = queue_mod.InventoryReader

    def build(config, st):
        return github_query.InventoryReader(
            config, st, http_post=transport, token="fake-token"
        )

    queue_mod.InventoryReader = build
    try:
        return queue_mod.reconcile(cfg, state, "o/r")
    finally:
        queue_mod.InventoryReader = original


def test_reader_surface_is_real() -> None:
    """Every reader attribute `queue.py` uses must exist on the real class.

    This is the direct guard for #1962: `queue.py` called
    `RestReader.changed_files`, which never existed on the real class.
    """
    import ast

    source_path = pathlib.Path(__file__).resolve().parent.parent / "scripts" / "queue.py"
    tree = ast.parse(source_path.read_text(encoding="utf-8"))

    used: set[str] = set()
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Attribute)
            and isinstance(node.value, ast.Name)
            and node.value.id == "reader"
        ):
            used.add(node.attr)

    assert used, "no reader attribute usage found; this guard would be vacuous"
    missing = [name for name in sorted(used) if not hasattr(github_query.InventoryReader, name)]
    assert not missing, f"queue.py calls reader methods that do not exist: {missing}"


def test_full_fact_enrichment() -> None:
    from queue import _checks_timestamps

    state = fresh_state()
    try:
        transport = _FakeTransport([_pr_node(1, "author", "h1", requested=["r1"])])
        result = _reconcile(state, transport)
        assert result["repo"] == "o/r"

        # One inventory query for the whole queue, not one call per pull request.
        assert len(transport.calls) == 1, transport.calls

        row = state.execute("SELECT payload FROM prs WHERE repo='o/r' AND number=1").fetchone()
        payload = json.loads(row["payload"])
        # complete file list
        assert payload["files"] == ["a.txt", "b.py"]
        # PR-level totals, authoritative even when files span pages
        assert payload["additions"] == 4
        assert payload["deletions"] == 1
        # enrichment from the inventory detail
        detail = payload["pr_detail"]
        assert detail["node_id"] == "NODE-1"
        assert detail["draft"] is False
        assert detail["user"]["login"] == "author"
        assert detail["head"]["sha"] == "h1"
        assert detail["base"]["ref"] == "main"
        # requested reviewers + checks timestamps
        assert payload["requested_reviewers"] == [{"login": "r1"}]
        assert payload["checks"][0]["name"] == "ci"
        assert payload["checks"][0]["conclusion"] == "SUCCESS"
        assert payload["checks_updated_at"] == "2026-08-27T01:00:00Z"
        assert _checks_timestamps(payload["checks"]) == "2026-08-27T01:00:00Z"
        # one job created for the unclaimed incoming PR
        jobs = state.execute("SELECT id, lane, status FROM jobs").fetchall()
        assert len(jobs) == 1
        assert jobs[0]["lane"] == "incoming_review"
        assert jobs[0]["status"] == "detected"
    finally:
        state.close()


def test_incomplete_file_list_fails_closed() -> None:
    """GitHub reports more changed files than the inventory assembled -> refuse.

    The safety property the old `changed-files` fail-closed branch protected:
    an understated file list could make `no_protected_trigger` or `limits_pass`
    pass on facts that were merely missing.
    """
    state = fresh_state()
    try:
        node = _pr_node(1, "author", "h1", changed_files=9)
        transport = _FakeTransport([node])
        try:
            _reconcile(state, transport)
            raise AssertionError("an incomplete file list must raise, never truncate")
        except github_query.InventoryError as exc:
            assert "incomplete" in str(exc)
        assert state.execute("SELECT 1 FROM jobs").fetchone() is None
    finally:
        state.close()


def test_inventory_read_failure_fails_closed() -> None:
    state = fresh_state()
    try:
        transport = _FakeTransport([], errors=[{"message": "RATE_LIMITED"}])
        try:
            _reconcile(state, transport)
            raise AssertionError("a failed inventory read must raise")
        except github_query.InventoryError as exc:
            assert "queue_inventory" in str(exc)
        assert state.execute("SELECT 1 FROM jobs").fetchone() is None
    finally:
        state.close()


def test_truncated_connection_is_followed_not_truncated() -> None:
    """A capped `files` connection is completed with a cursor, not silently cut."""
    state = fresh_state()

    page_one = [{"path": "a.txt", "additions": 1, "deletions": 1}]
    page_two = [{"path": "b.py", "additions": 3, "deletions": 0}]

    class _PagingTransport(_FakeTransport):
        def __call__(self, token, payload, *, timeout=60):
            body = json.loads(payload)
            self.calls.append(body)
            if "FilesPage" in body["query"]:
                return 200, {"data": {"repository": {"pullRequest": {"files": {
                    "pageInfo": {"hasNextPage": False, "endCursor": None},
                    "nodes": page_two,
                }}}, "rateLimit": {"cost": 1, "remaining": 4999}}}
            node = _pr_node(1, "author", "h1", files=page_one, changed_files=2)
            node["files"]["pageInfo"] = {"hasNextPage": True, "endCursor": "CUR-1"}
            return 200, {"data": {"repository": {"pullRequests": {
                "pageInfo": {"hasNextPage": False, "endCursor": None},
                "nodes": [node],
            }}, "rateLimit": {"cost": 1, "remaining": 4999}}}

    try:
        transport = _PagingTransport([])
        _reconcile(state, transport)
        payload = json.loads(
            state.execute("SELECT payload FROM prs WHERE number=1").fetchone()["payload"]
        )
        assert payload["files"] == ["a.txt", "b.py"], payload["files"]
        assert any("FilesPage" in c["query"] for c in transport.calls)
    finally:
        state.close()


def test_superseded_change_request_does_not_queue_author_triage() -> None:
    state = fresh_state()
    try:
        # Same reviewer: earlier CHANGES_REQUESTED is superseded by a later APPROVED.
        transport = _FakeTransport([
            _pr_node(1, _cfg()["login"], "h1", reviews=[
                _review("reviewer1", "CHANGES_REQUESTED"),
                _review("reviewer1", "APPROVED"),
            ])
        ])
        _reconcile(state, transport)
        assert state.execute("SELECT 1 FROM jobs").fetchone() is None
    finally:
        state.close()


def test_dismissed_change_request_does_not_queue() -> None:
    state = fresh_state()
    try:
        transport = _FakeTransport([
            _pr_node(1, _cfg()["login"], "hx", reviews=[_review("bob", "DISMISSED")])
        ])
        _reconcile(state, transport)
        assert state.execute("SELECT 1 FROM jobs").fetchone() is None
    finally:
        state.close()


def test_latest_change_request_queues_author_triage() -> None:
    state = fresh_state()
    try:
        transport = _FakeTransport([
            _pr_node(1, _cfg()["login"], "hx", reviews=[
                _review("bob", "CHANGES_REQUESTED"),
                _review("carol", "COMMENTED"),
                _review("carol", "CHANGES_REQUESTED"),
            ])
        ])
        _reconcile(state, transport)
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

        transport = _FakeTransport([_pr_node(3, "author", "newhead")])
        _reconcile(state, transport)
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


def test_main_runs_end_to_end() -> None:
    """`queue.main()` is invoked, not just `reconcile()`.

    #1775 identified the root cause of this defect class: no test in the suite
    invoked any `main()`, so every CLI surface was unexercised.
    """
    import queue as queue_mod

    state_dir = tempfile.mkdtemp()
    config_path = pathlib.Path(state_dir) / "config.json"
    config_path.write_text(json.dumps({
        "login": "tucktuck101",
        "state_dir": state_dir,
        "github": {"timeout_seconds": 5},
    }), encoding="utf-8")

    transport = _FakeTransport([_pr_node(7, "author", "h7")])
    original_reader = queue_mod.InventoryReader
    original_loader = queue_mod.load_config

    queue_mod.load_config = lambda path: (json.loads(config_path.read_text()), config_path)
    queue_mod.InventoryReader = lambda config, st: github_query.InventoryReader(
        config, st, http_post=transport, token="fake-token"
    )
    try:
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            code = queue_mod.main(["--config", str(config_path), "o/r"])
        assert code == 0
        emitted = json.loads(buffer.getvalue())
        assert emitted["repo"] == "o/r"
        assert emitted["open_count"] == 1
        assert emitted["transitions"][0]["number"] == 7
    finally:
        queue_mod.InventoryReader = original_reader
        queue_mod.load_config = original_loader


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
