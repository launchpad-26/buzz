---
id: platforms-relay-health-server
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
  - statement: "crates/buzz-relay/src/router.rs opens with the crate/module doc comment 'axum routers — app (WebSocket + REST), health (K8s probes), metrics (Prometheus)', and defines two distinct ways the relay exposes health information over HTTP: three routes mounted directly on the main API router built by build_router (`/health`, `/_liveness`, `/_readiness`, at lines 67-70), and a wholly separate build_health_router function (lines 291-301) exposing `/_liveness`, `/_readiness`, `/_status`, and `/_mesh`."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs:1"
      - "crates/buzz-relay/src/router.rs:62-70"
      - "crates/buzz-relay/src/router.rs:291-301"
  - statement: "build_health_router's own doc comment states it builds 'the health-only router for K8s probes (port 8080 in CAKE)' with 'No metrics middleware, no auth, no CORS, no body limit' — in contrast, build_router's returned router has middleware::from_fn(track_metrics), an HTTP trace layer, and a CORS layer applied via .layer(...) calls, none of which apply to the health-only router since it is built and served as a wholly separate axum Router value."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs:291-294"
      - "crates/buzz-relay/src/router.rs:203-206"
  - statement: "health_handler and liveness_handler are both unconditional: each takes no state and always returns (StatusCode::OK, \"ok\"), with no dependency on Postgres, Redis, or the shutdown flag."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs:401-407"
  - statement: "readiness_handler first checks state.shutting_down (an Arc<AtomicBool>) and immediately returns 503 with {\"status\": \"shutting_down\"} if set; otherwise it runs three checks concurrently via tokio::join! — state.db.ping(), state.redis_pool.get().await.is_ok(), and state.db.validate_deletion_serving_catalog().await.is_ok() — under a 2-second tokio::time::timeout that defaults all three to false on timeout, returning 200 with {\"status\": \"ready\"} only if all three succeed, otherwise 503 with a per-check breakdown naming which of postgres/redis/deletion_catalog failed."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs:409-449"
  - statement: "status_handler returns a JSON payload built by status_payload: a fixed \"service\": \"buzz-relay\" field, the crate's Cargo.toml version via env!(\"CARGO_PKG_VERSION\"), uptime in seconds computed from state.started_at.elapsed(), and a nested build object with source_sha/id/url sourced from crate::build_info's three functions."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs:451-467"
  - statement: "crates/buzz-relay/src/build_info.rs's three functions (source_sha, build_id, build_url) each read a compile-time environment variable via option_env! — BUZZ_SOURCE_SHA, BUZZ_BUILD_ID, BUZZ_BUILD_URL respectively — falling back to the literal strings \"unknown\", \"local\", and \"unknown\" when the binary was not built with that variable set, so the /_status build block reflects whatever provenance-aware build tooling (or its absence) baked into this specific binary, not the running host's environment."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/build_info.rs:1-16"
  - statement: "mesh_status_handler returns {\"enabled\": false} when state.mesh() yields None (mesh feature off), and otherwise serializes the mesh handle's own .status() value as JSON, with a fallback error object if serialization fails; its doc comment states this lets operators 'distinguish \"off\" from \"on with zero peers\"'."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs:469-479"
  - statement: "state.rs documents the shutting_down field as 'Set to true on SIGTERM — readiness probe returns 503' and started_at as 'Process start time — used by /_status endpoint', and both fields are initialized once inside AppState::new (shutting_down to Arc::new(AtomicBool::new(false)), started_at to Instant::now())."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/state.rs:714-716"
      - "crates/buzz-relay/src/state.rs:916-917"
  - statement: "crates/buzz-relay/src/config.rs defines health_port: u16 on the relay Config struct, documented as 'TCP port for the health-only router (/_liveness, /_readiness, /_status). Separate from the app router so K8s probes bypass Istio and auth middleware,' populated from the BUZZ_HEALTH_PORT environment variable with a default of 8080 when unset or unparsable."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/config.rs:194-196"
      - "crates/buzz-relay/src/config.rs:818-821"
  - statement: "crates/buzz-relay/src/main.rs imports both build_health_router and build_router (line 22), calls build_health_router(Arc::clone(&state)) once (line 1015 per the earlier grep of this file), and its serve() function (lines 1289-1303) binds a dedicated TCP listener on config.health_port and spawns axum::serve(health_listener, health_router) as its own tokio task — entirely independent of the main app's TCP/UDS listeners bound later in the same function."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:22"
      - "crates/buzz-relay/src/main.rs:1289-1303"
  - statement: "serve()'s own doc comment includes an ASCII diagram naming four listeners the relay binds: TCP app router, optional UDS app router, a separate TCP health-only listener (annotated 'port 8080 in CAKE' elsewhere), and the Prometheus metrics exporter — plus the sequence 'SIGTERM -> shutting_down=true -> readiness 503 -> graceful drain (30s) -> exit'."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:1244-1257"
  - statement: "The shutdown sequence is wired concretely: shutdown_signal() (lines 1449-1463) awaits either ctrl_c or a Unix SIGTERM signal; the moment it resolves, the spawned task at line 1336 immediately does shutdown_flag.store(true, Ordering::Relaxed) (line 1338) before any further delay, so readiness_handler's shutting_down check observes the flag as soon as the signal is caught — strictly before the subsequent 5-second sleep and 30-second drain described in the same task."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:1336-1343"
      - "crates/buzz-relay/src/main.rs:1449-1463"
  - statement: "track_metrics's own doc comment states it 'Skips health/metrics paths (/_*, /health) to avoid polluting dashboards', and its body matches any MatchedPath starting with \"/_\" or equal to \"/health\" or \"/metrics\" and returns early via next.run(req).await without recording the http_requests_total/http_request_latency_ms metrics that the rest of the function records for every other route; this middleware is applied only to the router built by build_router (via .layer(middleware::from_fn(track_metrics)) at router.rs:204), never to build_health_router's returned Router, which carries no such layer at all."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/metrics.rs:155-179"
      - "crates/buzz-relay/src/router.rs:204-206"
  - statement: "One conformance test (crates/buzz-test-client/tests/conformance_multitenant.rs, lines 578-581) cites the main API router's full route list, including /health, /_liveness, and /_readiness, as evidence that no token-minting route exists on the wire; this is the only reference to these route paths found in either crates/buzz-relay/tests/ or crates/buzz-test-client/tests/, and no test file directly exercises build_health_router, liveness_handler, readiness_handler, status_handler, or mesh_status_handler."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/conformance_multitenant.rs:578-581"
  - statement: "Because readiness_handler is the only one of the four health-only-router endpoints whose response depends on live external state (Postgres and Redis connectivity, plus a deletion-serving-catalog check), and because it is the endpoint a Kubernetes readiness probe uses to decide whether to route traffic to a pod, it is the health surface's single point of contact with the relay's actual operational health — liveness, status, and mesh all report either constants or purely in-process state (uptime, compiled-in build identity, mesh peer table) with no external dependency that could make the process itself unresponsive."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay/src/router.rs:401-449"
    confidence: 0.8
  - statement: "Issue #1272's Definition of Done requires (among other bullets) that the node 'states responsibility and well-defined interface/boundary', 'names dependencies and collaborators', 'links source implementation and tests', and 'explains only component-level behavior, not the entire containing platform.'"
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1272 definition of done"
  - statement: "At repository revision 131b02f989684117d9ab1dd426f1673fa638e523, no platforms/** node is merged onto origin/launchpad (git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus/platforms returns no entries), even though several sibling platforms/relay/* nodes (e.g. platforms-relay-app-state, platforms-relay-admission) exist as committed content on their own unmerged task branches; those sibling branches establish the type: platforms convention this node follows, but are not valid relationships targets because they do not exist on the branch being merged into."
    entry_class: FACT
    evidence:
      - "git_ls_tree(ref='origin/launchpad', path='launchpad/docs/corpus/platforms') -> no entries, at commit 131b02f989684117d9ab1dd426f1673fa638e523"
---

# Relay health server

The relay exposes its process health over plain HTTP through two distinct
surfaces defined in `crates/buzz-relay/src/router.rs`: a small set of routes
mounted directly on the main API router, and a wholly separate health-only
router served on its own TCP port for Kubernetes probes. This node answers:
what each health endpoint checks and returns, how the two surfaces differ,
how the health-only router is wired into the process at startup, and how it
participates in graceful shutdown.

**A note on `type` and template.** This node lives under `platforms/relay/`
and uses `type: platforms`, matching every already-authored sibling node
under `platforms/**` at the time of writing (`platforms-relay-app-state`,
`platforms-relay-admission`, and roughly forty others across relay, desktop,
mobile, cli, and agents). The merged `templates/component.md` template's own
text recommends `type: implementation` for a single-component node; this
node follows the batch's established `platforms` convention instead, since no
accepted decision was found settling which of the two is the corpus's final
answer for this path shape, and no sibling node is merged onto
`origin/launchpad` yet to defer to as binding precedent (see *Relationships*
below).

## Responsibility

The health server's job is to answer three separate questions cheaply and
without touching the relay's authenticated request path: is the process
alive (liveness), is it safe to route traffic to (readiness), and what build
is running (status) — plus, when the inter-relay mesh feature is on, whether
this node's mesh peer connections are healthy. `build_health_router`'s own
doc comment states it builds "the health-only router for K8s probes (port
8080 in CAKE)" with "No metrics middleware, no auth, no CORS, no body limit"
— it is deliberately the cheapest, least-gated path into the process.

## The two surfaces

1. **Mounted on the main API router.** `build_router`'s `api_router` includes
   `/health`, `/_liveness`, and `/_readiness` directly (`router.rs:67-70`),
   served on the same TCP/UDS listener(s) as the rest of the Nostr HTTP
   bridge, WebSocket upgrade, media, and git surfaces. These three routes
   pass through the same middleware stack as every other route on that
   router — `track_metrics`, an HTTP trace layer, and CORS
   (`router.rs:203-206`) — except that `track_metrics` explicitly excludes
   them from metrics recording (see *Metrics exclusion* below).
2. **A dedicated health-only router**, built by `build_health_router`
   (`router.rs:291-301`) and exposing `/_liveness`, `/_readiness`,
   `/_status`, and `/_mesh`. This router carries no metrics middleware, no
   auth, no CORS layer, and no body-size limit — it is a bare `Router::new()`
   with four routes and `.with_state(state)`, nothing else layered on top.
   `main.rs` binds it on its own TCP listener, on `config.health_port`
   (`BUZZ_HEALTH_PORT`, default `8080`), entirely independent of the main
   app's listener(s) (`main.rs:1289-1303`). The config field's own doc
   comment states the reason: "Separate from the app router so K8s probes
   bypass Istio and auth middleware" (`config.rs:194-196`).

`/_liveness` and `/_readiness` are therefore reachable on *both* surfaces
with identical handler functions; `/_status` and `/_mesh` exist only on the
health-only router, and plain `/health` exists only on the main router.

## Handlers

| Route | Handler | What it checks | Response |
|---|---|---|---|
| `/health` (main router only) | `health_handler` | nothing | always `200 "ok"` |
| `/_liveness` (both routers) | `liveness_handler` | nothing | always `200 "ok"` |
| `/_readiness` (both routers) | `readiness_handler` | `shutting_down` flag; Postgres via `db.ping()`; Redis via `redis_pool.get()`; `db.validate_deletion_serving_catalog()` — all under a 2s timeout | `200 {"status":"ready"}` or `503` with a per-check breakdown, or `503 {"status":"shutting_down"}` |
| `/_status` (health-only router only) | `status_handler` | nothing external | `200` with service name, `Cargo.toml` version, uptime, and compiled-in build identity (`source_sha`/`id`/`url`) |
| `/_mesh` (health-only router only) | `mesh_status_handler` | mesh handle presence | `{"enabled": false}` when mesh is off, else the mesh handle's own serialized status |

**`readiness_handler`** (`router.rs:409-449`) is the one endpoint whose
answer depends on live external state. It first checks
`state.shutting_down` (an `Arc<AtomicBool>`) and returns `503
{"status": "shutting_down"}` immediately if set — before running any other
check. Otherwise it runs three checks concurrently via `tokio::join!`:
`state.db.ping()`, `state.redis_pool.get().await.is_ok()`, and
`state.db.validate_deletion_serving_catalog().await.is_ok()`, all wrapped in
a 2-second `tokio::time::timeout` that defaults every check to `false` on
timeout. Only if all three succeed does it return `200 {"status": "ready"}`;
otherwise `503` with a JSON object naming which of `postgres`, `redis`, and
`deletion_catalog` failed.

**`liveness_handler`** and **`health_handler`** (`router.rs:401-407`) are
both unconditional — no state parameter, always `200 "ok"`. They exist so a
process that is alive but temporarily not ready (mid-drain, or with a
transient DB/Redis blip) is not killed and restarted by a liveness probe,
only deprioritized for traffic by a readiness probe — the standard
Kubernetes liveness/readiness distinction.

**`status_handler`** (`router.rs:451-467`) reports `service`,
`env!("CARGO_PKG_VERSION")`, uptime computed from `state.started_at`, and a
`build` object populated from `crate::build_info`'s three functions. Each of
those reads a compile-time environment variable via `option_env!` —
`BUZZ_SOURCE_SHA`, `BUZZ_BUILD_ID`, `BUZZ_BUILD_URL` — falling back to
`"unknown"`, `"local"`, and `"unknown"` respectively when the binary was
built without them set (`build_info.rs:1-16`). The reported build identity
therefore reflects whatever provenance the build pipeline baked into this
specific binary, not the current process environment.

**`mesh_status_handler`** (`router.rs:469-479`) returns
`{"enabled": false}` when `state.mesh()` is `None` (the inter-relay mesh
feature is off), and otherwise serializes the mesh handle's own `.status()`
value, with a fallback error object on a serialization failure. Its doc
comment states this lets operators "distinguish 'off' from 'on with zero
peers'".

## Shutdown integration

`shutting_down` is documented on `AppState` as "Set to `true` on SIGTERM —
readiness probe returns 503" (`state.rs:714-715`) and starts as `false`
(`state.rs:916`). `main.rs`'s `serve()` spawns a task
(`main.rs:1336-1343`) that awaits `shutdown_signal()` — which itself awaits
either `ctrl_c` or a Unix `SIGTERM` (`main.rs:1449-1463`) — and, the moment
that resolves, immediately does `shutdown_flag.store(true,
Ordering::Relaxed)` (`main.rs:1338`), strictly before the subsequent 5-second
grace sleep and 30-second drain the same task then runs. This means
`readiness_handler` starts returning `503` as soon as the signal is caught,
giving Kubernetes the earliest possible signal to stop routing new traffic,
while `liveness_handler` keeps returning `200` throughout the entire drain —
the process is not killed early just because it is draining. `serve()`'s own
doc comment carries an ASCII diagram naming this sequence explicitly:
"SIGTERM -> shutting_down=true -> readiness 503 -> graceful drain (30s) ->
exit" (`main.rs:1244-1257`).

## Metrics exclusion

`track_metrics` (`crates/buzz-relay/src/metrics.rs:155-179`) — the
middleware layered onto the main API router only
(`router.rs:204-206`) — states in its own doc comment that it "Skips
health/metrics paths (`/_*`, `/health`)" and its body matches any
`MatchedPath` starting with `/_` or equal to `/health` or `/metrics`,
returning early without recording the `http_requests_total` /
`http_request_latency_ms` metrics the same function records for every other
route. This applies only to the three health routes mounted on the main
router; the health-only router built by `build_health_router` carries no
`track_metrics` layer (or any other middleware layer) at all, so the
exclusion there is structural rather than a path-matched skip.

## Dependencies

**Depends on** (what the health handlers call into): `state.db` (`buzz_db`,
via `ping()` and `validate_deletion_serving_catalog()`), `state.redis_pool`
(`deadpool_redis`, via `get()`), `state.shutting_down` and
`state.started_at` (both fields on `AppState`, `crates/buzz-relay/src/state.rs`),
`state.mesh()` (the relay's own `mesh_boot` module), and
`crate::build_info`'s three compile-time identity functions. `axum`, `tokio`,
and `serde_json` are the crate-level web/async/JSON dependencies these
handlers are written against (`crates/buzz-relay/Cargo.toml:31-41`).

**Depended on by**: `crates/buzz-relay/src/main.rs`, the sole caller of both
`build_router` and `build_health_router` (`main.rs:22`), which binds the
health-only router's listener and spawns it as an independent task inside
`serve()` (`main.rs:1289-1303`).

## Boundary

This node does not describe:
- The internal behavior of `state.db`, `state.redis_pool`,
  `state.shutting_down`'s broader role in connection draining, or the mesh
  subsystem's protocol — each is named here only as a collaborator the
  readiness/mesh handlers call into; their own responsibilities belong in
  their own corpus nodes, none of which are merged yet (see *Relationships*).
- The full graceful-shutdown sequence (jittered drain, hard-drain timeout,
  per-connection close-frame acknowledgement) beyond the single moment where
  it sets `shutting_down` — that is a separate, larger subject; a sibling
  task (`#1271`, `platforms/relay/graceful-shutdown`) is in flight to own it
  as of this revision, but is not merged onto `origin/launchpad` and is not
  cited as a relationships target for that reason.
- Kubernetes deployment manifests, probe configuration
  (`initialDelaySeconds`, `periodSeconds`, etc.), or the CAKE-specific "port
  8080" annotation named in `build_health_router`'s own doc comment — that
  is deployment topology, owned by `architecture/deployment/*` nodes, not
  this component-level node.
- Prometheus metrics content or the `/metrics` endpoint itself, beyond the
  one fact that health/metrics paths are excluded from `http_requests_total`
  cardinality.

## Relationships

None declared. At the recorded revision, `origin/launchpad`'s corpus tree
under `launchpad/docs/corpus/` contains no `platforms/**` node at all — every
sibling `platforms/relay/*` node (including `platforms-relay-app-state`,
whose `AppState` struct this node's handlers read `shutting_down`,
`started_at`, `db`, `redis_pool`, and `mesh()` from) exists only on its own
unmerged task branch. Declaring a `depends-on` or `references` edge to any of
them would resolve in this worktree but is a hard validation error on the
branch this node is actually merging into, per `AGENTS.md`'s explicit warning
about checking the merge-base tree rather than the author's own worktree.
The first moment any `platforms/relay/*` node merges onto `origin/launchpad`
is the right moment to add a `depends-on` edge from this node toward
`platforms-relay-app-state` (for the shared fields) and toward whichever node
ends up owning `#1271`'s graceful-shutdown subject.

## Scope and omissions

**This node covers** the relay's two health-HTTP surfaces (routes on the
main API router vs. the dedicated health-only router), each of the five
handler functions and what they check/return, the health-only router's
separate-port wiring and middleware-free construction, its participation in
SIGTERM-triggered shutdown via the `shutting_down` flag, and its exclusion
from request metrics.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| `AppState`'s full field inventory and construction | `platforms-relay-app-state` (unmerged sibling branch at this revision) |
| The full graceful-drain sequence (jitter, hard-drain timeout, per-connection close acknowledgement) | `#1271` / a future `platforms/relay/graceful-shutdown` node (unmerged at this revision) |
| The inter-relay mesh's own protocol and peer-health model | A future component node for `crate::mesh_boot`, not yet written |
| Kubernetes probe configuration and deployment topology | `architecture/deployment/*` nodes |
| The front-matter contract itself | `launchpad/docs/corpus/schema/node.schema.json` |
| Creating/updating/retiring a corpus node procedurally | `launchpad/docs/corpus/AGENTS.md` |

**Expected but not verified when this node was written:**
- No automated test was found exercising `build_health_router`,
  `liveness_handler`, `readiness_handler`, `status_handler`, or
  `mesh_status_handler` directly, in either `crates/buzz-relay/tests/` or
  `crates/buzz-test-client/tests/`. The one reference found
  (`conformance_multitenant.rs:578-581`) cites the main router's route list
  only incidentally, for an unrelated token-minting-surface obligation. This
  absence was checked by a targeted search of both test directories, not by
  an exhaustive read of every integration test file.
- Whether `buzz-db`'s `ping()` and `validate_deletion_serving_catalog()`
  methods themselves have their own test coverage was not checked — this
  node treats them as an external collaborator called from
  `readiness_handler`, not as its own subject.
- Whether `type: platforms` or `type: implementation` is the corpus's
  eventual settled convention for this path shape is unresolved by any
  accepted decision found at this revision; see the note under the title.
