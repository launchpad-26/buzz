---
id: architecture-deployment-multi-relay
type: architecture
status: draft
origin: launchpad
audiences:
  - operator
  - developer
evidence:
  - statement: "This node was authored and checked against repository revision a44cf52fc740ebebbdd671427480d14f0bce0115."
    entry_class: FACT
    evidence:
      - "commit a44cf52fc740ebebbdd671427480d14f0bce0115"
  - statement: "The Kubernetes Helm chart at deploy/charts/buzz is the only in-repo deployment path that supports running more than one relay replica; the Docker Compose bundle at deploy/compose is explicitly documented as a single-node/VPS deployment."
    entry_class: FACT
    evidence:
      - "deploy/charts/buzz/values.yaml"
      - "deploy/compose/README.md"
  - statement: "The chart's replicaCount (fixed) and autoscaling.minReplicas/maxReplicas (HPA) both scale one Kubernetes Deployment of the buzz-relay container image; there is no separate per-replica manifest or StatefulSet in this chart."
    entry_class: FACT
    evidence:
      - "deploy/charts/buzz/values.yaml"
      - "deploy/charts/buzz/templates/deployment.yaml"
      - "deploy/charts/buzz/templates/hpa.yaml"
  - statement: "A chart-side template guard fails helm install/upgrade outright when the resolved minimum replica count exceeds 1 and none of redis.enabled, externalRedis.url, or secrets.existingSecret (with a REDIS_URL key) is set, because buzz-pubsub requires Redis to fan messages out across replicas."
    entry_class: FACT
    evidence:
      - "deploy/charts/buzz/templates/_validate.tpl"
  - statement: "Relay replicas do not require ReadWriteMany git storage: git ref/object state is object-store-backed (each request hydrates an ephemeral repo from S3-compatible storage, and writer serialization is the object-store pointer CAS), and repo-name uniqueness lives in Postgres, not on a shared volume."
    entry_class: FACT
    evidence:
      - "deploy/charts/buzz/values.yaml"
  - statement: "The local HA testbed (quickstart-ha-values.yaml, 3 replicas) sets persistence.git.enabled: false so each pod gets a per-pod emptyDir instead of the chart's default single ReadWriteOnce PVC, because one RWO PVC cannot multi-attach across 3 pods on one node and would wedge two of the three."
    entry_class: FACT
    evidence:
      - "deploy/local/quickstart-ha-values.yaml"
  - statement: "The chart's autoscaling can scale on CPU utilization (Metrics Server) and, when websocketMetricEnabled is true, on a custom Prometheus gauge (buzz_ws_connections_active) via a custom-metrics adapter; the HPA takes the larger replica recommendation across whichever metrics are enabled."
    entry_class: FACT
    evidence:
      - "deploy/charts/buzz/values.yaml"
      - "deploy/charts/buzz/templates/hpa.yaml"
  - statement: "A PodDisruptionBudget is rendered only when podDisruptionBudget.enabled is true and the resolved minimum replica count exceeds 1, guarding voluntary disruption (node drain, cluster upgrade) once more than one relay pod exists."
    entry_class: FACT
    evidence:
      - "deploy/charts/buzz/templates/pdb.yaml"
  - statement: "crates/buzz-relay-mesh implements an opt-in inter-relay QUIC mesh: one iroh transport endpoint per relay process, scuttlebutt gossip membership, and a fenced wire contract carrying huddle-audio datagrams and reliable-stream tunnel traffic directly between relay pods, bypassing the shared data stores for that traffic's data plane."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay-mesh/src/lib.rs"
      - "crates/buzz-relay-mesh/Cargo.toml"
  - statement: "The relay only constructs mesh machinery when the BUZZ_MESH environment variable resolves to on/true/1; any other value, including an absent variable, produces exact single-instance behavior with no UDP bind and no Redis registry write. The Helm chart itself sets no default for BUZZ_MESH -- an operator must pass it explicitly through relay.extraEnv."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/config.rs"
      - "crates/buzz-relay/src/mesh_boot.rs"
      - "deploy/charts/buzz/values.yaml"
  - statement: "The local HA testbed (quickstart-ha-values.yaml, consumed by deploy/local/build-and-deploy.sh) does not set BUZZ_MESH, so it exercises multi-replica horizontal scaling behind shared Postgres/Redis/S3 but not mesh formation; it is not, by itself, evidence that the mesh path has been exercised against that testbed."
    entry_class: FACT
    evidence:
      - "deploy/local/quickstart-ha-values.yaml"
      - "deploy/local/build-and-deploy.sh"
  - statement: "A mesh runtime's identity (RuntimeId) is the ed25519 public key of a fresh keypair generated at process start, deliberately not the shared secp256k1 Nostr relay signing key every pod of one release holds in common -- using the shared key would give every pod the same runtime id and collapse the ownership plane. Peers accept mesh connections only from endpoint ids present in a ready-registry or gossip record attested by that shared relay key."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay-mesh/src/wire.rs"
      - "crates/buzz-relay-mesh/src/membership.rs"
  - statement: "Mesh membership (gossip, phi-accrual suspicion, ready-registry heartbeats) is documented as a routing hint only and is deliberately incapable of electing session owners; the arbiter for who owns a session is a Redis-backed fenced lease with a {session_id, generation, owner_runtime_id} tuple that every session-bearing frame must carry and every hop must validate."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay-mesh/src/wire.rs"
      - "crates/buzz-relay-mesh/src/membership.rs"
      - "crates/buzz-relay/src/tunnel/directory.rs"
  - statement: "Session-ownership leases are acquired, renewed, and released through Redis Lua scripts (EVALSHA-style atomic GET/INCR/SET with a millisecond TTL) rather than a client-side check-then-set, so lease state changes atomically even under concurrent relay pods; a lease's TTL means a crashed owner's lease expires rather than requiring an explicit release."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/tunnel/directory.rs"
  - statement: "The mesh error taxonomy names four distinct fence-rejection reasons (stale_generation, no_active_lease, owner_mismatch, future_generation) as typed enum variants rather than one generic transport error, each counted separately, so a fence rejection observed in metrics or logs is diagnosable without re-deriving it from a generic failure."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay-mesh/src/lib.rs"
  - statement: "On graceful shutdown, a drain watcher gossips draining=true for the local runtime, generation-fences and drains locally-owned huddle leases, and clears the runtime's ready-registry heartbeat record, so peers stop routing new sessions to a draining pod before it exits."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/mesh_boot.rs"
  - statement: "The relay exposes live mesh status (peer table, connection/phi state, per-peer counters) over HTTP at GET /_mesh, distinct from the health-only router's /_liveness and /_readiness probes that Kubernetes uses for rollout gating."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs"
      - "crates/buzz-relay/src/config.rs"
  - statement: "The mesh's UDP bind (default 0.0.0.0:3478) is documented in-crate as intended to be excluded from Istio sidecar traffic capture, but the chart's own pod-annotation fields default to empty -- the chart does not apply that exclusion automatically, so an operator deploying under an Istio-meshed cluster must add the sidecar exclusion annotation themselves via relay.podAnnotations (or equivalent) for the two mesh planes not to conflict."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay-mesh/src/lib.rs"
      - "deploy/charts/buzz/values.yaml"
    confidence: 0.7
  - statement: "The chart also renders an entirely separate, optional relay deployment -- buzz-pair-relay, a stateless NIP-AB device-pairing relay under pairingRelay.* -- as its own Kubernetes Deployment/Service alongside the main relay Deployment. It is a second relay process in the same release, not a replica of the main relay and not part of the inter-relay mesh described above; this document does not cover its topology in depth."
    entry_class: FACT
    evidence:
      - "deploy/charts/buzz/templates/pairing-relay.yaml"
      - "deploy/charts/buzz/values.yaml"
  - statement: "Issue #673's definition of done requires naming the environment/topology and physical/virtual execution nodes, mapping Buzz containers/services/data stores to those nodes, describing network/persistence/trust boundaries without exposing secrets, and linking deployment automation/config as authority with failure/recovery implications."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#673 definition of done"
  - statement: "The issue title (architecture/deployment/multi-relay.md) does not itself disambiguate whether 'multi-relay' means the mesh/replica topology described here, the separate pairing-relay process, or a multi-community model where each Buzz community is backed by an independently deployed relay; this document resolves that ambiguity by scoping to the mesh/replica topology and naming the other readings explicitly rather than silently picking one."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#673 issue body (Objective line) and author judgment recorded in launchpad/plans/2026-08-27-issue-673-corpus-doc.md"
---

# Multi-Relay Deployment Topology

## Scope

"Multi-relay" resolves to two distinct, both-real mechanisms in this codebase. This
document covers the first in depth and names the second only to keep it from being
mistaken for out-of-scope silence:

1. **Horizontal scaling of `buzz-relay` itself** — more than one replica of the same
   relay Deployment, backed by shared Postgres/Redis/object storage, optionally forming
   an inter-relay QUIC mesh for session-bearing traffic. This is what
   `crates/buzz-relay-mesh`'s own module documentation and the local HA deploy tooling
   call the relay mesh / HA topology, and is the subject of the rest of this document.
2. **`buzz-pair-relay`** — a second, architecturally distinct relay binary for NIP-AB
   device pairing, deployed as its own optional Kubernetes Deployment in the same Helm
   release (`pairingRelay.*`). It is not a replica of the main relay and does not
   participate in the mesh described below. See
   `deploy/charts/buzz/templates/pairing-relay.yaml`. Not documented further here to
   keep this node to one concept.

A third possible reading — a multi-community model where each community is backed by
an independently deployed relay (the desktop app's community-switching model) — is a
client-side multiplexing concern, not a deployment topology of one relay's own
replicas, and is out of scope for this node.

## Environment and Topology

The only in-repo deployment path that supports more than one relay replica is the
Kubernetes Helm chart at `deploy/charts/buzz` (production tier: external
Postgres/Redis/S3; quickstart tier: bundled in-cluster Postgres/Redis/MinIO,
single-replica evaluation only unless overridden). `deploy/compose` is explicitly
documented as the single-node/VPS bundle and is out of scope for multi-relay topology.

The execution node for each relay replica is one Kubernetes Pod, all pods belonging to
one `apps/v1 Deployment` (`deploy/charts/buzz/templates/deployment.yaml`), scaled by
either a fixed `replicaCount` or a `HorizontalPodAutoscaler`
(`deploy/charts/buzz/templates/hpa.yaml`) driven by CPU utilization and, optionally, a
custom Prometheus gauge (`buzz_ws_connections_active`) exposing live WebSocket
connection count per pod. There is no StatefulSet and no per-replica identity beyond
the Pod's own network identity — replicas are treated as interchangeable by the
Deployment/HPA/PDB machinery.

A chart-side template guard (`deploy/charts/buzz/templates/_validate.tpl`) fails
`helm install`/`upgrade` outright, before any resource is applied, when the resolved
minimum replica count exceeds 1 and no Redis source (`redis.enabled`,
`externalRedis.url`, or a `secrets.existingSecret` carrying `REDIS_URL`) is configured
— multi-replica is refused at install time, not discovered as a runtime failure.

## Containers, Services, and Data Stores

| Component | What it is | Where it lives relative to a relay pod |
|---|---|---|
| `buzz-relay` container | The relay binary; the Deployment's only application container | One per Pod, N Pods per Deployment |
| Postgres | Event store, repo-name uniqueness registry | External service (production) or in-cluster subchart (quickstart); shared by every replica |
| Redis | `buzz-pubsub` fan-out across replicas, presence/typing, and (mesh only) the fenced session-ownership lease store | External service or in-cluster subchart; shared by every replica; hard-required once replica count exceeds 1 |
| S3-compatible object storage | Git object/ref state (ephemeral per-request hydration, pointer-CAS writer serialization) and Blossom media blobs | External service or in-cluster MinIO (quickstart); shared by every replica |
| Per-pod git scratch volume | Working directory for the ephemeral per-request git hydration | Either a PVC (default; wedges beyond 1 replica per node under RWO) or a per-pod `emptyDir` (the HA testbed's choice — see `deploy/local/quickstart-ha-values.yaml`) |
| `buzz-pair-relay` (optional) | Separate NIP-AB pairing relay | Its own Deployment/Service in the same release, not part of this topology's replica set |

None of the four shared data stores above (Postgres, Redis, object storage, and the
optional Redis-backed mesh lease store) is replica-local: a relay pod holds no durable
state of its own beyond the transient git scratch volume. This is what makes the
Deployment's pods interchangeable to the HPA and PDB.

## The Optional Inter-Relay Mesh

Independently of replica-count scaling, `crates/buzz-relay-mesh` implements an opt-in
QUIC mesh between relay pods, wired into the relay at startup by
`crates/buzz-relay/src/mesh_boot.rs`. The relay constructs mesh machinery only when
`BUZZ_MESH` resolves to `on`/`true`/`1`; any other value — including an absent
variable, which is the Helm chart's own default (the chart sets no `BUZZ_MESH` value
and it must be supplied by the operator via `relay.extraEnv`) — is exact
single-instance behavior: no UDP bind, no Redis registry write. The local HA testbed
(`deploy/local/quickstart-ha-values.yaml`, driven by
`deploy/local/build-and-deploy.sh`) does not set `BUZZ_MESH`, so by itself it exercises
multi-replica scaling behind the shared data stores above, not mesh formation.

When enabled, each relay process binds one iroh QUIC endpoint (default
`0.0.0.0:3478`) under a fresh, boot-unique ed25519 keypair — deliberately not the
shared secp256k1 Nostr relay signing key every pod in a release holds in common, since
reusing that key would give every pod the same mesh identity and collapse the
ownership plane. Peers gossip scuttlebutt-style membership and phi-accrual liveness
suspicion, and a peer accepts a mesh connection only from an endpoint id present in a
ready-registry or gossip record attested by the shared relay signing key. The mesh
carries two kinds of session-bearing traffic directly pod-to-pod: realtime huddle-audio
datagrams and reliable-stream tunnel data — bypassing the shared data-store data plane
for that traffic, while still using Redis as the ownership arbiter (below).

The mesh's UDP port is documented in-crate as intended for exclusion from Istio
sidecar traffic capture in a service-mesh-enabled cluster, but the chart's pod
annotation fields default to empty — the chart does not apply that exclusion
automatically. An operator deploying under Istio must add the sidecar-exclusion
annotation themselves (assessed as INFERENCE in the evidence ledger above, since no
in-repo chart value currently sets it).

## Trust and Ownership Boundary: Membership Is a Hint, Redis Is the Arbiter

The mesh crate states its own correctness law directly: membership (gossip, ready
registry, phi-accrual suspicion) may say "don't dial" but may never say "take over."
Every session-bearing frame carries a fenced tuple —
`{session_id, generation, owner_runtime_id}` — and every hop must reject a frame whose
generation is stale for that session. The arbiter for who currently owns a session is
a Redis-backed lease (`crates/buzz-relay/src/tunnel/directory.rs`): acquire, renew, and
release run as single atomic Lua scripts against Redis (GET/INCR/SET with a
millisecond TTL) rather than a client-side check-then-set, so lease transitions stay
atomic under concurrent relay pods, and a crashed owner's lease expires on its own TTL
instead of requiring an explicit release. Four distinct fence-rejection reasons —
stale generation, no active lease, owner mismatch, and future generation — are typed
enum variants with their own counters, not a single generic transport error, so a
rejection observed in metrics or logs is diagnosable without re-deriving it from a
catch-all failure.

No secret material (the relay's Nostr private key, Redis credentials, S3 credentials)
is named here beyond the fact of its existence and where the chart sources it
(`existingSecret` references, `externalRedis.url`/`externalPostgresql.url` — see the
chart's own `values.yaml` for the exact keys); this document does not reproduce any
credential value or connection string.

## Failure and Recovery Implications

- **Voluntary disruption (node drain, cluster upgrade):** guarded by a
  `PodDisruptionBudget`, rendered only when `podDisruptionBudget.enabled` is true and
  the resolved minimum replica count exceeds 1
  (`deploy/charts/buzz/templates/pdb.yaml`).
- **Involuntary pod loss (crash, eviction):** a session lease's Redis TTL expires on
  its own; the fenced-generation check means a stale frame from a since-restarted or
  since-superseded owner is rejected rather than silently accepted, at every hop, not
  just at the directory.
- **Graceful shutdown (mesh enabled):** a drain watcher gossips `draining=true`,
  generation-fences and drains locally-owned huddle leases, and clears the runtime's
  ready-registry heartbeat before the pod exits, so peers stop routing new sessions to
  it ahead of termination (`crates/buzz-relay/src/mesh_boot.rs`).
- **Rollout gating:** Kubernetes readiness/liveness/startup probes
  (`deploy/charts/buzz/templates/deployment.yaml`, backed by the relay's health-only
  router on a separate port from the app router and mesh traffic) gate whether a pod
  receives traffic during a rolling deploy; `deploy/local/build-and-deploy.sh` probes
  `/_readiness` on every pod individually after rollout, not just the Deployment's
  aggregate ready-replica count, because the aggregate can read "ready" while an
  individual pod is still failing.
- **Wire-version skew during a rolling deploy:** the mesh ALPN is versioned
  (`crates/buzz-relay-mesh/src/wire.rs`) so an old and a new pod version never
  half-speak the mesh protocol to each other; an unknown wire version is rejected
  loudly and counted rather than guessed at.
- **Redis unavailability:** since Redis is both the `buzz-pubsub` fan-out path and (when
  mesh is enabled) the session-ownership arbiter, and the chart refuses to install a
  multi-replica release without a configured Redis source, a production multi-relay
  deployment has no supported degraded mode that keeps multi-replica behavior without
  Redis — this is a hard dependency, not a soft one, at install time.

## Deployment Automation and Configuration as Authority

- `deploy/charts/buzz/values.yaml` — canonical topology knobs: `replicaCount`,
  `autoscaling.*`, `postgresql`/`externalPostgresql`, `redis`/`externalRedis`,
  `minio`, `persistence.git`, `pairingRelay.*`, `relay.extraEnv` (the mechanism for
  setting `BUZZ_MESH` and `BUZZ_MESH_BIND_ADDR`).
- `deploy/charts/buzz/templates/_validate.tpl` — the install-time Redis-for-replicas
  guard.
- `deploy/local/quickstart-ha-values.yaml` and `deploy/local/build-and-deploy.sh` — the
  local docker-desktop HA testbed: 3-replica quickstart profile, per-pod `emptyDir` git
  scratch, per-pod `/_readiness` verification after rollout.
- `crates/buzz-relay-mesh/src/wire.rs` — the frozen mesh wire contract (frame shapes,
  fencing law); changes here are documented in-crate as requiring cross-team
  coordination before the edit, since multiple relay-side consumers compile against
  these frame layouts.
- `crates/buzz-relay/src/config.rs` and `crates/buzz-relay/src/mesh_boot.rs` — how
  `BUZZ_MESH`/`BUZZ_MESH_BIND_ADDR`/`BUZZ_MESH_DEMO_ECHO` are resolved and how mesh
  startup/shutdown is sequenced.
- `crates/buzz-relay/src/tunnel/directory.rs` — the Redis-backed fenced session
  directory (Lua scripts for lease acquire/renew/release).

This document links these sources as authority rather than restating their content;
where a claim above depends on exact field names, defaults, or script bodies, the
cited path is the source of truth and this document does not attempt to stay
byte-for-byte synchronized with it.

## What Was Not Verified

No claim in this document was checked against a live multi-replica or mesh-enabled
deployment in this session — verification here is static (reading the chart, the
crate, and the local-testbed script), not a run of
`deploy/local/build-and-deploy.sh` against a real cluster. The Istio sidecar-exclusion
claim is recorded as INFERENCE for that reason. Whether any production
(non-`quickstart`) deployment of this chart currently runs with `BUZZ_MESH=on` was not
determined from this repository alone and is not claimed either way.
