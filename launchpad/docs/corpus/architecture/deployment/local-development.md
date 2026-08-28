---
id: architecture-deployment-local-development
type: architecture
status: draft
origin: launchpad
audiences:
  - developer
  - agent
  - operator
evidence:
  - statement: "This node was authored and checked against repository revision a44cf52fc740ebebbdd671427480d14f0bce0115."
    entry_class: FACT
    evidence:
      - "commit a44cf52fc740ebebbdd671427480d14f0bce0115"
  - statement: "Local development runs every Buzz process and Docker service on a single developer machine; there is no separate host per component."
    entry_class: INFERENCE
    evidence:
      - "Justfile"
      - "docker-compose.yml"
    confidence: 0.9
  - statement: "docker-compose.yml defines six services for local development: postgres, redis, adminer, keycloak, minio, minio-init, and prometheus."
    entry_class: FACT
    evidence:
      - "docker-compose.yml"
  - statement: "Every docker-compose.yml service publishes its port bound to 127.0.0.1 only (e.g. postgres at 127.0.0.1:5432, redis at 127.0.0.1:6379), so none of the six Docker-hosted dev services is reachable from another host on the network by default."
    entry_class: FACT
    evidence:
      - "docker-compose.yml"
  - statement: "buzz-relay's own bind address defaults to 0.0.0.0:3000 (BUZZ_BIND_ADDR unset), which listens on every network interface rather than only 127.0.0.1."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/config.rs"
      - ".env.example"
  - statement: "The relay's default bind address is therefore reachable from other hosts on the same network, unlike the Docker Compose infrastructure services, which are not — a wider default network surface for the one process meant to be reached by clients."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay/src/config.rs"
      - "docker-compose.yml"
    confidence: 0.75
  - statement: "buzz-relay's health check port defaults to 8080 and its Prometheus metrics port defaults to 9102, both read from BUZZ_HEALTH_PORT and BUZZ_METRICS_PORT with no compose-defined publish rule, so their default bind follows the relay process's own bind behavior rather than compose's 127.0.0.1 convention."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/config.rs"
  - statement: "`just relay` (relay: bootstrap _ensure-migrations) and `just dev` (dev: bootstrap _ensure-sidecar-stubs _ensure-migrations) both depend on _ensure-migrations, which depends on _ensure-services."
    entry_class: FACT
    evidence:
      - "Justfile"
  - statement: "_ensure-services starts `docker compose up -d` and polls `docker inspect` health status for buzz-postgres and buzz-redis for up to 40 attempts (3s apart, ~120s) before failing the recipe."
    entry_class: FACT
    evidence:
      - "Justfile"
  - statement: "_ensure-migrations runs `cargo run -p buzz-admin -- migrate` followed by scripts/seed-local-community.sh once services are healthy."
    entry_class: FACT
    evidence:
      - "Justfile"
      - "scripts/seed-local-community.sh"
  - statement: "buzz-relay's own startup only applies database migrations when the BUZZ_AUTO_MIGRATE environment variable is truthy (true/1/yes/on, case-insensitive); it is unset by default, so relay startup alone does not migrate the database in the local-dev flow described above, which instead relies on the explicit buzz-admin migrate step run by _ensure-migrations."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs"
  - statement: "The top-level AGENTS.md repo map describes migrations/ as \"auto-applied on relay startup,\" which is the deployed/production framing; the local-dev path documented here (Justfile _ensure-migrations calling buzz-admin migrate explicitly) is the mechanism that actually applies them in this environment, and the two statements describe different points in the pipeline rather than contradicting each other. Recorded here because a reader coming from the top-level AGENTS.md would otherwise expect the relay process itself to migrate on `just relay` / `just dev`, which it does not unless BUZZ_AUTO_MIGRATE is explicitly set."
    entry_class: INFERENCE
    evidence:
      - "AGENTS.md"
      - "crates/buzz-relay/src/main.rs"
      - "Justfile"
    confidence: 0.8
  - statement: "migrations/ contains 31 numbered SQL files (0001_initial_schema.sql through at least 0020_join_policy_acceptances.sql, continuing beyond it) applied in order by buzz-admin migrate."
    entry_class: FACT
    evidence:
      - "migrations/0001_initial_schema.sql"
      - "migrations/0020_join_policy_acceptances.sql"
  - statement: "docker-compose.yml declares three named volumes for persistence: buzz-postgres-data (postgres), buzz-minio-data (minio), and buzz-prometheus-data (prometheus); redis has no volume, so its data does not survive a container recreation."
    entry_class: FACT
    evidence:
      - "docker-compose.yml"
  - statement: "scripts/dev-reset.sh's own comment states Redis data is ephemeral and always wiped on restart, matching the absence of a redis volume in docker-compose.yml."
    entry_class: FACT
    evidence:
      - "scripts/dev-reset.sh"
      - "docker-compose.yml"
  - statement: "`just down` (docker compose down) stops containers and preserves the three named volumes; `just reset` runs scripts/dev-reset.sh --yes, which runs `docker compose down -v --remove-orphans` (deleting all three volumes) and then re-execs dev-setup.sh to recreate a clean environment."
    entry_class: FACT
    evidence:
      - "Justfile"
      - "scripts/dev-reset.sh"
  - statement: "scripts/dev-reset.sh also runs scripts/reset-desktop-dev-state.sh before tearing down containers, and states that installed Buzz app state and its production keyring are preserved — only development-scoped desktop state and Docker volumes are wiped."
    entry_class: FACT
    evidence:
      - "scripts/dev-reset.sh"
  - statement: "keycloak is provisioned in local dev for local OAuth/OIDC testing, per CONTRIBUTING.md's own description of what `just setup` starts."
    entry_class: FACT
    evidence:
      - "CONTRIBUTING.md"
      - "docker-compose.yml"
  - statement: "adminer is a Postgres browser UI reachable at http://localhost:8082, and depends on postgres being healthy before starting."
    entry_class: FACT
    evidence:
      - "docker-compose.yml"
      - "CONTRIBUTING.md"
  - statement: "minio-init runs once after minio is healthy, creates the buzz-media bucket if absent, and sets its anonymous access policy to none (private by default) before exiting."
    entry_class: FACT
    evidence:
      - "docker-compose.yml"
  - statement: "Postgres, MinIO, and Keycloak dev credentials in docker-compose.yml and .env.example are fixed, non-secret placeholder values scoped to the local dev-only network (127.0.0.1) described above; this document does not restate them, since the compose file and .env.example are the authoritative, already-committed source."
    entry_class: INFERENCE
    evidence:
      - "docker-compose.yml"
      - ".env.example"
    confidence: 0.85
  - statement: ".env.example documents a TYPESENSE_API_KEY and TYPESENSE_URL block, and CONTRIBUTING.md's port table lists Typesense at localhost:8108, but docker-compose.yml defines no typesense service and the top-level AGENTS.md states buzz-search performs Postgres full-text search rather than using Typesense."
    entry_class: FACT
    evidence:
      - ".env.example"
      - "docker-compose.yml"
      - "AGENTS.md"
  - statement: "`just dev` (the desktop-app dev recipe) refuses to launch when the relay, health, or metrics port is already bound by another process, printing which port and the offending process before exiting 1, rather than launching the desktop app against a stale relay."
    entry_class: FACT
    evidence:
      - "Justfile"
  - statement: "First-time local setup is `just setup` (running `just bootstrap` first, then scripts/dev-setup.sh), which copies .env.example to .env if absent, starts and health-waits the Docker services, applies migrations, seeds a local community, and installs desktop and web JS dependencies."
    entry_class: FACT
    evidence:
      - "Justfile"
      - "scripts/dev-setup.sh"
      - "CONTRIBUTING.md"
  - statement: "scripts/dev-setup.sh renames a legacy `sprout`-named default DATABASE_URL/PGUSER/PGPASSWORD/PGDATABASE to the current `buzz` defaults for developers carrying over an older .env, and stops/removes any legacy `sprout-*`-named containers so the current `buzz-*` containers can bind the same ports."
    entry_class: FACT
    evidence:
      - "scripts/dev-setup.sh"
  - statement: "This node's evidence was checked by reading the cited files directly, not by executing `just setup`, `just dev`, or `just reset` end-to-end in this task's environment; runtime behavior of the health-wait loop, the port-conflict guard, and the legacy-rename path was read from source, not observed live."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#671 task instructions (this task's own scope: author one corpus node from repository evidence, not run the dev stack)"
---

# Local development deployment

The canonical description of Buzz's **local development** environment/topology: what
runs where, how the pieces map to each other, the network and persistence boundaries
between them, and what to do when a piece fails. Scoped to local development only —
staging and production topology (Kubernetes via `block-coder-tf-stacks`, the relay
Docker image built by `sprout-oss`) is a separate concern and not covered here.

## Environment / topology

Local development is **single-node**: one developer machine hosts every component.
There is no multi-host topology to diagram — the "nodes" that matter here are the
*processes and containers on that one machine*, not physical or virtual hosts. Two
kinds of execution unit exist side by side:

- **Docker containers**, orchestrated by `docker-compose.yml` and started via
  `docker compose up -d` (wrapped by the Justfile's `_ensure-services` recipe).
- **Native host processes**: the Rust relay/admin binaries (`cargo run -p buzz-relay`,
  `cargo run -p buzz-admin`), the Tauri desktop app, and the Vite dev server for the
  web client — none of these are containerized in local dev.

## Containers, services, and data stores

`docker-compose.yml` defines six services, all on one bridge network (`buzz-net`):

| Service | Image | Purpose | Persistence |
|---|---|---|---|
| `postgres` | `postgres:17-alpine` | primary relational store | volume `buzz-postgres-data` |
| `redis` | `redis:7-alpine` | pub/sub fan-out, presence, typing indicators | none — ephemeral |
| `adminer` | `adminer:latest` | Postgres browser UI, depends on `postgres` healthy | n/a |
| `keycloak` | `quay.io/keycloak/keycloak:26.0` | local OAuth/OIDC testing | none — `dev-mem` DB |
| `minio` | `minio/minio:latest` | S3-compatible object store (media, git CAS) | volume `buzz-minio-data` |
| `minio-init` | `minio/mc:latest` | one-shot: creates `buzz-media` bucket, sets it private | n/a, exits after run |
| `prometheus` | `prom/prometheus:latest` | scrapes relay metrics | volume `buzz-prometheus-data` |

Alongside these, the native host processes connect to the containers over
`localhost`:

- **`buzz-relay`** (`cargo run -p buzz-relay`, or `just relay` / `just dev`) —
  connects to `postgres` (`DATABASE_URL`) and `redis` (`REDIS_URL`), and to `minio`
  for media/S3 storage (`BUZZ_S3_ENDPOINT`).
- **`buzz-admin`** (`cargo run -p buzz-admin -- migrate`) — applies
  `migrations/*.sql` directly against Postgres; run by the `_ensure-migrations`
  Justfile recipe, not by the relay process itself (see *Persistence and migrations*
  below).
- **Desktop app** (Tauri) and **web client** (Vite) — connect to the relay over
  `ws://localhost:3000` / `http://localhost:3000`, not to the containers directly.

`buzz-search` (Postgres full-text search) has no separate container — it runs inside
the `postgres` service. Note: `.env.example` documents `TYPESENSE_API_KEY` /
`TYPESENSE_URL`, and CONTRIBUTING.md's port table lists Typesense at
`localhost:8108`, but no `typesense` service exists in `docker-compose.yml`. That is
a real inconsistency between the environment template/docs and the actual compose
file, recorded as a gap below rather than resolved by guessing which is stale.

## Network boundaries

Every `docker-compose.yml` port publish is bound to `127.0.0.1` explicitly (for
example `127.0.0.1:5432:5432`), so none of the six Docker services in the table above
is reachable from another host on the network by default — they are local-loopback
only.

`buzz-relay` itself is different: its bind address defaults to `0.0.0.0:3000`
(`BUZZ_BIND_ADDR` unset), which listens on every network interface, not just
loopback. Its health port (default `8080`, `BUZZ_HEALTH_PORT`) and metrics port
(default `9102`, `BUZZ_METRICS_PORT`) follow the relay process's own bind behavior —
compose defines no publish rule for them because they are not containerized. So the
one process meant to be reached by real clients (desktop, web, mobile, other relays)
has a wider default network surface in local dev than the infrastructure it depends
on. A developer running local dev on a shared or untrusted network should be aware
the relay is not loopback-restricted by default the way Postgres/Redis/MinIO are.

`just dev` includes a port-conflict guard: before launching the desktop app it checks
whether the relay, health, or metrics port is already bound by another process (via
`lsof`) and refuses to launch against a possibly-stale relay, printing the offending
process instead.

## Persistence and migrations

Three of the six Docker services persist data across restarts via named volumes:
`buzz-postgres-data`, `buzz-minio-data`, `buzz-prometheus-data`. Redis has no volume
— both `docker-compose.yml` and `scripts/dev-reset.sh`'s own comment agree its data
is ephemeral and wiped on any container recreation.

**Migrations are applied explicitly, not automatically, in the local-dev flow
described here.** The Justfile's `_ensure-migrations` recipe runs
`cargo run -p buzz-admin -- migrate` (then seeds a local community) once Postgres and
Redis report healthy — this is what `just relay`, `just dev`, and `just setup` all
depend on. Separately, `buzz-relay`'s own startup code only applies migrations
itself when the `BUZZ_AUTO_MIGRATE` environment variable is set truthy; it is unset
by default, so the relay process does not self-migrate on `just relay` / `just dev`.
The top-level `AGENTS.md` repo map describes `migrations/` as "auto-applied on relay
startup" — that is the deployed/production framing (where `BUZZ_AUTO_MIGRATE` is
presumably set); the mechanism that actually runs migrations in the local-dev flow
this node documents is the explicit `buzz-admin migrate` step above, not relay
self-migration. `migrations/` holds 31 numbered SQL files today
(`0001_initial_schema.sql` through beyond `0020_join_policy_acceptances.sql`),
applied in order.

## Trust boundaries (without exposing secrets)

Postgres, MinIO, and Keycloak in `docker-compose.yml` and `.env.example` use fixed,
non-secret placeholder credentials scoped to the local-only (`127.0.0.1`) network
described above. This document does not restate those values — `docker-compose.yml`
and `.env.example` are the authoritative, already-committed source for them, and
duplicating them here would be a second copy that can drift.

`minio-init` sets the `buzz-media` bucket's anonymous access policy to `none`
(private) immediately after creating it, so the object store is not publicly
readable even within the local Docker network by default. `keycloak` runs in
`start-dev` / `dev-mem` mode — a non-persistent, development-only identity provider
for exercising OAuth/OIDC flows locally, not a boundary meant to resemble production
auth infrastructure.

## Deployment automation and configuration (authority)

This node describes the automation; it is not a substitute for reading it. The
authoritative sources are:

- [`Justfile`](../../../../../Justfile) — `bootstrap`, `setup`, `relay`, `relay-web`,
  `dev`, `down`, `reset`, `ps`, `logs`, and the internal `_ensure-services` /
  `_ensure-migrations` recipes.
- [`docker-compose.yml`](../../../../../docker-compose.yml) — the six-service
  topology in the table above.
- [`.env.example`](../../../../../.env.example) — every environment variable local
  dev reads, with defaults and comments.
- [`scripts/dev-setup.sh`](../../../../../scripts/dev-setup.sh) — first-time and
  re-run setup: legacy `sprout`→`buzz` rename, service health-wait, migrations,
  desktop/web dependency install, git hook install.
- [`scripts/dev-reset.sh`](../../../../../scripts/dev-reset.sh) — full teardown:
  desktop dev state, then `docker compose down -v --remove-orphans` (deletes all
  three named volumes), then re-runs `dev-setup.sh`.
- [`CONTRIBUTING.md`](../../../../../CONTRIBUTING.md) §"Setting Up the Development
  Environment" — prerequisites and the narrative walkthrough of the same commands.

## Failure and recovery implications

- **A Docker service fails to become healthy.** `_ensure-services` polls
  `docker inspect` health status for `buzz-postgres` and `buzz-redis` for up to 40
  attempts (~3s apart, ~120s total) before the recipe exits 1. Any recipe depending
  on `_ensure-migrations` (`just relay`, `just dev`, `just setup`) fails at that
  point rather than proceeding against unhealthy infrastructure.
- **The relay port is already in use.** `just dev`'s guard refuses to launch the
  desktop app against a possibly-stale relay and exits 1, naming the conflicting
  process rather than silently connecting to it.
- **Stop without losing data.** `just down` (`docker compose down`) stops containers
  and keeps all three named volumes intact.
- **Full recovery from corrupted/inconsistent local state.** `just reset`
  (`scripts/dev-reset.sh --yes`) is the only documented recovery path, and it is
  destructive: it deletes `buzz-postgres-data`, `buzz-minio-data`, and
  `buzz-prometheus-data` (Redis was already ephemeral) and recreates a clean
  environment from scratch via `dev-setup.sh`. Installed Buzz app state and its
  production keyring are explicitly preserved. There is no documented narrower
  recovery — for example, repairing a corrupted Postgres volume without discarding
  local dev data — in local-dev automation today; the only path this repository
  documents is full destructive reset.
- **Legacy state.** `dev-setup.sh` self-heals two categories of stale state
  automatically on every run: a legacy `sprout`-prefixed `DATABASE_URL`/`PGUSER`/
  `PGPASSWORD`/`PGDATABASE` in an existing `.env` is rewritten to the current `buzz`
  defaults, and any legacy `sprout-*`-named containers are stopped and removed so
  the current `buzz-*` containers can bind the same ports.

## Scope and omissions

**Out of scope for this node:** staging and production deployment topology
(Kubernetes via `block-coder-tf-stacks`, Terraform, ArgoCD, the relay Docker image
built by `sprout-oss`, Blox workstation agent provisioning via
`sprout-backend-blox`) — those are separate execution environments with their own
topology, owned by their respective repos per the top-level `AGENTS.md` ecosystem
table, and are not local development. Relay authentication/authorization internals,
event-kind design, and the desktop/mobile app architectures are covered by other
nodes, not this one.

**Gaps, named rather than resolved:**

- `.env.example` and `CONTRIBUTING.md`'s port table document a Typesense
  configuration block (`TYPESENSE_API_KEY`, `TYPESENSE_URL`, port `8108`) that has
  no corresponding service in `docker-compose.yml`, and the top-level `AGENTS.md`
  states search is Postgres full-text search (`buzz-search`), not Typesense. This
  reads as stale documentation rather than a hidden service, but that was not
  independently confirmed against Typesense-specific code, since no such code was
  found while gathering evidence for this node.
- Local-dev automation has no documented **non-destructive** recovery path for a
  corrupted or inconsistent Postgres volume — only the destructive `just reset`.
  Whether a narrower recovery (e.g. restoring the volume from a snapshot, or
  re-running only the migration step against existing data) is possible or intended
  was not established from the sources read for this node.
- This node's claims were verified by reading the cited files at the recorded
  revision, not by executing `just setup`, `just dev`, `just down`, or `just reset`
  end-to-end. The health-wait loop's actual timing, the port-conflict guard's actual
  output, and the legacy-rename path's actual behavior were read from source, not
  observed running.
