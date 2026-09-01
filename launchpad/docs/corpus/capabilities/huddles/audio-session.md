---
id: capabilities-huddles-audio-session
type: capabilities
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5 on the launchpad branch."
    entry_class: FACT
    evidence:
      - "commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
  - statement: "buzz-relay registers GET /huddle/{channel_id}/audio, handled by audio::handler::ws_audio_handler, as a plain WebSocket upgrade route."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs:133-136"
  - statement: "crates/buzz-relay/src/audio/mod.rs documents the capability's own model in its module doc comment: clients connect, authenticate via NIP-42, and join an audio room; binary frames (Opus) are fanned out to all other room members with a 1-byte peer_index prefix."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/audio/mod.rs"
  - statement: "One audio session is represented in code as a Room, keyed by community_id and the huddle channel's UUID, holding its connected participants in a peers: DashMap<Uuid, AudioPeer>, an admission guard (index allocator plus an ended flag under one lock), and a roster_tx broadcast channel for ordered roster mutations."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/audio/room.rs:161-173"
  - statement: "One participant in a session is represented as an AudioPeer, carrying the participant's Nostr pubkey, a stable 0-254 peer_index assigned at join and prefixed onto relayed frames, an audio_tx channel for outbound Opus frames (drops on full, since this is real-time), and a separate ctrl_tx channel for joined/left/close control messages so control is never starved by audio backpressure."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/audio/room.rs:19-29"
  - statement: "KIND_HUDDLE_STARTED=48100, KIND_HUDDLE_PARTICIPANT_JOINED=48101, KIND_HUDDLE_PARTICIPANT_LEFT=48102 and KIND_HUDDLE_ENDED=48103 are the Nostr event kinds that carry a huddle audio session's lifecycle (start, a participant joining, a participant leaving, the session ending) as ordinary signed events, alongside KIND_HUDDLE_GUIDELINES=48106 and the reaction kind KIND_HUDDLE_REACTION=24810."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs:472"
      - "crates/buzz-core/src/kind.rs:590"
      - "crates/buzz-core/src/kind.rs:592"
      - "crates/buzz-core/src/kind.rs:594"
      - "crates/buzz-core/src/kind.rs:596"
      - "crates/buzz-core/src/kind.rs:598"
  - statement: "VISION.md's Huddles section states that real-time voice runs over a WebSocket Opus relay built into buzz-relay, that Buzz authenticates participants via NIP-42 and admits them to a room and forwards Opus frames between peers with no external SFU, that agents join the same audio relay as humans and bring their own STT/TTS, and that huddle lifecycle flows as Nostr events (started, joined, left, ended)."
    entry_class: FACT
    evidence:
      - "VISION.md:104-111"
  - statement: "VISION.md's own feature checklist marks 'Huddles — WebSocket Opus voice relay + lifecycle events' with a shipped (✅) marker, with the parenthetical 'recording/tracks planned' naming the one part of the capability not yet built."
    entry_class: FACT
    evidence:
      - "VISION.md:230"
  - statement: "corpus node architecture-flows-huddle-audio documents the same capability's step-by-step join/relay/leave flow in detail (preconditions, ordered interactions, trust-boundary crossings, failure and rollback behavior) and is present in the corpus at this node's recorded revision, making it a valid references target."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/flows/huddle-audio.md"
  - statement: "corpus node architecture-containers-relay documents buzz-relay, the container that hosts this capability's audio session handling, and is present in the corpus at this node's recorded revision, making it a valid references target."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/containers/relay.md"
  - statement: "A session (room) admits at most MAX_PEERS_PER_ROOM = 25 participants as a defense-in-depth soft cap (the code comment reasons that N peers generate N x (N-1) frame copies per 20ms tick, and 25 peers = 600 copies/tick), separate from and stricter than the 255-slot peer-index space, which is the hard limit on distinct peer_index values a room can hand out."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/audio/room.rs:45-49"
      - "crates/buzz-relay/src/audio/room.rs:146-149"
  - statement: "The first peer successfully admitted to a room pins that room's huddle-audio protocol version; every later admission attempt in the same session must present the same version or is rejected with AdmissionError::VersionMismatch, and the three admission checks (room ended, peer-count cap, version pin) are deliberately ordered Ended > Full > VersionMismatch so that a client who could not have joined anyway (room ended or full) never learns the room's pinned protocol version."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/audio/room.rs:211-217"
      - "crates/buzz-relay/src/audio/room.rs:220-224"
      - "crates/buzz-relay/src/audio/room.rs:236-245"
  - statement: "Inbound binary WebSocket frames during a live session are treated as Opus audio and are capped at MAX_AUDIO_FRAME_BYTES = 4096 bytes; the handler enforces this cap when reading frames from a connected participant."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/audio/handler.rs:44"
      - "crates/buzz-relay/src/audio/handler.rs:977"
  - statement: "As of the recorded revision, no corpus node exists yet for a huddle-audio-facing interface (a CLI command group or HTTP route-group boundary contract distinct from the flow itself), and no corpus node exists yet for huddle creation/start or for the huddle text-channel/guidelines surface (kind:48106) — this capability node references only the two corpus nodes named above."
    entry_class: INFERENCE
    evidence:
      - "find(query='architecture/flows/huddle-audio.md;architecture/containers/relay.md', scope='launchpad/docs/corpus') -> 122 total .md files under launchpad/docs/corpus at the recorded revision, none under a capabilities/ or interfaces/ subtree naming huddles besides this new file"
    confidence: 0.8
  - statement: "The behavioral rules and constraints this capability enforces (session capacity caps, protocol-version pinning and its error-precedence ordering, and audio-frame size capping) are demonstrated by unit tests in crates/buzz-relay/src/audio/room.rs's own tests module, including admit_rejects_mismatched_version and admit_full_wins_over_version_mismatch; crates/buzz-relay/src/audio/handler.rs and crates/buzz-relay/src/audio/mesh.rs each carry their own tests modules as well, covering connection- and mesh-fencing-level behavior respectively."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/audio/room.rs:558"
      - "crates/buzz-relay/src/audio/room.rs:633"
      - "crates/buzz-relay/src/audio/room.rs:772"
      - "crates/buzz-relay/src/audio/handler.rs:1356"
      - "crates/buzz-relay/src/audio/mesh.rs:286"
---

# Huddle audio session: capability

Buzz lets a human or agent join a huddle's real-time voice channel and talk with
whoever else is in it. A caller opens a WebSocket to the huddle's audio route,
authenticates with their Nostr identity, and is admitted into a room where their
Opus audio frames are relayed to every other connected participant and every
join, leave, and end is recorded as an ordinary signed Nostr event other clients
(and other agents) can observe. Agents join the same relay as humans and bring
their own speech-to-text/text-to-speech — no separate agent-only voice path
exists.

## Maturity

**Shipped.** VISION.md's own feature checklist marks "Huddles — WebSocket Opus
voice relay + lifecycle events" with a shipped marker, and the code backs that:
`buzz-relay` registers a live `GET /huddle/{channel_id}/audio` WebSocket route
(`crates/buzz-relay/src/router.rs:133-136`), handled by
`audio::handler::ws_audio_handler`, and the four session-lifecycle event kinds
(`KIND_HUDDLE_STARTED`, `KIND_HUDDLE_PARTICIPANT_JOINED`,
`KIND_HUDDLE_PARTICIPANT_LEFT`, `KIND_HUDDLE_ENDED`) are defined and emitted at
the corresponding points in the join/leave flow (see
`architecture-flows-huddle-audio` for exactly where).

**Recording and per-track publishing are planned, not shipped.** VISION.md
names this as the one gap in an otherwise-wired capability.

## Behavioral rules and constraints

- **Session capacity is capped twice.** A soft cap of 25 participants per
  session is enforced as defense-in-depth (25 peers already means 600
  pairwise frame copies every 20ms tick), well inside the hard 255-slot
  peer-index space a session can ever hand out. Reaching either cap rejects
  the join; it does not degrade audio quality for those already in the
  session.
- **A session's audio protocol version is fixed by whoever joins first.**
  Every later participant in that same session must request the same
  version or is rejected — a session cannot silently mix two protocol
  versions among its participants. Admission checks are deliberately ordered
  so that a rejection for "session ended" or "session full" is always
  reported before a version mismatch would be, so a caller who could not
  have joined anyway never learns what protocol version the session is
  pinned to.
- **Audio is Opus only, frame-size capped.** A participant's audio is
  relayed as binary WebSocket frames, capped at 4096 bytes each; this is a
  per-frame limit, not a bandwidth or session-duration limit.
- **Humans and agents share one participant model.** There is no
  agent-specific join path or elevated capacity — an agent participates as
  an ordinary session participant and supplies its own speech-to-text/
  text-to-speech.

## Verification

The capacity caps, protocol-version pinning (and its deliberate error
precedence), and audio-frame-size capping named above are exercised by unit
tests colocated with the code: `crates/buzz-relay/src/audio/room.rs`'s own
`tests` module (for example `admit_rejects_mismatched_version`,
`admit_full_wins_over_version_mismatch`), plus separate `tests` modules in
`crates/buzz-relay/src/audio/handler.rs` (connection-level behavior) and
`crates/buzz-relay/src/audio/mesh.rs` (mesh generation fencing). For the
end-to-end join/relay/leave sequence this capability supports, and for the
one known coverage gap (no full-socket integration test), see
`architecture-flows-huddle-audio`'s own *Representative verification*
section — this node does not restate it.

## Boundary

This node does not describe:

- **How the capability is built** — the `Room`/`AudioPeer` data model, the
  cross-pod mesh ownership handshake, and the Axum/WebSocket server that hosts
  it. See `architecture-containers-relay` (the container) and, for the
  step-by-step mechanics, `architecture-flows-huddle-audio` (the flow).
- **The step-by-step flow through a session** — trigger, ordered
  preconditions, the join/relay/leave sequence, trust-boundary crossings, and
  failure/rollback behavior. That is entirely `architecture-flows-huddle-audio`'s
  territory, and this node deliberately does not restate it.
- **The interface(s) the capability is exposed through.** No corpus node for a
  huddle-audio interface exists yet; the sole client-facing boundary today is
  the single WebSocket route named above.
- **Huddle creation/start** (emitting `kind:48100` to begin a huddle) and the
  huddle text-channel/guidelines surface (`kind:48106`). Those are adjacent
  capabilities, not this one, and neither has a corpus node yet.
- **How the running system is operated** — deployment, scaling the relay's
  connection budget, or incident response for a stuck room. That is the
  `operations` corpus surface's territory, not this node's.
- **Desktop/mobile client-side huddle UI**, reconnection behavior, or the
  agent-side STT/TTS integration VISION.md mentions — none of these has a
  corpus node yet.

## Relationships

- references: architecture-flows-huddle-audio
- references: architecture-containers-relay

## Scope and omissions

**This node covers** what the huddle audio session capability is (real-time
voice within one huddle, admission via Nostr identity, Opus relay between
participants, lifecycle expressed as Nostr events), who its primary actors are
(human and agent participants, joining and leaving one session), its current
shipped/planned maturity, its behavioral rules and constraints (capacity
caps, protocol-version pinning, frame-size limits, the shared human/agent
participant model), and its boundary against the neighboring architecture,
flow, and interface documentation.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| How a session is built (data model, mesh ownership, container) | `architecture-containers-relay` |
| The step-by-step join/relay/leave flow, trust boundaries, failure behavior | `architecture-flows-huddle-audio` |
| The boundary contract this capability is exposed through | Not yet a corpus node |
| Huddle creation/start and the huddle guidelines channel (`kind:48106`) | Not yet a corpus node |
| Recording and per-track publishing | Marked "planned" in `VISION.md`; not implemented at the recorded revision |
| How the running system is operated | The `operations` corpus surface |
| Desktop/mobile client UI, reconnection behavior, agent STT/TTS integration | Not yet a corpus node |

**Expected but not verified when this node was written:**

- **No end-to-end test exercising a live huddle audio session was found or
  re-verified for this node**; `architecture-flows-huddle-audio`'s own ledger
  already records that `crates/buzz-test-client/tests/e2e_relay.rs` has no
  integration test opening the `/huddle/{channel_id}/audio` route, and this
  node relies on that finding rather than re-running the search independently.
- **Whether any corpus node for a huddle-audio interface or for huddle
  creation exists was checked only by directory listing at the recorded
  revision, not by a search across in-flight, unmerged sibling batch work**
  that may add one before this node merges.
