"""Validate reviewer verdicts against schemas/reviewer-verdict.json.

Rules enforced (spec #10, #11):
- Verdict must be strict valid JSON.
- Missing schema fields, contradictory fields, or a signal token embedded in prose
  (rather than as a real field) do NOT count as a completed review.
- `signal` is only accepted when it is an actual JSON string field inside the object.
"""

from __future__ import annotations

import json
import pathlib
import re
import sys
from typing import Any

SCHEMA_DIR = pathlib.Path(__file__).resolve().parent.parent / "schemas"
REVIEW_SCHEMA = SCHEMA_DIR / "reviewer-verdict.json"


VALID_RECOMMENDATIONS = {"clean", "findings", "human"}
VALID_SIGNALS = {
    "SUPPORTED",
    "DEFECTS_FOUND",
    "MISSING_EVIDENCE",
    "INSUFFICIENT_CAPABILITY",
    "MATERIAL_DISAGREEMENT",
    "HUMAN_RESERVED",
}
FINDING_FIELDS = ("severity", "title", "location", "evidence", "primary_source")

# Signal/recommendation pairs that cannot both be true for a coherent review.
_CONTRADICTIONS = (
    # clear signal demands a clear recommendation
    (lambda d: d.get("signal") == "SUPPORTED" and d.get("recommendation") not in (None, "clean"), "SUPPORTED signal conflicts with recommendation"),
    (lambda d: d.get("signal") in ("MISSING_EVIDENCE", "INSUFFICIENT_CAPABILITY", "MATERIAL_DISAGREEMENT", "HUMAN_RESERVED") and d.get("recommendation") == "clean", "signal conflicts with clean recommendation"),
    # SUPPORTED and clean both require no findings
    (lambda d: d.get("signal") == "SUPPORTED" and bool(d.get("findings")), "SUPPORTED signal conflicts with findings"),
    (lambda d: d.get("recommendation") == "clean" and bool(d.get("findings")), "clean recommendation conflicts with findings"),
    # DEFECTS_FOUND asserts a completed review that located real defects, so it
    # must carry at least one finding and must not claim the change is clean.
    (lambda d: d.get("signal") == "DEFECTS_FOUND" and not d.get("findings"), "DEFECTS_FOUND signal requires at least one finding"),
    (lambda d: d.get("signal") == "DEFECTS_FOUND" and d.get("recommendation") == "clean", "DEFECTS_FOUND signal conflicts with clean recommendation"),
)


class VerdictError(Exception):
    pass


def load_review_schema() -> dict[str, Any]:
    with REVIEW_SCHEMA.open(encoding="utf-8") as handle:
        return json.load(handle)


#: Matches ONE markdown fence that wraps the ENTIRE payload. Anchored at both
#: ends on purpose: if any prose sits outside the fence the match fails and the
#: verdict is rejected, so this never extracts JSON out of surrounding prose.
_FULL_PAYLOAD_FENCE = re.compile(
    r"\A```[ \t]*[A-Za-z0-9_+.-]*[ \t]*\r?\n(?P<body>.*?)\r?\n?[ \t]*```\Z",
    re.DOTALL,
)


def strip_code_fence(text: str) -> str:
    """Strip one markdown fence when it wraps the whole payload, else return as-is.

    Several models reliably emit an otherwise-correct verdict inside a ```json
    fence. Removing that wrapper is a formatting normalisation, not a relaxation:
    the signal is still read from a parsed JSON field, and a fence with prose
    outside it does not match, so a prose-embedded signal stays rejected.
    """
    if not text:
        return ""
    stripped = text.strip()
    match = _FULL_PAYLOAD_FENCE.match(stripped)
    if match is None:
        return stripped
    return match.group("body").strip()


def parse_verdict(text: str) -> dict[str, Any]:
    """Parse strict JSON. Raises VerdictError on malformed JSON (not a completed review)."""
    try:
        return json.loads(strip_code_fence(text))
    except json.JSONDecodeError as exc:
        raise VerdictError(f"malformed review JSON: {exc.msg}") from exc


def signal_from_verdict(text: str) -> str:
    """Return the signal ONLY from a real JSON field. A signal token in prose is
    explicitly rejected (returns "")."""
    try:
        data = parse_verdict(text)
    except VerdictError:
        return ""
    if not isinstance(data, dict):
        return ""
    sig = data.get("signal")
    if not isinstance(sig, str):
        return ""
    sig = sig.strip().upper()
    return sig if sig in VALID_SIGNALS else ""


def validate_structure(text: str) -> tuple[bool, list[str]]:
    """Strict structural validation of a complete review verdict.

    Returns (ok, issues). A review is 'complete' only when ok is True.
    """
    data = parse_verdict_or_none(text)
    issues: list[str] = []
    if data is None:
        issues.append("malformed JSON")
        return False, issues
    if not isinstance(data, dict):
        issues.append("verdict is not an object")
        return False, issues
    sig = data.get("signal")
    if sig not in VALID_SIGNALS:
        issues.append(f"invalid or missing signal field: {sig!r}")
    for field in ("summary", "findings", "good"):
        if field not in data:
            issues.append(f"missing required field: {field}")
    if not isinstance(data.get("findings", []), list):
        issues.append("findings must be a list")
    if not isinstance(data.get("good", []), list):
        issues.append("good must be a list")
    return not issues, issues


def parse_verdict_or_none(text: str) -> dict[str, Any] | None:
    try:
        return json.loads(strip_code_fence(text))
    except json.JSONDecodeError:
        return None




def _check_type(issues: list[str], data: dict[str, Any], field: str, expect: type) -> None:
    # Missing fields are reported once by the schema required-loop; this helper
    # only flags a present field whose value has the wrong type.
    if field in data and not isinstance(data[field], expect):
        issues.append(f"field {field!r} must be {expect.__name__}")


def validate_verdict(text: str) -> tuple[bool, list[str]]:
    """Full, schema-driven validation of a complete review verdict.

    A verdict only passes when it is strict JSON with every schema-required
    field present and well-typed, its `signal` is a real JSON string field (a
    token embedded in prose is not accepted), and no two fields contradict each
    other. This is the gate used to decide whether a reviewer slot is filled.
    Returns (ok, issues); ok is True only when every check passes.
    """
    try:
        data = parse_verdict(text)
    except VerdictError as exc:
        return False, [f"malformed JSON: {exc}"]
    if not isinstance(data, dict):
        return False, ["verdict is not an object"]

    schema = load_review_schema()
    issues: list[str] = []
    for field in schema.get("required", []):
        if field not in data:
            issues.append(f"missing required field: {field}")

    signal = data.get("signal")
    if not isinstance(signal, str) or signal not in VALID_SIGNALS:
        issues.append(f"invalid or missing signal field: {signal!r}")
    recommendation = data.get("recommendation")
    if not isinstance(recommendation, str) or recommendation not in VALID_RECOMMENDATIONS:
        issues.append(f"invalid or missing recommendation field: {recommendation!r}")

    _check_type(issues, data, "summary", str)
    findings = data.get("findings")
    if isinstance(findings, list):
        for idx, finding in enumerate(findings):
            if not isinstance(finding, dict):
                issues.append(f"findings[{idx}] must be an object")
                continue
            for ffind in FINDING_FIELDS:
                if finding.get(ffind) is None:
                    issues.append(f"findings[{idx}] missing required field: {ffind}")
    else:
        issues.append("findings must be a list")
    _check_type(issues, data, "good", list)
    _check_type(issues, data, "missing_evidence", list)

    for predicate, reason in _CONTRADICTIONS:
        if predicate(data):
            issues.append(f"contradictory fields: {reason}")

    return not issues, issues


def read_verdict(path: pathlib.Path) -> dict[str, Any] | None:
    try:
        return parse_verdict_or_none(path.read_text(encoding="utf-8"))
    except OSError:
        return None