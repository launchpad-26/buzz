---
id: layers-data-postgres-channel-members-table
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
  - statement: "node.schema.json's type enum contains layers (among architecture, capabilities, platforms, implementation, interfaces-events, verification, operations, development, release, governance, agent, ingestion) and no dedicated table/entity value."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "This document's type is set to layers rather than data-entity.md's own suggested type: implementation for a real instance, matching the precedent every layers/data/... sibling node authored so far in this same batch (Feature #610) has used, per this task's own dispatch brief; this is a deliberate deviation from the template's own reasoning, disclosed here rather than silently followed or silently overridden."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "corpus-batch-author dispatch brief for issue #1077 (Feature #610), stating the type: layers precedent set by prior layers/data/... nodes in the same batch"
  - statement: "launchpad/docs/corpus/templates/data-entity.md requires six sections for a real instance node -- Identity, Attributes and shape, Invariants, Relationships to other entities, Provenance, and Storage pointer (not storage description) -- and states its own worked illustration (thread_metadata) is 'the clearest example already in this codebase' of a single Postgres table treated as one domain entity, the same shape this document follows for channel_members."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/templates/data-entity.md"
  - statement: "launchpad/docs/corpus/templates/datastore.md's own Schema/namespace-inventory section is explicitly a one-row-per-table structural list with a one-line purpose each, not a deep dive on a single table's identity, fields, invariants and relationships -- the boundary this document respects by following data-entity.md's shape instead."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/templates/datastore.md"
  - statement: "At the recorded revision, origin/launchpad's launchpad/docs/corpus tree carries no layers/ subtree at all, so no sibling layers/data/... node is a legal relationships target -- a relationships.target naming an id no loaded node carries is a hard validation error per AGENTS.md."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
  - statement: "migrations/0001_initial_schema.sql defines channel_members with columns community_id (UUID, references communities(id)), channel_id (UUID), pubkey (BYTEA), role (member_role enum, default 'member'), joined_at (TIMESTAMPTZ, default NOW()), invited_by (BYTEA, nullable), removed_at (TIMESTAMPTZ, nullable), removed_by (BYTEA, nullable), and hidden_at (TIMESTAMPTZ, nullable), with PRIMARY KEY (community_id, channel_id, pubkey) and a FOREIGN KEY (community_id, channel_id) REFERENCES channels (community_id, id) ON DELETE CASCADE, under a comment reading 'Conformance: \"Channels and channel membership\". PK leads with community_id.'"
    entry_class: FACT
    evidence:
      - "migrations/0001_initial_schema.sql"
  - statement: "migrations/0001_initial_schema.sql also creates a partial index idx_channel_members_pubkey ON channel_members (community_id, pubkey) WHERE removed_at IS NULL, immediately after the channel_members table definition, and defines the member_role enum as ('owner', 'admin', 'member', 'guest', 'bot')."
    entry_class: FACT
    evidence:
      - "migrations/0001_initial_schema.sql"
  - statement: "crates/buzz-core/src/channel.rs's MemberRole enum documents the role hierarchy as 'Owner > Admin > Member > Guest', with Bot as 'a separate designation -- it is not part of the linear hierarchy'; its is_elevated method returns true only for Owner and Admin, and its as_str method's string values ('owner', 'admin', 'member', 'guest', 'bot') match the database enum's members exactly."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/channel.rs"
  - statement: "crates/buzz-db/src/store/channel_members.rs's add_member function inserts or reactivates a row via INSERT ... ON CONFLICT (community_id, channel_id, pubkey) DO UPDATE SET removed_at = NULL, removed_by = NULL, role = EXCLUDED.role, so re-adding an already-removed member reuses the same primary-key row rather than creating a second one -- removal is a soft delete via removed_at/removed_by, not a row deletion."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/channel_members.rs"
  - statement: "crates/buzz-db/src/store/channel_members.rs's remove_member function sets removed_at = NOW(), removed_by = $1 (the actor's pubkey) on the matching row, guarded by a WHERE ... AND removed_at IS NULL clause, and returns DbError::MemberNotFound if no row matched -- confirming removal never deletes the row."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/channel_members.rs"
  - statement: "crates/buzz-db/src/store/channel_members.rs's add_member doc comment states role-enforcement rules: on open channels invited_by is optional and role is forced to Member for self-join; on private channels an invite requires an invited_by who is an active member or the channel creator bootstrapping their own first membership; and elevated roles (Owner, Admin) may only be granted by an existing owner or admin, even on open channels. A code comment in the same function states that reactivating a soft-removed row is deliberately keyed on the CURRENT active role, not the removed row's stored role, because 'inferring current authority from a removed row would make soft-deleted ownership a resurrection token.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/channel_members.rs"
  - statement: "crates/buzz-db/src/store/channel_members.rs's add_member and remove_member both guard against demoting or removing a channel's last owner: before a demotion or removal that would leave role = 'owner' AND removed_at IS NULL with a count of 1, both functions return DbError::AccessDenied rather than proceeding, and both acquire a per-channel advisory transaction lock (acquire_channel_membership_lock, via pg_advisory_xact_lock(hashtextextended(...))) as the first statement in their transaction specifically to serialize this check-then-write sequence against concurrent membership writes on the same channel."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/channel_members.rs"
  - statement: "crates/buzz-db/src/store/channel_members.rs's is_member and membership_pairs functions both define active membership as a row joined against channels ON channels.deleted_at IS NULL, filtered by channel_members.removed_at IS NULL -- an active membership additionally requires the parent channel to not itself be soft-deleted."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/channel_members.rs"
  - statement: "crates/buzz-db/src/store/dm.rs's hide_dm and unhide_dm functions are the only call sites in the repository that write channel_members.hidden_at, both guarded by AND removed_at IS NULL, and hide_dm's own doc comment states 'the DM is not deleted -- it can be restored by opening a new DM with the same participants (which clears hidden_at)'; hidden_at has no code path writing it for non-DM channel types at the recorded revision."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/dm.rs"
  - statement: "crates/buzz-db/src/store/channel_members.rs's get_accessible_channels query joins channel_members with the condition (c.channel_type != 'dm' OR cm.hidden_at IS NULL), confirming hidden_at is read as a visibility filter scoped specifically to the dm channel type, matching hide_dm/unhide_dm's own DM-only write path."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/channel_members.rs"
  - statement: "migrations/0029_community_deletion.sql attaches a community_id-immutability write fence to channel_members via SELECT attach_community_write_fence('channel_members'), alongside every other community-scoped table in that migration."
    entry_class: FACT
    evidence:
      - "migrations/0029_community_deletion.sql"
  - statement: "crates/buzz-db/src/store/deletion.rs lists channel_members in both EXPECTED_SCOPED_TABLES (the exact-catalog inventory a whole-community deletion validates before proceeding) and PURGE_SCOPED_TABLES (the 'foreign-key-safe child-before-parent order for the PostgreSQL purge'), positioned before channels' own row in the purge order comment context of that module."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/deletion.rs"
  - statement: "crates/buzz-relay/src/handlers/side_effects.rs's group_members_tags function builds the Nostr tag list for a kind:39002 (NIP-29 group members) event directly from a Vec<MemberRecord> parameter, and every call site building that members list (for example the one immediately preceding the kind:39002 emission around line 1066) obtains it via state.db.get_members(tenant.community(), channel_id), which crates/buzz-db/src/store/channel_members.rs's get_members function implements as a SELECT ... FROM channel_members query -- channel_members rows are the source data for the relay-synthesized kind:39002 event, not a projection derived from a stored kind:39002 event."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/side_effects.rs"
      - "crates/buzz-db/src/store/channel_members.rs"
  - statement: "buzz_core::kind::KIND_NIP29_GROUP_MEMBERS is defined as 39002 under a comment 'NIP-29: Addressable group members list', in the module documented elsewhere in this repository as 'the authoritative source for Buzz kind numbers'."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "The only INSERT/UPDATE statements against channel_members in the repository's non-test production code are in crates/buzz-db/src/store/channel_members.rs (add_member's INSERT ... ON CONFLICT ... DO UPDATE, remove_member's UPDATE ... SET removed_at) and crates/buzz-db/src/store/dm.rs (hide_dm/unhide_dm's UPDATE ... SET hidden_at); a repository-wide search for the literal string channel_members also found an INSERT INTO channel_members inside crates/buzz-db/src/store/thread.rs, but that statement sits inside a #[cfg(test)] mod tests block (a test-fixture helper, create_test_channel), not production code, and every other match (buzz-relay's conformance/mod.rs, event.rs, ingest.rs, moderation_authz.rs, buzz-cli's channels.rs, and buzz-test-client's integration tests) reads or references channel_members without writing it."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/channel_members.rs"
      - "crates/buzz-db/src/store/dm.rs"
      - "crates/buzz-db/src/store/thread.rs"
  - statement: "Membership state is server-derived from processed commands rather than being written from the generic event-ingestion path -- a code comment in add_member references 'the huddle bot-add and kind:9021 join paths' as the callers that reach it -- and channel_members is not itself an event-storage table the way events is."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-db/src/store/channel_members.rs"
    confidence: 0.7
  - statement: "No merged corpus node documents the channels table, the Postgres datastore as a whole, or NIP-29 kind:39002/9021 as their own subject at the recorded revision, since origin/launchpad's launchpad/docs/corpus tree carries no layers/ or interfaces-events content nodes yet -- confirmed directly, not assumed."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
  - statement: "Issue #1077's definition of done requires, beyond the generic corpus-node checklist: defining identity/key and semantic ownership, summarizing fields by meaning without duplicating generated schema detail, defining relationships/lifecycle/invariants, and linking authoritative migration/schema and read/write code paths."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1077 definition of done, opened directly via gh issue view"
---

# Data entity: `channel_members` (Postgres)

The membership roster binding one Nostr pubkey to one channel within one community,
with a role, a join/removal lifecycle, and (for direct-message channels only) a
per-viewer hide flag. This is a **data-entity**-level node, following
`launchpad/docs/corpus/templates/data-entity.md`'s shape: it names the concept, its
identity, its fields by meaning, its invariants, and its relationships — not the
table's column-level storage mechanics, which belong to a future datastore-level node
for the Postgres instance as a whole (none merged yet).

## Scope and authority

**This node covers** the `channel_members` table as one domain entity: what makes two
rows the same membership, what its fields mean, what must always hold about it, what
it relates to, and where its data comes from and goes to. It does not cover Postgres
storage mechanics beyond naming the defining migrations (a future datastore-level
`layers/data/postgres` node's job, per `data-entity.md`'s own boundary against
`datastore.md`), the `channels` table's own identity (a separate future entity node),
or the full wire contract of kind:9021/kind:39002 (a future `interfaces-events`
node's job).

**A note on `type`.** `node.schema.json`'s `type` enum has no dedicated `table` or
`entity` value. `data-entity.md`, the template this node's shape follows, suggests
`type: implementation` for a real instance. This node instead uses `type: layers`,
matching the precedent set by every other `layers/data/...` sibling node authored so
far in this batch (Feature #610), per this task's own dispatch brief. That is a
disclosed deviation from the template's own reasoning, not a silent substitution — see
the evidence ledger.

## Identity

A `channel_members` row's identity is the composite primary key
`(community_id, channel_id, pubkey)` — a membership is uniquely one (community,
channel, pubkey) triple, not a single surrogate id. This mirrors `channels`' own
primary key shape: identity here is **community-scoped and channel-scoped**, not
global — the same pubkey can hold independent membership rows in different channels,
and (in principle) the same triple cannot repeat, enforced by the primary key
constraint itself.

Semantic ownership of a membership row is split across three actors named in its own
columns: `invited_by` (who granted this membership, nullable — absent for a bootstrap
self-add) and `removed_by` (who ended it, nullable — present only once removed). The
row itself is not "owned" by the member (`pubkey`) alone; a membership is a relationship
between a member and a channel, mediated by whoever acted on it.

## Attributes and shape

Scalar Postgres columns, cited to `migrations/0001_initial_schema.sql`; described
below only where the name alone does not convey the meaning:

| Column | Type | Meaning |
|---|---|---|
| `community_id` | `UUID` (FK → `communities.id`) | Tenant scope; part of the identity key. |
| `channel_id` | `UUID` | Part of the identity key; the FK below additionally requires this to match a live `channels` row within the same community. |
| `pubkey` | `BYTEA` | Compressed Nostr public key bytes of the member; part of the identity key. |
| `role` | `member_role` enum, default `'member'` | Current authority level. See Invariants — the stored value is only *live* authority while `removed_at IS NULL`; on a removed row it is history. |
| `joined_at` | `TIMESTAMPTZ`, default `NOW()` | When this membership was first created (not necessarily reactivated — the row is reused across a remove/re-add cycle, see Invariants). |
| `invited_by` | `BYTEA`, nullable | Pubkey of who granted this membership; `NULL` only for a channel-creator bootstrap self-add. |
| `removed_at` | `TIMESTAMPTZ`, nullable | Set once this membership is soft-deleted; `NULL` means active. |
| `removed_by` | `BYTEA`, nullable | Pubkey of who ended this membership; set together with `removed_at`. |
| `hidden_at` | `TIMESTAMPTZ`, nullable | Per-member sidebar-visibility hint, **DM channels only** — see Invariants. Not a membership-lifecycle field; a hidden DM membership is still active. |

`member_role` is a Postgres enum with members `owner`, `admin`, `member`, `guest`,
`bot`, mirrored one-for-one by `crates/buzz-core/src/channel.rs`'s `MemberRole` Rust
enum (`as_str()` produces the identical strings). That Rust type documents the
hierarchy as Owner > Admin > Member > Guest, with Bot as "a separate designation ...
not part of the linear hierarchy," and its `is_elevated()` method — `true` only for
Owner and Admin — is the authorization boundary `add_member`/`remove_member` enforce
(see Invariants).

## Invariants

- **A membership row is never deleted by ordinary application code; removal is a soft
  delete.** `remove_member` only ever sets `removed_at`/`removed_by` on the existing
  row (guarded by `removed_at IS NULL`, returning `MemberNotFound` if no row matched);
  it never issues a `DELETE`. Re-adding a previously removed member reuses the same
  primary-key row (`INSERT ... ON CONFLICT (community_id, channel_id, pubkey) DO
  UPDATE SET removed_at = NULL, removed_by = NULL, role = EXCLUDED.role`), so
  `joined_at` reflects first creation, not the most recent (re-)activation.
- **A soft-removed row's `role` is history, not live authority.** `add_member`'s own
  code comment states this explicitly: role/authorization checks always read the
  *active* role (`removed_at IS NULL`), never a removed row's stored role — otherwise
  "an owner removed by another owner could self-rejoin ... and silently regain
  ownership."
- **A channel must always retain at least one active owner.** Both `add_member`
  (demotion) and `remove_member` (removal) count active `role = 'owner'` rows for the
  channel before allowing a change that would reduce that count to zero, and return
  `DbError::AccessDenied` if it would. Both acquire a per-channel Postgres advisory
  transaction lock (`pg_advisory_xact_lock`) as the first statement in their
  transaction specifically to make this check-then-write sequence atomic against a
  concurrent membership change on the same channel.
- **Granting or changing to an elevated role (`Owner`, `Admin`) requires an existing
  elevated actor**, on both open and private channels; an unprivileged actor may only
  add/self-join at `Member` (or, on a private channel, be invited at any
  non-elevated role by any active member).
- **Active membership additionally requires the parent channel to be live.**
  `is_member` and `membership_pairs` both join against `channels` filtered by
  `deleted_at IS NULL` — a `channel_members` row with `removed_at IS NULL` is not a
  usable active membership if its channel has itself been soft-deleted.
- **`hidden_at` only has a defined write path for DM-type channels.** `hide_dm` and
  `unhide_dm` are the only functions writing it, and `get_accessible_channels` only
  applies it as a visibility filter when `channel_type = 'dm'`. Hiding does not soft
  remove the membership — `hide_dm`'s own doc comment: "the DM is not deleted — it can
  be restored by opening a new DM with the same participants."
- **Deleting a `channels` row cascades to its `channel_members` rows** (`FOREIGN KEY
  (community_id, channel_id) REFERENCES channels (community_id, id) ON DELETE
  CASCADE`) — a hard delete only ever happens as a consequence of the parent channel
  being hard-deleted, never as an ordinary membership-removal operation on its own.
- **`community_id` is write-fenced.** `migrations/0029_community_deletion.sql`
  attaches the same `attach_community_write_fence('channel_members')` trigger used on
  every other community-scoped table in that migration, alongside `channels`' own
  `community_id`-immutability trigger on the parent table.

## Relationships to other entities

- **Foreign key, in code**: `(community_id, channel_id) → channels (community_id,
  id)`, `ON DELETE CASCADE`. As a corpus `relationships` edge this would be
  `references` targeting a future `channels`-entity node once one is merged — not
  declared here yet (see Scope and omissions).
- **Application-level reference, not a foreign key**: `pubkey` identifies a member
  against `users (community_id, pubkey)`, but no `FOREIGN KEY` constraint enforces
  this in the schema at the recorded revision (confirmed by reading the
  `channel_members` table definition in full — it declares only the one FK to
  `channels`).
- **Application-level reference, not a foreign key**: `invited_by` and `removed_by`
  are `BYTEA` pubkey columns naming other actors, unconstrained by any FK to `users`
  or to `channel_members` itself.
- **Read by `buzz-relay`'s membership-sync side effects** to synthesize NIP-29
  addressable events: `group_members_tags` (kind:39002, "Addressable group members
  list") is built directly from a `Vec<MemberRecord>` obtained via
  `state.db.get_members(...)`, and the same members list feeds kind:39001
  ("Addressable group admins list," filtered to `role IN ('owner', 'admin')`) and, for
  DM channels, the `p` tags on kind:39000 group metadata.

## Provenance

`channel_members` is a **purely server-derived table with no Nostr event of its own
as its canonical form** — it is not the storage of an incoming client-signed event the
way `events` is. It is written exclusively by relay-side command handling
(`crates/buzz-db/src/store/channel_members.rs`'s `add_member`/`remove_member`, called in response to
processed membership commands — a code comment in `add_member` references "the huddle
bot-add and kind:9021 join paths" as callers — and `crates/buzz-db/src/store/dm.rs`'s
`hide_dm`/`unhide_dm`), never by the generic event-ingestion path.

In the other direction, `channel_members` rows are the **source data** the relay reads
to *synthesize* relay-signed, addressable NIP-29 events: kind:39001 (group admins),
kind:39002 (group members, `KIND_NIP29_GROUP_MEMBERS = 39002`), and DM participant `p`
tags on kind:39000 (group metadata). Those addressable events are downstream
projections of this table, not the other way around — this table is not itself
rebuilt from replaying stored events.

## Storage pointer, not storage description

Postgres, table `channel_members`, defined in `migrations/0001_initial_schema.sql` and
altered (write-fence trigger only) by `migrations/0029_community_deletion.sql`. Column
types, index internals (`idx_channel_members_pubkey`, a partial index `WHERE removed_at
IS NULL`), migration-ordering mechanics, and the table's role in whole-community
deletion (`crates/buzz-db/src/store/deletion.rs`'s `EXPECTED_SCOPED_TABLES` and
`PURGE_SCOPED_TABLES`) are named here for citation but not elaborated — that detail
belongs to a future datastore-level `layers/data/postgres` node once one exists, per
`data-entity.md`'s own "storage pointer, not storage description" boundary.

## Scope and omissions

**This document covers** identity/key and semantic ownership; fields summarized by
meaning; relationships, lifecycle and invariants; and the authoritative migration and
read/write code paths for the `channel_members` table, per issue #1077's own
definition of done.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The `channels` table's own identity and fields as an entity | A future `layers/data/postgres/channels-table.md` (or equivalent), not yet authored |
| The `users` table's own identity and fields as an entity | A future data-entity node, not yet authored |
| Postgres-instance-level operational characteristics (replication, backup posture, migration mechanism generally) | A future `layers/data/postgres` datastore-level node, not yet authored |
| The full wire contract of kind:9021 (join request), kind:39001/39002/39003 (NIP-29 addressable group state) | A future `interfaces-events` node, not yet authored |
| Whether a Redis or other cache ever mirrors membership state | Not checked in this session — no evidence of one was found while reading `crates/buzz-db/src/store/channel_members.rs`, but the search was not exhaustive |

**No `relationships` in this node's front matter.** At the recorded revision,
`origin/launchpad`'s `launchpad/docs/corpus` tree carries no `layers/` subtree at all
(checked directly, not assumed) — the `channels`-entity node this document would most
naturally point a `references` edge at does not exist yet on the branch being merged
into. The absence is deliberate; the first sibling entity node to merge is the moment
to add it, per `AGENTS.md`'s own relationship-timing rule.

**Expected but not verified when this node was written:**

- **Whether `channel_members` is ever written outside a generic event-ingestion
  path, versus always through explicit command handling, was not fully traced.** A
  repository-wide search for the literal string `channel_members` confirmed the only
  production `INSERT`/`UPDATE` statements are in `crates/buzz-db/src/store/channel_members.rs`
  (`add_member`, `remove_member`) and `crates/buzz-db/src/store/dm.rs`
  (`hide_dm`/`unhide_dm`) — a test-fixture `INSERT` also exists in
  `crates/buzz-db/src/store/thread.rs`, but inside a `#[cfg(test)] mod tests` block, not
  production code. What is not fully traced is *every* call site that reaches
  `add_member`/`remove_member` themselves (kind:9021 join requests and "huddle
  bot-add" are named in a code comment, not independently confirmed here) — that
  claim is recorded as an `INFERENCE`, not a `FACT`, for that reason.
- **Whether `hidden_at` is ever intended to apply beyond DM channels.** Only its
  current, DM-scoped behavior is documented here; whether that scope is a permanent
  design decision or an as-yet-unextended feature was not established.
- **Cross-model review was not run.** No external-model CLI was available to this
  session; this node's review pass (self-review against the plan's STEP 4) is a
  same-model substitute, per this batch's own dispatch brief, which defers
  `review-adjudicate` and a cross-model final pass to the batch owner's later review.
