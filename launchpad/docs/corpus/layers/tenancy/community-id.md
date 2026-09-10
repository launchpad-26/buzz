---
id: layers-tenancy-community-id
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
  - statement: "communities is defined as `CREATE TABLE communities (id UUID PRIMARY KEY DEFAULT gen_random_uuid(), host VARCHAR(255) NOT NULL, signing_key BYTEA, created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), CONSTRAINT chk_communities_id_not_nil CHECK (id <> '00000000-0000-0000-0000-000000000000'::uuid))`, with a comment stating the table 'is OPERATOR-GLOBAL: it is the registry of tenants, not itself tenant-scoped, so it carries no community_id of its own (its id IS the community key)'."
    entry_class: FACT
    evidence:
      - "migrations/0001_initial_schema.sql"
  - statement: "buzz-core's tenant module defines CommunityId as `pub struct CommunityId(Uuid)` -- an opaque UUID newtype whose doc comment states 'there is deliberately no community_id parsed from client input anywhere; a CommunityId only ever originates from host resolution or from a DB row the server already scoped', constructible only via the non-parsing `CommunityId::from_uuid`."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/tenant.rs"
  - statement: "TenantContext, the resolved tenant of an in-flight request, carries a CommunityId and can only be constructed by TenantContext::resolved, whose doc comment restricts its call site to 'the host-resolution path (the function that maps a connection's host to a communities row)'; every other call site takes `&TenantContext` and only reads it."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/tenant.rs"
  - statement: "The module doc comment for buzz-core::tenant states this is 'a lint-and-review fence, not a compiler fence': TenantContext::resolved and CommunityId::from_uuid are pub so the host-resolution path in another crate (buzz-relay) can call them, which means a determined caller elsewhere could call them too -- the type system removes only the accidental path (deserializing a client-chosen community id), not every deliberate misuse."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/tenant.rs"
  - statement: "channels.community_id is enforced immutable by a database trigger: `channels_community_id_immutable()` raises `channels.community_id is immutable (channel % cannot be re-tenanted)` whenever `NEW.community_id IS DISTINCT FROM OLD.community_id`, installed as `trg_channels_community_id_immutable BEFORE UPDATE ON channels`."
    entry_class: FACT
    evidence:
      - "migrations/0001_initial_schema.sql"
  - statement: "Every tenant-scoped table in the initial schema (channels, channel_members, events, thread_metadata, and the rest) declares `community_id UUID NOT NULL REFERENCES communities(id)`, and several -- for example channels -- key their primary key or unique indexes as a tuple led by community_id (`PRIMARY KEY (community_id, id)` per its own migration comment: 'Channel UUIDs stay valid wire identifiers, but they are NOT globally unique'), rather than treating the row's own id as globally unique on its own."
    entry_class: FACT
    evidence:
      - "migrations/0001_initial_schema.sql"
  - statement: "buzz-db's CommunityRecord (returned by `lookup_community_by_host`), EnsuredCommunityRecord, and CreatedCommunityRecord each carry a `pub id: CommunityId` field doc-commented 'Stable server-resolved community id', separate from the mutable `host` field on the same struct -- the identity and the presentation/routing attributes are modeled as distinct fields even where they are read back together."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/lib.rs"
  - statement: "buzz-db's `lookup_community_by_host` reads `id` and `host` from `communities` and wraps the id as `CommunityId::from_uuid(id)` before returning it -- the one production HostResolver impl (`buzz_db::Db`, in crates/buzz-relay/src/tenant.rs) adapts this Postgres-read id directly into the seam's CommunityId, with no client-supplied value in the path."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/lib.rs"
      - "crates/buzz-relay/src/tenant.rs"
  - statement: "Later migrations add lifecycle state to a communities row -- `archived_at` (migration 0016), and `deletion_state TEXT NOT NULL DEFAULT 'active' CHECK (deletion_state IN ('active', 'quiescing', 'fenced', 'tombstone'))` plus `deleted_at` (migration 0029) -- but every UPDATE statement against `communities` found in buzz-db (icon, host, signing_key, archival/deletion state) targets those columns by `WHERE id = $1`; none of them assigns to `id` itself, and no ALTER TABLE in the migrations directory ever redefines that column."
    entry_class: FACT
    evidence:
      - "migrations/0016_community_archival.sql"
      - "migrations/0029_community_deletion.sql"
      - "crates/buzz-db/src/lib.rs"
  - statement: "Because no UPDATE statement in the searched code path assigns to communities.id, and the column carries no trigger analogous to channels' community_id-immutability trigger forbidding such an assignment, a community's id is write-once in practice today by the absence of any code path that changes it, not by a database-enforced immutability guarantee comparable to the one channels.community_id has."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-db/src/lib.rs"
      - "migrations/0001_initial_schema.sql"
    confidence: 0.7
  - statement: "docs/multi-tenant-conformance.md states the row-zero contract as `req.community = resolve_host(connection.host)`, bound at connection establishment before any handler observes tenant data, and separately states for the 'Row zero: host binding' surface that the required DB/index scope is 'communities(host, id, signing_key, ...); every scoped table references immutable community_id.'"
    entry_class: FACT
    evidence:
      - "docs/multi-tenant-conformance.md"
  - statement: "The merged corpus node architecture-principles-host-selects-community documents the mechanism that mints a CommunityId (bind_community, normalize_host, the communities.host unique index) as the row-zero selection invariant; the merged corpus node architecture-principles-community-is-security-boundary documents the same CommunityId/TenantContext pairing as the boundary no client-supplied signal may override. Both are read directly as the recorded revision's account of this same identifier's role, not restated here."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/principles/host-selects-community.md"
      - "launchpad/docs/corpus/architecture/principles/community-is-security-boundary.md"
  - statement: "crates/buzz-db/src/runtime/migration.rs carries executable, migration-SQL-parsing unit tests that verify community_id's schema role directly: all_non_operator_global_tables_have_not_null_community_id asserts every non-operator-global table declares community_id NOT NULL; scoped_primary_key_unique_and_foreign_key_constraints_lead_with_community_id asserts every scoped table's PK/unique/FK constraints lead with community_id; and channels_community_id_is_immutable_after_insert asserts both that no migration statement re-tenants channels.community_id and that a BEFORE UPDATE trigger/function guard rejecting OLD.community_id <> NEW.community_id exists in the migrations. This is a real instance of the static migration-lint checking crates/buzz-core/src/tenant.rs's own doc comment gestures at, run by parsing migration_sql() rather than requiring a live database."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/runtime/migration.rs"
  - statement: "Sibling issue #1104 (layers/identity/community-identity.md) is scoped, per this task's own batch dispatch brief, to the identity/addressability angle of a community -- host-binding as the outward mechanism a client uses to reach a community, and NIP-11 presentation such as the workspace icon (added in migration 0003_community_icon.sql) -- distinct from this node's tenancy-key angle (the internal communities.id as the row-scoping identifier). At the recorded revision, #1104's PR (#1811) is open and unmerged, so launchpad/docs/corpus/layers/identity/community-identity.md does not exist on origin/launchpad or in this worktree and is not a valid relationships target."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1183 and #1104 (batch dispatch brief); launchpad-26/buzz#1811 (PR), checked via gh pr list --search 1104"
relationships:
  - type: references
    target: architecture-principles-host-selects-community
  - type: references
    target: architecture-principles-community-is-security-boundary
---

# Concept: community id (the internal tenancy key)

## Definition

**A community id is the UUID value in `communities.id` that every tenant-scoped
row in Buzz's Postgres schema carries as `community_id`, and that the relay
uses in-process as `buzz_core::tenant::CommunityId` -- the value that answers
"which tenant does this row, request, or cache key belong to?"**

It is not itself a lookup key a client supplies: `communities` is the
operator-global tenant registry -- its own row comment states the table
"carries no `community_id` of its own (its `id` IS the community key)" -- and
`CommunityId` in code is an opaque newtype around a `Uuid` that can only be
constructed from a value the server already trusts (`CommunityId::from_uuid`,
called only from a Postgres row already scoped, or from
`TenantContext::resolved` inside host resolution). There is no parse-from-JSON
or `Deserialize` path for it anywhere in the codebase.

**What this is not.** A community id is not the mechanism that *produces* a
`CommunityId` for a given request (that is host binding -- `resolve_host`,
`bind_community`, and the `communities.host` unique index -- documented by the
merged `architecture-principles-host-selects-community` node) and it is not
the community's outward-facing presentation or addressability (its host name
as a client-visible address, its NIP-11 `icon`, and related identity facts --
scoped to sibling issue #1104's `layers/identity/community-identity.md`, not
yet merged). This node is about the identifier itself: what it is, where it
lives, and what depends on it staying fixed.

## Background

Every tenant-scoped table added since the multi-tenant rewrite (migration
`0001_initial_schema.sql`) declares `community_id UUID NOT NULL REFERENCES
communities(id)`, and several key their primary key or a unique index as a
tuple *led by* `community_id` rather than trusting the row's own id to be
globally unique. `channels` is the clearest example: its primary key is
`(community_id, id)`, and its own migration comment explains why -- "Channel
UUIDs stay valid wire identifiers, but they are NOT globally unique" -- because
the conformance model requires the same channel UUID to be able to exist,
legitimately, in two different communities without collision. The community id
is therefore not a decorative label on a row; it is a component of how rows
are addressed at all in a multi-tenant schema.

That same load-bearing role is why `channels.community_id` carries its own
database trigger (`trg_channels_community_id_immutable`) that raises an
exception if an `UPDATE` ever changes it: a channel cannot be silently
"re-tenanted" after creation. `communities.id` itself has no comparable
trigger, but no code path found in `buzz-db` ever assigns to it -- every
`UPDATE communities ...` statement targets `host`, `icon`, `signing_key`, or a
lifecycle column (`archived_at`, `deletion_state`, `deleted_at`), always
scoped `WHERE id = $1`, never `SET id = ...`. In practice the id is write-once
from creation (`DEFAULT gen_random_uuid()`) through archival and deletion; only
its absence of a redefining code path establishes that today, not a database
constraint as explicit as the one `channels.community_id` has.

**Verification.** The community_id-leads-every-scoped-key shape above is not
only prose convention: `crates/buzz-db/src/runtime/migration.rs` carries executable
unit tests that parse the migration SQL directly and assert it --
`all_non_operator_global_tables_have_not_null_community_id`,
`scoped_primary_key_unique_and_foreign_key_constraints_lead_with_community_id`,
and `channels_community_id_is_immutable_after_insert` (which checks both that
no migration statement re-tenants `channels.community_id` and that a `BEFORE
UPDATE` trigger guard against it exists). This is a concrete instance of the
"migration-lint harness" `buzz-core::tenant`'s own doc comment refers to, and
it runs by parsing `migration_sql()` rather than needing a live database.

## Use cases

A reader needs this concept to answer questions like:

- **"What makes two rows the same tenant's data?"** They share the same
  `community_id` value, which is `communities.id` for the community that owns
  them. This is the scoping key behind every isolation guarantee
  `architecture-principles-community-is-security-boundary` describes.
- **"Can a client tell the server which community a request is for?"** No --
  not through this identifier. `CommunityId` cannot be parsed from client
  input; it only ever comes from a value the server already trusts (a
  Postgres row, or the result of host resolution). A client-supplied `h` tag
  or token stamp may *narrow* behavior inside an already-resolved community,
  but cannot mint or override the `CommunityId` itself.
  See `architecture-principles-host-selects-community` for the resolution
  mechanism that does mint one.
  See `docs/multi-tenant-conformance.md` for the full per-surface obligation
  table this identifier underlies.
- **"Why does `channels`' primary key include `community_id` instead of just
  `id`?"** Because a channel's own UUID is not globally unique across
  communities by design; the composite key is how the schema lets the same
  UUID exist twice, once per community, without collision.
- **"Can a community's id ever change?"** Not observed in this codebase: it is
  set once at creation and never reassigned by any code path found, including
  through archival and deletion -- those lifecycle states change other columns
  on the same row, not `id`.

## Related resources

This node's front matter carries two `references` relationships rather than
restating their content here, per `AGENTS.md`'s and the `concept.md`
template's "links instead of duplicating" guidance:

- `architecture-principles-host-selects-community` -- the row-zero mechanism
  that mints a `CommunityId` for an in-flight request from the connection's
  host. This node describes the identifier that mechanism produces; that node
  describes how it produces it.
- `architecture-principles-community-is-security-boundary` -- the invariant
  that no client-supplied signal may override the `CommunityId` a request was
  bound to. This node describes the identifier that invariant protects; that
  node describes why nothing may substitute for it.

A third edge -- to sibling issue #1104's `layers/identity/community-identity.md`
-- is named in prose only (see *Scope and omissions* below), because that
node does not exist on `origin/launchpad` yet.

## Scope and omissions

**This document covers** what `communities.id` / `CommunityId` is, why it is
the composite-key component that makes tenant-scoped rows addressable at all,
its write-once behavior in practice, and its boundary against the host-binding
mechanism and the community's outward identity/addressability.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| How a `CommunityId` gets bound to an in-flight request from a connection's host (`resolve_host`, `bind_community`, `normalize_host`) | `architecture-principles-host-selects-community` (merged) |
| Why no client-supplied signal may override the host-resolved community | `architecture-principles-community-is-security-boundary` (merged) |
| The community's outward-facing identity and addressability -- its host as a client-visible address, NIP-11 presentation, the `icon` column | sibling issue #1104, `layers/identity/community-identity.md` (open PR #1811, not yet merged) |
| The full per-surface tenant-scoping obligation table (search, pub/sub key prefixing, media, git, audit) | `docs/multi-tenant-conformance.md` |
| Community lifecycle states (`archived_at`, `deletion_state`, quiescing/fenced/tombstone) as their own concept | not yet a corpus node at the recorded revision |

**Expected but not verified when this node was written:**

- Whether `communities.id` is ever reassigned by a code path outside
  `crates/buzz-db/src` (for example a one-off operational script, or SQL run
  directly against the database) was not checked -- only `buzz-db`'s own
  `UPDATE communities` statements were searched.
- Whether a migration-lint or CI check exists anywhere that would reject a
  future `UPDATE communities SET id = ...` statement was not found by search;
  the write-once property recorded above is observed current behavior, not a
  guarantee enforced the way `channels.community_id`'s trigger enforces its
  own immutability.

**No `relationships` entry targets `layers-identity-community-identity`.**
Per `AGENTS.md`'s creation procedure, a relationship target must already be
merged on the branch being merged into (`origin/launchpad`); sibling issue
#1104's PR (#1811) is open and unmerged at the recorded revision, so that id
does not exist on `origin/launchpad` and is not a legitimate target. The two
`relationships` entries this node does carry
(`architecture-principles-host-selects-community` and
`architecture-principles-community-is-security-boundary`) were checked against
`git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus` before
being added, per the same procedure's warning against assuming a target
resolves just because it exists in the local worktree. The edge to #1104's
node is left as prose naming the future task, not a typed edge, until #1811
merges.
