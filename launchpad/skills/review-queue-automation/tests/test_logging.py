#!/usr/bin/env python3
"""Logging acceptance tests for review-queue-automation.

- Every phase/status change appends exactly one valid JSON object to events.jsonl.
- Every event has timestamp, severity_text, body, resource.service.name, job.id,
  repository, PR number, lane, phase, outcome.
- Two panel attempts -> distinct attempt-001/002.json artifacts with the required
  fields.
- No secret-like values or evidence/PR-body text in events or artifacts.
- stderr > 8KB is capped in diagnostics and reduced to a safe summary in events.
"""

from __future__ import annotations

import json
import pathlib
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scripts"))

from logging_otel import MAX_STDERR_BYTES, JobLogger, read_events  # noqa: E402


def _logger() -> tuple[JobLogger, pathlib.Path]:
    root = pathlib.Path(tempfile.mkdtemp())
    return JobLogger(
        root, "job-abc", repo="launchpad-26/buzz", number=42, lane="incoming_review"
    ), root


def _standard_logger():
    log_dir = pathlib.Path(tempfile.mkdtemp())
    jl = JobLogger(log_dir, "job-abc", repo="launchpad-26/buzz", number=42, lane="incoming_review")
    return jl, log_dir


def test_each_event_is_valid_json_line() -> None:
    jl, _ = _standard_logger()
    jl.info(body="phase start", phase="evidence", outcome="started")
    jl.transition("detected", "evidence", phase="evidence", reason="collected")
    events = read_events(jl.events_path)
    assert len(events) == 2
    for line in jl.events_path.read_text(encoding="utf-8").splitlines():
        json.loads(line)  # must not raise


def test_event_required_fields_present() -> None:
    jl, _ = _standard_logger()
    jl.info(body="attempt complete", phase="assurance", outcome="complete")
    ev = read_events(jl.events_path)[0]
    for key in ("timestamp", "severity_text", "body"):
        assert key in ev and ev[key]
    assert ev["resource"]["service.name"] == "review-queue-automation"
    attrs = ev["attributes"]
    for key in ("job.id", "github.repository", "github.pull_request.number", "review.lane", "review.phase", "review.outcome"):
        assert key in attrs


def test_two_attempts_distinct_immutable() -> None:
    jl, _ = _standard_logger()
    a1 = jl.attempt({"profile": {"capability": "workhorse"}, "signals": ["SUPPORTED"], "outcome": "complete"})
    a2 = jl.attempt({"profile": {"capability": "frontier"}, "signals": [], "outcome": "degraded"})
    assert a1 == 1 and a2 == 2
    files = sorted(p.name for p in jl.attempts_dir.glob("attempt-*.json"))
    assert files == ["attempt-001.json", "attempt-002.json"]
    for p in jl.attempts_dir.glob("attempt-*.json"):
        data = json.loads(p.read_text(encoding="utf-8"))
        assert "profile" in data and "job.id" in data and "outcome" in data


def test_artifacts_contain_no_secrets_or_evidence() -> None:
    jl, _ = _standard_logger()
    jl.info(
        body="candidate result", phase="assurance", outcome="complete",
        attributes={"ai.model": "claude-sonnet", "token": "sk-abc", "api_key": "x", "evidence": "<<<pr_meta>>>body"},
    )
    jl.attempt({"profile": {}, "token": "sk-secret", "signals": [], "outcome": "complete"})
    blob = "\n".join(
        [jl.events_path.read_text(encoding="utf-8")]
        + [p.read_text(encoding="utf-8") for p in jl.attempts_dir.glob("*.json")]
    )
    assert "sk-abc" not in blob
    assert "sk-secret" not in blob
    assert "<<<pr_meta>>>body" not in blob
    assert "value-redacted" not in blob
    assert "<redacted>" in blob


def test_stderr_capped_and_events_summarize() -> None:
    jl, _ = _standard_logger()
    big = "X" * 20000
    rel = jl.diagnostic("claude-stderr", big, attempt=1, candidate="claude")
    diag_path = jl.log_root / rel
    assert diag_path.read_text(encoding="utf-8") == ("X" * MAX_STDERR_BYTES)
    assert len(diag_path.read_text(encoding="utf-8")) <= MAX_STDERR_BYTES
    # events do NOT carry raw stderr
    events = read_events(jl.events_path)
    for ev in events:
        assert "X" * 100 not in json.dumps(ev)


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