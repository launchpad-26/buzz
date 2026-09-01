---
id: layers-compute-mesh-compute
type: layers
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5 on the launchpad branch."
    entry_class: FACT
    evidence:
      - "commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
  - statement: "Mesh compute is built on the external MeshLLM SDK, vendored via git dependencies pinned to tag v0.75.1 (mesh-llm-sdk, mesh-llm-host-runtime, mesh-llm-client, mesh-llm-node, mesh-llm-system, mesh-llm-events), all gated behind the desktop crate's optional `mesh-llm` Cargo feature."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/Cargo.toml:26"
      - "desktop/src-tauri/Cargo.toml:113"
  - statement: "The `mesh-llm` feature is not part of a plain desktop dev build. The project's own runbook states 'Using plain `just dev` is not sufficient: the Compute UI and embedded MeshLLM runtime are behind the `mesh-llm` feature,' and instructs `just mesh=1 dev` instead."
    entry_class: FACT
    evidence:
      - "docs/buzz-shared-compute-dev.md"
  - statement: "Buzz publishes a client-signed, replaceable Nostr discovery note carrying a member's MeshLLM owner identity and current iroh endpoint; MeshLLM itself performs the transport (direct QUIC or its own encrypted iroh relays) and admission, and the Buzz relay is only a generic Nostr store for that note and for membership -- it runs no mesh-specific handler."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/mesh_llm/coordinator.rs:1"
  - statement: "The discovery note is kind 30003, the standard NIP-51 bookmark-set kind reused with a reserved d-tag (`buzz-mesh-member-status`) precisely so an unmodified Buzz relay accepts and stores it through its existing generic user-state path -- confirmed independently by the desktop coordinator's own constant definition and by the e2e acceptance test's comment that kind 30003 is 'the NIP-51 bookmark set used for client-owned Mesh discovery notes.'"
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/mesh_llm/coordinator.rs:19"
      - "crates/buzz-core/src/kind.rs:43"
      - "crates/buzz-test-client/tests/e2e_mesh_llm.rs:45"
  - statement: "Admission to the mesh is gated by current Buzz community membership, not by MeshLLM itself: `owner_ids_from_events` in the desktop mesh-discovery module only trusts a status note whose Nostr signer appears in the latest kind:13534 (NIP-43) membership-list event, and it deliberately ignores status *freshness* for admission -- an offline member is still a member. Status *routing* (which node is actually selected to serve a request) is a separate check that does use freshness: a status note older than 120 seconds is excluded from routing even though it can still contribute to the admission allowlist."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/mesh_llm/discovery.rs:12"
      - "desktop/src-tauri/src/mesh_llm/discovery.rs:33"
      - "desktop/src-tauri/src/mesh_llm/discovery.rs:48"
  - statement: "Each machine holds a MeshLLM owner keypair (Ed25519) distinct from its Buzz/Nostr identity, and a node presents a signed ownership attestation binding `owner_id -> endpoint_id`; serve nodes enforce an allowlist of member owner ids built from the admission roster above."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/mesh_llm/identity.rs:1"
  - statement: "Iroh relay usage for symmetric-NAT peers is controlled by `BUZZ_MESH_IROH_RELAYS`, which defaults to MeshLLM's production relay set, accepts `0` to force direct QUIC only, and otherwise accepts a comma-separated allowlist of custom relay URLs; a remotely advertised relay URL that this node was not itself configured to contact is rejected."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/mesh_llm/transport_policy.rs:11"
      - "docs/buzz-shared-compute-dev.md"
  - statement: "A single mesh runtime slot on a machine serves two mutually exclusive roles that both report `state: \"running\"`: serve mode (this machine shares its own compute with the community) and client mode (this machine consumes a peer's compute). The desktop Share-compute toggle is derived from the runtime's `mode`, not its `state`, specifically because both roles report the same state."
    entry_class: FACT
    evidence:
      - "desktop/src/features/mesh-compute/shareToggleState.ts:1"
  - statement: "Managed agents consume mesh compute as a named LLM provider, `relay-mesh` (user-facing label 'Buzz shared compute'), which is translated into an OpenAI-compatible transport pointed at the local MeshLLM ingress `http://127.0.0.1:9337/v1`; the stored model value `auto` (or blank) maps to MeshLLM's virtual `mesh` model."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/managed_agents/relay_mesh.rs:3"
      - "desktop/src-tauri/src/managed_agents/relay_mesh.rs:16"
  - statement: "The virtual `mesh` model resolves per request to a Mixture-of-Agents committee when two or more mesh workers are reachable, and otherwise degrades to a single served model rather than erroring; this degradation is a pre-flight capacity decision, so a committee that forms and then loses a worker mid-turn still surfaces as a failed turn rather than repairing itself further."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/managed_agents/relay_mesh.rs:6"
  - statement: "A `relay-mesh` (Buzz shared compute) agent configuration is rejected at agent-creation time unless the agent's backend is `Local`: `normalize_relay_mesh` returns the error 'Buzz shared compute agents must use the local backend' for any non-local backend."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/commands/agents.rs:209"
  - statement: "The project's own remote-agents reference states this is a forced, not a chosen, constraint: 'Buzz shared compute (relay-mesh) is non-deployable, and this is forced, not chosen,' because the mesh transport resolves to the loopback address `127.0.0.1:9337`, which does not exist on a non-local backend; deploy-time validation MUST equally reject a mesh-configured agent create."
    entry_class: FACT
    evidence:
      - "docs/remote-agents.md"
  - statement: "`crates/buzz-relay-mesh` is a distinct subsystem that also uses the word 'mesh': its own module doc describes it as 'the inter-relay QUIC mesh' -- one iroh endpoint per relay runtime, gossip-based membership among relay pods, and a wire contract carrying tunnel traffic between pods -- entirely unrelated to LLM inference. It is constructed only when the relay's `BUZZ_MESH` environment seam is enabled, and single-instance/same-pod deployments never touch it."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay-mesh/src/lib.rs:1"
      - "crates/buzz-relay/src/mesh_boot.rs:1"
  - statement: "Because the desktop and relay codebases both use 'mesh' for two unrelated subsystems (MeshLLM-based shared LLM compute, documented here, and the inter-relay QUIC clustering mesh in `buzz-relay-mesh`), and because the sibling compute-provider documents named in issue #1046 (backend-provider, kubernetes-provider, local-agent-compute, remote-agent-compute) describe a different axis entirely -- where an agent's own runtime *process* executes -- rather than which LLM backend an already-running agent calls, this node's scope is deliberately narrow: the MeshLLM-based shared-LLM-compute capability only."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay-mesh/src/lib.rs:1"
      - "desktop/src-tauri/src/managed_agents/relay_mesh.rs:1"
      - "desktop/src-tauri/src/commands/agents.rs:209"
    confidence: 0.85
  - statement: "Issue #1046's own task body instructs that this document 'sits alongside sibling compute-provider documents (#1041 backend-provider, #1042 kubernetes-provider, #1045 local-agent-compute, #1048 remote-agent-compute)' and must 'scope it to mesh compute specifically and say so in boundaries/non-goals.'"
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1046 task body"
  - statement: "At the recorded revision, none of the sibling compute-provider documents (#1041, #1042, #1045, #1048) exist on origin/launchpad -- `git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus` returns no `layers/` entries at all -- so no relationship in this node may target them."
    entry_class: FACT
    evidence:
      - "git_ls_tree(origin/launchpad, launchpad/docs/corpus) -> no layers/ paths present"
  - statement: "architecture-containers-desktop, architecture-containers-agent-runtime and architecture-containers-relay exist on origin/launchpad as validated container nodes for exactly the three components mesh compute touches: the desktop app that embeds the MeshLLM runtime, the agent runtime (buzz-agent) that consumes it as an LLM provider, and the relay that stores its discovery/membership events generically."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/containers/desktop.md"
      - "launchpad/docs/corpus/architecture/containers/agent-runtime.md"
      - "launchpad/docs/corpus/architecture/containers/relay.md"
relationships:
  - type: references
    target: architecture-containers-desktop
  - type: references
    target: architecture-containers-agent-runtime
  - type: references
    target: architecture-containers-relay
---

# Mesh compute

Mesh compute is Buzz's peer-to-peer shared LLM inference capability: a member's
desktop app can share this machine's local LLM inference with other members of
the same Buzz community, and any member's managed agents can, in turn, consume
that shared capacity as an LLM provider — all without a hosted inference
service. It is built on the external MeshLLM SDK
(`github.com/Mesh-LLM/mesh-llm`), embedded in the desktop app behind an
optional Cargo feature, and coordinated using Buzz's own relay purely as a
generic Nostr event store.

**Disambiguation.** "Mesh" names two unrelated subsystems in this codebase.
This node is about MeshLLM-based shared LLM compute only. It is **not** about
`crates/buzz-relay-mesh`, the inter-relay QUIC mesh that clusters relay pods
for horizontal scaling — that is a server-side transport concern with no
connection to LLM inference, gated by a separate `BUZZ_MESH` relay
environment seam. See *Boundaries and non-goals* below.

## How it fits together

- **Sharing (serve mode).** A member turns on "Share this machine" in
  Settings → Compute. The desktop app starts an embedded MeshLLM node that
  serves a locally installed model over an OpenAI-compatible ingress on
  `127.0.0.1:9337`, and begins publishing a client-signed discovery note
  advertising its MeshLLM owner identity and iroh endpoint.
- **Consuming (client mode).** A member's agent selects the `relay-mesh`
  provider ("Buzz shared compute"). Buzz translates that selection into an
  OpenAI-compatible transport pointed at the same local `127.0.0.1:9337`
  ingress; MeshLLM itself routes the request over its peer-to-peer transport
  to whichever member is actually serving.
- **One slot, two roles.** A machine runs at most one mesh runtime at a time,
  and that single slot can be in serve mode or client mode — never both.
  Turning sharing on while consuming a peer's compute replaces the client
  runtime with a serve runtime.
- **Coordination via the relay, not a mesh-aware relay.** The discovery note
  is an ordinary NIP-51 bookmark-set event (kind 30003) with a reserved
  `d`-tag, deliberately chosen so any Buzz relay accepts and stores it through
  its existing generic path — the relay needs no mesh-specific handler at
  all.
- **Admission is Buzz's, transport and inference are MeshLLM's.** Whether a
  status note's signer is trusted to join the admission allowlist is decided
  from Buzz's own NIP-43 community membership roster (kind 13534), not from
  anything MeshLLM controls. Once admitted, actual transport (direct QUIC or
  MeshLLM's own encrypted iroh relays) and model routing are entirely
  MeshLLM's responsibility.
- **Model resolution.** Selecting the virtual `auto`/`mesh` model lets
  MeshLLM's router pick a target per request: a Mixture-of-Agents committee
  when two or more workers are reachable for that model, or a single served
  model when only one is available. A model named explicitly is passed
  through unchanged.

```mermaid
flowchart LR
    subgraph MemberA["Member A's desktop"]
        AgentA["managed agent<br/>(provider: relay-mesh)"] -->|"OpenAI-compat<br/>127.0.0.1:9337"| MeshClientA["embedded MeshLLM<br/>(client mode)"]
    end
    subgraph MemberB["Member B's desktop"]
        MeshServeB["embedded MeshLLM<br/>(serve mode)"] -->|"local model"| ModelB["installed LLM"]
    end
    Relay["Buzz relay<br/>(generic Nostr store)"]
    MeshClientA -. "discovery note (kind 30003)<br/>+ membership (kind 13534)" .-> Relay
    MeshServeB -. "discovery note (kind 30003)" .-> Relay
    MeshClientA <-->|"iroh QUIC<br/>(direct or relayed)"| MeshServeB
```

## Use cases

- **A community wants agent LLM inference without paying for or configuring a
  hosted provider.** Any member with spare local compute (and an installed
  model) can share it; other members' agents default to it without per-agent
  API keys.
- **An agent should always have *some* working LLM backend.** Setting "Buzz
  shared compute" with model "Default (auto)" as the agent-defaults provider
  means an agent with no pinned provider/model inherits it and resolves to a
  usable target whenever any member is sharing.
- **A developer needs to verify the real desktop → agent → LLM path.** The
  project's own local verification runbook exercises exactly this: share
  compute, set it as the agent default, start the built-in Fizz agent, and
  confirm a live channel reply — proving the harness, provider inheritance,
  and inference are all wired together, not just that a model is serving.

## Boundaries and non-goals

- **Not the inter-relay mesh.** `crates/buzz-relay-mesh` (the relay-clustering
  QUIC mesh behind `BUZZ_MESH`) is a different subsystem entirely — no shared
  code, no shared trust model, no connection to LLM inference. A reader
  looking for how relay pods discover and dial each other wants that crate,
  not this node.
  Constrained by the same `mesh_boot.rs` module boundary, that subsystem is
  its own candidate corpus node and is not documented here (see *Expected but
  not verified*).
- **Not a compute-provider (process placement) document.** This node
  describes mesh compute strictly as an *LLM provider* an already-running
  agent calls for inference. It does not describe where an agent's own
  runtime process executes — that is the sibling compute-provider
  documents' territory (#1041 backend-provider, #1042 kubernetes-provider,
  #1045 local-agent-compute, #1048 remote-agent-compute). None of those exist
  on `origin/launchpad` at this node's recorded revision, so this node
  carries no relationship to them; a future task may add one once they
  merge.
- **Local-only, by design and by enforcement.** A `relay-mesh`-provider agent
  can only be created with a `Local` backend — `normalize_relay_mesh` rejects
  any other backend outright — because the transport resolves to a loopback
  address that only exists on the machine actually running the mesh client.
  This is documented upstream as forced, not chosen. A reader who needs
  remote or containerized agent compute wants #1048 or #1042, not this
  concept.
- **Not the model catalog, download, or hardware-sizing UX.** The desktop
  feature also includes model catalog browsing, download progress, and
  hardware-based model suggestions (`desktop/src/features/mesh-compute/`).
  Those are implementation detail of the sharing UI, not part of the mesh
  compute *concept* itself, and are not catalogued here.

## Scope and omissions

**This document covers** what mesh compute is, how sharing (serve) and
consuming (client) roles work, how admission and routing are decided, how a
managed agent consumes it as the `relay-mesh` LLM provider, and its boundary
against the unrelated inter-relay mesh and against the process-placement
compute-provider documents.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The inter-relay QUIC clustering mesh (`crates/buzz-relay-mesh`, `BUZZ_MESH`) | Not yet filed as its own corpus task at this node's recorded revision — see *Expected but not verified* |
| Where an agent's own runtime process executes (backend/kubernetes/local/remote providers) | #1041, #1042, #1045, #1048 |
| The full MeshLLM SDK's own internal design (routing, Mixture-of-Agents gateway internals, native runtime installation) | Upstream `github.com/Mesh-LLM/mesh-llm`, not this repository |
| Desktop model-catalog, download-progress and hardware-suggestion UX detail | `desktop/src/features/mesh-compute/` implementation itself |
| Full security-boundary detail (signature schemes, relay allowlist mechanics) beyond what is needed to place the concept | `docs/buzz-shared-compute-dev.md` §Security boundary |

**Expected but not verified when this node was written:**

- **No relationship was added to a node for `crates/buzz-relay-mesh`.** No
  such node exists on `origin/launchpad` yet. Whether one should be filed as
  a follow-up task is noted below as a candidate, not decided here.
- **The MeshLLM SDK version referenced by the project's own runbook
  (`docs/buzz-shared-compute-dev.md`, which narrates behavior "post-v0.72.2"
  and of "MeshLLM v0.73.1") was not reconciled against the current pinned tag
  `v0.75.1` in `Cargo.toml` beyond confirming both are compatible ("post-"
  language does not contradict a later pin). Whether the runbook's narrated
  behavior still holds unchanged at `v0.75.1` was not independently verified
  against MeshLLM's own changelog.
- **No live mesh session was exercised while authoring this node.** All
  claims above are read from source and from the project's own runbook and
  reference documents, not observed by running `just mesh=1 dev` end to end.
