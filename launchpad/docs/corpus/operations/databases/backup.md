---
id: operations-databases-backup
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
  - statement: "buzz-db's crate-level doc comment describes it as \"Postgres event store for Buzz\", the crate that owns connection pooling, migrations, and every typed data-access module; Postgres is therefore the durable system of record this reference treats as the primary backup target."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/lib.rs"
  - statement: "The root docker-compose.yml (local development) mounts a named postgres-data volume for the postgres service and a named minio-data volume for the minio service, but declares no volumes: entry at all for the redis service, so a local-dev Redis container has no state that survives a restart."
    entry_class: FACT
    evidence:
      - "docker-compose.yml"
  - statement: "deploy/compose/compose.yml (the single-node production bundle) mounts four named volumes: buzz-postgres-data for postgres, buzz-redis-data for redis (started with --appendonly yes so its AOF file persists across restarts), buzz-minio-data for the bundled MinIO object store, and buzz-git-data mounted into the relay container at /data/git (the path BUZZ_GIT_REPO_PATH is set to in that same service definition)."
    entry_class: FACT
    evidence:
      - "deploy/compose/compose.yml"
  - statement: "deploy/compose/compose.caddy.yml, layered in only when BUZZ_COMPOSE_TLS=true, adds a caddy service with two further named volumes, buzz-caddy-data and buzz-caddy-config, holding Caddy's issued TLS certificates and ACME account state."
    entry_class: FACT
    evidence:
      - "deploy/compose/compose.caddy.yml"
  - statement: ".env.example documents BUZZ_GIT_REPO_PATH's own purpose as \"Root directory for ephemeral Git workspaces and the disposable pack cache\", calling the directory disposable in the same sentence that introduces it."
    entry_class: FACT
    evidence:
      - ".env.example"
  - statement: "docs/git-on-object-storage.md states the relay's git implementation \"has no authoritative per-repo filesystem state\": every request hydrates an ephemeral working tree from the published manifest, runs the relevant git subprocess against it, and drops the tree on scope exit, with \"object storage remains the source of truth\" stated explicitly; a per-pod cache of immutable pack/index pairs may be retained, but \"cache misses, restarts, and evictions only affect performance.\""
    entry_class: FACT
    evidence:
      - "docs/git-on-object-storage.md"
  - statement: "deploy/charts/buzz/values.yaml's own comment on the chart's git persistence option states plainly: \"Ephemeral working space only. No persistent git state lives here\" and that a per-pod emptyDir (no PVC at all) is \"the correct choice for multi-replica HA\" because it is \"[s]afe because the object store + Postgres are the sources of truth, not this disk.\""
    entry_class: FACT
    evidence:
      - "deploy/charts/buzz/values.yaml"
  - statement: "deploy/compose/run.sh defines a backup_hint shell function whose entire body is a cat heredoc printing a checklist: deploy/compose/.env (naming BUZZ_RELAY_PRIVATE_KEY, DB/Redis/S3 secrets, and BUZZ_GIT_HOOK_HMAC_SECRET specifically), the owner private key if bootstrap generated one, Postgres data (\"prefer pg_dump or a quiesced volume snapshot\"), MinIO/S3 bucket contents, the buzz-git-data volume, and the Caddy data/config volumes when compose.caddy.yml is used -- closing with the instruction to keep Postgres and object/git state snapshots from the same maintenance window."
    entry_class: FACT
    evidence:
      - "deploy/compose/run.sh"
  - statement: "In deploy/compose/run.sh's case statement, backup_hint is invoked by the backup-hint subcommand and once more automatically at the end of upgrade; no other branch in this 133-line script invokes pg_dump, an S3/mc copy command, a docker volume snapshot, or any other command that actually copies data -- every other subcommand's body is a docker compose invocation, a docker compose exec into the running relay for buzz-admin membership commands, or a bare cat of help text."
    entry_class: FACT
    evidence:
      - "deploy/compose/run.sh"
  - statement: "deploy/compose/README.md tells an operator performing an image-only rollback to \"restore the matching pre-upgrade database and object/git snapshots as a coordinated recovery\" when intervening migrations are not backward-compatible, and separately directs a reader to run ./launchpad/deploy/run.sh backup-hint \"for the backup checklist\" -- naming both actions without naming any tool in this repository that performs either restore or that the checklist's own commands could be scripted against."
    entry_class: FACT
    evidence:
      - "deploy/compose/README.md"
  - statement: "launchpad/deploy/run.sh sets CANONICAL_RUNNER to deploy/compose/run.sh and its final line execs that script with every argument forwarded unchanged, so backup-hint (and every other subcommand) is delegated verbatim; nothing in launchpad/deploy/run.sh's own 130 lines mentions backup, and its own README describes it as a Launchpad image/Compose preflight guard that \"delegates to the canonical deploy/compose/run.sh implementation\", not a second implementation."
    entry_class: FACT
    evidence:
      - "launchpad/deploy/run.sh"
      - "launchpad/deploy/README.md"
  - statement: "deploy/charts/buzz/templates/NOTES.txt (the text helm install/helm upgrade prints) contains a \"Backups -- save these\" block listing exactly five items: BUZZ_RELAY_PRIVATE_KEY, the PostgreSQL database (naming the release's own -postgresql PVC when the bundled subchart is enabled), the S3 bucket holding media blobs, the chart's own git PVC (\"repo on-disk state\"), and the owner private key, which the same line states is \"held by the operator, NOT the chart\" and restored by reinstalling with the same ownerPubkey."
    entry_class: FACT
    evidence:
      - "deploy/charts/buzz/templates/NOTES.txt"
  - statement: "deploy/charts/buzz/README.md carries a top-level \"## Backups\" section stating \"Save these. Losing any of them is data loss\", pointing to NOTES.txt for \"the live list\", and then repeating the same five items -- BUZZ_RELAY_PRIVATE_KEY, the PostgreSQL database, the S3 bucket (default name buzz-media), the git PVC (\"repo on-disk state served by the relay's git endpoint\"), and the owner private key held outside the chart."
    entry_class: FACT
    evidence:
      - "deploy/charts/buzz/README.md"
  - statement: "At the recorded revision, deploy/charts/buzz/templates/ contains seventeen files -- secret-chart.yaml, hpa.yaml, pdb.yaml, httproute.yaml, NOTES.txt, service.yaml, deployment.yaml, quickstart-minio-init.yaml, pvc-git.yaml, _validate.tpl, extramanifests.yaml, quickstart-minio.yaml, _helpers.tpl, ingress.yaml, serviceaccount.yaml, pairing-relay.yaml, and servicemonitor.yaml. Exactly one renders a batch workload -- quickstart-minio-init.yaml, a kind: Job that creates the quickstart MinIO bucket -- and it is a one-shot install-time bucket bootstrap, not a scheduled backup: no template in the chart is a CronJob, and none runs a pg_dump or an object-store sync on a schedule."
    entry_class: FACT
    evidence:
      - "deploy/charts/buzz/templates/quickstart-minio-init.yaml"
      - "deploy/charts/buzz/values.yaml"
  - statement: "deploy/charts/buzz/values.yaml's persistence-related keys for the bundled subcharts are capacity/storage-class settings only -- persistence.git.enabled/size (10Gi), postgresql.persistence.enabled/size (10Gi), redis.persistence.enabled/size (4Gi), and minio.persistence.enabled/size (10Gi) -- and no key anywhere in the file configures a backup schedule, a retention window, or a snapshot destination."
    entry_class: FACT
    evidence:
      - "deploy/charts/buzz/values.yaml"
  - statement: "deploy/charts/buzz/values.yaml separately defines externalPostgresql.url and externalRedis.url so a production release can point the relay at an externally managed Postgres or Redis instance instead of enabling the bundled CloudPirates subcharts, taking that data store's persistence and backup entirely outside anything this chart provisions."
    entry_class: FACT
    evidence:
      - "deploy/charts/buzz/values.yaml"
  - statement: "launchpad/deploy/runbooks/hardening-spec.md's own header states its status as \"specification only. Nothing here is implemented\", and its \"Part E -- Backup and recovery\" section states plainly that \"run.sh backup-hint prints a correct checklist and automates nothing\", proposing to \"[t]urn it into a role\" and naming four properties -- Object Lock immutability, write/delete credential separation, keys stored separately from backups, and a timed restore drill producing a measured RPO/RTO -- of which it states \"none is in backup-hint.\""
    entry_class: FACT
    evidence:
      - "launchpad/deploy/runbooks/hardening-spec.md"
  - statement: "launchpad/deploy/AGENTS.md states a mandatory rule that nothing under launchpad/deploy/archived/ -- which includes an Ansible role variable named buzz_backup_target -- may be used, run, copied, repaired, extended, or recommended to build or deploy Buzz, describing the archive as historical reference for a deployment method that failed, not a supported option."
    entry_class: FACT
    evidence:
      - "launchpad/deploy/AGENTS.md"
  - statement: "crates/buzz-pubsub/src/lib.rs's own top-of-file doc comment describes the crate as \"Redis pub/sub fan-out, presence tracking, and typing indicators\", and its architecture diagram shows the relay opening a pooled connection for commands (PUBLISH, SET, ZADD) and a separate, dedicated (non-pooled) connection for SUBSCRIBE/PSUBSCRIBE."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/lib.rs"
  - statement: "presence.rs's own doc comment states presence is \"Stored as SET buzz:{community}:presence:{pubkey_hex} \\\"online\\\" EX 180\"\", and its PRESENCE_TTL_SECS constant is 180 -- every presence key the crate writes carries a fixed 180-second expiry."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/presence.rs"
  - statement: "nip98_replay.rs's own doc comments describe its Redis write as \"SET buzz:{community}:nip98:{event_id_hex} 1 NX EX <ttl>\", an atomic set-if-absent-with-expiry operation, so every replay-guard key the crate writes also carries an expiry."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/nip98_replay.rs"
  - statement: "rate_limiter.rs's own doc comment states it uses \"a single Lua script to atomically INCR and conditionally EXPIRE\" a rate-limit counter key, so a counter key this crate writes either already carries an expiry or is assigned one in the same atomic script call that creates it."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/rate_limiter.rs"
  - statement: "cache_invalidation.rs and conn_control.rs's own module doc comments describe both as carrying transient PUBLISH messages -- a \"pure cache-key drop\" in the first case and a \"disconnect this pubkey\" connection-control intent in the second -- to every relay pod over Redis pub/sub, with nothing written to a Redis key by either module."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/cache_invalidation.rs"
      - "crates/buzz-pubsub/src/conn_control.rs"
  - statement: "Across the five buzz-pubsub modules opened for this node (presence, nip98_replay, rate_limiter, cache_invalidation, conn_control), every Redis write is either a key created with an expiry or a transient pub/sub PUBLISH with nothing stored at all, so Redis holds no state that a backup would need to preserve across a restore -- restoring Postgres, the object store, and the relay's keys is sufficient to reconstruct everything Redis would otherwise have held, because every Redis-resident fact is either regenerated by relay activity or was disposable by construction."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-pubsub/src/lib.rs"
      - "crates/buzz-pubsub/src/presence.rs"
      - "crates/buzz-pubsub/src/nip98_replay.rs"
      - "crates/buzz-pubsub/src/rate_limiter.rs"
      - "crates/buzz-pubsub/src/cache_invalidation.rs"
      - "crates/buzz-pubsub/src/conn_control.rs"
    confidence: 0.85
  - statement: "Two backup checklists in this repository (deploy/compose/run.sh's backup_hint and deploy/charts/buzz's NOTES.txt/README.md) both name a git volume/PVC as something to back up, while docs/git-on-object-storage.md and the chart's own values.yaml comment both state the git volume/PVC is a disposable cache and that object storage plus Postgres are the actual sources of truth for git state; this node records both without resolving which one an operator should follow, per AGENTS.md's convention of flagging rather than silently correcting a discrepancy found across this repository's own documents."
    entry_class: FACT
    evidence:
      - "deploy/compose/run.sh"
      - "deploy/charts/buzz/templates/NOTES.txt"
      - "docs/git-on-object-storage.md"
      - "deploy/charts/buzz/values.yaml"
  - statement: "AGENTS.md documents that squareup/block-coder-tf-stacks (Terraform + ArgoCD) deploys the relay's Helm chart to the staging Kubernetes cluster and that squareup/sprout-oss builds the relay's Docker image for internal use, without stating whether either pipeline additionally provisions or automates backups for a managed Postgres, Redis, or S3 instance; both are private repositories not present in this checkout, so this node cannot verify what, if anything, they automate."
    entry_class: FACT
    evidence:
      - "AGENTS.md"
  - statement: "Issue #1197's definition of done requires this node to be structured for lookup rather than narrative teaching, to contain only facts supported by current source with generated values labelled as such, to define its scope and omissions, and to link authoritative source/schema/config -- the acceptance bar this node is built against."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1197 definition of done"
  - statement: "This node was written using launchpad/docs/corpus/templates/reference.md, which was already merged on origin/launchpad at the recorded revision and directs a reference-shaped node to carry a reference description, structured entries, an optional commands table, an explicit boundary statement against the concept/explanation and how-to/procedure forms, relationships, and a scope-and-omissions section separating what the node excludes from what it could not verify."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/templates/reference.md"
relationships:
  - type: references
    target: architecture-containers-postgres
  - type: references
    target: architecture-containers-redis
  - type: references
    target: architecture-deployment-docker-compose
  - type: references
    target: architecture-deployment-kubernetes
---

# Database and object-storage backup: reference

What backing up this system's persistent state actually consists of in this
repository today: which stores hold durable state, what this repository ships to
back them up, and what it does not ship. This is a reference for an operator
deciding what to snapshot and when — it catalogues the checklist this repository
already prints, and is linked from the restore procedure (a sibling task, not yet
written) rather than duplicating it.

## Which stores hold durable state

| Store | Durable? | What backs it | Where |
|---|---|---|---|
| Postgres | Yes — the system of record | `buzz-db`'s connection pool and embedded migrations, against a real Postgres instance | Named volume `postgres-data` (dev) / `buzz-postgres-data` (compose prod) / the chart's `-postgresql` PVC or an `externalPostgresql.url` instance |
| Object storage (media + git) | Yes | An S3-compatible bucket, reached through `buzz-media` (media blobs) and `buzz-relay`'s independent `api::git::store` client (git packs/manifests) — both content-addressed and both writing to the same configured bucket | Named volume `minio-data`/`buzz-minio-data` (bundled MinIO) or an externally managed S3-compatible service |
| Relay private key (`BUZZ_RELAY_PRIVATE_KEY`) | Yes — identity | An environment variable read at process start; no separate keystore file | `deploy/compose/.env`, or the chart's Secret |
| Owner private key | Yes — the administrator's login | Generated once at bootstrap if `RELAY_OWNER_PUBKEY` was not supplied, then held by the operator | Outside the stack entirely — neither the Compose bundle nor the chart stores it |
| `.env` / chart Secret (DB, Redis, S3 credentials; `BUZZ_GIT_HOOK_HMAC_SECRET`) | Yes — secrets, not data | Plain environment configuration | `deploy/compose/.env`, or the chart's `secrets.existingSecret` |
| Git working-tree volume/PVC (`BUZZ_GIT_REPO_PATH`, `buzz-git-data`, the chart's git PVC) | **No — by design, but see the discrepancy noted below** | An ephemeral hydration cache; the relay reconstructs a working tree from the object-store manifest on every request and discards it afterward | Named volume `buzz-git-data` (compose), or an ephemeral PVC/`emptyDir` (chart) |
| Redis | No | Every key this repository's Redis-using crate (`buzz-pubsub`) writes carries a TTL, or is never written to a key at all (a transient pub/sub `PUBLISH`) | No volume at all in local dev; an AOF-backed volume in the Compose production bundle and a PVC in the chart's bundled subchart, for restart continuity rather than backup |

**The git-volume discrepancy.** `deploy/compose/run.sh`'s `backup_hint` and the
chart's `NOTES.txt`/`README.md` both list the git volume or PVC as something to back
up. `docs/git-on-object-storage.md` and the chart's own `values.yaml` comment both
state the opposite: the relay has "no authoritative per-repo filesystem state," every
request hydrates an ephemeral working tree from the object store and drops it
afterward, and object storage plus Postgres are the actual sources of truth. This
node records both without resolving which an operator should follow — including a
disposable cache in a backup costs nothing but capacity; treating it as skippable
without independently confirming the object-store-backed design is deployed as
documented would be the riskier reading to act on unverified.

**Why Redis is persisted in production despite holding nothing durable.** The
production Compose bundle runs Redis with `--appendonly yes` against a named volume,
and the chart's bundled Redis subchart enables `persistence`. Both give a restarted
Redis its rate-limit counters and presence state back immediately rather than an
empty cache, which is a restart-continuity choice, not evidence that Redis needs to
be included in a backup — nothing in `buzz-pubsub` writes a key without an expiry or
writes a durable key at all.

## What this repository provides for backing it up

**Nothing in this repository automates a backup.** Every artifact this repository
ships for the subject is a checklist that a human reads and acts on manually; none of
it invokes `pg_dump`, copies an object-store bucket, or snapshots a volume by itself.

- **`deploy/compose/run.sh`'s `backup_hint`** prints a fixed checklist naming
  `deploy/compose/.env`, the bootstrap-generated owner key, Postgres data ("prefer
  `pg_dump` or a quiesced volume snapshot"), the MinIO/S3 bucket, the `buzz-git-data`
  volume, and the Caddy data/config volumes, closing with the instruction to keep
  Postgres and object/git snapshots from the same maintenance window. It runs
  automatically once at the end of `upgrade` and on demand via the `backup-hint`
  subcommand. No other subcommand in that script touches backup state.
- **The Helm chart's `NOTES.txt`** (printed by `helm install`/`helm upgrade`) and
  **`README.md`'s `## Backups` section** carry the same shape of list: the relay
  private key, the PostgreSQL database, the S3 bucket, the git PVC, and the owner
  private key held outside the chart. The chart's `templates/` directory has no
  CronJob, Job, or other template that would execute any of it.
- **`launchpad/deploy/run.sh`** is a thin image/environment guard in front of
  `deploy/compose/run.sh` — it forwards `backup-hint` and every other subcommand
  unchanged and implements no backup logic of its own.
- **A proposal exists to change this and has not been built.**
  `launchpad/deploy/runbooks/hardening-spec.md` — itself marked "specification only.
  Nothing here is implemented" — states that `backup_hint` "automates nothing" and
  proposes turning it into an automated role with four properties it says are
  missing today: backup-store immutability (Object Lock), write/delete credential
  separation, keys stored apart from the backups they would recover, and a
  timed restore drill with a measured RPO/RTO. None of the four exists in this
  repository at the recorded revision.
- **A prior, unrelated attempt is explicitly disowned.** `launchpad/deploy/archived/`
  contains an Ansible role variable named `buzz_backup_target`, left over from a
  deployment method `launchpad/deploy/AGENTS.md` states failed and forbids using,
  running, copying, repairing, extending, or recommending for any Buzz deployment.
  It is not a source of working backup automation, archived or otherwise.
- **Managed infrastructure is out of view.** Production Postgres/Redis/S3 can be
  pointed at externally managed instances (`externalPostgresql.url`,
  `externalRedis.url`, or a non-bundled S3 endpoint) instead of the chart's bundled
  subcharts, and `AGENTS.md` names `squareup/block-coder-tf-stacks` and
  `squareup/sprout-oss` as the private pipelines that provision staging/production
  infrastructure. Whether either automates backups for a managed instance is not
  answerable from this repository.

## Commands

| Command | What it does | Where |
|---|---|---|
| `deploy/compose/run.sh backup-hint` | Prints the production backup checklist. Automates nothing. | `deploy/compose/run.sh` |
| `./launchpad/deploy/run.sh backup-hint` | Guard-and-delegate wrapper for the same command, from the repository root. | `launchpad/deploy/run.sh` |
| `deploy/compose/run.sh upgrade` | Pulls the configured image, restarts the relay, then prints `backup_hint` as a reminder — it does not itself back anything up before restarting. | `deploy/compose/run.sh` |
| `helm install` / `helm upgrade` | Prints the chart's `NOTES.txt`, whose "Backups — save these" block is the same kind of checklist. | `deploy/charts/buzz/templates/NOTES.txt` |

## Boundary

This node does not describe:

- **How to actually take or verify a backup** — no `pg_dump` invocation, S3 sync
  command, or volume-snapshot procedure is specified here, because none is specified
  anywhere in this repository at the recorded revision (see above). Writing one is
  the restore/backup-automation task this node's own evidence entries name as absent.
- **How to restore from a backup once taken.** That is a sibling task (issue #1202);
  linking to it directly is not possible because its corpus node does not exist on
  `origin/launchpad` at the recorded revision, per this corpus's rule against linking
  a path this Feature has not yet created.
- **Disaster recovery** — multi-failure scenarios, RTO/RPO targets, and rehearsed
  recovery drills are a separate task (issue #1216).
  `launchpad/deploy/runbooks/hardening-spec.md`'s Part E proposal is named above only
  as evidence that automation does not exist today, not as a specification adopted
  here.
- **Managed-service backup mechanics** — whatever `squareup/block-coder-tf-stacks` or
  `squareup/sprout-oss` may or may not automate for a staging/production managed
  Postgres, Redis, or S3 instance. Those are private repositories this task did not
  and could not open.

## Relationships

- `references`: `architecture-containers-postgres` — the corpus node establishing
  Postgres as the durable system of record this backup catalogue treats as the
  primary target.
- `references`: `architecture-containers-redis` — the corpus node whose own analysis
  of `buzz-pubsub`'s TTL/transient write patterns this node's independent reading of
  the same five source files (see the evidence ledger) corroborates.
- `references`: `architecture-deployment-docker-compose` — the corpus node covering
  the Compose bundle's volumes and `backup_hint`'s printed checklist in its own
  deployment-topology context.
- `references`: `architecture-deployment-kubernetes` — the corpus node covering the
  chart's PVCs and the same backup unrecoverable-loss inventory from `NOTES.txt`, in
  its own deployment-topology context.

## Scope and omissions

**This node covers** which stores in this repository hold durable state and which do
not, what this repository ships today to help an operator back up the durable ones
(two printed checklists and nothing that executes automatically), what a still-open
proposal says is missing from that checklist, and one internal discrepancy this
repository's own documents carry about whether the git volume/PVC needs backing up
at all.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The restore procedure | issue #1202 (not yet a corpus node at the recorded revision) |
| Disaster recovery, RTO/RPO, and drills | issue #1216 |
| Turning `backup_hint` into real automation, and the Object Lock/credential-separation properties `hardening-spec.md` proposes | `launchpad/deploy/runbooks/hardening-spec.md` Part E (specification only, unimplemented) |
| The formal safety argument for git-on-object-storage | `docs/git-on-object-storage.md` |
| Postgres's own connection/pooling/migration contract | `architecture-containers-postgres` |
| Redis's own responsibility, interfaces, and security implications | `architecture-containers-redis` |
| Object storage's own responsibility, interfaces, and security implications | `architecture-containers-object-storage` |
| Whether `squareup/block-coder-tf-stacks` or `squareup/sprout-oss` automate backups for a managed instance | those private repositories, not opened by this task |

**Expected but not verified when this node was written:**

- **Whether the git-volume discrepancy reflects an actually-stale checklist or a
  deliberate belt-and-suspenders inclusion.** Nobody was asked; both readings are
  consistent with the text this node cites, and this node does not choose between
  them.
- **Whether the CloudPirates Postgres and Redis subcharts this chart depends on ship
  any backup mechanism of their own beyond the `persistence.enabled` PVC settings
  read here.** Those subcharts are external dependencies, not vendored into this
  repository, and were not opened for this node.
- **What, if anything, `squareup/block-coder-tf-stacks` or `squareup/sprout-oss`
  automate for a managed staging/production Postgres, Redis, or S3 instance.** Both
  are private repositories `AGENTS.md` names but this task could not open.
- **Whether a timed restore drill has ever been run against any deployment path in
  this repository.** No test, script, or CI job matching one was found while
  gathering evidence for this node.
