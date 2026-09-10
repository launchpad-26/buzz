#!/usr/bin/env python3
"""Counterexample tests for every schema: verdict, author-triage, config, policy.

A counterexample test asserts the guard REJECTS the bad input. Asserting the
happy path works is not coverage — a validator that returns `[]` for everything
passes that and rejects nothing.

Each test below names the exact mutation that makes it pass against a broken
implementation, so a later reader can re-run the mutation check.
"""

from __future__ import annotations

import json
import pathlib
import re
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import config as cfgmod  # noqa: E402
import policy as policymod  # noqa: E402
import verdict as verdictmod  # noqa: E402

SCHEMAS = ROOT / "schemas"


# --------------------------------------------------------------------------
# 1. reviewer-verdict schema
# --------------------------------------------------------------------------

_GOOD_VERDICT = {
    "signal": "SUPPORTED",
    "recommendation": "clean",
    "summary": "no defects",
    "findings": [],
    "good": ["clear naming"],
    "missing_evidence": [],
}


def _verdict(**over) -> str:
    body = dict(_GOOD_VERDICT)
    body.update(over)
    return json.dumps(body)


def test_the_control_verdict_is_accepted() -> None:
    """Not a counterexample — the control. Without it, a validator that rejects
    EVERYTHING would pass every test below while accepting no real review."""
    ok, issues = verdictmod.validate_verdict(_verdict())
    assert ok, issues


def test_malformed_json_is_not_a_completed_review() -> None:
    for bad in ('{"signal": "SUPPORTED"', "", "   ", "not json at all", "[]", "null"):
        ok, issues = verdictmod.validate_verdict(bad)
        assert not ok, f"{bad!r} must be rejected"
        assert issues


def test_truncated_verdict_is_rejected() -> None:
    full = _verdict()
    for cut in (len(full) // 2, len(full) - 1, len(full) - 10):
        ok, _ = verdictmod.validate_verdict(full[:cut])
        assert not ok, f"a verdict truncated at {cut} must be rejected"


def test_signal_embedded_in_prose_is_not_a_signal() -> None:
    """The signal must be a real JSON string field. A model that writes
    'my verdict is SUPPORTED' in prose has not filled the slot."""
    prose = "After careful review my verdict is SUPPORTED. No defects were found."
    assert verdictmod.signal_from_verdict(prose) == ""
    ok, _ = verdictmod.validate_verdict(prose)
    assert not ok
    # ...and the same token inside a legitimate string field is still not the signal
    payload = _verdict(summary="the change is SUPPORTED by the tests", signal="not-a-signal")
    assert verdictmod.signal_from_verdict(payload) == ""
    # A NON-STRING signal must not be coerced into one. This is the branch that
    # separates "read the field" from "find the token somewhere in the payload":
    # a list, dict or bool here has to yield no signal at all.
    for shape in (["SUPPORTED"], {"value": "SUPPORTED"}, True, 1, None):
        assert verdictmod.signal_from_verdict(_verdict(signal=shape)) == "", shape
        assert not verdictmod.validate_verdict(_verdict(signal=shape))[0], shape


def test_a_fence_with_prose_outside_it_is_rejected() -> None:
    """`strip_code_fence` normalises ONE fence wrapping the WHOLE payload. It must
    never extract JSON out of surrounding commentary."""
    fenced_only = "```json\n" + _verdict() + "\n```"
    assert verdictmod.validate_verdict(fenced_only)[0], "a whole-payload fence is normalised"
    # Prose BEFORE the fence. `re.match` already anchors the start, so this alone
    # does not exercise the trailing anchor.
    leading = "Here is my review:\n```json\n" + _verdict() + "\n```"
    assert not verdictmod.validate_verdict(leading)[0], "prose before the fence must reject"
    # Prose AFTER the fence. This is the case the `\Z` anchor exists for: without
    # it the fence still matches from position 0 and the commentary is silently
    # discarded, so a model that appends its own summary would be accepted.
    trailing = "```json\n" + _verdict() + "\n```\nHope that helps!"
    assert not verdictmod.validate_verdict(trailing)[0], "prose after the fence must reject"
    both = "Here is my review:\n```json\n" + _verdict() + "\n```\nHope that helps!"
    assert not verdictmod.validate_verdict(both)[0], "prose around the fence must reject"


def test_every_required_schema_field_is_individually_required() -> None:
    schema = json.loads((SCHEMAS / "reviewer-verdict.json").read_text(encoding="utf-8"))
    required = schema["required"]
    assert required, "the schema must declare required fields"
    for field in required:
        body = dict(_GOOD_VERDICT)
        body.pop(field)
        ok, issues = verdictmod.validate_verdict(json.dumps(body))
        assert not ok, f"a verdict missing {field!r} must be rejected"
        assert any(field in issue for issue in issues), (field, issues)


def test_invalid_enum_members_are_rejected() -> None:
    for signal in ("APPROVED", "supported", "", None, 1, ["SUPPORTED"]):
        ok, _ = verdictmod.validate_verdict(_verdict(signal=signal))
        assert not ok, f"signal {signal!r} must be rejected"
    for rec in ("approve", "CLEAN", "", None, 0):
        ok, _ = verdictmod.validate_verdict(_verdict(recommendation=rec))
        assert not ok, f"recommendation {rec!r} must be rejected"


def test_every_contradiction_pair_is_rejected() -> None:
    """One counterexample per contradiction rule in verdict._CONTRADICTIONS."""
    finding = {"severity": "high", "title": "t", "location": "a.py:1",
               "evidence": "e", "primary_source": "s"}
    cases = [
        # SUPPORTED signal with a non-clean recommendation
        _verdict(signal="SUPPORTED", recommendation="findings", findings=[finding]),
        # a non-clean signal claiming a clean recommendation
        _verdict(signal="MISSING_EVIDENCE", recommendation="clean"),
        _verdict(signal="INSUFFICIENT_CAPABILITY", recommendation="clean"),
        _verdict(signal="MATERIAL_DISAGREEMENT", recommendation="clean"),
        _verdict(signal="HUMAN_RESERVED", recommendation="clean"),
        # SUPPORTED with findings
        _verdict(signal="SUPPORTED", recommendation="clean", findings=[finding]),
        # DEFECTS_FOUND with no finding at all
        _verdict(signal="DEFECTS_FOUND", recommendation="findings", findings=[]),
        # DEFECTS_FOUND claiming clean
        _verdict(signal="DEFECTS_FOUND", recommendation="clean", findings=[finding]),
    ]
    for payload in cases:
        ok, issues = verdictmod.validate_verdict(payload)
        assert not ok, f"contradiction not caught: {payload}"
        assert any("contradict" in i or "conflict" in i for i in issues), issues


def test_a_finding_missing_any_required_subfield_is_rejected() -> None:
    complete = {"severity": "high", "title": "t", "location": "a.py:1",
                "evidence": "e", "primary_source": "s"}
    for field in verdictmod.FINDING_FIELDS:
        partial = dict(complete)
        partial.pop(field)
        ok, issues = verdictmod.validate_verdict(
            _verdict(signal="DEFECTS_FOUND", recommendation="findings", findings=[partial])
        )
        assert not ok, f"a finding missing {field!r} must be rejected"
        assert any(field in i for i in issues), (field, issues)
    # a non-object finding is rejected too
    ok, _ = verdictmod.validate_verdict(
        _verdict(signal="DEFECTS_FOUND", recommendation="findings", findings=["just a string"])
    )
    assert not ok


def test_wrongly_typed_containers_are_rejected() -> None:
    for over in ({"findings": {}}, {"findings": "none"}, {"good": "one"},
                 {"missing_evidence": "none"}, {"summary": 12}):
        ok, _ = verdictmod.validate_verdict(_verdict(**over))
        assert not ok, f"{over} must be rejected"


# --------------------------------------------------------------------------
# 2. author-triage schema
# --------------------------------------------------------------------------
#
# NOTE: `schemas/author-triage.json` currently has NO production validator — no
# module imports it. These tests therefore exercise the schema ARTEFACT with a
# minimal checker defined here, so the schema's own constraints are known to
# reject bad documents. When the author-triage lane lands a real validator it
# should be pointed at this schema and these counterexamples reused against it.


def _check(schema: dict, doc: object, path: str = "$") -> list[str]:
    """A deliberately small JSON-Schema subset checker.

    Supports exactly the keywords these two schemas use: type, enum, required,
    properties, additionalProperties:false, items, minLength, minimum, pattern.
    It exists to test the schema documents themselves, not to become a runtime
    validator.
    """
    issues: list[str] = []
    types = {"object": dict, "array": list, "string": str, "integer": int}
    expect = schema.get("type")
    if expect and not isinstance(doc, types[expect]):
        return [f"{path}: expected {expect}"]
    if expect == "integer" and isinstance(doc, bool):
        return [f"{path}: bool is not an integer"]
    if "enum" in schema and doc not in schema["enum"]:
        issues.append(f"{path}: {doc!r} not in enum")
    if isinstance(doc, str):
        if len(doc) < schema.get("minLength", 0):
            issues.append(f"{path}: shorter than minLength")
        pattern = schema.get("pattern")
        if pattern and not re.search(pattern, doc):
            issues.append(f"{path}: does not match {pattern}")
    if isinstance(doc, int) and not isinstance(doc, bool) and "minimum" in schema:
        if doc < schema["minimum"]:
            issues.append(f"{path}: below minimum")
    if isinstance(doc, dict):
        properties = schema.get("properties", {})
        for field in schema.get("required", []):
            if field not in doc:
                issues.append(f"{path}: missing required field {field}")
        if schema.get("additionalProperties") is False:
            for key in doc:
                if key not in properties:
                    issues.append(f"{path}: unknown field {key}")
        for key, value in doc.items():
            if key in properties:
                issues.extend(_check(properties[key], value, f"{path}.{key}"))
    if isinstance(doc, list) and "items" in schema:
        for index, item in enumerate(doc):
            issues.extend(_check(schema["items"], item, f"{path}[{index}]"))
    return issues


_TRIAGE_SCHEMA = json.loads((SCHEMAS / "author-triage.json").read_text(encoding="utf-8"))

_GOOD_TRIAGE = {
    "signal": "SUPPORTED",
    "summary": "two comments triaged",
    "findings": [{
        "comment_id": 12,
        "classification": "VALID",
        "location": "scripts/a.py:10",
        "evidence": "the assertion is off by one",
        "action": "fixed in commit abc123",
    }],
}


def test_the_control_triage_document_is_accepted() -> None:
    assert _check(_TRIAGE_SCHEMA, _GOOD_TRIAGE) == []


def test_triage_schema_rejects_every_missing_required_field() -> None:
    for field in _TRIAGE_SCHEMA["required"]:
        doc = {k: v for k, v in _GOOD_TRIAGE.items() if k != field}
        assert _check(_TRIAGE_SCHEMA, doc), f"missing {field} must be rejected"


def test_triage_schema_rejects_a_defects_found_signal() -> None:
    """author-triage deliberately has a NARROWER signal enum than the reviewer
    verdict: DEFECTS_FOUND and the 'clean/findings/human' recommendation do not
    exist on this surface."""
    assert "DEFECTS_FOUND" not in _TRIAGE_SCHEMA["properties"]["signal"]["enum"]
    doc = dict(_GOOD_TRIAGE, signal="DEFECTS_FOUND")
    assert _check(_TRIAGE_SCHEMA, doc)


def test_triage_schema_rejects_unknown_fields_and_bad_classifications() -> None:
    assert _check(_TRIAGE_SCHEMA, dict(_GOOD_TRIAGE, recommendation="clean")), \
        "additionalProperties:false must reject an unknown top-level field"
    for bad in ("valid", "REJECTED", "", 1):
        doc = json.loads(json.dumps(_GOOD_TRIAGE))
        doc["findings"][0]["classification"] = bad
        assert _check(_TRIAGE_SCHEMA, doc), f"classification {bad!r} must be rejected"


def test_triage_schema_rejects_a_non_positive_comment_id() -> None:
    for bad in (0, -1):
        doc = json.loads(json.dumps(_GOOD_TRIAGE))
        doc["findings"][0]["comment_id"] = bad
        assert _check(_TRIAGE_SCHEMA, doc), f"comment_id {bad} must be rejected"
    doc = json.loads(json.dumps(_GOOD_TRIAGE))
    doc["findings"][0]["comment_id"] = "12"
    assert _check(_TRIAGE_SCHEMA, doc), "a string comment_id must be rejected"


def test_triage_schema_rejects_empty_evidence_and_action() -> None:
    for field in ("location", "evidence", "action"):
        doc = json.loads(json.dumps(_GOOD_TRIAGE))
        doc["findings"][0][field] = ""
        assert _check(_TRIAGE_SCHEMA, doc), f"empty {field} must be rejected"


def test_the_subset_checker_itself_rejects_things() -> None:
    """Guards the guard: a checker that always returns [] would make every
    counterexample above pass while proving nothing."""
    assert _check({"type": "object", "required": ["a"]}, {}) != []
    assert _check({"type": "string", "minLength": 1}, "") != []
    assert _check({"enum": ["x"]}, "y") != []
    assert _check({"type": "object", "additionalProperties": False, "properties": {}}, {"z": 1}) != []
    assert _check({"type": "integer", "minimum": 1}, 0) != []
    assert _check({"type": "string", "pattern": "^a+$"}, "b") != []
    # ...and accepts a valid one, so it is not simply always-reject
    assert _check({"type": "string", "minLength": 1}, "ok") == []


# --------------------------------------------------------------------------
# 3. config schema
# --------------------------------------------------------------------------


def _git_repo() -> pathlib.Path:
    root = pathlib.Path(tempfile.mkdtemp()).resolve()
    subprocess.run(["git", "init", "-q"], cwd=root, check=True, capture_output=True)
    (root / ".gitignore").write_text(
        ".review-queue-automation/\npr review logs\n", encoding="utf-8")
    return root


def _base_config(root: pathlib.Path) -> dict:
    cfg = cfgmod.onboarding_defaults(root)
    cfg["login"] = "op"
    cfg["repository"]["slug"] = "o/r"
    (root / cfgmod.DEFAULT_LOG_DIR_NAME).mkdir(exist_ok=True)
    return cfg


def test_the_control_config_is_accepted() -> None:
    root = _git_repo()
    assert cfgmod.validate_config(_base_config(root), root) == []


def test_config_rejects_every_missing_required_key() -> None:
    root = _git_repo()
    for key in sorted(cfgmod.REQUIRED_KEYS):
        cfg = _base_config(root)
        cfg.pop(key)
        issues = cfgmod.validate_config(cfg, root)
        assert issues, f"config missing {key!r} must be rejected"
        assert key in issues[0]


def test_config_rejects_a_concurrency_above_one() -> None:
    """A state directory has exactly one worker. Advertising more would promise
    concurrency the dispatcher refuses, so it is a config error, not a clamp."""
    root = _git_repo()
    for value in (2, 0, -1, True, "1", 1.0):
        cfg = _base_config(root)
        cfg["dispatch"]["incoming_concurrency"] = value
        assert any("incoming_concurrency" in i for i in cfgmod.validate_config(cfg, root)), value


def test_config_rejects_secret_like_keys_at_any_depth() -> None:
    root = _git_repo()
    for path, key in (("github", "token"), ("models", "api_key"),
                      ("repository", "client_secret"), ("approval", "password")):
        cfg = _base_config(root)
        cfg[path][key] = "value"
        issues = cfgmod.validate_config(cfg, root)
        assert any("secret-like" in i for i in issues), (path, key, issues)
    # nested three deep is still found
    cfg = _base_config(root)
    cfg["models"]["primary"] = [{"runner": "omp", "selector": "m", "provider_family": "x",
                                 "capability": "frontier", "efforts": ["low"],
                                 "private_key": "shh"}]
    assert any("secret-like" in i for i in cfgmod.validate_config(cfg, root))


def test_config_rejects_live_approval_without_its_canary_or_triggers() -> None:
    root = _git_repo()
    cfg = _base_config(root)
    cfg["approval"]["mode"] = "live"
    cfg["approval"]["live_canary_approved"] = False
    assert any("live_canary_approved" in i for i in cfgmod.validate_config(cfg, root))
    cfg["approval"]["live_canary_approved"] = True
    cfg["risk"]["protected_triggers"] = []
    assert any("protected_triggers" in i for i in cfgmod.validate_config(cfg, root))


def test_config_rejects_an_uncompilable_protected_trigger() -> None:
    """A typo in a protected-trigger regex must fail at config load, never at
    match time — silently skipping it would widen the approval surface."""
    root = _git_repo()
    cfg = _base_config(root)
    cfg["risk"]["protected_triggers"] = ["(unclosed"]
    assert any("not a valid regex" in i for i in cfgmod.validate_config(cfg, root))
    cfg["risk"]["protected_triggers"] = [123]
    assert any("must be a string" in i for i in cfgmod.validate_config(cfg, root))


def test_config_rejects_a_model_entry_missing_any_identity_field() -> None:
    root = _git_repo()
    complete = {"runner": "omp", "selector": "m", "provider_family": "x",
                "capability": "frontier", "efforts": ["low"]}
    for field in ("runner", "selector", "provider_family", "capability"):
        cfg = _base_config(root)
        entry = dict(complete)
        entry[field] = ""
        cfg["models"]["primary"] = [entry]
        assert any(field in i for i in cfgmod.validate_config(cfg, root)), field
    cfg = _base_config(root)
    cfg["models"]["primary"] = [{k: v for k, v in complete.items() if k != "efforts"}]
    assert any("efforts" in i for i in cfgmod.validate_config(cfg, root))


def test_config_rejects_an_out_of_range_approval_rate_and_bad_bands() -> None:
    root = _git_repo()
    for rate in (-0.1, 1.1, "half", None):
        cfg = _base_config(root)
        cfg["approval"]["approval_rate_max"] = rate
        assert any("approval_rate_max" in i for i in cfgmod.validate_config(cfg, root)), rate
    cfg = _base_config(root)
    cfg["risk"]["bands"] = {"low": 50, "medium": 20, "high": 100}  # not monotonic
    assert any("bands" in i for i in cfgmod.validate_config(cfg, root))
    cfg = _base_config(root)
    del cfg["risk"]["bands"]["high"]
    assert any("bands" in i for i in cfgmod.validate_config(cfg, root))


def test_config_rejects_a_malformed_notifications_section() -> None:
    """Absent means no delivery, which is safe. PRESENT but malformed must be an
    error: a typo silently disabling the only alert path is not safe."""
    root = _git_repo()
    for section in ({"transport": "carrier-pigeon"},
                    {"transport": "file"},            # no path
                    {"transport": "command"},         # no command
                    {"transport": "command", "command": []},
                    {"transport": "none", "timeout_seconds": 0},
                    "not-an-object"):
        cfg = _base_config(root)
        cfg["notifications"] = section
        assert cfgmod.validate_config(cfg, root), section


def test_config_load_rejects_a_tracked_or_unignored_config() -> None:
    root = _git_repo()
    (root / ".gitignore").write_text("", encoding="utf-8")  # no longer ignored
    cfg = _base_config(root)
    path = cfgmod.repo_config_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(cfg), encoding="utf-8")
    loaded, _, issues = cfgmod.load_repo_config(root)
    assert loaded is None
    assert any("not git-ignored" in i for i in issues), issues


# --------------------------------------------------------------------------
# 4. policy schema
# --------------------------------------------------------------------------

_GOOD_POLICY = {
    "version": "p1",
    "authority": {"approve": "disabled", "comment": "live"},
    "approval": {"effective_risk_max": 24, "complexity_max": 2, "file_limit": 50,
                 "line_limit": 1000, "approval_rate_max": 0.5},
    "risk": {"bands": {"low": 24, "medium": 99, "high": 100}},
    "human_queue": {"expiry_minutes": 1440},
}


def test_the_control_policy_is_accepted() -> None:
    assert policymod.validate_policy(_GOOD_POLICY) == []


def test_policy_rejects_every_missing_required_section() -> None:
    for key in sorted(policymod.REQUIRED_KEYS):
        body = {k: v for k, v in _GOOD_POLICY.items() if k != key}
        issues = policymod.validate_policy(body)
        assert issues, f"policy missing {key} must be rejected"
        assert any(key in i for i in issues), (key, issues)


def test_policy_rejects_an_unknown_authority_mode_so_it_cannot_widen() -> None:
    for mode in ("enabled", "LIVE", "yes", True, None):
        body = json.loads(json.dumps(_GOOD_POLICY))
        body["authority"] = {"approve": mode}
        assert policymod.validate_policy(body), f"authority mode {mode!r} must be rejected"


def test_policy_rejects_negative_or_non_integer_thresholds() -> None:
    for key in ("effective_risk_max", "complexity_max", "file_limit", "line_limit"):
        for bad in (-1, "24", 2.5, True, None):
            body = json.loads(json.dumps(_GOOD_POLICY))
            body["approval"][key] = bad
            assert policymod.validate_policy(body), f"{key}={bad!r} must be rejected"


def test_policy_rejects_discontinuous_bands_and_a_bad_expiry() -> None:
    body = json.loads(json.dumps(_GOOD_POLICY))
    body["risk"]["bands"] = {"low": 99, "medium": 24, "high": 100}
    assert policymod.validate_policy(body)
    body = json.loads(json.dumps(_GOOD_POLICY))
    body["risk"] = {}
    assert any("bands is required" in i for i in policymod.validate_policy(body))
    for expiry in (0, -5, "1440", None):
        body = json.loads(json.dumps(_GOOD_POLICY))
        body["human_queue"]["expiry_minutes"] = expiry
        assert policymod.validate_policy(body), expiry


def test_validate_or_raise_raises_and_canonicalize_refuses_an_invalid_policy() -> None:
    bad = {k: v for k, v in _GOOD_POLICY.items() if k != "risk"}
    try:
        policymod.validate_or_raise(bad)
    except policymod.PolicyValidationError:
        pass
    else:
        raise AssertionError("validate_or_raise must raise on an invalid policy")
    try:
        policymod.canonicalize(bad)
    except policymod.PolicyValidationError:
        pass
    else:
        raise AssertionError("canonicalize must refuse to pin an invalid policy")


def test_policy_content_hash_changes_when_any_threshold_changes() -> None:
    """A hash that ignored a field would let a threshold change reuse a decision
    pinned to the old policy."""
    base = policymod.content_hash(_GOOD_POLICY)
    for key, value in (("effective_risk_max", 99), ("complexity_max", 9),
                       ("file_limit", 1), ("line_limit", 1)):
        body = json.loads(json.dumps(_GOOD_POLICY))
        body["approval"][key] = value
        assert policymod.content_hash(body) != base, key
    body = json.loads(json.dumps(_GOOD_POLICY))
    body["authority"]["approve"] = "live"
    assert policymod.content_hash(body) != base


if __name__ == "__main__":
    failures = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"PASS {name}")
            except Exception as exc:  # noqa: BLE001
                failures += 1
                print(f"FAIL {name}: {exc}")
    sys.exit(1 if failures else 0)
