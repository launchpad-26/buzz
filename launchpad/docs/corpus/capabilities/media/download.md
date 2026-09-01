---
id: capabilities-media-download
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
  - statement: "Root VISION_PROJECTS.md's own 'Capability | Status' table lists 'Blossom media storage (SHA-256, S3)' as a single row marked 'Ships today', naming media storage (which includes retrieval, not only upload) as a shipped, product-level capability rather than an in-progress or designed one."
    entry_class: FACT
    evidence:
      - "VISION_PROJECTS.md:252"
  - statement: "Root VISION.md states that media uploads (paste, drop, or attach files) are stored via the Blossom protocol (BUD-01/BUD-02) on S3/MinIO, with thumbnails generated server-side, describing the product-level promise this capability's retrieval half fulfils."
    entry_class: FACT
    evidence:
      - "VISION.md:144"
  - statement: "The relay serves a previously uploaded blob at GET/HEAD /media/{sha256_ext}, implemented by the get_blob and head_blob handlers, gated by Blossom (BUD-01 `t=get`) signed-event authentication, tenant-host binding, and relay-membership authorization before any storage read -- the full ordered mechanics, authentication/authorization boundaries, and failure/rollback table for this contract are already documented in corpus node architecture-flows-media-download and are not restated here."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/media.rs"
      - "launchpad/docs/corpus/architecture/flows/media-download.md"
  - statement: "buzz-cli exposes this capability to agents as `buzz media get <input> [--output <path>]` (the `MediaCmd::Get` subcommand), which accepts a relay media URL or a bare sha256[.ext] path segment, signs a fresh Blossom BUD-01 `t=get` authorization event per download attempt via `download_media`, and writes the resulting bytes to a file or to stdout."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/lib.rs"
      - "crates/buzz-cli/src/commands/upload.rs"
      - "crates/buzz-cli/src/client.rs"
  - statement: "The desktop app does not let its WKWebView fetch relay media URLs directly. `desktop/src/shared/lib/mediaUrl.ts` rewrites a relay-hosted `/media/{sha256_ext}` URL to a localhost proxy URL (or, before the proxy port resolves, to a `buzz-media://` custom scheme), and the native Tauri backend (`desktop/src-tauri/src/media_proxy.rs`, `handle_buzz_media`) forwards the request to the relay via `reqwest`, minting its own fresh Blossom `t=get` authorization header per request through `mint_media_get_auth` before forwarding the Range header and streaming the response back without buffering the full body."
    entry_class: FACT
    evidence:
      - "desktop/src/shared/lib/mediaUrl.ts"
      - "desktop/src-tauri/src/media_proxy.rs"
      - "desktop/src-tauri/src/commands/media.rs"
  - statement: "The documented reason for desktop's proxy indirection is that WKWebView's networking stack bypasses the VPN tunnel, causing direct relay media fetches to be rejected (403) by Cloudflare Access; routing through the Rust backend's own `reqwest` client keeps the request on the VPN-tunneled path."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/media_proxy.rs"
  - statement: "e2e_media.rs and e2e_media_video.rs exercise this capability end to end at the relay's HTTP contract: a successful GET/HEAD round trip after upload, 404 for an authenticated request against a never-uploaded hash, 401 for a wholly unauthenticated read, and 206/416 range behavior against a video blob -- the same tests architecture-flows-media-download cites as its own representative verification."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/e2e_media.rs"
      - "crates/buzz-test-client/tests/e2e_media_video.rs"
  - statement: "relationships.schema.json defines `references` as: source cites target as supporting context, with no ownership or currency dependency implied -- the loose-coupling relationship type this node uses to point at the architecture nodes that realize it, per the capability template's own guidance to cite rather than restate an architecture node's content."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/relationships.schema.json"
  - statement: "At the recorded revision, `architecture-flows-media-download`, `architecture-containers-relay`, and `architecture-containers-object-storage` are all present in origin/launchpad's corpus tree (confirmed via `git ls-tree -r --name-only HEAD -- launchpad/docs/corpus`, run against this worktree's HEAD, which was checked out directly from origin/launchpad), so each is a resolvable relationship target; no `capabilities/` node existed anywhere in that tree prior to this one, so this is the corpus's first `type: capabilities` instance node and no sibling capability node exists yet to point at."
    entry_class: FACT
    evidence:
      - "git_ls_tree(ref='HEAD', path='launchpad/docs/corpus') -> no capabilities/ directory present; architecture/flows/media-download.md, architecture/containers/relay.md and architecture/containers/object-storage.md all present, at commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
  - statement: "Whether mobile (`mobile/`) has its own media-download entry point distinct from the relay's HTTP contract was not inspected for this node; only the desktop and CLI entry points were verified directly."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/architecture/flows/media-download.md"
    confidence: 0.5
---

# Media download: capability

A client that already knows the content hash (`sha256`) of a previously uploaded
image, video, or other file -- typically read from a message's `imeta` tag, or
returned by an earlier upload -- can retrieve that blob from the Buzz relay's
Blossom-compatible media store, with the request authenticated per attempt by a
freshly signed identity proof. This is the retrieval half of the "Blossom media
storage" capability VISION_PROJECTS.md's own Status table already names as shipped;
the corresponding write half (uploading a new blob) is a distinct capability and, if
it needs its own node, is a separate task.

## Maturity

**Shipped.** VISION_PROJECTS.md's Status table marks "Blossom media storage (SHA-256,
S3)" as "Ships today," and three independent entry points into this specific
capability are implemented and exercised by passing tests at the recorded revision:
the relay's `GET`/`HEAD /media/{sha256_ext}` contract (`crates/buzz-relay/src/api/media.rs`,
covered by `crates/buzz-test-client/tests/e2e_media.rs` and `e2e_media_video.rs`),
the desktop app's local proxy (`desktop/src-tauri/src/media_proxy.rs`,
`desktop/src/shared/lib/mediaUrl.ts`), and `buzz-cli`'s `buzz media get` subcommand
(`crates/buzz-cli/src/commands/upload.rs`, `crates/buzz-cli/src/client.rs`).

## Trigger, preconditions, and termination

**Trigger.** A client already holding a content hash issues a download request
through one of this capability's entry points: a direct `GET`/`HEAD` against the
relay (any client speaking the Blossom contract), the desktop app's message-attachment
renderer (which resolves to the local proxy transparently), or `buzz media get
<input>` from the CLI.

**Preconditions.** Common to every entry point: the caller can produce a validly
signed Blossom (kind `24242`, BUD-01 `t=get`) authorization event scoped to the
requested hash or to the bound relay host. The relay itself additionally requires the
request's `Host` header to resolve to a known community and the signer to be a member
of that community (or a delegated NIP-OA agent), before any storage I/O runs. The full
precondition set and check order are the relay's own contract, documented once in
`architecture-flows-media-download` rather than restated here.

**Termination/outcome.** The capability terminates synchronously in exactly one
outcome per attempt, with no queued or asynchronous follow-up: the requested bytes
(whole or a byte range), or a terminal error the caller can act on immediately. See
*Failure and abort behavior* below for what a caller of each entry point actually
receives on failure.

## Ordered interactions and data movement (summary)

1. The client resolves a content hash, from message content or a prior upload
   response.
2. The client's entry point (relay HTTP client, desktop proxy, or CLI) signs a fresh
   Blossom `t=get` authorization event for the request.
3. The relay authenticates the signed event, binds the request to a community by
   `Host` header, and authorizes the signer against that community's membership.
4. The relay resolves the authoritative content type and storage key from a per-blob
   sidecar record (never from the client-supplied extension), then streams the blob
   (or the requested byte range) back, or returns a terminal error.
5. Desktop and CLI entry points relay those bytes or that error to their own caller
   (the renderer, or the file/stdout the CLI was told to write to) unchanged.

Steps 3-4 are the relay's own admission and serving pipeline; the full ordered
sequence, including every intermediate check, is documented once in
`architecture-flows-media-download` and is not duplicated here.

## Authentication, authorization, and trust-boundary crossings (summary)

- **Client → relay identity.** A freshly signed Blossom event is the proof of *who*
  is asking, minted independently by each entry point (the CLI signs per attempt in
  `download_media`; the desktop native backend signs per proxied request in
  `mint_media_get_auth`) -- never a long-lived token reused across requests.
- **Tenant boundary.** The relay's `Host` header binding scopes which community's
  data a request can reach; the desktop proxy and the CLI both resolve this from the
  configured relay's own base URL, not from user input.
- **Authorization boundary.** Relay membership is checked only after identity is
  established, with an owner-delegation carve-out for NIP-OA agents.
- **Content-authority boundary.** The relay's own sidecar record, not the request
  path, decides what content type is served -- closing off extension/content-type
  spoofing regardless of which entry point issued the request.

The full crossing-by-crossing detail (exact checks, order, and status codes on
failure) belongs to `architecture-flows-media-download`, which this node references
rather than restates.

## Failure and abort behavior

There is no state mutation to roll back anywhere in this capability -- every failure
is a terminal error response, not a partial result:

| Failure | What each entry point does | Representative verification |
|---|---|---|
| Relay rejects the request (bad/missing auth, unresolvable tenant, not a member, hash never uploaded, malformed range) | Relay returns the documented HTTP status (401/403/404/416); the desktop proxy and `buzz media get` both surface that status/body to their own caller rather than retrying silently | `crates/buzz-test-client/tests/e2e_media.rs`, `crates/buzz-test-client/tests/e2e_media_video.rs` |
| Desktop proxy's own guard rejects the response (oversized non-range body) | `413 Payload Too Large` from the local proxy, before any relay bytes are forwarded | `desktop/src-tauri/src/media_proxy.rs` (`MAX_PROXY_RESPONSE` guard) |
| Upstream request itself fails (network, relay unreachable) | Desktop proxy returns `502 Bad Gateway`; `buzz media get` surfaces the CLI's own network error | `desktop/src-tauri/src/media_proxy.rs` |

The relay's own full status-code mapping (401/403/404/416/500 and why) is documented
once in `architecture-flows-media-download` and is not repeated here.

## Boundary

This node does not describe:
- **How the capability is built.** The relay's HTTP handlers, the Blossom
  authentication/authorization pipeline, and the storage layer are architecture, not
  capability, content -- see `architecture-flows-media-download` (the flow) and
  `architecture-containers-relay` / `architecture-containers-object-storage` (the
  containers), all referenced below rather than restated.
- **The interface(s) this capability is exposed through in full.** No `interfaces-events`
  corpus node exists yet for `buzz-cli`'s command surface or the relay's HTTP media
  route group; when one is authored, it is the natural place for the full command/route
  contract, and this node would `references` it.
- **The step-by-step flow through this capability**, beyond the summary above. The
  complete ordered interaction sequence, every intermediate check, and the full
  failure/status table already live in `architecture-flows-media-download`.
- **The upload (write) half of media storage**, mobile's own download call sites, or
  the exact BUD-01/BUD-02 wire specification -- none of these were inspected for this
  node.
- **How the running relay is operated** (deployment, monitoring, incident response)
  -- that is the `operations` corpus surface, not this one.

## Relationships

- references: architecture-flows-media-download
- references: architecture-containers-relay
- references: architecture-containers-object-storage

## Scope and omissions

**This node covers** the media-download capability as a product-level thing Buzz can
do: what it is, that it has shipped, its three known client entry points (relay HTTP
contract, desktop local proxy, `buzz-cli`), and a capability-level summary of its
trigger/preconditions/termination, ordered interactions, trust-boundary crossings, and
failure behavior -- each explicitly deferring exhaustive detail to
`architecture-flows-media-download` rather than duplicating it.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The relay's full HTTP contract, ordered checks, and status-code mapping | `architecture-flows-media-download` |
| The containers that implement storage and serving | `architecture-containers-relay`, `architecture-containers-object-storage` |
| The command/route-level interface contract | not yet authored (no `interfaces-events` node exists for this surface) |
| The upload (write) half of media storage | a separate capability, out of scope for this task |
| Mobile's own media-download call sites | not inspected for this node |
| How the running relay is operated | the `operations` corpus surface |

**Expected but not verified when this node was written:**
- **Whether `mobile/` has its own distinct media-download entry point** beyond the
  relay's HTTP contract every entry point ultimately depends on -- not inspected here,
  recorded above as an `INFERENCE` at `confidence: 0.5`.
- **The exact BUD-01/BUD-02 wire specification** -- this node and
  `architecture-flows-media-download` both describe what Buzz's own code enforces,
  not the external Blossom specification text itself.
