---
id: implementation-crates-buzz-ws-client
type: implementation
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 76a0a4ebbe4bc4d852b0d04362ed768620da34b3."
    entry_class: FACT
    evidence:
      - "commit 76a0a4ebbe4bc4d852b0d04362ed768620da34b3"
  - statement: "buzz-ws-client is a small crate of four source files (lib.rs, connection.rs, message.rs, error.rs), carries no README.md and no tests/ directory of its own, and its lib.rs re-exports NostrWsConnection and publish_event from connection.rs, WsClientError from error.rs, and build_auth_event, parse_relay_message, OkResponse, and RelayMessage from message.rs as the crate's public surface."
    entry_class: FACT
    evidence:
      - "crates/buzz-ws-client/src/lib.rs"
  - statement: "NostrWsConnection::connect opens a tokio-tungstenite WebSocket to a Nostr relay URL and returns immediately; connect_authenticated additionally calls authenticate, which waits up to AUTH_CHALLENGE_TIMEOUT_SECS (a const of 20, asserted by a compile-time test to be >= 20) for the relay's [\"AUTH\", challenge] frame, builds and signs a kind:22242 NIP-42 event via build_auth_event, sends it as [\"AUTH\", event], and waits up to AUTH_OK_TIMEOUT_SECS (a const of 20, also floor-asserted) for a matching OK response keyed by event id, returning WsClientError::AuthFailed(message) when the relay's OK.accepted is false."
    entry_class: FACT
    evidence:
      - "crates/buzz-ws-client/src/connection.rs"
  - statement: "send_event sends a signed Event as an [\"EVENT\", event] frame and waits up to PUBLISH_OK_TIMEOUT_SECS (a const of 30, floor-asserted) for the relay's OK; publish_event is a one-shot helper that connects, authenticates, sends one event, and disconnects, with the whole sequence additionally bounded by a caller-supplied timeout_secs via tokio::time::timeout."
    entry_class: FACT
    evidence:
      - "crates/buzz-ws-client/src/connection.rs"
  - statement: "message.rs's parse_relay_message parses NIP-01 relay text frames (EVENT, OK, EOSE, CLOSED, NOTICE, AUTH) plus a NIP-45 COUNT frame into a typed RelayMessage enum, returning WsClientError::UnexpectedMessage for any other first-array element or a shape that does not match; build_auth_event constructs a NIP-42 kind:22242 event via nostr::EventBuilder::auth(challenge, relay_url), optionally attaching one caller-supplied NIP-OA auth Tag before signing with the caller's Keys."
    entry_class: FACT
    evidence:
      - "crates/buzz-ws-client/src/message.rs"
  - statement: "error.rs's WsClientError enumerates ten variants -- WebSocket, Json, EventBuilder, Url, Timeout, ConnectionClosed, UnexpectedMessage, AuthFailed, EventRejected, NoAuthChallenge -- covering transport, (de)serialization, and protocol-level failure, derives thiserror::Error, and lib.rs declares #![deny(unsafe_code)] at the crate root."
    entry_class: FACT
    evidence:
      - "crates/buzz-ws-client/src/error.rs"
      - "crates/buzz-ws-client/src/lib.rs"
  - statement: "Exactly three crates in this workspace depend on buzz-ws-client per their own Cargo.toml at this node's recorded revision: buzz-cli (path dependency), buzz-test-client (workspace dependency), and the desktop app's Tauri backend (path dependency aliased buzz_ws_client_pkg). No other crate lists it as a dependency, including buzz-acp and buzz-pairing-cli, both of which depend on tokio-tungstenite directly instead of on this crate."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/Cargo.toml"
      - "crates/buzz-test-client/Cargo.toml"
      - "desktop/src-tauri/Cargo.toml"
      - "crates/buzz-acp/Cargo.toml"
      - "crates/buzz-pairing-cli/Cargo.toml"
  - statement: "buzz-cli's client.rs calls buzz_ws_client::publish_event (fully qualified, no explicit `use` import) inside publish_ephemeral_event, used specifically because the relay rejects ephemeral event kinds (20000-29999) over its HTTP surface; the call passes a 75-second outer timeout, and an inline comment states this is a hard cap sized above the crate's own 20+20+30=70-second inner wait ceilings to absorb connect time and network round-trip overhead."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/client.rs"
  - statement: "desktop/src-tauri/src/native_relay_client.rs is the desktop app's persistent relay connection: run_session loops NostrWsConnection::connect_authenticated with exponential reconnect backoff (resetting the delay on any successful authentication, not only on a clean exit), and run_connection drives one connected socket's REQ/EVENT/CLOSED lifecycle until the socket drops or the session is cancelled; is_read_timeout matches buzz_ws_client_pkg::WsClientError::Timeout to distinguish an idle read from a hard connection failure."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/native_relay_client.rs"
  - statement: "buzz-test-client/src/lib.rs wraps a NostrWsConnection as the `inner` field of its own TestRelayConnection, re-exports parse_relay_message, OkResponse, RelayMessage, and WsClientError from buzz_ws_client, and implements From<WsClientError> for the crate's own TestClientError covering every WsClientError variant -- this is the WebSocket transport the E2E test suite under crates/buzz-test-client/tests/ runs on."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/src/lib.rs"
  - statement: "buzz-ws-client's own in-crate tests are three #[cfg(test)] assertions in connection.rs confirming its three timeout constants meet stated floors (AUTH_CHALLENGE_TIMEOUT_SECS >= 20, AUTH_OK_TIMEOUT_SECS >= 20, PUBLISH_OK_TIMEOUT_SECS >= 30); the crate has no integration-test directory of its own, so its connect/authenticate/send behavior is exercised only through its consumers' test suites."
    entry_class: FACT
    evidence:
      - "crates/buzz-ws-client/src/connection.rs"
  - statement: "desktop/src-tauri/src/native_relay_client_tests.rs exercises NostrWsConnection against a real local TCP stub relay (deliberately not a fake connection, per its own module comment) through the same run_session/run_connection production code path, covering CLOSED-triggered resubscription and REQ-before-CLOSE wire ordering."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/native_relay_client_tests.rs"
  - statement: "crates/buzz-test-client/tests/e2e_relay.rs's test_connect_and_authenticate, test_unauthenticated_rejected, and test_auth_event_kind_rejected exercise buzz-ws-client indirectly through TestRelayConnection against a live relay instance; the same three tests are already cited as representative verification by architecture-flows-websocket-authentication.md and architecture-flows-websocket-connection.md, both merged corpus nodes describing this exact round trip from the relay side."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/e2e_relay.rs"
      - "launchpad/docs/corpus/architecture/flows/websocket-authentication.md"
      - "launchpad/docs/corpus/architecture/flows/websocket-connection.md"
  - statement: "architecture-flows-websocket-authentication.md's own FACT ledger states buzz-ws-client's AUTH_CHALLENGE_TIMEOUT_SECS and AUTH_OK_TIMEOUT_SECS are both 20 seconds, citing crates/buzz-ws-client/src/connection.rs; re-reading that file at this node's own recorded revision confirms both constants are still 20, so no divergence was found between that flow node's description of the client half and the crate's current source."
    entry_class: FACT
    evidence:
      - "crates/buzz-ws-client/src/connection.rs"
      - "launchpad/docs/corpus/architecture/flows/websocket-authentication.md"
  - statement: "architecture/context/nostr-network.md states that 'the crates that do open outbound Nostr WebSocket connections (buzz-acp, buzz-pairing-cli, via buzz-ws-client) connect to buzz-relay or buzz-pair-relay,' citing crates/buzz-pairing-cli/src/main.rs and crates/buzz-ws-client/src/connection.rs; at this node's recorded revision, neither buzz-acp's nor buzz-pairing-cli's Cargo.toml lists buzz-ws-client as a dependency, and buzz-pairing-cli's own Cargo.toml shows it depends on tokio-tungstenite directly. This node's consumer list above was built from fresh inspection of every crate's Cargo.toml, not from that claim."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/context/nostr-network.md"
      - "crates/buzz-acp/Cargo.toml"
      - "crates/buzz-pairing-cli/Cargo.toml"
---

# buzz-ws-client: implementation reference

This node documents `crates/buzz-ws-client`, a workspace crate providing a
minimal NIP-42-capable Nostr WebSocket client, and the piece of it this node
traces: that the crate is the concrete client-side realization of the
NIP-01/NIP-42 connect-and-authenticate round trip already documented from
the relay's side by the corpus's `architecture-flows-websocket-authentication`
and `architecture-flows-websocket-connection` nodes. It does not document
NIP-42 itself (an external, non-Buzz-authored Nostr NIP with no corpus node)
or the relay-side handlers those two flow nodes already own.

## Target

What this crate implements is the **client half of NIP-42** ("Authentication
of clients to relays"), the standard Nostr protocol specification maintained
at [nostr-protocol/nips](https://github.com/nostr-protocol/nips/blob/master/42.md)
outside this repository -- Buzz's own `docs/nips/` directory holds only
Buzz-authored custom NIPs (NIP-OA, NIP-GS, and others), none of them NIP-42,
so there is no corpus node yet for the spec itself and none is invented here.

Within this corpus, the same round trip is already documented from the
relay's side by two merged nodes:

- `architecture-flows-websocket-authentication` -- the NIP-42 challenge/response
  state machine, and the node whose own FACT ledger already names
  `buzz-ws-client` as "the other half of the round trip."
- `architecture-flows-websocket-connection` -- the broader WebSocket
  connection lifecycle (registration, heartbeat, termination) that the
  authentication flow is nested inside.

## Implementation surface

| Component / file / symbol | Realizes | Note |
|---|---|---|
| `connection.rs::NostrWsConnection::connect` | Opens the transport-level WebSocket the rest of the flow runs over. | No NIP-42 involvement; `connect_authenticated` composes this with `authenticate`. |
| `connection.rs::NostrWsConnection::authenticate` | The client side of NIP-42: waits for `["AUTH", challenge]`, builds and sends the signed kind:22242 response, waits for the relay's `OK`. | Timeout floors (20s / 20s) match the constants `architecture-flows-websocket-authentication.md` already cites. |
| `message.rs::build_auth_event` | Constructs the kind:22242 event via `nostr::EventBuilder::auth`, with optional NIP-OA `auth` tag. | Signing itself is delegated to the `nostr` crate's `sign_with_keys`; this crate does not implement Schnorr signing. |
| `message.rs::parse_relay_message` | Parses every NIP-01 relay frame type (`EVENT`, `OK`, `EOSE`, `CLOSED`, `NOTICE`, `AUTH`) plus NIP-45 `COUNT` into `RelayMessage`. | Client-side counterpart to the relay's outbound frame construction; this node does not re-document NIP-01 frame semantics themselves. |
| `connection.rs::NostrWsConnection::send_event` / `publish_event` | Publishes a signed event and waits for the relay's `OK`, after authentication has already completed. | `publish_event` is a one-shot connect+auth+send+disconnect helper; not a persistent-connection API. |
| `error.rs::WsClientError` | Client-side failure taxonomy for every step above (transport, parse, and protocol failure, including `AuthFailed` and `NoAuthChallenge`). | Each consumer (see below) maps these variants into its own error type rather than propagating `WsClientError` directly. |

**Consumers, each realizing a different use of the same crate:**

| Consumer | What it uses | Note |
|---|---|---|
| `buzz-cli` (`crates/buzz-cli/src/client.rs`) | `publish_event`, fully qualified | One-shot ephemeral-event publish, chosen because the relay's HTTP surface rejects ephemeral kinds. |
| desktop app (`desktop/src-tauri/src/native_relay_client.rs`) | `NostrWsConnection::connect_authenticated`, `RelayMessage`, `WsClientError` | A long-lived, reconnecting connection (`run_session`/`run_connection`) driving live subscriptions, not a one-shot publish. |
| `buzz-test-client` (`crates/buzz-test-client/src/lib.rs`) | `NostrWsConnection` (wrapped as `TestRelayConnection.inner`), `RelayMessage`, `OkResponse`, `WsClientError` | The E2E test suite's own WebSocket transport. |

No other workspace crate depends on `buzz-ws-client` -- confirmed by
inspecting `buzz-acp`'s and `buzz-pairing-cli`'s own `Cargo.toml` files,
both of which depend on `tokio-tungstenite` directly for their own,
separate outbound WebSocket use.

## Divergences

**Against the two flow nodes this crate implements:** none found.
`architecture-flows-websocket-authentication.md`'s FACT ledger states this
crate's `AUTH_CHALLENGE_TIMEOUT_SECS` and `AUTH_OK_TIMEOUT_SECS` are both 20
seconds; re-reading `crates/buzz-ws-client/src/connection.rs` at this node's
own recorded revision confirms both constants are unchanged. This was
checked by opening the current source and comparing it against that node's
citation, not assumed from the earlier node's word.

**Against a third corpus node, found while investigating, not this node's
own target:** `architecture/context/nostr-network.md` claims `buzz-acp` and
`buzz-pairing-cli` reach outbound Nostr WebSocket connections "via
buzz-ws-client." At this node's recorded revision that is not what either
crate's `Cargo.toml` shows -- neither depends on `buzz-ws-client`, and
`buzz-pairing-cli` depends on `tokio-tungstenite` directly. This node does
not attempt to correct `nostr-network.md` (out of this task's scope,
per its own Definition of Done: at most one hand-authored canonical
document); it is recorded here because it directly bears on this crate's
own consumer list, and because taking that other node's claim at face
value would have produced a wrong one here.

## Verification

The crate has no dedicated integration-test suite of its own. What exists:

- **In-crate:** three `#[cfg(test)]` assertions in `connection.rs` that
  `AUTH_CHALLENGE_TIMEOUT_SECS`, `AUTH_OK_TIMEOUT_SECS`, and
  `PUBLISH_OK_TIMEOUT_SECS` meet stated floors. These check constants, not
  connect/authenticate/send behavior.
- **Through the desktop consumer:**
  `desktop/src-tauri/src/native_relay_client_tests.rs` runs
  `NostrWsConnection` against a real local TCP stub relay through the same
  `run_session`/`run_connection` path used in production, covering
  CLOSED-triggered resubscription and REQ/CLOSE wire ordering.
- **Through the test-client consumer, end-to-end:**
  `crates/buzz-test-client/tests/e2e_relay.rs`'s `test_connect_and_authenticate`,
  `test_unauthenticated_rejected`, and `test_auth_event_kind_rejected` drive
  `TestRelayConnection` (this crate's `NostrWsConnection`, wrapped) against a
  live relay instance. These are `#[ignore]`d by the repository's convention
  for tests requiring Postgres and Redis, run via `just test`; this node
  links them as representative coverage, not as evidence they were executed
  while authoring it.

## Relationships

- implements: architecture-flows-websocket-authentication
- references: architecture-flows-websocket-connection

## Scope and omissions

**This node covers** what `buzz-ws-client` is responsible for (a minimal
NIP-42-capable WebSocket client to a single Nostr relay: connect, challenge/
response authenticate, publish one event and wait for its `OK`, parse
inbound relay frames), its public entry points, its real consumers as
verified by inspecting their `Cargo.toml` files and call sites, and how its
behavior compares against the corpus's own existing description of the same
round trip from the relay side.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| NIP-42 itself, the protocol specification | external (`nostr-protocol/nips`); no corpus node exists |
| The relay-side connection lifecycle and authentication gates | `architecture-flows-websocket-connection`, `architecture-flows-websocket-authentication` |
| NIP-01 message-level semantics (REQ/subscription matching, EVENT fan-out) | not this crate's concern -- it has no `REQ`-issuing API of its own; that logic lives in each consumer (e.g. desktop's `native_relay_client.rs`) |
| Whether `native_relay_client.rs`'s reconnect/backoff design or `buzz-cli`'s 75-second outer timeout choice are themselves correct or well-tuned | those consumers' own implementation, not this crate |
| Correcting `architecture/context/nostr-network.md`'s incorrect consumer claim | flagged above under *Divergences*; not fixed by this task |

**This crate does NOT own:** WebSocket transport itself (delegated to
`tokio-tungstenite`), Schnorr signing (delegated to the `nostr` crate's
`EventBuilder`/`Keys`), persistent-connection reconnect policy (each
consumer implements its own, as `native_relay_client.rs` does), or NIP-01
subscription/filter semantics.

**Expected but not verified when this node was written:**

- Whether `buzz-cli`'s specific 75-second outer timeout for
  `publish_ephemeral_event` has ever actually been exercised near that
  ceiling in production, versus being a documented-but-untested budget --
  not checked; out of this node's scope, which is what the crate does, not
  how well callers have tuned their own timeouts.
- Whether any workspace crate outside the three consumers named here reaches
  `buzz-ws-client` transitively through a re-export -- checked by `grep`
  across `Cargo.toml` files only, which catches every direct dependency;
  a transitive re-export chain was not separately searched for because none
  of the three consumers' own `lib.rs`/`main.rs` re-export `buzz-ws-client`
  types under a different path.
