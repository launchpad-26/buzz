#!/usr/bin/env python3
"""Historical shadow backtest + current shadow mode for review-queue-automation.

- Every historical sample carries an INDEPENDENTLY sourced outcome label
  (clean | adverse | contested | unknown), an evidence source, and a cutoff
  timestamp. Labels are never derived from evaluator output and never inferred
  from the fact that the PR merged — a merged PR with no independent outcome is
  simply `unknown`.
- The backtest reconstructs ONLY the evidence timestamped at or before each
  sample's cutoff (future data is excluded) and never hardcodes checks,
  evidence, or adjudication as complete. The current policy hash and each
  evaluated head SHA are pinned in the report.
- The backtest grades against the SAME gate set as the live path. It builds an
  explicit `ApprovalEvidence` (see `historical_evidence`) from what the
  historical record can actually prove and FAILS CLOSED for everything it
  cannot. It never calls `approval_evaluate.evaluate` without evidence: that
  legacy call shape defaults `bounded_change`, `audit_writable`,
  `assurance_met`, `revalidation_ok` and `rate_limit_ok` to True and would grade
  every sample against a strictly more permissive gate set than production.
- Pure and read-only: evaluation runs with the in-memory config forced to
  approval.mode=`shadow`, which persists no decision record and performs no
  GitHub mutation. Time-based train/calibration split; false-auto-approval
  candidates are measured against the independent outcomes; escalation,
  coverage, and unknown rates are reported; and a real threshold-sensitivity
  sweep quantifies the approval/false-auto tradeoff.
- The train split is FITTED, not merely counted: a conservative
  `effective_risk_max` is learned from the train half and then scored on the
  held-out calibration half (see `learn_threshold`).
- Config suggestions are advisory text only; nothing is applied and live mode is
  never enabled.
- Current shadow mode prints WOULD_AUTO_APPROVE or the failed gates and performs
  no mutation and no decision persistence.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys
import tempfile
from dataclasses import dataclass, field
from typing import Any

from approval_evaluate import (
    ApprovalEvidence,
    EvalResult,
    PRFacts,
    evaluate,
    policy_hash_of,
)
from cli import resolve_or_onboarding
from common import State

VALID_OUTCOMES = {"clean", "adverse", "contested", "unknown"}

# Gates that reflect whether live approval is *activated* rather than whether the
# PR is eligible. In shadow mode they are definitionally false (mode != live and
# authority is not granted), so they are excluded when deciding
# "would_auto_approve". The decision signal is the PR-quality gate set;
# activation is a separate authorization precondition.
ACTIVATION_GATES = {"approval_enabled", "live_canary_approved", "approve_authority_live"}

#: Gates that `approval_evaluate.compute_gates` can only fill from an explicit
#: `ApprovalEvidence`. Passing no evidence object defaults every one of them to
#: True, which is why this module always constructs one.
EVIDENCE_GATES = (
    "bounded_change",
    "audit_writable",
    "assurance_met",
    "revalidation_ok",
    "rate_limit_ok",
)


def _normalize_number_map(raw: Any, *, label: str) -> dict[int, Any]:
    """Coerce a JSON object keyed by PR number into an int-keyed mapping.

    `json.loads` always produces STRING keys, while every lookup in this module
    is by `sample.number`, an int. Coercing once at the boundary is what keeps a
    CLI-supplied `--verdicts` file from being silently discarded. A key that is
    not an integer is an error, not a skip: dropping it would understate reviewer
    coverage in exactly the direction that reads as a safety result.
    """
    if not raw:
        return {}
    if not isinstance(raw, dict):
        raise ValueError(f"{label} must be a JSON object keyed by PR number")
    out: dict[int, Any] = {}
    for key, value in raw.items():
        if isinstance(key, bool):
            raise ValueError(f"{label} has a non-integer key: {key!r}")
        try:
            number = int(key)
        except (TypeError, ValueError):
            raise ValueError(f"{label} has a non-integer key: {key!r}") from None
        out[number] = value
    return out


@dataclass
class HistoricalSample:
    repo: str
    number: int
    head_sha: str
    merged_at: str
    outcome: str = "unknown"  # INDEPENDENTLY sourced; never derived from evaluator/merged
    evidence_source: str = ""
    cutoff: str = ""          # historical cutoff; only evidence timestamped <= cutoff is used
    checks_ok_at: str | None = None
    adjudication_at: str | None = None
    evidence_at: str | None = None
    #: When the head SHA became final (a closed PR's head cannot advance). This
    #: is the ONLY thing the historical record can offer in place of the live
    #: pre-mutation REST revalidation, and it is absent unless ingest set it.
    head_frozen_at: str | None = None
    files: list[str] = field(default_factory=list)
    additions: int = 0
    pr_facts: dict[str, Any] = field(default_factory=dict)

    def outcome_label(self) -> str:
        label = (self.outcome or "").strip().lower()
        return label if label in VALID_OUTCOMES else "unknown"

    def before_merge_facts(self) -> PRFacts:
        """Reconstruct only evidence that existed at or before the historical cutoff.

        checks_ok / adjudication_complete / evidence_fresh are true only when
        their evidence timestamp is set and <= cutoff. Missing or future evidence
        stays fail-closed (False).

        These are the three PR-fact gates. They are not the whole gate set: five
        further gates need evidence PR facts cannot supply, and this method does
        not fill them. See `historical_evidence` — calling `evaluate` without it
        defaults all five to True, which is the exact defect this method's
        docstring used to obscure by claiming "no gate is hardcoded true".
        """
        cutoff = self.cutoff or ""
        at_or_before = lambda ts: bool(ts) and bool(cutoff) and ts <= cutoff  # noqa: E731
        return PRFacts(
            draft=False,
            author_login=self.pr_facts.get("author_login", ""),
            checks_ok=at_or_before(self.checks_ok_at),
            adjudication_complete=at_or_before(self.adjudication_at),
            evidence_fresh=at_or_before(self.evidence_at),
            complexity=int(self.pr_facts.get("complexity", 0) or 0),
            head_sha=self.head_sha,
            files=self.files,
            additions=self.additions,
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            "repo": self.repo,
            "number": self.number,
            "head_sha": self.head_sha,
            "merged_at": self.merged_at,
            "outcome": self.outcome_label(),
            "evidence_source": self.evidence_source,
            "cutoff": self.cutoff,
        }


def build_sample(entry: dict[str, Any]) -> HistoricalSample:
    return HistoricalSample(
        repo=entry["repo"],
        number=entry["number"],
        head_sha=entry["head_sha"],
        merged_at=entry.get("merged_at", ""),
        outcome=entry.get("outcome", "unknown"),
        evidence_source=entry.get("evidence_source", ""),
        cutoff=entry.get("cutoff", ""),
        checks_ok_at=entry.get("checks_ok_at") or None,
        adjudication_at=entry.get("adjudication_at") or None,
        evidence_at=entry.get("evidence_at") or None,
        head_frozen_at=entry.get("head_frozen_at") or None,
        files=entry.get("files", []),
        additions=entry.get("additions", 0),
        pr_facts=entry.get("pr_facts", {}),
    )


def shadow_cfg(cfg: dict[str, Any]) -> dict[str, Any]:
    """In-memory clone with approval mode forced to `shadow`.

    Guarantees the evaluation persists no eligible decision and performs no
    mutation even when the repo-local config says `live` or `disabled`. The
    on-disk/live config is never modified.
    """
    scfg = json.loads(json.dumps(cfg))
    approval = dict(scfg.get("approval", {}) or {})
    approval["mode"] = "shadow"
    scfg["approval"] = approval
    return scfg


def audit_writable_probe(state: State) -> bool:
    """Can this run write the audit artefacts an approval would produce?

    Mirrors `dispatcher._approval_evidence`: an actual write probe, not an
    assumption. It is deliberately evaluated against the CURRENT state directory
    — the backtest asks whether today's policy would approve these PRs under
    today's harness, and an unwritable audit path blocks that regardless of PR.
    """
    try:
        probe = state.root / ".audit-probe"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink()
        return True
    except OSError:
        return False


def historical_evidence(
    sample: HistoricalSample,
    cfg: dict[str, Any],
    assessment: dict[str, Any],
    *,
    audit_writable: bool,
    prior_approvals: int = 0,
) -> ApprovalEvidence:
    """Explicit evidence for the five gates PR facts alone cannot establish.

    Each is proved from the historical record or FAILS CLOSED. `None` is never
    used for these five: `compute_gates` treats `None` as False only when an
    evidence object is supplied at all, and this function is the reason one
    always is.

    bounded_change   provable: the recorded addition count against
                     `assurance.large_diff_lines`, the same limit the dispatcher
                     applies. A sample with no recorded additions proves
                     nothing, so it fails closed rather than reading as "small".
    audit_writable   provable: a real write probe of the run's state directory.
    assurance_met    NOT provable from GitHub history — the assurance ladder is
                     computed by the panel, not recorded on the PR. It must be
                     supplied per sample in the `--assessments` file
                     (`{"assurance_met": true}`); absent, it fails closed.
    revalidation_ok  the live path proves this with a REST read immediately
                     before the mutation. History cannot replay that, but a
                     CLOSED PR's head is frozen, so `head_frozen_at` at-or-before
                     the cutoff plus a non-empty head SHA is the equivalent
                     proof. Absent (e.g. an open PR in `--mode current`), it
                     fails closed. Note this is NOT a self-comparison: an entry
                     without the timestamp fails.
    rate_limit_ok    two components, exactly as in the dispatcher. The daily
                     approval cap is replayed as a counterfactual over the run
                     (`prior_approvals` inside the trailing window). The REST
                     remaining floor cannot be reconstructed from history at all,
                     so a configured floor (`poll.rest_remaining_floor > 0`)
                     fails closed. A floor of 0 is the operator declaring no
                     floor, not an assumption made here.
    """
    approval = cfg.get("approval", {}) or {}
    assurance_cfg = cfg.get("assurance", {}) or {}
    assessment = assessment or {}

    large = int(assurance_cfg.get("large_diff_lines", 700) or 700)
    additions = int(sample.additions or 0)
    bounded_change = 0 < additions <= large

    assurance_met = bool(assessment.get("assurance_met", False))

    cutoff = sample.cutoff or ""
    frozen = sample.head_frozen_at or ""
    revalidation_ok = bool(sample.head_sha) and bool(frozen) and bool(cutoff) and frozen <= cutoff

    daily_limit = approval.get("daily_limit")
    within_daily = True
    if isinstance(daily_limit, int) and not isinstance(daily_limit, bool) and daily_limit >= 0:
        within_daily = prior_approvals < daily_limit
    floor = int((cfg.get("poll") or {}).get("rest_remaining_floor", 0) or 0)
    within_rest = floor <= 0
    rate_limit_ok = within_daily and within_rest

    return ApprovalEvidence(
        bounded_change=bounded_change,
        audit_writable=bool(audit_writable),
        assurance_met=assurance_met,
        revalidation_ok=revalidation_ok,
        rate_limit_ok=rate_limit_ok,
    )


def evaluate_before_merge(
    cfg: dict[str, Any],
    state: State,
    sample: HistoricalSample,
    verdicts: list[dict[str, Any]],
    assessments: dict[str, Any],
    login: str,
    *,
    evidence: ApprovalEvidence | None = None,
    prior_approvals: int = 0,
) -> dict[str, Any]:
    """Evaluate one historical sample through the approval gate in shadow mode.

    Pure: no decision persisted, no mutation. `would_auto_approve` is the
    complement of the failed PR-quality gates (activation gates excluded). The
    outcome label comes solely from the sample's independent evidence source.

    An explicit `ApprovalEvidence` is ALWAYS passed to `evaluate`. When the
    caller supplies none, one is derived here via `historical_evidence`, so the
    permissive legacy default-open branch in `approval_evaluate.compute_gates`
    is unreachable from this module.
    """
    if evidence is None:
        evidence = historical_evidence(
            sample, cfg, assessments or {},
            audit_writable=audit_writable_probe(state),
            prior_approvals=prior_approvals,
        )
    result: EvalResult = evaluate(
        state,
        cfg,
        repo=sample.repo, number=sample.number, head_sha=sample.head_sha,
        pr=sample.before_merge_facts(),
        verdicts=verdicts,
        profile={"capability": "workhorse", "effort": "medium", "independence": "challenger"},
        reviewers=[v.get("model", "?") for v in verdicts],
        assessments=assessments or {},
        login=login,
        evidence=evidence,
    )
    failed = list(result.failed_gates)
    would_auto_approve = not any(g for g in failed if g not in ACTIVATION_GATES)
    return {
        "repo": sample.repo,
        "number": sample.number,
        "head_sha": sample.head_sha,
        "merged_at": sample.merged_at,
        "outcome": sample.outcome_label(),
        "evidence_source": sample.evidence_source,
        "cutoff": sample.cutoff,
        "would_auto_approve": would_auto_approve,
        "risk_score": result.risk_score,
        "risk_band": result.risk_band_name,
        "failed_gates": failed,
        "decision_id": result.decision_id,
    }


def _evaluate_split(
    ordered: list[HistoricalSample],
    scfg: dict[str, Any],
    st: State,
    verdicts: dict[int, list[dict[str, Any]]],
    assessments: dict[int, dict[str, Any]],
    login: str,
    *,
    audit_writable: bool,
) -> list[dict[str, Any]]:
    """Evaluate samples in time order, replaying the daily approval cap.

    The cap is stateful in production (`dispatcher._recent_approval_count`), so
    the counterfactual has to be stateful too: each sample sees the number of
    would-approvals this run already produced inside the trailing window.
    """
    results: list[dict[str, Any]] = []
    approvals: list[str] = []
    for sample in ordered:
        cutoff = sample.cutoff or sample.merged_at or ""
        prior = len([ts for ts in approvals if _within_day(ts, cutoff)])
        evidence = historical_evidence(
            sample, scfg, assessments.get(sample.number, {}),
            audit_writable=audit_writable, prior_approvals=prior,
        )
        result = evaluate_before_merge(
            scfg, st, sample, verdicts.get(sample.number, []),
            assessments.get(sample.number, {}), login, evidence=evidence,
        )
        if result["would_auto_approve"]:
            approvals.append(cutoff)
        results.append(result)
    return results


def _within_day(earlier: str, later: str) -> bool:
    """True when `earlier` is inside the 24h window ending at `later`.

    Timestamps are ISO-8601 UTC strings; an unparseable pair conservatively
    counts as inside the window (it can only tighten the rate-limit gate).
    """
    import datetime as _dt

    if not earlier or not later:
        return True
    try:
        a = _dt.datetime.fromisoformat(earlier.replace("Z", "+00:00"))
        b = _dt.datetime.fromisoformat(later.replace("Z", "+00:00"))
    except ValueError:
        return True
    return _dt.timedelta(0) <= (b - a) <= _dt.timedelta(hours=24)


def learn_threshold(
    train_results: list[dict[str, Any]], configured_max: int
) -> dict[str, Any]:
    """Fit a conservative `approval.effective_risk_max` on the TRAIN split.

    Previously the train split was counted and discarded: no parameter was
    learned from it, so the split bought no leakage protection and only shrank
    the evaluation set. It now fits one parameter.

    The fit: find the lowest risk score among train samples that clear every
    non-risk gate yet carry an ADVERSE or CONTESTED independent outcome — the
    cheapest mistake the current gate set would have made — and place the
    threshold just below it. The fit only ever LOWERS the configured ceiling:
    raising it on the strength of "no bad sample was seen" is precisely the
    absence-of-evidence-as-safety error this report exists to prevent.

    The learned value is advisory. Nothing applies it; `apply_threshold` scores
    it on the held-out calibration split so the operator can see the tradeoff.
    """
    unblocked_bad = [
        r["risk_score"] for r in train_results
        if r["outcome"] in {"adverse", "contested"}
        and not [g for g in r["failed_gates"]
                 if g not in ACTIVATION_GATES and g != "effective_risk_le"]
    ]
    if not unblocked_bad:
        return {
            "fitted_on": len(train_results),
            "effective_risk_max": int(configured_max),
            "changed": False,
            "basis": ("no train sample with an adverse/contested outcome cleared the "
                      "non-risk gates; the configured ceiling is kept unchanged "
                      "(a fit never raises it)"),
        }
    learned = max(0, min(int(configured_max), min(unblocked_bad) - 1))
    return {
        "fitted_on": len(train_results),
        "effective_risk_max": learned,
        "changed": learned != int(configured_max),
        "basis": (f"lowest risk score among train adverse/contested samples that "
                  f"cleared every non-risk gate was {min(unblocked_bad)}; the "
                  f"learned ceiling sits just below it"),
    }


def apply_threshold(results: list[dict[str, Any]], threshold: int) -> dict[str, Any]:
    """Score a threshold on results that were NOT used to fit it."""
    approvable = [
        r for r in results
        if r["risk_score"] <= threshold
        and not [g for g in r["failed_gates"]
                 if g not in ACTIVATION_GATES and g != "effective_risk_le"]
    ]
    return {
        "threshold": int(threshold),
        "approval_candidates": len(approvable),
        "false_auto": len([r for r in approvable if r["outcome"] in {"adverse", "contested"}]),
    }


def backtest(
    samples: list[HistoricalSample],
    cfg: dict[str, Any],
    *,
    verdicts: dict[int, list[dict[str, Any]]],
    assessments: dict[int, dict[str, Any]],
    login: str,
    train_ratio: float = 0.7,
    state: State | None = None,
) -> dict[str, Any]:
    """Run a time-based train/calibration split backtest. Pure + deterministic.

    The train half fits a conservative risk ceiling (`learn_threshold`); the
    calibration half is held out and reports both the configured ceiling's
    outcome and the learned ceiling's.
    """
    scfg = shadow_cfg(cfg)
    st = state if state is not None else _null_state()
    verdicts = _normalize_number_map(verdicts, label="verdicts")
    assessments = _normalize_number_map(assessments, label="assessments")
    ordered = sorted(samples, key=lambda s: s.merged_at)
    split = int(len(ordered) * train_ratio)
    train = ordered[:split]
    calibrate = ordered[split:]
    audit_writable = audit_writable_probe(st)

    train_results = _evaluate_split(
        train, scfg, st, verdicts, assessments, login, audit_writable=audit_writable
    )
    results = _evaluate_split(
        calibrate, scfg, st, verdicts, assessments, login, audit_writable=audit_writable
    )

    false_approval = [r for r in results if r["would_auto_approve"] and r["outcome"] in {"adverse", "contested"}]
    approval_candidates = [r for r in results if r["would_auto_approve"]]
    calibrated = [r for r in results if r["outcome"] in {"clean", "adverse", "contested"}]
    unknown = [r for r in results if r["outcome"] == "unknown"]
    escalation_rate = len([r for r in results if not r["would_auto_approve"]]) / max(len(results), 1)
    eff_max = int((cfg.get("approval", {}) or {}).get("effective_risk_max", 24))
    sensitivity = _threshold_sensitivity(results, eff_max)
    learned = learn_threshold(train_results, eff_max)
    learned["held_out"] = apply_threshold(results, learned["effective_risk_max"])
    learned["configured"] = apply_threshold(results, eff_max)
    suggestions = _suggestions(results, false_approval, learned)

    # Which gate actually drove the escalations. Without this an operator reading
    # a 100% escalation rate cannot tell a PR-quality result from an environment
    # one (an unwritable audit dir, or a configured REST floor that history
    # cannot reconstruct, blocks every sample regardless of the PR).
    blocking: dict[str, int] = {}
    for r in results:
        for gate in r["failed_gates"]:
            if gate in ACTIVATION_GATES:
                continue
            blocking[gate] = blocking.get(gate, 0) + 1
    universal = sorted(g for g, n in blocking.items() if results and n == len(results))

    # Reviewer-evidence gates are fail-closed, so a run with no supplied verdicts
    # can only ever produce a 0% would-approve rate. That is an ABSENCE OF DATA,
    # not evidence that the policy is safe, and the report must not let the two be
    # confused when someone reads it to justify enabling autonomy.
    with_verdicts = len([s for s in calibrate if verdicts.get(s.number)])
    verdict_coverage = with_verdicts / max(len(calibrate), 1)
    warnings: list[str] = []
    if not verdicts:
        warnings.append(
            "no reviewer verdicts supplied: every reviewer-evidence gate is "
            "fail-closed, so would-approve is 0 by construction. This run measures "
            "the deterministic gates only and CANNOT support an autonomy decision."
        )
    elif with_verdicts == 0:
        warnings.append(
            f"reviewer verdicts were supplied for {len(verdicts)} PR number(s) but "
            "NONE matched a calibration sample. The would-approve rate is 0 because "
            "the verdicts were not applied, not because the policy rejected them; "
            "check the PR numbers and the train/calibration split."
        )
    elif verdict_coverage < 1.0:
        warnings.append(
            f"reviewer verdicts supplied for only {with_verdicts}/{len(calibrate)} "
            "samples; the would-approve rate is understated."
        )
    if universal:
        warnings.append(
            "gate(s) " + ", ".join(universal) + " failed for EVERY calibration "
            "sample; the escalation rate is driven by these rather than by PR "
            "quality. Check whether the evidence for them is reconstructible at all."
        )
    if len(calibrated) < len(results):
        warnings.append(
            f"{len(unknown)} sample(s) have an unknown outcome and cannot confirm "
            "or refute a decision."
        )

    report = {
        "policy_hash": policy_hash_of(cfg),
        "pinned_heads": sorted({r["head_sha"] for r in results}),
        "train_ratio": train_ratio,
        #: `total` counts the EVALUATED (calibration) samples; `sample_count` is
        #: the whole input set. Both are reported because the split makes them
        #: differ and a reader comparing "total" to their input file would
        #: otherwise think samples went missing.
        "total": len(results),
        "sample_count": len(ordered),
        "train_count": len(train),
        "calibrate_count": len(calibrate),
        "coverage": len(calibrated) / max(len(results), 1),
        "verdict_coverage": verdict_coverage,
        "samples_with_verdicts": with_verdicts,
        "verdict_numbers_supplied": sorted(verdicts),
        "decision_capable": with_verdicts > 0,
        "warnings": warnings,
        "unknown_rate": len(unknown) / max(len(results), 1),
        "escalation_rate": escalation_rate,
        "false_auto_approval_candidates": [r["number"] for r in false_approval],
        "false_auto_approval_count": len(false_approval),
        "approval_candidate_count": len(approval_candidates),
        "blocking_gate_counts": dict(sorted(blocking.items())),
        "universally_failed_gates": universal,
        "evidence_gates": list(EVIDENCE_GATES),
        "audit_writable": audit_writable,
        "learned_threshold": learned,
        "threshold_sensitivity": sensitivity,
        "suggestions": suggestions,
        "outcome_counts": {
            "clean": len([r for r in results if r["outcome"] == "clean"]),
            "adverse": len([r for r in results if r["outcome"] == "adverse"]),
            "contested": len([r for r in results if r["outcome"] == "contested"]),
            "unknown": len([r for r in results if r["outcome"] == "unknown"]),
        },
        "samples": results,
        "train_samples": train_results,
    }
    return report


def current_shadow(
    cfg: dict[str, Any],
    entry: dict[str, Any],
    *,
    verdicts: dict[int, list[dict[str, Any]]],
    assessments: dict[int, dict[str, Any]],
    login: str,
    state: State | None = None,
) -> dict[str, Any]:
    """Current shadow mode: evaluate one live PR head, emit WOULD_AUTO_APPROVE or
    the failed gates. No mutation, no decision persistence."""
    sample = build_sample(entry)
    st = state if state is not None else _null_state()
    verdicts = _normalize_number_map(verdicts, label="verdicts")
    assessments = _normalize_number_map(assessments, label="assessments")
    return evaluate_before_merge(
        shadow_cfg(cfg), st, sample, verdicts.get(sample.number, []),
        assessments.get(sample.number, {}), login,
    )


# Lazy per-process null state (empty DB, never seeded with decisions).
_NULL: State | None = None


def _null_state() -> State:
    global _NULL
    if _NULL is None:
        _NULL = State({"state_dir": tempfile.mkdtemp()})
    return _NULL


def _threshold_sensitivity(results: list[dict[str, Any]], current_max: int) -> dict[str, Any]:
    """Real sweep of the risk threshold.

    A calibrate sample is approvable at threshold `t` iff it clears every non-risk,
    non-activation gate AND `risk_score <= t`. Each candidate threshold is one of
    the observed risk scores (plus 0 and the current max), so the sweep shows the
    exact approval/false-auto tradeoff breakpoints.
    """
    entries: list[dict[str, Any]] = []
    for r in results:
        non_risk_failed = [g for g in r["failed_gates"] if g not in ACTIVATION_GATES and g != "effective_risk_le"]
        entries.append({"risk": r["risk_score"], "blocked": bool(non_risk_failed), "outcome": r["outcome"]})
    candidates = sorted({e["risk"] for e in entries if not e["blocked"]} | {0, int(current_max)})
    sweep: list[dict[str, Any]] = []
    for t in candidates:
        approvable = [e for e in entries if not e["blocked"] and e["risk"] <= t]
        sweep.append(
            {
                "threshold": t,
                "approval_candidates": len(approvable),
                "false_auto": sum(1 for e in approvable if e["outcome"] in {"adverse", "contested"}),
            }
        )
    return {"current": int(current_max), "sweep": sweep}


def _suggestions(
    results: list[dict[str, Any]],
    false_approval: list[dict[str, Any]],
    learned: dict[str, Any] | None = None,
) -> list[str]:
    """Advisory calibration suggestions only. Never applied or enabled live."""
    out: list[str] = []
    if learned and false_approval:
        held = learned.get("held_out") or {}
        configured = learned.get("configured") or {}
        if held.get("false_auto", 0) >= configured.get("false_auto", 0):
            out.append(
                "the fitted risk ceiling removes no false-auto candidate on the "
                "held-out half: risk score does not separate the good outcomes "
                "from the bad ones in this sample set, so lowering "
                "approval.effective_risk_max is not the control that would have "
                "helped. Look at the reviewer-evidence gates instead."
            )
    unknown = [r for r in results if r["outcome"] == "unknown"]
    if len(unknown) and len(results) and len(unknown) / len(results) > 0.4:
        out.append("Unknown-rate exceeds 40%; source more independent outcomes before trusting auto-approval metrics.")
    if false_approval:
        out.append(
            "false-auto candidates exist here; a lower approval.effective_risk_max would reduce risk (see threshold sweep)."
        )
    return out


def render_summary(report: dict[str, Any]) -> str:
    sens = report["threshold_sensitivity"]
    lines = [
        "Shadow calibration summary (read-only; no decisions/mutations written)",
        f"  policy hash: {report['policy_hash']}   pinned heads: {len(report['pinned_heads'])}",
        f"  samples: {report.get('sample_count', report['total'])} "
        f"= train {report['train_count']} (fitted) + calibrate {report['calibrate_count']} (evaluated)",
        f"  outcomes: {report['outcome_counts']}",
        f"  coverage: {report['coverage']:.0%}   unknown rate: {report['unknown_rate']:.0%}   escalation: {report['escalation_rate']:.0%}",
        f"  would-approve: {report['approval_candidate_count']}   false-auto candidates: {report['false_auto_approval_count']} -> {report['false_auto_approval_candidates']}",
        f"  reviewer verdicts: {report.get('samples_with_verdicts', 0)}/{report['calibrate_count']}"
        f" ({report.get('verdict_coverage', 0):.0%})"
        f"   decision-capable: {'yes' if report.get('decision_capable') else 'NO'}",
        f"  threshold sweep (current {sens['current']}): ",
    ]
    learned = report.get("learned_threshold") or {}
    if learned:
        lines.insert(
            -1,
            f"  learned ceiling (fitted on {learned.get('fitted_on', 0)} train sample(s)): "
            f"{learned.get('effective_risk_max')}"
            f"{' (unchanged)' if not learned.get('changed') else ''}"
            f" -> held-out would-approve {learned.get('held_out', {}).get('approval_candidates')}"
            f" / false-auto {learned.get('held_out', {}).get('false_auto')}",
        )
    if report.get("blocking_gate_counts"):
        lines.insert(-1, f"  blocking gates: {report['blocking_gate_counts']}")
    for point in sens["sweep"]:
        lines.append(
            f"    threshold {point['threshold']:>5}  would-approve {point['approval_candidates']:>3}  false-auto {point['false_auto']:>3}"
        )
    for warning in report.get("warnings", []):
        lines.append(f"  WARNING: {warning}")
    for suggestion in report.get("suggestions", []):
        lines.append(f"  SUGGESTION (advisory only): {suggestion}")
    lines.append(
        "  NOTE: backtest forces shadow mode in memory; no config is edited and live mode is never enabled."
    )
    return "\n".join(lines) + "\n"


def _load_number_map(path: str | None, *, label: str) -> dict[int, Any]:
    if not path:
        return {}
    raw = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    return _normalize_number_map(raw, label=label)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Historical shadow backtest / current shadow")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--mode", choices=["backtest", "current"], default="backtest")
    parser.add_argument("--samples", default=None, help="path to JSON list of HistoricalSample entries")
    parser.add_argument("--pr-facts", default=None, help="path to JSON entry for one PR (current mode)")
    parser.add_argument("--verdicts", default=None, help="path to JSON map number->verdicts")
    parser.add_argument("--assessments", default=None, help="path to JSON map number->assessments")
    parser.add_argument("--train-ratio", type=float, default=0.7)
    parser.add_argument("--out", default=None)
    args = parser.parse_args(argv)

    # `resolve_or_onboarding` always returns a 2-tuple; unpack, then test the
    # config. Testing the tuple itself for None never fires and lets a rejected
    # config reach the evaluation path as `None`.
    cfg, _ = resolve_or_onboarding(args.repo_root)
    if cfg is None:
        return 1

    # `json.loads` yields STRING keys; every lookup downstream is by int PR
    # number. Coerce here, at the one boundary where the mismatch is created.
    try:
        verdicts = _load_number_map(args.verdicts, label="verdicts")
        assessments = _load_number_map(args.assessments, label="assessments")
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"error": str(exc)}, indent=2))
        return 1

    if args.mode == "current":
        if not args.pr_facts:
            print(json.dumps({"error": "--mode current requires --pr-facts"}, indent=2))
            return 1
        entry = json.loads(pathlib.Path(args.pr_facts).read_text(encoding="utf-8"))
        result = current_shadow(cfg, entry, verdicts=verdicts, assessments=assessments, login=cfg.get("login", ""))
        text = "WOULD_AUTO_APPROVE" if result["would_auto_approve"] else f"FAILED_GATES {result['failed_gates']}"
        payload = {"mode": "current", "shadow_verdict": text, "result": result}
        if args.out:
            pathlib.Path(args.out).write_text(json.dumps(payload, indent=2), encoding="utf-8")
            print(json.dumps({"wrote": args.out}))
        print(text)
        print(json.dumps(result, indent=2))
        print("NOTE: current shadow performs no mutation and persists no decision.")
        return 0

    if not args.samples:
        print(json.dumps({"error": "--samples required for backtest"}, indent=2))
        return 1
    raw = json.loads(pathlib.Path(args.samples).read_text(encoding="utf-8"))
    samples = [build_sample(e) for e in raw]
    if not samples:
        print(json.dumps({"error": "no samples provided for backtest"}, indent=2))
        return 1
    report = backtest(
        samples, cfg, verdicts=verdicts, assessments=assessments, login=cfg.get("login", ""),
        train_ratio=args.train_ratio,
    )
    if args.out:
        pathlib.Path(args.out).write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(json.dumps({"wrote": args.out}))
    else:
        print(json.dumps(report, indent=2))
    print(render_summary(report))
    return 0


if __name__ == "__main__":
    sys.exit(main())