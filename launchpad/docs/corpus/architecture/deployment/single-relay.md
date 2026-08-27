---
id: architecture-deployment-single-relay
type: architecture
status: draft
origin: launchpad
audiences:
  - operator
  - developer
evidence:
  - statement: "This node was authored and checked against repository revision a44cf52fc740ebebbdd671427480d14f0bce0115."
    entry_class: FACT
    evidence:
      - "commit a44cf52fc740ebebbdd671427480d14f0bce0115"
  - statement: "deploy/compose/ is described by its own README as the single-node/VPS deployment bundle, intentionally separate from the root docker-compose.yml which is local development infrastructure only."
    entry_class: FACT
    evidence:
      - "deploy/compose/README.md"
  - statement: "\"Single-relay\" is an existing term of art in this repository: the relay URL/domain is authoritative for a community, and today's single-relay deployment has exactly one community behind that URL (a hosted operator can run many communities behind many domains, each still resolved from a single relay process per host)."
    entry_class: FACT
    evidence:
      - "README.md"
      - "NOSTR.md"
  - statement: "The production Compose stack (deploy/compose/compose.yml) defines five services on one Docker host: relay, postgres, redis, minio, and a one-shot minio-init job; an optional sixth service, caddy, is added only when compose.caddy.yml is layered in for TLS termination."
    entry_class: FACT
    evidence:
      - "deploy/compose/compose.yml"
      - "deploy/compose/compose.caddy.yml"
  - statement: "The relay container is built from the repository's root Dockerfile, which compiles buzz-relay, buzz-admin, and buzz-pair-relay from Rust 1.95, bundles the web + admin-web static builds, and publishes ghcr.io/launchpad-26/buzz:<tag> as a debian-slim runtime image running as a non-root buzz:buzz user."
    entry_class: FACT
    evidence:
      - "Dockerfile"
  - statement: "The relay image is built and published by .github/workflows/docker.yml on push to the launchpad branch (tags :launchpad and :sha-<full-commit>) and on relay-v*.*.* tags (tags :{version}, :{major.minor}, :{major}); the image name is fixed to ghcr.io/launchpad-26/buzz."
    entry_class: FACT
    evidence:
      - ".github/workflows/docker.yml"
  - statement: "deploy/compose/README.md documents that normal VPS deployment consumes that prebuilt ghcr.io/launchpad-26/buzz image and does not build the Dockerfile locally, and that BUZZ_IMAGE has no default — Compose fails to start without an explicit digest or full 40-character commit-SHA tag."
    entry_class: FACT
    evidence:
      - "deploy/compose/README.md"
  - statement: "launchpad/deploy/run.sh is a guard that validates deploy/compose/.env selects an immutable ghcr.io/launchpad-26/buzz image, rejects the upstream ghcr.io/block/buzz image, and then delegates to deploy/compose/run.sh for all actual orchestration (start, stop, restart, pull, upgrade, logs, status, config, backup-hint, add-member, remove-member, list-members)."
    entry_class: FACT
    evidence:
      - "launchpad/deploy/README.md"
      - "deploy/compose/run.sh"
  - statement: "A prior Ansible/VirtualBox-based VPS deployment method under launchpad/deploy/archived/ failed because it defaulted to the hard-coded upstream ghcr.io/block/buzz:main image instead of a Launchpad-built one, and launchpad/deploy/AGENTS.md explicitly forbids using, running, copying, repairing, extending, or recommending anything in archived/ to build or deploy Buzz."
    entry_class: FACT
    evidence:
      - "launchpad/deploy/AGENTS.md"
      - "launchpad/deploy/README.md"
  - statement: "In deploy/compose/compose.yml, only the relay service publishes a host port (${BUZZ_HTTP_PORT:-3000}:3000); postgres, redis, minio, and minio-init declare no ports: mapping at all and are reachable only over the internal buzz-net bridge network via Docker DNS service names."
    entry_class: FACT
    evidence:
      - "deploy/compose/compose.yml"
  - statement: "compose.caddy.yml resets the relay's port mapping to empty (ports: !reset []) and instead publishes Caddy on ${CADDY_HTTP_PORT:-80} and ${CADDY_HTTPS_PORT:-443}, with a Caddyfile that reverse-proxies to relay:3000 over the internal network; this is the TLS-terminating single-node profile, activated by BUZZ_COMPOSE_TLS=true."
    entry_class: FACT
    evidence:
      - "deploy/compose/compose.caddy.yml"
      - "deploy/compose/Caddyfile"
      - "deploy/compose/run.sh"
  - statement: "compose.dev.yml is an optional overlay (BUZZ_COMPOSE_DEV=true) that publishes postgres, redis, and minio directly to the host plus adds adminer and prometheus containers; it is documented as local admin ports/tools, not part of the production network boundary."
    entry_class: FACT
    evidence:
      - "deploy/compose/compose.dev.yml"
      - "deploy/compose/run.sh"
  - statement: "The relay's environment in compose.yml wires DATABASE_URL to the postgres service, REDIS_URL to the redis service, and BUZZ_S3_ENDPOINT to http://minio:9000 with BUZZ_S3_ADDRESSING_STYLE=path (Docker DNS resolves the minio hostname, not an arbitrary <bucket>.minio hostname); it stores git repository state under BUZZ_GIT_REPO_PATH=/data/git, backed by the buzz-git-data named volume."
    entry_class: FACT
    evidence:
      - "deploy/compose/compose.yml"
  - statement: "Four named Docker volumes persist state for the production Compose stack: buzz-postgres-data (Postgres event store), buzz-redis-data (Redis, started with --appendonly yes), buzz-minio-data (S3-compatible media and git-CAS object storage), and buzz-git-data (the relay's on-disk git working state at /data/git); compose.caddy.yml adds buzz-caddy-data and buzz-caddy-config when TLS termination is enabled."
    entry_class: FACT
    evidence:
      - "deploy/compose/compose.yml"
      - "deploy/compose/compose.caddy.yml"
  - statement: "All required secrets and credentials (BUZZ_RELAY_PRIVATE_KEY, BUZZ_GIT_HOOK_HMAC_SECRET, POSTGRES_PASSWORD, REDIS_PASSWORD, BUZZ_S3_ACCESS_KEY, BUZZ_S3_SECRET_KEY, RELAY_OWNER_PUBKEY) are supplied through the untracked deploy/compose/.env file, templated by deploy/compose/.env.example with CHANGE_ME placeholders; deploy/compose/run.sh refuses to start (require_env) when .env is missing or still contains a CHANGE_ME value."
    entry_class: FACT
    evidence:
      - "deploy/compose/.env.example"
      - "deploy/compose/run.sh"
  - statement: "Schema migrations are embedded in the relay binary (sqlx migrate) and applied at startup only when BUZZ_AUTO_MIGRATE is truthy — buzz_auto_migrate_enabled() in crates/buzz-relay/src/main.rs recognizes true/1/yes/on (case-insensitive, trimmed) and treats anything else, including an empty string, as false; deploy/compose/.env.example sets BUZZ_AUTO_MIGRATE=true for production and README.md notes it as opt-in that requires either that flag or a manual buzz-admin migrate run before first start."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs"
      - "deploy/compose/.env.example"
      - "deploy/compose/README.md"
  - statement: "A migration failure at startup is fatal to the relay process: main.rs propagates db.migrate() errors with `?` before any listener is bound, so a bad migration or unreachable Postgres prevents the relay from ever serving traffic rather than starting in a degraded state."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs"
  - statement: "Compose's own service_healthy gate defers relay startup until postgres, redis, and minio report healthy and minio-init has completed successfully; the relay's own healthcheck probes GET /_readiness over /dev/tcp (chosen because the runtime image ships bash but no curl/wget/socat), with a 30s start_period and 12 retries at a 10s interval before Compose considers it unhealthy."
    entry_class: FACT
    evidence:
      - "deploy/compose/compose.yml"
  - statement: "/_readiness checks three things concurrently: a live shutting_down flag (returns 503 immediately if set), a Postgres ping, and a Redis pool connection; /_liveness returns 200 unconditionally once the process is up and performs no dependency checks of its own."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs"
  - statement: "On SIGTERM, the relay sets shutting_down=true (readiness immediately starts returning 503), waits a fixed 5s grace period before closing listeners, then runs a bounded graceful drain: per-connection close is jittered up to MAX_DRAIN_JITTER_MS (20s, default 0) plus a RESTART_CLOSE_ACK_TIMEOUT (5s) wait for a close-frame ack, backstopped by a hard GRACEFUL_DRAIN_TIMEOUT of 30s; documented worst case from SIGTERM to forced exit is 5s + 30s = 35s."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs"
  - statement: "None of deploy/compose/compose.yml, compose.caddy.yml, or compose.dev.yml set a stop_grace_period or stop_signal override for the relay service, so container shutdown timing on this stack relies entirely on whatever Docker Compose's built-in default grace period is; that default number is not verified in this evidence pass, and it may be shorter than the relay's documented 35s worst-case graceful-drain budget."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay/src/main.rs"
      - "deploy/compose/compose.yml"
    confidence: 0.5
  - statement: "The relay listens on three TCP ports plus a Prometheus exporter, mapped in compose.yml's relay environment: BUZZ_BIND_ADDR=0.0.0.0:3000 for the app router (WS + REST + web UI), BUZZ_HEALTH_PORT=8080 for the /_liveness, /_readiness, /_status, and /_mesh probes, and BUZZ_METRICS_PORT=9102; only 3000 is published to the host by default."
    entry_class: FACT
    evidence:
      - "deploy/compose/compose.yml"
      - "crates/buzz-relay/src/router.rs"
  - statement: "The root Dockerfile documents the same three ports as EXPOSE 3000 8080 9102, labels them app (WS+REST), /_liveness //_readiness, and /metrics respectively, and notes that only the bundled web UI (invite landing page) is always served — the repo browser and admin bundle require separate opt-in env vars (BUZZ_SERVE_GIT_WEB_GUI, BUZZ_ADMIN_HOST)."
    entry_class: FACT
    evidence:
      - "Dockerfile"
  - statement: "deploy/compose/run.sh's backup-hint checklist names deploy/compose/.env (especially BUZZ_RELAY_PRIVATE_KEY and the DB/Redis/S3 secrets), the owner private key held outside the stack, Postgres data (pg_dump or a quiesced snapshot), MinIO/S3 bucket contents, the buzz-git-data volume, and the Caddy data/config volumes when TLS is enabled — with the explicit instruction to keep Postgres and object/git snapshots from the same maintenance window."
    entry_class: FACT
    evidence:
      - "deploy/compose/run.sh"
  - statement: "deploy/compose/README.md documents that an image-only rollback (restoring the previous immutable BUZZ_IMAGE digest or full-SHA tag and re-running check/upgrade) is safe only when the intervening database migrations were backward-compatible; otherwise the operator must restore the matching pre-upgrade database and object/git snapshots as one coordinated recovery."
    entry_class: FACT
    evidence:
      - "deploy/compose/README.md"
  - statement: "The relay, postgres, and redis services in compose.yml all set restart: unless-stopped, so Docker restarts a crashed container automatically without operator action; minio and minio-init do not share this exact configuration — minio also sets restart: unless-stopped, but minio-init is a one-shot job with restart: \"no\"."
    entry_class: FACT
    evidence:
      - "deploy/compose/compose.yml"
  - statement: "The Helm chart at deploy/charts/buzz documents its own non-HA production profile as replicaCount: 1 by default, with HA requiring replicaCount >= 2 and hard-requiring Redis for buzz-pubsub fan-out; this is the Kubernetes-topology analogue of the single-node Compose bundle documented here, for an operator choosing that platform instead."
    entry_class: FACT
    evidence:
      - "deploy/charts/buzz/values.yaml"
      - "deploy/charts/buzz/README.md"
  - statement: "The Helm chart's own upgrade documentation states that schema migrations are embedded via sqlx::migrate! and run at startup gated by BUZZ_AUTO_MIGRATE (chart default true), race-safely behind a Postgres advisory lock when multiple replicas start concurrently — the same migration mechanism as the Compose bundle, just made concurrency-safe for a topology this single-relay node does not itself use."
    entry_class: FACT
    evidence:
      - "deploy/charts/buzz/README.md"
  - statement: "buzz-db, buzz-pubsub, buzz-auth, buzz-search, buzz-audit, and buzz-media are the crates the buzz-relay binary composes at runtime for its Postgres event store, Redis pub/sub fan-out, authentication/authorization, Postgres full-text search, hash-chain audit log, and Blossom/S3 media storage responsibilities respectively; buzz-relay also hosts git and huddle-audio handling directly rather than through a separate crate."
    entry_class: FACT
    evidence:
      - "CLAUDE.md"
---

# Single-relay deployment

One relay process, on one host, backed by Postgres, Redis, and S3-compatible
object storage — the deployment topology this repository calls **single-relay**:
one relay URL is authoritative for exactly one community
([README.md](../../../../README.md), [NOSTR.md](../../../../NOSTR.md)). This
node documents the canonical implementation of that topology in this
repository: the single-node/VPS Docker Compose bundle under
[`deploy/compose/`](../../../../deploy/compose/), governed for this fork by
[`launchpad/deploy/run.sh`](../../../../launchpad/deploy/run.sh). It also notes
the Kubernetes-topology analogue — see [Scope and omissions](#scope-and-omissions).

## Environment and topology

One physical or virtual host running Docker Engine with Compose v2.24.4+
([deploy/compose/README.md](../../../../deploy/compose/README.md)) is the
entire execution environment. `deploy/compose/compose.yml` defines five
containers on that one host — `relay`, `postgres`, `redis`, `minio`, and the
one-shot `minio-init` job — joined by a single bridge network, `buzz-net`.
Layering `compose.caddy.yml` (via `BUZZ_COMPOSE_TLS=true`) adds a sixth
container, `caddy`, as the public TLS-terminating entry point; layering
`compose.dev.yml` (via `BUZZ_COMPOSE_DEV=true`) adds host-bound admin ports
and two more containers (`adminer`, `prometheus`) for local operation. There is
exactly one relay process — no replica count, no leader election, no shared-
nothing partitioning. This is the whole point of the name: a single execution
node hosts the single relay for the single community it serves.

The relay container image is built by the repository's root
[`Dockerfile`](../../../../Dockerfile) — a multi-stage build that compiles
`buzz-relay`, `buzz-admin`, and `buzz-pair-relay` from Rust 1.95, bundles the
`web`/`admin-web` static frontends, and produces a `debian-slim` runtime
running as a non-root `buzz:buzz` user. `.github/workflows/docker.yml` builds
and publishes that image to `ghcr.io/launchpad-26/buzz` on every push to
`launchpad` (tags `:launchpad` and `:sha-<full-commit>`) and on `relay-v*.*.*`
tags. Normal VPS deployment consumes that prebuilt image directly — it does
not build the Dockerfile locally.

## Container/service → execution node mapping

| Container | Role | Data store it owns | Host-exposed? |
|---|---|---|---|
| `relay` | `buzz-relay` binary: WS + REST + web UI, plus git and huddle-audio handling in-process (`CLAUDE.md`) | none directly — reads/writes `postgres`, `redis`, `minio`, and the `buzz-git-data` volume | Yes — `${BUZZ_HTTP_PORT:-3000}:3000` (or none, behind Caddy) |
| `postgres` | Event store (`buzz-db`) | `buzz-postgres-data` volume | No — internal network only |
| `redis` | Pub/sub fan-out, presence (`buzz-pubsub`) | `buzz-redis-data` volume (AOF persistence) | No — internal network only |
| `minio` | S3-compatible media + git-CAS object storage (`buzz-media`) | `buzz-minio-data` volume | No — internal network only |
| `minio-init` | One-shot bucket/policy bootstrap, then exits | none | No |
| `caddy` (optional, TLS profile) | Reverse proxy + automatic HTTPS | `buzz-caddy-data`/`buzz-caddy-config` volumes | Yes — `80`/`443` |

The relay's own environment in `compose.yml` wires these connections
explicitly: `DATABASE_URL` to the `postgres` service, `REDIS_URL` to `redis`,
`BUZZ_S3_ENDPOINT=http://minio:9000` with `BUZZ_S3_ADDRESSING_STYLE=path`
(Docker's internal DNS resolves the `minio` hostname, not an arbitrary
`<bucket>.minio` hostname), and `BUZZ_GIT_REPO_PATH=/data/git`, backed by the
`buzz-git-data` volume.

The relay itself exposes three listeners, all declared in `compose.yml`'s
environment block and matched by the Dockerfile's `EXPOSE 3000 8080 9102`:

| Port | Purpose | Handlers |
|---|---|---|
| `3000` | App router: WebSocket + REST + bundled web UI | `crates/buzz-relay/src/router.rs` |
| `8080` | Health-only: `/_liveness`, `/_readiness`, `/_status`, `/_mesh` | `build_health_router` |
| `9102` | Prometheus metrics exporter | `crates/buzz-relay/src/metrics.rs::install` |

Only `3000` (or, behind Caddy, `80`/`443` on the `caddy` container) is
published to the host by default.

## Network, persistence, and trust boundaries

**Network.** All six possible containers share one Docker bridge network,
`buzz-net`. In the production profile (`compose.yml` alone), only `relay`
publishes a host port; `postgres`, `redis`, `minio`, and `minio-init` declare
no `ports:` mapping at all and are reachable only by Docker DNS service name
from inside `buzz-net`. Layering `compose.caddy.yml` moves the public surface
to `caddy` and resets the relay's own port mapping to empty
(`ports: !reset []`), so in the TLS profile the relay is not directly
reachable from outside the host at all — only Caddy is, and it reverse-proxies
to `relay:3000` over the internal network. `compose.dev.yml` is the one
profile that publishes `postgres`, `redis`, and `minio` to the host directly;
it is documented as a local admin/tooling overlay, not part of the production
boundary.

**Persistence.** Four named volumes carry state that outlives a container
restart: `buzz-postgres-data` (the canonical event store), `buzz-redis-data`
(Redis AOF, `--appendonly yes`), `buzz-minio-data` (media and git-CAS object
storage), and `buzz-git-data` (the relay's on-disk git working state at
`/data/git`). The TLS profile adds `buzz-caddy-data`/`buzz-caddy-config` for
certificate material. Everything else — the relay process's own memory, the
`minio-init` container — is disposable.

**Trust boundaries.** Secrets and credentials
(`BUZZ_RELAY_PRIVATE_KEY`, `BUZZ_GIT_HOOK_HMAC_SECRET`, `POSTGRES_PASSWORD`,
`REDIS_PASSWORD`, `BUZZ_S3_ACCESS_KEY`, `BUZZ_S3_SECRET_KEY`,
`RELAY_OWNER_PUBKEY`) live only in the untracked `deploy/compose/.env` file,
templated from `deploy/compose/.env.example` with `CHANGE_ME` placeholders
that must all be replaced before first start —
`deploy/compose/run.sh`'s `require_env` check refuses to start the stack
otherwise. No secret value is captured verbatim in this document. Within the
network, `postgres`/`redis`/`minio` trust any caller that can reach `buzz-net`
(their own passwords are the only additional gate); the `relay` container is
the sole boundary between that trusted internal network and the outside
world, whether exposed directly or behind Caddy.

## Deployment automation and config as authority

`launchpad/deploy/run.sh` is a thin guard, not a second implementation: it
validates that `deploy/compose/.env` selects an immutable
`ghcr.io/launchpad-26/buzz` image (digest or full 40-character commit-SHA tag;
floating tags are rejected unless `BUZZ_ALLOW_FLOATING_IMAGE=true`), refuses
the upstream `ghcr.io/block/buzz` image outright, and then delegates every
actual operation to `deploy/compose/run.sh` — `start`, `stop`, `restart`,
`pull`, `upgrade`, `logs`, `status`, `config`, `backup-hint`, and the
`add-member`/`remove-member`/`list-members` membership commands run through
`buzz-admin` inside the `relay` container. Those two scripts, plus
`deploy/compose/compose.yml`, `compose.caddy.yml`, `compose.dev.yml`, and
`.env.example`, are the authoritative deployment configuration for this
topology; this document links them rather than restating their contents.

A prior Ansible/VirtualBox-based VPS deployment method exists under
`launchpad/deploy/archived/`. It failed because it defaulted to the
hard-coded upstream `ghcr.io/block/buzz:main` image rather than a
Launchpad-built one, and `launchpad/deploy/AGENTS.md` explicitly forbids
using, running, copying, repairing, extending, or recommending anything in
`archived/` to build or deploy Buzz. It is named here only as a boundary
marker: it is not a second deployment path for this node to describe.

## Failure and recovery implications

**Startup ordering.** Compose's `depends_on: condition: service_healthy`
defers the `relay` container's start until `postgres`, `redis`, and `minio`
all report healthy and `minio-init` has completed successfully. The relay's
own Compose healthcheck probes `GET /_readiness` over a raw `/dev/tcp`
connection (the runtime image has `bash` but no `curl`/`wget`/`socat`), with a
30s `start_period` and 12 retries at a 10s interval.

**Readiness vs. liveness.** `/_readiness` checks three things on every call:
the in-process `shutting_down` flag (503 immediately if set), a live Postgres
ping, and a Redis pool connection. `/_liveness` returns `200` unconditionally
once the process is up — it performs no dependency checks, so only
`/_readiness` (which is what `compose.yml`'s healthcheck actually probes)
reflects backend health.

**Migrations.** Schema migrations are embedded in the relay binary via `sqlx`
and applied at startup only when `BUZZ_AUTO_MIGRATE` is truthy —
`buzz_auto_migrate_enabled()` recognizes `true`/`1`/`yes`/`on`
(case-insensitive, trimmed) and treats everything else, including an empty
value, as false. `.env.example` sets `BUZZ_AUTO_MIGRATE=true` for production.
A migration failure is fatal at startup: `main.rs` propagates the error before
any listener binds, so a bad migration — or an unreachable Postgres — prevents
the relay from ever serving traffic rather than starting in a degraded state.
Running with `BUZZ_AUTO_MIGRATE=false` against an unmigrated schema is
recoverable only by running `buzz-admin migrate` (or a prior manual migration)
before the relay is expected to pass its readiness probe.

**Graceful shutdown.** On `SIGTERM`, the relay immediately sets
`shutting_down=true` (readiness starts returning `503`), waits a fixed 5s
grace period, then runs a bounded drain: per-connection close is jittered up
to `MAX_DRAIN_JITTER_MS` (20s; default `0`) plus a `RESTART_CLOSE_ACK_TIMEOUT`
(5s) wait for a close-frame acknowledgment, backstopped by a hard 30s
`GRACEFUL_DRAIN_TIMEOUT`. Documented worst case, from `SIGTERM` to forced
exit, is 5s + 30s = 35s. None of the Compose files in this bundle set a
`stop_grace_period` override for the `relay` service, so shutdown timing here
depends on whatever Docker Compose's own default grace period is — that
default is not itself verified in this evidence pass, and an operator relying
on a plain `docker compose down`/`restart` should confirm it comfortably
exceeds 35s before assuming a clean drain every time.

**Container restart.** `relay`, `postgres`, `redis`, and `minio` all set
`restart: unless-stopped`, so Docker restarts a crashed container without
operator action; `minio-init` is a one-shot job (`restart: "no"`) that is
expected to exit after seeding the bucket.

**Backup and rollback.** `deploy/compose/run.sh backup-hint` names the
checklist an operator must action before upgrades and on a schedule:
`deploy/compose/.env` (especially the relay's private key and the DB/Redis/S3
secrets), the owner private key (held outside the stack, not by Compose), a
Postgres snapshot (`pg_dump` or a quiesced volume snapshot), the MinIO/S3
bucket contents, the `buzz-git-data` volume, and — when TLS is enabled — the
Caddy data/config volumes, all taken from the same maintenance window. An
image-only rollback (restoring a previous immutable `BUZZ_IMAGE` digest or
full-SHA tag) is documented as safe only when the intervening database
migrations were backward-compatible; otherwise the operator must restore the
matching pre-upgrade database and object/git snapshots together as one
coordinated recovery.

## Scope and omissions

This node covers the Docker Compose single-node/VPS bundle
(`deploy/compose/`) as the concrete implementation of "single-relay" —
one relay process, one host, one community. The repository defines a second,
Kubernetes-native way to run the same non-HA topology: the Helm chart at
`deploy/charts/buzz` defaults to `replicaCount: 1` (its production profile
requires `replicaCount >= 2` and a Redis dependency only once HA is chosen).
Its migration mechanism is the same embedded `sqlx::migrate!` gated by
`BUZZ_AUTO_MIGRATE`, made concurrency-safe with a Postgres advisory lock for
the multi-replica case this node does not itself use. A full description of
that chart — its values schema, ArgoCD/Flux GitOps flow, autoscaling, and
device-pairing relay option — is a separate node's concern and is not
duplicated here.

Out of scope, and why:

- **The archived Ansible/VirtualBox method** (`launchpad/deploy/archived/`) —
  explicitly disclaimed as a failed method, not a deployment option; named
  above only as a boundary marker.
- **The upstream ecosystem's private pipelines** — `squareup/buzz-releases`,
  `squareup/sprout-oss`, and `squareup/block-coder-tf-stacks`, named in this
  repository's top-level `CLAUDE.md` — are not accessible from this checkout
  and are not cited as evidence here. This fork's own deployment path is the
  Compose bundle documented above, governed by `launchpad/deploy/run.sh`.
- **The bootstrap script for `.env` generation** — `deploy/compose/README.md`
  describes it as intended future tooling ("should eventually replace manual
  `.env` editing"); it does not exist yet in this revision, so it is not
  described as though it does.
- **Docker Compose's actual default `stop_grace_period` value** — not
  verified against an opened source in this evidence pass (see the Failure
  and recovery section's inference); an operator or reviewer should confirm
  it directly against the installed Compose version before relying on the
  35s shutdown budget holding in practice.
- **Multi-community / hosted-operator deployment** — `NOSTR.md` describes a
  multi-community deployment as a distinct mode reached by separate domains;
  this node documents the single-community topology only.
