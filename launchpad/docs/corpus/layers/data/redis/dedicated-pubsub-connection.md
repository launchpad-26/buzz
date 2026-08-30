---
id: layers-data-redis-dedicated-pubsub-connection
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
  - statement: "node.schema.json's type enum has 13 members (architecture, layers, capabilities, platforms, implementation, interfaces-events, verification, operations, development, release, governance, agent, ingestion) and contains no dedicated sub-taxonomy for a data-layer connection pattern; this node uses type: layers per the disclosed batch precedent set by prior layers/data/... documents in this same batch, which override the datastore.md template's own worked reasoning that a real datastore instance takes type: architecture."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "crates/buzz-pubsub/src/lib.rs's own top-of-file module doc states the architecture directly: a shared deadpool-redis pool handles PUBLISH/SET/ZADD-style commands, while a 'dedicated redis::aio::PubSub connection (NOT from pool)' handles dynamic SUBSCRIBE; and states plainly, 'Dedicated pub/sub connection is stateful and cannot be shared. Pool connections handle all other commands.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/lib.rs"
  - statement: "crates/buzz-pubsub/src/subscriber.rs's connect_and_subscribe function opens a dedicated connection via redis::Client::open(redis_url)?.get_async_pubsub().await? — constructed directly from a Client, never acquired from the deadpool_redis::Pool the rest of PubSubManager holds — and uses it for dynamic per-topic SUBSCRIBE/UNSUBSCRIBE of buzz:{community}:channel:{id} and buzz:{community}:global channels."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/subscriber.rs"
  - statement: "crates/buzz-pubsub/src/cache_invalidation.rs's connect_and_subscribe function independently opens its own dedicated redis::Client::open(redis_url)?.get_async_pubsub().await? connection and calls conn.psubscribe(CACHE_INVALIDATION_PATTERN) once, where CACHE_INVALIDATION_PATTERN is the fixed pattern buzz:*:cache-invalidate — a second, separate dedicated connection from the one subscriber.rs opens."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/cache_invalidation.rs"
  - statement: "crates/buzz-pubsub/src/conn_control.rs's connect_and_subscribe function independently opens a third dedicated redis::Client::open(redis_url)?.get_async_pubsub().await? connection and calls conn.psubscribe(CONN_CONTROL_PATTERN) once, where CONN_CONTROL_PATTERN is the fixed pattern buzz:*:conn-control."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/conn_control.rs"
  - statement: "crates/buzz-relay/src/main.rs constructs exactly one deadpool_redis::Pool (sized by config.redis_pool_size) and passes it into PubSubManager::new; it then spawns three separate tokio tasks — pubsub_for_sub.run_subscriber(), pubsub_for_cache.run_cache_invalidation_subscriber(), pubsub_for_conn_ctrl.run_conn_control_subscriber() — each of which independently establishes its own dedicated connection per the three evidence entries above, so a single relay pod holds one pooled Redis client plus three separate dedicated pub/sub connections at steady state."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs"
  - statement: "crates/buzz-pubsub/src/subscriber.rs's run_subscriber module doc states the desired-topic refcount map is 'the source of truth' and that 'on every reconnect, this task snapshots topics with count > 0 and subscribes to those exact Redis channels before processing messages' — so which channels the dedicated connection is subscribed to is reconstructed from local state on every reconnect, not persisted in Redis itself."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/subscriber.rs"
  - statement: "All three subscriber loops (run_subscriber, run_cache_invalidation_subscriber, run_conn_control_subscriber) share the identical reconnect shape: an outer loop calling connect_and_subscribe, an exponential backoff starting at BACKOFF_INITIAL_SECS = 1 and capped at BACKOFF_MAX_SECS = 30 (doubling each failed attempt), reset to the initial value after any clean (non-error) disconnect, and no explicit upper bound on the number of reconnect attempts — each loop's own doc comment states it 'never returns' and 'runs for the lifetime of the relay.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/subscriber.rs"
      - "crates/buzz-pubsub/src/cache_invalidation.rs"
      - "crates/buzz-pubsub/src/conn_control.rs"
  - statement: "crates/buzz-pubsub/src/lib.rs's run_subscriber method takes the shared subscription_rx receiver out of a Mutex<Option<...>> with .take(), logs 'Redis pub/sub subscriber already started' and returns immediately if it is already None — so PubSubManager::run_subscriber is enforced at runtime to be called at most once per instance; no equivalent guard exists on run_cache_invalidation_subscriber or run_conn_control_subscriber, which take no shared receiver and can be spawned multiple times without an equivalent runtime check."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/lib.rs"
  - statement: "Every Redis channel name the three dedicated connections subscribe to is prefixed by the crate's BUZZ_PREFIX constant plus a resolved community id — channel_key/global_key in topic.rs for the channel-fan-out connection (buzz:{community}:channel:{uuid} / buzz:{community}:global), CACHE_INVALIDATION_PATTERN (buzz:*:cache-invalidate) and CONN_CONTROL_PATTERN (buzz:*:conn-control) for the other two, both wildcard patterns matched at PSUBSCRIBE time and narrowed back to one community per message only after parsing the concrete channel name the message arrived on."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/topic.rs"
      - "crates/buzz-pubsub/src/cache_invalidation.rs"
      - "crates/buzz-pubsub/src/conn_control.rs"
  - statement: "publish_cache_invalidation's and publish_conn_control's own doc comments in crates/buzz-pubsub/src/lib.rs state both are fire-and-forget at the call site with a durable backstop: a dropped cache-invalidation publish is 'backstopped by the REQ denial-path DB confirmation,' and a dropped conn-control publish is 'backstopped by the durable ban row,' which 'still refuses the next auth attempt' even if live disconnection on another pod is missed."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/lib.rs"
  - statement: "PubSubManager.publish_event's own doc comment in crates/buzz-pubsub/src/lib.rs states Redis 'only ever carries events between nodes inside the relay trust domain' and that the topic key is 'a routing label, not an isolation boundary' — the actual author-only delivery boundary for author-private reminder events is filter_fanout_by_access in the relay, applied uniformly to both in-process and Redis cross-node fan-out, independent of which pod's dedicated connection the message transits."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/lib.rs"
  - statement: "PubSubError (crates/buzz-pubsub/src/error.rs) defines a distinct BroadcastLagged(u64) variant produced when a local tokio::sync::broadcast receiver falls behind and drops messages, separate from the Redis(#[from] redis::RedisError) variant produced by a Redis-level failure — a dedicated connection's own reconnect handles Redis-level disconnects, while BroadcastLagged is a downstream, per-local-subscriber backpressure failure that a reconnect does not address."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/error.rs"
  - statement: "crates/buzz-pubsub/src/lib.rs's PubSubManager holds three separate tokio::sync::broadcast::Sender instances (broadcast_tx, cache_invalidation_tx, conn_control_tx), each constructed with broadcast::channel(4096) — a fixed local buffer of 4096 messages per broadcast channel, independent of and downstream from the dedicated Redis connections' own message stream."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/lib.rs"
  - statement: "crates/buzz-pubsub/src/lib.rs contains #[tokio::test] integration tests marked #[ignore = \"requires Redis\"] (test_publish_and_subscribe_roundtrip, test_cache_invalidation_roundtrip, test_presence_set_and_get, same_channel_id_in_two_communities_release_one_keeps_other_live) that exercise the dedicated-connection subscriber loops end to end against a real Redis instance, plus non-ignored unit tests (retain_release_refcounts_and_debounces_last_release, config_defaults_debounce_but_allows_override) that exercise the local refcount/debounce logic without Redis; crates/buzz-pubsub/src/subscriber.rs separately carries two non-ignored unit tests for the local desired-refcount lookup helper."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/lib.rs"
      - "crates/buzz-pubsub/src/subscriber.rs"
  - statement: "crates/buzz-pubsub/Cargo.toml depends on redis and deadpool-redis with no version pin of its own (workspace = true); the workspace root Cargo.toml pins redis to version \"1.0\" with features [\"tokio-comp\", \"connection-manager\", \"tokio-rustls-comp\"] and deadpool-redis to version \"0.23\" with feature [\"rt_tokio_1\"]."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/Cargo.toml"
      - "Cargo.toml"
  - statement: ".env.example documents REDIS_URL (default redis://localhost:6379) and a commented-out BUZZ_REDIS_POOL_SIZE (default 16); crates/buzz-relay/src/config.rs's Config parsing reads BUZZ_REDIS_POOL_SIZE, falling back to 16 when unset, non-numeric, or zero — this pool-size setting governs only the shared deadpool_redis::Pool's size and has no effect on the three dedicated pub/sub connections, which are each a single, unpooled redis::Client connection regardless of pool size."
    entry_class: FACT
    evidence:
      - ".env.example"
      - "crates/buzz-relay/src/config.rs"
  - statement: "docker-compose.yml runs local-development Redis as image redis:7-alpine, container name buzz-redis, published on 127.0.0.1:6379, with no volume mount — so local dev Redis state, including any in-flight pub/sub subscriptions, does not survive a container restart; this is a deployment-environment fact restated here only to the extent it bears on what a dedicated connection can and cannot rely on being persistent."
    entry_class: FACT
    evidence:
      - "docker-compose.yml"
  - statement: "launchpad/docs/corpus/architecture/containers/redis.md (id architecture-containers-redis, already merged on origin/launchpad) states in its own Ownership boundary section: \"PubSubManager's SUBSCRIBE/PSUBSCRIBE loops use their own dedicated (non-pooled) Redis connections rather than the shared pool, because a pooled connection cannot hold subscribe state; the pool is reserved for request-path commands\" — the same fact this node expands into required-vs-optional connection count, per-connection failure behavior, and consistency semantics, without restating that document's own container-level responsibility/interfaces/deployment sections."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/containers/redis.md"
  - statement: "Redis's own PUBLISH/SUBSCRIBE command semantics mean a message published while no client is subscribed to the matching channel is not queued or replayed to a client that subscribes later — delivery is at-most-once and only to currently-subscribed connections at the moment of PUBLISH; this crate's own code contains no buffering or replay mechanism for the gap between a dedicated connection's disconnect and its reconnect (checked: neither subscriber.rs, cache_invalidation.rs, nor conn_control.rs persists or replays messages missed during that window), so a message published to a topic while the corresponding dedicated connection is mid-reconnect is lost for that pod, backstopped only where a separate durable mechanism exists (the DB backstop cited above for cache-invalidation and conn-control) — no equivalent DB backstop was found for the channel/global event fan-out path (run_subscriber), so a cross-pod event delivered only via that Redis fan-out during another pod's reconnect window is not re-delivered by anything in this crate."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-pubsub/src/subscriber.rs"
      - "crates/buzz-pubsub/src/cache_invalidation.rs"
      - "crates/buzz-pubsub/src/conn_control.rs"
    confidence: 0.75
  - statement: "Issue #1093's Definition of Done requires this node to state whether the store is authoritative, derived, cache or transport; describe owned data, key access patterns, lifecycle/retention and consistency semantics; name tenancy/security boundaries and failure behavior; and link schema/migrations/code/tests rather than copying DDL."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1093 definition of done, opened directly via gh issue view"
  - statement: "The batch dispatch brief for issue #1093 states that layers/data/redis siblings channel-pubsub (#1091), connection-pool (#1092), and key-namespacing (#1094) do not exist on origin/launchpad yet and must not be linked as relationships, though this node's subject is likely tightly related to #1091 (channel-pubsub) in prose."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "corpus-batch-author batch dispatch brief for #1093, delivered directly in this task's instructions"
relationships:
  - type: part-of
    target: architecture-containers-redis
---

# Redis: dedicated pub/sub connection

## Purpose and scope

This node documents one specific mechanism inside Buzz's Redis usage: **why and how
Redis pub/sub subscriptions run over connections dedicated to that purpose, separate
from the shared `deadpool-redis` command pool**, and what that separation implies for
data ownership, lifecycle, consistency, and failure behavior. It is a `part-of` the
already-merged `architecture-containers-redis` node, which states the container-level
facts (Redis's overall responsibility, technology, five job categories, and one summary
sentence about dedicated connections) and defers this level of detail to a sibling.
This node zooms into that one summary sentence; it does not restate
`architecture-containers-redis`'s responsibility table, deployment section, or the other
four Redis job categories (presence, cache invalidation as a *concept*, connection
control as a *concept*, NIP-98 replay, rate limiting) except where they matter to the
connection mechanism itself.

**Not covered here, and named as neighbors rather than silently folded in:** the
Redis-wide key-naming convention across all of `buzz-pubsub`'s modules (likely
`layers/data/redis/key-namespacing`, #1094, not yet written); the pooled
`deadpool-redis` connection's own configuration and sizing (likely
`layers/data/redis/connection-pool`, #1092, not yet written); and the channel/topic
semantics of what gets published on the fan-out channel specifically (likely
`layers/data/redis/channel-pubsub`, #1091, not yet written, and probably the corpus node
most tightly related to this one in subject matter). None of the three exists on
`origin/launchpad` at this node's authoring time, so none is declared as a
`relationships` target — see *Scope and omissions*.

## Authoritative, derived, cache, or transport

**Transport — never authoritative, and not durable.** Every dedicated pub/sub
connection in `buzz-pubsub` carries live, in-flight messages only; nothing a dedicated
connection subscribes to persists a message anywhere. Postgres (`buzz-db`) remains the
system of record for every fact these channels carry: the channel-membership and
visibility state that `cache_invalidation` messages merely hint should be re-read, and
the ban row that `conn_control` messages merely hint should be enforced immediately, per
`architecture-containers-redis`'s own INFERENCE that every Redis write in this crate is
either TTL-bounded or a bare pub/sub `PUBLISH` with nothing stored. This node inherits
that classification rather than re-arguing it; the connection-specific consequence is
the point below (*Failure behavior*): if a dedicated connection is disconnected at the
moment of a `PUBLISH`, the message is gone, and the crate's own two-sided design
(cache-invalidation and conn-control's DB backstops) exists specifically because Redis
pub/sub here is transport, not a store.

## Technology and attachment profile

**Technology.** The `redis` crate (workspace-pinned `"1.0"`, features
`tokio-comp`, `connection-manager`, `tokio-rustls-comp`) and, for the pooled side only,
`deadpool-redis` (`"0.23"`, feature `rt_tokio_1`). A dedicated pub/sub connection is
constructed directly from `redis::Client::open(redis_url)` followed by
`.get_async_pubsub().await` — it is a plain `redis::aio::PubSub`/`MultiplexedConnection`
value, never acquired through `deadpool_redis::Pool::get()`. `PubSubManager` itself
holds only the pool and the `redis_url` string; the dedicated connections are opened
fresh, independently, inside each subscriber loop's own `connect_and_subscribe`
function, and are not stored as a `PubSubManager` field at all.

**How many, and for what.** Exactly **three** independent dedicated connections exist
per relay pod at steady state, one per long-running subscriber loop spawned in
`crates/buzz-relay/src/main.rs`:

| Loop | Dedicated-connection owner | Subscribes to |
|---|---|---|
| `run_subscriber` | `crates/buzz-pubsub/src/subscriber.rs` | Dynamic `SUBSCRIBE`/`UNSUBSCRIBE` of `buzz:{community}:channel:{uuid}` / `buzz:{community}:global`, driven by local desired-topic refcounts |
| `run_cache_invalidation_subscriber` | `crates/buzz-pubsub/src/cache_invalidation.rs` | One fixed `PSUBSCRIBE buzz:*:cache-invalidate`, issued once per connection lifetime |
| `run_conn_control_subscriber` | `crates/buzz-pubsub/src/conn_control.rs` | One fixed `PSUBSCRIBE buzz:*:conn-control`, issued once per connection lifetime |

The channel/global fan-out connection's subscription set changes at runtime (`SUBSCRIBE`
and `UNSUBSCRIBE` commands sent as local interest changes); the other two subscribe once
to a wildcard pattern for the connection's whole lifetime and never issue a second
`(p)subscribe`/`(p)unsubscribe` call. This is a real difference in shape between the
three connections, not merely three copies of the same loop.

**Why dedicated, not pooled.** `redis`'s pub/sub API puts a connection into a stateful
subscribe mode; a `deadpool-redis` pooled connection is designed to be checked out,
used for one command, and returned — it cannot hold open-ended subscribe state without
breaking the pool's own reuse contract. `crates/buzz-pubsub/src/lib.rs`'s own module
doc states this as a hard constraint ("Dedicated pub/sub connection is stateful and
cannot be shared. Pool connections handle all other commands."), and
`architecture-containers-redis` records the same reasoning at the container level.

## Owned data and key access patterns

**No data is owned by the connections themselves** — a dedicated connection holds no
state Redis persists; it holds only the local subscription set (which channels/patterns
it is currently listening on) and the in-process Rust structures it forwards messages
into. The *keys* the three connections listen on are:

- Channel/global fan-out: `buzz:{community}:channel:{uuid}` and `buzz:{community}:global`
  (`topic.rs`'s `channel_key`/`global_key`), community-scoped and exact-matched via
  `SUBSCRIBE`, one channel name per topic with local interest.
- Cache invalidation: the single wildcard pattern `buzz:*:cache-invalidate`, matched via
  `PSUBSCRIBE`, then narrowed back to one community by parsing the concrete channel name
  a received message arrived on (`parse_cache_invalidation_channel`).
- Connection control: the single wildcard pattern `buzz:*:conn-control`, matched via
  `PSUBSCRIBE`, narrowed the same way (`parse_conn_control_channel`).

**Local desired-topic map is the source of truth for the fan-out connection's
subscription set**, not Redis. `subscriber.rs`'s own module doc states this directly:
the `desired_topics` refcount map is authoritative, and "on every reconnect, this task
snapshots topics with count > 0 and subscribes to those exact Redis channels before
processing messages." Redis itself remembers nothing about which channels a dropped
connection was subscribed to — a fresh connection after reconnect starts with zero
subscriptions and is rebuilt entirely from the local map.

## Lifecycle and consistency semantics

**Connection lifetime is the process's own lifetime, by design.** Each of the three
`run_*_subscriber` methods is documented to "run forever" and to be spawned once as a
background `tokio::spawn` task at relay startup (`crates/buzz-relay/src/main.rs`); none
returns except on an unrecoverable local error.

**`run_subscriber` is runtime-guarded against double-start; the other two are not.**
`PubSubManager::run_subscriber` takes its shared `mpsc::Receiver` out of a
`Mutex<Option<...>>` with `.take()` and logs an error and returns immediately if it has
already been taken — so calling it twice on the same `PubSubManager` instance is a
no-op after the first call, not a second dedicated connection. `run_cache_invalidation_subscriber`
and `run_conn_control_subscriber` take no such shared receiver and carry no equivalent
guard in the code inspected for this node; nothing in `buzz-relay`'s `main.rs` spawns
either of them more than once, so this is a latent gap rather than an observed failure,
named here rather than silently assumed safe.

**Reconnect is exponential backoff, shared shape across all three.** `BACKOFF_INITIAL_SECS
= 1`, `BACKOFF_MAX_SECS = 30`, doubling on each failed attempt, reset to the initial
value after a *clean* disconnect (the Redis stream ending with `None`, not an error).
All three loops share this exact backoff shape — `cache_invalidation.rs` and
`conn_control.rs`'s own doc comments state they "mirror" `subscriber.rs`'s reconnect
loop.

**Consistency after reconnect is eventual, bounded by the backoff window, and
per-connection independent.** Because each of the three dedicated connections
reconnects on its own schedule, a relay pod can be mid-reconnect on one loop (say,
conn-control) while the other two remain connected — there is no cross-loop
coordination or shared reconnect state. Once the fan-out connection reconnects, its
subscription set is rebuilt exactly from the current `desired_topics` snapshot (see
above), so it converges to the *current* desired state, not necessarily the state at
the moment of disconnect — a topic released while the connection was down is correctly
not re-subscribed.

## Tenancy, security boundaries, and failure behavior

**Tenancy boundary: naming convention only, not connection-level isolation.** All three
dedicated connections are single, un-tenant-scoped Redis client connections shared
across every community a relay pod serves; the `buzz:{community}:...` prefix on every
channel name is the sole mechanism keeping one community's messages from being acted on
under another community's context, enforced by the parsing step
(`parse_cache_invalidation_channel` / `parse_conn_control_channel` / the fan-out path's
own channel-key parsing) each connection performs on every received message, not by
Redis itself. `architecture-containers-redis` already states this fan-out channel is
explicitly *not* a confidentiality boundary — the actual author-only delivery
enforcement is `filter_fanout_by_access` in `buzz-relay`, applied uniformly regardless
of which dedicated connection carried the message.

**Failure behavior differs by loop, not uniformly:**

- **Redis-level disconnect** (any of the three): the owning loop's `connect_and_subscribe`
  returns `Err`/`Ok(())` on stream end, the outer loop logs, sleeps for the current
  backoff, doubles it (capped at 30s), and retries — indefinitely, with no limit on
  total attempts found in the code inspected.
- **A message published while the relevant dedicated connection is disconnected or
  reconnecting is lost for that pod.** Redis `PUBLISH`/`SUBSCRIBE` delivers only to
  currently-subscribed connections at publish time; nothing in `buzz-pubsub` buffers or
  replays a missed message once the connection comes back (checked directly in
  `subscriber.rs`, `cache_invalidation.rs`, and `conn_control.rs` — see the INFERENCE
  entry in the evidence ledger). Whether that loss matters depends on the loop:
  - **Cache invalidation and conn-control publishes are explicitly fire-and-forget with
    a durable Postgres backstop**, per their own doc comments in `lib.rs`: a dropped
    cache-invalidation publish is backstopped by the REQ denial path's DB confirmation
    (the next read re-fetches authoritative state), and a dropped conn-control publish
    is backstopped by the durable ban row (the banned pubkey's next auth attempt is
    still refused). Losing the live push during a reconnect window degrades latency of
    enforcement on that one pod, not correctness.
  - **No equivalent DB backstop was found for the channel/global event fan-out path**
    (`run_subscriber`). A cross-pod realtime event delivered to a given pod only via
    Redis fan-out, during that pod's reconnect window, is not re-delivered by anything
    in this crate. This is a real, named gap rather than a resolved question — see
    *Scope and omissions*.
- **Local backpressure is a separate failure mode from a Redis-level disconnect.**
  Each loop forwards received messages into a local `tokio::sync::broadcast` channel
  (`broadcast::channel(4096)` per channel, three separate senders held on
  `PubSubManager`). A local receiver that falls behind the 4096-message buffer
  produces `PubSubError::BroadcastLagged`, a distinct error variant from
  `PubSubError::Redis` — a dedicated connection's own reconnect loop does nothing to
  address this, since the connection to Redis may be perfectly healthy while a local
  consumer lags.

## Links to code and tests, not copied DDL

Redis has no schema or migration mechanism to link in place of DDL; the closest
equivalent is the module boundary and the tests that exercise it directly, linked here
rather than restated:

- **Connection construction and reconnect loops:** `crates/buzz-pubsub/src/subscriber.rs`
  (`connect_and_subscribe`, `run_subscriber`), `crates/buzz-pubsub/src/cache_invalidation.rs`,
  `crates/buzz-pubsub/src/conn_control.rs`.
- **Where the three loops are spawned, and where the shared pool is built:**
  `crates/buzz-relay/src/main.rs`.
- **Pool-size configuration (governs the pooled side only, not the dedicated
  connections):** `crates/buzz-relay/src/config.rs`, `.env.example` (`BUZZ_REDIS_POOL_SIZE`,
  default 16).
- **Local dev provisioning:** `docker-compose.yml` (`redis:7-alpine`, no persistence
  volume).
- **Tests exercising the dedicated-connection subscriber loops against a real Redis
  instance:** `crates/buzz-pubsub/src/lib.rs`'s `#[ignore = "requires Redis"]` tests
  `test_publish_and_subscribe_roundtrip`, `test_cache_invalidation_roundtrip`, and
  `same_channel_id_in_two_communities_release_one_keeps_other_live` (the last of which
  specifically exercises the fan-out connection's reconnect/refcount interaction across
  two tenants sharing one channel id).
- **Tests exercising the local refcount/debounce logic without Redis:**
  `crates/buzz-pubsub/src/lib.rs`'s `retain_release_refcounts_and_debounces_last_release`
  and `config_defaults_debounce_but_allows_override`, and `crates/buzz-pubsub/src/subscriber.rs`'s
  `desired_refcount_returns_zero_for_absent_topic` / `desired_refcount_reads_present_topic`.

## Relationships

Declared: **`part-of`** → `architecture-containers-redis`, the already-merged
container-level node whose own "Ownership boundary" section states the summary fact
this node expands. This is the correct direction and type per
`relationships.schema.json`'s own directionality ("source is a constituent
section/child of target"): this node is a deeper, connection-level slice of the
container `architecture-containers-redis` already inventories at container depth, the
same relationship a `datastore`-shaped node would declare toward its own container
node per `templates/datastore.md`'s own relationships guidance.

**No relationship declared toward channel-pubsub (#1091), connection-pool (#1092), or
key-namespacing (#1094).** None of the three exists on `origin/launchpad` at this
node's authoring time (checked directly with `git ls-tree -r --name-only
origin/launchpad -- launchpad/docs/corpus`), and a `relationships[].target` naming an
id nothing carries is a hard validation error per `AGENTS.md`'s own rule. Of the three,
channel-pubsub (#1091) is named in prose above as the most likely future
`references`-type neighbor, since it would document what gets published on the same
fan-out channel this node's `run_subscriber` connection subscribes to — but that edge
is for #1091's own author to declare once merged, not for this node to assert in
advance.

## Scope and omissions

**This node covers** why Redis pub/sub in Buzz runs over connections dedicated to that
purpose rather than the shared command pool; how many dedicated connections exist per
relay pod and what each one subscribes to; the authoritative/derived/cache/transport
classification (transport, non-durable); lifecycle and reconnect behavior, including the
double-start guard gap on two of the three loops; consistency semantics across a
reconnect (local refcount map as source of truth, no Redis-side subscription memory);
tenancy boundaries (naming convention, not connection isolation); and failure behavior,
including the one real, unbackstopped gap on the channel/global fan-out path during a
reconnect window.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Redis's overall responsibility, technology choice, and container-level deployment/security implications | `architecture-containers-redis` (already merged) |
| The pooled `deadpool-redis` connection's own configuration, sizing, and request-path command set | `layers/data/redis/connection-pool` (#1092), not yet written |
| The Redis key-naming convention across all of `buzz-pubsub`'s modules, beyond the three key patterns named here | `layers/data/redis/key-namespacing` (#1094), not yet written |
| What is actually published on the channel/global fan-out channel — event shape, delivery classification | `layers/data/redis/channel-pubsub` (#1091), not yet written; the node most likely to declare a `references` edge back to this one |
| Presence, NIP-98 replay, and rate-limiting — the other Redis-backed mechanisms in `buzz-pubsub` that do not use a dedicated pub/sub connection | `architecture-containers-redis`'s existing responsibility table; not re-covered here since none of the three uses a dedicated connection |
| Operational tuning (ElastiCache sizing, eviction policy, TLS termination in staging/production) | `architecture-containers-redis`'s own named gap; not re-investigated here |

**Expected but not verified when this node was written:**

- **Whether the missing double-start guard on `run_cache_invalidation_subscriber` and
  `run_conn_control_subscriber` (versus `run_subscriber`'s `Mutex<Option<...>>` guard)
  is a deliberate asymmetry or an oversight.** No comment in either module explains the
  difference, and no call site in the repository at the recorded revision spawns either
  loop more than once, so this is a latent gap rather than an observed failure. Named
  here as a real asymmetry, not resolved.
  - **Not left unresolved further than that.** The most direct question this node could
    settle — does the code actually enforce single-start on all three loops, or only
    one — was checked directly against the three modules' source rather than assumed
    from the container-level document's summary prose; the asymmetry is confirmed, not
    inferred.
- **Whether the channel/global fan-out path's reconnect-window message loss is
  considered acceptable by design, or is an unaddressed gap.** No comment, test, or
  linked issue in the repository at the recorded revision states either way. This node
  reports the gap as found (see *Failure behavior*) rather than guessing at intent.
- **Whether `redis`'s `connection-manager` feature (enabled in the workspace `Cargo.toml`
  for the `redis` crate generally) is actually in use on the pub/sub path specifically,
  as opposed to only on the pooled/command path.** The three `connect_and_subscribe`
  functions call `redis::Client::open(...).get_async_pubsub()` directly, which was
  confirmed by reading the source; whether `get_async_pubsub()` internally uses the
  `connection-manager` feature's reconnect logic, in addition to this crate's own
  outer backoff loop, was not traced into the `redis` crate's own implementation.
