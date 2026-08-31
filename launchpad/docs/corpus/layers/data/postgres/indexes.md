---
id: layers-data-postgres-indexes
type: layers
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - operator
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5."
    entry_class: FACT
    evidence:
      - "commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
  - statement: "node.schema.json's type enum has thirteen members (architecture, layers, capabilities, platforms, implementation, interfaces-events, verification, operations, development, release, governance, agent, ingestion) and names the corpus surface a node documents, not the document's shape. This node uses type: layers rather than type: architecture -- the value launchpad/docs/corpus/templates/datastore.md's own evidence ledger reasons a real datastore instance most plausibly takes, on the grounds that node.schema.json has no finer-grained member for a container-, component-, or datastore-level structural view. That reasoning was read and is not re-argued here; type: layers is used instead because it is the established, disclosed precedent every other launchpad/docs/corpus/layers/data/postgres/*.md document in this batch uses, per standards/taxonomy.md's 'Choosing a value' rule that an imperfect-fit type MUST be disclosed in the node's own scope section rather than silently picked -- see Scope and omissions below."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
      - "launchpad/docs/corpus/templates/datastore.md"
      - "launchpad/docs/corpus/standards/taxonomy.md"
  - statement: "architecture-containers-postgres is a validated node on origin/launchpad at launchpad/docs/corpus/architecture/containers/postgres.md, describing buzz-db as the crate that owns Postgres connection pooling, migrations and typed data access, and documenting the events table's partitioning and pooling shape at the container level -- the container-level document this node's part-of relationship zooms into and does not repeat."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/containers/postgres.md"
  - statement: "The migrations/ directory contains 76 CREATE INDEX or CREATE UNIQUE INDEX statements across 16 of its 31 sequentially numbered SQL files (0001 through 0031), per grep -oE 'CREATE (UNIQUE )?INDEX' migrations/*.sql | wc -l and grep -lE 'CREATE (UNIQUE )?INDEX' migrations/*.sql | wc -l respectively, and schema/schema.sql -- described in its own header comment as the 'source of truth for fresh database setup' -- separately contains 69 CREATE INDEX statements by the same grep."
    entry_class: FACT
    evidence:
      - "migrations/0001_initial_schema.sql"
      - "migrations/0002_git_repo_names.sql"
      - "migrations/0004_events_tags_gin.sql"
      - "migrations/0005_agent_turn_metric_fts.sql"
      - "migrations/0006_moderation.sql"
      - "migrations/0007_nip_rs_retention.sql"
      - "migrations/0008_fresh_install_search_allowlist.sql"
      - "migrations/0012_push_leases.sql"
      - "migrations/0014_push_lease_fts.sql"
      - "migrations/0015_push_gateway_authority.sql"
      - "migrations/0017_product_feedback.sql"
      - "migrations/0018_push_match_queue.sql"
      - "migrations/0025_relay_invites.sql"
      - "migrations/0027_channels_id_lookup_index.sql"
      - "migrations/0029_community_deletion.sql"
      - "migrations/0030_community_deletion_recovery.sql"
      - "schema/schema.sql"
  - statement: "Every CREATE INDEX statement in migrations/0001_initial_schema.sql on a multi-tenant (community-scoped) table leads with community_id as its first indexed column, for example idx_events_community_channel_created ON events (community_id, channel_id, created_at DESC, id), idx_channels_community_type ON channels (community_id, channel_type), and idx_thread_metadata_channel_depth ON thread_metadata (community_id, channel_id, depth, event_created_at); the same convention holds for every UNIQUE index on a scoped table, e.g. idx_channels_nip29_group ON channels (community_id, nip29_group_id) and idx_users_nip05 ON users (community_id, lower(nip05_handle))."
    entry_class: FACT
    evidence:
      - "migrations/0001_initial_schema.sql"
  - statement: "schema/schema.sql's own header states its migration-lint obligations include 'No UNIQUE / PRIMARY KEY / FK on a scoped table is observable across communities: each leads with community_id', which is the same community-leading convention observed directly in migrations/0001_initial_schema.sql's index definitions, not merely an independent restatement."
    entry_class: FACT
    evidence:
      - "schema/schema.sql"
  - statement: "migrations/0027_channels_id_lookup_index.sql's own extensive comment documents one deliberate exception to the community-leading convention: idx_channels_id_live ON channels (id) INCLUDE (community_id) WHERE deleted_at IS NULL, built to serve two tenant-independent lookups in buzz-db (Db::communities_of_channels and Db::community_of_channel) that resolve a channel's owning community without a community_id predicate, because 'the same channel id can appear under more than one community' and 'a unique index would encode a false constraint.' The comment names this independence as load-bearing for what it calls Inv_NonInterference, a term also used in crates/buzz-conformance/src/transitions.rs and crates/buzz-relay/src/conformance/mod.rs to describe the invariant that every row label projected to a caller reflects the row's true community regardless of the query path -- this node cites that cross-reference without describing Inv_NonInterference's own contract, which is out of this node's scope."
    entry_class: FACT
    evidence:
      - "migrations/0027_channels_id_lookup_index.sql"
      - "crates/buzz-conformance/src/transitions.rs"
  - statement: "migrations/0027_channels_id_lookup_index.sql's comment states the query it serves was 'Observed as the top \"Load by waits (AAS)\" on the staging writer (db.r8g.8xlarge, ~53% CPU)' before this index existed, because 'neither query can use the primary key and no other index leads with id', so both sequentially scanned channels on every call -- a production performance measurement backing the index's existence, not an assumption."
    entry_class: FACT
    evidence:
      - "migrations/0027_channels_id_lookup_index.sql"
  - statement: "crates/buzz-db/src/event.rs cites idx_events_parameterized by name in a doc comment on the EventQuery.d_tag field ('Pushed into SQL via the idx_events_parameterized index'), and cites idx_events_tags_gin by name at two separate call sites (the e-tag JSONB-containment pushdown, and the SHARED_GATED_KINDS visibility pushdown), the second of which states the GIN index was added because unindexed containment made a channel-window fan-out 'the dominant scroll-back cost (~1.7s/page on staging)' per migrations/0004_events_tags_gin.sql's own comment."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/event.rs"
      - "migrations/0004_events_tags_gin.sql"
  - statement: "migrations/0004_events_tags_gin.sql's own comment states 'Partitioned parent: CREATE INDEX recurses to all partitions and future partitions inherit it', and crates/buzz-db/src/partition.rs's ensure_partition function creates each new monthly partition with a plain CREATE TABLE ... PARTITION OF <table> statement (no ONLY clause and no per-partition index DDL) -- the mechanism by which a partitioned-parent index automatically extends to a partition the code creates later, without any index-specific code in partition.rs."
    entry_class: FACT
    evidence:
      - "migrations/0004_events_tags_gin.sql"
      - "crates/buzz-db/src/partition.rs"
  - statement: "crates/buzz-db/src/partition.rs's PARTITIONED_TABLES constant restricts partition management to exactly events and delivery_log, and ensure_partition validates the table name against that allowlist, the partition suffix against a digits-and-underscores check, and both date strings against a fixed YYYY-MM-DD format before interpolating any of them into DDL, because 'parameterized queries cannot be used for DDL identifiers.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/partition.rs"
  - statement: "crates/buzz-db/src/migration.rs's run_migrations function runs the embedded sqlx::migrate! MIGRATOR while holding the exclusive SCHEMA_DESTRUCTION_LOCK_KEY session lock, its own doc comment stating this 'serializ[es] schema changes against destructive deletion transactions' and that a source lint (migration_execution_cannot_bypass_schema_destruction_lock) enforces MIGRATOR.run has no other call site -- index-creating migrations run under this same single, guarded entry point as every other schema change, with no separate mechanism of their own."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/migration.rs"
  - statement: "migrations/0027_channels_id_lookup_index.sql's comment states plainly that sqlx wraps each migration in a transaction and 'CREATE INDEX CONCURRENTLY cannot run in one', so the index is built without CONCURRENTLY and takes a SHARE lock on the table (blocking writes, not reads) for the build's duration; migrations/0004_events_tags_gin.sql's comment makes the same statement about its own GIN index, adding that CONCURRENTLY 'is not supported on partitioned parents' at all, so this constraint holds independently of the transaction-wrapping for any index on the events table."
    entry_class: FACT
    evidence:
      - "migrations/0027_channels_id_lookup_index.sql"
      - "migrations/0004_events_tags_gin.sql"
  - statement: "migrations/0027_channels_id_lookup_index.sql creates its index with IF NOT EXISTS, its own comment stating this 'makes this migration a no-op on that database' if an operator has already pre-built the index by hand with CREATE INDEX CONCURRENTLY, and separately states 'Additive migration: previously applied files must not change checksum' -- the same checksum-pinning sqlx applies to every migration file, meaning an already-applied index-creating migration cannot be edited in place without failing migration startup on any database that already recorded its checksum."
    entry_class: FACT
    evidence:
      - "migrations/0027_channels_id_lookup_index.sql"
  - statement: "crates/buzz-db/src/migration.rs contains a test, embedded_migrator_contains_consolidated_initial_schema, that asserts on the literal SQL text of specific migrations, including that migrations[26] (version 27) 'contains(\"idx_channels_id_live\")', 'contains(\"INCLUDE (community_id)\")', 'contains(\"WHERE deleted_at IS NULL\")' and '!contains(\"CREATE UNIQUE INDEX\")', and that schema/schema.sql -- loaded in the same test via include_str! -- also 'contains(\"idx_channels_id_live\")'; this is a real, running regression test pinning at least one index's shape and its presence in both the migration and the desired-state schema file."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/migration.rs"
  - statement: "idx_events_tags_gin, the GIN index created in migrations/0004_events_tags_gin.sql, does not appear anywhere in schema/schema.sql (grep for 'tags_gin' and for 'USING GIN' in that file finds only idx_events_search_tsv), and git log on schema/schema.sql shows no commit touching it for migration 0004's change, while migration 0027's own index (idx_channels_id_live) does appear in schema.sql and was added to it in the same commit (bc9e6528a) that added the migration -- a real, checked discrepancy between the two sources of truth for this specific index, not established for any other index in the inventory."
    entry_class: FACT
    evidence:
      - "schema/schema.sql"
      - "migrations/0004_events_tags_gin.sql"
      - "git_log(schema/schema.sql) -> bc9e6528a 'perf(relay): index channel-id lookups and skip trace-only reads (#4647)' is the commit that added idx_channels_id_live to schema.sql; no equivalent commit adds idx_events_tags_gin"
  - statement: "Multiple partial indexes exist across the migrations, each with a WHERE clause matching a soft-delete, active-flag, or not-yet-processed lifecycle predicate: idx_channels_id_live ... WHERE deleted_at IS NULL (migration 0027), idx_events_parameterized ... WHERE d_tag IS NOT NULL AND deleted_at IS NULL (migration 0001), idx_events_not_before ... WHERE not_before IS NOT NULL AND deleted_at IS NULL AND delivered_at IS NULL (migration 0001), idx_workflows_enabled ... WHERE enabled (migration 0001), push_leases_expiry ... WHERE active (migration 0012), idx_reactions_source_event ... WHERE reaction_event_id IS NOT NULL (migration 0001), and push_gateway_installations_expiry / push_gateway_delegations_expiry ... WHERE revoked_at IS NULL (migration 0015)."
    entry_class: FACT
    evidence:
      - "migrations/0027_channels_id_lookup_index.sql"
      - "migrations/0001_initial_schema.sql"
      - "migrations/0012_push_leases.sql"
      - "migrations/0015_push_gateway_authority.sql"
  - statement: "Several indexes exist purely to support time-based cleanup/expiry sweeps rather than any read-path filter named elsewhere in this ledger: idx_channels_ttl_expiry ON channels (ttl_deadline), push_leases_expiry, push_gateway_challenges_expiry, push_gateway_installations_expiry, push_gateway_delegations_expiry, push_gateway_endpoint_quotas_updated, push_gateway_delivery_auth_replays_expiry, push_gateway_delivery_request_replays_expiry, and relay_invites_expires_at_idx -- named here at the structural level only; the sweep jobs that scan them are out of this node's scope."
    entry_class: FACT
    evidence:
      - "migrations/0001_initial_schema.sql"
      - "migrations/0012_push_leases.sql"
      - "migrations/0015_push_gateway_authority.sql"
      - "migrations/0025_relay_invites.sql"
  - statement: "crates/buzz-relay/src/handlers/event.rs contains a comment stating 'the old Typesense index_event worker and its search_index_tx mpsc are gone with the Typesense backend', and crates/buzz-search/Cargo.toml describes buzz-search as Postgres full-text search -- confirming full-text search moved from an external, separately-updated Typesense index to the in-database idx_events_search_tsv GIN index created directly on the events table by the same transaction that inserts the row, per the events table's search_tsv GENERATED ALWAYS AS ... STORED column definition in migrations/0001_initial_schema.sql."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs"
      - "crates/buzz-search/Cargo.toml"
      - "migrations/0001_initial_schema.sql"
  - statement: "The events table's primary key is (community_id, created_at, id) per migrations/0001_initial_schema.sql, and migration 0001's own comment on idx_events_community_id explains a second, narrower index is needed because 'the PK can't serve WHERE id=$1' -- 'created_at sits between community_id and id' in the key -- so idx_events_community_id ON events (community_id, id, created_at DESC) exists specifically to make the scoped form WHERE community_id=$ AND id=$ index-served rather than a partition scan."
    entry_class: FACT
    evidence:
      - "migrations/0001_initial_schema.sql"
  - statement: "Issue #1082's Definition of Done requires stating whether the store is authoritative, derived, cache or transport; describing owned data, key access patterns, lifecycle/retention and consistency semantics; naming tenancy/security boundaries and failure behavior; and linking schema/migrations/code/tests rather than copying DDL -- distinct from and closer to launchpad/docs/corpus/templates/datastore.md's own required-sections shape (technology/attachment profile, schema/namespace inventory, migration mechanism, access-pattern summary, operational characteristics) than to templates/reference.md's three-section (description, structured entries, optional commands) shape, which this node is built against for that reason."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1082 definition of done, opened directly via gh issue view"
  - statement: "PR #1875, referenced in this task's own dispatch brief, adds sibling layers/data/postgres/*.md documents from the same batch but is unmerged at this node's authoring revision, so no other layers/data/postgres/*.md node is a valid relationships target for this node."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "corpus-batch-author overnight batch dispatch brief for issue #1082, 2026-08-30"
relationships:
  - type: part-of
    target: architecture-containers-postgres
---

# Postgres indexing strategy

This node documents Buzz's Postgres indexing strategy as a cross-cutting
concern spanning the whole `buzz` database: which indexes exist, why each was
added, how they are created and versioned, and what they promise (and do not
promise) about tenancy, consistency and failure behavior. It is not a second
description of the Postgres container's existence or connection profile --
that is `architecture-containers-postgres`, which this node is `part-of` and
does not repeat. It is not a catalogue of what any one table's rows mean --
no `layers/data/postgres/*.md` sibling document exists yet on `origin/launchpad`
to link to (see *Scope and omissions*), so table-level structural context is
given inline, at the same one-line-per-structure depth
`templates/datastore.md`'s own schema/namespace-inventory section prescribes,
rather than duplicated at length.

## Store role: derived, not authoritative

Every index in this inventory is a **derived** structure. Postgres builds and
maintains each one synchronously and transactionally from the rows of the
table it indexes; dropping an index or rebuilding it changes query plans and
latency, never the data a client can observe. No index in this repository is
itself a cache (nothing reads a stale copy through it -- see *Consistency
semantics* below) and none is a transport (nothing outside Postgres itself
ever addresses an index directly; every access goes through SQL issued by
`buzz-db`, `buzz-search`, or `buzz-relay`'s own handlers). The one exception
worth naming explicitly: `idx_channels_id_live` (migration 0027) exists
specifically to make a tenant-independent lookup path fast, but the lookup
itself still reads the same `channels` table rows the index derives from --
the index changes how the row is found, not what is found.

## Index inventory

Structural groupings only -- one row per concern, not one row per statement.
Every index leads with `community_id` on a multi-tenant table unless the
*Tenancy and security boundaries* section below names it as the deliberate
exception.

| Table / concern | Representative indexes | Structural purpose |
|---|---|---|
| `events` (hot path) | `idx_events_community_id`, `idx_events_community_channel_created`, `idx_events_community_pubkey_kind_created`, `idx_events_community_kind_created`, `idx_events_community_deleted` | Community-scoped lookup by id, by channel timeline, by author+kind, and by kind, all ordered `created_at DESC` for feed-style pagination. |
| `events` (addressable / NIP-33) | `idx_events_addressable`, `idx_events_parameterized` | Serve replaceable-event and parameterized-replaceable (`d` tag) lookups; `idx_events_parameterized` is partial (`WHERE d_tag IS NOT NULL AND deleted_at IS NULL`). |
| `events` (tag containment) | `idx_events_tags_gin` (GIN, `jsonb_path_ops`) | Serves `tags @> '[[...]]'` containment pushdowns -- `#e`-tag fan-out and the shared-gated-kind visibility check, both cited directly in `buzz-db/src/event.rs`. |
| `events` (full-text search) | `idx_events_search_tsv` (GIN) | Indexes the generated, stored `search_tsv` column; the in-database replacement for the removed Typesense index (see *Consistency semantics*). |
| `events` (scheduling) | `idx_events_not_before` | Partial index over not-yet-deliverable scheduled events. |
| `channels` | `idx_channels_nip29_group`, `idx_channels_dm_hash` (both `UNIQUE`), `idx_channels_community_type`, `idx_channels_community_visibility`, `idx_channels_created_by`, `idx_channels_ttl_expiry`, `idx_channels_id_live` | Community-scoped uniqueness and lookup by type/visibility/creator; TTL sweep; the one tenant-independent covering index (see *Tenancy and security boundaries*). |
| `users` | `idx_users_nip05`, `idx_users_okta` (both `UNIQUE`, community-scoped) | Enforce per-community uniqueness of externally-issued identity handles. |
| `thread_metadata` | `idx_thread_metadata_parent`, `idx_thread_metadata_root`, `idx_thread_metadata_channel_depth`, `idx_thread_metadata_event_id` | Serve the thread-tree lookups (`buzz-db/src/thread.rs`'s materialized reply/depth projection) by parent, root, channel+depth ordering, and direct event id. |
| `event_mentions` | `idx_event_mentions_pubkey_created`, `idx_event_mentions_pubkey_kind_created` | Serve `#p` fan-out lookups by mentioned pubkey, with and without a kind filter. |
| `reactions` | `idx_reactions_event`, `idx_reactions_pubkey`, `idx_reactions_source_event` (`UNIQUE`, partial) | Lookup by target event and by reactor; enforce a reaction event's source uniqueness within a community. |
| `moderation_reports` / `moderation_actions` | `idx_moderation_reports_status`, `idx_moderation_reports_target_event`, `idx_moderation_reports_target_pubkey`, `idx_moderation_reports_event` (`UNIQUE`), `idx_moderation_actions_created`, `idx_moderation_actions_target_pubkey` | Moderation queue and audit lookups. |
| `workflows` / `workflow_runs` / `workflow_approvals` | `idx_workflows_channel_active`, `idx_workflows_enabled` (partial), `idx_workflow_runs_workflow`, `idx_workflow_runs_status`, `idx_workflow_approvals_workflow`, `idx_workflow_approvals_run`, `idx_workflow_approvals_status` | Serve the workflow engine's active-workflow and run/approval status queries. |
| `push_leases` / `push_wake_outbox` / `push_gateway_*` | `push_leases_endpoint_unique` (`UNIQUE`), `push_leases_expiry` (partial), `push_wake_outbox_due`, `push_wake_outbox_recovery`, `push_gateway_challenges_expiry`, `push_gateway_installations_expiry` (partial), `push_gateway_delegations_expiry` (partial), `push_gateway_endpoint_quotas_updated`, `push_gateway_delivery_auth_replays_expiry`, `push_gateway_delivery_request_replays_expiry`, `push_match_queue_due`, `push_match_queue_recovery` | Push-delivery lease claiming, dedup, and expiry sweeps. |
| `community_deletion_requests` / `community_serving_write_leases` / `storage_taxonomy_sweeps` | `community_deletion_requests_runnable`, `community_deletion_requests_lease`, `community_deletion_requests_active_community` (`UNIQUE`), `storage_taxonomy_sweeps_latest`, `community_serving_write_leases_active` | Serve the whole-community deletion workflow's claim/runnable/recovery queries. |
| `relay_invites`, `audit_log`, `api_tokens`, `relay_members`, `git_repo_names`, `product_feedback`, `delivery_log`, `subscriptions` | `relay_invites_expires_at_idx`, `idx_audit_log_hash` (`UNIQUE`), `idx_api_tokens_hash` (`UNIQUE`), `idx_relay_members_role`, `idx_git_repo_names_owner`, `idx_product_feedback_received`, `idx_product_feedback_community_received`, `idx_delivery_log_community_sub` | One representative index per remaining scoped table; grouped here rather than given a row each because none carries a distinguishing structural pattern beyond community-scoped lookup or hash-uniqueness already illustrated above. |

Domain meaning of any of these tables' rows (what a "channel" or a "thread" *is*)
is out of scope here -- no `layers/data/postgres/*.md` sibling for any of them
is merged yet to link to instead (see *Scope and omissions*).

## Migration and versioning mechanism

Index-creating statements are ordinary statements inside the same
`migrations/*.sql` files and the same embedded `sqlx::migrate!` `MIGRATOR`
(`crates/buzz-db/src/migration.rs`) that versions every other schema change.
`run_migrations` holds the exclusive `SCHEMA_DESTRUCTION_LOCK_KEY` session
lock for the whole run, and a source lint enforces that `MIGRATOR.run` has no
call site outside that wrapper -- there is no separate index-specific
migration path. Two constraints specific to index DDL recur across the
migrations that add one:

- **`CREATE INDEX CONCURRENTLY` cannot run inside sqlx's transaction-wrapped
  migrations**, and is additionally unsupported on a partitioned parent table
  (`events`) regardless of transaction wrapping. Every index in this inventory
  is therefore built as a plain, blocking `CREATE INDEX`, which takes a
  `SHARE` lock (blocking writes, not reads) on the table -- or, for `events`,
  a share lock per partition -- for the build's duration. Migrations 0004 and
  0027 both document this explicitly and recommend an operator pre-build a
  large table's index by hand with `CONCURRENTLY` before a brownfield
  deploy.
- **Index creation on the partitioned `events` parent recurses to every
  existing partition and is inherited by every future one.** New monthly
  partitions are created by `crates/buzz-db/src/partition.rs`'s
  `ensure_partition` as a plain `CREATE TABLE ... PARTITION OF events`
  statement with an allowlisted table name and validated, non-parameterized
  date/suffix literals -- the parent's existing indexes attach automatically;
  `partition.rs` contains no index-specific logic of its own.

`schema/schema.sql` is a second, hand-maintained source of truth ("source of
truth for fresh database setup," per its own header) that is expected to
mirror the migrations' cumulative effect but is not generated from them, and
is not kept in lockstep by any enforced mechanism beyond the specific
assertions a given migration's author chooses to add to
`crates/buzz-db/src/migration.rs`'s
`embedded_migrator_contains_consolidated_initial_schema` test -- that test
pins `idx_channels_id_live`'s exact shape (`INCLUDE (community_id)`,
`WHERE deleted_at IS NULL`, not unique) in both the migration and
`schema.sql`. No equivalent assertion exists for most other indexes, and one
concrete drift was found while drafting this node: `idx_events_tags_gin`
(migration 0004) is absent from `schema.sql` entirely, while
`idx_channels_id_live` (migration 0027) was added to both in the same commit.
This is named as a real, unresolved gap in *Scope and omissions*, not
repaired here.

## Access-pattern summary

Application code cites specific index names directly where a query is built
to rely on one, rather than leaving the dependency implicit:

- `crates/buzz-db/src/event.rs`'s `EventQuery.d_tag` field doc comment states
  it is "Pushed into SQL via the `idx_events_parameterized` index."
- The same file's e-tag containment pushdown and its shared-gated-kind
  visibility pushdown both cite `idx_events_tags_gin` by name as the index
  that makes a JSONB `@>` containment check index-served rather than a
  sequential scan across the `events` partitions.
- `migrations/0027_channels_id_lookup_index.sql`'s own comment names the two
  `buzz-db` methods (`Db::communities_of_channels`, `Db::community_of_channel`)
  its covering index serves, and the production wait-event measurement
  (staging writer, `db.r8g.8xlarge`) that justified building it.

Every one of these access paths goes through `buzz-db`, the crate
`architecture-containers-postgres` documents as owning "every typed
data-access module" -- this node does not restate that container-level fact,
only the index-level detail underneath it.

## Lifecycle and retention

Several indexes exist to serve time-based cleanup rather than any read-path
filter named above: `idx_channels_ttl_expiry`, `push_leases_expiry`,
`push_gateway_challenges_expiry`, `push_gateway_installations_expiry`,
`push_gateway_delegations_expiry`, `push_gateway_endpoint_quotas_updated`,
`push_gateway_delivery_auth_replays_expiry`,
`push_gateway_delivery_request_replays_expiry`, and
`relay_invites_expires_at_idx`. The sweep jobs that scan them are out of this
node's scope. Separately, a recurring **partial-index** pattern narrows an
index to the live/active subset of a soft-deleted or flagged table --
`idx_channels_id_live` (`WHERE deleted_at IS NULL`),
`idx_events_parameterized` and `idx_events_not_before` (both
`AND deleted_at IS NULL`), `idx_workflows_enabled` (`WHERE enabled`),
`push_leases_expiry` (`WHERE active`), `idx_reactions_source_event`
(`WHERE reaction_event_id IS NOT NULL`), and the two `push_gateway_*_expiry`
indexes with `WHERE revoked_at IS NULL`. This keeps each index off historical
or inactive rows rather than growing unboundedly with them.

## Consistency semantics

Postgres builds and updates every index in this inventory synchronously,
inside the same transaction that writes the row -- there is no window in
which a committed row is invisible to an index scan that would otherwise find
it, and no separate process to fall behind. This is a direct, checked
contrast with the search subsystem's own recent history: `buzz-relay`'s event
handler code states the prior Typesense-backed search index (updated
asynchronously by a separate `index_event` worker) "are gone," replaced by
`idx_events_search_tsv`, a GIN index over a `GENERATED ALWAYS ... STORED`
column computed by Postgres itself on every insert. Full-text search moved
from an externally-consistent (eventually-consistent, worker-updated) index
to a transactionally-consistent, in-database one; no index in the current
inventory has the older, asynchronous shape.

## Tenancy and security boundaries

Every `CREATE INDEX` and `CREATE UNIQUE INDEX` on a multi-tenant table in
`migrations/0001_initial_schema.sql` leads with `community_id` as its first
column -- both the plain lookup indexes and, more consequentially, every
`UNIQUE` index (`idx_channels_nip29_group`, `idx_channels_dm_hash`,
`idx_users_nip05`, `idx_users_okta`, `idx_api_tokens_hash`,
`idx_audit_log_hash`, `idx_reactions_source_event`). A `UNIQUE` index that
did *not* lead with `community_id` would enforce a false cross-tenant
constraint -- `schema/schema.sql`'s own header names exactly this as one of
its enforced migration-lint obligations. **One index is a deliberate,
documented exception**: `idx_channels_id_live ON channels (id) INCLUDE
(community_id) WHERE deleted_at IS NULL` is intentionally *not*
`community_id`-leading, built to serve two lookups that resolve a channel's
owning community from its bare id -- the migration's own comment states a
`UNIQUE` index here would be wrong, because the same channel id can appear
under more than one community, and names the invariant (`Inv_NonInterference`,
checked elsewhere in `buzz-conformance`) that the surrounding query code, not
the index, is responsible for holding.

## Failure behavior

- **Build-time locking.** Because `CREATE INDEX CONCURRENTLY` is unavailable
  inside sqlx's transaction-wrapped migrations (and unsupported on the
  partitioned `events` parent regardless), building any index in this
  inventory for the first time takes a blocking `SHARE` lock on the target
  table -- reads proceed, writes queue -- for the duration of the build. On a
  small table this is brief; on a large brownfield `events` table an operator
  is expected to pre-build the index by hand with `CONCURRENTLY` before
  upgrading, per migration 0027's own documented workaround.
- **Idempotent re-application.** `idx_channels_id_live` is created with
  `IF NOT EXISTS` specifically so a hand-pre-built index makes the migration a
  no-op rather than an error; most other indexes in the inventory are not
  written this defensively and would fail migration startup if the same
  statement somehow ran twice outside the migrator's own once-only tracking.
- **Checksum pinning.** sqlx checksums every applied migration file; editing
  an index's definition inside an already-applied migration (rather than
  adding a new migration) fails startup on any database that already recorded
  that file's checksum, per the "Additive migration" convention every
  index-adding migration in this inventory states in its own comment.
- **Partition-attach failure mode.** `ensure_partition` treats a
  `42P17`/"would overlap partition" error from Postgres as success (a
  pre-existing catch-all partition already covers the range), not a hard
  failure -- this affects whether a *table* partition is created, and by
  extension whether the parent's indexes have a target to extend into; it is
  not itself an index-specific failure path.

## Scope and omissions

**This node covers** the current inventory of Postgres indexes grouped by
table/concern, the mechanism by which they are created, versioned and
inherited across partitions, real cited access patterns that depend on
specific indexes, their lifecycle/retention shape, their consistency
semantics relative to the removed external search index, the tenancy
convention they follow and its one documented exception, and their failure
behavior at build and migration time.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The Postgres container's existence, connection pooling, and replica topology | `architecture-containers-postgres` (merged) |
| The domain meaning of any indexed table's rows (what a channel, thread, or reaction *is*) | A future `layers/data/postgres/<table>.md` data-entity-shaped node, none of which is merged yet |
| The query planner's actual behavior (whether a given index is chosen at runtime, e.g. via `EXPLAIN`) | Not established by this node; no `EXPLAIN` output was captured while drafting it, only the code comments and doc comments that cite measured staging behavior |
| The sweep/cron jobs that scan the lifecycle-oriented indexes listed above | Out of scope; not traced to their call sites here |
| `Inv_NonInterference`'s own full contract | `crates/buzz-conformance`, not restated here beyond the one citation this node needs |

**No `relationships` beyond `part-of architecture-containers-postgres`.** No
`layers/data/postgres/*.md` sibling node is merged on `origin/launchpad` at
this node's authoring revision -- PR #1875 (this batch's own sibling
documents) is open and unmerged, and declaring an edge to any node in it would
validate in this worktree but fail in CI against `origin/launchpad`, per
`AGENTS.md`'s own relationship rule.

**The `type: layers` choice is a disclosed override, not this node's own
independent reasoning.** `templates/datastore.md`'s evidence ledger reasons a
real datastore instance most plausibly takes `type: architecture`; this node
uses `type: layers` instead because that is the established precedent for
every `layers/data/postgres/*.md` document in this batch. Per
`standards/taxonomy.md`, `type` may be revised later without touching this
node's permanent `id` if a better-fitting value or a future taxonomy decision
supersedes the batch precedent.

**Expected but not verified when this node was written:**

- **Whether `idx_events_tags_gin`'s absence from `schema/schema.sql` is a
  known, accepted gap or an overlooked one was not established.** Named as a
  real discrepancy in *Migration and versioning mechanism* above, not
  resolved either way.
- **No `EXPLAIN` output was captured for any query in this inventory.** Every
  access-pattern claim above is grounded in a code comment or doc comment
  that itself cites a staging measurement or a structural argument (e.g. "the
  PK can't serve this predicate"), not in a query plan captured while
  drafting this node.
- **Whether every one of the 76 `CREATE INDEX` statements is still reachable
  from live application code was not individually confirmed.** The
  *Access-pattern summary* section above cites the specific call sites this
  node found that name an index directly; the full inventory table groups the
  rest structurally without confirming each one's current callers.
