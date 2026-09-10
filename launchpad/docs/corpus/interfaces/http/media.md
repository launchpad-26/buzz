---
id: interfaces-http-media
type: interfaces-events
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 650354eab8d41ab6ce1a71de079a6c6d95c69052."
    entry_class: FACT
    evidence:
      - "commit 650354eab8d41ab6ce1a71de079a6c6d95c69052"
  - statement: "The relay registers exactly four Blossom-compatible HTTP routes for media -- PUT /upload, PUT /media/upload (a legacy alias), GET /media/{sha256_ext}, and HEAD /media/{sha256_ext} -- all under a dedicated media_router with a request-body-size limit layer, and all handled by upload_blob, get_blob and head_blob in the relay's media API module."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs:34-47"
      - "crates/buzz-relay/src/api/media.rs:1-8"
  - statement: "Kind 24242, the Blossom authorization event kind these routes require in every request's Authorization header, is registered in this repository's central Nostr kind registry as KIND_BLOSSOM_AUTH -- not invented ad hoc by the media crate."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs:79"
  - statement: "Before the upload handler body runs, the AuthenticatedUpload Axum extractor binds the request to a community from the Host header (failing closed with a generic 404 on an unmapped host, before any body byte is read or auth event parsed), then requires an Authorization: Nostr <base64(kind:24242 event)> header and a well-formed 64-character lowercase-hex X-SHA-256 header whose value matches an x tag on that auth event, verifies the auth event's Schnorr signature/kind/upload verb/expiration/freshness window (and, if server-tagged, a match against the bound tenant host), then enforces NIP-43 relay membership for the signer's pubkey, and finally applies a per-(community, pubkey) rate limit and a two-level (global plus per-pubkey) concurrency limit."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/media.rs:140-238"
      - "crates/buzz-media/src/auth.rs:31-141"
  - statement: "upload_blob reads up to 4096 bytes to sniff the real content -- never trusting the client-declared Content-Type -- and routes MP4/ISO-BMFF-looking bytes to a streaming video pipeline that never buffers the full body in RAM; every other body is buffered (bounded by the larger of the configured image and generic-file byte caps) and routed to the image pipeline if infer recognizes JPEG/PNG/GIF/WebP, otherwise to the generic-file pipeline, or rejected with 415 DisallowedContentType on the legacy /media/upload route, which accepts images only."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/media.rs:336-424"
  - statement: "The buffered upload pipeline (process_buffered_upload) computes the SHA-256 digest inside spawn_blocking, re-verifies the Blossom auth event's x-tag/hash match with a 600-second freshness window, derives a content-addressed storage key {sha256}.{ext}, and short-circuits to a success response -- without writing the blob again -- only when both the blob object and its sidecar metadata already exist for that hash; a moderation upload-event record is still written on this idempotent path when per-event records are enabled, so a re-upload of known bytes stays visible to moderation."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/src/upload.rs:54-121"
  - statement: "On success, the handler returns a JSON BlobDescriptor: url, sha256 (hex), size (bytes), type (MIME, serialized as \"type\"), uploaded (unix timestamp), and, when applicable, dim (\"WxH\"), blurhash, thumb (URL) and duration (seconds, video only)."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/src/types.rs:6-31"
  - statement: "Per-type upload size caps default to 50 MB for images, 10 MB for animated GIFs, 500 MB for video and 100 MB for generic files; upload concurrency defaults to 8 global and 2 per-pubkey (capped at the global value); the upload rate limit defaults to 30 uploads per rolling 60-second window per (community, pubkey) -- all overridable via BUZZ_MAX_IMAGE_BYTES / BUZZ_MAX_GIF_BYTES / BUZZ_MAX_VIDEO_BYTES / BUZZ_MAX_FILE_BYTES / BUZZ_MEDIA_MAX_CONCURRENT_UPLOADS / BUZZ_MEDIA_MAX_CONCURRENT_UPLOADS_PER_PUBKEY / BUZZ_MEDIA_UPLOADS_PER_MINUTE."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/config.rs:850-901"
  - statement: "Every read (GET and HEAD) requires its own Blossom kind:24242 \"get\" authorization event: verify_blossom_get_auth accepts either blob-scoped authorization (an x tag matching the requested sha256) or server-scoped authorization (a server tag matching the bound tenant host), after which the signer's relay membership (NIP-43) is enforced separately -- there is no configuration flag that allows an unauthenticated read through."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/src/auth.rs:207-239"
      - "crates/buzz-relay/src/api/media.rs:513-548"
  - statement: "validate_media_path restricts every requested {sha256_ext} path segment to one of exactly three shapes -- a bare 64-character lowercase-hex SHA-256, {sha256}.{ext}, or {sha256}.thumb.jpg (thumbnails are always JPEG) -- rejecting anything else (including path traversal, uppercase hex, or a compound extension like .tar.gz) as MediaError::NotFound before any storage lookup runs; the served Content-Type is derived only from the stored, validated sidecar metadata, never from raw storage-backend metadata or the client-requested extension, and a requested extension that disagrees with the sidecar's canonical extension is also rejected as NotFound."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/media.rs:566-698"
  - statement: "GET /media/{sha256_ext} supports HTTP range requests per RFC 9110 SS14.2: no Range header returns 200 with the full body; a satisfiable Range: bytes=... returns 206 with a Content-Range header, capped at 16 MiB per response chunk; an unsatisfiable range (start >= total) returns 416 with Content-Range: bytes */TOTAL; a multi-range request is not supported and is served as a full 200 response instead."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/media.rs:611-781"
  - statement: "Images and video render with Content-Disposition: inline; every other served content type (including HTML, which is deliberately accepted but never rendered) is forced to Content-Disposition: attachment, and every media response carries X-Content-Type-Options: nosniff and a restrictive Content-Security-Policy -- the combined defence against a stored file ever executing as active content in a client."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/media.rs:687-730"
  - statement: "MediaError::into_response groups every failure into one of: 401 for the whole authentication family (missing/malformed auth header, bad signature, wrong kind/verb, expired or out-of-window timestamp, hash mismatch, server-tag mismatch, missing required tag) collapsed to a single generic message to avoid an oracle that would let a caller distinguish failure reasons; 403 for InsufficientScope, RelayMembershipRequired and CommunityWriteFenced; 404 for NotFound; 413 for FileTooLarge/ImageTooLarge; 415 for DisallowedContentType/UnknownContentType/UnsupportedContainer/WrongCodec; 422 for InvalidImage/InvalidVideo/MetadataForbidden/MoovNotAtFront/DurationTooLong/ResolutionTooHigh; 429 for UploadRateLimitExceeded/UploadConcurrencyLimitReached; 503 for ServiceUnavailable; and 500 for Io/StorageError/Internal."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/src/error.rs:112-170"
  - statement: "Unit tests directly on the error-to-status mapping assert independently of a live server: serving-backend failures (ServiceUnavailable, Internal, StorageError) map to a 5xx status while CommunityWriteFenced stays 403; UnknownContentType/DisallowedContentType/UnsupportedContainer/WrongCodec map to 415; and InvalidImage/InvalidVideo/MetadataForbidden/MoovNotAtFront/DurationTooLong/ResolutionTooHigh map to 422."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/src/error.rs:176-222"
  - statement: "crates/buzz-test-client/tests/e2e_media.rs contains, among others, test_upload_and_get (successful upload/GET round trip), test_upload_idempotent (re-upload of identical bytes), test_upload_no_auth_returns_401 (missing Authorization header), test_upload_missing_x_sha256_returns_401 (missing X-SHA-256 header), test_upload_hash_mismatch_returns_400 (a misleadingly named test whose own assertion checks HTTP 401, matching the error.rs grouping above, not 400), test_get_nonexistent_returns_404, test_unauthenticated_reads_are_rejected, and test_upload_real_image."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/e2e_media.rs"
  - statement: "Root AGENTS.md's PR-screenshot workflow instructs agents to never use `buzz upload`, the relay media endpoint, or any third-party image host for PR screenshots, because relay media URLs fail through GitHub's camo proxy, and to use scripts/post-screenshots.sh instead."
    entry_class: FACT
    evidence:
      - "AGENTS.md:265-267"
  - statement: "https://github.com/hzrd149/blossom is the canonical Blossom Upgrade Document (BUD) specification repository (BUD-00 through BUD-12 at the time this node was checked), and its own content confirms BUD-01 covers server requirements and blob retrieval, BUD-02 covers blob upload and management, and BUD-11 specifies Nostr-key-based authorization -- matching the BUD numbers this repository's own code comments cite for the routes documented here."
    entry_class: FACT
    evidence:
      - "https://github.com/hzrd149/blossom"
      - "crates/buzz-relay/src/api/media.rs:1-8"
      - "crates/buzz-media/src/auth.rs:1"
relationships:
  - type: references
    target: architecture-flows-media-upload
  - type: references
    target: architecture-flows-media-download
---

# HTTP media (Blossom): interface

The Buzz relay's Blossom-compatible HTTP media surface -- the boundary across which a
client (desktop, mobile, CLI, or any third-party Blossom-aware tool) and the relay
exchange binary blobs and their metadata. The client authenticates every request with a
signed Nostr kind:24242 authorization event (Blossom's BUD-11 convention) carried in the
`Authorization` header; the relay responds with either a JSON `BlobDescriptor` (uploads)
or the raw blob bytes with standard HTTP caching/range headers (downloads). This is HTTP
+ JSON/binary, not a WebSocket or Nostr-relayed event exchange -- media bytes are never
routed through NIP-01/NIP-29 event storage.

## Operations

| Operation | Defined in | Summary |
|---|---|---|
| `PUT /upload` | `crates/buzz-relay/src/api/media.rs::upload_blob`, registered in `crates/buzz-relay/src/router.rs` | BUD-02 exact-byte upload. Authenticated via Blossom kind:24242 + `X-SHA-256`; accepts images, generic files, and MP4/ISO-BMFF video (streamed); returns a `BlobDescriptor`. |
| `PUT /media/upload` | Same handler, `UploadRouteMode::LegacyMedia` in `crates/buzz-relay/src/api/media.rs` | Temporary legacy alias for the same handler, restricted to images only -- any other sniffed content type is rejected with 415. |
| `GET /media/{sha256_ext}` | `crates/buzz-relay/src/api/media.rs::get_blob` | BUD-01 blob retrieval, with HTTP range-request support (RFC 9110 §14.2). |
| `HEAD /media/{sha256_ext}` | `crates/buzz-relay/src/api/media.rs::head_blob` | BUD-01 existence check: same authentication and sidecar-derived headers as GET, no body. |

## Contract and stability

- **Authentication is per-request, not session-based.** Every operation (upload and
  read alike) requires its own freshly signed Blossom kind:24242 event in the
  `Authorization` header, scoped to the correct verb (`upload` or `get`) and an
  `expiration` tag still in the future. There is no bearer-token or cookie-session
  alternative for this surface, and no configuration disables authentication for reads.
- **Authorization is two independent gates.** The Blossom auth event establishes *who*
  is asking (a Nostr keypair); NIP-43 relay membership, checked separately, establishes
  *whether that identity may use this community's media store*. An open relay (relay
  membership disabled) admits any validly signed Blossom request, matching the
  WebSocket door's admission policy.
- **Idempotency.** Uploading bytes whose SHA-256 already has both a stored blob and a
  published sidecar in this community short-circuits to a success response without a
  second storage write -- the same `BlobDescriptor` is returned. This is the interface's
  only idempotency guarantee; there is no other request-level idempotency key.
- **Ordering.** Within a single upload, the storage write always precedes the sidecar
  write, and the sidecar's existence is what makes a blob servable at all -- so a
  concurrent `GET` for a hash that is mid-upload will see `404 NotFound`, never a
  partially written blob. There is no ordering guarantee *across* separate uploads.
- **Versioning/compatibility.** The interface has no version header or negotiated
  protocol version; compatibility is expressed as route aliasing (`/media/upload` is
  explicitly marked a *temporary* legacy alias of `/upload` in the handler's own doc
  comment) rather than a versioned path or header. There is no deprecation timeline
  recorded in code for the legacy alias.
- **Error/rejection behavior.** See the status-code taxonomy in the evidence ledger
  above (`crates/buzz-media/src/error.rs`), which a caller may rely on: every
  authentication failure is collapsed to a generic 401 specifically to prevent an
  oracle that would let a caller distinguish *why* auth failed; 403 is reserved for
  authorization (membership/community-fence) failures once identity is established;
  413/415/422 distinguish size, content-type and content-validity rejections; 429 is
  rate/concurrency limiting; 503/500 are storage/service failures.
- **Size and rate limits are part of the contract, not incidental.** A caller may rely
  on the documented per-type size caps and per-(community, pubkey) rate/concurrency
  limits being enforced (values and env-var overrides in the evidence ledger above);
  exceeding them is a defined 413/429 outcome, not an unspecified failure.

## Boundary

This node does not describe:
- **Kind 24242's own wire contract** (tag shape, `t`/`x`/`expiration`/`server` tag
  semantics in full) beyond what this interface's contract needs -- that is an
  event-kind-shaped concern (`#1337`'s template, per `templates/interface.md`), and no
  such node exists yet in the merged corpus for this interface node to `references`.
  `crates/buzz-media/src/auth.rs` is the authoritative source for that wire contract
  today.
- **A field-by-field, domain-expert-depth parameter catalogue** of every request/response
  field -- see `templates/interface.md`'s own boundary against `#1346`/`#1532`
  (reference / API-Reference depth), which this node does not attempt.
- **The Blossom BUD-01/BUD-02/BUD-11 specification text itself.** This node states what
  Buzz's code enforces and cites that code, plus a confirmation that the cited BUD
  numbers exist and mean what the code's comments say in the canonical spec repository
  (`https://github.com/hzrd149/blossom`) -- it does not reproduce or paraphrase the BUD
  documents' own normative text.
- **Reading a blob back as a *separate* concern from uploading it.** Both are covered
  here (this is one interface, not two), but the step-by-step mechanics of each --
  including failure/rollback behavior at each stage -- are described at length in the
  two linked flow nodes, not repeated here.
- **Client-side construction of the auth event** (desktop, mobile, CLI, or third-party
  tooling) -- only the relay-side contract is in scope.

## Relationships

- `references`: `architecture-flows-media-upload` -- the ordered, step-by-step upload
  flow (admission checks, buffered/video pipelines, failure/rollback behavior per
  failure point) that this node's Contract-and-stability section summarizes at
  interface altitude.
- `references`: `architecture-flows-media-download` -- the equivalent step-by-step
  download/read flow.
- No `implements: corpus-template-interface` self-link is declared. `templates/interface.md`
  itself states that whether a node built from it should add that optional self-link is
  unsettled corpus-wide (its own "Expected but not verified" section); this node leaves
  it undeclared rather than picking a side of an open question the template does not
  resolve.
- Every declared target above was checked against `origin/launchpad`'s own corpus tree
  (`git ls-tree -r --name-only HEAD -- launchpad/docs/corpus`) at this node's recorded
  revision, not against an unmerged branch.

## Examples

**Valid flow (upload then read).** `crates/buzz-test-client/tests/e2e_media.rs::test_upload_and_get`
signs a Blossom `upload` auth event, `PUT`s a small file to `/upload` with a matching
`X-SHA-256` header, asserts a `200` response with a well-formed `BlobDescriptor`, then
signs a Blossom `get` auth event and asserts the blob is retrievable at the descriptor's
URL. `test_upload_idempotent` re-runs the same upload and asserts the second response is
the same success without a duplicate storage write (per the idempotency contract above).

**Failure example (missing authentication).** `test_upload_no_auth_returns_401` `PUT`s to
`/upload` with no `Authorization` header and asserts `401` -- the generic,
undifferentiated authentication-family status this node's Contract section states as a
deliberate anti-oracle design choice, not an accidental omission of a more specific code.

## Scope and omissions

**This node covers** the Blossom-compatible HTTP media interface's boundary: its four
operations, the authentication/authorization model shared by all of them, the
idempotency and ordering guarantees a caller may rely on, the versioning/compatibility
posture (route aliasing, no version header), the full error/status-code taxonomy, and a
link to the authoritative external Blossom BUD-01/02/11 specification.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Kind 24242's own tag-by-tag wire contract | An event-kind node, if/when one is drafted from `#1337`'s template; today, `crates/buzz-media/src/auth.rs` directly |
| Step-by-step upload/download mechanics, including per-failure-point storage rollback behavior | `architecture-flows-media-upload` and `architecture-flows-media-download` (both merged, both `references`d above) |
| Field-by-field, domain-expert-depth request/response parameter cataloguing | `#1346`/`#1532`'s undecided reference/API-Reference scope |
| Client-side construction of the auth event (desktop, mobile, CLI) | Not inspected for this node |
| The BUD-01/02/11 specification's own normative text | `https://github.com/hzrd149/blossom` directly |

**Expected but not verified when this node was written:**
- Whether any deprecation timeline exists (outside code) for the `/media/upload` legacy
  alias was not searched for beyond the handler's own "temporary" doc comment.
- Whether a background orphan-blob GC job (mentioned as a "V2" TODO in
  `crates/buzz-media/src/upload.rs`) exists anywhere in this repository was not checked
  for this node -- it is out of scope for an interface-contract node and is named in
  `architecture-flows-media-upload`'s own scope-and-omissions section instead.
- `crates/buzz-test-client/tests/e2e_media_extended.rs` and
  `crates/buzz-test-client/tests/e2e_media_video.rs` were located by directory listing
  but not opened or cited for this node; their assertions are not represented above.
