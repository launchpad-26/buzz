---
id: architecture-flows-websocket-connection
type: architecture
status: draft
origin: launchpad
audiences:
  - developer
  - operator
  - agent
evidence:
  - statement: "This node was authored and checked against repository revision a44cf52fc740ebebbdd671427480d14f0bce0115 on the launchpad branch."
    entry_class: FACT
    evidence:
      - "commit a44cf52fc740ebebbdd671427480d14f0bce0115"
  - statement: "A single axum handler content-negotiates every request to the relay's bare host route: it serves the admin SPA for the admin host, a NIP-11 JSON document for `Accept: application/nostr+json`, and otherwise attempts a WebSocket upgrade."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs"
  - statement: "The connection is bound to its community from the request Host header via `tenant::bind_community` before any WebSocket upgrade is attempted; an unmapped or unresolved host fails closed with a generic 404 that never echoes the host or distinguishes 'unmapped' from 'lookup error'."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs"
  - statement: "A shutting-down relay pod refuses new WebSocket upgrades with 503, even though only readiness already routes traffic away, to close the pre-drain grace-window gap where in-flight upgrades still reach the handler."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs"
  - statement: "Once upgraded, `handle_connection` allocates a connection id and registers the socket with the community connection registry via `run_registered_community_connection`, which checks `state.db.is_community_active` and cancels the connection immediately if the community is not active, before any client frame is processed."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/connection.rs"
      - "crates/buzz-relay/src/state.rs"
  - statement: "A global connection-count semaphore (`state.conn_semaphore`) is acquired before any further setup; if the process-wide connection limit is already reached, the socket is rejected without ever sending a challenge."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/connection.rs"
  - statement: "The relay immediately generates a random NIP-42 challenge and sends `[\"AUTH\", <challenge>]` as the connection's first outbound frame; the per-connection `active` gauge is only incremented, and the connection only registered with the connection manager, after that send succeeds, so an immediate client disconnect before the challenge is delivered leaks neither a gauge count nor a registry entry."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/connection.rs"
      - "crates/buzz-relay/src/protocol.rs"
  - statement: "A 5-second `AUTH_TIMEOUT` timer starts alongside the challenge send; if the connection has not reached `AuthState::Authenticated` when it fires, the relay cancels the connection unilaterally with no further protocol message."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/connection.rs"
  - statement: "The connection begins in `AuthState::Pending { challenge }`, per NIP-42 (client signs a kind:22242 event embedding the received challenge and this relay's URL); the relay's own AUTH-kind constant matches kind:22242."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/connection.rs"
      - "crates/buzz-auth/src/nip42.rs"
      - "crates/buzz-auth/src/lib.rs"
  - statement: "A client AUTH event is handled by `handle_auth`, which performs pure NIP-42 Schnorr-signature verification against the recorded challenge and the tenant's expected relay URL before any database lookup runs; a second AUTH after the connection is already `Authenticated` or already `Failed` is rejected with an `OK false` frame and no state change."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/auth.rs"
  - statement: "After NIP-42 verification succeeds, `handle_auth` runs three further gates in order before marking the connection authenticated: a community ban check (including a NIP-OA owner-ban cascade extracted from the event's self-proving `auth` tag), an optional pubkey allowlist check, and a relay-membership check; a database error at the ban gate fails closed (denies) rather than treating the lookup failure as 'not banned'."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/auth.rs"
  - statement: "A ban denial is delivered as an `OK false \"blocked: ...\"` frame queued on the connection's priority control channel (not the ordinary data channel, to avoid racing the following cancel), and the connection is cancelled immediately afterward; every other authentication failure sets `AuthState::Failed` and sends an `OK false \"auth-required: ...\"` frame without cancelling the socket."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/auth.rs"
      - "crates/buzz-relay/src/connection.rs"
  - statement: "Only after all gates pass does `handle_auth` set `AuthState::Authenticated(auth_ctx)` and register the authenticated pubkey with the connection manager via `set_authenticated_pubkey`; every message type other than AUTH is otherwise processed regardless of auth state, but downstream handlers (EVENT, REQ, COUNT) independently require authentication before doing anything privileged."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/auth.rs"
      - "crates/buzz-relay/src/handlers/count.rs"
  - statement: "Once established, the connection runs four concurrent tasks around a single `CancellationToken`: `send_loop` (writes to the socket, prioritizing control frames over data and draining any queued control frame before sending the final Close on cancellation), `heartbeat_loop` (pings every 30 seconds and cancels the connection after 3 consecutive missed pongs), the auth-timeout task, and `recv_loop` (reads and dispatches inbound frames) — `recv_loop` runs on the task calling `handle_active_connection` and the other three are spawned."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/connection.rs"
  - statement: "`recv_loop` dispatches each inbound frame by parsed `ClientMessage` variant: AUTH runs synchronously inline; EVENT, REQ, and COUNT each first acquire a bounded `handler_semaphore` permit (rejecting with a rate-limited notice if none is available) and then run on a spawned task carrying a tracing span; CLOSE runs synchronously inline."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/connection.rs"
  - statement: "For EVENT, REQ, and COUNT from an already-authenticated connection, `enforce_ws_admission` additionally checks a per-principal sliding-window rate limit (human vs. agent message budgets differ) before the message reaches its handler; a limit violation returns a rate-limited CLOSED/NOTICE frame and the message is dropped without reaching the handler."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/connection.rs"
      - "crates/buzz-relay/src/admission.rs"
  - statement: "Any inbound text or binary frame larger than the configured `max_frame_bytes` is rejected with a NOTICE and the connection's `recv_loop` breaks, terminating the connection; binary frames are otherwise accepted and treated as text after a UTF-8 decode attempt, since some Nostr client libraries send text payloads inside binary frames even though NIP-01 itself is text-only."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/connection.rs"
  - statement: "A slow client (send buffer consistently full) is disconnected after a configurable number of consecutive backpressure events (`grace_limit`, from `Config::slow_client_grace_limit`); each successful send resets the counter."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/connection.rs"
  - statement: "Ordinary connection termination — client-initiated Close frame, a WebSocket read error, the auth timeout, a missed-heartbeat cancellation, an oversized frame, or sustained backpressure — all converge on the same `cancel` token; `handle_active_connection`'s cleanup path always runs afterward: it awaits the send/heartbeat/auth-timeout tasks, removes the connection's subscriptions from the subscription registry (releasing any pubsub topics with no remaining subscriber), deregisters from the connection manager, decrements the active-connections gauge, and — if the connection had authenticated — clears presence for that pubkey once no other connection from the same pubkey remains in the community."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/connection.rs"
  - statement: "Two externally-triggered abort paths exist beyond the client's own disconnect: `ConnectionManager::disconnect_pubkey` (used by moderation/ban enforcement) best-effort delivers an `OK false` reason frame on the priority control channel before cancelling every connection for that pubkey in the community, and `CommunityConnectionRegistry::disconnect_community` (community deletion) records a `CommunityDisconnectReason::CommunityDeleted` and cancels every connection for that community, causing `send_loop` to emit a WebSocket Close frame with close code POLICY and reason \"community deleted\" instead of a bare unadorned close."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/state.rs"
  - statement: "No graceful WebSocket close-frame handshake is required from the client for cleanup to run correctly — `recv_loop` treats a client Close frame, a read error, and `None` (stream end) identically, all breaking the loop and falling through to the same cleanup path."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/connection.rs"
  - statement: "`test_connect_and_authenticate` in the E2E relay suite exercises the connect → AUTH-challenge → signed-AUTH-response → authenticated happy path against a real relay instance; `test_unauthenticated_rejected` and `test_auth_event_kind_rejected` exercise rejection paths."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/e2e_relay.rs"
  - statement: "Treating the four-task-per-connection design (send/heartbeat/auth-timeout/recv around one shared cancellation token) as the intended general shape for future relay-side per-connection state, rather than an incidental implementation detail, is a reasonable reading of the code's structure and comments but was not confirmed against any design document."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay/src/connection.rs"
    confidence: 0.6
---

# WebSocket connection flow

How a client establishes, authenticates, and eventually terminates a
NIP-01/NIP-42 WebSocket connection to `buzz-relay`. This node describes the
one flow — connection lifecycle and its authentication gate — as a single
independently maintainable idea; it does not describe the NIP-01 message
protocol's REQ/EVENT/COUNT semantics themselves (see the relevant handler
modules) or the moderation/ban system's own rules (only where they cross
this flow's trust boundary).

## Trigger

A client opens a WebSocket connection to the relay's bare host route
(`/`). The same route also serves the admin SPA (for the configured admin
host) and a NIP-11 relay-information JSON document (`Accept:
application/nostr+json`); a request that is none of those and successfully
completes the WebSocket upgrade handshake is what starts this flow
(`crates/buzz-relay/src/router.rs`, `nip11_or_ws_handler`).

## Preconditions

Before the upgrade is attempted:

1. **Host-based tenant binding.** The request's `Host` header is resolved to
   a community via `tenant::bind_community`. This runs *before* the upgrade
   and before any client frame is read — an unmapped or failed lookup is
   rejected with a generic 404 that never echoes the host, so an
   unauthenticated caller cannot probe which communities are configured on
   a deployment.
2. **Not shutting down.** If the process has begun a graceful shutdown, the
   upgrade is refused with 503 even though readiness has already flagged
   the pod unhealthy — this closes the window where an in-flight upgrade
   still reaches the handler during the pre-drain grace period.
3. **Community still active.** Immediately after upgrade, before any client
   frame is processed, `run_registered_community_connection` calls
   `state.db.is_community_active`; a `false` or error result cancels the
   connection with no further protocol interaction.
4. **Connection budget available.** A process-wide semaphore
   (`state.conn_semaphore`) must have a permit free, or the socket is
   dropped before a challenge is ever sent.

## Ordered interactions and state movement

1. **Registration and challenge.** `handle_connection` allocates a
   connection id, and `handle_active_connection` builds per-connection
   channels (data, control, restart) and a `ConnectionState` whose
   `auth_state` starts as `AuthState::Pending { challenge }` with a freshly
   generated random challenge. The relay sends `["AUTH", <challenge>]` as
   the first outbound frame. The active-connections gauge is incremented,
   and the connection is registered with the connection manager, **only
   after** that send succeeds — an immediate disconnect before delivery
   leaves neither a leaked gauge count nor a leaked registry entry.
2. **Concurrent task setup.** Four tasks now run around one shared
   `CancellationToken`:
   - `send_loop` — writes outbound frames, draining control frames ahead of
     data, and (on cancellation) drains any remaining control frames before
     sending the final Close.
   - `heartbeat_loop` — sends a WebSocket Ping every 30 seconds; three
     consecutive missed Pongs cancel the connection.
   - the auth-timeout task — a 5-second (`AUTH_TIMEOUT`) one-shot timer;
     if the connection is not `Authenticated` when it fires, it cancels the
     connection.
   - `recv_loop` — reads and dispatches inbound frames (runs on the calling
     task, not spawned).
3. **Client sends a signed AUTH event.** Per NIP-42, the client signs a
   kind:22242 event embedding the received challenge and the relay's URL.
   `handle_text_message` parses the frame and, for `ClientMessage::Auth`,
   calls `handlers::auth::handle_auth` synchronously (not spawned, so no
   tracing context is lost). A second AUTH sent while already
   `Authenticated` or already `Failed` is rejected with `OK false` and no
   state change.
4. **NIP-42 verification, then three further gates.** `handle_auth` first
   performs pure Schnorr-signature verification against the recorded
   challenge and tenant relay URL — no database access yet. On success it
   runs, in order: a community ban check (with a NIP-OA owner-ban cascade
   read from the event's self-proving `auth` tag, so a banned owner's agent
   is blocked too), an optional pubkey-allowlist check, and a
   relay-membership check. A ban denial is queued as an `OK false
   "blocked: ..."` frame on the **control** channel (ahead of data, to
   avoid a race with the following cancel) and the connection is cancelled
   immediately. Every other failure sets `AuthState::Failed` and sends `OK
   false "auth-required: ..."` without cancelling the socket — the client
   may retry once more before the auth-timeout task cancels it.
5. **Authenticated.** Once every gate passes, `handle_auth` sets
   `AuthState::Authenticated(auth_ctx)` and registers the pubkey with the
   connection manager (`set_authenticated_pubkey`), enabling
   pubkey-scoped lookups (e.g. "all connections for this pubkey in this
   community", used by ban enforcement and presence cleanup).
6. **Steady-state message dispatch.** For every subsequent inbound frame,
   `recv_loop` enforces the configured `max_frame_bytes` limit (oversized
   frames end the connection with a NOTICE), then `handle_text_message`
   parses and routes by `ClientMessage` variant: AUTH runs inline; EVENT,
   REQ, and COUNT each acquire a bounded `handler_semaphore` permit (a
   rate-limited NOTICE/CLOSED is returned and the message dropped if none
   is free) and run on a spawned, span-instrumented task; CLOSE runs
   inline. For an authenticated connection, EVENT/REQ/COUNT additionally
   pass through `enforce_ws_admission`, which checks a per-principal
   sliding-window rate limit (separate human vs. agent budgets) before the
   message reaches its handler.
7. **Keepalive.** Ping/Pong frames are handled independently of the message
   protocol: an inbound Pong resets the missed-pong counter; an inbound
   Ping is answered with a Pong on the priority control channel so it is
   not starved behind a full data buffer.

## Trust-boundary crossings

- **Host → tenant.** The `Host` header is the sole, non-overridable input
  that binds a socket to a community, resolved once before any frame is
  read. No later client input can move a connection between tenants.
- **Anonymous → NIP-42-authenticated.** The move from `AuthState::Pending`
  to `AuthState::Authenticated` is the connection's core authorization
  boundary crossing: pure cryptographic verification (Schnorr signature
  over the challenge and relay URL) gates everything that follows.
- **Authenticated → community-authorized.** Passing NIP-42 verification is
  necessary but not sufficient — the ban check, allowlist check, and
  relay-membership check are three further authorization gates run inside
  `handle_auth` before the connection is treated as authenticated for
  protocol purposes. A NIP-OA agent's ban status is cascaded from its
  cryptographically-proven owner, read out of the event's own signed `auth`
  tag with no separate database round trip for the delegation itself (only
  for the ban-state lookup).
- **Fail-closed on lookup error.** A database error at the ban-check gate
  is treated as a denial, not as "not banned" — the same fail-closed
  posture the relay's ingest write path uses.

## Failure, abort, and rollback behavior

There is no partial or rolled-back state to unwind — every failure mode
ends in either "connection stays open in a non-authenticated state" or
"connection is cancelled," never a half-registered connection:

| Trigger | Behavior |
|---|---|
| Community not active at registration | Cancelled immediately, no challenge sent, no registry entry. |
| Connection limit reached | Socket dropped before a challenge is sent. |
| Client disconnects before challenge delivery | No gauge increment, no connection-manager registration — nothing to clean up. |
| NIP-42 signature invalid | `AuthState::Failed`; `OK false "auth-required: ..."`; socket stays open (client may retry, subject to the auth timeout). |
| Ban / NIP-OA owner ban | `OK false "blocked: ..."` queued on the control channel, then immediate cancel. |
| Allowlist or relay-membership denial | `AuthState::Failed`; `OK false` with the specific reason; socket stays open. |
| Ban-state DB lookup errors | Denied (fail-closed), reported as `error: internal error checking restriction state`, not conflated with an actual ban. |
| 5s auth timeout with no successful AUTH | Connection cancelled unilaterally, no further protocol frame. |
| 3 consecutive missed heartbeat Pongs | Connection cancelled. |
| Oversized inbound frame | NOTICE sent, `recv_loop` breaks, connection ends. |
| Sustained backpressure (`grace_limit` consecutive full-buffer sends) | Connection cancelled; each successful send resets the counter. |
| Client Close frame, stream end, or read error | `recv_loop` breaks identically for all three; same cleanup path runs. |
| External ban disconnect (`disconnect_pubkey`) | Best-effort `OK false` reason frame on the control channel, then cancel — delivery is not guaranteed if the control channel is already full. |
| Community deleted mid-connection (`disconnect_community`) | `CommunityDisconnectReason::CommunityDeleted` recorded; `send_loop` emits a WebSocket Close with code `POLICY` and reason "community deleted" instead of a bare close. |

**Cleanup always runs once `cancel` fires**, regardless of which path
triggered it: `handle_active_connection` awaits the send/heartbeat/
auth-timeout tasks, removes the connection's subscriptions (releasing any
pubsub topics with no remaining subscriber), deregisters from the
connection manager, decrements the active-connections gauge, and — for a
connection that had authenticated — clears presence for that pubkey once no
sibling connection for the same pubkey remains in the community.

## Representative verification

- `crates/buzz-test-client/tests/e2e_relay.rs::test_connect_and_authenticate`
  — connect, receive the AUTH challenge, respond with a signed AUTH event,
  and confirm the authenticated state, against a real relay instance.
- `crates/buzz-test-client/tests/e2e_relay.rs::test_unauthenticated_rejected`
  — confirms privileged operations are refused before authentication.
- `crates/buzz-test-client/tests/e2e_relay.rs::test_auth_event_kind_rejected`
  — confirms a non-kind:22242 event on the AUTH path is rejected.

## Related corpus nodes

No `relationships` entry is declared. The only nodes merged in the corpus
at the revision above are `corpus-agents`, `corpus-readme`,
`corpus-schema-overview`, `corpus-standard-confidence`, and
`corpus-standard-decision-references` (per
`launchpad/docs/corpus/schema/relationships.schema.json` for the available
types) — none of which this flow node has a typed relationship to. This is
checked, not assumed, per `launchpad/docs/corpus/AGENTS.md`'s warning that
"nothing to point at" stops being true the moment a sibling node merges.

## Scope and omissions

**Covers:** the WebSocket connection lifecycle from the initial upgrade
request through NIP-42 authentication and its authorization gates, to
every termination path and the cleanup that follows.

**Does not cover, and these are gaps rather than silence:**

- The NIP-01 message-level semantics of EVENT, REQ, COUNT, and CLOSE
  themselves (subscription matching, fan-out, filter evaluation) — owned
  by their respective handler modules and any corpus node written against
  them.
- The moderation/ban system's own rules for how a ban is created or
  lifted — only the ban gate's effect *on this flow* is described here.
- The audio/huddle WebSocket handler (`crates/buzz-relay/src/audio/handler.rs`)
  and the git smart-HTTP transport, which are separate connection flows
  with their own preconditions.
- The exact numeric values of `max_frame_bytes`, `send_buffer_size`, and
  `slow_client_grace_limit` — these are operator-configurable
  (`crates/buzz-relay/src/config.rs`) and were not verified as fixed
  defaults worth citing as facts here.

**Expected but not verified when this node was written:** whether the
four-task-per-connection design is documented anywhere as an intentional
general pattern for future relay-side connection state, versus being this
flow's own incidental structure — recorded above as an `INFERENCE` at
confidence 0.6, not a `FACT`, because no design document was found to
confirm or deny it.
