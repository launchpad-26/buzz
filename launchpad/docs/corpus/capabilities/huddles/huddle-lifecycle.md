---
id: capabilities-huddles-huddle-lifecycle
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
  - statement: "Issue #756's definition of done requires this node to state trigger, preconditions and termination/outcome; list ordered interactions and data/state movement; identify authentication/authorization/trust-boundary crossings; and document failure/abort/rollback behavior with representative verification."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#756 definition of done"
  - statement: "KIND_HUDDLE_STARTED=48100, KIND_HUDDLE_PARTICIPANT_JOINED=48101, KIND_HUDDLE_PARTICIPANT_LEFT=48102, and KIND_HUDDLE_ENDED=48103 are the huddle lifecycle event kinds, in the 48000-48999 system/admin custom range."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs:588-596"
  - statement: "There is no dedicated 'Huddle' channel type: ChannelType's only variants are Stream, Forum, Dm and Workflow, and buzz_db::channel::create_channel is a generic channel constructor (channel_type, visibility, optional ttl_seconds) with no huddle-specific parameter or code path — a huddle is an ordinary (usually TTL-bearing) channel that later gets used through the /huddle/{channel_id}/audio route and linked by a kind:48100 event."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/channel.rs"
      - "crates/buzz-db/src/channel.rs:85-117"
  - statement: "A kind:48100 (HUDDLE_STARTED) event is ingested through the same generic pipeline as any other channel-scoped write: it requires Scope::ChannelsWrite and an 'h' tag resolving to a channel the author can write to, exactly like KIND_HUDDLE_PARTICIPANT_JOINED/LEFT/ENDED and KIND_HUDDLE_GUIDELINES; nothing at ingest time parses or validates the event's own content."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:430-435"
      - "crates/buzz-relay/src/handlers/ingest.rs:634-639"
  - statement: "huddle_started_content_links parses a kind:48100 event's content as JSON and requires an 'ephemeral_channel_id' field whose value exactly matches the target ephemeral channel's UUID; malformed JSON or a mismatched/missing field makes the event count as non-linking."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/event.rs:214-224"
  - statement: "huddle_started_link_exists additionally requires the candidate kind:48100 event to live in the claimed parent channel and to be signed by the ephemeral channel's own creator (channel.created_by) — a member of the parent channel who is not that creator can publish their own kind:48100 event there, but it will never satisfy this check."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/event.rs:226-268"
  - statement: "ensure_membership resolves a lifecycle_parent_id via huddle_started_link_exists for every TTL-bearing (ephemeral) channel, regardless of its visibility, before any peer — including the channel's own creator — is admitted to the audio room; an unlinked ephemeral channel returns 'ephemeral channel is not linked to claimed parent' and the join is rejected. An archived channel is rejected even earlier, before this linkage check runs."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/audio/handler.rs:1170-1208"
  - statement: "The channels table's ttl_seconds/ttl_deadline columns, and a partial index on ttl_deadline scoped to non-archived, TTL-bearing channels, were established in the initial schema migration."
    entry_class: FACT
    evidence:
      - "migrations/0001_initial_schema.sql:95-96"
      - "migrations/0001_initial_schema.sql:109-110"
  - statement: "reap_expired_ephemeral_channels archives (sets archived_at = NOW()) any channel whose ttl_deadline has passed, guarded by archived_at IS NULL for idempotency and by community_write_allowed; the query carries no huddle-specific condition, so it treats a huddle's ephemeral channel identically to any other TTL-bearing channel."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/channel.rs:1498-1531"
  - statement: "buzz-relay runs the ephemeral-channel reaper as a background loop (default interval 60s, overridable via BUZZ_REAPER_INTERVAL_SECS) that, for each channel it archives, emits a generic 'channel_auto_archived' system message, re-emits the channel's NIP-29 discovery events, and evicts live channel-subscription connections — it never emits kind:48103 and never touches the audio Room/mesh-lease state a huddle may be using."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:635-712"
  - statement: "An owner or admin can also explicitly archive any channel — including a TTL-bearing huddle channel — by publishing a kind:9002 (KIND_NIP29_EDIT_METADATA) event with an 'archived' tag; that tag requires the elevated Scope::AdminChannels, unlike every other kind:9002 field change, which only requires Scope::ChannelsWrite."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:414-425"
  - statement: "handle_edit_metadata's 'archived' => 'true' arm calls archive_channel and emits a generic 'channel_archived' system message — the same generic path a non-huddle channel's explicit archive takes; it does not emit kind:48103 and does not touch the audio Room/mesh-lease state."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/side_effects.rs:1440"
      - "crates/buzz-relay/src/handlers/side_effects.rs:1582-1598"
  - statement: "archived_at is checked only at two audio-join-time points (an early post-connection check and again inside ensure_membership) — no code in the audio connection's live receive/send/heartbeat/mesh loops re-reads or reacts to archived_at, so an already-admitted peer's live audio session is not observed, notified, or torn down by either the TTL reaper or an explicit admin archive while it runs."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/audio/handler.rs:388-416"
      - "crates/buzz-relay/src/audio/handler.rs:1177-1187"
  - statement: "The already-drafted architecture-flows-huddle-audio node documents the only server-driven teardown paths for an already-admitted audio session: last-peer-leaves auto-end (which itself archives the channel and emits kind:48103), owner mesh-lease loss or draining, and mesh control-stream closure — none of which is triggered by the channel becoming archived through the TTL reaper or an explicit admin action."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/flows/huddle-audio.md"
  - statement: "VISION.md states 'Huddle lifecycle flows as Nostr events: started, joined, left, ended' and marks voice, room lifecycle, and lifecycle events as wired, with recording and per-track publishing still planned."
    entry_class: FACT
    evidence:
      - "VISION.md:104-111"
  - statement: "reap_expired_ephemeral_channels's archival behavior (that it archives an expired channel, returns its community/host/channel-id provenance, and that unarchiving renews the TTL deadline so the same channel is not immediately re-reaped) is covered by two Postgres-backed unit tests in channel.rs's own tests module."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/channel.rs:1858-1899"
      - "crates/buzz-db/src/channel.rs:1797-1849"
  - statement: "huddle_started_content_links's JSON/field-matching behavior (a matching ephemeral_channel_id passes, a wrong field or non-JSON content does not) is covered by a unit test in event.rs's own tests module."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/event.rs:2677-2690"
  - statement: "No test found in this repository exercises the interaction between an in-progress audio session and either the TTL reaper or an explicit admin archive of its channel — neither channel.rs's, handler.rs's, nor side_effects.rs's own unit-test modules construct that scenario, and architecture-flows-huddle-audio.md already recorded that crates/buzz-test-client/tests/e2e_relay.rs has no end-to-end test for the audio route at all."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/channel.rs"
      - "crates/buzz-relay/src/audio/handler.rs"
      - "crates/buzz-relay/src/handlers/side_effects.rs"
      - "crates/buzz-test-client/tests/e2e_relay.rs"
relationships:
  - type: references
    target: architecture-flows-huddle-audio
---

# Huddle lifecycle

How one huddle's underlying channel moves from creation, through an active
session, to termination — independent of the moment-to-moment audio join,
relay and leave mechanics of any one participant's connection, which
`architecture-flows-huddle-audio` already documents in full.

## Note on scope and type

This node carries `type: capabilities` because it is filed under this
Feature's (#612) collaboration-capability corpus surface, documenting the
**huddle capability's own lifecycle** as a product-level concept — created,
active, ended — rather than the C4-style runtime interaction of one
connection joining and relaying audio, which is `architecture-flows-huddle-audio`'s
subject and already carries `type: architecture` per that node's own
reasoning. The two nodes describe different altitudes of the same feature and
`references` each other's territory rather than restating it: this node
narrates the channel's own state machine (create → active → end, and the
three independent ways "end" can arrive); the audio-flow node narrates what
happens to one WebSocket connection inside the "active" state.

There is no dedicated "huddle" entity in the schema. A huddle is an ordinary
channel — usually created with a `ttl_seconds` so it auto-expires — that
becomes a huddle in practice only once a `kind:48100` event links to it and a
client opens `/huddle/{channel_id}/audio` against it.

## Trigger, preconditions, and termination

**Trigger.** The channel's creator (the pubkey recorded as `created_by` when
the channel row was inserted) signs and publishes a `kind:48100`
(`KIND_HUDDLE_STARTED`) event in a parent channel, with content
`{"ephemeral_channel_id": "<uuid>"}` naming the (usually TTL-bearing) channel
that will serve as the huddle's audio room.

**Preconditions for a legitimate lifecycle to exist:**

1. The target channel exists and is not archived.
2. If the target channel is TTL-bearing (ephemeral) — the common case for a
   huddle — a `kind:48100` event exists in the claimed parent channel, is
   signed by the target channel's own `created_by` pubkey, and its content's
   `ephemeral_channel_id` matches the target channel's UUID exactly. A
   `kind:48100` posted by anyone else in that same parent channel is accepted
   at ingest but never satisfies this check.
3. Publishing the `kind:48100` event itself needs nothing huddle-specific —
   only the same `Scope::ChannelsWrite` and channel membership any other
   channel-scoped write requires. The relay does not parse or verify the
   event's content at ingest time; the link is only checked later, lazily, at
   audio-join time.

**Termination / outcome.** The lifecycle ends in exactly one of three ways,
which do not share a code path:

- **Last-participant auto-end.** The last peer leaves the live audio room; the
  owning pod archives the channel and emits `kind:48103`
  (`KIND_HUDDLE_ENDED`). Fully documented in
  `architecture-flows-huddle-audio`'s *Leaving and room auto-end* section —
  not restated here.
- **TTL expiry (reaper).** A background sweep archives the channel once its
  `ttl_deadline` passes, with no regard to whether an audio session is live.
- **Explicit admin archive.** An owner/admin archives the channel directly, at
  any time, with no regard to whether an audio session is live or the channel
  even has a TTL.

The last two both set `archived_at` through generic, non-huddle-aware channel
code and **never emit `kind:48103`** — from the lifecycle-event stream alone,
a TTL-expired or admin-archived huddle looks identical to one that was simply
never used, while a `kind:48103` unambiguously means "the last participant
left."

## Ordered interactions and state movement

1. **Create.** A client calls the generic channel-creation path
   (`buzz_db::channel::create_channel`), typically with a `ttl_seconds` value,
   getting back a new channel row with `created_by` set to the caller's
   pubkey and (if TTL was set) a `ttl_deadline` of `NOW() + ttl_seconds`.
2. **Link.** The same pubkey (`created_by`) signs and publishes `kind:48100`
   in some parent channel, with content naming the new channel's UUID. This
   event is stored like any other channel event; nothing yet reads or
   verifies its content.
3. **Activate (deferred, lazy).** The link is only evaluated the first time
   someone opens `/huddle/{channel_id}/audio` against that channel:
   `ensure_membership` looks up the channel, rejects it if already archived,
   and — because it is TTL-bearing — requires `huddle_started_link_exists` to
   find a matching, creator-signed `kind:48100` in the claimed parent before
   admitting anyone. A channel that was created but never validly linked can
   be joined by no one.
4. **Active session.** Participants join and leave the audio room; each join
   emits `kind:48101`, each leave emits `kind:48102`. This state and its
   internal mechanics (admission, frame relay, cross-pod ownership, heartbeat)
   are `architecture-flows-huddle-audio`'s territory.
5. **Terminate — one of three independent paths:**
   - the room empties and the owning pod archives + emits `kind:48103`
     (audio-flow node); or
   - the reaper's periodic sweep (`reap_expired_ephemeral_channels`, run from
     a loop in `buzz-relay`'s startup) finds `ttl_deadline < NOW()` and
     archives the channel, emits a generic `channel_auto_archived` system
     message, refreshes NIP-29 discovery, and evicts channel-subscription
     (chat) connections — with no awareness of any live audio Room; or
   - an owner/admin publishes `kind:9002` with an `archived` tag, which
     `handle_edit_metadata` turns into the same `archive_channel` call and a
     generic `channel_archived` system message — likewise with no awareness
     of any live audio Room.
6. **After termination.** New join attempts are rejected (`archived_at` is
   checked at the top of `ensure_membership`). An **already-admitted** audio
   connection is unaffected by paths 5b/5c — nothing in its live loop
   observes `archived_at` — until it ends through one of the audio-flow
   node's own teardown causes (owner lost/draining, mesh stream closed,
   client leave).

## Authentication, authorization, and trust-boundary crossings

| Boundary | Mechanism | Notes |
|---|---|---|
| Publish `kind:48100`/`48101`/`48102`/`48103`/`48106` | Standard event signature + `Scope::ChannelsWrite` + `h`-tag channel membership | Identical gate for all five kinds; no elevated permission to "start" a huddle |
| A `kind:48100` counts as the legitimating link | Content must parse as JSON with a matching `ephemeral_channel_id`, **and** the event must be signed by the target channel's own `created_by` | Anyone with channel-write access can publish a `kind:48100`; only the channel's own creator's version is ever load-bearing |
| Join the audio room | `ensure_membership`'s archived-check, then (for TTL-bearing channels) the link check above, then ordinary channel-membership admission | Applies uniformly, including to the creator's own join |
| Explicit archive of the channel | `kind:9002` `archived` tag, gated by the elevated `Scope::AdminChannels` | The only termination path that requires elevated privilege; TTL expiry requires none (a background sweep with no human actor) |
| Archived state → live audio session | **No boundary exists.** | Neither reaper-driven nor admin-driven archival is observed by an already-admitted audio connection |

## Failure, abort, and rollback behavior

**Creation-time validation is deferred, not immediate.** Publishing an
invalid or unlinked `kind:48100` — wrong `ephemeral_channel_id`, malformed
content, or signed by someone other than the target channel's creator —
succeeds at ingest unconditionally. The only consequence surfaces later, at
audio-join time, as a rejected join (`"ephemeral channel is not linked to
claimed parent"`). There is no rollback to perform, because nothing was ever
provisionally committed on the strength of an unverified link.

**The three termination paths do not roll back into one another.**
Last-participant auto-end's own rollback (an archive-write failure
un-archiving the room via `clear_ended` so the huddle stays rejoinable) is
`architecture-flows-huddle-audio`'s own documented behavior and is not
duplicated here. The TTL reaper and the explicit-archive path have no
equivalent rollback step of their own to document: `archive_channel` and
`reap_expired_ephemeral_channels` are simple, idempotent `UPDATE`s (guarded by
`archived_at IS NULL`), and neither path emits a lifecycle event whose
absence-on-failure would need to be reconciled.

**The asymmetry between the three termination paths is the lifecycle's most
load-bearing gap.** Only last-participant auto-end emits `kind:48103`; TTL
expiry and explicit admin archive both flip `archived_at` through completely
generic, huddle-unaware channel code and stop there. A client that treats the
Nostr lifecycle-event stream as authoritative (per `VISION.md`'s framing:
"Huddle lifecycle flows as Nostr events: started, joined, left, ended") will
never see an "ended" event for a huddle that was reaped or explicitly
archived, even though its channel is now archived and unjoinable. And because
`archived_at` is checked only at join time, a huddle that is still actively
being used when it is reaped or explicitly archived keeps relaying audio
uninterrupted — the archive silently forecloses future joins without
affecting the session already in progress.

### Representative verification

- `reap_expired_ephemeral_channels`'s archival behavior, its returned
  community/host/channel-id provenance, and that unarchiving renews
  `ttl_deadline` (so an unarchived channel is not immediately re-reaped) are
  covered by `reap_expired_ephemeral_channels_returns_row_community_and_host`
  and `test_unarchive_expired_ephemeral_channel_renews_ttl_deadline` in
  `crates/buzz-db/src/channel.rs`'s `tests` module.
- `huddle_started_content_links`'s JSON/field-matching logic is covered by
  `huddle_started_content_requires_matching_ephemeral_field` in
  `crates/buzz-db/src/event.rs`'s `tests` module.
- **Gap.** No test — unit or end-to-end — exercises a huddle's channel being
  reaped or explicitly archived while an audio session against it is live.
  `architecture-flows-huddle-audio` already recorded that no end-to-end test
  opens the `/huddle/{channel_id}/audio` route at all; this node adds that
  the interaction this section describes (archive vs. an in-progress session)
  has no test coverage of any kind, unit or end-to-end.

## Boundary

This node does not describe:

- **The audio join/relay/leave mechanics of one connection** — admission,
  frame relay, cross-pod mesh ownership, heartbeat, per-connection teardown
  causes. See `architecture-flows-huddle-audio`.
- **The wire contract of any one huddle event kind** (`48100`-`48103`,
  `48106`) — tags, full content schema, access model. Not yet a corpus node.
- **Huddle text-channel guidelines** (`kind:48106`). Not yet a corpus node.
- **Desktop/mobile client huddle UI, reconnection behavior, or agent-side
  STT/TTS integration.** Not yet a corpus node; the last is mentioned only as
  a capability in `VISION.md`.
- **The general ephemeral-channel/TTL mechanism** as a feature in its own
  right (it also backs non-huddle use cases). This node only describes how
  that generic mechanism intersects with a huddle's own lifecycle.

## Relationships

- `references`: `architecture-flows-huddle-audio` — the audio join/relay/leave
  flow this node's "active session" state defers to, and the node this one's
  auto-end/rollback claims point back to rather than restate.

## Scope and omissions

**This node covers** how one huddle's underlying channel is created and
linked via `kind:48100`, the deferred (join-time-only) validation of that
link, the three independent ways the lifecycle terminates (last-participant
auto-end, TTL reaper, explicit admin archive), the authorization each
termination path does or does not require, and the specific asymmetry that
only last-participant auto-end emits `kind:48103` while the other two leave
an already-live audio session running uninterrupted.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Audio join/relay/leave mechanics for one connection | `architecture-flows-huddle-audio` |
| The wire contract of `kind:48100`-`48103`/`48106` | Not yet a corpus node |
| Huddle text-channel guidelines (`kind:48106`) | Not yet a corpus node |
| Client-side (desktop/mobile/agent) huddle behavior | Not yet a corpus node |
| The ephemeral-channel/TTL mechanism as a general feature | Not yet a corpus node |

**Expected but not verified when this node was written:**

- **No test exercises reap-or-explicit-archive against a live audio session**,
  as stated in *Representative verification*. Whether an already-connected
  peer keeps relaying audio indefinitely after its channel archives, or
  whether some other mechanism eventually catches this case, was verified by
  reading every place `archived_at` is checked (none inside the connection's
  live loops), not by observing the behavior at runtime.
- **Whether any client (desktop, mobile, or agent) independently polls
  channel/archived state to leave a huddle whose channel was archived out from
  under it was not inspected.** This node documents only the relay's side of
  the contract, matching `architecture-flows-huddle-audio`'s own stated
  boundary.
- **Migrations after `0001_initial_schema.sql` that might further constrain or
  alter `ttl_seconds`/`ttl_deadline` were not enumerated exhaustively** —
  `0022_event_ttl_refresh.sql` and `0024_event_ttl_refresh_shared_lock.sql`
  also reference TTL machinery and were not opened; the initial schema
  migration was confirmed sufficient for the columns and index cited above,
  but a later migration narrowing their semantics cannot be ruled out from
  that alone.
