---
id: layers-data-postgres-channels-table
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
  - statement: "node.schema.json's type field is a closed 13-member enum (architecture, layers, capabilities, platforms, implementation, interfaces-events, verification, operations, development, release, governance, agent, ingestion) with no `data` member; a node whose path lives under `layers/` takes `type: layers`."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "Issue #1078 assigns this document the path launchpad/docs/corpus/layers/data/postgres/channels-table.md directly, via its own corpus-plan:v2 alias header comment and its Objective sentence, and scopes it to the channels table specifically, distinct from the sibling channel_members join-table task (#1077)."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1078, read directly via gh issue view"
  - statement: "This node uses type: layers rather than templates/datastore.md's own suggested value for a real datastore instance, following the same disclosed override two merged-once siblings in this batch already made: layers/data/object-storage/s3.md and media-objects.md (both in open PR launchpad-26/buzz#1874, branch task/610-batch-3-data-storage, read directly from the local worktree __worktrees/batch-610-3), which themselves followed blossom-storage.md and git-objects.md (open PR launchpad-26/buzz#1873). Per standards/taxonomy.md's step-4 rule (disclose an imperfect fit rather than silently pick), this tension is named here rather than resolved unilaterally. A second, independent tension is also disclosed: this document's required-section shape follows templates/data-entity.md, not templates/datastore.md, because the issue's own Definition of Done bullets (\"Defines identity/key and semantic ownership\", \"Summarizes fields by meaning without duplicating generated schema detail\", \"Defines relationships, lifecycle and invariants\", \"Links authoritative migration/schema and read/write code paths\") map onto data-entity.md's six required sections (Identity, Attributes and shape, Invariants, Relationships, Provenance, Storage pointer) far more closely than onto datastore.md's whole-instance sections (technology/attachment profile, schema/namespace inventory across many tables, migration mechanism, access-pattern summary, operational characteristics) — the `channels` table is one table mapping onto one domain concept (`Channel`), which is data-entity.md's stated subject, not a whole running Postgres instance, which is datastore.md's."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
      - "launchpad/docs/corpus/templates/datastore.md"
      - "launchpad/docs/corpus/templates/data-entity.md"
      - "launchpad/docs/corpus/standards/taxonomy.md"
      - "https://github.com/launchpad-26/buzz/issues/1078"
    confidence: 0.75
  - statement: "migrations/0001_initial_schema.sql defines the channels table with columns id (UUID, default gen_random_uuid()), community_id (UUID NOT NULL REFERENCES communities(id)), name, channel_type, visibility, description, canvas, created_by (BYTEA), created_at, updated_at, archived_at, deleted_at, nip29_group_id, topic_required, max_members, topic, topic_set_by, topic_set_at, purpose, purpose_set_by, purpose_set_at, participant_hash, ttl_seconds and ttl_deadline, with PRIMARY KEY (community_id, id) and a CHECK constraint chk_channels_id_not_nil rejecting the all-zero UUID."
    entry_class: FACT
    evidence:
      - "migrations/0001_initial_schema.sql"
  - statement: "migrations/0001_initial_schema.sql's own comment above the table states: 'Channel UUIDs stay valid wire identifiers, but they are NOT globally unique: the PK is (community_id, id), so the same UUID may legitimately exist in two communities' and names this a required isolation test ('same channel UUID collision in two communities'); it further states 'community_id immutable' and that 'Handlers always carry ctx, so (ctx.community, h) names exactly one channel; a client-supplied h can never reach another community's channel.'"
    entry_class: FACT
    evidence:
      - "migrations/0001_initial_schema.sql"
  - statement: "migrations/0001_initial_schema.sql defines a trigger channels_community_id_immutable (function of the same name) that raises a check_violation exception if an UPDATE changes a channel row's community_id, with the comment 'a channel can never be re-tenanted' and citing a migration-lint conformance rule forbidding re-tenanting except through an explicitly modeled admission path, which this repository has none of."
    entry_class: FACT
    evidence:
      - "migrations/0001_initial_schema.sql"
  - statement: "migrations/0001_initial_schema.sql defines CREATE TYPE channel_type AS ENUM ('stream', 'forum', 'dm', 'workflow') and CREATE TYPE channel_visibility AS ENUM ('open', 'private') and CREATE TYPE member_role AS ENUM ('owner', 'admin', 'member', 'guest', 'bot'), and crates/buzz-core/src/channel.rs defines Rust enums ChannelType, ChannelVisibility and MemberRole whose as_str()/FromStr implementations round-trip the identical lowercase strings, with a module doc comment stating these enums 'live in buzz-core (zero I/O deps) so both the SDK (client-side) and the DB layer (server-side) can use the same types without pulling in sqlx/tokio.'"
    entry_class: FACT
    evidence:
      - "migrations/0001_initial_schema.sql"
      - "crates/buzz-core/src/channel.rs"
  - statement: "crates/buzz-core/src/channel.rs's MemberRole doc comment states the permission hierarchy is 'Owner > Admin > Member > Guest', that 'Bot is a separate designation — it is not part of the linear hierarchy', and its permission_level() method returns 4/3/2/1/0 for Owner/Admin/Member/Guest/Bot respectively, with has_at_least() comparing those numeric levels and Bot never meeting any non-Bot requirement."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/channel.rs"
  - statement: "migrations/0001_initial_schema.sql creates idx_channels_nip29_group as a UNIQUE index on (community_id, nip29_group_id) WHERE nip29_group_id IS NOT NULL, and idx_channels_dm_hash as a UNIQUE index on (community_id, participant_hash) WHERE participant_hash IS NOT NULL, with the comment 'nip29 group id and DM participant hash are unique WITHIN a community, not globally.'"
    entry_class: FACT
    evidence:
      - "migrations/0001_initial_schema.sql"
  - statement: "migrations/0001_initial_schema.sql defines channel_members with columns community_id, channel_id, pubkey (BYTEA), role (member_role), joined_at, invited_by, removed_at, removed_by and hidden_at, PRIMARY KEY (community_id, channel_id, pubkey), and FOREIGN KEY (community_id, channel_id) REFERENCES channels (community_id, id) ON DELETE CASCADE."
    entry_class: FACT
    evidence:
      - "migrations/0001_initial_schema.sql"
  - statement: "migrations/0006_moderation.sql's moderation_reports table carries FOREIGN KEY (community_id, channel_id) REFERENCES channels (community_id, id) with the comment 'Same-community channel provenance (channels are soft-deleted, never hard-deleted, so this FK cannot dangle).'"
    entry_class: FACT
    evidence:
      - "migrations/0006_moderation.sql"
  - statement: "migrations/0022_event_ttl_refresh.sql and migrations/0024_event_ttl_refresh_shared_lock.sql together define a trigger function refresh_channel_ttl_after_event_insert that, on every non-kind-9007 event carrying a channel_id, takes a shared per-channel Postgres advisory lock (pg_advisory_xact_lock_shared, keyed 'buzz_channel_ttl:<community>:<channel>'), reads the channel's ttl_seconds, and if set, UPDATEs ttl_deadline to clock_timestamp() + ttl_seconds (only when archived_at and deleted_at are both NULL); a TTL refresh failure is caught and logged as a WARNING rather than rejecting the otherwise-valid event, per the function's own exception handler and 0024's comment 'a TTL refresh failure must not reject an otherwise valid durable event.' migration 0024's own header states this was a repair for a measured production issue: the earlier 0022 design took a row-level FOR UPDATE lock before testing ttl_seconds, serializing every durable-message commit in a permanent (non-ephemeral) channel and observed live at 200 QPS to raise commit latency from 0.07ms to ~15ms."
    entry_class: FACT
    evidence:
      - "migrations/0022_event_ttl_refresh.sql"
      - "migrations/0024_event_ttl_refresh_shared_lock.sql"
  - statement: "migrations/0024_event_ttl_refresh_shared_lock.sql's own comment states that the permanent-to-ephemeral (or TTL-change) transition, implemented by update_channel in crates/buzz-db/src/channel.rs, takes the same advisory-lock key in EXCLUSIVE mode before its UPDATE, so that either the transition commits first (and the event's shared-lock read then sees the new TTL and refreshes) or the event commits first (and the transition's own deadline reset is later than anything the event would have written) — 'no stale-NULL hole in either order.'"
    entry_class: FACT
    evidence:
      - "migrations/0024_event_ttl_refresh_shared_lock.sql"
      - "crates/buzz-db/src/channel.rs"
  - statement: "crates/buzz-db/src/channel.rs's reap_expired_ephemeral_channels function runs a single UPDATE that sets archived_at = NOW() for every channel row whose ttl_seconds IS NOT NULL, whose ttl_deadline has passed, that is not already archived or deleted, whose owning community is not archived, and for which community_write_allowed(community_id) holds, returning the community_id, community host and channel id of each row it archived."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/channel.rs"
  - statement: "crates/buzz-db/src/channel.rs's archive_channel sets archived_at = NOW() (refusing with AccessDenied if already archived, or ChannelNotFound if the row does not exist or is soft-deleted); unarchive_channel clears archived_at back to NULL and, if ttl_seconds is set, resets ttl_deadline to NOW() + ttl_seconds (refusing with AccessDenied if not currently archived); soft_delete_channel sets deleted_at = NOW() and returns Ok(false) if the row was already deleted or not found, never hard-deleting the row."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/channel.rs"
  - statement: "migrations/0027_channels_id_lookup_index.sql's own comment states that channels is keyed PRIMARY KEY (community_id, id) with every secondary index leading with community_id, that Db::communities_of_channels and Db::community_of_channel both query by id alone with no community_id predicate ('that independence is the point... which is what makes Inv_NonInterference non-vacuous'), that no existing composite index can serve those queries so both sequentially scanned channels on every call (observed as the top wait on the staging writer), and that the new idx_channels_id_live index is deliberately NOT UNIQUE because 'id alone is not unique in this table' — the same fact migrations/0001's own PK comment establishes."
    entry_class: FACT
    evidence:
      - "migrations/0027_channels_id_lookup_index.sql"
  - statement: "migrations/0029_community_deletion.sql calls SELECT attach_community_write_fence('channels'), and that function's own body (and the DO block auto-attaching it to every table carrying a community_id column) installs a BEFORE INSERT OR UPDATE OR DELETE trigger named community_write_fence_channels that calls enforce_community_write_fence(), which in turn calls assert_community_write_allowed() against the row's community_id (both old and new values on an UPDATE that changes it) — so a channels write is refused once its owning community has entered the deletion/tombstone state assert_community_write_allowed enforces."
    entry_class: FACT
    evidence:
      - "migrations/0029_community_deletion.sql"
  - statement: "crates/buzz-core/src/kind.rs defines KIND_NIP29_CREATE_GROUP = 9007 (doc comment 'NIP-29: Create a new group') and the addressable range comment 'NIP-29 group state (addressable range 39000-39003)' above KIND_NIP29_GROUP_METADATA = 39000, KIND_NIP29_GROUP_ADMINS = 39001, KIND_NIP29_GROUP_MEMBERS = 39002 and KIND_NIP29_GROUP_ROLES = 39003."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "crates/buzz-relay/src/handlers/side_effects.rs, in its channel-creation side-effect handler, calls state.db.create_channel(...) when a kind-9007 event carries no h-tag UUID, or as a resilience fallback via create_channel_with_id when an h-tag UUID is present but ingest_event's own pre-creation of the row (in crates/buzz-relay/src/handlers/ingest.rs) cannot be found — with a comment stating the fallback 'shouldn't happen (ingest_event pre-created it)' and explaining, in a 'Double-count analysis (C5)' comment, why the buzz_channels_created_total counter is not double-incremented across the two code paths."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/side_effects.rs"
  - statement: "crates/buzz-relay/src/handlers/side_effects.rs's emit_group_discovery_events function, doc-commented 'Emit NIP-29 group discovery events (39000, 39001, 39002) signed by the relay keypair. Called after group creation, metadata changes, or membership changes', reads the current channel row via state.db.get_channel and its members via state.db.get_members, then constructs and stores kind:39000/39001/39002 events tagged d=<channel_id> and signed by the relay's own keypair (relay_keypair), channel-scoped (channel_id = Some(...)) so existing access control applies -- with a NOTE that channel-scoped storage means these will not fan out to a live global {kinds:[39000]} subscription, only to historical REQ queries."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/side_effects.rs"
  - statement: "crates/buzz-relay/src/handlers/side_effects.rs's reconciliation helper (around its own comment 'Reconcile channels that exist in the DB but don't have kind:39000 events') is doc-commented 'Emits kind:39000 (metadata) and kind:39002 (members) for each channel' and 'Idempotent: checks for existing kind:39000 events before emitting' -- confirming the channels row, not the kind:39000/39001/39002 events, is this system's actual source of truth for a channel's existence and current metadata/membership: the events are a derived, relay-signed projection that can be (and is) regenerated from the row, the inverse relationship of thread_metadata, whose own module doc (crates/buzz-db/src/thread.rs) states it 'is populated when events are ingested and updated as replies arrive or are deleted' -- there, the events are the source of truth and the table is derived; here, the table is the source of truth and the events are derived."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay/src/handlers/side_effects.rs"
      - "crates/buzz-db/src/thread.rs"
      - "launchpad/docs/corpus/templates/data-entity.md"
    confidence: 0.8
  - statement: "Root CLAUDE.md's 'Channel scoping' entry states: 'Channels use h tags (NIP-29 group tag), not e tags... Addressable events that describe a channel carry its id in their d tag instead: kind:39000 (metadata), kind:39001, kind:39002 (membership). get_channels resolves a user's channels from the d tag of their kind:39002 events, not from h.'"
    entry_class: FACT
    evidence:
      - "CLAUDE.md"
  - statement: "crates/buzz-db/src/channel.rs defines the read/write surface for this table as a flat set of pub async fn functions taking &PgPool (or an active transaction) and a CommunityId: create_channel, create_channel_with_id, get_channel, get_canvas, set_canvas, add_member, remove_member, is_member, membership_pairs, get_members, get_members_bulk, get_accessible_channel_ids, list_channels, get_accessible_channels, get_bot_members, get_users_bulk, update_channel, set_topic, set_purpose, archive_channel, unarchive_channel, soft_delete_channel, get_member_count, get_member_counts_bulk, get_member_role and reap_expired_ephemeral_channels, and re-exports ChannelType/ChannelVisibility/MemberRole from buzz_core::channel rather than redefining them, per its own comment 'Re-export the canonical enum definitions from buzz-core... These live in core (zero I/O deps) so the SDK can share them without pulling in sqlx/tokio.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/channel.rs"
  - statement: "At the recorded revision, git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus lists no node under layers/data/postgres/ and no node whose id or path names channels, communities, datastore or data-entity, so no relationships.target exists for this node to point at yet -- checked directly rather than assumed, per AGENTS.md's own warning that an absent-target justification decays the moment a sibling node merges."
    entry_class: FACT
    evidence:
      - "git_ls_tree(ref='origin/launchpad', path='launchpad/docs/corpus') -> no layers/data/postgres/** entries at commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
---

# `channels` (Postgres) — data entity

The `channels` table is Buzz's own materialized record of a channel: its identity,
visibility, type, topic/purpose, TTL state, and its owning community. This node
documents the entity `channels` represents -- its identity, its fields by meaning,
its invariants, its relationships to other data, and its lifecycle -- not the
Postgres engine that hosts it (that is `datastore.md`'s territory, not yet
instantiated for this repository) and not the sibling `channel_members` join table's
own fields (`#1077`, out of scope here).

## Scope and authority

**This node covers** the `channels` table specifically: its identity/key and
semantic ownership, its columns summarized by meaning, its relationships to other
tables and to the Nostr events that create and mirror it, its lifecycle states and
the invariants that hold across them, and the migration and code paths that define
and touch it.

**Its authority is derived, not original.** `node.schema.json` is the front-matter
law; `AGENTS.md` is the create/update/retire procedure; `templates/data-entity.md` is
the required-section shape this node follows (see the type-and-template disclosure
in the evidence ledger above for why, and why `type: layers` rather than
`data-entity.md`'s own suggested `type: implementation`). This document adds nothing
to any of those; it applies them to one real table.

## Identity

A `channels` row's identity is the composite primary key `(community_id, id)`, not
`id` alone. The table's own schema comment is explicit that a channel's UUID "stay[s]
a valid wire identifier, but they are NOT globally unique" -- the same UUID may
legitimately exist as two different channels in two different communities, which the
schema comment names as a required isolation test. `community_id` is immutable once
set: an UPDATE trigger (`channels_community_id_immutable`) raises a `check_violation`
if any UPDATE attempts to change it, because "a channel can never be re-tenanted."
`id` itself is constrained only to reject the all-zero UUID
(`chk_channels_id_not_nil`); it is `id` *alone* that is not unique -- see *Storage
pointer*, below, on why the covering index that resolves a bare `id` to its owning
`community_id` was added specifically because "id alone is not unique in this
table."

Two secondary uniqueness constraints exist, both scoped to a community rather than
global: `nip29_group_id` (unique per `community_id`, when set) and `participant_hash`
(unique per `community_id`, when set -- this is the field that gives a DM
conversation between the same pair of participants exactly one channel per
community).

## Attributes and shape

Scalar columns, cited to `migrations/0001_initial_schema.sql` rather than restated
as generated DDL:

- **`name`** -- the channel's display name.
- **`channel_type`** -- one of `stream` (linear message stream, the default),
  `forum` (threaded discussion), `dm` (direct-message conversation) or `workflow`
  (internal workflow-execution channel). Mirrored in Rust by
  `buzz_core::channel::ChannelType`, whose `as_str()`/`FromStr` round-trip the
  identical lowercase strings the Postgres enum uses.
- **`visibility`** -- `open` (searchable, anyone can join) or `private`
  (invite-only), mirrored by `buzz_core::channel::ChannelVisibility`.
- **`description`**, **`canvas`** -- free-text description and a rich-document
  "canvas" body, both nullable.
- **`created_by`** -- the creator's compressed public key (`BYTEA`), not a
  foreign key to any user table.
- **`created_at`**, **`updated_at`** -- standard timestamps.
- **`archived_at`**, **`deleted_at`** -- lifecycle timestamps; see *Invariants and
  lifecycle*, below. Both `NULL` means active.
- **`nip29_group_id`** -- an optional external NIP-29 group identifier, unique per
  community when set.
- **`topic_required`** -- whether posts in this channel must carry an associated
  topic.
- **`max_members`** -- an optional membership cap.
- **`topic`**, **`topic_set_by`**, **`topic_set_at`** and **`purpose`**,
  **`purpose_set_by`**, **`purpose_set_at`** -- the channel's current topic and
  purpose, each with its own "who/when last set" pair, independently mutable.
- **`participant_hash`** -- present for `dm`-type channels; unique per community,
  giving the same participant pair exactly one DM channel per community.
- **`ttl_seconds`**, **`ttl_deadline`** -- TTL state for ephemeral channels; `NULL`
  `ttl_seconds` means permanent. See *Invariants and lifecycle*.

Membership is a **separate** table, `channel_members` (`#1077`, out of scope here
beyond the one relationship it forms -- see *Relationships*), not a column on
`channels`.

## Invariants and lifecycle

- **`community_id` is immutable** once a row exists, enforced by the
  `channels_community_id_immutable` trigger, not merely by convention.
- **`id` is never the all-zero UUID**, enforced by `chk_channels_id_not_nil`.
- **A channel's identity is community-scoped, not global.** The same `id` may exist
  in more than one community; only `(community_id, id)` is unique.
- **`nip29_group_id`** and **`participant_hash`** are each unique per community
  when set (partial unique indexes), not globally unique.
- **Lifecycle states, in order:** active (`archived_at` and `deleted_at` both
  `NULL`) → optionally archived (`archived_at` set; `archive_channel` refuses with
  `AccessDenied` if already archived, and with `ChannelNotFound` if the row does not
  exist or is already soft-deleted) → optionally unarchived (`unarchive_channel`
  clears `archived_at` and, if `ttl_seconds` is set, resets `ttl_deadline` to
  `NOW() + ttl_seconds`; refuses `AccessDenied` if not currently archived) →
  soft-deleted (`soft_delete_channel` sets `deleted_at`; idempotent, returning
  `Ok(false)` rather than erroring if already deleted or not found). **A channel
  row is never hard-deleted** -- `migrations/0006_moderation.sql`'s own FK comment
  states this explicitly as the reason its `moderation_reports.channel_id` foreign
  key "cannot dangle."
- **TTL-driven auto-archival.** A channel with `ttl_seconds` set is ephemeral: every
  non-creation event landing in it (any kind other than the creating `9007`)
  refreshes `ttl_deadline` to `NOW() + ttl_seconds` under a per-channel shared
  Postgres advisory lock, and the *permanent-to-ephemeral transition itself*
  (`update_channel`) takes the same lock key exclusively, so the two orderings
  cannot race into a stale `NULL` deadline. `reap_expired_ephemeral_channels`
  auto-archives any channel whose `ttl_deadline` has passed, skipping channels whose
  community is archived or whose community currently disallows writes. A TTL
  refresh failure is caught and logged, never rejecting the message event that
  triggered it.
- **Community deletion fences writes.** `attach_community_write_fence('channels')`
  installs a trigger that refuses any INSERT/UPDATE/DELETE on a `channels` row once
  its owning community has entered the deletion/tombstone state -- a channel cannot
  be created, modified or (soft-)deleted independently of its community's own
  deletion lifecycle once that lifecycle has started.

## Relationships

- **To `communities`** (foreign key, `community_id`) -- every channel belongs to
  exactly one community, immutably. No corpus node for `communities` exists yet
  (`#1079`, this same batch); once one merges, this node should add a `references`
  edge, not `depends-on` -- this document's own claims about the `channels` table's
  shape do not stop holding if the community's own document changes.
- **To `channel_members`** (foreign key, `(community_id, channel_id)`, `ON DELETE
  CASCADE`) -- a channel's membership rows are deleted if the channel row itself is
  ever physically deleted. In current practice this cascade is dormant: channels are
  soft-deleted, never hard-deleted (see *Invariants and lifecycle*), so the cascade
  exists as a safety property rather than a path this codebase's own code exercises.
  `channel_members`'s own fields are `#1077`'s document, out of scope here.
- **To `moderation_reports`** (foreign key, `(community_id, channel_id)`) -- a
  moderation report may reference the channel it concerns; relies on the same
  never-hard-deleted invariant to guarantee it cannot dangle.
- **To Nostr events, as both creator and mirrored projection** -- see *Provenance*.

## Provenance

A `channels` row is created as a side effect of the relay ingesting a **kind 9007**
(`KIND_NIP29_CREATE_GROUP`, NIP-29 "create a new group") event: the row is the
canonical, durable representation, not the 9007 event itself, which is the one-time
trigger. Separately, the relay emits **kind 39000** (group metadata), **39001**
(admins) and **39002** (members) -- relay-signed, addressable NIP-29 "group
discovery" events -- reading the current `channels` row (and its members) and
re-emitting them after creation, metadata changes, or membership changes, idempotent
against an existing kind:39000 event for the same channel. This is the **inverse**
of `thread_metadata`'s own provenance shape (per `data-entity.md`'s own worked
illustration of that table): there, the reply events are the source of truth and the
table is a derived projection; here, the `channels` row is the source of truth and
kind:39000/39001/39002 are the derived, relay-signed projection, regenerable from
the row on demand. Root `CLAUDE.md`'s own "Channel scoping" note confirms clients
are expected to resolve a user's channels from these addressable events' `d` tags
(not from `h` tags), which is the read-side consequence of this row-to-event
projection existing at all.

## Storage pointer

Postgres, table `channels`, defined in `migrations/0001_initial_schema.sql` and
touched by five later migrations: `migrations/0006_moderation.sql` (the
`moderation_reports` FK), `migrations/0022_event_ttl_refresh.sql` and
`migrations/0024_event_ttl_refresh_shared_lock.sql` (the TTL-refresh trigger and its
advisory-lock repair), `migrations/0027_channels_id_lookup_index.sql` (a covering
index for `id`-alone lookups, added because "`id` alone is not unique in this
table" makes every such lookup a sequential scan without it), and
`migrations/0029_community_deletion.sql` (the community write fence). No
`layers-data-postgres` datastore-level node exists yet to link via `references` for
this table's own engine, replication or backup posture -- see *Scope and
omissions*.

The read/write surface is `crates/buzz-db/src/channel.rs`, whose public functions
are enumerated in the evidence ledger above; `crates/buzz-relay/src/handlers/side_effects.rs`
and `crates/buzz-relay/src/handlers/ingest.rs` are the call sites that create a row
from a kind-9007 event and emit the kind:39000/39001/39002 projection.

## Scope and omissions

**This document covers** the `channels` table's identity, fields by meaning,
invariants, lifecycle, relationships and provenance, and its migration/code
pointers.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| `channel_members`'s own columns and semantics | `#1077` (not yet drafted at this node's authoring time) |
| The `communities` table's own identity and fields | `#1079` (not yet drafted at this node's authoring time) |
| Postgres itself as a datastore -- engine version, replication, backup posture, connection pooling | A future `layers/data/postgres` datastore-level node, not yet written; `templates/datastore.md` governs its shape |
| The NIP-29 wire contract for kinds 9007/39000/39001/39002 (tag semantics, content shape) | A future event-kind node (`templates/event-kind.md`, referenced but not yet instantiated in this repository's corpus at the recorded revision) |
| System-wide invariants not specific to this one table (e.g. the general community-write-fence mechanism, which fences every community-scoped table, not just `channels`) | A future cross-cutting invariant node |

**No `relationships` in this node's front matter.** Checked directly against
`origin/launchpad`'s corpus tree (`git ls-tree -r --name-only origin/launchpad --
launchpad/docs/corpus`) at the recorded revision: no node exists yet for
`communities`, for the Postgres datastore, for `channel_members`, or for the
NIP-29 event kinds this table's rows are created from and projected into. The most
likely first genuine edges are a `references` edge to a merged `communities` entity
node and a `references` edge to a merged Postgres datastore node, both named above
and neither available today.

**Expected but not verified when this node was written:**

- **Whether `channel_type = 'dm'` is the sole condition under which
  `participant_hash` is populated was not traced through the DM-creation code
  path itself** -- only the schema's own partial-unique-index predicate
  (`WHERE participant_hash IS NOT NULL`) and the enum's existence were checked.
- **The exact tag/content shape kind 39000/39001/39002 events carry** (beyond the
  `d`-tag-is-channel-id fact this node cites) was read from
  `emit_group_discovery_events`'s own tag-construction code but is not
  transcribed field-by-field here -- that belongs to the future event-kind node
  named in the table above, not to this one.
- **Whether every `channels` column changed by every migration after 0029 was
  checked** -- the migration list above covers structural changes to the table
  itself (its columns, indexes, triggers and FKs) found by `grep -l channels
  migrations/*.sql`; a column-level ALTER hidden inside a migration whose filename
  does not mention channels would not have been found by that search.
