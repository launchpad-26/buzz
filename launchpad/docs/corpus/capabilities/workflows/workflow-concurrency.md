---
id: capabilities-workflows-workflow-concurrency
type: capabilities
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 131b02f989684117d9ab1dd426f1673fa638e523."
    entry_class: FACT
    evidence:
      - "commit 131b02f989684117d9ab1dd426f1673fa638e523"
  - statement: "node.schema.json's type enum has no member specific to a runtime behavioral limit; capabilities is the closest match and, at this revision, no sibling node under launchpad/docs/corpus/capabilities/workflows/ has merged yet to establish precedent for this Feature's batch, so the choice is reasoned rather than confirmed against a merged example."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
    confidence: 0.7
  - statement: "WorkflowConfig declares a max_concurrent: usize field documented as the maximum number of concurrently executing workflow runs, defaulting to 100."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/lib.rs:60"
      - "crates/buzz-workflow/src/lib.rs:68"
  - statement: "WorkflowEngine holds a run_semaphore: Arc<tokio::sync::Semaphore> field, and WorkflowEngine::new constructs it with config.max_concurrent.max(1) permits, so a configured value of zero is coerced to a minimum of one permit rather than blocking every run."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/lib.rs:79"
      - "crates/buzz-workflow/src/lib.rs:110-111"
  - statement: "executor::execute_run and executor::execute_from_step each call engine.run_semaphore.try_acquire() as their first action, and map an acquisition failure to WorkflowError::CapacityExceeded before any run-status update or step execution occurs."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/executor.rs:1059-1064"
      - "crates/buzz-workflow/src/executor.rs:1109-1114"
  - statement: "try_acquire (as opposed to acquire) is non-blocking: it returns immediately with an error when no permit is free rather than waiting for one, so a run that cannot get a permit is rejected immediately instead of being queued."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/executor.rs:1058"
      - "crates/buzz-workflow/src/executor.rs:1108"
  - statement: "WorkflowError::CapacityExceeded renders as the message 'capacity exceeded' and maps to the stable code capacity_exceeded via WorkflowError::code()."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/error.rs:49-51"
      - "crates/buzz-workflow/src/error.rs:78"
  - statement: "WorkflowEngine::finalize_run persists a run that failed with any WorkflowError (including CapacityExceeded) as RunStatus::Failed, storing the error's code() and Display message as the run's failure record, rather than retrying or leaving the run pending."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/lib.rs:278-303"
  - statement: "Every call site in the repository that constructs a live WorkflowConfig for a WorkflowEngine used in the relay binary uses WorkflowConfig::default(), including the production entry point in main.rs; no environment variable or configuration field overrides max_concurrent in production."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:435"
      - "crates/buzz-relay/src/router.rs:579"
      - "crates/buzz-relay/src/state.rs:1425"
  - statement: "The semaphore and its permit count are scoped to a single WorkflowEngine instance (one per relay process), not to an individual workflow definition, channel, or owner, so the 100-run ceiling is shared across every workflow run this process is currently executing regardless of which workflow definition, channel, or community triggered it."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-workflow/src/lib.rs:74-79"
      - "crates/buzz-workflow/src/lib.rs:107-123"
    confidence: 0.85
  - statement: "Both callers of the semaphore span every path that creates a workflow run: on_event's per-triggered-event spawn, the 60-second cron/interval loop's spawn, and execute_from_step's approval-resume path all acquire from the same run_semaphore before any steps execute."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/lib.rs:723-738"
      - "crates/buzz-workflow/src/lib.rs:1046-1057"
      - "crates/buzz-workflow/src/executor.rs:1051-1064"
      - "crates/buzz-workflow/src/executor.rs:1099-1114"
  - statement: "The only automated tests touching max_concurrent assert that WorkflowConfig::default() carries the value 100 and that a custom value passed at construction time is preserved; no test in the repository drives the semaphore to exhaustion or asserts CapacityExceeded is returned or persisted end-to-end."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/lib.rs:1321-1326"
      - "crates/buzz-workflow/src/lib.rs:1544-1554"
  - statement: "A separate at-most-once claim mechanism for scheduled (cron/interval) trigger fires exists in the same file to prevent duplicate runs across relay pods and restarts, but it deduplicates which trigger instant creates a run rather than throttling how many runs may execute at once, so it is a distinct concept from the concurrency ceiling this node documents."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/lib.rs:683-693"
---

# Workflow run concurrency limit

The workflow engine caps how many workflow runs may execute at the same time on a
single relay process. This is a blunt, process-wide safety valve — not a per-workflow,
per-channel, or per-owner throttle — that exists so an unbounded burst of triggered
runs cannot exhaust the process. This node documents that ceiling: how it is enforced,
what happens when it is hit, and what it deliberately does not cover.

## Capability and primary actors

- **`WorkflowEngine`** (`crates/buzz-workflow/src/lib.rs`) owns a single
  `tokio::sync::Semaphore` (`run_semaphore`), sized from
  `WorkflowConfig.max_concurrent` (default `100`) at construction time. A configured
  value of `0` is coerced to a minimum of `1` permit.
- **Every code path that creates and executes a run** shares this one semaphore:
  event-triggered runs (`WorkflowEngine::on_event`'s per-event spawn), scheduled runs
  (the 60-second cron/interval background loop's spawn), and approval-resumed runs
  (`executor::execute_from_step`). Each acquires a permit before doing any work.
- **`executor::execute_run`** and **`executor::execute_from_step`** are the two entry
  points that actually enforce the limit: both call `run_semaphore.try_acquire()` as
  their very first action, before the run's status is even updated to `Running`.

## Behavioral rules

1. **Fail-fast, no queue.** `try_acquire()` is non-blocking. If every permit is
   currently held, the call returns an error immediately — there is no wait queue and
   no backpressure signal to the trigger source. The caller does not retry.
2. **Rejection is a normal run failure, not a crash or a dropped event.** A failed
   acquisition maps to `WorkflowError::CapacityExceeded` ("capacity exceeded", stable
   code `capacity_exceeded`). `WorkflowEngine::finalize_run` persists this exactly
   like any other run-level error: the run is marked `Failed` with that code and
   message recorded. There is no automatic retry and no re-queueing — the run is done.
3. **Scope is the whole process, not a workflow definition.** The semaphore lives on
   `WorkflowEngine`, of which the relay constructs one instance per process (every
   production call site builds it from `WorkflowConfig::default()`, e.g. the relay's
   own startup). The 100-permit ceiling is therefore shared by every workflow run this
   process is currently executing, across every workflow definition, channel, and
   community it serves — a single busy workflow can exhaust the budget for all others
   on the same pod. There is no per-workflow-definition "concurrency group," no
   per-channel limit, and no per-owner limit.
4. **Not configurable in production today.** `WorkflowConfig.max_concurrent` is a
   plain struct field with a hardcoded default of `100`; no environment variable or
   relay configuration surface overrides it. Every production and test construction
   site observed in the repository uses `WorkflowConfig::default()`.
5. **The permit is held for the full run, not just admission.** The acquired
   `Semaphore::Permit` (`_permit` in both entry points) is a local binding that is
   dropped only when `execute_run`/`execute_from_step` returns, so the permit is held
   for the entire sequential execution of the run's steps, not merely at admission
   time.

## What this is not

- **Not the scheduled-fire dedupe claim.** A separate mechanism (the
  `(community_id, workflow_id, scheduled_for)` claim row) guarantees at-most-once
  firing of cron/interval triggers across relay pods and restarts. That mechanism
  decides *whether a trigger instant is allowed to create a run at all*; this node's
  semaphore decides *whether an already-created run gets to execute right now*. They
  are independent and can both apply to the same scheduled run.
- **Not a rate limiter on trigger volume.** Nothing here throttles how many events or
  schedule ticks can attempt to create runs — `create_workflow_run` is called
  unconditionally before the semaphore is ever touched. The limit only bites at
  execution time, once a run row already exists.
- **Not per-workflow, per-channel, or per-owner.** See rule 3 above; there is
  currently no mechanism narrower than "the whole process" documented in the code.

## Maturity and verification gap

The mechanism is small and directly readable in code, but its runtime behavior under
load is unverified by any automated test found in the repository: the only tests
exercising `max_concurrent` check that `WorkflowConfig::default()` yields `100` and
that a custom value survives construction. No test drives the semaphore to exhaustion
or asserts that a rejected run is actually persisted as `Failed`/`capacity_exceeded`.
A reader relying on this capability for operational safety should treat the
fail-fast/no-retry/no-backpressure behavior described above as read from source, not
as demonstrated by a passing test.

## Links

- Implementation: `crates/buzz-workflow/src/lib.rs` (`WorkflowConfig`, `WorkflowEngine`,
  `finalize_run`, `on_event`, the cron/interval `run` loop), `crates/buzz-workflow/src/executor.rs`
  (`execute_run`, `execute_from_step`), `crates/buzz-workflow/src/error.rs`
  (`WorkflowError::CapacityExceeded`).
- Construction site (production): `crates/buzz-relay/src/main.rs`.
- Verification (partial only — see Maturity gap above): `crates/buzz-workflow/src/lib.rs`
  (`workflow_config_defaults` and the neighboring custom-value test), which cover the
  `max_concurrent` field's default and pass-through but not semaphore enforcement.

## Scope and omissions

**This node covers** the process-wide `run_semaphore` concurrency ceiling on workflow
run execution: what enforces it, what happens on rejection, its scope, and its
current lack of configurability.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The scheduled-fire at-most-once claim/dedupe mechanism | a sibling `capabilities/workflows/*` task (e.g. schedule-trigger) |
| `workflow-run` lifecycle/status model generally | `capabilities/workflows/workflow-run.md` (sibling task, unmerged at this revision) |
| Whether `max_concurrent` should become configurable, or the ceiling made per-definition/per-channel | not decided anywhere found in the repository; would need a separate implementation issue |
| Load-tested behavior of the semaphore under real contention | no automated test exists at this revision; noted above as a maturity gap |
