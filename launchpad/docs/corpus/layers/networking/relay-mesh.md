---
id: layers-networking-relay-mesh
type: layers
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - operator
evidence:
  - statement: "This node was authored and checked against repository revision 29ca9b189bd3f639ba09c972b57c70538c0860c6."
    entry_class: FACT
    evidence:
      - "commit 29ca9b189bd3f639ba09c972b57c70538c0860c6"
  - statement: "The crate's own module documentation names the subject 'the inter-relay QUIC mesh': one iroh endpoint per relay runtime, a warm full mesh of authenticated connections, scuttlebutt membership gossip on a control substream, and a fenced wire contract carrying tunnel traffic between pods, consumed by the relay through exactly two seams -- RelayMeshMembership ('who is alive / draining / dialable?') and RelayPeerTransport ('move these bytes to that runtime')."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay-mesh/src/lib.rs"
  - statement: "The mesh is opt-in and default-off: BUZZ_MESH enables it when the value is 'on' (compared case-insensitively) or exactly 'true' or '1' (both compared with ==, so 'TRUE' and 'True' do NOT enable it), and resolves to disabled for an absent variable, 'off', or any other value, with an inline comment stating the reason as strict rollout no-regression -- 'an image upgrade with untouched env must not bind a new UDP port or write a new Redis key' -- and BUZZ_MESH_BIND_ADDR defaults to 0.0.0.0:3478."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/config.rs"
  - statement: "MeshConfig's own field documentation records the bind address as a UDP bind for the iroh endpoint and states that it is 'Excluded from istio sidecar capture in k8s', which is the only stated relationship between this mesh and a cluster service mesh."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay-mesh/src/lib.rs"
  - statement: "boot_mesh is documented as the ONLY place the relay constructs mesh machinery, returning None and touching nothing when the seam is off, and consumers reach the mesh exclusively through MeshHandle via AppState::mesh(), where None means 'behave exactly like a single-instance relay'."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/mesh_boot.rs"
      - "crates/buzz-relay/src/state.rs"
  - statement: "The mesh runs on its own transport, separate from the relay's client-facing surface: a versioned ALPN (b\"buzz/mesh/1\"), a one-byte WIRE_VERSION prefix on every frame, QUIC datagrams for realtime media with the datagram boundary as the frame boundary, and length-delimited postcard bi-streams for reliable-stream and gossip-control traffic whose first frame MUST be Hello."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay-mesh/src/wire.rs"
  - statement: "A mesh runtime's identity is the ed25519 public key of a keypair generated fresh at process start, deliberately not the deployment's secp256k1 Nostr relay key, because the Helm chart shares one BUZZ_RELAY_PRIVATE_KEY Secret across all pods of a release and reusing it would give every pod the same runtime id and collapse the ownership plane."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay-mesh/src/wire.rs"
  - statement: "The mesh is closed to anything that is not an attested peer runtime: MeshPeer::from_connection returns a transport error outright when the negotiated ALPN is not the mesh ALPN, and the runtime's accept loop admits an inbound connection only when the remote runtime id is present in the attested membership table, granting unknown ids one registry rescan before rejection and logging 'rejected inbound connection from unattested runtime id'."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay-mesh/src/peer.rs"
      - "crates/buzz-relay-mesh/src/runtime.rs"
  - statement: "Two kinds of relay-side traffic ride the mesh: cross-pod huddle audio, where non-owner pods register their local clients as remote peers in the owner pod's room over a reliable HuddleControl stream and forward those clients' Opus frames to the owner as datagrams; and reliable-stream tunnel sessions, where a join landing on a non-owner runtime opens a fenced mesh bi-stream to the owner instead of serving locally."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/audio/mesh.rs"
      - "crates/buzz-relay/src/tunnel/reliable.rs"
      - "crates/buzz-relay/src/tunnel/mod.rs"
  - statement: "Cross-pod connection control does not ride the mesh: disconnect_pubkey_clusterwide and disconnect_community_clusterwide both close this pod's sockets locally and then fan the same command out to every other pod as a ConnControl message published to a community-scoped Redis channel matching buzz:*:conn-control."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/state.rs"
      - "crates/buzz-pubsub/src/conn_control.rs"
  - statement: "Cross-pod Nostr event fan-out likewise does not ride the mesh: buzz-pubsub declares itself as 'Redis pub/sub fan-out, presence tracking, and typing indicators', and its architecture note describes a dedicated Redis pub/sub connection subscribing to community- and channel-scoped keys and forwarding to N WebSocket receivers through an in-process broadcast channel, with cross-pod cache invalidation and connection control as sibling modules in the same crate."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/lib.rs"
  - statement: "The other two cross-pod planes are already documented by merged corpus nodes: architecture-deployment-multi-relay records that relay replicas share Postgres (event store, repo-name uniqueness), Redis (pub/sub fan-out across replicas, and the mesh's fenced lease store) and S3-compatible object storage (git object/ref state, media), that a relay pod holds no durable state of its own, and that a chart-side guard refuses to install a multi-replica release with no Redis source configured -- so Redis is a hard dependency beyond one replica, not a soft one."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/deployment/multi-relay.md"
  - statement: "The mesh moves bytes but never decides ownership: every session-bearing frame carries the fenced tuple {session_id, generation, owner_runtime_id}, receivers MUST reject a stale generation at every hop, and the crate states the rule as 'mesh membership is a hint; the fenced generation (Redis CAS lease) is the arbiter. The mesh may say \"don't dial\" -- it may never say \"take over.\"' The Redis-backed session directory that holds the lease lives relay-side, not in the mesh crate."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay-mesh/src/lib.rs"
      - "crates/buzz-relay-mesh/src/wire.rs"
      - "crates/buzz-relay/src/tunnel/directory.rs"
  - statement: "Without the mesh, horizontal scaling costs a client-visible capability: huddle_audio_available defaults to true so a single-pod deployment is unchanged, its field documentation states that under horizontal scaling 'two peers in the same huddle can land on different pods and never hear each other' and that operators running multiple relay pods MUST set BUZZ_HUDDLE_AUDIO_AVAILABLE=false, and the audio join handler then rejects the join with a huddle_audio_unavailable error frame."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/config.rs"
      - "crates/buzz-relay/src/audio/handler.rs"
  - statement: "The same join handler carries both paths in one place: when the mesh is live the pod either owns the huddle room locally or forwards the client to the owner over a HuddleControl stream, and the huddle_audio_available rejection applies only on the mesh-off branch, described in-code as 'the single-pod guardrail'."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/audio/handler.rs"
  - statement: "GET /_mesh -- live peer table, connection and phi state, per-peer counters and fence-rejection totals -- is registered on build_health_router, the health-only router documented as serving Kubernetes probes on a separate port and carrying no metrics middleware, auth, CORS or body limit, alongside /_liveness, /_readiness and /_status; it reports {\"enabled\": false} when the mesh is off specifically so an operator can distinguish 'off' from 'on with zero peers'. The separate POST /_mesh/demo/echo route is on the main application router and is testbed-only."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs"
      - "crates/buzz-relay/src/main.rs"
  - statement: "No frame in the mesh wire contract carries a community or tenant identifier, and the string 'community' does not appear anywhere in the mesh crate's source; community scoping enters only relay-side, where the fenced session directory takes a buzz_core::CommunityId when composing its Redis lease keys."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay-mesh/src/wire.rs"
      - "crates/buzz-relay/src/tunnel/directory.rs"
      - "grep(pattern='CommunityId|community', path='crates/buzz-relay-mesh/src/') -> 0 matches"
  - statement: "The relay mesh is horizontal scaling of one relay deployment rather than federation between independently operated relays or communities: peers are admitted only against an attestation signed by the one relay signing key a release's pods share, they bootstrap through one shared Redis ready registry, and the wire carries no community identity that a second deployment's traffic could be scoped by."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay-mesh/src/wire.rs"
      - "crates/buzz-relay-mesh/src/runtime.rs"
      - "crates/buzz-relay/src/mesh_boot.rs"
    confidence: 0.9
  - statement: "The repository has no integration or end-to-end test that exercises the relay mesh: crates/buzz-test-client/tests/ contains nineteen test files, of which the only one naming 'mesh' is e2e_mesh_llm.rs, whose own module doc scopes it to 'End-to-end acceptance tests for Buzz shared compute' -- the unrelated MeshLLM subsystem, not this one."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/e2e_mesh_llm.rs"
      - "ls(crates/buzz-test-client/tests/) -> 19 files; only e2e_mesh_llm.rs matches 'mesh'"
  - statement: "Issue #1129's definition of done requires that the document define the term in one sentence before deeper explanation, state boundaries and non-goals or what the concept must not be confused with, link the concept to related implementation and verification nodes without duplicating their canonical content, and use examples only to clarify rather than to introduce a second canonical concept."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1129 definition of done"
relationships:
  - type: references
    target: implementation-crates-buzz-relay-mesh
  - type: references
    target: architecture-deployment-multi-relay
  - type: references
    target: layers-compute-mesh-compute
  - type: references
    target: architecture-flows-huddle-audio
  - type: references
    target: layers-data-redis-channel-pubsub
---

# Relay mesh

**The relay mesh is a direct, authenticated QUIC network between the processes of
one horizontally-scaled relay deployment, so that a live session held on one pod
can be reached by a client connected to another.** It is the relay's second
east-west plane: opt-in, invisible to clients, and carrying only session-bearing
traffic that the always-on Redis-mediated plane structurally cannot.

**Disambiguation — "mesh" names two unrelated things in this repository.** This
node is about `crates/buzz-relay-mesh`, the server-side mesh between relay pods.
It is **not** about mesh compute, the desktop app's MeshLLM-based shared-LLM
inference feature, which shares no code, no trust model and no transport with
this subject (`layers-compute-mesh-compute`). It is also not the Istio service
mesh a cluster may separately be running; the relay's own UDP port is documented
in-crate as something to exclude from that mesh's sidecar capture, which is the
only relationship between the two.

## What "one logical relay" means here

A relay deployment may be served by many interchangeable pods, none of which
holds durable state of its own. Making N processes behave as one relay is not a
single mechanism — it is three planes with different jobs, and the mesh is only
the third. The first two rows below are the neighbouring nodes' subject, restated
here only far enough to place the third:

| Plane | What it carries | Always on? |
|---|---|---|
| Shared durable stores (Postgres, object storage) | Events, repo-name uniqueness, git object/ref state | Yes |
| Redis pub/sub | Cross-pod Nostr event fan-out, presence and typing, cache invalidation, and connection-control commands — `disconnect_pubkey_clusterwide` and `disconnect_community_clusterwide` both publish to a community-scoped `buzz:*:conn-control` channel | Yes, and hard-required beyond one replica |
| **Relay mesh (this node)** | Live, owner-bound session traffic: cross-pod huddle audio and reliable-stream tunnel sessions | **No — opt-in via `BUZZ_MESH`** |

The distinction that defines the mesh is *ownership*. Redis pub/sub broadcasts a
message to whoever happens to be listening and is content to be lossy about it;
a durable row in Postgres is the backstop. A huddle's audio and a tunnel's byte
stream cannot work that way — they belong to one pod at one moment, and a client
that landed elsewhere needs a pipe to *that* pod, not a broadcast to all of them.
The mesh is that pipe.

```mermaid
flowchart TB
    ClientA["client A<br/>(WebSocket)"] --> PodA["relay pod A"]
    ClientB["client B<br/>(WebSocket)"] --> PodB["relay pod B<br/><i>owns the session</i>"]
    PodA <-->|"mesh: QUIC, ALPN buzz/mesh/1<br/>datagrams + reliable streams"| PodB
    PodA -.->|"pub/sub + fenced lease"| Redis[("Redis")]
    PodB -.->|"pub/sub + fenced lease"| Redis
    PodA -.-> PG[("Postgres / object store")]
    PodB -.-> PG
```

## How the plane is shaped

**One endpoint per process, on its own port.** Each relay process binds a single
iroh QUIC endpoint (default `0.0.0.0:3478`, UDP) — a distinct transport and a
distinct port from the relay's TCP HTTP/WebSocket listeners. Every frame is
postcard-encoded behind a one-byte protocol version, under a versioned ALPN
(`buzz/mesh/1`) so an old and a new pod never half-speak the protocol during a
rolling deploy.

**Two shapes of traffic.** Realtime media rides QUIC datagrams, one frame per
datagram, lossy by design — a receiver tolerates gaps and reordering and never
waits. Everything state-bearing rides length-delimited bi-streams, whose first
frame must be a `Hello`. Membership gossip is itself one such stream, exactly one
per peer connection.

**Warm, not on-demand.** A reconcile loop periodically dials every known,
non-draining peer the process is not yet connected to. The connections are
already up before they are needed, which is what makes failover "the next frame
goes elsewhere" rather than "wait for a handshake."

**Closed by default, at two gates.** A connection whose negotiated ALPN is not
the mesh ALPN is rejected outright, and an inbound connection is admitted only if
the remote runtime id already appears in the attested membership table — an
unknown id gets one registry rescan and is then refused and logged. A mesh
runtime's identity is a fresh ed25519 keypair generated at process start, not the
secp256k1 relay signing key that every pod of a release shares; reusing the shared
key would give every pod the same identity and collapse the ownership plane
entirely.

**Membership is a hint; Redis is the arbiter.** Every session-bearing frame
carries `{session_id, generation, owner_runtime_id}`, and a receiver must reject a
stale generation at every hop, not only at the directory. The crate states the
rule as its own law: the mesh may say "don't dial" — it may never say "take over."
The lease that actually decides ownership lives relay-side, in the fenced session
directory, not in the mesh at all.

## Why this matters

**It is the difference between scaling out and losing a feature.** Before the
mesh, running more than one relay pod meant two participants in the same huddle
could land on different pods and never hear each other. The relay's answer was to
refuse rather than to split silently: `huddle_audio_available` defaults true so a
single-pod deployment is unaffected, a horizontally-scaled deployment sets
`BUZZ_HUDDLE_AUDIO_AVAILABLE=false`, and the join handler then returns a
`huddle_audio_unavailable` error the client can act on. With the mesh live, the
same handler takes the other branch: own the room locally, or forward this client
to the pod that does.

**It is opt-in, and that is deliberate.** `BUZZ_MESH` must be set explicitly to `on`
(case-insensitive) or to exactly `true` or `1`; an absent variable, `off`, or a typo all
resolve to disabled, so an image upgrade with untouched environment binds no new UDP port
and writes no new Redis key. Note the asymmetry, which matters to an operator choosing a
value: only `on` is compared case-insensitively, so **`BUZZ_MESH=TRUE` leaves the mesh
disabled** while `BUZZ_MESH=ON` enables it. `boot_mesh` is the single construction site, and its `None` return
means the relay behaves exactly as it did before the mesh existed.

**It is diagnosable from outside the process.** `GET /_mesh` returns the live peer
table, connection and suspicion state, per-peer counters and fence-rejection
totals — and returns `{"enabled": false}` when the mesh is off, specifically so an
operator can tell "off" apart from "on with zero peers." Those are different
problems and they look identical without that signal. It sits on the health-only
router beside `/_liveness` and `/_readiness`, not on the application router, so
reading mesh state does not go through the relay's auth, CORS or metrics
middleware.

## Boundaries and non-goals

- **Not the crate's implementation surface.** The module map, the two consumer
  seams, the typed `MeshError` taxonomy and the crate's own unit tests belong to
  `implementation-crates-buzz-relay-mesh`, which documents them at file grain.
  This node states what the plane *is*; that one states how it is built.
- **Not the deployment topology.** Replica counts, the Helm chart's autoscaling
  and PodDisruptionBudget, the install-time guard that refuses a multi-replica
  release without Redis, and the shared data stores belong to
  `architecture-deployment-multi-relay`.
- **Not mesh compute.** `layers-compute-mesh-compute` documents an unrelated
  subsystem that happens to share the word. Neither node's claims transfer to the
  other.
- **Not federation between relays.** The mesh joins the pods of one deployment,
  not independently operated relays or separate communities. The wire carries no
  community identity at all — community scoping enters only relay-side, in the
  Redis lease keys. Relay-to-relay traffic in the Nostr sense is a different
  subject entirely.
- **Not the pairing relay.** `buzz-pair-relay` is a second relay binary in the
  same Helm release for NIP-AB device pairing. It is not a replica of the main
  relay and does not join this mesh.
- **Not a client-facing surface.** No Buzz client speaks the mesh protocol. A
  client's only relationship to the mesh is that a session it opened may be
  served by a pod other than the one holding its socket.
- **Not the ownership mechanism.** How a lease is acquired, renewed, released and
  fenced is the relay-side session directory's, and this node states only the law
  the mesh holds itself to.

## Scope and omissions

**This node covers** what the relay mesh is as a networking-layer concept: which
plane it is among the three that make N relay processes one relay, what shape of
traffic it carries and why that traffic cannot use the others, how it is bounded
(ALPN, attestation, boot-unique identity, the fencing law), what it costs to run
without it, and its boundary against the three neighbouring nodes that use the
same word.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The crate's modules, seams, error taxonomy and unit tests | `implementation-crates-buzz-relay-mesh` |
| Chart topology, replicas, autoscaling, disruption budgets, failure and recovery | `architecture-deployment-multi-relay` |
| The huddle audio flow end to end, including the cross-pod case | `architecture-flows-huddle-audio` |
| Redis cross-pod event fan-out mechanics (channel naming, lifecycle, failure behaviour) | `layers-data-redis-channel-pubsub` |
| The MeshLLM shared-compute subsystem that shares the name | `layers-compute-mesh-compute` |
| Redis-mediated cross-pod *connection control* (`ConnControl`, `buzz:*:conn-control`), named here only to draw this node's boundary | Not filed as its own corpus task at this node's recorded revision — see below |

**Expected but not verified when this node was written:**

- **No live multi-pod mesh was exercised.** Every claim above is read from source
  at the recorded revision. No relay was started, no `BUZZ_MESH=on` deployment was
  brought up, and `GET /_mesh` was never called against a running process — the
  claim about its `{"enabled": false}` payload is read from the handler, not
  observed.
- **The repository has no integration or end-to-end test for the relay mesh, and
  this was looked for rather than assumed.** `crates/buzz-test-client/tests/`
  holds nineteen test files; the only one naming "mesh" is `e2e_mesh_llm.rs`,
  which scopes itself to Buzz shared compute — the other subsystem. Coverage for
  this subject exists only as the mesh crate's own in-process unit tests, which
  `implementation-crates-buzz-relay-mesh` catalogues.
- **Whether any deployment currently runs with `BUZZ_MESH=on` was not
  determined.** `architecture-deployment-multi-relay` independently records that
  the local HA testbed does not set it; nothing here establishes what production
  does, and this node claims nothing either way.
- **No specification governs the mesh.** No ADR under `launchpad/decisions/` and
  no NIP under `docs/nips/` was found by `implementation-crates-buzz-relay-mesh`'s
  own search, and this node did not repeat that search. The crate is self-
  specifying, so the definition above rests on code and in-code contract
  documentation rather than on an accepted decision record.
