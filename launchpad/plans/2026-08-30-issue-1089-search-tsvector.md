# Plan: document layers/data/postgres/search-tsvector.md (#1089)

Issue #1089 carries no explicit Size line in its body.

Stated size: not stated in issue body -> cap: 5 steps (overnight batch dispatch instruction caps this task at 5 steps)

ALREADY TRUE

- Worktree `__worktrees/task-1089-search-tsvector` exists on branch
  `task/1089-search-tsvector`, based on `origin/launchpad` at
  `338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5`.
- Issue #1089's body confirms the target path:
  `launchpad/docs/corpus/layers/data/postgres/search-tsvector.md`, and its DoD
  requires stating whether the store is authoritative/derived/cache/transport;
  describing owned data, access patterns, lifecycle/retention, consistency
  semantics; naming tenancy/security boundaries and failure behavior; and
  linking schema/migrations/code/tests rather than copying DDL.
- `git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus`
  carries no `layers/` subtree yet — every `layers/data/...` sibling
  (`#1060`-`#1084` batches, PRs #1872-#1876) is open and unmerged. No
  relationship in this node may target any of them.
- `architecture-containers-postgres` and `architecture-flows-search-query` are
  both merged, validated nodes on `origin/launchpad` — legitimate
  `relationships` targets.
- `search_tsv` is defined in `migrations/0001_initial_schema.sql:222-226`
  (`TSVECTOR GENERATED ALWAYS AS (...) STORED`) and evolved by
  `migrations/0005_agent_turn_metric_fts.sql`,
  `migrations/0008_fresh_install_search_allowlist.sql`, and
  `migrations/0014_push_lease_fts.sql`; `crates/buzz-search/src/query.rs` and
  `crates/buzz-search/src/lib.rs` are the query side; `crates/buzz-db/src/event.rs`'s
  `insert_event` never writes the column directly (checked against its own
  `INSERT` column list); `crates/buzz-search/tests/fts_integration.rs` carries
  two tripwire tests (`author_only_kinds_are_storage_level_unsearchable`,
  `p_gated_persistent_kinds_have_storage_null_tsvector`) proving the
  privacy-exclusion invariant; `crates/buzz-relay/src/main.rs:405-416` wires
  the search pool to prefer the read replica ("Search is lag-tolerant").
- A real, evidence-checked gap exists: `KIND_PRIVATE_MANAGED_AGENT` (30179) is
  in `AUTHOR_ONLY_KINDS` (`crates/buzz-core/src/kind.rs:129-133`) but is not
  present in any `search_tsv` exclusion/allowlist expression across the four
  migrations that touch the column — grepped directly, not assumed.
- Sibling `layers-data-postgres-events-table` (issue #1081, PR #1876, open and
  unmerged) already documents the `events` table's identity/attributes/
  invariants and mentions `search_tsv` only as one row of its attribute table,
  citing `migrations/0001_initial_schema.sql:190-224` alone — it does not cover
  the column's own migration evolution, the fresh-install/brownfield
  discrepancy, the tripwire tests, or the query-side mechanics. This node does
  not restate events-table's content and is not linked to it (unmerged).

STEP 1 — Draft the corpus document [independent]

Create `launchpad/docs/corpus/layers/data/postgres/search-tsvector.md`.

Front matter: `id: layers-data-postgres-search-tsvector`, `type: layers`
(disclosed override of the data-entity template's own `type: implementation`
suggestion, per the batch precedent already set by `events-table.md` and
`standards/taxonomy.md`'s disclosure rule), `status: draft`, `origin: launchpad`,
`audiences: [agent, developer, operator]`, an evidence ledger with a commit
citation for `338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5` plus one entry per
substantive claim below, and `relationships: [part-of ->
architecture-containers-postgres, references -> architecture-flows-search-query]`.

<-- RUNS HERE

Body sections (data-entity template shape, adapted — search_tsv is a generated
column/derived index, not a domain entity with independent identity):

1. Purpose & scope — names the events table it lives on (prose-only mention of
   `layers-data-postgres-events-table`, #1081, unmerged, not linked), the
   container it lives inside (`architecture-containers-postgres`, linked), and
   states explicitly this document is scoped to the `search_tsv` mechanism,
   not a restatement of the whole `events` row.
2. Classification — states plainly: DERIVED, not authoritative/cache/transport,
   citing the generated-column definition and buzz-search's own doc comment
   ("no sidecar indexer to keep coherent").
3. Generation rule & evolution — the CASE-wrapped `to_tsvector('simple',
   content)` expression, its four migrations (0001, 0005, 0008, 0014), why
   Postgres requires DROP+ADD COLUMN rather than ALTER (cited from the
   migrations' own comments), and the out-of-band maintenance script.
4. Tenancy & security boundaries — the community-scoped GIN/btree BitmapAnd
   pattern (migration comment), the privacy-kind NULL exclusion, the two
   tripwire tests, and the named `KIND_PRIVATE_MANAGED_AGENT` gap.
5. Access patterns & consistency semantics — `buzz-search::query::search()` as
   the sole read path, `websearch_to_tsquery`/prefix mode, the read-replica
   preference and its lag-tolerance trade-off, and the brownfield-vs-fresh-install
   expression discrepancy as a named, live consistency gap.
6. Lifecycle/retention — tied 1:1 to its parent row's lifecycle (soft-delete,
   partition retention); no independent TTL.
7. Scope and omissions — what this document does not cover (the whole `events`
   row, the wire meaning of any one kind, Postgres's general operational
   profile) and the `type: layers` override disclosure.

done when: the file exists, every DoD bullet in issue #1089 is addressed by a
named section, and every substantive claim has a matching evidence entry.

STEP 2 — Validate and earn the commit gate [needs 1]

Run `python3 launchpad/project-intelligence/corpus/validate.py` and fix any
reported error, repeating until it exits 0. Then run, as a bare standalone
command (never piped), `python3 -m unittest discover -s
launchpad/project-intelligence/corpus/tests -p "test_*.py"` and confirm it
reports OK.

done when: `validate.py` exits 0 and the unittest run reports OK with no
failures or errors.

STEP 3 — Commit [needs 2]

`git add` the plan file and the new document; `git commit -s` with a message
naming issue #1089.

done when: exactly one commit exists ahead of `origin/launchpad` touching only
the plan file and the target document, and `git status` is clean.

PARALLEL

None. Steps 1-3 are strictly sequential: drafting must finish before
validation, and validation must pass before the commit gate is earned.

GATES

- `python3 launchpad/project-intelligence/corpus/validate.py` exits 0.
- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` reports OK, run bare/unpiped, per repo convention that a piped command's exit code belongs to the pipe, not the suite.

BUDGET

Single document, one commit. No code changes, no other files touched besides
the plan and the target corpus node.

OPEN

- Whether `KIND_PRIVATE_MANAGED_AGENT`'s absence from the exclusion list is a
  deliberate scoping choice (ciphertext-only content, so tokenizing it leaks
  nothing) or an unnoticed gap is not resolved here — named as a gap per
  `AGENTS.md`'s convention of disclosing rather than silently resolving, not
  decided by this plan or its builder.
- Whether the brownfield/fresh-install expression discrepancy has an open
  tracking issue was not searched for exhaustively; named as a live gap in the
  document regardless, not resolved by this task.

LEFT OUT

- No relationship to `layers-data-postgres-events-table` (#1081) or any other
  `layers/data/...` sibling — all unmerged, and AGENTS.md's step 9 forbids
  targeting a node that does not exist on the branch being merged into.
- No edit to `layers-data-postgres-events-table` itself to slim its
  `search_tsv` row or add a cross-link — out of this task's scope and that
  document isn't merged yet anyway.
- No change to runtime code, migrations, or the maintenance script — this is a
  documentation-only task per issue #1089's "Out of scope" section.
