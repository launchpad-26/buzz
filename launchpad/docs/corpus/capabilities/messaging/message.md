---
id: capabilities-messaging-message
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
  - statement: "A message is a Nostr event of kind 9 (KIND_STREAM_MESSAGE, the NIP-29 group chat message kind) or kind 40002 (KIND_STREAM_MESSAGE_V2); both constants are defined together under the 'Stream messaging' section of the kind registry, and both are declared valid, storable timeline event kinds."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs:476-481"
  - statement: "Kind 9 and kind 40002 are treated as the same 'message' concept by consuming code, not as a superseded/superseding pair: buzz-db's feed queries list them side by side in every kind filter that selects timeline messages, and buzz-acp's context-fetching code queries both kinds together in a single filter when assembling thread or DM context for an agent."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/feed.rs:622-735"
      - "crates/buzz-acp/src/pool.rs:3258-3264"
      - "crates/buzz-acp/src/pool.rs:3382-3387"
  - statement: "The desktop client's own kind registry defines both KIND_STREAM_MESSAGE (9) and KIND_STREAM_MESSAGE_V2 (40002) and groups them together wherever it enumerates timeline-content kinds, confirming the same dual-kind treatment holds on the client side, not only in relay-side Rust code."
    entry_class: FACT
    evidence:
      - "desktop/src/shared/constants/kinds.ts:4-20"
      - "desktop/src/shared/constants/kinds.ts:84-133"
  - statement: "buzz-sdk's build_message function is the canonical way a client constructs a message event: it validates content against a 64 KiB limit, tags the event with an `h` tag naming the channel's UUID (channel scoping), optionally adds NIP-10 `e`-tag thread markers, adds deduplicated `p`-tag mentions (capped by buzz-sdk::mentions::MENTION_CAP), an optional `broadcast` tag, and optional `imeta` media tags -- and it builds the event as `Kind::Custom(9)`, i.e. KIND_STREAM_MESSAGE."
    entry_class: FACT
    evidence:
      - "crates/buzz-sdk/src/builders.rs:224-245"
  - statement: "A message's channel scope is carried by an `h` tag naming the channel's UUID, not an `e` tag -- `e` tags are reserved for NIP-10 thread/reply relationships within a channel."
    entry_class: FACT
    evidence:
      - "crates/buzz-sdk/src/builders.rs:224-245"
      - "AGENTS.md:159-163"
  - statement: "Threading uses NIP-10 `e`-tag markers via the `ThreadRef` struct: a direct reply (root event equals parent event) emits a single `[\"e\", root, \"\", \"reply\"]` tag, and a nested reply emits both `[\"e\", root, \"\", \"root\"]` and `[\"e\", parent, \"\", \"reply\"]`."
    entry_class: FACT
    evidence:
      - "crates/buzz-sdk/src/lib.rs:24-33"
      - "crates/buzz-sdk/src/builders.rs:178-190"
  - statement: "A reply increments `reply_count` and `last_reply_at` on its immediate parent event, and increments `descendant_count` on the thread root event; both counters are materialized columns updated as part of the same write path that inserts the reply, and a crash between the insert and the counter update is explicitly called out as a case the code must not leave inconsistent."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/thread.rs:49-113"
      - "crates/buzz-db/src/thread.rs:209-241"
      - "crates/buzz-db/src/event.rs:1268-1281"
  - statement: "VISION_PROJECTS.md's own capability status table lists 'Channels, forums, DMs, canvases' as '✅ Ships today', the maturity marker for messaging as a product capability."
    entry_class: FACT
    evidence:
      - "VISION_PROJECTS.md:249"
  - statement: "Root AGENTS.md states that thread counters (`reply_count` and `descendant_count`) are materialized on thread root events and that any code inserting replies must update these counters, directing an implementer to the existing reply-handler pattern rather than reinventing it."
    entry_class: FACT
    evidence:
      - "AGENTS.md:224-226"
  - statement: "The node.schema.json `type` enum lists `capabilities` as its own dedicated corpus surface, and at the time this node was drafted no other document existed anywhere under `launchpad/docs/corpus/capabilities/` -- confirmed by listing the merge target's corpus tree -- so this is the first capability-shaped node and there are no already-merged messaging-capability siblings (attachments, direct-message, gift-wrap, mention, message-edit, reaction, reply, stream-message, thread-counters, thread) to declare relationships toward."
    entry_class: FACT
    evidence:
      - "git_ls_tree(ref='origin/launchpad', path='launchpad/docs/corpus') -> no path under launchpad/docs/corpus/capabilities/, run 2026-08-31"
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "architecture-flows-live-fanout and architecture-flows-event-ingestion are corpus nodes already merged to origin/launchpad that respectively document the post-commit delivery pipeline and the shared ingest/validation pipeline a message event travels through; this node references both rather than re-describing their content."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/flows/live-fanout.md"
      - "launchpad/docs/corpus/architecture/flows/event-ingestion.md"
relationships:
  - type: references
    target: architecture-flows-event-ingestion
  - type: references
    target: architecture-flows-live-fanout
---

# Message: capability

Buzz lets a channel member (human or agent) send a message that every other member
of that channel sees, in order, as part of a persistent, replyable timeline. A
message is the atomic unit of conversation in Buzz: it carries text content, belongs
to exactly one channel, may optionally reply into an existing thread, may mention
other participants, and may carry attached media. Every higher-level messaging
concern in this repository -- direct messages, threads, replies, reactions, edits,
mentions, attachments -- is a variation or an annotation on this one underlying
concept, not a separate kind of thing.

## What a message fundamentally is

A message is a signed Nostr event, of kind 9 (`KIND_STREAM_MESSAGE`) or kind 40002
(`KIND_STREAM_MESSAGE_V2`). The two kinds are not a legacy/current pair -- consuming
code (the relay's feed queries, and the agent harness's own context-fetching code)
queries both together, in the same filter, whenever it wants "the messages in this
channel". The client-side kind registry does the same. `buzz-sdk`'s `build_message`,
the canonical message-construction function, builds the event as kind 9.

A message is scoped to a channel through an `h` tag naming the channel's UUID --
not an `e` tag, which this repository reserves for NIP-10 thread/reply
relationships. This is the same `h`-tag-for-scope convention NIP-29 uses for every
kind of event inside a channel, not a rule invented for messages specifically.

A message's content is capped at 64 KiB. Beyond the required channel-scoping `h`
tag, a message may carry:

- **Thread/reply markers** (`e` tags, NIP-10 style) -- a direct reply to a message
  emits one `e` tag marked `"reply"`; a reply nested inside an existing thread emits
  two -- one marked `"root"`, one marked `"reply"`.
- **Mentions** (`p` tags) -- deduplicated, capped, one per mentioned participant.
- **A `broadcast` tag** -- an explicit flag distinct from normal channel delivery.
- **`imeta` tags** -- attached media metadata.

Sending a reply is not just tagging: it also updates materialized counters.
`reply_count` (plus `last_reply_at`) is incremented on the message's immediate
parent, and `descendant_count` is incremented on the thread's root message, in the
same write path that inserts the reply -- a pattern the root repository guide
calls out explicitly so it is not silently dropped by new reply-handling code.

## Maturity

Shipped. VISION_PROJECTS.md's own capability status table marks "Channels, forums,
DMs, canvases" -- the product-level capability messaging is part of -- as
"Ships today", and the mechanics above (kind constants, the SDK builder, the
counter-update write path) are working, merged code, not a design in progress.

## Boundary

This node does not describe:

- **How a message is built and delivered end to end at the systems level** -- the
  relay's shared ingest/validation pipeline and its post-commit fan-out pipeline
  are their own architecture nodes (`architecture-flows-event-ingestion`,
  `architecture-flows-live-fanout`), referenced here rather than re-described.
- **The interface(s) a client uses to send or fetch a message** -- `buzz-cli`'s
  message subcommands and the relay's WebSocket/HTTP surfaces are interface-shaped
  content; no interface node exists yet for either at the time this node was
  written.
- **The specific, deeper concerns each sibling messaging-capability document owns**:
  direct messages, gift-wrapped (encrypted) messages, threads and thread counters as
  their own concept, replies as their own concept, reactions, edits, mentions as
  their own concept, and attachments. This node states what a message fundamentally
  is -- a Nostr event, channel-scoped by an `h` tag, capped at 64 KiB, optionally
  threaded and mentioned -- and does not re-derive the depth those sibling documents
  own. None of those sibling documents are merged to `origin/launchpad` at the time
  this node was written, so none are declared as relationship targets; the first of
  them to merge is the moment to add the corresponding edge back to this node.
- **How the running system operates message delivery at scale** (queueing,
  backpressure, cross-node fan-out) -- that is `architecture-flows-live-fanout`'s
  territory, not this node's.

## Relationships

- references: `architecture-flows-event-ingestion` -- the shared validation/storage
  pipeline a message event (like any persistent-kind event) travels through on
  submission.
- references: `architecture-flows-live-fanout` -- the post-commit delivery pipeline
  that fans a stored message out to other channel members in real time.

No sibling messaging-capability node (direct-message, thread, reply, reaction,
message-edit, mention, attachments, gift-wrap, stream-message, thread-counters) is
declared as a relationship target: none exists in `origin/launchpad`'s corpus tree
at the time this node was written (confirmed by listing that tree), so none is a
valid target per `AGENTS.md`'s own rule that a relationship may only name an
already-merged node.

## Scope and omissions

**This node covers** what a message fundamentally is in Buzz: the event kinds that
represent one (9 and 40002, treated as equivalent by consuming code), the `h`-tag
channel-scoping mechanism, the optional NIP-10 `e`-tag thread markers, `p`-tag
mentions, the `broadcast` tag, `imeta` media tags, the 64 KiB content cap, the
reply-count/descendant-count materialized-counter update that accompanies a reply,
and messaging's current product maturity.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| End-to-end delivery mechanics (ingest, fan-out, backpressure) | `architecture-flows-event-ingestion`, `architecture-flows-live-fanout` |
| The CLI/HTTP/WebSocket interface(s) used to send or fetch a message | An interface node, not yet drafted |
| Direct messages as their own concept | A `capabilities/messaging/direct-message.md` node, not yet drafted |
| Gift-wrapped (encrypted) messages | A `capabilities/messaging/gift-wrap.md` node, not yet drafted |
| Threads and thread counters as their own concept | `capabilities/messaging/thread.md`, `capabilities/messaging/thread-counters.md`, not yet drafted |
| Replies as their own concept | `capabilities/messaging/reply.md`, not yet drafted |
| Reactions | `capabilities/messaging/reaction.md`, not yet drafted |
| Message edits | `capabilities/messaging/message-edit.md`, not yet drafted |
| Mentions as their own concept | `capabilities/messaging/mention.md`, not yet drafted |
| Attachments | `capabilities/messaging/attachments.md`, not yet drafted |
| Stream messages (kind 9 as agent-shutdown convention, and any other non-chat use of kind 9/40002) | `capabilities/messaging/stream-message.md`, not yet drafted |

**Expected but not verified when this node was written:**

- **Whether kind 40002 is ever emitted by any current builder was not established.**
  `build_message` (the SDK's canonical builder) always constructs kind 9; kind 40002
  is queried for and handled everywhere kind 9 is, and the desktop client's kind
  registry documents it as "a valid timeline-content kind", but no code path that
  *constructs* a kind:40002 event was located while drafting this node. This is
  named here as a gap rather than a claim in either direction.
- **The relay-side validation rules specific to message content** (e.g. any
  content-shape checks inside `ingest_event` beyond the size cap enforced by
  `build_message` client-side) were not independently traced for this node; they
  belong to `architecture-flows-event-ingestion` if not already covered there.
