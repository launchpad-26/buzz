---
id: capabilities-workflows-workflow-step
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
  - statement: "A workflow step (`Step`) carries an id, an optional display name, an optional `if:` condition (`if_expr`), an optional per-step `timeout_secs`, and exactly one action (`ActionDef`, flattened into the step's own JSON/YAML fields)."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/schema.rs:73-90"
  - statement: "`ActionDef` is a closed, internally-tagged (`action:`) enum of exactly seven step kinds: SendMessage, SendDm, SetChannelTopic, AddReaction, CallWebhook, RequestApproval, Delay."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/schema.rs:92-155"
  - statement: "`WorkflowDef::validate()` rejects a definition with zero steps, and rejects any step whose id is empty, exceeds 64 characters, contains a character other than an ASCII alphanumeric or underscore, or duplicates another step's id in the same definition — all enforced before a definition can be saved, and therefore before any step can ever run."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/schema.rs:180-214"
  - statement: "`execute_steps` is the one step-dispatch loop every run passes through: `execute_run` (a fresh run, `start_index = 0`) and `execute_from_step` (an approval resume, `start_index` = the resume point) both call it after acquiring their own concurrency permit, rather than each duplicating step-dispatch logic."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/executor.rs:1084"
      - "crates/buzz-workflow/src/executor.rs:1146-1163"
  - statement: "Within `execute_steps`, a step's optional `if:` expression is evaluated first (via `evalexpr`, against the trigger context and the outputs already produced by earlier steps in the same run); a `false` result records a `\"skipped\"` trace entry and moves to the next step without dispatching the action, while an evaluation error aborts the whole run."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/executor.rs:1182-1204"
  - statement: "After the condition check, the step's action fields are template-resolved (`{{trigger.X}}` / `{{steps.ID.output.X}}` placeholders) against the same trigger context and accumulated step outputs before dispatch; a resolution error aborts the run in the same way a condition error does."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/executor.rs:1206-1215"
  - statement: "Each step's dispatch is wrapped in `tokio::time::timeout` using the step's own `timeout_secs` if set, else the engine's `default_timeout_secs`; a timeout aborts the run with `WorkflowError::StepTimeout`, which names the step id and the limit that was exceeded."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/executor.rs:1217-1254"
      - "crates/buzz-workflow/src/error.rs:36-43"
  - statement: "A step's outcome is exactly one of three `StepResult` variants: `Completed(output)` (recorded into the run's trace and into `step_outputs` under the step's own id, addressable by later steps), `Suspended { approval_token }` (returns out of the loop immediately, leaving the run resumable from that step index), or `Skipped` (recorded into the trace, no output produced)."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/executor.rs:474-484"
      - "crates/buzz-workflow/src/executor.rs:1257-1288"
  - statement: "On any step-level error — condition evaluation, template resolution, action dispatch, or timeout — `execute_steps` returns `Err((WorkflowError, PartialProgress))` carrying the failing step's index and the trace of every step already completed or skipped; it does not roll back or undo a side effect a prior step already produced, because no `ActionDef` variant has a compensating action."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/executor.rs:1195-1254"
      - "crates/buzz-workflow/src/error.rs:5-15"
  - statement: "`WorkflowError`'s ten variants (InvalidYaml, InvalidDefinition, ConditionError, TemplateError, StepTimeout, WebhookError, CapacityExceeded, Database, Unauthorized, NotImplemented) contain no retry-classified error and no retry loop exists anywhere in `crates/buzz-workflow/src` for a failed step dispatch — a step's failure is terminal for the run, not retried."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/error.rs:17-66"
      - "grep_case_insensitive('retry', path='crates/buzz-workflow/src') -> zero matches, run against commit 131b02f989684117d9ab1dd426f1673fa638e523"
  - statement: "Two of the seven action kinds are permanently unimplemented today: `SendDm` and `SetChannelTopic` both return `WorkflowError::NotImplemented` the instant `dispatch_action` is called for them, without attempting any side effect — a step authored with either action always fails, regardless of what precedes it in the same run."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/executor.rs:643-653"
  - statement: "VISION_PROJECTS.md's own Status table marks the row 'Workflow engine (triggers, traces, conditional logic)' as '✅ Ships today', while a separate row marks 'Approval gates' as '🚧 Infrastructure exists; executor wiring in progress' — the step-sequencing/dispatch mechanics this node documents are shipped even though specific action kinds built on top of them (RequestApproval's suspend-and-resume path, SendDm, SetChannelTopic) are not all complete."
    entry_class: FACT
    evidence:
      - "VISION_PROJECTS.md:247-259"
  - statement: "`launchpad/docs/corpus/architecture/flows/workflow-execution.md` (merged, id `architecture-flows-workflow-execution`) already documents the shared step loop's ordered interactions, trust-boundary crossings, and failure/abort/rollback behavior at FACT-level detail across all three trigger paths, so this node references it for that mechanics rather than restating it."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/flows/workflow-execution.md"
  - statement: "`launchpad/docs/corpus/templates/capability.md` (merged) defines `type: capabilities` as naming something the product can do, stated as a stakeholder-recognizable noun phrase distinct from the architecture that implements it, and states that a capability may declare `part-of` toward a broader capability it is a constituent piece of when one exists."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/templates/capability.md"
  - statement: "Choosing `type: capabilities` for this node — 'workflow step' being a constituent building block of the already-named 'Workflow engine' capability rather than a top-level capability in its own right — is a reasoned choice, not a merged precedent: no `capabilities`-typed node exists yet on `origin/launchpad` to confirm consistency against, and the fit is closer to 'the general unit of behavior a workflow author composes' than to a fully independent noun-phrase capability. `type` may be revised later without affecting this node's permanent `id`, per `standards/taxonomy.md`."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/templates/capability.md"
      - "launchpad/docs/corpus/standards/taxonomy.md"
      - "VISION_PROJECTS.md:250"
    confidence: 0.7
  - statement: "Sibling tasks #822, #823, #830, #833, #834, #835 and #836 each document one individual action kind (approval, delay, reaction, send-dm, send-message, set-topic, webhook) at the path `launchpad/docs/corpus/capabilities/workflows/<name>-action.md`, confirming the batch's own convention of placing per-action-kind step documentation under the `capabilities/workflows/` path this node also uses; none of the seven were merged to `origin/launchpad` at the recorded revision, so none is declared as a relationship target."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#822, #823, #830, #833, #834, #835, #836 titles (read via gh issue view)"
  - statement: "Issue #842's definition of done requires this node to state the capability and primary actors/outcomes, define behavioral rules/constraints/variants, link major flows/interfaces/data/platform implementation, and link verification demonstrating the capability — and states that this node is the umbrella step abstraction, distinct from the sibling per-action-type nodes."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#842 definition of done"
  - statement: "`condition_true_when_text_contains_p1`, `condition_false_when_text_does_not_contain_p1` and `condition_invalid_expression_returns_error` (all in `crates/buzz-workflow/src/executor.rs`'s test module) are representative unit tests asserting the `if:` gating behavior above: a true condition runs the step, a false one is treated as a distinct outcome from running it, and a malformed expression is a run-aborting error rather than a silent skip."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/executor.rs:1413-1432"
      - "crates/buzz-workflow/src/executor.rs:1519-1527"
  - statement: "`parse_step_with_timeout_secs` and `parse_all_action_types` (both in `crates/buzz-workflow/src/schema.rs`'s test module) are representative unit tests asserting a step's optional `timeout_secs` round-trips correctly and that all seven `ActionDef` variants parse from their tagged YAML form."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/schema.rs:664-672"
      - "crates/buzz-workflow/src/schema.rs:384-425"
relationships:
  - type: references
    target: architecture-flows-workflow-execution
---

# Workflow step

The general unit of behavior a workflow author composes to build a Buzz
**workflow**: an ordered list of steps, each performing one action, that
together turn a trigger (a channel event, a schedule, or a webhook) into a
sequence of effects — a message sent, a reaction added, an external system
called, a human asked to approve, a pause taken. A workflow author (human or
agent, through the `kind:30620` workflow-definition command) states *what*
should happen and in what order; the engine owns *how* each step is
sequenced, gated, timed out, and recorded.

## Maturity

**Ships today**, per VISION_PROJECTS.md's own Status table entry for
"Workflow engine (triggers, traces, conditional logic)". The step
abstraction itself — sequencing, `if:` gating, template resolution,
per-step timeout, and outcome recording — is fully implemented and exercised
by unit tests (see *Verification* below).

**Two of the seven action kinds are not**: `SendDm` and `SetChannelTopic`
always fail immediately with `WorkflowError::NotImplemented` the moment they
are dispatched, and `RequestApproval`'s suspend-and-resume path is
incomplete (no approval record is persisted and no resolvable event is
emitted, per `architecture-flows-workflow-execution`'s own *Failure, abort,
rollback* section) — consistent with VISION_PROJECTS.md's separate
"Approval gates" row, marked "infrastructure exists; executor wiring in
progress" rather than shipped. A step authored with any of these three
action kinds is well-formed at the step-abstraction level (it parses,
validates, and is scheduled like any other step) but cannot currently
succeed at the action level — that per-action detail belongs to the
individual action's own node (see *Boundary*), not here.

## Step shape

Every step, regardless of which action it performs, carries the same four
step-level fields:

| Field | Type | Meaning |
|---|---|---|
| `id` | string | Unique within the workflow; restricted to ASCII alphanumerics and underscores, 1-64 chars, because step ids become `evalexpr` variable names (`steps_<id>_output_<field>`) that later steps' conditions and templates read. |
| `name` | string, optional | Human-readable label; has no effect on execution. |
| `if` (`if_expr`) | string, optional | An `evalexpr` condition. Absent means "always run." |
| `timeout_secs` | integer, optional | Overrides the engine's default per-step timeout for this one step. |
| action fields | — | Exactly one of the seven `ActionDef` variants, flattened into the step's own fields, tagged by its own `action:` key (`send_message`, `send_dm`, `set_channel_topic`, `add_reaction`, `call_webhook`, `request_approval`, `delay`). |

A workflow definition must contain at least one step, and every step id in
it must be unique — both are rejected at definition-save time, never at run
time, so a saved definition can never contain a step-id collision or an
empty step list.

## Sequencing and conditional gating

Steps run **strictly in the order they are authored**, one at a time, never
concurrently within a single run. For each step, in order:

1. If the step carries an `if:` expression, evaluate it against the trigger
   context and every prior step's recorded output in *this* run. A `false`
   result is a distinct, first-class outcome — **skipped**, not failed —
   and execution moves to the next step. An evaluation error is not treated
   as `false`; it aborts the entire run.
2. Resolve any `{{trigger.X}}` / `{{steps.ID.output.X}}` template
   placeholders in the action's own fields against that same context. A
   resolution error also aborts the run.
3. Dispatch the resolved action, under a timeout (the step's own
   `timeout_secs`, or the engine's default if unset). A timeout aborts the
   run and names the step and the limit that was exceeded.
4. Record the outcome — `Completed` (with output, addressable by later
   steps), `Skipped`, or `Suspended` (pauses the run at this step, awaiting
   an external resume) — into the run's trace.

This gives every step type the same three building blocks for free —
ordering, conditional skipping, and output chaining — without any
individual action's own document needing to re-derive them.

## Failure and retry semantics

**A step failure is terminal for the run, and it is not retried.** There is
no retry-classified error variant and no retry loop anywhere in the step
executor: a condition-evaluation error, a template-resolution error, an
action-dispatch error, or a step timeout all abort every step after the
failing one. The run's terminal status becomes `Failed`, carrying a stable
error code and the trace of everything completed or skipped up to the
failure point.

**Failure does not roll anything back.** No `ActionDef` variant has a
compensating or undo action, so a step that already produced a side effect
(a message already sent, a reaction already added) before a later step
fails leaves that side effect standing. A workflow author who needs
idempotent or reversible behavior across steps must build it into the steps
themselves (for example, an `if:` guard on a later step checking an earlier
step's output) — the engine provides no automatic compensation.

**A `Suspended` outcome is the one exception to "run to completion or
fail."** It pauses the run at the suspending step rather than failing or
completing it, to be resumed later from that same index with the outputs
already produced preserved. Today only `RequestApproval` produces this
outcome, and — per `architecture-flows-workflow-execution`'s own findings —
the resume path is not wired up yet, so in practice a suspension is mapped
to `Failed` rather than staying queryable; see that node for the full
mechanics.

## Boundary: what this node is not

- **Not the per-action operational detail.** What `send_message` actually
  does with its `channel` override, what `call_webhook`'s SSRF guarding
  does, what `request_approval`'s timeout string means — each of the seven
  action kinds is its own document (`capabilities/workflows/*-action.md`,
  drafted as sibling tasks in this same batch; none merged at the recorded
  revision, so none is a relationship target here). This node states only
  what every step type has in common.
- **Not the trigger-to-run flow.** How a workflow is selected to run at all
  — the three trigger paths, tenant/authority checks, and the concurrency
  semaphore — is `architecture-flows-workflow-execution`'s subject, not
  this node's. This node begins where that flow's shared step loop begins.
- **Not workflow definition authoring/storage.** The `kind:30620` command,
  YAML/JSON round-tripping, and per-field schema validation beyond the
  step-shape invariants named above are out of scope here.
- **Not how the running system is operated.** Deployment, monitoring, and
  incident response for the workflow engine are the `operations` corpus
  surface's subject, not a capability-level concern.

## Relationships

- `references` → `architecture-flows-workflow-execution`: that node owns
  the full trigger-to-terminal-state mechanics (all three trigger paths,
  trust-boundary crossings, the same step loop's ordered interactions in
  FACT-level detail); this node cites it instead of restating that content,
  per `templates/capability.md`'s evidence-expectations guidance not to
  duplicate an architecture node's content inside a capability node.

No `part-of` edge toward a broader "workflow engine" capability node is
declared, because no such node is merged to `origin/launchpad` at the
recorded revision — the natural moment to add one is once that node exists,
per `AGENTS.md`'s node-creation step 9 (a relationship target must exist on
the branch being merged into).

## Verification

- `condition_true_when_text_contains_p1`, `condition_false_when_text_does_not_contain_p1`
  and `condition_invalid_expression_returns_error`
  (`crates/buzz-workflow/src/executor.rs`) — representative coverage of the
  three-way `if:` outcome (run / skip / abort) described above.
- `parse_step_with_timeout_secs` and `parse_all_action_types`
  (`crates/buzz-workflow/src/schema.rs`) — representative coverage that a
  step's `timeout_secs` round-trips and that all seven action kinds parse
  from their tagged form.
- `workflow_error_codes_are_stable_and_separate_from_diagnostics`
  (`crates/buzz-workflow/src/error.rs`, cited by
  `architecture-flows-workflow-execution`) — the stable, secret-free error
  classification a failed step's run ultimately persists as.

## Scope and omissions

**This node covers** the step abstraction shared by every workflow action
kind: the four step-level fields, strict in-order sequencing, `if:`
conditional gating (including the run/skip/abort three-way outcome),
per-step timeout, the three `StepResult` outcomes, and the failure/retry
semantics common to all of them (terminal on error, no retry, no
rollback), plus which two action kinds cannot currently succeed at all.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Each action kind's own fields, behavior, and side effects | The seven per-action nodes at `capabilities/workflows/*-action.md` (sibling batch tasks; not yet merged) |
| Trigger selection, tenant/authority checks, concurrency limits | `architecture-flows-workflow-execution` |
| Workflow definition authoring/storage (`kind:30620`) | Not yet documented in this corpus |
| How the workflow engine is deployed/monitored/operated | The `operations` corpus surface |

**Expected but not verified when this node was written:**

- **No broader "workflow engine" capability node exists yet** to declare a
  `part-of` edge toward, and none of the seven sibling per-action nodes are
  merged, so this node's only declared relationship is the one `references`
  edge above. Whether `type: capabilities` remains the best fit once a
  sibling "workflow engine" capability node is drafted was not checked —
  see the `INFERENCE` evidence entry above for the reasoning as it stands
  today.
- **Whether the desktop or CLI surfaces expose step-level state** (for
  example, a per-step status in a workflow-run UI) beyond what
  `architecture-flows-workflow-execution` already establishes about the
  `workflow_runs` row's own columns was not checked; this node is scoped to
  the engine-side step abstraction only.
