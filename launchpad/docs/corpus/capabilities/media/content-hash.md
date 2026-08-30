---
id: capabilities-media-content-hash
type: capabilities
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
  - statement: "VISION_PROJECTS.md's own Status table marks 'Blossom media storage (SHA-256, S3)' as shipped ('✅ Ships today')."
    entry_class: FACT
    evidence:
      - "VISION_PROJECTS.md:252"
  - statement: "For the buffered (image and generic-file) upload path, the server computes the SHA-256 of the exact received bytes itself, inside a spawn_blocking closure, as `hex::encode(Sha256::digest(&bytes))` — the hash is never taken on faith from the client."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/src/upload.rs"
  - statement: "For the video upload path, SHA-256 is computed incrementally with a `Sha256` hasher's `update()` calls as each chunk is streamed to a temporary file on disk, so the full body is never held in RAM at once; the digest is finalized with `hasher.finalize()` after the last chunk."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/src/upload.rs"
  - statement: "Before any request body is read, buzz-relay's `AuthenticatedUpload` Axum extractor requires an `X-SHA-256` request header (BUD-11), validates it is exactly 64 lowercase hex characters, and requires it to match at least one `x` tag on the Blossom kind:24242 auth event; this is a claimed-hash check on attacker-controlled input and is distinct from the server's own post-upload hash computation."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/media.rs"
  - statement: "After the server computes the actual SHA-256 of the received bytes, `verify_blossom_upload_auth` re-checks that at least one `x` tag on the auth event matches that computed hash and returns `MediaError::HashMismatch` if none does — so a claimed hash that passed the pre-body header check can still be rejected once the real bytes are hashed."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/src/auth.rs"
      - "crates/buzz-media/src/upload.rs"
  - statement: "The blob is stored at a content-addressed key `{sha256}.{ext}`, built once per upload from the computed hash and the resolved extension; identical bytes uploaded under different auth events or in different communities resolve to the same blob key."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/src/upload.rs"
  - statement: "Blob bytes are shared, community-agnostic CAS, but the metadata sidecar that gates read access is community-scoped at `_meta/{community}/{sha256}.json`, built by `MediaStorage::sidecar_key`/`ctx_sidecar_key` — so the same hash uploaded independently in two communities shares one blob object but never shares sidecar visibility."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/src/storage.rs"
  - statement: "A unit test (`same_sha_sidecars_do_not_bleed_between_communities`) asserts that two communities' sidecar keys for the identical sha256 are distinct and independently addressable, guarding the CAS/sidecar separation above against regression."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/src/storage.rs"
  - statement: "The upload pipeline is idempotent by content: if both the blob key and the community sidecar already exist for the computed hash, the pipeline short-circuits — it does not re-run `storage.put` — and returns a `BlobDescriptor` built from the existing sidecar, though it still records a fresh upload event for moderation attribution when per-event upload records are enabled, since a no-op storage write is still a distinct upload event."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/src/upload.rs"
  - statement: "If metadata generation (thumbnail/dimensions) fails after the blob has already been stored, the code deliberately leaves the blob in place rather than deleting it, reasoning in its own comments that a concurrent upload of the same hash could otherwise race a deletion against a request that is about to reference that blob via its own sidecar write, and notes that a background GC job to sweep such orphans does not exist yet."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/src/upload.rs"
  - statement: "On GET and HEAD, `validate_media_path` accepts only a bare 64-character lowercase-hex hash, `{hash}.{ext}`, or `{hash}.thumb.jpg` (1-3 dot-separated segments), and rejects any other path shape as `MediaError::NotFound` before any storage or sidecar lookup runs."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/media.rs"
  - statement: "Reading the full GET/HEAD serve path (`get_blob`, `head_blob`, `serve_blob_for_tenant`, `resolve_s3_key`) found no step that re-hashes the stored bytes to confirm they still match the requested hash — the requested hash is validated only for shape, then used directly as (part of) the storage lookup key. Content integrity of an object already at rest in the object store is not independently re-verified by the serve path."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/media.rs"
  - statement: "When a request names an explicit extension (`{hash}.{ext}`), `serve_blob_for_tenant` compares the requested extension against the extension recorded in that hash's own sidecar and returns `NotFound` on a mismatch — the sidecar's `ext` field, not the requested path, is authoritative for which extension a given hash may be served under."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/media.rs"
  - statement: "A Blossom read (`kind:24242`, verb `get`) auth event may authorize a request in either of two ways: an `x` tag matching the specific requested sha256 (blob-scoped), or a `server` tag matching the bound tenant host under the shared host-normalization rule (server-scoped, valid for any blob on that host until the event's expiration) — `verify_blossom_get_auth` accepts either."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/src/auth.rs"
  - statement: "An end-to-end test (`test_upload_and_get`) uploads a small JPEG, computes its SHA-256 independently in the test, asserts the returned `BlobDescriptor.sha256` equals that computed hash and that the descriptor's `url` contains it, then performs an authenticated GET on `/media/{sha256}.jpg` and asserts the returned bytes are byte-identical to what was uploaded."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/e2e_media.rs"
  - statement: "An end-to-end test (`test_upload_idempotent`) uploads the same bytes twice and asserts the `sha256` field in both `BlobDescriptor` responses is identical, exercising the content-addressed dedup path from outside the process."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/e2e_media.rs"
  - statement: "Two end-to-end tests assert the server-side hash cross-check fails closed: `test_upload_hash_mismatch_returns_400` signs an auth event whose `x` tag does not match the uploaded body's real hash and asserts the response is `401` (its name says 400, its assertion is 401), and `test_upload_missing_x_sha256_returns_401` omits the mandatory `X-SHA-256` header entirely and asserts `401`."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/e2e_media.rs"
  - statement: "These end-to-end media tests are annotated `#[ignore]` and were read directly rather than executed in this session — this repository's convention (see `crates/buzz-test-client/tests/`) is that they require a running relay plus Postgres/Redis and are run explicitly, not as part of a default `cargo test`."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/e2e_media.rs"
  - statement: "The code's own comments identify this scheme as an implementation of the Blossom protocol's BUD-01 (blob retrieval), BUD-02 (upload), and BUD-11 (kind:24242 authorization) conventions, by name, at the relevant call sites."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/src/auth.rs"
      - "crates/buzz-relay/src/api/media.rs"
---

# Content hash: capability

Buzz identifies and addresses every media blob — image, video, or generic file —
by the SHA-256 hex digest of its exact bytes, computed by the server itself rather
than trusted from the uploading client. That hash is simultaneously the blob's
storage key, its retrieval path segment, and the mandatory authorization scope
for both the upload and the read that follows: a user or agent uploads bytes once,
gets back a hash-bearing URL, and any later request for that exact content resolves
to the same object regardless of who uploaded it or when. Re-uploading identical
bytes is a no-op against storage (deduplication for free), and a Blossom
authorization event can scope itself to one specific hash rather than to a whole
server.

## Maturity

**Shipped.** VISION_PROJECTS.md's own Status table marks "Blossom media storage
(SHA-256, S3)" as "✅ Ships today" (`VISION_PROJECTS.md:252`), and the mechanism
described below is implemented and exercised by end-to-end tests in
`crates/buzz-test-client/tests/e2e_media.rs`.

## Behavioral rules and variants

- **The hash is computed twice, for two different reasons.** The client must
  claim a hash upfront — an `X-SHA-256` header (shape-validated: 64 lowercase hex
  characters) matched against an `x` tag on the signed Blossom auth event — and
  this claimed-hash check runs *before* any request body is buffered, so an
  unauthenticated or wrongly-scoped request never causes the server to read the
  body at all. Separately, once the body is available, the server computes the
  *actual* SHA-256 of the bytes it received and re-checks it against the same `x`
  tag; a mismatch here fails closed with `MediaError::HashMismatch` even though
  the pre-body claimed-hash check already passed.
- **Two computation paths, one guarantee.** Buffered uploads (images, generic
  files) hash the whole body at once via `Sha256::digest`. Video uploads hash
  incrementally via `Sha256::update()` while streaming to a temp file, so the
  full video is never held in RAM — but both paths produce the same kind of
  digest, checked the same way, before the blob is stored.
- **Content-addressing is global; access is not.** The blob itself is stored
  once per unique hash, shared across communities and uploaders — but a
  community-scoped metadata sidecar (`_meta/{community}/{sha256}.json`) is the
  actual read/existence gate. Knowing a hash lets you *ask* for the blob; the
  sidecar decides whether your community can see it.
- **Idempotent by content, not by request.** Uploading bytes the server has
  already stored short-circuits the storage write and returns the existing
  descriptor, but a per-event upload record (used for moderation attribution)
  is still written when that feature is enabled — a repeat upload is a distinct
  event even when it stores nothing new.
- **Orphans are left, not cleaned up.** If metadata generation fails after the
  blob is written, the blob is deliberately not deleted (to avoid racing a
  concurrent uploader of the same hash) and no background sweep exists yet to
  reclaim it.
- **The hash is verified on write, not re-verified on read.** `GET`/`HEAD`
  validate only that the requested hash is a well-formed 64-character lowercase
  hex string (plus an optional `.ext` or `.thumb.jpg` suffix); the server does
  not re-hash the object already sitting in storage to confirm it still matches
  before serving it. An explicit extension request is checked against the
  hash's own sidecar-recorded canonical extension, but that is a different
  check from re-verifying the content itself against the hash.
- **Read authorization can be hash-scoped or server-scoped.** A Blossom read
  auth event may name one specific hash (`x` tag) or grant access to the whole
  bound host (`server` tag) until it expires — both are valid, and relay
  membership is still enforced independently afterward either way.

## Boundary

This node does not describe:
- **How the object store is built or configured** — the S3/MinIO client,
  credential resolution, and addressing style are the object-storage
  architecture node's subject, not this one's; this node cites that container
  only for where the content-addressed bytes ultimately land.
- **The upload and download flows in full** — request-binding order, rate
  limiting, concurrency limits, relay-membership enforcement, and range-request
  handling are the upload/download flow nodes' subject; this node covers only
  the hashing and content-addressing behavior that runs inside those flows.
- **Any interface/CLI surface for media** — no corpus interface node for the
  Blossom HTTP routes exists yet to `references`; when one is authored, it
  should describe the route/command shapes and this node should be linked from
  it, not restate its content here.
- **Other content-addressing schemes elsewhere in Buzz** — Nostr event IDs and
  git object hashing are separate mechanisms in different subsystems and are
  out of scope for this node, which is about Blossom media blobs specifically
  (per this task's own impacted-components scope).
- **How the running relay is operated** — object-store capacity planning,
  orphan-blob GC, and monitoring are `operations`-surface subject matter, not
  a capability description.

## Relationships

- references: architecture-flows-media-upload
- references: architecture-flows-media-download
- references: architecture-containers-object-storage

## Scope and omissions

**This node covers** what the SHA-256 content-hash scheme is, how the hash is
computed on upload (buffered and streaming paths), how it is used as the
storage key and the community-scoped sidecar gate, its idempotency and orphan
behavior, what is and is not re-verified on read, and the end-to-end tests that
demonstrate the write-side hash check and content dedup.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| How the object store itself is built/configured | `architecture-containers-object-storage` |
| The full upload/download request flows (auth ordering, rate limits, range requests) | `architecture-flows-media-upload`, `architecture-flows-media-download` |
| The HTTP/CLI interface surface for media | no corpus interface node exists yet |
| Nostr event-id hashing and git object hashing | out of scope for this task; not investigated here |
| How the running system operates/garbage-collects orphan blobs | the `operations` corpus surface |

**Expected but not verified when this node was written:**
- **The Blossom BUD-01/BUD-02/BUD-11 specification texts themselves were not
  fetched or read.** This node's description of the protocol's expectations
  comes entirely from what Buzz's own code and doc-comments state they
  implement, not from an independent reading of the upstream specification —
  no claim here should be read as a statement about what those BUDs say beyond
  what the cited code enforces.
- **Whether an orphan-blob GC job exists anywhere outside `crates/buzz-media`
  was not checked** beyond the comment in `upload.rs` stating none exists yet;
  a background sweep implemented elsewhere (e.g. an ops script) would not have
  been found by this investigation, which was scoped to `crates/buzz-media`
  and the relay's media handlers.
- **No live upload was performed against a running relay.** The end-to-end
  tests cited above were read, not executed, in this session; their
  `#[ignore]` annotation means they require infrastructure this investigation
  did not stand up.
