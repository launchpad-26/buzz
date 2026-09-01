---
id: layers-data-postgres-backup-boundary
type: layers
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - operator
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5."
    entry_class: FACT
    evidence:
      - "commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
  - statement: "node.schema.json's type enum is architecture, layers, capabilities, platforms, implementation, interfaces-events, verification, operations, development, release, governance, agent, ingestion, and contains no data or datastore value -- a node whose path lives under layers/ takes type: layers."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "This node uses type: layers rather than templates/datastore.md's own suggested value for a real datastore instance (architecture, at confidence 0.6), for the same reason three other documents in this same overnight batch already chose it: the issue's own directory assignment (launchpad/docs/corpus/layers/data/postgres/backup-boundary.md, from issue #1076's corpus-plan:v2 alias header) and Feature #610's title ('data and storage layer corpus exists') both point at layers as the intended surface. Per standards/taxonomy.md's step-4 rule (disclose an imperfect fit rather than silently resolve it), this tension is named here rather than picked unilaterally."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
      - "launchpad/docs/corpus/templates/datastore.md"
      - "launchpad/docs/corpus/standards/taxonomy.md"
    confidence: 0.65
  - statement: "architecture-containers-postgres.md (merged on origin/launchpad) states Postgres is Buzz's single system of record: the durable event store behind every Nostr event the relay accepts, plus the relational tables for communities, channels, membership, moderation, workflows, push state, and audit -- there is no separate database per subsystem. This node zooms into one operational dimension of that container -- what must be backed up and who owns making that happen -- rather than repeating its connection-pooling, migration, or partitioning detail."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/containers/postgres.md"
  - statement: "deploy/charts/buzz/README.md's Backups section states, verbatim: 'Save these. Losing any of them is data loss.' and lists five items: (1) BUZZ_RELAY_PRIVATE_KEY -- relay identity, (2) PostgreSQL database -- 'the canonical event store', (3) S3 bucket -- media blobs, (4) Git PVC -- repo on-disk state served by the relay's git endpoint, and (5) Owner private key -- 'held by the operator, not by this chart. Restore by re-installing with the same ownerPubkey.' This is the one place in this repository that names Postgres as a backup-relevant store and states its role in that list explicitly."
    entry_class: FACT
    evidence:
      - "deploy/charts/buzz/README.md"
  - statement: "deploy/charts/buzz/templates/NOTES.txt renders the identical five-item list (under the heading 'Backups -- save these') as live post-install/post-upgrade Helm output, confirming the chart README's list is not aspirational documentation but text an operator actually sees after every install; its second item is rendered as 'PostgreSQL database{{ if .Values.postgresql.enabled }} ({{ .Release.Name }}-postgresql PVC){{ end }}', i.e. it names the bundled-quickstart PVC specifically when that profile is active, and otherwise names only the database itself (the production profile's externally managed instance has no chart-visible PVC to name)."
    entry_class: FACT
    evidence:
      - "deploy/charts/buzz/templates/NOTES.txt"
  - statement: "No backup-automation tooling exists anywhere in this repository at the recorded revision: a case-insensitive grep for backup, pg_dump, pg_basebackup, wal-g, pgbackrest, point-in-time, pitr, and snapshot across every .md/.yaml/.yml/.toml/.tf file, plus a repository-wide filename search for *backup*, returned no Postgres-backup-mechanism hits -- the only *backup*-named files found are desktop/src-tauri/src/key_backup.rs and its neighbors, which implement client-side encrypted Nostr private-key export/import (per crates and files inspected under desktop/src-tauri/src/ and desktop/src/features/{onboarding,settings}/), an unrelated feature about a user's own signing key, not the Postgres datastore."
    entry_class: INFERENCE
    evidence:
      - "grep(pattern='backup|pg_dump|pg_basebackup|wal-g|pgbackrest|point-in-time|pitr|snapshot', glob='**/*.{md,yaml,yml,toml,tf}', case_insensitive=true) -> no Postgres-backup-mechanism match, at repository revision 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
      - "find(iname='*backup*') -> desktop/src-tauri/src/key_backup.rs and sibling desktop client-side key-backup files only"
    confidence: 0.85
  - statement: "crates/buzz-admin/src/ contains exactly two source files, main.rs and deletions.rs; buzz-admin (the operator CLI crate) has no backup, dump, restore, or snapshot subcommand at the recorded revision."
    entry_class: FACT
    evidence:
      - "crates/buzz-admin/src/main.rs"
      - "crates/buzz-admin/src/deletions.rs"
  - statement: "architecture-containers-postgres.md's own scope-and-omissions table already names 'Production/staging Postgres provisioning and topology' as owned by squareup/block-coder-tf-stacks, described there as 'private, not opened by this task' -- the same boundary this node draws for backup automation specifically: whether and how a production Postgres instance is actually backed up on a schedule is a question this repository's own source cannot answer, because the pipeline that would implement it lives in a separate private repository this task did not open."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/architecture/containers/postgres.md"
      - "AGENTS.md"
    confidence: 0.75
  - statement: "docs/push-gateway-deployment.md documents a second, unrelated Postgres database belonging to the separate buzz-push-gateway service, and states explicitly that its migration DATABASE_URL 'MUST name a dedicated gateway database, not the relay database: SQLx stores its _sqlx_migrations history in public, so sharing a database would collide with another application's migration history.' The same document states, of that database, 'Database backups therefore contain ciphertext plus authority metadata and must receive the same access controls and retention treatment as the service secrets.' This is a structurally distinct Postgres instance from the one architecture-containers-postgres.md and this node describe, named here only to draw the boundary, not restated as this node's own subject."
    entry_class: FACT
    evidence:
      - "docs/push-gateway-deployment.md"
  - statement: "deploy/charts/buzz/values.yaml's Postgres block comments the bundled quickstart subchart as 'Eval-only CloudPirates subchart' with persistence.enabled: true and a 10Gi size, and docker-compose.yml's local-development Postgres service persists to a named buzz-postgres-data volume -- both are ordinary, unmanaged Docker/Kubernetes volumes with no snapshot, replication, or backup schedule attached at the chart or compose level; only the production profile (external, unmanaged-by-this-chart Postgres, per README.md's profile table) is a candidate for whatever backup posture its own operator or squareup/block-coder-tf-stacks provisions."
    entry_class: FACT
    evidence:
      - "deploy/charts/buzz/values.yaml"
      - "docker-compose.yml"
  - statement: "migrations/0001_initial_schema.sql defines every tenant-scoped table with a NOT NULL community_id, and architecture-containers-postgres.md records this as the row-zero invariant: cross-community data isolation is enforced in the schema itself, not merely in application logic. A single Postgres backup or restore operation is therefore community-boundary-blind -- it acts on the whole physical database at once, unlike buzz-deletion's whole-community teardown path (crates/buzz-deletion), which is explicitly scoped to one community_id."
    entry_class: INFERENCE
    evidence:
      - "migrations/0001_initial_schema.sql"
      - "launchpad/docs/corpus/architecture/containers/postgres.md"
      - "crates/buzz-deletion/src/lib.rs"
    confidence: 0.8
  - statement: "No mechanism in this repository coordinates a Postgres backup with a corresponding S3-bucket or Git-PVC backup into one consistent point-in-time snapshot; the chart's own Backups section lists the three stores as separate numbered items with no cross-store ordering or coordination instruction, and no script, Job template, or CI workflow under deploy/ or scripts/ references more than one of the three stores in a backup context."
    entry_class: INFERENCE
    evidence:
      - "deploy/charts/buzz/README.md"
      - "deploy/charts/buzz/templates/NOTES.txt"
    confidence: 0.7
  - statement: "crates/buzz-db/src/store/partition.rs's ensure_future_partitions creates partitions ahead of the current month (its own doc comment: 'Call ensure_future_partitions on startup and monthly via cron') but no function anywhere under crates/buzz-db/src/ drops, archives, or prunes an old partition -- a repository-wide search for drop/prune/retention language scoped to partition.rs and its callers found none. The events table therefore has no data-lifecycle expiry of its own; short of an explicit whole-community deletion (crates/buzz-deletion), a backup must be assumed to need to cover the full, ever-growing history, not a bounded recent window."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-db/src/store/partition.rs"
      - "crates/buzz-db/src/lib.rs"
    confidence: 0.75
  - statement: "architecture-containers-postgres.md's own inbound-interfaces table names five callers of the Postgres instance -- buzz-relay's main writer/reader pools via buzz-db, buzz-relay's direct audit pool, buzz-relay's direct search pool, buzz-admin, and buzz-deletion -- each a component within the same buzz-relay binary or a separate operator-invoked CLI, never a client reaching Postgres directly. A Postgres backup therefore captures the combined state of every one of those access paths at once; this node does not restate that table, it points to it."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/containers/postgres.md"
  - statement: "Issue #1076's definition of done requires this node to state whether the store is authoritative, derived, cache or transport; describe owned data, key access patterns, lifecycle/retention and consistency semantics; name tenancy/security boundaries and failure behavior; and link schema/migrations/code/tests rather than copy DDL."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1076 definition of done"
relationships:
  - type: part-of
    target: architecture-containers-postgres
---

# Postgres: backup boundary

What "backup" means for Buzz's Postgres datastore, and where this repository's own
responsibility for it starts and stops. This document zooms into one operational
facet of the container `architecture-containers-postgres` already inventories --
Postgres's existence, technology, and connection-pool ownership -- without repeating
that node's connection, migration, or partitioning detail.

## Purpose and scope

This node answers one question: **what needs to survive a Postgres loss, and who is
responsible for making that happen?** It is not a disaster-recovery runbook, an RPO/RTO
commitment, or a description of any actual backup schedule -- none of those exist in
this repository's own source, and this document says so rather than inventing one.
What it does state, drawn directly from this repository's own chart documentation, is
the shape of the obligation: what Postgres holds that must be saved, what this
repository leaves to the deploying operator, and the consequences that follow from
Postgres being a single, multi-tenant, authoritative store.

## Store classification: authoritative, not derived

Postgres is Buzz's authoritative event store, not a cache, derived projection, or
transport layer. `architecture-containers-postgres.md` states it directly: Postgres is
"Buzz's single system of record," holding the durable event log plus every relational
table (communities, channels, membership, moderation, workflows, push state, audit) --
there is no separate database per subsystem, and no other datastore in this repository
(Redis via `buzz-pubsub`, the S3-compatible bucket) holds a durable copy of what
Postgres holds. A backup of Postgres is therefore not an optimization or a
convenience cache-warm; losing it without a backup is losing the event history and
every relational fact derived from it.

## Owned data, access patterns, and lifecycle

The data a Postgres backup captures is exactly what `architecture-containers-postgres.md`
already inventories: the durable event log plus the relational tables for
communities, channels, membership, moderation, workflows, push state, and audit.
That same node's inbound-interfaces table names every access path into this
instance -- `buzz-relay`'s main writer/reader pools (via `buzz-db`), `buzz-relay`'s
own direct audit and search pools, `buzz-admin`, and `buzz-deletion` -- all of them
components inside the `buzz-relay` binary or an operator-invoked CLI, never a client
reaching Postgres directly. A backup captures the combined result of every one of
those writers at once; this node does not restate that table, it points to it.

On lifecycle: `crates/buzz-db/src/store/partition.rs`'s `ensure_future_partitions` only
creates partitions ahead of the current month (its own doc comment: "Call
`ensure_future_partitions` on startup and monthly via cron"). No function under
`crates/buzz-db/src/` drops, archives, or prunes an old partition. The `events` table
therefore has no data-lifecycle expiry of its own -- short of an explicit whole-
community deletion via `crates/buzz-deletion`, a backup must be assumed to need to
cover the full, ever-growing history, not a bounded recent window. This is a real
consequence for backup sizing and duration that this repository's code makes true,
even though it says nothing directly about backup itself.

## What this repository says must be backed up

`deploy/charts/buzz/README.md`'s own `## Backups` section is the one place in this
codebase that enumerates backup-relevant state, and it opens with "Save these. Losing
any of them is data loss." Five items are named, in this order:

1. `BUZZ_RELAY_PRIVATE_KEY` -- relay identity; rotating it is an identity change, not
   a restore.
2. **PostgreSQL database -- "the canonical event store."**
3. S3 bucket -- media blobs.
4. Git PVC -- repo on-disk state served by the relay's git endpoint.
5. Owner private key -- "held by the operator, not by this chart. Restore by
   re-installing with the same `ownerPubkey`."

`deploy/charts/buzz/templates/NOTES.txt` renders this identical list as live
`helm install`/`helm upgrade` output under the heading "Backups -- save these," so it
is not documentation an operator might miss -- it is printed on every install. Item 2
is the only one this node's subject covers; the other four belong to their own
container's or credential's backup story, not this one's.

## What this repository deliberately does not implement

No backup mechanism for Postgres exists in this repository's own source. A
case-insensitive search across every Markdown, YAML, TOML, and Terraform-shaped file
for `backup`, `pg_dump`, `pg_basebackup`, `wal-g`, `pgbackrest`, `point-in-time`,
`pitr`, and `snapshot` turns up no Postgres-backup-mechanism hit; the only files
matching a `*backup*` filename search are the desktop app's client-side, user-facing
Nostr private-key backup feature (`desktop/src-tauri/src/key_backup.rs` and its
neighbors) -- an unrelated feature about a user's own signing key, not this datastore.
`crates/buzz-admin`, the operator CLI, has no `backup`, `dump`, `restore`, or
`snapshot` subcommand; its entire source is `main.rs` plus `deletions.rs` (whole-
community deletion, the opposite operation).

Both Postgres instances this chart can stand up -- the quickstart profile's bundled,
eval-only CloudPirates subchart (`postgresql.enabled: true` in `values.yaml`,
explicitly commented "Eval-only") and local development's `docker-compose.yml`
service (persisted to a named `buzz-postgres-data` Docker volume) -- are ordinary
unmanaged volumes with no snapshot, replication, or backup schedule attached at the
chart or compose level. Only the production profile's externally managed Postgres
(per `README.md`'s own profile table: "External managed Postgres/Redis/S3") is a
candidate for whatever backup posture its operator, or the pipeline that provisions
it, actually implements.

**This is the boundary the node's name refers to.** `architecture-containers-postgres.md`
already draws the identical line for provisioning and topology generally, naming
`squareup/block-coder-tf-stacks` (private, not opened by this task) as the owner of
what this repository cannot see. This node extends that same reasoning to backup
automation specifically: whether a production Postgres instance is actually backed up
on any schedule, with what retention, is not answerable from this repository's own
source.

## Consistency semantics across the three backed-up stores

The chart's Backups list names three separate stores (Postgres, the S3 bucket, the Git
PVC) as three separate numbered items, with no ordering or coordination instruction
between them, and no script, Job template, or CI workflow in this repository backs up
more than one of the three in a single coordinated operation. A Postgres backup taken
independently of an S3-bucket or Git-PVC backup is not guaranteed to represent the
same instant in time as either -- there is no cross-store point-in-time consistency
mechanism in this repository. This is a real, checked gap, not an assumption of one:
consistency across those boundaries, if it is required, is an operator- or
pipeline-level concern this repository does not implement.

## Tenancy and failure behavior

Postgres is a single, shared, multi-tenant instance: `migrations/0001_initial_schema.sql`
gives every tenant-scoped table a `NOT NULL community_id`, and
`architecture-containers-postgres.md` records this as the schema's row-zero
invariant -- cross-community isolation is enforced in the schema and in `buzz-db`'s
query construction, never merely in application logic above it. A Postgres backup or
restore operation acts on the whole physical database at once and is therefore
**community-boundary-blind**: restoring from a backup restores (or fails to restore)
every community's data simultaneously. This is a materially different failure shape
from `crates/buzz-deletion`'s whole-community teardown path, which is explicitly
scoped to a single `community_id` and never touches any other tenant's rows. An
operator restoring Postgres from backup cannot restore one community in isolation
using anything this repository provides.

On the credential side, the chart's own Backups list separates what a Postgres
restore covers from what it does not: the relay's own signing identity
(`BUZZ_RELAY_PRIVATE_KEY`) and the community owner's private key are both named as
*separate* backup items, held outside Postgres (the owner key explicitly "held by the
operator, not by this chart"). Restoring a Postgres backup alone, without also
restoring or re-supplying those two keys, does not reconstitute a working relay --
the chart's own restore note for the owner key is "re-install with the same
`ownerPubkey`," which is orthogonal to database restoration entirely.

## A related but out-of-scope boundary: the push-gateway's own database

`docs/push-gateway-deployment.md` documents a second, structurally distinct Postgres
database belonging to the separate `buzz-push-gateway` service, and states its
migration `DATABASE_URL` "MUST name a dedicated gateway database, not the relay
database," because SQLx's own migration-history table would otherwise collide with
another application's. That document separately states that database's backups
"contain ciphertext plus authority metadata and must receive the same access controls
and retention treatment as the service secrets." That is a real, checked backup
consideration in this repository -- but for a different Postgres instance than the one
`architecture-containers-postgres.md` and this node describe. It is named here only to
draw the boundary explicitly, not restated as this node's own subject.

## Implementation, schema, and test references

- `launchpad/docs/corpus/architecture/containers/postgres.md` -- the container-level
  node this document is `part-of`; connection pooling, migrations, and partitioning
  detail live there, not here.
- `deploy/charts/buzz/README.md` -- the chart's own `## Backups` section, the primary
  source for this node's subject.
- `deploy/charts/buzz/templates/NOTES.txt` -- the same list rendered as live
  post-install output.
- `deploy/charts/buzz/values.yaml` -- the quickstart profile's eval-only bundled
  Postgres block.
- `docker-compose.yml` -- local development's unmanaged `buzz-postgres-data` volume.
- `migrations/0001_initial_schema.sql` -- the `NOT NULL community_id` invariant
  underlying the tenancy claim above.
- `crates/buzz-deletion/src/lib.rs` -- the community-scoped teardown path this node
  contrasts against a whole-database restore.
- `crates/buzz-admin/src/` -- confirmed to carry no backup/restore subcommand.
- `docs/push-gateway-deployment.md` -- the separate service and database this node
  explicitly excludes.

This document does not restate any of those files' full contents -- read them
directly for the detail; this node exists to state the backup boundary and its
consequences, not to duplicate the sources that establish it.

## Scope and omissions

**This node covers** what this repository's own source states must be backed up for
Postgres, what backup mechanism (if any) this repository implements, the consistency
and tenancy consequences of Postgres being a single shared authoritative store, and
where this repository's own visibility into backup automation stops.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Postgres connection pooling, migrations, partitioning, and container-level responsibility | `architecture-containers-postgres.md` |
| Actual production/staging backup schedule, retention window, or RPO/RTO commitment | `squareup/block-coder-tf-stacks` (private, not opened by this task) |
| `buzz-push-gateway`'s own, structurally separate Postgres database and its backup/ciphertext handling | `docs/push-gateway-deployment.md` |
| Table-by-table schema contents and the multi-tenant conformance contract | `migrations/0001_initial_schema.sql`, `docs/multi-tenant-conformance.md` |
| Whole-community deletion (the inverse, community-scoped operation) | `crates/buzz-deletion/src/lib.rs` |

**No relationships to sibling `layers/data/postgres/*` documents from this same
overnight batch** (events-table, migrations, partitions, connection-pool, and the
rest). None are merged on `origin/launchpad` at the recorded revision -- each exists,
if at all, only on an unmerged sibling worktree/branch -- and `AGENTS.md`'s node-
creation step 9 requires a `relationships[].target` to resolve against the branch
being merged into, not the author's own worktree. The `part-of` edge to
`architecture-containers-postgres` is the one relationship this node declares, because
that node is confirmed merged on `origin/launchpad`
(`git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus`).

**Expected but not verified when this node was written:**

- **Whether `squareup/block-coder-tf-stacks` or `squareup/sprout-oss` actually
  provisions or schedules Postgres backups was not established.** Both are private
  repositories this task did not open; this is named as an open gap, not resolved
  either way, matching `architecture-containers-postgres.md`'s own identical
  disclosure about provisioning generally.
- **Whether any cross-store backup coordination exists at the infrastructure level**
  (outside this repository's own source, e.g. a snapshot orchestrator in the private
  Terraform stacks) was not checked, because it would live in the same private
  repositories named above.
- **The `type: layers` versus `templates/datastore.md`'s suggested `type: architecture`
  tension is disclosed, not resolved**, per this batch's established precedent; a
  future corpus-wide pass may revisit which is correct for every instance node written
  from that template.
