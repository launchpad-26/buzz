#!/usr/bin/env python3
"""Lease tests: fakes only, no network, no GitHub, no model calls.

Covers the repaired `lease.py` contract:
- The mutation uses the PR node ID as `assignableId` and the configured USER
  node ID (from REST) as `assigneeIds`.
- The configured login is used; no hardcoded tucktuck fallback.
- `claim` REST-verifies the assignment BEFORE the local lease row is written;
  a failed mutation leaves the lease unclaimed.
- `release` drops the local lease ONLY after REST confirms the login is gone; a
  still-listed login raises and the lease survives.
"""

from __future__ import annotations

import json
import pathlib
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scripts"))

from common import State, utcnow  # noqa: E402
import github_mutate as gm  # noqa: E402
import lease as lease_mod  # noqa: E402


class FakeReader:
    """Replaces lease.RestReader. All instances share one in-repo assignee set."""

    ASSIGNEES: list[str] = []

    def __init__(self, config, state):
        self.config = config
        self.state = state

    def pr_meta(self, repo, number):
        return {"assignees": [{"login": lg} for lg in self.ASSIGNEES]}


def _seed(state: State, repo: str, number: int) -> None:
    state.db.execute(
        "INSERT INTO prs(repo,number,head_sha,updated_at,payload,open,last_seen) VALUES(?,?,?,?,?,1,?)",
        (repo, number, "h", utcnow(), json.dumps({"node_id": "PR_NODE_1", "user": {"login": "other"}}), utcnow()),
    )
    state.db.execute(
        "INSERT INTO etags(url,etag,body,updated_at) VALUES(?,?,?,?)",
        ("https://api.github.com/users/alice", "e", json.dumps({"node_id": "USER_NODE_ALICE"}), utcnow()),
    )
    state.db.execute(
        "INSERT INTO jobs(id,repo,number,head_sha,lane,status,artifact_dir,created_at,updated_at) "
        "VALUES(?,?,?,?,?,?,?,?,?)",
        ("job1", repo, number, "h", "incoming_review", "reviewing", "/tmp/j", utcnow(), utcnow()),
    )
    state.db.commit()


def _lease_row(state: State, repo: str, number: int):
    return state.db.execute(
        "SELECT job_id FROM leases WHERE repo=? AND number=?", (repo, number)
    ).fetchone()


def _install_reader(assignees: list[str]) -> None:
    FakeReader.ASSIGNEES = list(assignees)
    lease_mod.RestReader = FakeReader


def test_claim_uses_pr_node_id_and_user_node_id() -> None:
    state = State({"state_dir": tempfile.mkdtemp()})
    captured = {}

    def fake_post(state_, op, variables, job, **kw):
        captured["op"] = op
        captured["variables"] = variables
        if op == "add_assignee":
            FakeReader.ASSIGNEES = ["alice"]  # mutation applied on REST
        return {"ok": True}

    old = gm.post
    gm.post = fake_post
    try:
        _install_reader([])
        _seed(state, "o/r", 1)
        ok = lease_mod.claim({"login": "alice"}, state, "o/r", 1, "job1", "alice")
        assert ok is True
        # the mutation addressed the PR by its node id and the USER by its node id
        assert captured["variables"]["assignableId"] == "PR_NODE_1"
        assert captured["variables"]["assigneeIds"] == ["USER_NODE_ALICE"]
        assert _lease_row(state, "o/r", 1)["job_id"] == "job1"
    finally:
        gm.post = old
        state.close()


def test_claim_requires_nonempty_login_no_fallback() -> None:
    state = State({"state_dir": tempfile.mkdtemp()})
    called = []

    def fake_post(*args, **kw):
        called.append(args[1])
        return {"ok": True}

    old = gm.post
    gm.post = fake_post
    try:
        _install_reader([])
        _seed(state, "o/r", 1)
        try:
            lease_mod.claim({"login": "alice"}, state, "o/r", 1, "job1", "")
            raise AssertionError("empty login must be refused")
        except RuntimeError:
            pass
        assert called == []  # an empty login must never dispatch a mutation
        assert _lease_row(state, "o/r", 1) is None
    finally:
        gm.post = old
        state.close()


def test_claim_wont_steal_another_assignees_pr() -> None:
    state = State({"state_dir": tempfile.mkdtemp()})

    def no_mutate(*args, **kw):
        raise AssertionError("must not mutate a PR owned by another assignee")

    old = gm.post
    gm.post = no_mutate
    try:
        _install_reader(["someone-else"])
        _seed(state, "o/r", 1)
        ok = lease_mod.claim({"login": "alice"}, state, "o/r", 1, "job1", "alice")
        assert ok is False
        assert _lease_row(state, "o/r", 1) is None
    finally:
        gm.post = old
        state.close()


def test_claim_rest_verify_failure_leaves_no_local_lease() -> None:
    state = State({"state_dir": tempfile.mkdtemp()})

    def stuck(*args, **kw):
        # mutation is sent but the assignee list never changes -> verify fails
        return {"ok": True}

    old = gm.post
    gm.post = stuck
    try:
        _install_reader([])
        _seed(state, "o/r", 1)
        ok = lease_mod.claim({"login": "alice"}, state, "o/r", 1, "job1", "alice")
        assert ok is False
        assert _lease_row(state, "o/r", 1) is None
    finally:
        gm.post = old
        state.close()


def test_release_verifies_before_dropping_local_lease() -> None:
    state = State({"state_dir": tempfile.mkdtemp()})

    def stuck(*args, **kw):
        # removal mutation does not land: REST still lists alice
        return {"ok": True}

    old = gm.post
    gm.post = stuck
    try:
        _install_reader(["alice"])
        _seed(state, "o/r", 1)
        state.db.execute("INSERT INTO leases(repo, number, job_id, claimed_at) VALUES(?,?,?,?)",
                         ("o/r", 1, "job1", utcnow()))
        state.db.commit()
        try:
            lease_mod.release({"login": "alice"}, state, "o/r", 1, "job1", "alice")
            raise AssertionError("release should raise when REST still lists alice")
        except RuntimeError:
            pass
        assert _lease_row(state, "o/r", 1) is not None  # not dropped
    finally:
        gm.post = old
        state.close()


def test_release_removes_lease_after_rest_confirm() -> None:
    state = State({"state_dir": tempfile.mkdtemp()})

    def fake(state_, operation, variables, job, **kw):
        if operation == "remove_assignee":
            FakeReader.ASSIGNEES = []  # REST confirms removal
        return {"ok": True}

    old = gm.post
    gm.post = fake
    try:
        _install_reader(["alice"])
        _seed(state, "o/r", 1)
        state.db.execute("INSERT INTO leases(repo, number, job_id, claimed_at) VALUES(?,?,?,?)",
                         ("o/r", 1, "job1", utcnow()))
        state.db.commit()
        lease_mod.release({"login": "alice"}, state, "o/r", 1, "job1", "alice")
        assert _lease_row(state, "o/r", 1) is None
    finally:
        gm.post = old
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

                print(f"FAIL {name}: {exc}")
                traceback.print_exc()
    print(f"{passed} passed, {failures} failed")
    sys.exit(1 if failures else 0)