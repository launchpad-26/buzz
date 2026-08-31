---
id: capabilities-workflows-workflow-definition
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
  - statement: "No node exists under launchpad/docs/corpus/capabilities/ on origin/launchpad at the recorded revision -- the workflows/ directory itself does not exist there -- so no sibling capability node (workflow, workflow-run, workflow-step, workflow-trigger) had settled a type precedent to follow, and this node's type: capabilities is instead an inference from the directory-to-type convention already visible in the merged architecture/ subtree (architecture/containers/*.md and architecture/flows/*.md both carry type: architecture) plus the capability template's own stated rule that a capability-shaped node carries type: capabilities with no combination needed."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/templates/capability.md"
      - "launchpad/docs/corpus/architecture/containers/relay.md"
      - "launchpad/docs/corpus/architecture/flows/workflow-execution.md"
    confidence: 0.8
  - statement: "A workflow definition (WorkflowDef) is authored as YAML and carries a required name, an optional description, exactly one TriggerDef, an ordered Vec<Step>, and an enabled flag defaulting to true; all types must round-trip through both YAML and canonical JSON without loss."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/schema.rs:1-27"
  - statement: "TriggerDef is a serde-internally-tagged enum (tag field `on`) with exactly five variants: MessagePosted and DiffPosted (each with an optional evalexpr filter), ReactionAdded (an optional emoji plus an optional filter), Schedule (mutually exclusive cron or interval), and Webhook (no fields, fires on POST /hooks/{id})."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/schema.rs:33-71"
  - statement: "Each Step carries a unique id, an optional name, an optional `if` evalexpr condition (a false condition skips the step rather than failing the run), an optional timeout_secs, and exactly one ActionDef selected from seven variants: SendMessage, SendDm, SetChannelTopic, AddReaction, CallWebhook, RequestApproval, and Delay."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/schema.rs:73-155"
  - statement: "WorkflowDef::validate() enforces: a non-empty name; at least one step; every step id non-empty, at most 64 characters, alphanumeric-or-underscore only (dashes are rejected because step ids become evalexpr variable names like steps_{id}_output_{field}, and a dash would parse as subtraction), and unique within the definition; reply_in_thread: true only on a message-based trigger (message_posted, reaction_added, diff_posted), never on schedule or webhook; a Schedule trigger must set exactly one of cron or interval, never both nor neither; a set cron string must parse via the cron crate after 5/6/7-field normalization; and a set interval must parse to at least 60 seconds, since the background scheduler loop itself ticks every 60 seconds."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/schema.rs:157-306"
  - statement: "parse_yaml() is the sole entry point that turns an authored YAML string into a validated (WorkflowDef, canonical_json) pair, returning a WorkflowError on either a YAML parse failure (InvalidYaml) or a validate() invariant violation (InvalidDefinition)."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/schema.rs:308-317"
      - "crates/buzz-workflow/src/error.rs:17-26"
  - statement: "WorkflowDef::requires_elevated_authority() returns true when any step's action is CallWebhook, the one action capable of exfiltrating channel data to an arbitrary external destination."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/schema.rs:157-169"
  - statement: "A workflow definition is submitted as a Nostr event of kind 30620 (KIND_WORKFLOW_DEF), a NIP-33 parameterized-replaceable kind (asserted to fall in the 30000-39999 addressable range), whose content is the raw YAML, whose `h` tag names the owning channel UUID, and whose `d` tag names the workflow's own UUID."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs:441-442"
      - "crates/buzz-core/src/kind.rs:861"
  - statement: "The relay's live handler for kind:30620 events, handle_workflow_def in command_executor.rs, requires both an `h` tag (channel) and a `d` tag (workflow id) and rejects the event outright if either is missing or fails to parse as a UUID; it then requires the submitter to be a member of that channel, parses and validates the YAML body via parse_yaml, and -- per SEC-006 -- additionally requires the submitter to currently hold the owner or admin role in that channel whenever requires_elevated_authority() is true, failing closed (rejecting) if the role lookup itself errors."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/command_executor.rs:641-691"
  - statement: "check_owner_authority in buzz-workflow's WorkflowEngine re-checks the same rule at execution time, independent of the save-time check: the definition's owner must still be an active channel member, and if the stored definition requires elevated authority, the owner must currently hold owner or admin -- any role-lookup error is treated as a denial (fail-closed), so a removed or demoted owner cannot retain exfiltration authority merely because a membership read happened to fail at run time."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/lib.rs:132-171"
      - "crates/buzz-workflow/src/lib.rs:1029-1034"
  - statement: "VISION_PROJECTS.md's own Capability | Status table marks 'Workflow engine (triggers, traces, conditional logic)' as shipped ('Ships today'), and this is the maturity claim's citable source rather than an assumption."
    entry_class: FACT
    evidence:
      - "VISION_PROJECTS.md:250"
  - statement: "schema.rs carries an in-file #[cfg(test)] unit-test module (over 60 individual #[test] functions) exercising every TriggerDef variant, every ActionDef variant, every validate() invariant (empty name, empty steps, duplicate/invalid step ids, reply_in_thread cross-trigger rules, cron/interval mutual exclusion and minimum-interval enforcement, 5/6/7-field cron normalization), and full YAML-to-JSON round-tripping -- the verification this capability's shipped maturity claim rests on in addition to the VISION_PROJECTS.md status marker."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/schema.rs:319-1001"
  - statement: "An #[ignore]'d integration-test module in buzz-test-client's own code comments claims that submitting a kind:30620 event omits the `d` tag entirely and that the server generates the workflow id and returns it in the OK-message response, directly contradicting handle_workflow_def's current, unconditional requirement of a client-supplied `d` tag; because the test carrying that claim is marked #[ignore] and is not exercised by CI, it is not 'passing test' evidence under this corpus's own evidence-precedence rule (ADR-0029, restated in AGENTS.md), so this node treats the current code path as the FACT and names the ignored test's contradictory comment as unresolved drift rather than silently picking a side."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/conformance_multitenant.rs:1647-1779"
      - "crates/buzz-relay/src/handlers/command_executor.rs:655-658"
  - statement: "relationships.schema.json states references' directionality as 'source cites target as supporting context; no ownership or currency dependency implied', the loose-coupling relationship type this node uses to point at the already-merged runtime-execution flow node without duplicating its content."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/relationships.schema.json"
relationships:
  - type: references
    target: architecture-flows-workflow-execution
---

# Workflow definition: capability

Buzz lets a channel member author a **workflow definition** -- a single named
YAML document that declares one trigger, an ordered sequence of steps, and
whether the workflow is currently enabled -- and have the relay parse,
validate, and store it as the durable, replaceable source a workflow run is
later executed from. This is the authoring-time capability: the shape a
human or agent writes down, not the execution that later reads it.

A workflow author writes a `name`, an optional `description`, exactly one
trigger (`message_posted`, `reaction_added`, `diff_posted`, `schedule`, or
`webhook`), and one or more steps, each performing exactly one of seven
action kinds (`send_message`, `send_dm`, `set_channel_topic`, `add_reaction`,
`call_webhook`, `request_approval`, `delay`). Steps may carry an `if`
evalexpr condition and a timeout. The relay rejects a syntactically valid but
semantically inconsistent definition before it is ever stored -- empty
names, duplicate or unsafe step ids, an ambiguous or malformed schedule, and
a `reply_in_thread` flag on a trigger with no message to reply to are all
refused at authoring time rather than failing later at run time.

## Maturity

**Shipped.** VISION_PROJECTS.md's own Capability | Status table marks the
workflow engine -- "triggers, traces, conditional logic" -- as "Ships
today" (`VISION_PROJECTS.md:250`). The definition schema itself
(`crates/buzz-workflow/src/schema.rs`) is exercised by an extensive in-file
unit-test suite covering every trigger variant, every action variant, the
full validation rule set, and YAML/JSON round-tripping.

## Behavioral rules and constraints

- **One trigger, many steps.** A definition names exactly one `TriggerDef`
  and an ordered, non-empty list of `Step`s.
- **Step ids are load-bearing identifiers, not free text.** They must be
  non-empty, at most 64 characters, and contain only alphanumeric characters
  and underscores -- a dash is rejected because step ids become evalexpr
  variable names (`steps_{id}_output_{field}`) and a dash would parse as
  subtraction. Step ids must be unique within one definition.
- **`reply_in_thread` requires a message to reply to.** It is only valid on
  `message_posted`, `reaction_added`, or `diff_posted` triggers; `schedule`
  and `webhook` triggers have no triggering message, and the definition is
  rejected if any step sets it there.
- **A schedule trigger names exactly one of `cron` or `interval`, never
  both, never neither.** A set `cron` value must parse (after normalizing
  5/6/7-field cron strings to the 7-field form the underlying `cron` crate
  requires); a set `interval` must resolve to at least 60 seconds, because
  the background scheduler loop that fires schedule triggers itself only
  ticks once every 60 seconds -- a sub-minute interval could never fire
  correctly and is rejected at definition time instead of silently never
  firing.
- **One action kind is a standing authority elevation, not an ordinary
  step.** `call_webhook` can forward channel content to an arbitrary
  external HTTPS endpoint. A definition containing it
  (`requires_elevated_authority() == true`) may only be *saved* by a
  submitter who currently holds the channel's `owner` or `admin` role
  (`command_executor.rs`'s `handle_workflow_def`, citing SEC-006), and the
  same elevated-role check is re-applied independently at *execution* time
  against the definition's owner (`WorkflowEngine::check_owner_authority`).
  Both checks fail closed: any error while looking up the relevant role is
  treated as a denial, not a pass-through.
- **Definitions are addressed as NIP-33 parameterized-replaceable events**
  (kind 30620 / `KIND_WORKFLOW_DEF`), tagged `h` for the owning channel and
  `d` for the workflow's own UUID -- the same shape that lets a later event
  with the same `d` tag replace an earlier definition in place, per NIP-33.

## Boundary

This node does not describe:
- **How a workflow run executes** the steps of a stored definition
  (variable substitution, sequential execution, traces) -- that is the
  architecture flow already documented at `architecture-flows-workflow-
  execution`, which this node `references` rather than restates.
- **The run itself as a distinct entity** (a workflow-run instance, its
  status, its trace) -- a separate capability node, not yet drafted at the
  time this node was written.
- **An individual step or action's own runtime semantics** in depth (for
  example exactly how `send_message` templating resolves `{{trigger.text}}`)
  -- a separate capability node, not yet drafted at the time this node was
  written.
- **The trigger-matching machinery that decides which stored definitions a
  given incoming event fires** -- a separate capability node, not yet
  drafted at the time this node was written.
- **The workflow engine as a whole product capability** (the umbrella that
  the definition, run, step, and trigger concepts are all constituent parts
  of) -- a separate capability node, not yet drafted at the time this node
  was written; this node makes no `part-of` claim toward it because no such
  node exists yet on `origin/launchpad` to target.
- **How the running system operates workflows** (deployment, monitoring,
  incident response for the scheduler loop or webhook endpoint) -- the
  `operations` corpus surface, not this one.

## Relationships

- `references: architecture-flows-workflow-execution` -- the merged
  architecture node documenting the runtime flow that consumes a stored
  workflow definition; this node covers the authoring-time shape and
  validation, that node covers execution, and neither restates the other's
  content. No `part-of` or other relationship is declared toward a
  workflow/workflow-run/workflow-step/workflow-trigger node, because none of
  those exists on `origin/launchpad` at the recorded revision to target --
  checked directly (`launchpad/docs/corpus/capabilities/` does not contain a
  `workflows/` directory there), not assumed.

## Scope and omissions

**This node covers** the shape and authoring-time validation rules of a
workflow definition (`WorkflowDef`, `TriggerDef`, `Step`, `ActionDef`), how
it is submitted and stored as a kind:30620 Nostr event, the SEC-006
elevated-authority gate that applies to `call_webhook`-carrying definitions
both at save time and at execution time, and the capability's current
shipped maturity.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| How a stored definition is executed step by step | `architecture-flows-workflow-execution` |
| The workflow-run entity itself | a separate, not-yet-drafted capability node |
| Individual step/action runtime semantics (templating, timeouts in effect) | a separate, not-yet-drafted capability node |
| Trigger-to-event matching machinery | a separate, not-yet-drafted capability node |
| The workflow engine as one umbrella capability | a separate, not-yet-drafted capability node |
| How the running system operates workflows | the `operations` corpus surface |
| The front-matter contract itself | `launchpad/docs/corpus/schema/node.schema.json` |
| Creating, updating and retiring a node procedurally | `launchpad/docs/corpus/AGENTS.md` |

**Expected but not verified when this node was written:**
- **The `d`-tag discrepancy above was not resolved.** `handle_workflow_def`
  unconditionally requires and validates a `d` tag as the workflow's UUID;
  an `#[ignore]`d integration test's own code comments assert the opposite
  (no `d` tag; the server generates and returns the id). This node states
  the code's current, live behavior as FACT and records the ignored test's
  contradictory comment here rather than silently resolving which one is
  intended -- a human should confirm whether the test is stale or whether
  `handle_workflow_def` regressed a once-server-generated-id design.
- **`buzz-cli`'s workflow subcommands** (`crates/buzz-cli/src/commands/
  workflows.rs`) were located but not exhaustively read against every field
  this node documents; they are consistent with kind:30620 and the `d`-tag
  convention on the query/list side, but their own create-path behavior was
  not independently exercised against a running relay for this node.
- **No corpus sibling node exists yet** to confirm this node's `type:
  capabilities` choice by precedent -- see the INFERENCE evidence entry
  above. The first additional node placed under `capabilities/workflows/`
  is the moment to revisit that inference.
