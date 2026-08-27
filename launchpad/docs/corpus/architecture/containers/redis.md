---
id: architecture-containers-redis
type: architecture
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - operator
evidence:
  - statement: "This node was authored and checked against repository revision a44cf52fc740ebebbdd671427480d14f0bce0115 on the launchpad branch."
    entry_class: FACT
    evidence:
      - "commit a44cf52fc740ebebbdd671427480d14f0bce0115"
  - statement: "buzz-pubsub is a workspace crate whose stated purpose is Redis pub/sub fan-out, presence, and typing indicators for Buzz, and it depends on the redis and deadpool-redis crates."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/Cargo.toml"
  - statement: "PubSubManager (buzz-pubsub's central type) holds a deadpool_redis::Pool plus the Redis connection URL, and is constructed from a redis_url and an existing pool via PubSubManager::new / PubSubManager::with_config."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/lib.rs"
  - statement: "PubSubManager.publish_event PUBLISHes a Nostr event to a community- and topic-scoped Redis channel and returns the subscriber count; the topic key is a routing label, not an isolation boundary, and the code's own doc comment states Redis only ever carries events between nodes inside the relay trust domain, with NIP-44 ciphertext already encrypted to the intended recipient regardless."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/lib.rs"
  - statement: "EventTopicKey::redis_channel builds channel names of the form buzz:{community}:channel:{uuid} for a specific channel and buzz:{community}:global for community-wide events, both prefixed by the crate's BUZZ_PREFIX constant."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/topic.rs"
  - statement: "presence.rs sets a presence key at buzz:{community}:presence:{pubkey_hex} (built from the same tenant-scoped key convention) via Redis SET with a fixed PRESENCE_TTL_SECS TTL, chosen as 3x the 60s client heartbeat so one missed heartbeat does not flap presence; set_presence/clear_presence/get_presence/get_presence_bulk are the exposed operations."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/presence.rs"
  - statement: "cache_invalidation.rs carries cross-pod cache-key drops over a buzz:{community}:cache-invalidate Redis pub/sub channel; its own module doc states the payload is a pure cache-key drop, never an eviction instruction, because the per-event access gate re-fetches authoritative state from the database on the next read."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/cache_invalidation.rs"
  - statement: "conn_control.rs carries cross-pod connection-control commands (DisconnectCommunity, DisconnectPubkey) over a buzz:{community}:conn-control Redis pub/sub channel, used for live ban enforcement so a member banned on one pod is disconnected on every pod."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/conn_control.rs"
  - statement: "nip98_replay.rs's RedisNip98ReplayGuard implements buzz-auth's Nip98ReplayGuard trait; try_mark issues a single Redis SET buzz:{community}:nip98:{event_id_hex} 1 NX EX <ttl>, using NX atomicity so only the first claim within the TTL window succeeds and later claims are surfaced as replay."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/nip98_replay.rs"
  - statement: "rate_limiter.rs's RedisRateLimiter implements buzz-auth's RateLimiter trait as a fixed-window counter, keyed buzz:{community}:ratelimit:{pubkey_hex}:{suffix} for per-principal limits and buzz:ratelimit:ip:{ip}:conn (operator-global, not community-scoped) for per-IP connection limits; INCR and EXPIRE are combined into one Lua script so a crash between the two calls cannot leave a key without a TTL."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/rate_limiter.rs"
  - statement: "buzz-auth defines the RateLimiter trait's check_and_increment/check_ip_connection contract; buzz-pubsub is the only crate in the workspace providing a real (Redis-backed) implementation of it, alongside a test-only always-allow stub."
    entry_class: FACT
    evidence:
      - "crates/buzz-auth/src/rate_limit.rs"
      - "crates/buzz-pubsub/src/rate_limiter.rs"
  - statement: "buzz-relay's main() builds the single shared redis_pool via deadpool_redis::Config::from_url(&config.redis_url) with pool size config.redis_pool_size, then constructs PubSubManager::new(&config.redis_url, redis_pool) from it; PubSubManager additionally opens its own dedicated (non-pooled) redis::aio connections for its SUBSCRIBE/PSUBSCRIBE loops because pooled connections cannot hold subscribe state."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs"
  - statement: "buzz-relay spawns three long-running Redis pub/sub subscriber loops at startup: run_subscriber (multi-node channel event fan-out), run_cache_invalidation_subscriber (cross-pod cache-key drops), and run_conn_control_subscriber (cross-pod ban/disconnect enforcement); each reconnects with exponential backoff (1s to 30s) and runs forever once spawned."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs"
      - "crates/buzz-pubsub/src/lib.rs"
      - "crates/buzz-pubsub/src/conn_control.rs"
  - statement: "AppState::new wires the same redis_pool into Arc<RedisNip98ReplayGuard> and Arc<RedisRateLimiter>, stored on AppState as nip98_replay, admission_rate_limiter, and redis_pool respectively; these are used directly against Redis and do not go through PubSubManager's pub/sub machinery."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/state.rs"
  - statement: "buzz-relay's /readyz-equivalent readiness_handler checks Postgres (state.db.ping()), Redis (state.redis_pool.get().await.is_ok()), and the deletion-serving catalog concurrently under a 2s timeout, and returns HTTP 503 with a per-check status body if any one of the three fails or the check times out."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs"
  - statement: "buzz-relay periodically polls the Redis pool's status() and emits it as four Prometheus-style gauges: buzz_redis_pool_available, buzz_redis_pool_size, buzz_redis_pool_max, buzz_redis_pool_waiting."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs"
  - statement: "A source comment in buzz-relay's main() states that the ring rustls CryptoProvider is installed up front because it is required before any rustls TLS connection, explicitly naming rediss:// to ElastiCache as one such connection alongside wss:// and S3-over-TLS -- i.e. production/staging Redis is reached over TLS against AWS ElastiCache."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs"
  - statement: ".env.example documents REDIS_URL (default redis://localhost:6379) and BUZZ_REDIS_POOL_SIZE (default 16, commented out) as the two Redis-related environment variables, plus a separate block of shared Redis-backed admission-limit variables."
    entry_class: FACT
    evidence:
      - ".env.example"
  - statement: "The repository's local dev docker-compose.yml runs Redis as image redis:7-alpine, container name buzz-redis, published on 127.0.0.1:6379, health-checked via `redis-cli ping`, with no volume mount configured -- so the local dev container has no persistence across restarts."
    entry_class: FACT
    evidence:
      - "docker-compose.yml"
  - statement: "The Justfile's dev-services readiness check polls `docker inspect` for buzz-redis's health status alongside Postgres before reporting the local stack ready, and TESTING.md states `just test` runs integration tests against both Postgres and Redis."
    entry_class: FACT
    evidence:
      - "Justfile"
      - "TESTING.md"
  - statement: "This repository's own AGENTS.md documents that squareup/block-coder-tf-stacks is the Terraform + ArgoCD project that deploys buzz-relay's Helm chart to the staging Kubernetes cluster; that document does not state whether the same stack also provisions the backing Redis instance, or whether that is owned by separate infrastructure tooling."
    entry_class: FACT
    evidence:
      - "CLAUDE.md"
  - statement: "Every Redis write path inside buzz-pubsub is either a TTL-bounded key (presence: 180s; nip98 replay: caller-supplied ttl; rate-limit counters: window_secs, repaired via EXPIRE if found without one) or a transient pub/sub PUBLISH with nothing persisted -- across the six Redis-touching modules in the crate, none writes a key without an expiry or a script that is not itself pub/sub. This makes Redis a volatile coordination and rate-limiting layer rather than a system of record, consistent with the crash-safety comments in publish_cache_invalidation and publish_conn_control describing a durable Postgres backstop for both."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-pubsub/src/presence.rs"
      - "crates/buzz-pubsub/src/nip98_replay.rs"
      - "crates/buzz-pubsub/src/rate_limiter.rs"
      - "crates/buzz-pubsub/src/cache_invalidation.rs"
      - "crates/buzz-pubsub/src/conn_control.rs"
      - "crates/buzz-pubsub/src/lib.rs"
    confidence: 0.8
  - statement: "crates/buzz-pubsub/src/lib.rs carries a doc comment reading \"Typing indicator tracking in Redis.\" immediately above `pub use error::PubSubError;` -- not above any `pub mod` declaration -- and no `typing` module, file, or Redis key pattern exists anywhere under crates/buzz-pubsub/src/ at the recorded revision, despite the crate's own top-of-file doc comment and Cargo.toml description both naming typing indicators as part of its scope."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/lib.rs"
      - "crates/buzz-pubsub/Cargo.toml"
  - statement: "Issue #659's Definition of done requires that this node state the container's responsibility, technology and ownership boundary; name its inbound/outbound interfaces and directly connected containers/systems; link deployment/data/security implications where relevant; and link implementation paths without duplicating implementation-reference detail."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#659 definition of done, category tail for architecture/containers"
---

# Redis (architecture container)

Buzz's shared, in-memory coordination store. It is not a queue and not the system of
record — Postgres (`buzz-db`) owns durable state. Redis exists so that multiple relay
pods behave as one relay: fanning out realtime events, sharing rate-limit counters and
replay guards, and pushing live enforcement (bans, cache drops) to every pod immediately
instead of waiting for a TTL to expire it locally.

## Responsibility, technology and ownership boundary

**Technology.** Redis 7 (`redis:7-alpine` in local dev; AWS ElastiCache reached over TLS
(`rediss://`) in production/staging, per the `rustls` crypto-provider comment in
`buzz-relay`'s `main()`). Accessed via the `redis` and `deadpool-redis` Rust crates.

**Responsibility.** Five distinct jobs, all owned by the `buzz-pubsub` crate's modules:

| Job | Module | Mechanism |
|---|---|---|
| Cross-pod event fan-out | `lib.rs` (`PubSubManager::publish_event`), `topic.rs` | PUBLISH/SUBSCRIBE on `buzz:{community}:channel:{uuid}` / `buzz:{community}:global` |
| Presence | `presence.rs` | `SET`/`GET`/`DEL` on `buzz:{community}:presence:{pubkey_hex}`, 180s TTL |
| Cross-pod cache invalidation | `cache_invalidation.rs` | PUBLISH/SUBSCRIBE on `buzz:{community}:cache-invalidate` |
| Cross-pod connection control (live ban enforcement) | `conn_control.rs` | PUBLISH/SUBSCRIBE on `buzz:{community}:conn-control` |
| Shared admission state | `nip98_replay.rs`, `rate_limiter.rs` | `SET ... NX EX` (replay guard); Lua `INCR`+`EXPIRE` (rate limiter) |

**Ownership boundary.** `buzz-pubsub` owns every Redis access pattern and key-naming
convention in this table — nothing outside that crate issues a Redis command directly.
`buzz-relay` owns the *lifecycle*: it builds the one shared `deadpool_redis::Pool` from
`config.redis_url`/`config.redis_pool_size`, constructs `PubSubManager` from it, wires
the same pool into `RedisNip98ReplayGuard` and `RedisRateLimiter` on `AppState`, spawns
the three subscriber loops, and reports Redis health on the readiness probe. `buzz-auth`
owns the *interfaces* (`RateLimiter`, `Nip98ReplayGuard` traits) that `buzz-pubsub`'s
Redis-backed types implement — `buzz-auth` itself has zero Redis dependency, which keeps
the auth contract testable against an always-allow stub without Redis running.

`PubSubManager`'s SUBSCRIBE/PSUBSCRIBE loops use their own dedicated (non-pooled) Redis
connections rather than the shared pool, because a pooled connection cannot hold
subscribe state; the pool is reserved for request-path commands (PUBLISH, GET, SET,
INCR, the rate-limit Lua script).

## Inbound / outbound interfaces and directly connected containers

**Nothing outside `buzz-relay` connects to Redis directly.** Desktop, mobile, the CLI
and the web client never open a Redis connection — they reach the relay's WebSocket or
HTTP surface, and the relay is the sole process that speaks to Redis.

| Direction | Interface | Counterparty |
|---|---|---|
| Outbound (relay → Redis) | PUBLISH (events, cache-invalidation, conn-control) | Redis |
| Outbound (relay → Redis) | SET/GET/DEL/EXPIRE, INCR, Lua eval | Redis |
| Inbound (Redis → relay) | SUBSCRIBE/PSUBSCRIBE delivery on the three channel families above | Redis, fed by *any* relay pod's PUBLISH — including this pod's own, deduplicated locally via `AppState.local_event_ids` |
| Health | `state.redis_pool.get()` as one leg of `GET /readyz`'s three-way check (Postgres, Redis, deletion-serving catalog) | Load balancer / orchestrator readiness probe |

Every relay pod is symmetric: each one both publishes and subscribes on all three
channel families, so "directly connected containers" reduces to one edge — **every
`buzz-relay` pod ↔ the one shared Redis instance** — fanned out N-to-1-to-N rather than
peer-to-peer between pods.

## Deployment, data and security implications

**Deployment.** Local dev runs Redis as the `buzz-redis` container in
`docker-compose.yml` (`redis:7-alpine`, port 6379, health-checked, no volume — state does
not survive a container restart). `just dev-services`/`just relay` wait on that
container's health status before starting the relay. In staging, this repository's own
`AGENTS.md` names `squareup/block-coder-tf-stacks` as the Terraform + ArgoCD project that
deploys the relay's Helm chart to the Kubernetes cluster; whether that same stack (or a
separate one) provisions the backing ElastiCache instance is not established by anything
in this repository — see *Scope and omissions*.

**Data implications.** Redis holds no durable Buzz data. Every key this crate writes
either carries a TTL (presence: 180s; NIP-98 replay: caller-supplied window; rate-limit
counters: the configured window, self-repaired if found without an expiry) or is a
transient pub/sub message with nothing stored at all — see the INFERENCE entry above.
Where a Redis operation is fire-and-forget (cache-invalidation and conn-control publishes
are explicitly not awaited for delivery at their call sites), the code's own comments
describe a durable Postgres-backed fallback: a dropped cache-invalidation publish is
backstopped by the REQ denial path's DB confirmation, and a dropped conn-control publish
is backstopped by the durable ban row, which still refuses the banned member's next auth
attempt even if live disconnection on another pod was missed.

**Security implications.** Every Redis key this crate writes is prefixed with the
resolved community id (`buzz:{community}:...`), except the IP-keyed connection-rate
limiter, which is deliberately operator-global (`buzz:ratelimit:ip:{ip}:conn`) rather
than tenant-scoped, since an abusive IP is not a per-community property. The event
fan-out channel is explicitly *not* a confidentiality boundary: `PubSubManager`'s own doc
comment states the topic key is a routing label, and author-private reminder events
(kind:30300) still transit every pod's Redis fan-out because any pod might hold the
author's connection — the actual author-only delivery boundary is
`filter_fanout_by_access` in `buzz-relay`, applied uniformly to both the in-process and
the Redis cross-node fan-out paths, and payload confidentiality is carried by NIP-44
encryption independent of Redis. In short: Redis is trusted only as *transport inside the
relay trust domain*, never as an access-control or encryption boundary in its own right.

## Implementation and verification

Implementation lives in `crates/buzz-pubsub/src/` (all Redis access patterns) and is
wired up in `crates/buzz-relay/src/main.rs` (pool construction, subscriber spawning) and
`crates/buzz-relay/src/state.rs` (`AppState` wiring). The readiness probe is in
`crates/buzz-relay/src/router.rs`. Configuration is documented in `.env.example`
(`REDIS_URL`, `BUZZ_REDIS_POOL_SIZE`); local dev provisioning is in `docker-compose.yml`.
`TESTING.md` documents `just test`'s requirement of a running Redis instance for the
integration suite, and `ARCHITECTURE.md`'s "buzz-pubsub" section carries a fuller,
narrative walkthrough of the same subsystem this node summarizes structurally — this
node does not restate that walkthrough's prose.

## Scope and omissions

**This node covers** what Redis is for in Buzz, which crate/module owns each use, the
interfaces and connected containers, and the deployment/data/security implications
visible from this repository.

**It does not cover, and these are gaps rather than silence:**

- **Whether `squareup/block-coder-tf-stacks` (or a different stack) provisions the
  staging ElastiCache instance itself.** Only that it deploys the relay that depends on
  one. This repository does not contain that Terraform, and it was not inspected.
- **Typing indicators.** `buzz-pubsub`'s own top-of-file doc comment and its
  `Cargo.toml` description both name typing indicators as part of the crate's scope, and
  `lib.rs` even carries a stray doc comment reading "Typing indicator tracking in
  Redis." — but it sits above `pub use error::PubSubError;`, not above any `pub mod`
  declaration, and no `typing` module, file, or Redis key pattern exists anywhere under
  `crates/buzz-pubsub/src/` at the recorded revision. `ARCHITECTURE.md` separately
  describes a `buzz:typing:{channel_uuid}` sorted-set pattern, but that document is a
  narrative walkthrough this node deliberately does not re-verify claim-by-claim, and no
  first-party source in this node's own evidence ledger confirms it. Typing-indicator
  delivery may be implemented elsewhere (e.g. local-only fan-out in `buzz-relay`) or not
  at all — this node does not resolve which, and treats it as unverified.
- **Operational tuning** — ElastiCache instance sizing, eviction policy, maxmemory
  configuration, and failover behavior — none of which is visible from this repository.
- **The rate-limit tier design** (`RateLimitConfig`'s four tiers) beyond the mechanism
  that enforces whichever tier is configured; the tiers themselves are a `buzz-auth`
  concept, not a Redis one, and are out of this container node's scope.

No `relationships` are declared. No other `architecture/containers` sibling node is
merged on `launchpad` at the recorded revision, so there is no corpus id yet to point at;
per `launchpad/docs/corpus/AGENTS.md`, the first sibling node to merge is the point to
revisit this.
