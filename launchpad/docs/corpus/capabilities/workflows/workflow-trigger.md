---
id: capabilities-workflows-workflow-trigger
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
  - statement: "TriggerDef is a five-variant enum -- MessagePosted (optional filter), ReactionAdded (optional emoji, optional filter), DiffPosted (optional filter), Schedule (cron xor interval), and Webhook (no fields) -- and is the single umbrella type every workflow definition's trigger field holds."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/schema.rs:38-71"
  - statement: "There is no single generic dispatcher that decides whether a TriggerDef fires -- three independent engine entry points each apply their own matching logic against the same enum: the channel-event path (WorkflowEngine::on_event), the cron loop (WorkflowEngine::run), and the webhook handler (api::bridge::workflow_webhook)."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/lib.rs:320-410"
      - "crates/buzz-workflow/src/lib.rs:489-598"
      - "crates/buzz-relay/src/api/bridge.rs:2001-2040"
  - statement: "The channel-event path (on_event) is the only entry point that calls trigger_matches_event and should_fire_workflow; for each candidate workflow it skips unless trigger_matches_event(&def.trigger, kind_u32) returns true (line 379) and then unless should_fire_workflow(&def, &trigger_ctx, workflow.id) also returns true (line 383) -- both checks run before any owner-authority recheck or run creation."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/lib.rs:379"
      - "crates/buzz-workflow/src/lib.rs:383"
  - statement: "trigger_matches_event matches a stored event's Nostr kind against exactly one TriggerDef variant per event: MessagePosted only for KIND_STREAM_MESSAGE, ReactionAdded only for KIND_REACTION, DiffPosted only for KIND_STREAM_MESSAGE_DIFF -- and it always returns false for Schedule and Webhook, since a channel event can never satisfy either of those two variants."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/lib.rs:1038-1047"
  - statement: "should_fire_workflow applies each message-based trigger's own optional narrowing after the kind match already passed: an exact-string comparison against ReactionAdded's optional emoji field (mismatch skips the workflow), then an evalexpr filter expression for MessagePosted, ReactionAdded, or DiffPosted evaluated against the trigger context with no step outputs yet available -- Schedule and Webhook triggers have no filter field and always pass this stage with `None`, but they are already excluded earlier by trigger_matches_event, so this function is only ever reached for a message-based trigger."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/lib.rs:883-931"
  - statement: "A filter-evaluation error inside should_fire_workflow is logged as a warning and treated as skipping the workflow (return false), not as aborting anything -- there is no run yet at this stage for an abort to affect."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/lib.rs:883-931"
  - statement: "The cron loop (run()) never calls trigger_matches_event or should_fire_workflow. It matches &def.trigger directly against two Schedule sub-patterns -- TriggerDef::Schedule { cron: Some(expr), interval: None } computes a cron-window instant, TriggerDef::Schedule { cron: None, interval: Some(dur) } computes an interval-bucket instant -- and its catch-all arm explicitly discards every other pattern (MessagePosted, ReactionAdded, DiffPosted, Webhook, and a malformed Schedule carrying both or neither field) with the comment 'Non-schedule triggers handled by on_event()'."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/lib.rs:541-598"
  - statement: "The webhook handler (workflow_webhook) never calls trigger_matches_event, should_fire_workflow, or the cron loop's pattern match. Its own precondition is `if !matches!(def.trigger, buzz_workflow::TriggerDef::Webhook)` -- any other variant is rejected with 400 Bad Request before the shared secret is even checked, let alone before a run is created."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs:2036"
  - statement: "WorkflowDef::validate() enforces trigger-shaped preconditions independent of any fire attempt: a Schedule trigger must specify exactly one of cron or interval (both present or both absent is rejected), a present cron expression is syntax-checked via validate_cron, and a present interval is duration-parsed and rejected below 60 seconds because the cron loop itself only ticks once a minute -- so a sub-minute interval could never fire correctly."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/schema.rs:244-274"
  - statement: "validate() also rejects, at definition-save time, any step whose action is SendMessage with reply_in_thread: true when the workflow's trigger is not one of MessagePosted, ReactionAdded, or DiffPosted -- Schedule and Webhook triggers have no triggering message to reply to, so this combination is refused before it can fail silently at run time."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/schema.rs:216-242"
  - statement: "node.schema.json's type enum has thirteen members and none is named flow, dynamic, trigger, or dispatch; the corpus's own flow template (a node whose required sections are trigger/preconditions/termination, ordered interactions, trust-boundary crossings, and failure/abort/rollback -- the same four categories issue #843's own Definition of Done names) states that a flow-shaped instance node carries type: architecture, and the already-merged architecture-flows-workflow-execution.md node follows that precedent for the closely related full-run-lifecycle document. This node's own Definition of Done (issue #843) reproduces that same four-category shape, so it follows the same precedent rather than type: capabilities -- whose own template explicitly excludes 'the step-by-step path one interaction through a capability takes' as flow's territory, not capability's."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
      - "launchpad/docs/corpus/templates/flow.md"
      - "launchpad/docs/corpus/templates/capability.md"
      - "launchpad/docs/corpus/architecture/flows/workflow-execution.md"
    confidence: 0.65
  - statement: "Issue #843's Definition of Done requires this node to state trigger/preconditions/termination, list ordered interactions and data/state movement, identify authentication/authorization/trust-boundary crossings where relevant, and document failure/abort/rollback behavior with links to representative verification, while also requiring that this document stay at the umbrella/dispatch level and not duplicate the individual trigger-type content owned by sibling tasks #829/#831/#832/#837."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#843 definition of done, relayed via this batch's dispatch brief"
relationships:
  - type: references
    target: architecture-flows-workflow-execution
---

# Workflow Trigger

The `TriggerDef` enum (`crates/buzz-workflow/src/schema.rs:38-71`) is the umbrella
type every workflow definition's trigger holds: `MessagePosted`, `ReactionAdded`,
`DiffPosted`, `Schedule`, or `Webhook`. This node documents that enum and the
dispatch mechanism that decides, for a given fire attempt, whether a definition's
trigger matches. It does not narrate the full run lifecycle a matched trigger starts
— that is `architecture-flows-workflow-execution`'s territory, `references`d below —
and it does not document any one variant's own complete semantics (filter syntax,
cron grammar, webhook authentication details), which belongs to the individual
trigger-type nodes (`message-trigger`, `reaction-trigger`, `schedule-trigger`,
`webhook-trigger` — issues #829/#831/#832/#837), none of which are merged yet.

## Trigger, preconditions, termination

**There is no single generic dispatcher.** Three engine entry points each carry
their own trigger-matching logic against the same five-variant enum, and none of
them delegates to a shared "does this trigger match" function used by all three:

| Entry point | Variants it can ever match | Matching mechanism |
|---|---|---|
| `WorkflowEngine::on_event` (channel event) | `MessagePosted`, `ReactionAdded`, `DiffPosted` | `trigger_matches_event` (kind check) then `should_fire_workflow` (emoji/filter narrowing) |
| `WorkflowEngine::run` (cron loop, 60s tick) | `Schedule` only | Direct pattern match on `TriggerDef::Schedule { cron, interval }`; every other variant falls through a catch-all `_ => continue` |
| `api::bridge::workflow_webhook` (`POST /hooks/{id}`) | `Webhook` only | `matches!(def.trigger, TriggerDef::Webhook)`, checked before the shared secret |

**Preconditions specific to the trigger shape**, enforced by `WorkflowDef::validate()`
at definition-save time, independent of any fire attempt:

- A `Schedule` trigger must specify exactly one of `cron` or `interval` — both
  present or both absent is rejected. A present `cron` expression is syntax-checked;
  a present `interval` is duration-parsed and rejected below 60 seconds, because the
  cron loop itself only ticks once a minute and a shorter interval could never fire
  correctly.
- A step whose action is `SendMessage { reply_in_thread: true, .. }` is rejected
  unless the trigger is `MessagePosted`, `ReactionAdded`, or `DiffPosted` — `Schedule`
  and `Webhook` triggers have no triggering message to reply to, so this combination
  fails at save time rather than silently at run time.

**Termination / outcome, at the trigger-evaluation level only.** Each entry point's
outcome here is binary — the definition's trigger either matches (evaluation
continues toward `create_workflow_run`) or it does not (the candidate workflow is
skipped for this fire attempt). This node stops at that yes/no decision; what happens
once a match proceeds to run creation, step execution, and the run's own terminal
`RunStatus` is `architecture-flows-workflow-execution`'s subject, not this one's.

## Ordered interactions and data movement

**Channel-event path (`on_event`):**

1. For each enabled workflow whose channel matches the stored event, parse its
   definition and call `trigger_matches_event(&def.trigger, kind_u32)`
   (`crates/buzz-workflow/src/lib.rs:379`) — a kind-only check. `MessagePosted`
   matches only `KIND_STREAM_MESSAGE`, `ReactionAdded` only `KIND_REACTION`,
   `DiffPosted` only `KIND_STREAM_MESSAGE_DIFF`; `Schedule` and `Webhook` always
   return `false` here, since neither can ever be satisfied by a channel event.
2. If the kind matches, call `should_fire_workflow(&def, &trigger_ctx, workflow.id)`
   (`crates/buzz-workflow/src/lib.rs:383`), which narrows further: for
   `ReactionAdded` with an `emoji` set, the reaction's actual emoji must match
   exactly; then, for any of the three message-based variants, an optional evalexpr
   `filter` expression is evaluated against the trigger context (no step outputs
   exist yet). A filter-evaluation error is logged and treated as "skip this
   workflow," not as an abort.
3. Only after both checks pass does `on_event` proceed to the owner-authority
   recheck and run creation — out of this node's scope, see *Boundary*.

**Schedule path (`run()`):**

1. Every 60 seconds, for each enabled workflow, match `&def.trigger` directly:
   `Schedule { cron: Some(expr), interval: None }` computes a deterministic
   cron-window instant; `Schedule { cron: None, interval: Some(dur) }` computes an
   interval-bucket instant. Every other pattern — `MessagePosted`, `ReactionAdded`,
   `DiffPosted`, `Webhook`, or a malformed `Schedule` carrying both or neither field
   — falls through the match's catch-all arm and is skipped, with the code's own
   comment noting non-schedule triggers are `on_event`'s job
   (`crates/buzz-workflow/src/lib.rs:598`).
2. `trigger_matches_event` and `should_fire_workflow` are never called on this path;
   the computed instant itself is what feeds the durable at-most-once claim covered
   by `architecture-flows-workflow-execution`.

**Webhook path (`workflow_webhook`):**

1. After resolving the request's tenant and loading the workflow, the handler checks
   `!matches!(def.trigger, TriggerDef::Webhook)` and returns `400 Bad Request` if the
   definition's trigger is anything else (`crates/buzz-relay/src/api/bridge.rs:2036`)
   — before the shared secret is checked, and before any run is created.
2. This is the only trigger-matching step on this path: there is no kind check, no
   filter, and no schedule computation, because the enum carries no additional
   fields for `Webhook` to narrow against.

## Authentication / authorization / trust-boundary crossings

Trigger *matching itself* crosses no additional authentication or trust boundary
beyond what each entry point already performs downstream of a match:

- The channel-event and schedule paths both re-check the workflow owner's current
  channel authority (SEC-006) only *after* their respective trigger match succeeds,
  never as part of the match itself.
- The webhook path's trigger-type check (`Webhook` or reject) runs *before* the
  caller is authenticated by the shared secret — so an unauthenticated caller can
  learn only that a workflow's trigger type is wrong (400) versus some other
  rejection, not that it exists or is misconfigured in some other way. The generic
  404 for tenant/lookup failures is applied earlier still, at community binding.

The full authority-recheck, webhook-secret, SSRF, and community-fence crossings that
happen once a trigger has already matched are `architecture-flows-workflow-execution`'s
subject; this node states only that trigger matching precedes them and adds no
boundary crossing of its own beyond the webhook trigger-type check above.

## Failure, abort, rollback behavior

At the trigger-evaluation level, every failure mode observed is a **skip**, not an
abort of anything already running — there is no run yet for an abort to affect:

- A workflow definition that fails to parse from stored JSON is skipped with a
  logged warning, on both the channel-event and schedule paths.
- A filter-evaluation error inside `should_fire_workflow` is logged and treated as a
  non-match, skipping that workflow for this event.
- A malformed `Schedule` variant (both `cron` and `interval` set, or neither) is
  rejected at definition-save time by `validate()` and can therefore never reach the
  cron loop's match arms in a way that would need runtime handling — the loop's
  catch-all simply never sees a case `validate()` was supposed to prevent.
- A non-`Webhook` trigger on the webhook path returns `400` to the caller; no
  workflow row, run, or side effect is touched.

No trigger-matching step in any of the three paths mutates persisted state — the
first write any path performs is `create_workflow_run`, downstream of a successful
match, which is out of this node's scope.

**Representative verification:**
- `trigger_matches_event_kind_zero_matches_nothing`, `diff_posted_matches_kind_40008_only`,
  `message_posted_does_not_match_kind_40008`
  (`crates/buzz-workflow/src/lib.rs:1513-1546`) — unit tests asserting
  `trigger_matches_event`'s kind-only matching for each variant, including that
  `Schedule` and `Webhook` never match a channel event.

## Scope and omissions

**This node covers** the `TriggerDef` enum as the umbrella trigger type, the fact
that three independent engine entry points each apply their own matching logic
against it rather than sharing one dispatcher, the trigger-shaped preconditions
`WorkflowDef::validate()` enforces, and the failure behavior (always "skip," never
"abort a run") specific to trigger evaluation.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The full run lifecycle once a trigger matches (run creation, step execution, terminal status, the shared executor's own trust-boundary and failure behavior) | `architecture-flows-workflow-execution` |
| `MessagePosted`'s and `DiffPosted`'s own filter-expression grammar and semantics in full | `message-trigger` (#829, not yet drafted) |
| `ReactionAdded`'s own emoji-matching and filter semantics in full | `reaction-trigger` (#831, not yet drafted) |
| `Schedule`'s own cron grammar, interval parsing, and cross-pod claim mechanics in full | `schedule-trigger` (#832, not yet drafted) |
| `Webhook`'s own shared-secret authentication and request-body field mapping in full | `webhook-trigger` (#837, not yet drafted) |
| Workflow *definition* authoring/storage (the `kind:30620` command, JSON round-tripping) | not covered by this node or by `architecture-flows-workflow-execution` |

**Expected but not verified when this node was written:**

- Whether `#829`/`#831`/`#832`/`#837` will each declare a `references` or `part-of`
  edge back to this node once drafted was not checked — this node declares only the
  one `references` edge that already resolves on `origin/launchpad` today.
- Whether `type: architecture` versus `type: capabilities` for this node's family of
  documents will be reconciled once a per-type corpus standard lands is unsettled;
  `AGENTS.md` states per-type standards are still pending across issues #1307-#1351,
  and this node's own `type` choice is recorded as an `INFERENCE`, not a settled
  fact, for exactly that reason.
