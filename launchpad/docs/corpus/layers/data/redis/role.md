---
id: layers-data-redis-role
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
  - statement: "Every layers/data/... node in this Feature (#610) uses type: layers, not type: architecture, even though templates/datastore.md's own worked example directs a real datastore instance node to type: architecture. This is a deliberate, disclosed override: node.schema.json's type enum offers no finer-grained member than layers for 'the corpus surface this node documents' when that surface is a data-layer synthesis document (as opposed to a structural C4-style container inventory row, which architecture-containers-redis already is), and standards/taxonomy.md's own guidance is to disclose an imperfect-or-overridden fit in the node's own scope-and-omissions section rather than silently pick."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "corpus-batch-author overnight batch dispatch brief for Feature #610, precedent set by launchpad-26/buzz#1073 (layers/data/object-storage/role.md) and #1087 (layers/data/postgres/role.md), both unmerged at the recorded revision"
  - statement: "architecture-containers-redis (merged, status: draft) already documents Redis's container-level existence, technology, ownership boundary, and one-line interfaces/connected-containers table; this node is a datastore-level zoom into that container's own internal shape, per templates/datastore.md's stated boundary between the two."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/containers/redis.md"
      - "launchpad/docs/corpus/templates/datastore.md"
  - statement: "crates/buzz-pubsub/src/lib.rs's own module doc comment describes the crate's architecture as a shared deadpool-redis pool used for PUBLISH/SET/ZADD-style commands, plus a separate dedicated (non-pooled) redis::aio::PubSub connection for SUBSCRIBE, because pooled connections cannot hold subscribe state; this matches architecture-containers-redis's own claim but was independently re-read at this session's recorded revision rather than copied."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/lib.rs"
  - statement: "crates/buzz-relay/src/main.rs builds the one shared redis_pool via deadpool_redis::Config::from_url(&config.redis_url) with cfg.pool = Some(deadpool_redis::PoolConfig::new(config.redis_pool_size)), then constructs PubSubManager::new(&config.redis_url, redis_pool) from it; .env.example documents REDIS_URL (default redis://localhost:6379) and the optional BUZZ_REDIS_POOL_SIZE (default 16) as the two variables shaping this attachment point, matching Factor IV's config-addressed-resource framing (a URL plus a pool-size setting, not a hardcoded dependency)."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs"
      - ".env.example"
  - statement: "A source comment in buzz-relay's main() states the ring rustls CryptoProvider is installed before any rustls TLS connection, explicitly naming rediss:// to ElastiCache as one such connection alongside wss:// and S3-over-TLS -- i.e. the same attachment point (a URL) resolves to a plaintext redis:// in local dev and a TLS rediss:// in staging/production, without any code change, per Factor IV's own claim that a config change alone should suffice to move an attached resource."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs"
  - statement: "Six distinct Redis key/channel families exist in the codebase at the recorded revision, each owned by exactly one crates/buzz-pubsub/src module: buzz:{community}:channel:{uuid} and buzz:{community}:global (pub/sub, topic.rs/publisher.rs/subscriber.rs), buzz:{community}:presence:{pubkey_hex} (presence.rs), buzz:{community}:cache-invalidate (cache_invalidation.rs), buzz:{community}:conn-control (conn_control.rs), buzz:{community}:nip98:{event_id_hex} (nip98_replay.rs), and buzz:{community}:ratelimit:{pubkey_hex}:{suffix} plus the operator-global buzz:ratelimit:ip:{ip}:conn (rate_limiter.rs). All are built with format!() string interpolation of a shared BUZZ_PREFIX constant, not through any schema-definition file."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/topic.rs"
      - "crates/buzz-pubsub/src/presence.rs"
      - "crates/buzz-pubsub/src/cache_invalidation.rs"
      - "crates/buzz-pubsub/src/conn_control.rs"
      - "crates/buzz-pubsub/src/nip98_replay.rs"
      - "crates/buzz-pubsub/src/rate_limiter.rs"
  - statement: "No migration or schema-versioning mechanism exists for any Redis key/channel family: unlike crates/buzz-db/src/runtime/migration.rs's embedded sqlx::migrate!(\"../../migrations\") MIGRATOR (numbered SQL files applied in order, guarded by an exclusive session lock), a Redis key format is a plain Rust string constant/format! call inside its owning module, changed by an ordinary code edit and a crate version bump -- there is no ordering guard, no lock, and no migrations/ directory analogue for Redis in this repository."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/runtime/migration.rs"
      - "crates/buzz-pubsub/src/topic.rs"
      - "crates/buzz-pubsub/src/presence.rs"
  - statement: "buzz-pubsub owns every Redis access pattern in the repository; nothing outside that crate issues a Redis command directly, and buzz-auth (which defines the RateLimiter and Nip98ReplayGuard traits buzz-pubsub's Redis-backed types implement) has zero Redis dependency of its own, keeping the auth contract testable against an always-allow stub without Redis running."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/Cargo.toml"
      - "crates/buzz-auth/src/rate_limit.rs"
      - "crates/buzz-relay/src/state.rs"
  - statement: "buzz-relay spawns three independent, long-running Redis SUBSCRIBE/PSUBSCRIBE loops at startup -- run_subscriber (crates/buzz-pubsub/src/subscriber.rs), run_cache_invalidation_subscriber (cache_invalidation.rs), and run_conn_control_subscriber (conn_control.rs) -- each with its own duplicated exponential-backoff constants (BACKOFF_INITIAL_SECS = 1, BACKOFF_MAX_SECS = 30, doubling on each failed reconnect and resetting to 1s after any successful connection) rather than one shared reconnect implementation."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs"
      - "crates/buzz-pubsub/src/subscriber.rs"
      - "crates/buzz-pubsub/src/cache_invalidation.rs"
      - "crates/buzz-pubsub/src/conn_control.rs"
  - statement: "RedisNip98ReplayGuard::try_mark_in_scope issues SET key 1 NX EX <ttl>, clamping ttl_secs to [buzz_auth::DEFAULT_REPLAY_TTL_SECS (120s), buzz_auth::MAX_REPLAY_TTL_SECS (3600s)]; the code's own comments state a Redis pool-acquire failure or an unexpected SET reply is surfaced as Err, and that the caller 'MUST fail closed' on that Err -- logged via tracing::warn! at the acquire-failure site."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/nip98_replay.rs"
      - "crates/buzz-auth/src/nip98_replay.rs"
  - statement: "RedisRateLimiter::run_rate_limit runs a single Lua script (INCR then, only on the first INCR, EXPIRE) so a crash between the two calls cannot leave a key without a TTL; if TTL is nonetheless found negative (broken state from a prior crash) the code repairs it with a fresh EXPIRE and logs a tracing::warn!, then resets the caller's reported reset_in_secs to the full window rather than trusting the corrupted state."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/rate_limiter.rs"
  - statement: "PubSubManager::publish_cache_invalidation and publish_conn_control's own doc comments state both are 'Fire-and-forget at the call site' with a durable backstop: a dropped cache-invalidation publish is backstopped by the REQ denial path's DB confirmation (the per-event access gate re-fetches authoritative state from Postgres on the next read), and a dropped conn-control publish is backstopped by the durable ban row in Postgres, which still refuses the banned member's next auth attempt even if live disconnection on another pod was missed -- callers 'may spawn this without awaiting delivery.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/lib.rs"
  - statement: "Because every write path this crate exercises is either TTL-bounded (presence: 180s fixed; NIP-98 replay: 120-3600s caller-clamped; rate-limit counters: the caller's configured window, self-repaired if found without an expiry) or a transient PUBLISH with nothing stored, and because the two fire-and-forget publish paths both name a durable Postgres backstop in their own doc comments, Redis in this repository is a cache-and-transport layer, never the system of record -- durable state for every one of these concerns lives in Postgres via buzz-db, and every Redis loss scenario the code anticipates degrades to a slower or delayed Postgres read/write, not data loss."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-pubsub/src/presence.rs"
      - "crates/buzz-pubsub/src/nip98_replay.rs"
      - "crates/buzz-pubsub/src/rate_limiter.rs"
      - "crates/buzz-pubsub/src/lib.rs"
    confidence: 0.85
  - statement: "Every community-scoped Redis key/channel in this repository is prefixed buzz:{community}:..., where {community} is a CommunityId sourced from a TenantContext (buzz-pubsub/src/topic.rs's own unit test same_channel_in_two_communities_has_different_topics asserts two communities never collide on the same channel_id), except the connection-rate limiter's IP-keyed variant, buzz:ratelimit:ip:{ip}:conn, which is deliberately operator-global rather than tenant-scoped because an abusive IP is not a per-community property -- one disclosed exception to an otherwise uniform tenancy boundary, not an oversight."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/topic.rs"
      - "crates/buzz-pubsub/src/rate_limiter.rs"
  - statement: "buzz-relay's readiness handler checks state.redis_pool.get().await.is_ok() concurrently with the Postgres and deletion-serving-catalog checks under a 2s timeout, and returns HTTP 503 with a per-check status body (including a \"redis\": <bool> field) if the Redis leg fails or times out; separately, main() polls the pool's status() and emits four gauges (buzz_redis_pool_available, buzz_redis_pool_size, buzz_redis_pool_max, buzz_redis_pool_waiting) so pool exhaustion is observable before it manifests as readiness failures."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs"
      - "crates/buzz-relay/src/main.rs"
  - statement: "The repository's local dev docker-compose.yml runs Redis as image redis:7-alpine, container buzz-redis, published on 127.0.0.1:6379, health-checked via redis-cli ping, with no volume mount configured -- so state does not survive a local container restart -- and TESTING.md states just test runs integration tests against both Postgres and Redis, and separately documents REDIS_URL=redis://localhost:6379 as one of the environment variables its integration suite expects."
    entry_class: FACT
    evidence:
      - "docker-compose.yml"
      - "TESTING.md"
  - statement: "crates/buzz-pubsub carries at least 11 #[ignore = \"requires Redis\"]-gated async tests exercising the replay guard, rate limiter, presence, cache-invalidation, and conn-control modules against a real Redis instance (env var REDIS_URL, defaulting to redis://127.0.0.1:6379), in addition to the pure-function unit tests in topic.rs (key construction/parsing, per-community isolation) that run without Redis."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/nip98_replay.rs"
      - "crates/buzz-pubsub/src/topic.rs"
  - statement: "Issue #1097's Definition of done requires this node to state whether the store is authoritative, derived, cache or transport; describe owned data, key access patterns, lifecycle/retention and consistency semantics; name tenancy/security boundaries and failure behavior; and link schema/migrations/code/tests rather than copying DDL."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1097 definition of done"
relationships:
  - type: part-of
    target: architecture-containers-redis
---

# Redis (data layer role)

A datastore-level zoom into Redis's own internal shape: what it holds, how that shape
is organized, how it changes over time (it doesn't, via any versioned mechanism), how
other code reaches it, and what operational characteristics its use in this codebase
actually provides. `architecture-containers-redis` already establishes that Redis
exists, its technology, and its one-line responsibility and communication edges as one
row of Buzz's container inventory — this node does not repeat that; it opens the box.

## Purpose and scope

This node documents the Redis instance Buzz depends on, at the depth `templates/
datastore.md` defines for a datastore: its key/channel-namespace inventory, its
(non-existent) migration mechanism, which code accesses it and how, and the operational
characteristics — TTLs, persistence, reconnect behavior — that codebase actually wires
up. It is a datastore-level companion to `architecture-containers-redis` (`part-of`,
below), not a replacement for it: the container node's own responsibility table,
ownership-boundary paragraph, and deployment/security-implications sections are not
restated here. It is also not a domain-model document — no `data-entity` node yet
exists for the Nostr events or presence/rate-limit concepts Redis carries, so this node
stops at "what shape the data takes in Redis," not "what a channel or a presence status
means."

**On this node's `type`.** This node uses `type: layers`, matching the two sibling
`layers/data/*/role.md` documents drafted in the same Feature (#610), even though
`templates/datastore.md`'s own worked example directs a real datastore instance to
`type: architecture` — the same value `architecture-containers-redis` itself uses.
`node.schema.json`'s 13-member enum has no finer-grained value distinguishing a
container-level structural row from a data-layer synthesis document, so this is a
disclosed override of the template's guidance to follow this Feature's own established
precedent, per `standards/taxonomy.md`'s instruction to name an imperfect or overridden
fit explicitly rather than silently pick one enum value over another.

## Authoritative, derived, cache, or transport

**Cache and transport — never the system of record.** Every Redis write path this
codebase exercises is either TTL-bounded (presence, NIP-98 replay, rate-limit counters)
or a transient `PUBLISH` with nothing persisted at all (event fan-out, cache
invalidation, connection control). The two fire-and-forget publish paths
(`publish_cache_invalidation`, `publish_conn_control`) name a durable Postgres backstop
directly in their own doc comments: a dropped cache-invalidation publish is caught by
the per-event access gate re-fetching authoritative state from Postgres on the next
read, and a dropped conn-control publish is caught by the durable ban row in Postgres,
which still refuses the next auth attempt regardless of whether live disconnection
landed on every pod. Durable state for every concern Redis touches — events, channels,
bans, moderation — lives in Postgres via `buzz-db`; Redis holds only the transient
coordination layer on top of it.

## Owned data — key/channel-namespace inventory

A structural list only; domain meaning (what a channel or a presence status *is*) is
out of scope here and belongs to a future `data-entity` node.

| Key / channel family | Owning module | Structural purpose |
|---|---|---|
| `buzz:{community}:channel:{uuid}`, `buzz:{community}:global` | `topic.rs`, `publisher.rs`, `subscriber.rs` | Pub/sub channels: cross-pod Nostr event fan-out, scoped to one exact channel or community-wide |
| `buzz:{community}:presence:{pubkey_hex}` | `presence.rs` | `SET`/`GET`/`DEL` key holding one member's online/away status, 180s TTL |
| `buzz:{community}:cache-invalidate` | `cache_invalidation.rs` | Pub/sub channel carrying cross-pod cache-key drops (never eviction instructions) |
| `buzz:{community}:conn-control` | `conn_control.rs` | Pub/sub channel carrying cross-pod connection-control commands (live ban enforcement) |
| `buzz:{community}:nip98:{event_id_hex}` | `nip98_replay.rs` | `SET ... NX EX` seen-set entry for one HTTP-auth event id, atomic set-if-absent |
| `buzz:{community}:ratelimit:{pubkey_hex}:{suffix}` | `rate_limiter.rs` | Fixed-window counter, per-principal admission limits |
| `buzz:ratelimit:ip:{ip}:conn` | `rate_limiter.rs` | Fixed-window counter, per-IP connection limits — the one deliberately operator-global family, see *Tenancy and security boundaries* |

Every key/channel name is built by `format!()` interpolation of the shared
`BUZZ_PREFIX` constant inside its owning module — there is no separate schema file, and
no naming convention exists outside the module that constructs it.

## Migration / schema-versioning mechanism

**None exists, and this is a real datastore fact, not an omission.** Unlike
`buzz-db`'s embedded `sqlx::migrate!("../../migrations")` `MIGRATOR` — numbered SQL
files applied in strict order, the whole run guarded by an exclusive session lock — a
Redis key format in this codebase is a plain Rust `format!()` call or string constant
inside the module that owns it. Changing a key's shape is an ordinary code edit and a
crate version bump: no ordering guard, no lock, no `migrations/`-style directory, and
no tooling that would detect two pods running different key formats against the same
Redis instance simultaneously during a rolling deploy. Whether that gap has ever
mattered in practice is not established by anything in this repository — named here as
a gap, not resolved.

## Access-pattern summary

`buzz-pubsub` owns every Redis access pattern in the repository — nothing outside that
crate issues a Redis command directly. `buzz-relay` owns the *lifecycle*: it builds the
one shared `deadpool_redis::Pool` from `config.redis_url` / `config.redis_pool_size`,
constructs `PubSubManager` from it, and wires the same pool into
`Arc<RedisNip98ReplayGuard>` and `Arc<RedisRateLimiter>` on `AppState`. `buzz-auth`
owns the *interfaces* (`RateLimiter`, `Nip98ReplayGuard`) those Redis-backed types
implement, and has zero Redis dependency of its own — the auth contract stays testable
against an always-allow stub without Redis running.

Two distinct connection shapes are in play, deliberately kept separate:

- **The shared pool** (`deadpool_redis::Pool`) serves every request-path command:
  `PUBLISH`, `SET`/`GET`/`DEL`, `INCR`, and the rate-limiter's Lua script.
- **Three dedicated (non-pooled) connections**, one per subscriber loop —
  `run_subscriber`, `run_cache_invalidation_subscriber`, `run_conn_control_subscriber`
  — because a pooled connection cannot hold `SUBSCRIBE`/`PSUBSCRIBE` state. Each loop
  reconnects independently with its own duplicated exponential backoff (1s → 2s → 4s →
  … → 30s max, resetting to 1s after any successful connection); the three
  implementations are not shared, so a fix to one loop's reconnect logic does not
  automatically apply to the other two.

**Consistency semantics are per-key-family, not uniform:**

- **Atomic set-if-absent** — the NIP-98 replay guard's `SET key 1 NX EX <ttl>` succeeds
  exactly once per key; every later claim within the TTL window observes the key already
  present and is surfaced to the caller as replay.
- **Atomic increment-with-expiry** — the rate limiter's Lua script combines `INCR` and a
  first-call `EXPIRE` into one atomic operation specifically so a crash between the two
  cannot leave a counter key without a TTL; if a negative TTL is nonetheless observed
  (broken state from an earlier crash), the code repairs it with a fresh `EXPIRE` and
  logs a warning rather than trusting the corrupted state.
- **At-most-once, no queuing** — `PUBLISH` on the three pub/sub channel families
  delivers only to pods currently subscribed; nothing is queued or replayed for a pod
  that reconnects late. The cache-invalidation and conn-control paths are designed
  around exactly this: their own doc comments call them "fire-and-forget," backstopped
  by a Postgres re-read or a durable ban row rather than by Redis delivery guarantees.

## Tenancy and security boundaries

Every community-scoped key/channel is prefixed `buzz:{community}:...`, where
`{community}` comes from a resolved `TenantContext`; `topic.rs`'s own unit test asserts
two communities never collide on the same channel id. **One deliberate exception:**
`buzz:ratelimit:ip:{ip}:conn` is operator-global rather than tenant-scoped, because an
abusive IP address is not a per-community property — a disclosed exception to an
otherwise uniform boundary, not an oversight. The pub/sub channel key is a routing
label, not a confidentiality boundary: nothing outside `buzz-relay` opens a Redis
connection at all (desktop, mobile, CLI and web clients reach the relay's WebSocket/HTTP
surface only), and payload confidentiality for anything sensitive is carried by NIP-44
encryption independent of Redis, per `architecture-containers-redis`'s own security
paragraph, which this node does not restate further.

## Failure behavior

Failure behavior differs by which key family is on the critical path:

- **Admission paths fail closed.** `RedisNip98ReplayGuard` and `RedisRateLimiter` both
  surface a Redis pool-acquire failure as `Err`, and the caller "MUST fail closed" per
  the code's own comments and `tracing::warn!` sites — a Redis outage denies the
  affected requests rather than silently admitting them.
- **Cross-pod coordination degrades, it does not fail the request.** Cache-invalidation
  and connection-control publishes are explicitly not awaited for delivery; a dropped
  publish leaves a stale local cache (caught by the next Postgres re-read through the
  access gate) or a missed live disconnect (caught by the durable ban row refusing the
  next auth attempt) rather than surfacing an error to any caller.
- **Externally observable via the readiness probe and pool gauges.** `buzz-relay`'s
  readiness handler checks `state.redis_pool.get().await.is_ok()` concurrently with the
  Postgres and deletion-serving-catalog legs under a 2s timeout, returning HTTP 503 with
  a per-check status body (including a `"redis"` boolean) if the Redis leg fails or
  times out. Separately, four Prometheus-style gauges
  (`buzz_redis_pool_available/size/max/waiting`) expose pool exhaustion before it
  manifests as a readiness failure.
- **The three SUBSCRIBE loops reconnect indefinitely** with exponential backoff rather
  than terminating on a dropped Redis connection, so a transient outage recovers
  automatically once Redis returns; there is no maximum retry count and no alerting
  wired to sustained reconnect failure visible in this repository.

## Operational characteristics

**Lifecycle / retention** — presence: fixed 180s TTL (3x the 60s client heartbeat, so
one missed heartbeat does not flap presence); NIP-98 replay: caller-supplied TTL clamped
to `[120s, 3600s]`; rate-limit counters: the caller's configured window, self-repaired
via `EXPIRE` if found without one; pub/sub messages: nothing stored, delivered
at-most-once to currently-subscribed pods. **Persistence** — local dev's `redis:7-alpine`
container in `docker-compose.yml` has no volume mount configured, so state does not
survive a container restart; whether staging/production ElastiCache enables any
persistence mechanism (RDB snapshots, AOF) is not established by anything in this
repository. **Connectivity** — `redis://` in local dev, `rediss://` (TLS) to AWS
ElastiCache in staging/production, per the `rustls` crypto-provider installation comment
in `buzz-relay`'s `main()`; the same `REDIS_URL` config variable carries either form
without a code change, per Factor IV's backing-service framing.

## Implementation and verification

Implementation lives in `crates/buzz-pubsub/src/` (`topic.rs`, `presence.rs`,
`nip98_replay.rs`, `rate_limiter.rs`, `cache_invalidation.rs`, `conn_control.rs`,
`publisher.rs`, `subscriber.rs`) and is wired up in `crates/buzz-relay/src/main.rs`
(pool construction, subscriber-loop spawning, pool-status gauges) and
`crates/buzz-relay/src/state.rs` (`AppState` wiring of `RedisNip98ReplayGuard` and
`RedisRateLimiter`). The readiness probe is in `crates/buzz-relay/src/router.rs`.
Configuration is documented in `.env.example` (`REDIS_URL`, `BUZZ_REDIS_POOL_SIZE`);
local dev provisioning is in `docker-compose.yml`. Tests live alongside each module in
`crates/buzz-pubsub/src/` — at least 11 are gated `#[ignore = "requires Redis"]` and
exercise the replay guard, rate limiter, presence, cache-invalidation and conn-control
modules against a live Redis instance; `topic.rs`'s key-construction/parsing and
per-community-isolation tests run without Redis. `TESTING.md` documents `just test`'s
requirement of a running Redis instance for the integration suite. There is no DDL to
link — the closest analogue, the key-format constants and `format!()` call sites, are
cited directly above per key family rather than reproduced here.

## Scope and omissions

**This node covers** Redis's key/channel-namespace inventory, its (absent) migration
mechanism, which code accesses it and how, its consistency semantics per key family,
its tenancy and security boundaries, its failure behavior, and the operational
characteristics (TTL, persistence, connectivity) this codebase's own code establishes.

**It does not cover, and these are gaps rather than silence:**

- **Redis's container-level existence, technology name, and one-line responsibility and
  communication edges** — `architecture-containers-redis`, which this node is `part-of`
  and does not repeat.
- **The domain meaning of the data Redis carries** (what a channel, a presence status,
  or a rate-limit tier *means*) — no `data-entity` node exists yet for these concepts at
  the recorded revision; this node stops at structure, per `templates/datastore.md`'s
  own boundary against domain-model content.
- **Where any given Redis instance actually runs, per environment** — replica count,
  whether staging/production ElastiCache is externally managed, secret provisioning —
  a `deployment`-shaped concern this node does not attempt; `architecture-containers-
  redis`'s own deployment-implications paragraph already names
  `squareup/block-coder-tf-stacks` as the Terraform/ArgoCD project deploying the relay
  that depends on Redis, without establishing whether that same stack provisions the
  backing ElastiCache instance itself.
- **Whether staging/production ElastiCache enables persistence (RDB/AOF)** — not
  established by anything in this repository; local dev's container config (no volume)
  is the only persistence-relevant fact directly verified.
- **Whether a rolling deploy running two pods with different Redis key formats
  simultaneously has ever caused an observable problem** — named as a real gap in
  *Migration / schema-versioning mechanism*, above, not resolved.
- **`RateLimitConfig`'s tier design** beyond the mechanism that enforces whichever tier
  is configured — a `buzz-auth` concept, out of this datastore node's scope, matching
  `architecture-containers-redis`'s own identical omission.
- **Typing-indicator delivery** — `architecture-containers-redis` already names this as
  an unresolved gap (a stray doc comment references it, but no `typing` module or key
  pattern exists in `buzz-pubsub` at its recorded revision); not re-investigated here.

**Expected but not verified when this node was written:**

- **The two sibling `layers/data/*/role.md` documents (#1073 for object storage, #1087
  for Postgres) were not read**, since neither is merged at the recorded revision — this
  node's shape (`type: layers`, the datastore-template section set) follows the batch
  dispatch brief's stated precedent, not a direct comparison against their actual text.
- **Whether staging/production ElastiCache's sizing, eviction policy, or failover
  behavior matches what the codebase assumes** (e.g., that a `SET ... EX` key reliably
  expires, that `INCR` remains atomic under whatever eviction policy is configured) was
  not checked — none of that configuration is visible from this repository.
- **Whether any external monitoring alerts on the three SUBSCRIBE loops' sustained
  reconnect failure** was not verified; the code itself retries indefinitely with no
  visible alerting hook in this repository.
