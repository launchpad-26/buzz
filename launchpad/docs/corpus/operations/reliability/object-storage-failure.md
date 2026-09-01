---
id: operations-reliability-object-storage-failure
type: operations
status: draft
origin: launchpad
audiences:
  - operator
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 473205a7457b208455f188847bfb27b01aa83cac."
    entry_class: FACT
    evidence:
      - "commit 473205a7457b208455f188847bfb27b01aa83cac"
  - statement: "buzz-media's MediaStorage wraps rust-s3 and implements no retry logic on any of its operations (put, put_file, get, get_range, get_stream, head, head_with_metadata, delete, delete_objects, list_page, list_prefix_page, list_prefix_versions_page): every method makes exactly one underlying S3 call and maps its outcome directly, with no loop, no backoff and no retry count anywhere in the file."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/src/storage.rs"
  - statement: "MediaStorage's get, get_range, get_stream, head and head_with_metadata each match the backend's HttpFailWithBody(404, _) case to MediaError::NotFound; every other backend error (network failure, a 5xx from the object store, a credential rejection, malformed XML on the listing endpoints) is folded into MediaError::StorageError(String), carrying the backend's own error text."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/src/storage.rs"
  - statement: "MediaError's IntoResponse implementation maps NotFound to HTTP 404, and Io and StorageError (alongside the unrelated Internal variant) to a single HTTP 500 response with the fixed body {\"error\": \"internal error\"} -- the backend's own error text captured in StorageError is logged via tracing::error but never placed in the client-visible response body."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/src/error.rs"
  - statement: "crates/buzz-relay/src/api/media.rs's upload_blob, get_blob and head_blob handlers call MediaStorage's put/put_file/get_stream/get_range/head_with_metadata methods and propagate any MediaError via the ? operator with no additional handling specific to a storage-layer failure -- a storage outage during upload, download or a HEAD request reaches the client exactly as MediaError::IntoResponse renders it, with no distinct code path for 'the backend is down' versus 'the backend is misbehaving'."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/media.rs"
  - statement: "Neither crates/buzz-media/src/storage.rs nor the MediaConfig struct in crates/buzz-media/src/config.rs contains any occurrence of the word 'timeout', and MediaConfig defines no connect-timeout, request-timeout or retry-count field of any kind -- the media S3 client carries no repository-configured request timeout distinct from whatever default the underlying rust-s3/reqwest stack applies."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/src/storage.rs"
      - "crates/buzz-media/src/config.rs"
  - statement: "crates/buzz-media/src/upload.rs writes the content-addressed blob object before the community-scoped sidecar object, and its own comment states the omission of a rollback is deliberate: 'On failure we intentionally do NOT delete the orphan blob -- concurrent uploads of the same hash could race and delete a blob that another request is about to reference via its sidecar,' noting that orphan blobs are bounded by the upload size limit and cheap, with a future background GC job left to sweep them; a moderation record write and metadata generation can independently fail before the sidecar write, each leaving the same kind of orphan."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/src/upload.rs"
  - statement: "buzz-media's read_sidecar_mime collapses an absent sidecar and a storage read failure into the same None outcome, and its own doc comment states this is deliberate so that 'an A-bound request cannot distinguish a B-only blob from a missing blob' -- the same collapse means a blob written but never gaining a sidecar (per the orphan case above) is unreachable through any public read path, not merely slow to appear."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/src/storage.rs"
  - statement: "crates/buzz-relay/src/main.rs runs a git object-store conformance probe (testing linearizable conditional writes, axiom A3) before the relay begins serving traffic; the probe is enabled by default, configurable off via BUZZ_GIT_CONFORMANCE_PROBE=false, and a failed probe returns an error that is propagated out of main, aborting relay startup entirely -- a backend that cannot satisfy the axiom prevents the process from starting, not merely from serving git traffic."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs"
  - statement: "docs/git-on-object-storage.md describes its own conformance probe as a 'deployment admission gate' run once, at startup, against the configured backend, and states explicitly that passing it 'does not prove the universal axiom' for all future traffic -- the probe is a one-time admission check, not a continuous runtime health signal, so a backend that degrades its conditional-write behavior after startup is not re-probed."
    entry_class: FACT
    evidence:
      - "docs/git-on-object-storage.md"
  - statement: "crates/buzz-relay/src/api/git/hydrate.rs's HydrateError has no variant distinguishing a transport-level backend failure from any other kind of backend error; a StoreError of any kind (including a network failure or an S3 5xx) reaches the caller identically as HydrateError::Store, while a genuinely absent repository is signalled by hydrate_for_read returning Ok(None) rather than any HydrateError variant at all."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/hydrate.rs"
  - statement: "crates/buzz-relay/src/api/git/transport.rs's hydrate_error_to_response maps HydrateError::ResourceLimit to HTTP 413 and every other HydrateError variant -- including a backend/transport failure carried as HydrateError::Store -- to a single HTTP 500 response with the fixed body 'git backend hydration failed'; the underlying error is logged via tracing::error but not placed in the response body, and pointer-absent (hydrate_for_read returning Ok(None)) is handled separately as a 404 before this function is ever reached."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/transport.rs"
  - statement: "On the git write path, crates/buzz-relay/src/api/git/transport.rs's finalize_push_inner maps a lost CAS race (CasError::Conflict) to HTTP 409 with the message 'push superseded by a concurrent writer; pull and retry'; CasError::ManifestInvalid to HTTP 400; CasError::ResourceLimit to HTTP 413; and every remaining CasError variant (Backend, PackCapture, ManifestReadFailed) to a single HTTP 500 response with the fixed body 'git backend error'."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/transport.rs"
  - statement: "crates/buzz-relay/src/api/git/cas_publish.rs performs no retry when its own CAS write loses the race: its module comment states the losing push's receive-pack output was derived against a now-superseded parent, so reusing it would violate the design's Inv_RefDerivedFromParent invariant, and that the only safe retry is the client re-running git push, which re-hydrates against the current pointer state."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/cas_publish.rs"
  - statement: "docs/git-on-object-storage.md states that a bounded retry layer for transport-level object-store errors is 'parked, not closed' and that v1 ships without one, and states as a non-negotiable rule that any future retry layer may retry only pre-classification network errors and must never retry a classified Ok(2xx), LostRace(412), or NotFound(404) outcome, because retrying a classified outcome 'would change the TLA action and break the proof.'"
    entry_class: FACT
    evidence:
      - "docs/git-on-object-storage.md"
  - statement: "The git HTTP surface bounds its own local git-subprocess execution with fixed tokio::time::timeout wrappers -- 120 seconds for ref advertisement (INFO_REFS_TIMEOUT), 300 seconds for upload-pack/receive-pack (PACK_OPS_TIMEOUT), 300 seconds for post-push pack capture (PACK_CAPTURE_TIMEOUT), and 600 seconds for pack compaction (PACK_COMPACTION_OPERATION_TIMEOUT) -- each mapped to HTTP 504 on expiry; these wrap the local git binary's own runtime and do not wrap the S3 GET/PUT/CAS-PUT calls that hydrate_for_read, hydrate_for_write and cas_publish issue before or after the subprocess runs."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/transport.rs"
      - "crates/buzz-relay/src/api/git/cas_publish.rs"
  - statement: "crates/buzz-relay/src/api/git/store.rs -- the module that issues the actual S3 GET, PUT and conditional-PUT (CAS) HTTP calls for git pack, manifest and pointer objects -- contains no occurrence of the word 'timeout' anywhere in the file, so those calls carry no repository-configured request timeout of their own, distinct from whatever default the rust-s3/reqwest stack applies underneath."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/store.rs"
  - statement: "crates/buzz-relay/src/router.rs's readiness_handler (mounted at /_readiness) checks only three things under a fixed 2-second timeout -- Postgres connectivity via state.db.ping(), Redis pool connectivity, and the deletion-serving catalog via state.db.validate_deletion_serving_catalog() -- and reports {\"status\": \"ready\"} whenever all three succeed; object-storage reachability is never queried by this handler, so a relay whose configured S3 backend is completely unreachable can still report itself ready."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs"
  - statement: "crates/buzz-relay/src/storage_sweep.rs's hourly bucket-usage sweep wraps one whole sweep attempt in tokio::time::timeout (default 120 seconds, configurable via BUZZ_STORAGE_SWEEP_TIMEOUT_SECS), treats a timed-out or otherwise failed attempt as non-fatal -- logged via tracing::error and counted in failures_total -- keeps re-publishing the last successful snapshot from its cache on every usage tick regardless of whether the newest attempt failed, so a transient object-storage blip does not blank the usage-metric dashboards, and retries a failed attempt on the very next usage tick (default cadence, not the full sweep interval); the whole sweep can be disabled with BUZZ_STORAGE_METRICS=off for a deployment whose credentials lack s3:ListBucket."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/storage_sweep.rs"
  - statement: "The HTTP 503 responses that appear on the media surface (MediaError::ServiceUnavailable, raised by serving_write_error and serving_lease_lost) and on the git surface ('git service busy' from a global git-subprocess concurrency semaphore, and 'community writes are fenced' / 'community write lease lost' from finalize_push_inner) originate from the community-deletion serving-write fence and from a request-concurrency semaphore, not from an object-storage backend failure -- a genuine object-storage failure surfaces as 500 on both surfaces (or 404/409/413 in the specific git-CAS cases already recorded above), never as one of these particular 503s."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/media.rs"
      - "crates/buzz-relay/src/api/git/transport.rs"
  - statement: "docs/git-on-object-storage.md's Theorem 1 corollary states that if the process crashes, or a write fails, between any two steps of the push protocol, no client observes success unless the final CAS pointer swap completed, and that an incomplete push 'leaves orphan packs and an unchanged pointer -- wasted bytes, never a visible-but-lost ref change' -- under the stated A1-A3 axioms, an object-storage failure during a git push is described as making the push fail or the ref state stay unchanged, never as corrupting or silently losing already-published ref state."
    entry_class: FACT
    evidence:
      - "docs/git-on-object-storage.md"
  - statement: "This node was written using launchpad/docs/corpus/templates/reference.md, which was already merged on origin/launchpad at the recorded revision and directs a reference-shaped node toward a Reference description paragraph, a structured-entries table (ordered to match the source's own order, not alphabetically), an optional Commands section, an explicit Boundary statement against the concept/explanation and how-to/procedure neighboring forms, a Relationships section, and a Scope and omissions section separating what the node does not cover from what was expected but could not be verified."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/templates/reference.md"
relationships:
  - type: references
    target: architecture-containers-object-storage
---

# Object storage failure: reference

This node catalogues how Buzz's two object-storage consumers -- Blossom media
(`crates/buzz-media`, HTTP handlers in `crates/buzz-relay/src/api/media.rs`)
and git-on-object-storage (`crates/buzz-relay/src/api/git/`) -- behave when
the configured S3-compatible bucket is unreachable or erroring: which HTTP
status a client observes, whether the relay's own process is affected,
whether the failure is retried anywhere in this repository's code, what the
readiness probe reports, and what happens to already-written or in-flight
data. It is a failure-mode reference, read alongside
`architecture-containers-object-storage` (the container this node's failure
surfaces belong to) and `docs/git-on-object-storage.md` (the formal
durability/safety argument the git-write failure behavior below is derived
from). It does not prescribe how an operator should respond to an outage --
see *Boundary*, below.

## Failure surfaces and observed behavior

Ordered by the request lifecycle each surface belongs to: startup admission,
then media read/write, then git read, then git write, then the two
background/monitoring paths.

| Surface | Trigger | Observed behavior | Retried by this code? |
|---|---|---|---|
| Git conformance probe (startup) | Configured backend fails the A3 linearizable-conditional-write check | Relay process aborts startup entirely (the error propagates out of `main`); default-on, disable with `BUZZ_GIT_CONFORMANCE_PROBE=false` | No -- one admission attempt per process start |
| Media upload (`PUT /upload`, `PUT /media/upload`) | `MediaStorage::put`/`put_file`/`put_sidecar` returns a non-404 backend error | HTTP 500, fixed body `{"error": "internal error"}` (backend error text logged, not returned) | No |
| Media download (`GET`/`HEAD /media/{sha256_ext}`) | `get_stream`/`get_range`/`head_with_metadata` returns a non-404 backend error | HTTP 500, same fixed body as upload | No |
| Media object genuinely absent | Backend returns 404 | `MediaError::NotFound` -> HTTP 404 (indistinguishable from "object exists, backend unreachable" only in the sense that both eventually reach the client as a client-facing error, not the same status -- see the row above) | N/A |
| Git read (`info/refs`, `upload-pack`) | `hydrate_for_read` fails on a `StoreError` other than pointer-absent | HTTP 500, fixed body `git backend hydration failed`; pointer-absent is a separate `Ok(None)` path returning 404, not this row | No |
| Git read, resource limit | Stored repo exceeds the relay's configured pack/repo byte budget | HTTP 413 | N/A (not a storage failure) |
| Git write, lost CAS race | Backend returns 412 on the pointer's conditional PUT | HTTP 409, `push superseded by a concurrent writer; pull and retry` | No -- by design; see *Retry policy* below |
| Git write, backend/transport error | `CasError::Backend`, `PackCapture`, or `ManifestReadFailed` | HTTP 500, fixed body `git backend error` | No |
| Git write, manifest validation failure | Workspace produced refs/HEAD/OIDs the manifest validator rejects | HTTP 400 | N/A (not a storage failure) |
| Git write, resource limit | Push would exceed the relay's configured pack/repo byte budget | HTTP 413 | N/A (not a storage failure) |
| Git-subprocess local timeout | The local `git` binary itself hangs (advertise-refs, upload-pack/receive-pack, pack-objects capture/compaction) | HTTP 504 after 120s/300s/300s/600s respectively | N/A -- bounds the subprocess, not the S3 calls around it |
| Readiness probe (`/_readiness`) | Object-storage backend fully unreachable | No effect -- the handler checks only Postgres, Redis, and the deletion-serving catalog; it never queries object storage | N/A |
| Storage usage sweep (hourly, media only) | `list_page` call fails or the whole attempt exceeds its timeout (default 120s) | Non-fatal: logged, `failures_total` incremented, last good snapshot kept serving on dashboards, retried on the next usage tick (not the full sweep interval) | Yes, at tick cadence -- the one surface in this table with any retry behavior |

### Startup admission versus runtime unavailability

The conformance probe (first row above) is the only place this repository
treats an object-storage problem as fatal to the relay process itself.
Everywhere else in the table, a request-time object-storage failure is
scoped to the request that hit it: the relay process keeps running, keeps
accepting new connections, and the readiness probe keeps reporting ready
(see the `/_readiness` row) because it was never wired to check object
storage in the first place.

### Retry policy

Nothing in this repository retries an object-storage call at the point of
failure, with one exception: the hourly media usage sweep, which is a
monitoring/metrics path, not a request-serving one. The git-write path's
absence of retry is a stated design choice, not an oversight --
`docs/git-on-object-storage.md` records that a bounded retry layer is
"parked, not closed" for v1, and states the rule that governs any future
one: it may retry only a pre-classification transport error, never a
classified outcome (a success, a lost-race 412, or a not-found 404),
because retrying a classified outcome would invalidate the protocol's own
safety proof. On the git side the safe retry is the client re-running
`git push`, which re-hydrates against the object store's current state; on
the media side a client whose upload or download failed must itself decide
whether and how to retry, since the relay returns a flat 500 with no
`Retry-After` or backoff guidance for a storage-layer failure specifically
(contrast the semaphore-based 503s in the row below, which do carry
`Retry-After`).

### Data at risk versus merely unavailable

Git: under the A1-A3 axioms `docs/git-on-object-storage.md` states and the
relay's conformance probe admits a backend against, an object-storage
failure during a push either leaves the ref state completely unchanged
(the pointer CAS never completed) or the push completes and is durably
published -- there is no recorded failure mode between those two, per the
design doc's Theorem 1 corollary. Already-published ref state is not placed
at risk by a subsequent object-storage outage; a client simply cannot read
or write until the backend recovers.

Media: a partial upload -- the blob object written, then a later step
(sidecar write, metadata generation, or an optional moderation record)
failing -- deliberately leaves the blob object orphaned rather than
attempting a rollback delete, per `crates/buzz-media/src/upload.rs`'s own
comment on that choice. Because every public read path resolves a blob
through its community-scoped sidecar, an orphaned blob is not reachable by
any client and represents unreferenced storage usage rather than exposed or
corrupted data; the same file's comment names a future background GC job as
the intended cleanup, not anything in this failure path itself.

## Boundary

This node does not describe:

- What an operator should actually do when the object store is down --
  detection, diagnosis, mitigation, recovery verification, and escalation
  are the subject of the sibling runbook, issue #1223
  (`operations/runbooks/object-storage-unavailable.md`), unmerged at the time
  this node was written. This node names the failure modes that runbook
  responds to; it does not prescribe the response.
- Why the object-storage container is shaped the way it is, or how its two
  client code paths relate architecturally -- that is
  `architecture-containers-object-storage`'s subject (see *Relationships*).
- The formal safety proof for the git-on-object-storage protocol -- summarized
  above only as far as it bears on failure behavior; the full axioms, protocol
  steps, and mechanized verification are `docs/git-on-object-storage.md`'s.
- Any alerting rule, dashboard, or SLO for object-storage health. No
  Prometheus alert rule or dashboard definition naming object-storage
  reachability was found anywhere in this repository while researching this
  node -- see *Scope and omissions* for what that absence does and does not
  establish.

## Relationships

- references: `architecture-containers-object-storage` -- the container this
  node's failure surfaces (media, git-on-object-storage, the storage sweep)
  belong to; this node describes how that container's two client code paths
  fail, not what they are or how they are wired.

## Scope and omissions

**This node covers** the observed HTTP/process behavior of Buzz's two
object-storage consumers (Blossom media and git-on-object-storage) when the
configured S3-compatible backend is unreachable or erroring: the startup
conformance-probe gate, per-surface error-to-status mapping for media
upload/download and git read/write, which surfaces retry and which do not,
what the readiness probe does and does not check, the storage sweep's own
failure handling, and what happens to already-written or in-flight data
under each failure.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Operator diagnosis, mitigation, recovery-verification and escalation procedure for an object-storage outage | Issue #1223's runbook, `operations/runbooks/object-storage-unavailable.md`, unmerged at the time this node was written |
| The object-storage container's responsibility, technology, ownership boundary, interfaces, and deployment/data/security implications in general | `architecture-containers-object-storage` |
| The git-on-object-storage protocol's full axioms, proofs, and mechanized verification | `docs/git-on-object-storage.md` |
| Per-endpoint request/response schemas for the media and git HTTP surfaces | `ARCHITECTURE.md`, `crates/buzz-relay/src/api/media.rs`, `crates/buzz-relay/src/api/git/transport.rs` |
| Whether `squareup/block-coder-tf-stacks` (the private Terraform/ArgoCD pipeline that deploys the relay's Helm chart to staging) configures any alerting on the managed S3 bucket it provisions | that private repository, not present in this checkout |

**Expected but not verified when this node was written:**

- **Whether a client-side request timeout is applied to the underlying S3
  HTTP calls by the `rust-s3`/`reqwest` stack itself, beneath the level
  this repository's own code configures.** No timeout field or
  timeout-setting call was found in `crates/buzz-media/src/storage.rs`,
  `crates/buzz-media/src/config.rs`, or `crates/buzz-relay/src/api/git/store.rs`
  -- the three modules that actually issue S3 requests -- but a default
  applied by the HTTP client library underneath them was not independently
  confirmed by inspecting that library's own source or by exercising a
  hung connection against it.
- **No alerting rule or dashboard for object-storage reachability was found
  by searching this repository**, but that search was not exhaustive
  against private, non-checked-out infrastructure repositories
  (`squareup/block-coder-tf-stacks`, `squareup/sprout-backend-blox`) that
  `AGENTS.md` names as part of this fork's deployment pipeline.
- **None of the failure behaviors in the table above were exercised against
  a live, deliberately-degraded object-storage backend** (a stopped MinIO
  container, an injected network partition, or a backend returning sustained
  5xx). Every row is derived from reading the handling code and the design
  document's stated proofs, not from an observed run reproducing the
  failure.
- **Whether the media path's generic 500 response is ever distinguishable
  from a genuinely unhandled internal panic**, since both `MediaError::Internal`
  and `MediaError::StorageError` render the identical fixed body -- this was
  read from `crates/buzz-media/src/error.rs`'s `IntoResponse` implementation
  but not confirmed against a live log correlating a specific 500 response
  to its originating variant.
