---
id: capabilities-messaging-attachments
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
  - statement: "`buzz-sdk`'s `build_message` (Nostr kind 9, `KIND_STREAM_MESSAGE`), `build_forum_post` (kind 45001) and `build_forum_comment` (kind 45003) each take a `media_tags: &[Vec<String>]` parameter and pass it through a shared private `imeta_tags` helper that parses each entry into a `Tag` and appends it to the outgoing event — so attaching media is available uniformly on stream messages, forum posts and forum replies through the same builder-level mechanism, not three separate implementations."
    entry_class: FACT
    evidence:
      - "crates/buzz-sdk/src/builders.rs:207-245"
      - "crates/buzz-sdk/src/builders.rs:284-298"
      - "crates/buzz-core/src/kind.rs:479"
  - statement: "`buzz-cli`'s `messages send` subcommand exposes a repeatable `--file` flag (`files: Vec<String>`, `#[arg(long = \"file\")]`), documented in its own help text as \"Attach file(s) — uploads and includes as imeta tags\"."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/lib.rs:392-394"
  - statement: "`cmd_send_message` loops over every `--file` path, uploads each one via `BuzzClient::upload_file`, builds one imeta tag per upload with `build_imeta_tag`, and additionally appends a `![image](url)` or `![video](url)` markdown line to the message content for the same file — so a CLI attachment is represented twice on the outgoing event: once as a structured imeta tag and once as inline markdown naming the same URL. This loop runs before the event is handed to whichever of `build_message`/`build_forum_post`/`build_forum_comment` the caller's `--kind` selects, so the attach behavior is identical across all three message kinds."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/commands/messages.rs:564-570"
      - "crates/buzz-cli/src/commands/messages.rs:613-634"
  - statement: "`BuzzClient::upload_file` enforces a client-side allowlist before ever contacting the relay: only `image/jpeg`, `image/png`, `image/gif`, `image/webp` and `video/mp4` (sniffed from magic bytes via `infer`, not the file extension) are accepted, anything else is rejected with a `CliError::Usage` naming the unsupported MIME type, and a size cap (50 MB for images, 500 MB for video) is checked against the same MIME-derived branch — so the CLI's own attach capability is narrower than the server's upload pipeline, which separately supports a generic-file branch this client never reaches."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/client.rs:64-70"
      - "crates/buzz-cli/src/client.rs:72-76"
      - "crates/buzz-cli/src/client.rs:1100-1123"
  - statement: "Desktop's composer supports attaching a file two ways beyond the CLI's fixed MIME allowlist: a native multi-select file picker (`useFilePicker`, a single reused hidden `<input type=\"file\">` whose `value` is reset before and after each pick so re-selecting the same file still fires `change`) and whole-form drag-and-drop, gated on the drag payload actually carrying files (`isFileDrag` checks `dataTransfer.types` for `\"Files\"`) and visually indicated by a dashed-border `DropZoneOverlay` while dragging."
    entry_class: FACT
    evidence:
      - "desktop/src/features/messages/lib/useFilePicker.ts"
      - "desktop/src/features/messages/ui/ComposerAttachments.tsx:53-83"
  - statement: "Desktop's `ComposerAttachments` renders three distinct shapes for a resolved attachment depending on its MIME type: an image or video gets an image thumbnail or a poster-framed lightbox-capable thumbnail; anything else (`isFile = !isVideo && !isImage`) renders as a compact chip with a generic file icon and filename and no lightbox, because — per the component's own comment — there is nothing to preview. This is the desktop-side counterpart of the CLI's narrower MIME allowlist: desktop can attach and display a generic file that the CLI's own `--file` flag would reject outright."
    entry_class: FACT
    evidence:
      - "desktop/src/features/messages/ui/ComposerAttachments.tsx:609-663"
  - statement: "For a video file, desktop captures a client-side poster frame before/independent of the network upload: `captureVideoPosterFrame` loads the file into an off-DOM `<video>` element, seeks to roughly 0.1s (or the earliest available frame for very short clips), draws that frame to an in-memory `<canvas>` capped at a 640px maximum width, and encodes it as a JPEG at quality 0.82 — used as the queued-preview poster and, once uploaded, as the attachment's `image`/`thumb` fallback in the lightbox."
    entry_class: FACT
    evidence:
      - "desktop/src/features/messages/lib/useMediaUpload.ts:90-153"
  - statement: "Desktop's upload lifecycle reserves a numbered preview slot per attachment up front (`reserveSlots`/`fillSlot`), surfaces byte-level progress by listening for a Tauri `media-upload-progress` event correlated to the preview via a per-id string (`uploadProgressId`), and lets an in-flight upload be cancelled by that same preview id — all independently of network completion order, which unit tests exercise directly by asserting that concurrent uploads completing out of order still fill their originally reserved slot positions."
    entry_class: FACT
    evidence:
      - "desktop/src/features/messages/lib/useMediaUpload.ts:48-51"
      - "desktop/src/features/messages/lib/useMediaUpload.ts:190-234"
      - "desktop/src/features/messages/lib/useMediaUpload.test.mjs:53-79"
  - statement: "An `uploadEpochRef` counter increments whenever the composer's whole attachment set is replaced wholesale — a draft or channel switch, a post-send clear, or restoring an edit — and an upload that captured an earlier epoch at start time is discarded on completion rather than filling a slot in the newly-current draft; a queued preview from a stale epoch is likewise a no-op to cancel. Unit tests assert this directly by name: \"upload completing after a draft switch is discarded\", \"stale upload cannot overwrite a slot the new draft already filled\", and \"cancelling a stale preview does not null the new draft's slot\"."
    entry_class: FACT
    evidence:
      - "desktop/src/features/messages/lib/useMediaUpload.ts:226-234"
      - "desktop/src/features/messages/lib/useMediaUpload.test.mjs:161-186"
      - "desktop/src/features/messages/lib/useMediaUpload.test.mjs:217-223"
  - statement: "An already-uploaded, non-video attachment can be annotated with freehand drawing in a lightbox editor (`ComposerImageEditor`, opened via a \"Draw on image\" action gated to `!isVideo`); saving uploads the annotated bytes as a replacement blob through `uploadEditedAttachment` and swaps the attachment's URL to the new one, while the pre-edit original is retained so the attachment can be reverted in place via `onRevert` without losing the original bytes."
    entry_class: FACT
    evidence:
      - "desktop/src/features/messages/ui/ComposerAttachments.tsx:278-320"
      - "desktop/src/features/messages/lib/useAttachmentEditing.ts"
  - statement: "An image or video attachment (queued or already uploaded) can be toggled as a \"spoiler\", which blurs its thumbnail and expanded view behind a glyph until interacted with; spoiler membership is tracked by the attachment's own URL and is explicitly migrated from the old URL to the new one when an edit replaces that URL, so an edited spoilered image stays spoilered rather than silently losing the flag."
    entry_class: FACT
    evidence:
      - "desktop/src/features/messages/ui/ComposerAttachments.tsx:366-373"
      - "desktop/src/features/messages/ui/ComposerAttachments.tsx:463-489"
      - "desktop/src/features/messages/lib/useAttachmentEditing.ts:23-42"
  - statement: "An attached file whose filename ends in `.agent.png`, `.agent.json`, `.team.png` or `.team.json` and whose `sha256` is a full 64-character hash is detected by `getSnapshotKind` and rendered as a distinct \"snapshot card\" (an agent- or team-labeled icon chip, with an inline thumbnail for `.agent.png`) instead of the generic media-thumbnail or file-chip treatment every other attachment gets — a special-cased attachment variant layered on top of the general capability."
    entry_class: FACT
    evidence:
      - "desktop/src/features/messages/ui/ComposerAttachments.tsx:114-213"
  - statement: "`useMediaUpload` accepts a `deferUploadsUntilSend` option that, for video files specifically (`shouldQueueFile` checks `isVideoFile`), queues the file locally instead of starting the network upload immediately on selection — gated additionally by an E2E mock flag (`__BUZZ_E2E__.mock.deferredComposerUploads`) so this deferred path can be forced on or off under test."
    entry_class: FACT
    evidence:
      - "desktop/src/features/messages/lib/useMediaUpload.ts:155-174"
  - statement: "At the recorded revision, `origin/launchpad`'s corpus tree carries no `capabilities/` subtree at all — checked directly against the merge target rather than this worktree's own branch — so no imeta-tag wire-contract node or sibling messaging-capability node exists yet on `origin/launchpad` for this node to `references`. `architecture/containers/desktop.md`, `architecture/containers/cli.md`, `architecture/flows/media-upload.md` and `architecture/flows/media-download.md` are merged and are the nodes this capability's own implementation and its read-back path touch most directly."
    entry_class: FACT
    evidence:
      - "git_ls_tree(ref='origin/launchpad', path='launchpad/docs/corpus') -> AGENTS.md, README.md, architecture/{containers,context,deployment,flows,principles}/*.md, schema/**, standards/**, templates/**; no capabilities/ path present, checked at commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
relationships:
  - type: references
    target: architecture-containers-desktop
  - type: references
    target: architecture-containers-cli
  - type: references
    target: architecture-flows-media-upload
  - type: references
    target: architecture-flows-media-download
---

# Message attachments: capability

A user or agent can attach one or more previously-uploaded files to an outgoing
chat message, forum post, or forum reply, so recipients see the attachment inline
(images and video) or as a downloadable item (any other file type, on the client
that supports it) without a separate share step. The same underlying mechanism —
an imeta tag on the message event, referencing an already-uploaded blob — is
reached three different ways depending on which client sends the message, and each
client draws its own line around what counts as attachable and what happens to an
attachment between selection and send.

## Maturity

Shipped. `buzz-sdk`'s three message-family builders (`build_message`,
`build_forum_post`, `build_forum_comment`) all accept and emit attachment tags
today; `buzz-cli`'s `messages send --file` flag uploads and attaches files on
every send; and desktop's composer (`ComposerAttachments`, `useMediaUpload`,
`useFilePicker`) implements picking, dragging-and-dropping, previewing,
uploading, cancelling, editing, reverting and spoiler-marking attachments before
send, exercised by unit tests covering the slot-reservation and draft-epoch
correctness rules described below.

## Boundary

This node does not describe:

- **The imeta tag's own field contract and server-side validation rules**
  (NIP-92: which keys are allowed, what the relay's ingest-time structural and
  storage-backed checks require). No corpus node for that contract is merged on
  `origin/launchpad` at this revision — this node treats the tag as the wire
  mechanism attachment builders already emit, and does not restate its shape.
- **The Blossom upload/download HTTP flow** — the authenticated `PUT`/`GET`/`HEAD`
  request/response contract, its ordered admission checks, and its
  failure/rollback behavior. That is `architecture-flows-media-upload` and
  `architecture-flows-media-download`, referenced below; this node covers only
  the client-side capability of *initiating* an attach, not the wire protocol
  each client's upload call rides on.
- **How attachments are rendered once received**, in the message timeline rather
  than the composer. `ComposerAttachments` and its supporting hooks are the
  compose-time (pre-send) surface this node describes; the read-side rendering
  of an already-posted message's `imeta` tags is a related but distinct surface
  and was not inspected for this node.
- **Mobile's (`mobile/lib/**`) attachment handling.** Not inspected for this
  node; no claim is made about whether or how the Flutter client attaches
  files to a message.
- **How the running relay is operated, deployed, or monitored.** Not in scope
  for a capability node.

## Relationships

- `references`: `architecture-containers-desktop` — the container implementing
  the composer attach experience described above.
- `references`: `architecture-containers-cli` — the container implementing the
  `messages send --file` attach path.
- `references`: `architecture-flows-media-upload` — the flow an attach call
  rides on to get a blob onto the relay in the first place.
- `references`: `architecture-flows-media-download` — the flow that later
  serves an attached blob back to a reader.

## Scope and omissions

**This node covers** the capability of attaching one or more files to an
outgoing message, forum post, or forum reply: the shared `buzz-sdk` builder
mechanism all three message kinds use, the CLI's `--file` flag and its
client-side MIME/size allowlist (narrower than the server's own upload
pipeline), and desktop's composer capability in full — file-picker and
drag-and-drop selection, per-MIME-type rendering (image/video thumbnail vs.
generic file chip), client-side video poster-frame capture, the upload
lifecycle (slot reservation, byte-level progress, cancellation), the
draft-epoch guard that prevents a stale upload from leaking into a replaced
draft, post-attach annotation/revert, per-attachment spoiler marking, and the
agent/team "snapshot" attachment special case.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The `imeta` tag's own field contract and relay-side validation | Not yet a corpus node at this writing |
| The Blossom upload/download HTTP request/response contract | `architecture-flows-media-upload`, `architecture-flows-media-download` |
| Rendering a received message's attachments in the timeline (read side) | Not yet a corpus node at this writing |
| Mobile's own attachment-handling implementation | Not inspected for this node |
| How the relay is operated, deployed, or monitored | The `operations` corpus surface |

**Expected but not verified when this node was written:**

- **Whether the CLI's `ALLOWED_MIMES`/size-cap constants are deliberately kept
  in sync with the server's own per-type upload caps**, or merely coincide at
  this revision. Both were read and their current values agree (50 MB
  image / 500 MB video), but no shared source or test asserting that
  agreement was located.
- **Whether the server's upload endpoint would accept a CLI-supplied generic
  file if the client-side allowlist in `upload_file` were bypassed.** The CLI
  never reaches that code path, so this node makes no claim about it either
  way — only that the CLI itself does not offer it.
- **Whether the desktop composer enforces any maximum attachment count per
  message.** No such limit was located in the files inspected for this node; a
  targeted search for one was not performed beyond the files cited above.
