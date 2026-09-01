---
id: capabilities-huddles-opus
type: capabilities
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - operator
evidence:
  - statement: "This node was authored and checked against repository revision 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5."
    entry_class: FACT
    evidence:
      - "commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
  - statement: "Issue #758's definition of done requires this node to state the capability and primary actors/outcomes; define behavioral rules, constraints and relevant variants; link major flows, interfaces, data and platform implementation; and link verification demonstrating the capability."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#758 definition of done"
  - statement: "VISION.md states real-time voice runs over a WebSocket Opus relay built into buzz-relay, forwarding Opus frames between peers with no external SFU, and marks Huddles as shipped (✅) with recording/per-track publishing still planned."
    entry_class: FACT
    evidence:
      - "VISION.md:106"
      - "VISION.md:230"
  - statement: "buzz-relay never decodes huddle audio: crates/buzz-relay/src/audio/room.rs states frames are opaque Opus bytes, and crates/buzz-relay/src/audio/mod.rs's module doc describes the relay as a WebSocket Opus audio relay that fans binary frames out to other room members without inspecting their contents."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/audio/room.rs"
      - "crates/buzz-relay/src/audio/mod.rs"
  - statement: "The relay bounds an inbound binary audio frame at MAX_AUDIO_FRAME_BYTES (4 KB), a limit its own comment describes as generous for a single Opus packet; an oversized frame is dropped with a warning rather than closing the connection."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/audio/handler.rs"
  - statement: "The desktop client is the only codec implementation in this repository: desktop/src-tauri/Cargo.toml pins the `opus` crate at version \"0.3\", and no Opus or other audio-codec dependency or source file was found under mobile/lib (case-insensitive search for \"opus\", \"audio codec\", and \"voip\" returned zero matches)."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/Cargo.toml:90"
      - "grep_case_insensitive('opus|audio.*codec|voip', path='mobile/lib') -> zero matches"
  - statement: "The desktop encode pipeline (audio_relay_pipeline in desktop/src-tauri/src/huddle/relay_api.rs) constructs one opus::Encoder per connection at 48000 Hz, mono, Application::Voip, sets a target bitrate of 32000 bits/s via set_bitrate(Bitrate::Bits(32000)), and enables discontinuous transmission via set_dtx(true)."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/huddle/relay_api.rs"
  - statement: "The desktop encoder always encodes fixed 960-sample (20 ms at 48 kHz) float PCM frames (const FRAME_SAMPLES: usize = 960 in relay_api.rs), padding a short final chunk with zeros to reach that size before calling encode_float; desktop/src-tauri/src/huddle/jitter.rs's module documentation independently states the wire format is one Opus packet per 20 ms frame and defines FRAME_DURATION_MS = 20 with FRAME_TIMESTAMP_DELTA = 960 (SAMPLE_RATE_HZ / 1000 * FRAME_DURATION_MS)."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/huddle/relay_api.rs"
      - "desktop/src-tauri/src/huddle/jitter.rs"
  - statement: "An encoded Opus payload of 2 bytes or fewer is flagged FLAG_DTX in the v2 wire header so a receiver can identify a DTX/comfort-noise packet without re-parsing the Opus payload itself; desktop/src-tauri/src/huddle/wire.rs documents FLAG_DTX (bit 0) and states encoders MUST set it for any packet they tag as DTX."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/huddle/relay_api.rs"
      - "desktop/src-tauri/src/huddle/wire.rs"
  - statement: "The huddle wire protocol negotiates a frame-header format, not a codec choice: the WS auth message carries a protocol_version field (v1 legacy: bare Opus bytes; v2: an 8-byte sender-authored header of seq/ts_48k/level_dbov/flags followed by the Opus payload), and desktop/src-tauri/src/huddle/wire.rs states negotiation lives in that field, with a mixed-version room rejected by the relay as upgrade_required; Opus itself is not one of the negotiated fields at any version."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/huddle/wire.rs"
      - "desktop/src-tauri/src/huddle/relay_api.rs"
  - statement: "On receive, desktop/src-tauri/src/huddle/jitter.rs's OpusFrameDecoder wraps one opus::Decoder per remote peer (constructed at 48000 Hz, matching the peer's channel count via a Mono/Stereo match on `channels: u8`), registers it with a per-peer neteq::NetEq jitter buffer (min_delay_ms=40, max_delay_ms=200, max_packets_in_buffer=50) under RTP payload type OPUS_PAYLOAD_TYPE=111, and its decode() method calls decode_float(encoded, &mut self.scratch, false) unconditionally -- inband FEC is not requested on decode."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/huddle/jitter.rs"
  - statement: "desktop/src-tauri/src/huddle/jitter.rs's own doc comment states that receive-side FEC (decoding a frame's redundant copy on a known-lost prior frame) is out of scope for \"the initial 10-person fix\" and is tracked as a follow-up alongside encoder-side set_inband_fec, which the encoder construction in relay_api.rs does not call."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/huddle/jitter.rs"
      - "desktop/src-tauri/src/huddle/relay_api.rs"
  - statement: "Two unit tests in crates/buzz-relay/src/audio/wire.rs (parse_clamps_out_of_range_level_keeps_frame, parse_preserves_reserved_flag_bits) pin that the relay's v2 header parser separates the 8-byte header from a trailing Opus payload without inspecting or mutating that payload, using a literal b\"opus\" placeholder as the trailing bytes."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/audio/wire.rs"
  - statement: "desktop/src-tauri/src/huddle/jitter.rs's insert_packet_then_get_audio_returns_playout_frame test encodes real 20 ms silence frames with a live opus::Encoder (via its opus_silence_frame() helper, rather than a synthetic byte sequence), inserts six sequential packets into a PeerJitterBuffer, and asserts get_audio() returns a 480-sample (10 ms) playout frame -- a real encode-to-decode round trip through NetEq, not a mocked codec."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/huddle/jitter.rs"
  - statement: "As of the recorded revision, no end-to-end test in crates/buzz-test-client/tests/e2e_relay.rs opens the /huddle/{channel_id}/audio WebSocket route, so no test exercises a real client's Opus encoder sending audio through a live relay to another real client's Opus decoder; coverage of the codec path is unit-level (encoder/decoder construction and parameters, wire-header/payload separation, and single-process encode-decode round trips), not full end-to-end."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/e2e_relay.rs"
      - "crates/buzz-relay/src/audio/wire.rs"
      - "desktop/src-tauri/src/huddle/jitter.rs"
relationships:
  - type: references
    target: architecture-flows-huddle-audio
  - type: references
    target: architecture-containers-relay
  - type: references
    target: architecture-containers-desktop
---

# Opus audio codec: capability

Buzz huddles carry real-time voice as Opus-encoded audio: every participant's
microphone is encoded to Opus before it leaves the client, and every remote
peer's audio is Opus-decoded before playback. Opus is the sole codec used for
huddle voice in this repository today -- there is no codec negotiation and no
fallback codec; a client and the relay agree only on a wire *framing* version
(the header carried alongside the Opus payload), never on which codec to use.
This gives a human or agent participant low-bitrate, low-latency voice
suitable for many concurrent huddle participants, at a cost the relay never
pays: because the relay treats every frame as an opaque Opus byte string, it
cannot transcode, analyze, or moderate audio content -- only forward it.

## Maturity

**Shipped.** VISION.md marks "Huddles -- WebSocket Opus voice relay +
lifecycle events" as shipped (recording and per-track publishing are
separately marked planned, not part of this codec capability). The desktop
client's Opus encode pipeline (`connect_audio_relay` /
`audio_relay_pipeline` in `desktop/src-tauri/src/huddle/relay_api.rs`) and
decode pipeline (`OpusFrameDecoder` / `PeerJitterBuffer` in
`desktop/src-tauri/src/huddle/jitter.rs`) are real, exercised code paths, not
stubs, and the relay's frame-forwarding path
(`crates/buzz-relay/src/audio/{handler,room,wire,mesh}.rs`) is likewise
implemented and unit-tested.

**Desktop only.** The `opus` crate (pinned at `"0.3"` in
`desktop/src-tauri/Cargo.toml`) is the only codec dependency found in this
repository. A case-insensitive search of `mobile/lib` for `opus`,
`audio codec`, and `voip` returned no matches, so the mobile client has no
Opus (or other) audio-codec implementation at the recorded revision --
whatever huddle-related code exists in `mobile/lib` (message-kind rendering
for huddle lifecycle events) does not include voice capture, encode, decode,
or playback.

## Constraints and variants

**Encode parameters (desktop, fixed, not user-configurable at the recorded
revision).** 48 kHz sample rate, mono, `Application::Voip`, target bitrate
32000 bits/s (`set_bitrate(Bitrate::Bits(32000))`), DTX (discontinuous
transmission / comfort-noise) enabled (`set_dtx(true)`), fixed 20 ms (960
sample) frames -- a short final chunk is zero-padded to 960 samples rather
than encoded short. A DTX/comfort-noise packet is small enough (Opus payload
≤ 2 bytes) that the sender flags it explicitly (`FLAG_DTX` in the v2 wire
header) so a receiver can exclude it from active-speaker/level accounting
without re-parsing the Opus payload.

**Decode parameters (desktop, one `opus::Decoder` per remote peer).** 48 kHz,
channel count matched to the peer (mono or stereo), wrapped by a per-peer
`neteq::NetEq` jitter buffer (`min_delay_ms=40`, `max_delay_ms=200`,
`max_packets_in_buffer=50`) under a fixed synthetic RTP payload type
(`OPUS_PAYLOAD_TYPE=111`). Decode calls `decode_float(..., false)` --
inband FEC is not requested on the decode side, and the encoder does not call
`set_inband_fec` either; the code's own comments track adding receive-side
FEC as a follow-up, not yet implemented.

**Wire framing, not codec negotiation.** The auth message a client sends when
joining a huddle carries a `protocol_version` field the relay pins per room
(rejecting a mismatched later joiner with `upgrade_required`). Version 1
frames are bare Opus bytes; version 2 frames prepend an 8-byte sender-authored
header (`seq`, `ts_48k`, `level_dbov`, `flags`) before the Opus payload. This
negotiates *framing metadata*, never the codec -- every version's payload is
Opus, and the relay's role in both versions is identical: forward the frame,
optionally prefixed with the sender's `peer_index`, without decoding it.

**Relay-side bound, not codec-aware validation.** The relay caps an inbound
binary frame at `MAX_AUDIO_FRAME_BYTES` (4 KB, described in its own comment as
generous for a single Opus packet) and, for protocol v2, requires the frame
be at least long enough for the 8-byte header. Neither check inspects the
Opus payload itself for validity -- a corrupt but appropriately-sized Opus
packet is forwarded exactly like a valid one, and any decode failure surfaces
only at the receiving peer.

## Boundary

This node does not describe:
- **How a huddle session is joined, authenticated, admitted to a room, or
  torn down** -- see the flow node for the full join/relay/leave sequence,
  including the cross-pod mesh-ownership handshake and lifecycle events.
- **How the relay and desktop containers are built or deployed** -- see the
  architecture container nodes for `relay` and `desktop`.
- **The interface(s) huddle audio is exposed through** (the
  `/huddle/{channel_id}/audio` WebSocket route and its JSON control messages)
  -- not yet a corpus node at the recorded revision.
- **Recording or per-track publishing** -- VISION.md marks these planned, not
  implemented, and no code for either was found alongside the encode/decode
  pipelines documented here.
- **Non-Opus audio paths in the product**, if any exist elsewhere in the
  repository (for example agent text-to-speech/speech-to-text audio, which
  this node did not inspect) -- this node covers only the huddle
  microphone-to-peer voice path.

## Relationships

- references: `architecture-flows-huddle-audio` -- the join/relay/leave flow
  this codec's frames travel through.
- references: `architecture-containers-relay` -- the container that forwards
  (but never decodes) Opus frames between peers.
- references: `architecture-containers-desktop` -- the container that owns
  the only Opus encode/decode implementation found in this repository.

## Scope and omissions

**This node covers** the Opus codec's concrete role in Buzz huddles: that it
is the sole, non-negotiated codec; its maturity and desktop-only
implementation status; the desktop client's fixed encode and decode
parameters (sample rate, channels, application mode, bitrate, DTX, frame
size, FEC status); how codec framing (not codec choice) is versioned on the
wire; the relay's opaque, size-bounded but content-blind forwarding of Opus
frames; and the verification that exists for each of those claims.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The full huddle join/authentication/admission/teardown sequence | `architecture-flows-huddle-audio` |
| How the relay and desktop containers are built/deployed | `architecture-containers-relay`, `architecture-containers-desktop` |
| The WebSocket/JSON control-message interface huddle audio is exposed through | Not yet a corpus node |
| Recording and per-track publishing | Marked "planned" in `VISION.md`; not implemented at the recorded revision |
| Any non-huddle, non-Opus audio path in the product (e.g. agent TTS/STT) | Not inspected for this node |

**Expected but not verified when this node was written:**

- **No end-to-end test drives a real Opus frame from one client's encoder,
  through a live relay, to another client's decoder.** Verification here is
  unit-level: encoder/decoder construction and parameters, wire-header/payload
  separation on the relay side, and a single-process encode-then-decode round
  trip through NetEq on the desktop side. `crates/buzz-test-client/tests/e2e_relay.rs`
  contains no test opening the `/huddle/{channel_id}/audio` route.
  See also the same gap recorded in `architecture-flows-huddle-audio`.
- **Whether `opus::Bitrate::Bits(32000)` yields constant or variable bitrate
  output was not established.** The `opus` crate's own VBR/CBR default was
  not inspected; this node states only the target bitrate the code requests.
- **The relay-mesh (cross-pod) path's effect on Opus frames specifically was
  not re-verified here** beyond what `architecture-flows-huddle-audio` already
  documents (that mesh forwarding treats the frame as an opaque payload with a
  fencing check); no additional inspection of `buzz-relay-mesh` was performed
  for this node.
