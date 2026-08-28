---
id: architecture-containers-object-storage
type: architecture
status: draft
origin: launchpad
audiences:
  - developer
  - operator
  - agent
evidence:
  - statement: "This node was authored and checked against repository revision a44cf52fc740ebebbdd671427480d14f0bce0115."
    entry_class: FACT
    evidence:
      - "commit a44cf52fc740ebebbdd671427480d14f0bce0115"
  - statement: "buzz-media is described in the repo's own architecture map as 'Blossom/S3 media storage', a leaf crate alongside buzz-relay rather than a dependency of the core event-store stack (buzz-db, buzz-auth, buzz-pubsub, buzz-search, buzz-audit, buzz-workflow)."
    entry_class: FACT
    evidence:
      - "ARCHITECTURE.md"
      - "AGENTS.md"
  - statement: "buzz-media is a library crate with no Axum dependency of its own; its HTTP handlers are implemented in buzz-relay, which depends on buzz-media as a workspace crate."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/src/lib.rs"
      - "crates/buzz-relay/Cargo.toml"
  - statement: "buzz-media's MediaStorage client wraps an S3-compatible bucket (via the rust-s3 crate, pinned to 0.37 in buzz-media's Cargo.toml) and exposes put, put_file, get, get_range, get_stream, head and delete operations; put_file streams from disk through an 8 MiB buffered reader so large video blobs are never held fully in RAM."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/src/storage.rs"
      - "crates/buzz-media/Cargo.toml"
  - statement: "MediaStorage::new selects static S3 credentials when both s3_access_key and s3_secret_key are configured, and otherwise falls back to the AWS default credential chain (environment, shared profile, web-identity/IRSA, container, instance metadata), so a relay pod can use its IAM role instead of long-lived static keys."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/src/storage.rs"
  - statement: "MediaConfig's s3_addressing_style controls whether the bucket name is put in the request path (default, for MinIO/local compatibility) or in the hostname (virtual-hosted style, required by providers such as Railway Storage Buckets)."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/src/config.rs"
  - statement: "buzz-relay mounts the media (Blossom) routes PUT /upload, PUT /media/upload, and GET/HEAD /media/{sha256_ext} on api::media::upload_blob, upload_blob and get_blob/head_blob respectively, layered with a request-body-size limit sized to the larger of max_image_bytes and max_video_bytes."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs"
      - "crates/buzz-relay/src/api/media.rs"
  - statement: "Upload and get requests are authorized by verifying a Blossom kind:24242 auth event (BUD-11): Schnorr signature, kind == 24242, non-empty human-readable content, a t tag matching the verb, an expiration tag in the future, created_at in the past within a clock-skew tolerance, and (if present) a server tag naming this relay's domain."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/src/auth.rs"
  - statement: "Uploaded content is validated before being written to storage: magic-byte sniffing against an explicit MIME allowlist (image/jpeg, image/png, image/gif, image/webp for the image path; a separate ISO-BMFF/MP4 brand check for the video path), so a spoofed Content-Type on an MP4 uploaded through the image path is rejected rather than trusted."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/src/validation.rs"
  - statement: "buzz-media's on-disk key taxonomy in the shared bucket has five classes: {sha256}.thumb.jpg (thumb), {sha256}.{ext} (blob), _meta/{community-uuid}/{sha256}.json (sidecar, the community-to-blob binding), _uploads/{community-uuid}/{sha256}/{ulid}.json (auxiliary, an optional moderation side-channel record gated by MediaConfig.upload_records_enabled), and everything else (unknown, a deliberate non-silent catch-all)."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/src/bucket_index.rs"
      - "crates/buzz-media/src/config.rs"
  - statement: "buzz-relay's storage_sweep module runs an hourly, single-flight, cadence-independent background sweep that lists the bucket through buzz_media::MediaStorage's pagination and folds the listing with buzz_media::bucket_index's pure classifier into cached usage gauges; a kill switch (BUZZ_STORAGE_METRICS=off) disables the sweep entirely for a deployment that lacks s3:ListBucket."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/storage_sweep.rs"
  - statement: "The same physical S3-compatible bucket also backs git-on-object-storage: crates/buzz-relay/src/api/git/store.rs constructs its own rust-s3 Bucket client (not buzz-media's MediaStorage) for content-addressed pack/manifest objects and CAS pointer writes, reusing buzz_media::config::S3AddressingStyle as its addressing-style type rather than duplicating that enum."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/store.rs"
  - statement: "Git object writes are create-only and content-addressed (pack/manifest keys are the SHA-256 of their bytes, written with If-None-Match: *), and the current state of a ref is a single mutable manifest pointer updated by an S3 conditional PUT (compare-and-swap); a 412 response from that CAS PUT is treated as the semantic LostRace outcome, not an error."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/store.rs"
      - "docs/git-on-object-storage.md"
  - statement: ".env.example documents BUZZ_S3_ENDPOINT, BUZZ_S3_ACCESS_KEY, BUZZ_S3_SECRET_KEY, BUZZ_S3_BUCKET and BUZZ_S3_REGION under the heading 'S3-Compatible Object Storage (media + Git/CAS)', naming both consumers of the one configured bucket in a single config block rather than two."
    entry_class: FACT
    evidence:
      - ".env.example"
  - statement: "Local development provides the object store via a MinIO service in docker-compose.yml (S3 API on 9000, console on 9001), documented in ARCHITECTURE.md's infrastructure services table as 'S3-compatible object storage (media)'."
    entry_class: FACT
    evidence:
      - "ARCHITECTURE.md"
  - statement: "The relay's Helm chart (deploy/charts/buzz) offers a quickstart profile that bundles an in-cluster, single-replica, non-HA MinIO (chart default bucket buzz-media) for eval use, and a production profile that expects an external managed S3-compatible service configured via s3.endpoint / BUZZ_S3_* and an existingSecret, with no chart-side credential autogeneration."
    entry_class: FACT
    evidence:
      - "deploy/charts/buzz/README.md"
  - statement: "The chart's own README states the git storage path does not require ReadWriteMany filesystem access because ref/object state is object-store-backed and each replica hydrates an ephemeral repo from S3-compatible storage on request, with repo-name uniqueness tracked separately in Postgres."
    entry_class: FACT
    evidence:
      - "deploy/charts/buzz/README.md"
  - statement: "This repository's own AGENTS.md documents squareup/block-coder-tf-stacks as the separate repo whose Terraform + ArgoCD pipeline deploys the relay's Helm chart to the staging Kubernetes cluster; block-coder-tf-stacks itself is a private repo not present in this checkout, so what it actually provisions for object storage in staging was not verified here."
    entry_class: FACT
    evidence:
      - "AGENTS.md"
  - statement: "buzz-media's key namespacing depends on buzz-core's CommunityId/TenantContext types for community-scoped sidecar and auxiliary keys, and buzz-relay is the only crate that constructs both an S3 client through buzz-media (media) and a second, independent S3 client through its own git/store.rs module (git CAS) — so the object-storage container is reached by two client code paths compiled into one relay binary, not by two separately deployed services."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-media/src/storage.rs"
      - "crates/buzz-media/src/bucket_index.rs"
      - "crates/buzz-relay/src/api/git/store.rs"
      - "crates/buzz-relay/Cargo.toml"
    confidence: 0.8
  - statement: "buzz-media/tests/static_creds_minio.rs exercises a static-credential round trip against a real MinIO instance, and buzz-test-client's e2e_media.rs (7 cases, per ARCHITECTURE.md's test-suite table) and e2e_media_extended.rs cover media upload/download through the relay's HTTP surface."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/tests/static_creds_minio.rs"
      - "crates/buzz-test-client/tests/e2e_media.rs"
      - "crates/buzz-test-client/tests/e2e_media_extended.rs"
      - "ARCHITECTURE.md"
---

# Architecture container: Object storage

An S3-compatible object-storage bucket, and the two independent client code
paths inside the `buzz-relay` binary that read and write it: Blossom media
blobs (`buzz-media`) and git-on-object-storage content (`buzz-relay`'s
`api::git::store` module).

## Responsibility, technology, and ownership boundary

**Responsibility.** Durable byte storage for two kinds of content the relay
serves over HTTP: user-uploaded media blobs (images, animated GIFs, video —
the [NIP-96](https://github.com/nostr-protocol/nips)-adjacent
[Blossom](https://github.com/hzrd149/blossom) protocol), and git repository
objects (packs, manifests, ref pointers) for the relay's git smart-HTTP
surface. Both are content-addressed by SHA-256 in the same bucket.

**Technology.** An S3-compatible object store, accessed through the
[`rust-s3`](https://crates.io/crates/rust-s3) crate (pinned to `0.37` in
`crates/buzz-media/Cargo.toml`). MinIO backs local development and the Helm
chart's eval-only quickstart profile; production deployments point
`BUZZ_S3_*` at an externally managed S3-compatible service (AWS S3, Railway
Storage Buckets, or similar) — see *Deployment implications* below.

**Ownership boundary.** `buzz-media` (`crates/buzz-media`) owns the media
half: `MediaStorage` (the S3 client wrapper), `MediaConfig` (S3 endpoint,
credentials, addressing style, per-content-type size limits), Blossom BUD-11
auth verification, upload content validation, thumbnail/blurhash generation,
and the bucket key-taxonomy classifier used by the storage sweep. It is a
library crate with no Axum dependency — HTTP handlers live in `buzz-relay`.
The git half is **not** a separate crate: `crates/buzz-relay/src/api/git/store.rs`
constructs its own `rust-s3` `Bucket` client for content-addressed pack and
manifest objects and CAS pointer writes. It reuses `buzz_media::config::S3AddressingStyle`
as its addressing-style type rather than defining a second one, but does not
share `MediaStorage`'s connection instance, credential-resolution call, or key
taxonomy. Both client paths are configured from the same `BUZZ_S3_*` values
and, by default, the same bucket (`.env.example` documents the block as
"S3-Compatible Object Storage (media + Git/CAS)" precisely because it is one
config surface for two independent clients, not two config surfaces). No
crate other than `buzz-relay` constructs an S3 client for either purpose.

## Interfaces

**Inbound (what calls into this container's code paths):**

| Caller | Path(s) | Auth |
|---|---|---|
| Desktop/mobile/CLI clients | `PUT /upload`, `PUT /media/upload` | Blossom kind:24242 auth event (BUD-11), verb `upload` |
| Desktop/mobile/CLI clients, and unauthenticated fetchers | `GET/HEAD /media/{sha256_ext}` | Blossom kind:24242 auth event, verb `get`, or unauthenticated depending on relay config |
| Git clients (`git clone`/`fetch`/`push`) | `GET /git/{owner}/{repo}/info/refs`, `POST .../git-upload-pack`, `POST .../git-receive-pack` | NIP-98/relay auth on the git smart-HTTP layer, not the Blossom auth path |
| `buzz-relay`'s internal storage-sweep task | (no HTTP path — calls `MediaStorage::list_page` directly) | in-process, requires the relay's own S3 credentials to carry `s3:ListBucket` |

**Outbound (what this container's code calls out to):** the configured
S3-compatible endpoint (`BUZZ_S3_ENDPOINT`), authenticated with either static
`BUZZ_S3_ACCESS_KEY`/`BUZZ_S3_SECRET_KEY` credentials or, when both are
unset, the AWS default credential chain (environment, shared profile,
web-identity/IRSA, container, instance metadata) — letting a relay pod use
its Kubernetes service account's IAM role instead of long-lived static keys.

**Directly connected containers/systems:**

- **`buzz-relay`** — the only caller of both client paths; it is the process
  that embeds `buzz-media` and `api::git::store`, and the one that terminates
  the HTTP routes above.
- **`buzz-core`** — supplies the `CommunityId`/`TenantContext` types
  `buzz-media` uses to namespace sidecar (`_meta/{community}/{sha256}.json`)
  and auxiliary (`_uploads/{community}/{sha256}/{ulid}.json`) keys per
  community.
- **Postgres** — tracks git repo-name uniqueness for the git-on-object-storage
  path; it does not store media or git object bytes itself (see the [Postgres
  event store](../../../../../ARCHITECTURE.md) container, not yet a corpus node
  at this writing).
- **The S3-compatible bucket itself** — the external system both client
  paths read and write; not part of the `buzz-relay` binary.

## Deployment implications

Local development and CI bring up a MinIO container (`docker-compose.yml`,
API on 9000, console on 9001) as the S3-compatible backend. The relay's Helm
chart (`deploy/charts/buzz`) offers two profiles: a **quickstart** profile
that bundles an in-cluster, single-replica, non-HA MinIO with an
autogenerated `buzz-media`-named bucket for eval/demo use, and a
**production** profile that expects an externally managed S3-compatible
service supplied via `s3.endpoint`/`BUZZ_S3_*` in an `existingSecret`, with no
chart-side credential generation. The chart's addressing-style setting
(`s3.addressingStyle` → `BUZZ_S3_ADDRESSING_STYLE`) has to match the target
provider — path style for bundled MinIO, virtual-hosted style for providers
such as Railway Storage Buckets whose DNS does not resolve a bucket-in-path
form.

Because git ref/object state is entirely object-store-backed rather than
filesystem-backed, the chart's own documentation notes that each relay
replica needs only its own `ReadWriteOnce` volume for ephemeral hydration —
no shared `ReadWriteMany` filesystem is required for git.

This repository's own `AGENTS.md` names `squareup/block-coder-tf-stacks` as
the separate, private repository whose Terraform + ArgoCD pipeline deploys
the relay's Helm chart to the staging Kubernetes cluster. That repo is not
part of this checkout; what it specifically provisions for staging object
storage (a managed S3 bucket, IAM role, or something else) was not verified
for this node — see *Scope and omissions*.

## Data implications

Both consumers of the bucket use create-only, content-addressed writes rather
than in-place mutation:

- **Media.** Blob keys are `{sha256}.{ext}`; thumbnails are
  `{sha256}.thumb.jpg`. A community-to-blob binding lives in a separate
  `_meta/{community}/{sha256}.json` sidecar object, and an optional
  moderation side-channel record (gated by `MediaConfig.upload_records_enabled`,
  off by default) lives under `_uploads/{community}/{sha256}/{ulid}.json`.
  Every other key shape classifies as `Unknown` rather than being folded into
  a known class, so the storage-sweep's usage gauges stay loud instead of
  silently wrong on an unrecognized key.
- **Git.** Pack and manifest object keys are the SHA-256 of their own bytes,
  written with an `If-None-Match: *` create-only precondition (never
  overwritten). The current state of a ref is one mutable manifest *pointer*,
  updated by an S3 conditional `PUT` used as compare-and-swap; a `412`
  response from that PUT is the protocol's normal "lost the race" outcome,
  not an error condition. The full safety argument for this scheme —
  durability-ordering, manifest reconstruction, and linearizability, reduced
  to three object-store axioms — is specified in
  [`docs/git-on-object-storage.md`](../../../../../docs/git-on-object-storage.md)
  and is not repeated here.

## Security implications

- **Blossom auth (media).** Upload and get requests are authorized by
  verifying a Blossom kind:24242 event per BUD-11: Schnorr signature, correct
  kind, non-empty human-readable content, a `t` tag matching the verb, an
  `expiration` tag in the future, `created_at` in the past within a bounded
  clock-skew tolerance, and — when present — a `server` tag naming this
  relay's own domain.
- **Content validation (media).** Uploaded bytes are sniffed against an
  explicit MIME allowlist before being trusted, independent of the
  client-supplied `Content-Type` — an MP4 uploaded through the image path is
  detected by magic-byte inspection and rejected rather than accepted on a
  spoofed header.
- **Credential handling.** Static S3 credentials are optional; when unset,
  the relay resolves credentials through the AWS default chain, which
  includes IRSA web-identity tokens on EKS — a production deployment can
  avoid long-lived static keys entirely.
- **Optional uploader metadata.** Recording an uploader's IP/port alongside
  an upload record is off by default, requires an explicit trusted
  edge-header name, and fails closed (drops the value) if the header's
  content doesn't parse as a public IP — it is not implicitly enabled by
  turning on upload records.
- **Sweep failure mode.** The hourly storage sweep that lists the bucket for
  usage metrics can be disabled entirely (`BUZZ_STORAGE_METRICS=off`) for a
  deployment whose relay credentials don't carry `s3:ListBucket`, rather than
  the relay depending on that permission implicitly.

## Implementation

- `crates/buzz-media/src/` — storage client, config, Blossom auth,
  validation, thumbnailing, upload/upload-record handling, bucket key
  taxonomy.
- `crates/buzz-relay/src/api/media.rs` — HTTP handlers (`upload_blob`,
  `get_blob`, `head_blob`).
- `crates/buzz-relay/src/api/git/store.rs` — the git-on-object-storage S3
  client, content-addressed writes, and CAS pointer swap.
- `crates/buzz-relay/src/storage_sweep.rs` — the background usage sweep.
- `crates/buzz-relay/src/router.rs` — route wiring for both the media and
  git HTTP surfaces.
- `docs/git-on-object-storage.md` — the formal specification for the git
  half's safety properties.
- `deploy/charts/buzz/` — the Helm chart's quickstart/production S3
  profiles.

This node does not restate the request/response shape of each HTTP endpoint,
the full Blossom/BUD-11 protocol, or the object-storage design doc's formal
proofs — follow the links above for those.

## Scope and omissions

**This node covers** the object-storage container's responsibility and
technology, the ownership boundary between `buzz-media` and the git-storage
code path, its inbound/outbound interfaces, its directly connected
containers, and its deployment, data, and security implications.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The full Blossom/BUD-11 protocol semantics | `crates/buzz-media/src/auth.rs`, the upstream Blossom spec |
| The formal safety proof for git-on-object-storage | `docs/git-on-object-storage.md` |
| Per-endpoint request/response schemas | `ARCHITECTURE.md`, `crates/buzz-relay/src/api/media.rs`, `crates/buzz-relay/src/api/git/transport.rs` |
| The Postgres event-store container this document only mentions in passing | a future corpus node, not yet written |
| Whether `squareup/block-coder-tf-stacks` provisions staging object storage as managed AWS S3, and with what IAM boundary | that private repo, not present in this checkout |

**No `relationships` are declared.** At the recorded revision the merged
corpus on `origin/launchpad` (`git ls-tree -r --name-only origin/launchpad --
launchpad/docs/corpus`) contains no other `architecture`-typed node — this is
the first one. The only currently loadable node this could point at is
`corpus-agents`, a `governance` node about how to write a corpus entry, not a
domain sibling; a `references` edge to it would name process guidance rather
than a real conceptual relationship to the subject of this node, so it is
omitted rather than added for the sake of having one. The first sibling
`architecture` (or related) node to merge is the point to revisit this.

**Expected but not verified when this node was written:**

- **What `squareup/block-coder-tf-stacks` actually provisions for staging
  object storage.** That repo is private and not part of this checkout;
  this node relies only on this repository's own `AGENTS.md` for the fact
  that it deploys the relay's Helm chart to staging at all.
- **Whether `sprout-backend-blox`'s Blox compute provider script (which
  connects desktop-agent workstations to the relay, per this repository's
  `AGENTS.md`) touches this object-storage container at all.** Nothing in
  `crates/buzz-media` or `api::git::store` references it, but that absence
  was not exhaustively checked against the other repo.
- **Production-scale sweep behavior at `max_objects` / `timeout` boundaries.**
  `storage_sweep.rs`'s documented caps were read from its own doc comments
  and config-parsing code, not exercised against a bucket large enough to
  hit them.
