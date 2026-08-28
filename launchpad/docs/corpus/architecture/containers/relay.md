---
id: architecture-containers-relay
type: architecture
status: draft
origin: launchpad
audiences:
  - developer
  - operator
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision a44cf52fc740ebebbdd671427480d14f0bce0115 on the launchpad branch."
    entry_class: FACT
    evidence:
      - "commit a44cf52fc740ebebbdd671427480d14f0bce0115"
  - statement: "buzz-relay is an Axum WebSocket server, the only crate that imports and orchestrates buzz-db, buzz-auth, buzz-pubsub, buzz-search, buzz-audit and buzz-workflow directly, and those subsystem crates never call each other -- all cross-subsystem coordination happens through the relay."
    entry_class: FACT
    evidence:
      - "ARCHITECTURE.md"
      - "crates/buzz-relay/Cargo.toml"
  - statement: "The relay is described as the single source of truth for the system: all reads and writes flow through it, with no peer-to-peer event exchange, gossip, or replication between clients."
    entry_class: FACT
    evidence:
      - "ARCHITECTURE.md"
  - statement: "buzz-relay's package description is 'WebSocket relay server for the Buzz communications platform', and it ships as an independently versioned, independently releasable artifact (ghcr.io/block/buzz upstream) rather than inheriting the workspace version."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/Cargo.toml"
  - statement: "AppState (the relay's shared, Arc-wrapped connection state) holds direct handles to buzz-db (Db), a Redis pool (deadpool_redis::Pool), buzz-pubsub's PubSubManager, buzz-auth's AuthService, buzz-search's SearchService, buzz-audit's AuditService, buzz-workflow's WorkflowEngine, a MediaStorage client, and a GitStore -- confirming Postgres, Redis, S3/S3-compatible media storage and a content-addressed git object store as directly connected systems."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/state.rs:630-770"
      - "crates/buzz-media/src/storage.rs:19-21"
      - "crates/buzz-relay/src/api/git/store.rs:170-172"
  - statement: "The relay binds up to four listeners: a TCP app router on BUZZ_BIND_ADDR (default 0.0.0.0:3000), an optional Unix domain socket app listener (BUZZ_UDS_PATH), a health-only TCP listener (default 0.0.0.0:8080), and a Prometheus metrics listener (default 0.0.0.0:9102, already bound by PrometheusBuilder before serve() is called)."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:1248-1405"
      - "crates/buzz-relay/src/config.rs"
  - statement: "The inbound HTTP/WebSocket surface -- WebSocket upgrade or NIP-11 info at GET /, NIP-05 identity at GET /.well-known/nostr.json, health/liveness/readiness probes, POST /events, /query and /count as the generic Nostr-over-HTTP bridge, POST /hooks/{id} for workflow webhooks, PUT/GET/HEAD /media/* (Blossom), and GET/POST /git/{owner}/{repo}/* for git smart HTTP -- is built by build_router and build_health_router."
    entry_class: FACT
    evidence:
      - "ARCHITECTURE.md"
      - "crates/buzz-relay/src/router.rs:33-201"
      - "crates/buzz-relay/src/router.rs:247-254"
  - statement: "readiness_handler's doc comment states the readiness probe checks the shutdown flag plus Postgres and Redis connectivity, and status_handler serves service name, version and uptime at an internal status endpoint."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs:375-414"
      - "crates/buzz-relay/src/router.rs:417-424"
  - statement: "An inter-relay mesh (crate buzz-relay-mesh, an iroh-based peer transport) is an opt-in outbound/inbound seam controlled by BUZZ_MESH: boot_mesh's module doc states it touches nothing when BUZZ_MESH=off, and when enabled it binds an iroh endpoint on BUZZ_MESH_BIND_ADDR, publishes a relay-key-attested ready record to a Redis registry, and runs accept/reconcile/dial/gossip loops against peer relays."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/mesh_boot.rs"
      - "crates/buzz-relay/Cargo.toml"
      - "crates/buzz-relay/src/router.rs:429-436"
  - statement: "The relay drives an outbound mobile push-gateway delivery path: push_runtime.rs is a 'durable NIP-PL event matcher and gateway delivery worker', and config.rs validates an optional BUZZ_PUSH_GATEWAY_DELIVERY_URL as an exact HTTPS /v1/deliveries/apns URL, i.e. a separate push-gateway container this relay calls out to rather than implements."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/push_runtime.rs"
      - "crates/buzz-relay/src/config.rs"
      - "Dockerfile.push-gateway"
      - "deploy/charts/buzz-push-gateway/values.yaml"
  - statement: "A Buzz community (tenant) is selected from the request host before AUTH, EVENT, REQ, REST, media, git, search, workflow or pub/sub handling runs, and unknown hosts fail closed -- this host-derived tenancy boundary is owned and enforced by the relay, not by any of the crates it orchestrates."
    entry_class: FACT
    evidence:
      - "ARCHITECTURE.md"
  - statement: "Auto-applying pending SQL migrations at relay startup is opt-in, gated on the BUZZ_AUTO_MIGRATE environment variable via buzz_auto_migrate_enabled; when unset or falsy, main() logs 'Skipping database migrations because BUZZ_AUTO_MIGRATE is not enabled' rather than running them."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:29-36"
      - "crates/buzz-relay/src/main.rs:189"
      - "crates/buzz-relay/src/main.rs:197"
  - statement: "This is a correction to a summary elsewhere in the repository: root CLAUDE.md's repo-structure table describes migrations/ as 'SQL migrations (auto-applied on relay startup)' without noting the BUZZ_AUTO_MIGRATE gate; the code shows the apply step is opt-in, not unconditional."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay/src/main.rs:29-36"
      - "CLAUDE.md"
    confidence: 0.8
  - statement: "On SIGTERM the relay sets a shutting_down flag (readiness starts returning 503), waits a fixed 5s grace period, then runs a bounded graceful drain -- GRACEFUL_DRAIN_TIMEOUT is 30s -- closing WebSocket connections with an optional per-socket random jitter (BUZZ_DRAIN_JITTER_MS, capped at 20s) before force-exiting; the doc comment computes a worst case of 5s + 30s = 35s from SIGTERM to forced exit."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:1248-1405"
      - "crates/buzz-relay/src/config.rs"
  - statement: "The Helm chart's default terminationGracePeriodSeconds is 60, which the serve() doc comment cross-references as leaving headroom over the 35s worst-case drain, assuming no preStop hook adds further delay."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:1248-1405"
      - "deploy/charts/buzz/values.yaml"
  - statement: "The Helm chart's default relay.livenessProbe and relay.readinessProbe target the health-only listener (service port name 'health', chart default 8080) at /_liveness and /_readiness respectively, matching the router's liveness_handler and readiness_handler paths."
    entry_class: FACT
    evidence:
      - "deploy/charts/buzz/values.yaml"
      - "crates/buzz-relay/src/router.rs:375-414"
  - statement: "The chart's 'Chart-managed secrets' comment block documents DATABASE_URL, READ_DATABASE_URL, REDIS_URL, BUZZ_S3_ACCESS_KEY and BUZZ_S3_SECRET_KEY as the expected external-dependency secret keys, and config.rs's Config::from_env reads exactly those same names (DATABASE_URL, READ_DATABASE_URL, REDIS_URL, BUZZ_S3_ACCESS_KEY, BUZZ_S3_SECRET_KEY) plus BUZZ_RELAY_PRIVATE_KEY for relay identity, confirming the chart's documented contract matches the binary's actual env reads at this revision."
    entry_class: FACT
    evidence:
      - "deploy/charts/buzz/values.yaml"
      - "crates/buzz-relay/src/config.rs:466"
      - "crates/buzz-relay/src/config.rs:469"
      - "crates/buzz-relay/src/config.rs:515"
      - "crates/buzz-relay/src/config.rs:709"
      - "crates/buzz-relay/src/config.rs:739-741"
  - statement: "This fork publishes its own relay container image, ghcr.io/launchpad-26/buzz, built from the repository's own Dockerfile by .github/workflows/docker.yml on relay-v*.*.* tags -- distinct from the upstream ghcr.io/block/buzz image the Helm chart defaults its image.repository to."
    entry_class: FACT
    evidence:
      - "Dockerfile"
      - ".github/workflows/docker.yml"
      - "deploy/charts/buzz/values.yaml"
  - statement: "The Dockerfile's runtime image keeps `git` on PATH because, per its own comment, 'the relay shells out to git for repo hydrate / receive-pack / upload-pack', i.e. the git container-hosting feature depends on the container image bundling a real git binary rather than a pure-Rust implementation."
    entry_class: FACT
    evidence:
      - "Dockerfile"
      - "crates/buzz-relay/src/api/git/store.rs"
  - statement: "AGENTS.md's ecosystem table (root of this repository, not launchpad-authored) names squareup/sprout-oss as the CI pipeline building the relay's internal Docker image to ECR and squareup/block-coder-tf-stacks as the Terraform+ArgoCD deployment of that image to Block's internal staging Kubernetes cluster -- these are Block-internal deployment paths outside this repository's own visible source, separate from this fork's own ghcr.io/launchpad-26/buzz publishing path documented above."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "AGENTS.md ecosystem table (block/buzz root CLAUDE.md, checked into this repository)"
---

# Container: `buzz-relay`

The Buzz relay -- the Rust/Axum WebSocket server that is the system's single
source of truth. This node describes it as a deployable unit: its
responsibility, the technology it is built on, who owns each side of its
boundary, what talks to it and what it talks to, and where its
deployment/data/security surface is documented in depth elsewhere.

**This node describes the container as it exists in `block/buzz` upstream
source at the recorded revision.** Per this fork's own `AGENTS.md`, the fork
"operate[s] Buzz; we do not develop it" -- but the relay's own Dockerfile and
`.github/workflows/docker.yml`, both present in this checkout, show the fork
does build and publish its own image from this source, so that publishing
path is included as fork-verified fact below rather than treated as
out-of-repo.

## Responsibility

The relay is the single point through which every Buzz read and write flows.
There is no peer-to-peer event exchange, gossip, or replication between
clients -- clients connect to one relay over WebSocket (or the HTTP bridge),
and the relay enforces auth, verifies Nostr signatures, persists events,
fans them out to subscribers, indexes them for search, and triggers workflow
automation. It is also the only crate in the workspace that imports and
orchestrates `buzz-db`, `buzz-auth`, `buzz-pubsub`, `buzz-search`,
`buzz-audit` and `buzz-workflow` directly; those crates never call each
other, so every cross-subsystem coordination path runs through the relay.

It additionally owns the multi-tenancy boundary: a Buzz *community* (tenant)
is resolved from the connecting request's host before any AUTH, EVENT, REQ,
REST, media, git, search, workflow, or pub/sub handling runs, and an unknown
host fails closed. That resolution happens once, in the relay, not
independently in each subsystem it calls.

## Technology and ownership boundary

- **Language/runtime:** Rust, built as the `buzz-relay` binary
  (`crates/buzz-relay/src/main.rs`), on the Axum web framework over Tokio.
- **Versioning:** `buzz-relay` is versioned independently of the rest of the
  Cargo workspace and released on its own cadence, reflected in this fork by
  the `relay-v*.*.*` tag trigger that builds and publishes its own image.
- **Ownership boundary:** everything under `crates/buzz-relay/` -- routing,
  connection/session state, admission control, the WebSocket protocol
  handler, mesh boot wiring, and the push-gateway delivery worker -- is the
  relay's own code. Business logic for each subsystem (event storage,
  authn/authz, pub/sub fan-out mechanics, full-text search, the audit hash
  chain, workflow evaluation) is *not* owned here; the relay calls into the
  crate that owns it (`buzz-db`, `buzz-auth`, `buzz-pubsub`, `buzz-search`,
  `buzz-audit`, `buzz-workflow` respectively) and does not reimplement it.

## Inbound interfaces

Listeners bound by the relay process:

| Listener | Default bind | Purpose |
|---|---|---|
| App router (TCP) | `BUZZ_BIND_ADDR`, default `0.0.0.0:3000` | WebSocket (NIP-01 protocol) and the HTTP bridge/media/git surface below |
| App router (Unix domain socket) | `BUZZ_UDS_PATH`, optional | Same app router, for same-host callers that prefer a UDS |
| Health-only router (TCP) | default `0.0.0.0:8080` | `/health`, `/_liveness`, `/_readiness` -- no metrics middleware, no auth, no CORS, no body limit |
| Metrics (TCP) | default `0.0.0.0:9102` | Prometheus scrape endpoint, bound independently via `PrometheusBuilder` |

Selected HTTP/WebSocket routes on the app router:

| Method | Path | Purpose |
|---|---|---|
| GET | `/` | WebSocket upgrade, or NIP-11 relay info for a plain HTTP request |
| GET | `/.well-known/nostr.json` | NIP-05 identity |
| POST | `/events`, `/query`, `/count` | Generic Nostr-over-HTTP bridge (submit / NIP-01 filter query / NIP-45 count) |
| POST | `/hooks/{id}` | Workflow webhook trigger (secret-authenticated) |
| PUT / GET / HEAD | `/media/*` | Blossom media upload/retrieve |
| GET / POST | `/git/{owner}/{repo}/*` | Git smart HTTP (advertisement, fetch, push) |
| GET | `/_mesh` | Live inter-relay mesh status (peer table, connection state), reports `{"enabled": false}` when the mesh is off |

## Outbound interfaces / directly connected containers and systems

Read from `AppState`'s own fields, which is the relay's central shared
handle to every downstream connection:

- **Postgres** (`buzz-db`, via `Db`) -- events, channels, tokens, workflows,
  audit rows; also the target of `buzz-search`'s full-text search (a
  generated `search_tsv` column and GIN index over the same database, not a
  separate search service). `DATABASE_URL` and an optional
  `READ_DATABASE_URL` read-replica.
- **Redis** (`deadpool_redis::Pool`, via `buzz-pubsub`) -- channel-scoped
  `PUBLISH`/`PSUBSCRIBE` fan-out between relay instances/pods, presence,
  typing indicators, and (when the mesh is enabled) the mesh's ready
  registry. `REDIS_URL`.
- **S3 / S3-compatible object storage** (`MediaStorage`, from `buzz-media`)
  -- Blossom media blobs. `BUZZ_S3_ENDPOINT`, `BUZZ_S3_ACCESS_KEY`,
  `BUZZ_S3_SECRET_KEY`, `BUZZ_S3_BUCKET`.
- **Git object store** (`GitStore`, `crates/buzz-relay/src/api/git/`) --
  content-addressed packs/manifests, also backed by the same object storage,
  with a CAS-guarded manifest pointer for writer serialization; the relay
  also shells out to a real `git` binary on the container's `PATH` for
  repo hydrate / receive-pack / upload-pack.
- **Push gateway** (a separate deployable, `Dockerfile.push-gateway` /
  `deploy/charts/buzz-push-gateway/`) -- the relay's own
  `push_runtime.rs` durable delivery worker calls out to it over HTTPS at
  an operator-configured `BUZZ_PUSH_GATEWAY_DELIVERY_URL`
  (`.../v1/deliveries/apns`) to deliver mobile push notifications; the
  relay does not implement APNs delivery itself.
- **Peer relay instances** (opt-in, `BUZZ_MESH`) -- an iroh-based
  peer-to-peer mesh (`buzz-relay-mesh` crate) for inter-relay membership
  gossip and reconciliation, off by default and, per its own module
  documentation, byte-identical to a mesh-less relay when disabled.

## Deployment, data and security implications

- **Deployment.** This fork builds and publishes its own container image,
  `ghcr.io/launchpad-26/buzz`, from this repository's `Dockerfile` via
  `.github/workflows/docker.yml`, triggered on `relay-v*.*.*` tags; the
  Helm chart at `deploy/charts/buzz/` (defaulting `image.repository` to the
  upstream `ghcr.io/block/buzz`) is the deployment shape checked into this
  repository. Upstream's own internal deployment of the relay
  (`squareup/sprout-oss` building to ECR, `squareup/block-coder-tf-stacks`
  applying it to Block's staging Kubernetes cluster via ArgoCD) is
  documented at the level of this repository's own `AGENTS.md` ecosystem
  table and is not re-derived here.
- **Graceful shutdown.** SIGTERM flips a `shutting_down` flag (readiness
  starts failing), a fixed 5s grace period lets Kubernetes stop routing new
  traffic, then a 30s bounded drain closes live WebSockets (with an
  optional per-socket jitter, capped at 20s, to avoid a reconnect
  stampede) before the process force-exits -- a documented worst case of
  35s from signal to exit, which the chart's default
  `terminationGracePeriodSeconds: 60` is sized to cover with headroom.
- **Health surface for orchestration.** Liveness and readiness are served
  from the dedicated health-only listener, deliberately without auth,
  CORS or the metrics middleware applied to the main app router; readiness
  additionally checks Postgres and Redis connectivity, not only the
  shutdown flag.
- **Multi-tenancy / security boundary.** Community (tenant) resolution from
  the request host happens once, in the relay, before any handler runs, and
  an unrecognized host fails closed -- this is the enforcement point for
  cross-community isolation referenced by every downstream subsystem the
  relay calls.
- **Data migrations.** SQL migrations under `migrations/` are applied by
  `buzz-db`'s migration runner, but only when the relay's own
  `BUZZ_AUTO_MIGRATE` environment variable is set to a truthy value; left
  unset, relay startup explicitly skips applying pending migrations rather
  than applying them automatically.

## Implementation, verification and neighboring references

- **Implementation:** `crates/buzz-relay/` (this container's own code);
  `ARCHITECTURE.md` §"buzz-relay -- The Server" for the fuller endpoint
  table, `AppState`/`ConnectionState` shape, and protocol pipeline this
  node deliberately does not restate in full.
- **Deployment/build:** `Dockerfile`, `.github/workflows/docker.yml`,
  `deploy/charts/buzz/` (Helm chart, values, probes, secrets contract).
- **Verification:** `crates/buzz-test-client/tests/e2e_relay.rs` and
  sibling e2e suites exercise the relay's WebSocket/HTTP surface end to
  end; see `TESTING.md` for the multi-agent E2E guide this node does not
  duplicate.
- **Neighboring corpus nodes:** none of this node's plausible neighbors
  (a data-store/Postgres node, a deployment/Helm node, a security/tenancy
  node) are merged into the corpus at the recorded revision, so this node
  carries no `relationships` entries -- see `node.schema.json`'s
  requirement that a relationship's `target` resolve to an id some loaded
  node actually carries. A future pass should add `references`/`implements`
  edges once those sibling nodes exist.

## Scope and omissions

**Covered:** the container's responsibility, technology, ownership
boundary, inbound listeners and routes, outbound/connected systems,
graceful-shutdown and health-probe behavior, the migration-apply gate, and
this fork's own image-publishing path.

**Not covered, and left as gaps rather than restated elsewhere:**

- The full Nostr wire protocol (message types, the EVENT pipeline stages,
  kind registry) -- owned by `ARCHITECTURE.md` §2-3 and by
  `crates/buzz-core/src/kind.rs`; this node only names the endpoints that
  carry that protocol.
- The internal shape and behavior of each connected subsystem crate
  (`buzz-db`, `buzz-auth`, `buzz-pubsub`, `buzz-search`, `buzz-audit`,
  `buzz-workflow`, `buzz-media`) -- each is its own container/node once
  authored; this node names them only as directly connected systems.
- Block's internal (`squareup/*`) build-to-ECR and Terraform/ArgoCD
  deployment mechanics -- outside this repository's visible source; only
  the existence and ownership of those pipelines, as already recorded in
  this repository's `AGENTS.md`, is cited here.
- Whether `deploy/charts/buzz/` is the chart this fork's own production
  deployment actually uses, versus a reference chart maintained alongside
  the image -- not established from source read for this node; the fork's
  own operational deployment specifics belong in `launchpad/`, per this
  repository's `CLAUDE.md`.
