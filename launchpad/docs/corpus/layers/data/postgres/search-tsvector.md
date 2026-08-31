---
id: layers-data-postgres-search-tsvector
type: layers
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - operator
evidence:
  - statement: "This node was authored and checked against repository revision 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5."
    entry_class: FACT
    evidence:
      - "commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
  - statement: "migrations/0001_initial_schema.sql defines events.search_tsv as `TSVECTOR GENERATED ALWAYS AS (CASE WHEN kind IN (1059, 30300, 30622, 44100, 44101) THEN NULL::tsvector ELSE to_tsvector('simple', content) END) STORED`, and the column's own comment states the 'simple' text-search configuration was chosen deliberately ('no stemming/stopwords, matching the existing substring-ish search semantics') and that the column is 'Generated/STORED so it is a single source of truth — no sidecar indexer to keep coherent (Quinn option A, Lane-0 call)'."
    entry_class: FACT
    evidence:
      - "migrations/0001_initial_schema.sql:190-226"
  - statement: "The same migration creates `idx_events_search_tsv ON events USING GIN (search_tsv)` as a minimal single-column GIN index, with its own comment stating that community/tenant scoping is supplied separately by the community-leading btree indexes 'BitmapAnd-ed with the GIN probe,' so the GIN index itself carries no tenant column."
    entry_class: FACT
    evidence:
      - "migrations/0001_initial_schema.sql:274-278"
  - statement: "crates/buzz-search/src/lib.rs's own module doc states: 'The index lives in the events table: search_tsv TSVECTOR GENERATED ALWAYS AS (to_tsvector('simple', content)) STORED, with GIN (search_tsv) as the access path. Because the column is GENERATED ALWAYS, every row write *is* the index update — there is no separate indexer, no mpsc queue, no reindex job, no consistency window to reason about. A client cannot forge the tsvector out of sync with the content it signed.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-search/src/lib.rs:1-15"
  - statement: "crates/buzz-db/src/event.rs's insert_event function's INSERT statement names exactly twelve columns (community_id, id, pubkey, created_at, kind, tags, content, sig, received_at, channel_id, d_tag, not_before); search_tsv does not appear in that column list, confirming the Rust write path never supplies a value for it — Postgres computes it from `content` and `kind` as part of the same statement."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/event.rs:273-322"
  - statement: "migrations/0005_agent_turn_metric_fts.sql's own comment states 'PostgreSQL cannot alter a generated expression in place' and that the migration must 'DROP the generated column and re-ADD it with the extended exclusion list,' adding kind 44200 (agent turn metrics, NIP-44 ciphertext) to the exclusion set because indexing that ciphertext 'would waste storage and violate the spec's \"NOT index the event in any full-text search\" requirement.'"
    entry_class: FACT
    evidence:
      - "migrations/0005_agent_turn_metric_fts.sql"
  - statement: "migrations/0008_fresh_install_search_allowlist.sql takes a table-level SHARE ROW EXCLUSIVE lock, checks `NOT EXISTS (SELECT 1 FROM events LIMIT 1)`, and only for a genuinely empty table replaces search_tsv's generated expression with a positive allowlist — `CASE WHEN kind IN (0, 9, 40002, 45001, 45003) THEN to_tsvector('simple', content) ELSE NULL::tsvector END` — while its own comment states populated databases 'keep their current search_tsv expression until an operator runs the sized out-of-band maintenance script in scripts/maintenance/nip_rs_search_allowlist.sql.'"
    entry_class: FACT
    evidence:
      - "migrations/0008_fresh_install_search_allowlist.sql"
  - statement: "scripts/maintenance/nip_rs_search_allowlist.sql is explicitly commented 'OUT-OF-BAND MAINTENANCE: do not run from relay startup migrations,' rewrites every partition and rebuilds the GIN index with the same positive-allowlist expression migration 0008 gives fresh installs, and warns 'ALTER TABLE takes ACCESS EXCLUSIVE, so event reads and writes block until this transaction commits' — an operator-run, not automatic, step for any database that was already populated when migration 0008 ran."
    entry_class: FACT
    evidence:
      - "scripts/maintenance/nip_rs_search_allowlist.sql"
  - statement: "migrations/0014_push_lease_fts.sql reads the column's *currently installed* generated expression via `pg_get_expr(d.adbin, d.adrelid)` joined against `pg_attrdef`/`pg_attribute`, then replaces the column with that same captured expression wrapped in one more exclusion (`CASE WHEN kind = 30350 THEN NULL::tsvector ELSE (<captured>) END`) — its own comment states 'PostgreSQL cannot alter a generated expression in place. Capture the current expression before replacing the column, then wrap it with the new exclusion. This preserves both the fresh-install allowlist and any brownfield/operator-managed expression for every kind other than 30350.'"
    entry_class: FACT
    evidence:
      - "migrations/0014_push_lease_fts.sql"
  - statement: "Because migration 0008 only rewrites an empty table and migration 0014 explicitly preserves whichever shape a database already had, a database that was already populated when 0008 ran keeps the original exclusion-list expression (searchable by default, denylisted by kind) unless an operator manually runs scripts/maintenance/nip_rs_search_allowlist.sql, while a database that was empty at 0008-time runs the positive-allowlist expression (unsearchable by default, allowlisted by kind) from that point on — two structurally different search_tsv generation rules can coexist across real deployments of this repository's own migration set, not merely as a historical artifact."
    entry_class: INFERENCE
    evidence:
      - "migrations/0001_initial_schema.sql"
      - "migrations/0005_agent_turn_metric_fts.sql"
      - "migrations/0008_fresh_install_search_allowlist.sql"
      - "migrations/0014_push_lease_fts.sql"
      - "scripts/maintenance/nip_rs_search_allowlist.sql"
    confidence: 0.85
  - statement: "crates/buzz-db/src/migration.rs's run_migrations_applies_consolidated_initial_schema_on_fresh_database test reads the post-migration search_tsv generated expression back from pg_attrdef on a freshly migrated database and asserts it contains 'ARRAY[0, 9, 40002, 45001, 45003]' — confirming the fresh-install allowlist kinds directly against a running migration, not merely against the maintenance script's own text."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/migration.rs:1954-1968"
  - statement: "crates/buzz-core/src/kind.rs names the fresh-install allowlist's five kinds: KIND_PROFILE = 0, KIND_STREAM_MESSAGE = 9 (the NIP-29 group chat message kind), KIND_STREAM_MESSAGE_V2 = 40002, KIND_FORUM_POST = 45001, and KIND_FORUM_COMMENT = 45003."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs:9"
      - "crates/buzz-core/src/kind.rs:474-481"
      - "crates/buzz-core/src/kind.rs:549-554"
  - statement: "crates/buzz-core/src/kind.rs's own doc comment for P_GATED_KINDS states that for stored (non-ephemeral) kinds in that set, 'the storage layer additionally writes a NULL search_tsv so the event is unsearchable through NIP-50 FTS (schema/schema.sql and migrations/0001_initial_schema.sql — drift caught by p_gated_persistent_kinds_have_storage_null_tsvector in crates/buzz-search/tests/fts_integration.rs).'"
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs:144-169"
  - statement: "crates/buzz-search/tests/fts_integration.rs's p_gated_persistent_kinds_have_storage_null_tsvector test's own doc comment states it is a tripwire: 'every Rust-side P_GATED_KINDS entry that is persistent ... MUST be excluded from search_tsv at the storage layer,' and that 'the L1 NULL tsvector is the unbreakable backstop: @@ mathematically cannot match NULL,' distinct from the Rust-logic-dependent L2 filter-level #p gate; a companion test, author_only_kinds_are_storage_level_unsearchable, covers the same drift for AUTHOR_ONLY_KINDS."
    entry_class: FACT
    evidence:
      - "crates/buzz-search/tests/fts_integration.rs:1329-1400"
      - "crates/buzz-search/tests/fts_integration.rs:1403-1497"
  - statement: "crates/buzz-core/src/kind.rs defines AUTHOR_ONLY_KINDS as exactly KIND_EVENT_REMINDER (30300), KIND_PUSH_LEASE (30350), and KIND_PRIVATE_MANAGED_AGENT (30179)."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs:129-133"
  - statement: "Grepping every migration that touches search_tsv (0001, 0005, 0008, 0014) and the maintenance script for the literal '30179' finds no occurrence — KIND_PRIVATE_MANAGED_AGENT is the one AUTHOR_ONLY_KINDS member never added to any exclusion or allowlist expression that governs search_tsv, while its AUTHOR_ONLY_KINDS siblings (KIND_EVENT_REMINDER since migration 0001, KIND_PUSH_LEASE since migration 0014) both are."
    entry_class: FACT
    evidence:
      - "grep(30179, migrations/*.sql crates/buzz-search/**) -> no match"
      - "migrations/0001_initial_schema.sql"
      - "migrations/0014_push_lease_fts.sql"
  - statement: "Whether KIND_PRIVATE_MANAGED_AGENT's absence from every search_tsv exclusion/allowlist expression is a deliberate scoping choice — its content is described as 'NIP-44 v2 encrypted from the owner's key to itself' in its own doc comment, so tokenizing that ciphertext with to_tsvector would not expose plaintext even though the row would remain SQL-matchable — or an unnoticed gap parallel to the one migration 0005 closed for a different NIP-44-encrypted kind (KIND_AGENT_TURN_METRIC, whose migration comment states indexing its ciphertext 'would waste storage and violate the spec's \"NOT index the event in any full-text search\" requirement') was not established in this session."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-core/src/kind.rs:111-118"
      - "migrations/0005_agent_turn_metric_fts.sql"
    confidence: 0.4
  - statement: "crates/buzz-search/src/query.rs's search function's own doc comment gives the query's fixed SQL shape, including 'WHERE community_id = $ctx AND deleted_at IS NULL AND search_tsv @@ query [+ channel scope, kinds, authors, since, until]', and states plainly: 'community_id = $ctx is the first predicate and is non-negotiable. There is no code path through this function that omits it.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-search/src/query.rs:200-217"
  - statement: "query.rs's push_tsquery function builds `websearch_to_tsquery('simple', ...)` for SearchMode::FullText, and for SearchMode::Prefix instead hand-builds a tsquery from `regexp_split_to_table` over whitespace-delimited raw tokens run back through `to_tsvector('simple', ...)`, suffixing only the trailing token with `:*` — a doc comment on SearchMode::Prefix states this mode is 'Intended for bounded typeahead surfaces such as the desktop topbar,' and that 'the relay still refetches and re-authorizes every hit; this mode changes only the candidate tsquery, not the access boundary.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-search/src/query.rs:57-68"
      - "crates/buzz-search/src/query.rs:142-198"
  - statement: "query.rs's own module doc states: 'The relay never trusts a hit by itself: this layer returns canonical event ids ordered by relevance, the relay refetches StoredEvents through buzz-db's (community_id, event_id) scoped fetcher, and runs the access predicate (search_hit_accepted in bridge.rs) per hit. Search is never the access boundary — it cannot widen visibility.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-search/src/query.rs:1-9"
  - statement: "crates/buzz-relay/src/main.rs's own comment at the point it constructs the search connection pool states: 'Postgres FTS: the searchable row IS the persisted event row (its tsvector column is populated by the insert_event write), so there is no external collection to provision — the search service just queries the same Postgres over its own pool. Search is lag-tolerant, so it prefers the read replica when one is configured,' and the code binds `search_db_url` to `config.read_database_url` when set, falling back to `config.database_url` otherwise."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:404-419"
  - statement: "crates/buzz-search/src/query.rs's search function carries a #[datastore_span(name = \"search\", system = \"postgresql\")] attribute from buzz-datastore-tracing, the same privacy-preserving tracing policy macro used elsewhere in this repository's Postgres call sites, which per its own crate doc omits function arguments and exposes only canonical semantic fields plus explicitly supplied safe fields."
    entry_class: FACT
    evidence:
      - "crates/buzz-search/src/query.rs:218-219"
  - statement: "crates/buzz-relay/src/handlers/req.rs's handle_search_req calls `state.search.search(&search_query).await`, and on `Err(e)` logs `warn!(sub_id = %sub_id, \"NIP-50 search failed: {e}\")` and `break`s out of the per-filter pagination loop, rather than closing the subscription or surfacing an error message to the client — a search_tsv-backed query failure silently stops returning further results for that filter instead of tearing down the connection."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs:689-695"
  - statement: "scripts/maintenance/nip_rs_search_allowlist.sql sets `SET LOCAL lock_timeout = '5s'` before its ALTER TABLE/DROP+ADD COLUMN sequence, so if the required ACCESS EXCLUSIVE lock cannot be acquired within 5 seconds (for example, a long-running query or transaction still holding the events table), the maintenance transaction aborts with a lock-timeout error rather than blocking indefinitely against live traffic."
    entry_class: FACT
    evidence:
      - "scripts/maintenance/nip_rs_search_allowlist.sql:9"
  - statement: "launchpad/docs/corpus/architecture/flows/search-query.md, id architecture-flows-search-query, merged and validated on origin/launchpad, already documents the end-to-end request flow that reaches this column (the WebSocket REQ and HTTP POST /query entry points, tenant/auth resolution, the sensitive-kind gate ordering ahead of the search branch, and the same search_tsv @@ query mechanics cited above) at the flow level; this node does not restate that flow and instead declares a references relationship to it."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/flows/search-query.md"
  - statement: "launchpad/docs/corpus/architecture/containers/postgres.md, id architecture-containers-postgres, type: architecture, status: draft, is merged and validated on origin/launchpad and is the container-level node for the Postgres instance the events table (and this column) physically live inside."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/containers/postgres.md"
  - statement: "At the checked revision, git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus contains no layers/ subtree at all; layers-data-postgres-events-table (issue #1081, PR #1876) and its four batch-5 siblings, and every other layers/data/... document from issues #1060-#1084 (PRs #1872-#1876), are open, draft, and unmerged (checked directly with gh pr view, not assumed) — none is a valid relationships target under AGENTS.md's node-creation step 9."
    entry_class: FACT
    evidence:
      - "git_ls_tree(origin/launchpad, launchpad/docs/corpus) -> no layers/ path present"
      - "gh_pr_view(1876) -> state OPEN, isDraft true, mergedAt null"
      - "gh_pr_view(1873) -> state OPEN, isDraft true, mergedAt null"
  - statement: "layers-data-postgres-events-table's own (unmerged) draft documents the events table's row-level identity, full column shape, and cross-row invariants, and covers search_tsv only as one row of its own column-attribute table, citing migrations/0001_initial_schema.sql:190-224 alone; it does not cover the column's later migrations, the fresh-install/brownfield discrepancy, the security tripwire tests, or the query-side mechanics this node documents, so this node does not duplicate it and is not linked to it (unmerged)."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1876 (open, draft PR, layers-data-postgres-events-table), read directly via gh pr diff"
  - statement: "This batch's overnight corpus-batch-author dispatch brief for Feature #610 directs every layers/data/... document to carry type: layers, overriding the data-entity template's own worked reasoning that a real instance 'most plausibly takes type: implementation' — this node follows that batch-level precedent, already applied by the sibling layers-data-postgres-events-table node, rather than the template's own suggestion, and discloses the override here per standards/taxonomy.md's 'say so in the node's own scope-and-omissions section' rule."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "overnight corpus-batch-author dispatch brief for Feature #610 (task-1089-search-tsvector batch instructions); precedent also visible in launchpad-26/buzz#1876's layers-data-postgres-events-table"
  - statement: "Issue #1089's definition of done requires this node to state whether the store is authoritative, derived, cache or transport; describe owned data, key access patterns, lifecycle/retention and consistency semantics; name tenancy/security boundaries and failure behavior; and link schema/migrations/code/tests rather than copy DDL, in addition to the generic one-document, schema-valid, evidence-traceable, non-duplicating, revision-checked, validate.py-clean requirements shared by every corpus task."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1089 definition of done"
relationships:
  - type: part-of
    target: architecture-containers-postgres
  - type: references
    target: architecture-flows-search-query
---

# `events.search_tsv` — the Postgres full-text search column

The generated `tsvector` column and its GIN index that back Buzz's NIP-50
full-text search. This node documents the column itself: what generates it,
how that generation rule has evolved across migrations, what it excludes and
why, how `buzz-search` queries it, and what consistency and failure guarantees
it actually has. It does not document the `events` table as a whole — identity,
full column shape, and cross-row invariants for that table belong to
`layers-data-postgres-events-table` (issue #1081, not yet merged), which this
node names in prose but does not link to. It does not document the container
Postgres instance itself (`architecture-containers-postgres`, linked below via
`part-of`) or the end-to-end request flow that reaches this column
(`architecture-flows-search-query`, linked below via `references`).

## Classification: derived, not authoritative, cache, or transport

`search_tsv` is a **derived** index, not an authoritative store, a cache, or a
transport mechanism. The column is declared `TSVECTOR GENERATED ALWAYS AS
(...) STORED` on the `events` table itself — Postgres computes its value from
`content` (and gates it by `kind`) as part of every row write, and no code
path writes to it directly: `insert_event`'s own `INSERT` statement names
twelve columns and `search_tsv` is not one of them. `content` is the
authoritative source; `search_tsv` is a projection of it that cannot exist
independently of its row.

It is not a **cache** in the usual sense — there is no TTL, no invalidation
path, and no possibility of it going stale relative to its own row, because
Postgres recomputes it synchronously at write time rather than asynchronously
after the fact. `buzz-search`'s own module doc states this directly: "every
row write *is* the index update — there is no separate indexer, no mpsc
queue, no reindex job, no consistency window to reason about." It is not a
**transport** mechanism either — it never leaves Postgres as a distinct
message or event; it is read only via SQL predicates (`search_tsv @@ query`)
issued against the same table.

## Generation rule and its evolution

The base expression, unchanged since the initial schema, is:

```sql
search_tsv TSVECTOR GENERATED ALWAYS AS (
    CASE WHEN kind IN (<excluded kinds>) THEN NULL::tsvector
         ELSE to_tsvector('simple', content)
    END
) STORED
```

`'simple'` is a deliberate choice, not a default left unexamined: the initial
migration's own comment states it was picked so the search behavior matches
"the existing substring-ish search semantics," explicitly leaving room for a
future, evidence-backed change of configuration. Only `content` is indexed —
`tags` (the NIP-01 tag array) is never folded into `search_tsv`.

Postgres cannot `ALTER` a generated column's expression in place, so every
change to the kind list is a `DROP COLUMN` + `ADD COLUMN` + index rebuild, a
constraint each migration's own comment names explicitly rather than treating
as incidental. Four migrations touch this column at the checked revision:

| Migration | What changed |
|---|---|
| `0001_initial_schema.sql` | Establishes the column and its initial exclusion list (kinds 1059, 30300, 30622, 44100, 44101 — privacy-sensitive kinds get `NULL::tsvector`). |
| `0005_agent_turn_metric_fts.sql` | Adds kind 44200 (`KIND_AGENT_TURN_METRIC`, NIP-44 encrypted) to the exclusion list, "to not waste storage and to comply with the spec's 'NOT index' requirement" for that kind's ciphertext. |
| `0008_fresh_install_search_allowlist.sql` | Under a table-level lock and an emptiness check, replaces the expression with a **positive allowlist** (only kinds 0, 9, 40002, 45001, 45003 are indexed) — but only for a database with zero existing events. Populated databases are left untouched by this migration. |
| `0014_push_lease_fts.sql` | Reads back whichever expression a database currently has (via `pg_attrdef`/`pg_get_expr`) and wraps it with one more exclusion (kind 30350), preserving the fresh-install allowlist shape or the brownfield exclusion-list shape, whichever the database already had. |

An operator-run, out-of-band script, `scripts/maintenance/nip_rs_search_allowlist.sql`
(explicitly commented "do not run from relay startup migrations"), performs
the same rewrite migration 0008 gives fresh installs, for a database that was
already populated when 0008 ran. Its own comment warns the `ALTER TABLE`
step "takes ACCESS EXCLUSIVE, so event reads and writes block until this
transaction commits" — this is why it is a manual maintenance-window step
rather than something startup migrations attempt automatically.

## Consistency semantics: two live shapes can coexist

Because migration 0008 only rewrites an *empty* table and migration 0014
explicitly preserves whichever shape a database already had, two structurally
different `search_tsv` generation rules can be live simultaneously across
real deployments of this same migration set:

- A database that was already populated when migration 0008 ran keeps the
  original **exclusion-list** shape: searchable by default, with a growing
  denylist of privacy-sensitive kinds.
- A database that was empty at that point runs the **allowlist** shape from
  then on: unsearchable by default, with only five kinds
  (`KIND_PROFILE`, `KIND_STREAM_MESSAGE`, `KIND_STREAM_MESSAGE_V2`,
  `KIND_FORUM_POST`, `KIND_FORUM_COMMENT`) ever indexed.

Both shapes are legitimate outcomes of applying the same, unmodified
migration files in order — this is not documentation drift the way a stale
`.env.example` entry would be; it is a real, currently-live divergence
between deployments, closed only by an operator choosing to run the
maintenance script. `crates/buzz-db/src/migration.rs`'s own test suite
confirms the allowlist shape directly by reading `pg_attrdef` back off a
freshly migrated database and asserting it contains
`ARRAY[0, 9, 40002, 45001, 45003]`.

Beyond the column itself, `crates/buzz-relay/src/main.rs` wires the search
service's connection pool to prefer `config.read_database_url` when one is
configured, falling back to the primary otherwise, with its own comment
stating "Search is lag-tolerant, so it prefers the read replica when one is
configured." A `search_tsv` value is therefore always exactly consistent with
its own row at the primary (write time), but a search query answered from a
configured read replica can observe a row — and its `search_tsv` — slightly
behind the primary's current state, a deliberate, named trade-off rather than
an oversight.

## Tenancy and security boundaries

**Tenancy.** Every `buzz_search::query::search` call binds `community_id =
$ctx` as its own first SQL predicate, with (per the function's own doc
comment) "no code path through this function that omits it." The GIN index
over `search_tsv` itself carries no tenant column — tenant scoping is
supplied by Postgres combining the community-leading btree indexes with the
GIN probe (`BitmapAnd`), per the initial migration's own comment, so the GIN
index stays a minimal single-column index rather than a composite one.

**Security — a two-layer defense for sensitive kinds.** Kinds in
`AUTHOR_ONLY_KINDS` (`KIND_EVENT_REMINDER`, `KIND_PUSH_LEASE`,
`KIND_PRIVATE_MANAGED_AGENT`) and the persistent members of `P_GATED_KINDS`
(kinds whose reads are `#p`-tag-gated at the filter layer) are meant to be
storage-level unsearchable via a `NULL` `search_tsv`, so that `@@` — which
can never match `NULL` — is a backstop independent of any Rust-side
filtering logic. `crates/buzz-core/src/kind.rs`'s own doc comment for
`P_GATED_KINDS` names this explicitly, and two tripwire integration tests
(`author_only_kinds_are_storage_level_unsearchable`,
`p_gated_persistent_kinds_have_storage_null_tsvector`) assert it directly
against a running Postgres, failing if a future migration adds a
privacy-sensitive kind to one of the Rust-side constant lists without a
matching schema exclusion.

**A gap this session found and did not resolve.** `KIND_PRIVATE_MANAGED_AGENT`
(30179) is an `AUTHOR_ONLY_KINDS` member whose sibling kinds
(`KIND_EVENT_REMINDER` since the initial migration, `KIND_PUSH_LEASE` since
migration 0014) are both excluded from `search_tsv` — but grepping every
migration and the maintenance script that touches this column for `30179`
finds no occurrence. Its content is NIP-44 v2 encrypted to its own owner, so
tokenizing that ciphertext with `to_tsvector` would not expose plaintext —
but migration 0005 closed exactly this shape of gap for a different
NIP-44-encrypted kind (`KIND_AGENT_TURN_METRIC`), reasoning that indexing
ciphertext "would waste storage and violate the spec's ... requirement," not
purely a plaintext-exposure argument. Whether the omission for
`KIND_PRIVATE_MANAGED_AGENT` is a considered choice or an unnoticed gap is
not established here.

## Access patterns

`crates/buzz-search/src/query.rs`'s `search` function is the only code path
that reads `search_tsv`. It is reached from exactly two client entry points —
a WebSocket `REQ` with a `search` filter and an HTTP `POST /query` request —
both documented end-to-end (tenant resolution, auth, the sensitive-kind gate
ordering) by `architecture-flows-search-query`, linked below rather than
restated here. `search` issues `search_tsv @@ query`, where `query` is built
by `websearch_to_tsquery('simple', ...)` for ordinary search
(`SearchMode::FullText`) or a hand-built prefix `tsquery` — the trailing
whitespace-delimited token re-tokenized and suffixed `:*` — for bounded
typeahead surfaces (`SearchMode::Prefix`). The function's own doc comment
states the layer's access contract plainly: it returns canonical event ids
ordered by relevance only; the relay refetches full events through a
community-scoped fetcher and re-authorizes each hit; search "is never the
access boundary — it cannot widen visibility." The `search` function itself
carries a `#[datastore_span(name = "search", system = "postgresql")]`
tracing attribute, the same privacy-preserving instrumentation policy this
repository applies to its other Postgres call sites.

## Failure behavior

**Query-time failure fails soft, not closed.** On the WebSocket path,
`handle_search_req` calls `state.search.search(...)` per filter; if that call
returns an `Err` (any underlying `sqlx`/Postgres error, wrapped by
`SearchError::Db`), the handler logs a `warn!` and `break`s out of that
filter's pagination loop. The client's subscription is not closed and no
error is sent back — a `search_tsv`-backed query failure simply stops
producing further results for the affected filter rather than tearing down
the connection or surfacing a protocol-level error.

**Schema-change failure fails closed, not silently.** The out-of-band
maintenance script that moves a brownfield database onto the allowlist
expression sets `SET LOCAL lock_timeout = '5s'` before attempting its
`ALTER TABLE`. If the required `ACCESS EXCLUSIVE` lock cannot be acquired
within five seconds — for example, a long-running query still holding the
`events` table — the transaction aborts with a lock-timeout error rather than
blocking indefinitely against live traffic; the column is left exactly as it
was, and an operator must retry once contention clears.

## Lifecycle and retention

`search_tsv` has no lifecycle independent of its own row: it is created,
updated (there is no update path — the value is fixed at insert time for a
given row's `content`/`kind`), and removed exactly when its row is. Because
`events` deletion in this repository is soft (`deleted_at` set, not a SQL
`DELETE`), a soft-deleted row's `search_tsv` value is not immediately
reclaimed either — it remains part of the row and its GIN index entry until
whatever process ultimately removes the row (partition retention, hard
deletion), which this node does not itself document. There is no separate
TTL, expiry, or reindex schedule for the column; its only lifecycle event is
the DROP+ADD COLUMN rewrite a schema migration performs across every row at
once, described above.

## Scope and omissions

**This document covers** the `search_tsv` column's generation rule and its
migration history, its classification as a derived (not authoritative, cache,
or transport) index, its tenancy and security boundaries, its access
pattern through `buzz-search`, its consistency semantics (including the
live fresh-install/brownfield divergence and read-replica lag-tolerance), and
its lifecycle relative to its own row.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The `events` table's own identity, full column shape, and cross-row invariants | `layers-data-postgres-events-table` (issue #1081, PR #1876, unmerged at this node's checked revision) |
| The wire-level meaning of any one event kind's `tags`/`content` | That kind's own future event-kind (`interfaces-events`) node |
| The end-to-end search request flow (WS/HTTP entry points, auth, sensitive-kind gate ordering ahead of the search branch) | `architecture-flows-search-query` (merged; linked above via `references`) |
| Postgres's own operational profile as a container (connection pooling generally, replication topology, backup posture) | `architecture-containers-postgres` (merged; linked above via `part-of`), and any future Postgres datastore-level node |
| Partition retention and how/when soft-deleted rows (and their `search_tsv` values) are actually reclaimed | Not established in this session; a future retention-focused node's job |
| The evidence-class contract, `confidence`'s meaning, decision-reference citation mechanics | `launchpad/docs/corpus/AGENTS.md`, `launchpad/docs/corpus/standards/confidence.md`, `launchpad/docs/corpus/standards/decision-references.md` |

**`type: layers` is a disclosed override, not the data-entity template's own
suggestion.** The data-entity template's own reasoning would point at
`type: implementation`; this node follows this batch's precedent instead
(see the TEAM_KNOWLEDGE evidence entry above), the same override the sibling
`layers-data-postgres-events-table` node already discloses for itself.

**No relationship to any `layers/data/...` sibling.** Every document from
issues #1060-#1084, including `layers-data-postgres-events-table` (#1081) and
`layers-data-derived-data` (#1065, which discusses `search_tsv` as one
worked example of the general derived/generated-column concept), is open and
unmerged at this node's checked revision (confirmed directly with `gh pr
view`, not assumed) — `AGENTS.md`'s node-creation step 9 forbids targeting a
node that does not exist on the branch being merged into. Both are named in
prose above and would be reasonable `references` targets once merged.

**Expected but not verified when this node was written:**

- **Whether `KIND_PRIVATE_MANAGED_AGENT`'s absence from every `search_tsv`
  exclusion/allowlist expression is deliberate or an unnoticed gap** was not
  established — named directly above as a real, checked finding rather than
  smoothed over either way.
- **Whether an open issue already tracks the fresh-install/brownfield
  `search_tsv` divergence** was not searched for exhaustively; the divergence
  itself is verified directly against the migration files and is named here
  regardless of whether a tracking issue exists.
- **How and when partition retention actually reclaims a soft-deleted row**
  (and therefore its `search_tsv` entry) was not located in this session's
  reading and is left to a future node.
- **Whether any code path outside `crates/buzz-db/src/event.rs` writes to the
  `events` table's other columns in a way that could indirectly affect
  `search_tsv`** (for example, an `UPDATE` to `content`, if one exists
  anywhere) was not exhaustively searched for; `content` appears immutable in
  every write path this session located, but that is not asserted as a
  complete inventory of every call site in the repository.
