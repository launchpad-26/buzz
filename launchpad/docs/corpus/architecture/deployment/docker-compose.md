---
id: architecture-deployment-docker-compose
type: architecture
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - operator
evidence:
  - statement: "This node was authored and checked against repository revision a44cf52fc740ebebbdd671427480d14f0bce0115."
    entry_class: FACT
    evidence:
      - "commit a44cf52fc740ebebbdd671427480d14f0bce0115"
  - statement: "deploy/compose/README.md states its bundle is intentionally separate from the root docker-compose.yml, which remains local development infrastructure."
    entry_class: FACT
    evidence:
      - "deploy/compose/README.md"
  - statement: "deploy/compose/compose.yml defines five services on one Compose project (buzz-prod): relay, postgres, redis, minio, and a one-shot minio-init, all attached to a single bridge network buzz-net."
    entry_class: FACT
    evidence:
      - "deploy/compose/compose.yml"
  - statement: "Unlike the root docker-compose.yml, deploy/compose/compose.yml runs the buzz-relay binary itself as a container (the relay service, image ${BUZZ_IMAGE}), not just its backing services."
    entry_class: FACT
    evidence:
      - "deploy/compose/compose.yml"
      - "docker-compose.yml"
  - statement: "compose.caddy.yml is an optional overlay that removes the relay's direct port publish (ports: !reset []) and fronts it with a Caddy reverse proxy for automatic HTTPS, driven by BUZZ_DOMAIN and a single-line Caddyfile (reverse_proxy relay:3000)."
    entry_class: FACT
    evidence:
      - "deploy/compose/compose.caddy.yml"
      - "deploy/compose/Caddyfile"
  - statement: "compose.dev.yml is a third optional overlay that republishes postgres/redis/minio ports to the host and adds adminer and prometheus containers for local admin access; it is not used in a normal production start."
    entry_class: FACT
    evidence:
      - "deploy/compose/compose.dev.yml"
  - statement: "deploy/compose/run.sh selects which overlay files to pass to docker compose based on the BUZZ_COMPOSE_TLS and BUZZ_COMPOSE_DEV environment switches, and refuses to run start/restart/upgrade/pull if .env is missing or still contains a CHANGE_ME placeholder."
    entry_class: FACT
    evidence:
      - "deploy/compose/run.sh"
  - statement: "launchpad/deploy/run.sh is a guard that must be invoked instead of deploy/compose/run.sh directly for Launchpad operations: it rejects the upstream ghcr.io/block/buzz image outright, requires BUZZ_IMAGE to resolve to ghcr.io/launchpad-26/buzz, requires Docker Compose 2.24.4 or newer, and only delegates to the canonical deploy/compose/run.sh once those checks pass."
    entry_class: FACT
    evidence:
      - "launchpad/deploy/run.sh"
  - statement: "launchpad/deploy/AGENTS.md records that an earlier Launchpad VPS deployment method, now moved to launchpad/deploy/archived/, failed because it defaulted to the hard-coded Block test image ghcr.io/block/buzz:main, so a Launchpad checkout could silently deploy upstream Block's code instead of launchpad-26/buzz's; that archive must not be used, run, or extended."
    entry_class: FACT
    evidence:
      - "launchpad/deploy/AGENTS.md"
  - statement: ".github/workflows/docker.yml builds and publishes ghcr.io/launchpad-26/buzz on every push to the launchpad branch, which is the image family deploy/compose/.env.example and the Launchpad guard require."
    entry_class: FACT
    evidence:
      - ".github/workflows/docker.yml"
  - statement: "deploy/compose/compose.yml's relay service requires POSTGRES_PASSWORD, REDIS_PASSWORD, BUZZ_S3_ACCESS_KEY, and BUZZ_S3_SECRET_KEY via Compose's ${VAR:?...} required-variable syntax, so compose refuses to start if any of them is unset -- unlike the root docker-compose.yml's dev stack, which hardcodes fixed placeholder values instead of requiring the operator to supply their own."
    entry_class: FACT
    evidence:
      - "deploy/compose/compose.yml"
      - "docker-compose.yml"
  - statement: "deploy/compose/.env.example marks BUZZ_RELAY_PRIVATE_KEY, BUZZ_GIT_HOOK_HMAC_SECRET, POSTGRES_PASSWORD, REDIS_PASSWORD, BUZZ_S3_ACCESS_KEY, BUZZ_S3_SECRET_KEY, and RELAY_OWNER_PUBKEY as CHANGE_ME placeholders the operator must replace before starting; every value in that file as committed is a non-functional placeholder, not a real secret."
    entry_class: FACT
    evidence:
      - "deploy/compose/.env.example"
  - statement: "redis in deploy/compose/compose.yml runs with --appendonly yes and --requirepass, giving it durable AOF persistence and a required password, unlike the root docker-compose.yml's dev redis, which has neither a password nor a volume and is documented as wiped on every restart."
    entry_class: FACT
    evidence:
      - "deploy/compose/compose.yml"
      - "docker-compose.yml"
      - "scripts/dev-reset.sh"
  - statement: "deploy/compose/compose.yml declares four named volumes -- buzz-postgres-data, buzz-redis-data, buzz-minio-data, and buzz-git-data (mounted at /data/git, the relay's BUZZ_GIT_REPO_PATH) -- none of which are declared external, so docker compose down (without -v) preserves them while docker compose down -v would destroy all four."
    entry_class: FACT
    evidence:
      - "deploy/compose/compose.yml"
  - statement: "deploy/compose/run.sh's backup_hint lists exactly what an operator must snapshot together: the .env secrets, the owner private key if bootstrap generated one, Postgres data, MinIO/S3 bucket contents, the buzz-git-data volume, and the Caddy data/config volumes when TLS is enabled -- and states these should be captured from the same maintenance window."
    entry_class: FACT
    evidence:
      - "deploy/compose/run.sh"
  - statement: "deploy/compose/README.md distinguishes three run.sh commands by side effect: start (docker compose up -d --wait, does not force a pull) leaves an already-present image tag in place, upgrade (docker compose pull then up -d --wait) is the documented way to pick up a new BUZZ_IMAGE, and restart force-recreates only the relay service without pulling."
    entry_class: FACT
    evidence:
      - "deploy/compose/README.md"
      - "deploy/compose/run.sh"
  - statement: "deploy/compose/README.md's rollback guidance states an image-only rollback (restoring the previous BUZZ_IMAGE value) is safe only when the intervening database migrations are backward-compatible, and otherwise requires restoring the matching pre-upgrade database and object/git snapshots as a coordinated recovery."
    entry_class: FACT
    evidence:
      - "deploy/compose/README.md"
  - statement: "The relay container's healthcheck in deploy/compose/compose.yml probes /_readiness over /dev/tcp with bash, because the runtime image built by the root Dockerfile has bash but no curl/wget/socat installed."
    entry_class: FACT
    evidence:
      - "deploy/compose/compose.yml"
      - "Dockerfile"
  - statement: "relay in deploy/compose/compose.yml declares depends_on conditions requiring postgres, redis, and minio to be service_healthy and minio-init to be service_completed_successfully before it starts, so a stuck or failing backing service blocks the relay container from starting at all rather than starting and failing at runtime."
    entry_class: FACT
    evidence:
      - "deploy/compose/compose.yml"
  - statement: "deploy/compose/.env.example's production defaults enable BUZZ_REQUIRE_AUTH_TOKEN, BUZZ_REQUIRE_RELAY_MEMBERSHIP, and BUZZ_ALLOW_NIP_OA_AUTH, and README.md states closed relay mode additionally requires RELAY_OWNER_PUBKEY (a 64-character hex Nostr pubkey) and a stable BUZZ_RELAY_PRIVATE_KEY."
    entry_class: FACT
    evidence:
      - "deploy/compose/.env.example"
      - "deploy/compose/README.md"
  - statement: "The root docker-compose.yml is a separate, unrelated Compose file used for local development only: it starts postgres, redis, adminer, keycloak, minio, minio-init, and prometheus, but not the buzz-relay binary itself, which developers run natively on the host via cargo run per the Justfile's relay and dev recipes."
    entry_class: FACT
    evidence:
      - "docker-compose.yml"
      - "Justfile"
  - statement: "docker-compose.harness.yml stands up a second, independent Compose project (buzz-harness) with its own postgres/redis/minio on alternate host ports (5471/6471/9471-9472) so a GUI-overhaul test harness never collides with the default dev stack; the harness's own relay process is started separately by scripts/start-isolated-test-relay.sh and is not a service in this compose file."
    entry_class: FACT
    evidence:
      - "docker-compose.harness.yml"
  - statement: "prometheus.yml documents that the local dev Prometheus container scrapes the host-resident relay process at host.docker.internal:9102, because the relay itself runs on the host rather than inside the Compose network -- and deploy/compose/compose.dev.yml's optional prometheus container reuses that same prometheus.yml file and the same host.docker.internal:host-gateway extra_hosts entry."
    entry_class: FACT
    evidence:
      - "prometheus.yml"
      - "deploy/compose/compose.dev.yml"
  - statement: "deploy/charts/buzz/README.md documents a separate Kubernetes Helm chart deployment path for Buzz, with its own production and quickstart profiles, published from ghcr.io/block/buzz/charts/buzz; that chart and the staging cluster it targets per the buzz repository's own AGENTS.md ecosystem table are a distinct deployment surface from this Compose bundle and are out of this node's scope."
    entry_class: FACT
    evidence:
      - "deploy/charts/buzz/README.md"
      - "AGENTS.md"
  - statement: "The Launchpad guard's image-provenance checks -- rejecting ghcr.io/block/buzz outright and requiring a digest or full 40-character commit-SHA tag -- close exactly the gap that launchpad/deploy/AGENTS.md records as the cause of the earlier failed deployment method, so the guard reads as a direct response to that failure rather than a general precaution."
    entry_class: INFERENCE
    evidence:
      - "launchpad/deploy/run.sh"
      - "launchpad/deploy/AGENTS.md"
    confidence: 0.8
---

# Deployment: Docker Compose

Buzz has **two unrelated Docker Compose surfaces** in this repository. This node's
primary subject is the one actually named "deployment": the single-node/VPS
production bundle under `deploy/compose/`. It also documents the root
`docker-compose.yml` (and its `docker-compose.harness.yml` sibling), because both
files answer to the filename `docker-compose.yml` and an agent or operator landing
on this node needs to be told, explicitly, which one they are looking at. See
*Scope and omissions* for why both are covered here rather than split further.

**Authoritative sources — this node summarizes them, it does not replace them:**

| For | Read |
|---|---|
| Full production setup, upgrade and rollback procedure | `deploy/compose/README.md` |
| The production Compose service definitions | `deploy/compose/compose.yml`, `compose.caddy.yml`, `compose.dev.yml` |
| The production runner and its commands | `deploy/compose/run.sh` |
| The Launchpad-specific image guard | `launchpad/deploy/run.sh`, `launchpad/deploy/AGENTS.md` |
| Why an earlier VPS deployment method must not be reused | `launchpad/deploy/VPS-DEPLOYMENT-AUDIT.md` |
| Local dev environment setup | `CONTRIBUTING.md`, `scripts/dev-setup.sh`, `scripts/dev-reset.sh` |
| The production relay image build | `Dockerfile` |
| Kubernetes/Helm deployment (a different surface, not this node) | `deploy/charts/buzz/README.md` |

Where this node and any of those disagree, **they win** — this one has drifted and
should be fixed.

## Environment and topology

Three distinct deployment/runtime environments exist for Buzz's backend, and this
node covers the first two:

1. **Single-node/VPS production (`deploy/compose/`)** — one Docker host runs the
   relay binary itself as a container, alongside its Postgres, Redis and MinIO
   dependencies, optionally fronted by Caddy for TLS. This is the environment this
   node primarily documents.
2. **Local development and CI (root `docker-compose.yml`, `docker-compose.harness.yml`)**
   — backing services only; the relay runs natively on the developer's or CI
   runner's own host. Documented below as a clearly separate, secondary section.
3. **Kubernetes/Helm (`deploy/charts/buzz/`)** — a multi-node, GitOps-managed
   deployment path with its own production and quickstart profiles, targeting the
   staging cluster named in this repository's own `AGENTS.md` ecosystem table.
   **Not documented here** — a different node's subject.

## Execution nodes: `deploy/compose/`

**Physical/virtual node:** one Docker host (a VPS in the normal case). Every
service in `compose.yml` runs on that single host inside one Compose project
(`name: buzz-prod`) and one bridge network (`buzz-net`) local to it. There is no
multi-host orchestration in this file — no scheduler, no cross-host networking, no
replica placement. That is the load-bearing difference from the Kubernetes path in
`deploy/charts/buzz/`.

## Containers/services → this node

| Service | Image | Role | Persistent? | Required before relay starts? |
|---|---|---|---|---|
| `relay` | `${BUZZ_IMAGE}` (must be set; no default) | The `buzz-relay` binary itself — WS + REST + web UI | No (state lives in the services below) | — |
| `postgres` | `postgres:17-alpine` | Primary datastore | Yes, `buzz-postgres-data` | Yes (`service_healthy`) |
| `redis` | `redis:7-alpine`, AOF enabled | Pub/sub fan-out, presence, rate limiting | Yes, `buzz-redis-data` | Yes (`service_healthy`) |
| `minio` | `minio/minio:RELEASE.2025-09-07T16-13-09Z` | S3-compatible media + git CAS storage | Yes, `buzz-minio-data` | Yes (`service_healthy`) |
| `minio-init` | `minio/mc:RELEASE.2025-08-13T08-35-41Z` | One-shot: creates and privatizes the media bucket | No | Yes (`service_completed_successfully`) |
| `caddy` (optional, `compose.caddy.yml`) | `caddy:2-alpine` | TLS-terminating reverse proxy to `relay:3000` | Yes, `buzz-caddy-data`/`buzz-caddy-config` | No (fronts the relay after it's healthy) |

The relay also mounts a fifth named volume directly, `buzz-git-data`, at
`/data/git` — its `BUZZ_GIT_REPO_PATH` for NIP-34 bare repositories.

**Every dependency in the table above is a hard start-order gate, not just a
suggestion:** the relay's own `depends_on` conditions require `postgres`/`redis`/
`minio` to report `service_healthy` and `minio-init` to report
`service_completed_successfully` before Compose will even start the relay
container. A stuck backing service blocks the relay from starting at all, rather
than letting it start and fail at runtime. The relay's own healthcheck probes
`/_readiness` over `/dev/tcp` with `bash` — not `curl`, `wget`, or `socat` —
because the runtime image the root `Dockerfile` builds ships none of those tools.

## Network boundaries

- All services in `compose.yml` share one bridge network, `buzz-net`, local to the
  single Docker host. No service publishes a host port in the base file except the
  relay itself (`${BUZZ_HTTP_PORT:-3000}`).
- **With `compose.caddy.yml`** (`BUZZ_COMPOSE_TLS=true`), the relay's direct port
  publish is explicitly removed (`ports: !reset []`) and only Caddy publishes 80/443
  — the relay becomes reachable only through the reverse proxy, terminating TLS at
  the edge and forwarding plaintext to `relay:3000` inside the Docker network.
- **With `compose.dev.yml`** (`BUZZ_COMPOSE_DEV=true`), Postgres/Redis/MinIO ports
  and two admin UIs (Adminer, Prometheus) are additionally published to the host —
  this overlay is for operator debugging, not a normal production start.
- **Cross-environment note:** the dev-only Prometheus container in
  `compose.dev.yml` reuses the same `prometheus.yml` config as the local-dev stack,
  including its `host.docker.internal:host-gateway` route — but in the
  `deploy/compose/` environment the relay *is* one of the Compose services, so that
  route is present but not load-bearing here the way it is for local dev (see below).

## Persistence boundaries

| What | Where | Survives `docker compose down`? | Survives `down -v`? |
|---|---|---|---|
| Postgres data | `buzz-postgres-data` | Yes | No |
| Redis data (AOF) | `buzz-redis-data` | Yes | No |
| MinIO objects | `buzz-minio-data` | Yes | No |
| Git bare repos | `buzz-git-data` | Yes | No |
| Caddy TLS state | `buzz-caddy-data`, `buzz-caddy-config` (TLS overlay only) | Yes | No |

None of these volumes are declared `external`, so they are ordinary Compose-managed
volumes scoped to this project — `docker compose down` alone preserves all of them;
only an explicit `-v` destroys them. `deploy/compose/run.sh`'s `backup_hint`
enumerates exactly this set (plus the `.env` secrets and any generated owner key)
as what must be snapshotted together, from the same maintenance window, before an
upgrade.

## Trust boundaries and secrets, without exposing any

`deploy/compose/.env.example` is committed with every secret-shaped value set to a
literal `CHANGE_ME_*` placeholder — `BUZZ_RELAY_PRIVATE_KEY`,
`BUZZ_GIT_HOOK_HMAC_SECRET`, `POSTGRES_PASSWORD`, `REDIS_PASSWORD`,
`BUZZ_S3_ACCESS_KEY`, `BUZZ_S3_SECRET_KEY`, and `RELAY_OWNER_PUBKEY`. None of these
are real credentials; this node names their existence and role, not their values,
and does not reproduce any operator's actual secret.

- **Compose enforces their presence structurally.** `postgres`, `redis`, and
  `minio`/`minio-init` in `compose.yml` reference `POSTGRES_PASSWORD`,
  `REDIS_PASSWORD`, `BUZZ_S3_ACCESS_KEY`, and `BUZZ_S3_SECRET_KEY` via Compose's
  `${VAR:?message}` syntax — Compose refuses to start any of these services at all
  if the variable is unset. This is a structural difference from the root
  `docker-compose.yml`'s dev stack, which hardcodes fixed dev-only values instead
  of requiring the operator to supply real ones.
- **`deploy/compose/run.sh` adds a second, script-level gate**: `require_env`
  refuses `start`/`restart`/`upgrade`/`pull` outright if `.env` is missing, or if
  any assignment in it still matches the literal string `CHANGE_ME`.
- **Redis and Postgres are password-protected here**, unlike the dev stack: `redis`
  runs with `--requirepass ${REDIS_PASSWORD:?...}` and AOF persistence
  (`--appendonly yes`), where the dev-only root `docker-compose.yml`'s Redis has no
  password and no volume at all.
- **Auth defaults are stricter than dev.** The `.env.example` production defaults
  turn on `BUZZ_REQUIRE_AUTH_TOKEN`, `BUZZ_REQUIRE_RELAY_MEMBERSHIP`, and
  `BUZZ_ALLOW_NIP_OA_AUTH`. Closed relay mode additionally needs
  `RELAY_OWNER_PUBKEY` (a 64-character hex Nostr pubkey, deliberately not prefixed
  `BUZZ_` per `README.md`) and a stable `BUZZ_RELAY_PRIVATE_KEY` so that REST-created
  content keeps resolving to the same author across restarts.
- **Supply-chain trust boundary — which image gets deployed.** Every command must
  go through `launchpad/deploy/run.sh`, not `deploy/compose/run.sh` directly. The
  Launchpad guard hard-rejects any `ghcr.io/block/buzz` image, requires
  `BUZZ_IMAGE` to resolve to `ghcr.io/launchpad-26/buzz`, and — unless
  `BUZZ_ALLOW_FLOATING_IMAGE=true` is explicitly set — requires a content-addressed
  reference (a `sha256:` digest or a full 40-character `sha-<commit>` tag), not a
  moving tag. `.github/workflows/docker.yml` is what publishes
  `ghcr.io/launchpad-26/buzz` on every push to the `launchpad` branch, so that tag
  family traces directly back to a reviewed commit on this fork.

This last boundary exists **because it was crossed once already**: see
*Failure and recovery implications* below.

## Deployment automation/config as authority, and failure/recovery implications

`deploy/compose/run.sh` is the canonical runner; `launchpad/deploy/run.sh` is a
thin guard in front of it that this repository's operators must use instead of
calling the canonical runner directly. Its commands, in the order an operator
would reach for them:

| Command | Effect | Pulls a new image? |
|---|---|---|
| `check` | Validates Compose config and the image guard; changes nothing | No |
| `start` | `docker compose up -d --wait` | No (uses whatever is already present) |
| `upgrade` | `docker compose pull` then `up -d --wait`, then prints `backup_hint` | Yes |
| `restart` | Force-recreates only the `relay` service | No |
| `stop` | `docker compose down` (volumes preserved) | — |

**Rollback is conditional, not automatic.** `deploy/compose/README.md` states an
image-only rollback (reverting `BUZZ_IMAGE` to the previous immutable reference and
re-running `check`/`upgrade`) is safe *only if* the database migrations shipped
between the two versions are backward-compatible; otherwise the operator must
restore the matching pre-upgrade Postgres and object/git snapshots as one
coordinated recovery, not just swap the image back.

**A real prior failure shapes this design.** `launchpad/deploy/AGENTS.md` records
that an earlier Launchpad VPS deployment method — now moved to
`launchpad/deploy/archived/` and explicitly marked **do not use, run, copy, repair,
extend, or recommend** — defaulted to the hard-coded upstream test image
`ghcr.io/block/buzz:main`. A checkout of `launchpad-26/buzz` could therefore deploy
code built from `block/buzz` instead of from this fork, without the operator
noticing. The current guard's specific checks — refusing `ghcr.io/block/buzz`
outright and requiring an immutable Launchpad-published reference — close exactly
that gap; reading the guard as a direct response to that documented failure rather
than a generic precaution is this node's one inference, not a fact read off any
single file.

## Local development and CI: root `docker-compose.yml` and `docker-compose.harness.yml`

These are a **separate, unrelated** Compose surface — named here because both
answer to the filename this node's path implies, not because they share
infrastructure with `deploy/compose/`.

- **Root `docker-compose.yml`** (`name: buzz`) starts `postgres`, `redis`,
  `adminer`, `keycloak` (local OAuth/OIDC test scaffolding per `CONTRIBUTING.md`),
  `minio`, `minio-init`, and `prometheus` — backing services only. **The relay
  itself is not one of these containers.** Developers run `buzz-relay` natively on
  the host via `cargo run -p buzz-relay` (the Justfile's `relay`/`dev` recipes),
  and `prometheus.yml` scrapes that host-resident process at
  `host.docker.internal:9102` for exactly that reason. Every published host port in
  this file is bound to `127.0.0.1` only. All credentials are fixed, non-secret,
  publicly-committed dev-only defaults — there is nothing here for an operator to
  configure, unlike `deploy/compose/.env.example`'s `CHANGE_ME` placeholders.
  `.github/workflows/ci.yml` and `mesh-lifecycle.yml` bring up the same file's
  `postgres`, `redis`, `minio`, and `minio-init` services directly (with retry
  logic) for CI runs, skipping `adminer`/`keycloak`/`prometheus`.
- **`docker-compose.harness.yml`** stands up a second, independent Compose project
  (`buzz-harness`) — its own `postgres`/`redis`/`minio` on alternate ports
  (`5471`/`6471`/`9471-9472`) so a GUI-overhaul test harness never collides with the
  default dev stack. Its own relay process is started separately by
  `scripts/start-isolated-test-relay.sh` and is not a service in this file.
- **Recovery in this environment** is `just reset` (`scripts/dev-reset.sh`): after
  confirmation, it wipes desktop dev state, runs
  `docker compose down -v --remove-orphans` (destroying the Postgres/MinIO/
  Prometheus volumes — Redis carries no volume and is always ephemeral here), and
  re-runs `dev-setup.sh`. The script's own text is explicit that "installed Buzz
  app state and its production keyring are preserved" — i.e. any real desktop
  credentials live entirely outside this dev Compose stack.
- **Startup ordering** here is enforced by the Justfile's `_ensure-services`
  target, which polls `docker inspect`'s health status for up to 40 × 3 seconds
  before giving up, rather than by Compose `depends_on` health conditions (the dev
  file has none) — every `just relay`/`just dev`/`just admin` invocation depends on
  this gate transitively through `_ensure-migrations`.

## Scope and omissions

**This document covers** the single-node/VPS production Compose bundle under
`deploy/compose/` as its primary subject, and the unrelated local-dev/CI/harness
Compose files at the repository root as a clearly separated secondary section:
their topology and execution nodes, the container/service-to-node mapping, network
and persistence boundaries, secrets handling (named, never reproduced), and
deployment-automation-driven failure/recovery paths.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The Kubernetes/Helm deployment path (`deploy/charts/buzz/`) and the staging cluster it targets via Terraform/ArgoCD in `squareup/block-coder-tf-stacks` | A separate node — this repository cannot see that private repo at all |
| The detailed contents of `launchpad/deploy/archived/` beyond "do not use it" | `launchpad/deploy/VPS-DEPLOYMENT-AUDIT.md`, which this node cites but does not summarize further |
| The `benchmarks/harbor-buzz-orchestra` benchmark stack, which reuses `deploy/compose/compose.yml` under a third Compose project name (`buzz-benchmark`) with its own port overlay | `benchmarks/harbor-buzz-orchestra/scripts/benchmark.py` — read only far enough to confirm it reuses this bundle, not read for its own topology |
| Whether the bootstrap script `deploy/compose/README.md` describes as "eventually" replacing manual `.env` editing exists yet | Not found in this pass; treated as not yet built |
| Per-field documentation of every `deploy/compose/.env.example` variable | `deploy/compose/README.md` and the file itself, which are authoritative and not restated here |

**Expected but not verified when this node was written:**

- **Whether Keycloak (in the root `docker-compose.yml` only) is consumed anywhere
  at runtime.** A search across `crates/buzz-auth/src` and `.env.example` found no
  reference to it; `CONTRIBUTING.md` frames it only as "local OAuth/OIDC testing."
  This node treats it as declared-but-currently-unused scaffolding, consistent with
  what was found, but the search was not exhaustive across every file type.
- **Whether the desktop or mobile apps connect through any part of either Compose
  stack directly, or exclusively through the relay's own published port.** Not
  read in this pass.
- **The actual behavior of `deploy/compose/run.sh`'s `add-member`/`remove-member`/
  `list-members` commands** was read from the script's own case statement, not
  exercised against a running stack.
