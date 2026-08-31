---
id: capabilities-search-privacy-filtering
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
  - statement: "Migration 0001 defines `events.search_tsv` as a generated column whose `CASE` expression yields `NULL::tsvector` (never matched by `@@`) for kind 1059 (NIP-17 gift wrap ciphertext), 30300 (event reminder, author-only defense in depth), 30622 (per-viewer DM-visibility marker), 44100 and 44101 (p-gated membership add/remove notices); migration 0005 adds kind 44200 (agent turn metric) to the same exclusion, and migration 0014 excludes kind 30350 (NIP-PL push-lease, NIP-44 ciphertext) via its own CASE arm — all four migrations state this exclusion is at the storage level, so an excluded event never becomes a search candidate regardless of any later access check."
    entry_class: FACT
    evidence:
      - "migrations/0001_initial_schema.sql:209-223"
      - "migrations/0005_agent_turn_metric_fts.sql"
      - "migrations/0014_push_lease_fts.sql:1-30"
  - statement: "`buzz_search::search` (crates/buzz-search/src/query.rs) issues `WHERE community_id = $1 AND deleted_at IS NULL AND search_tsv @@ search_query.query`, with `community_id` bound as the first, non-optional predicate on every code path through the function, before any channel, kind, author or time-range predicate is layered on."
    entry_class: FACT
    evidence:
      - "crates/buzz-search/src/query.rs"
  - statement: "`buzz_search::search`'s channel-scope predicate (`ChannelScope::Any` / `ChannelLessOnly` / `Channels(ids)` / `ChannelsOrChannelLess(ids)`) constrains which `channel_id` values a search row may carry to reach the candidate list at all; the `ids` in a `Channels`/`ChannelsOrChannelLess` scope are the caller's own accessible-channel set, not the full community's channel list."
    entry_class: FACT
    evidence:
      - "crates/buzz-search/src/query.rs"
  - statement: "`buzz_db::channel::get_accessible_channel_ids` (crates/buzz-db/src/channel.rs:754-782) returns the UNION of two sets: channel ids the caller has an active row for in `channel_members` (`removed_at IS NULL`), and channel ids of every channel in the community whose `visibility = 'open'`; a channel that is not `open` and for which the caller has no active membership row is absent from both branches."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/channel.rs:754-782"
  - statement: "`channels.channel_type` is a three-valued column ('stream', 'forum', 'dm'); `buzz_db::channel`'s own listing query joins `channel_members` identically for every `channel_type` value and adds only one dm-specific clause (`c.channel_type != 'dm' OR cm.hidden_at IS NULL`, hiding a DM the caller archived), so a direct-message channel is a `channel_type` variant of the same `channels`/`channel_members` schema every other channel uses, not a separately modeled object with its own access path."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/channel.rs:963-984"
  - statement: "Because a DM is a `channel_type = 'dm'` row in the same `channels` table, and `get_accessible_channel_ids` only admits a non-open channel through an active `channel_members` row, a DM's accessibility for search is decided by the identical membership check that gates a private stream or forum channel -- there is no DM-specific branch in `get_accessible_channel_ids` itself."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-db/src/channel.rs:754-782"
      - "crates/buzz-db/src/channel.rs:963-984"
    confidence: 0.85
  - statement: "`AppState::get_accessible_channel_ids_cached` (crates/buzz-relay/src/state.rs:1232-1249) wraps `get_accessible_channel_ids` behind a 10-second per-(community, pubkey) cache and is the function both the WS `handle_search_req` path and the HTTP bridge path call to obtain the caller's `accessible_channels` before running any search."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/state.rs:1232-1249"
      - "crates/buzz-relay/src/api/bridge.rs:1010-1013"
  - statement: "Both delivery paths re-check every FTS candidate against the caller's own `accessible_channels` after the SQL query returns: `search_hit_accepted` (crates/buzz-relay/src/api/bridge.rs) and the inline per-hit block inside `handle_search_req` (crates/buzz-relay/src/handlers/req.rs) both drop a hit whose `stored.channel_id` is `Some` and not contained in `accessible_channels`, silently, before the event reaches the caller -- this re-check runs regardless of what the channel-scope SQL predicate already excluded."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs"
      - "crates/buzz-relay/src/handlers/req.rs"
  - statement: "`reader_authorized_for_event` (crates/buzz-core/src/filter.rs:23-31) returns `true` unconditionally unless the event's kind is `KIND_DM_VISIBILITY` (30622) or `KIND_AGENT_TURN_METRIC`, in which case it requires the requesting pubkey to appear in a `#p` tag on the event -- a per-viewer visibility marker is therefore only readable by the pubkey(s) it names, independent of channel membership."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/filter.rs:23-31"
  - statement: "`event_visible_to_reader` (crates/buzz-relay/src/handlers/req.rs:1368-1380) is the combined per-hit gate both delivery paths call on every surviving search candidate: it rejects an author-only-kind event whose author is not the requester (`is_author_only_event`), rejects a shared-gated-kind event that is neither authored by the requester nor explicitly marked shared (`is_unshared_gated_event`), and otherwise defers to `reader_authorized_for_event`'s p-tag check -- three independent gates in one call, run after the channel-membership re-check above."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs:1368-1380"
      - "crates/buzz-core/src/kind.rs:232-244"
  - statement: "`buzz-search/src/query.rs`'s own module-doc comment (lines 1-9, cited by the architecture-flows-search-query node) states the FTS layer's contract explicitly: it returns candidate event ids ordered by relevance only, never an access decision, and the relay is documented as re-running a full per-hit authorization gate on every candidate before serialization -- confirmed directly against `search_hit_accepted` and the inline `handle_search_req` block, both of which run the channel-membership check and `event_visible_to_reader` unconditionally on every hit, on both transports."
    entry_class: FACT
    evidence:
      - "crates/buzz-search/src/query.rs:1-9"
      - "crates/buzz-relay/src/api/bridge.rs"
      - "crates/buzz-relay/src/handlers/req.rs"
  - statement: "`crates/buzz-test-client/tests/e2e_nostr_interop.rs::test_nip17_gift_wrap_not_searchable` sends a kind:1059 gift wrap and a kind:9 control message carrying the same unique token over a live relay connection, then issues a NIP-50 REQ search for that token and asserts the kind:9 control is returned while the gift wrap is not -- exercising the storage-level exclusion from the wire, not merely at the SQL layer."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/e2e_nostr_interop.rs:971-1011"
  - statement: "`crates/buzz-search/tests/fts_integration.rs::excluded_kinds_are_storage_level_unsearchable` inserts a kind:9 control event and privacy-excluded-kind events sharing one unique marker token directly into Postgres, then queries `buzz_search::search` and asserts only the kind:9 control is returned -- a mutation-style test whose own comment states that dropping the migration's `CASE` exclusion would make the excluded kinds surface, i.e. it fails if the storage-level exclusion regresses."
    entry_class: FACT
    evidence:
      - "crates/buzz-search/tests/fts_integration.rs:1168-1186"
  - statement: "The architecture-flows-search-query corpus node (launchpad/docs/corpus/architecture/flows/search-query.md) documents the same request-to-response path this capability node describes privacy filtering within, and is present in the origin/launchpad corpus tree at the recorded revision, making it a valid relationship target."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/flows/search-query.md"
  - statement: "Sibling task issue #815 (launchpad-26/buzz) scopes a separate capability node, capabilities/search/channel-scope.md, for the general channel-scoping behavior of search (which channels a query is restricted to); this node deliberately covers only the privacy-exclusion mechanisms -- storage-level kind exclusion, membership-derived accessible-channels gating (which incidentally also governs DM privacy, since a DM is a channel_type variant), and the per-hit result-gated/author-only/shared-gated checks -- rather than re-describing channel scoping's own general mechanics, to avoid two hand-authored nodes covering the same ground."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#815 title and objective (read directly via gh issue view)"
---

# Search privacy filtering: capability

Buzz's search capability (NIP-50 full-text search, reachable over both the
WebSocket `REQ` door and the HTTP `POST /query` bridge) never returns a
result the searching user is not otherwise authorized to see. A user's
search never surfaces gift-wrapped (NIP-17) content, per-viewer DM-visibility
or agent-turn-metric markers addressed to someone else, author-only or
shared-gated events belonging to another user, or messages in a private
channel or direct-message conversation the searcher does not belong to --
regardless of how strongly the search text matches. This is what lets the
product expose a single search box across a community without that box
becoming a way to read content search was never meant to expose.

## Maturity

**Shipped.** The storage-level kind exclusion is enforced by a Postgres
generated column present since the initial schema migration
(`migrations/0001_initial_schema.sql`), extended by two later migrations
(0005, 0014) without ever removing an exclusion. The per-hit authorization
gate (`search_hit_accepted` / the inline `handle_search_req` check,
`event_visible_to_reader`, `reader_authorized_for_event`) runs unconditionally
on both the WS and HTTP delivery paths today. Both properties carry live E2E
and integration test coverage (`test_nip17_gift_wrap_not_searchable`,
`excluded_kinds_are_storage_level_unsearchable`) rather than resting on
inspection alone.

## Behavioral rules and variants

Privacy filtering for search operates in two layers, applied in this order:

1. **Storage-level exclusion (never a candidate).** `events.search_tsv` is a
   `GENERATED ALWAYS ... STORED` `tsvector` column whose defining expression
   yields `NULL::tsvector` for a fixed set of kinds: 1059 (NIP-17 gift wrap
   ciphertext), 30300 (event reminder), 30622 (DM-visibility marker), 44100/
   44101 (membership add/remove notices), 44200 (agent turn metric), and
   30350 (NIP-PL push-lease ciphertext, excluded by a later migration). A row
   of one of these kinds can never satisfy `search_tsv @@ query`, so it never
   reaches the candidate list irrespective of any later access check -- the
   exclusion is at the index, not at result filtering.
2. **Per-hit re-authorization (candidate, but only if the caller is
   authorized).** Every candidate id that does survive the SQL query is
   refetched and re-checked before being handed to the caller, identically on
   both transports:
   - **Community scope.** `community_id` is the first, non-optional `WHERE`
     predicate `buzz_search::search` ever issues -- a search can never cross
     a community boundary.
   - **Channel/DM membership.** A hit whose `channel_id` is not `NULL` is
     dropped unless that channel id is in the caller's own
     `accessible_channels` (cached via `get_accessible_channel_ids_cached`,
     computed as the union of channels the caller actively belongs to in
     `channel_members` plus channels marked `visibility = 'open'`). Because a
     direct-message conversation is stored as a `channels` row with
     `channel_type = 'dm'` -- not a separate object -- this is the same
     mechanism that keeps a private forum/stream channel's content out of a
     non-member's search results and that keeps a DM's content out of a
     third party's search results: neither is `open`, so neither is reachable
     without an active membership row.
   - **Result-gated kinds.** A DM-visibility (30622) or agent-turn-metric
     event additionally requires the caller's pubkey to appear in a `#p` tag
     on the event (`reader_authorized_for_event`) -- a per-viewer marker is
     readable only by the pubkey(s) it names, independent of channel
     membership.
   - **Author-only and shared-gated kinds.** `event_visible_to_reader` also
     rejects an author-only-kind event whose author is not the requester,
     and a shared-gated-kind event that is neither authored by the requester
     nor explicitly marked shared.

   A hit failing any of these checks is dropped silently -- the rest of the
   response, and the rest of that filter's pagination, is unaffected. No
   error is surfaced for the dropped hit specifically.

**Variants:** the two delivery transports (WS `REQ`, HTTP `POST /query`)
apply every rule above identically; they differ only in how the caller's
`accessible_channels` set and community binding are established on the way
in (connection-time NIP-42 AUTH for WS, per-request NIP-98 signature
verification for HTTP), which is the architecture flow node's territory, not
this capability's.

## Boundary

This node does not describe:
- how a search request travels end-to-end through either transport
  (authentication, admission, request/response shape, pagination, failure
  modes) -- see the flow node for search query
  (`architecture-flows-search-query`).
- the general mechanics of restricting a search to one or more channels
  (`#h`-tag scoping, the `ChannelScope` four-case mapping) as a feature in
  its own right, independent of privacy -- that is sibling issue #815's
  capability node (`capabilities/search/channel-scope.md`, not yet merged at
  the time this node was written).
- how a private channel or a DM conversation is created, or how channel
  membership itself is granted or revoked -- that is the channels/DM
  capability's own territory, not search's.
- how the running relay is operated, deployed or monitored.

## Relationships

- references: architecture-flows-search-query

## Scope and omissions

**This node covers** the privacy-filtering behavior of Buzz's search
capability: the storage-level kind exclusion that keeps gift-wrapped and
other privacy-sensitive content out of the search index entirely, the
membership-derived channel/DM accessibility check applied to every surviving
candidate, and the per-hit result-gated/author-only/shared-gated checks --
across both the WebSocket and HTTP delivery transports, with the tests that
exercise each property.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The end-to-end request/response path for a search query on either transport | `architecture-flows-search-query` |
| General channel-scoping mechanics for search (`#h` tags, `ChannelScope` variants) as a feature independent of privacy | `capabilities/search/channel-scope.md` (issue #815, not yet merged) |
| How channel or DM membership is granted, revoked, or how a channel's `visibility`/`channel_type` is set | the channels/DM capability, not documented by this node |
| Full enumeration of every gated-kind constant (`AUTHOR_ONLY_KINDS`, `RESULT_GATED_KINDS`, the shared-gate list) | `crates/buzz-core/src/kind.rs`, authoritative and not duplicated here |
| Whether the fresh-install-vs-brownfield `search_tsv` exclusion expression (migrations 0001/0005/0008/0014) has fully converged on every real deployment | Not established anywhere inspected for this node; the flow node's own scope-and-omissions section already names this gap |

**Expected but not verified when this node was written:**
- No live relay was run against this node's claims; every claim above is
  sourced from reading code, migrations and existing test files, not from
  executing `just test` / `just ci` as part of authoring this document.
  `validate.py` and the corpus unittest suite were run and are reported in
  this commit.
- Whether `get_accessible_channel_ids`'s membership check is the *only* path
  by which a DM's `channel_id` could ever appear in a non-member's
  `accessible_channels` (for example through a future admin/operator
  override) was not checked beyond reading the one query cited above -- the
  INFERENCE entry in the evidence ledger is scoped to that reading, not to
  every code path that could theoretically populate the set.
- No automated `review-code` pass was available in this environment; this
  node was checked by re-reading the diff against issue #817's Definition of
  Done and the capability template's required sections, not by a second
  model or an adjudication pass. Per the corpus-batch-author skill, that
  cross-model/adjudication pass is deliberately deferred to the batch
  owner's review before merge.
