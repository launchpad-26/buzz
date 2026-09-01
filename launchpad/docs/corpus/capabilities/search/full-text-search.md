---
id: capabilities-search-full-text-search
type: capabilities
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5."
    entry_class: FACT
    evidence:
      - "commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
  - statement: "buzz-search's own Cargo.toml describes it as \"Postgres full-text search for Buzz, scoped by community\", and its crate-level doc comment states the index lives in the events table's search_tsv column, a `TSVECTOR GENERATED ALWAYS AS (to_tsvector('simple', content)) STORED` column with a `GIN (search_tsv)` index -- because the column is generated, every row write to events IS the index update, so there is no separate indexer process, no queue, no reindex job, and no consistency window between a stored event and its searchability."
    entry_class: FACT
    evidence:
      - "crates/buzz-search/Cargo.toml"
      - "crates/buzz-search/src/lib.rs"
  - statement: "buzz-search's crate doc states explicitly that it is the query side only -- indexing is the SQL row insert, owned by buzz-db -- and that the relay refetches canonical events through buzz-db's scoped fetcher and runs access checks per hit, so search is never the access boundary."
    entry_class: FACT
    evidence:
      - "crates/buzz-search/src/lib.rs"
  - statement: "SearchQuery requires a CommunityId at the type level with no construction path that omits it, and buzz_search::search's own doc comment states community_id = $ctx is the first WHERE predicate and non-negotiable; the function body binds it immediately after building the mode-specific tsquery, before any other predicate is added."
    entry_class: FACT
    evidence:
      - "crates/buzz-search/src/query.rs"
  - statement: "Two distinct matching modes exist on the same SearchQuery/search() path: SearchMode::FullText builds `websearch_to_tsquery('simple', ...)` for word/lexeme search, and SearchMode::Prefix builds a hand-constructed tsquery that suffixes only the trailing whitespace-delimited token with `:*`, intended for bounded typeahead surfaces; both still refetch and re-authorize every hit identically."
    entry_class: FACT
    evidence:
      - "crates/buzz-search/src/query.rs"
  - statement: "An empty or whitespace-only search string never reaches Postgres: normalized_search_text trims the input, replaces embedded NUL bytes with spaces, caps it at 4096 characters, and on an empty-after-trim result buzz_search::search returns an empty SearchResult immediately with no SQL round trip; three unit tests (normalized_search_text_trims_and_rejects_empty, normalized_search_text_replaces_nul_bytes, normalized_search_text_caps_length) cover this boundary directly."
    entry_class: FACT
    evidence:
      - "crates/buzz-search/src/query.rs"
  - statement: "Kind-level privacy exclusion is enforced at the storage layer, not only by the relay's request-time gates: migrations/0001_initial_schema.sql defines the search_tsv generated column with a CASE expression that emits NULL tsvector for a blocklist of kinds (kind 1059 gift wraps, 30300 event reminders, 30622 DM-visibility, 44100/44101 membership notices at that revision), and a NULL tsvector can never satisfy `@@`, so those kinds cannot be found by search regardless of any bug in the relay's own filter-level gates."
    entry_class: FACT
    evidence:
      - "migrations/0001_initial_schema.sql"
  - statement: "buzz-search's own integration test suite verifies this storage-level exclusion directly with three tripwire tests -- excluded_kinds_are_storage_level_unsearchable, author_only_kinds_are_storage_level_unsearchable, and p_gated_persistent_kinds_have_storage_null_tsvector -- each inserting one row per excluded kind alongside a searchable kind:9 control and asserting only the control surfaces; the test file's own comments describe this as a defense-in-depth backstop against a future relay-side gate bug, not a substitute for the relay's own per-hit authorization."
    entry_class: FACT
    evidence:
      - "crates/buzz-search/tests/fts_integration.rs"
  - statement: "The same integration suite also exercises community isolation (search_does_not_return_other_community_events: an event indexed under community A is invisible to a query bound to community B), channel scoping across all four ChannelScope variants (channel_scope_restricts_results, channel_less_only_excludes_per_channel_events), pagination (pagination_works), since/until bounds (since_until_filters), soft-deleted-event exclusion (deleted_events_are_excluded), and kind:0 profile search over raw JSON content without a flattening step (kind0_search_by_display_name_works_without_flattening)."
    entry_class: FACT
    evidence:
      - "crates/buzz-search/tests/fts_integration.rs"
  - statement: "buzz-cli's `messages search` subcommand is a direct actor of this capability: it requires at least one of --query or --author, builds a fixed `kinds: [9, 40002, 45001, 45003]` filter (message-shaped kinds only), attaches the --query value as the NIP-01 `search` field, and sends the filter through BuzzClient::query, which POSTs it to the relay's `/query` HTTP bridge with a NIP-98-signed request."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/commands/messages.rs"
      - "crates/buzz-cli/src/client.rs"
  - statement: "The same buzz-cli command reuses this capability for a second purpose: resolving a `--author` value given as a display name runs a NIP-50 search scoped to `kinds: [0]` (profiles) and requires an exact, case-insensitive match on display_name or name, erroring with the candidate list on ambiguity rather than picking one silently."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/commands/messages.rs"
  - statement: "The desktop app's topbar search is a second, independent actor: useSearchResults (consumed by TopbarSearch) parses Slack-style `from:`/`in:`/`after:`/`before:` operators out of the raw query client-side via parseSearchOperators, leaving the remaining free text as the FTS query, and passes it to useSearchMessagesQuery scoped by the resolved channel/author/since/until -- the same underlying relay search capability buzz-cli calls, reached through a different client surface."
    entry_class: FACT
    evidence:
      - "desktop/src/features/search/useSearchResults.ts"
      - "desktop/src/features/search/lib/parseSearchOperators.ts"
  - statement: "The desktop client's SearchMessagesInput/SearchHit types carry a channel id, a relevance score, and an optional thread root id per hit, matching the relay's relevance-ordered, per-hit-authorized result shape rather than a raw event dump."
    entry_class: FACT
    evidence:
      - "desktop/src/shared/api/searchTypes.ts"
  - statement: "Root AGENTS.md states as a repository-wide pattern that `POST /query` accepts Nostr REQ filters over HTTP and that NIP-50 `search` filters are routed to buzz-search (Postgres FTS) automatically -- naming this capability's HTTP entry point as one instance of the repository's general 'prefer Nostr events over new HTTP endpoints' pattern rather than a bespoke search API."
    entry_class: FACT
    evidence:
      - "AGENTS.md"
  - statement: "VISION_PROJECTS.md's own Status table (the repository's product-level capability/maturity ledger) lists eleven rows and none of them names search or full-text search specifically, so this node's maturity claim below is grounded in code and tests rather than in that table."
    entry_class: FACT
    evidence:
      - "VISION_PROJECTS.md:247-259"
---

# Full text search: capability

Buzz members can search the content of messages and profiles within the
communities they belong to, and get back relevance-ranked results scoped to
what they are authorized to see -- across every channel-shaped and DM-shaped
message kind the relay stores, not a separate search-only subset.

## Maturity

**Shipped.** The capability is backed by a merged crate (`crates/buzz-search`)
with unit tests covering its text-normalization boundary and an `#[ignore]`d
Postgres integration suite (`crates/buzz-search/tests/fts_integration.rs`)
covering community isolation, channel scoping, pagination, time bounds,
soft-delete exclusion, kind:0 profile search, and storage-level privacy
exclusions. Two independent production call sites consume it today:
`buzz-cli`'s `messages search` subcommand and the desktop app's topbar search
(`useSearchResults`/`TopbarSearch`). Relay-boundary behavior (trigger,
termination, mixed-filter rejection, and a gift-wrap-kind exclusion
regression) has representative end-to-end coverage in
`crates/buzz-test-client/tests/e2e_nostr_interop.rs`
(`test_nip50_search_returns_results_and_eose`,
`test_nip50_search_mixed_filters_rejected`,
`test_nip50_search_empty_results`, `test_nip17_gift_wrap_not_searchable`).
VISION_PROJECTS.md's own product Status table does not carry a dedicated row
for search, so this maturity claim rests on the code and test evidence above,
not on a VISION status marker.

## Boundary

This node does not describe:
- **How the capability is built** -- the Postgres `search_tsv` generated
  column, its GIN index, and Postgres's role as the container hosting it are
  the architecture container node's territory; see
  `architecture-containers-postgres`.
- **The interface(s) the capability is exposed through** -- the WebSocket
  `REQ` search branch, the HTTP `POST /query` bridge, and `buzz-cli`'s
  `messages search` subcommand are each a boundary contract of their own.
  No interface-typed corpus node covers any of them yet at this revision.
- **The step-by-step flow through this capability** -- the ordered
  request-to-response path on both relay transports, including every
  authentication/authorization crossing, is already documented by
  `architecture-flows-search-query`; this node does not restate it.
- **How the running system is operated** -- deployment topology for
  Postgres, and any operational tuning of the `search_tsv` allowlist across
  migrations, is out of scope here (see `architecture-containers-postgres`
  and `architecture-flows-search-query` for what is currently known about
  that divergence).
- **The desktop/mobile UI search experience** beyond naming its two current
  call sites (typeahead debounce, result rendering, keyboard navigation) --
  that is client-side UI documentation, not this node.

## Behavioral rules, constraints and variants

- **Always community-scoped.** `SearchQuery` requires a `CommunityId` at the
  type level; there is no code path through `buzz-search` that can execute a
  query without binding `community_id = $ctx` as the first predicate.
- **Never the access boundary.** A search hit is a candidate event id only.
  The relay refetches the canonical event and re-runs the full per-event
  authorization gate before returning or emitting it -- search ordering and
  ranking are decided by Postgres, access is decided afterward, every time.
- **Storage-level privacy exclusion, independent of the relay's own gates.**
  A fixed set of kinds (gift wraps, event reminders, DM-visibility snapshots,
  membership notices, and other author-only/p-gated kinds) are given a
  `NULL` generated tsvector in the schema itself, so they cannot match `@@`
  regardless of whether a relay-side filter gate has a bug. Three
  integration tests tripwire this independently of the relay's request-time
  checks.
- **Two matching modes on one query path.** `SearchMode::FullText` (word/
  lexeme search via `websearch_to_tsquery`) and `SearchMode::Prefix`
  (trailing-token prefix match, for typeahead) share the same community
  scoping, channel scoping, and per-hit re-authorization -- only the
  candidate `tsquery` construction differs.
- **Empty or invalid input never reaches Postgres.** Search text is trimmed,
  NUL-sanitized, and capped at 4096 characters before any SQL is built; an
  empty result after that normalization returns zero hits with no database
  round trip.
- **Channel scoping is a closed four-variant enum**, not an ad hoc boolean
  pair -- `Any`, `ChannelLessOnly`, `Channels(ids)`, and
  `ChannelsOrChannelLess(ids)` -- so "no accessible channels, no global
  access" and "no channel constraint at all" cannot be confused with one
  another at the type level.
- **Two independent actors, one shared machinery.** `buzz-cli`'s
  `messages search` (fixed message-kind filter, plus a kind:0 profile search
  used only to resolve `--author` display names) and the desktop app's
  topbar search (Slack-style `from:`/`in:`/`after:`/`before:` operators
  parsed client-side, remaining text sent as the FTS query) both terminate
  in the same relay-side search capability documented by
  `architecture-flows-search-query`.

## Relationships

- references: architecture-flows-search-query
- references: architecture-containers-postgres

## Scope and omissions

**This node covers** what the full-text-search capability lets a Buzz member
do, its current maturity and the evidence for it, the actors that call it
today (`buzz-cli`, the desktop topbar search), and the behavioral
rules/constraints/variants a caller can rely on: community scoping, the
search-is-never-the-access-boundary guarantee, storage-level privacy
exclusion, the two matching modes, input normalization, and channel-scope
semantics.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The ordered request-to-response path on both relay transports, including every auth/trust-boundary crossing | `architecture-flows-search-query` |
| Postgres as a container: connection pooling, migration gating, deployment topology | `architecture-containers-postgres` |
| The boundary contract each call site is exposed through (WS `REQ`, HTTP `POST /query`, the `messages search` CLI subcommand) | no interface-typed corpus node exists yet at this revision |
| Whether the fresh-install-vs-brownfield `search_tsv` exclusion-list divergence across migrations 0001/0005/0008/0014 has been reconciled for any real deployment | not established anywhere inspected for this node; `architecture-flows-search-query` records the same open gap |
| The desktop/mobile UI search experience itself (typeahead debounce, result rendering, keyboard navigation) | client-side UI documentation, not this node |

**Expected but not verified when this node was written:**

- **The desktop client's native (Tauri/Rust) leg between `searchMessages` and the relay's HTTP bridge was not traced.** `desktop/src/features/search/hooks.ts` calls a `searchMessages` Tauri IPC function; this node did not open the Rust-side implementation behind that IPC boundary to confirm it reaches `/query` the same way `buzz-cli` does, only that the TypeScript-side request/response shapes (`SearchMessagesInput`/`SearchHit`) match the relay's documented contract.
- **No live relay was run against this node's claims.** Every claim above is sourced from reading the crate, its tests, migrations, and the two client call sites, not from executing `just test` or a fresh integration run as part of authoring this document. `validate.py` and the corpus test suite were run and are reported in this task's commit; the broader Rust/desktop test suites were not re-run as part of writing this node.
- **There is no automated `review-code` pass available in this task's environment.** Only a manual self-review against issue #816's Definition of Done was performed.
