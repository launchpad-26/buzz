"""Control for #575: the `test_*.py` suites beside this file must actually run in CI.

Seven suites live in this directory and every one of them passes, but until this control
existed **nothing ran them**. `launchpad-review-agent-controls.yml`'s only step is
`python3 run_controls.py`, and `CONTROLS` listed thirteen entries, none a `test_*.py`
runner — `suite.py` is #120's 35-case containment suite, not a discovery run. The one
workflow that does use `unittest discover` is scoped `-s launchpad/agents`.

Five of the suites say so in their own docstrings ("not wired into `run_controls.py`"),
and the escalation path dead-ended: #566's review recorded it against #270, #270's
"Out of scope" handed it to #118 STEP 10, and STEP 10 is one-control-per-done-criterion
over adjudication behaviour — it never runs `test_*.py`. A suite nothing runs is a
claim, not a check: it cannot fail, so it cannot protect anything.

One row in `CONTROLS` rather than a second workflow, per #270's own reasoning and
`launchpad/plans/2026-08-13-issue-118-adjudication.md:187` ("STEP 10 appends one row; no
second workflow is added").

Two steps, deliberately separate. Counting answers "is there anything to run"; the run
answers "does it pass". `unittest discover` exits 0 on an empty suite, which in a CI
summary is indistinguishable from a pass — the exact shape of the gap this control
closes, so an empty discovery has to be a failure here rather than a silent success.
"""

from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).parent
PATTERN = "test_*.py"

failures: list[str] = []


def check(ok: bool, label: str) -> None:
    print(f"{'PASS' if ok else 'FAIL'}  {label}")
    if not ok:
        failures.append(label)


# --- is there anything to run? ---------------------------------------------
# COUNTS CASES, NOT FILES. A guard that counted files could be satisfied by a
# filename: leave every test_*.py in place and rename each `test_*` method to
# `check_*`, and a file count reports seven suites while discovery collects zero
# cases and exits 0. That trap is documented in launchpad-agents-tests.yml, whose
# first version had it. A guard a filename can satisfy is not a guard.
#
# A module that fails to import counts as one case here — the loader substitutes a
# `_FailedTest` — so an ImportError passes this step and then fails the run below.
# That split is correct: it distinguishes "nothing to run" from "does not pass".

discovered = unittest.defaultTestLoader.discover(
    str(HERE), pattern=PATTERN, top_level_dir=str(HERE)
)
count = discovered.countTestCases()
check(count > 0, f"discovery over {PATTERN} collects at least one test case (got {count})")

# --- does it pass? ---------------------------------------------------------
# A subprocess rather than an in-process TextTestRunner, for two reasons: the suites
# patch process-global state (`subprocess.run`, `os.environ`, `urllib.request.urlopen`),
# and this is the command a contributor runs by hand, so a failure here reproduces
# verbatim rather than only inside this harness.

if count > 0:
    proc = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", str(HERE),
         "-t", str(HERE), "-p", PATTERN],
        capture_output=True,
        text=True,
    )
    check(proc.returncode == 0, f"all {count} test cases pass (exit {proc.returncode})")
    if proc.returncode != 0:
        # unittest writes results to stderr; stdout carries any print from the tests.
        print(proc.stdout[-2000:])
        print(proc.stderr[-4000:])

print(f"\n{len(failures)} failure(s)")
sys.exit(1 if failures else 0)
