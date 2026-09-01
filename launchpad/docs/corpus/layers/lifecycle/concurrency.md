---
id: layers-lifecycle-concurrency
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
  - statement: "buzz-relay's ConnectionState struct's own doc comment states its locking strategy explicitly, split by access pattern: auth_state uses RwLock because it is 'read-heavy after initial auth', subscriptions uses Mutex because it is 'write-heavy during REQ/CLOSE', and send_tx/ctrl_tx/cancel sit outside any lock entirely because they are 'Clone+Send, no coordination needed' — three different primitives chosen for three different access shapes on the same struct, not one lock protecting everything."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/connection.rs:56-87"
  - statement: "AppState carries four independent tokio::sync::Semaphore fields, each gating a different resource: conn_semaphore ('limiting total concurrent connections'), handler_semaphore ('limiting concurrent message handler tasks'), git_semaphore ('limiting concurrent git subprocess operations'), and media_upload_semaphore ('limiting concurrent media upload parsing/transcoding work')."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/state.rs:655-665"
  - statement: "A new WebSocket connection only proceeds past handle_active_connection's opening lines if state.conn_semaphore.clone().try_acquire_owned() succeeds; on failure (semaphore exhausted) the function logs 'Connection limit reached, rejecting {addr}' and returns immediately, rejecting the connection before any per-connection state is allocated."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/connection.rs:159-165"
  - statement: "The acquired conn_semaphore permit is held for the entire lifetime of handle_active_connection and only dropped as the function's very last statement, after deregistration and metrics are updated — so the permit's lifetime, not any explicit release call, is what bounds concurrent connections to the semaphore's configured capacity."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/connection.rs:318"
  - statement: "Once a connection is admitted, handle_active_connection spawns three concurrent tokio tasks around one shared Arc<ConnectionState>: send_task (running send_loop, driven by a data mpsc::Receiver, a control mpsc::Receiver, and a restart-close mpsc::Receiver), heartbeat_task (running heartbeat_loop on a 30-second tokio::time::interval), and auth_timeout_task (a bare tokio::spawn wrapping a tokio::select! between a 5-second sleep and the shared CancellationToken) — while the calling task itself drives a fourth loop, recv_loop, inline via .await rather than as a fifth spawned task."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/connection.rs:231-281"
  - statement: "After recv_loop returns, handle_active_connection calls cancel.cancel() once and then awaits all three spawned tasks' JoinHandles in sequence (send_task, heartbeat_task, auth_timeout_task), discarding each JoinHandle's Result with `let _ =` — so a panic inside any of the three spawned tasks is not propagated or observed by the caller, only silently swallowed by the discard."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/connection.rs:283-286"
  - statement: "send_loop_inner's main loop is a biased tokio::select! (the `biased;` keyword disables tokio's default random polling order and instead always checks branches top-to-bottom), giving a restart-close request priority over cancellation, which itself is checked before an ordinary control frame, which itself is checked before a data frame — a code comment states this exists because 'a restart command owns shutdown delivery and must flush its 1012 before cancellation can fall back to an unacknowledged close.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/connection.rs:346-397"
  - statement: "The data-frame branch of send_loop_inner's select batches: after the first message is fed to the sink, it drains up to MAX_WS_SEND_BATCH (64) additional already-queued messages via non-blocking try_recv() before issuing a single ws_send.flush().await, recording the actual batch size to a buzz_ws_send_batch_size histogram — trading one extra loop iteration per batch for fewer syscalls under load, rather than flushing after every individual message."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/connection.rs:403-426"
  - statement: "Inside handle_text_message, each of the three request-shaped client message kinds (Event, Req, Count) independently acquires its own permit from the same shared state.handler_semaphore before tokio::spawn-ing its handler; Auth and Close are instead run inline on the caller's own task (no semaphore acquisition, no spawn) — so only requests whose handling work is spawned onto a new task are gated by this particular semaphore, and a message kind never contends with itself across connections beyond the one shared capacity."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/connection.rs:560-641"
  - statement: "Each handler_semaphore-gated spawn wraps its handler call and the owned permit's drop in the same async block, and is instrumented with a per-request tracing::info_span!, captured before the tokio::spawn call — the surrounding code comment states plainly that 'a bare tokio::spawn drops tracing context', so the span capture is deliberate, not incidental."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/connection.rs:568-594"
  - statement: "ConnectionManager, the process-wide registry every live connection is entered into, stores its per-connection ConnEntry values in a DashMap<Uuid, ConnEntry> rather than a Mutex<HashMap<Uuid, ConnEntry>> or an RwLock-guarded map — DashMap internally shards its storage across independent locks, so two unrelated connections registering, looking up, or being removed concurrently do not contend on one process-wide lock the way a single Mutex<HashMap> would force them to."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/state.rs:236-252"
  - statement: "ConnectionManager additionally carries a `draining: AtomicBool` sticky flag alongside its DashMap, whose own doc comment states it exists so that 'registrations that land after the drain snapshot self-signal, so no upgrade-vs-shutdown interleaving can produce a connection that misses the restart close' — an atomic flag checked at registration time, not a lock held across the whole drain operation."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/state.rs:239-243"
  - statement: "A separate, narrower-purpose concurrent map exists one layer down: each ConnEntry's own authenticated_pubkey field is an Arc<std::sync::RwLock<Option<Vec<u8>>>> — a synchronous (non-async) std::sync::RwLock, not tokio::sync::RwLock, because the value it guards is read and written synchronously with no .await inside the critical section."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/state.rs:109"
  - statement: "The audit worker is one of several long-lived background tasks fed by a bounded mpsc::channel of capacity 1000 (audit_tx/audit_rx), constructed once in AppState's own initialization and spawned via tokio::spawn as a loop that awaits tokio::select! against its own cancellation token and the channel's recv() — a bounded producer-consumer channel is the coordination primitive here, not a shared mutable buffer guarded by a lock."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/state.rs:796-800"
  - statement: "A representative unit test, send_loop_batches_queued_data_frames_into_one_flush, directly exercises the data-frame batching behavior described above: it queues five messages onto a bounded mpsc channel ahead of calling send_loop_inner, then asserts the mock sink recorded exactly one flush_count and all five payloads in order — a concrete, currently-passing test of the batching claim, not merely a code comment describing intended behavior."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/connection.rs:850-879"
  - statement: "This node was authored against templates/concept.md (the closed corpus template whose Required Sections are Definition, an optional visual aid, optional Background, Use cases, optional Comparison, and optional Related resources/relationships), not templates/flow.md, because issue #1117's own Definition-of-done checklist asks for a one-sentence definition, stated boundaries/non-goals, links to related concepts/implementation/verification, and examples used only to clarify — the same four asks concept.md's own Required-sections list states, and not flow.md's trigger/preconditions/sequence/outcome shape that sibling tasks #1118 and #1120 used for their own DoD checklists."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/templates/concept.md"
      - "launchpad/docs/corpus/templates/flow.md"
    confidence: 0.8
  - statement: "node.schema.json's type enum includes layers as one of thirteen closed values, described only as 'the corpus surface this node documents,' with no further per-value elaboration in either node.schema.json or schema/README.md's own prose table for the type field."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "This node uses type: layers rather than a documentation-form-shaped alternative because Feature #611 (this node's parent) organizes its whole task set — including this task — under a layers/lifecycle/ directory naming convention, and layers is schema.json's own dedicated enum member for that surface; sibling tasks #1118 (graceful-shutdown) and #1120 (startup) already independently reasoned to the identical conclusion for the same parent Feature, and this node's own choice follows the same, re-derived reasoning rather than copying their prose (their branches are not merged to origin/launchpad and were not read verbatim for this entry)."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
    confidence: 0.75
  - statement: "architecture-containers-relay is present as a node id on origin/launchpad at the time this node was authored, confirmed via git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus and reading its own id front-matter field, making it a valid relationships target for the container (buzz-relay) this concept's evidence is drawn from."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/containers/relay.md:1-2"
  - statement: "No layers/lifecycle/* sibling node (background-workers #1115, cancellation #1116, graceful-shutdown #1118, resource-cleanup #1119, startup #1120) is present on origin/launchpad at the time this node was authored, confirmed by a pinned absence citation against that commit, so none of them is a valid relationships target yet even though each is named as a prose boundary callout below."
    entry_class: FACT
    evidence:
      - "absent:launchpad/docs/corpus/layers@338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
  - statement: "Issue #1117's Definition of Done requires the document to define the term in one sentence before deeper explanation, state boundaries/non-goals or what the concept must not be confused with, link the concept to related concepts/implementation/verification, and use examples only to clarify the concept rather than introducing a second canonical concept."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1117 definition of done"
relationships:
  - type: references
    target: architecture-containers-relay
---

# Concurrency

## A note on `type`

`node.schema.json`'s `type` enum lists thirteen closed values, and `layers` is one of them,
described (both in the schema and in `schema/README.md`'s prose table) only as naming "the
corpus surface a node documents." This node uses `type: layers` because its parent, Feature
`#611`, organizes its entire task set under a `layers/lifecycle/` directory taxonomy — a
cross-cutting technical-behavior grouping (lifecycle, concurrency, cancellation, background
work, resource cleanup, startup) distinct from the structural C4 `architecture/` family this
corpus already houses. Sibling tasks `#1118` (graceful-shutdown) and `#1120` (startup) already
reasoned to the same conclusion for the same parent Feature; this node's own evidence ledger
restates that reasoning independently rather than quoting their text verbatim, since neither
sibling's branch is merged to `origin/launchpad` at this node's recorded revision.

## Definition

**Concurrency**, in `buzz-relay`, is the practice of running many independent units of work —
one WebSocket connection's read/write/heartbeat loops, one client message's handler, one
background worker — as separate `tokio` tasks inside a single OS process, all sharing access to
common state (an `Arc<AppState>`, a connection registry, a database pool) through primitives
chosen for *how* that access happens rather than one lock protecting everything uniformly.
`buzz-relay`'s own `ConnectionState` doc comment states this discipline explicitly: `RwLock`
for state that is "read-heavy after initial auth," `Mutex` for state that is "write-heavy during
REQ/CLOSE," and no lock at all for values that are merely `Clone + Send` and need no
coordination (`crates/buzz-relay/src/connection.rs:56-59`). Concurrency here is not a single
mechanism — it is this repeated choice, made independently at each point shared state exists,
among locks (`Mutex`, `RwLock`), sharded concurrent maps (`DashMap`), bounded channels
(`mpsc`, `watch`), and admission-control counters (`Semaphore`).

**What this is not.** Concurrency is not parallelism guaranteed by extra CPU cores — `tokio`'s
multi-threaded runtime may or may not run two tasks on two cores simultaneously, and this node
makes no claim either way; it is not the same idea as *cancellation* (issue `#1116`'s subject:
how a task is asked to stop and unwinds), and it is not the same idea as *graceful shutdown*
(issue `#1118`'s subject: the process-wide sequence that stops admitting work and drains what
is in flight). Concurrency is the standing, steady-state shape of many tasks and shared state
coexisting; cancellation and shutdown are both *events* that act on that shape, not the shape
itself. See *Boundary* below for exactly where each sibling concept's territory begins.

## Diagram

```mermaid
flowchart TB
    subgraph AppState["Arc&lt;AppState&gt; (shared)"]
        CS["conn_semaphore"]
        HS["handler_semaphore"]
        CM["ConnectionManager<br/>DashMap&lt;Uuid, ConnEntry&gt;"]
    end

    NewConn["New WebSocket"] -->|try_acquire_owned| CS
    CS -->|permit granted| Handle["handle_active_connection<br/>(one Arc&lt;ConnectionState&gt;)"]

    Handle -->|tokio::spawn| Send["send_loop<br/>biased select!:<br/>restart &gt; cancel &gt; ctrl &gt; data"]
    Handle -->|tokio::spawn| Heartbeat["heartbeat_loop<br/>30s interval"]
    Handle -->|tokio::spawn| AuthTO["auth_timeout_task<br/>5s sleep"]
    Handle -->|.await inline| Recv["recv_loop<br/>(driving task)"]

    Recv -->|handle_text_message| Msg{Event / Req / Count?}
    Msg -->|try_acquire_owned| HS
    HS -->|permit granted| Spawned["tokio::spawn(handler + drop(permit))"]

    Handle -.->|register/deregister| CM
```

## Use cases

An agent or developer needs this concept before touching `crates/buzz-relay/src/connection.rs`
or `state.rs` for several concrete reasons:

- **Adding a new per-connection field.** Without knowing the read-heavy/write-heavy/no-lock
  discipline already in use (`connection.rs:56-59`), a new field is likely to default to the
  wrong primitive — for example, wrapping something read on every message in a `Mutex` when an
  `RwLock` (or no lock at all, if it is `Clone + Send`) already fits the codebase's own pattern.
- **Adding a new bounded resource.** `AppState`'s four semaphores (`conn_semaphore`,
  `handler_semaphore`, `git_semaphore`, `media_upload_semaphore`, `state.rs:655-665`) are the
  established shape for "cap how many X can run concurrently" — a new bounded resource should be
  recognized as fitting this same shape rather than reinvented as a counter guarded by a `Mutex`.
- **Debugging connection-registry contention.** `ConnectionManager`'s choice of `DashMap` over a
  single `Mutex<HashMap>` (`state.rs:236-252`) is specifically about avoiding one process-wide
  lock across every connection's register/lookup/remove — a developer investigating a
  contention or throughput issue in the registry needs to know this is deliberate, not an
  oversight to "fix" by wrapping it in a coarser lock.
- **Reasoning about message ordering and priority.** The biased `tokio::select!` in
  `send_loop_inner` (`connection.rs:346-397`) encodes a specific priority order (restart close >
  cancellation > control frames > data frames) as *code structure*, not configuration — anyone
  reordering or adding a branch to that `select!` needs to understand why the existing order
  exists before changing it.

## Comparison

| Primitive | Used for | Representative site |
|---|---|---|
| `tokio::sync::Semaphore` | Bounding how many concurrent units of one kind of work are in flight (connections, spawned message handlers, git subprocess ops, media transcoding) | `state.rs:655-665`; acquired at `connection.rs:159`, `571`, `599`, `621` |
| `tokio::sync::RwLock` | Per-connection state that is read far more often than written (`auth_state`) | `connection.rs:70`, doc comment at `56-59` |
| `tokio::sync::Mutex` | Per-connection state that is written frequently relative to reads (`subscriptions`) | `connection.rs:32`, `180` |
| `std::sync::RwLock` (synchronous, not `tokio::sync`) | A value read/written with no `.await` inside the critical section (`ConnEntry::authenticated_pubkey`) | `state.rs:109` |
| `DashMap` | A concurrently-accessed map where many independent keys are registered/looked up/removed without one global lock (`ConnectionManager`'s connection registry) | `state.rs:236-252` |
| `mpsc::channel` (bounded) | Point-to-point delivery from many producers into one consuming loop, with backpressure from the bound itself (per-connection send/control channels; the audit worker's input queue) | `connection.rs:169-177`; `state.rs:796-800` |
| `watch::channel` | Broadcasting the latest value of something to every current and future subscriber (per-connection disconnect reason) | `state.rs:69`, `77-78` |
| No lock at all | Values that are `Clone + Send` and need no coordination (`send_tx`, `ctrl_tx`, `cancel`) | `connection.rs:59`, doc comment |

Each row exists because the corresponding access pattern is genuinely different — this table is
not an exhaustive catalogue of every concurrency primitive `tokio` or the wider Rust ecosystem
offers, only the ones this node found actually in use in the code it cites.

## Boundary

This node does not describe:
- **Cancellation** — how a task observes a `CancellationToken` firing and unwinds cleanly. Every
  code excerpt above that mentions `cancel`/`CancellationToken` is cited only to show where
  concurrent tasks coordinate, not to explain cancellation's own semantics; that is issue
  `#1116`'s subject.
- **Graceful shutdown** — the process-wide sequence (SIGTERM → grace period → drain → hard
  timeout) that stops admitting new work and drains what is already running. This node's
  per-connection task fan-out and its semaphores are *acted upon* by that sequence, but the
  sequence itself is issue `#1118`'s subject, already documented in that sibling's own
  `layers/lifecycle/graceful-shutdown.md` node (not linked here as a `relationships` edge, since
  that node is not yet present on `origin/launchpad` at this node's recorded revision).
- **Background-worker startup ordering** — which of `buzz-relay`'s roughly dozen `tokio::spawn`
  calls made before the listener opens must run before which other, and why. This node cites
  `tokio::spawn` only as a mechanism (a task starts running concurrently with its caller); the
  specific inventory and ordering of startup-time background tasks is issue `#1115`'s subject.
- **`buzz-acp`'s own concurrency shape.** The agent harness has its own concurrent structures
  (`AgentPool`, `JoinSet`-driven task draining) that this node's evidence ledger does not survey
  — see *Scope and omissions* below.
- **What a capability lets a user or agent do**, or the general durable contract of the
  WebSocket protocol surface — this node narrates only the concurrency *mechanism*, not the
  product-level behavior built on top of it.

**The tell, either way:** a claim about *how many tasks exist and how they share state* belongs
here; a claim about *what happens when one is asked to stop*, *what happens when the whole
process is asked to stop*, or *what work gets started at boot* belongs to one of the three
siblings named above.

## Relationships

- `references`: `architecture-containers-relay` — the container this concept's evidence (every
  cited excerpt is from `crates/buzz-relay/`) is drawn from; supporting context, no ownership or
  currency dependency implied.

No `layers/lifecycle/*` sibling node (`#1115`, `#1116`, `#1118`, `#1119`, `#1120`) is linked here:
none is present on `origin/launchpad` at this node's recorded revision (confirmed with
`git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus`), so none is a valid
`relationships` target per `AGENTS.md` step 9's rule that a target must exist on the branch being
merged into. Each is instead named as a prose boundary callout above.

## Scope and omissions

**This node covers** `buzz-relay`'s per-connection concurrency model as a single, deeply-cited
worked example: connection admission via `Semaphore`, the four-task fan-out per connection
(`send_loop`, `heartbeat_loop`, `auth_timeout_task`, and the driving `recv_loop`), per-message
handler concurrency gated by a second `Semaphore`, the `DashMap`-based connection registry, and
the access-pattern-driven choice among `RwLock`/`Mutex`/no-lock/channels documented in
`ConnectionState`'s own doc comment.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Cancellation semantics (`CancellationToken`, how a task unwinds on cancel) | `#1116` |
| The graceful-shutdown sequence (SIGTERM, grace period, drain, hard timeout) | `#1118` (`layers/lifecycle/graceful-shutdown.md`, not yet merged) |
| Background-worker inventory and startup ordering | `#1115` |
| `buzz-acp`'s own concurrency shape (`AgentPool`, `JoinSet`-based draining) | Not surveyed by this node; not yet a corpus node |
| The standing container structure of `buzz-relay` itself | `architecture-containers-relay` |
| The general WebSocket protocol contract (as opposed to the concurrency mechanism serving it) | `architecture/flows/websocket-connection.md` (not linked here — not re-verified at this node's recorded revision) |

**Expected but not verified when this node was written:**

- **Whether every concurrency primitive in `buzz-relay` was surveyed, versus only the
  `connection.rs`/`state.rs` sample this node cites, was not established.** Other files in
  `crates/buzz-relay/src/` (for example `mesh_boot.rs`, referenced only in passing by sibling
  `#1118`'s own evidence) may contain further primitives this node does not cite.
- **Whether `tokio`'s runtime actually schedules any two of the tasks this node names onto
  separate OS threads at any given moment was not measured** — this node describes the code's
  concurrency structure (independent tasks, shared state, chosen coordination primitives), not
  a runtime trace of actual parallel execution.
- **The relative performance of `DashMap`'s sharded-lock design versus a single `Mutex<HashMap>`
  for `ConnectionManager`'s actual production connection counts was not benchmarked by this
  node's author** — the code comment's own stated rationale (avoiding one global lock) is cited
  as the design intent, not as a measured performance claim.
