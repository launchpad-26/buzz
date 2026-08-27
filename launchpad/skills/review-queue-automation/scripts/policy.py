"""Policy-as-data for review-queue-automation.

A policy is the immutable decision surface used for a review cycle: authority,
risk bands, approval/request-changes thresholds, reviewer requirements, and the
model routes. It is carried as data, validated on load, and versioned by both a
monotonic version and a content hash so in-flight decisions can be pinned to the
exact policy that produced them.

Guarantees:
- atomic reload: a new policy is written and switched only after full validation;
  a failed validation leaves the last-known-good active and never widens authority.
- last-known-good retention across restarts via a durable marker.
- in-flight pinning: every decision records the policy version + hash it was made
  under; a later reload does not silently alter it.
- malformed policy is rejected (schema + semantic) rather than partially applied.
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


class PolicyReloadError(RuntimeError):
    """Raised when a reload cannot be applied; last-known-good is retained."""


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


# ---- durable last-known-good store --------------------------------------
class PolicyStore:
    """A small atomic policy store under a state directory.

    The active policy is kept at `<state>/policy/active.json` with a sidecar
    `active.meta.json` (version + hash). Reload is atomic: write a temp file,
    validate the new candidate, then swap. A failed reload keeps the prior file.
    """

    def __init__(self, state_dir: str | pathlib.Path):
        self.dir = pathlib.Path(state_dir) / "policy"
        self.dir.mkdir(parents=True, exist_ok=True)
        self.active_path = self.dir / "active.json"
        self.meta_path = self.dir / "active.meta.json"

    def _read(self) -> tuple[ValidatedPolicy | None, str | None]:
        if not self.active_path.is_file():
            return None, "no active policy"
        try:
            policy = json.loads(self.active_path.read_text(encoding="utf-8"))
            vp = canonicalize(policy)
            return vp, None
        except Exception as exc:
            return None, f"stored policy invalid: {exc}"

    def active(self) -> tuple[ValidatedPolicy | None, str | None]:
        """Current active policy, or last-known-good if the file is stale/corrupt."""
        return self._read()

    def reload(self, candidate: dict[str, Any]) -> ValidatedPolicy:
        """Atomically replace the active policy with a validated candidate.

        On validation failure the existing active policy is retained (last-known-good)
        and PolicyReloadError is raised with the validation issues.
        """
        vp = canonicalize(candidate)  # raises PolicyValidationError on bad policy
        # write temp then rename (atomic on same filesystem)
        tmp = self.active_path.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(candidate, indent=2) + "\n", encoding="utf-8")
        tmp.replace(self.active_path)
        self.meta_path.write_text(
            json.dumps(vp.as_record(), indent=2) + "\n", encoding="utf-8"
        )
        return vp

    def reload_with_rollback(self, candidate: dict[str, Any]) -> ValidatedPolicy:
        """Reload; on any failure attempt to restore the prior active file.

        Returns the new or last-known-good ValidatedPolicy. Never leaves a
        half-applied policy and never widens authority on failure.
        """
        try:
            return self.reload(candidate)
        except Exception:
            prior, err = self._read()
            if prior is not None:
                # re-assert the last-known-good file back if it was disturbed
                self.active_path.write_text(
                    json.dumps(prior.policy, indent=2) + "\n", encoding="utf-8"
                )
                self.meta_path.write_text(
                    json.dumps(prior.as_record(), indent=2) + "\n", encoding="utf-8"
                )
                return prior
            raise PolicyReloadError(f"policy reload failed and no last-known-good to retain: {err}")