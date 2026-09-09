---
id: layers-networking-heartbeat
type: layers
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - operator
evidence:
  - statement: "This node was authored and checked against repository revision 96782d1035f5bcb878edaa4b75b95ccc85ef4ce0."
    entry_class: FACT
    evidence:
      - "commit 96782d1035f5bcb878edaa4b75b95ccc85ef4ce0"
  - statement: "The relay spawns one heartbeat_loop task per WebSocket connection; it drives a tokio::time::interval of Duration::from_secs(30), and on each tick calls missed_pongs.fetch_add(1) and cancels the connection's CancellationToken when the pre-increment value is already 2 or more, logging \"3 missed pongs -- closing connection\"."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/connection.rs"
  - statement: "heartbeat_loop sends its Ping with ctrl_tx.try_send on the small dedicated control channel rather than the data channel, and treats a full control channel as terminal -- it logs \"control channel full -- cannot send Ping, closing\" and cancels rather than blocking or retrying."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/connection.rs"
  - statement: "recv_loop is the other half of the mechanism: an inbound WsMessage::Pong resets missed_pongs to 0 via a store, and an inbound WsMessage::Ping is answered by echoing its payload back as a Pong on the same priority control channel, with a full control channel again treated as terminal (\"control channel full -- cannot send Pong, closing\")."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/connection.rs"
  - statement: "The relay's huddle-audio WebSocket carries a second, independent implementation of the same policy: crates/buzz-relay/src/audio/handler.rs defines HEARTBEAT_INTERVAL = Duration::from_secs(30) and MAX_MISSED_PONGS: u8 = 3, spawns its own heartbeat_loop and its own missed_pongs AtomicU8, and expresses the miss check as fetch_add(1) + 1 >= MAX_MISSED_PONGS where the main connection path uses an unnamed literal 30 and a bare fetch_add(1) >= 2."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/audio/handler.rs"
      - "crates/buzz-relay/src/connection.rs"
  - statement: "Neither relay-side interval nor miss threshold is configurable: both are compile-time constants in Rust source, and the only heartbeat-named environment variables in .env.example are BUZZ_ACP_HEARTBEAT_INTERVAL, BUZZ_ACP_HEARTBEAT_PROMPT and BUZZ_ACP_HEARTBEAT_PROMPT_FILE, which configure the ACP agent harness rather than any WebSocket keepalive."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/connection.rs"
      - "crates/buzz-relay/src/audio/handler.rs"
      - ".env.example"
  - statement: "buzz-ws-client never initiates a Ping: its recv_one and its two deadline-bounded wait loops each answer an inbound Message::Ping by sending Message::Pong with the same payload and then continuing to wait, and every read is bounded instead by a caller-supplied timeout_dur that surfaces as WsClientError::Timeout."
    entry_class: FACT
    evidence:
      - "crates/buzz-ws-client/src/connection.rs"
  - statement: "The Flutter mobile client is the one client in this repository that pings: RelaySocket declares pingInterval = Duration(seconds: 30) with a @visibleForTesting debugPingInterval override, and passes it to IOWebSocketChannel.connect, documenting it as the \"Interval for sending a ping and awaiting its pong before disconnecting.\""
    entry_class: FACT
    evidence:
      - "mobile/lib/shared/relay/relay_socket.dart"
  - statement: "The desktop client is deliberately passive: RelayStallWatchdog's module doc states it \"intentionally does not write to the socket\" because tauri-plugin-websocket 2.4.2 holds a global connection-manager mutex while awaiting send(), and instead relies on inbound relay traffic (naming the relay's heartbeat pings) as the liveness signal; it fires checkIdle on an interval and calls onStall only when no inbound frame has been recorded for idleTimeoutMs."
    entry_class: FACT
    evidence:
      - "desktop/src/shared/api/relayStallWatchdog.ts"
  - statement: "The desktop watchdog's two thresholds are STALL_CHECK_INTERVAL_MS = 10_000 and STALL_IDLE_TIMEOUT_MS = 60_000, described in relayClientTimings.ts as \"Passive liveness thresholds for the relay heartbeat stream\"; relayClientSession wires them in, starts the watchdog after live subscriptions replay, calls recordInbound at the top of handleWsMessage, and on stall sets connection state to \"stalled\" and calls resetConnection."
    entry_class: FACT
    evidence:
      - "desktop/src/shared/api/relayClientTimings.ts"
      - "desktop/src/shared/api/relayClientSession.ts"
  - statement: "The desktop native WebSocket plugin forwards Ping and Pong frames to the JavaScript layer rather than swallowing them: outbound_message maps Message::Ping and Message::Pong to OutboundMessage::Ping and OutboundMessage::Pong, and every non-terminal inbound frame is serialized and pushed into the same FrameBatch that carries Text frames to the on_message channel."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/native_websocket.rs"
  - statement: "Test coverage for this mechanism exists on the client side only: mobile/test/shared/relay/relay_socket_liveness_test.dart drives debugPingInterval and asserts both \"detects a peer that stops answering pings\" and \"keeps an idle but healthy peer connected\", and desktop/src/shared/api/relayStallWatchdog.test.mjs asserts the watchdog sends no probes, stalls on idle, resets on inbound frames, ignores recordInbound while stopped, and is idempotent on start."
    entry_class: FACT
    evidence:
      - "mobile/test/shared/relay/relay_socket_liveness_test.dart"
      - "desktop/src/shared/api/relayStallWatchdog.test.mjs"
  - statement: "Neither relay-side heartbeat_loop has a test: connection.rs's #[cfg(test)] module contains send_loop batching, control-frame ordering, restart-close and REQ-scoping tests but no test naming heartbeat_loop or missed_pongs, and a repository-wide search for those two identifiers under crates/ returns only connection.rs and audio/handler.rs themselves."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/connection.rs"
      - "crates/buzz-relay/src/audio/handler.rs"
  - statement: "A different corpus node, capabilities-presence-presence-heartbeat, is already merged and documents the application-level presence heartbeat -- a periodic kind:20001 status republish on a 60-second interval against a 180-second Redis TTL -- and its own Boundary section names \"the unrelated WebSocket-transport ping/pong keepalive (heartbeat_loop in connection.rs, 30s interval, 3 missed pongs -> disconnect)\" as explicitly out of its scope."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/capabilities/presence/presence-heartbeat.md"
  - statement: "The ACP agent harness adds two further, distinct uses of the word: buzz-acp's config carries heartbeat_interval_secs (BUZZ_ACP_HEARTBEAT_INTERVAL, rejected when non-zero and below 10) which schedules a prompt sent to an agent, and turn_liveness_secs, whose own doc comment says it is \"Seconds between per-turn liveness pings\" and is \"Distinct from heartbeat_interval_secs (agent self-prompting) -- this is the desktop crash-backstop signal.\""
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/config.rs"
      - ".env.example"
  - statement: "architecture-flows-websocket-connection already narrates heartbeat_loop's place in the relay's four-task-per-connection lifecycle, including a Keepalive step and a termination-trigger row for three consecutive missed Pongs, so this node links to that narrative rather than restating it."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/flows/websocket-connection.md"
  - statement: "Because missed_pongs is reset to zero by any inbound Pong and incremented once per 30-second tick before the Ping is sent, a peer that stops answering is cancelled on the third tick after its last Pong -- between roughly 60 and 90 seconds of transport silence, depending on where the last Pong landed within a tick window, rather than a flat 90 seconds."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay/src/connection.rs"
    confidence: 0.75
  - statement: "The mechanism is asymmetric by design rather than by oversight: the relay is the only party that will tear down a connection for transport silence in the desktop direction, because the desktop watchdog deliberately never writes a probe and buzz-ws-client never pings at all, which makes the relay's 30-second Ping the sole traffic keeping the desktop's 60-second idle timer from firing on an otherwise quiet connection."
    entry_class: INFERENCE
    evidence:
      - "desktop/src/shared/api/relayStallWatchdog.ts"
      - "desktop/src/shared/api/relayClientTimings.ts"
      - "crates/buzz-relay/src/connection.rs"
      - "crates/buzz-ws-client/src/connection.rs"
    confidence: 0.8
  - statement: "The two relay-side implementations agreeing on 30 seconds and three misses is a duplicated constant pair rather than a shared policy: the audio path names its constants and the main path inlines an unnamed 30 and an off-by-one-looking >= 2, so the two can drift apart without any compile-time or test-time signal."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay/src/connection.rs"
      - "crates/buzz-relay/src/audio/handler.rs"
    confidence: 0.85
  - statement: "git log attributes heartbeat_loop's introduction to the upstream commit titled \"fix: WebSocket hardening + agent reliability (8 WS bugs, member-only discovery, mention tag fix) (#67)\", which is consistent with recv_loop's surviving inline comment marking the priority-control-channel Pong reply as \"(Bug 7 fix)\"."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "git log -L on crates/buzz-relay/src/connection.rs's heartbeat_loop range, run directly while authoring this node"
  - statement: "Issue #1125's definition of done requires, for a concept-typed node, that the term is defined in one sentence before deeper explanation, that boundaries and what the concept must not be confused with are stated, that the concept is linked to related concepts, implementation and verification, and that examples clarify rather than introduce a second canonical concept."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1125 definition of done"
relationships:
  - type: references
    target: architecture-flows-websocket-connection
  - type: references
    target: capabilities-presence-presence-heartbeat
  - type: references
    target: implementation-crates-buzz-relay
  - type: references
    target: implementation-crates-buzz-ws-client
  - type: references
    target: verification-contracts-websocket
---

# Heartbeat (transport keepalive)

A **heartbeat** in Buzz's networking layer is the periodic WebSocket Ping/Pong exchange
that keeps an otherwise idle connection alive through intermediaries and detects a peer
that has stopped responding, so a connection that is dead at the TCP level is torn down
and rebuilt instead of silently absorbing every message sent into it.

It carries no application payload. It says nothing about who is online, what an agent is
doing, or whether a subscription is healthy — only whether the socket underneath all of
that is still there.

## Definition

The relay drives the heartbeat. For every accepted WebSocket connection it spawns a
`heartbeat_loop` task alongside the send, receive and auth-timeout tasks. That loop
ticks every 30 seconds; on each tick it increments a shared `missed_pongs` counter and
then sends a WebSocket Ping. Any inbound Pong resets the counter to zero. Once three
ticks have elapsed without a Pong arriving, the loop cancels the connection's
`CancellationToken`, which converges on the same teardown path as a client-sent Close
frame. Inbound Pings are answered symmetrically: the receive loop echoes the payload
back as a Pong.

Both the Ping and the answering Pong travel on a small dedicated **control channel**
rather than the ordinary outbound data channel, so keepalive traffic is not queued
behind a backlog of events for a slow reader. A control channel that is itself full is
treated as terminal — the socket writer is stalled, and the connection is cancelled
rather than blocked on.

### What this must not be confused with

The word "heartbeat" names at least four different mechanisms in this repository. They
share a name and nothing else. This node documents only the first.

| Name in code | What it actually is | Where it is documented |
|---|---|---|
| `heartbeat_loop` (`connection.rs`, `audio/handler.rs`) | **This node.** Transport keepalive. WebSocket Ping/Pong, 30s, 3 misses, no payload. | here |
| Presence heartbeat | Application-level liveness. A periodic **kind:20001 status event** republished every 60s against a 180s Redis TTL, carrying `online`/`away`/`offline`. | `capabilities-presence-presence-heartbeat` |
| ACP heartbeat (`heartbeat_interval_secs`, `BUZZ_ACP_HEARTBEAT_INTERVAL`) | A **prompt** the ACP harness sends into a long-running agent session on a timer, to stop the agent's own session idling out. | not yet owned by a corpus node |
| ACP turn liveness (`turn_liveness_secs`) | A per-turn signal the harness emits so the desktop app can detect a crashed agent turn. Its own doc comment calls out that it is distinct from the ACP heartbeat above. | not yet owned by a corpus node |

The presence collision is the one that misleads in practice, because both mechanisms are
periodic, both are called a heartbeat, and both end in a peer being treated as gone.
They differ in every way that matters: the transport heartbeat is a protocol-level frame
with no content, invisible to Nostr subscribers, terminating a **connection**; the
presence heartbeat is a signed Nostr event with a status string in it, fanned out to
subscribers, expiring a **user's status** while the connection carrying it stays open.
A user can be transport-alive and presence-stale, or presence-fresh on one device while
another device's socket is being torn down for missed Pongs.

## How each side behaves

The mechanism is not symmetric, and the asymmetry is deliberate on the desktop side.

| Side | Sends Ping? | Detects a dead peer by | Thresholds |
|---|---|---|---|
| Relay, ordinary WS (`connection.rs`) | Yes, every 30s | 3 consecutive ticks with no Pong | hardcoded `30` and `>= 2` |
| Relay, huddle audio WS (`audio/handler.rs`) | Yes, every 30s | 3 consecutive ticks with no Pong | `HEARTBEAT_INTERVAL`, `MAX_MISSED_PONGS` |
| `buzz-ws-client` (CLI, tests, tooling) | No | Per-operation read deadline → `WsClientError::Timeout` | caller-supplied `timeout_dur` |
| Mobile (Flutter) | Yes, every 30s via `IOWebSocketChannel`'s `pingInterval` | the socket library's own ping/pong timeout | `pingInterval = 30s` |
| Desktop | **No — never writes a probe** | no inbound frame of any kind for 60s | check every 10s, stall at 60s |

Desktop's passivity has a stated cause: the WebSocket plugin holds a global
connection-manager mutex while awaiting a `send()`, so a probe written into a half-open
TCP path can block later reconnects from registering. Rather than risk that, the desktop
watchdog only *listens*, treating any inbound frame as proof of life — and because the
native transport forwards Ping and Pong frames up to JavaScript alongside Text frames,
the relay's own 30-second Ping is what feeds it. The relay's heartbeat is therefore
load-bearing for desktop stall detection, not merely a relay-side safety net.

## Use cases

Understanding the transport heartbeat matters when:

- **A connection drops with no application-level error.** A `3 missed pongs` warning in
  relay logs means the socket went silent, not that a handler failed. The event that
  looks lost was never rejected — it was written into a connection already being torn
  down.
- **Diagnosing "the client thinks it is connected and the relay disagrees".** The two
  sides use different detectors with different windows: the relay cancels after roughly
  60–90 seconds of missed Pongs, while a desktop client declares a stall after 60
  seconds without *any* inbound frame. On a quiet community those windows are close
  enough that either side may notice first.
- **Reasoning about idle connections behind proxies.** A connection with no traffic for
  minutes is normal in Buzz — most communities are quiet most of the time. The 30-second
  Ping is what keeps such a connection from being reaped by an intermediary.
- **Choosing a timeout when writing a client.** `buzz-ws-client` does not ping, so any
  tool built on it depends entirely on its own per-operation deadline; a long-lived
  consumer of it inherits no liveness detection for free.
- **Reading a "heartbeat" identifier in unfamiliar code.** The disambiguation table
  above is the fastest way to tell which of the four mechanisms a symbol belongs to
  before changing it.

## Scope and omissions

**This node covers** what the transport heartbeat is, the policy both relay-side
implementations apply, how each client participates or declines to, why the desktop side
is passive, and how the name is disambiguated from the three other "heartbeat"
mechanisms in the repository.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The full per-connection lifecycle the heartbeat task sits inside — semaphore admission, NIP-42 challenge, the four-task structure, and the shared cancellation/cleanup path | `architecture-flows-websocket-connection` |
| Application-level presence liveness (kind:20001 republish, Redis TTL, `online`/`away`/`offline`) | `capabilities-presence-presence-heartbeat` |
| The relay crate's wider responsibilities, including `ConnectionState` and `AUTH_TIMEOUT` | `implementation-crates-buzz-relay` |
| `buzz-ws-client`'s connect/auth/publish API beyond its Ping handling and read deadlines | `implementation-crates-buzz-ws-client` |
| The WebSocket protocol contract and what is actually enforced in CI | `verification-contracts-websocket` |
| Reconnection and backoff after a heartbeat-triggered teardown (`relayReconnectPolicy`, `RECONNECT_BASE_DELAY_MS`, `BACKOFF_RESET_STABLE_MS`) | no corpus node yet |
| The ACP heartbeat prompt and ACP turn-liveness signal | no corpus node yet; named above only to prevent confusion |
| Whether the two duplicated relay-side heartbeat constants should be unified | an implementation question; not decided here |

**Expected but not verified when this node was written:**

- **No test exercises either relay-side `heartbeat_loop`.** `connection.rs`'s test
  module covers `send_loop` batching, control-frame ordering and restart-close
  acknowledgement, but nothing drives the 30-second interval, the `missed_pongs`
  arithmetic, or the cancel-on-third-miss path. The claim that a dead peer is dropped on
  the third tick rests on reading the code, not on a test that would fail if the
  arithmetic changed. The audio path's copy is likewise untested.
- **Whether the desktop actually answers the relay's Ping with a Pong was not
  confirmed.** The native transport forwards the Ping *up* to JavaScript, and no
  application code in `desktop/src` sends a Pong; if a reply is sent at all it is the
  underlying tungstenite sink doing it automatically, which was not verified in this
  repository. If no Pong is sent, the relay would cancel a healthy desktop connection
  every 60–90 seconds — which contradicts observed behaviour, so a reply almost
  certainly happens somewhere, but this node cannot say where from evidence it opened.
- **The 60–90 second detection window was reasoned from the code, not measured.** In
  particular `tokio::time::interval`'s first tick completing immediately, and the
  ordering of the increment before the send, were read but not exercised.
- **No end-to-end test of a stalled connection across the real relay and a real client
  was found.** Both existing tests are unit-scoped to one side.
- **Web (`web/`) client behaviour was not checked.** The client-side evidence here is
  desktop, mobile and `buzz-ws-client` only.
