---
id: platforms-relay-media-api
type: platforms
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 131b02f989684117d9ab1dd426f1673fa638e523."
    entry_class: FACT
    evidence:
      - "commit 131b02f989684117d9ab1dd426f1673fa638e523"
  - statement: "The relay's app router registers PUT /upload and PUT /media/upload (a legacy alias) on the same handler, upload_blob, and GET/HEAD /media/{sha256_ext} on get_blob/head_blob respectively, all under a media_router merged into the main router with a shared request-body-size layer."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs:39-46"
      - "crates/buzz-relay/src/router.rs:148"
  - statement: "upload_blob, get_blob and head_blob are declared pub async fn in crates/buzz-relay/src/api/media.rs, each taking axum State<Arc<AppState>> plus request-specific extractors (AuthenticatedUpload for upload; HeaderMap and Path<String> for get/head) and returning a Result carrying either a JSON BlobDescriptor (upload) or an axum Response (get/head), or a MediaError."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/media.rs:319-324"
      - "crates/buzz-relay/src/api/media.rs:633-641"
      - "crates/buzz-relay/src/api/media.rs:898-903"
  - statement: "BlobDescriptor (crates/buzz-media/src/types.rs) is documented in its own doc comment as the Blossom BUD-02 response type returned by PUT /upload and the legacy media alias, and carries url, sha256, size, a type field serialized as \"type\", uploaded, plus optional dim, blurhash, thumb and duration fields."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/src/types.rs"
  - statement: "buzz-media is declared a library crate with no Axum dependency for handlers; its own lib.rs doc comment states 'Axum handlers live in buzz-relay', and it publicly re-exports MediaConfig, MediaError, MediaStorage (and related storage types), BlobDescriptor, upload-pipeline functions, UploadRecord types, and validation helpers such as serve_inline and validate_video_file."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/src/lib.rs"
  - statement: "MediaStorage (crates/buzz-media/src/storage.rs) exposes the API surface the relay's media handlers are built on: new, put, put_file, get, get_range, get_stream, head, delete, head_with_metadata, delete_objects, sidecar_key/ctx_sidecar_key, get_sidecar/put_sidecar, read_sidecar_mime, ping, and paginated listing methods (list_page, list_prefix_page, list_prefix_versions_page)."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/src/storage.rs:209-580"
  - statement: "MediaConfig (crates/buzz-media/src/config.rs) carries the S3/MinIO connection fields (s3_endpoint, s3_access_key, s3_secret_key, s3_bucket, s3_region, s3_addressing_style), the per-media-class byte caps (max_image_bytes, max_gif_bytes required; max_video_bytes default 500 MB, max_file_bytes default 100 MB), a public_base_url that MediaConfig::validate requires to end with '/media' and not end with a trailing slash, an upload_records_enabled moderation-record toggle, and two optional trusted-edge-header names (upload_ip_header, upload_port_header) for attribution."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/src/config.rs:48-98"
      - "crates/buzz-media/src/config.rs:100-119"
  - statement: "MediaError (crates/buzz-media/src/error.rs) is a single thiserror enum spanning both authentication/authorization failures (InvalidSignature, InvalidAuthKind, InvalidAuthVerb, MissingTag, HashMismatch, ServerMismatch, TokenExpired, TimestampOutOfWindow, MissingAuth, InvalidAuthScheme, InvalidBase64, InvalidAuthEvent, Unauthorized, InsufficientScope, RelayMembershipRequired, CommunityWriteFenced, TokenRevoked, PubkeyMismatch) and content/operational failures (UnknownContentType, DisallowedContentType, FileTooLarge, ImageTooLarge, InvalidImage, MetadataForbidden, StorageError, Internal, NotFound, ServiceUnavailable, UploadRateLimitExceeded, UploadConcurrencyLimitReached, and codec/duration/resolution variants for video)."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/src/error.rs:1-70"
  - statement: "Four crates declare buzz-media as a Cargo dependency: buzz-relay, buzz-admin, buzz-deletion, and buzz-test-client. Of these, buzz-deletion's src/lib.rs directly references buzz_media:: symbols (sweep_bucket_taxonomy, MediaConfig, MediaStorage, S3AddressingStyle, BulkDeleteOutcome) for its own bucket-taxonomy sweep and test fixtures, and buzz-relay's router/state wire the handlers and construct a MediaStorage instance at startup; no buzz_media:: reference was found anywhere under buzz-admin/src, and buzz-test-client's only buzz_media:: reference is in tests/e2e_git.rs, unrelated to the media API."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/Cargo.toml:66"
      - "crates/buzz-admin/Cargo.toml:23"
      - "crates/buzz-deletion/Cargo.toml"
      - "crates/buzz-test-client/Cargo.toml"
      - "crates/buzz-deletion/src/lib.rs:18"
      - "crates/buzz-deletion/src/lib.rs:480"
      - "crates/buzz-deletion/src/lib.rs:562"
      - "crates/buzz-relay/src/router.rs:581-592"
  - statement: "buzz-cli does not declare buzz-media as a Cargo dependency; instead crates/buzz-cli/src/client.rs's upload_file and download_media methods construct their own Blossom authorization events and issue PUT /upload and GET /media/{sha256_ext} directly over HTTP against the relay, making buzz-cli an API-level consumer of this HTTP surface rather than a crate-level dependent of buzz-media."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/client.rs:1121"
      - "crates/buzz-cli/src/client.rs:1158-1165"
      - "crates/buzz-cli/src/client.rs:275-320"
  - statement: "Desktop rewrites relay-hosted /media/{64-hex-sha256}.{ext} (and .thumb.jpg) URLs to a local Tauri proxy; the module's own doc comment states the reason is that WKWebView's networking stack bypasses the VPN tunnel, so direct <img src> requests to the relay get 403'd by Cloudflare Access, and that external (non-relay) Blossom URLs are deliberately left unrewritten because they are not behind Cloudflare Access."
    entry_class: FACT
    evidence:
      - "desktop/src/shared/lib/mediaUrl.ts:1-31"
  - statement: "architecture-flows-media-upload and architecture-flows-media-download are validated corpus nodes already merged on origin/launchpad (commits 09b0694fd and 560b2d836 respectively) that document, step by step, the Blossom admission-check ordering, the buffered/streaming storage pipelines, and the full error-to-HTTP-status mapping for this same upload_blob/get_blob/head_blob surface; this node does not restate that content."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/flows/media-upload.md"
      - "launchpad/docs/corpus/architecture/flows/media-download.md"
  - statement: "architecture-containers-relay, also already merged on origin/launchpad, names PUT/GET/HEAD /media/* as one row of the relay container's inbound-route table but explicitly defers 'the internal shape and behavior of each connected subsystem crate (... buzz-media)' to that subsystem's own future node -- this node is that deferred subsystem-level detail for buzz-media's HTTP surface."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/containers/relay.md"
  - statement: "Because buzz-cli's client.rs builds and signs Blossom authorization events itself and calls the HTTP routes directly, while only buzz-deletion and buzz-relay actually use buzz-media's Rust API, this media API's real consumer boundary is the HTTP contract (routes, BlobDescriptor, status codes) rather than the buzz-media crate's Rust type signatures -- which is why this node documents the HTTP surface as the public interface, and treats the Rust MediaStorage/MediaConfig/MediaError types as supporting implementation detail rather than the contract itself."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-cli/src/client.rs:1121"
      - "crates/buzz-deletion/src/lib.rs:18"
      - "crates/buzz-relay/src/router.rs:39-46"
    confidence: 0.75
relationships:
  - type: references
    target: architecture-flows-media-upload
  - type: references
    target: architecture-flows-media-download
  - type: references
    target: architecture-containers-relay
---

# Media API (relay platform surface)

The relay's Blossom-compatible HTTP media API: the content-addressed blob
upload/download surface exposed at `/upload`, `/media/upload` (legacy alias)
and `/media/{sha256_ext}`. This node answers what this surface *is* — its
responsibility, its wire-level contract, and its real dependency edges — as
one independently maintainable platform-level component of the relay. It does
not restate how a request moves through that contract step by step; two
already-merged flow nodes own that.

## Responsibility

The media API is the relay's implementation of a Blossom-compatible
(BUD-02/BUD-11-shaped) blob store: clients `PUT` a file and get back a
content-addressed `BlobDescriptor`; clients `GET`/`HEAD` a previously uploaded
blob by its SHA-256 hash. All three routes are served by handlers in
`crates/buzz-relay/src/api/media.rs` (`upload_blob`, `get_blob`, `head_blob`),
backed by the `buzz-media` library crate, which owns storage, validation,
Blossom-auth verification and thumbnail/metadata generation but — per its own
doc comment — deliberately holds no Axum handlers itself; those live in
`buzz-relay`. This mirrors the `buzz-relay` container node's own description
of the relay as the crate that orchestrates subsystem crates that never call
each other directly.

## Public interface

| Method | Path | Handler | Purpose |
|---|---|---|---|
| PUT | `/upload` | `upload_blob` | Upload a blob (canonical Blossom route) |
| PUT | `/media/upload` | `upload_blob` | Legacy alias for upload, same handler |
| GET | `/media/{sha256_ext}` | `get_blob` | Download a blob (full or ranged) |
| HEAD | `/media/{sha256_ext}` | `head_blob` | Fetch blob headers only |

All three handlers are `pub async fn` taking Axum's `State<Arc<AppState>>`
plus request-specific extractors, and return either a JSON `BlobDescriptor`
(upload) or a raw `Response` (get/head), or a `MediaError`.

**Response type — `BlobDescriptor`** (`crates/buzz-media/src/types.rs`), the
BUD-02 shape returned by both upload routes:

| Field | Type | Notes |
|---|---|---|
| `url` | `String` | Full URL to the blob |
| `sha256` | `String` | 64-char hex hash |
| `size` | `u64` | Bytes |
| `type` | `String` | MIME type (serialized as `"type"`) |
| `uploaded` | `i64` | Unix timestamp |
| `dim` | `Option<String>` | `"WxH"`, images only |
| `blurhash` | `Option<String>` | Images only |
| `thumb` | `Option<String>` | Thumbnail URL, images only |
| `duration` | `Option<f64>` | Seconds, video only |

**Errors — `MediaError`** (`crates/buzz-media/src/error.rs`) is one enum
spanning both authentication/authorization failures (bad signature, wrong
auth kind/verb, missing tag, hash/server mismatch, expired/out-of-window
timestamp, missing/malformed auth header, revoked/mismatched token,
insufficient scope, not a relay member, community writes fenced) and
content/operational failures (unknown/disallowed content type, file/image too
large, invalid image, storage error, internal error, not found, service
unavailable, rate/concurrency limit exceeded, and video codec/duration/
resolution violations). The exact status-code each variant maps to, and why,
is the already-merged flow nodes' subject (see *Relationships*) — this node
names the variant surface, not the mapping.

## Dependencies

**Depends on** (this surface requires these to exist and be correct):

| Component | Why | Evidence |
|---|---|---|
| `buzz-media` crate | Owns `MediaStorage` (S3/MinIO client), `MediaConfig`, `MediaError`, Blossom-auth verification (`auth.rs`), and the upload/validation pipeline the handlers call into | `crates/buzz-relay/Cargo.toml:66`; `crates/buzz-media/src/lib.rs` |
| `buzz-deletion` crate | Provides the serving-write lease (`acquire_serving_write`) `upload_blob` takes before any storage write, fencing uploads against a concurrent whole-community deletion sweep | `crates/buzz-relay/src/api/media.rs:327-330` |
| S3-compatible object storage (S3/MinIO) | `MediaStorage` is a thin client over an S3-compatible bucket; connection fields (`s3_endpoint`, `s3_access_key`, `s3_secret_key`, `s3_bucket`, `s3_region`, `s3_addressing_style`) are required `MediaConfig` fields | `crates/buzz-media/src/config.rs:48-69`; `crates/buzz-media/src/storage.rs:1-16` |

**Depended on by** (these call this surface):

| Component | Why | Evidence |
|---|---|---|
| `buzz-relay` router/state | Registers the three routes and constructs the `MediaStorage` instance held in `AppState` at startup | `crates/buzz-relay/src/router.rs:39-46`, `:148`, `:581-592` |
| `buzz-deletion` | Uses `buzz_media::{MediaConfig, MediaStorage, S3AddressingStyle, BulkDeleteOutcome}` and `sweep_bucket_taxonomy` for its own bucket-taxonomy sweep, a crate-level (not HTTP) dependent | `crates/buzz-deletion/src/lib.rs:18,480,562` |
| `buzz-cli` (`client.rs`) | Signs its own Blossom auth events and calls `PUT /upload` / `GET /media/{sha256_ext}` directly over HTTP — an **API-level**, not crate-level, consumer | `crates/buzz-cli/src/client.rs:1121,1158-1165,275-320` |
| Desktop (`mediaUrl.ts`) | Rewrites relay-hosted `/media/*` URLs to a local Tauri proxy, because WKWebView's networking bypasses the VPN tunnel and direct `<img src>` fetches get 403'd by Cloudflare Access; external (non-relay) Blossom URLs are left unrewritten | `desktop/src/shared/lib/mediaUrl.ts:1-31` |

`buzz-admin` declares `buzz-media` as a Cargo dependency
(`crates/buzz-admin/Cargo.toml:23`) but no `buzz_media::` reference was found
anywhere under `crates/buzz-admin/src` at this revision — recorded in *Scope
and omissions* as unconfirmed rather than asserted either way.

## Boundary

This node does not describe:
- **The ordered admission-check sequence** for either upload or download
  (host→tenant binding, Blossom-auth verification, relay-membership,
  rate/concurrency limits, the serving-write lease) — `architecture-flows-media-upload`
  and `architecture-flows-media-download` already document this in full, per
  request, with the exact ordering and trust-boundary crossings.
- **The exact `MediaError` → HTTP-status mapping** — the same two flow nodes
  already state which variant maps to which status and why (e.g. the
  deliberate collapse of every auth failure to a generic 401 to avoid an
  authentication oracle).
- **The buffered vs. streaming storage-pipeline internals** (content
  sniffing, idempotency short-circuit, thumbnail/blurhash generation, MP4
  validation) — owned by the upload flow node, citing `crates/buzz-media/src/upload.rs`.
- **The relay container's full inbound/outbound surface** — `/media/*` is one
  row of `architecture-containers-relay`'s route table; this node is the
  deferred subsystem-level detail for that one row, not a restatement of the
  container's other routes, listeners, or connected systems.
- **Mobile's own media-API call site** — not inspected for this node; the
  relay-side contract it must satisfy is unchanged regardless, since it is
  defined server-side.

## Relationships

- **references** `architecture-flows-media-upload` — the ordered, per-request
  upload admission/pipeline/failure detail this node defers to.
- **references** `architecture-flows-media-download` — the same, for
  download (`get_blob`/`head_blob`).
- **references** `architecture-containers-relay` — the relay container node
  whose route table names this surface as one row and explicitly defers its
  detail here.

All three targets were confirmed present on `origin/launchpad` at the
recorded revision (their front matter `id` fields read directly, not
assumed), per `AGENTS.md`'s rule that a relationship target must resolve
against the branch being merged into.

## Scope and omissions

**This node covers** the media API's responsibility, its HTTP route/response/
error-variant contract, and its real dependency edges in both directions —
crate-level (`buzz-media`, `buzz-deletion`) and API-level (`buzz-cli`,
desktop) — as one standalone, non-duplicative platform-level document.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Per-request admission-check ordering, trust boundaries, and failure/rollback behavior for upload | `architecture-flows-media-upload` |
| Same, for download (`get_blob`/`head_blob`) | `architecture-flows-media-download` |
| The relay container's full inbound/outbound surface beyond this one route group | `architecture-containers-relay` |
| Mobile's own media-API call site | Not yet documented anywhere in the corpus |
| The external BUD-02/BUD-11 Blossom specification text itself | Not opened for this node; this node and its referenced flow nodes state what Buzz's code enforces, not the spec prose |

**Expected but not verified when this node was written:**
- **Whether `buzz-admin`'s declared `buzz-media` Cargo dependency is genuinely
  unused, or reached indirectly** (for example, via a type surfaced in a
  function signature that a plain `buzz_media::` text grep would miss) — a
  targeted build-graph or `cargo tree`-style check was not run; the claim
  above is limited to what a source grep at this revision showed.
- **Whether `buzz-cli`'s HTTP-level media calls (`client.rs`) are exercised by
  any integration test independent of the relay-side `e2e_media.rs` suite** —
  not checked; the relay-side test coverage is the existing flow nodes'
  subject, not this one's.
