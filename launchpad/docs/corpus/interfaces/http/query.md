---
id: interfaces-http-query
type: interfaces-events
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 650354eab8d41ab6ce1a71de079a6c6d95c69052."
    entry_class: FACT
    evidence:
      - "commit 650354eab8d41ab6ce1a71de079a6c6d95c69052"
  - statement: "`POST /query` is registered in the relay's axum router at the literal path `/query`, dispatching to `api::bridge::query_events`."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs:73"
  - statement: "`query_events` first binds the request to a community from the request `Host` header via `bind_community`, returning 404 with a generic message (never echoing the host, never a default tenant) when no community is configured for that host."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs:973-994"
  - statement: "`query_events` authenticates the caller via NIP-98 (`Authorization: Nostr <base64-encoded-signed-event>`, verified against the tenant-derived expected URL, method POST, and request body) or, only when `require_auth_token` is false, an `X-Pubkey` header for local/dev use; both paths return 401 (`UNAUTHORIZED`) with an `{\"error\": \"...\"}` body on failure, and NIP-98 additionally checks replay via a shared Redis-backed guard, rejecting a second use of the same signed auth event with `NIP-98: replay detected` and failing closed (also 401) if the replay guard itself is unavailable."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs:996-1003"
      - "crates/buzz-relay/src/api/bridge.rs:62-176"
  - statement: "The NIP-98 `u`-tag URL the relay checks against is built from the per-request tenant's own host, not the deployment's static `config.relay_url`, specifically to prevent a NIP-98 event signed for one community's host being accepted on another community's host in a multi-tenant deployment."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs:178-206"
  - statement: "After auth, `query_events` enforces a per-principal HTTP admission/rate limit (`enforce_http_admission`), returning 429 (`TOO_MANY_REQUESTS`) when the caller's quota is exceeded or 503 (`SERVICE_UNAVAILABLE`) if the shared admission limiter itself is unreachable, then enforces relay membership before any filter is evaluated."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs:24-56"
      - "crates/buzz-relay/src/api/bridge.rs:1040-1059"
  - statement: "The request body is a JSON array of NIP-01 filter objects, parsed twice: once as raw `serde_json::Value` (to preserve Buzz-specific extension fields `nostr::Filter` would silently drop) and once into `nostr::Filter`; either parse failing returns 400 (`BAD_REQUEST`) with the underlying serde error message."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs:1061-1069"
  - statement: "A request naming more distinct channel ids across its filters than `extract_channel_ids_from_filters_limited` allows is rejected 400 with `too many explicit channels`."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs:1070-1071"
  - statement: "P-gated kinds (event kinds whose content is private to the `#p`-tagged owner — e.g. DM visibility markers, agent-turn metrics, member notifications) require every filter that could match a p-gated kind to carry a `#p` tag naming only the authenticated caller's own pubkey; a filter omitting `kinds` entirely is treated as able to match every p-gated kind (`is_none_or` short-circuits to true), so an unscoped filter without a matching `#p` fails this gate. A specific-`ids` lookup is exempt from the `#p` requirement unless the filter explicitly names `KIND_DM_VISIBILITY` or `KIND_AGENT_TURN_METRIC`, because those kinds' event ids are not author-bound or carry cleartext metadata that ids-based access must not bypass. Failing this gate returns 403 (`FORBIDDEN`, \"restricted: p-gated kinds require #p tag matching your pubkey\")."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs:1182-1216"
      - "crates/buzz-relay/src/api/bridge.rs:1073-1081"
  - statement: "Root repository AGENTS.md's own \"Common Gotchas\" list independently states the same p-gate consequence in prose: \"Relay queries must specify kinds — omitting kinds triggers the p-gate (403). Always include explicit kind filters,\" corroborating the code-level finding above as documented, intentional behavior rather than an incidental side effect."
    entry_class: FACT
    evidence:
      - "AGENTS.md:242"
  - statement: "Two further, independently-gated read restrictions apply the same way: `engram_filters_authorized` requires a filter that can match `KIND_AGENT_ENGRAM` (kind 30174) to carry either `authors=[self]` or `#p=[self]` (exempting explicit `ids` lookups), and `author_only_filters_authorized` requires author-only kinds to carry `authors=[self]`; either failing returns 403 with a gate-specific message (\"restricted: agent-engram reads require authors=[self] or #p=[self]\" / \"restricted: author-only kinds require authors=[self]\")."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs:1082-1093"
      - "crates/buzz-relay/src/handlers/req.rs:1218-1245"
  - statement: "If any filter in the request array sets NIP-50's `search` field, the entire request is routed to the NIP-50 search path (`handle_bridge_search`), which rejects a request mixing search and non-search filters in the same array with 400 (\"mixed search and non-search filters not supported\"); a request whose filters are all non-search continues down the general catch-all path instead."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs:1109-1126"
      - "crates/buzz-relay/src/api/bridge.rs:1810-1812"
  - statement: "The `bridge_detects_mixed_search_and_non_search_filters` unit test asserts `has_mixed_search_filters` returns true for exactly this case: one filter with `.search(\"hello\")` and one filter with `.kind(Kind::TextNote)` and no `search`."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs:2492-2500"
  - statement: "On the search path, `handle_bridge_search` pushes only `kinds`, `authors`, `since`, `until`, the community, and a channel scope (derived from the filter's `#h` tag intersected with the caller's accessible channels, or the caller's full accessible-plus-global scope when no `#h` is present) down to `buzz-search`'s Postgres full-text-search layer as a `SearchQuery`; every other NIP-01 constraint on the filter (`#p`, `#e`, `#d`, `ids`, etc.) is re-checked afterward against the full stored event by `search_hit_accepted`, which also re-runs the same channel-accessibility and `reader_authorized_for_event` (p-gate) checks used by the non-search path, because the FTS backend cannot itself enforce them."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs:1846-1936"
      - "crates/buzz-relay/src/api/bridge.rs:1814-1844"
      - "crates/buzz-search/src/query.rs:1-9"
      - "crates/buzz-search/src/query.rs:70-90"
  - statement: "The regression test `search_hit_rejects_envelope_with_mismatched_p_tag`, whose own comment names it as fixing a real leak found in PR #593 review, demonstrates why that post-filter step exists: an authorized `{kinds:[30174], #p:[owner_a]}` search is approved by the engram gate before any DB work, but the FTS pushdown only carries `kind:=30174`, so an envelope belonging to a different owner (`owner_b`) could otherwise come back as a text-match hit; `search_hit_accepted` rejects it because the envelope's own `#p` tag does not match `owner_a`."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs:3238-3271"
  - statement: "`buzz-search`'s `SearchQuery` accepts an optional `mode` (`FullText`, using Postgres `websearch_to_tsquery`, or `Prefix`, for bounded typeahead), read from the raw JSON's `search_mode`/`searchMode` extension field, and a 1-based `page` (from `page`/`search_page`/`searchPage`), both Buzz-specific extensions to the NIP-50 filter object rather than part of the NIP-50 spec itself."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs:345-364"
      - "crates/buzz-search/src/query.rs:57-68"
  - statement: "On the non-search (general/catch-all) path, each filter is translated to a `buzz_db::EventQuery` by `build_event_query_from_filter` (the same function the WebSocket `REQ` handler in `req.rs` uses), channel-scoped to the caller's accessible channels, and an optional `before_id` extension field (a 64-char hex event id) further bounds the page — `before_id` is rejected 400 (\"before_id must be a 64-char hex event id\") if malformed, and 400 (\"before_id requires until to be set\") if the filter has no `until`."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs:1349-1418"
  - statement: "Every returned event on the general path passes `buzz_core::filter::filters_match` (full NIP-01 re-match against the stored row) and `event_visible_to_reader` (the same result-level `#p`/author-only/shared-gate visibility check used elsewhere) before being serialized; queries across multiple filters in one request run bounded-concurrently but results are consumed and appended strictly in original filter order, and DB query failures return 500 (`internal_error`, body `{\"error\": \"internal server error\"}`, with the real error only logged server-side)."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs:1421-1463"
      - "crates/buzz-relay/src/api/mod.rs:21-28"
  - statement: "A successful response body, on both the search and non-search paths, is a bare JSON array of full signed Nostr events (`{id, pubkey, created_at, kind, tags, content, sig}` per event, produced by `serde_json::to_value(&stored_event.event)`), not wrapped in an envelope object and not sig-stripped — distinct from `buzz-cli`'s own documented normalized-read contract, which strips `sig` from its JSON output."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs:1463"
      - "crates/buzz-relay/src/api/bridge.rs:1239"
      - "AGENTS.md:212-214"
  - statement: "Raw filter extension fields recognized on this endpoint beyond the NIP-01/NIP-50 filter object are: `top_level` (routes to the channel-window read model), `feed_types` (routes to a named feed: mentions/needs_action/activity, capped by `BRIDGE_FEED_MAX_LIMIT`), `depth_limit` combined with a single `#e` tag (routes to threaded-reply fetching via `get_thread_replies`, optionally including auxiliary events with `include_aux`), `before_id`/`buzz-channel` (general-path extensions), and `page`/`search_page`/`searchPage`/`search_mode`/`searchMode` (search-path extensions) — none of these are part of NIP-01 or NIP-50 and none is documented anywhere outside this code."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs:1061-1063"
      - "crates/buzz-relay/src/api/bridge.rs:1137-1346"
      - "crates/buzz-relay/src/api/bridge.rs:332-364"
  - statement: "No versioning or backward-compatibility contract for `POST /query`'s request or response shape is stated anywhere in this repository's code, comments, or root AGENTS.md; the only stability statement found is the general HTTP-surface framing in root AGENTS.md that the HTTP surface is deliberately narrow and new feature work is directed toward Nostr event kinds rather than new HTTP endpoints."
    entry_class: INFERENCE
    evidence:
      - "AGENTS.md:145-160"
      - "crates/buzz-relay/src/api/bridge.rs:1-4"
    confidence: 0.7
  - statement: "Issue #986's Definition of Done requires this node to define inputs/messages, outputs/responses, error/rejection behavior, authentication/authorization, versioning/compatibility and ordering/idempotency where applicable, and to link the authoritative machine/spec representation with at least one valid and one failure example."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#986 definition of done"
relationships:
  - type: implements
    target: corpus-template-interface
---

# HTTP POST /query: interface

The boundary between an authenticated HTTP client and the Buzz relay's Nostr
event store, reached at `POST /query`. A client submits one or more NIP-01
`Filter` objects as a JSON array in the request body, authenticated per
request via a NIP-98 signed Nostr event (or, only outside production auth
enforcement, an `X-Pubkey` header); the relay returns a JSON array of the
matching signed Nostr events the caller is authorized to read. This is the
HTTP-transport sibling of the WebSocket `REQ` message (NIP-01) that
`crates/buzz-relay/src/handlers/req.rs` implements — the same filter
semantics, access gates, and NIP-50 search routing apply, adapted to a
request/response HTTP call instead of a subscription.

## Operations

| Operation | Defined in | Summary |
|---|---|---|
| `POST /query` | `crates/buzz-relay/src/router.rs:73` -> `crates/buzz-relay/src/api/bridge.rs#query_events` (`bridge.rs:973`) | Submit a JSON array of NIP-01 filters, receive a JSON array of matching signed events. |

This node documents one HTTP route with one request/response shape, not a
catalogue of every field the raw filter JSON may carry; see *Boundary* below.

## Contract and stability

- **Authentication.** NIP-98 (`Authorization: Nostr <base64 signed event>`),
  verified against the tenant-bound host, method `POST`, and request body
  (`crates/buzz-relay/src/api/bridge.rs:996-1003`, `:62-176`). An `X-Pubkey`
  header is accepted only when the deployment has `require_auth_token: false`
  (local/dev use). NIP-98 requests are additionally replay-guarded: the same
  signed auth event cannot be reused (`crates/buzz-relay/src/api/bridge.rs:130-176`).
- **Authorization.** Relay membership is enforced before any filter runs.
  Three independent per-kind read gates apply on top of ordinary NIP-01
  matching: the p-gate (p-gated kinds require `#p` = caller), the engram gate
  (kind 30174 requires `authors=[self]` or `#p=[self]`), and the author-only
  gate (author-only kinds require `authors=[self]`) — see the evidence ledger
  above for the exact functions and line ranges. Channel-scoped results are
  further filtered to channels the caller can access.
- **Errors.** A standard `{"error": "<message>"}` JSON envelope
  (`crates/buzz-relay/src/api/mod.rs:21-28`) accompanies every non-2xx
  response. Observed status codes: `404` (no community configured for the
  request `Host`), `401` (missing/invalid NIP-98 or X-Pubkey auth, replay
  detected, replay guard unavailable), `429`/`503` (admission rate limit
  exceeded / limiter unavailable), `400` (malformed filter JSON, too many
  explicit channels, mixed search and non-search filters in one request,
  malformed or unsatisfiable `before_id`), `403` (a per-kind read gate
  rejected the filter), `500` (an internal DB or query error; the real cause
  is logged server-side only, never echoed to the caller).
- **Ordering.** The general (non-search) path orders each filter's own page
  deterministically by `created_at DESC, id ASC`, which is what makes its
  offset-based `page` extension stable across calls
  (`crates/buzz-relay/src/api/bridge.rs:1406-1418`). Across multiple filters in
  one request, per-filter DB reads run bounded-concurrently but are appended
  to the response strictly in the filters' original array order
  (`crates/buzz-relay/src/api/bridge.rs:1421-1463`), so the response's overall
  order is deterministic given the same request body and store state.
  NIP-50 search results are ordered by the FTS backend's own relevance
  ranking, not `created_at`.
- **Idempotency.** `POST /query` is a pure read; repeating an identical
  request against an unchanged store returns the same event set (module the
  ordering guarantees above). It is not idempotent across replayed *auth*
  events — the same signed NIP-98 event cannot be reused per the replay guard,
  independent of whether the underlying filter is a read.
- **Versioning/compatibility.** No explicit versioning or backward-compatibility
  contract for the request or response shape was found in code, comments, or
  root `AGENTS.md` (see the INFERENCE entry in the evidence ledger). Treat this
  as an open gap rather than an assumed guarantee.

## Boundary

This node does not describe:
- A single Nostr event kind's own wire contract (tag shape, content
  semantics) — kinds referenced here (p-gated kinds, `KIND_AGENT_ENGRAM`,
  author-only kinds) are defined in `crates/buzz-core/src/kind.rs`; an
  event-kind-shaped corpus node for any of them, once one exists, is the
  authority for that kind's own contract, not this node.
- A full parameter-by-parameter catalogue of every raw-JSON extension field
  this endpoint happens to read (`top_level`, `feed_types`, `depth_limit`,
  `before_id`, `page`, `search_mode`, etc.) beyond naming them and where they
  are implemented; a reference-depth node, if the corpus ever builds one for
  this endpoint, is the place for that.
- `POST /events` or `POST /count` — the other two routes `bridge.rs` also
  implements. They share this module and several helper functions (`api_error`,
  `enforce_http_admission`, `verify_bridge_auth`, `nip98_expected_url`) but are
  distinct operations with their own request/response contracts, appropriately
  left to their own corpus nodes once drafted. No corpus node for either exists
  in `launchpad/docs/corpus/interfaces/` at the time this node was written.
- The WebSocket `REQ` message's own contract, even though it shares most of
  the same filter-matching and access-gate code (`req.rs`) — that is a
  separate interface (a persistent subscription over WebSocket, not a
  request/response HTTP call) and, if documented, belongs in its own node.

## Relationships

- `implements: corpus-template-interface` — this node is a concrete instance
  of that template; the target id resolves in the corpus tree at
  `origin/launchpad`'s current revision (`launchpad/docs/corpus/templates/interface.md`).
- No `references` or `part-of` edges are declared. No event-kind-shaped node
  exists yet for any kind mentioned above (p-gated kinds, `KIND_AGENT_ENGRAM`,
  author-only kinds), and no broader capability/architecture node for "the
  Nostr HTTP bridge" exists in the corpus at this revision to sit `part-of`.
  The natural moment to add either is once such a node merges.

## Examples

**Valid request** — a general (non-search) filter for kind 40002 (channel
messages) since a given timestamp, scoped to one channel via `#h`:

```json
[
  {
    "kinds": [40002],
    "#h": ["b6a1e9d2-1f3c-4a9e-9b7d-2c6f8e0a11aa"],
    "since": 1735689600,
    "limit": 50
  }
]
```

A successful response is a bare JSON array of the matching signed events
(`crates/buzz-relay/src/api/bridge.rs:1463`), e.g. `[{"id": "...", "pubkey":
"...", "created_at": 1735689650, "kind": 40002, "tags": [...], "content":
"...", "sig": "..."}]` — possibly empty if nothing matches.

**Failure example** — mixing a NIP-50 search filter with a non-search filter
in the same request body is rejected:

```json
[
  { "search": "release notes" },
  { "kinds": [1] }
]
```

Response: `400 Bad Request`, body `{"error": "mixed search and non-search
filters not supported"}`
(`crates/buzz-relay/src/api/bridge.rs:1109-1126`, exercised by the unit test
`bridge_detects_mixed_search_and_non_search_filters` at
`crates/buzz-relay/src/api/bridge.rs:2492-2500`).

A second failure mode worth naming explicitly, because it is easy to trigger
by accident: a filter that omits `kinds` entirely and could therefore match a
p-gated kind, without a `#p` tag naming the caller, is rejected `403 Forbidden`
with `{"error": "restricted: p-gated kinds require #p tag matching your
pubkey"}` (`crates/buzz-relay/src/handlers/req.rs:1182-1216`,
`crates/buzz-relay/src/api/bridge.rs:1073-1081`) — matching root `AGENTS.md`'s
own "Common Gotchas" warning to always include explicit `kinds` filters.

## Scope and omissions

**This node covers** the `POST /query` HTTP interface end to end as
implemented today: authentication and authorization (NIP-98/X-Pubkey, replay
guard, relay membership, the three per-kind read gates), the general and
NIP-50-search request/response paths, the Buzz-specific extension fields each
path recognizes, ordering and idempotency guarantees, the error envelope and
observed status codes, and one valid plus one failure example.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| `POST /events` and `POST /count`, the sibling bridge endpoints | Their own corpus nodes, not yet drafted |
| Any single event kind's own wire contract (p-gated kinds, `KIND_AGENT_ENGRAM`, author-only kinds) | `buzz-core/src/kind.rs`'s event-kind template, once instantiated for these kinds |
| Field-by-field cataloguing of every raw-JSON extension field this endpoint reads | A reference-depth node, if the corpus later builds one for this endpoint |
| The WebSocket `REQ` message's own interface contract | A separate corpus node, if drafted |
| NIP-01's and NIP-50's own specification text | https://github.com/nostr-protocol/nips (external, not re-described here) |

**Expected but not verified when this node was written:**
- **No live request was made against a running relay.** Every claim above is
  grounded in reading the handler code and its unit tests directly, not in
  observing an actual HTTP response from a running instance.
- **Whether any deployment currently sets `require_auth_token: false`** (which
  would make the `X-Pubkey` dev-mode auth path reachable in that deployment)
  was not checked against any environment's actual configuration — only that
  the code path exists and is gated by that flag.
- **The admission rate-limit's configured numeric threshold** (`human_api_calls_per_min`)
  was not read from any deployment's live configuration; only that the check
  exists and returns `429`/`503` on the two failure modes.
