---
id: implementation-crates-buzz-pubsub
type: implementation
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 76a0a4ebbe4bc4d852b0d04362ed768620da34b3 on the launchpad branch."
    entry_class: FACT
    evidence:
      - "commit 76a0a4ebbe4bc4d852b0d04362ed768620da34b3"
  - statement: "buzz-pubsub's Cargo.toml describes it as \"Redis pub/sub fan-out, presence, and typing indicators for Buzz\" and its src/ tree has exactly ten files: lib.rs, topic.rs, publisher.rs, subscriber.rs, presence.rs, cache_invalidation.rs, conn_control.rs, nip98_replay.rs, rate_limiter.rs, error.rs."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/Cargo.toml"
      - "crates/buzz-pubsub/src/lib.rs"
  - statement: "PubSubManager is the crate's central façade: it holds a deadpool_redis::Pool, the redis_url used to open dedicated (non-pooled) pub/sub connections, an unsubscribe_debounce Duration, a desired_topics refcount map, an mpsc channel to the subscriber task, and three tokio broadcast::Sender fields (one each for channel events, cache invalidations, conn-control commands); PubSubManager::new/with_config construct it without opening any Redis connection themselves."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/lib.rs"
  - statement: "retain_topic/release_topic implement a local desired-refcount mechanism, not a direct SUBSCRIBE/UNSUBSCRIBE call: the first retain_topic for a topic (count goes 0 -> 1) sends SubscriptionCommand::Subscribe to the subscriber task; the retain that brings a topic back to zero spawns a tokio task that sleeps for unsubscribe_debounce (default 500ms) before sending SubscriptionCommand::UnsubscribeIfIdle, so a retain arriving during that window makes the pending unsubscribe a no-op because the subscriber task re-checks the live refcount before acting."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/lib.rs"
  - statement: "subscriber.rs's run_subscriber/connect_and_subscribe treats the desired_topics map, not the Redis connection, as the source of truth: on every (re)connect it snapshots every topic with a refcount > 0 and issues SUBSCRIBE for exactly that set before entering its tokio::select! loop, which then applies incoming SubscriptionCommand::Subscribe/UnsubscribeIfIdle values and forwards inbound pub/sub messages -- parsed back into an EventTopicKey via EventTopicKey::parse_redis_channel -- onto the broadcast channel; reconnection uses exponential backoff from BACKOFF_INITIAL_SECS=1 to BACKOFF_MAX_SECS=30, doubling each attempt and resetting to 1s only after a connection that ran successfully before ending."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/subscriber.rs"
  - statement: "topic.rs's EventTopicKey::parse_redis_channel is a strict inverse of redis_channel(): it rejects a wrong prefix, a non-UUID community segment, an unrecognized scope, a channel topic missing its UUID, and any trailing extra colon-delimited segment on either a global or channel key -- verified directly by its own rejects_malformed_or_wrong_prefix_topics test table."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/topic.rs"
  - statement: "PubSubError has six variants (Redis, Pool, Serialization, BroadcastLagged, SubscriberStopped, InvalidChannelKey) plus a hand-written From<tokio::sync::broadcast::error::RecvError> that maps RecvError::Lagged(n) to BroadcastLagged(n) and RecvError::Closed to SubscriberStopped, distinct from the #[from] derives used for the other three wrapped error types."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/error.rs"
  - statement: "presence.rs's get_presence_bulk returns Ok(HashMap::new()) immediately for an empty pubkeys slice without a Redis round trip, but a real connection failure (tested by pointing the pool at a closed port) still surfaces as Err rather than a false empty map -- the crate's own test comment states this matters because a caller relies on it to return an error response instead of a fake \"all offline\" snapshot on a Redis outage."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/presence.rs"
  - statement: "cache_invalidation.rs's CacheInvalidation enum (Membership, AccessibleAll, Visibility, ChannelDeleted, serde-tagged by \"op\") is published on buzz:{community}:cache-invalidate and consumed via a PSUBSCRIBE on buzz:*:cache-invalidate; run_cache_invalidation_subscriber's reconnect loop is a separate, structurally identical copy of subscriber.rs's exponential-backoff loop, not a shared implementation."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/cache_invalidation.rs"
  - statement: "conn_control.rs's ConnControl enum (DisconnectCommunity, DisconnectPubkey{pubkey,event_id,reason}) is published on buzz:{community}:conn-control and consumed via PSUBSCRIBE on buzz:*:conn-control; its own module doc comment states this is deliberately a separate channel/module from cache_invalidation because a disconnect is an imperative, non-idempotent action on a live socket, whereas a cache-key drop is a pure idempotent hint, and folding the two together would break cache_invalidation's own stated invariant."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/conn_control.rs"
  - statement: "RedisNip98ReplayGuard::try_mark_in_scope clamps the caller-supplied ttl_secs into [DEFAULT_REPLAY_TTL_SECS, MAX_REPLAY_TTL_SECS] (both imported from buzz_auth::nip98_replay) before issuing SET <key> 1 NX EX <ttl>; a typed Option<String> reply of Some(\"OK\") becomes Ok(true) (first claim), None becomes Ok(false) (replay), and any other reply is treated as an internal error and logged at error level rather than silently accepted."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/nip98_replay.rs"
  - statement: "RedisRateLimiter::check_and_increment/check_ip_connection both call a shared run_rate_limit helper that executes one Lua script combining INCR and a first-call-only EXPIRE atomically; if the script's returned TTL is negative (a key surviving from a prior crash between INCR and EXPIRE), the helper repairs it with a fresh EXPIRE and resets the reported window rather than leaving the key permanently unbounded. check_and_increment keys are community-scoped via buzz_auth::rate_limit::rate_limit_key(ctx, pubkey, limit_type); check_ip_connection keys via ip_rate_limit_key(ip) are explicitly operator-global, not tenant-scoped."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/rate_limiter.rs"
  - statement: "publisher.rs's publish_event is a thin PUBLISH wrapper that PubSubManager::publish_event delegates to directly; by contrast PubSubManager::publish_cache_invalidation and PubSubManager::publish_conn_control build their PUBLISH command and JSON payload inline inside lib.rs rather than through a dedicated per-module publish function -- the crate has one delegation pattern for channel events and a different, inline one for the other two publish paths."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/publisher.rs"
      - "crates/buzz-pubsub/src/lib.rs"
  - statement: "buzz-relay's main() builds the single shared deadpool_redis::Pool from config.redis_url with pool size config.redis_pool_size, constructs PubSubManager::new(&config.redis_url, redis_pool) from it, and spawns run_subscriber, run_cache_invalidation_subscriber, and run_conn_control_subscriber each as their own tokio::spawn background task."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs"
  - statement: "buzz-relay's AppState carries pubsub: Arc<PubSubManager>, nip98_replay: Arc<dyn Nip98ReplayGuard> (constructed as Arc::new(RedisNip98ReplayGuard::new(redis_pool.clone()))), admission_rate_limiter: Arc<RedisRateLimiter>, and redis_pool: deadpool_redis::Pool as four separate fields -- the trait-object fields are consumed through buzz-auth's trait interfaces, not through PubSubManager."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/state.rs"
  - statement: "retain_topic/release_topic are called from five distinct buzz-relay sites: handlers/req.rs retains a channel or global topic when a client REQuests a live subscription; connection.rs and handlers/close.rs release topics on disconnect/CLOSE; handlers/side_effects.rs releases a channel topic as part of a side-effect cleanup; handlers/event.rs retains the Global topic for the reminder-scheduler path -- confirmed by grep across crates/buzz-relay/src/ rather than by relying on lib.rs's own doc comments about how the manager is meant to be used."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs"
      - "crates/buzz-relay/src/connection.rs"
      - "crates/buzz-relay/src/handlers/close.rs"
      - "crates/buzz-relay/src/handlers/side_effects.rs"
      - "crates/buzz-relay/src/handlers/event.rs"
  - statement: "cargo test -p buzz-pubsub --lib, run under the repository's Hermit toolchain at commit 76a0a4ebbe4bc4d852b0d04362ed768620da34b3, reported 25 passed, 0 failed, 11 ignored (each ignored test is individually marked #[ignore = \"requires Redis\"]), finished in 1.01s."
    entry_class: FACT
    evidence:
      - "cargo_test(crate='buzz-pubsub', args='--lib') -> 25 passed; 0 failed; 11 ignored; 0 measured; 0 filtered out; finished in 1.01s"
      - "commit 76a0a4ebbe4bc4d852b0d04362ed768620da34b3"
  - statement: "lib.rs carries a doc comment reading \"Typing indicator tracking in Redis.\" directly above the line `pub use error::PubSubError;`, not above any `pub mod` declaration, and no typing module, file, or Redis key pattern exists anywhere among the crate's ten src/ files -- despite both this doc comment and Cargo.toml's description field naming typing indicators as part of the crate's scope."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/lib.rs"
      - "crates/buzz-pubsub/Cargo.toml"
  - statement: "conn_control.rs's module doc comment contains the intra-doc link `[crate::ConnectionManager]`, written as though ConnectionManager is a local item, but no struct or type named ConnectionManager is defined anywhere under crates/buzz-pubsub/src/; a struct of that exact name is instead defined in crates/buzz-relay/src/state.rs, a different crate."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/conn_control.rs"
      - "crates/buzz-relay/src/state.rs"
  - statement: "nip98_replay.rs imports Nip98ReplayGuard, DEFAULT_REPLAY_TTL_SECS, MAX_REPLAY_TTL_SECS and nip98_replay_key_for_scope from buzz_auth::nip98_replay, and rate_limiter.rs imports RateLimiter, LimitType and RateLimitResult from buzz_auth::rate_limit -- the two trait contracts RedisNip98ReplayGuard and RedisRateLimiter concretely implement live in the buzz-auth crate, which has no corpus node at the time this node was written."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/nip98_replay.rs"
      - "crates/buzz-pubsub/src/rate_limiter.rs"
  - statement: "Issue #933's Definition of Done requires that this node state implementation responsibility and what it deliberately does not own, name public interfaces/entry points and important dependencies, link owned source paths and representative tests, and avoid restating domain semantics already canonical in capability/layer/interface nodes -- the category tail specific to implementation/crates nodes, distinct from the generic corpus-wide DoD bullets that precede it in the issue body."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#933 definition of done, category tail for implementation/crates"
relationships:
  - type: references
    target: architecture-containers-redis
  - type: references
    target: architecture-flows-live-fanout
---

# buzz-pubsub: implementation reference

`buzz-pubsub` is the workspace crate that owns every Redis access pattern in Buzz:
cross-pod event fan-out, presence, cross-pod cache invalidation, cross-pod connection
control (live ban enforcement), and the Redis-backed implementations of `buzz-auth`'s
`RateLimiter` and `Nip98ReplayGuard` trait contracts. `architecture-containers-redis`
already documents this at the architecture-container grain -- what Redis is for, which
job belongs to which module, and the deployment/data/security implications. This node
goes one layer deeper: the concrete types, functions, and the one non-obvious mechanism
(the refcounted, debounced dynamic subscription system in `lib.rs`/`subscriber.rs`) that
`architecture-containers-redis` does not itself narrate, plus two code-level divergences
between the crate's own documentation and what its code actually contains.

## Target

Two distinct things are realized here, and neither is a formal NIP or ADR:

1. **`architecture-containers-redis`** (this corpus's existing architecture-container
   node) states a five-job responsibility table for Redis in Buzz and attributes each
   job to a `buzz-pubsub` module. This node is the deeper, symbol-level companion to
   that table -- it does not restate the table's prose, and where the same underlying
   fact is needed here (e.g. a Redis key format), it is re-verified against the crate's
   own source rather than cited from that other corpus node.
2. **`buzz-auth`'s `RateLimiter` and `Nip98ReplayGuard` traits** (`crates/buzz-auth/src/rate_limit.rs`,
   `crates/buzz-auth/src/nip98_replay.rs`) are the two literal Rust contracts
   `RedisRateLimiter` and `RedisNip98ReplayGuard` implement. `buzz-auth` has no corpus
   node at the time this node was written, so per `AGENTS.md`'s rule against edges to
   nonexistent ids, no `implements` relationship is declared toward either trait --
   they are named here by file path instead, and the edge is the natural thing to add
   once a `buzz-auth` (or per-trait) corpus node exists.

## Implementation surface

| Component / file / symbol | Realizes | Note |
|---|---|---|
| `lib.rs` -- `PubSubManager` (`new`/`with_config`), `PubSubConfig`, `ChannelEvent` | Central façade over all six Redis-touching modules; owns the refcounted `retain_topic`/`release_topic` subscription mechanism | Delegates channel-event `PUBLISH` to `publisher::publish_event`; builds cache-invalidation and conn-control `PUBLISH` calls inline instead |
| `topic.rs` -- `EventTopic`, `EventTopicKey`, `BUZZ_PREFIX`, `channel_key`/`global_key` | Redis key/channel naming for event fan-out: `buzz:{community}:channel:{uuid}` / `buzz:{community}:global` | `parse_redis_channel` is the strict inverse `subscriber.rs` uses to route inbound pub/sub payloads back to a topic |
| `publisher.rs` -- `publish_event` | The `PUBLISH` call for channel/global event fan-out | Thin wrapper around a pool connection; the one module-level publish function the crate actually uses via delegation |
| `subscriber.rs` -- `run_subscriber`, `connect_and_subscribe`, `DesiredTopics`, `SubscriptionCommand` | The dynamic scoped `SUBSCRIBE` loop: reconnects with exponential backoff (1s -> 30s), and on every (re)connect resubscribes to exactly the topics with a live local refcount | `desired_topics`, not the Redis connection, is the source of truth across reconnects |
| `presence.rs` -- `set_presence`/`get_presence`/`clear_presence`/`get_presence_bulk`, `PRESENCE_TTL_SECS` | Presence job: `SET ... EX 180`, `GET`, `DEL`, `MGET` | `get_presence_bulk` short-circuits an empty input to `Ok({})` but still surfaces a real Redis connection failure as `Err` |
| `cache_invalidation.rs` -- `CacheInvalidation`, `run_cache_invalidation_subscriber` | Cross-pod cache-key drops on `buzz:{community}:cache-invalidate`, consumed via `PSUBSCRIBE buzz:*:cache-invalidate` | Reconnect loop structurally duplicates `subscriber.rs`'s backoff logic rather than sharing it |
| `conn_control.rs` -- `ConnControl`, `run_conn_control_subscriber` | Cross-pod connection control on `buzz:{community}:conn-control`, consumed via `PSUBSCRIBE buzz:*:conn-control` | Deliberately kept separate from `cache_invalidation`: imperative/non-idempotent vs. a pure idempotent hint, per its own module doc |
| `nip98_replay.rs` -- `RedisNip98ReplayGuard` | Implements `buzz_auth::nip98_replay::Nip98ReplayGuard` via `SET key 1 NX EX <ttl>` | Clamps caller TTL into `[DEFAULT_REPLAY_TTL_SECS, MAX_REPLAY_TTL_SECS]`, both owned by `buzz-auth` |
| `rate_limiter.rs` -- `RedisRateLimiter` | Implements `buzz_auth::rate_limit::RateLimiter` via an atomic `INCR`+`EXPIRE` Lua script | The crate's one Redis write path that self-repairs a key found without a TTL |
| `error.rs` -- `PubSubError` | Crate-wide error type: `Redis`, `Pool`, `Serialization`, `BroadcastLagged`, `SubscriberStopped`, `InvalidChannelKey` | Hand-written `From<broadcast::error::RecvError>` maps `Lagged`/`Closed` distinctly from the `#[from]`-derived variants |

**Public interface / entry points.** Construction: `PubSubManager::new`/`with_config`.
Background tasks (each spawned once by `buzz-relay`, run forever): `run_subscriber`,
`run_cache_invalidation_subscriber`, `run_conn_control_subscriber`. Request-path API:
`retain_topic`/`release_topic`, `publish_event`, `publish_cache_invalidation`,
`publish_conn_control`, `set_presence`/`get_presence`/`clear_presence`/`get_presence_bulk`,
`subscribe_local`/`subscribe_cache_invalidations`/`subscribe_conn_control`. Two
free-standing trait implementations consumed via `buzz-auth`'s trait objects rather than
through `PubSubManager`: `RedisNip98ReplayGuard`, `RedisRateLimiter`.

**Important dependencies** (`Cargo.toml`): `redis` and `deadpool-redis` for the Redis
client and connection pool; `buzz-core` for `TenantContext`/`CommunityId`; `buzz-auth`
for the `RateLimiter`/`Nip98ReplayGuard` trait contracts this crate implements; `tokio`
for the broadcast/mpsc channels and the background reconnect loops; `nostr` for the
`Event`/`PublicKey` types carried over the wire; `serde`/`serde_json` for the
`CacheInvalidation`/`ConnControl` wire payloads; `thiserror` for `PubSubError`.

## Divergences

Two were found; the crate's other four claimed jobs (fan-out, presence,
cache-invalidation, conn-control) were checked against `architecture-containers-redis`'s
table and match what the code does, so this section is not empty by omission -- these
two are genuinely the only mismatches found between the crate's own documentation and
its code at the recorded revision:

1. **Typing indicators are documented but not implemented.** Both `Cargo.toml`'s
   `description` field and a stray doc comment in `lib.rs` ("Typing indicator tracking
   in Redis.", sitting directly above `pub use error::PubSubError;` rather than above
   any `pub mod` line) name typing indicators as part of this crate's scope. No
   `typing` module, file, or Redis key pattern exists anywhere in the crate's ten
   `src/` files. This is the same finding `architecture-containers-redis` already
   records; it is re-verified here independently rather than cited from that node.
2. **A broken intra-doc link to a type this crate does not own.** `conn_control.rs`'s
   module doc comment writes `[crate::ConnectionManager]`, which resolves (if at all)
   relative to `buzz-pubsub` itself -- but no `ConnectionManager` type exists anywhere
   under `crates/buzz-pubsub/src/`. A struct of that exact name is defined in
   `crates/buzz-relay/src/state.rs`, a different crate. Whether `cargo doc` actually
   emits a broken-link warning for this was not checked (see *Scope and omissions*);
   only that the referenced item does not exist in this crate is established.

## Verification

`cargo test -p buzz-pubsub --lib`, run under the repository's Hermit toolchain at the
recorded revision, passed cleanly: 25 passed, 0 failed, 11 ignored. Every ignored test
carries an explicit `#[ignore = "requires Redis"]` attribute rather than being silently
skipped, and covers exactly the behavior a mocked/local test cannot reach: real
publish/subscribe round trips, presence TTL against a live key, and NIP-98
first-claim/replay/clamping behavior against real `SET NX EX` semantics. `TESTING.md`
states `just test` runs the full integration suite (including these) against a real
Postgres and Redis; that claim was not independently re-executed as part of this node
(no local Redis instance was started in this corpus-authoring session). Beyond the
crate's own tests, `buzz-pubsub` has no dedicated CI job of its own -- it is covered by
the workspace-wide `just ci` (clippy, fmt, and `cargo test` across the workspace) like
every other crate, not by anything specific to pub/sub behavior.

## Relationships

- **references**: `architecture-containers-redis` -- the architecture-container node
  this implementation reference goes one layer deeper than. Cited as supporting
  context; this node does not restate that node's job table, deployment implications,
  or security-boundary discussion, and defers to it for all of that.
- **references**: `architecture-flows-live-fanout` -- documents the wider dispatch
  pipeline (`dispatch_persistent_event` -> `buzz_pubsub::publish_event`) that this
  crate's `publish_event` and `subscribe_local` sit inside; cited as supporting context
  for where this crate's API is actually called from.
- No `implements` edge is declared. The two contracts this crate's code most literally
  realizes -- `buzz_auth::rate_limit::RateLimiter` and
  `buzz_auth::nip98_replay::Nip98ReplayGuard` -- have no corpus node id at the time
  this node was written; per `AGENTS.md`, an edge to a nonexistent id is a hard
  validation error, so they are named by path in *Target* instead. This is the moment
  to add the edge, once a `buzz-auth` (or per-trait) corpus node exists.
- No `part-of` edge is declared. This is the first `implementation/` node in the
  corpus; there is no broader implementation-reference node for it to be a
  sub-component of.

## Scope and omissions

**This node covers** `buzz-pubsub`'s concrete implementation surface -- its types,
functions, the dynamic refcounted subscription mechanism, its five real Redis-backed
jobs, its public entry points and important dependencies, its representative tests, and
two code-level divergences between the crate's documentation and its actual contents.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The architecture-level responsibility/ownership narrative, deployment topology, and data/security implications of Redis in Buzz | `architecture-containers-redis` |
| `buzz-relay`'s own internals beyond the specific call sites that establish how this crate's API is used | No implementation-reference node exists yet for `buzz-relay` itself |
| The `RateLimiter`/`Nip98ReplayGuard` trait definitions themselves (as opposed to their Redis-backed implementations documented here) | `buzz-auth`, which has no corpus node yet |
| Whether typing-indicator delivery is implemented anywhere else in the system (e.g. local-only fan-out inside `buzz-relay`) or not at all | Unresolved; `architecture-containers-redis` leaves this the same way |
| Fixing either divergence found above (the typing-indicator claim or the `ConnectionManager` doc link) | Out of scope for a docs-only corpus task with no linked implementation issue authorizing a source change |
| Operational Redis tuning, ElastiCache sizing, and deployment provisioning | `architecture-containers-redis` |

**Expected but not verified when this node was written:**

- **Whether the 11 `#[ignore = "requires Redis"]` tests actually pass against a live
  Redis instance.** Not run in this session -- no local Redis instance was started.
  `TESTING.md`'s claim that `just test` exercises them was read, not re-executed here.
- **Whether `cargo doc` emits a warning for the broken `[crate::ConnectionManager]`
  intra-doc link** named in *Divergences*. Not run; only that the referenced type does
  not exist in this crate was established, by inspection and by grep across the
  crate's `src/` tree.
