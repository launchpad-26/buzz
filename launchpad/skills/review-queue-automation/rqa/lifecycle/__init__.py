"""`rqa.lifecycle` — P-02, `architecture/code/P-02-lifecycle.md`.

The only part that changes a job's state. It owns §2's closed transition table and the
mapping to `rqa status`'s six dispositions, contains every persistence failure into a safe
stop, and drives one job through flow steps 3-13 by calling its neighbours — never
deciding what their answers mean beyond the transition those answers license.

No other module in RQA imports from `rqa.lifecycle` except through this file. Inside
the package, neighbour decisions are reached through the Contract's shared types
(`rqa.contracts`) and injected clients. The one other part imported here is
`rqa.record`, and only through its front door: `append_trace` in `admit.py`,
`rest.py` and `steps.py` for P-12's non-authoritative milestones, and
`SQLiteRecordReader` in `steps.py`, constructed over the caller-owned connection for
E-05. Neither is a neighbour decision call. Every exchanged value type —
`Job`, `Snapshot`, `Facts`, `Grant`, `Deny`, `Judgement`, `GithubUnavailable`, the lot —
is imported from there, never redefined here. `JobStatus` is re-exported below for the
same reason `rqa.record` re-exports `Entry`: a consumer gets the status set and the table
that indexes it from one module. An import is not a declaration.

`LifecycleDeps` is part of §1's re-export list because P-01 constructs it through this
front door (`code/P-01-intake.md` §3 step 5). Its neighbour Protocols are bound here for
P-01's annotations but remain implementation vocabulary rather than wildcard exports.

§1 lists nine modules and fifteen re-exports, and this is the finished package:
`steps.py`, `rest.py` and `resume.py` — the step-3-to-13 cascade, the resting-status
successor/lease check, and E-11's reverse edge — landed with `resume`, completing the
list. `__all__` below is exactly those fifteen names.
"""

from __future__ import annotations

from rqa.lifecycle.admit import admit
from rqa.lifecycle.resume import resume
from rqa.lifecycle.deps import (
    AuthorityClient,
    EscalationClient,
    HarnessClient,
    JudgementClient,
    LifecycleDeps,
    PolicyClient,
    RemediationClient,
    ReuseClient,
    SupplyClient,
)
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
    "LifecycleDeps",
]
