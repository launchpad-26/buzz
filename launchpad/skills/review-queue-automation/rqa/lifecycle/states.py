"""The closed transition table and the six-disposition mapping — `code/P-02-lifecycle.md` §2.

`JobStatus` is the shared type of `CONTRACTS.md` §1 and is **imported**, never redefined
(§2: "Every value P-02 exchanges … is imported from `CONTRACTS.md` and never redefined
here"). It is re-exported from this module and from the package so a consumer can reach
the status set and the table it indexes from one place.

**"Closed" is the load-bearing word.** §2: "a transition not in it does not happen". Every
edge the lifecycle may take is a member of `TRANSITIONS[from_state]`; anything else is a
programming error, never a policy outcome (`transition()` raises `IllegalTransitionError`,
`code/P-02-lifecycle.md` §8 T1). Both mappings are therefore exposed as read-only views:
a closed table that a caller could mutate at runtime would be closed only by convention,
and the one guard that keeps a refusal, a denial or an unavailability off the approved
path would be one assignment away from being disabled process-wide.

`MERGED` and `SUPERSEDED` map to the empty frozenset: they are terminal, and the empty set
is the table's own statement of that, not an absence.

`DISPOSITION` is total over every status `status()` (§3.4) can return. It has no
`SUPERSEDED` entry because §3.4 step 4 proves `status()` can never observe one: its job
lookup is keyed on the PR's *current* head, and a superseded job's head is by definition
not the current head.
"""

from __future__ import annotations

from collections.abc import Mapping
from enum import Enum
from types import MappingProxyType

from rqa.contracts import JobStatus
from rqa.lifecycle.errors import LifecycleError

__all__ = ["JobStatus", "TRANSITIONS", "Disposition", "DISPOSITION", "as_status"]


def as_status(value: object, *, what: str = "status") -> JobStatus:
    """A `JobStatus`, or a `LifecycleError` naming what was not one.

    `jobs.status` is a `TEXT` column and a `Job` can be reconstructed from one, so a row
    can carry a string outside the thirteen members. A plain `TRANSITIONS[...]` lookup on
    such a value raises `KeyError` — an unnamed branch in the one function that decides
    whether a state change is legal. This is that branch, named.
    """
    try:
        return JobStatus(value)
    except ValueError as exc:
        raise LifecycleError(f"{what} is not a JobStatus: {value!r}") from exc


#: §2's table, verbatim. `frozenset()` for `MERGED` and `SUPERSEDED` is terminality.
TRANSITIONS: Mapping[JobStatus, frozenset[JobStatus]] = MappingProxyType(
    {
        JobStatus.QUEUED: frozenset(
            {JobStatus.CLAIMED, JobStatus.ESCALATED, JobStatus.SUPERSEDED}
        ),
        JobStatus.CLAIMED: frozenset(
            {
                JobStatus.PLANNED,
                JobStatus.ESCALATED,
                JobStatus.STOPPED,
                JobStatus.SUPERSEDED,
            }
        ),
        JobStatus.PLANNED: frozenset(
            {
                JobStatus.REVIEWING,
                JobStatus.JUDGED,
                JobStatus.ESCALATED,
                JobStatus.STOPPED,
            }
        ),
        JobStatus.REVIEWING: frozenset(
            {JobStatus.JUDGED, JobStatus.ESCALATED, JobStatus.STOPPED}
        ),
        JobStatus.JUDGED: frozenset(
            {
                JobStatus.REMEDIATING,
                JobStatus.ESCALATED,
                JobStatus.SUBMITTING,
                JobStatus.STOPPED,
            }
        ),
        JobStatus.REMEDIATING: frozenset(
            {JobStatus.SUPERSEDED, JobStatus.ESCALATED, JobStatus.STOPPED}
        ),
        JobStatus.ESCALATED: frozenset(
            {
                JobStatus.JUDGED,
                JobStatus.APPROVED,
                JobStatus.CHANGES_REQUESTED,
                JobStatus.STOPPED,
                JobStatus.SUPERSEDED,
            }
        ),
        JobStatus.SUBMITTING: frozenset(
            {
                JobStatus.CHANGES_REQUESTED,
                JobStatus.APPROVED,
                JobStatus.ESCALATED,
                JobStatus.STOPPED,
            }
        ),
        JobStatus.CHANGES_REQUESTED: frozenset({JobStatus.SUPERSEDED}),
        JobStatus.APPROVED: frozenset({JobStatus.MERGED, JobStatus.SUPERSEDED}),
        JobStatus.MERGED: frozenset(),
        JobStatus.STOPPED: frozenset({JobStatus.CLAIMED, JobStatus.SUPERSEDED}),
        JobStatus.SUPERSEDED: frozenset(),
    }
)


class Disposition(str, Enum):
    """RQA-FR-016's six answers. The strings are the operator-facing vocabulary of
    `flow-review-lifecycle.md` and are not free text."""

    BEING_REVIEWED = "being reviewed"
    AWAITING_REMEDIATION = "awaiting remediation"
    AWAITING_HUMAN_JUDGEMENT = "awaiting human judgement"
    BLOCKED = "blocked"
    REVIEW_COMPLETE = "review-complete"
    UNABLE_TO_PROGRESS = "unable to progress"


#: §2's mapping, verbatim: total over every status `status()` can return.
DISPOSITION: Mapping[JobStatus, Disposition] = MappingProxyType(
    {
        JobStatus.QUEUED: Disposition.BEING_REVIEWED,
        JobStatus.CLAIMED: Disposition.BEING_REVIEWED,
        JobStatus.PLANNED: Disposition.BEING_REVIEWED,
        JobStatus.REVIEWING: Disposition.BEING_REVIEWED,
        JobStatus.JUDGED: Disposition.BEING_REVIEWED,
        JobStatus.SUBMITTING: Disposition.BEING_REVIEWED,
        JobStatus.REMEDIATING: Disposition.AWAITING_REMEDIATION,
        JobStatus.ESCALATED: Disposition.AWAITING_HUMAN_JUDGEMENT,
        JobStatus.CHANGES_REQUESTED: Disposition.BLOCKED,
        JobStatus.APPROVED: Disposition.REVIEW_COMPLETE,
        JobStatus.MERGED: Disposition.REVIEW_COMPLETE,
        JobStatus.STOPPED: Disposition.UNABLE_TO_PROGRESS,
    }
)
