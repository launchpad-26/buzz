"""`HarnessProber` — the E-24 liveness-probe adapter, `code/P-05-reviewer-supply.md` §4.

**A no-content probe.** The harness named by `route.harness` — or the operator's
`route.command`, when the pair carries one — is invoked with an **empty** bundle directory
carrying a single probe marker file in place of a bundle, and an output path nothing has
written to. No PR content, no protocol definition, nothing to review: the marker directory
is the entire input (§4, `RQA-NFR-027`). This module is the only place in `rqa.supply`
that spawns anything, and it is the only import §1 permits outside `rqa.record`.

**Judged on exactly two things.** The process exits `0`, and no `verdict.json` appears at
the output path. Both hold → `True`. A non-zero exit, a verdict written despite the marker
(a harness that does not honour E-19's published contract), a spawn failure, or the process
exceeding `timeout` → `False`. `route()` never inspects *why*: a slow, crashing or
non-compliant harness is unavailable exactly like an absent one.

**Why the real transport rather than a cheaper check** (U-POLICY-13, kept): a ping, a
credential check or an API-version query passes for a harness that then cannot produce a
schema-valid verdict, which is not the question a routing decision needs answered.

**It never raises for a transport reason**, and it never lets a failure escape carrying
context. A spawn error's message can name the argv it tried, and an environment a harness
was handed can hold a credential, so every failure path here ends in a plain `False` —
nothing is re-raised, chained, logged or returned that could carry either
(`RQA-NFR-025`).

**The environment is minimal by construction.** `_probe_env()` builds the child's
environment from a fixed allowlist, so no RQA or GitHub credential in this process reaches
a harness even when one is present — the same rule E-19 states for a real invocation.
"""

from __future__ import annotations

import os
import subprocess
import tempfile
from datetime import timedelta
from pathlib import Path
from typing import TYPE_CHECKING

from rqa.contracts import ProcessResult

if TYPE_CHECKING:  # annotation-only; nothing here is needed at runtime
    from rqa.contracts import ProcessRunner, Route

__all__ = [
    "PROBE_COOLDOWN",
    "PROBE_MARKER_NAME",
    "PROBE_TIMEOUT_SECONDS",
    "SubprocessProcessRunner",
    "SubprocessHarnessProber",
    "VERDICT_FILENAME",
    "probe_argv",
]

#: §4, verbatim: matches the real invocation's own timeout — a cold container or a cold
#: model can legitimately take this long to answer.
PROBE_TIMEOUT_SECONDS: float = 300
#: §4, verbatim: the `providers` cooldown set on a failed probe.
PROBE_COOLDOWN = timedelta(seconds=300)

#: The marker that stands in for a bundle. Its presence is the harness's instruction to
#: exit zero without writing a verdict (`P-06-harness-interface.md` §3.3's closing line).
PROBE_MARKER_NAME = "PROBE"
#: The one file whose presence fails a probe.
VERDICT_FILENAME = "verdict.json"

#: The child's whole environment, drawn from these names only when this process has them.
#: `GITHUB_TOKEN`, `GH_TOKEN` and every other credential are absent by construction.
_ENV_ALLOWLIST = ("PATH", "HOME", "LANG", "LC_ALL", "TMPDIR")


def probe_argv(candidate: Route, *, bundle: Path, verdict: Path) -> tuple[str, ...]:
    """The probe invocation for `candidate`: its command, then the bundle and output paths.

    A non-empty `Route.command` is the operator-declared argv (`RQA-FR-030`); otherwise the
    executable is `route.harness` itself. The two paths are appended in the order
    `P-06-harness-interface.md` §3.3 fixes for every adapter, minus the protocol
    instruction, which §4 states a probe does not carry.
    """
    base = tuple(candidate.command) if candidate.command else (candidate.harness,)
    return (*base, str(bundle), str(verdict))


def _probe_env() -> dict[str, str]:
    """The child's environment: the allowlist, and nothing else."""
    return {name: os.environ[name] for name in _ENV_ALLOWLIST if name in os.environ}


class SubprocessProcessRunner:
    """`ProcessRunner` (E-26's shape) over `subprocess.run`, with no inherited environment.

    A timeout, a non-zero exit and a spawn failure are all just outcomes to the caller
    above; this class reports the first two as a `ProcessResult` and lets the third and a
    timeout raise, because `SubprocessHarnessProber` turns every one of them into `False`.
    """

    def run(self, *, cwd: Path, argv: tuple[str, ...], timeout: float) -> ProcessResult:
        completed = subprocess.run(  # noqa: S603 - argv is operator-configured, never shell
            argv,
            cwd=str(cwd),
            capture_output=True,
            timeout=timeout,
            env=_probe_env(),
            check=False,
        )
        return ProcessResult(
            returncode=completed.returncode,
            stdout=completed.stdout or b"",
            stderr=completed.stderr or b"",
        )


class SubprocessHarnessProber:
    """The E-24 `HarnessProber`: one no-content invocation, one boolean.

    The runner is injected so a test never spawns a real harness; it defaults to the
    subprocess-backed one above, which is the only form a deployment uses.
    """

    def __init__(self, *, runner: ProcessRunner | None = None) -> None:
        self._runner = runner if runner is not None else SubprocessProcessRunner()

    def probe(self, route: Route, *, timeout: float) -> bool:
        with tempfile.TemporaryDirectory(prefix="rqa-probe-") as workspace:
            root = Path(workspace)
            bundle = root / "bundle"
            bundle.mkdir()
            # The bundle holds the marker and nothing else — no PR-derived byte exists here
            # to leave out, which is the point of probing before a bundle is ever built.
            (bundle / PROBE_MARKER_NAME).write_text("probe\n", encoding="utf-8")
            verdict = root / "out" / VERDICT_FILENAME
            verdict.parent.mkdir()
            try:
                result = self._runner.run(
                    cwd=root, argv=probe_argv(route, bundle=bundle, verdict=verdict), timeout=timeout
                )
            except Exception:  # noqa: BLE001 - see the module docstring: nothing escapes
                # A spawn error, a timeout or any other transport fault is "not alive".
                # The exception is dropped here rather than wrapped: its message and its
                # `__context__` can carry the argv and the environment it was handed.
                # `BaseException` is deliberately not caught: an interrupt is not a
                # liveness answer.
                return False
            return result.returncode == 0 and not verdict.exists()
