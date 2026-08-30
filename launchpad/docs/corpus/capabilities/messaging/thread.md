---
id: capabilities-messaging-thread
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
  - statement: "buzz-sdk's ThreadRef carries a root_event_id and a parent_event_id, documented as NIP-10 markers: a direct reply (root == parent) emits a single `[\"e\", root, \"\", \"reply\"]` tag, and a nested reply (root != parent) emits both `[\"e\", root, \"\", \"root\"]` and `[\"e\", parent, \"\", \"reply\"]`."
    entry_class: FACT
    evidence:
      - "crates/buzz-sdk/src/lib.rs:24-33"
  - statement: "buzz-sdk's thread_tags function implements exactly that root/reply e-tag emission, and build_message, build_forum_comment and build_diff_message each call it when a ThreadRef is supplied (build_message and build_diff_message take it as optional, build_forum_comment requires it)."
    entry_class: FACT
    evidence:
      - "crates/buzz-sdk/src/builders.rs:177-190"
      - "crates/buzz-sdk/src/builders.rs:224-245"
      - "crates/buzz-sdk/src/builders.rs:300-316"
      - "crates/buzz-sdk/src/builders.rs:318-386"
  - statement: "buzz-db's thread_metadata table is populated through ThreadMetadataParams (event_id, channel_id, parent_event_id, root_event_id, depth, broadcast) and insert_thread_metadata, called inside the same Postgres transaction as the event insert, which -- only when the event row was newly inserted (never on a duplicate) -- also creates root/parent stub rows if missing and increments the parent's reply_count and the root's descendant_count."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/event.rs:1109-1130"
      - "crates/buzz-db/src/thread.rs:107-239"
  - statement: "get_thread_replies paginates a thread's replies by a composite (event_created_at, event_id) keyset specifically because replies routinely share a created_at second and a timestamp-only cursor silently drops tied replies past the first page; get_thread_replies_pages_same_second_ties_without_loss pins this behavior."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/thread.rs:331-344"
      - "crates/buzz-db/src/thread.rs:1106-1218"
  - statement: "get_thread_summary returns aggregated reply_count, descendant_count, last_reply_at and up to 10 distinct participant pubkeys (most-recent-first) for one event; get_channel_window batches the identical thread-summary shape across a whole page of channel rows in one query rather than one per root."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/thread.rs:45-56"
      - "crates/buzz-db/src/thread.rs:512-575"
      - "crates/buzz-db/src/thread.rs:736-791"
  - statement: "get_channel_window's top-level predicate excludes ordinary thread replies from a channel's main timeline: only depth-0 events, events with no thread_metadata row at all, and depth-1 replies explicitly marked broadcast are returned as channel rows; channel_window_top_level_predicate pins that a non-broadcast depth-1 reply is never a channel row."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/thread.rs:577-651"
      - "crates/buzz-db/src/thread.rs:1546-1607"
  - statement: "On ingest, the relay's resolve_nip10_thread_meta parses an event's e-tags for root/reply markers, looks up the parent's own thread_metadata row to determine the effective root and the new depth (parent depth + 1), and rejects the event outright if the client-supplied root tag does not match the parent's actual ancestry or if depth would exceed 100."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:720-806"
  - statement: "requires_h_channel_scope -- the set of kinds resolve_nip10_thread_meta is even attempted for -- includes the stream-message family, canvas, and the forum-post/vote/comment kinds; kinds outside that set never get thread metadata resolved regardless of any e-tag they carry."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:612-627"
      - "crates/buzz-relay/src/handlers/ingest.rs:2766-2773"
  - statement: "On successful ingest of an event with resolved NIP-10 thread metadata, the relay pushes a fresh relay-signed kind:39005 overlay event -- content `{reply_count, descendant_count, last_reply_at, participants}`, keyed by the root event id -- which is synthesized at push/query time and never itself stored; test_reply_ingest_pushes_live_thread_summary in the relay's own e2e suite exercises this side effect."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs:433-435"
      - "launchpad/docs/corpus/architecture/flows/event-ingestion.md"
  - statement: "buzz-cli's find_root_from_tags and resolve_thread_ref implement the identical root/reply e-tag interpretation client-side: given a parent event id, they fetch the parent, read its e-tags, and derive root == parent for a direct reply or root == the parent's own root marker for a nested reply -- the same rule the relay enforces server-side."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/commands/messages.rs:15-84"
  - statement: "buzz messages thread (cmd_get_thread) fetches a thread by ORing two filters in one query call -- events of kinds [9, 40002, 40003, 40008, 45003] whose e-tag references the given event id, plus the root event itself by id -- accepting an optional depth_limit and capping limit at 500."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/commands/messages.rs:394-428"
  - statement: "The desktop client's getThreadReference re-implements the same root/reply e-tag parsing (root tag if present, else the last reply-marked e-tag as both parent and root), and isThreadReply additionally excludes a broadcast reply from being treated as thread-only content -- both properties this node's ingest and read-path evidence above also establish server-side."
    entry_class: FACT
    evidence:
      - "desktop/src/features/messages/lib/threading.ts:1-52"
  - statement: "KIND_FORUM_POST (45001) is documented as 'a forum post (thread root)' and KIND_FORUM_COMMENT (45003) as 'a comment reply on a forum post', a second, structurally distinct thread-root/thread-reply pairing from the stream-message (kind 9) case, using the same NIP-10 e-tag markers via thread_tags."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs:549-554"
  - statement: "VISION_PROJECTS.md's own Status table marks 'Channels, forums, DMs, canvases' as shipping today; forum posts and comments (kind 45001/45003) and stream-message replies (kind 9) are both threaded via the same NIP-10 mechanism this node documents, so this capability's maturity is Shipped rather than in-progress or designed."
    entry_class: FACT
    evidence:
      - "VISION_PROJECTS.md:249"
  - statement: "VISION_PROJECTS.md's Nostr-Native table separately lists a 'Comments' layer using NIP-22 kind:1111 with the rationale 'Threaded replies everywhere', but a case-sensitive grep of crates/buzz-core/src/kind.rs and crates/buzz-relay/src for the literal token 1111 as a kind constant returns no match -- kind:1111 is not defined or handled anywhere in this repository at the recorded revision, so that row describes a future git-hosting/NIP-34-issue-comments surface this node's NIP-10-based capability does not cover."
    entry_class: INFERENCE
    evidence:
      - "VISION_PROJECTS.md:230"
      - "grep_case_sensitive('1111', path='crates/buzz-core/src/kind.rs') -> no kind-constant match, run against 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
      - "grep_case_sensitive('1111', path='crates/buzz-relay/src', recursive=true) -> matches only unrelated hex-literal test fixtures in crates/buzz-relay/src/api/git/manifest_event.rs, run against 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
    confidence: 0.75
  - statement: "Issue #781's Definition of Done, for this capability-typed task, requires the document to state the capability and primary actors/outcomes, define behavioral rules/constraints/variants, link major flows/interfaces/data/platform implementation, and link verification demonstrating the capability -- distinct in shape from the flow-typed DoD tail (trigger/preconditions/termination, ordered interactions, trust-boundary crossings, failure/rollback) seen on sibling issues #770 and #777, confirming #781 itself carries no instance of the flow/capability DoD-template mixup those two exhibit."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#781 definition of done, cross-checked against launchpad-26/buzz#770 and #777"
  - statement: "At the recorded revision, origin/launchpad carries no node anywhere under launchpad/docs/corpus/capabilities/ -- the directory does not exist on that branch -- so no capabilities-messaging-reply or capabilities-messaging-thread-counters sibling id exists yet to reference, and this node's Boundary section names both only as unmerged, in-progress sibling subjects rather than as relationships targets."
    entry_class: FACT
    evidence:
      - "git_ls_tree(ref='origin/launchpad', path='launchpad/docs/corpus/capabilities') -> empty, no such path, checked immediately before drafting this node"
relationships:
  - type: references
    target: architecture-flows-event-ingestion
  - type: references
    target: architecture-containers-relay
  - type: references
    target: architecture-containers-postgres
---

# Thread: capability

Buzz lets a user or agent reply to a specific message or forum post and have
that reply, and every further reply to it, tracked as one nested conversation
distinct from the channel's main timeline -- a **thread**. A thread has one
root (the first message or forum post), a chain of parents down to arbitrary
nesting depth, and materialized counters (direct reply count, total descendant
count, last-reply time, recent participants) a reader can query without
walking every reply.

**Primary actors.** A human or agent client composing a reply (via the
desktop app, the `buzz` CLI, or any NIP-10-aware Nostr client publishing into
a Buzz-scoped channel); the relay, which resolves and persists thread
ancestry and pushes live summary updates; and a reader (human or agent)
fetching a thread's replies or a channel's summarized top-level view.

**Primary outcomes.** A reply is durably linked to its root and its immediate
parent; a thread's aggregate shape (reply count, descendant count, last
activity, recent participants) is available without re-deriving it from every
individual reply; and a channel's main timeline shows only top-level activity
plus explicitly broadcast replies, not every buried reply in every thread.

## Maturity

**Shipped.** VISION_PROJECTS.md's own Status table marks "Channels, forums,
DMs, canvases" as shipping today, and this capability underlies both: stream
messages (kind 9) reply-thread via the same NIP-10 `e`-tag mechanism as forum
posts and comments (kind 45001/45003) (`crates/buzz-core/src/kind.rs:549-554`).
The capability is implemented end to end -- SDK tag construction
(`crates/buzz-sdk/src/builders.rs:177-190`), relay-side resolution and
persistence (`crates/buzz-relay/src/handlers/ingest.rs:720-806`,
`crates/buzz-db/src/thread.rs`), a CLI read path
(`crates/buzz-cli/src/commands/messages.rs:394-428`), and a desktop UI
(`desktop/src/features/messages/ui/MessageThreadPanel.tsx`,
`desktop/src/features/messages/lib/threading.ts`) -- rather than designed but
unbuilt.

## Behavioral rules, constraints, and variants

- **Threading is opt-in per message, not automatic.** A message becomes a
  reply only when its author (or their client/SDK) supplies a `ThreadRef`;
  an ordinary top-level message carries no `e`-tag root/reply marker and is
  never treated as a reply (`crates/buzz-sdk/src/builders.rs:224-245`).
- **Direct vs. nested reply is a marker distinction, not a separate code
  path.** `root == parent` (direct reply to a top-level message) emits one
  `["e", root, "", "reply"]` tag; `root != parent` (reply to a reply) emits
  both a `"root"`-marked and a `"reply"`-marked tag
  (`crates/buzz-sdk/src/lib.rs:24-33`, `crates/buzz-sdk/src/builders.rs:177-190`).
- **The relay re-derives and validates ancestry; it does not trust the
  client's root tag at face value.** `resolve_nip10_thread_meta` looks up the
  parent's own stored thread metadata (or, if the parent itself has none yet,
  the parent's own e-tags) to compute the *actual* root and depth, and
  rejects the event if the client-supplied root tag disagrees with that
  computed ancestry (`crates/buzz-relay/src/handlers/ingest.rs:749-844`,
  message: `"root tag does not match thread ancestry"`).
- **Nesting depth is capped at 100 server-side.** An event whose computed
  depth would exceed 100 is rejected at ingest
  (`crates/buzz-relay/src/handlers/ingest.rs:803-806`).
- **Only a fixed set of kinds is even eligible for thread resolution.**
  `requires_h_channel_scope` -- the stream-message family, canvas, and the
  forum post/vote/comment kinds -- gates whether `resolve_nip10_thread_meta`
  runs at all; a kind outside that set carrying an `e`-tag is never threaded
  (`crates/buzz-relay/src/handlers/ingest.rs:612-627, 2766-2773`).
- **A reply is invisible on the channel's main timeline unless explicitly
  broadcast.** `get_channel_window`'s top-level predicate returns only
  depth-0 events, events with no thread metadata at all, and depth-1 replies
  whose `broadcast` flag is true; an ordinary (non-broadcast) reply at any
  depth is never a channel-timeline row, only a thread-panel row
  (`crates/buzz-db/src/thread.rs:577-651`).
- **Counters are transactional and update-not-recompute.** `reply_count`
  (direct replies to one event) and `descendant_count` (every reply at every
  depth under a root) are incremented inside the same Postgres transaction as
  the reply's own insert, never recomputed by scanning replies
  (`crates/buzz-db/src/thread.rs:107-239`).
- **Thread-reply pagination requires a composite cursor.** Because replies
  routinely share a `created_at` second, `get_thread_replies` paginates on
  `(event_created_at, event_id)` rather than timestamp alone -- a
  timestamp-only cursor silently drops tied replies past the first page
  (`crates/buzz-db/src/thread.rs:331-344`).
- **A live summary overlay, not a stored event.** After a threaded event is
  accepted, the relay synthesizes and pushes a relay-signed kind:39005 event
  (content: `{reply_count, descendant_count, last_reply_at, participants}`)
  for the affected root; this overlay is generated at push/query time and is
  never itself persisted (`crates/buzz-core/src/kind.rs:433-435`).
- **Two independently-styled thread roots exist, sharing one mechanism.**
  Stream-message replies (kind 9, chat) and forum comments (kind 45003, forum
  posts) both thread via the identical NIP-10 marker scheme and the identical
  `thread_metadata` persistence, differing only in the surface (chat timeline
  vs. forum post) the root belongs to.

## Boundary

This node does not describe:

- **The single reply act itself** -- composing and sending one reply message,
  as distinct from the thread structure that act participates in. That is the
  sibling capability `capabilities/messaging/reply.md`, not yet merged onto
  `origin/launchpad` at the recorded revision (checked directly, see the
  evidence ledger) and therefore not a `relationships` target here.
- **The reply/descendant counter mechanics as their own subject** -- how
  `reply_count` and `descendant_count` are specifically incremented,
  decremented and kept consistent under deletion. That is the sibling
  capability `capabilities/messaging/thread-counters.md`, dispatched in this
  same wave and also not yet merged onto `origin/launchpad` at the recorded
  revision, so likewise not referenced.
- **The step-by-step ingestion sequence a threaded event travels through** --
  admission, storage transaction, side effects, live fan-out. That is
  `architecture-flows-event-ingestion`, already merged and referenced above;
  this node states what threading *is* and the rules it enforces, not the
  ordered mechanics of one event's trip through the relay.
- **The relay and Postgres containers' own internal structure** -- this node
  cites `architecture-containers-relay` and `architecture-containers-postgres`
  as where the capability's implementation lives, without restating either
  container's own architecture.
- **Any future NIP-22 (kind:1111) comment-threading surface** named in
  VISION_PROJECTS.md's Nostr-Native table for git-hosted issue discussions.
  That kind is not implemented anywhere in this repository at the recorded
  revision (see the INFERENCE evidence entry above); this node covers the
  NIP-10-based mechanism that is actually built.
- **Moderation-driven counter adjustment on delete** (`soft_delete_event_and_update_thread`,
  which decrements `reply_count`/`descendant_count` when a threaded event is
  soft-deleted) beyond naming that it exists -- its own behavior belongs with
  the counters capability above.

## Relationships

- references: `architecture-flows-event-ingestion` -- the merged flow node
  documenting the transactional ingest path (event insert, `thread_metadata`
  insert/update, kind:39005 push) that this capability's persistence rules
  are implemented inside.
- references: `architecture-containers-relay` -- where NIP-10 resolution
  (`resolve_nip10_thread_meta`) and per-kind eligibility
  (`requires_h_channel_scope`) run.
- references: `architecture-containers-postgres` -- where the
  `thread_metadata` table and its keyset-paginated read queries live.

## Verification

- **Unit/integration, buzz-db (require Postgres, `#[ignore]`, run via
  `just test`):** `crates/buzz-db/src/thread.rs`'s own `mod tests` --
  `get_thread_replies_reconstructs_stored_events`,
  `get_thread_replies_pages_same_second_ties_without_loss` (composite cursor
  under same-second ties),
  `get_thread_replies_reaches_nested_depth_two_replies` (depth >= 2
  reachability and the root-stub insert path),
  `insert_thread_metadata_nested_reply_creates_root_stub`,
  `get_thread_replies_skips_unreconstructable_row` (corrupt-row
  skip-and-continue), `channel_window_top_level_predicate` (broadcast vs.
  ordinary reply visibility), `channel_window_pages_same_second_ties_without_loss`,
  `channel_window_exact_multiple_final_page_reports_exhausted`, and
  `channel_window_joins_thread_summaries_with_participants`.
- **Relay end-to-end (`crates/buzz-test-client/tests/e2e_relay.rs`,
  `#[ignore]`, run via `just test`):** `test_reply_ingest_pushes_live_thread_summary`,
  named directly by `architecture-flows-event-ingestion`'s own evidence
  ledger as covering the kind:39005 live-push side effect this node
  describes.
- **CLI unit test:** `crates/buzz-cli/src/commands/messages.rs`'s own
  `#[cfg(test)]` module includes `no_thread_markers_returns_none`, pinning
  that a message with no root/reply e-tag is correctly treated as
  thread-less by `find_root_from_tags`.
- **Desktop:** `desktop/src/features/messages/lib/threadTreeLayout.test.mjs`
  exercises client-side thread-tree construction from the same
  `getThreadReference` parsing named in the evidence ledger above.

These end-to-end and integration tests are marked `#[ignore]` per this
repository's convention for tests requiring a live Postgres/Redis, run via
`just test` rather than `just test-unit` -- linked here as representative
coverage, not asserted to have been executed while authoring this node.

## Scope and omissions

**This node covers** the NIP-10 root/reply threading capability shared by
stream-message replies (kind 9) and forum comments (kind 45003): what makes a
message a threaded reply, how the relay validates and persists thread
ancestry, the depth cap, the broadcast-visibility rule that keeps ordinary
replies off the main channel timeline, the transactional counter-increment
rule, the composite-cursor pagination constraint, and the live kind:39005
summary-overlay mechanism. It also states which clients (SDK, CLI, desktop)
implement the same root/reply interpretation.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The single reply act (composing/sending one reply) | `capabilities/messaging/reply.md` (not yet merged) |
| Reply/descendant counter mechanics as their own subject, including delete-time decrement | `capabilities/messaging/thread-counters.md` (not yet merged) |
| The step-by-step ingestion sequence a threaded event travels through | `architecture-flows-event-ingestion` |
| The relay and Postgres containers' own internal architecture | `architecture-containers-relay`, `architecture-containers-postgres` |
| Any future NIP-22 (kind:1111) comment-threading surface for git-hosted issues | Not yet in this corpus; not implemented in this repository at the recorded revision |
| Forum-specific concerns beyond its shared use of the same threading mechanism (voting, forum post lifecycle) | Not yet in this corpus |

**Expected but not verified when this node was written:**

- **No live relay/Postgres run was exercised while authoring this node.**
  Every behavioral claim above is grounded in reading the source directly
  (SDK, relay, buzz-db, CLI, desktop) and in the `#[ignore]`-marked test
  bodies' own assertions, not in running `just test` against a live
  database during authoring.
- **Whether `capabilities-messaging-reply` or `capabilities-messaging-thread-counters`
  will validate cleanly against this node's boundary claims once either
  merges was not checked**, since neither exists on `origin/launchpad` at
  the recorded revision. If either lands with a different boundary than this
  node assumes, this node's Boundary section is the place to reconcile it,
  not a silent edit to the other document.
- **Whether NIP-22 kind:1111 threading is genuinely planned as a distinct
  future capability, or the VISION_PROJECTS.md row is aspirational prose with
  no concrete build plan, was not established** -- only that it is unbuilt
  today. This node's INFERENCE entry on that row is rated 0.75, not 1.0, for
  that reason.
