---
id: layers-compute-liveness
type: layers
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - operator
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5."
    entry_class: FACT
    evidence:
      - "commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
  - statement: "docs/remote-agents.md, the formal specification for remote agent management, states as a defining property of its remote lifecycle model that 'the desktop holds no management channel to the remote process. Relay presence is the sole status signal; shutdown is a relay message; liveness bounds are enforced by the agent harness itself, not by the desktop.'"
    entry_class: FACT
    evidence:
      - "docs/remote-agents.md:17-21"
  - statement: "docs/remote-agents.md's design axiom (M1), 'No management channel', states the desktop-to-provider protocol contains 'no substrate API: no status query, no exec, no log fetch, no kill', and that all post-deploy observation flows through the relay: 'status is relay presence (kind:20001), stop is a relay message (!shutdown)'."
    entry_class: FACT
    evidence:
      - "docs/remote-agents.md:92-97"
  - statement: "docs/remote-agents.md's invariant (I3), 'Presence is the status', states that the desktop derives a remote agent's live state exclusively from relay presence events self-signed by the agent key -- online/away/offline, kind:20001, ephemeral, WS-published -- and that the deployment axis (deployed/not_deployed, derived from the stored backend_agent_id) is 'bookkeeping, not liveness'."
    entry_class: FACT
    evidence:
      - "docs/remote-agents.md:200-204"
  - statement: "The same invariant states the staleness bound on that presence signal is 180 seconds (PRESENCE_TTL_SECS, cited there as buzz-pubsub/src/presence.rs:16), frames it as the accepted cost of M1, and attributes the 90s-to-180s change to '#3783' raising it 'to keep a three-heartbeat expiry window after the desktop heartbeat moved to 60s' -- a claim about what the spec document itself states, not independently confirmed issue history (see this node's own scope-and-omissions)."
    entry_class: FACT
    evidence:
      - "docs/remote-agents.md:204-212"
  - statement: "docs/remote-agents.md's Scope and Non-Goals section explicitly excludes 'Liveness of the substrate' from the specification -- that a pod schedules, that an image pulls, that a cluster is reachable -- calling it 'empirical, not formal', and states the protocol specifies only how such substrate failures are reported (structured error, redacted, fail-closed)."
    entry_class: FACT
    evidence:
      - "docs/remote-agents.md:64-67"
  - statement: "docs/remote-agents.md's Launchers section states the agent/harness contract -- which includes presence publication (I3) -- 'binds every launcher', naming a bash script that exports the harness environment and execs buzz-acp as a conforming launcher at that layer 'today, with no code change', while the provider/deployer contract (the two operations, the reconciliation loop, at-most-one-live-instance) binds provider-managed launches only, and binding policy (fingerprints, restart-policy, idle bound) is decided per substrate."
    entry_class: FACT
    evidence:
      - "docs/remote-agents.md:115-149"
  - statement: "crates/buzz-pubsub/src/presence.rs defines PRESENCE_TTL_SECS as 180 and documents it as '3x the 60s heartbeat interval -- single missed heartbeat won't cause presence flap', storing presence as a Redis key (buzz:{community}:presence:{pubkey_hex}) set with that TTL via set_presence, deleted immediately on clean disconnect per the module's own doc comment."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/presence.rs:1-6"
      - "crates/buzz-pubsub/src/presence.rs:16"
  - statement: "crates/buzz-core/src/kind.rs defines KIND_PRESENCE_UPDATE as event kind 20001 and comments it 'Ephemeral: user presence update (online/away/offline)'."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs:462-463"
  - statement: "crates/buzz-acp/src/lib.rs implements the harness side of presence: publish_presence signs a kind:20001 event and sends it over the relay WebSocket connection specifically because ephemeral kinds (20000-29999) are rejected by the HTTP bridge; when config.presence_enabled the harness publishes 'online' once at startup, republishes 'online' on a 60-second interval timer (Duration::from_secs(60)) for as long as the process runs, and best-effort publishes 'offline' during its shutdown path before exiting."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/lib.rs:69-90"
      - "crates/buzz-acp/src/lib.rs:2157-2160"
      - "crates/buzz-acp/src/lib.rs:2230-2238"
      - "crates/buzz-acp/src/lib.rs:3513-3527"
  - statement: "crates/buzz-backend-kubernetes/src/wire.rs's Request enum, the desktop-to-provider wire contract for this binding, has exactly two variants -- Info and Deploy -- and its own test asserts that an unrecognized op such as 'undeploy' fails to deserialize; the provider protocol carries no status, liveness, or query operation."
    entry_class: FACT
    evidence:
      - "crates/buzz-backend-kubernetes/src/wire.rs:13-26"
      - "crates/buzz-backend-kubernetes/src/wire.rs:171"
  - statement: "desktop/src-tauri/src/managed_agents/reserved_env_keys.rs lists BUZZ_ACP_NO_PRESENCE inside RESERVED_ENV_KEYS -- the desktop-enforced set of environment keys a user-supplied override cannot touch -- under the comment 'Remote lifetime/presence policy: user env must not disable the desktop/provider-owned bounds while the saved record still promises them.'"
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/managed_agents/reserved_env_keys.rs:58-65"
  - statement: "desktop/src/features/channels/ui/useChannelAgentSessions.ts derives a remote agent's rendered session status as 'stopped' when the relay-observed status is 'offline' and 'deployed' otherwise -- one concrete call site combining the provider's deployment bookkeeping with the relay-derived presence signal into a single UI status, illustrating I3's stated distinction between the two axes rather than collapsing them."
    entry_class: FACT
    evidence:
      - "desktop/src/features/channels/ui/useChannelAgentSessions.ts:51"
  - statement: "crates/buzz-test-client/tests/conformance_multitenant.rs's pubsub_presence_typing module publishes a kind:20001 event and queries it back through the REST POST /query bridge (publish_presence, query_presence), and its fanout_and_presence_do_not_cross_communities test exercises that path as a real, running integration test -- direct verification that presence functions as an observable, queryable signal, though this test's own assertions are about tenant isolation, not the TTL/staleness bound in isolation."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/conformance_multitenant.rs:2361-2367"
      - "crates/buzz-test-client/tests/conformance_multitenant.rs:2373-2379"
      - "crates/buzz-test-client/tests/conformance_multitenant.rs:2514-2516"
  - statement: "crates/buzz-relay/src/router.rs registers /_liveness and /_readiness routes on the relay's own health-only router; liveness_handler unconditionally returns 200 OK, while readiness_handler checks a shutdown flag and reports Postgres/Redis connectivity -- a Kubernetes-style container health-check surface for the relay process itself."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs:69-70"
      - "crates/buzz-relay/src/router.rs:370-385"
  - statement: "deploy/charts/buzz/values.yaml wires the relay Helm deployment's livenessProbe and readinessProbe to httpGet paths /_liveness and /_readiness on the health port, with initialDelaySeconds/periodSeconds/timeoutSeconds settings distinct from and unrelated to PRESENCE_TTL_SECS."
    entry_class: FACT
    evidence:
      - "deploy/charts/buzz/values.yaml:141-155"
  - statement: "The relay's own /_liveness//_readiness HTTP probes are a structurally distinct mechanism from the compute-provider agent liveness this node documents: one is a Kubernetes container health probe answering 'is the relay process itself alive and connected to its datastores', the other is a Nostr presence event answering 'is a specific agent's compute instance still running' -- both happen to use the English word 'liveness' for different questions, at different layers, with no shared code path between them."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay/src/router.rs:69-70"
      - "docs/remote-agents.md:200-226"
    confidence: 0.9
  - statement: "crates/buzz-backend-kubernetes/src/observe.rs's decode_startup classifies a pod's container state into Started/Terminated/NeverStartedProvablyBroken/NeverStartedPullFailing/NeverStartedRecoverable as part of the spec's Deploy State Machine, answering whether a deploy has reached a running state -- a question distinct from, and prior to, whether an already-started agent is still alive right now, which is the question this node's subject (I3, relay presence) answers instead."
    entry_class: FACT
    evidence:
      - "crates/buzz-backend-kubernetes/src/observe.rs:69-119"
  - statement: "docs/remote-agents.md's invariant (I5), 'Intentional termination is final', describes the inactivity-bound self-stop as 'the harness's opt-in self-stop (§Auto-Stop, default disabled)' and states that restart policy follows lifetime policy (dying on purpose is final; dying by accident may restart) -- a termination-and-restart-supervision concern distinct from the liveness-detection question this node documents."
    entry_class: FACT
    evidence:
      - "docs/remote-agents.md:243-303"
  - statement: "At the recorded revision, git ls-tree of origin/launchpad's launchpad/docs/corpus tree contains no layers/ directory at all, so none of this Feature's sibling compute-layer or observability-layer nodes (backend-provider #1041, kubernetes-provider #1042, lifecycle #1043, local-agent-compute #1045, mesh-compute #1046, observability/liveness #1138) exist yet as mergeable relationship targets."
    entry_class: FACT
    evidence:
      - "git_ls_tree(origin/launchpad, launchpad/docs/corpus) -> AGENTS.md, README.md, architecture/**, schema/**, standards/**, templates/**; no layers/ directory present"
  - statement: "Issues #1041 (task: document layers/compute/backend-provider.md), #1042 (kubernetes-provider.md), #1043 (lifecycle.md), #1045 (local-agent-compute.md) and #1046 (mesh-compute.md) are filed as open sibling tasks under this node's own parent Feature (#611), so the boundaries this node draws against the general provider protocol, the Kubernetes binding, start/stop/auto-stop lifecycle policy, local-only compute and mesh/shared compute name real filed issues rather than hypothetical future ones."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "gh issue view 1041/1042/1043/1045/1046 --repo launchpad-26/buzz, run directly while authoring this node"
  - statement: "Issue #1138 (task: document layers/observability/liveness.md) is filed as an open sibling task under the same parent Feature (#611); at the time this node was written its own issue body carried no scope detail beyond the target file path (the same boilerplate Objective sentence as this node's own issue, #1044), so the boundary this node draws against it -- naming the relay's /_liveness//_readiness probes as the likely subject -- is this node's own reasoned placement, not something #1138 has itself stated."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "gh issue view 1138 --repo launchpad-26/buzz, run directly while authoring this node"
relationships:
  - type: references
    target: architecture-containers-agent-runtime
---

# Compute liveness

A running Buzz agent's compute instance is only ever known to be alive through
one channel: the relay presence event its own harness publishes. This node
defines that mechanism, the invariant behind it, and the boundary between it
and every other thing in this codebase that also happens to be called
"liveness."

## Definition

**Compute liveness** is the answer to one question — *is this specific
agent's running process still alive, right now* — and in Buzz that answer
comes exclusively from **relay presence**: a self-signed, ephemeral
`kind:20001` event (`online`/`away`/`offline`) that the `buzz-acp` harness
itself publishes over its relay WebSocket connection, once at startup, on a
60-second heartbeat while it runs, and best-effort as `offline` on its
shutdown path. The relay stores the most recent value with a 180-second TTL
(`PRESENCE_TTL_SECS`) and expires it if the harness stops publishing. This is
`docs/remote-agents.md`'s invariant **(I3) Presence is the status**, and its
defining consequence is architectural, not incidental: the desktop-to-provider
protocol carries **no substrate status query** at all (design axiom **M1**,
"No management channel") — a provider's wire contract has exactly two
operations, `info` and `deploy`, and nothing else. Whether an agent deployed
via a Kubernetes pod, ran as a hand-launched process, or runs as shared
compute inside the relay itself, the same presence mechanism is what answers
"is it alive" — the spec states this binds *every launcher*, not only
provider-managed ones.

**What compute liveness is not:**

- **Not the deployment bookkeeping axis.** A managed-agent record's
  `deployed`/`not_deployed` state (derived from a stored `backend_agent_id`)
  records whether a `deploy` call was made and accepted. It says nothing
  about whether the resulting process is still running a minute later — the
  spec calls this axis "bookkeeping, not liveness" in the same sentence it
  defines I3.
- **Not a substrate health check.** The desktop never asks Kubernetes (or any
  other substrate) directly whether an agent's pod or process is alive. That
  would require a management channel M1 deliberately does not provide.
- **Not the relay's own process health.** The relay exposes its own
  `/_liveness` and `/_readiness` HTTP probes, wired into its Kubernetes
  deployment's `livenessProbe`/`readinessProbe`. That answers "is the relay
  process itself alive and connected to Postgres/Redis" — a Kubernetes
  container health check for Buzz's own infrastructure, with no code path
  shared with agent presence. Both mechanisms are reasonably called
  "liveness"; they answer different questions about different processes at
  different layers. See *Scope and omissions* for how this boundary is drawn
  against the sibling document that most plausibly covers the relay's own
  probes.
- **Not deploy-startup classification.** Whether a just-deployed pod's
  container has reached a running state (as opposed to still pulling an
  image, or provably broken) is a separate, prior question the Kubernetes
  binding's deploy state machine answers before I3 becomes the operative
  signal at all.

## Visual aid

```mermaid
sequenceDiagram
    participant H as buzz-acp harness (on substrate)
    participant R as Relay
    participant D as Desktop

    H->>R: kind:20001 "online" (WS, at startup)
    loop every 60s while running
        H->>R: kind:20001 "online" (heartbeat)
    end
    R-->>R: SET presence key, EX 180s
    D->>R: observe presence (relay is the only channel)
    R-->>D: online / away / offline

    Note over H,R: Clean exit: H publishes "offline" before quitting.
    Note over R: Abnormal death (SIGKILL, node loss):<br/>no more heartbeats, key expires after up to 180s.
```

## Background

The 180-second bound is deliberate, not arbitrary: `docs/remote-agents.md`
frames it as "the accepted cost of M1" — trading a persistent management
channel (more moving parts, more failure modes, a second source of truth
about a remote process) for a bounded window in which presence can be wrong
after an abnormal death. The number itself is 3× the harness's 60-second
heartbeat interval, chosen so a single missed heartbeat does not flap
presence, and the spec attributes the earlier 90-second value's move to 180
seconds to keeping that same three-heartbeat margin after the desktop's own
heartbeat interval separately moved to 60 seconds. The presence-suppression
env var, `BUZZ_ACP_NO_PRESENCE`, is reserved (the desktop refuses to let user
config override it) specifically because disabling it on a remote deploy
would convert a bounded "wrong for at most 180s" into an unbounded "wrong
forever," since presence is the *only* signal remotely — locally the same
knob is comparatively harmless because the process and desktop UI are still
directly visible.

## Use cases

- **Implementing a new backend provider binding** (a new
  `buzz-backend-<id>` executable): understanding why the wire protocol never
  needs a status or health operation, and that shipping a provider that tries
  to add one is solving a problem the architecture already answers elsewhere.
- **Debugging an agent that the desktop shows as online/offline
  unexpectedly**: knowing the answer comes from a Redis-backed, 180-second-TTL
  presence key rather than any live check of the substrate narrows where to
  look — the harness's heartbeat loop and its connection to the relay, not
  Kubernetes pod status.
- **Reading desktop agent-status code**: recognizing the `deployed` vs.
  `offline`-derived-`stopped` pattern (see evidence ledger) as the concrete
  expression of I3's bookkeeping-vs-liveness distinction, rather than two
  redundant ways of saying the same thing.
- **Reasoning about worst-case detection delay**: after an abnormal death
  (node eviction, OOM, SIGKILL), the desktop can show a live-looking agent
  for up to 180 seconds — a number that matters for on-call expectations and
  for any automation that reacts to an agent going offline.

## Scope and omissions

**This document covers** the definition of compute liveness for a Buzz agent
instance — relay presence via `kind:20001`, the 60-second heartbeat and
180-second TTL staleness bound, the design axiom (M1) that makes presence the
*only* signal, and the boundary between this mechanism and the other things
in this codebase also called "liveness."

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The general provider protocol shape — discovery, `info`/`deploy` operations, payload schema, security obligations | #1041, `layers/compute/backend-provider.md` |
| The Kubernetes binding's realization of deploy, observe, and GC (Pod shape, Secrets, fencing, reconciliation) | #1042, `layers/compute/kubernetes-provider.md` |
| Start/stop/reap lifecycle policy: owner `!shutdown`, auto-stop/inactivity self-termination (I5), restart-policy-follows-intent | #1043, `layers/compute/lifecycle.md` |
| Local (non-remote, non-provider) agent compute specifics | #1045, `layers/compute/local-agent-compute.md` |
| Shared/mesh compute (relay-mesh agents, the `RELAY_MESH_PROVIDER` refusal in the Kubernetes binding) | #1046, `layers/compute/mesh-compute.md` |
| Process/service-level liveness of Buzz's own infrastructure containers — the relay's `/_liveness`/`/_readiness` HTTP probes and their Kubernetes wiring | #1138, `layers/observability/liveness.md` (scope not yet drafted at this node's recorded revision — see the evidence ledger entry naming this as this node's own reasoned placement) |
| The deploy state machine's startup classification (did a deploy reach `Started`) | touched only to distinguish it from liveness (evidence ledger); otherwise #1042's territory |

**No relationships to the sibling compute- or observability-layer nodes
above.** Checked before deciding that rather than assuming it: at the
recorded revision, `origin/launchpad`'s `launchpad/docs/corpus` tree carries
no `layers/` directory at all, so none of #1041/#1042/#1043/#1045/#1046/#1138
exist as mergeable targets. One relationship is declared instead, to a node
that does exist and whose subject is the actual enforcing mechanism:
`architecture-containers-agent-runtime` describes `buzz-acp`, the harness
that publishes the presence heartbeat this concept depends on.

**Expected but not verified when this node was written:**

- Whether issue `#3783` — cited by `docs/remote-agents.md` as the change
  that raised `PRESENCE_TTL_SECS` from 90s to 180s — is a
  `launchpad-26/buzz` issue or an upstream `block/buzz` issue was not
  independently checked. The claim above is recorded as what the spec
  document states, not as independently confirmed issue history.
- `#1138`'s actual scope was not established beyond its file path and open
  status. The boundary drawn against it here (the relay's `/_liveness`
  probes) is this node's own placement, to be revisited once #1138 lands.
- Whether the mesh/shared-compute substrate (#1046, an agent running "on the
  relay's own compute" per the `RELAY_MESH_PROVIDER` refusal comment)
  publishes presence identically to the Kubernetes and local paths, or has
  its own presence particulars, was not verified here — only that
  `docs/remote-agents.md`'s Launchers section states the presence-publishing
  contract binds every launcher at its lowest layer. #1046's own node should
  confirm or refine that for its specific substrate.
- The `fanout_and_presence_do_not_cross_communities` integration test
  confirms presence is published and queryable end-to-end, but it was not
  read in full and its assertions are about multi-tenant isolation, not
  about the 60s/180s timing values themselves; no test exercising the TTL
  expiry behavior directly was located during this node's authoring.
