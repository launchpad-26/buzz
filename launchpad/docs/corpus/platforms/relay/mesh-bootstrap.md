---
id: platforms-relay-mesh-bootstrap
type: platforms
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - operator
evidence:
  - statement: "This node was authored and checked against repository revision 131b02f989684117d9ab1dd426f1673fa638e523."
    entry_class: FACT
    evidence:
      - "commit 131b02f989684117d9ab1dd426f1673fa638e523"
  - statement: "`mesh_boot.rs`'s crate-level (module-level) doc comment states that boot_mesh is the ONLY place the relay constructs mesh machinery, that it returns None and touches nothing when BUZZ_MESH=off, and that when enabled it (1) binds the iroh endpoint, (2) publishes an attested ReadyRecord and starts the readiness-gated heartbeat, (3) starts the MeshRuntime loops (accept, reconcile/dial, gossip) and runs one immediate reconcile pass, and (4) spawns a drain watcher that gossips draining=true and drains locally-owned huddle leases on shutdown."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/mesh_boot.rs:1-20"
  - statement: "boot_mesh's own body implements exactly that sequence: it returns Ok(None) immediately if config.mesh.enabled is false; otherwise it calls MeshEndpoint::bind on config.mesh.bind_addr (fatal on bind error), computes advertise addresses via advertise_addrs, builds a GossipRecord plus static capabilities(), constructs MeshMembership::new(...).with_expected_relay_pubkey(...) anchored to the relay's own signing key, builds a ReadyRegistry and ReadyRecord, calls registry.publish_ready(...) (fatal on error, with a comment explaining why: 'if Redis can't take the attested record, peers can never find us'), spawns spawn_registry_heartbeat, calls MeshRuntime::start(endpoint, membership, Some(registry)), constructs a HuddleOwnerRegistry, calls runtime.reconcile_now().await to dial seed peers immediately, spawns a drain-watcher task that polls the shutting_down flag and on shutdown calls runtime.membership().begin_drain() and owners.drain_all(), installs a MeshInboundDispatcher as the transport's single inbound slot via transport.set_inbound(...), and returns Ok(Some(MeshHandle { ... }))."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/mesh_boot.rs:411-521"
  - statement: "advertise_addrs resolves the address peers should dial in preference order: an explicit non-empty BUZZ_MESH_ADVERTISE_ADDR first, then POD_IP combined with the endpoint's actual bound port (Kubernetes Downward API, no RBAC needed) when both are available, then every IP transport address the endpoint itself reports."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/mesh_boot.rs:379-402"
  - statement: "MeshConfig has exactly three fields -- enabled (bool, BUZZ_MESH), bind_addr (SocketAddr, BUZZ_MESH_BIND_ADDR, default 0.0.0.0:3478), and registry_refresh (Duration, default 15s) -- documented as 'Mesh configuration, resolved from env by the relay.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-relay-mesh/src/lib.rs:52-63"
  - statement: "crates/buzz-relay/src/config.rs resolves BUZZ_MESH by requiring an explicit case-insensitive 'on', 'true', or '1' -- anything else, including an absent variable, resolves enabled=false -- and resolves BUZZ_MESH_BIND_ADDR by parsing it as a SocketAddr, defaulting to 0.0.0.0:3478 when absent, with a comment stating the intent is that 'an image upgrade with untouched env is a strict no-regression rollout.' The same file resolves a fourth env var, BUZZ_MESH_DEMO_ECHO, under the identical explicit-opt-in rule, feeding Config.mesh_demo_echo, a testbed-only reliable-stream echo flag documented as 'NOT a product flow.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/config.rs:680-705"
      - "crates/buzz-relay/src/config.rs:236-242"
  - statement: "crates/buzz-relay/src/main.rs calls buzz_relay::mesh_boot::boot_mesh(...) once, immediately after AppState::new, passing state.config, state.redis_pool, state.db, state.relay_keypair, and a clone of state.shutting_down; on Some(handle) it calls handle.wire_consumers(...) to register the per-profile inbound consumers before setting state.mesh (an Arc<OnceLock<MeshHandle>>) exactly once, with an unreachable!() guard if the OnceLock is already occupied."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:460-487"
  - statement: "AppState exposes the mesh handle only through a mesh() accessor returning Option<&MeshHandle> from the OnceLock, documented as 'None => mesh-off / single-instance: callers must no-op to today's behavior. Set once by main.rs after boot.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/state.rs:772"
      - "crates/buzz-relay/src/state.rs:958-962"
  - statement: "The relay's HTTP router registers GET /_mesh against mesh_status_handler, which returns state.mesh()'s live MeshStatus as JSON when the mesh is running, or the literal JSON object {\"enabled\": false} when state.mesh() is None."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs:299"
      - "crates/buzz-relay/src/router.rs:472-479"
  - statement: "MeshRuntime::start spawns three background loops over the bound endpoint -- accept_loop, reconcile_loop, gossip_tick_loop -- via tokio::spawn, and exposes reconcile_now() as an async method that runs one reconcile pass immediately (calling the same reconcile_once(&self.inner) the periodic loop uses) rather than waiting for the first interval tick; MeshRuntime::start delegates to start_with_intervals using DEFAULT_GOSSIP_INTERVAL and DEFAULT_RECONCILE_INTERVAL."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay-mesh/src/runtime.rs:82-152"
  - statement: "MeshInboundDispatcher has exactly three registration slots -- huddle_control, reliable_stream, datagrams -- each a std::sync::OnceLock so the first registration wins and a later call is logged and ignored ('mesh dispatcher: <lane> handler already registered — ignored'); traffic arriving on a slot before it is registered is logged and dropped rather than buffered or panicking."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/mesh_boot.rs:55-131"
  - statement: "wire_mesh_consumers wires the dispatcher's three lanes: RealtimeMedia datagrams to a MeshAudioRouter constructed with the MeshHandle's shared audio_fence (GenerationFloor), HuddleControl streams to HuddleControlAcceptor::accept_inbound spawned per-connection, and ReliableStream streams to ReliableStreamRouter::accept_inbound, after which the stream either runs run_demo_echo (only when BUZZ_MESH_DEMO_ECHO is on) or is accepted, logged, and closed with no product session consumer wired yet."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/mesh_boot.rs:200-299"
  - statement: "buzz-relay/Cargo.toml declares workspace dependencies on buzz-relay-mesh, buzz-db, nostr, and deadpool-redis, all four of which mesh_boot.rs's boot_mesh signature and body use directly (Config carries buzz_relay_mesh::MeshConfig; boot_mesh takes buzz_db::Db, &nostr::Keys, and deadpool_redis::Pool as parameters)."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/Cargo.toml:21"
      - "crates/buzz-relay/Cargo.toml:28"
      - "crates/buzz-relay/Cargo.toml:39"
      - "crates/buzz-relay/Cargo.toml:54"
  - statement: "buzz-relay-mesh's crate root doc comment states the relay consumes that crate exclusively through two seams -- RelayMeshMembership ('who is alive / draining / dialable?') and RelayPeerTransport ('move these bytes to that runtime') -- and that 'mesh membership is a hint; the Redis fenced generation is the arbiter,' naming the session directory's fenced generation, not mesh gossip, as the actual ownership authority for huddle/tunnel state."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay-mesh/src/lib.rs:1-19"
  - statement: "No corpus node on origin/launchpad at the recorded revision documents the mesh bootstrap sequence; a case-insensitive search of the corpus tree for 'mesh' returns only architecture/context, architecture/principles, architecture/deployment and architecture/containers nodes that mention mesh in passing (e.g. as a deployment topology or an extension point), none of which walks boot_mesh's own startup sequence, config resolution, or the /_mesh endpoint."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/containers/relay.md"
      - "launchpad/docs/corpus/architecture/deployment/multi-relay.md"
  - statement: "No platforms-specific corpus template is merged on origin/launchpad at the recorded revision (git ls-tree of launchpad/docs/corpus/templates lists no platforms.md), so this node borrows templates/component.md's section shape (Responsibility, Public interface, Dependencies, Boundary, Relationships, Scope and omissions) as an explicit convention, per Feature #614's sibling-node precedent, rather than inventing a new shape."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/templates/component.md"
    confidence: 0.7
  - statement: "This task's dispatching orchestrator recorded that sibling nodes in Feature #614 have settled on type: platforms for documents under platforms/** and that this convention should be followed for this task."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#614 batch-dispatch brief (Feature #614 sibling-node convention, as relayed in this task's dispatch instructions)"
---

# Relay mesh bootstrap (`boot_mesh`)

This node documents the relay's inter-relay mesh **bootstrap procedure** —
how a relay process decides whether to form a mesh at all, and if so, the
exact ordered sequence of steps `boot_mesh` runs to bind, register, and start
it. It answers: *when the relay starts, what actually happens to the mesh
subsystem, in what order, and what fails loudly versus silently no-ops?*

No platforms-specific corpus template (`platforms.md`) is merged at the
recorded revision, so this node borrows `templates/component.md`'s section
shape (Responsibility / Public interface / Dependencies / Boundary /
Relationships / Scope and omissions) rather than inventing a new one — the
convention this Feature's sibling `platforms/**` nodes have already settled
on. `type: platforms` is used because `node.schema.json`'s enum defines it as
one of PRD #602's named in-scope corpus surfaces, distinct from
`architecture` (container/context/decomposition diagrams) and
`implementation` (a single crate/module as a standalone artifact).

## Responsibility

`mesh_boot.rs`'s own module-level doc comment states its charter directly:
`boot_mesh` is *"the ONLY place the relay constructs mesh machinery. It
returns `None` — and touches nothing — when `BUZZ_MESH=off`, so mesh-off
deployments stay byte-identical to a relay built before this module
existed."* When enabled, the same comment enumerates four responsibilities:
bind the iroh endpoint, publish an attested ready-record and start the
readiness-gated heartbeat, start the `MeshRuntime` loops and run one
immediate reconcile pass, and spawn a drain watcher that gossips
`draining=true` and actively drains locally-owned huddle leases on shutdown.

## Boot sequence

`boot_mesh`'s body implements exactly the sequence above, in this concrete
order:

1. **Kill-switch check.** If `config.mesh.enabled` is `false`, log and return
   `Ok(None)` immediately — no bind, no Redis write, no spawned task.
2. **Endpoint bind.** `MeshEndpoint::bind(config.mesh.bind_addr)`. A bind
   failure is fatal (`anyhow::anyhow!` propagated) — an operator who set
   `BUZZ_MESH=on` gets the mesh or is told why not, per the function's own
   doc comment: *"a misconfigured enabled mesh fails loudly ... silently
   booting meshless would be the same class of bug as silently dropping to a
   default tenant."*
3. **Advertise-address resolution** (`advertise_addrs`), in preference order:
   an explicit non-empty `BUZZ_MESH_ADVERTISE_ADDR`; else `POD_IP` combined
   with the endpoint's actual bound port (Kubernetes Downward API, no RBAC
   needed); else every IP transport address the endpoint itself reports.
4. **Gossip record + capabilities.** A `GossipRecord` is built from the
   runtime id, resolved addresses, and `PROTO_VERSION`; `capabilities()`
   returns a static list (`reliable-stream`, `realtime-media`,
   `huddle-control`) since all three tunnel profiles ship in one binary.
5. **Membership, anchored.** `MeshMembership::new(local_record)
   .with_expected_relay_pubkey(relay_keypair.public_key().to_hex())` — the
   code comment attributes this anchor to review feedback: *"all pods share
   the relay signing key, so a seed attested by any other key is foreign and
   rejected (possession is not authorization)."*
6. **Ready-registry publish.** A `ReadyRegistry` and a signed `ReadyRecord`
   are built; `registry.publish_ready(&ready_record)` runs before anything
   else can rely on discoverability, and its failure is fatal — the code
   comment: *"if Redis can't take the attested record, peers can never find
   us — fail loudly now, not quietly forever."*
7. **Heartbeat spawn.** `spawn_registry_heartbeat` starts a background task
   that republishes while the relay would pass readiness and clears the
   record on ready→not-ready or shutdown.
8. **Runtime start + immediate reconcile.** `MeshRuntime::start(endpoint,
   membership, Some(registry))` spawns the accept/reconcile/gossip loops;
   `runtime.reconcile_now().await` then runs one reconcile pass immediately
   so seed peers are dialed at boot rather than waiting for the first
   interval tick.
9. **Drain watcher.** A spawned task polls the shared `shutting_down` flag
   every 500ms; on shutdown it calls `runtime.membership().begin_drain()`
   (gossips `draining=true`) and `owners.drain_all()` (actively drains
   locally-owned huddle leases) before returning.
10. **Dispatcher install.** A `MeshInboundDispatcher` is constructed and
    installed as the transport's single inbound slot
    (`transport.set_inbound(...)`) — this is the slot per-profile consumers
    register into afterwards via `MeshHandle::wire_consumers`.
11. **Return.** `Ok(Some(MeshHandle { directory, transport, membership,
    local_runtime_id, dispatcher, audio_fence, runtime, owners }))`.

**Caller-side completion, outside `boot_mesh` itself.** `main.rs` calls
`boot_mesh` once, immediately after `AppState::new`. On `Some(handle)`, it
calls `handle.wire_consumers(...)` — which registers the three inbound
dispatcher lanes (see *Public interface* below) **before** peers can route
traffic here — and then sets `state.mesh` (an
`Arc<std::sync::OnceLock<MeshHandle>>`) exactly once, with an `unreachable!()`
guard if that `OnceLock` is somehow already occupied.

## Configuration surface

| Env var | Resolved field | Default when absent | Resolution rule |
|---|---|---|---|
| `BUZZ_MESH` | `MeshConfig.enabled` | `false` (off) | Explicit case-insensitive `on`/`true`/`1` only; anything else, including absent, is off |
| `BUZZ_MESH_BIND_ADDR` | `MeshConfig.bind_addr` | `0.0.0.0:3478` | Parsed as `SocketAddr`; invalid value is a config error |
| `BUZZ_MESH_ADVERTISE_ADDR` | (consumed directly in `advertise_addrs`, not stored on `MeshConfig`) | none | First-preference override for the address peers dial |
| `BUZZ_MESH_DEMO_ECHO` | `Config.mesh_demo_echo` | `false` (off) | Same explicit-opt-in rule as `BUZZ_MESH`; testbed-only, *"NOT a product flow"* per its own doc comment |

`MeshConfig.registry_refresh` (heartbeat interval) is not env-configurable —
`config.rs` sets it to a fixed 15 seconds.

## Public interface

| Item | Kind | Contract | Evidence |
|---|---|---|---|
| `boot_mesh` | async fn | Boots the mesh or returns `Ok(None)` when off; fatal `Err` on bind/publish failure when on | `crates/buzz-relay/src/mesh_boot.rs:411-417` |
| `MeshHandle` | struct | Bundle a mesh consumer needs: `directory`, `transport`, `membership`, `local_runtime_id`, `dispatcher`, `audio_fence`, `owners`, plus a private `runtime` | `crates/buzz-relay/src/mesh_boot.rs:133-168` |
| `MeshHandle::status` | fn | Live `/_mesh` status snapshot via `runtime.membership().status()` | `crates/buzz-relay/src/mesh_boot.rs:171-174` |
| `MeshHandle::wire_consumers` | fn | Registers the three per-profile inbound consumers on the handle's dispatcher; called once from `main.rs` right after `boot_mesh` | `crates/buzz-relay/src/mesh_boot.rs:180-197` |
| `MeshInboundDispatcher` | struct | Fans inbound mesh traffic to the `huddle_control`/`reliable_stream`/`datagrams` slots; each slot is a `OnceLock` (first registration wins) | `crates/buzz-relay/src/mesh_boot.rs:55-89` |
| `AppState::mesh` | fn | `Option<&MeshHandle>` accessor over the `OnceLock` set once by `main.rs` | `crates/buzz-relay/src/state.rs:958-962` |
| `GET /_mesh` | HTTP route | Returns live `MeshStatus` JSON, or `{"enabled": false}` when `state.mesh()` is `None` | `crates/buzz-relay/src/router.rs:299`, `:472-479` |
| `MeshRuntime::start` | fn | Spawns accept/reconcile/gossip loops over a bound endpoint | `crates/buzz-relay-mesh/src/runtime.rs:88-100` |
| `MeshRuntime::reconcile_now` | async fn | Runs one reconcile pass immediately, without waiting for the periodic interval | `crates/buzz-relay-mesh/src/runtime.rs:148-152` |

## Dependencies

**Depends on** (this module requires these to build/run):

| Component | Why | Evidence |
|---|---|---|
| `buzz-relay-mesh` | Supplies `MeshConfig`, `MeshEndpoint`, `MeshMembership`, `MeshRuntime`, `ReadyRegistry`/`ReadyRecord`, `spawn_registry_heartbeat` — everything `boot_mesh` orchestrates | `crates/buzz-relay/Cargo.toml:28` |
| `buzz-db` | `boot_mesh` takes a `buzz_db::Db` parameter, threaded into `SessionDirectory::with_db` on the returned handle | `crates/buzz-relay/Cargo.toml:21` |
| `nostr` | `boot_mesh` takes `&nostr::Keys` (the relay signing key) to anchor `MeshMembership`'s expected-pubkey check and to sign the `ReadyRecord` | `crates/buzz-relay/Cargo.toml:39` |
| `deadpool-redis` | `boot_mesh` takes a `deadpool_redis::Pool`, used for the ready-registry publish/heartbeat and the session directory | `crates/buzz-relay/Cargo.toml:54` |

**Depended on by** (these require this module):

| Component | Why | Evidence |
|---|---|---|
| `crates/buzz-relay/src/main.rs` | Calls `boot_mesh` once at startup, then `wire_consumers`, then sets `AppState.mesh` | `crates/buzz-relay/src/main.rs:465-487` |
| `crates/buzz-relay/src/router.rs` (`GET /_mesh`) | Reads `state.mesh()` to report live mesh status to operators/probes | `crates/buzz-relay/src/router.rs:299`, `:472-479` |
| `crates/buzz-relay/src/audio/mesh.rs`, `crates/buzz-relay/src/audio/join.rs` | Huddle audio's cross-pod consumers register onto the `MeshInboundDispatcher` and read `MeshHandle.audio_fence`/`owners`, wired by `wire_mesh_consumers` | `crates/buzz-relay/src/mesh_boot.rs:200-299` |

No other crate in the workspace declares a dependency on `buzz-relay-mesh`
besides `buzz-relay` itself, so this bootstrap procedure is entirely
relay-internal.

## Boundary

This node does not describe:
- **The mesh transport crate's internals** — `buzz-relay-mesh`'s own wire
  protocol, phi-accrual gossip failure detection, iroh/QUIC transport
  mechanics, or scuttlebutt membership algorithm. Those are a distinct
  concept (the mesh transport itself, not its bootstrap) and belong in a
  future, separate node.
- **Huddle-audio session mechanics** — how `MeshAudioRouter`,
  `HuddleControlAcceptor`, or `HuddleOwnerRegistry` implement fenced
  ownership and rejoin; this node names them only as bootstrap-wired
  dependents. `architecture/flows/huddle-audio.md` is the closer neighbor for
  that subject, though it was not verified to already cover this specific
  boundary (see *Scope and omissions*).
- **Reliable-stream tunnel session semantics** (`ReliableStreamRouter`,
  `run_demo_echo`) beyond naming them as one of the three inbound lanes
  `wire_mesh_consumers` wires — the tunnel's own session protocol is a
  separate concern from mesh bootstrap.
- **Install/usage instructions** for running a relay with the mesh enabled —
  no crate-level README exists for `buzz-relay` or `buzz-relay-mesh` at the
  recorded revision to point to instead.

## Relationships

No relationships are declared. Checked, not assumed: a case-insensitive
search of the corpus tree on `origin/launchpad`
(`git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus`)
for "mesh" surfaces `architecture/containers/relay.md`,
`architecture/deployment/multi-relay.md`, `architecture/deployment/single-relay.md`,
`architecture/deployment/docker-compose.md`, `architecture/context/nostr-network.md`,
`architecture/context/external-services.md`, `architecture/context/relay-operator.md`,
`architecture/context/ai-agent.md`, `architecture/principles/relay-is-source-of-truth.md`,
`architecture/principles/subsystem-isolation.md`,
`architecture/principles/event-driven-extension.md`,
`architecture/principles/nostr-first.md`, `architecture/flows/huddle-audio.md`,
and `architecture/containers/desktop.md`. Each mentions mesh only as a
deployment-topology reference or an architectural principle example, at the
container/context/deployment/principle level of abstraction — none walks the
`boot_mesh` procedure itself, so none is a fit for `depends-on`, `references`,
or `part-of`. No sibling task in this Feature batch targets this node's
subject either. The first future node documenting the mesh transport crate's
own internals (see *Boundary*) is the natural moment to add a `references` or
`depends-on` edge from this node.

## Scope and omissions

**This node covers** the relay's mesh bootstrap procedure: the kill-switch
gate, the ordered sequence `boot_mesh` runs when the mesh is enabled, its
four env-configurable inputs, the public interface a consumer or operator
actually touches (`boot_mesh`, `MeshHandle`, the dispatcher, the `/_mesh`
route), and its real dependency edges in both directions.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| `buzz-relay-mesh`'s wire protocol, gossip algorithm, transport internals | A future node documenting the mesh transport crate itself (not yet written) |
| Huddle audio's fenced-ownership session logic | `architecture/flows/huddle-audio.md`, not independently re-verified against this node's boundary this session |
| Reliable-stream tunnel session protocol | Not yet documented in the corpus |
| Front-matter contract itself | `launchpad/docs/corpus/schema/node.schema.json` |
| Creating/updating/retiring a corpus node procedurally | `launchpad/docs/corpus/AGENTS.md` |

**Expected but not verified when this node was written:**

- **Live end-to-end mesh formation across multiple relay pods was not
  exercised.** This node is grounded entirely in a source-level read of the
  boot sequence and its unit tests (`mesh_off_boots_nothing`,
  `mesh_defaults_off_when_env_absent`, dispatcher routing tests) — it does
  not report on runtime behavior observed in a live multi-pod deployment.
- **Whether `architecture/flows/huddle-audio.md` already documents the exact
  boundary this node draws around huddle-audio consumers was not checked
  line-by-line.** The Boundary section above names it as the likely owner
  from a headline-level read, not a full comparison of the two documents'
  claims.
- **The mesh transport crate's own internals** (gossip, membership,
  phi-accrual, wire framing) were read only far enough to cite `MeshConfig`,
  `MeshRuntime::start`/`reconcile_now`, and the crate's own seam doc comment
  — not deeply enough to write a standalone node about them, which is why
  that remains explicitly out of scope here rather than folded in.
