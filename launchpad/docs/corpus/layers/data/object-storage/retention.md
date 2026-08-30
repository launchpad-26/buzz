---
id: layers-data-object-storage-retention
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
  - statement: "node.schema.json's type field is a closed 13-member enum (architecture, layers, capabilities, platforms, implementation, interfaces-events, verification, operations, development, release, governance, agent, ingestion), and layers is a real member of it."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "Issue #1072 assigns this document the path launchpad/docs/corpus/layers/data/object-storage/retention.md directly, via its own corpus-plan:v2 alias header comment and its Objective sentence."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1072, read directly via gh issue view"
  - statement: "Parent Feature #610 is titled 'data and storage layer corpus exists' and this task's issue is one of its 42 child issues; PRD #602's success criteria enumerate layers as its own distinct surface in the type taxonomy, separate from architecture."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#610 and launchpad-26/buzz#602, read directly via gh issue view"
  - statement: "This node uses type: layers rather than templates/datastore.md's own suggested value for a real datastore instance (type: architecture, an INFERENCE at confidence 0.6 in that template's own ledger), for consistency with the two sibling object-storage documents in the same batch (#1067 blossom-storage, #1069 git-objects), both of which independently made and disclosed the identical choice. Per standards/taxonomy.md's step-4 rule (disclose an imperfect fit rather than silently pick), this tension is named here rather than re-argued."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
      - "launchpad/docs/corpus/templates/datastore.md"
      - "launchpad/docs/corpus/standards/taxonomy.md"
    confidence: 0.65
  - statement: "At this node's authoring revision, origin/launchpad's launchpad/docs/corpus tree contains no layers/ directory at all; the sibling object-storage documents named in this task's batch (blossom-storage.md, id layers-data-object-storage-blossom-storage; git-objects.md, id layers-data-object-storage-git-objects) exist only on unmerged sibling task branches, confirmed not ancestors of origin/launchpad by git merge-base --is-ancestor. Their ids are therefore not legal relationships[].target values for this node per AGENTS.md step 9, which requires a target to resolve against git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus."
    entry_class: FACT
    evidence:
      - "git_ls_tree(origin/launchpad, launchpad/docs/corpus) -> no layers/ entry, at commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
      - "git_merge_base_is_ancestor(f0e7e7335..., origin/launchpad) -> false"
      - "git_merge_base_is_ancestor(258b99dbf..., origin/launchpad) -> false"
  - statement: "architecture-containers-object-storage (launchpad/docs/corpus/architecture/containers/object-storage.md) is a merged node at this revision and states the shared S3-compatible bucket's existence, its shared use by Blossom media and git, and a one-line summary of each; that node is the container-level document this retention node zooms into."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/containers/object-storage.md"
  - statement: "crates/buzz-media/src/bucket_index.rs's tenant_prefixes function has a doc comment stating verbatim: 'shared immutable CAS/thumb/probe data is deliberately outside them (fleet-wide physical GC is a separate retention phase)' -- and its own body returns exactly three community-scoped prefixes: _meta/{community}/, _uploads/{community}/, repos/{community}/."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/src/bucket_index.rs"
  - statement: "crates/buzz-media/src/bucket_index.rs's is_tenant_owned_key function returns false unconditionally for KeyClass::Blob and KeyClass::Thumb, and only returns true for a Sidecar or Auxiliary key whose embedded community matches, or an Unknown-classified key whose git_pointer_community resolves to that community -- shared, content-addressed blob and thumbnail bytes are structurally excluded from what any whole-community deletion request can ever target."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/src/bucket_index.rs"
  - statement: "crates/buzz-db/src/deletion.rs's DeletionStage enum is a fixed, ordered lifecycle (Submitted, Inventoried, Approved, Fenced, Drained, BindingsRemoved, PostgresPurged, CachePurged, LogicallyVerified, RetentionPending, Aborted) whose own doc comment on Self::next states 'There are no backwards or skipping transitions'; RetentionPending's own variant doc comment reads 'Logical deletion complete; shared CAS physical expiry is deferred,' and DeletionStage::next returns None for both RetentionPending and Aborted -- no further transition out of RetentionPending exists anywhere in this codebase."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/deletion.rs"
  - statement: "crates/buzz-deletion/src/lib.rs's execute_stage match arm for DeletionStage::LogicallyVerified calls DeletionStore::mark_retention_pending with the literal recorded detail policy string 'member-erasure and fleet-wide shared-CAS GC are out of V1 scope' -- a deliberate, named non-implementation recorded in the request's own audit trail, not silence."
    entry_class: FACT
    evidence:
      - "crates/buzz-deletion/src/lib.rs"
  - statement: "crates/buzz-db/src/deletion.rs's mark_retention_pending method has a doc comment 'Finish logical deletion and enter the physical-expiry pending state,' and its SQL UPDATE sets completed_at = now() when transitioning a request's stage to 'retention_pending' -- from the deletion pipeline's own perspective the request is complete at this point, even though the shared CAS bytes it could not touch remain physically present with no scheduled removal."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/deletion.rs"
  - statement: "docs/git-on-object-storage.md (root design doc, not a corpus node) states, independently of buzz-deletion, that 'because no writer removes packs. Physical pruning of unreachable packs is a backend retention concern outside this proof boundary; any such sweep must honor in-flight readers (e.g. a retention window longer than the max hydrate ...)' and separately that 'object-store deletion remains a separate retention concern outside this proof boundary' -- the identical no-scheduled-physical-deletion posture as buzz-deletion's RetentionPending stage, stated for the git-CAS half of the same bucket."
    entry_class: FACT
    evidence:
      - "docs/git-on-object-storage.md"
  - statement: "crates/buzz-media/src/bucket_index.rs's sweep_bucket_taxonomy function has a doc comment stating deletion stages 'gate on a recent clean sweep instead of re-listing the whole bucket per request' -- it folds a paginated bucket listing into a TaxonomySweepOutcome counting keys outside the known writer taxonomy (is_known_fleet_key, which recognizes blob/thumb/sidecar/auxiliary shapes, any community's git pointer, shared git CAS keys under packs/, idx/, manifests/, and probe/ keys), bounded by an explicit object cap that fails closed (SweepError::CapExceeded) rather than truncating silently."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/src/bucket_index.rs"
  - statement: "crates/buzz-deletion/src/lib.rs's Command enum has a Sweep variant whose own doc comment states 'This is independent of community deletion. It reports unknown writer shapes but never gates submission or destructive progress'; crates/buzz-admin/src/deletions.rs's deletions command calls buzz_deletion::run(command), so this sweep is an operator-invoked buzz-admin subcommand, not an automatically scheduled background task, and its own execution records a row via DeletionStore::record_taxonomy_sweep into the storage_taxonomy_sweeps table (created by migrations/0029_community_deletion.sql) before exiting nonzero only if unknown_object_count > 0."
    entry_class: FACT
    evidence:
      - "crates/buzz-deletion/src/lib.rs"
      - "crates/buzz-admin/src/deletions.rs"
      - "migrations/0029_community_deletion.sql"
  - statement: "crates/buzz-relay/src/storage_sweep.rs's own module doc comment describes an hourly, single-flight, cache-only usage-metrics background task (referencing PLANS/S3_STORAGE_METRICS_PLAN.md Rev 3) that re-publishes a cached snapshot every tick and is disableable via BUZZ_STORAGE_METRICS=off; it calls only MediaStorage::list_page for read-only enumeration and has no deletion or expiry side effect -- a different mechanism, crate, trigger, and purpose from buzz-deletion's operator-invoked Sweep command, despite the shared word 'sweep'."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/storage_sweep.rs"
  - statement: "crates/buzz-deletion/src/lib.rs's enumerate_tenant_prefixes function calls MediaStorage::bucket_versioning_detected before listing any tenant prefix and returns a permanent error ('bucket versioning detected; deletion cannot prove logical absence with delete markers') if the bucket has ever had versioning enabled -- this preflight gate applies to the BindingsRemoved/Drained deletion path, the only path in this codebase that ever issues a destructive S3 delete."
    entry_class: FACT
    evidence:
      - "crates/buzz-deletion/src/lib.rs"
  - statement: "Issue #1072's Definition of Done requires this document to state whether the store is authoritative, derived, cache or transport; describe owned data, key access patterns, lifecycle/retention and consistency semantics; name tenancy/security boundaries and failure behavior; and link schema/migrations/code/tests rather than copying DDL."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1072 definition of done"
relationships:
  - type: part-of
    target: architecture-containers-object-storage
---

# Object-storage retention

## Purpose & scope statement

This node documents the **retention and lifecycle policy of the shared
S3-compatible object-storage bucket** — the single question of *what is kept
forever, what is ever deleted, and by what mechanism* — across both halves of
the bucket that [`architecture-containers-object-storage`](../../../architecture/containers/object-storage.md)
(id `architecture-containers-object-storage`) already inventories as one
container: Blossom media blobs and git packs/manifests. It is a cross-cutting
concern, not a restatement of either half's own internal shape.

**What this document is not.** It does not restate the Blossom key-namespace
inventory, the git manifest/pack schema, or either datastore's own full
access-pattern summary — those belong to the sibling datastore-level nodes
this document is `part-of` the same container as (`blossom-storage.md`,
`git-objects.md`), neither of which is merged to `origin/launchpad` at this
node's authoring revision (see *Scope and omissions*). It does not repeat the
formal correctness proofs of `docs/git-on-object-storage.md` (durability
ordering, manifest reconstruction) — only that document's own retention
axiom is cited here. It is not the whole-community deletion pipeline's full
state machine — only the portion of it that determines what happens to
*stored bytes*.

**Authoritative, not derived, not a cache, not a transport — for the
question this document asks.** The object-storage bucket is the sole durable
location of the bytes retention policy governs; nothing else in this
repository holds a second copy that a retention decision here could instead
apply to. Retention state itself (which deletion request has reached which
stage) is authoritative in Postgres (`community_deletion_requests`,
`crates/buzz-db/src/deletion.rs`), not in the object store — the object store
holds the bytes; Postgres holds the record of what has and has not been done
to them.

## Technology & attachment profile

Shared with both sibling datastore nodes: an S3-compatible endpoint reached
through `rust-s3`, configured via `BUZZ_S3_ENDPOINT`, `BUZZ_S3_ACCESS_KEY`,
`BUZZ_S3_SECRET_KEY`, `BUZZ_S3_BUCKET` (default `buzz-media`),
`BUZZ_S3_REGION`, `BUZZ_S3_ADDRESSING_STYLE`. This document does not restate
the credential-resolution chain or per-environment values — see the
container node's own *Technology* section.

## Schema / namespace inventory (retention-relevant subset only)

A structural split of the bucket's key shapes along the one axis this
document is about: whether whole-community deletion can ever target the key.
Full per-class structural purpose belongs to the sibling datastore nodes; this
table exists only to ground the retention claims below in real key shapes.

| Key shape | Deletable by whole-community deletion? | Why |
|---|---|---|
| `_meta/{community-uuid}/{sha256}.json` (media sidecar) | Yes | Tenant-owned binding; `is_tenant_owned_key` matches `Sidecar` whose embedded community equals the target. |
| `_uploads/{community-uuid}/{sha256}/{ulid}.json` (upload record) | Yes | Tenant-owned binding; `is_tenant_owned_key` matches `Auxiliary` the same way. |
| `repos/{community-uuid}/{owner}/{repo}/pointer` (git ref pointer) | Yes | Tenant-owned binding; `is_tenant_owned_key`'s `Unknown` branch resolves it via `git_pointer_community`. |
| `{sha256}.{ext}` (media blob) | **No, structurally never** | `is_tenant_owned_key` returns `false` unconditionally for `KeyClass::Blob` — shared, content-addressed, no community owns it. |
| `{sha256}.thumb.jpg` (thumbnail) | **No, structurally never** | Same function returns `false` for `KeyClass::Thumb`. |
| `packs/<hex sha256>`, `manifests/<hex sha256>`, `idx/<pack_digest>` (git CAS) | **No, structurally never** | Not matched by any `is_tenant_owned_key` branch; `tenant_prefixes` deliberately excludes them, per that function's own doc comment naming "fleet-wide physical GC" as "a separate retention phase." |

## Access-pattern summary

| Path | Component | Retention effect |
|---|---|---|
| Whole-community deletion | `crates/buzz-deletion/src/lib.rs`, invoked as a `buzz-admin` subcommand (`crates/buzz-admin/src/deletions.rs`) | Deletes only the tenant-owned bindings above, after a write-drain fence; never touches shared CAS bytes. Gated by `MediaStorage::bucket_versioning_detected` before any delete is issued. |
| Fleet taxonomy sweep | `crates/buzz-media/src/bucket_index.rs::sweep_bucket_taxonomy`, invoked via `buzz-deletion`'s `Command::Sweep` (also `buzz-admin`) | **Read-only.** Records observational evidence (`storage_taxonomy_sweeps` table) of any key shape outside the known writer taxonomy; deletion stages consult a recent clean sweep instead of re-listing the bucket, but the sweep itself deletes nothing and never gates or blocks anything by its own doc comment. |
| Hourly usage-metrics sweep | `crates/buzz-relay/src/storage_sweep.rs` | **Read-only**, `MediaStorage::list_page` only, disableable via `BUZZ_STORAGE_METRICS=off`. A different mechanism, crate, and trigger from the fleet taxonomy sweep above — the shared word "sweep" names two unrelated, both non-destructive, tasks. |
| Upload / clone / push | `crates/buzz-media/src/upload.rs`, `crates/buzz-relay/src/api/git/*` | Writes only; own no retention behavior — covered by the sibling datastore nodes. |

## Operational characteristics

- **No per-object TTL or scheduled expiry exists anywhere in this codebase**,
  for either the media half or the git-CAS half. Every write is durable
  until an explicit, tenant-scoped deletion request removes the binding that
  points at it.
- **Whole-community deletion terminates in a named, deliberate non-implementation of physical cleanup, not in silence.**
  `DeletionStage`'s fixed, backwards-and-skip-free lifecycle
  (`Submitted → … → LogicallyVerified → RetentionPending`) ends at
  `RetentionPending`, whose own variant doc comment states "Logical deletion
  complete; shared CAS physical expiry is deferred," and `DeletionStage::next`
  returns `None` for it — there is no further transition in this codebase.
  The transition into it (`mark_retention_pending`) records the literal
  policy string `"member-erasure and fleet-wide shared-CAS GC are out of V1
  scope"` in the request's own audit detail, and marks the request
  `completed_at` at that point — from the deletion pipeline's own point of
  view, a community's deletion is "done" once its bindings, Postgres rows,
  and cache namespace are gone and logically verified absent, even though
  the shared CAS bytes it could never touch remain in the bucket with no
  scheduled removal.
- **The git-CAS half states the identical posture independently.**
  `docs/git-on-object-storage.md` states physical pruning of unreachable
  packs is "a backend retention concern outside this proof boundary" and
  that "object-store deletion remains a separate retention concern outside
  this proof boundary" — arrived at from the git design's own durability
  proof, not from `buzz-deletion`'s policy string, and agreeing with it.
- **The one mechanism that inspects retention risk does not act on it.**
  `sweep_bucket_taxonomy` (invoked as `buzz-deletion`'s `Sweep` operator
  command) records whether the bucket contains any key shape outside the
  known writer taxonomy — the safety precondition a future physical-GC pass
  would need — but is explicitly non-destructive: its own `Command::Sweep`
  doc comment states it "never gates submission or destructive progress." No
  code path in this repository consumes that recorded evidence to perform an
  actual deletion.
- **Consistency of the one thing that is deleted.** Tenant-owned bindings are
  deleted only behind a write-drain fence (new writes for the community are
  closed and confirmed drained before enumeration begins), enumerated into a
  durable, resumable chunk manifest, and bulk-deleted idempotently (a missing
  key reports as already deleted) — the deletion this codebase performs is
  whole-community and manifest-driven, never per-object or time-based.

## Tenancy / security boundaries and failure behavior

**Tenancy.** Retention/deletion eligibility is community-scoped only for the
three binding key shapes in the table above — `is_tenant_owned_key` checks
the community embedded in the key itself. Shared CAS bytes (blob, thumb,
pack, manifest, idx) carry **no tenant boundary at all**, by design: they are
content-addressed and may in principle be referenced by more than one
community's bindings, which is precisely why no per-community deletion path
is permitted to remove them — removing a key one community's binding points
at could silently break another community's still-live reference to the same
bytes.

**Security / correctness gate.** Before any destructive delete is issued,
`enumerate_tenant_prefixes` calls `MediaStorage::bucket_versioning_detected`
and permanently fails the whole deletion request if the bucket has ever had
versioning enabled — a versioned bucket's `DeleteObjects` only inserts
delete markers, which cannot prove logical absence, so the whole-community
deletion pipeline refuses to proceed under a threat model it cannot verify
against.

**Failure behavior.** The fleet taxonomy sweep fails closed rather than
truncating silently: `SweepError::CapExceeded` when the listed-object count
exceeds an explicit cap, `SweepError::MalformedPage` when a truncated
listing page carries no continuation token. `Command::Sweep` itself exits
nonzero whenever `unknown_object_count > 0`, surfacing an unrecognized key
shape as an operator-visible signal rather than swallowing it. Whole-community
deletion's own bulk-delete step is fail-visible on partial failure (folded
into a typed outcome distinguishing deleted, already-missing, failed, and
versioned-key results) — that behavior belongs to the sibling datastore
nodes' own failure-behavior sections and is not repeated here.

## Links

- Container-level existence and shared-bucket summary:
  [`architecture-containers-object-storage`](../../../architecture/containers/object-storage.md)
- Git-CAS retention axiom (root design doc, not a corpus node):
  [`docs/git-on-object-storage.md`](../../../../../../docs/git-on-object-storage.md)
- Retention-relevant code: `crates/buzz-media/src/bucket_index.rs`
  (`tenant_prefixes`, `is_tenant_owned_key`, `is_known_fleet_key`,
  `sweep_bucket_taxonomy`); `crates/buzz-deletion/src/lib.rs`
  (`execute_stage`, `enumerate_tenant_prefixes`, `Command::Sweep`);
  `crates/buzz-db/src/deletion.rs` (`DeletionStage`, `mark_retention_pending`,
  `record_taxonomy_sweep`); `crates/buzz-relay/src/storage_sweep.rs`
  (unrelated hourly usage-metrics task, linked here only to distinguish it
  from the fleet taxonomy sweep above).
- Operator entry point: `crates/buzz-admin/src/deletions.rs`
  (`buzz_deletion::run`).
- Schema: `migrations/0029_community_deletion.sql`
  (`community_deletion_requests`, `storage_taxonomy_sweeps`).

## Scope and omissions

**This node covers** what the shared object-storage bucket retains forever
versus what any code path in this repository can ever delete, the mechanism
and audit trail for the one deletion path that exists, the deliberate
non-implementation of fleet-wide shared-CAS physical garbage collection, and
the one non-destructive taxonomy-safety sweep that inspects but does not act
on retention risk.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The object-storage container's existence, shared-bucket summary, and Blossom media's own full key taxonomy | `architecture-containers-object-storage` |
| The Blossom/media datastore's own full schema, access patterns, and non-retention operational characteristics | `blossom-storage.md` (id `layers-data-object-storage-blossom-storage`), **not yet merged to `origin/launchpad` at this node's authoring revision** — no `relationships` edge to it exists here for that reason, per `AGENTS.md` step 9 |
| The git-CAS datastore's own full schema, access patterns, and non-retention operational characteristics | `git-objects.md` (id `layers-data-object-storage-git-objects`), **not yet merged to `origin/launchpad` at this node's authoring revision** — same reason as above |
| The formal safety proofs of `docs/git-on-object-storage.md` beyond its retention axiom | `docs/git-on-object-storage.md` |
| The full whole-community deletion state machine (approval, fencing, drain, Postgres/Redis purge mechanics) beyond the retention-relevant stages | `crates/buzz-db/src/deletion.rs`, `crates/buzz-deletion/src/lib.rs` — a future corpus node, if one is scoped for the deletion engine itself |
| The evidence-class contract (FACT/INFERENCE/TEAM_KNOWLEDGE, citation shapes) | `launchpad/docs/corpus/AGENTS.md` |

**No `relationships` beyond the one declared above.** The only object-storage
node confirmed present on `origin/launchpad` at this revision is
`architecture-containers-object-storage`; both sibling datastore nodes this
document's evidence cites directly by path (`blossom-storage.md`,
`git-objects.md`) exist only on unmerged sibling task branches, so neither id
resolves against the merge target and declaring an edge to either would be a
hard validation error in CI, per `AGENTS.md` step 9's explicit warning about
this exact trap. Revisit this once they merge.

**Expected but not verified when this node was written:**

- **Whether any fleet-wide shared-CAS physical-GC sweep is planned or
  scheduled outside this checkout** — a private ops repository, a future
  issue, or operational runbook. `buzz-deletion`'s own recorded policy
  string states it is "out of V1 scope," which is a statement about this
  codebase's current implementation, not a claim about future plans.
- **Whether the not-yet-merged `blossom-storage.md` and `git-objects.md`
  will land with the exact ids assumed in this node's prose**
  (`layers-data-object-storage-blossom-storage`,
  `layers-data-object-storage-git-objects`). Read directly from those
  branches' own front matter at this node's authoring time, but unmerged
  content can still change before it lands.
- **Whether production or staging enables S3 bucket versioning** on the
  configured bucket — `buzz-deletion` treats this as a hard, permanent
  failure condition for its one destructive path if true; the same gap
  `architecture-containers-object-storage` and both sibling datastore nodes
  already name for the identical reason (the answer lives in the private
  `squareup/block-coder-tf-stacks` repository, outside this checkout).
