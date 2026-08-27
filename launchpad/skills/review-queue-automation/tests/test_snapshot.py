#!/usr/bin/env python3
"""Unit tests for snapshot.py — immutable runtime snapshots.

Covers policy resolution (inline / file / missing), content hashing sensitivity,
fail-closed validation, atomic activation with last-known-good retention, exact
round-trip reconstruction, corrupt-payload rejection, and pin enforcement.
Deterministic; no network and no GitHub.
"""

from __future__ import annotations

import json
import pathlib
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scripts"))

from snapshot import (  # noqa: E402
    SnapshotError,
    SnapshotPinError,
    SnapshotStore,
    build_snapshot,
    config_version,
    content_hash,
    policy_version,
)


def _policy() -> dict:
    return {
        "version": "v1",
        "authority": {"approve": "disabled", "request_changes": "disabled"},
        "approval": {
            "effective_risk_max": 24,
            "complexity_max": 2,
            "file_limit": 50,
            "line_limit": 1000,
            "approval_rate_max": 0.5,
        },
        "risk": {"bands": {"low": 24, "medium": 99, "high": 100}},
        "human_queue": {"expiry_minutes": 1440},
    }


def _config() -> dict:
    return {"version": 1, "models": {"primary": [], "secondary": []}, "policy": _policy()}


# -- build / fail-closed -------------------------------------------------
def test_inline_policy_builds_snapshot() -> None:
    snap = build_snapshot(_config())
    assert snap.policy["version"] == "v1"
    assert snap.config_version == "cfg-1"
    assert snap.policy_version == "v1"
    assert len(snap.hash) == 64
    assert snap.created_at.endswith("Z")


def test_missing_policy_fails_closed() -> None:
    try:
        build_snapshot({"version": 1, "models": {}})
    except SnapshotError as exc:
        assert "no policy" in str(exc)
    else:
        raise AssertionError("a config with no policy must fail closed")


def test_non_object_config_rejected() -> None:
    for bad in (None, [], {}, "cfg"):
        try:
            build_snapshot(bad)  # type: ignore[arg-type]
        except SnapshotError:
            continue
        raise AssertionError(f"non-object config must be rejected: {bad!r}")


def test_validator_issues_reject_snapshot() -> None:
    try:
        build_snapshot(_config(), validate_policy=lambda _p: ["bands discontinuous"])
    except SnapshotError as exc:
        assert "invalid policy" in str(exc)
        assert "bands discontinuous" in str(exc)
    else:
        raise AssertionError("validator issues must prevent a snapshot")


def test_valid_policy_passes_validator() -> None:
    snap = build_snapshot(_config(), validate_policy=lambda _p: [])
    assert snap.hash


def test_policy_file_used_when_no_inline_section() -> None:
    with tempfile.TemporaryDirectory() as td:
        path = pathlib.Path(td) / "policy.json"
        path.write_text(json.dumps(_policy()), encoding="utf-8")
        snap = build_snapshot({"version": 2}, policy_path=path)
        assert snap.policy_version == "v1"
        assert snap.config_version == "cfg-2"


def test_missing_or_malformed_policy_file_fails_closed() -> None:
    with tempfile.TemporaryDirectory() as td:
        missing = pathlib.Path(td) / "nope.json"
        try:
            build_snapshot({"version": 1}, policy_path=missing)
        except SnapshotError as exc:
            assert "not found" in str(exc)
        else:
            raise AssertionError("missing policy file must fail closed")

        empty = pathlib.Path(td) / "empty.json"
        empty.write_text("{}", encoding="utf-8")
        try:
            build_snapshot({"version": 1}, policy_path=empty)
        except SnapshotError as exc:
            assert "non-empty" in str(exc)
        else:
            raise AssertionError("empty policy object must fail closed")

        broken = pathlib.Path(td) / "broken.json"
        broken.write_text("{not json", encoding="utf-8")
        try:
            build_snapshot({"version": 1}, policy_path=broken)
        except SnapshotError as exc:
            assert "unreadable" in str(exc)
        else:
            raise AssertionError("unparseable policy file must fail closed")


# -- hashing ------------------------------------------------------------
def test_hash_changes_when_policy_changes() -> None:
    baseline = content_hash(_config(), _policy())
    changed = _policy()
    changed["approval"]["effective_risk_max"] = 40
    assert content_hash(_config(), changed) != baseline


def test_hash_changes_when_config_changes() -> None:
    baseline = content_hash(_config(), _policy())
    cfg = _config()
    cfg["models"]["primary"] = [{"selector": "x"}]
    assert content_hash(cfg, _policy()) != baseline


def test_hash_is_key_order_independent() -> None:
    a = {"version": 1, "models": {}}
    b = {"models": {}, "version": 1}
    assert content_hash(a, _policy()) == content_hash(b, _policy())


def test_version_labels() -> None:
    assert config_version({"version": 5}) == "cfg-5"
    assert config_version({}) == "cfg-unversioned"
    assert config_version({"version": True}) == "cfg-unversioned"
    assert policy_version({"version": "v9"}) == "v9"
    assert policy_version({}) == "unversioned"


# -- store: activation, round-trip, corruption, last-known-good ---------
def test_activate_round_trips_exact_config_and_policy() -> None:
    with tempfile.TemporaryDirectory() as td:
        store = SnapshotStore(td)
        assert store.active() is None  # nothing active yet
        snap = build_snapshot(_config())
        store.activate(snap)

        loaded = store.active()
        assert loaded is not None
        # The real stored config/policy come back, not fabricated stubs.
        assert loaded.config == snap.config
        assert loaded.policy == snap.policy
        assert loaded.hash == snap.hash
        assert loaded.policy["approval"]["effective_risk_max"] == 24


def test_corrupt_payload_is_rejected_not_trusted() -> None:
    with tempfile.TemporaryDirectory() as td:
        store = SnapshotStore(td)
        store.activate(build_snapshot(_config()))

        # Tamper with the policy while leaving the recorded hash intact.
        payload = json.loads(store.active_path.read_text(encoding="utf-8"))
        payload["policy"]["approval"]["effective_risk_max"] = 9999
        store.active_path.write_text(json.dumps(payload), encoding="utf-8")

        assert store.active() is None, "hash mismatch must invalidate the payload"


def test_unparseable_active_file_returns_none() -> None:
    with tempfile.TemporaryDirectory() as td:
        store = SnapshotStore(td)
        store.active_path.write_text("{not json", encoding="utf-8")
        assert store.active() is None


def test_reactivation_replaces_previous_snapshot() -> None:
    with tempfile.TemporaryDirectory() as td:
        store = SnapshotStore(td)
        first = build_snapshot(_config())
        store.activate(first)

        cfg = _config()
        cfg["policy"]["approval"]["effective_risk_max"] = 10
        second = build_snapshot(cfg)
        store.activate(second)

        loaded = store.active()
        assert loaded is not None
        assert loaded.hash == second.hash != first.hash
        assert loaded.policy["approval"]["effective_risk_max"] == 10


def test_failed_activation_retains_last_known_good() -> None:
    with tempfile.TemporaryDirectory() as td:
        store = SnapshotStore(td)
        good = build_snapshot(_config())
        store.activate(good)
        before = store.active_path.read_bytes()

        # A snapshot carrying non-serializable config cannot be written; the
        # previously active payload must survive byte-for-byte.
        broken = build_snapshot({"version": 3, "policy": _policy()})
        object.__setattr__(broken, "config", {"bad": {1, 2}})  # set() is not JSON
        try:
            store.activate(broken)
        except (SnapshotError, TypeError):
            pass
        else:
            raise AssertionError("unserializable snapshot must not activate")

        assert store.active_path.read_bytes() == before
        assert store.active().hash == good.hash


def test_no_temp_file_left_behind_after_activation() -> None:
    with tempfile.TemporaryDirectory() as td:
        store = SnapshotStore(td)
        store.activate(build_snapshot(_config()))
        leftovers = [p.name for p in store.dir.iterdir() if p.name.endswith(".tmp")]
        assert leftovers == []


# -- pinning ------------------------------------------------------------
def test_pin_records_versions_and_hash() -> None:
    with tempfile.TemporaryDirectory() as td:
        store = SnapshotStore(td)
        snap = build_snapshot(_config())
        pinned = store.pin({"job": "j1"}, snap)
        assert pinned["snapshot_hash"] == snap.hash
        assert pinned["config_version"] == "cfg-1"
        assert pinned["policy_version"] == "v1"
        assert pinned["job"] == "j1"


def test_pin_does_not_mutate_caller_result() -> None:
    with tempfile.TemporaryDirectory() as td:
        store = SnapshotStore(td)
        snap = build_snapshot(_config())
        original = {"job": "j1"}
        store.pin(original, snap)
        assert original == {"job": "j1"}


def test_repinning_to_a_different_snapshot_is_refused() -> None:
    with tempfile.TemporaryDirectory() as td:
        store = SnapshotStore(td)
        first = build_snapshot(_config())
        cfg = _config()
        cfg["policy"]["approval"]["effective_risk_max"] = 10
        second = build_snapshot(cfg)

        pinned = store.pin({"job": "j1"}, first)
        try:
            store.pin(pinned, second)
        except SnapshotPinError as exc:
            assert "already pinned" in str(exc)
        else:
            raise AssertionError("an in-flight result must not be silently repinned")


def test_repinning_to_the_same_snapshot_is_idempotent() -> None:
    with tempfile.TemporaryDirectory() as td:
        store = SnapshotStore(td)
        snap = build_snapshot(_config())
        once = store.pin({"job": "j1"}, snap)
        twice = store.pin(once, snap)
        assert twice == once
