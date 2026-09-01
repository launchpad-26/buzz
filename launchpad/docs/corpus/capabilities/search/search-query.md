---
id: capabilities-search-search-query
type: capabilities
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5 on branch launchpad."
    entry_class: FACT
    evidence:
      - "commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
  - statement: "Both of the relay's search entry points detect and dispatch a NIP-50 search filter by reading the same NIP-01 filter field (`filter.search`), directly in the code that begins building the Postgres query: the WebSocket handler skips any filter whose `search` is `None` or empty, and the HTTP bridge handler does the identical `Some(s) if !s.is_empty()` check on its own copy of the raw filter."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs"
      - "crates/buzz-relay/src/api/bridge.rs"
  - statement: "`handle_search_req`'s own doc comment states the WebSocket search path directly: 'Handle a NIP-50 search REQ: query Postgres FTS, fetch full events, deliver results, EOSE. Search subscriptions are one-shot — no persistent subscription is registered.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs"
  - statement: "The query contract accepted from a client is a single NIP-50 `search` string handed to Postgres essentially unparsed: `SearchQuery.q` is normalized (trimmed, NUL bytes replaced, capped at 4096 characters) and then passed whole into `websearch_to_tsquery('simple', ...)` for standard matching, or split on whitespace and matched token-by-token for prefix mode — in neither mode does `buzz-search` itself parse or special-case any substring of the query text before that point."
    entry_class: FACT
    evidence:
      - "crates/buzz-search/src/query.rs"
  - statement: "None of the NIP-50 spec's optional extension words (for example `include:spam`, `domain:`, `language:`, `sentiment:`, `nsfw:`) are recognized or stripped anywhere in the search text path — a repository-wide search for those literal tokens across every Rust crate found no occurrence tied to query-text parsing, and `buzz-search`'s own `normalized_search_text` performs only trim/NUL-replace/length-cap, never token extraction."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-search/src/query.rs"
      - "grep_case_insensitive('domain:|language:|sentiment:|nsfw:|include:spam', scope='crates/**/*.rs') -> no match tied to search-text parsing, run against repository revision 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
    confidence: 0.8
  - statement: "The HTTP `POST /query` bridge recognizes two extension fields on the raw filter JSON that are not part of NIP-01/NIP-50 itself: `search_mode` (alias `searchMode`) selects `SearchMode::Prefix` when its value is exactly `\"prefix\"` and otherwise defaults to `SearchMode::FullText`, and `page` (aliases `search_page`/`searchPage`) selects a 1-indexed result page, defaulting to `1` and ignoring non-positive values; unit tests `bridge_search_mode_extension_defaults_to_full_text` and `bridge_search_mode_extension_accepts_prefix_snake_or_camel_case` exercise the alias handling directly."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs"
  - statement: "Those two extension fields are bridge-only: `handle_search_req` (the WebSocket path) reads only `filter.search`, `filter.limit`, `filter.kinds`, `filter.authors`, `filter.since`/`filter.until`, and `#h` tags from the incoming filter — there is no `search_mode` or `page` equivalent read anywhere in that function, and its own doc comment states pagination on that path is internal (paginating up to a fixed page cap) rather than client-selected."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs"
  - statement: "`buzz-cli`'s `messages search` subcommand is the primary agent-facing entry point to this capability: it requires at least one of `--query` (the NIP-50 search text) or `--author`, builds a filter with a fixed `kinds: [9, 40002, 45001, 45003]` (message-shaped kinds only) and no `--kinds` flag, resolves `--author` through hex/npub/display-name (the display-name path itself issuing a NIP-50 kind:0 search), and sends the assembled filter via `BuzzClient::query` to `POST /query`."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/commands/messages.rs"
      - "crates/buzz-cli/src/lib.rs"
  - statement: "`buzz-cli` also drives a NIP-50 kind:0 profile search from the `users` command group's display-name lookup, sending `{\"kinds\":[0],\"search\":<query>,\"limit\":100}` and then narrowing the response to an exact case-insensitive name match client-side."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/commands/users.rs"
  - statement: "`buzz-cli`'s `channels search` subcommand is a distinctly different, non-NIP-50 mechanism: it is a case-insensitive substring or exact match over already-fetched channel-metadata events' names (`--query`, `--exact`, `--include-archived`), not a `search` filter field sent to the relay, and is therefore out of this capability's scope even though its name suggests otherwise."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/lib.rs"
  - statement: "Desktop uses the bridge's `search_mode: \"prefix\"` extension for every typeahead-shaped surface (member picker, @mention popup, DM recipient search, and the topbar people/message search), and its own code comment states the reason explicitly: without prefix mode the relay runs whole-word `websearch_to_tsquery` matching and a partially typed name like `tyl` returns zero results for `Tyler`."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/commands/profile.rs"
      - "desktop/src-tauri/src/commands/messages.rs"
  - statement: "This repository's own NIP conformance summary marks `NIP-50 search` as shipped (✅), gives a client-facing example (`nak req -k 9 --tag \"h=<channel-uuid>\" --search \"search query\" -l 20 --auth --sec <privkey> ws://localhost:3000`), and lists it as verified by three independent client paths: `BuzzTestClient`'s automated E2E suite, the dedicated `e2e_nostr_interop.rs` interop tests, and manual verification against the third-party `nak` CLI."
    entry_class: FACT
    evidence:
      - "NOSTR.md"
  - statement: "Protocol-level verification of this capability's contract (not its relay-internal mechanics) exists in `crates/buzz-test-client/tests/e2e_nostr_interop.rs`: `test_nip50_search_returns_results_and_eose`, `test_nip50_search_mixed_filters_rejected`, `test_nip50_search_empty_results`, `test_nip50_search_relevance_order`, and `test_nip17_gift_wrap_not_searchable`."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/e2e_nostr_interop.rs"
  - statement: "Storage-layer verification of the prefix-mode extension and page-number clamping exists in `crates/buzz-search/tests/fts_integration.rs` (`#[ignore = \"requires Postgres\"]`, so not part of the default unit-test run): `prefix_mode_matches_final_token_prefix_without_changing_full_text`, `prefix_mode_handles_tsquery_boundary_punctuation`, `prefix_mode_preserves_storage_level_privacy_exclusions`, and `enormous_page_number_is_clamped`."
    entry_class: FACT
    evidence:
      - "crates/buzz-search/tests/fts_integration.rs"
  - statement: "The step-by-step request-to-response path for a NIP-50 search filter on both transports — trigger, authentication/authorization ordering, and failure outcomes — is already documented in full by the merged architecture flow node `architecture-flows-search-query`; this capability node does not restate that sequence."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/flows/search-query.md"
  - statement: "Parent task #820 (this document) and sibling task #816 (`capabilities/search/full-text-search.md`, not yet merged) are deliberately scoped apart: #820 covers the NIP-50 `search` filter contract itself (query syntax, extensions, how clients issue it), while #816 covers the Postgres FTS indexing internals — the two were read side by side to confirm neither subsumes the other before drafting this node."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#820 and #816 issue bodies (read directly via gh issue view)"
relationships:
  - type: references
    target: architecture-flows-search-query
  - type: references
    target: architecture-containers-cli
---

# Search query: capability

Buzz lets an authenticated, admitted community member search indexed content
by relevance — messages, forum posts, and user profiles — by sending a
standard [NIP-50](https://github.com/nostr-protocol/nips/blob/master/50.md)
`search` string as the `search` field of a Nostr filter, over either
transport the relay exposes (`WebSocket REQ` or `HTTP POST /query`). A client
does not need to know anything about the underlying Postgres full-text index
to use this capability — it sends a filter with `search` set, and gets back
relevance-ordered, access-checked results.

## Maturity

**Shipped.** This repository's own NIP conformance summary marks `NIP-50
search` ✅ (`NOSTR.md`), the request-to-response path is documented by the
merged architecture flow node `architecture-flows-search-query`, and the
capability is exercised by dedicated end-to-end tests
(`test_nip50_search_returns_results_and_eose` and siblings in
`crates/buzz-test-client/tests/e2e_nostr_interop.rs`) as well as manual
verification against the third-party `nak` CLI (see the evidence ledger).

## The query contract

A caller supplies one thing to invoke this capability: a non-empty `search`
string on a Nostr filter. `buzz-search` normalizes that string (trim,
replace embedded NUL bytes, cap at 4096 characters) and hands it to Postgres
essentially as-is — either as the argument to `websearch_to_tsquery('simple',
...)` for standard matching, or split into whitespace-delimited tokens for
prefix matching. Buzz does not parse or honor any of NIP-50's optional
extension words (`include:spam`, `domain:`, `language:`, `sentiment:`,
`nsfw:`, and so on) inside that string — nothing in the search-text path
recognizes them, so a caller who sends one gets it treated as literal search
text, not as a directive.

Two matching modes exist, selected differently per transport:

- **Full-text (default).** Whole-word matching via Postgres
  `websearch_to_tsquery`. Used by anything that does not explicitly ask for
  prefix mode.
- **Prefix.** Matches completed tokens exactly and the final (possibly
  partial) token as a prefix — the shape a typeahead surface needs so a
  partially typed name still matches. Selected only over the HTTP bridge, by
  setting the extension field `search_mode` (or camelCase `searchMode`) to
  `"prefix"` on the filter JSON; any other value, or its absence, falls back
  to full-text. The WebSocket `REQ` path has no equivalent field and always
  runs full-text matching.

The HTTP bridge accepts one further extension field the WebSocket path does
not: `page` (aliases `search_page`/`searchPage`), a 1-indexed page number for
paging through results; non-positive or missing values default to page 1.
The WebSocket path instead paginates internally up to a fixed page cap and
always terminates the subscription with `EOSE`, with no client-selected page
number. Both transports honor the filter's own `limit` field as the page
size, clamped server-side.

A request mixing a `search` filter with a non-search filter in the same
batch is rejected outright rather than partially served, and every result —
on both transports, every time — passes through the same per-event
authorization gate that governs any other read, so a widened search index
can never by itself grant access to an event a caller could not otherwise
see. Both of those guarantees, and the full ordered request path that
enforces them, are documented step-by-step in `architecture-flows-search-query`
rather than restated here.

## How clients issue it

- **`buzz-cli messages search`** — the primary agent-facing entry point.
  Requires `--query` and/or `--author`; builds a fixed
  `kinds: [9, 40002, 45001, 45003]` filter (message-shaped kinds only, no
  `--kinds` flag — root `AGENTS.md` calls this out explicitly as a deliberate
  difference from raw relay filters) and sends it to `POST /query`. Resolving
  a display-name `--author` itself issues a NIP-50 kind:0 search.
- **`buzz-cli users` name lookup** — sends `{"kinds":[0],"search":<query>}`
  to find a profile by display name, then narrows to an exact
  case-insensitive match client-side.
- **Desktop typeahead surfaces** (member picker, `@mention` popup, DM
  recipient search, topbar people/message search) — all set
  `search_mode: "prefix"` on the bridge filter, specifically because
  full-text mode would return no results for a partially typed name.
- **Third-party clients** — any NIP-50-aware client can use the plain filter
  contract (`{"search": "...", ...}`) over either transport; the bridge-only
  `search_mode`/`page` extensions are additive and optional, not required to
  get a working search.

**Not part of this capability:** `buzz-cli channels search` looks similar by
name but is not a `search` filter at all — it is a case-insensitive
substring/exact match over already-fetched channel-metadata event names,
resolved entirely client-side.

## Boundary

This node does not describe:
- **How the capability is built.** The Postgres FTS SQL shape, the
  `search_tsv` generated column, its GIN index, and the per-migration
  indexing-scope allowlist are `buzz-search`'s and the FTS indexing node's
  territory (`capabilities/search/full-text-search.md`, sibling task #816,
  not yet merged at this writing — see the evidence ledger for how the two
  were scoped apart).
- **The interface(s) this capability is exposed through**, beyond naming
  them above. No dedicated interface-type corpus node exists yet for
  `buzz-cli`'s command surface or the relay's HTTP bridge; when one merges,
  it is the better home for a full accounting of every flag and route.
- **The step-by-step flow through this capability.** Trigger, ordered
  interactions, authentication/authorization crossings, and failure/abort
  outcomes on both transports are already documented in full by
  `architecture-flows-search-query`.
- **How the running system is operated** — index maintenance, the
  out-of-band allowlist-convergence script referenced by migration 0008, or
  any other operational concern.

## Relationships

- references: `architecture-flows-search-query` — the merged flow node
  documenting the full request-to-response path this capability's query
  contract is served through.
- references: `architecture-containers-cli` — the merged container node for
  `buzz-cli`, the primary agent-facing surface that issues this capability's
  queries.

## Scope and omissions

**This node covers** the NIP-50 `search` filter as a product capability: the
query contract a caller sends (plain search text, no NIP-50 extension words
honored), the two matching modes and which transport supports which, the
bridge-only `search_mode`/`page` extension fields and their absence on the
WebSocket path, the concrete client surfaces that issue searches today
(`buzz-cli messages search`, `buzz-cli users` name lookup, Desktop typeahead
surfaces), and the explicit boundary against `buzz-cli channels search`
(similarly named, not the same mechanism).

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Postgres FTS internals — `search_tsv`, GIN indexing, per-migration allowlist divergence | `capabilities/search/full-text-search.md` (sibling task #816, not yet merged) |
| The full request-to-response path, ordered interactions, and every failure outcome on both transports | `architecture-flows-search-query` (merged) |
| Full per-flag accounting of `buzz-cli`'s command surface | `architecture-containers-cli` (merged, container-level) and a future interface-type node (not yet written) |
| The `COUNT`/`/count` request shape, a related but distinct flow | Not covered by this node or by `architecture-flows-search-query` |
| Mobile client search behavior | Not inspected for this node — only Desktop and `buzz-cli` were read |

**Expected but not verified when this node was written:**

- **Whether any Mobile (Flutter) surface issues NIP-50 search queries.**
  `mobile/` was not inspected for this node; only Desktop's Tauri backend and
  `buzz-cli` were read.
- **Whether every third-party NIP-50-aware client (beyond `nak`, already
  listed in `NOSTR.md`) interoperates cleanly with Buzz's specific
  extension-word non-support.** No live cross-client test against a
  NIP-50-extension-sending client was run for this node; the "extensions are
  not honored" claim rests on reading `buzz-search`'s normalization code and
  a repository-wide grep, not on observing a rejected or mis-handled request
  from such a client.
- **Whether the `search_page`/`searchPage` aliases (as opposed to `page`) are
  used by any shipping client today.** The code path accepting them was read
  directly; no caller using those alias names specifically was found in
  `desktop/` or `crates/buzz-cli/` during this pass.
