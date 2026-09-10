---
id: layers-networking-websocket
type: layers
status: draft
origin: launchpad
audiences:
  - agent
  - developer
evidence:
  - statement: "This node was authored and checked against repository revision 29ca9b189bd3f639ba09c972b57c70538c0860c6."
    entry_class: FACT
    evidence:
      - "commit 29ca9b189bd3f639ba09c972b57c70538c0860c6"
  - statement: "protocol.rs's own module doc describes the relay's WebSocket message layer as \"NIP-01 client/relay message parsing and formatting\", and its ClientMessage enum carries exactly five inbound variants (Event, Req, Close, Count, Auth), so both directions of traffic on this socket are NIP-01 JSON arrays rather than a Buzz-specific envelope."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/protocol.rs"
  - statement: "The relay registers a single bare-host route, GET /, whose handler nip11_or_ws_handler content-negotiates between the admin SPA, a NIP-11 JSON document, and a WebSocket upgrade; it separately registers POST /events, POST /query and POST /count as the Nostr HTTP bridge, and separately again registers GET /huddle/{channel_id}/audio to audio::handler::ws_audio_handler, a second and distinct WebSocket handler living in crates/buzz-relay/src/audio/handler.rs."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs"
  - statement: "api/bridge.rs's module doc states that POST /events, /query and /count \"provide HTTP access to the relay's Nostr protocol, authenticated via NIP-98 signed events\", and the router registers all three with axum's post() method handler, so each is a single request/response exchange."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs"
      - "crates/buzz-relay/src/router.rs"
  - statement: "handlers/ingest.rs documents IngestAuth as \"Authentication context for event ingestion -- transport-neutral\", and documents ingest_event as \"Shared by WebSocket and HTTP transports. The caller constructs IngestAuth from their transport-specific auth mechanism and maps the result to their transport-specific response format.\""
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "ingest_event_inner rejects two event kinds on the HTTP transport only, via the guard `auth.is_http() && (kind_u32 == KIND_GIFT_WRAP || kind_u32 == KIND_PRESENCE_UPDATE)`, returning the rejection message \"invalid: kind {kind_u32} is only accepted via WebSocket\"; ingest.rs's own unit test gift_wrap_is_in_scope_allowlist records in a comment that \"The HTTP block is transport-level (is_http gate), not scope-level.\""
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "buzz-core's kind registry defines KIND_GIFT_WRAP as 1059 and KIND_PRESENCE_UPDATE as 20001."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "The relay labels its own telemetry by transport: connection.rs increments buzz_admission_rejections_total with `\"transport\" => \"websocket\"`, api/bridge.rs increments the same counter with `\"transport\" => \"http\"`, and ingest.rs's reject_with_transport is documented as \"Shared by the WS EVENT handler and the HTTP POST /events handler so both transports feed the same series -- transport distinguishes them so existing WS-only dashboards aren't silently diluted by HTTP volume.\""
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/connection.rs"
      - "crates/buzz-relay/src/api/bridge.rs"
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "Each WebSocket connection owns three separate outbound queues, not one: a data channel sized from Config::send_buffer_size, a control channel of fixed capacity 8 documented as a \"Separate channel with priority drain\", and a restart channel of capacity 1 carrying a RestartClose request."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/connection.rs"
  - statement: "The control channel's own field doc names its contents as \"(Pong, Close)\", but more is queued on it in practice: the heartbeat loop try_sends a Ping there, an inbound Ping is answered with a Pong there, state.rs's disconnect path holds a ctrl_tx to deliver its reason frame, and send_loop_inner's cancel branch documents \"queue frame on ctrl, then cancel\" as a supported idiom for a ban's `OK false \"blocked: …\"` reason frame."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/connection.rs"
      - "crates/buzz-relay/src/state.rs"
  - statement: "send_loop_inner drains every pending control frame at the top of each iteration before selecting, and its tokio::select! is marked `biased` with the documented ordering \"restart > cancel > ordinary control > data\"."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/connection.rs"
  - statement: "Outbound data frames are written with Sink::feed and batched up to MAX_WS_SEND_BATCH (a const of 64) before a single Sink::flush, with the resulting batch size recorded to the buzz_ws_send_batch_size histogram, whereas control frames are written with Sink::send, which flushes each one individually."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/connection.rs"
  - statement: "The restart branch of send_loop_inner sends a Close frame carrying close_code::RESTART and the static reason \"relay restarting\", then reports whether that send succeeded back to the requester over a oneshot channel (RestartClose::flushed) before breaking the loop."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/connection.rs"
  - statement: "Because the HTTP bridge's three endpoints are each a single POST request/response exchange, none of them can carry a frame the relay originates on its own initiative -- the NIP-42 AUTH challenge, a live EVENT delivered onto an already-open subscription, EOSE, NOTICE or CLOSED -- so the persistent socket is not a faster alternative to the bridge but the only transport on which challenge/response authentication and subscription fan-out are expressible at all."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs"
      - "crates/buzz-relay/src/router.rs"
      - "crates/buzz-relay/src/protocol.rs"
    confidence: 0.8
  - statement: "The three-queue writer with a fixed 8-slot control channel and 64-frame data batching is a quality-of-service mechanism belonging to the transport rather than to the Nostr protocol: nothing in NIP-01 distinguishes a Pong from an EVENT, and the priority ordering exists so a connection whose data buffer is saturated can still be pinged, told why it is being disconnected, and closed."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay/src/connection.rs"
      - "crates/buzz-relay/src/protocol.rs"
    confidence: 0.7
  - statement: "buzz-cli's publish_ephemeral_event doc comment states \"The relay rejects ephemeral kinds (20000-29999) over HTTP\", which does not match the relay's actual is_http gate: that gate blocks exactly two kinds, one of which (1059) is not ephemeral, while the great majority of the 20000-29999 range it names is not blocked by it."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-cli/src/client.rs"
      - "crates/buzz-relay/src/handlers/ingest.rs"
      - "crates/buzz-core/src/kind.rs"
    confidence: 0.8
  - statement: "The connection's upgrade path, admission checks, four-task structure, frame-size rejection, binary-to-text decoding, heartbeat, backpressure and termination behaviour are already documented as a single flow by architecture-flows-websocket-connection; the NIP-42 round trip by architecture-flows-websocket-authentication; the inbound/outbound message-shape catalogue and its tests by verification-contracts-websocket; the prefer-events-over-endpoints design invariant by architecture-principles-nostr-first; and the client half by implementation-crates-buzz-ws-client."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/flows/websocket-connection.md"
      - "launchpad/docs/corpus/architecture/flows/websocket-authentication.md"
      - "launchpad/docs/corpus/verification/contracts/websocket.md"
      - "launchpad/docs/corpus/architecture/principles/nostr-first.md"
      - "launchpad/docs/corpus/implementation/crates/buzz-ws-client.md"
relationships:
  - type: references
    target: architecture-flows-websocket-connection
  - type: references
    target: architecture-flows-websocket-authentication
  - type: references
    target: verification-contracts-websocket
  - type: references
    target: architecture-principles-nostr-first
  - type: references
    target: implementation-crates-buzz-ws-client
  - type: references
    target: implementation-crates-buzz-relay
---

# The WebSocket transport layer

## Definition

Buzz's WebSocket transport is a **single long-lived, host-bound, stateful socket that
carries the NIP-01 message vocabulary in both directions between a client and the
relay** — and it is the relay's primary API surface because it is the only transport on
which the relay can speak first.

Everything in that sentence is load-bearing, so take it apart:

- **Single and long-lived.** One socket per client session, opened at `GET /` and held
  open. It is not re-established per operation.
- **Host-bound and stateful.** The socket carries connection-scoped state that no
  individual message re-supplies: the community it is bound to, its authenticated
  identity, and its open subscriptions.
- **NIP-01 in both directions.** `crates/buzz-relay/src/protocol.rs` describes itself as
  "NIP-01 client/relay message parsing and formatting". The wire format is the standard
  Nostr JSON array in each direction — there is no Buzz-specific envelope wrapping it.
- **The relay can speak first.** This is the property that makes it primary, and it is
  developed in the next section.

**What this node is not about.** It is not the connection's lifecycle, not the NIP-42
handshake, not the catalogue of message shapes, and not the client library. Those are
four other nodes, each named precisely in *Boundary* below. This node is about the
transport as an idea: what kind of pipe this is, and what that choice buys.

## Why the socket is primary, and HTTP is not

The relay does expose the same Nostr protocol over HTTP. `POST /events`, `POST /query`
and `POST /count` are registered in `crates/buzz-relay/src/router.rs`, and
`crates/buzz-relay/src/api/bridge.rs` describes them as endpoints that "provide HTTP
access to the relay's Nostr protocol, authenticated via NIP-98 signed events."

So the two transports are not different protocols. They are the same protocol, and the
relay's own code says so in three places:

**One ingest core, two transports.** `crates/buzz-relay/src/handlers/ingest.rs`
documents `IngestAuth` as "Authentication context for event ingestion —
transport-neutral", and documents the shared entry point directly:

> Shared by WebSocket and HTTP transports. The caller constructs `IngestAuth` from their
> transport-specific auth mechanism and maps the result to their transport-specific
> response format.

The transport supplies an authenticated principal and a response format. Validation,
authorization and storage are the same code either way.

**The relay measures itself by transport.** `buzz_admission_rejections_total` is
incremented with `"transport" => "websocket"` from `connection.rs` and with
`"transport" => "http"` from `api/bridge.rs`; `reject_with_transport` in `ingest.rs`
exists, by its own comment, "so both transports feed the same series — `transport`
distinguishes them so existing WS-only dashboards aren't silently diluted by HTTP
volume." The two-transport model is not an interpretation imposed on the code; it is
how the code labels its own telemetry.

**And the two are not equal.** `ingest_event_inner` carries a gate that fires on the
HTTP transport alone:

```rust
if auth.is_http() && (kind_u32 == KIND_GIFT_WRAP || kind_u32 == KIND_PRESENCE_UPDATE) {
    return Err(IngestError::Rejected(format!(
        "invalid: kind {kind_u32} is only accepted via WebSocket"
    )));
}
```

Kind 1059 and kind 20001 (`crates/buzz-core/src/kind.rs`) can be submitted over the
socket and cannot be submitted over the bridge. `ingest.rs`'s own unit test comment
records the reason this rejection is not a permissions decision: *"The HTTP block is
transport-level (`is_http` gate), not scope-level."*

**The structural reason.** Each bridge endpoint is a single `post(...)` request/response
exchange. A request/response exchange has no channel on which the relay may originate a
frame the client did not just ask for — and four of the things this protocol needs are
exactly that: the NIP-42 `AUTH` challenge the relay issues before the client has said
anything, a live `EVENT` pushed onto an already-open subscription, `EOSE` closing out a
backlog, and `CLOSED`/`NOTICE` explaining a server-side decision. So the socket is not a
lower-latency alternative to the bridge. Challenge/response authentication and
subscription fan-out are *inexpressible* over the bridge, which is why the bridge is best
read as a reduced projection of the socket rather than a peer of it.

This is a different claim from the one `architecture-principles-nostr-first` makes. That
node owns the *design invariant* — model new backend capability as a signed Nostr event
rather than a new HTTP JSON route, and keep the HTTP surface narrow. This node explains
the *transport* underneath that invariant: why the socket exists at all, and what the
bridge structurally cannot do.

## Transport-level property: three prioritised outbound queues

The most consequential thing this transport does that the Nostr protocol does not
describe is **prioritise its own outbound traffic**. Each connection owns three separate
queues into one socket writer, not one
(`crates/buzz-relay/src/connection.rs`):

| Queue | Capacity | Carries |
|---|---|---|
| data | `Config::send_buffer_size` | ordinary protocol frames — `EVENT`, `OK`, `NOTICE`, `EOSE`, `CLOSED` |
| control | fixed **8** — "Separate channel with priority drain" | its field doc names `Pong` and `Close`; in practice also the heartbeat's `Ping`, and a ban's `OK false "blocked: …"` reason frame |
| restart | **1** | a `RestartClose` request |

`send_loop_inner` drains every pending control frame at the top of each iteration
*before* it selects on anything, and its `tokio::select!` is marked `biased` with the
ordering its own comment states: **restart > cancel > ordinary control > data.**

The two disciplines differ, and the difference is the point:

- **Data frames are batched.** They are written with `Sink::feed` — which queues without
  flushing — up to `MAX_WS_SEND_BATCH` (64) frames, then flushed once, with the achieved
  batch size recorded to the `buzz_ws_send_batch_size` histogram. Throughput work.
- **Control frames are not.** They are written with `Sink::send`, which flushes each one
  on its own. Latency work.

The restart branch is the sharpest illustration of why the third queue exists: it emits a
`Close` carrying `close_code::RESTART` and the reason `"relay restarting"`, then reports
back over a `oneshot` whether that frame actually reached the wire. A shutdown that
merely cancels cannot tell whether the client was informed; a shutdown that owns a
priority queue and an acknowledgement can.

**Why this belongs to the transport and not the protocol.** NIP-01 has no notion of a
`Pong`, and no notion of one message mattering more than another — every relay message
is a JSON array of equal standing. The priority ordering is a quality-of-service property
this layer adds underneath the protocol, so that a connection whose data buffer has
saturated can still be pinged, still be told *why* it is being disconnected, and still be
closed cleanly. That is what makes it a transport-layer idea rather than a protocol one.

## Boundary

This node is deliberately narrow, because the WebSocket is one of the most heavily
documented subjects in this corpus already. **All five of the following are merged nodes,
and this node references rather than restates every one of them:**

| Node | Owns |
|---|---|
| `architecture-flows-websocket-connection` | The connection flow end to end: the `/` route's content negotiation, host-to-community binding, the pre-upgrade 404 and 503 paths, the community-active and connection-semaphore admission checks, the four-tasks-around-one-`CancellationToken` structure, per-variant message dispatch, oversized-frame rejection, binary-frames-decoded-as-text, slow-client backpressure, every termination path, and the cleanup that follows. |
| `architecture-flows-websocket-authentication` | The NIP-42 challenge/response round trip: challenge generation, `verify_nip42_event`'s ordered checks, the 5-second `AUTH_TIMEOUT`, the ban / allowlist / membership gates, NIP-OA owner delegation, and per-message-type auth enforcement. |
| `verification-contracts-websocket` | The testable contract: the five inbound and six outbound NIP-01 message shapes, the NIP-42-gated accept/reject behaviour for `EVENT` and `REQ`, `CLOSE`'s deliberate lack of an auth gate, the tests that exercise each, and which automated lanes do and do not run them. |
| `architecture-principles-nostr-first` | The design invariant that new backend capability is modelled as a signed Nostr event rather than a new endpoint-specific HTTP JSON route, where that invariant is written down, what enforces it (nothing automated), and the current route inventory that already sits outside it. |
| `implementation-crates-buzz-ws-client` | The client half: `NostrWsConnection`'s public surface, its timeout constants, its three workspace consumers, and its verification. |

The crate this transport lives inside — its modules, dependencies and responsibilities as
a unit of code rather than as a transport — is documented by
`implementation-crates-buzz-relay`, which this node also references.

**Adjacent subjects owned by sibling tasks in this same batch**, named by subject because
their nodes are not merged and their ids therefore cannot be targeted: connection
admission; the connection lifecycle including client-side timeouts and close frames;
connection limits including the frame-byte cap; the transport heartbeat and its
ping/pong cycle; the relay's HTTP surface; and slow-client backpressure. Where this node
touches any of them — the control queue carries `Pong` and `Close`, the bridge is an HTTP
surface — it does so only to place its own subject, and makes no claim those nodes own.

**Do not confuse this transport with**: the huddle audio WebSocket at
`/huddle/{channel_id}/audio`, which is a different socket on a different route with its
own protocol; and the git smart-HTTP transport, which is not a socket at all.

## Scope and omissions

**This node covers** what kind of transport the relay's Nostr WebSocket is, the
relationship between it and the HTTP bridge (one protocol, one shared transport-neutral
ingest core, two transports of unequal capability), the two kinds that are
WebSocket-exclusive at the relay, and the transport's own three-queue prioritised
outbound writer.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The connection lifecycle, admission, dispatch, frame limits, heartbeat, backpressure and termination | `architecture-flows-websocket-connection`, and more narrowly by this batch's admission / lifecycle / limits / heartbeat / backpressure siblings |
| The NIP-42 handshake and its authorization gates | `architecture-flows-websocket-authentication` |
| The inbound/outbound message-shape catalogue and its tests | `verification-contracts-websocket` |
| The prefer-events-over-endpoints invariant and the full HTTP route inventory | `architecture-principles-nostr-first`, and this batch's HTTP-surface sibling |
| The client-side implementation | `implementation-crates-buzz-ws-client` |
| NIP-98, the bridge's own authentication mechanism | Not a corpus node at this revision |
| The huddle audio WebSocket | Not a corpus node at this revision |

**A divergence found while gathering evidence, recorded but not fixed here.**
`crates/buzz-cli/src/client.rs`'s `publish_ephemeral_event` doc comment states that "The
relay rejects ephemeral kinds (20000–29999) over HTTP." The relay's actual `is_http` gate
blocks exactly two kinds — 1059, which is not ephemeral, and 20001 — so the comment is
inaccurate in both directions: it names a range far wider than what is blocked, and
misses the one blocked kind that falls outside that range. `implementation-crates-buzz-ws-client`
repeats the comment's version. This node states what the relay source does and does not
edit either the comment or that node; correcting them is a separate task.

**Expected but not verified when this node was written:**

- **No test appears to assert the WebSocket-only kind gate.** The `is_http()` guard's two
  unit-test neighbours in `ingest.rs` (`ingest_auth_is_http_returns_true_for_http_variant`,
  `ingest_auth_is_http_returns_false_for_nip42_variant`) test the `is_http()` accessor
  itself, not the rejection it guards. A workspace-wide search for the rejection message
  `"only accepted via WebSocket"` returns exactly two hits — the rejection site itself and
  an unrelated doc comment in `crates/buzz-cli/src/commands/users.rs` — and no test. That
  is a search over one distinctive string, not proof no test exists by another route, so
  the claim above rests on reading the guard rather than on an executed test.
- **Nothing was executed while authoring this node.** No relay was started, no test run,
  no frame observed on a wire. Every `FACT` here is a file opened and read at the recorded
  revision.
- **`Config::send_buffer_size`'s default value was not established.** The data queue's
  capacity is operator-configurable and only its configurability is claimed here; the
  fixed capacities (control 8, restart 1) and `MAX_WS_SEND_BATCH` (64) are literals read
  from `connection.rs` and are stated as such.
- **Whether the batching and priority behaviour is exercised end-to-end was not
  established.** `connection.rs` carries in-crate `send_loop_inner` tests whose names
  describe batching, control-before-data ordering, and the RESTART flush; they were seen
  in the file but were not read line by line or run, so they are not cited as evidence for
  any claim above. Their sufficiency is `verification`-surface territory, not this node's.
