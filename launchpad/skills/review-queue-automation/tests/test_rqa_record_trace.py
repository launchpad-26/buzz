#!/usr/bin/env python3
"""The non-authoritative trace — `code/P-12-record.md` §6's trace paragraph and §7,
carrying U-RESILIENCE-08, U-RESILIENCE-14 and U-DOCS-55's concurrency property.

No pytest: every `test_*` function here takes no arguments, per `tests/run_all.py`.

U-DOCS-55 is kept for the reason its disposition gives: "Sequential logging cannot
expose a read-then-increment race, and uniqueness alone cannot rule out a corrupted
file; both properties are needed". So the concurrency test asserts both — distinct
numbers *and* a file every line of which still parses.
"""

from __future__ import annotations

import json
import os
import pathlib
import sys
import tempfile
import threading
from datetime import datetime, timezone

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

import rqa.record.trace as trace_module  # noqa: E402
from rqa.record import PayloadNotSerializable  # noqa: E402
from rqa.record.trace import (  # noqa: E402
    ATTEMPT_ALLOCATED,
    LOCK_FILENAME,
    allocate_attempt_number,
    append_trace,
    trace_lines,
    trace_path,
)


def test_a_milestone_is_appended_as_one_json_object_per_line() -> None:
    with tempfile.TemporaryDirectory() as state_dir:
        append_trace(state_dir=state_dir, job_id="job-1", event="claimed")
        append_trace(
            state_dir=state_dir, job_id="job-1", event="planned", fields={"obligations": 3}
        )
        path = trace_path(state_dir=state_dir, job_id="job-1")
        assert path == pathlib.Path(state_dir) / "jobs" / "job-1" / "trace.jsonl"

        body = path.read_text(encoding="utf-8")
        assert body.endswith("\n")
        objects = [json.loads(line) for line in body.splitlines()]
        assert [entry["event"] for entry in objects] == ["claimed", "planned"]
        assert objects[1]["obligations"] == 3
        assert all(entry["job"] == "job-1" for entry in objects)
        assert trace_lines(state_dir=state_dir, job_id="job-1") == tuple(objects)


def test_the_timestamp_is_utc_with_microseconds() -> None:
    with tempfile.TemporaryDirectory() as state_dir:
        moment = datetime(2026, 9, 12, 8, 30, 15, 123456, tzinfo=timezone.utc)
        written = append_trace(
            state_dir=state_dir, job_id="job-1", event="claimed", at=moment
        )
        assert written["at"] == "2026-09-12T08:30:15.123456+00:00"


def test_each_job_gets_its_own_trace_and_its_own_lock() -> None:
    with tempfile.TemporaryDirectory() as state_dir:
        append_trace(state_dir=state_dir, job_id="job-1", event="claimed")
        append_trace(state_dir=state_dir, job_id="job-2", event="claimed")
        assert len(trace_lines(state_dir=state_dir, job_id="job-1")) == 1
        assert (
            trace_path(state_dir=state_dir, job_id="job-1").with_name(LOCK_FILENAME).exists()
        )


def test_a_trace_field_that_is_not_json_safe_is_refused_by_the_same_check() -> None:
    """The trace uses the record's own `canonical_json`, so a value the record would
    have refused cannot reach a trace line either."""
    with tempfile.TemporaryDirectory() as state_dir:
        raised = False
        try:
            append_trace(
                state_dir=state_dir,
                job_id="job-1",
                event="claimed",
                fields={"when": datetime.now(timezone.utc)},
            )
        except PayloadNotSerializable:
            raised = True
        assert raised
        assert not trace_path(state_dir=state_dir, job_id="job-1").exists()


# -- U-RESILIENCE-08: exclusive attempt-number allocation ----------------------


def test_attempt_numbers_are_allocated_in_order_and_recorded_in_the_trace() -> None:
    with tempfile.TemporaryDirectory() as state_dir:
        assert allocate_attempt_number(state_dir=state_dir, job_id="job-1") == 1
        assert allocate_attempt_number(state_dir=state_dir, job_id="job-1") == 2
        append_trace(state_dir=state_dir, job_id="job-1", event="planned")
        assert allocate_attempt_number(state_dir=state_dir, job_id="job-1") == 3

        objects = trace_lines(state_dir=state_dir, job_id="job-1")
        assert [entry.get("attempt") for entry in objects] == [1, 2, None, 3]
        assert objects[0]["event"] == ATTEMPT_ALLOCATED


def test_allocation_is_per_job() -> None:
    with tempfile.TemporaryDirectory() as state_dir:
        allocate_attempt_number(state_dir=state_dir, job_id="job-1")
        assert allocate_attempt_number(state_dir=state_dir, job_id="job-2") == 1


def test_u_docs_55_concurrent_writers_allocate_distinct_numbers_and_leave_valid_json() -> None:
    """U-DOCS-55, kept: concurrent distinct-number *and* valid-JSON assertions.

    A read-then-increment without the lock hands the same number to two writers; a
    plain append without the temp-file replacement interleaves two half-written lines.
    Both are asserted here because neither rules out the other.

    Plain `threading.Thread`, not a pool: this suite puts `scripts/` on `sys.path`, and
    `scripts/queue.py` shadows the standard library's `queue` that a pool imports.
    A `Barrier` releases every writer at once so the read-then-increment window is
    genuinely contended.
    """
    with tempfile.TemporaryDirectory() as state_dir:
        workers = 8
        start = threading.Barrier(workers)
        allocated: list[int] = []
        guard = threading.Lock()

        def allocate() -> None:
            start.wait()
            number = allocate_attempt_number(state_dir=state_dir, job_id="job-1")
            with guard:
                allocated.append(number)

        threads = [threading.Thread(target=allocate) for _ in range(workers)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        assert sorted(allocated) == list(range(1, workers + 1)), allocated

        body = trace_path(state_dir=state_dir, job_id="job-1").read_text(encoding="utf-8")
        objects = [json.loads(line) for line in body.splitlines()]
        assert len(objects) == workers
        assert sorted(entry["attempt"] for entry in objects) == list(range(1, workers + 1))


# -- U-RESILIENCE-14: crash-safe replacement -----------------------------------


def test_a_write_that_fails_at_the_rename_leaves_the_previous_complete_file() -> None:
    """U-RESILIENCE-14's point: same-directory temp file, fsync, atomic rename. An
    interrupted write leaves the previous, complete file — never a torn final line —
    and leaves no temp file behind."""
    with tempfile.TemporaryDirectory() as state_dir:
        append_trace(state_dir=state_dir, job_id="job-1", event="claimed")
        path = trace_path(state_dir=state_dir, job_id="job-1")
        before = path.read_text(encoding="utf-8")

        original = trace_module.os.replace

        def failing_replace(source, target):
            raise OSError("interrupted between writes")

        trace_module.os.replace = failing_replace
        try:
            raised = False
            try:
                append_trace(state_dir=state_dir, job_id="job-1", event="planned")
            except OSError:
                raised = True
            assert raised
        finally:
            trace_module.os.replace = original

        assert path.read_text(encoding="utf-8") == before
        assert [entry.name for entry in path.parent.iterdir() if entry.name.endswith(".tmp")] == []


def test_the_whole_file_is_rewritten_through_one_rename_per_append() -> None:
    """The mechanism, observed rather than asserted from the source: each append
    replaces the file, and the replacement carries every earlier line plus the new one."""
    with tempfile.TemporaryDirectory() as state_dir:
        renames: list[tuple[str, str]] = []
        original = trace_module.os.replace

        def watched_replace(source, target):
            renames.append((str(source), str(target)))
            return original(source, target)

        trace_module.os.replace = watched_replace
        try:
            append_trace(state_dir=state_dir, job_id="job-1", event="claimed")
            append_trace(state_dir=state_dir, job_id="job-1", event="planned")
        finally:
            trace_module.os.replace = original

        assert len(renames) == 2
        for source, target in renames:
            assert source.endswith(".tmp")
            assert os.path.dirname(source) == os.path.dirname(target), "same directory"
        assert len(trace_lines(state_dir=state_dir, job_id="job-1")) == 2


def test_an_unparseable_earlier_line_does_not_stop_the_next_allocation() -> None:
    """The trace is not authoritative (§7): a hand-edited line is skipped, not fatal."""
    with tempfile.TemporaryDirectory() as state_dir:
        allocate_attempt_number(state_dir=state_dir, job_id="job-1")
        path = trace_path(state_dir=state_dir, job_id="job-1")
        with open(path, "a", encoding="utf-8") as handle:
            handle.write("this is not json\n")
        assert allocate_attempt_number(state_dir=state_dir, job_id="job-1") == 2
