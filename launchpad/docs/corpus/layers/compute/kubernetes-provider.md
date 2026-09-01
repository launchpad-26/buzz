---
id: layers-compute-kubernetes-provider
type: layers
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - operator
evidence:
  - statement: "This node was authored and checked against repository revision 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5."
    entry_class: FACT
    evidence:
      - "commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
  - statement: "buzz-backend-kubernetes is a Rust crate whose Cargo.toml describes it as the 'Kubernetes backend provider for Buzz remote agents (docs/remote-agents.md)', built as a single binary (src/main.rs) rather than a library."
    entry_class: FACT
    evidence:
      - "crates/buzz-backend-kubernetes/Cargo.toml"
  - statement: "docs/remote-agents.md is a formal specification, carrying the draft status marker directly under its title, for the protocol by which Buzz Desktop delegates execution of a managed agent to a remote substrate through a backend provider binary; it names buzz-backend-kubernetes as 'the first conforming provider ... which realizes the contract as a bare Pod running the sprig image.'"
    entry_class: FACT
    evidence:
      - "docs/remote-agents.md:1-24"
  - statement: "The provider protocol is a zero-registration plugin contract: the desktop discovers an executable named buzz-backend-<id>, and every operation is one process, one JSON request on stdin, one JSON response on stdout, exit code carrying exactly one bit."
    entry_class: FACT
    evidence:
      - "docs/remote-agents.md:305-377"
      - "crates/buzz-backend-kubernetes/src/main.rs"
  - statement: "The crate implements exactly two operations, Info and Deploy, dispatched from a tagged Request enum parsed from the raw JSON request; PROTOCOL_VERSION is a constant equal to 1, matching the spec's stated wire-contract version."
    entry_class: FACT
    evidence:
      - "crates/buzz-backend-kubernetes/src/wire.rs:10-26"
      - "docs/remote-agents.md:387-415"
  - statement: "deploy_agent parses provider_config, derives the agent's identity by parsing private_key_nsec before any cluster contact, connects a kube-rs client, and calls reconcile::deploy — matching the spec's Deploy State Machine's Step 0 requirement to derive and verify identity before any substrate read or mutation."
    entry_class: FACT
    evidence:
      - "crates/buzz-backend-kubernetes/src/main.rs:116-135"
      - "docs/remote-agents.md:649-653"
  - statement: "The main.rs module doc states the exit-code contract explicitly: 'The exit code carries exactly one bit — 0 for a response that was produced, 1 for a failure to produce one,' with in-band {\"ok\": false, \"error\": ...} carrying the actual failure detail rather than a second, redundant error channel."
    entry_class: FACT
    evidence:
      - "crates/buzz-backend-kubernetes/src/main.rs:1-9"
      - "docs/remote-agents.md:370-372"
  - statement: "The crate refuses to deploy an agent whose wire-level agent.provider field equals \"relay-mesh\" (after trimming), before parsing the typed request, because a shared-compute (relay-mesh) agent runs on the relay's own compute and deploying it as a pod would create a second, contending consumer of the same agent identity; this refusal is asserted directly by three unit tests in main.rs (refuses_a_relay_mesh_agent, refuses_a_padded_relay_mesh_agent, does_not_refuse_a_normal_provider)."
    entry_class: FACT
    evidence:
      - "crates/buzz-backend-kubernetes/src/main.rs:28-32"
      - "crates/buzz-backend-kubernetes/src/main.rs:97-113"
      - "crates/buzz-backend-kubernetes/src/main.rs:150-181"
      - "docs/remote-agents.md:623-633"
  - statement: "provider_config accepts exactly nine v1 fields — context, namespace, image, cpu_request, memory_request, cpu_limit, memory_limit, inactivity_seconds, service_account — with namespace and image required; config.rs pins this exact field set with a dedicated test, schema_declares_exactly_the_nine_v1_fields, and no field name contains a credential-shaped word (secret|password|token|key|credential), also asserted by a dedicated test."
    entry_class: FACT
    evidence:
      - "crates/buzz-backend-kubernetes/src/config.rs:192-243"
      - "crates/buzz-backend-kubernetes/src/config.rs:426-469"
      - "docs/remote-agents.md:1396-1401"
  - statement: "provider_config carries no cluster-credential field; config.rs's own doc comment states cluster auth comes from ambient kubeconfig resolution and nothing else, and a dedicated test (credential_fields_have_no_effect) asserts that arbitrary token/client_key fields sent in provider_config have no effect on the parsed struct."
    entry_class: FACT
    evidence:
      - "crates/buzz-backend-kubernetes/src/config.rs:1-7"
      - "crates/buzz-backend-kubernetes/src/config.rs:362-377"
  - statement: "config::parse refuses inactivity_seconds: 0 outright, returning an error naming both the field and the gating condition (OnFailure), rather than silently downgrading to a bounded lifetime; a dedicated test, refuses_indefinite_lifetime, asserts both the field name and the word OnFailure appear in the error."
    entry_class: FACT
    evidence:
      - "crates/buzz-backend-kubernetes/src/config.rs:148-166"
      - "crates/buzz-backend-kubernetes/src/config.rs:307-320"
  - statement: "The spec states that inactivity_seconds: 0 is a legal, blessed value meaning 'no inactivity bound' at the protocol level, but the Kubernetes binding's own restartPolicy: OnFailure for that case is gated on a harness exit-code contract not yet pinned by test (Known Defect 6) and a crash-loop classification row the deploy state machine does not yet have; until both land, the binding MUST refuse the combination rather than ship OnFailure against an undefended convention, which is exactly what config.rs implements."
    entry_class: FACT
    evidence:
      - "docs/remote-agents.md:1133-1150"
      - "crates/buzz-backend-kubernetes/src/config.rs:58-62"
  - statement: "The pod's hardening defaults set automountServiceAccountToken: false, runAsNonRoot: true, allowPrivilegeEscalation: false, restartPolicy: \"Never\" (RESTART_POLICY constant), and terminationGracePeriodSeconds: 60 (TERMINATION_GRACE_SECONDS constant), each also asserted by dedicated unit tests in pod.rs."
    entry_class: FACT
    evidence:
      - "crates/buzz-backend-kubernetes/src/pod.rs:132"
      - "crates/buzz-backend-kubernetes/src/pod.rs:154-164"
      - "crates/buzz-backend-kubernetes/src/pod.rs:238"
      - "crates/buzz-backend-kubernetes/src/pod.rs:244"
      - "crates/buzz-backend-kubernetes/src/pod.rs:257"
      - "crates/buzz-backend-kubernetes/src/pod.rs:287-295"
      - "crates/buzz-backend-kubernetes/src/pod.rs:402"
      - "crates/buzz-backend-kubernetes/src/config.rs:46-62"
  - statement: "The default terminationGracePeriodSeconds of 60 is stated in the spec as a declared budget the harness must honor, chosen because Kubernetes' own default of 30s would SIGKILL the harness mid-drain and leave relay presence stale-online for the avoidable part of the 180-second presence staleness window (I3)."
    entry_class: FACT
    evidence:
      - "docs/remote-agents.md:1208-1222"
  - statement: "The provider builds the pod entrypoint to exec the buzz-acp harness as PID 1 (never a wrapping shell without exec), because a PID-1 process with no signal trap never delivers SIGTERM to a child, which would void the 60-second grace period and the presence-staleness guarantee it exists to bound."
    entry_class: FACT
    evidence:
      - "docs/remote-agents.md:1051-1074"
  - statement: "The Kubernetes binding runs a reconciliation loop (reconcile::deploy, driven by decisions in classify.rs) rather than a plain create, converging any number of concurrent or sequential deploy calls for the same agent key toward at-most-one live instance per namespace (invariant I4); reconcile.rs's own module doc states this is the exact shipped code path exercised by the crate's conformance tests, not a test-only reimplementation."
    entry_class: FACT
    evidence:
      - "crates/buzz-backend-kubernetes/src/reconcile.rs:1-18"
      - "docs/remote-agents.md:228-241"
      - "docs/remote-agents.md:641-647"
  - statement: "Preflight garbage collection (gc.rs) runs on every deploy call, deleting terminated pods and their referenced Secrets and age-eligible orphan Secrets, gated on two checks named directly in the module doc: the full-pubkey annotation check and the management-marker label, so an unmarked or unannotated object is never deleted regardless of its other labels."
    entry_class: FACT
    evidence:
      - "crates/buzz-backend-kubernetes/src/gc.rs:1-9"
      - "docs/remote-agents.md:1294-1335"
  - statement: "The default agent image is ghcr.io/block/buzz-sprig, pinned by digest (not merely a tag) at compile time, and config::parse rejects a tag-only image reference; a dedicated test, image_is_required_and_must_be_digest_pinned, asserts both that image is required and that a :latest tag is rejected with an error naming 'digest-pinned'."
    entry_class: FACT
    evidence:
      - "crates/buzz-backend-kubernetes/src/config.rs:44"
      - "crates/buzz-backend-kubernetes/src/config.rs:337-344"
      - "docs/remote-agents.md:1019-1049"
  - statement: "The spec's own rationale for digest pinning over a mutable tag is that the pod object holding the pinned reference runs with an nsec (the agent's private key), so an operator who could silently move a tag underneath a running or future deploy is a live-key supply-chain risk the digest pin closes."
    entry_class: FACT
    evidence:
      - "docs/remote-agents.md:1035-1045"
  - statement: "docs/remote-agents.md explicitly names an alternative substrate binding as already real, not hypothetical: 'a different substrate (the systemd/SSH deployer of PR #3449 is the live example) conforms to layers 1-2 and writes its own layer 3,' distinguishing the provider/deployer contract (shared by any provider) from binding policy (Kubernetes-specific: fingerprints, fenced deletes, restart-policy selection)."
    entry_class: FACT
    evidence:
      - "docs/remote-agents.md:115-149"
  - statement: "docs/remote-agents.md states its own scope boundary directly: it defines management-plane behavior (how agents get to a substrate, how their state is observed, how their lifetime is bounded) and explicitly does not specify agent conversational behavior (governed by the buzz-acp harness and the NIPs it implements), malicious-provider containment, substrate security (Kubernetes RBAC, namespace isolation, secret encryption at rest are named as cluster-operator concerns), or substrate liveness."
    entry_class: FACT
    evidence:
      - "docs/remote-agents.md:45-67"
  - statement: "The existing corpus node architecture-deployment-kubernetes explicitly defers this subject to a future node, stating buzz-backend-kubernetes 'is a distinct compute-provisioning concern from the relay's own deployment topology documented in this node, so it is deliberately out of scope here rather than folded in' and 'belongs in its own node.'"
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/deployment/kubernetes.md"
  - statement: "The existing corpus node architecture-containers-agent-runtime already cites docs/remote-agents.md for the general provider-protocol contract and names buzz-backend-kubernetes as the first conforming provider, so this concept node's relationship to it is a references edge to a sibling that discusses the same source from the container/runtime angle, not a duplicate definition."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/containers/agent-runtime.md"
  - statement: "At the recorded revision the spec names a known desktop-side defect (Known Defect 3) in which the deploy payload bypasses the launch resolver, so the launch block's normative fields (per-runtime model/provider env, resolved agent_command/agent_args, owner_pubkey, spawn policy) may not always be fully populated by the desktop that calls this provider; this is a defect in the desktop's payload construction, not in the buzz-backend-kubernetes crate's own handling of a launch block it does receive."
    entry_class: FACT
    evidence:
      - "docs/remote-agents.md:1597-1620"
  - statement: "Both PR #3449 (the systemd/SSH deployer) and the launch-payload Known Defect 3 gap were read only as named in docs/remote-agents.md's own text at the recorded revision; the PR's own diff and the current state of the desktop's deploy_payload_json were not independently inspected for this node."
    entry_class: INFERENCE
    evidence:
      - "docs/remote-agents.md:115-149"
      - "docs/remote-agents.md:1597-1620"
    confidence: 0.7
relationships:
  - type: references
    target: architecture-deployment-kubernetes
  - type: references
    target: architecture-containers-agent-runtime
---

# Kubernetes provider (`buzz-backend-kubernetes`)

## Definition

The **Kubernetes provider** is `buzz-backend-kubernetes`, a standalone Rust
binary that implements Buzz's remote-agent **provider protocol**
(`docs/remote-agents.md`) for Kubernetes: given an agent's identity and
configuration from Buzz Desktop, it deploys that agent as a Kubernetes Pod
running the `sprig` container image, so the agent's `buzz-acp` harness
process runs on a remote cluster instead of the user's own machine. It is
one specific **backend provider** — a `buzz-backend-<id>` executable
conforming to a documented desktop↔provider contract — not the provider
protocol itself, and not the only possible one: the specification names a
second, real binding (a systemd/SSH deployer, PR #3449) that satisfies the
same protocol layers against a different substrate.

Concretely, the crate is a single binary (`crates/buzz-backend-kubernetes`)
invoked once per operation: it reads one JSON request from stdin — either
`{"op": "info"}` or `{"op": "deploy", ...}` — and writes exactly one JSON
response to stdout before exiting, with the exit code carrying only "a
response was produced" (0) or "it was not" (1). All actual outcomes,
success or failure, ride inside the JSON response, never inside the exit
code alone.

## Boundaries and non-goals

**Not the relay's own Kubernetes deployment.** A separate corpus node,
`architecture-deployment-kubernetes`, documents how the Buzz **relay**
itself is deployed to Kubernetes via its Helm chart. That is the relay's
own runtime topology (Deployment, Service, HPA, PodDisruptionBudget); this
node's subject is a different compute-provisioning concern — how an
**agent** gets a pod of its own — and that existing node names the
distinction explicitly and defers it here.

**Not agent conversational behavior.** What a deployed agent does with
events — tool calls, turns, model selection — is governed by the `buzz-acp`
harness and the Nostr NIPs it implements, unchanged by whether the harness
runs locally or in a pod deployed by this provider. This provider's job
ends at getting the harness process running with the right identity and
environment.

**Not malicious-provider containment or substrate security.** The
specification states both exclusions directly: a provider binary is handed
the agent's private key (`nsec`) by design, and the protocol only bounds
the desktop's *exposure* to a hostile provider (staged-binary execution,
output redaction, anti-secret config validation) — it cannot make a hostile
provider safe. Kubernetes RBAC, namespace isolation, and secret encryption
at rest are the cluster operator's responsibility, not this provider's; the
residual exposure it states plainly is that any principal with pod-exec or
Secret-read access in the target namespace can read the deployed agent's
`nsec`.

**Not a management channel back to the running agent.** After a successful
deploy, the desktop holds no persistent connection to the pod. Everything
the desktop subsequently knows about the agent — online, away, offline —
comes from Nostr relay presence events the agent itself publishes, not from
any Kubernetes API the provider protocol exposes. There is no `undeploy`
operation in the wire protocol; deleting the agent record from the desktop
does not delete its pod.

## Use cases

- **Running a managed agent off the user's own machine.** An owner who
  wants an agent to keep running without their laptop staying on, or wants
  compute isolated from their local environment, configures the agent's
  backend as `Provider { id: "kubernetes", config: {...} }` instead of
  `Local`; the desktop then calls this provider's `deploy` operation
  instead of spawning a local process.
- **Recovering from a stale or dead instance without manual cleanup.**
  Because `deploy` is a reconciliation loop rather than a plain create, an
  owner can press Start again after an agent was reaped (inactivity
  timeout) or accidentally evicted (node loss), and the provider observes
  the existing state and either no-ops against a live pod, replaces
  terminated residue, or creates fresh — converging toward exactly one live
  instance for that agent's key in that namespace, rather than requiring
  the owner to manually find and delete a stuck pod first.
- **Bounding compute cost for an idle agent.** The `inactivity_seconds`
  configuration field (default 7200 = two hours) lets an owner choose a
  self-stop bound so a pod that nobody is using does not run — and be
  billed for — indefinitely; the value `0` is a legal choice meaning "no
  bound," though the current implementation refuses it pending a harness
  exit-code contract prerequisite (see *Scope and omissions*).

## Comparison

| | Local spawn (no provider) | Kubernetes provider (this node) | systemd/SSH deployer (PR #3449) |
|---|---|---|---|
| Where the harness runs | Desktop's own machine | A Pod in a Kubernetes cluster | A remote host over SSH, under systemd |
| Management channel to the running process | Direct (desktop spawned it) | None — relay presence only | None — relay presence only |
| Conforms to | The agent/harness contract only | Agent/harness contract + provider/deployer contract + this binding's own policy | Agent/harness contract + provider/deployer contract + its own binding policy |
| Configuration secrecy | N/A (no `provider_config`) | `provider_config` carries no credentials (I2); cluster auth comes from ambient kubeconfig | Binding-specific; not documented by this node |

The Kubernetes provider and the systemd/SSH deployer share the same two
upper layers (the provider protocol's `info`/`deploy` operations and the
deploy reconciliation discipline); what differs between them is entirely
**binding policy** — how each substrate is authenticated to, what a
deployed unit looks like, and how each substrate's own state machine quirks
(Kubernetes pod phases and restart policies, in this binding's case) are
classified.

## Related resources

- [`docs/remote-agents.md`](../../../../../docs/remote-agents.md) — the full
  specification this node summarizes: the provider protocol wire format,
  the five stated invariants, the complete deploy state machine, and every
  Kubernetes-binding-specific policy decision (image pinning, pod hardening,
  Secret lifecycle, garbage collection). This node deliberately does not
  restate that detail — see *Scope and omissions*.
- `architecture-deployment-kubernetes` (`references`) — the sibling node
  documenting the relay's own Kubernetes deployment via its Helm chart, a
  distinct compute-provisioning concern this node does not cover.
- `architecture-containers-agent-runtime` (`references`) — the container-
  level architecture node that already names `buzz-backend-kubernetes` as
  the first conforming remote-agent provider and the `sprig` image it runs.

## Scope and omissions

**This document covers** what the Kubernetes provider is, the layered
contract it sits inside (agent/harness, provider/deployer, Kubernetes
binding policy), what it explicitly does and does not take responsibility
for, and when an owner would choose it. It intentionally does not restate:

| Not covered here | Where it lives |
|---|---|
| The full provider wire protocol (`info`/`deploy` request/response shapes, the `launch` data block's three-tier environment precedence) | `docs/remote-agents.md` §Provider Protocol, §Launch data |
| The seven-row deploy state machine in full (fingerprint divergence, 409 discrimination, conflict convergence) | `docs/remote-agents.md` §Deploy State Machine |
| Secret lifecycle and garbage collection mechanics | `docs/remote-agents.md` §K8s Secrets, §K8s GC |
| The relay's own Kubernetes deployment (Helm chart, HPA, PodDisruptionBudget) | `architecture-deployment-kubernetes` |
| Agent conversational behavior once running | the `buzz-acp` harness and the NIPs it implements (out of this node's scope by the spec's own Non-Goals) |

**Expected but not verified when this node was written:**

- **Whether the desktop's `deploy_payload_json` currently emits a complete
  `launch` block.** The specification itself names this as a known,
  desktop-side defect (Known Defect 3) at the revision it was written
  against; whether it has since been fixed was not checked, because doing
  so would require reading current desktop source outside this crate,
  which is a different corpus surface. If the `launch` block is still
  incomplete, agents deployed through this provider may not receive the
  per-runtime model/provider environment, resolved command/args, or owner
  pubkey that a local spawn of the same agent record would get.
- **Whether `restartPolicy: OnFailure` (the indefinite-lifetime path) has
  since shipped.** At the recorded revision, `config::parse` refuses
  `inactivity_seconds: 0` outright because the harness's clean-exit
  contract is not yet pinned by test and the reconciler's state machine
  lacks a crash-loop classification row; this was confirmed by reading the
  refusal and its test directly, but whether either prerequisite has since
  landed was not checked.
- **PR #3449's actual contents.** The systemd/SSH deployer is referenced
  only as the specification's own example of a second binding; its diff
  was not opened for this node.
- **Live cluster behavior.** No deploy was executed against a real or fake
  Kubernetes cluster while writing this node; every claim above rests on
  reading the crate's source and its inline unit tests, not on running the
  conformance test suite the reconciler's own module doc mentions.
