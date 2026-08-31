---
id: capabilities-media-media
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
  - statement: "Root VISION_PROJECTS.md's own Capability/Status table lists 'Blossom media storage (SHA-256, S3)' with the status 'Ships today', the same product-level maturity marker the corpus's capability template requires a maturity claim to cite rather than assume."
    entry_class: FACT
    evidence:
      - "VISION_PROJECTS.md:252"
  - statement: "buzz-media is a library crate with no Axum dependency of its own (its own module doc says handlers live in buzz-relay), exposing auth, bucket_index, config, error, storage, thumbnail, types, upload, upload_record and validation as its public modules; buzz-relay's router mounts PUT /upload and PUT /media/upload on api::media::upload_blob, and GET/HEAD /media/{sha256_ext} on api::media::get_blob / api::media::head_blob, all three functions confirmed present at those exact routes."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/src/lib.rs"
      - "crates/buzz-relay/src/router.rs"
      - "crates/buzz-relay/src/api/media.rs"
  - statement: "The Blossom BUD-02 response type BlobDescriptor carries a url, a 64-character SHA-256 hex hash, a byte size, a MIME type, an upload timestamp, and format-specific optional fields (dim, blurhash, thumb, duration) -- one response shape shared by images, video and generic files, differentiated only by which optional fields are populated."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/src/types.rs"
  - statement: "Raw media bytes are stored as a single shared content-addressed object store keyed only by {sha256}.{ext} (buzz-media's own source comment states this explicitly), while a separate per-community sidecar record ({_meta}/{community-uuid}/{sha256}.json) is the tenant read gate -- the same physical bytes can be referenced from more than one community, but a community can only discover and serve a blob through its own sidecar, never through a bare hash lookup."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/src/storage.rs"
  - statement: "buzz-media's on-disk key taxonomy has five classes, enumerated in bucket_index.rs: blob ({sha256}.{ext}), thumb ({sha256}.thumb.jpg), sidecar (_meta/{community}/{sha256}.json), auxiliary (_uploads/{community}/{sha256}/{ulid}.json, an optional moderation record), and a deliberate Unknown catch-all for anything that fits none of the first four -- never silently folded into another class."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/src/bucket_index.rs"
  - statement: "MediaConfig documents per-content-type upload size ceilings in its own field doc comments -- 50 MB for images, 10 MB for animated GIFs (validated at startup to be no larger than the image ceiling), 500 MB for video (the only one with a literal code default, 524_288_000 bytes), and 100 MB for generic files (also code-defaulted, 104_857_600 bytes) -- so the capability distinguishes at least three upload variants (image, video, generic file) by distinct size and validation rules rather than treating all uploads identically."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/src/config.rs"
  - statement: "A signed Blossom (BUD-11) kind:24242 authorization event is required on both the write path (PUT /upload, PUT /media/upload) and the read path (GET/HEAD /media/{sha256_ext}) -- there is no configuration flag that admits an unauthenticated request on either path -- and relay membership (NIP-43) is enforced as a separate, later check against the community bound by the request's Host header."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/src/auth.rs"
      - "crates/buzz-relay/src/api/media.rs"
  - statement: "A client attaches previously uploaded media to a chat message by adding one or more NIP-92 imeta tags to the message event; the relay's shared imeta-tag validator restricts each tag to a fixed key set (url, m, x, size, dim, blurhash, alt, thumb, fallback, duration, bitrate, image, filename), enforces several keys as singleton (at most one occurrence per tag), and is invoked identically from both the REST send_message path and the WebSocket handle_event path -- one validation rule regardless of transport."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/imeta.rs"
  - statement: "buzz-cli exposes attaching a file to a channel message as a `--file` flag on its message-send command, documented in its own help text as 'Attach file(s) -- uploads and includes as imeta tags' -- confirming the CLI-driven path from a local file to an uploaded, message-linked attachment is implemented, not merely designed."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/lib.rs"
  - statement: "buzz-core's kind registry defines KIND_FILE_METADATA = 1063 (NIP-94), and root VISION_PROJECTS.md's own Nostr-kind mapping table separately lists '1063 (NIP-94)' against the row 'Artifacts -- Build outputs on Blossom/S3'; no call site constructing or handling a kind-1063 event was found anywhere under crates/ in a repository-wide search for the constant's name, so this second, standalone-event mechanism for referencing a Blossom blob is declared but not confirmed wired into any handler at this revision, unlike the imeta-tag mechanism above."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
      - "VISION_PROJECTS.md:234"
  - statement: "Three integration test files under crates/buzz-test-client/tests/ are named for media coverage -- e2e_media.rs, e2e_media_extended.rs, e2e_media_video.rs -- confirmed present in the repository at this revision by directory listing; their individual assertions are not restated here because the upload and download flow nodes this document references already cite specific test functions within them."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/e2e_media.rs"
      - "crates/buzz-test-client/tests/e2e_media_extended.rs"
      - "crates/buzz-test-client/tests/e2e_media_video.rs"
  - statement: "Issue #769 requires this node to state the capability and its primary actors/outcomes, define behavioral rules/constraints/variants, link major flows/interfaces/data/platform implementation, and link verification demonstrating the capability, while keeping this document to the bare overview and leaving attachment-authorization, blossom, content-hash, download, imeta, media-metadata and upload as separate sibling capability documents this node does not duplicate."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#769 definition of done"
relationships:
  - type: references
    target: architecture-flows-media-upload
  - type: references
    target: architecture-flows-media-download
  - type: references
    target: architecture-containers-object-storage
  - type: implements
    target: corpus-template-capability
---

# Media: capability

Buzz lets a human or agent attach a file -- an image, a video, or an arbitrary
generic file -- to a channel message, and later retrieve it, without any of that
content ever being written into a Nostr event body directly. The file's bytes are
uploaded once to a content-addressed, Blossom-protocol-compatible object store
(SHA-256 keyed, backed by S3-compatible storage), and the message that carries it
holds only a compact pointer -- a NIP-92 `imeta` tag naming the URL, hash and
format metadata -- so the same message-delivery, threading and moderation
machinery that already handles text handles an attachment too. The primary
actors are the uploading/sending party (human or agent, via desktop, `buzz-cli`,
or any other client that can sign a Blossom event) and the eventual reader who
resolves the `imeta` pointer back to bytes; the outcome for both is a piece of
media that is durably stored once, servable to every authorized member of the
community it was shared into, and never duplicated per-message the way an
inline data URL would be.

## Maturity

**Shipped.** Root `VISION_PROJECTS.md`'s own Status table lists "Blossom media
storage (SHA-256, S3)" as "Ships today" (`VISION_PROJECTS.md:252`), and the
underlying code confirms it: `buzz-relay` mounts working `PUT /upload`,
`PUT /media/upload`, and `GET`/`HEAD /media/{sha256_ext}` routes
(`crates/buzz-relay/src/router.rs`) backed by `buzz-media`'s upload, storage and
validation modules, with three named integration-test files exercising the
result end to end (`crates/buzz-test-client/tests/e2e_media*.rs`). The
message-attachment path (a client adding an `imeta` tag to a chat message) is
also shipped: the relay validates `imeta` tags identically on both the REST and
WebSocket ingestion paths (`crates/buzz-relay/src/handlers/imeta.rs`), and
`buzz-cli` exposes it directly as a `--file` flag on its message-send command.
**Not confirmed wired in:** a second, standalone way to reference a blob as its
own event -- Nostr kind `1063` (NIP-94), which `buzz-core` declares as a named
constant and `VISION_PROJECTS.md`'s Nostr-kind table associates with "Artifacts
-- Build outputs on Blossom/S3" -- has no call site constructing or handling
such an event anywhere under `crates/` at this revision; see *Scope and
omissions* below.

## Boundary

This node states what the media capability fundamentally is and does not
re-derive the depth its sibling capability documents own:

- **How a blob is authorized and admitted on write, and the exact ordered
  admission checks, are not repeated here** -- see the `upload` capability
  document and the referenced `architecture-flows-media-upload` node for the
  full write-path sequence (host-to-tenant binding, Blossom auth, hash
  re-verification, storage write, sidecar gate).
- **How a blob is authorized and served on read, including range requests and
  content-type resolution, are not repeated here** -- see the `download`
  capability document and the referenced `architecture-flows-media-download`
  node.
- **The Blossom (BUD-11) authorization-event shape and the general Blossom
  protocol contract are not restated here** -- see the `blossom` and
  `attachment-authorization` capability documents.
- **What a SHA-256 content hash guarantees, and how the capability relies on
  it for deduplication and integrity, are not elaborated here** -- see the
  `content-hash` capability document.
- **The `imeta` tag's exact key set, singleton rules, and how it is validated
  are named above only as evidence for this capability's existence, not
  explained in full** -- see the `imeta` capability document.
- **The sidecar record's full schema and what per-blob metadata it carries
  are not detailed here** -- see the `media-metadata` capability document.
- **How the capability is built** -- the S3-compatible storage client, its
  credential resolution, and the bucket key taxonomy -- is architecture, not
  capability, content; see `architecture-containers-object-storage`.
- **How the running system operates the media store** -- the hourly storage
  sweep, metrics, and the `BUZZ_STORAGE_METRICS` kill switch -- is an
  operations concern, out of scope for a capability node.

## Relationships

- `references architecture-flows-media-upload` -- the write-path flow that
  realizes this capability's upload half.
- `references architecture-flows-media-download` -- the read-path flow that
  realizes this capability's retrieval half.
- `references architecture-containers-object-storage` -- the storage
  container the capability is built on.
- `implements corpus-template-capability` -- this node follows that template's
  required sections (capability statement, maturity, boundary, relationships,
  scope and omissions).

No `relationships` target any of this capability's sibling documents
(attachment-authorization, blossom, content-hash, download, imeta,
media-metadata, upload) -- those are separate tasks in the same batch as this
one and do not yet exist as merged corpus nodes, so none of their ids would
resolve. Each is named in prose above, in *Boundary*, per the corpus's own
linking standard: a real connection that cannot yet be declared as an edge is
still worth stating in prose.

## Scope and omissions

**This node covers** what the media capability fundamentally is: a
content-addressed, Blossom-compatible attachment mechanism letting a human or
agent upload a file once and reference it from a chat message via an `imeta`
tag; its primary actors and outcomes; its shipped maturity, cited to code and
to `VISION_PROJECTS.md`; the variants it distinguishes (image, video, generic
file, each with its own size ceiling); the community-scoped read gate that
sits on top of a single shared content-addressed store; and pointers to the
flows, architecture and verification that realize and demonstrate it.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The upload write path's full admission sequence and failure modes | `architecture-flows-media-upload`, and the `upload` capability document (issue #768 / #770, whichever the batch assigns) |
| The download read path's full admission sequence and range/byte-serving behavior | `architecture-flows-media-download`, and the `download` capability document |
| The Blossom (BUD-11) protocol and authorization-event contract in full | The `blossom` and `attachment-authorization` capability documents |
| What a SHA-256 content hash establishes and how deduplication relies on it | The `content-hash` capability document |
| The `imeta` tag's full key set, validation rules and NIP-92 background | The `imeta` capability document |
| The per-blob sidecar metadata record's schema | The `media-metadata` capability document |
| How the S3-compatible object store is provisioned, credentialed and addressed | `architecture-containers-object-storage` |
| Operating the media store in production (the storage sweep, metrics, kill switches) | The `operations` corpus surface, not yet documented |
| The exact BUD-11/BUD-02 wire specification text | Not opened for this node; only Buzz's own code enforcing it was read |
| Mobile and CLI download call sites beyond `buzz-cli`'s upload/attach flag | Not inspected for this node |

**Expected but not verified when this node was written:**

- **Whether Nostr kind `1063` (NIP-94) is used anywhere in this codebase as a
  standalone artifact-reference event.** `buzz-core` declares the constant and
  `VISION_PROJECTS.md` associates it with build-artifact attachments, but a
  repository-wide search for the constant's name under `crates/` found no
  handler or builder using it. This node does not claim the mechanism is
  shipped, only that the `imeta`-tag mechanism is.
- **Whether the sibling capability documents this node's Boundary section
  names (`attachment-authorization`, `blossom`, `content-hash`, `download`,
  `imeta`, `media-metadata`, `upload`) will use exactly those ids once
  authored.** This node names them descriptively, from the batch's own task
  titles, not from reading their (not-yet-existing) front matter.
- **Live execution of the upload/download/attach flow was not performed for
  this node.** It is based on reading source and the named test files, not on
  running the test suite or a live relay as part of authoring it.
