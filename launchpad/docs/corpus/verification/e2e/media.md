---
id: verification-e2e-media
type: verification
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 473205a7457b208455f188847bfb27b01aa83cac."
    entry_class: FACT
    evidence:
      - "commit 473205a7457b208455f188847bfb27b01aa83cac"
  - statement: "The relay's media router registers PUT /upload and PUT /media/upload (a legacy alias) both to api::media::upload_blob, and GET/HEAD /media/{sha256_ext} to api::media::get_blob and api::media::head_blob respectively."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs:39-46"
      - "crates/buzz-relay/src/api/media.rs"
  - statement: "buzz-media is a library crate with no Axum dependency, exposing MediaStorage, BlobDescriptor, MediaError and the process_upload/process_file_upload/process_video_upload pipeline functions; the Axum handlers that call into it live in buzz-relay's api::media module, not in buzz-media itself."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/src/lib.rs"
  - statement: "e2e_media.rs's own module doc-comment states it requires a relay running at localhost:3000 and MinIO at localhost:9000, that every test in the file is #[ignore] so none run in CI by default selection, and names the command `cargo test -p buzz-test-client --test e2e_media -- --ignored --nocapture` to run them, with RELAY_HTTP_URL overriding the relay URL."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/e2e_media.rs"
  - statement: "test_upload_and_get asserts a successful PUT /upload returns 200 with a BlobDescriptor whose sha256 matches the uploaded content, whose url contains that sha256, whose size is positive and whose type is present; it then asserts an authenticated GET /media/{sha256}.jpg returns 200 with byte-identical content, an authenticated HEAD returns 200 with a content-type header, and an authenticated GET on the .thumb.jpg suffix returns 200."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/e2e_media.rs"
  - statement: "test_upload_idempotent asserts that uploading identical bytes twice, signed by two different keypairs, returns a BlobDescriptor with an identical sha256 and an identical url on both uploads."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/e2e_media.rs"
  - statement: "test_upload_no_auth_returns_401, test_upload_missing_x_sha256_returns_401 and test_upload_hash_mismatch_returns_400 each assert 401 for one malformed upload request: no Authorization header, a missing X-SHA-256 header, and an auth event whose x tag does not match the uploaded body's real hash respectively -- the third test's name says 400 but its own assertion checks status 401."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/e2e_media.rs"
  - statement: "test_get_nonexistent_returns_404 asserts an authenticated GET for a sha256 that was never uploaded returns 404, and test_unauthenticated_reads_are_rejected asserts a bare (no Authorization header) GET, HEAD and thumbnail GET against a never-uploaded hash each return 401 -- together establishing that authentication is checked before the storage existence lookup, so a bare request can never distinguish 'missing' from 'unauthorized'."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/e2e_media.rs"
  - statement: "test_upload_real_image is gated on a TEST_IMAGE_PATH environment variable; a repository-wide search found that variable referenced nowhere except inside this test function itself, including not in any GitHub Actions workflow, so the test prints 'Skipping' and returns without asserting anything in every environment this node checked."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/e2e_media.rs"
      - "grep_repo(\"TEST_IMAGE_PATH\") -> only crates/buzz-test-client/tests/e2e_media.rs"
  - statement: "e2e_media_extended.rs's module doc-comment describes itself as covering auth edge cases, content validation, multi-format uploads, and WebSocket imeta validation, and names the command `cargo test -p buzz-test-client --test e2e_media_extended -- --ignored --nocapture` to run it."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/e2e_media_extended.rs"
  - statement: "test_upload_png_roundtrip, test_upload_gif_roundtrip and test_upload_webp_roundtrip each assert a format-specific upload returns 200 with the correct sniffed MIME type and a URL carrying the matching extension, then assert an authenticated GET returns the identical bytes back."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/e2e_media_extended.rs"
  - statement: "test_auth_wrong_kind, test_auth_missing_t_tag, test_auth_missing_expiration, test_auth_expired_token, test_auth_empty_content and test_auth_server_tag_mismatch each construct one malformed Blossom auth-event shape and assert the upload is rejected 401; test_auth_server_tag_correct constructs a well-formed event carrying a server tag that matches the request host and asserts the upload succeeds with 200, confirming the server-tag check accepts a correctly scoped token rather than rejecting every server-tagged request."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/e2e_media_extended.rs"
  - statement: "test_upload_svg_accepted_as_text_xml, test_upload_pdf_accepted, test_upload_zero_bytes_accepted and test_upload_random_bytes_accepted each assert that content not recognized as a blocked type is accepted (200) via the generic-file path with the sniffed content-type reported in the BlobDescriptor; test_upload_html_served_as_inert_attachment additionally asserts that the round-tripped GET response carries Content-Disposition: attachment, X-Content-Type-Options: nosniff and Content-Security-Policy: default-src 'none'."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/e2e_media_extended.rs"
  - statement: "test_legacy_media_route_rejects_non_media asserts PUT /media/upload returns 415 (UNSUPPORTED_MEDIA_TYPE) for a PDF that the standard /upload route accepts, test_legacy_media_route_still_accepts_canonical_media asserts the same legacy route still returns 200 for a JPEG, and test_standard_upload_rejects_recognized_audio asserts the standard /upload route itself returns 415 for a recognized audio fixture."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/e2e_media_extended.rs"
  - statement: "test_concurrent_upload_same_file asserts that two concurrent uploads of identical bytes signed by two different keypairs both return 200 and converge on the same sha256 and url."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/e2e_media_extended.rs"
  - statement: "test_ws_valid_imeta, test_ws_invalid_imeta_external_url and test_ws_invalid_imeta_missing_fields each create a channel, upload or reference a media hash, then connect over WebSocket and assert whether a kind:9 message event carrying an imeta tag referencing that hash is accepted or rejected -- this exercises message-event imeta validation, a distinct obligation layered on top of, and not part of, the Blossom HTTP upload/download contract itself."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/e2e_media_extended.rs"
  - statement: "Root TESTING.md states that `just test-unit` and `just test` do not run the E2E suites in buzz-test-client because they are marked #[ignore] and require a running relay, naming `cargo test -p buzz-test-client -- --ignored` (against a relay already started separately) as the way to run them."
    entry_class: FACT
    evidence:
      - "TESTING.md"
  - statement: "The 'Relay E2E' job in .github/workflows/ci.yml has a step named 'Media read-auth e2e' whose own comment states these tests were #[ignore]d and 'selected by no CI job, so the lane never ran' before this step was added, and which runs `cargo test -p buzz-test-client --no-fail-fast --test e2e_media --test e2e_media_extended --test e2e_media_video -- --ignored --nocapture` against the relay and MinIO already started earlier in the same job."
    entry_class: FACT
    evidence:
      - ".github/workflows/ci.yml"
  - statement: "The 'Relay E2E' job (and the 'Desktop E2E Relay' job it needs, which builds the relay binary it runs against) each run unconditionally when github.event_name == 'push', and otherwise only when the repository's 'changes' job reports its rust path-filter as true -- a filter matching crates/**, migrations/**, schema/**, Cargo.toml, Cargo.lock, rust-toolchain.toml, deny.toml, .github/workflows/ci.yml, scripts/run-tests.sh, scripts/model-capabilities.json, scripts/normative-corpus.json and justfile -- so a pull request touching none of those paths (such as this corpus-only change) skips both jobs entirely."
    entry_class: FACT
    evidence:
      - ".github/workflows/ci.yml"
  - statement: "On a completed CI run of a branch that did touch Rust paths (task/1192-tenancy-tenant-context, run 33370592033), the 'Relay E2E' job concluded 'success' and its 'Media read-auth e2e' step individually concluded 'success', confirming the three named e2e media test binaries passed together against a live relay and MinIO at that commit."
    entry_class: FACT
    evidence:
      - "gh_run_view(33370592033, repo=\"launchpad-26/buzz\", job=\"Relay E2E\", step=\"Media read-auth e2e\") -> conclusion: success"
  - statement: "This node treats the Blossom upload round trip, its content-validation and format-acceptance variants, its idempotency guarantee, and its authentication/authorization rejection family as one obligation rather than splitting them into several nodes, because issue #1365's definition of done asks for exactly one hand-authored canonical document for this task and states that a newly discovered second concept should be filed separately rather than folded in or split out preemptively; the WS imeta-tag obligation is the concept this node did treat as separate, per the note below."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1365 definition of done"
relationships:
  - type: implements
    target: corpus-template-test-contract
  - type: references
    target: architecture-flows-media-upload
  - type: references
    target: architecture-flows-media-download
---

# Blossom media upload/download — test contract

## Purpose and boundary

This node documents one obligation: that Buzz's Blossom-compatible media endpoints
(`PUT /upload`, the legacy `PUT /media/upload` alias, and `GET`/`HEAD
/media/{sha256_ext}`) round-trip valid content byte-for-byte end to end and reject
invalid, unauthenticated or malformed requests with their documented status —
together with the two automated end-to-end test files that currently verify it and
those tests' actual enforcement status in this repository's CI. It covers that
obligation only. It does not restate the full request/response contract, the ordered
admission checks, or the storage pipeline internals — those are `architecture-flows-
media-upload` and `architecture-flows-media-download`'s subject, referenced below
rather than duplicated. It does not cover video upload or HTTP Range-request behavior
(a third test file, `e2e_media_video.rs`, not opened for this node), and it does not
cover WebSocket `imeta`-tag validation, a related but distinct obligation exercised by
three tests in one of this node's own named files — see *Scope and omissions*.

## Obligation

> A client that authenticates an upload with a valid, freshly-signed Blossom
> (kind:24242) authorization event and an `X-SHA-256` header matching the request
> body receives a `BlobDescriptor` describing that content, can retrieve
> byte-identical bytes back via an authenticated `GET` or `HEAD` on
> `/media/{sha256_ext}`, and uploading the same content again is idempotent
> (identical `sha256`/`url`); any upload or read that fails Blossom authentication,
> hash-integrity, or (for uploads) the route's content-type policy is rejected with
> its documented HTTP status and never becomes retrievable.

## Verifying test(s)

All tests below live in `crates/buzz-test-client/tests/` and are `#[tokio::test]`,
`#[ignore]`-annotated functions requiring a live relay and MinIO.

**`e2e_media.rs`** — the core round-trip and auth-rejection contract:

- `test_upload_and_get` — success round trip: 200 + correct `BlobDescriptor` fields,
  then byte-identical GET, a 200 HEAD with `content-type`, and a 200 thumbnail GET.
- `test_upload_idempotent` — re-uploading identical bytes under a different signer
  returns the same `sha256`/`url`.
- `test_upload_no_auth_returns_401` — missing `Authorization` header.
- `test_upload_missing_x_sha256_returns_401` — missing `X-SHA-256` header.
- `test_upload_hash_mismatch_returns_400` — `x`-tag/body hash mismatch (asserts 401
  despite its name).
- `test_get_nonexistent_returns_404` — authenticated GET for a hash never uploaded.
- `test_unauthenticated_reads_are_rejected` — bare GET/HEAD/thumbnail-GET against a
  never-uploaded hash each return 401, proving auth runs before the existence check.
- `test_upload_real_image` — real-image round trip, gated on `TEST_IMAGE_PATH`; see
  *Limits*, it currently no-ops.

**`e2e_media_extended.rs`** — format, edge-case and route-policy coverage of the same
obligation:

- `test_upload_png_roundtrip`, `test_upload_gif_roundtrip`, `test_upload_webp_roundtrip`
  — per-format content-type detection plus byte-identical round trip.
- `test_auth_wrong_kind`, `test_auth_missing_t_tag`, `test_auth_missing_expiration`,
  `test_auth_expired_token`, `test_auth_empty_content`, `test_auth_server_tag_mismatch`
  — one malformed Blossom auth-event shape each, all asserting 401.
- `test_auth_server_tag_correct` — the same server-tag check accepts a correctly
  host-scoped token (200), not just rejects mismatched ones.
- `test_upload_svg_accepted_as_text_xml`, `test_upload_pdf_accepted`,
  `test_upload_zero_bytes_accepted`, `test_upload_random_bytes_accepted` — non-image
  content accepted via the generic-file path with the sniffed content-type reported.
- `test_upload_html_served_as_inert_attachment` — HTML is accepted but its GET
  response is forced to `Content-Disposition: attachment` with `nosniff` and a
  restrictive CSP.
- `test_legacy_media_route_rejects_non_media`,
  `test_legacy_media_route_still_accepts_canonical_media`,
  `test_standard_upload_rejects_recognized_audio` — the legacy `/media/upload` alias
  enforces a narrower, image-only content policy than `/upload`, and the standard
  route itself rejects recognized audio.
- `test_concurrent_upload_same_file` — two concurrent uploads of identical bytes by
  different keys both succeed and converge on the same `sha256`/`url`.

**Not part of this obligation** (see *Scope and omissions*): `test_ws_valid_imeta`,
`test_ws_invalid_imeta_external_url`, `test_ws_invalid_imeta_missing_fields`, also in
`e2e_media_extended.rs`.

## How to run it

```bash
# Requires a running relay (default http://localhost:3000) and MinIO (localhost:9000).
cargo test -p buzz-test-client --no-fail-fast \
  --test e2e_media --test e2e_media_extended -- --ignored --nocapture

# Override the relay URL:
RELAY_HTTP_URL=http://localhost:3000 cargo test -p buzz-test-client \
  --test e2e_media --test e2e_media_extended -- --ignored --nocapture
```

`just test-unit` and `just test` do not run these — root `TESTING.md` documents that
`#[ignore]`-marked E2E suites are excluded from both and require a relay started
separately first (see `TESTING.md`'s "Live Local Relay" section).

## Current enforcement status

**Gated**, as of `473205a7457b208455f188847bfb27b01aa83cac`. Every test above is
`#[ignore]`-annotated in source and is not selected by either `just` test task. CI
does explicitly select and run them: `.github/workflows/ci.yml`'s `relay-e2e` job's
"Media read-auth e2e" step runs `e2e_media`, `e2e_media_extended` and
`e2e_media_video` together against a relay and MinIO it starts earlier in the same
job. That job itself is conditional — it runs unconditionally on a push to the
default branch, and on a pull request only when the workflow's `rust` path-filter
matches the changed files (`crates/**`, `migrations/**`, `schema/**`, `Cargo.toml`,
`Cargo.lock`, `rust-toolchain.toml`, `deny.toml`, the workflow file itself, and a
handful of scripts). A pull request that changes none of those paths — this
corpus-only change included — skips the job entirely, so "gated" names a real,
checkable condition rather than a formality.

**Point-in-time pass evidence.** On a completed run of a branch that did touch Rust
paths (`task/1192-tenancy-tenant-context`, CI run `33370592033`), the "Media
read-auth e2e" step concluded `success`. That is one observed pass at one commit on
another branch, not a claim about the commit recorded above — no live run was
executed while authoring this node; see *Limits*.

## Limits

**Scenarios actually exercised**, by the tests above: successful upload/download
round trip for JPEG, PNG, GIF, WebP, SVG-as-text/xml, PDF, zero-byte and random-byte
content; sequential and concurrent idempotent re-upload; the malformed-auth-event
rejection family (missing header, missing/mismatched hash, wrong kind, missing `t`
tag, missing/expired `expiration`, empty content, mismatched `server` tag) alongside
one accepted correctly-scoped `server`-tag case; unauthenticated-read rejection
ordered ahead of the existence check; a never-uploaded hash returning 404; the
legacy route's narrower content policy; and one recognized-audio rejection on the
standard route.

**Not exercised by these two files, and not asserted by this node:**

- **Video upload and HTTP Range-request handling** (206 partial content, 416 range
  errors) — a third file, `crates/buzz-test-client/tests/e2e_media_video.rs`, covers
  this and is run alongside these two in the same CI step, but was not opened for
  this node and no claim above rests on it.
- **The community-deletion write-fence** (`ServingWriteGuard`, the `403
  CommunityWriteFenced` / `503 ServiceUnavailable` split) — documented in
  `architecture-flows-media-upload.md`, but no test in either file named here was
  found asserting it.
- **Rate-limit and concurrency-limit rejections (429)** — defaults are documented in
  the same flow node; no test here exercises hitting either limit.
- `test_upload_real_image` **contributes nothing today**: it is gated on
  `TEST_IMAGE_PATH`, which this node found set nowhere in the repository, so it
  no-ops rather than exercising the real-image path it names.

**What "gated, last observed passing" does not mean.** It does not mean every
scenario above currently passes at the exact commit this node records — the cited
CI run is from a different branch and an earlier point in time. It does not mean
the obligation is exercised on every pull request — only ones that touch a
Rust-relevant path. A green run of the cited step proves those three test binaries
passed together at that commit; it does not certify this node's own recorded
revision.

## Scope and omissions

**This node covers** the Blossom upload/download round-trip-and-rejection
obligation, the tests in `e2e_media.rs` and `e2e_media_extended.rs` that verify it,
how to run them, and their real (conditional) CI enforcement status.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The full request/response contract, ordered admission checks, and storage pipeline for upload | `architecture-flows-media-upload` |
| The same, for download/read | `architecture-flows-media-download` |
| Video upload and Range-request behavior (`e2e_media_video.rs`) | Not opened for this node; a future test-contract node's task if one is written |
| WebSocket `imeta`-tag validation on a kind:9 message event (`test_ws_valid_imeta` and its two negative siblings) | A distinct, message-event-level obligation this node deliberately excludes rather than folds in, per this task's instruction to file a newly discovered second obligation separately instead of broadening this document |
| The Blossom/BUD-11 wire specification itself, and non-relay client construction of the auth event | `architecture-flows-media-upload`'s own stated omissions, unchanged here |

**Relationships, checked rather than assumed.** At the recorded revision,
`origin/launchpad`'s corpus tree (`git ls-tree -r --name-only origin/launchpad --
launchpad/docs/corpus`) carries both `architecture-flows-media-upload` and
`architecture-flows-media-download`, so the `references` edges above are real. It
also carries `corpus-template-test-contract`, the template this node is built from,
so the `implements` edge is real too. `capabilities-media-media`,
`capabilities-media-download` and `capabilities-media-blossom` are also present at
this revision and describe the same subject at a different (product-capability)
altitude; this node does not add edges to them, to avoid linking four neighbors for
one test-contract node before any convention exists for which of them a
verification node should point at — a later pass may add `references` there once
one does.

**Expected but not verified when this node was written:**

- **Whether every test named above currently passes at commit
  `473205a7457b208455f188847bfb27b01aa83cac` specifically.** The pass evidence cited
  is from a different branch and commit; no live relay/MinIO stack was started to
  re-run these tests as part of authoring this node.
- **Whether `e2e_media_video.rs` currently passes alongside these two in the same CI
  step**, and what it covers in detail — read only far enough to confirm it exists
  and is selected by the same CI step, per the enforcement-status claims above.
- **Client-side (desktop/mobile/CLI) construction of the Blossom auth event** — out
  of scope for this relay-side test contract, and already named as unverified by
  `architecture-flows-media-download`.
