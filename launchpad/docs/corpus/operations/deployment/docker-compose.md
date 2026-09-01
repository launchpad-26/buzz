---
id: operations-deployment-docker-compose
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
  - statement: "deploy/compose/README.md states that this bundle is the single-node/VPS deployment bundle and is intentionally separate from the root docker-compose.yml, which remains local development infrastructure."
    entry_class: FACT
    evidence:
      - "deploy/compose/README.md"
  - statement: "The root docker-compose.yml declares services for postgres, redis, adminer, keycloak, minio, minio-init and prometheus, and declares no relay service at all, so the buzz-relay binary is never one of its containers."
    entry_class: FACT
    evidence:
      - "docker-compose.yml"
  - statement: "deploy/compose/.env.example marks BUZZ_RELAY_PRIVATE_KEY, BUZZ_GIT_HOOK_HMAC_SECRET, POSTGRES_PASSWORD, REDIS_PASSWORD, BUZZ_S3_ACCESS_KEY, BUZZ_S3_SECRET_KEY and RELAY_OWNER_PUBKEY as CHANGE_ME placeholders the operator must replace, and instructs setting BUZZ_IMAGE to a digest or the full 40-character commit-SHA tag rather than a moving tag."
    entry_class: FACT
    evidence:
      - "deploy/compose/.env.example"
  - statement: "deploy/compose/run.sh's require_env function refuses start, restart, upgrade and pull when deploy/compose/.env is missing or still contains the literal string CHANGE_ME; confirmed by running ./run.sh start from deploy/compose twice — once with .env absent and once with .env copied unedited from .env.example — each exiting 1 before any container was touched."
    entry_class: FACT
    evidence:
      - "deploy/compose/run.sh"
      - "run_command('cd deploy/compose; remove the environment file entirely; ./run.sh start') -> exit 1: refuses to start because the environment file is missing"
      - "run_command('cd deploy/compose; copy the example template to the environment file unedited; ./run.sh start') -> exit 1: refuses to start because the environment file still contains CHANGE_ME placeholders"
  - statement: "launchpad/deploy/run.sh requires deploy/compose/.env to carry exactly one BUZZ_IMAGE assignment resolving to ghcr.io/launchpad-26/buzz, rejects ghcr.io/block/buzz outright, requires Docker Compose 2.24.4 or newer, and only delegates to deploy/compose/run.sh once those checks pass; its own check subcommand additionally runs docker compose config to validate the merged Compose file before reporting success."
    entry_class: FACT
    evidence:
      - "launchpad/deploy/run.sh"
  - statement: "Running ./launchpad/deploy/run.sh check from the repository root, against a deploy/compose/.env built from .env.example with every CHANGE_ME value replaced by a non-secret placeholder, passed cleanly both without BUZZ_COMPOSE_TLS and with BUZZ_COMPOSE_TLS=true, printing 'Launchpad deployment configuration is valid.' in both cases."
    entry_class: INFERENCE
    evidence:
      - "run_command('./launchpad/deploy/run.sh check') -> Launchpad relay image: ghcr.io/launchpad-26/buzz:sha-0000...; Docker Compose version: 5.5.0; Launchpad deployment configuration is valid."
      - "run_command('BUZZ_COMPOSE_TLS=true BUZZ_DOMAIN=buzz.example.com ./launchpad/deploy/run.sh check') -> Launchpad deployment configuration is valid."
    confidence: 0.9
  - statement: "The same guard rejects a BUZZ_IMAGE of ghcr.io/block/buzz:main with 'Upstream Block image ... is forbidden for Launchpad deployment', and separately rejects a floating ghcr.io/launchpad-26/buzz:launchpad tag with 'Floating images are rejected' unless BUZZ_ALLOW_FLOATING_IMAGE=true is set; both were confirmed by running the check command against each image value in turn."
    entry_class: FACT
    evidence:
      - "launchpad/deploy/run.sh"
      - "run_command('set BUZZ_IMAGE to ghcr.io/block/buzz:main in the environment file, then ./launchpad/deploy/run.sh check') -> exit 1: Launchpad deployment check failed: Upstream Block image is forbidden for Launchpad deployment"
      - "run_command('set BUZZ_IMAGE to a floating ghcr.io/launchpad-26/buzz tag in the environment file, then ./launchpad/deploy/run.sh check') -> exit 1: Launchpad deployment check failed: Floating images are rejected unless BUZZ_ALLOW_FLOATING_IMAGE is set"
  - statement: "launchpad/deploy/AGENTS.md states that an earlier Launchpad VPS deployment method, now moved to launchpad/deploy/archived/, defaulted to the hard-coded upstream test image ghcr.io/block/buzz:main and must not be used, run, copied, repaired, extended or recommended."
    entry_class: FACT
    evidence:
      - "launchpad/deploy/AGENTS.md"
  - statement: ".github/workflows/docker.yml publishes ghcr.io/launchpad-26/buzz on every push to the launchpad branch, tagging it :launchpad and :sha-<full 40-character commit>, which is the image family both deploy/compose/.env.example and the Launchpad guard require."
    entry_class: FACT
    evidence:
      - ".github/workflows/docker.yml"
  - statement: "deploy/compose/compose.yml's relay, postgres, redis, minio and minio-init services require POSTGRES_PASSWORD, REDIS_PASSWORD, BUZZ_S3_ACCESS_KEY and BUZZ_S3_SECRET_KEY via Compose's ${VAR:?...} syntax, and the relay's depends_on conditions require postgres, redis and minio to report service_healthy and minio-init to report service_completed_successfully before Compose starts the relay container at all; confirmed by running docker compose --env-file .env -f compose.yml config --images against a placeholder .env, which resolved cleanly and printed all five configured images."
    entry_class: FACT
    evidence:
      - "deploy/compose/compose.yml"
      - "run_command('cd deploy/compose; docker compose, pointed at the environment file, -f compose.yml config --images') -> ghcr.io/launchpad-26/buzz:sha-0000...; postgres:17-alpine; redis:7-alpine; minio/minio:RELEASE.2025-09-07T16-13-09Z; minio/mc:RELEASE.2025-08-13T08-35-41Z"
  - statement: "buzz-relay's own startup path (crates/buzz-relay/src/main.rs) only runs database migrations when buzz_auto_migrate_enabled reads BUZZ_AUTO_MIGRATE as enabled, logging 'Skipping database migrations because BUZZ_AUTO_MIGRATE is not enabled' otherwise; deploy/compose/.env.example sets BUZZ_AUTO_MIGRATE=true among its production defaults, so a first boot from the committed template runs migrations automatically unless the operator turns that default off."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs"
      - "deploy/compose/.env.example"
  - statement: "buzz-admin's Command enum defines a Migrate variant, invoked as buzz-admin migrate, which is the manual alternative deploy/compose/README.md names for running migrations before starting the relay when BUZZ_AUTO_MIGRATE is left disabled."
    entry_class: FACT
    evidence:
      - "crates/buzz-admin/src/main.rs"
      - "deploy/compose/README.md"
  - statement: "deploy/compose/README.md's Validation section verifies a fresh install by running ./launchpad/deploy/run.sh check, then start, then curl against /_liveness on the configured BUZZ_HTTP_PORT, then ./launchpad/deploy/run.sh status."
    entry_class: FACT
    evidence:
      - "deploy/compose/README.md"
  - statement: "deploy/compose/README.md documents inspecting the running relay's configured versus actual image with docker compose config --images, docker compose ps -q relay, and docker inspect / docker image inspect to read the immutable image digest, and states that the publishing workflow's own run summary records both the digest and the full commit-SHA tag together with a provenance-verification command."
    entry_class: FACT
    evidence:
      - "deploy/compose/README.md"
  - statement: "deploy/compose/README.md distinguishes start (docker compose up -d --wait, no forced pull), upgrade (pull then up -d --wait, then prints the backup checklist) and restart (force-recreates only the relay service, no pull) by side effect, and deploy/compose/run.sh's case statement implements exactly that behavior."
    entry_class: FACT
    evidence:
      - "deploy/compose/README.md"
      - "deploy/compose/run.sh"
  - statement: "deploy/compose/run.sh's backup_hint lists what an operator must snapshot together, from the same maintenance window: deploy/compose/.env (especially BUZZ_RELAY_PRIVATE_KEY, the database/Redis/S3 secrets and BUZZ_GIT_HOOK_HMAC_SECRET), any bootstrap-generated owner private key, Postgres data, MinIO/S3 bucket contents, the buzz-git-data volume, and the Caddy data/config volumes when compose.caddy.yml is in use."
    entry_class: FACT
    evidence:
      - "deploy/compose/run.sh"
  - statement: "deploy/compose/README.md states that an image-only rollback — reverting BUZZ_IMAGE to the previous immutable reference and re-running check/upgrade — is safe only when the database migrations shipped between the two versions are backward-compatible, and otherwise requires restoring the matching pre-upgrade Postgres and object/git snapshots as one coordinated recovery rather than swapping the image back alone."
    entry_class: FACT
    evidence:
      - "deploy/compose/README.md"
  - statement: "None of deploy/compose/compose.yml's four named volumes (buzz-postgres-data, buzz-redis-data, buzz-minio-data, buzz-git-data) are declared external, so a plain docker compose down preserves all four and only an explicit -v destroys them; deploy/compose/run.sh's stop command runs docker compose down with no -v flag."
    entry_class: FACT
    evidence:
      - "deploy/compose/compose.yml"
      - "deploy/compose/run.sh"
  - statement: "A search of deploy/, launchpad/deploy/ and scripts/ for a bootstrap script matching deploy/compose/README.md's forward-looking statement that a bootstrap script 'should eventually replace manual .env editing' found no such script anywhere in the repository."
    entry_class: FACT
    evidence:
      - "deploy/compose/README.md"
      - "run_command('grep -rl bootstrap deploy/ launchpad/deploy/ scripts/; find . -iname *bootstrap*') -> no compose-bootstrap script found; only unrelated matches (ADR-0040, desktop/mobile terminal and push bootstrap code, archived runbook prose)"
  - statement: "launchpad/deploy/runbooks/dev-deployment-SOP.md, a separate cohort-internal document that walks building a hardened development VM by hand, copies deploy/compose into that VM and confirms in its own text that the resulting Docker network is named buzz-prod_buzz-net, matching compose.yml's name: buzz-prod project declaration; that document is materially broader in scope (VM provisioning, hardening, agent bootstrap) than this node and is not restated here."
    entry_class: FACT
    evidence:
      - "launchpad/deploy/runbooks/dev-deployment-SOP.md"
      - "deploy/compose/compose.yml"
  - statement: "deploy/charts/buzz/README.md documents a separate Kubernetes Helm chart deployment path for Buzz with its own production and quickstart operating profiles, published as an OCI chart from ghcr.io/block/buzz/charts/buzz, which is a distinct deployment surface from this Compose bundle."
    entry_class: FACT
    evidence:
      - "deploy/charts/buzz/README.md"
  - statement: "launchpad/docs/corpus/architecture/deployment/docker-compose.md documents the topology, containers, network and persistence boundaries of this same deploy/compose/ bundle at the architecture level, including the same environment/topology distinction this node draws between single-node/VPS production, local development and Kubernetes; this node is the operator-facing how-to built on top of it and defers to it for the why and what rather than restating them."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/deployment/docker-compose.md"
  - statement: "This node was written using launchpad/docs/corpus/templates/procedure.md, which was already merged on origin/launchpad at the recorded revision and directs a how-to-shaped node to carry an Overview, an optional Before you start, one or more numbered task sequences, a See also section, an explicit Boundary statement, Relationships, and a Scope and omissions section distinguishing what is out of scope from what was expected but not verified."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/templates/procedure.md"
relationships:
  - type: references
    target: architecture-deployment-docker-compose
  - type: implements
    target: corpus-template-procedure
---

# Deploying Buzz with Docker Compose: how-to

Bring the single-node/VPS production Compose bundle under `deploy/compose/` from a
fresh checkout to a live, verified relay, and upgrade or roll it back safely
afterward. Read `architecture-deployment-docker-compose` first if you have not —
this node assumes that topology (the five services, the network and volume
boundaries, the trust boundaries around secrets and the image guard) and does not
restate it here.

## Before you start

- A Docker host (a VPS in the normal case) with Docker Compose v2.24.4 or newer —
  `./launchpad/deploy/run.sh check` verifies the version for you and fails clearly
  if it is too old.
- A checkout of this repository, or at minimum `deploy/compose/` and
  `launchpad/deploy/` copied onto the host — the guard script resolves
  `deploy/compose/run.sh` relative to its own location, and `deploy/compose/.env`
  relative to the repository root.
- A published `ghcr.io/launchpad-26/buzz` image to deploy. `.github/workflows/docker.yml`
  builds and publishes one automatically on every push to the `launchpad` branch,
  tagged both `:launchpad` (moving) and `:sha-<full 40-character commit>`
  (immutable) — use the immutable tag, or a digest, for production.
- This is the single-node/VPS deployment path only. It is not the same file or
  procedure as local development (the root `docker-compose.yml`, which starts no
  relay container at all — see *Boundary*), and it is not the Kubernetes/Helm
  chart path (`deploy/charts/buzz/`).

## Configure the environment

1. From the repository root, copy the template: `cd deploy/compose && cp .env.example .env`.
2. Edit `.env` and replace every `CHANGE_ME_*` placeholder with a real, generated
   value: `BUZZ_RELAY_PRIVATE_KEY`, `BUZZ_GIT_HOOK_HMAC_SECRET`, `POSTGRES_PASSWORD`,
   `REDIS_PASSWORD`, `BUZZ_S3_ACCESS_KEY`, `BUZZ_S3_SECRET_KEY`, and
   `RELAY_OWNER_PUBKEY` (a 64-character hex Nostr pubkey) if you are running a
   closed relay. Keep these stable across restarts — several of them, notably the
   relay private key, change the identity content resolves to if they rotate.
3. Set `BUZZ_IMAGE` to either `ghcr.io/launchpad-26/buzz@sha256:<digest>` or the
   workflow's `ghcr.io/launchpad-26/buzz:sha-<full 40-character commit>` tag —
   never the moving `:launchpad` tag, and never `ghcr.io/block/buzz` in any form.
   The next step's guard rejects both of the latter outright; see *Boundary* for
   why that rejection exists.
4. If you are fronting the relay with TLS, also set `BUZZ_DOMAIN` (and the
   derived `RELAY_URL`, `BUZZ_MEDIA_BASE_URL`, `BUZZ_MEDIA_SERVER_DOMAIN`,
   `BUZZ_CORS_ORIGINS` values) to your real hostname.
5. Return to the repository root: `cd ../..`. Every command from here on runs
   from there.

## Validate and start the stack

1. Run `./launchpad/deploy/run.sh check`. This is the Launchpad-specific guard in
   front of the canonical `deploy/compose/run.sh` runner — it verifies your
   Compose version, parses `BUZZ_IMAGE` out of `.env`, rejects it outright if it
   names `ghcr.io/block/buzz` in any form or is missing, warns and then rejects a
   non-immutable reference unless `BUZZ_ALLOW_FLOATING_IMAGE=true` is explicitly
   set, and finally validates the merged Compose configuration. Fix whatever it
   reports before continuing.
2. Run `./launchpad/deploy/run.sh start`. For automatic HTTPS via the bundled
   Caddy reverse proxy, prefix it instead: `BUZZ_COMPOSE_TLS=true
   ./launchpad/deploy/run.sh start`. Either form runs `docker compose up -d
   --wait` under the hood and does not force a pull — an already-present image
   tag is reused as-is.
3. Expect the relay container to wait, not fail, if its dependencies are slow:
   Compose will not even start the `relay` container until `postgres`, `redis`
   and `minio` report `service_healthy` and `minio-init` reports
   `service_completed_successfully`. If `start` times out, check those services'
   own health first rather than the relay's logs.
4. Do not assume a fresh database is migrated automatically without checking:
   the relay only runs migrations at startup when `BUZZ_AUTO_MIGRATE` is enabled,
   and `deploy/compose/.env.example`'s committed production defaults set
   `BUZZ_AUTO_MIGRATE=true` — so a first boot from the unedited template migrates
   on its own. If you turned that default off, run `buzz-admin migrate` (inside
   the `relay` container, once it exists, or via `docker compose exec relay
   /usr/local/bin/buzz-admin migrate`) before expecting the relay to serve
   traffic against a fresh database.

## Verify the deployment is live

1. Confirm liveness on the health port: `curl -fsS
   "http://127.0.0.1:$(grep -E '^BUZZ_HTTP_PORT=' deploy/compose/.env | cut -d= -f2-)/_liveness"`.
2. Check service status: `./launchpad/deploy/run.sh status` (a thin wrapper over
   `docker compose ps`) — every service should show healthy, not merely running.
3. Confirm the image actually running matches what you intended to deploy, not
   only what `.env` says: `cd deploy/compose && docker compose config --images`
   shows the configured reference; `container_id=$(docker compose ps -q relay)`
   and `docker inspect --format 'configured={{.Config.Image}}
   image_id={{.Image}}' "$container_id"` show what the running container
   actually resolved to; `docker image inspect --format
   'repo_digests={{json .RepoDigests}}' "$image_id"` shows the immutable digest
   backing it. The publishing workflow's own run summary records the same digest
   alongside the full commit-SHA tag and a `gh attestation verify` command, if
   you need to confirm the image traces back to a specific reviewed commit.
4. If you enabled TLS, confirm the public hostname resolves and serves over
   HTTPS through Caddy, not by hitting the relay's own port directly — with
   `compose.caddy.yml` active, the relay no longer publishes a host port at all.

## Upgrade to a new image

1. Take a backup first: `./launchpad/deploy/run.sh backup-hint` prints exactly
   what to snapshot together, from the same maintenance window — `.env`'s
   secrets, any bootstrap-generated owner key, Postgres data, MinIO/S3 bucket
   contents, the `buzz-git-data` volume, and the Caddy data/config volumes if
   TLS is enabled.
2. Update only `BUZZ_IMAGE` in `.env` to the new, already-verified digest or
   full commit-SHA tag.
3. Run `./launchpad/deploy/run.sh check` again — it re-validates the new
   reference against the same image guard.
4. Run `./launchpad/deploy/run.sh upgrade`. This runs `docker compose pull` and
   then `up -d --wait` (unlike `start`, it always pulls), and prints the same
   backup checklist again afterward as a reminder for next time.
5. Re-verify per *Verify the deployment is live*, above, before considering the
   upgrade complete.

## Roll back an upgrade

1. Determine whether the database migrations that shipped between the old and
   new image are backward-compatible — check `migrations/` for what changed
   between the two commits. This decides which of the next two steps applies.
2. **If the migrations are backward-compatible**, an image-only rollback is
   sufficient: restore the previous immutable `BUZZ_IMAGE` value in `.env`, then
   run `check` and `upgrade` again as in the steps above.
3. **If they are not**, an image-only rollback is not safe. Restore the matching
   pre-upgrade Postgres, MinIO/S3, and `buzz-git-data` snapshots you took under
   *Upgrade to a new image* step 1, alongside the previous `BUZZ_IMAGE` value,
   as one coordinated recovery — swapping only the image back while the schema
   has moved forward is exactly the case `deploy/compose/README.md` warns is
   unsafe.
4. Re-verify per *Verify the deployment is live* once more.

## Stop the stack

1. `./launchpad/deploy/run.sh stop` runs `docker compose down` with no `-v`
   flag — every named volume (`buzz-postgres-data`, `buzz-redis-data`,
   `buzz-minio-data`, `buzz-git-data`, and the Caddy volumes if present) survives
   because none of them is declared `external`; only an explicit `-v` you run
   yourself destroys them, and no command in `run.sh` passes it.

## See also

- `architecture-deployment-docker-compose` — the topology, containers, network
  boundaries and secrets-handling this node builds its steps on top of; read it
  first, not after.
- `deploy/compose/README.md` — the fuller narrative version of this procedure,
  including per-variable production notes this node does not restate.
- `launchpad/deploy/AGENTS.md` — why every command here must go through
  `launchpad/deploy/run.sh` rather than `deploy/compose/run.sh` directly, and
  what not to reuse from `launchpad/deploy/archived/`.
- `launchpad/deploy/runbooks/dev-deployment-SOP.md` — a broader, cohort-internal
  rehearsal that provisions and hardens a whole development VM and exercises
  this same Compose bundle inside it; out of scope here, useful if you need the
  VM-level context this node does not cover.
- `deploy/charts/buzz/README.md` — the separate Kubernetes/Helm deployment path,
  for a multi-node or GitOps-managed target instead of a single Docker host.

## Boundary

This node does not describe:
- **Per-variable reference documentation for every `deploy/compose/.env.example`
  setting** — facts to look up rather than actions to perform. `deploy/compose/README.md`
  and the `.env.example` file itself are authoritative for that and are linked
  above, not duplicated here.
- **Local development.** The root `docker-compose.yml` starts backing services
  only (Postgres, Redis, Adminer, Keycloak, MinIO, Prometheus) and no relay
  container at all — developers run `buzz-relay` natively via `cargo run`. That
  is a different file, a different audience, and a different procedure, owned
  by a sibling operations task under this same Feature that has not been
  authored yet; it is named here only in prose, not linked as a corpus path,
  because the path does not exist yet.
- **The Kubernetes/Helm deployment path** (`deploy/charts/buzz/`) — a
  structurally different, multi-node surface with its own production and
  quickstart profiles. See `deploy/charts/buzz/README.md`.
- **How to acquire Docker or Docker Compose skill from scratch, for a newcomer**
  — a tutorial, which has no corpus template as of this writing.
- **Why the topology is shaped the way it is** — the choice of five services,
  the network and persistence boundaries, and the reasoning behind the image
  guard's specific checks. That is `architecture-deployment-docker-compose`'s
  subject; this node assumes it and instructs the actions on top of it.
- **Provisioning or hardening the host VM or server itself**, and any
  Ansible-driven automation — `launchpad/deploy/runbooks/dev-deployment-SOP.md`
  is the broader, cohort-internal document for that; this node starts from "you
  already have a Docker host."

## Relationships

- references: `architecture-deployment-docker-compose` — the architecture-level
  node this how-to is built on top of, for the topology and secrets-handling
  background this node assumes rather than restates.
- implements: `corpus-template-procedure` — this node is written to that
  template's Required sections.

## Scope and omissions

**This node covers** the operator-facing procedure for deploying Buzz with the
`deploy/compose/` bundle: configuring the environment, validating and starting
the stack for the first time, verifying that the deployment is actually live and
running the intended image, upgrading to a new image, rolling back an upgrade
depending on migration compatibility, and stopping the stack without losing
state. It draws an explicit line against local development (the root
`docker-compose.yml`, which is a different file with no relay container) and
against the Kubernetes/Helm path, rather than covering either.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Per-variable reference for every `.env.example` setting | `deploy/compose/README.md`, `deploy/compose/.env.example` |
| Local development setup and its own procedure | A sibling operations task under this Feature, not yet authored |
| The Kubernetes/Helm deployment path | `deploy/charts/buzz/README.md` — a different corpus node's subject |
| The architecture-level "why" of the topology, network and persistence boundaries | `architecture-deployment-docker-compose` |
| Provisioning or hardening the underlying host/VM | `launchpad/deploy/runbooks/dev-deployment-SOP.md` (cohort-internal, broader scope) |
| Managing relay membership day-to-day (`add-member`/`remove-member`/`list-members`) | `deploy/compose/run.sh`'s own `help` output; not exercised as part of this deployment procedure |
| The `benchmarks/harbor-buzz-orchestra` benchmark stack that reuses this same Compose file under a third project name | `benchmarks/harbor-buzz-orchestra/scripts/benchmark.py`, not read for this node |

**Expected but not verified when this node was written:**

- **No `docker compose up` was actually run against the full stack.** This
  node's `check`/`config` steps, and the guard's accept/reject branches, were
  executed for real against a non-secret placeholder `.env` (recorded in the
  evidence ledger above); starting Postgres, Redis, MinIO and a real relay
  image end-to-end, and confirming `/_liveness` actually returns healthy, was
  not exercised in the environment this node was authored in.
- **`deploy/compose/run.sh`'s `add-member`, `remove-member` and `list-members`
  commands were read from the script's case statement, not exercised against a
  running stack.**
- **No bootstrap script exists to generate `.env` automatically**, despite
  `deploy/compose/README.md`'s forward-looking mention of one — confirmed
  absent by search, not merely unmentioned elsewhere.
- **Whether the desktop or mobile apps connect through this Compose stack
  directly, or exclusively through the relay's own published port**, was not
  checked in this pass; `architecture-deployment-docker-compose` names the same
  gap.
