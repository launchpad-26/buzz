"""Shared contract types — `architecture/code/CONTRACTS.md` §1 and §§3-8.

`CONTRACTS.md` is the seam truth: every value that crosses a part boundary has
exactly one definition, and for §1 and §§3-8 that definition is this module. No
other module under `rqa/` may declare a name this file declares — the guard in
`tests/test_rqa_contracts_guard.py` fails the build if one does — and this file
declares nothing it does not own.

§2 (the protocol types: `EvidenceState`, `Category`, `Finding`, `Obligation`,
`Verdict`, …) belongs to `rqa.protocol` per `code/P-04-protocol.md` §1, and §9
(the edge signatures and their Protocols) is a separate deliverable. Neither is
declared here.

§§3-8 annotate fields with §2 names, while `code/P-04-protocol.md` §1 forbids
`rqa.protocol` importing another RQA part — so the runtime dependency runs
`rqa.protocol` → `rqa.contracts`, never the reverse. `from __future__ import
annotations` makes every §2 reference a string, so this module imports cleanly
whether or not `rqa.protocol` exists, and the `TYPE_CHECKING` import below keeps
the annotation text exactly as documented at no runtime cost.

Conventions (`CONTRACTS.md` preamble): Python 3.12; every value type a frozen
dataclass; policy, availability and budget outcomes are values while programming
errors are `*Error` exceptions; `Mapping` and `Sequence` are `collections.abc`.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Literal, Protocol, get_args

if TYPE_CHECKING:  # annotation-only; resolved by type checkers, never at import
    from rqa.protocol import (
        Category,
        EvidenceState,
        Finding,
        Obligation,
        Verdict,
    )


# --------------------------------------------------------------------------
# §1. Identity and status
# --------------------------------------------------------------------------


class Activity(str, Enum):  # P-08
    REVIEW = "review"
    COMMENT = "comment"
    APPROVE = "approve"
    REQUEST_CHANGES = "request_changes"
    REMEDIATE = "remediate"
    MERGE = "merge"


class JobStatus(str, Enum):  # P-02
    QUEUED = "queued"
    CLAIMED = "claimed"
    PLANNED = "planned"
    REVIEWING = "reviewing"
    JUDGED = "judged"
    REMEDIATING = "remediating"
    ESCALATED = "escalated"
    SUBMITTING = "submitting"
    CHANGES_REQUESTED = "changes_requested"
    APPROVED = "approved"
    MERGED = "merged"
    STOPPED = "stopped"
    SUPERSEDED = "superseded"


@dataclass(frozen=True)
class Job:  # P-01
    id: str  # stable_hash(repo, number, head_sha)
    repo: str  # "owner/name" of the managed (base) repository
    number: int
    head_sha: str
    base_sha: str
    head_repo: str  # "owner/name" the PR head lives in; == repo unless a fork
    head_ref: str  # branch name of the PR head in head_repo
    predecessor_job: str | None
    predecessor_head_sha: str | None  # exact predecessor revision used for E-23 revision compare
    snapshot_hash: str | None
    status: JobStatus


# --------------------------------------------------------------------------
# §3. Policy types (owner P-03)
# --------------------------------------------------------------------------


class ValidationErrorCode(str, Enum):
    UNREADABLE = "unreadable"
    MISSING_REQUIRED_SECTION = "missing_required_section"
    MISSING_POLICY = "missing_policy"
    UNKNOWN_KEY = "unknown_key"
    UNKNOWN_AUTHORITY_KEY = "unknown_authority_key"
    TOOL_NOT_IN_SET = "tool_not_in_set"
    INVALID_PATH_PATTERN = "invalid_path_pattern"
    NEGATIVE_BUDGET = "negative_budget"
    BAD_TYPE = "bad_type"


@dataclass(frozen=True)
class ValidationError:
    code: ValidationErrorCode
    path: str
    detail: str


@dataclass(frozen=True)
class ValidationFailure:
    repo: str
    errors: tuple[ValidationError, ...]


@dataclass(frozen=True)
class External:
    allowed: bool
    deny_label: str


@dataclass(frozen=True)
class Blocking:
    categories: frozenset[Category]
    severities: frozenset[str]
    corroboration: int


@dataclass(frozen=True)
class Mechanical:
    categories: frozenset[Category]
    tools: frozenset[str]


@dataclass(frozen=True)
class RemediationPolicy:
    allow_forks: bool


@dataclass(frozen=True)
class Policy:
    version: str
    obligations: tuple[Obligation, ...]
    blocking: Blocking
    mechanical: Mechanical
    assurance: Mapping[str, int]
    remediation: RemediationPolicy


@dataclass(frozen=True)
class Budget:
    per_pr_tokens: int | None
    per_repo_daily_tokens: int | None
    per_model_daily_tokens: int | None


@dataclass(frozen=True)
class Snapshot:
    hash: str
    repo: str
    protocol_hash: str
    authority: Mapping[Activity, bool]
    routes: tuple[Route, ...]
    external: External
    policy: Policy
    budget: Budget


# --------------------------------------------------------------------------
# §4. GitHub types (owner P-09)
# --------------------------------------------------------------------------


class CheckConclusion(str, Enum):
    SUCCESS = "success"
    FAILURE = "failure"
    NEUTRAL = "neutral"
    CANCELLED = "cancelled"
    SKIPPED = "skipped"
    TIMED_OUT = "timed_out"
    ACTION_REQUIRED = "action_required"
    PENDING = "pending"


# attribution and blocking
FAILING: frozenset[CheckConclusion] = frozenset(
    {CheckConclusion.FAILURE, CheckConclusion.TIMED_OUT, CheckConclusion.ACTION_REQUIRED}
)
# never corroborates/blocks/inherits
UNSETTLED: frozenset[CheckConclusion] = frozenset({CheckConclusion.PENDING})
PASSING: frozenset[CheckConclusion] = frozenset(
    {
        CheckConclusion.SUCCESS,
        CheckConclusion.NEUTRAL,
        CheckConclusion.SKIPPED,
        CheckConclusion.CANCELLED,
    }
)


@dataclass(frozen=True)
class CheckRun:
    name: str
    conclusion: CheckConclusion
    sha: str
    observed_at: datetime  # provider completed_at; capture time only for unsettled checks


@dataclass(frozen=True)
class SubmittedReview:
    id: str
    actor: str
    outcome: Literal["approved", "changes_requested"]
    head_sha: str
    submitted_at: datetime


@dataclass(frozen=True)
class PrFacts:
    repo: str
    number: int
    head_sha: str
    base_sha: str
    merge_base_sha: str
    head_repo: str
    head_ref: str
    head_protected: bool
    author: str
    labels: frozenset[str]
    title: str
    body: str


@dataclass(frozen=True)
class Facts:
    pr: PrFacts
    diff: str  # base/merge-base to current head
    changed_paths: frozenset[str]  # all current PR paths
    revision_changed_paths: frozenset[str]  # predecessor head to current head; E-05 invalidation only
    files: Mapping[str, bytes]
    checks: tuple[CheckRun, ...]
    base_checks: tuple[CheckRun, ...]
    reviews: tuple[SubmittedReview, ...]
    fetched_at: datetime  # coherent GitHub-fact capture time; NOT the evidence cutoff


@dataclass(frozen=True)
class Mutation:
    id: str
    kind: str
    accepted: bool


@dataclass(frozen=True)
class Stale:
    reason: Literal["head_changed", "pr_closed"]
    observed_head_sha: str


@dataclass(frozen=True)
class LeaseTaken:
    login: str


@dataclass(frozen=True)
class GithubUnavailable:
    op: str
    reason: Literal["unreachable", "rate_limited", "graphql_error", "malformed",
                    "incomplete", "not_found", "page_cap_exceeded", "unauthenticated"]
    retriable: bool


@dataclass(frozen=True)
class CapabilityReading:
    capabilities: frozenset[str]
    attested_not_proven: frozenset[str]
    login: str


# --------------------------------------------------------------------------
# §5. Supply and harness types (owners P-05, P-06)
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class Route:
    harness: str
    model: str
    provider: str
    family: str
    external: bool
    command: tuple[str, ...] | None = None  # operator-declared argv for a harness RQA does not
    #                                         ship an alias for; None means a built-in alias.
    #                                         RQA-FR-030: a conforming harness participates
    #                                         through configuration, never a source edit.


@dataclass(frozen=True)
class RouteCursor:
    excluded_families: frozenset[str]
    excluded_routes: frozenset[Route]


@dataclass(frozen=True)
class Reservation:
    id: str
    tokens: int


@dataclass(frozen=True)
class Refusal:
    downgrade: Literal["fallback", "incomplete", "escalate"]
    axis: str


@dataclass(frozen=True)
class RouteUnavailable:
    no_fallback: bool
    tried: tuple[Route, ...]


@dataclass(frozen=True)
class Spend:
    tokens: int
    measured: bool
    source: Literal["harness", "reservation"]


@dataclass(frozen=True)
class Plan:
    obligations: tuple[str, ...]
    omitted: Mapping[str, str]
    strategy: str
    participants: int
    risk_class: str
    head_sha: str
    snapshot_hash: str
    protocol_hash: str
    policy_version: str


@dataclass(frozen=True)
class Attestation:
    harness: str
    model: str
    provider: str
    route: Route
    effort: str
    started_at: datetime
    ended_at: datetime
    exit_code: int


@dataclass(frozen=True)
class AttemptFailure:
    kind: Literal["TRANSIENT", "PROVIDER_TERMINAL", "CANDIDATE_TERMINAL"]
    detail: str


@dataclass(frozen=True)
class Attempt:
    id: str
    route: Route
    outcome: Verdict | AttemptFailure
    attestation: Attestation


@dataclass(frozen=True)
class PanelResult:
    attempts: tuple[Attempt, ...]
    complete: bool
    incomplete_reason: str | None  # when not complete: exhausted | budget | bundle
    evidence_cutoff: datetime  # captured after the final attempt and recorded with the panel
    bound_reached: bool  # any reservation was refused at a configured bound during this
    #                      run, including one that then took a configured fallback.
    #                      RQA-FR-039: such a run never ends in a successful disposition.


@dataclass(frozen=True)
class BundleFailure:
    reason: str


# --------------------------------------------------------------------------
# §6. Judgement, escalation, reuse and remediation types
#     (owners P-07, P-11, P-13, P-10)
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class Assurance:
    required: int
    achieved: int


class EscalationCause(str, Enum):
    UNRESOLVED_DECISION = "unresolved_decision"
    CONFLICTING_JUDGEMENT = "conflicting_judgement"
    EVIDENCE_GAP = "evidence_gap"
    REQUIRED_INFORMATION = "required_information"
    AUTHORITY_REQUIREMENT = "authority_requirement"


@dataclass(frozen=True)
class Decision:
    actor: str
    basis: str
    substantiates: str | None
    outcome: Literal["approved", "changes_requested"] | None


@dataclass(frozen=True)
class Escalation:
    id: int
    job_id: str
    cause: EscalationCause
    question: str
    context: Mapping[str, str]
    head_sha: str
    snapshot_hash: str
    entry_seq: int
    raised_at: datetime


@dataclass(frozen=True)
class Judgement:
    obligations: Mapping[str, EvidenceState]
    findings: tuple[Finding, ...]
    corroborated: frozenset[str]
    blocking: frozenset[str]
    attribution: Mapping[str, Literal["pr", "inherited"]]
    assurance: Assurance
    remediation_candidates: tuple[str, ...]
    escalation_causes: tuple[tuple[EscalationCause, str], ...]
    disposition: Literal["approve", "request_changes", "remediate", "escalate"]
    reused_from: str | None


@dataclass(frozen=True)
class CarriedEvidence:
    obligation_id: str
    state: EvidenceState
    source_job: str
    source_judgement_seq: int
    source_attestations: tuple[str, ...]


@dataclass(frozen=True)
class CarryOver:
    reused: tuple[CarriedEvidence, ...]
    regenerated: tuple[str, ...]
    reasons: Mapping[str, str]
    source_job: str | None


class RemediationRefusalReason(str, Enum):
    REMEDY_MISSING = "remedy_missing"
    TOOL_NOT_IN_SET = "tool_not_in_set"
    CHECK_NOT_IN_SET = "check_not_in_set"
    HEAD_PROTECTED = "head_protected"
    FORK_NOT_ALLOWED = "fork_not_allowed"
    INVALID_PATH = "invalid_path"
    NO_HEAD = "no_head"
    TOOL_UNAVAILABLE = "tool_unavailable"
    TOOL_FAILED = "tool_failed"
    SCOPE_EXCEEDED = "scope_exceeded"
    BEHAVIOUR_CHANGED = "behaviour_changed"
    CHECK_STILL_FAILING = "check_still_failing"
    NOT_FIXPOINT = "not_fixpoint"
    COMMIT_FAILED = "commit_failed"
    PUSH_REJECTED = "push_rejected"


@dataclass(frozen=True)
class RemediationPushed:
    new_head_sha: str
    tool_id: str
    entry_seq: int


@dataclass(frozen=True)
class RemediationRefused:
    reason: RemediationRefusalReason
    detail: str
    entry_seq: int


class EscalationRefusalReason(str, Enum):
    NOT_FOUND = "not_found"
    ALREADY_CLOSED = "already_closed"
    HEAD_MOVED = "head_moved"
    SNAPSHOT_MOVED = "snapshot_moved"


@dataclass(frozen=True)
class EscalationRefused:
    reason: EscalationRefusalReason
    detail: str


# --------------------------------------------------------------------------
# §7. Record types (owner P-12)
# --------------------------------------------------------------------------


EntryKind = Literal[
    "transition", "plan", "carry_over", "bundle", "attestation", "spend", "panel",
    "judgement", "grant", "action", "escalation", "decision", "snapshot", "legacy",
]
ENTRY_KINDS: frozenset[EntryKind] = frozenset(get_args(EntryKind))


@dataclass(frozen=True)
class Entry:
    seq: int
    hash: str


class AppendFailed(Exception):
    """The record could not be appended. Always propagates; never a recorded outcome."""


class RecordWriter(Protocol):
    def append(self, job_id: str, kind: EntryKind, payload: Mapping) -> Entry: ...


@dataclass(frozen=True)
class RecordRow:
    seq: int
    kind: EntryKind
    at: datetime
    payload: Mapping


class RecordTrustFailureReason(str, Enum):
    MISSING = "missing"
    INTEGRITY_BREAK = "integrity_break"
    UNVERIFIABLE = "unverifiable"
    LEGACY = "legacy"


@dataclass(frozen=True)
class RecordUntrusted:
    reason: RecordTrustFailureReason
    detail: str


@dataclass(frozen=True)
class VerifiedRecordPrefix:
    job_id: str
    rows: tuple[RecordRow, ...]
    checked_through_seq: int

    def latest(self, kind: EntryKind) -> RecordRow | None:
        """The last row of `kind`, searching only this prefix's immutable `rows`
        (`code/P-12-record.md` §2). None when the prefix holds no row of that kind."""
        for row in reversed(self.rows):
            if row.kind == kind:
                return row
        return None


class RecordReader(Protocol):
    def entries(self, job_id: str, kind: EntryKind | None = None) -> tuple[RecordRow, ...]: ...
    def latest(self, job_id: str, kind: EntryKind) -> RecordRow | None: ...
    def trusted_prefix(self, job_id: str) -> VerifiedRecordPrefix | RecordUntrusted: ...


# --------------------------------------------------------------------------
# §8. Authority and boundary types (owners P-08, P-10, P-12)
# --------------------------------------------------------------------------


class DenyReason(str, Enum):
    NOT_ENABLED = "not_enabled"
    NO_SNAPSHOT = "no_snapshot"
    CAPABILITY_MISSING = "capability_missing"
    CATEGORY_NOT_MECHANICAL = "category_not_mechanical"
    TOOL_NOT_IN_SET = "tool_not_in_set"
    CATEGORY_REQUIRED = "category_required"
    REPO_NOT_MANAGED = "repo_not_managed"


@dataclass(frozen=True)
class Grant:
    activity: Activity
    repo: str
    job_id: str
    snapshot_hash: str
    capability_proof_id: int
    categories: frozenset[Category] | None
    entry_seq: int


@dataclass(frozen=True)
class Deny:
    activity: Activity
    repo: str
    job_id: str
    reason: DenyReason
    detail: str
    entry_seq: int


@dataclass(frozen=True)
class ProcessResult:
    returncode: int
    stdout: bytes
    stderr: bytes


@dataclass(frozen=True)
class ExplanationUnavailable:
    repo: str
    number: int
    reason: Literal["no_record", "ambiguous_head"]
