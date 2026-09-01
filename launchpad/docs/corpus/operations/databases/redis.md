---
id: operations-databases-redis
type: operations
status: draft
origin: launchpad
audiences:
  - operator
  - developer
  - agent
evidence:
  - statement: "This node was authored and checked against repository revision 473205a7457b208455f188847bfb27b01aa83cac."
    entry_class: FACT
    evidence:
      - "commit 473205a7457b208455f188847bfb27b01aa83cac"
  - statement: "buzz-pubsub's own Cargo.toml describes the crate as \"Redis pub/sub fan-out, presence, and typing indicators for Buzz\" and depends on the redis and deadpool-redis crates."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/Cargo.toml"
  - statement: "PubSubManager holds a deadpool_redis::Pool plus the Redis connection URL, is constructed via PubSubManager::new / with_config from an existing pool, and its module-level doc comment states its SUBSCRIBE/PSUBSCRIBE loops use a dedicated (non-pooled) redis::aio connection because a pooled connection cannot hold subscribe state, reconnecting with exponential backoff from 1s to 30s."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/lib.rs"
  - statement: "topic.rs defines BUZZ_PREFIX = \"buzz\" and EventTopicKey::redis_channel, which builds buzz:{community}:channel:{channel_id} for one channel's events and buzz:{community}:global for community-wide events; publisher.rs's publish_event PUBLISHes to whichever of the two the caller names and returns the subscriber count."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/topic.rs"
      - "crates/buzz-pubsub/src/publisher.rs"
  - statement: "presence.rs's own module doc states presence is stored as SET buzz:{community}:presence:{pubkey_hex} \"status\" EX 180, with PRESENCE_TTL_SECS = 180 chosen as 3x the 60s client heartbeat so one missed heartbeat does not flap presence; clear_presence issues DEL on clean disconnect rather than waiting on the TTL."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/presence.rs"
  - statement: "presence.rs's own test suite asserts that a Redis connection failure surfaces from get_presence_bulk as an Err rather than a silently-empty Ok, with the test's comment stating this is so a caller returns an error response instead of a fake \"all offline\" snapshot on a backend outage."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/presence.rs"
  - statement: "cache_invalidation.rs carries a pure cache-key drop (never an eviction instruction, per its own module doc) over PUBLISH/SUBSCRIBE on buzz:{community}:cache-invalidate, with the subscriber loop pattern-subscribing to buzz:*:cache-invalidate across every community a pod may have cached locally; conn_control.rs carries the same shape of cross-pod command (DisconnectCommunity, DisconnectPubkey) over buzz:{community}:conn-control / buzz:*:conn-control, and its own module doc states this is deliberately a separate channel because a disconnect is an imperative, non-idempotent action unlike a pure cache-key drop."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/cache_invalidation.rs"
      - "crates/buzz-pubsub/src/conn_control.rs"
  - statement: "RedisNip98ReplayGuard::try_mark_in_scope issues a single SET buzz:{community}:nip98:{event_id_hex} 1 NX EX <ttl>, clamping the caller-supplied ttl_secs to between buzz-auth's DEFAULT_REPLAY_TTL_SECS (120) and MAX_REPLAY_TTL_SECS (3600); its own comments state a pool-acquire or SET failure must cause the caller to \"fail closed\"."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/nip98_replay.rs"
      - "crates/buzz-auth/src/nip98_replay.rs"
  - statement: "RedisRateLimiter runs a single Lua script that atomically INCRs a key and EXPIREs it only on the first increment, self-repairing a key found with a negative TTL (broken state from a crash between INCR and EXPIRE) by re-issuing EXPIRE; buzz-auth's rate_limit_key builds buzz:{community}:ratelimit:{pubkey_hex}:{suffix} with suffix one of msg/api/gif/ws/conn (LimitType::key_suffix), and ip_rate_limit_key builds the deliberately operator-global buzz:ratelimit:ip:{ip}:conn."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/rate_limiter.rs"
      - "crates/buzz-auth/src/rate_limit.rs"
  - statement: "buzz-relay-mesh's registry.rs stores a remote-agent-compute readiness record at mesh:ready:{runtime_id} (READY_KEY_PREFIX = \"mesh:ready:\") via SET ... EX, with the TTL computed as the caller's refresh interval multiplied by REGISTRY_EXPIRY_MULTIPLIER (3); this key is not under the buzz: prefix any other Redis-writing module in this repository uses. ReadyRegistry::publish_ready's own doc comment states callers MUST only invoke it after the relay's own readiness check (Postgres and Redis both reachable) has already passed, and clear_ready removes the entry on clean shutdown while a crash is handled by the key's own TTL expiry."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay-mesh/src/registry.rs"
  - statement: "buzz-deletion's community-deletion pipeline publishes {\"op\":\"DisconnectCommunity\"} to buzz:{community}:conn-control (publish_disconnect_community) and separately purges every key under buzz:{community}:* via repeated SCAN ... MATCH ... COUNT 1000 followed by UNLINK on each page (purge_redis_namespace), then confirms the namespace is empty with two full, clean SCAN passes (verify_redis_absence / scan_proves_absence) before treating a community's Redis state as erased."
    entry_class: FACT
    evidence:
      - "crates/buzz-deletion/src/lib.rs"
  - statement: "buzz-deletion and buzz-admin each read REDIS_URL and BUZZ_REDIS_POOL_SIZE (default 16) from the environment and construct their own deadpool_redis::Pool independently of buzz-relay's, using the identical variable names buzz-relay uses; buzz-core's own Cargo.toml carries a comment stating the crate has \"NO tokio, NO sqlx, NO redis\" — zero I/O dependencies."
    entry_class: FACT
    evidence:
      - "crates/buzz-deletion/src/lib.rs"
      - "crates/buzz-admin/src/main.rs"
      - "crates/buzz-core/Cargo.toml"
  - statement: ".env.example documents REDIS_URL (default redis://localhost:6379) and BUZZ_REDIS_POOL_SIZE (default 16, commented out) under a \"Redis 7\" heading, and separately documents a block of shared Redis-backed admission-limit variables (BUZZ_RATE_LIMIT_HUMAN_MESSAGES_PER_MIN and seven siblings) with the comment \"Shared Redis-backed admission limits.\""
    entry_class: FACT
    evidence:
      - ".env.example"
  - statement: "docker-compose.yml runs Redis as image redis:7-alpine, container name buzz-redis, published on 127.0.0.1:6379, health-checked via redis-cli ping, capped at 128m memory, with no volume mount configured, so the local dev container's data does not survive a container restart; docker-compose.harness.yml runs a second, independent redis:7-alpine instance for the isolated E2E test harness on host port 6471, also with no volume."
    entry_class: FACT
    evidence:
      - "docker-compose.yml"
      - "docker-compose.harness.yml"
  - statement: "TESTING.md states \"just test\" runs integration tests against Postgres and Redis, starting them automatically if not already running, and its configuration table documents REDIS_URL's default as redis://localhost:6379; the Justfile's dev-services readiness check polls docker inspect for buzz-redis's health status alongside Postgres before reporting the local stack ready."
    entry_class: FACT
    evidence:
      - "TESTING.md"
      - "Justfile"
  - statement: "This repository's own Helm chart, deploy/charts/buzz, declares an optional CloudPirates redis chart dependency (version 0.30.x, oci://registry-1.docker.io/cloudpirates, condition redis.enabled) alongside a postgres dependency; Chart.lock pins the resolved version to 0.30.3."
    entry_class: FACT
    evidence:
      - "deploy/charts/buzz/Chart.yaml"
      - "deploy/charts/buzz/Chart.lock"
  - statement: "deploy/charts/buzz's templates/_validate.tpl fails template rendering outright when the chart's computed minimum replica count exceeds 1 unless redis.enabled, externalRedis.url, or secrets.existingSecret is set, with the failure message naming buzz-pubsub as the reason Redis is required at that replica count; templates/secret-chart.yaml composes REDIS_URL as redis://:<password>@<release>-redis:6379 from an autogenerated or pre-existing redis-password when redis.enabled is true, or passes externalRedis.url through verbatim otherwise."
    entry_class: FACT
    evidence:
      - "deploy/charts/buzz/templates/_validate.tpl"
      - "deploy/charts/buzz/templates/secret-chart.yaml"
  - statement: "The chart's own README.md states plainly that replicaCount > 1 hard-requires Redis for buzz-pubsub fan-out and that the chart \"template-fails\" rather than silently degrading when that invariant is broken, lists Redis among the three external services (Postgres/Redis/S3) the production profile expects to be externally managed, and lists exactly four things an operator must back up (the relay private key, the PostgreSQL database, the S3 media bucket, and the git PVC) with Redis absent from that list."
    entry_class: FACT
    evidence:
      - "deploy/charts/buzz/README.md"
  - statement: "buzz-relay's readiness handler checks Postgres (state.db.ping()), Redis (state.redis_pool.get().await.is_ok()), and the deletion-serving catalog concurrently under a 2-second timeout, returning HTTP 503 with a per-check status body if any one of the three fails or the check times out."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs"
  - statement: "buzz-relay's admission::check_principal maps any Err from the RateLimiter trait's check_and_increment (which includes a Redis pool-acquire or Lua-script failure) to AdmissionError::Unavailable, a distinct error variant returned instead of Ok(()) — i.e. a Redis outage denies the admission check rather than allowing it through."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/admission.rs"
  - statement: "buzz-relay's check_nip98_replay_with_guard maps a try_mark Err into HTTP 401 with body \"NIP-98: replay check unavailable\", logging \"NIP-98 replay guard failed; rejecting request fail-closed\"; this function gates NIP-98-authenticated HTTP bridge endpoints including those in api/gifs.rs, api/workflows.rs and api/invites.rs in addition to api/bridge.rs's own routes."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs"
      - "crates/buzz-relay/src/api/gifs.rs"
      - "crates/buzz-relay/src/api/workflows.rs"
      - "crates/buzz-relay/src/api/invites.rs"
  - statement: "buzz-relay's event-submission handler still marks an event as durably stored and still fans it out to same-pod local subscribers (via sub_registry.fan_out_scoped) when the subsequent Redis PUBLISH for cross-pod fan-out fails; the failure is only logged as a warning (\"Redis publish failed\") and the pod's own already-published marker for that event is invalidated so a later Redis-delivered copy is not mistakenly dropped as a duplicate."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs"
  - statement: "A cross-pod event-fan-out failure therefore degrades multi-pod delivery (other pods' locally-connected subscribers do not receive the live copy over Redis) without causing data loss or blocking the write, because the event was already persisted to Postgres before the Redis PUBLISH was attempted and the same-pod fan-out path does not depend on Redis at all."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs"
      - "launchpad/docs/corpus/architecture/containers/redis.md"
    confidence: 0.85
  - statement: "Every Redis-writing module opened for this node either attaches a TTL to a key it writes (presence: 180s fixed; NIP-98 replay: 120s-3600s caller-clamped; rate-limit counters: the caller's configured window, self-repaired if found missing; the mesh readiness registry: refresh interval x3) or writes nothing durable at all (a PUBLISH with no persisted key), which is consistent with the architecture container node's independent finding that Redis holds no durable Buzz data in this repository."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-pubsub/src/presence.rs"
      - "crates/buzz-pubsub/src/nip98_replay.rs"
      - "crates/buzz-pubsub/src/rate_limiter.rs"
      - "crates/buzz-relay-mesh/src/registry.rs"
    confidence: 0.85
  - statement: "Issue #1201's Definition of Done requires this node to be structured for lookup rather than narrative teaching, to contain only facts supported by current source while labelling generated versus authored values, to define scope and omissions, and to link authoritative source/schema/config rather than restate it."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1201 definition of done"
  - statement: "Issues #1219 (\"task: document operations/reliability/redis-failure.md\") and #1226 (\"task: document operations/runbooks/redis-unavailable.md\") are open, unmerged sibling tasks under the same parent Feature at the time this node was written, planned as companion documents to this reference rather than folded into it."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1219 and launchpad-26/buzz#1226, issue titles and open state"
  - statement: "This repository's own AGENTS.md names squareup/block-coder-tf-stacks as the Terraform + ArgoCD project deploying the relay's Helm chart to the staging Kubernetes cluster, without stating whether that chart is this repository's own deploy/charts/buzz or a separate one, and without stating whether that stack (or a different one) provisions the backing Redis instance for staging."
    entry_class: FACT
    evidence:
      - "AGENTS.md"
  - statement: "This node was written using launchpad/docs/corpus/templates/reference.md, which was already merged on origin/launchpad at the recorded revision and directs a reference-shaped node to carry a reference description, structured entries, an optional Commands table, an explicit boundary statement, relationships and a scope-and-omissions section."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/templates/reference.md"
relationships:
  - type: references
    target: architecture-containers-redis
---

# Redis (operations reference)

This node catalogues Redis as an *operated* datastore in Buzz: the key
namespaces and TTLs every Redis-writing crate uses, how the relay and its
sibling processes are configured to reach it, how it is provisioned in local
development, the E2E harness and this repository's own Helm chart, and what
happens operationally when it becomes unreachable. It is a lookup table for
someone running or debugging a Buzz deployment, not an explanation of Redis's
architectural role — for that, see `architecture-containers-redis`
(`launchpad/docs/corpus/architecture/containers/redis.md`), which this node
links rather than restates.

## Key namespaces and TTLs

Every key or channel below was confirmed by reading the module that
constructs it, not inferred from a naming convention. `{community}` is the
resolved community UUID; keys and channels are otherwise plain strings, not
Redis hashes or richer structures.

| Key / channel pattern | Kind | Owning crate / module | TTL / lifetime | Purpose |
|---|---|---|---|---|
| `buzz:{community}:channel:{channel_id}` | pub/sub channel | `buzz-pubsub` (`topic.rs`, `publisher.rs`) | none — nothing persisted, only in-flight PUBLISH | Cross-pod event fan-out scoped to one channel |
| `buzz:{community}:global` | pub/sub channel | `buzz-pubsub` (`topic.rs`, `publisher.rs`) | none | Cross-pod fan-out for community-wide events |
| `buzz:{community}:presence:{pubkey_hex}` | string key | `buzz-pubsub` (`presence.rs`) | 180s fixed (`SET ... EX 180`) | Online/away presence; 3x the 60s heartbeat so one missed beat doesn't flap |
| `buzz:{community}:cache-invalidate` | pub/sub channel (subscriber pattern: `buzz:*:cache-invalidate`) | `buzz-pubsub` (`cache_invalidation.rs`) | none | Cross-pod drop of a stale in-memory (moka) cache key; never an eviction instruction |
| `buzz:{community}:conn-control` | pub/sub channel (subscriber pattern: `buzz:*:conn-control`) | `buzz-pubsub` (`conn_control.rs`); also published to by `buzz-deletion` | none | Cross-pod disconnect commands (`DisconnectCommunity`, `DisconnectPubkey`) for live ban enforcement and community offboarding |
| `buzz:{community}:nip98:{event_id_hex}` | string key | `buzz-pubsub` (`nip98_replay.rs`), key format from `buzz-auth` | 120s–3600s, caller-supplied and clamped (`SET ... NX EX`) | NIP-98 HTTP replay guard; `NX` makes first-claim atomic |
| `buzz:{community}:ratelimit:{pubkey_hex}:{msg\|api\|gif\|ws\|conn}` | counter key | `buzz-pubsub` (`rate_limiter.rs`), key format from `buzz-auth` | the caller's configured window, self-repaired via `EXPIRE` if found missing | Per-principal, per-limit-type fixed-window admission counter |
| `buzz:ratelimit:ip:{ip}:conn` | counter key | `buzz-pubsub` (`rate_limiter.rs`), key format from `buzz-auth` | the caller's configured window | Per-IP connection admission counter, deliberately **not** community-scoped |
| `mesh:ready:{runtime_id}` | string key | `buzz-relay-mesh` (`registry.rs`) | `refresh_interval x 3` (`SET ... EX`) | Remote agent-compute readiness registration; **the one namespace in this repository that is not `buzz:`-prefixed** |
| `buzz:{community}:*` (wildcard) | scan target, not a single key | `buzz-deletion` (`purge_redis_namespace`, `verify_redis_absence`) | n/a — a purge operation, not a stored key | Community-offboarding: `SCAN`+`UNLINK` every key under a community's namespace, confirmed empty by two full clean `SCAN` passes |

A fixed-window rate limiter allows up to roughly 2x burst at its window
boundary; `rate_limiter.rs`'s own module doc flags this and names a sliding
window or token bucket as the upgrade path, not yet implemented.

## Connection configuration

| Variable | Default | Read by | Notes |
|---|---|---|---|
| `REDIS_URL` | `redis://localhost:6379` | `buzz-relay`, `buzz-admin`, `buzz-deletion` (all three via the identical env var name) | `rediss://` (TLS) reaches AWS ElastiCache in staging/production, per the `rustls` `CryptoProvider` install this repository's own `buzz-relay::main()` performs at startup |
| `BUZZ_REDIS_POOL_SIZE` | `16` (commented out in `.env.example`) | `buzz-relay`, `buzz-deletion` | Sizes the shared `deadpool_redis::Pool`; `buzz-relay-mesh`'s `ReadyRegistry` takes an already-constructed pool from its caller rather than reading this variable itself (not independently confirmed which process constructs that pool) |
| `BUZZ_RATE_LIMIT_HUMAN_MESSAGES_PER_MIN` and seven siblings | as listed in `.env.example` | `buzz-auth`'s `RateLimitConfig`, enforced through `buzz-pubsub`'s `RedisRateLimiter` | Per-tier thresholds; the tiers themselves are a `buzz-auth` concept outside this node's scope |

`buzz-core` is the one crate in this dependency graph that deliberately
carries **no** Redis dependency at all — its own `Cargo.toml` states this in
so many words, as part of keeping the crate free of I/O dependencies.

## Provisioning by environment

| Environment | Mechanism | Persistence | Source |
|---|---|---|---|
| Local development | `docker-compose.yml`'s `redis` service — `redis:7-alpine`, container `buzz-redis`, `127.0.0.1:6379`, `redis-cli ping` health check, 128m memory cap | **None** — no volume is mounted; data does not survive `docker compose down`/restart | `docker-compose.yml` |
| Isolated E2E test harness | `docker-compose.harness.yml`'s independent `redis` service, same image, host port 6471 | None — also no volume | `docker-compose.harness.yml` |
| Kubernetes, quickstart/eval profile | This repository's own Helm chart (`deploy/charts/buzz`) bundles an optional CloudPirates `redis` subchart (`redis.enabled=true`), single replica, no HA | Chart-managed; not evaluated further here | `deploy/charts/buzz/Chart.yaml`, `Chart.lock`, `README.md` |
| Kubernetes, production profile | The chart expects `externalRedis.url` or `REDIS_URL` inside `secrets.existingSecret`; `replicaCount > 1` **hard-fails Helm template rendering** unless one of `redis.enabled`, `externalRedis.url` or `secrets.existingSecret` is set | Externally managed; out of this chart's scope | `deploy/charts/buzz/templates/_validate.tpl`, `README.md` |
| Staging (this repository's actual deployment) | `squareup/block-coder-tf-stacks` deploys the relay's Helm chart per this repository's own `AGENTS.md`; whether it is this chart or a different one, and whether it also provisions Redis, is not established here | Unknown from this repository | `AGENTS.md` |

## Behaviour when Redis is unreachable

This table is the operational payoff of the fail-open/fail-closed reading of
each Redis-touching call site; every row was traced to the code path handling
a Redis error, not assumed from the general "Redis is not durable" framing in
`architecture-containers-redis`.

| Subsystem | On a Redis error | Net effect |
|---|---|---|
| Readiness probe | `state.redis_pool.get()` fails inside the 2s readiness check | The relay reports `503` and stops receiving new traffic from a load balancer honoring readiness — existing connections are not dropped by this alone |
| NIP-98 HTTP replay guard | `try_mark` returns `Err`; the caller returns HTTP `401` (`"NIP-98: replay check unavailable"`) and logs "rejecting request fail-closed" | Every NIP-98-authenticated bridge endpoint (events/query/count bridge routes, GIF search, workflow webhooks, invites) stops accepting requests until Redis recovers |
| Shared rate limiter / admission | `check_and_increment` / `check_ip_connection` return `Err`; `admission::check_principal` maps this to `AdmissionError::Unavailable`, a denial rather than `Ok(())` | Rate-limited operations (messages, API calls, WS events, IP connections) are refused rather than allowed through uncounted |
| Presence reads | `get_presence_bulk` surfaces a connection failure as `Err` (verified by the crate's own test) | Callers get an explicit error rather than a false "everyone offline" snapshot |
| Cross-pod event fan-out | The Redis `PUBLISH` in the event-submission handler fails; logged as a warning, the event is already durably stored in Postgres, and same-pod local subscribers still receive it via `fan_out_scoped` | In a single-pod deployment this is invisible. In a multi-pod deployment, other pods' locally-connected clients miss the live copy of that event until they reconnect or re-query — no data is lost |
| Mesh readiness registry | `ReadyRegistry::publish_ready`'s own doc comment requires the caller to have already confirmed the relay's own readiness (Postgres and Redis) before calling it at all | A remote agent-compute runtime cannot register as ready while Redis is down, by construction rather than by error handling |
| Community deletion | `purge_redis_namespace` / `verify_redis_absence` need a working Redis connection to run at all | A community-deletion run cannot complete its Redis-purge step while Redis is unreachable; this blocks completion of the offboarding pipeline rather than silently skipping the purge |

## Boundary

This node does not describe:

- **Why Redis exists in Buzz's architecture, or its ownership boundary and
  connected containers** — that is `architecture-containers-redis`'s subject,
  linked above rather than restated here.
- **How to accomplish a specific operational task step by step** — for
  example, what to run when Redis is actually down, or how to size an
  ElastiCache instance. That is the redis-unavailable runbook (#1226, not yet
  written) and the redis-failure reliability document (#1219, not yet
  written) — both open siblings under the same parent Feature at the time
  this node was written, and neither has a corpus node id to link to yet.
- **`buzz-auth`'s `RateLimitConfig` tier design** — the numeric thresholds
  per tier are that crate's concept; this node covers only the Redis
  mechanism enforcing whichever tier is configured.
- **Whether `squareup/block-coder-tf-stacks` provisions staging's Redis
  instance**, or whether it deploys this repository's own Helm chart at all
  — see *Scope and omissions* below.

## Relationships

- `references`: `architecture-containers-redis` — this node's structured
  entries assume the reader already has, or will separately read, that
  node's account of Redis's role and ownership boundary; per
  `relationships.schema.json`, `references` asserts supporting context with
  no ownership or currency dependency, which fits a reference table that
  stays accurate independent of how that node's own framing evolves.

No `relationships` are declared toward the redis-failure or redis-unavailable
documents: neither exists as a corpus node yet, and declaring an edge to an
id no node on `origin/launchpad` carries is a hard validation error per
`launchpad/docs/corpus/AGENTS.md`'s own merge-order rule.

## Scope and omissions

**This node covers** what Redis is used for by every crate in this
repository that opens a direct Redis connection (`buzz-pubsub`,
`buzz-deletion`, `buzz-relay-mesh`, `buzz-admin`), the exact key/channel
patterns and TTLs each one writes, the environment variables that configure
the connection, how Redis is provisioned in local development, the E2E
harness and this repository's own Helm chart, and the traced fail-open versus
fail-closed behaviour of each Redis-dependent code path when Redis is
unreachable.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Redis's architectural role, ownership boundary and connected containers | `architecture-containers-redis` |
| Step-by-step incident response when Redis is down | The redis-unavailable runbook, #1226 (not yet written) |
| Reliability characteristics and failure-mode analysis of Redis in this system | The redis-failure document, #1219 (not yet written) |
| `buzz-auth`'s `RateLimitConfig` tier thresholds and their design rationale | `buzz-auth` itself, out of this reference's scope |
| Whether `squareup/block-coder-tf-stacks` provisions staging's Redis instance, or which Helm chart it deploys | Not established by anything in this repository |
| ElastiCache instance sizing, eviction policy, `maxmemory` configuration and failover behaviour | Not visible from this repository |
| Typing-indicator delivery over Redis, and whether it is implemented at all | Flagged as an open, unverified gap by `architecture-containers-redis` itself; not independently re-checked here |

**Expected but not verified when this node was written:**

- **Which process actually constructs the `deadpool_redis::Pool` that
  `buzz-relay-mesh`'s `ReadyRegistry` is handed.** `registry.rs` accepts an
  already-built pool rather than reading `REDIS_URL`/`BUZZ_REDIS_POOL_SIZE`
  itself, so whether it shares `buzz-relay`'s pool, `buzz-admin`'s, or
  constructs a dedicated one was not traced to its call site.
- **Whether `squareup/block-coder-tf-stacks` deploys this repository's own
  `deploy/charts/buzz` chart or a separately maintained one**, and whether it
  provisions the staging Redis instance itself or points at a pre-existing
  managed one. Neither this repository's `AGENTS.md` nor the chart answers
  this; `squareup/block-coder-tf-stacks` was not opened, since it is a
  separate repository outside this one's scope.
- **Whether the fixed-window rate limiter's documented ~2x burst tolerance
  has ever caused an observed operational issue.** The module doc names it as
  a known limitation and a future upgrade candidate; no incident record was
  found or searched for confirming or denying real-world impact.
- **The exact numeric values of `buzz-auth`'s per-tier `RateLimitConfig`
  defaults beyond what `.env.example` documents** — `RateLimitConfig`'s
  source was not opened, per this node's own boundary decision to leave the
  tier design to `buzz-auth`.
