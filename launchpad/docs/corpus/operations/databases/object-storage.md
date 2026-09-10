---
id: operations-databases-object-storage
type: operations
status: draft
origin: launchpad
audiences:
  - operator
  - developer
evidence:
  - statement: "This node was authored and checked against repository revision 473205a7457b208455f188847bfb27b01aa83cac."
    entry_class: FACT
    evidence:
      - "commit 473205a7457b208455f188847bfb27b01aa83cac"
  - statement: "buzz-relay's config loader reads BUZZ_S3_ENDPOINT, BUZZ_S3_ACCESS_KEY, BUZZ_S3_SECRET_KEY, BUZZ_S3_BUCKET, BUZZ_S3_REGION (falling back to AWS_REGION, then 'us-east-1') and BUZZ_S3_ADDRESSING_STYLE into a shared buzz_media::MediaConfig, defaulting to http://localhost:9000 / buzz_dev / buzz_dev_secret / buzz-media / us-east-1 / path style when a variable is unset -- the same values .env.example documents for local development."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/config.rs"
      - ".env.example"
  - statement: "BUZZ_MAX_IMAGE_BYTES, BUZZ_MAX_GIF_BYTES, BUZZ_MAX_VIDEO_BYTES and BUZZ_MAX_FILE_BYTES default to 50 MB, 10 MB, 500 MB and 100 MB respectively when unset, and MediaConfig::validate rejects a zero limit for any of the four, a GIF limit exceeding the image limit, a public_base_url that does not end in exactly one trailing '/media' segment, and an incoherent combination of the upload-record IP/port header knobs -- all checked at relay startup, not at first upload."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/config.rs"
      - "crates/buzz-media/src/config.rs"
  - statement: "MediaStorage::new selects static S3 credentials only when both s3_access_key and s3_secret_key are non-empty, falls back to the AWS default credential chain (environment, shared profile, web-identity/IRSA, container, instance metadata) when both are empty, and returns a startup error if exactly one of the pair is set -- so a relay pod can rely on its own IAM role instead of long-lived static keys."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/src/storage.rs"
  - statement: "S3AddressingStyle::Path (the default) calls the rust-s3 bucket's with_path_style(), putting the bucket name in the request path; S3AddressingStyle::Virtual leaves the bucket in the hostname. .env.example and the Helm chart both document path style as required for the bundled MinIO's internal DNS and virtual style as required for providers such as Railway Storage Buckets."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/src/config.rs"
      - "crates/buzz-media/src/storage.rs"
      - ".env.example"
  - statement: "MediaStorage exposes put, put_file, get, get_range, get_stream, head, head_with_metadata, delete, delete_objects and list_page; put_file streams a file from disk through an 8 MiB tokio::io::BufReader via rust-s3's put_object_stream_with_content_type rather than loading the whole blob into memory, and its own doc comment states it is intended for video blobs up to 500 MB."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/src/storage.rs"
  - statement: "buzz_media::bucket_index::classify_key recognizes exactly four strict key shapes -- thumb ({sha256}.thumb.jpg), blob ({sha256}.{ext}), sidecar (_meta/{community-uuid}/{sha256}.json) and auxiliary (_uploads/{community-uuid}/{sha256}/{ulid}.json) -- checked in that order, and classifies everything else, including a malformed variant of a known prefix, as Unknown rather than coercing it into a known class."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/src/bucket_index.rs"
  - statement: "MediaError::StorageError, MediaError::Io and MediaError::Internal all map to HTTP 500 with a generic 'internal error' body and a tracing::error! log line, MediaError::ServiceUnavailable maps to 503, and a unit test in the same file (serving_backend_failures_map_to_5xx_but_fences_remain_403) asserts all three storage-adjacent variants produce a server-error status while CommunityWriteFenced stays 403 -- so an S3-side failure surfaces to the client as a 5xx response, not a crashed relay process or a silently dropped request."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/src/error.rs"
  - statement: "The relay's GET /_readiness handler checks exactly three dependencies inside a 2-second timeout -- state.db.ping() (Postgres), state.redis_pool.get() (Redis), and state.db.validate_deletion_serving_catalog() -- and returns 503 if the process is shutting down or if any of the three checks fails or the timeout elapses; it does not call into buzz-media or otherwise probe object-storage connectivity."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs"
  - statement: "MediaStorage::ping() (a list_page(None, 1) call, doc-commented 'Probe object-store connectivity and bucket access') exists on the client, but a repository-wide search of crates/ for '.ping()' call sites found only Db::ping, called from the readiness handler -- no production call site invokes MediaStorage::ping, so no health or readiness endpoint in this repository currently exercises it."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-media/src/storage.rs"
      - "crates/buzz-relay/src/router.rs"
    confidence: 0.85
  - statement: "The relay's hourly storage sweep (crates/buzz-relay/src/storage_sweep.rs) is single-flight and cadence-independent of the usage-metrics tick that re-publishes its cached snapshot; it is disabled entirely by BUZZ_STORAGE_METRICS=off, and otherwise bounded by BUZZ_STORAGE_SWEEP_TIMEOUT_SECS (default 120s) and BUZZ_STORAGE_SWEEP_MAX_OBJECTS (default 1,000,000, a cumulative listed-object cap whose breach fails the attempt and keeps the old snapshot)."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/storage_sweep.rs"
  - statement: "A cold cache (no sweep has ever succeeded) publishes only health gauges with sweep_ok=0; a warm cache re-publishes its last successful snapshot even while the newest attempt is failing, so a transient S3 outage does not blank the storage dashboards -- and should_spawn's documented rule retries a persistently failing sweep (e.g. missing s3:ListBucket) on every usage tick rather than waiting a full BUZZ_STORAGE_SWEEP_INTERVAL_SECS, so the sweep self-heals as soon as the underlying cause clears."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/storage_sweep.rs"
  - statement: "Object-storage retention in this repository is not a bucket-level TTL or lifecycle policy: crates/buzz-deletion implements a durable, heartbeat-leased, staged whole-community deletion engine that freezes an inventory and bulk-deletes tenant-owned keys (matched via buzz_media::tenant_prefixes / is_tenant_owned_key against the same bucket MediaStorage writes to) only when an operator submits and approves deleting an entire community; it is exposed as `buzz-admin deletions submit|list|inspect|approve|abort` (and further subcommands not enumerated here)."
    entry_class: FACT
    evidence:
      - "crates/buzz-deletion/src/lib.rs"
      - "crates/buzz-admin/src/main.rs"
  - statement: "No S3 bucket-level lifecycle or object-expiration policy is configured anywhere in this repository -- searched deploy/charts/buzz/{values.yaml,values.schema.json,templates/**} and crates/buzz-media for 'lifecycle', 'ttl' and 'expiration'; every match found was unrelated to object-storage retention: a Kubernetes Job's ttlSecondsAfterFinished garbage-collecting the quickstart MinIO-init Job, the BUZZ_EPHEMERAL_TTL_OVERRIDE Nostr ephemeral-event knob, and the Blossom kind:24242 auth event's own expiration tag."
    entry_class: FACT
    evidence:
      - "deploy/charts/buzz/templates/quickstart-minio-init.yaml"
      - "deploy/charts/buzz/values.yaml"
      - "crates/buzz-media/src/auth.rs"
  - statement: "Local development and CI bring up the object store as a MinIO container in docker-compose.yml (S3 API on host port 9000, console on 9001, healthchecked against /minio/health/live), with a one-shot minio-init sidecar that creates the buzz-media bucket and sets it non-public (mc anonymous set none) before depending services start."
    entry_class: FACT
    evidence:
      - "docker-compose.yml"
  - statement: "The relay's Helm chart (deploy/charts/buzz) offers a quickstart profile that bundles an in-cluster, single-replica, non-HA MinIO (chart default bucket buzz-media, autogenerated credentials) for eval use, and a production profile (the default) that expects an externally managed S3-compatible service supplied via s3.endpoint/BUZZ_S3_* in an existingSecret, with no chart-side credential generation."
    entry_class: FACT
    evidence:
      - "deploy/charts/buzz/README.md"
  - statement: "crates/buzz-media/tests/static_creds_minio.rs exercises a static-credential round trip against a real MinIO instance, and buzz-test-client's e2e_media.rs (7 cases) and e2e_media_extended.rs (18 cases, per ARCHITECTURE.md's own test-suite table) exercise media upload/download through the relay's HTTP surface end to end."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/tests/static_creds_minio.rs"
      - "crates/buzz-test-client/tests/e2e_media.rs"
      - "crates/buzz-test-client/tests/e2e_media_extended.rs"
      - "ARCHITECTURE.md"
  - statement: "A corpus node already documents the object-storage container's architecture -- responsibility, technology, ownership boundary between buzz-media and the git-on-object-storage code path, inbound/outbound interfaces, and deployment/data/security implications -- at launchpad/docs/corpus/architecture/containers/object-storage.md (id architecture-containers-object-storage), merged on origin/launchpad at this node's recorded revision; this operations node does not restate that content."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/containers/object-storage.md"
      - "git_ls_tree(ref='origin/launchpad', path='launchpad/docs/corpus/architecture/containers/object-storage.md') -> present, id architecture-containers-object-storage"
  - statement: "This node was written using launchpad/docs/corpus/templates/reference.md, which was already merged on origin/launchpad at the recorded revision and directs a reference-shaped node to carry a reference description, structured entries, an optional commands section, a boundary statement naming what the node excludes, relationships, and a scope-and-omissions section distinguishing what the node does not cover from what it could not verify."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/templates/reference.md"
relationships:
  - type: references
    target: architecture-containers-object-storage
  - type: references
    target: corpus-template-reference
---

# Object storage: reference

This node catalogues object storage as an **operational datastore**: the
configuration surface an operator sets (`BUZZ_S3_*`, size limits, addressing
style), the bucket's own key layout, what retention exists and does not, the
local-development and deployment substitutes, and how the relay behaves when
the store is unreachable. It is a lookup reference, not the architecture
description -- for the container's responsibility, technology, and the
ownership boundary between `buzz-media`'s media path and `buzz-relay`'s
git-on-object-storage path, see
[`architecture-containers-object-storage`](../../architecture/containers/object-storage.md).
This node is a sibling of the object-storage failure-mode node (#1218) and its
runbook (#1223), which cover diagnosis and recovery rather than configuration
lookup.

## Configuration surface

All values are read once at relay startup by `buzz-relay`'s config loader into
a shared `buzz_media::MediaConfig`. Every row below is enforced or defaulted
in `crates/buzz-relay/src/config.rs`; `MediaConfig::validate` (in
`crates/buzz-media/src/config.rs`) additionally rejects an incoherent
combination before the relay finishes starting.

| Field | Description | Example |
|---|---|---|
| `BUZZ_S3_ENDPOINT` | S3-compatible endpoint URL. Default: `http://localhost:9000` (the local MinIO container). | `http://localhost:9000` |
| `BUZZ_S3_ACCESS_KEY` / `BUZZ_S3_SECRET_KEY` | Static S3 credentials. Must be set together or both left empty; empty-both falls back to the AWS default credential chain (env, shared profile, web-identity/IRSA, container, instance metadata) so a relay pod can use its IAM role instead. Default: `buzz_dev` / `buzz_dev_secret`. | `buzz_dev` / `buzz_dev_secret` |
| `BUZZ_S3_BUCKET` | Bucket name, shared by the media path and the git-on-object-storage path. Default: `buzz-media`. | `buzz-media` |
| `BUZZ_S3_REGION` | SigV4 signing region. Falls back to `AWS_REGION`, then `us-east-1`. Not meaningfully checked against MinIO but must match a real AWS S3 endpoint's actual region. | `us-east-1` |
| `BUZZ_S3_ADDRESSING_STYLE` | `path` (default; bucket in the URL path -- required by the bundled MinIO's internal DNS) or `virtual` (bucket in the hostname -- required by providers such as Railway Storage Buckets). Any other value fails config parsing at startup. | `path` |
| `BUZZ_MAX_IMAGE_BYTES` | Max upload size for images. Default 50 MB (`52428800`). Must be > 0. | `52428800` |
| `BUZZ_MAX_GIF_BYTES` | Max upload size for animated GIFs. Default 10 MB (`10485760`). Must be > 0 and <= `BUZZ_MAX_IMAGE_BYTES`. | `10485760` |
| `BUZZ_MAX_VIDEO_BYTES` | Max upload size for video. Default 500 MB (`524288000`). Must be > 0. | `524288000` |
| `BUZZ_MAX_FILE_BYTES` | Max upload size for generic (non-image, non-video) files. Default 100 MB (`104857600`). Must be > 0. | `104857600` |
| `BUZZ_MEDIA_BASE_URL` | Public base URL embedded in returned `BlobDescriptor`s. Must end in exactly one trailing `/media` segment (no trailing slash) or the relay fails to start. | `http://localhost:3000/media` |
| `BUZZ_MEDIA_UPLOAD_RECORDS` | Off by default. Enables an optional `_uploads/` moderation side-channel record per upload. | `true` |
| `BUZZ_MEDIA_UPLOAD_IP_HEADER` / `BUZZ_MEDIA_UPLOAD_PORT_HEADER` | Trusted edge headers to read an uploader's IP/port from. Setting the IP header without `BUZZ_MEDIA_UPLOAD_RECORDS=true`, or the port header without the IP header, or an invalid HTTP header name, all fail startup rather than silently recording nothing. | `cf-connecting-ip` |
| `BUZZ_STORAGE_METRICS` | `off` disables the hourly usage-metrics sweep (and every gauge it emits) entirely -- for a deployment whose relay credentials lack `s3:ListBucket`. Any other value, including unset, leaves it enabled. | `off` |
| `BUZZ_STORAGE_SWEEP_INTERVAL_SECS` / `BUZZ_STORAGE_SWEEP_TIMEOUT_SECS` / `BUZZ_STORAGE_SWEEP_MAX_OBJECTS` | Sweep cadence (default 3600s, floored to 60s), per-attempt timeout (default 120s), and cumulative listed-object cap (default 1,000,000) before an attempt fails and the old snapshot is kept. | `3600` |

Prose describing *how* these values are used, beyond their own definitions
above, lives in the container-level architecture node linked above and in the
source files cited in this node's evidence ledger.

## Bucket key taxonomy

The bucket is a flat namespace; `buzz_media::bucket_index::classify_key`
recognizes five classes, checked in this order, with an explicit,
non-silent `Unknown` catch-all for anything that does not match one of the
four strict shapes:

| Class | Shape | Description | Example |
|---|---|---|---|
| Blob | `{sha256}.{ext}` | The physical, content-addressed media bytes. `ext` is 1-8 mixed-case alphanumeric characters. | `af12...e9.jpg` |
| Thumb | `{sha256}.thumb.jpg` | A generated thumbnail, attributed to the blob's own sha256. | `af12...e9.thumb.jpg` |
| Sidecar | `_meta/{community-uuid}/{sha256}.json` | The (community, sha256) binding -- which community a blob belongs to. | `_meta/3fa8.../af12...e9.json` |
| Auxiliary | `_uploads/{community-uuid}/{sha256}/{ulid}.json` | Optional moderation side-channel record, gated by `BUZZ_MEDIA_UPLOAD_RECORDS`. | `_uploads/3fa8.../af12...e9/01H....json` |
| Unknown | (everything else) | A malformed or unrecognized key. Never coerced into one of the four classes above, so usage gauges stay loud on an unexpected key rather than silently misclassifying it. | -- |

The same bucket also holds git-on-object-storage's content-addressed pack,
manifest and ref-pointer objects, written by `buzz-relay`'s own S3 client
rather than through `MediaStorage` -- see the architecture container node's
*Ownership boundary* section for that split; this table covers only the
key shapes `buzz-media`'s own classifier recognizes.

## Local development and deployment substitutes

| Context | Substitute | Notes |
|---|---|---|
| Local development / CI | MinIO (`docker-compose.yml`, service `minio`) | S3 API on host port `9000`, console on `9001`. A one-shot `minio-init` sidecar creates the `buzz-media` bucket and sets it non-public before dependent services start. |
| Helm chart, `quickstart` profile | In-cluster MinIO subchart/Deployment | Single replica, no HA, autogenerated credentials, chart-default bucket `buzz-media`. Eval-only, not production-hardened. |
| Helm chart, `production` profile (default) | Externally managed S3-compatible service | Configured via `s3.endpoint`/`BUZZ_S3_*` rendered from an `existingSecret`; the chart never generates or stores credentials itself. |

## Behavior when the store is unreachable

An S3-side failure on a media `put`/`get`/`delete` call bubbles up through
`buzz_media::error::MediaError`: `StorageError`, `Io` and `Internal` all map
to HTTP `500` with a generic `"internal error"` body (and a
`tracing::error!` log line), so a client sees a server error rather than the
relay crashing or a request hanging silently -- this is asserted by a unit
test in `crates/buzz-media/src/error.rs`. `MediaError::ServiceUnavailable`
(distinct from a raw storage error; also used when a community's write lease
is fenced or lost) maps to `503`.

The relay's `GET /_readiness` probe does **not** include object storage in
its checked set -- it verifies only Postgres, Redis, and the
deletion-serving catalog, each within a shared 2-second timeout. A `MediaStorage::ping()`
method exists on the storage client for exactly this kind of probe, but no
call site in this repository currently invokes it, so an unreachable object
store is not visible through `/_readiness` or `/_liveness`; the first signal
an operator sees is either a `5xx` on an actual upload/download request, or
the hourly storage-sweep's `sweep_ok` gauge dropping to `0` (see below) --
whichever happens first.

The storage sweep itself degrades in a way that favors dashboard stability
over freshness: a cold cache (no sweep has ever succeeded) publishes only
health gauges at `sweep_ok=0`; a warm cache keeps re-publishing its last
good snapshot on every metrics tick even while the newest sweep attempt is
failing, so a transient S3 blip does not blank the per-community storage
gauges. A persistently failing sweep (for example, credentials that lack
`s3:ListBucket`) retries on every usage-metrics tick rather than waiting a
full `BUZZ_STORAGE_SWEEP_INTERVAL_SECS`, so it self-heals as soon as the
underlying cause is fixed, at the cost of one cheap `LIST` call per tick
until then.

## Retention

There is no bucket-level TTL or object-expiration policy anywhere in this
repository's configuration (Helm chart values/templates, `buzz-media`
itself) -- object bytes are retained indefinitely by default. The one
retention mechanism that exists is whole-**community** deletion:
`crates/buzz-deletion` is a durable, heartbeat-leased, staged deletion
engine that, once an operator submits and approves deleting a community,
freezes an inventory of that community's keys and bulk-deletes them from the
bucket using the same tenant-prefix matching `buzz-media` uses to namespace
sidecar and auxiliary keys. It is exposed operator-side as
`buzz-admin deletions submit|list|inspect|approve|abort` (further
subcommands exist and are not enumerated here). There is no per-object or
per-upload expiration independent of a whole-community deletion.

## Boundary

This node does not describe:
- The object-storage container's architecture -- responsibility, technology
  choice, the ownership boundary between `buzz-media` and git-on-object-storage,
  and the git half's CAS/compare-and-swap safety design -- see
  [`architecture-containers-object-storage`](../../architecture/containers/object-storage.md)
  and, for the formal proof, `docs/git-on-object-storage.md`.
- How to accomplish a task step by step -- rotating S3 credentials, migrating
  to a new bucket, or diagnosing/recovering from an unreachable store. The
  last of these is the failure-mode node #1218 and its runbook #1223's
  territory, not yet written at this revision.
- The Blossom/BUD-11 upload-authorization protocol's full semantics -- see
  `crates/buzz-media/src/auth.rs` and the upstream Blossom specification.
- The whole-community deletion engine's staged-lease protocol in full --
  only its touchpoint with object-storage retention is described here.

## Relationships

- `references`: [`architecture-containers-object-storage`](../../architecture/containers/object-storage.md)
  -- this node assumes that container's description of responsibility,
  technology and ownership boundary as background, and does not repeat it.
- `references`: `corpus-template-reference` -- the template this node's shape
  follows.

## Scope and omissions

**This node covers** the object-storage configuration surface an operator
sets at relay startup, the bucket's own key-namespace taxonomy, the local
development and Helm-chart deployment substitutes for the S3-compatible
store, what happens to a request and to the relay's own health signals when
the store is unreachable, and what retention exists (whole-community
deletion) versus what does not (no bucket-level TTL/lifecycle policy).

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The object-storage container's architecture, technology, and ownership boundary | `architecture-containers-object-storage` |
| The git-on-object-storage safety proof (CAS, durability ordering) | `docs/git-on-object-storage.md` |
| The Blossom/BUD-11 auth protocol's full semantics | `crates/buzz-media/src/auth.rs`, the upstream Blossom spec |
| The whole-community deletion engine's staged-lease protocol in full | `crates/buzz-deletion/src/lib.rs` (not yet its own corpus node) |
| A runbook for diagnosing and recovering an unreachable object store | The failure-mode node, issue #1218, and its runbook, issue #1223 -- neither written at this revision |
| What `squareup/block-coder-tf-stacks` actually provisions for staging object storage | That private repository, not present in this checkout |

**Expected but not verified when this node was written:**

- **Whether any client (desktop, mobile, CLI, or an internal operator tool)
  calls `MediaStorage::ping()` outside of `crates/buzz-media` itself.** The
  search behind that claim was a repository-wide grep for `.ping()` inside
  `crates/`; it did not extend to `desktop/` or `mobile/`, which cannot call
  a Rust method directly but could conceivably wrap an equivalent probe
  endpoint this node did not find.
- **Whether `BUZZ_STORAGE_SWEEP_MAX_OBJECTS`'s default cap (1,000,000) has
  ever been exercised against a bucket large enough to hit it.** Its
  behavior at that boundary was read from `storage_sweep.rs`'s own doc
  comments and config-parsing code, not observed against a real bucket of
  that size.
- **What `squareup/block-coder-tf-stacks` provisions for staging object
  storage.** That repository is private and not part of this checkout; this
  node relies on the container-level architecture node's own note that the
  gap exists, rather than re-verifying it independently.
