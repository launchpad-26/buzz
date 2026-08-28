---
id: architecture-containers-agent-runtime
type: architecture
status: draft
origin: launchpad
audiences:
  - developer
  - operator
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision a44cf52fc740ebebbdd671427480d14f0bce0115."
    entry_class: FACT
    evidence:
      - "commit a44cf52fc740ebebbdd671427480d14f0bce0115"
  - statement: "The agent runtime is composed of three crates — buzz-acp (the ACP harness), buzz-agent (a minimal ACP-compliant agent), and buzz-dev-mcp (a developer MCP server) — and CLAUDE.md groups exactly these three plus buzz-persona and buzz-workflow under one 'Agent surface' heading in the repo structure map."
    entry_class: FACT
    evidence:
      - "CLAUDE.md:69-74"
  - statement: "sprig is a multicall Rust binary whose only dependencies are buzz-acp, buzz-agent and buzz-dev-mcp; it dispatches to one of the three based on the argv0 name it was invoked as (or its own dev-mcp multicall names rg, tree, buzz, git-credential-nostr, git-sign-nostr for anything unrecognized), packaging the harness, the agent and the developer MCP server as one deploy-anywhere artifact."
    entry_class: FACT
    evidence:
      - "crates/sprig/src/main.rs"
      - "crates/sprig/Cargo.toml"
  - statement: "buzz-workflow (the YAML-as-code workflow engine) is a dependency compiled directly into buzz-relay rather than into buzz-acp, buzz-agent, buzz-dev-mcp or sprig, so it runs inside the relay process and is a separate container from the agent runtime despite sharing the 'Agent surface' grouping in CLAUDE.md's repo map."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/Cargo.toml"
  - statement: "buzz-acp's stated responsibility is to bridge Buzz relay events to any agent that speaks the Agent Client Protocol (ACP) over stdio: it listens for @-mentions on the relay, prompts the agent process it spawns, and the agent replies using the Buzz CLI."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/README.md:1-11"
  - statement: "buzz-acp's own five-step lifecycle description is: spawn N agent subprocesses and ACP-initialize each; discover accessible channels over the relay REST API and subscribe; queue inbound @-mention events per channel; drain a channel's queue into one batched ACP session/prompt call when no prompt is already in flight for it; and respawn the agent or reconnect to the relay (replaying via a since filter) on crash or disconnect."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/README.md:251-262"
  - statement: "buzz-agent's stated responsibility is a minimal, non-streaming ACP-compliant agent: it receives an ACP session/prompt over stdio, loops calling an LLM, executing the tool calls the LLM returns via MCP, and feeding results back, until the LLM stops requesting tools, a round cap is hit, or the client cancels."
    entry_class: FACT
    evidence:
      - "crates/buzz-agent/README.md:1-32"
  - statement: "buzz-dev-mcp depends on buzz-cli, git-credential-nostr and git-sign-nostr, and its Cargo.toml describes it as a developer MCP server; it is the multicall binary that also handles the rg, tree, buzz, git-credential-nostr and git-sign-nostr personality names, per sprig's own dispatch fallback and CLAUDE.md's crate table."
    entry_class: FACT
    evidence:
      - "crates/buzz-dev-mcp/Cargo.toml"
      - "crates/sprig/src/main.rs"
      - "CLAUDE.md:72"
  - statement: "buzz-acp depends on buzz-persona directly (path dependency in its Cargo.toml), while buzz-agent's Cargo.toml carries no such dependency, so persona-pack resolution is a harness-side responsibility performed before the agent subprocess is prompted, not something the agent process does itself."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/Cargo.toml:19-22"
      - "crates/buzz-agent/Cargo.toml"
  - statement: "The harness authenticates to the relay over WebSocket using NIP-42 (per its own 'How It Works' step 1) and discovers the agent's own channels via the relay REST API (GET /api/channels?member=true by default), auto-subscribing to a channel when a membership notification adds the agent to it."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/README.md:49-51"
      - "crates/buzz-acp/README.md:253"
  - statement: "By default the harness subscribes to stream message kinds 9 (KIND_STREAM_MESSAGE), 46010 (KIND_WORKFLOW_APPROVAL_REQUESTED) and 40007 (KIND_STREAM_REMINDER); forum event kinds (45001-45003) require opting in with --kinds and disabling the mention filter."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/README.md:225"
      - "crates/buzz-core/src/kind.rs:479"
      - "crates/buzz-core/src/kind.rs:491"
      - "crates/buzz-core/src/kind.rs:578"
  - statement: "Because the default subscription set includes kind 46010 (workflow approval requests), the agent runtime container has a direct inbound interface from the workflow-engine container (compiled into buzz-relay) in addition to its primary inbound interface of user/relay @-mentions."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-acp/README.md:225"
      - "crates/buzz-core/src/kind.rs:578"
      - "crates/buzz-relay/Cargo.toml"
    confidence: 0.6
  - statement: "The harness communicates with the spawned agent subprocess as an ACP JSON-RPC 2.0 client over that subprocess's stdio: initialize, then session/new (which passes the MCP servers to spawn), then session/prompt per batched turn."
    entry_class: FACT
    evidence:
      - "crates/buzz-agent/README.md:68-90"
      - "crates/buzz-acp/README.md:6-9"
  - statement: "buzz-agent's outbound interfaces are HTTPS calls to an LLM provider (Anthropic Messages API, OpenRouter, or any OpenAI-compatible endpoint including vLLM, llama.cpp, Databricks or Block Gateway) and stdio to zero or more MCP server child processes spawned via rmcp's transport-child-process, which is how it executes tool calls."
    entry_class: FACT
    evidence:
      - "crates/buzz-agent/README.md:9-32"
      - "crates/buzz-agent/Cargo.toml:33"
  - statement: "The 'Buzz CLI' tool the agent uses to act on Buzz (send_message, get_messages, etc., per buzz-acp's README diagram) is not called by buzz-agent directly — buzz-agent has no dependency on buzz-cli — it is exposed to the agent as an MCP server. buzz-dev-mcp is the MCP server that wraps buzz-cli, and is the default choice of MCP server binary by naming convention in buzz-acp's own tests, though buzz-acp does not spawn any MCP server unless BUZZ_ACP_MCP_COMMAND is explicitly set."
    entry_class: FACT
    evidence:
      - "crates/buzz-dev-mcp/Cargo.toml:17"
      - "crates/buzz-acp/README.md:6-9"
      - "crates/buzz-acp/src/config.rs:261-262"
      - "crates/buzz-acp/src/pool.rs:4408"
  - statement: "BUZZ_ACP_MCP_COMMAND defaults to an empty string, and buzz-acp's own unit test asserts an empty mcp_command produces no MCP servers at all — so the harness only wires an MCP server (conventionally buzz-dev-mcp) into the agent's session/new call when a deployment explicitly configures one."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/config.rs:261-262"
      - "crates/buzz-acp/src/lib.rs:5123"
      - "crates/buzz-acp/src/lib.rs:7263-7269"
  - statement: "Buzz Desktop launches buzz-acp as a bundled sidecar subprocess for every locally-run managed agent (DEFAULT_ACP_COMMAND = \"buzz-acp\"), configuring it via environment and CLI args rather than reimplementing the harness protocol itself; the desktop is therefore an inbound caller of the agent-runtime container's process boundary, not a peer implementation of it."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/managed_agents/types.rs:810"
      - "desktop/src-tauri/src/managed_agents/runtime.rs:250"
  - statement: "docs/remote-agents.md states directly that the desktop is 'one launcher among many': what makes a process a live Buzz agent is a keypair, a NIP-OA auth tag, and a relay URL handed as environment to the buzz-acp harness, and anything that can set that environment and exec the harness is a conforming launcher."
    entry_class: FACT
    evidence:
      - "docs/remote-agents.md:31-36"
  - statement: "docs/remote-agents.md names buzz-backend-kubernetes as the first conforming remote-agent provider, realizing its contract as a bare Kubernetes Pod running the sprig container image, and states that agent conversational behavior stays governed by the ACP harness unchanged by where the harness runs."
    entry_class: FACT
    evidence:
      - "docs/remote-agents.md:22-24"
      - "docs/remote-agents.md:50-52"
  - statement: "The agent runtime is released in two forms by dedicated CI workflows: sprig.yml builds a static-musl multicall binary tarball for x86_64/aarch64 Linux (rolling sprig-latest on push to main, versioned on sprig-v* tags), and sprig-image.yml builds and publishes the multi-arch container image ghcr.io/block/buzz-sprig, described as 'the digest-pinned box the Kubernetes backend deploys agents into.'"
    entry_class: FACT
    evidence:
      - ".github/workflows/sprig.yml:1-15"
      - ".github/workflows/sprig-image.yml:1-9"
  - statement: "buzz-agent's stated trust boundary is the operator who launched the agent: the harness, MCP server binaries and API keys are all trusted, while model output, tool results and prompts are treated as untrusted and bounded (stdout single-consumer discipline, an environment whitelist for MCP children, process-group kill on transport break, capped frame/prompt/response/tool-result sizes, and biased-select cancellation at every loop boundary)."
    entry_class: FACT
    evidence:
      - "crates/buzz-agent/README.md:292-322"
  - statement: "Desktop's access_policy module documents that the harness's inbound author gate (crates/buzz-acp/src/lib.rs) admits the human owner plus every NIP-OA-verified agent sharing that owner under 'owner-only' mode, and that this owner-plus-verified-siblings boundary is deliberate rather than an oversight, because Buzz's built-in Welcome team relies on a lead instructing owner-only teammates."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/managed_agents/access_policy.rs:1-36"
  - statement: "docs/remote-agents.md states that a remote-agent provider binary is handed the agent's private key (nsec) by design, that malicious-provider containment is explicitly out of scope for the protocol, and that the protocol only bounds the desktop's exposure to a hostile provider (discovery-only resolution, output caps, secret redaction, anti-secret config validation, an explicit UI trust warning) rather than making a hostile provider safe."
    entry_class: FACT
    evidence:
      - "docs/remote-agents.md:53-58"
  - statement: "Neither buzz-acp, buzz-agent, buzz-dev-mcp nor sprig depends on buzz-db, buzz-search or any other crate that reaches the relay's Postgres event store directly; the runtime's only path to Buzz's durable data is the relay's Nostr WebSocket/HTTP surface (events published and queried like any other authenticated client), never a direct database connection."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-acp/Cargo.toml"
      - "crates/buzz-agent/Cargo.toml"
      - "crates/buzz-dev-mcp/Cargo.toml"
      - "crates/sprig/Cargo.toml"
    confidence: 0.7
---

# Container: Agent Runtime

The process boundary that runs an AI agent as a first-class Buzz participant:
it bridges relay events to an ACP-speaking agent process, gives that agent a
bounded set of tools, and lets the agent act back on Buzz through the same
Nostr surface any other authenticated client uses. This node documents it as
one container per the corpus schema's `architecture` type — see
[`node.schema.json`](../../schema/node.schema.json) for the field contract
this front matter satisfies, and [`AGENTS.md`](../../AGENTS.md) for how this
node was authored and checked.

## Responsibility, technology and ownership boundary

**Responsibility.** Turn Buzz relay events addressed to an agent into LLM
turns, and turn the LLM's tool calls back into Buzz actions — without the
agent process ever needing to know how to speak Nostr, WebSocket, or NIP-42
itself.

**Technology.** Three Rust crates, each an independent binary and also
combinable into one multicall executable:

| Crate | Role |
|---|---|
| `buzz-acp` | The ACP harness: relay client, event router, agent-subprocess supervisor. |
| `buzz-agent` | A minimal, non-streaming, reference ACP-compliant agent: LLM-call-then-tool-call loop, no persistence. |
| `buzz-dev-mcp` | A developer MCP server exposing shell, file-edit and Buzz-CLI-backed tools to an agent process over MCP. |
| `sprig` | A multicall binary bundling all three above into one deploy-anywhere artifact, dispatched on argv0. |

`buzz-persona` (persona-pack resolution) is a direct dependency of `buzz-acp`
and is resolved harness-side, before the agent subprocess is prompted — the
agent process itself carries no dependency on it. `buzz-workflow` (the
YAML-as-code automation engine) is compiled into `buzz-relay`, not into any
crate in this table, and is therefore a different container despite being
grouped under the same "Agent surface" heading in the repository's crate map;
see *Scope and omissions* below.

**Ownership boundary.** The trust boundary buzz-agent's own documentation
states is the operator who launched the process: the harness, the MCP server
binaries it spawns, and any API keys in its environment are trusted. Model
output, tool call arguments, and tool results are the untrusted material the
runtime bounds — with a documented set of size caps, an environment
whitelist for MCP children, process-group teardown on transport break, and
cancellation that always wins the race at every loop boundary. Within a
running agent, the inbound author gate (in `buzz-acp`) further narrows *who*
may instruct the agent at all; Desktop's access-policy layer documents that
gate's "owner-only" mode as owner **plus** every NIP-OA-verified agent
sharing that owner, a deliberate boundary rather than an oversight (Buzz's
Welcome team depends on a lead instructing owner-only teammates).

## Inbound and outbound interfaces

**Inbound, from the relay:**
- WebSocket connection, NIP-42 authenticated, to `BUZZ_RELAY_URL`.
- Channel discovery over the relay's REST API (`GET /api/channels?member=true`
  by default), with auto-subscription when a membership notification adds the
  agent to a new channel.
- A default subscription to stream-message kinds `9` (mentions), `46010`
  (workflow-approval-requested) and `40007` (stream reminders); forum kinds
  require explicitly opting in and disabling the mention filter. The `46010`
  subscription is a direct, if narrow, inbound edge from the workflow-engine
  container running inside `buzz-relay`.

**Inbound, to the harness process itself:** anything a launcher can set as
environment and then exec `buzz-acp` with is a conforming way to start an
agent — Buzz Desktop is documented as "one launcher among many," spawning
`buzz-acp` as a bundled sidecar subprocess for every local managed agent
rather than reimplementing the harness protocol.

**Harness-to-agent (internal to the container):** ACP is JSON-RPC 2.0 over
the agent subprocess's stdio — `initialize`, then `session/new` (which
carries the MCP servers to spawn for that session), then one `session/prompt`
per batched turn. Each channel has at most one prompt in flight; multiple
channels run concurrently across a pool of `N` agent subprocesses.

**Outbound, from the agent process:**
- HTTPS to an LLM provider — Anthropic Messages API, OpenRouter, or any
  OpenAI-compatible endpoint (vLLM, llama.cpp, Databricks, Block Gateway,
  Ollama, …).
- Stdio to zero or more MCP server child processes (via `rmcp`'s
  transport-child-process), which is how the agent executes tool calls.
  `buzz-dev-mcp` — wrapping `buzz-cli`, `git-credential-nostr` and
  `git-sign-nostr` — is the conventional choice, but the harness spawns no
  MCP server at all unless `BUZZ_ACP_MCP_COMMAND` is explicitly set; an empty
  value (the default) yields zero MCP servers for the session.

**Directly connected containers/systems:** the Buzz relay (WebSocket + REST,
both directions), an LLM provider (outbound HTTPS, no Buzz-side coupling
beyond the API contract), Buzz Desktop (as one possible local launcher of the
harness process), and — where deployed remotely — a backend provider binary
such as `buzz-backend-kubernetes`, which the Desktop hands the agent's
private key to and which realizes the container as a bare Kubernetes Pod
running the `sprig` image. This runtime is never observed depending on
`buzz-db` or `buzz-search`; its only path to Buzz's durable data is the same
authenticated Nostr surface any other client uses, not a direct database
connection.

## Deployment implications

Released in two forms, by two dedicated CI workflows:

- `sprig.yml` — a static-musl multicall binary for `x86_64`/`aarch64` Linux,
  published as a rolling `sprig-latest` release on push to `main` and as a
  versioned release on `sprig-v*` tags.
- `sprig-image.yml` — the multi-arch container image
  `ghcr.io/block/buzz-sprig`, the image the Kubernetes remote-agent provider
  deploys.

`docs/remote-agents.md` is the formal specification governing remote
deployment: it defines the provider protocol between Buzz Desktop and any
`buzz-backend-<id>` binary, states that the desktop holds no management
channel to a remotely-run agent (relay presence is the sole status signal),
and is explicit that agent *conversational* behavior — the responsibility of
this container — is unchanged by where the harness runs. That document also
states plainly that malicious-provider containment is out of scope for the
protocol: a provider is handed the agent's `nsec` by design, and the protocol
only bounds the desktop's own exposure to a hostile provider, not the
provider's honesty.

## Data and security implications

No crate in this container links `buzz-db` or `buzz-search`; state the
runtime needs (channel membership, event history, session identity) is
fetched and published over the relay's Nostr surface, the same one every
other authenticated client uses. There is no separate agent-runtime
datastore documented or found.

Security is covered in depth by `buzz-agent`'s own README under "Security
Model" and "Bounded Everything" (size caps on every untrusted boundary,
MCP-child environment whitelisting, process-group teardown, cancellation
priority) and by `docs/remote-agents.md`'s five stated invariants for remote
deployment (identity fail-closed, no secrets in configuration,
presence-is-status, at-most-one-live-instance, intentional-termination-is-
final). This node summarizes their existence and does not restate their
content — see *Where each rule lives*.

## Where each rule lives

This node states the container boundary; it does not duplicate the
implementation it links to.

| For | Read |
|---|---|
| ACP harness configuration, lifecycle, BYOH tiers | [`crates/buzz-acp/README.md`](../../../../../crates/buzz-acp/README.md) |
| Agent loop, security model, size limits | [`crates/buzz-agent/README.md`](../../../../../crates/buzz-agent/README.md) |
| Developer MCP tool surface | [`crates/buzz-dev-mcp/src/`](../../../../../crates/buzz-dev-mcp/src/) |
| Persona-pack format | [`crates/buzz-persona/PERSONA_PACK_SPEC.md`](../../../../../crates/buzz-persona/PERSONA_PACK_SPEC.md) |
| Remote deployment protocol and invariants | [`docs/remote-agents.md`](../../../../../docs/remote-agents.md) |
| Desktop's local/remote launch and access-policy logic | `desktop/src-tauri/src/managed_agents/` |
| Event kind registry (mentions, workflow approvals, …) | [`crates/buzz-core/src/kind.rs`](../../../../../crates/buzz-core/src/kind.rs) |
| Release/build pipelines for this container | [`.github/workflows/sprig.yml`](../../../../../.github/workflows/sprig.yml), [`.github/workflows/sprig-image.yml`](../../../../../.github/workflows/sprig-image.yml) |

## Scope and omissions

**This node covers** the agent-runtime container's responsibility,
technology and ownership boundary; its inbound/outbound interfaces and
directly connected containers/systems; and its deployment, data and security
implications at a container level.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The full ACP wire protocol and BYOH tier details | `crates/buzz-acp/README.md` |
| The agent's exact LLM-provider selection and model-capability logic | `crates/buzz-agent/src/model_capabilities.rs`, `src/catalog.rs` |
| Persona-pack schema and merge rules | `crates/buzz-persona/PERSONA_PACK_SPEC.md` |
| The remote-agent provider protocol in full (payload schema, five invariants, Kubernetes binding) | `docs/remote-agents.md` |
| Whether `buzz-workflow` (compiled into `buzz-relay`) deserves its own architecture-container node describing its relationship to this one | Not filed as of this writing; a candidate for a follow-up task rather than folded into this node, per this task's own definition-of-done boundary on independently maintainable nodes |

**No `relationships` declared.** A `relationships[].target` naming an id no
loaded node carries is a hard validation error, and no other
`architecture`-typed node is merged in the corpus yet — 0 of 26 nodes on that
track are landed at the time this node was written. This follows the same
precedent `corpus-standard-confidence` and `corpus-readme` set for the same
reason: the edge set is left for the first pass once sibling nodes exist to
point at, not a claim that this container has no real relationships to a
relay container, a desktop container, or a workflow-engine container.

**Expected but not verified when this node was written:**

- **Whether `buzz-dev-mcp` is the MCP server every real deployment actually
  configures.** `BUZZ_ACP_MCP_COMMAND` is a free-text command name; this node
  establishes it as the conventional choice (by dependency shape and by
  buzz-acp's own test fixtures) but did not enumerate every deployment's
  actual configuration.
- **The precise resource-scaling relationship** between the agent pool size
  `N` and total memory, beyond buzz-acp's own README note that usage scales
  "approximately as N × (agent memory + MCP server memory)."
- **Whether any consumer besides Buzz Desktop and `buzz-backend-kubernetes`
  currently launches this container in practice.** `docs/remote-agents.md`
  states the protocol admits any conforming launcher; no third launcher was
  found in this repository at the recorded revision.
