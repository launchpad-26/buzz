"""The one process-execution routine used for every harness command — §1, §3.3.

Every harness a review attempt runs, and every conformance run that gates an
operator-declared command, comes through `invoke()`. One routine means one environment
policy, one timeout policy and one measured clock, so none of the three can be right in
one call path and wrong in another.

**The environment is an allow-list, never a copy.** §3.3: "RQA supplies only the minimal
environment plus the bundle, protocol and verdict paths; it supplies no RQA/GitHub
credentials." `_ENV_ALLOWLIST` is built *up* from names this process happens to have,
so `GITHUB_TOKEN`, `GH_TOKEN`, `BUZZ_PRIVATE_KEY` and every credential nobody has
thought of yet are absent by construction rather than by a deny-list somebody has to
keep current. `rqa/supply/probe.py` reached the same conclusion for the liveness probe
and named the same five variables; this is deliberately the same list.

**A timeout kills the process group, not the child.** A harness that spawns its own
model client and is killed alone leaves the grandchild holding the bundle, the output
path and a network connection. `start_new_session=True` gives the child its own process
group and `killpg` takes the whole tree down. `ATTEMPT_TIMEOUT_SECONDS = 1800` is §3.3's
number, verbatim.

**The clock is RQA's.** `started_at` and `ended_at` are read here, from
`datetime.now(timezone.utc)`, around the actual `Popen`. They are the timestamps §6's
`attestation` entry carries, and RQA-NFR-022 forbids any element of the provenance
record to be writable by model output: a harness that reports its own timings reports
them into the verdict, where they are recorded as self-reported and never merged with
these (U-VERDICT-11, kept).

**Failure to spawn is a value, not an exception.** `OSError` from `Popen` is a fact
about a route — §3.3's table classifies it `CANDIDATE_TERMINAL` — so it is captured in
the returned `Execution` rather than raised. The exception object is dropped rather than
stored: its message quotes an argv built from an operator-declared `command`, and there
is no need to carry that anywhere near a record payload.

**Standard streams go to the job-local slot, never into the record.** A harness may echo
pull-request bytes to stdout, so `stdout.log`/`stderr.log` live under
`jobs/<job>/harness/<NN>/` (§5, which names them) and nothing in this package copies a
byte of them into a record payload, a log line, or an exception message.

**E-24.** `CONTRACTS.md` §9 annotates `HarnessProber` as "implemented in P-06 over the
same `invoke()` as E-19", but P-05 landed `SubprocessHarnessProber` in
`rqa/supply/probe.py` with its own spawn, its own identical environment allow-list and
its own `PROBE_TIMEOUT_SECONDS`. E-24's consumer is P-05 and it is closed there. This
package does not add a second prober: a duplicate would be extra public surface P-06 §1
does not list, and two probers is worse than one in the wrong package. The divergence is
recorded in this lane's handoff rather than repaired unilaterally.
"""

from __future__ import annotations

import hashlib
import os
import signal
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

__all__ = [
    "ATTEMPT_TIMEOUT_SECONDS",
    "CONFORMANCE_TIMEOUT_SECONDS",
    "Execution",
    "SPAWN_FAILURE_EXIT_CODE",
    "TIMEOUT_EXIT_CODE",
    "argv_hash",
    "invoke",
    "utcnow",
]

#: §3.3, verbatim.
ATTEMPT_TIMEOUT_SECONDS: float = 1800
#: The §3.2 step 2 gate runs two invocations against a command that has never been
#: trusted with anything, on a bundle that holds no pull-request bytes. It is a
#: liveness-plus-behaviour check, so it uses the probe's bound rather than a full
#: review's: an unresponsive command should cost the ladder five minutes, not an hour.
CONFORMANCE_TIMEOUT_SECONDS: float = 300

#: `Attestation.exit_code` is an `int`, so the two non-exits need reserved values. Both
#: are outside the 0-255 a real exit can take and outside the negatives a signal death
#: reports, so neither can collide with an observed code.
TIMEOUT_EXIT_CODE = -1000
SPAWN_FAILURE_EXIT_CODE = -1001

#: The child's whole environment, drawn from these names only when this process has them.
#: Every credential is absent because it was never added, not because it was removed.
_ENV_ALLOWLIST = ("PATH", "HOME", "LANG", "LC_ALL", "TMPDIR")


def utcnow() -> datetime:
    """RQA's own clock: an aware UTC timestamp. The only time source in this package."""
    return datetime.now(timezone.utc)


def argv_hash(argv: tuple[str, ...]) -> str:
    """Stable digest of an exact argv — the cache key half of §3.2 step 2's
    `(argv_hash, protocol_hash)`, and the argv field of a conformance `attestation`.

    NUL-joined because NUL cannot occur in an argv member, so no two distinct argvs can
    render to the same text.
    """
    return hashlib.sha256("\x00".join(argv).encode("utf-8")).hexdigest()


def _child_env() -> dict[str, str]:
    return {name: os.environ[name] for name in _ENV_ALLOWLIST if name in os.environ}


@dataclass(frozen=True)
class Execution:
    """What RQA measured about one harness process. Every field is RQA's observation."""

    argv: tuple[str, ...]
    started_at: datetime
    ended_at: datetime
    exit_code: int
    timed_out: bool
    spawn_failed: bool


def _terminate_group(process: subprocess.Popen[bytes]) -> None:
    """Kill the child's whole process group; fall back to the child on a platform or a
    race where the group is already gone."""
    try:
        os.killpg(os.getpgid(process.pid), signal.SIGKILL)
    except (OSError, PermissionError):
        try:
            process.kill()
        except OSError:
            pass


def invoke(*, argv: tuple[str, ...], cwd: Path, stdout_path: Path, stderr_path: Path, timeout: float) -> Execution:
    """Run one harness command to completion, a timeout, or a failure to start.

    Never raises for anything the harness does: every outcome §3.3's table classifies is
    a field of the returned `Execution`.
    """
    started_at = utcnow()
    try:
        process = subprocess.Popen(  # noqa: S603 - argv is a tuple, never a shell string
            list(argv),
            cwd=str(cwd),
            env=_child_env(),
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            start_new_session=True,
        )
    except OSError:
        # The exception is deliberately not carried: its text quotes an argv that may be
        # operator-declared, and `CANDIDATE_TERMINAL` is the whole of what the loop needs.
        return Execution(
            argv=argv,
            started_at=started_at,
            ended_at=utcnow(),
            exit_code=SPAWN_FAILURE_EXIT_CODE,
            timed_out=False,
            spawn_failed=True,
        )

    timed_out = False
    try:
        stdout, stderr = process.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        timed_out = True
        _terminate_group(process)
        stdout, stderr = process.communicate()
    ended_at = utcnow()

    stdout_path.write_bytes(stdout or b"")
    stderr_path.write_bytes(stderr or b"")

    return Execution(
        argv=argv,
        started_at=started_at,
        ended_at=ended_at,
        exit_code=TIMEOUT_EXIT_CODE if timed_out else int(process.returncode),
        timed_out=timed_out,
        spawn_failed=False,
    )
