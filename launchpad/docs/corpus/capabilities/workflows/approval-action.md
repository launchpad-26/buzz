---
id: capabilities-workflows-approval-action
type: architecture
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision cad6c375fdcc590158c1456c9fc7875f0f84a844."
    entry_class: FACT
    evidence:
      - "commit cad6c375fdcc590158c1456c9fc7875f0f84a844"
  - statement: "node.schema.json's type enum has thirteen members -- architecture, layers, capabilities, platforms, implementation, interfaces-events, verification, operations, development, release, governance, agent, ingestion -- capabilities is one of them, and none of the thirteen is named flow."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "Issue #822's own Objective line reads 'Create ... as the single canonical flow node for approval action,' and its closed duplicate #827 carries byte-identical wording, even though the target path (capabilities/workflows/approval-action.md) and parent Feature #613's own title ('workflow and supporting capability corpus exists') both point at a capability-shaped node -- the same copy-paste boilerplate drift AGENTS.md, templates/flow.md and templates/capability.md each document elsewhere in this batch."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#822 Objective and launchpad-26/buzz#827 Objective (read directly via gh issue view; issue content is mutable GitHub state, so this stays TEAM_KNOWLEDGE rather than FACT)"
  - statement: "VISION_PROJECTS.md's own 'Capability | Status' table lists 'Approval gates' as one of its eleven rows, marked with the same in-progress marker as no other row in the table quotes verbatim: 'Infrastructure exists; executor wiring in progress' -- naming this exact subject as one of the corpus's own product-level capabilities, which this node initially treated as outweighing its own flow-shaped body when first drafted."
    entry_class: FACT
    evidence:
      - "VISION_PROJECTS.md:253"
  - statement: "Corrected during Feature #613's whole-branch review, after all ~70 sibling nodes existed side by side: this node's body is trigger/precondition/ordered-interaction/failure-rollback content -- the same shape templates/flow.md documents and the same shape 10 of its own direct siblings (send-dm-action, send-message-action, message-trigger, reaction-trigger, schedule-trigger, webhook-trigger, workflow-trigger, needs-action, agent-shutdown, reminder-lifecycle) already carry as type: architecture. type: capabilities was this node's own initial judgment call, made in isolation with no merged precedent to check against; once compared against its actual body shape and its true siblings, type: architecture is the consistent answer, not a directory-placement extension. The capabilities/workflows/ path names a corpus-plan directory grouping, not a type."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
      - "launchpad/docs/corpus/templates/flow.md"
      - "launchpad/docs/corpus/architecture/flows/workflow-execution.md"
      - "launchpad/docs/corpus/capabilities/workflows/send-dm-action.md"
      - "launchpad/docs/corpus/capabilities/activity/needs-action.md"
    confidence: 0.8
  - statement: "The RequestApproval action is defined in the workflow schema with three fields -- from (user mention or role, e.g. '@release-manager'), message (shown to the approver), and an optional timeout string defaulting to '24h' -- and requesting it does not require elevated (owner/admin) channel authority: WorkflowDef::requires_elevated_authority checks only for a CallWebhook step in the definition, never for RequestApproval."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/schema.rs:141-149"
      - "crates/buzz-workflow/src/schema.rs:165-169"
  - statement: "dispatch_action's RequestApproval arm logs the request, generates a random token via generate_approval_token (Uuid::new_v4, not mixed with run/step ids), and returns StepResult::Suspended{ approval_token }; its own comment marks that no approval record is created in the database and no event is emitted, tagged '// TODO (WF-08)'."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/executor.rs:713-731"
      - "crates/buzz-workflow/src/executor.rs:779-781"
  - statement: "finalize_run -- the single place every trigger path (event, schedule, webhook) routes an executor result through -- treats any result whose approval_token is Some(_) as a run failure: it writes RunStatus::Failed with error code approval_not_supported and logs a warning that the approval gate is 'not yet implemented,' rather than writing RunStatus::WaitingApproval."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/lib.rs:229-256"
  - statement: "No source file under crates/buzz-workflow, crates/buzz-relay or crates/buzz-db ever constructs a write of RunStatus::WaitingApproval; the two production references to that variant outside its own Display/FromStr definitions are both read-only equality guards in the relay's approval-grant and approval-deny handlers, each checking a run's current status before acting rather than ever setting it."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/command_executor.rs:1231"
      - "crates/buzz-relay/src/handlers/command_executor.rs:1290"
  - statement: "A database table, CRUD functions and a full relay command surface for resolving an approval already exist and are exercised by unit/integration tests, but are unreachable from any production request path today because nothing ever calls the insert function that would create the row a resolution needs: workflow_approvals is a real table (present since migrations/0001_initial_schema.sql, columns include a SHA-256-hashed token, workflow_id, run_id, step_id, step_index, approver_spec, status, expires_at); create_approval/get_approval_by_stored_hash/update_approval_by_stored_hash are implemented in buzz-db; and grep across crates/ shows create_approval's only two call sites are inside its own module's #[cfg(test)] block, not in executor.rs, lib.rs or command_executor.rs."
    entry_class: FACT
    evidence:
      - "schema/schema.sql:413-433"
      - "migrations/0001_initial_schema.sql:411-435"
      - "crates/buzz-db/src/store/workflow.rs:31-37"
      - "crates/buzz-db/src/store/workflow.rs:992-1024"
      - "crates/buzz-db/src/store/workflow.rs:2702"
      - "crates/buzz-db/src/store/workflow.rs:2717"
  - statement: "The relay's command dispatch table routes kind:46030 to handle_approval_grant and kind:46031 to handle_approval_deny, both of which: extract a token-hash reference from the event's d or e tag, look up the approval record by that hash, reject a non-pending or (grant path only, explicitly checked) expired approval, check the caller against the stored approver_spec via check_approver_spec, persist the command event for idempotency, then update the approval's status and -- on grant only -- spawn resume_workflow_after_approval, which reconstructs step_outputs and trigger context from the run's stored execution_trace/trigger_context and calls execute_from_step at step_index + 1 followed by finalize_run."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/command_executor.rs:70-72"
      - "crates/buzz-relay/src/handlers/command_executor.rs:1020-1130"
      - "crates/buzz-relay/src/handlers/command_executor.rs:1132-1270"
      - "crates/buzz-relay/src/handlers/command_executor.rs:1273-1367"
      - "crates/buzz-core/src/kind.rs:559-562"
  - statement: "check_approver_spec fails closed: an empty spec or the literal string 'any' allows any caller; a 64-character hex string is matched case-insensitively as an exact pubkey; anything else (including a role reference like '@release-manager', which is the very form the RequestApproval action's own `from` field example uses) is rejected as 'not yet supported' -- so today's approver_spec resolution cannot actually enforce a role-based approver even in the hypothetical case where a pending approval existed to check it against."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/command_executor.rs:995-1018"
  - statement: "A buzz-cli 'workflows approve' subcommand exists end to end: it takes a --token UUID and an --approved boolean (default true), hashes the token client-side with SHA-256 to build the relay's expected d-tag, and signs and submits a kind:46030 or kind:46031 event via buzz_sdk::build_workflow_approval -- the same command-signing path any other buzz-cli write uses, layered on top of resolve-side infrastructure that, per the entries above, no request ever actually populates."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/commands/workflows.rs:205-225"
      - "crates/buzz-cli/src/lib.rs:960-974"
  - statement: "Kinds 46010 (workflow_approval_requested), 46011 (workflow_approval_granted) and 46012 (workflow_approval_denied) are reserved in the kind registry as the notification events this capability would emit once WF-08 lands, distinct from the caller-facing command kinds 46030 (approval_grant) and 46031 (approval_deny) that a resolver actually signs and submits; none of the three notification kinds is constructed anywhere in buzz-workflow today, consistent with architecture-flows-workflow-execution.md's own finding for the whole engine."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs:558-582"
  - statement: "No unit or integration test anywhere in the workspace asserts the approval_not_supported error code or otherwise exercises a RequestApproval step end to end through finalize_run; grepping the full crates/ tree for that exact string finds only its one production definition site, with no matching assertion in any *_test.rs, tests.rs or #[cfg(test)] module."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/lib.rs:246"
  - statement: "architecture-flows-workflow-execution.md is already merged on origin/launchpad at this node's recorded revision, documents the shared step-dispatch loop every RequestApproval step actually runs inside, and states in its own Scope section that it does not cover 'the approval-gate resume flow, because that capability (WF-08) is not implemented yet' -- the exact boundary line this node's own Relationships section extends a references edge to rather than restating that node's content."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/flows/workflow-execution.md"
  - statement: "relationships.schema.json defines references' directionality as 'source cites target as supporting context; no ownership or currency dependency implied,' which is the relationship type and semantics this node uses to point at architecture-flows-workflow-execution."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/relationships.schema.json"
  - statement: "At this node's recorded revision, origin/launchpad's corpus tree carries no other node under capabilities/, so architecture-flows-workflow-execution is the only existing merged node this one declares a relationship to; re-checking against origin/launchpad rather than this worktree is required by AGENTS.md's own creating-a-node step 9."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
relationships:
  - type: part-of
    target: capabilities-workflows-workflow
---

# Approval action: capability

Buzz's workflow engine can pause a running workflow to ask a human for approval
before continuing — a `request_approval` step in a workflow definition. A workflow
author names who should approve (`from`), what they should be asked (`message`), and
how long the request stands before it should be considered stale (`timeout`,
defaulting to `24h`). No elevated channel authority is needed to author or run a step
of this kind; only a `call_webhook` step raises that bar.

## Maturity

**In progress, not shipped.** VISION_PROJECTS.md's own capability table marks
"Approval gates" as `🚧 Infrastructure exists; executor wiring in progress` — and
that is a precise description of what the code shows, not an approximation:

- The **request side** — the `RequestApproval` action a workflow step dispatches —
  runs, generates a token, and immediately reports itself as `Suspended`, but writes
  nothing to the database and emits no event. The engine's own `finalize_run` then
  treats that outcome as an outright run failure (`approval_not_supported`), never as
  a paused, resumable run.
- The **resolve side** — the `workflow_approvals` table, its CRUD functions, the
  relay's `kind:46030`/`46031` grant/deny command handlers, the resume logic, and a
  `buzz-cli workflows approve` command that signs and submits those events — is
  fully built and exercised by tests, but unreachable in production: nothing ever
  calls the function that would create the row those handlers look up.

The two halves do not yet meet. A workflow author can put a `request_approval` step
in a definition today; doing so reliably fails that run rather than pausing it.

## Trigger, preconditions, termination

**Trigger.** A `RequestApproval` step is dispatched by the shared step-execution
loop the moment its turn comes up in `def.steps` order, on any of the three trigger
paths documented in `architecture-flows-workflow-execution` (channel event, schedule,
webhook) — the action itself has no trigger logic of its own beyond "this step's
`if:` condition, if any, evaluated true."

**Preconditions.** Beyond the shared per-run preconditions documented in the
referenced flow node (definition parses, is enabled, owner authority checked), a
`RequestApproval` step has exactly one of its own: the definition must supply
`from` and `message` (both required, non-defaulted fields); `timeout` is optional
and defaults to `24h` at the point the log line is formatted. `requires_elevated_authority`
does not gate this action — only a `call_webhook` step anywhere in the same
definition raises the authority bar.

**Termination.** Today there is exactly one outcome: the surrounding run terminates
as `Failed` with error code `approval_not_supported`, immediately, on the same tick
that dispatches the step. There is no pending/paused state a caller can observe or
poll — `RunStatus::WaitingApproval` exists in the enum but nothing ever writes it.

## Ordered interactions and data/state movement

**Request side, as it behaves today:**

1. The shared step loop reaches a `request_approval` step and calls `dispatch_action`.
2. The action's fields (`from`, `message`, `timeout`) are logged; a random token is
   generated (`Uuid::new_v4()`, not derived from the run or step id).
3. `dispatch_action` returns `StepResult::Suspended { approval_token }`. No row is
   inserted into `workflow_approvals`; no `kind:46010` event is built or published.
4. The executor's caller maps this into an `ExecutionResult` carrying
   `approval_token: Some(token)`.
5. `finalize_run` sees `approval_token.is_some()`, logs a warning, and writes
   `RunStatus::Failed` with `error_code = "approval_not_supported"` and the trace
   accumulated up to and including this step. The generated token is discarded —
   nothing durable ever references it.

**Resolve side, built but never reached from production:**

1. A human (or agent) who somehow held a valid, persisted approval token would run
   `buzz workflows approve --token <uuid> [--approved true|false] [--note ...]`.
2. The CLI hashes the token with SHA-256 client-side and signs a `kind:46030`
   (approve) or `kind:46031` (deny) event whose `d`/`e` tag carries that hash in hex.
3. The relay's command dispatcher routes the kind to `handle_approval_grant` or
   `handle_approval_deny`, which looks up the `workflow_approvals` row by the
   stored hash, rejects it if not `pending` (or, on the grant path, expired), and
   checks the caller against `approver_spec` via `check_approver_spec`.
4. On success, the command event is persisted for idempotency, the approval row's
   `status` is updated (`granted` or `denied`), and — grant only — the relay spawns
   `resume_workflow_after_approval`, which re-fetches the run, guards that its
   status is still `WaitingApproval`, reconstructs `step_outputs` and trigger
   context from the run's stored `execution_trace`/`trigger_context`, and calls
   `execute_from_step` starting at `step_index + 1`, followed by `finalize_run`.
5. On deny, the run is instead moved straight to `Cancelled` with error code
   `approval_denied`, no resume attempted.

Step 3 of the resolve side can never succeed today: step 3 of the request side never
creates the row step 3 here looks up, so every grant/deny event a caller could
construct resolves to "approval not found."

## Trust-boundary crossings

- **Approver identity.** `check_approver_spec` fails closed: an empty spec or the
  literal `any` permits any caller; a 64-character hex string is matched
  case-insensitively as an exact pubkey; anything else — including a role reference
  like `@release-manager`, the very form the action's own `from` field is documented
  to accept — is rejected as unsupported. A workflow author can *write* a
  role-based approver spec; the relay cannot yet *enforce* one.
- **Token as bearer secret.** The raw token is generated once and never persisted
  in production; on the resolve side the DB stores only its SHA-256 hash
  (`workflow_approvals.token` holds the digest, not the raw value), the same
  pattern buzz-auth uses for API tokens — so a database read alone cannot recover a
  usable token, even in the code paths that do write it (tests).
- **No elevated authority required to request.** Unlike `call_webhook`, defining or
  running a `RequestApproval` step needs no owner/admin role — a plain active
  channel member can author a workflow that asks someone else to approve something.
- **Command-event idempotency.** Both grant and deny handlers persist the signed
  command event before updating approval/run state, the same idempotency pattern
  other workflow commands use, so a duplicate replayed grant/deny event is detected
  and short-circuited rather than double-applied.

## Failure, abort, rollback behavior

- **Fail closed, not open.** A `RequestApproval` step's only reachable outcome
  today is a failed run — there is no code path where hitting this action leaves a
  run in a waiting, retryable, or otherwise recoverable state.
- **The generated token is orphaned.** `generate_approval_token` runs and returns a
  value every time, but because no row is ever inserted, that token corresponds to
  nothing a grant/deny event could ever resolve — it exists only in a log line.
- **The resolve side's own guards never fire in practice.** `resume_workflow_after_approval`
  and the deny handler's cancellation path both check `run.status ==
  RunStatus::WaitingApproval` before acting; since nothing ever sets that status,
  these guards exist for a state the current system never produces.
- **No compensating action.** Consistent with `architecture-flows-workflow-execution`'s
  own finding for the engine generally, any step that ran and produced a side effect
  before the `RequestApproval` step is not undone when the run subsequently fails —
  this action's failure is no different from any other step-level failure in that
  respect.
- **Representative verification: none exists yet.** No unit or integration test in
  the workspace asserts the `approval_not_supported` mapping or exercises a
  `request_approval` step end to end through `finalize_run` — grepping the full
  `crates/` tree for that error-code string finds only its one production
  definition site. This is a real gap, not an oversight in this document: the
  request-side behavior above is verified by reading the dispatch and
  finalization code directly, not by a passing test that would catch a regression
  in it.

## Boundary

This node does not describe:

- **How a workflow run reaches the point of dispatching this step at all** — the
  three trigger paths, the shared executor loop, run-level concurrency and timeout
  handling. See `architecture-flows-workflow-execution`, which this node
  `references` rather than restates.
- **The wire contract of kinds 46010/46011/46012 or 46030/46031** — their tag
  shapes, content semantics, and access model are an event-kind node's subject, not
  this one's; this node cites the kind constants only as evidence that reserved
  space and a command surface already exist.
- **The `buzz workflows approve` CLI subcommand's own interface contract** — its
  full flag set, output shape, and exit codes are an interface node's subject; this
  node cites it only as evidence that resolve-side infrastructure exists end to end.
- **The workflow run state machine in general** (`RunStatus`'s full set of values
  and every path that can reach each one) — that is a sibling task's subject
  (`workflow-run.md`), not this one's; this node discusses only the states a
  `RequestApproval` step can currently produce.
- **When or how WF-08 will land.** No implementation timeline is claimed or implied
  by "infrastructure exists; executor wiring in progress" beyond what that phrase
  and the code it describes literally show today.

## Relationships

- `references`: `architecture-flows-workflow-execution` — the shared trigger paths
  and step-dispatch loop this action's step runs inside, and the flow node whose own
  Scope section already names the approval-gate resume flow as out of its coverage.

## Scope and omissions

**This node covers** the `RequestApproval` workflow action as a capability: what a
workflow author configures, what happens when the engine dispatches it today (an
immediate, fail-closed run failure), what resolve-side infrastructure already exists
in the database, relay and CLI but is unreachable in production, the trust
boundaries the approver-identity check and token hashing establish, and the absence
of any test that currently guards the failure-mapping behavior.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The shared trigger paths and step-dispatch loop | `architecture-flows-workflow-execution` (merged) |
| The wire contract of kinds 46010–46012 and 46030/46031 | a future event-kind node |
| The `buzz workflows approve` CLI subcommand's own interface contract | a future interface node |
| The workflow run state machine in general | `workflow-run.md` (sibling task, #841) |
| The workflow step/definition schema in general | `workflow-step.md` / `workflow-definition.md` (sibling tasks, #842 / #840) |

**Expected but not verified when this node was written:**

- **Whether any open, unmerged upstream pull request already implements WF-08** was
  not established as a claim in this node — such state is external, mutable, and not
  a fact about this repository's own checked-out revision, so it is left unstated
  rather than cited to a PR number or status that could go stale immediately.
- **Whether desktop, mobile, or any other client currently renders or reacts to a
  `RequestApproval`-suspended run** was not checked; this node only establishes what
  the relay/workflow-engine backend does.
- **Whether `check_approver_spec`'s role-reference rejection is intentional MVP scope
  or an unfinished sub-feature of WF-08 itself** was not established from any design
  document — only that the code rejects it today, fail-closed.
