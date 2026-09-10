---
id: layers-data-redis-channel-pubsub
type: layers
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - operator
evidence:
  - statement: "This node was authored and checked against repository revision 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5 on the launchpad branch."
    entry_class: FACT
    evidence:
      - "commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
  - statement: "crates/buzz-pubsub/src/topic.rs's own module doc states 'Pub/sub topics are a routing/performance boundary, not an authorization boundary. Tenant identity still comes from TenantContext on publish/retain paths, and the relay re-checks access before local fan-out.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/topic.rs"
  - statement: "EventTopicKey::redis_channel builds exactly two channel-name shapes: buzz:{community_id}:channel:{channel_id} for EventTopic::Channel(channel_id), and buzz:{community_id}:global for EventTopic::Global, where BUZZ_PREFIX is the constant \"buzz\"; EventTopicKey::parse_redis_channel is the inverse, and rejects any channel name with the wrong prefix, a non-UUID community or channel segment, an unrecognized scope word, or trailing segments."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/topic.rs"
  - statement: "topic.rs's own test suite proves the naming/parsing contract directly: channel_key_includes_community_and_channel and global_key_includes_community assert the two exact formats above; same_channel_in_two_communities_has_different_topics asserts two communities never share a channel string for the same channel_id; parses_channel_topic and parses_global_topic assert the round trip; rejects_malformed_or_wrong_prefix_topics asserts eight malformed inputs (wrong prefix, non-UUID community, missing scope, trailing segments, unrecognized scope word including \"presence\") are all rejected."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/topic.rs"
  - statement: "publisher::publish_event issues exactly one Redis command per call -- PUBLISH against the channel key from EventTopicKey::redis_channel, with the Nostr event's own JSON serialization (nostr::Event::as_json) as the payload -- and returns the subscriber count PUBLISH itself returns; no other Redis command (no SET, no persistence) is issued by this path."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/publisher.rs"
  - statement: "Every call site of PubSubManager::publish_event in crates/buzz-relay (handlers/event.rs, handlers/side_effects.rs, main.rs's NIP-ER reminder scheduler) discards the returned subscriber count -- none inspects it, logs it, or treats a zero-subscriber PUBLISH as a delivery failure."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs"
      - "crates/buzz-relay/src/handlers/side_effects.rs"
      - "crates/buzz-relay/src/main.rs"
  - statement: "PubSubManager::retain_topic increments a local desired-refcount map (desired_topics) keyed by the fully scoped EventTopicKey; only the transition from 0 to 1 sends a Subscribe command to the subscriber task. PubSubManager::release_topic decrements the same map; only the transition to 0 schedules a debounced UnsubscribeIfIdle command, delayed by PubSubConfig.unsubscribe_debounce (default 500ms, PubSubConfig::DEFAULT_UNSUBSCRIBE_DEBOUNCE), and a retain arriving during that delay makes the pending unsubscribe a no-op because the refcount is re-checked when the command is processed."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/lib.rs"
  - statement: "lib.rs's own two tests prove the refcount/debounce behavior directly: retain_release_refcounts_and_debounces_last_release asserts the count increments/decrements correctly across two retains and two releases; same_channel_id_in_two_communities_release_one_keeps_other_live asserts, against a real Redis connection, that releasing community A's retain on a channel_id does not unsubscribe community B's retain on the same channel_id -- proving the refcount is keyed by the fully scoped EventTopicKey (community + topic), not by channel_id alone."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/lib.rs"
  - statement: "subscriber::run_subscriber's reconnect loop uses exponential backoff from a 1-second initial value (BACKOFF_INITIAL_SECS) doubling to a 30-second cap (BACKOFF_MAX_SECS) on every Redis error, and resets to the 1-second initial value after any connection that completed a full connect_and_subscribe cycle (including a clean disconnect), not only after a successful message delivery."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/subscriber.rs"
  - statement: "On each (re)connection, connect_and_subscribe snapshots the current desired_topics map (topics with refcount > 0) and issues one SUBSCRIBE per topic before entering its message loop -- so a reconnect re-establishes exactly the subscriptions local REQ interest currently wants, not a stale set carried over from the previous connection."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/subscriber.rs"
  - statement: "A message received on an unrecognized/malformed channel name, or one that fails Nostr event JSON deserialization, is logged at warn level and dropped (skipped via `continue`) rather than causing the subscriber loop to error or reconnect; a successfully parsed ChannelEvent is sent on a tokio::sync::broadcast channel, and a send with zero active receivers is treated as an expected condition (traced at `trace` level, not `warn`), not an error."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/subscriber.rs"
  - statement: "crates/buzz-relay/src/state.rs declares AppState.local_event_ids as an Arc<moka::sync::Cache<(CommunityId, [u8; 32]), ()>> built with max_capacity(10_000) and time_to_live(60 seconds), and AppState::mark_local_event inserts (community, event_id.to_bytes()) with unit value -- a bounded, TTL-evicted set, not a durable record."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/state.rs"
  - statement: "Every event-publishing call site found in crates/buzz-relay/src/handlers/event.rs calls state.mark_local_event(...) immediately before calling pubsub.publish_event(...), and on a publish_event error, invalidates the same (community, event_id) key from local_event_ids and logs a warn -- a claim-before-publish pattern: the local echo is pre-armed so the event's own return trip through the Redis subscriber loop does not double-deliver it locally, and the pre-arm is rolled back only if the publish itself failed."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs"
  - statement: "fan_out_pubsub_event (the consumer of PubSubManager::subscribe_local, spawned once in main.rs against the shared broadcast receiver) checks local_event_ids for the incoming (community_id, event_id) pair before doing any fan-out work; a hit invalidates the entry and returns immediately (the event was already delivered locally when it was first published on this pod), and a miss proceeds to community-scoped subscription matching."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs"
  - statement: "In crates/buzz-relay/src/handlers/event.rs, the ephemeral-event publish path (kind:24134 pairing and similar) calls fan_out_event_to_local_subscribers unconditionally after attempting pubsub.publish_event, regardless of whether that publish succeeded -- so a Redis PUBLISH failure only prevents delivery to *other* relay pods; the originating pod's own local WebSocket subscribers still receive the event via the in-process fan-out path."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs"
  - statement: "filter_fanout_by_access (crates/buzz-relay/src/handlers/event.rs) is the single chokepoint both the in-process ingest fan-out path and the Redis cross-node fan_out_pubsub_event path call before delivering to any matched connection; its own doc comment states this explicitly. It first drops any match whose connection's resolved community (state.conn_manager.community_for_conn) does not equal the event's community_id, then -- for kinds in AUTHOR_ONLY_KINDS -- drops any match whose connection pubkey is not the event's author."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs"
  - statement: "crates/buzz-pubsub/src/lib.rs's doc comment on PubSubManager::publish_event states directly: 'the topic key is a routing label, not an isolation boundary,' that author-private reminders (kind:30300, stored under the nil channel sentinel) are 'therefore NOT protected by per-author Redis routing,' that 'the actual author-only delivery boundary is filter_fanout_by_access in the relay, which runs on BOTH the in-process and the Redis cross-node (subscribe_local) fan-out paths,' and that 'Redis only ever carries events between nodes inside the relay trust domain; the ciphertext is NIP-44-encrypted to the author regardless.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/lib.rs"
  - statement: "crates/buzz-relay/src/handlers/req.rs calls state.pubsub.retain_topic once per authorized requested channel_id (or once for EventTopic::Global when no channel-scoped filter applies) at REQ/subscription-registration time, after subscription registration and after any replaced prior subscription's topics have already been released."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs"
  - statement: "state.pubsub.release_topic is called from three distinct lifecycle points in crates/buzz-relay: handlers/close.rs on an explicit CLOSE command, connection.rs on WebSocket disconnect (after the send/heartbeat/auth-timeout tasks are joined), and handlers/side_effects.rs when a channel subscription is evicted server-side -- in each case, once per released Global or Channel(channel_id) scope the removed subscription held."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/close.rs"
      - "crates/buzz-relay/src/connection.rs"
      - "crates/buzz-relay/src/handlers/side_effects.rs"
  - statement: "crates/buzz-relay/src/main.rs spawns PubSubManager::run_subscriber once at startup, and separately spawns one consumer task that loops on state.pubsub.subscribe_local().recv(), dispatching each received ChannelEvent to handlers::event::fan_out_pubsub_event; a RecvError::Lagged(n) increments the buzz_multinode_fanout_lag_total counter and logs a warning without stopping the loop, and a RecvError::Closed logs an error and breaks the loop."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs"
  - statement: "PUBLISH/SUBSCRIBE over this Redis topic family carries no acknowledgment, no persistence and no replay: publisher::publish_event issues PUBLISH only (no key is ever written), a message with zero current subscribers is simply not delivered to anyone (ordinary Redis PUBLISH semantics -- nothing in this crate stores it for a later SUBSCRIBE to catch up on), and a pod that is mid-reconnect (during the up-to-30s backoff window) misses any message published to Redis during that window with no mechanism in this crate to detect or recover the gap."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-pubsub/src/publisher.rs"
      - "crates/buzz-pubsub/src/subscriber.rs"
    confidence: 0.85
  - statement: "This mechanism is transport, not a store: it holds no data at rest (publisher.rs issues PUBLISH only, never SET/persistence), is neither authoritative nor derived (Postgres, via buzz-db, is the durable source of truth for every event this mechanism carries -- this mechanism only relays an already-persisted event between relay pods) and is not a cache (there is nothing here to invalidate or expire -- a message not delivered is simply gone, per the no-replay claim above)."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-pubsub/src/publisher.rs"
      - "crates/buzz-pubsub/src/topic.rs"
    confidence: 0.85
  - statement: "launchpad/docs/corpus/architecture/containers/redis.md (id architecture-containers-redis) is merged on origin/launchpad and already catalogues 'cross-pod event fan-out' (lib.rs's PubSubManager::publish_event, topic.rs) as one of five distinct jobs the Redis container's buzz-pubsub crate performs, alongside presence, cross-pod cache invalidation, cross-pod connection control, and shared admission state (NIP-98 replay, rate limiting) -- none of which this node describes."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/containers/redis.md"
  - statement: "relationships.schema.json defines part-of's directionality as 'source is a constituent section/child of target,' with a generated inverse has-part -- the type templates/datastore.md itself recommends for a node describing one job/section of a container-level node, once that container node exists and is merged."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/relationships.schema.json"
  - statement: "At the recorded revision, git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus contains no launchpad/docs/corpus/layers/ path at all -- this is the first layers/data/redis/* node in the corpus, and no connection-pool.md, dedicated-pubsub-connection.md or key-namespacing.md sibling exists yet to relate to."
    entry_class: FACT
    evidence:
      - "git_ls_tree(ref='origin/launchpad', path='launchpad/docs/corpus') -> no launchpad/docs/corpus/layers/ prefix present at commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
  - statement: "Issue #1091's Definition of Done requires this node to state whether the store is authoritative, derived, cache or transport; describe owned data, key access patterns, lifecycle/retention and consistency semantics; name tenancy/security boundaries and failure behavior; and link schema/migrations/code/tests rather than copy DDL."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1091 definition of done"
  - statement: "The batch dispatch brief for this task (Feature #610's overnight corpus batch) states that every launchpad/docs/corpus/layers/data/... document in this batch uses type: layers in its front matter, overriding whatever type a real instance of the chosen template would otherwise pick on its own reasoning (templates/reference.md gives no layers/data worked example and, left to its own account in 'A note on type', would direct an instance to whichever surface value its subject's own domain calls for) -- disclosed here rather than silently applied, per standards/taxonomy.md's rule that an imperfect or externally-forced type fit be named in the node's own evidence."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "batch dispatch brief for launchpad-26/buzz#610's corpus batch (this task's own orchestrating instructions, corpus-batch-author skill run against Feature #610)"
relationships:
  - type: part-of
    target: architecture-containers-redis
---

# channel-pubsub: reference

This node catalogues the Redis-based mechanism by which `buzz-relay` fans a Nostr
event out to every relay pod, so that a client connected to pod A receives an event
published through pod B. It is one of the five distinct jobs
`architecture/containers/redis.md` (`architecture-containers-redis`) already
catalogues for the Redis container as a whole -- "cross-pod event fan-out" -- and
this node is the zoomed-in view of that one job: its channel-naming scheme, its
publish/subscribe mechanism, its lifecycle, and its tenancy and failure behavior.
It does not describe Redis's other four jobs (presence, cross-pod cache
invalidation, cross-pod connection control, shared admission state), which stay in
the parent container document.

## What kind of store this is

This mechanism is **transport, not a store**. `publisher::publish_event` issues a
single `PUBLISH` per call and nothing else -- no key is ever `SET`, so there is
nothing here to be authoritative or derived *of*. Postgres (via `buzz-db`) is the
durable source of truth for every event this mechanism carries; this mechanism only
relays an event a pod has already persisted, to every other pod, so that pod's own
locally-connected clients can receive it too. It is not a cache either: there is no
entry to invalidate or expire, because a message that finds no current subscriber is
simply never delivered -- ordinary Redis `PUBLISH` semantics, with nothing in this
crate storing it for a later `SUBSCRIBE` to catch up on.

## Topics

| Topic | Redis channel name | Scope | Built/parsed by |
|---|---|---|---|
| `EventTopic::Channel(channel_id)` | `buzz:{community_id}:channel:{channel_id}` | One specific channel, within one community | `EventTopicKey::redis_channel` / `EventTopicKey::parse_redis_channel` |
| `EventTopic::Global` | `buzz:{community_id}:global` | Community-wide events not routed to one exact channel (including channel-less ephemeral kinds, via the nil-UUID sentinel described in `handlers/event.rs`) | same |

Both shapes are prefixed by the crate's `BUZZ_PREFIX` constant (`"buzz"`) and scoped
by `community_id` first. `topic.rs`'s own test suite
(`rejects_malformed_or_wrong_prefix_topics`) proves the parser rejects a wrong
prefix, a non-UUID community or channel segment, a missing or unrecognized scope
word (including `"presence"` -- deliberately not a shape this mechanism owns), and
trailing segments.

## Commands

| Command | Direction | Purpose | Call site |
|---|---|---|---|
| `PUBLISH` | relay -> Redis | Publish one Nostr event's own JSON serialization to a topic's channel name; returns a subscriber count every call site discards | `crates/buzz-pubsub/src/publisher.rs` |
| `SUBSCRIBE` | relay -> Redis | Add a topic to the current pub/sub connection's active set, on the first local `retain_topic` for that topic and on every reconnect for every topic with a live refcount | `crates/buzz-pubsub/src/subscriber.rs` |
| `UNSUBSCRIBE` | relay -> Redis | Remove a topic from the active set, after `unsubscribe_debounce` (default 500ms) has elapsed with the refcount still at zero | `crates/buzz-pubsub/src/subscriber.rs` |

## Access pattern, lifecycle and consistency semantics

**Subscription lifecycle is refcounted and debounced, not one-shot.**
`PubSubManager::retain_topic`/`release_topic` maintain a local desired-refcount map
keyed by the fully scoped `EventTopicKey` (community + topic, not channel id alone
-- proven by `lib.rs`'s own
`same_channel_id_in_two_communities_release_one_keeps_other_live` test). Only a
0-to-1 transition issues `SUBSCRIBE`; only a 1-to-0 transition schedules a debounced
`UNSUBSCRIBE`, which becomes a no-op if a new retain arrives inside the debounce
window. `retain_topic` is called once per authorized channel (or once for `Global`)
whenever a client registers a `REQ` subscription (`handlers/req.rs`); `release_topic`
is called on `CLOSE` (`handlers/close.rs`), on WebSocket disconnect
(`connection.rs`), and when a channel subscription is evicted server-side
(`handlers/side_effects.rs`).

**Reconnection replays desired state, not history.** `subscriber::run_subscriber`
reconnects with exponential backoff (1s, doubling to a 30s cap) on any Redis error,
resetting to 1s after any connection that ran a full cycle. On each (re)connect it
snapshots the current desired-refcount map and re-issues `SUBSCRIBE` for exactly
those topics -- so a reconnect restores current local interest, not whatever
messages were missed while disconnected.

**Delivery is at-most-once, with no acknowledgment, no persistence and no replay.**
A `PUBLISH` to a topic with zero current subscribers is simply not delivered to
anyone; nothing in this crate stores it. A pod mid-reconnect (inside the backoff
window above) misses anything published to Redis during that window, with no
mechanism in this crate to detect or recover the gap (INFERENCE, reasoned from
`publisher.rs` issuing `PUBLISH` only and `subscriber.rs` having no catch-up
mechanism, not read from an explicit statement to that effect).

**Local delivery does not depend on the Redis publish succeeding.** Every
event-publishing call site in `handlers/event.rs` calls `state.mark_local_event`
*before* `pubsub.publish_event`, and on publish failure invalidates that mark and
logs a warning -- but the originating pod's own local WebSocket fan-out
(`fan_out_event_to_local_subscribers`) still runs regardless of whether the Redis
`PUBLISH` succeeded. A Redis publish failure therefore only prevents *other* pods
from receiving the event; it never blocks local delivery on the pod that received
it first.

**The receiving side dedupes local echo, not cross-pod duplicates.**
`fan_out_pubsub_event` (the sole consumer of `subscribe_local`, spawned once in
`main.rs`) checks `local_event_ids` -- a `moka` cache with a 60-second TTL and a
10,000-entry capacity, keyed `(community_id, event_id)` -- before doing any
fan-out work. A hit means this pod already delivered the event locally when it
first published it, so the echo is dropped and the mark is invalidated. A message
that fails to parse (unexpected channel name, invalid event JSON) is logged at
`warn` and dropped by the subscriber loop itself, without tearing down the
connection.

## Tenancy and security boundary

**The topic key is a routing label, not an isolation boundary.** `topic.rs`'s own
module doc states this directly, and `lib.rs`'s `publish_event` doc comment repeats
it for the specific case of author-private reminders (kind:30300): the community-
scoped channel name controls *which relay pods happen to receive* a message
(because pods only dynamically subscribe to topics with local interest), not *who
is allowed to see it*. The actual access-control chokepoint is
`filter_fanout_by_access` in `handlers/event.rs`, which runs identically on the
in-process ingest fan-out path and on this mechanism's Redis cross-node path: it
first drops any match whose connection's resolved community does not equal the
event's own `community_id`, then, for kinds in `AUTHOR_ONLY_KINDS`, drops any match
whose connection pubkey is not the event's author. NIP-44 ciphertext already
protects payload confidentiality independent of any of this -- Redis only ever
carries events between relay pods inside the relay's own trust domain.

## Failure behavior

- **Redis connection lost:** the subscriber loop reconnects with exponential
  backoff (1s doubling to a 30s cap); messages published to Redis during that
  window are missed with no recovery mechanism (see *consistency semantics* above).
- **`PUBLISH` call fails:** the calling handler invalidates its own
  `mark_local_event` pre-arm, logs a `warn`, and continues -- the failure is not
  retried, and it does not block the local pod's own in-process delivery to its
  own connected clients.
- **A received message fails to parse** (unrecognized channel name, or event JSON
  that does not deserialize): logged at `warn` and dropped; the subscriber loop
  keeps running.
- **No local broadcast receivers for a delivered message:** treated as an
  expected condition (`trace`-level log), not an error -- `broadcast::Sender::send`
  returning an error just means nobody is currently listening in-process.
- **The local `broadcast` receiver lags:** `RecvError::Lagged(n)` increments the
  `buzz_multinode_fanout_lag_total` metric and logs a `warn`; the consumer loop
  keeps running and simply continues from wherever the channel's ring buffer next
  yields a message -- the lagged messages themselves are gone.

## Boundary

This node does not describe:
- **Redis's other four jobs** (presence, cross-pod cache invalidation, cross-pod
  connection control, shared admission state/NIP-98 replay/rate limiting) or
  Redis's own deployment, technology version, or security implications as a whole
  container -- see `architecture/containers/redis.md`
  (`architecture-containers-redis`), which this node is `part-of`.
- **Connection-pool sizing and limits** (`deadpool_redis::Pool`, `BUZZ_REDIS_POOL_SIZE`)
  -- named in passing above only as "every call site" of the pooled `PUBLISH` path;
  the pool's own shape is a separate `layers/data/redis/connection-pool.md` task in
  this same batch, not yet merged.
- **Why the subscriber loop uses its own dedicated, non-pooled Redis connection**
  rather than the shared pool -- a separate `layers/data/redis/dedicated-pubsub-connection.md`
  task in this same batch, not yet merged.
- **General Redis key-namespacing conventions** beyond the two channel-name shapes
  this specific mechanism owns -- a separate `layers/data/redis/key-namespacing.md`
  task in this same batch, not yet merged.
- **The domain meaning of the Nostr events carried** (what a channel or a thread
  *is*) -- no data-entity-shaped corpus node for those concepts is merged yet to
  link to.

## Relationships

- `part-of`: `architecture-containers-redis` -- this mechanism is one of that
  node's own five catalogued jobs, zoomed in.

## Scope and omissions

**This node covers** the two Redis pub/sub topic shapes this mechanism uses, the
`PUBLISH`/`SUBSCRIBE`/`UNSUBSCRIBE` commands it issues, its refcounted-and-debounced
subscription lifecycle, its reconnect behavior, its delivery/consistency semantics
(at-most-once, no persistence, no replay), its tenancy boundary (a routing label,
not an access-control boundary -- `filter_fanout_by_access` is the real one), and
its failure behavior at each of the points named above.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Redis's other four jobs and the container as a whole | `architecture-containers-redis` (merged) |
| Connection-pool sizing and limits | `layers/data/redis/connection-pool.md` (this batch, not yet merged) |
| The dedicated non-pooled subscriber connection's own rationale | `layers/data/redis/dedicated-pubsub-connection.md` (this batch, not yet merged) |
| General Redis key-namespacing conventions | `layers/data/redis/key-namespacing.md` (this batch, not yet merged) |
| The domain meaning of the Nostr events this mechanism carries | No data-entity-shaped node merged yet |
| Presence, reconnect-behavior (as a general Redis concern beyond this one mechanism), role, TTL policy, and typing indicators | Later-batch `layers/data/redis/*` siblings, not yet merged |

**Expected but not verified when this node was written:**

- **Whether a Redis `PUBLISH` with zero subscribers is silently dropped by Redis
  itself, versus buffered anywhere server-side, was not verified against Redis's
  own documentation** -- the claim above is read from this crate's code (no
  catch-up mechanism exists on the consumer side) and marked `INFERENCE`
  accordingly, not confirmed against Redis's own PUBLISH/SUBSCRIBE specification.
- **No production or staging telemetry was inspected** for how often the
  reconnect-backoff gap actually drops messages in practice, or how often
  `buzz_multinode_fanout_lag_total` fires -- this node describes the mechanism as
  written in code, not its observed real-world failure rate.
- **The `type: layers` override recorded in this node's evidence ledger has not
  been checked against a later, corpus-authored `layers`-type standard**, because
  none is merged at the recorded revision -- see the disclosed `TEAM_KNOWLEDGE`
  entry above.
