---
id: architecture-flows-workflow-execution
type: architecture
status: draft
origin: launchpad
audiences:
  - agent
  - developer
evidence:
  - statement: "This node was authored and checked against repository revision a44cf52fc740ebebbdd671427480d14f0bce0115."
    entry_class: FACT
    evidence:
      - "commit a44cf52fc740ebebbdd671427480d14f0bce0115"
  - statement: "A workflow run can start from exactly three trigger paths: an in-process channel-event hook (message_posted, reaction_added, diff_posted), a 60-second background cron/interval loop (schedule), and an HTTP webhook handler at POST /hooks/{id} (webhook) -- the four TriggerDef variants map 1:1 onto these three code paths, since Schedule covers both cron and interval."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/schema.rs"
      - "crates/buzz-workflow/src/lib.rs"
      - "crates/buzz-relay/src/api/bridge.rs"
  - statement: "The channel-event path is wired from the relay's post-store event handler: for every stored event that is not a workflow-execution kind, not a command kind, not a relay-signed workflow message, and not a gift wrap, the handler spawns WorkflowEngine::on_event(community_id, &stored_event) via tokio::spawn, decoupled from the event's own storage/ack path."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs"
  - statement: "on_event excludes events whose kind falls in the reserved workflow-execution range (46001-46012) before doing any workflow lookup, which is what prevents a workflow's own emitted events from re-triggering workflows and looping."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/lib.rs"
      - "crates/buzz-core/src/kind.rs"
  - statement: "The per-channel enabled-workflow list is read through a 10-second TTL cache keyed (community_id, channel_id); the relay invalidates that same-pod cache entry at the two workflow mutation sites (command upsert, NIP-09 deletion), and the struct's own doc comment states there is deliberately no cross-pod invalidation, so another pod's worst case is a just-deleted workflow firing (or a just-created one missing events) for up to the cache TTL."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/lib.rs"
  - statement: "trigger_matches_event matches MessagePosted/ReactionAdded/DiffPosted definitions against the stored event's kind only; Schedule and Webhook triggers always return false from this function, because they are never fired by a channel event."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/lib.rs"
  - statement: "should_fire_workflow applies each trigger's own optional narrowing after the kind match: an exact emoji match for reaction_added, and an evalexpr filter expression (evaluated against the trigger context, no step outputs yet) for message_posted and diff_posted; a filter evaluation error is treated as a non-match and the workflow is skipped rather than the run failing."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/lib.rs"
  - statement: "The cron/interval path is a WorkflowEngine::run() background loop ticking every 60 seconds; for each active Schedule-triggered workflow it computes a deterministic scheduled_for instant (the cron crate's window-matched boundary, or the interval bucket boundary) identically on every relay pod, so all pods collide on one durable claim row rather than each firing independently."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/lib.rs"
  - statement: "Interval-trigger liveness across restarts is anchored on a durable read (latest_scheduled_workflow_fire) on the first tick after a process bounce, and the loop's own comment states that fires missed during downtime are not replayed, which it calls acceptable for MVP."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/lib.rs"
  - statement: "The webhook path is the POST /hooks/{id} route registered against api::bridge::workflow_webhook; it looks up the workflow, rejects (400) if the definition's trigger is not Webhook, and otherwise authenticates the caller before touching run state."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs"
      - "crates/buzz-relay/src/api/bridge.rs"
  - statement: "WorkflowDef::validate() is the precondition every definition must pass before it can be saved (and therefore before any of the three trigger paths can ever run it): non-empty name, at least one step, step ids unique and matching only ASCII alphanumerics/underscore up to 64 chars, and a Schedule trigger must specify exactly one of cron or interval, with interval rejected below 60 seconds because the cron loop itself only ticks once a minute."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/schema.rs"
  - statement: "Run execution (execute_run and execute_from_step) first acquires a permit from engine.run_semaphore, sized by WorkflowConfig::max_concurrent (default 100); if no permit is free it fails immediately with WorkflowError::CapacityExceeded rather than queuing, and only after acquiring the permit does it write the run's status to Running."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/executor.rs"
      - "crates/buzz-workflow/src/lib.rs"
  - statement: "create_workflow_run inserts a workflow_runs row with status 'pending', current_step 0 and an empty execution_trace before any step runs, scoped to (community_id, id); this is the run's starting state for all three trigger paths."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/workflow.rs"
  - statement: "Within execute_steps, def.steps run strictly in order: for each step the optional if: expression is evaluated first (evalexpr, against trigger fields and prior steps' outputs) and a false result records a 'skipped' trace entry and moves to the next step without dispatching the action; a condition-evaluation error aborts the run."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/executor.rs"
  - statement: "After the condition check, the step's action fields are template-resolved ({{trigger.X}} and {{steps.ID.output.X}} placeholders, with optional truncate(N)/npub filters) against the accumulated trigger context and step_outputs map before dispatch; a template resolution error aborts the run."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/executor.rs"
  - statement: "Each step's dispatch is wrapped in tokio::time::timeout using step.timeout_secs if set, else engine.config.default_timeout_secs (default 300s); a timeout aborts the run with WorkflowError::StepTimeout naming the step id and limit."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/executor.rs"
      - "crates/buzz-workflow/src/lib.rs"
  - statement: "A completed step's JSON output is recorded in a 'completed' trace entry and inserted into step_outputs under the step's own id, making it addressable by later steps' templates and conditions as steps.<id>.output.<field>."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/executor.rs"
  - statement: "build_trigger_context maps a stored channel event into the TriggerContext every step reads: text (content), author (pubkey hex), channel_id, timestamp, emoji (reaction content) and message_id (the reacted-to event's id via its e tag, or the event's own id otherwise); the webhook path instead populates channel_id from the workflow's bound channel and copies the JSON request body's top-level fields into webhook_fields."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/lib.rs"
      - "crates/buzz-relay/src/api/bridge.rs"
  - statement: "SEC-006 fail-closed authority gate: WorkflowEngine::check_owner_authority is re-run immediately before every run-creation door (per-fire in on_event, before the durable schedule claim in run(), and in workflow_webhook before run creation) rather than trusted from save time, because a run executes long after the definition was saved with the owner's *current* standing authority; any lookup error is treated as a denial, never a pass-through."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/lib.rs"
      - "crates/buzz-relay/src/api/bridge.rs"
  - statement: "owner_authority_allows encodes the authority rule as three cases: not an active channel member denies unconditionally; an active member is allowed for an ordinary definition; a definition that requires_elevated_authority (i.e. contains a call_webhook step, which can exfiltrate channel content to an arbitrary external host) is allowed only for owner/admin roles."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/lib.rs"
      - "crates/buzz-workflow/src/schema.rs"
  - statement: "The webhook trigger path binds the request to a community from the HTTP Host header (bind_community) before any tenant-scoped workflow lookup; an unmapped host, a bind failure, and a workflow id that does not exist in that resolved community all return the same generic 404, so a caller cannot distinguish 'wrong tenant' from 'workflow does not exist' -- the code comment states this is deliberate so a caller cannot probe which hosts or workflow ids exist in other tenants."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs"
  - statement: "The webhook handler authenticates the caller with a per-workflow shared secret (checked from the x-webhook-secret header, falling back to a ?secret= query param) before creating any run; a missing stored secret returns 401 telling the caller to re-save the workflow, and a present-but-wrong secret also returns 401 -- the secret only authenticates the caller, so the handler still re-runs check_owner_authority afterward and rejects a disabled or non-Active workflow with the same generic 404 used for a nonexistent one."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs"
      - "crates/buzz-relay/src/webhook_secret.rs"
  - statement: "Every side-effecting action dispatch (dispatch_action) re-acquires and verifies a community write fence (buzz_deletion::acquire_serving_write / .verify() / .protect() / .finish()) immediately before running, because the engine can outlive the request that spawned it; a fence acquisition or verification failure denies the side effect rather than letting a stale run act on a community whose write lease has moved on."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/executor.rs"
  - statement: "SendMessage resolves its target channel with resolve_send_message_channel: a workflow bound to a channel cannot be overridden to a different channel id (a mismatched explicit override is rejected as InvalidDefinition), an unbound workflow may specify an explicit channel override or fall back to the trigger event's own channel, and an unbound workflow with neither is rejected rather than silently posting nowhere."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/executor.rs"
  - statement: "call_webhook is the one action that reaches an operator-supplied external URL, and it is SSRF-guarded end to end: the host is DNS-resolved and any private/reserved-range address is rejected before the request is made, the request client is built per-call and pinned to the already-validated IP (so a second, unpinned resolution inside the HTTP client cannot return a different, unvalidated address -- a DNS-rebinding TOCTOU), the system proxy is disabled, HTTP redirects are disabled (a redirect target is never re-checked), and the response body is read incrementally with a hard 1 MiB (1024*1024 byte) cap rather than buffered whole."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/executor.rs"
  - statement: "delay actions are capped at 270 seconds (WorkflowError::InvalidDefinition rejects anything longer); the cap sits below the 300s default step timeout deliberately, and the action's own comment says a longer wait needs the not-yet-built scheduled-resume pattern (WF-09) instead of sleeping in-process."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/executor.rs"
  - statement: "SendDm and SetChannelTopic are defined in the schema but dispatch_action returns WorkflowError::NotImplemented for both immediately, without attempting any side effect -- authoring either action into a workflow makes that step, and therefore that run, always fail."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/executor.rs"
  - statement: "RequestApproval returns StepResult::Suspended with a generated token, but no approval record is persisted to the database and no kind:46010 (workflow_approval_requested) event is emitted -- the dispatch code's own comment marks this as pending WF-08 -- and finalize_run treats any run that suspends this way as Failed, logging a warning and recording error code approval_not_supported rather than leaving it queryable as WaitingApproval."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/executor.rs"
      - "crates/buzz-workflow/src/lib.rs"
  - statement: "On any step-level error -- condition evaluation, template resolution, action dispatch, or step timeout -- execute_steps returns Err((WorkflowError, PartialProgress)) carrying the failing step's index and the trace of every step completed or skipped up to that point; steps that already produced a side effect (e.g. a message already sent) are not undone, so a mid-run failure leaves any prior side effects standing and only the run's own status/trace reflects the failure."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/executor.rs"
      - "crates/buzz-workflow/src/error.rs"
  - statement: "finalize_run is the single place that maps an executor result to a persisted RunStatus, called by every execution path (event-triggered, cron, webhook, approval-resume) instead of each path duplicating the mapping; on success it writes Completed (or Failed with code approval_not_supported for the unimplemented-approval case above), and on error it writes Failed with the WorkflowError's stable code() and the accumulated partial trace."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/lib.rs"
  - statement: "RunStatus's six values (Pending, Running, WaitingApproval, Completed, Failed, Cancelled) are the full set of states a run's row can occupy; of these, only Completed and Failed are states this document's three trigger paths actually reach on their own, because WaitingApproval is unreachable (RequestApproval is mapped to Failed, not WaitingApproval, per the entry above) and Cancelled is not set by any code path covered here."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/workflow.rs"
      - "crates/buzz-workflow/src/lib.rs"
  - statement: "Because on_event is spawned via tokio::spawn from the relay's post-store hook rather than awaited inline, a workflow run's failure -- of any kind, including an authority denial or a step error -- has no path back to the triggering event: the event that fired the trigger is already durably stored and acknowledged before workflow execution even begins, so this flow never rolls back or blocks on the event it reacts to."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs"
      - "crates/buzz-workflow/src/lib.rs"
  - statement: "Kinds 46001-46012 are reserved in the kind registry as 'workflow execution events' (triggered, per-step started/completed/failed, workflow completed/failed/cancelled, approval requested/granted/denied) and is_workflow_execution_kind checks a stored event's kind against exactly that range, but no source file in buzz-workflow constructs or publishes an event of any of these kinds -- the only side-effecting event this engine actually emits today is the channel message published by the SendMessage action through ActionSink::send_message. Verified by reading every dispatch_action arm and by finding no EventBuilder::new(Kind::Custom(..)) construction for this range anywhere in the crate outside its own trigger-matching unit tests."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
      - "crates/buzz-workflow/src/executor.rs"
      - "crates/buzz-workflow/src/action_sink.rs"
      - "crates/buzz-workflow/src/lib.rs"
  - statement: "workflow_error_codes_are_stable_and_separate_from_diagnostics is a unit test asserting WorkflowError::code() returns a stable, secret-free classification (e.g. 'step_timeout', 'webhook_failed', 'action_not_implemented') distinct from the Display diagnostic text, which is the string finalize_run persists as the run's error_code -- representative verification for the failure-classification claims above."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/error.rs"
  - statement: "workflow_trigger_is_community_confined and approval_token_is_community_confined are integration tests in buzz-test-client asserting a workflow defined in one community cannot be fired, and an approval token cannot be resolved, from a different community sharing the same channel/workflow UUID -- representative verification for the tenant trust-boundary crossing, though both are marked #[ignore] and require a live multi-tenant test harness rather than running in the default unit suite."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/conformance_multitenant.rs"
  - statement: "send_message_rejects_cross_channel_override_for_bound_workflow is a unit test asserting resolve_send_message_channel rejects an explicit channel override that does not match a workflow's bound channel -- representative verification for the SendMessage channel-confinement claim above."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/executor.rs"
  - statement: "This node's category tail (issue #688's own definition of done) requires stating trigger/preconditions/termination, ordered interactions and data movement, auth/trust-boundary crossings, and failure/abort/rollback behavior with links to representative verification -- which is why this document is organized around those four sections rather than a general architecture narrative."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#688 definition of done, category: flows"
---

# Flow: Workflow Execution

How a Buzz workflow definition goes from a matching trigger to a terminal run state:
who may cause it to run, what moves through it, where trust boundaries are crossed,
and what happens when a step fails partway through.

**Scope.** This node covers `crates/buzz-workflow`'s three trigger paths
(`WorkflowEngine::on_event`, `WorkflowEngine::run`'s cron loop, and the
`POST /hooks/{id}` webhook handler in `buzz-relay`) and the shared sequential
executor (`crates/buzz-workflow/src/executor.rs`) they all call into. It does not
cover workflow *definition* authoring/validation as its own concern beyond the
preconditions a definition must satisfy to run at all (see `WorkflowDef::validate`),
and it does not cover the approval-gate *resume* flow, because that capability
(WF-08) is not implemented yet — see *Scope and omissions*.

**No `relationships`.** No other node in the merged corpus at the recorded revision
describes a target this flow would point at; a `relationships[].target` naming an id
nothing carries is a hard validation error, so none is declared. This is a fact about
the corpus's current contents, not a claim that nothing here is linkable — see
`launchpad/docs/corpus/AGENTS.md`'s warning about that exact false-justification trap.

## Trigger, preconditions, termination

**Trigger — three independent paths, one shared executor:**

| Path | Fires on | Entry point |
|---|---|---|
| Channel event | A stored message, reaction, or diff event whose kind matches the definition's trigger | `WorkflowEngine::on_event` |
| Schedule | A 60-second cron-loop tick whose cron/interval boundary has arrived | `WorkflowEngine::run` |
| Webhook | An authenticated `POST /hooks/{id}` request | `api::bridge::workflow_webhook` |

**Preconditions common to all three paths**, enforced before a run is ever created:

1. The workflow's stored `definition` must parse back into a `WorkflowDef` — a
   parse failure logs a warning and the workflow is skipped, not run.
2. The definition must be `enabled`, and (webhook path only) the workflow row's own
   `status` must be `Active` — a disabled or non-Active workflow is treated exactly
   like a nonexistent one.
3. The definition must have passed `WorkflowDef::validate()` at save time: non-empty
   name, at least one step, unique step ids restricted to
   `[A-Za-z0-9_]{1,64}`, and — for a `Schedule` trigger — exactly one of `cron` or
   `interval`, with `interval` rejected below 60 seconds (the cron loop itself only
   ticks once a minute, so anything shorter could never fire correctly).
4. The workflow's owner must currently hold sufficient channel authority — see
   *Trust-boundary crossings* below. This is re-checked at fire time, not trusted
   from save time.

**Termination / outcome.** A run's `workflow_runs` row starts `Pending`
(`current_step = 0`, empty trace) and, once a concurrency permit is acquired, moves
to `Running`. From there `finalize_run` is the single place that decides the terminal
state: `Completed` on a clean pass through all steps, or `Failed` — carrying a stable
error code and the trace accumulated up to the point of failure — on any error,
including a not-yet-implemented approval suspension (see *Failure, abort, rollback*).
`WaitingApproval` and `Cancelled` exist in the `RunStatus` enum but neither is
actually reached by the paths this document covers.

## Ordered interactions and data/state movement

**Channel-event path:**

1. The relay's post-store event handler spawns `on_event(community_id, &stored_event)`
   for any stored event that is not a workflow-execution kind, command kind,
   relay-signed workflow message, or gift wrap — asynchronously, decoupled from the
   event's own storage/ack path.
2. `on_event` reads the channel's enabled-workflow list (10s TTL cache keyed
   `(community_id, channel_id)`), skips entirely if empty, then builds a
   `TriggerContext` from the event: `text` (content), `author` (pubkey hex),
   `channel_id`, `timestamp`, `emoji` (reaction content), and `message_id` (the
   reacted-to event's id via its `e` tag, or the event's own id otherwise).
3. For each candidate workflow: parse its definition, check `trigger_matches_event`
   (kind match) then `should_fire_workflow` (optional emoji/filter narrowing), then
   re-check owner authority (SEC-006), then `create_workflow_run` and
   `tokio::spawn` the executor.

**Schedule path:**

1. Every 60s, `run()` loads all enabled workflows across all communities and, per
   `Schedule`-triggered workflow, computes a deterministic `scheduled_for` instant —
   identical across relay pods — from the cron expression's window match or the
   interval bucket boundary.
2. Owner authority is re-checked *before* the durable claim (placing it after would
   let a revoked owner's workflow consume the at-most-once fire slot and deny a
   future re-enable).
3. `claim_scheduled_workflow_fire(community_id, workflow_id, scheduled_for)` is the
   durable at-most-once boundary across pods and restarts; the losing pod (or an
   already-fired instant) skips before any run creation or side effect.
4. On a won claim: build a minimal `TriggerContext` (channel id + timestamp only),
   `create_workflow_run`, best-effort link the claim row to the run id for
   ops/audit forensics, and spawn the executor.

**Webhook path:**

1. `POST /hooks/{id}` resolves the request's community from its `Host` header
   (`bind_community`) before any workflow lookup, then loads the workflow scoped to
   that community and rejects (400) if its trigger is not `Webhook`.
2. The shared secret is verified (header preferred, query param fallback).
3. The workflow's enabled/`Active` state and owner authority are re-checked.
4. `create_workflow_run` records the request's optional JSON body fields into
   `TriggerContext.webhook_fields`, keyed by the body's top-level JSON keys; the
   handler responds `202 Accepted` with the run id immediately and spawns
   `execute_from_step` asynchronously — the HTTP response does not wait for the run
   to finish.

**Shared step loop (`execute_steps`), all three paths converge here:**

For each step, in `def.steps` order, starting from `start_index` (0 for a fresh run,
the resume point for an approval-resumed one — resume is otherwise out of scope, see
*Scope and omissions*):

1. Evaluate the optional `if:` expression (evalexpr) against the trigger context and
   the accumulated `step_outputs` map. `false` records a `"skipped"` trace entry and
   moves on; an evaluation error aborts the run.
2. Resolve `{{trigger.X}}` and `{{steps.ID.output.X}}` template placeholders in the
   action's fields (with optional `truncate(N)` / `npub` filters); a resolution
   error aborts the run.
3. Dispatch the resolved action under `tokio::time::timeout` (the step's own
   `timeout_secs`, else the engine's `default_timeout_secs`, default 300s); a
   timeout aborts the run with the step id and limit named in the error.
4. On success, the action's JSON output is recorded in a `"completed"` trace entry
   and inserted into `step_outputs` under the step's own id, becoming addressable
   by later steps.

## Trust-boundary crossings

- **Community/tenant fence.** The webhook path derives the serving community from
  the request's `Host` header before any workflow lookup; an unmapped host, a bind
  failure, and a workflow id absent from that community all return the same generic
  404, so a caller cannot distinguish "wrong tenant" from "does not exist" — a
  deliberate anti-probing choice. `dispatch_action` re-acquires and verifies a
  community write fence immediately before every side effect, because the engine
  instance can outlive the HTTP request that originally spawned it; a fence failure
  denies the side effect.
- **Owner authority (SEC-006), fail-closed.** A run executes with its owner's
  *current* channel authority, re-checked immediately before every run-creation
  door (not trusted from save time): not an active channel member denies
  unconditionally; an active member may run an ordinary definition; a definition
  containing `call_webhook` (which can exfiltrate channel content to an arbitrary
  external destination) additionally requires the owner/admin role. Any authority
  lookup error is treated as a denial.
- **Webhook shared-secret authentication.** The webhook path authenticates the
  *caller* via a per-workflow secret (header or query param) — a missing configured
  secret or a wrong one both return 401 — but this is layered under, not instead
  of, the owner-authority and enabled/`Active` checks above, because the secret
  proves who is calling, not that the run is still authorized to happen.
- **Outbound webhook SSRF.** `call_webhook` is the one action that reaches an
  operator-supplied external URL. The target host is DNS-resolved and any
  private/reserved-range address is rejected before the request is made; the
  HTTP client is built per-call and pinned to the already-validated IP (defeating a
  DNS-rebinding TOCTOU against a second, unpinned resolution inside the client);
  the system proxy and HTTP redirects are both disabled; and the response body is
  read incrementally with a hard 1 MiB cap.
- **Channel confinement for `send_message`.** A workflow bound to a channel cannot
  be redirected to a different channel by a step's `channel` override — a mismatch
  is rejected as an invalid definition rather than silently posted elsewhere.

## Failure, abort, rollback behavior

- **No queuing under load.** Both `execute_run` and `execute_from_step` acquire a
  permit from a semaphore sized by `WorkflowConfig::max_concurrent` (default 100)
  before doing anything else; if none is free, the call fails immediately with
  `CapacityExceeded` rather than waiting.
- **Mid-run failure leaves prior side effects standing.** A step-level error
  (condition evaluation, template resolution, dispatch, or timeout) aborts the
  *remaining* steps only — `execute_steps` returns the failing step's index and the
  trace of everything completed or skipped up to that point, but does **not** undo
  an already-sent message or any other side effect a prior step produced. There is
  no compensating/rollback action for any `ActionDef` variant.
- **The triggering event is never affected.** Because the channel-event path is
  spawned asynchronously from the relay's post-store hook, the event that caused
  the trigger is already durably stored (and, on the HTTP submit path, already
  acknowledged) before workflow execution begins — a workflow failure of any kind
  has no path back to roll back or block on that event.
- **Two actions are permanently unimplemented today.** `SendDm` and
  `SetChannelTopic` always return `NotImplemented` the moment they are dispatched —
  authoring either into a workflow makes that step, and therefore that run, always
  fail.
- **Approval requests fail closed, not open.** `RequestApproval` returns a
  suspended result with a token, but no approval record is persisted and no
  `kind:46010` event is emitted (WF-08 is not built); `finalize_run` maps this case
  to `Failed` with error code `approval_not_supported` rather than leaving the run
  queryable as `WaitingApproval`. A workflow author cannot currently rely on this
  step doing anything but failing the run.
- **Reserved telemetry kinds are not emitted.** Kinds 46001–46012 are reserved in
  the kind registry for per-run/per-step workflow-execution telemetry, but nothing
  in this engine constructs or publishes an event of any of them; the only
  side-effecting event actually emitted by a run is the channel message from a
  `SendMessage` step. A consumer expecting real-time Nostr events for run/step
  progress will not observe any — the only durable record is the `workflow_runs`
  row's `status`/`current_step`/`execution_trace` columns.
- **Representative verification:**
  - `workflow_error_codes_are_stable_and_separate_from_diagnostics`
    (`crates/buzz-workflow/src/error.rs`) — the stable, secret-free error
    classification `finalize_run` persists as `error_code`.
  - `send_message_rejects_cross_channel_override_for_bound_workflow`
    (`crates/buzz-workflow/src/executor.rs`) — the channel-confinement claim above.
  - `workflow_trigger_is_community_confined` and
    `approval_token_is_community_confined`
    (`crates/buzz-test-client/tests/conformance_multitenant.rs`) — the tenant
    trust-boundary claim above; both are `#[ignore]`d integration tests requiring a
    live multi-tenant harness, not part of the default unit-test run.

## Scope and omissions

**Not covered here, and owned elsewhere:**

- Workflow *definition* authoring/validation as its own subject (the `kind:30620`
  command, YAML/JSON round-tripping, per-field schema) beyond the run-time
  preconditions in *Trigger, preconditions, termination*.
- The approval-gate *resume* flow (`execute_from_step` called after a human grants
  an approval) — moot today, since no path currently produces a resolvable
  approval record (see *Failure, abort, rollback*). This is WF-08's own scope.
- The `kind:30620` definition-save path's own authority checks (as opposed to the
  run-creation-time recheck this document covers).

**Expected but not verified when this node was written:**

- Whether any *other* consumer (desktop, mobile, CLI) currently depends on
  observing `kind:46001`–`46012` events was not checked; this document only
  establishes that the relay-side engine does not emit them.
- Behavior under a relay restart mid-run (a `Running` row whose spawned task was
  killed) was not traced — no code path that sweeps or reconciles stuck `Running`
  rows was located, but its absence was not exhaustively confirmed across the full
  relay startup sequence.
