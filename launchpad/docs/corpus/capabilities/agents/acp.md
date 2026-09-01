---
id: capabilities-agents-acp
type: capabilities
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - operator
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision cad6c375fdcc590158c1456c9fc7875f0f84a844."
    entry_class: FACT
    evidence:
      - "commit cad6c375fdcc590158c1456c9fc7875f0f84a844"
  - statement: "Root VISION_PROJECTS.md's own 'Capability | Status' table lists 'MCP server + ACP agent harness' as its own row, marked '✅ Ships today', naming this capability at the same product level as its neighboring rows (channels/forums/DMs/canvases, workflow engine, Blossom media storage, git hosting)."
    entry_class: FACT
    evidence:
      - "VISION_PROJECTS.md:251"
  - statement: "buzz-acp's own README states its responsibility as bridging Buzz relay events to any agent that speaks the Agent Client Protocol (ACP) over stdio: it listens for @mentions on the relay, prompts the agent process it spawns, and the agent replies using the Buzz CLI — and names goose, codex (via codex-acp) and claude code (via claude-agent-acp) as agents it supports today."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/README.md:1-12"
  - statement: "buzz-acp's README states the general contract any ACP agent must meet to work with the harness: accept 'initialize' and return a result, accept 'session/new' with 'mcpServers' and return a sessionId, accept 'session/prompt' with a text message and stream 'session/update' notifications, and return a stopReason — with BUZZ_ACP_AGENT_COMMAND/BUZZ_ACP_AGENT_ARGS pointing the harness at any binary meeting it."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/README.md:323-332"
  - statement: "Buzz Desktop's Bring Your Own Harness (BYOH) system lets a user register any ACP-speaking agent tool as a selectable runtime without a PR, structured as three tiers: tier-1 compiled-in runtimes (Goose, Claude Code, Codex, Buzz Agent) with auto-installers and first-class onboarding; tier-2 a static preset catalog (Cursor, Oh My Pi, Grok Build, OpenCode, Kimi Code, Amp, Hermes Agent, OpenClaw), PATH-probed and not user-editable; and tier-3 user-authored custom-harness JSON files naming an id, label, command, args and env."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/README.md:264-321"
  - statement: "buzz-agent (the reference agent shipped for this capability) is described in its own README as a minimal, non-streaming, non-persistent ACP-compliant agent: a client sends session/prompt, and the agent loops calling an LLM, running the tool calls it returns via MCP, and feeding results back, until the LLM stops asking for tools, a round cap is hit, or the client cancels."
    entry_class: FACT
    evidence:
      - "crates/buzz-agent/README.md:1-30"
  - statement: "The Inbound Author Gate controls which authors' events the harness forwards to the agent at all, with four modes (owner-only, allowlist, anyone, nobody) and owner control commands (!shutdown, !cancel, !rotate) checked ahead of the gate so the owner can always manage the harness regardless of the configured mode; the documented default is owner-only, under which an agent with no registered owner drops all inbound events until one is resolved."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/README.md:132-162"
  - statement: "docs/remote-agents.md states that Buzz Desktop is 'one launcher among many' for this capability: what makes a process a live Buzz agent is a keypair, a NIP-OA auth tag, and a relay URL handed as environment to the buzz-acp harness, and any process that can set that environment and exec the harness is a conforming launcher — naming buzz-backend-kubernetes as the first conforming remote-agent provider, realizing the same capability as a bare Kubernetes Pod running the sprig container image."
    entry_class: FACT
    evidence:
      - "docs/remote-agents.md:31-36"
      - "docs/remote-agents.md:22-24"
  - statement: "launchpad/docs/corpus/architecture/containers/agent-runtime.md (id: architecture-containers-agent-runtime) already documents how this capability is built — the buzz-acp/buzz-agent/buzz-dev-mcp/sprig crates, their technology choices, and their inbound/outbound interfaces — and is merged on origin/launchpad at the checked revision."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/containers/agent-runtime.md"
  - statement: "launchpad/docs/corpus/architecture/flows/agent-turn.md (id: architecture-flows-agent-turn) already documents the step-by-step path one turn of this capability takes — startup, channel discovery, the Inbound Author Gate, batching, and dispatch — and is merged on origin/launchpad at the checked revision."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/flows/agent-turn.md"
  - statement: "At the checked revision, git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus lists no path under capabilities/ at all, so this is the first capabilities-typed node merged into the corpus, and no capability-shaped sibling exists yet to declare part-of or a second references edge toward."
    entry_class: FACT
    evidence:
      - "git_ls_tree(ref='origin/launchpad', path='launchpad/docs/corpus') -> AGENTS.md, README.md, architecture/**, schema/** (excluded), standards/**, templates/**; no capabilities/ path present, run against cad6c375fdcc590158c1456c9fc7875f0f84a844"
  - statement: "No interfaces-events-typed corpus node exists yet for the ACP JSON-RPC wire surface or for buzz-cli's own command surface, so this capability node has no interface-node sibling to reference for the boundary contract it is exposed through."
    entry_class: FACT
    evidence:
      - "git_ls_tree(ref='origin/launchpad', path='launchpad/docs/corpus') -> no interfaces-events-typed node present at cad6c375fdcc590158c1456c9fc7875f0f84a844"
  - statement: "Issue #703 (parent Feature #613) is the task this node is drafted against, and its Definition of Done requires the document to state the capability and primary actors/outcomes, define behavioral rules/constraints/variants, link major flows/interfaces/data/platform implementation, and link verification demonstrating the capability."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#703 definition of done"
relationships:
  - type: part-of
    target: capabilities-agents-agent
  - type: references
    target: architecture-containers-agent-runtime
  - type: references
    target: architecture-flows-agent-turn
---

# ACP Agent Harness: capability

Buzz can run any [ACP](https://agentclientprotocol.com/)-speaking AI agent as a
first-class participant in a community: a user registers an agent's identity, and
that agent is @mentioned in channels, replies through the same Buzz surface a human
uses, and can be one of several interchangeable agent tools — Goose, Claude Code,
Codex, Buzz's own reference agent, or (via Buzz Desktop's Bring Your Own Harness
system) any other agent binary that implements the ACP contract — without Buzz
itself needing to know anything about the agent's internals. This is the product
capability VISION_PROJECTS.md's own "Capability | Status" table names "MCP server +
ACP agent harness."

## Maturity

**Shipped.** VISION_PROJECTS.md's Status table marks this capability "✅ Ships
today" (line 251), and the capability is realized today by the `buzz-acp` harness
crate, the `buzz-agent` reference agent, and Buzz Desktop's three-tier
Bring-Your-Own-Harness system for registering additional ACP-speaking agent tools —
all present and documented in this repository at the revision this node was checked
against.

## What a user or agent can do because this capability exists

- **Register an AI agent as a Buzz participant.** An agent has its own Nostr
  keypair and identity, joins channels, and is reachable by @mention like any other
  member.
- **Choose which agent tool answers.** The harness is agent-agnostic: it supports
  Goose, Codex (via `codex-acp`) and Claude Code (via `claude-agent-acp`) out of the
  box, plus Buzz's own minimal reference agent (`buzz-agent`). Buzz Desktop's BYOH
  system extends this further with a tier-2 preset catalog (Cursor, Oh My Pi, Grok
  Build, OpenCode, Kimi Code, Amp, Hermes Agent, OpenClaw) and a tier-3 custom-harness
  path for any other binary a user points at, provided it implements ACP's
  `initialize` / `session/new` / `session/prompt` / stop-reason contract.
  Tier-1 runtimes (Goose, Claude Code, Codex, Buzz Agent) get auto-installers and
  first-class onboarding; tier-2 and tier-3 are PATH-probed, not auto-installed.
- **Control who the agent responds to.** An owner sets the Inbound Author Gate to
  one of four modes — owner-only (default), allowlist, anyone, or nobody — and can
  always issue `!shutdown`, `!cancel` or `!rotate` regardless of the configured mode,
  because owner control commands are checked ahead of the gate.
- **Run the agent anywhere a conforming launcher can set its environment.** Buzz
  Desktop is one launcher among several documented ones; a remote-agent provider such
  as `buzz-backend-kubernetes` can run the same capability as a Kubernetes Pod, with
  agent conversational behavior unchanged by where the harness process runs.

## Boundary

This node does not describe:

- **How the capability is built** — the crates, their dependencies, and their
  inbound/outbound interfaces are the architecture container's subject, not this
  node's. See `architecture-containers-agent-runtime`.
- **The step-by-step flow through the capability** — the exact turn lifecycle
  (startup, channel discovery, the Inbound Author Gate, batching, dispatch, recovery)
  is the flow node's subject, not this node's. See `architecture-flows-agent-turn`.
- **The boundary contract this capability is exposed through** — no
  `interfaces-events`-typed corpus node yet documents the ACP JSON-RPC wire surface
  or `buzz-cli`'s own command surface as an interface in the corpus schema's sense.
  This is a real gap, not a decision to fold that content in here; see *Scope and
  omissions*.
- **How the running system is operated** — deployment topology, monitoring, and
  incident response for a deployed agent runtime belong to the `operations` surface,
  not this capability description.

## Relationships

- `references`: `architecture-containers-agent-runtime` — the architecture node that
  realizes this capability (the `buzz-acp`/`buzz-agent`/`buzz-dev-mcp`/`sprig`
  crates), confirmed merged on `origin/launchpad` at the checked revision.
- `references`: `architecture-flows-agent-turn` — the flow node documenting the
  step-by-step turn lifecycle this capability runs, confirmed merged on
  `origin/launchpad` at the checked revision.

No `part-of` or `implements` edge is declared: at the checked revision, no other
`capabilities`-typed node is merged on `origin/launchpad` for this one to sit
underneath, and this template's own `implements` edge toward
`corpus-template-capability` is optional and not added here.

## Scope and omissions

**This node covers** what the ACP agent harness capability lets a user or agent do,
its current shipped maturity, its behavioral variants (agent-tool choice via BYOH's
three tiers, the Inbound Author Gate's four modes and owner-command override,
launcher independence), and its explicit boundary against the architecture, flow,
interface and operations neighbors.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| How the capability is built (crates, dependencies, interfaces) | `architecture-containers-agent-runtime` |
| The step-by-step turn lifecycle | `architecture-flows-agent-turn` |
| The ACP wire protocol / `buzz-cli` command surface as a formal interface node | Not yet filed as of this writing — no `interfaces-events`-typed node exists in the corpus for either surface |
| Persona-pack format and merge rules | `crates/buzz-persona/PERSONA_PACK_SPEC.md` (not yet a corpus node) |
| The remote-agent provider protocol in full | `docs/remote-agents.md` (not yet a corpus node) |
| How the running system is operated (deployment, monitoring, incident response) | the `operations` corpus surface |

**Expected but not verified when this node was written:**

- **Whether every BYOH tier-2 preset actually implements the full ACP contract in
  practice**, versus being PATH-probed as "available" without a live conformance
  check — `crates/buzz-acp/README.md`'s own note about `openclaw acp` (PATH-available
  even when its Gateway daemon is not running) suggests this is not uniformly true,
  but no exhaustive check of every preset was performed for this node.
- **Whether a dedicated verification artifact (an integration test suite, a
  conformance checklist) exists specifically demonstrating this capability**, as
  distinct from the crate-level tests referenced by the architecture and flow nodes
  this document `references`. No such artifact was located and cited directly here;
  a reader wanting verification evidence should follow this node's `references`
  edges to the architecture and flow nodes, which cite `crates/buzz-acp/src/` test
  modules directly.
- **Whether a future `interfaces-events` node for the ACP surface, or a broader
  sibling `capabilities`-typed node, should receive a `references` or `part-of` edge
  from this node** — left open per `AGENTS.md`'s rule that a relationship target
  must exist on the branch being merged into, not be declared in anticipation of it.
