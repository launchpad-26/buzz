---
id: capabilities-workflows-webhook-trigger
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
  - statement: "TriggerDef::Webhook is a unit variant of the trigger enum, documented in its own doc comment as firing 'when HTTP POST arrives at /hooks/{id}', distinct from the four other variants (MessagePosted, ReactionAdded, DiffPosted, Schedule)."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/schema.rs:69-70"
  - statement: "The relay's router registers POST /hooks/{id} against api::bridge::workflow_webhook, the sole HTTP entry point for firing a webhook-triggered workflow."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs:132"
  - statement: "workflow_webhook's own doc comment states there is no user auth on this route -- the webhook secret alone authenticates the caller -- and that it returns 202 Accepted with execution running asynchronously rather than waiting for the run to finish."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs:1997-2000"
  - statement: "The handler's first step parses the path's {id} segment as a UUID; a malformed UUID is rejected with 400 Bad Request before any database access."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs:2008-2009"
  - statement: "Before any workflow lookup, the handler binds the request to a community from the HTTP Host header (bind_community); an unmapped host or a lookup failure is mapped to the same generic 404 used for a nonexistent workflow, so a caller cannot distinguish 'wrong tenant' from 'workflow does not exist' -- the code's own comment states this anti-probing intent explicitly."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs:2011-2024"
  - statement: "bind_community itself fails closed on an empty or whitespace-only Host header before even calling the resolver, reusing the same UnmappedHost error an unmapped-but-nonempty host produces, so an empty header cannot be distinguished from an unmapped one either."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/tenant.rs:71-92"
  - statement: "The workflow is then looked up scoped to the bound community; a lookup failure returns the same generic 404, and if the stored definition's trigger is not TriggerDef::Webhook the request is rejected with 400 Bad Request naming the mismatch -- a workflow that exists but is configured for a different trigger type cannot be fired through this door."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs:2027-2041"
  - statement: "Caller authentication is a per-workflow shared secret checked from the X-Webhook-Secret header first, falling back to a ?secret= query-string parameter; a workflow with no stored secret returns 401 telling the caller to re-save the workflow to generate one, and a present-but-wrong secret also returns 401 via a length-checked, XOR-folded comparison in verify_secret."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs:2043-2065"
      - "crates/buzz-relay/src/webhook_secret.rs:71-89"
  - statement: "The request body is optional; if present it is parsed as JSON, with a parse failure returning 400. A JSON object's top-level fields are copied verbatim (non-string values stringified) into TriggerContext.webhook_fields, and the trigger context's channel_id is populated from the workflow's own bound channel_id, not from anything in the request body or headers."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs:2067-2094"
  - statement: "Immediately before any run is created, the handler re-checks that the workflow is both enabled and in Active status (either failing state returns the same generic 404 as a nonexistent workflow), requires the workflow to have a bound channel_id (a webhook-triggered workflow with no channel scope is rejected the same way, since there is no channel authority to verify), and re-runs check_owner_authority against the owner's current standing role rather than trusting anything recorded at save time; any of these failures maps to the same generic 404."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs:2096-2114"
  - statement: "check_owner_authority looks up the owner's current channel role and denies unconditionally on a lookup error (fail-closed); owner_authority_allows then applies the rule: no role denies, any role is sufficient for an ordinary definition, and only 'owner' or 'admin' is sufficient when the definition requires_elevated_authority (i.e. contains a call_webhook step)."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/lib.rs:148-171"
      - "crates/buzz-workflow/src/lib.rs:1029-1035"
  - statement: "Only after every precondition above passes does the handler create the workflow_runs row, spawn the shared executor (execute_from_step, starting at step 0) asynchronously via tokio::spawn, and return 202 Accepted with the new run_id, the workflow_id, and status: \"pending\" immediately -- the HTTP response does not wait for the spawned run to reach a terminal state."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs:2116-2174"
  - statement: "A webhook secret is generated (a UUIDv4 string, 122 bits of randomness) only the first time a workflow definition's trigger becomes TriggerDef::Webhook when the owner saves it via the kind:30620 command; on every later save of the same workflow the existing stored secret is re-extracted and preserved unchanged rather than replaced, and the plaintext secret is included in the command's response exactly once -- only on the save that first generates it, never again on subsequent saves."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/command_executor.rs:714-733"
      - "crates/buzz-relay/src/handlers/command_executor.rs:800-806"
  - statement: "The secret is stored co-located inside the workflow definition JSON under the reserved key \"_webhook_secret\" (inject_secret is a no-op if the definition is not a JSON object), read back by extract_secret, and the module's own doc comment states the definition_hash must be computed after injection or the stored hash will never match the stored definition -- a hash-ordering contract enforced by comment, not by a type-level guarantee."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/webhook_secret.rs:22-28"
      - "crates/buzz-relay/src/webhook_secret.rs:30-41"
      - "crates/buzz-relay/src/webhook_secret.rs:43-50"
  - statement: "A strip_secret helper exists, is documented to remove \"_webhook_secret\" 'before returning a definition to API callers', and is exercised by two unit tests -- but no call site for it was found anywhere in crates/buzz-relay/src outside webhook_secret.rs's own module and its tests, so whether any current code path actually returns a stored workflow definition (and therefore the raw secret) to a caller after creation was not established either way."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/webhook_secret.rs:52-69"
  - statement: "WorkflowDef::validate() rejects, at definition-save time, any send_message step with reply_in_thread: true when the trigger is not one of MessagePosted/ReactionAdded/DiffPosted -- Schedule and Webhook triggers have no triggering message to reply to, so a webhook-triggered workflow authored with reply_in_thread: true fails validation before it can ever be saved, rather than failing at run time."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/schema.rs:216-233"
  - statement: "trigger_matches_event returns false unconditionally for TriggerDef::Webhook, so a webhook-triggered workflow is never fired by a stored channel event (message, reaction, diff) -- the webhook_trigger_never_matches_events unit test asserts exactly this against two representative event kinds."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/lib.rs:1038-1046"
      - "crates/buzz-workflow/src/lib.rs:1427-1435"
  - statement: "crates/buzz-test-client/tests/conformance_multitenant.rs defines a workflow YAML with `trigger: {on: webhook}` for its trigger-isolation probe, but its own comment states the test fires the workflow through the kind:46020 command door, not the webhook HTTP door -- no test in the repository was found that directly exercises POST /hooks/{id}."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/conformance_multitenant.rs:1672-1675"
  - statement: "architecture-flows-workflow-execution, already merged on origin/launchpad, documents all three workflow trigger paths (channel-event, schedule, webhook) and the shared step executor at flow level, including the webhook path's host-bind/secret/authority sequence -- this node narrows to the webhook trigger specifically and references that node rather than restating its content."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/flows/workflow-execution.md"
  - statement: "Issue #837's own Definition of Done requires stating trigger/preconditions/termination-outcome, ordered interactions and data/state movement, authentication/authorization/trust-boundary crossings, and failure/abort/rollback behavior with links to representative verification -- the same four-part shape architecture-flows-workflow-execution was built against for issue #688, which is why this node is organized around the same four sections rather than the capability template's shape."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#837 definition of done"
  - statement: "Issue #836 ('task: document capabilities/workflows/webhook-action.md') is the sibling task documenting the outbound call_webhook action; this node's own subject is the inbound POST /hooks/{id} trigger instead, and the two are deliberately non-overlapping."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#836 title (gh issue list, Feature #613 batch)"
  - statement: "This node's type is chosen as architecture rather than capabilities: node.schema.json's type enum has no dedicated 'flow' value; the corpus's own flow template (launchpad/docs/corpus/templates/flow.md) establishes that a flow-shaped instance node carries type: architecture, a precedent architecture-flows-workflow-execution (merged) already follows; and the capability template's own Boundary section explicitly excludes step-by-step narration ('it does not narrate the sequence of steps'), which is exactly what issue #837's Definition of Done demands -- making capabilities a poor structural fit despite this node's capabilities/workflows/ file path. No merged sibling under capabilities/workflows/ exists yet in this batch (#822-#844 are all OPEN) to settle the question by precedent, so this is this node's own judgment call."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
      - "launchpad/docs/corpus/templates/flow.md"
      - "launchpad/docs/corpus/templates/capability.md"
      - "launchpad/docs/corpus/architecture/flows/workflow-execution.md"
    confidence: 0.65
relationships:
  - type: part-of
    target: capabilities-workflows-workflow
  - type: references
    target: architecture-flows-workflow-execution
---

# Webhook trigger

How an external system starts a Buzz workflow run over HTTP, without ever holding a
relay session: a `POST` to `/hooks/{id}`, authenticated by a per-workflow shared
secret rather than a signed Nostr event or a user session. This is the *inbound*
direction only -- an external caller reaching in to fire a workflow. The *outbound*
direction, where a running workflow calls out to an external URL (the `call_webhook`
action), is sibling issue #836's own subject and is not covered here.

**Scope.** This node covers the `POST /hooks/{id}` handler
(`api::bridge::workflow_webhook`) end to end: what it requires before firing a run,
the order it checks those requirements in, where trust boundaries are crossed, and
what happens on every rejection path. It does not re-derive the channel-event or
schedule trigger paths, the shared step executor, or workflow-definition
authoring/validation as a general subject -- `architecture-flows-workflow-execution`
already covers all three trigger paths and the shared executor, and this node
`references` it rather than restating that content.

## Trigger, preconditions, termination

**Trigger.** An HTTP `POST /hooks/{id}` request, where `{id}` is the workflow's UUID.
This is the only channel through which a `TriggerDef::Webhook`-configured workflow
can ever run -- it is never fired by a channel event (see *Ordered interactions*
below) and never by the schedule loop.

**Preconditions, in the order the handler checks them** (every one fails to the
generic response described in *Outcome* below, not to a partial or best-effort run):

1. `{id}` parses as a UUID.
2. The request's `Host` header binds to a known community (`bind_community`) --
   an empty, unmapped, or lookup-failing host is indistinguishable from every other
   failure in this list.
3. A workflow exists under that UUID *in the bound community* -- the same UUID
   existing in a different community's tenant is not a match.
4. The stored definition's trigger is `TriggerDef::Webhook` -- a workflow configured
   for a different trigger type cannot be fired through this door.
5. A per-workflow shared secret is configured, and the caller supplied a matching one
   (`X-Webhook-Secret` header, or `?secret=` query parameter as a fallback).
6. The workflow is `enabled` and its stored `status` is `Active`.
7. The workflow has a bound `channel_id` -- an unbound webhook-triggered workflow has
   no channel to check authority against, and is rejected on that basis alone.
8. The workflow's owner currently holds sufficient authority in that channel
   (`check_owner_authority`, re-checked at fire time, never trusted from save time).

A workflow can only ever reach preconditions 5-8 if it was *saved* with
`TriggerDef::Webhook` in the first place, which is itself gated by
`WorkflowDef::validate()` rejecting a `reply_in_thread: true` step under a trigger
with no triggering message (see *Secret lifecycle* below for the save-time secret
handling this implies).

**Termination / outcome.** Success creates a `workflow_runs` row and returns
`202 Accepted` with `{run_id, workflow_id, status: "pending"}` before the run has
executed a single step -- the HTTP response never reflects the run's eventual
`Completed`/`Failed` state. Every precondition failure above returns a fixed HTTP
status with no run ever created: `400` for a malformed UUID, a missing/invalid JSON
body, or a trigger-type mismatch; `401` for a missing configured secret or a wrong
one; the same generic `404` for an unmapped host, a nonexistent workflow, a
wrong-tenant workflow, a disabled/non-Active workflow, an unbound workflow, or a
denied owner-authority check.

## Ordered interactions and data/state movement

1. Parse `{id}` as a UUID; `400` on failure.
   (`crates/buzz-relay/src/api/bridge.rs:2008-2009`)
2. Bind the request to a community from its `Host` header, before any workflow
   lookup; unmapped/failed bind → generic `404`.
   (`crates/buzz-relay/src/api/bridge.rs:2011-2024`;
   `crates/buzz-relay/src/tenant.rs:71-92`)
3. Look up the workflow scoped to that community; not found → `404`. Parse its stored
   definition; reject with `400` if its trigger is not `Webhook`.
   (`crates/buzz-relay/src/api/bridge.rs:2027-2041`)
4. Extract the stored secret from the definition; compare it (header, then query
   param) against what the caller supplied. No stored secret, or a mismatch → `401`.
   (`crates/buzz-relay/src/api/bridge.rs:2043-2065`;
   `crates/buzz-relay/src/webhook_secret.rs:71-89`)
5. Parse the optional JSON body; `400` on invalid JSON. Copy its top-level fields into
   `TriggerContext.webhook_fields`; set `channel_id` from the workflow's own bound
   channel (never from the request).
   (`crates/buzz-relay/src/api/bridge.rs:2067-2094`)
6. Re-check `enabled`/`Active` status, presence of a bound channel, and current owner
   authority. Any failure → the same generic `404` used for a nonexistent workflow.
   (`crates/buzz-relay/src/api/bridge.rs:2096-2114`;
   `crates/buzz-workflow/src/lib.rs:148-171`, `:1029-1035`)
7. Create the `workflow_runs` row, spawn `execute_from_step` (step 0) asynchronously,
   and return `202 Accepted` with `{run_id, workflow_id, status: "pending"}`
   immediately -- the spawned task's own eventual success or failure is invisible to
   this HTTP response.
   (`crates/buzz-relay/src/api/bridge.rs:2116-2174`)

**Secret lifecycle (save time, a separate request from the steps above).** When an
owner saves a workflow definition (`kind:30620` command) whose trigger is
`TriggerDef::Webhook`: if the workflow had no stored secret yet, one is generated
(`generate_webhook_secret`, a UUIDv4) and returned to the caller once, in that save's
own response; if a secret already exists, it is re-extracted and re-injected
unchanged, and is *not* returned again. The secret is stored inside the definition
JSON under `"_webhook_secret"`.
(`crates/buzz-relay/src/handlers/command_executor.rs:714-733`, `:800-806`;
`crates/buzz-relay/src/webhook_secret.rs:22-28`, `:30-41`, `:43-50`)

## Diagram

```mermaid
sequenceDiagram
    participant Caller as External caller
    participant Handler as workflow_webhook (buzz-relay)
    participant Engine as WorkflowEngine (buzz-workflow)
    participant DB as buzz-db

    Caller->>Handler: POST /hooks/{id} (X-Webhook-Secret, optional JSON body)
    Handler->>Handler: bind_community(Host header)
    Handler->>DB: get_workflow(community_id, id)
    Handler->>Handler: verify trigger == Webhook, verify secret
    Handler->>Engine: check_owner_authority(owner, channel, def)
    Engine-->>Handler: Ok / Unauthorized
    Handler->>DB: create_workflow_run(...)
    Handler-->>Caller: 202 Accepted {run_id, workflow_id, status: pending}
    Handler->>Engine: execute_from_step(run_id, def, ctx, 0) [spawned, async]
    Engine->>DB: finalize_run(run_id, result)
```

## Boundary

This node does not describe:

- The channel-event and schedule trigger paths, or the shared step executor they
  share with the webhook path -- see `architecture-flows-workflow-execution`.
- The outbound `call_webhook` action, where a running workflow reaches an
  operator-supplied external URL -- see sibling issue #836
  (`capabilities/workflows/webhook-action.md`).
- Workflow-definition authoring/validation as its own subject, beyond the two
  webhook-specific preconditions this node states (`reply_in_thread` rejection,
  secret generation on save).
- Whether `webhook_secret::strip_secret` is actually applied anywhere a stored
  definition is returned to a caller -- see *Scope and omissions*.

## Relationships

- `references`: `architecture-flows-workflow-execution` -- the flow node this
  document narrows from; it owns the full three-trigger-path and shared-executor
  narrative this node does not restate.

## Scope and omissions

**This node covers** the `POST /hooks/{id}` webhook trigger end to end: its
preconditions and their order, the data that moves from the HTTP request into the
run's trigger context, the trust boundaries it crosses (tenant binding, shared-secret
authentication, owner authority), its termination outcomes on both the success and
every rejection path, and the webhook-specific secret lifecycle at workflow-save
time.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The channel-event and schedule trigger paths; the shared step executor | `architecture-flows-workflow-execution` |
| The outbound `call_webhook` action | issue #836 (`webhook-action`) |
| Workflow definition authoring/validation as a general subject | not yet drafted in this batch |
| Workflow run states and concurrency limits in general | issue #841 (`workflow-run`), issue #838 (`workflow-concurrency`) |

**Expected but not verified when this node was written:**

- **No test in this repository was found that directly exercises `POST /hooks/{id}`.**
  The one webhook-shaped workflow YAML in the test suite is fired through the
  `kind:46020` command door instead, per its own comment -- the handler's behavior
  here rests on reading `bridge.rs` directly, not on a passing integration test
  covering the HTTP door itself.
- **Whether `webhook_secret::strip_secret` is wired into any response path that
  returns a stored workflow definition was not established.** It is defined and
  unit-tested, but no call site was found in `crates/buzz-relay/src` outside its own
  module and tests; whether a raw `_webhook_secret` could currently leak through some
  other endpoint that returns a workflow's definition JSON was not traced.
- **Rate limiting or abuse protection on `/hooks/{id}` was not checked.** This node
  only establishes the authentication and authorization checks the handler performs,
  not whether any request-rate control exists in front of it.
