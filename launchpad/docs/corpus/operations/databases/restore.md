---
id: operations-databases-restore
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
  - statement: "deploy/compose/run.sh's command dispatch defines exactly start, stop, restart, pull, upgrade, logs, status, config, backup-hint, add-member, remove-member, and list-members; none of them is a restore command, and backup_hint() only prints a checklist of what to back up."
    entry_class: FACT
    evidence:
      - "deploy/compose/run.sh"
  - statement: "The Justfile defines no recipe named or described as backup, restore, dump, or snapshot anywhere in the file."
    entry_class: FACT
    evidence:
      - "Justfile"
  - statement: "scripts/dev-reset.sh tears the local stack down with `docker compose down -v --remove-orphans` (destroying the postgres, redis, and minio volumes), states outright that Redis data is ephemeral and always wiped on restart, and then execs scripts/dev-setup.sh to recreate an empty environment; it restores no prior data because none is kept."
    entry_class: FACT
    evidence:
      - "scripts/dev-reset.sh"
  - statement: "scripts/dev-setup.sh brings a freshly emptied Postgres to a working schema by running `cargo run -p buzz-admin -- migrate` and then scripts/seed-local-community.sh; it performs no restoration of previously backed-up data."
    entry_class: FACT
    evidence:
      - "scripts/dev-setup.sh"
  - statement: "crates/buzz-db/src/runtime/migration.rs declares a static sqlx::migrate! Migrator sourced from the migrations/ directory; crates/buzz-db/src/runtime/mod.rs exposes an async migrate() method that runs it; crates/buzz-admin/src/main.rs's Command::Migrate arm calls db.migrate().await, which is what `buzz-admin migrate` and scripts/dev-setup.sh's `cargo run -p buzz-admin -- migrate` invoke."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/runtime/migration.rs"
      - "crates/buzz-db/src/runtime/mod.rs"
      - "crates/buzz-admin/src/main.rs"
  - statement: "schema/schema.sql's own header describes itself as the source of truth for fresh database setup, a clean from-scratch declarative schema distinct from the incremental migrations/ directory that sqlx applies at runtime."
    entry_class: FACT
    evidence:
      - "schema/schema.sql"
  - statement: ".github/workflows/ci.yml applies schema/schema.sql with `./bin/pgschema apply --file schema/schema.sql --auto-approve` and immediately follows it with `psql ... < scripts/reconcile-schema-after-pgschema.sql`; the identical two-command sequence recurs in scripts/start-isolated-test-relay.sh, scripts/run-desktop-release-smoke.sh, and scripts/start-relay-for-tests.sh."
    entry_class: FACT
    evidence:
      - ".github/workflows/ci.yml"
      - "scripts/start-isolated-test-relay.sh"
      - "scripts/run-desktop-release-smoke.sh"
      - "scripts/start-relay-for-tests.sh"
  - statement: "AGENTS.md's own gotcha 7 states that `./bin/pgschema apply` does not execute INSERT statements or preserve every table storage parameter from schema/schema.sql, so every pgschema apply caller must also run scripts/reconcile-schema-after-pgschema.sql; this is a schema-desired-state bootstrap path for fresh installs and tests, not a data-restore path — it converges an empty database to the current schema shape and carries no data of its own."
    entry_class: FACT
    evidence:
      - "AGENTS.md"
      - "scripts/reconcile-schema-after-pgschema.sql"
  - statement: "The root docker-compose.yml (local development) declares named volumes postgres-data, minio-data, and prometheus-data, and declares no volume at all for the redis service."
    entry_class: FACT
    evidence:
      - "docker-compose.yml"
  - statement: "deploy/compose/compose.yml (the production single-node bundle) declares four named volumes that persist state across a container restart — buzz-postgres-data, buzz-redis-data, buzz-minio-data, and buzz-git-data — and starts its redis service with `--appendonly yes`."
    entry_class: FACT
    evidence:
      - "deploy/compose/compose.yml"
  - statement: "deploy/compose/compose.caddy.yml adds buzz-caddy-data and buzz-caddy-config named volumes and resets the relay service's port mapping to empty when the TLS profile (BUZZ_COMPOSE_TLS=true) is layered in."
    entry_class: FACT
    evidence:
      - "deploy/compose/compose.caddy.yml"
  - statement: "deploy/compose/run.sh's backup_hint() function names, as things to back up before upgrades and on a schedule: deploy/compose/.env (especially BUZZ_RELAY_PRIVATE_KEY, the DB/Redis/S3 secrets, and BUZZ_GIT_HOOK_HMAC_SECRET), the owner private key held outside the stack, Postgres data (pg_dump or a quiesced volume snapshot), MinIO/S3 bucket contents for media and git objects, the buzz-git-data volume, and the Caddy data/config volumes when TLS is used — with the instruction to keep the Postgres and object/git snapshots from the same maintenance window. It names no Redis artifact anywhere in that list."
    entry_class: FACT
    evidence:
      - "deploy/compose/run.sh"
  - statement: "deploy/compose/.env.example groups BUZZ_RELAY_PRIVATE_KEY, BUZZ_GIT_HOOK_HMAC_SECRET, POSTGRES_PASSWORD, REDIS_PASSWORD, BUZZ_S3_ACCESS_KEY, BUZZ_S3_SECRET_KEY, and RELAY_OWNER_PUBKEY under a comment reading 'Stable secrets. Generate once, keep in .env, and back up securely,' templated with CHANGE_ME placeholders that deploy/compose/run.sh's require_env check refuses to start against."
    entry_class: FACT
    evidence:
      - "deploy/compose/.env.example"
  - statement: "The root .env.example describes BUZZ_RELAY_PRIVATE_KEY as the relay's 'Stable relay signing key (required)' and instructs the reader to preserve that value across restarts and backups; scripts/ensure-local-relay-key.sh only ever generates a fresh random key when BUZZ_RELAY_PRIVATE_KEY is absent or empty in the target env file, and contains no path that recovers a previously lost key."
    entry_class: FACT
    evidence:
      - ".env.example"
      - "scripts/ensure-local-relay-key.sh"
  - statement: "Because BUZZ_RELAY_PRIVATE_KEY is described as the relay's signing key and asymmetric key derivation is deterministic (the relay's public identity is a function of this private key), and no tool in this repository recovers a lost value for it, losing this key without a separate operator-held backup permanently changes which Nostr identity the relay signs as — the repository provides regeneration, never recovery, of this specific value."
    entry_class: INFERENCE
    evidence:
      - ".env.example"
      - "scripts/ensure-local-relay-key.sh"
    confidence: 0.8
  - statement: "crates/buzz-db/src/store/git_repo.rs's module documentation states the relay holds no persistent per-repo filesystem state: git reads and writes hydrate an ephemeral bare repository from object storage per request, and writer serialization is the object-store manifest-pointer compare-and-swap described in docs/git-on-object-storage.md."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/git_repo.rs"
      - "docs/git-on-object-storage.md"
  - statement: "docs/git-on-object-storage.md states 'object storage remains the source of truth' for git repository content, describes the per-process pack/index cache as something whose 'cache misses, restarts, and evictions only affect performance,' and its Implementation Correspondence table names the concrete source files implementing the protocol; hydrate_for_read and hydrate_for_write are defined in crates/buzz-relay/src/api/git/hydrate.rs, cas_publish in cas_publish.rs, finalize_push in transport.rs, and run_conformance_probe in store.rs, confirming the design document describes code that exists rather than a proposal."
    entry_class: FACT
    evidence:
      - "docs/git-on-object-storage.md"
      - "crates/buzz-relay/src/api/git/hydrate.rs"
      - "crates/buzz-relay/src/api/git/cas_publish.rs"
      - "crates/buzz-relay/src/api/git/transport.rs"
      - "crates/buzz-relay/src/api/git/store.rs"
  - statement: "crates/buzz-relay/src/config.rs resolves BUZZ_GIT_REPO_PATH (default ./repos) and BUZZ_GIT_PACK_CACHE_PATH by creating the directories if they do not already exist, rather than requiring pre-existing content; the root .env.example describes that same path as the 'Root directory for ephemeral Git workspaces and the disposable pack cache.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/config.rs"
      - ".env.example"
  - statement: "docs/git-on-object-storage.md's axiom A1 states pack and manifest objects are written create-only and are never deleted by the protocol, so a reader holding an older manifest digest can always retrieve every pack it names; crates/buzz-media/src/storage.rs, in contrast, defines delete, delete_objects, and delete_object_versions methods, so media blobs in the same object-storage bucket are not subject to the same no-deletion discipline."
    entry_class: FACT
    evidence:
      - "docs/git-on-object-storage.md"
      - "crates/buzz-media/src/storage.rs"
  - statement: "Because git content addressed under the CAS protocol is never deleted in the ordinary course of operation while media objects can be explicitly deleted, restoring an object-storage snapshot taken at a different moment than the paired Postgres snapshot creates an asymmetric risk: a Postgres row naming a media key can dangle if the object-storage snapshot is older or if that media was legitimately deleted in the interval, whereas a Postgres row naming a git manifest or pack is at less risk of dangling purely from snapshot-timing skew, absent an actual deletion path for git objects, which this repository's evidence does not show existing."
    entry_class: INFERENCE
    evidence:
      - "docs/git-on-object-storage.md"
      - "crates/buzz-media/src/storage.rs"
    confidence: 0.7
  - statement: "The single-relay architecture node documents that deploy/compose/README.md treats an image-only rollback as safe only when the intervening database migrations were backward-compatible, and otherwise requires the operator to restore the matching pre-upgrade database and object/git snapshots together as one coordinated recovery, which is this repository's own statement of the ordering hazard between stores rather than a conclusion reached independently in this node."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/deployment/single-relay.md"
  - statement: "migrations/0029_community_deletion.sql and migrations/0030_community_deletion_recovery.sql implement a durable, CLI-only, staged whole-community deletion control plane with lease/fence/checkpoint guards and a terminal recovery path for requests that have not yet begun irreversible object deletion; this is an application-level undo for an in-progress deletion workflow, not an infrastructure-level restore of a lost or corrupted store, and is a different concept from this node's subject."
    entry_class: FACT
    evidence:
      - "migrations/0029_community_deletion.sql"
      - "migrations/0030_community_deletion_recovery.sql"
  - statement: "crates/buzz-pubsub/src/lib.rs's module documentation scopes the crate to Redis pub/sub fan-out, presence tracking, and typing indicators, and its non-error submodules are exactly cache_invalidation, conn_control, nip98_replay, presence, publisher, rate_limiter, subscriber, and topic — connection control, cache-invalidation broadcast, NIP-98 replay-nonce tracking, presence, publishing, subscribing, rate limiting, and topic naming."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/lib.rs"
      - "crates/buzz-pubsub/src/presence.rs"
      - "crates/buzz-pubsub/src/rate_limiter.rs"
      - "crates/buzz-pubsub/src/nip98_replay.rs"
      - "crates/buzz-pubsub/src/cache_invalidation.rs"
      - "crates/buzz-pubsub/src/conn_control.rs"
      - "crates/buzz-pubsub/src/publisher.rs"
      - "crates/buzz-pubsub/src/subscriber.rs"
      - "crates/buzz-pubsub/src/topic.rs"
  - statement: "deploy/compose/compose.yml's redis service runs with --appendonly yes against the buzz-redis-data volume, so production Redis content survives a container restart, while deploy/compose/run.sh's backup checklist names Postgres, the object-storage bucket, and the buzz-git-data volume but never Redis."
    entry_class: FACT
    evidence:
      - "deploy/compose/compose.yml"
      - "deploy/compose/run.sh"
  - statement: "Because every module buzz-pubsub exposes is fan-out, presence, rate-limiting, or short-lived replay-nonce state rather than a store this repository's own backup checklist names, and no evidence gathered while writing this node shows a Redis-only durable record with no Postgres or object-storage counterpart, Redis's AOF persistence in the production profile reads as a restart-continuity optimization rather than a backup requirement — this was checked against the modules buzz-pubsub exposes, not against every key the relay process writes to Redis."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-pubsub/src/lib.rs"
      - "deploy/compose/run.sh"
    confidence: 0.6
  - statement: "Issue launchpad-26/buzz#1197 is the sibling task documenting operations/databases/backup.md, and issue launchpad-26/buzz#1216 is the sibling task documenting operations/reliability/disaster-recovery.md, both dispatched alongside this task from parent Feature #618; neither corpus node exists on origin/launchpad at the recorded revision, so this node names them in prose rather than declaring a relationships edge to either."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1197 and launchpad-26/buzz#1216 issue titles, and the Feature #618 batch dispatch brief for this task set"
  - statement: "This node was written using launchpad/docs/corpus/templates/reference.md, which was already merged on origin/launchpad at the recorded revision and directs a Reference description, structured entries ordered to match the reference material's own order, an optional Commands section, a Boundary statement, a Relationships section, and a Scope and omissions section carrying both what the node does not cover and what was expected but could not be verified."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/templates/reference.md"
relationships:
  - type: references
    target: architecture-deployment-single-relay
  - type: references
    target: architecture-containers-postgres
  - type: references
    target: architecture-containers-redis
  - type: references
    target: architecture-containers-object-storage
---

# Restoring persistent state: reference

What a restore of this system's persistent state has to put back, in what order,
and with what tooling — the counterpart to backing that state up
([#1197](https://github.com/launchpad-26/buzz/issues/1197)) and to recovering a
whole lost site
([#1216](https://github.com/launchpad-26/buzz/issues/1216)). This node catalogues
each store this repository persists, what "restored" means for it, and which
restore step this repository actually automates versus which it leaves entirely
to the operator. It assumes a backup already exists; it does not tell you how to
take one.

## What has to come back

Ordered by restore dependency — later rows depend on earlier ones being in
place first, not by where each store appears in a compose file.

| Store | What "restored" means | Tooling this repository provides | What it does not provide |
|---|---|---|---|
| Relay signing key and `deploy/compose/.env` secrets (`BUZZ_RELAY_PRIVATE_KEY`, `BUZZ_GIT_HOOK_HMAC_SECRET`, `POSTGRES_PASSWORD`, `REDIS_PASSWORD`, `BUZZ_S3_ACCESS_KEY`, `BUZZ_S3_SECRET_KEY`, `RELAY_OWNER_PUBKEY`) | The exact `.env` values from before the loss, especially the relay's own signing key | `scripts/ensure-local-relay-key.sh` fills in a **new** key only when one is absent; `deploy/compose/run.sh`'s `require_env` refuses to start with a `CHANGE_ME` placeholder | Any recovery of a lost key. If `BUZZ_RELAY_PRIVATE_KEY` is gone with no operator-held copy, the relay comes back as a different Nostr identity |
| Object storage — media and git CAS (one S3-compatible bucket, `BUZZ_S3_BUCKET`) | The pack, manifest, and media objects the bucket held | None. No script in this repository writes to or reads from a second bucket, and no `just` recipe or `run.sh` command restores bucket contents | Any restore command. `deploy/compose/run.sh backup-hint` only names "MinIO/S3 bucket contents" as something to back up; nothing restores them |
| Postgres — schema shape | A schema matching what the relay binary expects | `buzz-admin migrate` (the embedded `sqlx` migrator over `migrations/`) for restoring into an already-correct-version relay; `./bin/pgschema apply --file schema/schema.sql` plus `scripts/reconcile-schema-after-pgschema.sql` for converging an **empty** database to the declarative shape in `schema/schema.sql` | Neither path loads data. `pgschema apply` explicitly skips `INSERT` statements (see `AGENTS.md` gotcha 7); a genuine restore of a Postgres backup (`pg_restore`, or bringing back a snapshotted data directory) is not represented anywhere in this repository |
| Postgres — event/roster/community data | The rows themselves | None. This repository names `pg_dump` and "a quiesced volume snapshot" as *backup* techniques in `deploy/compose/run.sh backup_hint()`; it ships no corresponding `pg_restore` invocation, no volume-restore script, and no `just` recipe that loads a dump |
| `buzz-git-data` volume (`/data/git` in production) | The relay's ephemeral git working trees and its disposable pack/index cache | `crates/buzz-relay/src/config.rs` recreates both directories on demand if missing — no restore step is needed for correctness | Nothing to restore *from*, because there is nothing authoritative to lose here — see *Boundary* |
| Redis | Presence, typing, rate-limit, and NIP-98 replay-nonce state | Redis is started fresh by `docker compose up` in every profile; production additionally persists it via `--appendonly yes` against `buzz-redis-data` | No restore tooling, and the repository's own backup checklist never lists Redis as something to back up in the first place |

## Commands

The only commands this repository actually ships for bringing a store's
*schema* into shape. None of them is framed by the repository as a restore
command, and none loads data.

| Command | What it does | Where it is used |
|---|---|---|
| `./bin/pgschema apply --file schema/schema.sql --auto-approve` | Converges an empty database's schema to `schema/schema.sql`'s declarative shape. Skips `INSERT` statements and some storage parameters | `.github/workflows/ci.yml`, `scripts/start-isolated-test-relay.sh`, `scripts/run-desktop-release-smoke.sh`, `scripts/start-relay-for-tests.sh` |
| `psql ... -v ON_ERROR_STOP=1 < scripts/reconcile-schema-after-pgschema.sql` | Applies the convergence statements `pgschema apply` cannot express, immediately after it | Same four call sites, always paired with the command above |
| `cargo run -p buzz-admin -- migrate` (equivalently, the installed `buzz-admin migrate`) | Runs the embedded `sqlx` migrator over `migrations/` against whatever Postgres it is pointed at | `scripts/dev-setup.sh`; production relies on `BUZZ_AUTO_MIGRATE` running the same migrator at relay startup instead |
| `docker compose down -v --remove-orphans` followed by `scripts/dev-setup.sh` (what `scripts/dev-reset.sh` runs) | Destroys and recreates the local dev stack's volumes, then re-runs schema convergence and seeding | Local development only. This is a wipe-and-recreate path, not a restore — no prior data survives it |

## Boundary

This node does not describe:

- **How to take a backup**, or how often — that is
  [#1197](https://github.com/launchpad-26/buzz/issues/1197)'s subject. This node
  assumes a backup artifact already exists and describes what putting it back
  requires.
- **Recovering the whole site** when the host itself, not just one store, is
  lost — standing up a fresh host, DNS, and TLS material alongside the stores
  below is [#1216](https://github.com/launchpad-26/buzz/issues/1216)'s subject.
  This node's per-store table is a component of that larger procedure, not a
  substitute for it.
- **The in-app community-deletion recovery path** (`migrations/0029_community_deletion.sql`,
  `migrations/0030_community_deletion_recovery.sql`). That is a resumable,
  operator-driven *undo* for a deletion workflow already in progress inside a
  live, otherwise-intact relay — a different concept from putting a lost store
  back from an external backup, even though both use the word "recovery."

## Relationships

- **references** `architecture-deployment-single-relay` — this node's per-store
  table is read directly against that node's documented volumes, secrets, and
  its own "Backup and rollback" section; that node names the same backup
  checklist this node treats as the restore side of the same coin.
- **references** `architecture-containers-postgres` — for what Postgres is
  responsible for and which crate owns its connections, which this node does
  not re-derive.
- **references** `architecture-containers-redis` — for what Redis is for and
  which crate/module owns each use, which this node's Redis row summarizes
  only as far as restore requires.
- **references** `architecture-containers-object-storage` — for the ownership
  boundary between `buzz-media` and the git-storage code path, which this
  node's object-storage row depends on without restating.

`references`' directionality is "source cites target as supporting context; no
ownership or currency dependency implied" — none of these four nodes changes
this node's own claims, and this node changes none of theirs.

## Scope and omissions

**This node covers** what has to come back to restore this system's persistent
state — Postgres schema and data, the object-storage bucket backing media and
git CAS, the `buzz-git-data` working volume, Redis, and the relay's signing
key and other `deploy/compose/.env` secrets — the dependency order between
them, what tooling this repository provides for each, and the consistency
hazard between a Postgres snapshot and an object-storage snapshot taken at
different times.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| How to take a backup of any of these stores | [#1197](https://github.com/launchpad-26/buzz/issues/1197) |
| Recovering a whole lost site, including the host, DNS, and TLS material | [#1216](https://github.com/launchpad-26/buzz/issues/1216) |
| What Postgres, Redis, and object storage are each responsible for in Buzz's architecture | `architecture-containers-postgres`, `architecture-containers-redis`, `architecture-containers-object-storage` |
| The production Compose topology, its volumes, and its own backup checklist in full | `architecture-deployment-single-relay` |
| The Kubernetes/Helm deployment's own restore posture | Not documented anywhere in this repository at the recorded revision, per `architecture-deployment-single-relay`'s own scope |

**Expected but not verified when this node was written:**

- **No live restore was actually performed.** Every row in *What has to come
  back* is derived from reading the scripts, Compose files, and code that
  exist, not from rehearsing a restore against a real backup artifact. This
  repository has no backup to restore from in this environment, and producing
  one is out of this task's scope.
- **Every Redis key the relay process writes was not enumerated.** The
  INFERENCE that Redis holds no durable-only application data rests on what
  `buzz-pubsub`'s modules expose and on the backup checklist's own omission of
  Redis, not on an exhaustive audit of every `SET`/`ZADD` call in the relay
  binary.
- **The Helm chart's (`deploy/charts/buzz`) restore posture was not checked.**
  `architecture-deployment-single-relay` documents that chart's non-HA default
  and its migration mechanism, but this node's evidence gathering did not
  extend to whether its values or runbooks say anything about restoring a
  lost Kubernetes-hosted deployment.
- **Docker Compose's own default `stop_grace_period`** was not independently
  checked here either — `architecture-deployment-single-relay` already names
  this same gap for its own subject, and a restore that involves recreating
  containers inherits it unchanged.
