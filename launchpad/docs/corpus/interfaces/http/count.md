---
id: interfaces-http-count
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
  - statement: "buzz-relay's router registers POST /count against api::bridge::count_events, alongside POST /events -> submit_event and POST /query -> query_events, as part of the 'Nostr HTTP bridge (NIP-98 auth)' route group."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs"
  - statement: "Root AGENTS.md documents POST /count as one of the relay's narrow HTTP surface endpoints, described as 'Nostr COUNT filters over HTTP', alongside POST /events and POST /query."
    entry_class: FACT
    evidence:
      - "AGENTS.md"
  - statement: "count_events (the HTTP handler) requires NIP-98 request signing: it derives the expected URL from the request's tenant-bound host via nip98_expected_url(state.config.relay_url, tenant, \"/count\"), then calls verify_bridge_auth with method \"POST\", that URL, and the raw request body, returning 401 Unauthorized on any auth failure (missing header, bad base64/UTF-8, invalid NIP-98 event JSON, or a signature that does not verify)."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs"
  - statement: "verify_bridge_auth accepts either an `Authorization: Nostr <base64 NIP-98 event>` header (production path, checked against buzz_auth::verify_nip98_event) or, only when the deployment's require_auth_token config is false, a dev-mode `X-Pubkey: <hex>` header with no signature check and no replay tracking (zero event id)."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs"
  - statement: "A successfully NIP-98-authenticated request still has its signed event id checked for replay via check_nip98_replay, which calls a shared, community-scoped Redis-backed Nip98ReplayGuard (try_mark with a TTL); a second use of the same signed event returns 401 'NIP-98: replay detected', and any guard error also fails closed with 401 rather than admitting the request."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs"
  - statement: "After NIP-98 auth and replay checks, count_events_authed calls enforce_http_admission (a per-principal, per-tenant rate limiter keyed on LimitType::ApiCalls) before doing any further work, returning 429 Too Many Requests on quota exceeded or 503 Service Unavailable if the shared admission backend is unreachable."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs"
  - statement: "count_events_authed additionally enforces relay membership via super::relay_members::enforce_relay_membership, reading an optional X-Auth-Tag request header, before parsing the request body as filters."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs"
  - statement: "The request body is deserialized as `Vec<nostr::Filter>` (a JSON array of one or more standard Nostr filter objects); a body that fails to deserialize returns 400 Bad Request with an 'invalid filters' message naming the serde error."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs"
  - statement: "A successful response is `200 OK` with a JSON body of the single shape `{\"count\": <non-negative integer>}`, the sum of matching-event counts across every filter in the request array; an error response is `{\"error\": \"<message>\"}` at the corresponding non-2xx status, and an internal error deliberately replaces its real message with the fixed string 'internal server error' in the response while logging the real cause server-side only."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs"
      - "crates/buzz-relay/src/api/mod.rs"
  - statement: "Before counting, the request is rejected 400 Bad Request ('too many explicit channels') if its filters name more distinct channel ids than extract_channel_ids_from_filters_limited allows, and 403 Forbidden if any filter fails p_gated_filters_authorized, engram_filters_authorized, or author_only_filters_authorized -- the same three read-authorization gates the WebSocket REQ/COUNT handlers apply, reused here rather than reimplemented for HTTP."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs"
      - "crates/buzz-relay/src/handlers/req.rs"
  - statement: "p_gated_filters_authorized treats an omitted `kinds` field on a filter as if it could match any p-gated kind (KIND_AGENT_OBSERVER_FRAME, KIND_MEMBER_ADDED_NOTIFICATION, KIND_MEMBER_REMOVED_NOTIFICATION, KIND_GIFT_WRAP = 1059, KIND_DM_VISIBILITY, KIND_AGENT_TURN_METRIC), so a kindless filter is rejected with 403 unless its `#p` tag is present and pins the caller's own authenticated pubkey -- the same 'omitting kinds triggers the p-gate' behavior this repository's own AGENTS.md documents as a common gotcha for relay queries generally, confirmed here at the /count endpoint specifically."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs"
      - "crates/buzz-core/src/kind.rs"
  - statement: "Access is further scoped per channel: for a filter naming specific channels via `#h`, only channels the caller's cached accessible-channel set contains are counted (others are silently skipped, not errored); for a filter naming no channel, the query is scoped in SQL to exactly the caller's accessible channel set plus global (channel-less) events, mirroring the WebSocket REQ/COUNT enforcement rather than duplicating a second policy."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs"
  - statement: "When a filter's constraints are fully pushable to SQL (filter_fully_pushable) and it cannot match author-only, result-gated, or shared-gated kinds it doesn't already narrow to the caller, count_events routes to a single SQL COUNT via count_events_routed. Otherwise it falls back to fetching a bounded candidate set via query_events_routed_bounded and post-filtering per event with buzz_core::filter::filters_match plus event_visible_to_reader; if that bounded fetch is exhausted (count_fallback_exceeded), the request is rejected 400 Bad Request with 'count filter requires narrower constraints' rather than silently under-counting."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs"
  - statement: "The route is registered as the bare path `/count` with no version segment (e.g. no `/v1/count`), and no other version marker (header, query parameter) appears anywhere in count_events or count_events_authed -- the endpoint's compatibility posture is whatever the current filter/response shape happens to be, not an explicitly versioned contract."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs"
      - "crates/buzz-relay/src/api/bridge.rs"
  - statement: "The endpoint is a pure read with no persisted side effect from the count operation itself, and returns one aggregate integer rather than an ordered list, so no result-ordering guarantee applies the way it would for /query; NIP-98 replay rejection is an auth-layer property of the signed request envelope, not an ordering or idempotency property of the COUNT semantics -- reissuing a *freshly signed* request for the same filters against an unchanged data set returns the same count."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs"
    confidence: 0.75
  - statement: "The WebSocket protocol's COUNT client message and CLOSED/COUNT server responses are both documented in this repository's own code as implementing NIP-45 ('NIP-45 COUNT handler', 'A COUNT message requesting aggregate counts (NIP-45)', 'Format a COUNT response (NIP-45)'), and handlers/count.rs's handle_count applies the identical read-authorization and channel-scoping logic (p-gate, engram gate, author-only gate, accessible-channel narrowing, fully-pushable-vs-fallback split) that count_events_authed applies for HTTP -- the HTTP endpoint is an alternate transport for the same NIP-45 semantics, not an independently designed contract."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/count.rs"
      - "crates/buzz-relay/src/protocol.rs"
      - "crates/buzz-relay/src/handlers/req.rs"
  - statement: "buzz-cli's BuzzClient has a count() method that POSTs to {relay_url}/count with a NIP-98-signed request built the same way as its query_multi sibling, but it is marked #[allow(dead_code)] and is not wired to any clap subcommand as of this revision -- the HTTP endpoint currently has no exposed buzz-cli command surface, unlike /query and /events."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/client.rs"
  - statement: "architecture-containers-cli, already merged to origin/launchpad, documents buzz-cli's outbound HTTP surface as including POST /count among a small fixed set of relay paths, and separately documents the relay router registering /count against api::bridge::count_events -- the same route and handler this node documents in depth."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/containers/cli.md"
---

# HTTP `POST /count`: interface

This node documents the boundary between an HTTP client and `buzz-relay` at
`POST /count`: a client sends a JSON array of Nostr filter objects in the
request body, authenticated with a NIP-98 signed event, and the relay
responds with a single aggregate count of matching events the caller is
authorized to see. It is one of three generic Nostr-bridge HTTP endpoints
(`/events`, `/query`, `/count`) this repository's root `AGENTS.md` documents
as the relay's deliberately narrow HTTP surface, and it exists specifically
so a caller without a live WebSocket connection can still get a NIP-45
aggregate count.

## Operations

| Operation | Defined in | Summary |
|---|---|---|
| `POST /count` | `crates/buzz-relay/src/router.rs` route table; handler `crates/buzz-relay/src/api/bridge.rs::count_events` (thin wrapper) and `count_events_authed` (the actual logic) | Accepts a JSON array of Nostr filter objects, returns `{"count": <u64>}` summed across all filters, subject to the same channel/kind read-authorization gates as the WebSocket `REQ`/`COUNT` path. |
| NIP-45 COUNT (WebSocket sibling, cited for contrast only) | `crates/buzz-relay/src/handlers/count.rs::handle_count`, `crates/buzz-relay/src/protocol.rs::RelayMessage::count` | The WebSocket transport for the same NIP-45 semantics; shares the p-gate/engram/author-only/channel-scoping helpers in `crates/buzz-relay/src/handlers/req.rs` with the HTTP path documented here rather than a second copy of that logic. |

## Contract and stability

**Authentication.** Every request must carry NIP-98 auth (`Authorization: Nostr
<base64-encoded signed kind:27235 event>`), verified against a URL derived
from the request's tenant-bound `Host` header (`nip98_expected_url`), not a
single deployment-wide URL — a NIP-98 event signed for one community's host
does not authenticate against another. A dev-only `X-Pubkey: <hex>` header is
accepted in place of NIP-98 when the deployment's `require_auth_token` config
is `false`; that path skips signature verification and replay tracking
entirely and must not be assumed present in production. `X-Auth-Tag` is
accepted as an optional additional header enforced by relay-membership logic
shared with the other bridge endpoints.

**Ordering of gates.** NIP-98 auth -> NIP-98 replay check -> admission
(rate-limit) -> relay-membership enforcement -> filter parsing -> explicit-
channel-count limit -> p-gate / engram-gate / author-only-gate -> per-filter
channel-access and count execution. A caller cannot reach any later gate by
failing an earlier one; each returns immediately.

**Inputs.** Request body is a JSON array of standard Nostr filter objects
(`ids`, `authors`, `kinds`, `since`, `until`, `limit`, `#`-prefixed tag
filters, etc. — the same `nostr::Filter` shape `/query` and WebSocket `REQ`
use). An empty array is valid and sums to zero matches. Per this repository's
own documented gotcha, a filter that omits `kinds` is treated as potentially
matching every p-gated kind and is rejected 403 unless its `#p` tag pins the
caller's own pubkey.

**Outputs.** Success: `200 OK`, body `{"count": <non-negative integer>}` —
one field, no envelope beyond that. This is the only success shape; there is
no paginated or partial-count response.

**Errors.** All error responses are `{"error": "<message>"}` at a non-2xx
status: `400` (malformed filter JSON, too many explicit channels, or a
non-pushable filter whose fallback candidate set exceeded its bound), `401`
(missing/invalid NIP-98 auth, or NIP-98 replay), `403` (p-gate / engram-gate /
author-only-gate rejection, or relay-membership rejection), `404` (no
community bound to the request host), `429` (rate limit), `500` (internal —
message is the fixed string `"internal server error"`, with the real cause
logged server-side only), `503` (shared admission backend unavailable).

**Versioning/compatibility.** The path carries no version segment and the
handler carries no version header or parameter; there is no separate
versioned contract to break against, only the current filter/response shape.

**Ordering/idempotency.** The response is a single aggregate integer, not an
ordered list, so `/query`'s deterministic-ordering concerns do not apply
here. The count operation itself has no persisted side effect; NIP-98 replay
rejection is a property of reusing one *signed request envelope*, not a
property of the COUNT operation's own idempotency — a freshly signed request
for the same filters against an unchanged data set returns the same count.

**Authoritative specification.** [NIP-45](https://github.com/nostr-protocol/nips/blob/master/45.md)
defines the COUNT semantics this endpoint implements; this repository's own
code (`handlers/count.rs`, `protocol.rs`) names NIP-45 directly rather than
this node re-describing the wire format.

## Boundary

This node does not describe:
- The WebSocket `REQ`/`COUNT` message wire format itself, or any single
  Nostr event kind's own tag shape/content semantics — those belong to
  NIP-01/NIP-29/NIP-45 and to each kind's own event-kind node (`kind.rs`),
  not restated here.
- A field-by-field, parameter-by-parameter catalogue of every filter field
  `nostr::Filter` supports — that is `/query`'s own filter grammar (NIP-01),
  common to all three bridge endpoints, and out of this node's depth per
  `corpus-template-interface`'s own stated boundary against reference-depth
  cataloguing.
- `buzz-cli`'s command surface — `count()` exists in `BuzzClient` but is
  currently dead code with no subcommand; wiring one is a product decision,
  not something this documentation node decides or performs.

## Relationships

- `implements: corpus-template-interface` — this is the first corpus node
  drafted from that template, matching the template's own stated preference
  for `implements` (not `references`) as the optional self-link once the
  template is merged (it is, on `origin/launchpad`).

No other relationship is declared. `/query` and `/events` are this
endpoint's siblings in the same route group, but neither has a corpus node
on `origin/launchpad` as of this revision (confirmed via `git ls-tree -r
--name-only origin/launchpad -- launchpad/docs/corpus`), so no edge to
either is safe to declare yet, per `AGENTS.md`'s rule that a relationship
target must already resolve on the branch being merged into.

## Scope and omissions

**This node covers** the `POST /count` HTTP endpoint's authentication order,
request/response shapes, error behavior, the read-authorization gates it
shares with the WebSocket COUNT path, its lack of API versioning, and its
relationship to NIP-45.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The NIP-45 wire specification itself | [nostr-protocol/nips#45](https://github.com/nostr-protocol/nips/blob/master/45.md) |
| `nostr::Filter`'s full field grammar (shared across `/query`, `/events`, `/count`, and WebSocket `REQ`) | NIP-01, and a future `/query` interface node if one is drafted |
| A single Nostr event kind's own wire contract (e.g. what a p-gated kind's tags mean) | that kind's own event-kind node, per `corpus-template-interface`'s boundary, none yet drafted |
| Whether `buzz-cli`'s dead-code `count()` should be wired to a subcommand | a future implementation issue, not this documentation task |

**Expected but not verified when this node was written:**
- No live HTTP request was sent against a running relay to observe the
  documented status codes and JSON shapes end-to-end; every claim above is
  read directly from the handler source rather than from an executed
  request/response pair.
- No dedicated integration test exercising `POST /count` specifically was
  found in `crates/buzz-relay` or `crates/buzz-test-client/tests`; the
  examples below are constructed from the handler's own code paths, not
  copied from an existing passing test.

## Examples

**Valid request** (kinds present, so the p-gate does not apply):

```
POST /count HTTP/1.1
Host: <community-host>
Authorization: Nostr <base64-encoded NIP-98 event>
Content-Type: application/json

[{"kinds": [1], "authors": ["<hex-pubkey>"]}]
```

Response:

```
200 OK
{"count": 3}
```

**Failure example** (kinds omitted on a filter that could match a p-gated
kind, e.g. `KIND_GIFT_WRAP = 1059`, with no `#p` tag pinning the caller):

```
POST /count HTTP/1.1
Host: <community-host>
Authorization: Nostr <base64-encoded NIP-98 event>
Content-Type: application/json

[{"authors": ["<hex-pubkey>"]}]
```

Response:

```
403 Forbidden
{"error": "restricted: p-gated kinds require #p tag matching your pubkey"}
```
