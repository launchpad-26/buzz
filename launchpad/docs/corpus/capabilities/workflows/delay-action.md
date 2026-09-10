---
id: capabilities-workflows-delay-action
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
  - statement: "ActionDef::Delay is a workflow step action carrying exactly one field, duration: String, documented in its own doc comment as 'Pause execution for a duration (e.g. \"5m\", \"1h\").'"
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/schema.rs:150-153"
  - statement: "resolve_step_templates clones a Delay step's duration field unchanged, unlike every one of the other five actions (SendMessage, SendDm, SetChannelTopic, CallWebhook, RequestApproval all resolve {{trigger.X}} / {{steps.ID.output.X}} placeholders in their own string fields via the same t()/t_opt() helpers) -- a Delay step's duration is never template-resolved."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/executor.rs:418-469"
  - statement: "parse_duration_secs parses a duration string with an 'h', 'm' or 's' suffix into whole seconds (checked multiplication, erroring on overflow), or, with no recognized suffix, parses the whole string as a plain integer assumed to already be seconds; any other content is an InvalidDefinition error."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/executor.rs:786-814"
  - statement: "parse_duration_secs's four accepted shapes (hours, minutes, seconds, bare number) and its rejection of unparseable input are each covered by a dedicated unit test."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/executor.rs:1546-1572"
  - statement: "dispatch_action's Delay arm rejects any duration whose parsed value exceeds a hardcoded MAX_DELAY_SECS of 270 with WorkflowError::InvalidDefinition; the surrounding comment states the cap must stay below the 300-second default step timeout to avoid a non-deterministic StepTimeout race, and that a longer wait needs the not-yet-built scheduled-resume pattern (referred to as future work 'WF-09') instead of sleeping in-process."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/executor.rs:734-745"
  - statement: "The 270-second cap is enforced only at dispatch time inside dispatch_action's Delay arm, not at workflow save time: WorkflowDef::validate() -- the function every definition must pass before any trigger path can ever run it -- contains no branch inspecting a Delay step's duration at all, so a workflow whose delay step requests, say, one hour saves successfully and only fails the first time that step actually dispatches."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/schema.rs:173-278"
  - statement: "On success, the Delay arm sleeps for the parsed duration via tokio::time::sleep and returns StepResult::Completed with output {\"slept_secs\": <seconds>}; execute_steps records this into the run's execution trace and into the step_outputs map under the step's own id exactly like any other action's output, making it addressable by later steps as steps.<id>.output.slept_secs."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/executor.rs:746-751"
      - "crates/buzz-workflow/src/executor.rs:1257-1265"
  - statement: "WorkflowDef::requires_elevated_authority checks only for a CallWebhook step among a definition's steps; Delay is not named, so a definition whose steps are Delay (plus any other non-CallWebhook actions) carries no elevated owner-authority requirement beyond the ordinary active-channel-member check the run-level flow already documents."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/schema.rs:165-169"
  - statement: "dispatch_action acquires a community serving-write lease (buzz_deletion::acquire_serving_write) and verifies it before entering the action match, then runs the entire matched arm -- for Delay, the full tokio::time::sleep -- inside that lease's own protect() wrapper."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/executor.rs:551-565"
  - statement: "ServingWriteGuard::protect verifies the lease, then races the wrapped future against the lease's own heartbeat-loss cancellation signal in a biased tokio::select!, verifying the lease again only if the wrapped future wins; if the lease's heartbeat is lost first, the wrapped future is dropped in place and protect() returns an error instead of letting it finish."
    entry_class: FACT
    evidence:
      - "crates/buzz-deletion/src/lib.rs:88-105"
  - statement: "Among the six workflow actions, Delay is the only one whose wrapped operation is an unconditional in-process wait (up to 270 seconds) rather than a bounded network or database call, so it holds its serving-write lease, and is exposed to the lease-loss race described above, for far longer than any other action's dispatch."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-workflow/src/executor.rs:566-751"
      - "crates/buzz-deletion/src/lib.rs:88-105"
    confidence: 0.8
  - statement: "dispatch_action maps any error surfaced by serving_write.protect() or .verify() (including the lease-loss case above) to WorkflowError::WebhookError; the entire per-step dispatch -- including Delay's -- is separately wrapped by execute_steps in tokio::time::timeout using the step's own timeout_secs if set, else the engine's default_timeout_secs (default 300s), and nothing in the Delay dispatch path checks timeout_secs against duration at definition time, so a step-level timeout_secs smaller than the requested delay produces a StepTimeout before the sleep would otherwise have completed."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/executor.rs:754-757"
      - "crates/buzz-workflow/src/executor.rs:1217-1254"
  - statement: "WorkflowError::code() maps InvalidDefinition to the stable code 'invalid_definition' and StepTimeout to 'step_timeout' -- the two persisted run error_code values a too-long or over-timeout-budget Delay step surfaces -- and a unit test asserts this mapping is stable and separate from the error's Display diagnostic text."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/error.rs:70-83"
      - "crates/buzz-workflow/src/error.rs:96-110"
  - statement: "No unit or integration test in the repository exercises the Delay action's own runtime dispatch behavior (the 270-second cap rejection, the successful sleep-and-complete path, or the lease-loss-during-sleep race); the only Delay-specific tests found are schema round-trip/parsing tests, and the generic parse_duration_secs unit tests already cited, which cover duration-string parsing shared with the Schedule trigger's interval field but not Delay's own dispatch-time behavior."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/schema.rs:384-424"
      - "crates/buzz-workflow/src/executor.rs:1546-1572"
  - statement: "At the recorded revision, architecture-flows-workflow-execution is the one node merged on origin/launchpad whose subject overlaps this one; it documents the workflow run lifecycle as a whole (three trigger paths, the shared step loop, owner-authority/write-fence/webhook-SSRF crossings, and generic mid-run failure behavior) and already records, at the run level, that delay actions are capped at 270 seconds pending the not-yet-built WF-09 scheduled-resume pattern. This node references it rather than restating that content, and narrows into Delay-specific facts that node does not cover: the template-resolution exemption, the validate()-time gap, the lease-hold-during-sleep exposure, and the absence of Delay-specific runtime tests."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/flows/workflow-execution.md"
  - statement: "Corrected during Feature #613's whole-branch review, after all ~70 sibling nodes existed side by side: this node's own initial reasoning noted that architecture/flows/* nodes carry type: architecture matching their directory, then chose type: capabilities anyway for a different directory -- a directory-matches-type argument that actually points the other way once this node's body (organized as trigger/preconditions/ordered-interactions/failure-rollback, per issue #823's own DoD) is compared against templates/flow.md and true siblings send-dm-action, send-message-action, needs-action and agent-shutdown, all already type: architecture for the identical shape. type: architecture is the consistent answer; capabilities.md's own 'product-level noun phrase' framing was correctly judged not to fit a single action step, which is itself evidence against type: capabilities, not for it."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
      - "launchpad/docs/corpus/templates/flow.md"
      - "launchpad/docs/corpus/architecture/flows/workflow-execution.md"
      - "launchpad/docs/corpus/capabilities/workflows/send-dm-action.md"
    confidence: 0.8
  - statement: "Issue #823's Definition of Done requires stating trigger/preconditions/termination, ordered interactions and data/state movement, authentication/authorization/trust-boundary crossings where relevant, and failure/abort/rollback behavior with links to representative verification -- the same checklist shape issue #688 used for architecture-flows-workflow-execution, which is why this node is organized around the same four sections rather than the capability.md template's Capability-statement/Maturity/Boundary shape."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#823 Definition of Done (read directly via gh issue view)"
relationships:
  - type: part-of
    target: capabilities-workflows-workflow
  - type: references
    target: architecture-flows-workflow-execution
---

# Delay action (workflow steps)

The `delay` action pauses a running workflow's step sequence in-process for a bounded
duration before continuing to the next step. It is one of six action types a workflow
step may perform (`send_message`, `send_dm`, `set_channel_topic`, `add_reaction`,
`call_webhook`, `request_approval`, `delay`); this node documents only `delay`'s own
contract. The workflow run lifecycle it executes inside — trigger paths, the shared
step loop's condition/template/timeout machinery in general, and owner-authority /
tenant / webhook trust boundaries — is `architecture-flows-workflow-execution`'s
scope, referenced below rather than restated.

## A note on `type`

No `node.schema.json` enum member names a single action step, and no merged
`templates/` document is scoped that narrowly. This node's path
(`capabilities/workflows/delay-action.md`) was assigned by the corpus plan that
generated the task, not decided here. The body below is organized as trigger,
preconditions, ordered interactions and failure/rollback — the same shape
`templates/flow.md` documents and the same shape ten direct siblings under
`capabilities/workflows/` already carry as `type: architecture`. `type: architecture`
is therefore this node's front-matter value, corrected during Feature #613's
whole-branch review (marked `INFERENCE`, confidence 0.8, in the evidence ledger
above) — a single action step does not cleanly fit `templates/capability.md`'s own
"product-level noun phrase" framing (e.g. "Git hosting") either, which argues against
`type: capabilities`, not for it. The product-level capability this action belongs to
is "Workflow engine (triggers, traces, conditional logic)" as a whole, not `delay` on
its own; that capability is documented separately by `workflow.md`.

## Trigger, preconditions, termination

**Trigger.** A `delay` step's action dispatches when `execute_steps` reaches it in
`def.steps` order, its optional `if:` condition (if any) evaluates true, and its
`duration` field — cloned unresolved, since `resolve_step_templates` does not
template-substitute `Delay`'s field the way it does for every other action's string
fields — is handed to `dispatch_action`.

**Preconditions specific to `delay`:**

1. `duration` must parse via `parse_duration_secs`: an `Nh`/`Nm`/`Ns`-suffixed string,
   or a bare integer assumed to be seconds. Anything else is
   `WorkflowError::InvalidDefinition`.
2. The parsed value must not exceed a hardcoded cap of **270 seconds** — checked
   inside `dispatch_action`'s `Delay` arm, not by `WorkflowDef::validate()`. This is a
   **run-time-only** precondition: `validate()`, the function every definition must
   pass before it can be saved, has no branch inspecting a `delay` step's `duration`
   at all. A workflow whose delay step requests, for example, one hour saves
   successfully and only fails the first time that step actually dispatches.
3. `delay` is not named in `requires_elevated_authority` (only `call_webhook` is), so
   a definition made only of `delay` steps (plus any other non-`call_webhook` action)
   needs no elevated owner role beyond the ordinary active-channel-member check the
   referenced flow node documents at the run level.

**Termination / outcome.** On success, the step sleeps for the parsed duration and
completes with output `{"slept_secs": <seconds>}`, recorded into the run's trace and
`step_outputs` under the step's own id like any other action's output — addressable
by later steps as `steps.<id>.output.slept_secs`. On failure (duration too long, an
unparseable duration, a step timeout, or a lost write lease — see below), the step
aborts the run with the trace accumulated up to that point, per the generic mid-run
failure behavior the referenced flow node already documents.

## Ordered interactions and data/state movement

1. `execute_steps` evaluates the step's optional `if:` expression and, if true, calls
   `resolve_step_templates` — which clones `duration` unchanged for `Delay`, the one
   action whose field is never `{{...}}`-resolved.
2. `execute_steps` wraps the whole dispatch in `tokio::time::timeout`, using the
   step's own `timeout_secs` if set, else the engine's `default_timeout_secs`
   (default 300s). Nothing in the `Delay` dispatch path checks `timeout_secs` against
   `duration` at definition time, so a configured `timeout_secs` smaller than the
   requested delay produces a `StepTimeout` before the sleep would otherwise have
   finished.
3. `dispatch_action` acquires a community serving-write lease
   (`buzz_deletion::acquire_serving_write`) and verifies it, then runs the matched
   `Delay` arm inside that lease's `protect()` wrapper.
4. Inside `protect()`, `duration`'s seconds are parsed and checked against the
   270-second cap (`WorkflowError::InvalidDefinition` if it fails); if the cap
   passes, `tokio::time::sleep` runs for the full parsed duration.
5. `protect()` races the sleep against the lease's own heartbeat-loss cancellation
   signal in a biased `tokio::select!`: the sleep is favored, but if the lease's
   heartbeat is lost first, the in-flight sleep is dropped in place and `protect()`
   returns an error instead of letting it complete.
6. On a successful sleep, `protect()` re-verifies the lease, `dispatch_action` returns
   `StepResult::Completed({"slept_secs": secs})`, and `execute_steps` records the
   `"completed"` trace entry and inserts the output into `step_outputs`.

## Authentication / authorization / trust-boundary crossings

- **Owner authority.** `delay` carries no elevated-authority requirement of its own
  (only `call_webhook` does); it runs under whatever the referenced flow node's
  fail-closed owner-authority recheck already establishes for the run as a whole.
- **Community write-fence / deletion boundary — the one crossing specific to this
  action's shape.** Every action's dispatch is wrapped in the same serving-write
  lease `protect()` call, but `delay` is the only action whose wrapped operation is
  an unconditional in-process wait of up to 270 seconds rather than a bounded network
  or database call. That makes `delay` the action most exposed, among the six, to the
  lease-loss race described above: if a community deletion drain revokes the lease
  while a `delay` step is asleep, the sleep is cancelled mid-flight and the step fails
  rather than completing, whereas a short-lived action's window for the same race is
  comparatively small. This is a structural consequence of `protect()`'s own
  `tokio::select!`, not a `delay`-specific code path — `delay` simply spends longer
  inside it than any other action.

## Failure, abort, rollback behavior

- **Duration too long.** Parsed seconds `> 270` →
  `WorkflowError::InvalidDefinition`, code `invalid_definition` — surfaced only at
  dispatch time, never at save time (see *Preconditions* above).
- **Unparseable duration.** Any string `parse_duration_secs` cannot parse as
  `Nh`/`Nm`/`Ns`/a bare integer → the same `WorkflowError::InvalidDefinition` /
  `invalid_definition` code.
- **Step timeout.** A configured `timeout_secs` smaller than the requested delay (or
  smaller than the 300s default, if unset) aborts the step with
  `WorkflowError::StepTimeout`, code `step_timeout`, before the sleep completes.
- **Write-lease loss mid-sleep.** If the community serving-write lease's heartbeat is
  lost while the step is asleep, `protect()` cancels the in-flight sleep and
  `dispatch_action` maps the resulting error to `WorkflowError::WebhookError`; the
  delay does not resume or retry.
- **No rollback for a completed sleep.** A `delay` step that already completed before
  a later step fails is not itself undone — consistent with the referenced flow
  node's generic statement that mid-run failure never undoes a prior step's effect,
  though a completed `delay` has no external side effect to undo in the first place.
- **Representative verification:**
  - `parse_duration_hours`, `parse_duration_minutes`, `parse_duration_seconds`,
    `parse_duration_plain_number`, `parse_duration_invalid`
    (`crates/buzz-workflow/src/executor.rs:1546-1572`) — cover
    `parse_duration_secs`'s accepted and rejected duration shapes, shared with the
    `Schedule` trigger's `interval` field.
  - `parse_all_action_types` (`crates/buzz-workflow/src/schema.rs:384-424`) — confirms
    a `delay` step round-trips through YAML parsing as `ActionDef::Delay`.
  - `workflow_error_codes_are_stable_and_separate_from_diagnostics`
    (`crates/buzz-workflow/src/error.rs:96-110`) — the `invalid_definition` /
    `step_timeout` code mapping a failing `delay` step's run surfaces.
  - **Gap:** no test in the repository exercises `delay`'s own dispatch-time
    behavior — the 270-second cap rejection, a successful sleep-and-complete run, or
    the lease-loss-during-sleep race — directly. This is stated as a known
    incompleteness, not implied by the tests listed above.

## Scope and omissions

**This node covers** the `delay` action's own contract: its schema, the
template-resolution exemption on its `duration` field, the 270-second cap and where
(only at dispatch, never at save) it is enforced, its lack of an elevated-authority
requirement, its successful-completion output shape, and the write-fence exposure
particular to holding a serving-write lease across an in-process sleep rather than a
bounded call.

**It does not cover, and these are gaps owned elsewhere:**

| Not covered here | Owned by |
|---|---|
| The three trigger paths, the shared step loop in general, owner-authority recheck mechanics, tenant/webhook trust boundaries, and generic mid-run failure behavior | `architecture-flows-workflow-execution` |
| The other five action types (`send_message`, `send_dm`, `set_channel_topic`, `add_reaction`, `call_webhook`, `request_approval`) | Not yet drafted as of this node's writing (see sibling tasks in the same corpus-plan batch) |
| The not-yet-built scheduled-resume pattern for delays longer than 270 seconds (referred to in code as future work "WF-09") | Not yet implemented; no corpus node exists for it |
| `buzz_deletion`'s serving-write lease mechanism in general (acquisition, heartbeat, release, and its role in community deletion draining) beyond the one race this node narrates | Not yet drafted as its own node |

**Expected but not verified when this node was written:**

- Whether the lease-loss-during-sleep race has ever actually been observed in
  production, or only exists as a structural possibility read from `protect()`'s
  code, was not checked — no incident record or test reproducing it was found.
- Whether any workflow author-facing UI (desktop, CLI) surfaces the 270-second cap or
  the "use the scheduled resume pattern" guidance from the error message before a
  workflow is saved was not checked; the cap is invisible until first dispatch, per
  the *Preconditions* section above.
