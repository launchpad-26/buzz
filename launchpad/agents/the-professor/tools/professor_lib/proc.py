"""One place every subprocess call in this pack goes through, so that a missing
binary or a hung command produces a structured error instead of a raw traceback
(issue #2112).

Both halves of the tool layer shell out: `netcmd` runs `gh`, `localcmd` runs
`git`. Neither binary is guaranteed to exist on the machine running the pack --
`$PROFESSOR_PACK_ROOT` deliberately lets a session point at this pack from
anywhere, so "anywhere" includes a container with no `gh` installed. A bare
`subprocess.run` raises `FileNotFoundError` there, and `TimeoutExpired` on a slow
network, and either one escapes as a Python traceback -- which contradicts the
"structured error, never a raw traceback" convention this pack already enforces
for malformed UTF-8 and for its own pack-root guard.
"""

import subprocess


def run(cmd: list[str], timeout: int, what: str) -> tuple[subprocess.CompletedProcess | None, str | None]:
    """Run `cmd`, returning `(result, None)` on completion or `(None, message)`
    if it could not be run to completion.

    A non-zero exit status is *completion* -- it comes back as a real
    `CompletedProcess` for the caller to interpret, exactly as before. Only the
    cases where there is no exit status at all produce a message: the binary is
    absent, the call timed out, or the OS refused to start it.

    `what` names the calling operation for the message, e.g.
    `"path-exists-at('block/buzz', ...)"`. Callers pass their own already-
    formatted context rather than having this helper guess at it.
    """
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout), None
    except subprocess.TimeoutExpired:
        return None, (
            f"{what}: `{cmd[0]}` did not finish within {timeout}s and was killed. "
            "This is a timeout, not an answer -- do not treat it as a negative "
            "result."
        )
    except FileNotFoundError:
        return None, (
            f"{what}: `{cmd[0]}` is not installed or not on PATH. This pack shells "
            f"out to `{cmd[0]}`; install it, or run from an environment that has it."
        )
    except OSError as exc:
        return None, f"{what}: could not run `{cmd[0]}`: {exc}"
