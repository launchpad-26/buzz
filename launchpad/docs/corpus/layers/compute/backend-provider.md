---
id: layers-compute-backend-provider
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
  - statement: "docs/remote-agents.md specifies the protocol by which Buzz Desktop delegates execution of a managed agent to a 'remote substrate' (any compute environment other than the local machine) through a 'backend provider binary,' and states the document's own status as draft directly under its title."
    entry_class: FACT
    evidence:
      - "docs/remote-agents.md:1-16"
  - statement: "A backend provider is any executable named buzz-backend-<id>: the desktop's discovery scan (discover_provider_candidates) walks the directory containing the desktop executable, every PATH entry and ~/.local/bin looking for files with that prefix, executes nothing during discovery, and derives the provider id by stripping the prefix (and, on Windows, a known executable extension)."
    entry_class: FACT
    evidence:
      - "docs/remote-agents.md:307-315"
      - "desktop/src-tauri/src/managed_agents/backend.rs:568-638"
  - statement: "An agent record's ManagedAgentRecord.backend field is a BackendKind enum with exactly two variants: Local (the default) or Provider { id: String, config: serde_json::Value } — the id names the discovered buzz-backend-<id> binary and config is the provider's persisted, schema-rendered settings object."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/managed_agents/types.rs:6-13"
      - "desktop/src-tauri/src/managed_agents/types.rs:319"
  - statement: "'Provider' is an overloaded name in this codebase and the two meanings sit on the same struct: ManagedAgentRecord.provider (Option<String>, doc-commented 'LLM inference provider' — e.g. an Anthropic/OpenAI-compatible model provider id) is a different field from ManagedAgentRecord.backend's Provider { id, config } variant (a backend/compute provider). Neither field is derived from the other."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/managed_agents/types.rs:287-295"
      - "desktop/src-tauri/src/managed_agents/types.rs:318-319"
  - statement: "The name collision is concrete on the wire, not just in the schema: buzz-backend-kubernetes (a backend provider) reads its deploy request's agent.provider field — the LLM-provider string — solely to refuse deploying an agent configured for the shared-compute 'relay-mesh' LLM provider, because that provider runs on the relay's own compute rather than in a pod this backend provider would create."
    entry_class: FACT
    evidence:
      - "crates/buzz-backend-kubernetes/src/main.rs:28-32"
      - "crates/buzz-backend-kubernetes/src/main.rs:97-113"
      - "crates/buzz-backend-kubernetes/src/main.rs:173-181"
  - statement: "resolve_provider_binary's own doc comment states it is 'the ONLY way to resolve provider binaries for execution': it validates the id against ^[a-z0-9][a-z0-9_-]*$, looks it up only among discover_provider_candidates()'s PATH-discovered results, and every deploy/start/create path must use it instead of raw command construction, to prevent a compromised frontend/IPC caller from steering execution to an arbitrary binary."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/managed_agents/backend.rs:640-677"
  - statement: "The provider protocol has exactly two operations, info and deploy, each one process per operation: the desktop writes one JSON request object to the provider's stdin and closes it; the provider writes one JSON response object to stdout and exits; a non-zero exit is treated as failure even when stdout parsed as valid JSON, because partial output from a crashed operation is never trusted."
    entry_class: FACT
    evidence:
      - "docs/remote-agents.md:361-376"
      - "docs/remote-agents.md:389-422"
      - "desktop/src-tauri/src/managed_agents/backend.rs:243-261"
  - statement: "Before any secret crosses the desktop-to-provider boundary, provider_deploy stages the resolved binary into a private, non-writable temp file while hashing the exact bytes copied, invokes info on that staged artifact and validates its declared protocol_version, then invokes deploy on the same staged bytes — closing the gap between 'the binary that answered info' and 'the binary that receives the nsec.'"
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/managed_agents/backend.rs:436-505"
      - "desktop/src-tauri/src/managed_agents/backend.rs:509-533"
      - "docs/remote-agents.md:334-359"
  - statement: "docs/remote-agents.md's own 'Known Defects (at 28ae6cd21)' section, whose citation pin states every file:line reference was verified against commit 28ae6cd21, lists as Known Defect 5 that 'the deploy path never checks protocol_version' and that the pre-secret negotiation gate 'is a design, not a description' at that commit."
    entry_class: FACT
    evidence:
      - "docs/remote-agents.md:1583-1585"
      - "docs/remote-agents.md:1631-1639"
  - statement: "At the current recorded revision, backend.rs's provider_deploy already implements exactly the resolve-once -> stage-and-digest -> info -> explicit-version-check -> deploy sequence Known Defect 5 calls for missing, so that defect entry is stale documentation drift rather than a description of current behavior; docs/remote-agents.md has not been re-pinned to reflect it."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/managed_agents/backend.rs:509-533"
      - "docs/remote-agents.md:1631-1639"
  - statement: "The staging-and-digest gate was added in commit 6530b58a6 ('feat(k8s): Kubernetes backend plugin + desktop deploy path'), which is a descendant of commit 28ae6cd21 (the commit docs/remote-agents.md's Known Defects section is pinned to) — so the fix postdates, and was never folded back into, the spec's defect list."
    entry_class: INFERENCE
    evidence:
      - "git_log(-S 'fn stage_provider', desktop/src-tauri/src/managed_agents/backend.rs) -> introduced in 6530b58a6"
      - "git_merge_base(--is-ancestor 28ae6cd21 6530b58a6) -> exit 0, confirming 28ae6cd21 is an ancestor of 6530b58a6"
    confidence: 0.85
  - statement: "The protocol states a design axiom (M1, 'No management channel'): after a successful deploy the desktop holds no persistent management session to the remote agent, and the desktop-provider protocol itself contains no substrate API (no status query, no exec, no log fetch, no kill) — all post-deploy observation and control flows through the relay (presence for status, a relay !shutdown message to stop, a future re-deploy to reconfigure)."
    entry_class: FACT
    evidence:
      - "docs/remote-agents.md:90-104"
  - statement: "The spec's Launchers section states the desktop is 'one launcher among many' and layers the obligations into three nested contracts: an agent/harness contract that binds every launcher (a bash script exporting the right env and exec'ing the harness conforms today with no code change); a provider/deployer contract that binds only provider-managed launches (the info/deploy operations, reconciliation, at-most-one-live-instance per deploy scope); and a binding policy that is specific to each substrate (e.g. the Kubernetes binding's fingerprinting and GC rules)."
    entry_class: FACT
    evidence:
      - "docs/remote-agents.md:115-149"
  - statement: "I2 ('No secrets in configuration') is enforced by validate_provider_config: provider_config must be a flat JSON object of scalar values, at most 20 fields and 64KB serialized, and any key whose word-split (splitting on separators and camelCase boundaries) contains secret, password, token, key or credential is rejected outright — a name-based lint the spec itself describes as having accepted false positives (e.g. ssh_key_path) in exchange for failing closed."
    entry_class: FACT
    evidence:
      - "docs/remote-agents.md:185-198"
      - "desktop/src-tauri/src/managed_agents/backend.rs:536-566"
  - statement: "docs/remote-agents.md names buzz-backend-kubernetes as 'the first conforming provider,' realizing the contract as a bare Kubernetes Pod running the sprig container image; the crate's own Cargo.toml description independently states the same thing: 'Kubernetes backend provider for Buzz remote agents (docs/remote-agents.md).'"
    entry_class: FACT
    evidence:
      - "docs/remote-agents.md:22-24"
      - "crates/buzz-backend-kubernetes/Cargo.toml:7"
  - statement: "The desktop exposes backend-provider discovery and config-schema probing to its frontend as two Tauri commands: discover_backend_providers (lists id/binary-path pairs from discover_provider_candidates) and probe_backend_provider, which re-validates that the requested binary path canonicalizes to one of the discovered candidates before invoking its info operation — closing the same 'arbitrary binary execution via a compromised frontend/IPC caller' gap resolve_provider_binary closes on the deploy path."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/commands/agent_providers.rs:1-46"
  - statement: "The already-merged corpus node architecture-containers-agent-runtime names 'a backend provider binary such as buzz-backend-kubernetes, which the Desktop hands the agent's private key to' as one of the agent-runtime container's directly connected containers/systems, and separately states that malicious-provider containment is explicitly out of scope for the protocol — a provider is handed the agent's nsec by design."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/containers/agent-runtime.md"
  - statement: "Issue #1041's definition of done requires this document to define the term in one sentence before deeper explanation, state boundaries/non-goals (what the concept must not be confused with), link related concepts/implementation/verification, and use examples only to clarify the concept rather than introduce a second one."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1041 definition of done"
relationships:
  - type: references
    target: architecture-containers-agent-runtime
---

# Concept: Backend provider

A **backend provider** is a small, discoverable executable — `buzz-backend-<id>`
— that gives Buzz Desktop a way to deploy a managed agent onto a compute
substrate other than the local machine, without the desktop having to know
anything about that substrate.

## Definition

A backend provider is any executable on the desktop's discovery path named
`buzz-backend-<id>` that speaks a small JSON request/response protocol on its
stdin/stdout: given an `info` request it describes itself and its
configuration schema, and given a `deploy` request (carrying the agent's
identity and configuration, including its private key) it stands the agent up
on whatever substrate it manages and returns a handle for that deployment.
Concretely, an agent record's `backend` field is a two-variant discriminator —
`Local` or `Provider { id, config }` — and choosing `Provider` is what makes
an agent "remote": the desktop delegates to the named provider binary rather
than spawning the agent harness itself.

**Boundary — what this is not.** "Provider" is genuinely overloaded in this
codebase, and the two meanings are easy to conflate because they live on the
same record. `ManagedAgentRecord.provider` is the agent's **LLM inference
provider** (e.g. an Anthropic- or OpenAI-compatible model endpoint) — a
completely different axis from `ManagedAgentRecord.backend`'s `Provider { id,
config }`, which names a **compute/deployment** provider. The collision is
not hypothetical: `buzz-backend-kubernetes`, itself a backend provider, reads
the *other* provider field (`agent.provider`, the LLM one) purely to refuse
deploying an agent configured for Buzz's shared-compute "relay-mesh" LLM
provider, since relay-mesh already runs on the relay's own compute and
deploying it into a pod would create a second, contending consumer of the
same agent identity. A backend provider is also not the substrate itself: the
protocol's own system model is explicit that the substrate (a Kubernetes
cluster, for the one shipped binding) is opaque to the desktop, and the
desktop never talks to it directly — only the provider binary does.

## How a deploy flows

```mermaid
sequenceDiagram
    participant D as Desktop
    participant P as Provider binary (buzz-backend-<id>)
    participant S as Substrate
    participant A as Agent (buzz-acp harness)
    participant R as Relay

    D->>P: stage binary, then "info" (JSON on stdin)
    P-->>D: name, protocol_version, config_schema
    D->>P: "deploy" (agent payload incl. nsec, provider_config)
    P->>S: create/reconcile the deployment
    S->>A: start the harness process
    P-->>D: agent_id (deployment handle)
    A->>R: connect, authenticate, publish presence
    D->>R: observe presence (the only post-deploy signal)
```

Two things this diagram makes visible: the provider is invoked twice, on the
same staged copy of itself, before the private key ever leaves the desktop;
and after `deploy` returns, the desktop's only channel back to the agent is
the relay, not the provider or the substrate.

## Background

**Why a plugin binary instead of a substrate SDK per backend.** The protocol
is intentionally the desktop's *door* to substrates, not a registry of
substrate integrations baked into the desktop itself: `buzz-backend-<id>` is
a zero-registration contract — any executable with the right name on `PATH`
participates — which is the same shape kubectl plugins and Docker CLI
plugins use. This keeps substrate-specific code (Kubernetes RBAC, namespace
choice, pod shape) out of the desktop binary entirely; the desktop's own
responsibility is the generic parts: discovery, the two-operation contract,
output caps, and secret handling.

**The trust boundary is stated, not hidden.** A backend provider is handed
the agent's private key by design — that is its job, since it must construct
the agent's identity on the substrate — and the specification is explicit
that malicious-provider containment is out of scope: the protocol *bounds*
the desktop's exposure (discovery only resolves binaries it will not
execute during discovery itself, output is capped and secret-redacted,
`provider_config` is validated against ever carrying a secret-shaped key,
and the UI surfaces an explicit trust decision) but cannot make a dishonest
provider safe.

**No management channel, by design (M1).** Once `deploy` succeeds, the
desktop deliberately keeps no persistent session to the remote agent or its
substrate: status comes from the agent's own relay presence, stopping it is a
relay message, and reconfiguring it is a future re-deploy. This is a stated
design axiom, not an oversight — it keeps the provider protocol's surface
small (no status query, no exec, no log fetch, no kill), at the cost of a
bounded staleness window on presence.

**A stale defect entry, corrected here.** The specification document
(`docs/remote-agents.md`) is pinned to a specific commit and lists, among its
"Known Defects," that the deploy path did not check a provider's declared
protocol version before sending it the agent's private key. At the revision
this node was checked against, that gate already exists in code — it was
added in a later commit that also shipped the Kubernetes provider — so the
defect entry is documentation drift rather than a description of the
protocol's current behavior. This node reports the drift rather than quietly
repeating the stale claim or silently "fixing" the spec's own text, which is
someone else's document to maintain.

## Use cases

- **Deciding whether an agent needs a backend provider at all.** Most agents
  run locally (`backend: Local`) and never touch this concept. It matters
  once an agent needs to run somewhere the desktop machine cannot guarantee —
  continuously, on shared infrastructure, or isolated from the desktop user's
  own session — at which point `backend: Provider { id, config }` is the
  record field that expresses that choice.
- **Writing or reviewing a new backend provider.** Anyone implementing a
  second `buzz-backend-<id>` binary (a systemd/SSH deployer is named
  elsewhere in the specification as a live example) needs this concept to
  know which obligations bind at which layer — the agent/harness contract
  binds every launcher, the provider/deployer contract binds only
  provider-managed ones — before diving into a specific substrate's binding
  policy.
- **Debugging "my remote agent looks stuck."** Because the desktop has no
  management channel to a deployed agent, the presence-only status model
  (and its bounded staleness window) is the first thing to reach for, rather
  than expecting the desktop to be able to query the substrate directly.
- **Auditing what a backend provider can do.** Understanding that a provider
  receives the agent's private key by design — and that containment of a
  dishonest provider is explicitly not this protocol's job — is the
  prerequisite for evaluating whether to trust a given provider binary at
  all.

## Comparison: `Local` vs. `Provider`

| | `Local` | `Provider { id, config }` |
|---|---|---|
| Where the harness runs | Spawned directly by the desktop, on the desktop's own machine | Deployed by the named `buzz-backend-<id>` binary onto its own substrate |
| Desktop's post-start channel | Direct process handle | None — relay presence only (M1) |
| Configuration edits | Re-resolved on every spawn | Take effect only on the deployment's next fresh generation (the running instance is a strict no-op) |
| Secrets exposure | Stay on the desktop's machine | Handed to the provider binary, then to whatever the provider constructs on the substrate |
| Who implements substrate specifics | Not applicable | The provider binary and its substrate-specific binding policy |

## Related resources

The full wire protocol, the five stated invariants, and the Kubernetes
binding's own reconciliation rules are `docs/remote-agents.md`'s to own — this
node does not restate them. `architecture-containers-agent-runtime` is the
corpus node for the agent-runtime container this concept deploys (`buzz-acp`,
`buzz-agent`, `buzz-dev-mcp`, `sprig`); a `references` relationship links to
it because that node already names `buzz-backend-kubernetes` as one of the
container's directly connected systems, and a reader arriving at either node
benefits from the other.

## Scope and omissions

**This node covers** what a backend provider is, the two-field name collision
with LLM providers, the shape of a deploy at a concept level, why the
protocol is a discoverable plugin binary rather than a built-in substrate
integration, the stated trust boundary and no-management-channel design
axiom, and the `Local`/`Provider` comparison.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The full wire protocol (payload fields, `launch` data, environment precedence) | `docs/remote-agents.md` |
| The five stated invariants (I1-I5) in full, and their enforcement mechanisms | `docs/remote-agents.md` |
| The Kubernetes binding's reconciliation state machine, GC, and fingerprinting | `docs/remote-agents.md` §The Kubernetes Binding; `crates/buzz-backend-kubernetes/src/` |
| The agent-runtime container this concept deploys, in full | `architecture-containers-agent-runtime` |
| Whether the LLM-provider concept (`ManagedAgentRecord.provider`, model/provider selection) needs its own corpus node | Not filed as of this writing; a candidate follow-up, not folded in here per the atomicity standard |
| A fix to `docs/remote-agents.md`'s stale Known Defect 5 entry | Not filed as of this writing; this node reports the drift, it does not correct the other document |

**Expected but not verified when this node was written:**

- **Whether any backend provider besides `buzz-backend-kubernetes` currently
  exists or ships in this repository.** `docs/remote-agents.md` names a
  systemd/SSH deployer as "the live example" of a second binding but this
  node did not locate or inspect that code — it may live outside this
  repository or not yet be merged.
- **Whether the desktop's own onboarding UI text (if any) states the trust
  warning `docs/remote-agents.md` requires before a user configures a
  provider.** This node cites the specification's requirement, not a
  verification that the UI implements it.
