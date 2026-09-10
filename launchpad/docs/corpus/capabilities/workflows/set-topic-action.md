---
id: capabilities-workflows-set-topic-action
type: architecture
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
  - statement: "ActionDef::SetChannelTopic is a workflow step whose only field is `topic: String`, tagged `action: set_channel_topic` in YAML/JSON."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/schema.rs:117-120"
  - statement: "Corrected during Feature #613's whole-branch review, after all ~70 sibling nodes existed side by side: this node originally followed sibling #830 (reaction-action.md)'s then-unmerged type: capabilities choice as the closest available precedent. Once all siblings were visible together, this node's own body (trigger/preconditions/ordered-interactions/failure-rollback, matching templates/flow.md) and true siblings send-dm-action, send-message-action and needs-action -- all type: architecture for the identical shape -- settle the question the other direction. type: architecture is the consistent answer for this class of single-action node."
    entry_class: INFERENCE
    confidence: 0.8
    evidence:
      - "launchpad/docs/corpus/templates/flow.md"
      - "launchpad/docs/corpus/capabilities/workflows/send-dm-action.md"
      - "launchpad/docs/corpus/capabilities/activity/needs-action.md"
  - statement: "The `dispatch_action` match arm for `SetChannelTopic` logs a warning and immediately returns `Err(WorkflowError::NotImplemented(\"SetChannelTopic\".into()))` -- no database write, no Nostr event construction, no HTTP call, and no call into `ActionSink` (the trait through which every other side-effecting action reaches the relay) is made."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/executor.rs:649-653"
  - statement: "`ActionSink` (the trait the relay implements to give the executor real DB/event access) declares exactly one method, `send_message`; no method for updating a channel's topic or description exists on it, so even a future fix to the `SetChannelTopic` dispatch arm has no existing sink method to call into today."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/action_sink.rs:48-70"
  - statement: "`WorkflowError::code()` maps `NotImplemented` to the stable string `\"action_not_implemented\"`, the same code every other not-yet-implemented action (currently only `SendDm`) produces, so a run's persisted `error_code` alone cannot distinguish a `SetChannelTopic` failure from a `SendDm` failure -- only the run's `execution_trace` step id can."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/error.rs:65"
      - "crates/buzz-workflow/src/error.rs:81"
  - statement: "Within the shared template-resolution step that runs before every action dispatches, `SetChannelTopic`'s `topic` field is resolved for `{{trigger.X}}` / `{{steps.ID.output.X}}` placeholders the same way every other action's string fields are, and a resolution error aborts the run before `SetChannelTopic`'s own dispatch code executes."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/executor.rs:432"
  - statement: "The product's own real, working path for setting a channel's topic (`buzz-cli`'s `channels set-topic` subcommand, via `cmd_set_channel_topic`) builds a signed NIP-29 kind:9002 edit-metadata event with `buzz_sdk::build_set_topic` -- carrying an `h` tag for the channel and a `topic` tag -- and submits it through the client's normal signed-event path; the relay's `handle_edit_metadata` (dispatched from the kind:9002 arm of its command-event router) applies the change and republishes the channel's addressable kind:39000 metadata event. The workflow engine's `SetChannelTopic` action is not wired to this path, or to any other mechanism, in any way."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/commands/channels.rs:1271-1282"
      - "crates/buzz-sdk/src/builders.rs:662-669"
      - "crates/buzz-relay/src/handlers/side_effects.rs:203"
      - "crates/buzz-relay/src/handlers/side_effects.rs:496-513"
  - statement: "No unit or integration test in `crates/buzz-workflow` exercises the `SetChannelTopic` dispatch arm or asserts the `action_not_implemented` failure path; the only test referencing `SetChannelTopic` (`parse_all_action_types`) confirms its YAML/JSON shape round-trips and parses into the correct enum variant, not that dispatch behaves as this node describes."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/schema.rs:394"
      - "crates/buzz-workflow/src/schema.rs:410"
  - statement: "`finalize_run` is the single place that maps an executor result to a DB run-status update; on the `Err((e, progress))` branch it marks the run `RunStatus::Failed` at the failing step index, persists the accumulated trace up to that point, and records `WorkflowRunFailure { code: e.code(), message: e.to_string() }` -- there is no retry and no rollback of any side effect an earlier step in the same run already produced."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/lib.rs:213"
      - "crates/buzz-workflow/src/lib.rs:278-296"
  - statement: "`dispatch_action` re-validates the run's community write-fence (`buzz_deletion::acquire_serving_write` then `.verify()`) immediately before every action's own match arm runs, regardless of which action it is; `SetChannelTopic`'s arm executes inside that same fenced `protect(...)` block, so the generic fence check happens before its stub returns, even though the stub itself performs no further boundary-crossing side effect."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/executor.rs:551-566"
  - statement: "VISION_PROJECTS.md's own Status table marks 'Workflow engine (triggers, traces, conditional logic)' as shipped, without naming any individual action type's own functional status."
    entry_class: FACT
    evidence:
      - "VISION_PROJECTS.md:250"
  - statement: "Issue #835's own Definition of Done requires this node to state trigger/preconditions/termination, list ordered interactions and data/state movement, identify authentication/authorization/trust-boundary crossings where relevant, and document failure/abort/rollback behavior with links to representative verification -- the reason this node is organized around those sections rather than a general capability narrative."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#835 definition of done"
  - statement: "Issue #834 ('task: document capabilities/workflows/send-message-action.md') and issue #833 ('task: document capabilities/workflows/send-dm-action.md') are sibling tasks in Feature #613 covering other action types, and were not opened for their own body text while drafting this node."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#613 child issue list (gh branch listing of task/833-send-dm-action, task/834-send-message-action)"
  - statement: "At the recorded revision, the corpus tree on `origin/launchpad` carries a merged, active/draft node at `launchpad/docs/corpus/architecture/flows/workflow-execution.md` (id `architecture-flows-workflow-execution`) documenting the shared trigger paths, run-semaphore/permit acquisition, and community write-fence this node's action participates in, and a merged, active template node at `launchpad/docs/corpus/templates/capability.md` (id `corpus-template-capability`); both are valid relationship targets."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/flows/workflow-execution.md"
      - "launchpad/docs/corpus/templates/capability.md"
relationships:
  - type: part-of
    target: capabilities-workflows-workflow
  - type: references
    target: architecture-flows-workflow-execution
  - type: implements
    target: corpus-template-capability
---

# Workflow set-topic action: capability

A Buzz workflow step type — `action: set_channel_topic` — intended to let an
automated workflow update a channel's topic without a human or agent running the
command themselves. It is one of seven action types (`send_message`, `send_dm`,
`set_channel_topic`, `add_reaction`, `call_webhook`, `request_approval`, `delay`) a
workflow step may perform after its trigger fires and any `if:` condition passes.

## Maturity

**Recognized and schema-valid; not implemented at all — a pure stub, more
completely unimplemented than a broken HTTP call would be.** `set_channel_topic`
parses, round-trips through YAML/JSON, and passes `WorkflowDef::validate()`
cleanly as part of the "Workflow engine" capability VISION_PROJECTS.md's own
Status table marks shipped. But its dispatch arm in `executor.rs` does nothing
beyond logging a warning and returning `WorkflowError::NotImplemented` — no
database write, no Nostr event construction, no HTTP call, and no call into
`ActionSink` (the trait every other side-effecting action reaches the relay
through). `ActionSink` itself has no method for updating a channel's topic or
description at all, so there is currently no sink method a fixed dispatch arm
could even call into. This is a stricter case of the pattern found in this
Feature's sibling node for `add_reaction` (#830): that action at least attempts a
real (if doomed) HTTP call before failing; `set_channel_topic` attempts nothing.
Reinforcing that this was designed but deliberately deferred rather than removed:
the product's actual channel-topic-setting path (`buzz-cli`'s `channels
set-topic`) already works end to end — it builds a signed NIP-29 kind:9002
edit-metadata event and submits it through the normal event-submission path,
which the relay's `handle_edit_metadata` applies and republishes as the
channel's kind:39000 metadata — but the workflow engine's action has never been
wired to it.

## Trigger, preconditions, termination

**Trigger.** `set_channel_topic` does not itself trigger a workflow; it executes
as one step inside a run already dispatched by one of the three trigger paths
`architecture-flows-workflow-execution` describes (channel event, schedule,
webhook), after the shared executor's per-step `if:` check passes.

**Preconditions, checked at dispatch time:**

1. The `topic` field must resolve its template placeholders (`{{trigger.X}}` /
   `{{steps.ID.output.X}}`) successfully; a resolution error aborts the run
   before `set_channel_topic`'s own dispatch code runs, identically to every
   other action's string fields.
2. The generic community write-fence (`acquire_serving_write` +
   `.verify()`) that `dispatch_action` re-checks before every action's match arm
   still runs for this action — but because the stub performs no further side
   effect, that fence check is the only boundary crossing that happens at all.
3. No precondition specific to `set_channel_topic` itself exists beyond these,
   because the dispatch arm never reaches any topic-specific logic — it returns
   immediately after logging.

**Termination/outcome.** Unlike every other action type, `set_channel_topic` has
exactly one reachable outcome today: `Err(WorkflowError::NotImplemented(...))`.
There is no `Completed` path, no partial success, and no skip — reaching this
step's dispatch always fails the run at this step, unconditionally.

## Ordered interactions and data/state movement

1. The executor's `if:` check passes; the `topic` template placeholder is
   resolved.
2. The shared per-action community write-fence is re-verified (as it is before
   every action's dispatch, regardless of action type).
3. The `SetChannelTopic` match arm executes: it logs a warning
   (`"SetChannelTopic not yet implemented"`) and returns
   `Err(WorkflowError::NotImplemented("SetChannelTopic".into()))`. No channel
   record, no Nostr event, and no `step_outputs` entry is ever produced by this
   step — data movement stops here.
4. `finalize_run` receives the `Err` result, marks the run `RunStatus::Failed` at
   this step's index, persists the trace accumulated up to (but not including) a
   successful entry for this step, and records
   `WorkflowRunFailure { code: "action_not_implemented", message: <Display of the
   error> }`.
5. No later step in the same run executes; the run terminates at this step.

## Trust-boundary crossings

The only boundary crossing that occurs is the generic one every action's
dispatch arm sits behind: `dispatch_action` re-validates the run's community
write-fence immediately before the `match action { ... }` block, so a stale or
lost community lease denies the step before `SetChannelTopic`'s own arm runs.
Beyond that generic check, `set_channel_topic` crosses no further trust boundary
today, because it never reaches a database write, an event-signing step, or an
outbound call — there is no channel-scoped authorization check, no
owner-authority check, and no data leaves the process. This differs from the
product's real topic-setting path (`buzz-cli` → kind:9002 → relay), which does
cross a real trust boundary: the relay's kind:9002 handler enforces a
`ChannelsWrite`-scoped authorization check before applying the edit. A future
implementation of this dispatch arm would need to add an equivalent
authorization boundary — today there is none to describe because there is no
side effect to authorize.

## Failure, abort, rollback behavior

- Every invocation of this action fails, unconditionally, with
  `WorkflowError::NotImplemented("SetChannelTopic")`
  (`error_code: "action_not_implemented"`) — the same code `SendDm` (the only
  other currently-stubbed action) also produces, so a run's persisted
  `error_code` alone cannot distinguish a `set_channel_topic` failure from a
  `send_dm` failure; only the run's `execution_trace` step id can.
- Like every other action, a `set_channel_topic` failure aborts only the
  *remaining* steps of the run; nothing rolls back any side effect an earlier
  step in the same run already produced, because `finalize_run` only persists a
  trace and a terminal status — it has no compensating-action mechanism.
- There is no retry: `execute_steps` returns the error immediately on the first
  `Err` from `dispatch_action`, with no backoff or re-attempt logic anywhere in
  the executor for any action type.
- **Representative verification.** No test exercises this failure path directly.
  `parse_all_action_types` (schema.rs:394,410) verifies only that
  `set_channel_topic` parses into the correct enum variant and round-trips
  through YAML/JSON — it does not construct an executor or assert the
  `NotImplemented` outcome this node describes.

## Scope and omissions

**This node covers** what the `set_channel_topic` workflow action currently does
(and does not do) when a workflow run reaches it: its schema shape, its
unconditional `NotImplemented` dispatch outcome, the absence of any `ActionSink`
method it could call into even if fixed, its lack of any trust-boundary crossing
beyond the shared per-action fence check, its failure/termination behavior, and
the real (but unconnected) product-level path that already performs the
equivalent channel-topic update outside the workflow engine.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The shared trigger paths, permit/concurrency handling, and community write-fence mechanics every action participates in | `architecture-flows-workflow-execution` |
| The generic corpus template this node's shape follows | `corpus-template-capability` |
| The real, working channel-topic-update path (`buzz-cli` → kind:9002 → relay) as a capability in its own right | not yet documented by any merged corpus node |
| Other workflow action types (`send_message`, `send_dm`, `add_reaction`, `call_webhook`, `request_approval`, `delay`) | their own sibling `capabilities/workflows/*` tasks in Feature #613 |
| Whether/how a future implementation should wire this action to the relay (a new `ActionSink` method, reuse of the kind:9002 command path, or something else) | not yet decided; no linked implementation issue exists at the time this node was written |

**Expected but not verified when this node was written:**
- **No test exercises `set_channel_topic`'s dispatch arm at runtime.** The only
  coverage is a YAML/JSON parse round-trip; the `NotImplemented` outcome and its
  interaction with `finalize_run` are read from the source, not confirmed by a
  passing test asserting that exact behavior.
- **This is now resolved, not open:** `type: architecture` is the settled convention
  for single-action/trigger nodes under `capabilities/workflows/*` — see the corrected
  `INFERENCE` evidence entry above. Umbrella nodes describing the capability as a whole
  (`workflow.md`, `workflow-definition.md`) remain `type: capabilities`.
