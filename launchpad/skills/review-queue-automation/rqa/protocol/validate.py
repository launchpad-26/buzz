"""Validate one harness verdict against the published protocol."""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import cast

from .contradictions import contradiction_reasons
from .fence import strip_fence
from .schema import structural_reasons
from .types import (
    Category,
    EvidenceState,
    Finding,
    HarnessIdentity,
    InjectionAttempt,
    Invalid,
    Location,
    Remedy,
    Valid,
    Verdict,
)
from .version import PROTOCOL_VERSION


class ProtocolError(Exception):
    """Programming error: blank attempt_id. Malformed verdicts return shared Invalid."""


def validate(*, path: Path, attempt_id: str) -> Valid | Invalid:
    """Validate one verdict file and attach its caller-owned attempt identifier."""
    if not isinstance(attempt_id, str) or attempt_id == "":
        raise ProtocolError("attempt_id must be a non-empty string")

    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return Invalid(("unreadable",))

    stripped = text.strip()
    if stripped == "":
        return Invalid(("empty_payload",))

    normalized = strip_fence(text=stripped)
    try:
        decoded = json.loads(normalized)
    except json.JSONDecodeError as exc:
        return Invalid((f"malformed_json: {exc.msg}",))

    if not isinstance(decoded, dict):
        return Invalid(("not_an_object",))
    data = cast(Mapping[str, object], decoded)

    structural = structural_reasons(data=data)
    if structural:
        return Invalid(structural)

    if data["protocol_version"] != PROTOCOL_VERSION:
        return Invalid(
            (
                "protocol_version_mismatch: got "
                + repr(data["protocol_version"])
                + ", expected "
                + repr(PROTOCOL_VERSION),
            )
        )

    contradictions = contradiction_reasons(data=data)
    if contradictions:
        return Invalid(contradictions)

    obligations_data = cast(dict[str, dict[str, object]], data["obligations"])
    obligations = {
        obligation_id: EvidenceState(cast(str, obligation["state"]))
        for obligation_id, obligation in obligations_data.items()
    }

    findings_data = cast(list[dict[str, object]], data["findings"])
    findings = tuple(
        Finding(
            id=cast(str, finding["id"]),
            categories=frozenset(
                Category(category)
                for category in cast(list[str], finding["categories"])
            ),
            extra_tags=frozenset(cast(list[str], finding["extra_tags"])),
            location=Location(
                cast(dict[str, object], finding["location"])["path"],
                cast(dict[str, object], finding["location"]).get("line"),
            ),
            evidence=cast(str, finding["evidence"]),
            severity=cast(str, finding["severity"]),
            remedy=_remedy(value=finding["remedy"]),
            behaviour_changing=cast(bool | None, finding["behaviour_changing"]),
            source_attempt=attempt_id,
        )
        for finding in findings_data
    )

    attempts_data = cast(list[dict[str, str]], data["injection_attempts"])
    injection_attempts = tuple(InjectionAttempt(**item) for item in attempts_data)
    identity_data = cast(dict[str, str], data["identity"])
    identity = HarnessIdentity(**identity_data)

    return Valid(
        Verdict(
            obligations=obligations,
            findings=findings,
            injection_attempts=injection_attempts,
            identity=identity,
            protocol_version=cast(str, data["protocol_version"]),
        )
    )


def _remedy(*, value: object) -> Remedy | None:
    if value is None:
        return None
    remedy = cast(dict[str, object], value)
    return Remedy(
        tool=cast(str, remedy["tool"]),
        paths=tuple(cast(list[str], remedy["paths"])),
        check=cast(str, remedy["check"]),
    )
