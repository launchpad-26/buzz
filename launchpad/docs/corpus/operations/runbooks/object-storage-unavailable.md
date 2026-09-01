---
id: operations-runbooks-object-storage-unavailable
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
  - statement: "buzz-media's MediaStorage wraps an S3-compatible bucket via the rust-s3 crate for Blossom media blobs, and buzz-relay's api::git::store module independently constructs its own rust-s3 Bucket client for git pack/manifest objects and the ref-pointer CAS write — two separate client instances inside the one relay binary, both reading and writing the same configured bucket."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/src/storage.rs"
      - "crates/buzz-relay/src/api/git/store.rs"
  - statement: "MediaStorage::new and GitStore::new are both synchronous constructors: they build a Bucket client and resolve credentials (static BUZZ_S3_ACCESS_KEY/BUZZ_S3_SECRET_KEY if both are set, otherwise the AWS default credential chain) without making any network request, so a relay that has just started and logged its storage clients as constructed has not thereby proven it can reach the object store."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/src/storage.rs"
      - "crates/buzz-relay/src/api/git/store.rs"
  - statement: "The relay's /_readiness handler (the Kubernetes readiness probe) checks only Postgres connectivity, a Redis pool checkout, and the deletion-serving catalog; it does not probe object storage at all, so a relay pod already marked Ready gives no signal about whether the configured S3-compatible bucket is currently reachable."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs"
  - statement: "buzz-media's MediaError maps StorageError (the variant every rust-s3 error not otherwise classified, and every I/O error, converts into) and the generic Internal variant to HTTP 500 with a generic JSON body {\"error\": \"internal error\"}, logging the real error server-side at error level; the client-visible response never distinguishes a network-level object-storage outage from any other internal failure."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/src/error.rs"
  - statement: "On the git smart-HTTP surface, hydrate_error_to_response maps every HydrateError other than a resource-limit violation to HTTP 500 with the body 'git backend hydration failed', covering both clone/fetch (upload-pack, read-side hydration) and the read-side of a push (parent-state hydration before CAS); this is the response a client sees when git-side reads cannot reach the object store."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/transport.rs"
  - statement: "On a push, once receive-pack itself has succeeded, a CasError other than Conflict (409, lost race), ManifestInvalid (400) or ResourceLimit (413) -- i.e. a Backend, ManifestReadFailed, or PackCapture failure during cas_publish -- is logged at error level and returned to the git client as HTTP 500 with the body 'git backend error'; no pointer is written in that case, so the push is not partially applied."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/transport.rs"
      - "crates/buzz-relay/src/api/git/cas_publish.rs"
  - statement: "Git object writes are create-only, content-addressed pack/manifest writes (If-None-Match: *), and the current state of a ref is one mutable manifest pointer updated by an object-store conditional PUT used as compare-and-swap; git-on-object-storage has no local-filesystem fallback for ref/object state, so every clone, fetch, and push depends on the object store being reachable, not only large-object transfer."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/store.rs"
      - "docs/git-on-object-storage.md"
  - statement: "At relay startup, unless BUZZ_GIT_CONFORMANCE_PROBE is explicitly set to a value other than the default, the relay runs a conformance probe (repeated read-after-write and CAS races) against the configured object-storage backend before serving any traffic, and a probe failure returns an error from the startup path -- the process does not come up and Kubernetes readiness never opens."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs"
  - statement: "The relay Helm chart's own documentation states plainly that object storage is contacted during relay startup only through that conformance probe: a probe failure is startup-fatal so readiness never opens, and if an operator explicitly disables the probe, /_readiness does not test object storage at all -- configuration is still parsed strictly, but reachability and addressing errors then surface only on the first live storage operation."
    entry_class: FACT
    evidence:
      - "deploy/charts/buzz/README.md"
  - statement: "buzz-relay's storage_sweep module runs an hourly (default; floor 60 seconds via BUZZ_STORAGE_SWEEP_INTERVAL_SECS), leader-only, single-flight background sweep that lists the bucket, and publishes a buzz_storage_sweep_ok Prometheus gauge (1 on the last attempt's success, 0 on failure) on the relay's dedicated metrics endpoint; the entire storage-metrics feature, including that health gauge, is disabled and never emitted when BUZZ_STORAGE_METRICS=off."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/storage_sweep.rs"
      - "crates/buzz-relay/src/metrics.rs"
  - statement: "Because the sweep only reruns on its own interval and only on whichever relay replica currently holds leadership, buzz_storage_sweep_ok can lag a real outage by up to the configured interval, is silent (not present at all) on a deployment with BUZZ_STORAGE_METRICS=off or lacking s3:ListBucket, and exercises only the bucket-listing permission path -- not the media PUT/GET or git CAS-write paths directly."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay/src/storage_sweep.rs"
      - "crates/buzz-relay/src/main.rs"
    confidence: 0.85
  - statement: "buzz-media defines a non-mutating MediaStorage::ping method, documented in its own doc comment as a probe of object-store connectivity and bucket access, implemented as a one-item bucket listing."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/src/storage.rs"
  - statement: "No caller of MediaStorage::ping was found anywhere in this repository's Rust sources outside buzz-media's own module, and neither buzz-admin nor buzz-cli defines any subcommand that touches object storage, so this repository provides no built-in, operator-triggered command to test object-storage connectivity on demand -- confirming reachability from the relay's own network position currently means reaching the configured endpoint directly from that same pod/host/container, not running a repository-provided check."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-media/src/storage.rs"
      - "grep_repo(pattern='\\.ping\\(\\)', scope='crates/') -> matches only buzz-media/src/storage.rs (definition and its own tests) and an unrelated Postgres buzz-db/src/store/usage.rs ping used by crates/buzz-relay/src/router.rs's /_readiness handler"
    confidence: 0.85
  - statement: "The env vars governing object-storage connectivity for both media and git/CAS are documented together under one .env.example heading, 'S3-Compatible Object Storage (media + Git/CAS)': BUZZ_S3_ENDPOINT, BUZZ_S3_ACCESS_KEY, BUZZ_S3_SECRET_KEY, BUZZ_S3_BUCKET, BUZZ_S3_REGION, and BUZZ_S3_ADDRESSING_STYLE, because one configuration block feeds two independent client code paths rather than two separate config surfaces."
    entry_class: FACT
    evidence:
      - ".env.example"
  - statement: "Local development and CI bring up the object store as a MinIO container (S3 API on port 9000, console on port 9001) whose docker-compose healthcheck repeatedly curls http://localhost:9000/minio/health/live without supplying any credential, so the same unauthenticated path is available for an operator to check MinIO's own liveness from inside that compose network."
    entry_class: FACT
    evidence:
      - "docker-compose.yml"
  - statement: "The relay's Helm chart offers a quickstart profile bundling a single-replica, non-HA, in-cluster MinIO for eval/demo use, and a production profile that instead expects an externally managed S3-compatible service supplied via s3.endpoint/BUZZ_S3_* in an existingSecret with no chart-side credential generation; the bundled MinIO exposes no equivalent documented health path in the chart's own README beyond what the underlying MinIO image provides."
    entry_class: FACT
    evidence:
      - "deploy/charts/buzz/README.md"
  - statement: "The addressing style must match the provider -- path style for the bundled MinIO, whose in-cluster Service DNS resolves only one endpoint hostname and not per-bucket subdomains, and virtual-hosted style for AWS-style providers such as Railway Storage Buckets -- and the configured region must match the provider's actual credential region for a non-MinIO backend, or requests are signed with the wrong SigV4 scope and rejected; both settings fail chart rendering and relay startup when given an unrecognized value, not just a wrong one."
    entry_class: FACT
    evidence:
      - "deploy/charts/buzz/README.md"
      - "crates/buzz-media/src/config.rs"
  - statement: "This repository's own AGENTS.md documents squareup/block-coder-tf-stacks as the separate, private repository whose Terraform + ArgoCD pipeline deploys the relay's Helm chart to the staging Kubernetes cluster; that repository is not part of this checkout, so what it specifically provisions for staging object storage (a managed bucket, an IAM role, network egress rules, or something else) cannot be verified from here."
    entry_class: FACT
    evidence:
      - "AGENTS.md"
  - statement: "This node was written using launchpad/docs/corpus/templates/runbook.md, which was already merged on origin/launchpad at the recorded revision and directs a runbook to state a trigger, severity and impact, diagnosis, mitigation and resolution, and escalation, each traceable to the Google SRE Workbook's playbook definition, plus a scope-and-omissions section."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/templates/runbook.md"
  - statement: "This repository's root AGENTS.md states, under its fork-notice section, that this checkout operates Buzz rather than developing it, and that genuine product bugs in Buzz still belong at block/buzz's own issue tracker rather than being fixed inside this fork."
    entry_class: FACT
    evidence:
      - "AGENTS.md"
relationships:
  - type: implements
    target: corpus-template-runbook
---

# Runbook: object storage unavailable

What to do when the relay's configured S3-compatible object store cannot be
reached, or rejects the relay's requests, while messaging over Postgres/Redis
continues to work. This node is the on-call response; it does not restate the
failure-mode analysis of *why* object storage fails in the ways it does —
that is a separate, not-yet-merged corpus task (see *Scope and omissions*).

## Trigger

Any of the following is this runbook's trigger:

- **Relay will not start / pod never becomes Ready**, and the relay's own log
  around startup contains `git conformance probe failed: ...`. At startup,
  unless `BUZZ_GIT_CONFORMANCE_PROBE` has been explicitly turned off, the
  relay runs a conformance probe against the configured object-storage
  backend before serving any traffic; a probe failure is fatal to startup and
  the process does not come up, so Kubernetes readiness never opens.
- **Git operations fail live** against an already-running relay: `git clone`,
  `git fetch`, or `git push` against this relay's smart-HTTP endpoints return
  `500` with a body of `git backend hydration failed` (read-side: clone,
  fetch, or a push's pre-CAS parent-state read) or `git backend error`
  (write-side: a push whose receive-pack succeeded but the object-store CAS
  publish then failed for a reason other than a lost race, an invalid
  manifest, or a resource limit).
- **Media upload/download fails live**: `PUT /upload`, `PUT /media/upload`,
  or `GET`/`HEAD /media/{sha256_ext}` return `500` with a generic JSON body
  `{"error": "internal error"}`. buzz-media's error type collapses every
  object-store and I/O failure into that one generic response and logs the
  real cause only server-side, so the client-visible error does not by
  itself distinguish an object-storage outage from any other internal
  failure.
- **`buzz_storage_sweep_ok` reads `0`** on the relay's Prometheus metrics
  endpoint (when `BUZZ_STORAGE_METRICS` has not been set to `off`). This is a
  *lagging* signal, not a real-time one — see *Diagnosis*.

**What does not trigger this runbook.** `/_readiness` failing on its own is
*not* evidence of an object-storage problem: that handler checks only
Postgres connectivity, a Redis pool checkout, and the deletion-serving
catalog. It never probes object storage, so a pod that is marked Ready gives
no information either way about whether the bucket is reachable, and a pod
that is *not* Ready points at Postgres or Redis, not at this runbook, unless
the specific startup-fatal conformance-probe log line above is also present.
`git service busy` (`503`, with a `Retry-After` header) is the git-subprocess
concurrency semaphore rejecting a request under load — an unrelated failure
mode that happens to share the git surface.

## Severity and impact

**If the relay was already running and object storage becomes unreachable
after startup:** messaging, presence, typing indicators, search, and every
other Postgres/Redis-backed capability continue to work normally. Only the
two capabilities that read or write the shared bucket degrade: media
upload/download (every request fails) and git clone/fetch/push (every
request fails). No partial git state is written — a failed CAS publish
leaves no pointer written, so a failed push does not corrupt the repository;
it simply does not land.

**If a relay pod restarts (or a new one is scheduled) while object storage is
still unreachable:** the conformance probe reruns and fails again, so the pod
crash-loops and never becomes Ready. In a multi-replica deployment this is
total git/media *and* WebSocket/HTTP unavailability for every replica that
restarts during the outage, escalating what was a partial-feature outage into
a full one for any pod that cycles.

**If the deployment is the Helm chart's quickstart profile** (bundled,
single-replica, non-HA MinIO, intended for eval/demo use), there is no
automatic failover for the object store itself — its own pod failing is the
object-storage outage, and recovery depends on that one pod being
rescheduled or repaired.

## Prerequisites

- Shell or `kubectl exec` access to the relay's own pod/container (or, in
  local development, to a shell on the docker-compose network), because
  confirming connectivity means reaching the configured endpoint from the
  relay's own network position, not from an operator's workstation.
- Read access to the relay's configuration (to confirm which environment
  variables are set, without needing to read their values — see
  *Diagnosis*).
- Knowledge of which deployment profile applies: local/CI docker-compose
  MinIO, the Helm chart's quickstart (bundled MinIO) profile, or the Helm
  chart's production profile against an externally managed bucket.
- Access to the relay's logs and, if scraped, its Prometheus metrics.

## Diagnosis

1. **Read the relay's own logs first.** They name the failing code path
   directly and distinguish a startup-fatal probe failure
   (`git conformance probe failed: ...`) from a live degradation
   (`push failed pre-response`, `hydrate failed`, or `media storage error`
   at error level from buzz-media). The underlying error string from the S3
   client (timeout, connection refused, DNS failure, `403`/`AccessDenied`,
   `SignatureDoesNotMatch`, etc.) is logged alongside these and is the
   fastest way to tell "unreachable" apart from "reachable but rejecting the
   request."
2. **Do not trust `/_readiness` either way.** It does not probe object
   storage at all (see *Trigger*, above), so a Ready pod is not evidence of
   storage health and a non-Ready pod needs its own reason checked
   (Postgres/Redis) before this runbook applies.
3. **Check `buzz_storage_sweep_ok` on the metrics endpoint, with its limits
   in mind.** A `0` is corroborating evidence of an object-storage problem
   reachable via bucket listing; a `1` is *not* proof of health right now —
   the sweep is hourly by default, runs only on whichever replica currently
   holds leadership, is entirely absent when `BUZZ_STORAGE_METRICS=off` or
   the relay's credentials lack `s3:ListBucket`, and exercises only the
   listing permission, not the media/git read-write paths a client actually
   uses. Treat it as a lagging signal, not a live probe.
4. **Confirm connectivity from the relay's own network position** — not from
   an operator's laptop, which may have a different network path or DNS
   view:
   - **Self-hosted MinIO (local/CI docker-compose, or the Helm chart's
     bundled quickstart MinIO):** from a shell with access to the same
     network the relay uses (the compose network, or `kubectl exec` into the
     relay pod or a debug pod on the same cluster network), reach the
     configured endpoint's MinIO liveness path directly, e.g.
     `curl -f <endpoint>/minio/health/live` — this path takes no credential,
     mirroring the docker-compose healthcheck already used for the local
     MinIO container. A failure here means the MinIO process itself is down
     or unreachable on the network, independent of the relay's credentials.
   - **Managed bucket (production profile: AWS S3, Railway Storage Buckets,
     or similar):** this repository defines no equivalent unauthenticated
     health path for a managed provider, and no `buzz-admin`/`buzz-cli`
     subcommand exercises object storage at all. Confirming reachability
     means either testing basic network egress from the relay's pod/host to
     the provider's endpoint hostname and port (DNS resolution, TCP connect,
     TLS handshake) with standard tools available in that environment, or
     checking the provider's own status page/console for an outage. Neither
     is scripted anywhere in this repository today.
5. **Check which configuration variables are set, without printing their
   values.** Confirm presence and shape, not content, of `BUZZ_S3_ENDPOINT`,
   `BUZZ_S3_ACCESS_KEY`, `BUZZ_S3_SECRET_KEY`, `BUZZ_S3_BUCKET`,
   `BUZZ_S3_REGION`, and `BUZZ_S3_ADDRESSING_STYLE` (all six live under one
   `.env.example` heading covering both media and git/CAS). Two
   configuration mistakes look exactly like an outage but are not:
   - **Addressing style mismatched to the provider.** Path style is required
     for the bundled MinIO (its Service DNS resolves one hostname, not a
     per-bucket subdomain); virtual-hosted style is required for AWS-style
     providers such as Railway Storage Buckets. The wrong style produces
     request failures that read like unreachability.
   - **Region mismatched to the provider's actual credential region** for a
     non-MinIO backend — requests are then signed with the wrong SigV4 scope
     and the provider rejects them, which also presents as the bucket being
     unreachable rather than as a signing error.
   Static credentials (`BUZZ_S3_ACCESS_KEY`/`BUZZ_S3_SECRET_KEY`) must be
   configured together or both left empty; leaving exactly one set fails
   client construction immediately with a config error rather than silently
   falling back to the AWS credential chain.
6. **Rule out a startup-time-only false negative.** Because the relay's own
   storage-client constructors are synchronous and perform no network
   request, a log line confirming the client was constructed proves only
   that configuration parsed, never that the endpoint is reachable. The only
   point object storage is actually contacted at startup is the conformance
   probe described in *Trigger*.

## Mitigation and resolution

**Self-hosted MinIO (local/CI, or the Helm chart's bundled quickstart
profile):**

- If the MinIO container/pod itself is down or crash-looping, restart or
  reschedule it (`docker compose restart minio` in local development; for
  the quickstart profile, whatever the cluster's normal pod-recovery path is
  for a single-replica Deployment). Because the quickstart MinIO is
  explicitly documented as non-HA and single-replica, there is no automatic
  failover to fall back on — restoring that one instance *is* the recovery.
- If MinIO is up but the relay still cannot reach it, re-check the six
  configuration variables above for a mismatch (addressing style, region,
  endpoint) before assuming a network partition.

**Managed bucket (production profile):**

- Check the provider's own status page or console first — this is an
  external dependency this repository does not operate.
- If credentials were recently rotated, confirm the Secret named by the
  chart's `secrets.existingSecret` (or the equivalent environment
  configuration outside the chart) actually carries the current
  `BUZZ_S3_ACCESS_KEY`/`BUZZ_S3_SECRET_KEY` pair — without printing them —
  and that the relay was restarted or reloaded after the rotation.
- For the staging deployment specifically, this repository's own `AGENTS.md`
  names `squareup/block-coder-tf-stacks` as the separate, private repository
  whose pipeline provisions the relay's Kubernetes deployment; what it
  specifically provisions for object storage (managed bucket, IAM role,
  network egress) is not verifiable from this checkout, so escalate to
  whoever owns that pipeline rather than guessing at its configuration here.

**If the relay is crash-looping on the startup conformance probe and
restoring object storage will take longer than is acceptable for
non-git/media traffic:** setting `BUZZ_GIT_CONFORMANCE_PROBE` to a
non-default value skips that startup gate, letting the relay start and serve
Postgres/Redis-backed traffic (messaging, presence, search) while git and
media continue to fail live per *Trigger*, instead of the whole pod refusing
to start. Treat this as a deliberate, escalated, temporary decision, not a
default response: the probe exists specifically to admit only a backend that
satisfies the linearizable compare-and-swap property git-on-object-storage's
safety proof depends on, and skipping it does not make the underlying object
store reachable — it only changes which parts of the relay are willing to
run without it.

## Verification of recovery

- **Startup path:** the relay's log shows the conformance probe passing
  (`git object-store backend admitted: A3 conformance probe passed`) and the
  pod becomes Ready.
- **Live path:** perform one benign operation against each affected surface
  — a `git ls-remote` (or `clone`) against a test repository this relay
  hosts, and a `HEAD` request for a known-existing media blob — and confirm
  both return success rather than `500`.
- **`/_readiness` returning `ready` is not sufficient evidence on its own**,
  because it never checked object storage in the first place (see
  *Trigger*); use it only to confirm Postgres/Redis are unaffected, not to
  confirm this incident is over.
- If scraped, expect `buzz_storage_sweep_ok` to return to `1` on the next
  sweep tick, which can lag actual recovery by up to the configured sweep
  interval (default one hour, floor sixty seconds) and only on the current
  leader replica — a `0` shortly after recovery is not necessarily a sign
  recovery failed.

## Escalation

- **Self-hosted MinIO the operator controls directly** (local development,
  or a cluster this cohort operates): escalate to whoever owns that
  cluster/compose environment if restarting the MinIO instance does not
  restore connectivity within a few minutes.
- **A managed bucket, or the staging Kubernetes deployment**: escalate to
  the provider's support/status channel, or to whoever owns
  `squareup/block-coder-tf-stacks` (this repository's own `AGENTS.md` names
  it as the pipeline that deploys the relay's Helm chart to staging) — this
  repository's checkout cannot diagnose that pipeline's own provisioning.
- **If the underlying cause turns out to be a defect in how the relay itself
  handles object-storage failure** (as opposed to the object store being
  genuinely down or misconfigured) — for example, an error path that should
  degrade more narrowly than it does — that is upstream product behavior.
  Per this fork's own operating rule, this cohort operates Buzz and does not
  develop it: file a genuine product defect at
  [block/buzz/issues](https://github.com/block/buzz/issues) rather than
  attempting a code fix from this runbook.

## Evidence to preserve

Before restarting the relay or the object store (either can overwrite the
log lines and metric samples that show what actually happened), capture:

- The relay's own log lines from the incident window — specifically the
  conformance-probe failure line (startup) or the `push failed pre-response`
  / `hydrate failed` / `media storage error` lines (live degradation), which
  carry the underlying S3-client error string.
- A snapshot of `buzz_storage_sweep_ok` and `buzz_storage_sweep_failures`
  over the incident window, if this deployment scrapes the relay's
  Prometheus endpoint — this is the only time-series evidence this
  repository emits for object-storage health, with the staleness caveats
  noted in *Diagnosis*.
- Which of the six configuration variable **names** (never values) were
  confirmed present and which addressing-style/region choice was in effect,
  so a later reviewer does not have to re-derive the configuration from a
  possibly-since-changed deployment.
- For a managed bucket: the provider's own status-page incident reference or
  timestamp, since this repository has no dashboard of its own for that
  dependency to link instead.

## Scope and omissions

**This node covers** recognizing that object storage is unreachable or
misbehaving, telling that apart from unrelated failures that present
similarly, confirming connectivity from the relay's own network position for
both a self-hosted MinIO and a managed-bucket deployment, the configuration
variables to check, mitigation and escalation paths for each deployment
shape this repository supports, and how to verify recovery.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Root-cause analysis of *why* object storage becomes unreachable, and a systematic failure-mode-by-failure-mode reference | A separate, sibling operations task (`operations/reliability/object-storage-failure.md`) that is open and unmerged at this node's recorded revision — not linked here for that reason, and its analysis is not restated |
| The formal safety proof for git-on-object-storage (why the CAS pointer scheme is correct) | `docs/git-on-object-storage.md` (itself marked `draft`) |
| The object-storage container's general architecture, ownership boundary, and interfaces outside a failure | `launchpad/docs/corpus/architecture/containers/object-storage.md` |
| What `squareup/block-coder-tf-stacks` actually provisions for staging object storage | that private repository, not present in this checkout |
| A repository-provided, on-demand connectivity check runnable by an operator | Not implemented anywhere in this repository today (see *Diagnosis* and *Expected but not verified*, below) |
| General reliability/observability practice for object storage beyond what this repository's own code and configuration already do | Not this document's place to import a generic ops playbook; only what this repository actually implements is described above |

**Expected but not verified when this node was written:**

- **No real object-storage outage was reproduced against a running relay or
  MinIO instance while writing this node.** Every claim above about error
  responses, the conformance probe, and the sweep gauge was verified by
  reading the code paths that produce them, not by inducing a live failure
  and observing the described behavior end to end.
- **Whether `MediaStorage::ping` is reachable through any operational tool
  this repository does not track in its own Rust sources** (an external
  script, a runbook-adjacent tool in a private ops repository, etc.) was not
  checked — only this repository's own sources were searched.
- **What a managed provider's outage actually looks like from inside a
  relay pod** (specific error strings, timeout behavior, retry semantics of
  the underlying `rust-s3`/`reqwest` stack) was not exercised against a real
  provider; the *Diagnosis* section names what to check, not what a specific
  provider's failure will literally print.
- **Whether `squareup/block-coder-tf-stacks` provisions staging object
  storage as a managed AWS S3 bucket, with what IAM boundary, or something
  else entirely** — that private repository is not part of this checkout.
