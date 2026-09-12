#!/usr/bin/env python3
"""`rqa.intake.lock` — `code/P-01-intake.md` §1, §3 step 1, §5 (U-DISPATCH-02).

Integration tests against a real `flock`, per §8's note that T3's lock half
is tested this way rather than with a fake. This file's `tick()`-return-value
half (`sweep_already_running`) is out of scope here — that is #2198's
`tick.py`, which does not exist on this branch (the wave-invariant rule: this
suite asserts only what this lane owns, never `tick()`'s absence)."""

from __future__ import annotations

import errno
import os
import pathlib
import subprocess
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from rqa.intake import lock  # noqa: E402

SKILL_ROOT = pathlib.Path(__file__).resolve().parent.parent
_CHILD_HOLDS_LOCK = """
import fcntl, pathlib, sys, time
path = pathlib.Path(sys.argv[1])
handle = open(path / "lock", "ab")
fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
print("locked", flush=True)
time.sleep(30)
"""


def test_a_second_exclusive_non_blocking_flock_on_the_same_lock_file_fails_immediately() -> None:
    with tempfile.TemporaryDirectory() as raw_dir:
        state_dir = pathlib.Path(raw_dir)
        held = lock.acquire(state_dir)
        try:
            try:
                lock.acquire(state_dir)
            except (BlockingIOError, OSError) as exc:
                assert exc.errno in (errno.EACCES, errno.EAGAIN), exc.errno
            else:
                raise AssertionError("a second acquire on a held lock must fail")
        finally:
            held.close()


def test_the_lock_is_reacquirable_once_the_holder_closes_its_handle() -> None:
    with tempfile.TemporaryDirectory() as raw_dir:
        state_dir = pathlib.Path(raw_dir)
        first = lock.acquire(state_dir)
        first.close()
        second = lock.acquire(state_dir)
        second.close()


def test_the_kernel_releases_the_lock_when_the_holding_process_exits_normally() -> None:
    with tempfile.TemporaryDirectory() as raw_dir:
        state_dir = pathlib.Path(raw_dir)
        env = dict(os.environ, PYTHONPATH=str(SKILL_ROOT))
        child = subprocess.Popen(
            [sys.executable, "-c", _CHILD_HOLDS_LOCK, str(state_dir)],
            stdout=subprocess.PIPE,
            env=env,
            text=True,
        )
        try:
            line = child.stdout.readline()
            assert line.strip() == "locked", repr(line)

            try:
                lock.acquire(state_dir)
            except (BlockingIOError, OSError) as exc:
                assert exc.errno in (errno.EACCES, errno.EAGAIN), exc.errno
            else:
                raise AssertionError("the holding subprocess is still alive")
        finally:
            child.terminate()
            child.wait(timeout=5)

        handle = lock.acquire(state_dir)
        handle.close()


def test_the_kernel_releases_the_lock_on_an_abnormal_process_exit() -> None:
    """A `SIGKILL`'d holder never runs a `finally`/`atexit` hook — the
    invariant this module exists for is that the kernel's own
    file-descriptor table releases the lock anyway."""
    with tempfile.TemporaryDirectory() as raw_dir:
        state_dir = pathlib.Path(raw_dir)
        env = dict(os.environ, PYTHONPATH=str(SKILL_ROOT))
        child = subprocess.Popen(
            [sys.executable, "-c", _CHILD_HOLDS_LOCK, str(state_dir)],
            stdout=subprocess.PIPE,
            env=env,
            text=True,
        )
        line = child.stdout.readline()
        assert line.strip() == "locked", repr(line)

        try:
            lock.acquire(state_dir)
        except (BlockingIOError, OSError) as exc:
            assert exc.errno in (errno.EACCES, errno.EAGAIN), exc.errno
        else:
            raise AssertionError("the holding subprocess is still alive")

        child.kill()  # SIGKILL: no finally, no atexit, no graceful shutdown
        child.wait(timeout=5)

        handle = lock.acquire(state_dir)
        handle.close()


def test_the_lock_file_lives_at_state_dir_lock_and_is_created_when_absent() -> None:
    with tempfile.TemporaryDirectory() as raw_dir:
        state_dir = pathlib.Path(raw_dir)
        assert not (state_dir / lock.LOCK_FILENAME).exists()
        handle = lock.acquire(state_dir)
        try:
            assert (state_dir / "lock").exists()
            assert lock.LOCK_FILENAME == "lock"
        finally:
            handle.close()
