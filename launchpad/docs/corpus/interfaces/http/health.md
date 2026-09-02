---
id: interfaces-http-health
type: interfaces-events
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - operator
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 650354eab8d41ab6ce1a71de079a6c6d95c69052."
    entry_class: FACT
    evidence:
      - "commit 650354eab8d41ab6ce1a71de079a6c6d95c69052"
  - statement: "The relay's app router (built by build_router) registers GET /health, GET /_liveness and GET /_readiness on the same axum Router that also serves the WebSocket endpoint, the NIP-98 HTTP bridge, media, and git routes."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs:67-70"
  - statement: "The relay's health-only router (build_health_router) registers GET /_liveness, GET /_readiness, GET /_status and GET /_mesh on a separate axum Router intended for a separate TCP listener, and its doc comment states this router carries no metrics middleware, no auth, no CORS, and no body limit."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs:291-301"
  - statement: "health_handler and liveness_handler both take no extractors and unconditionally return (StatusCode::OK, \"ok\") with no dependency check of any kind."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs:401-407"
  - statement: "readiness_handler returns 503 with JSON {\"status\":\"shutting_down\"} immediately if the process's shutting_down atomic flag is set; otherwise it runs, under a 2-second timeout, a concurrent Postgres ping (state.db.ping()), a Redis pool checkout (state.redis_pool.get()), and a deletion-serving-catalog validation (state.db.validate_deletion_serving_catalog()), and returns 200 with {\"status\":\"ready\"} only if all three succeed, or 503 with {\"status\":\"not_ready\", \"postgres\": bool, \"redis\": bool, \"deletion_catalog\": bool} naming exactly which check(s) failed (a timed-out check reports false for every component, since tokio::time::timeout's Err path is mapped to (false, false, false))."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs:409-449"
  - statement: "status_handler (GET /_status, health-only router only) returns 200 with a JSON object containing service (\"buzz-relay\"), version (CARGO_PKG_VERSION), uptime_seconds (elapsed since state.started_at), and a nested build object with source_sha, id, and url sourced from crate::build_info."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs:451-467"
  - statement: "mesh_status_handler (GET /_mesh, health-only router only) returns 200 with JSON serialization of the mesh handle's status() if mesh is enabled (state.mesh() is Some), or {\"enabled\": false} if mesh is disabled (state.mesh() is None); a serialization failure falls back to {\"enabled\": true, \"error\": \"status serialize: <e>\"} rather than a non-2xx response."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs:469-478"
  - statement: "No authentication or authorization middleware is applied to any of these five routes. The app router's merged Router (api_router + media_router + git_router + git_policy_router [+ admin_router]) has exactly three layers applied over the whole merge -- track_metrics, an HTTP trace layer, and a CORS layer -- none of which perform authentication, and the health-only router (build_health_router) applies no layer at all. NIP-98 authentication is instead enforced per-handler inside individual bridge/media/admin handlers that these five handlers do not call."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs:145-207"
      - "crates/buzz-relay/src/router.rs:291-301"
  - statement: "track_metrics (the CAKE HTTP metrics middleware applied to the app router) explicitly skips recording any path starting with \"/_\" or exactly \"/health\", so that health-probe traffic does not appear in the http_requests_total / http_request_latency_ms Prometheus series and does not pollute dashboards or cardinality."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/metrics.rs:155"
      - "crates/buzz-relay/src/metrics.rs:169-175"
  - statement: "The relay serves the health-only router on a distinct TCP listener bound to config.health_port (0.0.0.0), started as its own tokio::spawn task inside serve(), independently of the app router's own listener(s) (TCP bind address, optional Unix domain socket)."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:1291-1302"
  - statement: "config.health_port defaults to 8080 when the BUZZ_HEALTH_PORT environment variable is absent or fails to parse as a u16, via std::env::var(\"BUZZ_HEALTH_PORT\").ok().and_then(|v| v.parse().ok()).unwrap_or(8080)."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/config.rs:818-821"
  - statement: "The health_port field's own doc comment states it is 'Separate from the app router so K8s probes bypass Istio and auth middleware' and names /_liveness, /_readiness, /_status as the routes served there."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/config.rs:192-196"
  - statement: "The repository's canonical Kubernetes Helm chart (deploy/charts/buzz) wires the relay Deployment's livenessProbe to an HTTP GET on path /_liveness, readinessProbe to /_readiness, and startupProbe to /_liveness, all three against the container's named health port, with concrete thresholds: liveness initialDelaySeconds=5, periodSeconds=10, timeoutSeconds=3, failureThreshold=3; readiness initialDelaySeconds=5, periodSeconds=5, timeoutSeconds=3, failureThreshold=3; startup failureThreshold=60, periodSeconds=2 (no initialDelaySeconds set, i.e. Kubernetes' own default of 0)."
    entry_class: FACT
    evidence:
      - "deploy/charts/buzz/values.yaml:143-164"
  - statement: "The chart's Service and Deployment templates name a `health` port with value Values.service.healthPort (137 in values.yaml, set to 8080), map it to the container's `health` containerPort, and inject it into the container as the BUZZ_HEALTH_PORT environment variable, so the chart-declared probe port and the relay's own config.health_port default agree by construction rather than by coincidence."
    entry_class: FACT
    evidence:
      - "deploy/charts/buzz/templates/service.yaml:18"
      - "deploy/charts/buzz/templates/deployment.yaml:114"
      - "deploy/charts/buzz/templates/deployment.yaml:119"
      - "deploy/charts/buzz/values.yaml:238"
  - statement: "main.rs's own serve() doc comment states the SIGTERM shutdown sequence sets shutting_down=true (causing readiness to return 503 immediately), sleeps a fixed 5s grace period so Kubernetes stops routing new traffic before any listener closes, then runs a bounded 30s hard drain, for a documented worst case of 5s + 30s = 35s from SIGTERM to forced exit -- inside the chart's terminationGracePeriodSeconds: 60."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:1244-1280"
  - statement: "No versioned or namespaced schema governs these five response bodies; /health and /_liveness return a bare 200 with the literal text body \"ok\" (not JSON), while /_readiness, /_status and /_mesh return ad hoc serde_json::json! objects built inline in each handler, with no shared struct, OpenAPI document, or schema registry backing any of the three JSON shapes."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs:401-478"
  - statement: "No AsyncAPI or OpenAPI specification document exists anywhere in this repository describing this or any other HTTP surface; a case-insensitive grep for 'asyncapi|swagger' across rs/toml/md/yaml/yml/json files (excluding node_modules and target), run directly against this worktree at the recorded revision, found zero matches other than this node's own new file (which merely discusses the terms)."
    entry_class: FACT
    evidence:
      - "grep_repo('asyncapi|swagger', types='rs,toml,md,yaml,yml,json', exclude='node_modules,target') -> zero matches other than launchpad/docs/corpus/interfaces/http/health.md itself, verified 2026-09-01 against commit 650354eab8d41ab6ce1a71de079a6c6d95c69052"
  - statement: "Because none of the five handlers takes a body, reads request state beyond the shared AppState, or performs a write, repeated identical calls to any of them (GET with no body) cannot have a different effect than a single call -- the operations are naturally idempotent by virtue of being read-only GETs, not through any explicit idempotency-key mechanism."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay/src/router.rs:401-478"
    confidence: 0.9
  - statement: "Because these are plain GET routes registered directly on axum Routers with no version segment in any path (no /v1/health, no Accept-Version negotiation) and no version field in any response body, a breaking change to a response shape or status-code contract would be an unversioned, silently breaking change for any caller (in particular the Kubernetes probe wiring in deploy/charts/buzz/values.yaml) rather than something a caller could detect or opt out of in advance."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay/src/router.rs:401-478"
      - "deploy/charts/buzz/values.yaml:143-164"
    confidence: 0.85
relationships:
  - type: implements
    target: corpus-template-interface
  - type: references
    target: architecture-deployment-kubernetes
---

# HTTP health probes: interface

This node documents the relay's HTTP health-probe surface: five unauthenticated
`GET` routes (`/health`, `/_liveness`, `/_readiness`, `/_status`, `/_mesh`) that let
an orchestrator, a load balancer, or a human operator ask "is this relay process
alive, and is it safe to route traffic to it?" without going through NIP-98
authentication, WebSocket upgrade, or community/tenant resolution. Two are served
on the relay's main app port; four are also served on a second, dedicated
`health_port` listener (default `8080`) that Kubernetes probes reach directly,
bypassing the service mesh sidecar and any auth middleware layered on the app
router.

## Operations

| Operation | Defined in | Summary |
|---|---|---|
| `GET /health` | `crates/buzz-relay/src/router.rs:401` (`health_handler`), routed at `router.rs:68` | Always `200 "ok"`. No dependency check. App router only. |
| `GET /_liveness` | `crates/buzz-relay/src/router.rs:405` (`liveness_handler`), routed at `router.rs:69` (app) and `router.rs:296` (health-only) | Always `200 "ok"`. No dependency check. Served on both routers. |
| `GET /_readiness` | `crates/buzz-relay/src/router.rs:410` (`readiness_handler`), routed at `router.rs:70` (app) and `router.rs:297` (health-only) | `200 {"status":"ready"}` iff not shutting down AND Postgres ping AND Redis pool checkout AND deletion-serving-catalog validation all succeed within a 2s timeout; otherwise `503` naming which failed. Served on both routers. |
| `GET /_status` | `crates/buzz-relay/src/router.rs:465` (`status_handler`), routed at `router.rs:298` | `200` with service name, crate version, process uptime, and build identity (source SHA / build id / build URL). Health-only router only. |
| `GET /_mesh` | `crates/buzz-relay/src/router.rs:472` (`mesh_status_handler`), routed at `router.rs:299` | `200` with live mesh peer/connection status, or `{"enabled": false}` when the mesh feature is off. Health-only router only. |

## Contract and stability

- **No authentication or authorization is required for any of the five routes.**
  The app router's merged surface carries exactly three cross-cutting layers
  (`track_metrics`, an HTTP trace layer, CORS) and none authenticates; the
  health-only router applies no layer at all, per its own doc comment ("No
  metrics middleware, no auth, no CORS, no body limit"). This is a deliberate
  design choice recorded in `config.rs`'s `health_port` doc comment ("Separate
  from the app router so K8s probes bypass Istio and auth middleware"), not an
  oversight — the surface is deliberately reachable pre-auth so an orchestrator
  can probe a pod before any credential exchange is possible.
- **`/health` and `/_liveness` make no promise beyond process liveness.** Both
  return a bare `200 "ok"` unconditionally; neither checks Postgres, Redis, or
  any other dependency. A caller cannot distinguish "process is up and serving
  traffic correctly" from "process is up but every downstream dependency is
  down" using either route.
- **`/_readiness` is the only route with a dependency contract**, and that
  contract is explicit in its response body: a `503` names exactly which of
  `postgres`, `redis`, `deletion_catalog` failed (each a boolean), plus a
  distinct `{"status":"shutting_down"}` `503` when the process has begun
  graceful shutdown. The whole check is bounded to 2 seconds; a timeout is
  indistinguishable in the response from every check failing.
- **Response bodies carry no version field, no version-numbered path segment,
  and no shared schema.** `/health` and `/_liveness` return a literal text body,
  not JSON; `/_readiness`, `/_status`, `/_mesh` each build an ad hoc
  `serde_json::json!` object inline in its own handler. No OpenAPI or AsyncAPI
  document exists anywhere in this repository for this or any other HTTP
  surface. A shape change to any response is therefore an unversioned, silently
  breaking change for whatever consumes it — in particular the Kubernetes
  Helm-chart probe wiring below, which parses neither JSON body today but does
  depend on the exact paths and status codes.
- **Ordering and idempotency:** all five operations are plain, body-less `GET`
  requests that only read shared process/connection-pool state; none mutates
  anything. Repeated identical calls cannot have a cumulative or
  order-dependent effect — idempotency here is a structural consequence of
  being read-only, not an explicit idempotency-key mechanism the way a mutating
  Nostr event submission would need one.
- **The authoritative machine specification of how these routes are consumed in
  production is the relay's own Helm chart**, `deploy/charts/buzz/values.yaml`,
  not a document this corpus node re-encodes:

  ```yaml
  livenessProbe:
    httpGet: { path: /_liveness, port: health }
    initialDelaySeconds: 5
    periodSeconds: 10
    timeoutSeconds: 3
    failureThreshold: 3
  readinessProbe:
    httpGet: { path: /_readiness, port: health }
    initialDelaySeconds: 5
    periodSeconds: 5
    timeoutSeconds: 3
    failureThreshold: 3
  startupProbe:
    httpGet: { path: /_liveness, port: health }
    failureThreshold: 60
    periodSeconds: 2
  ```

  The chart's `service.yaml`/`deployment.yaml` templates name a `health`
  container port set from `Values.service.healthPort` (`8080`) and inject it as
  the `BUZZ_HEALTH_PORT` environment variable the relay reads at startup, so the
  chart's probe port and the relay's own `config.health_port` default agree by
  construction. `/_status` and `/_mesh` are not wired to any Kubernetes probe —
  they exist for human/operator inspection and are reachable only on the
  health-only listener.

### Example: successful readiness check

Request: `GET /_readiness` against the health-only listener (port `8080` by
default), no headers required.

```
HTTP/1.1 200 OK
Content-Type: application/json

{"status":"ready"}
```

### Example: failing readiness check

Same request, Redis unreachable (Postgres and the deletion-serving catalog both
still healthy):

```
HTTP/1.1 503 Service Unavailable
Content-Type: application/json

{"status":"not_ready","postgres":true,"redis":false,"deletion_catalog":true}
```

If the process has begun graceful shutdown instead, the body is
`{"status":"shutting_down"}` with the same `503` status, regardless of the
underlying dependency state — the shutdown check short-circuits before any
dependency is queried.

## Boundary

This node does not describe:
- **Any single Nostr event kind's wire contract.** These routes carry no Nostr
  event payloads at all — they are the one part of the relay's HTTP surface with
  no NIP-98, NIP-01, or NIP-29 involvement whatsoever.
- **A full parameter-by-parameter API reference for every HTTP route this
  relay exposes.** This node covers only the five health-probe routes; the
  Nostr HTTP bridge (`/events`, `/query`, `/count`), media (Blossom), git smart
  HTTP, and NIP-11/NIP-05 metadata are each a distinct boundary and, per
  `templates/interface.md`'s own guidance, belong in their own corpus node(s)
  once drafted rather than folded in here.
- **The relay's shutdown/drain sequencing in general.** `/_readiness`'s
  `shutting_down` check is described above only insofar as it changes this
  route's own response; the full drain timeline (grace period, jitter, hard
  drain deadline) is `main.rs`'s `serve()` documentation and, if a corpus node
  for it exists or is later drafted, that node's subject — not restated here.
- **The mesh feature's own status schema or peer protocol.** `/_mesh` is listed
  as an operation of this interface because it shares the health-only listener
  and handler style, but the shape of `handle.status()` and the mesh protocol
  itself belong to a mesh-focused corpus node, not this one.

## Relationships

- `implements` → `corpus-template-interface` — this node is drafted following
  that template's required sections (Interface description, Operations,
  Contract and stability, Boundary, Relationships, Scope and omissions).
- `references` → `architecture-deployment-kubernetes` — that node documents the
  Helm chart as the relay's canonical Kubernetes deployment automation; this
  node cites the same chart's `values.yaml` for the concrete probe wiring
  without duplicating that node's broader deployment-topology content.
- No `relationships` target any sibling `interfaces/http/*` node (the Nostr
  bridge, media, git, admin, NIP-11/NIP-05 surfaces): none exists on
  `origin/launchpad` at the recorded revision, and `AGENTS.md`'s node-creation
  rule requires a relationship target to resolve on the branch being merged
  into, not the author's own worktree. The first such sibling node to merge is
  the natural moment to add an edge in either direction.

## Scope and omissions

**This node covers** the five HTTP health-probe routes the relay exposes
(`/health`, `/_liveness`, `/_readiness`, `/_status`, `/_mesh`): their handlers,
which router(s) and listener(s) serve them, their request/response shapes,
their authentication posture (none), their dependency-check behavior, and the
Kubernetes Helm-chart probe configuration that is their primary real-world
caller.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The Nostr HTTP bridge (`/events`, `/query`, `/count`) and any other HTTP route group | A future `interfaces/http/*` sibling node, not yet drafted |
| The relay's full SIGTERM/drain sequencing | `main.rs`'s `serve()` documentation; no dedicated corpus node found at the recorded revision |
| The mesh feature's status schema and peer protocol | A future mesh-focused corpus node, not yet drafted |
| Per-type interface-node authoring standards beyond `templates/interface.md` | Somewhere in `#1307`-`#1351`, per `AGENTS.md`'s own gap table; none had merged at the recorded revision |

**Expected but not verified when this node was written:**
- **No live cluster or CI run was observed exercising these probes.** Every
  claim above comes from reading `router.rs`, `config.rs`, `main.rs`, and the
  Helm chart's YAML directly — not from watching a real Kubernetes deployment
  mark a pod ready or unready, or from a `just` recipe run in this session.
- **Whether any automated test exercises these five routes directly was not
  found.** A grep across `crates/buzz-test-client/tests` found only incidental
  mentions of the route *list* (documenting a different obligation in
  `conformance_multitenant.rs`) and an unrelated Nostr-level `kind:30003` mesh
  *member* status event in `e2e_mesh_llm.rs` that is not this `/_mesh` HTTP
  route — no test was found asserting `/health`, `/_liveness`, `/_readiness`,
  `/_status`, or `/_mesh`'s actual HTTP response shape or status code.
- **`crate::build_info`'s `source_sha`/`build_id`/`build_url` functions were not
  opened.** `/_status`'s response shape cites `status_payload`'s call sites in
  `router.rs`, but the exact fallback behavior of those three functions when
  build metadata is absent (e.g. a local `cargo build` outside CI) was not
  independently verified.
