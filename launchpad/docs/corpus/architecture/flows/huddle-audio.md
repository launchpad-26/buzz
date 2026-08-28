---
id: architecture-flows-huddle-audio
type: architecture
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - operator
evidence:
  - statement: "This node was authored and checked against repository revision a44cf52fc740ebebbdd671427480d14f0bce0115."
    entry_class: FACT
    evidence:
      - "commit a44cf52fc740ebebbdd671427480d14f0bce0115"
  - statement: "Issue #680's definition of done requires this flow node to state trigger, preconditions and termination/outcome; list ordered interactions and data/state movement; identify authentication/authorization/trust-boundary crossings; and document failure/abort/rollback behavior with representative verification."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#680 definition of done"
  - statement: "The relay registers GET /huddle/{channel_id}/audio, handled by ws_audio_handler, as a plain WebSocket upgrade route alongside the mesh demo route."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs"
  - statement: "ws_audio_handler binds the connection to a community from the request Host header via bind_community before upgrading the socket; an unmapped host returns a generic 404 and the WebSocket is never opened, so an unauthenticated caller cannot probe which communities exist on the deployment."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/audio/handler.rs"
  - statement: "Before upgrading, ws_audio_handler acquires a permit from the shared connection semaphore (conn_semaphore); if the relay's global WebSocket connection budget is exhausted, the request is rejected with 503 before any socket is opened."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/audio/handler.rs"
  - statement: "After upgrade, handle_active_audio_connection sends a NIP-42 challenge string over the socket, then waits up to AUTH_TIMEOUT for a text frame of type 'auth' carrying a signed nostr Event; any other message, an oversized text frame, a timeout, or a closed socket during this window ends the connection with no further response."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/audio/handler.rs"
  - statement: "The auth event is verified by state.auth.verify_auth_event against the issued challenge and the tenant's expected relay URL (NIP-42); verification failure sends {\"type\":\"error\",\"message\":\"auth failed\"} and closes the connection without admitting a peer."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/audio/handler.rs"
  - statement: "Once authenticated, the caller's pubkey and any NIP-OA auth tag are checked against relay membership via enforce_relay_membership; denial sends {\"type\":\"error\",\"message\":\"restricted: not a relay member\"} and closes the connection."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/audio/handler.rs"
      - "crates/buzz-relay/src/api/mod.rs"
  - statement: "ensure_membership loads the target channel first and rejects an archived channel outright (so an auto-ended huddle cannot be rejoined); for a TTL-bearing (ephemeral) channel it resolves the lifecycle parent from a creator-signed kind:48100 huddle_started_link_exists check rather than trusting the client-supplied parent_channel_id, and requires that linkage to exist."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/audio/handler.rs"
  - statement: "Within ensure_membership, an already-a-member caller or an open-visibility channel is admitted immediately; otherwise, for a private ephemeral channel only, a caller who is a member of the resolved parent channel is auto-added as a member of the huddle channel and the membership cache is invalidated; every other caller is rejected with 'not a member'."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/audio/handler.rs"
  - statement: "KIND_HUDDLE_STARTED=48100, KIND_HUDDLE_PARTICIPANT_JOINED=48101, KIND_HUDDLE_PARTICIPANT_LEFT=48102, and KIND_HUDDLE_ENDED=48103 are the huddle lifecycle event kinds, in the 48000-48999 system/admin custom range."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "When buzz-relay is not configured with a mesh (state.mesh() is None) and config.huddle_audio_available is false, a join attempt is rejected with {\"code\":\"huddle_audio_unavailable\"} rather than being silently admitted into a room that a horizontally-scaled peer on another pod could never reach."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/audio/handler.rs"
  - statement: "When a mesh is configured, resolve_join_owner_ready determines whether this pod owns the huddle's Redis-arbitrated fenced-CAS lease (LocalOwner) or must forward the client to a remote owner pod (RemoteOwner); on the steady-state reuse arm it retries up to OWNER_READY_MAX_ATTEMPTS, sleeping OWNER_READY_RETRY_INTERVAL between attempts, before failing closed rather than ever admitting a local owner peer with no live lease-loss watcher."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/audio/join.rs"
  - statement: "On the remote (non-owner) path the local pod calls dial_remote_owner to register the client with the owner over the mesh transport; the owner may reject the registration as RoomFull, RoomEnded, a protocol VersionMismatch, or Fenced(FenceRejection), and a transport/protocol failure opening the control stream is reported as DialError::Mesh, surfaced to the client as {\"code\":\"huddle_owner_unreachable\"}."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/audio/join.rs"
      - "crates/buzz-relay/src/audio/handler.rs"
  - statement: "Local Room admission (Room::add_peer / add_peer_at_index) rejects with AdmissionError::Ended once the room has been marked ended, AdmissionError::Full once the 255-slot peer-index space is exhausted, and AdmissionError::VersionMismatch when the requested protocol version does not match the version already pinned by the room's first successfully-admitted peer; these map to the client-facing codes room_ended, room_full, and upgrade_required respectively."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/audio/room.rs"
      - "crates/buzz-relay/src/audio/handler.rs"
  - statement: "Before local admission, the client's requested protocol_version is rejected up front with {\"code\":\"unsupported_version\"} if it is 0 or greater than CURRENT_PROTOCOL_VERSION; a room pins its protocol version to whichever value its first peer requested, and Room::add_peer sets that pin only after a successful index allocation so a Full rejection never pins a version for a peer that did not actually join."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/audio/handler.rs"
      - "crates/buzz-relay/src/audio/room.rs"
  - statement: "On successful admission the server sends the client a 'joined' message carrying its assigned peer_index and the current peer roster, and (on the local/owner path only) broadcasts that message as a control frame to the room's existing peers; it then persists and fans out a kind:48101 PARTICIPANT_JOINED event via emit_participant_event."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/audio/handler.rs"
  - statement: "emit_participant_event signs the lifecycle event with the relay's own keypair, persists it to Postgres (skipping fan-out on a detected duplicate insert), marks it locally-published before broadcasting to avoid double-delivery on echo, fans it out to local WebSocket subscribers, and publishes it cross-node over Redis pub/sub; a DB persistence failure is logged but the event is still broadcast live so connected clients are not left stale, at the cost of late joiners reconstructing an inconsistent history until the next lifecycle event lands."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/audio/handler.rs"
  - statement: "Once admitted, inbound binary WebSocket frames are treated as Opus audio, capped at MAX_AUDIO_FRAME_BYTES (4 KB); an oversized frame is dropped with a warning rather than closing the connection, and for protocol version 2 or higher a frame that is too short for the 8-byte wire header or fails FrameHeader::parse is likewise dropped rather than forwarded, without disconnecting the sender."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/audio/handler.rs"
      - "crates/buzz-relay/src/audio/room.rs"
      - "crates/buzz-relay/src/audio/wire.rs"
  - statement: "On the owner/local path, Room::broadcast_frame prepends the sending peer's 1-byte peer_index to the frame and fans it to every other local room peer's audio channel via a non-blocking try_send, so a slow or full peer link drops that frame rather than blocking the sender or other peers; on the non-owner path the client's frame is instead forwarded to the huddle owner as a mesh datagram via RemoteHuddleSession::forward_media, and the owner's room fans it back out including to co-located peers."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/audio/room.rs"
      - "crates/buzz-relay/src/audio/handler.rs"
  - statement: "Each connection runs an outbound send loop with two channels — a data channel for audio and a control channel for Ping/Pong/Close/control JSON — and drains the control channel first on every iteration so heartbeat pings and control messages are never starved by audio backpressure."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/audio/handler.rs"
  - statement: "heartbeat_loop pings the client every HEARTBEAT_INTERVAL and increments a missed-pong counter on each tick; once the counter reaches MAX_MISSED_PONGS, or once a ping send fails, it cancels the connection's cancellation token and stops; an incoming Pong resets the counter to zero in recv_loop."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/audio/handler.rs"
  - statement: "A client-sent text control frame of {\"type\":\"leave\"} breaks recv_loop and drives normal disconnect cleanup; a received Close frame, a WebSocket read error, or a stream end (None) also breaks the loop; a text frame over MAX_TEXT_FRAME_BYTES is dropped with a warning rather than ending the connection."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/audio/handler.rs"
  - statement: "On the non-owner (remote) path, a reader task owns the owner's HuddleControl stream and races the owner's teardown signal (read_owner_control) against the connection's own cancellation: if the owner speaks first (Goodbye or stream close) the local client is torn down for rejoin and its local generation-fence state for that session is forgotten; if the connection cancels first (client left, heartbeat death, or local error) it sends a clean UnregisterPeer plus Goodbye(SessionEnded) so the owner drops the registration."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/audio/handler.rs"
      - "crates/buzz-relay/src/audio/join.rs"
  - statement: "HuddleTeardownCause enumerates OwnerLost (owner observed a newer generation and fenced itself out), OwnerDraining (owner is shutting down, e.g. on SIGTERM), SessionEnded (the owner's room emptied normally), and StreamClosed (the control stream closed or reset with no Goodbye, treated like owner loss); every cause is documented as recoverable by the client rejoining, which resolves a fresh owner and generation via Redis."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/audio/join.rs"
  - statement: "On the owner (local) path, a dedicated watcher task races the room's owner-lost and owner-draining signals against the connection's own cancellation; whichever fires first cancels the local connection (closing it for rejoin) and forgets the local generation floor for that session, and the watcher is silent on an ordinary client-initiated leave."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/audio/handler.rs"
  - statement: "GenerationFloor::check accepts a mesh audio datagram only if its generation is greater than or equal to the highest generation observed for that session, advancing the floor (and signalling a takeover) on a strictly higher generation and rejecting anything below it as stale; MeshAudioRouter enforces this fence before delivering any datagram to local room peers, so a superseded owner's frames cannot reach a client after a takeover."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/audio/mesh.rs"
  - statement: "On disconnect, cancellation propagates to the send, heartbeat, and forward tasks, and (where applicable) the mesh reader/owner-teardown-watcher tasks, all of which are joined (awaited) before cleanup proceeds, so the owner control stream's clean-close or teardown completes before the connection finishes tearing down."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/audio/handler.rs"
  - statement: "Room::remove_peer_and_check_ended removes the peer and recycles its index and roster-revision state under a single lock held across both the removal and the empty/ended check, so only the first of two simultaneously-disconnecting peers wins the auto-end race and a duplicate archive/48103 cannot occur; on the non-owner (remote) path the local pod calls the plain remove_peer instead and never auto-ends, because ingress mirrors never decide authoritative huddle lifetime — only the owner does."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/audio/room.rs"
      - "crates/buzz-relay/src/audio/handler.rs"
  - statement: "A departing peer always triggers a 'left' control broadcast (on the local path) and a kind:48102 PARTICIPANT_LEFT event via emit_participant_event, regardless of whether the room auto-ends."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/audio/handler.rs"
  - statement: "When the room is the last-leaver's to empty, handle_active_audio_connection archives the channel in Postgres; on success it additionally emits kind:48103 HUDDLE_ENDED; on archive failure it logs a warning and calls Room::clear_ended so the room is explicitly un-marked ended and the huddle stays alive rather than becoming a dead room no client can rejoin cleanly."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/audio/handler.rs"
  - statement: "When the room empties and this connection held the mesh owner lease, the lease is released fenced to the generation this connection observed as owner (mesh.owners.release(channel_id, generation)), so a release from a stale generation is a no-op and cannot undo a newer owner's acquisition if a re-acquire raced ahead of this cleanup."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/audio/handler.rs"
  - statement: "As of the recorded revision, crates/buzz-test-client/tests/e2e_relay.rs contains no end-to-end test that opens the /huddle/{channel_id}/audio WebSocket route; huddle audio has unit-test coverage inside crates/buzz-relay/src/audio/{room,join,mesh}.rs (e.g. admission, version pinning, fencing) but no integration test exercises the full auth-to-audio-to-leave flow over a real socket."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/e2e_relay.rs"
      - "crates/buzz-relay/src/audio/room.rs"
      - "crates/buzz-relay/src/audio/mesh.rs"
  - statement: "VISION.md describes huddles as real-time voice over a WebSocket Opus relay built into buzz-relay, authenticating participants via NIP-42, admitting them to a room, and forwarding Opus frames between peers with no external SFU; it marks voice, room lifecycle, and lifecycle events as wired, with recording and per-track publishing still planned."
    entry_class: FACT
    evidence:
      - "VISION.md"
---

# Flow: Huddle audio join, relay, and leave

How a client (human or agent) joins a Buzz huddle's real-time voice channel, how Opus
audio and lifecycle events move while the session is live, and how the session ends —
cleanly or by failure — including the cross-pod mesh case where the joining pod is not
the huddle's owner.

## Trigger, preconditions, and termination

**Trigger.** A client opens a WebSocket connection to
`GET /huddle/{channel_id}/audio` on a community's relay host and sends a signed
NIP-42 `auth` message in response to the server's challenge.

**Preconditions**, checked in order before a peer is admitted to the room:

1. The request's `Host` header resolves to a configured community (`bind_community`).
2. The relay has a free connection permit under its shared WebSocket budget.
3. The client completes NIP-42 challenge/response auth within `AUTH_TIMEOUT`.
4. The authenticated pubkey passes relay-membership enforcement
   (`enforce_relay_membership`).
5. The target channel is not archived, and — for an ephemeral (TTL-bearing) huddle
   channel — is linked to the claimed parent channel by a creator-signed `kind:48100`
   event (`ensure_membership`).
6. The caller is already a channel member, the channel is `open` visibility, or (for a
   private ephemeral channel only) the caller is a member of the resolved parent
   channel and is auto-added.
7. The requested protocol version is in `1..=CURRENT_PROTOCOL_VERSION` and, if the room
   already has peers, matches the version already pinned to that room.
8. If Buzz Mesh is configured, the joining pod resolves — directly, or by forwarding to
   a remote owner pod — a ready huddle owner for the session without hitting the
   ownerless-owner failure case (see *Cross-pod ownership*).

**Termination / outcome.** The flow ends in exactly one of:

- **Admitted.** The peer receives a `joined` message with its assigned `peer_index`
  and the current roster, a `kind:48101` PARTICIPANT_JOINED event is emitted, and the
  connection moves into the active audio-relay state until it leaves or is torn down.
- **Rejected before admission.** The socket is sent a JSON `error` message (see
  *Failure, abort, and rejection taxonomy*) and closed; no room state changes and no
  lifecycle event is emitted.
- **Left / torn down after admission.** The peer is removed from the room, a
  `kind:48102` PARTICIPANT_LEFT event is emitted, and — only if it was the last peer —
  the channel is archived and a `kind:48103` HUDDLE_ENDED event is emitted (see
  *Leaving and room auto-end*).

## Ordered interactions and data/state movement

### 1. Upgrade and tenant binding

`ws_audio_handler` resolves the target community from the request's `Host` header
**before** upgrading the socket (`bind_community`); an unmapped host gets a generic 404
with no upgrade, so an unauthenticated caller cannot use this route to enumerate
configured communities. It then acquires a permit from the relay's shared connection
semaphore, replying `503` if the global WebSocket budget is exhausted, and only then
completes the WebSocket upgrade into `handle_audio_connection`.

### 2. Challenge/response auth (NIP-42)

`handle_active_audio_connection` sends a `{"type":"challenge","challenge":...}`
text message, then waits up to `AUTH_TIMEOUT` for a text `auth` message carrying a
signed `nostr::Event`. Any other message, an oversized text frame, a timeout, or a
closed socket during this window ends the connection with no reply. The event is
verified against the issued challenge and the tenant's expected relay URL via
`state.auth.verify_auth_event`.

### 3. Authorization: relay membership, then channel membership

The authenticated pubkey (plus any NIP-OA auth tag on the event) is checked against
relay-level membership (`enforce_relay_membership`). Only then is channel-level
membership resolved by `ensure_membership`, which:

- loads the channel and rejects an archived one outright (closing the "rejoin an
  already-auto-ended huddle" race),
- for a TTL-bearing (ephemeral) channel, resolves the lifecycle parent from a
  creator-signed `kind:48100` linkage rather than trusting the client-supplied
  `parent_channel_id`,
- admits an existing member or an `open`-visibility channel immediately, and
- auto-adds the caller as a member of a private ephemeral channel only if they are
  already a member of its resolved parent channel — invalidating the membership cache
  on success.

Every other caller is rejected `not a member`.

### 4. Cross-pod ownership (Buzz Mesh)

If the relay has a mesh configured (`state.mesh()`), the join resolves through
`resolve_join_owner_ready` against the session directory (Redis fenced-CAS lease):

- **This pod owns the huddle (`LocalOwner`).** Either this connection won the CAS and
  installs the lease renewer, or an earlier connection already did and this one reuses
  it. The steady-state reuse case retries (bounded by `OWNER_READY_MAX_ATTEMPTS`,
  sleeping `OWNER_READY_RETRY_INTERVAL` between attempts) until the winning
  connection's renewer is visibly installed, rather than ever admitting a local owner
  peer with no live lease-loss watcher; exhausting the retries fails the join closed.
- **A remote pod owns the huddle (`RemoteOwner`).** This pod dials the owner over the
  mesh transport (`dial_remote_owner`) with a fenced registration header. The owner may
  reject the registration (`RegisterRejection::RoomFull`, `RoomEnded`,
  `VersionMismatch`, or `Fenced`), mapped to the same client-facing error codes a
  same-pod join would produce so the client cannot distinguish topology. A transport or
  protocol failure opening the control stream surfaces as `huddle_owner_unreachable`.

If no mesh is configured and `config.huddle_audio_available` is `false`, the join is
rejected `huddle_audio_unavailable` — a deliberate guardrail against silently admitting
peers on different pods into a room that cannot span them.

### 5. Local room admission

The (local or owner) room admits the peer via `Room::add_peer` /
`add_peer_at_index` (the latter when a remote registration already assigned the
`peer_index`). Admission enforces, in this order inside the room's lock: the room is
not `ended`, the 255-slot peer-index space is not exhausted, and the requested protocol
version matches whatever the room's first successfully-admitted peer pinned — pinning
happens only after a successful index allocation, so a `Full` rejection never pins a
version for a peer that did not actually join.

### 6. Admission side effects

On success: the room's roster revision advances and a roster delta is published; the
client receives a `joined` message with its `peer_index` and the current roster
snapshot; on the local/owner path this is also broadcast as a control frame to existing
peers; and `emit_participant_event` signs, persists (Postgres), locally marks, locally
fans out, and Redis-publishes a `kind:48101` PARTICIPANT_JOINED event. A DB persistence
failure is logged but the event still broadcasts live to connected clients — late
joiners reconstructing history from storage see an inconsistent view until the next
lifecycle event lands.

### 7. Live audio relay

Once admitted, inbound binary frames are Opus audio, capped at `MAX_AUDIO_FRAME_BYTES`
(4 KB); an oversized frame is dropped with a warning, not a disconnect. For protocol
version ≥ 2, a frame too short for the 8-byte wire header, or one that fails
`FrameHeader::parse`, is likewise dropped without disconnecting the sender — the header
is treated as sender-authored telemetry, never rewritten.

- **Owner/local fan-out.** `Room::broadcast_frame` prepends the sender's 1-byte
  `peer_index` and pushes the frame to every other local peer's audio channel via a
  non-blocking `try_send` — a full or slow peer link drops that one frame rather than
  blocking the sender or any other peer.
- **Non-owner forwarding.** The client's frame is instead forwarded to the huddle owner
  as a mesh datagram (`RemoteHuddleSession::forward_media`); the owner's room fans it
  back out, including to peers co-located with the original sender.
- **Mesh fencing.** `GenerationFloor::check` accepts an inbound mesh datagram only if
  its generation is `>=` the highest generation observed for that session (advancing
  the floor, and signalling a takeover, on a strictly higher one); `MeshAudioRouter`
  enforces this before delivering to any local peer, so a superseded owner's frames
  cannot reach a client after a takeover.
- **Outbound priority.** Each connection runs a data channel (audio) and a
  higher-priority control channel (ping/pong/close/control JSON), draining control
  first every iteration so heartbeats are never starved by audio backpressure.
- **Heartbeat.** `heartbeat_loop` pings every `HEARTBEAT_INTERVAL`; a `Pong` resets the
  missed-pong counter; reaching `MAX_MISSED_PONGS`, or a failed ping send, cancels the
  connection.

### 8. Leaving and room auto-end

A client-sent `{"type":"leave"}` text control message, a WS `Close` frame, a read
error, or a closed stream all break the receive loop and start teardown. Cancellation
propagates to the send, heartbeat, and forward tasks (and, where applicable, the mesh
reader and owner-teardown-watcher tasks below); all are joined before cleanup
continues, so a mesh control-stream clean-close or teardown always completes first.

- **Owner/local path.** `Room::remove_peer_and_check_ended` removes the peer and
  recycles its index and roster state under one lock held across both the removal and
  the empty/ended check — only the first of two simultaneously-disconnecting peers wins
  the auto-end race, preventing a duplicate archive or duplicate `kind:48103`.
- **Non-owner path.** The plain `remove_peer` is used and auto-end never fires locally
  — an ingress mirror never decides authoritative huddle lifetime, only the owner does.
- A `kind:48102` PARTICIPANT_LEFT event is always emitted, regardless of auto-end, and
  (on the local path) a `left` control message is broadcast to the remaining peers.
- **Auto-end.** If the room emptied on the owner, the channel is archived in Postgres.
  On success, `kind:48103` HUDDLE_ENDED is additionally emitted. On archive failure,
  the room is explicitly un-marked ended (`Room::clear_ended`) so it stays joinable
  rather than becoming a dead room stuck between "ended" and "archived".
- **Lease release.** If this connection held the mesh owner lease and the room emptied,
  the lease is released fenced to the generation this connection observed as owner —
  a release from a stale generation is a no-op, so it cannot undo a newer owner's
  acquisition that raced ahead of this cleanup.

## Authentication, authorization, and trust-boundary crossings

| Boundary | Mechanism | Failure behavior |
|---|---|---|
| Host → community (multi-tenant) | `bind_community` on the `Host` header, before WS upgrade | Generic 404, no upgrade — an unmapped host is indistinguishable from a nonexistent route |
| Client → relay identity | NIP-42 challenge/response, `verify_auth_event` | `{"type":"error","message":"auth failed"}`, connection closed |
| Client → relay membership | `enforce_relay_membership` (pubkey + optional NIP-OA auth tag) | `{"type":"error","message":"restricted: not a relay member"}`, connection closed |
| Client → channel membership | `ensure_membership` (archived check, ephemeral-parent linkage check, membership/auto-add) | `{"type":"error","message":"not a member"}`, connection closed |
| Ephemeral channel → claimed parent | Creator-signed `kind:48100` linkage (`huddle_started_link_exists`), not the client-supplied `parent_channel_id` | `Err("ephemeral channel is not linked to claimed parent")`, connection closed |
| Pod → huddle ownership (Buzz Mesh) | Redis fenced-CAS lease, `resolve_join_owner_ready` | Local: fails closed after bounded retries. Remote: owner-side `RegisterRejection`, or `DialError::Mesh` on transport failure |
| Mesh audio datagram → freshness | `GenerationFloor` monotonic fence, checked by `MeshAudioRouter` before local delivery | Datagram silently dropped (`FenceVerdict::RejectStale`); no error surfaced to peers |

No boundary in this flow is skippable by protocol version, deployment topology (mesh vs.
non-mesh), or channel visibility — every path above reaches the same enforcement
functions regardless of how the client arrived.

## Failure, abort, and rollback behavior

**Rejections before admission** (no room or DB state changes; a JSON `error` is sent
and the socket closes):

| Code / condition | Cause |
|---|---|
| `huddle_relay_draining` | Relay's huddle-owner registry is draining (shutdown) |
| `join_rejected` | Fenced-CAS resolution error acquiring/finding the owner |
| `huddle_audio_unavailable` | No mesh configured and single-pod huddle audio is disabled |
| *(channel archived)* | Channel archived-check failed post-room-lookup (closes the archive-race window) |
| *(pre-join channel check failed)* | DB error re-checking archive status — fails closed |
| `unsupported_version` | Requested protocol version is 0 or above `CURRENT_PROTOCOL_VERSION` |
| `huddle_owner_unreachable` | Mesh transport/protocol failure dialing the remote owner |
| *(mapped from `RegisterRejection`)* | Remote owner rejected registration (full / ended / version mismatch / fenced) |
| `room_full` | Local room's 255-slot peer-index space is exhausted |
| `room_ended` | Local room was already marked ended |
| `upgrade_required` | Requested protocol version does not match the room's pinned version |

**In-session failure handling is frame-drop, not disconnect**, for anything that is
recoverable per-message: oversized binary/text frames, malformed v2 audio headers, and
control-channel backpressure (`try_send`) all drop the offending frame or delivery and
keep the connection alive. This is a deliberate choice for realtime media: a slow peer
link should never stall every other peer's audio.

**In-session failure handling is teardown-for-rejoin** for anything that invalidates the
session's ownership state:

- **Owner lost or draining, or the mesh control stream closes/resets unexpectedly**
  (`HuddleTeardownCause::{OwnerLost,OwnerDraining,StreamClosed}`) — the non-owner reader
  task or the owner-side watcher task cancels the local connection, closing the socket
  so the client reconnects and re-resolves a fresh owner/generation via Redis. The local
  `GenerationFloor` entry for that session is forgotten so the rejoin's fresh generation
  is not itself fenced as stale by leftover local state; Redis remains the sole
  ownership arbiter throughout — forgetting the local floor never grants ownership.
- **Ordinary session end** (`HuddleTeardownCause::SessionEnded`, or an explicit client
  leave) — the same teardown path runs, but is treated as expected and does not log at
  warning level.

**Rollback on the archive step is explicit, not implicit.** If archiving the channel on
last-leaver auto-end fails, the room is *not* left in the `ended` state: `clear_ended()`
reverses the room-level end flag so the huddle remains rejoinable, and `kind:48103` is
not emitted — the emitted `kind:48102` (PARTICIPANT_LEFT) for the departing peer still
stands, since that peer genuinely left regardless of the archive outcome.

**Auto-end double-fire is prevented by lock scope, not by a flag check alone.**
`Room::remove_peer_and_check_ended` holds the room's lock across peer removal *and* the
empty/ended check, so two peers disconnecting at the same instant cannot both observe
"empty and not yet ended" and both trigger archive + `kind:48103`.

### Representative verification

- Room admission and lifecycle invariants (version pinning, `Full`/`Ended`/
  `VersionMismatch`, roster revisions, per-community isolation) are covered by unit
  tests in `crates/buzz-relay/src/audio/room.rs` (`admit_rejects_mismatched_version`,
  `admit_after_mark_ended_returns_ended`, `admit_full_wins_over_version_mismatch`,
  `manager_isolates_same_channel_uuid_across_communities`, and others in that file's
  `tests` module).
- Mesh generation fencing (`GenerationFloor`, `MeshAudioRouter`) is covered by unit
  tests in `crates/buzz-relay/src/audio/mesh.rs` (`fence_accepts_first_and_equal_and_higher`,
  `fence_rejects_stale_after_advance`, `fence_is_per_session`, `fence_forget_resets_floor`,
  `router_drops_stale_datagram_without_delivering`).
- Connection-level behavior (shared connection-permit budget, oversized-message
  rejection at the WebSocket parser boundary, policy-close on community deletion) is
  covered by unit tests in `crates/buzz-relay/src/audio/handler.rs`'s `tests` module.
- **Gap:** no end-to-end test in `crates/buzz-test-client/tests/e2e_relay.rs` opens the
  `/huddle/{channel_id}/audio` route and drives it through a real auth → join → audio →
  leave sequence over an actual socket; coverage is unit-level only for this flow as a
  whole.

## Scope and omissions

**This document covers** the client-facing WebSocket join/relay/leave flow for one
huddle audio session on `buzz-relay`, including the cross-pod ownership handshake and
mesh audio fencing insofar as they change this flow's observable behavior (join
outcome, teardown cause, frame delivery).

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The internals of Buzz Mesh (`buzz-relay-mesh`) beyond what this flow observes — transport, `iroh` wiring, the fenced-CAS lease implementation itself | Not yet a corpus node; see `crates/buzz-relay-mesh/` and `VISION_MESH.md` |
| Huddle *creation* (starting a huddle, emitting `kind:48100`) and huddle text-channel guidelines (`kind:48106`) | Not yet a corpus node |
| Recording and per-track publishing | Marked "planned" in `VISION.md`; not implemented at the recorded revision |
| Desktop/mobile client-side huddle UI and reconnection behavior | Not yet a corpus node |
| Agent-side STT/TTS integration for huddle participation | Not yet a corpus node; mentioned only as a capability in `VISION.md` |

**Expected but not verified when this node was written:**

- **No end-to-end huddle audio test was found.** Behavior described in *Ordered
  interactions* and *Failure, abort, and rollback behavior* is verified against unit
  tests and direct source reading, not against a running relay driving a real WebSocket
  session end-to-end. See the verification gap noted above.
- **The `buzz-relay-mesh` crate's own contract (`InboundHandler`, `RelayPeerTransport`,
  `MeshDatagram`, `HuddleControl` stream framing) was read only as far as this flow's
  call sites required** (`crates/buzz-relay/src/audio/mesh.rs`, `join.rs`); its full
  implementation in `crates/buzz-relay-mesh/` was not inspected end-to-end.
- **Desktop and mobile client behavior on receiving each error code or teardown cause**
  (retry policy, backoff, UI presentation) was not inspected — this node documents only
  the relay's side of the contract.
