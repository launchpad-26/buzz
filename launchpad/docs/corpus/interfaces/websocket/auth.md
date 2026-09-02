---
id: interfaces-websocket-auth
type: interfaces-events
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision c34e62d16781dac3fa45cdedf0f09d4e1d8bbe8f."
    entry_class: FACT
    evidence:
      - "commit c34e62d16781dac3fa45cdedf0f09d4e1d8bbe8f"
  - statement: "NIP-42 defines a new client-relay protocol message, AUTH: relays send it as [\"AUTH\", <challenge-string>], clients send it as [\"AUTH\", <signed-event-json>], and an AUTH message sent by a client MUST be answered with an OK message like any EVENT message. The canonical authentication event MUST be kind:22242, carries at least a relay tag and a challenge tag, is ephemeral (not meant to be published or queried), and relays MUST exclude it from being broadcast to any client. NIP-42 also defines the auth-required: and restricted: machine-readable OK/CLOSED prefixes."
    entry_class: FACT
    evidence:
      - "https://github.com/nostr-protocol/nips/blob/24b2ae9fdfeb4e5c0d3be854df5977b81afe1983/42.md"
  - statement: "buzz-relay's ClientMessage::parse handles the \"AUTH\" message type by deserializing arr[1] as a signed Event into ClientMessage::Auth(Event), rejecting the message if arr.len() < 2 or the event fails to deserialize. RelayMessage::auth_challenge and RelayMessage::ok format the two relay-to-client frames as the JSON arrays [\"AUTH\", <challenge>] and [\"OK\", <event_id>, <accepted>, <message>] respectively."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/protocol.rs"
  - statement: "buzz-relay's protocol.rs carries its own unit tests exercising this exact wire shape: parse_valid_messages round-trips an AUTH client message built from a real signed kind:22242 event, and format_relay_messages asserts RelayMessage::auth_challenge produces [\"AUTH\", <challenge>] and RelayMessage::ok produces an [\"OK\", ...] array with the accepted boolean and message string in the expected positions."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/protocol.rs"
  - statement: "buzz-ws-client's message.rs mirrors this contract from the client side: RelayMessage::Auth { challenge } parses the relay's [\"AUTH\", <challenge>] frame, OkResponse { event_id, accepted, message } parses the relay's [\"OK\", ...] frame, and build_auth_event constructs the signed kind:22242 event via EventBuilder::auth(challenge, relay_url), optionally attaching a NIP-OA auth tag passed in by the caller."
    entry_class: FACT
    evidence:
      - "crates/buzz-ws-client/src/message.rs"
  - statement: "buzz-core's kind registry defines KIND_AUTH as the literal 22242, documented in the source as \"NIP-42 auth event — never stored (carries bearer tokens)\"."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs:77"
  - statement: "buzz-auth's nip42.rs module doc states the round trip as three steps -- relay sends [\"AUTH\", \"<challenge>\"] via generate_challenge, client signs a kind:22242 event with challenge and relay tags, relay validates via verify_nip42_event -- and states AUTH events are never stored or logged because they may contain bearer tokens. generate_challenge produces 32 CSPRNG bytes, hex-encoded. verify_nip42_event checks, in order: event.kind == Kind::Authentication, the event's Schnorr signature (via buzz_core::verify_event), the challenge tag matching the expected challenge, and (after the checked excerpt) the relay tag and a ±60-second created_at window (TIMESTAMP_TOLERANCE_SECS = 60), returning the first AuthError encountered rather than continuing to check the rest."
    entry_class: FACT
    evidence:
      - "crates/buzz-auth/src/nip42.rs"
  - statement: "nip42.rs's normalize_relay_url treats a relay tag's localhost or ::1 host as equivalent to 127.0.0.1, and strips a trailing slash from the path, before comparing it against the relay's own URL -- so a client's relay tag need not be byte-identical to the server's configured URL to pass the relay-URL check."
    entry_class: FACT
    evidence:
      - "crates/buzz-auth/src/nip42.rs"
  - statement: "buzz-auth's error.rs defines AuthError variants InvalidSignature (\"invalid signature or malformed auth event\"), ChallengeMismatch (\"challenge mismatch\"), RelayUrlMismatch (\"relay url mismatch\"), and EventExpired (\"auth event timestamp outside ±60s window\"), each corresponding to one verify_nip42_event failure mode, alongside NIP-98-specific and other variants not part of this WebSocket AUTH message's own contract."
    entry_class: FACT
    evidence:
      - "crates/buzz-auth/src/error.rs"
  - statement: "buzz-relay's connection.rs defines AUTH_TIMEOUT as 5 seconds and an AuthState enum with Pending { challenge }, Authenticated(AuthContext), and Failed variants. handle_connection sends the [\"AUTH\", <challenge>] frame (via RelayMessage::auth_challenge) before registering the connection with the connection manager -- registration happens only after the send succeeds, so an immediate client disconnect leaves no leaked registry entry -- and a background task cancels the connection if AuthState is not Authenticated within AUTH_TIMEOUT of connecting."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/connection.rs"
  - statement: "buzz-ws-client's connection.rs defines AUTH_CHALLENGE_TIMEOUT_SECS and AUTH_OK_TIMEOUT_SECS as 20 seconds each; authenticate() waits up to AUTH_CHALLENGE_TIMEOUT_SECS for the relay's AUTH challenge frame, then sends the signed AUTH event and waits up to AUTH_OK_TIMEOUT_SECS for the matching OK response keyed by the event id."
    entry_class: FACT
    evidence:
      - "crates/buzz-ws-client/src/connection.rs"
  - statement: "buzz-relay's handlers/auth.rs (handle_auth) rejects an AUTH message immediately, without re-running verification, when the connection's current AuthState is already Authenticated or already Failed -- replying OK false with \"auth-required: already authenticated\" or \"auth-required: authentication already failed\" respectively."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/auth.rs"
  - statement: "handle_auth reports a failed NIP-42 verification (wrong kind, bad signature, challenge mismatch, relay mismatch, or expired timestamp) to the client as OK false, \"auth-required: verification failed\". A banned pubkey (or its NIP-OA-proven owner) is reported as OK false, \"blocked: you are banned from this community\", followed by an immediate WebSocket close. A database error while checking ban state is reported as OK false, \"error: internal error checking restriction state\", and is fail-closed (treated as a denial, not a pass). Failing the relay-membership gate is reported as OK false, \"restricted: not a relay member\"."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/auth.rs"
  - statement: "The EVENT, REQ, and COUNT handlers each independently read the connection's AuthState and reject with their own client-visible message when it is not AuthState::Authenticated: event.rs and count.rs both use \"auth-required: not authenticated\", and req.rs uses \"auth-required: authenticate before subscribing\" for REQ specifically (falling back to \"auth-required: not authenticated\" in at least one other path). These three handlers are downstream consumers of this AUTH interface's outcome, not part of the AUTH message contract documented in this node."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs"
      - "crates/buzz-relay/src/handlers/req.rs"
      - "crates/buzz-relay/src/handlers/count.rs"
  - statement: "A separately merged corpus node, architecture-flows-websocket-authentication (launchpad/docs/corpus/architecture/flows/websocket-authentication.md), already documents the same NIP-42 round trip as a stateful, ordered flow: trigger/preconditions/termination, 15 numbered interaction steps, the ban/allowlist/membership gate order, and a full failure table. This node is scoped instead to the WebSocket message contract itself -- the AUTH/OK frame shapes and what a caller may rely on -- and defers the interaction sequence and gate ordering to that node rather than restating them."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/flows/websocket-authentication.md"
  - statement: "No corpus node with id interfaces-nostr-nip-42 or events-kinds-kind-22242-auth exists in origin/launchpad's corpus tree at the recorded revision, so no relationships entry can legally target either -- a relationships[].target naming an id no loaded node carries is a hard validation error."
    entry_class: FACT
    evidence:
      - "git_grep('^id: interfaces-nostr-nip-42|^id: events-kinds-kind-22242-auth', path='launchpad/docs/corpus') -> no matches at commit c34e62d16781dac3fa45cdedf0f09d4e1d8bbe8f"
  - statement: "node.schema.json's type enum has thirteen members and none of them is a plain \"interface\" value; the combined interfaces-events value is the schema-correct choice for an interface-shaped node, per templates/interface.md's own \"A note on type\" section, which states a node built from that template \"carries type: interfaces-events\"."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
      - "launchpad/docs/corpus/templates/interface.md"
  - statement: "Issue #1018's Definition of done requires: exactly one hand-authored canonical document; schema-valid front matter with a stable id, type, status, origin, audiences, evidence and typed relationships appropriate to the node; one independently maintainable knowledge node with any second concept filed separately; every substantive claim traceable with FACT/INFERENCE/TEAM_KNOWLEDGE not conflated; links to implementation/verification/specification/neighboring nodes without duplicating their canonical content; the draft checked against the provenance revision; local corpus validation passing; inputs/messages, outputs/responses and error/rejection behavior defined; authentication/authorization, versioning/compatibility and ordering/idempotency defined where applicable; a link to the authoritative machine/spec representation; and at least one valid and one failure example."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1018 definition of done"
---

# WebSocket AUTH: interface

The boundary this node documents is the `AUTH` message exchange between a
Nostr client and a Buzz relay over the same WebSocket connection used for
`EVENT`/`REQ`/`COUNT` traffic: the relay's `["AUTH", "<challenge>"]` frame,
the client's `["AUTH", <signed kind:22242 event>]` response, and the relay's
`["OK", <event_id>, <accepted>, <message>]` acknowledgement of that response.
Both sides exchange plain JSON-array text frames on the WebSocket, per NIP-01
message framing; the payload inside the client's `AUTH` array is a
Schnorr-signed Nostr event per NIP-42. This node documents the message
envelope and the contract callers may rely on -- not the cryptographic
protocol NIP-42 itself (a separate, unmerged interface node,
`interfaces/nostr/nip-42.md`, owns that) and not the kind:22242 event's own
tag/content schema (a separate, unmerged event-kind node owns that).

## Operations

| Operation | Defined in | Summary |
|---|---|---|
| Relay -> client: AUTH challenge | `RelayMessage::auth_challenge` (`crates/buzz-relay/src/protocol.rs`); parsed client-side by `buzz-ws-client`'s `RelayMessage::Auth { challenge }` (`crates/buzz-ws-client/src/message.rs`) | `["AUTH", "<challenge>"]`. The challenge is 32 CSPRNG bytes, hex-encoded, generated by `generate_challenge()` (`crates/buzz-auth/src/nip42.rs`) and sent once per connection before the connection is registered with the connection manager. |
| Client -> relay: AUTH response | `ClientMessage::parse`'s `"AUTH"` arm, producing `ClientMessage::Auth(Event)` (`crates/buzz-relay/src/protocol.rs`); built client-side by `build_auth_event` (`crates/buzz-ws-client/src/message.rs`) via `EventBuilder::auth(challenge, relay_url)` | `["AUTH", <signed kind:22242 event>]`. The event carries `relay` and `challenge` tags and, optionally, a NIP-OA `auth` tag; it is never stored or broadcast (`crates/buzz-core/src/kind.rs:77`). |
| Relay -> client: OK acknowledgement | `RelayMessage::ok` (`crates/buzz-relay/src/protocol.rs`); parsed client-side by `buzz-ws-client`'s `OkResponse` (`crates/buzz-ws-client/src/message.rs`) | `["OK", <event_id>, <accepted:bool>, <message:string>]`, keyed by the AUTH event's own id, exactly as NIP-01 defines `OK` for any submitted event. |
| Relay-side dispatch | `handlers::auth::handle_auth` (`crates/buzz-relay/src/handlers/auth.rs`), invoked from `handle_text_message` when a frame parses as `ClientMessage::Auth` | Runs cryptographic verification (`buzz-auth`'s `verify_nip42_event`) then the ban / allowlist / relay-membership gates, and commits `AuthState::Authenticated` or `Failed`. |
| Client-side round trip | `NostrWsConnection::authenticate` / `connect_authenticated` (`crates/buzz-ws-client/src/connection.rs`) | Waits for the challenge frame, builds and sends the signed AUTH event, and waits for the matching `OK`. |

## Contract and stability

- **The message envelope is NIP-01/NIP-42 framing and is not this repository's
  to redefine.** `AUTH` is a two-element JSON array in both directions
  (`["AUTH", <challenge-or-event>]`); `OK` is the same four-element array NIP-01
  defines for any event submission. A caller may rely on this shape not
  changing without a protocol-level (not Buzz-internal) versioning event.
- **Timing is asymmetric by design, not by accident.** The relay-side
  `AUTH_TIMEOUT` is 5 seconds (`crates/buzz-relay/src/connection.rs`) --
  protecting the relay's connection-semaphore slots from slow or malicious
  sockets -- while `buzz-ws-client`'s own `AUTH_CHALLENGE_TIMEOUT_SECS` and
  `AUTH_OK_TIMEOUT_SECS` are each 20 seconds (`crates/buzz-ws-client/src/connection.rs`),
  tolerating ordinary network latency for a cooperating client. A client
  library holding out for up to 20 seconds does not imply the relay will wait
  that long; a caller must complete the round trip within 5 seconds of the
  socket opening to succeed against this relay's own timeout.
- **The `created_at` window is ±60 seconds** (`TIMESTAMP_TOLERANCE_SECS`,
  `crates/buzz-auth/src/nip42.rs`), independent of the 5-second connection
  timeout above -- an AUTH event signed too far in the past or future fails
  verification even if it arrives promptly.
- **Kind:22242 AUTH events are never stored, logged, or rebroadcast** -- stated
  directly in `buzz-core`'s kind registry and `buzz-auth`'s module doc,
  because the event may carry bearer tokens (a NIP-OA `auth` tag). A caller
  must not expect an AUTH event to be queryable afterward.
-  **One outcome per connection, no re-verification.** Once a connection's
  `AuthState` is `Authenticated` or `Failed`, a further `AUTH` message on the
  same connection is rejected immediately by `handle_auth` without
  re-running any check -- a caller cannot retry authentication on an already-
  decided connection; a fresh attempt requires a new connection.
- **The relay's URL match tolerates known-equivalent hosts, not arbitrary
  ones.** `normalize_relay_url` treats `localhost`/`::1` as `127.0.0.1` and
  strips one trailing slash before comparing the event's `relay` tag against
  the relay's own URL -- a caller may rely on exactly this normalization and
  no broader one.
- **Versioning/compatibility.** No Buzz-specific versioning scheme applies to
  this message pair; it inherits NIP-01/NIP-42's own protocol stability.
  Buzz adds no extra required tag beyond what NIP-42 and the optional NIP-OA
  `auth` tag define.
- **Ordering/idempotency.** Exactly one AUTH exchange per connection produces
  a durable outcome (`Authenticated` or `Failed`); the exchange is not
  idempotent in the sense of being safely repeatable -- a second attempt is
  rejected outright rather than re-evaluated (see above).

### A valid example

Relay sends the challenge, client responds with a correctly signed and
correctly tagged event, relay accepts:

```
-> ["AUTH", "<challenge>"]
<- ["AUTH", {"kind":22242,"pubkey":"...","created_at":1735689600,
             "tags":[["relay","wss://relay.example.com"],
                     ["challenge","<challenge>"]],
             "content":"","id":"...","sig":"..."}]
-> ["OK", "<event id>", true, ""]
```

(`->` = relay-to-client, `<-` = client-to-relay, matching this node's
Operations table.)

### A failure example

Client responds with an event carrying a stale `created_at` (outside the
±60-second window) -- `verify_nip42_event` returns `AuthError::EventExpired`,
and `handle_auth` reports it as a generic verification failure without
distinguishing the specific `AuthError` variant to the client:

```
-> ["AUTH", "<challenge>"]
<- ["AUTH", {"kind":22242, ..., "created_at": <now - 300>, ...}]
-> ["OK", "<event id>", false, "auth-required: verification failed"]
```

The connection's `AuthState` becomes `Failed`; a further `AUTH` on the same
connection is rejected immediately with `"auth-required: authentication
already failed"` rather than re-verified.

## Boundary

This node does not describe:

- **The NIP-42 protocol contract itself** -- the challenge/response scheme's
  own rationale, the `auth-required:`/`restricted:` prefix semantics as a
  general Nostr-protocol concept, and cross-relay interoperability. That is
  `interfaces/nostr/nip-42.md`'s subject (issue #1014), not yet merged.
- **The kind:22242 event's own wire contract** -- exact tag list, content-field
  semantics, and NIP-OA `auth`-tag structure as a standalone event-kind
  node. That is a separate, unmerged event-kind node's subject.
- **The full connection-lifecycle flow** -- admission, the ban / allowlist /
  relay-membership gate order, NIP-OA owner-delegation cascading, and
  per-message-type (`EVENT`/`REQ`/`COUNT`) enforcement after authentication.
  All of that is already documented by the merged
  `architecture-flows-websocket-authentication` node; this node references
  it rather than restating it.
- **NIP-98 HTTP Auth** (kind:27235, `crates/buzz-auth/src/nip98.rs`) -- a
  sibling authentication path for the relay's HTTP surface, not the
  WebSocket transport this node covers.

## Relationships

None declared. The two natural targets --
`interfaces-nostr-nip-42` and an event-kind node for kind:22242 -- do not
yet exist as merged corpus nodes (confirmed by `git grep`/`git ls-tree`
against `origin/launchpad` at the recorded revision), and a
`relationships[].target` naming an id no loaded node carries is a hard
validation error. This node mentions both by filename in prose above
instead. Likewise, no edge is declared toward
`architecture-flows-websocket-authentication` even though it is merged and
directly relevant: `relationships.schema.json`'s types (`depends-on`,
`supersedes`, `implements`, `references`, `part-of`) are graph edges between
nodes' own subject matter, and adding one is a content decision about an
*existing* merged node's edges that this task's own "Out of scope" line
("broad while-here documentation cleanup") leaves to a follow-up rather than
this session -- the cross-link exists in prose (see *Interface description*
and *Boundary* above) in the meantime.

## Scope and omissions

**This node covers** the WebSocket `AUTH` message exchange between a Nostr
client and the Buzz relay: the two frame shapes in each direction and the
`OK` acknowledgement, the timeouts and timestamp window that bound the
exchange, the never-stored invariant on the AUTH event itself, the
one-outcome-per-connection rule, and the relay-URL normalization a caller
may rely on.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| NIP-42's own protocol rationale and cross-relay semantics | `interfaces/nostr/nip-42.md` (issue #1014, unmerged) |
| Kind:22242's own tag/content wire contract | An unmerged event-kind node for kind:22242 |
| The full connection lifecycle, gate ordering, and per-message-type enforcement | `architecture-flows-websocket-authentication` (merged) |
| NIP-98 HTTP Auth | Not yet in this corpus |
| Rate limiting and admission control applied after authentication | Not yet in this corpus |

**Expected but not verified when this node was written:**

- **Whether every `AuthError` variant maps to a distinct client-visible
  message, or several collapse to the same `"auth-required: verification
  failed"` string, was not exhaustively traced.** `handle_auth`'s failure
  example above was confirmed for the general verification-failure path; the
  per-variant mapping inside `handle_auth` was not line-by-line diffed
  against every `AuthError` variant in `error.rs`.
- **Whether a relay operator can configure `AUTH_TIMEOUT`,
  `AUTH_CHALLENGE_TIMEOUT_SECS`, or `AUTH_OK_TIMEOUT_SECS` at runtime, or
  whether they are compiled constants only, was not checked** -- they are
  read here as `const`/`pub const` declarations, which in Rust does not by
  itself prove no configuration layer overrides them before compilation.
- **No live relay/client round trip was executed while authoring this node** --
  every claim above is sourced from reading `buzz-relay`, `buzz-ws-client`,
  `buzz-auth`, and `buzz-core` source and their own unit tests, not from
  running `just test`'s end-to-end suite in this session.
