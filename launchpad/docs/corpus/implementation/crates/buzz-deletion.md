---
id: implementation-crates-buzz-deletion
type: implementation
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - operator
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 76a0a4ebbe4bc4d852b0d04362ed768620da34b3."
    entry_class: FACT
    evidence:
      - "commit 76a0a4ebbe4bc4d852b0d04362ed768620da34b3"
  - statement: "crates/buzz-deletion/Cargo.toml describes the crate as a \"Durable whole-community deletion engine for Buzz\", and its src/lib.rs crate doc comment reads \"Shared durable whole-community deletion engine and store adapters.\""
    entry_class: FACT
    evidence:
      - "crates/buzz-deletion/Cargo.toml"
      - "crates/buzz-deletion/src/lib.rs:1-3"
  - statement: "crates/buzz-deletion/src/lib.rs opens with #![deny(unsafe_code)] and #![warn(missing_docs)]."
    entry_class: FACT
    evidence:
      - "crates/buzz-deletion/src/lib.rs:1-2"
  - statement: "buzz-deletion depends on buzz-core, buzz-db and buzz-media directly (per its Cargo.toml [dependencies]), and its public run() function is the CLI-only entry point that dispatches a buzz_deletion::Command."
    entry_class: FACT
    evidence:
      - "crates/buzz-deletion/Cargo.toml"
      - "crates/buzz-deletion/src/lib.rs:372-434"
  - statement: "buzz_deletion::Command is a clap Subcommand enum with nine variants -- Submit, List, Inspect, Approve, Abort, Unblock, Run, Drain, Sweep -- each documented as a distinct step of the deletion lifecycle (e.g. Submit \"Persist a deletion request and freeze its initial cross-store inventory\", Sweep \"Sweep the whole bucket's key taxonomy and record observational evidence... independent of community deletion\")."
    entry_class: FACT
    evidence:
      - "crates/buzz-deletion/src/lib.rs:222-301"
  - statement: "buzz_deletion::store(db) returns db.deletion_store(), the shared DeletionStore handle used by both relay and operator/CLI paths."
    entry_class: FACT
    evidence:
      - "crates/buzz-deletion/src/lib.rs:52-55"
  - statement: "buzz_deletion::acquire_serving_write(db, community, operation) returns a ServingWriteGuard: a durable, heartbeated per-effect lease that a caller must verify() or protect() an external side effect with before an irreversible call, and finish() to release; the guard's own comment states this per-effect lease is \"the only durable proof that deletion can drain S3/Redis/push work across replicas.\""
    entry_class: FACT
    evidence:
      - "crates/buzz-deletion/src/lib.rs:57-157"
      - "crates/buzz-deletion/src/lib.rs:159-171"
  - statement: "Three crates in the workspace depend on buzz-deletion: buzz-admin, buzz-relay and buzz-workflow (grep of buzz-deletion across every crate's Cargo.toml, excluding buzz-deletion's own manifest)."
    entry_class: FACT
    evidence:
      - "crates/buzz-admin/Cargo.toml"
      - "crates/buzz-relay/Cargo.toml"
      - "crates/buzz-workflow/Cargo.toml"
  - statement: "crates/buzz-admin/src/deletions.rs is a thin adapter: it re-exports buzz_deletion::Command as DeletionsCommand and its run() delegates directly to buzz_deletion::run(command); a unit test in that same file asserts the crate's own continuous-worker Run/Drain-adjacent \"worker\" subcommand is deliberately not exposed through the buzz-admin CLI surface."
    entry_class: FACT
    evidence:
      - "crates/buzz-admin/src/deletions.rs"
  - statement: "buzz-relay calls buzz_deletion::acquire_serving_write around irreversible external side effects in five call sites: tunnel/directory.rs (session directory registration), api/git/transport.rs (git smart HTTP), api/media.rs (media upload, and checks ServingWriteGuard::acquisition_is_fenced / is_lease_lost on the resulting errors), handlers/side_effects.rs, and push_runtime.rs (push delivery)."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/tunnel/directory.rs:216-218"
      - "crates/buzz-relay/src/api/git/transport.rs:1855"
      - "crates/buzz-relay/src/api/media.rs:288"
      - "crates/buzz-relay/src/api/media.rs:328"
      - "crates/buzz-relay/src/api/media.rs:428"
      - "crates/buzz-relay/src/handlers/side_effects.rs:2741"
      - "crates/buzz-relay/src/push_runtime.rs:470"
  - statement: "buzz-relay calls buzz_deletion::store(&state.db) in handlers/event.rs to check is_serving_active(community) before accepting an ephemeral event, rejecting the write with \"restricted: community writes are fenced\" when the community is not serving-active; ingest.rs and command_executor.rs also call buzz_deletion::store() for the same shared DeletionStore handle."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs:708-721"
      - "crates/buzz-relay/src/handlers/ingest.rs:2177"
      - "crates/buzz-relay/src/handlers/ingest.rs:3532"
      - "crates/buzz-relay/src/handlers/command_executor.rs:115"
  - statement: "buzz-relay's main.rs records four buzz_deletion_serving_leases_* metrics (reaped counter, active/expired/dead_tuples gauges) from the deletion serving-write lease table."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:1072-1082"
  - statement: "buzz-workflow's executor.rs calls buzz_deletion::acquire_serving_write(&engine.db, community_id, \"workflow_action\") before running a workflow action's external side effect."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/executor.rs:552"
  - statement: "buzz-deletion does not itself define the DeletionStage/DeletionStore/DeletionRequest/LeaseToken/FrozenInventory/StorageManifest types it imports and orchestrates; those are defined in buzz-db's crates/buzz-db/src/store/deletion.rs (a 4922-line module, declared via `pub mod deletion;` in crates/buzz-db/src/store/mod.rs), which is where the eleven-variant DeletionStage enum (Submitted, Inventoried, Approved, Fenced, Drained, BindingsRemoved, PostgresPurged, CachePurged, LogicallyVerified, RetentionPending, Aborted) and its next()/runnable() transition rules live."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/deletion.rs:123-180"
      - "crates/buzz-db/src/store/mod.rs:18"
  - statement: "buzz-deletion's execute_stage function drives one full pass of the DeletionStage state machine per claimed request: Approved runs an S3 version-listing preflight and a structural-catalog revalidation before durably fencing the community; Fenced disconnects live connections, waits for drained serving writes, and freezes the destructive storage manifest; Drained bulk-deletes the frozen object-storage keys in resumable chunks; BindingsRemoved purges tenant-scoped PostgreSQL rows; PostgresPurged purges the Redis/community-cache namespace; CachePurged proves cross-store logical absence (Postgres, S3 listing, two-pass Redis SCAN); LogicallyVerified marks the request RetentionPending, explicitly noting \"member-erasure and fleet-wide shared-CAS GC are out of V1 scope\"."
    entry_class: FACT
    evidence:
      - "crates/buzz-deletion/src/lib.rs:1186-1416"
  - statement: "Migrations 0029_community_deletion.sql (575 lines) and 0030_community_deletion_recovery.sql (48 lines) create the schema buzz-deletion orchestrates: community_deletion_requests, community_deletion_approvals and community_deletion_checkpoints tables, plus terminal-recovery ALTER TABLE changes; 0029's header states the community row is \"never removed\" and becomes \"the permanent name tombstone\", and that every community-scoped table receives \"the same database-enforced write fence\" in one atomic migration."
    entry_class: FACT
    evidence:
      - "migrations/0029_community_deletion.sql:1-19"
      - "migrations/0029_community_deletion.sql:68"
      - "migrations/0029_community_deletion.sql:135"
      - "migrations/0030_community_deletion_recovery.sql:1-7"
  - statement: "buzz-deletion's own test module contains both plain unit tests that run unconditionally (e.g. submit_host_prefers_explicit_host, deletion_s3_key_pair_from variants, permanent_failures_are_typed_not_string_classified, redis_absence_requires_terminal_cursor_and_all_pages_empty) and #[tokio::test] integration tests marked #[ignore = \"requires Postgres\"] or #[ignore = \"requires Postgres and S3-compatible storage\"] that exercise real stage transitions, chunk-resume-after-crash behavior, and serving-write-guard heartbeat/lease-loss semantics against a live database and object store."
    entry_class: FACT
    evidence:
      - "crates/buzz-deletion/src/lib.rs:1601-2392"
  - statement: "A repository-wide grep of ARCHITECTURE.md and the top-level AGENTS.md finds zero mentions of buzz-deletion by name; both documents' crate lists and dependency diagrams predate this crate."
    entry_class: FACT
    evidence:
      - "ARCHITECTURE.md"
      - "AGENTS.md"
  - statement: "architecture-containers-postgres already states, as its own FACT, that buzz-relay is the sole crate constructing buzz_db::DbConfig/Db::new at startup and that buzz-admin and buzz-deletion are the only other crates depending on buzz-db directly, and lists buzz-deletion in its inbound-interfaces table as connecting \"via buzz-db::Db\" for \"Whole-community deletion lifecycle\"."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/containers/postgres.md:23-28"
      - "launchpad/docs/corpus/architecture/containers/postgres.md:118"
      - "launchpad/docs/corpus/architecture/containers/postgres.md:135"
  - statement: "architecture-principles-subsystem-isolation already lists buzz-deletion among the post-diagram crates (alongside buzz-conformance, buzz-relay-mesh, buzz-datastore-tracing, buzz-voice, buzz-push-gateway, buzz-backend-kubernetes) that do not appear in ARCHITECTURE.md's stated subsystem-isolation principle or its crate dependency diagram at all, and explicitly leaves open whether the corpus's architecture documentation should be updated to include them."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/principles/subsystem-isolation.md:145"
      - "launchpad/docs/corpus/architecture/principles/subsystem-isolation.md:209"
  - statement: "No node under launchpad/docs/corpus/ and no file under launchpad/decisions/ documents a community-deletion specification or ADR with a corpus node id; git ls-tree of origin/launchpad's corpus tree and a listing of launchpad/decisions/ both confirm this, and the only community-deletion-adjacent work found is unmerged remote branches (e.g. am/community-deletion-safety-79536ff, fry/community-deletion-v1), none of which are corpus nodes."
    entry_class: FACT
    evidence:
      - "git_ls_tree(ref='HEAD', path='launchpad/docs/corpus') -> no implementation/ or deletion-related node other than this one"
      - "grep(pattern='delet', path='launchpad/decisions/*.md', case_insensitive=true) -> no matching filenames"
---

# buzz-deletion: implementation reference

`crates/buzz-deletion` is the shared, durable, whole-community deletion engine
for Buzz. It realizes the CLI-only lifecycle described by its own crate doc
comment ("Shared durable whole-community deletion engine and store adapters")
and by migrations `0029_community_deletion.sql`/`0030_community_deletion_recovery.sql`:
submit a deletion request, freeze a cross-store inventory, require explicit
operator approval of that frozen digest, durably fence the community against
new serving writes, drain in-flight writes, destructively remove tenant-owned
object-storage keys and PostgreSQL rows, purge the Redis namespace, and
cross-verify logical absence -- while also exposing the serving-path primitive
(`acquire_serving_write`/`ServingWriteGuard`) that lets `buzz-relay` and
`buzz-workflow` prove an external side effect completed (or was safely
cancelled) under that same fence.

## Target

There is no corpus-id'd specification, NIP, or accepted ADR this crate
`implements` today. The closest artifacts are:

- The crate's own doc comment and public API (`crates/buzz-deletion/src/lib.rs`),
  which is the executable statement of the lifecycle.
- `migrations/0029_community_deletion.sql` and
  `migrations/0030_community_deletion_recovery.sql`, whose header comments are
  the closest thing to a design rationale in this repository (e.g. "The
  community row is never removed: it becomes the permanent name tombstone",
  and the note that the migration "intentionally remains one atomic catalog
  change so a failed deployment cannot expose only a subset of the universal
  fences").
- `buzz-db`'s `crates/buzz-db/src/store/deletion.rs`, which owns the persisted
  `DeletionStage`/`DeletionStore`/`DeletionRequest` types this crate
  orchestrates but does not define.

No ADR under `launchpad/decisions/` and no other corpus node documents a
community-deletion specification with an id this node could point `implements`
at. Several unmerged remote branches suggest active work in this area (for
example `am/community-deletion-safety-79536ff`, `fry/community-deletion-v1`,
`cid/community-deletion-fence-fixes-v2`), but none of them are corpus nodes,
and this node makes no claim about their content.

## Implementation surface

| Component / file / symbol | Realizes | Note |
|---|---|---|
| `buzz_deletion::run(Command)` | The CLI-only entry point for every deletion lifecycle command | `buzz-admin`'s `deletions.rs` delegates to this directly |
| `buzz_deletion::Command` (`Submit`, `List`, `Inspect`, `Approve`, `Abort`, `Unblock`, `Run`, `Drain`, `Sweep`) | The nine operator-facing lifecycle actions | `Sweep` is explicitly documented as independent of community deletion itself -- an observational bucket-taxonomy check |
| `buzz_deletion::store(&Db)` | Returns the shared `DeletionStore` handle | Called from both this crate's CLI path and `buzz-relay`'s serving-write-gate checks (`event.rs`, `ingest.rs`, `command_executor.rs`) |
| `buzz_deletion::acquire_serving_write` / `ServingWriteGuard` | A durable, heartbeated per-effect lease callers must hold across an irreversible external side effect | Called from `buzz-relay` (git transport, media upload, session directory, generic side effects, push delivery) and `buzz-workflow` (workflow action execution) |
| `execute_stage` (private) | One pass of the `DeletionStage` state machine per claimed request -- preflight, fence, drain, bulk-delete, Postgres purge, Redis purge, logical verification | Not exported; reached only through `run`/`run_loop` |
| `run_loop` / `execute_claim` (private) | Claim-and-run or claim-and-drain execution loop with lease heartbeating and graceful shutdown | Backs the `Run`/`Drain` commands |
| `verify_storage_absence`, `verify_redis_absence` (private) | The `CachePurged` stage's logical-absence proof: O(1) per-prefix S3 listing plus two-pass Redis `SCAN` | Two full empty `SCAN` passes are required because `SCAN` is only weakly consistent |

## Divergences

Checked: `ARCHITECTURE.md` and the top-level `AGENTS.md` crate list -- neither
mentions `buzz-deletion` at all, so there is no documented architectural
description for this node to diverge from or agree with in that source. This
is the same gap `architecture-principles-subsystem-isolation` already records
for a cluster of other post-diagram crates (`buzz-conformance`,
`buzz-relay-mesh`, `buzz-datastore-tracing`, `buzz-voice`,
`buzz-push-gateway`, `buzz-backend-kubernetes`), and this node adds
`buzz-deletion` to that already-open finding rather than re-litigating it.
No other divergence was found between the crate's stated purpose (its own doc
comment and `Cargo.toml` description) and its actual code: the CLI surface,
the state-machine stage order, and the serving-write-guard pattern used by
callers all match what the crate documents about itself.

## Verification

Two tiers exist in `crates/buzz-deletion/src/lib.rs`'s own `tests` module:
plain unit tests that always run in CI (host resolution, S3 credential
trimming, typed permanent-vs-transient error classification, Redis-absence
cursor logic), and `#[tokio::test]` integration tests marked
`#[ignore = "requires Postgres"]` or
`#[ignore = "requires Postgres and S3-compatible storage"]` that exercise real
stage transitions end-to-end: post-inventory row churn before fencing, frozen
inventory digest/ownership tamper detection, chunk-resume after a simulated
crash mid-delete, late-target-binding rejection during logical verification,
stale-lease-during-failure-recording, and serving-write-guard heartbeat loss
under quiescing. There is no CI job name distinct from the workspace's
standard `cargo test`/`clippy` gates found for this crate specifically; the
ignored tests require an operator or CI job to opt in with a live Postgres
(and, for some, S3-compatible storage) target.

## Relationships

- references: architecture-containers-postgres
- references: architecture-principles-subsystem-isolation

No `implements` edge is declared -- per *Target* above, no spec/decision this
crate realizes has a corpus node id yet. No `part-of` edge is declared -- this
crate is not documented anywhere as a sub-component of a larger
implementation-reference node, and none exists in the corpus yet for it to sit
under. No `depends-on` edge is declared toward `architecture-containers-postgres`
or `architecture-principles-subsystem-isolation`: `references`'s directionality
("source cites target as supporting context; no ownership or currency
dependency implied") fits better here, since this node's own claims do not
require those nodes' claims to remain true -- it merely points a reader at
where the wider architecture already discusses this crate.

## Scope and omissions

**This node covers** what `crates/buzz-deletion` is responsible for as a
crate: its public CLI/library surface (`run`, `Command`, `store`,
`acquire_serving_write`/`ServingWriteGuard`), which other crates depend on it
and through which real call sites, the `DeletionStage` pipeline it drives, and
how its own test suite verifies that pipeline.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The persisted `DeletionStage`/`DeletionStore`/`DeletionRequest`/`LeaseToken`/`StorageManifest` types and their SQL-backed persistence logic | `crates/buzz-db/src/store/deletion.rs` -- a separate, larger module this crate depends on but does not define |
| S3/media bulk-delete and prefix-listing mechanics (`delete_object_versions`, `list_prefix_versions_page`, `sweep_bucket_taxonomy`) | `crates/buzz-media` |
| The `community_deletion_requests`/`community_deletion_approvals`/`community_deletion_checkpoints` table schemas themselves | `migrations/0029_community_deletion.sql`, `migrations/0030_community_deletion_recovery.sql` |
| The operator-facing `buzz-admin deletions` CLI argument surface and its own thin-adapter test (worker subcommand intentionally not exposed) | `crates/buzz-admin/src/deletions.rs` |
| Whether `buzz-deletion` should be added to `ARCHITECTURE.md`'s crate list or dependency diagram | unresolved; the same open question `architecture-principles-subsystem-isolation` already records for a cluster of other post-diagram crates |
| Any content of the unmerged `am/community-deletion-safety-*`, `fry/community-deletion-v1`, or `cid/community-deletion-fence-fixes-v2` branches | out of scope -- none are merged, and this node makes no claim about branch content |

**Expected but not verified when this node was written:**

- **No CI workflow file was inspected to confirm whether or how the
  `#[ignore]`-marked Postgres/S3 integration tests are actually run in this
  repository's pipelines** (as opposed to locally by a developer or operator
  opting in). The tests exist and are readable; their CI execution path was
  not traced.
- **The exact operator workflow for approving a deletion request** (who is
  authorized to call `Approve`, what tooling surfaces the frozen inventory
  digest for a human to review before approving) was not traced beyond the
  CLI command's own doc comment.
