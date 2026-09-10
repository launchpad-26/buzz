---
id: implementation-crates-buzz-db
type: implementation
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 76a0a4ebbe4bc4d852b0d04362ed768620da34b3."
    entry_class: FACT
    evidence:
      - "commit 76a0a4ebbe4bc4d852b0d04362ed768620da34b3"
  - statement: "buzz-db's Cargo.toml describes it as \"Postgres event store and data access layer for Buzz\" and its dependency list carries no dependency on buzz-relay, buzz-auth, buzz-pubsub, buzz-search or buzz-workflow -- only buzz-core, buzz-datastore-tracing, sqlx, tokio, serde/serde_json, uuid, chrono, hex, sha2, tracing, thiserror, nostr, rand and metrics."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/Cargo.toml"
  - statement: "buzz-db/src/lib.rs's own doc comment states the crate is physically split behind a crate-root compatibility facade into two internal, non-public namespaces: `runtime` (pool construction, writer/replica routing, transactions, sessions, metrics, health support, migrations) and `store` (domain-specific SQL, row mapping, locking, mutation rules, indexes, focused persistence tests); `lib.rs` re-exports the public API (`Db`, `DbConfig`, `DbPoolStats`, `ReadSession`, `migration`, `replica_fence`, `insert_mentions`, `error`) plus 27 `pub use store::{...}` domain modules, so `runtime`/`store` are an internal reorganization, not a change to the crate's public surface."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/lib.rs"
  - statement: "crates/buzz-db/src/store/mod.rs enumerates exactly 27 domain-owned persistence modules: admin_moderation, allowlist, api_token, archived_identities, channel, channel_members, community, deletion, dm, event, feed, git_repo, moderation, partition, product_feedback, push, reaction, relay_admin_actions, relay_invite, relay_members, relay_operators, reminder, replaceable, thread, usage, user, workflow."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/mod.rs"
  - statement: "crates/buzz-db/src/runtime/mod.rs defines the `Db` handle (Arc-backed pool, cheap Clone), `DbConfig`, `insert_mentions`/`insert_mentions_in_transaction` (chunked multi-row p-tag mention inserts, ON CONFLICT DO NOTHING, 5,000-row chunks to stay under Postgres's 65,535 bind-parameter cap), `ReadSession`/`ReadSessionInner` (a request-scoped snapshot-pinned reader transaction that degrades to the writer mid-request on failure), and `RoutePredicate`/`RouteDecision`/`route_proof::ChannelScoped` -- a typestate proof-token mechanism where `ChannelScoped` can only be constructed by three named constructors (pinned-channel query predicate, thread-metadata inner join, or a bare channel-id argument), each documented as proving the query is scoped to a `channel_id IS NOT NULL` domain, which is what makes the `Covered`/`BoundedOrCovered` routing arms sound against the migration-0021 floor guard."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/runtime/mod.rs"
  - statement: "crates/buzz-db/src/error.rs's `DbError` enum carries `AuthEventRejected` and `EphemeralEventRejected(u16)` variants alongside driver/migration/serde passthroughs and domain errors (`ChannelNotFound`, `MemberNotFound`, `AccessDenied`, `ServingWritesNotDrained`, `DeletionSafety`, `LastOperator`); `runtime::Db::insert_event_with_serving_write_guard` returns `DbError::AuthEventRejected` for kind 22242 and `DbError::EphemeralEventRejected` for kinds in buzz_core::kind::is_ephemeral before any SQL executes, which is the enforcement point for the two storage-exclusion invariants `architecture-containers-postgres.md` names at the crate-doc level."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/error.rs"
      - "crates/buzz-db/src/runtime/mod.rs"
  - statement: "crates/buzz-db/src/runtime/migration.rs's `run_migrations` wraps the embedded `sqlx::migrate!(\"../../migrations\")` run inside `with_exclusive_schema_destruction_lock`, which takes Postgres advisory lock `SCHEMA_DESTRUCTION_LOCK_KEY` -- a constant now defined in `crates/buzz-db/src/store/deletion.rs`, not in the migration module itself -- and the migration module's own doc comment states a source lint (`migration_execution_cannot_bypass_schema_destruction_lock`) enforces `MIGRATOR.run` has no other call site; after running pending migrations the same locked path re-verifies `replica_fence::verify_floor_guard_catalog` against the live `events` parent table and every partition."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/runtime/migration.rs"
      - "crates/buzz-db/src/store/deletion.rs"
  - statement: "`architecture-containers-postgres.md` (recorded revision a44cf52fc740ebebbdd671427480d14f0bce0115) cites implementation paths `crates/buzz-db/src/migration.rs` and `crates/buzz-db/src/replica_fence.rs`; at this node's recorded revision (76a0a4ebbe4bc4d852b0d04362ed768620da34b3) neither path exists -- both modules were moved to `crates/buzz-db/src/runtime/migration.rs` and `crates/buzz-db/src/runtime/replica_fence.rs` by commit a3730784f (`refactor(db): extract domain stores from database runtime`, PR #6987), which also created the `crates/buzz-db/src/store/` subtree and split the crate-root file into the current `runtime`/`store` layout described above. `lib.rs` still re-exports `migration` and `replica_fence` at the crate root, so the two paths named in the postgres container node no longer resolve, but the public names they document (`buzz_db::migration`, `buzz_db::replica_fence`) still do."
    entry_class: FACT
    evidence:
      - "git_log(path='crates/buzz-db/src/runtime/migration.rs') -> a3730784f refactor(db): extract domain stores from database runtime (#6987)"
      - "crates/buzz-db/src/runtime/migration.rs"
      - "crates/buzz-db/src/runtime/replica_fence.rs"
      - "crates/buzz-db/src/lib.rs"
  - statement: "docs/multi-tenant-conformance.md's conformance table states, for most rows (channel-less global events and DMs, channels and channel membership, users/profiles, workflows/runs/approvals), that the 'Required DB/index/RLS scope' obligation is a NOT NULL/indexed `community_id` on every tenant-scoped table and that direct lookups (event id, token hash, workflow id, channel id) must carry community context; a direct grep count across four representative buzz-db store modules shows 127 occurrences of `community_id` in store/event.rs, 109 in store/channel.rs, 204 in store/workflow.rs and 47 in store/user.rs, consistent with (but not a full audit proving) that scoping obligation being carried through in the store layer's own SQL and bind parameters, not only in the migration DDL."
    entry_class: FACT
    evidence:
      - "docs/multi-tenant-conformance.md"
      - "crates/buzz-db/src/store/event.rs"
      - "crates/buzz-db/src/store/channel.rs"
      - "crates/buzz-db/src/store/workflow.rs"
      - "crates/buzz-db/src/store/user.rs"
  - statement: "Neither docs/multi-tenant-conformance.md nor buzz-db's own crate-doc invariant list (in crates/buzz-db/src/lib.rs) carries a corpus node id on the corpus tree as loaded from origin/launchpad at this node's recorded revision -- confirmed by `git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus`, which lists no implementation/ subtree and no node whose id could plausibly resolve to either target -- so this node declares no `implements` edge toward either and names them by path instead, per AGENTS.md's rule that an edge to a nonexistent id is a hard validation error, not a soft placeholder."
    entry_class: FACT
    evidence:
      - "git_ls_tree(ref='origin/launchpad', path='launchpad/docs/corpus') -> no implementation/ subtree present at commit 76a0a4ebbe4bc4d852b0d04362ed768620da34b3"
  - statement: "architecture-containers-postgres.md's own 'Responsibility, technology, and ownership boundary' section states ownership of Postgres is split between buzz-db and buzz-relay, and names buzz-db as the crate that 'owns the schema-facing contract: connection pooling and lifecycle (Db::new, DbConfig), the embedded migration runner, and every typed data-access module' -- explicitly describing buzz-db as a constituent piece of the Postgres container this node documents one layer deeper, which is the basis for this node's `part-of` relationship toward it."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/containers/postgres.md"
  - statement: "A grep for `^\\s*#\\[(test|tokio::test)\\]` across every file in crates/buzz-db/src/store/ and crates/buzz-db/src/runtime/ counts 349 unit test functions; a grep for `#\\[ignore = \"requires Postgres\"\\]` across the same files counts 227 of them gated on a live database (plus a handful of differently worded #[ignore] attributes, e.g. `#[ignore = \"requires migrated Postgres\"]` in store/product_feedback.rs and bare `#[ignore]` in store/channel_members.rs), meaning roughly two-thirds of the crate's own test suite cannot run without Postgres."
    entry_class: FACT
    evidence:
      - "grep(pattern='^\\s*#\\[(test|tokio::test)\\]', path='crates/buzz-db/src/store/*.rs;crates/buzz-db/src/runtime/*.rs') -> 349 matches, commit 76a0a4ebbe4bc4d852b0d04362ed768620da34b3"
      - "grep(pattern='#\\[ignore = \"requires Postgres\"\\]', path='crates/buzz-db/src/store/*.rs;crates/buzz-db/src/runtime/*.rs') -> 227 matches, same commit"
      - "crates/buzz-db/src/store/event.rs"
      - "crates/buzz-db/src/store/deletion.rs"
  - statement: "Justfile's `test-unit` target runs `cargo nextest run -p buzz-db --lib`, and the target's own inline comment states this is deliberate: 'buzz-db migrator/lint tests: pure SQL-parsing unit tests (no infra)... The Postgres-backed buzz-db tests are #[ignore]d, so --lib runs only the infra-free set.'"
    entry_class: FACT
    evidence:
      - "Justfile"
  - statement: "scripts/run-tests.sh's `run_integration_tests` function (invoked by `just test`, i.e. `./scripts/run-tests.sh all`) runs buzz-db's Postgres-backed tests via `cargo test -p buzz-db -- --nocapture`, with no `--ignored` or `--include-ignored` flag; the preceding `run_unit_tests` function's own comment states explicitly that 'the Postgres-backed buzz-db tests are #[ignore]d; nothing here (or in integration mode below, which runs `cargo test -p buzz-db` without --ignored) runs them -- they need a separate isolated-DB gate' -- so as wired in this script, buzz-db's #[ignore]d test functions run in neither the unit nor the integration path."
    entry_class: FACT
    evidence:
      - "scripts/run-tests.sh"
  - statement: ".github/workflows/ci.yml's `backend-integration` job runs a curated, individually named subset of buzz-db's #[ignore]d Postgres-backed tests via `cargo nextest run --run-ignored ignored-only -E '<filter>'` steps: replaceable-store parameterized/concurrent_parameterized tests, two named observability pool-acquire/advisory-lock tests, relay_invite::tests, one named coordinate-delete test, eight named relay_operators::tests (roster-mutation audit trail and last-operator invariants), and three named moderation/relay_admin_actions escalation tests -- a hand-enumerated allowlist of specific test names per step, not a blanket `--ignored` run of the crate."
    entry_class: FACT
    evidence:
      - ".github/workflows/ci.yml"
  - statement: "Given the prior three evidence entries, the great majority of buzz-db's 227 #[ignore = \"requires Postgres\"] test functions -- everything outside the roughly 15-20 individually named in ci.yml's backend-integration job -- are not executed by any test-running command this repository defines (Justfile, scripts/run-tests.sh, or .github/workflows/ci.yml); whether developers run them ad hoc with a manual `--ignored` flag against a local Postgres during focused work on a given store module is plausible but not verifiable from the repository alone."
    entry_class: INFERENCE
    evidence:
      - "Justfile"
      - "scripts/run-tests.sh"
      - ".github/workflows/ci.yml"
    confidence: 0.75
  - statement: "Issue #926's Definition of Done requires that the node states implementation responsibility and what it deliberately does not own, names public interfaces/entry points and important dependencies, links owned source paths and representative tests, and avoids restating domain semantics already canonical in capability/layer/interface nodes."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#926 definition of done"
relationships:
  - type: part-of
    target: architecture-containers-postgres
---

# buzz-db: implementation reference

`crates/buzz-db` is the Rust crate realizing Buzz's Postgres persistence layer: connection
pool construction and lifecycle (`Db`, `DbConfig`), the embedded SQLx migration runner, the
replica-freshness fence and its routed-read machinery, and 27 domain-owned data-access
modules (events, channels, users, moderation, workflow, and more). This node documents that
implementation one layer deeper than `architecture-containers-postgres` does -- concrete
modules, functions, and tests -- and claims it realizes two things: the crate's own
self-declared design invariants (its `lib.rs` doc comment) and, for the store layer
specifically, the `community_id`-scoping obligation `docs/multi-tenant-conformance.md`'s
conformance table states for tenant-scoped tables and direct lookups.

## Target

Two targets, neither of which carries a corpus node id yet (see the evidence ledger entry
recording that check against `origin/launchpad`), so no `implements` edge is declared toward
either -- both are named here by path instead, per `AGENTS.md`'s rule against inventing an
edge to a nonexistent id:

- **buzz-db's own crate-doc invariants** -- `crates/buzz-db/src/lib.rs`, "Design invariants"
  section: AUTH events (kind 22242) are never stored, ephemeral events (20000-29999) are
  never stored, the `events` table is partitioned by month on `created_at`, no foreign key
  references a partitioned table, and query construction uses runtime `sqlx::query()` rather
  than compile-time `sqlx::query!()`. These are self-authoritative: the crate states them and
  the crate is also where they are enforced.
- **`docs/multi-tenant-conformance.md`'s "Required DB/index/RLS scope" column** -- open the
  file directly. This is a document-wide checklist spanning auth, search, Redis, media, and
  git hosting; buzz-db realizes only its DB/index/RLS-scope obligations for the rows that
  describe persisted, tenant-scoped state (events, channels, users, workflows, moderation,
  and related tables) -- not the document's rows about Redis keys, media authorization, or
  git object storage, which other crates own.

## Implementation surface

| Component / file / symbol | Realizes | Note |
|---|---|---|
| `crates/buzz-db/src/runtime/mod.rs` -- `Db::insert_event_with_serving_write_guard` | Crate-doc invariant: AUTH and ephemeral events are never stored | Checks `buzz_core::kind::KIND_AUTH` and `buzz_core::kind::is_ephemeral` before any SQL executes, returning `DbError::AuthEventRejected` / `DbError::EphemeralEventRejected` |
| `crates/buzz-db/src/runtime/migration.rs` -- `run_migrations`, `with_exclusive_schema_destruction_lock` | Crate-doc invariant: schema changes are safe against concurrent destructive operations | Holds Postgres advisory lock `SCHEMA_DESTRUCTION_LOCK_KEY` (defined in `store/deletion.rs`) for the entire migration run; a source lint enforces `MIGRATOR.run` has no other call site |
| `crates/buzz-db/src/runtime/replica_fence.rs` -- `ReplicaFence`, `verify_floor_guard_catalog`, `verify_floor_guard_behavior`, `run_probe` | Crate-doc invariant (partitioning) plus the routed-read soundness the fence depends on | Verifies the migration-0021 floor-guard trigger on the `events` parent and every partition before the background heartbeat probe is ever spawned |
| `crates/buzz-db/src/runtime/mod.rs` -- `RoutePredicate`, `RouteDecision`, `route_proof::ChannelScoped` | Routed-read correctness (not itself a crate-doc bullet, but the mechanism the partitioning/floor-guard invariants rely on for reads) | `ChannelScoped` is a typestate proof token mintable only by three named constructors tied to specific query shapes; `RoutePredicate::for_query` returns `Bounded` (never routes) unless `BUZZ_REPLICA_READ_MAX_AGE_MS` is set |
| `crates/buzz-db/src/store/event.rs` -- `EventQuery`, `query_events`, `count_events`, `insert_event_with_thread_metadata_tx` | `docs/multi-tenant-conformance.md`'s "channel-less global events and DMs" row | 127 occurrences of `community_id` in this file's SQL/binds (grep count, this node's evidence ledger) |
| `crates/buzz-db/src/store/channel.rs`, `channel_members.rs` | `docs/multi-tenant-conformance.md`'s "channels and channel membership" row | 109 `community_id` occurrences in `channel.rs` alone |
| `crates/buzz-db/src/store/community.rs` | `docs/multi-tenant-conformance.md`'s "row zero: request community binding" row, DB side | Owns the `communities(host, id, ...)` table access this node's target row requires |
| `crates/buzz-db/src/store/workflow.rs` | `docs/multi-tenant-conformance.md`'s "workflows, runs, approvals, webhooks, schedules" row | 204 `community_id` occurrences (grep count); largest store module by test count (32 test functions) |
| `crates/buzz-db/src/store/user.rs` | `docs/multi-tenant-conformance.md`'s "users, profiles, NIP-05" row | 47 `community_id` occurrences |
| `crates/buzz-db/src/store/deletion.rs` | Not a target-realization row -- owns `SCHEMA_DESTRUCTION_LOCK_KEY` and the serving-write-lease admission the migration lock and `insert_event_with_serving_write_guard` both depend on | Largest store module (4,922 lines, 29 test functions) |

## Divergences

**A citation in an already-merged corpus node no longer resolves.**
`architecture-containers-postgres.md` (recorded at revision a44cf52fc740ebebbdd671427480d14f0bce0115)
names implementation paths `crates/buzz-db/src/migration.rs` and
`crates/buzz-db/src/replica_fence.rs`. At this node's recorded revision, both files have been
moved to `crates/buzz-db/src/runtime/migration.rs` and `crates/buzz-db/src/runtime/replica_fence.rs`
by commit a3730784f (`refactor(db): extract domain stores from database runtime`, PR #6987),
which is also the commit that created the current `runtime`/`store` split and the 27-module
`store/` subtree this node documents. The crate's *public* names (`buzz_db::migration`,
`buzz_db::replica_fence`, still re-exported from `lib.rs`) are unaffected -- this is a
divergence in an internal file path a sibling corpus node cited, not in the crate's public
API or in either target's substance. This node does not correct `architecture-containers-postgres.md`
itself; that is a separate edit to that node, owned by whoever revisits it next.

**No divergence found between the crate-doc invariants and their enforcement.** The AUTH/
ephemeral storage exclusions, the partitioning invariant, and the no-FK-to-partitioned-table
rule were checked directly against `runtime/mod.rs`, `runtime/migration.rs`, and
`runtime/replica_fence.rs` (see *Implementation surface* above) and each has a concrete,
locatable enforcement point. This was not checked against every one of the 27 store modules
individually, only against the crate-root/runtime enforcement paths named above.

## Verification

**Two-thirds of the crate's own tests cannot run without a live Postgres, and most of that
two-thirds are not exercised by anything this repository automates.** 349 unit test
functions exist across `store/` and `runtime/`; 227 of them carry `#[ignore = "requires
Postgres"]` (or an equivalent ignore reason). `just test-unit`
(`cargo nextest run -p buzz-db --lib`) deliberately runs only the un-ignored, infra-free
~122 -- its own inline comment says so. `just test` (`scripts/run-tests.sh`'s
`run_integration_tests`) runs `cargo test -p buzz-db -- --nocapture` with no `--ignored`
flag, and that script's own comment states this path does not run the ignored set either.
`.github/workflows/ci.yml`'s `backend-integration` job does run a curated subset of the
ignored tests, but by individually enumerated test name (`nextest -E` filters with
`--run-ignored ignored-only`) covering roughly 15-20 specific tests (replaceable-store
concurrency, pool/advisory-lock observability, invite security, one coordinate-delete
regression, relay-operator roster-audit invariants, and moderation escalation) -- not a
blanket run of the crate's ignored tests. The remainder of the 227 -- including, by file
inspection, most of `event.rs`'s, `channel.rs`'s, and `community.rs`'s own DB-backed test
functions -- are not selected by any test-running command this repository defines. This node
does not know whether they are exercised manually; see the corresponding `INFERENCE` entry
in the evidence ledger.

## Relationships

- part-of: `architecture-containers-postgres` -- `architecture-containers-postgres.md`
  itself states buzz-db "owns the schema-facing contract" as one of two crates splitting
  ownership of the Postgres container; this node documents that ownership one layer deeper.
- implements: none declared -- both candidate targets (buzz-db's own crate-doc invariants,
  `docs/multi-tenant-conformance.md`) have no corpus node id yet; see *Target* above.
- references: none -- no test-strategy or verification corpus node exists yet to cite for
  the *Verification* section above.

## Scope and omissions

**This node covers** what `crates/buzz-db` is responsible for (connection pooling and
lifecycle, migrations, the replica-freshness fence and routed reads, and 27 domain-owned
data-access modules), its public entry points and important dependencies, representative
implementation and test files, its realization of its own crate-doc invariants and of
`docs/multi-tenant-conformance.md`'s DB/index/RLS-scope obligation for persisted tenant
state, a file-path divergence against an already-merged sibling corpus node, and an honest
account of how much of the crate's own test suite actually runs in this repository's defined
automation.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Postgres container responsibility, writer/reader pool sizing, `BUZZ_AUTO_MIGRATE` gating, and the security-relevant multi-tenant schema boundary | `architecture-containers-postgres` |
| Table-by-table schema contents | `migrations/0001_initial_schema.sql` and later migration files |
| The full `docs/multi-tenant-conformance.md` checklist (auth, search, Redis, media, git-hosting rows) | those subsystems' own crates and future corpus nodes |
| `buzz-relay`'s wiring of `Db::new`, the audit and search pools it opens directly, and partition-maintenance scheduling | `architecture-containers-postgres`, a future `buzz-relay` implementation-reference node |
| `buzz-admin` and `buzz-deletion`, the only other crates depending on `buzz-db` directly | future implementation-reference nodes for those crates |
| The replica fence's full correctness proof | `crates/buzz-db/src/runtime/replica_fence.rs`'s own doc comments |
| Whether buzz-db's `#[ignore]`d Postgres tests are run manually outside this repository's automation | unresolved; not verifiable from the repository alone |

**Expected but not verified when this node was written:**

- **Whether the 27 store modules beyond the four spot-checked for `community_id` occurrence
  counts (`event.rs`, `channel.rs`, `workflow.rs`, `user.rs`) uniformly carry the same
  scoping discipline.** The occurrence-count check is a proxy, not a full audit; a module
  that stores tenant data without a `community_id` predicate would not be caught by this
  node's evidence.
- **Whether the specific test names CI's `backend-integration` job enumerates are still the
  full set of ignored tests anyone runs against real Postgres**, or whether other CI jobs
  not read for this node also select buzz-db tests by name.
