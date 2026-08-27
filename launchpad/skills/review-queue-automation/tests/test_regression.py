#!/usr/bin/env python3
"""Regression tests for the five panel/dispatcher defects:

P0 partial panel must not be complete (never SUCCESS)
P1 fallback candidates inside a slot must be attempted
P1 sensitive/large PRs keep their fact-aware minimum profile
P1 escalated attempts must not consume stale verdict files
P1 partial panels become degraded drafts, never a human hold
"""

from __future__ import annotations

import json
import pathlib
import sys
import tempfile
from contextlib import contextmanager

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scripts"))

import panel  # noqa: E402
from assurance import Profile  # noqa: E402
from common import State, atomic_write, job_id  # noqa: E402

REPO = "launchpad-26/buzz"


def cfg() -> dict:
    return {
        "login": "tucktuck101",
        "state_dir": tempfile.mkdtemp(),
        "repos": {REPO: {"path": "/tmp/none"}},
        "assurance": {"large_diff_lines": 700},
        "models": {
            "cooldown_seconds": 5,
            "timeout_seconds": 30,
            "primary": [
                {"runner": "x", "selector": "claude", "provider_family": "anthropic", "capability": "frontier"},
                {"runner": "x", "selector": "glm", "provider_family": "zai", "capability": "frontier"},
            ],
            "secondary": [
                {"runner": "x", "selector": "gpt", "provider_family": "openai", "capability": "frontier"},
                {"runner": "x", "selector": "deepseek", "provider_family": "deepseek", "capability": "workhorse"},
            ],
        },
    }


def _make_fake(fail: set[str], signals: dict[str, str]):
    def fake(entry, prompt, out_path, effort, repo_path, timeout):
        if entry["selector"] in fail:
            raise RuntimeError(f"no model {entry['selector']}")
        out_path.write_text(json.dumps({"signal": signals.get(entry["selector"], "SUPPORTED"), "recommendation": "clean", "summary": "test", "findings": [], "good": [], "missing_evidence": []}))

    return fake


_ORIGINAL = panel._run_reviewer


@contextmanager
def _reviewers(fail: set[str] | None = None, signals: dict[str, str] | None = None):
    panel._run_reviewer = _make_fake(fail or set(), signals or {})
    try:
        yield
    finally:
        panel._run_reviewer = _ORIGINAL


def _seed(state: State, number: int, lane: str = "incoming_review") -> str:
    jid = job_id(REPO, number, "abc123", lane)
    state.job_dir(jid)
    state.db.execute(
        "INSERT OR REPLACE INTO jobs(id,repo,number,head_sha,lane,status,artifact_dir,created_at,updated_at) "
        "VALUES(?,?,?,?,?,?,?,?,?)",
        (jid, REPO, number, "abc123", lane, "detected", str(state.job_dir(jid)), "2026-08-27T00:00:00Z", "2026-08-27T00:00:00Z"),
    )
    state.db.commit()
    atomic_write(state.job_dir(jid) / "evidence.txt", "evidence")
    return jid


def _seed_pr_row(state: State, files: list[str], additions: int, deletions: int) -> None:
    payload = {"files": [{"filename": f} for f in files], "additions": additions, "deletions": deletions}
    state.db.execute(
        "INSERT OR REPLACE INTO prs(repo,number,head_sha,updated_at,payload,open,last_seen) "
        "VALUES(?,?,?,?,?,1,?)",
        (REPO, 5, "abc123", "2026-08-27T00:00:00Z", json.dumps(payload), "2026-08-27T00:00:00Z"),
    )
    state.db.commit()


def test_partial_panel_not_complete() -> None:
    state = State(cfg())
    try:
        jid = _seed(state, 1)
        with _reviewers(fail={"claude", "glm"}, signals={"gpt": "SUPPORTED"}):
            result = panel.run_panel(cfg(), state, REPO, 1, "incoming_review", jid, Profile(independence="challenger"))
        assert result["complete"] is False
        assert result["completed_reviewers"] == ["gpt"]
    finally:
        state.close()


def test_fallback_within_slot_attempted() -> None:
    state = State(cfg())
    try:
        jid = _seed(state, 2)
        with _reviewers(fail={"claude"}, signals={"glm": "SUPPORTED"}):
            result = panel.run_panel(cfg(), state, REPO, 2, "incoming_review", jid, Profile(independence="single"))
        assert result["complete"] is True
        assert result["completed_reviewers"] == ["glm"]
        assert result["selected_candidates"] == ["x:glm"]
    finally:
        state.close()


def test_stale_verdict_not_consumed() -> None:
    state = State(cfg())
    try:
        jid = _seed(state, 3)
        atomic_write(state.job_dir(jid) / "review-A.txt", json.dumps({"signal": "SUPPORTED", "recommendation": "clean", "summary": "test", "findings": [], "good": [], "missing_evidence": []}))
        with _reviewers(fail={"claude", "glm", "gpt", "deepseek"}):
            result = panel.run_panel(cfg(), state, REPO, 1, "incoming_review", jid, Profile(independence="challenger"))
        assert result["complete"] is False
        assert result["signals"] == []
        assert not (state.job_dir(jid) / "review-A.txt").exists()
    finally:
        state.close()


def test_sensitive_keeps_frontier() -> None:
    state = State(cfg())
    try:
        _seed_pr_row(state, ["security/x"], 10, 10)
        prof = panel.decide_assurance(cfg(), state, REPO, 5, "incoming_review")
        assert prof.capability == "frontier"
        assert prof.effort == "high"
        assert prof.independence == "challenger"
    finally:
        state.close()


def test_large_diffs_keep_frontier() -> None:
    state = State(cfg())
    try:
        _seed_pr_row(state, ["docs/x"], 800, 0)
        prof = panel.decide_assurance(cfg(), state, REPO, 5, "incoming_review")
        assert prof.capability == "frontier"
    finally:
        state.close()


def test_plain_is_workhorse() -> None:
    state = State(cfg())
    try:
        _seed_pr_row(state, ["docs/x"], 10, 10)
        prof = panel.decide_assurance(cfg(), state, REPO, 5, "incoming_review")
        assert prof.capability == "workhorse"
        assert prof.effort == "medium"
    finally:
        state.close()


def test_partial_panel_is_degraded_draft_not_held() -> None:
    import dispatcher

    state = State(cfg())
    try:
        jid = _seed(state, 9)
        state.db.execute(
            "INSERT INTO canaries(lane,status,updated_at) VALUES('incoming_review','approved',?) "
            "ON CONFLICT(lane) DO UPDATE SET status='approved'",
            ("2026-08-27T00:00:00Z",),
        )
        state.db.commit()
        with _reviewers(fail={"claude", "glm"}, signals={"gpt": "SUPPORTED"}):
            result = dispatcher.run_job(
                cfg(),
                {"job_id": jid, "repo": REPO, "number": 9, "lane": "incoming_review"},
                state=state,
                claim_lease=False,  # offline test: no GitHub assignee mutation
            )
        assert result["status"] == "degraded_draft"
        assert result["decision"] == "PARTIAL_PANEL"
        assert result["completed_reviewers"] == ["gpt"]
        assert result["required_reviewers"] == 2
        row = state.db.execute("SELECT status FROM jobs WHERE id=?", (jid,)).fetchone()
        assert row["status"] == "degraded_draft"
    finally:
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
                print(f"FAIL {name}: {exc}")
    print(f"{passed} passed, {failures} failed")
    sys.exit(1 if failures else 0)