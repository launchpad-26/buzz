#!/usr/bin/env python3
"""P-01 admission tests: fail closed, call E-03 with job=None, and never pin."""

from __future__ import annotations

import pathlib
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

import rqa.intake.admission as admission_module  # noqa: E402
from rqa.contracts import (  # noqa: E402
    ValidationError,
    ValidationErrorCode,
    ValidationFailure,
)
from rqa.intake.admission import _check_admission  # noqa: E402
from rqa.policy.store import SqliteSnapshotStore  # noqa: E402


class NeverRecord:
    def append(self, job_id, kind, payload):
        raise AssertionError("admission-time snapshot validation must not append")


class PinTrapStore:
    """A successful admission may activate policy, but cannot pin a job hash."""

    def __init__(self) -> None:
        self.pin_calls = []

    def set_snapshot_hash(self, *args, **kwargs):
        self.pin_calls.append((args, kwargs))
        raise AssertionError("admission attempted to pin a snapshot before a job existed")


def test_t1_validation_failure_is_joined_into_one_fail_closed_refusal() -> None:
    failure = ValidationFailure(
        repo="org/repo",
        errors=(
            ValidationError(ValidationErrorCode.MISSING_POLICY, "policy", "policy is required"),
            ValidationError(ValidationErrorCode.BAD_TYPE, "budget", "budget must be an object"),
        ),
    )
    calls = []
    original = admission_module.snapshot_for

    def fake_snapshot_for(*, repo, job, store, record):
        calls.append((repo, job, store, record))
        return failure

    store = PinTrapStore()
    record = NeverRecord()
    admission_module.snapshot_for = fake_snapshot_for
    try:
        refusal = _check_admission("org/repo", store=store, record=record)
    finally:
        admission_module.snapshot_for = original

    assert calls == [("org/repo", None, store, record)]
    assert refusal is not None
    assert refusal.repo == "org/repo"
    assert "missing_policy at policy: policy is required" in refusal.reason
    assert "bad_type at budget: budget must be an object" in refusal.reason
    assert refusal.onboarding_command == "rqa onboard org/repo"
    assert store.pin_calls == []


def test_successful_admission_discards_the_returned_snapshot_without_pinning() -> None:
    sentinel_snapshot = object()
    calls = []
    original = admission_module.snapshot_for

    def fake_snapshot_for(*, repo, job, store, record):
        calls.append((repo, job, store, record))
        return sentinel_snapshot

    store = PinTrapStore()
    record = NeverRecord()
    admission_module.snapshot_for = fake_snapshot_for
    try:
        refusal = _check_admission("org/repo", store=store, record=record)
    finally:
        admission_module.snapshot_for = original

    assert refusal is None
    assert calls == [("org/repo", None, store, record)]
    assert store.pin_calls == []


def test_real_policy_refuses_a_genuinely_unconfigured_repository() -> None:
    """Real E-03 integration: no config file is a ValidationFailure, not admission."""
    with tempfile.TemporaryDirectory() as directory:
        root = pathlib.Path(directory)
        repo = root / "unconfigured-repository"
        repo.mkdir()
        store = SqliteSnapshotStore(root / "state")

        refusal = _check_admission(str(repo), store=store, record=NeverRecord())

        assert refusal is not None
        assert refusal.repo == str(repo)
        assert "unreadable" in refusal.reason
        assert ".rqa/config.json" in refusal.reason
        assert not (root / "state" / "snapshots").exists()
