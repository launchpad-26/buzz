---
id: platforms-relay-subscription-registry
type: platforms
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 46eb901e5aa928aa147fdaef9a509b636218653f."
    entry_class: FACT
    evidence:
      - "commit 46eb901e5aa928aa147fdaef9a509b636218653f"
  - statement: "crates/buzz-relay/src/subscription.rs opens with the crate-level doc comment '//! Subscription registry with active WebSocket indexes for targeted fan-out.', and defines `SubscriptionRegistry` as a `#[derive(Debug, Default)]` struct wrapping six `dashmap::DashMap` fields: `subs` (conn_id -> sub_id -> (filters, community_id, scope)), `channel_kind_index`, `channel_wildcard_index`, `global_kind_index`, `global_p_kind_index`, and `global_wildcard_index`."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/subscription.rs:1"
      - "crates/buzz-relay/src/subscription.rs:84-100"
  - statement: "The registry is server-resolved-community-scoped: every DashMap keyed by more than just conn_id/sub_id also carries a CommunityId (or a CommunityId component of its key), so one process-wide registry instance serves every tenant community without cross-community leakage in its own key space."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/subscription.rs:84-100"
  - statement: "Subscriptions have two mutually exclusive routing scopes, `SubscriptionScope::Global` and `SubscriptionScope::Channels(Vec<Uuid>)`, and registration always resolves to exactly one of the five non-`subs` indexes (or no index at all, for a `kinds: []` subscription, which NIP-01 defines as matching nothing): channel-scoped registrations go to `channel_kind_index` per requested kind or to `channel_wildcard_index` if any filter omits `kinds`; global registrations go to the narrower `global_p_kind_index` when every filter is both kind- and `#p`-constrained, else to `global_kind_index` per kind or `global_wildcard_index` if any filter omits `kinds`."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/subscription.rs:108-223"
      - "crates/buzz-relay/src/subscription.rs:715-742"
      - "crates/buzz-relay/src/subscription.rs:662-696"
  - statement: "`crates/buzz-relay/Cargo.toml` declares `dashmap = { workspace = true }` as a real dependency of the `buzz-relay` crate (line 52), and `buzz-core = { workspace = true }` (line 19), `nostr = { workspace = true }` (line 39), and `uuid = { workspace = true }` (line 50) are also declared there, matching the registry's use of `DashMap`, `buzz_core::{CommunityId, StoredEvent, filter::filters_match}`, `nostr::{Filter, Kind, ...}`, and `uuid::Uuid`."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/Cargo.toml:19"
      - "crates/buzz-relay/Cargo.toml:39"
      - "crates/buzz-relay/Cargo.toml:50"
      - "crates/buzz-relay/Cargo.toml:52"
      - "crates/buzz-relay/src/subscription.rs:1-9"
  - statement: "`AppState` (crates/buzz-relay/src/state.rs) holds one process-wide instance as `pub sub_registry: Arc<SubscriptionRegistry>`, constructed once via `SubscriptionRegistry::new()` (which is `Self::default()`), so every handler that touches subscriptions goes through `state.sub_registry`, not a locally constructed registry."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/state.rs:646"
      - "crates/buzz-relay/src/state.rs:869"
      - "crates/buzz-relay/src/subscription.rs:103-106"
  - statement: "`register_scoped` and `register_channels_scoped` (both `pub fn` on `SubscriptionRegistry`) are called from `crates/buzz-relay/src/handlers/req.rs` to register a new REQ subscription, one per requested authorized channel or as a single global registration when no channel scope applies; both funnel through the private `register_with_scope`, which first calls `remove_subscription` for the same `(conn_id, sub_id)` (NIP-01 same-id replacement) before inserting and indexing the new entry."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs:277-293"
      - "crates/buzz-relay/src/subscription.rs:110-150"
  - statement: "`remove_subscription` (pub fn) is called from `crates/buzz-relay/src/handlers/close.rs`'s `handle_close` to deregister a subscription before sending the client's `CLOSED` acknowledgement, explicitly so no further event is routed to that sub_id after the client's CLOSE is acknowledged; its return value's `scope` is used by the caller to release the corresponding Redis pub/sub topic."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/close.rs:17-29"
      - "crates/buzz-relay/src/subscription.rs:237-244"
  - statement: "`remove_connection` (pub fn) is called from `crates/buzz-relay/src/connection.rs` when a WebSocket connection's serve loop ends, to remove every subscription that connection held and release each one's Redis pub/sub topic; internally it removes the connection's whole `subs` entry in one `DashMap::remove` call and then walks its former subscriptions to clean up every per-index entry."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/connection.rs:288-294"
      - "crates/buzz-relay/src/subscription.rs:269-284"
  - statement: "`remove_channel_subscriptions_scoped` (pub fn) is called from `crates/buzz-relay/src/handlers/side_effects.rs`'s `evict_conn_channel_subscriptions` to strip one revoked channel out of a connection's subscriptions, re-indexing any multi-channel subscription's remaining scope or removing the subscription entirely if no channel is left; `channel_subscriber_conns_scoped` (pub fn) is called by the same file's `evict_non_member_channel_subscriptions` (non-member eviction on open-to-private channel flips) and `evict_all_channel_subscriptions` (bulk eviction when a channel is archived) to enumerate every connection currently subscribed to a channel before individually evicting it."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/side_effects.rs:100-138"
      - "crates/buzz-relay/src/handlers/side_effects.rs:140-167"
      - "crates/buzz-relay/src/handlers/side_effects.rs:169-189"
      - "crates/buzz-relay/src/subscription.rs:289-338"
      - "crates/buzz-relay/src/subscription.rs:350-368"
  - statement: "`fan_out_scoped` (pub fn) is called from `crates/buzz-relay/src/handlers/event.rs`'s `fan_out_event_to_local_subscribers` and from the relay's cross-node pubsub consumer path to return every `(conn_id, sub_id)` pair whose registered filters match one event, dispatching to the channel-and-kind/channel-wildcard indexes for a channel-scoped event or to the per-p-tag/per-kind/global-wildcard indexes for a channel-less (global) event; it re-checks each candidate's live, authoritative scope and community via the private `push_match` helper rather than trusting the index snapshot, so a same-ID subscription replaced mid-lookup cannot leak a match across scopes."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs:241-251"
      - "crates/buzz-relay/src/subscription.rs:378-495"
      - "crates/buzz-relay/src/subscription.rs:535-560"
  - statement: "`per_community_subscriptions` (pub fn) is called once, from `crates/buzz-relay/src/main.rs`'s `emit_in_memory_usage_metrics`, to snapshot the number of active subscriptions per community and feed the `buzz_total_subscriptions` and `buzz_community_subscriptions` gauges; the function's own doc comment states this snapshot approach avoids gauge drift from mismatched increment/decrement calls across communities."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:1543-1557"
      - "crates/buzz-relay/src/subscription.rs:520-533"
  - statement: "`get_filters`, `total_subscriptions`, and `total_connections` are public methods with no call site found anywhere under `crates/buzz-relay/src` outside `subscription.rs`'s own `#[cfg(test)]` module; `register` and `remove_channel_subscriptions` (undecorated names, distinct from `register_scoped`/`register_channels_scoped`/`remove_channel_subscriptions_scoped`) are explicitly `#[cfg(test)]`-gated convenience wrappers documented in their own doc comments as preserving the original single-tenant test API, and are not part of the production interface."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/subscription.rs:225-235"
      - "crates/buzz-relay/src/subscription.rs:340-348"
      - "crates/buzz-relay/src/subscription.rs:370-374"
      - "crates/buzz-relay/src/subscription.rs:497-501"
      - "crates/buzz-relay/src/subscription.rs:503-518"
  - statement: "Every non-test index removal in `remove_from_index` is a targeted O(k) lookup (k = number of kinds in the filters, or a single wildcard/p-kind-set lookup) rather than a full scan of the index, per the function's own doc comment and the passing unit test `test_remove_from_index_targeted_no_full_scan`, which registers subscriptions on two distinct channels, removes one, and asserts the other channel's index entry is untouched."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/subscription.rs:562-655"
      - "crates/buzz-relay/src/subscription.rs:1104-1148"
  - statement: "A concurrency regression test, `test_subscription_removal_cannot_delete_replacement_index`, drives a same-sub_id remove and a concurrent same-sub_id re-register on two threads with synchronization points, and asserts the replacement subscription remains reachable through fan-out afterward — i.e. a slow removal's index cleanup cannot delete a newer replacement's index entry that arrived while the removal was still in flight."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/subscription.rs:853-907"
  - statement: "A second regression test, `test_stale_candidate_snapshot_does_not_cross_subscription_scope`, reproduces `fan_out_scoped`'s unlocked candidate-snapshot pattern directly against `push_match` and asserts that a subscription moved to a different channel between snapshot and match cannot deliver the old channel's event through the stale snapshot — the authoritative re-check inside `push_match` is what this test exercises."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/subscription.rs:909-951"
  - statement: "A dedicated security regression test, `test_global_sub_does_not_receive_channel_events`, asserts that a global (channel_id = None) subscription never receives a channel-scoped event and still receives a genuinely global event, and the module carries an explicit `NOTE` comment inside `fan_out_scoped` stating this scoping invariant is symmetric in both directions to prevent both channel-content leakage to global subscribers and global-infrastructure-event leakage to channel subscribers."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/subscription.rs:1352-1383"
      - "crates/buzz-relay/src/subscription.rs:487-492"
  - statement: "`launchpad/docs/corpus/architecture/flows/live-fanout.md` (id `architecture-flows-live-fanout`) already documents `SubscriptionRegistry::fan_out_scoped`'s role inside the end-to-end live fan-out flow — including its interaction with `filter_fanout_by_access`, Redis publish, and cross-node delivery — in its own 'Ordered interactions and data movement' section, and is present in the corpus tree at `origin/launchpad` at the recorded revision."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/flows/live-fanout.md"
      - "git_ls_tree(ref='origin/launchpad', path='launchpad/docs/corpus') -> includes launchpad/docs/corpus/architecture/flows/live-fanout.md at commit 46eb901e5aa928aa147fdaef9a509b636218653f"
  - statement: "Sibling batch-task nodes for issue #1282 (`platforms-relay-req-handler`, drafted locally on branch `task/1282-relay-req-handler`) and issue #1264 (`platforms-relay-close-handler`, drafted locally on branch `task/1264-relay-close-handler`) both use `type: platforms`, `origin: launchpad`, and `audiences: [agent, developer, reviewer]`, and neither branch is present in `origin/launchpad`'s corpus tree at the recorded revision, so this node follows the same `type: platforms` convention for consistency but declares no relationship toward either, since AGENTS.md's own rule requires a relationship target to resolve on the branch being merged into, not the author's worktree."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "known findings from earlier Feature #614 batch tasks, corroborated by direct read of both local worktrees' drafted front matter at commit 46eb901e5aa928aa147fdaef9a509b636218653f"
  - statement: "No corpus node's public-interface table entry claims a Big-O complexity for any method beyond what the source's own doc comments and the `test_remove_from_index_targeted_no_full_scan` test directly support (targeted O(k) removal, where k is the number of kinds in a subscription's filters); this is a deliberate scope limit, not an unverified performance claim."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay/src/subscription.rs:562-655"
      - "crates/buzz-relay/src/subscription.rs:1104-1148"
    confidence: 0.8
relationships:
  - type: references
    target: architecture-flows-live-fanout
---

# Subscription registry (`buzz-relay::subscription::SubscriptionRegistry`)

`SubscriptionRegistry` is an in-memory, `DashMap`-backed structure inside the
`buzz-relay` crate (`crates/buzz-relay/src/subscription.rs`) that tracks every
client's active NIP-01 `REQ` subscription and maintains a set of targeted
fan-out indexes so a newly ingested event can find its matching subscribers
without scanning every live subscription. This node answers: what does the
registry actually store, what is its public interface, who calls it and why,
and what does it guarantee about index correctness under concurrent
registration, removal, and fan-out.

## Responsibility

Per its own crate-level doc comment, the module provides a "subscription
registry with active WebSocket indexes for targeted fan-out"
(`crates/buzz-relay/src/subscription.rs:1`). Concretely, it is the single
process-wide store of "which connection's which subscription wants which
events," server-resolved to one tenant community per entry, and it owns the
indexing scheme that turns "find every subscriber for this event" into a
handful of targeted `DashMap` lookups instead of an O(all-subscriptions) scan.

## Public interface

| Item | Kind | Contract | Evidence |
|---|---|---|---|
| `SubscriptionRegistry::new` | fn | Construct an empty registry (`Self::default()`). | `subscription.rs:103-106` |
| `register_scoped` | fn | Register/replace a subscription under one optional channel (or global if `None`), resolving to `SubscriptionScope::Channels(vec![id])` or `::Global`. | `subscription.rs:110-122` |
| `register_channels_scoped` | fn | Register/replace a subscription under every authorized requested channel at once (`SubscriptionScope::Channels(ids)`). | `subscription.rs:125-140` |
| `remove_subscription` | fn | Remove one `(conn_id, sub_id)` and clean up its index entries; returns the removed scope/community if it existed. | `subscription.rs:238-244` |
| `remove_connection` | fn | Remove every subscription for a connection (e.g. on socket close) and clean up all of their index entries. | `subscription.rs:270-284` |
| `remove_channel_subscriptions_scoped` | fn | Strip one revoked channel out of a connection's subscriptions; re-indexes remaining scope or removes the subscription if none is left. | `subscription.rs:289-338` |
| `channel_subscriber_conns_scoped` | fn | Return the distinct connections subscribed (kind-filtered or wildcard) to one channel in one community. | `subscription.rs:353-368` |
| `fan_out_scoped` | fn | Return every `(conn_id, sub_id)` whose filters match one event, in one community; re-validates scope/community per candidate before including it. | `subscription.rs:379-495` |
| `get_filters` | fn | Look up the stored filters for one `(conn_id, sub_id)`; no production call site found (see Scope and omissions). | `subscription.rs:504-508` |
| `total_subscriptions` / `total_connections` | fn | Aggregate counts across the whole registry; no production call site found (see Scope and omissions). | `subscription.rs:511-518` |
| `per_community_subscriptions` | fn | Snapshot active-subscription counts keyed by community, for gauge emission. | `subscription.rs:520-533` |
| `SubscriptionScope` (enum) | type | `Global` or `Channels(Vec<Uuid>)` — a subscription's server-resolved routing scope; mutually exclusive. | `subscription.rs:19-48` |
| `RemovedSubscription` (struct) | type | `{ community_id, scope }` returned by removal methods so callers can release the matching pub/sub topic. | `subscription.rs:66-73` |
| `ChannelSubscriptionUpdate` (struct) | type | `{ sub_id, removed }` returned per subscription by `remove_channel_subscriptions_scoped`. | `subscription.rs:76-82` |

## Dependencies

**Depends on** (this component requires these to build/run):

| Component | Why | Evidence |
|---|---|---|
| `dashmap` | Every index and the primary `subs` map are `DashMap`s, giving the registry lock-free-per-shard concurrent reads/writes across connections. | `Cargo.toml:52`; `subscription.rs:84-100` |
| `buzz-core` | Uses `CommunityId`, `StoredEvent`, and `filter::filters_match` from `buzz_core` to scope entries per tenant and to evaluate NIP-01 filter matches. | `Cargo.toml:19`; `subscription.rs:9` |
| `nostr` | Uses `nostr::{Filter, Kind, Alphabet, SingleLetterTag}` for filter representation and `#p`-tag extraction. | `Cargo.toml:39`; `subscription.rs:6` |
| `uuid` | Connection IDs (`ConnId`) and channel IDs are `Uuid`s. | `Cargo.toml:50`; `subscription.rs:7,12` |
| `metrics` | Emits `buzz_subscriptions_active` gauge increments/decrements on register/remove. | `Cargo.toml:79`; `subscription.rs:156,262,281,333` |

**Depended on by** (these require this component):

| Component | Why | Evidence |
|---|---|---|
| `crates/buzz-relay/src/state.rs` (`AppState`) | Holds the one process-wide instance as `sub_registry: Arc<SubscriptionRegistry>`. | `state.rs:646,869` |
| `crates/buzz-relay/src/handlers/req.rs` | Registers a new subscription (`register_scoped`, `register_channels_scoped`) on an incoming `REQ`. | `req.rs:277-293` |
| `crates/buzz-relay/src/handlers/close.rs` | Deregisters a subscription (`remove_subscription`) on `CLOSE`, before acknowledging. | `close.rs:17-29` |
| `crates/buzz-relay/src/handlers/event.rs` | Calls `fan_out_scoped` for both the in-process and the cross-node pubsub-consumer delivery paths. | `event.rs:241-251` |
| `crates/buzz-relay/src/connection.rs` | Calls `remove_connection` when a WebSocket connection's serve loop ends. | `connection.rs:288-294` |
| `crates/buzz-relay/src/handlers/side_effects.rs` | Calls `remove_channel_subscriptions_scoped` and `channel_subscriber_conns_scoped` for channel-membership-revocation and archival eviction. | `side_effects.rs:100-189` |
| `crates/buzz-relay/src/main.rs` | Calls `per_community_subscriptions` for periodic in-memory-usage gauge emission. | `main.rs:1543-1557` |

## Boundary

This node does not describe:
- **How a matched event is actually delivered once `fan_out_scoped` returns its
  match list** — the access re-validation (`filter_fanout_by_access`), Redis
  publish, cross-node consumption, and per-connection send/backpressure
  behavior are already documented end-to-end in
  `architecture-flows-live-fanout` (see *Relationships*); this node references
  that flow rather than restating it.
- **The `REQ`/`CLOSE` message-handling protocol itself** — parsing, EOSE
  emission, historical-query construction, and authorization gating live in
  `handlers/req.rs` and `handlers/close.rs`, which are the subject of sibling
  tasks #1282 and #1264, not this node.
- **Install/usage instructions for a human running `buzz-relay`** — `buzz-relay`
  carries no crate-level `README.md` at the recorded revision (only 6 of 30
  crates in this repository do).
- **Any node-specific exclusion beyond the above:** the internal index-key
  types (`IndexKey`, `GlobalPKindIndexKey`) and the private helper functions
  (`register_with_scope`, `remove_from_index`, `push_match`,
  `extract_kinds_from_filters`, `extract_global_p_kind_index_keys`,
  `event_p_tag_values`) are implementation detail behind the public interface
  table above; they are described only insofar as they explain a public
  method's contract in *Public interface* and *Responsibility*, not
  individually cataloged.

## Relationships

- references: `architecture-flows-live-fanout` — that node already documents
  `fan_out_scoped`'s role inside the full live fan-out flow (access
  re-validation, Redis publish, cross-node delivery); this node is the
  registry-internals detail behind that flow's fan-out step, not a
  duplicate of it. Confirmed present in `origin/launchpad`'s corpus tree at
  the recorded revision.
- No `depends-on` or `part-of` relationship is declared toward
  `platforms-relay-req-handler` (#1282) or `platforms-relay-close-handler`
  (#1264): both are drafted only on local, unmerged branches at the recorded
  revision, and `AGENTS.md`'s own rule requires a relationship target to
  resolve on the branch being merged into, not the author's worktree.

## Scope and omissions

**This node covers** what `SubscriptionRegistry` is, its full public method
surface, its concurrency/correctness guarantees as demonstrated by its own
regression tests, and its real dependency edges in both directions —
standing alone as one component, independent of whether `platforms-relay-req-handler`
or `platforms-relay-close-handler` ever land.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The end-to-end live fan-out flow (access re-check, Redis, cross-node delivery, send/backpressure) | `architecture-flows-live-fanout` |
| `REQ` message handling, historical query construction, authorization gating | `#1282` / `platforms-relay-req-handler` (unmerged at time of writing) |
| `CLOSE` message handling | `#1264` / `platforms-relay-close-handler` (unmerged at time of writing) |
| The front-matter contract itself | `launchpad/docs/corpus/schema/node.schema.json` |
| Creating, updating, and retiring any corpus node procedurally | `launchpad/docs/corpus/AGENTS.md` |

**Expected but not verified when this node was written:**
- Whether `get_filters`, `total_subscriptions`, or `total_connections` are
  reserved for a not-yet-implemented caller (e.g. an admin/debug surface) or
  are genuinely dead production code was not determined — only that no
  production call site exists under `crates/buzz-relay/src` today, and each
  has its own `#[cfg(test)]`-independent doc comment describing intended use.
- Whether any load or chaos test exercises the registry's `DashMap` shard
  contention or memory growth under a large number of concurrent
  subscriptions was not checked in this repository; that would be an
  operational/performance concern out of scope for a component-level node.
