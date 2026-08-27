#!/usr/bin/env python3
"""Tests for notify.py — human-request delivery.

The durable record is the SQLite queue; this module is only delivery. So the
tests assert: the packet is built from the queued row, it is bounded and free of
secrets/evidence, each transport behaves, and every failure RAISES so the caller
can preserve the queued request rather than treating it as handled.
"""

from __future__ import annotations

import json
import pathlib
import subprocess
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scripts"))

from notify import (  # noqa: E402
    MAX_FIELD,
    NotifyConfigError,
    NotifyError,
    build_packet,
    deliver,
    render_text,
    transport_of,
)


def _request(**over) -> dict:
    row = {
        "request_id": "req123",
        "job_id": "job123",
        "repo": "launchpad-26/buzz",
        "number": 42,
        "head_sha": "abc123",
        "action": "approve",
        "summary": "launchpad-26/buzz#42 needs human approval",
        "recommendation": "require human approval",
        "rationale": "protected trigger present",
        "risk_score": 30,
        "risk_band": "medium",
        "assurance": json.dumps({"capability": "frontier", "effort": "high"}),
        "reviewers": json.dumps(["claude-opus-5", "deepseek-v4-flash"]),
        "failed_gates": json.dumps(["no_protected_trigger"]),
        "protected": json.dumps([".github/workflows/release.yml"]),
        "findings": json.dumps([]),
        "expires_at": "2026-08-29T00:00:00Z",
    }
    row.update(over)
    return row


# -- packet construction ------------------------------------------------
def test_packet_carries_what_a_human_needs_to_decide() -> None:
    p = build_packet(_request())
    assert p["repo"] == "launchpad-26/buzz"
    assert p["pull_request"] == 42
    assert p["url"] == "https://github.com/launchpad-26/buzz/pull/42"
    assert p["head_sha"] == "abc123"
    assert p["action_required"] == "approve"
    assert p["failed_gates"] == ["no_protected_trigger"]
    assert p["protected_paths"] == [".github/workflows/release.yml"]
    assert p["assurance"] == {"capability": "frontier", "effort": "high"}
    assert "req123" in p["decide_with"]


def test_packet_parses_json_string_columns() -> None:
    """Queue rows store lists as JSON strings; the packet must not leak that."""
    p = build_packet(_request())
    assert isinstance(p["reviewers"], list)
    assert "claude-opus-5" in p["reviewers"]


def test_packet_tolerates_native_lists() -> None:
    p = build_packet(_request(reviewers=["a", "b"], failed_gates=["g"]))
    assert p["reviewers"] == ["a", "b"]
    assert p["failed_gates"] == ["g"]


def test_packet_omits_empty_fields() -> None:
    p = build_packet(_request(rationale="", risk_band="", findings=json.dumps([])))
    assert "rationale" not in p
    assert "risk_band" not in p
    assert "findings" not in p


def test_packet_fields_are_bounded() -> None:
    p = build_packet(_request(rationale="x" * (MAX_FIELD * 3)))
    assert len(p["rationale"]) <= MAX_FIELD + 1


def test_packet_allowlist_drops_unknown_keys() -> None:
    """The packet is built from an allowlist, so a smuggled key never reaches a
    channel at all."""
    bad = _request()
    bad["authorization"] = "Bearer zzz"
    bad["api_key"] = "sk-secret"
    packet = build_packet(bad)
    assert "authorization" not in packet
    assert "api_key" not in packet
    assert "zzz" not in json.dumps(packet)
    assert "sk-secret" not in json.dumps(packet)


def test_credential_inside_a_legitimate_field_is_redacted() -> None:
    """The live risk is a token pasted into an allowlisted field."""
    packet = build_packet(_request(rationale="failed with Bearer sk-abc123"))
    assert packet["rationale"] == "<redacted>"


def test_jwt_shaped_value_is_redacted() -> None:
    jwt = "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxIn0.dBjftJeZ4CVPmB92K27uhbUJU1p1r"
    packet = build_packet(_request(summary=f"token {jwt} leaked"))
    assert packet["summary"] == "<redacted>"


def test_redaction_applies_inside_lists() -> None:
    packet = build_packet(_request(failed_gates=json.dumps(["ok_gate", "api_key=zzz"])))
    assert "ok_gate" in packet["failed_gates"]
    assert "<redacted>" in packet["failed_gates"]
    assert "zzz" not in json.dumps(packet)


def test_rendered_text_is_self_explanatory() -> None:
    text = render_text(build_packet(_request()))
    assert "launchpad-26/buzz#42" in text
    assert "https://github.com/launchpad-26/buzz/pull/42" in text
    assert "approve" in text
    assert "no_protected_trigger" in text
    assert "req123" in text  # tells the operator how to decide


# -- transport selection ------------------------------------------------
def test_absent_section_is_none_transport() -> None:
    assert transport_of({}) == "none"


def test_unknown_transport_is_a_config_error() -> None:
    try:
        transport_of({"notifications": {"transport": "carrier-pigeon"}})
    except NotifyConfigError as exc:
        assert "must be one of" in str(exc)
    else:
        raise AssertionError("an unknown transport must fail closed")


def test_none_transport_reports_queue_only() -> None:
    record = deliver({}, _request())
    assert record["transport"] == "none"
    assert record["delivered"] is False
    assert "queued" in record["detail"]


# -- file transport -----------------------------------------------------
def test_file_transport_appends_one_json_line_per_request() -> None:
    with tempfile.TemporaryDirectory() as td:
        target = pathlib.Path(td) / "nested" / "notifications.jsonl"
        cfg = {"notifications": {"transport": "file", "path": str(target)}}

        deliver(cfg, _request())
        deliver(cfg, _request(request_id="req456", number=43))

        lines = target.read_text(encoding="utf-8").strip().splitlines()
        assert len(lines) == 2
        first = json.loads(lines[0])
        second = json.loads(lines[1])
        assert first["request_id"] == "req123"
        assert second["pull_request"] == 43


def test_file_transport_requires_a_path() -> None:
    try:
        deliver({"notifications": {"transport": "file"}}, _request())
    except NotifyConfigError as exc:
        assert "path is required" in str(exc)
    else:
        raise AssertionError("file transport without a path must fail closed")


def test_file_transport_failure_raises_so_queue_is_preserved() -> None:
    # A path whose parent cannot be created (a file stands where a dir is needed).
    with tempfile.TemporaryDirectory() as td:
        blocker = pathlib.Path(td) / "blocker"
        blocker.write_text("x", encoding="utf-8")
        cfg = {"notifications": {"transport": "file", "path": str(blocker / "out.jsonl")}}
        try:
            deliver(cfg, _request())
        except NotifyError:
            pass
        else:
            raise AssertionError("an undeliverable notification must raise")


# -- command transport --------------------------------------------------
def test_command_transport_receives_packet_and_text_on_stdin() -> None:
    seen: dict = {}

    def runner(argv, input=None, capture_output=False, timeout=None):
        seen["argv"] = argv
        seen["input"] = input
        return subprocess.CompletedProcess(argv, 0, b"", b"")

    cfg = {"notifications": {"transport": "command", "command": "notify-send --urgent"}}
    record = deliver(cfg, _request(), _runner=runner)

    assert record["delivered"] is True
    assert seen["argv"] == ["notify-send", "--urgent"]
    payload = json.loads(seen["input"].decode("utf-8"))
    assert payload["packet"]["request_id"] == "req123"
    assert "launchpad-26/buzz#42" in payload["text"]


def test_command_transport_accepts_argv_list() -> None:
    def runner(argv, input=None, capture_output=False, timeout=None):
        return subprocess.CompletedProcess(argv, 0, b"", b"")

    cfg = {"notifications": {"transport": "command", "command": ["send", "-x"]}}
    assert deliver(cfg, _request(), _runner=runner)["delivered"] is True


def test_command_nonzero_exit_raises() -> None:
    def runner(argv, input=None, capture_output=False, timeout=None):
        return subprocess.CompletedProcess(argv, 3, b"", b"upstream rejected")

    cfg = {"notifications": {"transport": "command", "command": "send"}}
    try:
        deliver(cfg, _request(), _runner=runner)
    except NotifyError as exc:
        assert "exit 3" in str(exc)
        assert "upstream rejected" in str(exc)
    else:
        raise AssertionError("a failing notification command must raise")


def test_command_timeout_raises() -> None:
    def runner(argv, input=None, capture_output=False, timeout=None):
        raise subprocess.TimeoutExpired(argv, timeout or 30)

    cfg = {"notifications": {"transport": "command", "command": "send",
                              "timeout_seconds": 5}}
    try:
        deliver(cfg, _request(), _runner=runner)
    except NotifyError as exc:
        assert "timed out" in str(exc)
    else:
        raise AssertionError("a hanging notification command must raise")


def test_command_missing_binary_raises() -> None:
    def runner(argv, input=None, capture_output=False, timeout=None):
        raise OSError("No such file or directory")

    cfg = {"notifications": {"transport": "command", "command": "definitely-absent"}}
    try:
        deliver(cfg, _request(), _runner=runner)
    except NotifyError as exc:
        assert "could not run" in str(exc)
    else:
        raise AssertionError("a missing notification binary must raise")


def test_command_transport_requires_a_command() -> None:
    try:
        deliver({"notifications": {"transport": "command"}}, _request())
    except NotifyConfigError as exc:
        assert "command is required" in str(exc)
    else:
        raise AssertionError("command transport without a command must fail closed")
