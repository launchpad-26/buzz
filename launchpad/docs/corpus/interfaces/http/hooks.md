---
id: interfaces-http-hooks
type: interfaces-events
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 650354eab8d41ab6ce1a71de079a6c6d95c69052."
    entry_class: FACT
    evidence:
      - "commit 650354eab8d41ab6ce1a71de079a6c6d95c69052"
  - statement: "Root AGENTS.md describes the relay's HTTP surface as deliberately narrow and names 'workflow webhooks at /hooks/{id}' as one of its members, alongside NIP-11/NIP-05 metadata, POST /events, POST /query, POST /count, Blossom media, git smart HTTP, git policy hooks, and health probes — all preserving the same host-derived community boundary."
    entry_class: FACT
    evidence:
      - "AGENTS.md:158"
  - statement: "crates/buzz-relay/src/router.rs registers POST /hooks/{id} to api::bridge::workflow_webhook inside the main api_router block, with no NIP-98 auth middleware applied to that specific route (the surrounding comment reads 'Webhook trigger (secret-authenticated, no NIP-98)')."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs:130-132"
  - statement: "workflow_webhook (crates/buzz-relay/src/api/bridge.rs:2001-2175) takes the path segment {id} as a workflow UUID (parsed with uuid::Uuid::parse_str), a HeaderMap, an optional ?secret= query parameter, and a raw request body (axum::body::Bytes) that is optionally parsed as JSON."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs:2001-2009"
  - statement: "Before any tenant-scoped lookup, workflow_webhook resolves the request's Host header through crate::tenant::bind_community, and the resulting community — not anything in the workflow row or the request body — determines which community's workflow table is queried; the handler's own comment states this explicitly as 'the host — not the workflow row — determines the tenant'."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs:2011-2025"
  - statement: "bind_community (crates/buzz-relay/src/tenant.rs:71-92) fails closed with BindError::UnmappedHost both when the normalized Host header is empty and when the resolver finds no community for that host, so an unmapped host and a mapped-but-wrong host produce the same error variant."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/tenant.rs:71-92"
  - statement: "workflow_webhook maps every one of: an invalid workflow UUID, a bind_community failure, a get_workflow lookup failure, a disabled or non-Active workflow, a workflow with no channel_id, and a failed check_owner_authority call, to the same generic 404 response body ('workflow not found') — the handler's own comment states this is deliberate so 'a caller cannot probe which hosts or workflow ids exist on other tenants' and so a revoked-owner workflow is 'indistinguishable from a nonexistent one'."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs:2027-2114"
  - statement: "workflow_webhook returns 400 Bad Request when the workflow's parsed trigger is not buzz_workflow::TriggerDef::Webhook, and separately when the request body is present but fails to parse as JSON."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs:2036-2041"
      - "crates/buzz-relay/src/api/bridge.rs:2067-2075"
  - statement: "TriggerDef::Webhook (crates/buzz-workflow/src/schema.rs:38-70) is a bare, field-less enum variant — a workflow either has a webhook trigger or it does not, with no per-workflow webhook configuration carried in the trigger definition itself."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/schema.rs:38"
      - "crates/buzz-workflow/src/schema.rs:70"
  - statement: "Authentication is a bearer secret, not user identity: workflow_webhook reads an X-Webhook-Secret header (preferred) or falls back to the ?secret= query parameter, extracts the stored secret from the workflow definition's _webhook_secret key via webhook_secret::extract_secret, and compares the two via webhook_secret::verify_secret; a missing stored secret (never generated) returns 401 with a message telling the caller to re-save the workflow, and a mismatch returns 401 'authentication failed' after a tracing::warn! log."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs:2043-2065"
      - "crates/buzz-relay/src/webhook_secret.rs:46-55"
  - statement: "verify_secret (crates/buzz-relay/src/webhook_secret.rs:81-89) does an XOR-fold comparison over the full length of both strings after an early length-mismatch return, explicitly documented as accepting that the length check itself is not constant-time because the secret's fixed UUID-v4 length (36 bytes) already gives an attacker nothing extra to learn from it."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/webhook_secret.rs:81-89"
  - statement: "generate_webhook_secret (crates/buzz-relay/src/webhook_secret.rs:26-28) produces a UUID v4 rendered as a hyphenated string as the webhook secret, documented in the function's own doc comment as giving '122 bits of randomness'."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/webhook_secret.rs:26-28"
  - statement: "The webhook secret is generated once, the first time a workflow gains a webhook trigger, inside handle_workflow_def (crates/buzz-relay/src/handlers/command_executor.rs:641-814) — the handler for kind:30620 workflow-definition Nostr command events, not this HTTP endpoint. handle_workflow_def preserves an existing secret across updates and returns a freshly generated secret to the caller, in the command's response JSON, only the first time; this HTTP endpoint (workflow_webhook) never returns or regenerates the secret."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/command_executor.rs:713-728"
      - "crates/buzz-relay/src/handlers/command_executor.rs:799-806"
  - statement: "The webhook_secret.rs module doc comment states an explicit hash-ordering contract: the secret must be injected into the workflow definition JSON with inject_secret before definition_hash is computed over that JSON, because reversing the two steps was a prior bug where the stored hash never matched the stored definition — so the secret is covered by the same integrity hash as the rest of the workflow definition, and there is no separate interface version number for this endpoint."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/webhook_secret.rs:1-14"
  - statement: "SEC-006 (crates/buzz-relay/src/api/bridge.rs:2096-2114): the webhook secret authenticates the HTTP caller, but the resulting workflow run executes with the workflow owner's standing authority, not the caller's — so, immediately before creating a run, workflow_webhook rejects disabled/non-Active workflows, requires a channel_id to be present, and rechecks the owner's current channel membership/role via state.workflow_engine.check_owner_authority, failing closed (generic 404) on any of these."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs:2096-2114"
  - statement: "An accepted request body is optionally parsed as JSON; if it is a JSON object, every top-level key/value pair is copied (string values verbatim, non-string values via their Display/to_string form) into buzz_workflow::executor::TriggerContext's webhook_fields map (crates/buzz-workflow/src/executor.rs:27-46), alongside a channel_id field taken from the workflow row — this is the entire caller-supplied payload shape the workflow's step templates can reference."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs:2067-2094"
      - "crates/buzz-workflow/src/executor.rs:27-46"
  - statement: "After the owner-authority recheck, workflow_webhook unconditionally calls state.db.create_workflow_run to insert a new workflow_run row (crates/buzz-db/src/store/workflow.rs:803), then returns immediately with HTTP 202 Accepted and a JSON body of {run_id, workflow_id, status: \"pending\"} while spawning the actual execution (buzz_workflow::executor::execute_from_step followed by engine.finalize_run) on a detached tokio::spawn task — the HTTP response never carries the run's eventual outcome."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs:2116-2172"
  - statement: "There is no idempotency key or deduplication on this endpoint: every request that passes the checks above creates exactly one new workflow_run row via create_workflow_run, so a duplicated webhook delivery (retried by the caller's own webhook sender, for example) produces a duplicate run rather than being deduplicated by the relay."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs:2116-2120"
    confidence: 0.85
  - statement: "buzz_db::workflow::RunStatus (crates/buzz-db/src/store/workflow.rs:80-93) enumerates Pending, Running, WaitingApproval, Completed, Failed, and Cancelled as the states a triggered run can occupy after this endpoint's initial 202 response, and WorkflowRunFailure (crates/buzz-db/src/store/workflow.rs:906-911) carries a stable machine-readable code plus a human-readable message when a run fails — this is the shape a caller must query separately (not via this endpoint) to learn a run's eventual outcome."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/workflow.rs:80-93"
      - "crates/buzz-db/src/store/workflow.rs:906-911"
  - statement: "crates/buzz-relay/src/api/workflows.rs exposes GET /workflows/{workflow_id}/runs and GET /workflows/{workflow_id}/runs/{run_id}/approvals as separate, NIP-98-authenticated read endpoints over the same run rows this endpoint creates — its own module doc comment states 'Runs and approvals are relay-owned database rows, not Nostr events. These endpoints expose those read models without inventing synthetic events.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/workflows.rs:1-4"
  - statement: "crates/buzz-test-client/tests/conformance_multitenant.rs's workflows module asserts, by defining the same workflow-id UUID space isolation, that a workflow defined under one community's host is only resolvable through this endpoint when bound to that same community's host, and its own comments state the community fence on get_workflow is deliberately the only mechanism the test isolates as the cause of a cross-community rejection."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/conformance_multitenant.rs:1645-1663"
  - statement: "Issue #982's Definition of Done requires that this node define inputs/messages, outputs/responses, error/rejection behavior, authentication/authorization, versioning/compatibility, and ordering/idempotency where applicable, plus a link to any authoritative machine/spec representation and at least one valid and one failure example."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#982 definition of done"
  - statement: "No OpenAPI, AsyncAPI, or other machine-readable specification document exists for this endpoint anywhere in the repository; the router registration and the handler function are the only authoritative representation of its contract."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay/src/router.rs:130-132"
      - "crates/buzz-relay/src/api/bridge.rs:2001-2175"
    confidence: 0.75
---

# HTTP workflow webhook trigger (`POST /hooks/{id}`): interface

This node documents the relay's `POST /hooks/{id}` HTTP route — the boundary across
which an external caller (a third-party service, a script, a `curl` invocation) and
the relay exchange a single request/response pair to asynchronously fire one
webhook-triggered workflow. The protocol is plain HTTP + JSON: no Nostr event is
submitted or returned on this route, and no NIP-98 signature is required — the caller
authenticates with a bearer secret embedded in the workflow's own definition instead.
This is one narrow member of the deliberately small HTTP surface AGENTS.md describes
alongside the Nostr-first WebSocket API; it exists specifically because an external
webhook sender cannot sign Nostr events.

## Operations

| Operation | Defined in | Summary |
|---|---|---|
| `POST /hooks/{id}` | `crates/buzz-relay/src/api/bridge.rs#workflow_webhook` (registered at `crates/buzz-relay/src/router.rs:132`) | Authenticates a webhook secret against the workflow named by `{id}` (a workflow UUID) and, if the workflow is enabled and has a webhook trigger, creates and asynchronously starts a workflow run. |

Only one HTTP operation exists on this route. The workflow's own *creation* — the
`kind:30620` Nostr command event handled by `handle_workflow_def`
(`crates/buzz-relay/src/handlers/command_executor.rs:641-814`), which is where a
workflow first gains a webhook trigger and where its secret is generated and returned
to the caller exactly once — is a different interface and is out of scope here; see
*Boundary* below.

## Contract and stability

**Inputs.** Path parameter `{id}`: the workflow's UUID, parsed with
`uuid::Uuid::parse_str`. Authentication: an `X-Webhook-Secret` request header
(preferred) or a `?secret=` query parameter (the handler prefers the header because,
per its own doc comment, "headers aren't logged by most proxies"). Body: an optional
JSON object; every top-level key becomes a `webhook_fields` entry available to the
workflow's step templates, alongside a `channel_id` field taken from the workflow row
itself, not from the request.

**Outputs.** A successful call returns `202 Accepted` immediately, with body
`{"run_id": "<uuid>", "workflow_id": "<uuid>", "status": "pending"}`. This is not the
run's outcome — execution is spawned onto a detached async task after the response is
sent. A caller that needs the eventual result must poll
`GET /workflows/{workflow_id}/runs` or `GET
/workflows/{workflow_id}/runs/{run_id}/approvals` (`crates/buzz-relay/src/api/workflows.rs`),
a separate, NIP-98-authenticated read surface over the same `workflow_run` rows. The
run's terminal state is one of `buzz_db::workflow::RunStatus`'s six values (`Pending`,
`Running`, `WaitingApproval`, `Completed`, `Failed`, `Cancelled`); a `Failed` run
carries a `WorkflowRunFailure { code, message }`.

**Errors.** All error bodies use the relay's standard `{"error": "<msg>"}` envelope.

| Status | Condition |
|---|---|
| 400 Bad Request | `{id}` is not a valid UUID; the workflow's trigger is not `TriggerDef::Webhook`; the request body is present but not valid JSON. |
| 401 Unauthorized | The workflow has no stored webhook secret (message directs the caller to re-save the workflow); or the provided secret does not match the stored one. |
| 404 Not Found (generic `"workflow not found"`) | The request's `Host` header maps to no configured community; the workflow UUID does not exist in that community; the workflow is disabled or not `Active`; the workflow has no `channel_id`; or the owner's current channel authority recheck (`check_owner_authority`) fails. All of these collapse to the same message deliberately, so an unauthenticated caller cannot distinguish "wrong host," "wrong workflow id," and "workflow exists but its owner lost access" from each other. |
| 500 Internal Server Error | A corrupt stored workflow definition fails to deserialize, or the database insert for the new run fails. |

**Authentication and authorization.** This route carries no NIP-98 signature
requirement — it is the one route in the router table's Nostr HTTP bridge section
explicitly commented "secret-authenticated, no NIP-98." The webhook secret
authenticates the *caller*, not a specific person; the run itself then executes with
the *workflow owner's* standing authority, which is why `check_owner_authority` is
re-verified on every call (SEC-006) rather than trusted once at workflow-creation
time. Community scoping is by request `Host` header, resolved through
`bind_community`, exactly like every other HTTP endpoint on this relay.

**Versioning and compatibility.** There is no separate version number for this
endpoint's contract. The webhook secret lives inside the workflow definition's own
JSON (under a `_webhook_secret` key) and is covered by that definition's
`definition_hash`, per the documented hash-ordering contract in `webhook_secret.rs`'s
module doc comment: the secret must be injected before the hash is computed, or the
stored hash silently stops matching the stored definition.

**Ordering and idempotency.** No idempotency key exists on this route. Every request
that passes authentication and the owner-authority recheck unconditionally inserts a
new `workflow_run` row and starts a new execution — a duplicate delivery of the same
webhook event (for example, a retry from the caller's own sending system) produces a
duplicate run rather than being deduplicated by the relay (INFERENCE, high confidence:
no dedup key, cache, or lookup-before-insert was found guarding `create_workflow_run`
on this path).

**Authoritative machine/spec representation.** None exists. No OpenAPI, AsyncAPI, or
other machine-readable document describes this endpoint anywhere in the repository;
the route registration (`router.rs:132`) and the handler function
(`bridge.rs#workflow_webhook`) are this contract's sole authoritative source.

**Example — valid call.**

```
POST /hooks/3fa85f64-5717-4562-b3fc-2c963f66afa6 HTTP/1.1
Host: community.example.com
X-Webhook-Secret: <webhook secret>
Content-Type: application/json

{"reason": "build finished", "status": "green"}
```

Response, assuming the workflow exists, is enabled, has a webhook trigger, and the
owner still holds channel authority:

```
202 Accepted
{"run_id": "…", "workflow_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6", "status": "pending"}
```

**Example — failure call.** The same request with a wrong or missing
`X-Webhook-Secret` (and no matching `?secret=` fallback):

```
401 Unauthorized
{"error": "authentication failed"}
```

An unknown workflow UUID, or one belonging to a different community's host, returns
the same generic:

```
404 Not Found
{"error": "workflow not found"}
```

## Boundary

This node does not describe:
- **Workflow creation or definition** — the `kind:30620` Nostr command event handled
  by `handle_workflow_def`, including how a workflow first gains a webhook trigger,
  how its secret is generated and returned exactly once, and how updates preserve an
  existing secret. That is a separate interface (a Nostr event-kind door, not this
  HTTP door) and belongs in its own future corpus node.
- **`GET /workflows/{workflow_id}/runs` and `/runs/{run_id}/approvals`** — the
  NIP-98-authenticated read endpoints a caller uses to observe a triggered run's
  eventual outcome. They are mentioned above only to show where this endpoint's
  `run_id` output leads; their own auth model, pagination, and response shape are a
  different interface's contract.
- **The workflow execution engine itself** (`buzz-workflow`'s step execution,
  `execute_from_step`, action types such as `call_webhook`) — this node covers only
  the HTTP trigger door, not what happens inside a run once started.
- **A full parameter-by-parameter catalogue** of every possible `webhook_fields` key
  a workflow author might reference in a step template — that depth, if the corpus
  ever builds a reference-style catalogue node, is separate from this interface-level
  description.

## Relationships

None declared. No sibling `interfaces/**` or event-kind-shaped node exists anywhere
in the corpus tree on `origin/launchpad` at the recorded revision — this is the first
node under `launchpad/docs/corpus/interfaces/`, confirmed by enumerating
`launchpad/docs/corpus/**/*.md` before drafting. A `relationships[].target` naming an
id no node in the corpus carries is a hard validation error, so none is declared. A
future `kind:30620` workflow-definition node, once it exists, is a natural
`references` target for this node (the two interfaces share the same workflow row and
the same webhook-secret field) — that edge is left for whichever node merges second
to add.

## Scope and omissions

**This node covers** the `POST /hooks/{id}` HTTP route: its request shape, its
tenant-binding and authentication path, every distinct error condition the handler
produces and the status code each maps to, the SEC-006 owner-authority recheck, the
async-execution response shape, the absence of an idempotency mechanism, and where a
caller goes to observe a triggered run's eventual outcome.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Workflow creation/definition (`kind:30620`, `handle_workflow_def`) | A future corpus node for that Nostr command interface |
| `GET /workflows/{workflow_id}/runs` and `/runs/{run_id}/approvals` | A future corpus node for that read interface |
| The workflow execution engine's internal step/action semantics | `buzz-workflow`'s own future corpus coverage |
| The front-matter contract itself | `launchpad/docs/corpus/schema/node.schema.json` |
| Creating, updating, and retiring a corpus node procedurally | `launchpad/docs/corpus/AGENTS.md` |

**Expected but not verified when this node was written:**
- **The `d`-tag-versus-server-generated workflow-id story was not resolved.**
  `crates/buzz-test-client/tests/conformance_multitenant.rs`'s `workflows` module
  comments state "the server *generates* the workflow id ... it is not the `d` tag,"
  and its test event carries no `d` tag at all, while `handle_workflow_def`
  (`command_executor.rs:648-651`) reads the workflow id via `extract_d_tag(event)` and
  fails the whole request when no `d` tag is present. Both cannot be true as stated
  without something upstream of `handle_workflow_def` synthesizing a `d` tag before
  ingestion, which was not located. Since workflow creation is out of this node's
  scope (see *Boundary*), this inconsistency is named here rather than resolved, so a
  future workflow-creation node inherits it rather than it silently disappearing.
- **No live end-to-end HTTP call against a running relay was made.** All claims above
  are read from the handler's source and the one cross-tenant conformance test found;
  no manual `curl` round trip against a running relay instance was performed to
  confirm the exact response bytes.
