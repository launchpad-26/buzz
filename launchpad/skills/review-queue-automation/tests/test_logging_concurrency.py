#!/usr/bin/env python3
"""Concurrency + dt-level logging acceptance tests (dev copy).

Fake-driven. Covers requirements 5/7:
- Event JSONL appends are process/thread safe (fcntl lock, no interleaved lines).
- Attempt numbering is concurrency-safe (distinct, immutable attempt-*.json).
- Diagnostics are capped by UTF-8 bytes without splitting a multi-byte char.
- The JWT regex is correct; secrets and JWTs are redacted recursively.
- Events carry version/head/phase/outcome/disposition/decision/request/risk.
"""

from __future__ import annotations

import json
import pathlib
import sys
import tempfile
import threading

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scripts"))

from logging_otel import JobLogger, read_events  # noqa: E402


def _logger(max_stderr: int = 8192) -> JobLogger:
    root = pathlib.Path(tempfile.mkdtemp())
    return JobLogger(root, "job-c", repo="o/r", number=1, lane="incoming_review",
                     max_stderr=max_stderr, service_version="1.2.3", head="sha-0102")


def test_concurrent_event_writes_are_not_interleaved() -> None:
    jl = _logger()
    n = 40

    def worker(i):
        jl.info(body=f"event {i}", phase="assurance", outcome="complete")

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(n)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    lines = jl.events_path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == n
    for line in lines:
        json.loads(line)  # each line must be a complete, parseable object


def test_concurrent_attempt_numbering_distinct_immutable() -> None:
    jl = _logger()
    n = 30
    results: list[int] = []
    lock = threading.Lock()

    def worker(i):
        num = jl.attempt({"i": i})
        with lock:
            results.append(num)

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(n)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert len(set(results)) == n  # every number distinct; none reused
    files = sorted(p.name for p in jl.attempts_dir.glob("attempt-*.json"))
    assert len(files) == n
    for i, fname in enumerate(sorted(p.name for p in jl.attempts_dir.glob("attempt-*.json")), 1):
        assert fname == f"attempt-{i:03d}.json"


def test_diagnostics_cap_by_utf8_bytes_without_splitting() -> None:
    jl = _logger(max_stderr=8)
    # U+2014 EM DASH is a 3-byte char; capping must not split it.
    jl.diagnostic("stderr", "ab\u2014cd", attempt=1, candidate="c")
    content = next(jl.diag_dir.glob("attempt-001-c-stderr.txt")).read_text(encoding="utf-8")
    assert len(content.encode("utf-8")) <= 8
    assert content  # decodes cleanly: no half multi-byte char remains


def test_jwt_and_secrets_redacted() -> None:
    jl = _logger()
    jl.info(body="probe", phase="assurance", outcome="complete",
            attributes={"token": "sk-123", "authorization": "zzz", "jwt": "eyJh.bc.def", "note": "n"})
    jl.diagnostic("stderr",
                  "Authorization: Bearer eyJk.xxxx.yyyy token=ghp_1111112222",
                  attempt=1, candidate="m")
    diag = next(jl.diag_dir.glob("attempt-001-m-stderr.txt")).read_text(encoding="utf-8")
    assert "eyJk.xxxx.yyyy" not in diag
    assert "ghp_1111112222" not in diag
    event = json.dumps(read_events(jl.events_path))
    assert "sk-123" not in event
    assert "zzz" not in event
    assert "eyJh.bc.def" not in event
    assert "<redacted>" in event


def test_events_carry_version_head_phase_outcome_disposition() -> None:
    jl = _logger()
    jl.info(body="svc", phase="assurance", outcome="complete",
            attributes={"error.disposition": "candidate_terminal",
                        "decision": "HUMAN", "request.id": "req-1",
                        "risk.score": 7})
    events = read_events(jl.events_path)
    assert len(events) == 1
    attrs = events[0]["attributes"]
    assert attrs["service.version"] == "1.2.3"
    assert attrs["github.head.sha"] == "sha-0102"
    assert attrs["review.phase"] == "assurance"
    assert attrs["review.outcome"] == "complete"
    assert attrs["error.disposition"] == "candidate_terminal"
    assert attrs["decision"] == "HUMAN"
    assert attrs["request.id"] == "req-1"
    assert attrs["risk.score"] == 7


def test_read_events_roundtrip() -> None:
    jl = _logger()
    jl.info(body="first", phase="a", outcome="x")
    jl.warning(body="second", phase="b", outcome="y")
    events = read_events(jl.events_path)
    assert len(events) == 2
    assert events[0]["severity_text"] == "INFO"
    assert events[1]["severity_text"] == "WARN"


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