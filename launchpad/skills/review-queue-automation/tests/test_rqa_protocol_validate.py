from __future__ import annotations

import json
import pathlib
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from rqa.protocol.types import (  # noqa: E402
    Category,
    EvidenceState,
    Invalid,
    Valid,
)
from rqa.protocol.validate import ProtocolError, validate  # noqa: E402
from rqa.protocol.version import PROTOCOL_VERSION  # noqa: E402


_SHA256 = "a" * 64


def _valid_payload() -> dict[str, object]:
    return {
        "protocol_version": PROTOCOL_VERSION,
        "identity": {
            "harness": "codex",
            "model": "gpt-test",
            "provider": "example",
        },
        "obligations": {
            "O-1": {"state": "not_verified", "findings": []},
        },
        "findings": [],
        "injection_attempts": [],
    }


def _finding(
    *,
    finding_id: str = "f1",
    categories: list[str] | None = None,
    evidence: str = "Observed a failing check.",
    remedy: dict[str, object] | None = None,
    behaviour_changing: bool | None = None,
) -> dict[str, object]:
    return {
        "id": finding_id,
        "categories": ["correctness"] if categories is None else categories,
        "extra_tags": [],
        "location": {"path": "src/main.py", "line": 12},
        "evidence": evidence,
        "severity": "high",
        "remedy": remedy,
        "behaviour_changing": behaviour_changing,
        "source_attempt": "untrusted-harness-value",
    }


def _validate_payload(
    *, payload: object | str, attempt_id: str = "attempt-1", fenced: bool = False
) -> Valid | Invalid:
    text = payload if isinstance(payload, str) else json.dumps(payload)
    if fenced:
        text = f"```json\n{text}\n```"
    with tempfile.TemporaryDirectory() as directory:
        path = pathlib.Path(directory) / "verdict.json"
        path.write_text(text, encoding="utf-8")
        return validate(path=path, attempt_id=attempt_id)


def _assert_malformed(*, result: Valid | Invalid) -> None:
    assert isinstance(result, Invalid)
    assert len(result.reasons) == 1
    assert result.reasons[0].startswith("malformed_json: ")


def test_t1_blank_or_non_string_attempt_id_raises_protocol_error() -> None:
    with tempfile.TemporaryDirectory() as directory:
        path = pathlib.Path(directory) / "verdict.json"
        path.write_text(json.dumps(_valid_payload()), encoding="utf-8")
        for attempt_id in ("", None, 7):
            try:
                validate(path=path, attempt_id=attempt_id)  # type: ignore[arg-type]
            except ProtocolError:
                pass
            else:
                raise AssertionError(f"attempt_id {attempt_id!r} did not raise")


def test_t2_unreadable_verdict_returns_invalid() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = pathlib.Path(directory)
        assert validate(path=root / "missing.json", attempt_id="a") == Invalid(
            ("unreadable",)
        )
        assert validate(path=root, attempt_id="a") == Invalid(("unreadable",))
        binary = root / "binary.json"
        binary.write_bytes(b"\xff\xfe")
        assert validate(path=binary, attempt_id="a") == Invalid(("unreadable",))


def test_t3_whitespace_only_payload_is_empty() -> None:
    assert _validate_payload(payload="   \n") == Invalid(("empty_payload",))


def test_t4_single_complete_fence_is_normalized() -> None:
    assert isinstance(_validate_payload(payload=_valid_payload(), fenced=True), Valid)


def test_t5_prose_before_fence_is_not_repaired() -> None:
    encoded = json.dumps(_valid_payload())
    _assert_malformed(
        result=_validate_payload(
            payload=f"Here is the verdict.\n```json\n{encoded}\n```"
        )
    )


def test_t6_two_fences_are_not_repaired() -> None:
    encoded = json.dumps(_valid_payload())
    _assert_malformed(
        result=_validate_payload(
            payload=f"```json\n{encoded}\n```\n```json\n{encoded}\n```"
        )
    )


def test_t7_unclosed_fence_is_malformed_json() -> None:
    _assert_malformed(
        result=_validate_payload(payload=f"```json\n{json.dumps(_valid_payload())}")
    )


def test_t8_invalid_json_is_rejected() -> None:
    _assert_malformed(result=_validate_payload(payload="not json{"))


def test_t9_non_object_json_is_rejected() -> None:
    assert _validate_payload(payload=[]) == Invalid(("not_an_object",))


def test_t10_missing_top_level_identity_is_named() -> None:
    payload = _valid_payload()
    del payload["identity"]
    assert _validate_payload(payload=payload) == Invalid(
        ("missing required field: identity",)
    )


def test_t11_missing_finding_categories_is_named() -> None:
    payload = _valid_payload()
    finding = _finding()
    del finding["categories"]
    payload["findings"] = [finding]
    result = _validate_payload(payload=payload)
    assert isinstance(result, Invalid)
    assert "findings[0]: missing required field: categories" in result.reasons


def test_t12_unexpected_finding_property_is_named() -> None:
    payload = _valid_payload()
    finding = _finding()
    finding["notes"] = "not in the wire format"
    payload["findings"] = [finding]
    result = _validate_payload(payload=payload)
    assert isinstance(result, Invalid)
    assert "findings[0]: unexpected property 'notes'" in result.reasons


def test_t13_unknown_evidence_state_is_rejected() -> None:
    payload = _valid_payload()
    obligations = payload["obligations"]
    assert isinstance(obligations, dict)
    obligations["O-1"] = {"state": "maybe", "findings": []}
    result = _validate_payload(payload=payload)
    assert isinstance(result, Invalid)
    assert len(result.reasons) == 1
    assert "obligations.O-1.state" in result.reasons[0]
    assert "'maybe'" in result.reasons[0]


def test_t14_all_seven_evidence_states_are_valid() -> None:
    for state in EvidenceState:
        payload = _valid_payload()
        obligations = payload["obligations"]
        assert isinstance(obligations, dict)
        obligations["O-1"] = {"state": state.value, "findings": []}
        result = _validate_payload(payload=payload)
        assert isinstance(result, Valid), (state, result)
        assert result.verdict.obligations == {"O-1": state}


def test_t15_protocol_version_mismatch_is_distinct() -> None:
    payload = _valid_payload()
    payload["protocol_version"] = "999"
    assert _validate_payload(payload=payload) == Invalid(
        (
            "protocol_version_mismatch: got "
            + repr("999")
            + ", expected "
            + repr(PROTOCOL_VERSION),
        )
    )


def test_t16_verified_obligation_cannot_cite_a_finding() -> None:
    payload = _valid_payload()
    payload["findings"] = [_finding()]
    payload["obligations"] = {
        "O-1": {"state": "verified", "findings": ["f1"]}
    }
    assert _validate_payload(payload=payload) == Invalid(
        ("obligation_verified_but_cited: O-1",)
    )


def test_t17_whitespace_only_finding_evidence_is_rejected() -> None:
    payload = _valid_payload()
    payload["findings"] = [_finding(evidence=" \t\n")]
    assert _validate_payload(payload=payload) == Invalid(("empty_evidence: f1",))


def test_t18_duplicate_finding_ids_are_rejected_once() -> None:
    payload = _valid_payload()
    payload["findings"] = [_finding(), _finding()]
    assert _validate_payload(payload=payload) == Invalid(
        ("duplicate_finding_id: f1",)
    )


def test_t19_unknown_finding_citation_is_rejected() -> None:
    payload = _valid_payload()
    payload["obligations"] = {
        "O-1": {"state": "not_verified", "findings": ["ghost"]}
    }
    assert _validate_payload(payload=payload) == Invalid(
        ("unknown_finding_reference: O-1 -> ghost",)
    )


def test_t20_rich_finding_is_preserved_and_attempt_is_overwritten() -> None:
    payload = _valid_payload()
    payload["findings"] = [
        {
            **_finding(
                categories=["mechanical", "security"],
                remedy={
                    "tool": "ruff",
                    "paths": ["src/main.py", "tests/test_main.py"],
                    "check": "lint",
                },
                behaviour_changing=False,
            ),
            "extra_tags": ["performance", "maintainability"],
        }
    ]
    result = _validate_payload(payload=payload, attempt_id="trusted-attempt")
    assert isinstance(result, Valid)
    finding = result.verdict.findings[0]
    assert finding.categories == frozenset(
        {Category.MECHANICAL, Category.SECURITY}
    )
    assert finding.extra_tags == frozenset({"performance", "maintainability"})
    assert finding.location.path == "src/main.py"
    assert finding.location.line == 12
    assert finding.remedy is not None
    assert finding.remedy.tool == "ruff"
    assert finding.remedy.paths == ("src/main.py", "tests/test_main.py")
    assert finding.remedy.check == "lint"
    assert finding.behaviour_changing is False
    assert finding.source_attempt == "trusted-attempt"


def test_t21_empty_and_unknown_categories_are_invalid() -> None:
    empty = _valid_payload()
    empty["findings"] = [_finding(categories=[])]
    empty_result = _validate_payload(payload=empty)
    assert isinstance(empty_result, Invalid)
    assert any(
        "categories" in reason and "at least" in reason
        for reason in empty_result.reasons
    )

    unknown = _valid_payload()
    unknown["findings"] = [_finding(categories=["style"])]
    unknown_result = _validate_payload(payload=unknown)
    assert isinstance(unknown_result, Invalid)
    assert any(
        "categories[0]" in reason and "'style'" in reason
        for reason in unknown_result.reasons
    )


def test_t22_invalid_remedy_paths_are_rejected() -> None:
    invalid_paths = (
        "/absolute.py",
        "src/../escape.py",
        "src\\windows.py",
        "src/*.py",
        "src/?.py",
        "src/[ab].py",
    )
    for invalid_path in invalid_paths:
        payload = _valid_payload()
        payload["findings"] = [
            _finding(
                remedy={
                    "tool": "ruff",
                    "paths": [invalid_path],
                    "check": "lint",
                }
            )
        ]
        assert _validate_payload(payload=payload) == Invalid(
            (f"invalid_remedy_path: f1 -> {invalid_path}",)
        )

    for paths in ([""], ["src/main.py", "src/main.py"]):
        payload = _valid_payload()
        payload["findings"] = [
            _finding(remedy={"tool": "ruff", "paths": paths, "check": "lint"})
        ]
        assert isinstance(_validate_payload(payload=payload), Invalid)


def test_t23_substantive_finding_with_exact_remedy_remains_valid() -> None:
    payload = _valid_payload()
    payload["findings"] = [
        _finding(
            categories=["security"],
            remedy={"tool": "ruff", "paths": ["src/main.py"], "check": "lint"},
        )
    ]
    assert isinstance(_validate_payload(payload=payload), Valid)


def test_t24_injection_attempts_is_mandatory_even_when_empty() -> None:
    assert isinstance(_validate_payload(payload=_valid_payload()), Valid)
    omitted = _valid_payload()
    del omitted["injection_attempts"]
    result = _validate_payload(payload=omitted)
    assert isinstance(result, Invalid)
    assert "missing required field: injection_attempts" in result.reasons


def test_t25_invalid_injection_attempt_shapes_are_rejected() -> None:
    malformed_field = _valid_payload()
    malformed_field["injection_attempts"] = [
        {"field": "title", "span_hash": _SHA256, "reason": "instruction"}
    ]
    result = _validate_payload(payload=malformed_field)
    assert isinstance(result, Invalid)
    assert result.reasons[0].startswith("invalid_injection_attempt: ")

    for span_hash in ("ABC", "a" * 64 + "\n"):
        malformed_hash = _valid_payload()
        malformed_hash["injection_attempts"] = [
            {"field": "body", "span_hash": span_hash, "reason": "instruction"}
        ]
        result = _validate_payload(payload=malformed_hash)
        assert isinstance(result, Invalid)
        assert any(
            "span_hash" in reason and "pattern" in reason
            for reason in result.reasons
        )

    blank_reason = _valid_payload()
    blank_reason["injection_attempts"] = [
        {"field": "body", "span_hash": _SHA256, "reason": "  \t"}
    ]
    result = _validate_payload(payload=blank_reason)
    assert isinstance(result, Invalid)
    assert result.reasons == (
        "invalid_injection_attempt: injection_attempts[0].reason is blank",
    )

    extra_property = _valid_payload()
    extra_property["injection_attempts"] = [
        {
            "field": "body",
            "span_hash": _SHA256,
            "reason": "instruction",
            "text": "untrusted content",
        }
    ]
    result = _validate_payload(payload=extra_property)
    assert isinstance(result, Invalid)
    assert "injection_attempts[0]: unexpected property 'text'" in result.reasons


def test_t25_valid_injection_field_forms_are_accepted() -> None:
    payload = _valid_payload()
    payload["injection_attempts"] = [
        {"field": "body", "span_hash": _SHA256, "reason": "instruction"},
        {"field": "comment:123", "span_hash": "b" * 64, "reason": "instruction"},
        {
            "field": "diff:src/main.py",
            "span_hash": "c" * 64,
            "reason": "instruction",
        },
    ]
    assert isinstance(_validate_payload(payload=payload), Valid)
