---
id: capabilities-messaging-stream-message
type: capabilities
status: draft
origin: launchpad
audiences:
  - agent
  - developer
evidence:
  - statement: "This node was authored and checked against repository revision 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5."
    entry_class: FACT
    evidence:
      - "commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
  - statement: "`KIND_STREAM_MESSAGE` is the constant `9` -- the NIP-29 group chat message kind -- and its doc comment records that earlier attempts used kind:10001 (wrong -- the NIP-33 parameterized-replaceable range) and then kind:40001 before the code settled on kind:9 as the correct, currently-live kind."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs:473-479"
  - statement: "The same doc comment documents an agent-shutdown convention layered on top of ordinary stream messages, not a separate event kind: the agent's owner sends a kind:9 message with content `\"!shutdown\"` and a `#p` tag mentioning the agent, and the harness exits gracefully on that convention."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs:475-478"
  - statement: "`ChannelType::Stream` is documented as \"Linear message stream (the default)\", one of four channel types (`Stream`, `Forum`, `Dm`, `Workflow`) whose canonical string form (`\"stream\"`) matches the DB enum and Nostr tags; this is the channel type this capability's messages are posted into."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/channel.rs:57-97"
  - statement: "`required_scope_for_kind`'s match arm groups `KIND_STREAM_MESSAGE` together with `KIND_STREAM_MESSAGE_V2`, the other stream-message variant kinds (edit/pinned/bookmarked/scheduled/reminder/diff), and forum kinds under `Scope::MessagesWrite` -- an authenticated principal must hold that scope to post a stream message, and `ingest_event_inner` rejects the event with `IngestError::AuthFailed` otherwise."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:378-392"
  - statement: "`requires_h_channel_scope` includes `KIND_STREAM_MESSAGE` in its match, so ingest requires an `h`-tag-resolvable `channel_id` for a stream message and rejects the event outright if none can be resolved -- every stream message is channel-scoped, never a global/channel-less event."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:611-627"
  - statement: "`ingest_event_inner` runs `validate_link_preview_tags` specifically when `kind_u32 == KIND_STREAM_MESSAGE`, before the generic `imeta` media-tag validation that applies to every kind -- link-preview validation is a behavior distinguishing stream messages from other event kinds, not a generic ingest check."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:2745-2750"
  - statement: "`validate_link_preview_tags` enforces: at most 8 `link-preview snapshot` tags, each an 11-field tag whose canonical URL (index 3) must parse as `https`, carry no username/password/fragment, be unique among the event's link-preview tags, and appear literally inside `event.content`; or, exclusively, a single `[\"link-preview\", \"none\"]` suppression marker that may not coexist with any snapshot tag."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:222-262"
  - statement: "Unit tests exercise this link-preview validation directly against `KIND_STREAM_MESSAGE` events: a lone `[\"link-preview\",\"none\"]` marker is accepted, a duplicated suppression marker is rejected, and a suppression marker mixed with a snapshot tag is rejected regardless of tag order."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:3857-3904"
  - statement: "`resolve_nip10_thread_meta` computes a channel-scoped message's NIP-10 `depth` (0 for a root, 1 for a direct reply, 2 for a reply-to-a-reply) and separately reads whether the event carries an explicit `[\"broadcast\", \"1\"]` tag, storing that as a `broadcast` boolean alongside the thread-metadata row."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:721-857"
  - statement: "`get_channel_window_on` -- the query backing a stream channel's main timeline -- filters to rows where `thread_metadata` is absent, `depth = 0`, or `depth = 1 AND broadcast = true`; a depth-1 reply with no broadcast tag, and every depth-2-or-deeper reply, is excluded from the main channel window regardless of its `depth`/`broadcast` combination and is reachable only through the separate thread-reply query."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/thread.rs:614-688"
  - statement: "`build_mentions_query` (the `@`-mention feed) and `build_activity_query` (the personal activity feed) both include `KIND_STREAM_MESSAGE` (alongside `KIND_STREAM_MESSAGE_V2`, `KIND_FORUM_POST`, and other content kinds) in their `kind IN (...)` filters, so a stream message the requesting user is mentioned in, or that lands in their accessible channels, surfaces in both feed surfaces the same way a forum post does."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/feed.rs:85-110"
      - "crates/buzz-db/src/feed.rs:252-266"
  - statement: "In every code path checked for this node -- `required_scope_for_kind`'s scope match, `requires_h_channel_scope`'s channel-scoping match, and both feed queries' `kind IN (...)` filters -- `KIND_STREAM_MESSAGE` (9) and `KIND_STREAM_MESSAGE_V2` (40002) are always listed together and handled identically; no branch inspected treats one differently from the other."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:378-392"
      - "crates/buzz-relay/src/handlers/ingest.rs:611-627"
      - "crates/buzz-db/src/feed.rs:85-110"
      - "crates/buzz-db/src/feed.rs:252-266"
  - statement: "`test_reply_ingest_pushes_live_thread_summary` builds a `Kind::Custom(9)` event (a stream message) tagged with an `h` channel tag as a thread root, sends it through a live relay connection, asserts it is accepted, and then asserts a live-delivered `kind:39005` thread-summary event follows over a subscription scoped to that channel -- an end-to-end demonstration that a stream message is accepted, stored, and drives derived live thread state."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/e2e_relay.rs:2579-2620"
  - statement: "Root `VISION_PROJECTS.md`'s Status table marks the row \"Channels, forums, DMs, canvases\" as \"Ships today\", and stream-type channels are one of the four `ChannelType` variants that row's \"Channels\" covers."
    entry_class: FACT
    evidence:
      - "VISION_PROJECTS.md:247"
relationships:
  - type: references
    target: architecture-flows-event-ingestion
  - type: references
    target: architecture-flows-live-fanout
  - type: references
    target: architecture-containers-relay
---

# Stream message: capability

A member of a stream-type channel (`ChannelType::Stream` -- "linear message stream
(the default)") can post a message that appears in that channel's main, linear
timeline for every other member to read live. The message may carry a link
preview (an author-supplied snapshot of a URL mentioned in the message, or an
explicit suppression marker), and may reply to an earlier message in the same
channel via NIP-10 threading; a reply only rejoins the channel's main timeline
if it is a direct reply explicitly marked for broadcast, otherwise it is
reachable only by opening the parent message's own thread. A stream message a
user is mentioned in, or that lands in one of their accessible channels, also
surfaces in that user's `@`-mentions feed and personal activity feed. A
narrow owner-to-agent convention is layered on the same kind: a stream message
whose content is exactly `"!shutdown"`, mentioning the target agent via a `#p`
tag, is the signal an agent harness treats as a graceful shutdown request.

## Maturity

**Shipped.** `KIND_STREAM_MESSAGE` (kind:9) is a stable, currently-live event
kind whose doc comment records a settled numbering history (wrong attempts at
kind:10001 and kind:40001 before landing on kind:9), not an in-progress
migration. `VISION_PROJECTS.md`'s own Status table marks "Channels, forums,
DMs, canvases" -- the row covering this capability's channel type -- "Ships
today". `test_reply_ingest_pushes_live_thread_summary` exercises the full path
end to end: post a kind:9 message, have it accepted, and observe the
live-delivered derived thread state that follows.

## Boundary

This node does not describe:
- **How the relay is built** (containers, components, the Postgres/Redis
  split) -- see the `architecture-containers-relay` node for that; this node
  cites it as the container that implements the behavior described here
  rather than re-describing its structure.
- **The interface(s) this capability is exposed through** -- no interface node
  for the relay's WebSocket/HTTP event-submission surface exists in the corpus
  yet; that is a gap, not a decision that none is needed.
- **The step-by-step path a stream message takes from submission to delivery**
  -- see `architecture-flows-event-ingestion` (submission through storage) and
  `architecture-flows-live-fanout` (storage through live delivery) for that;
  this node states the capability's rules and constraints, not the flow's
  ordered steps, trust boundaries, or rollback behavior.
- **How the relay is operated** (deployment, monitoring, incident response) --
  out of scope for a capability node.
- **The stream *channel* itself** as a channel-management capability (creating
  one, its visibility/membership rules) -- that is a distinct, narrower
  capability than the messaging behavior described here, and as of this
  writing has its own not-yet-merged corpus draft (PR #1912). This node does
  not reference it: `AGENTS.md`'s rule that a relationship target must already
  be merged on `origin/launchpad` was checked directly
  (`git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus/capabilities`
  returns nothing -- no `capabilities`-typed node of any kind is merged yet),
  so no `capabilities`-typed sibling is a valid relationship target right now.
- **The generic messaging capability** that would cover message kinds shared
  across channel types (edits, pinning, bookmarking, scheduling, reminders,
  diffs, and forum/DM messaging) -- this node is scoped to the behavior
  specific to a stream-type channel's own message kind, `KIND_STREAM_MESSAGE`
  (9), not the whole messaging surface. A generic `message` capability node,
  if one is later drafted, owns that broader ground; this node does not
  attempt to.
- **`KIND_STREAM_MESSAGE_V2`'s (40002) own wire/payload format**, beyond
  noting that every code path checked treats it identically to kind:9 for
  scope, channel-scoping, and feed inclusion. Whether the two carry a
  different content/tag shape for richer message formats was not
  investigated for this node.

## Relationships

- references: `architecture-flows-event-ingestion` -- the flow a stream
  message travels from wire submission through validation and storage.
- references: `architecture-flows-live-fanout` -- the flow that delivers a
  stored stream message live to the channel's other subscribers.
- references: `architecture-containers-relay` -- the container implementing
  the ingest validation, thread-metadata computation, and channel-window
  query described above.
- No `capabilities`-typed relationship is declared. Checked directly against
  `origin/launchpad`'s corpus tree at the recorded revision: no `capabilities`
  node of any kind is merged there yet (`stream-channel.md`, the nearest
  candidate sibling, is still open as PR #1912), so there is nothing in that
  surface to point at. This is the moment named in `AGENTS.md` where the
  edges are being added in a later pass, not an oversight.

## Scope and omissions

**This node covers** the capability a stream-type channel member has to post
a linear-timeline message (`KIND_STREAM_MESSAGE`, kind:9): the link-preview
validation rule specific to this kind, the mandatory channel (`h`-tag)
scoping and `MessagesWrite` scope requirement, the NIP-10 reply/broadcast rule
that decides whether a reply rejoins the channel's main timeline, this
capability's appearance in the `@`-mentions and activity feeds, its identical
treatment alongside `KIND_STREAM_MESSAGE_V2` everywhere checked, and the
narrow agent-shutdown convention layered on the same kind.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| How the relay is built (containers, components, technology) | `architecture-containers-relay` |
| The step-by-step ingestion and live-fanout flows | `architecture-flows-event-ingestion`, `architecture-flows-live-fanout` |
| The boundary contract (WebSocket/HTTP surface) this capability is exposed through | not yet drafted in the corpus |
| The stream channel type itself as a channel-management capability | not yet merged (PR #1912) |
| Generic/cross-channel-type messaging (edits, pinning, bookmarking, scheduling, reminders, diffs, forum/DM messages) | not yet drafted in the corpus |
| `KIND_STREAM_MESSAGE_V2`'s own payload/wire format, beyond its identical scope/channel-scope/feed treatment | not investigated for this node |
| How the running relay is operated | the `operations` corpus surface |

**Expected but not verified when this node was written:**
- Whether `KIND_STREAM_MESSAGE` and `KIND_STREAM_MESSAGE_V2` differ in their
  actual message payload/content shape (e.g. richer formatting, attachments)
  was not investigated -- only that every ingest/feed code path treats the two
  kinds identically was confirmed.
- Desktop/mobile client behavior for composing, rendering, or reacting to a
  stream message was not inspected; this node is scoped to the relay-side
  capability contract, not client UI behavior.
- Whether any interface node (a future corpus node for the relay's
  WebSocket/HTTP event-submission surface) will supersede part of this node's
  citations once drafted.
