---
id: implementation-crates-buzz-media
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
  - statement: "buzz-media is a workspace member library crate (root Cargo.toml lists \"crates/buzz-media\" in [workspace] members and buzz-media = { path = \"crates/buzz-media\" } in [workspace.dependencies]) with no binary target of its own; its own Cargo.toml describes it as \"Media storage, validation, and thumbnail generation for Buzz\"."
    entry_class: FACT
    evidence:
      - "Cargo.toml"
      - "crates/buzz-media/Cargo.toml"
  - statement: "crates/buzz-media/src/lib.rs's own doc comment states the crate has \"no Axum dependency for handlers\" and that \"Axum handlers live in buzz-relay\", and re-exports ten modules: auth, bucket_index, config, error, storage, thumbnail, types, upload, upload_record, validation."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/src/lib.rs"
  - statement: "auth.rs implements Blossom kind:24242 auth-event verification: verify_blossom_auth_event_for_verb checks Schnorr signature, kind==24242, a t tag matching the verb, an expiration tag in the future, created_at in the past (5s clock-skew tolerance), and — if server tags are present — that this relay's domain appears in at least one; verify_blossom_upload_auth additionally requires an x tag matching the uploaded sha256 (cited internally as BUD-11 §6); verify_blossom_get_auth accepts either a matching x tag or a matching server tag per BUD-01."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/src/auth.rs"
  - statement: "config.rs defines MediaConfig (S3 endpoint/access key/secret key/bucket/region/addressing style, per-content-type byte caps for images/GIFs/video/generic files, public_base_url, and opt-in upload-record/edge-header settings) and a MediaConfig::validate() method that rejects an IP-header setting without upload_records_enabled, a port-header setting without an IP header, and malformed header names."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/src/config.rs"
  - statement: "buzz-relay's own Config struct embeds buzz_media::MediaConfig verbatim as its `media` field, and separately declares media_max_concurrent_uploads, media_max_concurrent_uploads_per_pubkey, and media_uploads_per_minute as buzz-relay's own fields, not part of buzz_media::MediaConfig -- so per-upload rate/concurrency limiting is owned by buzz-relay, not buzz-media."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/config.rs"
  - statement: "buzz-relay's main() calls config.media.validate() and, only on success, buzz_media::MediaStorage::new(&config.media) during startup, before the relay begins serving; a validate() failure aborts startup with \"invalid media config\"."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs"
  - statement: "storage.rs's MediaStorage wraps an rust-s3 Bucket client and exposes put, put_file (streams from disk via an 8 MiB buffered reader, never loading a full video into RAM), get, get_range, get_stream, head, delete, delete_objects (bulk delete folding per-key outcomes into BulkDeleteOutcome so callers own retry/fail-closed policy), and bucket_versioning_detected (a synthetic-probe-object workaround because rust-s3 exposes no GetBucketVersioning call)."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/src/storage.rs"
  - statement: "storage.rs's sidecar_key/ctx_sidecar_key/get_sidecar/put_sidecar functions build and read/write a community-scoped _meta/{community}/{sha256}.json object; its own doc comments state this sidecar is the tenant read gate for otherwise shared content-addressed blob bytes, and that callers must never derive the community from client-supplied data."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/src/storage.rs"
  - statement: "bucket_index.rs is a pure, I/O-free module: classify_key partitions any bucket key string into KeyClass::{Thumb, Blob, Sidecar, Auxiliary, Unknown} (Unknown is a deliberate catch-all so a malformed key is loud rather than silently absorbed); tenant_prefixes/is_tenant_owned_key define the exact three listing prefixes and key shapes one community owns; fold_bucket_listing and sweep_bucket_taxonomy fold a paginated bucket listing into BucketSnapshot/TaxonomySweepOutcome under a caller-supplied object cap, retaining only bounded per-sha/per-binding state, never the full listing."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/src/bucket_index.rs"
  - statement: "upload.rs implements three upload pipelines: process_upload (buffered image path), process_file_upload (buffered generic-file/attachment path, deny-list validated, always served with Content-Disposition: attachment), and process_video_upload (streaming path: hashes incrementally into a tempfile::NamedTempFile, verifies the Blossom auth event's x tag against the computed hash, runs full MP4 validation, stores via MediaStorage::put_file, and never buffers the whole body in RAM). All three share a both-exist idempotency short-circuit and an optional per-event upload-record write via upload_record.rs's record_upload_event, gated on MediaConfig.upload_records_enabled."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/src/upload.rs"
      - "crates/buzz-media/src/upload_record.rs"
  - statement: "validation.rs enforces an image MIME allowlist (jpeg/png/gif/webp) that deliberately excludes video/mp4 so a spoofed image upload is still caught by magic-byte sniffing (looks_like_iso_bmff); a generic-file deny-list (validate_file_content) that blocks active-content/executable MIME types while still accepting unsniffable plain text/CSV/JSON as application/octet-stream downloads; per-format structural metadata-stripping checks for JPEG, PNG, WebP, GIF, and MP4 that reject embedded location/metadata payloads (one allowlisted Buzz-snapshot PNG tEXt chunk excepted); and validate_video_file, which checks container/codec (H.264/AAC only), track counts, duration (≤600s), resolution (≤3840×2160), and moov-before-mdat fast-start placement by scanning only 8-byte top-level atom headers, bounded to MAX_ATOMS iterations."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/src/validation.rs"
  - statement: "validation.rs alone carries 53 of the crate's 126 #[test]/#[tokio::test] functions found by grep across crates/buzz-media/src/*.rs, including fixture-driven regression tests against real iOS/Android encoder output stored under crates/buzz-media/tests/fixtures/{ios,android}/."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/src/validation.rs"
      - "crates/buzz-media/tests/fixtures/ios/README.md"
      - "crates/buzz-media/tests/fixtures/android/README.md"
  - statement: "thumbnail.rs's single function, generate_image_metadata_sync, is a synchronous, CPU-bound function returning (BlobMeta, Option<thumbnail JPEG bytes>); its own doc comment states the caller runs it inside spawn_blocking and is responsible for the S3 write of any thumbnail bytes returned -- this module performs no I/O itself."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/src/thumbnail.rs"
  - statement: "types.rs's BlobDescriptor struct is documented as \"returned by PUT /upload and the legacy media alias\": url, sha256, size, mime_type, uploaded, and optional dim/blurhash/thumb/duration fields; upload.rs's build_descriptor function constructs it."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/src/types.rs"
      - "crates/buzz-media/src/upload.rs"
  - statement: "error.rs's MediaError enum (29 variants spanning validation, auth, storage, rate-limit, and video-specific failures) implements axum::response::IntoResponse directly inside buzz-media, mapping variants to an HTTP status code and a JSON {\"error\": msg} body; error.rs imports axum::http::StatusCode and axum::response::{IntoResponse, Response} at its top, and crates/buzz-media/Cargo.toml lists axum = { workspace = true } as a direct dependency -- not merely a transitive one pulled in for other reasons."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/src/error.rs"
      - "crates/buzz-media/Cargo.toml"
  - statement: "Two more buzz-media modules depend on axum types beyond error.rs: config.rs's MediaConfig::validate uses axum::http::HeaderName to validate a configured edge-header name, and upload.rs's process_video_upload is typed over a body_stream: impl futures_core::Stream<Item = Result<Bytes, axum::Error>>."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/src/config.rs"
      - "crates/buzz-media/src/upload.rs"
  - statement: "crates/buzz-relay/src/router.rs registers exactly three Blossom HTTP routes against buzz-media-backed handlers in crates/buzz-relay/src/api/media.rs: PUT /upload and PUT /media/upload (legacy alias) to upload_blob, and GET/HEAD /media/{sha256_ext} to get_blob/head_blob, layered with a request-body-size limit sized to the larger of max_image_bytes and max_video_bytes."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs"
      - "crates/buzz-relay/src/api/media.rs"
  - statement: "crates/buzz-relay/src/api/media.rs's handlers call buzz_media:: symbols directly rather than reimplementing their logic: verify_blossom_auth_event and verify_blossom_get_auth for auth, process_video_upload/process_upload/process_file_upload for the write path, looks_like_iso_bmff for a pre-dispatch sniff, serve_inline to choose the response's Content-Disposition, and parse_public_ip/parse_port to build optional upload attribution from trusted edge headers."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/media.rs"
  - statement: "buzz_media::MediaStorage/MediaConfig and the bucket_index helpers (tenant_prefixes, is_tenant_owned_key, fold_bucket_listing) are consumed by buzz-relay well outside the Blossom media surface: crates/buzz-relay/src/handlers/imeta.rs's verify_imeta_blobs takes &buzz_media::MediaStorage to check link-preview blob references; crates/buzz-relay/src/api/git/{manifest,transport}.rs and crates/buzz-relay/src/handlers/ingest.rs call buzz_media::tenant_prefixes/is_tenant_owned_key for git-repository-pointer deletion scoping; crates/buzz-relay/src/storage_sweep.rs and crates/buzz-relay/src/main.rs call buzz_media::fold_bucket_listing for the background usage-metrics sweep; and buzz_media is additionally referenced in crates/buzz-relay/src/api/{admin/mod,bridge,gifs,invites,operator}.rs, crates/buzz-relay/src/handlers/{identity_archive,event,relay_admin}.rs, crates/buzz-relay/src/state.rs, and crates/buzz-relay/src/workflow_sink.rs."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/imeta.rs"
      - "crates/buzz-relay/src/api/git/manifest.rs"
      - "crates/buzz-relay/src/api/git/transport.rs"
      - "crates/buzz-relay/src/handlers/ingest.rs"
      - "crates/buzz-relay/src/storage_sweep.rs"
      - "crates/buzz-relay/src/main.rs"
      - "crates/buzz-relay/src/state.rs"
  - statement: "126 #[test]/#[tokio::test] functions exist directly under crates/buzz-media/src/*.rs (per-file grep count: auth.rs 14, bucket_index.rs 25, storage.rs 13, config.rs 7, upload_record.rs 7, upload.rs 4, validation.rs 53, error.rs 3; lib.rs, thumbnail.rs, and types.rs carry none), run by plain `cargo test -p buzz-media --lib` with no external infrastructure required."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/src/auth.rs"
      - "crates/buzz-media/src/bucket_index.rs"
      - "crates/buzz-media/src/storage.rs"
      - "crates/buzz-media/src/config.rs"
      - "crates/buzz-media/src/upload_record.rs"
      - "crates/buzz-media/src/upload.rs"
      - "crates/buzz-media/src/validation.rs"
      - "crates/buzz-media/src/error.rs"
  - statement: "crates/buzz-media/tests/static_creds_minio.rs and crates/buzz-media/tests/versioned_minio.rs are #[ignore]-gated live integration tests (3 and 10 test functions respectively) that round-trip the static-credential S3 path and destructive versioned-bucket deletion against a real docker-compose MinIO instance, run explicitly via `cargo test -p buzz-media --test <name> -- --ignored`."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/tests/static_creds_minio.rs"
      - "crates/buzz-media/tests/versioned_minio.rs"
  - statement: "No CI job in .github/workflows/ci.yml executes buzz-media's own unit tests. The \"Unit Tests\" job runs only `just test-unit`, whose recipe enumerates explicit `cargo nextest run -p <crate>` selections (buzz-core, buzz-auth, buzz-voice, buzz-cli, buzz-db, buzz-conformance, buzz-push-gateway, buzz-backend-kubernetes, buzz-agent, and a filtered buzz-relay --lib api::admin subset) and does not name buzz-media; the recipe's own comment states \"nothing in CI runs `cargo test --workspace`; workspace membership alone buys clippy/check, not a single executed test.\" Backend Integration's nextest archive is built with `-p buzz-db -p buzz-relay -p buzz-test-client --lib`, which also excludes buzz-media."
    entry_class: FACT
    evidence:
      - "Justfile"
      - ".github/workflows/ci.yml"
  - statement: "buzz-media's behavior is instead exercised end-to-end, indirectly, through buzz-test-client's e2e_media, e2e_media_extended, and e2e_media_video suites, run in Backend Integration via `cargo test -p buzz-test-client --no-fail-fast --test e2e_media --test e2e_media_extended --test e2e_media_video -- --ignored --nocapture` against a live relay -- these validate observable HTTP behavior through buzz-relay's routes, not buzz-media's own functions directly."
    entry_class: FACT
    evidence:
      - ".github/workflows/ci.yml"
  - statement: "No crates/buzz-media/README.md exists; the crate has no dedicated crate-level documentation file beyond its Cargo.toml description and in-source doc comments."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/Cargo.toml"
  - statement: "The corpus node architecture-containers-object-storage, architecture-flows-media-upload, and architecture-flows-media-download exist on origin/launchpad at the recorded revision (git ls-tree -r --name-only HEAD -- launchpad/docs/corpus), and each already documents part of buzz-media's role at the architecture-diagram level of detail, so this node's Implementation surface intentionally goes to the module/symbol level instead of restating their content."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/containers/object-storage.md"
      - "launchpad/docs/corpus/architecture/flows/media-upload.md"
      - "launchpad/docs/corpus/architecture/flows/media-download.md"
---

# buzz-media: implementation reference

This node documents `crates/buzz-media`, the library crate providing Buzz's
S3-compatible object-storage client, Blossom (BUD-01/BUD-11) auth verification,
upload content validation, thumbnail/blurhash generation, and bucket
key-taxonomy classification. It claims to realize the "media" half of the
ownership boundary already described at the architecture level by the corpus
node `architecture-containers-object-storage`, and to implement the wire-level
Blossom protocol (BUD-01 blob descriptors, BUD-11 auth events) that protocol
has no corpus node of its own yet.

## Target

**Primary target: `architecture-containers-object-storage`** (corpus node,
`launchpad/docs/corpus/architecture/containers/object-storage.md`). That node's
own "Ownership boundary" section states `buzz-media` owns "`MediaStorage` (the
S3 client wrapper), `MediaConfig` ..., Blossom BUD-11 auth verification, upload
content validation, thumbnail/blurhash generation, and the bucket
key-taxonomy classifier" — this node is the module/symbol-level realization of
exactly that claim.

**Secondary target: the Blossom protocol**, specifically BUD-01 (server
requirements / blob descriptor shape) and BUD-11 (upload authorization events),
named directly in the crate's own source comments (`storage.rs`: "just enough
for BUD-01 response headers"; `auth.rs`: "BUD-11 §6: 'at least one x tag
matches'"). Neither BUD document has a corpus node id at this writing, so no
`implements` edge targets them — per `AGENTS.md`'s rule, an edge to a
nonexistent id is a hard validation error, not a placeholder. A reader can open
the specification directly at
[github.com/hzrd149/blossom](https://github.com/hzrd149/blossom).

## Implementation surface

| Component / file / symbol | Realizes | Note |
|---|---|---|
| `crates/buzz-media/src/auth.rs` — `verify_blossom_auth_event_for_verb`, `verify_blossom_upload_auth`, `verify_blossom_get_auth` | BUD-11 kind:24242 auth-event validation (signature, kind, verb, expiration, timestamp window, `server`-tag match) | Verb-specific `x`/`server` scope checks are layered on top of the common validity check, not folded into it |
| `crates/buzz-media/src/storage.rs` — `MediaStorage` (`put`/`put_file`/`get`/`get_range`/`get_stream`/`head`/`delete`/`delete_objects`, `sidecar_key`/`get_sidecar`/`put_sidecar`, `bucket_versioning_detected`) | The S3-compatible client half of `architecture-containers-object-storage`'s "media" ownership boundary | `put_file`/`get_stream` never buffer a full blob in RAM; the sidecar is the tenant read gate for otherwise shared content-addressed bytes |
| `crates/buzz-media/src/config.rs` — `MediaConfig`, `MediaConfig::validate` | The crate's startup-validated configuration surface (S3 endpoint/credentials/addressing style, per-content-type byte caps, opt-in upload-record/edge-header settings) | `validate()` is invoked explicitly by `buzz-relay`'s `main()` before `MediaStorage::new` — see *Verification* |
| `crates/buzz-media/src/upload.rs` — `process_upload`, `process_file_upload`, `process_video_upload` | The three upload pipelines behind `PUT /upload` | `process_video_upload` streams to a `NamedTempFile` with incremental hashing; the other two buffer fully in RAM, bounded by `MediaConfig`'s byte caps |
| `crates/buzz-media/src/validation.rs` — `validate_content`, `validate_file_content`, `validate_video_file`, `serve_inline`, `looks_like_iso_bmff` | Content sniffing, MIME allow/deny-listing, per-format metadata stripping, and MP4 structural validation gating what `upload.rs` may store | 53 of the crate's 126 unit tests live in this one module, including real-encoder fixture regressions |
| `crates/buzz-media/src/thumbnail.rs` — `generate_image_metadata_sync` | Synchronous thumbnail/blurhash/dimension derivation from raw bytes | Returns data only; the caller performs the actual S3 write inside `spawn_blocking` |
| `crates/buzz-media/src/bucket_index.rs` — `classify_key`, `tenant_prefixes`, `is_tenant_owned_key`, `fold_bucket_listing`, `sweep_bucket_taxonomy` | The pure key-taxonomy classifier and paginated-listing fold `buzz-relay`'s storage sweep and community-deletion code both depend on | No I/O; unknown key shapes fall to a loud `Unknown` class instead of being silently absorbed |
| `crates/buzz-media/src/error.rs` — `MediaError`, `impl IntoResponse for MediaError` | Maps every buzz-media failure mode directly to an HTTP status + JSON body, consumed by `buzz-relay`'s `?` operator in `api::media` handlers | See *Divergences* — couples the crate directly to `axum` despite `lib.rs`'s "no Axum dependency" framing |
| `crates/buzz-media/src/upload_record.rs` — `UploadRecord`, `record_upload_event`, `parse_public_ip`, `parse_port` | The opt-in per-upload moderation side-channel record and its fail-empty edge-header parsing | Off by default (`MediaConfig.upload_records_enabled`); none of this module's write path runs unless enabled |
| `crates/buzz-media/src/types.rs` — `BlobDescriptor` | The BUD-01 blob-descriptor JSON response shape | Built by `upload.rs`'s `build_descriptor`, returned by all three upload pipelines |

**Integration points (owned by `buzz-relay`, not this crate).**
`crates/buzz-relay/src/router.rs` mounts the three Blossom routes onto
`crates/buzz-relay/src/api/media.rs`'s `upload_blob`/`get_blob`/`head_blob`,
which call the `buzz_media::` symbols above directly.
`crates/buzz-relay/src/state.rs` holds `media_storage: Arc<MediaStorage>`,
constructed once in `main()` after `config.media.validate()` succeeds.
`buzz_media::MediaStorage`/`MediaConfig` and the `bucket_index` helpers are
also consumed by `buzz-relay` outside the Blossom surface: git-repository
CAS-pointer deletion (`api/git/{manifest,transport}.rs`,
`handlers/ingest.rs`), `imeta` link-preview blob verification
(`handlers/imeta.rs`), and the background storage-usage sweep
(`storage_sweep.rs`, `main.rs`). Documenting `buzz-relay`'s own routing and
handler implementation is out of scope for this node — see *Scope and
omissions*.

## Divergences

**buzz-media's unit tests are not run by any current CI job — the largest
divergence found.** The crate carries 126 `#[test]`/`#[tokio::test]`
functions directly under `src/*.rs`. `.github/workflows/ci.yml`'s "Unit
Tests" job runs only `just test-unit`, whose `Justfile` recipe enumerates
explicit `-p <crate>` selections that do not include `buzz-media`, and whose
own comment states plainly: "nothing in CI runs `cargo test --workspace`;
workspace membership alone buys clippy/check, not a single executed test."
The Backend Integration job's nextest archive is built scoped to
`-p buzz-db -p buzz-relay -p buzz-test-client --lib` only, which also
excludes `buzz-media`. The only CI coverage that touches this crate's
behavior is indirect: `buzz-test-client`'s `e2e_media`/`e2e_media_extended`/
`e2e_media_video` suites exercise observable HTTP behavior through
`buzz-relay`'s routes, not `buzz-media`'s own unit-level functions. This
reads as an unintentional gap rather than a deliberate exclusion — nothing in
the `Justfile` or `ci.yml` states a reason `buzz-media` was left off the
enumerated list, unlike several neighboring recipe comments that explain
*why* a given crate is (or is not) in the unit job.

**The crate's "no Axum dependency" framing is narrower than its actual
dependency.** `lib.rs`'s doc comment states the crate has "no Axum dependency
for handlers," and the architecture node `architecture-containers-object-storage`
paraphrases this more broadly as "no Axum dependency of its own." Neither
statement is false about *handlers* — `buzz-media` defines no `Router` or
Axum handler function, and that ownership boundary (handlers live in
`buzz-relay`) holds. But `crates/buzz-media/Cargo.toml` lists `axum` as a
direct dependency, and the crate uses it directly in three places:
`error.rs`'s `impl IntoResponse for MediaError` (imports
`axum::http::StatusCode` and `axum::response::{IntoResponse, Response}`),
`config.rs`'s use of `axum::http::HeaderName` to validate an edge-header
name, and `upload.rs`'s `process_video_upload`, whose streaming parameter is
typed over `axum::Error`. A reader taking "no Axum dependency" at face value
would be surprised by a real, direct `axum` import in three modules.

## Verification

**Automated, infrastructure-free:** `cargo test -p buzz-media --lib` runs the
crate's 126 unit tests locally with no external services. **Not currently
wired into CI** — see *Divergences* above; this is the node's most
significant finding, not merely a testing-strategy note.

**Automated, live-infrastructure, manual-only:**
`cargo test -p buzz-media --test static_creds_minio -- --ignored` and
`cargo test -p buzz-media --test versioned_minio -- --ignored --nocapture`
round-trip the static-credential S3 path and destructive versioned-bucket
deletion against a real `docker-compose` MinIO instance. Neither is
`#[ignore]`-selected by any CI job found in `.github/workflows/ci.yml`.

**Indirect, via CI:** `buzz-test-client`'s `e2e_media`, `e2e_media_extended`,
and `e2e_media_video` suites run in the Backend Integration job
(`cargo test -p buzz-test-client --no-fail-fast --test e2e_media --test
e2e_media_extended --test e2e_media_video -- --ignored --nocapture`) against
a live relay process, exercising `buzz-media`'s logic only as observed
through `buzz-relay`'s HTTP surface.

**Startup self-check:** `MediaConfig::validate()` runs in `buzz-relay`'s
`main()` before `MediaStorage::new`, so a misconfigured deployment fails fast
at startup rather than on the first request.

**Corpus-level:** this node itself is checked by
`python3 launchpad/project-intelligence/corpus/validate.py`, which confirms
front-matter schema conformance and that cited repository paths resolve —
not that any cited statement is true, which is the reviewer's job per
`AGENTS.md`.

## Relationships

- implements: architecture-containers-object-storage
- references: architecture-flows-media-upload
- references: architecture-flows-media-download

## Scope and omissions

**This node covers** `buzz-media`'s module-by-module responsibility, its
public interfaces/entry points (the symbols re-exported from `lib.rs`), its
important dependencies (`rust-s3`, `infer`, `image`, `mp4`, `axum` for
error-response conversion), where and how `buzz-relay` calls into it
(including uses outside the Blossom media surface), its representative test
surface, and — as the node's most load-bearing finding — the gap between
that test surface and what CI actually executes.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The object-storage container's deployment topology, data-consistency model, and security posture at the architecture level | `architecture-containers-object-storage` |
| The HTTP request/response shape of the Blossom endpoints and the upload/download flow's step-by-step sequencing | `architecture-flows-media-upload`, `architecture-flows-media-download` |
| `buzz-relay`'s own routing, handler, and `AppState` implementation (`router.rs`, `api/media.rs`, `state.rs`) as a subject in its own right | a future `buzz-relay` implementation-reference node, not yet written |
| The git-on-object-storage code path (`crates/buzz-relay/src/api/git/store.rs`), which reuses `buzz_media::config::S3AddressingStyle` but constructs its own independent S3 client | `architecture-containers-object-storage`'s existing coverage of that boundary; no implementation-reference node exists for it yet |
| The full BUD-01/BUD-11 Blossom specification text | the upstream spec at github.com/hzrd149/blossom |
| Fixing the CI test-execution gap identified in *Divergences* | not this node's job — documenting the gap is; a future task should decide whether to add `buzz-media` to `just test-unit`'s enumerated list |

**Expected but not verified when this node was written:**

- **Whether any hook or script outside this repository's own `Justfile`/
  `.github/workflows/*.yml`** (for example a cohort-side pre-push hook not
  checked into `block/buzz`) **executes `buzz-media`'s unit tests.** Only
  this repository's own committed CI configuration was checked.
- **Whether `MediaError`'s several access-control-flavored variants**
  (`RelayMembershipRequired`, `CommunityWriteFenced`, `TokenRevoked`,
  `PubkeyMismatch`, `InsufficientScope`) **are ever actually constructed from
  within `buzz-media`'s own code**, or exist only so that `buzz-relay` can
  convert an auth-layer failure into the same `IntoResponse` path. This was
  not traced call-site by call-site and is not claimed either way above.
- **Coverage measurement** (e.g. `cargo llvm-cov`) for `buzz-media` was not
  checked; this node's test-count claims are function counts, not line or
  branch coverage.
