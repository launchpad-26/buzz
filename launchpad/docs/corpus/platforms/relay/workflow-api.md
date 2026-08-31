---
id: platforms-relay-workflow-api
type: platforms
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - operator
evidence:
  - statement: "This node was authored and checked against repository revision 46eb901e5aa928aa147fdaef9a509b636218653f."
    entry_class: FACT
    evidence:
      - "commit 46eb901e5aa928aa147fdaef9a509b636218653f"
  - statement: "The relay registers POST /hooks/{id} against api::bridge::workflow_webhook, with the route's own inline comment describing it as 'Webhook trigger (secret-authenticated, no NIP-98)', and the whole router (including this route) is wrapped in a RequestBodyLimitLayer capping request bodies at 1 MiB (1024*1024 bytes)."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs:132"
      - "crates/buzz-relay/src/router.rs:141-143"
  - statement: "TriggerDef::Webhook's own doc comment states it 'Fires when HTTP POST arrives at `/hooks/{id}`', naming this route as the one and only trigger surface for a workflow whose trigger is Webhook."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/schema.rs:69-70"
  - statement: "workflow_webhook takes the path segment as a workflow UUID, an optional ?secret= query parameter (WebhookQuery), the request's HeaderMap, and the raw request body as axum::body::Bytes; a UUID parse failure returns 400 'invalid workflow UUID' before any other work happens."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs:1990-2009"
  - statement: "The handler binds the request to a community from the HTTP Host header (crate::tenant::bind_community) before any workflow lookup; a bind failure or an id absent from the resolved community both return the same generic 404 'workflow not found', and the handler's own comment states this is deliberate so a caller cannot distinguish 'wrong tenant' from 'workflow does not exist' or probe which hosts/ids exist on other tenants."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs:2011-2031"
  - statement: "After the workflow definition is loaded and parsed, the handler rejects with 400 'workflow does not have a webhook trigger' unless def.trigger matches TriggerDef::Webhook -- a workflow whose trigger is a channel event or a schedule cannot be fired through this endpoint even with a valid id and secret."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs:2033-2041"
  - statement: "The handler authenticates the caller with a per-workflow shared secret, preferring the x-webhook-secret header over the ?secret= query parameter (the handler's own doc comment gives the reason: headers aren't logged by most proxies); a workflow with no stored secret returns 401 telling the caller to re-save the workflow to generate one, and a present-but-wrong secret also returns 401 'authentication failed', both checked via crate::webhook_secret::verify_secret."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs:1997-2000"
      - "crates/buzz-relay/src/api/bridge.rs:2043-2065"
  - statement: "verify_secret in webhook_secret.rs compares two strings by XOR-folding every byte pair rather than short-circuiting, specifically to avoid a timing oracle on the secret's contents; a length mismatch is still revealed immediately, which the module's own comment argues is safe because the secret's length (a 36-byte UUID v4 string) is already implied by the public generation algorithm."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/webhook_secret.rs:71-90"
  - statement: "generate_webhook_secret produces a UUID v4 rendered as a hyphenated string (122 bits of randomness) as the webhook secret's value; inject_secret stores it inside the workflow definition JSON under the key \"_webhook_secret\", and the module's own top-of-file comment states the definition_hash must be computed after injection or every later comparison fails."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/webhook_secret.rs:1-41"
  - statement: "A request body up to 1 MiB is parsed as optional JSON (an empty body is accepted as 'no trigger fields'); a non-empty body that fails to parse as JSON returns 400 'invalid JSON body: <serde error>'. A successfully parsed JSON object's top-level keys are copied into TriggerContext.webhook_fields as strings (non-string values are stringified via their Display/to_string form), and TriggerContext.channel_id is set from the workflow's own bound channel_id, never from the request."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs:2067-2094"
  - statement: "Immediately before creating a run, the handler re-checks that the workflow is enabled and its stored status is Active (buzz_db::workflow::WorkflowStatus::Active) -- either failing condition returns the same generic 404 'workflow not found' used for a nonexistent workflow -- and then re-verifies the owner's current channel authority via state.workflow_engine.check_owner_authority, which is call-site-identical to the SEC-006 recheck the channel-event and schedule trigger paths perform, per architecture-flows-workflow-execution."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs:2096-2114"
  - statement: "On success the handler creates a workflow_runs row via state.db.create_workflow_run (storing the parsed trigger-context JSON), immediately returns HTTP 202 Accepted with a JSON body {run_id, workflow_id, status: \"pending\"}, and only after responding spawns buzz_workflow::executor::execute_from_step (starting at step index 0) followed by engine.finalize_run asynchronously via tokio::spawn -- so the HTTP response never waits for any workflow step to run, and a step failure after the response has already been sent is invisible to the HTTP caller (it is only visible in the workflow_runs row)."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs:2116-2175"
  - statement: "Every non-2xx response from this endpoint uses the relay's standard error envelope, {\"error\": <message>} via the shared api_error/not_found/internal_error helpers, so the webhook API's error shape is not bespoke to this route."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/mod.rs:20-33"
  - statement: "The webhook secret a caller must present is provisioned at workflow-definition save time (the kind:30620 command handler), not by this endpoint: a secret is generated only the first time a workflow's trigger becomes Webhook, is preserved unchanged across later definition updates, and is returned to the saving client exactly once, in the save response's webhook_secret field -- this endpoint has no way to mint, rotate, or display a secret, only to verify one already provisioned elsewhere."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/command_executor.rs:714-733"
      - "crates/buzz-relay/src/handlers/command_executor.rs:800-806"
  - statement: "No test in this repository issues an HTTP request against POST /hooks/{id} itself. The only match for the route outside router.rs/bridge.rs is a doc comment in conformance_multitenant.rs enumerating the relay's full route list, and that same test file's own webhook-triggered-workflow fixture fires through the kind:46020 command door instead, with a comment stating the webhook door is irrelevant to that specific test row. webhook_secret.rs's unit tests cover only the generate/inject/extract/verify primitives in isolation, not the HTTP handler."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/conformance_multitenant.rs:577-581"
      - "crates/buzz-test-client/tests/conformance_multitenant.rs:1672-1687"
      - "crates/buzz-relay/src/webhook_secret.rs:92-161"
  - statement: "architecture-flows-workflow-execution already documents this same webhook trigger path as one of three converging trigger paths into the shared step executor -- its own Trigger/preconditions, Ordered interactions, Trust-boundary crossings, and Failure/abort/rollback sections cover the community/tenant fence, the secret authentication layering under owner-authority, and the async 202-then-execute shape -- so this node references it rather than restating that internal-execution content, and instead documents the wire-level HTTP contract (request/response shapes, headers, status codes) as its own standalone surface."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/architecture/flows/workflow-execution.md"
    confidence: 0.85
---

# Relay platform surface: workflow webhook HTTP API

The Buzz relay exposes one HTTP endpoint, `POST /hooks/{id}`, that lets an
external caller trigger a workflow whose trigger type is `webhook` without
going through the Nostr WebSocket/event-submission path at all. This node
documents that endpoint as a relay platform surface — its request and
response contract, its authentication mechanism, and its real dependency
edges — answering "what must a caller of this HTTP endpoint know" rather than
"how does a workflow run internally," which
`architecture-flows-workflow-execution` already owns (see *Boundary*).

## Responsibility

The endpoint's job is narrow: authenticate an inbound HTTP request as
authorized to fire one specific workflow, and hand off to the shared
workflow executor. The route registration in `crates/buzz-relay/src/router.rs`
carries it as `POST /hooks/{id}` with the inline comment *"Webhook trigger
(secret-authenticated, no NIP-98)"* — naming both what it is (a trigger door)
and how it differs from the relay's other authenticated HTTP surfaces (no
NIP-98 signed-event auth; a bearer-style shared secret instead).
`TriggerDef::Webhook`'s own doc comment in `buzz-workflow` independently names
this same route as the trigger's firing condition: *"Fires when HTTP POST
arrives at `/hooks/{id}`."*

## Public interface

**Request**

| Part | Value | Evidence |
|---|---|---|
| Method + path | `POST /hooks/{id}` | `crates/buzz-relay/src/router.rs:132` |
| Path param `id` | Workflow UUID | `crates/buzz-relay/src/api/bridge.rs:2008-2009` |
| Auth (preferred) | `X-Webhook-Secret: <secret>` header | `crates/buzz-relay/src/api/bridge.rs:2045-2050` |
| Auth (fallback) | `?secret=<secret>` query parameter | `crates/buzz-relay/src/api/bridge.rs:1992-1994`, `2049` |
| Tenant binding | `Host` header, resolved via `bind_community` before any lookup | `crates/buzz-relay/src/api/bridge.rs:2018-2025` |
| Body | Optional JSON object, ≤ 1 MiB; each top-level key/value becomes a `TriggerContext.webhook_fields` entry | `crates/buzz-relay/src/api/bridge.rs:2067-2093`, `crates/buzz-relay/src/router.rs:141-143` |

**Response**

| Status | Body | When | Evidence |
|---|---|---|---|
| 202 Accepted | `{"run_id", "workflow_id", "status": "pending"}` | Run created; execution spawned asynchronously | `crates/buzz-relay/src/api/bridge.rs:2167-2174` |
| 400 Bad Request | `{"error": "invalid workflow UUID"}` | Path segment does not parse as a UUID | `crates/buzz-relay/src/api/bridge.rs:2008-2009` |
| 400 Bad Request | `{"error": "workflow does not have a webhook trigger"}` | Definition's trigger is not `Webhook` | `crates/buzz-relay/src/api/bridge.rs:2036-2041` |
| 400 Bad Request | `{"error": "invalid JSON body: <detail>"}` | Non-empty body fails to parse as JSON | `crates/buzz-relay/src/api/bridge.rs:2068-2075` |
| 401 Unauthorized | `{"error": "webhook secret required but not configured — re-save the workflow to generate one"}` | No secret stored on the workflow | `crates/buzz-relay/src/api/bridge.rs:2059-2064` |
| 401 Unauthorized | `{"error": "authentication failed"}` | Provided secret does not match stored secret | `crates/buzz-relay/src/api/bridge.rs:2052-2058` |
| 404 Not Found | `{"error": "workflow not found"}` | Host does not bind to a community, workflow id absent from that community, workflow disabled/not-`Active`, unbound-channel workflow, or owner-authority check fails — all collapsed to the same generic message | `crates/buzz-relay/src/api/bridge.rs:2022-2031`, `2103-2114` |
| 500 Internal Server Error | `{"error": "internal server error"}` | Corrupt stored definition, or a DB error creating the run | `crates/buzz-relay/src/api/bridge.rs:2033-2035`, `2116-2120` |

All error responses use the relay's shared `{"error": <message>}` envelope
(`api_error` / `not_found` / `internal_error` in `crates/buzz-relay/src/api/mod.rs:20-33`)
— this endpoint does not define a bespoke error shape.

**Ordering of checks.** UUID parse → tenant bind → workflow lookup →
definition parse → trigger-type check → secret verification → enabled/Active
+ owner-authority recheck → run creation → `202` response → async execution.
Every failure before run creation returns before any database write happens
except the read lookups themselves.

## Dependencies

**Depends on** (this endpoint requires these to do its job):

| Component | Why | Evidence |
|---|---|---|
| `buzz-workflow` (`executor::execute_from_step`, `WorkflowEngine::finalize_run`, `WorkflowEngine::check_owner_authority`) | Executes the run and re-checks owner authority; the handler only creates the run row and spawns execution | `crates/buzz-relay/src/api/bridge.rs:2110-2165` |
| `crate::webhook_secret` (this crate) | Verifies the caller-supplied secret against the stored one in constant time | `crates/buzz-relay/src/webhook_secret.rs:71-90` |
| `crate::tenant::bind_community` (this crate) | Resolves the request's community from the `Host` header before any workflow lookup | `crates/buzz-relay/src/api/bridge.rs:2018-2025` |
| `buzz_db::workflow` (via `AppState.db`) | Loads the workflow row and its `WorkflowStatus`, and persists the new `workflow_runs` row | `crates/buzz-relay/src/api/bridge.rs:2027-2031`, `2103-2120` |

**Depended on by:** none found. This route is the outermost HTTP entry point
for the webhook trigger path — nothing else in the repository calls it
in-process; it exists to be called by an external, operator-configured
caller.

## Boundary

This node does not describe:
- **How a triggered run actually executes** — step ordering, condition/
  template evaluation, per-step timeouts, action dispatch (including the
  outbound-SSRF-guarded `call_webhook` action), or terminal run states. All
  of that is `architecture-flows-workflow-execution`'s subject, and this
  node `references` it instead of restating it (see *Relationships*).
- **How the webhook secret is minted or rotated.** Secret provisioning is a
  side effect of the `kind:30620` workflow-definition save path in
  `crates/buzz-relay/src/handlers/command_executor.rs`, not of this HTTP
  endpoint — see the *Public interface* and evidence ledger above for the
  one fact this node needs from that path (where the secret this endpoint
  checks actually comes from).
- **The other two workflow trigger paths** (channel-event, schedule) — they
  do not go through HTTP at all and are `architecture-flows-workflow-execution`'s
  subject.
- **Install/usage instructions for running the relay itself** — this is a
  wire-contract document, not a deployment or operator runbook.

## Relationships

- references: architecture-flows-workflow-execution

## Scope and omissions

**This node covers** the `POST /hooks/{id}` HTTP contract exposed by the
relay: request shape (path, headers, query fallback, body), the full
response/status-code matrix including every distinct error condition, the
order in which checks run, and this endpoint's real dependency edges within
`buzz-relay` and into `buzz-workflow`/`buzz-db`.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Internal execution semantics of a triggered run (step ordering, templating, timeouts, action dispatch, terminal states) | `architecture-flows-workflow-execution` |
| Webhook secret generation/rotation at workflow-definition save time | The `kind:30620` command handler (`crates/buzz-relay/src/handlers/command_executor.rs`) — not yet its own corpus node at this revision |
| The channel-event and schedule trigger paths | `architecture-flows-workflow-execution` |
| Deployment/operator instructions for running the relay | Not this node's genre |

**Expected but not verified when this node was written:**

- **No test in this repository was found that issues an actual HTTP request
  against `POST /hooks/{id}`.** The route's behavior above is verified by
  direct reading of `bridge.rs`, not by running any test against the live
  endpoint. `webhook_secret.rs`'s unit tests verify the secret
  generate/inject/extract/verify primitives in isolation, which is
  representative for the authentication mechanism but not for the handler's
  routing, tenant-binding, or response-shaping logic.
- **Whether any operator-facing documentation instructs a real external
  caller (e.g. a CI system, a chat bot, a third-party SaaS) how to configure
  this webhook** was not searched for; if such a runbook exists, it is not
  cited here.
