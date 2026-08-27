#!/usr/bin/env python3
"""Tests that dispatch claims a review lease and always releases it.

The contract is "claim first, release on every exit path; release is not
optional" — but the dispatcher never touched the lease at all, so two concurrent
sweeps could review the same PR and post duplicate advisory comments.

Properties under test: the claim precedes any review work, a PR claimed by
someone else is skipped, and the release happens on success, on safe-stop, and on
an unexpected exception — without a release failure ever masking the outcome.
"""

from __future__ import annotations

import pathlib
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scripts"))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import dispatcher  # noqa: E402
from common import State, utcnow  # noqa: E402
from test_dispatch_flow import (  # noqa: E402
    _clean_verdict,
    _config,
    fake_approve,
    fake_panel,
    patch_approval,
    patch_dispatcher,
    restore_approval,
    restore_dispatcher,
    seed_evidence,
    seed_job,
    seed_verdicts,
)


class _Trace:
    """Records lease calls and can be told to fail either operation."""

    def __init__(self, *, claim_result=True, claim_raises=None, release_raises=None):
        self.claims: list = []
        self.releases: list = []
        self.claim_result = claim_result
        self.claim_raises = claim_raises
        self.release_raises = release_raises

    def claim(self, cfg, state, repo, number, job, login):
        self.claims.append((repo, number, job, login))
        if self.claim_raises:
            raise self.claim_raises
        return self.claim_result

    def release(self, cfg, state, repo, number, job, login):
        self.releases.append((repo, number, job, login))
        if self.release_raises:
            raise self.release_raises


def _run(trace: _Trace, *, number: int, panel=None, approve=(True, "approved", "approved")):
    state = State({"state_dir": tempfile.mkdtemp()})
    saved = patch_dispatcher(
        run_panel=panel or fake_panel("SUPPORTED"),
        _lease_claim=trace.claim,
        _lease_release=trace.release,
    )
    previous = patch_approval(fake_approve(*approve))
    try:
        cfg = _config("live")
        jid = seed_job(state, number=number, head=f"h{number}")
        seed_evidence(state, jid)
        seed_verdicts(state, jid, [_clean_verdict("opus", "anthropic"),
                                   _clean_verdict("ds", "openrouter")])
        result = dispatcher.run_job(
            cfg, {"job_id": jid, "repo": "o/r", "number": number, "lane": "incoming_review"},
            state=state,
        )
        return result, jid, state
    finally:
        restore_approval(previous)
        restore_dispatcher(saved)


# -- claim ---------------------------------------------------------------
def test_lease_is_claimed_before_review() -> None:
    trace = _Trace()
    result, jid, state = _run(trace, number=700)
    try:
        assert len(trace.claims) == 1
        repo, number, job, login = trace.claims[0]
        assert (repo, number, job) == ("o/r", 700, jid)
        assert login == "tucktuck101"
        assert result["status"] == "completed_auto_approved"
    finally:
        state.close()


def test_pr_claimed_by_another_reviewer_is_skipped() -> None:
    """A PR someone else holds is not ours to review."""
    trace = _Trace(claim_result=False)
    result, _jid, state = _run(trace, number=701)
    try:
        assert result["status"] == "gated"
        assert "claimed by another reviewer" in result["reason"]
        assert trace.releases == [], "we never held it, so we must not release it"
    finally:
        state.close()


def test_claim_failure_gates_without_reviewing() -> None:
    trace = _Trace(claim_raises=RuntimeError("assignee mutation rejected"))
    result, _jid, state = _run(trace, number=702)
    try:
        assert result["status"] == "gated"
        assert "could not claim" in result["reason"]
        assert trace.releases == []
    finally:
        state.close()


def test_locally_held_lease_by_another_job_is_respected() -> None:
    """A local lease row for a different job blocks dispatch without a REST call."""
    state = State({"state_dir": tempfile.mkdtemp()})
    trace = _Trace()
    saved = patch_dispatcher(run_panel=fake_panel("SUPPORTED"),
                            _lease_claim=trace.claim, _lease_release=trace.release)
    try:
        cfg = _config("live")
        jid = seed_job(state, number=703, head="h703")
        seed_evidence(state, jid)
        # `leases.job_id` references `jobs(id)`, so the rival holder must be a real
        # job. It is inserted directly: `seed_job` would also write `prs`, which is
        # keyed on (repo, number) and already holds this PR.
        other = "o-r-703-incoming_review-earlier"
        now = utcnow()
        state.db.execute(
            "INSERT INTO jobs(id,repo,number,head_sha,lane,status,artifact_dir,"
            "created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?)",
            (other, "o/r", 703, "h703-earlier", "incoming_review", "detected",
             str(state.job_dir(other)), now, now),
        )
        state.db.execute(
            "INSERT INTO leases(repo,number,job_id,claimed_at) VALUES(?,?,?,?)",
            ("o/r", 703, other, now),
        )
        state.db.commit()

        result = dispatcher.run_job(
            cfg, {"job_id": jid, "repo": "o/r", "number": 703, "lane": "incoming_review"},
            state=state,
        )
        assert result["status"] == "gated"
        assert f"already held by job {other}" in result["reason"]
    finally:
        restore_dispatcher(saved)
        state.close()


def test_claim_can_be_disabled_for_offline_runs() -> None:
    state = State({"state_dir": tempfile.mkdtemp()})
    trace = _Trace()
    saved = patch_dispatcher(run_panel=fake_panel("SUPPORTED"),
                            _lease_claim=trace.claim, _lease_release=trace.release)
    previous = patch_approval(fake_approve(True, "approved"))
    try:
        cfg = _config("live")
        jid = seed_job(state, number=704, head="h704")
        seed_evidence(state, jid)
        seed_verdicts(state, jid, [_clean_verdict("opus", "anthropic"),
                                   _clean_verdict("ds", "openrouter")])
        dispatcher.run_job(
            cfg, {"job_id": jid, "repo": "o/r", "number": 704, "lane": "incoming_review"},
            state=state, claim_lease=False,
        )
        assert trace.claims == []
        assert trace.releases == []
    finally:
        restore_approval(previous)
        restore_dispatcher(saved)
        state.close()


# -- release -------------------------------------------------------------
def test_lease_is_released_after_success() -> None:
    trace = _Trace()
    _result, jid, state = _run(trace, number=710)
    try:
        assert len(trace.releases) == 1
        assert trace.releases[0][2] == jid
    finally:
        state.close()


def test_lease_is_released_after_a_degraded_outcome() -> None:
    """A partial panel still terminates, so the lease must still come back."""
    trace = _Trace()
    _result, _jid, state = _run(trace, number=711,
                                panel=fake_panel("SUPPORTED", complete=False))
    try:
        assert len(trace.releases) == 1
    finally:
        state.close()


def test_lease_is_released_when_the_mutation_is_uncertain() -> None:
    trace = _Trace()
    result, _jid, state = _run(trace, number=712,
                               approve=(False, "uncertain", "cannot confirm"))
    try:
        assert result["status"] == "safe_stop"
        assert len(trace.releases) == 1, "safe-stop must still release the lease"
    finally:
        state.close()


def test_lease_is_released_when_the_panel_raises() -> None:
    """An unexpected exception must not leave the queue blocked forever."""
    def exploding_panel(cfg, state, repo, number, lane, job_id, profile, logger=None):
        raise RuntimeError("panel exploded")

    trace = _Trace()
    state = State({"state_dir": tempfile.mkdtemp()})
    saved = patch_dispatcher(run_panel=exploding_panel,
                            _lease_claim=trace.claim, _lease_release=trace.release)
    try:
        cfg = _config("live")
        jid = seed_job(state, number=713, head="h713")
        seed_evidence(state, jid)
        try:
            dispatcher.run_job(
                cfg, {"job_id": jid, "repo": "o/r", "number": 713, "lane": "incoming_review"},
                state=state,
            )
        except RuntimeError:
            pass  # the exception is allowed to surface; the lease must not leak
        assert len(trace.releases) == 1, "the lease must be released even on a crash"
    finally:
        restore_dispatcher(saved)
        state.close()


def test_release_failure_does_not_mask_the_review_outcome() -> None:
    """A release problem is reported, never substituted for the result."""
    trace = _Trace(release_raises=RuntimeError("assignee still present"))
    result, _jid, state = _run(trace, number=714)
    try:
        assert result["status"] == "completed_auto_approved", result
        assert len(trace.releases) == 1
    finally:
        state.close()
