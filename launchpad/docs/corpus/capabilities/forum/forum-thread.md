---
id: capabilities-forum-forum-thread
type: capabilities
status: draft
origin: launchpad
audiences:
  - developer
  - agent
evidence:
  - statement: "This node was authored and checked against repository revision 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5."
    entry_class: FACT
    evidence:
      - "commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
  - statement: "VISION.md's own Surfaces table lists Forum as one of Buzz's seven surfaces (\"Async long-form threads. Culture.\", zero default notifications), and its accompanying bullet list states \"Forum — Discourse-like, slow. Post → flat replies. Zero-notification default,\" explicitly contrasted with Stream's \"Mandatory topics → sub-replies.\""
    entry_class: FACT
    evidence:
      - "VISION.md:19"
      - "VISION.md:27-28"
  - statement: "VISION_PROJECTS.md describes a planned Forum-based rendering of NIP-34 issues (\"Bug reports are NIP-34 kind:1621 events, rendered through Buzz's forum surface... Design discussions and RFCs use the forum's long-form async surface\") and its own capability-status table marks \"Channels, forums, DMs, canvases\" as \"Ships today.\""
    entry_class: FACT
    evidence:
      - "VISION_PROJECTS.md:185-189"
      - "VISION_PROJECTS.md:249"
  - statement: "buzz-core/src/kind.rs defines three dedicated forum event kinds — KIND_FORUM_POST = 45001, KIND_FORUM_VOTE = 45002, KIND_FORUM_COMMENT = 45003 — all included in the crate's exported ALL_KINDS registry."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs:550"
      - "crates/buzz-core/src/kind.rs:552"
      - "crates/buzz-core/src/kind.rs:554"
      - "crates/buzz-core/src/kind.rs:732-734"
  - statement: "ARCHITECTURE.md's own custom-kind table independently documents kind 45001 as \"KIND_FORUM_POST | Forum thread root\" and kind 45003 as \"KIND_FORUM_COMMENT | Forum thread reply,\" and states the relay's Channel type enum includes Forum alongside Stream, Dm and Workflow."
    entry_class: FACT
    evidence:
      - "ARCHITECTURE.md:137-138"
      - "ARCHITECTURE.md:413"
  - statement: "buzz-relay's ingest handler classifies KIND_FORUM_POST, KIND_FORUM_VOTE and KIND_FORUM_COMMENT as requiring the MessagesWrite auth scope, and requires_h_channel_scope() classifies all three as channel-scoped (h-tag-bearing) content, the same classification Stream messages receive."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:390-392"
      - "crates/buzz-relay/src/handlers/ingest.rs:612-641"
  - statement: "A merged unit test, channel_scoped_content_kinds_require_h_tags, directly asserts that requires_h_channel_scope() returns true for KIND_FORUM_POST, KIND_FORUM_VOTE and KIND_FORUM_COMMENT."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs:1221-1234"
  - statement: "Any h-scoped event carrying NIP-10 e-tag root/reply markers — which includes forum posts and comments, since both kinds pass the requires_h_channel_scope gate — is resolved into thread ancestry by the same resolve_nip10_thread_meta function Stream messages use; that function rejects a client-supplied root tag that does not match the parent's own recorded ancestry, and enforces a hard 100-level depth cap (\"thread depth limit exceeded\") regardless of event kind."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:2766-2776"
      - "crates/buzz-relay/src/handlers/ingest.rs:720-850"
      - "crates/buzz-relay/src/handlers/ingest.rs:804-805"
  - statement: "The thread metadata resolved for an inbound event is passed into the storage transaction's thread_params and into the emit_live_thread_summary fan-out call after storage, both unconditional on event kind — the ingest handler contains no forum-specific branch on this path."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:2835-2848"
      - "crates/buzz-relay/src/handlers/ingest.rs:2993-3005"
  - statement: "Because forum posts/comments and Stream messages share the exact code path that resolves thread ancestry and updates thread counters (see the two FACT entries above), a forum thread's reply_count, descendant_count and last_reply_at update the same way a Stream thread's do. This is a conclusion drawn from the shared, kind-unconditional code path rather than an observed run: no forum-kind-specific integration test exercising get_thread_summary against a kind:45001/45003 chain was found."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:2766-2776"
      - "crates/buzz-relay/src/handlers/ingest.rs:2835-2848"
      - "crates/buzz-db/src/store/thread.rs:517-580"
    confidence: 0.85
  - statement: "buzz-db/src/thread.rs maintains reply_count and descendant_count per thread root, with a doc comment stating a crash between the two updates cannot leave them inconsistent, and dedicated increment_reply_count/decrement_reply_count functions that update both fields (floored at 0 on decrement) in one transaction; KIND_THREAD_SUMMARY (kind:39005), the relay-signed overlay carrying {reply_count, descendant_count, last_reply_at, participants}, is documented directly in its own doc comment in kind.rs."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/thread.rs:118"
      - "crates/buzz-db/src/store/thread.rs:256-332"
      - "crates/buzz-core/src/kind.rs:433-435"
  - statement: "KIND_FORUM_VOTE events are rejected unless their e-tag target resolves to an existing event of kind KIND_FORUM_POST or KIND_FORUM_COMMENT in the same channel, enforced by validate_forum_vote_target, which ingest calls only when the submitted event's kind is KIND_FORUM_VOTE."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:1001-1050"
      - "crates/buzz-relay/src/handlers/ingest.rs:2497-2501"
  - statement: "buzz-cli exposes forum-thread interaction directly: `buzz channels create --type forum` creates a buzz_sdk::ChannelKind::Forum channel; `buzz messages thread --channel <uuid> --event <hex>` (cmd_get_thread) queries kinds [9, 40002, 40003, 40008, 45003] by e-tag against the given root, so forum comments (45003) are read through the same command as Stream thread replies; `buzz messages vote --event <id> --direction up|down` (cmd_vote_on_post) builds and submits a kind:45002 event via buzz_sdk::build_vote, which tags it with the target's h and e values and content \"+\"/\"-\"."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/commands/channels.rs:291-318"
      - "crates/buzz-cli/src/commands/messages.rs:394-428"
      - "crates/buzz-cli/src/commands/messages.rs:838-866"
      - "crates/buzz-cli/src/lib.rs:516"
      - "crates/buzz-sdk/src/builders.rs:457-471"
  - statement: "The desktop app ships a dedicated Forum feature (desktop/src/features/forum/) including ForumThreadPanel.tsx, whose ForumThreadResponse type (post, replies: ThreadReply[], totalReplies, nextCursor) renders replies as one flat, cursor-paginated list rather than a nested reply tree — matching VISION.md's \"Post → flat replies\" framing — and a dedicated TanStack Router route (channels.$channelId.posts.$postId.tsx) for viewing one forum post's thread."
    entry_class: FACT
    evidence:
      - "desktop/src/features/forum/ui/ForumThreadPanel.tsx:1-120"
      - "desktop/src/shared/api/types.ts:947-952"
      - "desktop/src/app/routes/channels.$channelId.posts.$postId.tsx:22-51"
  - statement: "On desktop, \"Forum Channels\" is registered as a preview feature in preview-features.json with no defaultEnabled value; resolveEnabled()'s own default parameter is false when a manifest entry omits defaultEnabled, so the Forum surface is off by default on desktop and must be turned on in Settings → Experiments (usePreviewFeatureWarning's own doc comment: \"Stays a no-op for stable features... featureId is in the manifest = preview by definition\"). This qualifies a literal reading of VISION.md's \"Desktop app supports all seven surfaces today\" as meaning every surface ships enabled-by-default."
    entry_class: FACT
    evidence:
      - "preview-features.json:22-27"
      - "desktop/src/shared/features/resolveEnabled.ts:10-19"
      - "desktop/src/app/routes/channels.$channelId.posts.$postId.tsx:33"
      - "desktop/src/shared/features/useFeatureEnabled.ts:80-105"
  - statement: "The mobile Flutter app ships its own forum-thread implementation — mobile/lib/features/forum/forum_thread_page.dart defines ForumThreadPage, documented in its own doc comment as the \"Full-screen page showing a forum post and its replies\" — independent of the desktop preview-feature manifest, since preview-features.json's forum entry lists \"platforms\": [\"desktop\"] only; whether the Flutter app gates Forum behind an equivalent feature flag of its own was searched for and not found, so mobile's default-on/off state is not established either way by this node."
    entry_class: FACT
    evidence:
      - "mobile/lib/features/forum/forum_thread_page.dart:1-38"
      - "preview-features.json:22-27"
  - statement: "No desktop or mobile client source references KIND_FORUM_VOTE (45002) or a vote kind literal 45002 anywhere under desktop/src/ or mobile/lib/, so upvoting/downvoting a forum post or comment is reachable only through buzz-cli's messages vote subcommand or a directly signed POST /events submission, not through either shipped human client UI."
    entry_class: FACT
    evidence:
      - "grep_recursive('FORUM_VOTE|45002', paths=['desktop/src/', 'mobile/lib/']) -> zero matches, run against worktree at commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
  - statement: "Issue #742's Definition of Done requires this node to state the capability and primary actors/outcomes, define behavioral rules/constraints/variants, link major flows/interfaces/data/platform implementation, and link verification demonstrating the capability, in addition to the structural bullets shared by every task in this batch."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#742 definition of done (read directly via gh issue view)"
  - statement: "Parent Feature #612 names this task's target as capabilities/forum/forum-thread.md under its \"collaboration capability corpus\" milestone, one of 71 planned documents in that feature, with acceptance criteria requiring every node to use its assigned template and to let an independent reader traverse from the node to implementation and verification evidence."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#612 body (read directly via gh issue view)"
  - statement: "At repository revision 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5, no launchpad/docs/corpus/capabilities/** directory exists on origin/launchpad, so no other capability-shaped node (merged or in this same batch) is a valid relationship target; the three ids this node does target — architecture-containers-relay, architecture-flows-event-ingestion, architecture-containers-postgres — are confirmed present at that revision."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/containers/relay.md"
      - "launchpad/docs/corpus/architecture/flows/event-ingestion.md"
      - "launchpad/docs/corpus/architecture/containers/postgres.md"
relationships:
  - type: references
    target: architecture-containers-relay
  - type: references
    target: architecture-flows-event-ingestion
  - type: references
    target: architecture-containers-postgres
---

# Forum thread: capability

A forum thread lets a member post a long-form, async topic in a Forum-type channel
(`KIND_FORUM_POST`, kind:45001) and lets other members and agents reply to it
(`KIND_FORUM_COMMENT`, kind:45003) and vote on the post or any comment
(`KIND_FORUM_VOTE`, kind:45002). It is Buzz's Discourse-like counterpart to Stream's
real-time chat: a post gets one flat, chronologically paginated list of replies rather
than nested sub-threads, and the surface defaults to zero notifications — culture and
discussion, not an inbox to keep up with. Primary actors are human members (posting,
replying, browsing) and agents (posting, replying and voting — the only two shipped
clients, desktop and mobile, do not yet expose a vote control, so voting today is an
agent/CLI/API-only outcome, not a human-UI one).

## Maturity

**Relay:** shipped and enforced. `buzz-core` defines all three forum kinds; `buzz-relay`
classifies them as channel-scoped, `MessagesWrite`-gated content; a merged unit test
pins that classification for all three kinds; a forum vote is rejected unless it
targets an existing forum post or comment in the same channel; and forum posts/comments
resolve NIP-10 thread ancestry through the identical code path Stream messages use,
including the shared 100-level depth cap and the shared `reply_count`/`descendant_count`
counter and live-summary update.

**CLI (`buzz-cli`):** shipped. `buzz channels create --type forum` creates the channel;
`buzz messages thread` reads a forum post's replies (kind:45003 is one of the kinds its
reply filter queries); `buzz messages vote` posts a kind:45002 vote.

**Desktop:** shipped as code, but gated off by default. "Forum Channels" is listed in
`preview-features.json` with no `defaultEnabled` value, which `resolveEnabled()`
resolves to `false`; a member must enable it in Settings → Experiments before the
Forum surface appears, and the route component itself calls
`usePreviewFeatureWarning("forum")`. This is a real qualifier on VISION.md's "Desktop
app supports all seven surfaces today" — the surface exists and works, but is not
on by default.

**Mobile:** shipped as code — a dedicated `ForumThreadPage` widget exists — but whether
the Flutter app applies its own equivalent of the desktop preview-feature gate was not
found either way; this node does not claim mobile ships Forum enabled-by-default, only
that the widget exists.

**Voting:** shipped at the relay, SDK and CLI layers; not shipped in either client's UI.
An agent or any direct API caller can vote today; a human using the desktop or mobile
app cannot yet.

## Boundary

This node does not describe:
- **How this is built.** The relay's ingest/validation pipeline, Postgres schema, and
  the shared NIP-10 resolution machinery are the architecture family's territory — see
  `architecture-containers-relay`, `architecture-containers-postgres` and
  `architecture-flows-event-ingestion` in *Relationships* below, all of which this
  capability's events flow through without a forum-specific branch.
- **The interface contract this capability is exposed through.** `buzz-cli`'s
  `channels`/`messages` subcommands and the relay's generic `POST /events` / `POST
  /query` bridge are that boundary; no interface-typed corpus node exists yet to
  reference (`#1342`'s template, not drafted as of this node).
- **The step-by-step request/response sequence** of posting, replying to, or voting on
  a forum thread. That is a flow node's territory (`#1338`, not in this batch) — this
  node states that the capability exists and what it can currently do, not the sequence
  of calls that does it.
- **How the running relay is operated** (deployment, monitoring, incident response) —
  the `operations` corpus surface's territory, not this one.
- **Stream-channel threading as its own subject.** Stream messages share the exact
  ancestry-resolution and counter code this capability relies on, but Stream threading
  itself — its own kinds, its own product framing ("Mandatory topics → sub-replies") —
  is a neighboring, not identical, capability and is only described here to the extent
  the shared code path is evidence for how forum threads behave.
- **Moderation, reporting, search-ranking or feed-inclusion semantics specific to forum
  content.** `crates/buzz-db/src/feed.rs` and the relay's report handler both reference
  forum kinds, but their forum-specific behavior beyond kind inclusion was not
  investigated for this node — see *Scope and omissions*.

## Relationships

- references: `architecture-containers-relay` — hosts the ingest validation, scope
  classification and NIP-10 thread-ancestry resolution every forum post, comment and
  vote passes through.
- references: `architecture-flows-event-ingestion` — the general event-ingestion flow
  a forum post/comment/vote is submitted through, no different in shape for these
  kinds than for any other channel-scoped kind.
- references: `architecture-containers-postgres` — the datastore holding the
  `reply_count`/`descendant_count`/`last_reply_at` thread state this capability's
  replies update.

No `implements`, `depends-on`, `part-of` or `supersedes` edge is declared. No
capability-, interface- or flow-typed sibling node exists yet in `origin/launchpad`'s
corpus (`launchpad/docs/corpus/capabilities/**` does not exist there at the recorded
revision) for this node to target, and this batch's own sibling capability tasks are
not merged either — the same "check before you justify it" rule `AGENTS.md` states,
verified here by listing the corpus tree rather than assumed.

## Scope and omissions

**This node covers** what the forum-thread capability lets a member or agent do (post,
reply, vote), the event kinds and relay-side rules that back it, the shared
thread-ancestry and counter machinery it reuses from Stream messaging, the CLI surface
that exposes it fully, and — as a load-bearing maturity finding rather than a gap — the
concrete difference between VISION.md's product framing and the desktop app's own
preview-feature gate.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| How the relay, Postgres and the ingestion flow are built | `architecture-containers-relay`, `architecture-containers-postgres`, `architecture-flows-event-ingestion` |
| The interface contract (CLI/HTTP surface) exposing this capability | `#1342`'s template (interface, not yet drafted) |
| The step-by-step flow through posting/replying/voting | `#1338` (flow, not yet drafted) |
| How the running relay is operated | the `operations` corpus surface |
| Stream-channel threading as its own capability | a future sibling capability node, not this one |
| Moderation, search-ranking and feed-inclusion treatment specific to forum content | not yet assigned in this batch |

**Expected but not verified when this node was written:**
- **No forum-kind-specific automated test was found** exercising `validate_forum_vote_target`'s
  rejection paths or an end-to-end `get_thread_summary` read against a kind:45001/45003
  chain — only the generic `channel_scoped_content_kinds_require_h_tags` unit test and
  the kind-agnostic `buzz-db/src/thread.rs` test suite (which do not use forum kinds
  directly) were found. This is the basis for the one `INFERENCE` entry in the evidence
  ledger above rather than a `FACT`.
- **Whether the mobile app gates the Forum surface behind its own feature flag** was
  searched for (no equivalent of `preview-features.json` found under `mobile/`) and not
  found — left open rather than assumed either way.
- **`crates/buzz-db/src/feed.rs`'s and the relay's report handler's forum-specific
  behavior** (mention/activity/search ranking, and moderation report handling) were
  found to reference forum kinds by grep but were not read in enough depth to make a
  claim about their forum-specific semantics.
- **No live relay/desktop/mobile run was exercised** for this node — every claim above
  is a static-code and static-vision-doc reading, not an observed runtime trace.
