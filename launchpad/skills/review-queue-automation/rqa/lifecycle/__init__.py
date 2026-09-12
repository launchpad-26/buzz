"""`rqa.lifecycle` — P-02, `architecture/code/P-02-lifecycle.md`.

The only part that changes a job's state. It owns §2's closed transition table and the
mapping to `rqa status`'s six dispositions, contains every persistence failure into a safe
stop, and drives one job through flow steps 3-13 by calling its neighbours — never
deciding what their answers mean beyond the transition those answers license.

No other module in RQA imports from `rqa.lifecycle` except through this file, and no
module in `rqa.lifecycle` imports another part's package (§1): the import graph is the
Contract's shared types (`rqa.contracts`) and nothing else. Every exchanged value type —
`Job`, `Snapshot`, `Facts`, `Grant`, `Deny`, `Judgement`, `GithubUnavailable`, the lot —
is imported from there, never redefined here. `JobStatus` is re-exported below for the
same reason `rqa.record` re-exports `Entry`: a consumer gets the status set and the table
that indexes it from one module. An import is not a declaration.

`__all__` is §1's re-export list exactly. `LifecycleDeps` is bound here but deliberately
not in it: §1 does not list it, and P-01 constructs it as `from rqa.lifecycle import
LifecycleDeps, admit` (`code/P-01-intake.md` §3 step 5). Binding the name without
exporting it satisfies both without adding surface §1 does not specify.

§1 lists nine modules and fourteen re-exports, and this is the finished package:
`steps.py`, `rest.py` and `resume.py` — the step-3-to-13 cascade, the resting-status
successor/lease check, and E-11's reverse edge — landed with `resume`, completing the
list. `__all__` below is exactly those fourteen names.
"""

from __future__ import annotations

from rqa.lifecycle.admit import admit
from rqa.lifecycle.resume import resume
from rqa.lifecycle.deps import LifecycleDeps  # noqa: F401 - bound for P-01, not in §1's list
from rqa.lifecycle.errors import (
    IllegalTransitionError,
    LifecycleError,
    StaleDecisionError,
    UnknownJobError,
)
from rqa.lifecycle.states import DISPOSITION, TRANSITIONS, Disposition, JobStatus
from rqa.lifecycle.status import NotFound, StatusReport, status
from rqa.lifecycle.transition import transition

__all__ = [
    "admit",
    "resume",
    "status",
    "transition",
    "JobStatus",
    "TRANSITIONS",
    "Disposition",
    "DISPOSITION",
    "StatusReport",
    "NotFound",
    "StaleDecisionError",
    "LifecycleError",
    "IllegalTransitionError",
    "UnknownJobError",
]
