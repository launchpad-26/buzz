---
id: layers-data-object-storage-blossom-storage
type: layers
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - operator
evidence:
  - statement: "This node was authored and checked against repository revision 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5."
    entry_class: FACT
    evidence:
      - "commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
  - statement: "buzz-media describes itself as 'Media storage, validation, and thumbnail generation for Buzz' and is the crate that owns the Blossom half of the shared S3-compatible object-storage container documented by architecture-containers-object-storage; that container node states the bucket also holds a disjoint git-on-object-storage namespace this document does not cover."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/Cargo.toml"
      - "launchpad/docs/corpus/architecture/containers/object-storage.md"
  - statement: "No SQL file under migrations/ references media storage (grep -rl media migrations/*.sql returns no matches at the recorded revision), and the media key namespace has no relational schema of its own; the S3-compatible bucket is the sole durable location of blob bytes and their sidecar metadata, and no other datastore in this repository (Postgres via buzz-db, Redis via buzz-pubsub) holds a copy — this is an authoritative store, not a cache, derived projection, or transport layer."
    entry_class: INFERENCE
    evidence:
      - "migrations/0001_initial_schema.sql"
      - "crates/buzz-media/src/storage.rs"
    confidence: 0.85
  - statement: "MediaStorage::put and MediaStorage::put_file write blob bytes via rust-s3's put_object_with_content_type / put_object_stream_with_content_type with no conditional-write precondition header, unlike the git-on-object-storage path (crates/buzz-relay/src/api/git/store.rs), which the object-storage container node documents as using If-None-Match: * for its content-addressed writes."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/src/storage.rs"
      - "launchpad/docs/corpus/architecture/containers/object-storage.md"
  - statement: "crates/buzz-media/src/bucket_index.rs classifies every bucket key into exactly five classes: thumb ({sha256}.thumb.jpg), blob ({sha256}.{ext}), sidecar (_meta/{community-uuid}/{sha256}.json), auxiliary (_uploads/{community-uuid}/{sha256}/{ulid}.json), and unknown (a deliberate, non-silent catch-all for anything not matching the first four shapes)."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/src/bucket_index.rs"
  - statement: "There is no schema-migration tool for this key namespace, unlike Postgres's embedded sqlx::migrate! (crates/buzz-db/src/migration.rs); the key namespace instead evolves as a source-code change to classify_key, and any key shape the classifier does not recognize falls to Unknown rather than being silently coerced into an existing class, keeping the storage-sweep's usage gauges loud instead of wrong on an unrecognized shape."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/src/bucket_index.rs"
      - "crates/buzz-db/src/migration.rs"
  - statement: "MediaStorage exposes put, put_file, get, get_range, get_stream, head, head_with_metadata, delete, delete_objects, get_sidecar, put_sidecar, ping and list_page/list_prefix_page; crates/buzz-relay/src/api/media.rs is the sole HTTP-facing caller (upload_blob, get_blob, head_blob), buzz-relay's storage_sweep.rs is the sole caller of list_page for read-only usage metrics, and buzz-deletion is the sole caller of delete_objects outside tests."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/src/storage.rs"
      - "crates/buzz-relay/src/api/media.rs"
      - "crates/buzz-relay/src/storage_sweep.rs"
      - "crates/buzz-deletion/src/lib.rs"
  - statement: "Upload processing (crates/buzz-media/src/upload.rs) hashes the body, verifies Blossom auth, derives the content-addressed key, and applies a both-exist idempotency short-circuit before ever writing a blob — a repeated upload of identical bytes does no redundant PUT, per that module's own doc comment."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/src/upload.rs"
  - statement: "Blob bytes have no per-object TTL or expiry in this codebase; the only bulk-deletion path is crates/buzz-deletion ('Durable whole-community deletion engine for Buzz'), whose sole caller of MediaStorage::delete_objects outside tests (crates/buzz-deletion/src/lib.rs, in its Drained deletion stage) performs manifest-driven, chunked, idempotent bulk deletes after a per-community write-drain fence — deletion is whole-community, not per-blob or time-based."
    entry_class: FACT
    evidence:
      - "crates/buzz-deletion/Cargo.toml"
      - "crates/buzz-deletion/src/lib.rs"
  - statement: "Before enumerating a community's keys for deletion, crates/buzz-deletion/src/lib.rs calls MediaStorage::bucket_versioning_detected and fails the whole deletion request permanently ('bucket versioning detected; deletion cannot prove logical absence with delete markers') if the probe finds the bucket has ever had versioning enabled; the same code path separately treats a non-empty versioned_keys result from the actual bulk-delete call as a second, independent permanent failure, because a versioned bucket's DeleteObjects only inserts delete markers rather than proving logical absence."
    entry_class: FACT
    evidence:
      - "crates/buzz-deletion/src/lib.rs"
      - "crates/buzz-media/src/storage.rs"
  - statement: "MediaStorage::sidecar_key/ctx_sidecar_key build the community-scoped _meta/{community}/{sha256}.json key from buzz_core's CommunityId/TenantContext, and MediaStorage::put_sidecar's own doc comment states the sidecar is the tenant read gate for otherwise-shared content-addressed bytes: raw blob bytes are shared CAS across communities, but a community can only resolve a blob's metadata (and therefore serve it) through its own sidecar key."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/src/storage.rs"
  - statement: "MediaStorage::read_sidecar_mime deliberately collapses an absent sidecar and a storage read failure into the same None result, and its own doc comment states public read handlers collapse that to a single 404 so that a request scoped to community A cannot distinguish a blob that exists only for community B from a blob that does not exist at all — a tenancy boundary enforced at the sidecar-read call site, not merely documented."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/src/storage.rs"
  - statement: "Upload and get requests are authorized by verifying a Blossom kind:24242 auth event per BUD-11 in crates/buzz-media/src/auth.rs, and uploaded bytes are validated by magic-byte MIME sniffing in crates/buzz-media/src/validation.rs against an explicit allowlist, independent of the client-supplied Content-Type — both are restated here only by reference, since architecture-containers-object-storage already documents them as container-level security implications and this node does not repeat that detail."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/src/auth.rs"
      - "crates/buzz-media/src/validation.rs"
      - "launchpad/docs/corpus/architecture/containers/object-storage.md"
  - statement: "crates/buzz-relay/src/storage_sweep.rs's hourly background sweep can be disabled entirely via BUZZ_STORAGE_METRICS=off, and crates/buzz-media/src/upload_record.rs's optional uploader-IP capture (gated by BUZZ_MEDIA_UPLOAD_IP_HEADER, itself gated behind the off-by-default BUZZ_MEDIA_UPLOAD_RECORDS flag) is fail-empty: a missing, malformed, or non-public address records nothing rather than a wrong value, per that module's own doc comment."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/storage_sweep.rs"
      - "crates/buzz-media/src/upload_record.rs"
  - statement: "buzz-media/tests/static_creds_minio.rs exercises a static-credential round trip against a real MinIO instance, and buzz-test-client's e2e_media.rs and e2e_media_extended.rs cover media upload/download through the relay's HTTP surface, per architecture-containers-object-storage's own evidence ledger for the same test suite."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/tests/static_creds_minio.rs"
      - "crates/buzz-test-client/tests/e2e_media.rs"
      - "crates/buzz-test-client/tests/e2e_media_extended.rs"
relationships:
  - type: part-of
    target: architecture-containers-object-storage
---

# Blossom storage

The Blossom (media) half of the shared S3-compatible object-storage bucket
that [`architecture-containers-object-storage`](../../../architecture/containers/object-storage.md)
inventories as one container. This document zooms into that container's
internal shape for the media path only — `buzz-media`'s own key namespace,
its (non-)migration mechanism, who reads and writes it, and its lifecycle,
tenancy, and failure characteristics. It does **not** cover the container's
own existence, technology choice, or the sibling git-on-object-storage
namespace that shares the same physical bucket — those are the container
node's job, linked above rather than repeated here.

## Store classification

**Authoritative.** The bucket is the sole durable location of Blossom blob
bytes and their community-scoped sidecar metadata. No SQL migration in this
repository defines a media-related table, and no other datastore (Postgres
via `buzz-db`, Redis via `buzz-pubsub`) holds a copy of blob bytes or their
metadata. This is not a cache in front of another source of truth, not a
derived projection computed from other data, and not a transport buffer —
once a blob is written, the bucket is where it lives.

## Technology & attachment profile

Shared with the git-on-object-storage path: an S3-compatible endpoint via
`rust-s3`, configured through `BUZZ_S3_*` (endpoint, credentials, bucket,
region, addressing style). This document does not restate that surface —
see the container node's *Technology* and *Deployment implications*
sections for the connection shape, credential-resolution chain, and
per-environment values.

## Key-namespace inventory

One row per key class recognized by `crates/buzz-media/src/bucket_index.rs`'s
`classify_key`. This is a structural list — what kind of thing a key shape
identifies — not a description of what the referenced data means.

| Class | Key shape | Structural purpose |
|---|---|---|
| `blob` | `{sha256}.{ext}` | The physical, content-addressed bytes of one uploaded object. Shared CAS across every community. |
| `thumb` | `{sha256}.thumb.jpg` | A generated JPEG thumbnail, keyed to its source blob's sha256. |
| `sidecar` | `_meta/{community-uuid}/{sha256}.json` | The community-to-blob binding and the tenant read gate — see *Tenancy & security boundaries* below. |
| `auxiliary` | `_uploads/{community-uuid}/{sha256}/{ulid}.json` | An optional, off-by-default moderation side-channel record of one accepted upload *event* (who, when, from where), distinct from the blob's own bytes. |
| `unknown` | anything else | Deliberate catch-all. A malformed or unrecognized key shape is never silently coerced into one of the four classes above, so usage gauges built from this classifier stay loud instead of wrong. |

## Migration / key-shape versioning mechanism

There is no schema-migration tool for this namespace, unlike Postgres's
embedded `sqlx::migrate!` (`crates/buzz-db/src/migration.rs`, linked rather
than described here). The key namespace instead evolves as an ordinary
source-code change to `classify_key` and the modules that construct each key
shape (`storage.rs`'s `sidecar_key`, `upload_record.rs`). There is no lock,
ordering guarantee, or destructive-change guard analogous to Postgres's
`SCHEMA_DESTRUCTION_LOCK_KEY` — the `Unknown` catch-all is this namespace's
only guard against an unrecognized shape being misread as something it is
not.

## Access-pattern summary

| Caller | Mechanism | Reads/writes |
|---|---|---|
| `crates/buzz-relay/src/api/media.rs` (`upload_blob`, `get_blob`, `head_blob`) | `MediaStorage`'s buffered (`put`/`get`) and streaming (`put_file`/`get_stream`/`get_range`) methods, behind Blossom BUD-11 auth | Read + write; the only HTTP-facing caller |
| `crates/buzz-media/src/upload.rs` | `MediaStorage::head`/`put`/`put_sidecar`, with a both-exist idempotency short-circuit before any write | Write (blob, thumb, sidecar), and an optional `upload_record.rs` write when `BUZZ_MEDIA_UPLOAD_RECORDS` is enabled |
| `crates/buzz-relay/src/storage_sweep.rs` | `MediaStorage::list_page`, an hourly, single-flight, cadence-independent background task | Read-only; disableable via `BUZZ_STORAGE_METRICS=off` |
| `crates/buzz-deletion` (`crates/buzz-deletion/src/lib.rs`) | `MediaStorage::bucket_versioning_detected` (preflight probe) then `MediaStorage::delete_objects` (chunked bulk delete) | Write (delete only); the sole caller of bulk delete outside tests |

No crate other than `buzz-media` itself constructs the `MediaStorage` client;
every access above goes through its public methods.

## Lifecycle & retention

Writes are content-addressed and, for blob bytes, effectively create-only in
practice (identical content always produces the identical key, and the
upload path's idempotency short-circuit avoids a redundant write) — though,
unlike the git-on-object-storage path's `If-None-Match: *` precondition,
`MediaStorage::put`/`put_file` issue plain, unconditional S3 `PUT`s with no
enforced precondition at the storage-client level.

There is no per-object TTL or scheduled expiry anywhere in this codebase.
The only deletion path is `crates/buzz-deletion`'s whole-community teardown:
after a write-drain fence closes new writes for a community and confirms
in-flight writes have drained, it enumerates that community's keys into a
durable chunk manifest and bulk-deletes each chunk via
`MediaStorage::delete_objects`, resuming from the first unstamped chunk on
crash (bulk deletes are idempotent — a missing key reports as already
deleted). Deletion is per-community and manifest-driven, never per-blob or
time-based.

## Tenancy & security boundaries

Raw blob bytes (`{sha256}.{ext}`) are shared, community-agnostic
content-addressed storage — the same bytes can be referenced by more than
one community. The tenant boundary is enforced one layer up, at the sidecar:
`MediaStorage::sidecar_key`/`ctx_sidecar_key` scope the community-to-blob
binding to `_meta/{community-uuid}/{sha256}.json`, and
`MediaStorage::put_sidecar`'s own doc comment states this sidecar is the
tenant *read gate* — a caller must never derive the community from
client-supplied metadata, only from the server-resolved request tenant.
`MediaStorage::read_sidecar_mime` collapses an absent sidecar and a storage
read failure into the same `None`, and the public read handlers collapse
that further to a single `404` — a request scoped to community A cannot
distinguish "this blob belongs to community B" from "this blob does not
exist," by construction rather than by convention.

Upload and get requests are authorized by Blossom BUD-11 (kind:24242 auth
events), and uploaded content is validated by magic-byte MIME sniffing
independent of the client-supplied `Content-Type` — both already documented
by the container node and not repeated in depth here.

## Failure behavior

- **Whole-community deletion refuses a versioned bucket, twice.** Before
  enumerating keys, `buzz-deletion` probes `bucket_versioning_detected` and
  fails the deletion request permanently if the bucket has ever had
  versioning enabled (a versioned bucket's `DeleteObjects` only inserts
  delete markers, which cannot prove logical absence). The bulk-delete call
  itself separately treats any non-empty `versioned_keys` result the same
  way, as a second, independent permanent failure — this is checked at two
  points in the deletion pipeline, not assumed to hold from the preflight
  probe alone.
- **Bulk delete is fail-visible, not fail-silent, on partial failure.**
  `MediaStorage::delete_objects` never raises on a per-key outcome; it folds
  results into a `BulkDeleteOutcome` (deleted, `already_missing`, `failed`,
  `versioned_keys`) and leaves retry/fail-closed policy to the caller —
  `buzz-deletion`'s chunked resume logic is that caller.
- **The storage sweep degrades to off, not to failure.** A deployment whose
  relay credentials lack `s3:ListBucket` can disable the hourly usage sweep
  entirely (`BUZZ_STORAGE_METRICS=off`) rather than have it fail repeatedly
  in the background.
- **Uploader-IP capture is fail-empty.** A missing, malformed, or non-public
  address records nothing rather than a guessed or wrong value, per
  `upload_record.rs`'s own doc comment — this is itself nested behind two
  independent opt-ins (`BUZZ_MEDIA_UPLOAD_RECORDS`, then
  `BUZZ_MEDIA_UPLOAD_IP_HEADER`), so its absence is the default in most
  deployments regardless of this failure mode.

## Scope and omissions

**This node covers** the Blossom/media half of the shared object-storage
bucket's own internal shape: its key-namespace inventory, its (lack of a)
schema-migration mechanism, which code paths read and write it and how,
its lifecycle and retention behavior, its tenancy and security boundaries,
and its failure behavior under whole-community deletion and sweep/upload
degradation.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The object-storage container's own existence, technology, and deployment topology | `launchpad/docs/corpus/architecture/containers/object-storage.md` |
| The disjoint git-on-object-storage key namespace sharing the same bucket | `launchpad/docs/corpus/architecture/containers/object-storage.md`, `docs/git-on-object-storage.md` |
| The full Blossom/BUD-11 auth protocol semantics | `crates/buzz-media/src/auth.rs`, the upstream Blossom spec |
| Per-endpoint HTTP request/response schemas | `crates/buzz-relay/src/api/media.rs` |
| The domain meaning of an uploaded blob (what a message attachment or avatar *is*) | a future data-entity corpus node, not yet written |
| Whether production/staging enables S3 bucket versioning on the configured bucket, which would permanently block `buzz-deletion`'s bulk-delete path | not established here; `squareup/block-coder-tf-stacks` (private, not in this checkout) is the most likely source of that fact |

**Expected but not verified when this node was written:**

- **Whether production or staging enables S3 bucket versioning** on the
  configured bucket was not established. `buzz-deletion` treats this as a
  hard, permanent failure condition if true; whether any real deployment is
  currently in that state is unknown from this checkout alone.
- **The `type` chosen for this node (`layers`) versus the `architecture`
  value the corpus's own `datastore` template recommends for a real datastore
  instance.** The issue that scoped this document names the target path
  under `layers/data/object-storage/`, and `layers` is a valid, distinct
  member of `node.schema.json`'s own `type` enum for exactly this corpus
  surface; this node follows that path rather than the template's
  general-case guidance, and the discrepancy is left open for a later corpus
  convention pass rather than resolved unilaterally here.
