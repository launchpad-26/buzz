---
id: capabilities-agents-managed-agent
type: capabilities
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 131b02f989684117d9ab1dd426f1673fa638e523."
    entry_class: FACT
    evidence:
      - "commit 131b02f989684117d9ab1dd426f1673fa638e523"
  - statement: "Root AGENTS.md states that the auth env vars BUZZ_RELAY_URL, BUZZ_PRIVATE_KEY and BUZZ_AUTH_TAG are auto-injected by the ACP harness into managed agent subprocesses, and that in development they are instead set manually in the environment."
    entry_class: FACT
    evidence:
      - "AGENTS.md:203-205"
  - statement: "AcpClient::spawn in buzz-acp builds its child process with tokio::process::Command and never calls env_clear on it, so the spawned agent subprocess inherits the harness's own process environment (including BUZZ_RELAY_URL, BUZZ_PRIVATE_KEY and BUZZ_AUTH_TAG when those are set in the harness's environment) in addition to the persona-specific extra_env entries layered on top with operator-wins precedence."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/acp.rs:454-523"
  - statement: "AcpClient::shutdown kills the agent subprocess's entire process group (the child was spawned with process_group(0) so its PID equals its PGID) so that MCP-server and tool child processes are cleaned up rather than orphaned, falls back to start_kill on the direct child only when the process group cannot be killed, and bounds the subsequent wait at five seconds rather than waiting unboundedly."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/acp.rs:416-444"
  - statement: "docs/remote-agents.md states directly that what makes a process a live Buzz agent is a keypair, a NIP-OA auth tag, and a relay URL, handed as environment to the buzz-acp harness, and that anything able to set that environment and exec the harness -- a bash script, a systemd unit, a CI job, or a remote-agent provider binary -- is a conforming launcher; the desktop is described as 'one launcher among many' rather than the only one."
    entry_class: FACT
    evidence:
      - "docs/remote-agents.md:31-36"
  - statement: "docs/remote-agents.md's own Summary states that remote agents 'extend Buzz's managed-agent model across a deliberately thin boundary,' naming the managed-agent model as the base the remote-agent protocol builds on rather than a separate, unrelated concept."
    entry_class: FACT
    evidence:
      - "docs/remote-agents.md:1768-1775"
  - statement: "Buzz Desktop's managed_agents module models an agent's backend as one of two variants: BackendKind::Local (the #[default] variant, carrying no further data) for a locally-run managed agent, and BackendKind::Provider { id, config } for an agent deployed to a remote substrate through a named provider binary -- the same local/remote split docs/remote-agents.md describes in prose, encoded directly in the desktop's own type."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/managed_agents/types.rs:6-9"
  - statement: "Buzz Desktop's managed_agents module defines DEFAULT_ACP_COMMAND as the literal string \"buzz-acp\", the sidecar binary the desktop spawns as the launcher for every locally-run managed agent, and stamps that spawned process's environment with a BUZZ_MANAGED_AGENT marker used elsewhere in the same module as the sole authoritative proof of the desktop's ownership of that process (for example, when identifying stale processes to reap)."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/managed_agents/types.rs:761"
      - "desktop/src-tauri/src/managed_agents/runtime.rs:592-593"
  - statement: "The architecture-containers-agent-runtime corpus node already documents, at container level, that Buzz Desktop launches buzz-acp as a bundled sidecar subprocess for every locally-run managed agent, configuring it via environment and CLI args rather than reimplementing the harness protocol, and that this makes the desktop an inbound caller of the agent-runtime container's process boundary rather than a peer implementation of it -- this capability node references that node instead of restating its architecture."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/containers/agent-runtime.md"
  - statement: "Sibling task issue #716 (capabilities/agents/remote-agent.md) is open and unmerged at the recorded revision, so capabilities-agents-remote-agent is not a valid relationships target for this node under AGENTS.md's own merge-target-branch rule."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#716 (title and open state, read via gh issue view)"
relationships:
  - type: references
    target: architecture-containers-agent-runtime
---

# Managed agent: capability

Buzz can run an AI agent as a **managed agent** -- a subprocess whose entire
lifecycle the launching harness directly controls: it spawns the agent
binary, hands it the identity and relay credentials it needs to act as a
Buzz participant, and can end its life on demand. This is the capability
docs/remote-agents.md calls "the managed-agent model" and states that a
remote agent (a separate, not-yet-drafted capability node, see *Boundary*)
extends across a thinner boundary rather than replaces. A human operator or
another agent gets, from this capability, an agent identity that can be
started with one command and stopped with one call, with no separate
credential-provisioning step: the same environment that names the agent's
relay and keypair is what starts it.

Concretely, this means:

- **One launcher, full control.** Whatever process starts `buzz-acp` (a
  shell command, a systemd unit, Buzz Desktop, a CI job) holds a direct
  process handle to the agent subprocess for as long as it runs -- it can
  observe the child's stdio, and it can kill it. `docs/remote-agents.md`
  states this as "the desktop is one launcher among many": what makes a
  process a live Buzz agent is a keypair, a NIP-OA auth tag, and a relay URL
  handed to it as environment, and anything able to set that environment and
  exec the harness is a conforming launcher for a managed agent.
- **Identity flows through the environment, not a provisioning API.** Root
  `AGENTS.md` documents `BUZZ_RELAY_URL`, `BUZZ_PRIVATE_KEY` and
  `BUZZ_AUTH_TAG` as the three auth env vars a managed agent subprocess
  needs, auto-injected by the ACP harness in a managed deployment (Buzz
  Desktop's local launch path) and set manually by a developer running the
  harness themselves. Mechanically, `buzz-acp`'s `AcpClient::spawn` never
  clears the child's environment before exec, so a managed agent subprocess
  inherits whatever the launching harness process already has set, with
  persona-specific overrides layered on top.
- **Shutdown is a direct call, not a message.** `AcpClient::shutdown` kills
  the agent subprocess's entire process group (cleaning up any MCP-server or
  tool child processes along with it) and bounds the wait for exit at five
  seconds. This is the opposite of a remote agent's shutdown, which
  `docs/remote-agents.md` states is a relay message because the desktop
  holds no process handle to a remotely deployed agent at all.
- **Local backend, by default.** Buzz Desktop's own agent model encodes this
  split directly: an agent's backend is `BackendKind::Local` (the default)
  for a managed agent the desktop launches and directly supervises as a
  subprocess, or `BackendKind::Provider { id, config }` when deployed to a
  remote substrate through a named provider binary instead.

## Maturity

**Shipped.** `AcpClient::spawn` and `AcpClient::shutdown` are implemented and
tested code in `crates/buzz-acp/src/acp.rs`, not a design in progress.
Root `AGENTS.md` documents the auto-injected auth env vars as a fact about
the current agent-first CLI, not a future plan. Buzz Desktop's
`managed_agents` module implements `BackendKind::Local` as the default
backend and spawns `buzz-acp` (`DEFAULT_ACP_COMMAND`) as the sidecar for
every local managed agent today.

## Boundary

This node does not describe:

- **How the capability is built.** The agent-runtime container --
  `buzz-acp` (the harness), `buzz-agent` (a reference agent), `buzz-dev-mcp`
  (the developer MCP server), and `sprig` (the multicall bundle of all
  three) -- is documented at container level by
  `architecture-containers-agent-runtime`, including its full inbound and
  outbound interfaces. This node references that node rather than
  restating its technology or interfaces.
- **The step-by-step flow of one agent turn.** How a relay event becomes a
  batched `session/prompt` call and a reply is a flow-shaped concern, not
  this capability's own subject matter.
- **The remote-agent capability.** A remote agent extends this same
  managed-agent model across a thinner boundary -- a provider binary and a
  relay, with the desktop holding no process handle to the running agent at
  all. That is a distinct, not-yet-drafted capability node
  (`launchpad-26/buzz#716`), not a variant of this one; this node does not
  describe the provider protocol, the five invariants `docs/remote-agents.md`
  states for remote deployment, or the Kubernetes binding.
- **How the running system is operated.** Deployment pipelines, monitoring
  and incident response for the agent-runtime container are outside this
  capability's own scope.

## Relationships

- references: `architecture-containers-agent-runtime` -- the container that
  realizes this capability (the ACP harness, the reference agent, the
  developer MCP server, and their bundled multicall binary).

No `part-of` or `implements` relationship is declared: no broader
"agents" capability node and no capability template instantiation edge back
to `corpus-template-capability` exist as a merged target at the recorded
revision, and adding either would be speculative rather than checked.

## Scope and omissions

**This node covers** what the managed-agent capability is (an agent
subprocess whose lifecycle -- spawn, identity/auth env injection, and
shutdown -- the launching harness directly controls), its current shipped
maturity, and its boundary against the agent-runtime architecture it is
built on, the flow of a single agent turn, the not-yet-drafted remote-agent
capability, and agent-runtime operations.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The agent-runtime container's technology, interfaces and deployment | `architecture-containers-agent-runtime` |
| The step-by-step flow of one agent turn | a flow-shaped node, not yet drafted in this batch |
| The remote-agent capability and its provider protocol | `launchpad-26/buzz#716` (capabilities/agents/remote-agent.md, unmerged) |
| The boundary contract (CLI subcommands, ACP JSON-RPC surface) this capability is exposed through | an interface-shaped node, not yet drafted |
| How the running agent-runtime system is operated | the `operations` corpus surface |

**Expected but not verified when this node was written:**

- **Whether every managed-agent launcher besides Buzz Desktop and a
  developer's own shell actually sets all three auth env vars identically.**
  `docs/remote-agents.md` states the environment contract admits any
  conforming launcher; no third launcher's exact invocation was inspected
  here.
- **The full persona `extra_env` precedence rules** (for example, the
  special-cased `CODEX_CONFIG` merge in `AcpClient::spawn`) are cited as
  evidence that environment inheritance is the injection mechanism, but
  their own per-key precedence behavior is not this node's subject and was
  not verified exhaustively.
