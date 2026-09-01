---
id: layers-observability-readiness
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
  - statement: "The relay exposes a readiness probe at `GET /_readiness`, handled by `readiness_handler`, registered on both the main app router and the dedicated health-only router built by `build_health_router`."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs"
  - statement: "`readiness_handler` first checks `state.shutting_down` and, if true, returns `503 Service Unavailable` with body `{\"status\": \"shutting_down\"}` immediately, without running any dependency check."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs"
  - statement: "When not shutting down, `readiness_handler` runs three checks concurrently via `tokio::join!`: `state.db.ping()` (Postgres), `state.redis_pool.get().await.is_ok()` (Redis), and `state.db.validate_deletion_serving_catalog().await.is_ok()` (deletion-fence schema), all bounded by a single 2-second `tokio::time::timeout`; a timeout defaults every check to `false` rather than hanging the probe."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs"
  - statement: "Readiness returns `200 OK` with `{\"status\": \"ready\"}` only when all three checks pass; otherwise it returns `503 Service Unavailable` with `{\"status\": \"not_ready\", \"postgres\": <bool>, \"redis\": <bool>, \"deletion_catalog\": <bool>}`, naming which dependency failed."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs"
  - statement: "`Db::ping` executes `SELECT 1` against the pool and returns `false` on any error; its own doc comment states it is 'used by readiness probes.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/runtime/mod.rs"
  - statement: "`DeletionStore::validate_serving_catalog` (reached via `Db::validate_deletion_serving_catalog`) queries `pg_attribute` for the `communities` table and asserts that `deletion_state`, `deletion_fence_generation`, and `deleted_at` exist with the expected Postgres types and nullability — it is a schema-shape check, not a bare connectivity ping."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/deletion.rs"
  - statement: "By contrast, `liveness_handler` (`GET /_liveness`) takes no state and unconditionally returns `200 OK` — it checks nothing about Postgres, Redis, the deletion catalog, or the shutdown flag."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs"
  - statement: "The health-only router (`build_health_router`) is bound on a separate TCP port from the main app router — `config.health_port` (field doc: 'Separate from the app router so K8s probes bypass Istio and auth middleware') — distinct from the metrics port and the app-traffic port/UDS."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/config.rs"
      - "crates/buzz-relay/src/main.rs"
  - statement: "The bundled Helm chart configures `readinessProbe` at `path: /_readiness` with `initialDelaySeconds: 5, periodSeconds: 5, timeoutSeconds: 3, failureThreshold: 3`, distinct from `livenessProbe` at `path: /_liveness` with `periodSeconds: 10` (readiness is polled twice as often as liveness in the shipped defaults)."
    entry_class: FACT
    evidence:
      - "deploy/charts/buzz/values.yaml"
  - statement: "On SIGTERM, the relay sets `shutting_down` to `true` immediately (so the very next `/_readiness` poll returns 503) and only then sleeps a fixed 5-second grace period before starting the graceful connection drain — the grace exists specifically to let Kubernetes observe the failing readiness probe and stop routing new traffic before any listener closes."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs"
  - statement: "The chart's README documents that object-storage reachability is probed at relay startup only when `BUZZ_GIT_CONFORMANCE_PROBE` is enabled (the default); a failure there is startup-fatal, so readiness never opens at all in that case. If an operator disables that startup probe, `/_readiness` itself does not test object storage — only Postgres, Redis, and the deletion-fence schema, per the three checks above."
    entry_class: FACT
    evidence:
      - "deploy/charts/buzz/README.md"
  - statement: "Mesh peer gossip reuses the same `shutting_down` flag as a coarser 'would this pod pass readiness' proxy for its own heartbeat gate (`spawn_registry_heartbeat`'s predicate is `!shutting_down`), but that predicate checks only the shutdown flag — it does not re-run the Postgres/Redis/deletion-catalog checks `readiness_handler` performs, so it is not the same readiness determination the HTTP probe makes."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/mesh_boot.rs"
  - statement: "Issue #1143's definition of done requires this node to define the readiness concept in one sentence, state its boundary against what must not be confused with it (specifically liveness), link related implementation/verification/corpus nodes without duplicating their content, and be checked against the recorded repository revision."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1143 definition of done"
---

# Concept: Readiness Probe

The readiness probe is how the relay tells its orchestrator "I am running, but not yet
(or no longer) fit to receive traffic" — distinct from merely being alive.

## Definition

The **readiness probe** is the relay's `GET /_readiness` endpoint
(`readiness_handler` in `crates/buzz-relay/src/router.rs`). It answers one question:
*can this pod correctly serve a request right now?* That is a stronger, narrower
claim than "is the process alive" — a process can be alive (accepting TCP
connections, running its event loop) while still being unfit to serve, for example
because its Postgres pool is unreachable or it is mid-shutdown and draining
in-flight work.

Readiness is computed, not assumed. On every poll, the handler:

1. Returns `503` immediately if `state.shutting_down` is `true` — no dependency
   check runs once shutdown has begun; the pod has already decided it is not
   ready.
2. Otherwise runs three checks concurrently, each bounded by one shared 2-second
   timeout: Postgres reachability (`Db::ping`, a bare `SELECT 1`), Redis pool
   availability (`redis_pool.get().await.is_ok()`), and the deletion-fence schema
   shape (`validate_deletion_serving_catalog`, which asserts the `communities`
   table actually carries the `deletion_state`, `deletion_fence_generation`, and
   `deleted_at` columns the deletion-serving code path depends on — a schema-shape
   assertion, not just "can I open a connection").
3. Returns `200 {"status": "ready"}` only if all three pass; otherwise `503` with
   a body naming exactly which dependency failed, so an operator reading the
   response body (not just the status code) can tell Postgres from Redis from a
   missing deletion-fence column.

**What readiness is not.** It is not the same thing as **liveness**
(`GET /_liveness`, `liveness_handler`): liveness takes no application state at all
and unconditionally returns `200 OK`. Liveness answers "should Kubernetes restart
this container" (a hung or crashed process); readiness answers "should Kubernetes
route traffic to this pod right now" (a healthy process that is temporarily unfit
to serve). Conflating the two would make a slow Postgres failover restart every
pod in the deployment instead of simply routing around them — which is exactly
the failure mode separate liveness/readiness probes exist to prevent.

## Where it runs

Both `/_liveness` and `/_readiness` are registered twice: once on the main app
router (reachable over the same port as WebSocket/API traffic) and once on a
dedicated **health-only router**, bound on its own TCP port
(`config.health_port`, default `8080`). The health-only router's own field doc
states the reason directly: it exists so K8s probes bypass Istio and the app's
auth middleware entirely — the orchestrator's probe traffic should never depend
on, or be blocked by, the same auth/service-mesh layers that gate real client
traffic.

```mermaid
flowchart TD
    P["Kubernetes kubelet<br/>readinessProbe"] -->|"GET /_readiness<br/>every 5s"| H["health-only router<br/>:health_port (default 8080)"]
    H --> RH["readiness_handler"]
    RH -->|"shutting_down == true"| R503a["503 shutting_down"]
    RH -->|"shutting_down == false"| CHK["tokio::join! (2s timeout)"]
    CHK --> PG["Db::ping()<br/>SELECT 1"]
    CHK --> RD["redis_pool.get()"]
    CHK --> DC["validate_deletion_serving_catalog()"]
    PG & RD & DC -->|"all ok"| R200["200 ready"]
    PG & RD & DC -->|"any fail / timeout"| R503b["503 not_ready<br/>+ which dependency failed"]
```

## Use cases

- **Rolling deploys and pod restarts.** A newly started pod's dependencies
  (Postgres pool warmup, Redis connection) may not be ready the instant the
  process starts listening. Readiness — gated by the chart's own
  `startupProbe`/`readinessProbe` combination — keeps Kubernetes from routing
  live traffic to a pod before its checks actually pass, without needing the
  liveness probe (and its restart behavior) to also encode that logic.
- **Graceful shutdown.** On `SIGTERM`, `shutting_down` flips to `true`
  immediately, so the very next readiness poll fails — well before the fixed
  5-second grace period and the subsequent connection drain even begin. This is
  the mechanism that lets Kubernetes stop routing *new* traffic to a
  terminating pod while the pod finishes draining the traffic it already has.
- **Dependency-outage isolation.** If one pod's Postgres or Redis connection
  degrades independently of its peers (a partial network partition, a stuck
  connection pool), that pod's readiness fails while its peers keep serving —
  the orchestrator routes around exactly the unhealthy replica instead of an
  operator having to intervene by hand.
- **Operator debugging.** Because the `503 not_ready` body names which
  dependency failed (`postgres`, `redis`, `deletion_catalog`), an operator
  curling `/_readiness` directly (the chart's own `NOTES.txt` documents doing
  exactly this via `kubectl port-forward`) gets a specific answer, not just a
  failing HTTP status.

## Comparison: the relay's four health-adjacent signals

| Endpoint / mechanism | Checks | Answers |
|---|---|---|
| `/_liveness` | Nothing — always `200 OK` | "Is the process alive enough not to be restarted?" |
| `/_readiness` | Shutdown flag, then Postgres, Redis, deletion-fence schema (2s timeout) | "Should traffic be routed to this pod right now?" |
| `/_status` | None of the above — reports service name, version, uptime, build identity | "What build/version is running, and for how long?" |
| Mesh heartbeat gate (`spawn_registry_heartbeat`) | Only the `shutting_down` flag (`!shutting_down`) | A coarser, mesh-internal "would this pod currently pass readiness" proxy — it does not re-run the Postgres/Redis/deletion-catalog checks, so it is not equivalent to a real `/_readiness` poll. |

## Scope and omissions

**This document covers** the readiness probe specifically: what `readiness_handler`
checks, in what order, with what timeout and response shape; where it is served and
why on a separate port; and its boundary against liveness, `/_status`, and the
mesh's own internal readiness proxy.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The liveness probe in depth (its own handler, restart semantics, `startupProbe` interaction) | The `layers/observability/liveness.md` node (issue #1138) — not yet merged at the checked revision, so no `relationships` edge is declared here (see below) |
| The umbrella overview of all relay health-check endpoints together | The `layers/observability/health-checks.md` node (issue #1137), being authored in parallel |
| The mesh membership/heartbeat protocol itself, beyond the one `shutting_down`-flag detail cited above | Not this node's subject |
| The graceful-shutdown drain sequence in full (jitter, per-connection close-frame acks, the 30s hard-drain timeout) | `crates/buzz-relay/src/main.rs`'s own `serve`/`GRACEFUL_DRAIN_TIMEOUT` doc comments; a candidate for its own corpus node, not duplicated here |
| The deletion-fence catalog/schema itself (why those three columns exist, what depends on them) | `crates/buzz-db/src/store/deletion.rs`; a candidate for its own corpus node |

**No `relationships` declared.** Checked immediately before finalizing this front
matter: `git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus` lists
no `layers/` directory at all yet, so neither the liveness node (#1138) nor any other
sibling observability node has an `id` to resolve against on the branch this change
would merge into. Declaring an edge now would validate on this worktree and still
fail once the corpus's own AGENTS.md-documented merge-target rule applies. The
natural edge — `references` (or a more specific type, once one exists) from this
node to `layers-observability-liveness` — is left for a later backfill pass once
that sibling merges.

**Expected but not verified when this node was written:**

- **No dedicated automated test was found exercising `readiness_handler` directly**
  (no match for `readiness` under any `tests/` directory in `buzz-relay` or
  `buzz-test-client`). Its behavior is documented here from reading the handler's
  source directly, not from a passing test asserting the response shapes described
  above.
- **Whether `BUZZ_GIT_CONFORMANCE_PROBE` is actually enabled by default in every
  deployment** was read from the chart's own README prose, not independently
  re-derived from the relay's own default-config source in this pass.
