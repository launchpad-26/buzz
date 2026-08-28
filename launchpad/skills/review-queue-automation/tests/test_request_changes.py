#!/usr/bin/env python3
"""Tests for the verified-defect request-changes path.

Two layers:
  1. `findings.py` corroboration — which findings may support an authoritative
     action at all (two distinct provider families, or one family citing a check
     that actually failed).
  2. the dispatcher path — every outcome is reachable, fail-closed by default,
     and no mutation happens without corroboration + live authority + a passing
     gate with a fresh revalidation.

No GitHub and no models: the mutation and REST transport are both intercepted.
"""

from __future__ import annotations

import pathlib
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scripts"))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import dispatcher  # noqa: E402
from assurance import Profile, classify, drive  # noqa: E402
from common import State  # noqa: E402
from findings import (  # noqa: E402
    CHECK_BACKED,
    TWO_FAMILIES,
    blocking_summary,
    corroborate,
    extract_findings,
    failing_check_names,
    verified_blockers,
)
from test_dispatch_flow import (  # noqa: E402
    _config,
    fake_panel,
    patch_dispatcher,
    restore_dispatcher,
    seed_evidence,
    seed_job,
    seed_verdicts,
)
from verdict import validate_verdict  # noqa: E402

LIVE_RC = {"request_changes": "live"}


def _finding(severity="blocker", location="src/a.py:12", evidence="expired sessions refresh",
             primary_source="src/a.py", title="auth bypass") -> dict:
    return {"severity": severity, "title": title, "location": location,
            "evidence": evidence, "primary_source": primary_source}


def _verdict(model, family, findings=None) -> dict:
    return {
        "signal": "DEFECTS_FOUND", "recommendation": "findings", "summary": "defect found",
        "findings": findings if findings is not None else [_finding()],
        "good": [], "missing_evidence": [],
        "model": model, "provider_family": family,
    }


# ============ signal + decision vocabulary ============
def test_defects_found_is_a_valid_complete_verdict() -> None:
    """The gap this closes: a completed review that located defects."""
    import json

    ok, issues = validate_verdict(json.dumps(_verdict("opus", "anthropic")))
    assert ok, issues


def test_defects_found_requires_a_finding() -> None:
    import json

    v = _verdict("opus", "anthropic", findings=[])
    ok, issues = validate_verdict(json.dumps(v))
    assert not ok
    assert any("requires at least one finding" in i for i in issues)


def test_defects_found_cannot_claim_clean() -> None:
    import json

    v = _verdict("opus", "anthropic")
    v["recommendation"] = "clean"
    ok, issues = validate_verdict(json.dumps(v))
    assert not ok


def test_unanimous_defects_yields_request_changes() -> None:
    assert classify(Profile(), ["DEFECTS_FOUND", "DEFECTS_FOUND"]) == "REQUEST_CHANGES"


def test_defects_versus_supported_is_a_disagreement_not_an_action() -> None:
    """One reviewer clean, one finding defects: escalate, never act."""
    assert classify(Profile(independence="challenger"),
                    ["DEFECTS_FOUND", "SUPPORTED"]) == "CONVENE_PANEL"
    assert classify(Profile(independence="panel"),
                    ["DEFECTS_FOUND", "SUPPORTED"]) == "HUMAN"


def test_higher_priority_signals_still_win() -> None:
    assert classify(Profile(), ["DEFECTS_FOUND", "HUMAN_RESERVED"]) == "HUMAN"
    assert classify(Profile(), ["DEFECTS_FOUND", "MISSING_EVIDENCE"]) == "GATHER_EVIDENCE"


def test_request_changes_terminates_the_escalation_loop() -> None:
    """Raising effort cannot make a located defect disappear."""
    attempts: list = []

    def assess(profile):
        attempts.append(profile)
        return ["DEFECTS_FOUND"]

    _profile, decision, steps = drive(Profile(), assess, max_steps=6)
    assert decision == "REQUEST_CHANGES"
    assert len(attempts) == 1, "must not re-run the panel after locating defects"
    assert len(steps) == 1


# ============ corroboration ============
def test_two_distinct_families_corroborate() -> None:
    results = verified_blockers([_verdict("opus", "anthropic"), _verdict("ds", "openrouter")])
    assert len(results) == 1
    assert results[0].basis == TWO_FAMILIES
    assert results[0].families == ("anthropic", "openrouter")


def test_differently_worded_reports_still_match() -> None:
    """Fingerprint is severity + location, so prose differences do not block it."""
    a = _verdict("opus", "anthropic", [_finding(title="auth bypass")])
    b = _verdict("ds", "openrouter", [_finding(title="session refresh flaw")])
    assert len(verified_blockers([a, b])) == 1


def test_single_family_is_not_corroborated() -> None:
    results = corroborate([_verdict("opus", "anthropic")])
    assert len(results) == 1
    assert results[0].verified is False
    assert results[0].basis == "single_family_uncorroborated"


def test_same_family_twice_is_not_independent() -> None:
    """Two Anthropic models are one provider family, so they cannot corroborate."""
    results = corroborate([_verdict("opus", "anthropic"), _verdict("sonnet", "anthropic")])
    assert results[0].verified is False


def test_single_family_plus_cited_failing_check_corroborates() -> None:
    results = verified_blockers(
        [_verdict("opus", "anthropic", [_finding(primary_source="ci-suite")])],
        checks=[{"name": "ci-suite", "conclusion": "FAILURE"}],
    )
    assert len(results) == 1
    assert results[0].basis == CHECK_BACKED
    assert results[0].citation == "ci-suite"


def test_passing_check_does_not_corroborate() -> None:
    results = corroborate(
        [_verdict("opus", "anthropic", [_finding(primary_source="ci-suite")])],
        checks=[{"name": "ci-suite", "conclusion": "SUCCESS"}],
    )
    assert results[0].verified is False


def test_finding_cannot_borrow_an_unrelated_failing_check() -> None:
    results = corroborate(
        [_verdict("opus", "anthropic", [_finding(primary_source="src/a.py")])],
        checks=[{"name": "lint", "conclusion": "FAILURE"}],
    )
    assert results[0].verified is False


def test_non_blocking_severities_are_not_actionable() -> None:
    for severity in ("high", "medium", "low"):
        results = corroborate([
            _verdict("opus", "anthropic", [_finding(severity=severity)]),
            _verdict("ds", "openrouter", [_finding(severity=severity)]),
        ])
        assert results == [], f"{severity} must not support a change request by default"


def test_findings_without_evidence_are_dropped() -> None:
    for missing in ("evidence", "primary_source", "location", "severity"):
        bad = _finding()
        bad[missing] = ""
        assert extract_findings([_verdict("opus", "anthropic", [bad])]) == []


def test_failing_check_conclusions_recognised() -> None:
    checks = [
        {"name": "a", "conclusion": "FAILURE"},
        {"name": "b", "conclusion": "TIMED_OUT"},
        {"name": "c", "conclusion": "SUCCESS"},
        {"name": "d", "conclusion": "NEUTRAL"},
    ]
    assert failing_check_names(checks) == ["a", "b"]


def test_duplicate_reports_are_deduplicated() -> None:
    summary = blocking_summary(corroborate(
        [_verdict("opus", "anthropic"), _verdict("ds", "openrouter")]
    ))
    assert summary["verified_count"] == 1


# ============ dispatcher path ============
def _fake_transport(revalidates: bool = True):
    def transport(cfg, state, repo, number):
        return (lambda head: (lambda: revalidates)), (lambda: [])

    return transport


def _run(verdicts, *, authority=None, mutate=None, checks=None, number=200,
         revalidates=True):
    """Drive one job to a terminal state with GitHub fully intercepted."""
    state = State({"state_dir": tempfile.mkdtemp()})
    saved = patch_dispatcher(run_panel=fake_panel(["DEFECTS_FOUND"] * len(verdicts)))
    calls: list = []
    original_execute, original_transport = dispatcher._rc_execute, dispatcher._rc_transport
    dispatcher._rc_execute = mutate or (lambda s, v, j, **k: calls.append(v) or {})
    dispatcher._rc_transport = _fake_transport(revalidates)
    try:
        cfg = _config("live")
        if authority:
            cfg["authority"] = authority
        jid = seed_job(state, number=number, head=f"h{number}")
        seed_evidence(state, jid, checks=checks)
        seed_verdicts(state, jid, verdicts)
        result = dispatcher.run_job(
            cfg, {"job_id": jid, "repo": "o/r", "number": number, "lane": "incoming_review"},
            state=state,
        )
        return result, state.current_status(jid), calls
    finally:
        dispatcher._rc_execute = original_execute
        dispatcher._rc_transport = original_transport
        restore_dispatcher(saved)
        state.close()


def test_default_authority_never_requests_changes() -> None:
    """Fail-closed: corroborated defects still need a human until enabled."""
    result, status, calls = _run(
        [_verdict("opus", "anthropic"), _verdict("ds", "openrouter")], number=201
    )
    assert status == "human_required"
    assert result["request_changes_outcome"] == "authority_not_live"
    assert calls == [], "no mutation may be posted without live authority"


def test_uncorroborated_defect_escalates_without_mutating() -> None:
    result, status, calls = _run([_verdict("opus", "anthropic")],
                                 authority=LIVE_RC, number=202)
    assert status == "human_required"
    assert result["request_changes_outcome"] == "uncorroborated"
    assert calls == []
    assert result["findings"]["unverified_count"] == 1


def test_two_families_with_live_authority_requests_changes() -> None:
    result, status, calls = _run(
        [_verdict("opus", "anthropic"), _verdict("ds", "openrouter")],
        authority=LIVE_RC, number=203,
    )
    assert status == "changes_requested"
    assert result["request_changes_outcome"] == "changes_requested"
    assert len(calls) == 1
    body = calls[0]["body"]
    assert "corroborated blocking finding" in body
    assert "src/a.py:12" in body
    assert "two provider families" in body


def test_check_backed_single_family_requests_changes() -> None:
    result, status, calls = _run(
        [_verdict("opus", "anthropic", [_finding(primary_source="ci-suite")])],
        authority=LIVE_RC, number=204,
        checks=[{"name": "ci-suite", "conclusion": "FAILURE"}],
    )
    assert status == "changes_requested"
    assert len(calls) == 1
    assert "failing check" in calls[0]["body"]


def test_mutation_failure_safe_stops() -> None:
    def boom(state, variables, job, **kwargs):
        raise RuntimeError("graphql 500")

    result, status, _calls = _run(
        [_verdict("opus", "anthropic"), _verdict("ds", "openrouter")],
        authority=LIVE_RC, mutate=boom, number=205,
    )
    assert status == "safe_stop"
    assert result["request_changes_outcome"] == "mutation_failed"


def test_failed_revalidation_denies_and_queues_human() -> None:
    result, status, calls = _run(
        [_verdict("opus", "anthropic"), _verdict("ds", "openrouter")],
        authority=LIVE_RC, number=206, revalidates=False,
    )
    assert status == "human_approval_pending"
    assert result["request_changes_outcome"] == "gate_denied"
    assert calls == [], "a failed revalidation must prevent the mutation"
    assert "final_revalidation" in result["failed_gates"]


def test_mutation_always_carries_verification_inputs() -> None:
    """`execute_request_changes` only verifies when probe+login+head are passed."""
    seen: dict = {}

    def capture(state, variables, job, **kwargs):
        seen.update(kwargs)
        return {}

    _run([_verdict("opus", "anthropic"), _verdict("ds", "openrouter")],
         authority=LIVE_RC, mutate=capture, number=207)
    assert seen.get("rest_probe") is not None
    assert seen.get("login")
    assert seen.get("head_sha") == "h207"


def test_request_changes_body_excludes_uncorroborated_findings() -> None:
    """A verified defect plus an unverified one: only the verified is posted."""
    verified = _finding(location="src/a.py:12")
    unverified = _finding(location="src/z.py:99", title="speculative")
    result, status, calls = _run(
        [_verdict("opus", "anthropic", [verified, unverified]),
         _verdict("ds", "openrouter", [verified])],
        authority=LIVE_RC, number=208,
    )
    assert status == "changes_requested"
    body = calls[0]["body"]
    assert "src/a.py:12" in body
    assert "src/z.py:99" not in body
    assert result["findings"]["verified_count"] == 1
    assert result["findings"]["unverified_count"] == 1
