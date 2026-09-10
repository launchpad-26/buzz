---
id: interfaces-nostr-nip-50
type: interfaces-events
status: draft
origin: upstream
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision c34e62d16781dac3fa45cdedf0f09d4e1d8bbe8f."
    entry_class: FACT
    evidence:
      - "commit c34e62d16781dac3fa45cdedf0f09d4e1d8bbe8f"
  - statement: "NIP-50 defines a `search` field carried on a NIP-01 `REQ` filter, taking a human-readable query string; relays SHOULD interpret it and return matching events, matching primarily against the `content` field; results SHOULD be ordered by relevance ('quality of search result, as defined by the implementation'), explicitly not by `.created_at`; and a query string may carry optional `key:value` extensions (for example `include:spam`, `domain:<domain>`, `language:<code>`, `sentiment:<type>`, `nsfw:<true/false>`) that relays SHOULD ignore if unsupported."
    entry_class: FACT
    evidence:
      - "https://github.com/nostr-protocol/nips/blob/999f9bfbf5fe00d5c2711fd24badb4e56748c9bc/50.md"
  - statement: "This repository does not implement any of NIP-50's optional `key:value` query-string extensions (`include:spam`, `domain:`, `language:`, `sentiment:`, `nsfw:`) -- none of those literal tokens appear anywhere under crates/buzz-search/src or crates/buzz-relay/src, so the entire query string is passed through as one opaque search term."
    entry_class: FACT
    evidence:
      - "crates/buzz-search/src/query.rs"
  - statement: "buzz-relay statically advertises NIP-50 support in its NIP-11 relay information document: `SUPPORTED_NIPS` includes `50` unconditionally, alongside NIP-1/2/10/11/16/17/23/25/29/33/38/42/56."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/nip11.rs"
  - statement: "A NIP-50 search is detected identically on both of the relay's client-facing doors -- any filter in the request whose `search` field (an `Option<String>` on the externally-owned `nostr::Filter` type) is non-empty triggers the search branch, via the same predicate `filters.iter().any(|f| f.search.is_some())` in both places."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs"
      - "crates/buzz-relay/src/api/bridge.rs"
  - statement: "Two operations expose this interface: a WebSocket `REQ` protocol message (`handle_req` dispatching to `handle_search_req`), and an HTTP `POST /query` request whose body is a JSON array of filters (`query_events` dispatching through `query_events_authed` to `handle_bridge_search`)."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs"
      - "crates/buzz-relay/src/api/bridge.rs"
  - statement: "The HTTP `POST /query` door requires a NIP-98 signed `Authorization: Nostr <event>` header verified against a canonical URL for the request's host-resolved community and the literal path `/query`; a dev-mode `X-Pubkey` header fallback exists only when the deployment sets `require_auth_token = false`."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs"
  - statement: "The WebSocket door authenticates a connection via a NIP-42 `AUTH` challenge/response handled by a dedicated handler ('NIP-42 AUTH handler -- verify challenge response, transition auth state'); a `REQ` frame carrying a search filter is only dispatched to the search branch once that connection has already reached authenticated, admitted, relay-member state."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/auth.rs"
      - "crates/buzz-relay/src/handlers/req.rs"
  - statement: "buzz-cli's `messages search` subcommand (`cmd_search`) is a documented client of this interface: it builds a fixed `kinds: [9, 40002, 45001, 45003]` filter, adds a `search` field only when `--query` is supplied, requires at least one of `--query`/`--author`, caps `--limit` at 100, and sends the filter to the relay through `BuzzClient::query`, which is the same HTTP `POST /query` entry point documented above. It exposes no `--kinds` flag of its own."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/commands/messages.rs"
  - statement: "buzz-cli's `resolve_author` helper also calls this same search interface for display-name resolution: a `{\"kinds\":[0],\"search\":<name>}` filter, requiring an exact case-insensitive match against exactly one profile or failing with an ambiguity/not-found error rather than silently picking a candidate."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/commands/messages.rs"
  - statement: "Beyond the bare NIP-50 `search` string, the HTTP `POST /query` bridge accepts two Buzz-specific, non-NIP-50 extension fields read from the raw filter JSON: `search_mode`/`searchMode` (`\"prefix\"` selects `SearchMode::Prefix`, anything else defaults to `SearchMode::FullText`) and `page`/`search_page`/`searchPage` (a 1-indexed page number, defaulting to 1 when absent or non-positive)."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs"
  - statement: "A request mixing a search filter with a non-search filter is rejected outright on both transports rather than partially served: the WebSocket path closes the subscription with the message 'error: mixed search and non-search filters not supported', and the HTTP path returns 400 Bad Request with the equivalent message 'mixed search and non-search filters not supported'."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs"
      - "crates/buzz-relay/src/api/bridge.rs"
  - statement: "An empty or whitespace-only search string never reaches Postgres: `buzz_search::search` calls `normalized_search_text` first, which trims the string, replaces embedded NUL bytes with spaces, caps normalized length at 4096 characters, and returns `None` for an empty-after-trim string, at which point `search()` returns an empty `SearchResult` immediately with no SQL round trip."
    entry_class: FACT
    evidence:
      - "crates/buzz-search/src/query.rs"
  - statement: "The FTS query this interface's search branch issues always includes `community_id = $1` as a non-optional predicate and orders results `rank DESC, created_at DESC, id` (rank from `ts_rank_cd(search_tsv, query)`, `search_tsv` a generated, GIN-indexed `tsvector` column, `query` from `websearch_to_tsquery`), so the created_at/id ordering NIP-50 explicitly de-prioritizes for relevance is retained only as a deterministic tie-break, not as the primary ordering."
    entry_class: FACT
    evidence:
      - "crates/buzz-search/src/query.rs"
  - statement: "The FTS layer's own module doc states its contract explicitly: it returns canonical event ids ordered by relevance only, never full events and never an access decision; the relay refetches full `StoredEvent`s through a `(community_id, event_id)`-scoped fetcher and independently re-runs an access predicate (`filters_match`, channel accessibility, `reader_authorized_for_event`, `event_visible_to_reader`) per hit before any result reaches a caller, on both transports."
    entry_class: FACT
    evidence:
      - "crates/buzz-search/src/query.rs"
      - "crates/buzz-relay/src/api/bridge.rs"
      - "crates/buzz-relay/src/handlers/req.rs"
  - statement: "This interface is read-only: a repeated identical, authorized search request against unchanged underlying data returns the same ranked candidate set (modulo internal pagination bookkeeping), and no code path in `buzz_search::search`, `handle_search_req`, or `handle_bridge_search` performs a write."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-search/src/query.rs"
      - "crates/buzz-relay/src/handlers/req.rs"
      - "crates/buzz-relay/src/api/bridge.rs"
    confidence: 0.85
  - statement: "HTTP `POST /query` terminates with exactly one response: either a 4xx/5xx error, or 200 with a single JSON array of authorized, deduplicated events across all filters in the request body; an empty array is a normal outcome of a query that matched nothing after authorization, not an error."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs"
  - statement: "A WebSocket search subscription is one-shot: `handle_search_req` does not register a persistent subscription, paginates internally up to a fixed page budget while filling the requested limit, and always terminates the subscription id with an `EOSE` -- including when the underlying FTS call errors mid-request, which is logged and simply ends that filter's pagination loop early rather than closing the subscription with an error frame."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs"
  - statement: "Representative live coverage of this interface's request/response contract exists in buzz-test-client's e2e interop suite: `test_nip50_search_returns_results_and_eose`, `test_nip50_search_mixed_filters_rejected`, `test_nip50_search_empty_results`, and `test_nip17_gift_wrap_not_searchable` (a privacy-kind-exclusion regression exercised directly at this search seam) -- all four functions were opened directly and confirmed present in the cited file at this revision."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/e2e_nostr_interop.rs"
  - statement: "A corpus node (`architecture-flows-search-query`, status draft) already documents the full ordered request/response lifecycle for this same interface on both transports -- trigger detection, auth/admission ordering, the sensitive-kind-gate-before-search invariant, and the complete failure/abort table -- and is present in this checkout, which is branched directly from `origin/launchpad`, making it a resolvable relationship target."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/flows/search-query.md"
  - statement: "The corpus interface template (`corpus-template-interface`) is likewise present in this checkout and is not excluded from `validate.py`'s node discovery (only the `schema/` subtree is excluded), so it is also a resolvable relationship target for an optional `implements` self-link."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/templates/interface.md"
      - "launchpad/project-intelligence/corpus/validate.py"
relationships:
  - type: references
    target: architecture-flows-search-query
  - type: implements
    target: corpus-template-interface
---

# NIP-50 search filter: interface

This node documents the boundary the relay exposes for **NIP-50 search** — a
Nostr-protocol-defined extension to the NIP-01 `REQ`/`/query` filter object,
not a Buzz-invented interface. Two sides exchange something across it: a
client (a WebSocket peer, an HTTP caller, or `buzz-cli`) sends a filter
carrying a `search` string, and the relay returns relevance-ranked,
access-checked matching events over WebSocket `EVENT`/`EOSE` frames or a
single HTTP JSON array. The wire format is NIP-50's own — this node cites
that specification and this repository's implementing code rather than
re-describing the format a second time.

**Authoritative sources this node does not restate:** the request/response
*lifecycle* (auth ordering, trust-boundary crossings, the full failure table)
is `architecture-flows-search-query`'s job, not this node's — see
*Relationships* and *Boundary* below. The upstream wire contract is
[NIP-50](https://github.com/nostr-protocol/nips/blob/999f9bfbf5fe00d5c2711fd24badb4e56748c9bc/50.md) itself.
The FTS SQL shape lives in `crates/buzz-search/src/query.rs`. Where this node
and those disagree, they win.

## Operations

| Operation | Defined in | Summary |
|---|---|---|
| WebSocket `REQ` with a `search` field | [NIP-50](https://github.com/nostr-protocol/nips/blob/999f9bfbf5fe00d5c2711fd24badb4e56748c9bc/50.md) (field); `crates/buzz-relay/src/handlers/req.rs` (`handle_req` → `handle_search_req`) | Any filter whose `search` field is non-empty triggers the search branch; results stream as `EVENT` frames followed by one terminal `EOSE`, never registered for live fan-out. |
| HTTP `POST /query` with a `search` field | [NIP-50](https://github.com/nostr-protocol/nips/blob/999f9bfbf5fe00d5c2711fd24badb4e56748c9bc/50.md) (field); `crates/buzz-relay/src/api/bridge.rs` (`query_events` → `query_events_authed` → `handle_bridge_search`) | Body is a JSON array of filters; a `search` field on any of them routes that filter through the same FTS machinery; response is a single JSON array of authorized, deduplicated events. |
| `buzz-cli messages search` | `crates/buzz-cli/src/commands/messages.rs` (`cmd_search`) | Fixed `kinds: [9, 40002, 45001, 45003]`; `--query` becomes the `search` field; `--author` is resolved (hex, npub, or a NIP-50 `kind:0` display-name search) into `authors`; sends via `BuzzClient::query` → `POST /query`. No `--kinds` flag. |
| `search_mode` / `searchMode` extension (HTTP only, Buzz-specific) | `crates/buzz-relay/src/api/bridge.rs` (`extract_search_mode`) | `"prefix"` selects `SearchMode::Prefix` (used for profile typeahead); any other value, or absence, selects `SearchMode::FullText`. Not part of the NIP-50 spec. |
| `page` / `search_page` / `searchPage` extension (HTTP only, Buzz-specific) | `crates/buzz-relay/src/api/bridge.rs` (`extract_search_page`) | 1-indexed page number for the FTS result page; defaults to 1 when absent or ≤ 0. Not part of the NIP-50 spec. |

## Contract and stability

- **Versioning.** NIP-50 is an upstream-owned Nostr specification. `buzz-relay`
  advertises support for it unconditionally in `SUPPORTED_NIPS` (NIP-11), so a
  client may rely on the relay's own information document to detect support
  rather than probing. A change to whether the relay supports NIP-50 at all
  would be a breaking change to that advertisement.
- **Extensions are additive and Buzz-specific.** NIP-50 itself defines optional
  `key:value` query-string extensions (`include:spam`, `domain:`, `language:`,
  `sentiment:`, `nsfw:`) that a relay MAY ignore; this repository implements
  none of them — the whole query string is passed through as one opaque
  search term to `websearch_to_tsquery`. Separately, this repository adds its
  own `search_mode`/`page` JSON extension fields on the HTTP bridge, which are
  not part of NIP-50 and are not portable to another NIP-50-compliant relay.
  A caller depending on either kind of extension is depending on a
  Buzz-specific contract, not a spec guarantee.
- **Ordering.** NIP-50 states results SHOULD be ordered by relevance, "not by
  the usual `.created_at`." This repository's FTS query honors that as the
  primary order (`rank DESC`) and uses `created_at DESC, id` only as a
  deterministic tie-break for otherwise-equal-relevance rows — it does not
  contradict the spec's guidance, it adds determinism the spec leaves
  unspecified.
- **Idempotency.** The interface is read-only. Repeating the same authorized
  request against unchanged data returns the same ranked candidate set;
  nothing in the search path writes.
- **Error/rejection behavior.** A search filter mixed with a non-search filter
  in the same request is rejected outright — closed on WebSocket, 400 on
  HTTP — rather than partially served. An empty or whitespace-only search
  string short-circuits to zero hits before any SQL runs, on both transports.
- **Authentication/authorization.** HTTP requires a NIP-98 signed
  `Authorization: Nostr` header (or a dev-mode pubkey header when auth
  tokens are disabled); WebSocket requires a prior NIP-42 `AUTH`
  challenge/response. Both doors additionally require relay membership
  before a `REQ`/`/query` request reaches the search branch at all. Every
  individual hit is re-authorized per-event after the FTS candidate lookup —
  the FTS layer itself is never the access decision, only a ranked candidate
  source.

## Boundary

This node does not describe:
- **The full ordered request/response lifecycle** — connection-time auth
  state, the exact sequence of trust-boundary crossings, and the complete
  failure/abort table for both transports. That is
  `architecture-flows-search-query`'s job; this node `references` it rather
  than duplicating it.
- **The `COUNT`/`/count` variant** of filter-based querying, which has its own
  handler and is not part of this interface's operation set. Not yet covered
  by any corpus node.
- **A full parameter-by-parameter API-reference catalogue** for domain-expert
  readers (every gated-kind constant, every migration-era divergence in the
  `search_tsv` indexing allowlist). Those live in `buzz-core/src/kind.rs` and
  the relevant migrations, not here.
- **NIP-50's own optional query-string extensions** (`include:spam`,
  `domain:`, `language:`, `sentiment:`, `nsfw:`) beyond stating that this
  repository does not implement any of them.

## Relationships

- `references: architecture-flows-search-query` — the flow node that
  documents this same interface's full ordered request/response lifecycle
  on both transports; this node states the boundary's contract, that node
  states how a request actually travels through it.
- `implements: corpus-template-interface` — this node is an instance of the
  corpus interface template.

## Scope and omissions

**This node covers** the NIP-50 search boundary the relay exposes: which
operations expose it (WebSocket `REQ`, HTTP `POST /query`, and the
`buzz-cli messages search` client), the Buzz-specific extension fields layered
on top of the bare NIP-50 `search` field, the ordering and idempotency
contract, the error/rejection behavior for a malformed or mixed request, and
the authentication/authorization boundary each transport enforces before a
search filter is evaluated.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The full ordered request/response lifecycle, trust-boundary crossings, and failure table | `architecture-flows-search-query` |
| The `COUNT`/`/count` request shape | Not yet written as a corpus node |
| Full parameter-by-parameter API-reference cataloguing | `buzz-core/src/kind.rs` and the relevant migrations, not a corpus node |
| Whether the `search_tsv` indexing allowlist has converged across fresh-install vs. brownfield deployments | Noted as an open gap by `architecture-flows-search-query`; not re-verified here |

**Expected but not verified when this node was written:**
- No live relay was run against this node's claims; every claim above is
  sourced from reading code, the NIP-50 specification text, and existing
  test files, not from executing `just test`/`just ci` as part of authoring
  this document.
- Whether any deployed client other than `buzz-cli` relies on the
  `search_mode`/`page` HTTP extension fields was not checked — this node
  states that the fields exist and what they do, not who consumes them today.

## Examples

**Valid — WebSocket `REQ` with a search filter:**

```json
["REQ", "sub1", {"kinds": [9, 40002], "search": "launch day", "limit": 20}]
```

Expected outcome: zero or more `EVENT` frames for authorized matches, ordered
by relevance then recency, followed by exactly one `EOSE` for `"sub1"`. The
subscription is not registered for live fan-out.

**Valid — HTTP `POST /query` with a search filter:**

```json
[{"kinds": [9, 40002, 45001, 45003], "search": "launch day", "limit": 20}]
```

Sent with a NIP-98 `Authorization: Nostr <event>` header. Expected outcome:
`200 OK` with a JSON array of authorized, deduplicated matching events (an
empty array is a valid, non-error outcome).

**Failure — mixed search and non-search filters in one request:**

```json
[{"search": "launch day"}, {"kinds": [1]}]
```

Expected outcome: HTTP `400 Bad Request` with body text
`"mixed search and non-search filters not supported"`; the WebSocket
equivalent (`search` mixed with a non-search filter in the same `REQ`) closes
the subscription with `"error: mixed search and non-search filters not
supported"` instead of partially serving either filter.
