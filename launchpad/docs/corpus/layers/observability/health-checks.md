---
id: layers-observability-health-checks
type: layers
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - operator
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision ed133f4c5dbd546a67d963f11ffa630a4513b228."
    entry_class: FACT
    evidence:
      - "commit ed133f4c5dbd546a67d963f11ffa630a4513b228"
  - statement: "buzz-relay's main app router registers three health-adjacent routes — GET /health, GET /_liveness, GET /_readiness — inside the same api_router that also carries the WebSocket/NIP-11 endpoint, the Nostr HTTP bridge and every other application route."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs:68-70"
  - statement: "A second, separate router — build_health_router, documented as 'the health-only router for K8s probes (port 8080 in CAKE)' with 'No metrics middleware, no auth, no CORS, no body limit' — registers GET /_liveness, GET /_readiness, GET /_status and GET /_mesh, and is the router actually served on the dedicated health port."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs:291-301"
  - statement: "health_handler and liveness_handler are both unconditional: each returns (StatusCode::OK, \"ok\") with no dependency check of any kind, so neither can ever report failure while the process is scheduling async tasks at all."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs:401-407"
  - statement: "readiness_handler first checks state.shutting_down (an AtomicBool) and immediately returns 503 with {\"status\": \"shutting_down\"} if set; otherwise it runs three checks concurrently (state.db.ping(), a Redis pool checkout, and state.db.validate_deletion_serving_catalog()) under a 2-second tokio::time::timeout, treating a timeout as all-checks-failed, and returns 200 {\"status\": \"ready\"} only if Postgres, Redis and the deletion-serving catalog all report healthy — otherwise 503 with a per-check breakdown."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs:409-449"
  - statement: "The relay binds a dedicated health-only TCP listener on 0.0.0.0:<config.health_port> in addition to the main app listener(s), and BUZZ_HEALTH_PORT defaults to 8080 when unset."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:1296-1299"
      - "crates/buzz-relay/src/config.rs:818-821"
  - statement: "The health-only listener's axum::serve call is not wrapped in with_graceful_shutdown, unlike every app-router TCP/UDS listener in the same function, which each subscribe to the shutdown watch channel and stop accepting only after it fires — so the health-only listener (and therefore /_readiness) keeps answering, including reporting 503 once shutting_down flips true, for the whole duration of the drain, right up until process exit."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:1301"
      - "crates/buzz-relay/src/main.rs:1406-1414"
      - "crates/buzz-relay/src/main.rs:1431-1439"
  - statement: "On receiving a shutdown signal, the relay sets shutting_down to true immediately (making /_readiness start returning 503 on its very next request), then sleeps 5 seconds before signalling the app-router drain to begin, a sequencing the function's own doc comment states exists specifically to 'let K8s stop routing new traffic before we close listeners.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:1336-1341"
  - statement: "The same function's doc comment diagrams all four of the relay's listeners (app TCP, optional app UDS, health-only TCP on 0.0.0.0:8080, and a Prometheus metrics listener on 0.0.0.0:9102) and states the total shutdown budget as 5s grace plus up to a 30s hard-drain timeout, bounded to fit inside the Helm chart's terminationGracePeriodSeconds: 60."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:1244-1287"
  - statement: "track_metrics (the middleware layered onto the main app router) explicitly skips any matched route path starting with \"/_\" or equal to \"/health\", stating in its own doc comment that this is 'to avoid polluting dashboards' — so requests to any of this node's health endpoints on the main app listener are not counted in http_requests_total/http_request_latency_ms."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/metrics.rs:150-179"
  - statement: "deploy/charts/buzz/values.yaml wires a livenessProbe (httpGet /_liveness, initialDelaySeconds 5, periodSeconds 10, timeoutSeconds 3, failureThreshold 3), a readinessProbe (httpGet /_readiness, initialDelaySeconds 5, periodSeconds 5, timeoutSeconds 3, failureThreshold 3) and a startupProbe (httpGet /_liveness, periodSeconds 2, failureThreshold 60 — i.e. up to 120 seconds of startup grace) all against a container port named \"health\", and sets service.healthPort: 8080."
    entry_class: FACT
    evidence:
      - "deploy/charts/buzz/values.yaml:143-164"
      - "deploy/charts/buzz/values.yaml:238"
  - statement: "deploy/charts/buzz/templates/deployment.yaml declares the container's \"health\" port from service.healthPort and passes it to the process as the BUZZ_HEALTH_PORT environment variable, and deploy/charts/buzz/templates/service.yaml maps a Kubernetes Service port named \"health\" to that same container port — the concrete plumbing that lets the probes in values.yaml address the relay's health-only listener by name rather than a hardcoded number."
    entry_class: FACT
    evidence:
      - "deploy/charts/buzz/templates/deployment.yaml:114-120"
      - "deploy/charts/buzz/templates/service.yaml:18"
  - statement: "The startup probe deliberately targets /_liveness rather than /_readiness, and its long failureThreshold (60 x periodSeconds 2 = up to 120s) exists to tolerate slow process startup without failing the pod, while still eventually detecting a process that never becomes responsive at all -- once the startup probe first succeeds, Kubernetes switches to the liveness and readiness probes for the rest of the pod's life. This reads the values.yaml probe shapes together with the router.rs handler split (an unconditional liveness check vs. a dependency-gated readiness check) rather than restating either source alone."
    entry_class: INFERENCE
    evidence:
      - "deploy/charts/buzz/values.yaml:143-164"
      - "crates/buzz-relay/src/router.rs:401-449"
    confidence: 0.85
  - statement: "At the recorded revision, origin/launchpad's launchpad/docs/corpus tree carries no layers/ directory at all, so this is the first layers-type node to merge; sibling tasks #1138 (layers/observability/liveness.md) and #1143 (layers/observability/readiness.md) are both still open with no merged content of their own to duplicate or link against."
    entry_class: FACT
    evidence:
      - "git_ls_tree(origin/launchpad, launchpad/docs/corpus) -> AGENTS.md, README.md, architecture/**, schema/**, standards/**, templates/**; no layers/ directory present"
  - statement: "Issue #1138's own open pull request (#1903) documents layers/compute/liveness.md (id layers-compute-liveness) -- agent-process presence via relay Nostr events -- and its body states explicitly that #1138's actual scope beyond the relay's /_liveness//_readiness probes 'was not established beyond its file path and open status' at the time #1903 was authored, so no existing draft of #1138 or #1143 covers the relay probe surface this node documents."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "gh pr diff 1903 --repo launchpad-26/buzz, read directly while authoring this node"
  - statement: "architecture-containers-relay (merged on origin/launchpad) already states the relay's four-listener shape including the health-only listener and lists health/liveness/readiness probes as part of the relay's inbound HTTP surface, at a summary level consistent with this node's more detailed account."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/containers/relay.md"
  - statement: "architecture-deployment-kubernetes (merged on origin/launchpad) already documents that the readiness probe checks Postgres connectivity only, not schema freshness, warning that an unmigrated pod can pass readiness and fail under load if BUZZ_AUTO_MIGRATE is disabled -- a caveat about the readiness probe's specific limits that this node references rather than restates."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/deployment/kubernetes.md:93"
      - "launchpad/docs/corpus/architecture/deployment/kubernetes.md:297-298"
relationships:
  - type: references
    target: architecture-containers-relay
  - type: references
    target: architecture-deployment-kubernetes
---

# Health checks

The Buzz relay exposes a small family of HTTP endpoints whose only job is to
answer "is this process okay" for an orchestrator, not for application
clients. This node is the umbrella map of that surface: which endpoints exist,
where they are served from, how Kubernetes is wired to them, and how they
relate to each other and to the relay's shutdown sequence. It intentionally
stays shallow on any single endpoint's internal dependency checks — that depth
belongs to this Feature's sibling nodes once they exist (see *Scope and
omissions*).

## Definition

A **health check**, in this codebase, is one of the relay's unauthenticated
`GET` endpoints — `/health`, `/_liveness`, `/_readiness` (and, on the
dedicated health port only, `/_status` and `/_mesh`) — that reports process or
dependency health as a plain HTTP status code (and a small JSON body for
`/_readiness`), consumed by Kubernetes probes rather than by desktop, mobile,
or CLI clients.

**What a health check is not:**

- **Not application data.** No health endpoint returns Nostr events, channel
  state, or anything a client renders. `/_status` and `/_mesh` return
  service/build and mesh-peer introspection respectively — operationally
  useful, but not "is it healthy" signals, and neither is wired to a
  Kubernetes probe in the Helm chart. They happen to share the health-only
  listener; this node does not treat their payloads as part of the
  health-*check* surface proper.
- **Not compute/agent liveness.** A Buzz agent's own liveness (is a specific
  agent's compute instance still running) is answered entirely differently —
  via relay presence events (`kind:20001`), not any HTTP probe — and is
  `layers/compute/liveness.md`'s subject, not this node's.
- **Not authenticated or community-scoped.** Every other HTTP path in this
  codebase resolves a host-derived community boundary or requires NIP-98
  auth; the health-only router explicitly carries none of that (no auth, no
  CORS, no metrics middleware, no body limit) because a Kubernetes kubelet
  probing a pod has no community context to present.

## The two surfaces

Two different routers carry overlapping route paths, and the distinction
matters operationally:

1. **The main app router** (`build_router`) registers `/health`, `/_liveness`
   and `/_readiness` alongside every other application route, served on the
   relay's primary listener(s) (`BUZZ_BIND_ADDR`, default `0.0.0.0:3000`, plus
   an optional Unix domain socket). Requests here pass through the same CORS
   layer as application traffic, but are explicitly excluded from the
   Prometheus request-metrics middleware (paths starting `/_` or equal to
   `/health` are skipped, "to avoid polluting dashboards").
2. **The health-only router** (`build_health_router`) is a second, separate
   `axum::Router` bound to its own dedicated TCP listener
   (`0.0.0.0:<BUZZ_HEALTH_PORT>`, default `8080`) with no metrics middleware,
   no auth, no CORS, and no body-size limit. It carries `/_liveness` and
   `/_readiness` (the same handlers as the main router) plus two endpoints the
   main router does not expose: `/_status` (service name, version, uptime,
   build identity) and `/_mesh` (mesh peer/connection status). This is the
   listener the Kubernetes chart's probes actually target, via a container
   port named `health`.

`/_liveness` and `/_readiness` therefore each answer twice, from two
independent listeners bound to two different ports, sharing the same handler
code. `/health` exists only on the main app listener and is not referenced by
any probe in the Helm chart.

## How Kubernetes is wired to it

```mermaid
flowchart LR
    subgraph Pod["Relay pod"]
        AppListener["App listener\nBUZZ_BIND_ADDR : 3000\n/health /_liveness /_readiness"]
        HealthListener["Health-only listener\n0.0.0.0 : BUZZ_HEALTH_PORT (8080)\n/_liveness /_readiness /_status /_mesh"]
    end
    Kubelet["kubelet"]
    Kubelet -- "startupProbe: GET /_liveness\nperiod 2s x60 (up to 120s)" --> HealthListener
    Kubelet -- "livenessProbe: GET /_liveness\nperiod 10s" --> HealthListener
    Kubelet -- "readinessProbe: GET /_readiness\nperiod 5s" --> HealthListener
```

`deploy/charts/buzz/values.yaml` wires all three Kubernetes probe types to the
container's `health` port (named via `service.healthPort: 8080`, plumbed
through `deployment.yaml`'s container port and `service.yaml`'s Service port,
and passed to the process as `BUZZ_HEALTH_PORT`):

| Probe | Target | Timing |
|---|---|---|
| `startupProbe` | `GET /_liveness` | `periodSeconds: 2`, `failureThreshold: 60` — up to 120s grace before liveness/readiness take over |
| `livenessProbe` | `GET /_liveness` | `initialDelaySeconds: 5`, `periodSeconds: 10`, `timeoutSeconds: 3`, `failureThreshold: 3` |
| `readinessProbe` | `GET /_readiness` | `initialDelaySeconds: 5`, `periodSeconds: 5`, `timeoutSeconds: 3`, `failureThreshold: 3` |

The startup probe deliberately targets `/_liveness`, not `/_readiness` —
tolerating a slow-starting process (still connecting to Postgres/Redis)
without the pod being killed, while the liveness probe behind it exists to
eventually catch a process that is truly wedged. Once the startup probe first
succeeds, Kubernetes hands off to the ordinary liveness/readiness probes for
the rest of the pod's life.

## How the endpoints relate to each other

The relay's own handlers draw a sharp, deliberate line between the two probe
paths:

- **`/_liveness` (and `/health`) are unconditional.** Both handlers return
  `200 OK` with no dependency check whatsoever — they can only fail to
  respond if the process itself cannot schedule an async task at all. This is
  exactly why the startup probe targets `/_liveness`: it answers "is the
  process alive," nothing more.
- **`/_readiness` is dependency-gated.** It checks, concurrently and under a
  2-second timeout, the shutdown flag, a Postgres ping, a Redis pool
  checkout, and the deletion-serving catalog's validity — reporting `503`
  with a per-check breakdown if any fail (or time out), and `200 {"status":
  "ready"}` only if all three pass. `architecture-deployment-kubernetes`
  already flags one specific limit of this check: it proves Postgres
  *connectivity*, not schema freshness, so a pod can be ready while running
  against an unmigrated schema if auto-migration is disabled.

This is also the mechanism the relay uses to signal graceful shutdown: on a
shutdown signal, `shutting_down` flips to `true` immediately, which makes
`/_readiness` start returning `503 {"status": "shutting_down"}` on its very
next request — before any listener stops accepting connections. The process
then sleeps 5 seconds (documented specifically so Kubernetes has time to stop
routing new traffic before listeners close) before starting the up-to-30-second
connection drain. Notably, the health-only listener is never itself wrapped
in graceful-shutdown wiring the way the app listeners are — it keeps serving
`/_liveness`/`/_readiness` (now reporting `shutting_down`) for the whole drain,
right up until process exit, which is exactly the behavior the readiness
probe needs during a rolling restart.

## Use cases

- **Debugging a pod stuck in `CrashLoopBackOff` or never becoming `Ready`**:
  knowing that `/_liveness` cannot fail on its own narrows the search to
  `/_readiness`'s three checks (Postgres, Redis, deletion-serving catalog)
  or, for a liveness failure specifically, to the process being genuinely
  wedged rather than merely slow to connect.
- **Reasoning about a rolling restart or `SIGTERM`**: expecting
  `/_readiness` to flip to `503` immediately, before any connection is
  dropped, and to keep answering that way for the whole drain window.
- **Adding a new dependency check** (e.g. a new datastore): deciding whether
  it belongs in `/_readiness`'s concurrent check set (traffic-affecting
  dependencies) versus being irrelevant to this endpoint entirely — the
  existing three checks are the pattern to extend, not `/_liveness`.
- **Writing or reviewing chart changes**: recognizing that all three probe
  types share one container port (`health`) and that changing
  `BUZZ_HEALTH_PORT` without updating `service.healthPort` (or vice versa)
  breaks probe routing silently rather than loudly.

## Scope and omissions

**This document covers** the inventory of health-check-adjacent endpoints
(`/health`, `/_liveness`, `/_readiness`, and the health-only listener's
`/_status`/`/_mesh`), the two-listener/two-router shape that serves them, how
the Helm chart's startup/liveness/readiness probes are wired to them, and how
the endpoints relate to each other and to the relay's graceful-shutdown
sequence.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The relay-process liveness probe's own deep dive — history, rationale for an unconditional check, any future evolution | #1138, `layers/observability/liveness.md` (not yet drafted at this node's recorded revision) |
| The readiness probe's deep dive — the specific semantics and failure modes of each of its three dependency checks | #1143, `layers/observability/readiness.md` (not yet drafted at this node's recorded revision) |
| Compute/agent-instance liveness (relay presence events, `kind:20001`) — a same-word, different-question, different-layer mechanism | `layers/compute/liveness.md` (drafted under #1138's sibling issue #1044) |
| `/_status` and `/_mesh` response payload internals | Not claimed by this node; neither is wired to a Kubernetes probe |
| Kubernetes deployment topology generally (replica strategy, resource limits, migrations) | `architecture-deployment-kubernetes` |
| The relay container's full inbound surface and all four listeners in overview | `architecture-containers-relay` |

**No relationships to `#1138`'s or `#1143`'s eventual nodes.** Checked before
declaring none, per this corpus's own convention: at the recorded revision,
`origin/launchpad`'s `launchpad/docs/corpus` tree has no `layers/` directory
at all, so `layers-observability-liveness` and `layers-observability-readiness`
do not exist as mergeable relationship targets yet. Two relationships are
declared instead, to nodes that do exist today and already touch this
subject: `architecture-containers-relay` (states the four-listener shape and
lists the health/liveness/readiness probes as part of the relay's inbound
surface) and `architecture-deployment-kubernetes` (already documents the
readiness probe's DB-connectivity-only limitation).

**Expected but not verified when this node was written:**

- Whether any load balancer, ingress, or external monitoring system (outside
  the Kubernetes chart in this repository) also targets `/health` or
  `/_liveness`/`/_readiness` was not checked — only the in-repo Helm chart's
  probe wiring was verified.
- No automated test exercising `/_liveness`, `/_readiness`, `/_status` or
  `/_mesh` over HTTP was located during this node's authoring; the behavior
  claims above are drawn directly from the handler source, not from an
  observed test run.
- Whether `#1138`'s or `#1143`'s eventual scope will draw exactly the
  boundary this node assumes (relay-process probes for #1138, the readiness
  dependency checks for #1143) is this node's own reasoned placement — like
  the sibling `layers/compute/liveness.md` node's own equivalent disclosure
  about #1138 — not something either issue has itself stated, since neither
  has been drafted yet.
