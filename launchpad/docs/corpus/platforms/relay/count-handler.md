---
id: platforms-relay-count-handler
type: platforms
status: draft
origin: launchpad
audiences:
  - agent
  - developer
evidence:
  - statement: "This node was authored and checked against repository revision 131b02f989684117d9ab1dd426f1673fa638e523."
    entry_class: FACT
    evidence:
      - "commit 131b02f989684117d9ab1dd426f1673fa638e523"
  - statement: "node.schema.json's type enum has no member named for a specific platform surface (e.g. 'relay'); prior batch nodes under platforms/** use type: platforms as a borrowed convention, and this node follows the same convention rather than inventing a new enum value."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
    confidence: 0.75
  - statement: "The relay implements NIP-45 COUNT over two entry points: a WebSocket 'COUNT' client message, parsed by ClientMessage::from_json and dispatched to handlers::count::handle_count from the message-routing match in connection.rs, and an HTTP bridge POST /count endpoint, handled by count_events / count_events_authed in api/bridge.rs."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/protocol.rs:108-145"
      - "crates/buzz-relay/src/connection.rs:618-638"
      - "crates/buzz-relay/src/api/bridge.rs:1503-1562"
      - "crates/buzz-relay/src/api/bridge.rs:1567-1626"
  - statement: "The WS COUNT response is the JSON array [\"COUNT\", sub_id, {\"count\": N}], formatted by RelayMessage::count; the HTTP /count response is a JSON object {\"count\": N} in the response body, formatted inside count_events_authed and returned by count_events."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/protocol.rs:213-216"
      - "crates/buzz-relay/src/api/bridge.rs:1503-1562"
  - statement: "Before executing any filter, both COUNT entry points require the caller to be authenticated (WS: AuthState::Authenticated; HTTP: NIP-98-verified pubkey via verify_bridge_auth) and reuse the same three shared pre-DB filter-authorization gates as the REQ/query historical-delivery flow -- p_gated_filters_authorized, engram_filters_authorized, and author_only_filters_authorized -- plus the same aggregate cap on explicit #h channel values per request (extract_channel_ids_from_filters_limited), rejecting the whole request/subscription before any DB query runs if any gate fails."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/count.rs:24-81"
      - "crates/buzz-relay/src/api/bridge.rs:1588-1612"
      - "crates/buzz-relay/src/handlers/req.rs:1182-1416"
  - statement: "This shared authentication and filter-authorization machinery -- NIP-42 WS auth, NIP-98 HTTP auth, the p-gated/engram/author-only filter gates, and channel-membership cache/repair via resolve_request_local_access -- is documented in detail by the corpus's architecture-flows-historical-query node, which explicitly scopes COUNT out of its own coverage; this node references that node instead of re-deriving those shared mechanics."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/flows/historical-query.md:272-275"
  - statement: "For each filter, COUNT decides between two execution paths: a fast exact-count SQL path (Db::count_events_routed, an aggregate SQL COUNT query with no row materialization) when filter_fully_pushable(filter) holds and none of three per-COUNT existence-leak guards force the fallback; otherwise a bounded post-filter fallback (Db::query_events_routed_bounded plus in-process filters_match / event_visible_to_reader checks) is used."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/count.rs:104-240"
      - "crates/buzz-relay/src/api/bridge.rs:1628-1733"
      - "crates/buzz-relay/src/handlers/req.rs:842-897"
  - statement: "filter_fully_pushable returns false (forcing the fallback) for a filter with a multi-value #p tag, a #d tag on a non-NIP-33-only kind set, any other generic tag with values (#t, #a, etc.), or a NIP-50 search field, because filter_to_query_params cannot represent those constraints in SQL without risking an overcount."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs:852-897"
  - statement: "Independently of filter_fully_pushable, COUNT forces the bounded post-filter fallback whenever a filter can match an author-only kind (AUTHOR_ONLY_KINDS: 30300 KIND_EVENT_REMINDER, 30350 KIND_PUSH_LEASE, 30179 KIND_PRIVATE_MANAGED_AGENT per kind.rs) unless the filter's authors are exactly the caller's own pubkey, or can match a shared-gated kind (SHARED_GATED_KINDS: 30175 KIND_PERSONA, 30178 KIND_TEAM_CATALOG), or can match a result-gated kind (RESULT_GATED_KINDS: 30622 KIND_DM_VISIBILITY, 44200 KIND_AGENT_TURN_METRIC) unless the filter's #p tag is pinned exactly to the caller's own pubkey (result_gated_count_safe_for_pushdown) -- because the fast SQL count has no per-event visibility check and would otherwise leak the existence of another user's private/gated events as a non-zero count even though no event content is ever returned."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/count.rs:104-123"
      - "crates/buzz-relay/src/handlers/req.rs:1271-1337"
      - "crates/buzz-core/src/kind.rs:94-215"
  - statement: "The bounded fallback path fetches at most COUNT_FALLBACK_CANDIDATE_LIMIT + 1 (5,001) candidate rows via apply_count_fallback_limit; if count_fallback_exceeded (more than 5,000 candidates returned) the request is rejected outright with 'restricted: count filter requires narrower constraints' (WS) or HTTP 400 (bridge), and a buzz_count_fallback_rejections_total metric counter is incremented, rather than silently returning a truncated count."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs:822-840"
      - "crates/buzz-relay/src/handlers/count.rs:206-223"
      - "crates/buzz-relay/src/api/bridge.rs:1699-1714"
  - statement: "Db::count_events_routed and Db::query_events_routed_bounded both restrict replica routing to the Bounded predicate arm only, never the Covered arm used by ordinary paginated reads, because the covered arm only bounds insert-completeness and can briefly under-reflect a soft-delete (an UPDATE outside the floor guard); a page absorbs that per-row, but a COUNT has no downstream re-filter to absorb an inflated aggregate number, so COUNT never takes the covered-eligible replica arm even when a filter shape would otherwise qualify for it."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/event.rs:1426-1496"
  - statement: "An ignored integration test (count_events_routed_is_bounded_only, requires Postgres) constructs a filter shape that is covered-arm-eligible (pinned ids + until) on purpose and asserts count_events_routed still reads the writer pool rather than taking the covered replica arm, distinguishing it by row-count divergence between a writer with 2 rows and a replica with 1 row."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/runtime/tests.rs:1245-1252"
  - statement: "The WS COUNT handler additionally narrows the caller's accessible_channels set to the connection's scoped auth token's channel_ids (token_channel_ids), when the token carries one, before executing any filter -- its own comment states this prevents a scoped token from counting events in channels outside its scope via the no-channel-filter SQL pushdown. The HTTP bridge's count_events_authed computes accessible_channels via the same get_accessible_channel_ids_cached call and repairs per-filter access the same way, but performs no equivalent token-scope narrowing step anywhere in its body."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/count.rs:83-102"
      - "crates/buzz-relay/src/api/bridge.rs:1614-1626"
  - statement: "Whether the HTTP bridge path's absence of token-scope channel narrowing is deliberate (because NIP-98 bridge authentication does not carry the same scoped-auth-token concept a WS connection can) or an unverified gap was not established by reading count.rs and bridge.rs alone, and is left as an open question rather than asserted either way."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay/src/handlers/count.rs:83-102"
      - "crates/buzz-relay/src/api/bridge.rs:1614-1626"
    confidence: 0.4
  - statement: "The relay's static SUPPORTED_NIPS list served in NIP-11 relay information does not include 45 (NIP-45, COUNT), even though COUNT is implemented and reachable on both the WS and HTTP surfaces at the recorded revision."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/nip11.rs:15"
  - statement: "The HTTP router registers POST /count against api::bridge::count_events directly (.route(\"/count\", post(api::bridge::count_events)))."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs:74"
  - statement: "Issue #1268's Definition of Done requires that this node explain only component-level behavior, not the entire containing platform, and that it name dependencies/collaborators and link source implementation and tests."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1268 definition of done"
relationships:
  - type: references
    target: architecture-flows-historical-query
---

# Relay COUNT handler

How the relay answers a NIP-45 `COUNT` request -- an aggregate event count
rather than the matching events themselves -- across its two entry points:
the WebSocket `COUNT` client message and the HTTP bridge's `POST /count`.
This node answers what a caller can rely on when it asks the relay "how many
events match this filter" rather than "give me the events": what
authorization runs first, when the answer is an exact fast SQL count versus a
bounded post-filtered one, why several kinds are excluded from the fast path
on purpose, and which replica-routing rule applies only to counts.

## Responsibility

`crates/buzz-relay/src/handlers/count.rs` states its own responsibility in
its module doc comment: *"NIP-45 COUNT handler -- aggregate queries with
channel access enforcement."* Its `handle_count` function is documented as
handling one WS `COUNT` message end to end: *"require auth, enforce channel
access, execute filters, and return the aggregate count."* The HTTP bridge's
`count_events` carries the equivalent responsibility for `POST /count`,
documented in its own doc comment as *"Count events via HTTP bridge (NIP-98
auth)... Enforces channel access: only counts events in channels the user can
access. For filters without a `#h` tag, falls back to per-event counting with
access checks."*

## Public interface

| Item | Kind | Contract | Evidence |
|---|---|---|---|
| `handlers::count::handle_count` | async fn | WS entry point: takes a `sub_id` and parsed `Filter` list, authenticates the connection, authorizes and executes each filter, and sends exactly one `RelayMessage::count` (or a `RelayMessage::closed` on any rejection) back to the connection. | `crates/buzz-relay/src/handlers/count.rs:18-23` |
| `ClientMessage::Count` (parsed by `ClientMessage::from_json`, case `"COUNT"`) | enum variant / wire format | `["COUNT", <sub_id>, <filter>, ...]`; requires a non-empty `sub_id` no longer than `MAX_SUB_ID_LENGTH` and no more than `MAX_FILTERS_PER_REQ` filters, mirroring `REQ`'s own limits. | `crates/buzz-relay/src/protocol.rs:108-145` |
| `RelayMessage::count` | fn | Formats the WS response `["COUNT", sub_id, {"count": N}]`. | `crates/buzz-relay/src/protocol.rs:213-216` |
| `api::bridge::count_events` | async axum handler | HTTP entry point for `POST /count`; binds the request to a tenant by `Host` header, verifies NIP-98 auth, and returns `Json({"count": N})` or a JSON error body with the matching HTTP status. | `crates/buzz-relay/src/api/bridge.rs:1503-1562` |
| `api::bridge::count_events_authed` | async fn (private) | Filter-execution body for `count_events`, run once NIP-98 auth succeeds: admission, replay protection, relay-membership, filter authorization gates, channel access resolution, and the fast/fallback count loop per filter. | `crates/buzz-relay/src/api/bridge.rs:1567-1808` |
| `handlers::req::filter_fully_pushable` | fn (`pub(crate)`, shared with REQ) | Returns whether a filter's constraints are fully representable in SQL by `filter_to_query_params`, so the fast exact-count path can be used without post-filtering. | `crates/buzz-relay/src/handlers/req.rs:852-897` |
| `handlers::req::{filter_can_match_author_only_kinds, filter_can_match_shared_gated_kinds, filter_can_match_result_gated_kinds, result_gated_count_safe_for_pushdown}` | fns (`pub(crate)`) | The three additional per-COUNT existence-leak guards described under *Fast path vs. fallback* below. | `crates/buzz-relay/src/handlers/req.rs:1271-1337` |
| `buzz_db::Db::count_events_routed` | async fn | Fast exact-count SQL path; routes reads to the Bounded predicate arm only, falling back to the writer pool on a replica error. | `crates/buzz-db/src/store/event.rs:1468-1496` |
| `buzz_db::Db::query_events_routed_bounded` | async fn | Bounded candidate-row fetch used by the post-filter fallback path; same Bounded-only routing rule as `count_events_routed`. | `crates/buzz-db/src/store/event.rs:1427-1457` |

## Dependencies

**Depends on** (this component requires these to build/run):

| Component | Why | Evidence |
|---|---|---|
| `buzz-core` (filter matching, kind constants) | `filters_match`, `AUTHOR_ONLY_KINDS`/`SHARED_GATED_KINDS`/`RESULT_GATED_KINDS`/`P_GATED_KINDS`/`KIND_AGENT_ENGRAM` constants used by the shared gates and the per-COUNT existence-leak guards. | `crates/buzz-relay/Cargo.toml`; `crates/buzz-core/src/kind.rs:129-215` |
| `buzz-db` (event store) | `count_events_routed`, `query_events_routed_bounded`, `is_member` -- the only way either COUNT path reads storage. | `crates/buzz-relay/Cargo.toml`; `crates/buzz-db/src/store/event.rs:1427-1496` |
| `crates/buzz-relay/src/handlers/req.rs` (same crate, not a separate dependency edge, but the count handler's own logic is inseparable from it) | Both COUNT entry points call straight into `req.rs`'s shared filter-authorization gates, channel-access helpers, and pushability/gating predicates rather than duplicating them. | `crates/buzz-relay/src/handlers/count.rs:8-12`; `crates/buzz-relay/src/api/bridge.rs:1588-1651` |
| `nostr` (Filter, SingleLetterTag, PublicKey types) | Filter parsing and tag inspection throughout both handlers. | `crates/buzz-relay/src/handlers/count.rs:5` |

**Depended on by** (these require this component):

| Component | Why | Evidence |
|---|---|---|
| `crates/buzz-relay/src/connection.rs` (WS message router) | Dispatches every parsed `ClientMessage::Count` to `handlers::count::handle_count` under the connection's handler-concurrency semaphore. | `crates/buzz-relay/src/connection.rs:618-638` |
| `crates/buzz-relay/src/router.rs` | Registers `POST /count` against `api::bridge::count_events`. | `crates/buzz-relay/src/router.rs:74` |

## Boundary

This node does not describe:
- The shared REQ/query historical-delivery mechanics that COUNT reuses
  verbatim -- WS NIP-42 auth, HTTP NIP-98 auth, the `p_gated_filters_authorized`
  / `engram_filters_authorized` / `author_only_filters_authorized` gates, and
  channel-membership cache/repair via `resolve_request_local_access`. See
  `architecture-flows-historical-query` (referenced below), which documents
  these in depth and explicitly excludes COUNT from its own scope.
- How live fan-out or NIP-50 search work -- neither is invoked by COUNT.
- Install/usage instructions for a human running the relay -- see the
  relay's own README/CONTRIBUTING docs, not this node.
- The underlying replica-routing predicate machinery (`RoutePredicate::Bounded`
  vs. `Covered`) beyond the one rule COUNT depends on (Bounded-only, never
  Covered); the general routing mechanism is `buzz-db`'s own concern.
- Why NIP-45 is absent from `SUPPORTED_NIPS` despite being implemented, and
  why the HTTP bridge path omits the WS path's token-scope channel narrowing
  -- both are named as observed facts under *Scope and omissions* below, not
  resolved here.

## Relationships

- references: `architecture-flows-historical-query` -- COUNT shares that
  flow's authentication and filter-authorization machinery; that node names
  COUNT explicitly as sharing code but out of its own scope, and this node
  is the other side of that boundary.

## Scope and omissions

**This node covers**: the WS `COUNT` message and HTTP `POST /count` entry
points; the fast exact-count SQL path and when it applies
(`filter_fully_pushable`); the three additional per-COUNT guards that force
the bounded post-filter fallback to prevent existence leaks for author-only,
shared-gated and result-gated kinds; the fallback's bounded candidate budget
and hard-rejection behavior past that budget; the Bounded-only replica
routing rule unique to counts; the WS-only scoped-token channel narrowing;
and the NIP-45-not-advertised discrepancy in `SUPPORTED_NIPS`.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Shared REQ/query auth and filter-authorization mechanics COUNT reuses | `architecture-flows-historical-query` |
| Live fan-out of newly published events | Not yet covered by any merged node at the recorded revision |
| NIP-50 search internals | `search-query.md` (`architecture-flows-search-query`, not independently re-verified for this node) |
| The general replica-routing predicate mechanism (`RoutePredicate`) in `buzz-db` | Not yet covered by any merged node at the recorded revision |
| No per-type corpus template exists yet for a `platforms` document | `templates/component.md`'s section shape is borrowed per prior batch convention; a later reshape may follow once a platforms-specific template lands |

**Expected but not verified when this node was written:**

- **Whether the HTTP bridge path's missing token-scope channel narrowing is
  deliberate or a latent gap.** `count.rs`'s own comment explains why the WS
  path needs the narrowing; `bridge.rs` has no equivalent comment or step.
  Concluding "deliberate because NIP-98 has no scoped-token concept" would
  require reading `buzz-auth`'s token model in full, which was out of scope
  for a count-handler-focused node; recorded here as an open question, not
  resolved as fact in either direction.
- **Why NIP-45 (45) is absent from `SUPPORTED_NIPS`** despite COUNT being
  implemented and reachable on both surfaces. Not explained by any comment
  found in `nip11.rs`; stated as an observed discrepancy only.
