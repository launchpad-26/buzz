# P-02 Lifecycle — code-level contract

This is the implementation contract for one part of the design in
[`../architecture.md`](../architecture.md). An agent implementing P-02 builds exactly what is here;
an agent implementing a neighbour calls exactly what is here. Anything not stated is the implementer's
choice, provided the stated shape, behaviour and tests hold. Contract ids (`E-NN`) and record names
are those of [`../components.md`](../components.md) §6 and [`../container.md`](../container.md) §5.

**Responsibility, in one sentence.** Be the only part that changes a job's state, own the closed
transition table and the mapping to `rqa status`'s six dispositions, contain every persistence
failure into a safe stop, and drive one job through flow steps 3–13 by calling its neighbours and
never deciding what their answers mean beyond the transition those answers license.

**Depends on.** ADR-D ([#2157](https://github.com/launchpad-26/buzz/issues/2157), assumed): steps
10a/12b use its no-verdict-authority outcome. No neighbour implementation is imported; dependency
protocols and shared `CONTRACTS.md` values define every seam.

## 1. Modules

```
rqa/lifecycle/
  __init__.py    re-exports: admit, resume, status, transition, JobStatus, TRANSITIONS,
                 Disposition, DISPOSITION, StatusReport, NotFound, StaleDecisionError,
                 LifecycleError, IllegalTransitionError, UnknownJobError
  states.py      imports shared JobStatus and defines TRANSITIONS, Disposition and DISPOSITION
  errors.py      LifecycleError and its subclasses; never a policy or availability outcome
  deps.py        LifecycleDeps and neighbour Protocols; no shared value-type redefinitions
  transition.py  transition(): the one function that writes `jobs.status` and a `transition`
                 entry atomically, and the AppendFailed → safe-stop fallback
  rest.py        the shared "entering a resting status" check every rest-capable status runs:
                 supersession by a successor job, and releasing an orphaned lease
  steps.py       step3 .. step13: one function per flow step, plus the dispatch table admit()
                 and resume() both drive
  admit.py       admit(): E-02
  resume.py      resume(): the E-11 reverse edge, steps 12a/12b
  status.py      status(): E-17
```

No other module in RQA imports from `rqa.lifecycle` except through `__init__`. No module in
`rqa.lifecycle` imports from another part's package, reads `snapshots`, `capabilities`, `spend`,
`breakers`, `mutations`, `etags`, `api_calls`, `human_requests`'s row content (only its existence is
read, per §5), or any table `container.md` §5 assigns to a different owner, except the three tables
named in §5 below (`jobs`, `pr_facts`, `leases` — read-only, owned by P-01; `record_entries` —
read-only, owned by P-12) and the one column this part writes (`jobs.status`). This is deliberate:
`architecture.md` §15 names this the largest, most safety-critical part precisely because it
concentrates every transition, recovery and degradation rule; keeping its import graph to "the
Contract's shared types plus `rqa.record`'s three names" is what makes "one part is one proof" true
rather than aspirational.

## 2. Types

`JobStatus` is the shared type in [`CONTRACTS.md`](CONTRACTS.md) §1. Every value P-02 exchanges —
including `GithubUnavailable`, `RouteUnavailable`, `BundleFailure`, `RemediationPushed` and
`RemediationRefused` — is imported from `CONTRACTS.md` and never redefined here. P-02-local types
are limited to its dependency bundle, transition/disposition mappings, reports and programming
errors.

`TRANSITIONS`, `Disposition`, `DISPOSITION`, `StatusReport`, `NotFound`, `StaleDecisionError`,
`LifecycleError`, `IllegalTransitionError`, and `UnknownJobError` remain P-02-local types. The
closed `TRANSITIONS` and `DISPOSITION` mappings below use the `JobStatus` of `CONTRACTS.md` §1.

```python
# states.py — JobStatus is imported from CONTRACTS.md §1.
TRANSITIONS: Mapping[JobStatus, frozenset[JobStatus]] = {
    JobStatus.QUEUED: frozenset({JobStatus.CLAIMED, JobStatus.ESCALATED, JobStatus.SUPERSEDED}),
    JobStatus.CLAIMED: frozenset({JobStatus.PLANNED, JobStatus.ESCALATED, JobStatus.STOPPED, JobStatus.SUPERSEDED}),
    JobStatus.PLANNED: frozenset({JobStatus.REVIEWING, JobStatus.JUDGED, JobStatus.ESCALATED, JobStatus.STOPPED}),
    JobStatus.REVIEWING: frozenset({JobStatus.JUDGED, JobStatus.ESCALATED, JobStatus.STOPPED}),
    JobStatus.JUDGED: frozenset({JobStatus.REMEDIATING, JobStatus.ESCALATED, JobStatus.SUBMITTING, JobStatus.STOPPED}),
    JobStatus.REMEDIATING: frozenset({JobStatus.SUPERSEDED, JobStatus.ESCALATED, JobStatus.STOPPED}),
    JobStatus.ESCALATED: frozenset({JobStatus.JUDGED, JobStatus.APPROVED, JobStatus.CHANGES_REQUESTED, JobStatus.STOPPED, JobStatus.SUPERSEDED}),
    JobStatus.SUBMITTING: frozenset({JobStatus.CHANGES_REQUESTED, JobStatus.APPROVED, JobStatus.ESCALATED, JobStatus.STOPPED}),
    JobStatus.CHANGES_REQUESTED: frozenset({JobStatus.SUPERSEDED}),
    JobStatus.APPROVED: frozenset({JobStatus.MERGED, JobStatus.SUPERSEDED}),
    JobStatus.MERGED: frozenset(), JobStatus.STOPPED: frozenset({JobStatus.CLAIMED, JobStatus.SUPERSEDED}),
    JobStatus.SUPERSEDED: frozenset(),
}

class Disposition(str, Enum):
    BEING_REVIEWED = "being reviewed"; AWAITING_REMEDIATION = "awaiting remediation"
    AWAITING_HUMAN_JUDGEMENT = "awaiting human judgement"; BLOCKED = "blocked"
    REVIEW_COMPLETE = "review-complete"; UNABLE_TO_PROGRESS = "unable to progress"

DISPOSITION: Mapping[JobStatus, Disposition] = {
    JobStatus.QUEUED: Disposition.BEING_REVIEWED, JobStatus.CLAIMED: Disposition.BEING_REVIEWED,
    JobStatus.PLANNED: Disposition.BEING_REVIEWED, JobStatus.REVIEWING: Disposition.BEING_REVIEWED,
    JobStatus.JUDGED: Disposition.BEING_REVIEWED, JobStatus.SUBMITTING: Disposition.BEING_REVIEWED,
    JobStatus.REMEDIATING: Disposition.AWAITING_REMEDIATION,
    JobStatus.ESCALATED: Disposition.AWAITING_HUMAN_JUDGEMENT,
    JobStatus.CHANGES_REQUESTED: Disposition.BLOCKED, JobStatus.APPROVED: Disposition.REVIEW_COMPLETE,
    JobStatus.MERGED: Disposition.REVIEW_COMPLETE, JobStatus.STOPPED: Disposition.UNABLE_TO_PROGRESS,
}

@dataclass(frozen=True)
class LifecycleDeps:
    policy: PolicyClient
    authority: AuthorityClient
    supply: SupplyClient
    harness: HarnessClient
    judgement: JudgementClient
    remediation: RemediationClient
    escalation: EscalationClient
    github: GithubClient
    reuse: ReuseClient
    record: RecordWriter
    connection: sqlite3.Connection
    state_dir: Path
    runner: ProcessRunner
    # P-01-owned E-01 callbacks; result types are P-09's, never defined by P-02.
    claim_lease: Callable[..., Mutation | LeaseTaken | GithubUnavailable]
    release_lease: Callable[..., Mutation | GithubUnavailable]
```

`LifecycleDeps` is P-02's dependency bundle, constructed by P-01. `runner` is the E-26
`ProcessRunner` that E-10 requires; it is carried with the state-directory execution context and is
not a second remediation API. The contained clients are the only way P-02 reaches another part.

```python
@dataclass(frozen=True)
class StatusReport:
    job_id: str; internal_state: JobStatus; disposition: Disposition; reason: str
@dataclass(frozen=True)
class NotFound: repo: str; number: int
class LifecycleError(Exception): ...
class StaleDecisionError(LifecycleError): ...
class IllegalTransitionError(LifecycleError): ...
class UnknownJobError(LifecycleError): ...
```

## 3. Entry point(s)

### 3.1 `admit` — E-02

```python
def admit(*, job: Job, deps: LifecycleDeps) -> JobStatus: ...
```

This is E-02 verbatim. It writes the arrival `queued` transition when necessary, then drives the
state machine until a resting status. Persistence failures are contained exactly as before: an
`AppendFailed`, `sqlite3.Error`, or `OSError` causes one `STOPPED` transition and return; failure
while committing that stop propagates. Neighbour `*Error` exceptions propagate. No branch silently
falls through.

The per-admission context is `(snapshot, facts, carry, plan, panel, judgement)`. Step 4 obtains
`facts` **once**, by the verbatim E-23 call:

```python
facts = deps.github.facts(job=job, record=deps.record)
```

`Facts` is retained for one admission cascade and passed unchanged to E-05, E-07, E-09 and E-10.
Its `fetched_at` is GitHub fact-capture time, not the cutoff. P-06 records the fresh-panel cutoff
after its final attempt; a later human resume may capture newer GitHub facts for the same pinned head
without changing the recorded attempt cutoff.

### 3.2 Flow steps 3–13

The dispatch table is `queued → 3/4`, `claimed → 5`, `planned → 6/7/8`, `reviewing → 8`,
`judged → 9/10`, `submitting → submit`, and `approved → 11`. `remediating`, `escalated`,
`changes_requested`, `merged`, `stopped`, and `superseded` rest. Before a rest-capable state is
returned, the existing successor/lease recovery check runs; a successor gives `SUPERSEDED`, and an
orphaned lease is released only under a fresh review `Grant`. That recovery uses the pinned snapshot,
never a replacement snapshot.

#### Steps 3–5 — snapshot, claim, carry-over and plan
1. Step 3 calls E-03 and E-04 with their `CONTRACTS.md` §9 keyword-only signatures. A
   `ValidationFailure` or `Deny` records an authority-requirement escalation and transitions to
   `ESCALATED`. With a review `Grant`, P-02 calls the P-01-supplied E-01 callback exactly:
   `deps.claim_lease(job=job, grant=grant, record=deps.record)`. An accepted `Mutation` transitions
   to `CLAIMED`; `LeaseTaken` returns the unchanged `QUEUED` job; `GithubUnavailable` transitions to
   `STOPPED`. These are all its result branches.
2. At claim, call E-23 once as above. `GithubUnavailable` is a value: transition to `STOPPED` with
   `"facts unavailable"`; it never reaches a success state.
3. Step 5 obtains `carry`. With a predecessor it calls E-05 exactly:

   ```python
   carry = deps.reuse.carry_over(
       job=job, prior=read_prior_record(job=job, connection=deps.connection), facts=facts,
       snapshot=snapshot, record=deps.record,
   )
   ```

   Without a predecessor it starts with empty `CarryOver`. In either case it calls E-07 exactly:

   ```python
   plan = deps.harness.plan(
       job=job, facts=facts, snapshot=snapshot, carry=carry, record=deps.record,
   )
   ```

   With no predecessor, P-02 then replaces `carry` with
   `CarryOver(reused=(), regenerated=plan.obligations, reasons={id: "no_predecessor" for id in
   plan.obligations}, source_job=None)`. Its final `carry.regenerated` is therefore total using
   only shared `CarryOver` fields; `plan` and final `carry` are recorded and threaded together.
4. After `plan` and the final `carry` are durable, transition `CLAIMED → PLANNED` unconditionally.
   If `carry.regenerated` is non-empty, continue to the one panel call. If it is empty, do not call
   `run`: construct `PanelResult(attempts=(), complete=True, incomplete_reason=None,
   evidence_cutoff=facts.fetched_at)`, call E-09, then transition `PLANNED → JUDGED`. The real
   returned `Judgement`, not the state alone, continues to step 9.

#### Steps 6–8 — one panel call, then judgement

P-02 owns no retry, provider-failure, candidate-failure, route, reservation, or fallback loop.
For a non-empty regenerated set it transitions `PLANNED → REVIEWING` immediately before its one
P-06 call. It constructs the `SupplyPort` once over P-05:

```python
cursor = RouteCursor(excluded_families=frozenset(), excluded_routes=frozenset())
supply = SupplyPort(
    route=lambda obligation, cursor: deps.supply.route(
        job=job, obligation=obligation, snapshot=snapshot, facts=facts, cursor=cursor,
        prober=deps.supply.prober, breakers=deps.supply.breakers,
    ),
    reserve=lambda plan, route: deps.supply.reserve(
        job=job, plan=plan, route=route, snapshot=snapshot, spend=deps.supply.spend,
    ),
    consumed=lambda attempt, reading, reservation: deps.supply.consumed(
        job=job, attempt=attempt, reading=reading, reservation=reservation,
        record=deps.record, spend=deps.supply.spend, breakers=deps.supply.breakers,
    ),
)
panel_or_failure = deps.harness.run(
    job=job, plan=plan, facts=facts, snapshot=snapshot, supply=supply,
    state_dir=deps.state_dir, record=deps.record,
)
```

Those closures preserve E-06/E-15's verbatim arguments. P-06 owns cursor advancement, every
attempt-failure category, every fresh reservation and every refusal branch. P-02 calls `run`
exactly once and never inspects an individual attempt failure.

`BundleFailure` transitions `REVIEWING → STOPPED` with `"bundle incomplete"`. For an incomplete
`PanelResult`, the total map is `exhausted → STOPPED`, `budget → STOPPED`, and `bundle → STOPPED`.
Any unknown or internally contradictory complete/reason pair raises `LifecycleError`; no refusal or
unavailability reaches `APPROVED`.

For a complete panel (including 5a's empty panel), call E-09 exactly:

```python
result = deps.judgement.judge(
    job=job, plan=plan, panel=panel, carry=carry, facts=facts, snapshot=snapshot,
    decision=None, record=deps.record,
)
```

`judge` writes the single `judgement` entry. P-02 then transitions `PLANNED → JUDGED` for the
carry-only path or `REVIEWING → JUDGED` for a fresh panel and sends the real result to step 9.

#### Steps 9–11 — act, submit, merge

`remediate` chooses the first P-07 candidate, obtains a Grant using the finding's complete
`categories` set, and calls E-10 exactly:

```python
push = deps.remediation.remediate(
    job=job, finding=finding, grant=grant, facts=facts, snapshot=snapshot,
    state_dir=deps.state_dir, runner=deps.runner, record=deps.record,
)
```

`RemediationPushed` leaves the job `REMEDIATING`; `RemediationRefused` raises an `EVIDENCE_GAP` escalation then transitions
to `ESCALATED`. A remediation `Deny` similarly escalates with `AUTHORITY_REQUIREMENT`. For every
other judgement disposition, P-02 uses the existing one-transition mapping: `escalate` raises every
named cause then `ESCALATED`; `approve`/`request_changes` proceed to verdict authority.

Every E-12 mutation carries its activity-specific `Grant` exactly:

```python
deps.github.comment(job=job, body=body, grant=comment_grant, record=deps.record)
deps.github.submit_review(job=job, state=state, body=body, grant=grant, record=deps.record)
deps.github.merge(job=job, grant=merge_grant, record=deps.record)
```

`Mutation`, `Stale`, and `GithubUnavailable` are handled totally: accepted mutation makes the named
transition; `Stale` escalates `EVIDENCE_GAP`; `GithubUnavailable` stops. Thus `Deny`,
`RemediationRefused`, and `GithubUnavailable` cannot take an approved path. Steps 12a/12b remain
the only direct human-outcome path.

### 3.3 `resume` — the E-11 reverse edge

```python
def resume(*, job_id: str, decision: Decision, deps: LifecycleDeps) -> JobStatus: ...
```

This is E-11 verbatim. `resume` loads `job_id` from P-02's permitted `jobs` read; an absent row
raises `UnknownJobError`, and a row not at `ESCALATED` raises `LifecycleError`. It fetches E-23
facts once with `facts(job=job, record=deps.record)` and compares the head and pinned snapshot.
Either mismatch raises `StaleDecisionError`; it never returns a local alternative value.

For 12a, `resume` reconstructs `plan`/`carry` and the last complete panel. A fresh run reads the
`panel` entry; carry-only uses the judgement cutoff. E-09 receives fresh same-head facts but considers
only checks whose immutable observation time is at or before that cutoff.

For 12b, exactly one `facts.reviews` row must match `decision.actor`, `decision.outcome`,
`job.head_sha`, and have `submitted_at >= escalation.raised_at`; absent/ambiguous mismatch raises
`StaleDecisionError`. Only then transition directly to `APPROVED` or `CHANGES_REQUESTED` and perform
step 11 for approval. Any other outcome raises `LifecycleError`.

### 3.4 `status` — E-17

```python
def status(repo: str, number: int, *, connection: sqlite3.Connection) -> StatusReport | NotFound:
```

**Behaviour, in order.**

1. `SELECT head_sha FROM pr_facts WHERE repo = ? AND number = ?` on `connection` (P-01's table;
   container.md §5 lists P-02 as a reader). No row: return `NotFound(repo, number)`.
2. `SELECT id, status FROM jobs WHERE repo = ? AND number = ? AND head_sha = ?` (the head from step
   1). No row: return `NotFound(repo, number)` — `pr_facts` knows of the PR but no job exists yet
   for its current head (a narrow window right after step 2's inventory, before step 3 admits it).
3. `SELECT payload FROM record_entries WHERE job = ? AND kind = 'transition' ORDER BY seq DESC
   LIMIT 1` (job id from step 2; P-12's table, read-only, per §5's read protocol). Decode
   `reason` from the payload's JSON.
4. Return `StatusReport(job_id, internal_state=JobStatus(status), disposition=DISPOSITION[status],
   reason=reason)`. `status` is never `JobStatus.SUPERSEDED` by construction: step 2's `WHERE
   head_sha = ?` (the PR's *current* head, per step 1) can never match a job a later job's
   `predecessor_job` points away from — a superseded job's `head_sha` is, by definition, not the
   PR's current head. `DISPOSITION` therefore never needs a `SUPERSEDED` entry (§2 already omits
   one) and this function never has to special-case it.

**Guarantees the caller may rely on.** Read-only: never calls `transition`, never touches a
neighbour, never blocks on a lock (`jobs`, `pr_facts` and `record_entries` are read with ordinary
`SELECT`s, not inside the write transaction `_commit` opens). Two calls with nothing changed in
between return field-for-field identical results (T20).

## 4. Dependencies consumed

Every consumed E-NN is called only with the keyword-only signature in `CONTRACTS.md` §9. These
protocol declarations repeat those signatures verbatim for injection; P-02 defines no exchanged
type and no alternative convenience overload.

```python
class PolicyClient(Protocol):
    def snapshot_for(self, *, repo: str, job: Job | None, store: SnapshotStore,
                     record: RecordWriter | None) -> Snapshot | ValidationFailure: ...

class AuthorityClient(Protocol):
    def grant(self, *, repo: str, activity: Activity, snapshot: Snapshot | None, job_id: str,
              categories: frozenset[Category] | None, record: RecordWriter, github: GithubProbe,
              store: CapabilityStore) -> Grant | Deny: ...

class ReuseClient(Protocol):
    def carry_over(self, *, job: Job, prior: RecordReader, facts: Facts, snapshot: Snapshot,
                   record: RecordWriter) -> CarryOver: ...

class SupplyClient(Protocol):
    def route(self, *, job: Job, obligation: str, snapshot: Snapshot, facts: Facts, cursor: RouteCursor,
              prober: HarnessProber, breakers: BreakerStore) -> tuple[Route, RouteCursor] | RouteUnavailable: ...
    def reserve(self, *, job: Job, plan: Plan, route: Route, snapshot: Snapshot,
                spend: SpendStore) -> Reservation | Refusal: ...
    def consumed(self, *, job: Job, attempt: Attempt, reading: int | None, reservation: Reservation,
                 record: RecordWriter, spend: SpendStore, breakers: BreakerStore) -> Spend: ...

class HarnessClient(Protocol):
    def plan(self, *, job: Job, facts: Facts, snapshot: Snapshot, carry: CarryOver,
             record: RecordWriter) -> Plan: ...
    def run(self, *, job: Job, plan: Plan, facts: Facts, snapshot: Snapshot, supply: SupplyPort,
            state_dir: Path, record: RecordWriter) -> PanelResult | BundleFailure: ...

class JudgementClient(Protocol):
    def judge(self, *, job: Job, plan: Plan, panel: PanelResult, carry: CarryOver, facts: Facts,
              snapshot: Snapshot, decision: Decision | None, record: RecordWriter) -> Judgement: ...

class RemediationClient(Protocol):
    def remediate(self, *, job: Job, finding: Finding, grant: Grant, facts: Facts,
                  snapshot: Snapshot, state_dir: Path, runner: ProcessRunner,
                  record: RecordWriter) -> RemediationPushed | RemediationRefused: ...

class EscalationClient(Protocol):
    def raise_(self, *, job: Job, cause: EscalationCause, question: str, context: Mapping,
               record: RecordWriter, store: EscalationStore) -> Escalation: ...
    def pending(self, *, store: EscalationStore) -> tuple[Escalation, ...]: ...

class GithubClient(Protocol):
    def submit_review(self, *, job: Job, state: Literal["APPROVE", "REQUEST_CHANGES"], body: str,
                      grant: Grant, record: RecordWriter) -> Mutation | Stale | GithubUnavailable: ...
    def comment(self, *, job: Job, body: str, grant: Grant,
                record: RecordWriter) -> Mutation | GithubUnavailable: ...
    def merge(self, *, job: Job, grant: Grant,
              record: RecordWriter) -> Mutation | Stale | GithubUnavailable: ...
    def facts(self, *, job: Job, record: RecordWriter) -> Facts | GithubUnavailable: ...
```

P-01 supplies the two E-01 callables in `LifecycleDeps`; their calls are likewise
`claim_lease(job=job, grant=grant, record=deps.record)` and
`release_lease(job=job, grant=grant, record=deps.record)`. Their `LeaseTaken` result is P-09's
type, not a P-02 type. The same `deps.record` instance is passed to every call that requires it.

## 5. Store

This part owns no table's DDL. It writes `jobs.status` on every transition and `jobs.snapshot_hash`
exactly once — immediately after a successful first E-03 pin, in the same transaction as that
transition (`P-03-policy.md` §3, E-03 step 9: "the caller, not `rqa.policy`, writes
`job.snapshot_hash`"). No other part writes either column. It also reads
three tables two other parts own, using the schemas already published in `container.md` §5 and
`P-12-record.md` §5 (shown below for reference, not redefinition).

```sql
-- P-01's table (container.md §5); shown for reference.
CREATE TABLE jobs (
  id              TEXT PRIMARY KEY,
  repo            TEXT NOT NULL,
  number          INTEGER NOT NULL,
  head_sha        TEXT NOT NULL,
  base_sha        TEXT NOT NULL,
  predecessor_job TEXT,
  snapshot_hash   TEXT,
  status          TEXT NOT NULL      -- this part writes this column, and `snapshot_hash` once (below)
);
-- P-01's tables; shown for reference.
CREATE TABLE pr_facts (repo TEXT NOT NULL, number INTEGER NOT NULL, head_sha TEXT NOT NULL, ...);
CREATE TABLE leases   (job TEXT NOT NULL, github_assignee_node_id TEXT NOT NULL, claimed_at TEXT NOT NULL);
```

**Write protocol.** Exactly one statement, always inside `_commit`'s transaction (below):
`UPDATE jobs SET status = ? WHERE id = ?`.

**Read protocol.**
- `status()` step 1: `SELECT head_sha FROM pr_facts WHERE repo = ? AND number = ?`.
- `status()` step 2, and `_enter_rest` step 1's successor lookup: `SELECT ... FROM jobs WHERE
  repo = ? AND number = ? AND head_sha = ?` / `WHERE predecessor_job = ?` — both single indexed
  lookups an implementer indexes `jobs(repo, number, head_sha)` and `jobs(predecessor_job)` for.
- `_enter_rest` step 2: `SELECT 1 FROM leases WHERE job = ?`.
- Steps 6+7 and 12a's read-back of the recorded `plan` (and, where a resumed `judged` job needs it
  without a fresh `judge()` call, the recorded `judgement`): `SELECT payload FROM record_entries
  WHERE job = ? AND kind = ? ORDER BY seq DESC LIMIT 1` (P-12's table, `container.md` §5 lists
  P-02 as a reader; `P-12-record.md` §5 publishes this exact indexed shape as `record_entries_by_job`).
  The JSON payload is decoded into the shared Contract's `Plan`/`Judgement` dataclasses by field
  name — this part, unlike P-12, does import those types, so it is free to reconstruct them.
- `status()` step 3: the same `record_entries` query, `kind = 'transition'`, for `reason`.

**Transaction boundary.**

```python
def _commit(job: Job, to: JobStatus, from_state: str | None, reason: str, *,
            connection: sqlite3.Connection, record: RecordWriter) -> None:
    with connection:                                     # BEGIN on first statement; COMMIT on
        connection.execute(                               # clean exit; ROLLBACK + re-raise on
            "UPDATE jobs SET status = ? WHERE id = ?",     # any exception — stdlib sqlite3's own
            (to.value, job.id),                            # transaction semantics, nothing this
        )                                                   # part adds.
        record.append(job.id, "transition", {
            "from_state": from_state, "to_state": to.value, "reason": reason,
            "repo": job.repo, "number": job.number, "head_sha": job.head_sha,
            "base_sha": job.base_sha, "predecessor_job": job.predecessor_job,
        })
```

`record` is constructed by whoever wires the process together over this same `connection` (per
`P-12-record.md` §3.1: "the caller constructs, or is handed, a `RecordWriter` over the *same*
`sqlite3.Connection` its own state-changing statement is about to execute on"). `record.append`
never calls `commit`/`rollback` itself; `with connection:` above is what does, and it is the only
place in this part that does. This is the literal mechanism behind "one SQLite transaction":
`UPDATE` and `INSERT` share one connection's implicit transaction, so a failure in either leaves
neither durable.

## 6. Record entries written

| kind | when | payload |
|---|---|---|
| `transition` | every call to `transition()`, including the arrival case (`from_state: None`) | `from_state: str \| None`, `to_state: str`, `reason: str`, `repo: str`, `number: int`, `head_sha: str`, `base_sha: str`, `predecessor_job: str \| None` — verbatim the shape `P-12-record.md` §6 already publishes, so `resolve_job` and `explain` (neither of which reads `jobs`) can resolve identity and supersession chains from `record_entries` alone. |

P-02 alone writes `transition` and `jobs.status`. P-07 writes `judgement` through the
transaction-bound `RecordWriter`; P-02 does not duplicate it. Neighbour calls that write `plan`,
`carry_over`, `bundle`, `attestation`, `spend`, `panel`, `grant`, `action` or `escalation` receive
that same writer. `AppendFailed` therefore aborts the surrounding state change, while P-12's
`explain_job` can reconstruct one ordered stream.

## 7. What it does not do

- Does not call GitHub, a harness process, or a model directly — each external effect is a listed
  neighbour edge. P-01-owned E-01 is invoked only through the injected `claim_lease` and
  `release_lease` callables with its shared P-09 result types.
- Does not decide what a verdict means, which findings corroborate, which obligations are
  satisfied, or which category is mechanical — `Judgement` arrives already decided (P-07); this
  part only maps `Judgement.disposition` to the transition it licenses.
- Does not compute a route, reservation, budget refusal, or fallback. It constructs P-06's
  `SupplyPort` and calls `run` once; P-06 owns all panel-loop branches.
- Does not validate policy, pin a snapshot, or re-read one mid-job. The pinned snapshot and one
  E-23 `Facts` value are threaded through the whole review.
- Does not own the E-01 GitHub mutation: P-01 constructs its callbacks and P-09 supplies
  `Mutation`, `LeaseTaken`, and `GithubUnavailable`; P-02 defines no lease type.
- Does not send a notification on escalation, comment, or any other action — no edge to a
  notification transport exists in this part's consumed set, matching `architecture.md` §17.
  Does not unwind or re-decide a `decision` entry once P-11 has appended it, even when `resume`'s
  own defensive check finds it stale after the fact (§3.3).
- Does not retry a `stopped` job by resuming whatever step it stopped at — `stopped`'s only legal
  forward edge is to `claimed` (§2's table), so a retry always restarts from plan-and-carry-over,
  never from mid-cascade; carry-over is what keeps this cheap, not step preservation.
- Does not purge, back up, or bound the growth of `jobs`, `pr_facts`, `leases` or `record_entries`
  — none of those tables' retention is this part's concern (`container.md` §5, §7).
- Does not read `snapshots`, `capabilities`, `spend`, `breakers`, `mutations`, `etags`, `api_calls`,
  or the content of `human_requests` rows — only `jobs`, `pr_facts`, `leases` and `record_entries`,
  and only the columns named in §5.

## 8. Tests that prove it

| # | Given | Then |
|---|---|---|
| T1 | `transition(job, to, ...)` where `to not in TRANSITIONS[job.status]` | raises `IllegalTransitionError`; neither `jobs.status` nor `record_entries` changes |
| T2 | A legal transition whose append succeeds | exactly one matching `jobs.status` update and `transition` entry commit atomically |
| T3 | An update or append fails, then the stop transition succeeds | the original transition is rolled back and exactly one `STOPPED` transition is committed |
| T4 | The fallback stop append also fails | `AppendFailed` propagates and the last-good state remains durable |
| T5 | A neighbour raises its named `*Error` | it propagates; P-02 does not misclassify it as `STOPPED` |
| T6 | Review authority returns `Deny` | `QUEUED → ESCALATED`, no E-01 claim, and one authority-requirement escalation |
| T7 | A planned review with regenerated obligations, including fallback and retries | P-02 transitions `CLAIMED → PLANNED → REVIEWING`, calls `harness.run` exactly once, and never drives an attempt |
| T8 | `run` returns an incomplete `PanelResult` or `BundleFailure` | `REVIEWING → STOPPED`; no failure subtype can reach `APPROVED` |
| T9 | `carry.regenerated == ()` | `CLAIMED → PLANNED`; zero `run` calls; E-09 receives an empty complete panel with `evidence_cutoff=facts.fetched_at`; only after it returns does `PLANNED → JUDGED` occur |
| T10 | A complete fresh panel | E-09 receives the panel's post-attempt `evidence_cutoff`; only after judgement does `REVIEWING → JUDGED` occur |
| T11 | A remediation judgement with a granted remediation activity | E-10 receives `job`, `finding`, `grant`, the same `facts`, the pinned `snapshot`, `state_dir`, `runner`, and `record`; `RemediationRefused` reaches only `ESCALATED` |
| T12 | Comment, submit-review, and merge mutations | every E-12 call carries its activity-specific `Grant`; `Stale` escalates and `GithubUnavailable` stops |
| T13 | Exhaustive state-path search with every refusal, unavailability and denial at its boundary | no path reaches `APPROVED`; every branch rests safely unless a recorded human 12b decision supplies the outcome |
| T14 | resume 12a with same head and newer facts | E-09 receives reconstructed panel; checks observed after its cutoff cannot affect judgement |
| T15 | resume 12b with exactly one submitted review matching actor, outcome, head and post-escalation time | direct human outcome transition; no verdict grant requested |
| T16 | moved head/snapshot, or missing/ambiguous/mismatched submitted review | `StaleDecisionError`; no transition follows |
| T17 | One normal admission through plan, panel, judgement, and remediation | E-23 `facts(job=job, record=record)` is called once, and object identity is preserved in E-05, E-07 plan/run, E-09, and E-10 |
| T18 | A crash-recovered `judged` job with its judgement entry | it does not call E-09 again; step 9 consumes the recorded judgement |
| T19 | A resting job retains an orphaned lease | only a review `Grant` releases it; a `Deny` leaves the lease visible |
| T20 | `status(repo, number)` for every current-head status and an unknown PR | disposition is total for known statuses and the unknown returns `NotFound` |

**Property that must hold across the suite.** `grep -rn "jobs.status\s*=" rqa/ --include=*.py`
(outside test fixtures) returns hits only inside `rqa/lifecycle/transition.py`'s one `UPDATE`
statement. No other part's code path writes that column.

## 9. Requirements this part answers for

Accountable: RQA-BR-001, RQA-BR-010, RQA-FR-016, RQA-FR-027, RQA-FR-028, RQA-FR-038, RQA-NFR-007,
RQA-NFR-010 (`components.md` line 126). Each requirement's fit criterion, and where this contract
discharges it:

- **RQA-BR-001** ("consistent, auditable, efficient, and trustworthy"). Fit criterion: satisfied
  exactly when its four cited rows are, not by a packaging test of its own. This part is the
  *consistency* row's mechanism at the state-machine level: one closed `TRANSITIONS` table (§2)
  and one function that writes `jobs.status` (§5's grep property) is what makes "the same review
  reaches the same disposition the same way" true structurally rather than by convention.
- **RQA-BR-010** ("progression shall not depend on manual owner intervention beyond what genuinely
  requires human judgement"). Fit criterion: a PR whose findings require no judgement is driven
  through *every* applicable RQA-FR-016 transition without owner action; automating one transition
  and stalling on a later one fails this. Steps 3–11 (§3.2) chain without any transition waiting on
  an owner except 9b/10a's genuine escalations — T11's property test is this fit criterion made
  mechanical: no non-escalating, non-stopping path halts before `approved`/`changes_requested`.
- **RQA-FR-016** (`rqa status` returns one of six dispositions and the reason). Fit criterion: after
  every observable lifecycle transition, `status` reflects the PR's independently established
  current state, not a stale or generic answer. `status()` (§3.4) reads `jobs.status` and the
  latest `transition.reason` fresh on every call (T20); `DISPOSITION` (§2) is the exhaustive,
  total mapping the fit criterion's "not merely one of the six legal values" requires — there is no
  status this part can reach that `DISPOSITION` does not cover (T20's 13-way parametrisation).
- **RQA-FR-027** (supplying an escalation's requested input resumes without restarting). Fit
  criterion: after supply, review re-enters at `judged` (not `queued` or `claimed`) with the
  recorded decision plus reconstructed `plan`, `carry`, and panel, re-running nothing the decision
  did not touch (T14); 12b transitions directly without re-entering step 10 at all (T15).
- **RQA-FR-028** (submit APPROVED or CHANGES_REQUESTED once obligations are satisfied). Fit
  criterion is the submission itself, not a state-machine property, but this part is what gates it:
  step 10 (§3.2) never calls `github.submit_review` without a `Grant` for the specific activity
  (T12), and `submitting`'s only forward edges are `changes_requested`/`approved`/`escalated`/
  `stopped` (§2's table) — never a second, silent path to submission.
- **RQA-FR-038** (stop in a clear, safe, recoverable state when no fallback is configured and a
  reviewer/model/provider becomes unavailable). Fit criterion: the halted state independently holds
  every standing invariant this specification names, including RQA-NFR-010, and is resumable. Steps
  6b/6c (§3.2) are the only paths from `planned` to `stopped`; §5's transaction boundary is what
  makes the resulting state "independently observable to hold" RQA-NFR-010 (below) rather than
  merely labelled safe (T8, T9).
- **RQA-NFR-007** (manage every step through to an authoritative outcome whenever progression
  remains possible). Fit criterion: every managed PR reaches `approved`/`changes_requested`, or the
  record carries evidence that no source-conforming next transition was available at the point it
  entered a non-success stop — and a recorded human approval or a supplied escalation input
  resuming the lifecycle does not itself fail this check. §2's `TRANSITIONS` table is this
  requirement's own "progression remains possible" made checkable: U-DISPATCH-23's total ordering
  is what proves a job was driven as far as a *reachable* rung allowed before it stopped, not
  merely to some non-success value. Step 10a's transition reason is written verbatim as "no
  source-conforming next transition was available" `[ADR-D assumed]` (T12); 12a/12b are exactly the
  "resuming the lifecycle" carve-out the fit criterion names (T14, T15).
- **RQA-NFR-010** (a failure during review shall never leave an ambiguous, corrupted or partially
  authoritative outcome). Fit criterion: every failure is checked against all three — not
  ambiguous, not corrupted, not partially authoritative — independently. §5's `with connection:`
  transaction boundary is *not ambiguous* (T2: status and its transition entry always agree) and
  *not partially authoritative* (T3: a failed transition never leaves `jobs.status` at the
  attempted value); §3.1 step 3's containment is *not corrupted* (T4: even a double failure leaves
  the last-good state, never a torn write, because the fallback attempt is itself inside the same
  `with connection:` discipline).

Contributes to (not accountable for, but this part's behaviour is part of how each is met):
RQA-BR-007 (one job per revision — the arrival check in §3.1 step 1 relies on P-01's own
one-job-per-head-per-repo invariant rather than re-deriving it), RQA-FR-011/RQA-FR-037 (successful
disposition requires every obligation checked — enforced by acting only on `Judgement`, never
re-deriving it), RQA-FR-022/RQA-FR-039 (resource bound reached never produces success — §3.2's
6c/T9), RQA-FR-029/RQA-NFR-008 (merge configurable per repository — step 11, gated the same way as
every other activity).
