---
id: capabilities-messaging-reply
type: capabilities
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5."
    entry_class: FACT
    evidence:
      - "commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
  - statement: "`buzz-sdk`'s `ThreadRef` type is the shared NIP-10 reply construct: it carries a `root_event_id` and a `parent_event_id`, and its own doc comment states the two shapes it produces -- a direct reply (root == parent) emits a single `[\"e\", root, \"\", \"reply\"]` tag, and a nested reply (root != parent) emits both `[\"e\", root, \"\", \"root\"]` and `[\"e\", parent, \"\", \"reply\"]`."
    entry_class: FACT
    evidence:
      - "crates/buzz-sdk/src/lib.rs"
  - statement: "`thread_tags()` in `buzz-sdk` implements exactly that branching -- comparing `thread_ref.root_event_id` against `thread_ref.parent_event_id` and pushing one or two `e` tags accordingly -- and is the single function every reply-capable builder calls to attach thread markers."
    entry_class: FACT
    evidence:
      - "crates/buzz-sdk/src/builders.rs"
  - statement: "`build_message` (kind 9, channel stream messages) takes `thread_ref: Option<&ThreadRef>` and calls `thread_tags()` only when a reply context is supplied, so an ordinary top-level message carries no `e` tag at all."
    entry_class: FACT
    evidence:
      - "crates/buzz-sdk/src/builders.rs"
  - statement: "`build_forum_comment` (kind 45003, forum replies) takes a required `thread_ref: &ThreadRef` -- unlike channel messages, a forum comment cannot be built without a reply target, and `build_forum_post` (kind 45001, the forum thread root) takes no thread reference at all."
    entry_class: FACT
    evidence:
      - "crates/buzz-sdk/src/builders.rs"
  - statement: "`build_note` (kind 1, NIP-01 global text notes) implements a deliberately simpler reply model than `ThreadRef`: it accepts a single optional `reply_to_event_id` and emits one `[\"e\", id, \"\", \"reply\"]` tag with no root/parent distinction, and its own doc comment states this is intentional -- full NIP-10 root+reply+p-tag threading is deferred for this event kind."
    entry_class: FACT
    evidence:
      - "crates/buzz-sdk/src/builders.rs"
  - statement: "`buzz-cli`'s `messages.rs` resolves a reply's thread root server-side before building the event: `find_root_from_tags` parses a fetched parent event's `e` tags for NIP-10 `root`/`reply` markers (preferring an explicit `root` marker, falling back to a `reply` marker when the parent itself has no root -- i.e. the parent is top-level and is therefore the root), and `resolve_thread_ref` queries the relay for the parent event by id and constructs a `ThreadRef` from that result, so a CLI-sent reply threads correctly even for a multi-hop nested reply the caller never inspected directly."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/commands/messages.rs"
  - statement: "`cmd_send_message`'s `SendMessageParams.reply_to` is a single optional immediate-parent event id (validated as 64 hex chars via `validate_hex64`); when present it is resolved to a full `ThreadRef` via `resolve_thread_ref` before dispatch, and sending a kind 45003 forum comment without `reply_to` is rejected with a `CliError::Usage` naming `--reply-to` as required, while kind 9 channel messages and kind 45001 forum posts both accept it as optional."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/commands/messages.rs"
  - statement: "The desktop app mirrors the same NIP-10 tag shape client-side rather than depending on a round trip: `threading.ts`'s `buildReplyTags(channelId, authorPubkey, parentEventId, rootEventId, mentionPubkeys)` emits `[\"e\", rootEventId, \"\", \"reply\"]` alone when `parentEventId === rootEventId`, and both a `\"root\"`-marked and a `\"reply\"`-marked `e` tag otherwise -- the same branch `thread_tags()` implements in Rust -- and also adds `[\"p\", authorPubkey]` plus per-mention `p` tags and the channel's `[\"h\", channelId]` tag in the same call."
    entry_class: FACT
    evidence:
      - "desktop/src/features/messages/lib/threading.ts"
  - statement: "`threading.ts`'s `resolveReplyRootId(parentEventId, events)` finds the parent message in the already-loaded local message list and reads its own thread reference (`getThreadReference`) to find the root the parent itself replied to, falling back to the parent's own id when the parent carries no thread reference (i.e. it is top-level) -- the desktop-local equivalent of the CLI's relay-side `find_root_from_tags`/`resolve_thread_ref`, avoiding a network round trip when the parent is already in memory."
    entry_class: FACT
    evidence:
      - "desktop/src/features/messages/lib/threading.ts"
  - statement: "`desktop/src/features/messages/hooks.ts` calls `buildReplyTags` in two places -- once to construct the tags of an optimistic local echo (`createOptimisticMessage`, called with a `parentEventId`) and once to construct the tags of the event actually submitted to the relay -- both resolving the root via `resolveReplyRootId` against the same in-memory message cache, so the optimistic and submitted events carry identical thread tags."
    entry_class: FACT
    evidence:
      - "desktop/src/features/messages/hooks.ts"
  - statement: "The desktop reply entry point is a per-message \"Reply\" button in `MessageActionBar.tsx`, rendered only when an `onReply` callback prop is supplied, which invokes `onReply(message)` with the full message the reply targets; `MessageComposer.tsx` accepts the resulting `replyTarget` and uses it to change the composer's placeholder text (`Reply to {author} in #{channelName}`) and to render `ComposerReplyEditBanner` with `replyTarget` -- a banner showing `Replying to {author}` plus a truncated quoted excerpt of the target message's body, with a cancel control that clears the reply target."
    entry_class: FACT
    evidence:
      - "desktop/src/features/messages/ui/MessageActionBar.tsx"
      - "desktop/src/features/messages/ui/MessageComposer.tsx"
      - "desktop/src/features/messages/ui/ComposerReplyEditBanner.tsx"
  - statement: "`ComposerReplyEditBanner`'s own doc comment states that edit takes precedence over reply when both a `replyTarget` and `isEditing` are present, matching the composer's own `editTarget ? … : replyTarget ? …` ordering -- a reply cannot be composed while an edit is in progress on the same composer instance."
    entry_class: FACT
    evidence:
      - "desktop/src/features/messages/ui/ComposerReplyEditBanner.tsx"
  - statement: "The mobile Flutter app exposes an equivalent reply entry point: `message_actions.dart` defines a promoted quick action labeled `Reply` (icon `LucideIcons.messageSquareReply`) among the dominant per-message mobile actions, and the file's own comment states its context menu changes \"when the message is a reply\"."
    entry_class: FACT
    evidence:
      - "mobile/lib/features/channels/message_actions.dart"
  - statement: "Both `buzz-sdk`'s builder tests and `buzz-cli`'s tag-parsing tests exercise the direct-vs-nested reply distinction and defensive fallbacks: `message_direct_reply` and `message_nested_reply` in `builders.rs` assert the one-tag and two-tag shapes respectively for kind 9 messages, `build_note_with_reply` asserts the flat single-tag shape for kind 1 notes, and `messages.rs`'s own tests (`root_marker_wins_over_reply_marker`, `reply_only_falls_back_to_reply_target`, `malformed_root_does_not_shadow_valid_reply`) assert that a parent's explicit `root` marker wins over its `reply` marker, that a reply-only parent falls back to treating the reply target as root, and that a malformed `root` marker does not block falling back to a valid `reply` marker."
    entry_class: FACT
    evidence:
      - "crates/buzz-sdk/src/builders.rs"
      - "crates/buzz-cli/src/commands/messages.rs"
  - statement: "The relay's shared event-ingestion pipeline (documented by the merged corpus node `architecture-flows-event-ingestion`) persists a non-replaceable event's `e`-tag reply/root markers as NIP-10 thread metadata inside the same Postgres transaction as the event insert, incrementing `reply_count` on the parent and root rows -- this is the server-side counterpart that gives a reply its durable position in a thread, but the counters themselves (`reply_count`, `descendant_count`) and the live kind:39005 thread-summary push are a distinct concern this node does not restate, per the *Boundary* section below."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/flows/event-ingestion.md"
      - "crates/buzz-db/src/store/event.rs"
  - statement: "Reply is shipped, not merely designed: it has production builder functions with unit tests (`buzz-sdk`), a CLI code path with its own tests and a required-field validation rule (`buzz-cli`), a wired desktop UI entry point and compose-time quoted preview (`desktop`), and a mobile quick action (`mobile`) -- all inspected directly for this node, none inferred from a status marker alone."
    entry_class: FACT
    evidence:
      - "crates/buzz-sdk/src/builders.rs"
      - "crates/buzz-cli/src/commands/messages.rs"
      - "desktop/src/features/messages/ui/MessageActionBar.tsx"
      - "mobile/lib/features/channels/message_actions.dart"
  - statement: "No dedicated corpus node documenting NIP-10 threading, reply-to-a-message, or thread counters existed under `launchpad/docs/corpus/architecture/**` or anywhere else in the corpus at the time this node was drafted -- the only existing mentions of `reply_count`/thread metadata are inside `architecture-flows-event-ingestion` and `architecture-flows-http-event-submission`, as part of describing the generic ingestion pipeline rather than as their own subject."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/flows/event-ingestion.md"
      - "launchpad/docs/corpus/architecture/flows/http-event-submission.md"
relationships:
  - type: implements
    target: corpus-template-capability
  - type: references
    target: architecture-flows-event-ingestion
  - type: references
    target: architecture-containers-cli
  - type: references
    target: architecture-containers-desktop
---

# Reply: capability

A user or agent can reply to an existing message so the new message carries an
explicit, machine-readable link back to what it responds to. Every reply-capable
surface in Buzz -- the agent-facing CLI, the desktop app, and the mobile app --
lets its author name a specific prior message as the thing being answered, and the
resulting event threads that relationship using NIP-10 `e`-tag markers so any
client (or the relay itself) can reconstruct which message a reply targets without
guessing from ordering or timing alone.

## Maturity

**Shipped.** `buzz-sdk`'s builder functions (`build_message` for kind 9 channel
messages, `build_forum_comment` for kind 45003 forum replies, `build_note` for
kind 1 notes) all construct real NIP-10 `e` tags today, each covered by unit
tests (`message_direct_reply`, `message_nested_reply`, `build_note_with_reply` in
`crates/buzz-sdk/src/builders.rs`). `buzz-cli`'s `messages.rs` resolves the full
thread reference server-side from a bare `--reply-to` parent id, with its own
tests for the marker-precedence and malformed-tag fallback rules. The desktop app
wires a "Reply" action per message (`MessageActionBar.tsx`) into a composer banner
showing a quoted excerpt of the target (`ComposerReplyEditBanner.tsx`), and builds
matching tags client-side (`threading.ts`'s `buildReplyTags`) for both the
optimistic local echo and the submitted event (`hooks.ts`). The mobile app carries
an equivalent "Reply" quick action (`message_actions.dart`). None of this is
behind a flag or described as in-progress in any source this node cites.

## Boundary

This node does not describe:
- **How a reply is built at the container/component level** -- the relay's write
  path, Postgres schema, or Redis fan-out that a reply event travels through once
  submitted. See `architecture-containers-cli`, `architecture-containers-desktop`,
  and `architecture-flows-event-ingestion` for that; this node cites them as the
  realizing architecture rather than restating their content.
- **Thread counters and thread-level state** -- `reply_count`, `descendant_count`,
  and the relay-pushed kind:39005 live-thread-summary event that
  `architecture-flows-event-ingestion` documents are incremented/emitted as a
  *side effect* of a reply being stored. Those are a sibling capability's subject
  matter (thread counters), not this node's -- this node covers how a reply is
  *constructed and sent*, not how the thread it joins keeps its own aggregate
  state.
- **The step-by-step flow one interaction through replying takes** -- the
  request/response sequence across client, relay, and Postgres. No flow node for
  this exists in the corpus yet; when one is drafted, it is the place for that
  sequence, not here.
- **The interface contract (CLI flags, HTTP/WebSocket payload shape) that exposes
  this capability** -- no `interfaces-events`-typed node exists yet in the corpus
  to reference for `buzz-cli`'s `messages send-message --reply-to` or the
  underlying event submission surface; this node names the capability, not the
  boundary contract exposing it.
- **The visual thread-indentation/connector rendering** in the desktop timeline
  (`MessageRow.tsx`'s depth guides, rails, and avatar connectors) -- that is
  thread *visualization*, a different capability from constructing and sending a
  reply, even though both consume the same underlying `e`-tag data.

## Relationships

- implements: `corpus-template-capability` -- this node follows that template's
  required sections (capability statement, maturity, boundary, relationships,
  scope and omissions).
- references: `architecture-flows-event-ingestion` -- the relay-side pipeline
  that persists a reply's `e`-tag markers as thread metadata and increments the
  parent/root counters, once the reply event reaches the relay.
- references: `architecture-containers-cli` -- the container hosting
  `buzz-cli`'s `messages.rs`, where a reply's `--reply-to` parent id is resolved
  into a full `ThreadRef` before the event is built.
- references: `architecture-containers-desktop` -- the container hosting the
  desktop app's reply entry point, composer banner, and client-side tag
  construction.

## Scope and omissions

**This node covers** the reply-to-a-message capability: constructing NIP-10
`e`-tag reply/root markers for a new message (`ThreadRef`, `thread_tags()` in
`buzz-sdk`), the CLI's server-side thread-root resolution from a bare parent id
(`buzz-cli`), the desktop and mobile entry points that let a user or agent
initiate a reply, and the desktop's compose-time quoted preview of the reply
target. It also states, as a `FACT`, that this capability is shipped and cites
the code and tests establishing that.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Thread counters (`reply_count`, `descendant_count`) and the live thread-summary push | a sibling capability node for thread counters, not yet merged at the time this node was drafted |
| The step-by-step flow of a reply from client through relay to storage and fan-out | a future `flow`-typed corpus node, not yet drafted |
| The CLI/HTTP/WebSocket interface contract exposing this capability | a future `interfaces-events`-typed corpus node, not yet drafted |
| How the relay's ingestion pipeline validates and stores any event, replies included | `architecture-flows-event-ingestion` (referenced above) |
| Visual thread indentation/connector rendering in the desktop timeline | out of this node's scope; a rendering concern, not the reply capability itself |

**Expected but not verified when this node was written:**
- **The relay-side HTTP submission path** (`POST /events`) was not independently
  re-checked for reply-specific handling distinct from the WebSocket path that
  `architecture-flows-event-ingestion` documents in depth; both transports are
  stated there to converge on the same shared `ingest_event()` function, and this
  node relies on that existing claim rather than re-deriving it.
- **Whether the forum comment path (`build_forum_comment`, kind 45003) and the
  channel message path (`build_message`, kind 9) present identical UI reply
  affordances on desktop** was not checked -- this node verified the
  `MessageActionBar`/`ComposerReplyEditBanner` path for channel messages and the
  corresponding `buzz-cli` support for both kinds, but not a forum-specific
  desktop reply UI, if a separate one exists.
- **Full mobile reply-composition wiring** (how `message_actions.dart`'s Reply
  action feeds into the mobile composer, analogous to desktop's `replyTarget`)
  was not traced end-to-end; only the entry-point action itself was confirmed.
