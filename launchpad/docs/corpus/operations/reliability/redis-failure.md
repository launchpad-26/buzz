---
id: operations-reliability-redis-failure
type: operations
status: draft
origin: launchpad
audiences:
  - operator
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 473205a7457b208455f188847bfb27b01aa83cac."
    entry_class: FACT
    evidence:
      - "commit 473205a7457b208455f188847bfb27b01aa83cac"
  - statement: "buzz-pubsub's own module doc states it implements Redis pub/sub fan-out, presence tracking, and typing indicators using a pooled deadpool-redis connection for commands (PUBLISH, SET, ZADD, etc.) and a separate dedicated, non-pooled redis::aio::PubSub connection for SUBSCRIBE, and states that its subscriber reconnects automatically on Redis disconnect with exponential backoff from 1s up to a 30s maximum."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/lib.rs"
  - statement: "buzz-pubsub's lib.rs declares exactly nine submodules -- cache_invalidation, conn_control, error, nip98_replay, presence, publisher, rate_limiter, subscriber, topic -- none named typing or holding a typing-specific Redis key scheme, even though lib.rs's own crate-level doc comment and error.rs's own enum doc comment both describe typing indicators / typing operations as part of the crate's scope."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/lib.rs"
      - "crates/buzz-pubsub/src/error.rs"
  - statement: "buzz-core defines KIND_TYPING_INDICATOR (20002) as an ephemeral event kind, and ephemeral events are delivered through the same community- and channel-scoped PUBLISH / SUBSCRIBE fan-out (publisher.rs, subscriber.rs) as every other Nostr event -- so a typing indicator depends on Redis exactly as far as ordinary event delivery does, through no Redis structure of its own."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
      - "crates/buzz-pubsub/src/publisher.rs"
  - statement: "run_subscriber (channel-event fan-out), run_cache_invalidation_subscriber, and run_conn_control_subscriber each run an independent, infinite reconnect loop using the identical exponential-backoff constants BACKOFF_INITIAL_SECS = 1 and BACKOFF_MAX_SECS = 30, doubling the delay on each error and resetting to the initial value after a clean stream end."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/subscriber.rs"
      - "crates/buzz-pubsub/src/cache_invalidation.rs"
      - "crates/buzz-pubsub/src/conn_control.rs"
  - statement: "On every reconnect, run_subscriber snapshots the local in-memory desired-topics refcount map -- the stated source of truth across reconnects -- and re-subscribes to every topic with a nonzero count before it resumes processing incoming messages."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/subscriber.rs"
  - statement: "Every Redis pub/sub write in buzz-pubsub (publish_event, publish_cache_invalidation, publish_conn_control) issues a plain redis::cmd(\"PUBLISH\"); no XADD, XREAD, XGROUP or other Redis Streams command appears anywhere under crates/buzz-pubsub/src/."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/lib.rs"
      - "crates/buzz-pubsub/src/publisher.rs"
  - statement: "Because Redis PUBLISH carries no consumer-group or backlog semantics and buzz-pubsub implements no Streams-based alternative, an event published while a given relay pod's dedicated subscribe connection is not yet connected (before initial connect, or mid reconnect-backoff) is not queued for that pod and is never redelivered to it once the connection is re-established."
    entry_class: INFERENCE
    confidence: 0.9
    evidence:
      - "crates/buzz-pubsub/src/subscriber.rs"
      - "crates/buzz-pubsub/src/publisher.rs"
      - "crates/buzz-pubsub/src/cache_invalidation.rs"
      - "crates/buzz-pubsub/src/conn_control.rs"
  - statement: "buzz-relay's state.rs describes revalidate_live_communities as the durable backstop for Redis pub/sub's lossy offline-subscriber semantics, specifically for a missed DisconnectCommunity conn-control message: a pod that missed the publish eventually observes the community's archived row directly by polling Postgres."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/state.rs"
  - statement: "On WebSocket disconnect (connection.rs) and on handling a presence-status event (handlers/event.rs), both clear_presence and set_presence calls discard their Result with `let _ = ... .await;`, so a Redis outage fails these presence writes silently, with no error surfaced to the connection or the client."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/presence.rs"
      - "crates/buzz-relay/src/connection.rs"
      - "crates/buzz-relay/src/handlers/event.rs"
  - statement: "api/bridge.rs's presence-lookup path does not discard a get_presence_bulk failure: it matches Err and returns an explicit internal-error response, with a code comment stating a lookup failure must surface as an error rather than a fake-empty success, precisely so a Redis outage is not indistinguishable from an authoritative all-offline snapshot."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs"
      - "crates/buzz-pubsub/src/presence.rs"
  - statement: "Presence entries carry a fixed 180-second TTL (three times the 60-second client heartbeat interval, by the module's own comment), so there is no active resync of presence state on Redis recovery; a set_presence or clear_presence dropped during an outage is corrected only passively, once that TTL expires the stale or missing entry."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/presence.rs"
  - statement: "RedisRateLimiter::run_rate_limit -- the atomic INCR+EXPIRE Lua script behind check_and_increment and check_ip_connection -- returns Err(AuthError::Internal(...)) when the connection pool cannot hand out a connection or the script invocation itself fails."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/rate_limiter.rs"
  - statement: "buzz-relay's admission::check_principal converts any Err from RateLimiter::check_and_increment into AdmissionError::Unavailable and logs a warning, rather than treating the failure as an implicit allow."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/admission.rs"
  - statement: "All three production call sites of check_principal treat AdmissionError::Unavailable as a rejection: connection.rs's send_admission_result sends a rejection message over the WebSocket and returns false, and api/gifs.rs's enforce_search_admission and api/bridge.rs's enforce_http_admission each return an HTTP error response instead of proceeding."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/connection.rs"
      - "crates/buzz-relay/src/api/gifs.rs"
      - "crates/buzz-relay/src/api/bridge.rs"
  - statement: "RateLimiter::check_ip_connection has no call site anywhere under crates/buzz-relay/src/ outside its own trait definition and two test-only stub implementations, so the relay's live admission path enforces the shared per-principal limiter but not a separate per-IP connection limiter today, whatever a Redis outage would otherwise do to that path."
    entry_class: INFERENCE
    confidence: 0.85
    evidence:
      - "crates/buzz-auth/src/rate_limit.rs"
      - "crates/buzz-relay/src/admission.rs"
  - statement: "RedisNip98ReplayGuard::try_mark_in_scope maps both a Redis pool-acquire failure and a failed SET NX EX into Err(AuthError::Internal(...)), and its own code comments state twice, in matching language, that the caller MUST fail closed on that error."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/nip98_replay.rs"
  - statement: "buzz-relay-mesh's ReadyRegistry module doc states that its Redis-backed entries are membership hints only -- they tell a fresh runtime which peer endpoints to dial but never decide session ownership or takeover -- and names a separately fenced Redis session directory, outside this registry, as the actual arbiter of session generations."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay-mesh/src/registry.rs"
  - statement: "boot_mesh only touches the mesh readiness registry when config.mesh.enabled is true (BUZZ_MESH=on); when disabled it logs single-instance behavior and returns Ok(None) without any Redis interaction for mesh purposes."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/mesh_boot.rs"
  - statement: "When the mesh is enabled, boot_mesh's first ReadyRegistry::publish_ready call propagates any Redis error out of boot_mesh with `?`, and a code comment states this is deliberate: a misconfigured enabled mesh is meant to fail loudly at publish rather than boot silently meshless."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/mesh_boot.rs"
  - statement: "At runtime, reconcile_once's registry.scan_ready() failures and spawn_registry_heartbeat's heartbeat.tick() failures are both handled with tracing::warn! and the loop continues on its normal interval rather than propagating or exiting."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay-mesh/src/runtime.rs"
  - statement: "MeshMembership::apply_ready_records's own doc comment states that existing gossip records win over Redis-sourced bootstrap records when the gossip record is newer, so Redis registry data functions only as an entry hint into an otherwise gossip-driven membership table once peers are talking directly."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay-mesh/src/membership.rs"
  - statement: "buzz-deletion's purge_redis_namespace (SCAN + UNLINK over buzz:{community}:*) runs inside the DeletionStage::PostgresPurged stage handler, and its result is independently re-checked by verify_redis_absence in the following DeletionStage::CachePurged stage."
    entry_class: FACT
    evidence:
      - "crates/buzz-deletion/src/lib.rs"
  - statement: "buzz-deletion's record_stage_failure classifies a stage error as permanent only when it matches PermanentSource, buzz_db::DbError::DeletionSafety, or EngineError::Permanent; any other error -- including a plain Redis pool or connection failure surfaced through `?` out of purge_redis_namespace -- is treated as transient and retried via record_retry on a fixed 30-second RETRY_DELAY."
    entry_class: FACT
    evidence:
      - "crates/buzz-deletion/src/lib.rs"
  - statement: "buzz-deletion's deletion pipeline runs as a lease-claiming loop (run_loop, claim_next / claim_specific) under its own executor id rather than executing inline with the request that triggered a community's deletion, and a code comment states that a separate short database lease per effect is the only durable proof that deletion can drain S3, Redis, and push work across replicas."
    entry_class: FACT
    evidence:
      - "crates/buzz-deletion/src/lib.rs"
  - statement: "buzz-relay's router.rs registers /health and /_liveness as unconditional 200-OK handlers that perform no check of any kind, while /_readiness checks state.db.ping(), state.redis_pool.get().await.is_ok(), and the deletion serving catalog together under a 2-second timeout, returning 503 with an explicit redis:false field the moment the Redis pool cannot hand out a connection."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs"
  - statement: "buzz-relay's main() builds redis_pool via deadpool_redis::Config::from_url(...).create_pool(...), maps a pool-creation error to a fatal anyhow error, and only then constructs PubSubManager::new(&config.redis_url, redis_pool) before spawning the three Redis subscriber tasks."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs"
  - statement: "deadpool_redis builds its pool lazily: a repository test constructs a pool against an unroutable address and the pool-construction call itself succeeds (its own `expect(\"pool builds lazily\")` message), with only the subsequent connection attempt failing."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/presence.rs"
  - statement: "PubSubManager::new / PubSubManager::with_config perform no Redis I/O of their own -- they only construct in-memory tokio broadcast and mpsc channels and store the pool and URL for later use by the subscriber tasks."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/lib.rs"
  - statement: "Combining the lazily-built Redis pool with the I/O-free PubSubManager constructor: a relay started with BUZZ_MESH off does not fail to start merely because Redis is unreachable; its three subscriber tasks instead begin their own reconnect-backoff loops immediately, and only the /_readiness probe reports the outage until Redis returns."
    entry_class: INFERENCE
    confidence: 0.85
    evidence:
      - "crates/buzz-relay/src/main.rs"
      - "crates/buzz-pubsub/src/presence.rs"
      - "crates/buzz-pubsub/src/lib.rs"
  - statement: "mesh_boot.rs's own doc comment states the startup tradeoff directly: a misconfigured enabled mesh (bind failure, Redis unreachable at publish) fails loudly, because an operator who sets BUZZ_MESH=on wants the mesh or wants to know why not -- so a Redis outage is fatal to relay startup only on that opt-in path, never by default."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/mesh_boot.rs"
  - statement: "deploy/charts/buzz/templates/_validate.tpl hard-fails Helm template rendering, via the `fail` function, whenever the chart's computed minimum replica count exceeds 1 and none of redis.enabled, externalRedis.url, or secrets.existingSecret is set, and its failure message names buzz-pubsub as the reason."
    entry_class: FACT
    evidence:
      - "deploy/charts/buzz/templates/_validate.tpl"
  - statement: "deploy/charts/buzz/values.yaml states in comment form that replicaCount > 1 hard-requires Redis for buzz-pubsub (in-cluster or external) directly above a default replicaCount of 1, and the chart's README repeats the requirement and adds that the chart template-fails if the invariant is broken, with no silent degradation."
    entry_class: FACT
    evidence:
      - "deploy/charts/buzz/values.yaml"
      - "deploy/charts/buzz/README.md"
  - statement: "The repository's docker-compose.yml runs Redis as a single redis:7-alpine container with no replication, clustering, Sentinel, or persistence-volume configuration -- a single point of failure by construction, appropriate to its stated local-development purpose."
    entry_class: FACT
    evidence:
      - "docker-compose.yml"
  - statement: "crates/buzz-search's Cargo.toml declares no dependency on redis or deadpool-redis, so a Redis outage has no direct effect on Postgres-FTS query or indexing behavior."
    entry_class: FACT
    evidence:
      - "crates/buzz-search/Cargo.toml"
  - statement: "This node was written using launchpad/docs/corpus/templates/reference.md, which was already merged on origin/launchpad at the recorded revision and directs a reference-shaped node to carry a reference description, structured entries, an optional commands section, an explicit boundary statement, relationships, and a scope-and-omissions section distinguishing what the node excludes from what it could not verify."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/templates/reference.md"
relationships:
  - type: references
    target: architecture-containers-redis
---

# Redis failure: reference

This node catalogues how the Buzz relay behaves when its Redis dependency is
unreachable: which capabilities keep working, which fail open, which fail
closed, which degrade silently, and what happens once Redis comes back. It is
the failure-mode counterpart to
[`architecture-containers-redis`](../../architecture/containers/redis.md),
which documents Redis's normal-path role (pub/sub fan-out, presence, cache
invalidation, connection control, rate limiting, replay protection) without
describing what happens when it is absent. Read that node first for what each
capability does; this node exists for what breaks.

## Redis-dependent capabilities and failure behavior

Two structural facts shape every row below. First, `buzz-pubsub`'s own module
doc states the subscriber side reconnects automatically with exponential
backoff (1s, doubling, capped at 30s), and this exact backoff is duplicated —
constants and all — across the channel-event, cache-invalidation, and
connection-control subscriber loops; each runs forever once spawned, and
resets to the 1-second floor after a clean disconnect. Second, every Redis
write in this crate is a plain `PUBLISH`/`SET`/`INCR`/`SCAN`/`UNLINK` command —
no Redis Streams primitive (`XADD`/`XREAD`/`XGROUP`) appears anywhere under
`crates/buzz-pubsub/src/`. Redis here is a fast, disposable coordination layer,
never a durable queue: a `PUBLISH` sent while a pod's subscriber connection is
down (before initial connect, or mid backoff) is gone the moment it is sent,
with no backlog for that pod to catch up on later.

| Capability | Redis role | On Redis failure | Recovery |
|---|---|---|---|
| Channel event fan-out (`buzz-pubsub::publisher`/`subscriber`) | `PUBLISH`/`SUBSCRIBE` on community- and channel-scoped topics for cross-pod delivery | A `publish_event` call returns `Err`; a down subscriber connection stops receiving cross-pod events for that pod until it reconnects. Messages published during the gap are not queued and are never redelivered. | Subscriber reconnects on its own backoff (1s→30s) and re-subscribes to every topic the pod's local desired-refcount map still holds, using that in-memory map — not Redis — as the source of truth. |
| Presence (`buzz-pubsub::presence`) | `SET`/`DEL`/`GET`/`MGET` with a 180s TTL (3x the 60s heartbeat) | Writes on connect/disconnect and on a presence-status event are fire-and-forget (`let _ = ...`): a failure is silently dropped, with no error surfaced to the connection or the client. Bulk reads (`get_presence_bulk`, used by the presence-synthesis API) are not silenced — a failure returns an explicit internal error rather than a fake all-offline snapshot. | No active resync exists. A dropped write self-heals only passively, once the 180s TTL would have expired the affected key anyway. |
| Typing indicators | None dedicated — `KIND_TYPING_INDICATOR` (20002) is an ephemeral Nostr event carried by the same channel fan-out above | Same as channel event fan-out. There is no separate Redis key or module for typing, despite the crate's own module- and error-doc comments describing "typing indicators" as part of its scope. | Same as channel event fan-out. |
| Cross-pod cache invalidation (`buzz-pubsub::cache_invalidation`) | `PUBLISH` on a per-community cache-invalidate channel | A drop or publish failure means a stale local cache entry is not proactively evicted on other pods. The crate's own module doc states this is recoverable by design: the per-event access gate always re-fetches authoritative state from the database on the next read, so a missed invalidation is a staleness window, not a correctness gap. | Independent reconnect loop, same backoff shape as channel fan-out. |
| Cross-pod connection control (`buzz-pubsub::conn_control`) | `PUBLISH` for `DisconnectCommunity`/`DisconnectPubkey` (live ban enforcement) | A missed `DisconnectPubkey` leaves a banned member's sockets open on other pods until they reconnect and are re-authenticated; the DB ban row is the durable backstop, so the next auth attempt is still refused. A missed `DisconnectCommunity` is separately backstopped: `state.rs`'s `revalidate_live_communities` polls Postgres for each pod's live community sockets and closes any whose community is no longer active — described in its own doc comment as the durable backstop for this exact lossy-offline-subscriber case. | Independent reconnect loop, same backoff shape as channel fan-out, plus the Postgres-polling backstop above. |
| Shared rate limiting (`buzz-pubsub::rate_limiter`, `RateLimiter::check_and_increment`) | Atomic Lua `INCR`+`EXPIRE` fixed-window counter | Fails **closed**: a pool or script error becomes `Err(AuthError::Internal)`, which `admission::check_principal` turns into `AdmissionError::Unavailable` (logged as a warning, never treated as an implicit allow). Every production caller (WebSocket event/message admission, GIF search admission, generic HTTP admission) rejects the request or connection rather than letting it through. | Counting resumes cleanly once Redis is back; fixed-window counters need no resync. A separate repair path re-applies `EXPIRE` if a key is ever found without a TTL from a prior crash between `INCR` and `EXPIRE`. |
| Per-IP connection limiting (`RateLimiter::check_ip_connection`) | Same Lua script, keyed per IP rather than per principal | Not observable in production today: this method has no call site anywhere under `crates/buzz-relay/src/` outside its own trait definition and two test-only stubs, so no live admission path currently depends on it, whatever a Redis outage would otherwise do to it. | N/A — dormant code path. |
| NIP-98 replay protection (`buzz-pubsub::nip98_replay`) | Atomic `SET key 1 NX EX <ttl>` seen-set | Fails **closed**: both a pool-acquire failure and a failed `SET NX EX` become `Err(AuthError::Internal)`; the implementation's own code comments state twice, in matching language, that the caller **MUST** fail closed on that error. | Resumes on the next successful `SET`; the seen-set carries no state to resync. |
| Mesh readiness registry (`buzz-relay-mesh::registry`/`runtime`) | `SET`/`DEL`/`SCAN` of `mesh:ready:{runtime_id}` records, opt-in via `BUZZ_MESH=on` | **At boot**, the first `publish_ready` call is fatal: `boot_mesh` propagates its error with `?`, and a code comment states this is deliberate — a misconfigured enabled mesh should fail loudly rather than boot silently meshless. **At runtime**, `scan_ready` and heartbeat-tick failures are each logged with `tracing::warn!` and the reconcile/heartbeat loop simply continues on its normal interval. The registry's own module doc frames every entry as a dial hint, never the arbiter of session ownership — a separately fenced Redis session directory (out of this node's scope) holds that role — and `MeshMembership::apply_ready_records`'s doc comment notes that live gossip records win over Redis-sourced ones when newer, so the registry matters most for discovering a fresh peer, less once peers are gossiping directly. When `BUZZ_MESH` is not `on` (the default), none of this runs and Redis reachability has no mesh-related effect on startup or runtime. | Runtime resumes normal-interval scanning and heartbeating with no special catch-up: `scan_ready` always returns full current state, so the next scheduled scan after Redis returns is a full resync by construction. |
| Community-namespace purge (`buzz-deletion`) | `SCAN`+`UNLINK` over `buzz:{community}:*`, verified by a second `SCAN` pass | Neither silently skipped nor a hard failure: the deletion pipeline's error classifier treats a plain Redis connection/pool error as transient (it matches none of the pipeline's defined permanent-error variants), so the stage is retried every 30 seconds via the pipeline's own retry/lease mechanism rather than abandoned. | Once Redis is reachable again, the next lease-driven retry attempt completes the purge and its follow-on verification stage; no manual intervention is required for the Redis portion specifically. |

Every "On Redis failure" cell above describes the **current, as-built**
behavior, not a documented contract that all of it was designed together
against; several of the rows are the read author's own synthesis of what a
given code path does when a specific Redis call errors, not a single
authoritative source stating the whole failure mode in one place.

## Startup and readiness

`buzz-relay`'s Redis pool is built with `deadpool_redis::Config::create_pool`,
which constructs lazily and does not itself dial Redis; `PubSubManager::new`
performs no Redis I/O either, only building in-memory channels. So **with
`BUZZ_MESH` off (the default), the relay does not fail to start merely because
Redis is unreachable** — it starts, and its three Redis subscriber tasks begin
their own reconnect-backoff loops immediately. The only startup path where a
Redis outage is fatal is the opt-in mesh path: `boot_mesh`'s first
`publish_ready` call is not backed by a retry, and its error is propagated to
process exit by design.

Once running, `/health` and `/_liveness` are unconditional `200 OK` — they
check nothing and would report healthy through an indefinite Redis outage.
`/_readiness` is the one endpoint that checks Redis: under a 2-second timeout
it checks Postgres, `state.redis_pool.get().await.is_ok()`, and the deletion
serving catalog together, returning `503` with an explicit `"redis": false`
field the moment the pool cannot hand out a connection. A deployment that
gates traffic on liveness alone, rather than readiness, will not detect a
Redis outage through this probe at all.

## Multi-replica requirement

The Helm chart in this repository (`deploy/charts/buzz/`) hard-fails at
template-render time — not merely documents — the coupling between multiple
relay replicas and Redis: `templates/_validate.tpl` calls Helm's `fail`
whenever the chart's computed minimum replica count exceeds 1 and none of
`redis.enabled`, `externalRedis.url`, or `secrets.existingSecret` is set,
naming `buzz-pubsub` as the reason. `values.yaml` and the chart's `README.md`
both restate the same requirement and note there is no silent-degradation
path: a multi-replica deployment either has Redis configured or the chart
refuses to render. Locally, `docker-compose.yml` runs a single
`redis:7-alpine` container with no replication or clustering — appropriate to
its single-relay-instance development purpose, and not a configuration this
node's multi-replica finding applies to.

## Commands

Not applicable — this subject has no CLI or code-block command surface of its
own; the relevant surface is the HTTP probe endpoints and Helm values covered
above.

## Boundary

This node does not describe:

- **Why Redis was chosen for these capabilities, or how each is designed to
  work under normal operation** — that is
  [`architecture-containers-redis`](../../architecture/containers/redis.md)'s
  subject, which this node deliberately does not restate; a description of
  mechanism above exists only where needed to make a failure-mode claim
  legible.
- **The operator's step-by-step response to a live Redis outage** —
  diagnosis, escalation, mitigation, recovery verification. That is the
  runbook's subject (tracked separately from this node; see *Scope and
  omissions*), not this reference table.
- **Huddle audio's own Redis-backed session-fencing mechanism.** `registry.rs`'s
  module doc names a separately fenced Redis session directory as the arbiter
  of mesh session generations, distinct from the readiness registry this node
  covers; that mechanism's own failure behavior was not investigated here.

## Relationships

- references: [`architecture-containers-redis`](../../architecture/containers/redis.md) — the normal-path description this node's failure-mode catalogue is the counterpart to.

## Scope and omissions

**This node covers** which Buzz relay capabilities depend on Redis
(`buzz-pubsub`'s channel-event fan-out, presence, typing-indicator delivery,
cache invalidation, connection control, shared rate limiting, per-IP rate
limiting, and NIP-98 replay protection; the mesh readiness registry; and
`buzz-deletion`'s community-namespace purge), whether each fails open or
closed, what is silently lost versus merely delayed, how each subsystem
reconnects and resyncs once Redis returns, whether the relay process itself
survives a Redis outage at startup and at runtime, what the readiness and
liveness probes actually check, and the Helm chart's hard multi-replica/Redis
coupling.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The operator's response procedure for a live Redis outage — diagnosis, escalation, mitigation steps, recovery verification | sibling runbook issue `launchpad-26/buzz#1226` ("redis-unavailable"), not yet merged at the recorded revision |
| Redis's normal-path role and design rationale for each capability | `architecture-containers-redis` |
| The huddle-audio session-fencing mechanism's own Redis dependency and failure behavior | not investigated in this task; flagged above as a boundary, not a filed task |
| Whether `RateLimiter::check_ip_connection` being uncalled today is intentional, a regression, or pending wiring | not determined here — reported as an observation, not a judgement, since deciding it is implementation work outside a documentation task |
| Production behavior of Redis under partial degradation (elevated latency short of outright unreachability, memory pressure, eviction) | not investigated; every finding above concerns outright unreachability (connection/pool failure), not degraded-but-reachable Redis |

**Expected but not verified when this node was written:**

- **None of the failure paths above were exercised against a real, deliberately
  killed Redis instance.** Every claim rests on reading the handling code (the
  `Err` arm, the retry classifier, the reconnect loop) and, for the two
  `INFERENCE` entries, on the absence of a Streams primitive and the absence of
  any production call to `check_ip_connection` — not on an observed outage.
  Whether the described behavior matches what an operator would actually see
  under `docker stop buzz-redis` was not tested here.
- **The Kubernetes manifests this Helm chart renders were not checked for how
  `/_readiness` and `/_liveness` are wired into actual liveness/readiness probe
  configuration** — the claim above is limited to what the handler code itself
  does, not to how any deployed probe consumes it.
- **Whether `buzz-relay-mesh`'s fenced Redis session directory (named in
  `registry.rs`'s own doc comment) has failure behavior similar to, or
  different from, the readiness registry described here** was not
  investigated, per the boundary above.
