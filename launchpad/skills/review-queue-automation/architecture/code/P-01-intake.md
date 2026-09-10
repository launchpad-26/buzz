# P-01 Intake — code-level contract

This is the implementation contract for one part of the design in
[`../architecture.md`](../architecture.md). An agent implementing P-01 builds exactly what is here;
an agent implementing a neighbour calls exactly what is here. Anything not stated is the implementer's
choice, provided the stated shape, behaviour and tests hold. Contract ids (`E-NN`) and record names
are those of [`../components.md`](../components.md) §6 and [`../container.md`](../container.md) §5.

**Responsibility, in one sentence.** Find the work and hold the queue: gate every configured
repository on a valid, resolvable snapshot before touching it, hold the machine's exclusive sweep
lock, read GitHub's PR inventory, create at most one job per revision, detect a head change and hand
Lifecycle the superseded predecessor's id, provide the GitHub-verified review-lease mechanism a
`Grant` authorises Lifecycle to drive, and hand a bounded, fairly-ordered batch of jobs to Lifecycle —
never deciding what a job means, only that it exists and whose turn it is.

**Depends on.** ADR-E ([#2158](https://github.com/launchpad-26/buzz/issues/2158), assumed) only
insofar as credential capability touches admission. The repository gate checks config validity; the
job-scoped E-16 probe cannot run before a job exists. A credential lacking review capability is
therefore denied by P-08 at flow step 3a, never misreported as an intake/config refusal. No other
part's internals.

## 1. Modules

```
rqa/intake/
  __init__.py     re-exports: tick, TickResult, AdmissionRefusal, JobFailure, job_id, stable_hash,
                  GithubAdapter, Lease, JobStore, PrFactsStore, LeaseStore, PrFactsRow, LeaseRow,
                  IntakeError
  identity.py     stable_hash(), job_id() — the deterministic hash this part owns (U-RESILIENCE-13);
                  P-09 imports this module directly for its own mutation ids (`components.md` §7's
                  placement note: "job identity is P-01's; the deterministic mutation-id half is
                  used by P-09")
  lock.py         the exclusive, non-blocking flock and its kernel release (U-DISPATCH-02)
  admission.py    the per-repository admission gate: `rqa.policy.snapshot_for(job=None)`
                  (U-DISPATCH-01; the E-03 extension `code/P-03-policy.md` §3 already documents)
  inventory.py    per-repository PR inventory, `pr_facts` upsert, job creation, and head-change /
                  supersede detection (U-QUEUE-01, U-QUEUE-02, U-QUEUE-14)
  lease.py        `Lease`: the GitHub-verified, `Grant`-gated claim/release mechanism around one
                  job's dispatch (U-QUEUE-03, U-QUEUE-04, U-DISPATCH-10)
  batch.py        bounded FIFO batch selection, plus the resting-job follow-up widening that is this
                  part's half of crash recovery (U-DISPATCH-08; flow-review-lifecycle.md §3 step 13)
  store.py        the `jobs`, `pr_facts` and `leases` DDL and the three read/write protocols
  types.py        `PrFactsRow`, `LeaseRow` and the small result values this part returns; shared
                  `Job` is imported from the Contract
  tick.py         `tick()`: the one entry point (E-21) — orchestrates every module above, with
                  per-repository and per-job error isolation (U-QUEUE-07, U-DISPATCH-22)
```

No other module in RQA imports from `rqa.intake` except through `__init__`, with one documented
exception symmetric to how `rqa.policy` treats `rqa.protocol` as shared vocabulary
(`code/P-03-policy.md` §1): `rqa.github` imports `rqa.intake.identity` directly for `stable_hash`,
because U-RESILIENCE-13 places the one hashing mechanism here and names P-09 as its other user. No
module in `rqa.intake` imports from any other part except: `rqa.record` (`RecordWriter`,
`AppendFailed` — to satisfy `snapshot_for`'s required parameter at admission time and to hand a
writer through to Lifecycle and E-01; this part appends nothing itself, §6), `rqa.policy`
(`snapshot_for`, `SnapshotStore`, `ValidationFailure` — the admission gate), and `rqa.github`
(`GithubAdapter`, `LeaseTaken`, `GithubUnavailable` — E-01's implementation). Shared `Job`, `JobStatus`,
`Grant`, `PrFacts` and `Mutation` are imported from the Contract, never redefined. This file never
imports `rqa.authority`, `rqa.judgement`, `rqa.protocol`, `rqa.supply`, `rqa.harness`,
`rqa.remediation`, `rqa.escalation`, or `rqa.reuse` directly at all.

## 2. Types

`Job` is the shared type defined only in [`CONTRACTS.md`](CONTRACTS.md) §1. In particular, intake
populates its required `head_repo` and `head_ref` from the inventory `PrFacts` when it creates a job;
they identify the actual PR head (the base repository and branch are not assumed).

`created_at` is deliberately **not** a `Job` field: it is a column of the `jobs` table (§5) used only
for this part's own FIFO ordering (U-DISPATCH-08), never a value another part's contract needs to
carry, so it stays out of the cross-part shape the Contract fixes.

`JobStatus` is the shared type defined only in [`CONTRACTS.md`](CONTRACTS.md) §1. Two sets, derived
from the public state table, decide what this part does with an existing job:

```python
# batch.py — mirrors flow-review-lifecycle.md §4.
_SWEEP_RESUMABLE: frozenset[JobStatus] = frozenset({
    JobStatus.QUEUED, JobStatus.CLAIMED, JobStatus.PLANNED, JobStatus.REVIEWING,
    JobStatus.JUDGED, JobStatus.SUBMITTING, JobStatus.STOPPED,
})
_RESTING: frozenset[JobStatus] = frozenset({
    JobStatus.ESCALATED, JobStatus.REMEDIATING, JobStatus.APPROVED,
    JobStatus.MERGED, JobStatus.CHANGES_REQUESTED, JobStatus.SUPERSEDED,
})
```

`Grant`, `PrFacts`, `Mutation`, `LeaseTaken` and `GithubUnavailable` are shared types defined only in
[`CONTRACTS.md`](CONTRACTS.md) §§4 and 8, consumed read-only per §4.

```python
# types.py — P01: this part's own result values, not in the shared Contract
@dataclass(frozen=True)
class TickResult:
    outcome: Literal["swept", "sweep_already_running"]
    repos_admitted: tuple[str, ...]
    repos_refused: tuple[AdmissionRefusal, ...]
    jobs_created: tuple[str, ...]              # job ids created this tick
    jobs_dispatched: tuple[str, ...]           # job ids handed to lifecycle.admit this tick
    jobs_failed: tuple[JobFailure, ...]        # admit() raised; U-DISPATCH-22
    revisited_resting_jobs: tuple[str, ...]    # job ids added to the batch only so Lifecycle can
                                                # revisit a resting job (§3 step 4)

@dataclass(frozen=True)
class AdmissionRefusal:
    repo: str
    reason: str                 # every ValidationError in the ValidationFailure, joined
    onboarding_command: str     # f"rqa onboard {repo}"

@dataclass(frozen=True)
class JobFailure:
    job_id: str
    error: str                  # repr(exc); logged, never appended to the record — see §6

class IntakeError(Exception):
    """Programming error: this part was called wrongly, or one of its own invariants is broken.
    Never raised for an admission refusal, a lock contention, a lease denial, or an inventory
    GithubUnavailable — those are values. Not caught by Lifecycle's containment boundary."""
```

```python
# types.py — P01's local PR-tracking cache row and lease row; neither crosses a part boundary.
@dataclass(frozen=True)
class PrFactsRow:
    repo: str
    number: int
    head_sha: str                # sole source of the observed head (U-QUEUE-14)
    base_sha: str
    head_repo: str               # copied from shared PrFacts for the actual PR head
    head_ref: str
    author: str
    labels: tuple[str, ...]
    last_seen_at: datetime       # refreshed on every inventory pass that lists this PR

@dataclass(frozen=True)
class LeaseRow:
    job_id: str
    repo: str
    number: int
    claimed_at: datetime
```

`PrFactsRow` is a local cache of exactly the inventory facts P-01 needs: the shared `PrFacts`
fields used for job identity, supersession and the PR-head destination, plus `last_seen_at` for its
own freshness bookkeeping. It is not a replacement definition of shared `PrFacts`.

## 3. Entry point — E-21 `tick`

def tick(
    *,
    repos: Sequence[str],
    github: GithubAdapter,             # E-01
    policy: PolicyClient,              # E-03, passed into LifecycleDeps
    authority: AuthorityClient,
    supply: SupplyPort,
    harness: HarnessPort,
    judgement: JudgementClient,
    remediation: RemediationClient,
    escalation: EscalationClient,
    reuse: ReuseClient,
    jobs: JobStore,
    pr_facts: PrFactsStore,
    leases: LeaseStore,
    record: RecordWriter,
    connection: Connection,
    state_dir: Path,
    runner: ProcessRunner,
    batch_size: int = DEFAULT_BATCH_SIZE,
    clock: Callable[[], datetime] = utcnow,
    log: Callable[[str], None] = tick_log,
) -> TickResult:

`jobs`, `pr_facts`, `leases`, `record` and `connection` share the one `state.db` connection
(`container.md` §3). P-01 commits once per PR after its `pr_facts` upsert and possible `jobs.create`,
and once per job after `admit(job=job, deps=deps)` returns or raises.

**Behaviour, in order.** `IntakeError` and `AppendFailed` are programming faults and propagate;
modelled availability and lease outcomes are values. Every `tick()` attempts a full sweep: there is
no cadence gate or persisted next-due state.

1. Acquire the exclusive, non-blocking `flock` on `<state_dir>/lock` (`lock.py`; U-DISPATCH-02).
   - Contended (`BlockingIOError`/`OSError` with `errno` in `{EACCES, EAGAIN}`) → return
     `TickResult(outcome="sweep_already_running", repos_admitted=(), repos_refused=(), jobs_created=(),
     jobs_dispatched=(), jobs_failed=(), revisited_resting_jobs=())` immediately. Nothing below runs;
     no table is read. The CLI maps this outcome to exit 0 — a named successful no-op, not an error
     [RQA-NFR-010's third invariant, carried by U-DISPATCH-02, not this part's own accountable set].
   - Held → keep the file descriptor open for the rest of this call. The kernel releases the lock
     when this process exits, however it exits — the crash-self-healing half of U-DISPATCH-02.
2. For each `repo` in `repos`, in order, run steps 2a–2c under one `try/except Exception`; on an
   exception, log `repo sweep failed: {repo}: {exc!r}` and continue to the next repository.
   - **2a.** `refusal = _check_admission(repo, store=policy, record=record)`, which calls
     `snapshot_for(repo=repo, job=None, store=policy, record=record)`. If `refusal is not None`,
     append it to `repos_refused`, log it, and continue. Nothing downstream runs for this repository.
   - **2b.** Append `repo` to `repos_admitted`; call `result = github.inventory(repo=repo)`.
     `GithubUnavailable` → log it and continue. Otherwise `result` is `tuple[PrFacts, ...]`; continue
     with 2c for each item.
   - **2c.** For each `pf` in `result`: `pr_facts.upsert(PrFactsRow(repo=repo, number=pf.number,
     head_sha=pf.head_sha, base_sha=pf.base_sha, head_repo=pf.head_repo, head_ref=pf.head_ref,
     author=pf.author, labels=tuple(pf.labels), last_seen_at=clock()))` (`inventory.py`) — always,
     whether or not a job results (U-QUEUE-01: "the fact upsert and the job key are one mechanism").
     Then:
     - `existing = jobs.current_for_pr(repo, pf.number)`.
     - `existing is None` → `new_job = Job(id=job_id(repo, pf.number, pf.head_sha), repo=repo,
       number=pf.number, head_sha=pf.head_sha, base_sha=pf.base_sha, head_repo=pf.head_repo,
       head_ref=pf.head_ref, predecessor_job=None, predecessor_head_sha=None,
       snapshot_hash=None, status=JobStatus.QUEUED)`;
       `jobs.create(new_job)`; commit; append `new_job.id` to `jobs_created` [U-RESILIENCE-13,
       U-QUEUE-01].
     - `existing is not None and existing.head_sha == pf.head_sha` → nothing to do. `UNIQUE(repo,
       number, head_sha)` would refuse a duplicate `create` anyway; this check only avoids
       attempting one [U-QUEUE-01].
     - `existing is not None and existing.head_sha != pf.head_sha` → the PR moved.
       `new_job = Job(id=job_id(repo, pf.number, pf.head_sha), repo=repo, number=pf.number,
       head_sha=pf.head_sha, base_sha=pf.base_sha, head_repo=pf.head_repo, head_ref=pf.head_ref,
       predecessor_job=existing.id, predecessor_head_sha=existing.head_sha,
       snapshot_hash=None, status=JobStatus.QUEUED)`;
       `jobs.create(new_job)`; commit; append `new_job.id` to `jobs_created`. This part never writes
       `existing`'s `status` and never calls Lifecycle about `existing` directly; carrying
       `predecessor_job` on `new_job` is the entire signal, and step 4 below makes Lifecycle revisit
       `existing` [U-QUEUE-02, U-QUEUE-14].
3. `resumable = jobs.select_batch(limit=batch_size)` — every job whose status is in
   `_SWEEP_RESUMABLE`, ordered `(created_at, id)` ascending, capped at `batch_size`
   (`DEFAULT_BATCH_SIZE = 20`, an implementer's-choice constant; no `container.md` §5 record models
   it as policy-configurable) [U-DISPATCH-08 — the stable order is what stops the cap from starving
   an old job].
4. `followup = jobs.pending_followup()` returns resting jobs with either an unsuperseded successor
   or an outstanding lease row. Add them after `resumable`, deduplicated by id, and record them in
   `revisited_resting_jobs`; neither reason consumes review capacity.
5. For each job in that batch, in order, isolate the following work in `try/except Exception`:
   - Construct `lease = Lease(leases=leases, github=github, clock=clock)`.
   - Construct P-02's frozen `LifecycleDeps`:

     ```python
     deps = LifecycleDeps(
         policy=policy, authority=authority, supply=supply, harness=harness,
         judgement=judgement, remediation=remediation, escalation=escalation, github=github,
         reuse=reuse, record=record, connection=connection, state_dir=state_dir, runner=runner,
         claim_lease=lease.claim_lease, release_lease=lease.release_lease,
     )
     ```

     P-02 invokes `claim_lease` only after its step-3 `review` grant succeeds. The P-01 capability
     calls E-01 only with that grant and persists the local lease row only after `Mutation`.
   - Call `admit(job=job, deps=deps)` exactly once; commit after it returns and append `job.id` to
     `jobs_dispatched`.
   - If `admit` raises an unexpected exception, log it, append `JobFailure(job.id, repr(exc))`, and
     continue. P-01 does not issue an unauthorised release; an outstanding row is re-offered through
     `pending_followup` on the next tick.
6. Return `TickResult(outcome="swept", repos_admitted=tuple(repos_admitted),
   repos_refused=tuple(repos_refused), jobs_created=tuple(jobs_created),
   jobs_dispatched=tuple(jobs_dispatched), jobs_failed=tuple(jobs_failed),
   revisited_resting_jobs=tuple(revisited_resting_jobs))`.

**Out of this function's scope, stated so a later reader does not have to re-derive it.** `repos` — the
configured set of managed repositories — is a parameter, not a record this file reads: no row in
`container.md` §5 models a "managed repositories" list, and `.rqa/config.json` is per-repository, not
the list of repositories itself. Sourcing it is the CLI's own wiring, the same way `code/
P-08-authority-gate.md`'s `grant()` takes `repo: str` without describing where the caller's configured
set comes from. An infrastructure failure that is not one of the two modelled shapes above — the
`state.db` connection itself unreachable, the state directory's filesystem full — is not caught by
either isolation wrapper and propagates out of `tick()` to the CLI's `main()`, which is the right
place to fail loudly: those are not per-repository or per-job conditions.

## 4. Dependencies consumed — E-01, E-02, E-03 (admission)

### E-01 — `rqa.github` (P-09)

P-01 consumes these signatures verbatim from [`CONTRACTS.md`](CONTRACTS.md) §9:

```python
def inventory(*, repo: str) -> tuple[PrFacts, ...] | GithubUnavailable: ...
def claim_lease(*, job: Job, grant: Grant, record: RecordWriter) -> Mutation | LeaseTaken | GithubUnavailable: ...
def release_lease(*, job: Job, grant: Grant, record: RecordWriter) -> Mutation | GithubUnavailable: ...
```

`inventory` is called once per admitted repository per tick as
`github.inventory(repo=repo)`. P-01 owns both lease-mutator calls, always with all keyword
arguments exactly as above; it never uses a per-repository adapter or an alternative mutator shape.
P-02 obtains the `Grant(Activity.REVIEW)` at flow step 3, reports it through the `LifecycleDeps`
lease capability it received from P-01, and only then may P-01 call `claim_lease`. Thus neither
claim nor release can run before review authority exists.

```python
# lease.py — P-01's callbacks supplied in LifecycleDeps; the shared values below are only
# referenced from CONTRACTS.md §9.
@dataclass
class Lease:
    leases: LeaseStore
    github: GithubAdapter
    clock: Callable[[], datetime]

    def claim_lease(
        self, *, job: Job, grant: Grant, record: RecordWriter,
    ) -> Mutation | LeaseTaken | GithubUnavailable: ...

    def release_lease(
        self, *, job: Job, grant: Grant, record: RecordWriter,
    ) -> Mutation | GithubUnavailable: ...
```

`claim_lease` calls `github.claim_lease(job=job, grant=grant, record=record)` only after P-02
supplies the review grant. On `Mutation`, it records the local `LeaseRow` for `job`; on
`LeaseTaken` or `GithubUnavailable`, it writes no row. `release_lease` calls
`github.release_lease(job=job, grant=grant, record=record)` only with that reported review grant;
it deletes the row only on `Mutation`, retaining it on `GithubUnavailable`. Every union branch returns its
original value; an unexpected `*Error` propagates.

### E-02 — `rqa.lifecycle`'s `admit` (P-02)

P-01 consumes this signature verbatim from [`CONTRACTS.md`](CONTRACTS.md) §9:

```python
def admit(*, job: Job, deps: LifecycleDeps) -> JobStatus: ...
```

For each selected job P-01 constructs the frozen `LifecycleDeps` defined by P-02, including the
P-01-owned lease capability, then calls `admit(job=job, deps=deps)` exactly once. P-02 alone
interprets the returned `JobStatus`; P-01 records only that this one call was made or raised.

### E-03 (extended) — `rqa.policy`'s `snapshot_for` (P-03)

```python
def snapshot_for(*, repo: str, job: Job | None, store: SnapshotStore,
                 record: RecordWriter | None) -> Snapshot | ValidationFailure: ...
```

This part calls it with `job=None` — the exact branch `code/P-03-policy.md` §3 step 2 names as "an
admission-time check before any job exists, per flow-review-lifecycle.md §3 step 1". `components.md`
§6's table lists E-03 as `P-02 | P-03` only; this file's use of it is the same edge, one caller wider
than the table's literal row, and the wider use is already anchored on P-03's own contract rather than
invented here. The returned `Snapshot`, when admission succeeds, is discarded — nothing job-scoped
exists yet to pin it to, and every job Lifecycle later admits re-derives its own pin at first claim
(`code/P-03-policy.md` §3 branch 2, `job.snapshot_hash is None`). The `record: RecordWriter` argument
this call requires is passed through unused on this branch (`code/P-03-policy.md`: "unused when job
is `None`"); this part holds one only to satisfy that parameter and to thread through to `Lease`/
`admit` (§6 explains why it never calls `.append` itself).

## 5. Store

```sql
CREATE TABLE jobs (
  id              TEXT PRIMARY KEY,
  repo            TEXT NOT NULL,
  number          INTEGER NOT NULL,
  head_sha        TEXT NOT NULL,
  base_sha        TEXT NOT NULL,
  head_repo       TEXT NOT NULL,             -- actual PR-head repository
  head_ref        TEXT NOT NULL,             -- actual PR-head branch
  predecessor_job TEXT REFERENCES jobs(id),
  predecessor_head_sha TEXT,                   -- immutable E-23 revision-compare base
  snapshot_hash   TEXT,
  status          TEXT NOT NULL,
  created_at      TEXT NOT NULL,
  UNIQUE (repo, number, head_sha)
);
CREATE INDEX idx_jobs_pr    ON jobs (repo, number, created_at DESC);
CREATE INDEX idx_jobs_sweep ON jobs (status, created_at, id);

CREATE TABLE pr_facts (
  repo         TEXT NOT NULL,
  number       INTEGER NOT NULL,
  head_sha     TEXT NOT NULL,
  base_sha     TEXT NOT NULL,
  head_repo    TEXT NOT NULL,
  head_ref     TEXT NOT NULL,
  author       TEXT NOT NULL,
  labels       TEXT NOT NULL,
  last_seen_at TEXT NOT NULL,
  PRIMARY KEY (repo, number)
);

CREATE TABLE leases (
  job_id     TEXT PRIMARY KEY,            -- the job this lease is attributed to, U-QUEUE-04
  repo       TEXT NOT NULL,
  number     INTEGER NOT NULL,
  claimed_at TEXT NOT NULL,               -- ISO-8601 UTC
  UNIQUE (repo, number)                   -- at most one active claim per PR, independent of job
);
```

`lock` is not a table: a zero-length file at `<state_dir>/lock`, opened once per `tick()` call and
held open via an exclusive, non-blocking `fcntl.flock(fd, LOCK_EX | LOCK_NB)` for the process's whole
lifetime (`lock.py`). No column, no row — the kernel's own file-descriptor table is the state, which
is what makes release automatic on any process exit, including a crash (U-DISPATCH-02).

```python
# store.py
class JobStore(Protocol):
    def create(self, job: Job) -> None: ...              # INSERT; UNIQUE violation is the caller's
                                                           # own duplicate-check failing, never reached
                                                           # in practice per §3 step 2c's guard
    def get(self, job_id: str) -> Job | None: ...                       # read: P-02, P-11, P-13
    def current_for_pr(self, repo: str, number: int) -> Job | None: ... # latest job for (repo, number)
    def select_batch(self, limit: int) -> list[Job]: ...                # §3 step 3
    def pending_followup(self) -> list[Job]: ...                        # §3 step 4
    def set_status(self, job_id: str, status: JobStatus) -> None: ...        # P-02's exclusive write
    def set_snapshot_hash(self, job_id: str, snapshot_hash: str) -> None: ... # P-02's exclusive write,
                                                                                # once, at first pin

class PrFactsStore(Protocol):
    def upsert(self, row: PrFactsRow) -> None: ...     # INSERT ... ON CONFLICT(repo, number) DO UPDATE
    def get(self, repo: str, number: int) -> PrFactsRow | None: ...

class LeaseStore(Protocol):
    def current(self, repo: str, number: int) -> LeaseRow | None: ...   # read: P-02 (container.md §5)
    def put(self, row: LeaseRow) -> None: ...
    def delete(self, repo: str, number: int) -> None: ...
```

`set_status`/`set_snapshot_hash` exist only for `code/P-02-lifecycle.md` to call — nothing under
`rqa/intake/` calls either after `create`'s own INSERT (`create` sets `status='queued'` literally, not
through `set_status`). `code/P-03-policy.md` §3's own note is what fixes `set_snapshot_hash`'s owner:
"P-02 persists the returned `hash` onto the job row after a successful first pin (`container.md` §5:
`jobs` is written by P-01, `job_state` by P-02)" — `jobs`'s "written by P-01" in `container.md` §5
means *row creation*; these two columns are the documented exceptions, exactly as `container.md`'s
separate `job_state` row already carves `status` out, and `code/P-03-policy.md` extends the same
carve-out to `snapshot_hash`.

## 6. Record entries written

**P-01 writes no record entries.** The closed fourteen kinds are `transition`, `plan`,
`carry_over`, `bundle`, `attestation`, `spend`, `panel`, `judgement`, `grant`, `action`,
`escalation`, `decision`, and `legacy`; none represents intake-owned state. Concretely:

- Job creation and the `pr_facts` upsert are captured durably in `jobs`/`pr_facts` themselves — a
  plain SQLite write, not an append-only ledger entry — and neither discards a fact a reader needs;
  `rqa explain`'s reconstruction reads `record_entries` alone (`code/P-12-record.md` §1: "no module in
  `rqa.record`… reads `jobs`… or any other table `container.md` §5 assigns to a different writer"),
  and its job-identity resolution comes from `transition` payloads Lifecycle writes, not from this
  part's tables (`code/P-12-record.md` §3.1: `resolve_job` reads only `record_entries`).
- The lease mutation itself is GitHub-facing, and `action`'s payload — "mutation id, kind, GitHub
  response" (`architecture.md` §10) — is data only P-09 has; `claim_lease`/`release_lease` produce
  it, so any `action` entry for a lease mutation is P-09's to write, not this part's.
- An admission refusal (§3 step 2a) has no job to record against — no job exists yet for a repository
  that fails admission — and a per-job dispatch fault (§3 step 5c, U-DISPATCH-22) is caught precisely
  because it escaped whatever transactional state Lifecycle's own containment could safely commit
  against; recording either into the hash-chained ledger would mean inventing a fifteenth kind or
  writing against a transaction already known to be unsound. Both go to the tick's own process log
  instead (`log`, §3) — the same "tick log" `architecture.md`'s risk table already names ("Policy file
  invalid or unreadable… The tick log names the repository and the validation error").

## 7. What P-01 does not do

- Does not validate repository configuration content itself. The admission gate calls P-03's
  `snapshot_for(job=None)` and relays its `ValidationFailure`; it never reimplements schema or
  semantic checks, and never reads `.rqa/config.json` directly.
- Does not write `jobs.status` or `jobs.snapshot_hash` after a row's initial `INSERT`. Every later
  value is Lifecycle's write (§5).
- Does not resolve, cache, or reason about GitHub identity (a login, a user node id). P-09 determines
  and reports which identity a lease mutation is performed as/against; this part's `leases` table
  carries only the local exclusivity key `(job_id, repo, number)`.
- Does not call a harness, judge evidence, grant authority, or decide a disposition. It creates jobs
  and hands them to Lifecycle; every downstream decision belongs to `flow-review-lifecycle.md`'s
  later steps and the parts that perform them.
- Does not decide when a lease may be claimed or released. P-02 obtains and reports the relevant
  `review` grant; P-01's supplied callbacks then make the E-01 mutation and maintain the local row.
- Does not retry a `LeaseTaken` or `GithubUnavailable` claim result within the same tick. P-02 decides
  the corresponding lifecycle transition; its resulting `JobStatus` alone decides whether the next
  tick offers the job again.
- Does not persist an adaptive sweep interval, a per-repository cadence row, or any "next due" state.
  The launchd timer (U-QUEUE-08, outside this part) fires at a fixed interval; every `tick()` attempts
  a full sweep (§3, preamble).
- Does not write to `record_entries` (§6).
- Does not detect or react to a PR closing outside RQA. `flow-review-lifecycle.md` §3 step 2 names
  only the head-change supersede path; a closed PR's existing job simply stops appearing in future
  inventories and is neither advanced nor explicitly closed by this part.
- Does not know or care whether a job in its batch is brand new or resuming after a crash; that
  distinction is read from `job.status` only inside Lifecycle's own contract (§4).

## 8. Tests that prove it

Each is a unit test with fakes for `GithubAdapter`, P-02's `LifecycleDeps` dependencies,
`JobStore`, `PrFactsStore`, `LeaseStore` and `RecordWriter`, except where noted as an integration test
against a real `flock`.

| # | Given | Then |
|---|---|---|
| T1 | `snapshot_for(job=None)` returns `ValidationFailure` | the repo is refused and `github.inventory` is never called |
| T2 | two configured repos; the first is refused and the second inventories one PR | the second still creates a job |
| T3 | lock contention | `tick()` returns `sweep_already_running`; no admission or inventory call occurs |
| T4 | inventory returns `GithubUnavailable` for repo A and facts for repo B | only repo B creates work |
| T5 | one inventory `PrFacts` with `head_repo="alice/fork"` and `head_ref="feature"` | its created `Job` and `PrFactsRow` carry exactly `"alice/fork"` and `"feature"` |
| T6 | the same `(repo, number, head_sha)` is observed twice | the second tick creates no duplicate job |
| T7 | existing head A then inventory head B | successor stores predecessor job id and head A SHA; head repository/ref come from B; predecessor row is unchanged |
| T8 | more resumable jobs than `batch_size` | exactly `batch_size` are selected in `(created_at, id)` order |
| T9 | a resting job has a successor or outstanding local lease | it is appended once to the batch and `revisited_resting_jobs` |
| T10 | P-02 invokes P-01's supplied `claim_lease` callback after it obtains a `review` `Grant` | the callback calls `github.claim_lease(job=job, grant=grant, record=record)` and no call precedes that grant |
| T11 | E-01 claim returns `Mutation` | the callback writes the local `LeaseRow` and returns that unchanged `Mutation` |
| T12 | E-01 claim returns `LeaseTaken` or `GithubUnavailable` | the callback writes no local row and returns the exact unchanged value |
| T13 | E-01 release returns `Mutation` | the callback calls `github.release_lease(job=job, grant=grant, record=record)`, deletes the local row and returns that `Mutation` |
| T14 | E-01 release returns `GithubUnavailable` | the callback retains the local row and returns that unchanged `GithubUnavailable` |
| T15 | every E-01 method fake accepts keyword-only parameters only | inventory, claim and release calls succeed with the exact CONTRACTS.md parameter names |
| T16 | one job enters the batch | P-01 constructs `LifecycleDeps` with every P-02-defined field and calls `admit(job=job, deps=deps)` exactly once |
| T17 | `admit` raises for the first of a two-job batch | `jobs_failed` names the first job and P-01 still calls `admit` exactly once for the second |

Property that must hold across the suite: `grep -n "status" rqa/intake/store.py` shows exactly one
occurrence outside `set_status`'s own definition — the literal `'queued'` inside `create`'s `INSERT`
— proving no other statement in this part ever assigns `jobs.status`.

## 9. Requirements this part answers for

Accountable: RQA-BR-007, RQA-FR-031, RQA-NFR-004, RQA-NFR-006.

- **RQA-BR-007** — *"Review work shall not be duplicated across a revision that has not changed."*
  Fit criterion: "Requesting review twice on an identical revision does not repeat the same reviewer
  work twice." Met by `UNIQUE(repo, number, head_sha)`, the `current_for_pr` guard and P-01's
  post-grant E-01 lease callbacks. Steps: 2c and 5. Tests: T5–T7, T10–T12.
- **RQA-FR-031** — *"One operator running locally shall be able to review pull requests across at
  least two independently configured repositories under different GitHub owners or organisations,
  with no centrally hosted service."* Fit criterion: one operator, locally, completes a review on
  each of two repositories under two different owners, with no central service. Met by the
  per-repository loop (§3 step 2) being isolated and independent — one repo's admission or inventory
  outcome never gates another's — and by the whole of `tick()` running as one local process against
  one local `state.db`, never a shared or hosted component. Steps: 2 (the loop itself), 1 (the local
  exclusive lock, not a server). Tests: T5, T6, T17.
- **RQA-NFR-004** — *"The system shall operate across multiple repositories and multiple
  organisations, including both public and private repositories under different owners."* Fit
  criterion: a review completes on a repository under one organisation and a genuinely different one
  under another, one public and one private. Served by the same per-repository independence as
  RQA-FR-031 above — nothing in the loop distinguishes a public repository from a private one, an
  owner from another owner, or reads any cross-repository state. Steps: 2. Tests: T5, T6, T17.
- **RQA-NFR-006** — *"One contributor shall be able to run the complete review workflow locally, with
  no central hosting, tenancy or SaaS functionality required."* Fit criterion: a policy or
  configuration change is applied and takes effect without any build or deployment step (shared with
  RQA-NFR-005) — read together with flow step 1's citation of this requirement at the admission gate:
  a fail-closed, *enforced* gate (not merely reported, per U-POLICY-07's disposition: "readiness is
  not reported, it is enforced") is what lets one contributor's local process refuse to act on bad
  local state, rather than depending on any external control plane to catch it. Steps: 1 (the
  exclusive local lock — no server coordinates two invocations), 2a (the admission gate). Tests: T1,
  T2, T4.
