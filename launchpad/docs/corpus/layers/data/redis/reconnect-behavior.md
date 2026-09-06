---
id: layers-data-redis-reconnect-behavior
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
  - statement: "node.schema.json's type enum has 13 members (architecture, layers, capabilities, platforms, implementation, interfaces-events, verification, operations, development, release, governance, agent, ingestion) and contains no dedicated sub-taxonomy for a data-layer connection pattern; this node uses type: layers per the disclosed batch precedent set by prior layers/data/... documents in this same batch (connection-pool #1092 and dedicated-pubsub-connection #1093, both read directly from PR #1878's branch this session), which override templates/datastore.md's own worked reasoning that a real datastore instance takes type: architecture."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "launchpad/docs/corpus/architecture/containers/redis.md (id architecture-containers-redis, already merged on origin/launchpad) states in its own evidence ledger that buzz-relay spawns three long-running Redis pub/sub subscriber loops, each of which 'reconnects with exponential backoff (1s to 30s) and runs forever once spawned' -- the container-level summary this node's own 'Two reconnect mechanisms' section expands on one side, without repeating the per-connection detail the unmerged dedicated-pubsub-connection.md (#1093) already gives that same fact."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/containers/redis.md"
  - statement: "crates/buzz-pubsub/src/subscriber.rs defines BACKOFF_INITIAL_SECS = 1 and BACKOFF_MAX_SECS = 30, and run_subscriber's loop sleeps for the current backoff, then doubles it capped at BACKOFF_MAX_SECS, resetting to BACKOFF_INITIAL_SECS only after a clean (non-error) stream end; crates/buzz-pubsub/src/cache_invalidation.rs and crates/buzz-pubsub/src/conn_control.rs each define the identical two constants and the identical loop shape, with cache_invalidation.rs's own doc comment stating it 'mirrors' subscriber.rs's reconnect loop."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/subscriber.rs"
      - "crates/buzz-pubsub/src/cache_invalidation.rs"
      - "crates/buzz-pubsub/src/conn_control.rs"
  - statement: "deadpool-redis 0.23.0's vendored source (Cargo.lock pins deadpool-redis to 0.23.0) defines its Manager type with two methods satisfying the deadpool::managed::Manager trait: async fn create, which calls self.client.get_multiplexed_async_connection().await with no AsyncConnectionConfig override, and async fn recycle, which runs a two-command pipeline (UNWATCH, ignored; PING <sequence-number>) against the existing connection via query_async and returns an error (managed::RecycleError) if the PING reply does not echo the sequence number sent."
    entry_class: FACT
    evidence:
      - "read(local vendored dependency source, not tracked by this repository's git history: deadpool-redis-0.23.0/src/lib.rs, pinned by Cargo.lock to version 0.23.0, fetched via the crates.io registry into this repository's Hermit-managed Rust toolchain cache) -> Manager::create calls self.client.get_multiplexed_async_connection().await; Manager::recycle runs an UNWATCH+PING pipeline and returns RecycleError on a mismatched PING reply"
  - statement: "deadpool 0.13.0's vendored source (Cargo.lock pins deadpool to 0.13.0) shows Pool::get calling timeout_get, whose inner loop pops a queued idle object and calls try_recycle on it if one exists, or calls try_create if the queue is empty; try_recycle wraps manager.recycle in the pool's configured recycle timeout and, on any recycle error or timeout, returns Ok(None) rather than propagating the error -- the caller's outer loop then falls through to try_create on the same Pool::get call, so a connection that fails its PING health check is silently discarded and replaced inline, in the same request that discovered it was broken, not retried later by a background task."
    entry_class: FACT
    evidence:
      - "read(local vendored dependency source, not tracked by this repository's git history: deadpool-0.13.0/src/managed/pool.rs, pinned by Cargo.lock to version 0.13.0, fetched via the crates.io registry into this repository's Hermit-managed Rust toolchain cache) -> Pool::get -> timeout_get's inner loop calls try_recycle on a queued idle object or try_create if none is queued; try_recycle returns Ok(None) (not an error) on a failed recycle, falling through to try_create on the same call"
  - statement: "deadpool 0.13.0's vendored src/managed/config.rs defines PoolConfig::new(max_size) as constructing a PoolConfig with timeouts: Timeouts::default(), and Timeouts::default()/Timeouts::new() set create, wait and recycle all to None -- 'no timeouts set,' per that struct's own doc comment; PoolConfig::default() (a different constructor, not used by this repository) is the only path shown in this crate's own source that would populate a non-default value, and this repository does not call it."
    entry_class: FACT
    evidence:
      - "read(local vendored dependency source, not tracked by this repository's git history: deadpool-0.13.0/src/managed/config.rs, pinned by Cargo.lock to version 0.13.0, fetched via the crates.io registry into this repository's Hermit-managed Rust toolchain cache) -> PoolConfig::new(max_size) sets timeouts: Timeouts::default(); Timeouts::default()/::new() set create/wait/recycle all to None"
  - statement: "crates/buzz-relay/src/main.rs constructs the shared Redis pool as `deadpool_redis::Config::from_url(&config.redis_url)` with `cfg.pool = Some(deadpool_redis::PoolConfig::new(config.redis_pool_size))` -- the exact no-timeouts constructor identified above -- then calls `cfg.create_pool(Some(deadpool_redis::Runtime::Tokio1))`; no call in this file or elsewhere in the crates/ tree (checked via grep for `PoolConfig` and `Timeouts`) sets a non-default `wait`, `create` or `recycle` timeout on this pool."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs"
  - statement: "The redis crate (Cargo.lock pins it to 1.2.4, resolving the workspace root Cargo.toml's `redis = { version = \"1.0\", features = [...] }`) defines DEFAULT_CONNECTION_TIMEOUT as Some(Duration::from_secs(1)) and DEFAULT_RESPONSE_TIMEOUT as Some(Duration::from_millis(500)) in src/client.rs; AsyncConnectionConfig::default() (and therefore ::new()) sets both fields to these values, and Client::get_multiplexed_async_connection() -- the exact method deadpool-redis's Manager::create calls -- internally calls get_multiplexed_async_connection_with_config(&AsyncConnectionConfig::new()), inheriting both defaults rather than passing None for either."
    entry_class: FACT
    evidence:
      - "read(local vendored dependency source, not tracked by this repository's git history: redis-1.2.4/src/client.rs, pinned by Cargo.lock to version 1.2.4, fetched via the crates.io registry into this repository's Hermit-managed Rust toolchain cache) -> DEFAULT_CONNECTION_TIMEOUT = Some(Duration::from_secs(1)); DEFAULT_RESPONSE_TIMEOUT = Some(Duration::from_millis(500)); AsyncConnectionConfig::default() sets both; get_multiplexed_async_connection() calls get_multiplexed_async_connection_with_config(&AsyncConnectionConfig::new())"
  - statement: "Because deadpool-redis's Manager::create and Manager::recycle both operate through a connection built with AsyncConnectionConfig's 1-second connection_timeout and 500-millisecond response_timeout defaults, and because those are client-level bounds independent of deadpool's own pool-level Timeouts (which this repository leaves at None, per the entries above), a single Pool::get() call's own retry-on-broken-connection path is bounded to roughly one connection attempt (up to ~1s) plus, if recycling an existing idle connection first, one PING round trip (up to ~500ms) -- not unbounded, despite the pool itself imposing no timeout of its own. This was reasoned from the redis and deadpool-redis crates' own source rather than observed by exercising a real timeout in this session, so it is classified as inference, not directly executed fact."
    entry_class: INFERENCE
    evidence:
      - "read(local vendored dependency source: redis-1.2.4/src/client.rs) -> AsyncConnectionConfig's 1s connection_timeout / 500ms response_timeout defaults, per the FACT entry above"
      - "read(local vendored dependency source: deadpool-redis-0.23.0/src/lib.rs) -> Manager::create/Manager::recycle, per the FACT entry above"
      - "read(local vendored dependency source: deadpool-0.13.0/src/managed/pool.rs) -> Pool::get's try_recycle/try_create fallthrough, per the FACT entry above"
    confidence: 0.7
  - statement: "crates/buzz-pubsub/src/nip98_replay.rs's try_mark_in_scope calls self.pool.get().await and, on error, logs a warning reading 'nip98 replay: redis pool acquire failed -- caller MUST fail closed' before returning AuthError::Internal; crates/buzz-relay/src/admission.rs's check_principal maps any Err from the underlying RateLimiter trait call (which crates/buzz-pubsub/src/rate_limiter.rs's RedisRateLimiter implements via its own pool.get()) to AdmissionError::Unavailable, logged via tracing::warn!; neither call site wraps its own pool.get() in an additional timeout beyond whatever the pool and the underlying redis client already impose."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/nip98_replay.rs"
      - "crates/buzz-relay/src/admission.rs"
  - statement: "crates/buzz-relay/src/router.rs's readiness_handler runs three checks concurrently under a single `tokio::time::timeout(Duration::from_secs(2), check)`, one of which is `async { state.redis_pool.get().await.is_ok() }`; a timeout on the outer future collapses all three checks to false regardless of which one was slow, and the handler returns HTTP 503 with a per-check JSON body (`\"redis\": redis_ok`) unless every check passed within the 2-second window -- this 2-second bound belongs to the caller (the readiness handler), not to the pool or the redis client themselves."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs"
  - statement: "A direct `grep -rn \"ConnectionManager\"` across the crates/ tree at the recorded revision finds no use of redis::aio::ConnectionManager (the type the workspace's redis dependency's enabled connection-manager Cargo feature provides, per redis-1.2.4/src/aio/connection_manager.rs) anywhere in this repository's Redis-touching code; every match is the unrelated, identically-named crates/buzz-relay/src/state.rs::ConnectionManager, a WebSocket connection registry with no relationship to Redis. Neither the pooled path (deadpool-redis's Manager::create, which calls Client::get_multiplexed_async_connection, not ConnectionManager::new) nor the three dedicated pub/sub connections (Client::open(...).get_async_pubsub(), per subscriber.rs/cache_invalidation.rs/conn_control.rs) constructs a redis::aio::ConnectionManager."
    entry_class: FACT
    evidence:
      - "grep(-rn, 'ConnectionManager', 'crates/') -> only crates/buzz-relay/src/state.rs hits (unrelated WebSocket registry type) and this node's own cited pooled/dedicated construction call sites"
  - statement: "redis-1.2.4/src/client.rs's get_async_pubsub method (used by all three dedicated connections) calls self.get_simple_async_connection_dynamically(&DefaultAsyncDNSResolver) directly, with no AsyncConnectionConfig parameter of its own -- unlike get_multiplexed_async_connection, which threads AsyncConnectionConfig::default()'s 1-second connection_timeout through explicitly. Whether get_simple_async_connection_dynamically's underlying TCP connect is bounded by an equivalent default, a different default, or no timeout at all was not traced further in this session."
    entry_class: FACT
    evidence:
      - "read(local vendored dependency source, not tracked by this repository's git history: redis-1.2.4/src/client.rs, pinned by Cargo.lock to version 1.2.4, fetched via the crates.io registry into this repository's Hermit-managed Rust toolchain cache) -> get_async_pubsub calls get_simple_async_connection_dynamically(&DefaultAsyncDNSResolver) directly, with no AsyncConnectionConfig parameter"
  - statement: "Issue #1096's Definition of Done requires this node to state whether the store is authoritative, derived, cache or transport; describe owned data, key access patterns, lifecycle/retention and consistency semantics; name tenancy/security boundaries and failure behavior; and link schema/migrations/code/tests rather than copying DDL -- the same checklist shape #1092's and #1093's own issues carry."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1096 definition of done, opened directly via gh issue view"
  - statement: "This task's own dispatch brief states that dedicated-pubsub-connection.md (#1093, unmerged PR #1878) already documents reconnect-loss backstop behavior for two of the three dedicated connections, and directs this node to check whether its own scope overlaps with #1093 or is meant to be the general/cross-cutting reconnect story -- resolved, in this node's own Purpose and scope section, as the latter: a cross-cutting comparison of the pooled and dedicated reconnect mechanisms, not a second pass over #1093's own per-connection detail."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "corpus-batch-author dispatch brief for issue #1096, delivered directly in this task's instructions"
relationships:
  - type: part-of
    target: architecture-containers-redis
---

# Redis: reconnect behavior

## Purpose and scope

This node is the general, cross-cutting account of what happens across **all** of
Buzz's Redis connections -- not just one connection type -- when Redis becomes
unreachable and comes back. It exists alongside two connection-type-specific siblings
in this same batch, neither merged at authoring time: `layers/data/redis/connection-pool`
(#1092), which documents the shared `deadpool-redis` pool's sizing, consumers and
observability, and `layers/data/redis/dedicated-pubsub-connection` (#1093), which
documents the three dedicated (non-pooled) pub/sub connections' own reconnect loop,
resubscription-from-local-state behavior, and per-connection backstop for two of the
three loops, in exhaustive detail. **This node does not redo that detail.** Its subject
is the comparison those two siblings do not make: Buzz's Redis usage recovers from a
disconnect through two structurally different mechanisms, and understanding either one
in isolation misses the difference that matters operationally -- one recovers passively,
per request, with no application-level retry loop of its own; the other recovers
actively, via a dedicated background task that retries on its own schedule regardless of
whether any caller is currently asking for a connection.

## Two reconnect mechanisms, compared

**The pooled connection: passive, per-request, no backoff of its own.**
`deadpool-redis`'s `Manager` (the type backing `buzz-relay`'s single shared
`deadpool_redis::Pool`) implements exactly two operations: `create`, which opens a fresh
`redis::aio::MultiplexedConnection` via `Client::get_multiplexed_async_connection()`, and
`recycle`, which runs an `UNWATCH`+`PING` health check against an already-checked-out
idle connection before handing it back out. `deadpool`'s own `Pool::get()` loop calls
`recycle` first if an idle connection is queued; if that health check fails for any
reason (including a broken TCP connection), the connection is silently dropped and the
same `Pool::get()` call falls through to `create`, opening a brand-new connection inline.
**There is no separate reconnect loop, no exponential backoff, and no background task for
the pooled path** -- recovery happens exactly when, and only when, some caller's own
`pool.get()` call next discovers the old connection is broken. If Redis is down between
requests, nothing retries in the background; the pool simply waits for the next caller.

**The dedicated pub/sub connections: active, backgrounded, exponential backoff.**
Each of the three dedicated connections (`crates/buzz-pubsub/src/subscriber.rs`,
`cache_invalidation.rs`, `conn_control.rs`) is owned by a `tokio::spawn`ed background
loop that runs for the relay process's lifetime, independent of whether any caller is
using it. On disconnect, each loop sleeps for a backoff starting at
`BACKOFF_INITIAL_SECS = 1`, doubling on each failed attempt up to
`BACKOFF_MAX_SECS = 30`, and resetting to the initial value only after a *clean*
disconnect. This is a self-driven retry schedule that runs whether or not a message is
currently trying to flow through it -- the opposite shape from the pool's
request-triggered recovery. The resubscription mechanics, the per-connection backstop
differences, and the local desired-topic refcount map that drives what gets
re-subscribed are `dedicated-pubsub-connection.md`'s (#1093) own subject and are not
repeated here.

**Neither path was found to use `redis::aio::ConnectionManager`.** The workspace's
`redis = "1.0"` dependency enables the crate's `connection-manager` Cargo feature, which
provides `redis::aio::ConnectionManager` -- a client-side type with its own built-in
transparent reconnect logic. A direct search of this repository's Redis-touching code
found no construction of that type anywhere: the pooled path builds a
`MultiplexedConnection` via `Client::get_multiplexed_async_connection()`, and the three
dedicated connections build a `PubSub` via `Client::open(...).get_async_pubsub()`.
Both recovery mechanisms described above are this repository's own code, not the `redis`
crate's `ConnectionManager` feature -- the feature flag is enabled but dead. This
resolves a gap #1093's own "Expected but not verified" section named and left open
("whether `redis`'s `connection-manager` feature ... is actually in use on the pub/sub
path specifically ... was not traced into the `redis` crate's own implementation") --
traced here for both connection types, not just the pub/sub path: neither uses it.

## Consequence for callers

**The pool's own reconnect attempt is bounded, but not by the pool.** `PoolConfig::new`
(the constructor `buzz-relay`'s `main()` uses) sets no `wait`, `create` or `recycle`
timeout at the pool level -- `Timeouts::default()` leaves all three `None`. Read in
isolation, that looks like an admission-critical `pool.get()` call (in
`nip98_replay.rs` or `rate_limiter.rs`) could block indefinitely while Redis is
unreachable. It does not, in practice, because the bound comes from a different layer:
the `redis` crate's own `AsyncConnectionConfig` defaults a 1-second connection timeout
and a 500-millisecond response timeout onto every connection `Manager::create` and
`Manager::recycle` build or use, and neither call site overrides those defaults. So a
single `pool.get()` call's worst case is roughly one connection attempt (up to ~1s) plus,
if an idle connection needed recycling first, one `PING` round trip (up to ~500ms) --
bounded, just not by anything this repository configured on the pool itself. This
conclusion follows from reading the `redis` and `deadpool-redis` crates' own source, not
from exercising an actual timeout in this session, and is recorded as inference
accordingly.

**Two different failure-visibility postures follow from the two mechanisms.** The
readiness probe (`readiness_handler` in `router.rs`) imposes its *own* explicit 2-second
`tokio::time::timeout` around `state.redis_pool.get()`, one leg of a three-way concurrent
check with Postgres and a deletion-serving-catalog validation; a timeout on any leg fails
all three and returns HTTP 503. That 2-second bound is the caller's choice, layered on
top of the pool's own implicit ~1.5-second worst case. Admission-critical callers
(`nip98_replay.rs`, `rate_limiter.rs`) impose no timeout of their own beyond what the
pool and the underlying redis client already provide -- both fail closed on any `Err`
from `pool.get()` (`nip98_replay.rs`'s own comment: "caller MUST fail closed"), so a
transient failure denies the one request that hit it rather than hanging it, and the
*next* request gets its own fresh attempt at `create`/`recycle`. The dedicated
connections have no equivalent per-request caller waiting on them at all -- their
recovery is entirely background, and a caller publishing to a topic mid-reconnect
observes only that the message never arrives (a distinct, already-documented failure
mode, per #1093).

## Authoritative, derived, cache, or transport

This node inherits, rather than re-derives, the classification `architecture-containers-redis`
already establishes for Redis as a whole: a volatile coordination and transport layer,
never a system of record, with every write path either TTL-bounded or a bare `PUBLISH`
with nothing persisted. Reconnection is a connection-lifecycle concern layered on top of
that classification, not a reason to revisit it -- neither the pool nor the dedicated
connections hold any state whose "authoritativeness" changes across a reconnect, because
neither holds any durable state at all.

## Owned data and consistency semantics after reconnect

**The pooled path owns no session state to reconcile.** A `MultiplexedConnection` built
fresh by `create()` carries no leftover state from whatever connection it replaced; every
command issued through the pool (`SET`, `GET`, `INCR`, the rate-limit Lua script) is a
single self-contained request-response, so a freshly created connection is immediately as
usable as a long-lived one. There is nothing to "catch up on" after a pooled reconnect --
unlike the dedicated connections, whose consistency-after-reconnect story (rebuilding a
subscription set from a local `desired_topics` map, per #1093) exists specifically
because a `SUBSCRIBE`d channel set *is* state that a fresh connection starts without.
This asymmetry -- the pool has nothing to resynchronize; the dedicated connections have
exactly one thing (their subscription set) -- is itself a fact about why the two
mechanisms differ in shape, not only in schedule.

**Key access patterns are out of this node's scope.** Which keys the pooled and
dedicated connections touch, and their naming convention, is `key-namespacing.md`'s
(#1094, unmerged at this node's authoring time) subject; this node's concern is
connection recovery, not what is stored under which key.

## Tenancy, security boundaries

Out of scope for this node. `architecture-containers-redis` (merged) already states the
community-prefixed key-naming convention that provides Buzz's only tenancy boundary
inside Redis, and `key-namespacing.md` (#1094, unmerged) is expected to own that
convention's full detail. Nothing about *reconnecting* changes which tenant a key
belongs to -- the boundary is enforced by key naming and by parsing logic in the
consuming code, not by anything connection-lifecycle-related.

## Links to code and tests, not copied DDL

Redis has no schema or migration mechanism; the closest equivalent is the module
boundary and the dependency source itself:

- **Pooled path construction and configuration:** `crates/buzz-relay/src/main.rs`
  (`deadpool_redis::Config::from_url`, `PoolConfig::new(config.redis_pool_size)`,
  `create_pool`), `crates/buzz-relay/src/config.rs` (`redis_pool_size` parsing).
- **Pooled path's recycle/create mechanics (vendored dependency source, not this
  repository's own code, cited because it is the actual mechanism):**
  `deadpool-redis-0.23.0/src/lib.rs` (`Manager::create`, `Manager::recycle`),
  `deadpool-0.13.0/src/managed/pool.rs` (`Pool::get`, `try_recycle`, `try_create`),
  `deadpool-0.13.0/src/managed/config.rs` (`PoolConfig::new`, `Timeouts::default`),
  `redis-1.2.4/src/client.rs` (`AsyncConnectionConfig` defaults,
  `get_multiplexed_async_connection`, `get_async_pubsub`) -- all under this repository's
  own `.hermit/rust/registry/src/index.crates.io-1949cf8c6b5b557f/` vendored copy at the
  pinned versions in `Cargo.lock`.
- **Dedicated path's own reconnect loops:** `crates/buzz-pubsub/src/subscriber.rs`,
  `crates/buzz-pubsub/src/cache_invalidation.rs`, `crates/buzz-pubsub/src/conn_control.rs`
  -- detailed in `dedicated-pubsub-connection.md` (#1093), not repeated here.
  `crates/buzz-relay/src/main.rs` is where all three loops are spawned.
  `crates/buzz-pubsub/src/lib.rs`'s `#[ignore = "requires Redis"]` integration tests
  (`test_publish_and_subscribe_roundtrip`, `test_cache_invalidation_roundtrip`, and
  `same_channel_id_in_two_communities_release_one_keeps_other_live`) exercise the
  dedicated-connection subscriber loops, including reconnect/refcount interaction,
  against a real Redis instance.
- **Caller-side failure handling:** `crates/buzz-pubsub/src/nip98_replay.rs`,
  `crates/buzz-pubsub/src/rate_limiter.rs` (fail-closed `pool.get()` error paths),
  `crates/buzz-relay/src/admission.rs` (`AdmissionError::Unavailable`),
  `crates/buzz-relay/src/router.rs` (`readiness_handler`'s 2-second timeout).
- **Dependency pins:** `Cargo.toml` (workspace root: `redis = "1.0"`,
  `deadpool-redis = "0.23"`), `Cargo.lock` (resolved versions: `redis` 1.2.4,
  `deadpool-redis` 0.23.0, `deadpool` 0.13.0).

## Relationships

Declared: **`part-of`** &rarr; `architecture-containers-redis`, the already-merged
container-level node whose own evidence ledger states the one-sentence summary this
node, together with #1092 and #1093, expands. This is the same relationship type and
directionality the sibling `connection-pool.md` (#1092) and `dedicated-pubsub-connection.md`
(#1093) each independently declare for the identical situation.

**No relationship declared toward connection-pool (#1092), dedicated-pubsub-connection
(#1093), key-namespacing (#1094), or the Postgres connection-pool analogue (#1080).**
None of the four exists on `origin/launchpad` at this node's authoring time (confirmed
via `git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus`, which lists
only `architecture/containers/redis.md` under a Redis path); a `relationships[].target`
naming an id nothing carries is a hard validation error per `AGENTS.md`'s own rule. All
four are named in prose above by issue number instead, for whoever authors or merges
them next to complete the edges.

## Scope and omissions

**This node covers** the two structurally different reconnect mechanisms across all of
Buzz's Redis usage (the shared pool's passive, per-request, no-backoff recovery via
`deadpool-redis`'s recycle/create cycle, and the three dedicated connections' active,
backgrounded, exponential-backoff loops, summarized and cross-referenced rather than
re-detailed); the resolved question of whether `redis`'s `connection-manager` feature is
actually used by either path (it is not); what bounds a pooled reconnect attempt in
practice despite the pool itself configuring no timeout; the differing failure-visibility
postures of the readiness probe versus admission-critical callers; and why the pooled
path has no state to resynchronize after a reconnect while the dedicated paths do.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Redis's overall responsibility, technology choice, and container-level deployment/security implications | `architecture-containers-redis` (already merged) |
| The pooled connection's own sizing, consumers, and request-path command set | `layers/data/redis/connection-pool` (#1092), not yet merged |
| The three dedicated connections' own per-connection subscription mechanics, resubscription-from-local-state behavior, and per-connection backstop differences | `layers/data/redis/dedicated-pubsub-connection` (#1093), not yet merged |
| The full Redis key-naming convention and tenancy boundary | `layers/data/redis/key-namespacing` (#1094), not yet written |
| Whether `get_simple_async_connection_dynamically` (used by the dedicated connections' `get_async_pubsub`) has a built-in connect timeout equivalent to the pooled path's 1-second default | Not traced in this session; named below |
| The Postgres connection pool, the analogous durable-store node | `layers/data/postgres/connection-pool` (#1080), not yet merged |

**Expected but not verified when this node was written:**

- **Whether `get_async_pubsub`'s underlying connection attempt (used by all three
  dedicated connections) is bounded by any client-level timeout equivalent to the pooled
  path's `AsyncConnectionConfig`-derived 1-second default.** `get_async_pubsub` calls
  `get_simple_async_connection_dynamically` directly, with no `AsyncConnectionConfig`
  parameter threaded through -- unlike `get_multiplexed_async_connection`, which
  explicitly defaults one. Whether the DNS-resolving connection path it takes has its own
  equivalent bound, a different one, or none was not traced further into the `redis`
  crate's source in this session. If it has no bound, the dedicated connections' own
  outer exponential-backoff loop (which does not itself impose a per-attempt timeout,
  per #1093) would be the only thing preventing one stuck `connect_and_subscribe`
  attempt from hanging past its scheduled backoff -- a real question for whoever traces
  this further, not resolved here.
- **Whether the pool's absent create/recycle/wait timeouts are a deliberate operator
  choice or an unaddressed gap.** No comment in `main.rs`, `config.rs`, or `.env.example`
  states either way, and no environment variable exposes a way to configure them at the
  recorded revision. Named as a real gap, not resolved by guessing at intent -- the same
  treatment `architecture-containers-redis` and #1093 give their own comparable gaps.
  In practice the redis crate's own client-level defaults bound each individual attempt
  (see *Consequence for callers* above), which narrows how much this gap matters but does
  not close it: those defaults could change independently of anything this repository
  controls, since they are the dependency's own choice, not a value this codebase pins.
- **This node's own claims about `deadpool`/`deadpool-redis`/`redis` internals were
  checked against the vendored source in this repository's own `.hermit` toolchain
  directory at the pinned `Cargo.lock` versions, not against upstream documentation or a
  running exercise of an actual timeout.** The source was read directly, not assumed from
  crate documentation, but no test in this session forced an actual Redis-unreachable
  condition to observe the described behavior end to end.
