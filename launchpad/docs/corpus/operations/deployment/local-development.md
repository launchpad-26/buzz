---
id: operations-deployment-local-development
type: operations
status: draft
origin: launchpad
audiences:
  - operator
  - developer
  - agent
evidence:
  - statement: "This node was authored and checked against repository revision 473205a7457b208455f188847bfb27b01aa83cac."
    entry_class: FACT
    evidence:
      - "commit 473205a7457b208455f188847bfb27b01aa83cac"
  - statement: "CONTRIBUTING.md's First-Time Setup labels activating Hermit (`. ./bin/activate-hermit`) as step 2, marked \"(optional but recommended)\", before step 3 (`just setup`) and step 4 (`just hooks`)."
    entry_class: FACT
    evidence:
      - "CONTRIBUTING.md"
  - statement: "The Justfile's `bootstrap` recipe triggers Hermit's lazy tool download for cargo/node/pnpm, exits with an error and an install pointer if `docker` is not on PATH, copies `.env.example` to `.env` only when `.env` does not already exist (printing a message that the reader should review it before `just dev`), and then runs `scripts/ensure-local-relay-key.sh .env`."
    entry_class: FACT
    evidence:
      - "Justfile"
  - statement: "scripts/ensure-local-relay-key.sh leaves an existing non-empty BUZZ_RELAY_PRIVATE_KEY in the target env file untouched (only chmod 600 is applied), and otherwise generates a fresh secp256k1-range private key with Node's crypto.randomBytes and either replaces the first existing BUZZ_RELAY_PRIVATE_KEY= line or appends one, then chmod 600s the file."
    entry_class: FACT
    evidence:
      - "scripts/ensure-local-relay-key.sh"
  - statement: "The Justfile's `setup` recipe depends on `bootstrap` and then runs `./scripts/dev-setup.sh` with no further arguments."
    entry_class: FACT
    evidence:
      - "Justfile"
  - statement: "scripts/dev-setup.sh: exits early if `docker` is missing or the Docker daemon is not running; loads `.env`, rewriting a legacy `sprout`-default `DATABASE_URL`/`PGUSER`/`PGPASSWORD`/`PGDATABASE` to the current `buzz` defaults for a carried-over `.env`; stops and removes any legacy `sprout-{postgres,redis,adminer,keycloak,minio,minio-init,prometheus}` containers (volumes preserved); refuses to proceed if a non-Docker local Redis is already listening on the port `REDIS_URL` resolves to; runs `bin/just _ensure-services`; polls `pg_isready` inside the `buzz-postgres` container (up to 10 attempts, 2s apart) before running `cargo run -p buzz-admin -- migrate` followed by `scripts/seed-local-community.sh`; installs `desktop/` and `web/` pnpm dependencies when `pnpm` is present (warning and skipping otherwise); installs git hooks via `lefthook install --force` against the shared, absolute `.git/hooks` path; and finally prints Postgres/Redis/Adminer/Keycloak connection info plus the next commands to run (`just relay`, `just dev`) and useful commands (`docker compose ps`, `docker compose logs -f`, `docker compose down`, `./scripts/dev-reset.sh`)."
    entry_class: FACT
    evidence:
      - "scripts/dev-setup.sh"
  - statement: "docker-compose.yml (top-level `name: buzz`) defines seven services on one bridge network `buzz-net`: `postgres` (postgres:17-alpine, container `buzz-postgres`, published `127.0.0.1:5432:5432`, healthcheck `pg_isready -U buzz`), `redis` (redis:7-alpine, container `buzz-redis`, `127.0.0.1:6379:6379`, healthcheck `redis-cli ping`), `adminer` (container `buzz-adminer`, `127.0.0.1:8082:8080`, depends on postgres being healthy), `keycloak` (quay.io/keycloak/keycloak:26.0, `start-dev`, container `buzz-keycloak`, `127.0.0.1:8180:8080`), `minio` (container `buzz-minio`, `127.0.0.1:9000:9000` and `127.0.0.1:9001:9001`), `minio-init` (one-shot, depends on minio healthy, creates the `buzz-media` bucket and sets it private), and `prometheus` (container `buzz-prometheus`, `127.0.0.1:9090:9090`)."
    entry_class: FACT
    evidence:
      - "docker-compose.yml"
  - statement: "The Justfile's internal `_ensure-services` recipe checks `docker inspect --format '{{.State.Health.Status}}'` for `buzz-postgres` and `buzz-redis`; if both already report `healthy` it exits immediately, otherwise it runs `docker compose up -d` and polls the same health status for up to 40 attempts, 3 seconds apart (~120s total), exiting 1 with \"timed out\" if neither becomes healthy in that window."
    entry_class: FACT
    evidence:
      - "Justfile"
  - statement: "The Justfile's `_ensure-migrations` recipe depends on `_ensure-services` and then runs `cargo run -p buzz-admin -- migrate` followed by `./scripts/seed-local-community.sh`; both `relay` and `dev` depend on `bootstrap` and `_ensure-migrations` (`dev` additionally depends on `_ensure-sidecar-stubs`), and the standalone `migrate` recipe is simply `_ensure-migrations`."
    entry_class: FACT
    evidence:
      - "Justfile"
  - statement: "crates/buzz-relay/src/main.rs only runs its own migration step when `BUZZ_AUTO_MIGRATE` parses truthy (case-insensitively `true`/`1`/`yes`/`on`; unset, empty, `false`, `0`, and `no` are all falsy per that function's own unit test), logging \"Skipping database migrations because BUZZ_AUTO_MIGRATE is not enabled\" otherwise; `BUZZ_AUTO_MIGRATE` is unset in `.env.example`, so in the local-dev flow this node documents, migrations are applied by the explicit `buzz-admin migrate` step inside `_ensure-migrations`/`dev-setup.sh`, not by the relay process itself."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs"
      - ".env.example"
  - statement: "The Justfile's `relay` recipe depends on `bootstrap` and `_ensure-migrations`, sources `.env`, and runs `cargo run -p buzz-relay` with no further flags."
    entry_class: FACT
    evidence:
      - "Justfile"
  - statement: "crates/buzz-relay/src/config.rs reads `BUZZ_HEALTH_PORT` and `BUZZ_METRICS_PORT` as u16s, defaulting to 8080 and 9102 respectively when unset or unparsable."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/config.rs"
  - statement: "The Justfile's `dev` recipe depends on `bootstrap`, `_ensure-sidecar-stubs`, and `_ensure-migrations`; sources `.env`; derives `relay_port` from `BUZZ_BIND_ADDR` (default `0.0.0.0:3000`) and reads `BUZZ_HEALTH_PORT`/`BUZZ_METRICS_PORT` (defaults `8080`/`9102`); when `lsof` is available it refuses to proceed and exits 1, naming the offending process, if any of the relay/health/metrics ports is already `LISTEN`-ing; builds `buzz-acp`, `buzz-agent`, `buzz-backend-kubernetes`, `buzz-dev-mcp`, `buzz-cli`, `git-credential-nostr`, and `buzz-relay`; launches `./target/debug/buzz-relay` directly (not via `cargo run`) in the background under a `trap` that kills it on exit; polls `curl --silent --fail --max-time 1 http://127.0.0.1:${health_port}/_readiness` every 0.5s for up to 120 attempts (~60s), exiting 1 with an error if the relay process dies or does not become ready in that window; and, once ready, `cd`s into `desktop/`, installs pnpm dependencies if `node_modules` is absent, sources `scripts/instance-env.sh` for a per-worktree `BUZZ_VITE_PORT`/`BUZZ_TAURI_CONFIG`, and runs `pnpm exec tauri dev --config \"$BUZZ_TAURI_CONFIG\"` (plus `--features mesh-llm` when invoked as `just mesh=1 dev`)."
    entry_class: FACT
    evidence:
      - "Justfile"
  - statement: "The Justfile's `desktop-dev` recipe (no dependencies declared) `cd`s into `desktop/`, installs pnpm dependencies if `node_modules` is absent, sources `scripts/instance-env.sh`, and runs `pnpm exec vite --port \"${BUZZ_VITE_PORT}\" --strictPort` — it starts only the Vite dev server, with no Tauri shell and no relay of its own; a relay must already be reachable at the `BUZZ_RELAY_URL` `instance-env.sh` derives."
    entry_class: FACT
    evidence:
      - "Justfile"
  - statement: "The Justfile's `mobile-dev` recipe opens the iOS Simulator app if the `Simulator` process is not already running (macOS-only: `pgrep -x Simulator` / `open -a Simulator`), runs `scripts/mobile-worktree-overrides.sh`, then `cd`s into the mobile directory, unsets `GIT_DIR`/`GIT_WORK_TREE`, and runs `flutter run` with no further flags."
    entry_class: FACT
    evidence:
      - "Justfile"
  - statement: "The Justfile's `down` recipe is exactly `docker compose down` (stops containers, keeps named volumes); `ps` is exactly `docker compose ps`; `logs *ARGS` is exactly `docker compose logs -f {{ARGS}}`."
    entry_class: FACT
    evidence:
      - "Justfile"
  - statement: "The Justfile's `reset` recipe carries a `[confirm(...)]` attribute prompting \"This will DELETE all development data and preserve installed Buzz. Continue? (y/N)\" before it runs, and then executes `./scripts/dev-reset.sh --yes`."
    entry_class: FACT
    evidence:
      - "Justfile"
  - statement: "scripts/dev-reset.sh, when not passed `--yes`, prints a warning that Postgres/MinIO volumes and desktop dev state will be deleted (Redis is already ephemeral) and prompts for confirmation before proceeding; it then runs `scripts/reset-desktop-dev-state.sh`, runs `docker compose down -v --remove-orphans` (deleting the `buzz-postgres-data`, `buzz-minio-data`, and `buzz-prometheus-data` named volumes), and `exec`s `scripts/dev-setup.sh` to recreate the environment from scratch — installed Buzz app state and its production keyring are stated as preserved, not touched by this teardown."
    entry_class: FACT
    evidence:
      - "scripts/dev-reset.sh"
  - statement: ".env.example documents a `TYPESENSE_API_KEY`/`TYPESENSE_URL` block (defaulting to `http://localhost:8108`), but docker-compose.yml defines no `typesense` service among its seven services — the environment template documents a variable with no corresponding local container in this compose file."
    entry_class: FACT
    evidence:
      - ".env.example"
      - "docker-compose.yml"
  - statement: "The corpus node architecture-deployment-local-development (launchpad/docs/corpus/architecture/deployment/local-development.md) is the canonical description of this same environment's topology, network boundaries, persistence, and failure/recovery implications, already merged at the time this node was authored, and states the same Typesense-versus-compose gap as an open, unresolved documentation drift rather than a hidden service."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/deployment/local-development.md"
  - statement: "The corpus node development-hermit (launchpad/docs/corpus/development/hermit.md) catalogues Hermit's pinned toolchain, its symlink activation mechanism, and where activation is required versus optional in this repository; development-prerequisites (launchpad/docs/corpus/development/prerequisites.md) catalogues the minimum tool versions and Hermit-pinned exact versions a contributor needs before building or running Buzz. Both are already merged at the time this node was authored, and this node defers toolchain-installation detail to them rather than restating it."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/development/hermit.md"
      - "launchpad/docs/corpus/development/prerequisites.md"
  - statement: "This node's steps and their ordering were derived from reading Justfile, docker-compose.yml, .env.example, and the shell scripts it invokes, and from CONTRIBUTING.md's own \"Setting Up the Development Environment\" narrative, which describes the same first-time-setup and running/stopping commands in the same order; no command in this node's task sequences was executed live in this authoring session, so the health-wait loop's actual timing, the port-conflict guard's actual output, and the confirmation-prompt's actual behavior were read from source, not observed running."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1206 task instructions (this task's own scope: author one corpus node from repository evidence, not run the dev stack end-to-end)"
  - statement: "Issue #1206 requires this node to state goal, prerequisites and allowed environment/scope; provide ordered, executable, project-specific steps; define success verification and rollback/cleanup where relevant; and link authoritative commands/config rather than giving generic advice."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1206 definition of done"
  - statement: "This node was written using launchpad/docs/corpus/templates/procedure.md, which was already merged on origin/launchpad at the recorded revision and directs a how-to-shaped body: an Overview, an optional Before you start, one numbered task sequence per logical goal (forking into labeled branches rather than one flattened list when a task genuinely forks), a See also section, an explicit Boundary statement, Relationships, and a Scope and omissions section distinguishing what the node does not cover from what was expected but could not be verified."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/templates/procedure.md"
relationships:
  - type: implements
    target: corpus-template-procedure
  - type: references
    target: architecture-deployment-local-development
  - type: references
    target: development-hermit
  - type: references
    target: development-prerequisites
---

# Running Buzz locally: how-to

How to bring up the relay and Docker infrastructure on your own machine and start a
client against it — the commands to run, in order, and how to tell the relay is
actually serving before you rely on it. For what runs where and why (topology,
network boundaries, persistence), see `architecture-deployment-local-development`
rather than this node.

## Before you start

- **Docker** installed and its daemon running. `just bootstrap` checks for `docker`
  on `PATH` and exits with an install pointer if it is missing; it does not check
  whether the daemon itself is running (`scripts/dev-setup.sh` does that check).
- Either the Hermit toolchain activated (`. ./bin/activate-hermit`, optional but
  recommended per CONTRIBUTING.md) or a manually installed toolchain meeting the
  floor versions `development-prerequisites` catalogues. This node does not restate
  which tools Hermit pins or at which versions — see `development-hermit` and
  `development-prerequisites`.
- A clone of this repository with a shell at its root. Every command below assumes
  that working directory.
- If you plan to launch the desktop app: `pnpm`, resolved from the activated Hermit
  environment or your own install.

## First-time setup

1. Activate Hermit for this shell session, if using it: `. ./bin/activate-hermit`.
2. Run `just setup`. This runs `just bootstrap` first — which downloads Hermit's
   pinned `cargo`/`node`/`pnpm` on first use, copies `.env.example` to `.env` if
   `.env` does not already exist, and generates a fresh `BUZZ_RELAY_PRIVATE_KEY` in
   `.env` if one is not already present — and then runs `scripts/dev-setup.sh`,
   which starts the seven Docker services (`postgres`, `redis`, `adminer`,
   `keycloak`, `minio`, `minio-init`, `prometheus`), waits for Postgres and Redis to
   report healthy, applies pending migrations (`cargo run -p buzz-admin -- migrate`)
   and seeds a local community (`scripts/seed-local-community.sh`), installs desktop
   and web JS dependencies if `pnpm` is available, and installs this repository's
   git hooks (`lefthook install --force`).
3. Review the printed connection info before continuing — it names the exact
   Postgres/Redis URLs and the Adminer (`http://localhost:8082`) and Keycloak
   (`http://localhost:8180`) UIs for this run, and the two example values above may
   not be current after a config change.
4. If you are carrying over a `.env` from before this repository was renamed from
   `sprout`, `scripts/dev-setup.sh` rewrites a legacy `sprout`-default
   `DATABASE_URL`/`PGUSER`/`PGPASSWORD`/`PGDATABASE` to the current `buzz` defaults
   automatically, and stops/removes any legacy `sprout-*`-named containers so the
   current `buzz-*` containers can bind the same ports — no separate action is
   needed for that case.
5. **`.env.example` documents `TYPESENSE_API_KEY`/`TYPESENSE_URL`, but no
   `typesense` service exists in `docker-compose.yml`.** Leave those two variables
   as generated; they name no running local service at the recorded revision, and
   nothing in this task's evidence resolved whether that is stale documentation or
   an unimplemented integration — see `architecture-deployment-local-development`'s
   own note on the same gap.

## Start the relay

Do this in its own terminal; it stays in the foreground.

1. Run `just relay`. This depends on `bootstrap` and `_ensure-migrations`, so it
   re-runs the same Hermit-download/`.env`-creation checks, starts the Docker
   services if they are not already healthy (waiting up to ~120 seconds), applies
   any pending migrations, and then runs `cargo run -p buzz-relay` with `.env`
   sourced into its environment.
2. Wait for the relay's own log output to settle before treating it as ready; this
   command does not itself health-check the process it starts. To confirm
   readiness independently, see *Verify the relay is serving* below.
3. To also serve the built web UI directly from the relay instead of running a
   separate Vite server, run `just relay-web` in place of `just relay` — it builds
   `web/` and sets `BUZZ_WEB_DIR` before the same `cargo run -p buzz-relay` step.
   This node does not cover the web client's own development workflow beyond this
   one substitution.

## Start a client against the relay

Pick the branch for the client you want to run. Each assumes a relay is already
reachable — either started per the previous section, or (desktop only) started
automatically by the branch itself.

**a. Desktop app, relay managed for you.** Run `just dev` in a fresh terminal
instead of `just relay`. It depends on `bootstrap`, `_ensure-sidecar-stubs`, and
`_ensure-migrations`; before doing anything else it checks whether the relay,
health, or metrics port (derived from `BUZZ_BIND_ADDR`, `BUZZ_HEALTH_PORT`,
`BUZZ_METRICS_PORT` — defaults `3000`, `8080`, `9102`) is already bound by another
process, and refuses to launch against a possibly-stale relay if so, naming the
offending process. It then builds the agent-tooling crates and `buzz-relay`,
launches the built relay binary directly in the background, polls its `/_readiness`
endpoint for up to ~60 seconds, and only then launches the Tauri desktop app; the
relay is killed automatically when the app quits or the command is interrupted.

**b. Desktop frontend only, relay started separately.** If you already started a
relay per *Start the relay* above (or want relay logs in a separate terminal from
the desktop process), run `just desktop-dev` instead of `just dev`. It starts only
the Vite dev server for the desktop app's frontend, with no Tauri shell of its own,
against whichever relay `scripts/instance-env.sh` resolves for your worktree.

**c. Mobile app (iOS simulator).** With a relay already running per *Start the
relay*, run `just mobile-dev`. It opens the iOS Simulator if one is not already
running, applies this worktree's debug identity overrides, and runs `flutter run`.
This recipe is written for macOS (it shells out to `pgrep -x Simulator` /
`open -a Simulator`); this node does not cover Android or a non-macOS mobile
workflow.

**d. Web client.** Not covered as a numbered branch here — `just relay-web` in
*Start the relay* above is this repository's one documented way to serve the web
client from the relay itself in local dev; a separate `web`-only Vite dev server
recipe exists in the Justfile but its own development workflow is out of this
node's scope (see *Boundary*).

## Verify the relay is serving

1. Confirm the relay process is actually listening: with the default
   `BUZZ_HEALTH_PORT` (`8080`), run
   `curl --silent --fail --max-time 1 http://127.0.0.1:8080/_readiness`. This is the
   exact check `just dev` itself polls before launching the desktop app — a
   non-zero exit means the relay is not yet ready (or not running), not that the
   command itself is broken.
2. Confirm the Docker infrastructure is healthy independently of the relay: run
   `just ps` (`docker compose ps`) and check that `buzz-postgres` and `buzz-redis`
   report a healthy status, the same status `_ensure-services` polls internally.
3. If either check fails, run `just logs` (`docker compose logs -f`) to tail every
   service's output, or `just logs <service>` to tail one service by its
   `docker-compose.yml` name (for example `just logs postgres`).

## Stop or reset

- **Stop without losing data.** Run `just down` (`docker compose down`). Containers
  stop; the three named volumes (`buzz-postgres-data`, `buzz-minio-data`,
  `buzz-prometheus-data`) are preserved.
- **Wipe and start fresh.** Run `just reset`. It prompts for confirmation (the
  Justfile's own `[confirm(...)]` attribute) unless bypassed, then runs
  `scripts/dev-reset.sh --yes`: this removes desktop-only development state,
  runs `docker compose down -v --remove-orphans` (deleting all three named
  volumes — Redis had no volume to begin with), and re-runs the first-time setup
  script to recreate the environment. Installed Buzz app state and its production
  keyring are not touched by this reset.

## See also

- `architecture-deployment-local-development` — the topology this procedure brings
  up: which pieces are containers versus native processes, network boundaries
  (every Docker service is loopback-only; the relay itself is not, by default),
  persistence, and failure/recovery implications in more depth than this node
  restates.
- `development-hermit` — what Hermit pins in this repository, its activation
  mechanism, and where activation is required versus optional.
- `development-prerequisites` — the minimum and Hermit-pinned tool versions this
  procedure's *Before you start* section assumes are already met.
- A Docker-Compose-focused deployment node for this same `docker-compose.yml`
  (parented to a sibling task in this same Feature) is expected to land separately;
  see *Boundary* below for how the two are meant to divide the subject.

## Boundary

This node does not describe:
- **Which fields to look up on a command or config file** — flags, environment
  variable meanings beyond what a step needs to run it, or the full `.env.example`
  contents. That is reference-shaped content; `.env.example` itself, read directly,
  is the authoritative source until a corresponding reference-shaped corpus node
  exists.
- **How to acquire the underlying skill of building a Rust/Tauri/Flutter project
  from scratch**, for a newcomer to this toolchain — a tutorial, which has no
  corpus template as of this writing.
- **Why this topology is shaped the way it is** — why Docker for infrastructure but
  native processes for the relay and clients, why the relay binds `0.0.0.0` while
  the Docker services bind loopback-only, and similar design rationale. See
  `architecture-deployment-local-development` for that discussion; this node only
  instructs the actions.
- **`docker-compose.yml` considered on its own terms** — as a deployment artifact
  with its own configuration surface, service-by-service rationale, and any
  production-adjacent use — is a sibling task's subject in this same Feature, not
  this node's. This node treats `docker-compose.yml` only instrumentally, as the
  thing `just setup`/`_ensure-services` start and wait on, in service of bringing
  the whole local-dev system up; drawing that boundary more precisely is the other
  task's to do, and this node does not link it because no such node exists on
  `origin/launchpad` yet.
- **Staging or production deployment** — Kubernetes via `block-coder-tf-stacks`,
  the relay Docker image built by `sprout-oss`, or Blox workstation provisioning
  via `sprout-backend-blox` — entirely separate execution environments per the
  top-level `AGENTS.md` ecosystem table, not local development.
- **The admin dashboard's own workflow** (`just admin`, `just admin-seed`) beyond
  noting that it exists as a separate Justfile recipe family from the ones this
  node walks through.

## Relationships

- `implements`: `corpus-template-procedure` — this node is a how-to-shaped instance
  of that template.
- `references`: `architecture-deployment-local-development` — this procedure brings
  up exactly the topology that node describes; the reader is assumed able to open
  it for network-boundary, persistence, and failure/recovery depth this node does
  not restate.
- `references`: `development-hermit` — this procedure's *Before you start* and
  first setup step assume Hermit activation works the way that node documents,
  without restating its pinned-tool table or symlink mechanism.
- `references`: `development-prerequisites` — this procedure's *Before you start*
  assumes the tool-version floor that node catalogues, without restating it.

No `depends-on` or `part-of` edge is declared: this procedure does not require any
of the three referenced nodes to remain unchanged for its own steps to still be
correct (a `references` edge, not `depends-on`), and it is not a constituent
section of a broader operations node — no such broader node exists on
`origin/launchpad` at the recorded revision. A `references`-only edge to a future
`operations`-typed Docker-Compose deployment node (the sibling task named in *See
also* and *Boundary*) is not declared here because no such node exists yet; per
`launchpad/docs/corpus/AGENTS.md`'s own rule, a `relationships[].target` must
resolve on the branch being merged into, and it does not.

## Scope and omissions

**This node covers** the executable sequence for bringing up Buzz's local
development environment from a fresh clone — activating Hermit, creating `.env`,
running `just setup`, starting the relay with `just relay` (or `just relay-web`),
starting a client (desktop via `just dev` or `just desktop-dev`, or mobile via
`just mobile-dev`), confirming the relay is actually serving, and stopping or
resetting the environment afterward — grounded in the Justfile recipes, the
Docker Compose service definitions, `.env.example`, and the shell scripts those
recipes invoke.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| `docker-compose.yml` as a deployment artifact in its own right | A sibling task in this Feature, not yet a corpus node on `origin/launchpad` |
| Local-dev topology, network boundaries, persistence, failure/recovery depth | `architecture-deployment-local-development` |
| Hermit's pinned toolchain and activation mechanism | `development-hermit` |
| Minimum and pinned tool versions | `development-prerequisites` |
| Field-by-field reference for `.env.example`, `docker-compose.yml`, or Justfile flags | No reference-shaped corpus node exists yet for these; read the files directly |
| The admin dashboard's own workflow (`just admin`, `just admin-seed`) | Not authored as a corpus node at the recorded revision |
| Android or non-macOS mobile local-dev workflow | Not authored as a corpus node at the recorded revision; `just mobile-dev` itself is macOS/iOS-Simulator-specific |
| Staging/production deployment | `block-coder-tf-stacks`, `sprout-oss`, `sprout-backend-blox`, per the top-level `AGENTS.md` ecosystem table |

**Expected but not verified when this node was written:**

- **No command in this node's task sequences was executed live in this authoring
  session.** `just setup`, `just relay`, `just dev`, `just desktop-dev`,
  `just mobile-dev`, `just down`, and `just reset` were all read from their
  Justfile and shell-script source, not run — matching the same disclosure
  `architecture-deployment-local-development` makes about its own evidence. The
  health-wait loop's actual timing, the port-conflict guard's actual console
  output, the `/_readiness` polling's actual behavior under a slow build, and the
  `[confirm(...)]` prompt's actual interactive behavior were not observed running.
- **Whether the `.env.example` Typesense variables reflect stale documentation or
  an unimplemented integration was not established** — only that no `typesense`
  service exists in `docker-compose.yml` today, matching the same open gap
  `architecture-deployment-local-development` records.
- **The web client's own standalone development workflow** (the Justfile's `web`
  recipe, distinct from `just relay-web`) was located but not exercised or
  described as a numbered branch here, since the issue's own subject-matter list
  names desktop and mobile explicitly and the web client only via the relay-served
  path; whether it deserves its own branch in a future revision of this node is an
  open question this task does not resolve.
- **Whether a Docker-Compose-focused sibling node (this node's named boundary
  above) will end up owning any content this node currently states about
  `docker-compose.yml`'s service list was not resolved with that task's author**,
  since no such node exists yet to reconcile against.
