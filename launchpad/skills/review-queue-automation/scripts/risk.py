"""Deterministic risk + approval policy for review-queue-automation.

Fail-closed approval gates. Auto-approval never happens unless every gate is true.
A reviewer/model may raise risk but never lower the deterministic floor.

Risk is "effective" = max score across failure modes (never average).
  FMEA-C = severity * likelihood * detectability * complexity
Bands (configurable but continuous + non-overlapping, validated):
  Low <= 24, Medium 25..99, High >= 100
Auto-approval default: effective <= 24 and complexity <= 2.

FMEA-C types round-trip losslessly through JSON (`to_dict`/`from_dict`), the
effective score is the maximum (never the mean), a model observation can only
raise the deterministic floor (`combined_risk`), band continuity is enforced by
`validate_bands`, and a versioned `risk-assessment.json` writer/reader keeps the
artifacts self-describing and rejects unknown formats instead of guessing.
"""

from __future__ import annotations

import json
import pathlib
from dataclasses import dataclass, field
from typing import Any

LOW_CEILING = 24
MEDIUM_CEILING = 99
HIGH_FLOOR = 100

DEFAULT_AUTO_EFFECTIVE_MAX = 24
DEFAULT_AUTO_COMPLEXITY_MAX = 2

#: Version of the serialized `risk-assessment.json` shape. Bumped on schema change;
#: readers reject a mismatched version rather than silently misinterpreting data.
RISK_ASSESSMENT_VERSION = 1


class ConfigBandError(ValueError):
    pass


def validate_bands(bands: dict[str, Any]) -> None:
    """Validate that the configured (Low/Medium/High) bands are continuous and
    non-overlapping. Bands provided as linear clip bounds:
        {"low": 24, "medium": 99, "high": 100}
    i.e. low is (<= 24), medium is (25..99), high is (>= 100).
    """
    low = int(bands.get("low", LOW_CEILING))
    medium = int(bands.get("medium", MEDIUM_CEILING))
    high = int(bands.get("high", HIGH_FLOOR))
    # Continuity is enforced by requiring strict ordering; a gap or an overlap
    # between any pair is a configuration error and fails closed.
    if not 0 <= low < medium < high:
        raise ConfigBandError(
            f"risk bands must be strictly increasing and continuous: low={low} medium={medium} high={high}"
        )


@dataclass(frozen=True)
class FailureMode:
    """One credible failure mode with integer FMEA-C inputs."""

    id: str
    severity: int
    likelihood: int
    detectability: int
    complexity: int

    def __post_init__(self) -> None:
        for attr in ("severity", "likelihood", "detectability", "complexity"):
            value = int(getattr(self, attr))
            if not 1 <= value <= 10:
                raise ValueError(f"{attr} must be in [1..10], got {value}")

    def rpn(self) -> int:
        return self.severity * self.likelihood * self.detectability * self.complexity

    def as_dict(self) -> dict[str, int]:
        return {
            "severity": self.severity,
            "likelihood": self.likelihood,
            "detectability": self.detectability,
            "complexity": self.complexity,
            "rpn": self.rpn(),
        }

    def to_dict(self) -> dict[str, Any]:
        """Lossless serialization (JSON-friendly) including identity + inputs."""
        return {
            "id": self.id,
            "severity": self.severity,
            "likelihood": self.likelihood,
            "detectability": self.detectability,
            "complexity": self.complexity,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "FailureMode":
        """Restore a FailureMode from `to_dict` output. Validates inputs (raises
        ValueError on out-of-range FMEA-C scores)."""
        return cls(
            id=str(data["id"]),
            severity=int(data["severity"]),
            likelihood=int(data["likelihood"]),
            detectability=int(data["detectability"]),
            complexity=int(data["complexity"]),
        )


def effective_risk(failure_modes: list[FailureMode]) -> int:
    """Effective risk is the MAXIMUM RPN over modes, never the average."""
    return max((m.rpn() for m in failure_modes), default=0)


def combined_risk(deterministic_score: int, model_observed: int) -> int:
    """Combine a deterministic floor with a model observation.

    The result is the maximum: a model can only RAISE the effective risk above
    the deterministic floor, never lower it. This is the single canonical combine
    used by every approval evaluation path.
    """
    return max(int(deterministic_score), int(model_observed))


def risk_band(score: int, bands: dict[str, Any] | None = None) -> str:
    b = bands or {"low": LOW_CEILING, "medium": MEDIUM_CEILING, "high": HIGH_FLOOR}
    if score <= int(b["low"]):
        return "low"
    if score <= int(b["medium"]):
        return "medium"
    return "high"


class ProtectedTriggerError(Exception):
    pass


def protected_triggered(changed_paths: list[str], patterns: list[str], *, regex=True) -> tuple[str | None, str | None]:
    """Return (matched_path, matched_pattern) if any changed path hits a protected
    pattern, else (None, None). Fail-closed: unknown/matching surface is protected."""
    import re

    for path in changed_paths:
        for pattern in patterns:
            try:
                if regex and re.search(pattern, path):
                    return path, pattern
                if not regex and (pattern in path):
                    return path, pattern
            except re.error:
                continue
    return None, None


DEFAULT_PROTECTED = (
    r"(^|/)(security|auth|authentication|authorization|credentials?)(/|$)",
    r"(^|/)migrations?/",
    r"\.(sql|prisma|graphql)$",
    r"(^|/)deploy/",
    r"(^|/)\.github/workflows/",
    r"(^|/)release",
    r"(^|/)infra",
    r"schema/",
    r"policy",
)


@dataclass
class BoundedChange:
    one_clear_purpose: bool = False
    bounded_blast_radius: bool = False
    no_protected_trigger: bool = True
    straightforward_rollback: bool = False
    adequate_tests: bool = False
    no_unexplained_deps: bool = True
    no_unresolved_ambiguity: bool = True

    def passes(self) -> bool:
        return all(
            (
                self.one_clear_purpose,
                self.bounded_blast_radius,
                self.no_protected_trigger,
                self.straightforward_rollback,
                self.adequate_tests,
                self.no_unexplained_deps,
                self.no_unresolved_ambiguity,
            )
        )

    def failed(self) -> list[str]:
        gates = {
            "one_clear_purpose": self.one_clear_purpose,
            "bounded_blast_radius": self.bounded_blast_radius,
            "no_protected_trigger": self.no_protected_trigger,
            "straightforward_rollback": self.straightforward_rollback,
            "adequate_tests": self.adequate_tests,
            "no_unexplained_deps": self.no_unexplained_deps,
            "no_unresolved_ambiguity": self.no_unresolved_ambiguity,
        }
        return [k for k, v in gates.items() if not v]


@dataclass
class ApprovalState:
    """Full, canonical set of gates. `passed()` is the fail-closed auto-approval
    predicate. This is the single gate implementation consumed by the approval
    evaluation; no other module re-implements the per-gate semantics."""

    approval_enabled: bool = False
    live_canary_approved: bool = False
    pr_open_not_draft: bool = False
    author_not_identity: bool = False
    head_matches: bool = False
    no_protected_trigger: bool = True
    bounded_change: bool = False
    effective_risk_le: bool = False
    complexity_le: bool = False
    limits_pass: bool = False
    checks_complete_ok: bool = False
    evidence_fresh: bool = False
    assurance_met: bool = False
    required_reviewers_complete: bool = False
    distinct_reviewers: bool = False
    valid_verdicts: bool = False
    unanimous_clean: bool = False
    adjudication_complete: bool = False
    audit_writable: bool = False
    revalidation_ok: bool = False
    rate_limit_ok: bool = False

    def passed(self) -> bool:
        return all(
            (
                self.approval_enabled,
                self.live_canary_approved,
                self.pr_open_not_draft,
                self.author_not_identity,
                self.head_matches,
                self.no_protected_trigger,
                self.bounded_change,
                self.effective_risk_le,
                self.complexity_le,
                self.limits_pass,
                self.checks_complete_ok,
                self.evidence_fresh,
                self.assurance_met,
                self.required_reviewers_complete,
                self.distinct_reviewers,
                self.valid_verdicts,
                self.unanimous_clean,
                self.adjudication_complete,
                self.audit_writable,
                self.revalidation_ok,
                self.rate_limit_ok,
            )
        )

    def failed(self) -> dict[str, bool]:
        return {gate: not getattr(self, gate) for gate in self.all_gates() if not getattr(self, gate)}

    def all_gates(self) -> list[str]:
        return [
            "approval_enabled", "live_canary_approved", "pr_open_not_draft",
            "author_not_identity", "head_matches", "no_protected_trigger",
            "bounded_change", "effective_risk_le", "complexity_le", "limits_pass",
            "checks_complete_ok", "evidence_fresh", "assurance_met",
            "required_reviewers_complete", "distinct_reviewers", "valid_verdicts",
            "unanimous_clean", "adjudication_complete", "audit_writable",
            "revalidation_ok", "rate_limit_ok",
        ]

# ---- versioned risk-assessment.json -----------------------------------------
def serialize_assessment(data: dict[str, Any]) -> dict[str, Any]:
    """Wrap an assessment payload in the versioned envelope used on disk."""
    return {
        "version": RISK_ASSESSMENT_VERSION,
        "risk_assessment": data,
    }


def write_assessment(path: str | pathlib.Path, data: dict[str, Any]) -> pathlib.Path:
    """Persist a versioned `risk-assessment.json` atomically. The envelope is
    forwarded by `RISK_ASSESSMENT_VERSION` so later readers can detect schema
    drift instead of misparsing an older/newer shape."""
    target = pathlib.Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(serialize_assessment(data), indent=2, sort_keys=True)
    temp = target.with_name(target.name + ".tmp")
    temp.write_text(payload, encoding="utf-8")
    temp.replace(target)
    return target


def read_assessment(path: str | pathlib.Path) -> tuple[int, dict[str, Any]]:
    """Read a versioned `risk-assessment.json`, returning (version, data).

    Raises ValueError when the envelope carries a version this module does not
    understand, so a future incompatible file is never silently reinterpreted.
    """
    raw = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    version = int(raw.get("version", -1))
    if version != RISK_ASSESSMENT_VERSION:
        raise ValueError(
            f"risk-assessment.json version {version} unsupported (expected {RISK_ASSESSMENT_VERSION})"
        )
    data = raw.get("risk_assessment")
    if not isinstance(data, dict):
        raise ValueError("risk-assessment.json is missing a risk_assessment object")
    return version, data


# ---------------------------------------------------------------------------
# Assurance / evidence / uncertainty compute
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class AssuranceEvaluation:
    """Deterministic assurance & evidence summary for one review cycle.

    - `required_assurance` is derived from the maximum applicable RPN (a severe
      failure mode raises the bar; we never average it away).
    - `achieved_assurance` reflects the evidence actually gathered and the
      reviewer completion actually achieved, not the requested profile.
    - `evidence_completeness` is the share of required evidence facts present and
      fresh (files, sizes, checks, linked issue, PR posture).
    - `residual_uncertainty` rises with missing evidence, disagreement, and
      unknown outcomes, and lowers achieved assurance.
    """

    required_assurance: str = "none"
    achieved_assurance: float = 0.0
    evidence_completeness: float = 0.0
    residual_uncertainty: float = 0.0
    blockers: tuple[str, ...] = ()
    can_approve: bool = False
    can_request_changes: bool = False
    can_comment: bool = True
    # separate recommendation/attempted/confirmed tracking markers
    action_recommended: str = "none"
    action_attempted: str = "none"
    action_confirmed: str = "none"

    @property
    def assurance_met(self) -> bool:
        return self.achieved_assurance >= self._assurance_floor()

    def _assurance_floor(self) -> float:
        order = {"none": 0.0, "low": 0.4, "medium": 0.7, "high": 1.0}
        return order[self.required_assurance]

    def as_dict(self) -> dict[str, Any]:
        return {
            "required_assurance": self.required_assurance,
            "achieved_assurance": self.achieved_assurance,
            "evidence_completeness": self.evidence_completeness,
            "residual_uncertainty": self.residual_uncertainty,
            "blockers": list(self.blockers),
            "assurance_met": self.assurance_met,
            "can_approve": self.can_approve,
            "can_request_changes": self.can_request_changes,
            "can_comment": self.can_comment,
            "action_recommended": self.action_recommended,
            "action_attempted": self.action_attempted,
            "action_confirmed": self.action_confirmed,
        }


def assurance_from_risk(rpn: int, bands: dict[str, Any] | None = None) -> str:
    band = risk_band(rpn, bands)
    return {"low": "low", "medium": "medium", "high": "high"}[band]


def compute_assurance(
    *,
    required_rpn: int,
    bands: dict[str, Any] | None = None,
    evidence_completeness: float = 0.0,
    achieved_slots: int = 0,
    required_slots: int = 1,
    fresh: bool = False,
    disagreement: bool = False,
    unknown: bool = False,
    blockers: tuple[str, ...] = (),
) -> AssuranceEvaluation:
    """Deterministic assurance evaluation (no external effects)."""
    required_assurance = assurance_from_risk(required_rpn, bands)
    # Achieved assurance = evidence completeness weighted by reviewer completion and
    # reduced by missing evidence / disagreement / unknown outcome.
    completeness = max(0.0, min(1.0, evidence_completeness))
    slot_ratio = min(1.0, achieved_slots / required_slots) if required_slots else 0.0
    achieved = completeness * slot_ratio
    if not fresh:
        achieved *= 0.5  # missing/fresh-failure lowers assurance
        completeness *= 0.5
    uncertainty = 0.0
    if completeness < 1.0:
        uncertainty += (1.0 - completeness) * 0.5
    if disagreement:
        uncertainty += 0.25
    if unknown:
        uncertainty += 0.25
    uncertainty = min(1.0, uncertainty)
    achieved = max(0.0, achieved * (1.0 - uncertainty * 0.5))
    floor = assurance_from_risk(required_rpn, bands)
    order = {"none": 0.0, "low": 0.4, "medium": 0.7, "high": 1.0}
    met = achieved >= order[floor]

    blockers_list = list(blockers)
    can_approve = met and completeness >= 0.8 and uncertainty <= 0.2 and not blockers_list
    can_request_changes = bool(any("blocker" in b for b in blockers_list))
    can_comment = True
    return AssuranceEvaluation(
        required_assurance=required_assurance,
        achieved_assurance=round(achieved, 3),
        evidence_completeness=round(completeness, 3),
        residual_uncertainty=round(uncertainty, 3),
        blockers=tuple(blockers_list),
        can_approve=can_approve,
        can_request_changes=can_request_changes,
        can_comment=can_comment,
    )
