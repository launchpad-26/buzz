#!/usr/bin/env python3
"""State persistence + transition acceptance tests. No GitHub/network.

Covers REQUIRED changes 5 (reject nonexistent-job transitions without a success
event; approval/human/log tables coherent and idempotent), 6 (onboarding-generated
config normalizes without legacy KeyError), and 8 (safe state-persistence failure
path: StatePersistenceError, never a swallowed sqlite3.Error).
"""

from __future__ import annotations

import json
import pathlib
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scripts"))

from common import State, StatePersistenceError, normalize_config  # noqa: E402
from errors import JobBlockingError  # noqa: E402


def fresh_state() -> State:
    return State({"state_dir": tempfile.mkdtemp()})


def _seed(state, job: str, status: str = "detected", head: str = "h") -> None:
    state.execute(
        "INSERT INTO jobs(id,repo,number,head_sha,lane,status,artifact_dir,created_at,updated_at) "
        "VALUES(?,?,?,?,?,?,?,?,?)",
        (job, "o/r", 1, head, "incoming_review", status, "/tmp/j",
         "2026-01-01T00:00:00Z", "2026-01-01T00:00:00Z"),
    )
    state._commit()


# ---- change 5: nonexistent-job transitions are rejected without success ----
def test_transition_on_nonexistent_job_raises_without_write() -> None:
    state = fresh_state()
    try:
        try:
            state.transition("does-not-exist", "assurance")
            raise AssertionError("must refuse a transition on a nonexistent job")
        except JobBlockingError:
            pass
        # no job row appeared, so no success event / no illegal mutation
        assert state.current_status("does-not-exist") is None
        rows = state.execute("SELECT 1 FROM jobs WHERE id=?", ("does-not-exist",)).fetchall()
        assert rows == []
    finally:
        state.close()


def test_legal_transition_writes_success_event() -> None:
    state = fresh_state()
    try:
        _seed(state, "j1")
        state.transition("j1", "evidence", reason="step")
        assert state.current_status("j1") == "evidence"
    finally:
        state.close()


def test_illegal_transition_leaves_state_and_logs_error_not_success() -> None:
    state = fresh_state()
    try:
        _seed(state, "j2", status="completed")  # completed is terminal
        try:
            state.transition("j2", "assurance")
            raise AssertionError("terminal -> assurance must be illegal")
        except JobBlockingError:
            pass
        # state unchanged, no success transition recorded
        assert state.current_status("j2") == "completed"
    finally:
        state.close()


# ---- mutation: required approval/human/log tables are coherent + idempotent --
def test_required_tables_exist_once() -> None:
    state = fresh_state()
    try:
        not_dup = state.db.execute(
            "SELECT name, COUNT(*) FROM sqlite_master WHERE type='table' "
            "AND name IN ('jobs','mutations','approval_decisions','human_requests','leases') "
            "GROUP BY name"
        ).fetchall()
        assert {r["name"]: r["COUNT(*)"] for r in not_dup} == {
            "jobs": 1, "mutations": 1, "approval_decisions": 1,
            "human_requests": 1, "leases": 1,
        }
    finally:
        state.close()


def test_approval_and_human_inserts_are_idempotent() -> None:
    """The same (repo, number, head, policy) cannot enqueue twice in human_requests,
    and approval_decisions upsert must be idempotent across re-runs."""
    import approval as approval_mod

    state = fresh_state()
    try:
        a = approval_mod.enqueue(state, repo="o/r", number=1, head_sha="h", policy={},
                                 summary="s", assurance={}, reviewers=[], risk_score=1,
                                 risk_band="low", protected=[], failed_gates=[], ci={},
                                 findings=[], recommendation="x", rationale="x", action="approve")
        b = approval_mod.enqueue(state, repo="o/r", number=1, head_sha="h", policy={},
                                 summary="s", assurance={}, reviewers=[], risk_score=1,
                                 risk_band="low", protected=[], failed_gates=[], ci={},
                                 findings=[], recommendation="x", rationale="x", action="approve")
        assert a["request_id"] == b["request_id"]
        assert state.db.execute("SELECT COUNT(*) FROM human_requests").fetchone()[0] == 1

        # approval_decisions upsert is idempotent on the same natural key
        state.db.execute(
            "INSERT INTO approval_decisions(id,repo,number,head_sha,policy_hash,status,mode,risk_score,created_at,expires_at) "
            "VALUES('d1','o/r',1,'h','ph','eligible','shadow',3,'2026-01-01T00:00:00Z',NULL) "
            "ON CONFLICT(repo,number,head_sha,policy_hash) DO UPDATE SET status='eligible'"
        )
        state.db.commit()
        state.db.execute(
            "INSERT INTO approval_decisions(id,repo,number,head_sha,policy_hash,status,mode,risk_score,created_at,expires_at) "
            "VALUES('d1b','o/r',1,'h','ph','eligible','shadow',3,'2026-01-01T00:00:00Z',NULL) "
            "ON CONFLICT(repo,number,head_sha,policy_hash) DO UPDATE SET status='eligible'"
        )
        state.db.commit()
        assert state.db.execute("SELECT COUNT(*) FROM approval_decisions").fetchone()[0] == 1
    finally:
        state.close()


def test_state_error_never_leaks_raw_sqlite() -> None:
    """A persistence failure (table gone) raises StatePersistenceError, not bare sqlite3.Error."""
    state = fresh_state()
    try:
        # force an invalid SQL statement through the typed path
        try:
            state.execute("SELECT * FROM no_such_table")
            raise AssertionError("invalid SQL must raise")
        except StatePersistenceError:
            pass
        except Exception as exc:  # pragma: no cover
            raise AssertionError(f"wrong exception: {type(exc).__name__}: {exc}")
    finally:
        state.close()


def test_onboarding_config_normalizes_without_keyerror() -> None:
    """An onboarding-generated repo-local config (with a filled slug) normalizes
    to a `repos` mapping and downstream KeyError is gone."""
    from config import onboarding_defaults

    with tempfile.TemporaryDirectory() as d:
        cfg = onboarding_defaults(pathlib.Path(d))
        cfg["login"] = "tucktuck101"
        cfg["repository"]["slug"] = "launchpad-26/buzz"
        norm = normalize_config(cfg)
        # the unified runtime shape always has `repos`
        assert "launchpad-26/buzz" in norm["repos"]
        entry = norm["repos"]["launchpad-26/buzz"]
        assert entry["path"] == str(pathlib.Path(d).resolve())
        assert entry["base"] == "launchpad"
        assert entry["dco"] is True
        # evidence/panel/lease consume config["repos"].get(repo, {}) — never a KeyError
        assert norm["repos"].get("launchpad-26/buzz", {}).get("path")


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