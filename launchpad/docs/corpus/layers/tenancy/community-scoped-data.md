---
id: layers-tenancy-community-scoped-data
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
  - statement: "Migration 0001's header states the schema is one 'in which `community_id` is a first-class, server-resolved key on every tenant-scoped row', names `docs/multi-tenant-conformance.md` as 'the governing contract', and lists four migration-lint obligations: every tenant-scoped table has `community_id NOT NULL`; no UNIQUE/PRIMARY KEY/FK on a scoped table is observable across communities (each leads with `community_id`, or a child row's join carries the community tuple); `channels.community_id` is immutable; and operator-global tables are named in an explicit allowlist rather than implied."
    entry_class: FACT
    evidence:
      - "migrations/0001_initial_schema.sql:1-21"
  - statement: "`docs/multi-tenant-conformance.md` states the rule in prose — a client-supplied `h` tag, if absent, still leaves the event 'community-scoped as `community_id = req.community`' — and its conformance table's 'Channel-less global events and DMs' row lists `events`, `event_mentions`, replaceable/NIP-33 indexes, reactions, thread metadata, and feed tables as all carrying `community_id`, with NIP-33 uniqueness stated as `(community_id, kind, pubkey, d_tag)`; its 'Search / FTS' row states 'every search query filters by `community_id`'; and its 'Channels and channel membership' row states `channels.community_id` is immutable."
    entry_class: FACT
    evidence:
      - "docs/multi-tenant-conformance.md:28-33"
      - "docs/multi-tenant-conformance.md:47"
      - "docs/multi-tenant-conformance.md:48"
      - "docs/multi-tenant-conformance.md:50"
  - statement: "The `channels` table defines `community_id UUID NOT NULL REFERENCES communities(id)`, a primary key `(community_id, id)`, and a `BEFORE UPDATE` trigger `trg_channels_community_id_immutable` (executing the `channels_community_id_immutable()` function) that raises an exception whenever `NEW.community_id IS DISTINCT FROM OLD.community_id` — a channel can never be re-tenanted after creation."
    entry_class: FACT
    evidence:
      - "migrations/0001_initial_schema.sql:74-127"
  - statement: "The `channel_members` table's primary key is `(community_id, channel_id, pubkey)` and its foreign key is the composite `(community_id, channel_id) REFERENCES channels (community_id, id)`, so a membership row cannot reference a channel in a different community even transitively through the foreign key."
    entry_class: FACT
    evidence:
      - "migrations/0001_initial_schema.sql:130-147"
  - statement: "The `users` table defines `community_id UUID NOT NULL REFERENCES communities(id)`, a primary key `(community_id, pubkey)`, and unique indexes on `(community_id, lower(nip05_handle))` and `(community_id, okta_user_id)` — the same pubkey can hold one profile per community without a global collision."
    entry_class: FACT
    evidence:
      - "migrations/0001_initial_schema.sql:155-180"
  - statement: "The `events` table defines `community_id UUID NOT NULL REFERENCES communities(id)`, a primary key `(community_id, created_at, id)`, and every btree index on the table (community lookup, channel timeline, pubkey/kind timeline, kind timeline, soft-delete lookup, replaceable/NIP-33 lookup, `not_before` lookup) leads with `community_id`; a code comment on the community-id index states the scoped query form `WHERE community_id=$ AND id=$` is 'index-served, not a partition scan.'"
    entry_class: FACT
    evidence:
      - "migrations/0001_initial_schema.sql:184-272"
  - statement: "The `event_mentions` table's primary key is `(community_id, pubkey_hex, event_id)`, and a comment above it states 'events MUST carry the community tuple (`e.community_id = m.community_id AND ...`)' when joined against `events`."
    entry_class: FACT
    evidence:
      - "migrations/0001_initial_schema.sql:282-299"
  - statement: "An explicit `_operator_global_tables` registry table (columns `table_name`, `reason`) is the allowlist of tables deliberately exempted from tenant scoping; its own comment states 'any table NOT listed here MUST carry a NOT NULL `community_id` and lead its uniques with it', and the seed rows exempt `communities` ('the tenant registry itself; id IS the community key'), `rate_limit_violations` ('community_id is an attribution label only'), and the registry table itself."
    entry_class: FACT
    evidence:
      - "migrations/0001_initial_schema.sql:621-636"
  - statement: "`EventQuery::for_community` is the only public constructor for an event query, takes a `CommunityId` argument, and its doc comment states '`community_id` has no safe default. This keeps call sites concise while making tenant provenance explicit at construction' — there is no code path that builds an `EventQuery` without one."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/event.rs:118-148"
  - statement: "Across `crates/buzz-db/src/store/event.rs`, every read, soft-delete, upsert-conflict check, and TTL lookup binds `community_id` into its `WHERE` clause as the leading predicate (representative call sites: event fetch by id, count, soft delete, NIP-33 replaceable-event dedup check, mention lookups, and channel TTL lookup) — the scoping is repeated per query, not centralized in one seam, so it is a per-call-site convention backed by the schema's `NOT NULL` and composite-key shape rather than something the type system alone forces."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/event.rs:1016"
      - "crates/buzz-db/src/store/event.rs:1072"
      - "crates/buzz-db/src/store/event.rs:698"
      - "crates/buzz-db/src/store/event.rs:827"
      - "crates/buzz-db/src/store/event.rs:907"
      - "crates/buzz-db/src/store/event.rs:878"
      - "crates/buzz-db/src/store/event.rs:921"
      - "crates/buzz-db/src/store/event.rs:932"
      - "crates/buzz-db/src/store/event.rs:1836"
  - statement: "`crates/buzz-db/src/runtime/migration.rs` carries two Rust unit tests, `all_non_operator_global_tables_have_not_null_community_id` and `scoped_primary_key_unique_and_foreign_key_constraints_lead_with_community_id`, that parse the real concatenated migration SQL (via `migration_sql()`) and assert respectively that every `CREATE TABLE` not named in the `_operator_global_tables` allowlist declares `community_id NOT NULL`, and that every such table's `PRIMARY KEY`, `UNIQUE`, and `FOREIGN KEY` constraints and unique indexes lead with `community_id`; both tests were run this session (`cargo test -p buzz-db --lib migration::`) and both reported `ok`, alongside a third passing test, `channels_community_id_is_immutable_after_insert`, which asserts no migration statement mutates `channels.community_id` and that the `BEFORE UPDATE` guard trigger exists."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/runtime/migration.rs:1418-1454"
      - "cargo_test(-p, buzz-db, --lib, migration::) -> test result: ok. 10 passed; 0 failed; 5 ignored; migration::tests::all_non_operator_global_tables_have_not_null_community_id ... ok, migration::tests::scoped_primary_key_unique_and_foreign_key_constraints_lead_with_community_id ... ok, migration::tests::channels_community_id_is_immutable_after_insert ... ok (run 2026-08-28 against commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5)"
  - statement: "A code comment labeled 'BUG-5 regression' on the `reactions_are_scoped_to_community` test states that the `reactions` table is community-scoped with primary key `(community_id, event_created_at, event_id, pubkey, emoji)`, and that before the fix, `add_reaction` omitted `community_id` (causing a `NOT NULL` violation) while every read/remove filtered by `event_id` only, which the comment names a 'latent cross-tenant bleed' — a real historical defect, not a hypothetical one."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/lib.rs:6779-6787"
  - statement: "`routed_reads_are_confined_to_the_requested_community` is a `#[tokio::test]` in `crates/buzz-db/src/lib.rs`, gated `#[ignore = \"requires Postgres\"]`, that asserts across multiple replica-routing seams that a community-A read never returns a row whose content is marked as belonging to community B (`assert!(!got.iter().any(|c| c.starts_with(\"b-\")), \"{seam}: community B rows leaked into a community A read; got {got:?}\")`)."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/lib.rs:8112-8114"
      - "crates/buzz-db/src/lib.rs:8226-8236"
  - statement: "`CommunityId` (in `buzz-core`, zero I/O dependencies) is an opaque UUID newtype whose only constructor, `from_uuid`, is documented as accepting a UUID 'the server has already established as a community id (e.g. read back from the `communities` table during host resolution)'; the module doc states 'there is deliberately no `community_id` parsed from client input anywhere' and calls the overall guarantee 'a lint-and-review fence, not a compiler fence' because `from_uuid` is `pub`."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/tenant.rs:1-53"
  - statement: "No migration under `migrations/` creates a Postgres `ROW LEVEL SECURITY` policy (`CREATE POLICY` / `ENABLE ROW LEVEL SECURITY` appear zero times across `migrations/*.sql`), even though `docs/multi-tenant-conformance.md`'s 'Migration gates' section names 'community_id, RLS policy' as part of what a tenant-scoped table needs before multi-tenant mode is admitted — the RLS half of that gate was not found implemented at the recorded revision."
    entry_class: FACT
    evidence:
      - "grep_repo(pattern='ROW LEVEL SECURITY|ROW SECURITY|CREATE POLICY', path='migrations/*.sql') -> zero matches, verified 2026-08-28 against commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
      - "docs/multi-tenant-conformance.md:62-64"
  - statement: "Because `CommunityId` cannot be parsed from client input anywhere, and every scoped query-construction path inspected above (`EventQuery::for_community`, the per-call-site `WHERE community_id` predicates) requires one already in hand, the data-layer scoping this node documents is a downstream consequence of correct community binding rather than an independent guarantee: if the host-resolution invariant documented in `architecture-principles-community-is-security-boundary` were violated (a wrong or client-influenced `CommunityId` reaching a query constructor), every schema-level and lint-level protection described here would faithfully scope data to the *wrong* community rather than catch the error, because none of it re-derives or re-checks which community *should* apply."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-core/src/tenant.rs:1-53"
      - "crates/buzz-db/src/store/event.rs:118-148"
      - "launchpad/docs/corpus/architecture/principles/community-is-security-boundary.md"
    confidence: 0.75
  - statement: "Issue #1185's own Objective is to create `launchpad/docs/corpus/layers/tenancy/community-scoped-cache.md` 'as the single canonical concept node for community scoped cache' — a distinct target path from this node's, so the in-memory/Redis pub-sub, presence, typing, and cache-invalidation key-scoping surface named in `docs/multi-tenant-conformance.md`'s 'Redis pub/sub, presence, typing, and cache invalidation' row belongs to that sibling node, not this one."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1185 Objective, cross-referenced against docs/multi-tenant-conformance.md:51"
  - statement: "Issue #1186 requires that every substantive factual claim be traceable to current code, test, specification, accepted decision, migration/configuration, or attributed GitHub evidence, with FACT, INFERENCE and TEAM KNOWLEDGE not conflated, and that the document define the term in one sentence, state boundaries/non-goals, and link related concepts, implementation and verification."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1186 definition of done"
relationships:
  - type: depends-on
    target: architecture-principles-community-is-security-boundary
---

# Community-scoped data: invariant

**Every row in a tenant-scoped Postgres table carries a `community_id` that is
set once, at write time, from the caller's already-resolved
[`CommunityId`](../../architecture/principles/community-is-security-boundary.md),
and every read, update, or delete of that row is reachable only through a
query that also carries that `community_id`.** No table row can be read,
mutated, or referenced across a community boundary through the schema's own
keys, and no query-construction path in `buzz-db` can build a scoped query
without a `CommunityId` already in hand.

## Scope

**Binds:** every Postgres table not named in the `_operator_global_tables`
allowlist — concretely, at minimum, `channels`, `channel_members`, `users`,
`events`, `event_mentions`, and `reactions` (the tables this node's evidence
opened directly). Each such table's `community_id` column is `NOT NULL`, and
every `PRIMARY KEY`, `UNIQUE`, and `FOREIGN KEY` constraint on it leads with
`community_id`, so a row cannot be looked up, joined, or referenced by any
key that omits it. `channels.community_id` additionally cannot be *changed*
after insert — a channel can never be re-tenanted.

**Does not bind:** tables in the `_operator_global_tables` allowlist —
`communities` itself (its `id` *is* the community key), `rate_limit_violations`
(a deployment-health table where `community_id` is an attribution label, not
a scoping key), and `_operator_global_tables` itself, plus whatever later
migrations add to that same allowlist. This node's evidence opened the
allowlist's seed rows only; it does not enumerate every table any later
migration has added to it.

**Every externally-visible read or write, not necessarily every internal
statement:** the invariant is stated at the level of "a caller cannot obtain
or mutate another community's row through the schema's keys," not "no SQL
statement anywhere ever omits a `community_id` filter." A statement that
touches every row of a scoped table without a `community_id` predicate (a
maintenance script, a full-table scan in a migration) is outside this node's
claim unless it is reachable from a request path.

## Enforcement today

This is **schema-shape-enforced, predicate-enforced, and test-enforced** —
not type-system-enforced and not Postgres Row-Level-Security-enforced,
despite `docs/multi-tenant-conformance.md`'s "Migration gates" section naming
RLS as part of the target gate. No migration under `migrations/` creates an
RLS policy; that half of the documented gate was not found implemented.

- **Schema-shape-enforced.** `community_id NOT NULL` plus a composite
  `PRIMARY KEY`/`UNIQUE`/`FOREIGN KEY` leading with it means a row cannot
  exist without a community, and a foreign key from a child table (e.g.
  `channel_members` → `channels`) cannot reference a parent row in a
  different community, because the FK itself is the composite
  `(community_id, ...)` tuple.
- **Predicate-enforced.** Every read, update, and delete path this node's
  evidence opened in `crates/buzz-db/src/store/event.rs` binds `community_id` as a
  leading `WHERE` predicate at the call site. `EventQuery::for_community`
  requires a `CommunityId` argument to construct a query at all — there is
  no unscoped query-builder path — but each SQL statement still repeats its
  own predicate; nothing centralizes it into one seam that every future call
  site is structurally forced to go through.
- **Test-enforced, at the schema-definition level.** `crates/buzz-db/src/runtime/migration.rs`'s
  `all_non_operator_global_tables_have_not_null_community_id` and
  `scoped_primary_key_unique_and_foreign_key_constraints_lead_with_community_id`
  parse the real migration SQL and fail if a new table skips
  `community_id NOT NULL` or a new constraint fails to lead with it; both
  passed when run against this node's recorded revision. This tier catches
  a missing column or constraint at schema-definition time — it says
  nothing about whether a hand-written query's `WHERE` clause is correct,
  which is the tier the BUG-5 regression (below) actually violated.
- **Convention-and-review only, for per-query correctness.** No test in this
  node's evidence asserts that a specific hand-written SQL statement's
  `WHERE` clause includes `community_id`; that is caught only by the schema
  rejecting a write with no `community_id` at all (a `NOT NULL` violation)
  or, for a read/update/delete that supplies the *wrong* `community_id`,
  by nothing at the SQL layer — the BUG-5 regression below is exactly a case
  where a well-formed `community_id` existed on the row but the read/remove
  path never filtered by it.

## Consequence of violation

The `reactions` table's `community_id`-led primary key
(`(community_id, event_created_at, event_id, pubkey, emoji)`) makes the
concrete, historical failure mode explicit rather than assumed: a "BUG-5
regression" comment on `reactions_are_scoped_to_community` states that
before the fix, `add_reaction` omitted `community_id` on write (causing a
`NOT NULL` constraint violation — a 500), and every *read or remove* filtered
by `event_id` alone, which the comment calls a "latent cross-tenant bleed."
The write side failed loudly (`NOT NULL`); the read/remove side would have
failed silently, returning or deleting another community's identically-shaped
row for the same `(event_id, pubkey, emoji)`. That is the shape of harm this
invariant exists to prevent: not a crash, but one community observing or
mutating another community's data because a query's own predicate, not the
schema, was the only thing that should have stopped it.

## Boundary

This node does not describe:

- **How a request's `CommunityId` is resolved and bound in the first
  place.** That is
  [`architecture-principles-community-is-security-boundary`](../../architecture/principles/community-is-security-boundary.md)'s
  claim — host-header resolution, fail-closed rejection, and the 24
  call-site fan-out that calls `bind_community` before any handler runs.
  This node assumes that binding already produced a trustworthy
  `CommunityId` and documents only what happens once persisted rows and
  queries carry it.
- **In-memory or Redis-backed scoping** — pub/sub channel keys, presence
  keys, typing keys, or cache-invalidation payloads. That surface is
  `docs/multi-tenant-conformance.md`'s "Redis pub/sub, presence, typing, and
  cache invalidation" row, and is issue #1185's own separate node
  (`community-scoped-cache.md`), not this one.
- **Postgres Row-Level-Security.** `docs/multi-tenant-conformance.md`'s
  migration-gate language names RLS as part of the target state; this node
  found it unimplemented and says so under *Enforcement today* rather than
  describing a policy that does not exist.
- **Every tenant-scoped table in the schema.** This node's evidence opened
  `channels`, `channel_members`, `users`, `events`, `event_mentions`, and
  `reactions` directly; it does not claim to have audited every table any
  migration has added since, only that the two migration-lint tests would
  catch a `community_id`-shape regression in any of them.

## Relationships

- `depends-on`: `architecture-principles-community-is-security-boundary` —
  this node's claims hold only if the `CommunityId` reaching a query
  constructor was itself correctly and exclusively derived from host
  resolution, per that node's own invariant; a violation upstream would
  make every guarantee described here faithfully apply to the *wrong*
  community rather than catch the error (see the INFERENCE in the evidence
  ledger above).

## Scope and omissions

**This node covers** the Postgres-level data-scoping invariant: which tables
carry `community_id`, how the schema's own keys and constraints shape
enforcement, what the migration-lint test suite checks and does not check,
a concrete historical consequence of the invariant failing, and how this
node's claim relates to and depends on the upstream community-binding
invariant.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| How a request's `CommunityId` is resolved and bound | `architecture-principles-community-is-security-boundary` |
| In-memory/Redis pub-sub, presence, typing, and cache-invalidation scoping | #1185 (`community-scoped-cache.md`, not yet written) |
| The full per-surface obligation table (search internals beyond the community filter, media, git, audit) | `docs/multi-tenant-conformance.md` directly |
| Whether every table added to the schema after this revision still satisfies the invariant | The migration-lint tests catch a shape regression going forward; this node makes no claim about tables added after its recorded revision |

**Expected but not verified when this node was written:**

- **`routed_reads_are_confined_to_the_requested_community` and
  `reactions_are_scoped_to_community` were not executed this session.** Both
  are `#[ignore = "requires Postgres"]` and need a live database; this node
  verified their presence and assertion shape by reading the source, not by
  running them. The two migration-lint tests that *were* run
  (`all_non_operator_global_tables_have_not_null_community_id`,
  `scoped_primary_key_unique_and_foreign_key_constraints_lead_with_community_id`)
  check schema shape, not runtime query behavior.
- **Whether every non-allowlisted table in the schema at this revision was
  individually inspected.** This node opened six representative tables
  directly; the migration-lint tests, not this node's own reading, are what
  cover the remainder.
- **Whether RLS is planned for a future migration.** This node states only
  that it is absent at the recorded revision, not whether its absence is a
  settled decision or an open gap in `docs/multi-tenant-conformance.md`'s
  own gate list.
