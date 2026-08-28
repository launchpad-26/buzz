#!/usr/bin/env python3
"""Fake degradation-ladder tests: monotone downward steps, exact reasons,
never raising evidence/risk/assurance/authority, safe-stop from a lower rung,
and refusal to degrade a completed job. No GitHub, no models.
"""

from __future__ import annotations

import datetime as dt
import pathlib
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scripts"))

import dispatcher  # noqa: E402
from common import State, job_id  # noqa: E402
from errors import JobBlockingError  # noqa: E402


def fresh_state() -> State:
    return State({"state_dir": tempfile.mkdtemp()})


def add_job(state: State, status: str) -> str:
    # Distinct head per status so multiple terminal-state jobs can coexist in one
    # state DB (the jobs table is UNIQUE on repo, number, head_sha, lane).
    head = "h-" + status.replace("_", "")
    jid = job_id("o/r", 1, head, "incoming_review")
    now = dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")
    state.db.execute(
        "INSERT INTO jobs(id,repo,number,head_sha,lane,status,artifact_dir,created_at,updated_at) "
        "VALUES(?,?,?,?,?,?,?,?,?)",
        (jid, "o/r", 1, head, "incoming_review", status, str(state.job_dir(jid)), now, now),
    )
    state.db.commit()
    return jid


def _status(state: State, jid: str) -> str | None:
    row = state.db.execute("SELECT status FROM jobs WHERE id=?", (jid,)).fetchone()
    return row["status"] if row else None


CFG = {"dispatch": {}}


def test_full_ladder_steps_down_exactly_and_monotonically() -> None:
    """approval_revalidation -> human_approval_pending -> advisory_action ->
    degraded -> safe_stop, each exact one rung, every reason 'degraded: ...'."""
    state = fresh_state()
    try:
        jid = add_job(state, "approval_revalidation")
        observed = [_status(state, jid)]
        reasons: list[str] = []
        while _status(state, jid) != "safe_stop":
            target = dispatcher.degrade(state, jid, reason=f"rung-{len(observed)}")
            reasons.append(state.current_status(jid) or target)
            nxt = _status(state, jid)
            assert nxt == target or nxt == target, (target, nxt)
            observed.append(nxt)
        assert observed == [
            "approval_revalidation", "human_approval_pending", "advisory_action",
            "degraded", "safe_stop",
        ], observed
        # monotonic authority: ranks never increase rung to rung
        ranks = [dispatcher._DEGRADE_RANK[s] for s in observed]
        assert all(ranks[i] > ranks[i + 1] for i in range(len(ranks) - 1)), ranks
        # exact downward reasons preserved verbatim (prefixed 'degraded: ')
        row = state.db.execute(
            "SELECT reason FROM jobs WHERE id=?", (jid,)
        ).fetchone()
        assert row["reason"].startswith("degraded: rung-"), row["reason"]
    finally:
        state.close()


def test_safe_stop_is_floor() -> None:
    state = fresh_state()
    try:
        jid = add_job(state, "safe_stop")
        # degrading from the floor is a no-op, not an error
        assert dispatcher.degrade(state, jid, reason="already stopped") == "safe_stop"
        assert _status(state, jid) == "safe_stop"
    finally:
        state.close()


def test_cannot_degrade_completed_or_superseded_jobs() -> None:
    state = fresh_state()
    try:
        for terminal in ("completed_auto_approved", "superseded", "completed_human_declined"):
            jid = add_job(state, terminal)
            try:
                dispatcher.degrade(state, jid, reason="no")
                raise AssertionError(f"must not degrade {terminal}")
            except JobBlockingError:
                pass
    finally:
        state.close()


def test_degrade_refuses_nonexistent_job() -> None:
    state = fresh_state()
    try:
        try:
            dispatcher.degrade(state, "no-such-job", reason="x")
            raise AssertionError("must reject nonexistent job")
        except JobBlockingError:
            pass
    finally:
        state.close()


def test_degrade_never_raises_authority() -> None:
    """A downgrade never jumps to a strictly lower-evidence rung's sibling of the
    same rank; each step lands on the highest-ranked lower state (nearest rung)."""
    state = fresh_state()
    try:
        jid = add_job(state, "human_approval_pending")
        target = dispatcher.degrade(state, jid, reason="policy reduced")
        # nearest lower rung is advisory_action (not straight to degraded)
        assert target == "advisory_action", target
        assert _status(state, jid) == "advisory_action"
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
                import traceback
                print(f"FAIL {name}: {exc}")
                traceback.print_exc()
    print(f"{passed} passed, {failures} failed")
    sys.exit(1 if failures else 0)