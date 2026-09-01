---
id: capabilities-channels-stream-channel
type: capabilities
status: draft
origin: launchpad
audiences:
  - developer
  - agent
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5."
    entry_class: FACT
    evidence:
      - "commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
  - statement: "buzz-core's ChannelType enum has exactly four variants -- Stream, Forum, Dm, Workflow -- and its own doc comment names Stream as 'Linear message stream (the default)', distinct from Forum's 'Threaded forum-style discussion'."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/channel.rs:57-68"
  - statement: "ChannelType::as_str/FromStr round-trip the wire string 'stream' for the Stream variant, matching the DB enum and Nostr tag value."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/channel.rs:70-100"
  - statement: "crates/buzz-sdk re-exports buzz_core::channel::ChannelType as ChannelKind, so the client-facing SDK type callers use (e.g. buzz_sdk::ChannelKind::Stream) is the same enum buzz-core and buzz-db share."
    entry_class: FACT
    evidence:
      - "crates/buzz-sdk/src/lib.rs:80"
  - statement: "The Postgres schema defines channel_type as an enum with values ('stream', 'forum', 'dm', 'workflow') and the channels table's channel_type column defaults to 'stream'."
    entry_class: FACT
    evidence:
      - "migrations/0001_initial_schema.sql:28"
      - "migrations/0001_initial_schema.sql:76"
  - statement: "buzz-cli's channel-create command rejects any --type other than 'stream' or 'forum' with a usage error, then maps the accepted string to buzz_sdk::ChannelKind::Stream or ::Forum; Dm and Workflow channels are not user-creatable through this path."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/commands/channels.rs:282-317"
  - statement: "get_accessible_channels's own doc comment and its SQL ORDER BY clause order a user's accessible channels stream -> forum -> dm before sorting by name, so channel type is also a first-class sort key in the channel-listing read path, not only a stored attribute."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/channel_members.rs:954-957"
      - "crates/buzz-db/src/store/channel_members.rs:997-999"
  - statement: "The desktop app's ChatHeader icon-selection logic special-cases channelType === 'dm' (CircleDot) and channelType === 'forum' (FileText) but falls through to the generic Hash icon for every other case, including Stream; there is no Stream-specific branch."
    entry_class: FACT
    evidence:
      - "desktop/src/features/chat/ui/ChatHeader.tsx:72-83"
  - statement: "buzz-core's kind registry documents KIND_STREAM_MESSAGE (9) as the 'NIP-29 group chat message kind', with a family of related kinds (KIND_STREAM_MESSAGE_V2 40002, _EDIT 40003, _PINNED 40004, _BOOKMARKED 40005, _SCHEDULED 40006, a stream reminder 40007, and _DIFF 40008 for unified-diff patch messages) grouped under the same 'Stream messaging' comment block, separate from the 'Forum / social (45000-45999)' block defining KIND_FORUM_POST/_VOTE/_COMMENT."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs:473-497"
      - "crates/buzz-core/src/kind.rs:547-554"
  - statement: "VISION.md names Stream as one of the app's seven surfaces -- 'Topic-based real-time chat. Work.' with zero default notifications -- and separately describes it as 'Slack-like, fast. Mandatory topics -> sub-replies. Zero-notification default,' explicitly contrasted against Forum's 'Discourse-like, slow. Post -> flat replies.'"
    entry_class: FACT
    evidence:
      - "VISION.md:15-19"
      - "VISION.md:27-28"
  - statement: "VISION.md's own Status table marks 'Desktop client (Tauri) -- Stream, Home, Forum, DMs, Agents, Workflows, Search, Settings, Profiles, Presence' and 'Channel features -- messaging, threads, reactions, canvases, media uploads, editing, deletion, typing indicators, NIP-29, soft-delete' both shipped."
    entry_class: FACT
    evidence:
      - "VISION.md:223-224"
  - statement: "VISION_PROJECTS.md's own Status table marks 'Channels, forums, DMs, canvases' as shipped today."
    entry_class: FACT
    evidence:
      - "VISION_PROJECTS.md:249"
  - statement: "The channels table carries a topic_required boolean column (default FALSE, not scoped by channel_type in its DDL), but no relay-side handler in crates/buzz-relay was found reading or enforcing topic_required; a grep of crates/buzz-relay for the column returned zero matches, so whether VISION.md's 'Mandatory topics' description of Stream is wired to this column, to some other mechanism, or is still a designed-not-built behavior is not established by this node."
    entry_class: FACT
    evidence:
      - "migrations/0001_initial_schema.sql:86"
      - "grep_recursive('topic_required', path='crates/buzz-relay/') -> zero matches, run against commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
  - statement: "crates/buzz-test-client's end-to-end relay test suite creates its default test channel by submitting a signed kind:9007 event carrying a [\"channel_type\", \"stream\"] tag to POST /events and asserting the relay accepts it, and this create_test_channel helper is the shared fixture reused across the e2e_relay, e2e_git, e2e_persona, e2e_media_video, e2e_media_extended, e2e_human_edit_agent_content, e2e_nostr_interop, and e2e_event_reminder integration test files, plus the multitenant conformance suite -- so a stream channel being created and accepted end-to-end through the relay's real event-ingestion path is exercised by the bulk of this repository's e2e coverage, not by a single isolated test."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/e2e_relay.rs:170-193"
  - statement: "git log for crates/buzz-core/src/channel.rs shows exactly three commits (a hash-prefix-stripping fix, an LLM-comment cleanup, and the sprout-to-buzz rename), none of which introduces ChannelType or a Stream variant as a new addition -- consistent with Stream having been the schema's default channel type since at least the current migration 0001 (itself a comprehensive multi-tenant rewrite, per its own commit message, not the repository's literal first migration), rather than a capability added later in a dedicated change."
    entry_class: INFERENCE
    evidence:
      - "git_log_oneline(path='crates/buzz-core/src/channel.rs') -> d0ab3fdb0, 73cc31cc5, d99ad131f"
      - "git_log_oneline(path='migrations/0001_initial_schema.sql') -> tail commit 14fba21e5 'Multi-tenant Buzz relay: community_id as a server-resolved key (comprehensive rewrite) (#1321)'"
    confidence: 0.6
relationships:
  - type: references
    target: architecture-containers-relay
  - type: references
    target: architecture-flows-live-fanout
---

# Stream channel: capability

A Buzz community's default, always-on real-time chat surface. Every channel a
user or agent creates through the ordinary channel-creation path is a stream
channel unless they deliberately choose the forum type instead: it is the
"Slack-like, fast" lane for live back-and-forth work conversation, as opposed
to Forum's "Discourse-like, slow" async long-form posts, a 1:1/group DM, or an
internal workflow-execution channel. A user or agent posting in a stream
channel gets ordinary linear messages -- with editing, reactions, pinning,
bookmarking, scheduling, reminders, and diff/patch messages all available as
first-class message kinds -- delivered live to every other member present, with
notifications off by default.

**Naming note.** "Stream" here names the channel *type* enum value
(`ChannelType::Stream`, wire value `"stream"`), not a live-video or
broadcast-streaming feature. Nothing in the code or in VISION.md ties this
capability to audio/video broadcast; that reading of "stream" does not apply
here (see *Boundary* below).

## Maturity

Shipped. `ChannelType::Stream` is a real, exercised enum variant backed by a
Postgres column default, the CLI's channel-create path, and the desktop
client's channel-listing and rendering code (see the evidence ledger above for
each). VISION.md's own Status table separately marks both the desktop
client's "Stream" surface and general channel features (messaging, threads,
reactions, canvases, media uploads, editing, deletion, typing indicators,
NIP-29, soft-delete) as shipped, and VISION_PROJECTS.md's Status table marks
"Channels, forums, DMs, canvases" as shipped today.

One specific behavior VISION.md attributes to Stream -- "Mandatory topics ->
sub-replies" -- could not be confirmed as implemented and gated specifically
to `channel_type = 'stream'`: the `channels.topic_required` column exists but
no relay handler enforcing it was found (see the evidence ledger and *Scope
and omissions* below). Treat that one sentence as a designed intent, not a
verified behavior, until a citation for its enforcement exists.

**Verification.** The repository's own end-to-end relay test suite creates a
real stream channel as its shared default fixture -- a signed kind:9007 event
carrying a `["channel_type", "stream"]` tag, submitted to `POST /events` and
asserted accepted by the live relay -- and that fixture is reused across the
bulk of the e2e integration suite (relay, git, persona, media, human-edit,
Nostr interop, event-reminder, and multitenant conformance tests). Creating
and accepting a stream channel end-to-end is therefore exercised continuously,
not by an isolated test.

## Boundary

This node does not describe:
- **How channels of any type are built** -- the relay's connection/auth/event
  pipeline, `buzz-db`'s channel storage, and `buzz-core`'s shared enums. See
  the architecture node for the relay container.
- **The interface(s) this capability is exposed through** -- `buzz-cli`'s
  `channels create --type stream`, the MCP server's channel tools, and the
  desktop UI's channel list/composer. No interface-type corpus node exists yet
  to `references` here; this is a gap, not a decision that none applies.
- **The step-by-step flow through a stream channel** -- a user joining a
  channel, composing a message, and seeing it delivered live to other members.
  A `flow`-type node would narrate that sequence; none has been drafted yet
  (issue #1338's template is unlanded).
- **How the running system is operated** -- deployment, monitoring, incident
  response for the relay that serves stream channels. That is the
  `operations` corpus surface.
- **Live-video or broadcast streaming.** Despite the name, `ChannelType::Stream`
  is a text-chat channel type, not a media-broadcast capability. Buzz's actual
  real-time voice feature is huddles (WebSocket Opus audio), which is a
  separate, unrelated capability from this one.
- **Forum, DM, and Workflow channels themselves.** Each is a distinct
  `ChannelType` variant with its own behavior (Forum's threaded posts/votes/
  comments, DM's 1:1/group semantics, Workflow's internal execution channel);
  none of the three has its own capability node yet, so this node does not
  attempt to describe them beyond the contrast needed to place Stream.

## Relationships

- references: architecture-containers-relay -- the relay container that
  persists stream-channel messages and routes them through the event pipeline.
- references: architecture-flows-live-fanout -- the flow that delivers a
  stream channel's messages to connected members in real time, including the
  channel-scoped fan-out and access-filtering steps a stream message goes
  through on the way to a subscriber.

## Scope and omissions

**This node covers** what the Stream channel type is, how it is represented
in `buzz-core`, `buzz-db`'s Postgres schema, `buzz-cli`, and the desktop
client; what distinguishes it from Forum, DM, and Workflow channels at the
type level; and what VISION.md and VISION_PROJECTS.md state about its product
maturity.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| How channels (of any type) are built -- relay, buzz-core, buzz-db | `architecture-containers-relay` |
| How a stream message is delivered live once ingested | `architecture-flows-live-fanout` |
| The interface(s) exposing this capability (buzz-cli, MCP, desktop UI) | a future interface-type node (none exists yet) |
| The step-by-step flow through a stream channel | a future flow node (issue #1338's template, unlanded) |
| How the running system is operated | the `operations` corpus surface |
| The Forum, DM, and Workflow channel types themselves | future capability nodes (none exist yet) |

**Expected but not verified when this node was written:**
- **Whether VISION.md's "Mandatory topics -> sub-replies" description of
  Stream is actually enforced anywhere**, and if so, whether it is gated by
  the `channels.topic_required` column. A repository-wide search of
  `crates/buzz-relay` for that column found no reference, so this remains an
  open gap between the product description and confirmed code behavior rather
  than a resolved claim.
- **Whether `nip29_group_id` (a generic, nullable column on the `channels`
  table, not scoped to `channel_type` in its DDL) has any Stream-specific
  behavior**, versus being wired identically for every channel type. Only the
  schema shape was checked; no relay code path conditioning on
  `channel_type = 'stream'` together with `nip29_group_id` was inspected.
- **No corpus interface or flow node exists yet for this capability.** The
  `references` and boundary sections above name the gap; they cannot cite a
  node that has not been drafted.
