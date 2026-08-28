---
id: architecture-flows-search-query
type: architecture
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision a44cf52fc740ebebbdd671427480d14f0bce0115."
    entry_class: FACT
    evidence:
      - "commit a44cf52fc740ebebbdd671427480d14f0bce0115"
  - statement: "A NIP-50 search is triggered by any NIP-01 filter whose `search` field is non-empty; both the WebSocket REQ door and the HTTP bridge detect this the same way — `filters.iter().any(|f| f.search.is_some())` — before deciding which code path to run."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs"
      - "crates/buzz-relay/src/api/bridge.rs"
  - statement: "There are exactly two client entry points into the same search machinery: a WebSocket REQ message (`handle_req` dispatching to `handle_search_req`) and an HTTP `POST /query` request (`query_events` dispatching through `query_events_authed` to `handle_bridge_search`)."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs"
      - "crates/buzz-relay/src/api/bridge.rs"
  - statement: "The HTTP entry point first resolves the request's community from the Host header (`bind_community`) before any auth check runs; an unmapped host fails closed with a generic 404 that never echoes which communities exist on the deployment."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs"
  - statement: "The HTTP entry point requires a NIP-98 signed `Authorization: Nostr <event>` header, verified against a canonical URL built from that same resolved tenant and the literal path `/query` (`nip98_expected_url` + `verify_bridge_auth`); a dev-mode `X-Pubkey` header fallback exists only when `require_auth_token` is configured false."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs"
  - statement: "After signature verification, the HTTP path runs replay detection (`check_nip98_replay`) against a per-community seen-set; on a `false` mark it fails with 401 'NIP-98: replay detected', and on a seen-set lookup error it fails closed with 401 rather than admitting the request."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs"
  - statement: "After replay detection, the HTTP path enforces community-level admission and then relay membership (`enforce_http_admission`, `enforce_relay_membership`) before the request body's filters are parsed at all."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs"
  - statement: "On both the WS and HTTP paths, a request mixing a search filter with a non-search filter is rejected outright rather than partially served: WS closes the subscription with 'error: mixed search and non-search filters not supported' via `RelayMessage::closed`, and HTTP returns 400 Bad Request with the same message text."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs"
      - "crates/buzz-relay/src/api/bridge.rs"
      - "crates/buzz-test-client/tests/e2e_nostr_interop.rs"
  - statement: "On the WS path, the sensitive-kind gates (p-gated kinds, agent-engram reads, author-only kinds) run before the search branch is reached, and only for global (non-channel-scoped) subscriptions; the comment at the call site states this ordering exists specifically so an authenticated member cannot use `{\"search\":...,\"kinds\":[30174]}` to harvest indexed-but-globally-stored sensitive events, because search hits are looked up by id and bypass the per-filter historical-delivery post-check that would otherwise catch them."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs"
  - statement: "The search-text-to-SQL layer (`buzz_search::search`) always issues `WHERE community_id = $ctx` as its first predicate, with no code path through the function that omits it; channel scope, kinds, authors, since and until are additional optional predicates layered on top."
    entry_class: FACT
    evidence:
      - "crates/buzz-search/src/query.rs"
  - statement: "Full-text matching is expressed as `search_tsv @@ query`, where `search_tsv` is a Postgres `GENERATED ALWAYS ... STORED` `tsvector` column over `content`, indexed by a GIN index, and `query` is built by `websearch_to_tsquery('simple', ...)` for standard search or a hand-built prefix tsquery for typeahead (`SearchMode::Prefix`)."
    entry_class: FACT
    evidence:
      - "crates/buzz-search/src/query.rs"
      - "migrations/0001_initial_schema.sql"
  - statement: "`buzz_search::search`'s own module doc states the layer's contract explicitly: it returns canonical event ids ordered by relevance only, the relay refetches full `StoredEvent`s through a `(community_id, event_id)`-scoped fetcher, and the relay runs an access predicate per hit — search is documented as never being the access boundary and never able to widen visibility on its own."
    entry_class: FACT
    evidence:
      - "crates/buzz-search/src/query.rs:1-9"
  - statement: "On the HTTP path, each accepted hit is re-checked by `search_hit_accepted`, which requires the stored event to still match the originating NIP-01 filter (`filters_match`), have a `channel_id` that is either absent or in the caller's `accessible_channels`, and pass `reader_authorized_for_event` (the `#p`-tag gate for viewer-private kinds); a further defense-in-depth call to `event_visible_to_reader` then covers author-only kinds and the persona shared-gate before the event is serialized into the response."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs"
  - statement: "On the WS path the same three checks (`filters_match`, channel accessibility, `event_visible_to_reader`) are applied inline per hit inside `handle_search_req`, and a hit that fails any of them is silently dropped from the emitted results rather than surfaced to the caller as an error."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs"
  - statement: "An empty or whitespace-only `search.q` is rejected before any SQL is issued: `buzz_search::search` calls `normalized_search_text`, and on `None` returns an empty `SearchResult` immediately, with no Postgres round trip."
    entry_class: FACT
    evidence:
      - "crates/buzz-search/src/query.rs"
  - statement: "HTTP `POST /query` terminates by returning a single JSON array (`Value::Array`) of the authorized events for all filters in the request body combined and de-duplicated; there is no separate error-vs-partial-success signal inside a 200 response."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs"
  - statement: "WS search subscriptions are one-shot: `handle_search_req`'s own doc comment states no persistent subscription is registered, the function paginates internally up to `MAX_SEARCH_PAGES` while `emitted < limit`, stops a filter's pagination loop early once a page returns fewer than `SEARCH_PAGE_SIZE` hits (exhausted) or an empty page, and always ends by sending a terminal EOSE for the subscription id — including when an underlying `search()` call errors, which is logged and simply breaks that filter's loop rather than closing the subscription with an error."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs"
  - statement: "The `events.search_tsv` generated column's indexing scope has diverged by install path across migrations and is not one fixed fact about 'the' relay: migration 0001 defines a negative-exclusion expression (index everything except a growing privacy blocklist: kind 1059 gift wraps, 30300 event reminders, 30622 DM-visibility, 44100/44101 membership notices), migration 0005 extends that blocklist to add kind 44200 (agent turn metrics), migration 0008 gives only genuinely *empty* databases a positive allowlist instead (kinds 0, 9, 40002, 45001, 45003) and leaves already-populated databases on their prior negative-exclusion expression until an operator runs a separate out-of-band maintenance script, and migration 0014 additionally excludes kind 30350 from whichever expression a given database currently has."
    entry_class: FACT
    evidence:
      - "migrations/0001_initial_schema.sql"
      - "migrations/0005_agent_turn_metric_fts.sql"
      - "migrations/0008_fresh_install_search_allowlist.sql"
      - "migrations/0014_push_lease_fts.sql"
  - statement: "`buzz-cli`'s `messages search` subcommand builds a fixed `kinds: [9, 40002, 45001, 45003]` filter (message-shaped kinds only, deliberately excluding kind 0 profiles) and exposes no `--kinds` flag; it requires at least one of `--query` or `--author`, and sends the filter to the relay via `BuzzClient::query`, which POSTs to `{relay_url}/query` with a NIP-98-signed request — the same HTTP entry point documented above."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/commands/messages.rs"
      - "crates/buzz-cli/src/client.rs"
  - statement: "Representative live coverage of this flow exists in `buzz-test-client`'s e2e interop suite: `test_nip50_search_returns_results_and_eose` (trigger, one-shot termination, no live delivery after EOSE), `test_nip50_search_mixed_filters_rejected` (the mixed-filter abort path), `test_nip50_search_empty_results` (a query that matches nothing still terminates cleanly), and `test_nip17_gift_wrap_not_searchable` (a privacy-kind-exclusion regression exercised directly at the NIP-50 search seam)."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/e2e_nostr_interop.rs"
  - statement: "`buzz-search/src/query.rs`'s own unit tests cover the text-normalization boundary this flow depends on before any SQL is built: trimming and empty-after-trim rejection, replacing embedded NUL bytes with spaces (Postgres text-search input hygiene), and capping normalized search text length at 4096 characters."
    entry_class: FACT
    evidence:
      - "crates/buzz-search/src/query.rs"
  - statement: "Because every search hit is independently re-authorized against the full per-event visibility gate at hydrate time (not merely filtered by the FTS candidate query), a future widening of the `search_tsv` kind allowlist could not by itself leak an event a reader is not otherwise authorized to see — the comment beside the `handle_bridge_search` re-check for kind 30175 states this defense-in-depth reasoning explicitly for one gated kind, and the same call (`event_visible_to_reader` / `search_hit_accepted`) runs unconditionally for every hit on both delivery paths, not only for that kind."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-search/src/query.rs:1-9"
      - "crates/buzz-relay/src/api/bridge.rs"
      - "crates/buzz-relay/src/handlers/req.rs"
    confidence: 0.8
---

# Flow: search query (NIP-50)

How a NIP-50 full-text search filter travels from a client request to
authorized results, on both transports the relay exposes it on.

**Authoritative sources this node does not restate:** the FTS SQL shape and
its parameter contract live in `crates/buzz-search/src/query.rs`; the NIP-98
bridge-auth contract lives in `crates/buzz-relay/src/api/bridge.rs`
(`verify_bridge_auth_with_options`, `nip98_expected_url`); the WS REQ handler
contract lives in `crates/buzz-relay/src/handlers/req.rs`. Where this
document and those disagree, they win.

## Trigger

Either transport, same detection rule: any NIP-01 filter in the request
whose `search` field is non-empty. Detected identically on both paths as
`filters.iter().any(|f| f.search.is_some())`.

- **WebSocket** — a `REQ` protocol message, handled by `handle_req`.
- **HTTP** — a `POST /query` request body (a JSON array of filters), handled
  by `query_events` → `query_events_authed`.

## Preconditions

Both paths require the caller to be an authenticated, admitted, relay
member before a search filter is ever evaluated. The two paths enforce this
with different transport-level machinery reaching the same guarantees — see
*Authentication, authorization and trust-boundary crossings* below for the
ordered detail. In both cases:

- The request is bound to exactly one community/tenant.
- The caller's relay membership is confirmed.
- Sensitive-kind gates (p-gated, agent-engram, author-only) have already run
  for global (non-channel-scoped) subscriptions, so a search filter cannot
  be used as a side door around them.
- A search filter must not be mixed with a non-search filter in the same
  request.

## Termination and outcome

- **HTTP `POST /query`** always terminates with a single response: either a
  4xx/5xx error (see *Failure, abort and rollback behavior*), or `200 OK`
  with a JSON array of the authorized events across all filters in the
  request, deduplicated. An empty array is not an error — it is the normal
  outcome of a query that matched nothing after authorization.
- **WebSocket `REQ`** always terminates the same subscription lifecycle: zero
  or more `EVENT` messages for authorized hits, followed by exactly one
  terminal `EOSE` for that subscription id. A search subscription is
  one-shot — it is never registered for live fan-out, so no further `EVENT`
  can arrive on it after `EOSE`. This holds even when the underlying FTS
  query errors partway through a filter: the error is logged and that
  filter's pagination loop breaks, but the subscription still ends in
  `EOSE`, not a `CLOSED`/error frame.

## Ordered interactions and data/state movement

The two transports share the same core (steps 5–8) but differ in their
outer authentication/admission wrapper (steps 1–4). WS-only and HTTP-only
steps are marked.

1. **[HTTP only]** Resolve the request's community from the `Host` header
   (`bind_community`) before any auth check. An unmapped host fails closed
   with a generic 404 that never reveals which communities exist on this
   deployment.
2. **[HTTP only]** Verify the NIP-98 `Authorization: Nostr <event>` header
   against a canonical URL built from that resolved tenant and the literal
   path `/query`. A dev-mode `X-Pubkey` fallback exists only when the
   deployment is configured with `require_auth_token = false`.
3. **[HTTP only]** Check NIP-98 replay against a per-community seen-set,
   marking the signed event's id as consumed. A repeat id, or a seen-set
   lookup failure, both fail the request closed.
4. **[HTTP only]** Enforce HTTP admission, then relay membership, before the
   request body is parsed as filters at all. **[WS only]** the WebSocket
   door performs its own connection-time NIP-42 AUTH, membership and
   channel-access resolution ahead of dispatching to `handle_req`; by the
   time a `REQ` frame reaches the search branch, the caller is already an
   authenticated, admitted member and their accessible-channel set has
   already been resolved for this connection.
5. Detect the search filter(s), and reject up front if any filter in the
   same request lacks a `search` field (*mixed search and non-search
   filters not supported*). **[WS only]** the sensitive-kind gates
   (p-gated / agent-engram / author-only) have already run just above this
   check, for global subscriptions, specifically so a search filter cannot
   be used to reach a gated kind that the historical-delivery path would
   otherwise catch per-filter.
6. Build a `channel_scope` from the caller's accessible channels: a filter's
   own `#h` tag intersected with what the caller can access if present,
   otherwise the caller's full accessible-channels-plus-global scope. If the
   caller has no accessible channels and no global access, both paths
   short-circuit — HTTP returns an empty array, WS sends `EOSE` immediately
   — without calling into `buzz_search` at all.
7. Normalize the search text (trim, replace embedded NULs, cap at 4096
   characters); an empty result here short-circuits to zero hits with no
   SQL round trip. Otherwise call `buzz_search::search` with the community
   (always the first `WHERE` predicate, non-optional), the channel scope,
   and any `kinds`/`authors`/`since`/`until` from the filter. This issues one
   Postgres query against `events.search_tsv` (a generated, GIN-indexed
   `tsvector` column), ordered by `ts_rank_cd` relevance then `created_at`
   then `id`, returning candidate event ids only — not full events, and not
   an access decision.
8. Refetch the full `StoredEvent`s for those candidate ids, scoped to
   `(community_id, event_id)`. For each hit, re-run the full authorization
   gate — `filters_match` against the originating filter, channel
   accessibility, `reader_authorized_for_event`, and the defense-in-depth
   `event_visible_to_reader` check — dropping any hit that fails, silently
   and without surfacing an error for the dropped hit specifically. This is
   the point where FTS relevance order is preserved but access is decided;
   the FTS layer itself never decides access (see the INFERENCE evidence
   entry above).
9. Emit surviving, deduplicated hits: as `EVENT` messages followed by
   `EOSE` on WS (paginating internally, up to `MAX_SEARCH_PAGES`, per
   filter, stopping early on an exhausted or empty page), or collected into
   the single JSON array response on HTTP.

## Authentication, authorization and trust-boundary crossings

- **Host → community binding (HTTP).** The `Host` header, not any
  client-asserted field, determines the tenant. This is the same
  host-derived community boundary the relay's HTTP surface preserves
  everywhere (see the repository's Nostr-first HTTP surface guidance).
- **NIP-98 request signing (HTTP).** The signed event must match the method,
  the canonical `/query` URL for the *resolved* tenant, and (depending on
  configuration) the request body — this is the crossing from an
  unauthenticated HTTP request to an identified pubkey.
- **NIP-98 replay (HTTP).** A second use of the same signed auth event is
  rejected; a replay-guard failure fails closed (401), not open.
- **Relay membership (both).** A caller who is not a member of this
  community's relay cannot reach the search branch regardless of transport.
- **Sensitive-kind gates ordered before search (WS, global subs only).**
  p-gated kinds, agent-engram reads, and author-only kinds are checked
  *before* the search branch is reached, specifically because a search hit
  is looked up by id and does not otherwise pass through the per-filter
  historical-delivery post-check that would catch a gated kind on a normal
  REQ.
- **Per-hit result-level authorization (both, always).** Every hit — on
  both transports, every time — passes through `reader_authorized_for_event`
  and `event_visible_to_reader` before being handed to the caller. This is
  the boundary that keeps the FTS index itself from ever being the access
  decision.

## Failure, abort and rollback behavior

There is no partial-write or rollback concern here — search is read-only —
so "failure" means the ways a request can end without results, and the
outcome each one produces:

| Condition | HTTP outcome | WS outcome |
|---|---|---|
| Unmapped host | 404, generic message, no community list leaked | n/a (WS resolves tenant at connection time) |
| NIP-98 verification failure | 401, reason included | n/a |
| NIP-98 replay detected, or replay-guard lookup fails | 401 (fail-closed on lookup error too) | n/a |
| Not a relay member | membership-enforced error response | `CLOSED` |
| Mixed search + non-search filters in one request | 400, `"error: mixed search and non-search filters not supported"` | `CLOSED`, same message text |
| No accessible channels and no global access | `200` with an empty array | `EOSE` immediately, no `EVENT`s |
| Empty/whitespace-only search text | zero hits, no SQL issued | zero hits, no SQL issued |
| A hit fails per-hit authorization | that hit is dropped silently; the rest of the response is unaffected | that hit is dropped silently; the rest of the response is unaffected |
| `buzz_search::search` itself errors mid-request | HTTP: `500`, `"search error: ..."` | WS: that filter's pagination loop breaks (logged `warn!`), subscription still ends in `EOSE`, not an error frame |

Representative verification for the trigger/termination and the
mixed-filter abort path: `test_nip50_search_returns_results_and_eose`,
`test_nip50_search_mixed_filters_rejected`, and
`test_nip50_search_empty_results` in
`crates/buzz-test-client/tests/e2e_nostr_interop.rs`. Representative
verification for the privacy-kind exclusion this flow depends on:
`test_nip17_gift_wrap_not_searchable` in the same file. Representative
verification for the text-normalization boundary ahead of any SQL:
`normalized_search_text_trims_and_rejects_empty`,
`normalized_search_text_replaces_nul_bytes`, and
`normalized_search_text_caps_length` in `crates/buzz-search/src/query.rs`.

## Scope and omissions

**This document covers** the request-to-response path for a NIP-50 search
filter on both the WebSocket `REQ` door and the HTTP `POST /query` bridge:
trigger, preconditions, the ordered interactions on both transports, the
auth/trust-boundary crossings each transport applies, and the observed
failure/abort outcomes.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The `COUNT`/`/count` flow, which is a related but distinct request shape with its own handler (`handlers/count.rs`) | A separate flow node, not yet written |
| The desktop/mobile UI search experience (typeahead debounce, result rendering) | Client-side documentation, not this node |
| Full enumeration of every gated-kind constant referenced by the per-hit authorization gate | `buzz-core/src/kind.rs` and `buzz-core/src/filter.rs`, which are authoritative and not duplicated here |
| Whether the fresh-install-vs-brownfield `search_tsv` allowlist divergence (migrations 0001/0005/0008/0014) is intended to ever converge, and by what mechanism | Not established anywhere inspected for this node; the out-of-band maintenance script referenced by migration 0008 (`scripts/maintenance/nip_rs_search_allowlist.sql`) exists but this node does not assert it has been run against any real deployment |
| Prefix search (`SearchMode::Prefix`, used by profile typeahead) beyond the one paragraph in *Ordered interactions* step 7 — its `#kind:0`-specific exact-lexeme prioritization logic is `buzz_search`'s own concern | `crates/buzz-search/src/query.rs` |

**No `relationships` in this node's front matter.** Checked against the
merge target rather than this worktree
(`git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus`):
only `corpus-agents`, `corpus-standard-confidence` and one other standards
node are merged there, and none of them is a node this flow would
meaningfully link to. This is `#608`'s own architecture/flows batch's first
node to reach `origin/launchpad`; the first sibling flow or capability node
to merge is the point to revisit this.

**Expected but not verified when this node was written:**

- Whether `scripts/maintenance/nip_rs_search_allowlist.sql` (referenced by
  migration 0008's comment) has actually been run against any populated
  deployment was not checked — this node states the migration-level fact
  only, not the operational status of any real database.
- No live relay was run against this node's claims; every claim above is
  sourced from reading code, migrations and existing test files, not from
  executing a fresh `just test` / `just ci` pass as part of authoring this
  document. `validate.py` was run and is reported in this PR; the broader
  test suites were not re-run as part of writing this node.
- There is no automated review-code pass available in this task's
  environment; only a manual self-review against the issue's Definition of
  done and this document's own category checklist was performed (see the
  PR description).
