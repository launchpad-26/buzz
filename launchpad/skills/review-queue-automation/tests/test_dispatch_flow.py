#!/usr/bin/env python3
"""Fake dispatch-flow tests: persisted facts, MISSING_EVIDENCE no-loop, actual
final-state reporting, notification-failure preservation, and safe-stop on
state-persistence / logging failures. No GitHub, no models; every external step
is faked.
"""

from __future__ import annotations

import datetime as dt
import json
import pathlib
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scripts"))

import dispatcher  # noqa: E402
from common import State  # noqa: E402


def _base_config() -> dict:
    return {
        "version": 1,
        "login": "tucktuck101",
        "state_dir": tempfile.mkdtemp(),
        "repository": {"slug": "o/r", "root": "/tmp", "base": "launchpad"},
        "logging": {"directory": tempfile.mkdtemp(), "format": "otel-jsonl"},
        "models": {"primary": [], "secondary": []},
        "assurance": {"large_diff_lines": 700},
        "dispatch": {"incoming_canary_approved": True, "author_canary_approved": True},
        "approval": {
            "mode": "human_escalation", "approval_enabled": False,
            "live_canary_approved": False, "effective_risk_max": 24,
            "complexity_max": 2, "file_limit": 50, "line_limit": 1000,
        },
        "risk": {
            "bands": {"low": 24, "medium": 99, "high": 100},
            "protected_triggers": [r"(^|/)security/", r"(^|/)migrations/"],
        },
        "human_queue": {"expiry_minutes": 1440},
        "github": {"read_only": True, "api_version": "2022-11-28"},
    }


def _config(mode: str = "human_escalation") -> dict:
    cfg = _base_config()
    cfg["approval"] = dict(cfg["approval"])
    cfg["approval"]["mode"] = mode
    if mode == "live":
        cfg["approval"]["approval_enabled"] = True
        cfg["approval"]["live_canary_approved"] = True
    return cfg


def _clean_verdict(model: str, family: str) -> dict:
    return {
        "signal": "SUPPORTED", "recommendation": "clean", "summary": "s",
        "findings": [], "good": ["x"], "missing_evidence": [],
        "model": model, "provider_family": family,
    }


def seed_job(
    state: State,
    *,
    repo: str = "o/r",
    number: int = 1,
    head: str = "abc",
    lane: str = "incoming_review",
    status: str = "detected",
) -> str:
    from common import job_id

    jid = job_id(repo, number, head, lane)
    now = dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")
    state.db.execute(
        "INSERT INTO jobs(id,repo,number,head_sha,lane,status,artifact_dir,created_at,updated_at) "
        "VALUES(?,?,?,?,?,?,?,?,?)",
        (jid, repo, number, head, lane, status, str(state.job_dir(jid)), now, now),
    )
    payload = {
        "user": {"login": "alice"},
        "draft": False,
        "additions": 2,
        "deletions": 0,
        "files": [{"filename": "docs/a.md"}],
        "head": {"sha": head},
        "node_id": f"PR_node_{repo}_{number}",
    }
    state.db.execute(
        "INSERT INTO prs(repo,number,head_sha,updated_at,payload,open,last_seen) VALUES(?,?,?,?,?,1,?)",
        (repo, number, head, now, json.dumps(payload), now),
    )
    state.db.commit()
    return jid


def seed_evidence(state: State, jid: str, *, checks: list[dict] | None = None, collected_at: str | None = None) -> None:
    evidence = {
        "collected_at": collected_at or dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z"),
        "checks": checks if checks is not None else [{"conclusion": "SUCCESS"}],
        "context": {"author": "alice", "draft": False, "head": "abc", "repo_path": "/tmp"},
    }
    state.job_dir(jid)
    (state.job_dir(jid) / "evidence.json").write_text(json.dumps(evidence), encoding="utf-8")


def seed_verdicts(state: State, jid: str, vs: list[dict]) -> None:
    names = ("review-A.txt", "review-B.txt")
    state.job_dir(jid)
    for i, v in enumerate(vs[:2]):
        (state.job_dir(jid) / names[i]).write_text(json.dumps(v), encoding="utf-8")


def fake_panel(signal="SUPPORTED", *, complete: bool = True, calls: list | None = None, required: int = 2):
    """Return a fake run_panel; counts invocations in `calls` when provided."""

    def run(cfg, state, repo, number, lane, job_id, profile, logger=None):
        if calls is not None:
            calls.append((repo, number, lane, job_id))
        signals = signal if isinstance(signal, list) else [signal]
        return {
            "profile": profile,
            "required_reviewers": required,
            "completed_reviewers": ["a", "b"] if complete else ["a"],
            "complete": complete,
            "signals": signals,
            "outcome": "complete" if complete else "degraded",
        }

    return run


def patch_dispatcher(**overrides):
    """Context-manager style install/revert for dispatcher module attributes.
    Always also installs a decide_assurance stub when run_panel is patched, so
    dispatcher's lazy `_ensure_panel` short-circuits without importing the
    (separately-owned) panel module.
    """
    if "run_panel" in overrides and "decide_assurance" not in overrides:
        from assurance import Profile

        def _min(cfg, state, repo, number, lane):
            return Profile("workhorse", "medium", "challenger")

        overrides["decide_assurance"] = _min
    saved = {k: getattr(dispatcher, k) for k in overrides}
    for k, v in overrides.items():
        setattr(dispatcher, k, v)
    return saved


def restore_dispatcher(saved: dict) -> None:
    for k, v in saved.items():
        setattr(dispatcher, k, v)


def patch_approval(fake):
    """Install a fake `approval_action.approve`; returns the previous callable.

    `_execute_live_approval` imports `approve` at call time, so patching the
    module attribute is what actually intercepts the mutation.
    """
    import approval_action

    previous = approval_action.approve
    approval_action.approve = fake
    return previous


def restore_approval(previous) -> None:
    import approval_action

    approval_action.approve = previous


def fake_approve(ok: bool, status: str, message: str = "", *, calls: list | None = None):
    def run(state, **kwargs):
        if calls is not None:
            calls.append(kwargs)
        return ok, status, message

    return run


# --- persisted facts drive the evaluation (never hardcoded) ------------------
def test_live_path_executes_approval_and_completes() -> None:
    """An eligible live decision must actually reach the verified APPROVE, not
    dead-end in `approval_revalidation`."""
    state = State({"state_dir": tempfile.mkdtemp()})
    saved = patch_dispatcher(run_panel=fake_panel("SUPPORTED"))
    calls: list = []
    previous = patch_approval(fake_approve(True, "approved", calls=calls))
    try:
        cfg = _config("live")
        jid = seed_job(state, number=3, head="h3")
        seed_evidence(state, jid)
        seed_verdicts(state, jid, [_clean_verdict("claude-sonnet", "anthropic"),
                                   _clean_verdict("gpt-5.6", "openai")])
        result = dispatcher.run_job(
            cfg, {"job_id": jid, "repo": "o/r", "number": 3, "lane": "incoming_review"},
            state=state,
        )
        final = state.current_status(jid)
        assert result["status"] == final == "completed_auto_approved", result
        assert result["approval_disposition"] == "live"
        assert result["approval_outcome"] == "approved"
        # the eligible decision was persisted and handed to the executor
        assert state.db.execute("SELECT 1 FROM approval_decisions").fetchone() is not None
        assert len(calls) == 1, "approve must be invoked exactly once"
        assert calls[0]["pr_node_id"] == "PR_node_o/r_3"
        assert calls[0]["head_sha"] == "h3"
        assert calls[0]["login"] == "tucktuck101"
    finally:
        restore_approval(previous)
        restore_dispatcher(saved)
        state.close()


def test_live_denial_queues_human_and_does_not_complete() -> None:
    state = State({"state_dir": tempfile.mkdtemp()})
    saved = patch_dispatcher(run_panel=fake_panel("SUPPORTED"))
    previous = patch_approval(fake_approve(False, "denied", "authority not live"))
    try:
        cfg = _config("live")
        jid = seed_job(state, number=4, head="h4")
        seed_evidence(state, jid)
        seed_verdicts(state, jid, [_clean_verdict("claude-sonnet", "anthropic"),
                                   _clean_verdict("gpt-5.6", "openai")])
        result = dispatcher.run_job(
            cfg, {"job_id": jid, "repo": "o/r", "number": 4, "lane": "incoming_review"},
            state=state,
        )
        assert state.current_status(jid) == "human_approval_pending", result
        assert result["approval_outcome"] == "denied"
        row = state.db.execute(
            "SELECT job_id FROM human_requests WHERE state='pending'"
        ).fetchone()
        assert row and row["job_id"] == jid, "denial must leave a durable human request"
    finally:
        restore_approval(previous)
        restore_dispatcher(saved)
        state.close()


def test_live_uncertain_mutation_safe_stops_without_retry() -> None:
    """An unconfirmable mutation must never be retried blind."""
    state = State({"state_dir": tempfile.mkdtemp()})
    saved = patch_dispatcher(run_panel=fake_panel("SUPPORTED"))
    calls: list = []
    previous = patch_approval(
        fake_approve(False, "uncertain", "cannot confirm review landed", calls=calls)
    )
    try:
        cfg = _config("live")
        jid = seed_job(state, number=5, head="h5")
        seed_evidence(state, jid)
        seed_verdicts(state, jid, [_clean_verdict("claude-sonnet", "anthropic"),
                                   _clean_verdict("gpt-5.6", "openai")])
        result = dispatcher.run_job(
            cfg, {"job_id": jid, "repo": "o/r", "number": 5, "lane": "incoming_review"},
            state=state,
        )
        assert state.current_status(jid) == "safe_stop", result
        assert result["approval_outcome"] == "uncertain"
        assert len(calls) == 1, "an uncertain mutation must not be reattempted"
        # no human request: the mutation may already have landed
        assert state.db.execute("SELECT 1 FROM human_requests").fetchone() is None
    finally:
        restore_approval(previous)
        restore_dispatcher(saved)
        state.close()


def test_live_missing_node_id_safe_stops_before_any_mutation() -> None:
    state = State({"state_dir": tempfile.mkdtemp()})
    saved = patch_dispatcher(run_panel=fake_panel("SUPPORTED"))
    calls: list = []
    previous = patch_approval(fake_approve(True, "approved", calls=calls))
    try:
        cfg = _config("live")
        jid = seed_job(state, number=6, head="h6")
        seed_evidence(state, jid)
        seed_verdicts(state, jid, [_clean_verdict("claude-sonnet", "anthropic"),
                                   _clean_verdict("gpt-5.6", "openai")])
        # Drop the cached node_id so the executor cannot identify the PR.
        payload = json.loads(state.db.execute(
            "SELECT payload FROM prs WHERE repo='o/r' AND number=6"
        ).fetchone()["payload"])
        payload.pop("node_id")
        state.db.execute("UPDATE prs SET payload=? WHERE repo='o/r' AND number=6",
                         (json.dumps(payload),))
        state.db.commit()

        result = dispatcher.run_job(
            cfg, {"job_id": jid, "repo": "o/r", "number": 6, "lane": "incoming_review"},
            state=state,
        )
        assert state.current_status(jid) == "safe_stop", result
        assert result["approval_outcome"] == "missing_node_id"
        assert calls == [], "no mutation may be attempted without a PR node id"
    finally:
        restore_approval(previous)
        restore_dispatcher(saved)
        state.close()


def test_draft_and_non_identity_author_drive_human_escalation() -> None:
    state = State({"state_dir": tempfile.mkdtemp()})
    saved = patch_dispatcher(run_panel=fake_panel("SUPPORTED"))
    try:
        cfg = _config("human_escalation")
        jid = seed_job(state, number=9, head="h9")
        seed_evidence(state, jid)
        seed_verdicts(state, jid, [_clean_verdict("claude-sonnet", "anthropic"),
                                   _clean_verdict("gpt-5.6", "openai")])
        result = dispatcher.run_job(cfg, {"job_id": jid, "repo": "o/r", "number": 9, "lane": "incoming_review"}, state=state)
        final = state.current_status(jid)
        assert final == "human_approval_pending", final
        assert result["status"] == final
        assert result["request_id"] and result["policy_hash"]
        row = state.db.execute(
            "SELECT job_id, policy_hash FROM human_requests WHERE repo='o/r' AND number=9 AND state='pending'"
        ).fetchone()
        assert row and row["job_id"] == jid
    finally:
        restore_dispatcher(saved)
        state.close()


# --- MISSING_EVIDENCE: exactly one bounded gather, never an identical re-run --
def test_missing_evidence_does_one_gather_no_rerun() -> None:
    state = State({"state_dir": tempfile.mkdtemp()})
    calls: list = []
    gather_calls: list = []
    saved = patch_dispatcher(run_panel=fake_panel("MISSING_EVIDENCE", calls=calls))

    def fake_gather(cfg, state, repo, number, lane, job_id):
        gather_calls.append(job_id)

    saved["collect_evidence"] = dispatcher.collect_evidence
    dispatcher.collect_evidence = fake_gather
    try:
        cfg = _config("human_escalation")
        jid = seed_job(state, number=7, head="h7")
        result = dispatcher.run_job(cfg, {"job_id": jid, "repo": "o/r", "number": 7, "lane": "incoming_review"}, state=state)
        assert len(gather_calls) == 1, gather_calls
        assert len(calls) == 1, calls
        assert result["status"] == "degraded_draft", result
        assert result["decision"] == "EVIDENCE_INCOMPLETE"
        assert state.current_status(jid) == "degraded_draft"
    finally:
        dispatcher.collect_evidence = saved["collect_evidence"]
        restore_dispatcher(saved)
        state.close()


def test_missing_evidence_no_gather_escalates() -> None:
    state = State({"state_dir": tempfile.mkdtemp()})
    calls: list = []
    saved = patch_dispatcher(run_panel=fake_panel("MISSING_EVIDENCE", calls=calls))

    def boom_gather(cfg, state, repo, number, lane, job_id):
        raise RuntimeError("no deterministic gather available")

    saved["collect_evidence"] = dispatcher.collect_evidence
    dispatcher.collect_evidence = boom_gather
    try:
        cfg = _config()
        jid = seed_job(state, number=8, head="h8")
        result = dispatcher.run_job(cfg, {"job_id": jid, "repo": "o/r", "number": 8, "lane": "incoming_review"}, state=state)
        assert result["status"] == "human_required", result
        assert len(calls) == 1, calls
        assert state.current_status(jid) == "human_required"
    finally:
        dispatcher.collect_evidence = saved["collect_evidence"]
        restore_dispatcher(saved)
        state.close()


# --- safe-stop on state persistence failure -----------------------------------
def test_persistence_failure_safe_stops_job() -> None:
    state = State({"state_dir": tempfile.mkdtemp()})
    orig_transition = State.transition
    saved = patch_dispatcher(run_panel=fake_panel("SUPPORTED"))
    try:
        def boom_transition(self, job_id, target, **kw):
            raise RuntimeError("disk full on state write")

        State.transition = boom_transition
        cfg = _config()
        jid = seed_job(state, number=11, head="h11")
        result = dispatcher.run_job(cfg, {"job_id": jid, "repo": "o/r", "number": 11, "lane": "incoming_review"}, state=state)
        assert result["status"] == "safe_stop", result
        assert "state" in result["reason"] or "persistence" in result["reason"], result["reason"]
    finally:
        State.transition = orig_transition
        restore_dispatcher(saved)
        state.close()


def test_logging_failure_safe_stops_job() -> None:
    from logging_otel import JobLogger

    state = State({"state_dir": tempfile.mkdtemp()})
    saved = patch_dispatcher(run_panel=fake_panel("SUPPORTED"))

    class BoomLogger(JobLogger):
        def info(self, **kw):
            raise RuntimeError("audit log write failed")

    orig_make_logger = dispatcher._make_logger
    dispatcher._make_logger = lambda cfg, jid, repo, number, lane: BoomLogger(
        tempfile.mkdtemp(), jid, repo=repo, number=number, lane=lane
    )
    try:
        cfg = _config("live")
        jid = seed_job(state, number=13, head="h13")
        seed_evidence(state, jid)
        seed_verdicts(state, jid, [_clean_verdict("claude-sonnet", "anthropic"),
                                   _clean_verdict("gpt-5.6", "openai")])
        result = dispatcher.run_job(cfg, {"job_id": jid, "repo": "o/r", "number": 13, "lane": "incoming_review"}, state=state)
        assert result["status"] == "safe_stop", result
        assert "logging" in result["reason"] or "audit" in result["reason"], result["reason"]
    finally:
        dispatcher._make_logger = orig_make_logger
        restore_dispatcher(saved)
        state.close()


# --- notification failure preserves the queued request ------------------------
def test_notification_failure_preserves_request() -> None:
    state = State({"state_dir": tempfile.mkdtemp()})
    saved = patch_dispatcher(run_panel=fake_panel("SUPPORTED"))
    saved_notify = dispatcher.notify_human
    dispatcher.notify_human = lambda cfg, req: (_ for _ in ()).throw(RuntimeError("slack down"))
    try:
        cfg = _config()
        jid = seed_job(state, number=17, head="h17")
        seed_evidence(state, jid)
        seed_verdicts(state, jid, [_clean_verdict("claude-sonnet", "anthropic"),
                                   _clean_verdict("gpt-5.6", "openai")])
        result = dispatcher.run_job(cfg, {"job_id": jid, "repo": "o/r", "number": 17, "lane": "incoming_review"}, state=state)
        assert result["status"] == "human_approval_pending", result
        assert result["notification"].startswith("notification failure")
        row = state.db.execute(
            "SELECT * FROM human_requests WHERE repo='o/r' AND number=17 AND state='pending'"
        ).fetchone()
        assert row is not None
    finally:
        dispatcher.notify_human = saved_notify
        restore_dispatcher(saved)
        state.close()


if __name__ == "__main__":
    failures = 0
    passed = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                passed += 1
            except Exception as exc:
                failures += 1
                import traceback
                print(f"FAIL {name}: {exc}")
                traceback.print_exc()
    print(f"{passed} passed, {failures} failed")
    sys.exit(1 if failures else 0)