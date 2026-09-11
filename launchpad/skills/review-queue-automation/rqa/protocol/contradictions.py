"""Semantic-coherence checks for structurally valid verdict payloads."""

from __future__ import annotations

from collections import Counter
from collections.abc import Callable, Mapping
from typing import cast


Predicate = Callable[[Mapping[str, object]], tuple[str, ...]]


def contradiction_reasons(*, data: Mapping[str, object]) -> tuple[str, ...]:
    """Return every semantic contradiction in deterministic order."""
    reasons: set[str] = set()
    for predicate in _PREDICATES:
        reasons.update(predicate(data))
    return tuple(sorted(reasons))


def _duplicate_finding_ids(data: Mapping[str, object]) -> tuple[str, ...]:
    findings = cast(list[dict[str, object]], data["findings"])
    counts = Counter(cast(str, finding["id"]) for finding in findings)
    return tuple(
        f"duplicate_finding_id: {finding_id}"
        for finding_id, count in counts.items()
        if count > 1
    )


def _empty_evidence(data: Mapping[str, object]) -> tuple[str, ...]:
    findings = cast(list[dict[str, object]], data["findings"])
    return tuple(
        f"empty_evidence: {finding['id']}"
        for finding in findings
        if not cast(str, finding["evidence"]).strip()
    )


def _verified_obligations_with_citations(
    data: Mapping[str, object],
) -> tuple[str, ...]:
    obligations = cast(dict[str, dict[str, object]], data["obligations"])
    return tuple(
        f"obligation_verified_but_cited: {obligation_id}"
        for obligation_id, obligation in obligations.items()
        if obligation["state"] == "verified" and obligation.get("findings", [])
    )


def _unknown_finding_references(data: Mapping[str, object]) -> tuple[str, ...]:
    findings = cast(list[dict[str, object]], data["findings"])
    finding_ids = {cast(str, finding["id"]) for finding in findings}
    obligations = cast(dict[str, dict[str, object]], data["obligations"])
    return tuple(
        f"unknown_finding_reference: {obligation_id} -> {finding_id}"
        for obligation_id, obligation in obligations.items()
        for finding_id in cast(list[str], obligation.get("findings", []))
        if finding_id not in finding_ids
    )


def _invalid_remedy_paths(data: Mapping[str, object]) -> tuple[str, ...]:
    findings = cast(list[dict[str, object]], data["findings"])
    reasons: list[str] = []
    for finding in findings:
        remedy = cast(dict[str, object] | None, finding["remedy"])
        if remedy is None:
            continue
        paths = cast(list[str], remedy["paths"])
        counts = Counter(paths)
        for path in paths:
            if counts[path] > 1 or not _is_normalized_exact_path(path=path):
                reasons.append(
                    f"invalid_remedy_path: {finding['id']} -> {path}"
                )
    return tuple(reasons)


def _invalid_injection_attempts(data: Mapping[str, object]) -> tuple[str, ...]:
    attempts = cast(list[dict[str, object]], data["injection_attempts"])
    reasons: list[str] = []
    for index, attempt in enumerate(attempts):
        field = cast(str, attempt["field"])
        if not _is_valid_injection_field(field=field):
            reasons.append(
                f"invalid_injection_attempt: injection_attempts[{index}].field {field!r}"
            )
        if not cast(str, attempt["reason"]).strip():
            reasons.append(
                f"invalid_injection_attempt: injection_attempts[{index}].reason is blank"
            )
    return tuple(reasons)


def _is_valid_injection_field(*, field: str) -> bool:
    if field == "body":
        return True
    if field.startswith("comment:"):
        return bool(field.removeprefix("comment:").strip())
    if field.startswith("diff:"):
        return _is_normalized_exact_path(path=field.removeprefix("diff:"))
    return False


def _is_normalized_exact_path(*, path: str) -> bool:
    if not path or path.startswith("/") or "\\" in path:
        return False
    if any(character in path for character in "*?[]"):
        return False
    return all(segment not in {"", ".", ".."} for segment in path.split("/"))


_PREDICATES: tuple[Predicate, ...] = (
    _duplicate_finding_ids,
    _empty_evidence,
    _verified_obligations_with_citations,
    _unknown_finding_references,
    _invalid_remedy_paths,
    _invalid_injection_attempts,
)
