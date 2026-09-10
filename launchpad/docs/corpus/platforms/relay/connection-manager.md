---
id: platforms-relay-connection-manager
type: platforms
status: draft
origin: launchpad
audiences:
  - developer
  - operator
  - agent
evidence:
  - statement: "This node was authored and checked against repository revision 131b02f989684117d9ab1dd426f1673fa638e523."
    entry_class: FACT
    evidence:
      - "commit 131b02f989684117d9ab1dd426f1673fa638e523"
  - statement: "node.schema.json's type enum has thirteen members, including platforms; at the recorded revision, launchpad/docs/corpus/templates/ contains no platforms-specific template, so per AGENTS.md's documented no-template path this node is written against node.schema.json directly rather than against an authoritative platforms template."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
      - "launchpad/docs/corpus/AGENTS.md"
  - statement: "templates/component.md's own front matter, section shape (Responsibility, Public interface, Dependencies, Boundary, Relationships, Scope and omissions) and its stated subject -- one software component documented as a standalone knowledge artifact, its responsibility/interface/dependencies -- is a structurally close analog for this node's subject, even though that template itself directs type: implementation rather than platforms; this node borrows the shape but not the type, since node.schema.json's platforms surface (not implementation) is where a relay platform's own components are being catalogued in this corpus, per convention across the platforms/** batch this task is part of."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/templates/component.md"
      - "launchpad/docs/corpus/schema/node.schema.json"
    confidence: 0.7
  - statement: "The corpus node architecture-flows-websocket-connection already exists on origin/launchpad and documents the WebSocket connection's full connect -> NIP-42-authenticate -> terminate request/response sequence, including the moments at which handle_active_connection calls into the connection manager (registration after challenge send, deregistration and pubkey lookup during cleanup, the four-task-per-connection shape, and the failure/abort table); this node does not restate that sequence and instead documents the connection-manager and community-connection-registry components themselves -- their data model, full public interface, cross-connection-type sharing, cross-pod fan-out, graceful-drain mechanics, and periodic revalidation -- which the flow node does not describe at that level of detail."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/flows/websocket-connection.md"
  - statement: "ConnectionManager is a struct in buzz-relay's shared application-state module holding a DashMap of live Nostr WebSocket connections keyed by connection UUID (each entry: outbound data/control senders, an optional restart-close sender, a CancellationToken, the resolved community id, a shared backpressure counter, the connection's subscription map, an authenticated-pubkey slot, and its slow-client grace limit), plus a sticky draining flag; its own doc comment states it 'tracks active Nostr WebSocket connections and provides message routing by connection ID.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/state.rs:93-111"
      - "crates/buzz-relay/src/state.rs:236-243"
  - statement: "CommunityConnectionRegistry is a separate, lighter-weight struct holding a DashMap from connection UUID to (community id, CommunityConnectionControl); its own doc comment states it is a 'community-scoped lifecycle registry shared by every long-lived socket type,' and its register() method returns a CommunityConnectionGuard whose Drop impl removes the entry on every exit path, including an early return or panic unwind."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/state.rs:113-171"
      - "crates/buzz-relay/src/state.rs:173-183"
  - statement: "The two registries are not the same thing tracking the same connections twice for the same reason: ConnectionManager is Nostr-WebSocket-specific (it stores per-connection Nostr protocol state such as the subscription map and authenticated pubkey, used for message routing and fan-out), while CommunityConnectionRegistry is generic to any long-lived socket type and is shared by both the Nostr WebSocket handler and the audio/huddle handler, which registers with it via run_registered_community_connection but never touches ConnectionManager directly."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/connection.rs:219-229"
      - "crates/buzz-relay/src/audio/handler.rs:157"
  - statement: "run_registered_community_connection is the shared entry point both socket types use: it registers with CommunityConnectionRegistry, then durably revalidates the community via a caller-supplied check_active closure, cancelling immediately if the community is not active, before ever invoking the caller's run closure; its doc comment names this ordering 'the archival admission invariant: archive-before-query is observed by the query, while archive-after-registration sees the token.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/state.rs:185-213"
  - statement: "buzz-relay/src/connection.rs registers a WebSocket connection with ConnectionManager only after the initial AUTH-challenge send succeeds (so an immediate disconnect leaks neither a gauge nor a registry entry), and deregisters it, after the four per-connection tasks have all been awaited, in the same cleanup block that also releases the connection's pubsub subscriptions and clears presence for the pubkey if no sibling connection for it remains."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/connection.rs:214-229"
      - "crates/buzz-relay/src/connection.rs:283-316"
  - statement: "ConnectionManager exposes connection_ids_for_pubkey_in_community, pubkey_for_conn, and pubkey_for -- all read-only lookups over the same authenticated_pubkey slot -- plus community_for_conn and subscriptions_for, used by handler modules such as handlers/event.rs and handlers/side_effects.rs to check membership of a pubkey in a community, resolve which channels/topics a live connection is subscribed to, and route ban/moderation side effects to the right sockets."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/state.rs:316-351"
      - "crates/buzz-relay/src/state.rs:517-529"
      - "crates/buzz-relay/src/handlers/event.rs:129"
      - "crates/buzz-relay/src/handlers/side_effects.rs:117-158"
  - statement: "ConnectionManager::disconnect_pubkey closes every live connection authenticated as a given pubkey within one community, first best-effort-delivering an OK false reason frame on that connection's priority control channel (queued ahead of the send loop's cancel branch) before cancelling it; its doc comment cites this as the mechanism for live ban enforcement, and states the community filter is 'the tenant fence: one pod holds sockets for many communities, and the same pubkey may be live in several,' so a ban in one community must never close a session the same member holds in another."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/state.rs:353-395"
  - statement: "AppState::disconnect_pubkey_clusterwide is the single sanctioned entry point for live ban enforcement: it calls the pod-local ConnectionManager::disconnect_pubkey and then fire-and-forget publishes a ConnControl::DisconnectPubkey command over Redis pub/sub so every other relay pod closes its own matching sockets too; its doc comment states 'Callers must not invoke the pod-local conn_manager.disconnect_pubkey directly -- doing so closes sockets only on the pod that processed the ban and silently drops the cluster-wide half,' and that a dropped publish is backstopped by the durable ban row rejecting the member's next auth attempt."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/state.rs:1149-1198"
  - statement: "AppState::disconnect_community_clusterwide is the analogous entry point for community archival/deletion: it calls CommunityConnectionRegistry::disconnect_community locally, then awaits (rather than fire-and-forgets) publishing ConnControl::DisconnectCommunity over Redis, so the archive API can distinguish durable-state completion from propagation completion and offer a retryable response on publish failure."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/state.rs:1200-1217"
  - statement: "buzz-relay's main.rs subscribes to the cross-pod connection-control channel and, on receiving ConnControl::DisconnectCommunity, calls state.community_connections.disconnect_community; on receiving ConnControl::DisconnectPubkey, calls state.conn_manager.disconnect_pubkey with the carried community id, pubkey, event id, and reason -- this is the receiving half of the cluster-wide fan-out the two AppState methods above publish."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:970-1005"
  - statement: "CommunityConnectionRegistry::disconnect_community, when invoked (whether locally by AppState or remotely via the cross-pod consumer above), sets a per-socket disconnect-reason watch channel to CommunityDisconnectReason::CommunityDeleted before cancelling; the writer task reads that reason to emit a WebSocket close frame with code POLICY and reason 'community deleted' instead of a bare unattributed close."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/state.rs:39-86"
      - "crates/buzz-relay/src/state.rs:151-162"
  - statement: "AppState::revalidate_live_communities is a periodic durable-state backstop for Redis pub/sub's lossy offline-subscriber semantics: it revalidates every community currently holding live sockets in CommunityConnectionRegistry against the database directly (state.db.is_community_active), disconnecting any that are no longer active and logging -- without disconnecting -- any community whose database check itself failed, so a pod that missed a publish still converges once its own DB query succeeds; it is driven on a fixed period by run_community_revalidator in main.rs."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/state.rs:1219-1234"
      - "crates/buzz-relay/src/main.rs:1208-1220"
  - statement: "ConnectionManager::drain_all closes every live connection synchronously and all at once with a WebSocket close code 1012 (Service Restart), setting the sticky draining flag first so any registration racing the drain snapshot self-signals its own immediate close instead of being missed; this is the default graceful-shutdown path used when BUZZ_DRAIN_JITTER_MS is unset or zero."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/state.rs:397-431"
  - statement: "ConnectionManager::drain_all_jittered is the alternative graceful-shutdown path (used when BUZZ_DRAIN_JITTER_MS is greater than zero) that spreads each connection's 1012 close across a uniform random delay in [1, jitter_ms] to avoid a thundering-herd reconnect burst; each delayed close is delivered over the connection's dedicated RestartClose channel and drain awaits a flush acknowledgement (bounded by RESTART_CLOSE_ACK_TIMEOUT) before considering that connection closed, falling back to plain cancellation if the channel is full/closed or the acknowledgement times out."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/state.rs:433-507"
  - statement: "main.rs's shutdown sequence calls drain_conn_manager.drain_all() when the jitter duration is zero and drain_conn_manager.drain_all_jittered(drain_jitter_ms).await otherwise, inside a graceful-drain window backstopped by a hard-shutdown timer that force-exits the process if the drain does not complete in time."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:1340-1361"
  - statement: "ConnectionManager::per_community_ws_connections and per_community_users_online snapshot, respectively, the live connection count and the count of distinct authenticated pubkeys per community by iterating the connection map once; main.rs's usage poller calls both to publish per-community online-presence metrics."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/state.rs:531-564"
      - "crates/buzz-relay/src/main.rs:1549-1550"
  - statement: "ConnectionManager::send_to and send_to_text_bytes are the fan-out send path: both route through the same private try_send_ws_message, which resets a connection's shared backpressure counter on a successful send and, on a full buffer, increments that counter and cancels the connection once it reaches the connection's own grace_limit -- the same counter and cancellation path a connection's own direct ConnectionState::send() uses, confirmed by the test shared_counter_between_direct_and_fanout."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/state.rs:573-619"
      - "crates/buzz-relay/src/state.rs:1491-1552"
  - statement: "buzz-relay/Cargo.toml declares dashmap, tokio (with its mpsc/watch/Semaphore primitives), tokio-util (for CancellationToken), and uuid as dependencies -- the concrete building blocks ConnectionManager and CommunityConnectionRegistry are built from."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/Cargo.toml:32"
      - "crates/buzz-relay/Cargo.toml:36"
      - "crates/buzz-relay/Cargo.toml:50"
      - "crates/buzz-relay/Cargo.toml:52"
  - statement: "buzz-relay/src/state.rs's unit test suite exercises the connection manager and registry directly, including send_to_resets_grace_counter_on_success, send_to_increments_grace_counter_on_full, send_to_cancels_after_grace_limit, tracks_connections_by_authenticated_pubkey_within_community, disconnect_pubkey_closes_matching_conns_with_reason, disconnect_pubkey_ignores_non_matching_conns, disconnect_pubkey_is_fenced_to_the_banning_community, community_lifecycle_disconnect_covers_socket_types_and_preserves_tenant_fence, community_lifecycle_guard_deregisters_on_early_return, drain_all_sends_restart_close_and_cancels_every_conn, drain_all_full_control_buffer_still_cancels, register_after_drain_self_signals_restart_close_and_cancel, drain_all_is_immediate, drain_all_jittered_waits_for_writer_acknowledgement_without_cancelling, drain_all_jittered_cancels_when_restart_channel_is_full_or_closed, drain_all_jittered_cancels_when_flush_ack_times_out, and drain_all_jittered_defers_close_until_within_jitter_window."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/state.rs:1443-1490"
      - "crates/buzz-relay/src/state.rs:1554-1556"
      - "crates/buzz-relay/src/state.rs:1727-1980"
      - "crates/buzz-relay/src/state.rs:1981-2320"
  - statement: "AppState carries conn_manager (Arc<ConnectionManager>), community_connections (Arc<CommunityConnectionRegistry>), and conn_semaphore (Arc<Semaphore>) as three of its fields, each constructed once in AppState's own initializer."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/state.rs:648"
      - "crates/buzz-relay/src/state.rs:650"
      - "crates/buzz-relay/src/state.rs:656"
      - "crates/buzz-relay/src/state.rs:870-874"
---

# Connection manager (buzz-relay)

`crates/buzz-relay/src/state.rs`'s `ConnectionManager` and
`CommunityConnectionRegistry`, plus the shared helper functions built around
them (`run_registered_community_connection`,
`revalidate_registered_communities`), are the relay's mechanism for
tracking every long-lived socket connected to a pod, routing messages to a
specific one, and closing connections in response to bans, community
deletion, graceful shutdown, and periodic durable-state revalidation. This
node answers: what data does the relay hold about a live connection, what
operations can be performed against it, who depends on those operations,
and how does a connection get closed when something other than the client
itself decides it should end?

No `platforms`-specific template exists in `launchpad/docs/corpus/templates/`
at the recorded revision. Per `AGENTS.md`'s documented no-template path,
this node is written directly against `node.schema.json`; its body borrows
`templates/component.md`'s section shape (Responsibility, Public interface,
Dependencies, Boundary, Relationships, Scope and omissions) as a
structurally close analog for documenting one standing component, without
adopting that template's `type: implementation` — this node's placement
under `platforms/` uses `type: platforms` instead, per the convention this
task follows across the sibling `platforms/**` batch.

## Responsibility

Two distinct registries exist, and they are not redundant:

- **`ConnectionManager`** — Nostr-WebSocket-specific. Its own doc comment:
  "Tracks active Nostr WebSocket connections and provides message routing by
  connection ID." It holds, per connection, the outbound data and control
  senders, an optional restart-close sender, a `CancellationToken`, the
  resolved community id, a shared backpressure counter, the connection's
  subscription map, an authenticated-pubkey slot, and its slow-client grace
  limit — everything a handler needs to route a Nostr protocol message to,
  or disconnect, one specific socket.
- **`CommunityConnectionRegistry`** — generic to any long-lived socket type.
  Its own doc comment: "Community-scoped lifecycle registry shared by every
  long-lived socket type." It holds only a connection id, its community,
  and a lightweight cancel/reason control handle — enough to answer "is
  this community still allowed to hold sockets" and "close everything bound
  to this community," independent of what protocol runs over the socket.
  Both the WebSocket handler and the audio/huddle handler register with
  this registry via the shared `run_registered_community_connection` helper;
  only the WebSocket handler additionally registers with `ConnectionManager`.

## Public interface

| Item | Kind | Contract | Evidence |
|---|---|---|---|
| `ConnectionManager::register` | fn | Insert a connection's senders, cancel token, community, backpressure counter, subscription map, and grace limit; self-signals an immediate restart-close if a drain is already in progress. | `crates/buzz-relay/src/state.rs:260-300` |
| `ConnectionManager::deregister` | fn | Remove a connection's entry. | `crates/buzz-relay/src/state.rs:303-305` |
| `ConnectionManager::set_authenticated_pubkey` | fn | Record the pubkey a connection authenticated as, after NIP-42 succeeds. | `crates/buzz-relay/src/state.rs:307-314` |
| `ConnectionManager::connection_ids_for_pubkey_in_community` / `pubkey_for_conn` / `pubkey_for` | fn | Look up live connection ids for a pubkey within one community, or the pubkey recorded for a connection id. | `crates/buzz-relay/src/state.rs:316-351`, `:566-571` |
| `ConnectionManager::community_for_conn` / `subscriptions_for` | fn | Return the community a connection is bound to, or a clone of its live subscription map handle. | `crates/buzz-relay/src/state.rs:517-529` |
| `ConnectionManager::disconnect_pubkey` | fn | Close every live connection for a pubkey within one community, delivering a best-effort reason frame first; fenced to the given community only. | `crates/buzz-relay/src/state.rs:353-395` |
| `ConnectionManager::drain_all` / `drain_all_jittered` | fn | Close every live connection with a 1012 Service Restart close, either all at once or spread across a jitter window with flush-acknowledgement tracking. | `crates/buzz-relay/src/state.rs:397-431`, `:433-507` |
| `ConnectionManager::per_community_ws_connections` / `per_community_users_online` | fn | Snapshot per-community live-connection and distinct-online-pubkey counts. | `crates/buzz-relay/src/state.rs:531-564` |
| `ConnectionManager::send_to` / `send_to_text_bytes` | fn | Fan-out send to one connection by id; increments/resets the connection's shared backpressure counter and cancels it past the configured grace limit. | `crates/buzz-relay/src/state.rs:573-619` |
| `CommunityConnectionRegistry::register` | fn | Register a socket (any type) under a community; returns a `CommunityConnectionGuard` that deregisters on drop. | `crates/buzz-relay/src/state.rs:137-149` |
| `CommunityConnectionRegistry::disconnect_community` | fn | Cancel every socket (any type) bound to a community, attributing the close to community deletion. | `crates/buzz-relay/src/state.rs:151-162` |
| `CommunityConnectionRegistry::bound_communities` | fn | Return the distinct communities with a live socket on this pod. | `crates/buzz-relay/src/state.rs:164-170` |
| `run_registered_community_connection` | fn | Shared entry point: register with the registry, durably revalidate the community, cancel-and-return if inactive, otherwise run the caller's connection body. | `crates/buzz-relay/src/state.rs:185-213` |
| `AppState::disconnect_pubkey_clusterwide` | fn | Sanctioned entry point for live ban enforcement: local `disconnect_pubkey` plus fire-and-forget cross-pod publish. | `crates/buzz-relay/src/state.rs:1149-1198` |
| `AppState::disconnect_community_clusterwide` | fn | Sanctioned entry point for community archival: local registry disconnect plus awaited cross-pod publish. | `crates/buzz-relay/src/state.rs:1200-1217` |
| `AppState::revalidate_live_communities` | fn | Periodic durable-state backstop: re-checks every community with live sockets directly against the database. | `crates/buzz-relay/src/state.rs:1219-1234` |

## Dependencies

**Depends on** (this component requires these to build/run):

| Component | Why | Evidence |
|---|---|---|
| `dashmap` | Backing concurrent map for both registries' connection tables. | `crates/buzz-relay/Cargo.toml:52` |
| `tokio` (`mpsc`, `watch`, `Semaphore`) | Per-connection data/control/restart channels, the community disconnect-reason watch channel, and the process-wide connection-count semaphore. | `crates/buzz-relay/Cargo.toml:32` |
| `tokio-util` (`CancellationToken`) | The per-connection and per-registration cancellation mechanism both registries and the send/heartbeat/recv tasks share. | `crates/buzz-relay/Cargo.toml:36` |
| `uuid` | Connection identity (`Uuid` keys in both registries' maps). | `crates/buzz-relay/Cargo.toml:50` |
| `buzz_core::CommunityId` / `buzz_db::Db` | Community identity carried on every entry, and the durable active-community check both `run_registered_community_connection` and `revalidate_live_communities` call. | `crates/buzz-relay/src/state.rs:1219-1234` |

**Depended on by** (these require this component):

| Component | Why | Evidence |
|---|---|---|
| `crates/buzz-relay/src/connection.rs` (WebSocket handler) | Registers/deregisters with `ConnectionManager` around the connection's lifetime; reads pubkey/subscription state during cleanup. | `crates/buzz-relay/src/connection.rs:219-229`, `:283-316` |
| `crates/buzz-relay/src/audio/handler.rs` (huddle/audio handler) | Registers with `CommunityConnectionRegistry` (not `ConnectionManager`) via `run_registered_community_connection`. | `crates/buzz-relay/src/audio/handler.rs:157` |
| `crates/buzz-relay/src/handlers/event.rs`, `handlers/side_effects.rs` | Look up connection membership, subscriptions, and pubkeys to route moderation and fan-out side effects. | `crates/buzz-relay/src/handlers/event.rs:129`, `crates/buzz-relay/src/handlers/side_effects.rs:117-158` |
| `crates/buzz-relay/src/main.rs` | Drives graceful-shutdown drain, the cross-pod connection-control consumer, the periodic community revalidator, and the connection-count metrics poller. | `crates/buzz-relay/src/main.rs:970-1005`, `:1208-1220`, `:1340-1361`, `:1549-1550` |

## Boundary

This node does not describe:
- The WebSocket connection's own connect → NIP-42-authenticate → terminate
  request/response sequence — that is
  `architecture-flows-websocket-connection`'s subject; this node covers the
  component the flow calls into, not the flow's own steps.
- NIP-01 message-level semantics (EVENT/REQ/COUNT dispatch, filter
  matching, subscription semantics) — owned by their own handler modules.
- How a ban is created or lifted, or how community archival is decided —
  only the connection-manager-side effect of those decisions
  (`disconnect_pubkey`, `disconnect_community`) is in scope here.
- The global `AppState` struct and its full field set beyond the three
  fields this node's claims depend on — sibling issue #1263 (app-state) is
  not merged into `origin/launchpad` at the time of writing, so its subject
  is out of scope rather than duplicated or linked.
- The audio/huddle protocol itself, or the git smart-HTTP transport — both
  are separate connection flows that either share (audio) or do not use
  (git) these registries; only the sharing point is described here.

## Relationships

- `references`: `architecture-flows-websocket-connection` — the WebSocket
  connection flow this component is called from; declared because that
  node exists on `origin/launchpad` at the recorded revision and this
  node's Boundary section explicitly defers the request/response sequence
  to it.

## Scope and omissions

**This node covers** the `ConnectionManager` and `CommunityConnectionRegistry`
data structures in `buzz-relay`: what per-connection state each holds, their
full public interface, how they differ and why both exist, which handler
modules and background tasks depend on them, the cross-pod fan-out
mechanism for live ban and community-deletion enforcement, the two
graceful-shutdown drain strategies, and the periodic durable-state
revalidation backstop.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The WebSocket connect/authenticate/terminate request-response sequence | `architecture-flows-websocket-connection` |
| NIP-01 message dispatch and filter semantics | The relevant handler modules; no corpus node yet |
| Ban/moderation decision rules themselves | Not yet a corpus node at the recorded revision |
| The global `AppState` struct | Sibling issue #1263 (app-state), unmerged at time of writing |
| A `platforms`-specific template's required sections, once one exists | Whichever future issue authors that template |

**Expected but not verified when this node was written:**

- Whether the audio/huddle handler's use of `CommunityConnectionRegistry`
  (rather than `ConnectionManager`) is documented anywhere as an
  intentional architectural boundary versus an artifact of audio sockets
  not needing Nostr-protocol routing — this node states the observed fact
  (which registry each handler calls) but did not find a design document
  confirming the *reason* for the split beyond what each registry's own
  doc comment already states.
- The exact values of `BUZZ_DRAIN_JITTER_MS`, `RESTART_CLOSE_ACK_TIMEOUT`,
  and each connection's `grace_limit` in production — these are
  operator-configurable (`crates/buzz-relay/src/config.rs`) and were not
  verified as fixed defaults worth citing as facts here.
