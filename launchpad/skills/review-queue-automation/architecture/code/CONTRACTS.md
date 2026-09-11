# Shared contracts — the seam truth

Every cross-part call in RQA has exactly one signature, and it is here. Every value that crosses a
part boundary has exactly one definition here, including domain-specific unavailability and refusal
types; no generic result name is shared by unrelated edges. A part contract (`P-NN-*.md`) may add
fields only to types that never cross a part boundary. It may not redefine, rename, reorder or retype
anything in this file. Where a part contract and this file disagree, this file is right and the part
contract is a defect. `../validate.py` checks that every signature below appears in its provider and
consumers and that no part contract defines a type named here.

Conventions: Python 3.12; every function keyword-only; every value type a frozen dataclass; policy,
availability and budget outcomes are values, programming errors are `*Error` exceptions;
`AppendFailed` always propagates. `Mapping` and `Sequence` are `collections.abc`.

---

## 1. Identity and status

```python
class Activity(str, Enum):                                  # P-08
    REVIEW = "review"; COMMENT = "comment"; APPROVE = "approve"
    REQUEST_CHANGES = "request_changes"; REMEDIATE = "remediate"; MERGE = "merge"

class JobStatus(str, Enum):                                 # P-02
    QUEUED = "queued"; CLAIMED = "claimed"; PLANNED = "planned"; REVIEWING = "reviewing"
    JUDGED = "judged"; REMEDIATING = "remediating"; ESCALATED = "escalated"
    SUBMITTING = "submitting"; CHANGES_REQUESTED = "changes_requested"; APPROVED = "approved"
    MERGED = "merged"; STOPPED = "stopped"; SUPERSEDED = "superseded"

@dataclass(frozen=True)
class Job:                                                  # P-01
    id: str                      # stable_hash(repo, number, head_sha)
    repo: str                    # "owner/name" of the managed (base) repository
    number: int
    head_sha: str
    base_sha: str
    head_repo: str               # "owner/name" the PR head lives in; == repo unless a fork
    head_ref: str                # branch name of the PR head in head_repo
    predecessor_job: str | None
    predecessor_head_sha: str | None # exact predecessor revision used for E-23 revision compare
    snapshot_hash: str | None
    status: JobStatus
```

## 2. Protocol types (owner P-04)

```python
class EvidenceState(str, Enum):
    VERIFIED = "verified"; NOT_VERIFIED = "not_verified"; UNAVAILABLE = "unavailable"
    CONTRADICTORY = "contradictory"; FAILED = "failed"; INCOMPLETE = "incomplete"; UNKNOWN = "unknown"

class Category(str, Enum):
    MECHANICAL = "mechanical"; PROCEDURAL = "procedural"; CREATION_TIME = "creation_time"
    CORRECTNESS = "correctness"; SECURITY = "security"; ARCHITECTURAL = "architectural"; EVIDENCE = "evidence"

MECHANICAL_GROUP: frozenset[Category] = {MECHANICAL, PROCEDURAL, CREATION_TIME}
SUBSTANTIVE_GROUP: frozenset[Category] = {CORRECTNESS, SECURITY, ARCHITECTURAL, EVIDENCE}

@dataclass(frozen=True)
class Location:
    path: str
    line: int | None

@dataclass(frozen=True)
class Remedy:
    """An exact, scoped remedy. Only findings carrying one can become remediation candidates.
    [ADR-G assumed]"""
    tool: str                    # a MECHANICAL_TOOL_SET id
    paths: tuple[str, ...]       # exact normalized repository-relative files; non-empty, unique,
                                 # no glob metacharacters, absolute path, "." or ".." segment
    check: str                   # the check name that must pass after the fix

@dataclass(frozen=True)
class Finding:
    id: str
    categories: frozenset[Category]   # non-empty; MUST contain ≥1 from MECHANICAL_GROUP ∪ SUBSTANTIVE_GROUP
    extra_tags: frozenset[str]        # open vocabulary the protocol does not close (e.g. "performance")
    location: Location
    evidence: str                     # non-empty
    severity: str
    remedy: Remedy | None
    behaviour_changing: bool | None   # the reviewer's own assertion; P-07 treats None as True
    source_attempt: str

@dataclass(frozen=True)
class InjectionAttempt:
    field: str                   # body | comment:<id> | diff:<path>
    span_hash: str               # lowercase SHA-256 of the exact untrusted bytes, never their text
    reason: str                  # semantic attempt to alter review/evidence, not phrase matching

@dataclass(frozen=True)
class HarnessIdentity:               # self-reported; recorded, never trusted
    harness: str; model: str; provider: str

@dataclass(frozen=True)
class Verdict:
    obligations: Mapping[str, EvidenceState]
    findings: tuple[Finding, ...]
    injection_attempts: tuple[InjectionAttempt, ...]
    identity: HarnessIdentity
    protocol_version: str

@dataclass(frozen=True)
class Valid: verdict: Verdict
@dataclass(frozen=True)
class Invalid: reasons: tuple[str, ...]

@dataclass(frozen=True)
class Obligation:
    id: str
    paths: tuple[str, ...]           # PathGlob patterns, matched ONLY by rqa.protocol.paths.matches()
    required_for: frozenset[str]     # risk classes
    evidence: str

def matches(path: str, pattern: str) -> bool: ...   # rqa.protocol.paths — the ONLY path matcher in RQA
```

Grammar of `PathGlob`, owned by P-04 and used by P-03 (validation), P-06 (planning), P-10 (scope),
P-13 (invalidation): `*` matches any run of non-`/` characters; `**` matches zero or more complete
segments; `?` one non-`/` character; patterns are anchored at the repository root; matching is
case-sensitive; a leading `.` is an ordinary character. No other matcher (`fnmatch`, `PurePath.match`)
may be used anywhere.

## 3. Policy types (owner P-03)

```python
class ValidationErrorCode(str, Enum):
    UNREADABLE = "unreadable"; MISSING_REQUIRED_SECTION = "missing_required_section"
    MISSING_POLICY = "missing_policy"; UNKNOWN_KEY = "unknown_key"
    UNKNOWN_AUTHORITY_KEY = "unknown_authority_key"; TOOL_NOT_IN_SET = "tool_not_in_set"
    INVALID_PATH_PATTERN = "invalid_path_pattern"; NEGATIVE_BUDGET = "negative_budget"
    BAD_TYPE = "bad_type"

@dataclass(frozen=True)
class ValidationError:
    code: ValidationErrorCode; path: str; detail: str
@dataclass(frozen=True)
class ValidationFailure:
    repo: str; errors: tuple[ValidationError, ...]

@dataclass(frozen=True)
class External: allowed: bool; deny_label: str
@dataclass(frozen=True)
class Blocking: categories: frozenset[Category]; severities: frozenset[str]; corroboration: int
@dataclass(frozen=True)
class Mechanical: categories: frozenset[Category]; tools: frozenset[str]
@dataclass(frozen=True)
class RemediationPolicy: allow_forks: bool
@dataclass(frozen=True)
class Policy:
    version: str; obligations: tuple[Obligation, ...]; blocking: Blocking
    mechanical: Mechanical; assurance: Mapping[str, int]; remediation: RemediationPolicy
@dataclass(frozen=True)
class Budget:
    per_pr_tokens: int | None; per_repo_daily_tokens: int | None; per_model_daily_tokens: int | None

@dataclass(frozen=True)
class Snapshot:
    hash: str; repo: str; protocol_hash: str
    authority: Mapping[Activity, bool]
    routes: tuple[Route, ...]
    external: External
    policy: Policy
    budget: Budget
```

## 4. GitHub types (owner P-09)

```python
class CheckConclusion(str, Enum):
    SUCCESS = "success"; FAILURE = "failure"; NEUTRAL = "neutral"; CANCELLED = "cancelled"
    SKIPPED = "skipped"; TIMED_OUT = "timed_out"; ACTION_REQUIRED = "action_required"; PENDING = "pending"

FAILING: frozenset[CheckConclusion] = {FAILURE, TIMED_OUT, ACTION_REQUIRED}    # attribution and blocking
UNSETTLED: frozenset[CheckConclusion] = {PENDING}                             # never corroborates/blocks/inherits
PASSING: frozenset[CheckConclusion] = {SUCCESS, NEUTRAL, SKIPPED, CANCELLED}

@dataclass(frozen=True)
class CheckRun:
    name: str; conclusion: CheckConclusion; sha: str
    observed_at: datetime             # provider completed_at; capture time only for unsettled checks

@dataclass(frozen=True)
class SubmittedReview:
    id: str; actor: str
    outcome: Literal["approved", "changes_requested"]
    head_sha: str; submitted_at: datetime

@dataclass(frozen=True)
class PrFacts:
    repo: str; number: int; head_sha: str; base_sha: str; merge_base_sha: str
    head_repo: str; head_ref: str
    head_protected: bool
    author: str; labels: frozenset[str]; title: str; body: str

@dataclass(frozen=True)
class Facts:
    pr: PrFacts
    diff: str                           # base/merge-base to current head
    changed_paths: frozenset[str]       # all current PR paths
    revision_changed_paths: frozenset[str] # predecessor head to current head; E-05 invalidation only
    files: Mapping[str, bytes]
    checks: tuple[CheckRun, ...]
    base_checks: tuple[CheckRun, ...]
    reviews: tuple[SubmittedReview, ...]
    fetched_at: datetime             # coherent GitHub-fact capture time; NOT the evidence cutoff

@dataclass(frozen=True)
class Mutation:
    id: str; kind: str; accepted: bool
@dataclass(frozen=True)
class Stale:
    reason: Literal["head_changed", "pr_closed"]; observed_head_sha: str
@dataclass(frozen=True)
class LeaseTaken: login: str
@dataclass(frozen=True)
class GithubUnavailable:
    op: str
    reason: Literal["unreachable", "rate_limited", "graphql_error", "malformed",
                    "incomplete", "not_found", "page_cap_exceeded", "unauthenticated"]
    retriable: bool
@dataclass(frozen=True)
class CapabilityReading:
    capabilities: frozenset[str]; attested_not_proven: frozenset[str]; login: str
```

## 5. Supply and harness types (owners P-05, P-06)

```python
@dataclass(frozen=True)
class Route:
    harness: str; model: str; provider: str; family: str; external: bool
    command: tuple[str, ...] | None = None   # operator-declared argv for a harness RQA does not
                                             # ship an alias for; None means a built-in alias.
                                             # RQA-FR-030: a conforming harness participates
                                             # through configuration, never a source edit.

@dataclass(frozen=True)
class RouteCursor:
    excluded_families: frozenset[str]
    excluded_routes: frozenset[Route]

@dataclass(frozen=True)
class Reservation: id: str; tokens: int
@dataclass(frozen=True)
class Refusal: downgrade: Literal["fallback", "incomplete", "escalate"]; axis: str
@dataclass(frozen=True)
class RouteUnavailable: no_fallback: bool; tried: tuple[Route, ...]
@dataclass(frozen=True)
class Spend: tokens: int; measured: bool; source: Literal["harness", "reservation"]

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
    harness: str; model: str; provider: str; route: Route; effort: str
    started_at: datetime; ended_at: datetime; exit_code: int

@dataclass(frozen=True)
class AttemptFailure:
    kind: Literal["TRANSIENT", "PROVIDER_TERMINAL", "CANDIDATE_TERMINAL"]; detail: str

@dataclass(frozen=True)
class Attempt:
    id: str; route: Route; outcome: Verdict | AttemptFailure; attestation: Attestation

@dataclass(frozen=True)
class PanelResult:
    attempts: tuple[Attempt, ...]
    complete: bool
    incomplete_reason: str | None    # when not complete: exhausted | budget | bundle
    evidence_cutoff: datetime        # captured after the final attempt and recorded with the panel
    bound_reached: bool              # any reservation was refused at a configured bound during this
                                     # run, including one that then took a configured fallback.
                                     # RQA-FR-039: such a run never ends in a successful disposition.

@dataclass(frozen=True)
class BundleFailure:
    reason: str
```

## 6. Judgement, escalation, reuse and remediation types (owners P-07, P-11, P-13, P-10)

```python
@dataclass(frozen=True)
class Assurance: required: int; achieved: int

class EscalationCause(str, Enum):
    UNRESOLVED_DECISION = "unresolved_decision"; CONFLICTING_JUDGEMENT = "conflicting_judgement"
    EVIDENCE_GAP = "evidence_gap"; REQUIRED_INFORMATION = "required_information"
    AUTHORITY_REQUIREMENT = "authority_requirement"

@dataclass(frozen=True)
class Decision:
    actor: str; basis: str
    substantiates: str | None
    outcome: Literal["approved", "changes_requested"] | None

@dataclass(frozen=True)
class Escalation:
    id: int; job_id: str; cause: EscalationCause; question: str; context: Mapping[str, str]
    head_sha: str; snapshot_hash: str; entry_seq: int; raised_at: datetime

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
    REMEDY_MISSING = "remedy_missing"; TOOL_NOT_IN_SET = "tool_not_in_set"
    CHECK_NOT_IN_SET = "check_not_in_set"; HEAD_PROTECTED = "head_protected"
    FORK_NOT_ALLOWED = "fork_not_allowed"; INVALID_PATH = "invalid_path"
    NO_HEAD = "no_head"; TOOL_UNAVAILABLE = "tool_unavailable"; TOOL_FAILED = "tool_failed"
    SCOPE_EXCEEDED = "scope_exceeded"; BEHAVIOUR_CHANGED = "behaviour_changed"
    CHECK_STILL_FAILING = "check_still_failing"; NOT_FIXPOINT = "not_fixpoint"
    COMMIT_FAILED = "commit_failed"; PUSH_REJECTED = "push_rejected"
@dataclass(frozen=True)
class RemediationPushed:
    new_head_sha: str; tool_id: str; entry_seq: int
@dataclass(frozen=True)
class RemediationRefused:
    reason: RemediationRefusalReason; detail: str; entry_seq: int

class EscalationRefusalReason(str, Enum):
    NOT_FOUND = "not_found"; ALREADY_CLOSED = "already_closed"
    HEAD_MOVED = "head_moved"; SNAPSHOT_MOVED = "snapshot_moved"
@dataclass(frozen=True)
class EscalationRefused:
    reason: EscalationRefusalReason; detail: str
```

## 7. Record types (owner P-12)

```python
EntryKind = Literal[
    "transition", "plan", "carry_over", "bundle", "attestation", "spend", "panel",
    "judgement", "grant", "action", "escalation", "decision", "snapshot", "legacy",
]
ENTRY_KINDS: frozenset[EntryKind]

@dataclass(frozen=True)
class Entry: seq: int; hash: str
class AppendFailed(Exception): ...

class RecordWriter(Protocol):
    def append(self, job_id: str, kind: EntryKind, payload: Mapping) -> Entry: ...

@dataclass(frozen=True)
class RecordRow: seq: int; kind: EntryKind; at: datetime; payload: Mapping

class RecordTrustFailureReason(str, Enum):
    MISSING = "missing"; INTEGRITY_BREAK = "integrity_break"
    UNVERIFIABLE = "unverifiable"; LEGACY = "legacy"
@dataclass(frozen=True)
class RecordUntrusted:
    reason: RecordTrustFailureReason; detail: str
@dataclass(frozen=True)
class VerifiedRecordPrefix:
    job_id: str; rows: tuple[RecordRow, ...]; checked_through_seq: int
    def latest(self, kind: EntryKind) -> RecordRow | None: ...

class RecordReader(Protocol):
    def entries(self, job_id: str, kind: EntryKind | None = None) -> tuple[RecordRow, ...]: ...
    def latest(self, job_id: str, kind: EntryKind) -> RecordRow | None: ...
    def trusted_prefix(self, job_id: str) -> VerifiedRecordPrefix | RecordUntrusted: ...
```

## 8. Authority and boundary types (owners P-08, P-10, P-12)

```python
class DenyReason(str, Enum):
    NOT_ENABLED = "not_enabled"; NO_SNAPSHOT = "no_snapshot"
    CAPABILITY_MISSING = "capability_missing"; CATEGORY_NOT_MECHANICAL = "category_not_mechanical"
    TOOL_NOT_IN_SET = "tool_not_in_set"; CATEGORY_REQUIRED = "category_required"
    REPO_NOT_MANAGED = "repo_not_managed"

@dataclass(frozen=True)
class Grant:
    activity: Activity; repo: str; job_id: str; snapshot_hash: str
    capability_proof_id: int; categories: frozenset[Category] | None; entry_seq: int

@dataclass(frozen=True)
class Deny:
    activity: Activity; repo: str; job_id: str; reason: DenyReason; detail: str; entry_seq: int

@dataclass(frozen=True)
class ProcessResult: returncode: int; stdout: bytes; stderr: bytes

@dataclass(frozen=True)
class ExplanationUnavailable:
    repo: str; number: int; reason: Literal["no_record", "ambiguous_head"]
```

---

## 9. Edge signatures — one per E-NN, verbatim

Provider implements exactly this; consumer calls exactly this. Dependency injection is by
keyword; every provider takes `record: RecordWriter` if it appends.

```python
# E-01  P-09 provides, P-01 consumes
def inventory(*, repo: str) -> tuple[PrFacts, ...] | GithubUnavailable: ...
def claim_lease(*, job: Job, grant: Grant, record: RecordWriter) -> Mutation | LeaseTaken | GithubUnavailable: ...
def release_lease(*, job: Job, grant: Grant, record: RecordWriter) -> Mutation | GithubUnavailable: ...

# E-02  P-02 provides, P-01 consumes
def admit(*, job: Job, deps: LifecycleDeps) -> JobStatus: ...
# LifecycleDeps bundles every neighbour P-02 calls.

# E-03  P-03 provides, P-02 consumes
def snapshot_for(*, repo: str, job: Job | None, store: SnapshotStore,
                 record: RecordWriter | None) -> Snapshot | ValidationFailure: ...

# E-04  P-08 provides, P-02 consumes
def grant(*, repo: str, activity: Activity, snapshot: Snapshot | None, job_id: str,
          categories: frozenset[Category] | None, record: RecordWriter, github: GithubProbe,
          store: CapabilityStore) -> Grant | Deny: ...

# E-05  P-13 provides, P-02 consumes
def carry_over(*, job: Job, prior: RecordReader, facts: Facts, snapshot: Snapshot, record: RecordWriter) -> CarryOver: ...

# E-06  P-05 provides, P-06 consumes (P-02 constructs the cursor; P-06 advances it)
def route(*, job: Job, obligation: str, snapshot: Snapshot, facts: Facts, cursor: RouteCursor,
          prober: HarnessProber, breakers: BreakerStore) -> tuple[Route, RouteCursor] | RouteUnavailable: ...
def reserve(*, job: Job, plan: Plan, route: Route, snapshot: Snapshot, spend: SpendStore) -> Reservation | Refusal: ...

# E-07  P-06 provides, P-02 consumes.  P-06 OWNS the panel loop; P-02 makes exactly one run() call per review.
def plan(*, job: Job, facts: Facts, snapshot: Snapshot, carry: CarryOver, record: RecordWriter) -> Plan: ...
def run(*, job: Job, plan: Plan, facts: Facts, snapshot: Snapshot, supply: SupplyPort, state_dir: Path,
        record: RecordWriter) -> PanelResult | BundleFailure: ...
#   SupplyPort is P-06's view of E-06 + E-15, constructed by P-02 over P-05's functions:
#     route(obligation, cursor) -> tuple[Route, RouteCursor] | RouteUnavailable
#     reserve(plan, route) -> Reservation | Refusal
#     consumed(attempt, reading, reservation) -> Spend

# E-08  P-04 provides, P-06 consumes
def validate(*, path: Path, attempt_id: str) -> Valid | Invalid: ...          # Valid.verdict: Verdict

# E-09  P-07 provides, P-02 consumes
def judge(*, job: Job, plan: Plan, panel: PanelResult, carry: CarryOver, facts: Facts, snapshot: Snapshot,
          decision: Decision | None, record: RecordWriter) -> Judgement: ...
#   `panel.evidence_cutoff` is captured and recorded after the final attempt; no later attestation counts.
#   When panel.attempts is empty and carry.regenerated is empty, judge() materialises the Judgement
#   from carry.reused alone — this is the zero-reviewer-call path, and it still records a `judgement` entry.

# E-10  P-10 provides, P-02 consumes
def remediate(*, job: Job, finding: Finding, grant: Grant, facts: Facts, snapshot: Snapshot,
              state_dir: Path, runner: ProcessRunner, record: RecordWriter) -> RemediationPushed | RemediationRefused: ...

# E-11  P-11 provides, P-02 consumes (reverse edge: P-11 calls P-02.resume)
def raise_(*, job: Job, cause: EscalationCause, question: str, context: Mapping, record: RecordWriter,
           store: EscalationStore) -> Escalation: ...
def pending(*, store: EscalationStore) -> tuple[Escalation, ...]: ...
def resume(*, job_id: str, decision: Decision, deps: LifecycleDeps) -> JobStatus: ...     # P-02 provides

# E-12  P-09 provides, P-02 consumes
def submit_review(*, job: Job, state: Literal["APPROVE", "REQUEST_CHANGES"], body: str, grant: Grant,
                  record: RecordWriter) -> Mutation | Stale | GithubUnavailable: ...
def comment(*, job: Job, body: str, grant: Grant, record: RecordWriter) -> Mutation | GithubUnavailable: ...
def merge(*, job: Job, grant: Grant, record: RecordWriter) -> Mutation | Stale | GithubUnavailable: ...

# E-13  P-12 provides, every part except P-04 consumes
RecordWriter.append(job_id, kind, payload) -> Entry

# E-14  P-09 provides internally to its E-23 fact capture
def checks(*, repo: str, sha: str) -> tuple[CheckRun, ...] | GithubUnavailable: ...

# E-15  P-05 provides, P-06 consumes through SupplyPort
def consumed(*, job: Job, attempt: Attempt, reading: int | None, reservation: Reservation,
             record: RecordWriter, spend: SpendStore, breakers: BreakerStore) -> Spend: ...

# E-16  P-09 provides, P-08 consumes
def probe(*, repo: str, credential: str) -> CapabilityReading | GithubUnavailable: ...

# E-17  CLI: P-02 status; P-12 explain → Explanation | ExplanationUnavailable; P-11 decide/pending; P-03 onboard; P-01 tick

# E-23  P-09 provides, P-02 consumes
def facts(*, job: Job, record: RecordWriter) -> Facts | GithubUnavailable: ...   # one coherent GitHub fact capture

# E-24  P-05 consumes (HarnessProber, implemented in P-06 over the same invoke() as E-19)
class HarnessProber(Protocol):
    def probe(self, route: Route, *, timeout: float) -> bool: ...

# E-18  P-09 → GitHub: HTTPS REST v3 / GraphQL v4 with the operator's `gh auth token`; the only HTTP client import in RQA
# E-20  P-10 → GitHub: `git fetch <sha>` and `git push <remote> HEAD:refs/heads/<head_ref>` over smart HTTP; never `--force`
# E-21  OS scheduler → P-01: process launch `rqa tick`; no payload
# E-22  P-08 → GitHub CLI: process execution `gh auth token`; value held in memory for one probe, never persisted

# E-25  P-12 consumes — the OS keychain (ADR-F key)          NEW: surfaced by review
class KeyStore(Protocol):
    def read(self, name: str) -> bytes | None: ...            # None: key absent → verify/explain report unverifiable, append proceeds unkeyed and says so

# E-26  P-10 consumes — local tool processes (MECHANICAL_TOOL_SET binaries)   NEW: surfaced by review
class ProcessRunner(Protocol):
    def run(self, *, cwd: Path, argv: tuple[str, ...], timeout: float) -> ProcessResult: ...
```

## 10. Ownership of the review loop — decided

**P-06 owns the panel loop.** `run()` is called once per review by P-02 and returns the whole
`PanelResult`. Inside it, P-06 asks `SupplyPort.route(obligation, cursor)` for a candidate, obtains a
fresh reservation immediately before **every** harness invocation (including the one permitted
same-route transient retry), invokes the harness, validates through E-08, reports `consumed`, and
advances the cursor on every terminal failure or refusal. A retry whose fresh reservation is refused
uses the same refusal branches as an initial reservation. P-02 sees only the `PanelResult` and decides
the transition. A `Refusal(downgrade="fallback")` grows `excluded_families` before P-06 asks again;
the finite route set, the one-retry transient bound and monotonic cursor make the loop finite.

**P-13 does not judge; P-07 judges reused evidence.** `carry_over` returns `CarriedEvidence` with
the source judgement seq and attestation ids; `judge()` receives `carry` and treats every reused
obligation as `VERIFIED` with provenance pointing at the predecessor. When nothing was regenerated,
`judge()` still runs, still records a `judgement` entry (with `reused_from` set), and P-02 proceeds
to step 9 with a real `Judgement`. The zero-reviewer-call proof is the `judgement` entry's
`reused_from` plus the absence of any `attestation` entry on this job — both positive facts in this
job's record.

**Remediation pushes to the PR head, wherever it lives.** `Job.head_repo`/`head_ref` come from
`PrFacts`. P-10 receives the pinned `Snapshot`, refuses before worktree creation when
`head_repo != job.repo` and `snapshot.policy.remediation.allow_forks` is false, and refuses a
protected or unreadable-protection head. It fetches the exact head SHA from `head_repo` and pushes
only `HEAD:refs/heads/<head_ref>`. `Remedy.paths` are exact normalized files, never patterns or
directories; P-10 resolves every one beneath the worktree before invoking a tool and refuses if the
post-tool changed-path set is not a subset of those exact files.

## 11. Category and mechanical classification — decided

`Finding.categories` is a non-empty set; the protocol requires at least one from the two named
groups and leaves `extra_tags` open. P-07 may select a **remediation candidate** only when
`categories ⊆ MECHANICAL_GROUP`, `remedy is not None`, its exact paths are present in the captured
files, its tool and categories are allowed by the snapshot, and `behaviour_changing is False`.
That model-supplied Boolean is only a conservative veto; it never proves neutrality. Before P-10 may
commit or push, the closed `ToolSpec` must run its language-specific behavior-equivalence check over
every changed file and prove the actual before/after pair equivalent. No sound equivalence check means
the tool is not in `MECHANICAL_TOOL_SET`; a failed check is `RemediationRefused(BEHAVIOUR_CHANGED)`.
Policy cannot weaken that test. A substantive category is never a candidate, and a finding blocks when
any category blocks under policy.

## 12. Untrusted content — decided

The guarantee is an E-19 behavioral contract, not delimiter folklore:

1. Every adapter uses its provider's instruction/data roles: RQA's immutable review protocol is the
   only instruction; every PR byte is nonce-enveloped and presented only through the data channel.
   An adapter without a role-separated data channel is not conforming and cannot be registered.
2. `Verdict.injection_attempts` is mandatory. The harness semantically identifies PR text intended to
   alter the review outcome or fabricate evidence and returns each exact field/span hash and reason;
   P-07 deterministically converts every item into a blocking `EVIDENCE` finding before authority or
   repository policy is considered. Envelope breakage is another such finding.
3. Every adapter must pass the published injection conformance suite before release. For paired clean
   and adversarial inputs spanning diff, body and comments, including semantic paraphrases absent from
   any fixture vocabulary, the non-defensive obligations/findings/evidence must be identical, while
   the adversarial case must add a blocking injection finding. The suite runs every authority mode,
   including advisory-only. A failed pair rejects the adapter; there is no runtime route qualification.
4. At runtime, a touched obligation reported wholly `VERIFIED` with no finding is additionally a
   `suspicious_clean_verdict` blocking finding requiring a second family. This is defense in depth,
   not the mechanism that discharges the paired behavioral property.

No phrase list or model self-attestation establishes compliance. Following PR content, omitting an
`InjectionAttempt`, or changing evidence under a paired adversarial input is an E-19 contract defect,
not an accepted residual.
