# P-11 Escalation — code-level contract

This is the implementation contract for one part of the design in
[`../architecture.md`](../architecture.md). An agent implementing P-11 builds exactly what is here;
an agent implementing a neighbour calls exactly what is here. Anything not stated is the implementer's
choice, provided the stated shape, behaviour and tests hold. Contract ids (`E-NN`) and record names
are those of [`../components.md`](../components.md) §6 and [`../container.md`](../container.md) §5.

**Responsibility, in one sentence.** Be the human seam: raise a durable, named escalation naming one
of five closed causes with a specific question, index what is open, and record a human's decision —
actor, basis, and what it substantiates — as a fact P-02 resumes from. Never push a notification.

**Depends on.** ADR-D ([#2157](https://github.com/launchpad-26/buzz/issues/2157), assumed) for the
no-verdict-authority outcome. It reads P-01 jobs through a narrow read-only protocol and calls P-02
resume through E-11; shared escalation/decision values remain canonical.

## 1. Modules

rqa/escalation/
  __init__.py     re-exports: raise_, pending, decide, EscalationCause, Escalation,
                  Decision, EscalationRefused, EscalationRefusalReason, EscalationError
  escalate.py     Escalation; raise_() and pending(): the E-11 entry points
  decide.py       EscalationRefused, EscalationRefusalReason; decide(): the E-17 `decide` CLI entry point;
                  the JobReader and P-02 resume Protocols this part depends on
  store.py        the `human_requests` table and the EscalationStore protocol

No other module in RQA imports from `rqa.escalation` except through `__init__`. No module in
`rqa.escalation` imports from any other part except `rqa.contracts` (the shared types named in
`CONTRACTS.md` §1 and §6) and `rqa.record` (to append the `escalation` and `decision` entries). It
never imports `rqa.intake` or P-02's lifecycle implementation: the `Job` value arrives as an argument
to `raise_()`, while the read of the job's current head/snapshot and the call into P-02 are Protocols
declared in `decide.py` that the caller satisfies at wiring time. P-11 never reads `jobs.status` or
writes it — only P-02 changes a job's state.

## 2. Types

`EscalationCause`, `Decision`, `Escalation`, `EscalationRefusalReason`, and
`EscalationRefused` are boundary values defined only in [`CONTRACTS.md`](CONTRACTS.md) §6. P-11
imports and uses them unchanged:

```python
from rqa.contracts import (
    EscalationCause, Decision, Escalation, EscalationRefusalReason, EscalationRefused,
)

class EscalationError(Exception):
    """Programming error: raise_() or decide() received a value outside the shared contract."""
```

`EscalationCause` is the whole RQA-FR-026 vocabulary. There is no `other` or free-text cause.

`Job` is P-01's type, consumed here read-only. `raise_()` reads exactly three fields:

```python
job.id: str
job.head_sha: str
job.snapshot_hash: str      # already pinned by the time raise_() is ever called (flow step 3/3a)
```

## 3. Entry points

### E-11 `raise_`

```python
def raise_(*, job: Job, cause: EscalationCause, question: str, context: Mapping, record: RecordWriter,
           store: EscalationStore) -> Escalation: ...
```

**Behaviour, in order. Every branch returns or raises.**

1. `cause not in EscalationCause` → raise `EscalationError`. Routine conditions never reach this
   module; this is the precondition P-02 enforces by construction (it only ever calls `raise_` from
   step 3a or step 9b/10a with one of the five) and the assertion P-11 makes anyway.
2. `question.strip() == ""` → raise `EscalationError`. RQA-FR-026 requires a *specific* question, not a
   generic "needs attention"; an empty string can never be specific.
3. `raised_at = utcnow()` captures the time this escalation is raised.
4. `record.append(job.id, kind="escalation", payload={"cause": cause.value, "question": question,
   "context": dict(context), "head_sha": job.head_sha, "snapshot_hash": job.snapshot_hash})`. If this
   raises `AppendFailed`, it propagates: the caller's transition fails with it (E-13), and no pending
   index row is written — there is never an index row without a record entry behind it.
5. `store.insert(job_id=job.id, entry_seq=entry.seq, cause=cause, question=question, context=context,
   head_sha=job.head_sha, snapshot_hash=job.snapshot_hash, raised_at=raised_at)` writes the open pending
   row and returns its id.
6. Return `Escalation(id, job.id, cause, question, context, job.head_sha, job.snapshot_hash,
   entry.seq, raised_at)`.

**No transport.** Nothing above sends mail, writes a file outside the store, executes a command, or
opens a socket. This is the whole of what U-AUTHORITY-12's binning leaves for RQA-FR-025/RQA-BR-013 to
mean at this layer: the escalation *is* the durable request; there is no delivery step to add one.

### E-11 `pending`

```python
def pending(*, store: EscalationStore) -> tuple[Escalation, ...]: ...
```

**Behaviour.** One branch: return every open row from `store.pending()` — ordered by `raised_at`
ascending, oldest first — as its complete `Escalation` value. Always returns; an empty state directory
yields an empty tuple. This is the whole of the human-facing surface `rqa status`/the `decide` CLI
reads before asking the operator which escalation they mean.

### E-17 `decide`

```python
def decide(
    escalation_id: int,
    actor: str,
    basis: str,
    outcome: Literal["approved", "changes_requested"] | None = None,
    *,
    store: EscalationStore,
    record: RecordWriter,          # E-13
    jobs: JobReader,                # read of P-01's `jobs.head_sha` / `jobs.snapshot_hash`
    lifecycle: LifecycleResume,     # P-02's resume(), the reverse edge of E-11
    deps: LifecycleDeps,            # P-02's dependency bundle; supplied by P-01 at wiring time
    clock: Callable[[], datetime] = utcnow,
) -> Decision | EscalationRefused:
```

**Behaviour, in order. Every branch returns or raises.**

1. `actor.strip() == ""` → raise `EscalationError`. RQA-FR-013 requires the approving human be named;
   an unnamed actor is a malformed call, not a business outcome.
2. `basis.strip() == ""` → raise `EscalationError`. RQA-FR-013's other half: a nameless basis is exactly
   the defect U-AUTHORITY-06 rebuilt this entry point to close.
3. `outcome is not None and outcome not in ("approved", "changes_requested")` → raise `EscalationError`.
   A closed vocabulary; there is no third outcome.
4. `escalation = store.get(escalation_id)`; if `None` → `EscalationRefused(NOT_FOUND, detail=f"no escalation
   {escalation_id}")`. An operator can mistype an id read from an old terminal; that is not a
   programming error.
5. `escalation.status != "open"` → `EscalationRefused(ALREADY_CLOSED, detail=...)`. Covers a second `decide` on
   the same id and a decide raced by intake closing the escalation as superseded (flow step 2).
6. `outcome is not None and escalation.cause is not EscalationCause.AUTHORITY_REQUIREMENT` → raise
   `EscalationError` [ADR-D assumed]. Recording an outcome only makes sense where RQA itself could not
   act and the human acted on GitHub in its place (flow step 12b); for the other four causes the human
   is answering a question, not reporting a GitHub-side verdict.
7. `current = jobs.current(escalation.job_id)`; `current is None or current.head_sha != escalation.head_sha`
   → `EscalationRefused(HEAD_MOVED, detail=f"job head is now {current.head_sha if current else '<gone>'}")`. A
   decision made against a superseded revision would authorise something no longer under review.
8. `current.snapshot_hash != escalation.snapshot_hash` → `EscalationRefused(SNAPSHOT_MOVED, detail=...)`. The
   rules changed under the escalation; the decision cannot be pinned to what it was asked against.
9. `substantiates = escalation.context.get("obligation") if escalation.cause is not
   EscalationCause.AUTHORITY_REQUIREMENT else None`.
10. `decision = Decision(actor=actor.strip(), basis=basis.strip(), substantiates=substantiates,
    outcome=outcome)`.
11. `record.append(escalation.job_id, kind="decision", payload={"escalation_id": escalation_id,
    "cause": escalation.cause.value, "actor": decision.actor, "basis": decision.basis,
    "substantiates": decision.substantiates, "outcome": decision.outcome})`. If this raises
    `AppendFailed`, it propagates: the escalation stays open, `store.close` is never reached, and
    `lifecycle.resume` is never called — a decision that was not recorded never resumes anything.
12. `store.close(escalation_id, decision_entry_seq=entry.seq, closed_at=clock())`.
13. `lifecycle.resume(job_id=escalation.job_id, decision=decision, deps=deps)`. Signals P-02 with the
    id of the `Job` validated at steps 7–8 and P-02's `LifecycleDeps`. What P-02 does with it
    (re-enter judgement at step 8, or verify the human's GitHub-side outcome and transition directly,
    per flow step 12) — and the `JobStatus` it returns — is outside this part; `decide()` does not
    branch on the return value (see guarantees).
14. Return `decision`.

**Guarantees the caller may rely on.**
- A `Decision` is never returned without both a `decision` record entry and a closed index row already
  in place; `lifecycle.resume` is never called before both exist.
- `outcome` is non-`None` on the returned `Decision` only when `escalation.cause` was
  `authority_requirement`; `substantiates` is non-`None` only when it was not.
- Deterministic refusal: the same stale `(escalation_id, current head, current snapshot)` always
  refuses the same way, decided once, at steps 7–8, before anything is written.
- `lifecycle.resume`'s `JobStatus` return value is never inspected or branched on: decide()'s own
  stale check is what "refused" means for this contract (U-AUTHORITY-05's mechanism, placed in P-11);
  once the `decision` entry is appended it stands as a durable historical fact whether or not P-02 can
  still apply it downstream. P-02's own equivalent check on the same job id is a defensive backstop on
  its side of the call, not a second source of truth P-11 reacts to.
- Never touches the network or the filesystem beyond the store and the record.

## 4. Dependencies consumed

`resume` is the reverse E-11 edge catalogued in `CONTRACTS.md` §9. P-11 declares only the narrow
Protocol it receives at wiring time; its method signature is the canonical P-02 signature, and
`LifecycleDeps` is P-02's type, defined in `P-02-lifecycle.md`.

```python
# decide.py — P-11: P-01 supplies this read-only P-01 jobs view at wiring time.
class JobReader(Protocol):
    def current(self, job_id: str) -> Job | None: ...

# P-02 supplies this E-11 reverse edge. LifecycleDeps is defined by P-02.
class LifecycleResume(Protocol):
    def resume(self, *, job_id: str, decision: Decision, deps: LifecycleDeps) -> JobStatus: ...
```

`JobReader` is read-only access to P-01's `jobs` table via the shared `Job` value — `container.md` §5
names P-11 among its readers for exactly this purpose — never a second copy of job state.
`LifecycleResume` is P-02's `resume`; P-11 calls it with the validated escalation job id, the decision,
and the caller-provided `LifecycleDeps`, and never inspects its `JobStatus`.

P-11 imports the canonical `RecordWriter`, `Entry`, and `AppendFailed` contracts from
`CONTRACTS.md` §7 unchanged.

## 5. Store

```sql
CREATE TABLE human_requests (
  id                  INTEGER PRIMARY KEY,
  job_id              TEXT NOT NULL,
  entry_seq           INTEGER NOT NULL,      -- seq of the `escalation` record entry that raised this
  cause               TEXT NOT NULL,         -- one of the five EscalationCause values
  question            TEXT NOT NULL,
  context             TEXT NOT NULL,         -- JSON object
  head_sha            TEXT NOT NULL,         -- job.head_sha at raise_() time
  snapshot_hash       TEXT NOT NULL,         -- job.snapshot_hash at raise_() time
  raised_at           TEXT NOT NULL,         -- ISO-8601 UTC
  status              TEXT NOT NULL DEFAULT 'open',   -- 'open' | 'closed'
  closed_at           TEXT,                  -- ISO-8601 UTC; set by close()
  decision_entry_seq  INTEGER,               -- seq of the `decision` entry that closed this row
  UNIQUE (job_id, entry_seq)
);
CREATE INDEX human_requests_status ON human_requests (status);
```

No `decision_actor`, `rationale`, or notification-transport column: `decision_actor`/`rationale`
migrate onto the `decision` record entry (§6) rather than this index — the index answers "what is
open", never "what was decided" — and the transport columns (`transport`, `delivered_at`, and
whatever routing key selected file/command/none) have no successor at all (U-AUTHORITY-12, bin).

```python
# store.py
@dataclass(frozen=True)
class EscalationRow:
    id: int
    job_id: str
    entry_seq: int
    cause: EscalationCause
    question: str
    context: Mapping[str, str]
    head_sha: str
    snapshot_hash: str
    raised_at: datetime
    status: Literal["open", "closed"]
    closed_at: datetime | None
    decision_entry_seq: int | None

class EscalationStore(Protocol):
    def insert(
        self, *, job_id: str, entry_seq: int, cause: EscalationCause, question: str,
        context: Mapping[str, str], head_sha: str, snapshot_hash: str, raised_at: datetime,
    ) -> int: ...                                              # returns the new row's id
    def get(self, escalation_id: int) -> EscalationRow | None: ...
    def pending(self) -> tuple[EscalationRow, ...]: ...         # status = 'open', raised_at ascending
    def close(self, escalation_id: int, *, decision_entry_seq: int, closed_at: datetime) -> None: ...
```

Written only by P-11. Read by P-02, which needs to know whether a job it is asking about has an open
escalation (`container.md` §5: readers of `human_requests` = P-02).

## 6. Record entries written

| kind | when | payload |
|---|---|---|
| `escalation` | every call to `raise_()` | `cause`, `question`, `context`, `head_sha`, `snapshot_hash` |
| `decision` | every call to `decide()` that does not raise or return `EscalationRefused` | `escalation_id`, `cause`, `actor`, `basis`, `substantiates`, `outcome` |

This is where RQA-FR-013's previously-missing `actor` and `basis` columns live, and it is what
`container.md` §5 calls the `approval_decisions` → `decision` migration.

## 7. What P-11 does not do

- Does not send a notification, email, webhook, or write any file-based or command-based transport —
  U-AUTHORITY-12 is binned with no successor; the durable record is the whole of the human-facing
  channel, and the human reads `pending()` on their own schedule.
- Does not decide *whether* a condition merits escalation, or which of the five causes applies — P-07
  proposes the cause (`Judgement.escalation_causes`) and P-02 chooses to call `raise_`; P-11 only
  records the answer it is given and asserts it is one of the five.
- Does not touch `jobs.status` or any other part's table; it writes only `human_requests` and appends
  only through P-12.
- Does not verify a human's claimed GitHub-side outcome (that the CHANGES_REQUESTED or APPROVED review
  is actually visible at the recorded head) — that check is P-02's, through E-23, at flow step 12b
  [ADR-D assumed]; P-11 only carries the human's stated `outcome` into the record.
- Does not re-run judgement, plan a review, or call a harness; `lifecycle.resume` is a signal, not a
  re-entry P-11 performs itself.
- Does not expire, time-box, or auto-close an escalation; how long one may rest open is repository
  governance, not a frozen requirement (`flow-review-lifecycle.md` §7/§8).
- Does not touch the network or any file outside its own SQLite rows and the record it appends to.
- Does not accept a sixth cause, a blank question, or a free-text escalation of any kind.

## 8. Tests that prove it

Each is a unit test with fakes for `RecordWriter`, `EscalationStore`, `JobReader`, `LifecycleResume`,
and P-02's `LifecycleDeps`.

| # | Given | Then |
|---|---|---|
| T1 | `raise_` is called once per `EscalationCause` with its complete E-11 keyword-only shape: `job`, `cause`, `question`, `context`, `record`, `store` | five `escalation` entries, each naming its own cause; `pending(store=store)` lists five complete open `Escalation` values |
| T2 | `raise_` called with a cause outside the five (a raw string coerced past the enum) | `EscalationError`; no `escalation` entry, no index row |
| T3 | `raise_` called with `question=""` (or all-whitespace) | `EscalationError`; no entry, no row |
| T4 | `raise_(job=..., cause=..., question=..., context=..., record=..., store=...)`; `record.append` raises `AppendFailed` | exception propagates; no index row written |
| T5 | `decide(actor="")` | `EscalationError`; no `decision` entry, `store.close` and `lifecycle.resume` never called |
| T6 | `decide(basis="  ")` | `EscalationError`; same as T5 |
| T7 | `decide(escalation_id, actor, basis, outcome="approved")` on an `evidence_gap` escalation | `EscalationError` [ADR-D assumed]; no entry |
| T8 | `decide(..., outcome="approved")` on an `authority_requirement` escalation | shared `Decision(outcome="approved", substantiates=None)`; `decision` entry recorded |
| T9 | `decide(..., outcome=None)` on a `required_information` escalation whose `context={"obligation": "OBL-3"}` | shared `Decision(substantiates="OBL-3", outcome=None)` |
| T10 | `decide` where `jobs.current(job_id).head_sha` differs from the escalation's `head_sha` | `EscalationRefused(HEAD_MOVED)`; escalation stays open; no `decision` entry; `lifecycle.resume` not called |
| T11 | `decide` where `head_sha` matches but `snapshot_hash` differs | `EscalationRefused(SNAPSHOT_MOVED)`; same non-effects as T10 |
| T12 | `decide` with an id `store.get` returns `None` for | `EscalationRefused(NOT_FOUND)` |
| T13 | `decide` called twice on the same escalation | first call returns a shared `Decision`; second returns `EscalationRefused(ALREADY_CLOSED)` |
| T14 | a successful `decide` | the `decision` entry payload carries `escalation_id`, `cause`, `actor`, `basis`, `substantiates`, `outcome` — all six readable back |
| T15 | a successful `decide` | the `human_requests` row is closed: `status="closed"`, `decision_entry_seq` set to the entry's `seq`; `pending(store=store)` no longer lists it |
| T16 | a successful `decide` with `deps` | `lifecycle.resume` is called exactly once as `resume(job_id=escalation.job_id, decision=decision, deps=deps)`; its `JobStatus` return is ignored |
| T17 | `decide`; `record.append` raises `AppendFailed` | exception propagates; the row stays open; `store.close` and `lifecycle.resume` never reached |
| T18 | `raise_`, `pending`, and a full successful `decide`, with `socket.socket.__init__` monkeypatched to raise | all three calls complete unchanged; zero socket constructions attempted |
| T19 | `pending(store=store)` with no open escalations | `()` |

## 9. Requirements this part answers for

Accountable: RQA-BR-011, RQA-BR-013, RQA-FR-013, RQA-FR-025, RQA-FR-026, RQA-NFR-033.

- **RQA-FR-026** — *"Every escalation record names one of the five listed causes concretely, not as a
  generic 'needs attention' notice."* Met by `raise_` step 1 (closed `EscalationCause`, no sixth value)
  and step 2 (a blank question can never stand in for a specific one). T1, T2, T3.
- **RQA-FR-025** and **RQA-BR-013** — *"No condition genuinely requiring no human judgement ever raises
  a notification demanding a human's immediate attention"* / *"...no notification...for a condition
  that did not need one."* Met structurally: §1 and §7 — there is no notification code path in this
  part at all, for any cause; the escalation is a durable row, never a push. T1 (nothing beyond the
  record and the row is written) and T18 (no network access of any kind).
- **RQA-FR-013** — *"A human approval used to satisfy assurance shall name the approving human and the
  basis of that approval."* Met by `decide` steps 1–2 (actor and basis both required non-blank) and
  step 9 (the substantiated obligation is carried from the escalation's own context, not invented at
  decide time). T5, T6, T9, T14.
- **RQA-BR-011** — *"A human approval used to satisfy assurance shall preserve the evidence behind that
  approval, not merely satisfy merge mechanics."* Met by the `decision` entry's complete payload (§6):
  `substantiates` names the specific obligation the approval is evidence for, retrievable by
  `rqa explain` from the record alone. T14.
- **RQA-NFR-033** — *"Before a review containing a behaviour-changing finding completes, its record
  shows that a named human received and considered that finding."* A behaviour-changing finding is
  folded into one of the five causes by P-07/P-02 before `raise_` is ever called (flow step 9b); P-11's
  part of the guarantee is that whichever cause is named is recorded and closed only by a named,
  substantiated decision, never silently. T1 (every cause, including whichever the finding maps to,
  is recorded) and T9 (the decision names the specific obligation).
