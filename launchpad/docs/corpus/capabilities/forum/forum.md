---
id: capabilities-forum-forum
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
  - statement: "The forum capability is backed by three dedicated Nostr event kinds in a reserved 45000-45999 range: KIND_FORUM_POST (45001, doc comment 'A forum post (thread root)'), KIND_FORUM_VOTE (45002, 'A vote on a forum post'), and KIND_FORUM_COMMENT (45003, 'A comment reply on a forum post'); a code comment at the top of the block notes an earlier V1 used the addressable range 30001-30003 and calls that choice 'wrong'."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs:547-554"
  - statement: "buzz-core defines a ChannelType enum with four variants -- Stream ('Linear message stream (the default)'), Forum ('Threaded forum-style discussion'), Dm ('Direct message conversation'), Workflow ('Internal workflow execution channel') -- whose as_str()/FromStr round-trip the literal string 'forum', and whose doc comment on as_str states the string 'matches DB enum and Nostr tags'."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/channel.rs:57-99"
  - statement: "The Postgres schema declares channel_type as an ENUM with exactly the values 'stream', 'forum', 'dm', 'workflow', matching buzz-core's ChannelType::as_str values one-to-one."
    entry_class: FACT
    evidence:
      - "migrations/0001_initial_schema.sql:28"
  - statement: "When the relay builds the kind:39000 channel-metadata event for a channel, it pushes a `t` tag carrying the channel's channel_type value, with the code comment 'Channel type tag so clients can distinguish stream/forum/dm without inference' -- meaning a forum channel is identified to clients by this `t` tag being literally \"forum\", not by a separate kind or a client-side heuristic."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/side_effects.rs:1099-1100"
  - statement: "The relay enforces that a kind:45002 vote event may only target a kind:45001 forum post or a kind:45003 forum comment: validate_forum_vote_target loads the event named by the vote's `e` tag and returns the error 'vote target must be a forum post or comment' when the target's kind is neither KIND_FORUM_POST nor KIND_FORUM_COMMENT; this validator is wired into the main ingest path when the incoming event's kind equals KIND_FORUM_VOTE."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:1000-1036"
  - statement: "A relay unit test, channel_scoped_content_kinds_require_h_tags, asserts that KIND_FORUM_POST, KIND_FORUM_VOTE and KIND_FORUM_COMMENT all require an `h` (channel-scope) tag via requires_h_channel_scope, in the same list as KIND_STREAM_MESSAGE and KIND_CANVAS -- forum events are channel-scoped exactly like stream messages, not a globally-scoped kind family."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs:1172-1234"
  - statement: "There is no dedicated forum_posts, forum_comments or forum_votes table in the SQL migrations; forum content is stored as ordinary rows in the generic Nostr events table, distinguished only by kind, and reply/thread bookkeeping (parent_event_id, root_event_id, depth, reply_count, descendant_count) is carried by the channel-type-agnostic thread_metadata table used for every threaded kind, not a forum-specific structure."
    entry_class: FACT
    evidence:
      - "migrations/0001_initial_schema.sql:512-528"
  - statement: "buzz-cli exposes no standalone `forum` subcommand tree. Forum posts and comments are sent through `buzz messages send` by passing `--kind 45001` (post) or `--kind 45003` with a required `--reply-to` (comment), dispatching to buzz_sdk::build_forum_post / buzz_sdk::build_forum_comment respectively, and any other kind value is rejected with 'is not supported (use 9, 45001, or 45003)'."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/commands/messages.rs:646-676"
  - statement: "buzz-cli's `messages vote` subcommand ('Upvote or downvote a forum post') takes --event <64-char hex> and --direction up|down, and its own ChannelType clap enum for `channels create --type` only offers the values 'stream' and 'forum' (dm and workflow are not user-creatable through this command)."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/lib.rs:102-107"
      - "crates/buzz-cli/src/lib.rs:516-524"
  - statement: "cmd_create_channel in buzz-cli's channels.rs rejects any --type value other than the literal strings 'stream' or 'forum' with a usage error, then maps 'forum' to buzz_sdk::ChannelKind::Forum before submitting the channel-creation event."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/commands/channels.rs:282-320"
  - statement: "The desktop app has a dedicated `desktop/src/features/forum/` module: hooks.ts exposes useForumPostsQuery, useForumThreadQuery, useCreateForumPostMutation, useCreateForumReplyMutation, useDeleteForumPostMutation and useDeleteForumReplyMutation, backed by a 15-second focused refetch interval for the post list and a 10-second interval for an open thread; the `ui/` subfolder holds ForumView.tsx (the list view), ForumPostCard.tsx (one post card), ForumThreadPanel.tsx (a post's flat-reply detail view), and a shared ForumComposer.tsx used for both new posts and replies."
    entry_class: FACT
    evidence:
      - "desktop/src/features/forum/hooks.ts:1-40"
      - "desktop/src/features/forum/ui/ForumView.tsx:1-40"
  - statement: "VISION.md's Surfaces table lists Forum with the model 'Async long-form threads. Culture.' and a 'Zero' default-notification level, and a following bullet describes it as 'Discourse-like, slow. Post -> flat replies. Zero-notification default,' explicitly contrasted with Stream's 'Slack-like, fast. Mandatory topics -> sub-replies.'"
    entry_class: FACT
    evidence:
      - "VISION.md:19"
      - "VISION.md:27-28"
  - statement: "VISION.md's platform-status table marks the desktop Tauri client as already shipping the Forum surface among others ('Stream, Home, Forum, DMs, Agents, Workflows, ...'), while the Flutter mobile client's forum support is marked in active development rather than shipped."
    entry_class: FACT
    evidence:
      - "VISION.md:223"
      - "VISION.md:232"
  - statement: "The desktop-shipped forum UI's list-then-thread-then-shared-composer shape (ForumView listing ForumPostCard items, opening into ForumThreadPanel, both using ForumComposer) matches VISION.md's stated 'Post -> flat replies' interaction model."
    entry_class: INFERENCE
    evidence:
      - "desktop/src/features/forum/ui/ForumView.tsx:1-40"
      - "VISION.md:27-28"
    confidence: 0.85
  - statement: "VISION_PROJECTS.md describes a second, distinct use of the word 'forum': the Projects/Issues feature renders NIP-34 kind:1621 bug-report events and NIP-22 kind:1111 threaded comments 'through Buzz's forum surface,' and design discussions/RFCs use 'the forum's long-form async surface' -- these are different event kinds (1621/1111) from the native forum capability's own KIND_FORUM_POST/KIND_FORUM_COMMENT (45001/45003), so 'forum' names both a capability with its own kinds and a rendering surface other capabilities can reuse."
    entry_class: FACT
    evidence:
      - "VISION_PROJECTS.md:185-189"
  - statement: "Issue #743's Definition of Done requires exactly one hand-authored canonical corpus document at launchpad/docs/corpus/capabilities/forum/forum.md, schema-valid front matter, one independently maintainable knowledge node, every substantive claim traceable to code/tests/specs/decisions/migrations or attributed evidence, links to relevant implementation/verification/specification/neighboring nodes without duplicating their content, checked against the recorded repository revision, and a passing corpus validation."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#743 definition of done"
  - statement: "Sibling issues #740, #741 and #742 each target a document at launchpad/docs/corpus/capabilities/forum/, titled 'document capabilities/forum/forum-comment.md', 'document capabilities/forum/forum-post.md' and 'document capabilities/forum/forum-thread.md' respectively, and issue #729 targets 'document capabilities/channels/forum-channel.md' -- so post, comment and thread depth, and the forum channel type itself, are each a separate task's document, not this one's to duplicate."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#740, #741, #742, #729 issue titles (read directly via gh issue view)"
---

# Forum: capability

Forum is Buzz's async, long-form discussion surface: a channel whose members
post standalone topics (forum posts) that others reply to with flat comments
and can upvote or downvote, distinct from the fast, linear Stream surface a
community also has. A user or agent that wants to start a slower-paced,
Discourse-like discussion -- a design proposal, an RFC, a "culture" topic that
does not need real-time back-and-forth -- creates or uses a channel of type
`forum` rather than `stream`, and everyone in that channel sees the same
post-then-flat-replies shape with a zero-notification default.

## Maturity

**Shipped**, on both the relay and the desktop client. The relay recognizes
and enforces the three forum event kinds and the `forum` channel type
end-to-end (`crates/buzz-core/src/kind.rs:547-554`,
`crates/buzz-core/src/channel.rs:57-99`,
`crates/buzz-relay/src/handlers/ingest.rs:1000-1036`), `buzz-cli` exposes it
through `messages send --kind 45001/45003`, `messages vote` and
`channels create --type forum` (`crates/buzz-cli/src/commands/messages.rs:646-676`,
`crates/buzz-cli/src/commands/channels.rs:282-320`), and the desktop app ships
a dedicated `desktop/src/features/forum/` feature module
(`desktop/src/features/forum/hooks.ts`, `desktop/src/features/forum/ui/`).
VISION.md's own platform-status table marks the desktop Tauri client as
already shipping Forum among its surfaces (`VISION.md:223`); the Flutter
mobile client's forum support is separately marked "in active development,"
i.e. not yet shipped there (`VISION.md:232`).

## Boundary

This node does not describe:

- **How a forum post, comment, or vote is individually shaped and validated**
  -- field-by-field kind structure, tagging rules, and lifecycle for each of
  the three event kinds are the forum-post (#741), forum-comment (#740), and
  the vote path within them; a future thread-level node (#742) covers the
  reply/threading behavior in depth. This node states only that the three
  kinds exist and how they relate to each other, not their full contracts.
- **The `forum` channel type as a channel-creation and metadata concept in
  its own right** -- channel visibility, membership, and the kind:39000
  metadata/`t`-tag mechanics belong to the forum-channel node (#729). This
  node cites that mechanism only to explain how a client tells a forum
  channel apart from a stream channel.
- **How the capability is built** -- no component diagram, deployment
  topology, or technology choice is this node's subject matter; the relay
  container node (`architecture-containers-relay`, not yet carrying a
  `capabilities`-facing relationship at this revision) is where that lives.
- **The interface(s) the capability is exposed through** -- `buzz-cli`'s
  exact subcommand contracts and the desktop app's API client
  (`desktop/src/shared/api/forum.ts`) are cited here as evidence the
  capability is reachable, not documented as interfaces in their own right.
- **The step-by-step flow through a forum interaction** (compose a post,
  open a thread, reply, vote) -- that narrative belongs to a flow-shaped
  node, not yet drafted in this corpus.
- **The Projects/Issues feature's reuse of the word "forum"** -- VISION_
  PROJECTS.md describes NIP-34 issues and NIP-22 comments as "rendered
  through Buzz's forum surface," but those are different event kinds
  (1621/1111) from this capability's own 45001/45002/45003. That is a
  separate reuse of the forum *rendering surface*, not part of this
  capability's own event-kind contract, and is not detailed further here.

## Relationships

Declared: none. `origin/launchpad`'s corpus tree at the recorded revision
carries no other `capabilities`-typed node and no architecture, interface, or
flow node yet exists for forum specifically to reference -- the sibling
documents this node explicitly defers to (forum-post #741, forum-comment
#740, forum-thread #742, forum-channel #729) are being authored in the same
batch and are not yet merged, so per `AGENTS.md`'s own rule a relationship
naming any of their eventual ids would resolve in this worktree but break in
CI on `launchpad`. Once those nodes merge, this node should gain `references`
edges to each, plus `references` toward an architecture node for
`buzz-relay` if/when one carries a matching id.

## Scope and omissions

**This node covers** what the forum capability fundamentally is (a channel
type plus three purpose-built Nostr event kinds for posts, comments, and
votes), its product-level framing per VISION.md, how a client distinguishes
a forum channel from a stream/dm/workflow channel, the relay-side invariant
tying votes to posts/comments, where the capability is reachable today
(`buzz-cli`, the desktop app), its shipped-vs-in-progress status by platform,
and how it relates to (without duplicating) the post/comment/thread/channel
documents this same batch is producing.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Forum post event shape, fields, lifecycle | #741 (forum-post) |
| Forum comment event shape, fields, lifecycle | #740 (forum-comment) |
| Threading/reply behavior in depth | #742 (forum-thread) |
| The `forum` channel type as its own concept (creation, visibility, membership, metadata) | #729 (forum-channel) |
| How `buzz-relay` is built as a container | `architecture-containers-relay` |
| The step-by-step interaction flow through a forum post | not yet drafted (flow-shaped node) |
| The mobile (Flutter) forum surface's current implementation, beyond VISION.md's own "in active development" status marker | not established from source read for this node |

**Expected but not verified when this node was written:**

- **Mobile (Flutter) forum implementation was not opened.** Only VISION.md's
  own status marker ("in active development") was read; no Dart source under
  `mobile/lib/features/` was inspected for this node, so no claim is made
  about what mobile forum support currently does or does not do.
- **`desktop/src/shared/api/forum.ts` was located but not opened in depth** --
  its existence is cited as evidence the desktop app has a forum API client
  layer, not as a source for any claim about its contents.
- **The relay's `ChannelKind` / `buzz_sdk::ChannelKind::Forum` mapping used
  by `buzz-cli` was read only at its call sites in `channels.rs` and
  `messages.rs`, not inside `buzz-sdk` itself** -- this node makes no claim
  about `buzz-sdk`'s own internal representation beyond the enum variant name
  observed at the call site.
