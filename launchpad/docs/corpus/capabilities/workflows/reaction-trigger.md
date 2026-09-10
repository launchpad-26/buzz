---
id: capabilities-workflows-reaction-trigger
type: architecture
status: draft
origin: launchpad
audiences:
  - agent
  - developer
evidence:
  - statement: "This node was authored and checked against repository revision cad6c375fdcc590158c1456c9fc7875f0f84a844."
    entry_class: FACT
    evidence:
      - "commit cad6c375fdcc590158c1456c9fc7875f0f84a844"
  - statement: "TriggerDef::ReactionAdded is one of six TriggerDef variants and carries two optional fields, emoji and filter, both defaulted to None by serde when omitted from a workflow's YAML/JSON definition."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/schema.rs:46-53"
  - statement: "TriggerDef's serde tag is \"on\" with rename_all snake_case, so a workflow definition selects this trigger with the literal YAML key `on: reaction_added`, confirmed by a round-trip parse test asserting emoji \"clipboard\" and filter 'trigger_message_id == \"abc123\"' are read back from exactly that form."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/schema.rs:36-37"
      - "crates/buzz-workflow/src/schema.rs:337-348"
  - statement: "trigger_matches_event maps TriggerDef::ReactionAdded to a single kind comparison, kind_u32 == KIND_REACTION, independent of whether emoji or filter is set on the trigger; Schedule and Webhook triggers always return false from this function because they are never fired by a channel event."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/lib.rs:1038-1047"
  - statement: "KIND_REACTION is the constant 7 in the kind registry, and a unit test confirms trigger_matches_event(ReactionAdded, ..) returns true for kind 7 and false for kind 9 (stream message) and kind 45001 (forum post), while a sibling test confirms a ReactionAdded trigger carrying a non-None emoji still matches on kind alone -- the emoji is not consulted at this stage."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs:58"
      - "crates/buzz-workflow/src/lib.rs:1450-1462"
      - "crates/buzz-workflow/src/lib.rs:1464-1474"
  - statement: "should_fire_workflow applies the trigger's optional emoji narrowing after the kind match already passed: when TriggerDef::ReactionAdded.emoji is Some(expected), the incoming reaction is skipped (workflow not fired) unless trigger_ctx.emoji is exactly equal to expected; a None emoji imposes no narrowing and any reaction on the matched kind proceeds to the next check."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/lib.rs:883-902"
  - statement: "After the emoji check, should_fire_workflow evaluates the trigger's optional evalexpr filter (present on MessagePosted, ReactionAdded and DiffPosted alike) against the trigger context with no step outputs yet available; Ok(false) or an evaluation Err both skip the workflow silently rather than failing a run, and a filter referencing trigger_message_id is confirmed by test to select or reject a reaction by its target message id."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/lib.rs:904-928"
      - "crates/buzz-workflow/src/lib.rs:1376-1404"
  - statement: "build_trigger_context derives the emoji field only for KIND_REACTION events, copying the event's raw content field verbatim (NIP-25 stores the reaction character or shortcode as content); every other event kind gets an empty emoji string, and a unit test confirms a \"\\u{1F44D}\" (thumbs-up) reaction event round-trips into both ctx.text and ctx.emoji unchanged."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/lib.rs:951-957"
      - "crates/buzz-workflow/src/lib.rs:1745-1758"
  - statement: "build_trigger_context derives message_id for a KIND_REACTION event by scanning its tags in reverse for the last `e` tag whose value is a 64-character hex string (distinguishing a NIP-25 event-id target from a UUID channel reference), falling back to the reaction event's own id if no such tag is found; a unit test with two `e` tags (an earlier thread-root id and a later direct-target id) confirms the last one wins, matching NIP-25's own ordering convention."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/lib.rs:959-987"
      - "crates/buzz-workflow/src/lib.rs:1822-1845"
  - statement: "on_event, the entry point every channel-event trigger (including reaction_added) fires through, returns early without evaluating any workflow when the stored event carries no channel_id at all, before the reaction-specific kind/emoji/filter checks ever run."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/lib.rs:325-332"
  - statement: "Within on_event's per-workflow loop, a candidate workflow is skipped (continue, no run created) at the first of five sequential gates it fails: definition parse error, disabled or kind-mismatched trigger (trigger_matches_event), should_fire_workflow's emoji/filter narrowing, a failed owner-authority recheck, or a database error creating the run row; only a workflow surviving all five reaches create_workflow_run and is handed to tokio::spawn for execution."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/lib.rs:370-420"
  - statement: "The relay's post-store event handler only spawns WorkflowEngine::on_event for a stored event that is none of: a workflow-execution kind, a command kind, a relay-signed event carrying a \"buzz:workflow\" tag, or a gift wrap -- a reaction event (kind 7) satisfies all four exclusions in the ordinary case, so it reaches on_event the same way a message or diff event does."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs:520-533"
      - "crates/buzz-relay/src/handlers/event.rs:543-546"
  - statement: "WorkflowDef::validate() classifies reaction_added as a message-based trigger (together with message_posted and diff_posted, as opposed to schedule and webhook): a step with reply_in_thread: true is accepted at definition-save time only when the workflow's trigger is message-based, because reply_in_thread needs a triggering message id to reply to and a reaction-triggered run's message_id is exactly the reacted-to message resolved above."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/schema.rs:219-242"
  - statement: "architecture-flows-workflow-execution is a corpus node merged to origin/launchpad documenting the shared executor (concurrency limiting, per-step template resolution and dispatch, action failure/timeout handling), the fail-closed owner-authority recheck (SEC-006), and the terminal run states that this document's reaction-triggered runs feed into once should_fire_workflow and the authority check both pass; this document narrates the reaction-specific trigger evaluation that precedes that shared machinery rather than re-describing it."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/flows/workflow-execution.md"
  - statement: "The only merged flow-shaped node in this corpus at the recorded revision, architecture-flows-workflow-execution, carries type: architecture rather than a dedicated flow value (node.schema.json's enum has none); this document follows that precedent for the same reason -- an ordered, multi-step runtime interaction narrative is the closest fit among the thirteen enum members, and no better-fitting value was found."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/architecture/flows/workflow-execution.md"
      - "launchpad/docs/corpus/schema/node.schema.json"
    confidence: 0.75
  - statement: "Issue #831's own definition of done requires this document to state trigger, preconditions and termination/outcome; list ordered interactions and data/state movement; identify authentication/authorization/trust-boundary crossings where relevant; and document failure/abort/rollback behavior with links to representative verification."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#831 definition of done"
relationships:
  - type: part-of
    target: capabilities-workflows-workflow
  - type: part-of
    target: architecture-flows-workflow-execution
---

# Reaction-added workflow trigger

How `crates/buzz-workflow`'s `reaction_added` trigger decides, for one incoming NIP-25
reaction event, whether a workflow fires -- the kind check, the optional emoji and
filter narrowing, and the reaction-specific fields (`emoji`, `message_id`) it exposes to
the workflow's own steps. This is the trigger-evaluation half of one of the three
channel-event trigger kinds `architecture-flows-workflow-execution` names in general
terms; this node is the canonical, detailed source for the `reaction_added` case
specifically, and defers to that node for the shared executor, authority and
finalization machinery every trigger path feeds into once it decides to fire.

**Not this node's subject:** the opposite direction -- a workflow *step* adding a
reaction (the `add_reaction` action) -- is a separate capability, tracked as a sibling
task (`launchpad-26/buzz#830`, not yet drafted at this writing) and not described here.

## Trigger, preconditions, termination

**Trigger.** A workflow whose definition's `trigger` is `TriggerDef::ReactionAdded`
(YAML/JSON form: `on: reaction_added`, with optional `emoji` and `filter` fields) is a
candidate to fire whenever a `kind:7` (NIP-25 reaction) event is stored in a channel the
workflow is enabled for.

**Preconditions, in the order they are actually checked:**

1. The stored event must carry a `channel_id` at all -- a reaction with no channel scope
   (for example, a reaction inside a DM) never reaches any workflow evaluation, for any
   trigger type, before the checks below run.
2. The relay's post-store handler must not have excluded the event as a
   workflow-execution kind, a command kind, a relay-signed `buzz:workflow`-tagged
   message, or a gift wrap -- an ordinary reaction event satisfies all four exclusions.
3. The candidate workflow's stored `definition` must parse back into a `WorkflowDef`,
   and the definition must be `enabled`.
4. `trigger_matches_event` must return true for the event's kind: for `ReactionAdded`
   this means the event's kind is exactly `KIND_REACTION` (7). This check consults only
   the trigger's *type* -- neither the trigger's `emoji` field nor its `filter` field
   narrows the match at this stage; a `ReactionAdded` trigger with `emoji: Some(..)`
   still matches every reaction event, deferring the narrowing to the next step.
5. `should_fire_workflow` must return true:
   - If the trigger's `emoji` is `Some(expected)`, the incoming reaction's content
     (`trigger_ctx.emoji`) must equal `expected` exactly, or the workflow is skipped.
   - The trigger's optional `filter` (an evalexpr expression, evaluated against the
     trigger context with no step outputs yet available) must evaluate to `true`; a
     `false` result or an evaluation error both skip the workflow without treating it as
     a run failure.
6. The workflow owner must currently hold sufficient channel authority -- re-checked at
   fire time rather than trusted from when the workflow was saved. This is the same
   `check_owner_authority` gate every channel-event trigger uses; see
   `architecture-flows-workflow-execution`'s *Trust-boundary crossings* for its full
   rule (SEC-006), which this document does not restate.

**Termination / outcome, at this trigger's own boundary.** Failing any precondition
above is a silent no-op for that one workflow: `on_event` `continue`s to the next
candidate workflow rather than aborting, and produces no `workflow_runs` row and no
error. A `ReactionAdded` trigger that passes every check above hands off to
`create_workflow_run` and `tokio::spawn`s the shared executor -- from that point, the
run's `Pending` → `Running` → `Completed`/`Failed` progression and the executor's own
failure modes are `architecture-flows-workflow-execution`'s subject, not this one's.

## Ordered interactions and data/state movement

1. A client's signed `kind:7` reaction event is submitted and durably stored by the
   relay before workflow evaluation begins (the storage/ack path and workflow
   evaluation are decoupled -- see *Failure, abort, rollback behavior*).
2. The relay's post-store event handler checks the four exclusions above and, finding
   none apply, `tokio::spawn`s `WorkflowEngine::on_event(community_id, &stored_event)`
   asynchronously.
3. `on_event` requires `event.channel_id` to be `Some`; a reaction with no channel scope
   returns immediately with no further work.
4. `on_event` reads the channel's enabled-workflow list (a cached lookup shared across
   all trigger types -- see `architecture-flows-workflow-execution` for the cache's own
   TTL and invalidation rule, not restated here) and returns immediately if it is empty.
5. `build_trigger_context` maps the stored reaction event into a `TriggerContext`:
   `text` and `emoji` both become the event's raw `content` (the NIP-25 emoji character
   or shortcode); `author` is the event's signing pubkey, never a spoofable `actor` tag;
   `message_id` is the *target* message's event id, read from the last `e` tag whose
   value is a 64-hex-character event id (falling back to the reaction event's own id if
   none is found); `channel_id` and `timestamp` are copied from the stored event.
6. For each enabled workflow definition in the channel, in the order `trigger_matches_event`
   (step 4 of *Trigger, preconditions, termination*), `should_fire_workflow` (step 5),
   and `check_owner_authority` (step 6) are evaluated in that sequence, each an early
   `continue` on failure -- so an emoji mismatch is decided before an authority lookup is
   ever made, and an authority denial is decided before any database write.
7. On success, `create_workflow_run` inserts the run row (scoped to the community and
   workflow, carrying the triggering event's id and the serialized trigger context as
   its initial data), and the engine `tokio::spawn`s `executor::execute_run` with a
   clone of the parsed definition and trigger context -- the shared step loop
   `architecture-flows-workflow-execution` documents takes over from here.

## Trust-boundary crossings

- **Owner authority, fail-closed (SEC-006).** A reaction-triggered run is gated by the
  same re-check every channel-event trigger uses: the workflow owner's *current* channel
  membership and role are re-verified immediately before `create_workflow_run`, not
  trusted from when the definition was saved, and any authority-lookup error denies
  rather than passes through. A reaction-triggered workflow whose steps include
  `call_webhook` is held to the same elevated-authority requirement (owner/admin role)
  as any other trigger type, because the exfiltration risk `call_webhook` poses is a
  property of the workflow's steps, not of what triggered it. The full rule, including
  the community/tenant fence and the webhook-specific authentication this trigger path
  does not use, is `architecture-flows-workflow-execution`'s *Trust-boundary crossings*
  section.
- **Author attribution cannot be spoofed by tag content.** `build_trigger_context`'s
  `author` field is read from the reaction event's own verified signature (`pubkey`),
  never from an `actor` tag or other signer-controlled metadata a reaction event could
  carry -- a workflow condition or template that reads `trigger.author` is reading who
  actually signed the reaction, not a claimed identity inside it.
- **Target-message resolution is not itself an authorization check.** `message_id`
  is resolved structurally (last valid `e` tag, or the reaction's own id as fallback)
  and carries no verification that the reacted-to message still exists, is visible to
  the reactor, or belongs to the same channel; a workflow step that uses `message_id`
  (for example, to reply in a thread) relies on the downstream action's own checks for
  that, which this document does not cover.

## Failure, abort, rollback behavior

- **Every precondition failure in *Trigger, preconditions, termination* is a silent
  skip of that one workflow, not an error surfaced anywhere else.** A parse failure logs
  a warning; a kind mismatch, an emoji mismatch, a `false`/erroring filter, and an
  authority denial each just `continue` the loop with at most a debug/warn log line --
  none of them abort evaluation of the *other* enabled workflows in the same channel,
  and none of them produce a `workflow_runs` row.
- **The triggering reaction event is never affected by anything that happens next.**
  Because `on_event` is spawned asynchronously from the relay's post-store hook, the
  reaction event is already durably stored (and, on the HTTP submit path, already
  acknowledged to the client) before any of this trigger evaluation runs -- a filter
  error, an authority denial, or a downstream run failure has no path back to the
  reaction event itself, and nothing about it is retried or rolled back.
- **Once a run is created, its failure modes belong to the shared executor, not to this
  trigger.** A step-level condition, template, dispatch or timeout error inside the
  executor aborts the *run*, not the trigger evaluation that created it; see
  `architecture-flows-workflow-execution`'s *Failure, abort, rollback behavior* for that
  half, including that a mid-run failure does not undo an already-sent message.
- **Representative verification** (all in `crates/buzz-workflow`, unit tests unless
  noted):
  - `trigger_matches_reaction`, `reaction_added_matches_kind_7_only` and
    `reaction_added_with_emoji_filter_still_matches_kind_7` (`src/lib.rs`) -- the kind-only
    match and that a non-`None` `emoji` field does not narrow `trigger_matches_event`.
  - `reaction_filter_matches_target_message` (`src/lib.rs`, async) -- that
    `should_fire_workflow`'s filter selects or rejects a reaction by its resolved
    `trigger_message_id`.
  - `build_trigger_context_reaction_event` and
    `test_build_trigger_context_reaction_multiple_e_tags` (`src/lib.rs`) -- the
    `emoji`/`text` copy from event content, and the last-`e`-tag-wins resolution of
    `message_id` across a thread-root plus direct-target pair of tags.
  - `parse_reaction_added_trigger` (`src/schema.rs`) -- the `on: reaction_added` YAML
    form round-tripping `emoji` and `filter` correctly.

## Scope and omissions

**This node covers** the `reaction_added` trigger's own matching and narrowing logic
(`trigger_matches_event`, `should_fire_workflow`'s emoji and filter checks), the
reaction-specific fields `build_trigger_context` derives (`emoji`, `message_id`), the
preconditions common to all channel-event triggers as they apply to a reaction event,
and the trust-boundary and failure behavior specific to this trigger's own evaluation
window (before a run is created).

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The shared step-loop executor, concurrency limiting, and terminal run states | `architecture-flows-workflow-execution` |
| The full owner-authority rule (SEC-006) and the community/tenant write fence | `architecture-flows-workflow-execution` |
| The `add_reaction` workflow *action* -- a workflow adding a reaction, the opposite direction from this trigger | `launchpad-26/buzz#830` (not yet drafted) |
| The `message_posted` and `diff_posted` sibling channel-event triggers | Not yet a dedicated corpus node at this writing |
| The channel-scoped workflow-list cache's TTL and invalidation rule | `architecture-flows-workflow-execution` |
| Whether any consumer other than the workflow engine itself relies on the exact `emoji` string format NIP-25 clients send | Not established anywhere in this repository at the checked revision |

**Expected but not verified when this node was written:**

- **Whether a reaction's `content` field can carry a custom-emoji shortcode format
  distinct from a literal Unicode character was not traced beyond the code comment
  describing it** (`crates/buzz-workflow/src/lib.rs:951-952` says "emoji character or
  shortcode (e.g. \"👍\", \"+\", \"-\")"); no NIP-25 client-side encoding was inspected to
  confirm the full set of forms `content` can actually take in practice.
- **Whether removing a reaction (NIP-09 deletion of a `kind:7` event) has any bearing on
  a workflow already triggered by its creation was not checked.** Nothing in
  `on_event`'s reaction path was found to special-case a subsequently deleted reaction,
  but the deletion-handling code path itself was not read for this node.
