---
id: capabilities-forum-forum-comment
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
  - statement: "Buzz defines three forum event kinds in the 45000-45999 range: kind:45001 is a forum post (thread root), kind:45002 is a vote, and kind:45003 is a forum comment -- a reply to a post or to another comment."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "buzz-sdk's build_forum_comment constructs a kind:45003 event requiring a channel id (emitted as an `h` tag), a ThreadRef, mentions and media tags; it emits NIP-10-style `e` tags via a shared thread_tags helper: a direct reply to the post carries one `e` tag marked `reply`, while a reply nested under another comment carries two `e` tags -- one marked `root`, one marked `reply` for the immediate parent."
    entry_class: FACT
    evidence:
      - "crates/buzz-sdk/src/builders.rs"
  - statement: "buzz-cli's `messages send --kind 45003` requires `--reply-to`; the CLI rejects the request outright when it is missing, resolves the immediate parent from that argument, and derives the thread root from the parent's own NIP-10 tags via the relay (`resolve_thread_ref`) before building the comment event."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/commands/messages.rs"
  - statement: "On ingest, kind:45003 is one of the kinds `requires_h_channel_scope` treats as mandatory-`h`-tag, and one of the kinds `required_scope_for_kind` maps to `Scope::MessagesWrite`; there is no forum-comment-specific structural validator comparable to `validate_forum_vote_target`, which validates only kind:45002 vote targets, not comment shape."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "A forum comment's `e` tags are parsed by the same `resolve_nip10_thread_meta` function used for other threaded, channel-scoped kinds: it resolves the comment's immediate parent and thread root, rejects a reply whose parent belongs to a different channel or has no channel association, and computes the comment's depth relative to the root."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "On a successful insert of a threaded event (including a kind:45003 comment), the same database transaction increments the parent event's `reply_count` (direct children only) and, when a distinct root exists, the thread root's `descendant_count`; a live kind:39005 thread-summary event is then pushed to subscribers so clients can update badge counts without refetching the head window."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/event.rs"
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "A forum vote (kind:45002) may target either a forum post (kind:45001) or a forum comment (kind:45003); `validate_forum_vote_target` rejects any other target kind, and separately rejects a vote whose target event belongs to a different channel than the vote itself."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "The desktop app's Tauri command layer parses a forum reply event's own `e` tags to resolve `parent_event_id` and an explicit root id (`forum_reply_from_event`), and `desktop/src/shared/api/forum.ts` models a forum comment client-side as a `ThreadReply` carrying `parent_event_id`, `root_event_id` and `depth` -- confirming the desktop client renders forum comments as replies within a thread view rather than as flat messages."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/commands/messages/forum.rs"
      - "desktop/src/shared/api/forum.ts"
  - statement: "The Flutter mobile app's forum_provider.dart builds kind:45003 reply events directly (not through buzz-sdk), including a single `e` tag marked `reply` pointing at the immediate parent, as part of its own forum reply-creation path."
    entry_class: FACT
    evidence:
      - "mobile/lib/features/forum/forum_provider.dart"
  - statement: "Root VISION_PROJECTS.md's Status table marks 'Channels, forums, DMs, canvases' as 'Ships today', the maturity marker for the forum capability family that forum comments belong to."
    entry_class: FACT
    evidence:
      - "VISION_PROJECTS.md:249"
  - statement: "buzz-cli's own documented usage treats 'forum' as a channel-creation convention (`buzz channels create --type forum ...`), distinct from the relay's structural admission checks for kind:45003 itself."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/lib.rs"
  - statement: "No channel-type gate (for example, restricting kind:45003 admission to channels whose `channel_type` is `forum`) was found in the relay's ingest structural checks for kind:45003; the only `channel_type` handling found in `ingest.rs` concerns kind:9007 channel-creation/edit events, not forum-kind admission -- so a forum comment appears postable into any channel that otherwise passes the generic `h`-tag/scope/membership checks, and 'forum channel' reads as a client-side convention rather than a relay-enforced constraint on which kinds a channel accepts."
    entry_class: INFERENCE
    evidence:
      - "grep_case_insensitive('channel_type|ChannelType', path='crates/buzz-relay/src/handlers/ingest.rs', ref='338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5') -> matches only inside the kind:9007 channel-creation/edit block (lines 2595-2669); no match references KIND_FORUM_COMMENT or KIND_FORUM_POST"
      - "crates/buzz-relay/src/handlers/ingest.rs"
    confidence: 0.75
  - statement: "At repository revision 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5, `origin/launchpad`'s corpus tree under `launchpad/docs/corpus/` contains no `capabilities/`, `interfaces-events/`, or forum-specific node of any type -- only `architecture/*`, `standards/*`, `templates/*`, `schema/*`, `AGENTS.md` and `README.md` -- so no existing node is a valid `relationships` target for this one."
    entry_class: FACT
    evidence:
      - "git_ls_tree(ref='origin/launchpad', path='launchpad/docs/corpus') -> AGENTS.md, README.md, architecture/{containers,context,deployment,flows,principles}/**, schema/**, standards/**, templates/**, at commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
---

# Forum comment: capability

A member or agent can reply to a forum post, or to another comment within that
post's thread, to hold a threaded discussion underneath a top-level forum post.
A forum comment is a first-class, independently addressable event: it can
itself receive further replies (nested threading, not just flat comments), it
can be voted on the same way a post can, and the reply/descendant counts on
its parent and thread root update live so clients can show thread activity
without refetching.

## Maturity

Shipped. Kind:45003 (forum comment) is defined and handled end-to-end: the
relay accepts, threads, and counts it (`crates/buzz-relay/src/handlers/ingest.rs`,
`crates/buzz-db/src/event.rs`); `buzz-sdk` builds it (`build_forum_comment`);
`buzz-cli` sends it (`messages send --kind 45003 --reply-to <id>`); the desktop
app's Tauri layer and `desktop/src/shared/api/forum.ts` model and render it as
a threaded reply; and the Flutter mobile app builds kind:45003 reply events
directly from `forum_provider.dart`. Root `VISION_PROJECTS.md`'s own Status
table separately marks the forum capability family ("Channels, forums, DMs,
canvases") "Ships today" (`VISION_PROJECTS.md:249`).

## Boundary

This node does not describe:
- how the relay's ingestion pipeline, thread-metadata schema, and live
  fan-out are built internally -- see a future architecture node for that (no
  forum-specific architecture node exists in the corpus yet; the generic
  `architecture-flows-event-ingestion` node documents ingestion for all kinds,
  not the forum kinds specifically).
- the interface(s) a comment is created and read through -- `buzz-cli`'s
  `messages` subcommands, the relay's WebSocket/HTTP event-submission surface,
  and each client's own API layer. A future interface node would own that.
- the step-by-step flow of composing, submitting, and rendering a comment
  reply across a client and the relay. A future flow node would own that.
- forum posts (kind:45001) and forum votes (kind:45002) as their own
  capabilities -- related, and sharing this node's own maturity evidence, but
  each is a separate votable/addressable event kind with its own rules
  (a post has no parent; only a vote has a distinct target-kind validator).
  This node documents the comment/reply kind only.
- how the forum feature is operated in production (deployment, monitoring,
  incident response).

## Relationships

Declared: none. Checked: `git ls-tree -r --name-only origin/launchpad --
launchpad/docs/corpus` at commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5 lists
only `architecture/*`, `standards/*`, `templates/*`, `schema/*`, `AGENTS.md`
and `README.md` -- no `capabilities/`, `interfaces-events/`, or forum-specific
node exists yet for this node to `references`, `part-of`, or `implements`
against. The closest candidate, `architecture-flows-event-ingestion`,
documents the relay's generic ingestion pipeline rather than the forum kinds
specifically, so pointing at it here would assert a capability-to-architecture
link the template reserves for a node that actually realizes *this*
capability, not one that happens to run every kind through the same pipeline.
The first forum-specific architecture, interface, or flow node is the natural
moment to add `references` edges back to this one.

## Scope and omissions

**This node covers** what the forum-comment capability is (a threaded reply to
a forum post or to another comment), where it currently stands (shipped,
evidenced by relay, CLI, SDK, desktop, and mobile code plus
`VISION_PROJECTS.md`'s own status marker), and its explicit boundary against
the architecture, interface, flow, sibling-capability, and operations content
it does not describe.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| How the relay's ingestion, thread-metadata, and fan-out pipeline is built | a future architecture node (none exists yet specifically for forum kinds) |
| The interface(s) (CLI, HTTP, protocol, per-client API) a comment is created/read through | a future interface node |
| The step-by-step flow of composing and submitting a comment | a future flow node |
| Forum posts (kind:45001) and forum votes (kind:45002) as their own capabilities | future sibling capability nodes |
| How the forum feature is operated in production | the `operations` corpus surface |

**Expected but not verified when this node was written:**
- No forum-specific architecture, interface, or flow node exists yet in the
  corpus to `references` -- confirmed by listing the corpus tree rather than
  assumed (see the evidence ledger and *Relationships* above).
- Whether a channel's `channel_type` is enforced anywhere else in the
  codebase (for example, client-side UI hiding the comment composer outside a
  forum-type channel) beyond the relay's ingest path was not checked -- the
  INFERENCE above is scoped to the relay's structural validation only, not to
  any client's own UI gating.
- The workflow engine's own event-matching against kind:45003 (for example,
  whether a workflow trigger can react to a new forum comment) was not
  investigated; `buzz-workflow` was found only via a filename grep for
  "forum" and was not opened for this node.
