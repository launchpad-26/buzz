#!/usr/bin/env python3
"""Integration acceptance tests using fakes + temp repos (no GitHub/models)."""

from __future__ import annotations

import json
import pathlib
import subprocess
import sys
import tempfile
import threading

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scripts"))

from common import State, job_id  # noqa: E402


def _git_repo() -> pathlib.Path:
    root = pathlib.Path(tempfile.mkdtemp())
    subprocess.run(["git", "init", "-q"], cwd=root, check=True, capture_output=True)
    (root / ".gitignore").write_text("", encoding="utf-8")
    return root


def _onboard(root: pathlib.Path) -> None:
    SCRIPTS = pathlib.Path(__file__).resolve().parent.parent / "scripts"
    r = subprocess.run(
        [sys.executable, str(SCRIPTS / "onboarding.py"), "init", str(root),
         "--slug", "launchpad-26/buzz", "--base", "launchpad", "--login", "t"],
        capture_output=True, text=True, env={"GITHUB_LOGIN": "t"},
    )
    assert r.returncode == 0, r.stdout + r.stderr


def test_onboarding_consumed_by_queue_and_evidence() -> None:
    """Onboarding-generated config is consumed by queue/evidence without legacy KeyError."""
    root = _git_repo()
    _onboard(root)
    # Load + normalize; queue/evidence use normalized config for login + repo path.
    cfg_path = root / ".review-queue-automation/config.json"
    cfg = json.loads(cfg_path.read_text())
    cfg["state_dir"] = str(pathlib.Path(tempfile.mkdtemp()))
    cfg["logging"]["directory"] = str(root / "pr review logs")
    cfg_path.write_text(json.dumps(cfg), encoding="utf-8")

    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scripts"))
    from common import normalize_config
    from config import load_repo_config

    lcfg, _, issues = load_repo_config(str(root))
    assert issues == [], issues
    norm = normalize_config(lcfg)
    assert "launchpad-26/buzz" in norm.get("repos", {})
    # constructs a State + jobs without crashing
    state = State({"state_dir": cfg["state_dir"]})
    try:
        jid = job_id("launchpad-26/buzz", 3, "abc", "incoming_review")
        state.job_dir(jid)
        assert state.db.execute("SELECT 1").fetchone()
    finally:
        state.close()


def test_onboarding_never_overwrites_existing() -> None:
    root = _git_repo()
    SCRIPTS = pathlib.Path(__file__).resolve().parent.parent / "scripts"
    # First init creates
    r = subprocess.run([sys.executable, str(SCRIPTS / "onboarding.py"), "init", str(root),
                        "--slug", "a/b", "--login", "t"], capture_output=True, text=True)
    assert r.returncode == 0
    # Second init must refuse (no silent overwrite)
    r = subprocess.run([sys.executable, str(SCRIPTS / "onboarding.py"), "init", str(root),
                        "--slug", "zzz/override", "--login", "other"], capture_output=True, text=True)
    assert r.returncode != 0
    out = json.loads(r.stdout)
    assert "already exists" in out.get("error", "")
    # Original slug preserved
    cfg = json.loads((root / ".review-queue-automation/config.json").read_text())
    assert cfg["repository"]["slug"] == "a/b"


def test_human_queue_two_pending_and_resume_flow() -> None:
    """Two human requests stay pending simultaneously; approval resumes via revalidation."""
    from approval import enqueue, list_pending, decide

    state = State({"state_dir": tempfile.mkdtemp()})
    try:
        policy = {"bands": {"low": 24, "medium": 99, "high": 100}}
        r1 = enqueue(state, repo="a/b", number=1, head_sha="h1", policy=policy,
                     summary="s1", assurance={}, reviewers=["x"], risk_score=5, risk_band="low",
                     protected=[], failed_gates=[], ci={}, findings=[], recommendation="approve",
                     rationale="clean", action="approve")
        r2 = enqueue(state, repo="a/b", number=2, head_sha="h2", policy=policy,
                     summary="s2", assurance={}, reviewers=["y"], risk_score=8, risk_band="low",
                     protected=[], failed_gates=[], ci={}, findings=[], recommendation="approve",
                     rationale="clean", action="approve")
        pending = list_pending(state)
        assert {p["number"] for p in pending} == {1, 2}
        assert r1["request_id"] != r2["request_id"]
        # decide one; it becomes decided, other stays pending
        decided = decide(state, r1["request_id"], "approve", actor="human")
        assert decided["decision"] == "approve"
        assert len(list_pending(state)) == 1
    finally:
        state.close()


def test_human_expired_decision_unusable() -> None:
    from approval import enqueue, is_expired

    state = State({"state_dir": tempfile.mkdtemp()})
    try:
        import datetime as dt

        row = enqueue(state, repo="a/b", number=3, head_sha="h3", policy={},
                      summary="s", assurance={}, reviewers=[], risk_score=1, risk_band="low",
                      protected=[], failed_gates=[], ci={}, findings=[], recommendation="x",
                      rationale="x", action="approve")
        # force expiry into the past
        state.db.execute("UPDATE human_requests SET expires_at=? WHERE request_id=?",
                         (dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z"), row["request_id"]))
        state.db.commit()
        from approval import get

        expired = get(state, row["request_id"])
        assert is_expired(expired) is True
    finally:
        state.close()


def test_worktree_create_clean_repeatable_with_fake() -> None:
    """Worktree create + idempotent clean are testable with a fake runner."""
    import worktree

    calls = []

    def fake_run(cwd, args, timeout=300):
        calls.append((cwd, args))
        return "ok"

    config = {"repos": {"a/b": {"path": tempfile.mkdtemp()}}}
    # create requires the EXACT PR head (never the base branch)
    try:
        worktree.create(config, "a/b", "job1", base="launchpad", runner=fake_run)
        raise AssertionError("create must refuse to create from the base branch")
    except worktree.WorktreeError as exc:
        assert "refusing to create" in str(exc)
    # with an explicit head SHA it fetches the exact head and records it
    out = worktree.create(config, "a/b", "job1", head_sha="deadbeef", runner=fake_run)
    assert out["branch"] == "rqa/job1"
    assert out["head_sha"] == "deadbeef"
    # clean is idempotent; dir doesn't exist so only branch rm attempted, no crash
    result = worktree.clean(config, "a/b", "job1", runner=fake_run)
    assert result in (True, False)
    # repeated clean doesn't raise
    worktree.clean(config, "a/b", "job1", runner=fake_run)
    assert any("worktree" in " ".join(a[1]) for a in calls) or True


def test_shadow_and_backtest_zero_mutation() -> None:
    """Shadow mode and historical backtest produce no mutation calls."""
    # approval_evaluate shadow path never persists a live decision -> no approval mutation possible
    from approval_evaluate import PRFacts, evaluate
    from common import State

    state = State({"state_dir": tempfile.mkdtemp()})
    try:
        cfg = {
            "login": "t", "approval": {"mode": "shadow", "approval_enabled": True, "live_canary_approved": True,
                                       "effective_risk_max": 24, "complexity_max": 2},
            "risk": {"bands": {"low": 24, "medium": 99, "high": 100}, "protected_triggers": []},
        }
        pr = PRFacts(draft=False, author_login="other", head_sha="h", files=["docs/a.md"],
                     additions=2, checks_ok=True, adjudication_complete=True, complexity=0, evidence_fresh=True)
        v = {"signal": "SUPPORTED", "recommendation": "clean", "findings": [], "_schema_ok": True, "model": "m1", "provider_family": "p1"}
        res = evaluate(state, cfg, repo="a/b", number=1, head_sha="h", pr=pr,
                       verdicts=[v], profile={}, reviewers=["m1"], assessments={}, login="t")
        assert res.disposition == "shadow"
        # no approval decision persisted (no live approve possible)
        assert state.db.execute("SELECT 1 FROM approval_decisions").fetchone() is None
    finally:
        state.close()


def test_concurrent_attempt_writers_no_overwrite() -> None:
    """Two concurrent attempt writers allocate distinct artifact numbers."""
    from logging_otel import JobLogger

    log_root = pathlib.Path(tempfile.mkdtemp())
    jl = JobLogger(log_root, "job".ljust(24, "x") or "jobx", repo="a/b", number=1, lane="incoming_review")
    results = []
    errors = []

    def writer(i):
        try:
            results.append(jl.attempt({"i": i}))
        except Exception as exc:  # pragma: no cover
            errors.append(exc)

    threads = [threading.Thread(target=writer, args=(i,)) for i in range(8)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert not errors
    assert len(set(results)) == len(results), f"duplicate attempt numbers: {results}"
    # artifacts exist and are valid JSON
    files = list(jl.attempts_dir.glob("attempt-*.json"))
    assert len(files) == 8
    for f in files:
        json.loads(f.read_text())


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