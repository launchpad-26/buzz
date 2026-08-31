---
id: capabilities-workflows-workflow-run
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
  - statement: "A merged corpus node, architecture-flows-workflow-execution, already documents the full trigger-to-terminal-state control flow (three trigger paths, preconditions, ordered interactions, trust-boundary crossings, failure/rollback) for workflow execution, so this node scopes itself to the workflow run as a persisted, queryable record rather than re-narrating that flow, and declares a references relationship to it instead."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/flows/workflow-execution.md"
  - statement: "node.schema.json's type enum has thirteen members and capabilities is its own dedicated value, distinct from architecture; no capabilities-typed node is merged anywhere in the corpus at this revision, so there is no merged precedent to follow for this node's own type, and the choice below is this node's own judgment."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "Every merged node under launchpad/docs/corpus/architecture/ carries type: architecture, and this node's target path (launchpad/docs/corpus/capabilities/workflows/workflow-run.md) sits under a capabilities/ directory the corpus-plan tool itself chose for this task, so type: capabilities is chosen by extending that same directory-to-type mapping rather than inventing an independent rule; this is this node's own reasoning, not a restatement of anything node.schema.json or schema/README.md states about the mapping."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/architecture/flows/workflow-execution.md"
      - "launchpad/docs/corpus/schema/node.schema.json"
    confidence: 0.6
  - statement: "RunStatus is a six-variant Rust enum (Pending, Running, WaitingApproval, Completed, Failed, Cancelled) serialized snake_case, backed 1:1 by the Postgres enum run_status ('pending','running','waiting_approval','completed','failed','cancelled')."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/workflow.rs:78-121"
      - "migrations/0001_initial_schema.sql:32"
  - statement: "The workflow_runs table is primary-keyed (community_id, id) with a foreign key on (community_id, workflow_id) referencing workflows(community_id, id) ON DELETE CASCADE, so a run's identity is community-scoped, not globally unique, and deleting its parent workflow deletes every one of its runs."
    entry_class: FACT
    evidence:
      - "migrations/0001_initial_schema.sql:386-405"
  - statement: "WorkflowRunRecord's fields are: id, community_id, workflow_id, status (RunStatus), trigger_event_id (optional raw event id bytes), current_step (0-based), execution_trace (JSON array), trigger_context (optional JSON, nullable for pre-migration rows), started_at/completed_at (optional timestamps), error_message/error_code (optional, kept separate so callers never parse diagnostics), and created_at."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/workflow.rs:192-228"
  - statement: "create_workflow_run inserts a row with status='pending', current_step=0 and execution_trace='[]' unconditionally -- every run, regardless of which of the three trigger paths created it, starts in exactly this state."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/workflow.rs:803-828"
  - statement: "execute_run and execute_from_step each acquire a permit from engine.run_semaphore before doing anything else (WorkflowError::CapacityExceeded if none is free, no queuing), and only after acquiring the permit do they call update_workflow_run to move the row to Running -- and, distinctively, this particular update_workflow_run call is propagated with '?': if the DB write to Running fails, the function returns Err immediately and no step ever executes for that run."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/executor.rs:1051-1085"
      - "crates/buzz-workflow/src/executor.rs:1099-1155"
  - statement: "Within execute_steps (the shared per-step loop for both execute_run and execute_from_step), no call to update_workflow_run exists -- current_step and execution_trace accumulate only in the in-memory ExecutionResult/PartialProgress structs as steps run, and are not written back to the workflow_runs row incrementally; the row is not touched again until finalize_run persists the final outcome in one write."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/executor.rs:1164-1298"
  - statement: "A consequence of the above: a reader who fetches a workflow_runs row while it is Running sees current_step at whatever value it held the moment the row was last written (0 for a fresh run, the resume start index for an approval-resumed one) and the execution_trace from that same moment, never a value reflecting steps that have completed since -- the row's mid-run snapshot is stale by construction, not because of a bug or a race."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-workflow/src/executor.rs:1051-1085"
      - "crates/buzz-workflow/src/executor.rs:1164-1298"
      - "crates/buzz-workflow/src/lib.rs:213-305"
    confidence: 0.85
  - statement: "finalize_run is the single place, called by every execution path, that maps an executor result to the run's terminal persisted state: Completed on a clean pass, or Failed (with a stable error code and the accumulated trace) on any error including the not-yet-implemented approval-suspend case, which is deliberately mapped to Failed with error_code 'approval_not_supported' rather than left as WaitingApproval."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/lib.rs:213-305"
  - statement: "finalize_run's own call to update_workflow_run is not propagated with '?' -- on either branch (Completed or Failed), a DB-write failure is caught, logged via tracing::error!, and swallowed; the function returns () either way, so a run whose terminal write fails is left with whatever status it last held (Running, from the earlier propagated write) with no retry and no code path shown elsewhere in this engine that sweeps or reconciles such a row."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/lib.rs:237-304"
  - statement: "This produces an asymmetry in the run record's own write reliability: the Pending-to-Running transition is fail-closed (a write failure aborts the run before any step executes, per the propagated '?'), while the transition to a terminal state is fail-open from the record's perspective (the run's side effects have already happened; only the row's own status write can silently fail to reflect that)."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-workflow/src/executor.rs:1051-1085"
      - "crates/buzz-workflow/src/lib.rs:237-304"
    confidence: 0.8
  - statement: "Of RunStatus's six values, only Pending, Running, Completed and Failed are ever written by code in this engine; WaitingApproval is defined in the enum and the database type but no code path sets it (the one place that could -- an approval suspend -- is explicitly mapped to Failed instead), and Cancelled is likewise defined but not set by any code path in buzz-workflow."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/workflow.rs:78-93"
      - "crates/buzz-workflow/src/lib.rs:229-256"
  - statement: "get_workflow_run, list_workflow_runs and list_workflow_runs_page are the only read paths over workflow_runs; list_workflow_runs_page orders by (created_at DESC, id DESC) with a keyset cursor, and all three scope every query to a server-resolved community_id, never a client-supplied one."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/workflow.rs:830-902"
  - statement: "buzz-cli's cmd_get_workflow_runs -- the CLI's own run-history command -- queries Nostr kinds [46001, 46002, 46003] rather than reading the workflow_runs table at all; its own doc comment states the relay does not currently emit those kinds and the command 'will return an empty array until the relay adds event emission or a dedicated REST endpoint for run history', so this command is dead code today: it always prints an empty array regardless of how many runs actually exist for the workflow."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/commands/workflows.rs:60-95"
  - statement: "buzz-cli has no other command that reads a workflow_runs row (by run id or otherwise) -- cmd_get_workflow_runs is the CLI's only run-facing command, and its query targets the wrong data source entirely."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-cli/src/commands/workflows.rs:1-260"
    confidence: 0.7
  - statement: "The already-merged flow node's own Scope and omissions section independently states that a relay restart mid-run (a Running row whose spawned task was killed) was not traced and that no sweeping/reconciling code path for stuck Running rows was located, though its absence was not exhaustively confirmed -- the same gap this node's finalize_run write-failure finding compounds from a different angle (a live process that simply fails one DB write, not a killed process)."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/flows/workflow-execution.md"
  - statement: "Issue #841's own definition of done requires stating trigger/preconditions/termination, ordered interactions and data/state movement, auth/trust-boundary crossings, and failure/abort/rollback behavior with links to representative verification -- the same four-part shape issue #688 used for the already-merged flow node -- which is why this document is organized around those same four section headings even though its subject (the run record) is narrower than that node's subject (the whole trigger-to-completion flow)."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#841 definition of done"
  - statement: "Sibling issue #840 ('task: document capabilities/workflows/workflow-definition.md') carries a definition of done requiring 'states the capability and primary actors/outcomes', 'defines behavioral rules, constraints and relevant variants', 'links major flows, interfaces, data and platform implementation' -- the capability-template shape -- confirming the batch's own intended split: #840 documents the static workflow definition as a capability, and #841 (this node) documents the runtime run record, not a second capability statement about the same subject."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#840 definition of done (read directly via gh issue view)"
  - statement: "workflow_run_row_maps_status_correctly and the surrounding row-mapping unit tests in buzz-db/src/store/workflow.rs assert that a WorkflowRunRecord constructed with a given RunStatus round-trips through row_to_run_record with that same status, and that cloning a record with a mutated status leaves the original unchanged -- representative verification for the record-shape and status-field claims above."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/workflow.rs:1920-2051"
  - statement: "run_status_display_and_parse_roundtrip (and the neighboring parse-error assertion) in buzz-db/src/store/workflow.rs is a unit test asserting every RunStatus variant's Display output re-parses via FromStr to the same variant, and that an unrecognized string is rejected -- representative verification for the six-value RunStatus claim above."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/workflow.rs:1722-1751"
relationships:
  - type: references
    target: architecture-flows-workflow-execution
---

# Workflow run: capability

A workflow run is one execution attempt of a workflow definition, persisted as a row
in Postgres's `workflow_runs` table and identified by a `RunStatus` value that names
where that attempt currently stands. This node documents the run **as a record**: its
identity, its schema, which `RunStatus` states are actually reachable, how the row is
written and read across its lifetime, and where that persisted state currently fails
to stay trustworthy or observable. It does not re-narrate *how* a run gets triggered
or *what* each step does — `architecture-flows-workflow-execution` already covers the
three trigger paths, the shared step-execution loop, and the trust-boundary crossings
a run's creation and side effects cross, in full, and this node `references` it rather
than duplicating that content.

## Trigger, preconditions, termination

**Creation.** Every run starts identically regardless of which of the three trigger
paths (channel event, schedule, webhook — see the referenced flow node) created it:
`create_workflow_run` inserts a `workflow_runs` row with `status = 'pending'`,
`current_step = 0`, and `execution_trace = '[]'`. The preconditions that must hold
before a run is ever created (definition parses, `enabled`, passes `WorkflowDef::validate()`,
owner authority) are the flow node's own *Trigger, preconditions, termination*
section; this node does not restate them.

**Identity.** A run's identity is `(community_id, id)` — `workflow_runs` is
primary-keyed on that pair, not on `id` alone, and carries a foreign key on
`(community_id, workflow_id)` referencing `workflows(community_id, id)` with
`ON DELETE CASCADE`. Two consequences follow directly: the same run UUID is not
guaranteed unique across communities, and deleting a workflow definition deletes
every run ever recorded against it — there is no independent retention for run
history once its parent workflow is gone.

**Termination — which `RunStatus` values a run can actually reach.** `RunStatus` has
six variants, backed 1:1 by the Postgres `run_status` enum. Of these, only four are
ever written by code in this engine:

| Value | Reached by | Notes |
|---|---|---|
| `Pending` | `create_workflow_run`, unconditionally | Starting state for every run |
| `Running` | `execute_run` / `execute_from_step`, after acquiring a concurrency permit | Write is propagated with `?` — see *Failure, abort, rollback* |
| `Completed` | `finalize_run`, on a clean pass through all steps | |
| `Failed` | `finalize_run`, on any step error, timeout, or the not-yet-implemented approval-suspend case | Carries a stable `error_code` and the accumulated trace |
| `WaitingApproval` | *(defined, never set)* | The one code path that could set it (an approval suspend) is explicitly mapped to `Failed` with `error_code: approval_not_supported` instead |
| `Cancelled` | *(defined, never set)* | No code path in `buzz-workflow` sets this value |

A run therefore terminates in exactly one of two states this engine can produce today
— `Completed` or `Failed` — never `WaitingApproval` or `Cancelled`, whatever those
values might suggest about the product's intended future shape.

## Ordered interactions and data/state movement

The row moves through **at most three writes** across a run's entire lifetime, not one
write per step:

1. **Creation** — `create_workflow_run` inserts the `Pending` row (see above).
2. **Start** — `execute_run` (or `execute_from_step`, for an approval resume) acquires
   a `run_semaphore` permit and writes `status = Running`. `execute_from_step`
   additionally re-reads the row's `execution_trace` first (`get_workflow_run`) so a
   resumed run does not lose its pre-resume trace.
3. **Terminal write** — `finalize_run`, called exactly once by whichever execution
   path invoked the steps, writes the final `status` (`Completed` or `Failed`),
   `current_step`, and the full `execution_trace` in one statement.

**Between writes 2 and 3, the row does not move.** `execute_steps` — the shared
per-step loop both `execute_run` and `execute_from_step` call into — accumulates
`current_step` and each step's trace entry only in an in-memory `ExecutionResult` /
`PartialProgress` value; no call to `update_workflow_run` exists inside it. A caller
reading the row via `get_workflow_run` while a run is `Running` sees whatever
`current_step` and `execution_trace` the row held at write 2 — `0` for a fresh run, or
the resume index for a resumed one — never a value reflecting steps that have
completed since. This is a structural property of the persistence pattern, not a race
or a bug: the row is a two-point snapshot (start, end), not a live progress counter.

**Reads.** `get_workflow_run` (by id), `list_workflow_runs`, and
`list_workflow_runs_page` (newest-first, keyset-paginated on `(created_at, id)`) are
the only read paths over `workflow_runs`, and all three bind a server-resolved
`community_id` — never a client-supplied one — matching the same tenant-confinement
pattern the referenced flow node documents for the write side.

## Trust-boundary crossings

This node adds one boundary observation beyond what the referenced flow node already
covers in full (fence re-verification, owner authority, webhook secret, SSRF
guarding): **the run record's own identity is the tenant boundary for every read.**
Because `workflow_runs` is keyed `(community_id, id)` rather than by a globally unique
run id, every read function above requires a `community_id` argument bound from
server-resolved context, so a run id alone — even if guessed or leaked — cannot be
used to read a run belonging to a different community. This is the same pattern
`workflows` itself uses (see `get_workflow`), applied consistently to its child table.

## Failure, abort, rollback behavior

- **The record's own write reliability is asymmetric.** The `Pending → Running`
  transition (`execute_run` / `execute_from_step`) propagates a DB-write failure with
  `?`: if that write fails, the function returns `Err` immediately and no step ever
  executes. The transition to a terminal state (`finalize_run`) does the opposite: its
  `update_workflow_run` call is wrapped in `if let Err(e) = ... { tracing::error!(...) }`
  and nothing else — the function still returns `()`. A run whose terminal write fails
  is left with `status = Running` (the last value a propagated write actually
  achieved), even though its steps have already fully executed (with whatever side
  effects that entailed) and no further code in this engine retries or reconciles
  that row.
- **This compounds an already-documented gap, from a different angle.** The
  referenced flow node's own *Scope and omissions* states that a relay restart
  mid-run — a `Running` row whose spawned task was killed — was not traced, and that
  no sweeping/reconciling code path for stuck `Running` rows was located. This node's
  finding is narrower and independently verified: even with no restart and no killed
  process, a single failed DB write inside a still-running engine produces the same
  visible symptom — a `workflow_runs` row stuck at `Running` forever.
- **The record is effectively unobservable through the one CLI command meant to read
  it.** `buzz-cli`'s `cmd_get_workflow_runs` queries Nostr kinds `[46001, 46002,
  46003]` for run history rather than reading `workflow_runs` — kinds the relay does
  not emit (also independently established by the referenced flow node for the wider
  `46001`–`46012` range). The command's own doc comment acknowledges this: it "will
  return an empty array until the relay adds event emission or a dedicated REST
  endpoint for run history." A run can be `Completed`, `Failed`, or silently stuck at
  `Running` per the point above, and this command will print `[]` in every case.
  `buzz-cli` has no other command that reads a `workflow_runs` row directly.
- **Representative verification:**
  - `crates/buzz-db/src/store/workflow.rs:1920-2051` — unit tests asserting a
    `WorkflowRunRecord`'s `RunStatus` round-trips through row mapping and that cloning
    with a mutated status leaves the original unchanged.
  - `crates/buzz-db/src/store/workflow.rs:1722-1751` — unit tests asserting every
    `RunStatus` variant's `Display` output re-parses via `FromStr` to the same
    variant, and that an unrecognized string is rejected.
  - No test in this repository was found exercising `finalize_run`'s error-branch
    logging path, the `execute_steps` no-intermediate-write behavior, or
    `cmd_get_workflow_runs`'s empty-array behavior directly — all three claims above
    rest on reading the source, not on a passing test naming them (see *Scope and
    omissions*).

## Scope and omissions

**This node covers** the workflow run as a persisted record: its identity and schema,
which `RunStatus` values are reachable, the exact write points across its lifetime,
the community-scoped read boundary, and two failure-mode findings specific to the
record's own write and read reliability (the fire-and-forget terminal write, and the
CLI's dead run-history command).

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The three trigger paths, per-step execution semantics, and the full trust-boundary/failure narrative for the flow as a whole | `architecture-flows-workflow-execution` |
| The workflow *definition*'s own shape, validation rules, and capability statement | `#840` (`capabilities/workflows/workflow-definition.md`, unmerged at this revision) |
| The approval-gate resume flow's intended design, once built (WF-08) | Not yet implemented; both this node and the referenced flow node treat `WaitingApproval` as unreachable today |
| Whether a relay-side reconciliation job for stuck `Running` rows should be built | Not filed as its own issue at this revision |

**Expected but not verified when this node was written:**

- **No test was found exercising `finalize_run`'s error-logging branch directly** —
  the fire-and-forget behavior is read from the source (`if let Err(e) = ... {
  tracing::error!(...) }` with no further handling), not confirmed by a test that
  forces the DB write to fail and asserts the row is left at `Running`.
- **No test was found asserting `execute_steps` never calls `update_workflow_run`** —
  this is an absence claim (no call site exists in the function), verified by reading
  the function's full body and by the grep evidence cited above, not by a test that
  would fail if a future edit added an intermediate write.
- **Whether any consumer other than `buzz-cli`'s `cmd_get_workflow_runs`** (desktop,
  mobile, a REST endpoint) reads `workflow_runs` today was not checked; this node
  only establishes that the one CLI command meant for this purpose queries the wrong
  source.
- **Whether `type: capabilities` is the corpus's eventual settled answer for a
  run-record-shaped node under `capabilities/`** is genuinely unresolved — no
  capabilities-typed node is merged anywhere in the corpus at this revision to serve
  as precedent, and the *data-entity* template (unmerged at this revision) reasons
  toward `type: implementation` for a domain-entity instance on different grounds
  (an entity "as it is actually built," not a capability). This node's own choice is
  recorded as an `INFERENCE` at confidence 0.6 for exactly that reason.
