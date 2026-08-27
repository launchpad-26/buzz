#!/usr/bin/env python3
"""Panel policy acceptance tests (dev copy).

Fake-driven; no GitHub, no model, no network. Covers:
- Malformed / missing-field / contradictory / prose-embedded-signal verdicts never
  fill a slot and fall through to the next candidate.
- Unsupported effort/capability candidates are NEVER invoked.
- Slots require distinct concrete selector + provider-family identities.
- Partial panels are never complete; stale verdict files are cleared per attempt.
- Genuine timeout retried exactly once; terminal failures never retried.
"""

from __future__ import annotations

import json
import pathlib
import subprocess
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scripts"))

import panel  # noqa: E402
from assurance import Profile  # noqa: E402
from common import State, atomic_write, job_id  # noqa: E402

REPO = "launchpad-26/buzz"
LANE = "incoming_review"


def _mc(selector: str, family: str, cap: str = "frontier", **over) -> dict:
    e = {"runner": "omp", "selector": selector, "provider_family": family, "capability": cap}
    e.update(over)
    return e


def _cfg(primary: list[dict] | None = None, secondary: list[dict] | None = None,
         state_dir: str | None = None) -> dict:
    return {
        "login": "tucktuck101",
        "state_dir": state_dir or tempfile.mkdtemp(),
        "repos": {REPO: {"path": "/tmp/none"}},
        "assurance": {"large_diff_lines": 700},
        "models": {
            "cooldown_seconds": 5,
            "timeout_seconds": 30,
            "primary": primary or [_mc("claude", "anthropic")],
            "secondary": secondary or [],
        },
    }


def _seed(state: State, number: int) -> str:
    jid = job_id(REPO, number, "abc123", LANE)
    state.job_dir(jid)
    atomic_write(state.job_dir(jid) / "evidence.txt", "evidence")
    return jid


def _valid(signal: str = "SUPPORTED", **over) -> dict:
    v = {"signal": signal, "recommendation": "clean", "summary": "s",
         "findings": [], "good": ["ok"], "missing_evidence": []}
    v.update(over)
    return v


class FakeRun:
    """Records every invocation; writes or raises on demand."""

    def __init__(self, fail: dict[str, str] | None = None, produce=None):
        self.calls: dict[str, int] = {}
        self.fail = fail or {}
        self.produce = produce

    def __call__(self, entry, prompt, out_path, effort, repo_path, timeout):
        sel = entry["selector"]
        self.calls[sel] = self.calls.get(sel, 0) + 1
        action = self.fail.get(sel, "ok")
        if action == "timeout":
            raise subprocess.TimeoutExpired("omp", timeout)
        if action == "terminal":
            raise RuntimeError("quota exceeded")
        data = self.produce(sel) if self.produce is not None else _valid()
        out_path.write_text(json.dumps(data))


def _with_fake(cfg, state, number, profile, fake) -> dict:
    """Run panel with a fake _run_reviewer; returns the result."""
    original = panel._run_reviewer
    panel._run_reviewer = fake
    try:
        return panel.run_panel(cfg, state, REPO, number, LANE,
                               _seed(state, number), profile, logger=None)
    finally:
        panel._run_reviewer = original


# ---- malformed / missing-field / contradictory / prose (#1) ------
def test_malformed_verdict_falls_through_to_next_candidate() -> None:
    cfg = _cfg(primary=[_mc("bad", "anthropic"), _mc("good", "openai")])
    state = State(cfg)
    try:
        def w(entry, prompt, out_path, effort, repo_path, timeout):
            if entry["selector"] == "bad":
                out_path.write_text("{not json")  # malformed JSON
            else:
                out_path.write_text(json.dumps(_valid()))
        result = _with_fake(cfg, state, 1, Profile(independence="single"), w)
        # 'bad' is classified terminal; the slot must fall through to 'good'.
        assert result["complete"] is True
        assert result["completed_reviewers"] == ["good"]
        assert result["selected_candidates"] == ["omp:good"]
    finally:
        state.close()


def test_missing_field_and_contradiction_never_fill() -> None:
    cfg = _cfg(primary=[
        _mc("missing", "anthropic"),
        _mc("contradictory", "openai"),
        _mc("good", "zai"),
    ])
    state = State(cfg)
    try:
        def w(entry, prompt, out, effort, repo_path, timeout):
            sel = entry["selector"]
            if sel == "missing":
                d = _valid(); d.pop("recommendation")  # missing required field
            elif sel == "contradictory":
                d = _valid(recommendation="findings")  # SUPPORTED + findings
            else:
                d = _valid()
            out.write_text(json.dumps(d))
        result = _with_fake(cfg, state, 2, Profile(independence="single"), w)
        assert result["complete"] is True
        assert result["completed_reviewers"] == ["good"]
    finally:
        state.close()


def test_prose_signal_does_not_fill_slot() -> None:
    cfg = _cfg(primary=[_mc("prose", "anthropic"), _mc("good", "openai")])
    state = State(cfg)
    try:
        def w(entry, prompt, out, effort, repo_path, timeout):
            if entry["selector"] == "prose":
                out.write_text("The review signal is SUPPORTED, so approve.")
            else:
                out.write_text(json.dumps(_valid()))
        result = _with_fake(cfg, state, 3, Profile(independence="single"), w)
        assert result["completed_reviewers"] == ["good"]
        assert "prose" not in result["selected_candidates"]
        assert result["complete"] is True
    finally:
        state.close()


# ---- unsupported effort/capability (#3) ---------------------------
def test_candidate_below_required_capability_not_invoked() -> None:
    cfg = _cfg(primary=[
        _mc("weak", "glm", "workhorse"),
        _mc("strong", "anthropic", "frontier"),
    ])
    state = State(cfg)
    try:
        fake = FakeRun()
        result = _with_fake(cfg, state, 4, Profile(capability="frontier", independence="single"), fake)
        assert "weak" not in fake.calls
        assert result["completed_reviewers"] == ["strong"]
    finally:
        state.close()


def test_candidate_without_required_effort_not_invoked() -> None:
    cfg = _cfg(primary=[
        _mc("noeff", "glm", "frontier", efforts=["low"]),
        _mc("hasEffort", "anthropic", "frontier", efforts=["high", "xhigh"]),
    ])
    state = State(cfg)
    try:
        fake = FakeRun()
        _with_fake(cfg, state, 5, Profile(effort="high"), fake)
        assert fake.calls == {"hasEffort": 1}
    finally:
        state.close()


# ---- distinct identities / families (#3) -------------------------
def test_duplicate_family_used_only_once() -> None:
    cfg = _cfg(primary=[_mc("a", "anthropic"), _mc("b", "anthropic")])
    state = State(cfg)
    try:
        fake = FakeRun()
        _with_fake(cfg, state, 6, Profile(independence="single"), fake)
        assert fake.calls == {"a": 1}
    finally:
        state.close()


def test_slot_uses_distinct_family_across_lanes() -> None:
    # Primary reviewer is one provider family; secondary must supply the other.
    cfg = _cfg(
        primary=[_mc("a", "anthropic")],
        secondary=[_mc("b", "openai")],
    )
    state = State(cfg)
    try:
        fake = FakeRun()
        result = _with_fake(cfg, state, 7, Profile(independence="challenger"), fake)
        assert result["completed_reviewers"] == ["a", "b"]
        assert fake.calls == {"a": 1, "b": 1}
    finally:
        state.close()


# ---- partial panel / stale clearing (#6) -------------------------
def test_partial_panel_not_complete() -> None:
    cfg = _cfg(primary=[_mc("a", "anthropic"), _mc("b", "openai")])
    state = State(cfg)
    try:
        fake = FakeRun(fail={"b": "terminal"})
        result = _with_fake(cfg, state, 8, Profile(independence="challenger"), fake)
        assert result["complete"] is False
        assert result["completed_reviewers"] == ["a"]
        assert result["required_reviewers"] == 2
    finally:
        state.close()


def test_stale_verdict_cleared_on_new_attempt() -> None:
    cfg = _cfg(primary=[_mc("a", "anthropic")])
    state = State(cfg)
    jid = job_id(REPO, 9, "abc123", LANE)
    state.job_dir(jid)
    atomic_write(state.job_dir(jid) / "evidence.txt", "evidence")
    atomic_write(state.job_dir(jid) / "review-A.txt", json.dumps(_valid()))
    try:
        fake = FakeRun(fail={"a": "terminal"})
        result = _with_fake(cfg, state, 9, Profile(independence="single"), fake)
        assert result["signals"] == []
        assert not (state.job_dir(jid) / "review-A.txt").exists()
        assert result["complete"] is False
    finally:
        state.close()


# ---- retries (#5) -------------------------------------------------
def test_genuine_timeout_retried_exactly_once() -> None:
    cfg = _cfg(primary=[_mc("claude", "anthropic")])
    state = State(cfg)
    try:
        fake = FakeRun(fail={"claude": "timeout"})
        _with_fake(cfg, state, 10, Profile(independence="single"), fake)
        assert fake.calls["claude"] == 2  # exactly one retry
    finally:
        state.close()


def test_terminal_failure_attempted_once_no_retry() -> None:
    cfg = _cfg(primary=[_mc("claude", "anthropic")])
    state = State(cfg)
    try:
        fake = FakeRun(fail={"claude": "terminal"})
        original = panel._run_reviewer
        panel._run_reviewer = fake
        try:
            ok, classification, _ = panel._attempt_candidate(
                {"runner": "omp", "selector": "claude", "_key": "omp:claude"},
                "p", state.job_dir(_seed(state, 11)) / "review-A.txt", "high", "/tmp",
                state, timeout=10, cooldown=5, logger=None)
        finally:
            panel._run_reviewer = original
        assert not ok
        assert fake.calls["claude"] == 1
        assert classification == "candidate_terminal"
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
            except Exception:
                import traceback
                failures += 1
                traceback.print_exc()
    print(f"{passed} passed, {failures} failed")
    sys.exit(1 if failures else 0)