"""Validation outcomes, the internal `ValidatedConfig`, and P-03's error family.

`code/P-03-policy.md` §2. Boundary values come from the seam truth: this module
**imports** `ValidationErrorCode`, `ValidationError` and `ValidationFailure` from
`rqa.contracts` (`CONTRACTS.md` §3 owns them) and declares only the three names
P-03 owns — `ValidatedConfig`, `PolicyError` and `SnapshotStoreCorrupted` — plus
the one clock both entry points read time from.

`ValidatedConfig` never crosses a part boundary: it is everything a `Snapshot`
needs except `hash`, `repo` and `protocol_hash`, handed from `validate()` to
`snapshot_for()` inside this package.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime, timezone

from rqa.contracts import (
    Activity,
    Budget,
    External,
    Policy,
    Route,
    ValidationError,
    ValidationErrorCode,
    ValidationFailure,
)

__all__ = [
    "ValidatedConfig",
    "PolicyError",
    "SnapshotStoreCorrupted",
    "utcnow",
    "ValidationError",
    "ValidationErrorCode",
    "ValidationFailure",
]


@dataclass(frozen=True)
class ValidatedConfig:
    """Everything a `Snapshot` needs except `hash`, `repo` and `protocol_hash`."""

    authority: Mapping[Activity, bool]
    routes: tuple[Route, ...]
    external: External
    policy: Policy
    budget: Budget


class PolicyError(Exception):
    """Programming error: rqa.policy was called wrongly, or its own invariants are
    broken. Never raised for malformed repository configuration — that is a shared
    ValidationFailure."""


class SnapshotStoreCorrupted(PolicyError):
    """A pinned hash is missing or its archived bytes no longer hash to their own name."""


def utcnow() -> datetime:
    """The one clock this package reads. UTC and timezone-aware, so an activation
    timestamp round-trips through `datetime.isoformat()` without losing its offset."""
    return datetime.now(timezone.utc)
