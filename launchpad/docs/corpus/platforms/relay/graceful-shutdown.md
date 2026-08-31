---
id: platforms-relay-graceful-shutdown
type: platforms
status: draft
origin: launchpad
audiences:
  - developer
  - operator
  - agent
evidence:
  - statement: "This node was authored and checked against repository revision 131b02f989684117d9ab1dd426f1673fa638e523."
    entry_class: FACT
    evidence:
      - "commit 131b02f989684117d9ab1dd426f1673fa638e523"
  - statement: "node.schema.json's type enum has thirteen members, including platforms; at the recorded revision, launchpad/docs/corpus/templates/ contains no platforms-specific template, so per AGENTS.md's documented no-template path this node is written against node.schema.json directly rather than against an authoritative platforms template."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
      - "launchpad/docs/corpus/AGENTS.md"
  - statement: "templates/component.md's own front matter, section shape (Responsibility, Public interface, Dependencies, Boundary, Relationships, Scope and omissions) and stated subject -- one software component documented as a standalone knowledge artifact -- is a structurally close analog for this node's subject; this node borrows that shape but not that template's type: implementation, following the same type: platforms convention the sibling platforms/relay/connection-manager.md node (issue #1267, unmerged branch task/1267-relay-connection-manager) already established for this batch."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/templates/component.md"
      - "launchpad/docs/corpus/schema/node.schema.json"
    confidence: 0.7
  - statement: "crates/buzz-relay/src/main.rs's serve() function carries a doc comment (immediately preceding it) stating the full shutdown budget in prose: a fixed 5-second grace period (readiness returns 503, then the process sleeps 5s so Kubernetes stops routing new traffic before any listener closes) followed by a GRACEFUL_DRAIN_TIMEOUT of 30 seconds that force-exits the process if exceeded, for a total worst case of 35 seconds from SIGTERM to forced exit, which the comment states fits inside the Helm chart's terminationGracePeriodSeconds: 60 with headroom."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:1244-1287"
  - statement: "shutdown_signal() waits for either a Unix SIGTERM (via tokio::signal::unix::signal(SignalKind::terminate())) or Ctrl+C (tokio::signal::ctrl_c()), racing the two with tokio::select!; on non-Unix platforms it waits on ctrl_c() alone."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:1448-1463"
  - statement: "serve()'s shutdown task, spawned once per process via tokio::spawn, runs the full orchestration: on shutdown_signal() resolving, it (1) stores true into state.shutting_down (an Arc<AtomicBool>), (2) sleeps 5 seconds (the grace period), (3) sends true on a tokio::sync::watch channel that every axum::serve listener subscribes to as its with_graceful_shutdown future, (4) spawns the hard-shutdown timer task, then (5) calls drain_conn_manager.drain_all() (jitter off, the default) or .drain_all_jittered(drain_jitter_ms).await (jitter on) to close every live WebSocket connection, and (6) returns the hard-shutdown timer's AbortHandle to the caller."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:1336-1369"
  - statement: "The hard-shutdown timer is a separate tokio::spawn'd task that sleeps for GRACEFUL_DRAIN_TIMEOUT (30 seconds, a const defined immediately above serve()) and then calls std::process::exit(1) directly, bypassing Rust's normal drop glue; its AbortHandle is held by the caller and only aborted after the awaited axum::serve future(s) and the connection-drain step have all completed, so a hung drain cannot be silently ignored -- it is a genuine backstop, not dead code."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:1287"
      - "crates/buzz-relay/src/main.rs:1347-1352"
      - "crates/buzz-relay/src/main.rs:1368"
      - "crates/buzz-relay/src/main.rs:1416-1420"
      - "crates/buzz-relay/src/main.rs:1441-1444"
  - statement: "serve() binds up to three HTTP/WebSocket listeners depending on configuration -- a TCP listener on config.bind_addr (always), an optional Unix domain socket listener on config.uds_path (Unix only, if configured), and a health-only TCP listener on config.health_port (always, spawned separately and never wired to the shared shutdown watch channel) -- plus a fourth, already-bound Prometheus metrics listener the doc comment names but this function does not itself construct."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:1244-1256"
      - "crates/buzz-relay/src/main.rs:1296-1302"
      - "crates/buzz-relay/src/main.rs:1371-1373"
      - "crates/buzz-relay/src/main.rs:1376-1422"
  - statement: "Both the TCP and UDS axum::serve calls are wired with .with_graceful_shutdown(async move { rx.changed().await.ok(); }), where rx is an independent .subscribe() handle on the same shutdown_tx watch channel the shutdown task sends true on; each listener therefore stops accepting new connections and lets axum finish in-flight requests the moment that one send fires, and the caller awaits the returned future before proceeding, in both the UDS+TCP branch and the TCP-only branch."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:1395-1414"
      - "crates/buzz-relay/src/main.rs:1430-1439"
  - statement: "The health-only listener (bound in serve() at its own tokio::spawn, using axum::serve(health_listener, health_router).await.ok()) is not subscribed to the shutdown watch channel and has no graceful-shutdown wiring of its own; it is only ever stopped by the whole process exiting, which is consistent with its purpose of continuing to answer readiness/liveness probes with a 503-carrying JSON body while the rest of the process drains."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:1296-1302"
  - statement: "router.rs's readiness_handler checks state.shutting_down first and, if true, returns 503 with a JSON body {\"status\": \"shutting_down\"} immediately, before running its own 2-second-timeout Postgres/Redis/deletion-catalog connectivity check -- so a draining pod always reports not-ready regardless of whether its dependencies are still reachable."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs:409-419"
  - statement: "router.rs's WebSocket-upgrade handler checks state.shutting_down a second time, independently of the readiness probe, immediately before completing a WebSocket upgrade; if the flag is set it returns 503 \"relay restarting\" instead of upgrading, with an inline comment explaining that readiness 503 alone only stops Kubernetes from routing new traffic, while a direct or already-in-flight upgrade can still reach this handler during the 5-second pre-drain grace window."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs:358-372"
  - statement: "config.rs defines MAX_DRAIN_JITTER_MS as a pub const of 20_000 (20 seconds), with a doc comment stating it leaves ten seconds of the 30-second hard-drain budget for WebSocket close-frame delivery after the final delayed cancellation; Config::from_env() parses BUZZ_DRAIN_JITTER_MS, treating an unset or empty/whitespace-only value as 0 (jitter off, the default, reproducing the previous all-at-once close), rejecting a non-integer value as ConfigError::InvalidValue, and .min()-clamping any parsed value to MAX_DRAIN_JITTER_MS."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/config.rs:112-114"
      - "crates/buzz-relay/src/config.rs:130-143"
      - "crates/buzz-relay/src/config.rs:580-592"
  - statement: "After serve() returns, main() calls state.community_revalidator_cancel.cancel() (a CancellationToken field on AppState, constructed fresh per-process and shared with the spawned run_community_revalidator background task), then awaits audit_shutdown.drain(Duration::from_secs(5)), then -- if OTEL was enabled -- calls the tracer provider's .shutdown() to flush pending spans before the function returns Ok(()), in that fixed order."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:1142-1160"
      - "crates/buzz-relay/src/state.rs:652"
      - "crates/buzz-relay/src/state.rs:872"
  - statement: "AuditShutdownHandle::drain(self, timeout) is documented as independent of Arc<AppState> lifetime specifically so it still works even when background tasks (reaper, pubsub, health) hold their own state clones; it cancels a CancellationToken the audit worker task selects on, then awaits the worker's JoinHandle under a tokio::time::timeout, logging one of three outcomes: clean drain, a worker panic, or a timeout that proceeds to exit anyway rather than blocking shutdown indefinitely."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/state.rs:1320-1343"
  - statement: "No explicit close/shutdown call for the Postgres connection pool or the Redis deadpool appears anywhere in main.rs's shutdown path (serve(), the post-serve() cleanup, or shutdown_signal()); both pools are only ever dropped implicitly -- either via normal Rust drop glue when the process exits after main() returns Ok(()), or not at all on the hard-shutdown-timeout path, since std::process::exit(1) terminates the process without running destructors."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:1142-1446"
  - statement: "deploy/charts/buzz/values.yaml sets terminationGracePeriodSeconds: 60 for the relay pod, which the serve() doc comment cites directly as the budget the 35-second (5s grace + 30s hard-drain) worst case must fit inside, with the comment noting this leaves headroom but assumes no preStop hook adds further delay."
    entry_class: FACT
    evidence:
      - "deploy/charts/buzz/values.yaml:118"
      - "deploy/charts/buzz/values.yaml:192"
  - statement: "A separate, BUZZ_MESH-gated inter-relay mesh subsystem (crates/buzz-relay/src/mesh_boot.rs) spawns its own drain watcher that reacts to the same shutting_down flag flipping -- gossiping draining=true to mesh peers, generation-fencing locally-owned huddle leases, and clearing the mesh's Redis ready-registry record -- entirely independently of the serve()-level orchestration this node documents; boot_mesh() is a no-op when BUZZ_MESH=off (the default), so this mesh-side drain behavior does not run in a default deployment."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/mesh_boot.rs:1-20"
      - "crates/buzz-relay/src/mesh_boot.rs:466-485"
  - statement: "The corpus node architecture-flows-websocket-connection exists on origin/launchpad and documents the WebSocket connection's connect -> NIP-42-authenticate -> terminate request/response sequence, not the process-level shutdown orchestration this node covers; the two nodes' subjects do not overlap enough to warrant a references edge, since shutdown is an event acting on already-established connections rather than a step inside that flow's own documented sequence."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/architecture/flows/websocket-connection.md"
    confidence: 0.65
  - statement: "ConnectionManager::drain_all and drain_all_jittered themselves (crates/buzz-relay/src/state.rs:397-507) already exist on origin/launchpad at the recorded revision -- only the corpus node documenting them, platforms-relay-connection-manager (issue #1267, branch task/1267-relay-connection-manager), is unmerged. Per this batch's own convention (and AGENTS.md's rule that a declared relationship target must resolve against the merge-target branch), no relationships.depends-on or .references edge toward that node id is declared in this node's front matter, even though this node's prose names it for a human reader's benefit; the edge should be added once #1267 merges."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/state.rs:397-507"
      - "commit 062eeffc8 (task/1267-relay-connection-manager, unmerged) -- the corpus node itself, not the code it documents"
---

# Graceful shutdown (buzz-relay)

`crates/buzz-relay/src/main.rs`'s `serve()` function and the cleanup that
runs immediately after it returns are the relay process's mechanism for
turning a SIGTERM (or Ctrl+C) into an orderly exit: stop routing new traffic,
let in-flight work finish or time out, close every live WebSocket connection,
flush the audit log and OpenTelemetry spans, and only then let the process
end -- with a hard timer that force-exits if any of that takes too long. This
node answers: what triggers shutdown, what order the shutdown steps run in,
how long each step is allowed to take, and what a client or operator observes
while it happens.

No `platforms`-specific template exists in `launchpad/docs/corpus/templates/`
at the recorded revision. Per `AGENTS.md`'s documented no-template path, this
node is written directly against `node.schema.json`; its body borrows
`templates/component.md`'s section shape as a structurally close analog,
using `type: platforms` rather than that template's `type: implementation`,
following the convention the sibling `platforms/relay/connection-manager.md`
node (issue #1267) already established for this batch.

## Responsibility

`serve()` is the single place the relay process decides *when* to stop and
*in what order* to tear things down. It does not itself close individual
WebSocket connections (`ConnectionManager::drain_all` /
`drain_all_jittered` do that -- see *Boundary*) and it does not itself decide
what a live connection's close frame looks like. What it owns is the
orchestration: racing a signal future, flipping a shared flag two other
code paths read, running a fixed grace period, fanning a single shutdown
signal out to every listener, invoking the connection drain, and bounding
the whole sequence with a hard timer that will kill the process outright if
the graceful path stalls.

## Public interface

| Item | Kind | Contract | Evidence |
|---|---|---|---|
| `serve` | async fn | Binds the TCP/UDS/health listeners and runs them until a shutdown signal fires, at which point it drives the full teardown described below before returning. | `crates/buzz-relay/src/main.rs:1289-1446` |
| `shutdown_signal` | async fn | Resolves on SIGTERM (Unix) or Ctrl+C; the trigger `serve()`'s shutdown task waits on. | `crates/buzz-relay/src/main.rs:1448-1463` |
| `GRACEFUL_DRAIN_TIMEOUT` | const | `30s` hard-drain backstop, started after the 5s grace; the process force-exits via `std::process::exit(1)` if exceeded. | `crates/buzz-relay/src/main.rs:1287` |
| `MAX_DRAIN_JITTER_MS` | const | `20_000` (20s); upper bound `Config::from_env()` clamps `BUZZ_DRAIN_JITTER_MS` to, leaving 10s of the hard-drain budget for close-frame delivery. | `crates/buzz-relay/src/config.rs:112-114` |
| `AppState.shutting_down` | field (`Arc<AtomicBool>`) | Set `true` once, by the shutdown task, immediately on signal receipt; read by the readiness probe and the WebSocket-upgrade handler. | `crates/buzz-relay/src/main.rs:1338`, `crates/buzz-relay/src/router.rs:366`, `:413` |
| `AuditShutdownHandle::drain` | async fn | Cancels the audit worker, awaits it under a timeout, and logs clean-drain / panic / timeout as three distinct outcomes. | `crates/buzz-relay/src/state.rs:1320-1343` |
| `AppState.community_revalidator_cancel` | field (`CancellationToken`) | Cancelled by `main()` right after `serve()` returns, stopping the periodic community-revalidation background task. | `crates/buzz-relay/src/state.rs:652`, `crates/buzz-relay/src/main.rs:1143` |

## Dependencies

**Depends on** (this orchestration requires these to build/run):

| Component | Why | Evidence |
|---|---|---|
| `tokio` (`signal`, `sync::watch`, `time`, `task`) | Signal waiting (`ctrl_c`, Unix `SIGTERM`), the shutdown fan-out channel, the grace/hard-drain sleeps, and the spawned shutdown/hard-timer tasks. | `crates/buzz-relay/src/main.rs:1304-1369` |
| `axum::serve(...).with_graceful_shutdown(...)` | The per-listener mechanism that stops accepting new connections and drains in-flight requests once its future resolves. | `crates/buzz-relay/src/main.rs:1398-1414`, `:1435-1437` |
| `ConnectionManager` (`platforms-relay-connection-manager`, #1267) | `drain_all` / `drain_all_jittered` are the functions this orchestration calls to close every live WebSocket; their internals are that node's subject, not this one's. | `crates/buzz-relay/src/main.rs:1357-1361` |
| `AuditShutdownHandle` | The audit-worker drain this node's post-`serve()` cleanup calls before returning. | `crates/buzz-relay/src/state.rs:1320-1343` |
| `deploy/charts/buzz/values.yaml`'s `terminationGracePeriodSeconds` | The Kubernetes-side budget this orchestration's own 35s worst case is designed to fit inside. | `deploy/charts/buzz/values.yaml:192` |

**Depended on by** (these require this orchestration or observe its effects):

| Component | Why | Evidence |
|---|---|---|
| `crates/buzz-relay/src/router.rs`'s readiness and WebSocket-upgrade handlers | Both read `state.shutting_down` to change their response the instant shutdown starts, independently of each other. | `crates/buzz-relay/src/router.rs:366`, `:409-419` |
| Kubernetes (readiness probe + `terminationGracePeriodSeconds`) | Readiness flipping to 503 is how the platform stops routing new traffic; the grace period is sized against this orchestration's documented worst case. | `crates/buzz-relay/src/main.rs:1244-1287` |
| `crates/buzz-relay/src/mesh_boot.rs`'s drain watcher (when `BUZZ_MESH` is enabled) | Reacts to the same `shutting_down` flag to gossip `draining=true` and clear the mesh ready-registry record, independently of the orchestration this node documents. | `crates/buzz-relay/src/mesh_boot.rs:466-485` |

## Boundary

This node does not describe:
- **Per-connection close mechanics.** `ConnectionManager::drain_all` and
  `drain_all_jittered` -- the 1012 close code, the sticky draining flag, the
  jittered-delay-plus-flush-acknowledgement path -- are
  `platforms-relay-connection-manager`'s subject (#1267). This node
  documents only that `serve()` calls one or the other depending on
  `drain_jitter_ms`, not what happens inside them.
- **The WebSocket request/response sequence.** Connect →
  NIP-42-authenticate → terminate is `architecture-flows-websocket-connection`'s
  subject. Shutdown acts on already-established connections; it is not a
  step inside that flow.
- **The mesh subsystem's own drain behavior.** `mesh_boot.rs`'s drain
  watcher (gossiping `draining=true`, fencing huddle leases, clearing the
  ready-registry record) reacts to the same `shutting_down` flag but is a
  separate, `BUZZ_MESH`-gated subsystem this node does not describe beyond
  naming its existence.
- **Explicit datastore-connection teardown**, because there isn't any to
  describe: no Postgres-pool or Redis-pool close call exists in the
  shutdown path at the recorded revision. See *Scope and omissions* below.
- **How readiness/liveness probes are wired into Kubernetes** beyond citing
  the chart's `terminationGracePeriodSeconds` value this orchestration's
  budget is sized against -- deployment topology itself is
  `architecture/deployment/kubernetes.md`'s subject.

## Relationships

None declared. `architecture-flows-websocket-connection` exists on
`origin/launchpad` but its subject (the connection's own request/response
sequence) does not overlap this node's subject (process-level shutdown
orchestration) closely enough to warrant a `references` edge -- see the
`INFERENCE` entry above. `platforms-relay-connection-manager` (#1267) is the
closest conceptual neighbor and is named throughout this node's prose, but it
exists only on the unmerged branch `task/1267-relay-connection-manager`, not
on `origin/launchpad`, so per this batch's convention (and `AGENTS.md`'s rule
that a declared relationship target must resolve against the merge-target
branch) no edge to it is declared here. The edge should be added once #1267
merges.

## Scope and omissions

**This node covers** the process-level graceful-shutdown orchestration in
`crates/buzz-relay/src/main.rs`: what triggers it (SIGTERM/Ctrl+C), the
`shutting_down` flag and its two independent readers, the fixed 5-second
grace period, the `watch`-channel fan-out that stops every `axum::serve`
listener from accepting new work, the hard-shutdown timer and its
`std::process::exit(1)` escape hatch, the point at which the connection
drain is invoked (without its internals), and the post-`serve()` cleanup
order (community-revalidator cancellation, audit-worker drain, OTEL flush).

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| `ConnectionManager::drain_all` / `drain_all_jittered` internals | `platforms-relay-connection-manager` (#1267), unmerged at time of writing |
| The WebSocket connect/authenticate/terminate sequence | `architecture-flows-websocket-connection` |
| The mesh subsystem's own `BUZZ_MESH`-gated drain watcher | Not yet a corpus node at the recorded revision |
| Kubernetes deployment topology and probe wiring beyond the grace-period budget | `architecture/deployment/kubernetes.md` |
| A `platforms`-specific template's required sections, once one exists | Whichever future issue authors that template |

**Expected but not verified when this node was written:**

- Whether the absence of an explicit Postgres/Redis pool close is an
  intentional design choice (relying on process exit to release the
  connections cleanly) or an unexamined gap -- this node states the observed
  fact (no such call exists in the shutdown path) but did not find a design
  document confirming the reasoning either way, and specifically did not
  verify what happens to in-flight database queries when
  `std::process::exit(1)` fires mid-query on the hard-shutdown-timeout path.
- Real-world timing of the 5s-grace-plus-30s-hard-drain budget against
  actual Kubernetes rolling-restart behavior in the staging/production
  cluster -- the 35-second worst case and its fit inside
  `terminationGracePeriodSeconds: 60` are read from source and chart values,
  not measured from a live drain event.
