---
id: interfaces-http-events
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
  - statement: "`POST /events` is registered on the relay's axum router as `api::bridge::submit_event`, in the same route table as `/query` and `/count`, under the router's Nostr-HTTP-bridge (NIP-98 auth) group; that group is layered with a combined 1 MiB request-body limit (`RequestBodyLimitLayer::new(1024 * 1024)`)."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs:72"
      - "crates/buzz-relay/src/router.rs:142"
  - statement: "`submit_event` binds the request to a community by resolving the `Host` header via `tenant::bind_community` before any tenant-scoped write or auth check; an unmapped or empty host fails closed with a generic 404 (\"relay: no community is configured for this host\") that never echoes the submitted host."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs:703-723"
  - statement: "Authentication is NIP-98 by default: an `Authorization: Nostr <base64>` header decodes to a signed Nostr event whose id/pubkey/signature and bound `url`+`method`+`body` are checked by `buzz_auth::verify_nip98_event` against a URL built from the resolved tenant host plus `/events`; any failure (bad base64, bad UTF-8, unparseable event JSON, verification failure) returns 401. When `require_auth_token` is false, an `X-Pubkey: <hex>` header is accepted instead as a dev-mode fallback with no signature check, and is given a zero-valued event id so no replay tracking applies to it."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs:62-128"
  - statement: "The NIP-98 auth event's id is claimed against a shared, community-scoped replay guard (`try_mark` with a TTL) before the request body is parsed; a second submission carrying the same auth event id within the TTL window is rejected 401 (\"NIP-98: replay detected\"), and the guard itself being unavailable also fails closed to 401 (\"NIP-98: replay check unavailable\") rather than admitting the request."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs:136-176"
  - statement: "After auth, the request is admission-checked per authenticated pubkey against a configured per-minute API-call rate limit; exceeding it returns 429 (\"rate-limited: quota exceeded; retry in Ns\"), and the shared admission backend being unavailable returns 503 (\"rate-limited: shared admission unavailable\") rather than allowing the write through."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs:24-56"
  - statement: "The request body is parsed as a single `nostr::Event` JSON object; a parse failure returns 400 with the serde error's message in the response body, while the server log for that outcome carries only the bounded, structured `category`/`line`/`column` fields rather than the raw serde error text, because that text can otherwise embed attacker-controlled input at unbounded size."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs:866-888"
  - statement: "After successful parse, relay membership is enforced (with a NIP-OA `x-auth-tag` header fallback for owner materialization) before the event reaches the shared ingest pipeline; a membership failure returns the error status/body that check produces."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs:890-916"
  - statement: "Both `submit_event` (via its `submit_event_authed` helper) and the WebSocket EVENT handler `handle_event` construct a transport-specific `IngestAuth` value and then call the identical `ingest_event()` function; this is the single shared validation/storage/fan-out pipeline for both transports, not two independent implementations."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs:918-925"
      - "crates/buzz-relay/src/handlers/event.rs:761"
      - "crates/buzz-relay/src/handlers/ingest.rs:2100-2105"
  - statement: "An HTTP-authenticated request is granted `Scope::all_known()` inside `IngestAuth::Http` regardless of the caller's actual relay role; the interface's real access control for channel-scoped content is enforced separately, by the membership/channel-access checks that run before and inside `ingest_event`, not by scope restriction on the HTTP door itself."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs:918-923"
  - statement: "Inside `ingest_event`, a submitted event is rejected before its signature is even checked if its kind is classified relay-only (`is_relay_only_kind`) or is one of the kinds this code path marks WebSocket-only; only after those gates does `verify_event` (SHA-256 id recomputation plus Schnorr signature check, run via `tokio::task::spawn_blocking` so it cannot block the async executor) run, followed by a ±900-second server-time drift check and a 256 KB content-size cap, both of which reject with `invalid:`-prefixed messages mapped to HTTP 400 by the caller."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:2195-2240"
  - statement: "`ingest_event`'s error type has exactly three variants and the HTTP bridge maps them one-to-one: `Rejected` to 400 (client/event error), `AuthFailed` to 403, `Internal` to 500 with a generic \"internal server error\" body — the real internal message is logged server-side (via `internal_error`) but never returned to the caller."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:383-392"
      - "crates/buzz-relay/src/api/bridge.rs:951-966"
      - "crates/buzz-relay/src/api/mod.rs:21-28"
  - statement: "A successful ingest returns HTTP 200 with a JSON body of exactly `{event_id, accepted, message}` — `event_id` hex-encoded, `accepted` a boolean, `message` an optional annotation string (empty on a normal fresh insert)."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs:926-931"
      - "crates/buzz-relay/src/handlers/ingest.rs:374-381"
  - statement: "Submission is idempotent at the level the wire format allows: for a plain (non-replaceable) kind, resubmitting a byte-identical signed event yields the same 200 response with `accepted: true, message: \"duplicate:\"` rather than a second stored row, because `was_inserted` is false on the second call."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:3192-3198"
  - statement: "For NIP-16 replaceable and NIP-33 parameterized-replaceable kinds, the store resolves concurrent writes to the same coordinate under a Postgres advisory transaction lock, and the highest `created_at` wins (with the lowest event id breaking a same-second tie); the parameterized path's own status enum (`ParameterizedReplaceStatus`) distinguishes `Inserted`, `Duplicate` (exact event already accepted) and `Superseded` (a newer or tie-winning event already dominates it) internally, but `replace_parameterized_event`'s public return collapses all three non-`Inserted` outcomes to the same `was_inserted = false`, so the HTTP response cannot distinguish \"this exact event was already stored\" from \"a newer write already won\" — both surface identically as `{accepted: true, message: \"duplicate:\"}`."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/replaceable.rs:14-27"
      - "crates/buzz-db/src/store/replaceable.rs:547-585"
      - "crates/buzz-relay/src/handlers/ingest.rs:3133-3198"
  - statement: "There is no version number or version header in the `/events` request or response contract itself; compatibility is carried by the Nostr event envelope's own `kind` field and by NIP-01's event id / signature scheme, which `verify_event` implements directly rather than through a versioned transport wrapper."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs:703-968"
      - "crates/buzz-relay/src/handlers/ingest.rs:2195-2240"
    confidence: 0.75
  - statement: "NIP-01 defines the canonical Nostr event JSON structure (`id`, `pubkey`, `created_at`, `kind`, `tags`, `content`, `sig`) and the id/signature scheme `verify_event` implements; it is the authoritative machine/spec representation `POST /events` accepts on the wire, and this repository holds no separate OpenAPI/AsyncAPI document describing this route."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "nostr-protocol/nips NIP-01 (https://github.com/nostr-protocol/nips/blob/master/01.md); repository-side confirmation that no such document exists came from opening router.rs, bridge.rs and ingest.rs directly rather than from a fetched or grepped absence-check in this session"
  - statement: "This repository's root AGENTS.md documents buzz-cli's own write-response contract as ending in \"5=write conflict (NIP-33 LWW)\" for CLI exit codes, but that exit-code interpretation is `buzz-cli`'s own client-side mapping over the raw `/events` JSON body, not a distinct field or status code this HTTP interface itself returns — the raw response for a losing NIP-33 write is the same `{accepted: true, message: \"duplicate:\"}` described above, observed directly in `ingest.rs`, not a `5`/409-shaped signal at this layer."
    entry_class: INFERENCE
    evidence:
      - "AGENTS.md:217-219"
      - "crates/buzz-relay/src/handlers/ingest.rs:3192-3198"
    confidence: 0.8
relationships:
  - type: references
    target: architecture-flows-http-event-submission
  - type: references
    target: architecture-flows-event-ingestion
---

# HTTP `POST /events`: interface

The HTTP bridge door onto the relay's single Nostr event-acceptance pipeline. A
caller who cannot or does not want to hold a WebSocket connection open — a script,
a batch job, a CLI invocation — signs a Nostr event exactly as it would for the
WebSocket `["EVENT", ...]` frame, then sends it as a JSON body to `POST /events`
authenticated with NIP-98 (`Authorization: Nostr <base64>`) or, in dev-mode
deployments, an `X-Pubkey` header. The relay authenticates and admits the HTTP
request, then hands the parsed event to the exact same `ingest_event()` function
the WebSocket path uses — this route is a second door into one room, not a
parallel implementation of event acceptance.

## Operations

| Operation | Defined in | Summary |
|---|---|---|
| `POST /events` | `crates/buzz-relay/src/router.rs:72` (route), `crates/buzz-relay/src/api/bridge.rs::submit_event` (handler) | Submit one signed Nostr event; returns `{event_id, accepted, message}` on success. |

There is exactly one operation on this interface. `submit_event` is a thin wrapper
around `submit_event_authed`, which performs admission, NIP-98 replay-marking, JSON
parse, relay-membership enforcement, and finally the shared `ingest_event()` call —
see `architecture-flows-http-event-submission` and `architecture-flows-event-ingestion`
for the step-by-step flow through that pipeline; this node does not restate it.

## Contract and stability

**Request.** `Content-Type: application/json` body containing one signed
`nostr::Event` JSON object (NIP-01 shape). `Authorization: Nostr <base64-encoded
NIP-98 event>` is the production auth header; an `X-Pubkey: <hex>` header is
accepted instead only when the deployment has `require_auth_token` set false. An
optional `x-auth-tag` header carries a NIP-OA fallback for relay-membership
resolution. Body size is capped at 1 MiB by the router's shared limit layer over
this route group.

**Response, success.** HTTP 200, JSON `{"event_id": "<hex>", "accepted": true|false,
"message": "<string, often empty>"}`. `accepted: true` with a non-empty `message`
(`"duplicate:"`) signals a no-op write — the submitted event, or a losing
NIP-33/NIP-16 write superseded by one that already won, was not newly stored; the
response body does not distinguish those two cases from each other (see the
evidence ledger above).

**Response, failure.** HTTP 400 for a malformed/rejected event (bad JSON, failed
signature/id verification, timestamp more than 900 seconds from server time,
content over 256 KB, a relay-only or WebSocket-only kind, or any other
`ingest_event` rejection); 401 for NIP-98 auth failure (bad signature, URL/method/
body mismatch, replay detected, replay guard unavailable) or missing auth
entirely; 403 for a scope/membership auth failure surfaced by `ingest_event` or by
the relay-membership check; 404 if the request's `Host` header does not resolve to
a configured community; 429 if the caller's rate-limit quota is exceeded; 503 if
the shared admission backend is unavailable; 500 for any other internal error,
returned as a generic `{"error": "internal server error"}` body with the real
cause logged server-side only.

**Ordering.** No ordering guarantee is made across separate `POST /events` calls;
each call is validated and stored independently. Within one event's own
replaceable/parameterized-replaceable coordinate, the highest `created_at` wins
(ties broken by lowest event id), enforced by a per-coordinate Postgres advisory
lock so concurrent writers to the same coordinate serialize rather than race.

**Idempotency.** Resubmitting an already-accepted, byte-identical signed event is
safe and returns the same accepted/duplicate response rather than a second stored
row. This is a property of the Nostr event's own content-addressed id, not of an
idempotency key this interface adds.

**Versioning/compatibility.** The wire contract has no explicit version field;
compatibility rides on the Nostr event envelope's `kind` and NIP-01's id/signature
scheme (INFERENCE, see evidence ledger — reasoned from the absence of any version
field or header in the handler code, not from a written compatibility policy).

**Authoritative spec.** [NIP-01](https://github.com/nostr-protocol/nips/blob/master/01.md)
defines the event JSON shape and id/signature scheme this endpoint accepts and
verifies; there is no OpenAPI, AsyncAPI, or other machine-readable description of
`POST /events` itself in this repository.

### Valid example

A dev-mode submission (`X-Pubkey` auth) of a plain kind:9 channel message,
adapted from `crates/buzz-test-client/tests/e2e_nostr_interop.rs`'s
`send_rest_message` helper:

```
POST /events HTTP/1.1
Host: relay.example
X-Pubkey: <hex-encoded pubkey>
Content-Type: application/json

{"id":"...","pubkey":"...","created_at":1234567890,"kind":9,
 "tags":[["h","<channel-uuid>"]],"content":"hello","sig":"..."}
```

Expected response: `HTTP 200`, body
`{"event_id":"<hex>","accepted":true,"message":""}`.

### Failure example

A NIP-98 auth event signed for the wrong community host, adapted from
`crates/buzz-relay/src/api/bridge.rs`'s
`verify_bridge_auth_rejects_nip98_event_signed_for_wrong_communitys_host` test:
the client signs its NIP-98 auth event's `u` tag as `https://host-a.example/events`,
then presents that auth event at a request whose `Host` header resolves to
`host-b.example`. Expected response: `HTTP 401`, body containing `"URL mismatch"`
in the `error` field — the cross-host reuse is rejected, never silently admitted
against the wrong tenant.

## Boundary

This node does not describe:
- The Nostr event kind wire contracts (tag shapes, content semantics) of any
  individual kind this endpoint can carry — those belong to that kind's own
  event-kind node, once one exists, or to `buzz-core/src/kind.rs` directly. This
  interface node covers the HTTP envelope and pipeline, not per-kind payload rules.
- The step-by-step body of the shared `ingest_event` pipeline (write-fence check,
  per-kind rejection rules, side-effect dispatch, thread-counter updates) — that
  is `architecture-flows-event-ingestion`'s subject; this node `references` it
  rather than restating it.
- The WebSocket `["EVENT", ...]` transport itself, or NIP-42 WebSocket
  authentication — a separate interface surface with its own auth scheme
  (NIP-42, not NIP-98).
- `POST /query` and `POST /count`, the two sibling routes in the same Nostr-HTTP-
  bridge route group — out of scope for this issue.
- A field-by-field, domain-expert-depth parameter catalogue in the Good Docs
  Project's API Reference sense — this node states the operation, its contract,
  and its failure modes, not an exhaustive parameter dictionary.

## Relationships

- `references: architecture-flows-http-event-submission` — the merged flow node
  documenting this route's own HTTP-transport-specific steps (tenant binding,
  NIP-98 verification, replay guard) in narrative form.
- `references: architecture-flows-event-ingestion` — the merged flow node
  documenting the shared `ingest_event` pipeline both this route and the
  WebSocket EVENT handler feed into.

Both targets are `status: draft` themselves but are present on `origin/launchpad`
at the time this node was authored, which is the bar `AGENTS.md` sets for a valid
relationship target ("already merged"), independent of the target's own status.

## Scope and omissions

**This node covers** the `POST /events` HTTP interface: its one operation, the
request/response shapes, the full authentication and admission chain (NIP-98,
dev-mode `X-Pubkey`, replay detection, rate limiting, relay membership), the
error-status taxonomy the shared ingest pipeline maps onto HTTP, ordering and
idempotency behavior including the replaceable/parameterized-replaceable
collapse noted above, and the absence of a machine-readable spec document beyond
NIP-01 itself.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Individual event kind wire contracts | Each kind's own event-kind node, none of which exists yet |
| The full `ingest_event` pipeline body | `architecture-flows-event-ingestion` |
| The HTTP-transport-specific submission steps in narrative form | `architecture-flows-http-event-submission` |
| `POST /query` and `POST /count` | Out of scope for this task |
| WebSocket transport and NIP-42 auth | A separate interface node, not yet drafted |

**Expected but not verified when this node was written:**
- **The exact production value of the admission rate limit** (`human_api_calls_per_min`)
  was not looked up in any deployment configuration — the mechanism and its
  status-code behavior were verified in code, not the number itself.
- **NIP-01's own specification text was read via its GitHub-hosted Markdown, not
  fetched and independently re-verified against the IETF/nostr-protocol
  organization's canonical source beyond that single link.**
- **Whether any client library other than this repository's own test helpers and
  `buzz-cli` actually relies on the specific `"duplicate:"` message string** was
  not checked; the claim here is only that the relay produces it, not that every
  consumer parses it the same way.
