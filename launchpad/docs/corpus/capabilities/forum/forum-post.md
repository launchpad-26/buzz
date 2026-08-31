---
id: capabilities-forum-forum-post
type: capabilities
status: draft
origin: upstream
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5."
    entry_class: FACT
    evidence:
      - "commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
  - statement: "A forum post is a Nostr thread-root event of kind 45001, defined alongside kind 45002 (forum vote) and kind 45003 (forum comment) in the 'Forum / social (45000-45999)' kind range; a code comment on this block records that 'V1 used addressable range (30001-30003) -- wrong', i.e. forum posts were previously modeled as addressable/parameterized-replaceable events and that was corrected to regular (non-replaceable) events in the current range."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs:547-554"
  - statement: "buzz_sdk::build_forum_post constructs a kind:45001 event: it rejects content over 64KiB via check_content, tags the event with the channel's h tag, appends mention (p) tags and imeta (media) tags, and calls allow_self_tagging() so an author who mentions themselves is not rejected as self-tagging."
    entry_class: FACT
    evidence:
      - "crates/buzz-sdk/src/builders.rs:284-297"
  - statement: "Unit tests forum_post_happy_path and forum_post_content_too_large confirm build_forum_post produces a signed kind:45001 event carrying the channel's h tag on success, and returns SdkError::ContentTooLarge when content exceeds 64KiB (tested at 64*1024+1 bytes)."
    entry_class: FACT
    evidence:
      - "crates/buzz-sdk/src/builders.rs:2577-2593"
  - statement: "buzz_sdk::build_forum_comment constructs a kind:45003 reply event with the same 64KiB content ceiling, the channel's h tag, and additionally NIP-10-style thread tags derived from a required ThreadRef (root and parent event ids), plus mention and imeta tags; forum_comment_happy_path confirms the resulting event is kind 45003 and carries the h tag."
    entry_class: FACT
    evidence:
      - "crates/buzz-sdk/src/builders.rs:299-312"
      - "crates/buzz-sdk/src/builders.rs:2595-2606"
  - statement: "buzz_sdk::build_vote constructs a kind:45002 vote event whose content is the literal string \"+\" for VoteDirection::Up or \"-\" for VoteDirection::Down, tagged with the channel's h tag and an e tag pointing at the target event id -- the vote itself carries no separate title, subject, or free-text payload."
    entry_class: FACT
    evidence:
      - "crates/buzz-sdk/src/builders.rs:456-471"
  - statement: "The relay's ingest pipeline requires an h (channel) tag for kind:45001, kind:45002 and kind:45003 events -- requires_h_channel_scope() lists all three explicitly -- and classifies all three under Scope::MessagesWrite for permission checks, the same write scope as stream messages, canvases and reactions."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:389-392"
      - "crates/buzz-relay/src/handlers/ingest.rs:618-627"
  - statement: "validate_forum_vote_target rejects a kind:45002 vote whose e-tagged target event does not resolve to an existing event, whose target's kind is neither KIND_FORUM_POST nor KIND_FORUM_COMMENT, or whose target belongs to a different channel than the vote event's own h tag -- a vote may only target a forum post or a forum comment, and only within the same channel."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:1001-1046"
  - statement: "Test channel_scoped_content_kinds_require_h_tags asserts, for KIND_FORUM_POST, KIND_FORUM_VOTE and KIND_FORUM_COMMENT among other kinds, that requires_h_channel_scope() returns true for each."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs:1215-1230"
  - statement: "buzz-cli exposes forum posting and reply through the existing messages send path: passing --kind 45001 builds a forum post via buzz_sdk::build_forum_post, and --kind 45003 builds a forum comment via buzz_sdk::build_forum_comment, which additionally requires --reply-to (rejected with a usage error if absent) because a forum comment needs a thread reference."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/commands/messages.rs:645-663"
  - statement: "buzz-cli's cmd_vote_on_post builds and submits a kind:45002 vote event from a target event id and a --direction of 'up' or 'down' (any other value is rejected as a usage error), via buzz_sdk::build_vote."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/commands/messages.rs:837-862"
  - statement: "A Buzz channel has a ChannelType enum with a dedicated Forum variant ('Threaded forum-style discussion'), distinct from Stream, Dm and Workflow, with canonical string representation \"forum\" round-tripped through FromStr; buzz-cli's channel-creation commands accept --type forum (alongside stream) and map it to buzz_sdk::ChannelKind::Forum."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/channel.rs:58-97"
      - "crates/buzz-cli/src/commands/channels.rs:291-318"
  - statement: "Forum posts (kind 45001) and forum comments (kind 45003) are included, alongside stream messages, kind:1 text notes and several git event kinds, in the mentions-feed query (build_mentions_query); forum posts alone (kind 45001, without the comment kind) are included in the activity-feed query (build_activity_query), both scoped to the community and the caller's accessible channels."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/feed.rs:91-112"
      - "crates/buzz-db/src/store/feed.rs:253-273"
  - statement: "The desktop app implements a dedicated forum feature module (desktop/src/features/forum) with ForumView, ForumPostCard, ForumThreadPanel, ForumComposer and related UI components, plus a hooks.ts data layer -- forum posting and reading is a built, not merely planned, desktop surface."
    entry_class: FACT
    evidence:
      - "desktop/src/features/forum/ui/ForumView.tsx"
      - "desktop/src/features/forum/ui/ForumPostCard.tsx"
      - "desktop/src/features/forum/ui/ForumThreadPanel.tsx"
      - "desktop/src/features/forum/ui/ForumComposer.tsx"
      - "desktop/src/features/forum/hooks.ts"
  - statement: "The desktop E2E mock bridge (desktop/src/testing/e2eBridge.ts) models forum posts and replies as distinct RawForumPost/RawForumReply/RawForumThreadResponse types and implements handleGetForumPosts, confirming forum-post read behavior is exercised in the desktop test surface, not only in production code."
    entry_class: FACT
    evidence:
      - "desktop/src/testing/e2eBridge.ts:771-805"
      - "desktop/src/testing/e2eBridge.ts:4606-4610"
  - statement: "Root VISION.md's Surfaces table describes Forum as 'Async long-form threads. Culture.' with a Zero default-notification setting, and separately states 'Forum -- Discourse-like, slow. Post -> flat replies. Zero-notification default,' naming a flat (non-nested) reply model as the intended interaction shape distinct from Stream's 'Mandatory topics -> sub-replies.'"
    entry_class: FACT
    evidence:
      - "VISION.md:15-28"
  - statement: "Root VISION.md marks the desktop client (Tauri) as already shipping a Forum surface (checked box, alongside Stream, Home, DMs, Agents, Workflows, Search, Settings, Profiles, Presence), and separately marks the Flutter mobile client's forum surface as in active development, not yet shipped."
    entry_class: FACT
    evidence:
      - "VISION.md:223"
      - "VISION.md:232"
  - statement: "Root VISION_PROJECTS.md's capability status table lists 'Channels, forums, DMs, canvases' as '✅ Ships today,' the product-level maturity marker for this capability among others."
    entry_class: FACT
    evidence:
      - "VISION_PROJECTS.md:249"
  - statement: "Root VISION_PROJECTS.md's 'Issues -> Forum + NIP-34' section states that Buzz's forum surface also renders NIP-34 kind:1621 bug-report/issue events with NIP-22 kind:1111 threaded comments, and that 'design discussions and RFCs use the forum's long-form async surface' -- meaning the forum UI surface hosts more than one underlying event kind, and kind:45001/45003 (this node's subject) is the native Buzz forum-post/comment pair, distinct from the NIP-34/NIP-22 issue-tracking kinds the same surface also displays."
    entry_class: FACT
    evidence:
      - "VISION_PROJECTS.md:185-189"
  - statement: "No code path was found that updates a reply_count or descendant_count counter for kind:45001/45003 forum events -- a repository-wide search of buzz-relay and buzz-db for reply_count/descendant_count alongside forum-specific kind constants returned no matches -- so unlike stream-message threads (per root AGENTS.md's 'Thread counters' note), forum thread size does not appear to be materialized as an incremental counter; this is reasoning from an absence of matches rather than a read of a design document stating so."
    entry_class: INFERENCE
    evidence:
      - "grep_recursive(pattern='reply_count|descendant_count', paths=['crates/buzz-db/src', 'crates/buzz-relay/src'], ref='338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5') -> no forum-kind-associated matches"
    confidence: 0.7
---

# Forum post: capability

Buzz lets a member of a forum-type channel start a top-level, long-form discussion
thread -- a forum post -- that other members reply to and upvote or downvote,
independently of the channel's real-time stream. This is the async, low-urgency
counterpart to Stream's real-time chat: a member opens a topic once, and replies
accumulate flat underneath it (not nested sub-threads) with no default notification
noise, the same "Discourse-like, slow" model VISION.md states for the Forum surface
as a whole.

## Maturity

**Shipped.** The relay ingest pipeline enforces channel scoping, write permission and
vote-target validation for kind:45001 (forum post), kind:45002 (forum vote) and
kind:45003 (forum comment) today (`crates/buzz-relay/src/handlers/ingest.rs`), the SDK
ships builders for all three (`crates/buzz-sdk/src/builders.rs`) with passing unit
tests, `buzz-cli` exposes posting, replying and voting through its existing
`messages`/`channels` commands, and the desktop app has a dedicated `forum` feature
module with composer, post-card and thread-panel UI plus E2E mock-bridge coverage.
VISION_PROJECTS.md's own capability status table marks "Channels, forums, DMs,
canvases" as shipping today, and VISION.md marks the desktop Forum surface with a
checked box while explicitly marking the Flutter mobile client's forum surface as
still in active development (not yet shipped there).

A forum-type channel's own existence is a prerequisite this node does not restate --
`ChannelType::Forum` is a channel-level classification (`crates/buzz-core/src/channel.rs`),
distinct from the kind:45001 event this node documents.

## Boundary

This node does not describe:
- **How the channel/relay/database architecture is built.** The relay's ingest
  pipeline, event storage and channel-scoping machinery are shared across every
  channel-scoped event kind, not specific to forum posts; no architecture node for
  that machinery exists yet in the merged corpus to reference.
- **The CLI or HTTP interface surface forum posting is exposed through.** `buzz-cli`'s
  `messages`/`channels` command groups and the relay's `POST /events` bridge expose
  many event kinds, not only forum posts; no interface node for either exists yet in
  the merged corpus to reference.
- **The step-by-step flow of composing, submitting and rendering one forum post.**
  That is a flow-shaped document, not this capability statement.
- **How the forum surface renders NIP-34 issues or NIP-22 issue comments.**
  VISION_PROJECTS.md states the same forum UI surface also displays kind:1621/kind:1111
  issue-tracking events; those are a different capability sharing a UI surface, not the
  kind:45001/45002/45003 forum-post/vote/comment triad this node documents.
- **How the running relay is operated, deployed or monitored.**

## Relationships

None declared. `origin/launchpad`'s merged corpus tree was checked at this node's
recorded revision and contains no architecture, interface or flow node yet that this
capability could `references` -- the four nodes present (`corpus-agents`,
`corpus-readme`, `corpus-standard-confidence`, `corpus-standard-decision-references`)
are all procedural/meta-documents about the corpus itself, not architecture or
interface nodes for the forum surface. Sibling capability nodes drafted in this same
batch are not yet merged to `origin/launchpad` and are therefore not valid targets
either, per `AGENTS.md`'s rule to resolve relationships against the merge-target
branch, not the author's own worktree.

## Scope and omissions

**This node covers** what a forum post is (kind:45001, its 64KiB content ceiling, its
channel-scoping and permission requirements), its companion kinds (kind:45002 vote,
kind:45003 comment) and how they relate to it, where the capability is implemented
today (relay, SDK, CLI, desktop), and its stated product maturity.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| How the channel/relay/event-storage architecture is built | an architecture-type node, not yet drafted |
| The CLI/HTTP interface surface exposing forum posting | an interfaces-events-type node, not yet drafted |
| The step-by-step compose-submit-render flow through a forum post | a flow-type node, not yet drafted |
| How the forum UI surface also renders NIP-34/NIP-22 issue events | a separate capability, out of this node's scope |
| How the running system is operated | the `operations` corpus surface |

**Expected but not verified when this node was written:**
- **Whether forum thread size (reply count) is materialized anywhere for display**
  (e.g. computed at query time versus stored). No incrementing counter analogous to
  stream threads' `reply_count`/`descendant_count` was found for forum kinds in
  `buzz-relay`/`buzz-db`; this is recorded above as an `INFERENCE`, not a `FACT`, since
  it rests on the absence of a grep match rather than a read design document.
- **Mobile (Flutter) forum behavior was not inspected.** VISION.md states the mobile
  forum surface is still in active development; this node's evidence is drawn from the
  relay, SDK, CLI and desktop, not from `mobile/`.
- **Vote scoring/aggregation (how up/down votes on a post are summed and surfaced)**
  was not traced beyond `validate_forum_vote_target`'s acceptance rule -- no vote-tally
  read path was inspected for this node.
