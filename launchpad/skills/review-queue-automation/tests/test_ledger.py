#!/usr/bin/env python3
"""Tests for ledger.py — the durable evidence and findings ledger.

Its purpose is to answer "why did this PR get this outcome?" without re-reading
raw model output. So the tests assert: entries are bound to an exact PR revision,
nothing carries between revisions, payloads are redacted, the ledger can never
break a decision, and a real dispatch is reconstructable end to end.
"""

from __future__ import annotations

import pathlib
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scripts"))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import dispatcher  # noqa: E402
from common import State  # noqa: E402
from ledger import (  # noqa: E402
    KINDS,
    LedgerError,
    entries,
    explain,
    record,
    render_explanation,
    revisions,
)
from test_dispatch_flow import (  # noqa: E402
    _clean_verdict,
    _config,
    fake_approve,
    fake_panel,
    patch_approval,
    patch_dispatcher,
    restore_approval,
    restore_dispatcher,
    seed_evidence,
    seed_job,
    seed_verdicts,
)


def _state() -> State:
    return State({"state_dir": tempfile.mkdtemp()})


def _record(state, **over):
    kwargs = {
        "job_id": "job1", "repo": "o/r", "number": 1, "head_sha": "h1",
        "kind": "decision", "payload": {"disposition": "live"},
    }
    kwargs.update(over)
    return record(state, **kwargs)


# -- identity ------------------------------------------------------------
def test_entry_is_bound_to_an_exact_revision() -> None:
    state = _state()
    try:
        _record(state)
        [item] = entries(state, "job1")
        assert item["repo"] == "o/r"
        assert item["number"] == 1
        assert item["head_sha"] == "h1"
        assert item["recorded_at"].endswith("Z")
    finally:
        state.close()


def test_unattributable_entries_are_refused() -> None:
    """An entry that cannot be tied to a revision would explain the wrong thing."""
    state = _state()
    try:
        for missing in ("job_id", "repo", "head_sha"):
            try:
                _record(state, **{missing: ""})
            except LedgerError as exc:
                assert "require" in str(exc)
                continue
            raise AssertionError(f"an entry without {missing} must be refused")
    finally:
        state.close()


def test_unknown_kind_is_refused() -> None:
    state = _state()
    try:
        try:
            _record(state, kind="vibes")
        except LedgerError as exc:
            assert "unknown ledger kind" in str(exc)
        else:
            raise AssertionError("an unknown kind must be refused")
    finally:
        state.close()


def test_every_declared_kind_is_recordable() -> None:
    state = _state()
    try:
        for kind in KINDS:
            _record(state, kind=kind)
        assert len(entries(state, "job1")) == len(KINDS)
    finally:
        state.close()


# -- append-only ---------------------------------------------------------
def test_entries_are_append_only_and_ordered() -> None:
    state = _state()
    try:
        _record(state, payload={"disposition": "first"})
        _record(state, payload={"disposition": "second"})
        items = entries(state, "job1")
        assert [i["payload"]["disposition"] for i in items] == ["first", "second"]
        assert items[0]["id"] < items[1]["id"]
    finally:
        state.close()


def test_kind_filter() -> None:
    state = _state()
    try:
        _record(state, kind="finding", payload={"severity": "blocker"})
        _record(state, kind="decision", payload={"disposition": "live"})
        assert len(entries(state, "job1", kind="finding")) == 1
        assert len(entries(state, "job1", kind="decision")) == 1
    finally:
        state.close()


# -- nothing carries between revisions ----------------------------------
def test_revisions_are_separate() -> None:
    state = _state()
    try:
        _record(state, job_id="jobA", head_sha="h1", payload={"disposition": "live"})
        _record(state, job_id="jobB", head_sha="h2", payload={"disposition": "human"})

        assert len(entries(state, "jobA")) == 1
        assert len(entries(state, "jobB")) == 1

        history = revisions(state, "o/r", 1)
        assert [r["head_sha"] for r in history] == ["h1", "h2"]
        assert all(r["entry_count"] == 1 for r in history)
    finally:
        state.close()


def test_explain_only_sees_its_own_job() -> None:
    state = _state()
    try:
        _record(state, job_id="jobA", head_sha="h1", payload={"disposition": "live"})
        _record(state, job_id="jobB", head_sha="h2", payload={"disposition": "human"})
        report = explain(state, "jobA")
        assert report["head_sha"] == "h1"
        assert report["final_decision"]["disposition"] == "live"
    finally:
        state.close()


# -- redaction -----------------------------------------------------------
def test_payloads_are_redacted() -> None:
    state = _state()
    try:
        _record(state, kind="evidence", payload={
            "api_key": "sk-secret-value",
            "note": "fine",
        })
        payload = entries(state, "job1")[0]["payload"]
        assert "sk-secret-value" not in str(payload)
        assert payload["note"] == "fine"
    finally:
        state.close()


def test_enveloped_evidence_is_not_stored() -> None:
    state = _state()
    try:
        _record(state, kind="evidence", payload={
            "bundle": "<<<pr_meta:nonce1>>> secret body END:pr_meta",
        })
        assert "secret body" not in str(entries(state, "job1")[0]["payload"])
    finally:
        state.close()


# -- explanation ---------------------------------------------------------
def test_explain_reports_nothing_recorded_honestly() -> None:
    state = _state()
    try:
        report = explain(state, "absent")
        assert report["explained"] is False
        assert "no ledger entries" in report["reason"]
        assert "no ledger entries" in render_explanation(report)
    finally:
        state.close()


def test_explain_separates_verified_findings() -> None:
    state = _state()
    try:
        _record(state, kind="finding", payload={"severity": "blocker", "verified": True,
                                                 "location": "a.py:1", "basis": "two_provider_families"})
        _record(state, kind="finding", payload={"severity": "blocker", "verified": False,
                                                 "location": "z.py:9", "basis": "single_family_uncorroborated"})
        report = explain(state, "job1")
        assert len(report["findings"]) == 2
        assert len(report["verified_findings"]) == 1
        assert report["verified_findings"][0]["location"] == "a.py:1"

        text = render_explanation(report)
        assert "1 verified, 1 unverified" in text
        assert "a.py:1" in text
        assert "z.py:9" not in text, "only corroborated findings are listed"
    finally:
        state.close()


def test_render_flags_unenforced_effort() -> None:
    """A route that could not apply the requested effort must be visible."""
    state = _state()
    try:
        _record(state, kind="route", payload={
            "runner": "claude", "selector": "opus", "effort": "xhigh",
            "effort_enforced": False,
        })
        assert "effort NOT enforced" in render_explanation(explain(state, "job1"))
    finally:
        state.close()


# -- the ledger must never break a decision -----------------------------
def test_dispatcher_recorder_swallows_ledger_failure() -> None:
    """A ledger problem must not change an outcome."""
    state = _state()
    try:
        # An unknown kind would raise inside `record`; the wrapper must absorb it.
        dispatcher._ledger_record(
            state, {"job_id": "j", "repo": "o/r", "number": 1}, "h1",
            "not-a-kind", {"x": 1},
        )
    finally:
        state.close()


# -- end-to-end reconstruction ------------------------------------------
def test_auto_approved_dispatch_is_reconstructable() -> None:
    state_dir = tempfile.mkdtemp()
    state = State({"state_dir": state_dir})
    saved = patch_dispatcher(run_panel=fake_panel("SUPPORTED"))
    previous = patch_approval(fake_approve(True, "approved"))
    try:
        cfg = _config("live")
        cfg["state_dir"] = state_dir
        jid = seed_job(state, number=500, head="h500")
        seed_evidence(state, jid)
        seed_verdicts(state, jid, [_clean_verdict("claude-opus-5", "anthropic"),
                                   _clean_verdict("deepseek-v4-flash", "openrouter")])
        dispatcher.run_job(
            cfg, {"job_id": jid, "repo": "o/r", "number": 500, "lane": "incoming_review"},
            state=state,
        )
        report = explain(state, jid)
        assert report["explained"] is True
        assert report["final_decision"]["disposition"] == "live"
        assert report["final_action"]["operation"] == "approve_review"
        assert report["final_action"]["verified"] is True

        text = render_explanation(report)
        assert "approve_review" in text
        assert "o/r#500" in text
    finally:
        restore_approval(previous)
        restore_dispatcher(saved)
        state.close()


def test_uncorroborated_defect_records_its_conclusion() -> None:
    """Every terminal outcome must land a decision entry, not just the happy path."""
    state_dir = tempfile.mkdtemp()
    state = State({"state_dir": state_dir})
    saved = patch_dispatcher(run_panel=fake_panel(["DEFECTS_FOUND"]))
    try:
        cfg = _config("live")
        cfg["state_dir"] = state_dir
        cfg["authority"] = {"request_changes": "live"}
        jid = seed_job(state, number=501, head="h501")
        seed_evidence(state, jid)
        seed_verdicts(state, jid, [{
            "signal": "DEFECTS_FOUND", "recommendation": "findings", "summary": "defect",
            "findings": [{"severity": "blocker", "title": "auth bypass",
                          "location": "src/a.py:12", "evidence": "expired sessions",
                          "primary_source": "src/a.py"}],
            "good": [], "missing_evidence": [],
            "model": "claude-opus-5", "provider_family": "anthropic",
        }])
        dispatcher.run_job(
            cfg, {"job_id": jid, "repo": "o/r", "number": 501, "lane": "incoming_review"},
            state=state,
        )
        report = explain(state, jid)
        assert report["final_decision"]["disposition"] == "uncorroborated"
        assert len(report["verified_findings"]) == 0
        assert len(report["findings"]) == 1
    finally:
        restore_dispatcher(saved)
        state.close()
