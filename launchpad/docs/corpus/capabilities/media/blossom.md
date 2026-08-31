---
id: capabilities-media-blossom
type: capabilities
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
  - statement: "Root VISION_PROJECTS.md's Status table lists 'Blossom media storage (SHA-256, S3)' with the marker '✅ Ships today', naming it as a shipped, user-facing capability rather than an in-progress or designed one."
    entry_class: FACT
    evidence:
      - "VISION_PROJECTS.md:252"
  - statement: "Root AGENTS.md's repo-structure table describes buzz-media as 'Blossom/S3 media storage', a leaf crate distinct from the core event-store stack (buzz-db, buzz-auth, buzz-pubsub, buzz-search, buzz-audit, buzz-workflow)."
    entry_class: FACT
    evidence:
      - "AGENTS.md"
  - statement: "crates/buzz-relay/src/api/media.rs's own module header enumerates exactly three HTTP routes implementing the capability: PUT /upload (labeled 'BUD-02 exact-byte upload', auth required), PUT /media/upload (labeled a temporary media-only legacy alias), GET /media/{sha256_ext} (labeled 'BUD-01 serve blob'), and HEAD /media/{sha256_ext} (labeled 'BUD-01 existence check')."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/media.rs:1-7"
  - statement: "crates/buzz-media/src/auth.rs is headed '//! Blossom kind:24242 auth verification (BUD-11 compliant)' and its verify_blossom_get_auth doc comment states 'BUD-01 permits either blob-scoped authorization (x tag matches sha256) or server-scoped authorization (server tag matches this relay host)', confirming the auth layer implements BUD-11 (authorization events) in service of the BUD-01 read/exists surface."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/src/auth.rs:1"
      - "crates/buzz-media/src/auth.rs:201-206"
  - statement: "crates/buzz-media/src/types.rs is headed '//! Blossom BUD-02 response types' and defines BlobDescriptor (url, sha256, size, mime_type, uploaded, plus optional dim/blurhash/thumb/duration) as the JSON shape returned by PUT /upload and the legacy media alias, matching BUD-02's upload-response contract."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/src/types.rs"
  - statement: "A grep of crates/buzz-media and crates/buzz-relay/src/api/media.rs and router.rs for 'mirror' and 'list' found no PUT /mirror route, no GET /list/{pubkey} route, and no server-side implementation of Blossom's mirror or list-blobs-by-pubkey operations; the only 'mirror' hit is an unrelated code comment in upload_record.rs about mirroring a data structure's own versioning, not the Blossom BUD-04 protocol operation. No DELETE route for a blob was found either."
    entry_class: FACT
    evidence:
      - "grep_case_insensitive('mirror', path='crates/buzz-media/', 'crates/buzz-relay/src/api/media.rs', 'crates/buzz-relay/src/router.rs') -> one unrelated hit, crates/buzz-media/src/upload_record.rs:340"
      - "grep_case_insensitive('delete', path='crates/buzz-relay/src/router.rs', 'crates/buzz-relay/src/api/media.rs') -> no route registration"
  - statement: "Content is addressed by its own SHA-256 hash: crates/buzz-media/src/types.rs's BlobDescriptor carries a sha256 field, and every upload/download path this node's referenced flow and architecture nodes describe keys the underlying S3-compatible object by {sha256}.{ext} (or a bare 64-character hex hash), never by a client-chosen name."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/src/types.rs"
      - "crates/buzz-relay/src/api/media.rs"
  - statement: "The capability's upload, download, and object-storage implementation, authentication/authorization ordering, failure-status mapping, and deployment/security implications are already documented in three corpus nodes merged on origin/launchpad (architecture-flows-media-upload, architecture-flows-media-download, architecture-containers-object-storage); this node references rather than restates them, per AGENTS.md's evidence guidance against duplicating an architecture or flow node's own content inside a capability node."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/architecture/flows/media-upload.md"
      - "launchpad/docs/corpus/architecture/flows/media-download.md"
      - "launchpad/docs/corpus/architecture/containers/object-storage.md"
      - "launchpad/docs/corpus/AGENTS.md"
    confidence: 0.9
---

# Blossom media storage: capability

Buzz lets a user or agent upload a file (image, animated GIF, video, or other
attachment) to a community's blob store and later retrieve it by content
hash, using a Blossom-compatible (`kind:24242` / BUD-11) HTTP surface layered
on an S3-compatible object store. A message can then embed a stable,
tenant-scoped URL to that blob — the capability VISION_PROJECTS.md's own
Status table names "Blossom media storage (SHA-256, S3)".

## Maturity

**Shipped.** VISION_PROJECTS.md's Status table marks "Blossom media storage
(SHA-256, S3)" `✅ Ships today`. The relay's own module header
(`crates/buzz-relay/src/api/media.rs:1-7`) enumerates the live routes —
`PUT /upload`, `PUT /media/upload` (legacy alias), `GET /media/{sha256_ext}`,
`HEAD /media/{sha256_ext}` — and `crates/buzz-test-client/tests/e2e_media.rs`
and `e2e_media_extended.rs` exercise them end to end (cited in full by
`architecture-flows-media-upload` and `architecture-flows-media-download`,
not repeated here).

**Partial against the wider Blossom protocol.** The code's own doc comments
name the specs it implements: BUD-01 (serve/exists), BUD-02 (upload,
including `BlobDescriptor`'s response shape), and BUD-11 (the `kind:24242`
authorization event). A direct search of `crates/buzz-media` and the relay's
media router found no `mirror` route (BUD-04) and no list-blobs-by-pubkey
route — Buzz's Blossom surface today covers upload, download/exists, and
auth, not the full multi-server mirroring or discovery operations some
Blossom deployments support elsewhere.

## Boundary

This node does not describe:
- **How the capability is built.** The S3-compatible storage client, the
  `buzz-media`/`buzz-relay` ownership split, credential resolution, and the
  bucket key taxonomy are the architecture container's territory — see
  `architecture-containers-object-storage`.
- **The interface(s) the capability is exposed through.** The exact HTTP
  request/response contract, header-by-header auth verification order, and
  status-code mapping are covered by the two flow nodes below, not restated
  here.
- **The step-by-step flow through this capability.** `architecture-flows-media-upload`
  and `architecture-flows-media-download` already narrate the ordered
  interactions, trust-boundary crossings, and failure/rollback behavior for
  upload and download respectively; this node states only that the
  capability exists and what it lets a user or agent do.
- **How it's operated.** Bucket provisioning, the hourly storage-usage sweep,
  and staging/production deployment topology belong to the `operations`
  corpus surface and to `architecture-containers-object-storage`'s own
  *Deployment implications* section.
- **Mirror, delete, and list-by-pubkey Blossom operations**, because they are
  not implemented server-side today (see *Maturity* above) — there is
  nothing yet to document for them.

## Relationships

- references: architecture-containers-object-storage
- references: architecture-flows-media-upload
- references: architecture-flows-media-download

## Scope and omissions

**This node covers** what the Blossom media capability lets a user or agent
do, its shipped/partial maturity against the BUD-01/BUD-02/BUD-11 specs the
code itself names, and an explicit boundary against the architecture,
interface, and flow documents that already own the how.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| How the capability is built (storage client, ownership split, key taxonomy, credentials) | `architecture-containers-object-storage` |
| The ordered HTTP contract, trust-boundary crossings, and failure mapping for upload | `architecture-flows-media-upload` |
| The ordered HTTP contract, trust-boundary crossings, and failure mapping for download | `architecture-flows-media-download` |
| How the running system is operated (bucket provisioning, the storage-usage sweep, staging/production topology) | the `operations` corpus surface; `architecture-containers-object-storage`'s *Deployment implications* |
| The full external Blossom/BUD specification text | the upstream Blossom spec, not read directly for this node (see below) |

**Expected but not verified when this node was written:**

- **The external BUD-01/BUD-02/BUD-04/BUD-11 specification text itself was
  not fetched or read.** This node's BUD labeling is taken entirely from the
  Buzz codebase's own doc comments (`crates/buzz-relay/src/api/media.rs`,
  `crates/buzz-media/src/auth.rs`, `crates/buzz-media/src/types.rs`), not
  from comparing those comments against the upstream Blossom BUD documents at
  `github.com/hzrd149/blossom` — the same gap `architecture-flows-media-upload`
  already discloses for BUD-11.
- **Whether mirror or list-by-pubkey support exists on any client
  (desktop/mobile/CLI) independent of the relay.** Only the relay's own
  routes were searched; a client-side implementation that calls a
  *different*, non-Buzz Blossom server for mirroring was not investigated,
  because it would be out of scope for this relay-capability node either way.
- **Whether a `DELETE` capability is planned but unimplemented, versus
  intentionally out of scope.** No code comment, VISION document, or open
  issue naming a planned delete route was found in the sources opened for
  this node.
