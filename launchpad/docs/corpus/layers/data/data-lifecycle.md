---
id: layers-data-data-lifecycle
type: layers
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
  - statement: "insert_event rejects a kind:22242 NIP-42 AUTH event outright, and rejects any event whose kind falls in the ephemeral range (20000-29999), so ephemeral events never become durable and never enter the lifecycle described here at all."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/event.rs:282-286"
      - "crates/buzz-core/src/kind.rs:768-771"
      - "crates/buzz-core/src/kind.rs:457-459"
  - statement: "A regular (non-replaceable) Nostr event, once accepted by insert_event, is identified by its own content-addressed id and is not itself mutated again -- the only state that later changes on its row is deleted_at."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/event.rs:273-329"
  - statement: "Replaceable (kinds 0, 3, 41, 10000-19999) and parameterized-replaceable (kinds 30000-39999) events are handled by a distinct write path, replace_parameterized_event, keyed on kind+pubkey(+d-tag) rather than on event id, because a newer version for the same coordinate supersedes the current live head."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs:773-778"
      - "crates/buzz-db/src/lib.rs:5155-5251"
  - statement: "By default, replace_parameterized_event soft-deletes the previously live row for a coordinate as it accepts the newer one -- the superseded version is tombstoned, not physically removed."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-db/src/lib.rs:5216-5251"
    confidence: 0.75
  - statement: "A NIP-09 kind:5 deletion event and a NIP-29 kind:9005 delete-event command both name their target by an e tag (regular/replaceable event id) or an a tag (addressable/parameterized-replaceable coordinate), and Buzz's own ingest validation requires exactly one such reference."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:2475-2489"
  - statement: "The relay's side-effect dispatch table routes kind:5 to handle_standard_deletion_event and kind:9005 to handle_delete_event_side_effect; both ultimately soft-delete the target -- by id via soft_delete_event_and_update_thread for an e-tag target, or by coordinate via soft_delete_by_coordinate for an a-tag target -- never by physically removing the row."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/side_effects.rs:198-206"
      - "crates/buzz-relay/src/handlers/side_effects.rs:2223-2268"
      - "crates/buzz-relay/src/handlers/side_effects.rs:2085-2184"
      - "crates/buzz-db/src/event.rs:793-799"
      - "crates/buzz-db/src/event.rs:838-862"
  - statement: "Soft-deleting an event sets its deleted_at timestamp; every ordinary read path filters on deleted_at IS NULL, so a soft-deleted event is invisible to every query built on those paths even though its row is still physically present."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/event.rs:788-799"
      - "crates/buzz-db/src/event.rs:986-988"
  - statement: "get_event_by_id_including_deleted is the deliberate escape hatch that returns a soft-deleted row anyway, documented as existing for callers that must distinguish 'never existed' from 'was deleted' -- for example audit trails and compliance queries -- which is the concrete case a moderator or reviewer relies on when re-inspecting a deleted message."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/event.rs:1032-1037"
  - statement: "A soft-deleted event's row is retained by default with no general sweep that later removes it; the tombstone is the terminal state for an individual event outside of the two narrow exceptions and the whole-community purge described below."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-db/src/event.rs:793-799"
      - "migrations/0019_mesh_status_retention.sql"
      - "migrations/0009_nip_rs_database_guards.sql"
    confidence: 0.7
  - statement: "Exactly two narrow coordinate shapes are hard-purged (DELETE FROM events, not merely soft-deleted) the instant they are superseded or soft-deleted, rather than being retained as a tombstone: kind:30078 NIP-RS read-state markers matching a 'read-state:<32-hex>' d-tag, and kind:30003 buzz-mesh-member-status heartbeats matching a 'buzz-mesh-member-status:' d-tag -- confirmed by grepping migrations/ for purge_soft_deleted, not assumed to be exhaustive across the whole codebase."
    entry_class: FACT
    evidence:
      - "migrations/0019_mesh_status_retention.sql"
      - "migrations/0009_nip_rs_database_guards.sql"
      - "crates/buzz-db/src/lib.rs:5200-5216"
  - statement: "The mesh-status migration states its own reason for the hard-purge exception directly: 'Only the live head has product value; retaining every superseded 45-second payload creates unbounded physical history.' The NIP-RS migration states the equivalent reason: 'NIP-RS payloads have no historical product value.'"
    entry_class: FACT
    evidence:
      - "migrations/0019_mesh_status_retention.sql:1-4"
      - "migrations/0009_nip_rs_database_guards.sql:74-76"
  - statement: "An ephemeral channel carries a ttl_deadline that is refreshed forward on every new event durably written into it, via a deferred, per-channel-locked trigger; a channel with ttl_seconds set to NULL (a permanent channel) is never touched by this trigger."
    entry_class: FACT
    evidence:
      - "migrations/0024_event_ttl_refresh_shared_lock.sql"
  - statement: "A background reaper task, started at relay boot and running on a fixed interval (default 60 seconds, overridable via BUZZ_REAPER_INTERVAL_SECS), archives -- sets archived_at, does not delete -- every ephemeral channel whose ttl_deadline has passed; this is idempotent across concurrently running relay pods because the update is guarded on archived_at IS NULL."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/channel.rs:1498-1531"
      - "crates/buzz-relay/src/main.rs:635-667"
  - statement: "Channel-level TTL reaping is orthogonal to an individual event's own soft-delete state: reaping acts on the channel container based on inactivity, not on any single event's deleted_at, and archiving a channel does not itself soft-delete the events inside it."
    entry_class: INFERENCE
    evidence:
      - "migrations/0024_event_ttl_refresh_shared_lock.sql"
      - "crates/buzz-db/src/channel.rs:1498-1531"
    confidence: 0.7
  - statement: "A whole-community deletion is a separate, durable, multi-stage lifecycle with its own fixed stage order and no backwards or skipping transitions: Submitted, Inventoried, Approved, Fenced, Drained, BindingsRemoved, PostgresPurged, CachePurged, LogicallyVerified, RetentionPending -- or Aborted, only before the irreversible point."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/deletion.rs:1-5"
      - "crates/buzz-db/src/deletion.rs:119-177"
  - statement: "The PostgresPurged stage of a whole-community deletion physically removes every row in every tenant-scoped table listed in PURGE_SCOPED_TABLES, in a foreign-key-safe child-before-parent order -- including the events table (so tombstoned rows are finally erased, not merely soft-deleted a second time) and the audit_log table itself. A fixed set of control-plane tables (the deletion request's own bookkeeping) is explicitly exempted and survives the purge."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/deletion.rs:42-117"
  - statement: "The audit log is described in its own module as an append-only, per-community hash-chain audit log; nothing in the per-event soft-delete path (kind:5/kind:9005 handling) touches audit_log, so an individual event's deletion does not remove or alter the audit entries recording it. The audit log is purged only as part of a whole-community deletion's PostgresPurged stage."
    entry_class: FACT
    evidence:
      - "crates/buzz-audit/src/service.rs:32-38"
      - "crates/buzz-db/src/deletion.rs:59-117"
  - statement: "The relay's hourly S3 storage sweep (storage_sweep.rs) is a usage-metrics listing job that classifies and counts objects for observability dashboards; it does not delete, expire, or otherwise mutate any stored object, and is not part of the deletion lifecycle described in this node."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/storage_sweep.rs:1-17"
  - statement: "Media storage (Blossom/S3-backed) has its own delete operation distinct from the Postgres event lifecycle, but its full retention behavior beyond that delete function was not inspected when this node was written and is deliberately left as a gap rather than described here."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-media/src/storage.rs"
    confidence: 0.5
---

# Data lifecycle

**Data lifecycle** is the sequence of phases a piece of tenant-owned data in Buzz --
principally a stored Nostr event, and the channel and community containers that hold
it -- passes through in the relay's own storage, from the moment it is accepted for
durable storage to the moment nothing in the system can observe it any more. It names
the shared shape connecting several mechanisms that, read individually, look like
separate features: soft-deletion on a moderation or NIP-09 request, supersession of a
replaceable event, TTL-driven archiving of an ephemeral channel, and the durable
whole-community deletion procedure. This node's job is to name that shape and the
boundary between its phases, not to duplicate any one mechanism's own implementation
detail.

**What this is not.** It is not the schema of the `events`, `channels`, or
`audit_log` tables (a reference-shaped node, not yet written). It is not a
step-by-step runbook for operating a whole-community deletion request (a
procedure-shaped node, not yet written). It is not a description of media-specific
(Blossom/S3) retention policy beyond noting that storage has its own delete path,
separate from the Postgres event lifecycle. And it is not the S3 usage-metrics sweep
(`storage_sweep.rs`), which lists and counts objects for dashboards on an hourly
cadence and deletes nothing -- a mechanism easy to mistake for a retention job from
its name alone, which is precisely why the boundary is stated here explicitly.

## Background: the phases

1. **Ingestion.** `insert_event` is where a signed Nostr event becomes durable.
   Two categories never make it past this point at all: a NIP-42 `AUTH` event, and
   any event whose kind falls in the ephemeral range (20000-29999). Neither is ever
   written to the `events` table, so neither has a lifecycle to describe -- ephemeral
   events, by NIP-01's own definition, are never meant to be stored.

2. **Live.** Once accepted, a regular event is identified by its own content-addressed
   id and is not mutated again as content -- the only thing that later changes on its
   row is `deleted_at`. Replaceable and parameterized-replaceable events (identified by
   `kind`+`pubkey`, optionally `+d-tag`) instead go through a distinct write path,
   `replace_parameterized_event`, because a newer version for the same coordinate
   supersedes whichever version was previously live.

3. **Deletion request.** A NIP-09 `kind:5` deletion event or a NIP-29 `kind:9005`
   delete-event command names its target by an `e` tag (a specific event id) or an
   `a` tag (an addressable/parameterized-replaceable coordinate). Both kinds are
   routed to a soft-delete: the target's `deleted_at` is set to the current time. The
   row is not removed -- it becomes a tombstone. Every ordinary read filters on
   `deleted_at IS NULL`, so a tombstoned event disappears from every normal query, but
   a dedicated function (`get_event_by_id_including_deleted`) exists specifically for
   callers -- audit trails, compliance review, undelete tooling -- that must still tell
   "never existed" apart from "was deleted."

4. **Tombstone retention.** By default, a soft-deleted event's row is kept
   indefinitely. Nothing in the general path sweeps it away later; the tombstone is
   the resting state for the overwhelming majority of deleted data, until either the
   narrow exception below applies or the whole-community purge (phase 7) eventually
   reaches it.

5. **The narrow immediate hard-purge exception.** Exactly two coordinate shapes break
   the "tombstone and keep" default: `kind:30078` NIP-RS read-state markers, and
   `kind:30003` `buzz-mesh-member-status` heartbeats. For both, the moment the row is
   superseded or soft-deleted, a database trigger physically deletes it
   (`DELETE FROM events`) instead of leaving a tombstone. Both migrations state their
   own reason in almost the same words: a mesh-status heartbeat fires roughly every 45
   seconds and "only the live head has product value," and a NIP-RS payload "has no
   historical product value" at all -- retaining a tombstone for every superseded write
   of either would be unbounded physical growth with nothing to show for it. This is a
   deliberate, hardcoded exception for two specific kinds, not a general policy any new
   high-churn kind gets automatically.

6. **Container-level TTL (channels), orthogonal to event deletion.** An *ephemeral*
   channel (one with `ttl_seconds` set) carries a `ttl_deadline` that is pushed further
   into the future every time a new event is durably written into it. A background
   reaper task, running on a fixed interval (60 seconds by default), archives --
   `archived_at`, not deletion -- any ephemeral channel whose deadline has passed. This
   bounds how long an inactive ephemeral channel exists as a container; it says nothing
   about whether any individual event inside it has itself been deleted, and a
   permanent channel (`ttl_seconds IS NULL`) is never touched by this mechanism at all.

7. **Whole-community purge -- the terminal case.** Deleting an entire community is a
   separate, durable, multi-stage lifecycle of its own, with a fixed stage order and
   no backwards or skipping transitions: `Submitted -> Inventoried -> Approved ->
   Fenced -> Drained -> BindingsRemoved -> PostgresPurged -> CachePurged ->
   LogicallyVerified -> RetentionPending`, with `Aborted` reachable only before the
   irreversible point. Its `PostgresPurged` stage physically removes every row in
   every tenant-scoped table -- including `events` (so a tombstone finally becomes
   gone, not merely soft-deleted again) and `audit_log` itself -- in a
   foreign-key-safe order, alongside a parallel purge of tenant-owned object storage
   and the Redis cache namespace. This is where the "retained indefinitely" default
   from phase 4 finally ends, and the only place it ends for most data.

8. **The audit log's own exception.** The audit log is an append-only,
   per-community hash chain. Nothing in the per-event soft-delete path touches it --
   deleting a message does not remove or alter the audit entry that recorded the
   deletion. It is purged only as part of phase 7's `PostgresPurged` stage, never by
   any individual event's own lifecycle.

## Use cases

- **"Is this data actually gone?"** is the question this concept exists to answer
  honestly. A moderator's `kind:9005` delete, or a user's own `kind:5` deletion
  request, makes content disappear from every ordinary query -- but the row still
  exists, still occupies storage, and is still reachable through
  `get_event_by_id_including_deleted`. Only a whole-community purge, or the two named
  hard-purge exceptions, physically erases a row.

- **Designing a new high-churn parameterized-replaceable kind.** Anyone adding a kind
  that writes a fresh coordinate version frequently (a heartbeat, a live-cursor, a
  presence marker) needs to know the default behavior is tombstone-and-keep-forever
  for every superseded version, and that opting into the narrow hard-purge convention
  today means adding the kind to the same hardcoded exception list `kind:30078` and
  `kind:30003` already use -- there is no general flag for it yet.

- **Reasoning about channel lifecycle versus event lifecycle.** These are two
  independent mechanisms that are easy to conflate because both use the word
  "expire." A channel being archived by the TTL reaper says nothing about whether the
  messages inside it have been deleted; an event being soft-deleted says nothing
  about the channel's own TTL state.

- **Auditing a data-retention or compliance claim.** A reviewer checking "how long is
  deleted content actually retained" needs the full chain above, not just the
  soft-delete step: the honest answer is "indefinitely, as an invisible tombstone,
  until the whole-community purge -- except for two named kinds, which are purged
  immediately."

## Scope and omissions

**This document covers** the shared phase structure connecting event ingestion,
supersession, soft-deletion, the narrow hard-purge exception, channel-level TTL
reaping, and whole-community purge -- and the boundary against the S3 usage-metrics
sweep, which is not part of this lifecycle despite the similar name.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The exact schema of the `events`, `channels`, and `audit_log` tables | A reference-shaped node, not yet written |
| The step-by-step operational procedure for running a whole-community deletion request | A procedure-shaped node, not yet written |
| Media (Blossom/S3) retention and deletion behavior beyond noting that a separate delete operation exists | Not yet written |
| Whether the workflow engine's own scheduled/ephemeral execution state follows this same lifecycle shape | Not inspected this session |

**Expected but not verified when this node was written:**

- **Whether any narrow hard-purge exception exists outside the `events` table** (for
  example in git storage, media metadata, or another table entirely) was not checked.
  Only `migrations/` was grepped for the `purge_soft_deleted` naming convention; a
  differently named mechanism elsewhere would not have been found by that search.
- **Whether an ephemeral channel's own events are ever swept once the channel is
  archived** was not verified. Only the archiving step itself (`archived_at`) was
  confirmed; whether anything downstream later soft-deletes or purges the channel's
  events as a consequence of archival was not traced.
- **Whether a superseded replaceable/parameterized-replaceable event is soft-deleted
  synchronously in the same transaction as the new version's insert, in every code
  path that calls `replace_parameterized_event`,** was read from one call site's logic
  rather than exhaustively traced across every caller; recorded as `INFERENCE`, not
  `FACT`, for that reason.
- **Media storage's full retention lifecycle** (`crates/buzz-media/src/storage.rs`)
  was located but not read in depth; only the existence of a `delete` operation
  distinct from the Postgres event path was confirmed.
