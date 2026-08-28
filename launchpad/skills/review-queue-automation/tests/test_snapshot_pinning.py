#!/usr/bin/env python3
"""Tests that a job runs under the runtime snapshot it STARTED with.

The guarantee: editing config or policy mid-flight must not retroactively change
an in-flight job's authority, thresholds, or model routes. A new job picks up the
new snapshot; a resumed job keeps its original pin.
"""

from __future__ import annotations

import pathlib
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scripts"))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import dispatcher  # noqa: E402
from common import State  # noqa: E402
from snapshot import SnapshotStore, build_snapshot  # noqa: E402
from test_dispatch_flow import (  # noqa: E402
    _clean_verdict,
    _config,
    fake_approve,
    fake_panel,
    patch_approval,
    patch_dispatcher,
    restore_approval,
    restore_dispatcher,
    seed_evidence,
    seed_job,
    seed_verdicts,
)


def _policy(risk_max: int = 24) -> dict:
    return {
        "version": "v1",
        "authority": {"approve": "disabled"},
        "approval": {"effective_risk_max": risk_max, "complexity_max": 2,
                      "file_limit": 50, "line_limit": 1000, "approval_rate_max": 0.5},
        "risk": {"bands": {"low": 24, "medium": 99, "high": 100}},
        "human_queue": {"expiry_minutes": 1440},
    }


def _cfg(state_dir: str, risk_max: int = 24) -> dict:
    cfg = _config("live")
    cfg["state_dir"] = state_dir
    cfg["policy"] = _policy(risk_max)
    return cfg


def _seed(state: State, number: int) -> str:
    jid = seed_job(state, number=number, head=f"h{number}")
    seed_evidence(state, jid)
    seed_verdicts(state, jid, [_clean_verdict("opus", "anthropic"),
                               _clean_verdict("ds", "openrouter")])
    return jid


def _dispatch(cfg: dict, state: State, jid: str, number: int) -> dict:
    saved = patch_dispatcher(run_panel=fake_panel("SUPPORTED"))
    previous = patch_approval(fake_approve(True, "approved"))
    try:
        return dispatcher.run_job(
            cfg, {"job_id": jid, "repo": "o/r", "number": number, "lane": "incoming_review"},
            state=state,
        )
    finally:
        restore_approval(previous)
        restore_dispatcher(saved)


# -- migration ----------------------------------------------------------
def test_snapshot_column_is_added_idempotently() -> None:
    state_dir = tempfile.mkdtemp()
    first = State({"state_dir": state_dir})
    try:
        columns = {r["name"] for r in first.db.execute("PRAGMA table_info(jobs)")}
        assert "snapshot_hash" in columns
    finally:
        first.close()
    # Reopening the same database must not fail on a duplicate ALTER.
    second = State({"state_dir": state_dir})
    try:
        assert second.db.execute("SELECT 1").fetchone() is not None
    finally:
        second.close()


# -- pinning ------------------------------------------------------------
def test_first_dispatch_pins_the_active_snapshot() -> None:
    state_dir = tempfile.mkdtemp()
    state = State({"state_dir": state_dir})
    try:
        cfg = _cfg(state_dir)
        jid = _seed(state, 300)
        result = _dispatch(cfg, state, jid, 300)
        meta = result["snapshot"]
        assert meta["pinned"] is True
        assert meta["resumed"] is False
        assert meta["policy_version"] == "v1"
        assert len(meta["snapshot_hash"]) == 64
        stored = state.db.execute(
            "SELECT snapshot_hash FROM jobs WHERE id=?", (jid,)
        ).fetchone()["snapshot_hash"]
        assert stored == meta["snapshot_hash"]
    finally:
        state.close()


def test_edited_policy_produces_a_new_snapshot_for_a_new_job() -> None:
    state_dir = tempfile.mkdtemp()
    state = State({"state_dir": state_dir})
    try:
        first = _dispatch(_cfg(state_dir, 24), state, _seed(state, 300), 300)
        second = _dispatch(_cfg(state_dir, 99), state, _seed(state, 301), 301)
        assert first["snapshot"]["snapshot_hash"] != second["snapshot"]["snapshot_hash"]
    finally:
        state.close()


def test_resumed_job_keeps_its_original_pin() -> None:
    """The core guarantee: a mid-flight edit cannot change an in-flight job."""
    state_dir = tempfile.mkdtemp()
    state = State({"state_dir": state_dir})
    try:
        jid = _seed(state, 300)
        original = _dispatch(_cfg(state_dir, 24), state, jid, 300)["snapshot"]

        # Operator raises the risk ceiling after the job started.
        effective, meta = dispatcher.resolve_snapshot(_cfg(state_dir, 99), state, jid)

        assert meta["resumed"] is True
        assert meta["snapshot_hash"] == original["snapshot_hash"]
        assert effective["policy"]["approval"]["effective_risk_max"] == 24, (
            "the edited ceiling must not apply to an already-pinned job"
        )
    finally:
        state.close()


def test_missing_archive_refuses_to_silently_upgrade() -> None:
    """If the pinned payload is gone we must say so, not adopt a newer snapshot."""
    state_dir = tempfile.mkdtemp()
    state = State({"state_dir": state_dir})
    try:
        jid = _seed(state, 300)
        original = _dispatch(_cfg(state_dir, 24), state, jid, 300)["snapshot"]

        store = SnapshotStore(state_dir)
        (store.by_hash_dir / f"{original['snapshot_hash']}.json").unlink()

        _effective, meta = dispatcher.resolve_snapshot(_cfg(state_dir, 99), state, jid)
        assert meta["pinned"] is False
        assert "no longer archived" in meta["reason"]
    finally:
        state.close()


def test_absent_policy_is_reported_not_fatal() -> None:
    """Snapshotting is additive: a repo without policy-as-data still dispatches."""
    state_dir = tempfile.mkdtemp()
    state = State({"state_dir": state_dir})
    try:
        cfg = _config("live")
        cfg["state_dir"] = state_dir  # no `policy` section at all
        jid = _seed(state, 302)
        result = _dispatch(cfg, state, jid, 302)
        meta = result["snapshot"]
        assert meta["pinned"] is False
        assert "no policy" in meta["reason"]
        # the job still reached a terminal decision
        assert result["status"] == "completed_auto_approved"
    finally:
        state.close()


def test_invalid_policy_is_reported_not_fatal() -> None:
    state_dir = tempfile.mkdtemp()
    state = State({"state_dir": state_dir})
    try:
        cfg = _config("live")
        cfg["state_dir"] = state_dir
        cfg["policy"] = {"version": "v1"}  # missing required sections
        jid = _seed(state, 303)
        meta = _dispatch(cfg, state, jid, 303)["snapshot"]
        assert meta["pinned"] is False
        assert "invalid policy" in meta["reason"]
    finally:
        state.close()


# -- archive ------------------------------------------------------------
def test_activation_archives_by_hash_for_resume() -> None:
    state_dir = tempfile.mkdtemp()
    store = SnapshotStore(state_dir)
    snap = build_snapshot({"version": 1, "policy": _policy()})
    store.activate(snap)

    assert (store.by_hash_dir / f"{snap.hash}.json").is_file()
    assert store.get(snap.hash) is not None
    assert store.get(snap.hash).hash == snap.hash


def test_later_activation_does_not_destroy_the_earlier_archive() -> None:
    state_dir = tempfile.mkdtemp()
    store = SnapshotStore(state_dir)
    first = build_snapshot({"version": 1, "policy": _policy(24)})
    second = build_snapshot({"version": 1, "policy": _policy(99)})
    store.activate(first)
    store.activate(second)

    assert store.active().hash == second.hash
    assert store.get(first.hash) is not None, "an earlier pin must stay resumable"
    assert store.get(first.hash).policy["approval"]["effective_risk_max"] == 24


def test_get_unknown_hash_returns_none() -> None:
    store = SnapshotStore(tempfile.mkdtemp())
    assert store.get("") is None
    assert store.get("f" * 64) is None
