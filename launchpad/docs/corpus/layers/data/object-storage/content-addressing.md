---
id: layers-data-object-storage-content-addressing
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
  - statement: "node.schema.json's type enum is architecture, layers, capabilities, platforms, implementation, interfaces-events, verification, operations, development, release, governance, agent, ingestion, and contains no data value — a node whose path lives under layers/ takes type: layers, not type: data."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "A media blob's object-storage key is the hex-encoded SHA-256 of the uploaded bytes plus its extension: `let sha256 = hex::encode(Sha256::digest(&bytes)); ... let key = format!(\"{sha256}.{ext}\");` — the key is derived, never client-supplied."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/src/upload.rs"
  - statement: "buzz-media's bucket key taxonomy has five classes, per bucket_index.rs's own doc comment: thumb (`{sha256}.thumb.jpg`), blob (`{sha256}.{ext}`), sidecar (`_meta/{community-uuid}/{sha256}.json`), auxiliary (`_uploads/{community-uuid}/{sha256}/{ulid}.json`), and unknown (a deliberate, non-silent catch-all for anything matching no known shape)."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/src/bucket_index.rs"
  - statement: "The sidecar key builder's own comment states the addressing/tenancy split directly: 'Raw media bytes remain shared content-addressed CAS (`{sha}.{ext}`), but the metadata sidecar is the tenant read gate' — the sidecar key format is `_meta/{community}/{sha256}.json`."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/src/storage.rs"
  - statement: "Git pack and manifest objects are keyed by the hex SHA-256 of their own bytes: `pub fn content_key(prefix: &str, bytes: &[u8]) -> String { ... format!(\"{prefix}/{}\", hex::encode(h.finalize())) }`, called as `put_pack` -> `packs/<sha256-of-pack-bytes>` and (by the same `put_immutable` helper) manifests -> `manifests/<sha256-of-manifest-bytes>`."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/store.rs"
  - statement: "The git idx sidecar is not content-addressed by its own bytes — it is keyed by the pack digest it was derived from (`idx/<pack_digest>`), and its own doc comment states why: 'The idx is a pure cache derived from `packs/<pack_digest>`, so it is keyed by the pack digest rather than by the idx bytes.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/store.rs"
  - statement: "A git ref's current value is stored at a community-scoped pointer key, not a content-addressed one: `pub fn pointer_key(community: CommunityId, owner: &str, repo: &str) -> String { ... format!(\"repos/{community}/{owner}/{repo}/pointer\") }`, and the function's own doc comment states the boundary this node's tenancy section relies on: the `repos/<community>/<owner>/<repo>/` namespace 'keeps the existing repo-local subtree intact under the server-resolved community boundary, while shared pack/manifest CAS objects remain outside that scoped pointer namespace.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/manifest.rs"
  - statement: "Blossom upload verification requires the computed SHA-256 to match an `x` tag on the client's kind:24242 auth event (BUD-11 §6); `verify_blossom_upload_auth` checks `auth_event.tags.iter().any(|tag| tag.kind().to_string() == \"x\" && (tag.content() == Some(sha256)))` and returns `MediaError::HashMismatch` when no tag matches."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/src/auth.rs"
  - statement: "Git pack/manifest writes are create-only via a conditional PUT (`IF_NONE_MATCH: \"*\"`), and the write path's own doc comment frames this as a constructive idempotency proof rather than a defensive check: 'a 412 collision means the key already holds bytes whose digest equals sha256(these bytes), so by A1 (content-addressing) the stored bytes equal these bytes' — a 412 response is mapped to `Ok(key)`, not an error."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/store.rs"
  - statement: "Git reads are verified against their content-addressed key on every read via `get_verified`, whose own doc comment states it is 'the read-side enforcement of A1 -- any deviation from the content-addressed invariant becomes a DigestMismatch error, never a silent corruption,' by re-hashing the fetched bytes and comparing to `expected_digest`."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/store.rs"
  - statement: "The git-on-object-storage design doc's Axiom A1 states the protocol relies on create-only, content-addressed writes rather than S3 object-lock features, and states plainly: 'No deletion under the protocol. Pack and manifest objects are never deleted by the protocol... Physical pruning of unreachable packs is a backend retention concern outside this proof boundary.'"
    entry_class: FACT
    evidence:
      - "docs/git-on-object-storage.md"
  - statement: "On upload, if metadata preparation fails after the blob PUT succeeds, the orphaned blob is deliberately left in place rather than deleted, per the code's own comment: concurrent uploads of the same hash could otherwise race and delete a blob another request is about to reference, and 'a V2 background GC job can sweep blobs with no matching sidecar' — no such GC job exists in this codebase at the recorded revision."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/src/upload.rs"
  - statement: "Media upload is idempotent only when both the blob key and the sidecar key already exist (`if sidecar_exists && blob_exists`); if only one is present the handler falls through and re-executes the write path rather than treating the upload as already complete."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/src/upload.rs"
  - statement: "No Postgres table tracks media-blob or git-object metadata or reference counts. The only git-related table is `git_repo_names` (a per-community repo-name registry, not object data), and the only blob-referencing column anywhere in migrations/ is `moderation_reports.target_blob_sha256`, a report-target foreign reference, not a storage record."
    entry_class: INFERENCE
    evidence:
      - "migrations/0002_git_repo_names.sql"
      - "migrations/0006_moderation.sql"
      - "grep_migrations_for_create_table(migrations/) -> no blobs/media/attachments/git_objects table exists among the matches"
    confidence: 0.85
  - statement: "git_repo_names exists specifically because it is the one piece of git state that is not content-addressable: the migration's own comment states 'The relay holds no persistent per-repo filesystem state: git reads/writes hydrate an ephemeral bare repo from object storage per request... This table is the one remaining shared-state need -- repo-name uniqueness.'"
    entry_class: FACT
    evidence:
      - "migrations/0002_git_repo_names.sql"
  - statement: "moderation_reports.target_blob_sha256 is one of three mutually exclusive report-target columns (event/pubkey/blob), `BYTEA CHECK (length = 32)`, enforced by a table-level CHECK requiring exactly the matching column for `target_kind` to be non-null."
    entry_class: FACT
    evidence:
      - "migrations/0006_moderation.sql"
  - statement: "The media download handler does not re-hash served bytes against the requested hash; it instead gates on the sidecar first, with its own comment stating the authority model directly: 'Sidecar gate FIRST -- reject before any blob I/O. Storage is not authoritative.' Content-type is taken from the sidecar rather than any S3-reported metadata, 'to prevent MIME spoofing via tampered storage.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/media.rs"
  - statement: "The sidecar lookup gating a media read is scoped to the requesting tenant (`state.media_storage.read_sidecar_mime(tenant, sha256_ext)`), so a community can only serve a hash for which its own sidecar exists, even though the underlying blob bytes at that hash are stored once, globally, and are not themselves tenant-scoped."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/media.rs"
  - statement: "On origin/launchpad's corpus tree at this node's authoring time, three nodes already exist and are safe relationships targets: architecture-containers-object-storage, architecture-flows-media-upload, architecture-flows-media-download. All three already document the Blossom route table, the full auth/verification chain, HTTP error-code mapping, and the git CAS pointer scheme in more depth than this node repeats."
    entry_class: FACT
    evidence:
      - "git_ls_tree(origin/launchpad, launchpad/docs/corpus) -> architecture/containers/object-storage.md (id: architecture-containers-object-storage), architecture/flows/media-upload.md (id: architecture-flows-media-upload), architecture/flows/media-download.md (id: architecture-flows-media-download)"
  - statement: "Issue #1068's definition of done requires this node to state whether the store is authoritative, derived, cache or transport; describe owned data, key access patterns, lifecycle/retention and consistency semantics; name tenancy/security boundaries and failure behavior; and link schema/migrations/code/tests rather than copy DDL."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1068 definition of done"
  - statement: "This node's required-section shape (authoritative/derived/cache/transport classification, owned-data inventory, access patterns, lifecycle/retention, consistency semantics, tenancy/security boundaries, failure behavior, link-not-copy-DDL) follows templates/datastore.md's own required sections and evidence expectations, applied to one addressing mechanism shared by two datastore-adjacent object families rather than to one full datastore instance -- no layers-typed per-topic template exists yet to follow instead, per AGENTS.md's own stated gap."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/templates/datastore.md"
      - "launchpad/docs/corpus/AGENTS.md"
    confidence: 0.7
relationships:
  - type: part-of
    target: architecture-containers-object-storage
  - type: references
    target: architecture-flows-media-upload
  - type: references
    target: architecture-flows-media-download
---

# Content addressing in Buzz's object storage

## Purpose and scope

Buzz's S3-compatible object store (MinIO locally, per `.env.example`) holds two
independent families of bytes addressed by their own SHA-256 content hash
rather than by a caller-chosen name: **media blobs**, uploaded via the
Blossom protocol and served by `crates/buzz-media`, and **git pack/manifest
objects**, written and read by `crates/buzz-relay/src/api/git` for the
relay's git-on-object-storage smart-HTTP hosting. Both share one physical
bucket.

This node documents the addressing mechanism itself: what determines an
object's key, what that implies about authority, lifecycle and consistency,
and where the tenancy boundary actually sits relative to that key. It is
**not** a restatement of the Blossom route table, the full Nostr auth-event
verification chain, or HTTP status-code mapping — `architecture-containers-object-storage`
(this node's `part-of` parent) already inventories the container-level facts,
and `architecture-flows-media-upload` / `architecture-flows-media-download`
already document those flows end to end. Read those first for "how a request
gets served"; this node answers "why the key looks like that, and what that
buys or costs."

## Addressing scheme

| Family | Key shape | Constructed at |
|---|---|---|
| Media blob | `{sha256}.{ext}` | `crates/buzz-media/src/upload.rs` |
| Media thumbnail | `{sha256}.thumb.jpg` | `crates/buzz-media/src/bucket_index.rs` (taxonomy), thumbnail generation path |
| Git pack | `packs/<sha256-of-pack-bytes>` | `crates/buzz-relay/src/api/git/store.rs` (`content_key`, `put_pack`) |
| Git manifest | `manifests/<sha256-of-manifest-bytes>` | same `content_key`/`put_immutable` helper, `put_manifest` |

Both families use the identical construction: hash the bytes, hex-encode the
digest, and that digest — not any caller input — is the key. Neither family
allows the writer to choose an object's name.

Two related key shapes are **not** content-addressed by their own bytes, and
matter to the sections below:

| Key | Shape | Why it differs |
|---|---|---|
| Media sidecar | `_meta/{community-uuid}/{sha256}.json` | Keyed by the *blob's* hash plus the tenant, not by the sidecar's own bytes — it is the tenant binding, not the content. |
| Git idx cache | `idx/<pack_digest>` | Keyed by the *pack's* digest so a hydrator can derive the idx key without re-reading the manifest, not by the idx file's own bytes. |
| Git ref pointer | `repos/{community}/{owner}/{repo}/pointer` | The one genuinely mutable object in this whole scheme — a ref points at whichever manifest digest is current, and that pointer itself is community-scoped, not content-addressed at all. |

## Authoritative, derived, cache, or transport

| Object class | Classification | Why |
|---|---|---|
| Media blob bytes | **Authoritative** | No Postgres table holds a copy or a reference count; deleting the S3 object loses the media permanently. |
| Media sidecar | **Authoritative** (for the tenant binding) | It is the only record of which community may read a given hash, and it is itself S3-resident, not a database row. |
| Media thumbnail | **Derived** | Regenerable from the blob; its absence degrades a preview, not correctness. |
| Media auxiliary upload record | **Derived / audit** | Optional (`BUZZ_MEDIA_UPLOAD_RECORDS`-gated) moderation trail, not needed to serve the blob. |
| Git pack / manifest | **Authoritative** | Per Axiom A1 (`docs/git-on-object-storage.md`), these are never deleted by the protocol; they are the only durable record of repository content — the relay itself "holds no persistent per-repo filesystem state" (`migrations/0002_git_repo_names.sql`'s own comment). |
| Git idx sidecar | **Pure cache** | Its own code comment calls it exactly that — derivable from the pack it indexes; a cache miss triggers regeneration with `git index-pack`, never a hydrate failure. |
| Git ref pointer | **Authoritative** (for "what does this ref currently point at"), but not content-addressed | A mutable compare-and-swap value layered on top of an otherwise immutable, content-addressed store. |

Nothing in this scheme is **transport-only** — every content-addressed key
that survives a request is durably written, not a passthrough buffer.

## Owned data: key-namespace inventory

This is a structural list, not a schema dump — see the Migration and
DDL links below rather than copied `CREATE TABLE` text.

- `{sha256}.{ext}` — media blob bytes.
- `{sha256}.thumb.jpg` — media thumbnail.
- `_meta/{community-uuid}/{sha256}.json` — media sidecar (tenant binding + canonical content-type/extension).
- `_uploads/{community-uuid}/{sha256}/{ulid}.json` — optional moderation audit record.
- `packs/<sha256>` — git pack object.
- `manifests/<sha256>` — git manifest object (ref-tree snapshot).
- `idx/<pack_digest>` — git pack index cache.
- `repos/{community}/{owner}/{repo}/pointer` — git ref pointer (current manifest digest for one repo).
- `git_repo_names` (Postgres, `migrations/0002_git_repo_names.sql`) — the one piece of git state that is *not* content-addressable: per-community repo-name uniqueness.
- `moderation_reports.target_blob_sha256` (Postgres, `migrations/0006_moderation.sql`) — a report-target reference into the blob namespace, not a copy of it.

## Access patterns

**Media write (upload):** bytes are hashed in-request
(`crates/buzz-media/src/upload.rs`); the resulting hex digest must match an
`x` tag on the caller's Blossom kind:24242 auth event (BUD-11 §6,
`crates/buzz-media/src/auth.rs::verify_blossom_upload_auth`) — a hash
mismatch is `MediaError::HashMismatch` before any storage write happens.
Verification is therefore at write time, driven by the client's claim.

**Media read (download):** `crates/buzz-relay/src/api/media.rs`'s
`serve_blob_for_tenant` does **not** re-hash the bytes it serves. It trusts
the object store for content correctness and instead gates on the
tenant-scoped sidecar first — its own comment states "Storage is not
authoritative" in the access-control sense, meaning the sidecar, not the S3
object, decides whether *this* request may see it.

**Git write:** the key is derived from the bytes inside `put_immutable`, so a
write can never be misfiled under the wrong digest by construction. A 412
(`If-None-Match` collision) is treated as success, not error, because a
matching key can, by the addressing invariant, only hold matching bytes.

**Git read:** `get_verified` / `get_verified_limited` re-hash every fetched
object and compare against the digest the caller expected, turning any
storage-layer corruption into a hard `DigestMismatch` rather than silently
serving wrong bytes. This is the read-time mirror of media's write-time
check — the two families verify at opposite ends of the pipe.

## Lifecycle and retention

**Media:** an upload that fails after the blob PUT but before the sidecar is
written leaves the blob orphaned *deliberately* — deleting it would risk a
race with a concurrent request about to reference the same hash. The code
names its own gap: "a V2 background GC job can sweep blobs with no matching
sidecar after a grace period." No such job exists in this codebase at the
recorded revision; orphaned media blobs currently accumulate without bound
beyond the per-upload size limit.

**Git:** retention is a protocol-level guarantee, not a maintenance task —
Axiom A1 states packs and manifests are never deleted by the protocol at
all, so every manifest digest a reader has ever seen remains fetchable
indefinitely. Physical pruning of unreachable packs is explicitly named as
future, out-of-protocol backend work, not something this codebase performs
today.

## Consistency semantics

Both families lean on the same backend property — a successful `PUT` is
immediately visible to a subsequent `GET` (Axiom A2 in
`docs/git-on-object-storage.md`, stated there as a documented S3 property,
not independently re-verified by the media code path). On top of that:

- **Git** uses `If-None-Match: *` for content-addressed writes (create-only,
  collision-safe by construction) and `If-Match: <etag>` compare-and-swap for
  the mutable ref pointer — the only place in this scheme where a real
  "last write wins vs. loses" race exists, and a losing writer gets a
  semantic `LostRace` outcome, not a generic error.
- **Media** achieves the same create-only effect without a conditional
  header: idempotency is checked explicitly (`sidecar_exists && blob_exists`)
  before deciding whether to re-run the write path.

## Tenancy and security boundaries

The content-addressed keys themselves carry **no tenant or community
segment** — `{sha256}.{ext}`, `packs/<sha256>`, and `manifests/<sha256>` are
global across every community sharing the bucket. Tenancy is enforced one
layer above the addressing scheme, not inside it:

- **Media:** the sidecar (`_meta/{community}/{sha256}.json`) is the read
  gate, and it is looked up scoped to the *requesting* tenant
  (`read_sidecar_mime(tenant, sha256_ext)`). Two different communities
  uploading byte-identical content share the same physical blob object, but
  each still needs its own sidecar entry before that community's members can
  read it — knowing the hash alone does not grant cross-tenant access.
- **Git:** pack and manifest CAS objects are likewise global, but the
  mutable ref pointer lives under a community-scoped key
  (`repos/{community}/{owner}/{repo}/pointer`). The pointer key's own doc
  comment states this split explicitly: the per-repo namespace sits "under
  the server-resolved community boundary, while shared pack/manifest CAS
  objects remain outside that scoped pointer namespace."

This is a real design property worth naming plainly: **the object store's
content-addressed layer is not itself a tenant isolation boundary.**
Isolation is enforced by the sidecar and the pointer namespace, both of
which sit above the addressing scheme documented here — see
`architecture-flows-media-upload` / `-download` for the full authorization
chain that enforces it.

## Failure behavior

| Failure | Where | Outcome |
|---|---|---|
| Uploaded bytes don't match claimed hash | Media upload, `auth.rs` | `MediaError::HashMismatch`, collapsed to a generic 401 at the API boundary (see `architecture-flows-media-upload` for the auth-oracle rationale — not repeated here). |
| Stored bytes don't match a git object's key digest on read | Git, `store.rs::get_verified` | Hard `StoreError::DigestMismatch` — surfaced, never silently served. |
| No sidecar for the requesting tenant | Media download | Generic 404 (`MediaError::NotFound`) — no distinction between "doesn't exist" and "exists for a different tenant." |
| Concurrent create-only write collision | Git, `put_immutable` / `put_pointer` | A content-addressed 412 is mapped to success (idempotent, by construction); a pointer-CAS 412 is the semantic `LostRace` outcome for the losing writer. |
| Metadata write fails after blob PUT succeeds | Media upload | Blob is left orphaned on purpose; no automatic cleanup exists yet (see Lifecycle above). |

## Deduplication

Deduplication is **incidental to the addressing scheme, not a designed
feature** on either path. Media's idempotency short-circuit (skip the blob
PUT when both blob and sidecar already exist) exists for correctness under
concurrent identical uploads, not as a storage-savings mechanism; a
different uploader referencing existing bytes still produces its own
moderation-audit record when that feature is enabled. Git's create-only
CAS write treats a same-content collision as success for the same
constructive reason. Neither path maintains an explicit reference count or
dedup index.

## Scope and omissions

**This node covers** the SHA-256 content-addressing mechanism shared by
media blobs and git pack/manifest objects: what determines a key, what that
implies for authority, lifecycle, consistency and the tenancy boundary, and
how failures surface on each side.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Blossom route table, full request/response shapes | `architecture-flows-media-upload`, `architecture-flows-media-download` |
| Full Nostr kind:24242 auth-event verification chain | `architecture-flows-media-upload`, `architecture-flows-media-download` |
| HTTP status-code mapping and the auth-oracle rationale for collapsing errors | `architecture-flows-media-upload` |
| Container-level existence/technology/one-line responsibility of the object store | `architecture-containers-object-storage` |
| `.env.example`'s stale Typesense variables | Named as a pre-existing gap in `templates/datastore.md`; not this node's subject |
| Whether `moderation_reports.target_blob_sha256` is ever cross-checked against a sidecar at moderation-action time | Not traced to every call site this session — the column's definition was read, its full usage was not |

**Expected but not verified when this node was written:**

- **Whether any environment currently runs the documented-but-unbuilt V2
  media GC job.** The code names the gap; whether work has started elsewhere
  was not checked.
- **Whether a `layers`-typed per-topic template will later formalize this
  directory's shape.** No such template exists yet; this node follows
  `templates/datastore.md`'s required-section shape directly against
  `node.schema.json`, per `AGENTS.md`'s stated fallback for unlanded
  per-type templates.
