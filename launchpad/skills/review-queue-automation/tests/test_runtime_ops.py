#!/usr/bin/env python3
"""Retention, recovery, backup and health tests (T27).

Two guarantees are asserted here:

1. A simulated process crash is recoverable with `recover` and NO manual DB
   surgery — including the case the original implementation missed, where the
   worker died before or without claiming a lease.
2. A retention run deletes artifact BYTES while leaving the audit trail
   reconstructable: the job row, the ledger, and a manifest naming and hashing
   every artifact that was removed.
"""

from __future__ import annotations

import contextlib
import io
import json
import pathlib
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scripts"))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import dispatcher  # noqa: E402
from common import State  # noqa: E402
from test_dispatch_flow import _config, seed_evidence, seed_job  # noqa: E402


def _setup() -> tuple[State, dict]:
    cfg = _config()
    cfg["state_dir"] = tempfile.mkdtemp()
    cfg["logging"] = {"directory": tempfile.mkdtemp(), "format": "otel-jsonl"}
    cfg["retention"] = {"artifact_days": 30}
    return State({"state_dir": cfg["state_dir"]}), cfg


def _age(state: State, job: str, when: str = "2000-01-01T00:00:00Z") -> None:
    state.db.execute("UPDATE jobs SET updated_at=? WHERE id=?", (when, job))
    state.db.commit()


def _finish(state: State, job: str) -> None:
    state.db.execute("UPDATE jobs SET status='completed_advisory' WHERE id=?", (job,))
    state.db.commit()


# -- crash recovery ---------------------------------------------------------
def test_crash_without_a_lease_is_recoverable() -> None:
    """The gap the original `recover` had: no lease row, so nothing to iterate."""
    state, cfg = _setup()
    try:
        jid = seed_job(state, number=900, head="h900")
        state.transition(jid, "assurance")  # a worker was mid-panel when it died
        assert state.db.execute("SELECT 1 FROM leases").fetchone() is None

        recovered = dispatcher.recover_interrupted(cfg, state)
        assert [r["job"] for r in recovered] == [jid], recovered
        assert state.current_status(jid) == "safe_stop"
    finally:
        state.close()


def test_recovery_leaves_work_that_is_waiting_on_a_person_alone() -> None:
    """A pending human request is not a stranded job and must not be stopped."""
    state, cfg = _setup()
    try:
        waiting = seed_job(state, number=901, head="h901")
        for step in ("assurance", "adjudication", "approval_evaluation",
                     "human_approval_pending"):
            state.transition(waiting, step)
        queued = seed_job(state, number=902, head="h902")  # still `detected`

        dispatcher.recover_interrupted(cfg, state)

        assert state.current_status(waiting) == "human_approval_pending"
        assert state.current_status(queued) == "detected"
    finally:
        state.close()


def test_recovery_is_idempotent() -> None:
    state, cfg = _setup()
    try:
        jid = seed_job(state, number=903, head="h903")
        state.transition(jid, "evidence")
        dispatcher.recover_interrupted(cfg, state)
        assert dispatcher.recover_interrupted(cfg, state) == []
        assert state.current_status(jid) == "safe_stop"
    finally:
        state.close()


# -- retention --------------------------------------------------------------
def test_retention_is_a_dry_run_unless_applied() -> None:
    state, cfg = _setup()
    try:
        jid = seed_job(state, number=910, head="h910")
        seed_evidence(state, jid)
        _finish(state, jid)
        _age(state, jid)

        report = dispatcher.retention_sweep(cfg, state)
        assert report["applied"] is False
        assert report["eligible_jobs"] == 1
        assert (state.job_dir(jid) / "evidence.json").is_file(), (
            "a dry run must not delete anything"
        )
    finally:
        state.close()


def test_retention_deletes_artifacts_and_leaves_the_audit_trail() -> None:
    from ledger import entries

    state, cfg = _setup()
    try:
        jid = seed_job(state, number=911, head="h911")
        seed_evidence(state, jid)
        (state.job_dir(jid) / "review-A.txt").write_text("verdict", encoding="utf-8")
        from ledger import record

        record(state, job_id=jid, repo="o/r", number=911, head_sha="h911",
               kind="decision", payload={"disposition": "advisory"})
        _finish(state, jid)
        _age(state, jid)

        report = dispatcher.retention_sweep(cfg, state, apply=True)
        assert report["applied"] is True
        assert report["jobs"][0]["artifact_files"] >= 2

        # the bytes are gone
        assert not (state.root / "jobs" / jid / "review-A.txt").exists()

        # the audit trail is not
        row = state.db.execute("SELECT status FROM jobs WHERE id=?", (jid,)).fetchone()
        assert row and row["status"] == "completed_advisory"
        kinds = [item["kind"] for item in entries(state, jid)]
        assert "decision" in kinds, "the decision trail must survive a purge"

        manifests = [item for item in entries(state, jid)
                     if item.get("entry_key") == "retention_manifest"]
        assert len(manifests) == 1, "a purge must record what it removed"
        artifacts = manifests[0]["payload"]["artifacts"]
        names = {item["path"] for item in artifacts}
        assert "review-A.txt" in names and "evidence.json" in names
        assert all(item.get("sha256") for item in artifacts), (
            "the manifest must hash each artifact so a reader can tell a purged "
            "artifact from one that was never written"
        )
    finally:
        state.close()


def test_retention_never_touches_a_job_that_can_still_run() -> None:
    state, cfg = _setup()
    try:
        jid = seed_job(state, number=912, head="h912")
        seed_evidence(state, jid)
        _age(state, jid)  # old, but still `detected`

        report = dispatcher.retention_sweep(cfg, state, apply=True)
        assert report["eligible_jobs"] == 0
        assert (state.job_dir(jid) / "evidence.json").is_file()
    finally:
        state.close()


def test_retention_respects_the_configured_window() -> None:
    state, cfg = _setup()
    try:
        jid = seed_job(state, number=913, head="h913")
        seed_evidence(state, jid)
        _finish(state, jid)  # terminal, but updated_at is NOW

        assert dispatcher.retention_sweep(cfg, state)["eligible_jobs"] == 0
        # a zero-day window makes everything terminal eligible
        assert dispatcher.retention_sweep(cfg, state, days=0)["eligible_jobs"] == 1
    finally:
        state.close()


# -- cooldown reset ---------------------------------------------------------
def test_cooldown_reset_clears_providers_and_breakers() -> None:
    import budget

    state, cfg = _setup()
    try:
        from panel import mark_unavailable

        mark_unavailable(state, "claude:opus", "quota", 900)
        budget.record_failure(
            state, {"budget": {"circuit_breaker": {"failure_threshold": 1,
                                                   "cooldown_seconds": 900}}},
            "o/r", "down")

        report = dispatcher.reset_cooldowns(state)
        assert report["providers_cleared"] == 1
        assert report["breakers_cleared"] == 1
        assert state.db.execute("SELECT 1 FROM providers").fetchone() is None
        assert budget.breaker_state(state, "o/r")["status"] == budget.CLOSED
    finally:
        state.close()


# -- backup -----------------------------------------------------------------
def test_backup_produces_a_readable_copy_of_the_state() -> None:
    state, cfg = _setup()
    try:
        jid = seed_job(state, number=920, head="h920")
        destination = tempfile.mkdtemp()
        report = dispatcher.backup_state(state, destination)

        copy = State({"state_dir": tempfile.mkdtemp()})
        try:
            import shutil

            shutil.copy(report["database"], copy.db_path)
        finally:
            copy.close()
        restored = State({"state_dir": str(pathlib.Path(report["database"]).parent)})
        try:
            row = restored.db.execute("SELECT id FROM jobs WHERE id=?", (jid,)).fetchone()
            assert row and row["id"] == jid, "the backup must contain the job rows"
        finally:
            restored.close()
    finally:
        state.close()


# -- health -----------------------------------------------------------------
def test_health_reports_a_clean_state_directory_as_healthy() -> None:
    state, cfg = _setup()
    try:
        report = dispatcher.runtime_health(cfg, state)
        assert report["status"] == "healthy", report
        assert report["checks"]["database"] == "ok"
        assert report["checks"]["state_dir_writable"] is True
        assert report["open_breakers"] == []
        assert report["budget"]["limits"]["per_pr_tokens"] > 0
    finally:
        state.close()


def test_health_reports_an_open_breaker_as_degraded() -> None:
    import budget

    state, cfg = _setup()
    try:
        budget.record_failure(
            state, {"budget": {"circuit_breaker": {"failure_threshold": 1,
                                                   "cooldown_seconds": 900}}},
            "o/r", "provider down")
        report = dispatcher.runtime_health(cfg, state)
        assert report["status"] == "degraded", report
        assert report["open_breakers"] == ["o/r"]
    finally:
        state.close()


def test_health_surfaces_the_oldest_unfinished_job() -> None:
    state, cfg = _setup()
    try:
        jid = seed_job(state, number=930, head="h930")
        state.transition(jid, "assurance")
        report = dispatcher.runtime_health(cfg, state)
        assert report["oldest_unfinished_job"]["job"] == jid
    finally:
        state.close()


# -- the commands are reachable from the CLI --------------------------------
def test_new_commands_are_wired_and_side_effect_free() -> None:
    state, cfg = _setup()
    original = dispatcher.load_repo_config
    dispatcher.load_repo_config = lambda _root: (cfg, pathlib.Path("config.json"), [])
    try:
        for command, expected in (
            (["health"], "status"),
            (["retention"], "retention_days"),
            (["cooldown-reset"], "providers_cleared"),
        ):
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                assert dispatcher.main(["--repo-root", ".", *command]) == 0
            payload = json.loads(output.getvalue())
            assert expected in payload, (command, payload)
    finally:
        dispatcher.load_repo_config = original
        state.close()
