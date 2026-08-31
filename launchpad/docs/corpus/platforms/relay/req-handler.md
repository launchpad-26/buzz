---
id: platforms-relay-req-handler
type: platforms
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 131b02f989684117d9ab1dd426f1673fa638e523."
    entry_class: FACT
    evidence:
      - "commit 131b02f989684117d9ab1dd426f1673fa638e523"
  - statement: "crates/buzz-relay/src/handlers/req.rs opens with the crate-level doc comment '//! REQ handler — subscribe, deliver historical events, then EOSE.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs:1"
  - statement: "handle_req is the only item in req.rs called from the WS message dispatcher: connection.rs's ClientMessage::Req branch acquires a permit from state.handler_semaphore via try_acquire_owned (rejecting with 'rate-limited: too many concurrent requests' if none is free), then spawns a tokio task instrumented with a 'ws.req' tracing span that awaits handlers::req::handle_req."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/connection.rs:596-617"
  - statement: "Of req.rs's other roughly two dozen top-level functions, none besides handle_req is invoked from connection.rs; fourteen are pub or pub(crate) and are called directly from crates/buzz-relay/src/api/bridge.rs (HTTP /query and /count) and crates/buzz-relay/src/handlers/count.rs (WS COUNT) via crate::handlers::req::* / super::req::* paths, making req.rs a shared toolkit module for query-building and authorization logic, not only the WS REQ entry point its module doc names."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs:1070"
      - "crates/buzz-relay/src/api/bridge.rs:1365"
      - "crates/buzz-relay/src/handlers/count.rs:9"
  - statement: "build_event_query_from_filter (pub async fn, req.rs:812) is the single shared constructor of a buzz_db::EventQuery from one NIP-01 Filter; it is called from handle_req's own historical pipeline, from count.rs's WS COUNT handler, and from bridge.rs's HTTP /query and /count handlers."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs:812"
      - "crates/buzz-relay/src/handlers/count.rs:170"
      - "crates/buzz-relay/src/handlers/count.rs:248"
      - "crates/buzz-relay/src/api/bridge.rs:1365"
      - "crates/buzz-relay/src/api/bridge.rs:1663"
      - "crates/buzz-relay/src/api/bridge.rs:1737"
  - statement: "filter_fully_pushable (pub fn, req.rs:852) decides whether a filter's authorization constraints can be pushed entirely into the SQL WHERE clause for a definitive DB-side count, versus requiring a fetch-and-post-filter fallback; it is called from count.rs's and bridge.rs's COUNT-fallback branches."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs:852"
      - "crates/buzz-relay/src/handlers/count.rs:194"
      - "crates/buzz-relay/src/handlers/count.rs:267"
      - "crates/buzz-relay/src/api/bridge.rs:1687"
      - "crates/buzz-relay/src/api/bridge.rs:1757"
  - statement: "The three sensitive-kind filter-authorization gates p_gated_filters_authorized, engram_filters_authorized, and author_only_filters_authorized (all pub(crate) in req.rs) are called identically from handle_req (WS REQ) and from bridge.rs's HTTP /query and /count authorization paths, so one gate implementation covers both transports."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs:1182"
      - "crates/buzz-relay/src/handlers/req.rs:1239"
      - "crates/buzz-relay/src/handlers/req.rs:1395"
      - "crates/buzz-relay/src/api/bridge.rs:1076"
      - "crates/buzz-relay/src/api/bridge.rs:1595"
  - statement: "event_visible_to_reader (pub(crate), req.rs:1368) is the single per-event result-level visibility gate reused by handle_req's historical-delivery loop, handle_search_req, and bridge.rs's HTTP query/search/count result hydration, enforcing author-only kinds, the persona shared-gate, and per-event result-gated kinds even when an event is reached through a kindless ids lookup."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs:1368"
      - "crates/buzz-relay/src/api/bridge.rs:1449"
      - "crates/buzz-relay/src/api/bridge.rs:1974"
  - statement: "resolve_request_local_access (pub(crate), req.rs:526) repairs a stale cache-negative for one requested channel id against the database in-request, so a just-added channel member is not denied by the 10-second membership cache's TTL; it is called from handle_req's own access-repair loop and from bridge.rs's HTTP equivalent."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs:501-526"
      - "crates/buzz-relay/src/handlers/req.rs:180-186"
      - "crates/buzz-relay/src/api/bridge.rs:1488"
  - statement: "Inside handle_req, dispatch runs in a fixed order before any DB read: authenticate and scope-check the connection; extract and cap requested #h channel ids; resolve the accessible-channel set (skipping the cache/DB lookup entirely for NIP-43-membership-only filter sets); narrow by any scoped-token channel restriction; repair stale cache-negatives in-request; reject if every requested channel ends up unauthorized; run the three sensitive-kind gates for global (non-channel-scoped) subscriptions only; then branch to the one-shot search path or continue toward registration."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs:56-270"
  - statement: "A NIP-50 search filter is dispatched to handle_search_req, a crate-private async fn (req.rs:584) reachable only from inside handle_req; it is not itself registered as a subscription and is not directly callable from connection.rs."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs:244-270"
      - "crates/buzz-relay/src/handlers/req.rs:584"
  - statement: "Once past the search branch, handle_req registers the subscription via SubscriptionRegistry::register_channels_scoped or register_scoped, both of which call register_with_scope, which first calls remove_subscription for the same (conn_id, sub_id) pair — implementing NIP-01's 'same sub_id replaces the prior subscription' rule — and returns the replaced entry, if any, as Option<RemovedSubscription>."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/subscription.rs:108-122"
      - "crates/buzz-relay/src/subscription.rs:124-140"
      - "crates/buzz-relay/src/subscription.rs:142-223"
  - statement: "handle_req uses that returned RemovedSubscription to release the old subscription's pubsub topic(s) via release_subscription_topics before retaining the new topic(s), so re-issuing a REQ with the same sub_id does not leak a stale topic retain from the replaced subscription."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs:277-309"
      - "crates/buzz-relay/src/handlers/req.rs:1136"
  - statement: "The historical-delivery portion of handle_req executes in three explicitly commented phases over the per-request filter set: pure per-filter EventQuery construction ('Phase 1'), bounded-concurrency DB reads via futures_util::stream::StreamExt::buffered ('Phase 2'), and strictly filter-ordered post-processing/dedup/delivery ('Phase 3'), terminating in a single EOSE."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs:313-480"
  - statement: "req.rs's own imports (buzz_core, buzz_db, buzz_pubsub, buzz_auth, nostr, hex) and its use of futures_util, tracing and metrics macros are all declared as workspace dependencies in buzz-relay's own Cargo.toml."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs:1-24"
      - "crates/buzz-relay/Cargo.toml"
  - statement: "req.rs also depends on sibling in-crate modules crate::connection (AuthState, ConnectionState), crate::protocol (RelayMessage), crate::state (AppState), and crate::conformance (state_for_request, record_req_authcheck, record_read_message_rows); all four are modules of buzz-relay itself, not separate crates."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs:21-23"
      - "crates/buzz-relay/src/handlers/req.rs:133-135"
  - statement: "req.rs carries its own #[cfg(test)] mod tests with named tests pinning this module's own behavior, including global_queries_push_access_scope_before_limit, the async filter_query_pipeline_preserves_filter_order (pinning Phase 2's order-preserving buffered concurrency), and req_filter_limit_clamps_to_advertised_nip11_max_limit (pinning the NIP-11 max_limit clamp)."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs:1417-1421"
      - "crates/buzz-relay/src/handlers/req.rs:1455"
      - "crates/buzz-relay/src/handlers/req.rs:1576"
  - statement: "Because architecture-flows-historical-query and architecture-flows-search-query already document the end-to-end trigger/auth/delivery/termination behavior of handle_req and handle_search_req in detail, citing req.rs directly for nearly every step of both flows, restating that content here would duplicate an existing corpus node; scoping this node to req.rs's own internal dispatch order and its role as a shared toolkit for count.rs and bridge.rs keeps it an independently maintainable idea distinct from either flow node."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/architecture/flows/historical-query.md"
      - "launchpad/docs/corpus/architecture/flows/search-query.md"
      - "launchpad/docs/corpus/AGENTS.md"
    confidence: 0.85
  - statement: "Sibling platforms/** batch tasks under parent Feature #614 have converged on front matter type: platforms, borrowing templates/component.md's section shape (Responsibility / Public interface / Dependencies / Boundary / Relationships / Scope and omissions), because no platforms-specific template has merged yet."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "#614 batch dispatch brief (known finding #4)"
relationships:
  - type: references
    target: architecture-flows-historical-query
  - type: references
    target: architecture-flows-search-query
---

# Platform component: relay REQ handler (`req.rs`)

What `crates/buzz-relay/src/handlers/req.rs` is as a piece of the relay
platform: its own module-level responsibility, its public surface (both the
WS entry point and the shared toolkit functions other modules call directly),
its dependencies, and the internal dispatch mechanics inside it that the
existing end-to-end flow documents do not detail.

**Authoritative sources this node does not restate:** the end-to-end
historical-query request/response flow (WS `REQ` and HTTP `POST /query`,
trigger through termination) is `architecture-flows-historical-query`'s
subject; the end-to-end NIP-50 search flow is
`architecture-flows-search-query`'s. Both already cite `req.rs` directly for
almost every step of those flows. This node does not repeat that content —
see *Boundary* below for the explicit line.

## Responsibility

Per its own module doc comment, `req.rs`'s stated responsibility is narrow:
"REQ handler — subscribe, deliver historical events, then EOSE." In practice
the module carries two responsibilities that its doc comment does not fully
name:

1. **The WS `REQ` entry point** (`handle_req`) — the only function in this
   module the WebSocket message dispatcher (`connection.rs`) calls directly.
2. **A shared toolkit** of query-construction and filter-authorization
   functions that `crates/buzz-relay/src/handlers/count.rs` (WS `COUNT`) and
   `crates/buzz-relay/src/api/bridge.rs` (HTTP `/query` and `/count`) import
   and call directly, rather than reimplementing. Fourteen of `req.rs`'s
   functions are `pub` or `pub(crate)` for exactly this reason.

## Public interface

| Item | Kind | Contract | Evidence |
|---|---|---|---|
| `handle_req` | `pub async fn` | WS `REQ` entry point: authenticate, resolve access, authorize, dispatch to search or historical delivery, terminate in `EOSE`. Sole caller: `connection.rs`'s WS dispatcher. | `crates/buzz-relay/src/handlers/req.rs:51`, `crates/buzz-relay/src/connection.rs:612` |
| `build_event_query_from_filter` | `pub async fn` | Builds one `buzz_db::EventQuery` from one `nostr::Filter`. Shared by WS `REQ`/`COUNT` and HTTP `/query`/`/count`. | `crates/buzz-relay/src/handlers/req.rs:812` |
| `filter_fully_pushable` | `pub fn` | Decides whether a filter's constraints are fully expressible in SQL (definitive DB-side count) or need a fetch-and-post-filter fallback. | `crates/buzz-relay/src/handlers/req.rs:852` |
| `resolve_request_local_access` | `pub(crate) fn` | Repairs one stale cache-negative channel-membership entry against the DB, in-request. | `crates/buzz-relay/src/handlers/req.rs:526` |
| `build_search_channel_scope_filter` | `pub(crate) fn` | Builds the channel-scope constraint a NIP-50 search query applies. | `crates/buzz-relay/src/handlers/req.rs:561` |
| `apply_count_fallback_limit` / `count_fallback_exceeded` | `pub(crate) fn` | Bound and detect overflow of the COUNT fetch-and-filter fallback path. | `crates/buzz-relay/src/handlers/req.rs:831`, `crates/buzz-relay/src/handlers/req.rs:838` |
| `apply_channel_scope_to_query` | `pub(crate) fn` | Pushes the caller's resolved accessible-channel scope into an `EventQuery`'s SQL predicate. | `crates/buzz-relay/src/handlers/req.rs:1069` |
| `extract_channel_ids_from_filters_limited` / `extract_channel_ids_from_filters` | `pub(crate) fn` | Pull requested `#h` channel ids out of a filter set; the `_limited` variant enforces `MAX_EXPLICIT_CHANNEL_VALUES`. | `crates/buzz-relay/src/handlers/req.rs:1099`, `crates/buzz-relay/src/handlers/req.rs:1120` |
| `p_gated_filters_authorized`, `engram_filters_authorized`, `author_only_filters_authorized` | `pub(crate) fn` | The three sensitive-kind filter-level authorization gates (see *Dependencies* below for their kind-constant sources). | `crates/buzz-relay/src/handlers/req.rs:1182`, `crates/buzz-relay/src/handlers/req.rs:1239`, `crates/buzz-relay/src/handlers/req.rs:1395` |
| `filter_can_match_author_only_kinds`, `filter_can_match_shared_gated_kinds`, `filter_can_match_result_gated_kinds`, `result_gated_count_safe_for_pushdown` | `pub(crate) fn` | Per-kind-class predicates a filter must satisfy for pushdown/authorization decisions. | `crates/buzz-relay/src/handlers/req.rs:1277-1341` |
| `is_author_only_event`, `event_visible_to_reader` | `pub(crate) fn` | Per-event result-level visibility gates, applied after a row is fetched. | `crates/buzz-relay/src/handlers/req.rs:1342`, `crates/buzz-relay/src/handlers/req.rs:1368` |
| `FILTER_QUERY_CONCURRENCY`, `MAX_EXPLICIT_CHANNEL_VALUES` | `pub(crate) const` | Bound Phase 2's DB-read concurrency and the aggregate explicit-channel-value cap, respectively. | `crates/buzz-relay/src/handlers/req.rs:34`, `crates/buzz-relay/src/handlers/req.rs:42` |

Not part of the module's outward interface: `handle_search_req`,
`filters_are_nip43_membership_only`, `extract_channel_id_from_filter(s)`,
`filter_to_query_params`, and `release_subscription_topics` carry no `pub` or
`pub(crate)` marker and are reachable only from within `req.rs` itself.

## Handler-level dispatch mechanics

This is the ground `architecture-flows-historical-query` and
`architecture-flows-search-query` do not detail: not *what* the request/
response flow accomplishes, but *how the module itself is wired* to make
that flow happen — its position in the WS dispatcher, its internal control
flow before any DB read, its subscription-replace bookkeeping, and its
staged read pipeline.

**WS dispatch entry.** `connection.rs`'s `ClientMessage::Req` branch acquires
a permit from `state.handler_semaphore` (`try_acquire_owned`); on
exhaustion, it rejects the request with `"rate-limited: too many concurrent
requests"` without ever reaching `handle_req`. On success it spawns a
`tokio::spawn`'d task, instrumented with a `"ws.req"` tracing span carrying
`conn_id` and `sub_id`, that awaits `handle_req` and then drops the permit.
`ClientMessage::Count` follows the identical acquire/spawn/instrument shape
one branch below it, dispatching to `count::handle_count` instead — the two
handlers share this outer wrapper but not a function.

**Internal dispatch order inside `handle_req`.** Before any database read,
the function runs a fixed sequence of gates, each an early-return on
failure:

1. Authenticate the connection and check scoped-token read permission.
2. Extract requested `#h` channel ids, capped at `MAX_EXPLICIT_CHANNEL_VALUES`.
3. Resolve the accessible-channel set — skipped entirely (no cache or DB
   lookup) when every filter is NIP-43-membership-only.
4. Narrow the accessible set by any scoped-token channel restriction.
5. Repair stale cache-negatives for explicitly requested channels,
   in-request, via `resolve_request_local_access`.
6. Reject if every requested channel ended up unauthorized.
7. Run the three sensitive-kind gates (`p_gated_filters_authorized`,
   `engram_filters_authorized`, `author_only_filters_authorized`) —
   **only** for global (non-channel-scoped) subscriptions.
8. Branch: a search filter diverts to `handle_search_req` and returns; a
   non-search filter set continues to subscription registration.

**Search branch.** `handle_search_req` is not itself a WS entry point — it
has no caller outside `handle_req` and is not present in `connection.rs`'s
dispatch table at all. Reaching it always means a `REQ` was received first
and its filters were found to contain a `search` field during step 8 above.

**Subscription registration and resubscribe.** Past the search branch,
`handle_req` calls `SubscriptionRegistry::register_channels_scoped` (channel-
scoped filters) or `register_scoped` (global filters). Both route through
`register_with_scope`, which calls `remove_subscription` for the same
`(conn_id, sub_id)` pair *before* inserting the new entry — implementing
NIP-01's "a `REQ` with an existing `sub_id` replaces the previous
subscription" rule — and returns the replaced entry as
`Option<RemovedSubscription>`. `handle_req` uses that return value to call
`release_subscription_topics` on the *old* scope before retaining the *new*
scope's pubsub topic(s), so a client re-issuing the same `sub_id` (e.g. to
change its filters) does not leak a topic retain from the subscription it
just replaced.

**Historical-delivery pipeline.** Once registered, `handle_req` runs its own
three explicitly phase-commented stages over the filter set: Phase 1 builds
one `EventQuery` per filter (pure, no I/O); Phase 2 issues those queries with
bounded concurrency (`FILTER_QUERY_CONCURRENCY`) via
`futures_util::stream::StreamExt::buffered`, which preserves input order;
Phase 3 consumes the results strictly in that same filter order, running
per-event visibility checks and dedup, before the function sends a single
terminal `EOSE`. The `buffered` (not `buffer_unordered`) choice is what lets
Phase 2 overlap DB round trips while Phase 3 still observes filters in their
original order.

## Dependencies

**Depends on** (this module requires these to build/run):

| Dependency | Why | Evidence |
|---|---|---|
| `buzz-core` (`filter::filters_match`, `kind::*` constants, `tenant::TenantContext`) | NIP-01 filter matching and the gated-kind constant set the sensitive-kind gates check against | `crates/buzz-relay/src/handlers/req.rs:8-13`, `crates/buzz-relay/Cargo.toml` |
| `buzz-db` (`EventQuery`) | The query type every historical/count read builds and executes | `crates/buzz-relay/src/handlers/req.rs:14`, `crates/buzz-relay/Cargo.toml` |
| `buzz-pubsub` (`EventTopic`) | Topic retain/release for the subscription this handler registers | `crates/buzz-relay/src/handlers/req.rs:15`, `crates/buzz-relay/Cargo.toml` |
| `buzz-auth` (`Scope`) | Scoped-token permission checks (`Scope::MessagesRead`) | `crates/buzz-relay/src/handlers/req.rs:19`, `crates/buzz-relay/Cargo.toml` |
| `nostr` (`Filter`) | The NIP-01 filter type this module parses and authorizes | `crates/buzz-relay/src/handlers/req.rs:17`, `crates/buzz-relay/Cargo.toml` |
| `hex`, `futures-util`, `tracing`, `metrics`, `tokio`, `uuid` | Pubkey hex-encoding, the bounded-concurrency stream combinator, structured logging/spans, counters/gauges, async runtime, channel-id typing | `crates/buzz-relay/src/handlers/req.rs:1-6`, `crates/buzz-relay/src/handlers/req.rs:365`, `crates/buzz-relay/Cargo.toml` |
| `crate::connection` (`AuthState`, `ConnectionState`), `crate::protocol` (`RelayMessage`), `crate::state` (`AppState`), `crate::conformance` | In-crate sibling modules for connection auth state, the WS message envelope, shared app state, and conformance-trace emission | `crates/buzz-relay/src/handlers/req.rs:21-23`, `crates/buzz-relay/src/handlers/req.rs:133-135` |

**Depended on by** (in-crate; all three are modules of `buzz-relay` itself,
not separate crates, so no cross-crate manifest entry exists to cite):

| Dependent | Why | Evidence |
|---|---|---|
| `crate::connection` | Dispatches every WS `REQ` message to `handle_req` | `crates/buzz-relay/src/connection.rs:612` |
| `crate::handlers::count` | Reuses `build_event_query_from_filter`, `filter_fully_pushable`, `apply_count_fallback_limit`, `count_fallback_exceeded` for WS `COUNT` | `crates/buzz-relay/src/handlers/count.rs:9`, `crates/buzz-relay/src/handlers/count.rs:170`, `crates/buzz-relay/src/handlers/count.rs:194` |
| `crate::api::bridge` | Reuses the same query-building, channel-scope, sensitive-kind-gate, and event-visibility functions for HTTP `/query` and `/count` | `crates/buzz-relay/src/api/bridge.rs:1070`, `crates/buzz-relay/src/api/bridge.rs:1365`, `crates/buzz-relay/src/api/bridge.rs:1687` |

## Boundary

This node does not describe:

- **The end-to-end historical-query request/response flow** (trigger,
  authentication, preconditions, termination, failure modes across both WS
  and HTTP) — see `architecture-flows-historical-query`.
- **The end-to-end NIP-50 search-query flow** — see
  `architecture-flows-search-query`.
- **The `COUNT` / `/count` flow's own trigger, termination, and fallback
  semantics** (`crates/buzz-relay/src/handlers/count.rs`). This node names
  `count.rs` only as a *consumer* of `req.rs`'s shared toolkit functions, not
  as a flow documented in its own right — no corpus node covers it yet.
- **The HTTP bridge's own NIP-98 authentication and tenant-binding
  mechanics** (`crates/buzz-relay/src/api/bridge.rs`) beyond naming it as a
  consumer of `req.rs`'s shared functions — those are already covered where
  the two flow nodes discuss the HTTP path.
- **`SubscriptionRegistry`'s full internal indexing structure** (the
  per-kind/per-channel/global index maps) beyond the one behavior this node
  depends on — replace-on-resub via `register_with_scope`. The registry's
  own responsibility, interface, and fan-out consumers are a separate
  component, not documented here.

## Relationships

- `references`: `architecture-flows-historical-query` — this node does not
  restate that node's end-to-end WS/HTTP historical-delivery flow content.
- `references`: `architecture-flows-search-query` — this node does not
  restate that node's end-to-end NIP-50 search flow content.

Both targets were confirmed present on `origin/launchpad`
(`git ls-tree -r --name-only origin/launchpad --
launchpad/docs/corpus/architecture/flows/`) before being declared, per
`AGENTS.md`'s rule to check the merge target, not the local worktree.

## Scope and omissions

**This node covers** `crates/buzz-relay/src/handlers/req.rs` as a platform
component: its dual responsibility (WS entry point plus shared toolkit), its
full public interface (`pub` and `pub(crate)` items) and which other modules
call each one, its dependencies in both directions, and — the content the
existing flow nodes do not carry — its internal dispatch order, the WS
dispatcher's wrapping semaphore/span mechanics, subscription
replace-on-resub bookkeeping, and its three-phase historical-read pipeline
structure.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| End-to-end historical-query flow (trigger through termination, both transports) | `architecture-flows-historical-query` |
| End-to-end NIP-50 search-query flow | `architecture-flows-search-query` |
| The `COUNT`/`/count` flow's own trigger/termination/fallback semantics | `crates/buzz-relay/src/handlers/count.rs`; no corpus node yet |
| The HTTP bridge's NIP-98 auth and tenant-binding mechanics | Covered incidentally by the two flow nodes; no dedicated component node yet |
| `SubscriptionRegistry`'s full indexing structure and fan-out consumers | `crates/buzz-relay/src/subscription.rs`; no corpus node yet |
| No `platforms`-specific corpus template has merged as of the recorded revision | This node is written directly against `node.schema.json` plus `templates/component.md`'s borrowed shape, per `AGENTS.md`'s "write it now, expect a later reshape" guidance |

**Expected but not verified when this node was written:**

- Whether every `pub(crate)` function listed in *Public interface* is called
  from exactly the call sites enumerated here, versus additional call sites
  elsewhere in `buzz-relay` not surfaced by the greps run for this node, was
  not exhaustively re-checked function-by-function beyond the representative
  citations given.
- No live relay was run against this node's claims; every claim is sourced
  from reading `req.rs`, `connection.rs`, `subscription.rs`, `count.rs`,
  `bridge.rs`, and `Cargo.toml` at the recorded revision, not from executing
  `just test` / `just ci` as part of authoring this document.
