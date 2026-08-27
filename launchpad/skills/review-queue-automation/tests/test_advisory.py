#!/usr/bin/env python3
"""Tests for advisory.py — the default product of the pipeline.

Before this, advisory mode ran the panel, reached a decision, and posted NOTHING:
`execute_comment_review` had no caller. So these tests assert the advisory review
is actually produced, is gated by comment authority, keeps corroborated findings
separate from unconfirmed ones, and cannot escalate into an approval.
"""

from __future__ import annotations

import pathlib
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scripts"))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import advisory  # noqa: E402
import dispatcher  # noqa: E402
from common import State  # noqa: E402
from test_dispatch_flow import (  # noqa: E402
    _clean_verdict,
    _config,
    fake_panel,
    patch_dispatcher,
    restore_dispatcher,
    seed_evidence,
    seed_job,
    seed_verdicts,
)

VERIFIED = {
    "severity": "blocker", "title": "expired session refreshed without recheck",
    "location": "src/auth/session.ts:12", "evidence": "isExpired returns refresh(s)",
    "primary_source": "src/auth/session.ts", "basis": "two_provider_families",
}
UNVERIFIED = {
    "severity": "blocker", "title": "possible unbounded retry",
    "location": "src/auth/retry.ts:40", "evidence": "no backoff observed",
    "primary_source": "src/auth/retry.ts", "basis": "single_family_uncorroborated",
}


def _body(**over) -> str:
    kwargs = dict(
        repo="o/r", number=1, head_sha="abcdef123456", disposition="disabled",
        verified=[], unverified=[],
    )
    kwargs.update(over)
    return advisory.build_body(**kwargs)


# -- body content --------------------------------------------------------
def test_body_states_it_is_advisory() -> None:
    body = _body()
    assert "approves nothing and requests no changes" in body


def test_body_reports_the_reviewed_head() -> None:
    assert "abcdef123456"[:12] in _body()


def test_corroborated_and_unconfirmed_are_separate_sections() -> None:
    """Presenting an uncorroborated finding as a defect loses a reader's trust."""
    body = _body(verified=[VERIFIED], unverified=[UNVERIFIED])
    assert "### Corroborated findings (1)" in body
    assert "### Unconfirmed observations (1)" in body
    verified_at = body.index("Corroborated findings")
    unverified_at = body.index("Unconfirmed observations")
    assert verified_at < unverified_at
    # the unconfirmed section carries an explicit caveat
    assert "leads, not defects" in body


def test_no_findings_says_so_explicitly() -> None:
    body = _body()
    assert "No finding met the corroboration bar" in body


def test_corroboration_basis_is_explained() -> None:
    two = _body(verified=[VERIFIED])
    assert "two provider families" in two

    checked = dict(VERIFIED, basis="check_failure_corroborated", citation="ci-tests")
    assert "cited failing check `ci-tests`" in _body(verified=[checked])


def test_unenforced_effort_is_disclosed() -> None:
    """A reader must be able to tell the route could not apply the effort."""
    body = _body(routes=[
        {"runner": "claude", "selector": "opus", "effort": "xhigh", "effort_enforced": False},
    ])
    assert "not enforceable by this transport" in body


def test_assurance_and_gates_are_disclosed() -> None:
    body = _body(
        assurance={"required_assurance": "low", "achieved_assurance": 0.61,
                    "assurance_met": True},
        failed_gates=["approve_authority_live"],
    )
    assert "required low" in body
    assert "achieved 0.61" in body
    assert "approve_authority_live" in body


def test_body_is_bounded() -> None:
    many = [dict(VERIFIED, location=f"src/f{i}.ts:{i}") for i in range(200)]
    body = _body(verified=many)
    assert len(body) <= advisory.MAX_BODY
    assert "more" in body, "a truncated list must say it was truncated"


def test_body_is_deterministic() -> None:
    kwargs = dict(verified=[VERIFIED], unverified=[UNVERIFIED])
    assert _body(**kwargs) == _body(**kwargs)


# -- authority gating ----------------------------------------------------
def _post(comment_authority: str, *, node_id: str = "PR_node", execute=None) -> dict:
    cfg = {"authority": {"comment": comment_authority}, "repository": {"slug": "o/r"}}
    return advisory.post_advisory(
        None, local_cfg=cfg, repo="o/r", number=1, job_id="j1",
        pr_node_id=node_id, body="body", _execute=execute or (lambda *a, **k: {}),
    )


def test_comment_requires_live_authority() -> None:
    for mode in ("disabled", "shadow", "human_escalation"):
        record = _post(mode)
        assert record["posted"] is False
        assert mode in record["reason"]


def test_live_authority_posts() -> None:
    calls: list = []

    def execute(state, variables, job, **kwargs):
        calls.append((variables, kwargs))
        return {}

    record = _post("live", execute=execute)
    assert record["posted"] is True
    assert len(calls) == 1
    variables, _kwargs = calls[0]
    assert variables["pullRequestId"] == "PR_node"


def test_missing_node_id_withholds() -> None:
    record = _post("live", node_id="")
    assert record["posted"] is False
    assert "node_id" in record["reason"]


def test_mutation_failure_is_reported_not_raised() -> None:
    def boom(state, variables, job, **kwargs):
        raise RuntimeError("graphql 500")

    record = _post("live", execute=boom)
    assert record["posted"] is False
    assert "graphql 500" in record["reason"]


# -- dispatch integration -----------------------------------------------
def _dispatch(comment_authority: str, number: int, verdicts=None) -> dict:
    state = State({"state_dir": tempfile.mkdtemp()})
    saved = patch_dispatcher(run_panel=fake_panel("SUPPORTED"))
    captured: list = []
    original = advisory.post_advisory

    def fake_post(state_, **kwargs):
        captured.append(kwargs)
        live = comment_authority == "live"
        return {"posted": live, "mode": comment_authority,
                "reason": "" if live else f"comment authority is {comment_authority}"}

    advisory.post_advisory = fake_post
    try:
        cfg = _config("disabled")
        cfg["authority"] = {"comment": comment_authority}
        jid = seed_job(state, number=number, head=f"h{number}")
        seed_evidence(state, jid)
        seed_verdicts(state, jid, verdicts or [
            _clean_verdict("opus", "anthropic"), _clean_verdict("ds", "openrouter")])
        result = dispatcher.run_job(
            cfg, {"job_id": jid, "repo": "o/r", "number": number, "lane": "incoming_review"},
            state=state, claim_lease=False,
        )
        result["_captured"] = captured
        return result
    finally:
        advisory.post_advisory = original
        restore_dispatcher(saved)
        state.close()


def test_advisory_mode_reaches_a_completed_state() -> None:
    """The regression: advisory mode used to stop at advisory_action doing nothing."""
    result = _dispatch("live", 800)
    assert result["status"] == "completed_advisory"
    assert result["advisory"]["posted"] is True
    assert len(result["_captured"]) == 1


def test_advisory_withheld_is_visible_in_the_result() -> None:
    """A withheld comment must not look like a posted one."""
    result = _dispatch("disabled", 801)
    assert result["status"] == "completed_advisory"
    assert result["advisory"]["posted"] is False
    assert "disabled" in result["advisory"]["reason"]


def test_advisory_body_carries_the_findings() -> None:
    defect = {
        "signal": "DEFECTS_FOUND", "recommendation": "findings", "summary": "defect",
        "findings": [{"severity": "blocker", "title": "auth bypass",
                      "location": "src/auth/session.ts:12",
                      "evidence": "expired sessions refresh",
                      "primary_source": "src/auth/session.ts"}],
        "good": [], "missing_evidence": [],
    }
    result = _dispatch("live", 802, verdicts=[
        dict(defect, model="opus", provider_family="anthropic"),
        dict(defect, model="ds", provider_family="openrouter"),
    ])
    body = result["_captured"][0]["body"]
    assert "src/auth/session.ts:12" in body
    assert "Corroborated findings (1)" in body
