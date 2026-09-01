---
id: operations-reliability-disaster-recovery
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
  - statement: "Postgres is Buzz's durable system of record for every Nostr event and every relational table (communities, channels, membership, moderation, workflow); migrations/0001_initial_schema.sql states it is the from-scratch multi-tenant schema, buzz-db's crate doc comment states the events table is partitioned by month, and local development persists it to a named buzz-postgres-data volume."
    entry_class: FACT
    evidence:
      - "migrations/0001_initial_schema.sql"
      - "crates/buzz-db/src/lib.rs"
      - "docker-compose.yml"
  - statement: "The shared S3-compatible object-storage bucket is the durable, create-only, content-addressed source of truth for both media blobs (buzz-media) and git repository objects (buzz-relay's api::git::store) in the same bucket; docs/git-on-object-storage.md's own abstract states the git protocol is designed for hosting repositories on an object store 'with no persistent filesystem', and .env.example documents one BUZZ_S3_* configuration block serving both consumers."
    entry_class: FACT
    evidence:
      - "docs/git-on-object-storage.md"
      - "crates/buzz-media/src/storage.rs"
      - "crates/buzz-relay/src/api/git/store.rs"
      - ".env.example"
  - statement: "BUZZ_RELAY_PRIVATE_KEY is the relay's durable, stable signing identity: .env.example instructs operators to 'Preserve that value across restarts and backups,' and crates/buzz-relay/src/main.rs's relay_keypair_from_config / startup path hard-fails ('BUZZ_RELAY_PRIVATE_KEY must be set') whenever the key is required (BUZZ_REQUIRE_RELAY_MEMBERSHIP=true or BUZZ_REQUIRE_AUTH_TOKEN=true) and absent."
    entry_class: FACT
    evidence:
      - ".env.example"
      - "crates/buzz-relay/src/main.rs"
      - "crates/buzz-relay/src/config.rs"
  - statement: "Both this repository's Compose bundle and its Helm chart print an identical operator checklist naming the same five durable items to preserve: BUZZ_RELAY_PRIVATE_KEY, the Postgres database, the S3 bucket, the git on-disk path, and an owner private key that the chart states is 'held by the operator, not by this chart' and is restored only by re-installing with the same ownerPubkey."
    entry_class: FACT
    evidence:
      - "deploy/compose/run.sh"
      - "deploy/charts/buzz/README.md"
      - "deploy/charts/buzz/templates/NOTES.txt"
  - statement: "Redis holds no durable Buzz data: every Redis-writing module in buzz-pubsub either sets a TTL-bound key (presence.rs's 180s SET EX; nip98_replay.rs's SET NX EX replay guard; rate_limiter.rs's Lua INCR+EXPIRE counter) or publishes a transient pub/sub message with nothing stored (cache_invalidation.rs's own module doc states a dropped invalidation is safe because 'the next read re-fetches authoritative state from the DB')."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/presence.rs"
      - "crates/buzz-pubsub/src/nip98_replay.rs"
      - "crates/buzz-pubsub/src/rate_limiter.rs"
      - "crates/buzz-pubsub/src/cache_invalidation.rs"
  - statement: "The relay's local on-disk git path is a self-bootstrapping scratch and pack-cache directory, not a durable store: crates/buzz-relay/src/config.rs's ensure_git_repo_path creates it if missing, crates/buzz-relay/src/api/git/transport.rs uses it only as a NamedTempFile scratch directory, and hydrate.rs's own module doc states 'object storage remains authoritative' over the cached pack/index pairs it materializes."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/config.rs"
      - "crates/buzz-relay/src/api/git/hydrate.rs"
      - "crates/buzz-relay/src/api/git/transport.rs"
  - statement: "Despite the git path being a reconstructable cache, both deployment configurations in this repository provision it as if it were durable: deploy/compose/compose.yml mounts a named buzz-git-data volume at BUZZ_GIT_REPO_PATH, and the Helm chart provisions a PersistentVolumeClaim for the same path (deploy/charts/buzz/templates/pvc-git.yaml); the Compose and Helm operator checklists both list this path/PVC under 'back these up.'"
    entry_class: FACT
    evidence:
      - "deploy/compose/compose.yml"
      - "deploy/charts/buzz/templates/pvc-git.yaml"
      - "deploy/compose/run.sh"
      - "deploy/charts/buzz/templates/NOTES.txt"
  - statement: "Both operator checklists' instruction to back up the git path/PVC is stale relative to this repository's own object-storage-backed git implementation: docs/git-on-object-storage.md's abstract states the protocol requires 'no persistent filesystem', and the merged corpus node architecture-containers-object-storage independently states git ref/object state is 'entirely object-store-backed' so each replica needs only ephemeral ReadWriteOnce storage -- treating the mounted git path as a recovery-critical backup target contradicts the design both sources describe, rather than merely restating it in different words."
    entry_class: INFERENCE
    evidence:
      - "docs/git-on-object-storage.md"
      - "crates/buzz-relay/src/api/git/hydrate.rs"
      - "launchpad/docs/corpus/architecture/containers/object-storage.md"
    confidence: 0.75
  - statement: "Postgres connectivity is a hard startup dependency -- crates/buzz-relay/src/main.rs calls Db::new and propagates any connection error as a fatal anyhow::Error before the relay binds any listener -- while object-storage reachability is not synchronously verified at startup and is absent from the readiness contract: crates/buzz-relay/src/router.rs's readiness_handler checks only Postgres (state.db.ping()), Redis (state.redis_pool.get()) and the deletion-serving catalog."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs"
      - "crates/buzz-relay/src/router.rs"
  - statement: "No backup or restore tooling ships in this repository. deploy/compose/run.sh's backup_hint function only prints a checklist to stdout and invokes no backup command; deploy/charts/buzz/templates/NOTES.txt prints the same checklist at helm install time; crates/buzz-admin/src/main.rs's Command enum has eight variants (AddMember, RemoveMember, ListMembers, GenerateKey, Migrate, ProductFeedback, Deletions, ReconcileChannels) and none performs a backup, restore, dump or snapshot operation; and launchpad/deploy/runbooks/hardening-spec.md's own Part E states plainly that 'run.sh backup-hint prints a correct checklist and automates nothing.'"
    entry_class: FACT
    evidence:
      - "deploy/compose/run.sh"
      - "deploy/charts/buzz/templates/NOTES.txt"
      - "crates/buzz-admin/src/main.rs"
      - "launchpad/deploy/runbooks/hardening-spec.md"
  - statement: "No RTO or RPO figure is defined anywhere in this repository. A repository-wide search for RTO/RPO/'recovery time objective'/'recovery point objective'/'disaster recovery' outside the corpus tree returns hits only in launchpad/Research/hardening-linux-servers.md and launchpad/deploy/runbooks/hardening-spec.md, both explicitly proposal documents rather than shipped configuration; hardening-spec.md's Part E states the one RPO-shaped constraint that exists -- 'Postgres and the object/git state must come from the same maintenance window' -- as a consistency rule to satisfy, not a numeric target, and separately instructs measuring an actual RPO/RTO figure in a future timed drill that this node found no record of having been run."
    entry_class: FACT
    evidence:
      - "grep_rto_rpo(**/*.md, **/*.yaml, **/*.yml, **/*.sh, excluding launchpad/docs/corpus/**) -> hits only in launchpad/Research/hardening-linux-servers.md and launchpad/deploy/runbooks/hardening-spec.md, at commit 473205a7457b208455f188847bfb27b01aa83cac"
      - "launchpad/deploy/runbooks/hardening-spec.md"
  - statement: "Feature #618's batch dispatch brief for this task names three related, unmerged sibling tasks that this node's scope boundary excludes rather than links: backup (issue #1197, operations/databases/backup.md), restore (issue #1202, operations/databases/restore.md), and availability (issue #1214, operations/reliability/availability.md)."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "Feature #618 batch dispatch brief dispatching issue #1216"
  - statement: "This node was written using launchpad/docs/corpus/templates/reference.md, which was already merged on origin/launchpad at the recorded revision and directs a reference-shaped node to carry a Reference description, structured entries, an optional Commands section, an explicit Boundary statement, Relationships, and a Scope-and-omissions section separating what the node does not cover from what it could not verify."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/templates/reference.md"
relationships:
  - type: references
    target: architecture-containers-postgres
  - type: references
    target: architecture-containers-redis
  - type: references
    target: architecture-containers-object-storage
  - type: references
    target: layers-configuration-secrets
---

# Disaster recovery: reference

What a whole-deployment loss of a Buzz relay would mean and what recovering
from one would consist of: the complete inventory of state that must survive
such a loss, what is genuinely disposable, the order recovery is structurally
constrained to follow, and what recovery capability this repository actually
ships today versus what an operator must supply themselves. This node is
linked from, and does not replace, the container-level architecture nodes for
[Postgres](../../architecture/containers/postgres.md),
[Redis](../../architecture/containers/redis.md), and
[object storage](../../architecture/containers/object-storage.md), and the
configuration-catalog node for
[secrets](../../layers/configuration/secrets.md) — each of those documents its
subsystem's own responsibility and technology; this node documents only the
durable-versus-disposable and recovery-ordering facts that follow from them.

## Durable state inventory

Loss of any row below is data loss or identity loss, not merely a
availability interruption. Ordered by how central each item is to the
system's own identity and content, per the discussion in *Recovery dependency
order* below, not alphabetically.

| Component | Where it lives | Why it is durable | Evidence |
|---|---|---|---|
| Postgres event store and relational tables | The configured `DATABASE_URL` Postgres instance | The single system of record for every Nostr event and every community/channel/membership/moderation/workflow row; nothing else in this repository holds this data | `migrations/0001_initial_schema.sql`, `crates/buzz-db/src/lib.rs` |
| S3-compatible object storage bucket | The configured `BUZZ_S3_*` endpoint/bucket | Create-only, content-addressed source of truth for both media blobs and git repository pack/manifest objects; `docs/git-on-object-storage.md` designs the git half around requiring no durable local filesystem at all | `docs/git-on-object-storage.md`, `crates/buzz-media/src/storage.rs`, `crates/buzz-relay/src/api/git/store.rs` |
| `BUZZ_RELAY_PRIVATE_KEY` | Operator-held secret, injected as an environment variable | The relay's stable signing identity for NIP-43 membership signing and addressable-event replacement; rotating it is an identity change federation peers will not recognize | `.env.example`, `crates/buzz-relay/src/main.rs` |
| Configuration and secrets (`DATABASE_URL` credentials, `BUZZ_S3_ACCESS_KEY`/`BUZZ_S3_SECRET_KEY`, `BUZZ_GIT_HOOK_HMAC_SECRET`, Redis credentials) | The environment file (`.env.example` names the shape; the populated file is operator-held and gitignored) | Without these, a redeployed relay cannot reach or authenticate to its own durable stores | `.env.example`, `deploy/compose/run.sh` |
| Owner private key (`RELAY_OWNER_PUBKEY`'s corresponding secret) | Held entirely by the operator, outside the relay and outside this repository's tooling | The chart's own documentation states this explicitly: it is "held by the operator, not by this chart," and is restored only by re-installing with the same `ownerPubkey`, never by anything this repository backs up on the operator's behalf | `deploy/charts/buzz/README.md`, `deploy/charts/buzz/templates/NOTES.txt` |

## Disposable state

Loss of either row below costs a brief window of degraded behavior on restart,
never data loss.

| Component | Why it is disposable | Evidence |
|---|---|---|
| Redis | Holds no durable Buzz data — every key `buzz-pubsub` writes is TTL-bound (presence, replay guards, rate-limit counters) or a transient pub/sub message; a dropped cache-invalidation message is explicitly backstopped by a re-fetch from Postgres on the next read | `crates/buzz-pubsub/src/presence.rs`, `crates/buzz-pubsub/src/nip98_replay.rs`, `crates/buzz-pubsub/src/rate_limiter.rs`, `crates/buzz-pubsub/src/cache_invalidation.rs` |
| Local on-disk git path (`BUZZ_GIT_REPO_PATH`, including its `.pack-cache` subdirectory) | A self-bootstrapping scratch and pack-cache directory the relay recreates if missing; the object-storage bucket is the authoritative source it rehydrates from on every git request | `crates/buzz-relay/src/config.rs`, `crates/buzz-relay/src/api/git/hydrate.rs` |

**A documented tension, not a silent resolution.** Both of this repository's
own deployment configurations provision the two rows above as if they were
durable anyway: `deploy/compose/compose.yml`'s production Redis service runs
with `--appendonly yes` against a named `buzz-redis-data` volume, and both the
Compose bundle (a `buzz-git-data` named volume) and the Helm chart
(`deploy/charts/buzz/templates/pvc-git.yaml`, a `PersistentVolumeClaim`)
provision persistent storage for the git path — and both operator-facing
checklists (see *Commands* below) list that path/PVC under "back these up."
That instruction contradicts the object-storage design `docs/git-on-object-storage.md`
and the merged `architecture-containers-object-storage` node both describe (see
the `INFERENCE` entry in this node's evidence ledger). This node records the
code's own behavior — the git path is reconstructable — as the operative fact,
consistent with `AGENTS.md`'s evidence-precedence rule that executable
behavior outranks documentation for how the system currently behaves, and
names the checklists' instruction as stale rather than silently repeating it.
The Redis persistence volume is not read the same way: nothing in this
repository's evidence claims Redis is *required* for recovery, so provisioning
it durably reads as an anti-cold-cache-stampede convenience, not a documented
contradiction.

## Recovery dependency order

This is a statement of structural dependency, not a procedure — restoring any
of these components is the subject of the separate backup/restore tasks named
in *Boundary* below, not this node.

| Stage | Behavior observed in code | Evidence |
|---|---|---|
| Postgres | A hard startup gate. `main()` calls `Db::new` and propagates a connection failure as a fatal error before any listener binds; the relay cannot serve any traffic at all against an unreachable or absent Postgres. | `crates/buzz-relay/src/main.rs` |
| Configuration and the relay signing key | Read once, before Postgres is dialed, and also fatal on failure when required (`relay_keypair_from_config`, `BUZZ_RELAY_PRIVATE_KEY must be set`) — recovering identity has to precede a production-mode restart, not merely follow it. | `crates/buzz-relay/src/main.rs`, `crates/buzz-relay/src/config.rs` |
| Object storage (S3 bucket) | Not verified synchronously at startup and not part of the readiness contract (`readiness_handler` checks only Postgres, Redis, and the deletion-serving catalog) — a relay can report itself ready while the bucket is unreachable, and media/git requests fail per-request instead of at boot. | `crates/buzz-relay/src/router.rs` |
| Redis | Checked by the readiness probe (so an operator sees the relay report "not ready" if Redis is down) but requires no recovery step of its own: a fresh, empty Redis instance is a valid starting state, per *Disposable state* above. | `crates/buzz-relay/src/router.rs` |
| Local git path | No recovery step: absent or empty, `ensure_git_repo_path` recreates it, and the relay rehydrates each repository from object storage on the next git request. | `crates/buzz-relay/src/config.rs` |

The one cross-component ordering constraint this repository's own material
states explicitly is about *consistency*, not sequencing: `launchpad/deploy/runbooks/hardening-spec.md`'s
Part E states "Postgres and the object/git state must come from the same
maintenance window," because an event row in Postgres referencing a media or
git object the object-store snapshot predates is a dangling reference. That
document is a proposal for how a backup/restore role should behave, not a
mechanism this repository enforces at runtime — see *RTO and RPO* below.

## RTO and RPO

No recovery time objective or recovery point objective is defined anywhere in
this repository. A repository-wide search for "RTO," "RPO," "recovery time
objective," "recovery point objective," and "disaster recovery" outside the
corpus tree itself returns hits only in two documents under
`launchpad/deploy/` and `launchpad/Research/` — both explicitly proposals for
work not yet done, not shipped configuration or measured figures. The nearest
thing to an RPO in this repository is the consistency *constraint* named in
*Recovery dependency order* above (snapshot Postgres and object/git state
together), which is a rule to satisfy during a future backup implementation,
not a numeric target this repository commits to today. No timed restore drill
or measured recovery time is recorded anywhere this node could find.

## Commands

<!-- The two commands below are the entire operator-facing surface this
     repository ships for disaster-recovery purposes; neither performs a
     backup or restore action. Included here, rather than omitted, because
     their print-only nature is itself the central fact this node reports. -->

| Command | Description | Argument | Example |
|---|---|---|---|
| `./launchpad/deploy/run.sh backup-hint` (wraps `deploy/compose/run.sh backup-hint`) | Prints the Compose deployment's "back these up" checklist to stdout. Performs no backup action — no `pg_dump`, no object-store copy, nothing written anywhere. | none | `./launchpad/deploy/run.sh backup-hint` |
| `helm install` against `deploy/charts/buzz` | Renders `templates/NOTES.txt`, which prints the identical five-item checklist once, at install time. Performs no backup action. | chart values | `helm install buzz deploy/charts/buzz -f values.yaml` |

## Boundary

This node does not describe:

- **How to actually back up or restore any of the durable items above,
  step by step.** That is the subject of two sibling tasks already authored
  on other, unmerged branches at the time of writing: a backup procedure
  (`operations/databases/backup.md`, issue #1197) and a restore procedure
  (`operations/databases/restore.md`, issue #1202). This node names what must
  be preserved and in what dependency order; it deliberately does not
  duplicate their procedural content, and does not link either path since
  neither is merged on `origin/launchpad` at this revision.
- **Availability, redundancy, or failover behavior during partial
  degradation** — replica counts, pod disruption budgets, read-replica
  routing, or graceful handling of one dependency being briefly unreachable
  without a total deployment loss. That is the cross-cutting sibling subject
  of `operations/reliability/availability.md` (issue #1214), not this node,
  which is scoped to whole-deployment loss and recovery from it.
- **A prescriptive RTO/RPO target this repository should adopt.** This node
  reports the absence documented in *RTO and RPO* above; proposing a number
  the repository does not itself state would be inventing operational
  procedure this repository does not support, which `AGENTS.md`'s evidence
  rules and this Feature's dispatch brief both treat as the one unrecoverable
  failure mode for this batch of work.
- **Whether the staging/production Postgres and object-storage topology
  (replica counts, snapshot cadence, retention) matches anything described
  here.** See *Scope and omissions* below.

## Relationships

- **references** → `architecture-containers-postgres` — the merged node
  documenting Postgres's responsibility, technology, and ownership boundary
  at container altitude; this node's durable-state entry for Postgres is
  narrower (durability and recovery-ordering facts only) and does not repeat
  that node's content.
- **references** → `architecture-containers-redis` — the merged node whose own
  evidence ledger already establishes every Redis key is TTL-bound or
  transient; this node's *Disposable state* entry for Redis draws the
  recovery-relevant conclusion from facts that node also documents, verified
  independently against the same source files here.
- **references** → `architecture-containers-object-storage` — the merged node
  documenting the shared S3-compatible bucket's dual role (media and git);
  this node's durable-state entry and the git-hydration-cache tension both
  depend on facts that node states about the git half.
- **references** → `layers-configuration-secrets` — the merged node cataloguing
  `BUZZ_RELAY_PRIVATE_KEY` and the other secret-shaped configuration surface in
  full; this node cites only the subset relevant to what must survive a
  whole-deployment loss.
- **Checked and not declared:** no relationship to backup (#1197), restore
  (#1202), or availability (#1214) — none of the three has a corresponding
  node id present in `origin/launchpad`'s corpus tree at the recorded
  revision (per `AGENTS.md` step 9, a target must resolve on the branch being
  merged into), and per this Feature's dispatch brief their paths are named in
  prose only, not linked. The first of the three to merge is the point to
  revisit this.

## Scope and omissions

**This node covers** the complete inventory of durable state a whole-deployment
loss of this repository's relay would need to recover (Postgres, the shared
object-storage bucket, the relay signing key, configuration/secrets, and the
operator-held owner key), what is genuinely disposable (Redis, the local git
hydration/pack cache) including the documented tension between that fact and
this repository's own deployment configurations, the structural dependency
order recovery would have to follow, what recovery-facing command surface this
repository actually ships (two print-only checklists and nothing else), and
the absence of any stated RTO or RPO.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Step-by-step backup procedure | `operations/databases/backup.md`, issue #1197, unmerged at time of writing |
| Step-by-step restore procedure | `operations/databases/restore.md`, issue #1202, unmerged at time of writing |
| Availability and partial-degradation behavior | `operations/reliability/availability.md`, issue #1214, unmerged at time of writing |
| Postgres's own responsibility, technology, and ownership boundary | `architecture-containers-postgres` |
| Redis's own responsibility, technology, and ownership boundary | `architecture-containers-redis` |
| Object storage's own responsibility, technology, and ownership boundary | `architecture-containers-object-storage` |
| The full secret-configuration catalog beyond what must survive a deployment loss | `layers-configuration-secrets` |
| The formal safety proof for git-on-object-storage | `docs/git-on-object-storage.md` |
| Whether `squareup/block-coder-tf-stacks` or `squareup/sprout-oss` (the private pipelines that deploy and build this repository's staging/production images, per the root `AGENTS.md`'s ecosystem table) provision Postgres/S3 with any backup, snapshot, or retention policy of their own | those private repositories, not present in this checkout |

**Expected but not verified when this node was written:**

- **Whether any timed restore drill has ever actually been run against this
  repository's deployment configurations.** `launchpad/deploy/runbooks/hardening-spec.md`
  calls for one and this node found no record that it happened; this node
  reports the absence of evidence, not evidence of absence beyond what a
  repository-wide search can show.
- **What Postgres and object-storage topology (single instance, replicated,
  managed-service snapshots) the private `squareup/block-coder-tf-stacks` and
  `squareup/sprout-oss` pipelines actually provision for staging/production.**
  Those repositories are not part of this checkout, consistent with the same
  gap already recorded in the merged `architecture-containers-postgres` and
  `architecture-containers-object-storage` nodes.
- **Whether the git-PVC/backup-checklist tension identified above has already
  been raised anywhere else** (e.g. as feedback on the Helm chart or Compose
  bundle) — this node's own search did not extend to closed issues or PR
  review threads on those files.
