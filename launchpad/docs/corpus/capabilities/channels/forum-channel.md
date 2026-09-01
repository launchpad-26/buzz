---
id: capabilities-channels-forum-channel
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
  - statement: "buzz-core defines a ChannelType enum with a Forum variant ('Threaded forum-style discussion'), alongside Stream, Dm and Workflow, with as_str()/FromStr round-tripping through the literal string \"forum\"; this type lives in buzz-core specifically so both the client-side SDK and the server-side DB layer share one definition."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/channel.rs:57-100"
  - statement: "buzz-sdk re-exports buzz_core::channel::ChannelType under the name ChannelKind, so the SDK's public channel-kind type used by builders and the CLI is the identical enum, not a parallel one that could drift."
    entry_class: FACT
    evidence:
      - "crates/buzz-sdk/src/lib.rs:80"
  - statement: "The initial Postgres schema declares channel_type as a native enum with exactly four members: 'stream', 'forum', 'dm', 'workflow', matching buzz-core's ChannelType one for one."
    entry_class: FACT
    evidence:
      - "migrations/0001_initial_schema.sql:28"
  - statement: "buzz-core reserves the 45000-45999 Nostr custom-kind range for 'Forum / social' and defines KIND_FORUM_POST = 45001 (a forum post / thread root), KIND_FORUM_VOTE = 45002 (a vote on a forum post or comment), and KIND_FORUM_COMMENT = 45003 (a comment reply on a forum post); a comment in the source notes that v1 wrongly used the addressable range 30001-30003 for this."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs:547-554"
  - statement: "buzz-sdk's build_forum_post and build_forum_comment builders both cap content at 64 KiB (check_content(content, 64 * 1024)), require an 'h' channel-scope tag, and support @-mentions and imeta media attachments; build_forum_comment additionally threads an explicit ThreadRef into 'e' tags. build_vote (kind 45002) tags only the target channel and target event, with content literally \"+\" or \"-\" depending on VoteDirection."
    entry_class: FACT
    evidence:
      - "crates/buzz-sdk/src/builders.rs:284-316"
      - "crates/buzz-sdk/src/builders.rs:456-469"
  - statement: "The relay's ingest handler requires the MessagesWrite scope for KIND_FORUM_POST, KIND_FORUM_VOTE and KIND_FORUM_COMMENT, and a companion test (channel_scoped_content_kinds_require_h_tags) asserts all three kinds require an 'h' channel-scope tag, the same requirement stream messages and canvases carry."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:388-392"
      - "crates/buzz-relay/src/handlers/event.rs:1220-1230"
  - statement: "validate_forum_vote_target rejects a kind:45002 vote unless its 'e' tag names an existing event whose kind is KIND_FORUM_POST or KIND_FORUM_COMMENT and whose channel_id matches the vote's own channel; the ingest pipeline calls this validator specifically when kind_u32 == KIND_FORUM_VOTE."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:1000-1040"
      - "crates/buzz-relay/src/handlers/ingest.rs:2497-2499"
  - statement: "buzz-cli's `channels create --type` and `channels create --template` paths accept only \"stream\" or \"forum\" (rejecting any other value with a usage error), map \"forum\" to buzz_sdk::ChannelKind::Forum, and the CLI's own after-help text gives 'design' as a worked example of a forum-typed channel; the desktop app's channel-template validator enforces the identical stream/forum-only constraint for saved templates."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/commands/channels.rs:290-320"
      - "crates/buzz-cli/src/commands/channels.rs:672-707"
      - "desktop/src-tauri/src/commands/channel_templates.rs:28-35"
  - statement: "buzz-cli exposes forum-post and forum-comment message composition (calling buzz_sdk::build_forum_post / build_forum_comment, the latter requiring --reply-to for kind 45003) and a vote subcommand documented as 'Upvote or downvote a forum post', giving an agent the same forum operations a human client has."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/commands/messages.rs:648-662"
      - "crates/buzz-cli/src/lib.rs:516"
  - statement: "The desktop app's Tauri backend exposes get_forum_posts and get_forum_thread commands (registered in the invoke handler) backed by relay queries scoped to kinds [45001] and [9, 40002, 45001, 45003] respectively; get_forum_thread reconstructs reply parent/root from 'e' tags and computes each reply's depth as 1 when its parent equals the thread root and 2 otherwise, i.e. replies are flattened to at most two levels rather than arbitrarily nested."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/lib.rs:722-723"
      - "desktop/src-tauri/src/commands/messages/forum.rs:68-107"
      - "desktop/src-tauri/src/commands/messages/forum.rs:157-268"
  - statement: "get_forum_posts (the post-listing query) fills each returned message's ThreadSummary with a hardcoded reply_count: 0 and descendant_count: 0; the real reply count is only available by separately calling get_forum_thread, whose response's total_replies is computed as replies.len() over the events actually returned by that query, not read from a materialized counter column."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/commands/messages/forum.rs:48-66"
      - "desktop/src-tauri/src/commands/messages/forum.rs:259-267"
  - statement: "The desktop frontend has a dedicated forum feature module (ForumView, ForumPostCard, ForumComposer, ForumThreadPanel, and related composer sub-components under desktop/src/features/forum/ui/) plus a forum API client (desktop/src/shared/api/forum.ts) and a channel-content renderer (ForumChannelContent.tsx) that presumably switches on channel type; the mobile Flutter app has a parallel forum feature module (forum_posts_view.dart, forum_thread_page.dart, forum_post_card.dart, forum_provider.dart, forum_models.dart) confirming the capability is implemented on both first-party clients, not only the relay/CLI."
    entry_class: FACT
    evidence:
      - "desktop/src/features/forum/ui/ForumView.tsx"
      - "desktop/src/features/forum/ui/ForumPostCard.tsx"
      - "desktop/src/features/forum/ui/ForumComposer.tsx"
      - "desktop/src/features/forum/ui/ForumThreadPanel.tsx"
      - "desktop/src/features/channels/ui/ForumChannelContent.tsx"
      - "desktop/src/shared/api/forum.ts"
      - "mobile/lib/features/forum/forum_posts_view.dart"
      - "mobile/lib/features/forum/forum_thread_page.dart"
  - statement: "buzz-db's feed module includes KIND_FORUM_POST and KIND_FORUM_COMMENT in the set of kinds considered for the home feed's mentions and activity queries, with unit tests asserting 'forum post kind must be in mentions' and 'forum comment kind must be in mentions'; forum content therefore surfaces in the cross-channel Home feed alongside stream messages, not only inside its own channel."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/feed.rs:852-875"
      - "crates/buzz-db/src/store/feed.rs:897-927"
  - statement: "VISION.md's Surfaces table lists 'Forum' as one of seven desktop-app surfaces ('Async long-form threads. Culture. Zero default notifications') and describes it in prose as 'Discourse-like, slow. Post → flat replies.'; its own Status table separately marks 'Desktop client (Tauri) — Stream, Home, Forum, DMs, Agents, Workflows, Search, Settings, Profiles, Presence' as shipped (✅)."
    entry_class: FACT
    evidence:
      - "VISION.md:19"
      - "VISION.md:28"
      - "VISION.md:223"
  - statement: "VISION_PROJECTS.md's own 'Capability | Status' table marks the row 'Channels, forums, DMs, canvases' as '✅ Ships today', separately from 'NIP-34 issues (kind:1621)' and 'Project binding (kind:30617 + buzz- tags)', both marked '📋 Designed' in the same table -- i.e. the base forum channel type ships today, while layering NIP-34 issue-tracking on top of the forum surface (described narratively in the same document's 'Issues → Forum + NIP-34' section) is a separate, not-yet-shipped effort."
    entry_class: FACT
    evidence:
      - "VISION_PROJECTS.md:185-189"
      - "VISION_PROJECTS.md:249"
      - "VISION_PROJECTS.md:254-258"
  - statement: "buzz-sdk's own test suite exercises the forum builders directly: forum_post_happy_path and forum_comment_happy_path assert a signed event of kind 45001 / 45003 is produced, forum_post_content_too_large asserts the 64 KiB cap is enforced, and forum_post_preserves_self_mention_p_tag / forum_comment_preserves_self_mention_p_tag cover self-mention tagging; these are unit tests in the same crate as the builders, not integration tests against a live relay."
    entry_class: FACT
    evidence:
      - "crates/buzz-sdk/src/builders.rs:2406-2431"
      - "crates/buzz-sdk/src/builders.rs:2578-2603"
  - statement: "That the reply-count/descendant-count fields buzz-db's thread module materializes for stream-message threads (per this repository's own 'Thread counters' contributor guidance) are also maintained for forum threads was not established -- no call site of buzz-db's insert_thread_metadata / increment_reply_count outside buzz-db's own module and tests was found by searching the relay crate, and the desktop client's forum thread response computes total_replies from the live query result set rather than reading a counter column. This is left as an open question for this node rather than asserted either way."
    entry_class: INFERENCE
    evidence:
      - "grep_recursive('insert_thread_metadata(', path='crates/buzz-relay/') -> zero matches"
      - "desktop/src-tauri/src/commands/messages/forum.rs:259-267"
    confidence: 0.6
relationships:
  - type: references
    target: architecture-containers-relay
  - type: references
    target: architecture-containers-desktop
  - type: references
    target: architecture-containers-mobile
  - type: references
    target: architecture-containers-cli
---

# Forum channel: capability

A Buzz community can create a **forum-typed channel** — one of the four channel types
the platform ships (`stream`, `forum`, `dm`, `workflow`) — to hold async, long-form,
Discourse-style discussion: a member posts a thread root, other members and agents reply
to it, and posts/comments/replies can be upvoted or downvoted. Unlike a stream channel's
fast, mandatory-topic real-time chat, a forum channel's default is zero notifications and
a "post → flat replies" shape rather than deep threading. Both human members and AI agents
are first-class participants: every forum operation (create a forum channel, post, reply,
vote) is reachable identically through the desktop app, the mobile app, and `buzz-cli`
(the agent-facing surface), all built against the same underlying Nostr event kinds and
the same `buzz-sdk` builders.

## Maturity

**Shipped.** VISION.md's own Status table marks the desktop client's Forum surface as
shipped, and VISION_PROJECTS.md's Status table marks "Channels, forums, DMs, canvases" as
"Ships today" — both are cited, dated product-status claims, not impressions. Code backs
the same conclusion end to end: the `forum` channel type and its three event kinds
(45001/45002/45003) are defined in `buzz-core`, built by dedicated `buzz-sdk` builders,
validated and scoped by the relay's ingest pipeline, exposed as first-class commands in
`buzz-cli`, and rendered by dedicated feature modules in both the desktop (React/Tauri)
and mobile (Flutter) clients. See the evidence ledger above for the specific files.

**Narrower and still designed, not shipped:** using the forum surface as the rendering
home for NIP-34 git issues (VISION_PROJECTS.md's "Issues → Forum + NIP-34" section) is a
distinct, forward-looking capability layered on top of the forum channel type. The same
document's own Status table marks "NIP-34 issues (kind:1621)" as "📋 Designed", separately
from the "Ships today" row for forums themselves. This node covers the forum channel type
as it exists today, not that future integration.

## Behavior: rules, constraints, and variants

- **Channel type is fixed at creation and gates which forum operations are legal.** A
  channel's `channel_type` is one of `stream`/`forum`/`dm`/`workflow` (`buzz-core`'s
  `ChannelType`, mirrored by Postgres's `channel_type` enum). Only `stream` and `forum`
  are accepted by the generic channel-creation and channel-template paths in both
  `buzz-cli` and the desktop app; `dm` and `workflow` channels are created through
  separate mechanisms, not this path.
- **Three event kinds carry all forum content:** `KIND_FORUM_POST` (45001, a thread
  root), `KIND_FORUM_COMMENT` (45003, a reply), and `KIND_FORUM_VOTE` (45002, an
  upvote/downvote whose content is literally `"+"` or `"-"`).
- **Posts and comments are capped at 64 KiB of content** (`buzz-sdk`'s
  `build_forum_post` / `build_forum_comment`), and every forum event must carry an `h`
  channel-scope tag — the relay's ingest pipeline enforces this the same way it does for
  stream messages and canvases.
- **A vote must target a real forum post or comment in the same channel.** The relay's
  `validate_forum_vote_target` looks up the voted-on event, rejects the vote if that
  event's kind is not 45001 or 45003, and separately checks the vote and its target
  share a `channel_id` — a vote cannot cross channels or target arbitrary event kinds.
- **Replies are flattened, not arbitrarily nested.** The desktop client's thread
  reconstruction gives a reply depth of 1 when its parent is the thread root and depth 2
  otherwise — matching VISION.md's own description of the surface as "Post → flat
  replies," in contrast to stream messages' deeper threading.
- **Forum content surfaces outside its own channel too.** `buzz-db`'s Home-feed queries
  include both forum kinds in their mentions and activity result sets, so a forum post or
  comment can appear in a member's cross-channel feed, not only when browsing the channel
  directly.
- **Open question, not settled by this node:** whether a forum thread's reply/descendant
  counts are materialized server-side the way stream-message thread counters are. What
  was directly observed is that the desktop client's post-listing view returns a
  zeroed placeholder count and its thread view instead counts the events actually
  returned by that one query. See the `INFERENCE` evidence entry above for exactly what
  was and was not checked.

## Verification

- `crates/buzz-sdk/src/builders.rs`'s own test module exercises the forum builders
  directly: `forum_post_happy_path`, `forum_comment_happy_path`, and
  `forum_post_content_too_large` (the 64 KiB cap) are unit tests in the same crate as the
  builders they check.
- `desktop/src-tauri/src/commands/messages/forum.rs`'s test module covers
  `link_preview_suppression_targets`, the rule that only a message's author or its
  verified agent-owner may suppress a link preview on a forum post/comment via a kind
  40003 edit.
- `crates/buzz-relay/src/handlers/event.rs`'s `channel_scoped_content_kinds_require_h_tags`
  test asserts all three forum kinds require channel scoping, alongside stream messages
  and canvases.

No end-to-end (relay + client) automated test covering the full forum post → reply → vote
path was found or run for this node; the verification above is unit-level, per kind.

## Boundary

This node does not describe:
- **How the capability is built** — the relay's event storage and query surface, the
  desktop/mobile client architectures, and `buzz-cli`'s own structure are the
  architecture family's territory. See `architecture-containers-relay`,
  `architecture-containers-desktop`, `architecture-containers-mobile`, and
  `architecture-containers-cli` in `relationships` above.
- **The interface contract each surface exposes** — the exact `buzz-cli` subcommand
  shapes, the desktop Tauri command signatures, and the relay's WebSocket/HTTP query
  filter shapes are an interface node's territory. No `interfaces-events`-typed corpus
  node exists yet to reference (see *Scope and omissions*).
- **The step-by-step flow of one forum interaction** (compose a post, a reply lands,
  a vote is cast and counted) — that is a flow node's territory. No forum-specific flow
  node exists yet to reference.
- **How the running system is operated** — deployment, monitoring, or incident response
  for the relay that stores forum events is the `operations` corpus surface's territory,
  not this node's.
- **The NIP-34-issues-via-forum integration** described in VISION_PROJECTS.md — that is
  a designed, not-yet-shipped capability layered on top of this one (see *Maturity*
  above), and belongs in its own node once built.

## Relationships

- `references: architecture-containers-relay` — the relay stores, validates and
  fans out every forum event; this capability cannot exist without it.
- `references: architecture-containers-desktop` — the desktop app's dedicated forum
  feature module is one of two first-party surfaces this capability is exposed through.
- `references: architecture-containers-mobile` — the mobile app's parallel forum
  feature module is the other.
- `references: architecture-containers-cli` — `buzz-cli` gives agents the same forum
  operations (create, post, comment, vote) a human client has.

All four targets were checked against `origin/launchpad`'s corpus tree at the recorded
revision and exist there today. No `part-of`, `depends-on`, `implements` or `supersedes`
edge is declared: no broader "channels" capability node, no forum-specific interface
node, and no forum-specific flow node exist yet in the merged corpus for this node to
relate to that way.

## Scope and omissions

**This node covers** what the forum channel type is, its current maturity, the event
kinds and constraints that define its behavior (content limits, channel scoping, vote
target validation, reply flattening), the surfaces it is exposed through, and the
verification found for it.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| How the relay, desktop, mobile and CLI containers that implement this capability are built | `architecture-containers-relay` / `-desktop` / `-mobile` / `-cli` (referenced above) |
| The exact interface contract (CLI subcommand shapes, Tauri command signatures, relay query filters) each surface exposes | a future `interfaces-events`-typed node (none exists yet) |
| The step-by-step flow of a single forum post/reply/vote interaction | a future flow node (none exists yet) |
| How the relay is operated in production | the `operations` corpus surface |
| The NIP-34-issues-via-forum integration | a future node, once that designed capability ships |

**Expected but not verified when this node was written:**
- **Whether forum threads are counted through the same server-side thread-counter
  mechanism stream messages use.** No caller of `insert_thread_metadata` /
  `increment_reply_count` was found outside `buzz-db`'s own module and tests when
  searching the relay crate; see the `INFERENCE` evidence entry above for the exact
  search performed and its limits.
- **Whether an end-to-end (relay + client) test exercises the full forum
  post-then-reply-then-vote path.** Only unit-level tests, one per surface, were found;
  see *Verification* above.
- **The exact database schema for forum-specific tables** (if any exist beyond the
  generic `channel_type` enum and event storage) was not inspected — this node relies on
  the event-kind and builder evidence above rather than a migration-by-migration schema
  read.
