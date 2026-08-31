# Plan: issue #1275 — platforms/relay/media-api.md

## ALREADY TRUE

- `launchpad/docs/corpus/platforms/relay/media-api.md` does not exist; `platforms/`
  does not exist anywhere under the corpus yet — this is the first `platforms` node.
- `launchpad/docs/corpus/architecture/flows/media-upload.md`
  (`architecture-flows-media-upload`) and `.../media-download.md`
  (`architecture-flows-media-download`) are already merged on `origin/launchpad`
  (commits `09b0694fd` / `560b2d836`) and exhaustively document the step-by-step
  upload/download admission checks, storage pipelines, and failure-status mapping,
  citing `crates/buzz-relay/src/api/media.rs`, `crates/buzz-media/src/auth.rs`,
  `crates/buzz-media/src/error.rs`, `crates/buzz-media/src/config.rs`.
- `launchpad/docs/corpus/architecture/containers/relay.md`
  (`architecture-containers-relay`) already names `PUT/GET/HEAD /media/*` as one row
  of the relay's inbound route table but explicitly defers each subsystem's own
  detail to that subsystem's future node.
- No `templates/platforms*.md` exists; per known findings, sibling `platforms/**`
  nodes borrow `templates/component.md`'s section shape (Responsibility, Public
  interface, Dependencies, Boundary, Relationships, Scope and omissions) with
  `type: platforms` instead of `type: implementation`.
- Confirmed in source at HEAD `131b02f989684117d9ab1dd426f1673fa638e523`:
  - Route table (`crates/buzz-relay/src/router.rs:39-46`): `PUT /upload`,
    `PUT /media/upload` (legacy alias) both to `upload_blob`; `GET`/`HEAD
    /media/{sha256_ext}` to `get_blob`/`head_blob`.
  - `BlobDescriptor` (`crates/buzz-media/src/types.rs`) is the BUD-02 response type.
  - `buzz-media` is a library crate with no Axum handlers of its own
    (`crates/buzz-media/src/lib.rs`); handlers live in `buzz-relay`.
  - Crates that declare `buzz-media` as a dependency: `buzz-relay`, `buzz-admin`,
    `buzz-deletion`, `buzz-test-client` (`grep -rl "^buzz-media" crates/*/Cargo.toml`).
    Of these, `buzz-deletion` and `buzz-relay` actually reference `buzz_media::` symbols
    in their own source; `buzz-admin` declares the dependency but no `buzz_media::`
    reference was found in its `src/`; `buzz-test-client`'s only `buzz_media::` hit is
    in `tests/e2e_git.rs` (unrelated to media).
  - `crates/buzz-cli/src/client.rs` (`upload_file`, `download_media`,
    `media_url_from_input`) constructs its own Blossom auth events and calls
    `PUT /upload` / `GET /media/{sha256_ext}` directly over HTTP — an API-level
    consumer, not a crate-level dependent of `buzz-media`.

## STEP 1 — Confirm scope against the two existing flow nodes

Read both flow nodes and `architecture-containers-relay.md` in full (done). Decide
this node's non-duplicative scope: a **platform-level interface reference** for the
Blossom-compatible media HTTP API — its responsibility, route/response-type
contract, and dependency edges — deferring the ordered admission-check sequence,
exact error-status mapping, and storage-pipeline mechanics to the two flow nodes via
`references` relationships rather than restating them.

## STEP 2 — Gather remaining evidence

Read `crates/buzz-media/src/storage.rs` (`MediaStorage` public methods),
`crates/buzz-media/src/config.rs` (`MediaConfig` fields), `crates/buzz-media/src/error.rs`
(status-mapping precedent, cited briefly, not restated), and confirm exact handler
signatures (`upload_blob`, `get_blob`, `head_blob`) in
`crates/buzz-relay/src/api/media.rs`.

## STEP 3 — Draft the node

Write `launchpad/docs/corpus/platforms/relay/media-api.md` with:
- Front matter: `id: platforms-relay-media-api`, `type: platforms`, `status: draft`,
  `origin: launchpad`, `audiences: [agent, developer, reviewer]`, evidence ledger
  (commit citation + one entry per claim), `relationships: references` toward
  `architecture-flows-media-upload`, `architecture-flows-media-download`, and
  `architecture-containers-relay` (all three confirmed present on `origin/launchpad`).
- Body sections mirroring `templates/component.md`'s shape: purpose/scope,
  Responsibility, Public interface (route table + `BlobDescriptor` + status-code
  summary table, cited), Dependencies (depends-on: `buzz-media`, `buzz-deletion`,
  S3/MinIO backing store; depended-on-by: `buzz-relay`'s router, `buzz-cli`'s
  `client.rs` as an HTTP-level consumer, desktop's `mediaUrl.ts` rewrite — each
  qualified by how it was verified), Boundary, Relationships, Scope and omissions.

## STEP 4 — Validate and commit

Run the corpus unittest suite, diff-and-restore check against `validate.py`'s
pre-existing FAIL baseline, then commit per the two-call gate sequence.

## GATES

- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` → `OK`.
- `python3 launchpad/project-intelligence/corpus/validate.py` contributes zero new
  FAIL lines versus the file-removed baseline.
- Every `relationships[].target` resolves against `origin/launchpad`'s corpus tree.
- Every evidence citation is a real path this session opened and read.

## OPEN

- Whether `buzz-admin`'s declared `buzz-media` Cargo dependency is genuinely unused
  or reached indirectly (e.g. via a re-exported type in a signature) was not fully
  resolved; the node states only what was directly verified and flags the rest as
  unconfirmed rather than asserting either way.
- Whether mobile (`mobile/`) has its own media-API call site was not inspected —
  named as a gap, matching the existing download flow node's own omission.

## LEFT OUT

- Restating the ordered admission-check sequence, the full error-to-status-code
  mapping, or the buffered/streaming storage pipeline mechanics — all already owned
  by the two flow nodes this node `references`.
- A Mermaid diagram — not required by `component.md`'s shape and no
  `platforms`-specific template mandates one.
- Any change to runtime behavior, or resolving `#1321`'s open provenance-revision
  question.
