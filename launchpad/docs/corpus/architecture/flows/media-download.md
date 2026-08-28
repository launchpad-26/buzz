---
id: architecture-flows-media-download
type: architecture
status: draft
origin: launchpad
audiences:
  - agent
  - developer
evidence:
  - statement: "This node was authored and checked against repository revision a44cf52fc740ebebbdd671427480d14f0bce0115."
    entry_class: FACT
    evidence:
      - "commit a44cf52fc740ebebbdd671427480d14f0bce0115"
  - statement: "GET /media/{sha256_ext} and HEAD /media/{sha256_ext} are the two HTTP routes that serve a downloaded blob, and both are handled by get_blob and head_blob in the relay's media API."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/media.rs"
  - statement: "The media router registers GET and HEAD on the same /media/{sha256_ext} path, alongside PUT /media/upload and /upload for uploads, and applies a request-body-size layer that download requests do not need but share the router with."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs"
  - statement: "validate_media_path restricts the requested path to 1-3 dot-separated segments: a bare 64-character lowercase-hex sha256, {sha256}.{ext}, or {sha256}.thumb.jpg, rejecting anything else as MediaError::NotFound before any other processing runs."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/media.rs"
  - statement: "Every read (GET and HEAD) requires a Blossom authorization event; there is no configuration flag that allows an unauthenticated read through, and a bare unauthenticated request against a never-uploaded hash returns 401, not 404, proving auth is checked before storage existence."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/media.rs"
      - "crates/buzz-test-client/tests/e2e_media.rs"
  - statement: "authenticate_media_read performs three checks in order: bind_media_read_tenant resolves the request's Host header to a TenantContext (or NotFound if the host does not resolve to a known community), extract_blossom_auth plus verify_blossom_get_auth validate the Blossom NIP-24242 event, and enforce_relay_membership checks the authenticated pubkey against the resolved community's membership."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/media.rs"
  - statement: "extract_blossom_auth reads the Authorization header, requires a 'Nostr ' scheme prefix, base64-decodes the remainder (URL-safe-no-pad first, then standard as a fallback), and parses the result as a signed Nostr event, failing with distinct MediaError variants (MissingAuth, InvalidAuthScheme, InvalidBase64, InvalidAuthEvent) at each step."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/media.rs"
  - statement: "verify_blossom_auth_event_for_verb verifies the event's Schnorr signature, requires kind 24242 with a non-empty content string, requires a 't' tag matching the verb ('get'), requires an 'expiration' tag in the future, requires created_at to be no more than 5 seconds in the future and no older than max_age_secs (3600 for reads), and if any 'server' tags are present requires one to match the request's bound tenant host under host-normalization rules, failing closed if the host is unknown."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/src/auth.rs"
  - statement: "verify_blossom_get_auth additionally requires the event to carry either an 'x' tag matching the requested sha256 or a matching 'server' tag; an event lacking both is rejected with MediaError::InsufficientScope."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/src/auth.rs"
  - statement: "enforce_relay_membership returns Ok(None) unconditionally on an open relay (require_relay_membership = false) or for a direct member of a closed relay, returns Ok(Some(owner_pubkey)) when the caller is an unregistered NIP-OA agent whose delegating owner is a member, and otherwise returns a 403 relay_membership_required error before any blob I/O occurs."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/mod.rs"
  - statement: "After authentication, serve_blob_for_tenant re-validates the path, then reads a per-blob sidecar record (read_sidecar_mime / get_sidecar) as the authoritative content-type source before any storage read; for a bare-hash request the sidecar's own extension is used, and for an explicit {sha}.{ext} request the requested extension must match the sidecar's canonical extension or the request is rejected as MediaError::NotFound. For {sha}.thumb.jpg the same sidecar gate runs against the parent hash and the content type is fixed to image/jpeg."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/media.rs"
  - statement: "The storage key served to the client is only ever the tenant-scoped sha256 plus the sidecar's own recorded extension (resolve_s3_key falls back to the sidecar's ext when the request used a bare hash), never a client-supplied extension, so the sidecar -- not the request path -- is authoritative for what gets served."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/media.rs"
  - statement: "serve_blob_for_tenant chooses a Content-Disposition of inline for content types buzz_media::serve_inline() allows and attachment for everything else, and always sets Content-Security-Policy: default-src 'none' and X-Content-Type-Options: nosniff on the response, as the documented primary defence against an uploaded file executing or rendering as active content in the client."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/media.rs"
  - statement: "A request with no Range header, or a Range header containing a comma (multi-range), is served as a full 200 OK response streamed from storage via get_stream, so the full blob is never buffered into relay memory; a single-range request is parsed by parse_byte_range and served as 206 Partial Content via get_range, capped per chunk at MAX_RANGE_CHUNK bytes even when the client asks for more."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/media.rs"
  - statement: "A parseable range whose start is at or beyond the blob's total size, or an unparseable Range header value, is answered with 416 Range Not Satisfiable and a Content-Range: bytes */{total} header rather than an error body."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/media.rs"
      - "crates/buzz-test-client/tests/e2e_media_video.rs"
  - statement: "head_blob runs the identical tenant-bind, Blossom-auth and sidecar-content-type gate as get_blob, then returns headers only (content-type, content-length, accept-ranges, cache-control) via head_with_metadata, or a bare 404 status if no metadata is found for the resolved key -- it never returns a MediaError::NotFound body for the final metadata-lookup miss, unlike every earlier gate in the same function."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/media.rs"
  - statement: "MediaError::into_response maps every authentication failure variant (MissingAuth, InvalidAuthScheme, InvalidBase64, InvalidAuthEvent, InvalidSignature, InvalidAuthKind, InvalidAuthVerb, TokenExpired, TimestampOutOfWindow, Unauthorized, TokenRevoked, PubkeyMismatch, HashMismatch, ServerMismatch, MissingTag) to the same generic 401 with the same body ('authentication failed'), by explicit design, to prevent an attacker from using the response to distinguish which check failed (an authentication oracle)."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/src/error.rs"
  - statement: "MediaError::InsufficientScope maps to 403 (a distinct status from the 401 authentication group) because it is documented as an authorization rather than authentication failure -- it is only reachable once a valid signed identity is already established, so distinguishing it does not create an authentication oracle."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/src/error.rs"
  - statement: "MediaError::NotFound maps to 404, MediaError::RelayMembershipRequired and MediaError::CommunityWriteFenced map to 403, and MediaError::Io / MediaError::StorageError / MediaError::Internal map to 500 with a generic 'internal error' body while logging the real error server-side via tracing::error!."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/src/error.rs"
  - statement: "Successful blob responses set Cache-Control: private, max-age=31536000, immutable, reflecting that a content-addressed blob (keyed by its own sha256) never changes once stored."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/media.rs"
  - statement: "e2e_media.rs and e2e_media_video.rs exercise this flow end to end: successful GET after upload with byte-for-byte comparison, 404 for an authenticated request against a never-uploaded hash, 401 for a wholly unauthenticated read, and 206/416 range behavior against a video blob."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/e2e_media.rs"
      - "crates/buzz-test-client/tests/e2e_media_video.rs"
  - statement: "On desktop, a relay-origin media URL embedded in message content is not fetched directly by the renderer; desktop/src/shared/lib/mediaUrl.ts rewrites it to a local Tauri-backed proxy URL, implying the signed Blossom Authorization header for the actual relay request is attached by the native side rather than by the web renderer, though this node does not verify how that header is constructed."
    entry_class: INFERENCE
    evidence:
      - "desktop/src/shared/lib/mediaUrl.ts"
    confidence: 0.6
---

# Media download flow

How a client retrieves a previously uploaded blob (image, video, or other file) from
the Buzz relay's Blossom-compatible media endpoint, and how the relay authenticates,
authorizes, and serves that request.

## Scope

This node documents the relay-side `GET`/`HEAD /media/{sha256_ext}` contract — the
canonical, client-agnostic definition of the flow — plus the desktop client's known
entry point into it. It does not document the upload flow (`PUT /media/upload`,
`upload_blob`), which is a distinct flow and, if it needs its own node, is a separate
task. It does not attempt to fully document mobile or CLI download call sites; only the
desktop rewrite in `mediaUrl.ts` was inspected, and that inspection is recorded as an
`INFERENCE`, not a `FACT` — see *Not verified* below.

## Trigger

A client already holds a content hash (a `sha256`) for a blob it wants — typically
extracted from an `imeta` tag on a Nostr message event, or from a previously received
`BlobDescriptor` returned by an earlier upload. The client issues `GET` or `HEAD` against
`/media/{sha256}`, optionally with a `.{ext}` or `.thumb.jpg` suffix, presenting a freshly
signed Blossom read-authorization event.

## Preconditions

- The requested path passes `validate_media_path`: 1–3 dot-separated segments, a
  64-character lowercase-hex first segment, and (if present) a safe extension or the
  literal `thumb.jpg` suffix. Anything else is rejected as `404` before any other work runs.
- The request's `Host` header resolves to a known community (`bind_media_read_tenant`);
  otherwise the request fails closed as `404` rather than revealing tenant-binding detail.
- The client presents an `Authorization: Nostr <base64(event)>` header carrying a
  freshly signed kind:24242 Blossom event scoped to the `get` verb, with a valid
  `expiration` in the future, a `created_at` within the last hour (`max_age_secs = 3600`),
  and either an `x` tag matching the requested sha256 or a `server` tag matching the
  bound tenant host.

## Termination / outcome

The flow is synchronous and terminates in exactly one HTTP response per request — there
is no async job, no partial-success state, and no follow-up step the client must poll for:

- **Success (`GET`)**: `200 OK` with the full blob streamed in the body, or `206 Partial
  Content` with the requested byte range, in both cases carrying the sidecar-derived
  `Content-Type` and the security headers described below.
- **Success (`HEAD`)**: `200 OK` with only headers (`content-type`, `content-length`,
  `accept-ranges`, `cache-control`) and an empty body.
- **Terminal failure**: one of the status codes in *Failure / abort / rollback behavior*
  below, each returned immediately with no retry performed by the relay itself.

## Ordered interactions and data movement

1. **Client** builds the request URL from the known hash (plus optional extension) and
   signs a Blossom `get` authorization event, then issues `GET`/`HEAD /media/{sha256_ext}`.
2. **Router** dispatches to `get_blob` or `head_blob` in `crates/buzz-relay/src/api/media.rs`,
   both under the `/media` sub-router.
3. **Path validation** — `validate_media_path` rejects a malformed path before any I/O.
4. **Tenant binding** — `bind_media_read_tenant` resolves the request `Host` header to a
   `TenantContext` via `crate::tenant::bind_community`.
5. **Blossom auth verification** — `extract_blossom_auth` decodes and parses the signed
   event; `verify_blossom_get_auth` (via `verify_blossom_auth_event_for_verb`) checks the
   signature, kind, verb tag, expiration, timestamp window, optional server-tag match, and
   hash/server scope.
6. **Relay-membership check** — `enforce_relay_membership` authorizes the event's pubkey
   against the bound community's membership, with NIP-OA owner-delegation fallback for
   registered agents.
7. **Sidecar content-type gate** — the relay reads a per-blob sidecar record
   (`read_sidecar_mime` / `get_sidecar`) as the authoritative MIME/extension source,
   independent of what the storage backend itself reports, and independent of any
   extension the client supplied in the path.
8. **Storage key resolution** — `resolve_s3_key` derives the actual object key from the
   sidecar's own extension, never from an unvalidated client-supplied one.
9. **Response construction** — for `GET`: no/multi-range → full `200 OK` streamed from
   storage; single valid range → `206 Partial Content` with a capped chunk; range past
   end-of-file or unparseable → `416 Range Not Satisfiable`. For `HEAD`: the same gates run,
   then only headers are returned from `head_with_metadata`, or a bare `404` if metadata is
   missing.
10. **Security headers** are attached to every successful `GET` response:
    `Content-Security-Policy: default-src 'none'`, `X-Content-Type-Options: nosniff`, and
    a `Content-Disposition` of `inline` (previewable types) or `attachment` (everything
    else).

## Authentication / authorization / trust-boundary crossings

- **Transport boundary**: client → relay HTTP, crossed at the router's `/media/{sha256_ext}`
  route.
- **Tenant boundary**: the `Host` header determines which community's data the request can
  reach; an unresolvable host fails closed as `404` rather than falling through to a default
  tenant.
- **Authentication boundary**: the Blossom NIP-24242 signed event (Nostr Schnorr signature,
  `kind:24242`, verb/expiration/timestamp/hash-or-server-tag checks) is the identity proof.
  There is no code path that skips this for reads.
- **Authorization boundary**: relay membership (`enforce_relay_membership`), evaluated only
  after identity is established, with an owner-delegation carve-out for NIP-OA agents.
- **Content-authority boundary**: once inside the tenant, the sidecar record — not the
  request path, not the storage backend's own metadata — is authoritative for what content
  type is served and under what key, closing off content-type/extension spoofing via the
  request path.

## Failure / abort / rollback behavior

This is a read-only flow — there is no state mutation to roll back. Failure means the
request is answered with an error status and no bytes are streamed:

| Condition | Status | Representative verification |
|---|---|---|
| Malformed or out-of-shape path | 404 | `validate_media_path` (unit-level; see also `test_get_nonexistent_returns_404`'s auth prerequisite) |
| Unresolvable tenant host | 404 | `bind_media_read_tenant` |
| Any Blossom auth failure (missing/malformed/expired/wrong-verb/bad-signature header) | 401, uniform body | `crates/buzz-test-client/tests/e2e_media.rs#symbol=test_unauthenticated_reads_are_rejected` |
| Authenticated but hash/server scope missing from the event | 401 (folded into the same generic authentication-failure group) | `crates/buzz-media/src/auth.rs#symbol=verify_blossom_get_auth` |
| Not a relay member (and no NIP-OA owner delegation) | 403 | `crates/buzz-relay/src/api/mod.rs#symbol=enforce_relay_membership` |
| Authenticated, authorized, but hash never uploaded / sidecar missing / extension mismatch | 404 | `crates/buzz-test-client/tests/e2e_media.rs#symbol=test_get_nonexistent_returns_404` |
| Range start beyond end-of-file, or unparseable Range header | 416 | `crates/buzz-test-client/tests/e2e_media_video.rs#symbol=test_video_range_request_416` |
| Storage/streaming/internal error | 500, generic body, real error logged server-side | `crates/buzz-media/src/error.rs#symbol=MediaError.into_response` |

There is no retry or abort-and-cleanup behavior on the relay side beyond returning the
appropriate status: a failed download attempt leaves no partial relay-side state, because
nothing is written during a read.

## Relationships

None declared. The only nodes merged on `origin/launchpad` as of the recorded revision
are `corpus-agents`, `corpus-readme`, `corpus-standard-confidence` and
`corpus-standard-decision-references` — all `type: governance` nodes documenting corpus
authoring practice itself, not a sibling architecture or flow node this document could
point at with `depends-on`, `part-of`, `implements`, `supersedes` or `references`. This is
checked against the current corpus tree, not assumed; revisit once a sibling
media/architecture node merges.

## Not verified

- **How the signed Blossom `Authorization` header is actually attached on desktop, mobile,
  or CLI clients.** Only `desktop/src/shared/lib/mediaUrl.ts`'s URL-rewrite-to-local-proxy
  behavior was inspected, which implies but does not prove the native Tauri side signs and
  attaches the header; this is recorded above as an `INFERENCE` with `confidence: 0.6`, not
  a `FACT`.
- **Mobile (`mobile/`) and `buzz-cli`'s own media-download call sites** were not inspected
  for this node; the relay contract they must satisfy is unchanged regardless, since it is
  defined server-side.
- **The exact behavior of `buzz_media::serve_inline()`'s allow-list** (which content types
  render inline versus force `attachment`) was not opened; the flow's use of it is
  documented structurally (a decision point exists) without restating its full type list.
