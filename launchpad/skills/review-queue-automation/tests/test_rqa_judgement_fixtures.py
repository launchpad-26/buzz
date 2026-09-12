#!/usr/bin/env python3
"""Fakes and fixtures shared by the `rqa.judgement` (P-07) tests.

Self-contained: no dependency on another part's test fixtures, so this
package's tests never break because a sibling's fixtures changed shape. Every
builder has a sane default so a test only names the field it is exercising.
"""

from __future__ import annotations

import pathlib
import sys
from datetime import datetime, timedelta, timezone

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from rqa.contracts import (  # noqa: E402
    Activity,
    AppendFailed,
    Attempt,
    AttemptFailure,
    Attestation,
    Blocking,
    Budget,
    CarriedEvidence,
    CarryOver,
    Category,
    CheckRun,
    Decision,
    Entry,
    EvidenceState,
    External,
    Facts,
    Finding,
    HarnessIdentity,
    InjectionAttempt,
    Job,
    JobStatus,
    Location,
    Mechanical,
    Obligation,
    PanelResult,
    Plan,
    Policy,
    PrFacts,
    Remedy,
    RemediationPolicy,
    Route,
    Snapshot,
    Verdict,
)
from rqa.protocol import protocol_hash
from rqa.record.hashing import canonical_json

REPO = "acme/widgets"
NUMBER = 7
HEAD_SHA = "a" * 40
BASE_SHA = "b" * 40

CUTOFF = datetime(2026, 9, 12, 12, 0, 0, tzinfo=timezone.utc)
BEFORE_CUTOFF = CUTOFF - timedelta(minutes=5)
AFTER_CUTOFF = CUTOFF + timedelta(minutes=5)


def make_job(*, job_id: str = "job-1") -> Job:
    return Job(
        id=job_id,
        repo=REPO,
        number=NUMBER,
        head_sha=HEAD_SHA,
        base_sha=BASE_SHA,
        head_repo=REPO,
        head_ref="feature/x",
        predecessor_job=None,
        predecessor_head_sha=None,
        snapshot_hash="snap-1",
        status=JobStatus.REVIEWING,
    )


def make_facts(
    *,
    changed_paths: frozenset[str] = frozenset({"src/widget.py"}),
    checks: tuple[CheckRun, ...] = (),
    base_checks: tuple[CheckRun, ...] = (),
    files: dict[str, bytes] | None = None,
    title: str = "Fix the widget",
    body: str = "Body text",
    diff: str = "--- a/x\n+++ b/x\n+line\n",
    fetched_at: datetime = CUTOFF,
) -> Facts:
    pr = PrFacts(
        repo=REPO,
        number=NUMBER,
        head_sha=HEAD_SHA,
        base_sha=BASE_SHA,
        merge_base_sha=BASE_SHA,
        head_repo=REPO,
        head_ref="feature/x",
        head_protected=False,
        author="alice",
        labels=frozenset(),
        title=title,
        body=body,
    )
    return Facts(
        pr=pr,
        diff=diff,
        changed_paths=changed_paths,
        revision_changed_paths=frozenset(),
        files=files if files is not None else {path: b"content\n" for path in sorted(changed_paths)},
        checks=checks,
        base_checks=base_checks,
        reviews=(),
        fetched_at=fetched_at,
    )


def make_obligation(
    *,
    obligation_id: str = "O1",
    paths: tuple[str, ...] = ("**",),
    required_for: frozenset[str] = frozenset({"standard"}),
    evidence: str = "tests pass",
) -> Obligation:
    return Obligation(id=obligation_id, paths=paths, required_for=required_for, evidence=evidence)


def make_policy(
    *,
    obligations: tuple[Obligation, ...] = (),
    assurance: dict[str, int] | None = None,
    blocking_categories: frozenset[Category] = frozenset({Category.SECURITY, Category.EVIDENCE}),
    mechanical_categories: frozenset[Category] = frozenset({Category.MECHANICAL}),
    mechanical_tools: frozenset[str] = frozenset({"fmt"}),
) -> Policy:
    return Policy(
        version="policy-1",
        obligations=obligations,
        blocking=Blocking(categories=blocking_categories, severities=frozenset({"high"}), corroboration=2),
        mechanical=Mechanical(categories=mechanical_categories, tools=mechanical_tools),
        assurance=dict(assurance or {"standard": 1}),
        remediation=RemediationPolicy(allow_forks=False),
    )


def make_snapshot(*, policy: Policy | None = None) -> Snapshot:
    return Snapshot(
        hash="snap-1",
        repo=REPO,
        protocol_hash=protocol_hash(),
        authority={activity: False for activity in Activity},
        routes=(),
        external=External(allowed=False, deny_label="no-external"),
        policy=policy if policy is not None else make_policy(),
        budget=Budget(per_pr_tokens=None, per_repo_daily_tokens=None, per_model_daily_tokens=None),
    )


def make_plan(
    *, obligations: tuple[str, ...] = ("O1",), risk_class: str = "standard", strategy: str = "single_pass"
) -> Plan:
    return Plan(
        obligations=obligations,
        omitted={},
        strategy=strategy,
        participants=len(obligations) or 1,
        risk_class=risk_class,
        head_sha=HEAD_SHA,
        snapshot_hash="snap-1",
        protocol_hash=protocol_hash(),
        policy_version="policy-1",
    )


def make_carried(
    *,
    obligation_id: str,
    source_job: str = "job-0",
    source_judgement_seq: int = 3,
    source_attestations: tuple[str, ...] = ("job-0:01",),
) -> CarriedEvidence:
    return CarriedEvidence(
        obligation_id=obligation_id,
        state=EvidenceState.VERIFIED,
        source_job=source_job,
        source_judgement_seq=source_judgement_seq,
        source_attestations=source_attestations,
    )


def make_carry(
    *,
    reused: tuple[CarriedEvidence, ...] = (),
    regenerated: tuple[str, ...] = (),
    reasons: dict[str, str] | None = None,
    source_job: str | None = None,
) -> CarryOver:
    return CarryOver(
        reused=reused,
        regenerated=regenerated,
        reasons=dict(reasons or {}),
        source_job=source_job if source_job is not None else ("job-0" if reused else None),
    )


def make_route(*, family: str = "fam-a", harness: str = "fake", model: str = "model-a") -> Route:
    return Route(harness=harness, model=model, provider=f"provider-{family}", family=family, external=False)


def make_attestation(
    *,
    route: Route | None = None,
    started_at: datetime = BEFORE_CUTOFF,
    ended_at: datetime = BEFORE_CUTOFF,
    effort: str = "medium",
) -> Attestation:
    resolved_route = route if route is not None else make_route()
    return Attestation(
        harness=resolved_route.harness,
        model=resolved_route.model,
        provider=resolved_route.provider,
        route=resolved_route,
        effort=effort,
        started_at=started_at,
        ended_at=ended_at,
        exit_code=0,
    )


def make_verdict(
    *,
    obligations: dict[str, EvidenceState] | None = None,
    findings: tuple[Finding, ...] = (),
    injection_attempts: tuple[InjectionAttempt, ...] = (),
    protocol_version: str = "1",
) -> Verdict:
    return Verdict(
        obligations=dict(obligations if obligations is not None else {"O1": EvidenceState.VERIFIED}),
        findings=findings,
        injection_attempts=injection_attempts,
        identity=HarnessIdentity(harness="fake", model="model-a", provider="provider-fam-a"),
        protocol_version=protocol_version,
    )


def make_attempt(
    *,
    attempt_id: str = "att-1",
    route: Route | None = None,
    outcome: Verdict | AttemptFailure | None = None,
    attestation: Attestation | None = None,
) -> Attempt:
    resolved_route = route if route is not None else make_route()
    resolved_attestation = (
        attestation if attestation is not None else make_attestation(route=resolved_route)
    )
    return Attempt(
        id=attempt_id,
        route=resolved_route,
        outcome=outcome if outcome is not None else make_verdict(),
        attestation=resolved_attestation,
    )


def make_panel(
    *,
    attempts: tuple[Attempt, ...] = (),
    complete: bool = True,
    incomplete_reason: str | None = None,
    evidence_cutoff: datetime = CUTOFF,
    bound_reached: bool = False,
) -> PanelResult:
    return PanelResult(
        attempts=attempts,
        complete=complete,
        incomplete_reason=incomplete_reason,
        evidence_cutoff=evidence_cutoff,
        bound_reached=bound_reached,
    )


def make_finding(
    *,
    finding_id: str = "F1",
    categories: frozenset[Category] = frozenset({Category.SECURITY}),
    location: Location | None = None,
    evidence: str = "evidence text",
    severity: str = "blocker",
    remedy: Remedy | None = None,
    behaviour_changing: bool | None = False,
    source_attempt: str = "att-1",
) -> Finding:
    return Finding(
        id=finding_id,
        categories=categories,
        extra_tags=frozenset(),
        location=location if location is not None else Location(path="src/widget.py", line=10),
        evidence=evidence,
        severity=severity,
        remedy=remedy,
        behaviour_changing=behaviour_changing,
        source_attempt=source_attempt,
    )


def make_decision(
    *,
    actor: str = "human-1",
    basis: str = "manual review",
    substantiates: str | None = "O1",
    outcome: str | None = "approved",
) -> Decision:
    return Decision(actor=actor, basis=basis, substantiates=substantiates, outcome=outcome)


class FakeRecord:
    """P-12's `RecordWriter`, in memory, with P-12's own payload rule enforced —
    the same canonical-JSON check the real writer applies, so a payload this
    package cannot actually persist fails the test that builds it rather than
    silently passing."""

    def __init__(self, *, fail_kind: str | None = None) -> None:
        self.entries: list[tuple[str, str, dict]] = []
        self.fail_kind = fail_kind
        self._seq = 0

    def append(self, job_id: str, kind: str, payload) -> Entry:
        if kind == self.fail_kind:
            raise AppendFailed(f"injected failure appending {kind}")
        canonical_json(payload=payload)
        self._seq += 1
        self.entries.append((job_id, kind, dict(payload)))
        return Entry(seq=self._seq, hash=f"hash-{self._seq}")

    def of_kind(self, kind: str) -> list[dict]:
        return [payload for _, entry_kind, payload in self.entries if entry_kind == kind]

    def kinds(self) -> list[str]:
        return [entry_kind for _, entry_kind, _ in self.entries]
