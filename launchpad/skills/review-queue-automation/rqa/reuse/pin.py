"""Protocol and policy pin lookup from a trusted predecessor plan — P-13 §4."""

from __future__ import annotations

from collections.abc import Mapping

from rqa.contracts import VerifiedRecordPrefix
from rqa.reuse.obligations import ReuseError


def prior_pin(*, prefix: VerifiedRecordPrefix) -> tuple[str, str] | None:
    """Return the latest trusted plan's `(protocol_hash, policy_version)` pins.

    A missing plan returns `None`, forcing complete regeneration. A present plan must
    carry both required non-empty strings; malformed trusted payloads raise `ReuseError`.
    """
    plan_row = prefix.latest("plan")
    if plan_row is None:
        return None
    payload = plan_row.payload
    if not isinstance(payload, Mapping):
        raise ReuseError("predecessor plan payload is not a mapping")
    protocol_hash = payload.get("protocol_hash")
    policy_version = payload.get("policy_version")
    if type(protocol_hash) is not str or not protocol_hash:
        raise ReuseError("predecessor plan protocol_hash is malformed")
    if type(policy_version) is not str or not policy_version:
        raise ReuseError("predecessor plan policy_version is malformed")
    return protocol_hash, policy_version
