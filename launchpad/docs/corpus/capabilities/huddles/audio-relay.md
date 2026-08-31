---
id: capabilities-huddles-audio-relay
type: capabilities
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - operator
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5, which is also the tip of origin/launchpad at authoring time."
    entry_class: FACT
    evidence:
      - "commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
  - statement: "VISION.md's 'Huddles' section states real-time voice runs over a WebSocket Opus relay built into buzz-relay, that Buzz authenticates participants (NIP-42), admits them to a room, and forwards Opus frames between peers with no external SFU, and that agents join the same audio relay as humans, bringing their own STT/TTS."
    entry_class: FACT
    evidence:
      - "VISION.md"
  - statement: "VISION.md's own product-capability Status table marks a row '✅ Huddles — WebSocket Opus voice relay + lifecycle events (recording/tracks planned)', its status marker for shipped capabilities."
    entry_class: FACT
    evidence:
      - "VISION.md:230"
  - statement: "ARCHITECTURE.md's 'Huddle Audio — WebSocket Opus Relay' section states real-time voice lives inside buzz-relay (src/audio/), not a separate crate, and that a WebSocket endpoint (wss://.../huddle/{channel_id}/audio) authenticates each participant with a NIP-42 challenge, checks channel membership, admits them to an in-memory room, and forwards opaque Opus frames between peers, with no external SFU."
    entry_class: FACT
    evidence:
      - "ARCHITECTURE.md"
  - statement: "The audio module's own top-level doc comment describes it as a 'WebSocket Opus audio relay' where clients authenticate via NIP-42, join an audio room, and binary Opus frames are fanned out to other room members with a 1-byte peer_index prefix identifying the speaker."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/audio/mod.rs"
  - statement: "crates/buzz-relay/src/router.rs registers GET /huddle/{channel_id}/audio, handled by ws_audio_handler, as the WebSocket route this capability is reached through."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs"
  - statement: "The relay defines two variants of the per-frame wire protocol negotiated at join: version 1 forwards each binary frame as opaque Opus bytes with no relay-parsed header, while version >= 2 requires a fixed 8-byte header (u16 seq, u32 ts_48k, i8 level_dbov clamped to -127..=0, u8 flags with bit 0 = DTX) before the opaque Opus payload; a room pins to whichever version its first successfully-admitted peer requested, and every later peer in that room must match it or is rejected with an upgrade_required-mapped VersionMismatch."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/audio/wire.rs"
      - "crates/buzz-relay/src/audio/room.rs"
  - statement: "level_dbov is explicitly documented as client-authored, untrusted telemetry: FrameHeader::parse clamps an out-of-range value to the -127 silence floor but never drops the audio frame for bad VU metadata, and the module's own threat-model comment states admission, moderation, and kick decisions MUST NOT consume level_dbov."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/audio/wire.rs"
  - statement: "A single audio room enforces a soft cap of 25 peers (MAX_PEERS_PER_ROOM) and a hard cap of 255 peers (the u8 peer_index space); each peer's audio channel has capacity for 8 frames (160ms at 20ms/frame) and drops the newest frame on a full buffer rather than queuing, while the separate control channel (32 slots) is sized so that joined/left messages are not expected to drop, logging a warning if one does."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/audio/room.rs"
  - statement: "When buzz-relay has no mesh configured (state.mesh() is None), a join is rejected with {\"code\":\"huddle_audio_unavailable\"} if the operator-controlled config.huddle_audio_available flag (BUZZ_HUDDLE_AUDIO_AVAILABLE, defaulting to true) is false — a deliberate guardrail against silently admitting peers into a single-pod room that a peer on a different horizontally-scaled pod could never reach."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/audio/handler.rs"
      - "crates/buzz-relay/src/config.rs"
  - statement: "crates/buzz-relay/src/audio/mesh.rs's module doc describes an owner-authoritative cross-pod variant of this capability: one pod owns a huddle (the holder of a Redis fenced-CAS lease keyed to the session/channel id) and hosts the single Room; non-owner pods register their local clients as remote peers over a HuddleControl stream, forward those clients' frames to the owner as mesh datagrams, and deliver the owner's fan-out back verbatim, with every datagram fenced by a monotonic GenerationFloor that rejects frames from a superseded ownership generation."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/audio/mesh.rs"
  - statement: "crates/buzz-core/src/kind.rs defines the huddle lifecycle event kinds this capability emits: KIND_HUDDLE_STARTED = 48100, KIND_HUDDLE_PARTICIPANT_JOINED = 48101, KIND_HUDDLE_PARTICIPANT_LEFT = 48102, KIND_HUDDLE_ENDED = 48103, and KIND_HUDDLE_GUIDELINES = 48106, all in the 48000-48999 system/admin custom range."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "VISION.md's Huddles section and ARCHITECTURE.md's Huddle Audio section both state that voice, room lifecycle, and lifecycle events are wired/shipped, while recording and per-track publishing are planned/not yet built at the recorded revision."
    entry_class: FACT
    evidence:
      - "VISION.md"
      - "ARCHITECTURE.md:570"
  - statement: "The already-merged flow node architecture-flows-huddle-audio documents this capability's full client-facing join/relay/leave sequence step by step — trigger and preconditions, the ordered auth and admission checks, the cross-pod mesh handshake, live audio relay behavior, leave/auto-end handling, an authentication/authorization/trust-boundary table, and a failure/abort/rollback taxonomy — at the same recorded revision."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/flows/huddle-audio.md"
  - statement: "The already-merged container node architecture-containers-relay documents buzz-relay as the deployable unit hosting this capability (among the relay's other responsibilities), including its technology, inbound/outbound interfaces, and deployment/health/security posture, without describing this capability's own step-by-step behavior."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/containers/relay.md"
  - statement: "architecture-flows-huddle-audio's own 'Representative verification' section states that room admission and lifecycle invariants are covered by unit tests in crates/buzz-relay/src/audio/room.rs, mesh generation fencing by unit tests in crates/buzz-relay/src/audio/mesh.rs, and connection-level behavior by unit tests in crates/buzz-relay/src/audio/handler.rs's tests module, and records as a gap that no end-to-end test in crates/buzz-test-client/tests/e2e_relay.rs opens the /huddle/{channel_id}/audio route and drives it through a real socket."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/flows/huddle-audio.md"
      - "crates/buzz-relay/src/audio/room.rs"
      - "crates/buzz-relay/src/audio/mesh.rs"
      - "crates/buzz-relay/src/audio/handler.rs"
  - statement: "At the recorded revision, a case-sensitive scan of every corpus node's id field under launchpad/docs/corpus (excluding schema/ and templates/) contains no node whose type is interfaces-events for the /huddle/{channel_id}/audio WebSocket route, so this capability node declares no references edge to an interface node — none exists yet to point at."
    entry_class: FACT
    evidence:
      - "grep_id_field(path='launchpad/docs/corpus/**/*.md', exclude='schema/**;templates/**', pattern='^id:') -> 61 ids returned, none of type interfaces-events, run at commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
  - statement: "Issue #754's definition of done requires this capability node to state the capability and primary actors/outcomes; define behavioral rules, constraints and relevant variants; link major flows, interfaces, data and platform implementation; and link verification demonstrating the capability, in addition to the corpus-wide schema-validity, evidence, and single-canonical-document requirements shared with every corpus task."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#754 definition of done"
relationships:
  - type: references
    target: architecture-flows-huddle-audio
  - type: references
    target: architecture-containers-relay
---

# Huddle audio relay: capability

Any Buzz community member — a human or an AI agent, as peers — can start or join a
live, real-time voice conversation ("huddle") in a channel and hear and be heard by
every other participant, with no external voice infrastructure (no third-party SFU,
no separate media server) required. An agent participant brings its own
speech-to-text/text-to-speech rather than the platform providing either.

## Primary actors and outcomes

- **Human and agent participants**, admitted as peers through the same WebSocket
  route and the same NIP-42 authentication and channel-membership checks — the
  capability does not distinguish a human caller from an agent caller at the
  protocol level.
- **Outcome for a participant:** join a channel's huddle, speak and be heard live by
  every other current participant (subject to the constraints below), and see the
  huddle's lifecycle (start, others joining/leaving, end) reflected as ordinary
  Nostr events in the same channel.
- **Outcome for the channel/community:** a huddle's lifecycle is durable and
  auditable — start, each join, each leave, and end are each a signed, persisted
  Nostr event (kinds 48100-48103) — even though the live audio itself is not
  persisted.

## Maturity

**Shipped.** VISION.md's own Status table marks Huddles "✅ ... WebSocket Opus voice
relay + lifecycle events (recording/tracks planned)", and both VISION.md's Huddles
section and ARCHITECTURE.md's Huddle Audio section describe voice, room lifecycle,
and lifecycle events as wired at the current revision. The implementation is real:
`crates/buzz-relay/src/audio/` (handler, room, join, mesh, wire) backs every claim in
this node.

**Not shipped: recording and per-track publishing.** Both VISION.md and
ARCHITECTURE.md name this as planned, not built, at the recorded revision — this
capability today is live-only; nothing captures or re-publishes a huddle's audio
after the fact.

## Behavioral rules, constraints, and variants

- **No external SFU.** The relay itself forwards opaque Opus frames between peers
  in-process; it never decodes, mixes, or re-encodes audio, and no third-party media
  server is involved.
- **Two wire-protocol variants, pinned per room.** Version 1 forwards each binary
  frame as opaque bytes with no relay-parsed header. Version 2 and above additionally
  require a fixed 8-byte header (sequence, a 48 kHz timestamp, a client-reported
  audio level, and a flags byte whose bit 0 signals a DTX/comfort-noise frame) ahead
  of the opaque Opus payload. A room pins to whichever version its first admitted
  peer requested; every later peer must match that pin or is rejected.
- **Client-reported audio level is untrusted telemetry, by explicit design.** An
  out-of-range level is clamped to a silence floor, never used to drop the audio
  frame itself, and is documented as unfit for any admission, moderation, or kick
  decision — only for diagnostics/UI hints.
- **Real-time delivery favors drops over queuing or blocking.** A room admits at
  most 255 peers (soft-capped at 25 by default), and every per-peer audio delivery
  is non-blocking: a slow or full peer's link drops that one frame rather than
  stalling the sender or any other peer. The control channel (join/leave/roster
  messages) is kept separate and sized so it is not expected to drop, unlike audio.
- **Single-pod and cross-pod (mesh) are two operating variants of the same
  capability.** With no mesh configured, all participants in a huddle must land on
  the same relay pod; an operator can explicitly disable this single-pod behavior
  under horizontal scaling (`huddle_audio_available = false`), which then rejects
  joins outright rather than silently admitting peers who could never hear a
  peer on another pod. With Buzz Mesh enabled, one pod owns each huddle
  (a Redis fenced-CAS lease) and other pods forward their local participants'
  frames to the owner over the mesh, so participants can be spread across pods
  without changing the client-facing wire format.
- **Lifecycle is Nostr-native.** Huddle started/participant-joined/participant-left/
  huddle-ended are each their own event kind (48100-48103), persisted and fanned out
  like any other Buzz event, distinct from the live audio path itself.

## Boundary

This node does not describe:
- **How the capability is built** — the room/peer/admission internals, the mesh
  fan-out and fencing mechanics, and the relay's technology choices belong to the
  `architecture-containers-relay` container node and to source under
  `crates/buzz-relay/src/audio/` directly; this node names them only as evidence for
  the capability's existence and constraints, not as its own subject matter.
- **The step-by-step flow through this capability** — the exact ordered sequence of
  auth, membership, admission, live relay, and teardown, including every rejection
  code and the failure/rollback behavior at each step, is `architecture-flows-huddle-
  audio`'s subject, not repeated here.
- **The interface contract this capability is exposed through** — no
  `interfaces-events` corpus node yet documents the `/huddle/{channel_id}/audio`
  WebSocket route as its own interface; today the closest documented boundary
  contract is `architecture-flows-huddle-audio`'s own authentication/authorization/
  trust-boundary table. This node declares no `references` edge to an interface node
  because none exists to point at yet.
- **How the running capability is operated** — deployment topology, horizontal
  scaling posture, and the mesh's own operational behavior belong to the
  `architecture-deployment-*` nodes and to Buzz Mesh's own (not yet authored)
  corpus coverage, not to this capability description.
- **Huddle creation and the surrounding text channel** — starting a huddle
  (emitting `kind:48100`) and huddle-channel guidelines (`kind:48106`) are named here
  only as lifecycle events this capability emits; neither has its own corpus node yet.
- **Recording and per-track publishing** — named above under *Maturity* as planned,
  not built; there is nothing implemented yet for this node to describe.

## Implementation, verification, and neighboring references

- **Implementation:** `crates/buzz-relay/src/audio/` — `handler.rs` (WebSocket
  lifecycle), `room.rs` (peer registry, admission, fan-out), `join.rs` (cross-pod
  ownership resolution), `mesh.rs` (mesh datagram routing and fencing), `wire.rs`
  (v2 frame header parsing); registered at `GET /huddle/{channel_id}/audio` in
  `crates/buzz-relay/src/router.rs`. Event kinds in
  `crates/buzz-core/src/kind.rs`.
- **Flow:** `architecture-flows-huddle-audio` — the full join/relay/leave sequence.
- **Platform/container:** `architecture-containers-relay` — the deployable unit
  this capability runs inside.
- **Verification:** unit tests in `crates/buzz-relay/src/audio/room.rs` (admission,
  version pinning, roster/community isolation), `crates/buzz-relay/src/audio/mesh.rs`
  (generation fencing), and `crates/buzz-relay/src/audio/handler.rs` and
  `crates/buzz-relay/src/audio/wire.rs` (connection- and frame-parsing behavior).
  **Gap, inherited from `architecture-flows-huddle-audio`:** no end-to-end test in
  `crates/buzz-test-client/tests/e2e_relay.rs` opens the huddle audio WebSocket
  route and drives a real auth-to-audio-to-leave session over an actual socket, so
  this capability's coverage is unit-level only.

## Relationships

- `references`: `architecture-flows-huddle-audio` — the step-by-step flow this
  capability's join/relay/leave behavior follows.
- `references`: `architecture-containers-relay` — the deployable container this
  capability runs inside.

## Scope and omissions

**This node covers** the huddle audio relay capability at product level: what a
human or agent participant can do because it exists, its primary actors and
outcomes, its shipped/planned maturity, the behavioral rules and deployment
variants (protocol version pinning, untrusted telemetry, drop-over-block delivery,
single-pod vs. mesh operation) that a caller of this capability needs to know, and
where its implementation, step-by-step flow, and verification are documented.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The step-by-step join/relay/leave sequence, failure codes, and rollback behavior | `architecture-flows-huddle-audio` |
| How the capability is built (room/peer/mesh internals, technology choices) | `architecture-containers-relay`, `crates/buzz-relay/src/audio/` |
| The interface contract for the WebSocket route | Not yet a corpus node (see *Boundary*) |
| Deployment/operational posture (horizontal scaling, mesh operations) | `architecture-deployment-*` nodes; Buzz Mesh's own corpus coverage, not yet authored |
| Huddle creation and huddle-channel guidelines | Not yet a corpus node |
| Recording and per-track publishing | Not implemented at the recorded revision (see *Maturity*) |

**Expected but not verified when this node was written:**

- **No end-to-end test was found for this capability's WebSocket route** — see
  *Implementation, verification, and neighboring references*. This node's
  behavioral claims rest on unit tests and direct source reading, inherited from
  the same gap `architecture-flows-huddle-audio` already recorded.
- **`crates/buzz-relay-mesh`'s own implementation was not read beyond `mesh.rs` and
  `join.rs`'s call sites** — the mesh transport, `iroh` wiring, and the Redis
  fenced-CAS lease implementation itself were not independently verified for this
  node; they are cited here only as `architecture-flows-huddle-audio` and
  `mesh.rs`'s own module documentation describe them.
- **Desktop/mobile client-side huddle UX (join UI, reconnection, STT/TTS
  integration for agents) was not inspected** — this node describes the relay-side
  capability only.
