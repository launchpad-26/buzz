---
id: capabilities-media-imeta
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
  - statement: "`validate_imeta_tags` (shared by the REST and WebSocket ingest paths) requires every tag in a `media_tags` slice to be an `imeta` tag, allows only a fixed set of keys (`url`, `m`, `x`, `size`, `dim`, `blurhash`, `alt`, `thumb`, `fallback`, `duration`, `bitrate`, `image`, `filename`), rejects any other key, rejects a repeated singleton key, and requires `url`, `m`, `x` and `size` to all be present — stricter than a bare parse of the tag."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/imeta.rs"
  - statement: "`validate_imeta_tags` further cross-checks internal consistency before accepting a tag: the `url` must be a local `/media/` path whose embedded hash matches `x` and whose extension matches the MIME-derived extension for previewable MIME types; `thumb`, if present, must be a local `.thumb.jpg` path whose hash also matches `x`; and the NIP-71 video-only fields `duration`, `bitrate` and `image` are rejected outright unless `m` is exactly `video/mp4`."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/imeta.rs"
  - statement: "`verify_imeta_blobs` is a second, storage-backed check run after `validate_imeta_tags`: for each tag's `x` hash it requires a sidecar record to exist, HEADs the actual blob object in storage, and rejects the tag if the claimed `m`, `size` or `duration` disagree with the sidecar's own recorded values; if `thumb` or `image` (poster frame) is present it separately HEADs that object and, for `image`, requires the poster's stored MIME to be an image type and its stored extension to match the URL."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/imeta.rs"
  - statement: "Both `validate_imeta_tags` and `verify_imeta_blobs` are called from two independently-reached ingestion paths — the shared `ingest_event_inner` function behind both the WebSocket and REST `POST /events` bridges (`ingest_event` is documented as the seam where the two transports are counted identically), and the separate product-feedback (`kind 42000`) handler that persists outside ordinary event storage — and in both call sites the check runs whenever the event's own tags contain one or more `imeta` tags, with no gate on the event's kind."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:1881-1899"
      - "crates/buzz-relay/src/handlers/ingest.rs:2745-2764"
      - "crates/buzz-relay/src/handlers/product_feedback.rs:16-34"
  - statement: "`buzz-sdk`'s `imeta_tags` helper takes raw `Vec<Vec<String>>` tag vectors and emits each, unmodified, as a parsed `Tag` via `Tag::parse`; it is called from `build_message` (kind 9, the NIP-29 stream message), `build_forum_post` (kind 45001) and `build_forum_comment` (kind 45003), so imeta attachment is available on chat messages, forum posts and forum replies through the same shared helper."
    entry_class: FACT
    evidence:
      - "crates/buzz-sdk/src/builders.rs:207-245"
      - "crates/buzz-sdk/src/builders.rs:284-316"
  - statement: "`buzz-cli`'s `build_imeta_tag` constructs one `imeta` tag array from a `BlobDescriptor` per its own doc comment ('NIP-92 media metadata'), always emitting `url`, `m`, `x` and `size` and conditionally appending `dim`, `blurhash`, `thumb` and `duration` when the descriptor carries them; the `messages send` command calls it once per uploaded file and, for each attachment, also appends a matching `![image](url)` or `![video](url)` markdown line to the outgoing message content so the two representations (imeta tag and rendered markdown) name the same URL."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/client.rs:39-61"
      - "crates/buzz-cli/src/commands/messages.rs:613-634"
  - statement: "Desktop's `parseImetaTags` parses a raw Nostr event's tag array into a `Map` of structured entries keyed by the tag's own `url` value, recognizing the same field set the relay validates (`url`, `m`, `x`, `size`, `dim`, `blurhash`, `alt`, `thumb`, `duration`, `image`, `filename`); `mediaEntry.ts`'s `isVideoMedia` then treats the parsed `m` (MIME) field as authoritative for choosing the image-versus-video render path, and falls back to the URL's own path extension only when no imeta MIME is present (a legacy event predating the tag)."
    entry_class: FACT
    evidence:
      - "desktop/src/shared/ui/markdown/parseImeta.ts"
      - "desktop/src/shared/ui/markdown/mediaEntry.ts:33-48"
  - statement: "A code comment in `desktop/src/features/messages/lib/imetaMediaMarkdown.ts` documents that NIP-92 itself treats every imeta field except `url` as optional (naming `url` and `m` as NIP-92's only de-facto required fields), while Buzz's own relay validator additionally requires `x` and `size` to be present and rejects an empty `x`/`size 0` — the composer's outgoing-tag builder (`buildImetaTags`) therefore emits `x` and `size` only when the attachment actually carries them, to stay compatible with legacy or cross-client imeta entries that lack a hash or size."
    entry_class: FACT
    evidence:
      - "desktop/src/features/messages/lib/imetaMediaMarkdown.ts:77-105"
  - statement: "The same file documents that edit events (kind 40003) carry only the new `content`, with imeta tags living on the original event; the composer's edit mode overlays the edit's full replacement imeta tag set onto the rendered message, and — because `BlobDescriptor` (the shape the composer's attachment state uses) does not carry NIP-92's `alt`, `fallback` or `service` fields — an edit made through Buzz's own composer silently drops those fields from the saved tag set if the original event carried them from another client."
    entry_class: FACT
    evidence:
      - "desktop/src/features/messages/lib/imetaMediaMarkdown.ts:1-51"
  - statement: "The capability is exercised by both unit and end-to-end tests: `crates/buzz-relay/src/handlers/imeta.rs`'s own unit tests cover accepted well-formed tags, a hash-mismatch rejection, generic-file attachments with a `filename`, an `application/octet-stream` file, a path-separator injection in `filename`, and a malformed-MIME rejection; `crates/buzz-test-client/tests/e2e_media_video.rs`'s `test_video_poster_imeta_accepted_via_ws` and `test_video_poster_imeta_rejects_video_as_poster` and `crates/buzz-test-client/tests/e2e_media_extended.rs`'s `test_ws_valid_imeta`, `test_ws_invalid_imeta_external_url` and `test_ws_invalid_imeta_missing_fields` exercise the same validation over a live WebSocket connection."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/imeta.rs:468-643"
      - "crates/buzz-test-client/tests/e2e_media_video.rs:499-679"
      - "crates/buzz-test-client/tests/e2e_media_extended.rs:598-802"
  - statement: "Mobile (`mobile/lib/features/channels/message_media.dart`, `message_content/media_carousel.dart`, `message_content/video_preview.dart`, `timeline_message.dart`, `message_content.dart` and `shared/relay/media_upload.dart`) references `imeta` in at least six files, indicating the capability is also implemented on the Flutter client, but none of those files were opened for this node — this is recorded as a gap in *Scope and omissions*, not as a verified claim about mobile's behavior."
    entry_class: FACT
    evidence:
      - "grep_imeta(path='mobile/lib', ref='338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5') -> message_media.dart, message_content/media_carousel.dart, message_content/video_preview.dart, timeline_message.dart, message_content.dart, shared/relay/media_upload.dart"
---

# imeta media metadata tagging: capability

Buzz lets a client attach structured metadata for one or more pieces of media — an
uploaded image, video, generic file, or a linked poster frame — directly to the Nostr
event carrying a message, using a `imeta` tag per NIP-92 media-metadata convention. A
user or agent can therefore send a message that both displays inline media and lets
every recipient (and the relay itself) verify what that media actually is — its hash,
MIME type, size, and dimensions/duration where applicable — without a side-channel
lookup back to the upload response.

## Maturity

Shipped. The relay enforces both a structural shape check (`validate_imeta_tags`) and
a storage-backed cross-check (`verify_imeta_blobs`) on every ingested event carrying
`imeta` tags, `buzz-sdk` and `buzz-cli` both build compliant tags for outgoing
messages, and the desktop client parses, renders, and round-trips them through editing.
Unit tests in `crates/buzz-relay/src/handlers/imeta.rs` and end-to-end WebSocket tests
in `crates/buzz-test-client/tests/e2e_media_video.rs` and
`e2e_media_extended.rs` exercise the accept and reject paths against a live relay.

## Boundary

This node does not describe:

- **How the referenced media itself is uploaded or served.** That is the media-upload
  and media-download flows (`architecture-flows-media-upload`,
  `architecture-flows-media-download`) — this node only covers the tag that
  *describes* already-stored media on a message event, not the Blossom upload/download
  HTTP contract those flows document.
- **The CLI's or relay's specific command/route boundary for attaching media.** No
  interface node exists yet for `buzz-cli`'s `messages send --attach` flag or the
  REST/WebSocket event-submission surface; this node describes the tag contract those
  surfaces both produce and consume, not the surfaces themselves.
- **The step-by-step sequence of uploading a file and then sending a message that
  references it.** That sequence-level narrative belongs to a flow node, not to this
  capability node, which states only that the capability exists and what its tag
  contract guarantees.
- **How the running relay is operated, deployed, or monitored.** Not in scope for a
  capability node per `templates/capability.md`.

## Relationships

- references: architecture-flows-media-upload
- references: architecture-flows-media-download

## Scope and omissions

**This node covers** the `imeta` tag's field contract as the relay validates it, the
storage-backed cross-check that runs after structural validation, the two independent
ingestion paths that both invoke that validation whenever an event carries `imeta`
tags, the event kinds `buzz-sdk` currently attaches it to (stream messages, forum
posts, forum comments), how `buzz-cli` and the desktop composer each build and parse
the tag, the desktop renderer's authoritative use of the tag's `m` field to choose an
image versus video render path, and one documented divergence between what NIP-92
itself requires and what Buzz's own relay validator additionally demands.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The Blossom upload/download HTTP contract that produces the blob an `imeta` tag describes | `architecture-flows-media-upload`, `architecture-flows-media-download` |
| A dedicated interface node for the CLI flag or HTTP/WebSocket surface that carries `imeta` tags | not yet drafted |
| The step-by-step flow of attaching media to an outgoing message | not yet drafted (flow node) |
| Mobile's (`mobile/lib/**`) own `imeta` handling | not inspected for this node — see below |
| The NIP-92 specification text itself | not opened directly; the divergence claim above is sourced from Buzz's own code comment describing it, not from reading the spec |

**Expected but not verified when this node was written:**

- **Mobile's `imeta` implementation was not inspected.** A `grep` located six files
  under `mobile/lib` referencing `imeta` (see the evidence ledger), confirming the
  capability is at least referenced on the Flutter client, but none of those files
  were opened, so no claim is made here about how mobile builds, parses, or renders
  the tag.
- **NIP-92's actual specification text was not read.** Every claim above about what
  NIP-92 "requires" or treats as "optional" is sourced from a Buzz code comment
  (`desktop/src/features/messages/lib/imetaMediaMarkdown.ts`) that describes the spec,
  not from opening `nostr-protocol/nips` directly.
- **Whether any event kind besides stream messages, forum posts and forum comments
  emits `imeta` tags via a path other than `buzz-sdk`'s three builders** was not
  searched for beyond the two ingestion call sites cited above; the product-feedback
  path validates `imeta` tags but this node did not confirm whether any client
  actually attaches them to a feedback event.
