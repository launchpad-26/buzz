---
id: capabilities-workflows-workflow
type: capabilities
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 131b02f989684117d9ab1dd426f1673fa638e523 on the launchpad branch."
    entry_class: FACT
    evidence:
      - "commit 131b02f989684117d9ab1dd426f1673fa638e523"
  - statement: "buzz-workflow's own crate-level doc comment describes it as 'Workflow engine for Buzz' providing 'Channel-scoped automations with sequential execution, variable substitution, conditional logic, and execution traces', and its Cargo package description is 'YAML-as-code workflow engine for Buzz'."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/lib.rs:1-10"
      - "crates/buzz-workflow/Cargo.toml:1-8"
  - statement: "A workflow definition (WorkflowDef) is authored in YAML and stored as canonical JSON, and is composed of exactly one trigger (TriggerDef: message_posted, reaction_added, diff_posted, or schedule) and an ordered list of steps (Step), each step wrapping one ActionDef with an optional if condition -- the trigger-conditions-actions shape this capability is named for."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/schema.rs:12-26"
      - "crates/buzz-workflow/src/schema.rs:35-56"
  - statement: "Root VISION_PROJECTS.md's Capability/Status table marks 'Workflow engine (triggers, traces, conditional logic)' as 'Ships today', the same product-level unit this node documents."
    entry_class: FACT
    evidence:
      - "VISION_PROJECTS.md:250"
  - statement: "A workflow run can be started from three independent trigger paths -- an in-process channel-event hook, a 60-second cron/interval background loop, and an authenticated POST /hooks/{id} webhook -- all converging on one shared sequential executor (execute_steps) that evaluates each step's optional condition, resolves template placeholders, dispatches the action under a timeout, and records the result in a per-run execution trace."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/lib.rs"
      - "crates/buzz-workflow/src/executor.rs"
      - "crates/buzz-relay/src/router.rs:132"
  - statement: "buzz-relay's router registers POST /hooks/{id} against api::bridge::workflow_webhook as the webhook trigger path, alongside the relay's other HTTP surfaces, confirming the webhook trigger is a real, routed endpoint rather than a schema-only definition."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs:132"
  - statement: "architecture-flows-workflow-execution is a merged corpus node documenting this capability's run-time engine in full detail -- the three trigger paths, the shared executor loop, trust-boundary crossings (community fence, owner authority, webhook secret, outbound SSRF guard), and failure/abort behavior -- and this capability node references it rather than restating its content."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/flows/workflow-execution.md"
  - statement: "architecture-containers-relay is a merged corpus node stating that buzz-relay's AppState holds a direct handle to buzz-workflow's WorkflowEngine and is the only crate that orchestrates it, alongside buzz-db, buzz-auth, buzz-pubsub, buzz-search and buzz-audit, which subsystem crates never call directly."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/containers/relay.md"
  - statement: "buzz-cli exposes a Workflows subcommand group ('Create, trigger, and manage workflows') implemented in crates/buzz-cli/src/commands/workflows.rs, giving an agent or human a command-line surface onto this capability distinct from the webhook and channel-event trigger paths."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/lib.rs:201-203"
      - "crates/buzz-cli/src/commands/workflows.rs"
  - statement: "Event kinds 46001 through 46012 are reserved in the kind registry as workflow-execution telemetry (triggered, per-step started/completed/failed, workflow completed/failed/cancelled, approval requested/granted/denied), naming the intended shape of this capability's observable event surface."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs:564"
      - "crates/buzz-core/src/kind.rs:582"
      - "crates/buzz-core/src/kind.rs:787-789"
  - statement: "The core trigger-conditions-actions engine, the YAML/JSON definition schema, the channel-event and webhook and schedule trigger paths, and the sequential executor with template resolution and execution tracing are all implemented and reachable in the current codebase, supporting the VISION_PROJECTS.md 'Ships today' marker for the capability as a whole."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-workflow/src/schema.rs"
      - "crates/buzz-workflow/src/executor.rs"
      - "crates/buzz-relay/src/router.rs:132"
      - "VISION_PROJECTS.md:250"
    confidence: 0.85
  - statement: "Several individual action types dispatched by this same executor are unimplemented or broken rather than shipped: dispatch_action returns WorkflowError::NotImplemented immediately for both SendDm and SetChannelTopic without attempting any side effect; RequestApproval returns a Suspended token but persists no approval record and emits no kind:46010 event, a gap the code's own comment marks 'TODO (WF-08)'; and AddReaction's HTTP call targets POST /api/messages/{message_id}/reactions, a path that does not appear anywhere in buzz-relay's router (grepped for 'messages/.../reactions' and 'reactions' route registrations, zero matches), so a workflow author cannot currently rely on any of these three actions to complete successfully."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/executor.rs:643-653"
      - "crates/buzz-workflow/src/executor.rs:713-728"
      - "crates/buzz-workflow/src/executor.rs:969-1001"
  - statement: "The scope and correctness of each individual action's or trigger's implementation (approval, reaction, send-dm, set-channel-topic, send-message, delay, webhook call, schedule, message trigger, reaction trigger, webhook trigger) is owned by that action's or trigger's own sibling corpus node under capabilities/workflows/, per the batch of ~15 sibling document tasks under parent Feature #613, none of which is merged as of this node's recorded revision."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#613 (parent Feature) and its child task issues #822-#823, #829-#843"
relationships:
  - type: references
    target: architecture-flows-workflow-execution
  - type: references
    target: architecture-containers-relay
---

# Workflow engine: capability

Buzz can run **channel-scoped automations**: a named trigger (a message posted, a
reaction added, a diff posted, or a schedule tick) sets off an ordered sequence of
steps, each optionally gated by a condition, each dispatching one action (send a
message, add a reaction, call a webhook, request approval, and others). A human or
agent author writes the automation once, as YAML, and the engine runs it every time
the trigger condition is met — without hand-wiring a bot or script for each channel.
This is the same automation VISION_PROJECTS.md's own Capability/Status table names
"Workflow engine (triggers, traces, conditional logic)".

## Maturity

**Shipped: the core engine.** VISION_PROJECTS.md marks the workflow engine "Ships
today" (`VISION_PROJECTS.md:250`). That marker is backed by working code, not aspiration
alone: a real YAML/JSON definition schema (`crates/buzz-workflow/src/schema.rs`), three
live trigger paths (an in-process channel-event hook, a 60-second cron/interval loop,
and a routed `POST /hooks/{id}` webhook — `crates/buzz-relay/src/router.rs:132`), and a
shared sequential executor that evaluates conditions, resolves `{{trigger.X}}` /
`{{steps.ID.output.X}}` templates, dispatches actions under a timeout, and records an
execution trace (`crates/buzz-workflow/src/executor.rs`). A `buzz-cli` `Workflows`
subcommand group gives both humans and agents a command-line surface onto the same
capability (`crates/buzz-cli/src/lib.rs:201-203`,
`crates/buzz-cli/src/commands/workflows.rs`).

**Not shipped, or broken: several individual actions.** The same executor that
correctly dispatches, for example, `SendMessage` and `CallWebhook` (see the referenced
flow node) also dispatches three actions that do not work today:

- `SendDm` and `SetChannelTopic` both return `WorkflowError::NotImplemented` the
  instant they are dispatched, before attempting any side effect
  (`crates/buzz-workflow/src/executor.rs:643-653`).
- `RequestApproval` returns a suspended run with a generated token, but persists no
  approval record and emits no `kind:46010` event — the code's own comment marks this
  `TODO (WF-08)` (`crates/buzz-workflow/src/executor.rs:713-728`).
- `AddReaction` issues an HTTP call to `POST /api/messages/{message_id}/reactions`, a
  route absent from `buzz-relay`'s router — a workflow author cannot rely on this
  action completing (`crates/buzz-workflow/src/executor.rs:969-1001`).

So the honest maturity statement is two-part: the trigger → conditions → actions
engine itself, its definition schema, and its three trigger paths are shipped and
exercised; several of the action types it can dispatch are not. Each broken or
unimplemented action's own specifics, fix, and verification are owned by that
action's own sibling corpus node under `capabilities/workflows/` (see *Scope and
omissions*), not restated here beyond this one honest sentence.

## Boundary

This node does not describe:
- **How the engine is built.** `crates/buzz-workflow`'s trigger dispatch, executor
  loop, trust-boundary checks (community fence, owner authority, webhook secret,
  outbound SSRF guard) and failure/rollback behavior are documented in full by
  `architecture-flows-workflow-execution`, referenced below — this node cites that
  detail, it does not repeat it.
- **The interface(s) this capability is exposed through** — the `buzz-cli` `Workflows`
  subcommand group and the `POST /hooks/{id}` HTTP webhook route. No interface-typed
  corpus node yet exists for either (unmerged as of this revision), so this node cites
  the source files directly rather than a corpus relationship; a future interface node
  should own describing their operations.
- **The step-by-step path one interaction takes.** That is a flow node's territory —
  `architecture-flows-workflow-execution` already fills that role for the run-time
  engine.
- **Any single trigger's or action's own contract, correctness, or fix.** Each of
  `message-trigger`, `reaction-trigger`, `schedule-trigger`, `webhook-trigger`,
  `send-message-action`, `send-dm-action`, `set-topic-action`, `reaction-action`,
  `delay-action`, `webhook-action`, `approval-action`, plus `workflow-definition`,
  `workflow-step`, `workflow-run`, `workflow-condition` and `workflow-concurrency`, is
  its own sibling document under `capabilities/workflows/` (parent Feature #613);
  this node names the overall capability and its maturity, and does not re-litigate
  any one sibling's findings.
- **How the running engine is operated** — deployment, monitoring, incident response
  for the relay process that hosts it. That is the `operations` corpus surface, not
  this node.

## Relationships

- `references`: `architecture-flows-workflow-execution` — the merged flow node
  documenting this capability's run-time engine end to end.
- `references`: `architecture-containers-relay` — the merged container node
  confirming `buzz-relay` is the sole orchestrator of `buzz-workflow`'s
  `WorkflowEngine`.

No `implements`, `part-of`, `depends-on`, or `supersedes` edge is declared: the ~15
sibling workflow-domain document tasks under Feature #613 are not merged on
`origin/launchpad` at this node's recorded revision, so none is a valid relationship
target yet (checked via `git ls-tree -r --name-only origin/launchpad --
launchpad/docs/corpus`, per `AGENTS.md`'s warning against assuming "nothing to point
at" without checking). The first sibling node to merge is the natural moment to add a
`part-of` edge from it back to this one, or a `references` edge from this one to it.

## Scope and omissions

**This node covers** the workflow engine as one product-level capability: what it is
(trigger → conditions → actions automation, YAML-authored), its two-part maturity
(core engine and definition schema shipped; three specific action types
unimplemented or broken), and pointers to the architecture and interface material
that back those claims without restating them.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The run-time engine's full mechanics (trigger paths, executor loop, trust boundaries, failure/rollback) | `architecture-flows-workflow-execution` |
| Each individual trigger's or action's own contract and correctness | its own sibling node under `capabilities/workflows/` (Feature #613): `message-trigger`, `reaction-trigger`, `schedule-trigger`, `webhook-trigger`, `send-message-action`, `send-dm-action`, `set-topic-action`, `reaction-action`, `delay-action`, `webhook-action`, `approval-action`, `workflow-definition`, `workflow-step`, `workflow-run`, `workflow-condition`, `workflow-concurrency` |
| The `buzz-workflow` crate as an implementation unit | issue `#941` (`implementation/crates/buzz-workflow.md`, not yet drafted) |
| The relay's workflow HTTP surface as a platform interface | issue `#1285` (`platforms/relay/workflow-api.md`, not yet drafted) |
| The `workflow_runs`/related Postgres tables | issue `#1090` (`layers/data/postgres/workflows-tables.md`, not yet drafted) |
| How the running relay is operated | the `operations` corpus surface |

**Expected but not verified when this node was written:**
- Whether any action beyond the three named above (`SendDm`, `SetChannelTopic`,
  `AddReaction`) or any trigger has its own undiscovered gap was not independently
  re-audited here — this node relies on the batch dispatch brief's summary plus its
  own direct reading of `executor.rs`'s `SendDm`/`SetChannelTopic`/`RequestApproval`/
  `AddReaction` arms, not an exhaustive review of every `ActionDef` variant.
- Whether `crates/buzz-relay/src/api/` defines a `messages/{id}/reactions`-shaped
  route under a different path or method than the one `AddReaction` calls was checked
  only by grepping `router.rs` for the literal path fragment; a differently-shaped
  but equivalent route was not exhaustively ruled out.
