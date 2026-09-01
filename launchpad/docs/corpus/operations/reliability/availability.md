---
id: operations-reliability-availability
type: operations
status: draft
origin: launchpad
audiences:
  - operator
  - developer
  - agent
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 473205a7457b208455f188847bfb27b01aa83cac."
    entry_class: FACT
    evidence:
      - "commit 473205a7457b208455f188847bfb27b01aa83cac"
  - statement: "The only in-repo deployment path that supports more than one relay replica is the Kubernetes Helm chart at deploy/charts/buzz; the Docker Compose bundle at deploy/compose is documented as a single-node/VPS deployment with exactly one relay process and no replica count at all."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/deployment/multi-relay.md"
      - "launchpad/docs/corpus/architecture/deployment/single-relay.md"
  - statement: "A chart-side template guard fails helm install/upgrade outright, before any resource is applied, when the resolved minimum replica count exceeds 1 and no Redis source (redis.enabled, externalRedis.url, or a secrets.existingSecret carrying REDIS_URL) is configured, because buzz-pubsub needs Redis to fan messages out across replicas; the chart's own README states this as a hard requirement with no silent degradation path."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/deployment/kubernetes.md"
      - "deploy/charts/buzz/README.md"
  - statement: "The readiness probe (GET /_readiness) first returns 503 immediately if the relay is mid-shutdown, and otherwise runs three checks concurrently under one shared 2-second timeout -- a Postgres ping, a Redis pool checkout, and a deletion-fence schema-shape assertion -- returning 200 only if all three pass and otherwise a 503 body naming exactly which check failed."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/layers/observability/readiness.md"
  - statement: "The liveness probe (GET /_liveness) is unconditional -- it takes no application state, performs no dependency check of any kind, and always returns 200 -- so a relay pod that has lost its Postgres or Redis connection, or that is mid-drain, is still reported alive; only readiness reacts to that condition by removing the pod from traffic, without restarting it."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/layers/observability/liveness.md"
  - statement: "Both probes are served twice: once on the main application router (sharing the app's traffic port) and once on a dedicated health-only router bound to a separate port, explicitly so that Kubernetes probe traffic bypasses the service mesh sidecar and the application's own auth middleware; the chart's startup probe targets /_liveness with a long failure threshold (up to 120 seconds) to tolerate slow process start before liveness/readiness take over for the rest of the pod's life."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/layers/observability/health-checks.md"
  - statement: "Readiness's Postgres check proves connectivity, not schema freshness: a pod running against an unmigrated schema can pass /_readiness and only fail once real traffic exercises the missing schema, a limitation the deployment-topology node states explicitly as a caveat on the readiness probe's guarantees rather than as a defect this node is introducing."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/deployment/kubernetes.md"
  - statement: "Kubernetes rolling updates on the relay Deployment use maxSurge 1 / maxUnavailable 0, so aggregate serving capacity never drops during a rollout; on SIGTERM the relay closes every live WebSocket with a 1012 Service Restart close frame, and an optional drainJitterMs setting spreads those closes over a random per-connection delay specifically to avoid a reconnect stampede against the shared database pool."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/deployment/kubernetes.md"
      - "launchpad/docs/corpus/layers/lifecycle/graceful-shutdown.md"
  - statement: "The relay's own documented worst-case shutdown budget is a fixed 5-second grace period (during which /_readiness already reports 503, giving Kubernetes time to stop routing new traffic) plus a hard 30-second drain backstop that force-exits the process if it fires, for a total of 35 seconds from signal to forced exit -- a budget the code comments state is sized to fit inside the chart's default 60-second terminationGracePeriodSeconds."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/layers/lifecycle/graceful-shutdown.md"
  - statement: "Both extra resilience controls the chart can render are opt-in and off by default: a PodDisruptionBudget renders only when podDisruptionBudget.enabled is true and the resolved minimum replica count exceeds 1, and the optional HorizontalPodAutoscaler scales on CPU and/or a custom active-WebSockets metric but needs a cluster Metrics Server (and, for the WebSocket metric, a custom-metrics adapter) that the chart does not itself install."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/deployment/kubernetes.md"
  - statement: "The chart's own huddleAudioAvailable helper template (buzz.huddleAudioAvailable in deploy/charts/buzz/templates/_helpers.tpl) resolves to false whenever the resolved minimum replica count exceeds 1 and the operator has not set an explicit override, because -- per the field's own doc comment in crates/buzz-relay/src/config.rs -- huddle audio frames are relayed peer-to-peer within a single pod today, and two peers in the same huddle landing on different pods under any-pod-any-connection horizontal scaling would silently never hear each other; the relay instead surfaces a clear, client-handleable \"huddle audio unavailable\" signal on join rather than shipping a silent split room."
    entry_class: FACT
    evidence:
      - "deploy/charts/buzz/templates/_helpers.tpl"
      - "crates/buzz-relay/src/config.rs"
  - statement: "The inter-relay QUIC mesh (crates/buzz-relay-mesh, gated by BUZZ_MESH) is opt-in -- an absent or non-'on' value is exact single-instance behavior, no UDP bind, no Redis registry write -- and, once enabled, each pod's ReadyRegistry publishes a signed mesh:ready:{runtime_id} record to Redis only after the relay's own readiness predicate (shutdown flag, Postgres, Redis) already passes; the record's own doc comment states registry membership is a routing hint only and 'never decide[s] session ownership or takeover.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-relay-mesh/src/registry.rs"
      - "launchpad/docs/corpus/architecture/deployment/multi-relay.md"
  - statement: "A ready-registry record expires from Redis on its own TTL (three times its refresh interval) if a pod crashes without deregistering, and is explicitly cleared by a clean shutdown; the actual arbiter of who currently owns a mesh-carried session (huddle audio, reliable-stream tunnels) is a separate Redis-backed fenced lease keyed by {session_id, generation, owner_runtime_id}, not the ready registry -- membership may say 'do not dial,' the fenced lease alone may say 'this pod owns it.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-relay-mesh/src/registry.rs"
      - "launchpad/docs/corpus/architecture/deployment/multi-relay.md"
  - statement: "The chart renders no Kubernetes Service-level session affinity for the relay at all: templates/service.yaml's spec sets only type (from service.type) plus the selector and the three named ports, with no sessionAffinity field anywhere in the file, so a Service fronting multiple relay pods gets Kubernetes's own default of no client-IP stickiness -- WebSocket clients are free to land on any ready pod on each new connection."
    entry_class: FACT
    evidence:
      - "deploy/charts/buzz/templates/service.yaml"
  - statement: "A live WebSocket connection is inherently pinned to whichever pod accepted it for the life of that TCP connection -- no load balancer rebalances an open connection mid-flight -- and Buzz's cross-pod message delivery does not depend on any additional stickiness beyond that: buzz-pubsub fans events out to every replica over Redis, so a message published on one pod reaches a client connected to any other pod without the Service needing to route repeat connections back to the same pod."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/architecture/deployment/multi-relay.md"
      - "deploy/charts/buzz/templates/service.yaml"
    confidence: 0.8
  - statement: "One specific HTTP surface is the documented exception to 'no stickiness is required': the relay's NIP-98 replay-defense seen-set that check_nip98_replay enforces before minting a token (workflow triggers, invite redemption, GIF proxy authorization, and other bridge.rs mint call sites) is scoped to one pod's own in-process AppState, so the chart's own shipped HA examples (replicaCount: 3 in deploy/charts/buzz/examples/argocd-app.yaml and examples/flux-helmrelease.yaml) are documented as non-conforming against that specific replay guarantee unless the operator adds either a header-stable sticky-routing rule at the ingress or a shared Redis-backed seen-set with atomic insert-if-absent and a TTL of at least the auth window; this is an HTTP-mint-path concern, not a property of the interactive WebSocket connection itself."
    entry_class: FACT
    evidence:
      - "docs/multi-tenant-relay.md"
  - statement: "An unreachable Postgres or a failed schema migration is fatal at relay startup: main.rs propagates the migration error with '?' before any listener is bound, so the process never serves traffic in a degraded state -- it either starts fully migrated and reachable, or it does not start at all."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/deployment/single-relay.md"
  - statement: "No availability service-level objective, uptime target, or error-budget commitment for the relay was found anywhere in this repository: a case-insensitive search for SLA/SLO/uptime-target/availability-target/99.9-style language across every Markdown, Rust, and YAML file returned no hit that names an availability commitment for buzz-relay itself -- the closest matches concern an unrelated agent-compute-provider startup-timing question (docs/remote-agents.md), a Kubernetes patch-SLA for OS packages in this fork's own (unused-in-production) hardening spec, and a research note listing 'HA/multi-AZ' as explicitly safe to relax in dev, none of which state a target for the relay's own availability."
    entry_class: INFERENCE
    evidence:
      - "grep_no_availability_target(pattern='SLA|SLO|uptime (target|commitment)|availability (target|commitment)|99\\.9', scope='repository-wide, case-insensitive') -> matches only docs/remote-agents.md:1752 (unrelated compute-provider startup timing), launchpad/deploy/runbooks/hardening-spec.md:625 and launchpad/deploy/archived/runbooks/hardening-spec.md:747 (OS patch SLA, not availability), launchpad/Research/hardening-linux-servers-gap-analysis.md:462 (HA/multi-AZ named as 'safe to relax in dev'); no hit names an availability/uptime commitment for buzz-relay"
      - "docs/remote-agents.md"
      - "launchpad/deploy/runbooks/hardening-spec.md"
      - "launchpad/Research/hardening-linux-servers-gap-analysis.md"
    confidence: 0.85
  - statement: "Issue #1214's definition of done requires this node to be structured for lookup rather than narrative teaching, to contain only facts supported by current source with generated versus authored values labeled, to define scope and omissions so a reader knows what the reference covers, and to link authoritative source/schema/config rather than duplicate it."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1214 definition of done"
  - statement: "This node was written using launchpad/docs/corpus/templates/reference.md, which was already merged on origin/launchpad at the recorded revision and directs a reference-shaped node toward a reference-description paragraph, a structured-entries table (one row per fact, ordered to match the subject's own order rather than alphabetically), an optional Commands section, an explicit boundary statement against the concept/explanation and procedure/how-to neighbors, relationships guidance, and a scope-and-omissions section."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/templates/reference.md"
relationships:
  - type: references
    target: architecture-deployment-kubernetes
  - type: references
    target: architecture-deployment-single-relay
  - type: references
    target: architecture-deployment-multi-relay
  - type: references
    target: layers-observability-readiness
  - type: references
    target: layers-observability-liveness
  - type: references
    target: layers-observability-health-checks
  - type: references
    target: layers-lifecycle-graceful-shutdown
---

# Availability: reference

What availability this system actually offers today -- not what a generic
production Kubernetes deployment could in principle offer, but what
`buzz-relay`'s own code and the chart that deploys it actually enforce, leave
optional, or do not implement at all. It catalogues replica/scaling
constraints, probe semantics, dependency coupling, rolling-update behavior,
mesh/session mechanics, and the presence or absence of a stated availability
target, each row pointing at the corpus node or source that carries the full
depth rather than restating it here. A reader arriving from
`architecture-deployment-kubernetes` (the topology this reference synthesizes
an availability view across) or from an operator's own on-call rotation is
this node's intended entry points.

## Availability envelope

Ordered by where a reader would encounter each concern going from "how many
copies of the relay can run" down to "is there a target for any of this at
all" -- not alphabetically.

| Dimension | What is actually enforced | Authoritative source |
|---|---|---|
| Replica topology | Single relay process only via the Docker Compose bundle (`deploy/compose`); more than one replica is possible only via the Kubernetes Helm chart (`deploy/charts/buzz`), scaled by a fixed `replicaCount` or an `HorizontalPodAutoscaler` | `architecture-deployment-single-relay`, `architecture-deployment-multi-relay` |
| Redis dependency at scale | Hard-required once the resolved minimum replica count exceeds 1; `helm install`/`upgrade` fails at template-render time (not at runtime) if no Redis source is configured -- `buzz-pubsub` fan-out has no supported degraded mode without it | `architecture-deployment-kubernetes` |
| Readiness (`GET /_readiness`) | 503 immediately if shutting down; otherwise Postgres ping + Redis checkout + deletion-fence schema check, concurrently, under a shared 2s timeout; 200 only if all three pass, else 503 naming which failed | `layers-observability-readiness` |
| Liveness (`GET /_liveness`) | Unconditional 200 -- no dependency check of any kind; a pod with a dead Postgres/Redis connection is still "alive," only not "ready" | `layers-observability-liveness` |
| Health-only listener | `/_liveness` and `/_readiness` served twice, once on a dedicated port with no auth/CORS/service-mesh sidecar interference, specifically so probe traffic never depends on the layers that gate real client traffic | `layers-observability-health-checks` |
| Readiness's real limit | Proves Postgres *connectivity*, not schema freshness -- an unmigrated pod can still pass `/_readiness` | `architecture-deployment-kubernetes` |
| Rolling updates | `maxSurge: 1`, `maxUnavailable: 0` -- capacity never drops during a deploy; SIGTERM triggers a `1012` close frame per WebSocket, optionally jittered to avoid a reconnect stampede | `architecture-deployment-kubernetes`, `layers-lifecycle-graceful-shutdown` |
| Graceful-shutdown budget | 5s grace (readiness already failing) + 30s hard drain backstop = 35s worst case, documented to fit inside the chart's default 60s `terminationGracePeriodSeconds` | `layers-lifecycle-graceful-shutdown` |
| Disruption/scaling controls | `PodDisruptionBudget` and the `HorizontalPodAutoscaler` both opt-in and off by default; the HPA needs a cluster Metrics Server (and, for the WebSocket metric, a custom-metrics adapter) the chart does not install | `architecture-deployment-kubernetes` |
| Huddle (voice) audio under scale-out | Automatically defaults to unavailable once minimum replicas exceed 1 (chart's `buzz.huddleAudioAvailable` helper), because audio frames are relayed in-process, per-pod, today; the relay surfaces a clear "unavailable" signal rather than a silent split room | `deploy/charts/buzz/templates/_helpers.tpl`, `crates/buzz-relay/src/config.rs` (no corpus node yet -- see *Boundary*) |
| Inter-relay mesh | Opt-in (`BUZZ_MESH`); off by default is exact single-instance behavior. When on, a Redis-backed ready registry (`mesh:ready:{runtime_id}`) publishes only after the pod's own readiness predicate already passes, and is a *bootstrap/routing hint only* | `crates/buzz-relay-mesh/src/registry.rs`, `architecture-deployment-multi-relay` |
| Session ownership (mesh-carried traffic) | Arbitrated by a separate Redis-backed fenced lease (`{session_id, generation, owner_runtime_id}`), not the ready registry -- membership says "don't dial," the lease alone says "this pod owns it" | `crates/buzz-relay-mesh/src/registry.rs`, `architecture-deployment-multi-relay` |
| WebSocket session affinity at the Service | None rendered -- no `sessionAffinity` field anywhere in `templates/service.yaml`; a live connection stays on its pod for its own lifetime purely because it is one open TCP connection, and cross-pod message fan-out runs through Redis rather than requiring the Service to route repeat connections back to the same pod | `deploy/charts/buzz/templates/service.yaml` |
| HTTP auth-replay stickiness (the one real exception) | The NIP-98 mint replay guard (`check_nip98_replay`) is per-pod in-process state; the chart's own shipped `replicaCount: 3` HA examples are documented as non-conforming against that specific guarantee unless the operator adds sticky HTTP routing or a shared Redis seen-set | `docs/multi-tenant-relay.md` §Conformance (P3) |
| Startup/migration failure | An unreachable Postgres or a failed migration is fatal before any listener binds -- fails fast, never serves in a degraded state | `architecture-deployment-single-relay` |
| Availability SLO/SLA | **None exists.** No file in this repository states an uptime target, an error budget, or an SLA for `buzz-relay` -- see the evidence ledger's repository-wide search entry above | Not defined anywhere in this repository |

## Boundary

This node does not describe:

- **Why any of the above was designed this way**, or the tradeoffs weighed in
  choosing an opt-in mesh over sticky routing, for example -- that is a
  concept/explanation node's territory, and none exists yet for this subject.
- **How to actually deploy, configure, or operate a highly-available relay
  step by step** -- the individual topology and probe nodes cited above, and
  the chart's own `README.md`, are the how-to/reference material for that; this
  node is a cross-cutting map of the availability picture across them, not a
  runbook.
- **Per-dependency failure-mode detail** -- what happens to a request already
  in flight when Postgres, Redis, or object storage specifically degrades or
  disappears mid-operation. That is the subject of sibling tasks in this same
  corpus batch (`operations/reliability/database-failure.md`,
  `redis-failure.md`, and `object-storage-failure.md`), none of which are
  merged at the recorded revision. This node's dependency-coupling coverage is
  limited to what the readiness probe observes and what the chart's install-time
  guard enforces, not what a live request does under each dependency's specific
  failure.
- **Disaster recovery** -- backup/restore procedures, cross-region failover, or
  data-loss scenarios, which are `operations/reliability/disaster-recovery.md`'s
  subject, a sibling task in this same batch and not merged at the recorded
  revision.
- **The full graceful-shutdown sequence as an operational runbook** -- this
  node cites `layers-lifecycle-graceful-shutdown` for the code-level mechanism
  (already merged), but an operations-facing runbook for graceful shutdown is
  `operations/reliability/graceful-shutdown.md`, a distinct, not-yet-merged
  sibling task in this same batch; the two are not the same document and this
  node does not anticipate the sibling's content.
- **An API Reference's depth.** This is a plain Reference article (Good Docs
  Project's own audience split) for an operator or developer trying to
  understand the availability picture, not an exhaustive parameter-by-parameter
  API surface for every chart value or handler involved.

## Relationships

- `references` → `architecture-deployment-kubernetes` -- the deployment
  topology this reference synthesizes an availability view across (replica
  scaling, Redis dependency, rolling-update strategy, PDB/HPA opt-in-ness).
- `references` → `architecture-deployment-single-relay` -- the non-HA topology
  this reference contrasts against, and the source for the startup/migration
  fatal-failure claim.
- `references` → `architecture-deployment-multi-relay` -- the source for the
  mesh, ready-registry, and fenced-session-lease claims this reference
  summarizes into single table rows.
- `references` → `layers-observability-readiness` -- the full depth behind this
  reference's readiness-probe row.
- `references` → `layers-observability-liveness` -- the full depth behind this
  reference's liveness-probe row.
- `references` → `layers-observability-health-checks` -- the full depth behind
  this reference's health-only-listener row.
- `references` → `layers-lifecycle-graceful-shutdown` -- the full depth behind
  this reference's graceful-shutdown-budget row.

All seven targets were confirmed present on `origin/launchpad` at the recorded
revision (they are listed in this batch's own known-existing-node-ids
inventory), so none of them is a sibling task from this same batch -- the
`operations/reliability/*` siblings named in *Boundary* above are deliberately
not targeted, because none of their node ids exist on `origin/launchpad` yet
and declaring an edge to one would validate in this worktree while becoming a
hard CI failure the moment this node merges ahead of them.

## Scope and omissions

**This node covers** the cross-cutting availability picture for `buzz-relay`:
replica/scaling constraints the chart and code enforce, the readiness/liveness
probe semantics and what each gates, dependency coupling as the readiness
probe and the chart's install-time guard express it, rolling-update and
graceful-shutdown behavior and their documented timing budgets, the opt-in
inter-relay mesh's ready registry and session-ownership arbitration, the
absence of load-balancer-level session affinity and the one documented HTTP
exception to that (NIP-98 mint replay stickiness), and the fact that no
availability SLO/SLA is defined anywhere in this repository.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Why the design chose an opt-in mesh over mandatory sticky routing, or any other design-rationale discussion | No concept/explanation node exists yet for this subject |
| Step-by-step deployment/operation instructions | The chart's own `README.md`, and the individual topology nodes cited above |
| Per-dependency failure-mode behavior (Postgres/Redis/object-storage degradation) | `operations/reliability/database-failure.md`, `redis-failure.md`, `object-storage-failure.md` -- sibling tasks in this batch, unmerged at the recorded revision |
| Disaster recovery, backup/restore, cross-region failover | `operations/reliability/disaster-recovery.md` -- sibling task in this batch, unmerged at the recorded revision |
| An operations-facing graceful-shutdown runbook | `operations/reliability/graceful-shutdown.md` -- sibling task in this batch, unmerged at the recorded revision (distinct from the already-merged code-level `layers-lifecycle-graceful-shutdown`) |
| The chart's full values schema and every field it exposes | `deploy/charts/buzz/values.yaml`, `values.schema.json` |
| Mesh compute (MeshLLM shared LLM inference) -- an unrelated subsystem that also uses the word "mesh" | `layers-compute-mesh-compute`; not the inter-relay QUIC mesh this node discusses |

**Expected but not verified when this node was written:**

- **No live multi-replica or mesh-enabled deployment was exercised.** Every
  claim above about replica scaling, the ready registry, and session leasing
  is read from the chart, the crate, and already-merged corpus nodes that
  themselves disclose the same limitation -- not observed against a running
  cluster.
- **Whether Buzz's WebSocket reconnect logic (client-side) ever depends on
  landing on the same pod it was previously connected to** was not checked
  from the client side (desktop/mobile) -- only the server-side absence of
  `sessionAffinity` and the Redis-backed fan-out path were verified. If a
  client-side assumption of pod continuity exists, it would change the
  "no stickiness required" claim above from a repository-wide fact to a
  server-side-only one.
- **Whether any production (non-quickstart) deployment of this chart
  currently runs with `BUZZ_MESH=on`, or with `replicaCount` greater than 1
  at all, was not determined from this repository alone** -- the same gap
  `architecture-deployment-multi-relay` and `architecture-deployment-kubernetes`
  both already disclose for their own claims.
- **Whether the repository-wide SLA/SLO search above missed a target phrased
  in a way the chosen pattern did not anticipate** (for example, a numeric
  target stated without the words "SLA," "SLO," "uptime," or "availability")
  was not independently re-checked with a second, differently-worded search.
