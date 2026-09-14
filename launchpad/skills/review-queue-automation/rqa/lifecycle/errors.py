"""`LifecycleError` and its subclasses — `code/P-02-lifecycle.md` §2.

These are **programming errors**, never outcomes. `CONTRACTS.md`'s preamble draws the
line this package holds to: "policy, availability and budget outcomes are values,
programming errors are `*Error` exceptions". A `Deny`, a `GithubUnavailable`, a
`Refusal`, a `RemediationRefused` or an incomplete `PanelResult` is a value that licenses
a transition; none of them is ever raised from here, and nothing here is ever recorded as
a review outcome.

**Why these carry nothing.** Batches 2c and 3c both found credentials reachable from a
raised exception's `__context__` chain and from traceback frame locals. Every class here
is therefore a plain `Exception` with a message and no attributes: no `deps`, no client,
no `Job`, no payload. A caller that wants structure reads the record, which is the
authoritative account anyway. The one object in this part that could render a credential
by accident — `LifecycleDeps`, which holds nine live clients — suppresses its own field
repr for the same reason (`deps.py`).

Message discipline: a message names states, job ids, kinds and exception *types*. It
never interpolates a client, a `deps` bundle, a token, a header, or a GitHub response
body. `tests/test_rqa_lifecycle_surface.py` asserts the containment path holds to it.
"""

from __future__ import annotations

__all__ = [
    "LifecycleError",
    "StaleDecisionError",
    "IllegalTransitionError",
    "UnknownJobError",
]


class LifecycleError(Exception):
    """A lifecycle invariant was violated. Always a defect in the caller or in the
    stored state, never a reviewable outcome."""


class StaleDecisionError(LifecycleError):
    """A human decision arrived for a head or a pinned snapshot that has since moved
    (§3.3). The decision is not applied and no local alternative is substituted."""


class IllegalTransitionError(LifecycleError):
    """A transition absent from §2's closed `TRANSITIONS` table was attempted. Neither
    `jobs.status` nor `record_entries` changes (§8 T1)."""


class UnknownJobError(LifecycleError):
    """No `jobs` row exists for the job being transitioned or resumed (§3.3). A status
    write that matched no row would be a silent no-op; this is that branch, named."""
