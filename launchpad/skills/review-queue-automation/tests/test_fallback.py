#!/usr/bin/env python3
"""Fallback + error-handling acceptance tests for panel.py.

Pinned criteria:
- transient failure  -> candidate attempted exactly twice before fallback
- terminal failure   -> candidate attempted exactly once before fallback
- candidate failure  -> cooldown persisted in SQLite + attempt artifact
- available fallback -> attempted after preferred failure
- successful candidate in a lane -> later lane candidates not run
"""

from __future__ import annotations

import json
import pathlib
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scripts"))

import panel  # noqa: E402
from assurance import Profile  # noqa: E402
from common import State, job_id  # noqa: E402

REPO = "launchpad-26/buzz"


def cfg(state_dir: str) -> dict:
    return {
        "login": "tucktuck101",
        "state_dir": state_dir,
        "repos": {REPO: {"path": "/tmp/none"}},
        "assurance": {"large_diff_lines": 700},
        "models": {
            "cooldown_seconds": 1000,
            "timeout_seconds": 30,
            "primary": [
                {"runner": "x", "selector": "claude", "provider_family": "anthropic", "capability": "frontier"},
                {"runner": "x", "selector": "glm", "provider_family": "glm", "capability": "frontier"},
            ],
            "secondary": [
                {"runner": "x", "selector": "gpt", "provider_family": "openai", "capability": "frontier"},
            ],
        },
    }


def _seed(state: State) -> str:
    jid = job_id(REPO, 7, "abc", "incoming_review")
    state.job_dir(jid)
    path = state.job_dir(jid) / "evidence.txt"
    path.write_text("evidence")
    return jid


class CallCounter:
    def __init__(self, raise_for: dict[str, str]):
        self.calls: dict[str, int] = {}
        self.raise_for = raise_for

    def __call__(self, entry, prompt, out_path, effort, repo_path, timeout):
        sel = entry["selector"]
        self.calls[sel] = self.calls.get(sel, 0) + 1
        action = self.raise_for.get(sel, "ok")
        if action == "transient":
            import subprocess as sp

            raise sp.TimeoutExpired("x", 1)
        if action == "terminal":
            raise RuntimeError("401 unauthorized")
        if action == "blocking":
            from errors import JobBlockingError

            raise JobBlockingError("invalid config")
        out_path.write_text(json.dumps({"signal": "SUPPORTED", "recommendation": "clean", "summary": "test", "findings": [], "good": [], "missing_evidence": []}))


def test_transient_retried_exactly_twice_then_cooldown():
    state = State(cfg(tempfile.mkdtemp()))
    try:
        jid = _seed(state)
        counter = CallCounter({"claude": "transient"})
        original = panel._run_reviewer
        panel._run_reviewer = counter
        try:
            ok, classification, _ = panel._attempt_candidate(
                {"runner": "x", "selector": "claude", "_key": "x:claude"},
                "p", state.job_dir(jid) / "review-A.txt", "medium", "/tmp",
                state, timeout=10, cooldown=1000,
            )
        finally:
            panel._run_reviewer = original
        assert not ok
        assert counter.calls["claude"] == 2, f"expected 2 attempts, got {counter.calls.get('claude')}"
        # cooldown persisted
        row = state.db.execute("SELECT unavailable_until FROM providers WHERE key='x:claude'").fetchone()
        assert row and row["unavailable_until"]
    finally:
        state.close()


def test_terminal_attempted_once_no_retry():
    state = State(cfg(tempfile.mkdtemp()))
    try:
        jid = _seed(state)
        counter = CallCounter({"claude": "terminal"})
        original = panel._run_reviewer
        panel._run_reviewer = counter
        try:
            ok, classification, _ = panel._attempt_candidate(
                {"runner": "x", "selector": "claude", "_key": "x:claude"},
                "p", state.job_dir(jid) / "review-A.txt", "medium", "/tmp",
                state, timeout=10, cooldown=1000,
            )
        finally:
            panel._run_reviewer = original
        assert not ok
        assert counter.calls["claude"] == 1, f"terminal should retry 0 times, got {counter.calls.get('claude')}"
    finally:
        state.close()


def test_fallback_attempted_after_preferred_failure():
    state = State(cfg(tempfile.mkdtemp()))
    try:
        jid = _seed(state)
        counter = CallCounter({"claude": "terminal", "glm": "ok"})
        original = panel._run_reviewer
        panel._run_reviewer = counter
        try:
            result = panel.run_panel(
                cfg(state.root), state, REPO, 7, "incoming_review", jid,
                Profile(independence="single"),
            )
        finally:
            panel._run_reviewer = original
        assert counter.calls["claude"] == 1
        assert counter.calls["glm"] == 1
        assert result["completed_reviewers"] == ["glm"]
        assert result["complete"] is True
    finally:
        state.close()


def test_success_in_lane_skips_later_candidates():
    state = State(cfg(tempfile.mkdtemp()))
    try:
        jid = _seed(state)
        counter = CallCounter({"claude": "ok"})
        original = panel._run_reviewer
        panel._run_reviewer = counter
        try:
            result = panel.run_panel(
                cfg(state.root), state, REPO, 7, "incoming_review", jid,
                Profile(independence="single"),
            )
        finally:
            panel._run_reviewer = original
        assert counter.calls["claude"] == 1
        assert "glm" not in counter.calls
        assert result["completed_reviewers"] == ["claude"]
    finally:
        state.close()


def test_job_blocking_propagates_and_no_cooldown():
    state = State(cfg(tempfile.mkdtemp()))
    try:
        jid = _seed(state)
        counter = CallCounter({"claude": "blocking"})
        original = panel._run_reviewer
        panel._run_reviewer = counter
        try:
            from errors import JobBlockingError

            raised = False
            try:
                panel.run_panel(
                    cfg(state.root), state, REPO, 7, "incoming_review", jid,
                    Profile(independence="single"),
                )
            except JobBlockingError:
                raised = True
            assert raised
            # job_blocking must not write a cooldown
            row = state.db.execute("SELECT 1 FROM providers WHERE key='x:claude'").fetchone()
            assert row is None
        finally:
            panel._run_reviewer = original
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