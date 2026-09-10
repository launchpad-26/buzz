---
id: implementation-crates-buzz-search
type: implementation
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 76a0a4ebbe4bc4d852b0d04362ed768620da34b3."
    entry_class: FACT
    evidence:
      - "commit 76a0a4ebbe4bc4d852b0d04362ed768620da34b3"
  - statement: "buzz-search's own crate doc states its boundary explicitly: it is the query side only, over a `search_tsv TSVECTOR GENERATED ALWAYS AS (to_tsvector('simple', content)) STORED` column with a GIN index; indexing is the SQL row insert, owned by buzz-db, not this crate — 'no separate indexer, no mpsc queue, no reindex job, no consistency window to reason about.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-search/src/lib.rs"
  - statement: "buzz-search's crate doc names the target this node documents explicitly: 'search is never the access boundary (conformance row 50)', pointing at docs/multi-tenant-conformance.md's numbered conformance table."
    entry_class: FACT
    evidence:
      - "crates/buzz-search/src/lib.rs"
  - statement: "docs/multi-tenant-conformance.md's row 50 ('Search / FTS') states the community-scoping contract this crate is checked against: every search query filters by community_id, BitmapAnd-ed with the GIN @@ probe; refetch is by (community_id, event_id); channel-less scope is ChannelScope::ChannelLessOnly, meaning channel-less within the community, not platform-global."
    entry_class: FACT
    evidence:
      - "docs/multi-tenant-conformance.md:50"
  - statement: "buzz-search's public surface, re-exported from src/lib.rs, is: SearchService (a thin PgPool wrapper with new() and an async search() method), and from query.rs: the search() function, ChannelScope, SearchHit, SearchMode, SearchQuery, and SearchResult; SearchError is the crate's one error type, wrapping sqlx::Error via #[from]."
    entry_class: FACT
    evidence:
      - "crates/buzz-search/src/lib.rs"
      - "crates/buzz-search/src/error.rs"
  - statement: "SearchQuery::community is a non-optional CommunityId field, and query::search's own doc comment states 'community_id = $ctx is the first predicate and is non-negotiable. There is no code path through this function that omits it' — verified directly in the QueryBuilder construction, which pushes 'WHERE community_id = ' immediately after the FROM/CROSS JOIN LATERAL tsquery clause, before any of the optional channel/kinds/authors/since/until predicates."
    entry_class: FACT
    evidence:
      - "crates/buzz-search/src/query.rs"
  - statement: "ChannelScope is a four-variant enum (Any, ChannelLessOnly, Channels(Vec<Uuid>), ChannelsOrChannelLess(Vec<Uuid>)) that is documented as closing a real ambiguity in a legacy (Option<Vec<Uuid>>, bool) 2x2 shape: with empty accessible channels and include_global=true, the old shape could not distinguish 'restrict to channel-less events' from 'broaden to all channels', and ChannelLessOnly is the variant that closes that hole at the type level."
    entry_class: FACT
    evidence:
      - "crates/buzz-search/src/query.rs"
  - statement: "SearchMode has two variants: FullText (websearch_to_tsquery('simple', ...)) and Prefix (a hand-built tsquery that keeps completed whitespace-delimited tokens exact and suffixes only the trailing token with ':*', intended for bounded typeahead such as the desktop topbar); both modes pass their raw search text through Postgres' own 'simple' parser before tsquery construction so query-side normalization matches the search_tsv generated column."
    entry_class: FACT
    evidence:
      - "crates/buzz-search/src/query.rs"
  - statement: "normalized_search_text trims the input, rejects an empty-after-trim string by returning None (search() then short-circuits to an empty SearchResult with no SQL round trip), replaces embedded NUL bytes with spaces, and caps the cleaned text at 4096 characters (SEARCH_TEXT_MAX_CHARS) before any Postgres text-search parser sees it; three unit tests in query.rs's own #[cfg(test)] module cover exactly these three behaviors (normalized_search_text_trims_and_rejects_empty, normalized_search_text_replaces_nul_bytes, normalized_search_text_caps_length)."
    entry_class: FACT
    evidence:
      - "crates/buzz-search/src/query.rs"
  - statement: "search() clamps per_page to a [1, 500] range (PER_PAGE_MAX=500, defaulting to PER_PAGE_DEFAULT=100 when the caller passes 0) and clamps page to [1, 1000] (PAGE_MAX=1000), with the module comment noting the 1000 cap exists specifically so 'a future caller cannot accidentally wire untrusted input into a multi-trillion-row OFFSET' even though today's only two callers (WS pagination 1..=MAX_SEARCH_PAGES, HTTP page 1) never approach it."
    entry_class: FACT
    evidence:
      - "crates/buzz-search/src/query.rs"
  - statement: "buzz-relay's HTTP POST /query bridge is one of exactly two callers of buzz_search::search: bridge.rs builds a SearchQuery per accepted search filter (community from the resolved tenant, channel_scope from an #h-tag/accessible-channel intersection, kinds/authors/since/until passed through, page from extract_search_page, mode from extract_search_mode which reads a caller-supplied 'prefix'/'fulltext' hint) and calls state.search.search(&search_query), propagating a search error as a 500 'search error: ...' response."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs"
  - statement: "buzz-relay's WebSocket REQ handler is the other of the two callers: handlers/req.rs's handle_search_req builds a SearchQuery per filter per page inside a bounded pagination loop (1..=MAX_SEARCH_PAGES), and its SearchQuery literal hardcodes mode: buzz_search::SearchMode::FullText — the WS entry point never selects SearchMode::Prefix, unlike the HTTP entry point's extract_search_mode; this is a real, verified capability asymmetry between the two transports, not an artifact of reading only one file."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs"
      - "crates/buzz-relay/src/api/bridge.rs"
  - statement: "buzz-relay's main.rs constructs the pool buzz-search runs against as a direct sqlx::postgres::PgPoolOptions connection (not through buzz_db::Db), preferring config.read_database_url when set and falling back to config.database_url otherwise; the surrounding comment states this is deliberate because 'search is lag-tolerant', and the same fact is independently corroborated by architecture-containers-postgres, which documents this same pool from the Postgres-container side."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs"
  - statement: "buzz-search's Cargo.toml declares five non-dev dependencies: buzz-core (for CommunityId), buzz-datastore-tracing (the #[datastore_span] macro instrumenting query::search), sqlx, uuid, thiserror, tracing, and metrics; its sole dev-dependency is tokio, used by the ignored integration test suite."
    entry_class: FACT
    evidence:
      - "crates/buzz-search/Cargo.toml"
  - statement: "crates/buzz-search/tests/fts_integration.rs is the crate's representative test file: 18 #[ignore = \"requires Postgres\"] async tests, each creating a uniquely-named Postgres schema, applying the full FTS-affecting migration chain (0001, 0002, 0003, 0004, 0005, 0006, 0007, 0008, 0014, 0033) in order, exercising one scenario, and dropping the schema; coverage includes community isolation (search_does_not_return_other_community_events), all four ChannelScope variants, soft-delete exclusion (deleted_events_are_excluded), pagination and page-number clamping, NUL-byte sanitization, and three storage-level privacy tripwires (excluded_kinds_are_storage_level_unsearchable, author_only_kinds_are_storage_level_unsearchable, p_gated_persistent_kinds_have_storage_null_tsvector) that assert specific privacy-sensitive kinds never surface from search_tsv regardless of application-level filtering."
    entry_class: FACT
    evidence:
      - "crates/buzz-search/tests/fts_integration.rs"
  - statement: "architecture-flows-search-query (merged on origin/launchpad) already documents the end-to-end NIP-50 request/response flow across both transports at the level of trust boundaries, ordering, and failure outcomes, citing crates/buzz-search/src/query.rs directly for the SQL-shape and text-normalization claims this node also makes; this node goes one layer deeper into the crate's own concrete modules, types, and tests rather than restating that flow."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/flows/search-query.md"
  - statement: "architecture-containers-postgres (merged on origin/launchpad) already documents the search pool's connection shape, ownership boundary, and read-replica preference from the Postgres-container side; this node does not restate that container-level detail."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/containers/postgres.md"
---

# buzz-search: implementation reference

`crates/buzz-search` is the query-side crate for Buzz's Postgres full-text
search: a thin, community-scoped SQL layer over the `events.search_tsv`
generated `tsvector` column. It claims to realize the community-scoping
contract stated in `docs/multi-tenant-conformance.md`'s conformance row 50
("Search / FTS") — every search query filters by `community_id`, refetch is
by `(community_id, event_id)`, and `ChannelScope::ChannelLessOnly` means
channel-less *within* the community, never platform-global. The crate's own
doc comment names that row explicitly as "conformance row 50," which is how
this node identified the target rather than inferring it.

## Target

`docs/multi-tenant-conformance.md`, row 50 ("Search / FTS") of the
conformance table starting at line 40. This file has no corpus node id yet —
no `implements` edge is declared toward it; see *Relationships* below for why.
A reader can open the row directly at `docs/multi-tenant-conformance.md:50`.

## Implementation surface

| Component / file / symbol | Realizes | Note |
|---|---|---|
| `crates/buzz-search/src/lib.rs` — `SearchService::new`/`search` | Stable injection point for `buzz-relay`'s `AppState`; holds nothing the wrapped `PgPool` doesn't already own | Public entry point |
| `crates/buzz-search/src/query.rs` — `search()` | Row 50's core predicate: `community_id = $ctx` as the first, non-optional `WHERE` clause; refetch-by-id is the caller's job (owned by `architecture-flows-search-query`) | The crate never fetches full `StoredEvent`s itself — it returns candidate ids and ranks only |
| `crates/buzz-search/src/query.rs` — `ChannelScope` (4 variants) | Row 50's `ChannelScope::ChannelLessOnly` language directly; the enum closes a real ambiguity a legacy `(Option<Vec<Uuid>>, bool)` pair could not express | `Channels(vec![])` and `ChannelsOrChannelLess(vec![])` are deliberately not special-cased — Postgres's own `ANY('{}')` semantics do the right thing |
| `crates/buzz-search/src/query.rs` — `normalized_search_text` | Search-input hygiene ahead of any SQL: trim, empty rejection, NUL replacement, 4096-char cap | Covered by 3 unit tests in the same file |
| `crates/buzz-search/src/query.rs` — `push_tsquery` / `SearchMode` | `FullText` (`websearch_to_tsquery`) vs `Prefix` (hand-built trailing-token prefix match for typeahead) | See *Divergences* — only the HTTP entry point ever selects `Prefix` |
| `crates/buzz-search/src/error.rs` — `SearchError` | Wraps `sqlx::Error` via `#[from]`; the crate's only error variant | — |
| `crates/buzz-relay/src/api/bridge.rs` — `extract_search_mode`, `SearchQuery` construction (~L1919-1936) | HTTP `POST /query` consumer; supports both `SearchMode` variants | Owned in detail by `architecture-flows-search-query` |
| `crates/buzz-relay/src/handlers/req.rs` — `build_search_channel_scope_filter`, `handle_search_req` (~L561-699) | WS `REQ` consumer; paginates internally, always `SearchMode::FullText` | Owned in detail by `architecture-flows-search-query` |
| `crates/buzz-relay/src/main.rs` — search pool construction (~L416-433) | Deployment wiring: a direct `sqlx::postgres::PgPoolOptions` pool preferring `READ_DATABASE_URL` | Owned in detail by `architecture-containers-postgres` |

## Divergences

Checked directly against row 50's stated community-scoping contract — the
first predicate, the refetch key, and the `ChannelLessOnly` semantics — and
found no divergence: `query::search`'s own doc comment and its `QueryBuilder`
construction match the target's language almost verbatim, and the target's
"one community produces the same search results as today" compatibility
claim has no counter-evidence in this crate's code or tests.

One real asymmetry was found, though it is not a divergence from row 50
specifically (row 50 says nothing about typeahead or prefix matching): the
crate exposes two `SearchMode` variants, but only the HTTP `POST /query`
entry point (`bridge.rs`'s `extract_search_mode`) can ever select
`SearchMode::Prefix`. The WebSocket `REQ` entry point
(`handlers/req.rs::handle_search_req`) constructs every `SearchQuery` with
`mode: buzz_search::SearchMode::FullText` hardcoded — there is no code path
from a WS client to prefix search. Whether that asymmetry is intentional
(desktop typeahead is HTTP-only today) or unreconciled drift was not
determined by this node; it is recorded as an observed fact about the
implementation surface, not adjudicated.

## Verification

- **Unit tests**, in `crates/buzz-search/src/query.rs`'s own `#[cfg(test)]`
  module: `normalized_search_text_trims_and_rejects_empty`,
  `normalized_search_text_replaces_nul_bytes`,
  `normalized_search_text_caps_length`. These run under plain `cargo test -p
  buzz-search` with no external dependency.
- **Integration tests**, in `crates/buzz-search/tests/fts_integration.rs`: 18
  `#[ignore = "requires Postgres"]` async tests run against a real Postgres
  instance (`BUZZ_TEST_DATABASE_URL=postgres://buzz:buzz_dev@localhost:5432/buzz
  cargo test -p buzz-search --tests -- --include-ignored`), each against a
  freshly created, uniquely-named schema with the full FTS-affecting migration
  chain applied. These are the crate's load-bearing tests: community
  isolation, all four `ChannelScope` variants, soft-delete exclusion,
  pagination/clamping, NUL-byte sanitization, and three storage-level privacy
  tripwires that assert specific privacy-sensitive Nostr kinds can never
  surface from `search_tsv` regardless of what the relay's own filters do.
- **No CI job specific to this crate** was found distinct from the workspace's
  general `cargo test`/`just ci` gate; this node does not assert one exists
  beyond that.

## Relationships

- `references`: `architecture-flows-search-query` — the merged flow node that
  documents this crate's one caller path end-to-end (trust boundaries,
  ordering, failure outcomes) across both transports; this node does not
  restate that flow.
- `references`: `architecture-containers-postgres` — the merged container
  node that documents the search pool's connection shape and ownership
  boundary from the Postgres side; this node does not restate that detail.
- No `implements` edge. The target (`docs/multi-tenant-conformance.md` row
  50) has no corpus node id at this revision — inventing one would be a hard
  validation error, and the template forbids it. The first moment to add
  this edge is whenever that document (or NIP-50 itself) gets its own corpus
  node.
- No `part-of` edge. `git ls-tree -r --name-only origin/launchpad --
  launchpad/docs/corpus` shows no other node under `implementation/` at this
  revision — this is the corpus's first implementation-reference instance, so
  there is no broader crate-family implementation node to sit under yet.

## Scope and omissions

**This node covers** what `crates/buzz-search` is responsible for (community-
scoped Postgres FTS query execution), what it deliberately does not own
(indexing — the generated `search_tsv` column and its write path belong to
`buzz-db`), its public interface (`SearchService`, `SearchQuery`,
`ChannelScope`, `SearchMode`, `SearchError`), its two real callers in
`buzz-relay`, its representative tests, and how it maps onto
`docs/multi-tenant-conformance.md` row 50's community-scoping contract.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The write side: how `events.search_tsv` is populated, indexed, and kept privacy-safe at the schema level (the `CASE WHEN kind IN (...)` exclusion logic) | `crates/buzz-db`, `migrations/0001_initial_schema.sql` and its successors — not a node yet |
| The full end-to-end NIP-50 request/response flow, trust boundaries, and per-hit re-authorization gate (`search_hit_accepted`, `event_visible_to_reader`) | `architecture-flows-search-query` |
| The search pool's connection shape, sizing, and Postgres-container-level ownership | `architecture-containers-postgres` |
| Full enumeration of every gated/author-only/ephemeral kind constant the storage-level exclusion depends on | `buzz-core/src/kind.rs`, authoritative and not duplicated here |
| Whether the WS/HTTP `SearchMode::Prefix` asymmetry noted in *Divergences* is intentional product scope or unreconciled drift | Not established anywhere inspected for this node |
| Whether `docs/multi-tenant-conformance.md` itself will get a corpus node id, and when | Unresolved; not filed as its own task by this node — an author hitting this gap should check for an existing issue before filing a new one |

**Expected but not verified when this node was written:**

- No live Postgres instance was run as part of authoring this node — the 18
  integration tests in `fts_integration.rs` were read and cited, not executed,
  since they require `BUZZ_TEST_DATABASE_URL` and this task's environment was
  not confirmed to have one available.
- Whether any CI workflow runs `crates/buzz-search`'s ignored integration
  suite specifically (as opposed to the general workspace `cargo test`/`just
  ci` gate) was not checked against `.github/workflows/`.
- There is no automated `review-code`-equivalent pass available for a
  docs-only corpus node in this task's environment; the `corpus-review` skill
  was attempted per this task's instructions — see the session report for
  whether it was reachable — and a careful manual self-review against issue
  #938's Definition of Done was performed regardless.
