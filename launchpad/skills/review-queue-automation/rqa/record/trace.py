"""`jobs/<job>/trace.jsonl` — the non-authoritative milestone trace,
`code/P-12-record.md` §6's trace paragraph (U-RESILIENCE-08, U-RESILIENCE-14).

One JSON object per orchestration milestone, for an operator or a future tool to
read. **Nothing in RQA reads it back for a trust decision** — §7: "Does not read
`jobs/<job>/trace.jsonl` for any purpose, including `explain`". It contributes no
name to §1's re-export list precisely because it is invisible to the authoritative
side of this package.

Two mechanisms, both carried from the estate because they are what make a
concurrently-written file usable at all:

* **An exclusive `flock` on a sidecar lock file for the whole write.** It gives
  cross-process safety, and it is what makes per-job attempt-number allocation
  exclusive: `allocate_attempt_number` reads the numbers already allocated and writes
  the next one while still holding the lock, so two concurrent writers cannot read
  the same maximum and both claim it (U-RESILIENCE-08).
* **Temp file in the same directory, `fsync`, then rename over the original**
  (U-RESILIENCE-14). The whole new content — every old line plus the one new line —
  is written to the temp file, so a crash between writes leaves the previous,
  complete file in place rather than a torn final line.

`container.md` §5 attributes the same technique to P-03's `snapshots/<hash>.json`;
these are two independent implementations of one pattern, not a shared dependency —
nothing here imports `rqa.policy`, and nothing here writes a snapshot.
"""

from __future__ import annotations

import fcntl
import json
import os
from collections.abc import Mapping
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from rqa.record.hashing import canonical_json

__all__ = [
    "ATTEMPT_ALLOCATED",
    "JOBS_DIR_NAME",
    "LOCK_FILENAME",
    "TRACE_FILENAME",
    "allocate_attempt_number",
    "append_trace",
    "trace_lines",
    "trace_path",
]

#: Relative to the state directory, per `container.md` §5's trace row.
JOBS_DIR_NAME = "jobs"
TRACE_FILENAME = "trace.jsonl"
LOCK_FILENAME = "trace.lock"

#: The milestone `allocate_attempt_number` records. A trace consumer keys off a fixed
#: vocabulary rather than free-form strings (U-DISPATCH-19's retained decision); the
#: caller names its own milestones, and this is the one this module names itself.
ATTEMPT_ALLOCATED = "attempt_allocated"


def trace_path(*, state_dir: str | os.PathLike[str], job_id: str) -> Path:
    """`<state_dir>/jobs/<job>/trace.jsonl`."""
    return Path(state_dir) / JOBS_DIR_NAME / job_id / TRACE_FILENAME


def _lock_path(*, state_dir: str | os.PathLike[str], job_id: str) -> Path:
    return trace_path(state_dir=state_dir, job_id=job_id).with_name(LOCK_FILENAME)


def _read_lines(path: Path) -> list[str]:
    try:
        body = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return []
    return [line for line in body.splitlines() if line.strip()]


def _replace_atomically(path: Path, *, lines: list[str]) -> None:
    """U-RESILIENCE-14: same-directory temp file, flush, fsync, atomic rename."""
    temporary = path.with_name(f"{path.name}.tmp")
    body = "".join(f"{line}\n" for line in lines)
    try:
        with open(temporary, "w", encoding="utf-8") as handle:
            handle.write(body)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except OSError:
        temporary.unlink(missing_ok=True)
        raise


def _write_under_lock(
    *, state_dir: str | os.PathLike[str], job_id: str, build: Any
) -> Mapping[str, Any]:
    """Hold the job's lock, let `build` decide the line from the existing ones, write.

    The lock is held across the read *and* the write. That is the whole property:
    a build function that derives its line from what is already there — the attempt
    allocator does — cannot be raced by another process doing the same.
    """
    path = trace_path(state_dir=state_dir, job_id=job_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    lock = _lock_path(state_dir=state_dir, job_id=job_id)
    with open(lock, "a+", encoding="utf-8") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        try:
            existing = _read_lines(path)
            record = build(existing)
            _replace_atomically(path, lines=[*existing, canonical_json(payload=record)])
            return record
        finally:
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def append_trace(
    *,
    state_dir: str | os.PathLike[str],
    job_id: str,
    event: str,
    fields: Mapping[str, Any] | None = None,
    at: datetime | None = None,
) -> Mapping[str, Any]:
    """Append one milestone object and return exactly what was written.

    `fields` is plain JSON-safe data, checked by the same `canonical_json` the record
    itself uses, so a trace line cannot carry a value the record would have refused.
    """
    moment = (at or datetime.now(timezone.utc)).astimezone(timezone.utc)

    def build(_existing: list[str]) -> Mapping[str, Any]:
        return {
            "job": job_id,
            "event": event,
            "at": moment.isoformat(timespec="microseconds"),
            **(dict(fields) if fields else {}),
        }

    return _write_under_lock(state_dir=state_dir, job_id=job_id, build=build)


def allocate_attempt_number(
    *,
    state_dir: str | os.PathLike[str],
    job_id: str,
    fields: Mapping[str, Any] | None = None,
    at: datetime | None = None,
) -> int:
    """The next attempt number for this job, allocated exclusively (U-RESILIENCE-08).

    Read-then-increment under the job's exclusive lock, and durable before the lock is
    released: the allocation is the trace line. Two concurrent callers therefore get
    two distinct numbers, and a crash cannot hand the same number out twice.
    """
    moment = (at or datetime.now(timezone.utc)).astimezone(timezone.utc)

    def build(existing: list[str]) -> Mapping[str, Any]:
        highest = 0
        for line in existing:
            try:
                previous = json.loads(line)
            except ValueError:
                continue
            number = previous.get("attempt") if isinstance(previous, dict) else None
            if type(number) is int and number > highest:
                highest = number
        return {
            "job": job_id,
            "event": ATTEMPT_ALLOCATED,
            "at": moment.isoformat(timespec="microseconds"),
            "attempt": highest + 1,
            **(dict(fields) if fields else {}),
        }

    return int(_write_under_lock(state_dir=state_dir, job_id=job_id, build=build)["attempt"])


def trace_lines(
    *, state_dir: str | os.PathLike[str], job_id: str
) -> tuple[Mapping[str, Any], ...]:
    """Every trace object written for `job_id`, in order.

    For an operator, a future tool, and this part's own tests. It is never called by
    `append`, `verify`, `explain` or any other reconstruction: §7 forbids the trace
    from being an authority source, and this function's existence does not change that.
    """
    path = trace_path(state_dir=state_dir, job_id=job_id)
    return tuple(json.loads(line) for line in _read_lines(path))
