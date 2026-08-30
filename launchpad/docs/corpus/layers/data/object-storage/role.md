---
id: layers-data-object-storage-role
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
  - statement: "node.schema.json's type enum is architecture, layers, capabilities, platforms, implementation, interfaces-events, verification, operations, development, release, governance, agent, ingestion, and contains no data or datastore value — a node whose path lives under layers/ takes type: layers."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "This node uses type: layers rather than templates/datastore.md's own suggested value for a real datastore instance (architecture, at confidence 0.6), for the same reason the two existing sibling documents in this same directory chose it: the issue's own directory assignment (launchpad/docs/corpus/layers/data/object-storage/role.md, from issue #1073's corpus-plan:v2 alias header) is a more concrete signal than that template's speculative reasoning about a hypothetical instance, and PRD #602's surface list and Feature #610's title ('data and storage layer corpus exists') both point at layers as the intended surface. Per standards/taxonomy.md's step-4 rule (disclose an imperfect fit rather than silently resolve it), this tension is named here rather than picked unilaterally."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
      - "launchpad/docs/corpus/templates/datastore.md"
      - "launchpad/docs/corpus/standards/taxonomy.md"
    confidence: 0.65
  - statement: "This node treats role.md as a whole-store synthesis spanning both namespaces the shared object-storage bucket holds (Blossom media and git-on-object-storage), rather than a third per-namespace deep dive. No document read this session states that reading directly; it follows from three things checked rather than assumed: the target path sits directly under object-storage/ rather than under a namespace-named subdirectory the way the two existing sibling documents' subjects are named; issue #1073's own Definition of Done restates, at the level of 'the store' singular, the same four classification bullets (authoritative/derived/cache/transport, owned data and access patterns, tenancy and failure, link-not-copy-DDL) the two namespace-level siblings already answered once each for their own namespace; and no third namespace exists in this bucket for a document at this path to describe instead. This is disclosed as an inference, not asserted as a settled corpus convention -- the sibling role.md tasks for postgres (#1087) and redis (#1097) are single-technology stores with no namespace split, so they cannot confirm or refute this reading."
    entry_class: INFERENCE
    evidence:
      - "gh_issue_view(1073) -> corpus-plan:v2 alias header names launchpad/docs/corpus/layers/data/object-storage/role.md directly; Definition of Done restates the same four store-classification bullets the two namespace-level siblings answered once each per namespace, now at the level of 'the store' singular"
      - "launchpad/docs/corpus/templates/datastore.md"
    confidence: 0.55
  - statement: "buzz-media (crates/buzz-media/src/storage.rs) constructs its own MediaStorage client, and crates/buzz-relay/src/api/git/store.rs independently constructs a second, separate rust-s3 Bucket client for content-addressed git objects; both are configured from the same BUZZ_S3_* variables, documented in .env.example under one heading, '# S3-Compatible Object Storage (media + Git/CAS)' -- one physical bucket, two independent client code paths compiled into the buzz-relay binary, not two separately deployed services."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/src/storage.rs"
      - "crates/buzz-relay/src/api/git/store.rs"
      - ".env.example"
  - statement: "No SQL migration defines a table for media blob bytes, media metadata, or git pack/manifest object bytes. A case-insensitive search of every file under migrations/ for media, blob, git_object or pack matches only migrations/0006_moderation.sql's moderation_reports.target_blob_sha256 column (a report-target foreign reference, BYTEA CHECK (length = 32), not a storage record) and migrations/0002_git_repo_names.sql's git_repo_names table (a per-community repo-name uniqueness registry, not object data). The S3-compatible bucket is the sole durable location of blob and git-object bytes in this repository, and no other datastore (Postgres via buzz-db, Redis via buzz-pubsub) holds a copy -- this store is authoritative for both namespaces it holds, not a cache, derived projection, or transport layer."
    entry_class: INFERENCE
    evidence:
      - "grep(pattern='media|blob|git_object|pack', glob='migrations/*.sql', case_insensitive=true) -> migrations/0006_moderation.sql (target_blob_sha256 column), migrations/0002_git_repo_names.sql (git_repo_names table); no other match, at repository revision 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
      - "migrations/0006_moderation.sql"
      - "migrations/0002_git_repo_names.sql"
    confidence: 0.85
  - statement: "MediaStorage exposes put, put_file, get, get_range, get_stream, head, head_with_metadata, delete, delete_objects, bucket_versioning_detected, sidecar_key/ctx_sidecar_key, get_sidecar/put_sidecar, read_sidecar_mime, ping, and list_page/list_prefix_page; buzz-media's own bucket_index.rs classifies every key in the bucket's Blossom half into exactly five classes -- Thumb, Blob, Sidecar, Auxiliary, and Unknown -- and that module's own doc comment states Unknown is deliberate: a key shape matching none of the first four is never silently coerced into one of them."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/src/storage.rs"
      - "crates/buzz-media/src/bucket_index.rs"
  - statement: "The git-CAS half of the same bucket is owned by crates/buzz-relay/src/api/git/store.rs directly (not by buzz-media): content_key builds a sha256-of-bytes key, put_pack and the manifest/pointer write paths set the IF_NONE_MATCH header to \"*\" on every content-addressed write, and a 412 response from that conditional PUT is classified as CasOutcome::LostRace -- the module's own comment states this is treated as the standard outcome of a losing compare-and-swap, not an error."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/store.rs"
  - statement: "Blossom media has a real, exercised bulk-deletion path (crates/buzz-deletion's whole-community teardown, calling MediaStorage::delete_objects), while docs/git-on-object-storage.md states its own design axiom in prose: 'No deletion under the protocol. Pack and manifest objects are never deleted by the protocol... Physical pruning of unreachable packs is a backend retention concern outside this proof boundary' -- the two namespaces sharing this one bucket have materially different lifecycle postures, not a single uniform one."
    entry_class: FACT
    evidence:
      - "crates/buzz-deletion/src/lib.rs"
      - "docs/git-on-object-storage.md"
  - statement: "crates/buzz-deletion/src/lib.rs calls MediaStorage::bucket_versioning_detected before enumerating any community's keys for deletion, and fails the whole deletion request permanently if the bucket has ever had versioning enabled; it separately treats a non-empty versioned_keys result from the bulk-delete call itself as a second, independent permanent failure. This check runs against the one shared bucket object, so a versioned bucket would block Blossom's deletion path exactly the same way regardless of whether the triggering community also holds git-CAS objects in that bucket -- the check is store-wide, even though today only the Blossom namespace exercises deletion at all."
    entry_class: FACT
    evidence:
      - "crates/buzz-deletion/src/lib.rs"
  - statement: "Both namespaces enforce their tenant boundary one layer above the raw content-addressed bytes, not on the bytes themselves: MediaStorage::sidecar_key/ctx_sidecar_key scope a community-to-blob binding to _meta/{community-uuid}/{sha256}.json, and MediaStorage::read_sidecar_mime's own doc comment states this sidecar is the tenant read gate; on the git side, the pointer key (repos/{community}/{owner}/{repo}/pointer, in crates/buzz-relay/src/api/git/manifest.rs) is community-scoped while the pack/manifest CAS objects it points at are not -- raw blob and pack bytes are shared, community-agnostic content-addressed storage in both namespaces, and neither namespace's raw bytes carry a tenancy check of their own."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/src/storage.rs"
      - "crates/buzz-relay/src/api/git/manifest.rs"
  - statement: "crates/buzz-relay/src/storage_sweep.rs's hourly, single-flight background usage sweep (which lists the bucket via MediaStorage::list_page) can be disabled entirely for a deployment whose relay credentials lack s3:ListBucket, via the BUZZ_STORAGE_METRICS kill switch -- a degrade-to-off failure mode at the whole-bucket level, not specific to either namespace's own write or read path."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/storage_sweep.rs"
  - statement: "buzz-media/tests/static_creds_minio.rs exercises a static-credential round trip against a real MinIO instance; buzz-test-client/tests/e2e_media.rs, e2e_media_extended.rs and e2e_media_video.rs cover Blossom media upload/download through the relay's HTTP surface; buzz-test-client/tests/e2e_git.rs covers the git smart-HTTP surface backed by the same bucket's git-CAS namespace."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/tests/static_creds_minio.rs"
      - "crates/buzz-test-client/tests/e2e_media.rs"
      - "crates/buzz-test-client/tests/e2e_media_extended.rs"
      - "crates/buzz-test-client/tests/e2e_media_video.rs"
      - "crates/buzz-test-client/tests/e2e_git.rs"
  - statement: "Issue #1073's definition of done requires this node to state whether the store is authoritative, derived, cache or transport; describe owned data, key access patterns, lifecycle/retention and consistency semantics; name tenancy/security boundaries and failure behavior; and link schema/migrations/code/tests rather than copy DDL."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1073 definition of done"
  - statement: "On origin/launchpad's corpus tree at this node's authoring time, architecture-containers-object-storage is the only merged node documenting this bucket; the two namespace-level siblings this node links to in prose (layers-data-object-storage-blossom-storage, layers-data-object-storage-git-objects) exist only on the unmerged origin/task/610-batch-2-data-storage branch and are not legal relationships targets per AGENTS.md step 9, which requires a target to resolve against the branch being merged into."
    entry_class: FACT
    evidence:
      - "git_ls_tree(origin/launchpad, launchpad/docs/corpus) -> architecture/containers/object-storage.md present; layers/ absent entirely"
      - "git_merge_base_is_ancestor(258b99dbf, origin/launchpad) -> false"
      - "git_merge_base_is_ancestor(f0e7e7335, origin/launchpad) -> false"
relationships:
  - type: part-of
    target: architecture-containers-object-storage
---

# Object storage: role

What role the shared S3-compatible object-storage bucket plays as a datastore in
this system, synthesized across both namespaces it holds: Blossom media
(`buzz-media`) and git-on-object-storage
(`buzz-relay`'s `api::git::store` module). This document zooms into
[`architecture-containers-object-storage`](../../../architecture/containers/object-storage.md)'s
internal shape at the level the container document deliberately keeps to one
line — what this store is *for*, structurally, as a whole — without
re-deriving either namespace's own key-shape inventory, migration mechanism,
or per-endpoint access pattern, each already covered in depth by its own
sibling document in this directory (not yet merged; linked by name below).

## Store classification

**Authoritative**, for both namespaces. No SQL migration in this repository
defines a table for media blob bytes, media metadata, or git pack/manifest
object bytes — a case-insensitive search of every file under `migrations/`
for `media`, `blob`, `git_object` or `pack` matches only
`moderation_reports.target_blob_sha256` (a report-target foreign reference,
not a storage record) and `git_repo_names` (a per-community repo-name
uniqueness registry, not object data). No other datastore in this
repository — Postgres via `buzz-db`, Redis via `buzz-pubsub` — holds a copy
of blob or git-object bytes. This bucket is not a cache in front of another
source of truth, not a derived projection, and not a transport buffer:
once either namespace writes bytes here, the bucket is where they live.

## Owned data and key access patterns

The bucket holds two disjoint key namespaces, owned by two separate code
paths compiled into the same `buzz-relay` binary:

| Namespace | Owning code | Client construction |
|---|---|---|
| Blossom media (blobs, thumbnails, tenant sidecars, optional upload records) | `crates/buzz-media` (`MediaStorage`) | `buzz-media/src/storage.rs`, exposing `put`, `put_file`, `get`, `get_range`, `get_stream`, `head`, `head_with_metadata`, `delete`, `delete_objects`, `bucket_versioning_detected`, sidecar accessors, `ping`, and paginated listing |
| Git-on-object-storage (content-addressed packs and manifests, a mutable ref pointer) | `crates/buzz-relay/src/api/git/store.rs` | A second, independent `rust-s3` client, not `MediaStorage` — `content_key`, `put_pack`, and the manifest/pointer CAS write path |

Both clients are configured from the same `BUZZ_S3_*` variables — `.env.example`
documents them under one heading, `S3-Compatible Object Storage (media +
Git/CAS)` — but neither shares the other's connection instance, credential
resolution call, or key taxonomy. `buzz-media`'s own `bucket_index.rs`
classifies every key in its half into exactly five structural classes
(`Thumb`, `Blob`, `Sidecar`, `Auxiliary`, `Unknown`, with `Unknown` a
deliberate, never-silently-coerced catch-all); the git half's own key
functions (`content_key` for packs/manifests, a separate pointer-key builder
for the mutable ref) are documented in full by the git namespace's own
sibling document, not repeated here.

## Lifecycle, retention, and consistency semantics

The two namespaces this store holds have materially different lifecycle
postures, not one uniform policy:

- **Blossom media** is create-idempotent (an upload short-circuits when both
  the blob and its sidecar already exist) and has a real, exercised
  bulk-deletion path: `crates/buzz-deletion`'s whole-community teardown calls
  `MediaStorage::delete_objects` after a per-community write-drain fence,
  manifest-driven and resumable.
- **Git-on-object-storage has no deletion under the protocol at all.**
  `docs/git-on-object-storage.md` states its own design axiom directly: "Pack
  and manifest objects are never deleted by the protocol... Physical pruning
  of unreachable packs is a backend retention concern outside this proof
  boundary."

Both namespaces derive their consistency guarantee from content-addressing
plus a conditional write, applied differently: git's pack/manifest writes set
`IF_NONE_MATCH: "*"` and treat a `412` response as the semantic
`CasOutcome::LostRace` outcome rather than an error, while Blossom's upload
path instead checks both the blob and sidecar keys for prior existence before
writing at all, short-circuiting a repeated identical upload rather than
relying on an S3-level precondition header.

## Tenancy and security boundaries

Both namespaces enforce their tenant boundary one layer above the raw
content-addressed bytes, not on the bytes themselves. `MediaStorage`'s
`sidecar_key`/`ctx_sidecar_key` scope a community-to-blob binding to
`_meta/{community-uuid}/{sha256}.json`, and `read_sidecar_mime`'s own doc
comment states this sidecar is the tenant *read gate*. On the git side, the
mutable ref pointer key (`repos/{community}/{owner}/{repo}/pointer`) is
community-scoped, while the pack/manifest objects it points at are not. In
both namespaces, raw content-addressed bytes are shared, community-agnostic
storage — the same bytes can in principle be referenced from more than one
community — and neither namespace's raw-byte key carries a tenancy check of
its own; the check lives at the sidecar or the pointer, one indirection
above.

## Failure behavior

- **A versioning check on the shared bucket, store-wide.** Before enumerating
  a community's keys for deletion, `crates/buzz-deletion` calls
  `MediaStorage::bucket_versioning_detected` and fails the whole deletion
  request permanently if the bucket has ever had versioning enabled (a
  versioned bucket's `DeleteObjects` only inserts delete markers, which
  cannot prove logical absence); a non-empty `versioned_keys` result from the
  bulk-delete call itself is treated as a second, independent permanent
  failure. This check runs against the one shared bucket object, so it would
  affect the whole store's operational posture if it ever fired — even
  though today only the Blossom namespace exercises deletion at all.
- **The background usage sweep degrades to off, not to failure.** A
  deployment whose relay credentials lack `s3:ListBucket` can disable the
  hourly storage-usage sweep entirely (`BUZZ_STORAGE_METRICS=off`) rather
  than have it fail repeatedly in the background. This applies to the whole
  bucket listing, not to either namespace's write or read path specifically.
- **A lost compare-and-swap is an expected outcome, not a fault, on the git
  side.** `CasOutcome::LostRace` (a `412` from the conditional pointer PUT)
  is handled as ordinary contention, per the git namespace's own sibling
  document.

## Links

- Container-level existence, technology, and shared-bucket ownership
  boundary: [`architecture-containers-object-storage`](../../../architecture/containers/object-storage.md)
- Blossom media namespace, full internal shape (key taxonomy, migration
  mechanism, access patterns, tenancy, failure behavior in depth): sibling
  document `blossom-storage.md` in this directory (not yet merged to
  `origin/launchpad` at this node's authoring time — see *Scope and
  omissions*)
- Git-on-object-storage namespace, full internal shape: sibling document
  `git-objects.md` in this directory (same merge status as above)
- The shared content-addressing mechanism both namespaces build on: sibling
  document `content-addressing.md` in this directory (same merge status)
- Formal safety specification for the git namespace (durability-ordering,
  manifest reconstruction, linearizability, the object-store axioms):
  [`docs/git-on-object-storage.md`](../../../../../../docs/git-on-object-storage.md)
- Code: `crates/buzz-media/src/{storage.rs,bucket_index.rs,upload.rs}`,
  `crates/buzz-relay/src/api/git/store.rs`, `crates/buzz-deletion/src/lib.rs`,
  `crates/buzz-relay/src/storage_sweep.rs`
- Tests: `crates/buzz-media/tests/static_creds_minio.rs`,
  `crates/buzz-test-client/tests/{e2e_media.rs,e2e_media_extended.rs,e2e_media_video.rs,e2e_git.rs}`

## Scope and omissions

**This node covers** the shared object-storage bucket's role as a whole
datastore: its classification, the two namespaces it owns and who accesses
each, their lifecycle/retention/consistency postures compared side by side,
the tenancy pattern both share, and the failure behaviors that apply at the
whole-bucket level rather than to one namespace alone.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The object-storage container's own existence, technology choice, and HTTP interfaces | `architecture-containers-object-storage` |
| The Blossom media namespace's full key taxonomy, migration mechanism, and per-endpoint access patterns | The `blossom-storage.md` sibling document (unmerged at this node's authoring time) |
| The git-on-object-storage namespace's full key taxonomy, migration mechanism, and per-endpoint access patterns | The `git-objects.md` sibling document (unmerged at this node's authoring time) |
| The shared content-addressing mechanism's own detailed proof and worked key derivations | The `content-addressing.md` sibling document (unmerged at this node's authoring time) |
| The formal safety proof for git-on-object-storage (Theorems, TLA+ model) | `docs/git-on-object-storage.md` |
| The domain meaning of an uploaded blob or a git object | Not yet documented anywhere in this corpus |
| The evidence-class contract (FACT/INFERENCE/TEAM_KNOWLEDGE, citation shapes) | `launchpad/docs/corpus/AGENTS.md` |

**No `relationships` beyond the one declared above.** The three most directly
relevant sibling documents — `blossom-storage.md`, `git-objects.md`, and
`content-addressing.md` — all exist only on the unmerged
`origin/task/610-batch-2-data-storage` branch at this node's authoring time
(confirmed with `git merge-base --is-ancestor` against each sibling's own
commit, not assumed from branch name alone); `AGENTS.md` step 9 requires a
relationship target to resolve against the branch being merged into, not the
author's own worktree, so none of the three is a legal target today even
though this document links to all three in prose. Once they merge, this node
should gain `references` edges to each, per `templates/datastore.md`'s own
stated precedent for an instance-to-topic edge of this shape.

**Expected but not verified when this node was written:**

- **Whether this document's own premise — that `role.md` is a whole-store
  synthesis distinct from a third per-namespace deep dive — matches what the
  batch that scoped issue #1073 actually intended.** No source read this
  session states that reading directly; it is inferred from the target
  path's placement (directly under `object-storage/`, not under a
  namespace-named subdirectory) and from issue #1073's own Definition of
  Done restating the same four classification bullets the two namespace
  documents already answered once each, now at the level of "the store"
  singular. See the corresponding `INFERENCE` entry in this node's own
  evidence ledger.
- **Whether staging or production enables S3 bucket versioning** on the
  configured bucket was not established here. `crates/buzz-deletion` treats
  this as a hard, permanent failure condition for the whole store if true;
  `architecture-containers-object-storage` and both namespace siblings name
  the identical gap, and this node inherits it without re-verifying anything
  new.
- **Whether the two namespace siblings' own eventual `type: layers` versus
  `templates/datastore.md`'s suggested `architecture` tension gets resolved
  the same way once a human reviews all three together.** This node follows
  the same precedent as the two siblings rather than re-arguing it, but the
  underlying question is unresolved corpus-wide, not settled by repetition
  across three nodes.
