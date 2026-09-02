---
id: platforms-relay-app-state
type: platforms
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 131b02f989684117d9ab1dd426f1673fa638e523."
    entry_class: FACT
    evidence:
      - "commit 131b02f989684117d9ab1dd426f1673fa638e523"
  - statement: "AppState is a public struct defined in crates/buzz-relay/src/state.rs (lines 630-773), documented at the file's crate-level doc comment as 'Shared application state — Arc-wrapped, shared across all connections' and re-exported from the crate root as pub use state::AppState."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/state.rs:1"
      - "crates/buzz-relay/src/state.rs:628-773"
      - "crates/buzz-relay/src/lib.rs:57"
  - statement: "AppState derives Clone and its own doc comment states it is 'cloned cheaply via inner Arc fields' — every field that needs to be shared across the process is itself an Arc, a moka/DashMap cache, or a Copy-able handle (CancellationToken, Instant, nostr::Keys), so cloning the struct is a shallow, cheap operation rather than a deep copy of relay state."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/state.rs:628-630"
  - statement: "AppState's fields group into: relay configuration and persistence (config: Arc<Config>, db: Db, redis_pool: deadpool_redis::Pool, media_storage: Arc<MediaStorage>, git_store: crate::api::git::store::GitStore, git_pack_cache: Arc<crate::api::git::pack_cache::GitPackCache>); collaborating services (audit: Option<Arc<AuditService>>, pubsub: Arc<PubSubManager>, auth: Arc<AuthService>, search: Arc<SearchService>, workflow_engine: Arc<WorkflowEngine>); connection/session registries (sub_registry: Arc<SubscriptionRegistry>, conn_manager: Arc<ConnectionManager>, community_connections: Arc<CommunityConnectionRegistry>, audio_rooms: Arc<AudioRoomManager>); admission control (conn_semaphore, handler_semaphore, git_semaphore, media_upload_semaphore: all Arc<Semaphore>, plus admission_rate_limiter: Arc<RedisRateLimiter> and several moka/DashMap-backed per-scope rate limiters); in-process caches with TTLs (local_event_ids, membership_cache, accessible_channels_cache, channel_visibility_cache, observer_owner_cache, author_type_cache: all Arc<moka::sync::Cache<...>>); and process-lifecycle/observability state (relay_keypair: nostr::Keys, shutting_down: Arc<AtomicBool>, started_at: Instant, tracer: Arc<dyn buzz_conformance::Tracer>, mesh: Arc<std::sync::OnceLock<crate::mesh_boot::MeshHandle>>)."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/state.rs:630-773"
  - statement: "AppState::new (crates/buzz-relay/src/state.rs, lines 782-956) is the sole constructor. It takes Config, Db, a deadpool_redis::Pool, an optional AuditService, an Arc<PubSubManager>, AuthService, SearchService, an Arc<WorkflowEngine>, a relay signing nostr::Keys, and MediaStorage as parameters, and returns a tuple of (Self, AuditShutdownHandle) rather than Self alone."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/state.rs:775-793"
  - statement: "Inside AppState::new, several fields are derived rather than passed in directly: it spawns a dedicated tokio task that owns the audit worker loop and returns its shutdown handle separately; it constructs a GitStore and a GitPackCache from the passed Config's media/git settings, panicking via .expect(...) if either fails, with comments noting the panics are guarded by media storage already having been constructed against the same S3 config and the pack cache path already being validated available; it wraps the Redis pool in a RedisNip98ReplayGuard and a RedisRateLimiter; and every cache field is built with an explicit moka::sync::Cache::builder() specifying max_capacity and time_to_live (60s for local_event_ids, 10s for the three membership/visibility caches, 300s for observer_owner_cache and author_type_cache)."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/state.rs:794-948"
  - statement: "AppState::new defaults the tracer field to Arc::new(crate::conformance::NoopTracer) and leaves mesh as an empty Arc<OnceLock<..>> — both are described in adjacent doc comments as intentionally not constructor parameters: the tracer is overwritten by conformance tests after construction, and the mesh handle is set exactly once by main.rs after boot_mesh runs, specifically so that AppState::new's own call sites never need to change when the mesh feature is toggled."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/state.rs:760-772"
      - "crates/buzz-relay/src/state.rs:942-947"
  - statement: "crates/buzz-relay/src/main.rs constructs AppState via AppState::new(...) (lines 446-457), immediately wraps the returned value in Arc::new(app_state) (line 458), and later passes Arc::clone(&state) into build_router(...) (line 1014), which in turn is imported from buzz_relay::router (line 22)."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:22"
      - "crates/buzz-relay/src/main.rs:446-458"
      - "crates/buzz-relay/src/main.rs:1014"
  - statement: "crates/buzz-relay/src/router.rs's pub fn build_router(state: Arc<AppState>) -> Router (line 33) is documented as building 'the axum Router with all relay routes, middleware, and CORS configuration', and calls .with_state(state.clone()) (or .with_state(state) for the final move) three times while assembling the media router, the main API router, and a further nested router, so every axum sub-router in the relay is wired against the same shared Arc<AppState>."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs:29-33"
      - "crates/buzz-relay/src/router.rs:47"
      - "crates/buzz-relay/src/router.rs:143"
      - "crates/buzz-relay/src/router.rs:300"
  - statement: "Exactly twelve files under crates/buzz-relay/src/ declare a handler parameter typed axum::extract::State<Arc<AppState>>: api/bridge.rs, api/gifs.rs, api/git/policy.rs, api/git/transport.rs, api/invites.rs, api/media.rs, api/mesh_demo.rs, api/nip05.rs, api/operator.rs, api/workflows.rs, audio/handler.rs, and router.rs itself (e.g. router.rs's own nip11_or_ws_handler at lines 304-305, and api/invites.rs's join_policy at line 112). This is the standard axum State extractor pattern: every HTTP handler that needs relay state receives it as State(state): State<Arc<AppState>> in its function signature, resolved from the Router's with_state(...) call."
    entry_class: FACT
    evidence:
      - "grep_repo(pattern='State<Arc<AppState>>', scope='crates/buzz-relay/src/**/*.rs') -> crates/buzz-relay/src/api/bridge.rs, crates/buzz-relay/src/api/gifs.rs, crates/buzz-relay/src/api/git/policy.rs, crates/buzz-relay/src/api/git/transport.rs, crates/buzz-relay/src/api/invites.rs, crates/buzz-relay/src/api/media.rs, crates/buzz-relay/src/api/mesh_demo.rs, crates/buzz-relay/src/api/nip05.rs, crates/buzz-relay/src/api/operator.rs, crates/buzz-relay/src/api/workflows.rs, crates/buzz-relay/src/audio/handler.rs, crates/buzz-relay/src/router.rs, at commit 131b02f989684117d9ab1dd426f1673fa638e523"
      - "crates/buzz-relay/src/router.rs:304-305"
      - "crates/buzz-relay/src/api/invites.rs:112"
  - statement: "The WebSocket path does not use the axum State extractor for AppState at all: router.rs's nip11_or_ws_handler resolves State<Arc<AppState>> once at the HTTP-upgrade boundary, and crates/buzz-relay/src/connection.rs's pub async fn handle_connection (lines 125-130) instead takes state: Arc<AppState> as a plain function argument, cloned via Arc::clone before being threaded into the per-connection lifecycle machinery (run_registered_community_connection)."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs:304-309"
      - "crates/buzz-relay/src/connection.rs:125-140"
  - statement: "AppState's inherent methods (crates/buzz-relay/src/state.rs, lines 775-1299) fall into three groups: cache-backed read helpers with a DB fallback (is_member_cached, get_accessible_channel_ids_cached, channel_visibility_cached — each checks a moka cache first, falls back to self.db on miss, then repopulates the cache); cache invalidation, each with a `_local` variant that only drops local moka entries and a cluster-wide variant that also fire-and-forgets a Redis publish via spawn_cache_invalidation, so a drop received from another pod (apply_cache_invalidation) can call the local-only variant without re-publishing and causing a fan-out loop (invalidate_membership/_local, invalidate_all_accessible_channels/_local, invalidate_channel_visibility/_local, invalidate_channel_deleted/_local, apply_cache_invalidation); and cluster-wide connection lifecycle actions that combine a pod-local effect with an awaited or fire-and-forget Redis publish (disconnect_pubkey_clusterwide, disconnect_community_clusterwide, revalidate_live_communities, mark_local_event, mesh)."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/state.rs:975-990"
      - "crates/buzz-relay/src/state.rs:998-1147"
      - "crates/buzz-relay/src/state.rs:1149-1234"
      - "crates/buzz-relay/src/state.rs:1236-1298"
  - statement: "AppState::disconnect_pubkey_clusterwide's own doc comment states it is 'the single entry point for live ban enforcement' and that callers 'must not invoke the pod-local conn_manager.disconnect_pubkey directly — doing so closes sockets only on the pod that processed the ban and silently drops the cluster-wide half. Pairing both halves here makes that mistake unrepresentable.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/state.rs:1149-1166"
  - statement: "AppState is exercised by in-crate unit tests: crates/buzz-relay/src/state.rs's own #[cfg(test)] mod tests block (starting line 1366) defines an async test_state() helper (line 1406) that builds a real AppState via a from-env Config with require_relay_membership disabled and a lazily-connected Postgres pool, used as shared setup for the module's tests. This unit-test coverage is against a live-shaped construction of the struct via its real constructor, not a hand-built stub."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/state.rs:1366-1406"
  - statement: "AppState is one node in a container-level architecture decomposition of the relay that this corpus does not yet have a merged node for: at the recorded revision, origin/launchpad's corpus tree under launchpad/docs/corpus/ carries only meta/governance nodes about the corpus itself (AGENTS.md, README.md, standards/confidence.md, standards/decision-references.md, standards/*) and no platforms/, architecture/containers/, or architecture/deployment/ node describing crates/buzz-relay as a whole, so this node has no existing sibling to declare a relationships edge toward."
    entry_class: FACT
    evidence:
      - "git_ls_tree(ref='origin/launchpad', path='launchpad/docs/corpus') -> AGENTS.md, README.md, schema/**, standards/**, at commit 131b02f989684117d9ab1dd426f1673fa638e523, no platforms/ or architecture/containers/ or architecture/deployment/ entries present"
  - statement: "Because AppState centralizes every collaborating service, registry, cache, semaphore, and rate limiter the relay's HTTP and WebSocket handlers depend on behind one Clone-cheap Arc-wrapped struct passed through axum's State extractor (for HTTP) or as a plain function argument (for the WebSocket upgrade path), it functions as the relay's single composition root / dependency-injection container rather than as a data model in its own right — a reader looking for 'what does a relay handler have access to' should start here rather than tracing each service's construction independently."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay/src/state.rs:628-773"
      - "crates/buzz-relay/src/router.rs:29-33"
    confidence: 0.75
---

# Relay AppState

`AppState` is the relay's central shared application-state struct, defined in
`crates/buzz-relay/src/state.rs`. It holds every collaborating service,
registry, cache, semaphore and rate limiter that the relay's HTTP and
WebSocket handlers need, and is threaded through the whole request-handling
path via a single `Arc<AppState>`. This node answers: what does `AppState`
contain, how is it built, and how does a handler actually get access to it.

## Responsibility

`state.rs` opens with the crate-internal doc comment `"Shared application
state — Arc-wrapped, shared across all connections."` `AppState` itself
derives `Clone` with the doc comment `"Shared application state, cloned
cheaply via inner Arc fields"` — every field is either an `Arc`, a
`moka`/`DashMap` cache, or an independently `Clone`-cheap handle
(`CancellationToken`, `Instant`, `nostr::Keys`), so cloning the whole struct
never deep-copies relay state; it copies a bundle of shared handles.

## Field inventory

Grouped by concern (see the struct definition for full doc comments on each
field):

| Group | Fields |
|---|---|
| Configuration and persistence | `config: Arc<Config>`, `db: Db`, `redis_pool: deadpool_redis::Pool`, `media_storage: Arc<MediaStorage>`, `git_store: crate::api::git::store::GitStore`, `git_pack_cache: Arc<crate::api::git::pack_cache::GitPackCache>` |
| Collaborating services | `audit: Option<Arc<AuditService>>`, `pubsub: Arc<PubSubManager>`, `auth: Arc<AuthService>`, `search: Arc<SearchService>`, `workflow_engine: Arc<WorkflowEngine>` |
| Connection/session registries | `sub_registry: Arc<SubscriptionRegistry>`, `conn_manager: Arc<ConnectionManager>`, `community_connections: Arc<CommunityConnectionRegistry>`, `audio_rooms: Arc<AudioRoomManager>` |
| Admission control | `conn_semaphore`, `handler_semaphore`, `git_semaphore`, `media_upload_semaphore` (all `Arc<Semaphore>`), `admission_rate_limiter: Arc<RedisRateLimiter>`, plus `observer_rate_limiter`, `media_upload_rate_limiter`, `invite_claim_rate_limiter`, `media_uploads_in_flight` |
| In-process TTL caches | `local_event_ids`, `membership_cache`, `accessible_channels_cache`, `channel_visibility_cache`, `observer_owner_cache`, `author_type_cache` (all `Arc<moka::sync::Cache<...>>`) |
| Process lifecycle / observability | `relay_keypair: nostr::Keys`, `shutting_down: Arc<AtomicBool>`, `started_at: Instant`, `tracer: Arc<dyn buzz_conformance::Tracer>`, `mesh: Arc<std::sync::OnceLock<crate::mesh_boot::MeshHandle>>`, `community_revalidator_cancel: CancellationToken`, `community_disconnect_publish_attempts: Arc<AtomicU64>` |

Full source: `crates/buzz-relay/src/state.rs:630-773`.

## Construction

`AppState::new` (`crates/buzz-relay/src/state.rs:775-793`) is the sole
constructor. It takes `Config`, `Db`, a `deadpool_redis::Pool`, an optional
`AuditService`, an `Arc<PubSubManager>`, `AuthService`, `SearchService`, an
`Arc<WorkflowEngine>`, a relay signing `nostr::Keys`, and `MediaStorage` as
parameters, and returns `(Self, AuditShutdownHandle)` — the caller must drain
the audit shutdown handle during graceful shutdown so any buffered audit
entries are flushed before the process exits.

Inside the constructor (`state.rs:794-948`):

- A dedicated `tokio::spawn`ed task owns the audit worker loop; its shutdown
  is returned separately as `AuditShutdownHandle` rather than tied to
  `AppState`'s own lifetime.
- `GitStore` and `GitPackCache` are constructed from the passed `Config`'s
  media/git settings. Both use `.expect(...)` on failure — the adjacent
  comments state this is safe because media storage was already constructed
  against the same S3 config, and the pack cache path was already validated
  available.
- The Redis pool is wrapped into a `RedisNip98ReplayGuard` and a
  `RedisRateLimiter`.
- Every TTL cache field is built via an explicit
  `moka::sync::Cache::builder()` with its own `max_capacity` and
  `time_to_live` (60s for `local_event_ids`; 10s for `membership_cache`,
  `accessible_channels_cache`, and `channel_visibility_cache`; 300s for
  `observer_owner_cache` and `author_type_cache`).
- Two fields are deliberately **not** constructor parameters
  (`state.rs:760-772`, `942-947`): `tracer` defaults to
  `Arc::new(crate::conformance::NoopTracer)` and is overwritten by
  conformance tests after construction; `mesh` starts as an empty
  `Arc<OnceLock<..>>` and is set exactly once by `main.rs` after
  `boot_mesh` runs, so toggling the mesh feature never changes
  `AppState::new`'s own call sites.

## Wiring: how a handler actually gets `AppState`

1. `crates/buzz-relay/src/main.rs:446-458` calls `AppState::new(...)` and
   immediately wraps the result in `Arc::new(app_state)`.
2. `main.rs:1014` passes `Arc::clone(&state)` into
   `buzz_relay::router::build_router` (imported at `main.rs:22`).
3. `crates/buzz-relay/src/router.rs:33`'s `pub fn build_router(state:
   Arc<AppState>) -> Router` calls `.with_state(state.clone())` (or
   `.with_state(state)` on the final move) three times — at
   `router.rs:47`, `143`, and `300` — while assembling the media router, the
   main API router, and a further nested router. Every axum sub-router in
   the relay is therefore wired against the same shared `Arc<AppState>`.
4. **HTTP handlers** declare `axum::extract::State<Arc<AppState>>` as a
   function parameter, resolved by axum from the `with_state(...)` call.
   Twelve files under `crates/buzz-relay/src/` do this: `api/bridge.rs`,
   `api/gifs.rs`, `api/git/policy.rs`, `api/git/transport.rs`,
   `api/invites.rs`, `api/media.rs`, `api/mesh_demo.rs`, `api/nip05.rs`,
   `api/operator.rs`, `api/workflows.rs`, `audio/handler.rs`, and
   `router.rs` itself (for example `router.rs:304-305`'s
   `nip11_or_ws_handler`, or `api/invites.rs:112`'s `join_policy`).
5. **The WebSocket path is different.** `nip11_or_ws_handler` resolves
   `State<Arc<AppState>>` once, at the HTTP-upgrade boundary. From there,
   `crates/buzz-relay/src/connection.rs:125-130`'s `pub async fn
   handle_connection` takes `state: Arc<AppState>` as a **plain function
   argument**, not an axum extractor — it is `Arc::clone`d and threaded
   through the per-connection lifecycle machinery
   (`run_registered_community_connection`) for the life of the socket.

## Public interface

`AppState`'s inherent methods (`state.rs:775-1299`) fall into three groups:

**Cache-backed reads with a DB fallback** — check a `moka` cache first, fall
back to `self.db` on miss, then repopulate the cache:
- `is_member_cached` (`state.rs:975-990`)
- `get_accessible_channel_ids_cached` (`state.rs:1236-1254`)
- `channel_visibility_cached` (`state.rs:1272-1298`)

**Cache invalidation**, each with a `_local` variant that only drops local
`moka` entries, and a cluster-wide variant that also fire-and-forgets a Redis
publish via `spawn_cache_invalidation` — so a drop received from another pod
(`apply_cache_invalidation`) can call the `_local` variant directly without
re-publishing and causing a fan-out loop:
- `invalidate_membership` / `invalidate_membership_local` (`state.rs:998-1021`)
- `invalidate_all_accessible_channels` / `_local` (`state.rs:1024-1044`)
- `invalidate_channel_visibility` / `_local` (`state.rs:1047-1060`)
- `invalidate_channel_deleted` / `_local` (`state.rs:1069-1108`)
- `apply_cache_invalidation` (`state.rs:1128-1147`)

**Cluster-wide connection lifecycle**, combining a pod-local effect with an
awaited or fire-and-forget Redis publish:
- `mark_local_event` (`state.rs:969-972`)
- `disconnect_pubkey_clusterwide` (`state.rs:1166-1198`) — its own doc
  comment states it is *"the single entry point for live ban enforcement"*
  and that callers *"must not invoke the pod-local
  `conn_manager.disconnect_pubkey` directly — doing so closes sockets only
  on the pod that processed the ban and silently drops the cluster-wide
  half. Pairing both halves here makes that mistake unrepresentable."*
  (`state.rs:1149-1166`)
- `disconnect_community_clusterwide` (`state.rs:1204-1217`)
- `revalidate_live_communities` (`state.rs:1224-1234`)
- `mesh` (`state.rs:960-962`) — accessor for the `OnceLock`-guarded mesh
  handle described above

## Dependencies

**Depends on** (types `AppState` embeds or constructs): `buzz_audit::AuditService`,
`buzz_auth::{AuthService, Nip98ReplayGuard}`, `buzz_core::tenant::TenantContext`,
`buzz_core::CommunityId`, `buzz_db::Db`, `buzz_media::MediaStorage`,
`buzz_pubsub::{PubSubManager, RedisNip98ReplayGuard, cache_invalidation::CacheInvalidation,
conn_control::ConnControl, rate_limiter::RedisRateLimiter}`, `buzz_search::SearchService`,
`buzz_workflow::WorkflowEngine`, `buzz_conformance::Tracer`, plus in-crate types
`crate::audio::AudioRoomManager`, `crate::config::Config`,
`crate::connection::{ConnectionSubscriptions, RestartClose}`,
`crate::subscription::SubscriptionRegistry`, `crate::api::git::store::GitStore`,
`crate::api::git::pack_cache::GitPackCache`, `crate::mesh_boot::MeshHandle`
(see `crates/buzz-relay/src/state.rs:18-35`).

**Depended on by**: every axum HTTP handler listed above, the WebSocket
connection handler (`crate::connection::handle_connection`), and
`crates/buzz-relay/src/main.rs`, which owns construction and the initial
`Arc` wrap.

## Boundary

This node does not describe:
- The internal behavior of `Config`, `Db`, `PubSubManager`,
  `AuthService`, `SearchService`, `WorkflowEngine`, `MediaStorage`,
  `GitStore`/`GitPackCache`, or the mesh subsystem — each is named here only
  as a field type and a collaborator; its own responsibilities and
  interface belong in that component's own corpus node, none of which are
  merged yet.
- A container-level decomposition of `crates/buzz-relay` as a whole, with a
  diagram — that is architecture-component/-container territory, and no
  such node exists in the merged corpus yet for this node to sit `part-of`.
- Class/function-level design of any one field's implementation beyond what
  is needed to describe `AppState`'s own shape and wiring.
- Runtime/deployment topology (how many relay pods run, Kubernetes
  manifests) — `AppState` is a per-process struct; how many processes run
  it is a deployment concern, not this node's.

## Relationships

None declared. At the recorded revision, `origin/launchpad`'s corpus tree
under `launchpad/docs/corpus/` contains only meta/governance nodes about the
corpus itself (`AGENTS.md`, `README.md`, `standards/*`) — no `platforms/`,
`architecture/containers/`, or `architecture/deployment/` node exists yet
that this node could legitimately target with `part-of`, `depends-on`, or
`references`. Declaring an edge to an unmerged sibling-batch node would
resolve in this worktree but hard-fail validation on `origin/launchpad`
itself, per `AGENTS.md`'s own warning about checking the merge-base tree.
The first `platforms/relay` container-level node, once merged, is the
natural moment to add a `part-of` edge from this node.

## Scope and omissions

**This node covers** the `AppState` struct's field inventory, its
construction path in `AppState::new`, exactly how HTTP and WebSocket
handlers obtain it (axum `State` extractor vs. plain function argument), and
its own inherent methods grouped by what kind of operation they perform.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| `Config`'s own fields and validation | A future component node for `crate::config::Config`, not yet written |
| The mesh subsystem's internal protocol | A future component node for `crate::mesh_boot`, not yet written |
| The git-on-object-storage manifest-pointer protocol | `docs/git-on-object-storage.md` and a future component node for `GitStore`, not yet written |
| A container-level diagram of `crates/buzz-relay` | A future `architecture-component`/`architecture-container` node, not yet written |
| Front-matter contract itself | `launchpad/docs/corpus/schema/node.schema.json` |
| Creating/updating/retiring a corpus node procedurally | `launchpad/docs/corpus/AGENTS.md` |

**Expected but not verified when this node was written:**
- Whether every one of `AppState`'s ~40 fields is reachable from at least
  one of the twelve `State<Arc<AppState>>` handler files, versus some being
  used only from the WebSocket path or background tasks spawned in
  `main.rs`, was not individually traced field-by-field — the wiring
  section above establishes the two access paths that exist, not a
  per-field usage map.
- Whether any other crate outside `buzz-relay` (for example
  `buzz-test-client`) constructs or references `AppState` directly was not
  exhaustively checked beyond the in-crate `#[cfg(test)]` module; none was
  found under `crates/buzz-relay/tests/` or `crates/buzz-test-client/` in a
  targeted search, but that search was not repository-exhaustive.
