"""Per-repository fail-closed admission — P-01 §3 step 2a and E-03."""

from __future__ import annotations

from rqa.policy import ValidationFailure, snapshot_for
from rqa.policy.store import SnapshotStore
from rqa.record import RecordWriter
from rqa.intake.types import AdmissionRefusal

__all__: list[str] = []


def _check_admission(
    repo: str, *, store: SnapshotStore, record: RecordWriter
) -> AdmissionRefusal | None:
    """Return a refusal for invalid policy, otherwise discard the admission snapshot.

    Admission deliberately calls E-03 with ``job=None``. A successful ``Snapshot``
    proves only that this repository may be inventoried; no job exists to pin it to.
    """
    result = snapshot_for(repo=repo, job=None, store=store, record=record)
    if not isinstance(result, ValidationFailure):
        return None

    reason = "; ".join(
        f"{error.code.value} at {error.path or '<root>'}: {error.detail}"
        for error in result.errors
    )
    return AdmissionRefusal(
        repo=repo,
        reason=reason,
        onboarding_command=f"rqa onboard {repo}",
    )
