---
id: capabilities-search-result-reauthorization
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
  - statement: "`buzz_search`'s own module doc states the relay never trusts a search hit by itself: the FTS layer returns canonical event ids ordered by relevance only, the relay refetches full `StoredEvent`s through a `(community_id, event_id)`-scoped fetcher, and runs an access predicate (`search_hit_accepted` in `bridge.rs`) per hit — search is documented as never being the access boundary and never able to widen visibility on its own."
    entry_class: FACT
    evidence:
      - "crates/buzz-search/src/query.rs:1-9"
  - statement: "On the HTTP `POST /query` path, each FTS-returned candidate id is refetched into a full `StoredEvent` and passed through `search_hit_accepted`, which re-checks, against the current request rather than against anything the index recorded: (a) the originating NIP-01 filter's non-pushed-down constraints via `filters_match`, (b) the event's `channel_id`, if any, against the caller's current `accessible_channels`, and (c) `reader_authorized_for_event`; a hit failing any of the three is dropped rather than returned."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs:1686-1716"
      - "crates/buzz-relay/src/api/bridge.rs:1836"
  - statement: "On the WebSocket `REQ` path, `handle_search_req` applies the same three checks inline per hit — `filters_match`, `accessible_channels.contains` on the event's `channel_id`, then `event_visible_to_reader` — immediately before emitting an `EVENT` message for that hit, and a hit failing any check is silently skipped (the loop `continue`s) rather than surfaced as an error to the caller."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs:773-786"
  - statement: "`event_visible_to_reader`, called from both the WS and HTTP result-reauthorization sites, combines three per-event checks in one function — author-only kinds, the persona/engram shared-gate, and `reader_authorized_for_event`'s result-gated-kind ownership check — and its own doc comment directs every read surface (WS REQ/COUNT/fan-out and HTTP `/query`/`/count`/search) to call it instead of inlining the three predicates separately."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs:1339-1380"
  - statement: "`reader_authorized_for_event` gates exactly two kinds — `KIND_DM_VISIBILITY` and `KIND_AGENT_TURN_METRIC` — requiring the reader's own pubkey to appear in the event's `#p` tag, and returns `true` unconditionally for every other kind; its own doc comment states it guards WS historical pull, the HTTP bridge, and live fan-out so that a query bypassing the filter-level `#p` gate (e.g. a kindless `ids:[…]` lookup of a known id) still cannot read another user's private event."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/filter.rs:14-33"
  - statement: "The `accessible_channels` value the reauthorization checks compare an event's `channel_id` against is fetched at request time via `state.get_accessible_channel_ids_cached` on both the WS path (inside `handle_req`, before dispatch to `handle_search_req`) and the HTTP path (inside `query_events_authed`, before dispatch to `handle_bridge_search`) — a per-request lookup, not a value captured once when a WS connection was opened and not anything derived from the search index itself."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs:108-121"
      - "crates/buzz-relay/src/api/bridge.rs:1009-1013"
  - statement: "`get_accessible_channel_ids_cached` is backed by a `moka` in-memory cache with a 10-second time-to-live, and is explicitly invalidated (not left to expire on TTL alone) by `invalidate_membership_local` on a per-user membership change, by `invalidate_all_accessible_channels`/`invalidate_channel_deleted` community-wide, and cross-pod via a spawned invalidation broadcast — so the membership state a search result is reauthorized against is bounded to at most this cache's staleness window, actively shortened by real membership-changing events, and is never sourced from whatever was true when the event was indexed."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/state.rs:890-894"
      - "crates/buzz-relay/src/state.rs:1004-1016"
      - "crates/buzz-relay/src/state.rs:1232-1249"
  - statement: "Because the FTS index (`events.search_tsv`) carries only indexed content text — no channel or membership information — and because every candidate id is independently re-authorized against current `accessible_channels` and `reader_authorized_for_event` at hydrate time rather than at index time, a reader's channel membership changing, or a relay-signed private-visibility snapshot changing, between when a matching event was indexed and when it is searched cannot by itself cause an over-broad disclosure through this path; the FTS layer's own candidate order and content are never treated as sufficient authorization on their own."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-search/src/query.rs:1-9"
      - "crates/buzz-relay/src/api/bridge.rs:1686-1716"
      - "crates/buzz-relay/src/handlers/req.rs:773-786"
    confidence: 0.85
  - statement: "Unit tests directly exercise the per-hit reauthorization gate rather than only its constituent primitives: `search_hit_rejects_envelope_with_mismatched_p_tag`, `search_hit_rejects_event_with_mismatched_author`, `search_hit_rejects_inaccessible_channel`, and `search_hit_rejects_dm_visibility_for_kindless_ids_third_party` in `bridge.rs`'s test module drive `search_hit_accepted` directly; `reader_authorized_for_event_gates_dm_visibility_by_p` and `reader_authorized_for_event_gates_agent_turn_metric_by_p` in `buzz-core/src/filter.rs` drive the underlying per-event ownership check."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs:2951-2976"
      - "crates/buzz-relay/src/api/bridge.rs:3005-3027"
      - "crates/buzz-relay/src/api/bridge.rs:3323-3354"
      - "crates/buzz-relay/src/api/bridge.rs:2982-3001"
      - "crates/buzz-core/src/filter.rs:260-320"
  - statement: "The already-merged flow node `architecture-flows-search-query` narrates this same reauthorization step as one stage (step 8) inside the full NIP-50 request-to-response sequence, and states in its own `Ordered interactions` section that access is decided at refetch/hydrate time, not by the FTS layer — this capability node states the guarantee at product level and references that flow node for the full ordered sequence rather than re-narrating it."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/flows/search-query.md"
relationships:
  - type: references
    target: architecture-flows-search-query
---

# Result reauthorization: capability

When a member searches a Buzz community, every candidate result the full-text
index turns up is independently re-checked against that member's *current*
channel membership and per-event visibility rules before it is ever returned
— on both the WebSocket `REQ` search path and the HTTP `POST /query` bridge.
The search index itself is never trusted as an access decision: it exists to
rank and shortlist candidate events by relevance, and every one of those
candidates is re-authorized at the moment of delivery, using request-time
membership state rather than whatever was true when the event was indexed.
This is what lets the product make full-text search available across a
community's whole event history without that index becoming a second,
independent way to leak a channel a reader has since left, or a private
event a reader was never entitled to see.

## Maturity

**Shipped.** The reauthorization check runs unconditionally on both delivery
paths in the current relay: `search_hit_accepted` on the HTTP bridge
(`crates/buzz-relay/src/api/bridge.rs:1698-1716`, invoked at
`bridge.rs:1836`) and an equivalent inline check on the WebSocket path
(`crates/buzz-relay/src/handlers/req.rs:773-786`). It is exercised by
dedicated unit tests (`search_hit_rejects_envelope_with_mismatched_p_tag`,
`search_hit_rejects_event_with_mismatched_author`,
`search_hit_rejects_inaccessible_channel`,
`search_hit_rejects_dm_visibility_for_kindless_ids_third_party` in
`bridge.rs`, and `reader_authorized_for_event_gates_dm_visibility_by_p` /
`reader_authorized_for_event_gates_agent_turn_metric_by_p` in
`crates/buzz-core/src/filter.rs`), not merely present as unexercised code.

## Behavioral rules, constraints and variants

- **Every candidate is re-authorized, not merely re-fetched.** The FTS query
  (`buzz_search::search`) returns event ids only; the relay refetches the
  full `StoredEvent` for each id and only then decides whether the caller
  may see it.
- **Three checks, applied per hit, on both transports:**
  1. `filters_match` — the original NIP-01 filter's constraints that the FTS
     pushdown did not itself enforce (e.g. `#p`, `#h`, `#e`, `#d`, `ids`).
  2. Channel accessibility — if the event carries a `channel_id`, it must be
     a member of the caller's *current* `accessible_channels`.
  3. `reader_authorized_for_event` (via `event_visible_to_reader` on the WS
     path) — the per-event ownership gate for author-only kinds, the
     persona/engram shared-gate, and the two result-gated kinds
     (`KIND_DM_VISIBILITY`, `KIND_AGENT_TURN_METRIC`).
- **A failing hit is dropped silently, not surfaced as an error.** Both
  paths skip the hit and continue; the caller sees a shorter result set, not
  a partial-failure signal naming which hit was withheld.
- **Membership is read at request time, bounded by a short, actively
  invalidated cache — never read from the index.** `accessible_channels`
  comes from `get_accessible_channel_ids_cached`, a 10-second-TTL cache that
  is explicitly invalidated on a membership change, a channel deletion, or a
  community-wide reset, rather than left to expire on its own. The
  reauthorization check can therefore lag a just-changed membership by at
  most that bounded window, actively shortened by real invalidation events —
  it never reflects membership as it stood when the event was indexed.
- **This is the same result-visibility gate other delivery surfaces use, not
  a search-specific reimplementation.** `event_visible_to_reader`'s own doc
  comment directs every read surface — WS historical pull, WS fan-out, and
  HTTP `/query`/`/count` — to call it rather than inline the three
  predicates separately; this document is scoped to its role in the search
  path specifically (see *Boundary*).

## Boundary

This node does not describe:
- **How the search subsystem itself is built** — the FTS SQL shape, the
  `search_tsv` generated column, ranking. That is `buzz-search`'s own
  concern and the architecture family's territory once a component/container
  node exists for it; this node only concerns itself with the
  re-authorization step that runs after a candidate comes back.
- **The general contract of the `POST /query` or WebSocket `REQ` interfaces**
  they are exposed through. No interface-typed corpus node exists yet to
  reference; when one is written for these surfaces, this node's `Relationships`
  section is the place to add it.
- **The step-by-step request-to-response sequence for a search query**,
  including the authentication and admission steps that run before the
  search branch is even reached. `architecture-flows-search-query` already
  narrates that full ordered sequence, with this reauthorization step as one
  stage (step 8) within it; this node references that flow rather than
  re-narrating it.
- **How the relay is operated** — cache sizing, eviction metrics, or
  monitoring the invalidation broadcast across pods. Those are the
  `operations` surface's concern, not what the product guarantees to a
  searching member.
- **The same result-visibility gate's role outside search** — WS historical
  delivery and live fan-out use the identical `event_visible_to_reader` /
  `reader_authorized_for_event` primitives, but that is those surfaces' own
  capability or flow to document (see `architecture/flows/historical-query.md`
  and `architecture/flows/live-fanout.md`), not this one.

## Relationships

- **references** `architecture-flows-search-query` — the merged flow node
  narrating the full NIP-50 request-to-response sequence this
  reauthorization step is one stage of, on both the WebSocket and HTTP
  transports.

No other relationship target exists yet: `capabilities/` had no prior node in
`origin/launchpad`'s corpus tree at the recorded revision (checked via
`git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus`), and
no interface-typed node for the search surfaces has merged either. The first
sibling capability or interface node to merge is the point to revisit this.

## Scope and omissions

**This node covers** the guarantee that a search result is re-authorized
against current channel membership and per-event visibility rules at
delivery time, on both the WebSocket and HTTP search paths: the three checks
applied per hit, that a failing hit is dropped silently, and that the
membership state used is a short-lived, actively invalidated cache rather
than anything carried by the search index itself.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The FTS query mechanism, ranking, and the `search_tsv` column | `crates/buzz-search/src/query.rs`; `architecture-flows-search-query` |
| The authentication/admission steps that run before the search branch is reached (NIP-98, NIP-42, replay detection) | `architecture-flows-search-query`; `architecture/flows/websocket-authentication.md` |
| The general contract of the `POST /query` and WebSocket `REQ` surfaces | An interface-typed node, not yet written |
| The same result-visibility gate's use outside search (historical delivery, live fan-out) | `architecture/flows/historical-query.md`; `architecture/flows/live-fanout.md` |
| Operating or monitoring the accessible-channels cache (metrics, eviction, cross-pod broadcast reliability) | The `operations` corpus surface, not written for this cache |

**Expected but not verified when this node was written:**
- **No live relay was run against these claims.** Every claim above is
  sourced from reading code and existing test files, not from executing a
  fresh `just test` / `just ci` pass as part of authoring this document.
  `validate.py` was run and is reported in this task's commit; the broader
  test suites were not independently re-run.
- **The cross-pod cache-invalidation broadcast's reliability was not
  independently exercised.** `invalidate_membership_local` and its callers
  spawn a broadcast to other pods (`spawn_cache_invalidation`), but this
  node cites the local invalidation code path and its 10-second TTL as the
  bound, not a live multi-replica test confirming the broadcast always
  lands before the next search request on another pod.
- **No automated `review-code` pass was available in this task's
  environment.** Only a manual self-review against issue #818's Definition
  of Done and this template's own required-sections checklist was
  performed, per this batch's own deliberate deferral of a cross-model
  adjudication pass to the batch owner.
