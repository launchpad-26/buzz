---
id: capabilities-search-channel-scope
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
  - statement: "Every `buzz_search::SearchQuery` carries a `CommunityId` at the type level and every execution binds `community_id = $ctx` as the query's first, non-negotiable predicate; there is no construction path that omits it, and channel scope is layered on top of that predicate, never in place of it."
    entry_class: FACT
    evidence:
      - "crates/buzz-search/src/lib.rs"
      - "crates/buzz-search/src/query.rs"
  - statement: "Channel scoping inside a search query is expressed by the `ChannelScope` enum with four variants — `Any` (no constraint), `ChannelLessOnly` (`channel_id IS NULL` only), `Channels(ids)` (restricted to a channel list), and `ChannelsOrChannelLess(ids)` (that list plus channel-less events) — and the enum's own doc states it closes a case the legacy `(Option<Vec<Uuid>>, bool)` pair could not express unambiguously."
    entry_class: FACT
    evidence:
      - "crates/buzz-search/src/query.rs"
  - statement: "The set of channels a pubkey may search within one community is computed by `buzz_db::channel::get_accessible_channel_ids` as the union of (a) channels where the pubkey has an active membership row (`removed_at IS NULL`) and (b) every channel in that community whose `visibility` is `open`; a private channel the pubkey is not an active member of is in neither branch and is therefore excluded."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/channel.rs"
  - statement: "Both the WebSocket `REQ` search path and the HTTP `POST /query` bridge resolve this same accessible-channel set once per request through `AppState::get_accessible_channel_ids_cached` (a 10-second cache falling back to `get_accessible_channel_ids` on a miss) before any `ChannelScope` is built, so the two transports share one channel-resolution mechanism rather than two independent ones."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/state.rs"
      - "crates/buzz-relay/src/api/bridge.rs"
  - statement: "When a search filter carries a `#h` tag, both `handle_search_req` (WS) and `handle_bridge_search` (HTTP) intersect the tag's channel ids with the caller's accessible-channel set via the identical `.filter(|id| accessible_channels.contains(id))` pattern; if every requested channel id is invalid or inaccessible, the filter is skipped (matches nothing) rather than falling back to the caller's broader accessible scope."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs"
      - "crates/buzz-relay/src/api/bridge.rs"
  - statement: "When a search filter carries no `#h` tag, both transports use `build_search_channel_scope_filter(accessible_channels, include_global)` to build the community-wide scope: the caller's full accessible-channel set, plus channel-less/global events when `include_global` is true, per the function's own doc table mapping (accessible, include_global) pairs onto the four `ChannelScope` variants."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs"
  - statement: "The HTTP `POST /query` bridge always calls `build_search_channel_scope_filter` with `include_global = true`, so an HTTP search caller's community-wide scope always includes channel-less events; the WS path instead passes `token_channel_ids.is_none()` as `include_global`, so a connection authenticated with a channel-scoped auth token (`token_channel_ids` present) gets `include_global = false` and never receives channel-less/global hits in its community-wide search scope, while a connection with no such scoped token does."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs"
      - "crates/buzz-relay/src/handlers/req.rs"
  - statement: "When accessible channels are empty and `include_global` is false, `build_search_channel_scope_filter` returns `None`, and both callers treat that as a hard short-circuit that never reaches `buzz_search::search`: the WS handler sends `EOSE` immediately and the HTTP bridge returns `200` with an empty JSON array."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs"
      - "crates/buzz-relay/src/api/bridge.rs"
  - statement: "After the FTS query returns candidate hits, both transports independently re-check each hit's `channel_id` against the caller's accessible-channel set before the hit is ever delivered: the HTTP bridge's `search_hit_accepted` rejects a hit whose `channel_id` is `Some` and not contained in `accessible_channels`, and the WS path applies the equivalent inline check — this re-check runs regardless of which `ChannelScope` the FTS query itself used."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs"
      - "crates/buzz-relay/src/handlers/req.rs"
  - statement: "Because every hit is re-checked against `accessible_channels` after retrieval, independent of whichever `ChannelScope` variant the SQL query used to narrow candidates, a bug in the pre-query `ChannelScope` construction could not by itself leak a channel-scoped event past a caller who lacks access to that channel — the post-query recheck is a second, independent enforcement of the same boundary rather than a restatement of the first."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-search/src/query.rs"
      - "crates/buzz-relay/src/api/bridge.rs"
      - "crates/buzz-relay/src/handlers/req.rs"
    confidence: 0.85
  - statement: "`channel_scope_restricts_results` and `channel_less_only_excludes_per_channel_events`, both in `crates/buzz-search/tests/fts_integration.rs`, exercise `Channels`, `ChannelsOrChannelLess`, `ChannelLessOnly` and `Any` against a real Postgres FTS index and assert the returned hit sets differ exactly as the variant's semantics require."
    entry_class: FACT
    evidence:
      - "crates/buzz-search/tests/fts_integration.rs"
  - statement: "`search_hit_rejects_inaccessible_channel`, in `crates/buzz-relay/src/api/bridge.rs`, asserts that `search_hit_accepted` rejects a channel-scoped hit when the caller's accessible-channel list is empty and accepts the same hit once that channel id is present in the list."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs"
  - statement: "`restricted_search_scope_excludes_global_results` and `restricted_search_scope_without_accessible_channels_matches_nothing`, both in `crates/buzz-relay/src/handlers/req.rs`, assert that a scoped-auth caller with channel access still scopes to exactly that channel (never broadening to global) and that empty accessible channels plus `include_global = false` returns `None` rather than falling back to an unscoped search."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs"
---

# Channel-scoped search results: capability

A searcher — human or agent, over either the WebSocket `REQ` door or the HTTP
`POST /query` bridge — can run a NIP-50 full-text search and receive only
results from channels they can actually read: channels where they hold an
active membership, plus any channel in the community marked `open`, plus
(depending on how they authenticated) channel-less/global events. A search
can never surface an event scoped to a private channel the searcher does not
belong to, regardless of how strongly the search text matches it.

## Maturity

Shipped. `ChannelScope`, `build_search_channel_scope_filter`,
`search_hit_accepted` and the accessible-channel resolution path are all
current, exercised code on both the WS and HTTP search entry points, backed
by unit and integration tests that run against a real Postgres FTS index (see
*Verification* below).

## Behavioral rules and variants

- **Community scope is non-negotiable and comes first.** Every search query
  binds `community_id = $ctx` before any channel predicate is added; channel
  scope only ever narrows within one community's events, never across
  communities.
- **A channel-tagged filter (`#h`) narrows to the intersection, never
  broadens.** If a filter names specific channels, the search is scoped to
  whichever of those the caller can access. A caller naming only channels
  they cannot access gets zero results from that filter, not a fallback to
  their full accessible set.
- **An untagged filter uses the caller's full accessible scope.** Accessible
  channels are the union of active memberships and community-`open`
  channels; a caller with no memberships can still search every open channel
  in the community.
- **Channel-less/global inclusion depends on how the caller authenticated.**
  The HTTP bridge always includes channel-less events in the community-wide
  scope. The WS door only does when the connection has no channel-scoped
  auth token — a connection authenticated with a token restricted to
  specific channels never sees channel-less/global hits, even for an
  untagged filter, while a normally authenticated connection does.
- **No accessible channels and no global inclusion short-circuits before any
  SQL runs.** WS sends `EOSE` immediately; HTTP returns an empty array. This
  is a distinct case from "zero matches" — the query is never issued.
- **Every hit is re-checked after retrieval, not only filtered beforehand.**
  A hit whose `channel_id` fails the caller's current accessible-channel
  check is dropped after the FTS query returns it, independent of which
  `ChannelScope` variant scoped the query itself. This is the capability's
  defense-in-depth: a narrowing mistake in query construction is not the
  only thing standing between a private channel and an unauthorized
  searcher.

## Boundary

This node does not describe:
- **How full-text matching itself works** — tsquery construction, relevance
  ranking, prefix/typeahead mode — which is `buzz-search`'s own concern and
  is documented by the flow node below, not restated here.
- **The transport/authentication mechanics of the two search entry points**
  (NIP-98 bridge auth, WS connection-time NIP-42 auth, replay detection,
  admission) — also owned by the flow node below.
- **The step-by-step request-to-response sequence** for a search call —
  trigger, ordered interactions, termination — which is exactly what the
  flow node exists to narrate.
- **How channel membership or visibility itself is created, changed, or
  enforced outside of search** — no corpus node yet documents channel
  membership/visibility as its own capability; this node only describes how
  search consumes that state, not how it is produced.
- **The `COUNT`/`/count` request shape.** It is a related but distinct
  handler and this node makes no claim about whether its channel scoping
  matches search's.

## Relationships

- references: `architecture-flows-search-query` — the flow node that
  narrates the full request-to-response path (both transports) this
  capability's channel-scoping rules operate inside of; this node exists to
  state the channel-scope *rules*, the flow node exists to state the
  *sequence* they're applied in.

**Checked against the merge target**
(`git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus`):
`architecture-flows-search-query` is present there. No channel-membership or
channel-visibility capability node is merged yet, so no edge is declared
toward one — the *Boundary* section above names that gap instead of
inventing a target.

## Verification

- `channel_scope_restricts_results` and
  `channel_less_only_excludes_per_channel_events`
  (`crates/buzz-search/tests/fts_integration.rs`) — the four `ChannelScope`
  variants against a real Postgres FTS index.
- `search_hit_rejects_inaccessible_channel`
  (`crates/buzz-relay/src/api/bridge.rs`) — the post-query per-hit channel
  recheck.
- `restricted_search_scope_excludes_global_results` and
  `restricted_search_scope_without_accessible_channels_matches_nothing`
  (`crates/buzz-relay/src/handlers/req.rs`) — the scoped-auth-token
  `include_global = false` behavior and the no-access short-circuit.

## Scope and omissions

**This node covers** what determines a searcher's channel-scoped visibility
in NIP-50 search on both transports: how the accessible-channel set is
computed, how a `#h`-tagged filter narrows within it, how an untagged filter
uses the full scope (including the channel-less/global variance by auth
type), the no-access short-circuit, and the post-query defense-in-depth
recheck.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| FTS matching mechanics, relevance ranking, prefix/typeahead mode | `architecture-flows-search-query`; `crates/buzz-search/src/query.rs`'s own module doc |
| WS/HTTP transport authentication and admission | `architecture-flows-search-query` |
| Channel membership and visibility as their own capability (creation, joining, roles, open vs. private) | Not yet documented by any merged corpus node |
| `/count`'s channel scoping | Not established anywhere inspected for this node |
| `buzz-cli`'s `messages search` fixed-kind behavior beyond noting it exists | `crates/buzz-cli/src/commands/messages.rs`, not this node |

**Expected but not verified when this node was written:**
- Whether `/count`'s channel-scoping logic reuses `ChannelScope`/
  `build_search_channel_scope_filter` identically to search was not traced —
  `handlers/count.rs` was not opened for this task.
- No live relay was run against this node's claims; every claim above comes
  from reading code and existing test files, and from
  `python3 launchpad/project-intelligence/corpus/validate.py` reported in
  this task, not from executing a fresh `just test` / `just ci` pass.
- No automated `review-code` pass was available in this task's environment;
  only a manual self-review against issue #815's Definition of Done and this
  document's own template checklist was performed.
