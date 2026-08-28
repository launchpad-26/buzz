#!/usr/bin/env python3
"""Regression tests for stale-head detection.

`head_matches` was tautological: `_load_pr_facts` fell back to the job's own head
when building `PRFacts.head_sha`, so the gate compared the reviewed head with
itself and could never fail. A PR that advanced after review still passed, which
allowed an "eligible" approval decision to be persisted against a stale revision.

`PRFacts.head_sha` must therefore be the OBSERVED current head, and an unknown
observed head must fail the gate closed.
"""

from __future__ import annotations

import json
import pathlib
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scripts"))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import dispatcher  # noqa: E402
from approval_evaluate import compute_gates  # noqa: E402
from common import State  # noqa: E402
from test_dispatch_flow import _config, seed_evidence, seed_job  # noqa: E402

REVIEWED = "REVIEWED_SHA"


def _facts_with_observed_head(observed: str | None, *, drop_context: bool = False):
    """Seed a job reviewed at REVIEWED, then set the observed head separately."""
    state = State({"state_dir": tempfile.mkdtemp()})
    try:
        cfg = _config("live")
        jid = seed_job(state, number=400, head=REVIEWED)
        seed_evidence(state, jid)

        if drop_context:
            path = state.job_dir(jid) / "evidence.json"
            evidence = json.loads(path.read_text(encoding="utf-8"))
            evidence["context"].pop("head", None)
            path.write_text(json.dumps(evidence), encoding="utf-8")

        if observed is not None:
            row = state.db.execute(
                "SELECT payload FROM prs WHERE repo='o/r' AND number=400"
            ).fetchone()
            payload = json.loads(row["payload"])
            if observed:
                payload["head"] = {"sha": observed}
            else:
                payload.pop("head", None)
            state.db.execute(
                "UPDATE prs SET payload=? WHERE repo='o/r' AND number=400",
                (json.dumps(payload),),
            )
            state.db.commit()

        facts = dispatcher._load_pr_facts(
            state, {"repo": "o/r", "number": 400, "job_id": jid}, REVIEWED, cfg
        )
        gates = compute_gates(cfg, facts, [], [], 0, "low", "me", head_sha=REVIEWED)
        return facts, gates
    finally:
        state.close()


def test_unchanged_head_passes() -> None:
    facts, gates = _facts_with_observed_head(None)
    assert facts.head_sha == REVIEWED
    assert gates.head_matches is True


def test_advanced_head_fails_the_gate() -> None:
    """The regression: this previously passed and could never fail."""
    facts, gates = _facts_with_observed_head("NEW_SHA_AFTER_PUSH")
    assert facts.head_sha == "NEW_SHA_AFTER_PUSH"
    assert gates.head_matches is False, (
        "a PR that advanced after review must not satisfy head_matches"
    )


def test_observed_head_falls_back_to_evidence_context() -> None:
    """With no payload head, the evidence context's head is the observed value."""
    facts, gates = _facts_with_observed_head("")
    # the fixture's evidence context records head 'abc', which is not the reviewed sha
    assert facts.head_sha == "abc"
    assert gates.head_matches is False


def test_unknown_observed_head_fails_closed() -> None:
    facts, gates = _facts_with_observed_head("", drop_context=True)
    assert facts.head_sha == ""
    assert gates.head_matches is False, "an unprovable head must fail closed"


def test_head_gate_blocks_the_live_approval_decision() -> None:
    """A stale head must prevent an eligible decision being persisted at all."""
    from approval_evaluate import evaluate

    state = State({"state_dir": tempfile.mkdtemp()})
    try:
        cfg = _config("live")
        jid = seed_job(state, number=401, head=REVIEWED)
        seed_evidence(state, jid)
        row = state.db.execute(
            "SELECT payload FROM prs WHERE repo='o/r' AND number=401"
        ).fetchone()
        payload = json.loads(row["payload"])
        payload["head"] = {"sha": "MOVED"}
        state.db.execute(
            "UPDATE prs SET payload=? WHERE repo='o/r' AND number=401",
            (json.dumps(payload),),
        )
        state.db.commit()

        facts = dispatcher._load_pr_facts(
            state, {"repo": "o/r", "number": 401, "job_id": jid}, REVIEWED, cfg
        )
        clean = {"signal": "SUPPORTED", "recommendation": "clean", "findings": [],
                 "good": ["x"], "missing_evidence": [], "_schema_ok": True}
        result = evaluate(
            state, cfg, repo="o/r", number=401, head_sha=REVIEWED, pr=facts,
            verdicts=[dict(clean, model="opus", provider_family="anthropic"),
                      dict(clean, model="ds", provider_family="openrouter")],
            profile={"independence": "challenger"},
            reviewers=["opus", "ds"], assessments={}, login="me",
        )
        assert result.disposition == "human_escalation"
        assert "head_matches" in result.failed_gates
        assert state.db.execute("SELECT 1 FROM approval_decisions").fetchone() is None, (
            "no eligible decision may be persisted for a stale head"
        )
    finally:
        state.close()
