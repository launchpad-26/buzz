#!/usr/bin/env python3
"""Tests that a config/policy edit reloads correctly and safely.

Required behaviour: a config edit hot-reloads for NEW jobs, an in-flight job stays
pinned to the snapshot it started with, and a malformed edit retains the
last-known-good rather than half-applying or widening authority.
"""

from __future__ import annotations

import pathlib
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scripts"))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import dispatcher  # noqa: E402
from common import State  # noqa: E402
from snapshot import SnapshotStore  # noqa: E402
from test_dispatch_flow import _config, seed_evidence, seed_job  # noqa: E402


def _policy(risk_max: int = 24, version: str = "v1") -> dict:
    return {
        "version": version,
        "authority": {"approve": "disabled"},
        "approval": {"effective_risk_max": risk_max, "complexity_max": 2,
                      "file_limit": 50, "line_limit": 1000, "approval_rate_max": 0.5},
        "risk": {"bands": {"low": 24, "medium": 99, "high": 100}},
        "human_queue": {"expiry_minutes": 1440},
    }


def _cfg(state_dir: str, policy: dict | None) -> dict:
    cfg = _config("live")
    cfg["state_dir"] = state_dir
    if policy is not None:
        cfg["policy"] = policy
    return cfg


def _job(state: State, number: int) -> str:
    jid = seed_job(state, number=number, head=f"h{number}")
    seed_evidence(state, jid)
    return jid


def test_valid_edit_applies_to_new_jobs_only() -> None:
    state_dir = tempfile.mkdtemp()
    state = State({"state_dir": state_dir})
    try:
        first_job = _job(state, 950)
        _eff, first = dispatcher.resolve_snapshot(_cfg(state_dir, _policy(24)), state, first_job)
        assert first["pinned"] is True

        edited = _cfg(state_dir, _policy(99, "v3"))
        second_job = _job(state, 952)
        _eff2, second = dispatcher.resolve_snapshot(edited, state, second_job)

        assert second["snapshot_hash"] != first["snapshot_hash"]
        assert second["policy_version"] == "v3"
        # the active snapshot advanced to the edited one
        assert SnapshotStore(state_dir).active().hash == second["snapshot_hash"]
    finally:
        state.close()


def test_in_flight_job_keeps_its_original_policy() -> None:
    state_dir = tempfile.mkdtemp()
    state = State({"state_dir": state_dir})
    try:
        job = _job(state, 953)
        _eff, original = dispatcher.resolve_snapshot(_cfg(state_dir, _policy(24)), state, job)

        edited = _cfg(state_dir, _policy(99, "v3"))
        effective, resumed = dispatcher.resolve_snapshot(edited, state, job)

        assert resumed["resumed"] is True
        assert resumed["snapshot_hash"] == original["snapshot_hash"]
        assert effective["policy"]["approval"]["effective_risk_max"] == 24, (
            "an edit must not retroactively change an in-flight job"
        )
    finally:
        state.close()


def test_malformed_edit_retains_last_known_good() -> None:
    state_dir = tempfile.mkdtemp()
    state = State({"state_dir": state_dir})
    try:
        dispatcher.resolve_snapshot(_cfg(state_dir, _policy(24)), state, _job(state, 954))
        store = SnapshotStore(state_dir)
        good_hash = store.active().hash
        before = store.active_path.read_bytes()

        malformed = _cfg(state_dir, {"version": "v2"})  # missing required sections
        _eff, meta = dispatcher.resolve_snapshot(malformed, state, _job(state, 955))

        assert meta["pinned"] is False
        assert "invalid policy" in meta["reason"]
        assert store.active().hash == good_hash, "last-known-good must remain active"
        assert store.active_path.read_bytes() == before
    finally:
        state.close()


def test_malformed_edit_does_not_widen_authority() -> None:
    """A rejected policy must never leak its authority into the effective config."""
    state_dir = tempfile.mkdtemp()
    state = State({"state_dir": state_dir})
    try:
        dispatcher.resolve_snapshot(_cfg(state_dir, _policy(24)), state, _job(state, 956))

        # A policy that grants approve authority but is structurally invalid.
        malformed = _cfg(state_dir, {"version": "v9", "authority": {"approve": "live"}})
        effective, meta = dispatcher.resolve_snapshot(malformed, state, _job(state, 957))

        assert meta["pinned"] is False
        assert SnapshotStore(state_dir).active().policy["authority"]["approve"] == "disabled"
        # the caller's config is returned unchanged, not merged with the bad policy
        assert effective["policy"]["version"] == "v9"
        assert "invalid policy" in meta["reason"]
    finally:
        state.close()


def test_absent_policy_is_reported_and_not_fatal() -> None:
    state_dir = tempfile.mkdtemp()
    state = State({"state_dir": state_dir})
    try:
        _eff, meta = dispatcher.resolve_snapshot(
            _cfg(state_dir, None), state, _job(state, 958)
        )
        assert meta["pinned"] is False
        assert "no policy" in meta["reason"]
    finally:
        state.close()


def test_repeated_resolve_with_unchanged_config_is_stable() -> None:
    """Re-resolving must not churn the active snapshot."""
    state_dir = tempfile.mkdtemp()
    state = State({"state_dir": state_dir})
    try:
        cfg = _cfg(state_dir, _policy(24))
        first_job = _job(state, 959)
        _eff, first = dispatcher.resolve_snapshot(cfg, state, first_job)
        second_job = _job(state, 960)
        _eff2, second = dispatcher.resolve_snapshot(cfg, state, second_job)
        assert first["snapshot_hash"] == second["snapshot_hash"]
    finally:
        state.close()
