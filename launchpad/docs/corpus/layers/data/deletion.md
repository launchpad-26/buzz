---
id: layers-data-deletion
type: layers
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - operator
evidence:
  - statement: "This node was authored and checked against repository revision 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5."
    entry_class: FACT
    evidence:
      - "commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
  - statement: "node.schema.json's type enum includes layers, the corpus-surface value for any node under launchpad/docs/corpus/layers/."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "NIP-09 kind:5 is Buzz's event deletion request kind, defined as KIND_DELETION = 5 with the doc comment \"NIP-09: Event deletion request.\""
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs:55-56"
  - statement: "NIP-29 defines two further deletion-shaped kinds Buzz implements: KIND_NIP29_DELETE_EVENT = 9005 (\"Delete an event from a group\") and KIND_NIP29_DELETE_GROUP = 9008 (\"Delete a group\")."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs:340-341"
      - "crates/buzz-core/src/kind.rs:344-345"
  - statement: "A kind:5/kind:9005 deletion request targeting an existing event is executed by soft_delete_event_and_update_thread, which runs `UPDATE events SET deleted_at = NOW() WHERE community_id = $1 AND id = $2 AND deleted_at IS NULL` inside a transaction that also decrements the target's thread reply/descendant counters; the row is not physically removed."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/event.rs:897-946"
  - statement: "A kind:9008 (delete group) request is executed by handle_delete_group, which calls soft_delete_channel; that function runs `UPDATE channels SET deleted_at = NOW() WHERE community_id = $1 AND id = $2 AND deleted_at IS NULL` and returns whether a row was actually changed."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/side_effects.rs:1886-1901"
      - "crates/buzz-db/src/store/channel.rs:609-650"
  - statement: "Ingest routes kind:5 and kind:9005/9008 events to this soft-delete side effect: handle_standard_deletion_event resolves each e-tagged target via get_event_by_id_including_deleted and calls soft_delete_event_and_update_thread per target, and the a-tag (addressable-event) deletion path is handled separately by handle_a_tag_deletion."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/side_effects.rs:2223-2266"
      - "crates/buzz-relay/src/handlers/side_effects.rs:2085"
  - statement: "Ordinary event reads filter on `deleted_at IS NULL` (for example get_last_message_at's query), while get_event_by_id_including_deleted deliberately bypasses that filter; its own doc comment states most callers should use get_event_by_id instead, and that the including-deleted variant \"is needed when the caller must distinguish 'never existed' from 'was deleted' (e.g. audit trails, compliance queries).\""
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/event.rs:947-971"
      - "crates/buzz-db/src/store/event.rs:1065-1088"
  - statement: "The events table has carried a deleted_at TIMESTAMPTZ column, and the index idx_events_community_deleted on (community_id, deleted_at), since the initial schema migration -- soft-deletion of individual events is not a later addition to the data layer."
    entry_class: FACT
    evidence:
      - "migrations/0001_initial_schema.sql:230"
      - "migrations/0001_initial_schema.sql:265"
  - statement: "buzz-deletion is described in its own Cargo.toml as a \"Durable whole-community deletion engine for Buzz\", and buzz-db's deletion.rs module doc states it \"owns request inventory, approval, claims, fencing, checkpoints, retries, tombstoning, and logical verification\" for that engine."
    entry_class: FACT
    evidence:
      - "crates/buzz-deletion/Cargo.toml:1-9"
      - "crates/buzz-db/src/store/deletion.rs:1-5"
  - statement: "The durable community-deletion lifecycle is a fixed, non-skippable stage sequence -- DeletionStage: Submitted, Inventoried, Approved, Fenced, Drained, BindingsRemoved, PostgresPurged, CachePurged, LogicallyVerified, RetentionPending, or the terminal Aborted -- and PURGE_SCOPED_TABLES names the foreign-key-safe child-before-parent order in which every community-scoped PostgreSQL table, including events, is physically purged once that lifecycle reaches PostgresPurged."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/deletion.rs:119-154"
      - "crates/buzz-db/src/store/deletion.rs:89-117"
  - statement: "Migration 0029's own header states the boundary of what whole-community deletion actually removes: \"The community row is never removed: it becomes the permanent name tombstone,\" and adds a deletion_state column to communities constrained to ('active', 'quiescing', 'fenced', 'tombstone') alongside deletion_fence_generation and deleted_at."
    entry_class: FACT
    evidence:
      - "migrations/0029_community_deletion.sql:1-16"
  - statement: "Migration 0029's own header additionally describes the engine as a \"Durable, CLI-only whole-community deletion control plane,\" and buzz-admin's deletions subcommand is a thin adapter that delegates directly to buzz_deletion::run -- the durable engine has no protocol-event trigger of its own, unlike kind:5/9005/9008."
    entry_class: FACT
    evidence:
      - "migrations/0029_community_deletion.sql:1"
      - "crates/buzz-admin/src/deletions.rs:1-8"
  - statement: "Soft-deletion (per-event, per-channel) and durable whole-community deletion are two deliberately separate mechanisms rather than two implementations of one idea, because they differ in every dimension that matters for a data-layer concept: trigger surface (any authorized user's signed protocol event vs. an operator's CLI command), blast radius (one event or channel vs. every community-scoped row across PostgreSQL, Redis and object storage), and physical effect (a single UPDATE ... SET deleted_at vs. a staged, fenced, checkpointed purge)."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-db/src/store/event.rs:897-946"
      - "crates/buzz-relay/src/handlers/side_effects.rs:1886-1901"
      - "crates/buzz-db/src/store/deletion.rs:89-154"
      - "migrations/0029_community_deletion.sql:1"
    confidence: 0.75
  - statement: "At the recorded revision, no other child task in Feature #610's 42-document batch (#1060-#1101) is scoped to the whole-community deletion engine specifically; #1100 (layers/data/retention.md) and #1072 (layers/data/object-storage/retention.md) are named for time-based expiry, a distinct concept from deletion triggered on request."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#610 child-issue list and #1100/#1072/#1062 titles, read directly while authoring this node"
relationships:
  - type: references
    target: architecture-containers-postgres
  - type: references
    target: architecture-containers-relay
---

# Deletion

**Deletion is making data stop being returned by Buzz's data layer, by one of two
distinct mechanisms depending on scope: soft-deleting a single event or channel, or
durably purging an entire community.**

Those two mechanisms are documented in full below. Neither is a lesser version of
the other -- they answer different questions at different scales, and "deletion"
in Buzz always means one or the other, never a single unified operation.

## Definition

**Soft-deletion** marks a single row -- one event, one channel -- as gone by setting
its `deleted_at` timestamp, without removing it from PostgreSQL. Ordinary queries
filter on `deleted_at IS NULL` and never see it again; the row itself, including its
original `content`, remains physically present and can still be read back by a
caller that explicitly asks for deleted rows (audit and compliance paths do this).
It is triggered by a signed Nostr protocol event -- NIP-09's kind:5 (event
deletion) or NIP-29's kind:9005 (delete an event from a group) and kind:9008
(delete a group) -- arriving through ordinary event ingestion, the same pipeline
every other event goes through.

**Durable whole-community deletion** is a different operation at a different
scale: the staged, fenced, checkpointed, auditable physical purge of every
community-scoped row across PostgreSQL, Redis, and object storage for one entire
tenant. It has no protocol-event trigger -- it is invoked only through the
`buzz-admin deletions` CLI, which delegates directly to the `buzz-deletion` crate's
engine. It does not soft-delete; by the time it reaches its `PostgresPurged` stage
it physically removes rows (see `PURGE_SCOPED_TABLES`, which includes `events`
itself), and it is deliberately difficult to trigger or reverse. The one row it
*never* removes is the `communities` row -- that row becomes a permanent tombstone
recording that the name was once in use, so the host can never be silently reused
by a different tenant.

**What this document is not about.** It does not cover time-based data expiry
(TTL/retention policies that remove data on a schedule rather than on request --
that is a separate concept, `layers/data/retention.md`), and it does not restate
the durable engine's full stage-by-stage mechanics (that is reference-shaped
material for a future reference-typed node, not this concept node).

## Background

Buzz's data layer draws this two-mechanism line because the two operations sit at
genuinely different trust boundaries. Any user with an event they are entitled to
delete can sign a kind:5 request, and any moderator entitled to remove a group can
sign a kind:9008 request -- these are ordinary, frequent, self-service actions
scoped to one row, and they need to be fast and reversible-in-storage (the data is
still there for audit until something else removes it). Erasing an entire
community's data, by contrast, is an operator action with no self-service path: it
is destructive, affects every table and every store the tenant ever wrote to, and
is exactly the kind of action that benefits from being slow, staged, and hard to
run by accident -- hence a lifecycle with ten ordered stages (`Submitted` through
`RetentionPending`, or a terminal `Aborted`) rather than a single UPDATE statement.

## Use cases

- **An agent or developer tracing what happened to a message** needs to know that
  a missing event is not necessarily gone -- it may be soft-deleted (visible via
  `get_event_by_id_including_deleted`, still present in the `events` table) or it
  may belong to a community that has completed the durable deletion lifecycle (in
  which case the row is truly gone and only the community's tombstone remains).
  These have different implications for what can still be recovered.
- **An operator retiring a customer's community** needs to know that community
  deletion is a CLI-only, multi-stage process they must explicitly submit,
  inventory, and approve -- not something that happens as a side effect of any
  protocol event -- and that the community's host name is permanently reserved
  once the tombstone is written, so it can never be reused.
- **Anyone implementing a new deletion-adjacent feature** needs to know which of
  the two mechanisms it is extending, because they have incompatible guarantees:
  adding a new soft-deletable table does not automatically make it part of the
  durable engine's scoped-table inventory, and vice versa.

## Comparison

| | Soft-deletion (events, channels) | Durable whole-community deletion |
|---|---|---|
| Trigger | Signed Nostr event: kind:5, kind:9005, kind:9008 | `buzz-admin deletions` CLI only -- no protocol event |
| Scope | One event or one channel | Every community-scoped row in PostgreSQL, Redis, and object storage |
| Mechanism | `UPDATE ... SET deleted_at = NOW()` | Staged `DeletionStage` lifecycle: Submitted → Inventoried → Approved → Fenced → Drained → BindingsRemoved → PostgresPurged → CachePurged → LogicallyVerified → RetentionPending (or Aborted) |
| Physical effect | Row stays; excluded from normal reads by `deleted_at IS NULL` | Row physically removed once `PostgresPurged` is reached |
| What survives | The row itself, including content, for audit/compliance reads | Only the `communities` row, permanently marked as a tombstone |

## Related resources

- `architecture-containers-postgres` -- both mechanisms are implemented as
  PostgreSQL state: `deleted_at` columns and their supporting index for
  soft-deletion, and the `community_deletion_requests` control-plane tables plus
  the physical `PURGE_SCOPED_TABLES` purge for the durable engine.
- `architecture-containers-relay` -- the relay's ingest pipeline is what routes an
  incoming kind:5/9005/9008 event to the soft-deletion side effect; the durable
  engine bypasses the relay's serving path entirely and runs through `buzz-admin`
  instead.

## Scope and omissions

**This document covers** what "deletion" means in Buzz's data layer, the two
distinct mechanisms that implement it, why they are kept separate, and the
representative situations where the distinction matters.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Time-based data expiry / TTL and retention policy | `layers/data/retention.md` (issue #1100, unmerged) and `layers/data/object-storage/retention.md` (issue #1072, unmerged) |
| The durable deletion engine's full field-by-field state-machine mechanics (approval digests, fencing, checkpoints, lease tokens) | A future reference-typed node, not yet templated at this revision |
| Whether moderation-driven content redaction (as distinct from full row soft-deletion) exists as a third mechanism | Not inspected this session -- expected but not verified |
| The broader data lifecycle a piece of data moves through before deletion becomes relevant | `layers/data/data-lifecycle.md` (issue #1062, unmerged) |

**No relationship to a retention or data-lifecycle node.** Checked before omitting
it rather than assuming: at the recorded revision `origin/launchpad`'s corpus tree
carries no `layers/` node at all, so neither `layers/data/retention.md` nor
`layers/data/data-lifecycle.md` has a resolvable id yet. The edges named above in
*Scope and omissions* are the likely future ones once those sibling tasks merge.

**Expected but not verified when this node was written:**

- **Whether moderation actions (bans, content takedowns) drive a third, distinct
  deletion-adjacent path** through the `moderation_actions` / `moderation_reports`
  tables visible in `PURGE_SCOPED_TABLES`, beyond the two mechanisms described
  above. Those tables were seen in the purge-order list but not opened this
  session.
- **Whether object-storage (Blossom/S3) media bound to a soft-deleted event is
  also removed**, or only community-scoped media is removed (via the durable
  engine's `BindingsRemoved` stage). The durable engine's storage-manifest
  freezing was read structurally; the soft-deletion path's interaction with
  object storage was not traced this session.
