---
id: architecture-flows-media-upload
type: architecture
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision a44cf52fc740ebebbdd671427480d14f0bce0115."
    entry_class: FACT
    evidence:
      - "commit a44cf52fc740ebebbdd671427480d14f0bce0115"
  - statement: "Media upload is served at `PUT /upload` and `PUT /media/upload` (legacy alias), both routed to the same `upload_blob` handler."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs"
      - "crates/buzz-relay/src/api/media.rs"
  - statement: "Before `upload_blob` runs, the `AuthenticatedUpload` Axum extractor binds the request to a community from the `Host` header, fails closed with a generic 404 on an unmapped or unresolved host (never a default tenant, never echoing the host), and does this before verifying the Blossom auth event so the auth event's `server` tag is checked against the actual bound tenant host rather than a process-global domain."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/media.rs"
  - statement: "The Blossom (BUD-11) upload authorization event must be Nostr kind 24242, carry a non-empty human-readable `content`, a Schnorr-valid signature, a `t` tag equal to `upload`, and an `expiration` tag whose value is still in the future; its `created_at` must not be more than 5 seconds in the future nor older than the caller-supplied `max_age_secs` window, and if it carries any `server` tag at least one must match the bound tenant host under the shared host-normalization rule."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/src/auth.rs"
  - statement: "The auth event must also carry an `x` tag equal to the uploaded content's SHA-256 hex digest; the extractor separately requires a matching `X-SHA-256` request header (BUD-11 mandates this header) as a well-formed 64-character lowercase-hex string, and rejects the request if the header, the `x` tag, or the actual body hash disagree."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/src/auth.rs"
      - "crates/buzz-relay/src/api/media.rs"
  - statement: "After Blossom auth, the extractor enforces relay membership (NIP-43) for the signer's pubkey against the bound community — the sole upload authority, independent of bearer-token storage and of `require_auth_token`, which governs the unrelated REST API — then applies a per-(community, pubkey) sliding-window rate limit and a two-level concurrency limit (a global semaphore plus a per-pubkey cap) before the handler body runs."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/media.rs"
  - statement: "Defaults for the upload guards are: global concurrent uploads 8 (`BUZZ_MEDIA_MAX_CONCURRENT_UPLOADS`), per-pubkey concurrent uploads 2, capped at the global value (`BUZZ_MEDIA_MAX_CONCURRENT_UPLOADS_PER_PUBKEY`), and 30 uploads per rolling 60-second window per (community, pubkey) (`BUZZ_MEDIA_UPLOADS_PER_MINUTE`)."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/config.rs"
      - "crates/buzz-relay/src/api/media.rs"
  - statement: "Once authenticated, `upload_blob` acquires a durable, heartbeated `ServingWriteGuard` lease (`acquire_serving_write`) scoped to the community before doing any storage write. This lease fences the upload against a whole-community deletion sweep in progress: `verify()` checks the lease before and after the protected operation, and `protect()` races the operation itself against an asynchronous lease-lost signal so an in-flight write is not silently allowed to continue once a deletion sweep has claimed the community."
    entry_class: FACT
    evidence:
      - "crates/buzz-deletion/src/lib.rs"
      - "crates/buzz-relay/src/api/media.rs"
  - statement: "`upload_blob` reads up to 4096 bytes to sniff the real content — never trusting the client's `Content-Type` — and routes MP4/ISO-BMFF-looking bytes to the streaming video pipeline; every other body is buffered (bounded by the larger of the configured image and generic-file byte caps) and then routed to the image pipeline if `infer` recognizes it as JPEG/PNG/GIF/WebP, otherwise to the generic-file pipeline (or rejected with `DisallowedContentType` on the legacy `/media/upload` route, which serves images only)."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/media.rs"
  - statement: "The buffered pipeline (`process_buffered_upload`, shared by the image and generic-file paths) validates content and computes the SHA-256 digest inside `spawn_blocking`, then re-verifies the Blossom `x`-tag/hash match with a 600-second auth window; it derives a content-addressed key `{sha256}.{ext}` and a sidecar metadata key, and short-circuits as an idempotent success only when both the blob object and its sidecar already exist."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/src/upload.rs"
  - statement: "On a fresh (non-idempotent) upload, the blob bytes are written to storage first, then per-file metadata (thumbnail, dimensions, blurhash for images) is prepared; if metadata preparation fails, the already-written blob is intentionally left orphaned rather than deleted, because a concurrent upload of the same content hash could otherwise race a compensating delete against a blob another request is about to reference — orphan cleanup is left to a future background GC job."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/src/upload.rs"
  - statement: "When per-upload-event moderation records are enabled (`BUZZ_MEDIA_UPLOAD_RECORDS`), the moderation upload-event record is written after the blob (and any thumbnail) but before the sidecar; the sidecar is the gate that makes a blob servable at all, so a record-write failure leaves the blob stored but unservable, and — conversely — a moderation record's existence implies its referenced objects exist. On an idempotent short-circuit (no blob PUT), a record is still written so re-uploads of already-known bytes remain visible to moderation."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/src/upload.rs"
      - "crates/buzz-media/src/upload_record.rs"
  - statement: "The video pipeline (`process_video_upload`) never buffers the full body in RAM: it streams the request body to a `tempfile::NamedTempFile` while computing SHA-256 incrementally, verifies the `x`-tag hash match, validates MP4 constraints (H.264/AAC codecs, duration at most 600 seconds, resolution at most 3840x2160, and a fast-start `moov`-before-`mdat` layout), stores the file via a streaming read (`MediaStorage::put_file`), and writes a sidecar carrying `duration_secs` but no thumbnail."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/src/upload.rs"
  - statement: "On success, `upload_blob` rewrites the returned `BlobDescriptor`'s URLs for the request's tenant host, increments an `uploads_total` metric labeled by a bounded MIME set, sends a `MediaUploaded` audit entry over a bounded channel on a best-effort basis (a full or closed channel only logs and increments an error counter — it does not fail the upload), and finally releases the serving-write lease before returning the descriptor as JSON."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/media.rs"
  - statement: "Failure responses are grouped by `MediaError::into_response`: every authentication failure (missing/malformed auth header, bad signature, wrong kind/verb, expired or out-of-window timestamp, hash mismatch, server-tag mismatch, missing required tag, revoked or mismatched token) collapses to a generic 401 to avoid an oracle that would let a caller distinguish failure reasons; `InsufficientScope`, `RelayMembershipRequired`, and `CommunityWriteFenced` are 403; oversized bodies are 413; disallowed or unrecognized content types (including a non-MP4 container or wrong codec) are 415; invalid/non-canonical media (bad image data, video over the duration/resolution/fast-start constraints) is 422; rate-limit and concurrency-limit rejections are 429; a lost serving-write lease and other storage/service failures are mapped to 503 (`ServiceUnavailable`) or, for opaque I/O/storage/internal failures, 500."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/src/error.rs"
  - statement: "A community-deletion fence rejected at lease *acquisition* time (before any body is read) surfaces as `CommunityWriteFenced` (403); a lease lost *during* the protected write surfaces as `ServiceUnavailable` (503), distinguishing an upload that was never permitted from one that was aborted mid-flight."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/media.rs"
  - statement: "Because `ServingWriteGuard::protect` only detects a lease loss that occurs while its inner future is still pending — and, once that future (the blob `put` plus metadata/sidecar writes) resolves on its own, `protect` still re-verifies the lease and can return an error even though the storage side effects already completed durably — a client can receive a 503 for an upload whose blob (and, for a fresh upload, whose sidecar) were nonetheless written to storage. This is a genuine best-effort race, not a two-phase commit: the lease bounds when writes are *permitted to start* and is checked again afterward, but it cannot undo a write already in flight when the lease was lost."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-deletion/src/lib.rs"
      - "crates/buzz-media/src/upload.rs"
    confidence: 0.6
  - statement: "The end-to-end flow is exercised by integration tests asserting: a successful upload/GET round trip with correct `BlobDescriptor` fields and a working thumbnail endpoint; idempotent re-upload returning the same descriptor; 401 for a request with no `Authorization` header; 401 for a request missing the mandatory `X-SHA-256` header; and 401 when the auth event's `x`-tag hash does not match the uploaded body (the test function is misleadingly named `test_upload_hash_mismatch_returns_400` but its own assertion checks status 401, matching `error.rs`'s grouping)."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/e2e_media.rs"
  - statement: "Unit tests on the error-to-status mapping assert, independently of the integration suite, that serving-backend failures map to a 5xx status while the deletion fence itself stays 403, that unsupported media types map to 415, and that invalid or non-canonical media maps to 422."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/src/error.rs"
  - statement: "Per-type upload size caps default to 50 MB for images, 10 MB for animated GIFs, 500 MB for video, and 100 MB for generic files, all configurable via `MediaConfig`."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/src/config.rs"
---

# Flow: media upload (Blossom `PUT /upload`)

How a client uploads a piece of media to a Buzz community's blob store, from the
signed HTTP request to a servable, moderation-visible object — or to one of the
flow's several distinct failure/abort outcomes.

**Authoritative sources this node does not duplicate:** the Blossom/BUD-11
authorization-event shape and header contract live in
`crates/buzz-media/src/auth.rs`; the field-by-field error-to-status mapping lives in
`crates/buzz-media/src/error.rs`; per-deployment size and rate-limit defaults live in
`crates/buzz-media/src/config.rs` and `crates/buzz-relay/src/config.rs`. Read those for
exact values and wire formats; this node describes the flow that connects them.

## Trigger, preconditions, and termination

**Trigger.** An HTTP `PUT` to `/upload` or the legacy `/media/upload` alias, carrying
the request body as the raw file bytes, a Blossom (kind `24242`) authorization event in
the `Authorization` header, and an `X-SHA-256` header naming the claimed content hash.

**Preconditions** (all enforced before the handler body runs, in this order): the
request's `Host` header resolves to a known community; the Blossom auth event is
well-formed, signed, scoped to the `upload` verb, unexpired, freshly created, and (if
`server`-tagged) tagged for the bound host; the `X-SHA-256` header is well-formed and
matches an `x` tag on the auth event; the signer is a member of the bound community's
relay (NIP-43); the signer is under its rate limit; and a global and per-pubkey upload
concurrency permit is available. See *Authentication, authorization, and trust-boundary
crossings* below for what each of these actually establishes.

**Termination — success.** The handler returns HTTP 200 with a JSON `BlobDescriptor`
(URL, SHA-256, size, MIME type, upload timestamp, and format-specific fields such as
image dimensions/blurhash/thumbnail or video duration). The blob is a distinct
independently-maintainable concern once uploaded — how it is later fetched and
re-authenticated on read (`get_blob`/`head_blob` in the same file) is out of scope for
this node.

**Termination — failure/abort.** The handler returns a JSON `{"error": "..."}` body
with one of several HTTP status codes; no partial `BlobDescriptor` is ever returned.
See *Failure, abort, and rollback behavior* below for exactly which failures leave
which storage side effects behind.

## Ordered interactions and data/state movement

1. **Host → tenant binding.** The `AuthenticatedUpload` extractor resolves the request's
   community from its `Host` header. An unmapped host fails closed as a generic 404
   before any other check runs, so an unauthenticated caller cannot use this endpoint to
   enumerate which communities exist on a deployment.
2. **Blossom auth verification**, against the *bound* tenant host (not a process-global
   domain) — signature, kind, verb, expiration, freshness window, and optional
   `server`-tag match.
3. **`X-SHA-256` header check** — well-formed hex, and matches an `x` tag already
   verified against the auth event.
4. **Relay membership gate (NIP-43)** for the signer's pubkey against the bound
   community — the only upload authority; independent of bearer-token/REST auth.
5. **Rate limit and concurrency permits** acquired for the (community, pubkey) pair;
   the extractor returns without reading any request body if any of steps 1–5 reject.
6. **Serving-write lease acquired** (`acquire_serving_write`) for the community, fencing
   the upload against a concurrent whole-community deletion sweep.
7. **Content sniff** (first ≤4096 bytes) selects the video-streaming path or the
   buffered path; the buffered path further selects image vs. generic-file handling by
   sniffing magic bytes, never by the client-declared `Content-Type`.
8. **Hash + auth re-verification** inside the selected pipeline, with a path-appropriate
   freshness window (600s buffered, up to the caller's window for video) — this is a
   second, narrower check than step 2, now bound to the actual computed body hash.
9. **Idempotency check.** If a blob and its sidecar already exist for the computed hash,
   the pipeline short-circuits to a success response (writing a moderation record only,
   when enabled) without re-writing the blob.
10. **Blob write**, then **derived-metadata preparation** (thumbnail/dimensions/blurhash
    for images; MP4 constraint validation for video), then, when enabled, a
    **moderation upload-event record**, then the **sidecar write** — the sidecar is the
    gate that makes the blob fetchable at all.
11. **Response assembly**: descriptor URL rewritten for the tenant host, a metrics
    counter incremented, a best-effort audit entry sent, the serving-write lease
    released, and the descriptor returned.

## Authentication, authorization, and trust-boundary crossings

- **Transport → tenant.** The `Host` header is the only input to community binding;
  binding happens before any body byte is read or any auth event is parsed, and fails
  closed rather than falling back to a default tenant.
- **Client → relay identity (authentication).** The Blossom kind-`24242` event, signed
  by the uploader's Nostr key, is the proof of *who* is asking — verified independently
  of any bearer token or the unrelated `require_auth_token` REST-API gate.
- **Relay identity → community (authorization).** NIP-43 relay membership is the
  separate check for *whether that identity may write* to this community's media
  store; on an open relay (membership disabled) any validly-signed Blossom request is
  admitted, matching the WebSocket door's admission policy.
- **Claimed hash → actual bytes.** The `X-SHA-256` header and the auth event's `x` tag
  are both checked against the auth event at admission time, and the pipeline
  re-derives the hash from the real body and re-checks it before ever writing to
  storage — the client's claim is never trusted past that re-derivation.
- **Serving path → deletion path.** The `ServingWriteGuard` lease is the trust boundary
  between an in-flight upload and a concurrent whole-community deletion sweep; a
  fenced or lost lease is the only way this flow's storage write is interrupted by
  another subsystem.

## Failure, abort, and rollback behavior

There is no transactional rollback of already-written storage objects anywhere in this
flow — every "abort" below describes what response the caller receives and what, if
anything, was left behind in storage:

| Failure point | Client sees | Storage left behind |
|---|---|---|
| Host doesn't resolve to a community | 404 | Nothing written |
| Any Blossom-auth check (signature, kind, verb, expiration, freshness, hash, server tag) | 401 (generic, undifferentiated) | Nothing written |
| Not a relay member | 403 (`RelayMembershipRequired`) | Nothing written |
| Rate or concurrency limit exceeded | 429 | Nothing written |
| Serving-write lease fenced at acquisition (community deletion already claimed) | 403 (`CommunityWriteFenced`) | Nothing written |
| Body too large / disallowed or unrecognized content type / invalid media | 413 / 415 / 422 | Nothing written (rejected before or during buffering, ahead of the storage write) |
| Metadata preparation fails after the blob write (buffered path) | The pipeline's own error status | Blob written, orphaned — no compensating delete, by design, to avoid racing a concurrent idempotent upload of the same hash; left for a future GC sweep |
| Moderation record write fails after the blob (and metadata) write, before the sidecar | The pipeline's own error status | Blob (and thumbnail) written, unservable — the sidecar gate was never reached |
| Serving-write lease lost mid-operation (deletion sweep starts during the write) | 503 (`ServiceUnavailable`) | Possibly a complete, durable write (see the INFERENCE above) — the lease bounds *permission*, not the write itself |

**Representative verification:** `crates/buzz-test-client/tests/e2e_media.rs` exercises
the success round trip, idempotent re-upload, and the 401 family (missing auth, missing
`X-SHA-256`, hash mismatch). `crates/buzz-media/src/error.rs`'s own unit tests assert
the 5xx-vs-403 split for serving-backend/fence failures, and the 415/422 groupings, at
the mapping level independent of a live server.

## Scope and omissions

**This node covers** the write path only: the HTTP contract, the ordered admission
checks, the buffered and streaming storage pipelines, the community-deletion fence, and
the failure/status mapping as it applies to upload.

**Not covered here, and owned elsewhere or by a future node:**

| Not covered | Notes |
|---|---|
| Reading a blob back (`GET`/`HEAD /media/*`) | A distinct, independently authenticated flow (`get_blob`/`head_blob` in the same source file); belongs in its own node if/when one is written. |
| The exact Blossom/BUD-11 wire specification | This node states what Buzz's code enforces and cites the code, not the external BUD-11 text itself, which was not opened for this node. |
| Client-side construction of the auth event (desktop, mobile, CLI) | Not inspected for this node; only the relay-side contract was verified. |
| Background orphan-blob GC | Referenced in a code comment as a "V2" job; no such job was located or verified to exist at this revision. |
| `crates/buzz-test-client/tests/e2e_media_extended.rs` | Named in project documentation as covering "extended media scenarios" but not opened for this node — its assertions are not cited here. |
| Live execution of the flow (a running relay + Postgres/Redis/MinIO) | This node is based on reading source and existing test assertions, not on running the test suite as part of authoring it. |

**Expected but not verified:** whether the "V2 background GC job" mentioned in
`crates/buzz-media/src/upload.rs` for sweeping orphaned blobs actually exists anywhere
in this repository at this revision — a targeted search was not performed, and no such
job is cited above.

**No `relationships` are declared.** At the recorded revision, `origin/launchpad`'s
`launchpad/docs/corpus/` tree (`git ls-tree -r --name-only origin/launchpad --
launchpad/docs/corpus`) contains only `AGENTS.md`, `README.md`, and the `standards/`
governance nodes — no other `architecture` or `flows` node is merged there for this
node to point at, checked directly rather than assumed, per `AGENTS.md`'s "check
before you justify it" rule. (Two sibling `architecture/flows/*` documents exist as
uncommitted work from other in-progress batch tasks at authoring time, but an
unmerged file cannot be a valid `relationships[].target`.) `references` edges to a
media-download node and to `corpus-agents` are the natural first additions once
either exists on `origin/launchpad`.
