---
id: capabilities-search-search
type: capabilities
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - operator
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5 on the launchpad branch."
    entry_class: FACT
    evidence:
      - "commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
  - statement: "buzz-search's own package description is 'Postgres full-text search for Buzz, scoped by community', and its crate-level doc comment states the index lives in the events table as a GENERATED ALWAYS AS (to_tsvector('simple', content)) STORED column with a GIN (search_tsv) access path, so every row write is the index update -- there is no separate indexer, mpsc queue, reindex job, or consistency window."
    entry_class: FACT
    evidence:
      - "crates/buzz-search/Cargo.toml"
      - "crates/buzz-search/src/lib.rs:1-22"
  - statement: "migrations/0001_initial_schema.sql creates events.search_tsv as a GENERATED ALWAYS tsvector column and idx_events_search_tsv as a GIN index over it; migration 0008 (fresh_install_search_allowlist.sql) rewrites that generated expression on empty installs to CASE WHEN kind IN (0, 9, 40002, 45001, 45003) THEN to_tsvector('simple', content) ELSE NULL::tsvector END, so any event kind outside that positive allowlist is storage-level unsearchable -- a NULL tsvector never matches the @@ operator."
    entry_class: FACT
    evidence:
      - "migrations/0001_initial_schema.sql:222"
      - "migrations/0001_initial_schema.sql:278"
      - "migrations/0008_fresh_install_search_allowlist.sql:11-23"
  - statement: "migrations/0008's own comment states that already-populated databases keep their existing search_tsv expression rather than being rewritten at relay startup, and an operator applies the same allowlist to a populated database only by running the out-of-band script scripts/maintenance/nip_rs_search_allowlist.sql, which exists in this repository."
    entry_class: FACT
    evidence:
      - "migrations/0008_fresh_install_search_allowlist.sql:1-9"
      - "scripts/maintenance/nip_rs_search_allowlist.sql"
  - statement: "SearchQuery's community field is a required, non-Option CommunityId -- there is no construction path through the crate that omits it -- and buzz_search::query::search's own SQL-shape doc comment states community_id = $ctx is the first predicate and 'non-negotiable', which the function body confirms by pushing that predicate immediately after the FROM clause, before any channel/kind/author/time predicate."
    entry_class: FACT
    evidence:
      - "crates/buzz-search/src/query.rs:70-101"
      - "crates/buzz-search/src/query.rs:200-253"
  - statement: "ChannelScope is a four-variant enum (Any, ChannelLessOnly, Channels(Vec<Uuid>), ChannelsOrChannelLess(Vec<Uuid>)) whose doc comment states it is 1-to-1 with a legacy (accessible_channels: &[Uuid], include_global: bool) matrix from a prior Typesense-backed relay, and that ChannelLessOnly is the variant the old Option<Vec<Uuid>> + bool shape could not express unambiguously (empty accessible channels + include_global=true used to silently broaden to all community channels instead of restricting to channel-less events)."
    entry_class: FACT
    evidence:
      - "crates/buzz-search/src/query.rs:19-55"
  - statement: "SearchMode has two variants: FullText, which builds a websearch_to_tsquery('simple', <text>) tsquery, and Prefix, which suffixes only the trailing whitespace-delimited token with :* for bounded typeahead surfaces such as the desktop topbar, quoting each token through quote_literal to prevent tsquery syntax injection from user punctuation."
    entry_class: FACT
    evidence:
      - "crates/buzz-search/src/query.rs:57-68"
      - "crates/buzz-search/src/query.rs:142-180"
  - statement: "search() clamps per_page to a hard maximum of 500 (PER_PAGE_MAX) and page number to 1000 (PAGE_MAX), caps incoming search text at 4096 characters (SEARCH_TEXT_MAX_CHARS) before it reaches the Postgres text-search parser, and replaces embedded NUL bytes with spaces -- an empty or all-whitespace query short-circuits to an empty SearchResult before any SQL round trip."
    entry_class: FACT
    evidence:
      - "crates/buzz-search/src/query.rs:131-140"
      - "crates/buzz-search/src/query.rs:181-198"
      - "crates/buzz-search/src/query.rs:219-225"
  - statement: "buzz-search's own crate-level doc comment states the relay refetches canonical events through buzz-db's scoped fetcher and runs access checks per hit, and that search is never the access boundary -- SearchHit carries only enough fields (event_id, kind, pubkey, channel_id, created_at, rank) to drive that refetch and preserve relevance ordering, not the full event content."
    entry_class: FACT
    evidence:
      - "crates/buzz-search/src/lib.rs:12-22"
      - "crates/buzz-search/src/query.rs:103-129"
  - statement: "The relay's WebSocket NIP-50 path (handlers/req.rs) and its HTTP bridge path (api/bridge.rs's handle_bridge_search) each call state.search.search(...) to get candidate hit ids, then call state.db.get_events_by_ids_routed(...) to refetch full StoredEvents by (community_id, event_id), and only then apply a per-hit acceptance check before including a hit in the response."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs:665-717"
      - "crates/buzz-relay/src/api/bridge.rs:1720-1857"
  - statement: "The bridge path's search_hit_accepted function re-applies the caller's full NIP-01 filter against the refetched StoredEvent (not just the FTS-pushed kind/authors/time predicates), rejects any hit whose channel_id is outside the caller's accessible_channels, and rejects any hit the reader is not authorized for per buzz_core::filter::reader_authorized_for_event -- its own doc comment states this exists because the FTS backend receives only kind/authors/time pushdown, so other filter constraints (#p, #h, #e, #d, ids) must be enforced here against the full stored event, or an authorized-kind search could leak envelopes whose #p tag belongs to a different owner."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs:1686-1716"
  - statement: "The bridge path additionally calls crate::handlers::req::event_visible_to_reader as defense-in-depth after search_hit_accepted, with a comment noting the current FTS positive allowlist (migration 8: kinds 0, 9, 40002, 45001, 45003) does not include the persona shared-gate kind (30175) today, so this second check exists to keep a future allowlist change from silently reopening that gate rather than to catch a hit the allowlist currently admits."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs:1836-1848"
  - statement: "docs/multi-tenant-conformance.md's own conformance table row for 'Search / FTS' (its 'Row 50' per buzz-search's own source comments citing 'conformance row 50') states every search query carries req.community, searchable rows carry community_id, every search query filters by community_id BitmapAnd-ed with the GIN @@ probe, and the relay refetches canonical events by (community_id, event_id) -- matching the community_id-first-predicate behavior read directly in query.rs."
    entry_class: FACT
    evidence:
      - "docs/multi-tenant-conformance.md:50"
      - "crates/buzz-search/src/query.rs:9"
  - statement: "Root AGENTS.md's HTTP-surface section states that POST /query accepts Nostr REQ filters over HTTP and that NIP-50 search filters within them are routed to buzz-search (Postgres FTS) automatically, i.e. the same community-scoped search path is reachable over both the WebSocket REQ path and the HTTP bridge, not only one of the two."
    entry_class: FACT
    evidence:
      - "AGENTS.md:153-157"
  - statement: "buzz-cli's messages search subcommand (cmd_search) is the CLI's dedicated search entry point: it requires at least one of --query or --author, builds a NIP-01 filter restricted to kinds [9, 40002, 45001, 45003] (message, thread-root and reaction-shaped kinds), attaches the query text as the filter's search field when --query is given, and resolves --author (hex, npub1 bech32, or a display name via a separate NIP-50 kind:0 search) before sending the request."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/commands/messages.rs:430-475"
      - "crates/buzz-cli/src/commands/messages.rs:477-500"
  - statement: "Root AGENTS.md's own Common Gotchas section states that messages search chooses its own supported kinds and the current command does not accept a --kinds option, distinguishing it from raw relay filters (used directly over WS/HTTP), which still need explicit kinds."
    entry_class: FACT
    evidence:
      - "AGENTS.md:454"
  - statement: "buzz-cli's channel-name search (cmd_search_channels, backing `channels search`) is a distinct mechanism from the FTS content search this node documents: it fetches all kind:39000 channel-metadata events for the community and post-filters them client-side by name substring/exact match, rather than querying events.search_tsv."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/commands/channels.rs:113-146"
  - statement: "The desktop client's search UI lives under desktop/src/features/search/ (TopbarSearch.tsx, SearchResultItem.tsx, SearchScopeControls.tsx, useSearchResults.ts, parseSearchOperators.ts) with supporting modules for search-hit navigation (desktop/src/app/navigation/resolveSearchHitDestination.ts) and result highlighting (desktop/src/shared/lib/rehypeSearchHighlight.ts), confirming the desktop app is a second, UI-facing consumer of the same search capability alongside buzz-cli."
    entry_class: FACT
    evidence:
      - "desktop/src/features/search/ui/TopbarSearch.tsx"
      - "desktop/src/features/search/ui/SearchResultItem.tsx"
      - "desktop/src/features/search/useSearchResults.ts"
  - statement: "VISION.md's Scale table lists 'Search | Postgres FTS, permission-aware, full-text' and its Status table marks both 'Core relay, auth, pub/sub, search, audit' and the desktop client's Search surface as shipped (checkmark rows), which this node treats as the maturity source for 'search is a shipped capability' rather than an assumption."
    entry_class: FACT
    evidence:
      - "VISION.md:204"
      - "VISION.md:220"
      - "VISION.md:223"
  - statement: "VISION.md's top-level feature callout states 'Search | Cmd+K. Instant. Full-text.', naming the desktop keyboard shortcut and describing the capability as instant full-text search at the product-marketing level, the same 'what, not how' framing the capability template's industry-model section prescribes."
    entry_class: FACT
    evidence:
      - "VISION.md:23"
  - statement: "ARCHITECTURE.md's buzz-search section states permission filtering is the caller's responsibility -- buzz-search returns candidate hits and the relay re-authorizes each one (channel membership, #p, owner gates) before delivering it -- and explicitly lists what buzz-search does NOT do: it does not enforce channel membership or access control, and it does not write events, since indexing is the search_tsv generated column on the events insert rather than a separate write path this crate owns."
    entry_class: FACT
    evidence:
      - "ARCHITECTURE.md:464-489"
  - statement: "crates/buzz-search/tests/fts_integration.rs is a 1509-line integration test suite (34 #[tokio::test] functions at the time this node was written) covering same-community matches, cross-community isolation, channel-scope restriction (including channel_less_only), kind0 display-name search, prefix-mode typeahead including tsquery-boundary punctuation and storage-level privacy exclusions under prefix mode, deleted-event exclusion, since/until filtering, pagination, NUL-byte sanitization, enormous page-number clamping, very-long-query bounding, and excluded-kinds storage-level unsearchability -- confirming the behaviors cited above as FACT are also under test, not merely documented in comments."
    entry_class: FACT
    evidence:
      - "crates/buzz-search/tests/fts_integration.rs:1-1509"
  - statement: "AGENTS.md's Testing section lists crates/buzz-test-client/tests/e2e_nostr_interop.rs as covering 'NIP-50 search' among its Nostr-interop E2E scenarios, so search behavior is additionally exercised end-to-end against a running relay, not only at the buzz-search crate boundary."
    entry_class: FACT
    evidence:
      - "AGENTS.md:239"
  - statement: "This node's own relationships are empty because, at the recorded revision, git ls-tree against origin/launchpad's launchpad/docs/corpus/capabilities/search/ path returns no files -- none of this capability's sibling nodes (channel-scope, full-text-search, privacy-filtering, result-reauthorization, search-index, search-query) nor any architecture/interface node this capability could reference are yet merged, so no relationships.target would resolve."
    entry_class: FACT
    evidence:
      - "git_ls_tree(ref='origin/launchpad', path='launchpad/docs/corpus/capabilities/search') -> empty, at commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
---

# Search: capability

Buzz lets a member or agent find prior conversation, reaction, and public-profile
content across a community by matching free text against message-shaped events,
rather than scrolling or re-reading channel history. A caller reaches it through
`buzz-cli`'s `messages search` subcommand, the desktop app's Cmd+K search surface,
or a raw NIP-50 `search` filter sent over WebSocket REQ or the `POST /query` HTTP
bridge -- all four paths converge on the same community-scoped Postgres
full-text-search query underneath.

## Behavioral rules, constraints and variants

At the level this overview stays at (each rule's own mechanism is a named
sibling's depth, per *Boundary* below):

- **Community-scoped, always.** Every search query is bound to the caller's
  community before anything else; a search can never return another
  community's events, by construction rather than by a later filter.
- **Storage-level privacy filtering.** Only a positive allowlist of event kinds
  (today: kind 0 profiles, kind 9/40002/45001/45003 message/thread/reaction
  shapes) is indexed at all -- any other kind's row is unsearchable at the
  storage level, not merely excluded from results after the fact.
- **Two matching variants.** `FullText` (ordinary multi-word relevance search,
  the NIP-50-style default) and `Prefix` (trailing-token prefix match, for
  bounded typeahead surfaces) are the two ways a query's text is turned into a
  Postgres tsquery; both share every other rule on this list.
- **Search is never the access boundary.** A hit returned by the search layer
  is a candidate, not a result -- the relay always refetches the canonical
  event and re-authorizes it (channel membership, `#p` targeting, owner gates)
  before it reaches a caller, regardless of which entry point issued the
  query.
- **Four reachable entry points, one underlying query.** WebSocket NIP-50
  `search` filters, the HTTP `POST /query` bridge, `buzz-cli`'s `messages
  search` subcommand, and the desktop app's Cmd+K surface all resolve to the
  same community-scoped query described above -- none of the four has its own
  separate search semantics.

## Maturity

**Shipped.** VISION.md's own Status table marks "Core relay, auth, pub/sub, search,
audit" and the desktop client's "Search" surface as shipped (checkmark rows), and
its Scale table names search as "Postgres FTS, permission-aware, full-text" among
the platform's stated production characteristics. The implementation crate
(`buzz-search`), its 1509-line integration test suite, the relay's two call sites
(WebSocket REQ and HTTP bridge), the CLI subcommand, and the desktop feature
directory all exist in this repository today -- this is not a designed-but-unbuilt
capability.

## Boundary

This node does not describe:

- **How the capability is built.** The Postgres schema (`events.search_tsv`, its
  GIN index, the positive-kind allowlist migration), the `buzz-search` crate's
  query construction, and the relay's `AppState` wiring are architecture-level
  detail. No architecture node for `buzz-search` or the `events` table exists yet
  at the recorded revision (see *Relationships* below), so this boundary is stated
  without a node to point at.
- **The interface(s) the capability is exposed through.** The NIP-50 `search`
  filter field over WebSocket REQ and `POST /query`, and `buzz-cli`'s `messages
  search` subcommand, are boundary contracts an interface-typed node would own.
  None is merged yet.
- **The step-by-step flow through this capability.** How a single search request
  actually moves -- CLI/desktop issues a filter, relay dispatches to
  `buzz-search`, `buzz-search` returns candidate hits, relay refetches and
  re-authorizes, relay responds -- is flow-shaped content. No flow node for
  search is merged yet.
- **Channel-scoping, full-text matching, privacy filtering, result
  re-authorization, the search index, or search-query construction as their own
  depth topics.** Those are this capability's own named sibling concerns
  (`channel-scope`, `full-text-search`, `privacy-filtering`,
  `result-reauthorization`, `search-index`, `search-query`), each intended as its
  own node under `launchpad/docs/corpus/capabilities/search/`. This node states
  that each of those mechanisms exists and cites where it lives, without
  re-deriving how any one of them works in depth -- that is each sibling's job
  once drafted.
- **How the running system is operated.** Applying the out-of-band allowlist
  maintenance script to an already-populated database
  (`scripts/maintenance/nip_rs_search_allowlist.sql`) is an operational
  procedure, not a statement about what the capability lets a user do.
- **Channel-name search (`channels search` / `cmd_search_channels`).** That
  command post-filters `kind:39000` channel-metadata events by name client-side
  and never queries `events.search_tsv` -- a different mechanism entirely, not a
  variant of the content-search capability this node documents.

## Relationships

None declared. Checked against `origin/launchpad`'s corpus tree at the recorded
revision: `launchpad/docs/corpus/capabilities/search/` contains no merged files, so
none of this capability's own named siblings (`channel-scope`, `full-text-search`,
`privacy-filtering`, `result-reauthorization`, `search-index`, `search-query`) are
valid relationship targets yet, and no architecture or interface node covering
`buzz-search`, the `events` table, or the NIP-50/`messages search` boundary is
merged either. The first of those siblings to merge is the natural moment to add
`references` edges back to this overview node, and for this node to add
`references` edges out to them.

## Scope and omissions

**This node covers** what the search capability lets a user or agent do (find
message/reaction/profile content by free text across a community), the four
entry points that reach it (WebSocket NIP-50 `search`, HTTP `POST /query`,
`buzz-cli messages search`, the desktop Cmd+K surface), its shipped maturity per
VISION.md, and the boundary against its own architecture/interface/flow layers and
against its as-yet-undrafted depth siblings.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| How `buzz-search`, `events.search_tsv`, and the GIN index are built | an architecture node for `buzz-search` / the event store, not yet drafted |
| The NIP-50 filter contract and `messages search`'s CLI surface as boundary contracts | an interface node, not yet drafted |
| The step-by-step path one search request takes end to end | a flow node, not yet drafted |
| Channel-scoping mechanics (`ChannelScope`'s four variants) in depth | the `channel-scope` sibling capability node, not yet drafted |
| Full-text matching mechanics (`websearch_to_tsquery`, prefix-mode typeahead) in depth | the `full-text-search` sibling capability node, not yet drafted |
| Storage-level privacy exclusion (the kind allowlist, its migration and maintenance script) in depth | the `privacy-filtering` sibling capability node, not yet drafted |
| Post-hit re-authorization (`search_hit_accepted`, `event_visible_to_reader`) in depth | the `result-reauthorization` sibling capability node, not yet drafted |
| The search index's storage shape and indexing mechanism in depth | the `search-index` sibling capability node, not yet drafted |
| Search-query construction (`SearchQuery`, `SearchMode`, pagination/clamping) in depth | the `search-query` sibling capability node, not yet drafted |
| Applying the allowlist migration to an already-populated database | `scripts/maintenance/nip_rs_search_allowlist.sql`, an operational procedure |
| Channel-name search (`channels search`) | out of scope for this node entirely -- a different mechanism, named only to exclude it |

**Expected but not verified when this node was written:**
- **No live search request was executed against a running relay while drafting
  this node.** Every behavior cited above comes from reading source, tests, and
  documentation, not from an interactive session against `just relay`.
- **`docs/multi-tenant-conformance.md`'s row numbering was read literally** (the
  "Search / FTS" row is the 50th content line counting from the file's start, per
  the citation above) to corroborate `buzz-search`'s own source comment
  referencing "conformance row 50" and "conformance row zero" -- whether the
  document's authors intend "row" to mean a literal line number or a numbered
  table entry with its own independent numbering was not separately confirmed.
- **Whether the six named sibling capability nodes (`channel-scope`,
  `full-text-search`, `privacy-filtering`, `result-reauthorization`,
  `search-index`, `search-query`) will each land with exactly those ids** was
  not confirmed against any merged task list -- their names are taken from this
  task's own dispatch instructions, not from reading each sibling's issue.
