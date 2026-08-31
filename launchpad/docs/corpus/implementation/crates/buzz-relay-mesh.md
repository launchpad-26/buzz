---
id: implementation-crates-buzz-relay-mesh
type: implementation
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - operator
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 76a0a4ebbe4bc4d852b0d04362ed768620da34b3."
    entry_class: FACT
    evidence:
      - "commit 76a0a4ebbe4bc4d852b0d04362ed768620da34b3"
  - statement: "buzz-relay-mesh's Cargo.toml describes it as 'Inter-relay QUIC mesh: transport, membership, and the fenced wire contract', has no crate-local README.md, and depends on iroh (QUIC transport), redis/deadpool-redis (ready-registry bootstrap), postcard (wire encoding), nostr (relay-key attestation signatures) and tokio; only crates/buzz-relay and the workspace root Cargo.toml reference it as a dependency, so buzz-relay is its sole in-repo consumer."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay-mesh/Cargo.toml"
      - "crates/buzz-relay/Cargo.toml"
      - "Cargo.toml"
  - statement: "crates/buzz-relay-mesh/src/lib.rs's module documentation states the crate exposes exactly two consumer seams -- RelayMeshMembership ('who is alive / draining / dialable?') and RelayPeerTransport ('move these bytes to that runtime') -- and states 'the law: mesh membership is a hint; the Redis fenced generation is the arbiter. Nothing in this crate grants ownership.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-relay-mesh/src/lib.rs:1-19"
  - statement: "lib.rs defines MeshError with four distinct fence-rejection variants named as typed enum members -- StaleGeneration, NoActiveLease, OwnerMismatch, FutureGeneration -- documented as 'every fence-visible reject is a typed variant, never a generic Transport' so each is independently countable, plus Encode/Decode/UnknownWireVersion/EmptyFrame/FrameTooLarge/DatagramTooLarge/PeerNotConnected/PeerDraining/Disabled/Transport/Redis variants."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay-mesh/src/lib.rs:65-125"
  - statement: "crates/buzz-relay-mesh/src/wire.rs opens with 'The mesh wire contract -- FROZEN surface' and states 'Changes here require a post in the mesh thread before the edit', defines ALPN = b\"buzz/mesh/1\", WIRE_VERSION = 1, MAX_STREAM_FRAME = 16 MiB, RuntimeId (an ed25519 public key of a boot-unique keypair generated fresh at process start, deliberately not the deployment's shared secp256k1 Nostr relay key), FencedHeader{session_id, generation, owner_runtime_id}, Profile{ReliableStream, RealtimeMedia, HuddleControl}, MeshDatagram, MeshStreamFrame{Hello, Data, Goodbye, Gossip}, StreamRole, StreamHello, and GoodbyeReason."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay-mesh/src/wire.rs:1-64"
      - "crates/buzz-relay-mesh/src/wire.rs:110-190"
  - statement: "crates/buzz-relay-mesh/src/endpoint.rs's MeshEndpoint::bind generates a fresh SecretKey and binds one iroh endpoint per relay process with RelayMode::Disabled and the mesh ALPN; MeshEndpoint::bind_with_secret_key exists so tests get stable identities while production code always calls bind for a fresh boot-unique RuntimeId."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay-mesh/src/endpoint.rs:17-45"
  - statement: "crates/buzz-relay-mesh/src/peer.rs's MeshPeer::from_connection rejects a connection outright if its negotiated ALPN does not equal the mesh ALPN, and MeshPeer tracks per-peer PeerCounters (streams_opened, streams_accepted, datagrams_sent, datagrams_received) that feed /_mesh status."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay-mesh/src/peer.rs:44-58"
  - statement: "crates/buzz-relay-mesh/src/registry.rs implements a Redis-backed ready-registry keyed mesh:ready:{runtime_id}, where ReadyRecord carries a RuntimeAttestation (a Schnorr signature by the deployment's Nostr/secp256k1 relay key over the boot-unique runtime pubkey), ReadyRegistry::publish_ready's doc states callers 'MUST only invoke this after the relay would pass readiness' with no hidden readiness probe inside the crate, and expiry_for sets TTL to REGISTRY_EXPIRY_MULTIPLIER (3) times the refresh interval."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay-mesh/src/registry.rs:1-22"
      - "crates/buzz-relay-mesh/src/registry.rs:78-100"
      - "crates/buzz-relay-mesh/src/registry.rs:141-150"
  - statement: "crates/buzz-relay-mesh/src/membership.rs's MeshMembership (implementing RelayMeshMembership) is documented as 'deliberately incapable of electing session owners'; its apply_ready_records only admits a ready record when its relay_pubkey matches an explicitly configured expected_relay_pubkey anchor AND the attestation signature verifies, and the field's own comment states the unanchored (None) state 'rejects every ready record: the unanchored state is fail-closed, not accept-any.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-relay-mesh/src/membership.rs:1-9"
      - "crates/buzz-relay-mesh/src/membership.rs:35-42"
  - statement: "crates/buzz-relay-mesh/src/gossip.rs's module doc states gossip 'answers liveness/dialability questions only. It never elects owners, never transfers sessions, and never carries tunnel data bytes'; GossipState applies scuttlebutt-style last-version-wins deltas via apply_delta, and PhiAccrual computes a phi-accrual suspicion score from observed heartbeat inter-arrival samples."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay-mesh/src/gossip.rs:1-6"
      - "crates/buzz-relay-mesh/src/gossip.rs:56-95"
  - statement: "crates/buzz-relay-mesh/src/runtime.rs's MeshRuntime implements RelayPeerTransport (send_datagram, open_session_stream, set_inbound) and runs an accept loop that admits an inbound connection only when the remote runtime id is present in the attested membership table (with one registry rescan for unknown ids), a reconcile loop that dials every known non-draining peer not yet connected, one control stream per peer connection carrying scuttlebutt digest/delta gossip, and a deterministic simultaneous-dial tie-break where the connection dialed by the smaller RuntimeId wins."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay-mesh/src/runtime.rs:1-20"
      - "crates/buzz-relay-mesh/src/runtime.rs:409-431"
  - statement: "crates/buzz-relay-mesh/src/status.rs defines MeshStatus/MeshPeerStatus/MeshCounters/MeshPeerCounters/ConnectionState as a pure serde-Serialize data model with a doc comment stating 'the relay's axum handler can serialize MeshStatus directly as JSON', with no behavior of its own."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay-mesh/src/status.rs:1-15"
  - statement: "crates/buzz-relay/src/mesh_boot.rs's module doc states 'boot_mesh is the ONLY place the relay constructs mesh machinery. It returns None -- and touches nothing -- when BUZZ_MESH=off', and boot_mesh's own doc comment states an operator who explicitly enables the mesh gets loud failure on misconfiguration (bind failure, unreachable Redis) rather than a silent fallback to single-instance behavior; MeshHandle bundles the session directory, RelayPeerTransport, RelayMeshMembership, local RuntimeId, MeshInboundDispatcher and the running MeshRuntime into one struct for consumers."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/mesh_boot.rs:1-19"
      - "crates/buzz-relay/src/mesh_boot.rs:133-168"
      - "crates/buzz-relay/src/mesh_boot.rs:405-421"
  - statement: "crates/buzz-relay/src/config.rs resolves BUZZ_MESH by mapping it case-insensitively against 'on'/'true'/'1' and defaulting to false (mesh disabled) for an absent, 'off', or any other value, with an inline comment stating this is a deliberate strict-opt-in, no-regression choice: 'an image upgrade with untouched env must not bind a new UDP port or write a new Redis key.' BUZZ_MESH_BIND_ADDR defaults to 0.0.0.0:3478 when unset."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/config.rs:680-699"
  - statement: "crates/buzz-relay/src/router.rs registers GET /_mesh (live mesh status) and POST /_mesh/demo/echo (a testbed-only reliable-stream echo consumer, 404 unless the deployment opted in via BUZZ_MESH_DEMO_ECHO)."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs:135"
      - "crates/buzz-relay/src/router.rs:299"
  - statement: "crates/buzz-relay/src/tunnel/directory.rs's module doc states its own correctness law -- 'mesh membership is only a routing hint. Redis is the arbiter for session ownership, and every session-bearing frame must validate its {session_id, generation, owner_runtime_id} fence against this directory before it is accepted or forwarded' -- and it, not buzz-relay-mesh, owns the Redis fenced CAS lease acquisition (ACQUIRE_SCRIPT) for tunnel sessions."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/tunnel/directory.rs:1-20"
  - statement: "crates/buzz-relay/src/audio/mesh.rs's module doc describes an owner-authoritative cross-pod huddle audio model built on top of buzz-relay-mesh's transport: one pod owns a huddle (the holder of the Redis fenced CAS lease, exposed via HuddleOwnerDirectory), non-owner pods forward client Opus frames to the owner as datagrams and register remote peers over a HuddleControl stream -- this fan-out, ownership and room/peer-index allocation logic lives in buzz-relay, not in the mesh crate."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/audio/mesh.rs:1-20"
  - statement: "cargo test -p buzz-relay-mesh --lib, run against this crate's source at the recorded revision, compiled and passed all 32 unit/async tests (0 failed) spanning endpoint.rs (5), gossip.rs (4), membership.rs (7), registry.rs (6), runtime.rs (6) and wire.rs (4), with no external Postgres/Redis service running -- the registry.rs tests exercise attestation/key/expiry logic only, not live Redis I/O."
    entry_class: FACT
    evidence:
      - "cargo_test(package='buzz-relay-mesh', profile='test') -> 'test result: ok. 32 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 2.48s'"
  - statement: "No ADR under launchpad/decisions/ or NIP document under docs/nips/ specifies the buzz-relay-mesh wire protocol, membership model, or ready-registry contract; a repository-wide grep for 'mesh' across both directories surfaces only unrelated matches (ADR-0051's MeshComputeSettingsCard UI component name; NIP-PMA's passing mention of 'relay-mesh' in an unrelated deprecation list), so this crate has no external governing specification with a corpus node id to declare an implements edge toward."
    entry_class: FACT
    evidence:
      - "grep(pattern='mesh', path='launchpad/decisions/*.md') -> 1 match, ADR-0051-cohort-settings-registration-seam.md:47 (MeshComputeSettingsCard, unrelated UI component)"
      - "grep(pattern='mesh', path='docs/nips/*.md') -> 1 match, NIP-PMA.md:78 (unrelated deprecation list mention)"
  - statement: "architecture-deployment-multi-relay and architecture-containers-relay, both already merged on origin/launchpad, cite crates/buzz-relay-mesh's source files directly and describe the same crate from the deployment/HA-topology and container-architecture surfaces respectively; both were authored by reading this crate's code rather than being a governing specification the crate was built against, which is why this node declares them as references rather than implements."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/deployment/multi-relay.md:46-93"
      - "launchpad/docs/corpus/architecture/containers/relay.md:50-53"
---

# buzz-relay-mesh: implementation reference

`crates/buzz-relay-mesh` implements the opt-in inter-relay QUIC mesh: one iroh
transport endpoint per relay process, a Redis-backed ready-registry bootstrap,
scuttlebutt membership gossip, and a frozen wire contract carrying huddle-audio
datagrams and reliable-stream tunnel traffic directly between relay pods. This
node documents that crate's implementation surface -- what it owns, its two
public consumer seams, its typed error taxonomy, and how `crates/buzz-relay`
wires it into the running relay via `boot_mesh` -- checked against the crate's
own source, its unit test suite, and the two existing architecture-level
corpus nodes that already describe it from a different altitude.

## Target

There is no external ADR, NIP, or other governing specification document for
the inter-relay mesh protocol at this repository revision (checked:
`launchpad/decisions/*.md` and `docs/nips/*.md`; the only "mesh" matches in
either tree are unrelated -- ADR-0051's `MeshComputeSettingsCard` UI component
name and NIP-PMA's passing, unrelated mention of "relay-mesh" in a
deprecation-markers list). The crate is self-specifying: its own module
documentation states the contract implementers on both ends must satisfy, and
this node treats that documentation as the target the implementation surface
below is checked against:

- `crates/buzz-relay-mesh/src/lib.rs`'s module doc states "the fencing law":
  mesh membership is a hint; the Redis fenced generation is the arbiter, and
  nothing in the crate grants ownership.
- `crates/buzz-relay-mesh/src/wire.rs`'s header marks itself a "FROZEN
  surface" and requires every session-bearing frame to carry a `FencedHeader`
  that receivers MUST reject when stale, at every hop.

Two already-merged corpus nodes independently describe this same crate from
the deployment and container-architecture surfaces:
`architecture-deployment-multi-relay` (the HA/mesh deployment topology) and
`architecture-containers-relay` (the relay container's full responsibility
list, including its mesh seam). Both were authored by reading this crate's
code, not the reverse, so they are documented below as `references` --
siblings at a different altitude -- rather than as an `implements` target.

## Implementation surface

| Component / file / symbol | Realizes | Note |
|---|---|---|
| `crates/buzz-relay-mesh/src/wire.rs` -- `ALPN`, `WIRE_VERSION`, `RuntimeId`, `FencedHeader`, `Profile`, `MeshDatagram`, `MeshStreamFrame`, `StreamHello`, `StreamRole`, `GoodbyeReason`, `encode`/`decode` | The frozen wire contract: frame shapes, the fencing tuple `{session_id, generation, owner_runtime_id}`, and a versioned ALPN so mixed-version pods never half-speak during a rolling deploy. | File states "Changes here require a post in the mesh thread before the edit." |
| `crates/buzz-relay-mesh/src/endpoint.rs` -- `MeshEndpoint::bind`/`bind_with_secret_key`/`accept`/`connect` | One iroh QUIC endpoint per relay process; identity is a boot-unique ed25519 keypair, relay mode disabled, ALPN pinned to the mesh ALPN. | `bind_with_secret_key` exists only so tests get stable identities. |
| `crates/buzz-relay-mesh/src/peer.rs` -- `MeshPeer::from_connection`/`open_bi`/`accept_bi`/`send_datagram`/`recv_datagram` | An authenticated iroh connection to one peer runtime; rejects a connection whose negotiated ALPN is not the mesh ALPN. | Per-peer `PeerCounters` feed `/_mesh` status. |
| `crates/buzz-relay-mesh/src/registry.rs` -- `RuntimeAttestation`, `ReadyRecord`, `ReadyRegistry`, `ReadyHeartbeat` | Redis `mesh:ready:{runtime_id}` bootstrap registry: a relay-key-signed attestation binding a boot-unique endpoint pubkey, published/renewed by a readiness-gated heartbeat with a 3x-refresh TTL. | `publish_ready` documents that callers MUST only invoke it once the relay itself would pass readiness. |
| `crates/buzz-relay-mesh/src/membership.rs` -- `MeshMembership` (`impl RelayMeshMembership`) | In-memory peer table fed by ready-registry seeds and gossip; admits a ready record only when its `relay_pubkey` matches an explicitly configured anchor (fail-closed when unset); never elects session owners. | `apply_ready_records` doc: "Matching first makes the authorization question explicit." |
| `crates/buzz-relay-mesh/src/gossip.rs` -- `GossipRecord`, `GossipState`, `GossipMessage`, `PhiAccrual` | Scuttlebutt-style digest/delta gossip (last-version-wins per runtime) plus phi-accrual suspicion; answers liveness/dialability only. | Module doc: "never elects owners, never transfers sessions, never carries tunnel data bytes." |
| `crates/buzz-relay-mesh/src/runtime.rs` -- `MeshRuntime` (`impl RelayPeerTransport`), accept/reconcile loops, control-stream exchange | The live runtime: admits inbound connections only from attested known peers, dials every known non-draining peer, one gossip control stream per peer, and a deterministic simultaneous-dial tie-break (smaller `RuntimeId` wins). | Reconcile loop is what makes the mesh "warm" -- failover is "next frame goes elsewhere." |
| `crates/buzz-relay-mesh/src/status.rs` -- `MeshStatus`, `MeshPeerStatus`, `MeshCounters`, `MeshPeerCounters`, `ConnectionState` | A serializable status/counter data model the relay's `GET /_mesh` handler returns directly as JSON. | No behavior -- pure data model. |
| `crates/buzz-relay-mesh/src/lib.rs` -- `MeshConfig`, `MeshError`, `PeerInfo`, `RelayMeshMembership`, `RelayPeerTransport`, `InboundHandler`, `MeshStream` | The two public consumer seams (membership, transport); a typed error taxonomy including four distinct fence-rejection variants (`StaleGeneration`, `NoActiveLease`, `OwnerMismatch`, `FutureGeneration`); `MeshConfig` (`BUZZ_MESH`/`BUZZ_MESH_BIND_ADDR`/registry refresh). | Doc comment: single-instance deployments stay "mesh-free" when `BUZZ_MESH=off` or no peers exist. |
| `crates/buzz-relay/src/mesh_boot.rs` -- `boot_mesh`, `MeshHandle`, `MeshInboundDispatcher` | Relay-side wiring: the ONLY place the relay constructs mesh machinery, returning `None` untouched when disabled; bundles transport/membership/dispatcher/local runtime id into `MeshHandle`. | An explicitly-enabled but misconfigured mesh fails relay startup loudly rather than falling back silently. |

## Divergences

None found between the crate's own stated contract (see *Target* above) and
its implementation, checked as follows:

- `MeshConfig`'s fields (`enabled`, `bind_addr`, `registry_refresh`) were
  cross-checked against `crates/buzz-relay/src/config.rs`'s actual resolution
  of `BUZZ_MESH`/`BUZZ_MESH_BIND_ADDR`: the code requires an explicit
  `on`/`true`/`1` value and defaults closed (mesh disabled, byte-identical to
  a build before the mesh existed) for every other input, including an absent
  variable -- consistent with `mesh_boot.rs`'s own "touches nothing when
  `BUZZ_MESH=off`" claim and with `architecture-deployment-multi-relay`'s
  independently-reached description of the same default.
- The fencing law stated in `lib.rs` and `wire.rs` was checked against actual
  callers: `crates/buzz-relay/src/tunnel/directory.rs` (not this crate) owns
  the Redis fenced CAS lease acquisition, and `crates/buzz-relay-mesh` itself
  contains no code that acquires or mutates a session-ownership lease --
  consistent with the stated seam boundary.
- The four fence-rejection `MeshError` variants named in `lib.rs`'s comment
  (`stale_generation | no_active_lease | owner_mismatch | future_generation`)
  match the four enum variant names actually defined in the same file.

An empty divergence section on a node checked against real code is itself a
claim, per the template's evidence expectations -- the three checks above are
what that claim rests on, not silence.

## Verification

`cargo test -p buzz-relay-mesh --lib`, run against this crate's source at the
recorded revision with no external Postgres/Redis service running, compiled
and passed all 32 unit/async tests: `endpoint.rs` (5, including
`two_endpoints_connect_with_alpn_and_authenticated_identity` and
`oversized_datagram_is_rejected_before_send`), `gossip.rs` (4, including
`digest_delta_only_sends_newer_records` and `phi_rises_as_heartbeats_age`),
`membership.rs` (7, including `ready_records_from_foreign_relay_identity_are_rejected`
and `unanchored_membership_rejects_all_ready_records`), `registry.rs` (6,
including `attestation_rejects_signature_for_other_runtime`), `runtime.rs` (6,
including `simultaneous_dial_converges_to_one_connection` and
`warm_pair_connects_and_gossips_membership`), and `wire.rs` (4, including
`unknown_version_rejected` and `datagram_header_overhead_within_budget`). No
separate CI job or manual-review procedure specific to this crate was found
beyond the workspace-wide `just ci` gate documented in the repository's own
`AGENTS.md`.

## Relationships

- references: architecture-deployment-multi-relay
- references: architecture-containers-relay

## Scope and omissions

**This node covers** `buzz-relay-mesh`'s implementation responsibility (QUIC
transport, ready-registry bootstrap, membership gossip, the frozen wire
contract), its two public consumer seams (`RelayMeshMembership`,
`RelayPeerTransport`), its typed error taxonomy, its owned source paths and
representative tests, and how `crates/buzz-relay/src/mesh_boot.rs` wires it
into the running relay.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Redis fenced session-ownership CAS lease acquisition / session directory | `crates/buzz-relay/src/tunnel/directory.rs` |
| Reliable-stream tunnel routing built atop the mesh transport | `crates/buzz-relay/src/tunnel/reliable.rs` |
| Cross-pod huddle audio owner-authoritative fan-out and room/peer-index allocation | `crates/buzz-relay/src/audio/mesh.rs`, `crates/buzz-relay/src/audio/join.rs`, `crates/buzz-relay/src/audio/handler.rs` |
| Kubernetes/Helm chart replica scaling, Istio sidecar exclusion, and the wider HA deployment topology | `architecture-deployment-multi-relay` |
| The relay container's full responsibility list and HTTP surface beyond the mesh seam | `architecture-containers-relay` |

**Expected but not verified when this node was written:**

- No live multi-pod mesh deployment (real Kubernetes replicas exchanging
  traffic over a real network) was exercised in this session; the tests cited
  under *Verification* run entirely in-process against loopback iroh
  endpoints and an in-memory membership table, not against a deployed
  cluster.
- Whether any non-`quickstart` deployment of this repository currently runs
  with `BUZZ_MESH=on` was not checked -- `architecture-deployment-multi-relay`
  independently notes the same gap for the local HA testbed.
- Whether `cargo test -p buzz-relay-mesh` (workspace-wide, beyond `--lib`) or
  the full `just ci` gate passes was not checked; only the crate's own `--lib`
  unit test target was run.
