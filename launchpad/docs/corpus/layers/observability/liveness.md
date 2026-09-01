---
id: layers-observability-liveness
type: layers
status: draft
origin: launchpad
audiences:
  - developer
  - operator
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5 on the launchpad branch."
    entry_class: FACT
    evidence:
      - "commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
  - statement: "liveness_handler is an async fn taking no State or other extractor parameters, whose entire body is `(StatusCode::OK, \"ok\")` -- it performs no dependency checks, no shutdown-flag check, and no I/O of any kind."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs:370-372"
  - statement: "GET /_liveness is registered twice: once on the main app router built by build_router (alongside the WebSocket/REST surface, port 3000 by default), and once on the dedicated health-only router built by build_health_router (port 8080 by default) -- both routes point at the same liveness_handler."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs:69"
      - "crates/buzz-relay/src/router.rs:249"
  - statement: "readiness_handler, by contrast, carries a doc comment stating it checks the shutdown flag plus Postgres and Redis connectivity, and its body additionally awaits state.db.validate_deletion_serving_catalog() under a 2-second total timeout, returning 503 with a JSON status body if the process is shutting down or if any dependency check fails or times out."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs:374-410"
  - statement: "build_health_router's doc comment describes it as 'the health-only router for K8s probes (port 8080 in CAKE)', with 'No metrics middleware, no auth, no CORS, no body limit'."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs:244-246"
  - statement: "config.rs documents health_port as 'Separate from the app router so K8s probes bypass Istio and auth middleware', reading BUZZ_HEALTH_PORT and defaulting to 8080 when unset."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/config.rs:131-133"
      - "crates/buzz-relay/src/config.rs:716-718"
  - statement: "The Helm chart's default relay.livenessProbe is an httpGet against path /_liveness on the named 'health' container port, with initialDelaySeconds: 5, periodSeconds: 10, timeoutSeconds: 3, failureThreshold: 3; templates/deployment.yaml renders that value directly into the pod spec's livenessProbe field via toYaml."
    entry_class: FACT
    evidence:
      - "deploy/charts/buzz/values.yaml:141-148"
      - "deploy/charts/buzz/templates/deployment.yaml:230-231"
  - statement: "Already-merged corpus node architecture-containers-relay documents this same health surface -- the relay's four listeners, build_health_router, readiness_handler's dependency checks, and the Helm probe wiring -- with its own FACT evidence citing this router.rs, so this concept node references it rather than re-deriving the same architectural detail."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/containers/relay.md"
  - statement: "Already-merged corpus node architecture-context-relay-operator documents BUZZ_HEALTH_PORT, names CAKE as Block's internal platform that probes port 8080, and states that the operator's monitoring stack -- not the relay's own logic -- is what consumes the health/metrics surface; that operator-facing framing is what this node's Use cases section draws on."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/context/relay-operator.md"
  - statement: "A Kubernetes liveness probe crossing failureThreshold consecutive failures causes the kubelet to restart the container, while a readiness probe failing removes the pod from Service endpoints without restarting it; that difference in remediation action is why an orchestrator distinguishes the two probe types, and is why the Helm chart wires /_liveness and /_readiness to two different handlers rather than one."
    entry_class: INFERENCE
    evidence:
      - "deploy/charts/buzz/values.yaml:141-156"
      - "crates/buzz-relay/src/router.rs:370-410"
    confidence: 0.85
  - statement: "liveness_handler's unconditional response, contrasted with readiness_handler's dependency checks, reads as a deliberate design choice: a relay process that has lost its Postgres or Redis connection, or is draining during a graceful shutdown (the shutting_down flag readiness_handler checks), is still reported alive and is not killed by the kubelet -- it is only removed from traffic by readiness -- because the process may still be capable of resuming service once the dependency recovers, and restarting it would compound an already-detected condition rather than resolve it."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay/src/router.rs:370-372"
      - "crates/buzz-relay/src/router.rs:374-410"
    confidence: 0.7
  - statement: "Issue #1044 (task: document layers/compute/liveness.md, open and unmerged at the recorded revision) scopes a distinct concept -- compute-instance liveness, whether a managed AI agent's compute substrate is alive, answered via relay presence -- not the relay process's own /_liveness HTTP probe this node documents."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1044 (open issue body, read directly while authoring this node)"
  - statement: "Issue #1137 (task: document layers/observability/health-checks.md, open and unmerged at the recorded revision) scopes the general health-check umbrella concept; this node documents one instance of that umbrella -- the liveness probe specifically -- not the umbrella itself."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1137 (open issue body, read directly while authoring this node)"
  - statement: "Issue #1143 (task: document layers/observability/readiness.md, open and unmerged at the recorded revision) scopes the sibling readiness concept in full; this node's Comparison section distinguishes the two by what each handler actually executes, but leaves the full readiness treatment to that node."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1143 (open issue body, read directly while authoring this node)"
relationships:
  - type: references
    target: architecture-containers-relay
  - type: references
    target: architecture-context-relay-operator
---

# Liveness (relay process probe)

Liveness, in Buzz's relay, is the answer to one narrow question posed by
container orchestration: **is this relay process itself still alive and able
to respond to a request at all?** It is one of several health signals the
relay exposes (see `layers-observability-health-checks`, #1137, for the
umbrella), and it is deliberately the *weakest* of them.

## Definition

Liveness is served at `GET /_liveness`, handled by `liveness_handler`, whose
entire implementation is an unconditional `(StatusCode::OK, "ok")` response
(`crates/buzz-relay/src/router.rs:370-372`). The handler takes no `State`
extractor and performs no I/O, no dependency check, and no shutdown-flag
check — it cannot observe anything about the relay's Postgres connection,
Redis connection, or in-flight shutdown, because it does not look. As long
as the Tokio runtime can schedule the handler and return a response, `/_liveness`
answers `200 ok`.

The route is registered twice against the identical handler: once on the
main application router (`build_router`, alongside the WebSocket and REST
surface, default port 3000) and once on a separate health-only router
(`build_health_router`, default port 8080) (`crates/buzz-relay/src/router.rs:69,249`).
The health-only router's own doc comment names its purpose directly: "the
health-only router for K8s probes (port 8080 in CAKE)," configured with "No
metrics middleware, no auth, no CORS, no body limit" (`crates/buzz-relay/src/router.rs:244-246`).
CAKE is Block's internal platform; the corpus's own operator-facing node
already names it as the thing that probes this port (`architecture-context-relay-operator`).
`config.rs` states the reason for the separate port explicitly: "Separate
from the app router so K8s probes bypass Istio and auth middleware"
(`crates/buzz-relay/src/config.rs:131-133`), defaulting to 8080 via
`BUZZ_HEALTH_PORT` (`crates/buzz-relay/src/config.rs:716-718`).

## Use cases

**Restart-on-hang detection.** An orchestrator (Kubernetes via the Helm
chart's `relay.livenessProbe`, or an equivalent) polls `/_liveness` on a
fixed interval and, after a configured number of consecutive failures,
concludes the process is unresponsive and restarts the container. The
chart's default is `httpGet` against `/_liveness` on the `health` port with
`initialDelaySeconds: 5, periodSeconds: 10, timeoutSeconds: 3,
failureThreshold: 3` (`deploy/charts/buzz/values.yaml:141-148`), wired into
the pod spec by `templates/deployment.yaml:230-231`. Because
`liveness_handler` never blocks on external state, a failure here means the
process's own request-handling loop has stopped functioning — a deadlock, a
runtime panic in a way that leaves the process alive but unresponsive, or
similar — not merely that a dependency is unreachable.

**Staying alive through degradation and shutdown.** Because liveness checks
nothing beyond the runtime's ability to answer, a relay pod that has lost
its Postgres or Redis connection, or that is draining during a graceful
shutdown (`readiness_handler`'s `shutting_down` flag check,
`crates/buzz-relay/src/router.rs:374-410`), keeps reporting alive. Only
`readiness` reacts to those conditions, by returning 503 and causing the
orchestrator to stop routing new traffic to the pod — without restarting
it. This split is why the Helm chart wires `/_liveness` and `/_readiness`
to two different handlers with two different probe schedules rather than
one combined check (`deploy/charts/buzz/values.yaml:141-156`): a lost
dependency the process might recover from is a traffic-routing problem, not
a process-health problem, and treating it as the latter would restart pods
that did not need restarting.

## Comparison

| Probe | Handler | What it checks | Orchestrator reaction on failure |
|---|---|---|---|
| Liveness (`/_liveness`) | `liveness_handler` | Nothing — unconditional 200 (`router.rs:370-372`) | Restart the container |
| Readiness (`/_readiness`, #1143) | `readiness_handler` | Shutdown flag, Postgres, Redis, deletion-serving-catalog connectivity, all under a 2s timeout (`router.rs:374-410`) | Remove the pod from Service endpoints; no restart |
| Compute-instance liveness (#1044, `layers-compute-liveness`) | Not this HTTP probe | Whether a managed AI agent's *compute substrate* is alive, answered via relay presence | Out of scope for this node entirely |

The first two rows are both served by this same relay process on the same
health-only listener and are easy to conflate because they share a name
prefix and a port. The third row is a different concept that happens to
share the word "liveness": it is about whether a piece of compute an agent
runs on is alive, determined by whether that compute is present and
communicating with the relay — not about an HTTP probe on the relay's own
process. #1044 is that node's task; it is not yet merged, so no
`relationships` edge exists from here to it (see *Scope and omissions*).

## Related resources

`architecture-containers-relay` documents the relay's full health surface
architecturally — all four listeners, both health-router handlers, and the
Helm wiring — and is the deeper implementation reference this node draws
its FACT citations from without repeating its whole content. `architecture-context-relay-operator`
documents the operator-facing framing: the CAKE platform name, the
environment variables that configure the health port, and that an external
monitoring stack (not the relay's own logic) is what consumes this surface.
Both are `references` relationships in this node's front matter.

## Scope and omissions

**This node covers** the relay process's own `/_liveness` HTTP probe: its
handler, its unconditional nature, why it is registered on two routers, and
why an orchestrator treats a liveness failure differently from a readiness
failure. It does not cover:

| Not covered here | Owned by |
|---|---|
| The readiness probe (`/_readiness`) in full — its exact dependency checks, timeout behavior, and shutdown-flag interaction beyond the contrast drawn above | #1143, `layers/observability/readiness.md` (open, unmerged) |
| The general health-check umbrella concept this node is one instance of | #1137, `layers/observability/health-checks.md` (open, unmerged) |
| Compute-instance liveness — whether a managed AI agent's compute substrate is alive, answered via relay presence | #1044, `layers/compute/liveness.md` (open, unmerged) |
| The relay's full listener/port architecture, the inter-relay mesh, and the push-gateway delivery path | `architecture-containers-relay` |
| Graceful shutdown's full timing (grace period, drain timeout, jitter) | `architecture-containers-relay` |

**No `relationships` edge points at #1044, #1137, or #1143.** All three are
open, unmerged sibling tasks in this same corpus batch (feature #611); none
of their node ids exist on `origin/launchpad` at the recorded revision
(`git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus`
carries no `layers/` subtree at all yet), and `AGENTS.md` treats a
relationship target that resolves only in one's own worktree as a hard
error once it reaches the branch it merges into. The boundary against each
is instead drawn in prose above, and the edges are a natural follow-up once
those siblings merge.

**Expected but not verified when this node was written:**

- **Whether `liveness_handler`'s complete absence of any check (not even a
  cheap in-memory flag read) is documented anywhere as an intentional
  contract**, versus being merely the simplest implementation that happened
  to satisfy the Helm chart's probe wiring. No doc comment sits above
  `liveness_handler` itself (only `readiness_handler` carries one); the
  "why unconditional" reasoning above is therefore classified `INFERENCE`,
  not `FACT`.
- **Whether `architecture-deployment-kubernetes`** (which discusses
  readiness and migration-freshness at length but mentions liveness only
  through the shared three-port table) **also warrants a `references` edge
  from this node.** Decided against for this draft — the handler-level
  detail this node cites lives in `architecture-containers-relay`, and a
  second edge to the Kubernetes deployment node would largely duplicate
  that citation rather than add a distinct one — but a reviewer may
  reasonably disagree.
- **Whether a `startupProbe` (present in `deploy/charts/buzz/templates/deployment.yaml:234-235`
  alongside `livenessProbe` and `readinessProbe`) also targets `/_liveness`
  or a different path.** Not inspected while writing this node; if it
  targets the same endpoint, the Use cases section's "restart-on-hang"
  framing may need a startup-vs-steady-state distinction added later.

**Candidate follow-up, not filed by this task:** whether the corpus should
also record, on `architecture-containers-relay` or a new node, the fact
that `liveness_handler` and `health_handler` (`GET /health` on the main app
router) are two independently-defined handlers with byte-identical bodies —
a second concept (route duplication / potential drift risk) noticed while
reading `router.rs:366-372`, out of scope for a single liveness concept
node and not folded in here.
