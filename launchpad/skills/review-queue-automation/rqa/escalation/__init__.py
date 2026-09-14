"""`rqa.escalation` — P-11, `code/P-11-escalation.md`.

The human seam: raise a durable, named escalation naming one of five closed causes with
a specific question, index what is open, and record a human's decision — actor, basis,
and what it substantiates — as a fact P-02 resumes from. Never pushes a notification.

No other module in RQA imports from `rqa.escalation` except through this file (§1), and
no module in `rqa.escalation` imports another part's package: the import graph is
`rqa.contracts` (the shared types) and `rqa.record` (to append the `escalation` and
`decision` entries), and nothing else. `Job` arrives as an argument to `raise_()`; the
read of a job's current head/snapshot and the call into P-02 are Protocols declared in
`decide.py` that the caller satisfies at wiring time — this part never imports
`rqa.intake` or P-02's lifecycle implementation, and never reads or writes a job's
status column; only P-02 changes a job's state.

`__all__` is §1's re-export list exactly.
"""

from __future__ import annotations

from rqa.contracts import (
    Decision,
    Escalation,
    EscalationCause,
    EscalationRefusalReason,
    EscalationRefused,
)

from rqa.escalation.decide import decide
from rqa.escalation.escalate import EscalationError, pending, raise_

__all__ = [
    "raise_",
    "pending",
    "decide",
    "EscalationCause",
    "Escalation",
    "Decision",
    "EscalationRefused",
    "EscalationRefusalReason",
    "EscalationError",
]
