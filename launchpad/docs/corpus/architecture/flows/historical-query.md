---
id: architecture-flows-historical-query
type: architecture
status: draft
origin: launchpad
audiences:
  - agent
  - developer
evidence:
  - statement: "This node was authored and checked against repository revision a44cf52fc740ebebbdd671427480d14f0bce0115."
    entry_class: FACT
    evidence:
      - "commit a44cf52fc740ebebbdd671427480d14f0bce0115"
  - statement: "A historical query is triggered either by a NIP-01 REQ message over the WebSocket connection, handled by handle_req, or by an authenticated POST to the HTTP bridge's /query endpoint, handled by query_events."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs"
      - "crates/buzz-relay/src/api/bridge.rs"
  - statement: "A WebSocket REQ is only processed once the connection holds AuthState::Authenticated; an unauthenticated REQ is rejected with a NOTICE plus a CLOSED message carrying 'auth-required: authenticate before subscribing' and no subscription is registered."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs"
  - statement: "WebSocket authentication is NIP-42 challenge/response: the relay sends an AUTH challenge, the client signs a kind:22242 event carrying the challenge and relay URL, and handle_auth verifies it via verify_nip42_event (kind, signature, challenge match, relay-URL match after localhost normalization, and a +/-60s timestamp tolerance) before flipping the connection's AuthState to Authenticated. AUTH events are never stored or logged because they may carry bearer tokens embedded by callers."
    entry_class: FACT
    evidence:
      - "crates/buzz-auth/src/nip42.rs"
      - "crates/buzz-relay/src/handlers/auth.rs"
  - statement: "If the WebSocket connection carries a scoped auth token, a REQ is rejected with 'restricted: insufficient scope' unless the token's scopes are empty or include Scope::MessagesRead."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs"
  - statement: "The HTTP /query endpoint binds the request to a tenant from the Host header before any tenant-scoped read; an unmapped host fails closed with a generic 404 that does not echo the host, preventing an unauthenticated caller from probing which communities exist on the deployment."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs"
  - statement: "The HTTP /query endpoint authenticates each request via verify_bridge_auth, which accepts a NIP-98 event (kind:27235) presented as a base64-encoded 'Authorization: Nostr <event>' header and verified against the expected method, URL and body by buzz_auth::verify_nip98_event, or, only when the deployment has require_auth_token disabled, a dev-mode X-Pubkey header with no replay protection."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs"
  - statement: "After NIP-98 verification, query_events_authed enforces HTTP admission, NIP-98 replay protection (a shared Redis seen-set keyed by event id, failing closed on a Redis error) and relay membership before any filter is executed."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs"
  - statement: "Per NIP-01 OR semantics, each filter in a REQ or /query request is converted independently into one buzz_db::EventQuery via filter_to_query_params (WS) or the shared build_event_query_from_filter (WS and HTTP), so a single filter's per-filter limit and time window (since/until) are never merged with another filter's."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs"
  - statement: "A filter's requested limit is clamped to buzz_db::DEFAULT_MAX_PAGE_LIMIT (the value NIP-11 advertises as limitation.max_limit); an unset limit defaults to the same ceiling. The clamp bounds the request, not the response -- post-filtering for NIP-01 match, channel access, and reader visibility can still return fewer events than the ceiling."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs"
  - statement: "On the WS path, per-filter EventQuery construction runs channel-scope pushdown via apply_channel_scope_to_query against the reader's request-local accessible_channels set, computed from a 10s membership cache and repaired in-request against a stale cache-negative by confirming uncached membership against the database."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs"
  - statement: "Filter-level authorization gates run before any subscription is registered or any DB query issued, for global (non-channel-scoped) filters only: p_gated_filters_authorized requires a #p tag matching the caller for p-gated kinds, engram_filters_authorized requires authors=[self] or #p=[self] for KIND_AGENT_ENGRAM, and author_only_filters_authorized requires authors=[self] for author-only kinds (30300/30350). The same three functions are reused verbatim by the HTTP /query path in query_events_authed."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs"
      - "crates/buzz-relay/src/api/bridge.rs"
  - statement: "A REQ or /query request naming more explicit #h channel values than MAX_EXPLICIT_CHANNEL_VALUES in aggregate across its filters is rejected before any membership lookup runs, closing the WS subscription with 'restricted: too many explicit channels' or returning HTTP 400 on /query."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs"
      - "crates/buzz-relay/src/api/bridge.rs"
  - statement: "If a REQ's requested channel(s) are all unauthorized after per-channel membership resolution, the WS subscription is closed with 'restricted: not a channel member' and no subscription is registered; an OR filter spanning multiple channels instead silently omits only the inaccessible branches and keeps the accessible ones."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs"
  - statement: "Once filter-level gates pass, the WS handler registers the subscription (register_channels_scoped or register_scoped) and retains its pubsub topic(s) before executing the historical DB reads, so a live event published mid-query is not missed between the historical scan and the subscription becoming active."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs"
  - statement: "Per-filter DB reads on both the WS and HTTP paths run with bounded concurrency (FILTER_QUERY_CONCURRENCY, via futures_util::stream::StreamExt::buffered rather than buffer_unordered) so results are consumed in the same order the filters were declared, keeping NIP-01 dedupe order, conformance-trace order and first-error-wins semantics deterministic."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs"
      - "crates/buzz-relay/src/api/bridge.rs"
  - statement: "Each returned row passes three sequential per-event checks before delivery: filters_match against the current filter only (OR semantics across filters are the outer per-filter-query loop, not this check), channel accessibility if the row carries a channel_id, and event_visible_to_reader, which enforces author-only kinds, the persona shared-gate (kind:30175/30178 without an explicit shared tag) and per-event result-gated kinds (44200, 30622) even when reached through a kindless ids lookup that bypassed the filter-level #p gate."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs"
  - statement: "Events are deduplicated by event id only after a candidate event passes every per-event check, so an event that fails filter A's per-event checks remains independently eligible for filter B, preserving NIP-01 OR semantics across filters."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs"
  - statement: "A NIP-50 search filter (filter.search set) is dispatched to a separate one-shot path (handle_search_req on WS, handle_bridge_search on HTTP) that queries Postgres full-text search and is never registered for live fan-out; mixing a search filter with a non-search filter in the same request is rejected outright rather than partially served."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs"
      - "crates/buzz-relay/src/api/bridge.rs"
  - statement: "Historical delivery terminates on the WS path with an EOSE message sent after every filter's results have been streamed to the client; on the HTTP path it terminates by returning a single JSON array of matched events in the response body, with no EOSE concept."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs"
      - "crates/buzz-relay/src/api/bridge.rs"
  - statement: "On the WS path, a DB query error for any one filter aborts the remaining historical delivery immediately: the handler logs the error server-side, sends EOSE without processing later filters, and returns -- so a request can EOSE having delivered only a partial result set for the filters that had already succeeded, with no client-visible error distinguishing that from a normal empty tail."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs"
  - statement: "On the HTTP /query path, a DB query error for any one filter aborts the whole request atomically: query_events_authed returns an HTTP 500 with no partial JSON body, in contrast to the WS path's partial-then-EOSE behavior for the same underlying error."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs"
  - statement: "A WS subscription request is closed outright, with no partial registration, when the connection already holds MAX_SUBSCRIPTIONS active subscriptions and the incoming sub_id is not a replacement for an existing one."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs"
  - statement: "A channel-membership confirmation database error during request-local access repair on either path closes the WS subscription (or fails the HTTP request) with a generic 'database error' rather than falling back to a stale or default-permissive access decision."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs"
      - "crates/buzz-relay/src/api/bridge.rs"
  - statement: "The e2e test test_stored_events_returned_before_eose asserts that an event stored before a WS subscription is opened is delivered to that subscription before its EOSE arrives; it is marked #[ignore] because it requires a live relay rather than running in the default unit-test suite."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/e2e_relay.rs"
  - statement: "This node covers only the read-side historical-delivery flow (REQ historical phase and HTTP /query); it does not cover live fan-out of newly published events to an already-registered subscription, NIP-50 search internals, or the HTTP /count aggregate-count flow, each of which shares code with this flow but has its own trigger and termination and was out of scope to verify in depth here."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs"
      - "crates/buzz-relay/src/handlers/count.rs"
    confidence: 0.85
---

# Historical query

How the relay serves a client's request for already-stored events, as distinct
from live fan-out of newly published ones. Two entry points implement the same
core matching and authorization logic: the WebSocket `REQ` message and the HTTP
bridge's `POST /query`.

## Trigger

- **WebSocket**: the client sends a NIP-01 `REQ` message with one or more
  filters. `handle_req` is the entry point.
- **HTTP**: the client sends an authenticated `POST /query` with a JSON array
  of filters as the body. `query_events` is the entry point.

## Preconditions

| Path | Requirement |
|---|---|
| WebSocket | The connection already holds `AuthState::Authenticated`, established by a prior NIP-42 challenge/response (relay `AUTH` challenge -> client-signed kind:22242 -> `verify_nip42_event`). A scoped auth token, if present, must include `Scope::MessagesRead`. |
| HTTP | The request resolves to a known tenant from its `Host` header, and carries a NIP-98 event (kind:27235) in `Authorization: Nostr <base64>` verified against the exact method/URL/body, passes NIP-98 replay protection, admission, and relay-membership checks. |

Both entry points additionally require every filter to pass three shared
pre-DB authorization gates for global (non-channel-scoped) filters --
`p_gated_filters_authorized`, `engram_filters_authorized`, and
`author_only_filters_authorized` -- and an aggregate cap on how many distinct
`#h` channel values a single request may name.

## Ordered interactions

1. **Authenticate** the connection (WS: already done at connect time) or the
   request (HTTP: NIP-98 verification, replay check, admission, membership).
2. **Bound and validate** the filter set: aggregate `#h` value limit, then
   resolve the caller's accessible-channel set from a 10s membership cache,
   repairing any stale cache-negative for an explicitly requested channel by
   confirming membership against the database in-request
   (`resolve_request_local_access`).
3. **Authorize** each filter against the shared pre-DB gates (p-gated, engram,
   author-only kinds) for global filters, and reject the request/subscription
   if any requested channel has no authorized member left.
4. **Register** (WS only) the subscription and retain its pubsub topic(s)
   *before* running the historical scan, so a concurrently published event
   cannot land in the gap between the scan and the subscription becoming live.
5. **Build one `EventQuery` per filter** (`filter_to_query_params` /
   `build_event_query_from_filter`), pushing kinds, authors, ids, `#e`,
   single-value `#p`, single-value `#d` (NIP-33 kinds only), the resolved
   channel scope, `since`/`until`, and a limit clamped to
   `buzz_db::DEFAULT_MAX_PAGE_LIMIT` (the NIP-11 `max_limit` ceiling) into SQL.
6. **Execute** the per-filter queries with bounded concurrency
   (`FILTER_QUERY_CONCURRENCY`, order-preserving `buffered`), so filters with
   independent time windows or limits are never merged into one query.
7. **Filter and authorize each returned row**, in filter order: NIP-01
   `filters_match` against the current filter, channel accessibility, then
   `event_visible_to_reader` (author-only kinds, persona shared-gate,
   result-gated kinds such as 44200/30622).
8. **Deduplicate** by event id only after a row survives step 7, so a row
   rejected under one filter remains eligible under a later filter (OR
   semantics).
9. **Deliver**: WS sends each surviving event as it clears step 8, then sends
   `EOSE` once every filter's results have been processed. HTTP accumulates
   surviving events into one JSON array and returns it as the response body.

A NIP-50 search filter (`filter.search` set) is diverted at step 3 to a
separate one-shot code path (`handle_search_req` / `handle_bridge_search`)
that queries Postgres FTS instead of steps 5-8, and is never registered for
live fan-out. Mixing a search filter with a non-search filter in one request
is rejected outright.

## Trust-boundary crossings

- **WS connection -> relay**: NIP-42 crypto challenge/response. AUTH events
  are never stored or logged.
- **HTTP caller -> relay**: NIP-98 signed-event auth bound to the exact
  method, URL (including the tenant host) and body, plus replay protection
  and relay-membership enforcement -- a materially different trust mechanism
  from the WS path even though both converge on the same filter-authorization
  and per-event visibility code.
- **Reader -> channel-scoped content**: accessible-channel resolution, with a
  request-local repair path so a just-added member is never denied by a stale
  cache.
- **Reader -> globally stored gated kinds**: the three pre-DB filter gates
  (p-gated, engram, author-only) plus the per-event `event_visible_to_reader`
  result gate, which additionally covers kinds reachable via a kindless `ids`
  lookup that bypasses the filter-level `#p` gate.

## Termination / outcome

- **Success (WS)**: `EOSE` sent after all filters are processed; the
  subscription remains registered for live fan-out afterward (unless it was a
  search request, which is one-shot).
- **Success (HTTP)**: a `200` response with a JSON array of matched events.
- **Rejection before any query runs**: WS closes the subscription with a
  `CLOSED` message naming the reason (`auth-required:`, `restricted:`,
  `error: too many subscriptions`); HTTP returns `400`/`401`/`403`/`404` with
  a JSON error body. No subscription is registered and no query is executed
  in either case.

## Failure / abort behavior

- **WS, mid-scan DB error**: the first filter whose DB query errors aborts
  all remaining filters; the handler logs the error server-side and sends
  `EOSE` anyway, so the client can receive a silently partial result set
  (results only from filters that had already completed) with no
  client-visible signal distinguishing it from a normal empty tail.
- **HTTP, mid-scan DB error**: the whole request fails atomically with `500`
  and no partial JSON body -- the opposite failure shape from the WS path for
  the same class of underlying error, because HTTP has no equivalent of
  EOSE to terminate a partially delivered response.
- **Channel-membership confirmation DB error** (either path): fails closed
  with a generic `database error` rather than falling back to a stale or
  default-permissive access decision.
- **Aggregate `#h` limit exceeded**: rejected before any membership lookup or
  DB read, on both paths.
- **All requested channels unauthorized**: WS closes with
  `restricted: not a channel member` and registers no subscription; an OR
  filter spanning multiple channels instead silently drops only the
  inaccessible branches rather than failing the whole filter.
- There is no rollback to reason about: a historical query is read-only and
  never mutates stored state.

## Representative verification

- `crates/buzz-test-client/tests/e2e_relay.rs#test_stored_events_returned_before_eose`
  -- asserts a stored event is delivered before `EOSE` on a fresh WS
  subscription. Marked `#[ignore]`; requires a live relay rather than running
  in the default unit-test suite.
- `crates/buzz-relay/src/handlers/req.rs#tests::filter_query_pipeline_preserves_filter_order`
  -- pins the order-preserving concurrency invariant in step 6.
- `crates/buzz-relay/src/handlers/req.rs#tests::req_filter_limit_clamps_to_advertised_nip11_max_limit`
  -- pins the limit-clamp behavior in step 5.

## Scope and omissions

**Covers**: the historical-delivery phase of `REQ` and the HTTP `/query`
bridge endpoint -- trigger, authentication, per-filter authorization, query
construction, execution, per-event visibility filtering, and termination.

**Does not cover, and these are gaps rather than silence**:

- **Live fan-out** of a newly published event to an already-registered
  subscription. `handle_req` registers the subscription used for fan-out as
  part of this flow, but the fan-out mechanism itself (`event.rs`,
  `fan_out_pubsub_event`) is a separate, unverified-here flow with its own
  trigger and termination.
- **NIP-50 search internals** (`handle_search_req`, `handle_bridge_search`,
  the Postgres FTS query shape and page budget). This node documents only
  that search filters are diverted to that path, not how it works.
- **`COUNT` / `POST /count`** (`crates/buzz-relay/src/handlers/count.rs`).
  Shares the filter-authorization and access-resolution code with this flow
  but returns an aggregate number with different fast-path/fallback
  semantics, not a matter for this node.
- **No per-type corpus template exists yet** for a `flows` document (0 of the
  standards issues #1307-#1351 have merged as of the recorded revision); this
  node is written directly against `node.schema.json` per
  `launchpad/docs/corpus/AGENTS.md`'s "write it now, expect a later reshape"
  guidance, and may be restructured once a template lands.
- **`relationships` is empty.** No other `architecture`/flow node is merged
  on `origin/launchpad` at the recorded revision for this node to point at;
  see `launchpad/docs/corpus/AGENTS.md`'s warning against declaring an edge
  merely because it would resolve in a local worktree.
