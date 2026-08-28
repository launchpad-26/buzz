#!/usr/bin/env python3
"""Managed-harness runtime ownership tests.

A state directory permits one dispatcher command at once. Batch order is stable
FIFO; an interrupted worker is recovered by releasing its recorded review lease
and safe-stopping the incomplete job rather than replaying unknown model work.
"""

from __future__ import annotations

import contextlib
import io
import json
import pathlib
import subprocess
import sys
import tempfile
SCRIPTS = pathlib.Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import dispatcher  # noqa: E402
from common import State  # noqa: E402
from test_dispatch_flow import _config, seed_job  # noqa: E402


def _state() -> tuple[State, dict]:
    cfg = _config()
    cfg["state_dir"] = tempfile.mkdtemp()
    return State(cfg), cfg


def test_runtime_lock_is_exclusive_across_processes_and_crash_recoverable() -> None:
    state, cfg = _state()
    lock = state.try_runtime_lock("sweep")
    assert lock is not None
    script = (
        "import sys; sys.path.insert(0, sys.argv[2]); "
        "from common import State; s=State({'state_dir':sys.argv[1]}); "
        "x=s.try_runtime_lock('sweep'); print('locked' if x else 'busy'); "
        "x and x.release(); s.close()"
    )
    try:
        busy = subprocess.run(
            [sys.executable, "-c", script, cfg["state_dir"], str(SCRIPTS)],
            check=True, text=True, capture_output=True,
        )
        assert busy.stdout.strip() == "busy"
    finally:
        lock.release()
        state.close()

    recovered = subprocess.run(
        [sys.executable, "-c", script, cfg["state_dir"], str(SCRIPTS)],
        check=True, text=True, capture_output=True,
    )
    assert recovered.stdout.strip() == "locked", "kernel releases flock when owner exits"


def test_sweep_refuses_when_another_command_owns_state_dir() -> None:
    state, cfg = _state()
    lock = state.try_runtime_lock("sweep")
    assert lock is not None
    original_load = dispatcher.load_repo_config
    original_run = dispatcher.run_job
    original_reconcile = dispatcher._reconcile_queue
    dispatcher.load_repo_config = lambda _root: (cfg, pathlib.Path("config.json"), [])
    dispatcher.run_job = lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError("must not run"))
    dispatcher._reconcile_queue = lambda *_args: {"transitions": []}
    try:
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            assert dispatcher.main(["--repo-root", ".", "--no-capability-probe", "sweep"]) == 0
        assert '"status": "sweep_already_running"' in output.getvalue()
    finally:
        dispatcher.load_repo_config = original_load
        dispatcher.run_job = original_run
        dispatcher._reconcile_queue = original_reconcile
        lock.release()
        state.close()


def test_sweep_selects_stable_fifo_order() -> None:
    state, cfg = _state()
    first = seed_job(state, number=2, head="h2")
    second = seed_job(state, number=1, head="h1")
    # Equal timestamps demand an unambiguous tie-breaker. IDs sort by PR number.
    state.db.execute("UPDATE jobs SET created_at='2026-01-01T00:00:00Z'")
    state.db.commit()
    seen: list[str] = []
    original_load = dispatcher.load_repo_config
    original_run = dispatcher.run_job
    original_reconcile = dispatcher._reconcile_queue
    dispatcher.load_repo_config = lambda _root: (cfg, pathlib.Path("config.json"), [])
    dispatcher.run_job = lambda _cfg, job, **_kwargs: seen.append(job["job_id"]) or {"job": job["job_id"], "status": "gated"}
    dispatcher._reconcile_queue = lambda *_args: seen.append("queue") or {"transitions": []}
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            assert dispatcher.main(["--repo-root", ".", "--no-capability-probe", "sweep", "--limit", "2"]) == 0
        assert seen == ["queue", second, first]
    finally:
        dispatcher.load_repo_config = original_load
        dispatcher.run_job = original_run
        dispatcher._reconcile_queue = original_reconcile
        state.close()


def test_status_is_local_and_reports_job_and_lease_counts() -> None:
    state, cfg = _state()
    jid = seed_job(state, number=40, head="h40")
    state.db.execute(
        "INSERT INTO leases(repo,number,job_id,claimed_at) VALUES(?,?,?,?)",
        ("o/r", 40, jid, "2026-01-01T00:00:00Z"),
    )
    state.db.commit()
    original_load = dispatcher.load_repo_config
    dispatcher.load_repo_config = lambda _root: (cfg, pathlib.Path("config.json"), [])
    try:
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            assert dispatcher.main(["--repo-root", ".", "status"]) == 0
        payload = json.loads(output.getvalue())
        assert payload["jobs"] == {"detected": 1}
        assert payload["leases"] == 1
        assert payload["worker_concurrency"] == 1
    finally:
        dispatcher.load_repo_config = original_load
        state.close()


def test_recover_releases_only_recorded_lease_and_safe_stops_incomplete_job() -> None:
    state, cfg = _state()
    jid = seed_job(state, number=31, head="h31")
    state.transition(jid, "evidence")
    state.db.execute(
        "INSERT INTO leases(repo,number,job_id,claimed_at) VALUES(?,?,?,?)",
        ("o/r", 31, jid, "2026-01-01T00:00:00Z"),
    )
    state.db.commit()
    released: list[tuple[str, int, str]] = []
    original_release = dispatcher._lease_release

    def fake_release(_cfg, local_state, repo, number, job, _login):
        released.append((repo, number, job))
        local_state.db.execute("DELETE FROM leases WHERE repo=? AND number=?", (repo, number))
        local_state.db.commit()

    dispatcher._lease_release = fake_release
    try:
        result = dispatcher.recover_interrupted(cfg, state)
        assert result == [{"job": jid, "repo": "o/r", "number": 31, "released": True, "status": "safe_stop"}]
        assert released == [("o/r", 31, jid)]
        assert state.current_status(jid) == "safe_stop"
        assert state.db.execute("SELECT 1 FROM leases WHERE job_id=?", (jid,)).fetchone() is None
    finally:
        dispatcher._lease_release = original_release
        state.close()


def test_recover_preserves_lease_when_rest_release_is_uncertain() -> None:
    state, cfg = _state()
    jid = seed_job(state, number=32, head="h32")
    state.db.execute(
        "INSERT INTO leases(repo,number,job_id,claimed_at) VALUES(?,?,?,?)",
        ("o/r", 32, jid, "2026-01-01T00:00:00Z"),
    )
    state.db.commit()
    original_release = dispatcher._lease_release
    dispatcher._lease_release = lambda *_args: (_ for _ in ()).throw(RuntimeError("REST verification failed"))
    try:
        result = dispatcher.recover_interrupted(cfg, state)
        assert result[0]["released"] is False
        assert "REST verification failed" in result[0]["reason"]
        assert state.current_status(jid) == "detected"
        assert state.db.execute("SELECT 1 FROM leases WHERE job_id=?", (jid,)).fetchone() is not None
    finally:
        dispatcher._lease_release = original_release
        state.close()
