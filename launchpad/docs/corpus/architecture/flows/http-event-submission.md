---
id: architecture-flows-http-event-submission
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
  - statement: "`POST /events` is registered on the relay's HTTP router as `api::bridge::submit_event`, alongside `/query` and `/count`, under the router's Nostr-HTTP-bridge (NIP-98 auth) section."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs"
  - statement: "The router applies a combined 1 MiB request-body limit (`RequestBodyLimitLayer::new(1024 * 1024)`) over the API router that carries `/events`."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs"
  - statement: "`ingest_event` documents itself as the transport-neutral seam both WebSocket `[\"EVENT\", ...]` frames and HTTP `POST /events` feed into: \"two doors, one room\"."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "`submit_event` resolves the request's community from the `Host` header via `tenant::bind_community` before any tenant-scoped write; an empty or unmapped host fails closed with a generic 404 that never echoes the host, and this binding happens before NIP-98 auth is checked."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs"
      - "crates/buzz-relay/src/tenant.rs"
  - statement: "Authentication is NIP-98: an `Authorization: Nostr <base64>` header decodes to a signed Nostr event (kind `HttpAuth`) whose id/pubkey/signature and bound `url`+`method`+`body` are verified by `buzz_auth::verify_nip98_event`; the expected URL is built from the resolved tenant host plus `/events`, binding the signed auth event to this exact request."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs"
  - statement: "When `require_auth_token` is false, an `X-Pubkey: <hex>` header is accepted as a dev-mode fallback with no signature check and a zero event id (no replay detection for that path)."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs"
  - statement: "The NIP-98 auth event's id is claimed against a replay guard (`try_mark` with a TTL) before the request body is parsed; a second submission of the same auth event id within the TTL is rejected 401 (\"NIP-98: replay detected\"), and the guard being unavailable fails closed to 401 rather than admitting the request."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs"
  - statement: "A per-principal admission/rate-limit check (`enforce_http_admission`, quota `human_api_calls_per_min`) runs before body parse; exceeding it returns 429, and the shared admission backend being unavailable returns 503 rather than admitting the request."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs"
  - statement: "Admission and replay checks are ordered ahead of JSON body parsing specifically so a 429 or replay rejection on a malformed body is still attributed to the correct outcome in the terminal log line."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs"
  - statement: "A body that fails to parse as a Nostr event returns 400; the parse-failure log line intentionally omits serde_json's `Display` error text (which embeds the offending input) and instead logs only a bounded category/line/column, while the HTTP response body still returns the full parse error message."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs"
  - statement: "After parse, relay membership is enforced (`enforce_relay_membership`, with a NIP-OA `x-auth-tag` fallback); a resolved NIP-OA owner is materialized into the tenant before the event proceeds to ingest."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs"
  - statement: "The authenticated request is handed to the shared `ingest_event` pipeline as `IngestAuth::Http { pubkey, scopes: Scope::all_known(), auth_method }`, i.e. an HTTP-authenticated principal is granted the full known scope set (channel access is enforced separately, via membership) rather than a narrower HTTP-specific scope subset."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs"
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "`ingest_event_inner` refuses the write if the event's community is not in the \"serving active\" lifecycle state (a durable community write fence checked via `buzz_deletion::store(..).is_serving_active`), ahead of any kind-specific check."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "Kind 22242 (`KIND_AUTH`) cannot be submitted as an ordinary event, and kinds 44100/44101 (member-added/member-removed notifications) are rejected as relay-signed-only, on both transports."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
      - "crates/buzz-core/src/kind.rs"
  - statement: "Kind 1059 (gift wrap, NIP-59) and kind 20001 (presence update) are rejected specifically when submitted over the HTTP transport (`auth.is_http()`), while remaining acceptable over WebSocket."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
      - "crates/buzz-core/src/kind.rs"
  - statement: "Signature verification (`verify_event`) runs in a blocking task and rejects the event on failure; the event timestamp must be within ±15 minutes of server time; event content over 256 KB is rejected; and the event's `pubkey` must equal the authenticated identity's pubkey, except for gift-wrap events (NIP-59 signs with an unrelated ephemeral key by design)."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "A required scope is computed per kind (`required_scope_for_kind`); NIP-43 relay-admin commands and leave requests additionally require a non-channel-scoped (global) token even when the event itself carries no `h` tag."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "Product feedback (kind 42000) and NIP-56 reports (kind 1984) are sidecarred into private deployment/moderation tables and never enter ordinary event storage or subscriber fan-out; both still return an `accepted: true` `IngestResult` on success."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
      - "crates/buzz-core/src/kind.rs"
  - statement: "For ordinary storable kinds, an already-seen reaction (kind:7) is detected via an atomic upsert and returns `accepted: false` with a `duplicate:` message without re-storing a second event row; replaceable and parameterized-replaceable kinds are written through dedicated atomic-replace storage calls rather than plain insert."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "A successful new-row insert emits an abstract write action (`WriteInsert` / `WriteInsertGlobal` / `WriteDuplicate`, depending on whether the event carries a channel and whether the row was newly inserted) to the conformance tracer, then calls `dispatch_persistent_event`, which enqueues an audit record synchronously and spawns the subscriber/pub-sub fan-out as a background task — the HTTP response returns before fan-out to other connections necessarily completes."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
      - "crates/buzz-relay/src/handlers/event.rs"
  - statement: "A freshly inserted threaded reply updates its thread's `reply_count`/`descendant_count` in the same database transaction as the insert, and separately triggers a best-effort, relay-signed kind:39005 live-thread-summary push so subscribed clients can update counts without refetching."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "The HTTP response on every outcome is `{event_id, accepted, message}` as JSON; `IngestError::Rejected` maps to HTTP 400, `IngestError::AuthFailed` to 401/403, and `IngestError::Internal` to 500 — the same three-way split the WebSocket transport also maps onto its own OK-frame semantics."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
      - "crates/buzz-relay/src/api/bridge.rs"
  - statement: "Rejections increment `buzz_events_rejected_total{transport=\"http\", reason=...}` (reason one of `invalid`, `auth`, `error`) and accepted stores increment `buzz_events_stored_total{kind=..., author_type=...}`, both emitted at the shared ingest seam so HTTP and WebSocket submissions are counted identically."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
      - "crates/buzz-relay/src/api/bridge.rs"
  - statement: "`crates/buzz-test-client/tests/e2e_relay.rs`'s `create_test_channel` helper exercises the accepted/success path over `POST /events` (dev-mode `X-Pubkey` auth), and its `test_client_submitted_nip43_membership_snapshots_are_rejected` test exercises the HTTP rejection path for a relay-only kind, asserting HTTP 400 and the exact `restricted: relay-only kind` message on the same event already proven rejected over WebSocket."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/e2e_relay.rs"
  - statement: "`crates/buzz-relay/src/api/bridge.rs`'s unit test `nip98_replay_guard_rejects_cross_pod_replay_on_bridge_path` exercises the replay-rejection path directly against `check_nip98_replay_with_guard`, proving the replay guard is scoped per-community (a Redis-backed guard shared across relay pods) rather than per-process."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs"
  - statement: "No test in this repository was found that exercises the admission/rate-limit (429) or shared-admission-unavailable (503) branches of `enforce_http_admission` specifically for the `/events` route; this is expected-but-unverified coverage, not a claim that the branches are untested code paths of unknown behavior."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs"
      - "crates/buzz-test-client/tests/e2e_relay.rs"
    confidence: 0.6
---

# HTTP event submission (`POST /events`)

## Overview

`POST /events` is the HTTP half of Buzz's Nostr event-submission surface: a client
signs a Nostr event and submits it over plain HTTP instead of the WebSocket relay
connection. It shares one ingestion pipeline with the WebSocket `["EVENT", ...]` path —
`ingest_event` in `crates/buzz-relay/src/handlers/ingest.rs` — so every acceptance,
rejection, storage, and fan-out rule described here also governs WebSocket-submitted
events, except where this document calls out an HTTP-specific branch.

This node documents the flow as of the recorded revision. Per-claim citations are on
each `evidence` entry above rather than restated in prose; the field-level contract
(required properties, enums, evidence-class rules) lives in
`launchpad/docs/corpus/schema/node.schema.json` and is not repeated here.

## Trigger, preconditions, termination/outcome

**Trigger:** an HTTP `POST` to `/events` on a relay host, carrying a JSON-encoded,
already-signed Nostr event as the request body.

**Preconditions:**
- The request's `Host` header must resolve to a provisioned community (row-zero
  tenant binding). An unmapped or empty host never reaches auth or event handling.
- The request must carry either a valid NIP-98 `Authorization: Nostr <base64>` header,
  or (only when the relay's `require_auth_token` config is false) an `X-Pubkey` header.
- The request body must be at most 1 MiB (enforced by the router's body-limit layer
  before the handler runs at all).

**Termination/outcome:** the request always ends in exactly one HTTP response, one of:
- `200` with `{event_id, accepted, message}` — the event was processed by the ingest
  pipeline, whether that means a genuinely new row, a no-op duplicate/dedupe outcome,
  or a private sidecar write (product feedback, reports). `accepted` distinguishes a
  new row from a duplicate; a 200 status does not by itself mean "stored".
- `400` — malformed JSON, or the ingest pipeline rejected the event's content
  (`IngestError::Rejected`).
- `401` / `403` — NIP-98 verification failed, replay was detected, the replay guard
  was unavailable, relay membership was denied, or the ingest pipeline rejected the
  event on auth/scope grounds (`IngestError::AuthFailed`).
- `404` — the request's `Host` did not resolve to any community.
- `429` — the per-principal HTTP admission quota was exceeded.
- `500` / `503` — an internal ingest failure, or the shared admission backend was
  unavailable.

There is no partial-success outcome for one event: the pipeline is a single
request/response round trip per event, and background fan-out (see below) happening
after the response has already been sent is the one place where "the response
returned" and "every downstream side effect has completed" are not the same moment.

## Ordered interactions and data/state movement

1. **Body-size gate.** The router's `RequestBodyLimitLayer` rejects bodies over 1 MiB
   before the handler runs.
2. **Tenant binding.** `submit_event` reads the `Host` header and calls
   `tenant::bind_community`, which normalizes the host and looks up its community.
   An empty or unmapped host fails closed with a generic 404 (never echoing the host).
3. **NIP-98 auth.** The expected signed URL is built from the resolved tenant's host
   plus `/events`. `verify_bridge_auth_with_options` decodes the `Authorization: Nostr`
   header, parses the embedded auth event, and calls `buzz_auth::verify_nip98_event`
   against that URL, the HTTP method, and the raw request body — binding the signature
   to this exact request, not just to the sender's identity. On success this yields the
   caller's Nostr pubkey and the auth event's id.
4. **Admission check.** `enforce_http_admission` checks the per-principal
   `human_api_calls_per_min` quota for this pubkey/tenant.
5. **Replay check.** The NIP-98 auth event's id is claimed against a TTL-scoped replay
   guard; a duplicate claim (or a store lookup failure) is rejected.
6. **Body parse.** The raw bytes are deserialized into a `nostr::Event`. Failure exits
   here with a 400 and a category/line/column-only log line (never the raw body).
7. **Relay membership.** `enforce_relay_membership` checks whether the authenticated
   pubkey is a member of the resolved community, with an `x-auth-tag` NIP-OA fallback;
   a resolved NIP-OA owner is materialized into the tenant.
8. **Handoff to the shared pipeline.** The event and an `IngestAuth::Http { pubkey,
   scopes: Scope::all_known(), auth_method }` value are passed to `ingest_event`.
9. **Serving-fence check.** `ingest_event_inner` refuses to write if the community is
   not in the active "serving" lifecycle state.
10. **Kind admissibility.** Relay-signed-only kinds (AUTH; member-added/removed
    notifications), other relay-only kinds, and (on this transport specifically)
    WebSocket-only kinds (gift wrap, presence update) are rejected here.
11. **Signature, timestamp, size, identity.** The event's own cryptographic signature
    is verified (off the async runtime, in a blocking task); its timestamp must be
    within ±15 minutes of server time; its content must be ≤256 KB; and its `pubkey`
    must match the authenticated identity (gift wrap is the one designed exception).
12. **Scope check.** A required scope is derived from the event's kind; NIP-43
    admin/leave-request kinds additionally require a non-channel-scoped token.
13. **Kind-specific routing.** Command kinds route to the command executor. Product
    feedback and NIP-56 reports are sidecarred into their own tables/queues and return
    directly, never reaching ordinary storage or fan-out.
14. **Storage.** For ordinary kinds: reactions are atomically upserted with duplicate
    detection; replaceable and parameterized-replaceable kinds go through dedicated
    atomic-replace calls; other kinds insert normally. Threaded replies update their
    thread's `reply_count`/`descendant_count` in the same transaction as the insert.
15. **Post-commit dispatch.** A successful new-row insert enqueues an audit record
    synchronously, then spawns a background task (`dispatch_persistent_event`) that
    fans the stored event out to subscribers over pub/sub, and — for a threaded reply —
    separately pushes a relay-signed kind:39005 live-thread-summary update. This is the
    one step of the flow that is **not** complete when the HTTP response is sent.
16. **Response.** The pipeline's `Ok`/`Err` result is mapped to the JSON body and
    status code described under Termination/outcome, and a single structured
    `"HTTP bridge request"` log line is emitted for every outcome (including auth,
    admission, and replay failures that return before parsing the body).

## Authentication / authorization / trust-boundary crossings

- **Host → community (row zero).** Every other decision in this flow depends on the
  community resolved from the `Host` header in step 2. This is a trust boundary: an
  unmapped host is refused before any authentication is even attempted, and the
  failure response is generic specifically so an unauthenticated caller cannot use it
  to enumerate valid hosts.
- **HTTP → Nostr identity (NIP-98).** The caller's cryptographic identity is
  established by a signed Nostr event embedded in the `Authorization` header, bound to
  this request's exact URL, method, and body. This is the crossing from "an HTTP
  request arrived" to "this Nostr pubkey sent it."
- **Dev-mode fallback.** When `require_auth_token` is false, `X-Pubkey` bypasses
  signature verification entirely. This is a deliberately weaker boundary meant for
  local/dev use, not a documented production trust posture.
- **Identity → relay membership → channel access.** A verified pubkey is not yet an
  authorized actor: relay membership (with NIP-OA fallback) is checked next, and the
  ingest pipeline separately enforces per-kind scope requirements and (for admin/leave
  commands) that the caller's token is not channel-scoped.
- **Event envelope signer vs. authenticated principal.** The pipeline distinguishes
  "who signed this HTTP request" from "who signed the event content" — they must match
  except for gift-wrap events, where NIP-59 intentionally uses an unrelated ephemeral
  signer for the outer envelope.

## Failure, abort, and rollback behavior

There is no multi-step transaction that partially commits and needs rollback from the
caller's perspective: every rejection above happens before the event's storage write,
and the storage write itself (insert, atomic reaction upsert, atomic replace) is a
single database operation reported back as accepted or not — there is no "stored then
undone" path in this flow.

- **Fail-closed, not fail-open.** Tenant binding, the replay guard, and the shared
  admission backend all fail closed: a lookup or store error on any of them rejects
  the request rather than admitting it.
- **Attribution survives early rejection.** Admission and replay checks are
  deliberately ordered ahead of body parsing so that a 429 or replay rejection on a
  malformed body is still logged with the correct status/reason, rather than being
  misattributed to a parse failure.
- **No event content in rejection logs.** A JSON parse failure logs only a bounded
  category/line/column, not the raw body — malformed input of attacker-chosen size and
  content is not reflected into the log at full size. (The HTTP response body itself
  does return the full parse error, unchanged from prior behavior.) Ingest-rejection
  reasons that can embed event-controlled tag content are truncated before logging,
  though the full message is still returned in the response body.
- **Background fan-out failure is not surfaced to the submitter.** Because
  `dispatch_persistent_event` spawns fan-out as a background task after the response
  is already prepared, a fan-out-side failure cannot change the HTTP status the caller
  already received; storage acceptance and delivery-to-subscribers are decoupled by
  design.
- **Representative verification:**
  - Success path: `crates/buzz-test-client/tests/e2e_relay.rs`'s `create_test_channel`.
  - Rejection path (relay-only kind, HTTP 400): `crates/buzz-test-client/tests/e2e_relay.rs`'s
    `test_client_submitted_nip43_membership_snapshots_are_rejected`.
  - Replay rejection, cross-pod: `crates/buzz-relay/src/api/bridge.rs`'s
    `nip98_replay_guard_rejects_cross_pod_replay_on_bridge_path`.

## Scope and omissions

**This node covers** the request/response life cycle of `POST /events`: tenant
binding, NIP-98 authentication and replay protection, admission, the shared
`ingest_event` pipeline's ordering of checks, storage, post-commit fan-out, and the
HTTP status/response-body mapping.

**It does not cover, and these are boundaries, not gaps:**
- The WebSocket `["EVENT", ...]` transport's own connection lifecycle (NIP-42
  challenge/auth, subscription management) — only the pipeline steps it shares with
  HTTP are described here.
- The full per-kind validation and authorization rule set (`required_scope_for_kind`,
  command-kind dispatch, every individual kind's storage shape) — this node describes
  the ordering and the categories of checks, not every kind's specific rule.
- `POST /query` and `POST /count`, the sibling Nostr-HTTP-bridge endpoints registered
  alongside `/events`.
- Blossom media upload/download, git smart HTTP, and workflow webhooks — separate HTTP
  surfaces on the same router.

**Expected but not verified against the current repository** (per the rule in
`launchpad/docs/corpus/AGENTS.md`'s *Creating a node* step 3): no test was found that
specifically exercises the 429 (admission quota exceeded) or 503 (admission backend
unavailable) response branches for the `/events` route. This is recorded as an
`INFERENCE` in the evidence ledger above rather than presented as a verified `FACT`,
and rather than silently omitted.
