---
id: capabilities-messaging-thread-counters
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
  - statement: "The thread_metadata table carries reply_count and descendant_count as INT NOT NULL DEFAULT 0 columns, keyed on (community_id, event_created_at, event_id), alongside parent_event_id, root_event_id, depth and last_reply_at."
    entry_class: FACT
    evidence:
      - "migrations/0001_initial_schema.sql"
  - statement: "insert_event_with_thread_metadata_tx inserts the event and, only when the event row was newly inserted (ON CONFLICT DO NOTHING on the events table) and thread metadata was supplied, inserts the thread_metadata row (also ON CONFLICT DO NOTHING) and -- only if that metadata row was itself newly inserted -- increments the parent's reply_count and, when a root is present, the root's descendant_count, creating stub thread_metadata rows for a parent or root that has none yet; all of this runs inside the one transaction insert_event_with_thread_metadata wraps, so a duplicate event can never double-increment a counter and a crash between the event insert and the counter update cannot happen."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/event.rs"
  - statement: "soft_delete_event_and_update_thread performs the symmetric decrement: it soft-deletes the event (UPDATE events SET deleted_at = NOW() ... WHERE deleted_at IS NULL) and, only when that update actually changed a row and a parent_event_id was supplied, decrements the parent's reply_count and the root's descendant_count with GREATEST(count - 1, 0) floors, all inside one transaction with the delete."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/event.rs"
  - statement: "Both of the relay's NIP-09 deletion paths -- the direct e-tag deletion handler and the standard multi-target deletion loop -- look up the target's parent/root via get_thread_metadata_by_event and then call soft_delete_event_and_update_thread with those ids before treating the delete as applied, and on success both push a fresh live-thread-summary overlay for the affected root."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/side_effects.rs"
  - statement: "buzz-db/src/thread.rs additionally defines standalone increment_reply_count and decrement_reply_count functions, and buzz-db/src/lib.rs exposes the latter as a Db facade method, but neither the standalone increment_reply_count nor any caller of the decrement_reply_count facade method appears anywhere in the ingest or deletion handlers; the production increment/decrement path is the transactional logic inlined in event.rs's insert_event_with_thread_metadata_tx and soft_delete_event_and_update_thread, not these standalone functions. thread.rs's own doc comment on increment_reply_count says as much: it exists for a future re-parenting use case, not the current write path."
    entry_class: FACT
    evidence:
      - "grep(pattern='\\.decrement_reply_count\\(', scope='crates/**/*.rs') -> only the definition sites in buzz-db/src/thread.rs and buzz-db/src/lib.rs, no call site, run against this node's recorded revision"
      - "crates/buzz-db/src/store/thread.rs"
  - statement: "get_thread_summary reads reply_count, descendant_count and last_reply_at for one event_id from thread_metadata, plus up to 10 distinct participant pubkeys for that root ordered by most recent activity, in a second query."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/thread.rs"
  - statement: "get_channel_window LEFT JOINs thread_metadata onto each top-level row of a channel page, so reply_count/descendant_count/last_reply_at come back with the page itself rather than one query per root, and batches the same 10-participant-per-root lookup for every row in the page with thread activity in a single additional query rather than one per root."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/thread.rs"
  - statement: "get_thread_replies -- the paginated per-reply subtree read used to render an open thread -- returns ThreadReply rows with no embedded ThreadSummary at all; reply_count and descendant_count are only attached to the top-level channel-window read (get_channel_window) and the single-event summary read (get_thread_summary), not to the subtree-of-replies read."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/thread.rs"
  - statement: "KIND_THREAD_SUMMARY is 39005, a parameterized-replaceable (NIP-33) kind; emit_live_thread_summary re-reads the current reply_count, descendant_count, last_reply_at and participants fresh from thread_metadata (not incremented client-side or in memory) after a thread mutation and publishes a relay-signed kind:39005 event carrying them as JSON content, tagged with the root's e/d id and the channel's h tag; this overlay is fan-out only and is never persisted, so a client that was not subscribed at the moment it was published never sees it and must refetch the channel window instead."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
      - "crates/buzz-relay/src/handlers/side_effects.rs"
  - statement: "The channel-window HTTP bridge endpoint signs and returns the same kind:39005 overlay shape, one per window row that carries a thread_summary, but only when the request opts in via an include_summaries extension flag."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs"
  - statement: "test_reply_ingest_pushes_live_thread_summary sends a root message, subscribes to kind:39005 scoped to the channel, sends a reply, and asserts a live 39005 overlay event arrives -- an end-to-end exercise of the increment-then-emit path over the real WebSocket protocol, not a unit test of thread.rs in isolation."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/e2e_relay.rs"
  - statement: "The desktop client parses reply_count and descendant_count directly off both the channel-window response and the forum API's thread_summary payload into its own replyCount/descendantCount fields; buzz-cli's messages.rs, by contrast, contains no reference to either field name, so the CLI's thread-reading commands were not confirmed to surface these two counters to an agent caller."
    entry_class: FACT
    evidence:
      - "desktop/src/features/messages/lib/channelWindowResponse.ts"
      - "desktop/src/shared/api/forum.ts"
  - statement: "Root AGENTS.md's own Key Patterns section states, as a documented invariant rather than an incidental detail: 'reply_count and descendant_count are materialized on thread root events. Any code that inserts replies must update these counters -- check existing reply handlers for the pattern.'"
    entry_class: FACT
    evidence:
      - "AGENTS.md"
  - statement: "The already-merged corpus flow node architecture-flows-event-ingestion independently documents the same insert_event_with_thread_metadata mechanism as one step of the event-ingestion flow, citing crates/buzz-db/src/event.rs directly for the claim that a duplicate event's thread counters are never double-incremented because dedupe and the counter update share one transaction."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/flows/event-ingestion.md"
  - statement: "At the recorded revision, git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus lists architecture-flows-event-ingestion, architecture-containers-postgres and architecture-containers-relay among its loaded nodes, and lists no capabilities/ node at all, so this is the first node under type: capabilities the corpus will carry; the three references declared below all resolve against that merge target."
    entry_class: FACT
    evidence:
      - "git_ls_tree(ref='origin/launchpad', path='launchpad/docs/corpus') -> includes architecture/flows/event-ingestion.md (id architecture-flows-event-ingestion), architecture/containers/postgres.md (id architecture-containers-postgres), architecture/containers/relay.md (id architecture-containers-relay); no capabilities/ path present; run against commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
  - statement: "This node's maturity claim of shipped rests on the transactional increment/decrement logic in event.rs, the schema in migrations/0001_initial_schema.sql, and the end-to-end e2e_relay.rs test, all opened directly for this node, rather than on any VISION document's status table -- VISION_PROJECTS.md's own Status table lists capabilities at a coarser grain (for example 'Channels, forums, DMs, canvases') and does not itemize thread counters as a row of its own."
    entry_class: INFERENCE
    evidence:
      - "VISION_PROJECTS.md"
      - "migrations/0001_initial_schema.sql"
      - "crates/buzz-db/src/store/event.rs"
      - "crates/buzz-test-client/tests/e2e_relay.rs"
    confidence: 0.9
  - statement: "Issue #780's definition of done, under parent PRD #612, requires this node to state the capability and primary actors/outcomes, define behavioral rules/constraints/variants, link major flows/interfaces/data/platform implementation, and link verification demonstrating the capability -- the capability-template shape rather than the flow-template shape."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#780 definition of done"
relationships:
  - type: references
    target: architecture-flows-event-ingestion
  - type: references
    target: architecture-containers-postgres
  - type: references
    target: architecture-containers-relay
---

# Thread counters: capability

Buzz keeps a running, materialized count of how many replies a message has
received and how deep its conversation has grown, so a user or agent looking
at a channel window can see reply activity on a root message without opening
the thread, and can watch that count update live while the thread is open.
Two numbers make up the capability: `reply_count` (direct replies to one
message) and `descendant_count` (every reply anywhere below the message, at
any nesting depth). Both are attached to the message that is their subject --
a root message carries counters describing its own thread, and any reply that
itself has children carries its own `reply_count` too, independent of the
root's.

## Maturity

**Shipped.** The `thread_metadata` table's `reply_count` and
`descendant_count` columns are defined in the initial schema migration
(`migrations/0001_initial_schema.sql`) with no later migration altering their
shape. The increment path is inlined in
`insert_event_with_thread_metadata_tx` (`crates/buzz-db/src/event.rs`) inside
the same transaction as the event insert, and the decrement path is inlined
symmetrically in `soft_delete_event_and_update_thread` in the same file,
called from both of the relay's NIP-09 deletion handlers
(`crates/buzz-relay/src/handlers/side_effects.rs`). An end-to-end test,
`test_reply_ingest_pushes_live_thread_summary`
(`crates/buzz-test-client/tests/e2e_relay.rs`), exercises the whole path over
the real WebSocket protocol: send a root, subscribe to the live overlay kind,
send a reply, and observe the overlay arrive with the updated counts. The
desktop client is a real, wired-up consumer of both counters
(`desktop/src/features/messages/lib/channelWindowResponse.ts`,
`desktop/src/shared/api/forum.ts`).

## Boundary

This node does not describe:

- **How the capability is built.** The `thread_metadata` table lives in
  Postgres -- see the `architecture-containers-postgres` node for the
  container that hosts it -- and the increment/decrement/live-emit logic
  lives inside the relay process -- see `architecture-containers-relay`.
  This node states what the counters are and do, not the storage engine or
  process topology underneath them.
- **The interface(s) this capability is exposed through.** A read of the
  counters currently reaches a caller through the channel-window HTTP bridge
  endpoint's `include_summaries` extension flag
  (`crates/buzz-relay/src/api/bridge.rs`) and through the relay-signed
  kind:39005 live overlay event over WebSocket
  (`crates/buzz-relay/src/handlers/side_effects.rs`). No corpus node yet
  documents either of those as a named interface, so this node cites the code
  directly rather than a boundary node that does not exist.
- **The step-by-step flow the counters participate in.** Incrementing on a
  new reply is one step inside the broader event-ingestion flow, already
  documented at `architecture-flows-event-ingestion`. Decrementing on a
  NIP-09 delete has no dedicated flow node in the corpus at this revision; this
  node names the deletion code path directly (`side_effects.rs`'s two
  deletion handlers) rather than asserting a flow node that does not exist.
- **How the running system is operated.** Nothing here covers deployment,
  monitoring, or incident response for the tables or processes involved.
- **Reactions, broadcast flags, or any other per-message counter or metadata
  field.** `thread_metadata` also carries `depth`, `broadcast` and
  `last_reply_at`; this node is scoped to the two counter fields and their
  behavior, not to the row's other columns.
- **Whether `buzz-cli` surfaces these counters to an agent caller.** Checked
  and found absent at this revision -- see *Scope and omissions* below.

## Relationships

- references: `architecture-flows-event-ingestion` -- the flow this
  capability's increment step is part of.
- references: `architecture-containers-postgres` -- the datastore
  `thread_metadata` lives in.
- references: `architecture-containers-relay` -- the process that owns the
  increment, decrement and live-emit logic.

## Scope and omissions

**This node covers** what `reply_count` and `descendant_count` are, where they
live, how each is incremented and decremented and under what transactional
guarantee, which read paths return them and which do not, how a live update
reaches a subscribed client without a refetch, which client is a confirmed
consumer, and the standalone counter-mutation functions that exist in the
codebase but are not the ones actually wired into the production write path.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| How the capability is built (container, technology, process topology) | `architecture-containers-postgres`, `architecture-containers-relay` |
| The interface contract for reading or subscribing to the counters | no interface node exists yet in the corpus at this revision |
| The step-by-step ingestion flow the increment is one step of | `architecture-flows-event-ingestion` |
| The step-by-step deletion flow the decrement is one step of | no dedicated flow node exists yet in the corpus at this revision |
| How the running system is operated | the `operations` corpus surface |
| The front-matter contract itself | `launchpad/docs/corpus/schema/node.schema.json` |
| Creating, updating and retiring a node procedurally | `launchpad/docs/corpus/AGENTS.md` |

**Expected but not verified when this node was written:**

- **Whether `buzz-cli`'s `messages thread` / `resolve_thread_ref` commands
  surface `reply_count` or `descendant_count` to an agent caller was checked
  and found negative** (`crates/buzz-cli/src/commands/messages.rs` contains no
  reference to either field name at this revision), but the command's full
  output shape was not read line-by-line beyond that grep -- only that the
  two literal field names are absent.
- **Whether desktop actually renders the two counters in a visible badge or
  affordance was not checked.** Only the API-parsing layer
  (`channelWindowResponse.ts`, `forum.ts`) was confirmed to receive and
  rename the fields; no UI component was opened.
- **Whether any capability node this one should sit `part-of` -- a broader
  "messaging" or "channels" capability -- exists or is planned was not
  established.** No such node is present in the corpus at this revision, so
  no `part-of` relationship is declared; one may become appropriate once a
  broader messaging-capability node is drafted.
- **The standalone `increment_reply_count` function and the
  `decrement_reply_count` Db facade method's absence of call sites was
  established by a repository-wide grep for their exact call syntax, not by
  reading every file that imports `buzz_db::thread` or the `Db` facade type**,
  so an indirect call reached through a trait object or a re-export using a
  different call syntax would not have been found by that grep.
