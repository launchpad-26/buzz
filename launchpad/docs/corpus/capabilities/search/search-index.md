---
id: capabilities-search-search-index
type: capabilities
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
  - statement: "buzz-search's own crate doc states the index lives in the `events` table as `search_tsv TSVECTOR GENERATED ALWAYS AS (to_tsvector('simple', content)) STORED`, with `GIN (search_tsv)` as the access path; because the column is `GENERATED ALWAYS`, every row write is the index update, so there is no separate indexer, no queue, no reindex job and no consistency window to reason about, and buzz-search is documented as the query side only -- indexing is the SQL row insert, owned by buzz-db."
    entry_class: FACT
    evidence:
      - "crates/buzz-search/src/lib.rs:1-22"
  - statement: "Migration 0001 defines `events.search_tsv` as a `TSVECTOR GENERATED ALWAYS AS (...) STORED` column using a `CASE` expression that nulls out `content`'s tsvector for a fixed set of privacy-sensitive kinds (1059 gift wrap, 30300 event reminder, 30622 DM visibility, 44100/44101 membership notices) and indexes it with `CREATE INDEX idx_events_search_tsv ON events USING GIN (search_tsv)`; its own comment states a NULL tsvector never matches `@@`, so excluded rows are storage-level unsearchable, and names the parity source (the pre-rewrite Typesense relay's kind skip list) and the config choice ('simple' = no stemming/stopwords)."
    entry_class: FACT
    evidence:
      - "migrations/0001_initial_schema.sql:190-226"
      - "migrations/0001_initial_schema.sql:274-278"
  - statement: "Three later migrations modify the same generated column additively rather than replacing its intent: migration 0005 extends the exclusion list to add kind 44200 (NIP-AM agent turn metrics, which carry NIP-44 ciphertext); migration 0008 gives only databases that are empty at migration time a positive allowlist instead (kinds 0, 9, 40002, 45001, 45003), explicitly leaving already-populated databases on their prior expression until an operator runs a separate out-of-band script (`scripts/maintenance/nip_rs_search_allowlist.sql`, named in its own comment); and migration 0014 reads whichever expression a given database currently has via `pg_attrdef`/`pg_get_expr` and wraps it to additionally exclude kind 30350 (NIP-PL, endpoint-bearing ciphertext), preserving both the fresh-install allowlist and any brownfield/operator-managed expression for every other kind."
    entry_class: FACT
    evidence:
      - "migrations/0005_agent_turn_metric_fts.sql"
      - "migrations/0008_fresh_install_search_allowlist.sql"
      - "migrations/0014_push_lease_fts.sql"
  - statement: "As a direct consequence of the 0001/0005/0008/0014 migration sequence, `events.search_tsv`'s indexing scope (which kinds are searchable at all) is not one fixed fact about 'the' relay -- it depends on whether a given deployment's database was empty at the moment migration 0008 ran, and whether the out-of-band maintenance script has since been run against a populated one; this node makes no claim about which expression any real deployment currently carries."
    entry_class: INFERENCE
    evidence:
      - "migrations/0008_fresh_install_search_allowlist.sql"
      - "migrations/0014_push_lease_fts.sql"
    confidence: 0.9
  - statement: "`buzz_search::query::search`'s own doc comment states the SQL shape and that `community_id = $ctx` is its first predicate and non-negotiable -- there is no code path through the function that omits it; the function body confirms this by pushing the community-id predicate immediately after the `FROM events CROSS JOIN LATERAL` clause, before channel scope, kinds, authors, since or until are layered on as additional optional predicates."
    entry_class: FACT
    evidence:
      - "crates/buzz-search/src/query.rs:200-217"
      - "crates/buzz-search/src/query.rs:244-304"
  - statement: "Two matching modes exist on the same generated column: `SearchMode::FullText` builds its tsquery with `websearch_to_tsquery('simple', ...)`; `SearchMode::Prefix` builds a hand-assembled tsquery that treats every completed whitespace-delimited token as exact and suffixes only the trailing token with `:*`, documented as intended for bounded typeahead surfaces such as the desktop topbar, and still routes every hit through the same refetch-and-reauthorize path as full-text mode."
    entry_class: FACT
    evidence:
      - "crates/buzz-search/src/query.rs:57-68"
      - "crates/buzz-search/src/query.rs:142-180"
  - statement: "Before any SQL is issued, `normalized_search_text` trims the query, replaces embedded NUL bytes with spaces, and caps the result at 4096 characters (`SEARCH_TEXT_MAX_CHARS`); an empty-or-whitespace-only result short-circuits `search()` to a zero-hit `SearchResult` with no Postgres round trip, and this normalization/cap behavior is covered directly by three unit tests in the same file."
    entry_class: FACT
    evidence:
      - "crates/buzz-search/src/query.rs:181-198"
      - "crates/buzz-search/src/query.rs:220-225"
      - "crates/buzz-search/src/query.rs:346-368"
  - statement: "The relay exposes exactly two entry points into this same search machinery, both detecting a search request identically as `filters.iter().any(|f| f.search.is_some())`: a WebSocket `REQ` (`handle_req` dispatching to `handle_search_req`), and an HTTP `POST /query` request (`query_events` dispatching through to `handle_bridge_search`); both reject a request that mixes a search filter with a non-search filter in the same batch rather than partially serving it, with the same message text ('mixed search and non-search filters not supported')."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs:246-257"
      - "crates/buzz-relay/src/api/bridge.rs:1023-1030"
      - "crates/buzz-relay/src/api/bridge.rs:1682-1698"
  - statement: "`buzz-cli`'s `messages search` subcommand (`MessagesCmd::Search`, dispatched to `cmd_search`) builds a fixed `kinds: [9, 40002, 45001, 45003]` filter -- message-shaped kinds only, deliberately excluding kind 0 profiles -- and exposes no `--kinds` flag; it requires at least one of `--query` or `--author`, and its `--author` resolution falls back to a NIP-50 `kinds:[0]` search on display name when given neither a 64-char hex pubkey nor an `npub1...` bech32 key."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/lib.rs:499-513"
      - "crates/buzz-cli/src/commands/messages.rs:430-475"
      - "crates/buzz-cli/src/commands/messages.rs:477-500"
  - statement: "The desktop app consumes the same search machinery through a dedicated `features/search` module -- `TopbarSearch.tsx` (the search dialog UI), `useSearchResults.ts` (a `useSearchMessagesQuery` hook combined with user/channel candidate ranking), and `parseSearchOperators.ts` (operator parsing such as `in:<channel>` and `from:<user>`) -- confirming the capability has a real, wired client surface beyond the CLI and raw protocol."
    entry_class: FACT
    evidence:
      - "desktop/src/features/search/ui/TopbarSearch.tsx:1-20"
      - "desktop/src/features/search/useSearchResults.ts:1-30"
  - statement: "Representative live coverage of this capability's request-to-result path exists in `buzz-test-client`'s e2e interop suite (`test_nip50_search_returns_results_and_eose`, `test_nip50_search_mixed_filters_rejected`, `test_nip50_search_empty_results`, `test_nip17_gift_wrap_not_searchable`) and in `buzz-search`'s own integration test file, which names 22 async test functions covering community isolation (`search_does_not_return_other_community_events`), channel scoping (`channel_scope_restricts_results`, `channel_less_only_excludes_per_channel_events`), pagination and bounds (`pagination_works`, `enormous_page_number_is_clamped`, `very_long_query_is_bounded_before_pg_parse`), input sanitization (`nul_bytes_in_query_are_sanitized`), and the storage-level privacy exclusions this node's kind-allowlist claims above depend on (`excluded_kinds_are_storage_level_unsearchable`, `author_only_kinds_are_storage_level_unsearchable`, `p_gated_persistent_kinds_have_storage_null_tsvector`)."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/e2e_nostr_interop.rs:262-431"
      - "crates/buzz-test-client/tests/e2e_nostr_interop.rs:971-1046"
      - "crates/buzz-search/tests/fts_integration.rs:157-1470"
  - statement: "Root AGENTS.md's own 'Common Gotchas' section states as an existing constraint that `messages search` chooses its own supported kinds and that a `--kinds` option should not be added to it, distinct from raw relay filters which still need explicit kinds -- corroborating, from a second independent source, the fixed-kinds behavior read directly from `cmd_search` above."
    entry_class: FACT
    evidence:
      - "AGENTS.md:454"
  - statement: "VISION_PROJECTS.md's own 'Capability | Status' table (the same table the capability template's evidence ledger cites as this repository's product-level capability catalogue) does not carry a row for search -- so this node's 'Shipped' maturity claim below is grounded directly in merged code and tests, not in a VISION status marker, because no such marker exists for this capability."
    entry_class: FACT
    evidence:
      - "VISION_PROJECTS.md:247-259"
  - statement: "The already-merged flow node `architecture-flows-search-query` documents the same request-to-result path this node names at capability level -- trigger, preconditions, the ordered WS/HTTP interactions, trust-boundary crossings and failure outcomes -- and is the correct target for that detail rather than restating it here."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/flows/search-query.md"
  - statement: "The already-merged container nodes `architecture-containers-postgres` and `architecture-containers-relay` both describe this capability's storage and orchestration: postgres.md states buzz-search's full-text search reads the same `events` table buzz-db writes to (no separate index to provision or keep in sync) and that the relay's search pool prefers `READ_DATABASE_URL` when configured; relay.md states buzz-search is one of the subsystem crates buzz-relay orchestrates directly and that AppState holds a direct handle to buzz-search's `SearchService`."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/containers/postgres.md"
      - "launchpad/docs/corpus/architecture/containers/relay.md"
  - statement: "At the recorded revision, no `capabilities`-typed node has yet been merged to `origin/launchpad`'s corpus tree -- confirmed by listing `launchpad/docs/corpus/**` and finding only `architecture/`, `schema/`, `standards/` and `templates/` subtrees -- so this is the first node built from the capability template to reach the corpus, and no capability-shaped sibling exists yet to relate this node to via `part-of` or a shared parent."
    entry_class: FACT
    evidence:
      - "git_ls_tree(ref='HEAD', path='launchpad/docs/corpus') -> AGENTS.md, README.md, architecture/**, schema/**, standards/**, templates/**, no capabilities/ subtree present, checked against a worktree created from origin/launchpad at commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
relationships:
  - type: references
    target: architecture-flows-search-query
  - type: references
    target: architecture-containers-postgres
  - type: references
    target: architecture-containers-relay
---

# Search index: capability

Buzz gives every member and agent full-text search over the messages, posts and
other content stored in their community: a NIP-50 `search` filter, sent over either
the relay's WebSocket `REQ` door or its HTTP `POST /query` bridge, returns
relevance-ranked, authorization-filtered results from the same Postgres database
that stores the events themselves. The same machinery backs `buzz-cli`'s
`messages search` subcommand, the desktop app's topbar search dialog, and
display-name lookups used internally by author-resolution and NIP-50 profile
matching.

## Maturity

**Shipped.** The generated `search_tsv` column and its GIN index were introduced in
the initial schema migration and have been extended additively by three further
merged migrations since; the query layer (`buzz-search`), its wiring into both relay
entry points (`buzz-relay`'s WS and HTTP handlers), the `buzz-cli` `messages search`
subcommand, and the desktop `features/search` module are all present in the merged
tree with passing unit and integration tests. No VISION status marker names this
capability directly (see the evidence ledger), so this maturity claim rests on the
migrations, the query crate, the CLI/desktop consumers and the test suites cited
above, not on a status table row.

## Behavior: rules, constraints and variants

- **Query text is normalized and bounded before any SQL runs.** The search string
  is trimmed, embedded NUL bytes are replaced with spaces, and the result is capped
  at 4096 characters; an empty or whitespace-only query returns zero hits with no
  Postgres round trip at all.
- **A request cannot mix a search filter with a non-search filter.** Both transports
  reject such a request outright — WS closes the subscription, HTTP returns 400 —
  rather than partially serving it.
- **Two matching variants exist over the same index.** `FullText` uses
  `websearch_to_tsquery` for ordinary word/lexeme search; `Prefix` treats completed
  tokens as exact and prefix-matches only the trailing token, for bounded typeahead
  callers such as the desktop topbar. Both variants still refetch and re-authorize
  every hit identically — the variant changes only the candidate tsquery, never the
  access boundary.
- **Certain kinds are unsearchable at the storage level, independent of any query or
  caller.** Privacy-sensitive kinds (gift wraps, DM-visibility markers, membership
  notices, agent-turn metrics, NIP-PL endpoint ciphertext) have their `search_tsv`
  generated as `NULL`, which never matches `@@` — no query shape or authorization
  level can surface them through this capability.
- **The community boundary is non-negotiable.** Every query is scoped to exactly one
  community as its first predicate; there is no call path that omits it.
- **Search results are never the access decision.** Every hit is independently
  re-authorized against the full per-event visibility gate before being returned,
  regardless of which transport or matching variant produced the candidate.

## Boundary

This node does not describe:
- **How the capability is built** — the Postgres schema (`search_tsv`/GIN index
  ownership, connection pooling, read-replica preference) and the relay's process
  orchestration are the architecture container nodes' territory; see
  `architecture-containers-postgres` and `architecture-containers-relay`.
- **The interface(s) the capability is exposed through** — the WebSocket `REQ`
  protocol shape, the HTTP `POST /query` bridge contract, and the `buzz-cli`
  subcommand surface are boundary contracts in their own right. No `interfaces-events`
  node documenting them has been merged yet; this node names their existence (above)
  without describing their operations in general, durable terms.
- **The step-by-step flow through this capability** — trigger, preconditions,
  ordered interactions, trust-boundary crossings and failure outcomes for one request
  are already documented in `architecture-flows-search-query`; this node does not
  restate them.
- **How the running system is operated** — whether a given deployment's database is
  on the fresh-install allowlist or an older brownfield expression, and whether the
  out-of-band maintenance script (`scripts/maintenance/nip_rs_search_allowlist.sql`)
  has been run against it, is an operational fact about one deployment, not a
  property of the capability itself.

## Relationships

- references: `architecture-flows-search-query` — the ordered, step-by-step path a
  NIP-50 search request takes across both transports.
- references: `architecture-containers-postgres` — the storage this capability's
  index lives in: the generated `search_tsv` column, its GIN index, and the search
  pool's read-replica preference.
- references: `architecture-containers-relay` — the process that orchestrates
  `buzz-search` alongside the community's other subsystems and holds its
  `SearchService` handle.

## Scope and omissions

**This node covers** the search-index capability itself: what a user or agent can do
because it exists (full-text search over community content, exposed through
multiple client surfaces), its maturity and the evidence for that maturity, the
storage-level privacy exclusions that make certain kinds unsearchable regardless of
query, and the boundary against the architecture, interface and flow neighbors that
own their own slices of this subject.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The Postgres schema, connection pooling and read-replica preference that store and serve the index | `architecture-containers-postgres` |
| The relay process that orchestrates `buzz-search` alongside its other subsystems | `architecture-containers-relay` |
| The step-by-step request/response path across both transports | `architecture-flows-search-query` |
| The WebSocket `REQ`, HTTP `POST /query` and `buzz-cli` boundary contracts in general, durable terms | An `interfaces-events` node, not yet drafted |
| Whether any specific real deployment's `search_tsv` expression is on the fresh-install allowlist or an older brownfield expression, and whether the out-of-band maintenance script has been run against it | Not established anywhere inspected for this node; an operational fact about one deployment, not this capability |
| The desktop UI's full search experience (operator parsing, keyboard navigation, result ranking beyond FTS relevance) beyond naming that `features/search` exists and consumes this capability | Client-side documentation, not this node |

**Expected but not verified when this node was written:**
- **No live relay was run against this node's claims.** Every claim above is sourced
  from reading migrations, crate source and existing test files, not from executing
  `just test` or `just ci` as part of authoring this document.
- **Whether `scripts/maintenance/nip_rs_search_allowlist.sql` has been run against any
  populated deployment was not checked** — this node states the migration-level fact
  only (that the script exists and that migration 0008 defers to it), not the
  operational status of any real database.
- **No automated `review-code` pass is available in this task's environment**; only a
  manual self-review against issue #819's Definition of Done and this document's own
  capability-template checklist was performed, and cross-model/adjudicated review is
  deferred to the batch owner per this batch's own process.
