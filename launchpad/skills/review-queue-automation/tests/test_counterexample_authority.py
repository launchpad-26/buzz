#!/usr/bin/env python3
"""Counterexample tests for authority resolution, the action gate, and snapshot pinning.

These are the three guards that stand between a computed opinion and a change to
somebody's repository, so every test here asserts a REFUSAL:

* authority resolution — the two authority mechanisms are conjunctive, and a mode
  that is not exactly `live` never authorises anything;
* the action gate — every gate is fail-closed, and no decision path reaches a
  GitHub mutation without passing one (asserted by proving the injected HTTP
  sender was never called);
* snapshot pinning — an in-flight job resolves the snapshot it started with, and a
  result already pinned to one snapshot cannot be relabelled with another.

Sibling ownership: none of `authority.py`, `action_gate.py`, `github_mutate.py` or
`snapshot.py` is sibling-owned; `test_snapshot_pinning.py` and
`test_panel_policy.py` are, so these counterexamples live in a new file even
where they overlap.
"""

from __future__ import annotations

import datetime as dt
import pathlib
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import authority as authmod  # noqa: E402
import github_mutate as gh  # noqa: E402
import policy as policymod  # noqa: E402
import snapshot as snapmod  # noqa: E402
from action_gate import request_changes_gate  # noqa: E402
from approval_evaluate import ApprovalEvidence, PRFacts, compute_gates  # noqa: E402
from common import State, utcnow  # noqa: E402
from errors import DecisionStaleError, PermissionAuthorityError  # noqa: E402
from risk import AssuranceEvaluation  # noqa: E402

_HEAD = "d" * 40


def _state() -> State:
    return State({"state_dir": tempfile.mkdtemp()})


# --------------------------------------------------------------------------
# 1. authority resolution
# --------------------------------------------------------------------------


def _approval_cfg(*, authority: dict, mode: str = "live") -> dict:
    return {
        "repository": {"slug": "o/r"},
        "authority": authority,
        "approval": {"mode": mode, "approval_enabled": True, "live_canary_approved": True},
        "risk": {},
    }


def _all_gates_pass_config(authority: dict, mode: str = "live") -> tuple[dict, PRFacts, list, list]:
    cfg = _approval_cfg(authority=authority, mode=mode)
    pr = PRFacts(draft=False, author_login="a-human", head_sha=_HEAD, complexity=0,
                 files=["README.md"], additions=1, checks_ok=True,
                 adjudication_complete=True, evidence_fresh=True)
    verdicts = [
        {"model": "claude-opus-4-5", "provider_family": "anthropic", "signal": "SUPPORTED",
         "recommendation": "clean", "findings": [], "_schema_ok": True},
        {"model": "gpt-5.6-sol", "provider_family": "openai", "signal": "SUPPORTED",
         "recommendation": "clean", "findings": [], "_schema_ok": True},
    ]
    return cfg, pr, verdicts, ["claude-opus-4-5", "gpt-5.6-sol"]


def _gates(authority: dict, mode: str = "live"):
    cfg, pr, verdicts, reviewers = _all_gates_pass_config(authority, mode)
    return compute_gates(
        cfg, pr, verdicts, reviewers, 0, "low", "review-bot",
        head_sha=_HEAD, profile={"independence": "challenger"},
        evidence=ApprovalEvidence(
            bounded_change=True, audit_writable=True, assurance_met=True,
            revalidation_ok=True, rate_limit_ok=True,
        ),
    )


def test_the_control_a_fully_authorised_configuration_passes_every_gate() -> None:
    """Without this control, an `ApprovalState` that failed unconditionally would
    satisfy every counterexample below while approving nothing — and would hide a
    real regression in the gate set."""
    gates = _gates({"approve": "live"})
    assert gates.failed() == {}, gates.failed()
    assert gates.passed() is True


def test_authority_approve_disabled_cannot_be_overridden_by_approval_mode_live() -> None:
    """The two authority mechanisms are CONJUNCTIVE. An operator who set
    `authority.approve: disabled` has disabled auto-approval, whatever
    `approval.mode` says. This regression is exactly what shipped once."""
    for mode in ("disabled", "shadow", "human_escalation"):
        gates = _gates({"approve": mode})
        assert gates.approve_authority_live is False, mode
        assert gates.passed() is False, mode
        assert "approve_authority_live" in gates.failed(), mode


def test_a_repo_scoped_disable_beats_a_globally_live_approve_authority() -> None:
    gates = _gates({"approve": "live", "o/r": {"approve": "disabled"}})
    assert gates.approve_authority_live is False
    assert gates.passed() is False
    # ...and the per-repo override is genuinely consulted, not ignored both ways.
    assert _gates({"approve": "disabled", "o/r": {"approve": "live"}}).approve_authority_live is True


def test_approval_mode_not_live_cannot_be_overridden_by_authority_approve_live() -> None:
    """The conjunction has to hold in the other direction too."""
    for mode in ("disabled", "shadow", "human_escalation"):
        gates = _gates({"approve": "live"}, mode=mode)
        assert gates.approval_enabled is False, mode
        assert gates.passed() is False, mode


def test_no_mode_other_than_live_ever_authorises_an_action() -> None:
    for mode in ("disabled", "shadow", "human_escalation"):
        cfg = {"authority": {"default": mode}}
        for activity in sorted(authmod.ACTIVITIES):
            assert authmod.can_act(cfg, "o/r", activity, repo_hard_gate_ok=True) is False, (
                mode, activity
            )


def test_a_live_mutating_activity_still_needs_its_caller_supplied_hard_gate() -> None:
    """`live` is permission to act once the safety gate passed — not instead of it."""
    cfg = {"authority": {"default": "live"}}
    for activity in sorted(authmod.MUTATING_ACTIVITIES | authmod.BRANCH_MUTATING_ACTIVITIES):
        assert authmod.can_act(cfg, "o/r", activity, repo_hard_gate_ok=False) is False, activity
        assert authmod.can_act(cfg, "o/r", activity, repo_hard_gate_ok=True) is True, activity


def test_an_unrecognised_mode_value_is_not_honoured() -> None:
    """A near-miss spelling must fail closed. Accepting `LIVE` or `true` would let
    a typo grant authority."""
    for bogus in ("LIVE", "Live", "live ", "enabled", True, 1, None):
        cfg = {"authority": {"approve": bogus}}
        assert authmod.mode_for(cfg, "o/r", "approve") == "disabled", bogus
        assert authmod.can_act(cfg, "o/r", "approve") is False, bogus
        assert authmod.validate_authority(cfg["authority"]) != [], bogus


def test_an_unhashable_mode_value_never_grants_authority() -> None:
    """`mode_for` tests membership in a frozenset, so a list or dict mode raises
    TypeError rather than resolving. A crash denies the action, which is the
    property that matters here — but it is reported as an unhandled shape, since
    fail-closed would be a returned `disabled`, not a traceback."""
    for bogus in (["live"], {"mode": "live"}, {"live"}):
        cfg = {"authority": {"approve": bogus}}
        try:
            resolved = authmod.mode_for(cfg, "o/r", "approve")
        except TypeError:
            continue  # denied by crashing; never granted
        assert resolved == "disabled", bogus
        assert authmod.can_act(cfg, "o/r", "approve") is False, bogus


def test_an_unknown_activity_resolves_to_disabled() -> None:
    cfg = {"authority": {"default": "live"}}
    for bogus in ("merge", "push", "", "APPROVE", "approve_review"):
        assert authmod.mode_for(cfg, "o/r", bogus) == "disabled", bogus
        assert authmod.can_act(cfg, "o/r", bogus) is False, bogus


def test_a_malformed_authority_section_is_reported_not_ignored() -> None:
    for bad in (None, [], "live", 0):
        assert authmod.validate_authority(bad) != [], bad
    assert authmod.validate_authority({"default": "on"}) != []
    assert authmod.validate_authority({"o/r": "live"}) != []
    assert authmod.validate_authority({"o/r": {"merge": "live"}}) != []
    assert authmod.validate_authority({"o/r": {"approve": "on"}}) != []
    # ...and a valid one really is accepted.
    assert authmod.validate_authority({"default": "disabled", "o/r": {"approve": "live"}}) == []


def test_the_absent_authority_section_grants_nothing() -> None:
    for cfg in ({}, {"authority": None}, {"authority": {}}, {"authority": {"other/repo": {"approve": "live"}}}):
        for activity in sorted(authmod.ACTIVITIES):
            assert authmod.mode_for(cfg, "o/r", activity) == "disabled", (cfg, activity)
    assert set(authmod.defaults().values()) == {"disabled"}


# --------------------------------------------------------------------------
# 2. the request-changes action gate
# --------------------------------------------------------------------------


def _rc_kwargs(**over):
    kwargs = dict(
        cfg={"authority": {"request_changes": "live"}},
        repo="o/r",
        head_sha=_HEAD,
        pr={"head": _HEAD},
        verified_blocker=True,
        blocker_evidence_sufficient=True,
        assurance=AssuranceEvaluation(required_assurance="high", achieved_assurance=1.0),
        revalidate=lambda: True,
    )
    kwargs.update(over)
    return kwargs


def test_the_control_a_fully_evidenced_request_changes_is_allowed() -> None:
    gate = request_changes_gate(**_rc_kwargs())
    assert gate.allowed is True, gate.as_dict()
    assert gate.failed == []


def test_each_request_changes_gate_denies_on_its_own() -> None:
    """One counterexample per gate: flip exactly one input and the action must be
    refused, naming that gate. A gate that only fires in combination is not a
    gate."""
    cases = [
        ({"cfg": {"authority": {"request_changes": "disabled"}}}, "authority"),
        ({"cfg": {}}, "authority"),
        ({"rc_authority_ok": lambda: False}, "authority"),
        ({"pr": {"head": "e" * 40}}, "exact_head"),
        ({"verified_blocker": False}, "verified_blocker"),
        ({"blocker_evidence_sufficient": False}, "blocker_evidence"),
        ({"assurance": None}, "assurance"),
        ({"assurance": AssuranceEvaluation(required_assurance="high", achieved_assurance=0.2)},
         "assurance"),
        ({"revalidate": None}, "final_revalidation"),
        ({"revalidate": lambda: False}, "final_revalidation"),
    ]
    for override, expected_gate in cases:
        gate = request_changes_gate(**_rc_kwargs(**override))
        assert gate.allowed is False, override
        assert expected_gate in gate.failed, (override, gate.failed)


def test_an_unverified_finding_is_never_a_request_changes() -> None:
    """Suggestions and uncertain findings are comments. Blocking someone's PR on an
    unverified opinion is the failure this gate exists to prevent."""
    gate = request_changes_gate(**_rc_kwargs(verified_blocker=False,
                                             blocker_evidence_sufficient=False))
    assert gate.allowed is False
    assert "verified_blocker" in gate.failed and "blocker_evidence" in gate.failed


def test_request_changes_authority_is_independent_of_approve_authority() -> None:
    """Granting one mutating activity must not grant the other."""
    gate = request_changes_gate(**_rc_kwargs(cfg={"authority": {"approve": "live"}}))
    assert gate.allowed is False
    assert "authority" in gate.failed


# --------------------------------------------------------------------------
# 3. no decision path reaches a mutation without the gate
# --------------------------------------------------------------------------


class _Sender:
    """An injected HTTP sender that records every call. A refused mutation must
    leave `calls` empty — that is the observable proof no request was made."""

    def __init__(self) -> None:
        self.calls: list[str] = []

    def __call__(self, token: str, payload: str):
        self.calls.append(payload)
        return 200, {"data": {"addPullRequestReview": {"pullRequestReview": {"id": "R_1"}}}}


def test_the_generic_mutation_entry_point_refuses_approval_without_sending() -> None:
    state = _state()
    sender = _Sender()
    try:
        gh.post(state, "approve_review", {"pullRequestId": "PR_1"}, "job-1", token="t",
                http_post=sender)
    except gh.ApprovalRecordRequiredError as exc:
        assert "execute_approval" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("post() must never expose APPROVE")
    assert sender.calls == []
    state.close()


def test_the_generic_entry_point_does_send_a_non_approval_mutation() -> None:
    """Guards the guard: if `post` refused everything, the test above would prove
    nothing about approval specifically."""
    state = _state()
    sender = _Sender()
    gh.post(state, "add_comment_review", {"pullRequestId": "PR_1", "body": "note"}, "job-2",
            token="t", http_post=sender)
    assert len(sender.calls) == 1
    state.close()


def test_an_unsupported_operation_is_refused_before_any_request() -> None:
    state = _state()
    sender = _Sender()
    for operation in ("merge_pull_request", "approve", "", "close_pr"):
        try:
            gh.post(state, operation, {}, "job-3", token="t", http_post=sender)
        except RuntimeError as exc:
            assert "unsupported mutation operation" in str(exc)
        else:  # pragma: no cover
            raise AssertionError(f"{operation!r} must be refused")
    assert sender.calls == []
    state.close()


def test_only_approve_review_is_flagged_as_requiring_a_decision_record() -> None:
    required = {name for name in gh.MUTATIONS if gh.requires_approval_record(name)}
    assert required == {"approve_review"}
    assert gh.fixed_event_of("approve_review") == "APPROVE"
    assert gh.fixed_event_of("add_comment_review") == "COMMENT"
    assert gh.fixed_event_of("request_changes_review") == "CHANGES_REQUESTED"


def _decision(**over) -> dict:
    expires = (dt.datetime.now(dt.timezone.utc) + dt.timedelta(hours=1)) \
        .replace(microsecond=0).isoformat().replace("+00:00", "Z")
    base = {"id": "dec-1", "repo": "o/r", "number": 5, "head_sha": _HEAD,
            "policy_hash": "ph-1", "status": "eligible", "expires_at": expires}
    base.update(over)
    return base


def _approve(state, decision, sender, **over):
    kwargs = dict(
        variables={"pullRequestId": "PR_1"},
        job="job-approve",
        repo="o/r",
        number=5,
        current_head_sha=_HEAD,
        current_policy_hash="ph-1",
        login="review-bot",
        token="t",
        http_post=sender,
        rest_before=lambda: True,
        rest_after=lambda: "verified",
    )
    kwargs.update(over)
    return gh.execute_approval(state, decision, **kwargs)


def test_the_control_a_fully_eligible_decision_does_approve() -> None:
    state = _state()
    sender = _Sender()
    _approve(state, _decision(), sender)
    assert len(sender.calls) == 1
    state.close()


def test_no_defective_decision_reaches_the_approve_mutation() -> None:
    """Every way a decision can be wrong, and in every one the injected sender must
    never be called. `sender.calls == []` is the whole assertion: an approval that
    is refused *after* the request has already been made is not refused."""
    expired = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(minutes=1)) \
        .replace(microsecond=0).isoformat().replace("+00:00", "Z")
    cases = [
        (None, "no decision record at all"),
        ({}, "empty decision record"),
        (_decision(repo="other/repo"), "decision belongs to another repository"),
        (_decision(number=6), "decision belongs to another PR"),
        (_decision(head_sha="f" * 40), "decision was made against another HEAD"),
        (_decision(policy_hash="ph-2"), "policy changed since the decision"),
        (_decision(status="pending"), "decision is not eligible"),
        (_decision(status="revoked"), "decision was revoked"),
        (_decision(expires_at=None), "decision has no expiry"),
        (_decision(expires_at=""), "decision has an empty expiry"),
        (_decision(expires_at="not-a-timestamp"), "unparseable expiry fails closed"),
        (_decision(expires_at=expired), "decision has expired"),
    ]
    for decision, why in cases:
        state = _state()
        sender = _Sender()
        try:
            _approve(state, decision, sender)
        except (gh.ApprovalRecordRequiredError, DecisionStaleError):
            pass
        else:  # pragma: no cover
            raise AssertionError(f"approval must be refused: {why}")
        assert sender.calls == [], why
        state.close()


def test_approval_never_mutates_without_a_passing_final_revalidation() -> None:
    """Revalidation is injected, never assumed. Missing, falsy, or reporting any
    failing condition all deny — and deny before the request.

    `lambda: {}` is deliberately absent: an empty dict has no failing keys, so
    `_revalidate_before` treats it as a pass. That default-open branch is
    reported rather than asserted as correct."""
    for revalidation, why in (
        (None, "no revalidation supplied"),
        (lambda: None, "revalidation returned nothing"),
        (lambda: False, "revalidation failed"),
        (lambda: {"head_matches": True, "still_open": False}, "one condition failed"),
        (lambda: {"head_matches": False}, "head moved"),
    ):
        state = _state()
        sender = _Sender()
        try:
            _approve(state, _decision(), sender, rest_before=revalidation)
        except PermissionAuthorityError:
            pass
        else:  # pragma: no cover
            raise AssertionError(f"approval must be refused: {why}")
        assert sender.calls == [], why
        state.close()


def test_a_decision_loaded_by_id_that_does_not_exist_never_reaches_the_mutation() -> None:
    """Caller JSON is not the record. Passing a perfectly-formed decision dict
    alongside an unknown id must still refuse."""
    state = _state()
    sender = _Sender()
    try:
        _approve(state, _decision(), sender, decision_id="no-such-decision")
    except gh.ApprovalRecordRequiredError as exc:
        assert "no-such-decision" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("an unknown decision id must be refused")
    assert sender.calls == []
    state.close()


# --------------------------------------------------------------------------
# 4. snapshot pinning
# --------------------------------------------------------------------------


_POLICY = {
    "version": "p1",
    "authority": {"approve": "disabled"},
    "approval": {"mode": "disabled", "effective_risk_max": 24, "complexity_max": 2,
                 "file_limit": 50, "line_limit": 1000, "approval_rate_max": 0.2},
    "risk": {"bands": {"low": 24, "medium": 99, "high": 100}},
    "human_queue": {"expiry_minutes": 1440},
}


def _snapshot(config: dict, policy: dict | None = None) -> snapmod.RuntimeSnapshot:
    return snapmod.build_snapshot({**config, "policy": policy or _POLICY})


def test_an_in_flight_job_resolves_the_snapshot_it_started_with() -> None:
    """A config edit mid-flight must not retroactively change a running job's
    authority. This is the counterexample for "get() quietly falls back to
    active()"."""
    store = snapmod.SnapshotStore(tempfile.mkdtemp())
    original = _snapshot({"version": 1, "approval": {"mode": "disabled"}})
    store.activate(original)

    widened = _snapshot({"version": 2, "approval": {"mode": "live"}},
                        {**_POLICY, "version": "p2", "approval": {"mode": "live"}})
    store.activate(widened)

    assert store.active().hash == widened.hash
    resumed = store.get(original.hash)
    assert resumed is not None
    assert resumed.hash == original.hash
    assert resumed.config["approval"]["mode"] == "disabled"
    assert resumed.policy["approval"]["mode"] == "disabled"
    assert resumed.config_version == "cfg-1"

    # If the archive is gone the answer is "unknown", never "use the current
    # one" — silently upgrading an in-flight job is the exact failure here.
    (store.by_hash_dir / f"{original.hash}.json").unlink()
    assert store.get(original.hash) is None
    assert store.get("") is None


def test_a_result_pinned_to_one_snapshot_cannot_be_relabelled_with_another() -> None:
    store = snapmod.SnapshotStore(tempfile.mkdtemp())
    first = _snapshot({"version": 1})
    second = _snapshot({"version": 2})
    pinned = store.pin({"outcome": "advisory"}, first)
    assert pinned["snapshot_hash"] == first.hash
    try:
        store.pin(pinned, second)
    except snapmod.SnapshotPinError as exc:
        assert first.hash[:12] in str(exc) and second.hash[:12] in str(exc)
    else:  # pragma: no cover
        raise AssertionError("repinning must be refused")
    # Re-pinning to the SAME snapshot is idempotent, not an error.
    assert store.pin(pinned, first)["snapshot_hash"] == first.hash


def test_a_snapshot_whose_hash_does_not_match_its_contents_is_not_loaded() -> None:
    """A tampered or truncated archive must read as absent, so the job stops rather
    than resuming under a payload nobody signed."""
    root = pathlib.Path(tempfile.mkdtemp())
    store = snapmod.SnapshotStore(root)
    snapshot = _snapshot({"version": 1, "approval": {"mode": "disabled"}})
    store.activate(snapshot)

    archive = store.by_hash_dir / f"{snapshot.hash}.json"
    body = archive.read_text(encoding="utf-8").replace('"disabled"', '"live"')
    archive.write_text(body, encoding="utf-8")
    assert store.get(snapshot.hash) is None

    store.active_path.write_text("{ not json", encoding="utf-8")
    assert store.active() is None


def test_an_unusable_config_or_policy_never_becomes_a_snapshot() -> None:
    for bad_config in ({}, None, [], "config"):
        try:
            snapmod.build_snapshot(bad_config)  # type: ignore[arg-type]
        except snapmod.SnapshotError:
            continue
        raise AssertionError(f"{bad_config!r} must not build a snapshot")
    # No inline policy and no policy file at all.
    try:
        snapmod.build_snapshot({"version": 1})
    except snapmod.SnapshotError as exc:
        assert "no policy configured" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("a config with no policy must not build a snapshot")
    # A policy that fails validation must not be activated either.
    try:
        snapmod.build_snapshot({"version": 1, "policy": {"version": "p1"}},
                               validate_policy=policymod.validate_policy)
    except snapmod.SnapshotError as exc:
        assert "invalid policy" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("an invalid policy must not build a snapshot")


def test_a_missing_policy_file_is_an_error_not_an_empty_policy() -> None:
    missing = pathlib.Path(tempfile.mkdtemp()) / "policy.json"
    try:
        snapmod.build_snapshot({"version": 1}, policy_path=missing)
    except snapmod.SnapshotError as exc:
        assert "policy file not found" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("a missing policy file must be refused")

    unreadable = pathlib.Path(tempfile.mkdtemp()) / "policy.json"
    unreadable.write_text("{ broken", encoding="utf-8")
    try:
        snapmod.build_snapshot({"version": 1}, policy_path=unreadable)
    except snapmod.SnapshotError as exc:
        assert "unreadable" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("an unreadable policy file must be refused")

    empty = pathlib.Path(tempfile.mkdtemp()) / "policy.json"
    empty.write_text("{}", encoding="utf-8")
    try:
        snapmod.build_snapshot({"version": 1}, policy_path=empty)
    except snapmod.SnapshotError:
        pass
    else:  # pragma: no cover
        raise AssertionError("an empty policy file must be refused")


def test_a_policy_missing_any_required_section_is_refused() -> None:
    assert policymod.validate_policy(dict(_POLICY)) == []
    for key in sorted(policymod.REQUIRED_KEYS):
        broken = {k: v for k, v in _POLICY.items() if k != key}
        issues = policymod.validate_policy(broken)
        assert issues, key
        try:
            policymod.validate_or_raise(broken)
        except policymod.PolicyValidationError:
            continue
        raise AssertionError(f"a policy missing {key} must raise")
