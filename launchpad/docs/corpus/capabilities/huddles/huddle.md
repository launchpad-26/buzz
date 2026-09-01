---
id: capabilities-huddles-huddle
type: capabilities
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - operator
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5."
    entry_class: FACT
    evidence:
      - "commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
  - statement: "Issue #757's definition of done requires this capability node to state the capability and its primary actors/outcomes; define behavioral rules, constraints and relevant variants; link major flows, interfaces, data and platform implementation; and link verification demonstrating the capability."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#757 definition of done"
  - statement: "VISION.md's own 'Huddles' section states that real-time voice runs over a WebSocket Opus relay built into buzz-relay, that Buzz authenticates participants via NIP-42 and admits them to a room before forwarding Opus frames between peers with no external SFU, that agents join the same audio relay as humans and bring their own STT/TTS, and that huddle lifecycle flows as Nostr events (started, joined, left, ended)."
    entry_class: FACT
    evidence:
      - "VISION.md"
  - statement: "VISION.md's own product-capability Status table marks Huddles shipped -- 'WebSocket Opus voice relay + lifecycle events' -- with recording and per-track publishing marked planned rather than shipped."
    entry_class: FACT
    evidence:
      - "VISION.md"
  - statement: "buzz-core's kind registry defines the huddle lifecycle kinds KIND_HUDDLE_STARTED=48100, KIND_HUDDLE_PARTICIPANT_JOINED=48101, KIND_HUDDLE_PARTICIPANT_LEFT=48102 and KIND_HUDDLE_ENDED=48103, the KIND_HUDDLE_GUIDELINES=48106 channel-guidelines kind, and the ephemeral KIND_HUDDLE_REACTION=24810 (a channel-scoped emoji-reaction burst that is never stored in the timeline)."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "buzz-relay's requires_h_channel_scope requires an `h` (NIP-29 channel) tag on all five huddle lifecycle/guidelines kinds, and required_scope_for_kind grants all five the same ordinary Scope::ChannelsWrite as everyday channel content rather than an elevated admin scope -- a huddle's lifecycle events are channel-scoped and channel-write-permissioned like any other channel message."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "The desktop Tauri huddle module's own doc comment states its lifecycle model: parent channel -> start_huddle creates an ephemeral channel plus an audio WebSocket relay session; other clients -> join_huddle joins that same relay; any client -> leave_huddle emits a lifecycle event and clears local state; the creator -> end_huddle archives the ephemeral channel and clears state."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/huddle/mod.rs"
  - statement: "start_huddle creates its backing channel as a private, stream-type channel with ttl_seconds=3600 (one hour) via a kind:9007 NIP-29 create-group event, posts voice-mode guidelines (kind:48106) before adding any member so an agent auto-subscribing on its kind:9000 membership notification cannot miss them, adds each invited member (kind:9000), and only then emits KIND_HUDDLE_STARTED (kind:48100) to the parent channel; a failure at any step -- including channel creation itself -- archives the orphaned ephemeral channel on a best-effort basis and resets local state to Idle."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/huddle/mod.rs"
  - statement: "start_huddle rejects a request inviting more than MAX_HUDDLE_AGENTS=20 member pubkeys at the Tauri command boundary, before any channel is created or relay call is made."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/huddle/relay_api.rs"
      - "desktop/src-tauri/src/huddle/mod.rs"
  - statement: "end_huddle is restricted to the huddle's creator, with an explicit force parameter documented as a recovery override for when the creator has disconnected ungracefully; a non-creator instead calls leave_huddle, which only auto-ends the huddle if they were the last human participant."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/huddle/mod.rs"
  - statement: "buzz-db's channel model backs ephemeral channels with nullable ttl_seconds/ttl_deadline columns (None meaning permanent), and buzz-core's ChannelType enum has exactly three variants -- stream, forum, dm -- with no dedicated huddle variant; a huddle's backing channel is an ordinary private stream channel distinguished only by its TTL and its kind:48100 linkage to a parent channel, not by a separate channel type."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/channel.rs"
      - "crates/buzz-core/src/channel.rs"
  - statement: "Desktop's getDmHuddleMemberPubkeys computes which agent pubkeys to offer as huddle invitees only when the parent channel's channelType is 'dm', confirming a huddle can be started from a direct-message channel and not only from a stream or forum channel."
    entry_class: FACT
    evidence:
      - "desktop/src/features/channels/lib/dmHuddleMembers.ts"
  - statement: "The merged corpus node architecture-flows-huddle-audio documents, in step-by-step depth this node does not restate, the WebSocket join/relay/leave protocol for an already-created huddle audio session: the NIP-42 challenge/response handshake, relay- and channel-membership enforcement, Buzz Mesh cross-pod ownership resolution, Opus frame relay and its failure/backpressure behavior, and room auto-end on last-peer departure."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/flows/huddle-audio.md"
  - statement: "Desktop test suites exercise huddle-capability behavior distinct from the relay-side audio-protocol tests architecture-flows-huddle-audio already cites: huddleAvailability.test.mjs (whether starting/joining a huddle is offered for a given channel), huddleCardState.test.mjs (the huddle-started message card's rendered state), huddleChannelVisibility.test.mjs (the ephemeral channel's sidebar visibility), and huddleError.test.mjs (mapping start/join failure strings to user-facing messages)."
    entry_class: FACT
    evidence:
      - "desktop/src/features/channels/lib/huddleAvailability.test.mjs"
      - "desktop/src/features/huddle/lib/huddleCardState.test.mjs"
      - "desktop/src/app/huddleChannelVisibility.test.mjs"
      - "desktop/src/features/huddle/lib/huddleError.test.mjs"
relationships:
  - type: references
    target: architecture-flows-huddle-audio
  - type: references
    target: architecture-containers-desktop
  - type: references
    target: architecture-containers-relay
  - type: references
    target: architecture-context-ai-agent
  - type: references
    target: architecture-context-human-user
  - type: implements
    target: corpus-template-capability
---

# Huddle: capability

A **huddle** is Buzz's ad-hoc, channel-scoped real-time voice call. Any member of a
stream, forum, or DM channel can start one from that channel; Buzz creates a private,
one-hour-TTL ephemeral channel to back the call, admits participants over a WebSocket
Opus audio relay built into `buzz-relay`, and narrates the whole session — started,
joined, left, ended — as ordinary channel-scoped Nostr events. A human and an AI agent
are peers in a huddle: agents join the same audio relay as human participants and bring
their own speech-to-text/text-to-speech, rather than being routed through a separate
integration surface.

## Maturity

**Shipped.** VISION.md's own product-capability Status table marks Huddles `✅` —
"WebSocket Opus voice relay + lifecycle events" — with recording and per-track
publishing named separately as planned, not shipped. The lifecycle event kinds
(`48100`–`48103`), the ephemeral guidelines kind (`48106`), the desktop `start_huddle` /
`join_huddle` / `leave_huddle` / `end_huddle` Tauri commands, and the relay's
`/huddle/{channel_id}/audio` WebSocket route are all present in the repository at the
recorded revision, not merely designed.

## Behavioral rules, constraints, and variants

- **Backing channel.** Starting a huddle creates a private, `stream`-type,
  `ttl_seconds=3600` channel (a `kind:9007` NIP-29 create-group event) rather than a
  dedicated huddle channel type — `ChannelType` has only `stream`, `forum`, and `dm`.
  The huddle's identity as a huddle (rather than an ordinary ephemeral stream channel)
  comes from the `kind:48100` HUDDLE_STARTED event linking it to its parent channel, not
  from any column on the channel row itself.
- **Ordering on start.** The ephemeral channel is created first; voice-mode guidelines
  (`kind:48106`) are posted *before* any member is added, because an agent auto-subscribes
  on its own `kind:9000` membership notification and could otherwise complete its initial
  sync before the guidelines exist; `KIND_HUDDLE_STARTED` (`kind:48100`) to the parent
  channel is emitted last, only once the preceding steps succeed. A failure at any step,
  including channel creation itself, archives the orphaned ephemeral channel on a
  best-effort basis rather than leaving a half-created huddle behind.
- **Participant cap.** A huddle invite is capped at `MAX_HUDDLE_AGENTS=20` member
  pubkeys, rejected at the Tauri command boundary before any channel or relay call is
  made. (The underlying audio room's own 255-slot peer-index limit, and its
  version-pinning and admission rules once a peer actually joins, belong to
  `architecture-flows-huddle-audio`, not this node.)
- **Who can end it.** Only the huddle's creator can end it for everyone
  (`end_huddle`), archiving the ephemeral channel and emitting `kind:48103`
  HUDDLE_ENDED; an explicit `force` override exists as a documented recovery path for a
  creator who disconnected ungracefully. Any other participant instead calls
  `leave_huddle`, which only auto-ends the huddle if they were the last human present.
- **Channel-scoped like ordinary content.** All five huddle lifecycle/guidelines kinds
  require an `h` (NIP-29 channel) tag and are gated at the same `Scope::ChannelsWrite`
  as everyday channel messages — starting, joining, or ending a huddle needs no
  elevated or huddle-specific permission beyond ordinary channel-write access.
- **Variant: DM huddles.** A huddle can be started from a direct-message channel as
  well as a stream or forum channel; desktop's `getDmHuddleMemberPubkeys` computes
  agent invitees specifically for the `channelType === "dm"` case.
- **Variant: human-agent parity.** VISION.md states agents join the same audio relay
  as humans and bring their own STT/TTS, rather than huddles offering a separate
  agent-only or human-only mode.

## Verification

- Desktop unit/component tests exercise capability-level behavior distinct from the
  relay-side audio-protocol tests `architecture-flows-huddle-audio` already cites:
  `huddleAvailability.test.mjs` (whether a huddle can be offered for a given channel),
  `huddleCardState.test.mjs` (the huddle-started message card's rendered state),
  `huddleChannelVisibility.test.mjs` (the ephemeral channel's sidebar visibility), and
  `huddleError.test.mjs` (mapping start/join failure strings to user-facing messages).
- The WebSocket join/relay/leave protocol for an already-created huddle session,
  including its own representative unit-test coverage and its one documented
  end-to-end test gap, is verified in depth by `architecture-flows-huddle-audio` and is
  not re-verified here.

## Boundary

This node does not describe:
- **How the audio session itself is joined, relayed, or torn down** — the WebSocket
  upgrade, NIP-42 challenge/response, Buzz Mesh cross-pod ownership, Opus frame relay,
  and room auto-end are `architecture-flows-huddle-audio`'s territory, referenced here
  rather than restated.
- **How the desktop client or the relay are built** — containers, components, and
  technology choices belong to `architecture-containers-desktop` and
  `architecture-containers-relay`, referenced here rather than restated.
- **The boundary contract a huddle is exposed through** — no interface-type corpus
  node yet documents the `/huddle/{channel_id}/audio` WebSocket route or the desktop
  Tauri command surface (`start_huddle`/`join_huddle`/`leave_huddle`/`end_huddle`) as an
  interface in its own right; see *Scope and omissions* below.
- **How the running system is operated** — deployment, scaling, and incident response
  for huddle audio (e.g. Buzz Mesh capacity, `huddle_audio_available` configuration)
  are an operations concern, not this capability's own description of what it does for
  users.

## Relationships

- `references`: `architecture-flows-huddle-audio` — the step-by-step audio join/relay/
  leave flow this capability is exposed through once a huddle exists.
- `references`: `architecture-containers-desktop`, `architecture-containers-relay` —
  the client and server containers that implement this capability.
- `references`: `architecture-context-ai-agent`, `architecture-context-human-user` —
  the two participant types this capability treats as peers.
- `implements`: `corpus-template-capability` — this node's own shape (capability
  statement, maturity, boundary, relationships, scope and omissions) follows that
  template.

## Scope and omissions

**This node covers** what a huddle fundamentally is — a channel-scoped, ad-hoc,
ephemeral-channel-backed real-time voice call — its primary actors (human and agent
participants, and the huddle creator specifically), its lifecycle-level behavioral
rules and constraints (backing-channel shape, step ordering and rollback on start,
participant cap, creator-only end with a force override, channel-scoping and
permission model), its DM and human/agent-parity variants, its shipped/planned
maturity split, and pointers to the flow, container, and context nodes that own the
depth this node deliberately does not restate.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The WebSocket audio join/relay/leave protocol, Buzz Mesh cross-pod ownership, and room admission/fencing | `architecture-flows-huddle-audio` |
| How the desktop client and relay containers are built | `architecture-containers-desktop`, `architecture-containers-relay` |
| The interface boundary the huddle capability is exposed through (the audio WebSocket route; the desktop Tauri command surface) | Not yet a corpus node |
| Huddle *creation* as its own event-flow (the exact ordered `kind:9007`/`kind:48106`/`kind:9000`/`kind:48100` sequence and its rollback path), and huddle-channel text/guidelines conventions (`kind:48106`) | Not yet a corpus node; described here only at the level this capability node needs |
| Recording and per-track publishing | Marked "planned" in `VISION.md`; not implemented at the recorded revision |
| Buzz Mesh's own internals (compute pooling, transport) beyond what huddle audio observes | Not yet a corpus node; see `VISION_MESH.md` |
| Agent-side STT/TTS pipeline internals (desktop `huddle::{stt,tts,pipeline}` modules) | Not yet a corpus node |

**Expected but not verified when this node was written:**

- **No dedicated interface-type corpus node exists for the huddle audio WebSocket
  route or the desktop Tauri huddle command surface**, so this node's *Boundary*
  section names that gap rather than pointing to a node that does not yet exist.
- **The exact Postgres schema backing `channel_type`'s `stream`/`forum`/`dm` enum**
  (the `channel_type`/`channel_visibility` SQL enum types themselves) was read only
  through `buzz-db`'s Rust bindings, not through the migration file that defines them.
- **`HuddlePhase`'s full state machine** (the desktop-side `Idle`/`Creating`/
  `Connected`/`Active`/`Leaving` phases and their transition rules) was read only far
  enough to confirm the creator/non-creator end-vs-leave asymmetry cited above; a
  future huddle-lifecycle node would need to verify the phase machine in full rather
  than relying on this node's partial read.
