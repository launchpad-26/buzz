---
id: layers-lifecycle-graceful-shutdown
type: layers
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5."
    entry_class: FACT
    evidence:
      - "commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
  - statement: "buzz-relay's shutdown_signal() waits on either Ctrl+C (tokio::signal::ctrl_c, all platforms) or SIGTERM (tokio::signal::unix::signal(SignalKind::terminate()), Unix only), whichever arrives first, and returns once one of them fires."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:1407-1422"
  - statement: "serve()'s spawned shutdown task, once shutdown_signal() resolves, stores true into state.shutting_down (an Arc<AtomicBool>, Ordering::Relaxed) and logs before doing anything else — this flag alone, not the listener close, is what the readiness and WS-upgrade handlers observe."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:1295-1298"
  - statement: "readiness_handler returns 503 with body {\"status\": \"shutting_down\"} as its first check, before any Postgres or Redis ping, whenever state.shutting_down is true."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs:374-384"
  - statement: "The WebSocket-upgrade handler independently checks state.shutting_down and refuses a successfully-negotiated upgrade with 503 \"relay restarting\" — a second, direct-path check that exists because readiness only stops Kubernetes from routing new traffic, while an upgrade already in flight can still land on the handler during the pre-drain grace window."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs:325-333"
  - statement: "After setting the flag, the shutdown task sleeps a fixed 5 seconds (the doc comment calls this the grace period, letting Kubernetes stop routing new traffic before any listener closes) before sending true on a tokio::sync::watch channel (shutdown_tx) that every axum listener's with_graceful_shutdown future subscribes to."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:1299-1302"
      - "crates/buzz-relay/src/main.rs:1263"
  - statement: "Both the TCP listener and, when configured, the Unix-domain-socket listener are served via axum::serve(...).with_graceful_shutdown(async move { rx.changed().await.ok(); }), each on its own subscription to the same watch channel, so both stop accepting new connections/requests at the same moment the watch fires."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:1354-1372"
      - "crates/buzz-relay/src/main.rs:1389-1397"
  - statement: "Immediately after sending the watch signal, the shutdown task spawns a 30-second (GRACEFUL_DRAIN_TIMEOUT) backstop task that force-exits the whole process via std::process::exit(1) if it fires — this is the hard ceiling on everything that follows, not on the 5s grace that preceded it."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:1246"
      - "crates/buzz-relay/src/main.rs:1306-1311"
  - statement: "With the backstop running, the shutdown task drains every live WebSocket connection: drain_all() (synchronous, used when BUZZ_DRAIN_JITTER_MS is unset or 0, the default) or drain_all_jittered(jitter_ms) (used when jitter is configured, spreading closes across [1, jitter_ms] milliseconds to avoid a thundering-herd reconnect burst)."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:1312-1320"
  - statement: "drain_all() sets a sticky draining flag, then for every registered connection queues a 1012 Service Restart close frame on its control channel and cancels its CancellationToken — it returns as soon as every close is queued, without waiting for delivery."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/state.rs:418-431"
  - statement: "drain_all_jittered(jitter_ms) also sets the sticky draining flag before its first await (so a connection registering mid-shutdown self-signals immediately instead of racing the snapshot), then for every connection delays 1..=jitter_ms ms before sending its 1012 close over a dedicated RestartClose channel and awaiting a flush acknowledgement bounded by RESTART_CLOSE_ACK_TIMEOUT (5 seconds); a full/closed channel or a timed-out ack falls back to cancelling the connection outright."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/state.rs:465-507"
      - "crates/buzz-relay/src/state.rs:89"
  - statement: "The doc comment on GRACEFUL_DRAIN_TIMEOUT states the worst-case single-socket teardown time from SIGTERM as 5s grace + up to 20s jitter (MAX_DRAIN_JITTER_MS) + up to 5s close-frame ack = 30s, landing inside the 30s hard-drain backstop, for a total worst case of 5s + 30s = 35s from SIGTERM to forced exit — which the comment states fits inside the Helm chart's terminationGracePeriodSeconds: 60, leaving headroom that assumes no preStop hook adds further delay."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:1218-1245"
      - "crates/buzz-relay/src/config.rs:51"
  - statement: "After axum::serve(...) returns for every listener (i.e. after the watch fired and each listener's own accept loop drained), serve()'s caller awaits the shutdown task's join handle and aborts the 30s backstop task, then main() calls state.community_revalidator_cancel.cancel() before doing anything else."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:1375-1404"
      - "crates/buzz-relay/src/main.rs:1101-1102"
  - statement: "main() then calls audit_shutdown.drain(Duration::from_secs(5)), which cancels the audit worker's CancellationToken and awaits its JoinHandle bounded by a 5-second timeout, logging one of three outcomes: drained cleanly, the worker task panicked, or the timeout expired and the process exits anyway."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:1104-1109"
      - "crates/buzz-relay/src/state.rs:1315-1337"
  - statement: "The audit worker's own loop, on observing the cancellation token fire (via tokio::select! against audit_rx.recv()), closes the receiver — which rejects any further sends — and then drains every entry already buffered in the channel via audit_rx.recv().await until it returns None, logging how many entries were flushed."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/state.rs:800-832"
  - statement: "The final step of main()'s post-serve teardown, after the audit drain, is flushing any buffered OpenTelemetry spans by calling the tracer provider's shutdown() method (only when telemetry is enabled), logging a warning on error rather than failing the process, after which main() returns Ok(())."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:1111-1118"
  - statement: "When the optional inter-relay mesh is enabled (BUZZ_MESH), a separate drain watcher polls the same shutting_down flag and, on observing it true, gossips draining=true via the mesh membership protocol and actively drains locally-owned huddle sessions — an additional, mesh-specific reaction to the same flag documented above, not a second shutdown trigger."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/mesh_boot.rs:479-494"
  - statement: "buzz-acp's main loop creates one tokio::sync::watch shutdown channel and spawns two signal-listening tasks — one waiting on tokio::signal::ctrl_c(), one (Unix only) waiting on SIGTERM via tokio::signal::unix::signal(SignalKind::terminate()) — either of which sends on the same channel."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/lib.rs:2314-2332"
  - statement: "The identical shutdown_tx watch channel is also fired from inside the main event loop when a kind:9 event whose content is exactly \"!shutdown\", mentions this agent, and is authored by the cached owner pubkey is observed — so SIGINT, SIGTERM, and an owner's relay-published !shutdown command all converge on one shutdown path with no separate code for each trigger."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/lib.rs:2737-2760"
  - statement: "Once the watch fires, buzz-acp first drains in-flight pool-wake tasks: it re-sends the same watch (so an in-flight initialize_agent_pool observes it and reaps its own partially-spawned agents), then waits up to 30 seconds for every wake task to finish, falling back to wake_tasks.shutdown().await (an abort) if the timeout expires; any awakened pool whose result already arrived is reaped via shutdown_agent_pool()."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/lib.rs:3420-3442"
  - statement: "Next, buzz-acp waits up to a second, independent 30-second grace period for in-flight prompts: a loop selects between the pool's JoinSet completing tasks and its result channel receiving finished agents, explicitly calling agent.acp.shutdown().await on each checked-out agent as it is reaped (rather than relying on Drop) so the child process is guaranteed reaped, not merely signalled; if the grace expires, remaining tasks are aborted via pool.join_set.shutdown().await."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/lib.rs:3444-3479"
  - statement: "After that grace period (bounded or not), buzz-acp serially reaps: any results that arrived between join_set draining and the abort, every idle agent still sitting in a pool slot, and — after aborting in-flight respawn tasks — any respawn results that had already completed; every one of these calls agent.acp.shutdown().await one at a time, with no aggregate timeout wrapping the whole serial sequence."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/lib.rs:3480-3511"
  - statement: "AcpClient::shutdown() (the method every per-agent reap above calls) kills the agent's process group (or falls back to killing just the child on non-Unix or an already-reaped child), then waits up to 5 seconds for the child to exit before giving up and abandoning it to Drop/the OS — this 5-second bound is per agent, not shared across agents."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/acp.rs:422-444"
  - statement: "After all agent reaping, buzz-acp cancels any in-flight presence heartbeat task, then (if presence is enabled) attempts to publish presence \"offline\" bounded by a 2-second timeout, logging success, a publish error, or a timeout without treating any of the three as fatal to the shutdown sequence."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/lib.rs:3513-3530"
  - statement: "The last step is relay.shutdown().await, which sends a Shutdown command to the relay's background task and waits up to 5 seconds for that task to finish before aborting it — HarnessRelay's own doc comment states this exists so the relay connection closes gracefully (a WebSocket close frame) rather than being dropped/aborted immediately."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/lib.rs:3536-3538"
      - "crates/buzz-acp/src/relay.rs:958-974"
  - statement: "No code in buzz-acp's shutdown sequence establishes a shared deadline across the whole tail — the wake-task drain (30s), the in-flight-prompt drain (30s), the serial per-slot reap that follows it (no timeout of its own beyond each individual 5s AcpClient::shutdown() call), the 2s presence publish, and the 5s relay close are five independently-bounded segments with nothing summing or capping their total."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/lib.rs:3420-3538"
  - statement: "docs/remote-agents.md names this absence explicitly as \"Known Defect 7\" and states a requirement, not a description of current behavior: \"the harness MUST bound its total shutdown tail — every post-signal segment, including per-slot reaping — under one shared deadline no greater than the declared grace budget,\" with a reserved finalization slice \"no smaller than those finalizers' declared bounds — currently 2s + 5s = 7s\" held back for presence-offline and relay-close specifically, so that child-reaping degrades (skips remaining waits, force-kills) before it can consume the slice the grace period exists to protect."
    entry_class: FACT
    evidence:
      - "docs/remote-agents.md:906-917"
  - statement: "docs/remote-agents.md's own worst-case arithmetic states the post-drain reap segment alone can reach \"30 + 5×parallelism + 7\" — roughly 87 seconds at the desktop's default agent parallelism of 10, and roughly 197 seconds at the harness's configured cap of 32 — both already exceeding a 60-second grace, and states this is a lower bound on the tail because it excludes the earlier 30s wake-task drain that runs before it."
    entry_class: FACT
    evidence:
      - "docs/remote-agents.md:893-906"
  - statement: "node.schema.json's type enum includes layers as one of thirteen closed values (alongside architecture, capabilities, platforms, ...), described only as \"the corpus surface a node documents\" with no further per-value elaboration in either node.schema.json or schema/README.md's own prose table for the type field."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
      - "launchpad/docs/corpus/schema/README.md"
  - statement: "This node uses type: layers rather than flow.md's own worked-skeleton default of type: architecture, because Feature #611 (this node's parent) organizes its whole task set under a layers/lifecycle/ directory naming convention, and layers is schema.json's own dedicated enum member for that surface rather than the C4-architecture surface flow.md's skeleton defaults to — the same reasoning basis a sibling task in this batch (#1043) used for the same departure, independently re-derived here rather than copied, since #1043's own branch is unmerged and not readable from this worktree."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
    confidence: 0.7
  - statement: "The existing merged flow instance architecture/flows/websocket-connection.md sets the precedent this node otherwise follows for id shape, origin, and audiences on a corpus node documenting real Buzz product code: id derived from its path, origin: launchpad (not upstream), audiences including developer/operator/agent/reviewer as fits the content."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/flows/websocket-connection.md:1-9"
  - statement: "architecture-containers-relay and architecture-containers-agent-runtime are both present as node ids on origin/launchpad at the time this node was authored, confirmed via git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus and reading each file's own id front-matter field, making them valid relationships targets for the standing structure this flow's two actors (buzz-relay, the buzz-acp-based agent runtime) are built from."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/containers/relay.md:1-2"
      - "launchpad/docs/corpus/architecture/containers/agent-runtime.md:1-2"
relationships:
  - type: references
    target: architecture-containers-relay
  - type: references
    target: architecture-containers-agent-runtime
---

# Graceful shutdown: flow

## A note on `type`

`node.schema.json`'s `type` enum lists thirteen closed values, and `layers` is one of
them, described (both in the schema and in `schema/README.md`'s prose table) only as
naming "the corpus surface a node documents" — with no further elaboration
distinguishing it from its neighbors. `launchpad/docs/corpus/templates/flow.md`'s own
worked skeleton defaults an instance of this template to `type: architecture`,
reasoning that a flow node is a fourth member of the C4 model's diagram family. This
node departs from that default and uses `type: layers` instead, because this node's
parent, Feature #611, organizes its entire task set under a `layers/lifecycle/`
directory taxonomy — a cross-cutting technical-behavior grouping (lifecycle,
concurrency, cancellation, background work, resource cleanup, startup) distinct from
the structural C4 architecture family the `architecture/` subtree already houses. A
sibling task in this same batch run, #1043, made the identical departure for the same
Feature; its own branch is not present on `origin/launchpad` and could not be read from
this worktree, so this section restates the reasoning independently rather than
quoting #1043's text, and marks the choice `INFERENCE` (confidence 0.7) rather than
`FACT` accordingly. Everything else about this node — required sections, evidence
expectations, the Mermaid `sequenceDiagram` form — follows `flow.md` unchanged; only
the `type` value differs from its worked skeleton.

## Flow statement

Buzz runs two long-running processes that must exit cleanly rather than dropping
in-flight work: `buzz-relay` (the WebSocket/HTTP server, `architecture-containers-relay`)
and the `buzz-acp` agent harness (`architecture-containers-agent-runtime`). Both are
triggered the same conceptual way — an external signal (SIGTERM/SIGINT) or, for
`buzz-acp`, an owner-authored `!shutdown` command over the relay — and both follow the
same shape: stop admitting new work, drain what is already in flight under a bounded
timeout, flush anything durable, then exit. This node narrates both sequences as one
"graceful shutdown" idea because they are the same lifecycle pattern applied to Buzz's
two server-shaped processes, not two unrelated behaviors; it does not narrate the
desktop or mobile client apps' own teardown, which is out of scope (see *Boundary*).

## Sequence

### buzz-relay

1. `shutdown_signal()` waits on Ctrl+C or, on Unix, SIGTERM — whichever fires first.
   (`crates/buzz-relay/src/main.rs:1407-1422`)
2. The spawned shutdown task stores `true` into `state.shutting_down` (an
   `AtomicBool`) and logs. (`crates/buzz-relay/src/main.rs:1295-1298`)
3. From this moment, `readiness_handler` returns 503 `{"status":"shutting_down"}`
   before any dependency check, and the WebSocket-upgrade handler independently
   refuses a successful upgrade with 503 `"relay restarting"` — a second check that
   exists because readiness alone only stops Kubernetes routing new traffic, not an
   upgrade already mid-flight. (`crates/buzz-relay/src/router.rs:374-384`,
   `crates/buzz-relay/src/router.rs:325-333`)
4. The task sleeps a fixed 5-second grace period, then sends `true` on the
   `shutdown_tx` watch channel every listener's `with_graceful_shutdown` future
   subscribes to. (`crates/buzz-relay/src/main.rs:1299-1302`)
5. Both the TCP and (if configured) Unix-domain-socket `axum::serve` listeners stop
   accepting new connections/requests the moment the watch fires; each still
   finishes serving requests already accepted. (`crates/buzz-relay/src/main.rs:1354-1372`,
   `crates/buzz-relay/src/main.rs:1389-1397`)
6. Immediately after sending the watch signal, a 30-second (`GRACEFUL_DRAIN_TIMEOUT`)
   backstop task is spawned that force-exits the process (`std::process::exit(1)`) if
   it fires before the sequence below completes.
   (`crates/buzz-relay/src/main.rs:1246`, `crates/buzz-relay/src/main.rs:1306-1311`)
7. Every live WebSocket connection is drained: `drain_all()` (synchronous close, the
   default) or `drain_all_jittered(jitter_ms)` (delayed close spread across
   `[1, jitter_ms]` ms, with a `RESTART_CLOSE_ACK_TIMEOUT` of 5s per connection) when
   `BUZZ_DRAIN_JITTER_MS` is configured non-zero.
   (`crates/buzz-relay/src/main.rs:1312-1320`, `crates/buzz-relay/src/state.rs:418-431`,
   `crates/buzz-relay/src/state.rs:465-507`)
8. Once every listener's `axum::serve` future has returned, the caller awaits the
   shutdown task's join handle and aborts the 30s backstop.
   (`crates/buzz-relay/src/main.rs:1375-1404`)
9. `main()` cancels `state.community_revalidator_cancel`, then calls
   `audit_shutdown.drain(Duration::from_secs(5))`, which cancels the audit worker's
   token and awaits its task bounded by 5 seconds; the worker itself closes its
   receiver on cancellation and drains every already-buffered entry before exiting.
   (`crates/buzz-relay/src/main.rs:1101-1109`, `crates/buzz-relay/src/state.rs:1325-1337`,
   `crates/buzz-relay/src/state.rs:800-832`)
10. Finally, if telemetry is enabled, the OTEL tracer provider's `shutdown()` flushes
    buffered spans (errors are logged, not fatal), and `main()` returns `Ok(())`.
    (`crates/buzz-relay/src/main.rs:1111-1118`)
11. If the optional inter-relay mesh (`BUZZ_MESH`) is enabled, a separate watcher on
    the same `shutting_down` flag gossips `draining=true` to peers and drains
    locally-owned huddle sessions — an additional reaction to step 2's flag, not a
    separate trigger. (`crates/buzz-relay/src/mesh_boot.rs:479-494`)

### buzz-acp

1. A `shutdown_tx` watch channel is fed by three independent sources: a SIGINT
   listener, a SIGTERM listener (Unix only), and — inside the main event loop — a
   relay-published kind:9 event whose content is exactly `"!shutdown"` and mentions
   this agent. The third source is an authorization crossing, not a bare content
   match: the event's `pubkey` is compared against the harness's cached owner
   pubkey, and the command is silently treated as an ordinary chat message (not a
   shutdown trigger) when the sender is not the owner. All three sources converge
   on the same downstream path once accepted.
   (`crates/buzz-acp/src/lib.rs:2314-2332`, `crates/buzz-acp/src/lib.rs:2737-2760`)
2. Wake-task drain: the same watch is re-sent (so an in-flight
   `initialize_agent_pool` observes it and reaps its own partially-spawned agents),
   then the harness waits up to 30s for every pool-wake task to finish, aborting the
   remainder if the timeout expires; any awakened pool whose result already arrived
   is reaped via `shutdown_agent_pool()`. (`crates/buzz-acp/src/lib.rs:3420-3442`)
3. In-flight-prompt drain: a second, independent 30-second grace period during which
   a loop drains the agent pool's `JoinSet` and result channel, explicitly calling
   `agent.acp.shutdown().await` on each checked-out agent as it is reaped rather than
   relying on `Drop`; remaining tasks are aborted if the grace expires.
   (`crates/buzz-acp/src/lib.rs:3444-3479`)
4. Serial reap: any results that arrived between drain and abort, every idle agent
   still sitting in a pool slot, and (after aborting in-flight respawn tasks) any
   already-completed respawn results — each one calls `agent.acp.shutdown().await`
   in turn, with no aggregate timeout wrapping this sequence as a whole.
   (`crates/buzz-acp/src/lib.rs:3480-3511`)
5. Each `AcpClient::shutdown()` call in steps 3-4 kills the agent's process group (or
   falls back to killing just the child), then waits up to 5 seconds for the child to
   exit before abandoning it — a per-agent bound, not a shared one.
   (`crates/buzz-acp/src/acp.rs:422-444`)
6. Presence heartbeat is cancelled, then (if enabled) `"offline"` presence is
   published under a 2-second timeout; none of publish-error, timeout, or success is
   treated as fatal to the sequence. (`crates/buzz-acp/src/lib.rs:3513-3530`)
7. `relay.shutdown()` sends a `Shutdown` command to the relay's background task and
   waits up to 5 seconds for it to finish before aborting it, so the relay connection
   closes with a WebSocket close frame rather than being dropped.
   (`crates/buzz-acp/src/lib.rs:3536-3538`, `crates/buzz-acp/src/relay.rs:958-974`)

## Diagram

### buzz-relay

```mermaid
sequenceDiagram
    participant Signal as SIGTERM/Ctrl+C
    participant Relay as buzz-relay main
    participant Readiness as readiness/WS handlers
    participant Conns as ConnectionManager
    participant Audit as audit worker
    participant OTEL as tracer provider

    Signal->>Relay: signal received
    Relay->>Relay: shutting_down = true
    Readiness-->>Readiness: 503 shutting_down (reads flag)
    Relay->>Relay: sleep 5s grace
    Relay->>Relay: shutdown_tx.send(true)
    Relay->>Conns: drain_all() / drain_all_jittered()
    Conns-->>Relay: closed count
    Relay->>Relay: await listeners, abort 30s backstop
    Relay->>Audit: cancel + drain(5s)
    Audit-->>Relay: drained / timed out
    Relay->>OTEL: tracer_provider.shutdown()
    Relay->>Relay: return Ok(())
```

### buzz-acp

```mermaid
sequenceDiagram
    participant Trigger as SIGINT/SIGTERM/!shutdown
    participant Harness as buzz-acp main loop
    participant Pool as AgentPool
    participant Agent as AcpClient (per agent)
    participant Presence as presence publisher
    participant Relay as HarnessRelay

    Trigger->>Harness: shutdown_tx.send(())
    Harness->>Pool: drain wake tasks (30s)
    Harness->>Pool: drain in-flight prompts (30s)
    Pool->>Agent: acp.shutdown() (serial, per slot)
    Agent-->>Pool: killed / 5s timeout
    Harness->>Presence: publish offline (2s)
    Harness->>Relay: relay.shutdown() (5s)
    Harness->>Harness: return
```

## Outcome

**buzz-relay, success path.** Once `main()` returns `Ok(())`, every listener has
stopped accepting new work, every WebSocket connection has been sent a `1012 Service
Restart` close frame (or cancelled), the audit worker has flushed its buffer, and OTEL
spans have been flushed — the process then exits normally.
(`crates/buzz-relay/src/main.rs:1101-1118`)

**buzz-relay, failure/backstop path.** If the 30-second `GRACEFUL_DRAIN_TIMEOUT`
backstop fires before listener/connection drain completes, the process force-exits via
`std::process::exit(1)` immediately, skipping the audit drain and OTEL flush that would
otherwise run after `serve()` returns. Independently, if the audit worker does not
drain within its own 5-second timeout, `AuditShutdownHandle::drain` logs an error and
returns anyway — the process continues its teardown rather than blocking further.
(`crates/buzz-relay/src/main.rs:1306-1311`, `crates/buzz-relay/src/state.rs:1332-1335`)

**buzz-acp, success path.** All pool-wake tasks and in-flight prompts drain within
their 30-second windows, every agent is reaped via a bounded `AcpClient::shutdown()`,
presence is published `offline`, and the relay connection closes gracefully before the
process exits. (`crates/buzz-acp/src/lib.rs:3420-3538`)

**buzz-acp, degraded/unbounded path (Known Defect 7).** Each individual segment above
is independently bounded (30s, 30s, 5s per agent, 2s, 5s), but no code establishes a
shared deadline across the whole tail. `docs/remote-agents.md` documents this as a
requirement not yet met — "the harness MUST bound its total shutdown tail ... under one
shared deadline" with a reserved finalization slice (currently 2s + 5s = 7s) for
presence and relay close — and gives worst-case arithmetic of roughly 87 seconds at the
desktop's default agent parallelism (10) and roughly 197 seconds at the harness's
configured cap (32), both exceeding a 60-second Kubernetes grace period.
(`docs/remote-agents.md:893-917`)

## Boundary

This node does not describe:
- The standing structure of `buzz-relay` or the `buzz-acp`-based agent runtime as
  containers — see `architecture-containers-relay` and
  `architecture-containers-agent-runtime` for what each process is and how it is
  deployed; this node narrates only their shutdown behavior.
- What a capability lets a user or agent do — no capability-typed corpus node exists
  yet for either process to reference.
- The general, durable contract of the WebSocket protocol surface or the relay REST
  API that `buzz-acp` calls — only the specific shutdown-time behavior of each is
  narrated here.
- Fixing the buzz-acp shutdown-tail bound (Known Defect 7). This node documents the
  gap as it exists in code today and quotes the requirement `docs/remote-agents.md`
  states for it; implementing that bound is separately-owned work, per issue #1118's
  own "Out of scope: Changing runtime product behavior unless a separately linked
  implementation issue owns that change."
- The desktop and mobile client apps' own process teardown, or any provider-specific
  Kubernetes Pod termination mechanics (`terminationGracePeriodSeconds`, `preStop`
  hooks) beyond the one budget-arithmetic citation above.

## Relationships

- references: `architecture-containers-relay` — the container this flow's first actor
  (buzz-relay) is built from.
- references: `architecture-containers-agent-runtime` — the container this flow's
  second actor (the buzz-acp harness) is built from.

## Scope and omissions

**This node covers** the ordered, code-cited shutdown sequence of Buzz's two
long-running processes — `buzz-relay` (SIGTERM/SIGINT-triggered) and the `buzz-acp`
agent harness (SIGINT/SIGTERM/owner `!shutdown`-triggered) — from trigger through
drain to exit, on both the success path and the bounded/degraded paths each process
exposes, including `buzz-acp`'s documented but unimplemented shutdown-tail-budget
requirement (Known Defect 7).

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The standing structure of `buzz-relay` and the agent runtime as containers | `architecture-containers-relay`, `architecture-containers-agent-runtime` |
| Fixing buzz-acp's unbounded shutdown tail (Known Defect 7) | a separately-linked implementation issue, not #1118 |
| Sibling `layers/lifecycle/*` concerns — background workers, cancellation, concurrency, resource cleanup, startup | #1115, #1116, #1117, #1119, #1120 (drafted in this same batch, unmerged as of this writing) |
| Desktop/mobile client teardown and Kubernetes-provider-specific termination mechanics | not yet owned by any corpus node |

**Expected but not verified when this node was written:**
- **The exact commit `docs/remote-agents.md` cites for buzz-acp's shutdown code
  (`28ae6cd21`) was not checked against this node's own recorded revision.** Line
  numbers in this node's own evidence ledger were read directly from
  `crates/buzz-acp/src/lib.rs` at commit `338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5` and
  differ from the line numbers `docs/remote-agents.md` cites for the same code at its
  own, earlier commit — this node's line citations are current as of its own
  provenance entry, not as of `docs/remote-agents.md`'s.
- **Whether any automated test exercises `buzz-relay`'s shutdown wiring end-to-end was
  not established as absent by this node's author independently** — `main.rs`'s own
  `TODO(coverage)` comment above the shutdown task states plainly that the wiring has
  no automated test today, and this node repeats that claim from the comment rather
  than re-deriving it. (`crates/buzz-relay/src/main.rs:1268-1294`)
- **Whether `buzz-acp`'s `shutdown_drain_is_paced_and_lossless` test (`lib.rs:6886`)
  covers the full multi-segment sequence narrated here, or only one segment of it, was
  not read in full** — the test's existence was found by name search, not by reading
  its body against this node's Sequence section step by step.
- **The relationship between this node's `type: layers` choice and issue #1043's own
  drafted reasoning could not be cross-checked**, because #1043's branch is not present
  on `origin/launchpad` and was not readable from this worktree; the *A note on `type`*
  section above is independently reasoned toward the same conclusion, not a
  verification of #1043's actual text.
