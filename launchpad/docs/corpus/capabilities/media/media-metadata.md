---
id: capabilities-media-media-metadata
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
  - statement: "buzz-media's upload pipeline computes and stores per-blob metadata in a `BlobMeta` struct (`dim`, `blurhash`, `thumb_url`, `ext`, `mime_type`, `size`, `uploaded_at`, `duration_secs`), serialized as sidecar JSON at a tenant-scoped key `_meta/{community}/{sha256}.json` (built by `MediaStorage::sidecar_key`/`ctx_sidecar_key`) — a distinct object from the blob bytes themselves, which live at `{sha256}.{ext}`."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/src/storage.rs"
  - statement: "The image pipeline (`generate_image_metadata_sync` in `thumbnail.rs`) populates `dim` (pixel `WxH`), `blurhash` (encoded at 4x3 components from a 320px-max-dimension thumbnail), and `thumb_url`, leaving `duration_secs` at its default `None`; it is a no-op returning `BlobMeta::default()` for any MIME type not prefixed `image/`, so a generic file or a video never reaches this function at all."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/src/thumbnail.rs"
  - statement: "The video pipeline (`process_video_upload` in `upload.rs`) populates `dim` from the sniffed video's own measured width/height and `duration_secs` from its measured duration, but leaves `blurhash` and `thumb_url` as empty strings — the code's own comment marks this 'no thumbnail for video — desktop handles that', so no server-side thumbnail or blurhash is ever generated for a video blob."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/src/upload.rs"
  - statement: "The generic-file pipeline (the buffered path's not-an-image branch in `upload.rs`) stores a minimal sidecar carrying only `size`, `ext`, `mime_type`, and `uploaded_at`, with `dim`, `blurhash`, and `thumb_url` left as empty strings and `duration_secs` left `None` — the surrounding code comment states explicitly 'no thumbnail/dim/blurhash/duration for generic files'."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/src/upload.rs"
  - statement: "The `BlobMeta` sidecar carries no field naming the uploader — no pubkey, no display name, no IP address — and `MediaStorage::get_sidecar` and `read_sidecar_mime`, the only two functions that read it, return only the fields the struct defines; an uploader's identity is not part of this record at all."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/src/storage.rs"
  - statement: "The HTTP response returned to the uploader — `BlobDescriptor`, defined in `crates/buzz-media/src/types.rs` as the Blossom BUD-02 response type — is a distinct Rust type from the stored `BlobMeta` sidecar. `upload.rs`'s private `build_descriptor` function constructs a `BlobDescriptor` from a `BlobMeta` plus the request-scoped `sha256`/`ext`/`mime`/`size`/`uploaded_at`, converting `BlobMeta`'s empty-string `dim`/`blurhash`/`thumb_url` fields to `None` so `BlobDescriptor`'s `#[serde(skip_serializing_if = \"Option::is_none\")]` fields are omitted from the JSON response entirely, rather than serialized as empty strings."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/src/upload.rs"
      - "crates/buzz-media/src/types.rs"
  - statement: "Two unit tests in `crates/buzz-media/src/upload.rs` directly assert this empty-to-`None` conversion: `test_build_descriptor_video_omits_empty_thumb_and_blurhash` asserts a video's empty `blurhash`/`thumb_url` become `None` and are absent from the serialized JSON while `dim` and `duration` remain present, and `test_build_descriptor_image_includes_thumb_and_blurhash` asserts the inverse for an image (populated `blurhash`/`thumb` present in JSON, `duration` absent)."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/src/upload.rs"
  - statement: "Reading a blob back is gated on this same sidecar record before any blob bytes are read from storage: both `get_blob` and `head_blob` in `crates/buzz-relay/src/api/media.rs` call `read_sidecar_mime`/`get_sidecar` first and return `MediaError::NotFound` if no sidecar resolves for the requesting tenant, and — for an explicit `{sha256}.{ext}` path — additionally reject the request if the requested extension does not match the sidecar's own recorded `ext`. The sidecar, not the blob's mere presence in the bucket, is what makes a blob servable."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/media.rs"
  - statement: "`crates/buzz-test-client/tests/e2e_media.rs`'s `test_upload_and_get` uploads a tiny JPEG, parses the returned `BlobDescriptor` JSON, and asserts `sha256` matches the computed content hash, `url` contains that `sha256`, and `size` is greater than zero. The same test's own comment states that `dim` and `blurhash` are checked only as best-effort — logged, not asserted to a specific value — because image processing may not run reliably against a minimal, hand-constructed 1x1 test JPEG."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/e2e_media.rs"
  - statement: "A second, entirely separate record type — `UploadRecord` in `crates/buzz-media/src/upload_record.rs`, written only when the deployment enables `BUZZ_MEDIA_UPLOAD_RECORDS` (off by default) — is the sole place an uploader's identity is recorded: it carries `uploader_id` (hex pubkey), `uploader_npub` (bech32 encoding of the same key), an optional best-effort `uploader_name`, and optional `ip`/`port` fields collected only when a second, independent opt-in (`BUZZ_MEDIA_UPLOAD_IP_HEADER`) is also configured and the header parses as a syntactically valid public IP address (fail-empty otherwise, per `parse_public_ip`/`is_public_ip`)."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/src/upload_record.rs"
  - statement: "`upload_record.rs`'s own module documentation states this record exists because 'moderation and legal reporting (e.g. NCMEC CyberTipline) need facts about upload events' that content-addressed blob storage cannot answer on its own, and states the collected IP 'goes only into this record — never blob metadata, never the upload response, never the hash-chained audit log' — the moderation record and the `BlobMeta` sidecar are kept structurally separate by design, not merely by current omission."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/src/upload_record.rs"
  - statement: "The moderation record duplicates `ext`, `mime_type`, and `size` from the same accepted upload, and the module's own 'Consumer contract' documentation states this is so a consumer (buzz-moderation) can derive the blob key (`{sha256}.{ext}`) and assess scan eligibility without a second round trip to the sidecar; the record is keyed `_uploads/{community}/{sha256}/{event_id}.json`, a distinct prefix from the sidecar's `_meta/{community}/{sha256}.json`."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/src/upload_record.rs"
  - statement: "A second, entirely independent mechanism for media-adjacent metadata exists at the Nostr event layer: an `imeta` tag (NIP-92), built from a `BlobDescriptor` by `crates/buzz-cli/src/client.rs`'s `build_imeta_tag` when a client attaches an uploaded file to a message, and checked on ingest by `crates/buzz-relay/src/handlers/imeta.rs`'s `validate_imeta_tags`, which allows exactly the keys `url, m, x, size, dim, blurhash, alt, thumb, fallback, duration, bitrate, image, filename` on such a tag. Several of these key names (`size`, `dim`, `blurhash`, `duration`, `thumb`) echo `BlobDescriptor`/`BlobMeta` field names, but the tag is client-supplied content on a message event, re-validated independently at ingest — not the storage-layer sidecar this node describes, and not restated here."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/client.rs"
      - "crates/buzz-relay/src/handlers/imeta.rs"
  - statement: "VISION_PROJECTS.md's own Status table marks 'Blossom media storage (SHA-256, S3)' as 'Ships today', naming the capability this node's metadata is part of at the product level."
    entry_class: FACT
    evidence:
      - "VISION_PROJECTS.md:252"
  - statement: "At the recorded revision, `origin/launchpad`'s corpus tree carries three merged nodes whose subject matter this node depends on: `architecture-containers-object-storage` (the bucket and key taxonomy the sidecar and moderation record live in), `architecture-flows-media-upload` (the end-to-end upload flow that produces this metadata), and `architecture-flows-media-download` (the flow that serves a blob once this metadata resolves it) — confirmed directly against the merge target rather than this worktree's own branch."
    entry_class: FACT
    evidence:
      - "git_ls_tree(ref='origin/launchpad', path='launchpad/docs/corpus') -> includes architecture/containers/object-storage.md, architecture/flows/media-upload.md, architecture/flows/media-download.md, checked at commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
relationships:
  - type: references
    target: architecture-containers-object-storage
  - type: references
    target: architecture-flows-media-upload
  - type: references
    target: architecture-flows-media-download
---

# Media metadata: capability

The product records a fixed set of facts about every uploaded media blob — its byte
size, sniffed MIME type, pixel dimensions and blurhash placeholder for images, a
thumbnail location, and video duration where applicable — independently of, and
before, any Nostr event that later references the blob. A client that uploads to
`PUT /upload` (or the legacy `/media/upload` alias) receives these facts back
immediately in the response, and a later `GET`/`HEAD /media/{sha256_ext}` request from
any client is served only once the same stored facts resolve for the requesting
tenant — the metadata is not merely an echo back to the uploader, it is the
authoritative gate every read must pass.

## What is recorded, and how it varies by content type

Buzz's upload pipeline (`crates/buzz-media`) writes one JSON sidecar object per blob,
tenant-scoped at `_meta/{community}/{sha256}.json`, holding a `BlobMeta` record: pixel
`dim` ("WxH"), a `blurhash` placeholder string, a `thumb_url`, the canonical file
`ext`, the sniffed `mime_type`, the byte `size`, the `uploaded_at` Unix timestamp, and
an optional `duration_secs`. Which of these fields carry real content depends on what
was uploaded:

- **Images** get a full record: `dim`, `blurhash` (encoded from a 320px-max-dimension
  thumbnail), and `thumb_url` are all populated; `duration_secs` stays `None`.
- **Video** gets `dim` and `duration_secs` from the sniffed file itself, but no
  thumbnail or blurhash is generated server-side at all — that is left to the client.
- **Generic files** get the smallest record of the three: only `size`, `ext`,
  `mime_type`, and `uploaded_at` — `dim`, `blurhash`, and `thumb_url` stay empty and
  `duration_secs` stays `None`.

None of these three variants records who uploaded the file. The sidecar's `BlobMeta`
type has no uploader field at all, and the two functions that ever read it back
(`get_sidecar`, `read_sidecar_mime`) can only return what the struct defines.

## The upload response is a different object from the stored sidecar

What a client receives back from `PUT /upload` — a `BlobDescriptor` — is a distinct
type from the `BlobMeta` sidecar just written to storage, built from it by a
dedicated `build_descriptor` step. That step converts `BlobMeta`'s empty-string
`dim`/`blurhash`/`thumb_url` (the generic-file and partial-video cases above) into
`None`, so the JSON response omits those keys entirely for a video or a generic file
rather than sending them as empty strings. Unit tests pin this conversion in both
directions — one confirming a video's descriptor omits `blurhash`/`thumb` while
keeping `dim`/`duration`, the other confirming an image's descriptor carries
`blurhash`/`thumb` while omitting `duration`. A live end-to-end test uploads a real
JPEG and asserts the response's `sha256`, `url`, and `size` fields directly, while
treating `dim`/`blurhash` as best-effort for its minimal test image rather than
asserting exact values.

## Reading is gated on the same metadata that recording produced

The metadata capability is not one-directional. Serving a blob back — the `GET`/`HEAD
/media/{sha256_ext}` handlers — resolves the tenant-scoped sidecar first, before any
blob bytes are read from storage, and fails the request with a not-found response if
no sidecar resolves for the requesting tenant. When the request names an explicit
extension, the handler additionally checks it against the sidecar's own recorded
`ext` and rejects a mismatch. The sidecar this capability writes at upload time is
therefore the thing that later makes the blob servable at all, not a passive record
kept alongside it.

## A separate, opt-in ledger for who uploaded

A structurally distinct record — an upload-event record, gated behind a
deployment-wide flag that is off by default — is the only place an uploader's
identity is recorded at all: a hex pubkey, its bech32 equivalent, an optional
best-effort display name, and an optional IP/port pair collected only when a second,
independent flag is also configured and the observed address parses as public. Its
own documentation states this separation is deliberate — the collected IP, in
particular, is stated to go into this record and nowhere else, never into the blob
metadata this node otherwise describes, never into the response the uploader sees,
and never into the hash-chained audit log. It duplicates a few of the same facts
(extension, MIME type, size) purely so a downstream consumer can act on it without a
second lookup against the sidecar — it does not supersede or extend the sidecar
itself.

## Maturity

Shipped. The `BlobMeta` sidecar and `BlobDescriptor` response types are both in the
main `buzz-media`/`buzz-relay` code today, exercised by unit tests on the
descriptor-building conversion and by a live end-to-end upload/download test.
VISION_PROJECTS.md's own product-level Status table marks "Blossom media storage
(SHA-256, S3)" — the capability this metadata is part of — "Ships today".

## Boundary

This node does not describe:

- **How the metadata is produced and consumed as part of the larger upload/download
  flow** — the ordered admission checks, auth, and failure/rollback behavior belong to
  the architecture flow nodes for media upload and media download, referenced below.
- **The object-storage bucket and key taxonomy** the sidecar (`_meta/...`) and
  moderation record (`_uploads/...`) live inside, alongside the blob bytes themselves
  and the unrelated git-on-object-storage content sharing the same bucket — that is
  the object-storage container node, referenced below.
- **The boundary contract this capability is exposed through** — the exact
  `PUT`/`GET`/`HEAD` HTTP request and response shapes, as an interface. No
  interface-typed corpus node exists yet at this writing; when one is written for the
  Blossom HTTP surface, it should own that contract rather than this node restating
  it.
- **The step-by-step flow through this capability.** The two flow nodes referenced
  below already cover upload and download end to end; no separate flow node is needed
  for metadata specifically.
- **How the system is operated** — bucket provisioning, the storage-usage sweep, or
  deployment topology. That is the object-storage container node's territory.
- **The `imeta` Nostr event tag (NIP-92).** A client separately attaches an `imeta`
  tag to a message event referencing an uploaded blob, built from the upload response
  and independently re-validated on ingest. It echoes some of the same field names
  this node describes but is a distinct mechanism at the event-composition layer, not
  the storage-layer metadata recorded here. No corpus node for it exists yet at this
  writing.

## Relationships

- `references`: `architecture-containers-object-storage` — the bucket and key
  taxonomy the sidecar and moderation record are stored under.
- `references`: `architecture-flows-media-upload` — the end-to-end flow that produces
  this metadata as one of its steps.
- `references`: `architecture-flows-media-download` — the flow that serves a blob
  gated on this same metadata.

## Scope and omissions

**This node covers** what per-blob metadata Buzz's media (Blossom) storage records at
upload time, where it is stored, which facts differ by content type (image, video,
generic file), how the stored sidecar differs from the HTTP response descriptor
returned to the uploader, how a later read is gated on that same metadata, and the
distinct, off-by-default moderation side-channel record that is the only place an
uploader's identity is ever recorded — as distinguished from the separate,
Nostr-event-level `imeta` tag.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The full upload/download flow, its ordered auth checks, and its failure/rollback behavior | `architecture-flows-media-upload`, `architecture-flows-media-download` |
| The object-storage bucket, its key taxonomy, and its git-on-object-storage co-tenant | `architecture-containers-object-storage` |
| The `imeta` Nostr event tag (NIP-92) — its own construction, validation rules, and how a message references a blob | Not yet a corpus node at this writing |
| The Blossom/BUD-11 HTTP request/response contract as a formal interface | No interface-typed corpus node exists yet |
| What buzz-moderation does with the upload-event record once written (NCMEC CyberTipline reporting, scan triggers, etc.), beyond the shape of the record itself | Not yet a corpus node at this writing |
| Per-content-type upload size caps and rate/concurrency limits | `architecture-flows-media-upload` |

**Expected but not verified when this node was written:**

- **Whether a background GC job exists for a blob orphaned when metadata preparation
  fails after the blob write.** `architecture-flows-media-upload` already flags this
  as unverified for the flow as a whole; this node makes no independent claim about
  it.
- **Whether `crates/buzz-test-client/tests/e2e_media_extended.rs` exercises anything
  metadata-specific.** Not opened for this node; only `e2e_media.rs` was read.
- **Whether any client (desktop, mobile, CLI) surfaces `dim`/`blurhash`/`duration` to
  a human user, versus only consuming them to build an `imeta` tag.** Not inspected —
  only the relay/storage-side contract was verified here.
- **Whether the moderation upload-event record is actually consumed by a running
  `buzz-moderation` component today**, versus existing only as a write-side record
  with no reader yet built. Only the writer (`upload_record.rs`) and its own module
  documentation were inspected.
