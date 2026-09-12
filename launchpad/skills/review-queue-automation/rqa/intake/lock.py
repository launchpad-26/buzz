"""The exclusive, non-blocking sweep `flock` and its kernel release —
`code/P-01-intake.md` §1, §3 step 1, §5 (U-DISPATCH-02).

`lock` is not a table: a zero-length file at `<state_dir>/lock`, opened once
per `tick()` call and held open via an exclusive, non-blocking
`fcntl.flock(fd, LOCK_EX | LOCK_NB)` for the process's whole lifetime. No
column, no row — the kernel's own file-descriptor table is the state, which is
what makes release automatic on any process exit, including a crash: closing
the returned handle, letting it get garbage-collected, or the process dying
outright (`SIGKILL`, a hard crash) all release it, because the kernel tears
down every open file descriptor when a process exits, however it exits.

`tick()` (`code/P-01-intake.md` §3 step 1) is the caller: it acquires the lock
first, keeps the returned handle referenced for the rest of the call so the
lock stays held, and treats a `BlockingIOError`/`OSError` with `errno` in
`{EACCES, EAGAIN}` as "sweep already running" rather than a fault.
"""

from __future__ import annotations

import fcntl
from pathlib import Path
from typing import IO

__all__ = ["LOCK_FILENAME", "acquire"]

#: Relative to the state directory (`container.md` §5's `lock` row).
LOCK_FILENAME = "lock"


def acquire(state_dir: Path) -> IO[bytes]:
    """Take the exclusive, non-blocking sweep lock at `<state_dir>/lock`.

    Returns the open file handle on success; the caller MUST keep a reference
    to it for as long as the lock must stay held — there is no separate
    release function, because the kernel releases the lock the moment every
    reference to this file descriptor is gone, deliberately including an
    abnormal process exit that never runs a `finally` block.

    Raises `BlockingIOError`/`OSError` with `errno` in `{EACCES, EAGAIN}` when
    another process already holds the lock. This function does not retry and
    does not distinguish that outcome from a fault; the caller decides what a
    contended lock means.
    """
    state_dir.mkdir(parents=True, exist_ok=True)
    handle = open(state_dir / LOCK_FILENAME, "ab")
    try:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        handle.close()
        raise
    return handle
