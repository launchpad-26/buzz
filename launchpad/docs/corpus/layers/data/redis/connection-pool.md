---
id: layers-data-redis-connection-pool
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
  - statement: "buzz-relay's main() builds the single shared Redis connection pool via deadpool_redis::Config::from_url(&config.redis_url), sets its PoolConfig from config.redis_pool_size, and creates it with the Tokio1 runtime; a pool-creation failure at startup is fatal (anyhow::anyhow!(\"Redis pool creation failed: {e}\")), not a degraded-mode fallback."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs"
  - statement: "Config::from_env reads REDIS_URL (falling back to redis://localhost:6379 when unset) and BUZZ_REDIS_POOL_SIZE (parsed as usize, filtered to values greater than zero, defaulting to 16 when unset, zero, or unparsable) into Config.redis_url and Config.redis_pool_size."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/config.rs"
  - statement: "config.rs's own doc comment on redis_pool_size states its default of 16 is a deliberate departure from deadpool's own CPU_COUNT * 2 default, reasoning that on a 2-vCPU relay pod that default is only 4 -- small enough that rate-limit checks, presence, and pub/sub publishes queue behind each other under load."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/config.rs"
  - statement: "config.rs's own redis_pool_size_env_override_and_invalid_fallback test asserts that BUZZ_REDIS_POOL_SIZE=32 overrides the default to 32, while both BUZZ_REDIS_POOL_SIZE=0 and BUZZ_REDIS_POOL_SIZE=not-a-number fall back to 16."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/config.rs"
  - statement: "main() clones the pool -- a cheap Arc clone, per its own inline comment -- into a dedicated redis_health_pool before constructing PubSubManager::new(&config.redis_url, redis_pool) from the original; AppState.redis_pool (wired in state.rs) is that same pool, additionally passed into Arc<RedisNip98ReplayGuard> and Arc<RedisRateLimiter>."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs"
      - "crates/buzz-relay/src/state.rs"
  - statement: "buzz-pubsub's own module-level doc comment draws the pool boundary explicitly, as an architecture diagram: a deadpool-redis pool handles PUBLISH/SET/ZADD-class commands, while a dedicated (non-pooled) redis::aio::PubSub connection -- described as stateful and not shareable -- serves the SUBSCRIBE loops. PubSubManager's run_subscriber, run_cache_invalidation_subscriber, and run_conn_control_subscriber each construct their own connection from self.redis_url.clone(), never from self.pool."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/lib.rs"
  - statement: "Every other Redis-touching operation in buzz-pubsub draws from the shared pool: PubSubManager's publish_event and the four presence functions call pool.get().await via their own module functions (publisher::publish_event(&self.pool, ...), presence::set_presence(&self.pool, ...) and its three siblings); RedisNip98ReplayGuard::try_mark and RedisRateLimiter's run_rate_limit each hold their own deadpool_redis::Pool field and call pool.get().await directly."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/lib.rs"
      - "crates/buzz-pubsub/src/nip98_replay.rs"
      - "crates/buzz-pubsub/src/rate_limiter.rs"
  - statement: "nip98_replay.rs's try_mark carries a source comment on its pool.get() error path reading \"nip98 replay: redis pool acquire failed — caller MUST fail closed\", and returns AuthError::Internal on that path rather than treating the failure as an implicit pass."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/nip98_replay.rs"
  - statement: "rate_limiter.rs's run_rate_limit maps a pool.get() failure to Err(AuthError::Internal(...)); buzz-relay's admission::check_principal maps any Err surfaced through the RateLimiter trait to AdmissionError::Unavailable (and logs it via tracing::warn!), a distinct outcome from AdmissionError::Exceeded (quota hit but the check itself succeeded)."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/rate_limiter.rs"
      - "crates/buzz-relay/src/admission.rs"
  - statement: "Both call sites that handle AdmissionError::Unavailable deny the request rather than letting it through: api/bridge.rs's HTTP path returns 503 Service Unavailable with a \"shared admission unavailable\" body, and connection.rs's WebSocket path sends a rejection message and returns false from its admission check; both increment a buzz_admission_rejections_total counter tagged reason=\"unavailable\"."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs"
      - "crates/buzz-relay/src/connection.rs"
  - statement: "router.rs's readiness_handler runs three checks concurrently (tokio::join!) under a 2-second tokio::time::timeout: state.db.ping(), state.redis_pool.get().await.is_ok(), and a deletion-serving-catalog validation. A timeout collapses all three to false; the response is HTTP 503 with a per-check JSON body (including \"redis\": redis_ok) unless every check passed."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs"
  - statement: "main() spawns a background task that, on a BUZZ_POOL_METRICS_INTERVAL_SECS-controlled interval (parsed as u64, defaulting to 10, floored at 1 to avoid a zero-duration tokio::time::interval panic), reads the pool's own status() and publishes it as four gauges: buzz_redis_pool_available, buzz_redis_pool_size, buzz_redis_pool_max, buzz_redis_pool_waiting."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs"
  - statement: "The workspace root Cargo.toml pins redis to version 1.0 with the tokio-comp, connection-manager, and tokio-rustls-comp features, and deadpool-redis to version 0.23 with the rt_tokio_1 feature. buzz-pubsub's own Cargo.toml depends on both and describes the crate as \"Redis pub/sub fan-out, presence, and typing indicators for Buzz\"."
    entry_class: FACT
    evidence:
      - "Cargo.toml"
      - "crates/buzz-pubsub/Cargo.toml"
  - statement: ".env.example documents REDIS_URL (default redis://localhost:6379) and a commented-out BUZZ_REDIS_POOL_SIZE=16; the local dev docker-compose.yml runs Redis as redis:7-alpine (container buzz-redis, published on 127.0.0.1:6379, health-checked via `redis-cli ping`, memory-limited to 128m, with no volume mount configured -- so state does not survive a container restart)."
    entry_class: FACT
    evidence:
      - ".env.example"
      - "docker-compose.yml"
  - statement: "main()'s startup carries a source comment stating the ring rustls CryptoProvider is installed up front because it is required before any rustls TLS connection, explicitly naming rediss:// to ElastiCache alongside wss:// and S3-over-TLS as connections that need it -- i.e. production/staging Redis is reached over TLS, not the plaintext redis:// used in local dev."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs"
  - statement: "topic.rs's channel_key/global_key functions and rate_limiter.rs's own module doc comment establish the key-naming convention every pool-drawn command operates under: pubkey- and channel-scoped keys are community-prefixed (buzz:{community}:channel:{id}, buzz:{community}:global, buzz:{community}:ratelimit:{pubkey_hex}:{suffix}), except the IP-based connection limiter's key, which is deliberately operator-global (buzz:ratelimit:ip:{ip}:conn) rather than tenant-scoped."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/topic.rs"
      - "crates/buzz-pubsub/src/rate_limiter.rs"
  - statement: "presence.rs's own module doc comment states presence is TTL-bound (\"TTL is 3x the 60s heartbeat interval so a single missed heartbeat doesn't flip a user to offline\"), and its PRESENCE_TTL_SECS constant is 180, asserted directly by the module's own presence_ttl_is_three_one_minute_heartbeat_windows test (PRESENCE_TTL_SECS == 3 * 60)."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/presence.rs"
  - statement: "Across the pooled write paths inspected in this node's own evidence (presence: 180s TTL; the rate-limit counter: caller-supplied window, atomically INCR+EXPIRE via a Lua script per rate_limiter.rs's own doc comment; the NIP-98 replay guard: caller-supplied TTL via SET ... NX EX) and the pub/sub PUBLISH paths (transient, nothing stored), the connection pool fronts a volatile coordination/transport layer rather than an authoritative or durable store of Buzz data -- consistent with, and independently re-derived from primary sources rather than merely re-cited from, the same conclusion architecture-containers-redis's own evidence ledger reaches about Redis as a whole."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-pubsub/src/presence.rs"
      - "crates/buzz-pubsub/src/rate_limiter.rs"
      - "crates/buzz-pubsub/src/nip98_replay.rs"
      - "crates/buzz-pubsub/src/lib.rs"
    confidence: 0.8
  - statement: "Issue #1092's Definition of done requires this node to state whether the store the pool fronts is authoritative, derived, cache, or transport; describe owned data, key access patterns, lifecycle/retention, and consistency semantics; name tenancy/security boundaries and failure behavior; and link schema/migrations/code/tests rather than copy DDL -- the same checklist shape #1080's Postgres connection-pool analogue and the parent template (templates/datastore.md) both carry."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "https://github.com/launchpad-26/buzz/issues/1092 definition of done"
  - statement: "This batch's own dispatch brief overrides templates/datastore.md's own stated guidance -- that a real datastore instance node should take type: architecture, on the grounds no finer-grained enum member exists -- to type: layers for every launchpad/docs/corpus/layers/data/... document in this batch, including this one; the override is followed here rather than templates/datastore.md's literal text, per the dispatching task's explicit instruction."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "corpus-batch-author dispatch brief for issue #1092, overriding templates/datastore.md's own type guidance for every layers/data/... sibling in the same overnight batch"
relationships:
  - type: part-of
    target: architecture-containers-redis
---

# Redis connection pool

The shared `deadpool_redis::Pool` `buzz-relay` builds at startup and hands to every
Redis-touching consumer inside the relay process except the three long-running pub/sub
SUBSCRIBE loops, which deliberately bypass it. This is the connection-pool axis of the
already-merged `architecture-containers-redis` node, which documents Redis's five job
areas, deployment, and security posture at one line of depth; this document opens the
pool itself: how it is sized and attached, who draws from it versus who does not, how
its health is observed, and what happens when it cannot be drawn from.

**A note on this node's `type`.** `node.schema.json`'s 13-member `type` enum has no
member more specific than `architecture` for an instance document like this one, and
`templates/datastore.md` — the closest-fitting existing template, itself `type:
governance` — states that a real datastore instance most plausibly takes `type:
architecture` for exactly that reason. This node instead carries `type: layers`,
overriding that guidance per the batch dispatch brief that produced it, matching every
other `launchpad/docs/corpus/layers/data/...` sibling in the same overnight batch. See
*Scope and omissions* for the disclosure this override requires.

## Store classification

The pool exists to reach Redis, and Redis's own role here is coordination and
transport, not an authoritative or durable store of Buzz data. Every pooled write path
this node inspected directly is either TTL-bound (presence: 180 seconds, per
`presence.rs`'s own constant and test; the rate-limit counter: the caller-supplied
window, atomically `INCR`+`EXPIRE`'d by a Lua script; the NIP-98 replay guard: a
caller-supplied TTL via `SET ... NX EX`) or a transient `PUBLISH` with nothing
persisted at all. Postgres (`buzz-db`) is the system of record; this pool never reaches
it. Nothing here contradicts `architecture-containers-redis`'s own evidence for Redis
as a whole — this node re-derives the same conclusion from primary sources rather than
resting on that document's word for it.

## Technology and attachment profile

`redis` 1.0 (`tokio-comp`, `connection-manager`, `tokio-rustls-comp` features) and
`deadpool-redis` 0.23 (`rt_tokio_1` feature), pinned in the workspace root `Cargo.toml`.
The pool is constructed once, in `buzz-relay`'s `main()`, from `deadpool_redis::Config::from_url`
against `REDIS_URL` (`.env.example` default `redis://localhost:6379`; local dev runs
Redis as the `redis:7-alpine` `buzz-redis` container in `docker-compose.yml`, no volume
mount, so state does not survive a restart), with its `PoolConfig` sized from
`BUZZ_REDIS_POOL_SIZE` (`config.rs`: parsed as `usize`, any non-positive or unparsable
value falls back to a default of 16, asserted directly by `config.rs`'s own
`redis_pool_size_env_override_and_invalid_fallback` test). `config.rs`'s own doc
comment states 16 is a deliberate departure from `deadpool`'s own `CPU_COUNT * 2`
default, sized against a 2-vCPU relay pod where that default (4) is too small to avoid
rate-limit, presence, and pub/sub publish operations queuing behind each other under
load. In staging and production this connection is `rediss://` (TLS) to AWS
ElastiCache — `main()`'s own startup comment names that connection explicitly as one of
the reasons the `rustls` `ring` crypto provider is installed before any other TLS
connection is opened. Pool creation failure at startup is fatal to relay boot, not a
degraded-mode fallback.

## Consumers: pooled versus dedicated

`buzz-pubsub`'s own module-level doc comment states this split as the crate's
architecture. The pool serves every request/response-shaped Redis operation in the
relay process:

| Consumer | Operation | Pool-drawn? |
|---|---|---|
| `PubSubManager::publish_event` | `PUBLISH` (channel/global event fan-out) | Yes — `self.pool` |
| `PubSubManager`'s four presence functions | `SET`/`GET`/`DEL` | Yes — `self.pool` |
| `RedisNip98ReplayGuard::try_mark` | `SET ... NX EX` | Yes — its own `pool` field |
| `RedisRateLimiter`'s rate-limit script | Lua `INCR`+`EXPIRE` | Yes — its own `pool` field |
| Readiness probe (`readiness_handler`) | `pool.get()` as a liveness check, no command issued | Yes — `state.redis_pool` |
| Pool-metrics gauge loop | `pool.status()` | Yes — the pool's own in-memory state, no network round trip |

Three long-running loops bypass the pool entirely, each opening its own
`redis::aio::PubSub` connection from `self.redis_url.clone()`: `run_subscriber`
(channel/global event fan-out), `run_cache_invalidation_subscriber` (cross-pod cache-key
drops), and `run_conn_control_subscriber` (cross-pod ban/disconnect enforcement).
`buzz-pubsub`'s own doc comment gives the reason: a pooled connection cannot hold
`SUBSCRIBE` state, and the dedicated connection is described as stateful and not
shareable. **The dedicated-connection reconnect behavior, and the SUBSCRIBE/PUBLISH
channel protocol those three loops speak, are out of this node's scope** — see *Scope
and omissions*.

## Lifecycle, health, and observability

The pool is created once at relay startup and lives for the process's lifetime; there
is no runtime resize. `readiness_handler` (`router.rs`) folds `state.redis_pool.get().await.is_ok()`
into a three-way concurrent check (alongside a Postgres ping and a deletion-serving
catalog validation) under a single 2-second `tokio::time::timeout`; a timeout counts
every check as failed, and the endpoint returns HTTP 503 with a per-check JSON body
(`"redis": redis_ok`) unless all three passed. A background task polls the pool's own
`status()` on a `BUZZ_POOL_METRICS_INTERVAL_SECS`-controlled interval (default 10
seconds, floored at 1 to avoid a zero-duration timer panic) and publishes four Prometheus-style
gauges: `buzz_redis_pool_available`, `buzz_redis_pool_size`, `buzz_redis_pool_max`,
`buzz_redis_pool_waiting`.

## Tenancy, security boundary, and failure behavior

Every key a pool-drawn command touches is community-prefixed
(`buzz:{community}:channel:{id}`, `buzz:{community}:global`,
`buzz:{community}:ratelimit:{pubkey_hex}:{suffix}`, per `topic.rs` and `rate_limiter.rs`'s
own doc comment), with one deliberate exception: the IP-based connection-rate limiter's
key (`buzz:ratelimit:ip:{ip}:conn`) is operator-global rather than tenant-scoped,
because an abusive IP is not a per-community property. **The full key-naming
convention beyond what a pool consumer needs is out of this node's scope** — see *Scope
and omissions*.

On failure, the two callers most exposed to a pool outage — the NIP-98 replay guard and
the rate limiter — both fail closed, and this is stated in the code, not merely
observed as a side effect: `nip98_replay.rs` carries an explicit comment that a
`pool.get()` failure "MUST fail closed," returning an error rather than treating the
failure as an implicit pass. `rate_limiter.rs` propagates a `pool.get()` failure as an
error, which `buzz-relay`'s `admission::check_principal` maps to a distinct
`AdmissionError::Unavailable` (logged via `tracing::warn!`) rather than `Exceeded`. Both
call sites that handle `Unavailable` — the HTTP path in `api/bridge.rs` and the
WebSocket path in `connection.rs` — deny the request (503 / rejection message) rather
than letting it through, each incrementing `buzz_admission_rejections_total{reason="unavailable"}`.
A pool outage therefore degrades availability for rate-limited and replay-guarded
operations rather than silently relaxing either guarantee.

## Migration / schema-versioning

Not applicable in the sense `templates/datastore.md` uses the term for a schema-bearing
store: Redis carries no DDL and this repository defines no migration mechanism for it.
The only "schema" a reader can check against code is the key-naming convention itself
(`topic.rs`, `rate_limiter.rs`'s doc comment, `presence.rs`), which this node names at
the level a pool consumer needs and does not restate in full — see *Scope and
omissions*.

## Links

Implementation: `crates/buzz-relay/src/main.rs` (pool construction, subscriber spawns,
pool-metrics loop), `crates/buzz-relay/src/config.rs` (`redis_url`/`redis_pool_size`
fields and env parsing), `crates/buzz-relay/src/state.rs` (`AppState.redis_pool`
wiring), `crates/buzz-relay/src/router.rs` (`readiness_handler`),
`crates/buzz-relay/src/admission.rs` and its callers in
`crates/buzz-relay/src/api/bridge.rs` and `crates/buzz-relay/src/connection.rs`
(fail-closed admission handling), `crates/buzz-pubsub/src/lib.rs` (`PubSubManager`,
the pooled/dedicated split), `crates/buzz-pubsub/src/rate_limiter.rs` and
`crates/buzz-pubsub/src/nip98_replay.rs` (pooled consumers with explicit fail-closed
behavior). Tests: `crates/buzz-relay/src/config.rs`'s
`redis_pool_size_env_override_and_invalid_fallback`. Configuration:
`.env.example` (`REDIS_URL`, `BUZZ_REDIS_POOL_SIZE`), `docker-compose.yml` (local dev
Redis container). The broader Redis container this pool is one axis of:
`launchpad/docs/corpus/architecture/containers/redis.md`.

## Scope and omissions

**This node covers** the shared Redis connection pool itself: how it is constructed,
sized, and attached; which consumers draw from it and which deliberately bypass it;
how its health and metrics are observed; and what happens, concretely, when it cannot
be drawn from.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The full Redis container — its five job areas, deployment topology, and security posture at container-inventory depth | `architecture-containers-redis` (already merged) |
| The channel/PUBLISH pub/sub protocol and event fan-out semantics | `layers/data/redis/channel-pubsub.md`, launchpad-26/buzz#1091 — not yet authored on `origin/launchpad` at this node's authoring time |
| The three dedicated (non-pooled) SUBSCRIBE connections' own reconnect/backoff behavior | `layers/data/redis/dedicated-pubsub-connection.md`, launchpad-26/buzz#1093 — not yet authored |
| The full `buzz:{community}:...` key-naming convention, beyond what a pool consumer needs to be named here | `layers/data/redis/key-namespacing.md`, launchpad-26/buzz#1094 — not yet authored |
| The Postgres connection pool, the analogous node for the durable store | `layers/data/postgres/connection-pool.md`, launchpad-26/buzz#1080 — not yet authored on `origin/launchpad` at this node's authoring time |

**The `type: layers` override.** `templates/datastore.md`'s own guidance directs a real
datastore instance node to `type: architecture`, reasoning that `node.schema.json`
offers no finer-grained member for a container-, component-, or datastore-level
structural view. This node uses `type: layers` instead, per this batch's own dispatch
instruction applied uniformly to every `layers/data/...` sibling. No corpus-wide
decision reconciling the two was found or made here; a future pass across the batch may
need to revisit either the template's guidance or this batch's override.

**No `relationships` edge to any of the four not-yet-authored sibling tasks named
above**, or to `layers/data/postgres/connection-pool.md` (#1080): none exist on
`origin/launchpad` at this node's authoring time, and `relationships[].target` naming an
id no loaded node carries is a hard validation error. The one edge this node does
declare — `part-of` targeting `architecture-containers-redis` — resolves today because
that node is already merged.

**Expected but not verified when this node was written:**

- **Whether ElastiCache's own connection or backlog limits are provisioned by
  `squareup/block-coder-tf-stacks` or a separate stack** was not established — this
  repository does not contain that Terraform, and `architecture-containers-redis` names
  the same gap for Redis as a whole.
- **Whether `BUZZ_REDIS_POOL_SIZE`'s default of 16 or `BUZZ_POOL_METRICS_INTERVAL_SECS`'s
  default of 10 seconds were sized against any measured production load**, versus chosen
  as a reasonable starting point, is not established from the code or its comments
  alone, and this node does not claim more than what the source states.
- **Whether any consumer outside `buzz-pubsub` acquires from this pool directly** was
  checked only for the call sites this node's own evidence cites (`buzz-relay`'s
  readiness handler and pool-metrics loop); no exhaustive repository-wide search for
  every `redis_pool.get()` call site was performed.
