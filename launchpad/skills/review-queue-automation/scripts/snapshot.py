"""Immutable runtime snapshots for review-queue-automation.

A runtime snapshot binds a validated repo-local config AND its resolved policy
into one content-hashed, versioned record. Every job pins the snapshot it started
with, so a later config/policy change cannot retroactively alter an in-flight or
already-recorded decision.

Guarantees actually implemented here:
- `content_hash` covers the canonical (sorted) config + policy, so any authority,
  model, threshold, or route change yields a different hash.
- `build_snapshot` is fail-closed: a missing, unreadable, or invalid policy raises
  `SnapshotError` and never produces a snapshot.
- `SnapshotStore.activate` is atomic and retains last-known-good: the candidate is
  validated and written to a temp file, then renamed over the active payload in a
  single operation. A failure at any point leaves the previous active payload
  byte-for-byte intact.
- Config and policy are stored in ONE payload file, so a restart reconstructs the
  exact snapshot; there is no window where two files disagree.
- `pin` enforces the pin: re-pinning a result that already carries a different
  snapshot hash raises `SnapshotPinError` rather than silently relabelling it.
"""

from __future__ import annotations

import hashlib
import json
import os
import pathlib
import time
from dataclasses import dataclass
from typing import Any, Callable

#: Top-level config key that, when present, carries the policy body inline.
POLICY_KEY = "policy"

#: Payload schema version for the stored snapshot file.
PAYLOAD_VERSION = 1


class SnapshotError(RuntimeError):
    """Raised when a snapshot cannot be built or activated; last-known-good stands."""


class SnapshotPinError(RuntimeError):
    """Raised when a result is re-pinned to a snapshot other than its original."""


@dataclass(frozen=True)
class RuntimeSnapshot:
    config: dict[str, Any]
    policy: dict[str, Any]
    config_version: str
    policy_version: str
    hash: str
    created_at: str

    def as_meta(self) -> dict[str, Any]:
        """Version identifiers only — safe to log, carries no config values."""
        return {
            "config_version": self.config_version,
            "policy_version": self.policy_version,
            "snapshot_hash": self.hash,
            "created_at": self.created_at,
        }


def _now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _canonical(payload: dict[str, Any]) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def content_hash(config: dict[str, Any], policy: dict[str, Any]) -> str:
    """Stable SHA-256 over the canonical combined config + resolved policy."""
    return hashlib.sha256(
        _canonical({"config": config, "policy": policy}).encode("utf-8")
    ).hexdigest()


def config_version(config: dict[str, Any]) -> str:
    value = config.get("version")
    if isinstance(value, bool) or not isinstance(value, (int, float, str)) or value == "":
        return "cfg-unversioned"
    return f"cfg-{value}"


def policy_version(policy: dict[str, Any]) -> str:
    value = policy.get("version")
    if isinstance(value, bool) or not isinstance(value, (int, float, str)) or value == "":
        return "unversioned"
    return str(value)


def _resolve_policy(
    config: dict[str, Any], policy_path: str | os.PathLike[str] | None
) -> dict[str, Any]:
    """Locate the policy: inline `policy` section first, else a policy file.

    Fail-closed: a missing, unreadable, or non-object policy raises SnapshotError.
    """
    inline = config.get(POLICY_KEY)
    if isinstance(inline, dict) and inline:
        return inline
    if policy_path:
        path = pathlib.Path(policy_path)
        if not path.is_file():
            raise SnapshotError(f"policy file not found: {path}")
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            raise SnapshotError(f"policy file unreadable: {exc}") from exc
        if not isinstance(data, dict) or not data:
            raise SnapshotError("policy file is not a non-empty JSON object")
        return data
    raise SnapshotError(
        "no policy configured (inline `policy` section or policy source required)"
    )


def build_snapshot(
    config: dict[str, Any],
    *,
    policy_path: str | os.PathLike[str] | None = None,
    validate_policy: Callable[[dict[str, Any]], list[str]] | None = None,
) -> RuntimeSnapshot:
    """Validate and assemble a RuntimeSnapshot from a raw config.

    `validate_policy` returns a list of issues (empty == valid). It is injectable
    so callers can pass `policy.validate_policy` without this module importing the
    validator, keeping the dependency direction one-way.
    """
    if not isinstance(config, dict) or not config:
        raise SnapshotError("cannot build a snapshot from a non-object config")
    policy = _resolve_policy(config, policy_path)
    if validate_policy is not None:
        issues = validate_policy(policy)
        if issues:
            raise SnapshotError("invalid policy: " + "; ".join(issues))
    return RuntimeSnapshot(
        config=config,
        policy=policy,
        config_version=config_version(config),
        policy_version=policy_version(policy),
        hash=content_hash(config, policy),
        created_at=_now(),
    )


class SnapshotStore:
    """Durable snapshot store under a state directory.

    Layout:
      <state>/snapshots/active.json          the currently active payload
      <state>/snapshots/by-hash/<hash>.json  every activated payload, kept so an
                                             in-flight job can be resumed under
                                             the exact snapshot it started with

    Each payload is one file, so a restart either sees the complete previous
    snapshot or the complete new one — never a half-applied mixture.
    """

    def __init__(self, state_dir: str | os.PathLike[str]):
        self.dir = pathlib.Path(state_dir) / "snapshots"
        self.by_hash_dir = self.dir / "by-hash"
        self.by_hash_dir.mkdir(parents=True, exist_ok=True)
        self.active_path = self.dir / "active.json"

    def _load(self, path: pathlib.Path) -> RuntimeSnapshot | None:
        """Reconstruct a stored snapshot, or None when absent/unreadable/corrupt."""
        if not path.is_file():
            return None
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return None
        if not isinstance(payload, dict):
            return None
        config = payload.get("config")
        policy = payload.get("policy")
        if not isinstance(config, dict) or not isinstance(policy, dict):
            return None
        meta = payload.get("meta") or {}
        stored_hash = meta.get("snapshot_hash", "")
        # A payload whose hash does not match its own contents is corrupt.
        if stored_hash != content_hash(config, policy):
            return None
        return RuntimeSnapshot(
            config=config,
            policy=policy,
            config_version=meta.get("config_version", config_version(config)),
            policy_version=meta.get("policy_version", policy_version(policy)),
            hash=stored_hash,
            created_at=meta.get("created_at", ""),
        )

    def active(self) -> RuntimeSnapshot | None:
        """The currently active snapshot, or None when absent/corrupt."""
        return self._load(self.active_path)

    def get(self, snapshot_hash: str) -> RuntimeSnapshot | None:
        """Retrieve a previously activated snapshot by hash.

        This is what lets an in-flight job be resumed under the exact snapshot it
        started with, so a config edit cannot retroactively change its authority.
        """
        if not snapshot_hash:
            return None
        return self._load(self.by_hash_dir / f"{snapshot_hash}.json")

    def activate(self, snapshot: RuntimeSnapshot) -> RuntimeSnapshot:
        """Atomically make `snapshot` active, retaining last-known-good on failure.

        The payload is also archived by hash so any job pinned to it stays
        resumable after later activations.
        """
        payload = {
            "payload_version": PAYLOAD_VERSION,
            "meta": snapshot.as_meta(),
            "config": snapshot.config,
            "policy": snapshot.policy,
        }
        try:
            body = json.dumps(payload, indent=2, sort_keys=True) + "\n"
        except (TypeError, ValueError) as exc:
            raise SnapshotError(f"snapshot is not serializable: {exc}") from exc

        # Archive first: an archived-but-not-active payload is harmless, whereas an
        # active payload with no archive would break resume-under-original-pin.
        archive = self.by_hash_dir / f"{snapshot.hash}.json"
        for target in (archive, self.active_path):
            tmp = target.with_name(target.name + ".tmp")
            try:
                tmp.write_text(body, encoding="utf-8")
                tmp.replace(target)
            except OSError as exc:
                tmp.unlink(missing_ok=True)
                raise SnapshotError(f"could not activate snapshot: {exc}") from exc
        return snapshot

    def pin(self, result: dict[str, Any], snapshot: RuntimeSnapshot) -> dict[str, Any]:
        """Bind a result to `snapshot`, refusing to relabel a differently-pinned one."""
        existing = result.get("snapshot_hash")
        if existing and existing != snapshot.hash:
            raise SnapshotPinError(
                f"result already pinned to {existing[:12]}; refusing to repin to {snapshot.hash[:12]}"
            )
        pinned = dict(result)
        pinned["snapshot_hash"] = snapshot.hash
        pinned["config_version"] = snapshot.config_version
        pinned["policy_version"] = snapshot.policy_version
        return pinned
