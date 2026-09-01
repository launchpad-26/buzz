---
id: layers-data-object-storage-media-objects
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
  - statement: "node.schema.json's type field is a closed 13-member enum (architecture, layers, capabilities, platforms, implementation, interfaces-events, verification, operations, development, release, governance, agent, ingestion) with no `data` member; a node whose path lives under `layers/` takes `type: layers`."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "Issue #1070 assigns this document the path launchpad/docs/corpus/layers/data/object-storage/media-objects.md directly, via its own corpus-plan:v2 alias header comment and its Objective sentence."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1070, read directly via gh issue view"
  - statement: "Sibling issues #1067 and #1069 in the same layers/data/object-storage/ group are drafted on still-open PR #1873 (branch task/610-batch-2-data-storage, not merged to origin/launchpad at authoring time); both blossom-storage.md and git-objects.md chose type: layers over templates/datastore.md's own type: architecture suggestion for a real instance, and both disclose that tension in their own evidence ledgers rather than resolving it silently. blossom-storage.md's own Scope-and-omissions table names one gap it deliberately leaves unowned, quoted verbatim: 'The domain meaning of an uploaded blob (what a message attachment or avatar is) | a future data-entity corpus node, not yet written.'"
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1873 (open PR, task/610-batch-2-data-storage), read directly via git show against the PR branch"
  - statement: "This document follows the same type: layers precedent as #1067 and #1069 for consistency, and scopes itself to the gap blossom-storage.md's own ledger names rather than re-documenting the bucket's key-namespace, migration, access-pattern, lifecycle, tenancy, or failure internals a second time — a second full datastore-shaped document over the same bucket half would duplicate blossom-storage.md's canonical content, which AGENTS.md's one-idea rule and Feature #610's own anti-duplication acceptance criterion both bar."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
      - "launchpad/docs/corpus/schema/node.schema.json"
    confidence: 0.7
  - statement: "crates/buzz-media/src/types.rs defines BlobDescriptor, documented as 'Blossom BUD-02 response types ... returned by PUT /upload and the legacy media alias', with fields url (String), sha256 (String, 64-char hex), size (u64), mime_type (String, serialized as `type`), uploaded (i64 unix timestamp), and optional dim (String, 'WxH'), blurhash (String), thumb (String, thumbnail URL), and duration (f64 seconds, 'None for non-video blobs')."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/src/types.rs"
  - statement: "crates/buzz-media/src/storage.rs defines BlobMeta with fields dim, blurhash, thumb_url, ext, mime_type, size, uploaded_at, and optional duration_secs — the shape persisted at the sidecar key, distinct from BlobDescriptor's own field set and names (thumb_url vs thumb, uploaded_at vs uploaded, plus ext and ambient fields BlobDescriptor never exposes)."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/src/storage.rs"
  - statement: "crates/buzz-media/src/upload.rs's build_descriptor function is the sole mapping from the persisted BlobMeta sidecar to the client-facing BlobDescriptor: it derives the public URL from sha256+ext, copies size/mime_type/uploaded_at across, and converts each optional BlobMeta field (dim, blurhash, thumb_url, duration_secs) to BlobDescriptor's corresponding optional field, collapsing an empty string to None on the string fields."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/src/upload.rs"
  - statement: "crates/buzz-relay/src/handlers/imeta.rs's validate_imeta_tags accepts exactly twelve imeta keys (url, m, x, size, dim, blurhash, alt, thumb, fallback, duration, bitrate, image, filename), rejects any other key, enforces that url, m, x, size, dim, blurhash, thumb, alt, duration, bitrate, image, and filename may each appear at most once per tag (SINGLETON_KEYS), requires url+m+x+size on every tag, and restricts duration/bitrate/image to m == \"video/mp4\" tags only."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/imeta.rs"
  - statement: "validate_imeta_tags additionally cross-checks internal consistency before any storage lookup: the 64-char hex hash embedded in a /media/{hash}.{ext} url must equal the tag's x value; for the five previewable MIME types (image/jpeg, image/png, image/gif, image/webp, video/mp4) the url's extension must equal the extension mime_to_ext derives from m; and a claimed thumb url's embedded hash must also equal x."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/imeta.rs"
  - statement: "crates/buzz-relay/src/handlers/imeta.rs's verify_imeta_blobs performs five storage-backed checks per imeta tag carrying a non-empty x: (1) the community-scoped sidecar for x must exist via MediaStorage::get_sidecar, or the tag is rejected as referencing a nonexistent blob; (2) the blob object itself ({x}.{sidecar.ext}) must exist via MediaStorage::head; (3) a non-empty claimed m or size must equal the sidecar's stored mime_type/size, and a claimed duration within a 0.1-second tolerance of the sidecar's duration_secs; (4) a claimed thumb's {x}.thumb.jpg object must exist; (5) a claimed image (video poster) must itself have an existing sidecar whose mime_type is one of image/jpeg, image/png, image/gif, image/webp, whose extension matches the image url's embedded extension, and whose blob object exists."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/imeta.rs"
  - statement: "crates/buzz-relay/src/handlers/ingest.rs's ingest_event_inner collects every tag on the incoming event whose first element is the literal string \"imeta\" into imeta_tags, and — only when that collection is non-empty, for any event kind, not gated to one specific kind constant — calls validate_imeta_tags and then, awaited, verify_imeta_blobs, mapping either function's Err(String) to IngestError::Rejected(format!(\"invalid: {e}\")) with the ? operator, before any later processing of the event (thread metadata resolution, storage) runs."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "IngestError's own doc comments state its three variants' wire behavior directly: Rejected is 'Client error (bad event) — WS: OK false, HTTP: 400', distinct from AuthFailed (401/403) and Internal (500) — so a failed imeta structural or referential-integrity check surfaces to the publishing client as an ordinary NIP-01 OK-false rejection (or HTTP 400 on the REST path), not a server error, and the event is never accepted or stored."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "crates/buzz-media/src/storage.rs's sidecar_key/ctx_sidecar_key build the community-scoped _meta/{community}/{sha256}.json key from a CommunityId resolved off a TenantContext, and put_sidecar's own doc comment states directly: 'ctx must be the server-resolved request tenant. Callers must never derive the community from client-supplied blob metadata, URLs, or event tags; this sidecar key is the tenant read gate for otherwise shared CAS bytes.' verify_imeta_blobs calls get_sidecar with the ingest pipeline's own resolved TenantContext, never a value derived from the imeta tag being verified."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/src/storage.rs"
      - "crates/buzz-relay/src/handlers/imeta.rs"
  - statement: "crates/buzz-test-client/tests/e2e_media_extended.rs exercises validate_imeta_tags/verify_imeta_blobs end to end over the WebSocket ingest path in test_ws_valid_imeta, test_ws_invalid_imeta_external_url, and test_ws_invalid_imeta_missing_fields; crates/buzz-test-client/tests/e2e_media_video.rs's test_video_poster_imeta_accepted_via_ws and test_video_poster_imeta_rejects_video_as_poster cover the image (poster-frame) branch of verify_imeta_blobs specifically, including the video-vs-image MIME rejection."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/e2e_media_extended.rs"
      - "crates/buzz-test-client/tests/e2e_media_video.rs"
  - statement: "NIP-92 ('Media Attachments Metadata (imeta)'), fetched pinned to nostr-protocol/nips commit 24b2ae9fdfeb4e5c0d3be854df5977b81afe1983, defines the imeta tag as variadic space-delimited key/value entries, states 'Each imeta tag MUST have a url, and at least one other field', and states 'imeta MAY include any field specified by NIP 94' — Buzz's own required-field set (url, m, x, size) is a stricter subset of this MUST, not a departure from it."
    entry_class: FACT
    evidence:
      - "https://github.com/nostr-protocol/nips/blob/24b2ae9fdfeb4e5c0d3be854df5977b81afe1983/92.md"
  - statement: "NIP-94 ('File Metadata'), fetched at the same pinned commit, defines the base imeta/tag field vocabulary Buzz's ALLOWED_IMETA_KEYS draws from: url, m, x (SHA-256 hex of the file), size, dim, blurhash, thumb, image, alt, and fallback are all defined there; Buzz's filename key is not among NIP-94's fields (nor NIP-92's or NIP-71's), making it a Buzz-specific extension to the imeta vocabulary rather than a spec-defined key."
    entry_class: FACT
    evidence:
      - "https://github.com/nostr-protocol/nips/blob/24b2ae9fdfeb4e5c0d3be854df5977b81afe1983/94.md"
  - statement: "NIP-71 ('Video Events'), fetched at the same pinned commit, states 'The primary source of video information is the imeta tags which is defined in NIP-92' and defines duration and bitrate as additional imeta properties 'aside from those listed in NIP-92 & NIP-94', with image documented there as the video's poster-frame url — matching Buzz's own restriction of duration/bitrate/image to video/mp4-typed imeta tags exactly."
    entry_class: FACT
    evidence:
      - "https://github.com/nostr-protocol/nips/blob/24b2ae9fdfeb4e5c0d3be854df5977b81afe1983/71.md"
  - statement: "launchpad/docs/corpus/architecture/containers/object-storage.md, merged and validating on origin/launchpad at the recorded revision, does not mention imeta or BlobDescriptor anywhere in its own text (checked directly), confirming this node's subject is not a restatement of that container document's own claims."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/containers/object-storage.md"
  - statement: "Issue #1070's Definition of Done requires this document to state whether the store is authoritative, derived, cache or transport; describe owned data, key access patterns, lifecycle/retention and consistency semantics; name tenancy/security boundaries and failure behavior; and link schema/migrations/code/tests rather than copying DDL — worded identically to sibling issue #1069's own Definition of Done."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1070 definition of done"
relationships:
  - type: part-of
    target: architecture-containers-object-storage
---

# Media objects: identity, the `imeta` reference contract, and referential integrity

A **media object** here means the domain unit a message or other Nostr event points
at through an `imeta` tag — the media half of the object-storage bucket, viewed as
*something referenced and checked*, not as bucket internals. This document does not
cover the object-storage container's own existence or technology
(`architecture-containers-object-storage`'s job, linked above via `part-of`), and does
not re-describe the bucket's key-namespace, migration mechanism, access patterns,
lifecycle, tenancy, or failure behavior for the store itself — that is
`blossom-storage.md`'s job (issue #1067, drafted on open PR #1873, not yet merged;
named here by id `layers-data-object-storage-blossom-storage` rather than linked,
since the file does not exist on this branch or on `origin/launchpad` yet). That
document's own evidence ledger explicitly leaves the gap this document fills unowned:
what an uploaded blob *is*, as data another event can point to, and how the system
proves a claimed reference is real before accepting the event that makes it.

## Two representations of one media object

A single uploaded blob has two distinct shapes in this codebase, and this document
treats confusing them as the most likely reader error:

| Shape | Type | Where it lives | Fields |
|---|---|---|---|
| Persisted (sidecar) | `BlobMeta` (`crates/buzz-media/src/storage.rs`) | The community-scoped sidecar object `blossom-storage.md` documents the key shape of | `dim`, `blurhash`, `thumb_url`, `ext`, `mime_type`, `size`, `uploaded_at`, optional `duration_secs` |
| API response | `BlobDescriptor` (`crates/buzz-media/src/types.rs`) | The Blossom BUD-02 JSON body returned by `PUT /upload` and the legacy media alias | `url`, `sha256`, `size`, `mime_type` (as `type`), `uploaded`, optional `dim`, `blurhash`, `thumb`, `duration` |

`upload.rs`'s `build_descriptor` is the sole mapping from one to the other: it derives
`url` from `{sha256}.{ext}`, copies `size`/`mime_type`/`uploaded_at` across, and
converts each optional `BlobMeta` field to `BlobDescriptor`'s equivalent, collapsing
an empty string to `None`. Nothing else in this codebase constructs a
`BlobDescriptor` independently of this function.

## The `imeta` reference contract

Any Nostr event — not one specific message kind — may reference a media object by
including an `imeta` tag in its `tags` array, following NIP-92 ("Media Attachments
Metadata"), whose base field vocabulary is NIP-94 ("File Metadata") and which NIP-71
("Video Events") extends with `duration`, `bitrate`, and `image` for `video/mp4`
content. Buzz accepts twelve keys structurally
(`url`, `m`, `x`, `size`, `dim`, `blurhash`, `alt`, `thumb`, `fallback`, `duration`,
`bitrate`, `image`, `filename`) — all but `filename` trace to one of those three NIPs;
`filename` is a Buzz-specific addition for a generic file-card label, deliberately
kept out of storage keys (content-addressed, never filename-derived).

Every tag must carry `url`, `m`, `x`, and `size`; most keys may appear at most once
per tag. Before any storage lookup, `validate_imeta_tags` enforces three internal
consistency checks: the hash embedded in `url` must equal `x`; for previewable MIME
types the URL's extension must match the extension `m` implies; and a claimed `thumb`
URL's embedded hash must also equal `x`. `duration`, `bitrate`, and `image` are
rejected outright on any non-`video/mp4` tag.

## Store classification for this surface

An `imeta` reference is a **derived pointer** into the authoritative store
`blossom-storage.md` documents — it is not itself a store, a cache, or a transport
layer. The tag's fields are claims made by the event's author; nothing about the
`imeta` tag's own existence persists any bytes or metadata beyond the event it is
part of. Whether the claim is trustworthy is exactly what the next section
establishes.

## Referential integrity and consistency semantics

`verify_imeta_blobs` cross-checks every structurally valid `imeta` tag against
storage before the containing event is accepted: the sidecar for `x` must exist; the
blob object itself must exist; a claimed `m` or `size` must equal the sidecar's
stored value, and a claimed `duration` must be within 0.1 seconds of the sidecar's;
a claimed `thumb` object must exist; and a claimed `image` (poster frame) must itself
resolve to an existing, image-typed sidecar and blob. `ingest_event_inner`
(`crates/buzz-relay/src/handlers/ingest.rs`) runs `validate_imeta_tags` then, awaited,
`verify_imeta_blobs` for any event carrying at least one `imeta` tag, for any event
kind, before the event is accepted or stored.

This makes the reference check **synchronous and strict, not eventually
consistent**: an event whose `imeta` tag claims metadata the stored blob does not
back is rejected outright — the relay never stores an event alongside a media
reference it has not itself verified at ingest time. There is no repair or
reconciliation path for an event that was accepted before a referenced blob was
later deleted; that failure mode is `blossom-storage.md`'s deletion-lifecycle
concern, not this document's.

## Tenancy boundary

`verify_imeta_blobs` resolves the sidecar through the ingest pipeline's own
server-resolved `TenantContext`, never through any value derived from the `imeta` tag
being checked. Because the sidecar key is community-scoped
(`_meta/{community}/{sha256}.json`), an event in community A cannot make a validated
reference to a blob whose sidecar only exists for community B — the lookup fails the
same way a reference to a genuinely nonexistent blob does, so a cross-community
reference and a nonexistent one are indistinguishable to the author attempting it.

## Failure behavior

`IngestError`'s own doc comments state the wire behavior directly: a failed
`imeta` check (structural, via `validate_imeta_tags`, or referential, via
`verify_imeta_blobs`) maps to `IngestError::Rejected`, documented as "Client error
(bad event) — WS: `OK` false, HTTP: 400" — an ordinary NIP-01 rejection, not a server
error, and the event is never stored. This is a fail-closed gate: any one tag's
check failing rejects the whole event before later processing (thread metadata,
storage) runs.

## Scope and omissions

**This node covers** the two in-code representations of a media object
(`BlobMeta`/`BlobDescriptor`), the `imeta` tag contract an event uses to reference
one (structural shape, and the industry specs — NIP-92, NIP-94, NIP-71 — it
implements), the referential-integrity check the relay performs before accepting a
referencing event, the tenancy boundary that check inherits, and the failure
behavior on any mismatch.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The object-storage container's own existence, technology, and deployment topology | `architecture-containers-object-storage` |
| The bucket's key-namespace inventory, migration mechanism, access-pattern summary, lifecycle/retention, and failure behavior for the store itself | `blossom-storage.md` (#1067, PR #1873, not yet merged) |
| The full Blossom BUD-01/02/11 protocol (upload auth, range GET, HEAD) | `crates/buzz-media/src/auth.rs`, `crates/buzz-relay/src/api/media.rs`, the upstream Blossom spec |
| Content-addressed key derivation itself (how the sha256-based key is computed) | `content-addressing.md` (#1068, PR #1873, not yet merged) |
| What happens to `imeta` references when a referenced blob is later deleted | `blossom-storage.md`'s deletion-lifecycle section, not established here |

**Expected but not verified when this node was written:**

- **Whether any client-side code (desktop, mobile, CLI) constructs `imeta` tags
  matching this exact contract was not checked** — this document verifies the
  relay's own acceptance-time enforcement, not that every current Buzz client emits
  conforming tags.
- **Whether `verify_imeta_blobs`'s 0.1-second `duration` tolerance, or any other
  numeric tolerance in these checks, is deliberately chosen or an implementation
  default was not established** — reported as a fact of current behavior, not a
  justified design decision.
- **The relationship between this node and `blossom-storage.md`/`content-addressing.md`
  is stated only in prose, not as a schema `relationships` edge**, because neither
  target exists on `origin/launchpad` at authoring time; per `AGENTS.md`'s own
  warning, an edge that resolves in this worktree but not on the branch being merged
  into is a hard CI error, so it is deliberately omitted pending those PRs merging.
