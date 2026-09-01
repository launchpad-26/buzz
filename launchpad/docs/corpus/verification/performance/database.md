---
id: verification-performance-database
type: verification
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 473205a7457b208455f188847bfb27b01aa83cac."
    entry_class: FACT
    evidence:
      - "commit 473205a7457b208455f188847bfb27b01aa83cac"
  - statement: "migrations/0004_events_tags_gin.sql adds `CREATE INDEX idx_events_tags_gin ON events USING GIN (tags jsonb_path_ops)` as its own additive migration, and its own comment states the index was added because the channel-window aux closure's and every other #e fan-out's `tags @> '[[\"e\",\"<hex>\"]]'` JSONB containment lookup, run without an index, measured roughly 900ms per hop on staging -- two sequential hops per scroll-back page, about 1.7s of a roughly 2.1s per-page total -- and names jsonb_path_ops as deliberately narrower and faster than the default jsonb_ops because the query path uses only the `@>` operator."
    entry_class: FACT
    evidence:
      - "migrations/0004_events_tags_gin.sql"
  - statement: "The migration's own comment attributes its ~900ms/hop and ~1.7s/2.1s-page measurements to a document it names RESEARCH/PERF_STAGING_SCROLLBACK; a second, unrelated comment in desktop/src/features/profile/hooks.ts independently cites the same name (as RESEARCH/PERF_STAGING_SCROLLBACK.md) for a related staging measurement about scroll-back payload size; and no file matching that name, with or without a .md extension, exists anywhere in this repository at the recorded revision, so neither measurement is independently corroborated beyond the two comments' own text."
    entry_class: FACT
    evidence:
      - "migrations/0004_events_tags_gin.sql"
      - "desktop/src/features/profile/hooks.ts:343"
      - "grep(-rin, 'PERF_STAGING_SCROLLBACK', repository root) -> migrations/0004_events_tags_gin.sql and desktop/src/features/profile/hooks.ts only; find(-iname 'PERF_STAGING_SCROLLBACK*') -> no file found"
  - statement: "crates/buzz-db/src/store/event.rs's query_events builds the e-tag pushdown clause (JSONB containment, OR-ed across multiple #e tags) and, separately, the shared-gated-visibility pushdown clause (`tags @> '[[\"shared\",\"true\"]]'`), and both clauses' own comments state they are served by idx_events_tags_gin from migration 0004."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/event.rs:501-520"
      - "crates/buzz-db/src/store/event.rs:564-580"
  - statement: "crates/buzz-relay/src/api/bridge.rs defines handle_channel_window_filter, the function migrations/0004_events_tags_gin.sql's own comment names as the caller that fans the e-tag containment lookup out once per retained row."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs:489"
  - statement: "crates/buzz-db/src/runtime/migration.rs's embedded_migrator_contains_consolidated_initial_schema test asserts that the parsed migration set's version-4 entry (migrations[3]) contains the literal text `CREATE INDEX idx_events_tags_gin` and that the version-1 entry (migrations[0], the consolidated initial schema) does not contain it -- proving the index is defined as its own additive migration and is not folded into 0001, and nothing more."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/runtime/migration.rs:688-689"
      - "crates/buzz-db/src/runtime/migration.rs:739-744"
  - statement: "No file under crates/buzz-db, crates/buzz-search, crates/buzz-relay or crates/buzz-test-client contains the case-sensitive string EXPLAIN (the SQL command), and the only .github/workflows files matching 'explain', 'benchmark' or 'perf' case-insensitively are benchmark-harbor.yml (the unrelated Harbor AI-agent leaderboard benchmark) and launchpad-review-agent-publish.yml, so no automated test or CI step in this repository issues EXPLAIN/EXPLAIN ANALYZE against Postgres to confirm the planner actually chooses idx_events_tags_gin for this query, and no automated, CI-gated test measures the e-tag containment query's latency."
    entry_class: FACT
    evidence:
      - "grep(-rn, 'EXPLAIN', crates/buzz-db, crates/buzz-search, crates/buzz-relay, crates/buzz-test-client) -> no matches (case-sensitive)"
      - "grep(-rliE, 'explain|benchmark|perf', .github/workflows) -> benchmark-harbor.yml, launchpad-review-agent-publish.yml only"
      - ".github/workflows/benchmark-harbor.yml"
  - statement: "crates/buzz-test-client/src/bin/wamp_bench.rs is a paced kind:9 load generator that measures end-to-end write-acknowledgement latency against a running relay (and, through it, Postgres), documented in its own module comment as a manual tool invoked with explicit connection/rate/duration arguments; it is not registered in any .github/workflows file and carries no #[test] or #[tokio::test] attribute, so it is not run automatically or gated in CI."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/src/bin/wamp_bench.rs:1-33"
      - "grep(-rl, 'wamp', .github/workflows) -> no matches"
  - statement: "migrations/0001_initial_schema.sql's own comments on the `search_tsv` generated column and `idx_events_search_tsv` GIN index state that the index shape was chosen and confirmed against EXPLAIN during development ('the search lane confirms the final spelling with EXPLAIN before its work lands'; 'avoid btree_gin unless EXPLAIN proves it buys something'), attributed in-line to 'Max' and to 'Quinn option A' -- a distinct obligation, about a different index on the same table, that this node does not adopt as its own subject."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "migrations/0001_initial_schema.sql inline comments (attributed there to Max and to 'Quinn option A')"
  - statement: "crates/buzz-search/tests/fts_integration.rs applies the full FTS-affecting migration chain to a uniquely-named schema per test and exercises full-text search scoping and privacy-kind exclusion scenarios; its own module doc-comment describes it as testing scenarios, not measuring or asserting timing, and it contains no Duration/Instant-based latency assertion."
    entry_class: FACT
    evidence:
      - "crates/buzz-search/tests/fts_integration.rs:1-33"
relationships:
  - type: references
    target: architecture-containers-postgres
---

# Database e-tag containment index — test contract

## Purpose and boundary

This node documents one obligation: that Postgres serves the `events.tags` e-tag
containment lookup used by channel scroll-back and by shared-gated-visibility
filtering through the `idx_events_tags_gin` GIN index added in migration 0004,
rather than falling back to a sequential or bitmap scan across the partitioned
`events` table. It covers that obligation only. It does not cover the full-text
search GIN index over `search_tsv` (a different index, a different migration,
a different obligation -- see *Scope and omissions*), the query-planning
behaviour of any other indexed predicate on `events`, or database performance
for any table other than `events`.

## Obligation

> Postgres serves e-tag containment lookups against `events.tags`
> (`tags @> '[["e","<hex>"]]']`), issued by the channel-window aux closure
> (`handle_channel_window_filter`) and by `query_events`'s shared-gated-visibility
> pushdown, via the `idx_events_tags_gin` GIN index (`jsonb_path_ops`, defined in
> `migrations/0004_events_tags_gin.sql`) rather than a sequential or bitmap scan
> across the `events` partitions.

This is a performance obligation, not a correctness one: the query returns the
same rows with or without the index. What the index exists to guarantee is that
the query stays fast as the `events` table grows, per the motivating measurement
migration 0004's own comment records (see *Limits*).

## Verifying test(s)

- `crates/buzz-db/src/runtime/migration.rs` --
  `embedded_migrator_contains_consolidated_initial_schema` -- asserts that
  migration version 4's SQL text contains the literal
  `CREATE INDEX idx_events_tags_gin` statement, and that migration version 1
  (the consolidated initial schema) does not contain it. This proves the index
  is defined, and defined as its own additive migration rather than folded into
  0001 -- it does **not** exercise a real query against the index, does not run
  `EXPLAIN`, and does not measure latency. It is the only automated test in this
  repository that touches this obligation at all.

No test in this repository issues `EXPLAIN`/`EXPLAIN ANALYZE` against the index,
and no automated, CI-gated benchmark measures the e-tag containment query's
latency. See *Current enforcement status* and *Limits*.

## How to run it

```bash
cargo test -p buzz-db --lib runtime::migration::tests::embedded_migrator_contains_consolidated_initial_schema
```

No infrastructure is required -- the test parses the embedded migration SQL as
text and does not connect to Postgres.

## Current enforcement status

**Pending**, for the obligation as stated above. The only automated coverage is
the DDL-presence check named in *Verifying test(s)*, which runs unconditionally
in CI and currently passes -- but it establishes a narrower claim (the index is
defined, and stays defined as its own migration) than the obligation this node
documents (the planner actually serves the query through that index, and the
query stays fast). Nothing in this repository automates a check of either of
those two things. Claiming "verified" for this obligation on the strength of the
DDL-presence test would be exactly the failure mode *Current enforcement status*
in the test-contract template exists to prevent.

## Limits

What the existing test proves: the `idx_events_tags_gin` index's `CREATE INDEX`
statement is present in migration 4's SQL text and absent from migration 1's,
at every commit that passes CI. That is a real, currently-enforced guarantee
against the index silently disappearing or being folded into the initial
schema (which would break brownfield migration checksums), and nothing more.

What no test in this repository proves, today:

- That Postgres's query planner actually chooses `idx_events_tags_gin` for the
  `tags @> ...` containment queries in `query_events`, on any schema shape or
  data volume, rather than a sequential or bitmap-heap scan.
- That the e-tag containment query's latency is below any stated bound, on any
  data volume, in CI or anywhere else automated.
- The ~900ms-per-hop / ~1.7s-of-~2.1s-per-page measurement migration 0004's own
  comment cites as its motivation. That measurement is quoted from the
  migration's comment only; the document it names as its source
  (`RESEARCH/PERF_STAGING_SCROLLBACK`) does not exist anywhere in this
  repository at the recorded revision, so the number could not be independently
  re-derived while authoring this node.
- Anything about query performance on a schema whose partition layout,
  row counts, or Postgres version differ materially from what production or
  staging looked like when migration 0004 was written.

## Scope and omissions

**This node covers** the `idx_events_tags_gin` GIN index's obligation to serve
`events.tags` e-tag containment lookups, the one existing test that touches it,
and that test's real (narrower) coverage versus the obligation as stated.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The full-text search GIN index over `events.search_tsv` (`idx_events_search_tsv`, migration 0001) -- a distinct index, distinct obligation, on the same table, whose own migration comments record it was shaped against `EXPLAIN` during development ("Max's caveat: avoid btree_gin unless EXPLAIN proves it buys something") | Not yet a corpus node; a candidate for a sibling `verification/performance/*` task, not folded into this one per the one-node-one-idea rule |
| `crates/buzz-search/tests/fts_integration.rs`, which tests full-text search scoping and privacy-kind exclusion correctness, not performance | `launchpad/docs/corpus/capabilities/search/full-text-search.md` and `capabilities/search/search-index.md` |
| `crates/buzz-test-client/src/bin/wamp_bench.rs`, a manual, non-CI-gated write-amplification load generator that measures end-to-end relay latency (and, indirectly, Postgres write latency) but is not scoped to this obligation and asserts nothing | Not a corpus node at this revision |
| The other community-leading btree indexes on `events` (`idx_events_community_id`, `idx_events_community_channel_created`, and siblings) and their own performance rationale | Not yet a corpus node |
| Whether Postgres actually chooses `idx_events_tags_gin` on the current production or staging schema -- no `EXPLAIN` was run against a live database while authoring this node; every claim above about planner behaviour is stated as an obligation still to be verified, never as an observed fact | pending automated coverage, as stated above |

**Relationships.** `origin/launchpad`'s corpus tree at the recorded revision
carries `architecture-containers-postgres` (`launchpad/docs/corpus/architecture/containers/postgres.md`),
which this node cites via a `references` edge: that node describes Postgres as
the connected datastore this obligation concerns, and this node adds no
ownership or currency dependency on it beyond that context. No other corpus
node at the recorded revision names the `events.tags` GIN index, the
`query_events` e-tag pushdown, or a full-text-search sibling obligation, so no
further edge was found to add; `git ls-tree -r --name-only origin/launchpad --
launchpad/docs/corpus` was the check run to confirm that.
