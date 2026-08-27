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
- Pure and read-only: evaluation runs with the in-memory config forced to
  approval.mode=`shadow`, which persists no decision record and performs no
  GitHub mutation. Time-based train/calibration split; false-auto-approval
  candidates are measured against the independent outcomes; escalation,
  coverage, and unknown rates are reported; and a real threshold-sensitivity
  sweep quantifies the approval/false-auto tradeoff.
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

from approval_evaluate import EvalResult, PRFacts, evaluate, policy_hash_of
from cli import resolve_or_onboarding
from common import State

VALID_OUTCOMES = {"clean", "adverse", "contested", "unknown"}

# Gates that reflect whether live approval is *activated* rather than whether the
# PR is eligible. In shadow mode they are definitionally false (mode != live), so
# they are excluded when deciding "would_auto_approve". The decision signal is the
# PR-quality gate set; activation is a separate authorization precondition.
ACTIVATION_GATES = {"approval_enabled", "live_canary_approved"}


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
    files: list[str] = field(default_factory=list)
    additions: int = 0
    pr_facts: dict[str, Any] = field(default_factory=dict)

    def outcome_label(self) -> str:
        label = (self.outcome or "").strip().lower()
        return label if label in VALID_OUTCOMES else "unknown"

    def before_merge_facts(self) -> PRFacts:
        """Reconstruct only evidence that existed at or before the historical cutoff.

        No gate is hardcoded true: checks_ok / adjudication_complete / evidence_fresh
        are true only when their evidence timestamp is set and <= cutoff. Missing or
        future evidence stays fail-closed (False).
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


def evaluate_before_merge(
    cfg: dict[str, Any],
    state: State,
    sample: HistoricalSample,
    verdicts: list[dict[str, Any]],
    assessments: dict[str, Any],
    login: str,
) -> dict[str, Any]:
    """Evaluate one historical sample through the approval gate in shadow mode.

    Pure: no decision persisted, no mutation. `would_auto_approve` is the
    complement of the failed PR-quality gates (activation gates excluded). The
    outcome label comes solely from the sample's independent evidence source.
    """
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
    """Run a time-based train/calibration split backtest. Pure + deterministic."""
    scfg = shadow_cfg(cfg)
    st = state if state is not None else _null_state()
    ordered = sorted(samples, key=lambda s: s.merged_at)
    split = int(len(ordered) * train_ratio)
    train = ordered[:split]
    calibrate = ordered[split:]
    results: list[dict[str, Any]] = []

    for sample in calibrate:
        results.append(
            evaluate_before_merge(
                scfg, st, sample, verdicts.get(sample.number, []), assessments.get(sample.number, {}), login
            )
        )

    false_approval = [r for r in results if r["would_auto_approve"] and r["outcome"] in {"adverse", "contested"}]
    approval_candidates = [r for r in results if r["would_auto_approve"]]
    calibrated = [r for r in results if r["outcome"] in {"clean", "adverse", "contested"}]
    unknown = [r for r in results if r["outcome"] == "unknown"]
    escalation_rate = len([r for r in results if not r["would_auto_approve"]]) / max(len(results), 1)
    eff_max = int((cfg.get("approval", {}) or {}).get("effective_risk_max", 24))
    sensitivity = _threshold_sensitivity(results, eff_max)
    suggestions = _suggestions(results, false_approval)

    # Reviewer-evidence gates are fail-closed, so a run with no supplied verdicts
    # can only ever produce a 0% would-approve rate. That is an ABSENCE OF DATA,
    # not evidence that the policy is safe, and the report must not let the two be
    # confused when someone reads it to justify enabling autonomy.
    with_verdicts = len([s for s in calibrate if verdicts.get(s.number)])
    verdict_coverage = with_verdicts / max(len(calibrate), 1)
    warnings: list[str] = []
    if with_verdicts == 0:
        warnings.append(
            "no reviewer verdicts supplied: every reviewer-evidence gate is "
            "fail-closed, so would-approve is 0 by construction. This run measures "
            "the deterministic gates only and CANNOT support an autonomy decision."
        )
    elif verdict_coverage < 1.0:
        warnings.append(
            f"reviewer verdicts supplied for only {with_verdicts}/{len(calibrate)} "
            "samples; the would-approve rate is understated."
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
        "total": len(results),
        "train_count": len(train),
        "calibrate_count": len(calibrate),
        "coverage": len(calibrated) / max(len(results), 1),
        "verdict_coverage": verdict_coverage,
        "samples_with_verdicts": with_verdicts,
        "decision_capable": with_verdicts > 0,
        "warnings": warnings,
        "unknown_rate": len(unknown) / max(len(results), 1),
        "escalation_rate": escalation_rate,
        "false_auto_approval_candidates": [r["number"] for r in false_approval],
        "false_auto_approval_count": len(false_approval),
        "approval_candidate_count": len(approval_candidates),
        "threshold_sensitivity": sensitivity,
        "suggestions": suggestions,
        "outcome_counts": {
            "clean": len([r for r in results if r["outcome"] == "clean"]),
            "adverse": len([r for r in results if r["outcome"] == "adverse"]),
            "contested": len([r for r in results if r["outcome"] == "contested"]),
            "unknown": len([r for r in results if r["outcome"] == "unknown"]),
        },
        "samples": results,
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
    return evaluate_before_merge(
        shadow_cfg(cfg), st, sample, verdicts.get(sample.number, []), assessments.get(sample.number, {}), login
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


def _suggestions(results: list[dict[str, Any]], false_approval: list[dict[str, Any]]) -> list[str]:
    """Advisory calibration suggestions only. Never applied or enabled live."""
    out: list[str] = []
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
        f"  samples: {report['total']} (train {report['train_count']}, calibrate {report['calibrate_count']})",
        f"  outcomes: {report['outcome_counts']}",
        f"  coverage: {report['coverage']:.0%}   unknown rate: {report['unknown_rate']:.0%}   escalation: {report['escalation_rate']:.0%}",
        f"  would-approve: {report['approval_candidate_count']}   false-auto candidates: {report['false_auto_approval_count']} -> {report['false_auto_approval_candidates']}",
        f"  reviewer verdicts: {report.get('samples_with_verdicts', 0)}/{report['calibrate_count']}"
        f" ({report.get('verdict_coverage', 0):.0%})"
        f"   decision-capable: {'yes' if report.get('decision_capable') else 'NO'}",
        f"  threshold sweep (current {sens['current']}): ",
    ]
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

    resolved = resolve_or_onboarding(args.repo_root)
    if resolved is None:
        return 1
    cfg, _ = resolved

    verdicts = json.loads(pathlib.Path(args.verdicts).read_text(encoding="utf-8")) if args.verdicts else {}
    assessments = json.loads(pathlib.Path(args.assessments).read_text(encoding="utf-8")) if args.assessments else {}

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