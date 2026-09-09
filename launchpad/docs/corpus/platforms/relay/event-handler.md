---
id: platforms-relay-event-handler
type: platforms
status: draft
origin: launchpad
audiences:
  - developer
  - agent
evidence:
  - statement: "This node was authored and checked against repository revision 131b02f989684117d9ab1dd426f1673fa638e523."
    entry_class: FACT
    evidence:
      - "commit 131b02f989684117d9ab1dd426f1673fa638e523"
  - statement: "`handle_event` in `crates/buzz-relay/src/handlers/event.rs` is the WebSocket relay's single entry point for a client-submitted NIP-01 EVENT frame; it is invoked from the connection message loop only after the incoming text frame has already been parsed into a `ClientMessage::Event(event)` and only while holding a permit from `state.handler_semaphore` (a bounded concurrency gate), spawned in its own tracing span so each EVENT is handled on an independent task."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs:608"
      - "crates/buzz-relay/src/connection.rs:568-595"
  - statement: "`handle_event` requires the connection to already be `AuthState::Authenticated`; an unauthenticated connection is rejected immediately with `OK false \"auth-required: not authenticated\"` and never reaches any further branch, including the ephemeral and agent-observer-frame paths."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs:634-654"
  - statement: "Before branching to any downstream handling, `handle_event` enforces that `event.pubkey` equals the authenticated connection's pubkey unless the event is a NIP-59 gift wrap (kind 1059), and separately rejects any event of kind `KIND_AUTH` outright with `invalid: AUTH events cannot be submitted via EVENT` -- both checks run once here, before the event is routed to the persistent, ephemeral, or agent-observer-frame branch below."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs:656-678"
  - statement: "`handle_event` routes every incoming, already-auth/pubkey/AUTH-checked event into exactly one of three branches based on kind, in this order: kind `KIND_AGENT_OBSERVER_FRAME` (24200) goes to `handle_agent_observer_event`; any kind for which `is_ephemeral` is true (the 20000-29999 NIP-16 range) goes to `handle_ephemeral_event`; every other kind is handed to the shared `super::ingest::ingest_event` pipeline documented separately."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs:680-761"
  - statement: "The two non-persistent branches (`handle_ephemeral_event`, `handle_agent_observer_event`) never call `ingest_event` and therefore never reach the community write-fence, signature/timestamp checks, scope allowlist, or storage/dispatch pipeline that `architecture-flows-event-ingestion` documents for persistent kinds -- confirmed by reading `handle_event`'s branch structure top to bottom: both branches `return` before the `ingest_event` call is ever reached."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs:680-761"
  - statement: "`architecture-flows-event-ingestion`'s own Scope and omissions section states that ephemeral-kind handling (`handle_ephemeral_event`) is out of scope for that document, calling it 'a distinct, unstored delivery-only flow'; it does not mention `handle_agent_observer_event` at all, since kind:24200 (agent observer frames) is itself an ephemeral-range-adjacent kind handled entirely inside `event.rs`, never routed through `ingest_event`."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/flows/event-ingestion.md:365-390"
  - statement: "For ephemeral kinds, `handle_event` enforces `MessagesWrite` scope (when the connection's scope list is non-empty) and re-checks the community's write fence (`buzz_deletion::store(&state.db).is_serving_active(...)`) before calling `handle_ephemeral_event` -- both checks are local to the WS handler and are not the same call sites as `ingest_event`'s own community-write-fence and scope checks, since ephemeral events never reach `ingest_event`."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs:694-732"
  - statement: "`handle_ephemeral_event` verifies the event's signature via `buzz_core::verification::verify_event`, dispatched through `tokio::task::spawn_blocking` (the same off-executor pattern the persistent ingest path uses for its own signature check), before doing any kind-specific work."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs:802-811"
  - statement: "`handle_ephemeral_event` gives kind `KIND_PRESENCE_UPDATE` (20001) special-cased content handling: it accepts either a bare status string or a legacy `{\"status\": ...}` JSON object, truncates an over-length bare string to at most 128 bytes at a UTF-8 char boundary, and calls `state.pubsub.clear_presence` when the resolved status is exactly `\"offline\"` or `state.pubsub.set_presence` otherwise, before falling through to the same channel-scoped or channel-less publish/fan-out path every other ephemeral kind uses."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs:813-847"
  - statement: "For a channel-scoped ephemeral event, `handle_ephemeral_event` resolves the channel id via `super::ingest::extract_channel_id` and enforces membership via `super::ingest::check_channel_membership` -- the same two functions `ingest_event_inner` calls for persistent events -- before marking the event as a local echo (`state.mark_local_event`), publishing it to Redis on the channel's topic, and fanning it out to local subscribers through `fan_out_event_to_local_subscribers`."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs:850-874"
      - "crates/buzz-relay/src/handlers/ingest.rs:550"
      - "crates/buzz-relay/src/handlers/ingest.rs:704"
      - "crates/buzz-relay/src/handlers/ingest.rs:742"
  - statement: "A channel-less ephemeral event (for example NIP-AB pairing kind:24134) is published to Redis under a nil-UUID sentinel routing key via `EventTopic::Global`, which the receiving node's subscriber loop recognizes via `is_nil()` and converts back to `None` so the global subscriber index is used; the nil UUID is only ever a Redis routing key and is never written to the database, since ephemeral events are never stored."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs:875-903"
  - statement: "`handle_agent_observer_event` handles kind:24200 (`KIND_AGENT_OBSERVER_FRAME`) frames: it verifies the event's signature via `spawn_blocking(verify_event)`, then rejects any frame whose `created_at` differs from server time by more than 300 seconds (a tighter freshness window than the persistent-ingest path's 900-second timestamp bound) with 'invalid: observer frame timestamp outside +/-5 minute freshness window'."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs:959-991"
  - statement: "`agent_observer_route` requires the frame's content to look NIP-44-encrypted (`content_looks_like_nip44`), requires exactly one each of a `p` tag (recipient), an `OBSERVER_AGENT_TAG` tag (the agent's pubkey), and an `OBSERVER_FRAME_TAG` tag (the frame-type marker), and classifies the frame as agent-to-owner telemetry (event signed by the agent, recipient != agent, frame value must equal `OBSERVER_FRAME_TELEMETRY`) or owner-to-agent control (recipient == agent, event signed by someone other than the agent, frame value must equal `OBSERVER_FRAME_CONTROL`); any other combination of signer/recipient/agent is rejected as invalid, and a recognized-shape frame whose frame-tag value does not match its direction's expected constant is silently dropped (`Ok(None)`, acknowledged to the sender as accepted) rather than rejected with an error."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs:1103-1141"
  - statement: "Authorization for an agent observer frame is `is_agent_owner(community, agent, owner)`: `handle_agent_observer_event` first takes a fast path if the sending connection authenticated via NIP-OA with `ctx.agent_owner_pubkey` already matching the frame's resolved owner, otherwise checks a per-community `(agent, owner)` cache (`state.observer_owner_cache`) and falls back to a database lookup (`state.db.is_agent_owner`) that populates the cache on success; a database error is rejected as `error: internal server error` rather than defaulting to allow or deny, and a non-owner is rejected with 'restricted: observer frame is not authorized for this agent owner'."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs:1007-1061"
  - statement: "Agent observer telemetry frames (agent-to-owner direction) are rate-limited to 100 per second per `(community_id, agent_key)` pair via an in-process sliding-window-by-second counter (`observer_frame_rate_limited`); control frames (owner-to-agent) deliberately bypass this limiter so a rare owner action cannot be starved by bursty agent telemetry."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs:921-945"
      - "crates/buzz-relay/src/handlers/event.rs:1063-1076"
  - statement: "A successfully authorized, rate-limit-passing agent observer frame is marked as a local echo, published to Redis under the channel-less `EventTopic::Global` topic (agent observer frames are never channel-scoped), fanned out to local subscribers via `fan_out_event_to_local_subscribers`, and only then acknowledged to the sender with `OK true \"\"` -- unlike the ephemeral-event branch, which sends its `OK` from the calling `handle_event` frame after `handle_ephemeral_event` returns, `handle_agent_observer_event` sends its own `OK` frame internally at every exit path."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs:1078-1101"
  - statement: "For the persistent-kind branch, `handle_event` constructs an `IngestAuth::Nip42` value from the connection's already-authenticated pubkey, scopes, and channel ids and calls `super::ingest::ingest_event`; on return it converts the `Result<IngestResult, IngestError>` into exactly one `RelayMessage::ok(event_id, accepted, message)` WebSocket frame, sanitizing `IngestError::Internal` to the fixed string 'error: internal server error' so no database/system detail reaches the client over this transport -- the same sanitization rule `architecture-flows-event-ingestion` documents for the shared pipeline, applied here at the WS-specific translation seam rather than restated."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs:754-791"
  - statement: "`RelayMessage::ok` formats the NIP-01 `[\"OK\", <event_id>, <accepted>, <message>]` JSON array that every one of `handle_event`'s three branches ultimately sends back over the WebSocket connection, regardless of which branch handled the event."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/protocol.rs:203-206"
  - statement: "`filter_fanout_by_access`, `fan_out_event_to_local_subscribers`, `fan_out_pubsub_event`, and `dispatch_persistent_event`/`dispatch_persistent_event_inner` -- the fan-out and post-commit dispatch mechanics used by both the persistent-ingest path and the ephemeral/agent-observer paths in this file -- are already documented by `architecture-flows-event-ingestion` (its Ordered interactions steps 15-16 and its Authentication/authorization/trust-boundary-crossings section); this node cites their call sites from the ephemeral/observer branches without restating their internal filtering logic."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs:115-278"
      - "launchpad/docs/corpus/architecture/flows/event-ingestion.md:272-314"
  - statement: "Representative test coverage of this file's dispatch/routing behavior lives in its own `#[cfg(test)] mod tests`: `channel_scoped_content_kinds_require_h_tags` and `non_channel_kinds_do_not_require_h_tags` cover the shared `requires_h_channel_scope` classification, `agent_observer_route_accepts_agent_to_owner_telemetry`/`agent_observer_route_accepts_owner_to_agent_control`/`agent_observer_route_rejects_plaintext_content` cover `agent_observer_route`'s classification and NIP-44 gate, `observer_frame_rate_limiter_is_scoped_by_community` and `observer_owner_cache_is_scoped_to_community` cover the per-community isolation of the rate limiter and owner cache, and `fanout_event_frame_matches_legacy_format_byte_for_byte`/`fanout_frame_cache_reuses_frames_within_one_cycle_only` cover the EVENT frame serialization helpers; separately, `crates/buzz-test-client/tests/e2e_relay.rs::test_ephemeral_event_not_stored` exercises the ephemeral branch end to end over a live relay connection."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs:1166-1450"
      - "crates/buzz-test-client/tests/e2e_relay.rs:803"
  - statement: "This node does not itemize every kind-specific structural validator or the full workflow-triggering/audit mechanics of `dispatch_persistent_event_inner`; that content stays owned by `architecture-flows-event-ingestion`, and this node's Boundary section names the split explicitly rather than silently overlapping it."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/architecture/flows/event-ingestion.md:357-390"
    confidence: 0.85
relationships:
  - type: references
    target: architecture-flows-event-ingestion
---

# Relay EVENT handler

`handle_event` in `crates/buzz-relay/src/handlers/event.rs` is the WebSocket
relay's dispatcher for a client-submitted NIP-01 `EVENT` frame: the code that
decides, for one already-parsed, already-authenticated event, which of three
handling paths it takes, and that ultimately answers the client with exactly
one NIP-01 `OK` frame. This node answers: what does the handler itself check
before routing, what are its three branches, and what do the two branches that
never touch persistent storage (ephemeral events, agent observer frames)
actually do end to end?

## Responsibility

`handle_event` is invoked once per incoming `EVENT` message, after the WS
message loop (`connection.rs`) has already parsed the frame into a
`ClientMessage::Event(event)` and acquired a `handler_semaphore` permit
(crates/buzz-relay/src/connection.rs:568-595). Its own responsibilities, run
in this order for every event regardless of kind, are:

1. Require the connection to be `AuthState::Authenticated`; otherwise reject
   with `auth-required:` and stop (crates/buzz-relay/src/handlers/event.rs:634-654).
2. Enforce `event.pubkey == authenticated pubkey`, with a NIP-59 gift-wrap
   exception, and reject client-submitted `KIND_AUTH` events outright
   (crates/buzz-relay/src/handlers/event.rs:656-678).
3. Route the event to exactly one of three branches by kind: agent observer
   frames (kind 24200), ephemeral kinds (20000-29999), or everything else,
   which is handed to the shared `ingest_event` pipeline
   (crates/buzz-relay/src/handlers/event.rs:680-761).
4. Translate whatever the chosen branch produces into one NIP-01 `OK` frame
   sent back on the connection.

## The three branches

### Agent observer frames (kind 24200)

Requires `MessagesWrite` scope if the connection has any scopes at all, then
delegates to `handle_agent_observer_event`
(crates/buzz-relay/src/handlers/event.rs:680-692). That function:

- Verifies the signature off-executor via `spawn_blocking(verify_event)`.
- Rejects frames whose timestamp drifts more than 300 seconds (+/-5 minutes)
  from server time -- tighter than persistent ingest's 900-second bound
  (crates/buzz-relay/src/handlers/event.rs:959-991).
- Parses and classifies the frame via `agent_observer_route`: content must
  look NIP-44-encrypted; exactly one `p` tag, one agent tag, one frame-type
  tag; the signer/recipient/agent combination determines telemetry
  (agent to owner) versus control (owner to agent) direction; a
  recognized-shape frame whose frame-tag value doesn't match its direction is
  silently dropped rather than rejected (crates/buzz-relay/src/handlers/event.rs:1103-1141).
- Authorizes via `is_agent_owner`, checked in order: a NIP-OA session fast
  path, then a per-community `(agent, owner)` cache, then a DB lookup that
  populates the cache; a DB error fails as an internal error, never as an
  implicit allow (crates/buzz-relay/src/handlers/event.rs:1007-1061).
- Rate-limits telemetry frames only, 100/second per `(community, agent)`;
  control frames bypass the limiter
  (crates/buzz-relay/src/handlers/event.rs:921-945, 1063-1076).
- On success: marks the event as a local echo, publishes to Redis under the
  channel-less `EventTopic::Global`, fans out to local subscribers, and sends
  its own `OK true ""` -- this branch answers the client itself, unlike the
  ephemeral branch below (crates/buzz-relay/src/handlers/event.rs:1078-1101).

### Ephemeral kinds (20000-29999)

Requires `MessagesWrite` scope if the connection has any scopes, then re-checks
the community's write fence (`buzz_deletion::store(&state.db).is_serving_active`)
before calling `handle_ephemeral_event`
(crates/buzz-relay/src/handlers/event.rs:694-732). That function:

- Verifies the signature off-executor, the same pattern as the observer path.
- Special-cases `KIND_PRESENCE_UPDATE` (20001): accepts a bare status string
  or legacy `{"status": ...}` JSON, truncates an over-length bare string to
  128 bytes at a char boundary, and calls `clear_presence`/`set_presence`
  before falling through to the shared publish/fan-out path below
  (crates/buzz-relay/src/handlers/event.rs:813-847).
- For a channel-scoped event: resolves the channel via
  `super::ingest::extract_channel_id` and enforces membership via
  `super::ingest::check_channel_membership` -- the same two functions the
  persistent-ingest pipeline calls -- then marks the local echo, publishes to
  Redis on the channel's topic, and fans out locally
  (crates/buzz-relay/src/handlers/event.rs:850-874).
- For a channel-less event (e.g. NIP-AB pairing kind:24134): publishes under a
  nil-UUID sentinel routing key via `EventTopic::Global`, recognized by
  `is_nil()` on the receiving node and converted back to `None`; the nil UUID
  is a Redis routing key only and is never written to the database
  (crates/buzz-relay/src/handlers/event.rs:875-903).
- Returns `Result<(), String>` to `handle_event`, which sends the `OK` frame
  itself from the caller side -- unlike the observer branch.

### Everything else: handoff to `ingest_event`

Every kind that is neither an agent observer frame nor ephemeral is handed to
`super::ingest::ingest_event` via a constructed `IngestAuth::Nip42`
(crates/buzz-relay/src/handlers/event.rs:754-761). `handle_event`'s only job
here is: build the transport-specific auth value, call the shared pipeline,
and translate the `Result<IngestResult, IngestError>` it gets back into one
`OK` frame -- sanitizing `IngestError::Internal` to a fixed
`"error: internal server error"` string so no backend detail reaches the
client. Everything the pipeline itself does (community write fence, signature/
timestamp checks, the per-kind scope allowlist, storage, post-commit
dispatch) is `architecture-flows-event-ingestion`'s subject, not this node's --
see *Boundary* below.

## The NIP-01 `OK` response contract

`RelayMessage::ok(event_id, accepted, message)`
(crates/buzz-relay/src/protocol.rs:203-206) formats the
`["OK", <event_id>, <accepted>, <message>]` array every branch above sends.
Two of the three branches send it from inside `handle_event` itself (the
persistent handoff, and the ephemeral branch via its `Result` return); the
agent-observer branch sends it itself at each exit path inside
`handle_agent_observer_event`. Regardless of which branch produced it, this is
the one acknowledgement frame a client sees for any submitted event.

## Dependencies

**Depends on** (this handler requires these to run):

| Component | Why | Evidence |
|---|---|---|
| `crates/buzz-relay/src/connection.rs` | Parses the incoming WS frame into `ClientMessage::Event` and spawns `handle_event` under a semaphore permit | crates/buzz-relay/src/connection.rs:568-595 |
| `crates/buzz-relay/src/handlers/ingest.rs` | Owns the shared `ingest_event` pipeline for persistent kinds, and the `extract_channel_id`/`requires_h_channel_scope`/`check_channel_membership` helpers this file's ephemeral branch reuses | crates/buzz-relay/src/handlers/ingest.rs:550,704,742 |
| `crates/buzz-relay/src/protocol.rs` | `RelayMessage::ok` -- the NIP-01 OK frame format | crates/buzz-relay/src/protocol.rs:203-206 |
| `crates/buzz-core/src/verification.rs` | `verify_event` -- signature/id verification, called by both non-persistent branches | crates/buzz-relay/src/handlers/event.rs:805,960 |
| `crates/buzz-core/src/observer.rs` | NIP-44-content heuristic and observer tag name constants used by `agent_observer_route` | crates/buzz-relay/src/handlers/event.rs:13-16 |

**Depended on by** (these require this handler):

| Component | Why | Evidence |
|---|---|---|
| `crates/buzz-relay/src/connection.rs` | The WS message loop's only call site for handling a client `EVENT` frame | crates/buzz-relay/src/connection.rs:590 |

## Boundary

This node does not describe:

- The `ingest_event`/`ingest_event_inner` persistent pipeline itself -- the
  community write fence, signature/timestamp bounds, per-kind scope
  allowlist, the ~30 structural validators, storage, and post-commit dispatch
  are `architecture-flows-event-ingestion`'s subject. This node only
  describes how `handle_event` hands off to that pipeline and translates its
  result into an `OK` frame.
- The internal filtering logic of `filter_fanout_by_access`,
  `fan_out_event_to_local_subscribers`, `fan_out_pubsub_event`, or
  `dispatch_persistent_event_inner` -- already documented by
  `architecture-flows-event-ingestion`'s Ordered interactions and
  Authentication/authorization sections. This node cites their call sites
  from the ephemeral and agent-observer branches without restating them.
- The REQ/subscription read path, `filter.rs`'s NIP-29 scoping, or how a
  subscriber comes to match an event in the first place -- a separate flow
  this file does not implement.
- HTTP transport handling (`POST /events`) -- `handle_event` is the
  WebSocket-only entry point; the HTTP bridge (`buzz-relay/src/api/bridge.rs`)
  constructs its own `IngestAuth::Http` and calls `ingest_event` directly,
  never through this file.

## Relationships

- references: `architecture-flows-event-ingestion` -- this node scopes
  itself to the WS-dispatch mechanics and the two non-persistent branches
  (`handle_ephemeral_event`, `handle_agent_observer_event`) that document
  explicitly names as out of its own scope, rather than restating the
  persistent pipeline that document already covers.

## Scope and omissions

**This node covers** `handle_event`'s own pre-routing checks
(auth-required, pubkey/gift-wrap match, AUTH-kind rejection), its three-way
routing by kind, the full mechanics of the two branches that never reach
`ingest_event` (`handle_ephemeral_event`, `handle_agent_observer_event`,
including the presence-update special case, channel resolution/membership
reuse, the nil-UUID channel-less sentinel, agent-observer NIP-44/tag
classification, owner authorization, and per-agent rate limiting), and the
NIP-01 `OK` response contract every branch converges on.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The persistent `ingest_event`/`ingest_event_inner` pipeline | `architecture-flows-event-ingestion` |
| Fan-out/post-commit dispatch internals (`filter_fanout_by_access`, `dispatch_persistent_event_inner`) | `architecture-flows-event-ingestion` |
| The REQ/subscription read path and NIP-29 filter scoping | Not yet documented in this corpus |
| HTTP `POST /events` transport handling | `crates/buzz-relay/src/api/bridge.rs`, not yet documented in this corpus |

**Expected but not verified when this node was written:**

- Whether every one of the in-file `#[cfg(test)] mod tests` cases (beyond the
  ones named in evidence above) is relevant to this node's claims was not
  individually re-verified line by line; the ones cited were read directly.
- Whether a `platforms.md` template will later formalize the section shape
  used here (borrowed from `templates/component.md` per the batch's settled
  convention) was not something this node could confirm, since no
  `platforms`-specific template exists in the corpus yet.
