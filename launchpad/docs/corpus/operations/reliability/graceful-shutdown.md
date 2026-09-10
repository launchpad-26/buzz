---
id: operations-reliability-graceful-shutdown
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
  - statement: "buzz-relay's shutdown task is triggered by shutdown_signal(), which resolves on Ctrl+C (tokio::signal::ctrl_c(), all platforms) or, on Unix, SIGTERM (tokio::signal::unix::signal(SignalKind::terminate())), whichever fires first."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:1449-1463"
  - statement: "Once shutdown_signal() resolves, the spawned shutdown task stores true into state.shutting_down (an Arc<AtomicBool>, Ordering::Relaxed) and logs \"Shutdown signal received — readiness now returns 503\" before doing anything else."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:1336-1339"
  - statement: "readiness_handler checks state.shutting_down before any Postgres or Redis connectivity check and returns 503 with body {\"status\": \"shutting_down\"} immediately whenever it is true."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs:409-419"
  - statement: "The WebSocket-upgrade handler independently checks state.shutting_down after a successful upgrade negotiation and refuses with 503 \"relay restarting\"; an inline comment states this exists because readiness alone only stops Kubernetes routing new traffic, while a direct or in-flight upgrade can still reach the handler during the pre-drain grace window."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs:360-368"
  - statement: "After setting the shutdown flag, the shutdown task sleeps a fixed 5 seconds, then sends true on a tokio::sync::watch channel (shutdown_tx) that every axum listener's with_graceful_shutdown future subscribes to; a code comment states this grace exists so Kubernetes stops routing new traffic before any listener closes."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:1340-1343"
  - statement: "GRACEFUL_DRAIN_TIMEOUT is a 30-second constant. Immediately after sending the watch signal, the shutdown task spawns a task that sleeps this duration and, if it fires, force-exits the whole process via std::process::exit(1) — the hard ceiling on everything after the 5-second grace, not on the grace itself."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:1287"
      - "crates/buzz-relay/src/main.rs:1347-1351"
  - statement: "With the backstop running, the shutdown task drains every live WebSocket connection using drain_all() (the default, when BUZZ_DRAIN_JITTER_MS is unset or 0) or drain_all_jittered(jitter_ms) (used when jitter is configured non-zero)."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:1357-1361"
  - statement: "drain_all() sets a sticky draining flag, then for every registered connection queues a 1012 Service Restart close frame on its control channel and cancels its CancellationToken, returning as soon as every close is queued without waiting for delivery."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/state.rs:418-431"
  - statement: "drain_all_jittered(jitter_ms) sets the same sticky flag before its first await, then for every connection delays a uniformly random 1..=jitter_ms milliseconds before sending its 1012 close over a dedicated channel and awaiting a flush acknowledgement bounded by RESTART_CLOSE_ACK_TIMEOUT (5 seconds); a full/closed channel or a timed-out acknowledgement falls back to cancelling the connection outright instead of waiting further."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/state.rs:465-505"
      - "crates/buzz-relay/src/state.rs:88"
  - statement: "MAX_DRAIN_JITTER_MS is a 20-second (20_000ms) constant. BUZZ_DRAIN_JITTER_MS is parsed as a non-negative integer of milliseconds, defaults to 0 (jitter off) when unset or blank, and is capped at MAX_DRAIN_JITTER_MS when a larger value is supplied."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/config.rs:114"
      - "crates/buzz-relay/src/config.rs:580-590"
  - statement: "main.rs's own doc comment states the worst-case single-socket teardown time from SIGTERM as 5s grace + up to 20s jitter + up to 5s close-frame ack = 30s landing inside the 30s hard-drain backstop, for a stated total worst case of 5s + 30s = 35s from SIGTERM to forced exit — which it states fits inside the Helm chart's terminationGracePeriodSeconds: 60, leaving headroom that assumes no preStop hook adds further delay."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:1259-1287"
  - statement: "deploy/charts/buzz/values.yaml sets relay.terminationGracePeriodSeconds to 60, and deploy/charts/buzz/templates/deployment.yaml wires that value directly into the Pod spec's terminationGracePeriodSeconds field; no preStop lifecycle hook is defined anywhere in that deployment template."
    entry_class: FACT
    evidence:
      - "deploy/charts/buzz/values.yaml:192"
      - "deploy/charts/buzz/templates/deployment.yaml:37"
      - "deploy/charts/buzz/templates/deployment.yaml"
  - statement: "deploy/charts/buzz/values.yaml configures the relay's readinessProbe with periodSeconds: 5 and failureThreshold: 3, and its livenessProbe with periodSeconds: 10 and failureThreshold: 3."
    entry_class: FACT
    evidence:
      - "deploy/charts/buzz/values.yaml:143-158"
  - statement: "Because Kubernetes' readinessProbe here polls every 5 seconds with a failure threshold of 3, a route-removal path relying solely on repeated probe failure could take up to 15 seconds to notice a pod has stopped being ready — longer than the shutdown task's fixed 5-second in-process grace — which is a plausible reason the WebSocket-upgrade handler carries its own independent shutting_down check rather than relying on readiness alone. This repository's source does not state that reasoning explicitly, and whether Kubernetes' own Service-endpoint removal on a pod entering Terminating state (as distinct from probe-failure-triggered removal) makes this moot was not checked here."
    entry_class: INFERENCE
    evidence:
      - "deploy/charts/buzz/values.yaml:143-158"
      - "crates/buzz-relay/src/main.rs:1340-1341"
      - "crates/buzz-relay/src/router.rs:360-368"
    confidence: 0.6
  - statement: "docker-compose.yml and docker-compose.harness.yml each define only dependency services — docker-compose.yml runs postgres, redis, adminer, keycloak, minio, minio-init and prometheus, and docker-compose.harness.yml runs postgres, redis, minio and minio-init — and neither file defines a service that runs buzz-relay itself, so no stop_grace_period setting in either file governs the relay process in this repository."
    entry_class: FACT
    evidence:
      - "docker-compose.yml"
      - "docker-compose.harness.yml"
  - statement: "After every listener's axum::serve future returns, main() cancels state.community_revalidator_cancel, then calls audit_shutdown.drain(Duration::from_secs(5))."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:1142-1150"
  - statement: "AuditShutdownHandle::drain(timeout) cancels the audit worker's CancellationToken and awaits its JoinHandle bounded by timeout, logging one of three outcomes — drained cleanly, the worker task panicked, or the timeout expired and \"exiting anyway\" — and the process continues its teardown regardless of which of the three occurs."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/state.rs:1325-1341"
  - statement: "The audit worker's own loop, on observing its cancellation token fire, closes its receiver (rejecting further sends) and then drains every entry already buffered in the channel until none remain, logging how many entries were flushed before logging that it exited."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/state.rs:803-834"
  - statement: "The final step of main()'s post-serve teardown, run only when telemetry is enabled, calls the OTEL tracer provider's shutdown() method to flush buffered spans; an error there is logged as a warning rather than treated as fatal, after which main() returns Ok(())."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:1153-1157"
  - statement: "std::process::exit(1), called by the 30-second hard-drain backstop if it fires, terminates the process immediately without unwinding the stack or running Drop implementations, per documented Rust std library semantics; consequently that path never reaches main()'s post-serve teardown (community-revalidator cancel, audit drain, OTEL flush) at all, since those statements sit after serve()'s return in the same function the backstop task never rejoins."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay/src/main.rs:1347-1351"
      - "crates/buzz-relay/src/main.rs:1142-1157"
    confidence: 0.9
  - statement: "AppState's db field (the Postgres connection pool) and redis_pool field (a deadpool_redis::Pool) have no corresponding close/shutdown call anywhere in buzz-relay's shutdown path — neither the shutdown task nor main()'s post-serve teardown calls a pool-close method on either — so on a normal exit both pools are torn down implicitly via Rust's Drop when the last Arc<AppState> reference is released, and on the std::process::exit(1) backstop path they are not torn down via any code path at all."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay/src/state.rs:630-636"
      - "crates/buzz-relay/src/main.rs:1142-1157"
    confidence: 0.85
  - statement: "The merged sibling node layers-lifecycle-graceful-shutdown narrates buzz-relay's and buzz-acp's full shutdown sequences step by step with its own code citations, and the merged sibling node layers-lifecycle-background-workers states that nine of the ten background timer loops it inventories in buzz-relay carry no CancellationToken and are \"simply dropped along with the rest of the process when the tokio runtime shuts down\" rather than being part of any drain sequence described above."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/layers/lifecycle/graceful-shutdown.md"
      - "launchpad/docs/corpus/layers/lifecycle/background-workers.md"
  - statement: "layers-lifecycle-graceful-shutdown and layers-lifecycle-background-workers are both present, with matching id front matter, in launchpad/docs/corpus/layers/lifecycle/ on this worktree's branch (based on origin/launchpad), making them valid relationship targets."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/layers/lifecycle/graceful-shutdown.md:1-2"
      - "launchpad/docs/corpus/layers/lifecycle/background-workers.md:1-2"
  - statement: "This node was written using launchpad/docs/corpus/templates/reference.md, which was already merged on origin/launchpad at the recorded revision and directs a reference-shaped node toward a Reference-description paragraph, structured entries ordered to match the source material rather than alphabetically, an explicit Boundary statement, Relationships, and a Scope-and-omissions section carrying both what the node excludes and what was expected but not verified."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/templates/reference.md"
relationships:
  - type: references
    target: layers-lifecycle-graceful-shutdown
  - type: references
    target: layers-lifecycle-background-workers
---

# Graceful shutdown: reference

This node catalogues the timeouts, grace periods and deployment budgets that govern
`buzz-relay`'s shutdown, and states plainly what is dropped or left unbounded when a
deadline is exceeded. It is a lookup table for operators tuning shutdown behavior or
diagnosing a restart that dropped work, not a narrative of the shutdown code path —
`layers-lifecycle-graceful-shutdown` already provides that narration, step by step,
with its own code citations, and this node links to it rather than repeating it.
Scope is `buzz-relay` only; `buzz-acp`'s separate shutdown sequence is out of scope
(see *Boundary*).

## Shutdown timeline and bounds

Ordered as the sequence actually runs, from signal to process exit.

| Phase | Bound | What happens | Source |
|---|---|---|---|
| Signal received | — | `shutting_down` flips to `true`; readiness begins returning 503 immediately | `crates/buzz-relay/src/main.rs:1336-1339,1449-1463` |
| Pre-drain grace | 5s, fixed | Process sleeps so Kubernetes stops routing new traffic before any listener closes | `crates/buzz-relay/src/main.rs:1340-1341` |
| Hard-drain backstop | 30s (`GRACEFUL_DRAIN_TIMEOUT`) | If the drain below has not finished when this fires, the process force-exits via `std::process::exit(1)` | `crates/buzz-relay/src/main.rs:1287,1347-1351` |
| WebSocket drain, jitter off (default) | immediate | `drain_all()` queues a `1012 Service Restart` close and cancels every connection; returns without waiting for delivery | `crates/buzz-relay/src/state.rs:418-431` |
| WebSocket drain, jitter on | up to `MAX_DRAIN_JITTER_MS` (20s) delay, then up to `RESTART_CLOSE_ACK_TIMEOUT` (5s) ack wait, per connection | `drain_all_jittered()` spreads closes to avoid a reconnect thundering herd; a full/closed channel or a timed-out ack falls back to cancellation | `crates/buzz-relay/src/state.rs:465-505,88` |
| Post-serve: community revalidator | — | `state.community_revalidator_cancel.cancel()` | `crates/buzz-relay/src/main.rs:1142-1143` |
| Post-serve: audit drain | up to 5s | `AuditShutdownHandle::drain()` cancels and awaits the audit worker, logging clean-drain, panic, or timeout — teardown continues regardless | `crates/buzz-relay/src/main.rs:1148-1150`, `crates/buzz-relay/src/state.rs:1325-1341,803-834` |
| Post-serve: OTEL flush | — | Tracer provider `shutdown()`, only if telemetry is enabled; an error is logged, not fatal | `crates/buzz-relay/src/main.rs:1153-1157` |
| Kubernetes pod budget | 60s (`terminationGracePeriodSeconds`) | Total time Kubernetes allows before sending SIGKILL; the code's own comment states the 35s worst case fits inside this with headroom, assuming no `preStop` hook adds delay | `deploy/charts/buzz/values.yaml:192`, `deploy/charts/buzz/templates/deployment.yaml:37`, `crates/buzz-relay/src/main.rs:1259-1287` |

The stated worst case from SIGTERM to forced exit is **5s + 30s = 35s**
(`crates/buzz-relay/src/main.rs:1259-1287`), inside the 60s Kubernetes budget above but
with no `preStop` hook accounted for, since none exists in this chart.

## Configuration knobs

| Knob | Default | Effect | Source |
|---|---|---|---|
| `BUZZ_DRAIN_JITTER_MS` (env) | `0` (jitter off) | Spreads WebSocket closes across `[1, value]` ms instead of closing all at once; parsed as a non-negative integer, blank/unset treated as `0` | `crates/buzz-relay/src/config.rs:580-590` |
| `MAX_DRAIN_JITTER_MS` (Rust constant, not env-configurable) | `20_000` (20s) | Upper bound `BUZZ_DRAIN_JITTER_MS` is clamped to | `crates/buzz-relay/src/config.rs:114` |
| `GRACEFUL_DRAIN_TIMEOUT` (Rust constant, not env-configurable) | `30s` | Hard-drain backstop duration | `crates/buzz-relay/src/main.rs:1287` |
| `RESTART_CLOSE_ACK_TIMEOUT` (Rust constant, not env-configurable) | `5s` | Per-connection close-frame acknowledgement wait in the jittered drain path | `crates/buzz-relay/src/state.rs:88` |
| `relay.terminationGracePeriodSeconds` (Helm value) | `60` | Kubernetes' total budget for the whole Pod before SIGKILL | `deploy/charts/buzz/values.yaml:192`, `deploy/charts/buzz/templates/deployment.yaml:37` |
| `relay.readinessProbe.periodSeconds` / `.failureThreshold` (Helm value) | `5s` / `3` | How often, and after how many failures, Kubernetes would remove routing on probe failure alone, absent the in-process flag flip | `deploy/charts/buzz/values.yaml:143-158` |
| Docker Compose `stop_grace_period` | not applicable in this repository | Neither `docker-compose.yml` nor `docker-compose.harness.yml` runs `buzz-relay` as a compose service — both define only dependency services (Postgres, Redis, and others) | `docker-compose.yml`, `docker-compose.harness.yml` |

## What is dropped or unbounded if a deadline is exceeded

- **Hard-drain backstop fires (30s exceeded).** `std::process::exit(1)` terminates the
  process immediately, without unwinding the stack or running `Drop` implementations.
  This path never reaches `main()`'s post-serve teardown — the community-revalidator
  cancel, the audit drain, and the OTEL span flush all sit after `serve()`'s return in
  the same function the backstop task never rejoins, so all three are skipped, not
  merely delayed. (`crates/buzz-relay/src/main.rs:1347-1351,1142-1157`)
- **Audit drain times out (5s exceeded).** `AuditShutdownHandle::drain` logs "did not
  drain in time — exiting anyway" and returns; teardown continues rather than blocking
  further, so any audit entries still buffered in the channel at that moment are lost.
  (`crates/buzz-relay/src/state.rs:1325-1341`)
- **Background timer workers are not part of this sequence at all, deadline or not.**
  Per `layers-lifecycle-background-workers`, nine of `buzz-relay`'s ten catalogued
  background loops (the NIP-43 reconciler, the ephemeral-channel reaper, the reminder
  scheduler, and others) carry no `CancellationToken` and are dropped whenever the
  tokio runtime exits — this is unconditional, not a consequence of any timeout above
  being exceeded.
- **Connection pools have no explicit close call in the shutdown path.** Postgres and
  Redis connections are torn down implicitly via `Drop` on a normal exit, and are not
  torn down via any code path on the `std::process::exit(1)` backstop path, since
  `process::exit` skips destructors. (`crates/buzz-relay/src/state.rs:630-636`)

## Boundary

This node does not describe:
- `buzz-acp`'s own shutdown sequence (SIGINT/SIGTERM/owner `!shutdown`, the two 30s
  drain windows, per-agent reaping) — see `layers-lifecycle-graceful-shutdown` for that
  process's narration; this node covers `buzz-relay` only.
- The step-by-step code path that produces the timeline above — see
  `layers-lifecycle-graceful-shutdown` for the sequence narration this node's table
  summarizes into bounds and defaults.
- The full inventory of `buzz-relay`'s background timer workers or their individual
  cancellation-awareness — see `layers-lifecycle-background-workers`.
- `buzz-push-gateway`'s own Helm chart and shutdown behavior, which has its own
  `terminationGracePeriodSeconds: 60` but was not otherwise inspected here.
- Whether the current bounds, or the unclosed connection pools noted above, represent
  an accepted trade-off or an unaddressed gap — neither this node nor any source found
  while authoring it settles that question.

## Relationships

- references: `layers-lifecycle-graceful-shutdown` — the code-cited sequence narration
  this node's timeline table summarizes into bounds and configuration, without
  restating the step-by-step flow.
- references: `layers-lifecycle-background-workers` — the inventory this node's
  "dropped or unbounded" section draws on for the unconditional-drop claim about
  background timer workers.

## Scope and omissions

**This node covers** the timeouts, grace periods, and deployment-level budgets that
bound `buzz-relay`'s shutdown from SIGTERM to process exit; the Rust constants and
environment/Helm knobs that configure them; and, separately, what is dropped or left
unbounded when the hard-drain backstop or the audit-drain timeout is exceeded, or that
was never part of the drain sequence in the first place.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| `buzz-acp`'s own shutdown sequence and bounds | `layers-lifecycle-graceful-shutdown` |
| The step-by-step shutdown code path for `buzz-relay` | `layers-lifecycle-graceful-shutdown` |
| The full background-worker inventory and per-worker cancellation-awareness | `layers-lifecycle-background-workers` |
| Sibling `operations/reliability/*` concerns from this same batch (availability and others) | unmerged as of this writing, not yet owned by any merged node |
| `buzz-push-gateway`'s own chart and termination behavior | not yet owned by any corpus node |
| Whether the current bounds or the unclosed connection pools are an accepted trade-off or an unaddressed gap | not decided by any source found while authoring this node |

**Expected but not verified when this node was written:**

- **Whether Kubernetes' own Service-endpoint removal on a pod entering `Terminating`
  happens independently of readiness-probe failure** — which would make the
  probe-timing `INFERENCE` above moot — was not checked against Kubernetes' own
  documentation; this repository's source does not address it.
- **Whether any automated test exercises `buzz-relay`'s shutdown wiring end-to-end**
  was not independently re-checked here; `layers-lifecycle-graceful-shutdown` already
  states, citing a `TODO(coverage)` comment in `main.rs`, that the wiring has no
  automated test, and that claim is linked to rather than re-verified here to avoid
  restating it.
- **Whether `buzz-push-gateway`'s chart implements an equivalent graceful-shutdown code
  path** was not checked; only its Helm `terminationGracePeriodSeconds: 60` value was
  noted as existing, and that component is otherwise out of this node's `buzz-relay`-only
  scope.
