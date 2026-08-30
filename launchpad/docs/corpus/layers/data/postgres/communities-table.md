---
id: layers-data-postgres-communities-table
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
  - statement: "node.schema.json's type enum has 13 members (architecture, layers, capabilities, platforms, implementation, interfaces-events, verification, operations, development, release, governance, agent, ingestion) and contains no member named datastore, data-entity, or template; this node uses type: layers, matching the precedent already set by the other layers/data/postgres/* nodes authored in this same batch, rather than either candidate template's own suggested type for a real instance."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "templates/data-entity.md reasons that a real instance written from it -- one domain concept, described by identity, attribute shape, invariants, relationships and provenance -- most plausibly takes type: implementation, while templates/datastore.md reasons that a real instance describing one running storage technology most plausibly takes type: architecture; neither of the 13 enum members is layers-specific to a single table, so this node's type: layers is taken on established batch precedent, not derived independently from either template's own reasoning, and that tension is not resolved here."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/templates/data-entity.md"
      - "launchpad/docs/corpus/templates/datastore.md"
    confidence: 0.6
  - statement: "Issue #1079's own Objective describes this document as 'the single canonical data entity node for communities table,' and its Definition of Done requires that the document define identity/key and semantic ownership, summarize fields by meaning without duplicating generated schema detail, define relationships/lifecycle/invariants, and link authoritative migration/schema and read/write code paths -- a shape that maps onto templates/data-entity.md's six required sections (Identity, Attributes and shape, Invariants, Relationships, Provenance, Storage pointer) rather than onto templates/datastore.md's seven sections (technology & attachment profile, full schema/namespace inventory, migration mechanism, access-pattern summary, operational characteristics), which describe an entire running Postgres instance rather than one table."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1079 issue body, read directly via gh issue view"
  - statement: "migrations/0001_initial_schema.sql defines the communities table as `CREATE TABLE communities (id UUID PRIMARY KEY DEFAULT gen_random_uuid(), host VARCHAR(255) NOT NULL, signing_key BYTEA, created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), CONSTRAINT chk_communities_id_not_nil CHECK (id <> '00000000-0000-0000-0000-000000000000'::uuid))`, followed by `CREATE UNIQUE INDEX idx_communities_host ON communities (lower(host))`."
    entry_class: FACT
    evidence:
      - "migrations/0001_initial_schema.sql:53"
      - "migrations/0001_initial_schema.sql:61"
  - statement: "The comment block immediately preceding the communities table in migrations/0001_initial_schema.sql states: 'Conformance: row zero (host binding). The host map. resolve_host(host) reads exactly one row here to mint the request's TenantContext. This table is OPERATOR-GLOBAL: it is the registry of tenants, not itself tenant-scoped, so it carries no community_id of its own (its id IS the community key).' The same comment states host is stored already-normalized (ASCII-lowercased, trailing dot stripped, default port omitted) and that the UNIQUE index on lower(host) is belt-and-suspenders against a writer forgetting to normalize."
    entry_class: FACT
    evidence:
      - "migrations/0001_initial_schema.sql:39"
  - statement: "migrations/0001_initial_schema.sql's lint-allowlist registry (_operator_global_tables) records communities with the reason 'the tenant registry itself; id IS the community key', alongside rate_limit_violations and the registry table itself -- the only three tables in the schema explicitly exempted from the migration lint's requirement that every other table carry a NOT NULL community_id leading its unique/foreign-key constraints."
    entry_class: FACT
    evidence:
      - "migrations/0001_initial_schema.sql:620"
      - "migrations/0001_initial_schema.sql:633"
  - statement: "crates/buzz_core/src/tenant.rs defines CommunityId as a newtype wrapping uuid::Uuid, and crates/buzz-relay/src/tenant.rs's bind_community path calls buzz_core::tenant::normalize_host on the raw request host before resolving it via a resolve_host trait method whose production implementation (in the same file) delegates to buzz-db's lookup_community_by_host -- so the communities.id column is exactly the value CommunityId wraps, and communities.host is normalized once in buzz-core and stored already-normalized, matching the migration comment's own claim that 'resolution and storage agree by construction.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/tenant.rs"
      - "crates/buzz-relay/src/tenant.rs"
  - statement: "migrations/0003_community_icon.sql adds `icon TEXT` and states in its comment that communities 'is an operator-global registry table (no community_id column by design); this adds a per-row presentation attribute, not tenant data in a shared table', set by relay admins/owners via the kind:9033 command and served in the NIP-11 relay information document."
    entry_class: FACT
    evidence:
      - "migrations/0003_community_icon.sql"
  - statement: "migrations/0016_community_archival.sql adds `archived_at TIMESTAMPTZ` with the comment 'Archived hosts remain reserved by the existing full unique index and continue to count toward owner quotas.'"
    entry_class: FACT
    evidence:
      - "migrations/0016_community_archival.sql"
  - statement: "migrations/0029_community_deletion.sql adds three columns to communities: `deletion_state TEXT NOT NULL DEFAULT 'active' CHECK (deletion_state IN ('active', 'quiescing', 'fenced', 'tombstone'))`, `deletion_fence_generation BIGINT NOT NULL DEFAULT 0 CHECK (deletion_fence_generation >= 0)`, and `deleted_at TIMESTAMPTZ`, under a comment stating 'The community row is never removed: it becomes the permanent name tombstone' and that every existing community-scoped table receives 'the same database-enforced write fence.'"
    entry_class: FACT
    evidence:
      - "migrations/0029_community_deletion.sql:9"
      - "migrations/0029_community_deletion.sql:12"
  - statement: "migrations/0029_community_deletion.sql defines community_write_allowed(target UUID) and assert_community_write_allowed(target UUID) as the two functions that read communities.deletion_state and communities.deletion_fence_generation for a given community id (taking a shared advisory lock keyed by community first); assert_community_write_allowed raises 'community write rejected: community % is missing' if no row is found, and otherwise checks the caller's asserted deletion_executor_community/deletion_fence_generation session GUCs against the row's own lifecycle state and generation before permitting the write."
    entry_class: FACT
    evidence:
      - "migrations/0029_community_deletion.sql:299"
      - "migrations/0029_community_deletion.sql:322"
  - statement: "migrations/0029_community_deletion.sql's enforce_community_write_fence() trigger function calls assert_community_write_allowed against a row's community_id (both OLD and NEW when a cross-community UPDATE would otherwise be possible), and attach_community_write_fence(target REGCLASS) is the helper every future migration must invoke after adding a community_id column, per the migration lint's own enforced contract -- so communities.deletion_state/deletion_fence_generation is the single control-plane state every other community-scoped table's writes are fenced against, not merely a status field on the communities row itself."
    entry_class: FACT
    evidence:
      - "migrations/0029_community_deletion.sql:402"
      - "migrations/0029_community_deletion.sql:472"
  - statement: "migrations/0029_community_deletion.sql's enforce_community_tombstone() trigger, attached BEFORE UPDATE OR DELETE ON communities, rejects any DELETE outright once a row is no longer 'active' or already has deleted_at set ('community tombstones are permanent'), and rejects any UPDATE that changes deletion_state, deletion_fence_generation, or deleted_at unless the caller's session-local buzz.deletion_executor_community and buzz.deletion_fence_generation GUCs match the row's own id and the expected next generation -- so the communities row itself can never be hard-deleted and its deletion-lifecycle columns can only advance through the deletion executor's own guarded path, never an ordinary UPDATE."
    entry_class: FACT
    evidence:
      - "migrations/0029_community_deletion.sql:430"
      - "migrations/0029_community_deletion.sql:468"
  - statement: "crates/buzz-db/src/deletion.rs's postgres-purge step runs `UPDATE communities SET deletion_state = 'tombstone', deleted_at = COALESCE(deleted_at, now()), archived_at = COALESCE(archived_at, now()), signing_key = NULL, icon = NULL WHERE id = $1 AND deletion_state = 'fenced' AND deletion_fence_generation = $2`, and treats any affected-row count other than 1 as a DbError::DeletionSafety -- the terminal step of the whole-community deletion pipeline, run only after every PURGE_SCOPED_TABLES row for that community has already been deleted in the same transaction."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/deletion.rs"
  - statement: "migrations/0030_community_deletion_recovery.sql changes product_feedback's community_id foreign key to `ON DELETE SET NULL` and its own comment states product_feedback and rate_limit_violations are 'deployment-global operator evidence. community_id is provenance, not ownership, so they are neither fenced nor purged with a tenant' -- meaning a communities row's tombstone (which never physically deletes the row per the trigger above) still leaves those two tables' community_id columns nullable rather than fenced the same way tenant data is."
    entry_class: FACT
    evidence:
      - "migrations/0030_community_deletion_recovery.sql"
  - statement: "31 CREATE TABLE / ALTER TABLE statements across migrations/0001 through 0030 declare a `community_id ... REFERENCES communities(id)` foreign key, including channels, users, relay_members, threads, moderation, git_repo, product_feedback, push leases, relay invites, and community_deletion_requests -- communities.id is the parent key of essentially every tenant-scoped table in the schema, not merely a lookup convenience."
    entry_class: FACT
    evidence:
      - "migrations/0001_initial_schema.sql"
      - "migrations/0002_git_repo_names.sql"
      - "migrations/0006_moderation.sql"
      - "migrations/0007_nip_rs_retention.sql"
      - "migrations/0012_push_leases.sql"
      - "migrations/0017_product_feedback.sql"
      - "migrations/0018_push_match_queue.sql"
      - "migrations/0025_relay_invites.sql"
      - "migrations/0029_community_deletion.sql"
  - statement: "crates/buzz-db/src/lib.rs's CommunityRecord struct (returned by lookup_community_by_host) has exactly two fields: `id: CommunityId` (doc comment 'Stable server-resolved community id') and `host: String` (doc comment 'Normalized host that maps to this community'); EnsuredCommunityRecord adds a `created: bool` ('True only when this call inserted the communities row'); OwnedCommunityRecord adds `created_at: DateTime<Utc>` and `archived_at: Option<DateTime<Utc>>`; ArchivedCommunityRecord's host field is documented 'Reserved canonical host' and its archived_at 'Durable first-archive timestamp'."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/lib.rs"
  - statement: "crates/buzz-db/src/lib.rs's lookup_community_by_host reads `SELECT id, host FROM communities WHERE lower(host) = lower($1) AND archived_at IS NULL AND deleted_at IS NULL AND deletion_state = 'active'`, its own doc comment stating 'buzz-db only reads the durable host map' and that the caller owns turning a None result into a fail-closed request error -- so a host that maps to an archived, deleted, or non-active community resolves to no community at all on the tenant-binding path, not to a degraded one."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/lib.rs"
  - statement: "crates/buzz-db/src/lib.rs's lookup_community_by_host_for_management performs the identical lookup without the archived_at/deleted_at/deletion_state filter, and its doc comment marks it 'Operator-plane only' -- the same host/id mapping, deliberately unfiltered for operator tooling that must be able to see a non-active community."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/lib.rs"
  - statement: "crates/buzz-db/src/lib.rs's is_community_active runs `SELECT EXISTS(SELECT 1 FROM communities WHERE id = $1 AND archived_at IS NULL AND deleted_at IS NULL AND deletion_state = 'active')`, and ensure_configured_community (the N=1 deployment startup/config seeding path, per its own doc comment) runs `INSERT INTO communities (host) VALUES ($1) ON CONFLICT (lower(host)) DO UPDATE SET host = communities.host WHERE communities.deletion_state = 'active' AND communities.deleted_at IS NULL RETURNING id, host, (xmax = 0) AS created`, returning a DbError::AccessDenied('community host ... is permanently tombstoned') if the WHERE clause excludes every row -- i.e. a tombstoned host can never be silently re-provisioned by restarting the relay."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/lib.rs"
  - statement: "crates/buzz-db/src/lib.rs's create_community_with_owner takes a per-owner-pubkey Postgres advisory lock (via relay_members::owner_count_advisory_lock_key) before inserting into communities and counting the caller's existing 'owner' rows in relay_members against relay_members::max_communities_per_owner() (an env-overridable limit, BUZZ_MAX_COMMUNITIES_PER_OWNER), rolling back and returning CreateCommunityWithOwnerResult::LimitReached if the count is already at or over the limit -- a communities row is never created without simultaneously enforcing this per-owner cap in the same transaction."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/lib.rs"
      - "crates/buzz-db/src/relay_members.rs"
  - statement: "crates/buzz-db/src/lib.rs's get_community_icon/set_community_icon read and write the icon column directly by community_id with no lifecycle filter, and archive_community_owned_by/unarchive_community_owned_by both UPDATE communities joined to relay_members, requiring the asserted pubkey to hold the 'owner' role for that community and (for archive) that the target host does not equal a separately-passed protected_deployment_host, so the deployment's own configured host cannot be archived by its owner."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/lib.rs"
  - statement: "crates/buzz-db/src/lib.rs's list_communities_owned_by and lookup_community_host are both documented as operator-plane or internal-producer helpers rather than tenant-scoped data-plane reads: list_communities_owned_by's doc comment states callers 'must gate it on deployment-level operator auth before exposing it', and lookup_community_host's doc comment describes it as the reverse of lookup_community_by_host, used by side-effect producers (e.g. workflow actions) that already hold a server-resolved CommunityId and need the host back only for labelling, 'never used to re-derive the community.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/lib.rs"
  - statement: "No production INSERT or UPDATE statement against communities.signing_key was found anywhere under crates/ at the checked revision; the only write is the NULLing UPDATE in the deletion pipeline's tombstone step, and the only place a non-null value is ever inserted is a test fixture in crates/buzz-search/tests/fts_integration.rs (`INSERT INTO communities (id, host, signing_key) VALUES ($1, $2, $3)`)."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/deletion.rs"
      - "crates/buzz-search/tests/fts_integration.rs"
  - statement: "Whether communities.signing_key is a reserved column awaiting a not-yet-built feature (e.g. relay-level Nostr signing) or genuinely dead schema was not established anywhere found this session -- no migration comment, code comment, issue, or PR explaining its purpose was located, and this gap is intentionally left open rather than guessed at."
    entry_class: INFERENCE
    evidence:
      - "migrations/0001_initial_schema.sql:56"
      - "crates/buzz-db/src/deletion.rs"
    confidence: 0.5
  - statement: "architecture-containers-postgres is a validated node on origin/launchpad at the checked revision (status: draft), describing buzz-db as 'the crate that owns Postgres connection pooling, migrations, and every typed data-access module' -- confirmed with git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus, which also confirms no layers/data/postgres/* sibling table node exists there yet, so no relationships edge to a sibling table document is declared."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/containers/postgres.md"
      - "git_ls_tree(ref='origin/launchpad', path='launchpad/docs/corpus') -> confirms architecture/containers/postgres.md present, no layers/data/postgres/* present"
relationships:
  - type: part-of
    target: architecture-containers-postgres
---

# communities table

## Purpose & scope

This node documents the `communities` table in Buzz's Postgres schema: the
row-zero host-to-tenant map every request is bound against, and the control
plane for the whole-community deletion lifecycle. It is a data-entity-level
view of one table -- identity, field meaning, invariants, relationships and
provenance -- not a full description of the `buzz-db` crate or the Postgres
container it runs in, which
[`architecture-containers-postgres`](../../../architecture/containers/postgres.md)
already covers at a higher level; this node is `part-of` that container
document. It does not restate column-by-column SQL types the migrations
already declare precisely -- see *Attributes and shape* below for what it
covers instead.

## Identity and semantic ownership

`communities` is the tenant registry itself. Its own `id` column **is** the
community key server-side code calls `CommunityId` -- there is no separate
tenant identifier layered on top. The table is explicitly registered as
**operator-global**, not tenant-scoped: it is the one place in the schema
that legitimately carries no `community_id` column of its own, and the
migration lint's own allowlist records the reason verbatim: "the tenant
registry itself; id IS the community key."

The table's other unique axis is `host`: a `UNIQUE INDEX ... (lower(host))`
makes the normalized host the second way to resolve a community, and the
buzz-core/buzz-relay tenant-binding path (`normalize_host` in `buzz-core`,
`resolve_host`/`bind_community` in `buzz-relay`, backed by `buzz-db`'s
`lookup_community_by_host`) normalizes a request's `Host` header the same
way before ever touching the table, so resolution and storage are built to
agree rather than merely happening to.

## Attributes and shape

Fields, by meaning rather than by restating the `CREATE TABLE`/`ALTER TABLE`
statements verbatim (see *Migration history* for the authoritative
definitions):

- **`id`** -- the community's permanent identity; the value wrapped by
  `CommunityId` everywhere else in the codebase.
- **`host`** -- the normalized (lowercased, no trailing dot, no default
  port) hostname this community currently answers to. Reserved even while
  archived or tombstoned, so a retired host can never be silently reused by
  a different community.
- **`signing_key`** -- a `BYTEA` column present since the initial schema.
  No production code path writes a non-null value at the checked revision;
  it is only ever nulled (by the deletion pipeline) or set from a test
  fixture. Its intended purpose is not established anywhere this node's
  research reached -- see *Scope and omissions*.
- **`created_at`** -- row creation time, set once, never updated.
- **`icon`** -- an optional NIP-11 `icon` value (an `http(s)` URL or a small
  `data:image/*` URL), settable by a relay admin/owner via the kind:9033
  command and served back through the NIP-11 relay information document.
  Validated and size-capped at that write path, not by the column itself.
- **`archived_at`** -- when set, the community is soft-retired: its host
  stays reserved and still counts toward the owner's community quota, but
  the community no longer resolves on the ordinary request-binding path.
- **`deletion_state`** -- one of `active`, `quiescing`, `fenced`, or
  `tombstone`. This is the control-plane state every other community-scoped
  table's write fence checks (see *Lifecycle and invariants*), not merely a
  status label on this row.
- **`deletion_fence_generation`** -- a monotonically-advancing counter the
  deletion executor presents alongside its identity claim to prove it is
  acting on the current, not a stale, deletion attempt.
- **`deleted_at`** -- set once deletion reaches its terminal step. The row
  itself is never physically deleted (see *Lifecycle and invariants*), so
  this timestamp -- not row absence -- is what "deleted" means for this
  table.

## Lifecycle and invariants

**A `communities` row is never hard-deleted.** A dedicated trigger
(`enforce_community_tombstone`, attached `BEFORE UPDATE OR DELETE`) rejects
any `DELETE` outright once a row has left the `active` state or already has
`deleted_at` set, and rejects any ordinary `UPDATE` that touches
`deletion_state`, `deletion_fence_generation`, or `deleted_at` unless the
caller presents matching `buzz.deletion_executor_community` /
`buzz.deletion_fence_generation` session-local settings for the row's own
id and expected next generation. In practice this means the deletion
lifecycle can only be advanced by the guarded deletion executor path in
`crates/buzz-db/src/deletion.rs`, never by an arbitrary `UPDATE communities`
statement.

**The deletion lifecycle's terminal step nulls two columns.** The
postgres-purge stage sets `deletion_state = 'tombstone'`, stamps
`deleted_at`/`archived_at` if unset, and nulls `signing_key` and `icon` --
run only after every other tenant-scoped table's rows for that community
have already been purged in the same transaction, and only if exactly one
row is affected (any other count is treated as a deletion-safety error, not
silently ignored).

**Every other community-scoped table's writes are fenced against this
table's own lifecycle columns.** `assert_community_write_allowed` reads
`deletion_state`/`deletion_fence_generation` for a target community id
(under a shared advisory lock) and raises if the community is missing or
not `active`; a trigger function
(`enforce_community_write_fence`/`attach_community_write_fence`) wires this
check onto every table that carries a `community_id`, and the migration
lint enforces that every future migration adding a `community_id` column
also attaches the fence. `communities.deletion_state` is therefore not a
local status field -- it is the single piece of state the entire
multi-tenant write path is gated on.

**An owner may create at most a configurable number of communities.**
`create_community_with_owner` takes a per-owner-pubkey advisory lock, then
checks the caller's existing `role = 'owner'` count in `relay_members`
against an env-overridable limit before inserting the new `communities` row
and its owner membership row in the same transaction -- the cap is enforced
atomically with creation, not as a separate check that could race it.

**A tombstoned host can never be silently re-provisioned.**
`ensure_configured_community` -- the startup seeding path for single-tenant
deployments -- only updates (or inserts) a row whose `deletion_state` is
still `active` and `deleted_at` is still null; if a host has already been
tombstoned, the same `INSERT ... ON CONFLICT` returns no row and the caller
gets an access-denied error rather than quietly resurrecting the old
community identity under its old host.

## Relationships

**In code:** 31 `CREATE TABLE`/`ALTER TABLE` statements across the
migration history declare a `community_id ... REFERENCES communities(id)`
foreign key -- essentially every tenant-scoped table in the schema
(`channels`, `users`, `relay_members`, threads, moderation, `git_repo`,
`product_feedback`, push leases, relay invites, and
`community_deletion_requests` among them) is a child of this table. Two
tables deliberately loosen that edge: `migrations/0030` changes
`product_feedback`'s foreign key to `ON DELETE SET NULL`, alongside
`rate_limit_violations`, because both are "deployment-global operator
evidence" whose `community_id` is provenance rather than tenant ownership,
and neither is fenced or purged the way real tenant data is.

**In the corpus:** this node is `part-of`
[`architecture-containers-postgres`](../../../architecture/containers/postgres.md),
the container-level document for the Postgres instance this table lives
in. No sibling `layers/data/postgres/*` table node is merged to
`origin/launchpad` at the checked revision, so no `references` edge to a
sibling table document is declared here -- see *Scope and omissions*.

## Migration history

| Migration | Change |
|---|---|
| `migrations/0001_initial_schema.sql` | Creates the table: `id`, `host`, `signing_key`, `created_at`; unique index on `lower(host)`; registers `communities` in `_operator_global_tables`. |
| `migrations/0003_community_icon.sql` | Adds `icon TEXT`, additive, explicitly documented as a per-row presentation attribute rather than tenant data. |
| `migrations/0016_community_archival.sql` | Adds `archived_at TIMESTAMPTZ`. |
| `migrations/0029_community_deletion.sql` | Adds `deletion_state`, `deletion_fence_generation`, `deleted_at`; creates `community_deletion_requests` (FK to this table); defines the write-fence and tombstone-protection functions/triggers described above. |
| `migrations/0030_community_deletion_recovery.sql` | Loosens `product_feedback`'s foreign key to this table to `ON DELETE SET NULL`; does not itself alter the `communities` table's own columns. |

All five are applied, in this numeric order, by the single embedded
`sqlx::migrate!` migrator in `crates/buzz-db/src/migration.rs`, which the
same crate documents as holding an exclusive schema-destruction lock for
the whole run.

## Access patterns

All reads and writes below live in `crates/buzz-db/src/lib.rs` unless noted,
and are the only production call sites this node found touching the table
directly (test-only helpers that insert fixture rows are not included):

| Method | Purpose |
|---|---|
| `lookup_community_by_host` | Tenant-binding read: host -> `CommunityRecord`, filtered to `active`/not archived/not deleted. Backs `buzz-relay`'s `resolve_host`. |
| `lookup_community_by_host_for_management` | Same lookup, unfiltered by lifecycle state; operator-plane only. |
| `is_community_active` | Existence + `active`-state check by id. |
| `list_communities_owned_by` | Operator-plane: communities where a pubkey holds `owner` in `relay_members`. |
| `lookup_community_host` | Reverse lookup (id -> host) for internal producers that already hold a `CommunityId`, for labelling only. |
| `get_community_icon` / `set_community_icon` | Read/write the `icon` column, backing the kind:9033 command and NIP-11 serving path. |
| `ensure_configured_community` | Idempotent insert-or-touch for the N=1 startup seeding path. |
| `create_community_with_owner` | Atomic create-with-owner, advisory-locked and quota-enforced. |
| `archive_community_owned_by` / `unarchive_community_owned_by` | Owner-authorized soft archive/restore. |
| `crates/buzz-db/src/deletion.rs` postgres-purge step | The guarded tombstone `UPDATE` that terminates the deletion lifecycle. |

Every method above is instrumented under `#[datastore_span(..., system =
"postgresql")]` per `buzz-db`'s tracing convention, except the
`deletion.rs` tombstone update, which runs inside the deletion executor's
own transaction-scoped checkpoint instrumentation instead.

## Scope and omissions

**This node covers** the `communities` table's identity/key semantics,
field meaning, deletion/archival lifecycle and its role as the write-fence
control plane, its relationships to other tables and to the corpus, its
migration history, and the `buzz-db` methods that read and write it.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The Postgres container's own technology, version, connection pooling, and its role among Buzz's other datastores | `architecture-containers-postgres` |
| Full column-by-column SQL type detail (lengths, exact constraint syntax) | The migration files cited above, which are authoritative |
| Domain meaning of the tenant-scoped tables that reference this one (channels, users, etc.) | Their own future data-entity nodes, not yet authored |
| The evidence-class contract, citation shapes, and node-creation procedure this document follows | `launchpad/docs/corpus/AGENTS.md`, `launchpad/docs/corpus/standards/evidence.md` |

**The `type: layers` versus `type: implementation`/`type: architecture`
tension is disclosed, not resolved, per `standards/taxonomy.md`'s own
guidance to name an imperfect fit rather than silently pick one.** Neither
candidate template's own reasoning independently arrives at `layers`; this
node follows the precedent already established by its sibling
`layers/data/postgres/*` documents in the same batch for cross-document
consistency.

**Expected but not verified when this node was written:**

- **What `communities.signing_key` is for.** No migration comment, code
  comment, issue, or PR explaining its purpose was located; it has no
  production write path today beyond being nulled on deletion.
- **Whether any environment currently sets `BUZZ_MAX_COMMUNITIES_PER_OWNER`
  away from its compiled default.** The per-owner community cap is
  enforced in code regardless, but this node did not check any specific
  deployment's configured value -- that is a deployment-level fact, not a
  data-entity fact.
- **No sibling `layers/data/postgres/*` table node exists on
  `origin/launchpad` yet**, so this node's own inbound/outbound edges to
  other table-level documents are necessarily absent today and should be
  revisited once siblings merge.
