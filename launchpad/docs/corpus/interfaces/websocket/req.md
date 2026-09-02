---
id: interfaces-websocket-req
type: interfaces-events
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision b5dd39acb7ade0a33692edaebe674a1212111dd5."
    entry_class: FACT
    evidence:
      - "commit b5dd39acb7ade0a33692edaebe674a1212111dd5"
  - statement: "A client opens a subscription by sending `[\"REQ\", <subscription_id>, <filter>...]`; the relay requires `arr.len() >= 2`, rejects an empty or missing subscription id, enforces a 256-byte NIP-11-advertised `max_subid_length`, and enforces a 10-filter NIP-11-advertised `max_filters` (more than 10 filter objects after the subscription id is rejected)."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/protocol.rs:68-98"
      - "crates/buzz-relay/src/protocol.rs:9-12"
  - statement: "The relay's NIP-11 document advertises `max_subscriptions: 1024`, `max_filters: 10`, `max_subid_length: 256`, `max_limit` equal to `buzz_db::DEFAULT_MAX_PAGE_LIMIT`, and `auth_required: true` unconditionally, because the REQ, EVENT and COUNT handlers unconditionally reject an unauthenticated connection — this is independent of the separate REST token toggle."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/nip11.rs:83-140"
  - statement: "`handle_req` requires the connection to already be `AuthState::Authenticated`; an unauthenticated REQ receives a `NOTICE` (\"auth-required: authenticate before subscribing\") followed by `[\"CLOSED\", <sub_id>, \"auth-required: not authenticated\"]`, and the subscription is never registered."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs:56-93"
  - statement: "A scoped-auth connection (one whose token carries a non-empty `scopes` set) must include `Scope::MessagesRead` or the REQ is rejected with `[\"CLOSED\", <sub_id>, \"restricted: insufficient scope\"]`; an unscoped (full) auth context is exempt from this check."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs:57-68"
  - statement: "A connection may hold at most `MAX_SUBSCRIPTIONS` (1024) live subscriptions; a REQ that would exceed this while introducing a new `sub_id` is rejected with `[\"CLOSED\", <sub_id>, \"error: too many subscriptions\"]` rather than silently evicting an older subscription."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs:25"
      - "crates/buzz-relay/src/handlers/req.rs:72-79"
  - statement: "For a community-global subscription (one whose filters carry no single consistent `#h` channel tag), any filter that can match a kind in `P_GATED_KINDS` (includes `KIND_GIFT_WRAP`, `KIND_DM_VISIBILITY`, `KIND_AGENT_TURN_METRIC`, agent-observer and membership-notification kinds) must carry a `#p` tag whose every value equals the authenticated caller's own pubkey hex, or the REQ is rejected with `[\"CLOSED\", <sub_id>, \"restricted: p-gated events require #p matching your pubkey\"]`; a narrow `ids`-only exemption exists but is itself withdrawn for `KIND_DM_VISIBILITY` and `KIND_AGENT_TURN_METRIC` because those kinds' event ids are not author-bound proof of authorization. Channel-scoped subscriptions skip this gate because the `fan_out()` invariant already prevents a channel-scoped subscription from ever receiving a globally stored event."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs:211-227"
      - "crates/buzz-relay/src/handlers/req.rs:1182-1216"
      - "crates/buzz-core/src/kind.rs:159-168"
  - statement: "Root `AGENTS.md`'s own contributor-facing gotcha states that a relay query which omits `kinds` triggers this same p-gate (documented there as a 403, the HTTP `/query` bridge's status code for the identical `p_gated_filters_authorized` rejection; the WebSocket REQ path signals the equivalent rejection as a `CLOSED` message, not an HTTP status, because REQ has no HTTP status code to return)."
    entry_class: FACT
    evidence:
      - "AGENTS.md:469"
      - "crates/buzz-relay/src/api/bridge.rs:1076-1090"
  - statement: "A REQ whose filters mix at least one NIP-50 `search` filter with at least one non-search filter is rejected outright with `[\"CLOSED\", <sub_id>, \"error: mixed search and non-search filters not supported\"]`; a REQ whose filters are all search filters is answered as a one-shot query (Postgres FTS hits, hydrated, NIP-01-matched, access-checked, deduplicated, delivered, then EOSE) and is never registered as a live subscription."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs:244-270"
      - "crates/buzz-relay/src/handlers/req.rs:581-806"
  - statement: "For a non-search REQ, the relay inserts the filters into the connection's subscription map keyed by `sub_id` (a second REQ with the same `sub_id` replaces the prior entry outright, matching NIP-01's own replace-on-same-id rule) and separately registers the subscription in `state.sub_registry` for live fan-out, releasing the pubsub topics of any subscription it replaced."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs:272-296"
  - statement: "Historical delivery executes one database query per filter (NIP-01 OR-across-filters semantics — a single merged query would incorrectly collapse independent per-filter `limit`/time windows), runs up to `FILTER_QUERY_CONCURRENCY` (4) queries concurrently but yields results strictly in original filter order, re-applies `filters_match` per-event against only that event's own filter, applies channel-accessibility and result-level reader-visibility checks per event, deduplicates by event id only after acceptance (so an event rejected by filter A remains eligible under filter B), and streams each accepted event as `[\"EVENT\", <sub_id>, <event>]` before finally sending `[\"EOSE\", <sub_id>]` once every filter's query has been drained."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs:313-472"
  - statement: "`filters_match` implements NIP-01 filter semantics as OR-across-filters, AND-within-one-filter: an event matches a filter set if it matches at least one filter, and matches one filter only if every constraint present on that filter (kinds, authors, since, until, ids-prefix, tags, ...) holds."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/filter.rs:1-58"
  - statement: "A malformed WebSocket text frame (invalid JSON, wrong message shape, an unrecognized first-array-element) is answered with `[\"NOTICE\", \"invalid message: <parse error>\"]` and the frame is otherwise ignored; because parsing fails before a `sub_id` is known, no `CLOSED` message is possible for this failure class."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/connection.rs:547-554"
  - statement: "Issue #1022 (parent Feature #616) requires this node to define inputs/messages, outputs/responses, error/rejection behavior, authentication/authorization, versioning/compatibility, ordering/idempotency where applicable, a link to the authoritative machine/spec representation, and at least one valid plus one failure example."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1022 definition of done"
relationships:
  - type: implements
    target: corpus-template-interface
  - type: references
    target: architecture-flows-historical-query
  - type: references
    target: architecture-flows-websocket-authentication
  - type: references
    target: architecture-flows-live-fanout
---

# WebSocket REQ: interface

This node documents the relay's WebSocket **REQ** message — the NIP-01 client
request that opens (or replaces) a subscription, over the WebSocket connection
`architecture-flows-websocket-connection` establishes and
`architecture-flows-websocket-authentication` authenticates. Two sides
exchange it: a client (desktop, mobile, `buzz-cli`, or an agent) sends a
`["REQ", <subscription_id>, <filter>...]` frame; the relay replies with zero
or more `["EVENT", <sub_id>, <event>]` frames covering matching stored
events, then exactly one `["EOSE", <sub_id>]` frame, after which the same
subscription continues receiving newly published matching events in real
time until the client sends `CLOSE`, the connection drops, or the client
reuses the same `sub_id` to replace it.

## Operations

| Operation | Defined in | Summary |
|---|---|---|
| Open subscription / historical replay | `crates/buzz-relay/src/handlers/req.rs` `handle_req` | Register the subscription (or replace one with the same `sub_id`), run one DB query per filter in filter order, deliver matching stored events, send `EOSE`. |
| Full-text search subscription (NIP-50) | `crates/buzz-relay/src/handlers/req.rs` `handle_search_req` | One-shot variant taken when every filter carries `search`: paginates Postgres FTS, hydrates and re-checks hits, delivers, sends `EOSE`; never registered for live fan-out. |
| Terminate subscription | `crates/buzz-relay/src/protocol.rs` `ClientMessage::Close` | A distinct client message (`["CLOSE", <sub_id>]`) that ends a subscription this node opened; not itself part of REQ's own contract — see *Boundary*. |
| Live delivery after EOSE | `architecture-flows-live-fanout` | The same subscription keeps receiving matching events published after EOSE; this node does not restate that mechanism's own contract. |

## Contract and stability

**Message shape.** `["REQ", <subscription_id>, <filter>...]`. `subscription_id`
must be a non-empty string of at most 256 bytes (NIP-11 `max_subid_length`).
At most 10 filter objects are accepted per REQ (NIP-11 `max_filters`); more
are rejected outright rather than truncated.

**Authentication.** `auth_required` is unconditionally `true` in this relay's
NIP-11 document: REQ (like EVENT and COUNT) is rejected for any connection
not already `AuthState::Authenticated`, regardless of the separate REST API
token toggle. See `architecture-flows-websocket-authentication` for how that
authenticated state is reached.

**Authorization.** Beyond authentication, three independent checks gate what
a REQ may return: (1) a scoped token must carry `Scope::MessagesRead`; (2) a
channel-scoped filter (`#h` tag) is authorized per-channel against the
caller's cached-then-DB-confirmed membership, with partial authorization
across an OR'd multi-channel filter — unauthorized channels are silently
omitted, and only an entirely-unauthorized requested set is rejected; (3) a
community-global filter (no consistent `#h`) that can match a kind in
`P_GATED_KINDS` must carry a `#p` tag naming only the caller's own pubkey.
Root `AGENTS.md`'s gotcha #2 — "omitting `kinds` triggers the p-gate" —
describes exactly this third check: a kindless filter is treated as
"can match every p-gated kind" and so is held to the `#p` requirement.

**Ordering.** Historical delivery runs one query per filter, up to 4
concurrently, but yields and emits results strictly in the filters' original
array order (never out of order across filters, though within Postgres a
single filter's own row order is whatever `EventQuery`'s `ORDER BY` produces).
`EOSE` is always the last message of the historical phase for a given REQ —
sent only after every filter's query has been drained — and no `EVENT` for
that subscription's historical phase is ever sent after its `EOSE`.

**Idempotency / replace semantics.** Sending REQ again with a `sub_id` that
names an already-open subscription on the same connection replaces it
outright (the underlying map insert overwrites), matching NIP-01's own
"MAY use the same string to update an existing subscription" rule; the
replaced subscription's pubsub topics are released before the new one's are
retained.

**Error / rejection behavior.** A structurally invalid frame (bad JSON, wrong
shape) never reaches `handle_req` — it is answered with `NOTICE` at parse
time, before any `sub_id` is known. Every rejection that *does* know a
`sub_id` (auth, scope, subscription-limit, channel-authorization, p-gate,
mixed search) is answered with `CLOSED` naming that `sub_id` and a
machine-greppable `"<category>: <reason>"` string (`auth-required: ...`,
`restricted: ...`, `error: ...`), never a silent drop.

**Versioning / compatibility.** This is NIP-01's own wire message, unmodified
in shape; Buzz adds authorization rejections NIP-01 leaves relay-defined
(NIP-01 permits `CLOSED` for exactly this purpose) rather than a
Buzz-specific message variant. The authoritative spec is
[NIP-01](https://github.com/nostr-protocol/nips/blob/master/01.md); this node
does not restate its filter-matching or message-framing text.

## Boundary

This node does not describe:
- **`EVENT`, `CLOSE`, `COUNT`, or `AUTH`'s own contracts** — each is a
  distinct NIP-01/NIP-45/NIP-42 client message with its own request/response
  shape; they share this connection and some helper code (`p_gated_filters_authorized`
  is also called from the HTTP `/query` bridge) but are not this node's
  subject. A future interface node may cover each on its own terms.
- **Live fan-out's own delivery mechanism** (how a newly published event
  reaches an already-registered subscription) — `architecture-flows-live-fanout`
  owns that; this node states only that REQ leaves the subscription
  registered for it.
- **Any single event kind's own wire contract** (tag shape, content
  semantics) — `#1337`'s event-kind template owns that; `P_GATED_KINDS` and
  similar sets are cited here only as the *set* a given check applies to, not
  as per-kind documentation.
- **A field-by-field, domain-expert-depth parameter catalogue** of `nostr::Filter`
  itself — that depth, if the corpus builds it, belongs to `#1346`/`#1532`.

## Relationships

- `implements`: `corpus-template-interface` — this node is an instance of
  that template.
- `references`: `architecture-flows-historical-query` — REQ's historical
  delivery phase is that flow's WebSocket entry point.
- `references`: `architecture-flows-websocket-authentication` — the
  `AuthState::Authenticated` precondition this node's Contract section states
  is that flow's outcome, not re-derived here.
- `references`: `architecture-flows-live-fanout` — REQ's post-EOSE behavior
  hands off to that flow; not restated here.

## Examples

**Valid REQ, channel-scoped, historical + EOSE.** An authenticated client
requests text notes in one channel:

```json
["REQ", "sub1", {"kinds": [40002], "#h": ["3f9e2b0a-...-uuid"], "limit": 50}]
```

The relay replies with zero or more `["EVENT", "sub1", <event>]` frames for
matching stored events the caller may access in that channel, then
`["EOSE", "sub1"]`. The subscription then stays open for live delivery of
newly published matches.

**Failure example — the p-gate AGENTS.md gotcha #2 describes.** The same
authenticated client omits `kinds` on a community-global (no `#h`) filter:

```json
["REQ", "sub2", {"limit": 20}]
```

Because no `kinds` constraint is present, the filter "can match" every
`P_GATED_KINDS` kind, and it carries no `#p` tag naming the caller. The relay
replies `["CLOSED", "sub2", "restricted: p-gated events require #p matching your pubkey"]`
and registers no subscription — exactly the rejection AGENTS.md's gotcha
documents (there, in the HTTP `/query` bridge, as a 403; here, as `CLOSED`).

## Scope and omissions

**This node covers** the WebSocket `REQ` client message's own contract: its
wire shape and NIP-11-advertised limits, the authentication/authorization
gates `handle_req` applies before registering a subscription or returning
any historical event, the ordering and replace/idempotency guarantees of
historical delivery, and the `CLOSED`/`NOTICE` error-rejection vocabulary —
grounded in `crates/buzz-relay/src/handlers/req.rs`, `protocol.rs`,
`connection.rs`, `crates/buzz-core/src/filter.rs`, and `nip11.rs`.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| `EVENT`, `CLOSE`, `COUNT`, `AUTH` message contracts | future interface nodes, not filed here |
| Live fan-out's own delivery mechanism | `architecture-flows-live-fanout` |
| Any single event kind's wire contract | `#1337` (event-kind template), once instantiated |
| Field-by-field `nostr::Filter` parameter catalogue | `#1346`/`#1532` (reference / API-Reference gap, unresolved) |
| The HTTP `/query` bridge's own request/response shape (which reuses `p_gated_filters_authorized` and returns an HTTP 403 rather than `CLOSED`) | a future HTTP-surface interface node |

**Expected but not verified when this node was written:**
- **NIP-01's own specification text was not fetched** — its existence and
  content were relied on through this repository's own code and root
  `AGENTS.md`'s prose description ("Buzz's primary API is NIP-29 over
  WebSocket"), not by opening `nips/01.md` directly.
- **No live end-to-end REQ exchange was run against a running relay** while
  writing this node; every claim above is grounded in reading the handler,
  parser and their unit tests, not in observing a live socket.
- **Whether `implements` or `references` is the corpus-wide convention** for
  a node's optional self-link to its own template remains unsettled per
  `corpus-template-interface`'s own note; this node follows that template's
  stated preference (`implements`).
