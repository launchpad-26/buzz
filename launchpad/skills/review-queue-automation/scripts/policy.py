"""Policy-as-data for review-queue-automation.

A policy is the immutable decision surface used for a review cycle: authority,
risk bands, approval/request-changes thresholds, reviewer requirements, and the
model routes. It is carried as data, validated on load, and versioned by both a
monotonic version and a content hash so in-flight decisions can be pinned to the
exact policy that produced them.

This module owns policy VALIDATION and versioning only. The durable runtime store
is `snapshot.SnapshotStore`, which activates config and policy together as one
content-hashed snapshot — they must be validated as a pair, and a policy-only
store previously duplicated that machinery without ever being called.

Guarantees provided here:
- deterministic schema + semantic validation; a malformed policy is rejected
  rather than partially applied, so it can never widen authority.
- stable content hashing and version extraction, used to pin a decision to the
  exact policy that produced it.
"""

from __future__ import annotations

import hashlib
import json
import pathlib
from dataclasses import dataclass
from typing import Any

from authority import validate_authority
from risk import ConfigBandError, validate_bands

POLICY_SCHEMA_VERSION = 1
#: Key that a policy object must carry.
REQUIRED_KEYS = {"version", "authority", "approval", "risk", "human_queue"}


class PolicyValidationError(ValueError):
    """Raised when a policy fails schema or semantic validation. Existing policy stands."""


def content_hash(policy: dict[str, Any]) -> str:
    """Stable SHA-256 content hash over the canonical (sorted) policy."""
    canonical = json.dumps(policy, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class ValidatedPolicy:
    policy: dict[str, Any]
    version: str
    hash: str

    def as_record(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "hash": self.hash,
            "policy": self.policy,
        }


def validate_policy(policy: dict[str, Any]) -> list[str]:
    """Deterministic schema + semantic validation. Empty list == valid.

    A malformed policy must never widen authority, so validation rejects:
    unknown keys, out-of-range thresholds, discontinuous bands, unknown modes,
    and any missing required section.
    """
    issues: list[str] = []
    if policy is None or not isinstance(policy, dict):
        return ["policy must be a non-empty object"]
    for key in REQUIRED_KEYS:
        if key not in policy:
            issues.append(f"policy is missing required key: {key}")

    # authority
    authority = policy.get("authority")
    if authority is not None:
        issues.extend(validate_authority(authority))

    # risk bands (continuity enforced)
    risk = policy.get("risk") or {}
    bands = risk.get("bands")
    if bands:
        try:
            validate_bands(bands)
        except (ConfigBandError, ValueError, TypeError) as exc:
            issues.append(f"risk.bands invalid: {exc}")
    else:
        issues.append("policy.risk.bands is required")

    # approval thresholds
    approval = policy.get("approval") or {}
    for intkey in ("effective_risk_max", "complexity_max", "file_limit", "line_limit"):
        value = approval.get(intkey, 0)
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            issues.append(f"approval.{intkey} must be a non-negative integer")
    rate = approval.get("approval_rate_max")
    if not (isinstance(rate, (int, float)) and 0 <= rate <= 1):
        issues.append("approval.approval_rate_max must be a number in [0,1]")
    req_eff = approval.get("required_effective_risk_max", approval.get("effective_risk_max"))
    req_compl = approval.get("required_complexity_max", approval.get("complexity_max"))
    if not (isinstance(req_eff, int) and isinstance(req_compl, int)):
        issues.append("approval requires integer effective_risk_max and complexity_max")

    # human queue
    human = policy.get("human_queue") or {}
    if not isinstance(human.get("expiry_minutes", 0), int) or human.get("expiry_minutes", 0) <= 0:
        issues.append("human_queue.expiry_minutes must be a positive integer")

    return issues


def validate_or_raise(policy: dict[str, Any]) -> None:
    issues = validate_policy(policy)
    if issues:
        raise PolicyValidationError("; ".join(issues))


def policy_version(policy: dict[str, Any]) -> str:
    """Return the policy's declared version string, defaulting to 'unversioned'."""
    v = policy.get("version")
    if isinstance(v, str) and v:
        return v
    if isinstance(v, (int, float)):
        return str(v)
    return "unversioned"


def canonicalize(policy: dict[str, Any]) -> ValidatedPolicy:
    """Validate and return a pinned ValidatedPolicy (version + content hash)."""
    validate_or_raise(policy)
    return ValidatedPolicy(policy=policy, version=policy_version(policy), hash=content_hash(policy))
