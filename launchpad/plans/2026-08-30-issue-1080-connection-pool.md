Issue #1080: document layers/data/postgres/connection-pool.md

Stated size: issue carries no explicit Size label; matches every other single-document task in this overnight batch, capped at 5 steps by the corpus-batch-author skill.  ->  cap: 5 steps

ALREADY TRUE

`launchpad/docs/corpus/schema/node.schema.json`'s `type` enum has no `data` or
`datastore` member; it is `architecture, layers, capabilities, platforms,
implementation, interfaces-events, verification, operations, development, release,
governance, agent, ingestion`. A node whose path lives under `layers/` takes
`type: layers`, per this same overnight batch's own established precedent (PR #1875,
unmerged: `audit-tables.md`, `backup-boundary.md`, `channel-members-table.md`,
`channels-table.md`, `communities-table.md` all chose `layers` over
`templates/datastore.md`'s own suggested `architecture` for a real datastore
instance, and disclosed the tension per `standards/taxonomy.md` step 4 rather than
silently resolving it).

`launchpad/docs/corpus/templates/datastore.md` and
`launchpad/docs/corpus/templates/data-entity.md` both exist on `origin/launchpad`
and were read in full. The connection pool is a cross-cutting operational facet of
the whole Postgres instance (not one table/domain entity), so `datastore.md` is the
template this node adapts — matching `backup-boundary.md`'s own template choice for
the identical reason (a facet of `architecture-containers-postgres`, not an entity).

`launchpad/docs/corpus/architecture/containers/postgres.md` (`architecture-containers-postgres`)
is merged on `origin/launchpad` and already documents the writer pool's own defaults
(20 max / 2 min connections, 3s acquire timeout, 1800s max lifetime, 600s idle
timeout), the optional lazy read-replica pool, and `BUZZ_DB_POOL_SIZE` /
`BUZZ_DB_READ_POOL_SIZE`. This node is `part-of` that container node and zooms into
the connection-pool facet specifically, without repeating its migration or
partitioning content.

The target file `launchpad/docs/corpus/layers/data/postgres/connection-pool.md`
does not exist on `origin/launchpad` or in this worktree (`test -f` confirmed
`NOT_EXISTS`).

Primary source for the pool's actual shape is already read in full:
`crates/buzz-db/src/lib.rs` (`DbConfig`, `Db::new`, `connect_pool`,
`connect_read_pool`, `DbPoolStats`, `proved_reader`, `has_read_pool`, `pool_stats`,
`read_pool_stats`), `crates/buzz-db/src/replica_fence.rs` (`CREATED_AT_FLOOR_SECS`,
`FENCE_STALENESS`, `read_budget_from_ms`), `crates/buzz-relay/src/config.rs`
(`db_pool_size`, `db_read_pool_size` env parsing), `crates/buzz-relay/src/main.rs`
(`DbConfig` construction, the separate audit and search `PgPoolOptions` pools, the
periodic pool-metrics task), and `.env.example`.

STEP 1 [independent] — Confirm scope and template shape <- RUNS HERE

Re-read issue #1080's body and the sibling Redis issue #1092 to confirm the Postgres
connection pool is this task's whole and only subject, distinct from the Redis pool
(a separate sibling document, not drafted here). Confirm no `layers/data/postgres/*`
sibling from the same overnight batch is merged on `origin/launchpad`.

done when: `git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus`
lists no `layers/data/postgres/*` path, and issue #1080's body has been re-read
directly (not re-derived from Feature #610 or PRD #602).

STEP 2 [needs 1] — Draft the front matter and evidence ledger

Write `id: layers-data-postgres-connection-pool`, `type: layers`, `status: draft`,
`origin: launchpad`, `audiences: [agent, developer, operator, reviewer]` (matching
`backup-boundary.md`'s audience set for the same container facet). One evidence entry
per substantive claim, classified honestly: FACT for anything opened directly in this
session (`crates/buzz-db/src/lib.rs`, `replica_fence.rs`, `crates/buzz-relay/src/config.rs`,
`crates/buzz-relay/src/main.rs`, `.env.example`, `migrations/0021_created_at_fence_floor.sql`,
`architecture-containers-postgres.md`), INFERENCE with `confidence` for reasoned
claims (the `type: layers` disclosure; the pool-is-tenant-blind claim), TEAM_KNOWLEDGE
for the unmerged PR #1875 precedent and issue #1080's own DoD.

done when: every claim in the drafted body has a matching ledger entry and no `FACT`
rests on a source that was not actually opened this session.

STEP 3 [needs 2] — Write the body

Sections: purpose/scope; store classification (the pool is a transport mechanism to
the authoritative store `architecture-containers-postgres` documents, not a store, cache,
or derived projection itself); the pools that exist and who owns each (writer, lazy
reader, audit, search — four separate `PgPoolOptions` instances, only two of them via
`buzz_db::Db`); owned data / access patterns / lifecycle (connection lifetime and
idle-recycling settings, not row data); consistency semantics (the writer's
`after_connect` floor-guard + isolation assertion, the reader's bounded-staleness fence
and `BUZZ_REPLICA_READ_MAX_AGE_MS` clamp); tenancy and security boundaries (the pool
itself is community-blind; credentials externalized via `DATABASE_URL`/
`READ_DATABASE_URL`); failure behavior (writer-connect failure is fatal at boot,
reader-connect is lazy and non-fatal, a saturated reader fails closed to the writer
inside a 150ms budget); configuration surface (every env var, and which of them
`.env.example` does not actually document); implementation/schema/test references;
scope and omissions naming what this node defers to `architecture-containers-postgres`,
the Redis sibling (#1092), and any future migrations/partitioning-specific sibling.

done when: every DoD bullet in issue #1080 is answered by a named section, not
merely implied.

STEP 4 [needs 3] — Validate

Run `python3 launchpad/project-intelligence/corpus/validate.py` from the repository
root, fixing and re-running until it exits 0.

done when: `validate.py` exits 0 against the drafted node.

STEP 5 [needs 4] — Earn the commit gate and commit

As the sole command in its own tool call, run
`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
(bare, unpiped) and confirm `OK`. Only then, in a separate tool call, `git add` the
plan and the document and `git commit -s`.

done when: the unittest run reports `OK` and the commit succeeds without touching the
verify-gate stamp by hand or using `--no-verify`.

PARALLEL

None of these steps are independent of each other in practice — each step's output
is what the next reads — except step 1, which needs nothing and is marked
`[independent]` above.

GATES

- `python3 launchpad/project-intelligence/corpus/validate.py` exits 0.
- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` reports `OK`, run bare (not piped).
- `git commit -s` succeeds without touching the verify-gate stamp by hand.

BUDGET

Single document, single relationship edge, five steps. No code changes — this is a
corpus-documentation task only.

OPEN

- Whether `.env.example`'s omission of `BUZZ_DB_READ_POOL_SIZE` and
  `BUZZ_REPLICA_READ_MAX_AGE_MS` is a deliberate scoping choice or a documentation gap
  was not established — named as a gap in the node's own scope-and-omissions section,
  not resolved.
- The `type: layers` versus `templates/datastore.md`'s own suggested `type: architecture`
  tension is disclosed per this batch's precedent, not resolved by this task.

LEFT OUT

- The Redis connection pool (`layers/data/redis/connection-pool.md`, issue #1092) —
  explicitly a separate sibling document, because issue #1080's own alias header
  scopes this task to `layers/data/postgres/connection-pool.md` only.
- Migration mechanics and partitioning detail — already owned by
  `architecture-containers-postgres.md`; not repeated here.
- Any relationship edge to unmerged `layers/data/postgres/*` siblings from the same
  overnight batch — none are present on `origin/launchpad` at the recorded revision.
