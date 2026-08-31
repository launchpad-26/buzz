---
id: capabilities-workflows-reaction-action
type: capabilities
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
  - statement: "ActionDef::AddReaction is a workflow step whose only field is `emoji: String`, tagged `action: add_reaction` in YAML/JSON, documented as adding an emoji reaction to the triggering message."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/schema.rs:121-125"
  - statement: "buzz-workflow's own Cargo.toml declares `reqwest` as an optional dependency gated behind a `reqwest` feature that is off by default."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/Cargo.toml:28-31"
  - statement: "buzz-relay's Cargo.toml depends on buzz-workflow with `features = [\"reqwest\"]` set unconditionally, so the real relay binary always compiles buzz-workflow's reqwest-feature code path in."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/Cargo.toml:65"
  - statement: "The AddReaction dispatch arm checks that trigger_ctx.message_id is non-empty (returning WorkflowError::InvalidDefinition if it is), then, only when the reqwest feature is compiled in, calls add_reaction_impl and returns its result as StepResult::Completed; when the reqwest feature is absent it instead logs a warning and completes with a `{\"added\": false, \"skipped\": true}` placeholder, without attempting any HTTP call."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/executor.rs:655-680"
  - statement: "add_reaction_impl's own doc comment states it POSTs `{\"emoji\": emoji}` to `POST /api/messages/{message_id}/reactions`; the function builds that URL against a `BUZZ_RELAY_BASE_URL` environment variable defaulting to `http://localhost:3000`, attaches `Authorization: Bearer <BUZZ_API_TOKEN>` if that env var is set, else `X-Pubkey: <BUZZ_RELAY_PUBKEY>` if that one is set, else neither header, sends the request through a shared reqwest client built once with a fixed 10-second timeout, and maps any non-success HTTP status to WorkflowError::WebhookError carrying the response body."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/executor.rs:955-1014"
  - statement: "crates/buzz-relay/src/router.rs's complete HTTP route table (the api_router block registering every non-WebSocket, non-media, non-admin HTTP path the relay serves) contains no path matching `/api/messages/{id}/reactions` or any reactions-specific route; no `crates/buzz-relay/src/api/messages.rs` module or equivalent exists either."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs:62-143"
  - statement: "executor.rs's own module-level doc comment states: 'Action dispatch uses placeholder implementations that log intent. Real event emission is wired in WF-07/08 (relay integration).'"
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/executor.rs:9-10"
  - statement: "The product's own human/agent-facing path for adding a reaction (buzz-cli's `reactions add` subcommand) builds and signs a NIP-25 kind:7 reaction event with buzz_sdk::build_reaction and submits it through the client's normal signed-event submission path, not through any messages/reactions REST route."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/commands/reactions.rs:9-30"
  - statement: "Within the shared template-resolution step that runs before every action dispatches, AddReaction's `emoji` field is resolved for `{{trigger.X}}` / `{{steps.ID.output.X}}` placeholders the same way every other action's string fields are, and a resolution error aborts the run before AddReaction's own dispatch code executes."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/executor.rs:433"
  - statement: "build_trigger_context populates TriggerContext.message_id only for channel-event triggers: for a non-reaction event it is the event's own id; for a reaction (kind:7) event it is the *target* message's id taken from the last `e` tag holding a 64-char hex value, falling back to the reaction event's own id if no such tag is found — so an add_reaction step chained off a reaction_added trigger reacts to the same message already reacted to, not to the incoming reaction event."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/lib.rs:942-988"
  - statement: "The schedule trigger path builds its TriggerContext with only channel_id and timestamp set and `..Default::default()` for the rest, leaving message_id as an empty string."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/lib.rs:651-655"
  - statement: "The webhook trigger path builds its TriggerContext with only channel_id set from the workflow's bound channel and `..Default::default()` for the rest (webhook_fields is populated afterward from the request body), leaving message_id as an empty string."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs:2078-2084"
  - statement: "WorkflowDef::validate() (the full precondition check every definition must pass before any trigger path can run it) contains no rule pairing the add_reaction action with a message-based trigger, unlike its explicit rule rejecting SendMessage's reply_in_thread on a non-message trigger (schedule/webhook) at definition time; an add_reaction step on a schedule- or webhook-triggered workflow therefore passes validation and fails only at run time."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/schema.rs:173-278"
      - "crates/buzz-workflow/src/schema.rs:219-243"
  - statement: "WorkflowError::code() maps InvalidDefinition to the stable string \"invalid_definition\" and WebhookError to \"webhook_failed\"; AddReaction's own HTTP-failure path reuses the WebhookError variant (and therefore the \"webhook_failed\" code), the same code CallWebhook failures produce, so a run's persisted error_code alone cannot distinguish an AddReaction failure from a CallWebhook failure — only the execution_trace's failing step id can."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/error.rs:73"
      - "crates/buzz-workflow/src/error.rs:77"
  - statement: "No unit or integration test in crates/buzz-workflow exercises add_reaction_impl's HTTP call or asserts the \"AddReaction: no trigger.message_id available\" error path; crates/buzz-workflow/Cargo.toml declares no HTTP-mocking dev-dependency. The only tests referencing AddReaction confirm its YAML/JSON shape round-trips and that it parses into the correct enum variant, not that dispatch behaves as this node describes."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/schema.rs:395"
      - "crates/buzz-workflow/src/schema.rs:412-415"
      - "crates/buzz-workflow/Cargo.toml"
      - "crates/buzz-workflow/src/executor.rs"
  - statement: "VISION_PROJECTS.md's own Status table marks 'Workflow engine (triggers, traces, conditional logic)' as shipped, without naming any individual action type's own functional status."
    entry_class: FACT
    evidence:
      - "VISION_PROJECTS.md:249"
  - statement: "Issue #830's own Definition of Done requires this node to state trigger/preconditions/termination, list ordered interactions and data/state movement, identify authentication/authorization/trust-boundary crossings where relevant, and document failure/abort/rollback behavior with links to representative verification — the reason this node is organized around those sections rather than a general capability narrative."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#830 definition of done"
  - statement: "Issue #831 ('task: document capabilities/workflows/reaction-trigger.md') is the sibling task in Feature #613 covering the reaction_added trigger — the opposite direction from this node's add_reaction action — and was not opened for its own body text while drafting this node."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#613 child issue list (gh issue list --search parent:613)"
  - statement: "At the recorded revision, the corpus tree on origin/launchpad carries a merged, active node at launchpad/docs/corpus/architecture/flows/workflow-execution.md (id architecture-flows-workflow-execution) documenting the shared workflow trigger paths and executor this node's action participates in, and a merged, active template node at launchpad/docs/corpus/templates/capability.md (id corpus-template-capability); both are valid relationships targets."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/flows/workflow-execution.md"
      - "launchpad/docs/corpus/templates/capability.md"
relationships:
  - type: references
    target: architecture-flows-workflow-execution
  - type: implements
    target: corpus-template-capability
---

# Workflow reaction action: capability

A Buzz workflow step type — `action: add_reaction` — that lets an automated
workflow react with an emoji to the message that triggered its run, the same way a
human or agent reacting manually would, without a human present to click the emoji
themselves. It exists as one of seven action types (`send_message`, `send_dm`,
`set_channel_topic`, `add_reaction`, `call_webhook`, `request_approval`, `delay`) a
workflow step may perform after its trigger fires and any `if:` condition passes.

## Maturity

**Recognized and schema-valid; broken end to end in the real relay build.**
`add_reaction` parses, round-trips through YAML/JSON, and passes
`WorkflowDef::validate()` cleanly as part of the "Workflow engine" capability
VISION_PROJECTS.md's own Status table marks shipped. But its actual dispatch code
targets `POST {BUZZ_RELAY_BASE_URL}/api/messages/{message_id}/reactions`, and that
route does not exist anywhere in the relay's HTTP route table — confirmed by reading
the complete `api_router` registration in `router.rs`, not inferred from its absence
from documentation. `buzz-relay`'s own `Cargo.toml` unconditionally turns on the
`reqwest` feature that makes this HTTP call path live, so this is not a
build-configuration escape hatch: every deployed relay compiles the code path that
will make this doomed request. `executor.rs`'s own module doc comment says outright
that action dispatch is placeholder code pending relay integration work
(WF-07/08). Reinforcing that this was never a real endpoint rather than one removed
later: the product's actual reaction-adding path (`buzz-cli`'s `reactions add`)
publishes a signed NIP-25 `kind:7` event through the normal event-submission path —
the same Nostr-first pattern every other Buzz feature uses — not a
messages-and-reactions REST route.

## Trigger, preconditions, termination

**Trigger.** `add_reaction` does not itself trigger a workflow; it executes as one
step inside a run already dispatched by one of the three trigger paths
`architecture-flows-workflow-execution` describes (channel event, schedule,
webhook), after the shared executor's per-step `if:` check passes.

**Preconditions, checked at dispatch time, not definition time:**

1. `trigger_ctx.message_id` must be non-empty. Only the three channel-event
   triggers (`message_posted`, `reaction_added`, `diff_posted`) ever populate it,
   via `build_trigger_context`; the schedule path and the webhook path each
   construct their `TriggerContext` with the rest of the struct left at its
   `Default`, so `message_id` is an empty string on both. An `add_reaction` step on
   a schedule- or webhook-triggered workflow therefore always fails at run time with
   `WorkflowError::InvalidDefinition("AddReaction: no trigger.message_id
   available")`. Unlike `SendMessage`'s `reply_in_thread` field — which
   `WorkflowDef::validate()` explicitly rejects at *save* time for a non-message
   trigger — no equivalent check exists for `add_reaction`; the full `validate()`
   body has no rule pairing this action with a message-capable trigger, so this
   failure mode surfaces only by running the workflow, never by saving or
   validating its definition.
2. The `emoji` field must resolve its template placeholders successfully; a
   resolution error aborts the run before `add_reaction`'s own dispatch code runs.
3. When the trigger is `reaction_added`, `message_id` is the *target* message being
   reacted to (from the triggering reaction event's `e` tag), not the incoming
   reaction event itself — so an `add_reaction` step chained after a
   `reaction_added` trigger reacts again to the same message a human or agent
   already reacted to.

**Termination/outcome.** Same terminal states as any step in the shared executor:
`Completed`, with the action's JSON output folded into `step_outputs`, or the
run-aborting `Failed`. On a (hypothetical, currently unreachable) successful HTTP
response, `Completed`'s output is `{"added": true, "status": <u16>, "response":
<relay body>}`. When the `reqwest` feature is not compiled in at all, the step
always "completes" with `{"added": false, "skipped": true}` — a silent no-op rather
than a visible failure, and indistinguishable from a real success by run status
alone.

## Ordered interactions and data/state movement

1. The executor's `if:` check passes; `emoji`'s template placeholders are resolved.
2. `trigger_ctx.message_id` is checked for emptiness; empty aborts the run with
   `InvalidDefinition` before anything else happens.
3. If the `reqwest` feature is compiled in (always true for `buzz-relay`'s own
   build), `add_reaction_impl` builds `POST {BUZZ_RELAY_BASE_URL}/api/messages/
   {message_id}/reactions` (base URL defaults to `http://localhost:3000`), attaches
   an `Authorization` bearer token or `X-Pubkey` header from the *process
   environment* if either is set, and sends `{"emoji": emoji}` as the JSON body
   through a shared client with a fixed 10-second timeout.
4. The relay's router has no handler registered for that path, so the request
   cannot succeed against `buzz-relay` itself; any non-success status is wrapped as
   `WorkflowError::WebhookError` carrying the response body.
5. If the `reqwest` feature is absent, steps 3-4 never happen — the step
   short-circuits straight to the skip placeholder.
6. On the success branch this dispatch can never actually reach against
   `buzz-relay`'s own router, the JSON response would be folded into
   `{"added": true, "status", "response"}` and recorded into
   `step_outputs.<step_id>.output`, addressable by later steps' templates and
   conditions — the same mechanism every other action's output uses.

## Trust-boundary crossings

Unlike `call_webhook`, the target host here is not operator-supplied through the
workflow definition — it is `BUZZ_RELAY_BASE_URL`, an environment variable
belonging to the relay process itself — so none of `call_webhook`'s SSRF guarding
(DNS pinning, private-range rejection, redirect/proxy disablement) applies or is
needed the same way. The optional bearer token / pubkey header is read from that
same process environment, not from the workflow definition or trigger context, so a
workflow author cannot control or exfiltrate it through `add_reaction`'s own
`emoji` field. `add_reaction_impl` also never threads a community id through the
request at all — it authenticates, at best, with a relay-wide environment
credential rather than the workflow owner's own identity — unlike `SendMessage`,
whose dispatch goes through `engine.action_sink()?.send_message(community_id, ...)`
and the same community write-fence and owner-authority checks
`architecture-flows-workflow-execution` documents for every other action.

## Failure, abort, rollback behavior

- A missing `message_id` aborts the run immediately with
  `WorkflowError::InvalidDefinition` (`error_code: "invalid_definition"`), before
  any HTTP call is attempted.
- An HTTP-level failure — which, against `buzz-relay`'s own router, is the only
  outcome this dispatch can reach today — is wrapped as `WorkflowError::WebhookError`
  (`error_code: "webhook_failed"`), the identical code `call_webhook` failures also
  produce; a run's persisted `error_code` alone cannot distinguish an
  `add_reaction` failure from a `call_webhook` failure, only the run's
  `execution_trace` step id can.
- Like every other action, an `add_reaction` failure aborts only the *remaining*
  steps of the run; nothing rolls back any side effect an earlier step already
  produced — the same executor and the same `execute_steps` error propagation
  `architecture-flows-workflow-execution` documents apply here unmodified.
- When the `reqwest` feature is absent, there is no failure signal at all: the run
  reports `Completed` with a silent `skipped: true` placeholder, which is
  indistinguishable from a genuine success by run status alone.
- **Representative verification: none exists.** No unit or integration test in
  `crates/buzz-workflow` exercises `add_reaction_impl`'s HTTP call or the
  message-id-empty error path, and the crate declares no HTTP-mocking
  dev-dependency to make such a test possible today. The only tests touching
  `AddReaction` confirm its YAML/JSON shape parses into the correct enum variant —
  they do not exercise dispatch.

## Boundary

This node does not describe:
- the shared workflow trigger paths, executor step loop, or concurrency model — see
  `architecture-flows-workflow-execution`, which this node `references` rather than
  restates.
- the `reaction_added` *trigger* (starting a workflow because a reaction was
  posted) — the opposite direction, owned by sibling issue #831's own capability
  node, not yet drafted at this revision.
- how a human or agent adds a reaction outside a workflow (`buzz-cli`'s
  `reactions add`, publishing a signed `kind:7` event) — cited above only as
  contrasting evidence for the Maturity claim, not documented here as its own
  capability.
- every other workflow action type (`send_message`, `send_dm`,
  `set_channel_topic`, `call_webhook`, `request_approval`, `delay`) — each is its
  own sibling issue in Feature #613.
- fixing the broken HTTP target. That is a product-code change with its own
  implementation issue to own it, not something this documentation task decides or
  performs.

## Relationships

- `references`: `architecture-flows-workflow-execution` — the shared trigger paths
  and executor this action's step participates in, cited rather than restated.
- `implements`: `corpus-template-capability` — this node is a `capabilities`-typed
  instance built from that template's required sections.

## Scope and omissions

**This node covers** the `add_reaction` workflow action step: its schema shape,
its run-time-only preconditions (and the definition-time check `reply_in_thread`
has that `add_reaction` lacks), its ordered dispatch interactions, why none of
`call_webhook`'s SSRF guarding applies to its own HTTP call, its failure/rollback
behavior, and — as its central, directly-verified finding — that its HTTP target
does not exist in the relay's own route table, so the action cannot succeed against
a real deployment as currently implemented.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The `reaction_added` trigger (starting a workflow from an incoming reaction) | #831 |
| The shared workflow executor, trigger paths, and concurrency model | `architecture-flows-workflow-execution` |
| The product-facing way a human/agent adds a reaction outside a workflow | not yet a corpus node at this revision |
| Every other workflow action type (`send_message`, `send_dm`, `set_channel_topic`, `call_webhook`, `request_approval`, `delay`) | their own sibling issues in Feature #613 |
| Fixing the broken HTTP target | a product-code issue, not this documentation task |

**Expected but not verified when this node was written:**
- Whether `/api/messages/{message_id}/reactions` was ever implemented and later
  removed, or was never implemented at all, was not traced through git history —
  only its current absence from `router.rs` was confirmed directly.
- What HTTP status a request to an unmatched path actually returns from this
  relay's configured axum stack was not observed against a running relay; this
  node establishes only that no handler is registered for the path, not the exact
  failure response `add_reaction_impl` would receive.
- Whether any deployment points `BUZZ_RELAY_BASE_URL` at a different service that
  does implement this route was not checked; this node establishes only that
  `buzz-relay`'s own router — the service most deployments and the unset default
  (`http://localhost:3000`) would resolve to — has no such handler.
